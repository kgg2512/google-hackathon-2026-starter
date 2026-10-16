# Verification evidence and limits

## Historical production observation

The parent review supplied a synthetic library-book-club probe from approximately 14:52–14:54 KST. It requested no money, links, downloads or personal data. The streamed result mixed the new summary with unrelated preset evidence, identities/accounts, graph and help packet. Wall time was about 82.1 seconds; pipeline telemetry reported 75,342 ms. Initial timeout fallback appeared completed and final mode was `live_multi_model_sse`. These are historical failures, preserved even if later code changed.

HTML and health reachability were established earlier. Current deployed revision and corrected custom-input behavior were not retested here. This task made no paid model calls, production analysis requests or redeployments.

## CI evidence

The [14:40 KST CI job](https://github.com/kgg2512/google-hackathon-2026-starter/actions/runs/38856961023/job/116830490398) was read through the existing GitHub connection. It built the container, started Uvicorn, received HTTP 200 from `/health`, then failed at `KeyError: 'scope'`. The workflow still expected the older infrastructure contract (`scope=infrastructure-only`) and old readiness flags. This was a stale test assertion, not proof that the server never started.

The active workflow is not changed by this preservation branch. A new branch push may therefore reproduce the historical CI failure. Its container check exercises the historical root runtime, not the archived snapshot. CI success would still not prove successful real-input analysis.

## Static review of the later local snapshot

| Area | Evidence in archived source | Limit or remaining defect |
| --- | --- | --- |
| Custom input | `is_custom` creates no base fixture and uses supplied touchpoints/contacts only | Does not establish that real model output is factual |
| Failed models | Per-stage `failed`, empty synthesis claims/anchors and overall failure aggregation | Execution mode still says `live_multi_model_sse`; check overall/stage status |
| JSON route | `/api/analyze` consumes the same streaming pipeline | Different from the historical deterministic JSON route |
| Fixture mode | Only `mode=showcase` selects a fixture | Local prose incorrectly said `mode=fixture` |
| Consent | Explicit false is rejected | Request schema defaults consent to true; full scoped consent/withdrawal not established |
| Readiness | Key presence maps to model access; deployment flag is constant true | No live validation of models or deployment |
| Media input | Schema accepts media fields; UI collects base64 | Main decomposition/synthesis prompts use touchpoints, contacts and text; actual media-model input was not established |
| Source linking | Structured claims and dynamic graph exist | Prompt schema lacks full required span/timestamp linkage; independent verification is not implemented merely by a critic |
| Token/cache claims | Token counts estimated and clamped to a minimum | No measured cache hit rate or billing proof |
| Corrections/deletion | Correction and in-memory/HITL routes exist | Custom recompute, derived-data deletion and multiple-container behavior require validation |
| Video | Route serves a local file only if it exists | No `demo.mp4` in inspected local tree or baseline |

The original local README and submission prose claimed four live checks passed and 10–25 second latency. No accompanying test output or recording was found in the inspected project. Their SDK prose (v1.73.1) also disagreed with preserved pins (2.30.1). Those claims are not adopted here.

## Offline verification

Python syntax was checked for the two archived Python source files. The accompanying [offline audit](offline_audit.py) covers health contract, misleading readiness flags, controlled all-model failure, empty generated claims/anchors, custom input isolation, explicit consent rejection, mocked success assembly and the fixture-mode contract. Successful model helpers are synthetic stubs and connections are blocked after event-loop initialization. This does not establish real model quality, deployed behavior, rendering, accessibility, media generation or end-to-end correctness.

See [offline audit results](offline-results.json) for the actual completed outcome. The audit was run only on copied source. The original working tree was not edited.
