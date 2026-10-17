# Ariadne public evidence update — 17 October 2026

This publishes the prepared inventory's public summary. It records historical evidence and unresolved work; it is not a new model evaluation or deployment.

## Recorded failures and limited passes

Source: [saved verification report](https://github.com/kgg2512/google-hackathon-2026-starter/blob/dc589078ca6dcc7c2e8e9c634ceafde696940ec6/verification_report.json), timestamp 16 October 2026, 15:52:41 KST.

| Test | Recorded pass | Outcome and limits | Recorded seconds |
| --- | --- | --- | --- |
| A | true | partial_failure; privacy model timed out | 51.16 |
| B | **false** | partial_failure; zero extracted claims; privacy timeout and partial media failure | 57.05 |
| C | **false** | controlled Round 1 timeout; overall partial_failure; privacy timeout and partial media failure | 44.44 |
| D | true | Recorded UI/video check only; does not establish complete model success | 66.74 |

A/D passing flags do not make the full suite pass. C's controlled failure flag remains false; observing an injected timeout does not mean its overall failure-handling acceptance criteria passed. No failure is relabeled as successful analysis.

The README's blanket success and 10–25-second statements conflict with this report. Documentation corrections are in [Draft PR #2](https://github.com/kgg2512/google-hackathon-2026-starter/pull/2), not merged into main. [The existing status review](STATUS_REVIEW.md) gives the wider timeline.

## Implementation and version boundaries

The inspected source baseline is [dc589078](https://github.com/kgg2512/google-hackathon-2026-starter/commit/dc589078ca6dcc7c2e8e9c634ceafde696940ec6). It contains application, interface, fixtures, design/submission documents and a 4,730,365-byte demo MP4. Presence does not prove playback, current deployment, model availability, or timely submission. The existing Notion project result records a missed submission deadline; this update does not claim an accepted submission.

The dependency file pins google-genai 2.30.1; prose describing 1.73.1 is stale. The afternoon preservation snapshot in [Draft PR #1](https://github.com/kgg2512/google-hackathon-2026-starter/pull/1) predates this baseline. Its historical lack of a video must not be presented as the later repository state. Eight recorded offline snapshot checks and container smoke checks cover different scopes from real model success.

## Unfinished work

1. B and C still fail their recorded criteria. Privacy-model timeouts and incomplete structured output remain unresolved.
2. Reuse requires fresh custom-input, timeout, partial-failure and fixture-isolation checks. No such tests were rerun for this publication.
3. Current service reachability, deployed revision parity, model access, and end-to-end behavior remain unverified.
4. Documentation changes remain an open draft proposal. No merge, runtime change or deployment is included.

The previous-event survey records 111 projects, zero independently reproduced services and zero fully watched demo videos. These are collection statistics, not performance evidence.

## Publication boundary

Only this summary and a derived [verification summary](VERIFICATION_SUMMARY.json) are added. Raw inputs, names/contact/account identifiers, credentials, authentication material, local filesystem/session identifiers and private operational documents are excluded. Local originals, runtime source, the original verification report, video and historical archive are preserved.
