# Collection plan

The map of where knowledge about myoepithelial carcinoma lives, and what has
been collected. Update the status column whenever a source is harvested.

Status: **done** = harvested and in the repo. **partial** = started.
**todo** = not started.

## 1. Published literature (index records and abstracts)

| Source | What it adds | Status |
| --- | --- | --- |
| PubMed | The biomedical index; MeSH terms, publication types | done, 3,942 records |
| Europe PMC | Preprints, full-text search hits, open-access flags | done, 5,840 records |
| OpenAlex | Books, theses, conference abstracts, regional journals, citation counts | done, 7,996 works in the catalog, including the skin and adnexal query |
| Crossref | DOIs not in the above | todo, low priority |
| Semantic Scholar | Citation graph, extra abstracts | done, 1,949 records. 287 works were in no other index, 90 of them naming the disease. |
| Google Scholar | Widest coverage, no API | todo, manual spot checks only |
| Scopus, Web of Science, Embase | Subscription indexes; Embase is strong on conference abstracts | todo, needs access |

## 2. Full text

| Source | Status |
| --- | --- |
| PMC full-text XML via NCBI | done, 2,882 papers (208 core). 798 more have a PMC ID but no downloadable body. |
| Open-access PDFs outside PMC (OpenAlex gives the URLs) | todo |
| Paywalled papers | todo. List them, then get them through a library, purchase, or author request. No scraping. |
| Pre-1990 papers with no abstract | todo, likely needs library scans |

## 3. Non-English literature

116 of the core works are not in English (Chinese, German, Japanese,
French, Spanish and others). Regional databases will hold more.

| Source | Status |
| --- | --- |
| CNKI, Wanfang (Chinese) | todo |
| J-STAGE, Ichushi (Japanese) | todo |
| KoreaMed | todo |
| SciELO, LILACS (Latin America) | todo |
| eLibrary.ru (Russian) | todo |

## 4. Clinical trials

| Source | Status |
| --- | --- |
| ClinicalTrials.gov | done, 527 trials, 13 name myoepithelial tumours |
| WHO ICTRP (aggregates non-US registries) | todo |
| EU CTIS and EudraCT | todo |
| ISRCTN, ChiCTR, jRCT, ANZCTR | todo |
| Basket and tumour-agnostic trials that would accept this diagnosis | todo, needs eligibility review |

## 5. Molecular and genomic data

| Source | Status |
| --- | --- |
| cBioPortal (MSK-IMPACT and other studies, by OncoTree code) | todo |
| AACR Project GENIE | todo |
| GEO and BioProject (expression and sequencing datasets) | done, 12 GEO series and 7 BioProjects, 8 naming the disease. SRA runs not listed yet. |
| COSMIC | todo |
| Fusion databases (EWSR1, FUS, PLAG1, HMGA2 partners) | todo |
| Cell lines and patient-derived models (Cellosaurus, cureMEC) | todo |

## 6. Epidemiology

| Source | Status |
| --- | --- |
| SEER (ICD-O-3 morphology 8982/3) | todo |
| National Cancer Database studies | in the catalog as papers |
| RARECARE / RARECAREnet (Europe) | todo |
| National registries (Japan, Nordic, Netherlands) | todo |

## 7. Reference works and guidelines

| Source | Status |
| --- | --- |
| WHO Classification of Tumours (Head and Neck; Soft Tissue and Bone; Skin; Breast) | todo, paywalled |
| NCCN, ESMO, ASCO guidelines (salivary gland, soft-tissue sarcoma) | todo |
| NCI Thesaurus, OncoTree, MONDO, Disease Ontology, MeSH, Wikidata | done, in `terminology.json`. GARD, Orphanet and ICD-11 still todo. |
| Pathology references (PathologyOutlines, AFIP fascicles) | todo |

## 8. Grey literature

| Source | Status |
| --- | --- |
| Conference abstracts (ASCO, ESMO, AACR, USCAP, CTOS) | partial, via OpenAlex |
| Theses and dissertations | partial, via OpenAlex (about 110) |
| Patents | todo |
| Grants (NIH RePORTER, Europe PMC grants, CDMRP) | partial. NIH RePORTER done: 4 projects mention it, none in the title. |
| FDA and EMA documents (orphan designations, approvals that list it) | todo |

## 9. People and organisations

| Item | Status |
| --- | --- |
| Authors ranked by number of core papers | can be derived from the catalog |
| Treating centres and their case volumes | todo |
| cureMEC: The Myoepithelial Carcinoma Project (patient-driven, launched 2022) | todo, see notes/first-findings.md |
| Other foundations (Rare Cancer Research Foundation, salivary and sarcoma groups) | todo |

## 10. Patient experience

| Source | Status |
| --- | --- |
| Peter's own published writing | 2 posts, linked from the site. |
| Other public patient accounts, blogs, forums | todo. Privacy rule: public posts only, link rather than copy. |

## 11. The case registry

The equivalent of the directory of every named Saddington: one row for every
patient with myoepithelial carcinoma described in the literature. Site, age,
sex, size, margins, molecular findings, treatment, recurrence, metastasis,
follow-up, outcome, and the paper it came from.

Status: done from abstracts. 479 single-patient reports are in
`data/catalog/cases.jsonl`, 382 of them read by a model. Reading the cases in
full text, starting with the skin cases, is still to do.

## 12. The public page

A compendium page in the style of staas.fund/saddington, built from the above.
Status: done. Live since 2026-11-11 at
https://staas.fund/myoepithelial-carcinoma/.
