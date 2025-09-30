import os
import json
import time
import logging
from typing import Dict, Any, Optional

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


