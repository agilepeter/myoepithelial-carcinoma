"""Check and merge what the readers extracted into the catalog.

    python harvest/merge_reading.py <folder with the readers' output files>

Copies the raw outputs into data/read/ for the record, validates them, and
writes:
    data/catalog/cases.jsonl        the registry, with read fields replacing the rule-based ones
    data/catalog/skin_cases.jsonl   patients from skin papers read in full
    data/catalog/treatments.jsonl   drug treatments reported
    data/catalog/trials_read.jsonl  open trials with an eligibility judgment
    data/catalog/stains.jsonl       immunostain rates
    data/catalog/lookalikes.jsonl   tumors it is confused with
    data/catalog/verification.jsonl each cited claim checked against its source

Missing input files are skipped, so this can run as results arrive.
"""

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import CATALOG, DATA, ROOT, log, read_jsonl, write_jsonl  # noqa: E402

READ = DATA / "read"
GROUPS = {"salivary", "soft_tissue", "skin", "breast", "lung", "bone", "head_neck_other", "gyn", "other"}


def load(path):
    """Read JSONL, skipping lines that do not parse, and say how many were skipped."""
    rows, bad = [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            bad += 1
    if bad:
        log("  %s: %d unparseable lines skipped" % (path.name, bad))
    return rows


def take(src, name):
    path = src / name
    if not path.exists():
        return None
    READ.mkdir(parents=True, exist_ok=True)
    if path.resolve() != (READ / name).resolve():     # re-running from data/read itself
        shutil.copyfile(path, READ / name)
    return path


def cases(src):
    read = {}
    for n in range(1, 5):
        path = take(src, "cases_read_%d.jsonl" % n)
        if path:
            for row in load(path):
                read[row.get("id")] = row
    if not read:
        return
    registry = read_jsonl(CATALOG / "cases.jsonl")
    merged = 0
    for c in registry:
        r = read.get(c["id"])
        c["read"] = bool(r)
        if not r:
            c.setdefault("status", None)
            continue
        merged += 1
        c["not_this_disease"] = r.get("is_myoepithelial_carcinoma") is False
        c["patients_in_report"] = r.get("patients_in_report") or 1
        c["age"], c["age_unit"] = r.get("age"), r.get("age_unit") if r.get("age") is not None else None
        c["age_years"] = None
        if isinstance(c["age"], (int, float)):
            unit = c["age_unit"] or "year"
            c["age_years"] = c["age"] if unit == "year" else round(c["age"] / {"month": 12.0, "week": 52.0, "day": 365.0}.get(unit, 1.0), 1)
        c["child"] = c["age_years"] is not None and c["age_years"] < 18
        c["sex"] = r.get("sex") or ""
        c["site"] = (r.get("primary_site") or "").strip().capitalize()
        if r.get("site_group") in GROUPS:
            c["site_group"] = "" if r["site_group"] == "other" else r["site_group"]
        c["arose_in"] = r.get("arose_in")
        c["size_cm"] = r.get("size_cm") if isinstance(r.get("size_cm"), (int, float)) else None
        c["treatments"] = [t for t in r.get("treatments") or [] if isinstance(t, str)]
        c["drugs"] = [d for d in r.get("drugs") or [] if isinstance(d, str)]
        c["margin"] = r.get("margin")
        c["genes"] = [g for g in r.get("genes_or_fusions") or [] if isinstance(g, str)]
        c["recurrence"], c["metastasis"] = r.get("recurrence"), r.get("metastasis")
        c["metastasis_sites"] = [s for s in r.get("metastasis_sites") or [] if isinstance(s, str)]
        c["follow_up_months"] = r.get("follow_up_months") if isinstance(r.get("follow_up_months"), (int, float)) else None
        c["status"] = r.get("status_at_last_follow_up")
        c["confidence"] = r.get("confidence")
        c["events"] = [name for name, on in (("recurrence", c["recurrence"] == "yes"), ("metastasis", c["metastasis"] == "yes"),
                                             ("death", (c["status"] or "").startswith("died"))) if on]
    write_jsonl(CATALOG / "cases.jsonl", registry)
    log("cases: %d of %d registry entries now come from a read abstract; %d flagged as a different diagnosis; %d describe several patients"
        % (merged, len(registry), sum(1 for c in registry if c.get("not_this_disease")),
           sum(1 for c in registry if (c.get("patients_in_report") or 1) > 1)))


def simple(src, name, target, key):
    path = take(src, name)
    if not path:
        return
    rows = load(path)
    write_jsonl(CATALOG / target, rows)
    log("%s: %d lines, %d distinct %s" % (target, len(rows), len({r.get(key) for r in rows}), key))


def main(src):
    cases(src)
    simple(src, "skin_read.jsonl", "skin_cases.jsonl", "id")
    simple(src, "drugs_read.jsonl", "treatments.jsonl", "id")
    simple(src, "trials_read.jsonl", "trials_read.jsonl", "nct_id")
    simple(src, "stains_read.jsonl", "stains.jsonl", "id")
    simple(src, "lookalikes_read.jsonl", "lookalikes.jsonl", "id")
    simple(src, "verification.jsonl", "verification.jsonl", "key")
    path = take(src, "skin_reviews.json")
    if path:
        shutil.copyfile(path, CATALOG / "skin_reviews.json")
    path = take(src, "verification_summary.md")
    if path:
        summary(path, ROOT / "notes" / "verification-summary.md")


def summary(path, dest):
    """Copy the checker's summary into notes/, keeping the corrections recorded below it there."""
    text = path.read_text(encoding="utf-8")
    if dest.exists():
        old = dest.read_text(encoding="utf-8")
        at = old.find("\n## Corrections applied")
        if at != -1:
            text = text.rstrip("\n") + "\n\n" + old[at:]
    dest.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
