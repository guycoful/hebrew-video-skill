# Lessons behind the pipeline (3.9.2026, Control Center client video)

## Why not HyperFrames
Three wipes in one day, each right after a `hyperframes render` failed/was stopped or `skills update` ran: the project folder, then all of `outputs/valor` (brief, rough cuts, keys, VO, user uploads), then the project again **plus a backup folder two levels up**. Nothing in the Recycle Bin. Also: its bundled chrome-headless-shell is blocked on this PC ("spawn UNKNOWN"; direct exec = Permission denied) and it needs `HYPERFRAMES_BROWSER_PATH` pointed at system Chrome. Banned.

## ElevenLabs facts
- `eleven_v3` is the only model listing Hebrew; it accepts `/with-timestamps`, so character timing for captions works.
- `eleven_multilingual_v2` speaks Hebrew unofficially but Guy rejected it as robotic.
- **PVC does not support Hebrew** (39 languages, none Hebrew) and trains only on Flash/Turbo/Multilingual v2; `eleven_v3` has `can_be_finetuned: false`. `POST /voices/pvc/{id}/train` answers `{"status":"ok"}` yet `fine_tuning.state` stays `{}` forever. Voice `ma6RJ8S3AeaumgehntdT` ("Guy Cohen HE PVC") exists but is unusable.
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
