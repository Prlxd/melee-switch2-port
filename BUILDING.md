# Building

This repository holds the Switch 2 port as changes on top of
[melee-unlocked](https://github.com/hero88go/melee-unlocked). You need a melee-unlocked checkout at
the exact commit below, the devkitPro Switch toolchain with libnx, and the Switch 2 graphics stack the
port uses (OunceVK: Mesa Zink and NVK, with its CMake toolchain file).

| | Commit |
|---|---|
| melee-unlocked | `0696966d250fd0decdc53218aaafb60cbb763296` (Version 0.9.118) |
| its `sourceport/extern/melee` submodule (doldecomp/melee) | `039c4bf4ca33338c35d21901ad19b7ede19d19ad` |

## What is here

| Path | Contents |
|---|---|
| `patches/melee-unlocked-switch2.patch` | Changes and new files in melee-unlocked (the Switch 2 host, renderer and game fixes). |
| `patches/melee-decomp-switch2.patch` | Changes to the decompiled game code (20 files), applied after melee-unlocked's own `sourceport/patches/melee-native.patch`. |
| `switch2/nro/` | The NRO Makefile, the list of source files it builds, and one generated source. |
| `switch2/launcher/` | The scripts that draw the launcher's screens (game picker, options, "Preparing graphics") and the icon, the two picker panels, and the script that packs the built-in shader list. |

## Steps

1. **Get melee-unlocked at the right commit:**
   ```sh
   git clone https://github.com/hero88go/melee-unlocked
   cd melee-unlocked
   git checkout 0696966d250fd0decdc53218aaafb60cbb763296
   git submodule update --init sourceport/extern/melee
   ```
2. **Apply melee-unlocked's own patch to the decompiled code, then this port's:**
   ```sh
   cd sourceport/extern/melee
   git apply ../../patches/melee-native.patch
   git apply /path/to/this-repo/patches/melee-decomp-switch2.patch
   cd ../../..
   ```
3. **Apply the port's changes to melee-unlocked:**
   ```sh
   git apply /path/to/this-repo/patches/melee-unlocked-switch2.patch
   ```
4. **Build the game library** with the Switch 2 toolchain, then prelink it:
   ```sh
   cmake -S sourceport/game -B build-game -DCMAKE_BUILD_TYPE=Release \
     -DCMAKE_TOOLCHAIN_FILE=$DEVKITPRO/libounce/cmake/Switch2.cmake \
     -DMU_NO_SLIPPI=ON -DMU_AKANEIA_FIGHTERS=ON -DMU_ACE_FIGHTERS=ON -DMU_MEX_STAGES=ON -DMU_ROGUE=ON \
     -DCMAKE_C_FLAGS="-mcpu=cortex-a78c+crypto -mtp=soft -ftls-model=local-exec -ffunction-sections -fdata-sections -D__SWITCH__ -D__SWITCH2__" \
     -DCMAKE_CXX_FLAGS="-mcpu=cortex-a78c+crypto -mtp=soft -ftls-model=local-exec -ffunction-sections -fdata-sections -D__SWITCH__ -D__SWITCH2__"
   make -C build-game melee_game
   cd build-game && sh ../port/switch2/prelink_game.sh $DEVKITPRO/devkitA64/bin libmelee_game.a melee_game.o && cd ..
   ```
5. **Draw the launcher screens** (needs Python 3 with Pillow and NumPy, and the Poppins font; set
   `POPPINS_DIR` to its folder if it is not in `/usr/share/fonts/truetype/google-fonts`):
   ```sh
   L=/path/to/this-repo/switch2/launcher
   python3 $L/make.py 0.8.3 .             # the game picker: port/switch2/launcher_art.h, and icon.jpg
   python3 $L/options_art.py 0.8.3 .      # the options screen: port/switch2/options_art.h
   python3 $L/prewarm_screen.py 0.8.3 .   # "Preparing graphics": port/switch2/prewarm_art.h
   ```
   `art.py` redraws the two picker panels (`art/left.png`, `art/right.png`); they are already in the
   repository, so it is optional.

   The built-in shader list, `port/switch2/shader_seed.h`, comes with the patch. It was recorded on a
   Switch 2 by the shader sweep (`shadersweep=1` in `config.ini`: 203 scripted matches covering every
   character, VS stage and item); `shader_seed.py` packs the `recipes.bin` files such a run leaves in
   `sdmc:/melee/shader-cache/` into that header.
6. **Build the NRO.** It also needs glslang and SPIRV-Cross built for Switch 2, in one folder
   (`THIRD`):
   ```sh
   cp -r /path/to/this-repo/switch2/nro ./nro && cp /path/to/this-repo/switch2/launcher/icon.jpg nro/
   sh nro/link-sources.sh .
   make -C nro MU=$PWD GAME_O=$PWD/build-game/melee_game.o THIRD=/path/to/third
   ```
   The result is `nro/melee-switch2-port.nro`.

Outside a git checkout, use `patch -p1 < file.patch` in place of `git apply file.patch`.

## Version

The version is set in two places: `MU_APP_VERSION` near the top of `port/switch2/host_switch.cpp`,
and `APP_VERSION` in `switch2/nro/Makefile`. Pass the same number to the launcher scripts.
