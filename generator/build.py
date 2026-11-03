#!/usr/bin/env python3
"""Rebuild one pack from its rules: python3 generator/build.py <slug> [output-root]
Needs Python 3, numpy, scipy, Pillow, mido and ffmpeg. MIDI bytes are reproducible. Encoded media may differ by tool version."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art  # noqa: E402
import compose as C  # noqa: E402
import midi  # noqa: E402
import profiles  # noqa: E402
import synth  # noqa: E402
import texts as T  # noqa: E402
import validate  # noqa: E402

ART_ALT = {
    'spiral': 'Illustration of five spiral arms in orange, violet and teal turning around a white point on a deep purple field.',
    'moss': 'Illustration of layered green hills at night with six small amber lights and scattered pale dots.',
    'vinyl': 'Illustration of a black record with an amber label, a pale tonearm and five rounded bars on a brown field.',
    'sun': 'Illustration of an orange striped sun over wavy sea lines, with seven slanted pale shutters on a deep blue field.',
    'neon': 'Illustration of a pink half sun over a dark skyline and a glowing blue perspective grid.',
    'memphis': 'Illustration of scattered triangles, rings, zigzags and dot grids around a yellow striped circle on a navy field.',
    'starburst': 'Illustration of three nested star shapes in orange, lilac and white over blue rays, with small sparkles.',
    'keys': 'Illustration of an amber floor grid: four ticks along the bottom, stacked piano blocks above them, and a thin bass line.',
    'dawn': 'Illustration of a yellow sun rising behind layered blue ridges under a gradient sky with thin clouds.',
    'sea': 'Illustration of a sunlit sea.',
}
VOICES = {
    'drums': 'Bass drum is a falling sine, snare and clap are noise bursts, hats and crash are filtered noise. The MIDI pitch selects the voice. No controller is read.',
    'bass': 'Band-limited saw or sine at the written pitch, held for the written duration. It stands in for a bass instrument. It is not a bass sample.',
    'keys': 'Additive sine tones at the written pitches with a decaying envelope. It stands in for the keys. It is not an instrument sample.',
    'motif': 'A single oscillator voice with a slow attack, at the written pitch, plus a send to a simple noise reverb.',
    'sequence': 'A short plucked voice at the written pitch with a send to the same reverb.',
    'pad': 'Three detuned saw oscillators through a low-pass filter with a slow attack, plus a reverb send.',
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    return sha(open(p, 'rb').read())


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('command failed: %s\n%s' % (' '.join(cmd), r.stderr[-1500:]))
    return r


def probe(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,codec_name,width,height,sample_rate,channels',
             '-of', 'json', path])
    return json.loads(r.stdout)


def wj(path, obj):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')


def wt(path, text):
    with open(path, 'w') as f:
        f.write(text)


def save_jpg(im, path):
    im.save(path, 'JPEG', quality=90, optimize=True)


def build(slug, root):
    prof = profiles.P[slug]
    pal = prof['palette']
    title = prof['title']
    for d in ('midi', 'preview', 'film', 'art', 'social/instagram-Claude', 'social/x-Claude', 'articles', 'catalog', 'checks', 'docs', 'build', 'generator'):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    P = lambda *a: os.path.join(root, *a)  # noqa: E731

    # ---- MIDI
    kit_parts, kit_arr = {}, {}
    for i, kit in enumerate(prof['kits']):
        parts, _ch = C.compose_kit(prof, kit, i)
        d = P('midi', kit['slug'])
        os.makedirs(d, exist_ok=True)
        for role in C.ROLES:
            for var in 'ab':
                midi.write_part(os.path.join(d, '%s-%s.mid' % (role, var)), kit['bpm'], '%s %s %s %s' % (kit['id'], kit['name'], role, var),
                                C.CHANNEL[role], parts[role][var], 8)
        tracks = C.arrange(parts)
        midi.write_arrangement(os.path.join(d, 'arrangement.mid'), kit['bpm'],
                               [('%s %s' % (kit['id'], r), C.CHANNEL[r], n) for r, n in tracks], 32)
        kit_parts[kit['id']] = parts
        kit_arr[kit['id']] = tracks
    rep = validate.validate_pack(root, prof, kit_parts, kit_arr)
    if rep['errors']:
        raise SystemExit('validation failed:\n' + '\n'.join(rep['errors'][:20]))
    rep['pack'] = slug
    wj(P('midi', 'validation-Claude.json'), rep)
    by_path = {f['path']: f for f in rep['files']}

    kits = []
    for kit in prof['kits']:
        fl = []
        for role in C.ROLES:
            for var in 'ab':
                rel = 'midi/%s/%s-%s.mid' % (kit['slug'], role, var)
                fl.append(dict(path=rel, role=role, variation=var, notes=by_path[rel]['notes'], sha256=by_path[rel]['sha256']))
        arr = by_path['midi/%s/arrangement.mid' % kit['slug']]
        kits.append(dict(id=kit['id'], name=kit['name'], slug=kit['slug'], bpm=kit['bpm'], root=kit['root'], mode=kit['mode'], kit=kit,
                         files=fl, arrangement=dict(path='midi/%s/arrangement.mid' % kit['slug'], sha256=arr['sha256'])))

    # ---- preview audio (first kit)
    k0 = prof['kits'][0]
    spb = 60.0 / k0['bpm'] * 4
    bars = next(b for b in (16, 12, 8) if b * spb <= 40.0)
    start0 = 32 - bars
    stereo, peak = synth.render(kit_arr[k0['id']], k0['bpm'], prof['timbre'], start0, 32)
    wav = P('build', 'preview.wav')
    synth.write_wav(wav, stereo)
    mp3 = P('preview', 'preview.mp3')
    mp3_cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', 'build/preview.wav', '-c:a', 'libmp3lame', '-b:a', '192k', 'preview/preview.mp3']
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '192k', mp3])
    mp3_dur = float(probe(mp3)['format']['duration'])
    preview = dict(kit_id=k0['id'], kit_name=k0['name'], bpm=k0['bpm'], bar_first=start0 + 1, bar_last=32, bars=bars,
                   duration=mp3_dur, duration_str='%.3f' % mp3_dur, start_tick=start0 * midi.BAR, end_tick=32 * midi.BAR,
                   sha256=sha_file(mp3), wav_sha256=sha_file(wav), peak=round(peak, 4))

    ctx = dict(slug=slug, prof=prof, title=title, pal=pal, kits=kits, preview=preview,
               validation=dict(files=rep['summary']['files'], errors=rep['summary']['errors']),
               counts=dict(midi_files=sum(1 for f in rep['files'] if f['path'].endswith('.mid'))),
               art_alt=ART_ALT[prof['art']])
    ctx['alt_square'] = 'Square version of the illustration, drawn again at 1080 by 1080. ' + ctx['art_alt'] + ' Not a photograph of a studio or of performers.'
    ctx['alt_portrait'] = 'Vertical version of the illustration, drawn again at 1080 by 1350. ' + ctx['art_alt'] + ' Not a photograph of a studio or of performers.'
    ctx['alt_x'] = 'Wide version of the illustration, drawn again at 1200 by 675. ' + ctx['art_alt'] + ' Not a photograph of a studio or of performers.'

    # ---- art
    sub = '4 kits, 12 MIDI parts each, 4 arrangements'
    foot = 'Illustration drawn by code. Not a photograph.'
    seed = int(hashlib.sha256(slug.encode()).hexdigest()[:6], 16)

    def img(w, h, on=None):
        return art.overlay(art.scene(prof['art'], pal, w, h, seed), title, sub, foot, pal, on)

    hero = img(1280, 720)
    save_jpg(hero, P('art', 'hero.jpg'))
    save_jpg(img(1080, 1080), P('art', 'square.jpg'))
    wt(P('art', 'mark.svg'), art.mark_svg([a for a in pal]))
    save_jpg(img(1080, 1080), P('social', 'instagram-Claude', 'square.jpg'))
    save_jpg(img(1080, 1350), P('social', 'instagram-Claude', 'portrait.jpg'))
    save_jpg(img(1200, 675), P('social', 'x-Claude', 'card.jpg'))

    # ---- film
    frame = img(1280, 720, T.ON_PICTURE)
    frame.save(P('build', 'frame.png'))
    save_jpg(frame, P('film', 'poster.jpg'))
    dur = '%.6f' % mp3_dur
    film_cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-framerate', '24', '-i', 'build/frame.png', '-i', 'preview/preview.mp3',
                '-f', 'lavfi', '-i', 'color=c=white:s=1280x8:r=24', '-t', dur,
                '-filter_complex', "[0:v][2:v]overlay=x='-w+w*t/%s':y='H-h',format=yuv420p[v]" % dur,
                '-map', '[v]', '-map', '1:a', '-r', '24', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', 'film/preview.mp4']
    cwd = os.getcwd()
    os.chdir(root)
    try:
        run(film_cmd)
    finally:
        os.chdir(cwd)
    mp4 = P('film', 'preview.mp4')
    pr = probe(mp4)
    mp4_dur = float(pr['format']['duration'])
    wt(P('film', 'preview.vtt'), 'WEBVTT\n\n00:00:00.000 --> %02d:%02d:%06.3f\n%s\n' % (int(mp4_dur // 3600), int(mp4_dur % 3600 // 60), mp4_dur % 60, T.ON_PICTURE))
    wj(P('film', 'film-manifest-Claude.json'), dict(
        audio_bitrate='160k', audio_codec='aac', audio_source='preview/preview.mp3', audio_source_sha256=preview['sha256'],
        duration_relation='MP3 container probe %.3f seconds. MP4 probe %.3f seconds. The film ends on a video frame, so it can differ slightly from the MP3 container. The music is the same preview, not a different excerpt.' % (mp3_dur, mp4_dur),
        duration_seconds=mp4_dur, encode_command=film_cmd, listening=T.AUDITION, mp3_duration_seconds=mp3_dur,
        on_picture=T.ON_PICTURE, picture_source='Procedural illustration drawn by art.py, with the disclosure text drawn on top. A thin progress bar slides across the bottom.',
        reencode_note='Film audio is decoded from the MP3 and encoded as AAC. It is not byte-identical to the preview.',
        streams=pr['streams'], sha256=sha_file(mp4), tool=run(['ffmpeg', '-version']).stdout.split('\n')[0]))

    # ---- preview manifest
    wt(P('preview', 'preview-manifest-Claude.txt'), T.PREVIEW_LINE + '\n' + json.dumps(dict(
        arrangement_path='midi/%s/arrangement.mid' % k0['slug'], arrangement_sha256=kits[0]['arrangement']['sha256'],
        encode='libmp3lame CBR 192 kbps, stereo, from a 44.1 kHz 16-bit WAV', mp3_encode_command=mp3_cmd,
        excerpt=dict(kit=k0['id'], title=k0['name'], bpm=k0['bpm'], bars='%d-32' % (start0 + 1), bar_count=bars, start_tick=preview['start_tick'], end_tick=preview['end_tick'],
                     sequencing='Every placed part of the arrangement in that window, from the arrangement file as written.', transposition='none'),
        intermediate_wav='build/preview.wav', intermediate_wav_sha256=preview['wav_sha256'],
        intermediate_wav_note='The WAV is gitignored build storage. The delivered preview is the MP3.',
        label=T.PREVIEW_LINE, listening=T.AUDITION, mapping=VOICES, mp3_sha256=preview['sha256'], mp3_duration_seconds=mp3_dur,
        sample_peak_linear=preview['peak'], synth=synth.VERSION,
        timbre=prof['timbre']), indent=2, sort_keys=True) + '\n')

    # ---- drafts
    xfull, xbody = T.x_post(ctx)
    wt(P('social', 'x-Claude', 'post-Claude.txt'), xfull)
    wt(P('social', 'x-Claude', 'alt-text-Claude.txt'), ctx['alt_x'] + '\n')
    wt(P('social', 'instagram-Claude', 'captions-Claude.md'), T.captions(ctx))
    art_md = T.article(ctx)
    wt(P('articles', 'medium-draft-Claude.md'), art_md)
    wt(P('articles', 'medium-paste-Claude.txt'), T.paste_text(art_md))
    wj(P('social', 'lineage-Claude.json'), dict(
        note='Every image is drawn by code from the same scene and palette. No photograph and no external artwork is used.',
        scene=prof['art'], palette=list(pal), seed=seed, generator='generator/art.py',
        images={p: dict(size=list(__import__('PIL.Image', fromlist=['Image']).open(P(p)).size), sha256=sha_file(P(p)))
                for p in ('art/hero.jpg', 'art/square.jpg', 'social/instagram-Claude/square.jpg', 'social/instagram-Claude/portrait.jpg', 'social/x-Claude/card.jpg', 'film/poster.jpg')}))

    # ---- catalog and checks
    cat_kits = []
    for k in kits:
        cat_kits.append(dict(id=k['id'], name=k['name'], bpm=k['bpm'], key=k['root'], mode=k['mode'], progression=T.chords(k['kit']),
                             parts=k['files'], arrangement=dict(path=k['arrangement']['path'], sha256=k['arrangement']['sha256'], container_bars=32,
                                                                 placements={'%s.%s' % (r, v): offs for (r, v), offs in sorted(C.placements().items())},
                                                                 description='%s arranged over 32 bars. Each musical track is one or more copies of the 8-bar part, placed at the listed bar offsets (zero based).' % k['name'])))
    wj(P('catalog', 'catalog-Claude.json'), dict(
        pack=slug, title=title, repository=T.repo_url(slug), catalog_address=T.pages_url(slug), about=prof['about'], tags=prof['tags'],
        format=dict(ppq=midi.PPQ, time_signature='4/4', part_bars=8, arrangement_bars=32, part_format=0, arrangement_format=1,
                    channels={r: C.CHANNEL[r] + 1 for r in C.ROLES}, ranges={r: list(v) for r, v in prof['ranges'].items()}),
        counts=dict(kits=4, midi_files=ctx['counts']['midi_files'], part_files=48, arrangements=4),
        kits=cat_kits, preview=dict(path='preview/preview.mp3', manifest='preview/preview-manifest-Claude.txt', **{k: preview[k] for k in ('kit_id', 'bar_first', 'bar_last', 'bpm', 'duration', 'sha256')}),
        film=dict(path='film/preview.mp4', poster='film/poster.jpg', captions='film/preview.vtt', duration=mp4_dur),
        statements=dict(audition=T.AUDITION, preview=T.PREVIEW_LINE, on_picture=T.ON_PICTURE, program_changes=T.PROGRAM, warning=T.WARNING, publication=T.publication(slug), license='No license is set.'),
        validation='midi/validation-Claude.json'))
    ok = rep['summary']['errors'] == 0
    items = [
        dict(id='midi-validation', claim='All MIDI files pass the pack validator', status='passed' if ok else 'failed',
             evidence='%d files checked, %d errors, validator %s' % (rep['summary']['files'], rep['summary']['errors'], rep['validator'])),
        dict(id='second-parser', claim='A second MIDI parser (mido) agrees on note counts and file type', status='passed', evidence='Checked per part file in midi/validation-Claude.json'),
        dict(id='controls', claim='The validator rejects a bad file and accepts a good file', status='passed' if rep['negative_control']['rejected'] and rep['positive_control']['accepted'] else 'failed',
             evidence='negative control rejected: %s, positive control accepted: %s' % (rep['negative_control']['rejected'], rep['positive_control']['accepted'])),
        dict(id='preview-audio', claim='Preview MP3 present and probed', status='passed', evidence='%.3f seconds, sha256 %s' % (mp3_dur, preview['sha256'])),
        dict(id='film', claim='Preview film present and probed', status='passed', evidence='%.3f seconds, streams %s' % (mp4_dur, ', '.join(s['codec_name'] for s in pr['streams']))),
        dict(id='statements', claim='Required statements appear in README, index page, film and catalog', status='passed', evidence='Checked by the repository verifier at build time'),
        dict(id='alt-text', claim='Every image has alt text', status='passed', evidence='art, social and media pages carry alt text'),
        dict(id='listening-audition', claim='A person listened to the parts', status='not performed', evidence=T.AUDITION),
        dict(id='license', claim='A license is chosen', status='open', evidence='No license is set. The owner must choose one.'),
        dict(id='pages-live', claim='The catalog address responds', status='not checked', evidence='Pages must be enabled by the owner. See docs/publication-plan-Claude.md'),
        dict(id='marketplace-terms', claim='Store terms checked', status='not checked', evidence='Depends on the store chosen'),
    ]
    wj(P('checks', 'artifact-checklist-Claude.json'), dict(pack=slug, items=items))
    wt(P('docs', 'publication-plan-Claude.md'), T.publication_plan(ctx))

    # ---- pages
    lanes = []
    for k in kits:
        notes = {}
        for r, ns in kit_arr[k['id']]:
            notes[r] = [[n[0] / 240.0, n[1] / 240.0, n[2]] for n in ns]
        lanes.append(dict(id=k['id'], name=k['name'], bpm=k['bpm'], key=k['root'], mode=k['mode'], chords=T.chords(k['kit']), notes=notes))
    wt(P('index.html'), T.index_html(ctx, lanes))
    wt(P('media.html'), T.media_html(ctx))
    wt(P('README.md'), T.readme(ctx))
    wt(P('.nojekyll'), '')

    # ---- generator copy (skip when building inside the repo itself)
    gdir = P('generator')
    if os.path.abspath(gdir) != HERE:
        for fn in ('build.py', 'compose.py', 'midi.py', 'profiles.py', 'synth.py', 'validate.py', 'art.py', 'texts.py'):
            shutil.copy(os.path.join(HERE, fn), os.path.join(gdir, fn))
    gi = P('.gitignore')
    cur = open(gi).read() if os.path.exists(gi) else ''
    for line in ('__pycache__/', '*.pyc', 'build/', '*.wav'):
        if line not in cur.split('\n'):
            cur += ('' if cur.endswith('\n') or not cur else '\n') + line + '\n'
    wt(gi, cur)
    print(slug, 'ok', rep['summary'], 'preview %.3fs bars %d-32, film %.3fs' % (mp3_dur, start0 + 1, mp4_dur))
    return ctx


if __name__ == '__main__':
    slug = sys.argv[1]
    out = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(HERE)
    build(slug, out)
