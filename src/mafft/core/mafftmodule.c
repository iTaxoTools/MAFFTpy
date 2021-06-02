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

// Create arguments from dictionary
// On failure, sets error indicator and returns -1.
// Return 0 on success.
int argsFromDict(PyObject *dict, int* rargc, char*** rargv, char* progname) {

	PyObject *key, *value;
	PyObject *str, *enc, *check;
	Py_ssize_t pos = 0;

	int len = (int) PyDict_Size(dict);
	char **argv = malloc(sizeof(char*)*(len*2+2));
	int argc = 1;
	argv[0] = progname;

	while (PyDict_Next(dict, &pos, &key, &value)) {

		str = PyObject_Str(key);
		enc = PyUnicode_AsEncodedString(str, "utf-8", "~E~");
		const char *bytes = PyBytes_AS_STRING(enc);
		Py_XDECREF(str);
		Py_XDECREF(enc);
		check = PyUnicode_AsEncodedString(key, "utf-8", "~E~");
		if (check == NULL) {
			PyErr_Format(PyExc_TypeError, "argsFromDict: key must be string: %s", bytes);
			return -1;
		}

		argv[argc] = malloc(strlen (bytes) + 2);
		argv[argc][0] = '-';
		strcpy(argv[argc]+1, bytes);
		argc++;

		if (value != Py_None) {
			str = PyObject_Str(value);
			enc = PyUnicode_AsEncodedString(str, "utf-8", "~E~");
			const char *bytes = PyBytes_AS_STRING(enc);
	    Py_XDECREF(str);
	    Py_XDECREF(enc);

			argv[argc] = malloc(strlen (bytes) + 1);
			strcpy(argv[argc], bytes);
			argc++;
		}
	}
	argv[argc] = NULL;

	*rargc = argc;
	*rargv = argv;

	return 0;
}

// Frees memory allocated by argsFromDict
// Doesn't work since disttbfast alters argv pointers
// int argsFree(int argc, char** argv) {
// 		for (int i = 1; i < argc; i++) {
// 			printf("freeing %d, %s\n", i, argv[i]);
// 			free(argv[i]);
// 		}
// 		printf("freeing last\n");
// 		free(argv);
// }

static PyObject *
mafft_disttbfast(PyObject *self, PyObject *args, PyObject *kwargs) {

	/* module specific */

	PyObject *dict = kwargs;
	PyObject *item;
	FILE *f_in;

	int argc;
	char **argv;
	if (argsFromDict(dict, &argc, &argv, "disttbfast")) return NULL;

	fprintf(stderr, ">");
	for (int i = 0; i < argc; i++) fprintf(stderr, " %s", argv[i]);
	fprintf(stderr, "\n");

	int res = disttbfast( 0, 0, NULL, NULL, argc, argv, NULL );
	if (res) {
		PyErr_Format(PyExc_TypeError, "mafft_disttbfast: Abnormal exit code: %i", res);
		return NULL;
	}

	// argsFree(argc, argv);

	// Required, as streams are redirected by python caller
	fflush(stdout);
	fflush(stderr);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
mafft_tbfast(PyObject *self, PyObject *args, PyObject *kwargs) {

	/* module specific */

	PyObject *dict = kwargs;
	PyObject *pdict = NULL;
	PyObject *item;
	FILE *f_in;

	int argc, pargc = 0, targc = 0;
	char **argv, **pargv = NULL, **targv = NULL;

	const char *pair_string = "pair";

	pdict = PyDict_GetItemString(dict, pair_string);
	if (pdict != NULL) {
		if (!PyDict_Check(pdict)) {
			PyErr_SetString(PyExc_TypeError, "mafft_tbfast: Pair argument must be a dictionary");
			return NULL;
		}
		if (PyDict_DelItemString(dict, pair_string)) {
			PyErr_SetString(PyExc_TypeError, "mafft_tbfast: Unexpected error deleting pair key");
			return NULL;
		}
		if (argsFromDict(pdict, &pargc, &pargv, "tbfast-pair")) return NULL;
	}

	if (argsFromDict(dict, &targc, &targv, "tbfast")) return NULL;

	// Prepare arguments to be parsed by tbfast()
	// Pair args (if any) are "enclosed" in underscores
	if (pargc) {
		argc = pargc + targc + 1;
		argv = malloc(sizeof(char*)*(argc+1));
		argv[0] = targv[0];
		argv[1] = "_";
		for (int i = 1; i < pargc; i++) argv[1+i] = pargv[i];
		argv[pargc+1] = "_";
		for (int i = 1; i < targc; i++) argv[pargc+1+i] = targv[i];
		argv[argc] = NULL;
	}
	else {
		argc = targc;
		argv = targv;
	}

	fprintf(stderr, ">");
	for (int i = 0; i < argc; i++) fprintf(stderr, " %s", argv[i]);
	fprintf(stderr, "\n");

	int res = tbfast(argc, argv);
	if (res) {
		PyErr_Format(PyExc_TypeError, "mafft_tbfast: Abnormal exit code: %i", res);
		return NULL;
	}

	// argsFree(argc, argv);

	// Required, as streams are redirected by python caller
	fflush(stdout);
	fflush(stderr);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
mafft_dvtditr(PyObject *self, PyObject *args, PyObject *kwargs) {

	/* module specific */

	PyObject *dict = kwargs;
	PyObject *item;
	FILE *f_in;

	int argc;
	char **argv;
	if (argsFromDict(dict, &argc, &argv, "dvtditr")) return NULL;

	fprintf(stderr, ">");
	for (int i = 0; i < argc; i++) fprintf(stderr, " %s", argv[i]);
	fprintf(stderr, "\n");

	int res = dvtditr(argc, argv);
	if (res) {
		PyErr_Format(PyExc_TypeError, "mafft_dvtditr: Abnormal exit code: %i", res);
		return NULL;
	}

	// argsFree(argc, argv);

	// Required, as streams are redirected by python caller
	fflush(stdout);
	fflush(stderr);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
mafft_foo(PyObject *self, PyObject *args) {
	fprintf(stdout, "BAR STDOUT\n");
	fprintf(stderr, "BAR STDERR\n");
	Py_INCREF(Py_None);
	return Py_None;
}
static PyMethodDef MafftMethods[] = {
  {"disttbfast",  mafft_disttbfast, METH_VARARGS | METH_KEYWORDS,
   "Run mafft/disttbfast with given parameters."},
	{"tbfast",  mafft_tbfast, METH_VARARGS | METH_KEYWORDS,
   "Run mafft/tbfast with given parameters."},
  {"dvtditr",  mafft_dvtditr, METH_VARARGS | METH_KEYWORDS,
   "Run mafft/dvtditr with given parameters."},
  {"dvtditr",  mafft_dvtditr, METH_VARARGS | METH_KEYWORDS,
   "Run mafft/dvtditr with given parameters."},
  {"foo",  mafft_foo, METH_VARARGS, "bar"},
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
