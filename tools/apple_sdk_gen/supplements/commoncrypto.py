"""Generate CommonCrypto stub headers for the SDK.

CommonCrypto provides hashing (SHA, MD5), symmetric encryption (AES),
HMAC, key derivation, and random bytes.  The API is stable and well-known.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def install_commoncrypto_headers(sdk_root: Path) -> None:
    """Write CommonCrypto headers into ``<sdk>/usr/include/CommonCrypto/``."""
    cc_dir = sdk_root / "usr" / "include" / "CommonCrypto"
    cc_dir.mkdir(parents=True, exist_ok=True)

    _HEADERS: dict[str, str] = {
        "CommonCryptoError.h": _COMMON_CRYPTO_ERROR_H,
        "CommonDigest.h": _COMMON_DIGEST_H,
        "CommonCryptor.h": _COMMON_CRYPTOR_H,
        "CommonHMAC.h": _COMMON_HMAC_H,
        "CommonKeyDerivation.h": _COMMON_KEY_DERIVATION_H,
        "CommonRandom.h": _COMMON_RANDOM_H,
        "CommonSymmetricKeywrap.h": _COMMON_SYMMETRIC_KEYWRAP_H,
        "CommonCrypto.h": _COMMON_CRYPTO_H,
    }

    for name, content in _HEADERS.items():
        (cc_dir / name).write_text(content)

    logger.info("Installed %d CommonCrypto headers", len(_HEADERS))


# ── Header contents ─────────────────────────────────────────────────

_COMMON_CRYPTO_ERROR_H = """\
#ifndef _CC_COMMON_CRYPTO_ERROR_H_
#define _CC_COMMON_CRYPTO_ERROR_H_

#include <stdint.h>

enum {
    kCCSuccess          = 0,
    kCCParamError       = -4300,
    kCCBufferTooSmall   = -4301,
    kCCMemoryFailure    = -4302,
    kCCAlignmentError   = -4303,
    kCCDecodeError      = -4304,
    kCCUnimplemented    = -4305,
    kCCOverflow         = -4306,
    kCCRNGFailure       = -4307,
    kCCUnspecifiedError  = -4308,
    kCCCallSequenceError = -4309,
    kCCKeySizeError     = -4310,
    kCCInvalidKey       = -4311,
};
typedef int32_t CCCryptorStatus;

#endif /* _CC_COMMON_CRYPTO_ERROR_H_ */
"""

_COMMON_DIGEST_H = """\
#ifndef _CC_COMMON_DIGEST_H_
#define _CC_COMMON_DIGEST_H_

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* MD5 */
#define CC_MD5_DIGEST_LENGTH    16
#define CC_MD5_BLOCK_BYTES      64
#define CC_MD5_BLOCK_LONG       (CC_MD5_BLOCK_BYTES / sizeof(uint32_t))

typedef struct {
    uint32_t A, B, C, D;
    uint64_t Nl, Nh;
    uint32_t data[CC_MD5_BLOCK_LONG];
    uint32_t num;
} CC_MD5_CTX;

extern int CC_MD5_Init(CC_MD5_CTX *c);
extern int CC_MD5_Update(CC_MD5_CTX *c, const void *data, unsigned long len);
extern int CC_MD5_Final(unsigned char *md, CC_MD5_CTX *c);
extern unsigned char *CC_MD5(const void *data, unsigned int len, unsigned char *md);

/* SHA1 */
#define CC_SHA1_DIGEST_LENGTH   20
#define CC_SHA1_BLOCK_BYTES     64
#define CC_SHA1_BLOCK_LONG      (CC_SHA1_BLOCK_BYTES / sizeof(uint32_t))

typedef struct {
    uint32_t h0, h1, h2, h3, h4;
    uint64_t Nl, Nh;
    uint32_t data[CC_SHA1_BLOCK_LONG];
    uint32_t num;
} CC_SHA1_CTX;

extern int CC_SHA1_Init(CC_SHA1_CTX *c);
extern int CC_SHA1_Update(CC_SHA1_CTX *c, const void *data, unsigned long len);
extern int CC_SHA1_Final(unsigned char *md, CC_SHA1_CTX *c);
extern unsigned char *CC_SHA1(const void *data, unsigned int len, unsigned char *md);

/* SHA256 */
#define CC_SHA256_DIGEST_LENGTH 32
#define CC_SHA256_BLOCK_BYTES   64

typedef struct {
    uint32_t count[2];
    uint32_t hash[8];
    uint32_t wbuf[16];
} CC_SHA256_CTX;

extern int CC_SHA256_Init(CC_SHA256_CTX *c);
extern int CC_SHA256_Update(CC_SHA256_CTX *c, const void *data, unsigned long len);
extern int CC_SHA256_Final(unsigned char *md, CC_SHA256_CTX *c);
extern unsigned char *CC_SHA256(const void *data, unsigned int len, unsigned char *md);

/* SHA224 */
#define CC_SHA224_DIGEST_LENGTH 28
#define CC_SHA224_BLOCK_BYTES   64
typedef CC_SHA256_CTX CC_SHA224_CTX;

extern int CC_SHA224_Init(CC_SHA224_CTX *c);
extern int CC_SHA224_Update(CC_SHA224_CTX *c, const void *data, unsigned long len);
extern int CC_SHA224_Final(unsigned char *md, CC_SHA224_CTX *c);
extern unsigned char *CC_SHA224(const void *data, unsigned int len, unsigned char *md);

/* SHA384 */
#define CC_SHA384_DIGEST_LENGTH 48
#define CC_SHA384_BLOCK_BYTES   128

typedef struct {
    uint64_t count[2];
    uint64_t hash[8];
    uint64_t wbuf[16];
} CC_SHA512_CTX;

extern int CC_SHA384_Init(CC_SHA512_CTX *c);
extern int CC_SHA384_Update(CC_SHA512_CTX *c, const void *data, unsigned long len);
extern int CC_SHA384_Final(unsigned char *md, CC_SHA512_CTX *c);
extern unsigned char *CC_SHA384(const void *data, unsigned int len, unsigned char *md);

/* SHA512 */
#define CC_SHA512_DIGEST_LENGTH 64
#define CC_SHA512_BLOCK_BYTES   128
typedef CC_SHA512_CTX CC_SHA512_CTX_ref;

extern int CC_SHA512_Init(CC_SHA512_CTX *c);
extern int CC_SHA512_Update(CC_SHA512_CTX *c, const void *data, unsigned long len);
extern int CC_SHA512_Final(unsigned char *md, CC_SHA512_CTX *c);
extern unsigned char *CC_SHA512(const void *data, unsigned int len, unsigned char *md);

#ifdef __cplusplus
}
#endif

#endif /* _CC_COMMON_DIGEST_H_ */
"""

_COMMON_CRYPTOR_H = """\
#ifndef _CC_COMMON_CRYPTOR_H_
#define _CC_COMMON_CRYPTOR_H_

#include <CommonCrypto/CommonCryptoError.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct _CCCryptor *CCCryptorRef;

enum {
    kCCEncrypt = 0,
    kCCDecrypt = 1,
};
typedef uint32_t CCOperation;

enum {
    kCCAlgorithmAES128 = 0,
    kCCAlgorithmAES    = 0,
    kCCAlgorithmDES    = 1,
    kCCAlgorithm3DES   = 2,
    kCCAlgorithmCAST   = 3,
    kCCAlgorithmRC4    = 4,
    kCCAlgorithmRC2    = 5,
    kCCAlgorithmBlowfish = 6,
};
typedef uint32_t CCAlgorithm;

enum {
    kCCOptionPKCS7Padding = 0x0001,
    kCCOptionECBMode      = 0x0002,
};
typedef uint32_t CCOptions;

enum {
    kCCModeECB = 1,
    kCCModeCBC = 2,
    kCCModeCFB = 3,
    kCCModeCTR = 4,
    kCCModeOFB = 7,
    kCCModeRC4 = 9,
    kCCModeCFB8 = 10,
};
typedef uint32_t CCMode;

enum {
    ccNoPadding = 0,
    ccPKCS7Padding = 1,
};
typedef uint32_t CCPadding;

/* Key sizes */
enum {
    kCCKeySizeAES128       = 16,
    kCCKeySizeAES192       = 24,
    kCCKeySizeAES256       = 32,
    kCCKeySizeDES          = 8,
    kCCKeySize3DES         = 24,
    kCCKeySizeMinCAST      = 5,
    kCCKeySizeMaxCAST      = 16,
    kCCKeySizeMinRC4       = 1,
    kCCKeySizeMaxRC4       = 512,
    kCCKeySizeMinRC2       = 1,
    kCCKeySizeMaxRC2       = 128,
    kCCKeySizeMinBlowfish  = 8,
    kCCKeySizeMaxBlowfish  = 56,
};

/* Block sizes */
enum {
    kCCBlockSizeAES128 = 16,
    kCCBlockSizeDES    = 8,
    kCCBlockSize3DES   = 8,
    kCCBlockSizeCAST   = 8,
    kCCBlockSizeRC2    = 8,
    kCCBlockSizeBlowfish = 8,
};

extern CCCryptorStatus CCCrypt(
    CCOperation op, CCAlgorithm alg, CCOptions options,
    const void *key, size_t keyLength,
    const void *iv,
    const void *dataIn, size_t dataInLength,
    void *dataOut, size_t dataOutAvailable,
    size_t *dataOutMoved);

extern CCCryptorStatus CCCryptorCreate(
    CCOperation op, CCAlgorithm alg, CCOptions options,
    const void *key, size_t keyLength, const void *iv,
    CCCryptorRef *cryptorRef);

extern CCCryptorStatus CCCryptorCreateWithMode(
    CCOperation op, CCMode mode, CCAlgorithm alg, CCPadding padding,
    const void *iv, const void *key, size_t keyLength,
    const void *tweak, size_t tweakLength,
    int numRounds, uint32_t options,
    CCCryptorRef *cryptorRef);

extern CCCryptorStatus CCCryptorUpdate(
    CCCryptorRef cryptorRef,
    const void *dataIn, size_t dataInLength,
    void *dataOut, size_t dataOutAvailable,
    size_t *dataOutMoved);

extern CCCryptorStatus CCCryptorFinal(
    CCCryptorRef cryptorRef,
    void *dataOut, size_t dataOutAvailable,
    size_t *dataOutMoved);

extern CCCryptorStatus CCCryptorRelease(CCCryptorRef cryptorRef);
extern CCCryptorStatus CCCryptorReset(CCCryptorRef cryptorRef, const void *iv);
extern size_t CCCryptorGetOutputLength(CCCryptorRef cryptorRef, size_t inputLength, int final);

#ifdef __cplusplus
}
#endif

#endif /* _CC_COMMON_CRYPTOR_H_ */
"""

_COMMON_HMAC_H = """\
#ifndef _CC_COMMON_HMAC_H_
#define _CC_COMMON_HMAC_H_

#include <CommonCrypto/CommonDigest.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

enum {
    kCCHmacAlgSHA1   = 0,
    kCCHmacAlgMD5    = 1,
    kCCHmacAlgSHA256 = 2,
    kCCHmacAlgSHA384 = 3,
    kCCHmacAlgSHA512 = 4,
    kCCHmacAlgSHA224 = 5,
};
typedef uint32_t CCHmacAlgorithm;

#define CC_HMAC_CONTEXT_SIZE 96
typedef struct {
    uint32_t ctx[CC_HMAC_CONTEXT_SIZE];
} CCHmacContext;

extern void CCHmacInit(CCHmacContext *ctx, CCHmacAlgorithm algorithm,
                       const void *key, size_t keyLength);
extern void CCHmacUpdate(CCHmacContext *ctx, const void *data, size_t dataLength);
extern void CCHmacFinal(CCHmacContext *ctx, void *macOut);

extern void CCHmac(CCHmacAlgorithm algorithm, const void *key, size_t keyLength,
                   const void *data, size_t dataLength, void *macOut);

#ifdef __cplusplus
}
#endif

#endif /* _CC_COMMON_HMAC_H_ */
"""

_COMMON_KEY_DERIVATION_H = """\
#ifndef _CC_COMMON_KEY_DERIVATION_H_
#define _CC_COMMON_KEY_DERIVATION_H_

#include <CommonCrypto/CommonCryptoError.h>
#include <CommonCrypto/CommonHMAC.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum {
    kCCPBKDF2 = 2,
};
typedef uint32_t CCPBKDFAlgorithm;

enum {
    kCCPRFHmacAlgSHA1   = 1,
    kCCPRFHmacAlgSHA224 = 2,
    kCCPRFHmacAlgSHA256 = 3,
    kCCPRFHmacAlgSHA384 = 4,
    kCCPRFHmacAlgSHA512 = 5,
};
typedef uint32_t CCPseudoRandomAlgorithm;

extern CCCryptorStatus CCKeyDerivationPBKDF(
    CCPBKDFAlgorithm algorithm,
    const char *password, size_t passwordLen,
    const uint8_t *salt, size_t saltLen,
    CCPseudoRandomAlgorithm prf, unsigned rounds,
    uint8_t *derivedKey, size_t derivedKeyLen);

extern unsigned CCCalibratePBKDF(
    CCPBKDFAlgorithm algorithm,
    size_t passwordLen, size_t saltLen,
    CCPseudoRandomAlgorithm prf,
    size_t derivedKeyLen, uint32_t msec);

#ifdef __cplusplus
}
#endif

#endif /* _CC_COMMON_KEY_DERIVATION_H_ */
"""

_COMMON_RANDOM_H = """\
#ifndef _CC_COMMON_RANDOM_H_
#define _CC_COMMON_RANDOM_H_

#include <CommonCrypto/CommonCryptoError.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct __CCRandom *CCRandomRef;

extern CCCryptorStatus CCRandomGenerateBytes(void *bytes, size_t count);

#ifdef __cplusplus
}
#endif

#endif /* _CC_COMMON_RANDOM_H_ */
"""

_COMMON_SYMMETRIC_KEYWRAP_H = """\
#ifndef _CC_COMMON_SYMMETRIC_KEYWRAP_H_
#define _CC_COMMON_SYMMETRIC_KEYWRAP_H_

#include <CommonCrypto/CommonCryptoError.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum {
    kCCWRAPAES = 1,
};

extern const uint8_t CCrfc3394_iv[];
extern const size_t CCrfc3394_ivLen;

extern CCCryptorStatus CCSymmetricKeyWrap(
    uint32_t algorithm,
    const uint8_t *iv, size_t ivLen,
    const uint8_t *kek, size_t kekLen,
    const uint8_t *rawKey, size_t rawKeyLen,
    uint8_t *wrappedKey, size_t *wrappedKeyLen);

extern CCCryptorStatus CCSymmetricKeyUnwrap(
    uint32_t algorithm,
    const uint8_t *iv, size_t ivLen,
    const uint8_t *kek, size_t kekLen,
    const uint8_t *wrappedKey, size_t wrappedKeyLen,
    uint8_t *rawKey, size_t *rawKeyLen);

extern size_t CCSymmetricWrappedSize(uint32_t algorithm, size_t rawKeyLen);
extern size_t CCSymmetricUnwrappedSize(uint32_t algorithm, size_t wrappedKeyLen);

#ifdef __cplusplus
}
#endif

#endif /* _CC_COMMON_SYMMETRIC_KEYWRAP_H_ */
"""

_COMMON_CRYPTO_H = """\
#ifndef _CC_COMMON_CRYPTO_H_
#define _CC_COMMON_CRYPTO_H_

#include <CommonCrypto/CommonCryptoError.h>
#include <CommonCrypto/CommonDigest.h>
#include <CommonCrypto/CommonCryptor.h>
#include <CommonCrypto/CommonHMAC.h>
#include <CommonCrypto/CommonKeyDerivation.h>
#include <CommonCrypto/CommonRandom.h>
#include <CommonCrypto/CommonSymmetricKeywrap.h>

#endif /* _CC_COMMON_CRYPTO_H_ */
"""
