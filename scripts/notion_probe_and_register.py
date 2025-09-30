# -*- coding: utf-8 -*-
"""
Probe Notion token validity and DB permission, then register pages from temp_drive.

Usage:
  set PYTHONPATH=.
  python scripts/notion_probe_and_register.py --folder temp_drive
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import requests


def probe(token: str, dbid: str) -> tuple[int, int]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": os.getenv("NOTION_VERSION", "2022-06-28"),
    }
    s1 = s2 = 0
    try:
        r1 = requests.get("https://api.notion.com/v1/users/me", headers=headers, timeout=15)
        s1 = r1.status_code
    except Exception:
        s1 = -1
    try:
        r2 = requests.get(f"https://api.notion.com/v1/databases/{dbid}", headers=headers, timeout=15)
        s2 = r2.status_code
    except Exception:
        s2 = -1
    return s1, s2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="temp_drive")
    args = parser.parse_args()

    token = os.getenv("NOTION_TOKEN", "").strip()
    dbid = os.getenv("TARGET_DATABASE_ID", "").strip()
    if not token or not dbid:
        print("NOTION_TOKEN or TARGET_DATABASE_ID missing")
        return 2

    s1, s2 = probe(token, dbid)
    print(f"probe users/me={s1} db={s2}")

    if s1 == 200 and s2 == 200:
        # Run the registrar
        env = os.environ.copy()
        cmd = [sys.executable, "scripts/a2g2n_register_from_temp.py", "--folder", args.folder]
        proc = subprocess.run(cmd, env=env)
        return proc.returncode
    else:
        print("Probe failed. Fix token or DB permissions and retry.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


