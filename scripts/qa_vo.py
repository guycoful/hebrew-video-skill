# -*- coding: utf-8 -*-
"""Pronunciation QA: transcribe every generated VO segment with ElevenLabs Scribe and diff against the narration.
Prints, per segment, the words the model apparently said differently. Run after vo.py, before render."""
import os, json, uuid, urllib.request, difflib, re
P = json.load(open("project.json", encoding="utf-8"))
env_file = os.path.expanduser(P["voice"].get("env_file", "~/.config/valor-video/.env"))
KEY = {l.split('=',1)[0]: l.split('=',1)[1].strip() for l in open(env_file, encoding="utf-8") if '=' in l}["ELEVENLABS_API_KEY"]
VO = json.load(open("vo.json", encoding="utf-8"))
def stt(path):
    d = open(path, "rb").read(); b = uuid.uuid4().hex.encode(); body = b""
    for k, v in {"model_id": "scribe_v1", "language_code": "heb"}.items():
        body += b"--"+b+b'\r\nContent-Disposition: form-data; name="'+k.encode()+b'"\r\n\r\n'+v.encode()+b"\r\n"
    body += b"--"+b+b'\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n'+d+b"\r\n--"+b+b"--\r\n"
    r = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", body, {"xi-api-key": KEY, "Content-Type": "multipart/form-data; boundary="+b.decode()})
    return json.load(urllib.request.urlopen(r, timeout=600))["text"]
norm = lambda s: re.findall(r"[\w'’-]+", s.replace("-", " ").lower())
issues = 0
for o, text in zip(VO, P["narration"]):
    heard = stt(o["file"])
    a, h = norm(text), norm(heard)
    sm = difflib.SequenceMatcher(None, a, h)
    diffs = [(" ".join(a[i1:i2]), " ".join(h[j1:j2])) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
    print(f"--- segment {o['i']}  ({o['duration']}s)  {len(diffs)} differences")
    for x, y in diffs:
        print(f"   said: {y!r:40}  expected: {x!r}"); issues += 1
print("total differences:", issues, "(STT noise included; look for repeated offenders)")
