# SPDX-License-Identifier: MIT
# mbedTLS for the Switch 2 port (the TLS of Slippi's matchmaking, wss://matchmaking.slippi.gg).
# Usage: make -C switch2/mbedtls MBEDTLS=/path/to/mbedtls-3.6.2 [OUT=build-mbedtls]
# Builds $(OUT)/libmbedtls_all.a from every file of library/, with switch_config.h over the defaults.
DKP     ?= $(DEVKITPRO)
MBEDTLS ?= ../../../mbedtls
OUT     ?= build
HERE    := $(CURDIR)
CC      := $(DKP)/devkitA64/bin/aarch64-none-elf-gcc
AR      := $(DKP)/devkitA64/bin/aarch64-none-elf-ar
CFLAGS  := -O2 -g -mcpu=cortex-a78c+crypto -mtp=soft -fPIE -ffunction-sections -fdata-sections -D__SWITCH__ \
           -I$(MBEDTLS)/include -I$(MBEDTLS)/library -I$(HERE) -DMBEDTLS_USER_CONFIG_FILE='"switch_config.h"' \
           -I$(DKP)/libounce/include
SRC     := $(wildcard $(MBEDTLS)/library/*.c)
OBJ     := $(patsubst $(MBEDTLS)/library/%.c,$(OUT)/obj/%.o,$(SRC))
$(OUT)/libmbedtls_all.a: $(OBJ)
	rm -f $@; $(AR) rcs $@ $^
$(OUT)/obj/%.o: $(MBEDTLS)/library/%.c
	@mkdir -p $(dir $@); $(CC) $(CFLAGS) -c $< -o $@
