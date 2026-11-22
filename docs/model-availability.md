# Model availability preflight

There are three distinct failures that are often all reported as 404:

- A group `model_allowlist` rejects the requested name before account dispatch.
- A non empty account `credentials.model_mapping` does not contain the requested name (or a
  matching wildcard), so no account in the pinned group supports it.
- The request reaches the upstream OpenAI service and that service rejects the model.

The first two are platform routing/configuration results. Inspect them before counting an account
as model unavailable. `POST /api/v1/admin/accounts/bulk-update` merges the top level credentials
key and is the safe temporary mapping operation. Since the nested mapping is replaced as one key,
send the complete original mapping plus the identity entry, then restore the complete original
mapping. Avoid a partial `PUT /admin/accounts/:id` credentials update.

If a production group allowlist blocks the probe, use a temporary group with
`model_allowlist.enabled=true` and a non empty `models` list. Save and restore original account
group IDs. Do not change a production allowlist merely to make a scan pass.

Record the exact error text and layer in JSONL. `Model "..." is not supported by any configured
account in this group` is a routing/platform result; it is not evidence of Astra to Luna behavior.
