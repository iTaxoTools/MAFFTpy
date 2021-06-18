 /*
  * wrapio - Redirect stdio to Python-level operations
  * Copyright (C) 2021  Patmanidis Stefanos
  *
  * This program is free software: you can redistribute it and/or modify
  * it under the terms of the GNU General Public License as published by
  * the Free Software Foundation, either version 3 of the License, or
  * (at your option) any later version.
  *
  * This program is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  *
  * You should have received a copy of the GNU General Public License
  * along with this program.  If not, see <https://www.gnu.org/licenses/>.
  */

 /*
  * wrapio.c:
  * Uses static variables, does not support subinterpreters
  */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <stdio.h>


static PyObject * _module = NULL;
static char *_buffer = NULL;
static int _buffer_size = 512;


int __add_attr_from_dict ( PyObject *m, PyObject *dict, char *attr ) {
 /*
  * setattr(m, attr, dict[attr])
  * Return 0 on success. Return -1 and sets an error on failure.
  */

  PyObject *item = NULL;

  if (!(item = PyDict_GetItemString(dict, attr))) {
    PyErr_Format(PyExc_AttributeError,
      "Could not retrieve attibute 'sys.%s'.", attr
    );
    return -1;
  }
  Py_INCREF(item);
  if (PyModule_AddObject(m, attr, item)) {
    Py_DECREF(item);
    return -1;
    // DOES IT SET ERROR THOUGH ????
  }
  return 0;
}

char *__attr_from_stream ( FILE *stream ) {
/*
  * Return the corresponding attribute name,
  * or an empty string if not one of stdout/stderr.
  */
  char * attr = "";
  if (stream == stdout) attr = "stdout";
  else if (stream == stderr) attr = "stderr";
  return attr;
}

PyObject *__file_from_stream ( FILE *stream ) {
 /*
  * Return the corresponding Python IO object.
  * On failure, set error indicator and return NULL.
  */

  PyObject *dict = NULL;
  PyObject *file = NULL;
  char * attr = __attr_from_stream(stream);

  if (!(dict = PyModule_GetDict(_module)))
    return NULL;

  if (!(file = PyDict_GetItemString(dict, attr))) {
    PyErr_Format(PyExc_AttributeError,
      "Module '%s' has no attibute '%s'.",
      PyModule_GetName(_module), attr
    );
    return NULL;
  }
  return file;
}

int _vfprintf ( FILE *stream, const char *format, va_list args ) {
 /*
  * Set error indicator, write nothing and return -1 on failure.
  * Reallocate buffer if needed.
  * Caller should check afterwards with PyErr_Occurred().
  */
	int done;
  char * attr = __attr_from_stream(stream);

  if ((_module) && (attr[0] != '\0')) {

  	PyObject *dict = NULL;
  	PyObject *file = NULL;

    if (!_buffer) {
      PyErr_SetString(PyExc_RuntimeError,	"Buffer not initialised.");
      return -1;
    }
    while ((done = vsnprintf (_buffer, _buffer_size, format, args)) >= _buffer_size) {
      free(_buffer);
      _buffer_size = done + 1;
      if (!(_buffer = malloc(sizeof(char) * _buffer_size))) {
        PyErr_SetString(PyExc_RuntimeError,	"Failed to re-allocate memory.");
        return -1;
      }
    }

    if (!(file = __file_from_stream(stream)))
      return -1;

  	if (PyFile_WriteString(_buffer, file))
  		return -1;
  }
  else {
    done = vfprintf(stream, format, args);
  }
	return done;
}

int _fprintf ( FILE *stream, const char *format, ... ) {
  va_list args;
  int done;
  va_start(args, format);
  done = _vfprintf(stream, format, args);
  va_end(args);
  return done;
}

int _printf ( const char *format, ...) {
  va_list args;
  int done;
  va_start(args, format);
  done = _vfprintf(stdout, format, args);
  va_end(args);
  return done;
}

int _fputc ( int character, FILE * stream ) {
 /*
  * Set error indicator, write nothing and return EOF on failure.
  * Caller should check afterwards with PyErr_Occurred().
  */

	int done = character;
  PyObject *file = NULL;
  char array[2] = {'\0', '\0'};
  char * attr = __attr_from_stream(stream);

  if ((_module) && (attr[0] != '\0')) {

    if (!(file = __file_from_stream(stream)))
      return EOF;

    array[0] = (char) character;
  	if (PyFile_WriteString(array, file))
  		return EOF;
  }
  else {
    done = fputc(character, stream);
  }
	return done;
}

int _putc ( int character, FILE * stream ) {
  return _fputc(character, stream);
}

int _putchar ( int character ) {
  return _fputc(character, stdout);
}

int _fputs ( const char * str, FILE * stream ) {
 /*
  * Set error indicator, write nothing and return -1 on failure.
  * Caller should check afterwards with PyErr_Occurred().
  */

	int done = 0;
  PyObject *file = NULL;
  char * attr = __attr_from_stream(stream);

  if ((_module) && (attr[0] != '\0')) {

    if (!(file = __file_from_stream(stream)))
      return EOF;

  	if (PyFile_WriteString(str, file))
  		return EOF;
  }
  else {
    done = fputs(str, stream);
  }
	return done;
}

int _puts ( const char * str ) {
  if (_fputs(str, stdout) == EOF) return EOF;
  if (_fputc('\n', stdout) == EOF) return EOF;
  return 0;
}

int _fflush ( FILE * stream ) {
 /*
  * Set error indicator, write nothing and return -1 on failure.
  * Caller should check afterwards with PyErr_Occurred().
  */

  int done = 0;
  PyObject *file = NULL;
  PyObject *res = NULL;
  char * attr = __attr_from_stream(stream);

  if ((_module) && (attr[0] != '\0')) {

    file = __file_from_stream(stream);
    if (!(res = PyObject_CallMethod(file, "flush", NULL)))
      return EOF;
    Py_DECREF(res);
  }
  else {
   done = fflush(stream);
  }
  return done;
}

int wrapio_init ( PyObject *m ) {
/*
 * Add redirection attributes to module and allocate the buffer.
 * Call from within the module's PyInit function after PyModule_Create().
 * Return 0 on success. Return -1 and sets an error on failure.
 *
 * Arguments:
 * - m: the parenting python module
 */

  PyObject *sys = NULL;
  PyObject *dict = NULL;
  int done;

  if (!PyModule_Check(m)) {
		PyErr_SetString(PyExc_AttributeError,	"Not a module.");
		goto except;
  }

	// Copy stdout/stderr from sys

	if (!(sys = PyImport_ImportModule("sys")))
		goto except;

	if (!(dict = PyModule_GetDict(sys)))
		goto except;

  __add_attr_from_dict(m, dict, "stdout");
  __add_attr_from_dict(m, dict, "stderr");

  // (Re)set globals

  if (_module) Py_DECREF(_module);
  if (_buffer) free(_buffer);

  _module = m;
	Py_INCREF(m);
	if (!(_buffer = malloc(sizeof(char) * _buffer_size))) {
		PyErr_SetString(PyExc_RuntimeError,	"Failed to allocate memory.");
		goto except;
	}

  done = 0;
	goto finally;
except:
	done = -1;
finally:
  Py_XDECREF(dict);
	Py_XDECREF(sys);
  return done;
}
