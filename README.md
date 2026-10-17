# Ariadne — Multi-Channel Epistemic Safety Copilot

## Status as of 17 October 2026

The 16 October hackathon submission missed the 15:20 KST deadline. This repository contains subsequent development and preservation work; it is not evidence of an accepted or on-time submission. The current implementation commit is [`dc58907`](https://github.com/kgg2512/google-hackathon-2026-starter/commit/dc589078ca6dcc7c2e8e9c634ceafde696940ec6), committed at 21:05:48 KST, after the deadline. The earlier [preservation draft PR #1](https://github.com/kgg2512/google-hackathon-2026-starter/pull/1) remains a separate historical snapshot.

The committed verification report contains both passes and failures. See [the evidence review](docs/2026-10-17/STATUS_REVIEW.md) before using the descriptions below as verified behavior. No new live-model or deployment verification was performed for this documentation review.

**Track 3: Google AI for Social Good** — *2026 Google DeepMind AI Hackathon (Seoul)*

- **Recorded Cloud Run App URL (availability not rechecked in this review)**: [https://hackathon-app-xhhkfbrg4a-du.a.run.app](https://hackathon-app-xhhkfbrg4a-du.a.run.app)
- **Public GitHub Repository**: [https://github.com/kgg2512/google-hackathon-2026-starter](https://github.com/kgg2512/google-hackathon-2026-starter)
- **Committed Demo MP4 (file presence verified; playback not rechecked)**: [https://github.com/kgg2512/google-hackathon-2026-starter/raw/main/demo.mp4](https://github.com/kgg2512/google-hackathon-2026-starter/raw/main/demo.mp4) *(the existing documentation also links to Cloud Run at [https://hackathon-app-xhhkfbrg4a-du.a.run.app/demo.mp4](https://hackathon-app-xhhkfbrg4a-du.a.run.app/demo.mp4))*

---

## 1. Problem & Target Users

Older adults, families, and small business staff increasingly face coordinated multi-channel scams across SMS, voice calls, messenger apps, and video calls. Single-artifact deepfake detectors fail in two critical ways:
1. **Authentic media can still be used for fraud** (e.g., an attacker sends an authentic leaked document or compromises a real account and demands an urgent wire transfer to a third-party beneficiary).
2. **Benign messages can be misclassified** if an assistant relies on superficial keyword triggers rather than decomposing claims, requested actions, and verification status.

**Ariadne** is an epistemic safety copilot that separates **what was observed**, **what is claimed**, **what remains unverified**, and **how to verify independently out-of-band** before acting on high-stakes requests.

---

## 2. Configured Google AI Roles

Ariadne is configured for a multi-stage verification pipeline on the official `google-genai` SDK (pinned to `2.30.1` in `requirements.txt`):
- **`gemini-4-argon` (Round 1 Decomposer & Round 2 Synthesizer)**: Extracts structured claims (`IDENTITY`, `CRISIS`, `PAYMENT_REQUEST`, `AUTHORITY`, `URGENCY`, `CHANNEL_SHIFT`), identifies unverified gaps, and synthesizes a plain-language decision brief with out-of-band verification steps.
- **`gemini-3.8-flash` (Epistemic Safety Critic)**: Audits the Round 1 draft to ensure synthetic media is not equated with automatic fraud, authentic formatting is not equated with safety, and benign messages are not falsely flagged as emergencies.
- **`gemma-4-31b-it` (Privacy & PII Redaction Auditor)**: Is intended to generate a redacted help packet (`help_packet`) that masks phone numbers and bank account identifiers before a user shares the summary with a trusted family member or public helpline (`112`, `1332`, `118`).
- **`gemini-nano-banana-2.1` & `gemini-3.8-flash-tts`**: Generates visual warning diagrams and spoken Korean audio guidance for accessibility.

---

## 3. Implementation Overview

This describes the intended implementation. A configured stage or endpoint is not evidence that every live run succeeds; the recorded failures in section 4 remain open.

1. **Dual Operating Modes (Clearly Separated in UI & API)**:
   - **Live Multi-Agent API Mode (`/api/analyze/stream` & `/api/analyze` with `mode="live"`)**: Executes real-time calls to `gemini-4-argon`, `gemini-3.8-flash`, and `gemma-4-31b-it` on any custom user input, reporting exact per-stage call status (`completed` vs. `failed`) and elapsed wall-clock latency.
   - **Reference Scenario Fixtures (`mode="fixture"`)**: Clearly labeled reference fixtures for instant inspection of three representative scenarios.
2. **Strict Input Isolation & Honest Failure States**:
   - Custom inputs never inherit preset touchpoints, claims, provenance nodes, or known contacts.
   - If a model call times out or errors, Ariadne explicitly reports `status: "failed"` (`overall_status: "failed"` or `"partial_failure"`) and leaves ungenerated fields empty rather than substituting preset data as a fake success.
3. **Structured Claims Ledger & Cross-Channel Provenance Graph**:
   - Displays each extracted claim's type, source touchpoint, verification state, and missing evidence.
   - Interactive HTML5 Canvas graph linking touchpoints (`T1..Tn`), claims (`C1..Cn`), unverified gaps, and out-of-band verification actions (`A1..An`).
4. **Human-in-the-Loop (HITL) Decision Gate & Redacted Help Packet**:
   - Ariadne does **not** automatically contact third parties, block bank accounts, or submit police reports. Users review out-of-band verification steps and must explicitly check a confirmation box before unlocking the redacted help packet.

---

## 4. Recorded Verification Results

The checked-in [verification_report.json](https://github.com/kgg2512/google-hackathon-2026-starter/blob/dc589078ca6dcc7c2e8e9c634ceafde696940ec6/verification_report.json) is timestamped **16 October 2026, 15:52:41 KST**. This review inspected that artifact; it did not rerun the live service or independently reproduce the report.

| Check | Recorded result | Important limit |
| --- | --- | --- |
| A: benign book-club input | `pass: true`, `VERIFIED_LOW`, no preset leak, 0 known contacts; 51.16 s | Overall `partial_failure`; the Gemma privacy stage timed out. This is a bounded benign-input result, not a fully successful pipeline. |
| B: fictional urgent wire input | `pass: false`; 0 claims, 1 out-of-band anchor; 57.05 s | Overall `partial_failure`; Gemma timed out and image generation failed. Claim extraction is not verified by this run. |
| C: simulated model timeout | `pass: false`; 0 claims; 44.44 s | The first Argon stage failed, later stages still ran, and the final status was `partial_failure`. The artifact does not support the previous claim that this test returned overall `failed`. |
| D: deployed UI and video | `pass: true`, preset-leak-free; UI 66.74 s | Reported UI result only. The MP4 exists in the repository (4,730,365 bytes); this review did not inspect playback or establish current deployment parity. |

The [CI run for `dc58907`](https://github.com/kgg2512/google-hackathon-2026-starter/actions/runs/38898179566) passed. Its [workflow](https://github.com/kgg2512/google-hackathon-2026-starter/blob/dc589078ca6dcc7c2e8e9c634ceafde696940ec6/.github/workflows/verify.yml) checks container build/startup, health/readiness/presets responses, and an HTML marker. It does not call the live analysis endpoint or establish model quality, privacy-redaction success, or full browser behavior.

---

## 5. Current Limitations

- **Advisory Only (No Financial Interception)**: Ariadne cannot hold, block, or reverse real bank transfers; "Pause Before Acting" in the UI is user guidance, not bank-level transaction blocking.
- **Session Storage Scope**: Client-side purge clears `localStorage` and in-memory server session history for the current instance, but requests sent to the Gemini API are subject to Google's standard API data handling policies.
- **Observed Latency**: The checked-in A–C runs took 44.44–57.05 seconds, and the UI run took 66.74 seconds. These few recorded runs are not a general latency guarantee.
- **Open Verification Gaps**: B and C are recorded failures, and the Gemma privacy stage timed out in A–C. A reliable redacted help packet and complete custom-input claim extraction still require successful, reproducible evidence.

---

## 6. Quick Start

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8080
```
