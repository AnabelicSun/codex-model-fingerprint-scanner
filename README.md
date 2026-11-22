# Codex model fingerprint scanner

Fast account level screening for silent model family downgrade through a Sub2API gateway. The
primary question is whether an account requested as `gpt-6.2-astra` behaves like
`gpt-5.6-luna`; changes in reasoning effort such as `max` to `xhigh` are outside this project.

The scanner uses one deterministic lm-detector challenge per account for a quick first pass.
The response `model` field is supporting evidence only. A behavior prediction from the challenge
is required before labeling a model mismatch. Use a later multi challenge run when a candidate
needs confirmation.

Before calling a model unavailable, inspect the platform layers. A 404 can be caused by the
account's non empty `credentials.model_mapping` or by a group `model_allowlist`. For a temporary
experiment, save the complete mapping, use

```json
{"account_ids":[123],"credentials":{"model_mapping":{"...":"...","gpt-6.2-astra":"gpt-6.2-astra"}}}
```

with `POST /api/v1/admin/accounts/bulk-update`, run the probe, then write back the exact saved
mapping and verify it with GET. Do not use a partial credentials `PUT`; it can remove non sensitive
metadata such as expiry and plan fields. Only a 404 that remains after the platform mapping and
group admission are valid counts as an upstream model unavailable result.

Model requests must be pinned by the service to the account's own server returned `proxy_id`.
The orchestration layer gives every proxy its own concurrency slot, while all management API
requests share one global start limiter and bounded retry. The management surface uses the fixed
gateway entry point; it is not an account egress test.

The library is deliberately adapter based: deployment code supplies the temporary user/key/group
lifecycle and the lm-detector sampler, while `FastScanner`, `Sub2ApiClient`, `ProxySlots`, and
`classify_sample` provide the reusable safety and classification pieces. `--plan-only` validates a
scrubbed inventory without mutating a service.

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .
codex-fingerprint-scan --accounts-file inventory.json --plan-only \
  --requested-model gpt-6.2-astra --workers 16 --max-per-proxy 1
```

Keep admin keys, OAuth credentials, account inventories, challenge text, raw responses and scan
results outside Git. The `.gitignore` is intentionally broad; use a protected result store for
operational output.

See [the method](docs/method.md), [model availability](docs/model-availability.md), and
[routing and limits](docs/routing-and-limits.md).
