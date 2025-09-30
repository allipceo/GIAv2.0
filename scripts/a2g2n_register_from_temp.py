# -*- coding: utf-8 -*-
"""
Register pages to Notion from markdown files generated in temp_drive.

Environment:
- NOTION_TOKEN
- TARGET_DATABASE_ID

Usage:
  set PYTHONPATH=.
  python scripts/a2g2n_register_from_temp.py --folder temp_drive
"""

from __future__ import annotations

import argparse
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import logging
import requests


def _robust_load_env() -> None:
    """Load environment variables from .env/.env.local/config.env with BOM tolerance.

    This mirrors the tolerant loader in src/run_stage3.py and adds BOM-safe reading.
    """
    try:
        from dotenv import load_dotenv
    except Exception:
        load_dotenv = None  # type: ignore

    # Try python-dotenv first (won't work on UTF-16 BOM files)
    if load_dotenv is not None:
        for fname in [".env", ".env.local", "config.env"]:
            try:
                load_dotenv(dotenv_path=fname, encoding="utf-8", override=False)
            except Exception:
                pass

    # BOM-tolerant fallback simple parser
    for fname in [".env", ".env.local", "config.env"]:
        p = Path(fname)
        if not p.exists():
            continue
        try:
            raw = p.read_bytes()
            # Detect common BOMs
            if raw.startswith(b"\xef\xbb\xbf"):
                text = raw[3:].decode("utf-8", errors="ignore")
            elif raw.startswith(b"\xff\xfe"):
                text = raw.decode("utf-16", errors="ignore")
            elif raw.startswith(b"\xfe\xff"):
                text = raw.decode("utf-16-be", errors="ignore")
            else:
                text = raw.decode("utf-8", errors="ignore")
            for line in text.splitlines():
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if "=" in s:
                    k, v = s.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and v and (k not in os.environ):
                        os.environ[k] = v
        except Exception:
            continue


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": os.getenv("NOTION_VERSION", "2022-06-28"),
        "Content-Type": "application/json; charset=utf-8",
    }


def get_database_schema(token: str, database_id: str) -> Dict[str, Any]:
    resp = requests.get(
        f"https://api.notion.com/v1/databases/{database_id}", headers=_headers(token), timeout=30
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Get database schema failed: {resp.status_code} {resp.text[:300]}")
    return resp.json()


def resolve_property_ids_for_minimal(schema: Dict[str, Any]) -> Dict[str, str]:
    props: Dict[str, Any] = schema.get("properties", {}) or {}
    # Notion title property id is always the literal string "title"
    title_id = "title"
    if "title" not in (meta.get("id") if isinstance(meta, dict) else None for meta in props.values()):
        # Fallback: find by type
        for meta in props.values():
            if isinstance(meta, dict) and meta.get("type") == "title":
                title_id = meta.get("id", "title")
                break

    # For this run, we only need the title property id
    return {"title_id": title_id}


def read_title_from_md(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.stem
    for line in text.splitlines():
        s = line.strip()
        if s:
            # strip leading markdown header marks
            return s.lstrip("# ")[:200]
    return path.stem[:200]


def create_page(token: str, database_id: str, title: str, prop_ids: Dict[str, str]) -> str:
    # Minimal payload with property IDs only
    properties: Dict[str, Any] = {prop_ids["title_id"]: {"title": [{"text": {"content": title}}]}}

    payload = {"parent": {"database_id": database_id}, "properties": properties}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    resp = requests.post("https://api.notion.com/v1/pages", headers=_headers(token), data=data, timeout=30)
    if resp.status_code // 100 != 2:
        raise RuntimeError(f"Create page failed: {resp.status_code} {resp.text[:300]}")
    pj = resp.json()
    return pj.get("id", "")


def main() -> int:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="%(asctime)s %(levelname)s %(message)s")
    _robust_load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="temp_drive")
    args = parser.parse_args()

    token = os.getenv("NOTION_TOKEN", "").strip()
    dbid = os.getenv("TARGET_DATABASE_ID", "").strip()
    if not token or not dbid:
        print("NOTION_TOKEN or TARGET_DATABASE_ID missing")
        return 2

    src = Path(args.folder)
    if not src.exists():
        print(f"folder not found: {src}")
        return 3

    files = sorted([p for p in src.glob("*.md")])
    if not files:
        print("no markdown files found")
        return 4

    # Resolve property ids from schema (title and optional url)
    schema = get_database_schema(token, dbid)
    prop_ids = resolve_property_ids_for_minimal(schema)

    created: List[Dict[str, str]] = []
    for fp in files:
        title = read_title_from_md(fp)
        try:
            page_id = create_page(token, dbid, title, prop_ids)
            created.append({"title": title, "page_id": page_id})
            print(f"CREATED: {title} -> {page_id}")
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {fp.name} -> {exc}")

    print("\n=== created ===")
    for item in created:
        print(json.dumps(item, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


