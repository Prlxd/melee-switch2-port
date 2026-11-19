/* mbedTLS settings for the Switch 2 port (user config over the default mbedtls_config.h). */
#undef MBEDTLS_NET_C            /* the port brings its own sockets (libnx BSD) */
#undef MBEDTLS_TIMING_C
#undef MBEDTLS_PSA_ITS_FILE_C
#undef MBEDTLS_PSA_CRYPTO_STORAGE_C
#define MBEDTLS_NO_PLATFORM_ENTROPY      /* no /dev/urandom: entropy from the console's CSPRNG */
#define MBEDTLS_ENTROPY_HARDWARE_ALT     /* mbedtls_hardware_poll (tls_switch.cpp) */
#define MBEDTLS_PLATFORM_MS_TIME_ALT    /* mbedtls_ms_time (tls_switch.cpp) */
