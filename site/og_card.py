"""Draw the image that shows when a link to the site is shared.

    python site/og_card.py

Builds the site to get the current numbers, writes a small HTML card set in
the site's own type and colours, and has Chrome photograph it at 1200 by 630.
The result is site/static/<OG_IMAGE>, the file named in site/content.py.

Run it when the headline numbers change. Give the image a new file name each
time (change OG_IMAGE in site/content.py first): staas.fund tells browsers to
keep a PNG for seven days, so a changed image under an old name is not seen.

This is the one script in the repository that needs something installed:
Google Chrome. Everything else is the standard library.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build as B  # noqa: E402

CHROME = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser",
]

CARD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ width: 1200px; height: 630px; overflow: hidden; }}
  body {{ background: #e7eff0; color: #1c1b19; border-top: 22px solid #0e4a5b;
         font-family: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
         padding: 46px 80px 0; }}
  .kicker {{ font-family: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif; font-size: 19px;
            font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #0e4a5b;
            padding-bottom: 16px; border-bottom: 2px solid #1c1b19; }}
  h1 {{ font-size: 112px; font-weight: 400; line-height: 0.98; letter-spacing: -0.015em; margin: 28px 0 18px; }}
  .deck {{ font-size: 31px; line-height: 1.3; color: #47443e; max-width: 1000px; text-wrap: balance; }}
  .stats {{ position: absolute; left: 80px; right: 80px; bottom: 34px; display: flex; border-top: 3px solid #b4601f; }}
  .stat {{ flex: 1; padding: 16px 22px 0; border-left: 1px solid #c6d8db; }}
  .stat:first-child {{ padding-left: 0; border-left: 0; }}
  .n {{ font-size: 42px; line-height: 1.1; color: #0e4a5b; white-space: nowrap; }}
  .l {{ font-family: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif; font-size: 17px; color: #47443e; margin-top: 2px; white-space: nowrap; }}
</style></head><body>
<p class="kicker">A reference to the published research</p>
<h1>Myoepithelial carcinoma</h1>
<p class="deck">Survival figures, gene fusions, trials and {n_core} papers, each with its source.</p>
<div class="stats">
  <div class="stat"><div class="n">{n_core}</div><div class="l">papers naming the disease</div></div>
  <div class="stat"><div class="n">{n_cases}</div><div class="l">published patient reports</div></div>
  <div class="stat"><div class="n">0.013</div><div class="l">cases per 100,000 a year</div></div>
  <div class="stat"><div class="n">{year_min} to {year_max}</div><div class="l">of research</div></div>
</div>
</body></html>
"""


def find_chrome():
    for candidate in CHROME:
        path = candidate if Path(candidate).is_file() else shutil.which(candidate)
        if path:
            return path
    raise SystemExit("Chrome was not found. Install it, or add its path to CHROME in this file.")


def main():
    ctx = B.build()
    target = HERE / B.C.OG_IMAGE
    with tempfile.TemporaryDirectory() as tmp:
        card = Path(tmp) / "card.html"
        card.write_text(CARD.format(**ctx), encoding="utf-8")
        shot = Path(tmp) / "card.png"
        subprocess.run([find_chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1200,630",
                        "--screenshot=%s" % shot, card.as_uri()], check=True, capture_output=True, timeout=120)
        data = shot.read_bytes()
    # A PNG states its size in bytes 16 to 24.
    width, height = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if (width, height) != (1200, 630):
        raise SystemExit("the image came out %d by %d, not 1200 by 630" % (width, height))
    target.write_bytes(data)
    print("wrote %s (%d KB). Rebuild so the pages carry it: python site/build.py" % (target.relative_to(HERE.parent), len(data) // 1024))


if __name__ == "__main__":
    main()
