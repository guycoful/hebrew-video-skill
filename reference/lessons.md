# Lessons behind the pipeline (3.9.2026, Control Center client video)

## Why not HyperFrames
Three wipes in one day, each right after a `hyperframes render` failed/was stopped or `skills update` ran: the project folder, then all of `outputs/valor` (brief, rough cuts, keys, VO, user uploads), then the project again **plus a backup folder two levels up**. Nothing in the Recycle Bin. Also: its bundled chrome-headless-shell is blocked on this PC ("spawn UNKNOWN"; direct exec = Permission denied) and it needs `HYPERFRAMES_BROWSER_PATH` pointed at system Chrome. Banned.

## ElevenLabs facts
- `eleven_v3` is the only model listing Hebrew; it accepts `/with-timestamps`, so character timing for captions works.
- `eleven_multilingual_v2` speaks Hebrew unofficially but Guy rejected it as robotic.
- **PVC does not support Hebrew** (39 languages, none Hebrew) and trains only on Flash/Turbo/Multilingual v2; `eleven_v3` has `can_be_finetuned: false`. `POST /voices/pvc/{id}/train` answers `{"status":"ok"}` yet `fine_tuning.state` stays `{}` forever. Voice `ma6RJ8S3AeaumgehntdT` ("Guy Cohen HE PVC") was deleted and recreated on 4.9.2026 as `WZgqJaSYXQ2OtBWkc1zJ`; Guy wants it kept. The UI shows "not fine-tuned … instabilities" — expected for Hebrew. Do not delete account voices without asking.
- Instant clones from Guy's 32-min studio take: `jUf6zBvAkDrBllNnevJJ` (3-min slice), **`ND8JTbPy2RGiXF2rpt6p` (4×2.5-min slices) — chosen**. Older one-sample clones `pEC1hVCB2mYHhaaS3B9A` / `cJ6GWxLpNcAblrtC1aVv` are worse (D-style stability 1.0 distorts; the "Guy Voice" clone stresses רובוט on the wrong syllable).
- `eleven_multilingual_v2 + style 0.2 + speed 0.95` was the robotic combination; plain `stability 0.5 / similarity 0.75` on v3 won the A/B.
- Output `mp3_44100_192`, then transcode to 48 kHz stereo WAV for ffmpeg mixing (`amix normalize=0`).

## ffmpeg / Chrome details
- This ffmpeg build rejects `-filter_complex_script`; use `-/filter_complex <file>`.
- `boxblur=luma_r:luma_p:chroma_r:chroma_p` — chroma radius ≥ 7 fails on yuv420p.
- Overlays: `chrome.exe --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1920,1080 --default-background-color=00000000 --screenshot=<png> file:///…html` gives a true RGBA PNG; Segoe UI renders Hebrew correctly (in HyperFrames the same name was aliased to Roboto).
- Each overlay is its own ffmpeg input with `-loop 1 -t <dur>`, `setpts=PTS-STARTPTS+<start>/TB`, `fade=t=in:alpha=1`, and `overlay=…:enable='between(t,a,b)'`. 60+ inputs render fine.
- The user's own long PVC take: two m4a parts joined with `concat`, `pan=mono`, `highpass=f=70`, `volume=6dB` → peak −1.9 dB.

## Numbers that recur in Valor copy
21,876 runs / 90 days · 103 tracked processes · 34 with a clear rhythm · 3 machines · 59 % busiest · checks every 5 minutes · 17d 19h stuck job vs 1m 38s typical.

## Punch / High-Impact Editions (Lessons learned 6.9.2026, Manager sign-off)
- **Visuals**: Posters, big bold numbers (140-210px), dark cyber grid, 3-5 words per shot, zero micro-dashboard clutter. Legible from 10m away.
- **Audio DOs**: Use conventional, driving, upbeat corporate tech music (128-138 BPM, e.g. `Presenterator`, `Shiny Tech`). Master at ~ -13.4 LUFS. Continuous flow across all 60s.
- **Audio DONTs (Firm rule from management)**:
  1. Never add artificial explosion/sub-bass boom SFX (`sub_landing.wav`) between transitions every 4 seconds. Management finds them jarring, exaggerated, and cheap ("בומים מוגזמים ולא יפים").
  2. Never use aggressive sidechain ducking pump on cuts.
  3. Never choose dark industrial, dissonant, horror, or noisy tracks (like `REACTOR` with screeching at 00:40). Management finds them scary and intolerable ("רעש נוראי ומפחיד, מזוויע ב-00:40").
  4. Never use quiet elevator/piano music (`bed1` at 0.35 gain) when a punchy/kicking cut is requested.

## Hebrew stress (4.9.2026)
`eleven_v3` places stress on the last syllable of any Hebrew-script word and ignores nikud, hyphens, meteg and spacing for stress purposes (six spellings of בלוגים tested, all ba-lo-GIM). Loanwords that Israelis stress penultimately must be written in Latin script inside the Hebrew line ("בקבצי ה-log"), which is also what the caption shows. Nikud never reaches the screen: map it away in `display`. Scribe QA cannot catch stress errors because it strips nikud and returns consonants only — send the user an mp3 instead.

## Vertical Shorts / Reels & Advanced Hebrew Synchronization (6.9.2026)

### 1. Pronunciation Stability and The "ערכה" Rule
- **Ambiguous Hebrew words break TTS:** Words without explicit vowels can fail silently or with wrong vowels and incorrect stress. For example, "ערכה" is frequently misread as "ARAKA" or stressed on the first syllable like English ("ÉR-ka") instead of Israeli Hebrew milra ("er-KÁ").
- **Do not fight the model with endless phonetic hacks:** Attempting to force stress with hyphens or question marks ("הער-כָּה ?") can introduce unnatural acoustic pauses or plosive bursts.
- **The Golden Replacement Rule:** If a Hebrew word fails in TTS or creates pronunciation ambiguity, **replace it immediately with an unambiguous synonym**. Changing "רוצים את הערכה המלאה ?" ל-"רוצים את החבילה המלאה ?" פתר את הבעיה בטייק ראשון בצליל טבעי וללא עמימות.
- **Loanwords and dagesh:** Loanwords like "טלפרומפטר" must be checked to ensure the Pe is pronounced hard (P, not F). If needed, write "טלפרומפטר" with dagesh or phonetically.
- **Never simulate organic human groans/snores:** Never attempt to generate snore sounds, grunts or sighing noises ("אה אה אה") via TTS. It sounds distorted, uncanny and grotesque. Keep the voice clean, articulate and professional, and let royalty-free fairy-tale background music and crisp UI sound effects (ping, sparkle, whoosh) tell the story.

### 2. Subtitle Synchronization and Dynamic Badge Design
- **Verbatim accuracy is non-negotiable:** Viewers read and listen simultaneously. Dropping even a single connective word (like "ללכת", "מהחיים", "בינה מלאכותית", "ממני") creates an immediate feeling of desynchronization.
- **Always extract centisecond word timestamps with Whisper:** Never estimate subtitle start and end times by ear. Run `faster-whisper` with `word_timestamps=True` directly on the final mixed/spliced audio.
- **Dynamic badge timing:** The visual highlight badge (yellow `#facc15` or cyan `#38bdf8`) must trigger at the exact millisecond the spoken word begins.
- **Word chunk density:** Limit subtitle chunks to 2 to 4 words per view. Long sentences clutter the screen and look like outdated corporate slides.
- **Typography:** Use **Heebo Black** (`font-weight: 900`, -0.5px letter-spacing). Never use default serif fonts or Segoe UI for social media reels.
- **Safe zones (9:16):**
  - General vertical dialogue: `bottom: 810px` (chest height) avoids both Instagram/TikTok bottom UI and top headers.
  - Scene-specific exceptions: If foreground subjects (e.g. dogs, laptops, desks) occupy the lower center, elevate the caption box to `bottom: 1020px` to prevent occlusion.

### 3. Vertical Video Engineering and Timing Budget
- **Duration limit:** Instagram Reels and YouTube Shorts strictly require < 60.00s. Target 58.5s to 59.5s (e.g. 59.36s). Anything beyond 60.00s breaks shorts categorization on platforms.
- **Avoid AI face distortion:** When animating static illustrated characters, AI video generators often distort facial features or morph eyes unnaturally across cuts. Keep characters in their original clean keyframe state or use controlled subtle cinematic pans/zooms (lerp + ease-in-out).
- **Audio mixing standards:** Master voiceover leveled to -14 LUFS, background music ducked to 0.08 with lowpass filter at 4500Hz to preserve voice intelligibility, and SFX aligned to millisecond cue marks.
