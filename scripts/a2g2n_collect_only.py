# -*- coding: utf-8 -*-
"""
Collect top search results for a list of queries using the unified adapter.

Outputs simple markdown files into ./temp_drive/ as an offline stand-in for Drive.

Usage:
  set PYTHONPATH=.
  python scripts/a2g2n_collect_only.py --queries queries.txt --per-query 3
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import List

from src.utils.web_search_adapter import GoogleCSEAdapter, SearchResult


def _configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def read_queries(path: Path) -> List[str]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [q for q in lines if q]


def save_markdown(out_dir: Path, query: str, results: List[SearchResult]) -> Path:
    safe_name = "_".join(query.split())[:80]
    fp = out_dir / f"{safe_name}.md"
    lines = [f"# {query}", "", f"총 {len(results)}건"]
    for i, r in enumerate(results, 1):
        lines.append(f"\n## {i}. {r.title}\n{r.link}\n\n{r.snippet}")
    fp.write_text("\n".join(lines), encoding="utf-8")
    return fp


def main() -> int:
    _configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", required=True)
    parser.add_argument("--per-query", type=int, default=3)
    parser.add_argument("--out", default="temp_drive")
    args = parser.parse_args()

    queries = read_queries(Path(args.queries))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("collect")
    adapter = GoogleCSEAdapter()

    outputs: List[Path] = []
    for q in queries:
        logger.info("collecting: %s", q)
        try:
            rs = adapter.search(q, num=args.per_query)
        except Exception as exc:  # noqa: BLE001
            logger.error("query failed: %s", exc)
            continue
        fp = save_markdown(out_dir, q, rs)
        outputs.append(fp)
        logger.info("saved: %s", fp)

    print("\n=== outputs ===")
    for p in outputs:
        print(str(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


