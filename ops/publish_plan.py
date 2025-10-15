from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


TAG_NAME = "ai_power_user_sprint"
FORM_NAME = "AI Power User Sprint — Opt-in"
SEQUENCE_NAME = "AI Power User Sprint (5-day) — v1"
SEQUENCE_SLUG = "ai-power-user-sprint-5d-v1"
TIMEZONE = "America/New_York"
DEFAULT_SEND_TIME = "09:00"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    build_dir = root / ".build"
    emails_path = build_dir / "course_emails.json"
    if not emails_path.exists():
        raise SystemExit(f"Missing build artifact: {emails_path}")

    emails: List[Dict[str, Any]] = json.loads(emails_path.read_text(encoding="utf-8"))

    plan = {
        "actions": [
            {"tool": "kit.tag.ensure", "params": {"name": TAG_NAME}},
            {
                "tool": "kit.form.ensure",
                "params": {
                    "name": FORM_NAME,
                    "type": "inline",
                    "success_redirect_url": "https://thedrakenorton.com/thanks",
                    "dry_run": True,
                },
            },
            {
                "tool": "kit.sequence.upsert",
                "params": {
                    "name": SEQUENCE_NAME,
                    "slug": SEQUENCE_SLUG,
                    "timezone": TIMEZONE,
                    "default_send_time": DEFAULT_SEND_TIME,
                    "dry_run": True,
                },
            },
            {
                "tool": "kit.sequence.ensure_emails",
                "params": {
                    "sequence_id": "<from upsert>",
                    "emails": emails,
                    "dry_run": True,
                },
            },
            {
                "tool": "kit.automation.ensure",
                "params": {
                    "form_id": "<from form>",
                    "tag_id": "<from tag>",
                    "sequence_id": "<from upsert>",
                    "dry_run": True,
                },
            },
        ]
    }

    out_path = build_dir / "publish_plan.json"
    out_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[plan] Wrote:", out_path)
    print("Actions:")
    for action in plan["actions"]:
        tool = action["tool"]
        print(" -", tool)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

