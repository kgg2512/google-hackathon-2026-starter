# Ariadne: development review — 16 October 2026

> Historical review, not a claim of current production readiness. Implementation and deployment changes after the observations below require fresh verification.

## Outcome

The hackathon submission was not completed before the 15:20 KST deadline. A Cloud Run prototype and a public repository existed, but a playable submission video and final form receipt were not verified. Development continued locally after the deadline. Later source is preserved separately; its deployment is unverified.

## Product intent

Ariadne aims to prevent differences in AI literacy from becoming differences in personal digital safety. Attackers can exploit familiarity, urgency, authority and shame to isolate people from independent verification. The product should help a person understand a risky request and find an independent confirmation or support path before an irreversible action.

Scoped consent → permitted inputs across digital touchpoints → decomposition of identities, claims, evidence and requested actions → source-linked timeline → independent verification → facts, unknowns and next steps → user correction and deletion.

The long-term vision is an accessible personal protection app. Connections must use permitted platform capabilities; consent alone does not grant access to every app or call. Automatic transfers, reporting, third-party contact and covert surveillance are outside the intended behavior.

The name draws from Ariadne's thread: a traceable path back to evidence and independent help. REA inspired decomposition and tracing of claims, sources, dependencies, contradictions and actions. A specific REA package was not mandatory; installation or execution was not established. This concept is not forensic proof, universal deepfake detection or permission to investigate an attacker's systems.

## Historical evidence

| Evidence | Observation | Limit |
| --- | --- | --- |
| Final PRD v0.5 | Defined consent, provenance, identity/claim separation, independent verification, uncertainty, correction/deletion, accessibility and submission artifacts. | Requirements are not completed features. |
| Public repository and Cloud Run | Public source and a reachable deployed application existed on the event day. | Reachability does not prove correctness or local/deployed parity. |
| HTML and provided screenshots | Styled dashboard with presets, custom input and analysis controls. | Consumer usability and full rendered flow were not established. |
| Synthetic probe, approximately 14:52–14:54 KST | A benign library book-club message reached `/api/analyze/stream`; observer wall time was about 82.1 seconds and reported pipeline latency was 75,342 ms. | Different timing boundaries; one test, not a benchmark. |
| Probe result | Headline/summary reflected the book club; evidence ledger, identity/account table, graph and help packet retained unrelated family-emergency preset content. | Demonstrated contamination for that test, not every input. |
| Probe telemetry | Initial `TimeoutError` used `resilient_schema_fallback` yet reported `completed`; final execution label was `live_multi_model_sse`. | Labels alone do not establish each actual model or companion output. |
| Historical GitHub CI | Build and server startup succeeded; health returned HTTP 200, then an obsolete assertion raised `KeyError: 'scope'`. | CI failure was not a server startup failure; neither startup nor corrected assertions prove analysis quality. |

The probe used fictional input with no demand for money, links or personal data. No real victim material was needed. Browser automation did not produce a successful rendered-browser audit; HTML, provided screenshots and an API response supplied the historical evidence. Raw API output is deliberately not republished because it contained realistic fictional personal/contact/account details.

The source published at 14:39:58 KST was [25ce858](https://github.com/kgg2512/google-hackathon-2026-starter/commit/25ce8588a0d17528b8c47302fb56f60a026b9fa8). That version's JSON analysis endpoint returned preset-derived deterministic results rather than making real model calls. Readiness flags relied on key presence/constants; some scores/cache values were targets or fixture values rather than measurements.

## Later local changes — separate evidence

At the preservation inspection, GitHub `main` and local HEAD still matched 25ce858. Seven tracked files were modified locally. Selected stable copies are preserved in [the archive](../../archive/local-2026-10-16/README.md); their source timestamps include changes after 15:20 KST. Antigravity had six running processes. Files remained stable across copy-time checks and the later 15:43:10 KST comparison; this is not proof that future edits stopped.

Static inspection shows custom input separated from base fixtures, explicit failed states and empty generated fields on synthesis failure, and a JSON route consuming the SSE pipeline. These are changes toward the observed defects. The local README's claims that four live tests passed, latency was 10–25 seconds and a playable MP4 existed were unsupported by inspected test artifacts. This preservation task does not turn those claims into verified outcomes. See [the exact verification scope](VERIFICATION.md).

## Incomplete or unverified at the deadline

- Clean arbitrary-input results without inherited preset facts.
- Faithful live/cache/fallback/showcase separation throughout the UI.
- Every advertised companion/model capability and media path.
- Measured accuracy, improvement, cache savings or harm-prevention impact.
- End-to-end consent withdrawal, correction, session isolation and deletion.
- Playable, accessible demo video and final submission receipt.
- Local source, remote commit and deployed revision parity after the observation.

Displayed scores or percentages must not be described as achievements without a reproducible method and supporting data. Model agreement is not independent external verification.

## Lessons

1. Secure the minimum working path and submission artifacts first. Additional features cannot compensate for a missing required video or final form submission.
2. Test a novel benign input early; persuasive presets can conceal input contamination.
3. Treat fallback as a distinct outcome. Never silently convert timeout or missing evidence into success or safety.
4. Separate official requirements from architectural ambitions. Extra panels/models must not displace required deliverables.
5. Freeze scope early and reserve upload/access/receipt time. A queued prompt is not proof it was received or acted on. Explain necessary user actions early.
6. Report completion only with evidence. Label estimates uncertain; working, deployed and submitted are distinct states.

## Follow-up backlog

P0 preservation is partly addressed by this branch: selected source, public requirements and sanitized evidence are retained without modifying active work. Runtime revision parity and a demo artifact remain unresolved. No missed submission is retroactively represented as completed.

P1 correctness work remains future work: regression cases for benign requests, impersonation, insufficient/conflicting evidence and failed tools; source references for all claims; no invented contacts; honest per-stage and overall status; consent, correction, session isolation and deletion tests.

P2 demonstration work remains future work: one understandable input → facts/unknowns/next-action path, optional technical details, clearly labeled fixtures, a short recording of actual normal and uncertain behavior, and reproducible test instructions before efficacy claims. No feature development, paid calls or redeployment was performed as part of preservation.

## Publication boundaries

This is a sanitized project record. Private conversations, event credentials, account identifiers and raw sensitive logs are excluded. Historical source already public remains available in Git history; this task does not claim to scrub existing history.
