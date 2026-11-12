"""Derive three things from the catalog. Run after build_catalog.py.

    python harvest/derive.py

Writes:
    data/catalog/centers.json      institutions and countries behind the core papers
    data/catalog/cases.jsonl       one row per single-patient case report
    data/catalog/first_seen.json   the date each work first entered the catalog
    data/catalog/harvest_log.jsonl one line per harvest date, with totals

The case registry is extracted by rule from titles and abstracts. It is an
index to the reports, not reviewed clinical data: every row needs checking
against its paper before anyone relies on it.
"""

import collections
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import CATALOG, RAW, log, read_gz, read_jsonl, write_json, write_jsonl  # noqa: E402

COUNTRIES = {
    "US": "United States", "JP": "Japan", "CN": "China", "IN": "India", "IT": "Italy", "GB": "United Kingdom",
    "DE": "Germany", "BR": "Brazil", "CA": "Canada", "KR": "South Korea", "CZ": "Czechia", "TR": "Turkey",
    "FR": "France", "ES": "Spain", "AU": "Australia", "NL": "Netherlands", "TW": "Taiwan", "GR": "Greece",
    "IR": "Iran", "EG": "Egypt", "MX": "Mexico", "SA": "Saudi Arabia", "PL": "Poland", "CH": "Switzerland",
    "SE": "Sweden", "BE": "Belgium", "AT": "Austria", "PT": "Portugal", "IL": "Israel", "TH": "Thailand",
    "PK": "Pakistan", "MY": "Malaysia", "SG": "Singapore", "DK": "Denmark", "FI": "Finland", "NO": "Norway",
    "RS": "Serbia", "TN": "Tunisia", "MA": "Morocco", "NG": "Nigeria", "ID": "Indonesia", "AR": "Argentina",
    "CL": "Chile", "CO": "Colombia", "HU": "Hungary", "RO": "Romania", "IE": "Ireland", "NZ": "New Zealand",
    "HK": "Hong Kong", "RU": "Russia", "ZA": "South Africa", "NP": "Nepal", "BD": "Bangladesh", "LK": "Sri Lanka",
    "HR": "Croatia", "SI": "Slovenia", "SK": "Slovakia", "BG": "Bulgaria", "LB": "Lebanon", "JO": "Jordan",
    "QA": "Qatar", "AE": "United Arab Emirates", "KW": "Kuwait", "VN": "Vietnam", "PH": "Philippines", "PE": "Peru",
    "KZ": "Kazakhstan", "UA": "Ukraine", "BY": "Belarus", "LT": "Lithuania", "LV": "Latvia", "EE": "Estonia",
    "CU": "Cuba", "VE": "Venezuela", "EC": "Ecuador", "UY": "Uruguay", "KE": "Kenya", "ET": "Ethiopia", "GH": "Ghana",
    "SD": "Sudan", "DZ": "Algeria", "IQ": "Iraq", "SY": "Syria", "OM": "Oman", "BH": "Bahrain", "YE": "Yemen",
    "UZ": "Uzbekistan", "MN": "Mongolia", "KH": "Cambodia", "MM": "Myanmar", "CY": "Cyprus", "MT": "Malta",
    "LU": "Luxembourg", "IS": "Iceland", "BA": "Bosnia and Herzegovina", "MK": "North Macedonia", "AL": "Albania",
    "GE": "Georgia", "AM": "Armenia", "AZ": "Azerbaijan", "LY": "Libya", "SN": "Senegal", "CM": "Cameroon",
    "TZ": "Tanzania", "UG": "Uganda", "ZW": "Zimbabwe", "CR": "Costa Rica", "PA": "Panama", "DO": "Dominican Republic",
    "GT": "Guatemala", "BO": "Bolivia", "PY": "Paraguay", "PR": "Puerto Rico", "MO": "Macau", "BN": "Brunei",
}


def openalex_institutions():
    """Map OpenAlex work ID -> list of (institution, country code, type) and first-author country."""
    out = {}
    for path in sorted((RAW / "openalex").glob("page_*.json.gz")):
        for work in json.loads(read_gz(path)).get("results", []):
            wid = work["id"].rsplit("/", 1)[-1]
            if wid in out:
                continue
            seen, first_country = {}, ""
            for n, author in enumerate(work.get("authorships") or []):
                for inst in author.get("institutions") or []:
                    if inst.get("display_name"):
                        seen[inst["display_name"]] = (inst.get("country_code") or "", inst.get("type") or "")
                    if n == 0 and not first_country:
                        first_country = inst.get("country_code") or ""
            out[wid] = (seen, first_country)
    return out


def centers(papers, inst_by_work):
    core = [p for p in papers if p["tier"] == "core" and not p["is_animal"]]
    rows = collections.defaultdict(lambda: {"papers": 0, "skin": 0, "since_2015": 0, "years": [], "sites": collections.Counter()})
    countries = collections.Counter()
    covered = 0
    for p in core:
        seen, _ = inst_by_work.get(p.get("openalex_id") or "", ({}, ""))
        if not seen:
            continue
        covered += 1
        countries.update({code for code, _ in seen.values() if code})
        for name, (code, kind) in seen.items():
            row = rows[name]
            row["country"], row["type"] = code, kind
            row["papers"] += 1
            row["skin"] += p["focus"] == "primary"
            row["since_2015"] += (p["year"] or 0) >= 2015
            row["sites"].update(p["sites"])
            if p["year"]:
                row["years"].append(p["year"])
    institutions = []
    for name, row in rows.items():
        institutions.append({
            "name": name, "country_code": row["country"], "country": COUNTRIES.get(row["country"], row["country"]),
            "type": row["type"], "papers": row["papers"], "skin_papers": row["skin"], "since_2015": row["since_2015"],
            "first_year": min(row["years"]) if row["years"] else None, "last_year": max(row["years"]) if row["years"] else None,
            "top_sites": [s for s, _ in row["sites"].most_common(3)],
        })
    institutions.sort(key=lambda r: (-r["papers"], r["name"]))
    write_json(CATALOG / "centers.json", {
        "core_papers": len(core), "papers_with_institutions": covered,
        "countries": [{"code": c, "country": COUNTRIES.get(c, c), "papers": n} for c, n in countries.most_common()],
        "institutions": institutions,
    })
    log("centers: %d institutions in %d countries, from %d of %d core papers"
        % (len(institutions), len(countries), covered, len(core)))


MULTI = re.compile(r"\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:new\s+|additional\s+)?(?:cases|patients)\b"
                   r"|case series|series of|review of \d+", re.I)
AGE = re.compile(r"(\d{1,3})[\s-]*(year|yr|month|week|day)s?[\s-]*old", re.I)
AGE_ALT = re.compile(r"\b(?:aged|age of)\s+(\d{1,3})\b(?:\s*(year|month))?", re.I)
FEMALE = re.compile(r"\b(?:woman|female|girl|lady|she|her)\b", re.I)
MALE = re.compile(r"\b(?:man|male|boy|gentleman|he|his)\b", re.I)
SITES = [
    ("Parotid gland", r"parotid"), ("Submandibular gland", r"submandibular"), ("Sublingual gland", r"sublingual"),
    ("Palate", r"palat"), ("Tongue", r"tongue"), ("Lip", r"\blips?\b"), ("Gingiva", r"gingiv"),
    ("Floor of mouth", r"floor of (?:the )?mouth"), ("Buccal mucosa", r"buccal"),
    ("Lacrimal gland", r"lacrimal"), ("Orbit", r"orbit"), ("Maxillary sinus", r"maxillary sinus|maxilla"),
    ("Nasal cavity", r"nasal cavity|nasal septum|sinonasal|\bnose\b"), ("Nasopharynx", r"nasopharyn"),
    ("Larynx", r"laryn|epiglott|vocal"), ("Trachea", r"trache"), ("Lung", r"\blung|pulmonary|bronch"),
    ("Breast", r"\bbreast|mammary"), ("Vulva", r"vulva|bartholin"), ("Vagina", r"vagin"),
    ("Ear canal", r"auditory canal|\bear\b"), ("Mandible", r"mandib"), ("Scalp", r"scalp"),
    ("Axilla", r"axilla"), ("Hand or finger", r"\bhand\b|finger|thumb|palm"), ("Foot or toe", r"\bfoot\b|\btoe\b|\bheel\b|plantar"),
    ("Thigh", r"thigh"), ("Leg", r"\bleg\b|\bcalf\b|\bknee\b|shin"), ("Arm", r"\barm\b|forearm|elbow|shoulder"),
    ("Chest wall", r"chest wall"), ("Back", r"\bback\b"), ("Groin", r"groin|inguinal"), ("Retroperitoneum", r"retroperitone"),
    ("Mediastinum", r"mediastin"), ("Spine", r"vertebra|spine|spinal|sacr"), ("Bone", r"\bbone\b|femur|tibia|humerus|iliac"),
    ("Liver", r"\bliver|hepatic"), ("Kidney", r"\bkidney|renal"), ("Bladder", r"bladder"), ("Esophagus", r"esophag|oesophag"),
    ("Stomach", r"stomach|gastric"), ("Heart", r"cardiac|\bheart\b|atri"), ("Brain", r"\bbrain\b|intracranial|cerebr|dura"),
    ("Thyroid", r"thyroid"), ("Pancreas", r"pancrea"), ("Scrotum", r"scrot"), ("Pharynx", r"vallecula|pharyn|tonsil"),
    ("Cheek or face", r"cheek|\bface\b|facial|eyelid|forehead"), ("Neck", r"\bneck\b|cervical"),
    ("Abdominal wall", r"abdominal wall"), ("Pelvis or buttock", r"pelvi|buttock|glute|perine"),
    ("Skin", r"cutaneous|\bskin\b|dermal"),
    ("Salivary gland", r"salivary"), ("Soft tissue", r"soft[\s-]tissue"),
]
SITES = [(label, re.compile(pattern, re.I)) for label, pattern in SITES]
GROUP_ORDER = ["skin", "soft_tissue", "salivary", "breast", "lung", "bone", "head_neck_other", "gyn"]
TREATMENTS = [
    ("surgery", r"excis|resect|surg|ectomy|\bmohs\b|amputat"),
    ("radiotherapy", r"radiother|radiation|irradiat|brachyther"),
    ("chemotherapy", r"chemother|doxorubicin|cisplatin|ifosfamide|carboplatin|paclitaxel|etoposide|vincristine|cyclophosphamide"),
    ("targeted or immune therapy", r"pembrolizumab|nivolumab|immunother|targeted therap|pazopanib|imatinib|inhibitor"),
]
TREATMENTS = [(label, re.compile(pattern, re.I)) for label, pattern in TREATMENTS]
EVENTS = [
    ("recurrence", r"recurr"), ("metastasis", r"metasta"),
    ("death", r"\b(?:died|death|deceased|succumbed|expired)\b"),
    ("disease-free at follow-up", r"no evidence of (?:disease|recurrence|metasta)|disease[\s-]free|free of (?:disease|recurrence)"
                                  r"|alive and well|without (?:any )?(?:evidence of )?recurrence|no (?:sign|signs) of recurrence|no recurrence"),
]
EVENTS = [(label, re.compile(pattern, re.I)) for label, pattern in EVENTS]
# A sentence such as "no recurrence or metastasis at 12 months" is not an event.
NEGATED = re.compile(r"\b(?:no|not|without|free of|free from|absence of|negative for|neither|nor|rule out|excluded?)\b"
                     r"[^.;]{0,70}?(?:recurr|metasta)", re.I)
GENES = re.compile(r"\b(EWSR1|FUS|PLAG1|HMGA2|SMARCB1|INI1|KLF15|KLF17|PBX1|PBX3|POU5F1|ATF1|ZNF444|NTRK[123]?|HRAS|PIK3CA|TP53|FGFR[12]|TGFBR3|SS18)\b")
FOLLOW = [
    re.compile(r"(\d{1,3})[\s-]*(month|year)s?[\s'-]*(?:of\s+)?(?:post[\s-]?operative\s+)?follow[\s-]?up", re.I),
    re.compile(r"follow[\s-]?up[^.;]{0,50}?(\d{1,3})[\s-]*(month|year)", re.I),
    re.compile(r"(\d{1,3})[\s-]*(month|year)s?\s+(?:after|following|post)[^.;]{0,25}?(?:surg|operation|resect|excis|treatment)", re.I),
]


def one_case(p, inst_by_work):
    text = "%s. %s" % (p["title"] or "", p["abstract"] or "")
    age = unit = None
    match = AGE.search(text) or AGE_ALT.search(text)
    if match:
        value, raw_unit = int(match.group(1)), (match.group(2) or "year").lower()
        raw_unit = "year" if raw_unit == "yr" else raw_unit
        if (raw_unit == "year" and value <= 105) or (raw_unit != "year" and value <= 48):
            age, unit = value, raw_unit
    sex = ""
    if match:
        window = text[max(0, match.start() - 60):match.end() + 80]
        f, m = bool(FEMALE.search(window)), bool(MALE.search(window))
        sex = "F" if f and not m else "M" if m and not f else ""
    if not sex:
        f, m = len(FEMALE.findall(text)), len(MALE.findall(text))
        sex = "F" if f > m else "M" if m > f else ""
    # The title names where the tumor arose. Abstracts also name where it spread
    # to, so they are not used for the site.
    site = next((label for label, rx in SITES if rx.search(p["title"] or "")), "")
    events = []
    sentences = re.split(r"(?<=[.;])\s+", p["abstract"] or "")
    for label, rx in EVENTS:
        hits = [s for s in sentences if rx.search(s)]
        if label in ("recurrence", "metastasis"):
            hits = [s for s in hits if not NEGATED.search(s)]
        if hits:
            events.append(label)
    follow = None
    for rx in FOLLOW:
        found = rx.search(p["abstract"] or "")
        if found:
            months = int(found.group(1)) * (12 if found.group(2).lower() == "year" else 1)
            if 0 < months <= 480:
                follow = months
                break
    _, first_country = inst_by_work.get(p.get("openalex_id") or "", ({}, ""))
    age_years = None
    if age is not None:
        age_years = age if unit == "year" else round(age / {"month": 12.0, "week": 52.0, "day": 365.0}[unit], 1)
    return {
        "id": p["id"], "pmid": p["pmid"], "doi": p["doi"], "year": p["year"], "title": p["title"], "journal": p["journal"],
        "language": p["language"], "country": COUNTRIES.get(first_country, first_country),
        "age": age, "age_unit": unit, "age_years": age_years, "sex": sex,
        "site": site, "site_group": next((g for g in GROUP_ORDER if g in p["sites"]), ""),
        "child": age_years is not None and age_years < 18,
        "treatments": [label for label, rx in TREATMENTS if rx.search(p["abstract"] or "")],
        "events": events,
        "follow_up_months": follow,
        "genes": sorted(set(GENES.findall(text))),
        "has_abstract": p["has_abstract"], "is_oa": p["is_oa"], "focus": p["focus"],
    }


def cases(papers, inst_by_work):
    reports = [p for p in papers if p["tier"] == "core" and p["is_case_report"] and not p["is_animal"]
               and p["named_in_title"] and not MULTI.search(p["title"] or "")]
    rows = [one_case(p, inst_by_work) for p in reports]
    rows.sort(key=lambda r: (-(r["year"] or 0), r["title"] or ""))
    write_jsonl(CATALOG / "cases.jsonl", rows)
    log("cases: %d single-patient reports; age found in %d, sex in %d, site in %d, follow-up in %d"
        % (len(rows), sum(r["age"] is not None for r in rows), sum(bool(r["sex"]) for r in rows),
           sum(bool(r["site"]) for r in rows), sum(r["follow_up_months"] is not None for r in rows)))


def whats_new(papers):
    today = datetime.date.today().isoformat()
    path = CATALOG / "first_seen.json"
    first_seen = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    baseline = not first_seen
    added = 0
    for p in papers:
        if p["id"] not in first_seen:
            first_seen[p["id"]] = today
            added += 1
    write_json(path, first_seen)
    log_path = CATALOG / "harvest_log.jsonl"
    entries = [e for e in (read_jsonl(log_path) if log_path.exists() else []) if e["date"] != today]
    previous = entries[-1] if entries else None
    core = sum(p["tier"] == "core" for p in papers)
    entries.append({
        "date": today, "total": len(papers), "core": core, "baseline": baseline or not previous,
        "added": added if previous or not baseline else len(papers),
        "added_core": sum(1 for p in papers if p["tier"] == "core" and first_seen[p["id"]] == today),
    })
    write_jsonl(log_path, entries)
    log("what's new: %d works first seen today, %d harvest dates on record" % (added, len(entries)))


if __name__ == "__main__":
    catalog = read_jsonl(CATALOG / "papers.jsonl")
    lookup = openalex_institutions()
    centers(catalog, lookup)
    cases(catalog, lookup)
    whats_new(catalog)
