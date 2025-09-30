#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G2N 수신 웹훅 /health 점검 스크립트

환경변수:
- G2N_HEALTH_URL: 예) https://<your-tunnel-or-endpoint>/health

출력:
- 콘솔 로그와 JSON 결과 파일(health_check_result.json)
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any

import requests


FORBIDDEN_CHARS = ["%", "{", "}", " "]


def run_health_check() -> Dict[str, Any]:
    health_url = os.getenv("G2N_HEALTH_URL", "").strip()
    result: Dict[str, Any] = {
        "trace_id": f"health_{int(time.time())}",
        "checked_at": datetime.utcnow().isoformat() + "Z",
        "health_url": health_url,
        "status_code": None,
        "ok": False,
        "error": None,
    }

    if not health_url:
        result["error"] = "G2N_HEALTH_URL is not set"
        return result

    try:
        resp = requests.get(health_url, timeout=10)
        result["status_code"] = resp.status_code
        result["ok"] = resp.status_code == 200
        if not result["ok"]:
            result["error"] = resp.text[:500]
    except Exception as e:
        result["error"] = str(e)

    return result


def save_result(result: Dict[str, Any]) -> str:
    out_path = os.path.join(os.getcwd(), "health_check_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return out_path


def main() -> None:
    print("🚑 /health 점검 시작")
    result = run_health_check()
    out = save_result(result)
    status = "OK" if result.get("ok") else "FAIL"
    print(f"결과: {status}, status_code={result.get('status_code')}, file={out}")


if __name__ == "__main__":
    main()



