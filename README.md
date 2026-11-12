# Myoepithelial carcinoma: a reference to the published research

This is the public record of the reference at
<https://staas.fund/myoepithelial-carcinoma/>: the scripts that gather the
literature on a rare cancer, the catalog they produce, and the generator that
builds the site from it.

> **This is a scrubbed copy.** It is not the repository the work is done in.
> It is a copy made for the public record, with sensitive and restricted
> material taken out: the compiler's private notes and correspondence, his
> medical records, the abstracts and full text of other people's papers, and
> the raw downloads that contain them. What was left out, and why, is listed
> below. A script builds this copy from a list of files that are allowed in.
> Nothing else is copied. Each update replaces the copy as a whole, so the
> history here shows published versions and not the day-to-day work.

It is kept by Peter Saddington, who was diagnosed with myoepithelial carcinoma
in 2021. Why he built it is told at the end of the site's main page. Nothing
here is medical advice.

## What is here

| Path | What it holds |
| --- | --- |
| `data/catalog/papers.jsonl` | 10,435 works, one per line: identifiers, title, authors, journal, year, language, open-access status, and this project's tags. 1,366 of them name the disease in their title or abstract. |
| `data/catalog/trials.jsonl` | 527 registered trials from ClinicalTrials.gov. |
| `data/catalog/cases.jsonl` | 479 published single-patient reports, with age, sex, site, treatment and follow-up as far as each abstract states them. |
| `data/catalog/treatments.jsonl` | 205 reports of a drug treatment being given, and what was reported to happen. |
| `data/catalog/verification.jsonl` | 141 cited claims, each checked against its source, with the verdict. |
| `data/catalog/fulltext_held.jsonl` | The 2,904 papers held in full text, by PMC ID, with the license each one carries. The papers themselves are not here. |
| `data/catalog/` (the rest) | Centers, stains, look-alike tumors, trial eligibility, cell lines, grants, datasets, standard codes and organizations. |
| `data/read/` | What the model readers extracted, as they wrote it. |
| `harvest/` | The scripts that download from the public databases and build the catalog. |
| `site/` | The site generator and the text of the site. |
| `notes/` | The collection plan, the instructions given to the model readers, the source check, the first findings, and the reading list for the skin form. |

The records were last downloaded on 2026-11-11. This copy was made on
2026-11-12.

## What was left out

| Left out | Why |
| --- | --- |
| The abstracts of 8,340 papers, and of the grants | They belong to their publishers and authors. Each record says whether an abstract exists (`has_abstract`) and carries the PubMed ID or DOI where it can be read. |
| The full text of 2,904 papers | Their licenses differ. 1,484 carry a license that allows free redistribution and 1,420 do not. `harvest/fulltext.py` downloads them again from PubMed Central. |
| The raw downloads from each database | They contain the abstracts. The harvest scripts recreate them. |
| Email addresses | The databases print authors' addresses inside affiliations, and contacts inside trial and dataset records. They are replaced with "[address removed]". Each record links to its source, where the address was published. |
| The compiler's notes on his own case, his medical records and his correspondence | Private. What he has chosen to publish about his case is on the site. |
| Working files of the private repository | Session notes, plans and instructions that are not part of the record. |

## Build the site

Python 3.11 or newer. Nothing to install.

```
python site/build.py --serve
```

Then open <http://localhost:8000/myoepithelial-carcinoma/>. The site built
from this copy is the same, byte for byte, as the one built from the private
repository. The script that makes this copy checks that every time.

## Run the harvest again

```
python harvest/pubmed.py
python harvest/europepmc.py
python harvest/openalex.py          # set OPENALEX_API_KEY to run it in one go
python harvest/ctgov.py
python harvest/extras.py
python harvest/build_catalog.py
python harvest/fulltext.py all
python harvest/derive.py
python harvest/merge_reading.py data/read
python harvest/reading_list.py
```

Each step reads what the one before wrote. They write to `data/raw/` and
`data/fulltext/`, which this copy does not carry and `.gitignore` keeps out.
The harvest has been run from the private repository. It has not been run from
this copy.

Six parts of the catalog were read by a model and not matched by rule: the case
registry, the skin cases, the drug treatments, the trial eligibility, the
stains and look-alike tumors, and the source check.
`notes/reading-instructions.md` has the instructions each reader was given.
Papers from a later harvest need the same reading.

## How far to trust it

- Nothing here has been reviewed by a clinician.
- The case registry, the treatment table, the trial list and the pathology
  tables were extracted from abstracts by an AI model. An abstract leaves out
  most of a paper.
- A model checked 141 cited claims against their sources. The
  verdicts are in `data/catalog/verification.jsonl`, and what was corrected is
  in `notes/verification-summary.md`.
- Tiers, body-site tags and case-report flags are keyword rules. Expect some
  misfiled papers.
- The counts are a floor. Subscription indexes, non-English databases and most
  grey literature are not covered.
- Only open sources were used. No paywalled article was accessed.

## Reuse

- The scripts in `harvest/` and `site/` are under the MIT license. See `LICENSE`.
- The data this project compiled and added is under Creative Commons
  Attribution 4.0. Records taken from the public databases keep the terms of
  those databases. See `LICENSE-DATA.md`.
- The text of the site (`site/content.py`, `site/content_pages.py` and
  `site/translations/`) is under neither license. Quote it with a link, and
  ask before republishing it.

To cite: Saddington P. Myoepithelial carcinoma: a reference to the published
research. <https://staas.fund/myoepithelial-carcinoma/>. `CITATION.cff` has the
same in a form reference managers read.

## Corrections and additions

A paper, a trial, a registry, a research group, or a mistake in the numbers:
write through <https://staas.fund/contact>. Patients and families are welcome
too.
