"""
Unified web search adapter interfaces and implementations.

Supports Google Custom Search (CSE) out of the box and provides
placeholders for SerpAPI and Bing adapters sharing the same interface.

Environment variables (Google CSE):
- CSE_API_KEY or GOOGLE_CUSTOM_SEARCH_API_KEY
- CSE_CX or GOOGLE_SEARCH_ENGINE_ID

Operational requirements:
- Retries with exponential backoff (3 attempts)
- Timeout 8 seconds per HTTP request
- Mask API keys in logs
"""

from __future__ import annotations

import os
import time
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import requests


_LOGGER = logging.getLogger(__name__)


def _mask_secret(value: Optional[str]) -> str:
    if not value:
        return ""
    if len(value) <= 6:
        return "***"
    return f"{value[:4]}***{value[-2:]}"


@dataclass
class SearchResult:
    link: str
    title: str
    snippet: str


class SearchAdapter:
    def search(self, query: str, num: int = 10) -> List[SearchResult]:
        raise NotImplementedError


class GoogleCSEAdapter(SearchAdapter):
    def __init__(self, api_key: Optional[str] = None, cx: Optional[str] = None, timeout_seconds: float = 8.0):
        # Read envs and strip whitespace to avoid trailing spaces turning into '+' in requests
        env_key = os.getenv("CSE_API_KEY") or os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
        env_cx = os.getenv("CSE_CX") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.api_key = (api_key if api_key is not None else env_key or "").strip()
        self.cx = (cx if cx is not None else env_cx or "").strip()
        self.timeout_seconds = timeout_seconds

        if not self.api_key or not self.cx:
            raise ValueError(
                "Google CSE credentials are not set. Expect CSE_API_KEY/GOOGLE_CUSTOM_SEARCH_API_KEY and CSE_CX/GOOGLE_SEARCH_ENGINE_ID."
            )

    def search(self, query: str, num: int = 10) -> List[SearchResult]:
        endpoint = "https://www.googleapis.com/customsearch/v1"
        # Google CSE returns up to 10 per request; clamp
        per_request = max(1, min(num, 10))

        params: Dict[str, Any] = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": per_request,
        }

        backoff_seconds = [1, 2, 4]  # 3 attempts total
        last_exc: Optional[Exception] = None

        for attempt_index, delay in enumerate(backoff_seconds, start=1):
            try:
                response = requests.get(endpoint, params=params, timeout=self.timeout_seconds)
                status = response.status_code
                if status == 200:
                    payload = response.json()
                    items = payload.get("items", []) or []
                    results: List[SearchResult] = []
                    for item in items:
                        results.append(
                            SearchResult(
                                link=item.get("link", ""),
                                title=item.get("title", ""),
                                snippet=item.get("snippet", ""),
                            )
                        )
                    return results

                if status in (403, 429):
                    _LOGGER.warning(
                        "Google CSE request blocked (status=%s). key=%s cx=%s attempt=%s",
                        status,
                        _mask_secret(self.api_key),
                        self.cx,
                        attempt_index,
                    )
                else:
                    _LOGGER.error(
                        "Google CSE unexpected status=%s. body=%s attempt=%s",
                        status,
                        _safe_truncate(response.text),
                        attempt_index,
                    )
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                _LOGGER.error(
                    "Google CSE request error: %s (attempt=%s, key=%s, cx=%s)",
                    exc,
                    attempt_index,
                    _mask_secret(self.api_key),
                    self.cx,
                )

            if attempt_index < len(backoff_seconds):
                time.sleep(delay)

        if last_exc:
            raise last_exc
        raise RuntimeError("Google CSE failed after retries")


def _safe_truncate(text: Optional[str], limit: int = 500) -> str:
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "...<truncated>"


class SerpAPIAdapter(SearchAdapter):
    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 8.0):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, num: int = 10) -> List[SearchResult]:  # pragma: no cover - placeholder
        raise NotImplementedError("SerpAPIAdapter not yet implemented")


class BingAdapter(SearchAdapter):
    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None, timeout_seconds: float = 8.0):
        self.api_key = api_key or os.getenv("BING_KEY") or os.getenv("AZURE_BING_KEY")
        self.endpoint = endpoint or os.getenv("BING_ENDPOINT") or os.getenv("AZURE_BING_ENDPOINT")
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, num: int = 10) -> List[SearchResult]:  # pragma: no cover - placeholder
        raise NotImplementedError("BingAdapter not yet implemented")


