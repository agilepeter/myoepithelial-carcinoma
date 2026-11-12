"""Prepare the batches that a model reads and extracts from.

    python harvest/prep_reading.py <output folder>

The rule-based passes in derive.py only match words. These batches are for a
careful reader (a model, checked by a person) to extract what the texts say:

    cases_batch_N.jsonl     single-patient case reports, title and abstract
    skin_fulltext/          full text of skin case reports held on disk
    drugs_input.jsonl       papers and trials that mention drug treatment
    trials_input.jsonl      open trials, with eligibility text
    stains_input.jsonl      series that report immunostain rates
    lookalikes_input.jsonl  papers on differential diagnosis
    verify_input.json       each cited source with the sentences that cite it
    essentials_en.json      the core patient text, for translation
"""

import gzip
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "site"))

from common import CATALOG, FULLTEXT, ROOT, read_jsonl, write_json, write_jsonl  # noqa: E402

DRUG = re.compile(r"chemother|doxorubicin|adriamycin|cisplatin|carboplatin|ifosfamide|paclitaxel|docetaxel|etoposide|vincristine"
                  r"|cyclophosphamide|gemcitabine|methotrexate|5-fluorouracil|capecitabine|pembrolizumab|nivolumab|ipilimumab"
                  r"|immunother|checkpoint|targeted therap|tyrosine kinase|pazopanib|imatinib|sunitinib|apatinib|anlotinib|lenvatinib"
                  r"|axitinib|sorafenib|larotrectinib|entrectinib|tazemetostat|trastuzumab|bevacizumab|everolimus|olaparib|\binhibitor", re.I)
STAIN = re.compile(r"S-?100|calponin|\bp63\b|SOX-?10|cytokeratin|keratin|\bEMA\b|GFAP|smooth muscle actin|\bSMA\b|INI1|SMARCB1|vimentin", re.I)
RATE = re.compile(r"\d+\s*%|\d+\s+of\s+\d+|\d+/\d+")
MIMIC = re.compile(r"differential diagnos|mimic|pitfall|misdiagnos|distinguish|masquerad|confused with|resembl", re.I)
LIVE = {"RECRUITING", "NOT_YET_RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION"}


def plain_text(pmcid, limit=45000):
    raw = gzip.open(FULLTEXT / ("%s.xml.gz" % pmcid), "rb").read().decode("utf-8", "replace")
    body = raw[raw.find("<body"):raw.find("</body>")] if "<body" in raw else raw
    body = re.sub(r"<(xref|sup)[^>]*>.*?</\1>", "", body, flags=re.S)
    body = re.sub(r"</(p|title|sec|td|tr|li)>", "\n", body)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", text)).strip()[:limit]


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    papers = read_jsonl(CATALOG / "papers.jsonl")
    by_id = {p["id"]: p for p in papers}
    have = {f.name[:-7] for f in FULLTEXT.glob("PMC*.xml.gz")}
    core = [p for p in papers if p["tier"] == "core" and not p["is_animal"]]

    cases = [c for c in read_jsonl(CATALOG / "cases.jsonl") if by_id[c["id"]]["has_abstract"]]
    rows = [{"id": c["id"], "year": c["year"], "title": c["title"], "abstract": by_id[c["id"]]["abstract"]} for c in cases]
    size = -(-len(rows) // 4)
    for n in range(4):
        write_jsonl(out / ("cases_batch_%d.jsonl" % (n + 1)), rows[n * size:(n + 1) * size])

    (out / "skin_fulltext").mkdir(exist_ok=True)
    skin = []
    for p in core:
        if p["focus"] == "primary" and p["named_in_title"] and p["pmcid"] in have:
            (out / "skin_fulltext" / ("%s.txt" % p["pmcid"])).write_text(plain_text(p["pmcid"]), encoding="utf-8")
            skin.append({"id": p["id"], "pmcid": p["pmcid"], "year": p["year"], "title": p["title"],
                         "file": "skin_fulltext/%s.txt" % p["pmcid"]})
    write_jsonl(out / "skin_input.jsonl", skin)

    drugs = [{"id": p["id"], "year": p["year"], "kind": "case report" if p["is_case_report"] else "study",
              "title": p["title"], "abstract": p["abstract"]}
             for p in core if p["has_abstract"] and DRUG.search(p["abstract"])]
    trials = read_jsonl(CATALOG / "trials.jsonl")
    for t in trials:
        if t["names_myoepithelial"]:
            drugs.append({"id": t["nct_id"], "year": (t["start"] or "")[:4], "kind": "trial", "title": t["title"],
                          "abstract": "Status: %s. Interventions: %s. %s" % (t["status"], "; ".join(t["interventions"]), t["summary"][:900])})
    write_jsonl(out / "drugs_input.jsonl", drugs)

    live = [t for t in trials if t["status"] in LIVE and t["study_type"] == "INTERVENTIONAL"]
    write_jsonl(out / "trials_input.jsonl", [
        {"nct_id": t["nct_id"], "title": t["title"], "status": t["status"], "phases": t["phases"], "conditions": t["conditions"][:12],
         "interventions": t["interventions"][:8], "countries": t["countries"][:12], "names_myoepithelial": t["names_myoepithelial"],
         "eligibility": t["eligibility"][:2600]} for t in live])

    series = [p for p in core if p["has_abstract"] and not p["is_case_report"]]
    stains = [p for p in series if len(STAIN.findall(p["abstract"])) >= 2 and RATE.search(p["abstract"])]
    write_jsonl(out / "stains_input.jsonl", [{"id": p["id"], "year": p["year"], "title": p["title"], "abstract": p["abstract"]}
                                             for p in sorted(stains, key=lambda p: -(p["cited_by"] or 0))[:90]])
    mimics = [p for p in core if p["has_abstract"] and MIMIC.search(p["abstract"])]
    write_jsonl(out / "lookalikes_input.jsonl", [{"id": p["id"], "year": p["year"], "title": p["title"], "abstract": p["abstract"]}
                                                 for p in sorted(mimics, key=lambda p: -(p["cited_by"] or 0))[:110]])

    import content as C
    import content_pages as P
    source = (ROOT / "site" / "content.py").read_text(encoding="utf-8") + (ROOT / "site" / "content_pages.py").read_text(encoding="utf-8")
    source = re.sub(r"\s*\n\s*", " ", source)
    (out / "verify_fulltext").mkdir(exist_ok=True)
    checks = []
    for key, ref in C.REFS.items():
        if isinstance(ref, dict):
            continue
        p = by_id.get(ref)
        claims = sorted({re.sub(r"<[^>]+>", "", s).strip(" \"',()") for s in
                         re.findall(r"[^.>\"]*?[^.>\"]{12,}?\[\[%s\]\][^.<\"]{0,80}" % re.escape(key), source)})
        full = ""
        if p["pmcid"] in have:
            full = "verify_fulltext/%s.txt" % p["pmcid"]
            (out / full).write_text(plain_text(p["pmcid"], 60000), encoding="utf-8")
        checks.append({"key": key, "id": p["id"], "title": p["title"], "year": p["year"], "doi": p["doi"], "pmcid": p["pmcid"],
                       "is_oa": p["is_oa"], "oa_url": p["oa_url"], "full_text_file": full, "abstract": p["abstract"], "claims": claims})
    write_json(out / "verify_input.json", checks)

    def strip(text):
        return html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"\[\[\w+\]\]", "", text))).strip()
    essentials = {"title": "Myoepithelial carcinoma: the essentials",
                  "intro": "A short version of the main reference, for patients and families. The full reference, with its "
                           "sources, is in English.",
                  "not_advice": "This is a summary of published research, compiled by a patient. It is not medical advice.",
                  "h_facts": "Key facts", "h_first": "If you were just diagnosed", "h_plan": "A plan for the first 30 days",
                  "h_questions": "Questions to take to your next appointment", "h_numbers": "Survival figures",
                  "numbers": "In the U.S. National Cancer Database (336 patients, all body sites), 79.4% were alive at 2 years, "
                             "66.5% at 5 years and 52.0% at 10 years. In 691 patients pooled from the published literature, median "
                             "overall survival was 167 months, about 14 years. These are group figures and do not predict one "
                             "person's course.",
                  "own": "Your doctors treat the disease, but you have to run the project. With a disease this rare, many of the "
                         "people treating you may be seeing it for the first time. Arrive prepared, ask until you understand, and "
                         "keep your own records.",
                  "full_link": "Read the full reference in English"}
    for n, (label, text) in enumerate(C.QUICK, 1):
        essentials["fact_%d_label" % n] = label
        essentials["fact_%d" % n] = strip(text)
    for n, (label, text) in enumerate(C.FIRST_THREE, 1):
        essentials["first_%d_title" % n] = label
        essentials["first_%d" % n] = strip(text)
    for n, (label, text) in enumerate(C.PLAN, 1):
        essentials["plan_%d_title" % n] = label
        essentials["plan_%d" % n] = strip(text)
    for n, text in enumerate(C.QUESTIONS, 1):
        essentials["question_%d" % n] = text
    write_json(out / "essentials_en.json", essentials)

    print("cases with abstract: %d in 4 batches of %d | skin full texts: %d | drug records: %d | open trials: %d"
          % (len(rows), size, len(skin), len(drugs), len(live)))
    print("stain series: %d | look-alike papers: %d | sources to verify: %d (%d with full text on disk) | essentials strings: %d"
          % (min(len(stains), 90), min(len(mimics), 110), len(checks), sum(bool(c["full_text_file"]) for c in checks), len(essentials)))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
