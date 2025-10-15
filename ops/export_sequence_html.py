from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    build_dir = root / ".build"
    emails_path = build_dir / "course_emails.json"
    if not emails_path.exists():
        raise SystemExit("Missing .build/course_emails.json. Run render_emails.py first.")

    emails: List[Dict[str, Any]] = json.loads(emails_path.read_text(encoding="utf-8"))
    emails_sorted = sorted(emails, key=lambda e: int(e.get("position", 0)))

    export_dir = build_dir / "export"
    export_dir.mkdir(parents=True, exist_ok=True)

    guide_md_lines: List[str] = []
    guide_md_lines.append("# Kit UI Paste Guide — AI Power User Sprint\n")
    guide_md_lines.append("Paste each Subject + HTML into the Sequence emails (positions 1–5).\n")
    guide_md_lines.append("Time: 09:00 America/New_York. Offsets: 0,1,2,3,4 days.\n\n")

    for e in emails_sorted:
        pos = int(e.get("position", 0))
        subject = str(e.get("subject", "")).strip()
        preheader = str(e.get("preheader", "")).strip()
        html = str(e.get("html", ""))

        out_html = export_dir / f"day{pos}.html"
        out_html.write_text(html, encoding="utf-8")

        guide_md_lines.append(f"## Day {pos}\n")
        guide_md_lines.append(f"Subject: {subject}\n\n")
        guide_md_lines.append(f"Preheader (hidden in HTML): {preheader}\n\n")
        guide_md_lines.append(f"File: {out_html.as_posix()}\n\n")
        guide_md_lines.append("HTML (copy all):\n")
        guide_md_lines.append("```html")
        guide_md_lines.append(html)
        guide_md_lines.append("``""\n")

    guide_path = export_dir / "sequence_paste_guide.md"
    guide_path.write_text("\n".join(guide_md_lines), encoding="utf-8")

    print("[export] Wrote:")
    for e in sorted(export_dir.glob("*.html")):
        print(" -", e)
    print(" -", guide_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

