from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright


DEFAULT_BASE_URL = os.getenv("KIT_APP_BASE", "https://app.kit.com")


async def main() -> int:
    parser = argparse.ArgumentParser(description="Open Kit app for manual login and save storage state.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--state", default=str(Path(__file__).resolve().parents[1] / ".build" / "kit_storage_state.json"))
    args = parser.parse_args()

    state_path = Path(args.state)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(args.base_url, wait_until="load")

        print("\n[kit-login] A browser window opened.\n"
              " - Log in to Kit (including 2FA if prompted).\n"
              " - Wait until you can see your dashboard (or Broadcasts/Forms pages).\n"
              " - Then return to this terminal and press ENTER to save the session.\n")
        try:
            input("Press ENTER to save storage state...")
        except KeyboardInterrupt:
            print("Aborted.")
            await browser.close()
            return 1

        await context.storage_state(path=str(state_path))
        print(f"[kit-login] Saved storage state to {state_path}")
        await browser.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

