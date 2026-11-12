"""Download full text (JATS XML) for every catalog entry that has a PMC ID.

Source is NCBI's PMC, fetched in batches. PMC returns the article body only
where the publisher permits XML download; the rest come back as front matter
only and are listed in data/fulltext/_no_body.txt.

Files land in data/fulltext/PMC<id>.xml.gz. Safe to stop and re-run: papers
already saved or already known to have no body are skipped.

    python harvest/fulltext.py              core tier only
    python harvest/fulltext.py related      core and related
    python harvest/fulltext.py all          every tier
"""

import re
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import CATALOG, FULLTEXT, TOOL, fetch, log, read_jsonl, write_gz  # noqa: E402

EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
TIERS = {"core": ("core",), "related": ("core", "related"), "all": ("core", "related", "mention")}
BATCH = 25

ARTICLE = re.compile(rb"<article[\s>].*?</article>", re.S)
PMCID = re.compile(rb'<article-id pub-id-type="(?:pmcid|pmc|pmcaid)">\s*(?:PMC)?(\d+)\s*</article-id>')
HEADER = b'<?xml version="1.0" encoding="UTF-8"?>\n'


def main(scope="core"):
    wanted = TIERS[scope]
    ids = sorted({p["pmcid"] for p in read_jsonl(CATALOG / "papers.jsonl")
                  if p["tier"] in wanted and p["pmcid"] and re.fullmatch(r"PMC\d+", p["pmcid"])},
                 key=lambda x: int(x[3:]))
    FULLTEXT.mkdir(parents=True, exist_ok=True)
    no_body_path = FULLTEXT / "_no_body.txt"
    no_body = set(no_body_path.read_text().split()) if no_body_path.exists() else set()
    todo = [i for i in ids if i not in no_body and not (FULLTEXT / ("%s.xml.gz" % i)).exists()]
    log("full text: %d PMC IDs in scope '%s', %d to fetch" % (len(ids), scope, len(todo)))

    saved = 0
    for start in range(0, len(todo), BATCH):
        batch = todo[start:start + BATCH]
        body = urlencode({"db": "pmc", "id": ",".join(i[3:] for i in batch), "tool": TOOL}).encode()
        try:
            xml = fetch(EFETCH, data=body, timeout=300)
        except Exception as err:  # a re-run retries this batch
            log("  batch at %d failed: %s" % (start, str(err)[:100]))
            continue
        returned = set()
        for match in ARTICLE.finditer(xml):
            article = match.group(0)
            found = PMCID.search(article)
            if not found:
                continue
            pmcid = "PMC" + found.group(1).decode()
            returned.add(pmcid)
            if b"<body" in article:
                write_gz(FULLTEXT / ("%s.xml.gz" % pmcid), HEADER + article + b"\n")
                saved += 1
            else:
                no_body.add(pmcid)
        # IDs PMC did not return at all (withdrawn or not yet released).
        no_body.update(set(batch) - returned)
        no_body_path.write_text("\n".join(sorted(no_body, key=lambda x: int(x[3:]))) + "\n")
        done = min(start + BATCH, len(todo))
        if done % 250 == 0 or done == len(todo):
            log("  %d/%d fetched, %d saved" % (done, len(todo), saved))
    have = len(list(FULLTEXT.glob("PMC*.xml.gz")))
    log("full text: %d files on disk, %d with no downloadable body" % (have, len(no_body)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "core")
