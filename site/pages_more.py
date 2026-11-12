"""Pages built from the read-and-extracted data, plus search, the feed and translations.

Each page is skipped if its data file is not there yet, so the site still
builds while extraction is in progress.
"""

import collections
import html
import json
import re

import pages as PG

RESPONSE_ORDER = ["complete response", "partial response", "stable disease", "no recurrence after adjuvant treatment",
                  "mixed across patients", "progression", "not stated"]
ACCEPT_ORDER = [
    ("names myoepithelial carcinoma", "Trials that name the disease"),
    ("any advanced solid tumor or rare tumor", "Open to any advanced or rare solid tumor"),
    ("salivary gland cancers including other histologies", "Salivary gland cancers, including the rarer types"),
    ("salivary gland cancers, histology limits unclear", "Salivary gland cancers, where the record does not say which types"),
    ("soft tissue sarcoma broadly", "Soft-tissue sarcoma, broadly"),
    ("requires a specific biomarker", "Open only to tumors with a named marker"),
]
LANGS = [("es", "Español", "es"), ("zh", "中文", "zh-Hans"), ("ja", "日本語", "ja")]


def source_link(B, S, ident):
    p = S["by_id"].get(ident)
    if p:
        url = B.paper_url(p)
        label = "%s %s" % ((p["authors"] or ["Source"])[0].split(" ")[0], p["year"] or "")
        return '<a href="%s" rel="noopener">%s</a>' % (B.esc(url), B.esc(label.strip())) if url else B.esc(label)
    if str(ident).startswith("NCT"):
        return '<a href="https://clinicaltrials.gov/study/%s" rel="noopener">%s</a>' % (ident, ident)
    return B.esc(str(ident))


def treatments_page(B, S):
    rows = [r for r in S.get("treatments") or [] if r.get("regimen") and r.get("is_myoepithelial_carcinoma")]
    if not rows:
        return None
    rows.sort(key=lambda r: (RESPONSE_ORDER.index(r["response"]) if r.get("response") in RESPONSE_ORDER else 9, -(int(r.get("year") or 0))))
    by_class = collections.OrderedDict()
    for label in ("chemotherapy", "targeted therapy", "immunotherapy", "combination of classes", "hormonal"):
        chosen = [r for r in rows if r.get("drug_class") == label]
        if chosen:
            by_class[label] = chosen
    other = [r for r in rows if r.get("drug_class") not in by_class]
    if other:
        by_class["other or unclassified"] = other
    responded = [r for r in rows if r.get("response") in ("complete response", "partial response")]
    sections = [("about", "What this is", """
<p>Every drug treatment for myoepithelial carcinoma that a paper abstract or trial record in the catalog describes
being given to a patient, with what the abstract says happened[[catalog]]. %s reports, %s of them with a complete
or partial response.</p>
<div class="callout"><strong>Read this first.</strong> These are single patients and small groups, read from abstracts
by a model and not yet checked by a clinician. A response in one patient does not show that a drug works, and
reports of failure are published less often than reports of success. There is no established standard drug
treatment for this disease[[curemec2026]]. Take the table to your oncologist; do not act on it alone.</div>%s"""
                 % (B.num(len(rows)), B.num(len(responded)),
                    PG.stat_row([(B.num(len(rows)), "treatment reports"), (B.num(len({r["id"] for r in rows})), "papers and trials"),
                                 (B.num(len(responded)), "complete or partial responses reported"),
                                 (B.num(sum(1 for r in rows if r.get("population") == "child")), "in children")])))]
    for label, chosen in by_class.items():
        def sentence(text):
            text = (text or "").strip()
            return text[:1].upper() + text[1:] + ("" if text.endswith(".") else ".") if text else ""
        body = PG.table(["Regimen", "Tumor and setting", "Response reported", "What the abstract says"], [
            ("<td><strong>%s</strong>%s</td>" % (B.esc(r["regimen"]), '<br><span class="paper-meta">%s patient%s</span>'
                                                 % (r["n_patients"], "" if r["n_patients"] == 1 else "s") if r.get("n_patients") else ""),
             "<td>%s</td>" % B.esc(sentence("; ".join(x for x in (r.get("site"), r.get("setting"), r.get("population") if r.get("population") == "child" else None) if x)).rstrip(".")),
             "<td>%s</td>" % B.esc((r.get("response") or "not stated").capitalize()),
             "<td>%s %s</td>" % (B.esc(" ".join(sentence(x) for x in (r.get("duration"), r.get("note")) if x)), source_link(B, S, r["id"])))
            for r in chosen])
        sections.append((re.sub(r"[^a-z]+", "-", label).strip("-"), label.capitalize(), body))
    sections.append(("trials", "Drugs being tested now", '<p>Open trials a patient could ask about are on the <a href="../trials/">trials page</a>.</p>'))
    return PG.render(B, S, "treatments", "Myoepithelial Carcinoma Drug Treatments: Every Regimen Reported",
                     "Every chemotherapy, targeted therapy and immunotherapy reported for myoepithelial carcinoma in the "
                     "published literature, with the response each report describes.",
                     "Treatments tried", "Every drug treatment reported",
                     "What has been tried, in whom, and what the reports say happened.", sections)


def trials_page(B, S):
    read = {r.get("nct_id"): r for r in S.get("trials_read") or []}
    if not read:
        return None
    trials = {t["nct_id"]: t for t in S["trials"]}
    sections = [("about", "How to use this", """
<p>These are open treatment trials from ClinicalTrials.gov whose records suggest a patient with myoepithelial
carcinoma might be eligible[[ctgov]]. %d open trials were read. The ones limited to other tumor types are left out.</p>
<div class="callout"><strong>This is a list of questions, not of places.</strong> Eligibility was judged by a model from
the first part of each record's criteria and has not been checked by a clinician or with the trial. Only the trial
team can say whether a particular patient qualifies. Status changes: check the registry link.</div>""" % len(read))]
    shown = 0
    for key, heading in ACCEPT_ORDER:
        chosen = [r for r in read.values() if r.get("accepts") == key and r.get("nct_id") in trials]
        if not chosen:
            continue
        chosen.sort(key=lambda r: (trials[r["nct_id"]]["status"] != "RECRUITING", r["nct_id"]))
        shown += len(chosen)
        body = PG.table(["Registry ID", "Trial", "Phase", "Status", "Where", "Treatment", "Why it is listed"], [
            ('<td class="num"><a href="%s" rel="noopener">%s</a></td>' % (B.esc(trials[r["nct_id"]]["url"]), r["nct_id"]),
             "<td>%s</td>" % B.esc(trials[r["nct_id"]]["title"]),
             "<td>%s</td>" % B.esc(", ".join(x.replace("PHASE", "Phase ") for x in trials[r["nct_id"]]["phases"]) or ""),
             '<td><span class="pill%s">%s</span></td>' % (" live" if trials[r["nct_id"]]["status"] == "RECRUITING" else "",
                                                           B.esc(trials[r["nct_id"]]["status"].replace("_", " ").capitalize())),
             "<td>%s</td>" % B.esc(", ".join(trials[r["nct_id"]]["countries"][:4]) + (" and others" if len(trials[r["nct_id"]]["countries"]) > 4 else "")),
             "<td>%s</td>" % B.esc(r.get("treatment") or ""),
             "<td>%s%s</td>" % (B.esc(r.get("basis") or ""), " Needs: %s." % B.esc(r["biomarker_required"]) if r.get("biomarker_required") else ""))
            for r in chosen])
        sections.append((re.sub(r"[^a-z]+", "-", key).strip("-"), heading, body))
    sections.append(("ask", "What to ask", """
<ul class="plain-list">
<li>Does this trial accept myoepithelial carcinoma, and has it enrolled anyone with it?</li>
<li>Does my tumor need a particular marker or fusion to qualify, and has mine been tested?</li>
<li>Which sites are open, and what would taking part involve?</li>
</ul>
<p>What has already been tried is on the <a href="../treatments/">treatments page</a>.</p>"""))
    return PG.render(B, S, "trials", "Myoepithelial Carcinoma Clinical Trials: Open Trials to Ask About",
                     "Open clinical trials that a patient with myoepithelial carcinoma could ask about: trials naming the "
                     "disease, rare-tumor and salivary gland trials, and marker-based trials.",
                     "Trials", "Trials to ask about", "%d open trials whose records leave room for this diagnosis." % shown, sections)


def recurrence_page(B, S):
    cases = [c for c in S["cases"] if c.get("read") and not c.get("not_this_disease")]
    recurred = [c for c in cases if c.get("recurrence") == "yes"]
    spread = [c for c in cases if c.get("metastasis") == "yes"]
    sites = collections.Counter()
    for c in spread:
        for s in set(re.sub(r"s$", "", x.lower().strip()) for x in c.get("metastasis_sites") or []):
            sites[{"lymph node": "lymph nodes", "lung": "lung", "bone": "bone", "liver": "liver", "brain": "brain"}.get(s, s)] += 1
    advanced = [r for r in S.get("treatments") or [] if r.get("regimen") and r.get("is_myoepithelial_carcinoma")
                and r.get("setting") == "recurrent or metastatic"]
    sections = [
        ("how-often", "How often it comes back", """
<p>Often. In a 101-tumor soft-tissue series, 42% of malignant tumors recurred locally and 32% metastasized[[hornick2003]].
A review puts recurrence and metastasis at up to 40 to 50%[[jo2015]], and in one sarcoma unit 13 of 24 patients relapsed[[chamberlain2020]]. In salivary tumors, 27% of the patients
with follow-up in one series developed distant metastases[[kong2015]], and in another, ten of 25 patients had recurrences, mostly more than one[[savera2000]]. In
children, nine of 17 whose tumors were completely removed with clear margins still had a local recurrence[[gleason2007]].</p>
<p>So a recurrence is the expected course for many patients, and does not by itself mean that treatment failed or
that nothing more can be done.</p>"""),
        ("when", "When", """
<p>It can be early or very late. Follow-up in the soft-tissue series ran from 4 to 252 months[[hornick2003]]. In
children the deaths came at a median of nine months[[gleason2007]], while in the pooled literature median
progression-free survival was 48 months[[giridhar2019]]. This is the reason for a long surveillance schedule.</p>"""),
        ("where", "Where it spreads", """
<p>The lung is the most common distant site: 83%% of distant metastases in one salivary series[[kong2015]]. Of patients
with major salivary gland tumors and a recorded stage, 14.5%% had lymph-node involvement and 6.6%% had distant
spread at diagnosis[[luo2022]].</p>%s""" % (
            '<p class="chart-note">Sites of spread named in %d single-patient reports that describe metastasis, from the '
            '<a href="../cases/">case registry</a>. A report can name several.</p>%s'
            % (len(spread), B.bars(sites.most_common(8), label="Sites of metastasis in case reports")) if sites else "")),
        ("what-was-done", "What was done", """
<ul class="plain-list">
<li><strong>More surgery.</strong> Complete removal with clear margins is the factor most tied to survival in the pooled
data[[giridhar2019]], and re-excision is the usual first answer to a local recurrence that can be removed.</li>
<li><strong>Radiotherapy.</strong> After surgery it reduced local and regional recurrence in the pooled analysis[[giridhar2019]].</li>
<li><strong>Implanted radiation.</strong> In 27 patients with tumors of the mouth and face treated with radioactive iodine
seeds, 14 of them after a recurrence that could not be operated on, recurrence-free survival was 51.9%% at three years
and overall survival 68.6%%. Patients treated at first diagnosis did better than those treated at relapse[[zheng2016]].</li>
<li><strong>Mohs surgery</strong> has been reported for a recurrent myoepithelioma of the skin[[miller2009]].</li>
<li><strong>Drugs.</strong> %s</li>
<li><strong>Trials.</strong> The authors of the adult soft-tissue series encourage enrollment[[chamberlain2020]]. See
<a href="../trials/">trials to ask about</a>.</li>
</ul>""" % ("The catalog holds %d reports of drug treatment for recurrent or metastatic disease. They are set out on the "
            '<a href="../treatments/">treatments page</a>.' % len(advanced) if advanced else
            'Evidence is limited[[chamberlain2020]]. See the <a href="../treatments/">treatments page</a>.')),
        ("reports", "In the published cases", """
<p>Of %s single-patient reports read for the registry, %s describe a local recurrence and %s describe metastasis.
Reports are not a sample of patients, so these are not rates. <a href="../cases/">Browse the reports</a>.</p>"""
         % (B.num(len(cases)), B.num(len(recurred)), B.num(len(spread)))),
        ("ask", "What to ask", """
<ul class="plain-list">
<li>Is this a recurrence where the first tumor was, a new tumor, or spread? How do we know?</li>
<li>Can it be removed with a clear margin?</li>
<li>Should the new tissue be tested for fusions, if the first was not?</li>
<li>Is radiotherapy an option here, including implanted radiation?</li>
<li>Is there a trial open to me now?</li>
<li>What will the surveillance schedule be after this?</li>
</ul>"""),
    ]
    return PG.render(B, S, "recurrence", "When Myoepithelial Carcinoma Comes Back: Recurrence and Spread",
                     "How often myoepithelial carcinoma recurs or spreads, when, where to, and what the published reports "
                     "describe being done about it.",
                     "If it comes back", "If it comes back", "Recurrence is common in this disease. This is what the literature says about it.",
                     sections)


def pathology_page(B, S):
    stains = [s for s in S.get("stains") or [] if s.get("marker")]
    looks = [x for x in S.get("lookalikes") or [] if x.get("lookalike")]
    if not stains and not looks:
        return None
    sections = [("about", "For pathologists", """
<p>Two tables built from the abstracts of the published series: how often each immunostain is positive, and which
tumors the disease is confused with[[catalog]]. They were extracted by a model and have not been checked by a
pathologist. Each row links to its sources.</p>""")]
    pooled = collections.OrderedDict()
    for s in stains:
        if s.get("tumor_group") != "myoepithelial carcinoma":
            continue
        if isinstance(s.get("positive_n"), int) and isinstance(s.get("tested_n"), int) and s["tested_n"]:
            pct, n = 100.0 * s["positive_n"] / s["tested_n"], s["tested_n"]
        elif isinstance(s.get("percent"), (int, float)):
            pct, n = float(s["percent"]), s.get("n_tumors_in_study") if isinstance(s.get("n_tumors_in_study"), int) else None
        else:
            continue
        pooled.setdefault(s["marker"], {})[s["id"]] = (pct, n, s.get("site") or "")
    chosen = sorted([(m, r) for m, r in pooled.items() if len(r) >= 2], key=lambda mr: -len(mr[1]))
    if chosen:
        def each(r):
            parts = []
            for ident, (pct, n, site) in sorted(r.items(), key=lambda kv: -kv[1][0]):
                parts.append("%d%%%s, %s (%s)" % (round(pct), " of %d" % n if n else "", B.esc(site), source_link(B, S, ident)))
            return "; ".join(parts)
        sections.append(("stains", "Immunostains in myoepithelial carcinoma", """
<p class="chart-note">Markers with a positivity rate in two or more series of the carcinoma. Each series is shown on its own,
because they differ in site, antibody and cut-off and their abstracts do not all give counts that could be added up.</p>%s"""
                         % PG.table(["Marker", "Series", "Range", "Each series: share positive, tumors, site"], [
                             ("<td><strong>%s</strong></td>" % B.esc(m[:1].upper() + m[1:]), '<td class="num">%d</td>' % len(r),
                              '<td class="num">%d to %d%%</td>' % (round(min(v[0] for v in r.values())), round(max(v[0] for v in r.values()))),
                              "<td>%s</td>" % each(r)) for m, r in chosen])))
    if looks:
        grouped = collections.OrderedDict()
        for x in looks:
            g = grouped.setdefault(x["lookalike"].strip().lower(), {"ids": set(), "sites": collections.Counter(), "how": []})
            g["ids"].add(x["id"])
            g["sites"][x.get("site") or ""] += 1
            if x.get("how_told_apart"):
                g["how"].append((x["how_told_apart"], x["id"]))
        top = sorted(grouped.items(), key=lambda kv: -len(kv[1]["ids"]))
        top = [kv for kv in top if len(kv[1]["ids"]) >= 2][:40]
        sections.append(("lookalikes", "Tumors it is confused with", """
<p class="chart-note">Tumors named alongside myoepithelial carcinoma in two or more abstracts, with how those abstracts say
they are told apart.</p>%s""" % PG.table(["Tumor", "Papers", "Mostly in", "How papers tell them apart"], [
            ("<td><strong>%s</strong></td>" % B.esc(name.capitalize()), '<td class="num">%d</td>' % len(g["ids"]),
             "<td>%s</td>" % B.esc(", ".join(s for s, _ in g["sites"].most_common(2) if s and s != "not site-specific")),
             "<td>%s</td>" % " ".join("%s (%s)" % (B.esc(text.rstrip(".") + "."), source_link(B, S, i)) for text, i in g["how"][:2]))
            for name, g in top])))
    sections.append(("criteria", "Criteria and grading", """
<p>In the salivary glands the diagnosis requires a tumor that is unequivocally malignant and exclusively
myoepithelial[[savera2000]]. In soft tissue, at least moderate cytologic atypia makes a myoepithelial tumor
malignant[[jo2015]]. Grading is described as controversial[[kong2015]]. Necrosis and vascular invasion correlated with
disease-free survival in one salivary series[[kong2015]], and tumor size over 5 cm and more than 10 mitoses per 10
high-power fields with worse survival in the pooled literature[[giridhar2019]].</p>
<p>For patients, the <a href="../pathology-report/">guide to reading a report</a> explains these terms.</p>"""))
    return PG.render(B, S, "pathology", "Myoepithelial Carcinoma Pathology: Immunostains and Differential Diagnosis",
                     "Pooled immunohistochemistry positivity rates for myoepithelial carcinoma across published series, and "
                     "the tumors it is mistaken for with how to tell them apart.",
                     "Pathology", "Stains and look-alikes", "What the series report under the microscope, pooled.", sections)


def search_page(B, S):
    entries = []
    for path, title, heads in S.get("site_map", []):
        entries.append(["Page", title, "", path + "/" if path else ""])
        for sid, heading in heads:
            entries.append(["Section", "%s: %s" % (title, heading), "", (path + "/" if path else "") + "#" + sid])
    for sec in B.C.SECTIONS:
        entries.append(["Section", sec["title"], "Main page", "#" + sec["id"]])
    for term, text in B.C.GLOSSARY:
        entries.append(["Glossary", term, B.plain(text)[:140], "#glossary"])
    for o in S["orgs"]:
        if o["ok"]:
            entries.append(["Organization", o["name"], o["what"], o["url"]])
    for c in S["cases"]:
        url = "https://pubmed.ncbi.nlm.nih.gov/%s/" % c["pmid"] if c["pmid"] else ("https://doi.org/%s" % c["doi"] if c["doi"] else "")
        if url:
            entries.append(["Case", " · ".join(x for x in (PG.describe_case(c), c["site"], c["country"]) if x),
                            "%s (%s)" % ((c["title"] or "")[:120], c["year"] or ""), url])
    for t in S["trials"]:
        entries.append(["Trial", t["title"], "%s · %s" % (t["nct_id"], t["status"].replace("_", " ").lower()), t["url"]])
    for p in S["directory"]:
        url = B.paper_url(p)
        if url:
            tags = [B.SITE_LABELS[s] for s in p["sites"] if s in B.SITE_LABELS] + (["Case report"] if p["is_case_report"] else [])
            entries.append(["Paper", (p["title"] or "")[:200], " · ".join(
                x for x in (B.short_authors(p, 2), p["journal"], str(p["year"] or ""), ", ".join(tags)) if x), url])
    (B.OUT / "data" / "search.json").write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    sections = [("search", "Search", """
<form class="search-form" role="search" onsubmit="return false">
  <label for="q" style="position:absolute;left:-9999px">Search this site</label>
  <input id="q" class="dir-search" type="search" placeholder="A site, a gene, a drug, an author, a year" autocomplete="off" autofocus>
</form>
<p class="dir-count" id="search-count" aria-live="polite">%s entries: pages, glossary terms, organizations, cases, trials and papers.</p>
<div id="search-results"></div>
<noscript><p>Search needs JavaScript. The <a href="../papers/">directory of papers</a> and the <a href="../">contents</a> work without it.</p></noscript>
<script src="../static/search.js" defer></script>""" % B.num(len(entries)))]
    return PG.render(B, S, "search", "Search the Myoepithelial Carcinoma Reference",
                     "Search every page, paper, published case, trial, glossary term and organization in the myoepithelial "
                     "carcinoma reference.", "Search", "Search", "One box for everything on this site.", sections, ld_type="WebPage")


def feed(B, S):
    C = B.C
    papers = [p for p in S["core"] if p["named_in_title"] and not p["is_animal"]]
    papers.sort(key=lambda p: (S["first_seen"].get(p["id"], ""), p["year"] or 0, p["date"] or ""), reverse=True)
    latest = S["harvest_log"][-1]["date"]
    items = []
    for p in papers[:60]:
        url = B.paper_url(p)
        items.append("""  <entry>
    <id>urn:myo:%s</id>
    <title>%s</title>
    <link href="%s"/>
    <updated>%sT00:00:00Z</updated>
    <summary>%s. %s, %s.</summary>
  </entry>""" % (html.escape(p["id"]), html.escape(p["title"] or ""), html.escape(url or C.BASE_URL + "new/"),
                 S["first_seen"].get(p["id"], latest), html.escape(B.short_authors(p, 3)), html.escape(p["journal"] or ""), p["year"] or ""))
    (B.OUT / "feed.xml").write_text("""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>%sfeed.xml</id>
  <title>Myoepithelial carcinoma: new papers</title>
  <subtitle>Papers naming the disease, as each search of the research indexes finds them.</subtitle>
  <link href="%sfeed.xml" rel="self"/>
  <link href="%snew/"/>
  <updated>%sT00:00:00Z</updated>
  <author><name>%s</name></author>
%s
</feed>
""" % (C.BASE_URL, C.BASE_URL, C.BASE_URL, latest, html.escape(C.AUTHOR), "\n".join(items)), encoding="utf-8", newline="\n")


def essentials_pages(B, S):
    folder = B.HERE / "translations"
    english = json.loads((folder / "en.json").read_text(encoding="utf-8")) if (folder / "en.json").exists() else None
    if not english:
        return []
    urls = []
    C = B.C
    for code, name, lang in LANGS:
        path = folder / ("%s.json" % code)
        if not path.exists():
            continue
        t = dict(english, **json.loads(path.read_text(encoding="utf-8")))

        def rows(prefix, with_title):
            out, n = [], 1
            while "%s_%d" % (prefix, n) in t:
                out.append((t.get("%s_%d_%s" % (prefix, n, "label" if prefix == "fact" else "title")) if with_title else None,
                            t["%s_%d" % (prefix, n)]))
                n += 1
            return out
        facts = "".join("<dt>%s</dt><dd>%s</dd>" % (B.esc(a), B.esc(b)) for a, b in rows("fact", True))
        first = "".join('<div class="step3"><div class="step3-n">%d</div><div class="step3-t">%s</div><p>%s</p></div>'
                        % (i, B.esc(a), B.esc(b)) for i, (a, b) in enumerate(rows("first", True), 1))
        plan = "".join('<li><div class="plan-t">%s</div><div class="plan-d">%s</div></li>' % (B.esc(a), B.esc(b)) for a, b in rows("plan", True))
        questions = "".join("<li>%s</li>" % B.esc(b) for _, b in rows("question", False))
        url = C.BASE_URL + code + "/"
        alternates = "".join('<link rel="alternate" hreflang="%s" href="%s%s/">\n' % (l, C.BASE_URL, c) for c, _, l in LANGS)
        head = B.head(t["title"], t["intro"], url, [], "../", S["iso"]).replace(
            '<link rel="alternate" hreflang="en" href="%s">' % url,
            alternates + '<link rel="alternate" hreflang="en" href="%s">' % C.BASE_URL)
        main = """
<div class="page" lang="%s">
<header class="title-block">
  <p class="kicker"><a href="../">Myoepithelial carcinoma</a> / %s</p>
  <h1>%s</h1>
  <p class="standfirst">%s</p>
  <p class="meta-line">%s %s</p>
</header>
<div class="content" style="margin:0">
  <section class="section quick"><h2>%s</h2><dl>%s</dl></section>
  <section class="section"><h2 class="section-heading">%s</h2><div class="steps3">%s</div><p>%s</p></section>
  <section class="section"><h2 class="section-heading">%s</h2><ol class="plan">%s</ol></section>
  <section class="section"><h2 class="section-heading">%s</h2><ul class="checklist">%s</ul></section>
  <section class="section"><h2 class="section-heading">%s</h2><p>%s</p>
  <p><a class="btn btn-primary" href="../">%s</a></p></section>
</div>
</div>""" % (lang, name, B.esc(t["title"]), B.esc(t["intro"]), B.esc(t["not_advice"]), B.esc(t.get("machine_note", "")),
             B.esc(t["h_facts"]), facts, B.esc(t["h_first"]), first, B.esc(t["own"]), B.esc(t["h_plan"]), plan,
             B.esc(t["h_questions"]), questions, B.esc(t["h_numbers"]), B.esc(t["numbers"]), B.esc(t["full_link"]))
        out = B.OUT / code
        out.mkdir(parents=True, exist_ok=True)
        page = B.PAGE.format(head=head, nav=B.nav("../"), main=main, footer=B.footer(S["ctx"]), script="../static/app.js")
        (out / "index.html").write_text(page.replace('<html lang="en">', '<html lang="%s">' % lang), encoding="utf-8", newline="\n")
        urls.append(url)
    return urls


def build_more(B, S):
    urls = []
    for page in (treatments_page, trials_page, recurrence_page, pathology_page):
        url = page(B, S)
        if url:
            urls.append(url)
    urls += essentials_pages(B, S)
    urls.append(search_page(B, S))      # last, so it can index every page built before it
    feed(B, S)
    return urls
