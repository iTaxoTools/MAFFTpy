#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <math.h>
#include "mtxutl.h"
#ifdef ismodule
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "wrapio.h"
#endif

#define PI 3.14159265358979323846
#define END_OF_VEC -1

#define NKOUHO   20
#define NKOUHO_LONG   500

#define MAX(X,Y)    ( ((X)>(Y))?(X):(Y) )
#define MIN(X,Y)    ( ((X)<(Y))?(X):(Y) )
