# Psychill

**Slow psychedelic downtempo: half-time drums, ninth chords, soft bell motifs and long pads in the 90 to 105 BPM range.** 52 MIDI files (4 kits x 6 roles x 2 variations, plus 4 arrangements), notes only, no samples.

## Status

- Built and checked by script. Validator result: 52 files, 0 errors. See `midi/validation-Claude.json`.
- No human listening audition was performed for this build.
- The audio preview and the film are preview, not a master. They are a simple synthesized render, not a recording and not a mix.
- The GitHub repository is https://github.com/mizcausevic-dev/psychill and it is public. The catalog address is https://mizcausevic-dev.github.io/psychill/ . Treat that address as live only after it responds.
- No license is set in this repository. Add one before you sell or redistribute the files.

## Kits

| Kit | BPM | Key | Mode | Chords |
|---|---|---|---|---|
| k01 Moss Lantern | 98 | A | dorian | Am9 (2 bars) | D9 (2 bars) | Am9 (2 bars) | Em7 (2 bars) |
| k02 Slow Spores | 92 | E | aeolian | Em7 (2 bars) | Cmaj7 (2 bars) | Am7 (2 bars) | B7 (2 bars) |
| k03 Amber Drift | 104 | D | dorian | Dm9 (4 bars) | G13 (2 bars) | Dm9 (2 bars) |
| k04 Night Garden | 96 | G | mixolydian | G9 (2 bars) | Fmaj7 (2 bars) | Cmaj9 (2 bars) | G9 (2 bars) |

## Roles

Each kit folder `midi/<kit>/` holds `<role>-a.mid` and `<role>-b.mid` (8 bars, 4/4, 960 ticks per quarter note, format 0) and `arrangement.mid` (32 bars, format 1, one tempo track plus six role tracks).

| Role | Channel | What it is | Written range (MIDI note) |
|---|---|---|---|
| drums | 10 | drum pattern on channel 10 (GM drum map) | GM drum map |
| bass | 1 | monophonic bass line | 36 to 55 |
| keys | 2 | chord voicings, up to four notes at once | 48 to 76 |
| motif | 3 | monophonic hook, the part the arrangement restates at the end | 60 to 86 |
| sequence | 4 | monophonic running pattern, used in place of the motif | 52 to 81 |
| pad | 5 | sustained chord layer, up to four notes at once | 48 to 81 |

## Arrangement

| Bars | Section | Parts |
|---|---|---|
| 1-8 | theme | drums A, bass A, keys A, pad A, motif A |
| 9-16 | sequence | drums A, bass A, keys A, pad A, sequence A |
| 17-24 | open | keys B, pad B, sequence B. No drums, bass or motif. |
| 25-32 | return | drums B, bass B, keys A, pad A, motif A |

Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.

No program changes are encoded. A conventional GM player will normally use its default piano program for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. Player behavior may vary.

## Preview

Preview is Moss Lantern bars 17-32 at 98 BPM, 39.210 seconds, not the 32-bar MIDI. Files: `preview/preview.mp3`, `film/preview.mp4`. Both are preview, not a master. No human listening audition was performed for this build.

## Verify

```
python3 generator/build.py psychill   # rebuilds every file below from the rules
```
MIDI bytes are reproducible from the seeds. The MP3, MP4 and JPEG files depend on the ffmpeg and Pillow versions, so their hashes can differ after a rebuild. Needs Python 3, numpy, scipy, Pillow, mido and ffmpeg.

## Layout

`midi/` the MIDI kits and the validation report. `preview/` the audio preview and its manifest. `film/` the preview film, poster and captions. `art/` the hero and square illustrations. `social/` draft post material, never posted. `articles/` draft article, never published. `catalog/` machine-readable catalog. `checks/` the release checklist. `docs/` the publication plan. `generator/` the code that wrote all of it. `index.html` and `media.html` are the catalog pages.

## Limits

Notes only. No audition by a person has happened. Rule-based generation can sound plain, so audition the parts in your own instrument before you rely on them.
