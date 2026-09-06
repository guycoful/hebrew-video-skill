# -*- coding: utf-8 -*-
"""Hebrew voiceover per scene via ElevenLabs, driven by project.json in the current folder.
Writes assets/vo/vo<N>.mp3/.wav/.json and vo.json (durations + one-line caption chunks with timing).
Only segments whose .json is missing are (re)generated: delete assets/vo/vo<N>.* to re-voice one line."""
import os, sys, json, base64, urllib.request, urllib.error, subprocess

P = json.load(open("project.json", encoding="utf-8"))
V = P["voice"]
env_file = os.path.expanduser(V.get("env_file", "~/.config/valor-video/.env"))
env = {l.split('=', 1)[0]: l.split('=', 1)[1].strip() for l in open(env_file, encoding="utf-8") if '=' in l and not l.startswith('#')}
KEY = env["ELEVENLABS_API_KEY"]
VOICE, MODEL, VS = V["voice_id"], V.get("model_id", "eleven_v3"), V.get("voice_settings", {"stability": 0.5, "similarity_boost": 0.75})
NARRATION = P["narration"]
DISPLAY = [tuple(x) for x in P.get("display", [])]
MAXC = P.get("caption", {}).get("max_chars", 50)
REAL_DIR = "assets/vo-real"   # optional: Guy's own recordings vo<N>.wav override TTS

def display(t):
    for a, b in DISPLAY: t = t.replace(a, b)
    return t

def tts(text, mp3, meta):
    body = json.dumps({"text": text, "model_id": MODEL, "voice_settings": VS}).encode()
    H = {"xi-api-key": KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_192", body, H)
    try:
        j = json.load(urllib.request.urlopen(req, timeout=300))
        open(mp3, "wb").write(base64.b64decode(j["audio_base64"]))
        al = j["alignment"]
        json.dump({"chars": al["characters"], "starts": al["character_start_times_seconds"], "ends": al["character_end_times_seconds"]}, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
    except urllib.error.HTTPError as e:
        print("with-timestamps failed:", e.code, e.read()[:200], "-> plain TTS + proportional timing")
        req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_192", body, H)
        open(mp3, "wb").write(urllib.request.urlopen(req, timeout=300).read())
        proportional(text, mp3, meta)

def proportional(text, audio, meta):
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]).decode().strip())
    n = len(text); per = (d - 0.3) / n
    json.dump({"chars": list(text), "starts": [round(0.15 + k * per, 3) for k in range(n)], "ends": [round(0.15 + (k + 1) * per, 3) for k in range(n)]}, open(meta, "w", encoding="utf-8"), ensure_ascii=False)

def chunks_for(al):
    chars, starts, ends = al["chars"], al["starts"], al["ends"]
    def rng(a, b): return {"text": "".join(chars[a:b]).strip(), "start": round(starts[a], 2), "end": round(ends[b - 1], 2)}
    pieces, a = [], 0
    for k, c in enumerate(chars):
        if c in ".?:!" and k - a >= 20: pieces.append((a, k + 1)); a = k + 1
    if a < len(chars) and "".join(chars[a:]).strip(): pieces.append((a, len(chars)))
    def latin(c): return c.isascii() and c.isalpha()
    def ok_space(k):
        if chars[k] != " ": return False
        l = chars[k - 1] if k > 0 else ""; r = chars[k + 1] if k + 1 < len(chars) else ""
        if latin(l) and latin(r): return False        # keep "Valor Automation Control Center"
        if r == "ו": return False                      # keep "דקה וחצי"
        return True
    def split(a, b):
        if b - a <= MAXC: return [(a, b)]
        mid = (a + b) // 2
        commas = [k for k in range(a + 12, b - 12) if chars[k] == ","]
        cands = commas or [k for k in range(a + 12, b - 12) if ok_space(k)]
        if not cands: return [(a, b)]
        best = min(cands, key=lambda k: abs(k - mid))
        return split(a, best + 1) + split(best + 1, b)
    merged = []
    for a, b in pieces:
        for x, y in split(a, b):
            ch = rng(x, y)
            if merged and len(ch["text"]) < 14 and len(merged[-1]["text"]) + len(ch["text"]) <= MAXC:
                merged[-1]["text"] += " " + ch["text"]; merged[-1]["end"] = ch["end"]
            elif ch["text"]: merged.append(ch)
    # a caption line never ends on a dangling comma — the sentence continues on the next line
    for ch in merged: ch["text"] = display(ch["text"].rstrip().rstrip(",").rstrip())
    return merged

os.makedirs("assets/vo", exist_ok=True)
out = []
for i, text in enumerate(NARRATION):
    mp3, wav, meta = f"assets/vo/vo{i}.mp3", f"assets/vo/vo{i}.wav", f"assets/vo/vo{i}.json"
    real = f"{REAL_DIR}/vo{i}.wav"
    if os.path.exists(real):                      # Guy's own take wins over TTS
        if not os.path.exists(meta) or json.load(open(meta, encoding="utf-8")).get("source") != "real":
            subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", real, "-ar", "48000", "-ac", "2", "-af", "highpass=f=70,loudnorm=I=-18:TP=-2", wav])
            proportional(text, wav, meta); m = json.load(open(meta, encoding="utf-8")); m["source"] = "real"; json.dump(m, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
    else:
        if not os.path.exists(meta): tts(text, mp3, meta)
        if not os.path.exists(wav): subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "2", wav])
    al = json.load(open(meta, encoding="utf-8"))
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]).decode().strip())
    caps = chunks_for(al)
    out.append({"i": i, "file": wav, "duration": round(dur, 2), "captions": caps})
    print(i, round(dur, 1), "s", len(caps), "captions", "(real take)" if os.path.exists(real) else "")
json.dump(out, open("vo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total VO", round(sum(o["duration"] for o in out), 1), "s; longest caption", max(len(c["text"]) for o in out for c in o["captions"]), "chars")
