"""Second-pass sources: grants, datasets, standard codes, and two more indexes.

    python harvest/extras.py              run every step
    python harvest/extras.py grants geo   run the named steps

Steps:
    grants      NIH RePORTER projects                 -> data/catalog/grants.jsonl
    geo         NCBI GEO series and BioProjects       -> data/catalog/datasets.jsonl
    codes       NCI Thesaurus, OncoTree, MeSH, Wikidata -> data/catalog/terminology.json
    s2          Semantic Scholar bulk search          -> data/raw/semanticscholar/
    openalex    the skin and adnexal OpenAlex query only (fits the keyless daily quota)

Each step is independent: a failure in one is reported and the rest still run.
"""

import json
import sys
import time
import traceback
from pathlib import Path
from urllib.parse import quote, urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import CATALOG, RAW, TOOL, fetch, log, now, read_gz, write_gz, write_json, write_jsonl  # noqa: E402
from queries import OPENALEX_QUERIES  # noqa: E402

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TERM = '"myoepithelial carcinoma" OR "malignant myoepithelioma" OR myoepithelioma OR "myoepithelial tumor"'


def grants():
    """NIH-funded projects whose title, abstract or terms name the disease."""
    out = RAW / "reporter"
    results, offset = [], 0
    while True:
        body = json.dumps({
            "criteria": {"advanced_text_search": {
                "operator": "advanced", "search_field": "projecttitle,terms,abstracttext",
                "search_text": '"myoepithelial carcinoma" OR "malignant myoepithelioma" OR myoepithelioma'}},
            "offset": offset, "limit": 500,
        }).encode()
        page = json.loads(fetch("https://api.reporter.nih.gov/v2/projects/search", data=body,
                                headers={"Content-Type": "application/json", "Accept": "application/json"},
                                min_interval=1.0))
        results += page.get("results", [])
        offset += 500
        if offset >= page.get("meta", {}).get("total", 0):
            break
    write_gz(out / "projects.json.gz", json.dumps(results).encode())
    write_json(out / "query.json", {"count": len(results), "fetched_at": now()})
    slim = []
    for r in results:
        org = r.get("organization") or {}
        slim.append({
            "project_num": r.get("project_num"),
            "core_project_num": r.get("core_project_num"),
            "title": (r.get("project_title") or "").strip(),
            "fiscal_year": r.get("fiscal_year"),
            "organization": (org.get("org_name") or "").title(),
            "state": org.get("org_state") or "",
            "investigators": [(p.get("full_name") or "").title() for p in r.get("principal_investigators") or []],
            "agency": (r.get("agency_ic_admin") or {}).get("abbreviation") or "",
            "award_amount": r.get("award_amount"),
            "start": (r.get("project_start_date") or "")[:10],
            "end": (r.get("project_end_date") or "")[:10],
            "names_in_title": "myoepitheli" in (r.get("project_title") or "").lower(),
            "abstract": r.get("abstract_text") or "",
            "url": r.get("project_detail_url") or "",
        })
    slim.sort(key=lambda g: (-(g["fiscal_year"] or 0), g["project_num"] or ""))
    write_jsonl(CATALOG / "grants.jsonl", slim)
    log("grants: %d NIH project-years, %d distinct projects"
        % (len(slim), len({g["core_project_num"] for g in slim})))


def _esearch(db, term):
    url = EUTILS + "esearch.fcgi?" + urlencode({"db": db, "term": term, "retmode": "json", "retmax": 1000, "tool": TOOL})
    return json.loads(fetch(url, min_interval=0.5))["esearchresult"].get("idlist", [])


def _esummary(db, ids):
    docs = []
    for start in range(0, len(ids), 200):
        url = EUTILS + "esummary.fcgi?" + urlencode(
            {"db": db, "id": ",".join(ids[start:start + 200]), "retmode": "json", "tool": TOOL})
        result = json.loads(fetch(url, min_interval=0.5)).get("result", {})
        docs += [result[uid] for uid in result.get("uids", [])]
    return docs


def geo():
    """Expression and sequencing datasets: GEO series and BioProjects."""
    out = RAW / "geo"
    gds = _esummary("gds", _esearch("gds", TERM))
    projects = _esummary("bioproject", _esearch("bioproject", TERM))
    write_gz(out / "gds.json.gz", json.dumps(gds).encode())
    write_gz(out / "bioproject.json.gz", json.dumps(projects).encode())
    write_json(out / "query.json", {"term": TERM, "gds": len(gds), "bioproject": len(projects), "fetched_at": now()})
    rows = []
    for d in gds:
        if d.get("entrytype") != "GSE":      # keep whole studies, not single samples
            continue
        text = "%s %s" % (d.get("title", ""), d.get("summary", ""))
        rows.append({
            "source": "GEO", "accession": d.get("accession"), "title": d.get("title", ""),
            "summary": d.get("summary", ""), "type": d.get("gdstype", ""), "organism": d.get("taxon", ""),
            "samples": d.get("n_samples"), "date": d.get("pdat", ""),
            "pubmed_ids": [str(x) for x in d.get("pubmedids") or []],
            "names_disease": "myoepithelial carcinoma" in text.lower() or "malignant myoepithelioma" in text.lower(),
            "url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=%s" % d.get("accession"),
        })
    for d in projects:
        text = "%s %s" % (d.get("project_title", ""), d.get("project_description", ""))
        rows.append({
            "source": "BioProject", "accession": d.get("project_acc"), "title": d.get("project_title", ""),
            "summary": d.get("project_description", ""), "type": d.get("project_data_type", ""),
            "organism": d.get("organism_name", ""), "samples": None, "date": (d.get("registration_date") or "")[:10],
            "pubmed_ids": [],
            "names_disease": "myoepithelial carcinoma" in text.lower() or "malignant myoepithelioma" in text.lower(),
            "url": "https://www.ncbi.nlm.nih.gov/bioproject/%s" % d.get("project_acc"),
        })
    rows.sort(key=lambda r: (not r["names_disease"], r["source"], r["accession"] or ""))
    write_jsonl(CATALOG / "datasets.jsonl", rows)
    log("datasets: %d GEO series (of %d GEO records), %d BioProjects, %d name the disease"
        % (sum(r["source"] == "GEO" for r in rows), len(gds), len(projects), sum(r["names_disease"] for r in rows)))


def codes():
    """How each standard vocabulary names and codes the disease."""
    out = RAW / "terminology"
    found = {"fetched_at": now(), "systems": {}}

    ncit = json.loads(fetch("https://api-evsrest.nci.nih.gov/api/v1/concept/ncit/search?" + urlencode(
        {"term": "myoepithelial", "type": "contains", "include": "synonyms,definitions", "pageSize": 100})))
    write_gz(out / "ncit.json.gz", json.dumps(ncit).encode())
    found["systems"]["NCI Thesaurus"] = [
        {"code": c["code"], "name": c["name"],
         "definition": next((d.get("definition") for d in c.get("definitions") or [] if d.get("source") == "NCI"), ""),
         "synonyms": sorted({s["name"] for s in c.get("synonyms") or [] if s.get("name")})[:12],
         "url": "https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&code=%s" % c["code"]}
        for c in ncit.get("concepts", [])
        if "myoepitheli" in c["name"].lower() and "mouse" not in c["name"].lower()]

    onco = json.loads(fetch("https://oncotree.mskcc.org/api/tumorTypes/search/name/myoepithelial?exactMatch=false"))
    write_gz(out / "oncotree.json.gz", json.dumps(onco).encode())
    found["systems"]["OncoTree"] = [
        {"code": t.get("code"), "name": t.get("name"), "main_type": t.get("mainType"), "tissue": t.get("tissue"),
         "parent": t.get("parent"), "url": "https://oncotree.mskcc.org/?field=CODE&search=%s" % t.get("code")}
        for t in onco]

    mesh = json.loads(fetch("https://id.nlm.nih.gov/mesh/lookup/descriptor?" + urlencode(
        {"label": "Myoepithelioma", "match": "exact", "limit": 5})))
    write_gz(out / "mesh.json.gz", json.dumps(mesh).encode())
    found["systems"]["MeSH"] = [{"code": m["resource"].rsplit("/", 1)[-1], "name": m["label"], "url": m["resource"]}
                                for m in mesh]

    wd = json.loads(fetch("https://www.wikidata.org/w/api.php?" + urlencode(
        {"action": "wbsearchentities", "search": "myoepithelial carcinoma", "language": "en", "format": "json", "limit": 5})))
    write_gz(out / "wikidata.json.gz", json.dumps(wd).encode())
    found["systems"]["Wikidata"] = [
        {"code": e["id"], "name": e.get("label"), "definition": e.get("description") or "", "url": e.get("concept_uri")}
        for e in wd.get("search", []) if (e.get("description") or "").startswith("carcinoma")]

    try:    # the ontology lookup service is slow; it is a bonus, not a requirement
        ols = json.loads(fetch("https://www.ebi.ac.uk/ols4/api/search?" + urlencode(
            {"q": "myoepithelial carcinoma", "rows": 60, "ontology": "mondo,doid,ordo,efo",
             "fieldList": "obo_id,label,ontology_name,description"}), retries=2, timeout=120))
        write_gz(out / "ols.json.gz", json.dumps(ols).encode())
        for doc in ols["response"]["docs"]:
            if "myoepitheli" not in (doc.get("label") or "").lower():
                continue
            found["systems"].setdefault(doc["ontology_name"].upper(), []).append(
                {"code": doc.get("obo_id"), "name": doc.get("label"),
                 "definition": " ".join(doc.get("description") or [])[:400]})
    except Exception as err:
        log("codes: ontology lookup skipped (%s)" % str(err)[:80])

    write_json(CATALOG / "terminology.json", found)
    log("codes: %s" % ", ".join("%s %d" % (k, len(v)) for k, v in found["systems"].items()))


def s2():
    """Semantic Scholar bulk search: one more index to catch works the others miss."""
    out = RAW / "semanticscholar"
    fields = "title,year,venue,externalIds,publicationTypes,openAccessPdf,citationCount,authors,publicationDate"
    token, pages, total = None, [], 0
    while True:
        params = {"query": '"myoepithelial carcinoma" | "malignant myoepithelioma"', "fields": fields}
        if token:
            params["token"] = token
        raw = fetch("https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urlencode(params, quote_via=quote),
                    min_interval=3.0, retries=6, timeout=120)
        page = json.loads(raw)
        pages.append(raw)
        total += len(page.get("data") or [])
        token = page.get("token")
        if not token or not page.get("data"):
            break
    for old in out.glob("page_*.json.gz"):
        old.unlink()
    for i, raw in enumerate(pages):
        write_gz(out / ("page_%04d.json.gz" % i), raw)
    write_json(out / "query.json", {"count": total, "fetched_at": now()})
    log("semantic scholar: %d records" % total)


def s2_parse():
    """Yield normalised records from the Semantic Scholar pages (used by build_catalog)."""
    for path in sorted((RAW / "semanticscholar").glob("page_*.json.gz")):
        for r in json.loads(read_gz(path)).get("data") or []:
            ids = r.get("externalIds") or {}
            pmc = str(ids.get("PubMedCentral") or "")
            pdf = (r.get("openAccessPdf") or {}).get("url") or ""
            yield {
                "s2_id": r.get("paperId"),
                "pmid": str(ids["PubMed"]) if ids.get("PubMed") else None,
                "pmcid": ("PMC" + pmc.replace("PMC", "")) if pmc else None,
                "doi": (ids.get("DOI") or "").lower() or None,
                "title": " ".join((r.get("title") or "").split()),
                "abstract": "",
                "authors": [a.get("name") or "" for a in r.get("authors") or []],
                "affiliation": "",
                "journal": r.get("venue") or "",
                "year": r.get("year"),
                "date": r.get("publicationDate") or "",
                "language": "",
                "pub_types": r.get("publicationTypes") or [],
                "mesh": [], "keywords": [],
                "is_oa": bool(pdf),
                "oa_url": pdf,
                "cited_by": r.get("citationCount"),
            }


def openalex_skin():
    """Fetch only the skin and adnexal OpenAlex query and add its pages to the raw set."""
    import os
    import urllib.error
    label, param, value = next(q for q in OPENALEX_QUERIES if q[0] == "cutaneous_title_abstract")
    fields = ("id,doi,title,publication_year,publication_date,type,language,ids,primary_location,"
              "open_access,best_oa_location,authorships,cited_by_count,abstract_inverted_index")
    key = os.environ.get("OPENALEX_API_KEY", "")
    pages, got, total, page_no = [], 0, None, 1
    while total is None or got < min(total, 10000):
        params = {param: value, "per-page": 200, "page": page_no, "select": fields}
        if key:
            params["api_key"] = key
        try:
            raw = fetch("https://api.openalex.org/works?" + urlencode(params), min_interval=0.3, retries=3, timeout=180)
        except urllib.error.HTTPError as err:
            log("openalex skin: stopped on HTTP %s at page %d, nothing saved" % (err.code, page_no))
            return
        page = json.loads(raw)
        total = page.get("meta", {}).get("count", 0)
        if not page.get("results"):
            break
        pages.append(raw)
        got += len(page["results"])
        page_no += 1
    out = RAW / "openalex"
    for old in out.glob("page_skin_*.json.gz"):
        old.unlink()
    for i, raw in enumerate(pages):
        write_gz(out / ("page_skin_%04d.json.gz" % i), raw)
    log("openalex skin: %d of %s works" % (got, total))


def models():
    """Cell lines derived from myoepithelial tumors, from Cellosaurus."""
    raw = fetch("https://api.cellosaurus.org/search/cell-line?" + urlencode(
        {"q": "di:myoepithelial OR di:myoepithelioma", "format": "json", "rows": 200,
         "fields": "id,ac,di,ox,ca,sx,ag,derived-from-site,rx"}), timeout=120)
    write_gz(RAW / "cellosaurus" / "lines.json.gz", raw)
    rows = []
    for line in json.loads(raw).get("Cellosaurus", {}).get("cell-line-list", []):
        def values(key):
            return [x.get("value") or x.get("label") or "" for x in line.get(key) or []]
        accession = (values("accession-list") or [""])[0]
        diseases = values("disease-list")
        rows.append({
            "name": (values("name-list") or [""])[0], "accession": accession, "diseases": diseases,
            "category": line.get("category") or "", "species": (values("species-list") or [""])[0],
            "sex": line.get("sex") or "", "age": line.get("age") or "",
            "names_carcinoma": any("carcinoma" in d.lower() or "malignant" in d.lower() for d in diseases),
            "epithelial_myoepithelial": any("epithelial-myoepithelial" in d.lower() or "epithelial myoepithelial" in d.lower()
                                            for d in diseases),
            "url": "https://www.cellosaurus.org/%s" % accession,
        })
    write_jsonl(CATALOG / "models.jsonl", rows)
    log("models: %d cell lines" % len(rows))


def links():
    """Check that each organization in organizations.json still answers at its address."""
    import re
    import urllib.request
    orgs = json.loads((Path(__file__).resolve().parent / "organizations.json").read_text(encoding="utf-8"))
    checked = []
    for org in orgs:
        ok, title = False, ""
        try:
            req = urllib.request.Request(org["url"], headers={"User-Agent": "Mozilla/5.0 (compatible; myo-corpus/0.1)"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                page = resp.read(300000).decode("utf-8", "replace")
            found = re.search(r"<title[^>]*>(.*?)</title>", page, re.S | re.I)
            title = " ".join(found.group(1).split()) if found else ""
            ok = org["expect"].lower() in page.lower()
        except Exception as err:
            title = "not reached: %s" % str(err)[:60]
        checked.append(dict(org, ok=ok, page_title=title[:120], checked=now()[:10]))
        time.sleep(0.5)
    write_json(CATALOG / "organizations.json", checked)
    log("links: %d of %d organizations answered and matched" % (sum(o["ok"] for o in checked), len(checked)))


STEPS = {"grants": grants, "geo": geo, "codes": codes, "s2": s2, "openalex": openalex_skin,
         "models": models, "links": links}

if __name__ == "__main__":
    wanted = sys.argv[1:] or list(STEPS)
    for name in wanted:
        try:
            STEPS[name]()
        except Exception:
            log("%s FAILED:\n%s" % (name, traceback.format_exc(limit=2)))
        time.sleep(1)
