#ifdef enablemultithread
#ifdef _MSC_VER
#define TLS __declspec(thread)
#else
#define TLS __thread
#endif
#else
#define TLS
#endif

#ifdef enableatomic
#define ATOMICINT atomic_int
#else
#define ATOMICINT int
#endif

extern TLS int commonAlloc1;
extern TLS int commonAlloc2;
extern TLS int **commonIP;
extern TLS int **commonJP;
