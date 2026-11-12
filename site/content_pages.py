"""Hand-written text for the pages beyond the main reference.

Same rule as content.py: every factual sentence carries a [[key]] marker that
resolves through content.REFS, and {name} placeholders are filled at build time.
"""

# ---------------------------------------------------------------- site pages
# key -> page. "tag" is the catalog site tag the page is built around.
SITE_PAGES = {
    "skin": {
        "tag": "skin", "label": "Skin",
        "title": "Myoepithelial Carcinoma of the Skin (Cutaneous): Research and Cases",
        "h1": "Myoepithelial carcinoma of the skin",
        "description": "Cutaneous myoepithelial carcinoma: what the published cases show, its gene fusions, "
                       "how it relates to mixed tumors of the skin, and every indexed paper.",
        "standfirst": "A rare form of a rare disease. A 2026 review counted 26 reported cases of primary "
                      "cutaneous myoepithelial carcinoma[[gillis2026]].",
        "sections": [
            ("known", "What is known", """
<p>Myoepithelial cells surround the sweat glands of the skin, as they do the salivary glands and the
breast[[mentzel2003]]. The first series of these tumors in the skin came in 2003 and 2004, with 20 and 14
cases[[mentzel2003]][[hornick2004]]. The earliest paper in this catalog, from 1957, describes
a malignant myoepithelioma of the sweat glands[[devenyi1957]].</p>
<p>In the 14-case series, most tumors were on the limbs, the median age was 22.5, tumors measured 0.5 to 2.5 cm,
and one of the 14 was a carcinoma[[hornick2004]]. In an 18-case series, patients were 34 to 86 years old and
one tumor, on the cheek, was a carcinoma that had grown into the fat beneath the skin[[flucke2011]].</p>
<p>The carcinoma has a high rate of local recurrence and metastasis in the skin[[gillis2026]]. A 2025 report
describes a tumor in the axilla that had spread to lymph nodes[[zhu2025]].</p>
"""),
            ("spectrum", "Related skin tumors", """
<p>Skin tumors of this family form a spectrum: mixed tumor, which forms ducts and is also called chondroid
syringoma; myoepithelioma, which is purely myoepithelial and benign; and myoepithelial carcinoma[[flucke2011]].
A related malignant tumor, malignant mixed tumor, was counted together with myoepithelial carcinoma in a
101-tumor soft-tissue series, which defined it by malignant cartilage or bone[[hornick2003]].</p>
<p>A pathology report may also use the wider term <em>adnexal carcinoma</em>, meaning a cancer of the skin's
glands and follicles, with myoepithelial carcinoma given as the specific type[[post]].</p>
"""),
            ("genetics", "Genetics in the skin", """
<p>Half of the duct-forming tumors of skin and soft tissue in one study carried PLAG1 rearrangements, as mixed
tumors of the salivary glands do[[antonescu2013]]. EWSR1 is rearranged in a subset of cutaneous myoepithelial tumors[[flucke2011]], and
fusions of EWSR1 with PBX1 or PBX3 are enriched in skin and bone[[michal2026]]. A TRPS1::PLAG1 fusion was reported
in a primary cutaneous carcinoma in 2026[[gillis2026]].</p>
<p>A 2026 methylation study found that PLAG1-rearranged tumors were mostly benign, in older adults and in the
skin, and were biologically distinct from tumors with EWSR1 or FUS fusions[[michal2026]]. Which group a skin
tumor belongs to is therefore worth knowing.</p>
"""),
            ("treatment", "Treatment reports", """
<p>There is no series large enough to compare treatments in the skin. Across all sites, complete removal with
clear margins was associated with better survival[[giridhar2019]]. Mohs micrographic surgery has been reported
for a recurrent cutaneous myoepithelioma[[miller2009]].</p>
"""),
        ],
    },
    "soft-tissue": {
        "tag": "soft_tissue", "label": "Soft tissue",
        "title": "Soft Tissue Myoepithelial Carcinoma: Outcomes, Genetics and Research",
        "h1": "Myoepithelial carcinoma of soft tissue",
        "description": "Soft-tissue myoepithelial carcinoma: where it arises, recurrence and metastasis rates, "
                       "EWSR1 fusions, chemotherapy results, and every indexed paper.",
        "standfirst": "Mostly a tumor of the limbs and limb girdles, in adults and children alike. In a 101-tumor "
                      "series, malignant tumors recurred in 42% and metastasized in 32%[[hornick2003]].",
        "sections": [
            ("known", "What is known", """
<p>The reference series is 101 myoepithelial tumors of soft tissue, of which 40 were malignant. Patients were 3 to
83 years old, with a mean of 38. Tumors measured 0.7 to 20 cm. Forty-one were in the lower limbs, 35 in the upper
limbs, 15 in the head and neck and 10 in the trunk[[hornick2003]].</p>
<p>In soft tissue, a tumor with at least moderate cytologic atypia is classified as malignant. Benign tumors recur
in up to 20% and do not metastasize. The carcinoma recurs or metastasizes in up to 40 to 50%[[jo2015]].</p>
"""),
            ("outcomes", "Outcomes", """
<p>Of 31 malignant tumors with follow-up, averaging 50 months, 13 recurred locally, 10 metastasized and four
patients died of the disease[[hornick2003]]. In 24 adults treated at one sarcoma unit, 13 relapsed (54.2%), 3 locally
and 10 with metastases[[chamberlain2020]].</p>
<p>In children, of 23 followed, 52% developed metastases and 43% died, at a median of nine
months[[gleason2007]]. See the page on <a href="../children/">children</a>.</p>
"""),
            ("genetics", "Genetics", """
<p>EWSR1 was rearranged in 45% of 66 myoepithelial tumors from outside the salivary glands[[antonescu2010]]. Known
partners include PBX1, PBX3, POU5F1, ZNF444, ATF1 and KLF15[[antonescu2010]][[flucke2012]][[michal2026]]. A subset
of malignant tumors lose INI1[[jo2015]].</p>
<p>A 2026 study argues that malignant soft-tissue tumors with EWSR1 or FUS fusions are sarcomas, not carcinomas,
and found the shortest survival in the SS18::POU5F1, EWSR1::PBX3 and EWSR1::KLF15 groups[[michal2026]].</p>
"""),
            ("treatment", "Treatment reports", """
<p>Complete surgical resection is the mainstay for localized disease. Of 24 adults, nine received systemic
treatment, one had a partial response (to doxorubicin), and median progression-free survival on first-line
chemotherapy was 9.3 months. The authors encourage enrollment in trials[[chamberlain2020]].</p>
"""),
        ],
    },
    "salivary": {
        "tag": "salivary", "label": "Salivary glands",
        "title": "Salivary Gland Myoepithelial Carcinoma: Survival, Genetics and Research",
        "h1": "Myoepithelial carcinoma of the salivary glands",
        "description": "Salivary gland myoepithelial carcinoma: parotid and palate tumors, survival in SEER, "
                       "PLAG1 fusions, carcinoma ex pleomorphic adenoma, and every indexed paper.",
        "standfirst": "The most common form, and the best studied. In U.S. registry data, median overall survival "
                      "for major salivary gland cases was 142 months[[luo2022]].",
        "sections": [
            ("known", "What is known", """
<p>The diagnosis requires a tumor that is unequivocally malignant and exclusively myoepithelial. In the series
that set those criteria, 15 of 25 tumors were in the parotid, 15 arose in a pre-existing benign mixed tumor and
10 arose on their own[[savera2000]]. In a 51-case series the parotid and the palate were equally common[[kane2010]].</p>
<p>A tumor that arises in a pre-existing pleomorphic adenoma is called carcinoma ex pleomorphic adenoma. It
accounted for 54% of 48 cases in one series and was linked to worse outcomes than tumors arising on their
own[[kong2015]].</p>
"""),
            ("outcomes", "Outcomes", """
<p>In SEER, 290 patients with major salivary gland tumors had a median overall survival of 142 months, with 53%
alive at 10 years and 38% at 15. Of patients with a recorded stage, 14.5% had lymph-node involvement and 6.6% had
distant spread at diagnosis[[luo2022]].</p>
<p>In a 48-case series, 12 of the 44 patients with follow-up (27%) developed distant metastases, most often in the lung. None of the 23 patients whose
tumors had no necrosis did[[kong2015]]. In the 25-patient series, 47% of the 17 patients followed developed
metastases and 29% died of the disease[[savera2000]].</p>
"""),
            ("genetics", "Genetics", """
<p>In a genomic study of 40 tumors, 70% carried a gene fusion, most involving PLAG1. FGFR1::PLAG1 was found in 18%
and TGFBR3::PLAG1 in 15%, and the latter was absent from 723 other salivary tumors[[dalin2017]]. EWSR1
rearrangement has been reported in the clear cell type[[skalova2015]].</p>
"""),
            ("treatment", "Treatment reports", """
<p>Surgery is the main treatment. In SEER, 55.2% of patients had surgery alone and 44.8% had surgery with
radiotherapy, and radiotherapy was associated with better survival only after statistical adjustment[[luo2022]]. In the pooled literature,
radiotherapy after surgery reduced local and regional recurrence[[giridhar2019]].</p>
"""),
        ],
    },
    "children": {
        "tag": "pediatric", "label": "Children",
        "title": "Myoepithelial Carcinoma in Children: Outcomes, Genetics and Research",
        "h1": "Myoepithelial carcinoma in children",
        "description": "Pediatric myoepithelial carcinoma: how it differs from the adult disease, the EWSR1 "
                       "fusions involved, published outcomes, and every indexed paper.",
        "standfirst": "About one in five soft-tissue myoepithelial tumors occurs in a child, and in children they "
                      "are frequently malignant[[jo2015]].",
        "sections": [
            ("known", "What is known", """
<p>The reference series is 29 soft-tissue carcinomas in patients from newborn to 17 years old, with a median age
of nine. Fourteen were in the limbs, six in the trunk, five in internal organs and four in the head and
neck[[gleason2007]].</p>
<p>Of 23 children followed, nine had local recurrences, 12 developed metastases and 10 died of the disease, at a
median of nine months after diagnosis[[gleason2007]].</p>
"""),
            ("genetics", "Genetics", """
<p>The childhood disease is defined by gene fusions[[curemec2026b]]. EWSR1::KLF15 tumors occur mostly in children
under five, and EWSR1::POU5F1 was first found in a child and then in other children and young
adults[[michal2026]][[antonescu2010]]. In a pooled analysis of 185 fusion-positive cases, age under 25 predicted
worse progression-free survival[[michal2026]].</p>
"""),
            ("treatment", "Treatment reports", """
<p>Evidence is at the level of single patients. One report describes a child treated with ifosfamide, cisplatin and
etoposide, then ifosfamide, vincristine and etoposide, with radiotherapy to the surgical bed[[miccio2016]]. Another
used RNA expression analysis to choose a targeted drug for a four-year-old[[vasquez2025]].</p>
<p>cureMEC, the patient organization, reports building preclinical models of the fusion-positive
disease[[curemec2026b]].</p>
"""),
        ],
    },
}

# ------------------------------------------------- reading a pathology report
REPORT_LINES = [
    ("title", "SLIDE CONSULTATION REPORT", [1]),
    ("pair", "Service: 09/08/2021 &nbsp; Received: 09/14/2021 &nbsp; Reported: 09/16/2021", [2]),
    ("pair", "Clinical data: SECOND OPINION", [1]),
    ("diag", "Diagnosis: ADNEXAL CARCINOMA{3}, CONSISTENT WITH{4} MYOEPITHELIAL CARCINOMA (C44.609){5}", []),
    ("note", "Note: Immunostains demonstrate avid coexpression of CK5/6 and SOX-10, which suggests myoepithelial "
             "lineage. There is also partial expression of S100 protein.{6} To exclude secretory carcinoma, TRK and "
             "mammaglobin immunostains remain pending. An addendum report with results will follow early next week "
             "when staining is complete.{7}", []),
    ("note", "Invasion close to the inked surgical margin is noted. Additional excision to define a fully free "
             "surgical margin will be necessary.{8}", []),
]
REPORT_NOTES = [
    ("Slide consultation, second opinion", "The slides from the first biopsy were sent to another pathologist to read. "
     "For a rare tumor this is worth asking for: in one series most cases had first been given a different diagnosis[[savera2000]]."),
    ("The dates", "Service is the day the tissue was taken. Received and reported are when the second laboratory got the "
     "slides and when it answered. Here the report came eight days after the tissue was taken."),
    ("Adnexal carcinoma", "A cancer of the skin's appendages: the sweat glands, oil glands and hair follicles. It says "
     "what kind of tissue the tumor comes from."),
    ("Consistent with", "Pathologists' wording for a diagnosis that the findings fit. It is less absolute than a flat "
     "statement, and is common when a tumor is rare or hard to classify."),
    ("C44.609", "A code for the location, used for billing and registries: skin of the left upper limb, including the "
     "shoulder. It describes the site, not the tumor type."),
    ("The stains", "Immunostains show which proteins the cells make. Most myoepithelial tumors stain for epithelial "
     "markers, such as keratins, together with S-100 protein[[jo2015]]. This pathologist reads CK5/6 with SOX-10 as pointing "
     "to myoepithelial cells."),
    ("Pending, and the addendum", "Two more stains were ordered to rule out secretory carcinoma, a different gland cancer. "
     "Pending means the result is not in yet. Ask for the addendum when it arrives: it is part of the report."),
    ("The margin", "The surgeon's cut edge is marked with ink. Tumor close to the ink means cancer cells near the edge, "
     "so more tissue has to come out. Complete removal with clear margins was associated with better survival[[giridhar2019]]."),
]
REPORT_ALSO = [
    ("Size", "Tumors larger than 5 cm did worse in the pooled literature[[giridhar2019]]."),
    ("Mitotic rate", "More than 10 dividing cells per 10 high-power fields was linked to worse survival[[giridhar2019]]."),
    ("Necrosis", "In one salivary series, no patient whose tumor lacked necrosis developed distant metastases[[kong2015]]."),
    ("Perineural and vascular invasion", "Tumor growing along nerves or into vessels. Recorded in 11 and 4 of 25 salivary tumors[[savera2000]]."),
    ("Grade", "How abnormal the cells look. Grading of this tumor is described as controversial[[kong2015]]."),
    ("Molecular tests", "FISH or sequencing for EWSR1, PLAG1 and other fusions, and a stain for INI1[[jo2015]][[michal2026]]."),
]

# ------------------------------------------------------- printable summary
SUMMARY_FACTS = [
    ("Definition", "Malignant tumor showing exclusively myoepithelial differentiation[[savera2000]]. Older papers call it "
     "malignant myoepithelioma[[crissman1977]]. ICD-O-3 morphology 8982[[tandon2026]]. Listed apart from "
     "epithelial-myoepithelial carcinoma in standard vocabularies[[vocab]]."),
    ("Incidence", "About 0.013 per 100,000 person-years (SEER 1973 to 2012, 368 patients)[[zhang2017]]."),
    ("Sites", "Major salivary glands most often, then minor salivary glands, skin and soft tissue, breast[[giridhar2019]]."),
    ("Pathology", "Co-expression of epithelial markers (keratins, EMA) with S-100; calponin in most, GFAP in about half and p63 in under a quarter of "
     "soft-tissue tumors; a subset lose INI1[[jo2015]][[hornick2003]]."),
    ("Genetics", "EWSR1 rearranged in 45% of non-salivary tumors (partners PBX1, PBX3, POU5F1, ZNF444, ATF1, KLF15)[[antonescu2010]][[flucke2012]][[michal2026]]. "
     "PLAG1 fusions in most fusion-positive salivary cases (FGFR1, TGFBR3)[[dalin2017]]."),
    ("Behavior", "Soft tissue: local recurrence 42%, metastasis 32% of malignant tumors[[hornick2003]]. Salivary: distant "
     "metastasis 27%, mostly lung[[kong2015]]."),
    ("Survival", "All sites, National Cancer Database (n=336): 79.4% at 2 years, 66.5% at 5, 52.0% at 10[[tandon2026]]. "
     "Pooled literature (n=691): median overall survival 167 months[[giridhar2019]]."),
    ("Treatment evidence", "Complete resection with clear margins associated with better survival; adjuvant radiotherapy "
     "reduced locoregional recurrence[[giridhar2019]]. Limited chemotherapy data[[chamberlain2020]]. No established "
     "systemic standard[[curemec2026]]."),
    ("Prognostic factors", "Size over 5 cm, more than 10 mitoses per 10 HPF[[giridhar2019]]; necrosis, vascular invasion, "
     "origin in pleomorphic adenoma (salivary)[[kong2015]]; fusion type and age under 25 (fusion-positive)[[michal2026]]."),
]
SUMMARY_FORM = [
    "Name and date of birth", "Date of diagnosis", "Site of the first tumor", "Diagnosis line from the pathology report",
    "Second pathology opinion (where, when)", "Stains reported positive", "Margin status after each surgery",
    "Fusion and INI1 testing (test, result)", "Size, grade, mitotic rate", "Scans done (type, date, finding)",
    "Surgeries (date, site, surgeon)", "Radiotherapy or drug treatment", "Recurrences or new tumors (date, site)",
    "Current surveillance schedule", "Treating doctors and centers", "Questions for this visit",
]


# ── About this reference ────────────────────────────────────────────────────
# Who is behind the site and how it is kept. These sentences are about the site itself, so most
# carry no source. {name} placeholders are filled in by pages.about_page().

ABOUT = [
    ("who", "Who compiles it", """
<p>{author}, a patient. He was diagnosed with myoepithelial carcinoma of the skin in September 2021[[post]]. He is not
a doctor or a scientist, and nothing here should be read as if he were.</p>
<p>His account of why he built the reference is <a href="{story_url}">the last section of the main page</a>.</p>"""),
    ("what", "What it is, and what it is not", """
<p>It is a reference to the published research on one rare cancer. It reports what studies found and names each
study, so that a reader can go to the source.</p>
<p>It is not medical advice. It does not recommend a treatment, a doctor or a hospital. Figures for groups of
patients cannot say what will happen to one person. Decisions belong with you and your doctors.</p>"""),
    ("made", "How it is made", """
<ul class="plain-list">
<li><strong>Open sources only.</strong> The records come from free public databases: PubMed, Europe PMC, OpenAlex,
Semantic Scholar, ClinicalTrials.gov and the others named on each page. No paywalled article was accessed.</li>
<li><strong>Every figure has a source.</strong> Each factual sentence carries a numbered reference. The program that
builds the pages stops if a sentence points to a source that is not in the catalog.</li>
<li><strong>Compiled with AI.</strong> One person could not read {n_total} records. AI models were used to gather and
sort the records, to help write the pages, and to extract the case registry, the treatment table, the trial list and
the pathology tables from abstracts. Pages built that way say so at the top.</li>
<li><strong>Checked against the sources.</strong> On {check_date} a model checked {n_checked} cited claims against
their sources. {n_wrong_word} were wrong or not supported, and were corrected.
<a href="{changes_url}">The list is public</a>.</li>
<li><strong>Translations.</strong> The Spanish, Chinese and Japanese pages were translated by a model and checked by
translating them back into English. No clinician who speaks the language has reviewed them, and each page says so.</li>
</ul>
<p>The method in full, with its limits, is in <a href="{base_url}#method">Method and limits</a> on the main page.</p>"""),
    ("review", "Who has reviewed it", """
<p>No clinician has reviewed this site. When one does, their name and the date will be given here and on the pages
they read.</p>
<p>If you treat or study this disease and would read part of it, <a href="#contact">please write</a>. An hour on the
sections about diagnosis, genetics, outcomes and treatment would help most.</p>"""),
    ("independence", "Independence", """
<p>This is a personal project. It carries no advertising, has no sponsor and sells nothing. No link on it earns a
commission.</p>
<p>The organizations, hospitals, trials and researchers named here are listed because they appear in the public
record. Being listed is not an endorsement, and none of them has reviewed or paid for anything on the site.</p>
<p>The pages are hosted on staas.fund, the compiler's own website, which is otherwise about his work.</p>"""),
    ("corrections", "Corrections", """
<p>If something here is wrong, out of date or missing, <a href="#contact">write</a>. A paper, a trial, a registry, a
research group or a mistake in a number are all welcome, from patients and families as much as from clinicians.</p>
<p>A reported error is checked against the source. If it is an error, it is corrected, and the correction is recorded
with its date in <a href="{changes_url}">Corrections and changes</a>. Corrections are not made silently.</p>"""),
    ("updates", "How it is kept current", """
<p>Each page shows the date it was last updated. The records were last downloaded from the public databases on
{harvest_date}. Papers added by a later download are listed on <a href="{base_url}new/">What is new</a> and in the
<a href="{base_url}feed.xml">feed</a>.</p>"""),
    ("privacy", "Privacy", """
<p>The site has no accounts, no forms and no advertising, and it sets no cookies of its own.</p>
<p>It is served through Cloudflare, the network that staas.fund uses. Like any web host, Cloudflare sees each
request, including the address of the computer it came from. It adds two things to every page: a script that checks
whether a visitor is automated traffic, which sets one cookie named cf_clearance, and Cloudflare Web Analytics, which
counts page views without cookies.</p>
<p>Search runs in your browser, against a file the site downloads. The words you search for appear in the page
address, so they reach the server like any other address you visit.</p>
<p>If you write, your message and your email address go to {author}. They are used to answer you and to correct the
site, and for nothing else.</p>"""),
    ("reuse", "Reuse and citation", """
<p>The catalog, the case registry and the other data files may be reused under the
<a href="{license_url}" rel="license">{license_name}</a> license. The scripts that gather the records and build the
pages are public at <a href="{repo_url}">{repo_label}</a>.</p>
<p>To cite: Saddington P. Myoepithelial carcinoma: a reference to the published research. {base_url} Updated
{build_date}.</p>
<p>The text of the pages may be quoted with a link. Please ask before republishing it.</p>"""),
    ("contact", "Contact", """
<p>Write to <a href="mailto:{contact_email}?subject={contact_subject}">{contact_email}</a>.</p>
<p>It helps to say which page you mean and, for a correction, where the right figure can be read. Mail about this
reference is read by {author}. He cannot give medical advice or comment on anyone's care.</p>"""),
]


# ── Corrections and changes ─────────────────────────────────────────────────
# Newest first. Add an entry whenever the site changes in substance: a correction, a new page, a
# new download of the records. Say what changed and why, in plain words. A sentence about what a
# study found carries its [[key]] like anywhere else.

CHANGES = [
    ("2026-11-12", [
        "Added this page and <a href=\"{about_url}\">About this reference</a>: who compiles the site, how it is made, "
        "how corrections are handled, privacy and contact.",
        "The data may now be reused under the {license_name} license, and the scripts and the catalog were published "
        "at <a href=\"{repo_url}\">{repo_label}</a>.",
        "Translations. A separate model translated the Spanish, Chinese and Japanese pages back into English without "
        "seeing the original, and the results were compared. 29 sentences were corrected. In Chinese and Japanese, a "
        "word used for \u201cpatient organization\u201d also means \u201ctissue\u201d. The Chinese said a tumor had "
        "\u201cinfiltrated the adjacent margin\u201d where the English says \u201cinvasion close to the margin\u201d. "
        "Every number matched the English.",
        "Dates. \u201cRetrieved\u201d, the date on which trial status was recorded and the date of the source check had "
        "been following the day the pages were built. Each now shows the day the thing happened.",
        "An email address quoted inside a public dataset description was removed from the open data.",
        "The machine-readable description of the main page no longer says the page was \u201clast reviewed\u201d. No "
        "clinician has reviewed it.",
        "The author\u2019s name at the foot of each page now goes to his account of why he built the site. It had "
        "gone to his profile on another part of staas.fund.",
        "Contact moved from a general contact page to an address for this reference.",
        "Reading on a phone. A table that holds sentences is now set out as one record under another, so no column "
        "is cut off. Chart labels are larger, and the menus open across the screen. Two text colors were darkened to "
        "meet the contrast guideline for readers with low vision.",
        "The image shown when a link is shared said \u201cevery published paper\u201d. It now gives the count of papers "
        "that name the disease. The catalog is not complete, as Method and limits says.",
    ]),
    ("2026-11-11", [
        "The reference was published.",
        "Source check. A model checked {n_checked} cited claims against their sources: {n_full} against the full paper "
        "and {n_abstract} against the abstract. {n_wrong_word} were wrong or not supported by the source cited. The "
        "corrections follow.",
        "\u201c40 to 45% of tumors recurred\u201d in the adult soft-tissue series was a figure that paper quotes from "
        "earlier work. It was replaced with the series\u2019 own result: 13 of 24 patients (54.2%) relapsed, 3 locally "
        "and 10 with metastases[[chamberlain2020]].",
        "Survival at 15 years in the salivary registry study was changed from 39% to 38%, the figure in the full "
        "text. The shares with lymph node and distant spread now say they are of patients with a recorded stage, and "
        "the benefit of radiotherapy now says it appeared only after adjustment[[luo2022]].",
        "The proposal that some of these tumors are sarcomas is now limited, as in the paper, to malignant tumors with "
        "EWSR1 or FUS fusions. \u201cBiologically unrelated\u201d became \u201cepigenetically unrelated\u201d, and the "
        "outcomes table now says that 69 of the 185 tumors had survival data[[michal2026]].",
        "A figure of 27% from a salivary series is now given as 12 of the 44 patients with follow-up[[kong2015]].",
        "ATF1 as a partner gene of EWSR1 is now cited to the paper that reports it[[flucke2012]].",
        "The definition, the older name, the registry code and the separation from epithelial-myoepithelial carcinoma "
        "are each cited to a source that states them. The code is given as 8982, without \u201c/3\u201d.",
        "Two statements about the skin form were removed because the sources do not make them: that it is the rarest "
        "and least studied form, and that it was recognized only in 2003 and 2004[[gillis2026]][[hornick2004]][[mentzel2003]].",
        "\u201cThe largest soft-tissue series\u201d became \u201ca 101-tumor soft-tissue series\u201d[[hornick2003]].",
        "\u201cDiagnosis often involves a second opinion\u201d became the finding it rested on: in one series most "
        "cases had first been given a different diagnosis[[savera2000]].",
        "The National Cancer Database survival figures are no longer called overall survival. The abstract does not say "
        "which kind of survival they are[[tandon2026]].",
        "The incidence rates for 2012 were added from the full text of the registry study[[zhang2017]].",
    ]),
]

