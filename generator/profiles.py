"""Genre profiles for the ten pack repositories."""

STD = dict(bass=(41, 62), keys=(48, 76), motif=(60, 86), sequence=(52, 81), pad=(48, 81))


def rng_(**kw):
    r = dict(STD)
    r.update(kw)
    return r


P = {}

P['balearic-trance'] = dict(
    title='Balearic Trance', drums='trance', cells='slow', ranges=rng_(),
    art='sea', palette=('#14213d', '#fca311', '#e5e5e5', '#f4a261', '#ffffff'),
    timbre=dict(bass='saw', keys='soft', motif='sine', seq='tri', pad='pad', kick='909', verb=0.30),
    about='Sunset-terrace trance: warm major and Lydian harmony, a singing motif, and a bright sixteenth sequence over a four-on-the-floor kit.',
    use='Drop the arrangement into a session for a fast sketch, or pull single parts, for example the motif or the pad, into your own tracks.',
    tags=['midi', 'balearic-trance', 'trance', 'music-production', 'composition'],
    kits=[
        dict(id='k01', name='Salt Terrace', bpm=128, root='D', mode='mixolydian', prog=[('D', 'dom7', 2), ('C', 'maj7', 2), ('G', 'maj7', 2), ('A', 'min7', 2)]),
        dict(id='k02', name='White Cove', bpm=126, root='A', mode='ionian', prog=[('A', 'maj7', 2), ('D', 'maj', 2), ('E', 'maj', 2), ('F#', 'min', 2)]),
        dict(id='k03', name='Glass Room', bpm=132, root='G', mode='lydian', prog=[('G', 'maj7', 4), ('D', 'maj7', 4)]),
        dict(id='k04', name='Ferry Light', bpm=136, root='F', mode='ionian', prog=[('Bb', 'maj7', 2), ('F', 'maj', 2), ('D', 'min7', 2), ('C', 'maj', 2)]),
    ])

P['psychedelic-fx'] = dict(
    title='Psychedelic FX', drums='fx', cells='slow', ranges=rng_(bass=(33, 55)),
    art='spiral', palette=('#10002b', '#ff6d00', '#9d4edd', '#00f5d4', '#ffffff'),
    timbre=dict(bass='sub', keys='soft', motif='bell', seq='saw', pad='pad', kick='909', verb=0.42),
    about='Note-only psychedelic textures: broken percussion, pedal-tone basses, eerie motifs and cluster pads at psy-trance tempos.',
    use='Layer the sequence and pad under a rolling bass for atmosphere, or use the sparse drum parts as a percussion bed.',
    tags=['midi', 'psychedelic', 'psytrance', 'sound-design', 'music-production'],
    kits=[
        dict(id='k01', name='Tape Bloom', bpm=146, root='E', mode='phrygian', prog=[('E', 'min7', 2), ('F', 'maj7', 2), ('E', 'min7', 2), ('G', 'maj', 2)]),
        dict(id='k02', name='Spiral Gate', bpm=150, root='A', mode='aeolian', prog=[('A', 'min', 4), ('G', 'maj', 2), ('F', 'maj', 2)]),
        dict(id='k03', name='Dust Orbit', bpm=144, root='D', mode='dorian', prog=[('D', 'min7', 2), ('G', 'dom7', 2), ('D', 'min7', 2), ('C', 'maj7', 2)]),
        dict(id='k04', name='Mirror Rain', bpm=148, root='C', mode='harmonic minor', prog=[('C', 'min', 2), ('Ab', 'maj', 2), ('G', 'dom7', 2), ('C', 'min', 2)]),
    ])

P['psychill'] = dict(
    title='Psychill', drums='chill', cells='slow', ranges=rng_(bass=(36, 55)),
    art='moss', palette=('#0b2b26', '#8ab17d', '#e9c46a', '#2a9d8f', '#f1faee'),
    timbre=dict(bass='sub', keys='epiano', motif='bell', seq='tri', pad='pad', kick='808', verb=0.45),
    about='Slow psychedelic downtempo: half-time drums, ninth chords, soft bell motifs and long pads in the 90 to 105 BPM range.',
    use='Use the half-time drums and pad as a bed, then add the motif for a melodic top line.',
    tags=['midi', 'psychill', 'downtempo', 'chillout', 'music-production'],
    kits=[
        dict(id='k01', name='Moss Lantern', bpm=98, root='A', mode='dorian', prog=[('A', 'min9', 2), ('D', 'dom9', 2), ('A', 'min9', 2), ('E', 'min7', 2)]),
        dict(id='k02', name='Slow Spores', bpm=92, root='E', mode='aeolian', prog=[('E', 'min7', 2), ('C', 'maj7', 2), ('A', 'min7', 2), ('B', 'dom7', 2)]),
        dict(id='k03', name='Amber Drift', bpm=104, root='D', mode='dorian', prog=[('D', 'min9', 4), ('G', 'dom13', 2), ('D', 'min9', 2)]),
        dict(id='k04', name='Night Garden', bpm=96, root='G', mode='mixolydian', prog=[('G', 'dom9', 2), ('F', 'maj7', 2), ('C', 'maj9', 2), ('G', 'dom9', 2)]),
    ])

P['neo-soul-pocket'] = dict(
    title='Neo-Soul Pocket', drums='neosoul', cells='rnb', ranges=rng_(bass=(36, 55), motif=(60, 79)),
    art='vinyl', palette=('#2d1b0e', '#d4a373', '#faedcd', '#bc6c25', '#fefae0'),
    timbre=dict(bass='sub', keys='epiano', motif='soft', seq='tri', pad='pad', kick='808', verb=0.28),
    about='Laid-back neo-soul grooves: late snares, swung hats, extended chords and a pocket bass at 72 to 88 BPM.',
    use='Start from the drums and bass for the pocket, then voice your own chords or use the keys part as a guide.',
    tags=['midi', 'neo-soul', 'rnb', 'groove', 'music-production'],
    kits=[
        dict(id='k01', name='Back Porch', bpm=84, root='F', mode='dorian', prog=[('F', 'min9', 2), ('Bb', 'dom13', 2), ('Eb', 'maj9', 2), ('Ab', 'maj7', 1), ('G', 'm7b5', 1)]),
        dict(id='k02', name='Slow Burn', bpm=78, root='A', mode='aeolian', prog=[('A', 'min9', 2), ('D', 'min11', 2), ('F', 'maj9', 2), ('E', 'dom7s9', 2)]),
        dict(id='k03', name='Honey Room', bpm=88, root='C', mode='ionian', prog=[('C', 'maj9', 2), ('A', 'min9', 2), ('D', 'min9', 2), ('G', 'dom13', 2)]),
        dict(id='k04', name='Late Bloom', bpm=72, root='Bb', mode='ionian', prog=[('Bb', 'dom9', 2), ('Eb', 'maj9', 2), ('G', 'min9', 2), ('C', 'dom9', 2)]),
    ])

P['bossa-nova'] = dict(
    title='Bossa Nova', drums='bossa', cells='bossa', ranges=rng_(bass=(36, 55), motif=(60, 84)),
    art='sun', palette=('#003049', '#f77f00', '#fcbf49', '#eae2b7', '#ffffff'),
    timbre=dict(bass='pluck', keys='epiano', motif='soft', seq='pluck', pad='pad', kick='808', verb=0.22),
    about='Bossa nova construction kits: root-fifth bass, side-stick clave, syncopated comping and ii-V-I harmony.',
    use='Use the bass and side-stick drums as the rhythm bed, then comp with the keys part or your own voicings.',
    tags=['midi', 'bossa-nova', 'jazz', 'latin', 'music-production'],
    kits=[
        dict(id='k01', name='Harbor Sun', bpm=128, root='C', mode='ionian', prog=[('D', 'min7', 1), ('G', 'dom7', 1), ('C', 'maj7', 2), ('A', 'min7', 1), ('D', 'dom7', 1), ('D', 'min7', 1), ('G', 'dom7', 1)]),
        dict(id='k02', name='Blue Shutters', bpm=120, root='F', mode='ionian', prog=[('F', 'maj7', 2), ('E', 'm7b5', 1), ('A', 'dom7b9', 1), ('D', 'min7', 2), ('G', 'dom7', 1), ('C', 'dom7', 1)]),
        dict(id='k03', name='Morning Tram', bpm=132, root='A', mode='aeolian', prog=[('A', 'min7', 2), ('D', 'min7', 2), ('E', 'dom7b9', 2), ('A', 'min6', 2)]),
        dict(id='k04', name='Salt Window', bpm=124, root='Bb', mode='ionian', prog=[('Bb', 'maj7', 2), ('G', 'min7', 2), ('C', 'min7', 2), ('F', 'dom7', 2)]),
    ])

P['90s-rnb'] = dict(
    title='90s R&B', drums='rnb90', cells='rnb', ranges=rng_(bass=(36, 52), motif=(60, 79), pad=(48, 72)),
    art='neon', palette=('#240046', '#ff006e', '#3a86ff', '#8338ec', '#ffffff'),
    timbre=dict(bass='sub', keys='epiano', motif='soft', seq='tri', pad='pad', kick='808', verb=0.34),
    about='Slow-jam R&B kits: swung sixteenth hats, doubled backbeats, ninth chords and a vocal-range motif at 76 to 96 BPM.',
    use='Build from the drums and bass, then lay the motif where a vocal line would sit.',
    tags=['midi', 'rnb', '90s', 'slow-jam', 'music-production'],
    kits=[
        dict(id='k01', name='Slow Dial', bpm=90, root='Ab', mode='ionian', prog=[('Ab', 'maj9', 2), ('F', 'min9', 2), ('Db', 'maj7', 2), ('Eb', 'dom7', 2)]),
        dict(id='k02', name='Late Line', bpm=82, root='F', mode='aeolian', prog=[('F', 'min9', 2), ('Db', 'maj9', 2), ('Ab', 'maj7', 2), ('C', 'dom7s9', 2)]),
        dict(id='k03', name='Quiet Storm', bpm=76, root='C', mode='dorian', prog=[('C', 'min9', 2), ('F', 'dom9', 2), ('Bb', 'maj7', 2), ('G', 'm7b5', 1), ('C', 'dom7', 1)]),
        dict(id='k04', name='Sunday Tape', bpm=96, root='D', mode='ionian', prog=[('D', 'maj9', 2), ('B', 'min9', 2), ('E', 'min9', 2), ('A', 'dom13', 2)]),
    ])

P['new-jack-swing'] = dict(
    title='New Jack Swing', drums='njs', cells='sync', ranges=rng_(bass=(36, 55)),
    art='memphis', palette=('#1a1a2e', '#ff2e63', '#08d9d6', '#f9ed69', '#ffffff'),
    timbre=dict(bass='saw', keys='epiano', motif='saw', seq='pluck', pad='pad', kick='909', verb=0.26),
    about='Swingbeat kits: heavy swung sixteenths, hard backbeats, syncopated bass and sharp-ninth chords at 100 to 112 BPM.',
    use='Use the drums and bass as a swing foundation, then stack the keys stabs and motif for the hook.',
    tags=['midi', 'new-jack-swing', 'swingbeat', 'rnb', 'music-production'],
    kits=[
        dict(id='k01', name='Block Party', bpm=108, root='G', mode='aeolian', prog=[('G', 'min9', 2), ('Eb', 'maj7', 2), ('C', 'min7', 2), ('D', 'dom7s9', 2)]),
        dict(id='k02', name='Chrome Crew', bpm=104, root='B', mode='dorian', prog=[('B', 'min9', 2), ('E', 'dom9', 2), ('A', 'maj9', 2), ('F#', 'min7', 2)]),
        dict(id='k03', name='Neon Stoop', bpm=112, root='F', mode='ionian', prog=[('F', 'maj9', 2), ('D', 'min9', 2), ('Bb', 'maj7', 2), ('C', 'dom13', 2)]),
        dict(id='k04', name='Late Set', bpm=100, root='Eb', mode='dorian', prog=[('Eb', 'min9', 2), ('Ab', 'dom9', 2), ('Db', 'maj7', 2), ('B', 'dom7', 2)]),
    ])

P['eurodance'] = dict(
    title='Eurodance', drums='euro', cells='steady', ranges=rng_(bass=(40, 60)),
    art='starburst', palette=('#0d1b2a', '#e0aaff', '#ff9e00', '#00b4d8', '#ffffff'),
    timbre=dict(bass='saw', keys='pluck', motif='saw', seq='saw', pad='pad', kick='909', verb=0.24),
    about='Eurodance hooks: four-on-the-floor drums, octave-jump bass, minor-key piano chords and a steady-eighth lead at 136 to 144 BPM.',
    use='Start from the drums and octave bass, then drop the motif on top as the hook.',
    tags=['midi', 'eurodance', 'dance', '90s', 'music-production'],
    kits=[
        dict(id='k01', name='Neon Crowd', bpm=140, root='A', mode='aeolian', prog=[('A', 'min', 2), ('F', 'maj', 2), ('C', 'maj', 2), ('G', 'maj', 2)]),
        dict(id='k02', name='Star Ticket', bpm=138, root='D', mode='aeolian', prog=[('D', 'min', 2), ('Bb', 'maj', 2), ('F', 'maj', 2), ('C', 'maj', 2)]),
        dict(id='k03', name='Night Bus', bpm=144, root='G', mode='aeolian', prog=[('G', 'min', 2), ('Eb', 'maj', 2), ('Bb', 'maj', 2), ('F', 'maj', 2)]),
        dict(id='k04', name='Laser Bridge', bpm=136, root='C', mode='aeolian', prog=[('C', 'min', 2), ('Ab', 'maj', 2), ('Eb', 'maj', 2), ('Bb', 'maj', 2)]),
    ])

P['piano-house'] = dict(
    title='Piano House', drums='house', cells='sync', ranges=rng_(bass=(38, 57)),
    art='keys', palette=('#0b132b', '#e8a317', '#f2f2f2', '#5bc0be', '#ffffff'),
    timbre=dict(bass='saw', keys='piano', motif='piano', seq='pluck', pad='pad', kick='909', verb=0.26),
    about='Piano house kits: syncopated piano stabs, offbeat bass, four-on-the-floor drums and seventh and ninth chords at 120 to 126 BPM.',
    use='Use the keys part for stabs, the bass and drums for the floor, and the motif as the piano riff.',
    tags=['midi', 'piano-house', 'house', 'dance', 'music-production'],
    kits=[
        dict(id='k01', name='Floor Seven', bpm=124, root='A', mode='aeolian', prog=[('A', 'min7', 2), ('D', 'min7', 2), ('G', 'dom7', 2), ('C', 'maj7', 2)]),
        dict(id='k02', name='Brass Lamp', bpm=122, root='F', mode='dorian', prog=[('F', 'min9', 2), ('Bb', 'dom9', 2), ('Eb', 'maj7', 2), ('C', 'dom7', 2)]),
        dict(id='k03', name='Late Lift', bpm=126, root='C', mode='ionian', prog=[('C', 'maj7', 2), ('E', 'min7', 2), ('F', 'maj7', 2), ('G', 'dom7', 2)]),
        dict(id='k04', name='Riverside', bpm=120, root='E', mode='aeolian', prog=[('E', 'min9', 2), ('A', 'min9', 2), ('D', 'dom9', 2), ('G', 'maj7', 2)]),
    ])

P['uplifting-trance'] = dict(
    title='Uplifting Trance', drums='uplift', cells='steady', ranges=rng_(),
    art='dawn', palette=('#03045e', '#ffb703', '#90e0ef', '#fb8500', '#ffffff'),
    timbre=dict(bass='saw', keys='pluck', motif='saw', seq='saw', pad='pad', kick='909', verb=0.34),
    about='Uplifting trance kits: rolling offbeat bass, anthem chords in minor keys, a steady-eighth lead and sixteenth arps at 136 to 140 BPM.',
    use='Use the arrangement as a build-and-return sketch, or take the sequence and motif as lead lines.',
    tags=['midi', 'uplifting-trance', 'trance', 'edm', 'music-production'],
    kits=[
        dict(id='k01', name='First Light', bpm=138, root='E', mode='aeolian', prog=[('E', 'min', 2), ('C', 'maj', 2), ('G', 'maj', 2), ('D', 'maj', 2)]),
        dict(id='k02', name='Open Sky', bpm=140, root='F#', mode='aeolian', prog=[('F#', 'min', 2), ('D', 'maj', 2), ('A', 'maj', 2), ('E', 'maj', 2)]),
        dict(id='k03', name='Long Way Up', bpm=136, root='B', mode='aeolian', prog=[('B', 'min', 2), ('G', 'maj', 2), ('D', 'maj', 2), ('A', 'maj', 2)]),
        dict(id='k04', name='Last Ridge', bpm=140, root='G#', mode='aeolian', prog=[('G#', 'min', 2), ('E', 'maj', 2), ('B', 'maj', 2), ('F#', 'maj', 2)]),
    ])

for slug, p in P.items():
    p['slug'] = slug
    for k in p['kits']:
        k['slug'] = k['id'] + '-' + k['name'].lower().replace(' ', '-')
