#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
property_id 기반 status.name 업데이트 유틸리티

환경변수:
- NOTION_TOKEN: Notion 내부 연동 키
- TARGET_DATABASE_ID: 대상 DB ID (parent.database_id 가드용)

사용 예:
python scripts/notion_status_update.py --page-id <uuid> --property-id :Vmr --status-name 검토중

증빙 로그:
- 콘솔 출력과 JSON 로그 파일(status_update_log.jsonl)
"""

import argparse
import json
import os
import time
from datetime import datetime
from typing import Dict, Any

import requests


FORBIDDEN_CHARS = ["%", "{", "}", " "]
NOTION_VERSION = "2022-06-28"


def build_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def fail_fast_on_forbidden(value: str) -> None:
    for ch in FORBIDDEN_CHARS:
        if ch in value:
            raise ValueError(f"Forbidden char '{ch}' in value: {value}")


def fetch_page(token: str, page_id: str) -> Dict[str, Any]:
    url = f"https://api.notion.com/v1/pages/{page_id}"
    resp = requests.get(url, headers=build_headers(token), timeout=15)
    resp.raise_for_status()
    return resp.json()


def assert_page_in_database(page_json: Dict[str, Any], expected_db_id: str) -> None:
    parent = page_json.get("parent") or {}
    db_id = parent.get("database_id")
    if not db_id or db_id.replace("-", "") != expected_db_id.replace("-", ""):
        raise AssertionError("Page does not belong to expected database")


def update_status(token: str, page_id: str, status_property_id: str, status_name: str) -> Dict[str, Any]:
    fail_fast_on_forbidden(status_property_id)
    payload = {
        "properties": {
            status_property_id: {"status": {"name": status_name}}
        }
    }
    url = f"https://api.notion.com/v1/pages/{page_id}"
    resp = requests.patch(url, headers=build_headers(token), data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), timeout=20)
    return {"status_code": resp.status_code, "text": resp.text[:2000]}


def append_log(record: Dict[str, Any]) -> None:
    path = os.path.join(os.getcwd(), "status_update_log.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update Notion status by property_id")
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--property-id", required=True)
    parser.add_argument("--status-name", required=True)
    args = parser.parse_args()

    token = os.getenv("NOTION_TOKEN", "").strip()
    expected_db = os.getenv("TARGET_DATABASE_ID", "").strip()
    if not token:
        raise SystemExit("NOTION_TOKEN is not set")
    if not expected_db:
        raise SystemExit("TARGET_DATABASE_ID is not set")

    trace_id = f"status_{int(time.time())}"
    now = datetime.utcnow().isoformat() + "Z"

    page = fetch_page(token, args.page_id)
    assert_page_in_database(page, expected_db)

    result = update_status(token, args.page_id, args.property_id, args.status_name)

    log_record = {
        "trace_id": trace_id,
        "ts": now,
        "page_id": args.page_id,
        "database_id": expected_db,
        "property_id": args.property_id,
        "status_name": args.status_name,
        "status_code": result.get("status_code"),
        "response_preview": result.get("text"),
    }
    append_log(log_record)

    ok = result.get("status_code") in (200, 201)
    print(json.dumps({"ok": ok, **log_record}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()



