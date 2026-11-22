"""Minimal Sub2API admin/public client with one shared management limiter."""
from __future__ import annotations

import time
from typing import Any

import requests

from .limiter import GlobalStartLimiter


class Sub2ApiClient:
    """HTTP client whose base URL and admin key come from the caller's secret store."""

    def __init__(self, base_url: str, admin_key: str, *, min_interval: float = 0.5,
                 max_admin_in_flight: int = 4, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._admin_key = admin_key
        self.timeout = timeout
        self._limiter = GlobalStartLimiter(min_interval, max_admin_in_flight)
        self.session = requests.Session()

    def _request(self, method: str, path: str, *, public: bool = False,
                 retries: int = 3, timeout: float | None = None, **kwargs: Any) -> requests.Response:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if not public:
            headers["x-api-key"] = self._admin_key
        headers.update(kwargs.pop("headers", {}))
        last: requests.Response | None = None
        for attempt in range(retries + 1):
            with self._limiter.request_slot():
                last = self.session.request(method, self.base_url + path, headers=headers,
                                            timeout=timeout or self.timeout, **kwargs)
            if last.status_code != 429 or attempt == retries:
                return last
            retry_after = last.headers.get("Retry-After", "")
            try:
                delay = max(0.25, min(8.0, float(retry_after)))
            except ValueError:
                delay = min(8.0, 2 ** attempt)
            time.sleep(delay)
        assert last is not None
        return last

    @staticmethod
    def body(response: requests.Response) -> Any:
        response.raise_for_status()
        value = response.json()
        return value.get("data", value) if isinstance(value, dict) else value

    def admin(self, method: str, path: str, **kwargs: Any) -> Any:
        return self.body(self._request(method, path, **kwargs))

    def public(self, method: str, path: str, **kwargs: Any) -> Any:
        return self.body(self._request(method, path, public=True, **kwargs))
