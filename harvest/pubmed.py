"""PubMed: download every record matching PUBMED_QUERY and parse it.

    python harvest/pubmed.py        download into data/raw/pubmed/
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RAW, TOOL, fetch, log, now, read_gz, replace_batches, write_json  # noqa: E402
from queries import PUBMED_QUERY  # noqa: E402

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
OUT = RAW / "pubmed"
BATCH = 200


def download():
    body = urlencode(
        {"db": "pubmed", "term": PUBMED_QUERY, "retmode": "json", "retmax": 0,
         "usehistory": "y", "tool": TOOL}
    ).encode()
    res = json.loads(fetch(EUTILS + "esearch.fcgi", data=body))["esearchresult"]
    count = int(res["count"])
    log("PubMed: %d records match" % count)
    payloads = []
    for start in range(0, count, BATCH):
        url = EUTILS + "efetch.fcgi?" + urlencode(
            {"db": "pubmed", "query_key": res["querykey"], "WebEnv": res["webenv"],
             "retstart": start, "retmax": BATCH, "retmode": "xml", "tool": TOOL}
        )
        payloads.append(fetch(url))
        log("  fetched %d-%d" % (start + 1, min(start + BATCH, count)))
    replace_batches(OUT, "batch_*.xml.gz", payloads, "batch_%04d.xml.gz")
    write_json(OUT / "query.json", {"query": PUBMED_QUERY, "count": count, "fetched_at": now()})


def _text(el):
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def _year(article):
    for path in ("MedlineCitation/Article/Journal/JournalIssue/PubDate",
                 "MedlineCitation/Article/ArticleDate",
                 "PubmedData/History/PubMedPubDate[@PubStatus='pubmed']"):
        node = article.find(path)
        if node is None:
            continue
        year = _text(node.find("Year")) or _text(node.find("MedlineDate"))[:4]
        if year[:4].isdigit():
            month = _text(node.find("Month"))
            day = _text(node.find("Day"))
            return int(year[:4]), " ".join(x for x in (year[:4], month, day) if x)
    return None, ""


def _parse_article(node):
    cit = node.find("MedlineCitation")
    art = cit.find("Article") if cit is not None else None
    if art is None:
        return None
    abstract_parts = []
    for part in art.findall("Abstract/AbstractText"):
        label = part.get("Label")
        text = _text(part)
        if text:
            abstract_parts.append("%s: %s" % (label, text) if label else text)
    authors = []
    for au in art.findall("AuthorList/Author"):
        name = " ".join(x for x in (_text(au.find("LastName")), _text(au.find("Initials"))) if x)
        authors.append(name or _text(au.find("CollectiveName")))
    ids = {a.get("IdType"): _text(a) for a in node.findall("PubmedData/ArticleIdList/ArticleId")}
    year, date = _year(node)
    return {
        "pmid": _text(cit.find("PMID")),
        "pmcid": ids.get("pmc") or None,
        "doi": (ids.get("doi") or "").lower() or None,
        "title": _text(art.find("ArticleTitle")),
        "abstract": "\n".join(abstract_parts),
        "authors": [a for a in authors if a],
        "affiliation": _text(art.find("AuthorList/Author/AffiliationInfo/Affiliation")),
        "journal": _text(art.find("Journal/Title")),
        "year": year,
        "date": date,
        "language": ", ".join(_text(x) for x in art.findall("Language")),
        "pub_types": [_text(x) for x in art.findall("PublicationTypeList/PublicationType")],
        "mesh": [_text(x) for x in cit.findall("MeshHeadingList/MeshHeading/DescriptorName")],
        "keywords": [_text(x) for x in cit.findall("KeywordList/Keyword") if _text(x)],
    }


def _parse_book(node):
    doc = node.find("BookDocument")
    if doc is None:
        return None
    year = _text(doc.find("Book/PubDate/Year"))
    return {
        "pmid": _text(doc.find("PMID")),
        "pmcid": None,
        "doi": None,
        "title": _text(doc.find("ArticleTitle")) or _text(doc.find("Book/BookTitle")),
        "abstract": "\n".join(_text(x) for x in doc.findall("Abstract/AbstractText")),
        "authors": [],
        "affiliation": "",
        "journal": _text(doc.find("Book/BookTitle")),
        "year": int(year) if year.isdigit() else None,
        "date": year,
        "language": _text(doc.find("Language")),
        "pub_types": ["Book Chapter"],
        "mesh": [],
        "keywords": [],
    }


def parse():
    """Yield one normalised record per PubMed entry in the raw batches."""
    for path in sorted(OUT.glob("batch_*.xml.gz")):
        root = ET.fromstring(read_gz(path))
        for node in root:
            rec = _parse_article(node) if node.tag == "PubmedArticle" else _parse_book(node)
            if rec and rec["pmid"]:
                yield rec


if __name__ == "__main__":
    download()
    log("PubMed: parsed %d records" % sum(1 for _ in parse()))
