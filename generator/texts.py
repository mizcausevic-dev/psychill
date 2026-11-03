"""Text, catalog and page generators. Every number written here is passed in from the build, none is typed by hand."""
import html
import json

AUDITION = 'No human listening audition was performed for this build.'
PREVIEW_LINE = 'preview, not a master'
ON_PICTURE = 'preview, not master'
PROGRAM = ('No program changes are encoded. A conventional GM player will normally use its default piano program '
           'for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. '
           'Player behavior may vary.')
WARNING = 'Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.'
NO_PHOTO = 'Illustration drawn by code. Not a photograph of a studio or of performers.'
OWNER = 'mizcausevic-dev'

QDISP = {'maj': '', 'min': 'm', 'dom7': '7', 'maj7': 'maj7', 'min7': 'm7', 'min9': 'm9', 'maj9': 'maj9', 'dom9': '9',
         'dom13': '13', 'min11': 'm11', 'm7b5': 'm7b5', 'sus2': 'sus2', 'sus4': 'sus4', 'dom7s9': '7#9', 'maj6': '6',
         'min6': 'm6', 'add9': 'add9', 'dom7b9': '7b9', 'dim7': 'dim7'}
ROLE_TEXT = {
    'drums': 'drum pattern on channel 10 (GM drum map)',
    'bass': 'monophonic bass line',
    'keys': 'chord voicings, up to four notes at once',
    'motif': 'monophonic hook, the part the arrangement restates at the end',
    'sequence': 'monophonic running pattern, used in place of the motif',
    'pad': 'sustained chord layer, up to four notes at once',
}
ROLES = ['drums', 'bass', 'keys', 'motif', 'sequence', 'pad']
SECTION_TEXT = [
    ('theme', 1, 8, 'drums A, bass A, keys A, pad A, motif A'),
    ('sequence', 9, 16, 'drums A, bass A, keys A, pad A, sequence A'),
    ('open', 17, 24, 'keys B, pad B, sequence B. No drums, bass or motif.'),
    ('return', 25, 32, 'drums B, bass B, keys A, pad A, motif A'),
]


def chords(kit):
    return ' | '.join('%s%s' % (r, QDISP.get(q, q)) + ('' if b == 1 else ' (%d bars)' % b) for r, q, b in kit['prog'])


def repo_url(slug):
    return 'https://github.com/%s/%s' % (OWNER, slug)


def pages_url(slug):
    return 'https://%s.github.io/%s/' % (OWNER, slug)


def publication(slug):
    return ('The GitHub repository is %s and it is public. The catalog address is %s . '
            'Treat that address as live only after it responds.' % (repo_url(slug), pages_url(slug)))


def kit_line(k):
    return '%s %d' % (k['name'], k['bpm'])


def kit_list(ctx):
    return ', '.join(kit_line(k) for k in ctx['kits'])


def hero_alt(ctx):
    return ctx['art_alt'] + ' ' + 'Not a photograph of a studio or of performers.'


def preview_sentence(ctx):
    p = ctx['preview']
    return ('Preview is %s bars %d-%d at %d BPM, %s seconds, not the 32-bar MIDI.'
            % (p['kit_name'], p['bar_first'], p['bar_last'], p['bpm'], p['duration_str']))


def x_post(ctx):
    pv = preview_sentence(ctx)
    short = pv.replace(', not the 32-bar MIDI', '')
    variants = []
    for names, pvx in ((kit_list(ctx), pv), (kit_list(ctx), short), (', '.join(k['name'] for k in ctx['kits']), short)):
        variants.append('%s kits: %s. %s %s The film shows preview, not master. %s'
                        % (ctx['title'], names, pvx, PREVIEW_LINE + '.', AUDITION))
    body = next((v for v in variants if len(v) <= 280), None)
    assert body, [len(v) for v in variants]
    return ('DRAFT\nThis label is not the post body.\n\nPOST BODY\n' + body + '\n'), body


def captions(ctx):
    body = ('%s. Four kits: %s. Drums, bass, keys, motif, sequence and pad, two variations each, one 32-bar arrangement per kit. '
            '%s %s. The film shows preview, not master. %s'
            % (ctx['title'], kit_list(ctx), preview_sentence(ctx), PREVIEW_LINE, AUDITION))
    tags = ' '.join('#' + t.replace('-', '') for t in ctx['prof']['tags'])
    return ('DRAFT\nThis file is a draft. It has not been posted.\n\nCaption\n\n%s\n\nHashtags\n\n%s\n\n'
            'Alt text, 1080x1080\n\n%s\n\nAlt text, 1080x1350\n\n%s\n'
            % (body, tags, ctx['alt_square'], ctx['alt_portrait']))


def article(ctx):
    p, t = ctx['prof'], ctx['title']
    kits = ctx['kits']
    out = []
    out.append('# %s: four MIDI kits, built from rules and checked by script\n' % t)
    out.append('DRAFT. This article has not been published.\n')
    out.append('%s The pack holds four kits. Each kit has six roles with two variations each as 8-bar MIDI parts, '
               'plus one 32-bar arrangement that places those parts. That is %d MIDI files you can open in any DAW.\n'
               % (p['about'], ctx['counts']['midi_files']))
    out.append('## What is inside\n')
    for k in kits:
        out.append('- **%s**: %d BPM, %s %s. Chords: %s.' % (k['name'], k['bpm'], k['root'], k['mode'], chords(k['kit'])))
    out.append('')
    out.append('Roles in every kit: drums, bass, keys, motif, sequence and pad. The motif and the sequence never play together in the arrangement. '
               'The last eight bars restate the motif from the first eight, so each arrangement has a beginning, a middle and a return.\n')
    out.append('## How it was made\n')
    out.append('A script writes the notes from fixed rules and a seeded random generator, so the same inputs give the same MIDI bytes. '
               'Then a separate validator reads every file back and checks the format, the tempo, the note ranges, the polyphony limits, '
               'the drum map, and that the two variations of a part differ. A second MIDI parser counts the notes again as a cross-check. '
               'The validator also rejects a deliberately broken file and accepts a clean one, so you know it can fail. '
               'Result for this build: %d files checked, %d errors.\n' % (ctx['validation']['files'], ctx['validation']['errors']))
    out.append('## How to use it\n')
    out.append('%s\n' % p['use'])
    out.append('%s %s\n' % (WARNING, PROGRAM))
    out.append('## What the preview is\n')
    out.append('%s It is a simple synthesized render of the MIDI, made so you can hear the structure. It is %s. '
               '%s\n' % (preview_sentence(ctx), PREVIEW_LINE, AUDITION))
    out.append('## Limits\n')
    out.append('The files are notes only. They contain no samples, no sound design and no mix. '
               'The artwork is an illustration drawn by code. No license is set in the repository yet.\n')
    out.append('Repository: %s\n' % repo_url(ctx['slug']))
    return '\n'.join(out)


def paste_text(md):
    lines = []
    for ln in md.split('\n'):
        ln = ln.replace('**', '')
        if ln.startswith('#'):
            ln = ln.lstrip('# ').upper()
        lines.append(ln)
    return '\n'.join(lines)


def readme(ctx):
    p, t, slug = ctx['prof'], ctx['title'], ctx['slug']
    L = []
    L.append('# %s\n' % t)
    L.append('**%s** %d MIDI files (4 kits x 6 roles x 2 variations, plus 4 arrangements), notes only, no samples.\n' % (p['about'], ctx['counts']['midi_files']))
    L.append('## Status\n')
    L.append('- Built and checked by script. Validator result: %d files, %d errors. See `midi/validation-Claude.json`.' % (ctx['validation']['files'], ctx['validation']['errors']))
    L.append('- %s' % AUDITION)
    L.append('- The audio preview and the film are %s. They are a simple synthesized render, not a recording and not a mix.' % PREVIEW_LINE)
    L.append('- %s' % publication(slug))
    L.append('- No license is set in this repository. Add one before you sell or redistribute the files.\n')
    L.append('## Kits\n')
    L.append('| Kit | BPM | Key | Mode | Chords |')
    L.append('|---|---|---|---|---|')
    for k in ctx['kits']:
        L.append('| %s %s | %d | %s | %s | %s |' % (k['id'], k['name'], k['bpm'], k['root'], k['mode'], chords(k['kit'])))
    L.append('')
    L.append('## Roles\n')
    L.append('Each kit folder `midi/<kit>/` holds `<role>-a.mid` and `<role>-b.mid` (8 bars, 4/4, 960 ticks per quarter note, format 0) and `arrangement.mid` (32 bars, format 1, one tempo track plus six role tracks).\n')
    L.append('| Role | Channel | What it is | Written range (MIDI note) |')
    L.append('|---|---|---|---|')
    ch = {'drums': 10, 'bass': 1, 'keys': 2, 'motif': 3, 'sequence': 4, 'pad': 5}
    for r in ROLES:
        rg = 'GM drum map' if r == 'drums' else '%d to %d' % tuple(p['ranges'][r])
        L.append('| %s | %d | %s | %s |' % (r, ch[r], ROLE_TEXT[r], rg))
    L.append('')
    L.append('## Arrangement\n')
    L.append('| Bars | Section | Parts |')
    L.append('|---|---|---|')
    for n, a, b, txt in SECTION_TEXT:
        L.append('| %d-%d | %s | %s |' % (a, b, n, txt))
    L.append('')
    L.append('%s\n' % WARNING)
    L.append('%s\n' % PROGRAM)
    L.append('## Preview\n')
    L.append('%s Files: `preview/preview.mp3`, `film/preview.mp4`. Both are %s. %s\n' % (preview_sentence(ctx), PREVIEW_LINE, AUDITION))
    L.append('## Verify\n')
    L.append('```')
    L.append('python3 generator/build.py %s   # rebuilds every file below from the rules' % slug)
    L.append('```')
    L.append('MIDI bytes are reproducible from the seeds. The MP3, MP4 and JPEG files depend on the ffmpeg and Pillow versions, so their hashes can differ after a rebuild. Needs Python 3, numpy, scipy, Pillow, mido and ffmpeg.\n')
    L.append('## Layout\n')
    L.append('`midi/` the MIDI kits and the validation report. `preview/` the audio preview and its manifest. `film/` the preview film, poster and captions. `art/` the hero and square illustrations. '
             '`social/` draft post material, never posted. `articles/` draft article, never published. `catalog/` machine-readable catalog. `checks/` the release checklist. `docs/` the publication plan. '
             '`generator/` the code that wrote all of it. `index.html` and `media.html` are the catalog pages.\n')
    L.append('## Limits\n')
    L.append('Notes only. No audition by a person has happened. Rule-based generation can sound plain, so audition the parts in your own instrument before you rely on them.\n')
    return '\n'.join(L)


def publication_plan(ctx):
    slug = ctx['slug']
    return ('# Publication plan: %s\n\n'
            'Status: draft. Nothing in this folder has been posted, published or announced.\n\n'
            '## Before publishing\n\n'
            '1. Listen to the parts in a real instrument. %s\n'
            '2. Choose a license and add a LICENSE file. None is set today.\n'
            '3. If the pack will be sold, check the terms of the store you plan to use.\n\n'
            '## GitHub Pages\n\n'
            '1. Repository Settings, Pages, deploy from the `main` branch, folder `/` (root). Only the repository owner can do this.\n'
            '2. Wait for the build, then open %s and check that `index.html` loads and the preview plays.\n'
            '3. Treat the address as live only after it responds.\n\n'
            '## Rollback\n\n'
            'Revert the merge commit, or set the Pages source to none. The files are plain static files, so nothing else needs undoing.\n\n'
            '## Draft material\n\n'
            '`articles/` and `social/` hold drafts. They are not posted. Review each before posting under your name.\n' % (ctx['title'], AUDITION, pages_url(slug)))


# ---------------------------------------------------------------- pages
CSS = '''
:root{--bg:%%BG%%;--ac:%%AC%%;--tx:#f5f5f5;--mu:#c9c9d0;--pn:rgba(255,255,255,.07);--ln:rgba(255,255,255,.22)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--ac)}
a:focus-visible,button:focus-visible,audio:focus-visible,canvas:focus-visible{outline:3px solid #fff;outline-offset:2px}
header,main,footer{max-width:60rem;margin:0 auto;padding:0 1rem}
header img{width:100%;height:auto;display:block;border-radius:10px;margin-top:1rem}
h1{font-size:clamp(1.8rem,5vw,2.8rem);margin:.8rem 0 .2rem}
h2{font-size:1.35rem;margin:2rem 0 .6rem}
.lede{color:var(--mu);max-width:44rem}
.note{border:1px solid var(--ln);background:var(--pn);border-radius:8px;padding:.7rem 1rem;margin:1rem 0}
.tabs{display:flex;flex-wrap:wrap;gap:.5rem;margin:.5rem 0}
button.tab{background:transparent;color:var(--tx);border:1px solid var(--ln);border-radius:999px;padding:.5rem 1rem;font:inherit;cursor:pointer;min-height:44px}
button.tab[aria-pressed=true]{background:var(--ac);color:#000;border-color:var(--ac);font-weight:700}
canvas{width:100%;height:auto;background:rgba(0,0,0,.35);border:1px solid var(--ln);border-radius:8px;display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:.8rem}
.card{border:1px solid var(--ln);background:var(--pn);border-radius:8px;padding:.8rem 1rem}
table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{border-bottom:1px solid var(--ln);padding:.4rem .5rem;text-align:left;vertical-align:top}
.scroll{overflow-x:auto}
.legend{display:flex;flex-wrap:wrap;gap:.3rem 1rem;margin:.5rem 0;padding:0;list-style:none;font-size:.9rem}
.legend i{display:inline-block;width:.9rem;height:.9rem;border-radius:3px;margin-right:.35rem;vertical-align:-.1rem}
footer{padding-bottom:3rem;color:var(--mu);font-size:.9rem}
audio{width:100%}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
'''

JS = '''
(function(){
var D=JSON.parse(document.getElementById('data').textContent);
var COL={drums:'#ff7b54',bass:'#ffd166',keys:'#06d6a0',motif:'#4cc9f0',sequence:'#c77dff',pad:'#e5e5e5'};
var cv=document.getElementById('lanes'),ctx=cv.getContext('2d');
var cur=0;
function draw(){
  var k=D.kits[cur],dpr=window.devicePixelRatio||1,W=1200,H=420;
  cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.clearRect(0,0,W,H);
  var L=86,R=10,T=18,B=22,lh=(H-T-B)/6,pw=(W-L-R)/32;
  ctx.font='12px sans-serif';ctx.textBaseline='middle';
  for(var b=0;b<32;b++){
    if(b%8===0){ctx.fillStyle='rgba(255,255,255,.07)';ctx.fillRect(L+b*pw,T,pw*8,H-T-B);}
    ctx.fillStyle='rgba(255,255,255,.55)';ctx.textAlign='left';
    if(b%4===0)ctx.fillText(String(b+1),L+b*pw+2,T-8);
  }
  D.roles.forEach(function(r,i){
    var y0=T+i*lh,nn=k.notes[r];
    ctx.fillStyle='#f5f5f5';ctx.textAlign='right';ctx.fillText(r,L-8,y0+lh/2);
    ctx.strokeStyle='rgba(255,255,255,.18)';ctx.beginPath();ctx.moveTo(L,y0+lh);ctx.lineTo(W-R,y0+lh);ctx.stroke();
    if(!nn.length)return;
    var lo=1e9,hi=-1e9;nn.forEach(function(n){lo=Math.min(lo,n[2]);hi=Math.max(hi,n[2]);});
    var sp=Math.max(hi-lo,6);
    ctx.fillStyle=COL[r];
    nn.forEach(function(n){
      var x=L+n[0]/16*pw,w=Math.max(1.5,n[1]/16*pw-.5);
      var y=y0+lh-4-((n[2]-lo)/sp)*(lh-10);
      ctx.fillRect(x,y-2,w,4);
    });
  });
  document.getElementById('kitfacts').textContent=k.id+' '+k.name+', '+k.bpm+' BPM, '+k.key+' '+k.mode+'. Chords: '+k.chords+'.';
}
var box=document.getElementById('tabs');
D.kits.forEach(function(k,i){
  var b=document.createElement('button');b.className='tab';b.type='button';
  b.textContent=k.id+' '+k.name;b.setAttribute('aria-pressed',i===0?'true':'false');
  b.onclick=function(){cur=i;[].forEach.call(box.children,function(c,j){c.setAttribute('aria-pressed',j===i?'true':'false');});draw();};
  box.appendChild(b);
});
draw();
})();
'''


def e(s):
    return html.escape(str(s), quote=True)


def index_html(ctx, lane_data):
    p, pal = ctx['prof'], ctx['pal']
    data = dict(roles=ROLES, kits=lane_data)
    css = CSS.replace('%%BG%%', pal[0]).replace('%%AC%%', pal[1])
    rows = []
    for k in ctx['kits']:
        for f in k['files']:
            rows.append('<tr><td>%s</td><td><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>' % (
                e(k['id']), e(f['path']), e(f['path'].split('/', 1)[1]), e(f['role']), e(f['notes'])))
    kit_cards = ''.join('<div class="card"><h3 style="margin:.1rem 0">%s %s</h3><p style="margin:.2rem 0">%d BPM, %s %s</p><p style="margin:.2rem 0;color:var(--mu)">%s</p></div>'
                        % (e(k['id']), e(k['name']), k['bpm'], e(k['root']), e(k['mode']), e(chords(k['kit']))) for k in ctx['kits'])
    sect = ''.join('<tr><td>%d-%d</td><td>%s</td><td>%s</td></tr>' % (a, b, e(n), e(t)) for n, a, b, t in SECTION_TEXT)
    legend = ''.join('<li><i style="background:%s"></i>%s</li>' % (c, r) for r, c in zip(ROLES, ['#ff7b54', '#ffd166', '#06d6a0', '#4cc9f0', '#c77dff', '#e5e5e5']))
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s MIDI pack</title>
<meta name="description" content="%(about)s">
<style>%(css)s</style></head>
<body>
<header>
<img src="art/hero.jpg" width="1280" height="720" alt="%(alt)s">
<h1>%(title)s</h1>
<p class="lede">%(about)s</p>
<p class="note"><strong>Status:</strong> %(aud)s The audio and the film are %(pl)s. They are a simple synthesized render of the MIDI, not a recording and not a mix. No license is set.</p>
</header>
<main>
<h2>Listen to the preview</h2>
<p>%(prev)s</p>
<audio controls preload="none" src="preview/preview.mp3">Your browser does not play audio. The file is preview/preview.mp3.</audio>
<p><a href="media.html">Film, images and draft posts</a></p>

<h2>Kits</h2>
<div class="grid">%(cards)s</div>

<h2>Arrangement view</h2>
<p>Pick a kit to see its 32-bar arrangement. Each row is a role. Notes are drawn by start, length and pitch.</p>
<div class="tabs" id="tabs" role="group" aria-label="Choose a kit"></div>
<canvas id="lanes" width="1200" height="420" tabindex="0" role="img" aria-label="Piano-roll view of the selected kit arrangement, six rows, 32 bars. The same information is in the section table below."></canvas>
<ul class="legend" aria-label="Legend">%(legend)s</ul>
<p id="kitfacts" aria-live="polite"></p>
<div class="scroll"><table><caption style="text-align:left;color:var(--mu)">Arrangement sections, same for every kit</caption><thead><tr><th>Bars</th><th>Section</th><th>Parts</th></tr></thead><tbody>%(sect)s</tbody></table></div>

<h2>How to use the files</h2>
<p>%(use)s</p>
<p>%(warn)s</p>
<p>%(prog)s</p>

<h2>All MIDI files</h2>
<div class="scroll"><table><thead><tr><th>Kit</th><th>File</th><th>Role</th><th>Notes</th></tr></thead><tbody>%(rows)s</tbody></table></div>
<p>Checks: <a href="midi/validation-Claude.json">midi/validation-Claude.json</a>, <a href="checks/artifact-checklist-Claude.json">checks/artifact-checklist-Claude.json</a>, <a href="catalog/catalog-Claude.json">catalog/catalog-Claude.json</a>.</p>
</main>
<footer><p>%(pub)s</p><p>Source: <a href="%(repo)s">%(repo)s</a></p></footer>
<script type="application/json" id="data">%(data)s</script>
<script>%(js)s</script>
</body></html>
''' % dict(title=e(ctx['title']), about=e(p['about']), css=css, alt=e(hero_alt(ctx)), aud=e(AUDITION), pl=e(PREVIEW_LINE),
           prev=e(preview_sentence(ctx) + ' ' + PREVIEW_LINE + '.'), cards=kit_cards, legend=legend, sect=sect,
           use=e(p['use']), warn=e(WARNING), prog=e(PROGRAM), rows=''.join(rows), pub=e(publication(ctx['slug'])),
           repo=e(repo_url(ctx['slug'])), data=json.dumps(data, separators=(',', ':')).replace('</', '<\\/'), js=JS)


def media_html(ctx):
    pal = ctx['pal']
    css = CSS.replace('%%BG%%', pal[0]).replace('%%AC%%', pal[1])
    _body, xbody = x_post(ctx)
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s media</title><style>%(css)s</style></head>
<body><header><h1>%(title)s media</h1>
<p class="lede">Film, images and draft posts. Nothing here has been posted. %(aud)s</p>
<p><a href="index.html">Back to the catalog</a></p></header>
<main>
<h2>Preview film</h2>
<video controls preload="none" width="1280" height="720" poster="film/poster.jpg" style="width:100%%;height:auto;border-radius:8px">
<source src="film/preview.mp4" type="video/mp4"><track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
Your browser does not play video. The file is film/preview.mp4.</video>
<p>The film shows %(on)s. Its sound is the same preview as the MP3.</p>
<h2>Images</h2>
<div class="grid">
<figure class="card"><img src="art/square.jpg" width="1080" height="1080" style="width:100%%;height:auto" alt="%(alt_sq)s"><figcaption>art/square.jpg, 1080 by 1080</figcaption></figure>
<figure class="card"><img src="social/instagram-Claude/portrait.jpg" width="1080" height="1350" style="width:100%%;height:auto" alt="%(alt_po)s"><figcaption>social/instagram-Claude/portrait.jpg, 1080 by 1350</figcaption></figure>
<figure class="card"><img src="social/x-Claude/card.jpg" width="1200" height="675" style="width:100%%;height:auto" alt="%(alt_x)s"><figcaption>social/x-Claude/card.jpg, 1200 by 675</figcaption></figure>
</div>
<h2>Draft X post</h2>
<p class="note">%(x)s</p>
<p><a href="social/instagram-Claude/captions-Claude.md">Instagram caption draft</a> | <a href="articles/medium-draft-Claude.md">Article draft</a></p>
</main><footer><p>%(pub)s</p></footer></body></html>
''' % dict(title=e(ctx['title']), css=css, aud=e(AUDITION), on=e(ON_PICTURE), alt_sq=e(ctx['alt_square']), alt_po=e(ctx['alt_portrait']),
           alt_x=e(ctx['alt_x']), x=e(xbody), pub=e(publication(ctx['slug'])))
