# Ariadne evidence review — 17 October 2026

## Scope and outcome

This documentation-only review reconciles accessible GitHub evidence for the work week beginning 10 October 2026 KST. It is not a whole-computer audit, a new live-model evaluation, or a deployment check. The event submission missed the **16 October, 15:20 KST deadline**, as already recorded in [preservation PR #1](https://github.com/kgg2512/google-hackathon-2026-starter/pull/1). Later work does not change that outcome.

Reviewed implementation baseline: [`dc589078ca6dcc7c2e8e9c634ceafde696940ec6`](https://github.com/kgg2512/google-hackathon-2026-starter/commit/dc589078ca6dcc7c2e8e9c634ceafde696940ec6). Repository state was checked on 17 October 2026 around 14:28 KST.

## Timeline and separate versions

| Time (KST) | Evidence | Meaning |
| --- | --- | --- |
| 15 Oct 20:21 | [`69968c1`](https://github.com/kgg2512/google-hackathon-2026-starter/commit/69968c14cb91c03f304108ddd8c3e0c603d17c43) | Generic infrastructure starter. |
| 15 Oct 20:22 | [`1497c63`](https://github.com/kgg2512/google-hackathon-2026-starter/commit/1497c63d37df2a2b8d4c9a0a07472c85679a3ba0) | Generic container verification workflow. |
| 16 Oct 14:39:58 | [`25ce858`](https://github.com/kgg2512/google-hackathon-2026-starter/commit/25ce8588a0d17528b8c47302fb56f60a026b9fa8) | Ariadne implementation baseline captured by the earlier preservation work. |
| 16 Oct 15:20 | [PR #1 outcome](https://github.com/kgg2512/google-hackathon-2026-starter/pull/1) | Submission deadline missed. |
| 16 Oct, capture checked through 15:51:45 | [Preservation inventory](https://github.com/kgg2512/google-hackathon-2026-starter/blob/4a4a180206bf394c900e8d91b336b4e1192af231/docs/2026-10-16/PRESERVATION.md) | Historical sanitized archive. PR #1 remains draft/open at `4a4a180`, unmerged at this review. Its no-video finding is limited to the inspected capture. |
| 16 Oct 15:52:41 | [Report timestamp](https://github.com/kgg2512/google-hackathon-2026-starter/blob/dc589078ca6dcc7c2e8e9c634ceafde696940ec6/verification_report.json) | Time declared inside the A–D report; not an independently observed execution time. |
| 16 Oct 21:05:48 | [`dc58907`](https://github.com/kgg2512/google-hackathon-2026-starter/commit/dc589078ca6dcc7c2e8e9c634ceafde696940ec6) | Later commit on main adds the report and MP4 alongside source/document changes. This is separate from the earlier archive. |

The existing preservation branch and its manifests are unchanged by this review. Its failed historical CI is not the current main CI result.

## What the committed report actually says

| Check | pass | overall_status | Time | Essential detail |
| --- | --- | --- | --- | --- |
| A — benign book club | true | partial_failure | 51.16 s | No preset leak; 0 known contacts; privacy stage timed out. |
| B — fictional urgent wire | false | partial_failure | 57.05 s | 0 claims and 1 OOB anchor; privacy timeout and image failure. |
| C — controlled timeout | false | partial_failure | 44.44 s | First Argon call failed; later stages continued; privacy timeout and image failure. |
| D — deployed UI/video | true | Not recorded | 66.74 s UI | Report says preset-leak-free; video size matches the repository entry. |

Source: [immutable verification report](https://github.com/kgg2512/google-hackathon-2026-starter/blob/dc589078ca6dcc7c2e8e9c634ceafde696940ec6/verification_report.json). The reported model-call outcomes have not been independently replayed. The result does not establish that every feature passed. In particular, a successful summary or low risk tier must not hide an overall partial failure.

## Artifact and CI evidence

- [MP4 repository entry](https://github.com/kgg2512/google-hackathon-2026-starter/blob/dc589078ca6dcc7c2e8e9c634ceafde696940ec6/demo.mp4): 4,730,365 bytes, Git blob `18d8bb7a12ec5da2f7182ac1f96c5a14286b0b82`. Presence is verified; video playback, content, and current Cloud Run serving were not checked.
- [Main CI run](https://github.com/kgg2512/google-hackathon-2026-starter/actions/runs/38898179566): completed successfully for `dc58907`.
- [Workflow scope](https://github.com/kgg2512/google-hackathon-2026-starter/blob/dc589078ca6dcc7c2e8e9c634ceafde696940ec6/.github/workflows/verify.yml): Docker build/startup; health, readiness and presets endpoints; root HTML marker. No live analysis request is made. Passing this smoke check is not proof of successful model calls, financial-safety quality, redaction quality, or browser end-to-end correctness.
- [Historical archive CI](https://github.com/kgg2512/google-hackathon-2026-starter/actions/runs/38863528450): failure recorded on `4a4a180`. PR #1 explains the older workflow assertion mismatch. No failure is silently rewritten as a pass.

## Documentation corrections made

1. Add the missed deadline and clear version boundaries to README and the historical submission draft.
2. Replace all-pass-style A–D prose with the report's actual pass/failure values.
3. Replace the unsupported 10–25-second latency statement with recorded measurements and their limits.
4. Qualify video availability, deployment status, and privacy-stage success; correct the design's source path to `app.py`.
5. Keep runtime source, workflows, the MP4, and the earlier preservation archive untouched.

## Remaining work, if development is resumed

- Reproduce and fix B's empty claim extraction; define and test intended overall status and stage continuation for C.
- Establish successful privacy-stage redaction evidence, including failure handling and no accidental disclosure from partial outputs.
- Record reproducible tests, inputs, timestamps, implementation SHA and deployment revision together; review the resulting demo playback against that version.
- Treat readiness booleans as application assertions until supported by external verification.
- Any further live model calls, source fixes, merge or deployment require their applicable authorization. This review performs none of them.
