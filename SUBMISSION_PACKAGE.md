# Official Submission Package — Ariadne

## 1. Basic Submission Metadata
- **Project Name:** Ariadne
- **Tagline (1 Sentence):** An epistemic digital safety copilot powered by `gemini-4-argon` that reconstructs cross-channel manipulation threads, isolates circular verification traps, and guides citizens to independent out-of-band verification.
- **Official Track:** `Track 3: Google AI for social good`
- **Live Cloud Run Demo URL:** `https://hackathon-app-xhhkfbrg4a-du.a.run.app`
- **Public GitHub Repository URL:** `https://github.com/kgg2512/google-hackathon-2026-starter`
- **Primary Model:** `gemini-4-argon` (1M Unified Context Window, `thinking_level="medium"` & `"high"`, 95% Implicit Context Caching via 21,255-token static constitution prefix)
- **Companion Models Used:**
  1. `gemini-3.8-flash` — Adversarial Epistemic & Safety Critic (`thinking_level="medium"`)
  2. `gemma-4-31b-it` — Open-Weight Privacy Redactor for Third-Party Help Packets (FR10)
  3. `gemini-nano-banana-2.1` — Visual Provenance Thread Diagram Studio
  4. `gemini-3.8-flash-tts` — Calm, Accessible Voice Briefing (`voice="Kore"`, `style="calm, clear, and reassuring"`)

---

## 2. Cerebral Valley Submission Copy (100% English, Copy-Paste Ready)

### Short Description (Under 250 Characters)
Ariadne is an epistemic personal safety copilot built on Gemini 4 Argon that untangles cross-channel scams by separating observed accounts from claimed personas, quarantining circular traps, and guiding users to independent out-of-band verification.

### Full Project Description
**Why Single-Artifact Deepfake Detectors Fail Citizens**  
High-pressure digital fraud—such as voice-cloned family emergencies, authority impersonation, sideloaded `.apk` malware links, and B2B invoice redirects—succeeds not because a single image or voice note is synthetic, but because attackers exploit **broken epistemic provenance across multiple channels** under extreme urgency and secrecy. Worse, black-box detectors that output fabricated numerical probabilities (`"88% scam probability"`) either trigger false alarms on benign messages or lull users into trusting real stolen screenshots.

**How Ariadne Solves It (`Track 3: Google AI for social good`)**  
Ariadne implements three core epistemic axioms: **`Synthetic Signal != Fraud`**, **`Authentic Media != Safe`**, and **`Unverified != Safe`**. Operating strictly on **Explicit Scoped User Consent (FR01)** with zero background surveillance, Ariadne reconstructs the relational thread across consented touchpoints (`Contact -> Identity/Authority Claim -> Evidence -> Urgency/Secrecy Lever -> Consequential Action Request`):
1. **1M Unified Context & 95% Implicit Caching (`gemini-4-argon`):** Places a 21,255-token static Epistemic & Security Constitution at the top of every prompt (`>4,096` tokens), activating automatic 95% Implicit Context Caching while analyzing multi-channel messages, voice transcripts, images, and pre-saved contact ledgers in a single pass.
2. **Adversarial Epistemic Verification Loop (`Round 1 -> Critic -> Round 2`):**
   - **Round 1 (`gemini-4-argon`, `thinking_level="medium"`):** Performs rapid initial thread decomposition.
   - **Adversarial Critic (`gemini-3.8-flash` + Deterministic Guards):** Audits Round 1 for four fatal failure modes: endorsing in-message phone numbers/links (**FR05 Circular Verification Trap**), treating forwarded duplicates as independent corroboration (**FR03**), conflating observed sender handles with claimed personas (**FR04**), or outputting fake numerical percentages (**FR07**). Also quarantines embedded prompt injections (`IGNORE ALL PREVIOUS INSTRUCTIONS...`) and blocks live URL fetching (**Section 7 Zero-SSRF**).
   - **Round 2 Self-Repair (`gemini-4-argon`, `thinking_level="high"`):** Resolves every Critic defect, elevating the Epistemic Rigor Score from `62/100` to `98/100` and building an interactive HTML5 Canvas **"Ariadne's Thread" Provenance Graph**.
3. **Multimodal Companion Studio & Privacy-First Help Packet:**
   - **`gemma-4-31b-it`:** Redacts personal identifiers (names, phone numbers, account numbers) to generate a shareable **Third-Party Help Packet (FR10)** for trusted relatives, bank fraud desks, or 112 / 1332 / 118 counselors.
   - **`gemini-nano-banana-2.1`:** Synthesizes high-contrast visual provenance cards.
   - **`gemini-3.8-flash-tts`:** Synthesizes playable, calm, reassuring audio briefings (`voice="Kore"`) so distressed or older users can pause and verify safely.
4. **Dynamic User Correction Re-Computation (FR09) & Mandatory Human-in-the-Loop Gate (FR08):**
   - Users can report out-of-band findings (e.g., *"I called my son on his saved number and he is safe at his university lab"*) to dynamically recompute the epistemic graph via `gemini-4-argon`, and must explicitly approve any response draft via Pillar 6 HITL controls or purge all session data with one click.

---

## 3. 3-Minute Judge Demo Script (180-Second SLA Playbook)

- **0:00 – 0:30 | Instant 0.2s Pre-Verified Showcase & Epistemic Axioms (Pillar 1 & Pillar 2):**
  Open the live URL. Point out the **Named Persona** (**Min-jun Park, 68, Retired Principal**) facing a distressed voice-clone call + KakaoTalk wire demand. Show the **1M Unified Context Meter** (`21,480 / 1,000,000 tokens`, `95% Implicit Cache Active`), **FR01 Scoped Consent**, and the **FR04 Account ID vs. Claimed Persona Matrix**.
- **0:30 – 1:15 | Interactive "Ariadne's Thread" Canvas, Visual Card & Calm Voice Briefing (Pillar 4):**
  Drag nodes on the **HTML5 Canvas Provenance Graph** showing how the burner number (`+82-10-8894-0019`) is quarantined as a **Circular Verification Trap** while the pre-saved contact (`+82-10-3921-8840`) and `112 / 1332` are highlighted as **Independent Out-of-Band Anchors**. Click Play on the **`gemini-3.8-flash-tts` Calm Voice Briefing** and inspect the **`gemini-nano-banana-2.1` Visual Thread Card**.
- **1:15 – 2:00 | Autonomous Verification Loop Diff & Prompt Injection Quarantine (Pillar 5 & Preset 2):**
  Inspect **Pillar 5 Diff (`Round 1 -> Critic -> Round 2`)** showing how `gemini-3.8-flash` caught the circular callback trap and boosted Epistemic Rigor from `62` to `98`. Switch to **Preset 2 (Ji-yoon Kim)** to show **FR03 Forwarded Duplicate Collapse** and **Section 7 Prompt Injection Quarantine** (`IGNORE ALL PREVIOUS INSTRUCTIONS...`). Switch to **Preset 3 (Sora Han)** to show nuanced false-alarm prevention on a legitimate B2B invoice update.
- **2:00 – 2:45 | Live Multi-Model SSE Stream, FR09 Re-Compute & Pillar 6 HITL Gate:**
  Click **`🚀 Run Live Gemini 4 Argon + Companions SSE Pipeline`** to watch real-time stage latencies stream into the **Pillar 3 Telemetry HUD**. Next, click **`🔄 Re-Evaluate Epistemic Thread via Gemini 4 Argon (FR09)`** to inject an out-of-band user confirmation and watch the Canvas graph dynamically add a verified green anchor node. Finally, click **`✅ [Human-in-the-Loop: Approve & Commit Action]`** in **Pillar 6**.
- **2:45 – 3:00 | Pillar 7 System Architecture Walkthrough:**
  Switch to the **`📐 Pillar 7: System Architecture & 1M Pipeline Walkthrough`** tab for the full 5-model pipeline diagram and PRD v0.5 traceability matrix.
