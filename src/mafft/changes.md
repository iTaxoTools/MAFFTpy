
The following changes were made to the original (version 7.525):

Added python module: `mafftmodule.c`, `mafftmodule.h`
Added output wrapper: `wrapio.c`, `wrapio.h`

Renamed the main() functions in `disttbfast.c`, `tbfast.c`, `makedirectionlist.c`, `setdirection.c`
and put ``#ifndef ismodule` around them.

Also modified the following functions as static in `tbfast.c`, `disttbfast.c`, `dvtditr.c`, `makedirectionlist.c`, `setdirection.c`:
- arguments()
- makecompositiontable_p()
- makepointtable()
- seq_grp()
- makepointtable_nuc()
- seq_grp_nuc()


Added section to the following files: `fft.h` `mltaln.h` `mtxutl.c`
```
#ifdef ismodule
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "wrapio.h"
#endif
```

Changed for module workflow:

- diff `makedirectionlist.c` :
```
737,739d736
< #ifdef ismodule
< 		return 0;
< #else
741d737
< #endif
```

Changed for MSVC compatibility:

- diff `disttbfast.c`:
```
1422c1422
<       return (int)((char *)p - (char *)q);
---
>       return (int)((void *)p - (void *)q);
1429c1429
<       return (int)((char *)q - (char *)p);
---
>       return (int)((void *)q - (void *)p);
```

Update multiprocessing macros for Windows in `dp.h` and `mltaln.h`:
```
#ifdef enablemultithread
    #ifdef _MSC_VER
        #define TLS __declspec(thread)
    #else
        #define TLS __thread
    #endif
#else
    #define TLS
#endif
```
