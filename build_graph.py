"""
build_graph.py — Notion → graph_data.json extractor

Required environment variables:
  NOTION_TOKEN       — Notion Internal Integration Secret
  NOTION_DATABASE_ID — 32-char database ID from the page URL

Output: graph_data.json  (nodes + links)

Relationship sources (both are merged and deduplicated):
  1. Prerequisites relation property on each database page
  2. Inline @page mentions anywhere in the page body text
"""

import json
import os
import sys
import time

import requests

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
DATABASE_ID  = os.environ.get("NOTION_DATABASE_ID", "")

HEADERS = {
    "Authorization":  f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type":   "application/json",
}

# ── Property names in your Notion database ────────────────────────────────────
PROP_NAME         = "Name"           # Title property
PROP_TAG          = "Tags"           # Select / Multi-select
PROP_PREREQUISITES = "Prerequisites" # Relation property
# ─────────────────────────────────────────────────────────────────────────────


def fetch_all_pages() -> list[dict]:
    """Query the Notion database with pagination, return all page objects."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    pages: list[dict] = []
    cursor = None

    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor

        response = requests.post(url, headers=HEADERS, json=body, timeout=30)
        if response.status_code != 200:
            print(f"[ERROR] Notion API returned {response.status_code}: {response.text}",
                  file=sys.stderr)
            sys.exit(1)

        data = response.json()
        pages.extend(data.get("results", []))

        if data.get("has_more"):
            cursor = data.get("next_cursor")
        else:
            break

    return pages


def extract_text(prop: dict) -> str:
    """Extract plain text from a title or rich_text property."""
    ptype = prop.get("type", "")
    items = prop.get(ptype, [])
    return "".join(block.get("plain_text", "") for block in items).strip()


def extract_tag(prop: dict) -> str:
    """Extract the first tag value from a select or multi_select property."""
    ptype = prop.get("type", "")
    if ptype == "select":
        sel = prop.get("select")
        return sel["name"] if sel else ""
    if ptype == "multi_select":
        items = prop.get("multi_select", [])
        return items[0]["name"] if items else ""
    return ""


def extract_relations(prop: dict) -> list[str]:
    """Return a list of related page IDs from a relation property."""
    return [r["id"] for r in prop.get("relation", [])]


def fetch_mention_ids(page_id: str) -> list[str]:
    """
    Walk the block tree of a page and collect every inline @page mention.
    Returns a list of mentioned page IDs (may contain duplicates).
    """
    mentioned: list[str] = []
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    cursor = None

    while True:
        params: dict = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor

        response = requests.get(url, headers=HEADERS, params=params, timeout=30)

        # Rate-limit backoff (Notion returns 429)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "1"))
            time.sleep(retry_after)
            continue

        if response.status_code != 200:
            # Non-fatal: skip blocks we can't read (e.g. unsupported types)
            break

        data = response.json()

        for block in data.get("results", []):
            # Each supported block type exposes a rich_text array
            block_type = block.get("type", "")
            content = block.get(block_type, {})
            rich_text = content.get("rich_text", [])

            for segment in rich_text:
                if segment.get("type") == "mention":
                    mention = segment.get("mention", {})
                    if mention.get("type") == "page":
                        mentioned.append(mention["page"]["id"])

        if data.get("has_more"):
            cursor = data.get("next_cursor")
        else:
            break

    return mentioned


def build_graph(pages: list[dict]) -> dict:
    nodes: list[dict] = []
    links: list[dict] = []

    # Build a set of valid IDs so we can skip dangling relations
    valid_ids = {p["id"] for p in pages}

    # Track seen (source, target) pairs to deduplicate across both sources
    seen_links: set[tuple[str, str]] = set()

    def add_link(source: str, target: str) -> None:
        key = (source, target)
        if key not in seen_links and source in valid_ids and target in valid_ids:
            seen_links.add(key)
            links.append({"source": source, "target": target})

    for i, page in enumerate(pages):
        props   = page.get("properties", {})
        page_id = page["id"]

        # Node label
        name_prop = props.get(PROP_NAME, {})
        name = extract_text(name_prop) or page_id

        # Node group (tag)
        tag_prop = props.get(PROP_TAG, {})
        group = extract_tag(tag_prop)

        nodes.append({"id": page_id, "name": name, "group": group})

        # Source 1: Prerequisites relation property
        prereq_prop = props.get(PROP_PREREQUISITES, {})
        for prereq_id in extract_relations(prereq_prop):
            add_link(prereq_id, page_id)

        # Source 2: Inline @page mentions in the page body
        print(f"[INFO]   ({i + 1}/{len(pages)}) Scanning mentions in '{name}' …")
        for mentioned_id in fetch_mention_ids(page_id):
            # Direction: mentioned page → current page (same as Prerequisites)
            add_link(mentioned_id, page_id)

    return {"nodes": nodes, "links": links}


def main() -> None:
    if not NOTION_TOKEN or not DATABASE_ID:
        print("[ERROR] NOTION_TOKEN and NOTION_DATABASE_ID must be set.", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Fetching pages from database {DATABASE_ID} …")
    pages = fetch_all_pages()
    print(f"[INFO] Retrieved {len(pages)} page(s).")

    graph = build_graph(pages)
    print(f"[INFO] Graph: {len(graph['nodes'])} nodes, {len(graph['links'])} links.")

    out_path = os.path.join(os.path.dirname(__file__), "graph_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Wrote {out_path}")


if __name__ == "__main__":
    main()
