"""Mock data for the incident scenario.

Everything is pinned to a fixed reference time (``INCIDENT_NOW``) so the workshop
is fully reproducible and does not depend on the real wall clock.

The scenario is "culprit among red herrings":
  * ``checkout`` starts throwing 500s at 14:32 — upstream timeouts to ``payments-service``.
  * Three services deployed in the last ~90 min; only ``payments-service v2.3.1``
    (14:30, two minutes before the spike) lines up.
  * That deploy shipped commit ``a1b2c3`` — "lower max idle conns" — which explains
    the "connection pool exhausted" errors in the log.
  * The other deploys/commits are decoys: wrong service, wrong time, unrelated change.
"""

# Reference "current time" for the incident. All `since_minutes` filters are
# measured backwards from this instant, not from real time.
INCIDENT_NOW = "2026-07-02T14:40:00Z"

# Recent deployments, newest first. status is informational only.
#
# Only three entries actually matter for the investigation; the rest are noise
# from a busy prod afternoon. The culprit is the payments-service v2.3.1 deploy
# at 14:30 (two minutes before the checkout spike). Note the red herrings that
# deploy right around 14:29-14:31 — recommendations, inventory-service,
# feature-flags — none of which are on checkout's blast radius.
DEPLOYMENTS = [
    {
        "timestamp": "2026-07-02T14:38:22Z",
        "service": "cdn-edge",
        "version": "v2.0.9",
        "commit": "e1a7c2",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:36:03Z",
        "service": "analytics-ingest",
        "version": "v1.4.0",
        "commit": "b3f9d0",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:33:41Z",
        "service": "notifications-service",
        "version": "v3.0.2",
        "commit": "4c8e11",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:31:47Z",
        "service": "recommendations",
        "version": "v3.2.0",
        "commit": "7a2f9b",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:30:12Z",
        "service": "payments-service",
        "version": "v2.3.1",
        "commit": "a1b2c3",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:29:55Z",
        "service": "inventory-service",
        "version": "v5.1.4",
        "commit": "d51099",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:29:10Z",
        "service": "feature-flags",
        "version": "v0.8.7",
        "commit": "0f3ab8",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:22:33Z",
        "service": "shipping-service",
        "version": "v2.7.1",
        "commit": "62c4de",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:18:19Z",
        "service": "cart-service",
        "version": "v1.2.0",
        "commit": "9b1207",
        "status": "rolled_back",
    },
    {
        "timestamp": "2026-07-02T14:15:40Z",
        "service": "search-service",
        "version": "v1.9.2",
        "commit": "9de44f",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:11:05Z",
        "service": "pricing-service",
        "version": "v4.4.4",
        "commit": "aa54f1",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T14:04:52Z",
        "service": "email-worker",
        "version": "v0.9.1",
        "commit": "3ded80",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T13:58:01Z",
        "service": "web-frontend",
        "version": "v4.7.0",
        "commit": "77c0aa",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T13:49:27Z",
        "service": "auth-service",
        "version": "v6.0.0",
        "commit": "f00baa",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T13:41:16Z",
        "service": "user-profile",
        "version": "v2.1.8",
        "commit": "12ab34",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T13:33:02Z",
        "service": "fraud-detection",
        "version": "v1.0.3",
        "commit": "cc90ef",
        "status": "failed",
    },
    {
        "timestamp": "2026-07-02T13:19:44Z",
        "service": "api-gateway",
        "version": "v8.2.0",
        "commit": "5e7d21",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T13:08:37Z",
        "service": "search-indexer",
        "version": "v1.6.2",
        "commit": "8d0c3a",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T12:47:15Z",
        "service": "cron-runner",
        "version": "v0.3.0",
        "commit": "41f6b9",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T12:22:58Z",
        "service": "notifications-service",
        "version": "v3.0.1",
        "commit": "4c8e10",
        "status": "succeeded",
    },
    {
        "timestamp": "2026-07-02T11:41:30Z",
        "service": "recommendations",
        "version": "v3.1.9",
        "commit": "7a2f9a",
        "status": "rolled_back",
    },
    {
        "timestamp": "2026-07-02T11:12:06Z",
        "service": "analytics-ingest",
        "version": "v1.3.9",
        "commit": "b3f9cf",
        "status": "succeeded",
    },
]

# Recent commits, newest first.
#
# The single commit that explains the incident is a1b2c3 on payments-service
# (the connection-pool refactor that dropped max idle conns 50 -> 5). Everything
# else here is ordinary churn from other teams shipping the same afternoon.
COMMITS = [
    {
        "timestamp": "2026-07-02T14:35:12Z",
        "service": "analytics-ingest",
        "sha": "b3f9d0",
        "author": "mia.wong",
        "message": "feat: add event batching to ingest pipeline",
    },
    {
        "timestamp": "2026-07-02T14:33:02Z",
        "service": "notifications-service",
        "sha": "4c8e11",
        "author": "tom.harris",
        "message": "fix: retry SMS send on transient gateway error",
    },
    {
        "timestamp": "2026-07-02T14:31:20Z",
        "service": "recommendations",
        "sha": "7a2f9b",
        "author": "alex.chen",
        "message": "feat: personalize homepage carousel by cohort",
    },
    {
        "timestamp": "2026-07-02T14:29:41Z",
        "service": "inventory-service",
        "sha": "d51099",
        "author": "nina.patel",
        "message": "fix: correct off-by-one in stock reservation",
    },
    {
        "timestamp": "2026-07-02T14:28:33Z",
        "service": "payments-service",
        "sha": "a1b2c3",
        "author": "dev.rivera",
        "message": "refactor: replace connection pool, lower max idle conns from 50 to 5",
    },
    {
        "timestamp": "2026-07-02T14:28:05Z",
        "service": "feature-flags",
        "sha": "0f3ab8",
        "author": "carlos.diaz",
        "message": "chore: bump feature-flags SDK to 2.4.0",
    },
    {
        "timestamp": "2026-07-02T14:24:56Z",
        "service": "shipping-service",
        "sha": "62c4de",
        "author": "jen.kim",
        "message": "feat: add same-day delivery estimates",
    },
    {
        "timestamp": "2026-07-02T14:19:48Z",
        "service": "search-service",
        "sha": "e77a10",
        "author": "sam.lee",
        "message": "test: add fuzz tests for query parser",
    },
    {
        "timestamp": "2026-07-02T14:16:02Z",
        "service": "cart-service",
        "sha": "9b1207",
        "author": "omar.said",
        "message": "refactor: extract cart totals into helper",
    },
    {
        "timestamp": "2026-07-02T14:14:27Z",
        "service": "web-frontend",
        "sha": "3b8c55",
        "author": "priya.k",
        "message": "fix: hydration mismatch on product page",
    },
    {
        "timestamp": "2026-07-02T14:12:10Z",
        "service": "pricing-service",
        "sha": "aa54f1",
        "author": "alex.chen",
        "message": "feat: tiered discount rules engine",
    },
    {
        "timestamp": "2026-07-02T14:10:22Z",
        "service": "search-service",
        "sha": "9de44f",
        "author": "sam.lee",
        "message": "perf: bump ranking model to v3",
    },
    {
        "timestamp": "2026-07-02T14:09:38Z",
        "service": "inventory-service",
        "sha": "771abc",
        "author": "nina.patel",
        "message": "chore: tidy up logging",
    },
    {
        "timestamp": "2026-07-02T14:06:15Z",
        "service": "analytics-ingest",
        "sha": "9ffed3",
        "author": "mia.wong",
        "message": "docs: document ingest schema v2",
    },
    {
        "timestamp": "2026-07-02T14:03:44Z",
        "service": "email-worker",
        "sha": "3ded80",
        "author": "tom.harris",
        "message": "fix: encode subject lines as UTF-8",
    },
    {
        "timestamp": "2026-07-02T14:01:02Z",
        "service": "recommendations",
        "sha": "d22f81",
        "author": "alex.chen",
        "message": "test: snapshot tests for ranking",
    },
    {
        "timestamp": "2026-07-02T13:50:09Z",
        "service": "web-frontend",
        "sha": "77c0aa",
        "author": "priya.k",
        "message": "style: update nav bar spacing and colors",
    },
    {
        "timestamp": "2026-07-02T13:46:03Z",
        "service": "auth-service",
        "sha": "f00baa",
        "author": "jen.kim",
        "message": "feat: add WebAuthn passkey support",
    },
    {
        "timestamp": "2026-07-02T13:42:51Z",
        "service": "payments-service",
        "sha": "5f0b2e",
        "author": "dev.rivera",
        "message": "docs: add README note about retry budget",
    },
    {
        "timestamp": "2026-07-02T13:39:27Z",
        "service": "fraud-detection",
        "sha": "cc90ef",
        "author": "nina.patel",
        "message": "feat: add velocity checks on new accounts",
    },
    {
        "timestamp": "2026-07-02T13:35:50Z",
        "service": "api-gateway",
        "sha": "2277ab",
        "author": "tom.harris",
        "message": "fix: propagate trace headers downstream",
    },
    {
        "timestamp": "2026-07-02T13:31:18Z",
        "service": "checkout",
        "sha": "c30991",
        "author": "sam.lee",
        "message": "test: add cart-summary snapshot tests",
    },
    {
        "timestamp": "2026-07-02T13:29:14Z",
        "service": "search-indexer",
        "sha": "8d0c3a",
        "author": "sam.lee",
        "message": "perf: parallelize index rebuild",
    },
    {
        "timestamp": "2026-07-02T13:22:08Z",
        "service": "api-gateway",
        "sha": "5e7d21",
        "author": "tom.harris",
        "message": "feat: add per-route rate limiting",
    },
    {
        "timestamp": "2026-07-02T13:15:33Z",
        "service": "payments-service",
        "sha": "b9e044",
        "author": "dev.rivera",
        "message": "chore: add structured logging to auth handler",
    },
    {
        "timestamp": "2026-07-02T13:07:51Z",
        "service": "search-indexer",
        "sha": "55dd20",
        "author": "sam.lee",
        "message": "chore: bump lucene to 9.10",
    },
    {
        "timestamp": "2026-07-02T12:58:22Z",
        "service": "cron-runner",
        "sha": "41f6b9",
        "author": "carlos.diaz",
        "message": "feat: add nightly cleanup job",
    },
    {
        "timestamp": "2026-07-02T12:55:03Z",
        "service": "checkout",
        "sha": "d7e9a2",
        "author": "sam.lee",
        "message": "chore: bump test fixtures",
    },
    {
        "timestamp": "2026-07-02T12:49:40Z",
        "service": "pricing-service",
        "sha": "1c3f88",
        "author": "alex.chen",
        "message": "docs: pricing rules readme",
    },
    {
        "timestamp": "2026-07-02T12:43:17Z",
        "service": "notifications-service",
        "sha": "4c8e10",
        "author": "tom.harris",
        "message": "feat: template preview endpoint",
    },
    {
        "timestamp": "2026-07-02T12:38:05Z",
        "service": "inventory-service",
        "sha": "90ab77",
        "author": "nina.patel",
        "message": "fix: stale cache on restock",
    },
    {
        "timestamp": "2026-07-02T12:25:44Z",
        "service": "analytics-ingest",
        "sha": "b3f9cf",
        "author": "mia.wong",
        "message": "chore: rotate ingest keys",
    },
    {
        "timestamp": "2026-07-02T12:10:19Z",
        "service": "user-profile",
        "sha": "33c0de",
        "author": "carlos.diaz",
        "message": "test: profile settings coverage",
    },
    {
        "timestamp": "2026-07-02T11:52:37Z",
        "service": "recommendations",
        "sha": "7a2f9a",
        "author": "alex.chen",
        "message": "chore: retire legacy model v2",
    },
    {
        "timestamp": "2026-07-02T11:38:11Z",
        "service": "auth-service",
        "sha": "e2b901",
        "author": "jen.kim",
        "message": "fix: session expiry rounding",
    },
    {
        "timestamp": "2026-07-02T11:20:48Z",
        "service": "web-frontend",
        "sha": "88f2a0",
        "author": "priya.k",
        "message": "feat: skeleton loaders on listing page",
    },
    {
        "timestamp": "2026-07-02T11:03:26Z",
        "service": "email-worker",
        "sha": "5b7cc1",
        "author": "omar.said",
        "message": "chore: dependency bump",
    },
]
