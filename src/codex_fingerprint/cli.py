"""Safe CLI plan mode; deployment-specific binding and detector code stays in an adapter."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accounts-file", type=Path, required=True,
                        help="JSON list or {accounts: [...]} with account_id and proxy_id")
    parser.add_argument("--requested-model", default="gpt-6.2-astra")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--max-per-proxy", type=int, default=1)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args(argv)
    document = json.loads(args.accounts_file.read_text(encoding="utf-8"))
    accounts = document.get("accounts", document) if isinstance(document, dict) else document
    if not isinstance(accounts, list):
        parser.error("accounts file must contain a JSON list or an accounts list")
    clean = []
    for item in accounts:
        if not isinstance(item, dict) or not item.get("account_id"):
            parser.error("each account must contain account_id")
        clean.append({"account_id": int(item["account_id"]), "proxy_id": item.get("proxy_id")})
    if not args.plan_only:
        parser.error("no adapter configured; use FastScanner with a Sub2API probe adapter")
    print(json.dumps({"requested_model": args.requested_model, "accounts": len(clean),
                      "workers": args.workers, "max_per_proxy": args.max_per_proxy},
                     separators=(",", ":")))
    return 0
