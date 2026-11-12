"""ClinicalTrials.gov: download trials matching CTGOV_SEARCHES and parse them.

Two groups are kept. Trials whose record names myoepithelial tumours anywhere,
and all salivary gland trials, because those often enrol myoepithelial carcinoma
under "other histologies" without naming it.

    python harvest/ctgov.py         download and write data/catalog/trials.jsonl
"""

import json
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import CATALOG, RAW, fetch, log, now, read_gz, replace_batches, write_json, write_jsonl  # noqa: E402
from queries import CTGOV_SEARCHES  # noqa: E402

API = "https://clinicaltrials.gov/api/v2/studies"
OUT = RAW / "ctgov"


def download():
    payloads = []
    counts = {}
    for label, param, value in CTGOV_SEARCHES:
        token = None
        got = 0
        while True:
            params = {param: value, "pageSize": 100, "countTotal": "true"}
            if token:
                params["pageToken"] = token
            raw = fetch(API + "?" + urlencode(params), timeout=180)
            page = json.loads(raw)
            if "totalCount" in page:
                counts[label] = page["totalCount"]
            payloads.append(raw)
            got += len(page.get("studies", []))
            token = page.get("nextPageToken")
            if not token:
                break
        log("ClinicalTrials.gov: %s -> %d of %s" % (label, got, counts.get(label)))
    replace_batches(OUT, "page_*.json.gz", payloads, "page_%04d.json.gz")
    write_json(OUT / "query.json", {"searches": counts, "fetched_at": now()})


def parse():
    """Yield one slim record per distinct trial in the raw pages."""
    seen = set()
    for path in sorted(OUT.glob("page_*.json.gz")):
        for study in json.loads(read_gz(path)).get("studies", []):
            ps = study.get("protocolSection") or {}
            ident = ps.get("identificationModule") or {}
            nct = ident.get("nctId")
            if not nct or nct in seen:
                continue
            seen.add(nct)
            status = ps.get("statusModule") or {}
            design = ps.get("designModule") or {}
            cond = ps.get("conditionsModule") or {}
            arms = ps.get("armsInterventionsModule") or {}
            locs = (ps.get("contactsLocationsModule") or {}).get("locations") or []
            criteria = (ps.get("eligibilityModule") or {}).get("eligibilityCriteria") or ""
            blob = json.dumps(study).lower()
            yield {
                "nct_id": nct,
                "names_myoepithelial": "myoepitheli" in blob,
                # "adnexal" alone also matches ovarian trials, so require a skin phrase.
                "names_skin_adnexal": any(w in blob for w in (
                    "adnexal carcinoma", "skin adnexal", "cutaneous adnexal", "adnexal skin",
                    "sweat gland", "skin appendage", "chondroid syringoma", "eccrine",
                    "rare dermatological", "rare skin cancer")),
                "title": ident.get("briefTitle") or "",
                "official_title": ident.get("officialTitle") or "",
                "status": status.get("overallStatus") or "",
                "start": (status.get("startDateStruct") or {}).get("date") or "",
                "primary_completion": (status.get("primaryCompletionDateStruct") or {}).get("date") or "",
                "study_type": design.get("studyType") or "",
                "phases": design.get("phases") or [],
                "enrollment": (design.get("enrollmentInfo") or {}).get("count"),
                "conditions": cond.get("conditions") or [],
                "interventions": ["%s: %s" % (i.get("type"), i.get("name"))
                                  for i in arms.get("interventions") or []],
                "sponsor": ((ps.get("sponsorCollaboratorsModule") or {}).get("leadSponsor") or {}).get("name") or "",
                "countries": sorted({l.get("country") for l in locs if l.get("country")}),
                "has_results": bool(study.get("hasResults")),
                "summary": (ps.get("descriptionModule") or {}).get("briefSummary") or "",
                "eligibility": criteria,
                "url": "https://clinicaltrials.gov/study/%s" % nct,
            }


def build():
    trials = sorted(parse(), key=lambda t: (not t["names_myoepithelial"], t["nct_id"]))
    write_jsonl(CATALOG / "trials.jsonl", trials)
    named = sum(t["names_myoepithelial"] for t in trials)
    adnexal = sum(t["names_skin_adnexal"] for t in trials)
    log("ClinicalTrials.gov: %d trials, %d name myoepithelial tumours, %d name skin adnexal tumours"
        % (len(trials), named, adnexal))
    return trials


if __name__ == "__main__":
    download()
    build()
