# Ariadne — Hackathon Submission Package (100% English)

## Status as of 17 October 2026

The 16 October hackathon submission missed the 15:20 KST deadline. This repository contains subsequent development and preservation work; it is not evidence of an accepted or on-time submission. The current implementation commit is [`dc58907`](https://github.com/kgg2512/google-hackathon-2026-starter/commit/dc589078ca6dcc7c2e8e9c634ceafde696940ec6), committed at 21:05:48 KST, after the deadline. The earlier [preservation draft PR #1](https://github.com/kgg2512/google-hackathon-2026-starter/pull/1) remains a separate historical snapshot.

The committed verification report contains both passes and failures. See [the evidence review](docs/2026-10-17/STATUS_REVIEW.md) before using the descriptions below as verified behavior. No new live-model or deployment verification was performed for this documentation review.

## Historical Draft Fields for the Cerebral Valley Submission Form

These fields preserve project intent and artifact references. They are not a submission receipt and should not be presented as an accepted entry.

**Form URL**: `https://cerebralvalley.ai/e/google-deepmind-ai-hackathon`

- **Project Name**: `Ariadne: Multi-Channel Epistemic Safety Copilot`
- **Track**: `Track 3: Google AI for social good`
- **Recorded Cloud Run URL**: `https://hackathon-app-xhhkfbrg4a-du.a.run.app`
- **Public GitHub Repository URL**: `https://github.com/kgg2512/google-hackathon-2026-starter`
- **Demo Video Link (Primary Direct MP4)**: `https://github.com/kgg2512/google-hackathon-2026-starter/raw/main/demo.mp4`
- **Demo Video Link (Backup Cloud Run MP4)**: `https://hackathon-app-xhhkfbrg4a-du.a.run.app/demo.mp4`

---

## Short Description / Tagline (1–2 sentences)
Ariadne is a multi-channel epistemic safety copilot built with `gemini-4-argon`, `gemini-3.8-flash`, and `gemma-4-31b-it` that helps older adults, families, and small business staff verify suspicious cross-channel requests (SMS, voice, messenger, and documents) before transferring money or sensitive data.

---

## Project Description (Historical Draft; Verification Limits Apply)

### 1. Problem & Target Users
Older adults, families, and small-business staff increasingly face multi-channel social engineering attacks spanning SMS, voice calls, messenger apps, and documents. Existing deepfake detectors output a single binary "real vs. fake" score, which fails when attackers use authentic messages from compromised accounts or when benign community notices are misclassified. **Ariadne** helps users pause and verify **what is claimed**, **what remains unverified**, and **how to independently confirm identity and payment requests out-of-band**.

### 2. Google AI Implementation
The implementation records **Google Cloud Run** (`asia-northeast3`); `requirements.txt` pins the `google-genai` SDK to `2.30.1`. This dependency pin does not establish the SDK version used by the current deployed service:
- **`gemini-4-argon`**: Performs Round 1 structured epistemic claim extraction (`IDENTITY`, `CRISIS`, `PAYMENT_REQUEST`, `AUTHORITY`, `URGENCY`, `CHANNEL_SHIFT`) and Round 2 synthesis of plain-language action briefs and out-of-band verification steps.
- **`gemini-3.8-flash`**: Acts as an Epistemic Safety Critic between Round 1 and Round 2, checking that synthetic cues are not conflated with automatic fraud, authentic formatting is not conflated with safety, and benign inputs are not over-escalated.
- **`gemma-4-31b-it`**: Is intended to generate a PII-redacted incident summary (`help_packet`) that masks phone numbers and bank account numbers before a user shares the summary with a trusted contact or public helpline (`112`, `1332`, `118`).
- **`gemini-nano-banana-2.1` & `gemini-3.8-flash-tts`**: Generates visual flow cards and spoken Korean audio summaries for older adults.

### 3. Intended Features & Verification Boundaries

The bullets below describe the design and implementation intent, not a claim that all live checks passed. The committed report and its failure states govern the current evidence.
- **Strict Separation of Live AI Mode vs. Reference Fixtures**: Users can inspect reference cases or run full Live Multi-Agent Gemini API analysis (`/api/analyze/stream` and `/api/analyze` with `mode="live"`) on any custom message.
- **Zero Preset Leakage & Honest Failure Reporting**: Custom inputs are analyzed purely from user-provided touchpoints and contacts. If an upstream model call times out or fails, Ariadne explicitly marks the stage as `failed` and leaves ungenerated fields empty rather than substituting example data.
- **Claims Ledger, Cross-Channel Provenance Graph & User Fact Correction**: Interactive HTML5 Canvas graph connecting touchpoints, claims, unverified gaps, and out-of-band actions, plus interactive user corrections (`User confirmed via saved callback number`).
- **Human-in-the-Loop Decision Gate**: Ariadne never automatically initiates calls, blocks bank transfers, or files external reports; all actions are advisory out-of-band verification steps.

### 4. Current Limitations
- **Advisory Guidance Only**: Ariadne does not connect to banking rails or telecom carriers and cannot automatically hold or cancel wire transfers.
- **Session Purge Scope**: Clearing session data removes browser `localStorage` and in-memory server state for the current Cloud Run instance; upstream API calls follow standard Google Gemini API data policies.
- **Recorded Verification Failures**: The committed report records test B and test C as failed. A–C all have overall `partial_failure`; the Gemma privacy stage timed out in all three. B returned 0 claims. See [the evidence review](docs/2026-10-17/STATUS_REVIEW.md).
- **Recorded Latency**: A–C took 44.44–57.05 seconds; the UI check took 66.74 seconds. The earlier 10–25-second estimate is not supported by this artifact.
