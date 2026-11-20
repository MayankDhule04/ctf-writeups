import importlib.util
spec=importlib.util.spec_from_file_location("emu", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate.py")
emu=importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

def ok(s):
    if len(s)!=32: return None
    r,st,fv=emu.run2(s.encode())
    return r,fv

# Candidate inner contents (25 chars) for IATCQ{....} 32 total => inner len 25
inners=[
 "custom_vm_reverse_engine!",
 "custom_virtual_machine123",
 "the_little_machine_runs_x",
 "underneath_the_0s_and_1ss",
 "quiet_steps_till_the_endx",
 "32_bytes_walkthrough_okay",
 "a_custom_vm_with_aes_sbox",
 "reverse_the_custom_vm_now",
 "vm_crackme_solved_by_you1",
 "hidden_machine_own_ruless",
 "w4lk_thr0ugh_the_32_bytes",
 "custom_vm_is_fun_to_solve",
 "0s_and_1s_hide_a_machinex",
 "temporal_vm_reverse_me_ok",
]
for inner in inners:
    s="IATCQ{"+inner+"}"
    if len(s)==32:
        r,fv=ok(s)
        print(f"{'HIT' if r else '   '} fnv={fv:08x} {s}")
    else:
        print("LEN", len(s), s)
