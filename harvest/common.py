"""Shared helpers: paths, polite HTTP with retries, gzip and JSONL I/O."""

import datetime
import gzip
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CATALOG = DATA / "catalog"
FULLTEXT = DATA / "fulltext"

USER_AGENT = "myo-corpus/0.1 (personal research archive)"
TOOL = "myo-corpus"

_last_call = {}


def log(*parts):
    print(*parts, flush=True)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url, data=None, min_interval=0.4, retries=6, timeout=90, headers=None):
    """GET (or POST when data is given) with per-host spacing and backoff.

    Raises urllib.error.HTTPError straight away on 404 so callers can record a
    missing item; other failures are retried.
    """
    host = urllib.parse.urlsplit(url).netloc
    for attempt in range(retries):
        wait = _last_call.get(host, 0) + min_interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_call[host] = time.monotonic()
        try:
            req = urllib.request.Request(url, data=data, headers=dict({"User-Agent": USER_AGENT}, **(headers or {})))
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as err:
            if err.code == 404 or attempt == retries - 1:
                raise
            if err.code not in (408, 425, 429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
            if attempt == retries - 1:
                raise
        time.sleep(min(60, 2 ** attempt * 2))
    raise RuntimeError("unreachable")


def write_gz(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    # mtime=0 keeps the file byte-identical when the content has not changed.
    with open(path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
            gz.write(payload)


def read_gz(path):
    with gzip.open(path, "rb") as fh:
        return fh.read()


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True))
            fh.write("\n")


def read_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def replace_batches(folder, pattern, payloads, name_fmt):
    """Swap a folder's raw batch files for a freshly downloaded set."""
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob(pattern):
        old.unlink()
    for i, payload in enumerate(payloads):
        write_gz(folder / (name_fmt % i), payload)


def main_guard(fn):
    try:
        fn()
    except KeyboardInterrupt:
        sys.exit(130)
