"""OpenAlex: download works matching OPENALEX_SEARCHES and parse them.

OpenAlex reaches material the biomedical indexes miss: books, theses, conference
abstracts and regional journals. It also gives open-access locations and
citation counts.

    python harvest/openalex.py      download into data/raw/openalex/
"""

import json
import os
import re
import sys
import urllib.error
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RAW, fetch, log, now, read_gz, replace_batches, write_json  # noqa: E402
from queries import OPENALEX_QUERIES  # noqa: E402

API = "https://api.openalex.org/works"
OUT = RAW / "openalex"
FIELDS = ("id,doi,title,publication_year,publication_date,type,language,ids,"
          "primary_location,open_access,best_oa_location,authorships,cited_by_count,"
          "abstract_inverted_index")


def download():
    """Page through each query.

    Without a key OpenAlex allows roughly 100 requests a day and only
    page-number paging (first 10,000 results per query). Set OPENALEX_API_KEY
    (free at https://openalex.org/settings/api) to lift the daily limit.
    If the quota runs out part-way, what was fetched is kept and query.json
    records the run as incomplete.
    """
    key = os.environ.get("OPENALEX_API_KEY", "")
    payloads = []
    summary = {}
    complete = True
    for label, param, value in OPENALEX_QUERIES:
        got = 0
        total = None
        page_no = 1
        while total is None or got < min(total, 10000):
            params = {param: value, "per-page": 200, "page": page_no, "select": FIELDS}
            if key:
                params["api_key"] = key
            try:
                raw = fetch(API + "?" + urlencode(params), min_interval=0.25, retries=3, timeout=180)
            except urllib.error.HTTPError as err:
                log("OpenAlex: stopped on HTTP %s at page %d of %s" % (err.code, page_no, label))
                complete = False
                break
            page = json.loads(raw)
            results = page.get("results", [])
            total = page.get("meta", {}).get("count", 0)
            if not results:
                break
            payloads.append(raw)
            got += len(results)
            page_no += 1
        summary[label] = {"query": value, "matched": total, "fetched": got}
        log("OpenAlex: %s -> %d of %s" % (label, got, total))
        if not complete:
            break
    if not complete:
        # Never let a run that hit the quota overwrite a complete harvest.
        log("OpenAlex: run incomplete, existing data left untouched. "
            "Set OPENALEX_API_KEY and retry.")
        return
    replace_batches(OUT, "page_*.json.gz", payloads, "page_%04d.json.gz")
    write_json(OUT / "query.json", {"queries": summary, "complete": complete, "fetched_at": now()})


def _abstract(inverted):
    if not inverted:
        return ""
    words = []
    for word, positions in inverted.items():
        for pos in positions:
            words.append((pos, word))
    return " ".join(w for _, w in sorted(words))


def _strip(url, prefix):
    return url[len(prefix):] if url and url.startswith(prefix) else (url or None)


def parse():
    """Yield one normalised record per distinct OpenAlex work in the raw pages."""
    seen = set()
    for path in sorted(OUT.glob("page_*.json.gz")):
        for w in json.loads(read_gz(path)).get("results", []):
            if w["id"] in seen:
                continue
            seen.add(w["id"])
            ids = w.get("ids") or {}
            loc = w.get("primary_location") or {}
            source = loc.get("source") or {}
            oa = w.get("open_access") or {}
            best = w.get("best_oa_location") or {}
            # OpenAlex gives PMC IDs as URLs, with or without the "PMC" prefix.
            pmc_digits = re.search(r"(\d+)/?$", ids.get("pmcid") or "")
            yield {
                "openalex_id": _strip(w["id"], "https://openalex.org/"),
                "pmid": _strip(ids.get("pmid"), "https://pubmed.ncbi.nlm.nih.gov/"),
                "pmcid": "PMC" + pmc_digits.group(1) if pmc_digits else None,
                "doi": (_strip(w.get("doi"), "https://doi.org/") or "").lower() or None,
                "title": " ".join((w.get("title") or "").split()),
                "abstract": _abstract(w.get("abstract_inverted_index")),
                "authors": [(a.get("author") or {}).get("display_name") or ""
                            for a in w.get("authorships") or []],
                "affiliation": "",
                "journal": source.get("display_name") or "",
                "year": w.get("publication_year"),
                "date": w.get("publication_date") or "",
                "language": w.get("language") or "",
                "pub_types": [w["type"]] if w.get("type") else [],
                "mesh": [],
                "keywords": [],
                "is_oa": bool(oa.get("is_oa")),
                "oa_url": best.get("pdf_url") or best.get("landing_page_url") or oa.get("oa_url") or "",
                "license": best.get("license") or "",
                "cited_by": w.get("cited_by_count"),
            }


if __name__ == "__main__":
    download()
    log("OpenAlex: parsed %d distinct works" % sum(1 for _ in parse()))
