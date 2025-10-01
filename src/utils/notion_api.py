import os
import json
import time
import logging
import hashlib
from typing import Dict, Any, Optional, List

import requests


NOTION_BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")


class NotionApiError(Exception):
    pass


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json; charset=utf-8",
    }


def get_database_schema(notion_token: str, database_id: str) -> Dict[str, Any]:
    resp = requests.get(
        f"{NOTION_BASE_URL}/databases/{database_id}", headers=_headers(notion_token), timeout=30
    )
    if resp.status_code != 200:
        raise NotionApiError(f"Databases Retrieve failed: {resp.status_code} {resp.text}")
    return resp.json()


def extract_status_property_id(schema: Dict[str, Any]) -> str:
    props = schema.get("properties", {})
    if "상태" not in props:
        raise NotionApiError("'상태' property not found in database schema")
    return props["상태"]["id"]


def get_page(notion_token: str, page_id: str) -> Dict[str, Any]:
    resp = requests.get(f"{NOTION_BASE_URL}/pages/{page_id}", headers=_headers(notion_token), timeout=30)
    if resp.status_code != 200:
        raise NotionApiError(f"Get Page failed: {resp.status_code} {resp.text}")
    return resp.json()


def validate_page_in_database(page_json: Dict[str, Any], target_database_id: str) -> bool:
    parent = page_json.get("parent", {})
    if parent.get("type") != "database_id":
        return False
    return parent.get("database_id") == target_database_id


def _validate_props_payload(props: Dict[str, Any]) -> None:
    # Key set/type schema checks and forbidden characters guard
    forbidden = {"%", "{", "}", " "}
    for key in props.keys():
        if any(ch in key for ch in forbidden):
            raise NotionApiError(f"Forbidden character in property id: {key}")

    # Type guards for commonly used property payloads
    for prop_id, value in props.items():
        if not isinstance(value, dict):
            raise NotionApiError(f"Property {prop_id} must be dict payload")
        # status
        if "status" in value:
            status_val = value["status"]
            if not (isinstance(status_val, dict) and "name" in status_val and isinstance(status_val["name"], str)):
                raise NotionApiError("status payload must be {'status': {'name': '<option>'}}")
        # date
        if "date" in value:
            date_val = value["date"]
            if not (isinstance(date_val, dict) and "start" in date_val and isinstance(date_val["start"], str)):
                raise NotionApiError("date payload must be {'date': {'start': 'YYYY-MM-DD'}}")
        # url
        if "url" in value:
            url_val = value["url"]
            if not isinstance(url_val, str):
                raise NotionApiError("url payload must be {'url': 'https://...'}")


def update_page_properties_by_id(
    notion_token: str,
    page_id: str,
    properties_by_id: Dict[str, Any],
    parent_database_id: Optional[str] = None,
) -> Dict[str, Any]:
    _validate_props_payload(properties_by_id)

    payload: Dict[str, Any] = {"properties": properties_by_id}
    if parent_database_id:
        payload["parent"] = {"database_id": parent_database_id}

    json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    resp = requests.patch(
        f"{NOTION_BASE_URL}/pages/{page_id}", headers=_headers(notion_token), data=json_bytes, timeout=30
    )
    if resp.status_code // 100 != 2:
        raise NotionApiError(f"Update Page failed: {resp.status_code} {resp.text}")
    return resp.json()


def set_status_by_property_id(
    notion_token: str,
    page_id: str,
    status_property_id: str,
    status_name: str,
    parent_database_id: Optional[str] = None,
) -> Dict[str, Any]:
    props = {status_property_id: {"status": {"name": status_name}}}
    return update_page_properties_by_id(notion_token, page_id, props, parent_database_id)


def check_health(url: str) -> Dict[str, Any]:
    ts = time.time()
    resp = requests.get(url, timeout=15)
    return {
        "status_code": resp.status_code,
        "ok": resp.status_code == 200,
        "timestamp": ts,
        "body": safe_json(resp),
    }


def safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return {"text": resp.text[:500]}


# 선과장님 스크립트에 따른 NotionClient 클래스 구현
class NotionClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json; charset=utf-8",
        }

    def _req(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{NOTION_BASE_URL}{path}"
        
        # UTF-8 바이트 인코딩 보장
        for k in ("json", "data"):
            if k in kwargs and isinstance(kwargs[k], str):
                kwargs[k] = kwargs[k].encode("utf-8")
        
        r = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)
        
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {r.status_code} {r.text[:400]}")
        
        return r.json()

    # 프로브 메서드들
    def users_me(self):
        return self._req("GET", "/users/me")

    def get_database(self, db_id: str):
        return self._req("GET", f"/databases/{db_id}")

    def query_database(self, db_id: str, payload: Optional[Dict] = None) -> Dict:
        return self._req("POST", f"/databases/{db_id}/query", json=payload or {})

    def get_page(self, page_id: str):
        return self._req("GET", f"/pages/{page_id}")

    def list_block_children(self, block_id: str, page_size=100, start_cursor=None):
        params = []
        if page_size:
            params.append(f"page_size={page_size}")
        if start_cursor:
            params.append(f"start_cursor={start_cursor}")
        
        qs = ("?" + "&".join(params)) if params else ""
        return self._req("GET", f"/blocks/{block_id}/children{qs}")


# 스키마 해시 생성 함수
def build_schema_hash(db_json: Dict) -> str:
    props = db_json.get("properties", {})
    sig = {k: {"id": v.get("id"), "type": v.get("type")} for k, v in props.items()}
    raw = json.dumps(sig, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


