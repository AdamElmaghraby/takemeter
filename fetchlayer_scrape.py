"""
r/stocks candidate scraper for TakeMeter (Milestone 3), via the FetchLayer API.

Reddit blocks unauthenticated scraping, so we go through FetchLayer's managed
Reddit API (free tier = 30 requests). This script is request-budget aware:
  - 3 community-posts calls (top/month, top/year, hot) -> post pool (title +
    previewText). Good source of evidenced_analysis / logical_speculation.
  - N post calls on the most-commented threads -> full bodyText + comment tree.
    Comments are a good source of emotional_sentiment / short speculation.

Every raw API response is saved under raw_json/ so we never re-spend a request.
Output: candidates.csv with empty `label` / `notes` columns for manual review.

Key is read from env FETCHLAYER_API_KEY or local file .fetchlayer_key.
Run:  python3 fetchlayer_scrape.py
"""

import csv
import json
import os
import re
import time

import requests

BASE = "https://fetchlayer.dev/api"
OUT_FILE = "candidates.csv"
RAW_DIR = "raw_json"

POST_LISTINGS = [("top", "month"), ("top", "year"), ("hot", None)]
LIST_LIMIT = 100            # posts requested per listing call
COMMENT_POOL_POSTS = 18     # most-commented posts to harvest comments from
COMMENTS_PER_POST = 8       # comments to keep per thread
REQUEST_CAP = 28            # hard stop to stay under the 30 free requests
SLEEP = 1.5

MIN_POST_CHARS = 120
MIN_COMMENT_CHARS = 80
MAX_COMMENT_CHARS = 1800
MAX_TEXT_CHARS = 6000

_request_count = 0


def load_key():
    key = os.environ.get("FETCHLAYER_API_KEY")
    if not key and os.path.exists(".fetchlayer_key"):
        with open(".fetchlayer_key") as f:
            key = f.read().strip()
    if not key:
        raise SystemExit("No API key. Put it in .fetchlayer_key or export FETCHLAYER_API_KEY.")
    return key


HEADERS = {"Authorization": f"Bearer {load_key()}", "Content-Type": "application/json"}


def clean(text):
    if not text:
        return ""
    text = text.strip()
    if text in ("[removed]", "[deleted]"):
        return ""
    return re.sub(r"\s+", " ", text)[:MAX_TEXT_CHARS]


def post_api(endpoint, payload, save_as):
    """POST to FetchLayer, save raw response, respect the request cap.

    If a cached raw response already exists, load it instead of spending a
    request — so re-running the script never re-spends the free quota.
    """
    global _request_count
    cache_path = os.path.join(RAW_DIR, save_as)
    if os.path.exists(cache_path):
        print(f"[cache] /{endpoint}  {save_as}")
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)
    if _request_count >= REQUEST_CAP:
        raise SystemExit(f"Hit request cap ({REQUEST_CAP}); stopping to preserve free quota.")
    _request_count += 1
    print(f"[req {_request_count}] POST /{endpoint}  {payload}")
    resp = requests.post(f"{BASE}/{endpoint}", headers=HEADERS, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    time.sleep(SLEEP)
    return data


def fetch_posts():
    posts = {}
    for sort, t in POST_LISTINGS:
        payload = {"subreddit": "stocks", "sort": sort, "limit": LIST_LIMIT}
        if t:
            payload["time"] = t
        tag = f"{sort}_{t or 'na'}"
        data = post_api("reddit/community-posts", payload, f"list_{tag}.json")
        items = data.get("items", [])
        print(f"  -> {len(items)} items")
        for it in items:
            # NOTE: FetchLayer reports stickied=true for every item, so we can't
            # filter on it. A couple of genuine pinned posts may slip in; that's
            # negligible and we'll catch them during manual review.
            pid = it.get("id")
            if not pid:
                continue
            posts.setdefault(pid, {
                "id": pid,
                "url": it.get("url") or it.get("permalink"),
                "title": it.get("title", ""),
                "preview": it.get("previewText", ""),
                "score": it.get("score", 0),
                "comment_count": it.get("commentCount", 0),
                "permalink": it.get("permalink", ""),
                "body": "",  # filled if we fetch the full post below
            })
    return posts


def fetch_comments_and_bodies(posts):
    """For the most-commented posts: pull full bodyText + top-level comments."""
    ranked = sorted(posts.values(), key=lambda p: p["comment_count"], reverse=True)
    targets = ranked[:COMMENT_POOL_POSTS]
    comments = []
    for p in targets:
        if _request_count >= REQUEST_CAP:
            print("Reached request cap; stopping comment harvest.")
            break
        try:
            data = post_api("reddit/post", {"url": p["url"], "pages": 1}, f"post_{p['id']}.json")
        except requests.HTTPError as e:
            print(f"  skip {p['id']}: {e}")
            continue
        # Upgrade the post's text to the full body now that we have it.
        p["body"] = clean(data.get("bodyText", ""))
        kept = 0
        for c in data.get("comments", []):
            if kept >= COMMENTS_PER_POST:
                break
            if c.get("depth", 0) != 0:
                continue
            body = clean(c.get("bodyText", ""))
            if not (MIN_COMMENT_CHARS <= len(body) <= MAX_COMMENT_CHARS):
                continue
            comments.append({
                "id": c.get("id"),
                "type": "comment",
                "score": c.get("score", 0),
                "permalink": c.get("permalink", ""),
                "text": body,
            })
            kept += 1
    return comments


def main():
    posts = fetch_posts()
    print(f"Collected {len(posts)} unique posts from listings.")
    comments = fetch_comments_and_bodies(posts)
    print(f"Collected {len(comments)} candidate comments.")

    rows = []
    for p in posts.values():
        # Prefer full body when we fetched it, else title + preview.
        title = p.get("title") or ""
        body = p.get("body") or p.get("preview") or ""
        text = clean((title + ". " + body).strip())
        if len(text) < MIN_POST_CHARS:
            continue
        rows.append({"id": p["id"], "type": "post", "score": p["score"],
                     "permalink": p["permalink"], "text": text})
    rows.extend(comments)

    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "type", "score", "permalink", "text", "label", "notes"])
        w.writeheader()
        for r in rows:
            w.writerow({"id": r["id"], "type": r["type"], "score": r["score"],
                        "permalink": r["permalink"], "text": r["text"], "label": "", "notes": ""})

    n_posts = sum(1 for r in rows if r["type"] == "post")
    n_comments = sum(1 for r in rows if r["type"] == "comment")
    print(f"\nUsed {_request_count} FetchLayer requests.")
    print(f"Wrote {len(rows)} candidates to {OUT_FILE} ({n_posts} posts, {n_comments} comments).")


if __name__ == "__main__":
    main()
