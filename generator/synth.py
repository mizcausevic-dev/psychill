"""Small numpy synth: renders a Format 1 arrangement to a stereo preview. Not a master."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, lfilter

from midi import BAR, PPQ

SR = 44100
VERSION = 'claude-simple-synth-1.0.0'
LEVEL = {'drums': 0.9, 'bass': 0.75, 'keys': 0.32, 'motif': 0.38, 'sequence': 0.26, 'pad': 0.28}
PAN = {'drums': 0.0, 'bass': 0.0, 'keys': -0.25, 'motif': 0.15, 'sequence': 0.3, 'pad': 0.0}
SEND = {'drums': 0.05, 'bass': 0.0, 'keys': 0.8, 'motif': 1.0, 'sequence': 0.7, 'pad': 1.0}


def hz(p):
    return 440.0 * 2 ** ((p - 69) / 12)


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def hp(x):
    return np.concatenate([[0], np.diff(x)])


def adsr(n, a=0.005, d=0.1, s=0.7, r=0.05, gate=None):
    gate = n if gate is None else gate
    t = np.arange(n)
    e = np.ones(n)
    ai, di = max(1, int(a * SR)), max(1, int(d * SR))
    e[:ai] = np.linspace(0, 1, ai)
    seg = slice(ai, ai + di)
    m = len(e[seg])
    e[seg] = np.linspace(1, s, di)[:m]
    e[ai + di:] = s
    ri = max(1, int(r * SR))
    if gate < n:
        e[gate:] = e[gate - 1] * np.linspace(1, 0, n - gate) ** 2 if n - gate > 0 else 0
    return e


def osc(kind, f, n, t0=0):
    t = (np.arange(n) + t0) / SR
    if kind == 'sine':
        return np.sin(2 * np.pi * f * t)
    if kind == 'tri':
        return 2 * np.abs(2 * ((f * t) % 1) - 1) - 1
    if kind == 'saw':
        return 2 * ((f * t) % 1) - 1
    raise ValueError(kind)


def noise(n, rng):
    return rng.standard_normal(n)


def drum(pitch, vel, rng, kick_kind):
    v = vel / 127.0
    if pitch == 36:
        n = int(0.55 * SR)
        t = np.arange(n) / SR
        f0, f1, tau = (165, 48, 0.045) if kick_kind == '909' else (115, 44, 0.07)
        f = f1 + (f0 - f1) * np.exp(-t / tau)
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = np.sin(ph) * np.exp(-t / (0.16 if kick_kind == '909' else 0.28))
        y[:int(0.004 * SR)] += np.linspace(0.6, 0, int(0.004 * SR))
        return y * v * 1.1
    if pitch == 37:
        n = int(0.08 * SR)
        t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1700 * t) * 0.5 + hp(noise(n, rng)) * 0.4) * np.exp(-t / 0.015) * v
    if pitch in (38, 40):
        n = int(0.28 * SR)
        t = np.arange(n) / SR
        f = 190 if pitch == 38 else 250
        body = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.05)
        nz = hp(hp(noise(n, rng))) * np.exp(-t / (0.09 if pitch == 38 else 0.06))
        return (body * 0.5 + nz * 0.9) * v
    if pitch == 39:
        n = int(0.3 * SR)
        y = np.zeros(n)
        t = np.arange(n) / SR
        nz = hp(noise(n, rng))
        for off in (0, 0.011, 0.022):
            i = int(off * SR)
            y[i:] += nz[:n - i] * np.exp(-np.arange(n - i) / SR / 0.012)
        y += nz * np.exp(-t / 0.09) * 0.6
        return y * v * 0.8
    if pitch == 42:
        n = int(0.06 * SR)
        t = np.arange(n) / SR
        return hp(hp(noise(n, rng))) * np.exp(-t / 0.012) * v * 0.7
    if pitch == 46:
        n = int(0.3 * SR)
        t = np.arange(n) / SR
        return hp(hp(noise(n, rng))) * np.exp(-t / 0.07) * v * 0.6
    if pitch == 49:
        n = int(1.6 * SR)
        t = np.arange(n) / SR
        return hp(hp(noise(n, rng))) * np.exp(-t / 0.5) * v * 0.55
    return np.zeros(10)


def voice(role, timbre, pitch, vel, dur_s, rng):
    f = hz(pitch)
    v = vel / 127.0
    tail = 0.35 if role != 'pad' else 0.7
    n = int((dur_s + tail) * SR)
    gate = int(dur_s * SR)
    if role == 'bass':
        kind = timbre['bass']
        if kind == 'sub':
            y = osc('sine', f, n) + 0.25 * osc('sine', 2 * f, n)
            e = adsr(n, 0.008, 0.2, 0.8, 0.06, gate)
        elif kind == 'pluck':
            y = lp(osc('saw', f, n), 700) + 0.4 * osc('sine', f, n)
            e = np.exp(-np.arange(n) / SR / 0.35) * adsr(n, 0.004, 0.05, 1, 0.05, gate)
        else:
            y = lp(osc('saw', f, n), 480 if f < 120 else 900) + 0.35 * osc('sine', f, n)
            e = adsr(n, 0.005, 0.12, 0.7, 0.05, gate)
        return y * e * v
    if role == 'keys' or (role == 'motif' and timbre['motif'] in ('piano',)):
        kind = timbre['keys'] if role == 'keys' else 'piano'
        t = np.arange(n) / SR
        if kind == 'epiano':
            y = osc('sine', f, n) + 0.5 * osc('sine', 2 * f, n) * np.exp(-t / 0.25) + 0.15 * osc('sine', 4 * f, n) * np.exp(-t / 0.08)
            e = np.exp(-t / 1.1) * adsr(n, 0.004, 0.05, 1, 0.12, gate)
        elif kind == 'piano':
            y = sum(a * osc('sine', k * f, n) * np.exp(-t / (0.9 / k)) for k, a in ((1, 1), (2, .55), (3, .3), (4, .18), (5, .1)))
            e = adsr(n, 0.003, 0.05, 1, 0.14, gate)
        elif kind == 'pluck':
            y = lp(osc('saw', f, n), 1800) * np.exp(-t / 0.22)
            e = adsr(n, 0.003, 0.05, 1, 0.08, gate)
        else:  # soft
            y = osc('sine', f, n) + 0.4 * osc('sine', 2 * f, n) + 0.2 * osc('sine', 3 * f, n)
            e = adsr(n, 0.012, 0.15, 0.6, 0.15, gate)
        return y * e * v * 0.7
    if role == 'motif':
        kind = timbre['motif']
        t = np.arange(n) / SR
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.3)
        if kind == 'bell':
            y = osc('sine', f, n) + 0.5 * osc('sine', 2.76 * f, n) * np.exp(-t / 0.4) + 0.25 * osc('sine', 5.4 * f, n) * np.exp(-t / 0.15)
            e = np.exp(-t / 0.9) * adsr(n, 0.003, 0.05, 1, 0.2, gate)
        elif kind == 'saw':
            y = lp(0.6 * osc('saw', f * vib, n) + 0.6 * osc('saw', f * 1.004, n), 2600)
            e = adsr(n, 0.01, 0.15, 0.75, 0.12, gate)
        elif kind == 'soft':
            y = osc('tri', f * vib, n) * 0.8 + 0.2 * osc('sine', 2 * f, n)
            e = adsr(n, 0.02, 0.15, 0.7, 0.18, gate)
        else:  # sine
            y = osc('sine', f * vib, n) + 0.15 * osc('sine', 2 * f, n)
            e = adsr(n, 0.015, 0.12, 0.8, 0.15, gate)
        return y * e * v
    if role == 'sequence':
        kind = timbre['seq']
        t = np.arange(n) / SR
        if kind == 'tri':
            y = osc('tri', f, n) * np.exp(-t / 0.3)
        elif kind == 'pluck':
            y = lp(osc('saw', f, n), 1500) * np.exp(-t / 0.18)
        else:
            y = lp(osc('saw', f, n), 2200) * np.exp(-t / 0.25)
        return y * adsr(n, 0.003, 0.05, 1, 0.06, gate) * v
    if role == 'pad':
        y = (osc('saw', f * 0.997, n) + osc('saw', f, n) + osc('saw', f * 1.003, n)) / 3
        y = lp(y, 1300)
        e = adsr(n, 0.35, 0.4, 0.8, 0.5, gate)
        return y * e * v
    return np.zeros(10)


def render(tracks, bpm, timbre, start_bar, end_bar, seed=7):
    """tracks: list of (role, notes[(tick, dur, pitch, vel)]). Renders bars [start_bar, end_bar)."""
    rng = np.random.default_rng(seed)
    spt = 60.0 / (bpm * PPQ)
    t0, t1 = start_bar * BAR, end_bar * BAR
    total = int((t1 - t0) * spt * SR) + int(2.2 * SR)
    dry = np.zeros((2, total))
    wet = np.zeros((2, total))
    for role, notes in tracks:
        for tick, dur, pitch, vel in notes:
            if tick < t0 or tick >= t1:
                continue
            at = int((tick - t0) * spt * SR)
            if role == 'drums':
                y = drum(pitch, vel, rng, timbre['kick'])
            else:
                y = voice(role, timbre, pitch, vel, dur * spt, rng)
            y = y * LEVEL[role]
            pan = PAN[role]
            gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            n = min(len(y), total - at)
            dry[0, at:at + n] += y[:n] * gl
            dry[1, at:at + n] += y[:n] * gr
            if role == 'pad':  # width: delay the right channel a little
                d = int(0.012 * SR)
                m = min(n, total - at - d)
                if m > 0:
                    dry[1, at + d:at + d + m] += y[:m] * 0.3
            s = SEND[role]
            if s:
                wet[0, at:at + n] += y[:n] * s * gl
                wet[1, at:at + n] += y[:n] * s * gr
    ir_n = int(1.8 * SR)
    tt = np.arange(ir_n) / SR
    out = dry.copy()
    for c in range(2):
        ir = rng.standard_normal(ir_n) * np.exp(-tt / 0.45)
        ir = lp(ir, 5000) * 0.02
        out[c] += fftconvolve(wet[c], ir)[:total] * timbre['verb'] * 3
    # fade the last 0.2 s, soft clip, normalise to about -1 dBFS sample peak
    keep = int((t1 - t0) * spt * SR)
    out = out[:, :keep]
    fade = int(0.15 * SR)
    out[:, -fade:] *= np.linspace(1, 0, fade)
    out = np.tanh(out * 1.1)
    # master level: about -17 dBFS RMS, sample peak held under -1 dBFS
    rms = float(np.sqrt(np.mean(out ** 2))) or 1.0
    out = out * (10 ** (-17 / 20) / rms)
    peak = float(np.max(np.abs(out)))
    if peak > 0.891:
        out = out * (0.891 / peak)
    return out, float(np.max(np.abs(out)))


def write_wav(path, stereo):
    wavfile.write(path, SR, (stereo.T * 32767).astype(np.int16))
