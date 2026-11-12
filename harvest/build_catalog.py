"""Merge the raw harvests into one deduplicated catalog of papers.

Reads data/raw/{pubmed,europepmc,openalex,semanticscholar}/ and writes:
    data/catalog/papers.jsonl   one line per distinct work
    data/catalog/stats.json     counts used in notes and reports

    python harvest/build_catalog.py

Records are matched across sources by PMID, then DOI, then PMCID. PubMed is
loaded first and wins on conflicts; later sources only fill gaps.
"""

import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import europepmc  # noqa: E402
import extras  # noqa: E402
import openalex  # noqa: E402
import pubmed  # noqa: E402
from common import CATALOG, log, now, write_json, write_jsonl  # noqa: E402

# "epithelial-myoepithelial carcinoma" is a different diagnosis, so it is removed
# from the text before testing for the core phrases.
EMC = re.compile(r"epithelial[\s\-‐-―/]+myoepithelial\s+(?:cell\s+)?carcinoma", re.I)
CORE = re.compile(
    r"myoepithelial\s+(?:cell\s+)?carcinoma|malignant\s+myoepitheliom|malignant\s+myoepithelial"
    r"|carcinoma,\s+myoepithelial|myoepithelioma,\s+malignant", re.I)
RELATED = re.compile(
    r"myoepitheliom|myoepithelial\s+(?:cell\s+)?(?:tumou?r|neoplasm|lesion)"
    r"|epithelial[\s\-‐-―/]+myoepithelial", re.I)

# The skin and adnexal neighbourhood, also counted as "related".
RELATED_SKIN = re.compile(
    r"chondroid\s+syringoma|mixed\s+tumou?rs?\s+of\s+(?:the\s+)?skin"
    r"|(?:cutaneous|apocrine|eccrine)\s+mixed\s+tumou?r", re.I)
SKIN_WORD = re.compile(r"cutaneous|adnexal|\bskin\b|dermal", re.I)

# "Adnexal" also means the ovaries and tubes, and the tissues around the eye.
# Count an adnexal tumour as skin only when nothing points to those.
ADNEXAL = re.compile(r"adnexal\s+(?:carcinoma|tumou?r|neoplasm)", re.I)
OTHER_ADNEXA = re.compile(
    r"ovar|uter|pelvi|wolffian|fallopian|tubal|gyn[ae]+col|endometri|ocular\s+adnex|orbit", re.I)


def skin_adnexal(text):
    return bool(ADNEXAL.search(text)) and not OTHER_ADNEXA.search(text)

# Peter's diagnosis is a skin adnexal myoepithelial carcinoma. The "focus" field
# marks the works closest to it ("primary") and the next ring out ("secondary").
SKIN_MALIGNANT = re.compile(
    r"malignant\s+chondroid\s+syringoma|malignant\s+(?:cutaneous\s+)?mixed\s+tumou?r"
    r"|cutaneous\s+myoepithelial\s+carcinoma|cutaneous\s+malignant\s+myoepitheliom"
    r"|myoepithelial\s+carcinomas?\s+of\s+(?:the\s+)?skin", re.I)
SKIN_NEIGHBOUR = re.compile(
    r"chondroid\s+syringoma|mixed\s+tumou?rs?\s+of\s+(?:the\s+)?skin"
    r"|(?:cutaneous|apocrine|eccrine)\s+mixed\s+tumou?r|cutaneous\s+myoepitheliom", re.I)

# Heuristic body-site tags from title and abstract. A starting point for
# browsing, not a classification.
SITES = {
    "salivary": r"salivary|parotid|submandibular|sublingual|palat|minor gland|pleomorphic adenoma",
    "breast": r"\bbreast|mammary",
    "soft_tissue": r"soft[\s-]tissue|EWSR1|extremit|\bthigh|retroperitone",
    "skin": (r"cutaneous|\bskin\b|dermal|dermis|subcutaneous|chondroid syringoma|adnexal"
             r"|sweat gland|eccrine|subungual|\bscalp\b"),
    "bone": r"\bbone\b|osseous|intraosseous|vertebra|tibia|femur",
    "lung": r"\blung|pulmonary|bronch|trachea",
    "head_neck_other": r"lacrimal|nasal|sinus|sinonasal|nasopharyn|laryn|orbit|maxill|tongue|oral cavity",
    "gyn": r"vulva|vagin|uter|ovar|bartholin",
    "pediatric": r"child|pediatric|paediatric|infant|adolescen|congenital|neonat",
}
SITE_RES = {name: re.compile(pattern, re.I) for name, pattern in SITES.items()}

ANIMAL = re.compile(r"\b(?:canine|dogs?|feline|cats?|murine|mice|mouse|rats?|bovine|equine|veterinary)\b", re.I)

# OpenAlex entries that are journal front matter rather than works.
SKIP_TYPES = {"paratext"}

LANGUAGES = {"eng": "en", "chi": "zh", "ger": "de", "fre": "fr", "spa": "es", "jpn": "ja",
             "ita": "it", "rus": "ru", "por": "pt", "kor": "ko", "pol": "pl", "cze": "cs",
             "dut": "nl", "nor": "no", "srp": "sr", "tur": "tr", "hun": "hu", "dan": "da",
             "swe": "sv", "ukr": "uk", "rum": "ro", "gre": "el", "heb": "he", "per": "fa",
             "ara": "ar", "fin": "fi", "bul": "bg", "hrv": "hr", "slo": "sk", "slv": "sl"}

LIST_FIELDS = ("authors", "pub_types", "mesh", "keywords")
TEXT_FIELDS = ("title", "abstract", "affiliation", "journal", "date", "language", "license", "oa_url")
ID_FIELDS = ("pmid", "pmcid", "doi", "openalex_id", "epmc_id", "s2_id")


def merge(base, new, source):
    for field in ID_FIELDS + TEXT_FIELDS + ("year",):
        if not base.get(field) and new.get(field):
            base[field] = new[field]
    for field in LIST_FIELDS:
        values = [str(v) for v in new.get(field) or [] if v]
        if not base.get(field) and values:
            base[field] = values
    if new.get("is_oa"):
        base["is_oa"] = True
    if new.get("in_epmc"):
        base["in_epmc"] = True
    if new.get("cited_by") is not None:
        base["cited_by"] = max(base.get("cited_by") or 0, new["cited_by"])
    if source not in base["sources"]:
        base["sources"].append(source)


def classify(rec):
    text = "%s\n%s" % (rec.get("title", ""), rec.get("abstract", ""))
    extra = " ".join(rec.get("keywords", []) + rec.get("mesh", []))
    if CORE.search(EMC.sub(" ", text)) or CORE.search(EMC.sub(" ", extra)):
        return "core"
    if RELATED.search(text) or RELATED.search(extra) or RELATED_SKIN.search(text):
        return "related"
    if skin_adnexal(text):
        return "related"
    if "myoepithelial" in text.lower() and SKIN_WORD.search(text) and not OTHER_ADNEXA.search(text):
        return "related"
    return "mention"


def finish(rec):
    text = "%s\n%s" % (rec.get("title", ""), rec.get("abstract", ""))
    types = " ".join(rec.get("pub_types", [])).lower()
    rec["tier"] = classify(rec)
    # True when the title itself names the disease, not only the abstract.
    rec["named_in_title"] = bool(CORE.search(EMC.sub(" ", rec.get("title", ""))))
    rec["sites"] = sorted(name for name, rx in SITE_RES.items() if rx.search(text))
    rec["is_case_report"] = "case report" in types or bool(
        re.search(r"case report|report of (?:a|an|two|three|\d+) cases?|a rare case|: a case", text, re.I))
    rec["is_review"] = "review" in types or "meta-analysis" in types
    rec["has_abstract"] = bool(rec.get("abstract"))
    mesh = rec.get("mesh", [])
    rec["is_animal"] = ("Animals" in mesh and "Humans" not in mesh) or bool(
        not mesh and ANIMAL.search(rec.get("title", "")))
    if rec["is_animal"]:
        rec["focus"] = ""
    elif (rec["tier"] == "core" and "skin" in rec["sites"]) or SKIN_MALIGNANT.search(text):
        rec["focus"] = "primary"
    elif ((rec["tier"] == "core" and "soft_tissue" in rec["sites"]) or SKIN_NEIGHBOUR.search(text)
          or skin_adnexal(text)
          or (rec["tier"] == "related" and "skin" in rec["sites"] and not OTHER_ADNEXA.search(text))):
        rec["focus"] = "secondary"
    else:
        rec["focus"] = ""
    langs = [LANGUAGES.get(x.strip().lower(), x.strip().lower())
             for x in (rec.get("language") or "").split(",") if x.strip()]
    rec["language"] = ", ".join(dict.fromkeys(langs))
    rec["id"] = ("pmid:%s" % rec["pmid"] if rec.get("pmid")
                 else "doi:%s" % rec["doi"] if rec.get("doi")
                 else "pmcid:%s" % rec["pmcid"] if rec.get("pmcid")
                 else "epmc:%s" % rec["epmc_id"] if rec.get("epmc_id")
                 else "openalex:%s" % rec["openalex_id"] if rec.get("openalex_id")
                 else "s2:%s" % rec.get("s2_id"))
    for field in ID_FIELDS + TEXT_FIELDS:
        rec.setdefault(field, None if field in ID_FIELDS else "")
    for field in LIST_FIELDS:
        rec.setdefault(field, [])
    rec.setdefault("year", None)
    rec.setdefault("is_oa", False)
    rec.setdefault("in_epmc", False)
    rec.setdefault("cited_by", None)
    return rec


def build():
    by_key = {}
    records = []
    for source, parse in (("pubmed", pubmed.parse), ("europepmc", europepmc.parse),
                          ("openalex", openalex.parse), ("semanticscholar", extras.s2_parse)):
        added = 0
        for new in parse():
            if SKIP_TYPES.intersection(new.get("pub_types") or []):
                continue
            keys = [(k, new[k]) for k in ("pmid", "doi", "pmcid") if new.get(k)]
            base = next((by_key[k] for k in keys if k in by_key), None)
            if base is None:
                base = {"sources": []}
                records.append(base)
                added += 1
            merge(base, new, source)
            for k in ("pmid", "doi", "pmcid"):
                if base.get(k):
                    by_key.setdefault((k, base[k]), base)
        log("%-10s added %5d new works (running total %d)" % (source, added, len(records)))

    order = {"core": 0, "related": 1, "mention": 2}
    records = [finish(r) for r in records]
    # Works that share a title but not an identifier are usually a preprint and
    # its published version, or a conference abstract and the later paper. They
    # are kept as separate records and cross-linked.
    by_title = collections.defaultdict(list)
    for r in records:
        key = re.sub(r"[^a-z0-9]+", "", (r.get("title") or "").lower())
        if len(key) >= 25:
            by_title[key].append(r["id"])
    for r in records:
        key = re.sub(r"[^a-z0-9]+", "", (r.get("title") or "").lower())
        r["same_title_ids"] = [i for i in by_title.get(key, []) if i != r["id"]]
    records.sort(key=lambda r: (order[r["tier"]], -(r["year"] or 0), r["id"]))
    write_jsonl(CATALOG / "papers.jsonl", records)

    def count(items):
        return dict(collections.Counter(items).most_common())

    core = [r for r in records if r["tier"] == "core"]
    stats = {
        "built_at": now(),
        "total": len(records),
        "by_tier": count(r["tier"] for r in records),
        "by_source": count(s for r in records for s in r["sources"]),
        "single_source_only": count(r["sources"][0] for r in records if len(r["sources"]) == 1),
        "by_focus": count(r["focus"] for r in records if r["focus"]),
        "open_access": {t: sum(1 for r in records if r["tier"] == t and r["is_oa"]) for t in order},
        "fulltext_in_europepmc": {t: sum(1 for r in records if r["tier"] == t and r["in_epmc"] and r["is_oa"] and r["pmcid"])
                                  for t in order},
        "core": {
            "with_abstract": sum(r["has_abstract"] for r in core),
            "named_in_title": sum(r["named_in_title"] for r in core),
            "case_reports": sum(r["is_case_report"] for r in core),
            "animal_studies": sum(r["is_animal"] for r in core),
            "by_type": count(t for r in core for t in (r["pub_types"] or ["unknown"])[:1]),
            "reviews": sum(r["is_review"] for r in core),
            "year_range": [min((r["year"] for r in core if r["year"]), default=None),
                           max((r["year"] for r in core if r["year"]), default=None)],
            "by_decade": count("%ds" % (r["year"] // 10 * 10) for r in sorted(core, key=lambda r: r["year"] or 0) if r["year"]),
            "by_site_tag": count(s for r in core for s in r["sites"]),
            "no_site_tag": sum(1 for r in core if not r["sites"]),
            "by_language": count((r["language"] or "unknown") for r in core),
            "top_journals": dict(collections.Counter(r["journal"] for r in core if r["journal"]).most_common(15)),
        },
    }
    write_json(CATALOG / "stats.json", stats)
    log("catalog: %d works -> %s" % (len(records), stats["by_tier"]))
    return stats


if __name__ == "__main__":
    build()
