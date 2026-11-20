#!/usr/bin/env python3
import wave, struct, sys, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
w=wave.open("/work/noise.wav"); n=w.getnframes()
s=struct.unpack("<%dh"%n, w.readframes(n))
print("n",n,"min",min(s),"max",max(s))
uniq=len(set(s)); print("unique values",uniq)
# histogram of magnitude range
u=[x&0xFFFF for x in s]
cnt=collections.Counter(u)
print("most common sample values:", cnt.most_common(8))
# are values full-range uniform?
import statistics
print("mean",statistics.mean(s),"stdev",round(statistics.pstdev(s),1))
# low byte / high byte distribution
low=[x&0xFF for x in u]; high=[(x>>8)&0xFF for x in u]
print("unique low bytes",len(set(low)),"unique high bytes",len(set(high)))
# spectrum via numpy
import numpy as np
arr=np.array(s,dtype=np.float64)
F=np.abs(np.fft.rfft(arr))
print("FFT: dc",round(F[0],1),"max bin",int(np.argmax(F[1:])+1),"maxmag",round(F[1:].max(),1),"meanmag",round(F[1:].mean(),1))
# spectrogram image
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12,6))
    plt.specgram(arr, NFFT=1024, Fs=44100, noverlap=512)
    plt.savefig("/work/noise_spec.png",dpi=80)
    print("spectrogram saved")
except Exception as e:
    print("spec err",e)
