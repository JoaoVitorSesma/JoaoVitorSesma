"""Check every link in the READMEs and assets/SOURCES.md.

    python scripts/check_links.py

Relative links must point to a file in the repository, "#anchors" to a heading of
the same page, and web links must answer. Uses only the standard library, so the
CI job needs no install. Exits 1 if anything is broken.
"""

import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [ROOT / "README.md", ROOT / "README.pt-BR.md", ROOT / "assets" / "SOURCES.md"]

# Markdown links [text](target) and HTML href/src attributes.
LINK = re.compile(r'\]\(([^)\s]+)\)|(?:href|src|srcset)="([^"]+)"')
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.M)

# Sites that refuse automated requests although the page works in a browser.
# A refusal from them is reported but does not fail the check.
# Checked by hand in a browser: LinkedIn opens the profile, Outlook opens its sign-in
# page before composing (as a compose link should).
BLOCKS_BOTS = {"www.linkedin.com": {999}, "outlook.live.com": {417}}
TIMEOUT, ATTEMPTS = 20, 3


def slug(heading):
    """GitHub's anchor for a heading: lower case, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"[`*_]", "", heading).strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def links(page):
    for match in LINK.finditer(page.read_text(encoding="utf-8")):
        yield match[1] or match[2]


def check_web(url):
    """None if the link answers, else the reason it does not."""
    host = urllib.parse.urlsplit(url).hostname
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (readme link check)"})
    error = None
    for attempt in range(ATTEMPTS):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                if response.status < 400:
                    return None
                error = f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            if e.code in BLOCKS_BOTS.get(host, ()):
                return "skip"
            error = f"HTTP {e.code}"
            if e.code < 500 and e.code != 429:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            error = str(getattr(e, "reason", e))
        time.sleep(2 * (attempt + 1))
    return error


def main():
    broken, skipped, seen = [], [], {}
    for page in PAGES:
        anchors = {slug(h) for h in HEADING.findall(page.read_text(encoding="utf-8"))}
        for target in links(page):
            where = f"{page.relative_to(ROOT).as_posix()}: {target}"
            if target.startswith("mailto:"):
                continue
            if target.startswith("#"):
                if target[1:] not in anchors:
                    broken.append(f"{where} (no such heading)")
                continue
            if target.startswith(("http://", "https://")):
                if target not in seen:
                    seen[target] = check_web(target)
                result = seen[target]
                if result == "skip":
                    skipped.append(where)
                elif result:
                    broken.append(f"{where} ({result})")
                continue
            path = (page.parent / urllib.parse.unquote(target.split("#")[0])).resolve()
            if not path.exists():
                broken.append(f"{where} (missing file)")
    print(f"Checked {len(seen)} web links and the relative links of {len(PAGES)} pages.")
    for line in skipped:
        print(f"  skipped, site refuses automated requests: {line}")
    for line in broken:
        print(f"  BROKEN {line}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
