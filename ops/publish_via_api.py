from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import requests

import sys
from dotenv import load_dotenv


def _add_workspace_to_path() -> None:
    # Ensure workspace root (which contains kit_client.py) is importable
    this = Path(__file__).resolve()
    workspace_root = this.parents[2]
    if str(workspace_root) not in sys.path:
        sys.path.insert(0, str(workspace_root))
    # Load .env from workspace for Kit credentials
    load_dotenv(dotenv_path=workspace_root / ".env")


_add_workspace_to_path()

from kit_client import KitAPI  # noqa: E402


TAG_NAME = "ai_power_user_sprint"
FORM_NAME = "AI Power User Sprint — Opt-in"
SEQUENCE_NAME = "AI Power User Sprint (5-day) — v1"


def ensure_tag(api: KitAPI, name: str) -> str | int:
    tags = api.list_tags()
    for t in tags.get("items") or tags.get("tags") or []:
        if str(t.get("name", "")).strip().lower() == name.strip().lower():
            return t.get("id")
    created = api.create_tag(name=name)
    return (created.get("tag") or {}).get("id") or created.get("id")


def find_form(api: KitAPI, name: str) -> str | int | None:
    forms = api.list_forms()
    for f in forms.get("items") or forms.get("forms") or []:
        if str(f.get("name", "")).strip().lower() == name.strip().lower():
            return f.get("id")
    return None


def find_sequence(api: KitAPI, name: str) -> str | int | None:
    seqs = api.list_sequences()
    for s in seqs.get("items") or seqs.get("sequences") or []:
        if str(s.get("name", "")).strip().lower() == name.strip().lower():
            return s.get("id")
    return None


def create_broadcast_drafts(api: KitAPI, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for e in emails:
        subject = e.get("subject")
        html = e.get("html")
        preheader = e.get("preheader")
        payload = {
            "subject": subject,
            "content": html,
            "description": f"Course draft: {SEQUENCE_NAME} d{e.get('position')}",
            "public": False,
            "preview_text": preheader,
        }
        try:
            created = api.create_broadcast(**payload)
            bid = (created.get("broadcast") or {}).get("id") or created.get("id")
            results.append({"subject": subject, "broadcast_id": bid})
        except requests.HTTPError as exc:  # type: ignore[attr-defined]
            results.append({"subject": subject, "error": getattr(exc.response, "text", str(exc))})
    return results


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    emails_path = root / ".build" / "course_emails.json"
    if not emails_path.exists():
        raise SystemExit(f"Missing build artifact: {emails_path}")
    emails = json.loads(emails_path.read_text(encoding="utf-8"))

    api = KitAPI.from_env()

    who = api.get_current_account()
    print(f"[kit] Account: {who.get('account', {}).get('name')} ({who.get('account', {}).get('id')})")

    tag_id = ensure_tag(api, TAG_NAME)
    print(f"[kit] Tag ensured: {TAG_NAME} -> {tag_id}")

    form_id = find_form(api, FORM_NAME)
    if form_id:
        print(f"[kit] Form present: {FORM_NAME} -> {form_id}")
    else:
        print(f"[kit] Form missing (create in UI): {FORM_NAME}")

    seq_id = find_sequence(api, SEQUENCE_NAME)
    if seq_id:
        print(f"[kit] Sequence present: {SEQUENCE_NAME} -> {seq_id}")
    else:
        print(f"[kit] Sequence missing (cannot create via public API): {SEQUENCE_NAME}")

    print("[kit] Creating 5 draft broadcasts for review/copy…")
    drafts = create_broadcast_drafts(api, emails)
    for d in drafts:
        if "broadcast_id" in d:
            print(f"  - Draft created: {d['subject']} -> {d['broadcast_id']}")
        else:
            print(f"  - Draft failed: {d['subject']} :: {d.get('error')}")

    # Write a state file for traceability
    state_path = root / ".build" / "course_state.json"
    state = {
        "account": who.get("account"),
        "tag": {"name": TAG_NAME, "id": tag_id},
        "form": {"name": FORM_NAME, "id": form_id},
        "sequence": {"name": SEQUENCE_NAME, "id": seq_id},
        "broadcast_drafts": drafts,
    }
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[state] Wrote: {state_path}")

    print("\nNext steps:\n- If the sequence is missing, create it in Kit UI, then paste the HTML from the drafts into sequence emails (positions 1–5).\n- Wire the form submit -> add tag -> subscribe to sequence automation in UI (API not available).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
