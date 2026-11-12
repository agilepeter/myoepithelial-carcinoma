"""Hand-written content for the public page.

Every factual sentence carries a [[key]] marker. build.py turns markers into
numbered references and fills the reference list from the catalog, so a claim
cannot appear without its source. {name} placeholders are numbers computed
from the catalog at build time.

Wording rule: say what a study reported, name the study, and do not give advice.
"""

# Where the page will live. Change BASE_URL before publishing.
BASE_URL = "https://staas.fund/myoepithelial-carcinoma/"
SITE_NAME = "StaaS Fund"
AUTHOR = "Peter Saddington"
AUTHOR_URL = "https://staas.fund/peter-saddington"   # his profile. Used in the structured data only
# Where the author's name links to on the page itself: his account of why he built the site.
STORY_URL = BASE_URL + "#why"
CONTACT_URL = "https://staas.fund/contact"
POST_URL = "https://theagilevc.substack.com/p/today-im-supposed-to-die-76"
POST2_URL = "https://theagilevc.substack.com/p/caal-cancer-as-a-lifestyle-94"
TWITTER = "@agilepeter"
# Dates of things that happened once. They must not move when the site is rebuilt.
FIRST_PUBLISHED = "2026-11-11"            # the day the site went live
SOURCE_CHECK_DATE = "11 November 2026"    # the day the cited claims were checked against their sources
# Where the author has written about this in public. Used in the page's structured data.
AUTHOR_PROFILES = ["https://x.com/agilepeter", "https://theagilevc.substack.com/"]
# The public record: the scripts and the catalog, without abstracts, full text or private notes.
REPO_URL = "https://github.com/agilepeter/myoepithelial-carcinoma"
REPO_LABEL = "github.com/agilepeter/myoepithelial-carcinoma"
# The compiled data may be reused with attribution. Records taken from public sources keep those sources' terms.
DATA_LICENSE = "Creative Commons Attribution 4.0"
DATA_LICENSE_SHORT = "CC BY 4.0"
DATA_LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
# IndexNow tells Bing and other search engines when pages change. The key is public by design:
# it is served at https://staas.fund/<key>.txt and only proves that requests come from the site.
INDEXNOW_KEY = "d6736e0e3e301dc9b5b32d73835f5b0b"

# Kept near 60 characters so search results show it whole.
TITLE = "Myoepithelial Carcinoma: Survival, Genetics, Trials and Research"
SHORT_TITLE = "Myoepithelial carcinoma: a reference to the research"
DESCRIPTION = (
    "A data-rich reference on myoepithelial carcinoma: incidence, survival figures, "
    "gene fusions, clinical trials, and a sourced directory of {n_core} published papers."
)
KEYWORDS = [
    "myoepithelial carcinoma", "malignant myoepithelioma", "myoepithelial carcinoma survival rate",
    "myoepithelial carcinoma prognosis", "myoepithelial carcinoma treatment",
    "cutaneous myoepithelial carcinoma", "soft tissue myoepithelial carcinoma",
    "salivary gland myoepithelial carcinoma", "myoepithelial carcinoma EWSR1",
    "myoepithelial carcinoma PLAG1", "myoepithelial carcinoma clinical trials",
    "myoepithelial carcinoma in children", "ICD-O 8982", "rare cancer",
]

# Reference keys -> catalog IDs (looked up in data/catalog/papers.jsonl) or
# external sources given in full.
REFS = {
    "zhang2017": "doi:10.21037/tcr.2017.04.15",
    "tandon2026": "doi:10.1200/jco.2026.44.16_suppl.e22590",
    "giridhar2019": "pmid:31276988",
    "luo2022": "pmid:35417814",
    "miccio2016": "pmid:26886377",
    "savera2000": "pmid:10843278",
    "kong2015": "pmid:25970687",
    "kane2010": "pmid:20644067",
    "dalin2017": "pmid:29084941",
    "skalova2015": "pmid:25581728",
    "hornick2003": "pmid:12960802",
    "gleason2007": "pmid:18043035",
    "jo2015": "pmid:25804378",
    "chamberlain2020": "pmid:31879796",
    "antonescu2010": "pmid:20815032",
    "antonescu2013": "pmid:23630011",
    "brandal2008": "pmid:18383210",
    "brandal2009": "pmid:19760602",
    "agaram2015": "pmid:25231231",
    "flucke2012": "pmid:22154050",
    "hornick2004": "pmid:14745720",
    "mentzel2003": "pmid:12753168",
    "flucke2011": "pmid:21725291",
    "gillis2026": "pmid:41239844",
    "zhu2025": "pmid:39539473",
    "miller2009": "pmid:19125803",
    "michal2026": "pmid:41342886",
    "kashyap2026": "pmid:41834073",
    "vasquez2025": "pmid:40379813",
    "curemec2026": "doi:10.1158/1538-7445.am2026-6355",
    "curemec2026b": "doi:10.1158/1538-7445.fusionpositive26-a004",
    "devenyi1957": "pmid:13497030",
    "crissman1977": "pmid:201361",
    "schurch1985": "pmid:2413600",
    "post2": {
        "text": "Saddington P. CAAL: Cancer as a Lifestyle. TheAgileVC, 24 October 2025.",
        "url": POST2_URL,
    },
    "calm": {
        "text": "Saddington P. Keep Calm and Carry On. TheAgileVC, 12 June 2024.",
        "url": "https://theagilevc.substack.com/p/keep-calm-and-carry-on",
    },
    "reporter": {
        "text": "NIH RePORTER, U.S. National Institutes of Health. Search of project titles, abstracts and terms "
                "for the disease and for myoepithelioma, retrieved {harvest_date}.",
        "url": "https://reporter.nih.gov/",
    },
    "geo": {
        "text": "NCBI Gene Expression Omnibus and BioProject. Search for myoepithelial tumors, retrieved {harvest_date}.",
        "url": "https://www.ncbi.nlm.nih.gov/gds/?term=myoepithelial+carcinoma",
    },
    "vocab": {
        "text": "NCI Thesaurus, OncoTree, MONDO, the Disease Ontology, MeSH and Wikidata, retrieved {harvest_date}.",
        "url": "https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&code=C7596",
    },
    "cellosaurus": {
        "text": "Cellosaurus, SIB Swiss Institute of Bioinformatics. Cell lines with a myoepithelial tumor as "
                "the disease of origin, retrieved {harvest_date}.",
        "url": "https://www.cellosaurus.org/",
    },
    "zheng2016": "pmid:26778756",
    "post": {
        "text": "Saddington P. Today, I'm Supposed to Die. TheAgileVC, 20 March 2025.",
        "url": POST_URL,
    },
    "ctgov": {
        "text": "ClinicalTrials.gov, U.S. National Library of Medicine. Registry search "
                "for records containing \"myoepithelial\" or \"myoepithelioma\", retrieved {harvest_date}.",
        "url": "https://clinicaltrials.gov/search?term=myoepithelial",
    },
    "catalog": {
        "text": "Catalog compiled for this page: PubMed, Europe PMC, OpenAlex and Semantic Scholar "
                "records merged and de-duplicated, retrieved {harvest_date}. Method described on this page.",
        "url": "#method",
    },
}

HERO_SUB = (
    "A rare cancer of myoepithelial cells, the contractile cells that wrap around glands. "
    "It arises in the salivary glands, soft tissue, skin, breast and other sites, at about "
    "<strong>0.013 cases per 100,000 people per year</strong> in U.S. registry data[[zhang2017]]. "
    "This reference gathers what has been published about it: <strong>{n_core} papers</strong> that name "
    "the disease, the registered trials, and the figures they report."
)

# The box at the top right of the main page: short facts, each with its source.
INFOBOX = [
    ("Also called", "Malignant myoepithelioma[[crissman1977]]"),
    ("Rarity", "About 0.013 cases per 100,000 a year[[zhang2017]]"),
    ("Sites", "Salivary glands, soft tissue, skin, breast[[giridhar2019]]"),
    ("Survival", "66.5% at 5 years, 52.0% at 10[[tandon2026]]"),
    ("Treatment", "Surgery with clear margins[[giridhar2019]]. No standard drug treatment[[curemec2026]]"),
    ("Genetics", "EWSR1 or PLAG1 gene fusions[[antonescu2010]][[dalin2017]]"),
    ("Code", "ICD-O-3 8982[[tandon2026]]"),
    ("Patients", "cureMEC, a patient-led project[[curemec2026]]"),
]
INFOBOX_CAPTION = "Myoepithelial cells (dark) sit between a gland's secreting cells and its outer membrane[[vocab]]."

# Longer versions of the same facts. Used for the translated essentials pages.
QUICK = [
    ("What it is", "A malignant tumor made of myoepithelial cells. In the salivary glands the "
     "diagnosis requires a tumor that is unequivocally malignant and exclusively myoepithelial[[savera2000]]. "
     "Older papers call it malignant myoepithelioma."),
    ("How rare", "About 0.013 per 100,000 person-years, from 368 patients in the U.S. SEER registry, "
     "1973 to 2012[[zhang2017]]. The U.S. National Cancer Database recorded 336 cases from 2004 to 2020[[tandon2026]]."),
    ("Where it arises", "In 691 patients pooled from the published literature, the major salivary glands "
     "were the most common site (36.4%), followed by minor salivary glands, skin and soft tissue, and breast[[giridhar2019]]."),
    ("Survival figures", "In the National Cancer Database, survival was 79.4% at two years, 66.5% at five "
     "and 52.0% at ten, across all sites[[tandon2026]]. The pooled literature gives a median overall survival "
     "of 167 months[[giridhar2019]]. Outcomes differ sharply by site, grade and age."),
    ("Main treatment", "Surgery. Complete removal with clear margins was associated with better "
     "progression-free and overall survival in the pooled analysis[[giridhar2019]]. There are no established "
     "standards for drug treatment[[curemec2026]]."),
    ("Genetics", "Largely a disease of gene fusions. EWSR1 is rearranged in 45% of myoepithelial tumors "
     "outside the salivary glands[[antonescu2010]], and 70% of salivary cases carry a fusion, most involving PLAG1[[dalin2017]]."),
    ("Registry code", "ICD-O-3 morphology code 8982[[tandon2026]]."),
    ("Not the same as", "Epithelial-myoepithelial carcinoma, which standard vocabularies list as a separate diagnosis[[vocab]], and "
     "myoepithelioma, which is benign[[jo2015]]."),
    ("Patient organization", "cureMEC: The Myoepithelial Carcinoma Project, a patient-driven research "
     "initiative launched in 2022[[curemec2026]]."),
]

SECTIONS = [
    {
        "id": "first-steps", "title": "If you were just diagnosed",
        "html": """
<p>Nobody opens this page for fun. If you are here, you or someone you love has had bad news, and you are reading
under stress. So, three things first.</p>
{first_three}
<p class="fineprint">Written by Peter Saddington, a patient, from what he learned after his own diagnosis in
2021. His account is <a href="#why">at the end of this page</a>.</p>
<h3 class="sub-heading">Take ownership</h3>
<p>Your doctors treat the disease, but you have to run the project. With a disease this rare[[zhang2017]], many of the people
treating you may be seeing it for the first time. You are the only person in every room, and nobody has more at
stake than you do. You cannot hand your health to the system and wait.</p>
<p>None of this means distrusting your doctors. It means arriving prepared, asking until you understand, and
keeping your own records.</p>
<h3 class="sub-heading">A plan for the first 30 days</h3>
{plan}
<h3 class="sub-heading">Questions to take to your next appointment</h3>
{questions}
<h3 class="sub-heading">Staying calm enough to think</h3>
<p>Fear is a normal response to this news, and it makes people decide badly. The goal is to be steady
enough to make the next decision well, and that is possible while still afraid. This is the list Peter keeps[[calm]].</p>
{calm}
<p><strong>Tell people, and give them jobs.</strong> One drives, one takes notes, one makes the insurance calls.
Peter, who by his own account rarely asks for help, wrote: “I got cancer. I need help.”[[post]]</p>
<p><strong>Protect sleep, food and movement.</strong> They are the part of this you control today.</p>
<h3 class="sub-heading">If you are the family or the friend</h3>
<ul class="plain-list">
<li>Go to the appointments and write everything down. It is hard to listen and take notes when the news is about you.</li>
<li>Take a job off their list: scheduling, records, insurance, meals, rides.</li>
<li>Do not send cures you found online. Ask what would help this week.</li>
<li>Let them talk about the numbers, including the bad ones. Then bring it back to the next step.</li>
</ul>
<h3 class="sub-heading">Where the hope is</h3>
<p>The reasons for hope are in the data.</p>
{hope}
<p>Four years after his diagnosis, past the date he had been told to expect, Peter wrote: “We’re making history
by simply not dying.” His routine is plain: scans every three months, and “you cut what you find.” His advice is
four words: “Stay the course. Focus.”[[post2]]</p>
<div class="callout"><strong>If tonight is too much.</strong> In the United States you can call or text 988 at any
hour to reach the Suicide and Crisis Lifeline. For questions about cancer, the National Cancer Institute's
information service is on 1-800-4-CANCER. More are listed under <a href="support/">organizations and support</a>.</div>
<p class="fineprint">This is one patient’s checklist, informed by the published research. It is not medical advice.
Every step is something to do with your doctors, not instead of them.</p>
""",
    },
    {
        "id": "what-it-is", "title": "What it is",
        "html": """
<p>Myoepithelial cells sit between the secreting cells of a gland and the membrane around it. They contract,
which pushes secretions out. Glands that have them include the salivary glands, the sweat glands of the skin
and the breast[[mentzel2003]], which is why tumors of these cells turn up in such different parts of the body.</p>
<p>Tumors of myoepithelial cells form a spectrum. A <strong>mixed tumor</strong> (called pleomorphic adenoma in
the salivary glands and chondroid syringoma in the skin) contains ducts as well as myoepithelial cells.
A <strong>myoepithelioma</strong> is purely myoepithelial and benign. A <strong>myoepithelial carcinoma</strong>
is the malignant form[[jo2015]][[hornick2004]].</p>
<p>The dividing line depends on the site. In the salivary glands, the tumor must be unequivocally malignant and
exclusively myoepithelial[[savera2000]]. In soft tissue, tumors with at least moderate cytologic atypia are
classified as malignant[[jo2015]]. In one salivary series most cases had first been diagnosed as something
else, usually malignant mixed tumor[[savera2000]].</p>
{spectrum}
{etymology}
""",
    },
    {
        "id": "names", "title": "Names and codes",
        "html": """
<p>The same disease appears under several names, which is one reason it is hard to search for.</p>
<div class="table-wrap"><table class="data-table">
<thead><tr><th>Name or code</th><th>How it is used</th></tr></thead>
<tbody>
<tr><td><strong>Myoepithelial carcinoma</strong></td><td>The name used by the series cited on this page[[catalog]]. Some standard vocabularies list it as malignant myoepithelioma[[vocab]].</td></tr>
<tr><td><strong>Malignant myoepithelioma</strong></td><td>The older name. A 1977 report of a parotid tumor used it[[crissman1977]], as did a 1957 report from the sweat glands[[devenyi1957]].</td></tr>
<tr><td><strong>MECA, MEC, MC</strong></td><td>Abbreviations used in different papers[[kong2015]][[giridhar2019]][[miccio2016]]. MEC is also the usual abbreviation for mucoepidermoid carcinoma, a different salivary cancer.</td></tr>
<tr><td><strong>ICD-O-3 8982</strong></td><td>The morphology code cancer registries use to count cases[[tandon2026]].</td></tr>
<tr><td><strong>Carcinoma ex pleomorphic adenoma</strong></td><td>A myoepithelial carcinoma that arises inside a pre-existing benign mixed tumor. That was the origin of 26 of 48 salivary cases in one series (54%)[[kong2015]] and 15 of 25 in another[[savera2000]].</td></tr>
<tr><td><strong>Malignant mixed tumor</strong></td><td>A related malignant tumor. A 101-tumor soft-tissue series defined it by malignant cartilage or bone and counted it together with myoepithelial carcinoma[[hornick2003]].</td></tr>
<tr><td><strong>Epithelial-myoepithelial carcinoma</strong></td><td>A different diagnosis with a similar name. It is tracked here as related literature, not as the same disease[[catalog]].</td></tr>
</tbody></table></div>
""",
    },
    {
        "id": "where", "title": "Where it occurs",
        "html": """
<p>The answer depends on who is counting. In the pooled literature the salivary glands lead[[giridhar2019]].
In the U.S. National Cancer Database the most common coded site was the breast, followed by the vulva, and 70.5% of
patients were women[[tandon2026]]. Within the major salivary glands, 76.6% of cases were in the parotid[[luo2022]].
In soft tissue, most tumors arise in the limbs and limb girdles[[hornick2003]].</p>
<p>The chart counts <em>papers</em>, not patients: the {n_title} human studies in this catalog that name the
disease in their title, tagged by the body sites their title or abstract mentions[[catalog]].</p>
{bars_sites}
""",
    },
    {
        "id": "rarity", "title": "How rare it is",
        "html": """
<div class="stat-row">
<div class="stat-card"><span class="stat-num">0.013</span><span class="stat-label">cases per 100,000 people per year, SEER 1973 to 2012[[zhang2017]]</span></div>
<div class="stat-card"><span class="stat-num">368</span><span class="stat-label">patients in four decades of SEER data[[zhang2017]]</span></div>
<div class="stat-card"><span class="stat-num">336</span><span class="stat-label">cases in the National Cancer Database, 2004 to 2020[[tandon2026]]</span></div>
<div class="stat-card"><span class="stat-num">691</span><span class="stat-label">patients described in 340 publications, pooled in 2019[[giridhar2019]]</span></div>
</div>
<p>The SEER study found the same incidence in men and women, and a higher rate in the mouth and throat than at
other sites. For 2012 alone it reports higher rates: 0.058 per 100,000 in men and 0.025 in women[[zhang2017]]. The National Cancer Database study saw a gradual rise in reported cases over
its 17 years[[tandon2026]]. In the skin the disease is rarer still: a 2026 review found 26 known cases of primary
cutaneous myoepithelial carcinoma[[gillis2026]].</p>
""",
    },
    {
        "id": "diagnosis", "title": "How it is diagnosed",
        "html": """
<p>Diagnosis is made under the microscope and confirmed with immunostains. Most myoepithelial tumors stain for
both epithelial markers (keratins or EMA) and S-100 protein. GFAP and p63 are often positive, and a subset of
malignant tumors lose INI1[[jo2015]]. No single stain is decisive, so pathologists read a panel.</p>
<p>The chart shows how often each marker was positive in a soft-tissue series of 101 tumors, 40 of them
malignant[[hornick2003]].</p>
{bars_markers}
<p>Salivary tumors show a similar pattern. In 25 salivary carcinomas, keratin AE1/AE3 and S-100 were positive in
all, calponin in 75% and smooth muscle actin in 50%[[savera2000]]. In a 51-case series from a tertiary cancer
center, calponin was positive in 98% and S-100 in 82%[[kane2010]].</p>
<div class="callout"><strong>Why second opinions are common.</strong> The cells can be epithelioid, spindled,
clear or plasmacytoid, in varied patterns[[kane2010]], and in one series most tumors had first been given a
different diagnosis[[savera2000]]. The pathology report that prompted this page was itself a second-opinion
slide review, and relied on CK5/6, SOX-10 and S-100[[post]].</div>
""",
    },
    {
        "id": "genetics", "title": "Gene fusions",
        "html": """
<p>Since 2008, genetics has changed how the disease is understood. Many tumors carry a fusion, where two genes are joined
and the hybrid drives growth. Which fusion a tumor has tracks with where it arises, how old the patient is and
how it behaves[[michal2026]].</p>
{fusion_families}
<div class="table-wrap"><table class="data-table">
<thead><tr><th>Fusion or rearrangement</th><th>What has been reported</th></tr></thead>
<tbody>
<tr><td><strong>EWSR1</strong> (any partner)</td><td>Rearranged in 45% of 66 myoepithelial tumors outside the salivary glands[[antonescu2010]].</td></tr>
<tr><td><strong>EWSR1::PBX1</strong></td><td>Described in 2008[[brandal2008]]. Found in 5 of 66 tumors[[antonescu2010]]. Enriched in skin and bone[[michal2026]].</td></tr>
<tr><td><strong>EWSR1::ZNF444</strong></td><td>Described in 2009 in a soft-tissue myoepithelial carcinoma[[brandal2009]].</td></tr>
<tr><td><strong>EWSR1::POU5F1</strong></td><td>Found in soft-tissue tumors in children and young adults[[antonescu2010]]. Tends to show malignant histology[[michal2026]].</td></tr>
<tr><td><strong>EWSR1::ATF1</strong></td><td>Reported in a soft-tissue myoepithelial tumor in 2012[[flucke2012]].</td></tr>
<tr><td><strong>EWSR1::PBX3</strong></td><td>Described in 2015[[agaram2015]]. Enriched in skin and bone, with a median disease-specific survival of 38 months[[michal2026]].</td></tr>
<tr><td><strong>EWSR1::KLF15</strong></td><td>Mostly in children under five. Median disease-specific survival 45 months[[michal2026]].</td></tr>
<tr><td><strong>SS18::POU5F1</strong></td><td>Malignant histology and the shortest median disease-specific survival of the groups studied, 31 months[[michal2026]].</td></tr>
<tr><td><strong>PLAG1</strong> (skin and soft tissue)</td><td>Rearranged in 37% of 35 tumors that lacked EWSR1 and FUS changes. All were benign and nearly all formed ducts[[antonescu2013]]. Predominantly benign, in older adults, in the skin[[michal2026]].</td></tr>
<tr><td><strong>FGFR1::PLAG1, TGFBR3::PLAG1</strong></td><td>Found in 18% and 15% of 40 salivary myoepithelial carcinomas. TGFBR3::PLAG1 was absent from 723 other salivary tumors[[dalin2017]].</td></tr>
<tr><td><strong>TRPS1::PLAG1</strong></td><td>Reported in 2026 in a primary cutaneous myoepithelial carcinoma, the first such report[[gillis2026]].</td></tr>
<tr><td><strong>EWSR1</strong> in clear cell salivary tumors</td><td>Rearrangement reported in clear cell myoepithelial carcinoma of the salivary glands[[skalova2015]].</td></tr>
</tbody></table></div>
<p>A 2026 methylation study of 52 fusion-positive skin, soft-tissue and bone tumors concluded that tumors with
EWSR1 or FUS fusions are epigenetically unrelated to the PLAG1-driven tumors of skin and salivary gland, and that
their malignant forms are better classified as sarcomas than carcinomas[[michal2026]]. A separate 2026 sequencing
study of 27 patients placed the disease closest to salivary adenoid cystic carcinoma, found IGF1R over-expressed
with or without a fusion, and made its sequencing data available to researchers[[kashyap2026]]. The two studies point in different
directions, and the question is open.</p>
""",
    },
    {
        "id": "outcomes", "title": "Survival and outcomes",
        "html": """
<h3 class="sub-heading">Out of 100 people diagnosed</h3>
<p class="chart-note">Survival across all body sites in the U.S. National Cancer Database: 336 patients,
2004 to 2020[[tandon2026]]. The abstract does not say whether deaths from other causes are counted.</p>
{survival_people}
<p>In the pooled literature, median overall survival was 167 months, about 14 years[[giridhar2019]].
The table sets out what each major series reported.</p>
<div class="table-wrap"><table class="data-table">
<thead><tr><th>Study</th><th>Patients</th><th>What it reported</th></tr></thead>
<tbody>
<tr><td>Pooled literature, 2019[[giridhar2019]]</td><td>691, all sites</td><td>Median progression-free survival 48 months. Median overall survival 167 months. Worse with tumors over 5 cm and with more than 10 mitoses per 10 high-power fields.</td></tr>
<tr><td>National Cancer Database, 2026[[tandon2026]]</td><td>336, all sites</td><td>Survival 79.4% at 2 years, 66.5% at 5 and 52.0% at 10. Mean age at diagnosis 56.7.</td></tr>
<tr><td>SEER, major salivary glands, 2022[[luo2022]]</td><td>290</td><td>Median overall survival 142 months. 53% alive at 10 years and 38% at 15. Of patients with a recorded stage, lymph nodes were involved in 14.5% and distant organs in 6.6% at diagnosis.</td></tr>
<tr><td>Salivary, 2015[[kong2015]]</td><td>48</td><td>Distant metastasis in 12 of the 44 patients with follow-up (27%), most often to the lung. None in the 23 patients whose tumors had no necrosis.</td></tr>
<tr><td>Salivary, 2000[[savera2000]]</td><td>25, 17 followed</td><td>Metastasis in 47%. Death from disease in 29%. No evidence of disease in 59%.</td></tr>
<tr><td>Soft tissue, 2003[[hornick2003]]</td><td>31 malignant, followed</td><td>Local recurrence in 42% and metastasis in 32%. Of 33 benign or low-grade tumors, 18% recurred and none metastasized.</td></tr>
<tr><td>Soft tissue, adults, 2020[[chamberlain2020]]</td><td>24</td><td>13 of 24 patients (54.2%) relapsed, 3 locally and 10 with metastases. Median progression-free survival on first-line chemotherapy 9.3 months.</td></tr>
<tr><td>Soft tissue, children, 2007[[gleason2007]]</td><td>29, 23 followed</td><td>Metastasis in 52%. Death from disease in 43%, at a median of 9 months.</td></tr>
<tr><td>Fusion-positive, pooled, 2026[[michal2026]]</td><td>185 pooled, 69 with survival data</td><td>Median disease-specific survival 31 to 45 months in the three shortest-lived fusion groups. Age 25 or under predicted worse progression-free survival.</td></tr>
</tbody></table></div>
<h3 class="sub-heading">Deaths from the disease, series by series</h3>
<p class="chart-note">Share of followed patients who had died of the disease at last follow-up. Follow-up was a few
years in every series, so later deaths are not counted.</p>
{series_deaths}
<div class="callout"><strong>How to read these numbers.</strong> Each comes from a small group treated at
different times, at different sites and with different grades of tumor. A median describes a group, not a
person. The spread between series, from children with soft-tissue tumors to adults with salivary tumors,
is wider than any one figure can carry.</div>
""",
    },
    {
        "id": "treatment", "title": "Treatment: what studies report",
        "html": """
<p>This section reports what studies found. It is not advice, and nobody should change treatment on the
strength of a web page.</p>
<ul class="plain-list">
<li><strong>Surgery</strong> is the mainstay. Complete resection with clear margins was associated with better
progression-free and overall survival[[giridhar2019]], and complete resection is the standard for localized
soft-tissue disease[[chamberlain2020]]. In the National Cancer Database, 77.9% of patients had surgery[[tandon2026]].</li>
<li><strong>Radiotherapy</strong> after surgery reduced local and regional recurrence in the pooled analysis[[giridhar2019]].
A SEER analysis linked it to better survival in high-grade tumors[[miccio2016]]. In major salivary gland
cases the link appeared only after statistical adjustment[[luo2022]]. 36.6% of patients in the National Cancer Database received it[[tandon2026]].</li>
<li><strong>Chemotherapy</strong> has limited evidence. In 24 adults with soft-tissue disease, nine received
systemic treatment, one had a partial response (to doxorubicin), and median progression-free survival on
first-line chemotherapy was 9.3 months[[chamberlain2020]].</li>
<li><strong>Targeted treatment</strong> is at the case-report stage. One group used RNA expression analysis to
choose a targeted drug for a four-year-old patient[[vasquez2025]]. A 2026 sequencing study proposed IGF1R as a
target worth exploring[[kashyap2026]].</li>
<li><strong>Mohs surgery</strong> has been reported for a recurrent cutaneous myoepithelioma[[miller2009]].</li>
</ul>
<p>There are no established therapeutic standards for the disease[[curemec2026]]. Authors of the adult soft-tissue
series concluded that more effective systemic therapies are needed and that enrollment in clinical trials
should be encouraged[[chamberlain2020]].</p>
""",
    },
    {
        "id": "skin", "title": "In the skin",
        "html": """
<p>The earliest paper in this catalog, from 1957, describes a malignant myoepithelioma of the sweat glands[[devenyi1957]].
The first series of skin tumors in the catalog came in 2003 and 2004. One had 20 tumors, two of them carcinomas,
and its authors wrote that the idea of myoepithelial tumors of the skin was still debated[[mentzel2003]]. The other had 14[[hornick2004]]. In the 14-case series most tumors were on the limbs, the median
age was 22.5, and one of the 14 was a carcinoma[[hornick2004]].</p>
<p>Skin tumors split genetically. Of the tumors that form ducts (mixed tumors, also called chondroid syringomas), half carried PLAG1
rearrangements in one study, as salivary mixed tumors do[[antonescu2013]]. EWSR1 rearrangement occurs in a
subset of cutaneous myoepithelial tumors[[flucke2011]], and EWSR1 fusions with PBX1 or PBX3 are enriched in skin
and bone[[michal2026]].</p>
<p>Primary cutaneous myoepithelial carcinoma has a high rate of local recurrence and metastasis, and a 2026 review
counted 26 known cases[[gillis2026]]. A 2025 report describes a case in the axilla with lymph-node metastasis[[zhu2025]].</p>
<p>This catalog flags <strong>{n_skin} works</strong> as closest to the skin form: myoepithelial carcinoma placed in
the skin by its title or abstract, and malignant mixed tumor of the skin[[catalog]].
<a href="papers/#focus">Browse them in the directory</a>.</p>
""",
    },
    {
        "id": "children", "title": "In children",
        "html": """
<p>About 20% of soft-tissue myoepithelial tumors occur in children, and in children they are frequently
malignant[[jo2015]]. In 29 pediatric soft-tissue carcinomas, ages ran from newborn to 17, with a median
of nine. Of 23 children with follow-up, 52% developed metastases and 43% died of the disease, at a median of
nine months[[gleason2007]].</p>
<p>Genetics separates the childhood disease. EWSR1::KLF15 tumors occur mostly in children under five, and age
under 25 predicted worse progression-free survival in a pooled analysis of 185 fusion-positive cases[[michal2026]].
The patient group cureMEC describes the pediatric form as fusion-driven and reports building preclinical
models[[curemec2026b]].</p>
""",
    },
    {
        "id": "open-questions", "title": "What is not known",
        "html": """
<p>A reference should say where the knowledge runs out. These are the questions the papers themselves call open.</p>
<ul class="plain-list">
<li><strong>Which drugs work.</strong> There are no established therapeutic standards[[curemec2026]]. In what its authors
call the largest published cohort of adult soft-tissue disease, nine patients received drug treatment[[chamberlain2020]].</li>
<li><strong>Who should have radiotherapy.</strong> The pooled analysis calls the role of adjuvant therapy unclear[[giridhar2019]],
and a SEER study calls the role of radiation unknown while reporting a benefit in high-grade tumors[[miccio2016]].</li>
<li><strong>Whether it is one disease.</strong> One 2026 study argues that malignant tumors with EWSR1 or FUS
fusions are sarcomas, and that PLAG1-rearranged skin tumors belong with the salivary ones[[michal2026]]. Another finds the disease closest to salivary carcinomas[[kashyap2026]].</li>
<li><strong>How to grade it.</strong> Grading is described as controversial[[kong2015]].</li>
<li><strong>How the skin form behaves.</strong> Everything known comes from 26 single case reports, which point to a high rate
of recurrence and metastasis[[gillis2026]].</li>
<li><strong>Who gets it.</strong> Reports conflict. SEER found the same incidence in men and women[[zhang2017]].
The National Cancer Database found that 70.5% of patients were women[[tandon2026]].</li>
<li><strong>Why it starts.</strong> None of the series cited on this page identifies a cause.</li>
<li><strong>Who is paying to find out.</strong> A search of U.S. federal research grants found no project with the
disease in its title[[reporter]].</li>
</ul>
""",
    },
    {
        "id": "timeline", "title": "Timeline of the research",
        "html": """
<p>The main steps in the research, by year.</p>
{timeline}
""",
    },
    {
        "id": "literature", "title": "The literature in numbers",
        "html": """
<p>Everything on this page rests on a catalog built from four indexes: PubMed, Europe PMC, OpenAlex and Semantic Scholar[[catalog]].
Of {n_total} works, <strong>{n_core}</strong> name the disease in their title or abstract. The rest cover
neighboring tumors or mention the disease only in passing. All of it comes from free public sources.</p>
{glance}
<h3 class="sub-heading">Papers per year</h3>
<p class="chart-note">Works naming myoepithelial carcinoma in title or abstract, by year of publication.
The count for {year_max} is incomplete.</p>
{chart_years}
<h3 class="sub-heading">What kind of evidence</h3>
<p>{n_case_reports} of the {n_core} are flagged as case reports, which is {pct_case_reports}% of the literature.
Most of what is known about this disease comes from descriptions of one patient at a time.</p>
{bar_types}
<h3 class="sub-heading">Languages</h3>
<p>The disease has been written about in {n_langs} languages. {n_nonenglish} of the {n_core} papers are not in English.</p>
{bars_langs}
<h3 class="sub-heading">Journals that publish it most</h3>
{bars_journals}
<h3 class="sub-heading">How much is open</h3>
{coverage}
""",
    },
    {
        "id": "most-cited", "title": "Most cited papers",
        "html": """
<p>The ten papers naming the disease in their title that other researchers cite most, by OpenAlex and
Europe PMC citation counts[[catalog]]. Citation counts favor older papers.</p>
{ranking}
""",
    },
    {
        "id": "trials", "title": "Clinical trials",
        "html": """
<p>ClinicalTrials.gov holds <strong>{n_trials_named} records</strong> in which the word myoepithelial appears anywhere[[ctgov]].
A record is listed here if it matches, so some mention the disease only as one of many eligible tumor types.
The catalog also holds {n_trials_other} trials for salivary gland cancers and skin adnexal tumors, which may
accept this diagnosis without naming it.</p>
{trials_table}
<p class="fineprint">Status is as recorded on {harvest_date}. Check the registry for current status and eligibility.</p>
""",
    },
    {
        "id": "people", "title": "Researchers and organizations",
        "html": """
<p><strong>cureMEC: The Myoepithelial Carcinoma Project</strong> is a patient-driven initiative launched in 2022.
It reports building biospecimen collections, molecular data and preclinical models[[curemec2026]], in collaboration
with the Rare Cancer Research Foundation[[curemec2026b]].</p>
<p>The authors below appear most often on PubMed-indexed papers naming the disease[[catalog]]. Counts are by
name as printed, so they can merge or split people.</p>
{bars_authors}
<p>Shared data: a 2026 study deposited exome and RNA sequencing from 27 patients in the EGA repository[[kashyap2026]].</p>
""",
    },
    {
        "id": "resources", "title": "For researchers: codes, data and funding",
        "html": """
<h3 class="sub-heading">Standard codes</h3>
<p>How the main vocabularies name and code the disease[[vocab]]. The ICD-O-3 code is the one a registry study used[[tandon2026]]. Use these to search registries, biobanks and
genomic portals. MeSH has no heading for the carcinoma alone: it is indexed under Myoepithelioma.</p>
{codes_table}
<h3 class="sub-heading">Public datasets</h3>
<p>NCBI holds {n_datasets} studies that mention myoepithelial tumors, of which {n_datasets_named} name the
carcinoma[[geo]]. Exome and RNA sequencing from 27 patients is in the EGA archive[[kashyap2026]].</p>
{datasets_table}
<h3 class="sub-heading">Federal funding</h3>
<p>NIH RePORTER lists {n_grant_projects} funded projects whose title, abstract or terms mention the disease or
myoepithelioma. None has it in the title[[reporter]].</p>
{grants_table}
<h3 class="sub-heading">This page's data</h3>
<p>The full catalog, without abstracts: <a href="data/papers.json">papers.json</a>, <a href="data/papers.csv">papers.csv</a>,
<a href="data/trials.json">trials.json</a>, <a href="data/datasets.json">datasets.json</a>,
<a href="data/terminology.json">terminology.json</a>.</p>
<p><strong>Reuse.</strong> The catalog, the case registry and the other data files may be reused under the
<a href="{license_url}" rel="license">{license_name}</a> license: say where they came from and link to this page.
Titles, author names, trial records and dataset descriptions come from the public sources named on this page and keep
the terms of those sources.</p>
<p><strong>To cite this page.</strong> Saddington P. Myoepithelial carcinoma: a reference to the published research.
{base_url} Updated {build_date}.</p>
<p><strong>Source.</strong> The scripts that gather the records and build these pages are public, together with the
catalog, at <a href="{repo_url}">{repo_label}</a>. That copy leaves out abstracts, full text and the compiler's
private notes.</p>
""",
    },
    {
        "id": "faq", "title": "Common questions",
        "html": "{faq}",
    },
    {
        "id": "glossary", "title": "Glossary",
        "html": """
<p>Words that appear in pathology reports and in the papers cited here.</p>
{glossary}
""",
    },
    {
        "id": "directory", "title": "Directory of papers",
        "html": """
<p>Every paper that names the disease, with its authors, journal, year and a link to the source. Filter by
body site, by type of paper, or search by word.</p>
{directory_teaser}
""",
    },
    {
        "id": "method", "title": "Method and limits",
        "html": """
<ul class="plain-list">
<li><strong>Open sources only.</strong> Everything on this site was gathered from free public sources: PubMed,
Europe PMC, OpenAlex, Semantic Scholar, ClinicalTrials.gov and the other public databases named on each page. No
paywalled article was accessed. Of the {n_core} papers that name the disease, {n_core_ft} are held in full text
from PubMed Central, {n_core_oa} more are open access elsewhere, and {n_core_closed} are behind a paywall. For those
{n_core_closed}, this site knows only what the public indexes show: the title, the authors and, where there is one,
the abstract. If you wrote one of them and can share it, <a href="{contact_url}">please write</a>.</li>
<li><strong>Sources.</strong> PubMed, Europe PMC, OpenAlex and Semantic Scholar were searched for the disease and its neighbors,
and ClinicalTrials.gov for trials. Records were merged by PubMed ID, DOI and PMC ID[[catalog]].</li>
<li><strong>Sorting is by keyword.</strong> A paper counts as naming the disease if its title or abstract contains
"myoepithelial carcinoma" or "malignant myoepithelioma". Body-site tags and case-report flags are also keyword
rules. Expect some misfiled papers.</li>
<li><strong>Figures are quoted from abstracts.</strong> Each number on this page is followed by its source.
Where a paper's abstract and full text differ, the full text is right.</li>
<li><strong>Not yet covered.</strong> Subscription indexes, non-English databases, conference posters without a
DOI and trial registries outside the United States. The counts here are a floor.</li>
<li><strong>Read by a model.</strong> The case registry, the treatment table, the trial list and the pathology
tables were extracted from abstracts by an AI model told to record only what the text states. They are marked as
such on their pages.</li>
<li><strong>Checked against the sources.</strong> On {check_date} a model checked 141 cited claims against their
sources: 65 against the full paper and 76 against the abstract. Thirteen were wrong or not supported by the source
cited, and were corrected. A claim confirmed only against an abstract may still differ from the full paper.</li>
<li><strong>Not yet reviewed by a clinician.</strong> If you treat or study this disease and would read it,
<a href="{contact_url}">please write</a>.</li>
<li><strong>Not medical advice.</strong> This is a reference to published research, compiled by a patient. It
cannot tell you about your own case. Decisions belong with you and your doctors.</li>
</ul>
<p class="fineprint">Last updated {build_date}. Data: <a href="data/papers.json">papers.json</a> ·
<a href="data/papers.csv">papers.csv</a> · <a href="data/trials.json">trials.json</a>, free to reuse under
<a href="{license_url}" rel="license">{license_short}</a>. Scripts and catalog: <a href="{repo_url}">{repo_label}</a>.</p>
""",
    },
    {
        "id": "correction", "title": "Corrections and additions",
        "html": """
<div class="cta-box">
<h3>Know something this page is missing?</h3>
<p>A paper, a trial, a registry, a research group, or a mistake in the numbers. Patients and families are
welcome too.</p>
<a class="btn btn-primary" href="{contact_url}">Send a correction or addition</a>
</div>
""",
    },
    {
        "id": "why", "title": "Why I built this",
        "byline": "By Peter Saddington, diagnosed September 2021",
        "html": """
<p>On 20 September 2021 a doctor phoned to tell me I had cancer. When I asked how I got it, he said it was bad
luck, and that there were few studies. Over the next weeks I met five more doctors. Every one of them said the
word “rare.” One told me he had never heard of it. None could point to a standard of care[[post]].</p>
<p>I was told there was no cure, a 40% chance it would spread or return, and that the average patient lived
3.5 years. I asked for data. What I could find on my own in 2021 was one prognosis paragraph last updated in 2016
and a study of 24 patients[[post]]. I came away believing that most people with this disease die of it, and soon.</p>
<p>I lived under that number for three and a half years. On the day I was statistically supposed to be dead,
I wrote about it[[post]]. Then I did the research again, properly.</p>
{compare}
<h3 class="sub-heading">What went wrong</h3>
<p>I do not think any one doctor lied to me. This disease turns up in about one person in every 7.7 million each
year[[zhang2017]]. Most doctors will never see a case, and none has the hours to read {n_core} papers. So they
reach for the nearest small study, and the patient hears one sentence. I was given incomplete information at the
moment it mattered most, and it shaped the care I thought I should ask for.</p>
<h3 class="sub-heading">What changed</h3>
<p>In 2021 I searched by hand and found fragments. In 2026 I did it again with AI. In a day it pulled {n_total}
works from four open research indexes, sorted them, and traced every figure on this page back to its source[[catalog]].
A patient could not have done that alone in 2021. Now anyone can read the result.</p>
<p>None of this makes it a mild disease. It comes back. Mine has, on my jawline, hairline, leg, back and finger,
and I am scanned every three months[[post2]]. The skin form I have has fewer than 30 reported cases[[gillis2026]],
and the largest group in the big datasets is salivary gland cases[[giridhar2019]]. Group numbers cannot tell any
one person what will happen. But “about three and a half years” and “half of patients alive at ten years” are
different lives, and a patient deserves the second number when it is the true one.</p>
<p>I built this so the next person does not start from a phone call and a paragraph from 2016. If that is you,
<a href="#first-steps">start with the first-steps guide</a>.</p>
<div class="hero-actions" style="justify-content:flex-start">
<a class="btn btn-outline" href="{post_url}" rel="noopener">My first account, 2025</a>
<a class="btn btn-outline" href="{post2_url}" rel="noopener">Four years on</a>
</div>
""",
    },
]

ETYMOLOGY = [
    ("Myo", "muscle", "From the Greek <em>mys</em>. The cells contract like muscle."),
    ("epithelial", "lining tissue", "They belong to epithelium, the tissue that forms glands and linings."),
    ("carcinoma", "epithelial cancer", "From <em>karkinos</em>, crab. A malignant tumor of epithelial cells."),
]

TIMELINE = [
    ("1957", "early", "The first indexed report", "A German pathology journal describes a malignant myoepithelioma of the sweat glands[[devenyi1957]]."),
    ("1977", "early", "A parotid case in <em>Cancer</em>", "Malignant myoepithelioma of the parotid gland is reported in a major oncology journal[[crissman1977]]."),
    ("1985", "early", "A breast case studied in detail", "Electron microscopy and immunostaining characterize a malignant myoepithelioma of the breast[[schurch1985]]."),
    ("2000", "series", "Criteria for the salivary form", "A 25-patient series sets two requirements: unequivocally malignant and exclusively myoepithelial[[savera2000]]."),
    ("2003", "series", "101 soft-tissue tumors", "A 101-tumor soft-tissue series finds that malignant cases recur in 42% and metastasize in 32%[[hornick2003]]. A 20-case series maps the skin tumors[[mentzel2003]]."),
    ("2004", "series", "Cutaneous myoepithelioma", "Fourteen purely myoepithelial tumors of the skin are described, one of them a carcinoma[[hornick2004]]."),
    ("2007", "series", "A pediatric series", "Twenty-nine pediatric soft-tissue carcinomas show an aggressive course[[gleason2007]]."),
    ("2008", "genetic", "A fusion gene is found", "A translocation joining EWSR1 and PBX1 is identified in a myoepithelioma[[brandal2008]]."),
    ("2010", "genetic", "EWSR1 in 45%", "A study of 66 tumors finds EWSR1 rearranged in nearly half and identifies the POU5F1 partner[[antonescu2010]]."),
    ("2013", "genetic", "PLAG1 in skin and soft tissue", "Duct-forming tumors of skin and soft tissue are tied to PLAG1, like salivary mixed tumors[[antonescu2013]]."),
    ("2017", "genetic", "Fusions in most salivary cases", "Integrated genomics finds fusions in 70% of 40 salivary carcinomas[[dalin2017]]. A SEER study puts incidence at 0.013 per 100,000[[zhang2017]]."),
    ("2019", "modern", "691 patients pooled", "A systematic review gathers individual data from 340 publications[[giridhar2019]]."),
    ("2022", "modern", "A patient organization", "cureMEC: The Myoepithelial Carcinoma Project is launched[[curemec2026]]."),
    ("2026", "modern", "Three large studies", "Methylation profiling separates fusion groups[[michal2026]], a 27-patient sequencing cohort is shared with researchers[[kashyap2026]], and a National Cancer Database analysis reports 336 cases[[tandon2026]]."),
]

FAQ = [
    ("What is myoepithelial carcinoma?",
     "Myoepithelial carcinoma is a rare malignant tumor of myoepithelial cells, the contractile cells that surround glands. "
     "It occurs in the salivary glands, soft tissue, skin, breast and other sites. In the salivary glands the diagnosis "
     "requires a tumor that is unequivocally malignant and exclusively myoepithelial[[savera2000]]. It was formerly called malignant myoepithelioma."),
    ("How rare is myoepithelial carcinoma?",
     "About 0.013 cases per 100,000 people per year. That figure comes from 368 patients recorded in the U.S. SEER registry "
     "between 1973 and 2012[[zhang2017]]. The U.S. National Cancer Database recorded 336 cases between 2004 and 2020[[tandon2026]]."),
    ("What is the survival rate for myoepithelial carcinoma?",
     "In the U.S. National Cancer Database, covering all body sites, survival was 79.4% at two years, 66.5% at five years and "
     "52.0% at ten years[[tandon2026]]. A pooled analysis of 691 published patients found a median overall survival of 167 months[[giridhar2019]]. "
     "For major salivary gland cases in SEER the median was 142 months[[luo2022]]. Some groups do worse: in a series of children "
     "with soft-tissue tumors, 43% died of the disease[[gleason2007]]. These are group figures and do not predict an individual's course."),
    ("Where in the body does myoepithelial carcinoma occur?",
     "Most often the major salivary glands, especially the parotid, followed by the minor salivary glands, skin and soft tissue, "
     "and breast[[giridhar2019]][[luo2022]]. In soft tissue it mostly affects the limbs and limb girdles[[hornick2003]]."),
    ("Is myoepithelial carcinoma the same as epithelial-myoepithelial carcinoma?",
     "No. Standard vocabularies list them as separate diagnoses[[vocab]]. Myoepithelial carcinoma is made of myoepithelial cells alone[[savera2000]]. "
     "It is also distinct from myoepithelioma, the benign tumor of the same cells[[jo2015]]."),
    ("How is myoepithelial carcinoma treated?",
     "Surgery is the main treatment, and complete removal with clear margins is associated with better outcomes[[giridhar2019]]. "
     "Radiotherapy after surgery reduced local recurrence in a pooled analysis[[giridhar2019]]. Evidence for chemotherapy is limited[[chamberlain2020]], "
     "and there is no established standard drug treatment[[curemec2026]]. Treatment decisions belong with a specialist team."),
    ("What gene changes cause myoepithelial carcinoma?",
     "Many tumors carry a gene fusion. EWSR1 is rearranged in 45% of myoepithelial tumors outside the salivary glands[[antonescu2010]]. "
     "In the salivary glands 70% carry a fusion, most involving PLAG1[[dalin2017]]. Known EWSR1 partners include PBX1, PBX3, POU5F1, "
     "ZNF444, ATF1 and KLF15[[antonescu2010]][[flucke2012]][[michal2026]]."),
    ("Can myoepithelial carcinoma occur in the skin?",
     "Yes, though it is very rare there. A 2026 review counted 26 known cases of primary cutaneous myoepithelial carcinoma and "
     "noted a high rate of local recurrence and metastasis[[gillis2026]]."),
    ("Does myoepithelial carcinoma occur in children?",
     "Yes. About 20% of soft-tissue myoepithelial tumors occur in children, in whom they are frequently malignant[[jo2015]]. "
     "A series of 29 pediatric cases found an aggressive course[[gleason2007]]."),
    ("Are there clinical trials for myoepithelial carcinoma?",
     "ClinicalTrials.gov lists {n_trials_named} records that mention the disease[[ctgov]]. Trials for salivary gland cancers, soft-tissue sarcomas "
     "and rare tumors may also accept the diagnosis. A treating oncologist can check eligibility."),
    ("Is there a patient organization for myoepithelial carcinoma?",
     "cureMEC: The Myoepithelial Carcinoma Project is a patient-driven research initiative launched in 2022[[curemec2026]]."),
]

# One-line summaries shown under section headings.
LEADS = {
    "what-it-is": "A cancer of the cells that squeeze glands, at the malignant end of a spectrum that begins with benign mixed tumors[[jo2015]].",
    "where": "Most often the salivary glands, then soft tissue, skin and breast[[giridhar2019]].",
    "rarity": "About one new case for every 7.7 million people each year[[zhang2017]].",
    "diagnosis": "A panel of stains under the microscope, usually keratin with S-100[[jo2015]]. In one series most tumors had first been given another diagnosis[[savera2000]].",
    "genetics": "Two genetic families, EWSR1 and PLAG1, that arise in different places and behave differently[[michal2026]].",
    "outcomes": "Across all sites, about two in three patients were alive at five years and about half at ten[[tandon2026]].",
    "treatment": "Surgery with clear margins first, radiotherapy sometimes, and no standard drug treatment yet[[giridhar2019]][[curemec2026]].",
    "skin": "A 2026 review found 26 reported cases of primary skin carcinoma[[gillis2026]].",
    "children": "Frequently malignant in children, and often aggressive[[jo2015]][[gleason2007]].",
}

# "What I was told" against "what the research says": (topic, then, now)
COMPARE = [
    ("How long",
     "“Average lifespan after diagnosis? 3.5 years.”[[post]]",
     "Median overall survival of 167 months, about 14 years, in 691 pooled patients[[giridhar2019]]. In 336 U.S. registry patients, 66.5% were alive at five years and 52.0% at ten[[tandon2026]]."),
    ("Who survives",
     "“So… all of them grew more tumors and died?”[[post]]",
     "In the four series that count deaths from the disease, between 13% and 43% of patients had died of it at last follow-up. Most had not[[hornick2003]][[savera2000]][[chamberlain2020]][[gleason2007]]."),
    ("What is known",
     "“…nobody on this earth actually knows anything about this cancer and a proper standard of care.”[[post]]",
     "{n_core} papers name the disease, the first in 1957[[devenyi1957]]. Its gene fusions have been mapped since 2008[[brandal2008]] and patients have organized since 2022[[curemec2026]]. There is still no standard drug treatment[[curemec2026]]."),
    ("The cause",
     "“It’s just bad luck.”[[post]]",
     "Many tumors carry a specific gene fusion: 70% of salivary cases[[dalin2017]] and 45% of tumors elsewhere[[antonescu2010]]. Why the fusion happens is not known."),
]

FIRST_THREE = [
    ("You have time to think", "This is seldom a same-day decision. Ask your doctor how long you can safely take, then use that time for a second opinion."),
    ("The first numbers you find are not the whole story", "Old summaries and small studies read worse than the larger datasets. The <a href=\"#outcomes\">survival figures</a> are set out below, with their sources."),
    ("People have walked this before", "At least 691 patients are described in the medical literature[[giridhar2019]], and there is a patient organization[[curemec2026]]."),
]

PLAN = [
    ("Get the pathology report in your hands",
     "Ask for the full written report. Find three things on it: the exact diagnosis line, the stains that were positive, and what it says about the margin. Peter’s read “adnexal carcinoma, consistent with myoepithelial carcinoma,” with invasion close to the margin[[post]]."),
    ("Get the slides read a second time",
     "Ask for a second pathology opinion at a center that sees these tumors. In one series most cases had first been given a different diagnosis[[savera2000]]. Peter’s diagnosis came from a second-opinion review[[post]]."),
    ("Ask about fusion testing",
     "Ask whether the tumor has been tested for gene fusions such as EWSR1 and PLAG1, and for INI1. The result affects how the tumor is classified and what is known about how it behaves[[michal2026]][[jo2015]]."),
    ("Find a team that has seen it",
     "Ask each doctor how many cases they have treated. The published series come from specialist units: a sarcoma unit for soft-tissue disease[[chamberlain2020]], tertiary cancer centers for salivary disease[[kane2010]]. Ask for your case to go to a tumor board."),
    ("Know what the scans show",
     "Ask which scans are needed to look for spread, and keep copies of the images and the reports. PET, CT and MRI were ordered for Peter[[post]]."),
    ("Talk about margins, before surgery and after",
     "Complete removal with clear margins was associated with better survival in the pooled data[[giridhar2019]]. Ask whether the margin was clear, what happens if it was not, and whether radiotherapy afterward is worth discussing[[giridhar2019]]."),
    ("Ask about trials, and about your tissue",
     "The authors of the adult soft-tissue series say trial enrollment should be encouraged[[chamberlain2020]]. Ask whether your tissue can be banked for research. cureMEC is building biospecimen collections[[curemec2026]], and Peter donates his[[post]]."),
    ("Set a surveillance schedule and keep it",
     "This disease returns often. In a 101-tumor soft-tissue series, 42% of malignant tumors recurred, and follow-up ran as long as 21 years[[hornick2003]]. Agree how often you will be checked, and do not let it slide when you feel well."),
]

QUESTIONS = [
    "What exactly does my pathology report say, and has it had a second opinion?",
    "Where did it start, and how large and how deep was it?",
    "Were the margins clear?",
    "Has it been tested for EWSR1, PLAG1 and INI1?",
    "What do my scans show?",
    "How many patients with this diagnosis have you treated?",
    "Will a tumor board review my case?",
    "What are my options, and what happens if we wait?",
    "Is radiotherapy worth considering after surgery?",
    "Is there a trial I could join, and can my tissue go to research?",
    "How often will I be checked, and with which scans?",
    "Who do I call between appointments?",
]

# From Peter's newsletter, "Keep Calm and Carry On", June 2024: (when you are, do this)
CALM = [
    ("Overthinking", "Write"), ("Stuck", "Walk"), ("Tired", "Sleep"), ("Confused", "Ask"),
    ("Frustrated", "Move"), ("Burned out", "Take a day off"), ("Impatient", "Review progress"),
    ("Unmotivated", "Remember your why"),
]

HOPE = [
    ("52%", "of patients alive at ten years in the U.S. National Cancer Database[[tandon2026]]"),
    ("14 years", "median overall survival across 691 published patients[[giridhar2019]]"),
    ("27", "patients’ tumor sequencing made available to researchers through the EGA archive[[kashyap2026]]"),
    ("2022", "the year patients organized their own research project[[curemec2026]]"),
]

# The benign-to-malignant spectrum: (name, status, css class, description)
SPECTRUM = [
    ("Mixed tumor", "Benign", "benign",
     "Ducts plus myoepithelial cells. Called pleomorphic adenoma in the salivary glands and chondroid syringoma in the skin[[hornick2004]]."),
    ("Myoepithelioma", "Benign", "benign",
     "Myoepithelial cells only. Recurs in up to 20%, usually after incomplete removal, and does not metastasize[[jo2015]]."),
    ("Myoepithelial carcinoma", "Malignant", "malignant",
     "Myoepithelial cells with malignant features. Recurrence and metastasis in up to 40 to 50%[[jo2015]]."),
]

# Fusion families: (name, css class, facts, partner genes, sources)
FUSION_FAMILIES = [
    ("EWSR1 and FUS family", "fam-a",
     [("Where", "Soft tissue, skin, bone"), ("Who", "All ages. The KLF15 and POU5F1 fusions occur in children and young adults"),
      ("Behavior", "Includes the groups with the shortest survival")],
     ["PBX1", "PBX3", "POU5F1", "ZNF444", "ATF1", "KLF15", "KLF17"],
     "[[antonescu2010]][[flucke2012]][[michal2026]]"),
    ("PLAG1 family", "fam-b",
     [("Where", "Salivary glands, and duct-forming tumors of skin and soft tissue"), ("Who", "In the skin, mostly older adults"),
      ("Behavior", "Mostly benign in skin and soft tissue, but also found in many salivary carcinomas")],
     ["FGFR1", "TGFBR3", "LIFR", "TRPS1"],
     "[[dalin2017]][[antonescu2013]][[michal2026]][[gillis2026]]"),
]

# Deaths from the disease during follow-up: (series, patients followed, died of disease, note, ref)
SERIES_DEATHS = [
    ("Soft tissue, 2003", 31, 4, "mean follow-up 50 months", "[[hornick2003]]"),
    ("Salivary, 2000", 17, 5, "deaths at a mean of 32 months", "[[savera2000]]"),
    ("Soft tissue, adults, 2020", 24, 10, "median follow-up 3.9 years", "[[chamberlain2020]]"),
    ("Soft tissue, children, 2007", 23, 10, "deaths at a median of 9 months", "[[gleason2007]]"),
]

# Survival across all sites, National Cancer Database: (label, percent alive)
SURVIVAL_POINTS = [("2 years", 79.4), ("5 years", 66.5), ("10 years", 52.0)]

FAQ.insert(3, (
    "What should I do after a myoepithelial carcinoma diagnosis?",
    "Get the written pathology report and a second pathology opinion, because misdiagnosis is common[[savera2000]]. Ask whether the tumor "
    "has been tested for gene fusions[[michal2026]]. Find a team that has treated the disease, discuss surgery with clear margins[[giridhar2019]], "
    "ask about clinical trials[[chamberlain2020]], and agree a long-term surveillance schedule, since recurrence is common[[hornick2003]]. "
    "Do each of these with your doctors."))

GLOSSARY = [
    ("Adnexal", "Belonging to the skin's appendages: the sweat glands, oil glands and hair follicles."),
    ("Carcinoma", "A cancer that arises from epithelial cells, the cells that line surfaces and form glands."),
    ("Chondroid syringoma", "The name for a mixed tumor when it arises in the skin."),
    ("FISH", "Fluorescence in situ hybridization. A laboratory test that shows whether a gene has been broken or moved."),
    ("Gene fusion", "Two genes joined abnormally into one hybrid gene. Written with a double colon, as in EWSR1::PBX1."),
    ("Grade", "How abnormal the cells look and how fast they are dividing. High grade means more aggressive."),
    ("Immunostain", "A stain that shows which proteins a tumor's cells make. Pathologists use a panel of them to identify the cell type."),
    ("INI1", "A protein, also called SMARCB1, that restrains cell growth. Some myoepithelial carcinomas have lost it[[jo2015]]."),
    ("Local recurrence", "The tumor returning at or near the place it was removed from."),
    ("Margin", "The rim of normal tissue removed around a tumor. A clear or negative margin has no tumor cells at its edge. An R0 resection is complete removal with clear margins."),
    ("Median", "The middle value. With a median survival of ten years, half of the patients lived longer than ten years and half did not."),
    ("Metastasis", "Spread of the cancer to another part of the body."),
    ("Mitotic rate", "The number of dividing cells counted under the microscope. A higher count means faster growth."),
    ("Mixed tumor", "A tumor with ducts as well as myoepithelial cells. Called pleomorphic adenoma in the salivary glands."),
    ("Mohs surgery", "A way of removing a skin cancer one thin layer at a time, checking each layer under the microscope before taking the next."),
    ("Myoepithelial cell", "A contractile cell that sits around a gland and squeezes its secretions out."),
    ("Myoepithelioma", "The benign tumor of myoepithelial cells."),
    ("Overall survival", "The share of patients alive at a given time, whatever the cause of any deaths."),
    ("Progression-free survival", "The time during which the disease does not grow or spread."),
    ("Sarcoma", "A cancer of connective tissue such as bone, muscle or fat."),
    ("Surveillance", "Scheduled examinations and scans after treatment, to catch a return early."),
    ("Tumor board", "A meeting at which surgeons, oncologists, radiologists and pathologists review a case together."),
]
