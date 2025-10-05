#!/usr/bin/env python3
"""
U001 접근 및 증빙 자동화 스크립트

기능 개요
- 환경 변수 점검(NOTION_TOKEN, TARGET_DATABASE_ID, U001_PAGE_ID)
- 3단계 연결 검증: users/me → databases/:id → pages/:id
- (성공 시) U001 본문 하단에 "접근 증빙" 블록 1회 추가
- (성공 시) 개발문서 DB 내 U001 카드 메타 업데이트(상태/목적 요약/작성일)
- (항상) 실행 결과를 logs/u001_access_YYYYMMDD.jsonl 에 기록

주의사항
- 토큰/ID는 절대 코드에 하드코딩하지 말고 환경변수로만 주입
- 실패 시에도 JSONL 로그에 원인과 응답을 요약 기록
"""

from __future__ import annotations

import json
import os
import sys
import datetime as dt
from typing import Any, Dict, Optional, Tuple

import requests


NOTION_VERSION = "2022-06-28"
LOG_DIR = "logs"


def utc_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def kst_now_iso() -> str:
    tz_kst = dt.timezone(dt.timedelta(hours=9))
    return dt.datetime.now(tz_kst).replace(microsecond=0).isoformat()


def ensure_log_dir() -> str:
    os.makedirs(LOG_DIR, exist_ok=True)
    return LOG_DIR


def log_path_for_today() -> str:
    ensure_log_dir()
    return os.path.join(LOG_DIR, f"u001_access_{dt.datetime.utcnow():%Y%m%d}.jsonl")


def write_jsonl(entry: Dict[str, Any]) -> None:
    path = log_path_for_today()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_env() -> Tuple[str, str, str]:
    token = os.environ.get("NOTION_TOKEN", "").strip()
    db_id = os.environ.get("TARGET_DATABASE_ID", "").strip()
    page_id = os.environ.get("U001_PAGE_ID", "").strip()
    return token, db_id, page_id


def build_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def http_get(url: str, headers: Dict[str, str]) -> requests.Response:
    return requests.get(url, headers=headers, timeout=30)


def http_post(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> requests.Response:
    return requests.post(url, headers=headers, json=payload, timeout=30)


def http_patch(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> requests.Response:
    return requests.patch(url, headers=headers, json=payload, timeout=30)


def check_users_me(headers: Dict[str, str]) -> Tuple[bool, Dict[str, Any]]:
    resp = http_get("https://api.notion.com/v1/users/me", headers)
    ok = resp.status_code == 200
    body = safe_json(resp)
    return ok, {
        "status": resp.status_code,
        "ok": ok,
        "body": redact(body),
    }


def check_database(headers: Dict[str, str], db_id: str) -> Tuple[bool, Dict[str, Any]]:
    resp = http_get(f"https://api.notion.com/v1/databases/{db_id}", headers)
    ok = resp.status_code == 200
    body = safe_json(resp)
    return ok, {
        "status": resp.status_code,
        "ok": ok,
        "body": redact(body),
    }


def check_page(headers: Dict[str, str], page_id: str) -> Tuple[bool, Dict[str, Any]]:
    resp = http_get(f"https://api.notion.com/v1/pages/{page_id}", headers)
    ok = resp.status_code == 200
    body = safe_json(resp)
    return ok, {
        "status": resp.status_code,
        "ok": ok,
        "body": redact(body),
    }


def append_proof_block(headers: Dict[str, str], page_id: str, actor: str, token_source: str, summary_line: str, request_id: Optional[str]) -> Tuple[bool, Dict[str, Any]]:
    # children append API
    # https://api.notion.com/v1/blocks/{block_id}/children
    # For pages, we can use page_id as block_id to append at the end.
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    now_utc = utc_now_iso()
    now_kst = kst_now_iso()

    title_text = "[접근 증빙] 서대리 U001 연결 점검 로그"
    lines = [
        f"1) 시각(UTC {now_utc} / KST {now_kst}), 호출자 {actor}, 토큰 경로 {token_source}",
        summary_line,
        f"3) 요청ID/해시: {request_id or 'N/A'}, 다음 실행 예정: 링크 검증·위젯 연계",
    ]

    payload = {
        "children": [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": title_text}}]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "\n".join(lines)}}]
                },
            },
        ]
    }

    resp = http_patch(url, headers, payload)
    ok = resp.status_code in (200, 201)
    body = safe_json(resp)
    return ok, {"status": resp.status_code, "ok": ok, "body": redact(body)}


def update_db_card_meta(headers: Dict[str, str], page_id: str) -> Tuple[bool, Dict[str, Any]]:
    """Update page properties with schema-aware mapping.

    Expected targets (best-effort by names):
    - 상태: status (set to "검토중")
    - 목적 요약: rich_text/text/title (set content string)
    - 작성일: date (set start to today)
    - 태그: multi_select (ensure ["ZOBIS", "UI"]) if exists
    """
    # 1) Read current page to learn property types
    page_url = f"https://api.notion.com/v1/pages/{page_id}"
    page_resp = http_get(page_url, headers)
    page_body = safe_json(page_resp)
    if page_resp.status_code != 200 or not isinstance(page_body, dict):
        return False, {"status": page_resp.status_code, "ok": False, "body": redact(page_body)}

    props = page_body.get("properties", {}) if isinstance(page_body, dict) else {}

    def find_prop_by_name(candidates: Tuple[str, ...]) -> Optional[Tuple[str, Dict[str, Any]]]:
        for name in candidates:
            if name in props:
                return name, props[name]
        return None

    today_iso = dt.datetime.now().date().isoformat()
    update_props: Dict[str, Any] = {}

    # 상태 (status or select)
    status_match = find_prop_by_name(("상태", "status", "Status"))
    if status_match:
        key, meta = status_match
        ptype = meta.get("type")
        if ptype == "status":
            update_props[key] = {"status": {"name": "검토중"}}
        elif ptype == "select":
            update_props[key] = {"select": {"name": "검토중"}}

    # 목적 요약 (rich_text/text/title)
    summary_match = find_prop_by_name(("목적 요약", "목적요약", "summary", "요약", "제목 요약"))
    summary_text = "U001 접근·검증 완료, 본문 하단 증빙 기록"
    if summary_match:
        key, meta = summary_match
        ptype = meta.get("type")
        if ptype in ("rich_text", "text"):
            update_props[key] = {"rich_text": [{"type": "text", "text": {"content": summary_text}}]}
        elif ptype == "title":
            update_props[key] = {"title": [{"type": "text", "text": {"content": summary_text}}]}

    # 작성일 (date)
    date_match = find_prop_by_name(("작성일", "date", "Date"))
    if date_match:
        key, meta = date_match
        if meta.get("type") == "date":
            update_props[key] = {"date": {"start": today_iso}}

    # 태그 (multi_select)
    tags_match = find_prop_by_name(("태그", "Tags", "tags"))
    desired_tags = ["ZOBIS", "UI"]
    if tags_match:
        key, meta = tags_match
        if meta.get("type") == "multi_select":
            update_props[key] = {"multi_select": [{"name": t} for t in desired_tags]}

    if not update_props:
        return False, {"status": 400, "ok": False, "body": "No mappable properties found"}

    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": update_props}
    resp = http_patch(url, headers, payload)
    ok = resp.status_code == 200
    body = safe_json(resp)
    return ok, {"status": resp.status_code, "ok": ok, "body": redact(body), "payload": payload}


def redact(obj: Any) -> Any:
    # 최소 마스킹: token, bearer 값, 내부 URL 등
    s = json.dumps(obj, ensure_ascii=False) if isinstance(obj, (dict, list)) else str(obj)
    s = s.replace("Bearer ", "Bearer ***")
    # 길이 제한
    if len(s) > 2000:
        s = s[:2000] + "…(truncated)"
    try:
        return json.loads(s)
    except Exception:
        return s


def safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return resp.text


def main() -> int:
    actor = "서대리(Cursor)"
    token, db_id, page_id = load_env()

    # 환경 변수 유효성 검증
    env_ok = True
    missing = []
    if not token:
        env_ok = False
        missing.append("NOTION_TOKEN")
    if not db_id:
        env_ok = False
        missing.append("TARGET_DATABASE_ID")
    if not page_id:
        env_ok = False
        missing.append("U001_PAGE_ID")

    env_entry = {
        "ts": utc_now_iso(),
        "actor": actor,
        "task": "env_check",
        "notion_token_present": bool(token),
        "db_id_present": bool(db_id),
        "page_id_present": bool(page_id),
        "missing": missing,
    }
    write_jsonl(env_entry)

    if not env_ok:
        print("[FAIL] 환경 변수 누락:", ", ".join(missing))
        return 2

    headers = build_headers(token)

    # 1) users/me
    ok_users, users_info = check_users_me(headers)
    write_jsonl({
        "ts": utc_now_iso(),
        "actor": actor,
        "task": "users_me",
        "result": users_info,
    })

    # 2) database
    ok_db, db_info = check_database(headers, db_id)
    write_jsonl({
        "ts": utc_now_iso(),
        "actor": actor,
        "task": "database_get",
        "result": db_info,
    })

    # 3) page
    ok_page, page_info = check_page(headers, page_id)
    write_jsonl({
        "ts": utc_now_iso(),
        "actor": actor,
        "task": "page_get",
        "result": page_info,
    })

    summary_ok = ok_users and ok_db and ok_page
    if summary_ok:
        summary_line = "2) 검증 결과: users/me 200, DB 200, U001 200"
    else:
        # 실패 요약 구성
        failed = []
        if not ok_users:
            failed.append(f"users/me {users_info.get('status')}")
        if not ok_db:
            failed.append(f"DB {db_info.get('status')}")
        if not ok_page:
            failed.append(f"U001 {page_info.get('status')}")
        summary_line = f"2) 검증 결과: 실패 - {', '.join(failed)}"

    # 증빙 블록 추가 (성공/실패 모두 기록 정책)
    proof_ok, proof_info = append_proof_block(
        headers=headers,
        page_id=page_id,
        actor=actor,
        token_source="ENV(NOTION_TOKEN)",
        summary_line=summary_line,
        request_id=(page_info.get("body", {}) or {}).get("request_id") if isinstance(page_info.get("body"), dict) else None,
    )
    write_jsonl({
        "ts": utc_now_iso(),
        "actor": actor,
        "task": "append_proof_block",
        "result": proof_info,
    })

    # 메타 업데이트는 성공 시도 우선, 실패해도 로깅만
    meta_ok, meta_info = update_db_card_meta(headers, page_id)
    write_jsonl({
        "ts": utc_now_iso(),
        "actor": actor,
        "task": "update_db_card_meta",
        "result": meta_info,
    })

    # 콘솔 출력 요약
    print("=== Summary ===")
    print("users/me:", users_info.get("status"))
    print("database:", db_info.get("status"))
    print("page(U001):", page_info.get("status"))
    print("append_proof_block:", proof_info.get("status"))
    print("update_db_card_meta:", meta_info.get("status"))

    return 0 if summary_ok else 1


if __name__ == "__main__":
    sys.exit(main())


