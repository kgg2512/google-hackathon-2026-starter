# Ariadne — System Design & Architecture (`DESIGN.md`)

## Verification boundary · 17 October 2026

This document describes architecture and intended behavior. The checked-in report records B and C as failed, A–C as `partial_failure`, and Gemma privacy-stage timeouts. Current deployment parity and live behavior were not retested in this review. See [the evidence review](docs/2026-10-17/STATUS_REVIEW.md).

## 1. Architectural Overview
Ariadne is a FastAPI + Vanilla JS single-page web application with a recorded **Google Cloud Run** deployment URL (`https://hackathon-app-xhhkfbrg4a-du.a.run.app`) for **Track 3: Google AI for Social Good**.

### Multi-Agent Verification Pipeline (`app.py`)
1. **Stage 1 — Round 1 Claim Decomposition (`gemini-4-argon`, `thinking_level="low"`)**:
   - Parses raw user touchpoints and optional user-provided known contacts into a structured JSON `claims_ledger`, `unverified_gaps`, and `risk_tier` (`VERIFIED_LOW`, `MODERATE_CONCERN`, `ELEVATED_RISK`, `HIGH_CONCERN_PAUSE`).
   - Enforces strict input isolation: when `is_custom=True`, Ariadne never merges preset touchpoints or preset contacts.
2. **Stage 2 — Epistemic Safety Critic (`gemini-3.8-flash`, `thinking_level="low"`)**:
   - Audits Round 1 output for epistemic errors (e.g., false alarms on benign messages, missing out-of-band verification steps on payment demands, or over-reliance on tone).
   - Supports zero defects (`defects_found: []`) when Round 1 accurately classifies a benign input.
3. **Stage 3 — Round 2 Verified Synthesis (`gemini-4-argon`, `thinking_level="medium"`)**:
   - Synthesizes the refined plain-Korean `one_screen_summary`, `decision_label`, `claims_ledger`, and `oob_anchors`.
4. **Stage 4 — PII Redaction (`gemma-4-31b-it`)**:
   - Is intended to mask phone numbers and account numbers in the user's input and produces a shareable `help_packet` for trusted contacts or public helplines (`112`, `1332`, `118`).

## 2. Failure Handling & Epistemic Integrity
- If any live model stage fails or times out, Ariadne records `status: "failed"` and `call_outcome: "failed"` in the stage telemetry and sets `overall_status` to `"failed"` or `"partial_failure"`.
- Failed runs do not substitute preset scenario claims, provenance graphs, or contacts in place of live analysis.

## 3. Limitations
- Ariadne provides advisory verification steps and redacted summaries; it does not intercept financial transactions or telecom calls.
- In-memory audit logs and browser `localStorage` can be cleared via `/api/session/purge`, scoped to the active browser and container instance.
