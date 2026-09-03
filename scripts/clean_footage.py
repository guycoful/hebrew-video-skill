# -*- coding: utf-8 -*-
"""Crop the browser chrome, blur client names in time-boxed rectangles, scale to the stage. Config: project.json → footage_clean.
blur_boxes are [x, y, w, h, t_from, t_to] in CROPPED coordinates. Writes assets/probe_<sec>.png frames for a visual check."""
import json, subprocess
P = json.load(open("project.json", encoding="utf-8"))["footage_clean"]
cw, ch, cx, cy = P["crop"]; sw, sh = P["scale"]
chain = f"[0:v]crop={cw}:{ch}:{cx}:{cy}"
lab = "s0"
parts = []
cur = "[c0]"; parts.append(chain + "[c0]")
for i, (x, y, w, h, t0, t1) in enumerate(P.get("blur_boxes", [])):
    parts.append(f"{cur}split[p{i}a][p{i}b];[p{i}b]crop={w}:{h}:{x}:{y},boxblur=10:3:6:3[r{i}];[p{i}a][r{i}]overlay={x}:{y}:enable='between(t,{t0},{t1})'[c{i+1}]")
    cur = f"[c{i+1}]"
parts.append(f"{cur}scale={sw}:{sh}[out]")
fc = ";".join(parts)
subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", P["source"], "-an", "-filter_complex", fc, "-map", "[out]",
                       "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", P["output"]])
for s in P.get("probe_seconds", []):
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-i", P["output"], "-frames:v", "1", "-vf", "scale=960:-1", f"assets/probe_{s}.png"])
print("clean footage ->", P["output"], "| probes:", P.get("probe_seconds", []))
