#pragma once
#include <time.h>
#ifdef __cplusplus
#if !defined(MU_HAVE_GMTIME_S)
#define MU_HAVE_GMTIME_S
inline int gmtime_s(struct tm* out, const time_t* t) { return gmtime_r(t, out) ? 0 : 1; }
#endif
#endif
