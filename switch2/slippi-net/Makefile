# SPDX-License-Identifier: MIT
# The Slippi online layer for the Switch 2 port: melee-unlocked's Slippi sources (account,
# matchmaking, netplay, reports, replays, rollback snapshots), ENet, the port's TLS (mbedTLS) and
# the stubs for what the port does not have.
# Usage: make -C switch2/slippi-net MU=/path/to/patched/melee-unlocked MBEDTLS=/path/to/mbedtls-3.6.2 [OUT=build]
DKP     ?= $(DEVKITPRO)
MU      ?= ../../../melee-unlocked
MBEDTLS ?= ../../../mbedtls
OUT     ?= build
HERE    := $(CURDIR)
P       := $(MU)/port
CC      := $(DKP)/devkitA64/bin/aarch64-none-elf-gcc
CXX     := $(DKP)/devkitA64/bin/aarch64-none-elf-g++
AR      := $(DKP)/devkitA64/bin/aarch64-none-elf-ar
ARCH    := -mcpu=cortex-a78c+crypto -mtp=soft -fPIE -ffunction-sections -fdata-sections
INC     := -I$(P)/switch2 -I$(MBEDTLS)/include -I$(HERE)/../mbedtls -I$(P)/switch2/compat -I$(P)/linux/compat -I$(P)/linux \
           -I$(P)/runtime/abi -I$(P)/runtime/hle -I$(P)/runtime/host -I$(P)/runtime/gx -I$(P)/runtime/ppc -I$(P)/third_party \
           -I$(P)/third_party/enet/include -I$(P)/third_party/nlohmann/include -I$(DKP)/libounce/include -I$(MU)/native
DEFS    := -D__SWITCH__ -DMU_SWITCH2 -DMELEE_LINUX -DMELEE_SOURCE_PORT -DMU_SLIPPI_SWITCH -DMBEDTLS_USER_CONFIG_FILE=\"switch_config.h\"
CXXFLAGS := -include $(HERE)/sw_extra.h -O2 -g -std=gnu++17 -fsigned-char -ffp-contract=off $(ARCH) $(INC) $(DEFS)
CFLAGS  := -include arpa/inet.h -O2 -g -fsigned-char $(ARCH) -I$(P)/third_party/enet/include -D__SWITCH__ -DHAS_SOCKLEN_T=1 \
           -DHAS_POLL=1 -DHAS_FCNTL=1 -DHAS_GETADDRINFO=1 -DHAS_GETNAMEINFO=1 -DHAS_INET_PTON=1 -DHAS_INET_NTOP=1 \
           -I$(DKP)/libounce/include
CXXSRC  := $(addprefix $(P)/runtime/hle/,slippi_online.cpp slippi_net.cpp slippi_report.cpp slippi_spectate.cpp \
             native_replay_stream.cpp online_rows.cpp slippi_hsd_links.cpp slippi_mm_service.cpp native_savestate.cpp) \
           $(P)/switch2/tls_switch.cpp $(P)/switch2/slippi_switch_stubs.cpp
CSRC    := $(filter-out %/yg_enet_socket.c,$(wildcard $(P)/third_party/enet/*.c))
OBJ     := $(patsubst $(P)/%.cpp,$(OUT)/obj/%.o,$(CXXSRC)) $(patsubst $(P)/%.c,$(OUT)/obj/%.o,$(CSRC))
$(OUT)/libslippi_net.a: $(OBJ)
	rm -f $@; $(AR) rcs $@ $^
$(OUT)/obj/%.o: $(P)/%.cpp
	@mkdir -p $(dir $@); $(CXX) $(CXXFLAGS) -c $< -o $@
$(OUT)/obj/%.o: $(P)/%.c
	@mkdir -p $(dir $@); $(CC) $(CFLAGS) -c $< -o $@
