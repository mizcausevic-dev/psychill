"""Re-opens the written MIDI bytes and checks them. A second parser (mido) cross-checks note counts."""
import hashlib
import json
import os
import tempfile

import midi
from compose import CHANNEL, DRUM_MAP, POLY, ROLES, SECTIONS, BAR, arrange

VERSION = 'claude-validate-1.0.0'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def check_part(data, role, bpm, ranges, bars=8):
    errs = []
    try:
        m = midi.read_midi(data)
    except Exception as e:  # noqa
        return ['parse: %s' % e], None
    if m['format'] != 0 or len(m['tracks']) != 1:
        errs.append('not format 0 single track')
    if m['ppq'] != midi.PPQ:
        errs.append('ppq %s' % m['ppq'])
    tr = m['tracks'][0]
    tempos = [e[3] for e in tr['events'] if e[1] == 'meta' and e[2] == 0x51]
    if len(tempos) != 1 or int.from_bytes(tempos[0], 'big') != round(60_000_000 / bpm):
        errs.append('tempo')
    ts = [e[3] for e in tr['events'] if e[1] == 'meta' and e[2] == 0x58]
    if len(ts) != 1 or ts[0][:2] != bytes([4, 2]):
        errs.append('time signature')
    if tr['end_tick'] != bars * BAR:
        errs.append('end of track %s' % tr['end_tick'])
    if any(e[1] == 'other' for e in tr['events']):
        errs.append('program change or other channel message')
    notes, problems = midi.notes_of(tr)
    errs += problems
    if not notes:
        errs.append('no notes')
    lo, hi = ranges
    ch = CHANNEL[role]
    for s, d, p, v, c in notes:
        if c != ch:
            errs.append('channel %d' % c)
            break
        if d <= 0 or s + d > bars * BAR:
            errs.append('note outside bar range at %d' % s)
            break
        if not 1 <= v <= 127:
            errs.append('velocity')
            break
        if role == 'drums':
            if p not in DRUM_MAP:
                errs.append('drum pitch %d' % p)
                break
        elif not lo <= p <= hi:
            errs.append('pitch %d outside %d-%d' % (p, lo, hi))
            break
    if role != 'drums':
        # polyphony by sweeping start/end
        ev = sorted([(s, 1) for s, d, *_ in notes] + [(s + d, -1) for s, d, *_ in notes], key=lambda e: (e[0], e[1]))
        cur = mx = 0
        for _t, k in ev:
            cur += k
            mx = max(mx, cur)
        if mx > POLY[role]:
            errs.append('polyphony %d > %d' % (mx, POLY[role]))
    # off before on at a shared tick
    last_tick, seen_on = None, False
    for e in tr['events']:
        if e[1] in ('on', 'off'):
            if e[0] != last_tick:
                last_tick, seen_on = e[0], False
            if e[1] == 'on':
                seen_on = True
            elif seen_on:
                errs.append('note-off after note-on at tick %d' % e[0])
                break
    return errs, dict(notes=len(notes), tuples=sorted((s, d, p) for s, d, p, v, c in notes), polyphony=None)


def mido_count(path):
    import mido
    f = mido.MidiFile(path)
    n = sum(1 for t in f.tracks for m in t if m.type == 'note_on' and m.velocity > 0)
    return n, f.type, f.ticks_per_beat


def validate_pack(root, prof, kit_parts, kit_arr):
    """kit_parts[kit_id][role][var] = notes written; kit_arr[kit_id] = [(role, notes)]."""
    rep = dict(validator=VERSION, files=[], errors=[], checks=[])
    ranges = dict(prof['ranges'])
    ranges['drums'] = (0, 127)
    motifA = {}
    for kit in prof['kits']:
        kid, kslug = kit['id'], kit['slug']
        pdir = os.path.join(root, 'midi', kslug)
        tuples = {}
        for role in ROLES:
            for var in ('a', 'b'):
                rel = 'midi/%s/%s-%s.mid' % (kslug, role, var)
                data = open(os.path.join(root, rel), 'rb').read()
                errs, info = check_part(data, role, kit['bpm'], ranges[role])
                n_mido, typ, tpq = mido_count(os.path.join(root, rel))
                if info and n_mido != info['notes']:
                    errs.append('mido note count %d vs %d' % (n_mido, info['notes']))
                if typ != 0 or tpq != midi.PPQ:
                    errs.append('mido type/ppq')
                if info:
                    tuples[(role, var)] = info['tuples']
                rep['files'].append(dict(path=rel, role=role, variation=var, sha256=sha(data), notes=info['notes'] if info else 0, errors=errs))
                rep['errors'] += ['%s: %s' % (rel, e) for e in errs]
        # variation differs in start, pitch, duration
        for role in ROLES:
            a, b = tuples[(role, 'a')], tuples[(role, 'b')]
            for idx, name in ((0, 'start'), (2, 'pitch'), (1, 'duration')):
                if sorted(x[idx] for x in a) == sorted(x[idx] for x in b):
                    rep['errors'].append('%s %s: variations share %s multiset' % (kslug, role, name))
        # arrangement
        rel = 'midi/%s/arrangement.mid' % kslug
        data = open(os.path.join(root, rel), 'rb').read()
        m = midi.read_midi(data)
        errs = []
        if m['format'] != 1 or len(m['tracks']) != 1 + len(ROLES):
            errs.append('arrangement format or track count')
        else:
            for tr in m['tracks']:
                if tr['end_tick'] != 32 * BAR:
                    errs.append('arrangement end tick %s' % tr['end_tick'])
            by_role = {}
            for tr, role in zip(m['tracks'][1:], ROLES):
                notes, problems = midi.notes_of(tr)
                errs += ['%s %s' % (role, p) for p in problems]
                by_role[role] = sorted((s, d, p) for s, d, p, v, c in notes)
            expect = {role: sorted((s, d, p) for s, d, p, v in n) for role, n in kit_arr[kid]}
            for role in ROLES:
                if by_role.get(role) != expect[role]:
                    errs.append('%s differs from placed parts' % role)
            # section rules
            def sect(role, a, b):
                return [x for x in by_role[role] if a * BAR <= x[0] < b * BAR]
            for role in ('drums', 'bass', 'motif'):
                if sect(role, 16, 24):
                    errs.append('open section has %s' % role)
            for name, off, _items in SECTIONS:
                if sect('motif', off, off + 8) and sect('sequence', off, off + 8):
                    errs.append('motif and sequence overlap in %s' % name)
            theme = [(s - 0, d, p) for s, d, p in sect('motif', 0, 8)]
            ret = [(s - 24 * BAR, d, p) for s, d, p in sect('motif', 24, 32)]
            if theme != ret:
                errs.append('return does not restate motif A')
        rep['files'].append(dict(path=rel, role='arrangement', sha256=sha(data), errors=errs))
        rep['errors'] += ['%s: %s' % (rel, e) for e in errs]
        # motif contour
        ta = tuples[('motif', 'a')]
        motifA[kid] = tuple(ta[i + 1][2] - ta[i][2] for i in range(len(ta) - 1))
    if len(set(motifA.values())) != len(motifA):
        rep['errors'].append('motif A contours are not distinct across kits')
    # negative control: an overlapping monophonic part must be rejected
    tmp = tempfile.mkdtemp()
    bad = midi.write_part(os.path.join(tmp, 'bad.mid'), 120, 'bass', 0, [(0, 960, 40, 90), (480, 960, 41, 90)], 8)
    bad_errs, _ = check_part(bad, 'bass', 120, ranges['bass'])
    rep['negative_control'] = dict(fixture='overlapping bass notes, written outside the pack', rejected=any('polyphony' in e for e in bad_errs), errors=bad_errs)
    # positive control
    good = midi.write_part(os.path.join(tmp, 'good.mid'), 120, 'bass', 0, [(0, 900, 45, 90), (960, 900, 46, 90)], 8)
    good_errs, _ = check_part(good, 'bass', 120, ranges['bass'])
    rep['positive_control'] = dict(fixture='two clean bass notes', accepted=not good_errs, errors=good_errs)
    if not rep['negative_control']['rejected']:
        rep['errors'].append('negative control was not rejected')
    if not rep['positive_control']['accepted']:
        rep['errors'].append('positive control was rejected')
    rep['summary'] = dict(files=len(rep['files']), errors=len(rep['errors']))
    return rep
