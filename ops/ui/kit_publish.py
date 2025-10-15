from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


DEFAULT_BASE_URL = os.getenv("KIT_APP_BASE", "https://app.kit.com")


async def ensure_logged_in(context, base_url: str) -> None:
    page = await context.new_page()
    await page.goto(base_url, wait_until="domcontentloaded")
    # Heuristic: presence of navigation bar or user avatar indicates logged in
    # If redirected to login, abort to let the user refresh the storage state
    try:
        await page.wait_for_selector("text=Broadcasts", timeout=5000)
    except PlaywrightTimeout:
        raise RuntimeError("Not logged in. Run kit_login.py to capture a session.")
    await page.close()


async def goto(page, url: str):
    await page.goto(url, wait_until="networkidle")


async def ensure_form(page, base_url: str, name: str, redirect_url: str | None) -> None:
    # Best-effort navigation: Forms index → New Form → Inline → Name → Save → Settings → Redirect
    await goto(page, f"{base_url}/forms")
    # New Form button text can vary; try common variants
    for text in ["New form", "Create new", "Create form", "Create"]:
        try:
            await page.get_by_text(text, exact=False).first.click(timeout=2000)
            break
        except PlaywrightTimeout:
            continue
    # Select Inline if prompted
    try:
        await page.get_by_text("Inline", exact=False).first.click(timeout=2000)
    except PlaywrightTimeout:
        pass
    # Name field
    for label in ["Name", "Form name", "Title"]:
        try:
            await page.get_by_label(label).fill(name, timeout=2000)
            break
        except PlaywrightTimeout:
            continue
    # Save
    for text in ["Save", "Create", "Done"]:
        try:
            await page.get_by_role("button", name=text).click(timeout=2000)
            break
        except PlaywrightTimeout:
            continue
    # Redirect URL (optional)
    if redirect_url:
        for tab in ["Settings", "General", "Options"]:
            try:
                await page.get_by_text(tab, exact=False).click(timeout=2000)
                break
            except PlaywrightTimeout:
                continue
        for label in ["Redirect", "Success redirect", "Success URL"]:
            try:
                await page.get_by_label(label).fill(redirect_url, timeout=2000)
                # Save if needed
                await page.get_by_role("button", name="Save").click(timeout=2000)
                break
            except PlaywrightTimeout:
                continue


async def ensure_sequence(page, base_url: str, name: str) -> None:
    await goto(page, f"{base_url}/sequences")
    for text in ["New sequence", "Create sequence", "New", "Create"]:
        try:
            await page.get_by_text(text, exact=False).first.click(timeout=2000)
            break
        except PlaywrightTimeout:
            continue
    # Name
    for label in ["Name", "Sequence name", "Title"]:
        try:
            await page.get_by_label(label).fill(name, timeout=2000)
            break
        except PlaywrightTimeout:
            continue
    # Save
    for text in ["Save", "Create", "Done"]:
        try:
            await page.get_by_role("button", name=text).click(timeout=2000)
            break
        except PlaywrightTimeout:
            continue


async def paste_email_into_sequence(page, base_url: str, seq_name: str, position: int, subject: str, html: str,
                                    offset_days: int, send_time: str) -> None:
    await goto(page, f"{base_url}/sequences")
    await page.get_by_text(seq_name, exact=False).first.click()
    # Ensure there are enough emails
    for _ in range(position):
        try:
            await page.get_by_role("button", name="Add email").click(timeout=1000)
        except PlaywrightTimeout:
            break
    # Select the email by position (left list usually labeled with numbers)
    await page.get_by_text(str(position), exact=True).first.click()
    # Subject
    for label in ["Subject", "Email subject"]:
        try:
            await page.get_by_label(label).fill(subject, timeout=2000)
            break
        except PlaywrightTimeout:
            continue
    # Switch editor to HTML mode if needed
    try:
        await page.get_by_role("button", name="HTML").click(timeout=1000)
    except PlaywrightTimeout:
        pass
    # Body
    # Try a generic contenteditable region or textarea
    try:
        await page.locator('[contenteditable="true"]').first.fill(html)
    except Exception:
        await page.get_by_role("textbox").first.fill(html)
    # Schedule: offset days and time (heuristic)
    for label in ["Days to send", "Send after", "Delay (days)"]:
        try:
            await page.get_by_label(label).fill(str(offset_days), timeout=1000)
            break
        except PlaywrightTimeout:
            continue
    for label in ["Send time", "Time", "Scheduled time"]:
        try:
            await page.get_by_label(label).fill(send_time, timeout=1000)
            break
        except PlaywrightTimeout:
            continue
    # Save
    for text in ["Save", "Save changes", "Publish", "Done"]:
        try:
            await page.get_by_role("button", name=text).click(timeout=1000)
            break
        except PlaywrightTimeout:
            continue


async def run(base_url: str, state_path: Path, emails: List[Dict[str, Any]],
              form_name: str | None, redirect_url: str | None, seq_name: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=str(state_path))
        await ensure_logged_in(context, base_url)
        page = await context.new_page()

        if form_name:
            await ensure_form(page, base_url, form_name, redirect_url)

        await ensure_sequence(page, base_url, seq_name)

        # Paste emails in order
        for e in sorted(emails, key=lambda x: int(x.get("position", 0))):
            await paste_email_into_sequence(
                page,
                base_url,
                seq_name,
                int(e.get("position", 0)),
                str(e.get("subject", "")),
                str(e.get("html", "")),
                int(e.get("send_offset_days", 0)),
                str(e.get("send_time", "09:00")),
            )

        print("[kit-ui] Sequence populated. Review and publish as needed.")
        await browser.close()


async def main() -> int:
    parser = argparse.ArgumentParser(description="Populate Kit sequence via UI automation using Playwright.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--state", default=str(Path(__file__).resolve().parents[1] / ".build" / "kit_storage_state.json"))
    parser.add_argument("--emails-json", default=str(Path(__file__).resolve().parents[1] / ".build" / "course_emails.json"))
    parser.add_argument("--form-name", default="AI Power User Sprint — Opt-in")
    parser.add_argument("--form-redirect", default="https://thedrakenorton.com/thanks")
    parser.add_argument("--sequence-name", default="AI Power User Sprint (5-day) — v1")
    args = parser.parse_args()

    state_path = Path(args.state)
    emails_path = Path(args.emails_json)
    if not state_path.exists():
        raise SystemExit("Missing storage state. Run kit_login.py first.")
    if not emails_path.exists():
        raise SystemExit("Missing .build/course_emails.json. Run render_emails.py first.")

    emails: List[Dict[str, Any]] = json.loads(emails_path.read_text(encoding="utf-8"))

    await run(
        args.base_url,
        state_path,
        emails,
        args.form_name,
        args.form_redirect,
        args.sequence_name,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

