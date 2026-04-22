import math, numpy as np
from scipy.io import wavfile

SR = 48000
BPM = 124
BEATS_PER_BAR = 4
BARS = 8
DURATION = (60 / BPM) * BEATS_PER_BAR * BARS
N = int(SR * DURATION)

def normalize(x, peak=0.92):
    m = np.max(np.abs(x)) + 1e-12
    return (x / m) * peak

def midi_to_freq(m):
    return 440.0 * (2 ** ((m - 69) / 12.0))

def adsr_env(length, a=0.01, d=0.08, s=0.8, r=0.02, sr=SR):
    n = max(1, int(length * sr))
    env = np.ones(n)
    na = max(1, int(a * sr))
    nd = max(1, int(d * sr))
    nr = max(1, int(r * sr))
    sustain_start = min(n, na + nd)
    sustain_end = max(sustain_start, n - nr)
    env[:na] = np.linspace(0, 1, na, endpoint=False)
    if sustain_start > na:
        env[na:sustain_start] = np.linspace(1, s, sustain_start - na, endpoint=False)
    env[sustain_start:sustain_end] = s
    if n > sustain_end:
        env[sustain_end:] = np.linspace(env[sustain_end - 1] if sustain_end > 0 else s, 0, n - sustain_end, endpoint=True)
    return env

def make_wavetable(kind, size=2048):
    phase = np.linspace(0, 1, size, endpoint=False)
    if kind == "warm_saw":
        wt = sum(np.sin(2*np.pi*n*phase)/n for n in range(1, 32))
    elif kind == "glass_tri":
        wt = sum(((-1)**((n-1)//2)) * (np.sin(2*np.pi*n*phase)/(n*n)) for n in range(1, 32, 2))
    elif kind == "vocal_form":
        base = np.sin(2*np.pi*phase)
        base += 0.5*np.sin(2*np.pi*2*phase + 0.2)
        base += 0.28*np.sin(2*np.pi*3*phase + 1.1)
        base += 0.18*np.sin(2*np.pi*5*phase + 2.3)
        wt = np.tanh(1.3*base)
    else:
        wt = np.sin(2*np.pi*phase)
    return wt / (np.max(np.abs(wt)) + 1e-12)

def segment_osc(freq, wavetable, n, sr=SR, phase0=0.0):
    phase = (phase0 + np.cumsum(np.full(n, freq / sr))) % 1.0
    size = len(wavetable)
    pos = phase * size
    i0 = np.floor(pos).astype(np.int32)
    frac = pos - i0
    i1 = (i0 + 1) % size
    return wavetable[i0] * (1 - frac) + wavetable[i1] * frac, float(phase[-1])

# This file is a minimal starter extracted from the full pack generator.
