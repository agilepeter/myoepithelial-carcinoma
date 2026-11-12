"""Search definitions. Edit here to widen or narrow what the corpus collects.

Scope: myoepithelial carcinoma (also called malignant myoepithelioma) at any body
site, plus the neighbouring entities needed to understand it: benign
myoepithelioma, myoepithelial tumours of soft tissue and skin, and
epithelial-myoepithelial carcinoma (a distinct diagnosis, kept as "related").

Peter's own diagnosis is "adnexal carcinoma, consistent with myoepithelial
carcinoma" of the skin (the report is quoted on the site), so the skin and adnexal
neighbourhood is searched explicitly: mixed tumours of the skin (chondroid
syringoma) and their malignant form, and cutaneous adnexal carcinomas as a group.
"""

# Phrases that name the disease itself.
CORE_PHRASES = [
    "myoepithelial carcinoma",
    "myoepithelial carcinomas",
    "malignant myoepithelioma",
    "malignant myoepitheliomas",
    "malignant myoepithelial",
]

# Phrases for neighbouring entities.
RELATED_PHRASES = [
    "myoepithelioma",
    "myoepitheliomas",
    "myoepithelial tumor",
    "myoepithelial tumors",
    "myoepithelial tumour",
    "myoepithelial tumours",
    "myoepithelial neoplasm",
    "myoepithelial neoplasms",
    "epithelial-myoepithelial carcinoma",
    "epithelial myoepithelial carcinoma",
]

# Phrases for the skin and adnexal neighbourhood.
CUTANEOUS_PHRASES = [
    "chondroid syringoma",
    "chondroid syringomas",
    "cutaneous mixed tumor",
    "cutaneous mixed tumour",
    "mixed tumor of the skin",
    "mixed tumour of the skin",
    "mixed tumor of skin",
    "mixed tumour of skin",
    "apocrine mixed tumor",
    "eccrine mixed tumor",
    "adnexal carcinoma",
    "adnexal carcinomas",
    "malignant adnexal tumor",
    "malignant adnexal tumors",
    "malignant adnexal tumour",
    "malignant adnexal tumours",
]

# Words that, next to "myoepithelial", mark a skin or adnexal paper.
SKIN_WORDS = ["skin", "cutaneous", "adnexal", "dermal", "subcutaneous"]


def _q(p):
    return '"%s"' % p


# PubMed: core phrases in any field, related and cutaneous phrases in
# title/abstract, the MeSH heading that covers all myoepithelial tumours, and
# "myoepithelial" together with a skin word.
PUBMED_QUERY = " OR ".join(
    [_q(p) for p in CORE_PHRASES]
    + ['"Myoepithelioma"[Mesh]']
    + ["%s[tiab]" % _q(p) for p in RELATED_PHRASES + CUTANEOUS_PHRASES]
    + ["(myoepithelial[tiab] AND (%s))" % " OR ".join("%s[tiab]" % w for w in SKIN_WORDS)]
)

# Europe PMC: core phrases anywhere (this searches full text too), the rest in
# title or abstract.
_rel = " OR ".join(_q(p) for p in RELATED_PHRASES + CUTANEOUS_PHRASES)
_skin = " OR ".join(SKIN_WORDS)
EUROPEPMC_QUERY = (
    "(%s) OR TITLE:(%s) OR ABSTRACT:(%s)"
    " OR (TITLE:myoepithelial AND TITLE:(%s)) OR (ABSTRACT:myoepithelial AND ABSTRACT:(%s))"
) % (" OR ".join(_q(p) for p in CORE_PHRASES), _rel, _rel, _skin, _skin)

# OpenAlex: (label, API parameter, value). Results are merged.
# "search" covers title, abstract and (where indexed) full text, so it is used
# for the core phrases only. Other phrases are limited to title and abstract.
OPENALEX_QUERIES = [
    ("core_anywhere", "search",
     '"myoepithelial carcinoma" OR "malignant myoepithelioma"'),
    ("all_title_abstract", "filter",
     'title_and_abstract.search:"myoepithelial carcinoma" OR "malignant myoepithelioma"'
     ' OR myoepithelioma OR "myoepithelial tumor" OR "myoepithelial tumour"'
     ' OR "myoepithelial neoplasm" OR "epithelial-myoepithelial carcinoma"'),
    ("cutaneous_title_abstract", "filter",
     'title_and_abstract.search:"chondroid syringoma" OR "cutaneous mixed tumor"'
     ' OR "cutaneous mixed tumour" OR "mixed tumor of the skin" OR "mixed tumour of the skin"'
     ' OR "adnexal carcinoma" OR "malignant adnexal tumor" OR "malignant adnexal tumour"'),
]

# ClinicalTrials.gov: (label, API parameter, value)
CTGOV_SEARCHES = [
    ("names_myoepithelial", "query.term", "myoepithelial OR myoepithelioma"),
    ("salivary_gland", "query.cond",
     "Salivary Gland Neoplasms OR Salivary Gland Cancer OR Salivary Gland Carcinoma"
     " OR Salivary Gland Tumor"),
    ("skin_adnexal", "query.term",
     '"adnexal carcinoma" OR "adnexal tumor" OR "sweat gland carcinoma"'
     ' OR "skin appendage" OR "chondroid syringoma"'),
]
