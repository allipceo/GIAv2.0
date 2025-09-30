#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stage 3 G1 단건 회귀 테스트 스크립트 (Z062 대상)

환경변수:
- NOTION_TOKEN
- TARGET_DATABASE_ID (ZOBIS 개발문서 DB)
- Z062_PAGE_ID (테스트 페이지)
- STATUS_PROPERTY_ID (예: :Vmr)

시나리오:
1) 작성중 -> 검토중
2) 검토중 -> 작성중

각 단계마다 2xx 확인 및 구조화 로그를 JSONL로 저장(g1_regression_log.jsonl)
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any

from notion_status_update import fetch_page, assert_page_in_database, update_status, build_headers


def append_log(record: Dict[str, Any]) -> None:
    path = os.path.join(os.getcwd(), "g1_regression_log.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    token = os.getenv("NOTION_TOKEN", "").strip()
    db_id = os.getenv("TARGET_DATABASE_ID", "").strip()
    page_id = os.getenv("Z062_PAGE_ID", "").strip()
    prop_id = os.getenv("STATUS_PROPERTY_ID", "").strip()

    if not all([token, db_id, page_id, prop_id]):
        raise SystemExit("Missing env: NOTION_TOKEN, TARGET_DATABASE_ID, Z062_PAGE_ID, STATUS_PROPERTY_ID")

    trace_prefix = f"g1_{int(time.time())}"
    now = datetime.utcnow().isoformat() + "Z"

    # 사전 검증: 페이지가 대상 DB 소속인지 확인
    page = fetch_page(token, page_id)
    assert_page_in_database(page, db_id)

    # 1) 작성중 -> 검토중
    r1 = update_status(token, page_id, prop_id, "검토중")
    step1_ok = r1.get("status_code") in (200, 201)
    append_log({
        "trace_id": f"{trace_prefix}_1",
        "ts": now,
        "page_id": page_id,
        "database_id": db_id,
        "property_id": prop_id,
        "status_name": "검토중",
        "status_code": r1.get("status_code"),
        "response_preview": r1.get("text"),
    })

    # 2) 검토중 -> 작성중
    r2 = update_status(token, page_id, prop_id, "작성중")
    step2_ok = r2.get("status_code") in (200, 201)
    append_log({
        "trace_id": f"{trace_prefix}_2",
        "ts": now,
        "page_id": page_id,
        "database_id": db_id,
        "property_id": prop_id,
        "status_name": "작성중",
        "status_code": r2.get("status_code"),
        "response_preview": r2.get("text"),
    })

    ok = bool(step1_ok and step2_ok)
    print(json.dumps({
        "ok": ok,
        "trace_prefix": trace_prefix,
        "step1_ok": step1_ok,
        "step2_ok": step2_ok,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()



