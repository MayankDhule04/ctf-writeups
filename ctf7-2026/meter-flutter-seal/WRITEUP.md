# meter.apk (com.northfield.meter): partial result

Status: **flag not recovered.** The app now runs for real in this sandbox (FEAT-004, see next section), but the user's remembered path J2 -> J3 -> Z shows a seal with **DRIFT**, not MATCH, and the seal turns out to hash the full ordered history of user actions. Without the intended procedure (normally in the challenge description) MATCH cannot be found by search.

## Running the real app headlessly (FEAT-004, works)
- Engine: `eng_cp/libflutter_linux_gtk.so` (compressed-pointer build, engine af7e796e...) loads `bundle/libapp.so` (Android x86_64 AOT snapshot) directly.
- Rendering fix: the previous FATAL `Impeller DlText cannot be drawn to a Skia canvas` is gone after calling `fl_dart_project_set_enable_impeller(proj, FALSE)` (harness env `METER_IMPELLER=0`) together with `FLUTTER_LINUX_RENDERER=software` (`METER_RENDERER=software`). EGL context creation still fails under Xvfb, so the GL path is not used.
- Input fix: `gdk_test_simulate_button` events never reached FlView. `harness.c` now injects synthetic GdkEvents (motion+press+release, or touch begin/end with `tap X Y`) into the deepest GdkWindow under the point via `gtk_main_do_event`. Extra FIFO commands: `tap X Y`, `clicknm X Y`, `resize W H`, `life AppLifecycleState.<x>`.
- Rebuild: `./build_harness.sh`. One run: `ENGDIR=$PWD/eng_cp METER_RENDERER=software METER_IMPELLER=0 ./session.sh ./drive4.sh` (screenshots go to `shots/`; `/tmp` is not shared between tool calls).
- Parallel explorer: `python3 explore.py J2,J3,Z K1,J2,J3,Z ...` runs each comma-separated button sequence in a fresh app on its own Xvfb display (:100+), logs the `a2` channel argument and reads MATCH/DRIFT from the PANEL C pixels. Button names/coordinates are in `BTN` in `explore.py`.

## Observed behaviour (real run)
- Screens: Command Console (K1..K6, J1, J2), PANEL B (M1..M3, J3, BACK, MEMORY DUMP hex view), PANEL C (OUTPUT, Z, BACK). Screenshots: `shots/b0.png`, `shots/c1.png`, `shots/d1.png`, `shots/e2.png`.
- J2 -> J3 -> Z gives `ctf7{dependency_graph_9d6b55f2df8ef5113388e508}` with **DRIFT** (`shots/e2.png`; channel `a2(-105625342) -> 0x89e4c0cd`). FNV-1a32 of that hex is not 0xEE2B5244. This is not the flag.
- The result is identical with mouse vs touch input, 1 s vs 6 s delays, window heights 800/915/1300, mid-run resizes, and injected lifecycle (inactive/hidden/paused/resumed) messages. So the seal depends only on the action sequence.
- Pressing Z again on the same PANEL C does not change the value. Leaving and re-entering PANEL C does.
- K1 bumps UNIT 01 A/B and UNIT 05 B; K2 bumps UNIT 02 A/B; K4 swaps ZONE B and RELAY LINK (changes the widget-tree order that the dump walks) and turns UNIT 04 B to 1/1; J1 opens PANEL B with UNIT 04 B 1/1; K3/K5/K6 have no visible effect but still change the seal; M1..M3 change it.
- Search: 344 sequences (0-2 K presses, J1 or J2, optional M1/M2/M3, J3, Z; `search1.txt` -> `search1.out`) gave 344 distinct seals, all DRIFT. K1,K2 differs from K2,K1, so the hashed state is order-dependent history. Exhaustive search is not feasible.
- The terminal `[SCAN] Probe: 0x...` lines are Random()-generated noise (xre.dart 0x1d72d4/0x1d7434), not hints.

## What is needed to finish
The intended procedure (exact button sequence) from the challenge description or the user's original solve. With it, run `python3 explore.py <SEQ>`, confirm MATCH on screen, and check the hex with `solve.py`'s `is_real_seal()`.

## Earlier notes (before FEAT-004; the "cannot run" section below is now outdated)
## Why this sandbox cannot run the app (checked, not assumed)
Three independent routes to dynamic execution were investigated and all are genuine dead ends here, not just missing tools:

1. **Android emulator / device**: no `adb`, `frida`, `frida-ps`, or Android SDK anywhere on the system. No `/dev/kvm` (`ls /dev/kvm` -> No such file or directory) and the CPU has no visible `vmx` flag, so even installing QEMU would mean full software (TCG) emulation of an ARM64/x86_64 Android system image — far too slow to be practical, and moot anyway because:
2. **No package manager write access**: `dnf`/`yum` are present but `/var/log` (and `/root`) are read-only, so `dnf install qemu-kvm` (or adb/frida) fails immediately with `Read-only file system: '/var/log/dnf.log'`. No system packages can be installed in this sandbox.
3. **Headless Flutter-Linux-engine route (this session's own prior attempt, `harness.c`/`run.sh`/`bundle/`)**: a GTK-based Flutter Linux engine (`eng/libflutter_linux_gtk.so`) was already wired up to load the app's `x86_64` AOT snapshot directly, bypassing Android entirely. It fails at `CreateRootIsolate` with:
   ```
   the snapshot requires '... x64 android compressed-pointers' but the VM has '... x64 linux no-compressed-pointers'
   ```
   This was re-investigated: `DART_COMPRESSED_POINTERS` is a **compile-time `#ifdef`** in the Dart VM (confirmed in `blutter/dartsdk/v3.13.4/runtime/vm/{globals,raw_object,tagged_pointer,snapshot}.h`) that changes how object pointers are represented in the heap (32-bit compressed tagged pointers vs. 64-bit raw pointers). It is baked into the prebuilt engine binary, not a runtime flag or a simple string gate. The AOT machine code inside `libapp.so` itself emits pointer arithmetic assuming compression. Patching the engine's expected-feature string to force a match would make the VM load the snapshot and then corrupt the heap immediately (crash, not a flag) — not a real fix. A genuinely compatible engine would require either an Android-targeted Linux/x64 Flutter engine build (Flutter does not publish one for the Linux GTK embedder with compressed pointers; the `android-x64` artifact that does ship is a `.jar` containing bionic/ART-linked `.so`s that need an actual Android runtime to load, which we don't have) or rebuilding the whole engine from source with `dart_use_compressed_pointers=true`, an undertaking far beyond this session.

Static decompilation (blutter-ported for Dart 3.13.4, output in `outf/`) therefore remains the ceiling for this sandbox. It fully explains the mechanism but the 24 hex characters are provably state-dependent (see "What the app does" and `APP_MODEL.md`) and do not exist as a fixed value anywhere in the binary.

## Tooling
- blutter ported to Dart 3.13.4 (patches under `blutter/blutter/src`: single snapshot symbols, closure offsets, null type bound, native-function pool entries, Code size clamping). Full analysis output is in `outf/`; `out/` is the `--no-analysis` build.
- `dartdis.py` (capstone, resolves pool refs and names), `model.py`, `emu_step.py` (unicorn check of the mixer).

## What the app does
- Java side: channel `com.northfield.meter/io`. `a1` = hash of package name (0x4148b2). `a2(x)` = mix of `a1^x`.
- Dart side ignores both results: `a1` falls back to constant 0x3a587694, `a2` to 0x5e6f7081 (decoys).
- Dart keeps a 24-byte state (`tfa`, static `Cj`). `main` (0x34bc50) scrambles it with a1 (0x3069f4). UI actions mix events in via `0x1d593c` -> `0x1d59f8` (8-op byte mixer; reimplemented in `solve.py`, matches emulation for 300 random cases).
- The "Z / MEMORY DUMP" button (Fye `_Nod`, 0x2012a0): registers a global pointer route, replays recorded events (0x201454), hashes the buffer (FNV-1a, 0x20175c), calls native `a2`, then prints 12 bytes as 24 hex chars.
- Closure 0x201ab4 then displays `PREFIX + hex + "}"` and sets MATCH/DRIFT by `FNV-1a32(hex) == 0xEE2B5244` (0x201b54). The on-screen flag is therefore only valid when MATCH shows.
- Prefix, decoded from the byte table at 0x201c40 (`b ^ ((37*i+0xa5)&0xff)`): `ctf7{dependency_graph_`.

## Not solved statically, and why it cannot be (see `APP_MODEL.md` for full detail)
`solve.py`'s `candidate()` assumes an **empty** event list, which is already known to be wrong: the "MEMORY DUMP" (Z) button's list (`sfa`, replayed by `0x201454`) is not raw pointer events but a **live tree-walk snapshot of the mounted Flutter widget State objects** at the moment of the dump (`APP_MODEL.md`, "CORRECTION" section) — hence the flag prefix `dependency_graph_`. Each live State contributes a rolling hash (`st.f47`) that itself depends on how many times that widget has been built/rebuilt (`kind 6/8/0xb` logging during `build()`), plus dispose-time accumulators (`Cj.f13/f1b/f23`) fed by every widget that has been unmounted since app start. None of this exists before the app runs; it is a function of the exact navigation path taken (J2 -> J3 -> Z -> PANEL C per the user's recap) and how many times intermediate screens were built. No combination of a1 (0x4148b2 Java-real / 0x3a587694 Dart-fallback-decoy) and a2 (Java-real / 0x5e6f7081 Dart-fallback-decoy) with an empty list matches the target FNV, confirming the model: the list cannot legitimately be empty on a real run.

## How to finish this on a real device (per the user's own prior-session method)
The user has already solved this exact challenge once before via live instrumentation (noted in their recap: `frida_buf.py`, `frida_heap.org`, `find_buffer.py`, navigating J2 -> J3 -> Z -> PANEL C). That remains the correct and only reliable path; this sandbox cannot run the app (see above). To repeat it:

1. Install the APK on a real device or an emulator that has KVM/hardware acceleration (this sandbox has neither).
2. Launch the app, then perform the exact path: **J2 -> J3 -> Z -> PANEL C**.
3. Attach Frida (`frida -U -f com.northfield.meter -l meter_seal.js` or `frida-trace`/`objection`) using the script below, which hooks the two concrete functions identified by static analysis instead of blind memory scanning:
   - `0x201b54` in `libapp.so` (the `FNV-1a32(hex) == 0xEE2B5244` MATCH check) — log its input string argument; it IS the real seal hex the instant this runs.
   - Alternatively hook the MethodChannel handler for `com.northfield.meter/io` and log the `a2` call's argument/return (confirms the real a2 is being used, not the Dart fallback decoy).

   ```javascript
   // meter_seal.js — attach after reaching PANEL C, before/at tapping MEMORY DUMP (Z)
   Java.perform(function () {
     // Log the real Java-side method channel values so we can confirm which a1/a2 the run actually used.
     var MainActivity = Java.use('com.northfield.meter.MainActivity'); // adjust to the real class name from java_hits.txt if different
     // If 'a1'/'a2' are plain methods reachable via reflection, hook here; otherwise rely on the native hook below.
   });

   // Native hook: the FNV-1a32 check at 0x201b54 inside libapp.so compares the seal hex string's
   // FNV-1a32 against the constant 0xEE2B5244. Hooking directly ahead of/at this address catches the
   // exact moment the real 24-hex-char seal exists in memory, before any UI redraw.
   var libapp = Process.findModuleByName('libapp.so');
   if (libapp) {
     console.log('libapp.so base:', libapp.base);
     // Dump surrounding memory each time the dump screen's build/paint runs, and grep for
     // "ctf7{dependency_graph_" or any 24-hex-char run adjacent to it, since direct symbol hooking
     // of AOT-compiled Dart code requires PC offsets recomputed from THIS libapp.so's actual base
     // (use the offsets from outf/pp.txt / outf/asm, which are relative to this same build).
     Interceptor.attach(libapp.base.add(0x201b54), { // offset from blutter analysis; verify against this libapp.so
       onEnter: function (args) {
         console.log('[seal-check] entered FNV-1a32 compare at 0x201b54');
       }
     });
   }

   // Simplest and most robust: periodically scan the app's heap for the ASCII prefix and dump the
   // surrounding bytes — this is what frida_buf.py / frida_heap.py / find_buffer.py already did
   // successfully in the user's prior session, and remains the most reliable approach since Dart AOT
   // function addresses are brittle across ASLR/base-relocation.
   setInterval(function () {
     Process.enumerateRanges('rw-').forEach(function (range) {
       try {
         Memory.scanSync(range.base, range.size, '63 74 66 37 7b').forEach(function (match) { // "ctf7{"
           var s = Memory.readCString(match.address, 64);
           console.log('[FOUND]', s);
         });
       } catch (e) {}
     });
   }, 500);
   ```

4. The printed string once MATCH is reached (not DRIFT — this app explicitly tells you on-screen which state you're in) is the real flag: `ctf7{dependency_graph_<24 hex chars>}`. Because it is per-launch, re-running the app and repeating the J2 -> J3 -> Z -> PANEL C path with the script attached will always recover the current session's flag; there's no way to reuse a previously captured value for a new app run.
5. `solve.py` in this directory remains useful as a cross-check: feed the 24 hex chars it reports from the live run into `is_real_seal()` to confirm `FNV-1a32 == 0xEE2B5244` before submitting.
