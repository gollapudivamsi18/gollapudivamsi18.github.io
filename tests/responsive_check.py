"""Responsive and behaviour check for the portfolio pages (Playwright + Chrome).

  python3 tests/responsive_check.py            # serves the repo on a local port
Checks at 320, 375, 390, 768, 1024, 1440 and 1920 px:
  - no horizontal page overflow
  - no element wider than the viewport (outside scroll containers)
  - the floating assistant answers, keeps identity, and minimizes
  - the architecture lightbox opens
Screenshots go to tests/screenshots/ (git-ignored).
"""
import asyncio
import functools
import http.server
import sys
import threading
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
WIDTHS = [320, 375, 390, 768, 1024, 1440, 1920]
PAGES = ["index.html", "projects.html", "resume.html"]
SHOTS = ROOT / "tests" / "screenshots"


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Quiet, directory=str(ROOT))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


OVERFLOW_JS = """() => {
  const vw = document.documentElement.clientWidth;
  const bad = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || getComputedStyle(el).position === 'fixed' || el.closest('.skip, .sr-only')) continue;
    let p = el.parentElement, scroll = false;
    while (p) { const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') { scroll = true; break; } p = p.parentElement; }
    if (!scroll && (r.right > vw + 1 || r.left < -1)) bad.push(el.tagName + '.' + el.className + ' ' + Math.round(r.left) + '-' + Math.round(r.right));
  }
  return { docWidth: document.documentElement.scrollWidth, vw, bad: bad.slice(0, 5) };
}"""


async def main(chrome):
    srv, base = serve()
    SHOTS.mkdir(parents=True, exist_ok=True)
    failures = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=chrome) if chrome else await p.chromium.launch()
        for width in WIDTHS:
            page = await browser.new_page(viewport={"width": width, "height": 900})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            for name in PAGES:
                await page.goto(base + name)
                await page.wait_for_load_state("networkidle")
                res = await page.evaluate(OVERFLOW_JS)
                ok = res["docWidth"] <= res["vw"] and not res["bad"]
                print(f"{width:>5}px {name:<14} {'ok' if ok else 'OVERFLOW'} {'' if ok else res}")
                if not ok:
                    failures.append((width, name, res))
                await page.screenshot(path=str(SHOTS / f"{width}-{name.replace('.html', '')}.png"), full_page=False)
            # Floating assistant (once per width): open, ask, follow up, minimize
            await page.goto(base + "index.html")
            await page.click(".ai-fab")
            await page.wait_for_selector(".ai-panel .msg.bot")
            await page.fill("#ai-input", "What is his notice period?")
            await page.click(".ai-panel button.send")
            await page.fill("#ai-input", "Is he a frontend developer?")
            await page.click(".ai-panel button.send")
            bots = await page.locator(".ai-panel .msg.bot").all_inner_texts()
            if len(bots) < 3 or "15 days" not in bots[1] or not bots[2].startswith("No."):
                failures.append((width, "assistant", bots[-2:]))
                print(f"{width:>5}px assistant FAILED: {bots[-2:]}")
            await page.screenshot(path=str(SHOTS / f"{width}-assistant.png"))
            await page.click('.ai-panel [data-act="min"]')
            if await page.locator(".ai-panel").is_visible():
                failures.append((width, "assistant-minimize", "panel still visible"))
            # Diagram lightbox
            await page.click("#p-aks .card-actions button")
            if not await page.locator("dialog.lightbox[open]").is_visible():
                failures.append((width, "lightbox", "did not open"))
            await page.screenshot(path=str(SHOTS / f"{width}-lightbox.png"))
            await page.keyboard.press("Escape")
            if errors:
                failures.append((width, "js-errors", errors))
                print(f"{width:>5}px JS errors: {errors}")
            await page.close()
        await browser.close()
    srv.shutdown()
    print("\nFAILED" if failures else "\nAll responsive and assistant checks passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    chrome = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(asyncio.run(main(chrome)))
