---
name: hebrew-video
description: Produce a Valor-branded Hebrew product/marketing video from a screen recording — cleaned footage (browser chrome cropped, client names blurred), Hebrew voiceover in Guy's cloned voice (ElevenLabs eleven_v3, voice IVC10), single-line RTL captions synced to the narration, top-right capability chips that show for exactly 4 s, and branded title / stats / closing cards — rendered with headless Chrome + one ffmpeg graph. Use for any "סרטון", "וידאו", "קריינות", "כתוביות", "דיבוב", client demo, conference loop or LinkedIn clip for Valor, and for edits to an existing one (change a line, re-time, re-voice, blur a name). Never use HyperFrames on this machine.
---

# Valor video pipeline

Everything runs from a **project folder** that holds `project.json`, `assets/`, `overlays/` and `out/`. The scripts live in this skill; the project folder only holds config and media. Renders take ~3 minutes for a 2–3 minute video.

## Hard rules (learned the expensive way, 3.9.2026)

1. **Never run `npx hyperframes …` on this PC.** Its render/skills commands wiped three directory trees, including a sibling backup. This pipeline replaced it.
2. **Render in `C:\Users\Valor\Videos\<Project>`**, not in a OneDrive-synced folder. Copy `out/` and `project.json` back to the OneDrive project root when done: `C:\Users\Valor\OneDrive - Valor\מסמכים\Codex\2026-08-09\tb\outputs\<project>\`.
3. **Keys live outside every project:** `C:\Users\Valor\.config\valor-video\.env` (`ELEVENLABS_API_KEY=`). Never copy keys into a project folder.
4. **Voice:** ElevenLabs `eleven_v3` only (the only model that speaks Hebrew). Voice **IVC10 = `ND8JTbPy2RGiXF2rpt6p`** ("Guy HE IVC 10min"), settings `stability 0.5, similarity 0.75`, no style/speed. Professional Voice Clone does **not** support Hebrew — do not try again. Highest-quality alternative: Guy reads the lines himself into `assets/vo-real/vo<N>.wav`.
5. **Back up user-supplied assets immediately** (logo, mascot, recordings) to a second folder before doing anything else.

## Workflow

1. `mkdir C:\Users\Valor\Videos\<Project>\assets` and copy in: the screen recording, `valor-logo-white.png`, `robot.png` (both in `C:\Users\Valor\Videos\ValorControlCenter\assets\` — reuse).
2. Copy `templates/project.json` from this skill into the project folder and edit: narration lines, scene list (source seconds in the recording), chip labels, card texts, blur boxes.
3. Clean the footage: `python <skill>/scripts/clean_footage.py` (reads `project.json → footage_clean`). Verify with the probe frames it writes to `assets/probe_*.png`.
4. Voice: `python <skill>/scripts/vo.py` → `assets/vo/vo<N>.wav` + `vo.json` (caption chunks with character-level timing). Only missing segments are regenerated, so editing one line re-voices one line — delete `assets/vo/vo<N>.*` to force.
4b. **Pronunciation QA (mandatory):** `python <skill>/scripts/qa_vo.py` transcribes every segment with ElevenLabs Scribe and diffs it against the narration. Fix repeat offenders by respelling the *spoken* text and mapping it back in `display`, then delete that segment's `assets/vo/vo<N>.*` and rerun `vo.py`. Send the user the mp3 of any segment you are unsure about; only they can judge.
5. Render: `python <skill>/scripts/render.py` → `out/<name>.mp4`. Then QC: `ffmpeg -i out/x.mp4 -vf "select='eq(n,150)+eq(n,900)+eq(n,3000)',scale=640:-1,tile=3x1" -frames:v 1 out/qc.jpg` and look at it.
6. Send the MP4 with SendUserFile (uploads over ~10 MB sometimes time out to phone; the desktop copy still works) and mirror to OneDrive.

## Narration and caption conventions Guy signed off on

- Spoken text and on-screen text differ on purpose. `display` in `project.json` maps spoken → shown: digits and clock format on screen (ב-16:00, 17 יום, ב-03:12, 5 דקות, 20 דקות), English product terms on screen (Snooze, job, tolerance — and *tolerance* is also spoken in English), emphasis via `<b>…</b>` = same font, white, weight 800, no colour.
- One caption = **one line** (≤50 chars at 54 px). The splitter prefers commas, never breaks inside a Latin phrase (keeps "Valor Automation Control Center") and never before a ו-word (keeps "דקה וחצי").
- Captions run continuously, including over the title and closing cards, at `bottom:110px` so the player bar never covers them. Wrap every RTL overlay in U+200F on both ends so trailing punctuation sits on the right.
- Chips (top-right capability labels) are benefit-phrased ("יודעים על תהליך שלא רץ – לפני הלקוח"), appear 0.3 s into the scene and stay **exactly 4 s** so they never hide the app's top toolbar.
- **Fixed spellings, always (Guy's ruling):** speak **"וָואלוֹר"** (kamatz on the א, full holam after the ל, stress on the second syllable) → show `Valor`; speak **"יוּ אַיי פַּאף"** → show `UiPath`. Never write `Valor` or `UiPath` in the spoken text — the model breaks on them every time. Use these exact nikud strings in every project; speak "שבעה-עשר" (hyphen) not "שבעה עשר"; avoid "ניצולת" (unstable) → "ניצול הרובוטים"; avoid "קיבולת" → "מקום פנוי". Keep "See. Control. Optimize." spoken, shown as `See · Control · Optimize.`
- Words the model mispronounces: say "מיום שני" not "משני", "התפספס" not "פוספס". Write numbers as words in the spoken text (שבעה עשר, בתשעים, בשלוש ושתים עשרה) and let `display` show digits.
- Product name on screen: **Valor Automation Control Center** (Gal's internal name "Run Rhythm" stays off-screen). Closing card: on-prem message, "תאמו שיחת הדגמה · 20 דקות", the contact line from project.json → cards.close.contact.

## Footage cleaning

`clean_footage.py` crops the browser chrome (`crop=1920:946:0:85` for a 1920×1032 capture) so the URL bar never shows a client domain, scales to the 1760×868 stage, and applies time-boxed `boxblur` rectangles over client names (chroma radius must be < 7 or ffmpeg errors). Find coordinates by extracting a frame at the right second and reading pixel positions; the blur boxes are `[x, y, w, h, t_from, t_to]` in *cropped* coordinates.

## Editing an existing video

- Change a line → edit `narration[i]` in `project.json`, delete `assets/vo/vo<i>.*`, run `vo.py` then `render.py`.
- Reorder / retime → edit `scenes` (source seconds), run `render.py` only.
- Re-voice everything → delete `assets/vo/*` and `vo.json`.
- The DISPLAY map and blur boxes are data, not code: edit `project.json`.

See `reference/lessons.md` for the incident log and the ElevenLabs findings.
