# -*- coding: utf-8 -*-
import os, subprocess, pathlib

PUNCH_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
    width: 1920px; height: 1080px; overflow: hidden;
    background: radial-gradient(circle at 50% 40%, #0d1322 0%, #05070b 80%);
    font-family: 'Segoe UI', 'Segoe UI Variable', -apple-system, sans-serif;
    color: #fff; position: relative;
}
.punch-grid {
    position: absolute; inset: 0;
    background-image: linear-gradient(rgba(56, 189, 248, 0.06) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(56, 189, 248, 0.06) 1px, transparent 1px);
    background-size: 80px 80px;
    mask-image: radial-gradient(circle at 50% 45%, black 45%, transparent 85%);
}
.punch-orb-cyan {
    position: absolute; width: 900px; height: 650px; border-radius: 50%;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.28) 0%, transparent 70%);
    top: 50px; left: 50%; transform: translateX(-50%);
    filter: blur(60px); pointer-events: none;
}
.punch-orb-red {
    position: absolute; width: 900px; height: 650px; border-radius: 50%;
    background: radial-gradient(circle, rgba(239, 68, 68, 0.32) 0%, transparent 70%);
    top: 50px; left: 50%; transform: translateX(-50%);
    filter: blur(60px); pointer-events: none;
}
.punch-orb-amber {
    position: absolute; width: 900px; height: 650px; border-radius: 50%;
    background: radial-gradient(circle, rgba(245, 158, 11, 0.28) 0%, transparent 70%);
    top: 50px; left: 50%; transform: translateX(-50%);
    filter: blur(60px); pointer-events: none;
}
.punch-stage {
    position: absolute; top: 40px; left: 80px; width: 1760px; height: 750px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center;
}
.punch-tag {
    display: inline-flex; align-items: center; gap: 12px;
    padding: 10px 30px; border-radius: 30px;
    font-size: 24px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 24px;
}
.punch-headline {
    font-size: 96px; font-weight: 900; line-height: 1.08; letter-spacing: -2px;
    text-shadow: 0 10px 40px rgba(0,0,0,0.8);
}
.punch-sub {
    font-size: 40px; font-weight: 700; color: #94a3b8; margin-top: 20px; line-height: 1.3;
}
.punch-big-num {
    font-size: 190px; font-weight: 950; line-height: 0.95; letter-spacing: -4px;
}
.punch-big-text {
    unicode-bidi: isolate; white-space: nowrap; position: absolute; left: 50%;
    transform: translateX(-50%); max-width: 1800px; bottom: 105px;
    text-align: center; font-size: 92px; font-weight: 800; line-height: 1.25;
    padding: 20px 64px; border-radius: 26px;
    background: rgba(8, 11, 16, 0.95); color: #fff;
    border: 2.5px solid rgba(56, 189, 248, 0.7);
    box-shadow: 0 25px 70px rgba(0,0,0,0.9), 0 0 50px rgba(56, 189, 248, 0.35);
}
.punch-big-text b { font-weight: 900; color: #38bdf8; }
"""

def build_punch_shot(n, it, L, HERE, CHROME, ff, ENC, W, H, FPS, RLM, ease_out):
    out = f"overlays/punch_seg{n}.mp4"
    scene_body, orb_type = PUNCH_SCENES.get(n, ("", "punch-orb-cyan"))
    
    html_scene = f"""<!doctype html>
    <html lang="he" dir="rtl">
    <head><meta charset="utf-8"><style>{PUNCH_CSS}</style></head>
    <body>
        <div class="punch-grid"></div>
        <div class="{orb_type}"></div>
        <div class="punch-stage">{scene_body}</div>
    </body>
    </html>
    """
    
    h_scene = HERE / "overlays" / f"punch_shot{n}_scene.html"
    p_scene = HERE / "overlays" / f"punch_shot{n}_scene.png"
    h_scene.write_text(html_scene, encoding="utf-8")
    
    if not p_scene.exists():
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={W},{H}", "--default-background-color=00000000", f"--screenshot={p_scene}", h_scene.as_uri()],
                       check=True, capture_output=True, timeout=120)
    
    inputs = ["-f", "lavfi", "-i", f"color=c=0x05070b:s={W}x{H}:r={FPS}:d={L}",
              "-loop", "1", "-t", str(L), "-i", str(p_scene).replace('\\', '/')]
    
    # Impact Zoom Snap: fast slam in first 14 frames (0.45s), then subtle drift
    slam_frames = 14
    kb_expr = f"zoompan=z='if(lte(on,{slam_frames}), 1.10 - 0.10*on/{slam_frames}, 1.00 + 0.03*(on-{slam_frames})/({L*FPS}))':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps={FPS}"
    
    fc = [
        f"[1:v]scale={W*2}:{H*2}:flags=lanczos,{kb_expr},format=rgba[scene]",
        f"[0:v][scene]overlay=0:0[bg_scene]"
    ]
    last = "[bg_scene]"
    if it.get("text"):
        html_text = f"""<!doctype html>
        <html lang="he" dir="rtl">
        <head><meta charset="utf-8"><style>{PUNCH_CSS} body{{background:transparent;}}</style></head>
        <body>
            <div class="punch-big-text" dir="rtl">{RLM}{it["text"]}{RLM}</div>
        </body>
        </html>
        """
        h_text = HERE / "overlays" / f"punch_shot{n}_text.html"
        p_text = HERE / "overlays" / f"punch_shot{n}_text.png"
        h_text.write_text(html_text, encoding="utf-8")
        if not p_text.exists():
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                            f"--window-size={W},{H}", "--default-background-color=00000000", f"--screenshot={p_text}", h_text.as_uri()],
                           check=True, capture_output=True, timeout=120)
        inputs += ["-loop", "1", "-t", str(L), "-i", str(p_text).replace('\\', '/')]
        # text snaps in fast at 0.15s
        fc += [
            f"[2:v]format=rgba,fade=t=in:st=0.15:d=0.25:alpha=1[tx]",
            f"[bg_scene][tx]overlay=0:'{ease_out('t', 0.15, 0.45, 60)}':enable='gte(t,0.15)'[c]"
        ]
        last = "[c]"
    fc.append(f"{last}format=yuv420p[v]")
    ff(inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-t", str(L)] + ENC + [out])
    return out


PUNCH_SCENES = {
    # 0: עשרות תהליכי אוטומציה.
    0: ('''
    <div class="punch-tag" style="background: rgba(56,189,248,0.15); border: 2px solid #38bdf8; color: #38bdf8; box-shadow: 0 0 30px rgba(56,189,248,0.4);">
        ⚡ ENTERPRISE RPA FLEET
    </div>
    <div class="punch-big-num" style="color: #38bdf8; text-shadow: 0 0 80px rgba(56,189,248,0.7);">
        103
    </div>
    <div class="punch-headline" style="color: #fff; margin-top: 10px;">
        תהליכים פעילים בו-זמנית.
    </div>
    <div class="punch-sub" style="color: #94a3b8;">
        עשרות שרתים · אלפי משימות · 21,876 הרצות ב-90 יום
    </div>
    ''', "punch-orb-cyan"),

    # 1: מי רואה את כולם ביחד?
    1: ('''
    <div class="punch-tag" style="background: rgba(239,68,68,0.15); border: 2px solid #ef4444; color: #f87171; box-shadow: 0 0 30px rgba(239,68,68,0.4);">
        ⚠️ BLIND SPOT ALERT
    </div>
    <div style="font-size: 210px; font-weight: 950; color: #ef4444; text-shadow: 0 0 90px rgba(239,68,68,0.9); line-height: 0.9;">
        ?
    </div>
    <div class="punch-headline" style="color: #fff; margin-top: 10px;">
        אפס נראות מרכזית.
    </div>
    <div class="punch-sub" style="color: #fca5a5;">
        מערכות מבודדות · שרתים נפרדים · אף אחד לא רואה את התמונה המלאה
    </div>
    ''', "punch-orb-red"),

    # 2: מה מתוכנן, מתי, על איזה משאב?
    2: ('''
    <div class="punch-tag" style="background: rgba(245,158,11,0.15); border: 2px solid #f59e0b; color: #fbbf24; box-shadow: 0 0 30px rgba(245,158,11,0.4);">
        ⚡ RESOURCE COLLISION
    </div>
    <div class="punch-big-num" style="color: #fbbf24; text-shadow: 0 0 80px rgba(245,158,11,0.8);">
        14:00
    </div>
    <div class="punch-headline" style="color: #fff; margin-top: 10px;">
        2 ג'ובים מתנגשים על רובוט אחד.
    </div>
    <div class="punch-sub" style="color: #fde68a;">
        עומסי שיא לא מנוהלים · תורים תקועים · משאבים מושבתים
    </div>
    ''', "punch-orb-amber"),

    # 3: היום? מנהלים את זה ב-Excel.
    3: ('''
    <div class="punch-tag" style="background: rgba(239,68,68,0.15); border: 2px solid #ef4444; color: #f87171; box-shadow: 0 0 30px rgba(239,68,68,0.4);">
        ❌ HUMAN ERROR DISASTER
    </div>
    <div style="display: flex; align-items: center; justify-content: center; gap: 40px; position: relative;">
        <div style="font-size: 170px; font-weight: 950; color: #107c41; letter-spacing: -2px; text-shadow: 0 0 60px rgba(16,124,65,0.5);">
            EXCEL
        </div>
        <!-- Huge Slanted Stamp -->
        <div style="position: absolute; transform: rotate(-12deg); background: #ef4444; color: #fff; font-size: 56px; font-weight: 950; padding: 12px 36px; border-radius: 16px; border: 4px solid #fff; box-shadow: 0 10px 40px rgba(0,0,0,0.8), 0 0 50px rgba(239,68,68,0.8); letter-spacing: 3px;">
            באמת?!
        </div>
    </div>
    <div class="punch-headline" style="color: #fff; margin-top: 20px;">
        #REF! · #VALUE! · קבצים מיושנים
    </div>
    <div class="punch-sub" style="color: #fca5a5;">
        אוטומציה במיליונים – מנוהלת בקובץ טבלה של פעם
    </div>
    ''', "punch-orb-red"),

    # 4: רובוט שלא רץ? אף אחד לא יודע.
    4: ('''
    <div class="punch-tag" style="background: rgba(239,68,68,0.2); border: 2px solid #ef4444; color: #f87171; box-shadow: 0 0 40px rgba(239,68,68,0.5);">
        ☠️ SILENT FAILURE
    </div>
    <!-- Red EKG Flatline Bar -->
    <div style="width: 1400px; height: 120px; display: flex; align-items: center; justify-content: center; margin: 15px 0;">
        <svg viewBox="0 0 1200 100" style="width: 100%; height: 100px;">
            <line x1="0" y1="50" x2="1200" y2="50" stroke="#ef4444" stroke-width="8" stroke-dasharray="24 12"/>
        </svg>
    </div>
    <div class="punch-headline" style="color: #ef4444; text-shadow: 0 0 50px rgba(239,68,68,0.8);">
        רובוט קפא. שקט מוחלט.
    </div>
    <div class="punch-sub" style="color: #fca5a5;">
        0 שגיאות נזרקו · 0 התראות נשלחו · הלקוח יגלה ראשון
    </div>
    ''', "punch-orb-red"),

    # 5: תקוע 17 יום. נראה ירוק.
    5: ('''
    <div class="punch-tag" style="background: rgba(239,68,68,0.2); border: 2px solid #ef4444; color: #f87171; box-shadow: 0 0 40px rgba(239,68,68,0.5);">
        ⚡ THE FALSE GREEN TRAP
    </div>
    <div class="punch-big-num" style="color: #ef4444; text-shadow: 0 0 90px rgba(239,68,68,0.9); font-size: 160px;">
        17 ימים.
    </div>
    <div class="punch-headline" style="color: #fff; margin-top: 10px;">
        נראה ירוק במערכת. תקוע בזיכרון.
    </div>
    <div class="punch-sub" style="color: #fde68a;">
        זמן ריצה רגיל: 01:38 דק' · חריגה של +1,500,000%
    </div>
    ''', "punch-orb-red"),

    # 6: תצוגה חכמה אחת. בזמן אמת.
    6: ('''
    <div class="punch-tag" style="background: rgba(56,189,248,0.2); border: 2px solid #38bdf8; color: #38bdf8; box-shadow: 0 0 40px rgba(56,189,248,0.6);">
        🛡️ MISSION CONTROL REVEAL
    </div>
    <div style="font-size: 80px; font-weight: 950; color: #fff; letter-spacing: -2px;">
        VALOR CONTROL CENTER
    </div>
    <div class="punch-big-num" style="color: #38bdf8; text-shadow: 0 0 90px rgba(56,189,248,0.9); font-size: 140px; margin-top: 10px;">
        100%
    </div>
    <div class="punch-headline" style="color: #fff; font-size: 64px;">
        שליטה מלאה. מסך אחד. זמן אמת.
    </div>
    ''', "punch-orb-cyan"),

    # 7: כל תהליך. כל ריצה. כל מגמה.
    7: ('''
    <div class="punch-tag" style="background: rgba(56,189,248,0.15); border: 2px solid #38bdf8; color: #38bdf8;">
        📊 90-DAY DEEP TELEMETRY
    </div>
    <div class="punch-big-num" style="color: #38bdf8; text-shadow: 0 0 80px rgba(56,189,248,0.7); font-size: 140px;">
        10 שניות.
    </div>
    <div class="punch-headline" style="color: #fff; margin-top: 10px;">
        להבין כל תהליך וכל מגמה.
    </div>
    <div class="punch-sub" style="color: #94a3b8;">
        במקום לנבור שעות בלוגים · אבחון מיידי של 21,876 הרצות
    </div>
    ''', "punch-orb-cyan"),

    # 8: הריצה הבאה? המערכת כבר יודעת.
    8: ('''
    <div class="punch-tag" style="background: rgba(56,189,248,0.2); border: 2px solid #38bdf8; color: #38bdf8; box-shadow: 0 0 30px rgba(56,189,248,0.5);">
        🎯 PREDICTIVE AI TARGET LOCK
    </div>
    <div style="border: 3px solid #38bdf8; border-radius: 28px; padding: 20px 60px; background: rgba(56,189,248,0.15); display: inline-block; box-shadow: 0 0 60px rgba(56,189,248,0.4);">
        <div style="font-size: 120px; font-weight: 950; color: #fff; line-height: 1;">NEXT RUN: 14:00</div>
    </div>
    <div class="punch-headline" style="color: #38bdf8; margin-top: 24px; text-shadow: 0 0 40px rgba(56,189,248,0.7);">
        ה-AI לומד את הקצב לבד.
    </div>
    <div class="punch-sub" style="color: #cbd5e1;">
        זיהוי אי-הופעה וסטייה של שניות · בלי להגדיר חוק ידני אחד
    </div>
    ''', "punch-orb-cyan"),

    # 9: עומסים, התנגשויות, מקום פנוי.
    9: ('''
    <div class="punch-tag" style="background: rgba(245,158,11,0.2); border: 2px solid #f59e0b; color: #fbbf24; box-shadow: 0 0 30px rgba(245,158,11,0.4);">
        ⚡ CAPACITY OPTIMIZATION
    </div>
    <div style="display: flex; justify-content: center; gap: 80px; align-items: center;">
        <div>
            <div style="font-size: 130px; font-weight: 950; color: #ef4444; line-height: 0.95;">92%</div>
            <div style="font-size: 32px; font-weight: 800; color: #fca5a5;">עומס יתר</div>
        </div>
        <div style="font-size: 90px; color: #38bdf8; font-weight: 900;">➔</div>
        <div>
            <div style="font-size: 130px; font-weight: 950; color: #10b981; line-height: 0.95;">82%</div>
            <div style="font-size: 32px; font-weight: 800; color: #6ee7b7;">מקום פנוי</div>
        </div>
    </div>
    <div class="punch-headline" style="color: #fff; margin-top: 20px;">
        איזון משאבים מושלם.
    </div>
    <div class="punch-sub" style="color: #cbd5e1;">
        מנצלים כל רישיון רובוט עד הסוף · אפס ניחושים
    </div>
    ''', "punch-orb-amber"),

    # 10: התראה תוך 5 דקות. בלי רעש.
    10: ('''
    <div class="punch-tag" style="background: rgba(56,189,248,0.2); border: 2px solid #38bdf8; color: #38bdf8; box-shadow: 0 0 40px rgba(56,189,248,0.6);">
        🚨 5-MINUTE EARLY WARNING
    </div>
    <div class="punch-big-num" style="color: #38bdf8; text-shadow: 0 0 90px rgba(56,189,248,0.9); font-size: 170px;">
        05:00
    </div>
    <div class="punch-headline" style="color: #fff; margin-top: 10px;">
        התראה מדויקת. בלי רעש.
    </div>
    <div class="punch-sub" style="color: #34d399; font-weight: 800;">
        45 דקות לפני שהעסק מרגיש תקלה.
    </div>
    ''', "punch-orb-cyan")
}
