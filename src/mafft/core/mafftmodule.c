/*
  MAFFTpy - Multiple sequence alignment with MAFFT
  Copyright (C) 2021  Patmanidis Stefanos

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

/*
Extension Module for MAFFT

Consider using multi-phase extension module initialization instead:
https://www.python.org/dev/peps/pep-0489/
*/

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <stdio.h>
#include "mafftmodule.h"

// Set var = dict[str], do nothing if key does not exist.
// On failure, sets error indicator and returns -1.
// Return 0 on success.
// Beware: parsing strings allocates memory!
int parseItem(PyObject *dict, const char *str, const char t, void *var) {

	PyObject *item;
	PyObject *value;
	switch(t){
		case 'b':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			*(int *)var = PyObject_IsTrue(item);
			if (*(int *)var == -1) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected boolean value for key '%s'", str);
				return -1;
			}
			break;
		case 'i':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			*(int *)var = (int) PyLong_AsLong(item);
			if (PyErr_Occurred()) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected integer value for key '%s'", str);
				return -1;
			}
			break;
		case 'd':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			*(double *)var = (double) PyFloat_AsDouble(item);
			if (PyErr_Occurred()) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected double value for key '%s'", str);
				return -1;
			}
			break;
		case 'f':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			*(float *)var = (float) PyFloat_AsDouble(item);
			if (PyErr_Occurred()) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected float value for key '%s'", str);
				return -1;
			}
			break;
		case 's':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			value = PyUnicode_AsEncodedString(item, "utf-8", "~E~");
			if (value == NULL) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected string value for key '%s'", str);
				return -1;
			}
			const char *bytes = PyBytes_AS_STRING(value);
			*(const char **)var = malloc(strlen (bytes) + 1);
			strcpy(*(const char **)var, bytes);
			Py_XDECREF(value);
			break;
		default:
			PyErr_Format(PyExc_TypeError, "parseItem: Unexpected type: %c", t);
			return -1;
		}
	return 0;
}

static PyObject *
mafft_main(PyObject *self, PyObject *args) {

	/* module specific */

	PyObject *dict;
	PyObject *item;
	char *file_data;
	FILE *f_in;

	printf("foobar\n");

	// Accept a dictionary-like python object
	if (!PyArg_ParseTuple(args, "O", &dict))
		return NULL;
	if (!PyDict_Check(dict)) {
		PyErr_SetString(PyExc_TypeError, "asap_main: Argument must be a dictionary");
		return NULL;
	}

	if (parseItem(dict, "file", 's', &file_data)) return NULL;

	if (!file_data) {
		PyErr_SetString(PyExc_KeyError, "asap_main: Mandatory key: 'file'");
		return NULL;
	}

	f_in = fopen(file_data, "r");
	if (f_in==NULL) {
		PyErr_Format(PyExc_FileNotFoundError, "asap_main: Input file not found: '%s'", file_data);
		return NULL;
	}

	printf("file = %s\n", file_data);

	int argc = 3;
	char *argv[3];
	argv[0] = "disttbfast";
	argv[1] = "-i";
	argv[2] = file_data;
	int res = disttbfast( 0, 0, NULL, NULL, argc, argv, NULL );

	printf("res=%d\n", res);

	Py_INCREF(Py_None);
	return Py_None;
}


static PyMethodDef MafftMethods[] = {
  {"main",  mafft_main, METH_VARARGS,
   "Run MAFFT for given parameters."},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyDoc_STRVAR(mafft_doc,
"Multiple sequence alignment.");

static struct PyModuleDef mafftmodule = {
  PyModuleDef_HEAD_INIT,
  "mafft",   /* name of module */
  mafft_doc, /* module documentation, may be NULL */
  -1,       /* size of per-interpreter state of the module,
               or -1 if the module keeps state in global variables. */
  MafftMethods
};

PyMODINIT_FUNC
PyInit_mafft(void)
{
	PyObject *m = NULL;
  m = PyModule_Create(&mafftmodule);
	// if (m != NULL) {
	// 	if (PyModule_AddStringConstant(m, "separator", "/")) {
	// 		Py_XDECREF(m);
	// 		m = NULL;
	// 	}
	// }
	return m;
}
