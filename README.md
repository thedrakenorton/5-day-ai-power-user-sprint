# AI Power User Sprint — 5‑Day Email Course (Handoff Package)

This repo contains everything needed to **instantiate the 5‑day course in Kit (formerly ConvertKit)** and keep it versioned in Git. It’s designed for **Codex CLI** to run non‑interactively and call your **Kit MCP Server** for safe, idempotent actions.

> TL;DR: Edit the video URLs in `content/d*.md`, wire your **Kit MCP server** in `~/.codex/config.toml`, then run the Codex prompts under `ops/codex/prompts/` to publish.

---

## Structure

```
ai_power_user_sprint_course_v1/
├── content/
│   ├── d1_email.md
│   ├── d2_email.md
│   ├── d3_email.md
│   ├── d4_email.md
│   └── d5_email.md
├── ops/
│   ├── mcp/
│   │   └── mcp_contract.json
│   └── codex/
│       ├── config_sample.toml
│       └── prompts/
│           ├── course_init.prompt
│           └── course_publish.prompt
├── templates/
│   └── email/
│       └── course_base.html
└── README.md
```

---

## What Codex will create in Kit (idempotent)

- **Tag**: `ai_power_user_sprint`
- **Form**: “AI Power User Sprint — Opt‑in” (success redirect configurable)
- **Sequence**: “AI Power User Sprint (5‑day) — v1”  
  - 5 emails loaded from `content/d*.md` (subject, preheader, HTML body)
  - Schedule: send **daily at 9:00 AM America/New_York** (adjustable in config)
- **Automation** (if your MCP server exposes it): *Form submit → add Tag → subscribe to Sequence*

If resources exist, Codex updates them; otherwise it creates them. All operations are dry‑run‑first.

---

## Before you run

1) **Install Codex CLI** and sign in with ChatGPT (Plus/Pro/Team/Enterprise).  
2) **Configure MCP** in `~/.codex/config.toml` to point to your Kit MCP server.  
3) **Export API keys** for Kit as env vars (see `ops/codex/config_sample.toml`).  
4) **Edit video URLs** in `content/d*.md` (search for `VIDEO_Dx_URL`).  
5) Optionally tweak send time / timezone in the front‑matter of each email.

> ⚠️ **Safety**: The Codex prompts run a *dry‑run* first and print a diff. You must approve (or switch to full‑auto if you accept the defaults).

---

## One‑liners

**Initialize (parse, validate, render to HTML only):**
```bash
codex exec --prompt-file ops/codex/prompts/course_init.prompt
```

**Publish to Kit (create/update Tag, Form, Sequence + emails, and optional Automation):**
```bash
codex exec --prompt-file ops/codex/prompts/course_publish.prompt
```

> Tip: You can run Codex non‑interactively with `codex exec`. MCP servers are configured in `~/.codex/config.toml` and are shared between the CLI and the IDE extension.

---

## Content model (Markdown → HTML)

Each `content/d*.md` file contains front‑matter and Markdown. Codex will:
1) Parse the YAML front‑matter (subject, preheader, send offset/time, placeholders).  
2) Convert Markdown to HTML (using a minimal renderer) and wrap it with `templates/email/course_base.html`.  
3) Inject Liquid personalization and video links as provided.  
4) Upsert into the Kit Sequence in the correct order.

---

## Placeholders you must fill

- `VIDEO_D1_URL` … `VIDEO_D5_URL` — hosted lesson URLs (YouTube, Loom, or your CDN/HLS).  
- Optionally set `VIDEO_Dx_THUMB` for a custom thumbnail image URL.

> Kit supports Liquid, e.g. `{ subscriber.first_name | default: "friend" }`. We already include safe defaults in the email copy.

---

## Idempotency & dry‑run

- The MCP contract exposes `dry_run: true|false` on write operations.  
- Codex computes a per‑resource **hash** of the desired state and compares against Kit before writing.  
- A local `course_state.json` is written into Codex session storage for traceability.

---

## Deploy notes

- **Timezone**: default `America/New_York`. Adjust in front‑matter.  
- **Deliverability**: emails are mobile‑scannable (short paragraphs, bullets, semantic headings).  
- **Personalization**: simple Liquid first name with safe default.  
- **Unsubscribe**: rely on Kit’s managed footers.

---

## Where to change things later

- Copy tweaks → edit the `content/*.md` files and re‑run `course_publish`.  
- Styling tweaks → edit `templates/email/course_base.html`.  
- Schedule tweaks → adjust `send_offset_days` / `send_time` in front‑matter and republish.

— Last updated: 2025-10-11
