#!/usr/bin/env python3
"""
Build a coin sequence leaving r8 == T (T up to ~0x1025b2), then quarter/cent/shilling.
Handles the initial carry flag (stc) by first clearing CF with a no-op 'sub r8,r9'.
"""

COIN_EFF = {
    'croeseid':('adc',8,1),'daric':('adc',9,2),'siglos':('adc',10,4),'karshapana':('adc',11,8),
    'tetradrachm':('adc',12,0x10),'stater':('adc',13,0x20),'obol':('adc',14,0x40),'lepton':('adc',15,0x80),
    'aureus':('adc',8,0x100),'solidus':('adc',9,0x200),'denarius':('adc',10,0x400),'antoninianus':('adc',11,0x800),
    'sestertius':('adc',12,0x1000),'florin':('adc',13,0x2000),'sequin':('adc',14,0x4000),'tremissis':('adc',15,0x8000),
    'dinar':('adc',8,0x10000),'dirham':('adc',8,0x20000),'scudo':('adc',8,0x40000),'thaler':('adc',8,0x80000),
    'real':('adc',9,0x20000),'piloncitos':('adc',10,0x40000),'koban':('adc',11,0x80000),
    'loonie':('sub',8,9),'krugerrand':('sub',8,10),'sovereign':('sub',8,11),'drachma':('sub',8,12),
    'penny':('sub',8,13),'nickel':('sub',8,14),'dime':('sub',8,15),
    'quarter':('lea',),'cent':('add_rax_r8',),'shilling':('jmp',),
}

def coin_add(reg, value):
    for nm,eff in COIN_EFF.items():
        if eff[0]=='adc' and eff[1]==reg and eff[2]==value:
            return nm
    raise KeyError((reg,value))

SUB_FOR_REG = {}
for nm,eff in COIN_EFF.items():
    if eff[0]=='sub':
        SUB_FOR_REG[eff[2]] = nm

LOW_BIT_REG = {2:9,4:10,8:11,0x10:12,0x20:13,0x40:14,0x80:15}
MID_BIT_REG = {0x200:9,0x400:10,0x800:11,0x1000:12,0x2000:13,0x4000:14,0x8000:15}
REG_DENOMS = {
    9:[0x20000,0x200,2], 10:[0x40000,0x400,4], 11:[0x80000,0x800,8],
    12:[0x1000,0x10], 13:[0x2000,0x20], 14:[0x4000,0x40], 15:[0x8000,0x80],
}

def plan(T):
    assert 0 <= T < (1<<21), hex(T)
    coins = ['loonie']   # sub r8,r9 (both 0) -> r8=0, CF=0. Clears the initial stc carry.

    # --- direct r8 high bits (16..20) ---
    high = T & ~0xFFFF  # bits 16+
    # represent 'high' with r8 denoms {0x10000,0x20000,0x40000,0x80000}, repeat 0x80000 for bit20
    rem = high
    for d in [0x80000, 0x40000, 0x20000, 0x10000]:
        while rem >= d:
            coins.append(coin_add(8, d))
            rem -= d
    assert rem == 0, hex(rem)

    # --- bit 0 and bit 8 direct ---
    if T & 1:
        coins.append(coin_add(8, 1))
    if T & 0x100:
        coins.append(coin_add(8, 0x100))

    reg_val = {r:0 for r in range(9,16)}

    # low transfer bits 1..7
    lo_hard = T & 0xFE
    if lo_hard:
        coins.append(coin_add(8, 0x100))      # overshoot
        sub_amt = 0x100 - lo_hard             # even, [2,0xFE]
        for val,reg in LOW_BIT_REG.items():
            if sub_amt & val:
                reg_val[reg] += val
    # mid transfer bits 9..15
    mid_hard = T & 0xFE00
    if mid_hard:
        coins.append(coin_add(8, 0x10000))    # overshoot
        sub_amt = 0x10000 - mid_hard          # multiple of 0x200, [0x200,0xFE00]
        for val,reg in MID_BIT_REG.items():
            if sub_amt & val:
                reg_val[reg] += val

    for reg in range(9,16):
        v = reg_val[reg]
        if v == 0: continue
        for d in REG_DENOMS[reg]:
            while v & d:
                coins.append(coin_add(reg, d))
                v -= d
        assert v == 0, (reg, hex(reg_val[reg]))
        coins.append(SUB_FOR_REG[reg])
    return coins

def simulate(coins):
    regs={r:0 for r in range(8,16)}
    cf=1  # initial stc
    M=(1<<64)-1
    for nm in coins:
        eff=COIN_EFF[nm]
        if eff[0]=='adc':
            _,reg,c=eff
            s=regs[reg]+c+cf
            regs[reg]=s&M; cf=1 if s>M else 0
        elif eff[0]=='sub':
            _,dst,src=eff
            s=regs[dst]-regs[src]
            cf=1 if s<0 else 0
            regs[dst]=s&M
    return regs

if __name__=="__main__":
    import random
    fails=0; worst=0
    for _ in range(50000):
        T=random.randint(0,0xfffd8)+0x25da
        coins=plan(T)
        r=simulate(coins)
        worst=max(worst,len(coins))
        if r[8]!=T:
            fails+=1
            if fails<6: print("FAIL T=%#x got %#x n=%d"%(T,r[8],len(coins)))
    print("fails:",fails,"worst arith coins:",worst,"(+3 => total, limit 31)")
