---
id: d4
position: 4
subject: "Day 4 — Build your page (mobile‑first)"
preheader: "Render the copy into clean HTML + one small flourish. Save page.html."
send_offset_days: 3
send_time: "09:00"
timezone: "America/New_York"
video_url: "{{VIDEO_D4_URL}}"
---

# Day 4 — Build: Generate the Working Page (15–20 min)

**TL;DR**
- Ask 5 setup questions (vibe, adjectives, CTA target, image plan, flourish).
- Generate **semantic HTML + minimal CSS** from your copy.
- Add one tiny JS flourish. Save `page.html`.

---

## 1) Materials (copy‑paste prompt)

```
MINE — Ask 5 setup Qs:
1) Accent color vibe (calm | bold | neutral)
2) Brand adjectives (pick 2): minimal, friendly, precise, energetic, classic, futuristic
3) CTA target (email or link)
4) Profile image plan (upload or skip)
5) Tiny flourish (copy-email button | smooth scroll | “last updated” timestamp)

CRAFT — Generate mobile-first page.html from copy_full.md:
• Header (H1, subhead, CTA wired)
• “What this looks like” (3 bullets)
• “Proof” (1–2 specifics)
• Footer with current year
• Add the chosen tiny JS flourish

REFINE — Do a mobile pass (spacing, headings, tap targets).
Paste full page.html.
```

---

## 2) Minimal starter you can request if you get stuck

```html
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Your One‑Line Promise</title>
<meta name="description" content="Short, plain English description.">
<style>
  body {background:#0a0a0a; color:#eaeaea; font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial; margin:0}
  .wrap {max-width:720px; margin:0 auto; padding:24px}
  h1 {font-size:28px; line-height:1.2; margin:0 0 8px}
  p,li {font-size:16px; line-height:1.6}
  a {color:#6ee7ff; text-decoration:none}
  .btn {display:inline-block; padding:10px 14px; background:#1f2937; color:#fff; border-radius:8px; margin-top:12px}
  section {margin:24px 0}
</style>
<body>
  <div class="wrap">
    <header>
      <h1>Your One‑Line Promise</h1>
      <p>A short subhead that adds a payoff.</p>
      <a class="btn" href="#cta">Request a fit check</a>
    </header>
    <section>
      <h2>What this looks like</h2>
      <ul>
        <li>Outcome bullet</li>
        <li>Concrete artifact</li>
        <li>Risk removed</li>
      </ul>
    </section>
    <section>
      <h2>Proof</h2>
      <p>One specific line with a measurable result or artifact link.</p>
    </section>
    <footer>
      <p id="cta">© <span id="year"></span> Your Name</p>
    </footer>
  </div>
  <script>document.getElementById('year').textContent = new Date().getFullYear()</script>
</body>
</html>
```

---

## Acceptance

- `page.html` loads cleanly, CTA wired, tiny JS flourish present, headings readable on mobile.

**Reply keyword:** `LINK`
