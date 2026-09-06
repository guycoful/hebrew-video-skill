---
name: hebrew-video
description: Produce high-conversion Hebrew marketing and product videos in both 16:9 landscape (desktop demo/client walkthrough) and 9:16 vertical (Instagram Reels, YouTube Shorts, TikTok) formats. Features cleaned footage or AI visual scenes, Hebrew voiceover in Guy's cloned voice (ElevenLabs eleven_v3, voice IVC10), centisecond-accurate RTL captions with dynamic word badges, and audio mixing with background music and SFX. Rendered via headless Chrome overlays and ffmpeg. Use for any "סרטון", "וידאו", "רילס", "שורטס", "קריינות", "כתוביות", "דיבוב", client demo, or automated video studio. Never use HyperFrames on this machine.
---

# Hebrew Video Production Pipeline (16:9 Landscape & 9:16 Vertical Shorts)

Everything runs from a **project folder** that holds configuration, `assets/`, `overlays/` and `out/`. Rendered with headless Chrome (transparent PNG overlays) and ffmpeg compositing.

## Hard Rules & Production Safeguards

1. **Never run `npx hyperframes …` on this PC:** HyperFrames commands wiped directories. This independent Chrome + ffmpeg pipeline replaces it completely.
2. **Platform Duration Budget (< 60.00s for Shorts/Reels):** Vertical videos must strictly remain below 60.00 seconds (ideal target: 58.5s to 59.5s). Any duration at or over 60.00s breaks short-form categorization and video loops.
3. **Pronunciation Golden Rule (Zero Ambiguity):**
   - Hebrew words with vowel ambiguity (e.g. "ערכה" which TTS mispronounces as "ARAKA" or with penultimate English stress "ÉR-ka") must **not** be fought with endless acoustic hacks.
   - **Immediately substitute ambiguous words with clean, unambiguous synonyms** (e.g. replace "ערכה" with "חבילה").
   - Technical loanwords: ensure explicit hard consonants (e.g. "טלפרומפטר" with dagesh in Pe, not "telefrompter").
   - **Zero vocal groans or snore simulations:** Never attempt to generate snore sounds, sighs or grunts ("אה אה אה") via TTS. They sound distorted and bizarre. Keep narration articulate and pair with subtle background music and clean SFX.
4. **Voice Engine:** ElevenLabs `eleven_v3` only. Voice **IVC10 = `ND8JTbPy2RGiXF2rpt6p`** ("Guy HE IVC 10min"), settings `stability 0.5, similarity 0.75`, no style/speed.
5. **Verbatim Subtitle Synchronization (Whisper Alignment):**
   - Captions must match the spoken words 100% verbatim. Dropping words (like "ללכת", "מהחיים", "בינה מלאכותית", "ממני") breaks synchronization.
   - Extract timestamps using `faster-whisper` (`word_timestamps=True`) directly on the final mixed/spliced audio.
6. **Keys and Config:** Keys live in `~/.config/valor-video/.env` (`ELEVENLABS_API_KEY=`) or environment variables. Never commit keys into project repos.

---

## Mode 1: 9:16 Vertical Reels / Shorts (Mobile Social)

### 1. Typography & Dynamic Badges
- **Font:** **Heebo Black** (`font-weight: 900`, -0.5px letter-spacing). Never use serif or standard desktop fonts.
- **Chunk Density:** 2 to 4 words per caption box. Fast, punchy and readable on mobile.
- **Badge Styling:**
  - Plain words: White `#ffffff` with heavy black stroke (`-webkit-text-stroke: 10px #000; paint-order: stroke fill;`) and deep drop shadow.
  - Active highlight badge: Rounded pill (`border-radius: 16px`, padding `8px 24px`), colored in vibrant yellow (`#facc15`) or electric cyan (`#38bdf8`) with black text (`#000000`).
  - Badge timing: Pops exactly on the start millisecond of the spoken keyword.
- **Vertical Safe Zones:**
  - Standard talking head / chest placement: `bottom: 810px`.
  - Cleared zone when lower third has prominent subjects (pets, desks, devices): `bottom: 1020px`.

### 2. Visual Animation & Camera Flow
- Divide video into 5 to 6 distinct visual scenes (7 to 12 seconds each).
- When animating static illustrations, avoid aggressive AI morphing that distorts human faces or eyes.
- Use controlled camera zooms and pans (lerp with cubic ease-in-out) in Python (PIL / OpenCV) to create smooth, high-end motion.
- Special visual cues (e.g. eye sparkle flare, graphic badges) must be placed at exact cue times.

### 3. Audio Mastering
- Speech normalized to `-14 LUFS` (`loudnorm=I=-14:TP=-1.5:LRA=11`).
- Royalty-free background music ducked to `volume=0.08` with a gentle `lowpass=f=4500` filter so narration remains crystal clear.
- Sound effects (whoosh, ping, sparkle, chime) mixed with millisecond precision via ffmpeg `adelay`.

---

## Mode 2: 16:9 Landscape Product & Client Demos (B2B Walkthrough)

### 1. Workflow
1. `mkdir C:\Users\Valor\Videos\<Project>\assets` and copy in: screen recording, `valor-logo-white.png`, `robot.png`.
2. Copy `templates/project.json` and edit: narration lines, scene list, chip labels, card texts, blur boxes.
3. Clean footage: `python ~/.claude/skills/hebrew-video/scripts/clean_footage.py` (crop browser chrome + time-boxed `boxblur`).
4. Voice: `python ~/.claude/skills/hebrew-video/scripts/vo.py` -> `assets/vo/vo<N>.wav` + `vo.json`.
5. Pronunciation QA: `python ~/.claude/skills/hebrew-video/scripts/qa_vo.py`.
6. Render: `python ~/.claude/skills/hebrew-video/scripts/render.py` -> `out/<name>.mp4`.

### 2. Captions & Capability Chips
- Spoken text and on-screen text differ on purpose: `display` in `project.json` maps spoken -> shown (digits, clock format, product terms).
- One caption = one single line (<= 50 chars at 54px), positioned at `bottom: 110px`.
- Benefit-phrased top-right chips appear 0.3s into a scene and stay **exactly 4 seconds**.
- **Fixed spellings (Guy's rulings):** speak **"וָואלוֹר"** -> show `Valor`; speak **"UI Path"** (two English words, capital UI, space) -> show `UiPath`. Never write `Valor` or `UiPath` as one word in spoken text.
- Loanwords: write in Latin script inside Hebrew line ("בקבצי ה-log", `tolerance`, `job`).
- Words to avoid/fix: say "מיום שני" not "משני", "התפספס" not "פוספס", "פעלו" not "רצו", "לחפש" not "לחפור".

---

## Mode 3: Silent & "Punch" Conference Loops

### 1. Standard Silent Loop (`render_loop.py`)
- Renders no-narration loop from `project.json -> timeline` with big 96px titles (3-5 words per shot) and contact QR card.

### 2. High-Impact "Punch" Loops (`render_punch_loop.py`)
- **Visuals:** Minimalist, bold poster typography (140px-210px), big glowing numbers, dark cyber-grid.
- **Music:** Upbeat, driving, positive corporate tech / electro-pop (128-138 BPM, e.g. `Presenterator`, `Shiny Tech`), continuous at ~ -13 LUFS.
- **Strict Audio Bans (Management ruling):**
  - NO artificial explosion / sub-bass "boom" SFX on transitions (`sub_landing.wav`).
  - NO aggressive sidechain ducking pump on video cuts.
  - NO dark, scary, dissonant, horror or noisy industrial tracks (`REACTOR`).
  - NO quiet elevator/piano music (`bed1` at 0.35 gain).

---

## Project Execution Checklist

1. **Draft Script & Validate Pronunciation:** Verify all words are unambiguous. If a word sounds awkward in test TTS, replace it with a synonym immediately (e.g. "ערכה" -> "חבילה").
2. **Synthesize TTS:** Run `eleven_v3` with timestamps. Save 48kHz 16-bit stereo WAV.
3. **Run Word Alignment:** Run `faster-whisper` on generated audio to record exact word start/end bounds.
4. **Render Overlays:** Generate transparent PNG overlays via headless Chrome.
5. **Composite Video:** Run ffmpeg graph (anim/footage + overlays + audio mix).
6. **Quality Control (QC):** Extract test frames at key timestamps. Verify:
   - Total duration strictly under target limit (< 60.00s for vertical).
   - No subtitle text clipping or awkward wraps.
   - Active highlight badge matches spoken word timing.
   - Audio balance: voice intelligible over BGM.

See `reference/lessons.md` for detailed technical logs and pronunciation test cases.
