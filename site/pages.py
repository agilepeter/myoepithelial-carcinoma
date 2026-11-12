"""The pages beyond the main reference and the directory.

build.py calls build_all() with itself (for its helpers) and the data it has
already loaded. Each page gets its own numbered references.
"""

import collections
import csv
import io
import json
import re

import content_pages as P

GROUPS = [("skin", "Skin"), ("soft_tissue", "Soft tissue"), ("salivary", "Salivary glands"), ("breast", "Breast"),
          ("lung", "Lung and airway"), ("bone", "Bone"), ("head_neck_other", "Other head and neck"), ("gyn", "Gynecologic")]


def render(B, S, path, title, description, crumb, h1, standfirst, sections, ld_type="MedicalWebPage", lead=""):
    """Write one page. sections: (id, heading, html). Returns its URL."""
    C = B.C
    refs = B.References(S["by_id"], S["ctx"])
    stand = refs.cite(standfirst)
    lead = refs.cite(lead)
    body, toc = [], []
    for n, (sid, heading, inner) in enumerate(sections, 1):
        body.append('<section class="section" id="%s"><h2 class="section-heading"><span class="sec-num">%d</span>%s</h2>%s</section>'
                    % (sid, n, heading, refs.cite(inner)))
        toc.append('<li><a href="#%s">%s</a></li>' % (sid, heading))
    if refs.order:
        body.append('<section class="section" id="references"><h2 class="section-heading"><span class="sec-num">%d</span>References</h2>%s</section>'
                    % (len(sections) + 1, refs.render().replace('href="#method"', 'href="../#method"')))
        toc.append('<li><a href="#references">References</a></li>')
    S.setdefault("site_map", []).append((path, h1, [(sid, heading) for sid, heading, _ in sections]))
    url = C.BASE_URL + path + "/"
    ld = [
        {"@context": "https://schema.org", "@type": ld_type, "name": title, "url": url, "description": description,
         "inLanguage": "en", "dateModified": S["iso"], "isPartOf": {"@type": "WebPage", "url": C.BASE_URL},
         "about": {"@id": C.BASE_URL + "#condition"}, "author": {"@type": "Person", "name": C.AUTHOR, "url": C.AUTHOR_URL}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Myoepithelial carcinoma", "item": C.BASE_URL},
            {"@type": "ListItem", "position": 2, "name": crumb, "item": url}]},
    ]
    main = """
<div class="hero-band"><div class="page">
<header class="title-block">
  <p class="kicker"><a href="../">Myoepithelial carcinoma</a> / %s</p>
  <h1>%s</h1>
  <p class="standfirst">%s</p>
  <p class="meta-line">Updated %s. Not medical advice.</p>
</header>
</div></div>
<div class="page">
<div class="layout">
  <aside class="sidebar"><nav class="toc" aria-label="On this page"><h2>On this page</h2><ol>%s</ol></nav></aside>
  <div class="content">
    <details class="toc toc-details"><summary>On this page</summary><ol>%s</ol></details>
    %s%s
  </div>
</div>
</div>""" % (crumb, h1, stand, S["ctx"]["build_date"], "".join(toc), "".join(toc), lead, "\n".join(body))
    out = B.OUT / path
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(
        B.PAGE.format(head=B.head(title, description, url, ld, "../", S["iso"]), nav=B.nav("../"), main=main,
                      footer=B.footer(S["ctx"]), script="../static/app.js"), encoding="utf-8", newline="\n")
    return url


def paper_item(B, p):
    url = B.paper_url(p)
    title = B.esc(p["title"]).rstrip(".") or "(untitled)"
    return ('<div class="paper"><div class="paper-title">%s</div><div class="paper-meta">%s · %s · %s</div></div>'
            % ('<a href="%s" rel="noopener">%s</a>' % (B.esc(url), title) if url else title,
               B.esc(B.short_authors(p, 2)), B.esc(p["journal"]), p["year"] or ""))


def stat_row(items):
    return '<div class="stat-row">%s</div>' % "".join(
        '<div class="stat-card"><span class="stat-num">%s</span><span class="stat-label">%s</span></div>' % item for item in items)


def table(headers, rows):
    return ('<div class="table-wrap"><table class="data-table"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % ("".join("<th>%s</th>" % h for h in headers), "".join("<tr>%s</tr>" % "".join(r) for r in rows)))


def describe_case(c):
    if c["age"] is None and not c["sex"]:
        who = "Age and sex not in the abstract"
    else:
        noun = {"F": "girl" if c["child"] else "woman", "M": "boy" if c["child"] else "man"}.get(c["sex"], "patient")
        who = "%d-%s-old %s" % (c["age"], c["age_unit"], noun) if c["age"] is not None else noun.capitalize()
    return who


def site_pages(B, S):
    urls = []
    for path, spec in P.SITE_PAGES.items():
        tag = spec["tag"]
        papers = [p for p in S["core"] if tag in p["sites"] and not p["is_animal"]]
        titled = [p for p in papers if p["named_in_title"]]
        cases = [c for c in S["cases"] if (c["child"] if tag == "pediatric" else c["site_group"] == tag)]
        by_year = collections.Counter(p["year"] for p in papers if p["year"])
        top = sorted(titled, key=lambda p: -(p["cited_by"] or 0))[:8]
        newest = sorted(titled, key=lambda p: (p["year"] or 0, p["date"] or ""), reverse=True)[:8]
        figures = stat_row([
            (B.num(len(papers)), "papers on this form"), (B.num(sum(p["is_case_report"] for p in papers)), "case reports"),
            (B.num(len(cases)), "single-patient reports in the registry"),
            (B.num(sum(1 for p in papers if p["pmcid"] in S["have"])), "held in full text"),
        ])
        sections = list(spec["sections"]) + [
            ("literature", "The literature", """
<p class="chart-note">Papers naming the disease that mention this form in title or abstract, by year. Assigned by keyword[[catalog]].</p>
%s%s
<p><a href="../papers/#%s">Browse all of them in the directory</a>. <a href="../cases/#%s">See the published cases</a>.</p>"""
             % (figures, B.year_chart(by_year, 1985, max(by_year)), tag, tag)),
            ("most-cited", "Most cited papers", "".join(paper_item(B, p) for p in top)),
            ("newest", "Newest papers", "".join(paper_item(B, p) for p in newest)),
        ]
        full = [c for c in S.get("skin_cases") or [] if c.get("is_skin_or_subcutaneous_primary") and c.get("is_myoepithelial_carcinoma")]
        if path == "skin" and full:
            def person(c):
                noun = {"F": "woman", "M": "man"}.get(c.get("sex"), "patient")
                return "%s-%s-old %s" % (c["age"], c.get("age_unit") or "year", noun) if c.get("age") is not None else noun.capitalize()

            def source(c):
                p = S["by_id"].get(c["id"])
                return '<a href="%s" rel="noopener">%s %s</a>' % (B.esc(B.paper_url(p)), B.esc((p["authors"] or ["Source"])[0].split(" ")[0]), p["year"]) if p else ""
            rows = [("<td><strong>%s</strong><br>%s</td>" % (
                        B.esc(person(c)), B.esc(", ".join(str(x) for x in (c.get("primary_site"), c.get("depth"),
                                                "%g cm" % c["size_cm"] if isinstance(c.get("size_cm"), (int, float)) else None) if x))),
                     "<td>%s</td>" % B.esc(", ".join(c.get("treatments") or []) + (" (%s)" % ", ".join(c["drugs"]) if c.get("drugs") else "")),
                     "<td>%s</td>" % B.esc(c.get("summary") or ""),
                     "<td>%s</td>" % B.esc(" ".join(x for x in ("%g months." % c["follow_up_months"] if isinstance(c.get("follow_up_months"), (int, float)) else "",
                                                                (c.get("status_at_last_follow_up") or "").capitalize()) if x)),
                     "<td>%s</td>" % source(c)) for c in sorted(full, key=lambda c: -(S["by_id"].get(c["id"], {}).get("year") or 0))]
            sections.insert(len(spec["sections"]), ("read-in-full", "Skin cases read in full", """
<p>The archive holds the full text of %d papers that each describe a primary myoepithelial carcinoma of the skin or
the fat beneath it. A model read each paper in full and recorded what it says[[catalog]]. This has not been checked
by a clinician. The other published skin cases are indexed from their abstracts in the <a href="../cases/#skin">case
registry</a>.</p>%s""" % (len({c["id"] for c in full}), table(["Patient and tumor", "Treatment", "What happened", "Follow-up", "Source"], rows))))
        urls.append(render(B, S, path, spec["title"], spec["description"], spec["label"], spec["h1"], spec["standfirst"], sections))
    return urls


def outcome_table(B, cases):
    """What the read reports say happened, by site. Counts, not rates."""
    stated = [c for c in cases if c.get("read") and (c.get("patients_in_report") or 1) == 1 and c.get("status")]
    if not stated:
        return ""
    short = [("alive, no evidence of disease", "Alive, no disease"), ("alive with disease", "Alive with disease"),
             ("died of disease", "Died of disease")]
    rows = []
    for key, label in GROUPS + [("", "Other or not stated")]:
        group = [c for c in stated if c["site_group"] == key]
        if not group:
            continue
        months = sorted(c["follow_up_months"] for c in group if c.get("follow_up_months") is not None)
        median = months[len(months) // 2] if months else None
        rows.append(("<td>%s</td>" % label, '<td class="num">%d</td>' % len(group))
                    + tuple('<td class="num">%d</td>' % sum(1 for c in group if c["status"] == s) for s, _ in short)
                    + ('<td class="num">%s</td>' % ("%d months" % median if median is not None else ""),))
    return """<h3 class="sub-heading">What the reports say happened</h3>
<p class="chart-note">Single-patient reports whose abstract states the patient's condition at last follow-up (%d of them).
These are counts of reports. Follow-up is short and good outcomes are reported more readily than bad ones, so they are
not survival rates.</p>%s""" % (len(stated), table(["Site", "Reports", "Alive, no disease", "Alive with disease", "Died of disease",
                                                    "Median follow-up"], rows))


def cases_page(B, S):
    cases = [c for c in S["cases"] if not c.get("not_this_disease")]
    aged = [c for c in cases if c["age_years"] is not None]
    bands = collections.Counter(min(int(c["age_years"] // 10), 8) for c in aged)
    band_rows = [("%d to %d" % (b * 10, b * 10 + 9) if b < 8 else "80 and over", bands.get(b, 0)) for b in range(9)]
    groups = collections.Counter(c["site_group"] for c in cases if c["site_group"])
    sexes = collections.Counter(c["sex"] for c in cases if c["sex"])
    blocks = collections.OrderedDict()
    for c in cases:
        blocks.setdefault(c["year"] or 0, []).append(c)
    out = []
    for year, items in blocks.items():
        rows = []
        for c in items:
            kinds = [k for k, on in (("f", c["sex"] == "F"), ("m", c["sex"] == "M"), ("followup", c["follow_up_months"] is not None),
                                     ("genes", bool(c["genes"])), ("open", c["is_oa"])) if on]
            sites = [c["site_group"]] if c["site_group"] else []
            if c["child"]:
                sites.append("pediatric")
            url = "https://pubmed.ncbi.nlm.nih.gov/%s/" % c["pmid"] if c["pmid"] else ("https://doi.org/%s" % c["doi"] if c["doi"] else "")
            head = " · ".join(x for x in (describe_case(c), c["site"], c["country"]) if x)
            facts = []
            if (c.get("patients_in_report") or 1) > 1:
                facts.append("Report covers %d patients; details are for the first" % c["patients_in_report"])
            if c.get("size_cm"):
                facts.append("Size: %g cm" % c["size_cm"])
            if c["treatments"]:
                facts.append(("Treatment: " if c.get("read") else "Treatment mentioned: ") + ", ".join(c["treatments"]))
            if c.get("drugs"):
                facts.append("Drugs: " + ", ".join(c["drugs"]))
            if c["events"]:
                facts.append(("Reported: " if c.get("read") else "Abstract mentions: ") + ", ".join(c["events"]))
            if c["follow_up_months"] is not None:
                facts.append("Follow-up: %d months" % c["follow_up_months"])
            if c.get("status"):
                facts.append("At last follow-up: " + c["status"])
            if c["genes"]:
                facts.append("Molecular: " + ", ".join(c["genes"]))
            if not c.get("read"):
                facts.append("Title only: no abstract to read")
            title = B.esc(c["title"]).rstrip(".")
            text = " ".join([head, c["title"] or "", c["journal"] or "", str(year), " ".join(c["genes"])]).lower()
            rows.append(
                '<div class="paper" data-sites="%s" data-kind="%s" data-text="%s"><div class="case-head">%s</div>'
                '<div class="paper-title">%s</div><div class="paper-meta">%s%s</div></div>'
                % (" ".join(sites), " ".join(kinds), B.esc(text), B.esc(head),
                   '<a href="%s" rel="noopener">%s</a>' % (B.esc(url), title) if url else title,
                   B.esc(c["journal"]), "".join('<span class="tag">%s</span>' % B.esc(f) for f in facts)))
        out.append('<div class="year-group"><h2>%s <small>%d reports</small></h2>%s</div>' % (year or "Year unknown", len(items), "\n".join(rows)))
    site_buttons = '<button class="filter-btn" data-group="site" data-value="all" aria-pressed="true">All sites</button>' + "".join(
        '<button class="filter-btn" data-group="site" data-value="%s" aria-pressed="false">%s</button>' % (k, v)
        for k, v in GROUPS + [("pediatric", "Children")])
    kind_buttons = "".join(
        '<button class="filter-btn" data-group="kind" data-value="%s" aria-pressed="%s">%s</button>' % (k, "true" if k == "all" else "false", v)
        for k, v in (("all", "All reports"), ("f", "Women and girls"), ("m", "Men and boys"), ("followup", "Follow-up stated"),
                     ("genes", "Genes named"), ("open", "Open access")))
    fields = ["id", "pmid", "doi", "year", "country", "age", "age_unit", "sex", "site", "site_group", "treatments",
              "events", "follow_up_months", "genes", "title", "journal"]
    slim = [{k: c[k] for k in fields} for c in cases]
    (B.OUT / "data" / "cases.json").write_text(json.dumps(slim, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(fields)
    for c in slim:
        writer.writerow(["; ".join(c[k]) if isinstance(c[k], list) else ("" if c[k] is None else c[k]) for k in fields])
    (B.OUT / "data" / "cases.csv").write_text(buf.getvalue(), encoding="utf-8", newline="")
    n = len(cases)
    sections = [
        ("about", "What this is", """
<p>One entry for each published report of a single patient: {n} in all, from {y0} to {y1}, drawn from the
catalog behind this site[[catalog]]. Each links to the paper. A 2019 analysis pooled 691 patients from 340
publications to study survival[[giridhar2019]]. This list is for looking up individual reports.</p>
<div class="callout"><strong>Read this first.</strong> Each entry was extracted from the paper's abstract by a model
instructed to record only what the abstract states. It has not been checked by a person, and an abstract leaves out
much of what the full paper says. Entries marked "title only" had no abstract to read. Reports that turned out to
describe a different diagnosis are left out. Follow the link before relying on any entry.</div>
{figures}""".format(n=B.num(n), y0=min(c["year"] for c in cases if c["year"]), y1=max(c["year"] for c in cases if c["year"]),
                    figures=stat_row([(B.num(n), "single-patient reports"), (B.num(len(aged)), "with an age in the abstract"),
                                      ("%d : %d" % (sexes.get("F", 0), sexes.get("M", 0)), "women to men, where stated"),
                                      (B.num(sum(c["child"] for c in cases)), "under 18")]))),
        ("patterns", "Patterns", """
<p>Published cases are not a sample of patients. Unusual cases get written up and ordinary ones do not, so read
these as a description of the literature.</p>
<h3 class="sub-heading">Age at diagnosis</h3>%s
<h3 class="sub-heading">Where the tumor was</h3>%s%s"""
         % (B.bars(band_rows, label="Reports by age band"),
            B.bars([(label, groups.get(key, 0)) for key, label in GROUPS], label="Reports by site"), outcome_table(B, cases))),
        ("registry", "The reports", """
<div class="dir-controls">
  <label for="dir-search" style="position:absolute;left:-9999px">Search reports</label>
  <input id="dir-search" class="dir-search" type="search" placeholder="Search site, country, gene, title, year" autocomplete="off">
  <div class="filter-row"><span class="filter-label">Site</span>%s</div>
  <div class="filter-row"><span class="filter-label">Show</span>%s</div>
  <p class="dir-count" id="dir-count" aria-live="polite">%s reports</p>
</div>
<div id="directory-list" data-noun="reports">%s</div>
<p class="fineprint" style="margin-top:24px">Download: <a href="../data/cases.json">cases.json</a>, <a href="../data/cases.csv">cases.csv</a>.</p>"""
         % (site_buttons, kind_buttons, B.num(n), "\n".join(out))),
    ]
    return render(B, S, "cases", "Myoepithelial Carcinoma Case Registry: %s Published Patient Reports" % B.num(n),
                  "An index of every published single-patient report of myoepithelial carcinoma: age, sex, site, country, "
                  "treatment and follow-up as stated in each abstract, with a link to the paper.",
                  "Cases", "Published cases", "Every single-patient report in the literature, one line each.", sections,
                  ld_type="CollectionPage")


def centers_page(B, S):
    data = S["centers"]
    inst = [i for i in data["institutions"] if i["papers"] >= 3]
    rows = [("<td class=\"num\">%d</td>" % (n + 1), "<td>%s</td>" % B.esc(i["name"]), "<td>%s</td>" % B.esc(i["country"]),
             '<td class="num">%d</td>' % i["papers"], '<td class="num">%d</td>' % i["since_2015"], '<td class="num">%s</td>' % (i["skin_papers"] or ""),
             "<td>%s</td>" % B.esc(", ".join(B.SITE_LABELS.get(s, s) for s in i["top_sites"][:2])))
            for n, i in enumerate(inst[:80])]
    skin = sorted([i for i in data["institutions"] if i["skin_papers"] >= 2], key=lambda i: -i["skin_papers"])[:20]
    sections = [
        ("about", "How to read this", """
<p>These are the institutions whose staff have written the papers naming the disease, counted from author
affiliations on {covered} of {total} papers[[catalog]]. A paper counts once for each institution on it.</p>
<div class="callout"><strong>This is not a list of recommended hospitals.</strong> Publishing on a disease shows that
someone there has seen it and studied it, often a pathologist. It does not show how many patients are treated there
now, or how well. Use it to find people worth asking, and ask them how many cases they have managed.</div>""".format(
            covered=B.num(data["papers_with_institutions"]), total=B.num(data["core_papers"]))),
        ("countries", "By country", B.bars([(c["country"], c["papers"]) for c in data["countries"][:18]], label="Papers by country")),
        ("institutions", "Institutions",
         '<p class="chart-note">Institutions with three or more papers. University and hospital names are as recorded by OpenAlex, '
         "so one center can appear under two names.</p>"
         + table(["", "Institution", "Country", "Papers", "Since 2015", "Skin form", "Mostly on"], rows)),
        ("skin", "Institutions that have published on the skin form",
         table(["Institution", "Country", "Skin papers", "All papers"],
               [("<td>%s</td>" % B.esc(i["name"]), "<td>%s</td>" % B.esc(i["country"]), '<td class="num">%d</td>' % i["skin_papers"],
                 '<td class="num">%d</td>' % i["papers"]) for i in skin])),
        ("authors", "Authors", "<p>The names that appear most often on PubMed-indexed papers. Counts are by name as printed[[catalog]].</p>"
         + S["comp"]["bars_authors"]),
    ]
    return render(B, S, "centers", "Myoepithelial Carcinoma: Centers and Researchers Who Have Published on It",
                  "Hospitals, universities and authors ranked by how many papers they have published on myoepithelial "
                  "carcinoma, by country, with a separate list for the skin form.",
                  "Centers", "Centers and researchers", "Who has studied this disease, and where.", sections, ld_type="CollectionPage")


def report_page(B, S):
    def mark(n):
        return '<span class="mk">%d</span>' % n
    lines = []
    for kind, text, marks in P.REPORT_LINES:
        text = re.sub(r"\{(\d)\}", lambda m: mark(int(m.group(1))), text)
        lines.append('<div class="rp-%s">%s%s</div>' % (kind, text, "".join(mark(n) for n in marks)))
    notes = "".join('<li><div><strong>%s.</strong> %s</div></li>' % (t, d) for t, d in P.REPORT_NOTES)
    also = '<dl class="glossary">%s</dl>' % "".join("<dt>%s</dt><dd>%s</dd>" % row for row in P.REPORT_ALSO)
    sections = [
        ("example", "An example, line by line", """
<p>This is the text of a real second-opinion report, published by the patient it belongs to[[post]]. The numbers
match the notes underneath.</p>
<div class="report-paper" aria-label="Text of a pathology report">%s</div>
<ol class="report-notes">%s</ol>""" % ("".join(lines), notes)),
        ("also", "What else a report may give", "<p>Not every report has these. Each one bears on outlook, so ask if it is missing.</p>" + also),
        ("ask", "What to ask for", """
<ul class="plain-list">
<li>A copy of every report, including addenda that arrive later.</li>
<li>A second opinion on the slides from a center that sees these tumors.</li>
<li>Whether fusion testing has been done, and if not, whether it can be.</li>
<li>Where the slides and tissue blocks are stored, in case another center needs them.</li>
</ul>
<p>The <a href="../#first-steps">first-steps guide</a> puts these in order. The <a href="../#glossary">glossary</a> explains the terms.</p>"""),
    ]
    return render(B, S, "pathology-report", "How to Read a Myoepithelial Carcinoma Pathology Report",
                  "A real pathology report for myoepithelial carcinoma explained line by line: the diagnosis wording, "
                  "the stains, the margin, and what else to look for.",
                  "Reading a report", "How to read the pathology report", "The report decides everything that follows. This is how to read one.", sections)


def support_page(B, S):
    orgs = [o for o in S["orgs"] if o["ok"]]
    groups = collections.OrderedDict()
    for o in orgs:
        groups.setdefault(o["group"], []).append(o)
    sections = []
    for name, items in groups.items():
        sections.append((re.sub(r"[^a-z]+", "-", name.lower()).strip("-"), name, '<dl class="glossary">%s</dl>' % "".join(
            '<dt><a href="%s" rel="noopener">%s</a></dt><dd>%s</dd>' % (B.esc(o["url"]), B.esc(o["name"]), B.esc(o["what"])) for o in items)))
    sections.append(("note", "About this list", """
<p>Each address was checked on %s and answered. Being listed is not an endorsement, and none of these organizations
has reviewed this page. Know one that belongs here? <a href="%s">Send it</a>.</p>""" % (orgs[0]["checked"] if orgs else "", B.C.CONTACT_URL)))
    return render(B, S, "support", "Myoepithelial Carcinoma Support: Patient Organizations and Help",
                  "Organizations for people with myoepithelial carcinoma and other rare cancers: the patient research "
                  "project, rare cancer and sarcoma charities, practical help and crisis lines.",
                  "Support", "Organizations and support", "Where to find other patients, practical help and someone to talk to.", sections)


def models_page(B, S):
    models = S["models"]
    rows = [('<td><a href="%s" rel="noopener">%s</a></td>' % (B.esc(m["url"]), B.esc(m["name"])), '<td class="num">%s</td>' % B.esc(m["accession"]),
             "<td>%s</td>" % B.esc("; ".join(m["diseases"][:1])), "<td>%s</td>" % B.esc(m["category"]),
             "<td>%s</td>" % ("A different diagnosis" if m["epithelial_myoepithelial"] else "Malignant" if m["names_carcinoma"] else "Benign"))
            for m in models]
    datasets = [d for d in S["datasets"] if re.search(r"organoid|xenograft|cell line", d["title"] + d["summary"], re.I)]
    sections = [
        ("lines", "Cell lines", """
<p>Cellosaurus, the reference catalog of cell lines, lists %d lines derived from myoepithelial tumors. %d of them
come from a malignant myoepithelial tumor[[cellosaurus]].</p>%s"""
         % (len(models), sum(1 for m in models if m["names_carcinoma"] and not m["epithelial_myoepithelial"]),
            table(["Line", "Accession", "Derived from", "Kind", "Note"], rows))),
        ("models", "Organoids, xenografts and other models", """
<p>cureMEC reports building the first preclinical models of the disease, including for the EWSR1 fusion-positive
form[[curemec2026]][[curemec2026b]].</p>%s""" % (table(["Accession", "Study"], [
            ('<td class="num"><a href="%s" rel="noopener">%s</a></td>' % (B.esc(d["url"]), B.esc(d["accession"])), "<td>%s</td>" % B.esc(d["title"]))
            for d in datasets]) if datasets else "")),
        ("data", "Datasets and codes", """
<p>Sequencing and expression datasets, standard codes and federal funding are listed in the
<a href="../#resources">researcher section</a> of the main page. Exome and RNA sequencing from 27 patients is in the
EGA archive[[kashyap2026]], and the raw reads behind the 2017 genomic study are in BioProject PRJNA390610[[dalin2017]].</p>"""),
        ("gap", "The gap", """
<p>A disease with one malignant cell line in the reference catalog cannot be studied the way common cancers are.
Tissue from patients is how that changes. Patients can ask their surgeon whether tissue can be banked for
research, and cureMEC is building biospecimen collections[[curemec2026]].</p>"""),
    ]
    return render(B, S, "models", "Myoepithelial Carcinoma Cell Lines and Research Models",
                  "Cell lines, organoids, xenografts and datasets available for myoepithelial carcinoma research, "
                  "with accession numbers.",
                  "Models", "Cell lines and research models", "What a laboratory can work with today. It is a short list.", sections)


def summary_page(B, S):
    facts = '<dl class="glossary">%s</dl>' % "".join("<dt>%s</dt><dd>%s</dd>" % row for row in P.SUMMARY_FACTS)
    form = '<div class="form-lines">%s</div>' % "".join('<div class="form-line"><span>%s</span></div>' % f for f in P.SUMMARY_FORM)
    sections = [
        ("disease", "The disease, in one page", '<p class="chart-note">For a clinician who has not seen it before. Figures are from the '
         "sources numbered below.</p>" + facts),
        ("patient", "This patient", '<p class="chart-note">Fill in before the appointment. Bring the reports themselves as well.</p>' + form),
    ]
    lead = ('<div class="hero-actions"><button class="btn btn-primary" onclick="window.print()">Print or save as PDF</button>'
            '<a class="btn" href="../#first-steps">Back to the first-steps guide</a></div>')
    return render(B, S, "summary", "Myoepithelial Carcinoma: Printable Summary for a New Doctor",
                  "A two-page printable summary of myoepithelial carcinoma for a clinician who has not seen it, "
                  "with a form for the patient's own details.",
                  "Printable summary", "A summary to hand to a new doctor",
                  "Most doctors will not have seen this disease. One page on the disease, one page on you.", sections, lead=lead)


def new_page(B, S):
    log = S["harvest_log"]
    latest = log[-1]
    first_seen = S["first_seen"]
    core_titled = [p for p in S["core"] if p["named_in_title"] and not p["is_animal"]]
    recent = sorted([p for p in core_titled if (p["year"] or 0) >= S["ctx"]["year_max"] - 1],
                    key=lambda p: (p["year"] or 0, p["date"] or ""), reverse=True)
    added = [] if latest.get("baseline") else [p for p in S["core"] if first_seen.get(p["id"]) == latest["date"]]
    rows = [("<td class=\"num\">%s</td>" % e["date"], '<td class="num">%s</td>' % B.num(e["total"]), '<td class="num">%s</td>' % B.num(e["core"]),
             "<td>%s</td>" % ("First harvest" if e.get("baseline") else "%s added, %s naming the disease" % (B.num(e["added"]), B.num(e["added_core"]))))
            for e in reversed(log)]
    sections = [
        ("harvests", "Harvests", "<p>Each time the indexes are searched again, the totals are recorded here.</p>"
         + table(["Date", "Works", "Naming the disease", "Change"], rows)),
        ("added", "Added in the latest harvest",
         "".join(paper_item(B, p) for p in added[:150]) if added else
         "<p>The first harvest was on %s. Papers found after that date will be listed here.</p>" % latest["date"]),
        ("recent", "Published in %d and %d" % (S["ctx"]["year_max"] - 1, S["ctx"]["year_max"]),
         '<p class="chart-note">%d papers with the disease in the title, newest first.</p>' % len(recent)
         + "".join(paper_item(B, p) for p in recent[:120])),
    ]
    return render(B, S, "new", "What's New in Myoepithelial Carcinoma Research",
                  "The newest published papers on myoepithelial carcinoma and what each harvest of the research "
                  "indexes has added.",
                  "What's new", "What's new", "New papers, and what each search of the indexes added.", sections, ld_type="CollectionPage")


NUMBER_WORDS = ["None", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven",
                "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty"]


def site_facts(B, S):
    """The values the About and Changes pages fill in. The counts come from the source check itself."""
    C, checks = B.C, S["verification"]
    wrong = sum(1 for v in checks if v["verdict"] in ("contradicted", "not found in the source text available"))
    facts = dict(S["ctx"])
    facts.update({
        "author": B.esc(C.AUTHOR), "story_url": C.STORY_URL, "about_url": C.ABOUT_URL, "changes_url": C.CHANGES_URL,
        "contact_email": C.CONTACT_EMAIL, "contact_subject": C.CONTACT_SUBJECT, "contact_spoken": C.CONTACT_SPOKEN,
        "n_checked": len(checks), "n_wrong_word": NUMBER_WORDS[wrong] if wrong < len(NUMBER_WORDS) else str(wrong),
        "n_full": sum(1 for v in checks if v["checked_against"] != "abstract only"),
        "n_abstract": sum(1 for v in checks if v["checked_against"] == "abstract only"),
    })
    return facts


def about_page(B, S):
    facts = site_facts(B, S)
    sections = [(sid, heading, html.format(**facts)) for sid, heading, html in P.ABOUT]
    return render(B, S, "about", "About the Myoepithelial Carcinoma Reference: Who, How, Corrections",
                  "Who compiles this reference on myoepithelial carcinoma and how: sources, the use of AI, review "
                  "status, independence, corrections, privacy and contact.",
                  "About", "About this reference",
                  "Who compiles it, how it is made, how far it has been checked, and how to reach the person behind it.",
                  sections, ld_type="AboutPage")


def changes_page(B, S):
    facts = site_facts(B, S)
    sections = []
    for iso_date, items in P.CHANGES:
        sections.append(("d" + iso_date, B.long_date(iso_date), '<ul class="plain-list">%s</ul>' % "".join(
            "<li>%s</li>" % item.format(**facts) for item in items)))
    return render(B, S, "changes", "Myoepithelial Carcinoma Reference: Corrections and Changes",
                  "A dated record of every correction and change of substance made to this reference on "
                  "myoepithelial carcinoma, with what was wrong and what replaced it.",
                  "Changes", "Corrections and changes",
                  "What has been corrected or changed, and when. Newest first.", sections, ld_type="WebPage")


def build_all(B, S):
    urls = site_pages(B, S)
    for page in (cases_page, centers_page, report_page, support_page, models_page, summary_page, new_page,
                 about_page, changes_page):
        urls.append(page(B, S))
    import pages_more
    return urls + pages_more.build_more(B, S)
