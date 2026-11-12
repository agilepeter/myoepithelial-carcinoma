# Instructions given to the readers

On 2026-11-11 ten model readers extracted structured data from batches made by
`harvest/prep_reading.py`. These are the instructions each was given, kept so
the work can be repeated or checked. Every reader was told the same three
things first:

- Record only what the text states. Use null where it does not say.
- Do not infer, and do not use outside knowledge.
- A wrong value is worse than a blank.

## Case reports (four batches, one reader each)

Input: title and abstract of each single-patient report. Output: one record
per report with these fields.

- `is_myoepithelial_carcinoma`: false if the tumor is something else, or the
  disease appears only as a differential diagnosis
- `patients_in_report`; if more than one, the rest describe the first patient
- `age`, `age_unit`, `sex`
- `primary_site` (where it arose, never where it spread), `site_group`
- `arose_in` (for example pleomorphic adenoma, or de novo), `size_cm`
- `treatments`, `drugs`, `margin`
- `genes_or_fusions` found in this tumor
- `recurrence` and `metastasis`: "no" only if the text says there was none
- `metastasis_sites`, `follow_up_months`
- `status_at_last_follow_up`: alive with no evidence of disease, alive with
  disease, died of disease, died of other cause, alive with status not stated
- `confidence`

## Skin cases in full text (one reader)

Input: the body text of each skin paper held in the archive. Output: one
record per patient, with the case fields above plus depth, time before
diagnosis, first diagnosis if different, stains positive and negative, time to
recurrence, and a summary of at most 45 words. The reader first decided
whether each paper was truly a primary skin tumor.

## Drug treatments (one reader)

Input: abstracts and trial records that mention drug treatment. Output: one
line per regimen given to patients with this disease: regimen as stated, drug
class, number of patients, site, adult or child, setting, response as stated,
duration, a note of at most 25 words. A response was not to be inferred from
survival. Records with no specific treatment got one line saying why.

## Trial eligibility (one reader)

Input: 89 open interventional trials with the first 2,600 characters of their
eligibility criteria. Output: one of eight categories for each, from "names
myoepithelial carcinoma" to "not a treatment trial for cancer", with the
required marker, population, stage, treatment, and the wording that decided
it. The reader was told to choose the more cautious category when in doubt.

## Immunostains (one reader)

Input: abstracts of series that give stain rates. Output: one line per marker
per paper: site, tumor group, number of tumors, marker, positive and tested
counts or the percentage as stated. Rates for comparison tumors were skipped.

## Look-alike tumors (one reader)

Input: abstracts on differential diagnosis. Output: one line per look-alike
named: site, tumor, direction of the confusion, and how the abstract says they
are told apart, with nothing added from the reader's own knowledge.

## Source verification (one reader)

Input: the site's text and, for each cited paper, its abstract and the full
text where held. Output: one line per claim per source: what the claim says,
what it was checked against, a verdict (confirmed, confirmed in substance,
not found, contradicted), and what the source says. "Confirmed" meant the
source says exactly that, including every number.
