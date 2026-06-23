"""
Targeted DD pass for TakeMeter (Milestone 3): harvest analysis-heavy r/stocks
posts that are buried below the top news/sentiment posts, to boost the scarce
`evidenced_analysis` class.

DD posts get few upvotes, so listings miss them. We use FetchLayer's search
endpoint scoped to r/stocks with flair / valuation-term queries. Output:
dd_candidates.csv (title + previewText), which the human then labels. Raw
responses cached under raw_json/ so re-runs cost no requests.
"""

import csv
import json
import os
import re
import time

import requests

BASE = "https://fetchlayer.dev/api"
RAW_DIR = "raw_json"
OUT_FILE = "dd_candidates.csv"
REQUEST_CAP = 29  # leave 1 of 30 as buffer
SLEEP = 1.5
MAX_TEXT_CHARS = 6000
MIN_CHARS = 80

# Queries chosen to surface data-backed analysis, not news. Reddit search syntax.
QUERIES = [
    'subreddit:stocks flair:"Company Analysis"',
    'subreddit:stocks flair:"Industry Discussion"',
    'subreddit:stocks valuation revenue earnings',
    'subreddit:stocks DD intrinsic value price target',
]

_request_count = 0


def load_key():
    key = os.environ.get("FETCHLAYER_API_KEY")
    if not key and os.path.exists(".fetchlayer_key"):
        key = open(".fetchlayer_key").read().strip()
    if not key:
        raise SystemExit("No API key.")
    return key


HEADERS = {"Authorization": f"Bearer {load_key()}", "Content-Type": "application/json"}


def clean(t):
    if not t:
        return ""
    t = t.strip()
    if t in ("[removed]", "[deleted]"):
        return ""
    return re.sub(r"\s+", " ", t)[:MAX_TEXT_CHARS]


def search(query, idx):
    global _request_count
    cache = os.path.join(RAW_DIR, f"search_{idx}.json")
    if os.path.exists(cache):
        print(f"[cache] search_{idx}")
        return json.load(open(cache, encoding="utf-8"))
    if _request_count >= REQUEST_CAP:
        raise SystemExit("Request cap reached.")
    _request_count += 1
    print(f"[req {_request_count}] search: {query}")
    payload = {"query": query, "sort": "top", "time": "all", "limit": 100}
    r = requests.post(f"{BASE}/reddit/search", headers=HEADERS, json=payload, timeout=90)
    r.raise_for_status()
    d = r.json()
    os.makedirs(RAW_DIR, exist_ok=True)
    json.dump(d, open(cache, "w", encoding="utf-8"))
    time.sleep(SLEEP)
    return d


def main():
    # Exclude ids we already have so we don't double-count.
    seen = set()
    if os.path.exists("candidates.csv"):
        seen = {r["id"] for r in csv.DictReader(open("candidates.csv", encoding="utf-8"))}

    pool = {}
    for i, q in enumerate(QUERIES):
        d = search(q, i)
        items = d.get("items", [])
        print(f"  -> {len(items)} items")
        for it in items:
            pid = it.get("id")
            if not pid or pid in seen or pid in pool:
                continue
            if (it.get("subreddit") or "").lower() != "stocks":
                continue
            title = it.get("title") or ""
            body = it.get("previewText") or ""
            text = clean((title + ". " + body).strip())
            if len(text) < MIN_CHARS:
                continue
            pool[pid] = {
                "id": pid, "type": "post", "score": it.get("score", 0),
                "permalink": it.get("permalink", ""), "text": text,
            }

    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "type", "score", "permalink", "text", "label", "notes"])
        w.writeheader()
        for r in pool.values():
            w.writerow({**r, "label": "", "notes": ""})

    print(f"\nUsed {_request_count} requests. Wrote {len(pool)} new DD candidates to {OUT_FILE}.")


if __name__ == "__main__":
    main()
