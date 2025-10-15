from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class EmailSpec:
    position: int
    subject: str
    preheader: str
    html: str
    send_offset_days: int
    send_time: str


def parse_front_matter(text: str) -> tuple[Dict[str, Any], str]:
    text = text.lstrip("\ufeff")  # strip BOM if present
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        # fallback if end delimiter uses CRLF variations
        m = re.search(r"\n---\r?\n", text)
        if not m:
            return {}, text
        head = text[4:m.start()]  # after initial '---\n'
        body = text[m.end():]
        fm = _parse_simple_yaml(head)
        return fm, body
    head = parts[0][4:]  # skip initial '---\n'
    body = parts[1]
    fm = _parse_simple_yaml(head)
    return fm, body


def _parse_simple_yaml(head: str) -> Dict[str, Any]:
    # Minimal YAML parser for simple key: value lines with quoted values
    fm: Dict[str, Any] = {}
    for line in head.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        # Try to coerce ints where appropriate
        if key in {"position", "send_offset_days"}:
            try:
                fm[key] = int(val)
                continue
            except ValueError:
                pass
        fm[key] = val
    return fm


def markdown_to_html(md_text: str) -> str:
    try:
        import markdown  # type: ignore

        return markdown.markdown(
            md_text,
            extensions=["extra", "sane_lists", "smarty"],  # type: ignore[arg-type]
            output_format="xhtml",
        )
    except Exception:
        # Fallback: wrap as preformatted text
        escaped = (
            md_text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return f"<pre>{escaped}</pre>"


def wrap_template(template: str, subject: str, preheader: str, content_html: str) -> str:
    html = template
    html = html.replace("{{ subject }}", subject)
    html = html.replace("{{ preheader }}", preheader)
    html = html.replace("{{ content }}", content_html)
    return html


def build_emails(root: Path) -> List[EmailSpec]:
    content_dir = root / "content"
    template_path = root / "templates" / "email" / "course_base.html"
    template = template_path.read_text(encoding="utf-8")

    specs: List[EmailSpec] = []
    for md_path in sorted(content_dir.glob("d*_email.md")):
        raw = _read_text_smart(md_path)
        fm, body_md = parse_front_matter(raw)

        # Normalize any single/triple/quad-brace VIDEO token usage to Liquid double braces
        body_md = re.sub(r"\{+VIDEO_D([1-5])_URL\}+", r"{{VIDEO_D\1_URL}}", body_md)

        # Required fields with defaults
        position = int(fm.get("position") or 0)
        subject = str(fm.get("subject") or "")
        preheader = str(fm.get("preheader") or fm.get("preview_text") or "")
        send_offset_days = int(fm.get("send_offset_days") or 0)
        send_time = str(fm.get("send_time") or "09:00")

        body_html = markdown_to_html(body_md)
        full_html = wrap_template(template, subject=subject, preheader=preheader, content_html=body_html)

        specs.append(
            EmailSpec(
                position=position,
                subject=subject,
                preheader=preheader,
                html=full_html,
                send_offset_days=send_offset_days,
                send_time=send_time,
            )
        )

    # Sort by position to ensure order
    specs.sort(key=lambda s: s.position)
    return specs


def main() -> int:
    # Ensure stdout can emit UTF-8 safely on Windows consoles
    try:
        import sys

        sys.stdout.reconfigure(encoding="utf-8", errors="ignore")  # type: ignore[attr-defined]
    except Exception:
        pass
    root = Path(__file__).resolve().parents[1]
    build_dir = root / ".build"
    build_dir.mkdir(parents=True, exist_ok=True)

    emails = build_emails(root)
    out = [
        {
            "position": e.position,
            "subject": e.subject,
            "preheader": e.preheader,
            "html": e.html,
            "send_offset_days": e.send_offset_days,
            "send_time": e.send_time,
        }
        for e in emails
    ]

    out_path = build_dir / "course_emails.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # Print a compact summary to stdout
    print("[build] Wrote:", out_path)
    for e in emails:
        print(f"  - d{e.position}: {e.subject} [{e.send_offset_days}d @ {e.send_time}]")

    return 0


def _read_text_smart(path: Path) -> str:
    """Read text trying UTF-8/UTF-8-sig first, then cp1252 fallback without loss.

    Avoids replacement characters by attempting multiple encodings.
    """
    data = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    # Fallback for Windows-authored files
    try:
        return data.decode("cp1252")
    except UnicodeDecodeError:
        # As a last resort, replace
        return data.decode("utf-8", errors="replace")


if __name__ == "__main__":
    raise SystemExit(main())
