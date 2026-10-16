# Ariadne — Hackathon Submission Package (100% English)

## Copy-Paste Fields for Cerebral Valley Submission Form
**Form URL**: `https://cerebralvalley.ai/e/google-deepmind-ai-hackathon`

- **Project Name**: `Ariadne: Multi-Channel Epistemic Safety Copilot`
- **Track**: `Track 3: Google AI for social good`
- **Live Cloud Run URL**: `https://hackathon-app-xhhkfbrg4a-du.a.run.app`
- **Public GitHub Repository URL**: `https://github.com/kgg2512/google-hackathon-2026-starter`
- **Demo Video Link (Primary Direct MP4)**: `https://github.com/kgg2512/google-hackathon-2026-starter/raw/main/demo.mp4`
- **Demo Video Link (Backup Cloud Run MP4)**: `https://hackathon-app-xhhkfbrg4a-du.a.run.app/demo.mp4`

---

## Short Description / Tagline (1–2 sentences)
Ariadne is a multi-channel epistemic safety copilot built with `gemini-4-argon`, `gemini-3.8-flash`, and `gemma-4-31b-it` that helps older adults, families, and small business staff verify suspicious cross-channel requests (SMS, voice, messenger, and documents) before transferring money or sensitive data.

---

## Full Project Description (Copy-Paste Ready)

### 1. Problem & Target Users
Older adults, families, and small-business staff increasingly face multi-channel social engineering attacks spanning SMS, voice calls, messenger apps, and documents. Existing deepfake detectors output a single binary "real vs. fake" score, which fails when attackers use authentic messages from compromised accounts or when benign community notices are misclassified. **Ariadne** helps users pause and verify **what is claimed**, **what remains unverified**, and **how to independently confirm identity and payment requests out-of-band**.

### 2. Google AI Implementation
Deployed on **Google Cloud Run** (`asia-northeast3`) using the `google-genai` SDK (`v1.73.1`):
- **`gemini-4-argon`**: Performs Round 1 structured epistemic claim extraction (`IDENTITY`, `CRISIS`, `PAYMENT_REQUEST`, `AUTHORITY`, `URGENCY`, `CHANNEL_SHIFT`) and Round 2 synthesis of plain-language action briefs and out-of-band verification steps.
- **`gemini-3.8-flash`**: Acts as an Epistemic Safety Critic between Round 1 and Round 2, checking that synthetic cues are not conflated with automatic fraud, authentic formatting is not conflated with safety, and benign inputs are not over-escalated.
- **`gemma-4-31b-it`**: Generates a PII-redacted incident summary (`help_packet`) that masks phone numbers and bank account numbers before a user shares the summary with a trusted contact or public helpline (`112`, `1332`, `118`).
- **`gemini-nano-banana-2.1` & `gemini-3.8-flash-tts`**: Generates visual flow cards and spoken Korean audio summaries for older adults.

### 3. Key Features & Verification
- **Strict Separation of Live AI Mode vs. Pre-Verified Reference Fixtures**: Users can inspect pre-verified reference cases or run full Live Multi-Agent Gemini API analysis (`/api/analyze/stream` and `/api/analyze` with `mode="live"`) on any custom message.
- **Zero Preset Leakage & Honest Failure Reporting**: Custom inputs are analyzed purely from user-provided touchpoints and contacts. If an upstream model call times out or fails, Ariadne explicitly marks the stage as `failed` and leaves ungenerated fields empty rather than substituting example data.
- **Claims Ledger, Cross-Channel Provenance Graph & User Fact Correction**: Interactive HTML5 Canvas graph connecting touchpoints, claims, unverified gaps, and out-of-band actions, plus interactive user corrections (`User confirmed via saved callback number`).
- **Human-in-the-Loop Decision Gate**: Ariadne never automatically initiates calls, blocks bank transfers, or files external reports; all actions are advisory out-of-band verification steps.

### 4. Current Limitations
- **Advisory Guidance Only**: Ariadne does not connect to banking rails or telecom carriers and cannot automatically hold or cancel wire transfers.
- **Session Purge Scope**: Clearing session data removes browser `localStorage` and in-memory server state for the current Cloud Run instance; upstream API calls follow standard Google Gemini API data policies.
- **Live Latency**: End-to-end live multi-agent verification takes approximately 10–25 seconds per custom run.
