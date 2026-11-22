# Routing and limits

Management requests go to one fixed Sub2API base URL and use a single global limiter. The default
is four in flight and 0.5 seconds between starts, with bounded 429 backoff. Running multiple
scanner processes defeats that limiter.

Model requests are different: the service pins the temporary key to one account and selects the
account's stored `proxy_id`. The scanner keeps one semaphore per proxy so unrelated Osaka exits
can proceed in parallel while a shared exit is protected. There is no fallback to a fixed proxy;
the result must describe the account's own egress.

Separate management 429, model 429, model 404, upstream 5xx and detector timeout in reports. A
429 caused by an account or gateway is not a model family result.
