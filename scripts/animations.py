# -*- coding: utf-8 -*-
import os, subprocess, pathlib

ANIM_CSS = """
.grid-bg {
    position: absolute; inset: 0;
    background-image: linear-gradient(rgba(123, 167, 208, 0.07) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(123, 167, 208, 0.07) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(circle at 50% 40%, black 50%, transparent 85%);
}
.glow-orb {
    position: absolute; width: 850px; height: 600px; border-radius: 50%;
    background: radial-gradient(circle, rgba(123, 167, 208, 0.22) 0%, transparent 70%);
    top: 40px; left: 50%; transform: translateX(-50%);
    filter: blur(50px); pointer-events: none;
}
.anim-stage {
    position: absolute; top: 50px; left: 80px; width: 1760px; height: 740px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.header-badge {
    display: inline-flex; align-items: center; gap: 14px;
    padding: 12px 32px; border-radius: 40px;
    background: rgba(123, 167, 208, 0.12); border: 1.5px solid rgba(123, 167, 208, 0.4);
    font-size: 26px; font-weight: 700; color: #7BA7D0; letter-spacing: 1.5px;
    margin-bottom: 28px; box-shadow: 0 0 30px rgba(123, 167, 208, 0.2);
}
.pulse-dot { width: 14px; height: 14px; border-radius: 50%; background: #10b981; box-shadow: 0 0 14px #10b981; }
.pulse-dot-red { width: 14px; height: 14px; border-radius: 50%; background: #ef4444; box-shadow: 0 0 14px #ef4444; }
.pulse-dot-amber { width: 14px; height: 14px; border-radius: 50%; background: #f59e0b; box-shadow: 0 0 14px #f59e0b; }
"""

def build_anim_shot(n, it, L, HERE, CHROME, CSS, ff, ENC, W, H, FPS, BGHEX, RLM, ease_out):
    out = f"overlays/seg{n}.mp4"
    scene_body = SCENES.get(n, "")
    full_css = CSS + ANIM_CSS
    
    h_scene = HERE / "overlays" / f"shot{n}_scene.html"
    p_scene = HERE / "overlays" / f"shot{n}_scene.png"
    h_scene.write_text(f'<!doctype html><html lang="he"><head><meta charset="utf-8"><style>{full_css}</style></head><body><div class="stage"><div class="grid-bg"></div><div class="glow-orb"></div><div class="anim-stage">{scene_body}</div></div></body></html>', encoding="utf-8")
    if not p_scene.exists():
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={W},{H}", "--default-background-color=00000000", f"--screenshot={p_scene}", h_scene.as_uri()],
                       check=True, capture_output=True, timeout=120)
    
    inputs = ["-f", "lavfi", "-i", f"color=c={BGHEX}:s={W}x{H}:r={FPS}:d={L}",
              "-loop", "1", "-t", str(L), "-i", str(p_scene).replace('\\', '/')]
    
    kb_expr = f"zoompan=z='1+0.035*on/{L*FPS}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps={FPS}"
    fc = [
        f"[1:v]scale={W*2}:{H*2}:flags=lanczos,{kb_expr},format=rgba[scene]",
        f"[0:v][scene]overlay=0:0[bg_scene]"
    ]
    last = "[bg_scene]"
    if it.get("text"):
        h_text = HERE / "overlays" / f"shot{n}_text.html"
        p_text = HERE / "overlays" / f"shot{n}_text.png"
        h_text.write_text(f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>{full_css} body{{background:transparent;}}</style></head><body><div class="stage"><div class="big" dir="rtl">{RLM}{it["text"]}{RLM}</div></div></body></html>', encoding="utf-8")
        if not p_text.exists():
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                            f"--window-size={W},{H}", "--default-background-color=00000000", f"--screenshot={p_text}", h_text.as_uri()],
                           check=True, capture_output=True, timeout=120)
        inputs += ["-loop", "1", "-t", str(L), "-i", str(p_text).replace('\\', '/')]
        fc += [
            f"[2:v]format=rgba,fade=t=in:st=0.25:d=0.4:alpha=1[tx]",
            f"[bg_scene][tx]overlay=0:'{ease_out('t', 0.25, 0.6, 70)}':enable='gte(t,0.25)'[c]"
        ]
        last = "[c]"
    fc.append(f"{last}format=yuv420p[v]")
    ff(inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-t", str(L)] + ENC + [out])
    return out


SCENES = {
    # 0: עשרות תהליכי אוטומציה.
    0: '''
    <div class="header-badge">
        <div class="pulse-dot"></div>
        <span>VALOR AUTOMATION CLUSTER · 103 ACTIVE PROCESSES</span>
    </div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; width: 1560px;">
        <div style="background: rgba(18, 24, 38, 0.88); border: 1.5px solid rgba(123, 167, 208, 0.3); border-radius: 22px; padding: 26px 32px; backdrop-filter: blur(20px); display: flex; flex-direction: column; gap: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:28px; font-weight:700; color:#fff;">SAP Financial Billing</span>
                <span style="background:rgba(16,185,129,0.18); color:#34d399; border:1px solid rgba(16,185,129,0.4); padding:8px 16px; border-radius:12px; font-size:17px; font-weight:700;">● ACTIVE</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.08); padding-top:14px; font-size:20px; color:#94a3b8;">
                <span>Daily Execution</span><span style="color:#7BA7D0; font-weight:700; font-size:22px;">99.8% Success</span>
            </div>
        </div>
        <div style="background: rgba(18, 24, 38, 0.88); border: 1.5px solid rgba(123, 167, 208, 0.3); border-radius: 22px; padding: 26px 32px; backdrop-filter: blur(20px); display: flex; flex-direction: column; gap: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:28px; font-weight:700; color:#fff;">Salesforce Lead Ingestion</span>
                <span style="background:rgba(56,189,248,0.18); color:#38bdf8; border:1px solid rgba(56,189,248,0.4); padding:8px 16px; border-radius:12px; font-size:17px; font-weight:700;">⚡ RUNNING</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.08); padding-top:14px; font-size:20px; color:#94a3b8;">
                <span>Real-Time Trigger</span><span style="color:#7BA7D0; font-weight:700; font-size:22px;">1m 42s avg</span>
            </div>
        </div>
        <div style="background: rgba(18, 24, 38, 0.88); border: 1.5px solid rgba(123, 167, 208, 0.3); border-radius: 22px; padding: 26px 32px; backdrop-filter: blur(20px); display: flex; flex-direction: column; gap: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:28px; font-weight:700; color:#fff;">Automated PO Dispatcher</span>
                <span style="background:rgba(16,185,129,0.18); color:#34d399; border:1px solid rgba(16,185,129,0.4); padding:8px 16px; border-radius:12px; font-size:17px; font-weight:700;">● ACTIVE</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.08); padding-top:14px; font-size:20px; color:#94a3b8;">
                <span>Queue: 1,420 items</span><span style="color:#7BA7D0; font-weight:700; font-size:22px;">Optimal</span>
            </div>
        </div>
        <div style="background: rgba(18, 24, 38, 0.88); border: 1.5px solid rgba(123, 167, 208, 0.3); border-radius: 22px; padding: 26px 32px; backdrop-filter: blur(20px); display: flex; flex-direction: column; gap: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:28px; font-weight:700; color:#fff;">HR Employee Onboarding</span>
                <span style="background:rgba(16,185,129,0.18); color:#34d399; border:1px solid rgba(16,185,129,0.4); padding:8px 16px; border-radius:12px; font-size:17px; font-weight:700;">● ACTIVE</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.08); padding-top:14px; font-size:20px; color:#94a3b8;">
                <span>Weekly Schedule</span><span style="color:#7BA7D0; font-weight:700; font-size:22px;">100% SLA</span>
            </div>
        </div>
        <div style="background: rgba(18, 24, 38, 0.88); border: 1.5px solid rgba(123, 167, 208, 0.3); border-radius: 22px; padding: 26px 32px; backdrop-filter: blur(20px); display: flex; flex-direction: column; gap: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:28px; font-weight:700; color:#fff;">Warehouse Inventory Audit</span>
                <span style="background:rgba(56,189,248,0.18); color:#38bdf8; border:1px solid rgba(56,189,248,0.4); padding:8px 16px; border-radius:12px; font-size:17px; font-weight:700;">⚡ RUNNING</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.08); padding-top:14px; font-size:20px; color:#94a3b8;">
                <span>Batch #489</span><span style="color:#7BA7D0; font-weight:700; font-size:22px;">3 Robots</span>
            </div>
        </div>
        <div style="background: rgba(18, 24, 38, 0.88); border: 1.5px solid rgba(123, 167, 208, 0.3); border-radius: 22px; padding: 26px 32px; backdrop-filter: blur(20px); display: flex; flex-direction: column; gap: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:28px; font-weight:700; color:#fff;">Bank Account Reconciliation</span>
                <span style="background:rgba(16,185,129,0.18); color:#34d399; border:1px solid rgba(16,185,129,0.4); padding:8px 16px; border-radius:12px; font-size:17px; font-weight:700;">● ACTIVE</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.08); padding-top:14px; font-size:20px; color:#94a3b8;">
                <span>Nightly Cadence</span><span style="color:#7BA7D0; font-weight:700; font-size:22px;">0 Errors</span>
            </div>
        </div>
    </div>
    ''',

    # 1: מי רואה את כולם ביחד?
    1: '''
    <div class="header-badge" style="border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.12); color: #f87171;">
        <div class="pulse-dot-red"></div>
        <span>DISCONNECTED AUTOMATION SILOS · ZERO CENTRAL VISIBILITY</span>
    </div>
    <div style="position:relative; width: 1560px; height: 500px; display: flex; align-items: center; justify-content: center;">
        <div style="width: 440px; height: 440px; border-radius: 50%; border: 2px dashed rgba(239,68,68,0.5); background: radial-gradient(circle, rgba(239,68,68,0.15) 0%, rgba(15,17,21,0.9) 70%); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10; box-shadow: 0 0 60px rgba(239,68,68,0.25);">
            <div style="font-size: 110px; font-weight: 900; color: #f87171; text-shadow: 0 0 30px rgba(239,68,68,0.8); line-height: 1;">?</div>
            <div style="font-size: 24px; font-weight: 700; color: #fff; margin-top: 12px; letter-spacing: 1px;">BLIND SPOT</div>
            <div style="font-size: 16px; color: #fca5a5; margin-top: 4px;">No Unified Dashboard</div>
        </div>
        <div style="position: absolute; top: 20px; left: 60px; width: 380px; background: rgba(18,24,38,0.9); border: 1.5px solid rgba(255,255,255,0.15); border-radius: 20px; padding: 22px; box-shadow: 0 20px 40px rgba(0,0,0,0.6);">
            <div style="font-size: 22px; font-weight: 700; color: #7BA7D0; margin-bottom: 8px;">UiPath Orchestrator</div>
            <div style="font-size: 16px; color: #94a3b8;">Isolated Tenant · 8 Machines</div>
            <div style="margin-top: 12px; font-size: 14px; color: #ef4444; font-weight: 600;">❌ No Cross-System Link</div>
        </div>
        <div style="position: absolute; top: 20px; right: 60px; width: 380px; background: rgba(18,24,38,0.9); border: 1.5px solid rgba(255,255,255,0.15); border-radius: 20px; padding: 22px; box-shadow: 0 20px 40px rgba(0,0,0,0.6);">
            <div style="font-size: 22px; font-weight: 700; color: #7BA7D0; margin-bottom: 8px;">SAP & Core ERP</div>
            <div style="font-size: 16px; color: #94a3b8;">Batch Queues · Manual Triggers</div>
            <div style="margin-top: 12px; font-size: 14px; color: #ef4444; font-weight: 600;">❌ Separate Logs & Metrics</div>
        </div>
        <div style="position: absolute; bottom: 20px; left: 60px; width: 380px; background: rgba(18,24,38,0.9); border: 1.5px solid rgba(255,255,255,0.15); border-radius: 20px; padding: 22px; box-shadow: 0 20px 40px rgba(0,0,0,0.6);">
            <div style="font-size: 22px; font-weight: 700; color: #7BA7D0; margin-bottom: 8px;">Cloud VM Farm</div>
            <div style="font-size: 16px; color: #94a3b8;">Unmonitored CPU & Memory</div>
            <div style="margin-top: 12px; font-size: 14px; color: #ef4444; font-weight: 600;">❌ Hidden Resource Spikes</div>
        </div>
        <div style="position: absolute; bottom: 20px; right: 60px; width: 380px; background: rgba(18,24,38,0.9); border: 1.5px solid rgba(255,255,255,0.15); border-radius: 20px; padding: 22px; box-shadow: 0 20px 40px rgba(0,0,0,0.6);">
            <div style="font-size: 22px; font-weight: 700; color: #7BA7D0; margin-bottom: 8px;">Departmental Scripts</div>
            <div style="font-size: 16px; color: #94a3b8;">Local Excel & PowerAutomate</div>
            <div style="margin-top: 12px; font-size: 14px; color: #ef4444; font-weight: 600;">❌ Complete Visibility Void</div>
        </div>
    </div>
    ''',

    # 2: מה מתוכנן, מתי, על איזה משאב?
    2: '''
    <div class="header-badge" style="border-color: rgba(245,158,11,0.4); background: rgba(245,158,11,0.12); color: #fbbf24;">
        <div class="pulse-dot-amber"></div>
        <span>SCHEDULING & RESOURCE CONFLICT MAP</span>
    </div>
    <div style="width: 1560px; background: rgba(18,24,38,0.85); border: 1.5px solid rgba(123,167,208,0.3); border-radius: 24px; padding: 30px; box-shadow: 0 24px 50px rgba(0,0,0,0.6);">
        <div style="display: grid; grid-template-columns: 240px repeat(6, 1fr); padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 18px; color: #94a3b8; font-weight: 600;">
            <span>RESOURCE</span>
            <span style="text-align:center;">08:00</span>
            <span style="text-align:center;">10:00</span>
            <span style="text-align:center;">12:00</span>
            <span style="text-align:center; color:#fbbf24; font-weight:800;">14:00 (PEAK)</span>
            <span style="text-align:center;">16:00</span>
            <span style="text-align:center;">18:00</span>
        </div>
        <div style="display: grid; grid-template-columns: 240px 1fr; align-items: center; padding: 22px 0; border-bottom: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 22px; font-weight: 700; color: #fff;">Robot-VM-01 <span style="font-size:14px; color:#38bdf8; display:block;">Production</span></div>
            <div style="position: relative; height: 50px; background: rgba(255,255,255,0.03); border-radius: 12px;">
                <div style="position: absolute; left: 10%; width: 25%; height: 100%; background: linear-gradient(90deg, #10b981, #059669); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 17px;">SAP Billing</div>
                <div style="position: absolute; left: 45%; width: 30%; height: 100%; background: linear-gradient(90deg, #3b82f6, #1d4ed8); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 17px;">Doc OCR</div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 240px 1fr; align-items: center; padding: 22px 0; border-bottom: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 22px; font-weight: 700; color: #fff;">Robot-VM-02 <span style="font-size:14px; color:#fbbf24; display:block;">Finance Cluster</span></div>
            <div style="position: relative; height: 50px; background: rgba(255,255,255,0.03); border-radius: 12px;">
                <div style="position: absolute; left: 20%; width: 22%; height: 100%; background: linear-gradient(90deg, #6366f1, #4338ca); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 17px;">Inventory Sync</div>
                <div style="position: absolute; left: 52%; width: 28%; height: 100%; background: rgba(239,68,68,0.25); border: 2px solid #ef4444; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; color: #fca5a5; box-shadow: 0 0 20px rgba(239,68,68,0.5);">
                    ⚠️ CONFLICT: 2 JOBS OVERLAP
                </div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 240px 1fr; align-items: center; padding: 22px 0;">
            <div style="font-size: 22px; font-weight: 700; color: #fff;">Robot-VM-03 <span style="font-size:14px; color:#94a3b8; display:block;">Standby Batch</span></div>
            <div style="position: relative; height: 50px; background: rgba(255,255,255,0.03); border-radius: 12px;">
                <div style="position: absolute; left: 5%; width: 20%; height: 100%; background: linear-gradient(90deg, #0ea5e9, #0284c7); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 17px;">Email Reports</div>
                <div style="position: absolute; left: 40%; width: 45%; height: 100%; border: 2px dashed rgba(16,185,129,0.5); background: rgba(16,185,129,0.08); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 17px; color: #34d399;">
                    AVAILABLE CAPACITY (UNASSIGNED)
                </div>
            </div>
        </div>
    </div>
    ''',

    # 3: היום? מנהלים את זה ב-Excel.
    3: '''
    <div class="header-badge" style="border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.12); color: #f87171;">
        <div class="pulse-dot-red"></div>
        <span>THE REALITY: FRAGILE EXCEL SPREADSHEETS</span>
    </div>
    <div style="width: 1560px; background: #fff; color: #1e293b; border-radius: 20px; overflow: hidden; box-shadow: 0 30px 60px rgba(0,0,0,0.8); border: 2px solid #cbd5e1;">
        <div style="background: #107c41; color: #fff; padding: 14px 24px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; font-size: 20px; letter-spacing: 0.5px;">Auto_Schedule_Master_v4_FINAL_really_updated_2026.xlsx - Excel</span>
            <span style="background: rgba(239,68,68,0.9); color: #fff; padding: 4px 14px; border-radius: 8px; font-size: 14px; font-weight: 800;">OUTDATED</span>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 18px; text-align: left;">
            <thead>
                <tr style="background: #f1f5f9; color: #475569; font-weight: 700; border-bottom: 2px solid #cbd5e1;">
                    <th style="padding: 14px 20px; border-right: 1px solid #cbd5e1; width: 60px;">#</th>
                    <th style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">Process Name</th>
                    <th style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">Target Machine</th>
                    <th style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">Scheduled Time</th>
                    <th style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">Live Status</th>
                    <th style="padding: 14px 20px;">Operational Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 14px 20px; background: #f8fafc; font-weight: 700; border-right: 1px solid #cbd5e1;">1</td>
                    <td style="padding: 14px 20px; font-weight: 600; border-right: 1px solid #cbd5e1;">SAP Billing Daily</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">VM-Finance-01</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">04:00 AM</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1; color: #15803d; font-weight: 700;">Supposed to run</td>
                    <td style="padding: 14px 20px; color: #64748b;">Manual check required every morning</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0; background: #fff1f2;">
                    <td style="padding: 14px 20px; background: #ffe4e6; font-weight: 700; border-right: 1px solid #cbd5e1;">2</td>
                    <td style="padding: 14px 20px; font-weight: 700; color: #b91c1c; border-right: 1px solid #cbd5e1;">Invoice OCR Batch</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1; background: #fee2e2; color: #b91c1c; font-weight: 800;">#REF!</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">09:30 AM</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1; font-weight: 800; color: #dc2626;">FAILED YESTERDAY</td>
                    <td style="padding: 14px 20px; color: #b91c1c; font-weight: 700;">Formula broke after Excel cell deleted</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0; background: #fefce8;">
                    <td style="padding: 14px 20px; background: #fef9c3; font-weight: 700; border-right: 1px solid #cbd5e1;">3</td>
                    <td style="padding: 14px 20px; font-weight: 600; border-right: 1px solid #cbd5e1;">Salesforce Lead Sync</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">VM-Prod-02</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">14:00 PM</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1; color: #b45309; font-weight: 700;">Who updated this?</td>
                    <td style="padding: 14px 20px; color: #854d0e;">Someone changed schedule without telling IT</td>
                </tr>
                <tr>
                    <td style="padding: 14px 20px; background: #f8fafc; font-weight: 700; border-right: 1px solid #cbd5e1;">4</td>
                    <td style="padding: 14px 20px; font-weight: 600; border-right: 1px solid #cbd5e1;">Inventory Audit</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1; background: #fee2e2; color: #b91c1c; font-weight: 800;">#VALUE!</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1;">22:00 PM</td>
                    <td style="padding: 14px 20px; border-right: 1px solid #cbd5e1; color: #64748b;">Pending review</td>
                    <td style="padding: 14px 20px; color: #64748b;">Row 14 deleted accidentally by user</td>
                </tr>
            </tbody>
        </table>
    </div>
    ''',

    # 4: רובוט שלא רץ? אף אחד לא יודע.
    4: '''
    <div class="header-badge" style="border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.12); color: #f87171;">
        <div class="pulse-dot-red"></div>
        <span>THE SILENT FAILURE: 0 HEARTBEAT · NO ERROR TRIGGERED</span>
    </div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; width: 1560px;">
        <div style="background: rgba(18,24,38,0.85); border: 1.5px solid rgba(16,185,129,0.4); border-radius: 22px; padding: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:24px; font-weight:700;">Robot-01 (Prod)</span>
                <span style="color:#34d399; font-weight:700;">100% HEALTH</span>
            </div>
            <svg viewBox="0 0 400 100" style="width:100%; height:100px; margin: 20px 0;">
                <path d="M0,50 L100,50 L120,20 L140,80 L160,10 L180,70 L200,50 L400,50" fill="none" stroke="#10b981" stroke-width="4" stroke-linecap="round"/>
            </svg>
            <div style="font-size:18px; color:#94a3b8; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 14px;">
                Heartbeat: <span style="color:#10b981; font-weight:700;">Every 30s Active</span>
            </div>
        </div>
        <div style="background: rgba(45,15,20,0.9); border: 2px solid #ef4444; border-radius: 22px; padding: 30px; box-shadow: 0 0 50px rgba(239,68,68,0.4);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:24px; font-weight:700; color:#fca5a5;">Robot-02 (Batch)</span>
                <span style="background:#ef4444; color:#fff; padding:4px 12px; border-radius:8px; font-weight:800; font-size:14px;">SILENT DEATH</span>
            </div>
            <svg viewBox="0 0 400 100" style="width:100%; height:100px; margin: 20px 0;">
                <line x1="0" y1="50" x2="400" y2="50" stroke="#ef4444" stroke-width="4" stroke-dasharray="10 5"/>
            </svg>
            <div style="font-size:18px; color:#fca5a5; border-top: 1px solid rgba(239,68,68,0.3); padding-top: 14px;">
                Last Beat: <span style="color:#ef4444; font-weight:800;">8 HOURS AGO · 0 ALERTS</span>
            </div>
        </div>
        <div style="background: rgba(18,24,38,0.85); border: 1.5px solid rgba(16,185,129,0.4); border-radius: 22px; padding: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:24px; font-weight:700;">Robot-03 (CRM)</span>
                <span style="color:#34d399; font-weight:700;">99% HEALTH</span>
            </div>
            <svg viewBox="0 0 400 100" style="width:100%; height:100px; margin: 20px 0;">
                <path d="M0,50 L120,50 L140,25 L160,75 L180,15 L200,65 L220,50 L400,50" fill="none" stroke="#10b981" stroke-width="4" stroke-linecap="round"/>
            </svg>
            <div style="font-size:18px; color:#94a3b8; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 14px;">
                Heartbeat: <span style="color:#10b981; font-weight:700;">Every 30s Active</span>
            </div>
        </div>
    </div>
    ''',

    # 5: תקוע 17 יום. נראה ירוק.
    5: '''
    <div class="header-badge" style="border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.12); color: #f87171;">
        <div class="pulse-dot-red"></div>
        <span>THE FALSE-GREEN DISASTER · HUNG IN MEMORY</span>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1.3fr; gap: 40px; width: 1560px;">
        <div style="background: rgba(18,24,38,0.85); border: 1.5px solid rgba(16,185,129,0.4); border-radius: 24px; padding: 40px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
            <div style="font-size: 20px; color: #94a3b8; font-weight: 700; margin-bottom: 24px; letter-spacing: 1px;">WHAT TRADITIONAL CONSOLE SHOWS:</div>
            <div style="background: rgba(16,185,129,0.2); border: 2px solid #10b981; border-radius: 24px; padding: 24px 44px; display: flex; align-items: center; gap: 20px; box-shadow: 0 0 40px rgba(16,185,129,0.3);">
                <div style="width: 48px; height: 48px; border-radius: 50%; background: #10b981; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 900; color: #000;">✓</div>
                <div style="font-size: 42px; font-weight: 900; color: #34d399;">RUNNING</div>
            </div>
            <div style="margin-top: 28px; font-size: 20px; color: #94a3b8; text-align: center;">Status Flag: OK (No Exception Raised)</div>
        </div>
        <div style="background: rgba(45,15,20,0.92); border: 2px solid #ef4444; border-radius: 24px; padding: 40px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 0 60px rgba(239,68,68,0.4);">
            <div style="font-size: 20px; color: #fca5a5; font-weight: 700; margin-bottom: 16px; letter-spacing: 1px;">REAL DURATION IN MEMORY:</div>
            <div style="font-size: 78px; font-weight: 900; color: #ef4444; line-height: 1; letter-spacing: -2px; text-shadow: 0 0 30px rgba(239,68,68,0.8);">
                17d 19h 42m
            </div>
            <div style="margin-top: 24px; font-size: 22px; color: #fff; display: flex; gap: 20px; align-items: center;">
                <span style="color:#94a3b8;">Normal Run Time:</span>
                <span style="font-weight: 800; color: #38bdf8;">01m 38s</span>
                <span style="background: #ef4444; color: #fff; padding: 4px 12px; border-radius: 8px; font-size: 16px; font-weight: 800;">+1,550,000%</span>
            </div>
            <div style="margin-top: 16px; font-size: 18px; color: #fca5a5;">
                ⚠️ Process zombie locked VM thread silently for 17 days.
            </div>
        </div>
    </div>
    ''',

    # 6: תצוגה חכמה אחת. בזמן אמת.
    6: '''
    <div class="header-badge" style="border-color: rgba(56,189,248,0.5); background: rgba(56,189,248,0.15); color: #38bdf8;">
        <div class="pulse-dot"></div>
        <span>VALOR AUTOMATION CONTROL CENTER · UNIFIED COCKPIT</span>
    </div>
    <div style="width: 1560px; background: rgba(18,24,38,0.92); border: 2px solid rgba(123,167,208,0.4); border-radius: 26px; padding: 36px 50px; box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 40px rgba(123,167,208,0.25);">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px;">
            <div style="background: rgba(255,255,255,0.03); border: 1.5px solid rgba(56,189,248,0.3); border-radius: 20px; padding: 28px; text-align: center;">
                <div style="font-size: 64px; font-weight: 900; color: #38bdf8; line-height: 1;">99.4%</div>
                <div style="font-size: 22px; font-weight: 700; color: #fff; margin-top: 12px;">Fleet Health Score</div>
                <div style="font-size: 16px; color: #94a3b8; margin-top: 4px;">Real-Time Telemetry</div>
            </div>
            <div style="background: rgba(255,255,255,0.03); border: 1.5px solid rgba(16,185,129,0.3); border-radius: 20px; padding: 28px; text-align: center;">
                <div style="font-size: 64px; font-weight: 900; color: #10b981; line-height: 1;">18 / 18</div>
                <div style="font-size: 22px; font-weight: 700; color: #fff; margin-top: 12px;">Robots Synchronized</div>
                <div style="font-size: 16px; color: #94a3b8; margin-top: 4px;">Zero Unlinked Units</div>
            </div>
            <div style="background: rgba(255,255,255,0.03); border: 1.5px solid rgba(123,167,208,0.3); border-radius: 20px; padding: 28px; text-align: center;">
                <div style="font-size: 64px; font-weight: 900; color: #7BA7D0; line-height: 1;">0</div>
                <div style="font-size: 22px; font-weight: 700; color: #fff; margin-top: 12px;">Silent Breakdowns</div>
                <div style="font-size: 16px; color: #94a3b8; margin-top: 4px;">Proactive Discovery</div>
            </div>
        </div>
        <div style="margin-top: 28px; background: rgba(0,0,0,0.4); border-radius: 14px; padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255,255,255,0.08);">
            <div style="display:flex; align-items:center; gap:16px;">
                <div class="pulse-dot"></div>
                <span style="font-size: 20px; font-weight: 700; color: #e2e8f0;">LIVE TELEMETRY STREAM</span>
            </div>
            <div style="font-size: 18px; color: #7BA7D0; font-weight: 600;">Latency: 4ms · Protocol: UiPath Orchestrator Native · On-Prem Security</div>
        </div>
    </div>
    ''',

    # 7: כל תהליך. כל ריצה. כל מגמה.
    7: '''
    <div class="header-badge">
        <div class="pulse-dot"></div>
        <span>DEEP EXECUTION ANALYTICS & 90-DAY TRENDS</span>
    </div>
    <div style="width: 1560px; background: rgba(18,24,38,0.9); border: 1.5px solid rgba(123,167,208,0.3); border-radius: 24px; padding: 32px; box-shadow: 0 24px 50px rgba(0,0,0,0.6);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px;">
            <span style="font-size:24px; font-weight:700; color:#fff;">90-Day Execution Activity Heatmap (21,876 Total Runs)</span>
            <span style="background:rgba(56,189,248,0.15); color:#38bdf8; padding:6px 16px; border-radius:10px; font-size:16px; font-weight:700;">⏱️ 10-Second Diagnostic</span>
        </div>
        <div style="display: grid; grid-template-rows: repeat(5, 24px); grid-template-columns: repeat(24, 1fr); gap: 8px;">
            ''' + "".join(f'''<div style="background: {['rgba(123,167,208,0.1)', 'rgba(56,189,248,0.3)', 'rgba(56,189,248,0.6)', '#38bdf8', '#10b981'][(i*7 + i//3)%5]}; border-radius: 4px;"></div>''' for i in range(120)) + '''
        </div>
        <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 20px; font-weight: 700; color: #fff;">Average Run Time Deviation</div>
                <div style="font-size: 16px; color: #94a3b8; margin-top: 4px;">Historical baseline auto-calculated across 90 days</div>
            </div>
            <div style="display:flex; gap:36px; align-items:center;">
                <div style="text-align:right;">
                    <span style="font-size:32px; font-weight:900; color:#10b981;">-38%</span>
                    <span style="font-size:16px; color:#94a3b8; display:block;">Run Duration</span>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:32px; font-weight:900; color:#38bdf8;">100%</span>
                    <span style="font-size:16px; color:#94a3b8; display:block;">Visibility</span>
                </div>
            </div>
        </div>
    </div>
    ''',

    # 8: הריצה הבאה? המערכת כבר יודעת.
    8: '''
    <div class="header-badge" style="border-color: rgba(56,189,248,0.5); background: rgba(56,189,248,0.15); color: #38bdf8;">
        <div class="pulse-dot"></div>
        <span>SMART SCHEDULING · PREDICTIVE CADENCE RECOGNITION</span>
    </div>
    <div style="width: 1560px; background: rgba(18,24,38,0.9); border: 2px solid rgba(123,167,208,0.4); border-radius: 24px; padding: 40px; box-shadow: 0 25px 60px rgba(0,0,0,0.7);">
        <div style="display: flex; justify-content: space-between; align-items: center; position: relative;">
            <div style="text-align: center; width: 220px;">
                <div style="background: rgba(16,185,129,0.15); border: 1.5px solid #10b981; border-radius: 18px; padding: 20px;">
                    <div style="font-size: 26px; font-weight: 800; color: #34d399;">08:00 AM</div>
                    <div style="font-size: 16px; color: #94a3b8; margin-top: 6px;">COMPLETED</div>
                </div>
            </div>
            <div style="height: 3px; flex-grow: 1; background: #10b981;"></div>
            <div style="text-align: center; width: 220px;">
                <div style="background: rgba(16,185,129,0.15); border: 1.5px solid #10b981; border-radius: 18px; padding: 20px;">
                    <div style="font-size: 26px; font-weight: 800; color: #34d399;">10:00 AM</div>
                    <div style="font-size: 16px; color: #94a3b8; margin-top: 6px;">COMPLETED</div>
                </div>
            </div>
            <div style="height: 3px; flex-grow: 1; background: #10b981;"></div>
            <div style="text-align: center; width: 220px;">
                <div style="background: rgba(16,185,129,0.15); border: 1.5px solid #10b981; border-radius: 18px; padding: 20px;">
                    <div style="font-size: 26px; font-weight: 800; color: #34d399;">12:00 PM</div>
                    <div style="font-size: 16px; color: #94a3b8; margin-top: 6px;">COMPLETED</div>
                </div>
            </div>
            <div style="height: 3px; flex-grow: 1; background: dashed 2px #38bdf8;"></div>
            <div style="text-align: center; width: 340px;">
                <div style="background: radial-gradient(circle, rgba(56,189,248,0.25) 0%, rgba(18,24,38,0.9) 100%); border: 2.5px solid #38bdf8; border-radius: 20px; padding: 24px; box-shadow: 0 0 50px rgba(56,189,248,0.5);">
                    <div style="font-size: 16px; font-weight: 800; color: #38bdf8; letter-spacing: 1.5px;">PREDICTED NEXT RUN</div>
                    <div style="font-size: 38px; font-weight: 900; color: #fff; margin-top: 6px;">14:00 PM</div>
                    <div style="font-size: 15px; color: #7BA7D0; margin-top: 4px;">Confidence: 99.4% · Window: ±2m</div>
                </div>
            </div>
        </div>
        <div style="margin-top: 30px; text-align: center; font-size: 20px; color: #cbd5e1;">
            No manual rules required. The system learns process rhythms autonomously.
        </div>
    </div>
    ''',

    # 9: עומסים, התנגשויות, מקום פנוי.
    9: '''
    <div class="header-badge" style="border-color: rgba(245,158,11,0.4); background: rgba(245,158,11,0.12); color: #fbbf24;">
        <div class="pulse-dot-amber"></div>
        <span>MACHINE LOAD BALANCING & FREE CAPACITY DISCOVERY</span>
    </div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; width: 1560px;">
        <div style="background: rgba(45,15,20,0.9); border: 2px solid #ef4444; border-radius: 24px; padding: 32px; box-shadow: 0 0 40px rgba(239,68,68,0.3);">
            <div style="font-size: 24px; font-weight: 700; color: #fff;">Server-01 (Prod)</div>
            <div style="font-size: 16px; color: #fca5a5; margin-top: 4px;">6 Robots Assigned</div>
            <div style="margin: 24px 0 16px 0; height: 26px; background: rgba(255,255,255,0.1); border-radius: 13px; overflow: hidden;">
                <div style="width: 92%; height: 100%; background: linear-gradient(90deg, #f59e0b, #ef4444); border-radius: 13px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size: 32px; font-weight: 900; color: #ef4444;">92% LOAD</span>
                <span style="background: #ef4444; color: #fff; padding: 4px 12px; border-radius: 8px; font-weight: 800; font-size: 14px;">OVERLOAD</span>
            </div>
        </div>
        <div style="background: rgba(18,24,38,0.85); border: 1.5px solid rgba(123,167,208,0.3); border-radius: 24px; padding: 32px; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
            <div style="font-size: 24px; font-weight: 700; color: #fff;">Server-02 (Finance)</div>
            <div style="font-size: 16px; color: #94a3b8; margin-top: 4px;">4 Robots Assigned</div>
            <div style="margin: 24px 0 16px 0; height: 26px; background: rgba(255,255,255,0.1); border-radius: 13px; overflow: hidden;">
                <div style="width: 64%; height: 100%; background: linear-gradient(90deg, #38bdf8, #3b82f6); border-radius: 13px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size: 32px; font-weight: 900; color: #38bdf8;">64% LOAD</span>
                <span style="background: rgba(56,189,248,0.2); color: #38bdf8; padding: 4px 12px; border-radius: 8px; font-weight: 800; font-size: 14px;">OPTIMAL</span>
            </div>
        </div>
        <div style="background: rgba(18,35,30,0.9); border: 2px solid #10b981; border-radius: 24px; padding: 32px; box-shadow: 0 0 40px rgba(16,185,129,0.3);">
            <div style="font-size: 24px; font-weight: 700; color: #fff;">Server-03 (Batch)</div>
            <div style="font-size: 16px; color: #6ee7b7; margin-top: 4px;">1 Robot Assigned</div>
            <div style="margin: 24px 0 16px 0; height: 26px; background: rgba(255,255,255,0.1); border-radius: 13px; overflow: hidden;">
                <div style="width: 18%; height: 100%; background: #10b981; border-radius: 13px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size: 32px; font-weight: 900; color: #34d399;">82% FREE</span>
                <span style="background: #10b981; color: #000; padding: 4px 12px; border-radius: 8px; font-weight: 800; font-size: 14px;">AVAILABLE</span>
            </div>
        </div>
    </div>
    ''',

    # 10: התראה תוך 5 דקות. בלי רעש.
    10: '''
    <div class="header-badge" style="border-color: rgba(56,189,248,0.5); background: rgba(56,189,248,0.15); color: #38bdf8;">
        <div class="pulse-dot"></div>
        <span>PROACTIVE ALERT DISPATCH · 5-MINUTE SLA</span>
    </div>
    <div style="width: 1200px; background: rgba(18,24,38,0.95); border: 2px solid rgba(56,189,248,0.5); border-radius: 26px; padding: 40px 48px; box-shadow: 0 30px 70px rgba(0,0,0,0.8), 0 0 50px rgba(56,189,248,0.3);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; align-items:center; gap:16px;">
                <span style="background:#ef4444; color:#fff; padding:6px 16px; border-radius:10px; font-size:16px; font-weight:800;">HIGH PRIORITY</span>
                <span style="font-size:24px; font-weight:700; color:#fff;">Process Anomaly Detected</span>
            </div>
            <div style="display:flex; align-items:center; gap:12px; background:rgba(56,189,248,0.15); border:1px solid #38bdf8; padding:8px 20px; border-radius:14px;">
                <span style="font-size:16px; color:#94a3b8;">DISPATCH TIME:</span>
                <span style="font-size:28px; font-weight:900; color:#38bdf8;">4:58</span>
            </div>
        </div>
        <div style="margin: 28px 0; padding: 24px; background: rgba(0,0,0,0.4); border-radius: 16px; border: 1px solid rgba(255,255,255,0.08);">
            <div style="font-size: 22px; font-weight: 700; color: #e2e8f0;">Invoice Extraction Bot #4 · Host: VM-Finance-02</div>
            <div style="font-size: 18px; color: #fca5a5; margin-top: 8px;">Scheduled cadence at 14:00 did not initialize within 3m tolerance threshold.</div>
            <div style="font-size: 16px; color: #34d399; margin-top: 8px;">✓ Alert dispatched 45 minutes before business impact. Zero alert noise.</div>
        </div>
        <div style="display:flex; gap:20px; justify-content:flex-end;">
            <button style="background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; padding:12px 28px; border-radius:12px; font-size:18px; font-weight:700;">⏸️ Snooze (20m)</button>
            <button style="background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; padding:12px 28px; border-radius:12px; font-size:18px; font-weight:700;">🔇 Mute Channel</button>
            <button style="background:#38bdf8; border:none; color:#000; padding:12px 32px; border-radius:12px; font-size:18px; font-weight:800;">⚡ Re-Route Robot</button>
        </div>
    </div>
    '''
}
