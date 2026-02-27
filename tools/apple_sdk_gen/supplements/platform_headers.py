"""Generate essential platform headers that are not available from Apple OSS repos.

- **TargetConditionals.h** — included transitively by nearly every Apple header.
- **Block.h** — needed by any code using Objective-C / C blocks.
- **dlfcn.h** — standard POSIX dynamic-loading API (lives in dyld, not open-sourced).
- **math.h** — standard C99/POSIX math (not in the Libc OSS ``include/`` directory).
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── TargetConditionals per-platform values ──────────────────────────
# Tuple: (TARGET_OS_MAC, TARGET_OS_IPHONE, TARGET_OS_IOS, TARGET_OS_WATCH,
#          TARGET_OS_TV, TARGET_OS_VISION, TARGET_OS_SIMULATOR,
#          TARGET_CPU_ARM64, TARGET_RT_64_BIT)

_TARGET_VALUES: dict[str, tuple[int, ...]] = {
    #                MAC  IPHONE  IOS  WATCH  TV  VISION  SIM  ARM64  64BIT
    "ios":       (   1,    1,      1,   0,     0,  0,      0,   1,     1),
    "macos":     (   1,    0,      0,   0,     0,  0,      0,   1,     1),
    "tvos":      (   1,    1,      0,   0,     1,  0,      0,   1,     1),
    "watchos":   (   1,    1,      0,   1,     0,  0,      0,   1,     1),
    "visionos":  (   1,    1,      0,   0,     0,  1,      0,   1,     1),
}


def _generate_target_conditionals(platform_key: str) -> str:
    vals = _TARGET_VALUES.get(platform_key, _TARGET_VALUES["ios"])
    (mac, iphone, ios, watch, tv, vision, sim, arm64, bit64) = vals

    return f"""\
/*
 * TargetConditionals.h — auto-generated for {platform_key}
 */
#ifndef __TARGETCONDITIONALS__
#define __TARGETCONDITIONALS__

/* Operating-system flags */
#define TARGET_OS_MAC               {mac}
#define TARGET_OS_OSX               {1 if platform_key == 'macos' else 0}
#define TARGET_OS_IPHONE            {iphone}
#define TARGET_OS_IOS               {ios}
#define TARGET_OS_WATCH             {watch}
#define TARGET_OS_WATCHOS           {watch}
#define TARGET_OS_TV                {tv}
#define TARGET_OS_VISION            {vision}
#define TARGET_OS_SIMULATOR         {sim}
#define TARGET_OS_EMBEDDED          {iphone}
#define TARGET_OS_MACCATALYST       0
#define TARGET_OS_DRIVERKIT         0
#define TARGET_OS_UNIX              1
#define TARGET_OS_WIN32             0
#define TARGET_OS_WINDOWS           0
#define TARGET_OS_LINUX             0
#define TARGET_OS_NANO              {watch}

/* CPU flags */
#define TARGET_CPU_ARM              0
#define TARGET_CPU_ARM64            {arm64}
#define TARGET_CPU_X86              0
#define TARGET_CPU_X86_64           {1 if platform_key == 'macos' else 0}
#define TARGET_CPU_PPC              0
#define TARGET_CPU_PPC64            0
#define TARGET_CPU_MIPS             0

/* Runtime flags */
#define TARGET_RT_LITTLE_ENDIAN     1
#define TARGET_RT_BIG_ENDIAN        0
#define TARGET_RT_64_BIT            {bit64}
#define TARGET_RT_MAC_CFM           0

/* Feature flags */
#define TARGET_IPHONE_SIMULATOR     TARGET_OS_SIMULATOR
#define TARGET_OS_BRIDGE            0

#endif /* __TARGETCONDITIONALS__ */
"""


def _generate_block_h() -> str:
    """Generate Block.h — Blocks runtime API (well-known, from LLVM compiler-rt)."""
    return """\
/*
 * Block.h — Blocks runtime API
 */
#ifndef _BLOCK_H_
#define _BLOCK_H_

#if !defined(BLOCK_EXPORT)
#  if defined(__cplusplus)
#    define BLOCK_EXPORT extern "C"
#  else
#    define BLOCK_EXPORT extern
#  endif
#endif

#if __cplusplus
extern "C" {
#endif

BLOCK_EXPORT void *_Block_copy(const void *aBlock);
BLOCK_EXPORT void _Block_release(const void *aBlock);
BLOCK_EXPORT void _Block_object_assign(void *, const void *, const int);
BLOCK_EXPORT void _Block_object_dispose(const void *, const int);

#define Block_copy(...) ((__typeof(__VA_ARGS__))_Block_copy((const void *)(__VA_ARGS__)))
#define Block_release(...) _Block_release((const void *)(__VA_ARGS__))

/* Block descriptor flags */
enum {
    BLOCK_FIELD_IS_OBJECT   = 3,
    BLOCK_FIELD_IS_BLOCK    = 7,
    BLOCK_FIELD_IS_BYREF    = 8,
    BLOCK_FIELD_IS_WEAK     = 16,
    BLOCK_BYREF_CALLER      = 128,
};

#if __cplusplus
}
#endif

#endif /* _BLOCK_H_ */
"""


def _generate_dlfcn_h() -> str:
    """Generate dlfcn.h — standard POSIX dynamic-loading prototypes."""
    return """\
/*
 * dlfcn.h — dynamic linking API
 */
#ifndef _DLFCN_H_
#define _DLFCN_H_

#include <sys/cdefs.h>
#include <stddef.h>

__BEGIN_DECLS

/* dlopen() mode flags */
#define RTLD_LAZY       0x1
#define RTLD_NOW        0x2
#define RTLD_LOCAL      0x4
#define RTLD_GLOBAL     0x8
#define RTLD_NOLOAD     0x10
#define RTLD_NODELETE   0x80
#define RTLD_FIRST      0x100

/* Special handle values */
#define RTLD_NEXT       ((void *) -1)
#define RTLD_DEFAULT    ((void *) -2)
#define RTLD_SELF       ((void *) -3)
#define RTLD_MAIN_ONLY  ((void *) -5)

typedef struct dl_info {
    const char *dli_fname;
    void       *dli_fbase;
    const char *dli_sname;
    void       *dli_saddr;
} Dl_info;

extern void *dlopen(const char * __path, int __mode);
extern int   dlclose(void * __handle);
extern void *dlsym(void * __handle, const char * __symbol);
extern char *dlerror(void);
extern int   dladdr(const void *, Dl_info *);

__END_DECLS

#endif /* _DLFCN_H_ */
"""


def _generate_math_h() -> str:
    """Generate math.h — C99/POSIX math functions and constants."""
    return """\
/*
 * math.h — standard math functions and constants
 */
#ifndef _MATH_H_
#define _MATH_H_

#include <sys/cdefs.h>

__BEGIN_DECLS

/* Classification macros (C99) */
#define FP_NAN          1
#define FP_INFINITE     2
#define FP_ZERO         3
#define FP_NORMAL       4
#define FP_SUBNORMAL    5

#define HUGE_VAL        __builtin_huge_val()
#define HUGE_VALF       __builtin_huge_valf()
#define HUGE_VALL       __builtin_huge_vall()
#define NAN             __builtin_nanf("0x7fc00000")
#define INFINITY        __builtin_inf()

#define M_E             2.71828182845904523536028747135266250
#define M_LOG2E         1.44269504088896340735992468100189214
#define M_LOG10E        0.434294481903251827651128918916605082
#define M_LN2           0.693147180559945309417232121458176568
#define M_LN10          2.30258509299404568401799145468436421
#define M_PI            3.14159265358979323846264338327950288
#define M_PI_2          1.57079632679489661923132169163975144
#define M_PI_4          0.785398163397448309615660845819875721
#define M_1_PI          0.318309886183790671537767526745028724
#define M_2_PI          0.636619772367581343075535053490057448
#define M_2_SQRTPI      1.12837916709551257389615890312154517
#define M_SQRT2         1.41421356237309504880168872420969808
#define M_SQRT1_2       0.707106781186547524400844362104849039

/* Trigonometric */
extern double sin(double);
extern double cos(double);
extern double tan(double);
extern double asin(double);
extern double acos(double);
extern double atan(double);
extern double atan2(double, double);
extern float sinf(float);
extern float cosf(float);
extern float tanf(float);
extern float asinf(float);
extern float acosf(float);
extern float atanf(float);
extern float atan2f(float, float);

/* Hyperbolic */
extern double sinh(double);
extern double cosh(double);
extern double tanh(double);
extern double asinh(double);
extern double acosh(double);
extern double atanh(double);
extern float sinhf(float);
extern float coshf(float);
extern float tanhf(float);
extern float asinhf(float);
extern float acoshf(float);
extern float atanhf(float);

/* Exponential and logarithmic */
extern double exp(double);
extern double exp2(double);
extern double expm1(double);
extern double log(double);
extern double log2(double);
extern double log10(double);
extern double log1p(double);
extern double ldexp(double, int);
extern double frexp(double, int *);
extern float expf(float);
extern float exp2f(float);
extern float expm1f(float);
extern float logf(float);
extern float log2f(float);
extern float log10f(float);
extern float log1pf(float);
extern float ldexpf(float, int);
extern float frexpf(float, int *);

/* Power and absolute value */
extern double pow(double, double);
extern double sqrt(double);
extern double cbrt(double);
extern double hypot(double, double);
extern double fabs(double);
extern float powf(float, float);
extern float sqrtf(float);
extern float cbrtf(float);
extern float hypotf(float, float);
extern float fabsf(float);

/* Rounding and remainder */
extern double ceil(double);
extern double floor(double);
extern double round(double);
extern double trunc(double);
extern double nearbyint(double);
extern double rint(double);
extern long lrint(double);
extern long long llrint(double);
extern long lround(double);
extern long long llround(double);
extern double fmod(double, double);
extern double remainder(double, double);
extern double remquo(double, double, int *);
extern float ceilf(float);
extern float floorf(float);
extern float roundf(float);
extern float truncf(float);
extern float nearbyintf(float);
extern float rintf(float);
extern long lrintf(float);
extern long long llrintf(float);
extern long lroundf(float);
extern long long llroundf(float);
extern float fmodf(float, float);
extern float remainderf(float, float);
extern float remquof(float, float, int *);

/* Min, max, difference */
extern double fmax(double, double);
extern double fmin(double, double);
extern double fdim(double, double);
extern float fmaxf(float, float);
extern float fminf(float, float);
extern float fdimf(float, float);

/* Fused multiply-add */
extern double fma(double, double, double);
extern float fmaf(float, float, float);

/* Manipulation */
extern double modf(double, double *);
extern double scalbn(double, int);
extern double scalbln(double, long);
extern double copysign(double, double);
extern double nan(const char *);
extern double nextafter(double, double);
extern int ilogb(double);
extern double logb(double);
extern float modff(float, float *);
extern float scalbnf(float, int);
extern float scalblnf(float, long);
extern float copysignf(float, float);
extern float nanf(const char *);
extern float nextafterf(float, float);
extern int ilogbf(float);
extern float logbf(float);

/* Error and gamma */
extern double erf(double);
extern double erfc(double);
extern double tgamma(double);
extern double lgamma(double);
extern float erff(float);
extern float erfcf(float);
extern float tgammaf(float);
extern float lgammaf(float);

/* Classification functions (C99) */
extern int __isnormalf(float);
extern int __isnormald(double);
extern int __isfinitef(float);
extern int __isfinited(double);
extern int __isinff(float);
extern int __isinfd(double);
extern int __isnanf(float);
extern int __isnand(double);
extern int __fpclassifyf(float);
extern int __fpclassifyd(double);

#define fpclassify(x) \
    (sizeof(x) == sizeof(float) ? __fpclassifyf(x) : __fpclassifyd(x))

#define isfinite(x) \
    (sizeof(x) == sizeof(float) ? __isfinitef(x) : __isfinited(x))

#define isinf(x) \
    (sizeof(x) == sizeof(float) ? __isinff(x) : __isinfd(x))

#define isnan(x) \
    (sizeof(x) == sizeof(float) ? __isnanf(x) : __isnand(x))

#define isnormal(x) \
    (sizeof(x) == sizeof(float) ? __isnormalf(x) : __isnormald(x))

#define signbit(x) \
    (sizeof(x) == sizeof(float) ? __builtin_signbitf(x) : __builtin_signbit(x))

__END_DECLS

#endif /* _MATH_H_ */
"""


def install_platform_headers(sdk_root: Path, platform_key: str) -> None:
    """Install essential platform headers into usr/include/."""
    usr_include = sdk_root / "usr" / "include"
    usr_include.mkdir(parents=True, exist_ok=True)

    generated = 0

    # TargetConditionals.h
    tc_path = usr_include / "TargetConditionals.h"
    if not tc_path.exists():
        tc_path.write_text(_generate_target_conditionals(platform_key))
        generated += 1

    # Block.h
    block_path = usr_include / "Block.h"
    if not block_path.exists():
        block_path.write_text(_generate_block_h())
        generated += 1

    # dlfcn.h
    dlfcn_path = usr_include / "dlfcn.h"
    if not dlfcn_path.exists():
        dlfcn_path.write_text(_generate_dlfcn_h())
        generated += 1

    # math.h
    math_path = usr_include / "math.h"
    if not math_path.exists():
        math_path.write_text(_generate_math_h())
        generated += 1

    logger.info("Generated %d platform headers for %s", generated, platform_key)
