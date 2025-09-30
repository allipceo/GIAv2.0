# -*- coding: utf-8 -*-
"""
Smoke test for Google Custom Search API via unified adapter.

Usage (PowerShell):
  $env:CSE_API_KEY="<key>"; $env:CSE_CX="<cx>"; python scripts/smoke_cse_test.py

Expectation:
- HTTP 200 from Google CSE
- items[].link length >= 1

If 403 occurs, loosen restrictions or reissue keys. If 429, switch project/quota.
"""

from __future__ import annotations

import logging
import os
import sys

from src.utils.web_search_adapter import GoogleCSEAdapter


def _configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def main() -> int:
    _configure_logging()
    logger = logging.getLogger("smoke_cse")

    query = "서남해해상풍력발전사업"
    logger.info("Running CSE smoke test. query=%s", query)

    try:
        adapter = GoogleCSEAdapter()
    except Exception as exc:  # noqa: BLE001
        logger.error("CSE adapter init failed: %s", exc)
        return 2

    try:
        results = adapter.search(query=query, num=5)
    except Exception as exc:  # noqa: BLE001
        logger.error("CSE search failed: %s", exc)
        return 3

    links = [r.link for r in results if r.link]
    if not links:
        logger.error("Smoke failed: no links returned")
        return 4

    logger.info("Smoke success: %d links. First=%s", len(links), links[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())


