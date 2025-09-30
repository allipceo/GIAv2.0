# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import json
import requests


def main() -> int:
    token = os.getenv("NOTION_TOKEN", "").strip()
    dbid = os.getenv("TARGET_DATABASE_ID", "").strip()
    if not token or not dbid:
        print("missing envs")
        return 2
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": os.getenv("NOTION_VERSION", "2022-06-28"),
    }
    r = requests.get(f"https://api.notion.com/v1/databases/{dbid}", headers=headers, timeout=20)
    print(r.status_code)
    js = r.json()
    props = js.get("properties", {})
    out = []
    for name, meta in props.items():
        out.append({"name": name, "id": meta.get("id"), "type": meta.get("type")})
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


