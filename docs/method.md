# Fast method

1. Read the account inventory from the management API and keep only non free, active,
   schedulable accounts without an error and with a non exhausted weekly quota.
2. Preflight the account mapping and group allowlist for the requested model. Resolve platform
   admission before labeling a model unavailable.
3. Pin one account at a time with a temporary user, key and group. The group allows only the
   requested model. Always save original groups and restore them in `finally`.
4. Send one fixed lm-detector challenge through the normal Responses endpoint. Let the server
   route it through that account's native `proxy_id` egress.
5. Classify behavior first. Keep `model_unavailable`, `rate_limited`, upstream 5xx and sample
   timeout separate from a behavior mismatch.
6. Delete the temporary key, user and group, then verify there are no `tmp-fast-lmfp-*` objects.

The single challenge is a fast ranking screen, not a calibrated identity proof. Candidate Luna
or Sol results can be re-run with three independent challenges when the operating policy requires
higher confidence.
