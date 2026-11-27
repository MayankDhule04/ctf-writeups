# APP_MODEL (FEAT-002), incremental notes

## Pointer-event history (sfa)
- sfa (class 186, size 0x60) = summary of a Flutter PointerEvent, built in Zte.dart by 8 per-event-type methods (0x2d9b8c family, e.g. 0x2d9bxx). Field 0x7 is a per-type constant: 212,161,103,229,178,120,195,246 (one per event class). Other int fields come from pointer id/device/buttons-mask etc (no float positions stored).
- Global route: Fye 0x201868 (called from _Wfa state setup) creates List<sfa> and registers closure `pyd` (rre.dart 0x201918) via static field 0x5a8 +0x103 (GestureBinding.pointerRouter.addGlobalRoute, 0x2d1f88). pyd: if event cid==0x758 and event.field_3f (a nA-subtype) is set, appends sfa-converted event to list; then calls a method on the event (vtable -0xdf8).
- So history = all real pointer events (touch down/up/move...) seen after the Fye screen registered, i.e. depends on actual gestures.
- Dump (Fye _Nod 0x2012a0): replay 0x201454 over list: per sfa: record kind 17 (a=f7<<?..), 18, 19, 21 each via 0x1d59f8, then kind 22 with Cj.f13^Cj.f1b, Cj.f23; then FNV(0x20175c), native a2, kind 20, 12 bytes -> hex.

## Cj (tfa, static field 0x784) mutable fields
- f13: Smi toggled by xor raw 0x10 (Dye 0x200708). f17: toggled raw 0x10 (Dye 0x2004cc). f1b: counter (+1 mod 3) (Dye 0x2005c8). f23: TBD.
- Pattern in Dye: handler first calls Cj.record(kind, arg-from-old-state), then setState-like 0x10cd20 with mutation closure.

## CORRECTION: the "global route" is a widget-tree walk, not pointer events
- static 0x5a8 = WidgetsBinding instance; +0x103 (ptr at 0x104) = rootElement; 0x2d1f88 = Element.visitChildren.
- pyd(Element e): if cid(e)==0x758 (1880 = cX = StatefulElement, field_3f = _state) and state is xt<nA> (rre.dart class 1753, app base State),
  call state.<vtable -0xf11>() -> sfa and append; then e.visitChildren(pyd) (recursion via ctx field_13).
- So the sfa list = snapshot, in tree DFS order, of every app State of class xt that is mounted at dump time ("dependency graph").
- 8 xt subclasses (via mixin apps): _wfa(1752,qre.dart, UNIT 01..04 cards with "A: ","B: ","C: "), _xfa(1750,sre), zfa(1748,tre), _Bfa(1746,ure), _Cfa(1744,vre), _Efa(1742,wre), _yfa(1738,yre), _Afa(1736,zre).
  Their snapshot methods are the 8 AllocatesfaStub sites in Zte.dart (blutter misplaced them), sfa.f7 constants 212,161,103,229,178,120,195,246.
- Replay per sfa (0x201454): kind17(a=f7,b=f_f), kind18(a=f_17? ,b=(f1f<<8)+f27), kind19(a=(f2f<<8)+(f37<<4)+f3f, b=(f47<<16)+f4f), kind21(a=f57,b=0); counter increments per call.

## Dump flow (async body 0x33f09c of Fye _Nod 0x2012a0), exact
1. list = 0x201860() (tree-walk snapshot, List<sfa>).
2. h = 0x20175c(Cj, list): buf,cnt = 0x201454(Cj,list) (replay on a COPY of Cj.bytes, counter starts at Cj.counter); h = FNV-1a32 over buf iterator; returned as signed int32.
3. a2 = await MethodChannel('a2', h) (0x33f1a4), fallback 0x5e6f7081 on error.
4. seal = 0x2012d8(Cj, list, a2): replay again (same as 2), then mixer(kind=20, a=a2, b=len(list), c=cnt_after_replay)  <-- solve.py used b=0 (wrong when list non-empty); then hex = buf[i]^(a2>>(8*(i&3)))&0xff for i<12.
5. closure 0x201ab4 shows flag + MATCH/DRIFT.
Replay per sfa s (exact, 0x201454): mix(17, s.f7, s.f_f, c++); mix(18, s.f17, (s.f1f<<8)+s.f27, c++); mix(19, (s.f2f<<8)+(s.f37<<4)+s.f3f, (s.f47<<16)+s.f4f, c++); mix(21, s.f57, 0, c++). After list: mix(22, Cj.f13^Cj.f1b, Cj.f23, c++).

## State class -> snapshot builder (Zte.dart, sfa.f7 const) and lifecycle mixin
| f7 | class | file | mixin app (MHa field) | builder |
|----|-------|------|-----|---------|
| 212 | _wfa | qre | _vt | 0x2d9b8c |
| 161 | _xfa | sre | _yt | 0x2d9d90 |
| 103 | zfa | tre | _At | 0x2d9f84 |
| 229 | _Bfa | ure | _Ct | 0x2da188 |
| 178 | _Cfa | vre | _Et | 0x2da388 |
| 120 | _Efa | wre | _Gt (+_uKc @0x54) | 0x2da57c |
| 195 | _yfa | yre | _Kt | 0x2da788 |
| 246 | _Afa | zre | _Mt | 0x2da97c |
Builder 212 (others analogous): sfa.f_f=MHa(state+0x14, late int), sfa.f17 = OR over Set state.f4f(+0x50) of 1<<elem.index, sfa.f1f=st.f17, f27=st.f1f, f2f=0, f37=st.f2f, f3f=st.f37, f47=st.f3f, f4f=(st.f67<<6 + st.f6f)&0xffff, f57=st.f47 (rolling hash).
(Variants: 161/178/195: f4f=st.f67&0xffff; 103/246: (f67<<4)+f6f; 229: f2f=st.f27, shifts others; 120: f4f=_uKc&0xffff.)
State mixin per-instance rolling hash (e.g. 0x1c3408 for 212): st.f47 = fmix(st.f47*0x1000193 + kind*0x9e3779b1 + 0xe743a09c + v*0xc2b2ae35) [32-bit, fmix = ^>>16,*0x45d9f3b,^>>16,*0x45d9f3b,^>>16].
Lifecycle hooks (dart_mixin_deduplication copies, 0x206448.. per class): kind4: st.f2f++ then log(4,MHa); kind5 (0x2072e4..): st.f37++, set f4f cleared(0x135258), log(5,MHa); kind6: set-add of enum, log(6,v).

## Lifecycle kinds (per-state log, st.f47 rolling hash)
- Cj (tfa) fields: f7 = Uint8List(24) bytes; fb = record counter; f13,f1b,f23 = dispose accumulators; f2b = global State instance-id counter. (alloc 0x1cefd4)
- kind 2 = initState (0x1cef08 etc per class): MHa = ++Cj.f2b; log(2, MHa).
- kind 3 = dispose (0x2119f0 for 212, per class in 0x211a3c..0x212120): log(3,MHa); then Cj absorb 0x211aa8(cc=classconst, id=MHa, h=st.f47): g=fmix(h); g^=cc*0x9e3779b1; g^=id*0x85ebca6b; g=fmix(g); Cj.f13=(f13+g)&M; Cj.f1b^=g; Cj.f23+=1.
  fmix(x): x^=x>>16; x*=0x45d9f3b; x^=x>>16; x*=0x45d9f3b; x^=x>>16 (all 32-bit).
- kind 4 (0x206448..): st.f2f++, log(4,MHa). kind 5 (0x2072e4..): st.f37++, st.f4f set cleared, log(5,MHa).
- log func for 212 (0x1c3408): f47 = fmix'(f47*0x1000193 + kind*0x9e3779b1 + 0xe743a09c + v*0xc2b2ae35). 120's (0x1cf4d0) uses cc*0x85ebca6b instead of the 0xe743a09c constant (= 0xd4*0x85ebca6b? check). 

## Cj.record sites (0x1d593c record(kind,a,[b]); mixes via 0x1d59f8 with counter Cj.fb++)
| site | kind,a,b | handler | notes |
|---|---|---|---|
| Dye 0x20097c | 10,81,ctx.f7 | closure 0x20088c (Dye _Sfa, "Z"/other button) then setState | b = value captured in context |
| Dye 0x2006cc | 12, a=!(Cj.f13&8), b=0 | _Nsa 0x20061c; then Cj.f13 ^= 8 (closure 0x200708) | toggle |
| Dye 0x20058c | 13, a=Cj.f1b (Smi value 0..2), 0 | _Lod 0x2004f4; then f1b=(f1b+1)%3 (0x2005c8) | NOTE: Cj here is the *Dye state's* own fields, not tfa (state field_13/17/1b) |
| Dye 0x200490 | 14, a=!(f17&8), 0 | _index 0x2003e0; then f17^=8 (0x2004cc) | toggle |
| Dye 0x1ffd48 | 15, a=1, b=!(f?&8) | closure 0x1ffc5c/0x1ffca8: if route=="/" push "/b" with 0x200038 args | navigation |
| Dye 0x200144 | 10,83,state.f13 | 0x2000c0 (route-change listener) then setState | |
| Eye 0x200804 | 10,82,ctx.f13 | Eye closure 0x200730 | |
| Eye 0x22157c | 15,2,0 | route '/b' push '/c' (0x221518 "/b", 0x221590 "/c") | |
| fwe 0x1d5920 | 2,82,0 | fn 0x1d58dc (tfa-level) | kind 2 a=81/82/83 at 0x1d62d8 / 0x1d5920 / 0x1d6340 |
| Fye 0x20126c | 16,... | dump screen _Wfa closure | |
CORRECTION to the above pattern: in Dye closures the LoadStaticField(0x784) result IS tfa Cj, and the loaded fields (0x13,0x17,0x1b) ARE Cj fields. BUT tfa field layout (alloc 0x1cefd4) is f7 bytes,fb counter,f13,f1b,f23,f2b zero-initialised, and f17 is ALSO read ("ArrayLoad r0[0]" = offset 0x17). The setState closures mutate the same Cj.f13 (xor 0x10 raw) / f17 (xor 0x10) / f1b (+1 mod 3).
   => Cj.f13/f1b are ALSO the dispose accumulators (kind 3 absorb: f13 += g, f1b ^= g). So user toggles and widget dispose mix into the same words, and kind 22 at dump uses f13^f1b, f23 (= dispose count).

## Build-time logging (qre.dart _wfa.build 0x1ed220 etc.)
- Each State builder calls log kinds during build: kind 6 (0x1ed14c, 0x1ed8b0), kind 8 (0x1ed618), kind 0xb (0x1ed1e4). So st.f47 (hash), st.f67 (counter) depend on number of builds/rebuilds. UNIT 01..04 card widgets (A:/B:/C: text = f67 counters).

## Status
Not completed: remaining unmapped = exact handlers of kinds 16/3 sites in Fye 0x20126c, cmd: console (Eye 0x221614), Jye/xre/cxe screens (k1..k6 etc.), timers. Brute-force plan (FEAT-003): the seal is deterministic given (a) which Dye/Eye taps happened (records 10..16), (b) set of live xt States (their f47 hashes, which depend on build counts and instance ids MHa), (c) dispose accumulators; enumerate action sequences and test FNV(hex)==0xEE2B5244.

## FEAT-007: terminal, Zone E, SESSION label (static + runtime)
- TERMINAL widget (xre.dart class _fga, builder closure 0x203298, timer closure 0x1d72d4) is a display-only log. A timer appends one of 25 fixed lines ([INIT]/[SCAN]/[AUTH]/[SEC ]/[WARN]/[INFO]/[SYS ] ...), then "[SCAN] Probe: 0x<LCG hex>" lines (LCG 1103515245/12345). The "> " prompt is a const Text (pp 0xffa8, class eda), and "controller" is its ScrollController. No TextField, no onSubmitted, no command parser exists. "SESSION:A7F2" is a const Text (pp 0xff90). "cmd:" (pp 0xc888) is only a label string in Eye. So typed commands do nothing.
- Zone E 7A/F2/3C: pressing them in any order/repeat before J2,J3,Z gives the identical a2 arg (-105625342 / 0x89e4c0cd) as J2,J3,Z, i.e. they do not touch Cj and add no record. Inert.
- MATCH closure 0x201ab4 -> 0x201b54: only FNV-1a32(hex string)==0xEE2B5244 (3995816516). No extra condition.
- Tested (explore.py): 7A,F2,J2,J3,Z; F2,7A,J2,J3,Z; 7A,F2,3C,J2,J3,Z; 3C,J2,J3,Z; 7A,F2,3C x2,J2,J3,Z; J2,J3,Z,BACKC,Z; J2,J3,BACKB,J3,Z; J2,J3,Z,Z. All DRIFT (or no status), same a2.
- Unit cards: UNIT 05 (builder kre.dart 0x1ec5d4, state field_67 in 0..2 shown as "A: I/II/III") is tappable. Tap handler _LJc (qre.dart 0x1ed168 -> 0x1ed1a0): per-state log(kind 11, v=field_67) via 0x1c3408, then setState with field_67=(field_67+1)%3. The build picks const [Jfa,Jfa,Jfa][field_67] and calls 0x1c3870(context, Jfa) (inherited-aspect lookup, result stored in field_6f = "B:"), then 0x1ed100 adds the aspect index to the State's set field_4f and logs kind 6 if it is new. This aspect set is the "dependency graph" that the dump snapshots (sfa.f17 = OR of 1<<index).
  Runtime: U5 changes the seal (U5,J2,J3,Z a2=1432371198; U5,U5,J2,J3,Z a2=1095621356; U5,U5,J1,J3,Z a2=1020582188). Taps on U1..U4, U6, U7, U4B leave a2 unchanged (-105625342), so they are not tappable.
- More sequences tested, all DRIFT: K1..K6 (asc and desc) then J2 or J1,J3,Z; J2,M1,M2,M3,J3,Z; J1,M1,M2,M3,J3,Z; U1..U5 each before J2,J3,Z; U6/U7/U4B on Panel B.
- Java side re-checked with androguard: MainActivity.l() and Lda.s a1/a2 match harness.c; MainActivity.g has no reads or writes in code that matter. So the harness reproduces the Android channel values.
- Harness note: running 8 explore.py instances in one call hung once (600 s timeout). Batches of 2-6 under `timeout 170` work. Do not use `pkill -f harness` or `pkill -f Xvfb` inside a tool command, because the pattern also matches the calling shell and kills it.
