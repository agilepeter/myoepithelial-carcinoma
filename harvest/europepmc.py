"""Europe PMC: download every record matching EUROPEPMC_QUERY and parse it.

Europe PMC adds what PubMed lacks: preprints, patents, theses, and papers that
only mention the disease in their full text.

    python harvest/europepmc.py     download into data/raw/europepmc/
"""

import json
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RAW, fetch, log, now, read_gz, replace_batches, write_json  # noqa: E402
from queries import EUROPEPMC_QUERY  # noqa: E402

API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OUT = RAW / "europepmc"


def download():
    cursor = "*"
    payloads = []
    total = None
    got = 0
    while True:
        url = API + "?" + urlencode(
            {"query": EUROPEPMC_QUERY, "format": "json", "resultType": "core",
             "pageSize": 1000, "cursorMark": cursor}
        )
        raw = fetch(url, timeout=180)
        page = json.loads(raw)
        results = page.get("resultList", {}).get("result", [])
        if total is None:
            total = page.get("hitCount", 0)
            log("Europe PMC: %d records match" % total)
        if not results:
            break
        payloads.append(raw)
        got += len(results)
        log("  fetched %d" % got)
        nxt = page.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
    replace_batches(OUT, "page_*.json.gz", payloads, "page_%04d.json.gz")
    write_json(OUT / "query.json", {"query": EUROPEPMC_QUERY, "count": total, "fetched_at": now()})


def _list(obj, outer, inner):
    return (obj.get(outer) or {}).get(inner) or []


def parse():
    """Yield one normalised record per Europe PMC entry in the raw pages."""
    for path in sorted(OUT.glob("page_*.json.gz")):
        page = json.loads(read_gz(path))
        for r in page.get("resultList", {}).get("result", []):
            journal = ((r.get("journalInfo") or {}).get("journal") or {}).get("title", "")
            book = (r.get("bookOrReportDetails") or {}).get("publisher", "")
            year = r.get("pubYear")
            urls = _list(r, "fullTextUrlList", "fullTextUrl")
            oa_url = next((u.get("url") for u in urls
                           if u.get("availabilityCode") in ("OA", "F")), "")
            yield {
                "epmc_id": "%s:%s" % (r.get("source"), r.get("id")),
                "epmc_source": r.get("source"),
                "pmid": r.get("pmid") or None,
                "pmcid": r.get("pmcid") or None,
                "doi": (r.get("doi") or "").lower() or None,
                "title": " ".join((r.get("title") or "").split()),
                "abstract": r.get("abstractText") or "",
                "authors": [a.strip() for a in (r.get("authorString") or "").rstrip(".").split(",")
                            if a.strip()],
                "affiliation": r.get("affiliation") or "",
                "journal": journal or book,
                "year": int(year) if str(year or "").isdigit() else None,
                "date": r.get("firstPublicationDate") or "",
                "language": r.get("language") or "",
                "pub_types": _list(r, "pubTypeList", "pubType"),
                "mesh": [m.get("descriptorName") for m in _list(r, "meshHeadingList", "meshHeading")
                         if m.get("descriptorName")],
                "keywords": _list(r, "keywordList", "keyword"),
                "is_oa": r.get("isOpenAccess") == "Y",
                "in_epmc": r.get("inEPMC") == "Y",
                "license": r.get("license") or "",
                "oa_url": oa_url or "",
                "cited_by": r.get("citedByCount"),
            }


if __name__ == "__main__":
    download()
    log("Europe PMC: parsed %d records" % sum(1 for _ in parse()))
