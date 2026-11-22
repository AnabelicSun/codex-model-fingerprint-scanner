"""Parallel orchestration independent of the detector implementation."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable

from .limiter import ProxySlots

Probe = Callable[[dict], dict]


class FastScanner:
    """Run one short probe per account with native proxy_id slots."""

    def __init__(self, workers: int = 16, max_per_proxy: int = 1) -> None:
        if workers < 1:
            raise ValueError("workers must be positive")
        self.workers = workers
        self.proxy_slots = ProxySlots(max_per_proxy)

    def run(self, accounts: Iterable[dict], probe: Probe) -> list[dict]:
        def wrapped(account: dict) -> dict:
            with self.proxy_slots.slot(account.get("proxy_id")):
                return probe(account)

        results: list[dict] = []
        with ThreadPoolExecutor(max_workers=self.workers, thread_name_prefix="fingerprint") as pool:
            futures = [pool.submit(wrapped, account) for account in accounts]
            for future in as_completed(futures):
                results.append(future.result())
        return results
