"""Tell search engines that the site's pages are new or have changed.

    python site/indexnow.py             submit every page in the built sitemap
    python site/indexnow.py --dry-run   show what would be sent

IndexNow is a shared protocol: one request reaches Bing, Yandex, Seznam, Naver
and the others that take part. Bing's index also feeds several AI assistants.
Google does not take part: it learns of the pages from the sitemap, which is
registered in Search Console.

Run it after a publish has gone live, not before. The search engine fetches
the key file from the site to confirm the request, so the key file
(<key>.txt at the top of staas.fund, holding the key and nothing else) must
already be deployed. The key is in site/content.py. It is public by design.

Standard library only.
"""

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build as B  # noqa: E402

ENDPOINT = "https://api.indexnow.org/indexnow"
USER_AGENT = "myoepithelial-carcinoma-site/1.0"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def main(argv):
    sitemap = B.OUT / "sitemap.xml"
    if not sitemap.is_file():
        raise SystemExit("no built sitemap. Run python site/build.py first.")
    urls = re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8"))
    host = re.match(r"https://([^/]+)/", B.C.BASE_URL).group(1)
    key = B.C.INDEXNOW_KEY
    key_url = "https://%s/%s.txt" % (host, key)
    payload = {"host": host, "key": key, "keyLocation": key_url, "urlList": urls}

    if "--dry-run" in argv:
        print("would send %d URLs for %s to %s" % (len(urls), host, ENDPOINT))
        print("key file expected at %s" % key_url)
        return

    try:
        status, body = fetch(key_url)
    except urllib.error.HTTPError as e:
        status, body = e.code, ""
    if status != 200 or body.strip() != key:
        raise SystemExit("the key file is not live at %s (status %s). Deploy it first." % (key_url, status))

    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            code = resp.status
    except urllib.error.HTTPError as e:
        raise SystemExit("IndexNow refused the request: HTTP %s %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
    # 200: accepted. 202: accepted, the key is still being checked.
    print("IndexNow answered HTTP %s for %d URLs on %s" % (code, len(urls), host))


if __name__ == "__main__":
    main(sys.argv[1:])
