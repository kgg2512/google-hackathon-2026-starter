# AGENTS.md — 2026 Google DeepMind AI Hackathon Workspace Rules (Live Build Phase)

1. **Event Phase**: Live Hackathon Build (11:20–15:20 KST, 2026-10-16). Full implementation of competition features, live `gemini-4-argon` calls, companion model orchestration, and Cloud Run deployment are active and required.
2. **Lead Model (`gemini-4-argon`) Constraints**:
   - Prefer the **Interactions API** (`client.interactions.create`) or `google-genai>=2.3.0`.
   - Use `thinking_level` (`"low"` | `"medium"` | `"high"`). NEVER use deprecated `thinking_budget`.
   - NEVER pass `temperature`, `top_p`, `top_k`, or `cached_content` to `gemini-4-argon` (omit them completely; implicit caching is automatic at >= 4,096 prefix tokens).
   - In the unified 1M-token window, `max_output_tokens` caps `(thinking + output)` combined. Omit `max_output_tokens` (defaults to 65,536) or set `>= 32768`. For outputs `> 65,536` tokens, set `background=True`.
3. **Mandatory Multimodal & Multi-Model Orchestration**:
   - Pair `gemini-4-argon` (lead orchestrator / reasoning / multimodal input analysis / 3D & code synthesis) with at least 1–2 official companion models (`gemini-3.8-flash`, `gemini-nano-banana-2.1`, `gemini-3.8-flash-tts`, `gemini-3.8-live`, `gemini-3.5-live-translate-preview`, `gemini-omni-1.1-flash`, `lyria-3.5`, `antigravity-preview-09-2026`, `deep-research-preview-04-2026`, `gemma-4-31b-it`).
   - Surface **Multimodal Inputs** (image/video/audio/PDF/code/telemetry) and **Multimodal Companion Outputs** visibly in the UI alongside a **Live Multi-Model Telemetry HUD**.
4. **Mandatory Autonomous Verification Loop & Human-in-the-Loop (HITL)**:
   - Implement a real `Generate -> Critique/Verify -> Auto-Repair` loop in backend code and display the **Round 1 Draft vs. Round 2 Self-Corrected Diff** in the UI.
   - Include an explicit **Human-in-the-Loop (HITL) Confirmation Gate** in the UI before executing external system changes, patches, or high-stakes actions.
5. **Cloud Run & Security Hygiene**:
   - Keep `GET /health` returning `{"status": "ok"}` on port `8080`.
   - Load `GEMINI_API_KEY` from environment variables (`.env` locally, `--set-env-vars` on Cloud Run). Never hardcode API keys or commit `.env` to Git.
   - All user-facing documentation (`README.md`, `DESIGN.md`, `SUBMISSION_PACKAGE.md`) must be written 100% in English.
