"""Minimal Standard MIDI File writer and reader (standard library only)."""
import struct

PPQ = 960
BAR = PPQ * 4
STEP = PPQ // 4


def vlq(n):
    if n < 0:
        raise ValueError('negative delta %d' % n)
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def _track(events, end_tick, name):
    """events: list of (tick, order, bytes). Returns an MTrk chunk."""
    body = bytearray()
    nb = name.encode('ascii')
    body += b'\x00\xff\x03' + vlq(len(nb)) + nb
    last = 0
    for tick, _o, data in sorted(events, key=lambda e: (e[0], e[1])):
        body += vlq(tick - last) + data
        last = tick
    body += vlq(end_tick - last) + b'\xff\x2f\x00'
    return b'MTrk' + struct.pack('>I', len(body)) + bytes(body)


def _note_events(notes, channel):
    ev = []
    for start, dur, pitch, vel in notes:
        ev.append((start, 1, bytes([0x80 | channel, pitch, 0])))      # off first at shared ticks
        ev[-1] = (start + dur, 0, bytes([0x80 | channel, pitch, 0]))
        ev.append((start, 1, bytes([0x90 | channel, pitch, vel])))
    return ev


def _meta_events(bpm):
    us = int(round(60_000_000 / bpm))
    return [(0, -2, b'\xff\x51\x03' + us.to_bytes(3, 'big')),
            (0, -1, b'\xff\x58\x04\x04\x02\x18\x08')]


def write_part(path, bpm, name, channel, notes, bars):
    end = bars * BAR
    ev = _meta_events(bpm) + _note_events(notes, channel)
    data = b'MThd' + struct.pack('>IHHH', 6, 0, 1, PPQ) + _track(ev, end, name)
    with open(path, 'wb') as f:
        f.write(data)
    return data


def write_arrangement(path, bpm, tracks, bars):
    """tracks: list of (name, channel, notes with absolute ticks)."""
    end = bars * BAR
    chunks = [_track(_meta_events(bpm), end, 'tempo')]
    for name, channel, notes in tracks:
        chunks.append(_track(_note_events(notes, channel), end, name))
    data = b'MThd' + struct.pack('>IHHH', 6, 1, len(chunks), PPQ) + b''.join(chunks)
    with open(path, 'wb') as f:
        f.write(data)
    return data


def _rd_vlq(b, i):
    n = 0
    while True:
        c = b[i]
        i += 1
        n = (n << 7) | (c & 0x7F)
        if not c & 0x80:
            return n, i


def read_midi(data):
    """Returns dict(format, ppq, tracks=[dict(name, events, end_tick)])."""
    if data[:4] != b'MThd':
        raise ValueError('no MThd')
    fmt, ntr, ppq = struct.unpack('>HHH', data[8:14])
    i = 14
    tracks = []
    for _ in range(ntr):
        if data[i:i + 4] != b'MTrk':
            raise ValueError('no MTrk')
        ln = struct.unpack('>I', data[i + 4:i + 8])[0]
        j, end = i + 8, i + 8 + ln
        tick, status, name, evs, eot = 0, None, '', [], None
        while j < end:
            d, j = _rd_vlq(data, j)
            tick += d
            b = data[j]
            if b == 0xFF:
                typ = data[j + 1]
                l, k = _rd_vlq(data, j + 2)
                payload = data[k:k + l]
                j = k + l
                if typ == 0x03:
                    name = payload.decode('ascii', 'replace')
                elif typ == 0x2F:
                    eot = tick
                evs.append((tick, 'meta', typ, payload))
            else:
                if b & 0x80:
                    status = b
                    j += 1
                kind = status & 0xF0
                ch = status & 0x0F
                if kind in (0xC0, 0xD0):
                    evs.append((tick, 'other', kind, ch, data[j]))
                    j += 1
                else:
                    p1, p2 = data[j], data[j + 1]
                    j += 2
                    if kind == 0x90 and p2 > 0:
                        evs.append((tick, 'on', ch, p1, p2))
                    elif kind == 0x80 or kind == 0x90:
                        evs.append((tick, 'off', ch, p1, p2))
                    else:
                        evs.append((tick, 'other', kind, ch, p1))
        tracks.append(dict(name=name, events=evs, end_tick=eot))
        i = end
    return dict(format=fmt, ppq=ppq, tracks=tracks)


def notes_of(track):
    """Pair note on/off. Returns (notes[(start, dur, pitch, vel, ch)], problems)."""
    open_, notes, problems = {}, [], []
    for ev in track['events']:
        if ev[1] == 'on':
            _t, _k, ch, p, v = ev
            if (ch, p) in open_:
                problems.append('overlap same pitch %d at %d' % (p, ev[0]))
            open_[(ch, p)] = (ev[0], v)
        elif ev[1] == 'off':
            _t, _k, ch, p, _v = ev
            if (ch, p) not in open_:
                problems.append('off without on %d at %d' % (p, ev[0]))
            else:
                s, v = open_.pop((ch, p))
                notes.append((s, ev[0] - s, p, v, ch))
    if open_:
        problems.append('unclosed notes %d' % len(open_))
    return notes, problems
