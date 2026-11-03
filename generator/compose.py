"""Deterministic note-only composition for the construction kits. Seeds name kits; nothing is drawn at run time."""
import random
import zlib

from midi import BAR, STEP

PC = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
      'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
MODES = {
    'ionian': [0, 2, 4, 5, 7, 9, 11], 'mixolydian': [0, 2, 4, 5, 7, 9, 10], 'lydian': [0, 2, 4, 6, 7, 9, 11],
    'dorian': [0, 2, 3, 5, 7, 9, 10], 'aeolian': [0, 2, 3, 5, 7, 8, 10], 'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'harmonic minor': [0, 2, 3, 5, 7, 8, 11],
}
QUAL = {
    'maj': [0, 4, 7], 'min': [0, 3, 7], 'dom7': [0, 4, 7, 10], 'maj7': [0, 4, 7, 11], 'min7': [0, 3, 7, 10],
    'min9': [0, 3, 7, 10, 14], 'maj9': [0, 4, 7, 11, 14], 'dom9': [0, 4, 7, 10, 14], 'dom13': [0, 4, 10, 14, 21],
    'min11': [0, 3, 7, 10, 17], 'm7b5': [0, 3, 6, 10], 'sus2': [0, 2, 7], 'sus4': [0, 5, 7],
    'dom7s9': [0, 4, 7, 10, 15], 'maj6': [0, 4, 7, 9], 'min6': [0, 3, 7, 9], 'add9': [0, 4, 7, 14],
    'dom7b9': [0, 4, 7, 10, 13], 'dim7': [0, 3, 6, 9],
}
DRUM_PITCH = {'kick': 36, 'rim': 37, 'snare': 38, 'clap': 39, 'esnare': 40, 'chat': 42, 'ohat': 46, 'crash': 49}
DRUM_MAP = sorted(DRUM_PITCH.values())
CHANNEL = {'drums': 9, 'bass': 0, 'keys': 1, 'motif': 2, 'sequence': 3, 'pad': 4}
POLY = {'drums': 4, 'bass': 1, 'keys': 4, 'motif': 1, 'sequence': 1, 'pad': 4}
ROLES = ['drums', 'bass', 'keys', 'motif', 'sequence', 'pad']
VEL = {'x': 112, 'o': 98, 'g': 56}


def fit16(s):
    return (s + '.' * 16)[:16]


def seed_of(*parts):
    return zlib.crc32('|'.join(str(p) for p in parts).encode())


def expand(prog):
    bars = []
    for root, q, n in prog:
        bars += [(PC[root], q)] * n
    assert len(bars) == 8, prog
    return bars


# ---------- drums ----------
# Lanes are 16-step strings: x accent, o normal, g ghost, . rest. B overrides lanes of A. fill replaces lanes in bar 8.
DR = {
    'trance': dict(A=dict(kick='x...x...x...x...', clap='....x.......x...', ohat='..o...o...o...o.', chat='.g.g.g.g.g.g.g.g'),
                   B=dict(rim='...g.......g...g', chat='g.gg.g.gg.g.gg.g'),
                   fill=dict(esnare='........g.g.ogox', clap='....x...........'), crash=(0,), crashB=(0, 4)),
    'uplift': dict(A=dict(kick='x...x...x...x...', clap='....x.......x...', ohat='..o...o...o...o.', chat='.g.g.g.g.g.g.g.g'),
                   B=dict(chat='gggggggggggggggg', rim='.......g.......g'),
                   fill=dict(esnare='......g.g.g.oxox', clap='....x...........'), crash=(0, 4), crashB=(0,)),
    'fx': dict(A=dict(kick='x.......x.....x.', rim='g..g..g..g..g...', ohat='....o.......o...', chat='.g.gg..g.g.gg..g'),
               B=dict(kick='x.....x...x.....', clap='........x.......', rim='..g..g...g..g..g'),
               fill=dict(esnare='g.g.g.g.gggxxxxx'), crash=(0, 4), crashB=(0,)),
    'chill': dict(A=dict(kick='x.....g...x.....', snare='........x.......', chat='.g.g.g.g.g.g.g.g', ohat='......o.......o.'),
                  B=dict(rim='g..g..g.g..g..g.', clap='........g.......'),
                  fill=dict(esnare='........x.g.oxox'), crash=(0,), crashB=(0, 4)),
    'neosoul': dict(A=dict(kick='x.....g...x...g.', snare='....g.......x...', chat='x.g.x.g.x.g.x.g.', ohat='..............o.'),
                    B=dict(kick='x......g..x.....', esnare='.......g.......g', rim='....g...........'),
                    fill=dict(snare='....g.......x.gx'), crash=(0,), crashB=(0,), swing=70, late=dict(snare=36, esnare=24)),
    'bossa': dict(A=dict(kick='x.....x.x.....x.', rim='x..x..x...x.x...', chat='x.x.x.x.x.x.x.x.'),
                  B=dict(rim='x..x..x..x..x...', ohat='..............o.'),
                  fill=dict(rim='x.x.x.x.x.x.xxxx'), crash=(0,), crashB=(0, 4)),
    'rnb90': dict(A=dict(kick='x......x..x.....', snare='....x.......x...', clap='....x.......x...', chat='x.x.x.x.x.x.x.x.', esnare='.......g.......g'),
                  B=dict(kick='x..x....x.x.....', chat='x.xgx.xgx.xgx.xg', ohat='..............o.'),
                  fill=dict(snare='....x.......x.xx'), crash=(0,), crashB=(0, 4), swing=80),
    'njs': dict(A=dict(kick='x.....x..x......', snare='....x.......x...', clap='....x.......x...', chat='xgxxxgxxxgxxxgxx', esnare='.g...g....g...g.'),
                B=dict(kick='x..x..x..x..x...', ohat='..o.......o.....'),
                fill=dict(snare='....x...x.x.xxxx'), crash=(0,), crashB=(0, 4), swing=85),
    'house': dict(A=dict(kick='x...x...x...x...', clap='....x.......x...', ohat='..o...o...o...o.', chat='.g.g.g.g.g.g.g.g'),
                  B=dict(rim='...g.......g...g', chat='g.g.g.g.g.g.g.g.'),
                  fill=dict(clap='....x.......xxxx'), crash=(0,), crashB=(0, 4)),
    'euro': dict(A=dict(kick='x...x...x...x...', snare='....x.......x...', clap='....x.......x...', ohat='..o...o...o...o.', chat='x.x.x.x.x.x.x.x.'),
                 B=dict(esnare='..............g.', chat='xgxgxgxgxgxgxgxg'),
                 fill=dict(snare='........g.g.oxxx'), crash=(0, 4), crashB=(0,)),
}


def make_drums(style, var, kit_i, rng, bars=8):
    d = DR[style]
    swing = d.get('swing', 0)
    late = d.get('late', {})
    notes = []
    for b in range(bars):
        lanes = dict(d['A'])
        if var == 'b':
            lanes.update(d['B'])
        if b == bars - 1:
            lanes.update(d['fill'])
        crash = d['crash'] if var == 'a' else d['crashB']
        for name, pat in lanes.items():
            pat = fit16(pat)
            pitch = DRUM_PITCH[name]
            for s, ch in enumerate(pat):
                if ch == '.':
                    continue
                t = b * BAR + s * STEP
                if swing and s % 2 == 1:
                    t += swing
                t += late.get(name, 0)
                vel = max(1, min(127, VEL[ch] + rng.randint(-5, 5)))
                dur = 700 if name in ('ohat',) else 180
                notes.append((t, dur, pitch, vel))
        if b in crash:
            notes.append((b * BAR, 1800, DRUM_PITCH['crash'], 108))
    return clean_percussion(notes)


def clean_percussion(notes):
    """Drop a repeat of the same pitch at the same tick."""
    seen, out = set(), []
    for n in sorted(notes):
        key = (n[0], n[2])
        if key in seen:
            continue
        seen.add(key)
        out.append(n)
    # end an open note before the same pitch retriggers
    last = {}
    res = []
    for i, n in enumerate(out):
        res.append(list(n))
    by_pitch = {}
    for i, n in enumerate(res):
        by_pitch.setdefault(n[2], []).append(i)
    for idxs in by_pitch.values():
        for a, b in zip(idxs, idxs[1:]):
            if res[a][0] + res[a][1] > res[b][0]:
                res[a][1] = max(1, res[b][0] - res[a][0])
    return [tuple(n) for n in res]


# ---------- pitch helpers ----------
def pitch_in(pc, lo, hi, near):
    best = None
    for p in range(lo, hi + 1):
        if p % 12 == pc and (best is None or abs(p - near) < abs(best - near)):
            best = p
    return best


def scale_pitches(root_pc, mode, lo, hi):
    pcs = {(root_pc + i) % 12 for i in MODES[mode]}
    return [p for p in range(lo, hi + 1) if p % 12 in pcs]


def chord_pcs(root_pc, q):
    return [(root_pc + i) % 12 for i in QUAL[q]]


def voicing(root_pc, q, center, n, lo, hi, drop_root=False):
    ints = QUAL[q]
    # priority: third, seventh or sixth, extension, fifth, root
    third = ints[1]
    rest = [i for i in ints[2:]]
    order = [third] + rest[::-1] + [0]
    if drop_root:
        order = [i for i in order if i != 0] or order
    pcs, seen = [], set()
    for i in order + ints:
        pc = (root_pc + i) % 12
        if pc not in seen:
            seen.add(pc)
            pcs.append(pc)
        if len(pcs) == n:
            break
    pitches = []
    for pc in pcs:
        p = pitch_in(pc, lo, hi, center)
        pitches.append(p)
    pitches = sorted(set(pitches))
    k = 0
    while len(pitches) < n:
        base = pitches[k % len(pitches)] + 12
        if base <= hi and base not in pitches:
            pitches.append(base)
        k += 1
        if k > 12:
            break
        pitches.sort()
    return sorted(pitches)[:n]


def parse_cells(cell, vel_acc=None):
    """16-char rhythm string to [(step, length_in_steps)]."""
    cell = fit16(cell)
    out, i = [], 0
    while i < 16:
        if cell[i] == 'x':
            j = i + 1
            while j < 16 and cell[j] == '-':
                j += 1
            out.append((i, j - i))
            i = j
        else:
            i += 1
    return out


# ---------- bass ----------
BASS = {
    'trance': ('..r-..r-..r-..r-', '.r-.r-.r-.r-.r-.'),
    'uplift': ('..rr..rr..rr..rr', '.rr.rr.rf.ro.rf.'),
    'fx': ('r-------r-------', 'r-----f-r---o---'),
    'chill': ('r--.....r-f.....', 'r-----f.o-..r-..'),
    'neosoul': ('r-..r--.f-..o-a.', 'r--.-r..f.r-.a.o'),
    'bossa': ('r-----f-r-----f-', 'r-----f-r---a-f-'),
    'rnb90': ('r--.r-..f--.r-a.', 'r-.r--.f-.t-..a.'),
    'njs': ('r-.r-r..r-.rf-a.', 'r-.r-.r-o..rf.a.'),
    'house': ('r-.r-.r-.r-.r-.r', '..r-..r-..r-..r-'),
    'euro': ('.o.r.o.r.o.r.o.r', '.o-r-.o-r-.o-r-.'),
}


def make_bass(style, var, chords, lo, hi, rng, kit_i):
    pat = BASS[style][0 if var == 'a' else 1]
    pat = fit16(pat)
    notes = []
    for b in range(8):
        pc, q = chords[b]
        npc, nq = chords[(b + 1) % 8]
        root = pitch_in(pc, lo, lo + 11, lo + 5)
        fifth = root + 7 if root + 7 <= hi else root - 5
        octv = root + 12 if root + 12 <= hi else root
        third = root + (QUAL[q][1])
        nroot = pitch_in(npc, lo, lo + 11, lo + 5)
        appr = nroot - 1 if nroot - 1 >= lo else nroot + 1
        sym = {'r': root, 'f': fifth, 'o': octv, 't': third, 'a': appr}
        i = 0
        while i < 16:
            ch = pat[i]
            if ch in sym:
                j = i + 1
                while j < 16 and pat[j] == '-':
                    j += 1
                dur = int((j - i) * STEP * 0.92)
                vel = max(1, min(127, (104 if i % 4 == 0 else 92) + rng.randint(-5, 5)))
                notes.append((b * BAR + i * STEP, dur, min(hi, max(lo, sym[ch])), vel))
                i = j
            else:
                i += 1
    return notes


# ---------- keys and pad ----------
KEYS = {
    'trance': ('x---------------', 'x-----x-----x---'),
    'uplift': ('x.x.x.x.x.x.x.x.', 'x---x---x---x---'),
    'fx': ('x---------------', 'x.......x.......'),
    'chill': ('x-------x-------', 'x....x..x..x....'),
    'neosoul': ('x.x-..x-..x...x.', 'x..x--.x-.x.....'),
    'bossa': ('x..x..x...x..x..', 'x..x..x.x-.x....'),
    'rnb90': ('x-----x-x-.....x', 'x--x-.x-----x...'),
    'njs': ('x..x.x..x..x.x..', 'x.x--x..x-x..x..'),
    'house': ('x..x..x...x.x...', 'x.x.x.x.x.x.x.x.'),
    'euro': ('x.x.x.x.x.x.x.x.', 'x..x..x.x..x..x.'),
}


def make_keys(style, var, chords, lo, hi, rng, kit_i, center=62):
    pat = fit16(KEYS[style][0 if var == 'a' else 1])
    cen = center if var == 'a' else center + 4
    notes = []
    for b in range(8):
        pc, q = chords[b]
        v = voicing(pc, q, cen, 4, lo, hi, drop_root=True)
        hits = parse_cells(pat)
        for s, ln in hits:
            dur = max(120, int(ln * STEP * 0.95))
            if ln == 1:
                dur = int(STEP * 1.6)
            dur = min(dur, (16 - s) * STEP - 20)
            vel = max(1, min(127, 84 + rng.randint(-6, 6)))
            for p in v:
                notes.append((b * BAR + s * STEP, dur, p, vel))
    return notes


def make_pad(chords, lo, hi, rng, kit_i, var, center=60):
    cen = center if var == 'a' else center + 5
    notes, b = [], 0
    while b < 8:
        j = b + 1
        while j < 8 and chords[j] == chords[b]:
            j += 1
        pc, q = chords[b]
        v = voicing(pc, q, cen, 4, lo, hi)
        length = (j - b) * BAR
        if var == 'b':
            segs = [((b + k) * BAR, BAR) for k in range(j - b)]
        else:
            segs = [(b * BAR, length)]
        for s, ln in segs:
            for p in v:
                notes.append((s, ln - 60, p, 72 + rng.randint(-4, 4)))
        b = j
    return notes


# ---------- motif ----------
CELLS = {
    'slow': (['x---..x-x---....', 'x-x-x---..x-....', 'x-----x-x-x-....', '..x-x-x-x---....'],
             ['x-x-..x---x-....', 'x---x-x-x-......', '..x---x-x---x-..', 'x-----x---x-x-..']),
    'steady': (['x-x-x-x-x-x-x---', 'x-x-x---x-x-x---', 'x-x-x-x---x-x---', 'x---x-x-x-x-x---'],
               ['x-x-x---x-x-x-x-', 'x---x-x-x---x-x-', 'x-x---x-x-x---x-', 'x-x-x-x-x---x---']),
    'sync': (['x..x..x-..x-..x.', 'x-.x..x...x.x...', '..x-.x-.x..x-...', 'x..x-.x..x-.....'],
             ['.x-.x-.x-..x-.x.', 'x-.x-.x-.x..x...', '..x..x-.x-.x-...', 'x.x-..x-..x..x-.']),
    'rnb': (['x--.x-..x---..x.', '..x-.x-.x--.....', 'x-.x--.x-.x-....', '.x--.x-x--.x-...'],
            ['x---.x--.x-.x...', '.x-x--.x-..x-...', 'x.x--.x--.x.....', '..x--x-.x---x...']),
    'bossa': (['x--x--x-.x-x--..', 'x-x--x--x-x-....', '..x-x--x--x-x---', 'x--x-x--x--.x---'],
              ['x-x--x-x--x--x--', 'x--x--x--x-x-...', '.x--x-x--x--x-..', 'x-x-x--x-x--....']),
}


def make_motif(family, var, chords, root_pc, mode, lo, hi, rng, kit_i, hi_cap=None):
    cellsA, cellsB = CELLS[family]
    cells = cellsA if var == 'a' else cellsB
    top = hi_cap or hi
    scale = scale_pitches(root_pc, mode, lo, top)
    mid = lo + (top - lo) * (0.38 + 0.07 * (kit_i % 4)) + (0 if var == 'a' else 3)
    ci = min(range(len(scale)), key=lambda i: abs(scale[i] - mid))
    cur = ci
    order = [0, 1, 0, 2, 0, 1, 3, 4]
    picks = [rng.choice(cells), rng.choice(cells)]
    rhythm = []
    for b in range(8):
        if b == 7:
            rhythm.append('x-------------..' if var == 'a' else 'x---x-----------.')
        elif b in (2, 4, 6):
            rhythm.append(picks[0])
        elif b in (3, 5):
            rhythm.append(picks[1] if b == 3 else rng.choice(cells))
        else:
            rhythm.append(picks[b % 2])
    notes = []
    prev = []
    for b in range(8):
        pc, q = chords[b]
        ctones = set(chord_pcs(pc, q))
        for s, ln in parse_cells(rhythm[b]):
            if s % 4 == 0:
                cands = [i for i in range(max(0, cur - 3), min(len(scale), cur + 4)) if scale[i] % 12 in ctones]
                if cands:
                    cur = min(cands, key=lambda i: (abs(i - cur), rng.random()))
            else:
                cur += rng.choice([-2, -1, -1, 0, 1, 1, 2])
            cur = max(ci - 5, min(ci + 5, cur, len(scale) - 1))
            cur = max(0, cur)
            if len(prev) >= 2 and prev[-1] == prev[-2] == cur:
                cur = max(0, min(len(scale) - 1, cur + rng.choice([-1, 1])))
            prev.append(cur)
            if b == 7 and s == 0:
                tones = [i for i in range(len(scale)) if scale[i] % 12 == pc] or [i for i in range(len(scale)) if scale[i] % 12 in ctones] or [cur]
                cur = min(tones, key=lambda i: abs(i - cur))
            dur = int(ln * STEP * 0.92)
            vel = max(1, min(127, (100 if s % 4 == 0 else 88) + rng.randint(-5, 5)))
            notes.append((b * BAR + s * STEP, dur, scale[cur], vel))
    return notes


# ---------- sequence ----------
MASKS = {'full': 'xxxxxxxxxxxxxxxx', 'eighth': 'x.x.x.x.x.x.x.x.', 'sync': 'x..x..x..x..x.x.', 'sparse': 'x.....x...x.....',
         'offbeat': '.x.x.x.x.x.x.x.x', 'rolling': '.xxx.xxx.xxx.xxx'}
IDX = {'up': [0, 1, 2, 3] * 4, 'updown': [0, 1, 2, 3, 2, 1] * 3, 'skip': [0, 2, 1, 3] * 4,
       'pedal': [0, 2, 0, 3, 0, 2, 0, 1] * 2, 'acid': [0, 0, 2, 0, 0, 3, 0, 2, 0, 0, 2, 0, 3, 0, 1, 0]}
SEQ = {  # style: (maskA, idxA, maskB, idxB)
    'trance': ('full', 'updown', 'sparse', 'up'), 'uplift': ('full', 'up', 'eighth', 'updown'),
    'fx': ('rolling', 'acid', 'sparse', 'pedal'), 'chill': ('eighth', 'updown', 'sparse', 'skip'),
    'neosoul': ('sync', 'skip', 'sparse', 'up'), 'bossa': ('sync', 'pedal', 'sparse', 'skip'),
    'rnb90': ('sync', 'updown', 'sparse', 'pedal'), 'njs': ('eighth', 'skip', 'sparse', 'up'),
    'house': ('offbeat', 'pedal', 'sparse', 'updown'), 'euro': ('eighth', 'up', 'sparse', 'skip'),
}


def make_sequence(style, var, chords, lo, hi, rng, kit_i):
    ma, ia, mb, ib = SEQ[style]
    mask = MASKS[ma if var == 'a' else mb]
    idx = IDX[ia if var == 'a' else ib]
    notes = []
    for b in range(8):
        pc, q = chords[b]
        ints = QUAL[q]
        tones = []
        base = 55 + 2 * (kit_i % 4) + (5 if var == 'b' else 0)
        for i in ints[:4]:
            p = pitch_in((pc + i) % 12, lo, hi, base + len(tones) * 4)
            tones.append(p)
        tones = sorted(set(tones))
        while len(tones) < 4:
            tones.append(min(hi, tones[0] + 12 * (len(tones) // 2 + 1)))
            tones = sorted(set(tones))
        for s in range(16):
            if mask[s] != 'x':
                continue
            p = tones[idx[s] % len(tones)]
            if style in ('trance', 'uplift') and s % 8 == 7 and p + 12 <= hi:
                p += 12
            vel = max(1, min(127, (96 if s % 4 == 0 else 80) + rng.randint(-5, 5)))
            dur = int(STEP * (1.7 if mask == MASKS['sparse'] else 0.8))
            notes.append((b * BAR + s * STEP, dur, p, vel))
    return notes


def compose_kit(prof, kit, kit_i):
    """Returns {role: {'a': notes, 'b': notes}} with ticks inside an 8-bar part."""
    chords = expand(kit['prog'])
    root_pc = PC[kit['root']]
    r = prof['ranges']
    out = {}
    for var in ('a', 'b'):
        base = seed_of(prof['slug'], kit['id'], var)
        out.setdefault('drums', {})[var] = make_drums(prof['drums'], var, kit_i, random.Random(base + 1))
        out.setdefault('bass', {})[var] = make_bass(prof['drums'], var, chords, r['bass'][0], r['bass'][1], random.Random(base + 2), kit_i)
        out.setdefault('keys', {})[var] = make_keys(prof['drums'], var, chords, r['keys'][0], r['keys'][1], random.Random(base + 3), kit_i, prof.get('keys_center', 62))
        out.setdefault('motif', {})[var] = make_motif(prof['cells'], var, chords, root_pc, kit['mode'], r['motif'][0], r['motif'][1], random.Random(base + 4), kit_i)
        out.setdefault('sequence', {})[var] = make_sequence(prof['drums'], var, chords, r['sequence'][0], r['sequence'][1], random.Random(base + 5), kit_i)
        out.setdefault('pad', {})[var] = make_pad(chords, r['pad'][0], r['pad'][1], random.Random(base + 6), kit_i, var, prof.get('pad_center', 60))
    end = 8 * BAR
    for role in out:
        for var in out[role]:
            out[role][var] = trim(sorted((s, min(d, end - s), p, v) for s, d, p, v in out[role][var] if s < end), role)
    return out, chords


def trim(notes, role):
    """Shorten a note so it ends before the next onset: any note for mono parts, the same pitch for the rest."""
    notes = [list(n) for n in notes]
    if role == 'drums':
        return [tuple(n) for n in notes]
    if POLY[role] == 1:
        for a, b in zip(notes, notes[1:]):
            if a[0] + a[1] > b[0]:
                a[1] = max(1, b[0] - a[0])
    else:
        by = {}
        for n in notes:
            by.setdefault(n[2], []).append(n)
        for lst in by.values():
            for a, b in zip(lst, lst[1:]):
                if a[0] + a[1] > b[0]:
                    a[1] = max(1, b[0] - a[0])
    return [tuple(n) for n in notes]


# arrangement: section -> bar offset; (role, var) placements
SECTIONS = [
    ('theme', 0, [('drums', 'a'), ('bass', 'a'), ('keys', 'a'), ('pad', 'a'), ('motif', 'a')]),
    ('sequence', 8, [('drums', 'a'), ('bass', 'a'), ('keys', 'a'), ('pad', 'a'), ('sequence', 'a')]),
    ('open', 16, [('keys', 'b'), ('sequence', 'b'), ('pad', 'b')]),
    ('return', 24, [('drums', 'b'), ('bass', 'b'), ('keys', 'a'), ('pad', 'a'), ('motif', 'a')]),
]


def placements():
    pl = {}
    for _name, off, items in SECTIONS:
        for role, var in items:
            pl.setdefault((role, var), []).append(off)
    return pl


def arrange(parts):
    """parts: {role: {var: notes}} -> list of (role, notes) with absolute ticks, ordered by ROLES."""
    pl = placements()
    tracks = []
    for role in ROLES:
        notes = []
        for (r, var), offs in pl.items():
            if r != role:
                continue
            for off in offs:
                notes += [(t + off * BAR, d, p, v) for t, d, p, v in parts[role][var]]
        tracks.append((role, sorted(notes)))
    return tracks
