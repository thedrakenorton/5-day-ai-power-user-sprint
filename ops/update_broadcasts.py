from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

import sys


def _add_workspace_to_path() -> Path:
    this = Path(__file__).resolve()
    workspace_root = this.parents[2]
    if str(workspace_root) not in sys.path:
        sys.path.insert(0, str(workspace_root))
    load_dotenv(dotenv_path=workspace_root / ".env")
    return workspace_root


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    workspace_root = _add_workspace_to_path()
    from kit_client import KitAPI  # local import after sys.path tweak

    emails_path = root / ".build" / "course_emails.json"
    state_path = root / ".build" / "course_state.json"

    if not emails_path.exists() or not state_path.exists():
        raise SystemExit("Missing build/state artifacts. Run render_emails.py and publish_via_api.py first.")

    emails: List[Dict[str, Any]] = json.loads(emails_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    drafts = state.get("broadcast_drafts") or []
    if len(drafts) != len(emails):
        print(f"[warn] Draft count mismatch: drafts={len(drafts)} emails={len(emails)}")

    # Sort both lists by position and update by index
    emails_sorted = sorted(emails, key=lambda e: int(e.get("position", 0)))
    # drafts are in creation order; assume same order; if ids missing, skip

    api = KitAPI.from_env()
    who = api.get_current_account()
    print(f"[kit] Account: {who.get('account', {}).get('name')} ({who.get('account', {}).get('id')})")

    updated = 0
    for idx, e in enumerate(emails_sorted):
        if idx >= len(drafts):
            break
        bid = drafts[idx].get("broadcast_id")
        if not bid:
            print(f"[skip] No broadcast id for idx {idx}")
            continue
        subject = e.get("subject")
        html = e.get("html")
        preheader = e.get("preheader")
        try:
            api.update_broadcast(bid, subject=subject, content=html, preview_text=preheader, public=False, send_at=None)
            print(f"  - Updated broadcast {bid} :: {subject}")
            updated += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  - Failed to update {bid}: {exc}")

    print(f"[done] Updated {updated} broadcasts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

