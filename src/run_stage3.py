import os
import json
from pathlib import Path
from typing import List

# Robust dotenv loading: .env, .env.local, config.env (project root)
def _load_env_files():
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    base = Path(__file__).resolve().parent.parent  # project root (parent of src)
    for fname in [".env", ".env.local", "config.env"]:
        p = base / fname
        if p.exists():
            try:
                load_dotenv(dotenv_path=str(p), encoding="utf-8", override=False)
            except Exception:
                pass

    # Fallback parser for simple KEY=VALUE lines
    cfg = base / "config.env"
    if cfg.exists():
        try:
            for line in cfg.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)
        except Exception:
            pass

_load_env_files()

from branch_manager import (
    step_health_check,
    step_fetch_status_property_id,
    run_g1_regression,
    run_g2_batch,
)


def _print(title: str, payload):
    print(f"\n=== {title} ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def maybe_split_env_list(name: str) -> List[str]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def main():
    # 1) health check
    health = step_health_check()
    _print("health_check", health)

    # 2) status property id
    status_prop_id = step_fetch_status_property_id()
    _print("status_property_id", {"STATUS_PROPERTY_ID": status_prop_id})

    # 3) G1 regression
    g1_logs = run_g1_regression(status_prop_id)
    _print("g1_regression", {"count": len(g1_logs), "logs": g1_logs})

    # 4) G2 batch (optional via env G2_PAGE_IDS)
    page_ids = maybe_split_env_list("G2_PAGE_IDS")
    if page_ids:
        report = run_g2_batch(status_prop_id, page_ids, status_name=os.getenv("G2_STATUS", "검토중"), concurrency=int(os.getenv("G2_CONCURRENCY", "3")))
        _print("g2_batch_report", report)
    else:
        _print("g2_batch_report", {"skipped": True, "reason": "G2_PAGE_IDS not provided"})


if __name__ == "__main__":
    main()


