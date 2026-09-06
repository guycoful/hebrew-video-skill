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
3. Clean the footage: `python ~/.claude/skills/hebrew-video/scripts/clean_footage.py` (reads `project.json → footage_clean`). Verify with the probe frames it writes to `assets/probe_*.png`.
4. Voice: `python ~/.claude/skills/hebrew-video/scripts/vo.py` → `assets/vo/vo<N>.wav` + `vo.json` (caption chunks with character-level timing). Only missing segments are regenerated, so editing one line re-voices one line — delete `assets/vo/vo<N>.*` to force.
4b. **Pronunciation QA (mandatory):** `python ~/.claude/skills/hebrew-video/scripts/qa_vo.py` transcribes every segment with ElevenLabs Scribe and diffs it against the narration. Fix repeat offenders by respelling the *spoken* text and mapping it back in `display`, then delete that segment's `assets/vo/vo<N>.*` and rerun `vo.py`. Send the user the mp3 of any segment you are unsure about; only they can judge.
5. Render: `python ~/.claude/skills/hebrew-video/scripts/render.py` → `out/<name>.mp4`. Then QC: `ffmpeg -i out/x.mp4 -vf "select='eq(n,150)+eq(n,900)+eq(n,3000)',scale=640:-1,tile=3x1" -frames:v 1 out/qc.jpg` and look at it.
6. Send the MP4 with SendUserFile (uploads over ~10 MB sometimes time out to phone; the desktop copy still works) and mirror to OneDrive.

## Narration and caption conventions Guy signed off on

- Spoken text and on-screen text differ on purpose. `display` in `project.json` maps spoken → shown: digits and clock format on screen (ב-16:00, 17 יום, ב-03:12, 5 דקות, 20 דקות), English product terms on screen (Snooze, job, tolerance — and *tolerance* is also spoken in English), emphasis via `<b>…</b>` = same font, white, weight 800, no colour.
- One caption = **one line** (≤50 chars at 54 px). The splitter prefers commas, never breaks inside a Latin phrase (keeps "Valor Automation Control Center") and never before a ו-word (keeps "דקה וחצי").
- Captions run continuously, including over the title and closing cards, at `bottom:110px` so the player bar never covers them. Wrap every RTL overlay in U+200F on both ends so trailing punctuation sits on the right.
- Chips (top-right capability labels) are benefit-phrased ("יודעים על תהליך שלא רץ – לפני הלקוח"), appear 0.3 s into the scene and stay **exactly 4 s** so they never hide the app's top toolbar.
- **Fixed spellings, always (Guy's ruling):** speak **"וָואלוֹר"** (kamatz on the א, full holam after the ל, stress on the second syllable) → show `Valor`; speak **"UI Path"** (two English words, capital UI, a space — chosen by Guy from six A/B takes on 3.9.2026; nikud spellings like יוּ אַיי פַּאת'/פַּאף were NOT respected by the model) → show `UiPath`. Never write `Valor` or `UiPath` (one word) in the spoken text. Use these exact nikud strings in every project; speak "שבעה-עשר" (hyphen) not "שבעה עשר"; avoid "ניצולת" (unstable) → "ניצול הרובוטים"; avoid "קיבולת" → "מקום פנוי". **No full English sentences in the narration** (Guy: single terms are fine, sentences are not). Brochure slogans are spoken in Hebrew: "לראות. לשלוט. לייעל." and "הגיע הזמן לעבור מניהול אוטומציות באקסל, לתפעול חכם, נגיש ומקצועי." (Guy's wording, fixed) The three-word English tagline may stay on the title card only.
- **Stress on loanwords cannot be fixed with nikud.** eleven_v3 always stresses the final syllable in Hebrew script; kamatz, patah+dagesh, hyphen, meteg and a space after the prefix were all tested on "בלוגים" and all produced ba-lo-GIM. The fix is to write the loanword in **Latin script** inside the Hebrew sentence — "בקבצי ה-log", like the working `tolerance` and `job` — and let the caption show the same. Prefer the singular when it removes the stress question entirely (one syllable). Never put nikud in a caption; if a spoken spelling carries nikud, map it to a clean form in `display`.
- Words the model mispronounces: say "מיום שני" not "משני", "התפספס" not "פוספס", "פעלו" not "רצו" (it stresses רָצוּ like רצון), never "לחפור" (say "לחפש"). Write numbers as words in the spoken text (שבעה עשר, בתשעים, בשלוש ושתים עשרה) and let `display` show digits.
- Product name on screen: **Valor Automation Control Center** (Gal's internal name "Run Rhythm" stays off-screen). Closing card: on-prem message, "תאמו שיחת הדגמה · 20 דקות", the contact line from project.json → cards.close.contact.

## Footage cleaning

`clean_footage.py` crops the browser chrome (`crop=1920:946:0:85` for a 1920×1032 capture) so the URL bar never shows a client domain, scales to the 1760×868 stage, and applies time-boxed `boxblur` rectangles over client names (chroma radius must be < 7 or ffmpeg errors). Find coordinates by extracting a frame at the right second and reading pixel positions; the blur boxes are `[x, y, w, h, t_from, t_to]` in *cropped* coordinates.

## Silent conference loop (`render_loop.py`, added 6.9.2026)

`python ~/.claude/skills/hebrew-video/scripts/render_loop.py` renders a no-narration loop from `project.json → timeline` (items: `kind: shot|close|contact`, `src` second, `dur`, `text` = one big 96 px line, 3–5 words). First and last `black_seconds` are pure black so the loop closes; `--vo` adds the `narration_at` lines (ElevenLabs, same voice) and writes `output_vo`. The contact card draws a QR from `cards.contact.qr_url` (`pip install qrcode`). Reference project: `C:\Users\Valor\Videos\ValorConference` (60 s, 13 items, renders in ~70 s).

## High-impact "Punch" conference loops (`render_punch_loop.py`, added 6.9.2026)

When the user asks for a punchy / kicking version ("גרסה בועטת ומגרה"):
1. **Visuals**: Minimalist, bold, poster-style typography (140px–210px), big glowing numbers (`103`, `?`, `14:00`, `EXCEL! באמת?!`, flatline EKG bar, `17 ימים`, `100%`, `05:00`), dark cyber-grid with subtle ambient glow orbs. Less small dashboard clutter, much higher legibility from 10 meters away.
2. **Music**: Upbeat, driving, positive, conventional corporate tech / electro-pop (128–138 BPM, e.g. `Presenterator` or `Shiny Tech`). The music must drive continuously at ~ -13 LUFS across the full 60 seconds.
3. **STRICT RULES — What to AVOID AT ALL COSTS (Learned 6.9.2026, Management sign-off)**:
   - ❌ **NO artificial explosion / sub-bass "boom" SFX on transitions** (`sub_landing.wav`, impact bass drops every 4 seconds). They sound exaggerated, cheap, jarring, and unpleasing to management.
   - ❌ **NO aggressive sidechain ducking pump** on video cuts that sucks the music in and out.
   - ❌ **NO dark, scary, dissonant, horror, or noisy industrial tracks** (like `REACTOR` with metallic screeches or weird breakdowns at 00:40). Management finds this "רעש נוראי ומפחיד".
   - ❌ **NO quiet elevator/piano music** (`bed1` at 0.35 gain) that whispers in the background.

## Editing an existing video

- Change a line → edit `narration[i]` in `project.json`, delete `assets/vo/vo<i>.*`, run `vo.py` then `render.py`.
- Reorder / retime → edit `scenes` (source seconds), run `render.py` only.
- Re-voice everything → delete `assets/vo/*` and `vo.json`.
- The DISPLAY map and blur boxes are data, not code: edit `project.json`.

See `reference/lessons.md` for the incident log and the ElevenLabs findings.
