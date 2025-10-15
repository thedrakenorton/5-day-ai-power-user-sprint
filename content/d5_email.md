---
id: d5
position: 5
subject: "Day 5 — Voice, polish & publish plan"
preheader: "Lock your voice, tighten copy, add meta/OG, and generate a simple publish plan."
send_offset_days: 4
send_time: "09:00"
timezone: "America/New_York"
video_url: "{{VIDEO_D5_URL}}"
---

# Day 5 — Refine: Voice DNA + Polish + Publish Plan (15–20 min)

**TL;DR**
- Build `voice_dna.md` (traits, do/don’t, stems, red flags).
- Rewrite with small diffs → `copy_final.md`.
- Add meta tags to `page.html`; create `site_meta.json` + `publish_plan.md`.

---

## 1) Materials (copy‑paste prompt)

```
MINE — Gather 2–3 short writing samples (or name 1–2 public voices to blend).
Ask what feels “off” (too generic, weak verbs, over-explains).
List 3 phrases I’d say; 3 I’d never say.

CRAFT — Create voice_dna.md:
• 8–12 traits • Do/Don’t • 5 sentence stems • 3 red flags
Then rewrite copy section-by-section with short diffs → produce copy_final.md.

REFINE — Add <title>, <meta name="description">, and basic OG tags to page.html.
Create site_meta.json (title, description, og_title, accent).
Create publish_plan.md with steps for Notion→Super and GitHub Pages + a 1-sentence social caption.
Paste changed files.
```

---

## 2) Meta + OG cheat sheet

Add inside `<head>` of `page.html`:
```html
<title>Your One‑Line Promise</title>
<meta name="description" content="Short, plain English description for search/social.">
<meta property="og:title" content="Your One‑Line Promise">
<meta property="og:description" content="Short, plain English description for social.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://example.com">
<meta property="og:image" content="https://example.com/og.jpg">
```

**site_meta.json example**
```json
{
  "title": "Your One‑Line Promise",
  "description": "Short, plain English description.",
  "og_title": "Your One‑Line Promise",
  "accent": "neutral"
}
```

**publish_plan.md outline**
```
- Option A: Super (Notion) — Export/port sections, wire custom domain, test on mobile.
- Option B: GitHub Pages — Create repo, push page.html, enable Pages, set custom domain.
- Social caption: “Shipped my one‑page site today. Plain-spoken promise + one clear CTA. {your link}”
```

---

## Acceptance

- `voice_dna.md`, `copy_final.md`, updated `page.html` (with meta/OG), plus `site_meta.json` and `publish_plan.md` saved.

**Reply keyword:** `LIVE`
