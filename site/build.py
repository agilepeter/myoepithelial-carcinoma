"""Build the public page from the catalog.

    python site/build.py            writes site/dist/
    python site/build.py --serve    builds, then serves http://localhost:8000/myoepithelial-carcinoma/

Output:
    dist/myoepithelial-carcinoma/index.html          the compendium page
    dist/myoepithelial-carcinoma/papers/index.html   the directory of papers
    dist/myoepithelial-carcinoma/data/*              open data (no abstracts)
    dist/robots.txt, dist/sitemap.xml

Text lives in content.py. Numbers and charts are computed here from
data/catalog/, so the page cannot drift from the data.
"""

import collections
import csv
import datetime
import html
import io
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import content as C  # noqa: E402

ROOT = HERE.parent
CATALOG = ROOT / "data" / "catalog"
FULLTEXT = ROOT / "data" / "fulltext"
DIST = HERE / "dist"
SLUG = "myoepithelial-carcinoma"
# An email address in the output is either a private person's or a researcher's quoted from a public record.
# Neither belongs on the site: the contact route is CONTACT_URL. build() fails if one gets through.
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
OUT = DIST / SLUG

SITE_LABELS = collections.OrderedDict([
    ("salivary", "Salivary glands"), ("soft_tissue", "Soft tissue"), ("skin", "Skin"),
    ("head_neck_other", "Other head and neck"), ("breast", "Breast"), ("lung", "Lung and airway"),
    ("bone", "Bone"), ("gyn", "Gynecologic"), ("pediatric", "Children"),
])
LANG_NAMES = {
    "zh": "Chinese", "de": "German", "ja": "Japanese", "es": "Spanish", "fr": "French",
    "ko": "Korean", "tr": "Turkish", "ru": "Russian", "it": "Italian", "cs": "Czech",
    "nl": "Dutch", "id": "Indonesian", "pt": "Portuguese", "sr": "Serbian", "pl": "Polish",
    "no": "Norwegian", "en": "English", "hu": "Hungarian", "sv": "Swedish", "da": "Danish",
}
# Surnames too common to count by "Surname Initial" without merging people.
COMMON_SURNAMES = {"Zhang", "Wang", "Li", "Chen", "Liu", "Yang", "Kim", "Lee", "Xu", "Wu", "Zhao", "Huang", "Zhou", "Lin", "Park"}
LIVE_STATUS = {"RECRUITING", "NOT_YET_RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION"}
# Marker positivity in 101 soft-tissue myoepithelial tumours (Hornick and Fletcher 2003).
MARKERS = [("Keratins", 93), ("S-100 protein", 87), ("Calponin", 86), ("EMA", 63),
           ("GFAP", 46), ("Smooth muscle actin", 36), ("p63", 23), ("Desmin", 14)]


def esc(text):
    return html.escape(re.sub(r"<[^>]+>", "", text or "").strip(), quote=True)


def num(n):
    return "{:,}".format(n)


def read_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def paper_url(p):
    if p.get("pmid"):
        return "https://pubmed.ncbi.nlm.nih.gov/%s/" % p["pmid"]
    if p.get("doi"):
        return "https://doi.org/%s" % p["doi"]
    return ""


def short_authors(p, limit=3):
    names = [a for a in p.get("authors") or [] if a]
    if not names:
        return ""
    return ", ".join(names[:limit]) + (" et al" if len(names) > limit else "")


# ---------------------------------------------------------------- references

class References:
    """Numbers [[key]] markers in order of first appearance."""

    def __init__(self, by_id, ctx):
        self.by_id = by_id
        self.ctx = ctx
        self.order = []

    def cite(self, text):
        def repl(match):
            key = match.group(1)
            if key not in C.REFS:
                raise KeyError("content.py cites [[%s]] but REFS has no such key" % key)
            first = key not in self.order
            if first:
                self.order.append(key)
            n = self.order.index(key) + 1
            anchor = ' id="fn-%d"' % n if first else ""
            return '<sup class="fn"><a href="#ref-%d"%s aria-label="Reference %d">%d</a></sup>' % (n, anchor, n, n)
        return re.sub(r"\[\[(\w+)\]\]", repl, text)

    def entry(self, key, link=True):
        src = C.REFS[key]
        if isinstance(src, dict):
            text = esc(src["text"].format(**self.ctx))
            url = src["url"]
            label = "source" if url.startswith("http") else "method"
        else:
            p = self.by_id.get(src)
            if p is None:
                raise KeyError("reference %s points at %s, which is not in the catalog" % (key, src))
            authors = short_authors(p, 3)
            title = esc(p["title"]).rstrip(".")
            journal = esc(p["journal"])
            text = "%s%s. <em>%s</em>%s." % (
                esc(authors) + ". " if authors else "", title, journal,
                ", %s" % p["year"] if p["year"] else "")
            url = paper_url(p)
            label = "PubMed" if p.get("pmid") else "DOI"
        if not link:
            return text
        rel = ' rel="noopener"' if url.startswith("http") else ""
        return '%s <a href="%s"%s>%s</a>' % (text, esc(url), rel, label)

    def render(self):
        items = []
        for n, key in enumerate(self.order, 1):
            items.append('<li id="ref-%d">%s <a href="#fn-%d" class="ref-back" aria-label="Back to text">↩</a></li>'
                         % (n, self.entry(key), n))
        return '<div class="references"><ol>%s</ol></div>' % "\n".join(items)


def plain(text):
    """Strip markers and tags, for meta tags and structured data."""
    text = re.sub(r"\[\[\w+\]\]", "", text)
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


# ---------------------------------------------------------------- components

def bars(rows, suffix="", maximum=None, label="", wide=False):
    """Horizontal bars, one hue. rows: (name, value)."""
    top = maximum or max(v for _, v in rows) or 1
    out = ['<div class="bars%s" role="list" aria-label="%s">' % (" wide" if wide else "", esc(label))]
    for name, value in rows:
        shown = "%s%s" % (num(value), suffix)
        out.append(
            '<div class="bar-row" role="listitem" title="%s: %s">'
            '<div class="bar-label">%s</div>'
            '<div class="bar-track"><div class="bar-fill" style="width:%.1f%%"></div></div>'
            '<div class="bar-count">%s</div></div>'
            % (esc(name), shown, esc(name), 100.0 * value / top, shown))
    out.append("</div>")
    return "\n".join(out)


def segbar(parts, label):
    """One whole split into parts. parts: (name, value, css colour variable)."""
    total = sum(v for _, v, _ in parts) or 1
    blocks, keys = [], []
    for name, value, colour in parts:
        share = 100.0 * value / total
        text = "%s · %d%%" % (num(value), round(share)) if share >= 12 else ""
        blocks.append('<div class="seg-part" style="flex:%d 1 0;background:var(%s)" title="%s: %s (%d%%)">%s</div>'
                      % (max(value, 1), colour, esc(name), num(value), round(share), text))
        keys.append('<span><span class="key" style="background:var(%s)"></span>%s</span>' % (colour, esc(name)))
    rows = "".join('<tr><td>%s</td><td class="num">%s</td><td class="num">%d%%</td></tr>'
                   % (esc(n), num(v), round(100.0 * v / total)) for n, v, _ in parts)
    return (
        '<div class="segbar" role="img" aria-label="%s">%s</div><div class="legend">%s</div>'
        '<details class="table-view"><summary>View as table</summary><table class="data-table">'
        '<thead><tr><th>Group</th><th>Papers</th><th>Share</th></tr></thead><tbody>%s</tbody></table></details>'
        % (esc(label), "".join(blocks), "".join(keys), rows))


def year_chart(counts, first, last):
    """Column chart of papers per year, with hover tooltips and a table view."""
    width, height = 860, 250
    left, right, top, bottom = 36, 8, 22, 26
    years = list(range(first, last + 1))
    peak = max(counts.get(y, 0) for y in years) or 1
    step = 10 if peak <= 60 else 20
    ymax = (peak // step + 1) * step
    plot_w, plot_h = width - left - right, height - top - bottom
    slot = plot_w / len(years)
    col_w = min(24.0, slot * 0.72)
    peak_year = max(years, key=lambda y: (counts.get(y, 0), y if y != last else 0))
    out = ['<div class="chart" data-h="%d"><svg viewBox="0 0 %d %d" role="img" aria-label="Papers naming '
           'myoepithelial carcinoma, per year, %d to %d">' % (height, width, height, first, last)]
    for tick in range(0, ymax + 1, step):
        y = top + plot_h - plot_h * tick / ymax
        out.append('<line class="%s" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/>'
                   % ("axis" if tick == 0 else "gridline", left, width - right, y, y))
        out.append('<text class="tick" x="%d" y="%.1f" text-anchor="end">%d</text>' % (left - 6, y + 4, tick))
    for i, year in enumerate(years):
        n = counts.get(year, 0)
        x = left + slot * i + (slot - col_w) / 2
        h = plot_h * n / ymax
        y = top + plot_h - h
        note = " (year incomplete)" if year == last else ""
        out.append('<rect class="hit" x="%.1f" y="%d" width="%.1f" height="%d" data-top="%.1f" '
                   'data-tip="%d: %d paper%s%s"/>'
                   % (left + slot * i, top, slot, plot_h, y, year, n, "" if n == 1 else "s", note))
        if n:
            r = min(4.0, col_w / 2, h)
            path = ("M%.1f %.1f v%.1f q0 -%.1f %.1f -%.1f h%.1f q%.1f 0 %.1f %.1f v%.1f z"
                    % (x, top + plot_h, -(h - r), r, r, r, col_w - 2 * r, r, r, r, h - r))
            out.append('<path class="col%s" d="%s" pointer-events="none"/>'
                       % (" partial" if year == last else "", path))
        if year % 10 == 0:
            out.append('<text class="tick" x="%.1f" y="%d" text-anchor="middle">%d</text>'
                       % (left + slot * i + slot / 2, height - 8, year))
        if year == peak_year:
            out.append('<text class="dlabel" x="%.1f" y="%.1f" text-anchor="middle">%d</text>'
                       % (left + slot * i + slot / 2, y - 6, n))
    out.append('</svg><div class="tooltip" role="status"></div></div>')
    decades = collections.OrderedDict()
    for year in sorted(counts):
        decades.setdefault("%ds" % (year // 10 * 10), 0)
        decades["%ds" % (year // 10 * 10)] += counts[year]
    rows = "".join('<tr><td>%s</td><td class="num">%s</td></tr>' % (d, num(n)) for d, n in decades.items())
    out.append('<details class="table-view"><summary>View as table, by decade</summary><table class="data-table">'
               '<thead><tr><th>Decade</th><th>Papers</th></tr></thead><tbody>%s</tbody></table></details>' % rows)
    return "\n".join(out)


def gland_svg():
    """A schematic gland: secreting cells around a lumen, with myoepithelial cells outside them."""
    import math
    cx, cy = 150, 62

    def pt(r, deg):
        a = math.radians(deg)
        return cx + r * math.cos(a), cy + r * math.sin(a)

    def sector(r0, r1, a0, a1):
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pt(r1, a0), pt(r1, a1), pt(r0, a1), pt(r0, a0)
        return ("M%.1f %.1f A%d %d 0 0 1 %.1f %.1f L%.1f %.1f A%d %d 0 0 0 %.1f %.1f Z"
                % (x0, y0, round(r1), round(r1), x1, y1, x2, y2, round(r0), round(r0), x3, y3))

    out = ['<svg viewBox="0 0 320 124" role="img" aria-label="Schematic cross-section of a gland, showing '
           'myoepithelial cells around the secreting cells">',
           '<circle cx="%d" cy="%d" r="52" fill="none" stroke="#8a857c" stroke-width="1.3"/>' % (cx, cy)]
    for i in range(8):
        out.append('<path d="%s" fill="#f1dfc4" stroke="#c7ad86" stroke-width="1"/>' % sector(12, 40, i * 45 + 1.8, (i + 1) * 45 - 1.8))
        out.append('<circle cx="%.1f" cy="%.1f" r="3.4" fill="#b98e5c"/>' % pt(30, i * 45 + 22.5))
    for a0 in (-80, -8, 64, 136, 208):
        out.append('<path d="%s" fill="#0e4a5b"/>' % sector(42.5, 49, a0, a0 + 56))
        nx, ny = pt(45.7, a0 + 28)
        out.append('<ellipse cx="%.1f" cy="%.1f" rx="4.6" ry="2.1" fill="#062832" transform="rotate(%.1f %.1f %.1f)"/>'
                   % (nx, ny, a0 + 118, nx, ny))
    labels = [("Myoepithelial cell", pt(45.7, -34), 222, 26, "start"), ("Secreting cell", pt(30, 22.5), 222, 72, "start"),
              ("Outer membrane", pt(52, 50), 222, 114, "start"), ("Lumen", pt(3, 180), 62, 66, "end")]
    for text, (x, y), lx, ly, anchor in labels:
        out.append('<line x1="%.1f" y1="%.1f" x2="%d" y2="%.1f" stroke="#47443e" stroke-width="0.8"/>'
                   % (x, y, lx - 4 if anchor == "start" else lx + 4, ly - 3.5))
        out.append('<text x="%d" y="%d" font-size="10.5" font-family="Segoe UI, Arial, sans-serif" fill="#1c1b19" '
                   'text-anchor="%s">%s</text>' % (lx, ly, anchor, text))
    out.append("</svg>")
    return "".join(out)


def people_grid(alive):
    """A 10 by 10 grid of dots, the first `alive` of them filled."""
    dots = "".join('<circle cx="%d" cy="%d" r="5" class="%s"/>'
                   % (7 + (i % 10) * 14, 7 + (i // 10) * 14, "on" if i < alive else "off") for i in range(100))
    return '<svg viewBox="0 0 140 140" role="img" aria-label="%d of 100 people alive">%s</svg>' % (alive, dots)


def build():
    papers = read_jsonl(CATALOG / "papers.jsonl")
    trials = read_jsonl(CATALOG / "trials.jsonl")
    by_id = {p["id"]: p for p in papers}
    grants = read_jsonl(CATALOG / "grants.jsonl")
    datasets = read_jsonl(CATALOG / "datasets.jsonl")
    terminology = json.loads((CATALOG / "terminology.json").read_text(encoding="utf-8"))
    cases = read_jsonl(CATALOG / "cases.jsonl")
    centers = json.loads((CATALOG / "centers.json").read_text(encoding="utf-8"))
    models = read_jsonl(CATALOG / "models.jsonl")
    orgs = json.loads((CATALOG / "organizations.json").read_text(encoding="utf-8"))
    harvest_log = read_jsonl(CATALOG / "harvest_log.jsonl")
    first_seen = json.loads((CATALOG / "first_seen.json").read_text(encoding="utf-8"))

    def optional(name):
        path = CATALOG / name
        return read_jsonl(path) if path.exists() else []
    treatments, trials_read = optional("treatments.jsonl"), optional("trials_read.jsonl")
    stains = [s for s in optional("stains.jsonl") if not str(s.get("id", "")).startswith("doi:10.3410/f.")]
    lookalikes, skin_cases, verification = optional("lookalikes.jsonl"), optional("skin_cases.jsonl"), optional("verification.jsonl")
    have = {f.name[:-7] for f in FULLTEXT.glob("PMC*.xml.gz")}
    if not have:
        # The public copy of this repo carries no full text, only the list of which papers are held.
        have = {r["pmcid"] for r in optional("fulltext_held.jsonl")}
    today = datetime.date.today()

    core = [p for p in papers if p["tier"] == "core"]
    titled = [p for p in core if p["named_in_title"] and not p["is_animal"]]
    focus = [p for p in papers if p["focus"] == "primary"]
    named_trials = [t for t in trials if t["names_myoepithelial"]]

    langs = collections.Counter()
    for p in core:
        for code in (p["language"] or "").split(","):
            code = code.strip()
            if code in LANG_NAMES:
                langs[code] += 1
    by_year = collections.Counter(p["year"] for p in core if p["year"])
    year_max = max(by_year)
    n_case = sum(p["is_case_report"] for p in core)
    n_review = sum(1 for p in core if p["is_review"] and not p["is_case_report"])
    core_ft = sum(1 for p in core if p["pmcid"] in have)
    core_oa = sum(1 for p in core if p["pmcid"] not in have and p["is_oa"])
    core_closed = len(core) - core_ft - core_oa

    ctx = {
        "n_total": num(len(papers)), "n_core": num(len(core)), "n_title": num(len(titled)),
        "n_case_reports": num(n_case), "pct_case_reports": round(100.0 * n_case / len(core)),
        "n_langs": len(langs), "n_nonenglish": sum(n for c, n in langs.items() if c != "en"),
        "n_fulltext": num(len(have)), "n_skin": num(len(focus)),
        "n_trials": num(len(trials)), "n_trials_named": len(named_trials),
        "n_trials_other": num(len(trials) - len(named_trials)),
        "year_min": min(by_year), "year_max": year_max,
        "build_date": "%d %s %d" % (today.day, today.strftime("%B"), today.year),
        # When the records were last downloaded, from the harvest log. Not the day of this build.
        "harvest_date": long_date(max(h["date"] for h in harvest_log)), "check_date": C.SOURCE_CHECK_DATE,
        "post_url": C.POST_URL, "post2_url": C.POST2_URL, "contact_url": C.CONTACT_URL,
        "base_url": C.BASE_URL, "repo_url": C.REPO_URL, "repo_label": C.REPO_LABEL,
        "license_url": C.DATA_LICENSE_URL, "license_name": C.DATA_LICENSE, "license_short": C.DATA_LICENSE_SHORT,
        "n_datasets": len(datasets), "n_datasets_named": sum(d["names_disease"] for d in datasets),
        "n_grant_projects": len({g["core_project_num"] for g in grants}),
        "n_core_ft": num(core_ft), "n_core_oa": num(core_oa), "n_core_closed": num(core_closed),
        "n_cases": num(len(cases)), "n_centers": num(sum(1 for i in centers["institutions"] if i["papers"] >= 3)),
        "n_orgs": sum(1 for o in orgs if o["ok"]),
    }
    refs = References(by_id, ctx)

    # ---- components that sections embed
    comp = {}
    comp["etymology"] = '<div class="etymology">%s</div>' % '<div class="ety-plus" aria-hidden="true">+</div>'.join(
        '<div class="ety-card c%d"><div class="ety-frag">%s</div><div class="ety-label">%s</div>'
        '<div class="ety-meaning">%s</div></div>' % (i + 1, frag, label, meaning)
        for i, (frag, label, meaning) in enumerate(C.ETYMOLOGY))

    site_counts = collections.Counter(s for p in titled for s in p["sites"])
    comp["bars_sites"] = bars([(SITE_LABELS[k], site_counts[k]) for k in sorted(SITE_LABELS, key=lambda k: -site_counts[k])],
                              label="Papers by body site")
    comp["bars_markers"] = bars(MARKERS, suffix="%", maximum=100, label="Marker positivity, percent of tumors tested")
    comp["chart_years"] = year_chart(by_year, 1975, year_max)
    comp["bar_types"] = segbar([("Case reports", n_case, "--s1"), ("Reviews", n_review, "--s2"),
                                ("Series, studies and other papers", len(core) - n_case - n_review, "--s3")],
                               "Papers by type")
    comp["bars_langs"] = bars([(LANG_NAMES[c], n) for c, n in langs.most_common() if c != "en"][:10],
                              label="Non-English papers by language")
    journals = collections.Counter(p["journal"] for p in core if p["journal"])
    comp["bars_journals"] = bars([(j[:1].upper() + j[1:], n) for j, n in journals.most_common(10)], label="Papers by journal", wide=True)
    comp["coverage"] = (
        '<div class="coverage"><div class="coverage-head"><div><div class="coverage-tag">Full text in the archive</div>'
        '<div class="coverage-num">%s <span class="denom">of %s papers naming the disease</span></div></div>'
        '<div class="coverage-pct">%d%%</div></div>%s'
        '<p class="fineprint">Full text is archived where PubMed Central permits download. Open-access papers hosted '
        'only by their publisher are next to be collected. The rest sit behind a paywall and are listed, not copied.</p></div>'
        % (num(core_ft), num(len(core)), round(100.0 * core_ft / len(core)),
           segbar([("Full text archived", core_ft, "--s1"), ("Open access elsewhere", core_oa, "--s2"),
                   ("Not open access", core_closed, "--s3")], "Papers by access")))

    ranked = sorted(titled, key=lambda p: -(p["cited_by"] or 0))[:10]
    rows = []
    for i, p in enumerate(ranked, 1):
        rows.append(
            '<div class="rank%s"><div class="rank-pos">%d</div><div><div class="rank-name"><a href="%s" rel="noopener">%s</a></div>'
            '<div class="rank-detail">%s · %s · %s</div></div><div class="rank-metric">%s<small>citations</small></div></div>'
            % (" gold" if i <= 3 else "", i, esc(paper_url(p)), esc(p["title"]).rstrip("."),
               esc(short_authors(p, 2)), esc(p["journal"]), p["year"], num(p["cited_by"] or 0)))
    comp["ranking"] = '<div class="rankings">%s</div>' % "\n".join(rows)

    author_counts = collections.Counter(
        a for p in core if "pubmed" in p["sources"] for a in p["authors"] if a.split(" ")[0] not in COMMON_SURNAMES)
    comp["bars_authors"] = bars(author_counts.most_common(10), label="Papers per author")

    trial_rows = []
    for t in sorted(named_trials, key=lambda t: (t["status"] not in LIVE_STATUS, t["nct_id"])):
        status = t["status"].replace("_", " ").capitalize()
        phase = ", ".join(x.replace("PHASE", "Phase ").replace("EARLY_", "Early ") for x in t["phases"]) or t["study_type"].replace("_", " ").capitalize()
        phase = "Not applicable" if phase == "NA" else phase
        trial_rows.append(
            '<tr><td class="num"><a href="%s" rel="noopener">%s</a></td><td>%s</td><td>%s</td>'
            '<td><span class="pill%s">%s</span></td><td>%s</td></tr>'
            % (esc(t["url"]), t["nct_id"], esc(t["title"]), esc(phase),
               " live" if t["status"] in LIVE_STATUS else "", esc(status), esc(t["sponsor"])))
    comp["trials_table"] = (
        '<div class="table-wrap"><table class="data-table"><thead><tr><th>Registry ID</th><th>Trial</th><th>Phase</th>'
        '<th>Status</th><th>Sponsor</th></tr></thead><tbody>%s</tbody></table></div>' % "\n".join(trial_rows))

    eras = [("early", "First reports", "--rust"), ("series", "Case series", "--parchment"),
            ("genetic", "Genetics", "--verdant"), ("modern", "Pooled data and patients", "--accent")]
    comp["timeline"] = (
        '<div class="tl-legend">%s</div><div class="timeline">%s</div>'
        % ("".join('<span><span class="key" style="background:var(%s)"></span>%s</span>' % (c, n) for _, n, c in eras),
           "\n".join('<div class="tl-item %s"><div class="tl-year">%s</div><div class="tl-title">%s</div>'
                     '<div class="tl-desc">%s</div></div>' % (era, year, title, desc)
                     for year, era, title, desc in C.TIMELINE)))
    def names_carcinoma(name):
        low = name.lower()
        return (("myoepithelial carcinoma" in low or "malignant myoepithelioma" in low)
                and "epithelial-myoepithelial" not in low and "epithelial myoepithelial" not in low)

    code_rows = [("ICD-O-3 morphology", "8982", "Myoepithelial carcinoma", "")]
    labels = {"DOID": "Disease Ontology"}
    for system in ("NCI Thesaurus", "OncoTree", "MONDO", "DOID", "MeSH", "Wikidata"):
        for entry in terminology["systems"].get(system, []):
            if system in ("MeSH", "Wikidata") or names_carcinoma(entry["name"] or ""):
                code_rows.append((labels.get(system, system), entry["code"], entry["name"], entry.get("url") or ""))
    comp["codes_table"] = (
        '<div class="table-wrap"><table class="data-table"><thead><tr><th>System</th><th>Code</th><th>Name used</th></tr></thead>'
        "<tbody>%s</tbody></table></div>" % "".join(
            '<tr><td>%s</td><td class="num">%s</td><td>%s</td></tr>'
            % (esc(system), '<a href="%s" rel="noopener">%s</a>' % (esc(url), esc(code)) if url else esc(code), esc(name[:1].upper() + name[1:]))
            for system, code, name, url in code_rows))
    comp["datasets_table"] = (
        '<div class="table-wrap"><table class="data-table"><thead><tr><th>Accession</th><th>Kind</th><th>Samples</th><th>Study</th></tr></thead>'
        "<tbody>%s</tbody></table></div>" % "".join(
            '<tr><td class="num"><a href="%s" rel="noopener">%s</a></td><td>%s</td><td class="num">%s</td><td>%s</td></tr>'
            % (esc(d["url"]), esc(d["accession"]), esc(d["source"]), num(d["samples"]) if d["samples"] else "", esc(d["title"]))
            for d in datasets if d["names_disease"]))
    projects = collections.OrderedDict()
    for g in grants:
        projects.setdefault(g["core_project_num"], []).append(g)
    grant_rows = []
    for core_num, years in projects.items():
        first = years[0]
        title = first["title"].capitalize() if first["title"].isupper() else first["title"]
        fiscal = sorted(y["fiscal_year"] for y in years if y["fiscal_year"])
        grant_rows.append(
            '<tr><td class="num"><a href="%s" rel="noopener">%s</a></td><td class="num">%s</td><td>%s</td><td>%s</td></tr>'
            % (esc(first["url"]), esc(core_num), "%d to %d" % (fiscal[0], fiscal[-1]) if fiscal else "",
               esc(first["organization"]), esc(title)))
    comp["grants_table"] = (
        '<div class="table-wrap"><table class="data-table"><thead><tr><th>Project</th><th>Years</th><th>Institution</th><th>Title</th></tr></thead>'
        "<tbody>%s</tbody></table></div>" % "".join(grant_rows))
    comp["glossary"] = '<dl class="glossary">%s</dl>' % "".join(
        "<dt>%s</dt><dd>%s</dd>" % (term, text) for term, text in C.GLOSSARY)
    comp["faq"] = "\n".join('<div class="faq-item"><h3>%s</h3><p>%s</p></div>' % (q, a.format(**ctx)) for q, a in C.FAQ)

    comp["compare"] = (
        '<div class="compare" role="table" aria-label="What Peter was told in 2021, against what the research reports">'
        '<div class="compare-row compare-head" role="row"><div role="columnheader"></div>'
        '<div class="compare-col then" role="columnheader">What I was told, or believed, in 2021</div>'
        '<div class="compare-col now" role="columnheader">What the research reports</div></div>%s</div>'
        % "".join('<div class="compare-row" role="row"><div class="compare-topic" role="rowheader">%s</div>'
                  '<div class="compare-cell then" role="cell">%s</div><div class="compare-cell now" role="cell">%s</div></div>'
                  % (topic, then, now.format(**ctx)) for topic, then, now in C.COMPARE))
    comp["first_three"] = '<div class="steps3">%s</div>' % "".join(
        '<div class="step3"><div class="step3-n">%d</div><div class="step3-t">%s</div><p>%s</p></div>' % (i, t, d)
        for i, (t, d) in enumerate(C.FIRST_THREE, 1))
    comp["plan"] = '<ol class="plan">%s</ol>' % "".join(
        '<li><div class="plan-t">%s</div><div class="plan-d">%s</div></li>' % (t, d) for t, d in C.PLAN)
    comp["questions"] = '<ul class="checklist">%s</ul>' % "".join("<li>%s</li>" % q for q in C.QUESTIONS)
    comp["calm"] = '<div class="calm">%s</div>' % "".join(
        '<div class="calm-item"><span class="calm-when">%s</span><span class="calm-arrow" aria-hidden="true">→</span>'
        '<span class="calm-do">%s</span></div>' % (when, do) for when, do in C.CALM)
    comp["hope"] = '<div class="stat-row">%s</div>' % "".join(
        '<div class="stat-card"><span class="stat-num">%s</span><span class="stat-label">%s</span></div>' % (n, t)
        for n, t in C.HOPE)
    comp["spectrum"] = '<div class="spectrum">%s</div>' % '<div class="spectrum-arrow" aria-hidden="true">→</div>'.join(
        '<div class="spec-card %s"><span class="pill">%s</span><div class="spec-name">%s</div><p>%s</p></div>'
        % (cls, status, name, desc) for name, status, cls, desc in C.SPECTRUM)
    comp["fusion_families"] = '<div class="families">%s</div>' % "".join(
        '<div class="family %s"><div class="family-name">%s%s</div><dl>%s</dl>'
        '<div class="chips"><span class="filter-label">Partner genes</span>%s</div></div>'
        % (cls, name, srcs, "".join("<dt>%s</dt><dd>%s</dd>" % fact for fact in facts),
           "".join('<span class="chip">%s</span>' % gene for gene in genes))
        for name, cls, facts, genes, srcs in C.FUSION_FAMILIES)
    comp["survival_people"] = (
        '<div class="people">%s</div><div class="legend"><span><span class="key dot-on"></span>Alive</span>'
        '<span><span class="key dot-off"></span>Died</span></div>'
        % "".join('<figure class="people-fig">%s<figcaption><strong>%d of 100</strong> alive at %s<span>%.1f%%</span></figcaption></figure>'
                  % (people_grid(int(pct + 0.5)), int(pct + 0.5), label, pct) for label, pct in C.SURVIVAL_POINTS))
    series_rows = []
    for name, followed, died, note, src in C.SERIES_DEATHS:
        share = int(100.0 * died / followed + 0.5)
        series_rows.append(
            '<div class="series-row"><div class="series-name">%s%s<small>%d patients followed, %s</small></div>'
            '<div class="series-bar" role="img" aria-label="%d of %d patients had died of the disease">'
            '<div class="series-died" style="flex:%d 1 0">%d%%</div>'
            '<div class="series-alive" style="flex:%d 1 0">%d%% had not</div></div></div>'
            % (name, src, followed, note, died, followed, died, share, followed - died, 100 - share))
    comp["series_deaths"] = (
        '<div class="legend"><span><span class="key" style="background:var(--died)"></span>Died of the disease</span>'
        '<span><span class="key" style="background:var(--accent)"></span>Had not died of the disease</span></div>'
        '<div class="series">%s</div>' % "".join(series_rows))
    directory = sorted({p["id"]: p for p in core + focus}.values(),
                       key=lambda p: (-(p["year"] or 0), (p["title"] or "").lower()))
    ctx["n_dir"] = num(len(directory))
    newest = [p for p in directory if p["named_in_title"]][:5]
    comp["directory_teaser"] = (
        '<div class="coverage"><div class="coverage-head"><div><div class="coverage-tag">Total directory</div>'
        '<div class="coverage-num">%s <span class="denom">papers, %d to %d</span></div></div>'
        '<a class="btn btn-primary" href="papers/">Open the directory</a></div>'
        '<div class="filter-row" style="margin-top:16px"><span class="filter-label">Jump to</span>%s'
        '<a class="filter-btn" href="papers/#focus">Closest to the skin form</a></div></div>'
        '<h3 class="sub-heading">Newest papers</h3>%s'
        % (num(len(directory)), ctx["year_min"], year_max,
           "".join('<a class="filter-btn" href="papers/#%s">%s</a>' % (k, v) for k, v in list(SITE_LABELS.items())[:5]),
           "\n".join('<div class="paper"><div class="paper-title"><a href="%s" rel="noopener">%s</a></div>'
                     '<div class="paper-meta">%s · %s · %s</div></div>'
                     % (esc(paper_url(p)), esc(p["title"]).rstrip("."), esc(short_authors(p, 2)), esc(p["journal"]), p["year"])
                     for p in newest)))

    # ---- assemble the main page in reading order so reference numbers ascend
    hero_sub = refs.cite(C.HERO_SUB.format(**ctx))
    quick = "".join("<dt>%s</dt><dd>%s</dd>" % (k, refs.cite(v.format(**ctx))) for k, v in C.INFOBOX)
    gland_caption = refs.cite(C.INFOBOX_CAPTION)
    tiles = [
        (len(core), "papers naming the disease", True), (len(papers), "works catalogued in all", True),
        (len(have), "held in full text", True), (len(named_trials), "registered trials naming it", True),
        (n_case, "case reports", True), (len(focus), "works on the skin form", True),
        (len(langs), "languages", True), (ctx["year_min"], "earliest indexed paper", False),
    ]
    glance = "".join(
        '<div class="stat"><span class="stat-num"%s>%s</span><span class="stat-label">%s</span></div>'
        % (' data-count="%d"' % v if counted else "", num(v) if counted else v, label)
        for v, label, counted in tiles)
    comp["glance"] = '<div class="stats-grid">%s</div>' % glance
    body_sections = []
    for number, sec in enumerate(C.SECTIONS, 1):
        lead = C.LEADS.get(sec["id"])
        lead_html = '<p class="deck">%s</p>' % lead if lead else ""
        byline = '<p class="byline">%s</p>' % sec["byline"] if sec.get("byline") else ""
        inner = refs.cite(lead_html + byline + sec["html"].format(**dict(ctx, **comp)))
        body_sections.append(
            '<section class="section" id="%s"><h2 class="section-heading"><span class="sec-num">%d</span>%s</h2>%s</section>'
            % (sec["id"], number, sec["title"], inner))
    toc = "".join('<li><a href="#%s">%s</a></li>' % (i, t) for i, t in
                  [(s["id"], s["title"]) for s in C.SECTIONS] + [("references", "References")])
    references = refs.render()
    ctx["n_refs"] = len(refs.order)
    ctx["n_last"] = len(C.SECTIONS) + 1

    description = C.DESCRIPTION.format(**ctx)
    iso = today.isoformat()
    ld = [
        {"@context": "https://schema.org", "@type": "MedicalWebPage", "name": C.TITLE, "url": C.BASE_URL,
         "description": description, "inLanguage": "en", "datePublished": C.FIRST_PUBLISHED, "dateModified": iso,
         "author": {"@type": "Person", "name": C.AUTHOR, "url": C.AUTHOR_URL, "sameAs": C.AUTHOR_PROFILES},
         "publisher": {"@type": "Organization", "name": C.SITE_NAME, "url": C.BASE_URL.split("/" + SLUG)[0] + "/"},
         "audience": {"@type": "MedicalAudience", "audienceType": "Patient"}, "isAccessibleForFree": True,
         "about": {"@type": "MedicalCondition", "@id": C.BASE_URL + "#condition", "name": "Myoepithelial carcinoma",
                   "alternateName": ["Malignant myoepithelioma", "MECA"],
                   "sameAs": ["https://www.wikidata.org/wiki/Q18556495"],
                   "code": [{"@type": "MedicalCode", "codeValue": "8982", "codingSystem": "ICD-O-3"},
                            {"@type": "MedicalCode", "codeValue": "C7596", "codingSystem": "NCI Thesaurus"},
                            {"@type": "MedicalCode", "codeValue": "MONDO:0003158", "codingSystem": "MONDO"}],
                   "associatedAnatomy": [{"@type": "AnatomicalStructure", "name": n}
                                         for n in ("Salivary glands", "Soft tissue", "Skin", "Breast")],
                   "epidemiology": "About 0.013 cases per 100,000 person-years in the U.S. SEER registry, 1973 to 2012.",
                   "possibleTreatment": [{"@type": "MedicalTherapy", "name": "Surgical resection"},
                                         {"@type": "MedicalTherapy", "name": "Radiation therapy"}]},
         "citation": [plain(refs.entry(k, link=False)) for k in refs.order if not isinstance(C.REFS[k], dict)][:40]},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": plain(a.format(**ctx))}} for q, a in C.FAQ]},
        {"@context": "https://schema.org", "@type": "Dataset", "name": "Myoepithelial carcinoma literature catalog",
         "description": "Bibliographic records for %s works on myoepithelial carcinoma and related tumors, merged from "
                        "PubMed, Europe PMC, OpenAlex and Semantic Scholar, with body-site tags and open-access status." % ctx["n_total"],
         "url": C.BASE_URL + "papers/", "creator": {"@type": "Person", "name": C.AUTHOR, "url": C.AUTHOR_URL},
         "dateModified": iso, "keywords": C.KEYWORDS[:8], "isAccessibleForFree": True,
         "license": C.DATA_LICENSE_URL, "sameAs": C.REPO_URL,
         "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": C.BASE_URL + "data/papers.json"},
                          {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": C.BASE_URL + "data/papers.csv"}]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": C.SITE_NAME, "item": C.BASE_URL.split("/" + SLUG)[0] + "/"},
            {"@type": "ListItem", "position": 2, "name": "Myoepithelial carcinoma", "item": C.BASE_URL}]},
    ]

    index = PAGE.format(
        head=head(C.TITLE, description, C.BASE_URL, ld, "", iso),
        nav=nav(""),
        main="""
<div class="hero-band"><div class="page">
<header class="title-block">
  <p class="kicker">A reference to the published research</p>
  <h1>Myoepithelial carcinoma</h1>
  <div class="lead-grid">
    <div class="lead-text">
      <p class="standfirst">{hero_sub}</p>
      <p class="meta-line">Compiled by <a href="#why">Peter Saddington</a>, a patient. Updated {build_date}.
      {n_refs} numbered sources. Not medical advice.</p>
      <p class="meta-line open-note"><strong>Open sources only.</strong> Gathered from free public sources. No paywalled
      article was accessed, so {n_core_closed} of the {n_core} papers are known here by title and abstract alone.
      <a href="#method">How it was built</a>.</p>
      <nav class="site-index" id="in-this-reference" aria-label="In this reference">
        <p><span class="idx-label">By site</span> <a href="skin/">Skin</a> <a href="soft-tissue/">Soft tissue</a>
        <a href="salivary/">Salivary glands</a> <a href="children/">Children</a></p>
        <p><span class="idx-label">For patients</span> <a href="#first-steps">First steps</a>
        <a href="pathology-report/">Reading the pathology report</a> <a href="recurrence/">If it comes back</a>
        <a href="treatments/">Treatments tried</a> <a href="trials/">Trials to ask about</a>
        <a href="summary/">Printable summary</a> <a href="support/">Support</a></p>
        <p><span class="idx-label">For researchers</span> <a href="papers/">{n_dir} papers</a>
        <a href="cases/">{n_cases} published cases</a> <a href="centers/">Centers</a>
        <a href="pathology/">Stains and look-alikes</a> <a href="models/">Cell lines</a>
        <a href="#resources">Codes, data and funding</a> <a href="new/">What's new</a> <a href="feed.xml">Feed</a></p>
      </nav>
    </div>
    <aside class="infobox" id="key-facts" aria-label="Key facts">
      <div class="infobox-title">Myoepithelial carcinoma</div>
      <figure class="infobox-fig">{gland}<figcaption>{gland_caption}</figcaption></figure>
      <dl>{quick}</dl>
    </aside>
  </div>
</header>
</div></div>
<div class="page">
<div class="layout">
  <aside class="sidebar"><nav class="toc" aria-label="Contents"><h2>Contents</h2><ol>{toc}</ol></nav></aside>
  <div class="content">
    <details class="toc toc-details"><summary>Contents</summary><ol>{toc}</ol></details>
    {sections}
    <section class="section" id="references"><h2 class="section-heading"><span class="sec-num">{n_last}</span>References</h2>
    <p>Sources for the numbered markers on this page. All {n_dir} papers are listed in the <a href="papers/">directory</a>.</p>
    {references}</section>
  </div>
</div>
</div>""".format(hero_sub=hero_sub, quick=quick, gland=gland_svg(), gland_caption=gland_caption, toc=toc, sections="\n".join(body_sections),
                 references=references, **ctx),
        footer=footer(ctx), script="static/app.js")

    # ---- directory page
    groups = collections.OrderedDict()
    for p in directory:
        groups.setdefault(p["year"] or 0, []).append(p)
    blocks = []
    for year, items in groups.items():
        rows = []
        for p in items:
            kinds = [k for k, on in (("case", p["is_case_report"]), ("review", p["is_review"]),
                                     ("open", p["is_oa"]), ("focus", p["focus"] == "primary"),
                                     ("animal", p["is_animal"])) if on]
            tags = [SITE_LABELS[s] for s in p["sites"] if s in SITE_LABELS]
            if p["is_case_report"]:
                tags.append("Case report")
            if p["is_animal"]:
                tags.append("Animal study")
            url = paper_url(p)
            title = esc(p["title"]).rstrip(".") or "(untitled)"
            text = " ".join([p["title"] or "", " ".join(p["authors"][:6]), p["journal"] or "", str(year)]).lower()
            rows.append(
                '<div class="paper" data-sites="%s" data-kind="%s" data-text="%s"><div class="paper-title">%s</div>'
                '<div class="paper-meta">%s%s%s</div></div>'
                % (" ".join(p["sites"]), " ".join(kinds), esc(text),
                   '<a href="%s" rel="noopener">%s</a>' % (esc(url), title) if url else title,
                   esc(short_authors(p, 3)), " · " + esc(p["journal"]) if p["journal"] else "",
                   "".join('<span class="tag">%s</span>' % esc(t) for t in tags)))
        blocks.append('<div class="year-group"><h2>%s <small>%d papers</small></h2>%s</div>'
                      % (year or "Year unknown", len(items), "\n".join(rows)))
    site_buttons = '<button class="filter-btn" data-group="site" data-value="all" aria-pressed="true">All sites</button>' + "".join(
        '<button class="filter-btn" data-group="site" data-value="%s" aria-pressed="false">%s</button>' % (k, v)
        for k, v in SITE_LABELS.items())
    kind_buttons = "".join(
        '<button class="filter-btn" data-group="kind" data-value="%s" aria-pressed="%s">%s</button>' % (k, "true" if k == "all" else "false", v)
        for k, v in (("all", "All papers"), ("case", "Case reports"), ("review", "Reviews"),
                     ("open", "Open access"), ("focus", "Closest to the skin form")))
    dir_title = "Myoepithelial Carcinoma Papers: A Directory of %s Publications" % ctx["n_dir"]
    dir_desc = ("Every indexed paper naming myoepithelial carcinoma or malignant myoepithelioma, %d to %d, "
                "with authors, journal and source link. Filter by body site and type." % (ctx["year_min"], year_max))
    dir_ld = [
        {"@context": "https://schema.org", "@type": "CollectionPage", "name": dir_title, "url": C.BASE_URL + "papers/",
         "description": dir_desc, "dateModified": iso, "isPartOf": {"@type": "WebPage", "url": C.BASE_URL},
         "about": {"@id": C.BASE_URL + "#condition"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Myoepithelial carcinoma", "item": C.BASE_URL},
            {"@type": "ListItem", "position": 2, "name": "Papers", "item": C.BASE_URL + "papers/"}]},
    ]
    papers_page = PAGE.format(
        head=head(dir_title, dir_desc, C.BASE_URL + "papers/", dir_ld, "../", iso),
        nav=nav("../"),
        main="""
<div class="hero-band"><div class="page">
<header class="title-block">
  <p class="kicker"><a href="../">Myoepithelial carcinoma</a> / Directory</p>
  <h1>Every paper on myoepithelial carcinoma</h1>
  <p class="standfirst">{n_dir} publications from {year_min} to {year_max}: the {n_core} that name the disease in their
  title or abstract, and the closest work on the skin form. Each links to its source. The list was gathered from
  free public indexes, and no paywalled article was accessed.</p>
</header>
</div></div>
<div class="page">
<div class="directory-main">
  <div class="dir-controls">
    <label for="dir-search" style="position:absolute;left:-9999px">Search papers</label>
    <input id="dir-search" class="dir-search" type="search" placeholder="Search titles, authors, journals, years" autocomplete="off">
    <div class="filter-row"><span class="filter-label">Site</span>{site_buttons}</div>
    <div class="filter-row"><span class="filter-label">Type</span>{kind_buttons}</div>
    <p class="dir-count" id="dir-count" aria-live="polite">{n_dir} papers</p>
  </div>
  <div id="directory-list">{blocks}</div>
  <p class="fineprint" style="margin-top:28px">Site tags and case-report labels are assigned by keyword and can be wrong.
  The full catalog: <a href="../data/papers.json">JSON</a>, <a href="../data/papers.csv">CSV</a>.</p>
</div>
</div>""".format(site_buttons=site_buttons, kind_buttons=kind_buttons, blocks="\n".join(blocks), **ctx),
        footer=footer(ctx), script="../static/app.js")

    # ---- write everything
    if DIST.exists():
        shutil.rmtree(DIST)
    (OUT / "papers").mkdir(parents=True)
    (OUT / "data").mkdir()
    shutil.copytree(HERE / "static", OUT / "static")
    (OUT / "index.html").write_text(index, encoding="utf-8", newline="\n")
    (OUT / "papers" / "index.html").write_text(papers_page, encoding="utf-8", newline="\n")

    fields = ["id", "pmid", "doi", "pmcid", "title", "authors", "journal", "year", "language", "tier",
              "focus", "sites", "is_case_report", "is_review", "is_animal", "is_oa", "cited_by"]
    slim = [{k: p[k] for k in fields} for p in papers]
    (OUT / "data" / "papers.json").write_text(json.dumps(slim, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(fields)
    for p in slim:
        writer.writerow(["; ".join(p[k]) if isinstance(p[k], list) else ("" if p[k] is None else p[k]) for k in fields])
    (OUT / "data" / "papers.csv").write_text(buf.getvalue(), encoding="utf-8", newline="")
    (OUT / "data" / "datasets.json").write_text(
        EMAIL.sub("[address removed]", json.dumps(datasets, ensure_ascii=False, separators=(",", ":"))), encoding="utf-8")
    (OUT / "data" / "terminology.json").write_text(json.dumps(terminology, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "data" / "trials.json").write_text(
        json.dumps([{k: v for k, v in t.items() if k not in ("eligibility", "summary")} for t in trials],
                   ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    import pages
    extra_urls = pages.build_all(sys.modules[__name__], {
        "by_id": by_id, "ctx": ctx, "iso": iso, "core": core, "have": have, "comp": comp, "cases": cases,
        "centers": centers, "models": models, "orgs": orgs, "datasets": datasets,
        "harvest_log": harvest_log, "first_seen": first_seen, "trials": trials, "directory": directory,
        "treatments": treatments, "trials_read": trials_read, "stains": stains, "lookalikes": lookalikes,
        "skin_cases": skin_cases, "verification": verification})
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n"
                                     % (C.BASE_URL.split(SLUG)[0]), encoding="utf-8", newline="\n")
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join("  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (u, iso) for u in [C.BASE_URL, C.BASE_URL + "papers/"] + extra_urls)
        + "</urlset>\n", encoding="utf-8", newline="\n")
    shutil.copyfile(DIST / "sitemap.xml", OUT / "sitemap.xml")
    (DIST / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=%s/"><a href="%s/">Open the page</a>\n'
        % (SLUG, SLUG), encoding="utf-8", newline="\n")
    leaked = sorted({"%s: %s" % (f.relative_to(DIST), m) for f in DIST.rglob("*") if f.is_file() and f.suffix != ".png"
                     for m in EMAIL.findall(f.read_text(encoding="utf-8", errors="ignore"))})
    if leaked:
        raise SystemExit("email address in the built site, remove it at the source:\n  " + "\n  ".join(leaked[:20]))
    print("built %s: %d references, %d papers in directory, %d more pages, index %d KB, directory %d KB"
          % (OUT.relative_to(ROOT), len(refs.order), len(directory), len(extra_urls), len(index) // 1024, len(papers_page) // 1024))
    return ctx


def long_date(iso_date):
    """2026-11-11 -> 11 November 2026."""
    d = datetime.date.fromisoformat(iso_date)
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def head(title, description, url, ld, rel, iso):
    tags = "".join('<meta property="article:tag" content="%s">\n' % esc(k) for k in C.KEYWORDS[:6])
    scripts = "\n".join('<script type="application/ld+json">%s</script>'
                        % json.dumps(block, ensure_ascii=False).replace("</", "<\\/") for block in ld)
    icon = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
            "%3Crect width='64' height='64' fill='%231c1b19'/%3E%3Ctext x='32' y='46' font-size='40' "
            "font-family='Georgia,serif' text-anchor='middle' fill='%23fbfaf6'%3EM%3C/text%3E%3C/svg%3E")
    return """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<meta name="author" content="{author}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<link rel="alternate" type="application/json" title="Myoepithelial carcinoma literature catalog" href="{rel}data/papers.json">
<link rel="alternate" type="application/atom+xml" title="Myoepithelial carcinoma: new papers" href="{rel}feed.xml">
<meta name="theme-color" content="#0e4a5b">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{base}static/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Myoepithelial carcinoma: a reference to the published research">
<meta property="og:site_name" content="{site}">
<meta property="og:locale" content="en_US">
<meta property="article:published_time" content="{published}">
<meta property="article:modified_time" content="{iso}">
<meta property="article:author" content="{author}">
<meta property="article:section" content="Health">
{tags}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="{twitter}">
<meta name="twitter:title" content="{short}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{base}static/og.png">
<link rel="icon" href="{icon}">
<link rel="stylesheet" href="{rel}static/style.css">
{scripts}""".format(title=esc(title), description=esc(description), keywords=esc(", ".join(C.KEYWORDS)),
                    author=esc(C.AUTHOR), url=url, rel=rel, base=C.BASE_URL, site=esc(C.SITE_NAME), iso=iso, published=C.FIRST_PUBLISHED,
                    tags=tags, twitter=C.TWITTER, short=esc(C.SHORT_TITLE), icon=icon, scripts=scripts)


def nav(rel):
    return """<div class="masthead"><div class="page mast">
  <a href="{rel}" class="site-name">Myoepithelial carcinoma</a>
  <nav class="menus" aria-label="Site">
    <details class="menu"><summary>By site</summary><div class="menu-panel">
      <a href="{rel}skin/">Skin</a><a href="{rel}soft-tissue/">Soft tissue</a><a href="{rel}salivary/">Salivary glands</a><a href="{rel}children/">Children</a>
    </div></details>
    <details class="menu"><summary>For patients</summary><div class="menu-panel">
      <a href="{rel}#first-steps">First steps</a><a href="{rel}pathology-report/">Reading the pathology report</a><a href="{rel}recurrence/">If it comes back</a><a href="{rel}treatments/">Treatments tried</a><a href="{rel}trials/">Trials to ask about</a><a href="{rel}summary/">Printable summary</a><a href="{rel}support/">Organizations and support</a>
    </div></details>
    <details class="menu"><summary>For researchers</summary><div class="menu-panel">
      <a href="{rel}#outcomes">Survival and outcomes</a><a href="{rel}papers/">Papers</a><a href="{rel}cases/">Published cases</a><a href="{rel}centers/">Centers and researchers</a><a href="{rel}pathology/">Stains and look-alikes</a><a href="{rel}models/">Cell lines and models</a><a href="{rel}new/">What's new</a>
    </div></details>
  </nav>
  <form class="mast-search" action="{rel}search/" method="get" role="search">
    <label for="mast-q" style="position:absolute;left:-9999px">Search</label>
    <input id="mast-q" name="q" type="search" placeholder="Search">
  </form>
  <span class="mast-langs"><a href="{rel}es/" lang="es">Español</a><a href="{rel}zh/" lang="zh-Hans">中文</a><a href="{rel}ja/" lang="ja">日本語</a></span>
</div></div>""".format(rel=rel or "./")


def footer(ctx):
    return """<footer><div class="page">
  <p>A personal, non-commercial project by <a href="{author_url}">{author}</a>: an attempt to gather every
  verifiable detail about myoepithelial carcinoma into one place.</p>
  <p>Built from open sources only. No paywalled article was accessed.</p>
  <p>Not medical advice. Updated {build_date}. <a href="{contact}">Corrections and additions</a>.</p>
  <p>Data free to reuse under <a href="{license_url}" rel="license">{license_short}</a>. Scripts and catalog:
  <a href="{repo_url}">{repo_label}</a>.</p>
</div></footer>""".format(author=esc(C.AUTHOR), author_url=C.STORY_URL, contact=C.CONTACT_URL, build_date=ctx["build_date"],
                          license_url=C.DATA_LICENSE_URL, license_short=C.DATA_LICENSE_SHORT,
                          repo_url=C.REPO_URL, repo_label=C.REPO_LABEL)


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
{head}
</head>
<body>
{nav}
<main>
{main}
</main>
{footer}
<script src="{script}" defer></script>
</body>
</html>
"""


def serve(port=8000):
    import functools
    import http.server
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    print("serving http://localhost:%d/%s/  (Ctrl+C to stop)" % (port, SLUG), flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
