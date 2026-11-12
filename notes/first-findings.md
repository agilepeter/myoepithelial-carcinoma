# First findings from the catalog

Written 2026-11-11 from titles and abstracts in `data/catalog/`. Nothing here
has been checked against full text yet. Not medical advice.

## Size of the literature

- 9,470 distinct works after merging PubMed, Europe PMC and OpenAlex.
- 1,276 are "core": the title or abstract names myoepithelial carcinoma or
  malignant myoepithelioma. 744 of those name it in the title.
- 3,876 are "related": benign myoepithelioma, myoepithelial tumours,
  epithelial-myoepithelial carcinoma (a different diagnosis), and the skin
  neighbourhood (mixed tumours of the skin, skin adnexal carcinomas).
- 4,318 are "mention": the disease appears only in the body of the paper.
- Core works run from 1957 to 2026. Over half were published since 2015.
- About 635 core works are flagged as case reports and 48 as animal studies
  (keyword heuristics). 116 are not in English.

## How much of it we hold in full

- Full text is on disk for 2,882 works: 208 core, 600 related, 2,074 mention.
- Of the 1,068 core works without full text, 419 are marked open access
  somewhere else (usually a PDF on the publisher's site) and 649 are not open
  access.
- 160 core works have no abstract in any index, mostly older papers.

## Closest to Peter's diagnosis

Peter's report reads "adnexal carcinoma, consistent with myoepithelial
carcinoma" of the skin (the report is quoted on the site). 242 works are tagged
`focus: primary` and listed in `notes/reading-list-skin.md`. Ones to read first:

- `pmid:41239844` (2026) TRPS1::PLAG1 fusion in a primary cutaneous myoepithelial
  carcinoma, with a literature review. Full text is open access.
- `pmid:41342886` (2026) Michal et al., the methylation study below, which
  separates adnexal PLAG1-rearranged tumours from FET-rearranged ones.
- `pmid:39539473` (2025) Primary cutaneous myoepithelial carcinoma in the axilla
  with lymph-node metastasis. Full text is open access.
- `pmid:40110023` (2025) Myoepithelial carcinoma of the skin, case report. Full
  text is open access.
- `pmid:41392389` (2026) Cutaneous myoepithelial carcinoma arising within
  syringocystadenoma papilliferum.
- `pmid:21725291` (2011) EWSR1 rearrangement in a subset of cutaneous
  myoepithelial tumours, 18 cases.
- `pmid:14745720` (2004) Cutaneous myoepithelioma, 14 cases.
- `pmid:19125803` (2009) Recurrent cutaneous myoepithelioma treated with Mohs
  micrographic surgery, case report and review.

## The paper cited in Peter's post

"Medical Oncology volume 37, Article 13 (2020)" is `pmid:31879796`:
Chamberlain F, Cojocaru E, Scaranti M, et al. *Adult soft tissue myoepithelial
carcinoma: treatment outcomes and efficacy of chemotherapy.* A Royal Marsden
Sarcoma Unit series of 24 patients treated 1996 to 2019. The abstract reports
recurrence in 40 to 45% of tumours despite optimal treatment, and a median
progression-free survival of 9.3 months on first-line chemotherapy. It is open
access.

Correction, 2026-11-11: the 40 to 45% recurrence figure is that paper's
background number. In the series itself 13 of 24 patients (54.2%) relapsed.

## A patient-led effort already exists

Two 2026 AACR abstracts (`doi:10.1158/1538-7445.am2026-6355`,
`doi:10.1158/1538-7445.fusionpositive26-a004`; authors Barber, Natale, Casaus,
Van Hare) describe **cureMEC: The Myoepithelial Carcinoma Project**, a
patient-driven nonprofit launched in 2022 that is building biospecimen
collections and preclinical models. The abstracts put incidence at 0.013 per
100,000. Worth contacting: their goal overlaps with this one.

## Recent work that looks important

- `pmid:41834073` Kashyap et al., *Oral Diseases* 2026. Exome and RNA sequencing
  of a 27-patient cohort.
- `pmid:41342886` Michal et al., *Clinical Cancer Research* 2026. DNA methylation
  profiling of 52 fusion-positive skin, soft-tissue and bone myoepithelial
  tumours, with a pooled outcome analysis of 185 cases.
- `pmid:40379813` Vasquez et al., *NPJ Precision Oncology* 2025. RNA-expression
  analysis used to pick a targeted drug for a 4-year-old patient.
- `doi:10.1200/jco.2026.44.16_suppl.e22590` Tandon et al., ASCO 2026 abstract.
  National Cancer Database study, 336 cases from 2004 to 2020.

## Landmark series (most cited)

- `pmid:12960802` Hornick and Fletcher 2003. 101 soft-tissue myoepithelial tumours.
- `pmid:10843278` Savera, Sloman and Huvos 2000. 25 salivary gland patients.
- `pmid:18043035` Gleason and Fletcher 2007. 29 soft-tissue cases in children.

## Where it occurs, by keyword tag

Among the 729 human works naming the disease in the title: salivary 426, soft tissue 139, other head and neck 124, lung 102, breast 101, skin 73, bone 65, paediatric 51, gynaecological 18. A work can carry several tags.

## Trials

13 ClinicalTrials.gov records name myoepithelial tumours. Several are false
hits or closed. Ones to read first:

- `NCT06244420` Istituto Ortopedico Rizzoli, observational, malignant
  myoepithelioma of bone and soft tissue. Completed.
- `NCT06239272` St. Jude NRSTS2021, phase 1/2. Recruiting.
- `NCT03874455` tazemetostat expanded access (no longer available) and
  `NCT05355753` CFT8634 for SMARCB1-altered tumours (terminated).
- `NCT00045669` imatinib and `NCT02857712` axitinib in salivary gland cancer.
  Both completed.

Another 514 trials are in `trials.jsonl`: salivary gland cancer trials and a
search for skin adnexal tumours. The skin search is noisy; the clearest hit is
`NCT03210935`, the French national database of rare dermatological cancers
(recruiting). Whether any trial would accept this diagnosis needs an
eligibility review.

## From the second sweep (2026-11-11)

- Semantic Scholar held 287 works that no other index had, 90 of them naming
  the disease. Most are case reports in small journals.
- NIH RePORTER lists four funded projects that mention the disease or
  myoepithelioma. None has it in the title. Their titles concern breast cancer
  and tumor profiling (`data/catalog/grants.jsonl`).
- Eight public datasets name the disease, including the raw reads behind the
  2017 genomic study (`PRJNA390610`) and a copy-number study of salivary
  myoepitheliomas (`GSE12951`).
- OncoTree has two codes, MYEC (salivary) and STMYEC (soft tissue). There is
  none for the skin form.
- The counts higher up this note are from the first sweep. Current totals are
  in the README.

## Most frequent authors in the core tier (PubMed records)

Katabi N (14), Fletcher CD (12), Michal M (11), Antonescu CR (11), Agaimy A (11),
Hornick JL (10), Bishop JA (10), Ghossein R (10). Common surnames with one
initial are unreliable in this count.
