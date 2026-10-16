# Ariadne — Multi-Channel Epistemic Safety Copilot

**Track 3: Google AI for Social Good** — *2026 Google DeepMind AI Hackathon (Seoul)*

- **Live Deployed App (Google Cloud Run)**: [https://hackathon-app-xhhkfbrg4a-du.a.run.app](https://hackathon-app-xhhkfbrg4a-du.a.run.app)
- **Public GitHub Repository**: [https://github.com/kgg2512/google-hackathon-2026-starter](https://github.com/kgg2512/google-hackathon-2026-starter)
- **Playable Demo Video (Direct MP4 — No Login Required)**: [https://github.com/kgg2512/google-hackathon-2026-starter/raw/main/demo.mp4](https://github.com/kgg2512/google-hackathon-2026-starter/raw/main/demo.mp4) *(also served on Cloud Run at [https://hackathon-app-xhhkfbrg4a-du.a.run.app/demo.mp4](https://hackathon-app-xhhkfbrg4a-du.a.run.app/demo.mp4))*

---

## 1. Problem & Target Users

Older adults, families, and small business staff increasingly face coordinated multi-channel scams across SMS, voice calls, messenger apps, and video calls. Single-artifact deepfake detectors fail in two critical ways:
1. **Authentic media can still be used for fraud** (e.g., an attacker sends an authentic leaked document or compromises a real account and demands an urgent wire transfer to a third-party beneficiary).
2. **Benign messages can be misclassified** if an assistant relies on superficial keyword triggers rather than decomposing claims, requested actions, and verification status.

**Ariadne** is an epistemic safety copilot that separates **what was observed**, **what is claimed**, **what remains unverified**, and **how to verify independently out-of-band** before acting on high-stakes requests.

---

## 2. How Google AI Is Used

Ariadne runs a multi-stage verification pipeline on the official `google-genai` SDK (`v1.73.1`):
- **`gemini-4-argon` (Round 1 Decomposer & Round 2 Synthesizer)**: Extracts structured claims (`IDENTITY`, `CRISIS`, `PAYMENT_REQUEST`, `AUTHORITY`, `URGENCY`, `CHANNEL_SHIFT`), identifies unverified gaps, and synthesizes a plain-language decision brief with out-of-band verification steps.
- **`gemini-3.8-flash` (Epistemic Safety Critic)**: Audits the Round 1 draft to ensure synthetic media is not equated with automatic fraud, authentic formatting is not equated with safety, and benign messages are not falsely flagged as emergencies.
- **`gemma-4-31b-it` (Privacy & PII Redaction Auditor)**: Generates a redacted help packet (`help_packet`) that masks phone numbers and bank account identifiers before a user shares the summary with a trusted family member or public helpline (`112`, `1332`, `118`).
- **`gemini-nano-banana-2.1` & `gemini-3.8-flash-tts`**: Generates visual warning diagrams and spoken Korean audio guidance for accessibility.

---

## 3. Key Implemented Features

1. **Dual Operating Modes (Clearly Separated in UI & API)**:
   - **Live Multi-Agent API Mode (`/api/analyze/stream` & `/api/analyze` with `mode="live"`)**: Executes real-time calls to `gemini-4-argon`, `gemini-3.8-flash`, and `gemma-4-31b-it` on any custom user input, reporting exact per-stage call status (`completed` vs. `failed`) and elapsed wall-clock latency.
   - **Pre-Verified Scenario Fixtures (`mode="fixture"`)**: Clearly labeled reference fixtures for instant inspection of three representative scenarios.
2. **Strict Input Isolation & Honest Failure States**:
   - Custom inputs never inherit preset touchpoints, claims, provenance nodes, or known contacts.
   - If a model call times out or errors, Ariadne explicitly reports `status: "failed"` (`overall_status: "failed"` or `"partial_failure"`) and leaves ungenerated fields empty rather than substituting preset data as a fake success.
3. **Structured Claims Ledger & Cross-Channel Provenance Graph**:
   - Displays each extracted claim's type, source touchpoint, verification state, and missing evidence.
   - Interactive HTML5 Canvas graph linking touchpoints (`T1..Tn`), claims (`C1..Cn`), unverified gaps, and out-of-band verification actions (`A1..An`).
4. **Human-in-the-Loop (HITL) Decision Gate & Redacted Help Packet**:
   - Ariadne does **not** automatically contact third parties, block bank accounts, or submit police reports. Users review out-of-band verification steps and must explicitly check a confirmation box before unlocking the redacted help packet.

---

## 4. Live Verification Summary (4-Part Unified Test Suite)

All four verification checks were executed against the live application:
- **Test A (Benign Input — Library Book Club Notice)**: Input `"도서관 독서모임 안내, 송금·링크·다운로드·개인정보 요구 없음"` produced `VERIFIED_LOW` risk with zero leakage of preset family/wire claims or preset contacts.
- **Test B (Fictional Urgent Wire Scam Input)**: Custom urgent wire demand extracted the specific payment/urgency claims, linked unverified gaps, and generated independent out-of-band verification steps matching the input.
- **Test C (Controlled Model Timeout / Failure)**: Simulated timeout (`simulate_failure="timeout"`) returned `overall_status: "failed"` with `call_outcome: "failed"` and empty claims/anchors (`[]`), never disguising fallback text as completed live analysis.
- **Test D (Deployed Cloud Run UI End-to-End)**: Verified live custom input submission, SSE stage progression, and full DOM rendering of the summary, claims ledger, provenance graph, out-of-band checklist, and redacted help packet.

---

## 5. Current Limitations

- **Advisory Only (No Financial Interception)**: Ariadne cannot hold, block, or reverse real bank transfers; "Pause Before Acting" in the UI is user guidance, not bank-level transaction blocking.
- **Session Storage Scope**: Client-side purge clears `localStorage` and in-memory server session history for the current instance, but requests sent to the Gemini API are subject to Google's standard API data handling policies.
- **Latency in Live Mode**: Full multi-model execution (`gemini-4-argon` Round 1 + `gemini-3.8-flash` Critic + `gemini-4-argon` Round 2 + `gemma-4-31b-it` Redactor) takes ~10–25 seconds depending on network and model load.

---

## 6. Quick Start

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8080
```
