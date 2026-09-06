# Hebrew Video Skill

Turn a screen recording into a finished Hebrew product video: cleaned footage, narration in your own cloned voice, one-line RTL captions synced to the speech, benefit chips, branded title / stats / closing cards. One `project.json`, three scripts, ffmpeg + headless Chrome. No video editor, no cloud renderer.

Built for Claude Code by Guy Cohen. Brand, voice, contacts and footage are all configuration, so the same skill produces videos for any product or client.

---

## למה זה קיים

סרטון מוצר בעברית עם קריינות משובטת נשמע כמו פרויקט של יום. בפועל נפלתי בשמונה מלכודות, ורובן נכשלות בשקט.

| המלכודת | מה קורה | הפתרון בסקיל |
|---|---|---|
| **מסגרת רנדור שמוחקת קבצים** | כלי רנדור פופולרי מחק שלוש פעמים ביום אחד תיקיות שלמות, כולל גיבוי | צינור עצמאי: Chrome headless לשכבות, ffmpeg אחד לכל הסרטון. שום דבר לא נמחק |
| **מודל קול לא נכון** | ב‑ElevenLabs רק `eleven_v3` מדבר עברית. מודלים אחרים מחזירים קובץ תקין שנשמע רובוטי או ג'יבריש | המודל נעול ב‑`project.json` |
| **שיבוט מקצועי** | Professional Voice Clone לא תומך בעברית. הבקשה מאושרת, האימון לא מתחיל לעולם | Instant Clone מ‑4 קטעים של הקלטה נקייה, `reference/lessons.md` מסביר איך |
| **הגייה** | המודל שובר מילים כמו Valor, UiPath, "משני", "פוספס" | איות מנוקד בטקסט המדובר, וטבלת `display` שמראה על המסך את הכתיב הנכון |
| **כתוביות בשתי שורות** | כתובית ארוכה גולשת ומסתירה את המסך | חיתוך לפי זמני התווים, עד 50 תווים, מעדיף פסיקים, לא שובר שמות באנגלית ולא לפני ו' החיבור |
| **פיסוק בצד הלא נכון** | משפט עברי שנגמר במילה באנגלית מקבל נקודה משמאל | כל שכבה עטופה ב‑U+200F משני הצדדים |
| **שם הלקוח על המסך** | שורת הכתובת ושמות תהליכים חושפים לקוח | חיתוך שורת הדפדפן וטשטוש מתוזמן לפי קואורדינטות |
| **שכבות שמסתירות תפריט** | תגית יכולת שנשארת מסתירה את סרגל הכלים של המוצר | תגית מופיעה 4 שניות בדיוק |
| **מילים עם עמימות ניקוד/הטעמה ב-TTS** | מילים כמו "ערכה" נקראות כ-ARAKA או בהטעמה אנגלית במלעיל | החלפה מידית למילה נרדפת ללא עמימות ("חבילה"), שמייצרת הגייה טבעית בטייק ראשון |
| **סנכרון כתוביות רופף או השמטת מילים** | השמטת מילות קישור ("ללכת", "ממני") יוצרת תחושת דיסאוריינטציה | תמלול כתוביות מדויק 100% מילה במילה באמצעות חילוץ זמנים ב-Whisper |
| **עיצוב כתוביות מיושן לסושיאל** | פונט ברירת מחדל נראה משרדי ולא מתאים לרילס | פונט Heebo Black ותגיות הדגשה מעוגלות בצהוב וטורקיז שקופצות בדיוק כשהמילה נאמרת |
| **חריגה מ-60 שניות ברילס/שורטס** | סרטון מעל 60 שניות נחתך או נפסל מלופים של שורטס | בקרת זמנים קפדנית ל-58 עד 59 שניות |
| **רעשי גניחה/נחירות מלאכותיים** | ניסיונות לייצר קולות נחירה או אנחות ב-TTS נשמעים מעוותים | קריינות נקייה ורהוטה על גבי מוזיקת רקע אווירתית ואפקטים קוליים מתוזמנים (UI SFX) |

---

## התקנה

```bash
git clone https://github.com/guycoful/hebrew-video-skill ~/.claude/skills/hebrew-video
```

**דרישות:** `ffmpeg` ו‑`ffprobe` ב‑PATH, Google Chrome מותקן, Python 3.10+, ו‑`ELEVENLABS_API_KEY` בקובץ `~/.config/valor-video/.env` (הנתיב ניתן לשינוי ב‑`project.json`).

---

## שימוש

```bash
# 1. תיקיית פרויקט עם assets/: הקלטת המסך, לוגו לבן על שקוף, תמונת מסקוט (רשות)
# 2. מעתיקים את templates/project.json ועורכים: קריינות, סצנות (שניות במקור), תגיות, כרטיסים, תיבות טשטוש
python ~/.claude/skills/hebrew-video/scripts/clean_footage.py   # חיתוך + טשטוש, כותב פריימים לבדיקה
python ~/.claude/skills/hebrew-video/scripts/vo.py              # קריינות + כתוביות מתוזמנות (רק קטעים שהשתנו)
python ~/.claude/skills/hebrew-video/scripts/qa_vo.py           # תמלול חוזר של כל קטע והשוואה לתסריט
python ~/.claude/skills/hebrew-video/scripts/render.py          # out/<name>.mp4
```

שינוי משפט אחד: עורכים אותו ב‑`narration`, מוחקים את `assets/vo/vo<N>.*`, ומריצים `vo.py` ואז `render.py`. רק הקטע הזה מוקלט מחדש.

הקלטה אמיתית במקום TTS: שמים `assets/vo-real/vo<N>.wav` והסקריפט מעדיף אותה אוטומטית.

---

## מבנה

```
SKILL.md                  ההוראות ל‑Claude Code: כללים, סדר עבודה, מוסכמות כתוביות
templates/project.json    פרויקט מלא לדוגמה (סרטון לקוח של 2:16)
scripts/clean_footage.py  crop + boxblur מתוזמן + scale
scripts/vo.py             ElevenLabs eleven_v3 עם with-timestamps, חיתוך כתוביות לשורה אחת
scripts/qa_vo.py          תמלול חוזר (Scribe) מול התסריט
scripts/render.py         שכבות HTML → PNG ב‑Chrome headless → גרף ffmpeg אחד
reference/lessons.md      יומן התקלות: מה נכשל, למה, ומה עובד
```

---

## רישיון

MIT. אם זה חסך לך יום, ספר לי.
