"""Small concurrency primitives used by the fast screening path."""
from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from typing import Iterator


class GlobalStartLimiter:
    """Limit starts against one shared management endpoint."""

    def __init__(self, min_interval: float = 0.5, max_in_flight: int = 4) -> None:
        if min_interval < 0 or max_in_flight < 1:
            raise ValueError("min_interval must be non-negative and max_in_flight positive")
        self.min_interval = float(min_interval)
        self._next_start = 0.0
        self._rate_lock = threading.Lock()
        self._slots = threading.BoundedSemaphore(max_in_flight)

    @contextmanager
    def request_slot(self) -> Iterator[None]:
        with self._slots:
            with self._rate_lock:
                now = time.monotonic()
                start = max(now, self._next_start)
                self._next_start = start + self.min_interval
            if start > now:
                time.sleep(start - now)
            yield


class ProxySlots:
    """One semaphore per server-returned account proxy_id."""

    def __init__(self, per_proxy: int = 1) -> None:
        if per_proxy < 1:
            raise ValueError("per_proxy must be positive")
        self.per_proxy = per_proxy
        self._lock = threading.Lock()
        self._semaphores: dict[str, threading.BoundedSemaphore] = {}

    def _get(self, proxy_id: object) -> threading.BoundedSemaphore:
        key = "<none>" if proxy_id is None else str(proxy_id)
        with self._lock:
            return self._semaphores.setdefault(key, threading.BoundedSemaphore(self.per_proxy))

    @contextmanager
    def slot(self, proxy_id: object) -> Iterator[None]:
        with self._get(proxy_id):
            yield
