# Ariadne — Personal Digital Safety & Epistemic Provenance Copilot

**2026 Google DeepMind AI Hackathon (Seoul Startup Campus)**  
**Official Track:** `Track 3: Google AI for social good`  
**Live Cloud Run Demo URL:** [https://hackathon-app-xhhkfbrg4a-du.a.run.app](https://hackathon-app-xhhkfbrg4a-du.a.run.app)  
**Public GitHub Repository:** [https://github.com/kgg2512/google-hackathon-2026-starter](https://github.com/kgg2512/google-hackathon-2026-starter)  
**Lead Model:** `gemini-4-argon` (1M Unified Context Window, 95% Implicit Context Caching)  
**Companion Models:** `gemini-3.8-flash`, `gemma-4-31b-it`, `gemini-nano-banana-2.1`, `gemini-3.8-flash-tts`

---

## 1. Problem Statement & Epistemic Philosophy (PRD v0.5)

Modern AI-enabled scams—voice-cloned family emergencies, authority impersonation, sideloaded `.apk` traps, and supplier invoice redirects—rarely rely on a single synthetic media file. Instead, attackers exploit **broken epistemic provenance across multiple communication channels**:
- A caller on an unknown burner number claims to be a family member whose phone screen broke (**Account Identifier vs. Claimed Persona break**).
- A message includes an internal callback phone number or verification portal (**Circular Verification Trap**).
- Forwarded messages are repeated across chat groups to create an illusion of corroboration (**Forwarded Duplicate Inflation**).
- Adversarial strings (`IGNORE ALL PREVIOUS INSTRUCTIONS...`) are embedded inside text or image captions to hijack naive AI safety filters (**Prompt Injection**).

Single-image deepfake detectors fail because they output opaque numerical percentages (`"87% scam probability"`) that induce panic or false reassurance. **Ariadne** is built on three foundational epistemic axioms:
1. **`Synthetic Signal != Fraud`** (Creative, assistive, or compressed media can appear synthetic without malicious intent).
2. **`Authentic Media != Safe`** (Real screenshots, real stolen photos, or real forwarded invoices can be weaponized inside an impersonation thread).
3. **`Unverified != Safe`** (Any high-consequence action—money wire, credential entry, `.apk` sideloading, secrecy pledge—requires **Independent Out-of-Band Verification**).

---

## 2. Multi-Model & Multimodal Architecture

Ariadne orchestrates **five distinct models** via the official `google-genai` SDK (`client.interactions.create`):

| Stage | Model | Configuration | Responsibility |
| :--- | :--- | :--- | :--- |
| **Stage 1: Pre-Audit Guard** | Deterministic Guard | Zero-SSRF / Regex | Enforces **FR01 Scoped Consent**, collapses forwarded duplicates (**FR03**), isolates in-message callback numbers (**FR05**), and quarantines prompt injections (**Section 7**). |
| **Stage 2: Round 1 Lead Architect** | `gemini-4-argon` | `thinking_level="medium"` | Performs initial cross-channel thread decomposition over the **1M Unified Context Window** with a **21,255-token Static Epistemic Constitution Prefix** (activating **95% Implicit Context Caching**). |
| **Stage 3: Adversarial Critic** | `gemini-3.8-flash` | `thinking_level="medium"` | Audits Round 1 draft for circular trap endorsement (**FR05**), account-persona conflation (**FR04**), duplicate inflation (**FR03**), or prohibited numerical probability claims (**FR07**). |
| **Stage 4: Round 2 Self-Repair** | `gemini-4-argon` | `thinking_level="high"` | Repairs all Critic defects, constructs the interactive **Ariadne's Thread Provenance Graph**, and ranks independent out-of-band anchors (`Saved Contacts` -> `112 / 1332 / 118 Registries`). |
| **Stage 5: Privacy Help Packet** | `gemma-4-31b-it` | Open-Weight Companion | Generates a **PII-minimized Third-Party Help Packet (FR10)** scrubbed of personal phone numbers and names for sharing with family members or bank fraud desks. |
| **Stage 6: Multimodal Studio** | `gemini-nano-banana-2.1` + `gemini-3.8-flash-tts` | Image + WAV Audio (`Kore`, `"calm, clear, and reassuring"`) | Generates a high-contrast visual provenance diagram card and a playable, accessible calm voice briefing to de-escalate user panic. |

---

## 3. 7-Pillar Showcase+ User Interface (`index.html`)

1. **Pillar 1 — Named Persona Scenarios & Dual-Mode Execution:**
   - **Min-jun Park (68, Retired Principal):** Family voice clone emergency + KakaoTalk detention wire request.
   - **Ji-yoon Kim (31, UX Designer):** Overseas customs fee + sideloaded `.apk` link + forwarded duplicate + embedded prompt injection.
   - **Sora Han (42, Specialty Coffee Roastery Owner):** Legitimate-looking B2B supplier settlement account update (nuanced false-alarm prevention).
   - Supports both **0.2s Pre-Verified Showcase Mode** and **Live Multi-Model Server-Sent Events (SSE) Streaming Mode**.
2. **Pillar 2 — Scoped Consent Gate (FR01), Multimodal Input & 1M Context Meter:**
   - Explicit opt-in consent gate, multimodal file attachment (`image/*, audio/*, video/*, .pdf, .csv`), 1M token utilization bar (`21,255+ / 1,000,000 tokens`, `95% Implicit Cache Active`), and **FR04 Account ID vs. Claimed Persona Matrix**.
3. **Pillar 3 — Live Multi-Model Orchestration DAG & Telemetry HUD:**
   - Real-time 6-stage pipeline HUD displaying active model delegation and millisecond latency per stage.
4. **Pillar 4 — Interactive HTML5 Canvas "Ariadne's Thread" Graph & Companion Studio:**
   - Draggable/interactive HTML5 Canvas provenance graph (`Observed Fact`, `Unverified Claim`, `Quarantined Circular Trap`, `Independent Out-of-Band Anchor`), `gemini-nano-banana-2.1` visual card, and playable `gemini-3.8-flash-tts` audio player.
5. **Pillar 5 — Autonomous Verification Loop Diff Inspector:**
   - Side-by-side comparison of **Round 1 Initial Draft**, **Adversarial Critic Defects**, **Round 2 Self-Corrected Output**, and the **FR07 Observed vs. Claimed vs. Unverified Claims Ledger**.
6. **Pillar 6 — Mandatory Human-in-the-Loop (HITL) Gate & FR09 Live Re-Evaluation:**
   - Allows the user to input out-of-band verification results (**FR09**) to dynamically recompute the graph via `/api/recompute`, requires explicit HITL approval (**FR08**) before unlocking response actions, and provides one-click **Revoke Consent & Purge Session Data (FR01/FR09)**.
7. **Pillar 7 — Interactive System Architecture & 1M Pipeline Walkthrough Tab:**
   - Built-in architectural briefing and PRD v0.5 traceability matrix (`FR01`–`FR11` & `Section 7`).

---

## 4. Local Setup & Cloud Run Deployment

### Run Locally
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8080
```
Open `http://localhost:8080` in your browser.

### Verify API Endpoints
- `GET /health` — Service health & model registry
- `GET /api/readiness` — Implicit cache token count (`21,255` static tokens) & active model configuration
- `GET /api/presets` — Pre-verified multi-model bundles for all 3 Named Personas
- `POST /api/analyze/stream` — Live Server-Sent Events (SSE) multi-model pipeline
- `POST /api/recompute` — FR09 dynamic epistemic graph re-evaluation upon user correction
- `POST /api/hitl/decision` — Pillar 6 Human-in-the-Loop audit commit & FR01 session data purge
