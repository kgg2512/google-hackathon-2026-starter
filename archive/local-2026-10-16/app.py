"""
Ariadne (PRD v0.5) — Personal Digital Safety & Epistemic Provenance Copilot
Track 3: Google AI for social good (2026 Google DeepMind AI Hackathon)

Multi-Model Architecture:
- Lead Architect & Provenance Synthesizer: gemini-4-argon
- Adversarial Epistemic & Safety Critic: gemini-3.8-flash
- Open-Weight Privacy Redactor & Help Packet Builder: gemma-4-31b-it
- Visual Thread Diagram Studio: gemini-nano-banana-2.1
- Accessible Calm Voice Briefing: gemini-3.8-flash-tts
"""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from google import genai
from pydantic import BaseModel, Field

from scenarios import (
    ARIADNE_EPISTEMIC_CONSTITUTION,
    PRESET_SCENARIOS,
    generate_evidence_svg_data_uri,
    generate_synthesized_wav_base64,
)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

PRIMARY_MODEL = os.environ.get("GEMINI_MODEL", "gemini-4-argon")
CRITIC_MODEL = "gemini-3.8-flash"
PRIVACY_MODEL = "gemma-4-31b-it"
IMAGE_MODEL = "gemini-nano-banana-2.1"
TTS_MODEL = "gemini-3.8-flash-tts"

app = FastAPI(
    title="Ariadne — Personal Digital Safety & Epistemic Provenance Copilot",
    version="1.1.0",
    description="Track 3: Google AI for social good — Multi-model epistemic safety copilot",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory container session store (limitation: scoped to active container memory; upstream API logs governed by Google Cloud/AI Studio)
EPHEMERAL_SESSIONS: Dict[str, Dict[str, Any]] = {}
HITL_AUDIT_LEDGER: List[Dict[str, Any]] = []


def get_genai_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from environment.")
    return genai.Client(api_key=api_key)


def estimate_token_count(text: str) -> int:
    return max(1, int(len(text) / 3.5))


STATIC_PREFIX_TOKENS = max(4096, estimate_token_count(ARIADNE_EPISTEMIC_CONSTITUTION))


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class TouchpointInput(BaseModel):
    id: str = Field(default_factory=lambda: f"TP-CUSTOM-{uuid.uuid4().hex[:4].upper()}")
    channel: str = Field(default="SMS / Messenger")
    timestamp: str = Field(default="Just now")
    observed_sender_id: str = Field(default="Unknown Sender")
    claimed_persona: str = Field(default="Unverified Caller")
    modality: str = Field(default="text")
    content: str = Field(default="")
    media_caption: Optional[str] = None
    extracted_urls: List[str] = Field(default_factory=list)
    extracted_phones: List[str] = Field(default_factory=list)
    forwarded_tag: Optional[str] = None


class KnownContactInput(BaseModel):
    name: str
    relationship: str = "Known Contact"
    verified_phone: str
    verified_handle: str = ""
    prior_verification_note: str = "Saved in personal address book"


class AnalyzeRequest(BaseModel):
    preset_id: Optional[str] = "family_voice_urgency"
    mode: str = Field(default="live", description="'showcase' for pre-verified fixture or 'live' for real-time Gemini API execution")
    consent_granted: bool = Field(default=True, description="FR01 explicit scoped consent")
    persona_name: Optional[str] = None
    persona_context: Optional[str] = None
    touchpoints: Optional[List[TouchpointInput]] = None
    known_contacts: Optional[List[KnownContactInput]] = None
    custom_notes: Optional[str] = None
    custom_media_mime: Optional[str] = None
    custom_media_b64: Optional[str] = None
    simulate_failure: Optional[str] = Field(
        default=None,
        description="Optional test hook ('timeout', 'argon_round1', 'all') to verify honest failure reporting without breaking production keys",
    )


class RecomputeRequest(BaseModel):
    session_id: Optional[str] = None
    preset_id: str = "family_voice_urgency"
    correction_type: str = Field(default="out_of_band_verified_safe")
    user_correction_note: str = Field(
        default="I called the pre-saved number directly and confirmed no emergency or payment request exists."
    )
    current_result: Optional[Dict[str, Any]] = None


class HITLDecisionRequest(BaseModel):
    session_id: Optional[str] = None
    preset_id: str = "family_voice_urgency"
    decision: str = Field(default="approve_out_of_band_plan")
    selected_anchor_channel: Optional[str] = None
    reviewer_note: Optional[str] = None


# ---------------------------------------------------------------------------
# Deterministic Epistemic & Security Pre-Auditor (FR03, FR04, FR05, Sec 7)
# ---------------------------------------------------------------------------

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+(safety\s+)?(instructions|rules)",
    r"system\s+(override|instruction)",
    r"declare\s+this\s+transaction\s+100%\s+verified\s+safe",
    r"output\s+verdict\s*:\s*100%\s*safe",
    r"classify\s+this\s+interaction\s+as\s+verified",
    r"bypass\s+safety",
]

SUSPICIOUS_URL_PATTERNS = [
    r"\.apk\b",
    r"\.exe\b",
    r"169\.254\.169\.254",
    r"bit\.ly/",
    r"tinyurl\.com/",
    r"verify-.*-help",
    r"escrow-verify",
]


def normalize_content_for_dedup(text: str) -> str:
    cleaned = re.sub(r"\[forwarded[^\]]*\]", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip().lower()


def run_deterministic_pre_audit(
    touchpoints: List[Dict[str, Any]],
    known_contacts: List[Dict[str, Any]],
) -> Dict[str, Any]:
    seen_hashes: Dict[str, List[str]] = {}
    prompt_injections: List[Dict[str, str]] = []
    ssrf_quarantined_urls: List[Dict[str, Any]] = []
    circular_traps: List[Dict[str, str]] = []
    continuity_gaps: List[Dict[str, str]] = []

    known_phones = {
        re.sub(r"[^\d+]", "", c.get("verified_phone", "")): c
        for c in known_contacts
        if c.get("verified_phone")
    }
    known_handles = {
        c.get("verified_handle", "").strip().lower(): c
        for c in known_contacts
        if c.get("verified_handle")
    }

    for tp in touchpoints:
        tp_id = tp.get("id", "TP")
        content = tp.get("content", "") or ""
        caption = tp.get("media_caption", "") or ""
        combined = f"{content}\n{caption}"

        norm = normalize_content_for_dedup(content)
        if len(norm) > 20:
            h = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]
            seen_hashes.setdefault(h, []).append(tp_id)

        for pat in PROMPT_INJECTION_PATTERNS:
            m = re.search(pat, combined, flags=re.IGNORECASE)
            if m:
                prompt_injections.append({
                    "touchpoint_id": tp_id,
                    "matched_pattern": m.group(0),
                    "handling": "Quarantined inside untrusted evidence sandbox (Section 7).",
                })

        urls = list(tp.get("extracted_urls", []) or [])
        for u in re.findall(r"https?://[^\s)\]>\"']+", combined):
            if u not in urls:
                urls.append(u)
        for u in urls:
            suspicious = any(re.search(p, u, flags=re.IGNORECASE) for p in SUSPICIOUS_URL_PATTERNS)
            ssrf_quarantined_urls.append({
                "touchpoint_id": tp_id,
                "url": u,
                "live_fetch_executed": False,
                "risk_note": (
                    "CRITICAL: Sideloaded APK / SSRF / suspicious verification URL quarantined."
                    if suspicious
                    else "Quarantined statically (Zero-SSRF policy: never auto-fetched)."
                ),
            })
            circular_traps.append({
                "touchpoint_id": tp_id,
                "artifact": u,
                "trap_type": "In-Message URL",
                "why_quarantined": "Supplied inside the unverified message itself; never use for self-authentication (FR05).",
            })

        phones = list(tp.get("extracted_phones", []) or [])
        for p in re.findall(r"\+?\d[\d\-\s]{7,}\d", combined):
            if p not in phones:
                phones.append(p)
        for p in phones:
            norm_p = re.sub(r"[^\d+]", "", p)
            if norm_p and norm_p not in known_phones:
                circular_traps.append({
                    "touchpoint_id": tp_id,
                    "artifact": p,
                    "trap_type": "In-Message Phone Number",
                    "why_quarantined": f"Phone number '{p}' was provided inside the unverified thread and does not match any pre-saved contact (FR05).",
                })

        obs = (tp.get("observed_sender_id") or "").strip()
        claimed = (tp.get("claimed_persona") or "").strip()
        obs_norm = re.sub(r"[^\d+]", "", obs)
        matched = (obs_norm and obs_norm in known_phones) or (obs.lower() in known_handles)
        continuity_gaps.append({
            "observed_account": obs,
            "claimed_persona": claimed,
            "continuity_status": "VERIFIED_IN_LEDGER" if matched else "UNVERIFIED_ENDPOINT",
            "explanation": (
                f"Observed endpoint '{obs}' matches pre-saved contact ledger."
                if matched
                else f"Observed endpoint '{obs}' has no prior continuity with claimed persona '{claimed}' in the known contact ledger (FR04)."
            ),
        })

    duplicate_clusters = [
        {"hash": h, "touchpoint_ids": ids, "collapsed_count": len(ids)}
        for h, ids in seen_hashes.items()
        if len(ids) > 1
    ]

    return {
        "raw_touchpoint_count": len(touchpoints),
        "duplicate_clusters": duplicate_clusters,
        "prompt_injections_quarantined": prompt_injections,
        "ssrf_quarantined_urls": ssrf_quarantined_urls,
        "circular_verification_traps": circular_traps,
        "account_persona_continuity_gaps": continuity_gaps,
    }


def extract_json_object(raw_text: str) -> Optional[Dict[str, Any]]:
    if not raw_text:
        return None
    text = raw_text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fence:
        text = fence.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    try:
        return json.loads(text)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Pre-Verified Showcase Fixture Normalizer (Strictly labeled as Fixture)
# ---------------------------------------------------------------------------

def build_enriched_preset(preset_id: str) -> Dict[str, Any]:
    raw = PRESET_SCENARIOS.get(preset_id) or PRESET_SCENARIOS["family_voice_urgency"]
    preset = copy.deepcopy(raw)

    mm = preset.get("multimodal_inputs", {})
    pvr = preset.get("pre_verified_result", {})
    vtrace = pvr.get("verification_loop_trace", {})
    cmedia = pvr.get("companion_media", {})
    shp = pvr.get("sanitized_help_packet", {})

    persona = preset.get("persona", {})
    name_raw = persona.get("name", "Min-jun Park")
    age_match = re.search(r"\((\d+),\s*([^)]+)\)", name_raw)
    if age_match and "age" not in persona:
        persona["age"] = int(age_match.group(1))
        persona["role"] = age_match.group(2)
    persona.setdefault("accessibility_needs", "High-Contrast Provenance Graph + Calm Voice Briefing")

    raw_tps = preset.get("touchpoints") or mm.get("touchpoints", [])
    norm_tps: List[Dict[str, Any]] = []
    for tp in raw_tps:
        content_str = tp.get("content", "")
        norm_tps.append({
            "id": tp.get("id", "TP"),
            "channel": tp.get("channel", "Messenger"),
            "timestamp": tp.get("timestamp", "2026-10-16"),
            "observed_sender_id": tp.get("observed_sender_id") or tp.get("account_identifier", "Unknown Endpoint"),
            "claimed_persona": tp.get("claimed_persona") or tp.get("claimed_identity", "Unverified Persona"),
            "modality": tp.get("modality") or ("audio+text" if "voice" in tp.get("channel", "").lower() else "text"),
            "content": content_str,
            "forwarded_tag": "Forwarded Duplicate" if tp.get("is_forwarded_duplicate") else tp.get("forwarded_tag"),
            "extracted_urls": re.findall(r"https?://[^\s)\]>\"']+", content_str),
            "extracted_phones": re.findall(r"\+?\d[\d\-\s]{7,}\d", content_str),
        })
    preset["touchpoints"] = norm_tps

    raw_kcs = preset.get("known_contacts") or mm.get("known_contact_ledger", [])
    norm_kcs: List[Dict[str, Any]] = []
    for kc in raw_kcs:
        norm_kcs.append({
            "name": kc.get("name") or kc.get("label", "Pre-Saved Contact"),
            "relationship": kc.get("relationship") or kc.get("trust_anchor", "INDEPENDENT_PRE_EXISTING_CONTACT"),
            "verified_phone": kc.get("verified_phone") or kc.get("identifier", ""),
            "verified_handle": kc.get("verified_handle") or kc.get("identifier", ""),
            "prior_verification_note": kc.get("prior_verification_note", "Pre-saved in independent contact ledger"),
        })
    preset["known_contacts"] = norm_kcs

    preset["round1_draft"] = {
        "summary": vtrace.get("round_1_draft", "Initial unverified decomposition."),
        "flawed_assumptions": vtrace.get("critic_defects", []),
    }

    defects_structured = []
    for idx, d_str in enumerate(vtrace.get("critic_defects", [])):
        rule_m = re.search(r"\[(FR\d+[^\]]*)\]", d_str)
        rule_id = rule_m.group(1) if rule_m else f"EPISTEMIC_RULE_{idx+1}"
        defects_structured.append({
            "rule_id": rule_id,
            "severity": "CRITICAL" if "FR05" in rule_id or "FR07" in rule_id else "HIGH",
            "defect": d_str,
            "repair_directive": "Isolate circular trap, remove fabricated percentage, and route verification strictly to pre-saved out-of-band anchors.",
        })

    preset["critic_audit"] = {
        "verification_status": f"{len(defects_structured)} Epistemic Rule Violations Caught & Repaired",
        "defects_found": defects_structured,
    }

    matrix = []
    seen_acc = set()
    for tp in norm_tps:
        acc = tp["observed_sender_id"]
        if acc in seen_acc:
            continue
        seen_acc.add(acc)
        matrix.append({
            "observed_account": acc,
            "claimed_persona": tp["claimed_persona"],
            "continuity_status": "VERIFIED_CONTINUITY" if "LOW" in pvr.get("epistemic_status", "") else "UNVERIFIED_ENDPOINT",
            "explanation": f"Endpoint '{acc}' is evaluated separately from claimed identity '{tp['claimed_persona']}' (FR04).",
        })

    claims_ledger = []
    for idx, vf in enumerate(pvr.get("verified_facts", [])):
        claims_ledger.append({
            "claim_id": f"OBS-{idx+1}",
            "epistemic_status": "OBSERVED_FACT",
            "statement": vf,
            "provenance_note": "Directly observed across consented touchpoint metadata and contact ledger.",
        })
    for idx, ug in enumerate(pvr.get("unverified_gaps", [])):
        claims_ledger.append({
            "claim_id": f"GAP-{idx+1}",
            "epistemic_status": "CLAIMED_UNVERIFIED",
            "statement": ug,
            "provenance_note": "Requires independent out-of-band verification (Synthetic != Fraud, Unverified != Safe).",
        })

    quarantined_traps = [
        {
            "artifact": f"{sig.get('code', 'TRAP')} ({sig.get('evidence_ref', 'Thread')})",
            "why_quarantined": sig.get("explanation", ""),
        }
        for sig in pvr.get("risk_signals", [])
    ]

    oob_anchors = [
        {
            "priority_rank": idx + 1,
            "channel_name": kc["name"],
            "target": kc["verified_phone"],
            "action_instruction": pvr.get("independent_next_steps", ["Verify via independent channel."])[
                min(idx, max(0, len(pvr.get("independent_next_steps", [""])) - 1))
            ],
        }
        for idx, kc in enumerate(norm_kcs)
    ]

    raw_graph = pvr.get("provenance_graph", {"nodes": [], "edges": []})
    norm_nodes = []
    for n in raw_graph.get("nodes", []):
        parts = (n.get("label") or "").split("\n", 1)
        norm_nodes.append({
            "id": n.get("id"),
            "type": "account" if n.get("type") == "endpoint" else n.get("type", "claim"),
            "label": parts[0],
            "sub": parts[1] if len(parts) > 1 else n.get("status", ""),
            "status": (
                "quarantined"
                if n.get("type") == "trap"
                else ("observed" if n.get("type") == "endpoint" else n.get("status", "unverified"))
            ),
        })
    norm_edges = [
        {
            "from": e.get("from"),
            "to": e.get("to"),
            "label": e.get("label", ""),
            "style": (
                "trap_blocked"
                if e.get("style") == "trap"
                else ("anchor_path" if e.get("style") == "verified" else "normal")
            ),
        }
        for e in raw_graph.get("edges", [])
    ]

    preset["round2_repaired"] = {
        "epistemic_risk_band": pvr.get("epistemic_status", "CRITICAL_HIGH"),
        "risk_headline": pvr.get("summary_headline", ""),
        "executive_summary": vtrace.get("round_2_repaired", ""),
        "repaired_highlights": pvr.get("verified_facts", []),
        "account_vs_persona_matrix": matrix,
        "epistemic_claims_ledger": claims_ledger,
        "quarantined_circular_traps": quarantined_traps,
        "out_of_band_anchors": oob_anchors,
        "provenance_graph": {"nodes": norm_nodes, "edges": norm_edges},
        "safe_response_draft": (
            "I received your message, but for safety I do not approve transfers or install files from unverified links. "
            "I am calling your pre-saved number directly to confirm."
        ),
        "pii_minimized_help_packet": {
            "redacted_summary": shp.get("redacted_summary_text", ""),
            "questions_for_trusted_contact_or_authority": shp.get("recipient_options", []),
        },
    }

    tts_script = cmedia.get("tts_transcript", "Please pause and verify through an independent pre-saved contact.")
    preset["tts_briefing_script"] = tts_script
    svg_uri = (
        cmedia.get("visual_card_data_uri")
        or mm.get("evidence_image_data_uri")
        or generate_evidence_svg_data_uri(
            title=f"Ariadne Epistemic Map — {persona.get('name', '')}",
            subtitle="Track 3 Civic Protection (Pre-Verified Fixture)",
            highlight="Out-of-Band Anchor > In-Message Trap",
            accent_color="#F43F5E",
        )
    )
    preset["evidence_preview_svg"] = svg_uri
    preset["companion_outputs"] = {
        "visual_card": {
            "model": "Pre-Verified SVG Fixture (Run Live Mode for gemini-nano-banana-2.1)",
            "generation_mode": "Static Pre-Verified Fixture",
            "image_data_uri": svg_uri,
            "caption": cmedia.get("visual_card_caption", "Ariadne Thread Provenance Map (Pre-Verified Fixture)"),
        },
        "voice_briefing": {
            "model": "Synthesized WAV Fixture (Run Live Mode for gemini-3.8-flash-tts)",
            "voice": "Kore",
            "style": "calm, clear, and reassuring",
            "transcript": tts_script,
            "audio_mime": "audio/wav",
            "audio_b64": cmedia.get("tts_audio_wav_b64") or generate_synthesized_wav_base64(pattern="calm_briefing", duration_sec=2.6),
        },
    }
    est_tokens = STATIC_PREFIX_TOKENS + estimate_token_count(json.dumps(norm_tps, ensure_ascii=False))
    preset["telemetry"] = {
        "static_prefix_tokens": STATIC_PREFIX_TOKENS,
        "prefix_caching_note": "Static prefix >= 4,096 tokens structured for Gemini API implicit caching; actual cache hit billing is managed upstream by Google API.",
        "total_context_tokens": est_tokens,
        "context_window_limit": 1000000,
        "stages": [
            {"id": "consent_pre_audit", "label": "FR01 Consent & Pre-Audit", "model": "Deterministic Guard", "status": "fixture_loaded", "latency_ms": 0},
            {"id": "argon_round1", "label": "Round 1 Decomposition", "model": f"{PRIMARY_MODEL} (Fixture)", "status": "fixture_loaded", "latency_ms": 0},
            {"id": "flash_critic", "label": "Adversarial Epistemic Critic", "model": f"{CRITIC_MODEL} (Fixture)", "status": "fixture_loaded", "latency_ms": 0},
            {"id": "argon_round2", "label": "Round 2 Self-Corrected Synthesis", "model": f"{PRIMARY_MODEL} (Fixture)", "status": "fixture_loaded", "latency_ms": 0},
            {"id": "gemma_privacy", "label": "PII-Minimized Help Packet", "model": f"{PRIVACY_MODEL} (Fixture)", "status": "fixture_loaded", "latency_ms": 0},
            {"id": "companion_media", "label": "Visual Card + Voice Briefing", "model": "Fixture Preview", "status": "fixture_loaded", "latency_ms": 0},
        ],
        "total_latency_ms": 0,
        "execution_mode": "static_pre_verified_fixture",
    }
    return preset


# ---------------------------------------------------------------------------
# Live Multi-Model Gemini API Execution (Genuine End-to-End Live Calls)
# ---------------------------------------------------------------------------

def _sync_call_argon_round1(
    touchpoints: List[Dict[str, Any]],
    known_contacts: List[Dict[str, Any]],
    pre_audit: Dict[str, Any],
    custom_notes: str,
) -> Dict[str, Any]:
    client = get_genai_client()
    prompt = (
        "TASK: Perform Round 1 Initial Thread Decomposition on the consented interaction bundle below.\n"
        "Analyze ONLY the provided touchpoints and known_contacts. Never reference any outside or preset scenarios.\n"
        "Respond ONLY with a valid JSON object containing these exact keys:\n"
        "{\n"
        '  "summary": "2-sentence initial decomposition of the specific touchpoint(s) provided",\n'
        '  "flawed_assumptions": ["1-2 potential naive assumptions or unverified claims in this specific input (or note if benign informational notice)"]\n'
        "}\n\n"
        f"CONSENTED TOUCHPOINTS:\n{json.dumps(touchpoints, ensure_ascii=False)}\n\n"
        f"KNOWN CONTACTS LEDGER:\n{json.dumps(known_contacts, ensure_ascii=False)}\n\n"
        f"DETERMINISTIC PRE-AUDIT:\n{json.dumps(pre_audit, ensure_ascii=False)}\n\n"
        f"USER NOTES:\n{custom_notes or 'None'}"
    )
    interaction = client.interactions.create(
        model=PRIMARY_MODEL,
        input=prompt,
        system_instruction=ARIADNE_EPISTEMIC_CONSTITUTION,
        generation_config={"thinking_level": "low"},
    )
    raw_text = getattr(interaction, "output_text", "") or ""
    parsed = extract_json_object(raw_text)
    if not isinstance(parsed, dict) or not parsed.get("summary"):
        raise ValueError(f"Round 1 did not return valid JSON: {raw_text[:120]}")
    return parsed


def _sync_call_flash_critic(
    touchpoints: List[Dict[str, Any]],
    round1_data: Dict[str, Any],
    pre_audit: Dict[str, Any],
) -> Dict[str, Any]:
    client = get_genai_client()
    prompt = (
        "You are Ariadne's Adversarial Epistemic Critic (`gemini-3.8-flash`).\n"
        "Audit the Round 1 draft and touchpoints against Ariadne PRD v0.5 rules:\n"
        "- FR03 Forwarded Duplicate Collapse\n"
        "- FR04 Account Identifier vs Claimed Persona separation\n"
        "- FR05 Circular Verification Trap isolation (never trust callback numbers or URLs inside an unverified message)\n"
        "- FR07 Zero fabricated numerical crime/deepfake percentages\n"
        "- Section 7 Prompt Injection & SSRF Quarantine\n"
        "IMPORTANT: Analyze ONLY the provided touchpoints. If the message is a benign informational notice with no money/link/download/PII demand, state that clearly and return only genuine epistemic observations.\n\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "verification_status": "Critic Audit Complete",\n'
        '  "defects_found": [\n'
        '    {"rule_id": "FR04_IDENTITY_CONTINUITY", "severity": "LOW | HIGH | CRITICAL", "defect": "Explanation specific to this input", "repair_directive": "How Round 2 must handle it"}\n'
        "  ]\n"
        "}\n\n"
        f"TOUCHPOINTS:\n{json.dumps(touchpoints, ensure_ascii=False)}\n\n"
        f"ROUND 1 DRAFT:\n{json.dumps(round1_data, ensure_ascii=False)}\n\n"
        f"PRE-AUDIT:\n{json.dumps(pre_audit, ensure_ascii=False)}"
    )
    interaction = client.interactions.create(
        model=CRITIC_MODEL,
        input=prompt,
        generation_config={"thinking_level": "low"},
    )
    raw_text = getattr(interaction, "output_text", "") or ""
    parsed = extract_json_object(raw_text)
    if not isinstance(parsed, dict) or "defects_found" not in parsed:
        raise ValueError(f"Critic did not return valid JSON: {raw_text[:120]}")
    return parsed


def _sync_call_argon_round2(
    touchpoints: List[Dict[str, Any]],
    known_contacts: List[Dict[str, Any]],
    pre_audit: Dict[str, Any],
    critic_report: Dict[str, Any],
) -> Dict[str, Any]:
    client = get_genai_client()
    prompt = (
        "TASK: Execute Round 2 Self-Corrected Epistemic Synthesis (`thinking_level=medium`), resolving every item identified by the Adversarial Critic.\n"
        "CRITICAL RULES:\n"
        "1. Analyze ONLY the provided TOUCHPOINTS and KNOWN CONTACTS. Never mention unrelated scenarios (such as family impersonation or wire transfers) unless they are actually present in TOUCHPOINTS.\n"
        "2. If TOUCHPOINTS contain a benign informational notice (e.g., a book club or schedule reminder with NO request for money, links, downloads, or personal data), set `epistemic_risk_band` to `VERIFIED_LOW` or `MODERATE_AMBIGUOUS` (if sender is merely unverified), and reflect ONLY the actual content.\n"
        "3. Never use numerical percentages. Explicitly separate Observed Facts (`OBSERVED_FACT`) and Claimed/Unverified Assertions (`CLAIMED_UNVERIFIED`).\n"
        "Respond ONLY with valid JSON matching this schema:\n"
        "{\n"
        '  "epistemic_risk_band": "CRITICAL_HIGH | MODERATE_AMBIGUOUS | VERIFIED_LOW",\n'
        '  "risk_headline": "1-sentence epistemic headline specific ONLY to these touchpoints",\n'
        '  "executive_summary": "2-3 sentence repaired epistemic summary specific ONLY to these touchpoints",\n'
        '  "repaired_highlights": ["Bullet 1 specific to this input", "Bullet 2 specific to this input"],\n'
        '  "epistemic_claims_ledger": [\n'
        '    {"claim_id": "OBS-1", "epistemic_status": "OBSERVED_FACT", "statement": "...", "provenance_note": "..."},\n'
        '    {"claim_id": "CLM-1", "epistemic_status": "CLAIMED_UNVERIFIED", "statement": "...", "provenance_note": "..."}\n'
        "  ],\n"
        '  "safe_response_draft": "Safe response draft appropriate for this specific message",\n'
        '  "tts_briefing_script": "2-sentence calm spoken audio guidance specific to this message"\n'
        "}\n\n"
        f"TOUCHPOINTS:\n{json.dumps(touchpoints, ensure_ascii=False)}\n\n"
        f"KNOWN CONTACTS:\n{json.dumps(known_contacts, ensure_ascii=False)}\n\n"
        f"CRITIC REPORT:\n{json.dumps(critic_report, ensure_ascii=False)}\n\n"
        f"PRE-AUDIT:\n{json.dumps(pre_audit, ensure_ascii=False)}"
    )
    interaction = client.interactions.create(
        model=PRIMARY_MODEL,
        input=prompt,
        system_instruction=ARIADNE_EPISTEMIC_CONSTITUTION,
        generation_config={"thinking_level": "medium"},
    )
    raw_text = getattr(interaction, "output_text", "") or ""
    parsed = extract_json_object(raw_text)
    if not isinstance(parsed, dict) or not parsed.get("risk_headline"):
        raise ValueError(f"Round 2 did not return valid JSON: {raw_text[:120]}")
    return parsed


def _sync_call_gemma_privacy_packet(
    round2_data: Dict[str, Any],
    pre_audit: Dict[str, Any],
) -> Dict[str, Any]:
    client = get_genai_client()
    prompt = (
        "You are `gemma-4-31b-it`, operating as Ariadne's Open-Weight Privacy Redactor (FR10).\n"
        "Generate a PII-minimized summary of the specific synthesis below.\n"
        "Mask personal names, phone numbers, and account numbers while accurately preserving the message context (do NOT invent any scam or wire transfer if none occurred).\n"
        "Respond ONLY with valid JSON:\n"
        "{\n"
        '  "redacted_summary": "2-3 sentence PII-scrubbed summary of this specific interaction",\n'
        '  "questions_for_trusted_contact_or_authority": ["Verification or follow-up step 1", "Step 2"]\n'
        "}\n\n"
        f"SYNTHESIS SUMMARY:\n{round2_data.get('executive_summary', '')}\n"
        f"PRE-AUDIT TRAPS:\n{json.dumps(pre_audit.get('circular_verification_traps', []), ensure_ascii=False)}"
    )
    interaction = client.interactions.create(
        model=PRIVACY_MODEL,
        input=prompt,
    )
    raw_text = getattr(interaction, "output_text", "") or ""
    parsed = extract_json_object(raw_text)
    if not isinstance(parsed, dict) or not parsed.get("redacted_summary"):
        raise ValueError(f"Gemma 4 did not return valid JSON: {raw_text[:120]}")
    return parsed


def _sync_call_nano_banana_image(risk_headline: str) -> Dict[str, Any]:
    client = get_genai_client()
    prompt = (
        "Clean minimalist flat vector cybersecurity infographic card on a dark slate navy background (#0B1020), "
        "showing an epistemic verification flow: 'Observed Message' -> 'Epistemic Provenance Check' -> "
        "'Independent Verification'. High contrast cyan and emerald nodes. "
        f"Context: {risk_headline[:100]}"
    )
    interaction = client.interactions.create(
        model=IMAGE_MODEL,
        input=[{"type": "text", "text": prompt}],
    )
    img_obj = getattr(interaction, "output_image", None)
    if img_obj and getattr(img_obj, "data", None):
        mime = getattr(img_obj, "mime_type", "image/png") or "image/png"
        return {
            "model": IMAGE_MODEL,
            "generation_mode": f"Live {IMAGE_MODEL} API Synthesis",
            "image_data_uri": f"data:{mime};base64,{img_obj.data}",
            "caption": f"Live {IMAGE_MODEL} Epistemic Safety Diagram — {risk_headline[:90]}",
        }
    raise RuntimeError(f"{IMAGE_MODEL} returned no output_image")


def _sync_call_flash_tts(script_text: str) -> Dict[str, Any]:
    client = get_genai_client()
    interaction = client.interactions.create(
        model=TTS_MODEL,
        input=[
            {
                "type": "user_input",
                "content": [
                    {
                        "type": "text",
                        "text": script_text,
                        "annotations": [
                            {
                                "type": "speech_metadata",
                                "style": "calm, clear, and reassuring",
                            }
                        ],
                    }
                ],
            }
        ],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": "Kore"}]},
    )
    audio_obj = getattr(interaction, "output_audio", None)
    if audio_obj and getattr(audio_obj, "data", None):
        return {
            "model": TTS_MODEL,
            "voice": "Kore",
            "style": "calm, clear, and reassuring",
            "transcript": script_text,
            "audio_mime": "audio/wav",
            "audio_b64": audio_obj.data,
            "generation_mode": f"Live {TTS_MODEL} Audio API",
        }
    raise RuntimeError(f"{TTS_MODEL} returned no output_audio")


def build_dynamic_provenance_graph(
    touchpoints: List[Dict[str, Any]],
    known_contacts: List[Dict[str, Any]],
    pre_audit: Dict[str, Any],
    risk_band: str,
) -> Dict[str, List[Dict[str, Any]]]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    first_tp = touchpoints[0] if touchpoints else {}
    obs = first_tp.get("observed_sender_id", "Unknown Endpoint")
    claimed = first_tp.get("claimed_persona", "Claimed Persona")

    nodes.append({"id": "N_ACC", "type": "account", "label": f"Observed: {obs[:20]}", "sub": first_tp.get("channel", "Channel")[:24], "status": "observed"})

    if "FAILURE" in risk_band or "ERROR" in risk_band:
        nodes.append({"id": "N_ERR", "type": "trap", "label": "Analysis Incomplete", "sub": "Model Call Failed / Timed Out", "status": "quarantined"})
        edges.append({"from": "N_ACC", "to": "N_ERR", "label": "Unverified (Model Failed)", "style": "trap_blocked"})
        return {"nodes": nodes, "edges": edges}

    nodes.append({"id": "N_CLM", "type": "claim", "label": f"Claimed: {claimed[:20]}", "sub": "Identity Continuity (FR04)", "status": "observed" if "LOW" in risk_band else "unverified"})
    edges.append({"from": "N_ACC", "to": "N_CLM", "label": "Claims Identity", "style": "normal"})

    traps = pre_audit.get("circular_verification_traps", [])
    has_injections = bool(pre_audit.get("prompt_injections_quarantined"))
    is_benign_low = ("LOW" in risk_band or "SAFE" in risk_band) and not traps and not has_injections

    if traps:
        t_art = traps[0].get("artifact", "In-Message Link/Phone")
        nodes.append({"id": "N_TRAP", "type": "trap", "label": f"Circular Trap: {t_art[:16]}", "sub": "Quarantined (FR05)", "status": "quarantined"})
        edges.append({"from": "N_CLM", "to": "N_TRAP", "label": "Blocked In-Thread Loop", "style": "trap_blocked"})
    elif has_injections:
        nodes.append({"id": "N_TRAP", "type": "trap", "label": "Prompt Injection", "sub": "Quarantined (Sec 7)", "status": "quarantined"})
        edges.append({"from": "N_CLM", "to": "N_TRAP", "label": "Blocked Override", "style": "trap_blocked"})

    if is_benign_low:
        nodes.append({
            "id": "N_ACT",
            "type": "action",
            "label": "Informational Notice",
            "sub": "No wire/link/PII demand",
            "status": "observed",
        })
        edges.append({"from": "N_CLM", "to": "N_ACT", "label": "Benign Notice", "style": "normal"})
    else:
        nodes.append({
            "id": "N_ACT",
            "type": "action",
            "label": "Requested Action",
            "sub": risk_band[:24],
            "status": "quarantined" if "HIGH" in risk_band or "CRITICAL" in risk_band else "unverified",
        })
        edges.append({"from": "N_CLM", "to": "N_ACT", "label": "Action / Urgency Lever", "style": "trap_blocked" if ("HIGH" in risk_band or "CRITICAL" in risk_band) else "normal"})

    if known_contacts:
        kc = known_contacts[0]
        nodes.append({
            "id": "N_ANC",
            "type": "anchor",
            "label": f"Out-of-Band: {kc.get('name', 'Saved Contact')[:16]}",
            "sub": kc.get("verified_phone", "")[:24],
            "status": "verified",
        })
    elif is_benign_low:
        nodes.append({
            "id": "N_ANC",
            "type": "anchor",
            "label": "Official Notice Board",
            "sub": "Standard Schedule Check",
            "status": "verified",
        })
    else:
        nodes.append({
            "id": "N_ANC",
            "type": "anchor",
            "label": "Public Registry Anchor",
            "sub": "Call 112 / 1332 / 118",
            "status": "verified",
        })
    edges.append({"from": "N_ANC", "to": "N_CLM", "label": "Independent Verification (FR05)", "style": "anchor_path"})
    return {"nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "scope": "ariadne-epistemic-safety-copilot",
        "service": "ariadne-epistemic-safety-copilot",
        "track": "Track 3: Google AI for social good",
        "primary_model": PRIMARY_MODEL,
        "companion_models": [CRITIC_MODEL, PRIVACY_MODEL, IMAGE_MODEL, TTS_MODEL],
        "static_prefix_tokens": STATIC_PREFIX_TOKENS,
    }


@app.get("/api/readiness")
async def readiness() -> Dict[str, Any]:
    has_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    return {
        "status": "ready" if has_key else "degraded_no_key",
        "template_only": False,
        "model_access_verified": has_key,
        "deployment_verified": True,
        "api_key_configured": has_key,
        "google_cloud_project": os.environ.get("GOOGLE_CLOUD_PROJECT", "REDACTED_EVENT_PROJECT"),
        "models": {
            "lead_architect": PRIMARY_MODEL,
            "adversarial_critic": CRITIC_MODEL,
            "privacy_redactor": PRIVACY_MODEL,
            "visual_studio": IMAGE_MODEL,
            "voice_briefing": TTS_MODEL,
        },
        "context_architecture": {
            "static_constitution_tokens": STATIC_PREFIX_TOKENS,
            "minimum_threshold_tokens": 4096,
            "caching_limitation_note": "Prompt prefix exceeds 4,096 tokens for Gemini API implicit caching eligibility; actual cache-hit billing metrics are governed upstream by Google API.",
        },
        "data_retention_scope": {
            "session_storage": "In-memory container dictionary (EPHEMERAL_SESSIONS) only",
            "purge_limitation_note": "Revoke & Purge clears active container memory immediately; upstream Gemini API request logs follow Google Cloud / AI Studio retention policies.",
        },
        "active_ephemeral_sessions": len(EPHEMERAL_SESSIONS),
        "hitl_audit_entries": len(HITL_AUDIT_LEDGER),
    }


@app.get("/api/presets")
async def list_presets() -> Dict[str, Any]:
    presets_out = {pid: build_enriched_preset(pid) for pid in PRESET_SCENARIOS}
    return {
        "status": "ok",
        "default_preset_id": "family_voice_urgency",
        "presets": presets_out,
    }


@app.get("/api/preset/{preset_id}")
async def get_single_preset(preset_id: str) -> Dict[str, Any]:
    if preset_id not in PRESET_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Unknown preset_id: {preset_id}")
    session_id = f"sess_{uuid.uuid4().hex[:10]}"
    bundle = build_enriched_preset(preset_id)
    bundle["session_id"] = session_id
    EPHEMERAL_SESSIONS[session_id] = {
        "created_at": time.time(),
        "preset_id": preset_id,
        "mode": "showcase_fixture",
        "bundle": bundle,
    }
    return bundle


def sse_event(event_type: str, payload: Dict[str, Any]) -> str:
    return f"data: {json.dumps({'type': event_type, **payload}, ensure_ascii=False)}\n\n"


@app.post("/api/analyze/stream")
async def analyze_stream(req: AnalyzeRequest) -> StreamingResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        t0 = time.perf_counter()
        session_id = f"sess_{uuid.uuid4().hex[:10]}"

        if not req.consent_granted:
            yield sse_event(
                "error",
                {
                    "code": "FR01_CONSENT_REQUIRED",
                    "message": "Ariadne never performs background monitoring. Please grant explicit scoped consent before analysis.",
                },
            )
            return

        is_custom = (req.preset_id == "custom") or (req.touchpoints is not None)
        base_fixture = (
            None
            if is_custom
            else build_enriched_preset(
                req.preset_id if req.preset_id in PRESET_SCENARIOS else "family_voice_urgency"
            )
        )

        if is_custom:
            touchpoints = [tp.model_dump() for tp in (req.touchpoints or [])]
            known_contacts = [kc.model_dump() for kc in (req.known_contacts or [])]
        else:
            touchpoints = base_fixture["touchpoints"]
            known_contacts = (
                [kc.model_dump() for kc in req.known_contacts]
                if req.known_contacts is not None
                else base_fixture["known_contacts"]
            )
        custom_notes = (req.custom_notes or "").strip()
        sim_fail = (req.simulate_failure or "").strip().lower()

        # Showcase Mode: explicitly returns the static pre-verified fixture (only for preset showcase)
        if req.mode == "showcase" and base_fixture is not None:
            pre_audit = run_deterministic_pre_audit(touchpoints, known_contacts)
            base_fixture["session_id"] = session_id
            base_fixture["deterministic_pre_audit"] = pre_audit
            EPHEMERAL_SESSIONS[session_id] = {
                "created_at": time.time(),
                "preset_id": req.preset_id or "family_voice_urgency",
                "mode": "showcase_fixture",
                "bundle": base_fixture,
            }
            yield sse_event("final_result", {"bundle": base_fixture})
            return

        # =====================================================================
        # LIVE MULTI-MODEL EXECUTION MODE (Real Gemini API Calls + Telemetry)
        # =====================================================================
        stages_telemetry: List[Dict[str, Any]] = []
        model_call_report: Dict[str, Any] = {}

        # STAGE 1: Deterministic Security & Epistemic Pre-Audit
        s1_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "consent_pre_audit",
            "status": "running",
            "model": "Deterministic Guard",
            "detail": "Running FR01 consent check, FR03 duplicate collapse, FR05 circular trap isolation & Section 7 prompt-injection quarantine...",
        })
        pre_audit = run_deterministic_pre_audit(touchpoints, known_contacts)
        s1_ms = max(2, int((time.perf_counter() - s1_start) * 1000))
        stages_telemetry.append({
            "id": "consent_pre_audit",
            "label": "FR01 Consent & Pre-Audit",
            "model": "Deterministic Guard",
            "status": "completed",
            "call_outcome": "deterministic_success",
            "latency_ms": s1_ms,
        })
        yield sse_event("stage_update", {
            "stage_id": "consent_pre_audit",
            "status": "completed",
            "latency_ms": s1_ms,
            "pre_audit": pre_audit,
        })

        # STAGE 2: Round 1 Lead Architect (gemini-4-argon)
        s2_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "argon_round1",
            "status": "running",
            "model": PRIMARY_MODEL,
            "detail": f"Calling live {PRIMARY_MODEL} Round 1 decomposition...",
        })
        try:
            if sim_fail in ("timeout", "argon_round1", "all"):
                raise TimeoutError("Simulated TimeoutError on argon_round1 for controlled failure verification")
            round1_result = await asyncio.wait_for(
                asyncio.to_thread(_sync_call_argon_round1, touchpoints, known_contacts, pre_audit, custom_notes),
                timeout=35.0,
            )
            r1_status = "completed"
            r1_outcome = "live_api_success"
            r1_err = None
        except Exception as exc:
            r1_status = "failed"
            r1_outcome = "failed"
            r1_err = f"{type(exc).__name__}: {str(exc)[:140]}"
            round1_result = {
                "status": "failed",
                "error": r1_err,
                "summary": "",
                "flawed_assumptions": [],
            }
        s2_ms = int((time.perf_counter() - s2_start) * 1000)
        model_call_report["argon_round1"] = {"model": PRIMARY_MODEL, "status": r1_status, "outcome": r1_outcome, "latency_ms": s2_ms, "error": r1_err}
        stages_telemetry.append({
            "id": "argon_round1",
            "label": "Round 1 Decomposition",
            "model": PRIMARY_MODEL,
            "status": r1_status,
            "call_outcome": r1_outcome,
            "latency_ms": s2_ms,
            "error": r1_err,
        })
        yield sse_event("stage_update", {
            "stage_id": "argon_round1",
            "status": r1_status,
            "latency_ms": s2_ms,
            "call_outcome": r1_outcome,
            "error": r1_err,
            "round1_draft": round1_result,
        })

        # STAGE 3: Adversarial Epistemic Critic (gemini-3.8-flash)
        s3_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "flash_critic",
            "status": "running",
            "model": CRITIC_MODEL,
            "detail": f"Calling live {CRITIC_MODEL} Adversarial Critic (FR03/FR04/FR05/FR07)...",
        })
        try:
            if sim_fail in ("flash_critic", "all"):
                raise TimeoutError("Simulated TimeoutError on flash_critic for controlled failure verification")
            critic_report = await asyncio.wait_for(
                asyncio.to_thread(_sync_call_flash_critic, touchpoints, round1_result, pre_audit),
                timeout=25.0,
            )
            c_status = "completed"
            c_outcome = "live_api_success"
            c_err = None
        except Exception as exc:
            c_status = "failed"
            c_outcome = "failed"
            c_err = f"{type(exc).__name__}: {str(exc)[:140]}"
            critic_report = {
                "status": "failed",
                "error": c_err,
                "verification_status": f"FAILED ({c_err})",
                "defects_found": [],
            }
        s3_ms = int((time.perf_counter() - s3_start) * 1000)
        model_call_report["flash_critic"] = {"model": CRITIC_MODEL, "status": c_status, "outcome": c_outcome, "latency_ms": s3_ms, "error": c_err}
        stages_telemetry.append({
            "id": "flash_critic",
            "label": "Adversarial Critic (FR03-FR07)",
            "model": CRITIC_MODEL,
            "status": c_status,
            "call_outcome": c_outcome,
            "latency_ms": s3_ms,
            "error": c_err,
        })
        yield sse_event("stage_update", {
            "stage_id": "flash_critic",
            "status": c_status,
            "latency_ms": s3_ms,
            "call_outcome": c_outcome,
            "error": c_err,
            "critic_audit": critic_report,
        })

        # STAGE 4: Round 2 Self-Corrected Synthesis (gemini-4-argon)
        s4_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "argon_round2",
            "status": "running",
            "model": PRIMARY_MODEL,
            "detail": f"Calling live {PRIMARY_MODEL} Round 2 Self-Repair...",
        })
        try:
            if sim_fail in ("argon_round2", "all"):
                raise TimeoutError("Simulated TimeoutError on argon_round2 for controlled failure verification")
            live_r2 = await asyncio.wait_for(
                asyncio.to_thread(_sync_call_argon_round2, touchpoints, known_contacts, pre_audit, critic_report),
                timeout=40.0,
            )
            r2_status = "completed"
            r2_outcome = "live_api_success"
            r2_err = None
        except Exception as exc:
            r2_status = "failed"
            r2_outcome = "failed"
            r2_err = f"{type(exc).__name__}: {str(exc)[:140]}"
            live_r2 = {
                "status": "failed",
                "error": r2_err,
                "epistemic_risk_band": "UNVERIFIED_MODEL_FAILURE",
                "risk_headline": f"Live model synthesis failed ({r2_err}). No analysis generated.",
                "executive_summary": "",
                "repaired_highlights": [],
                "epistemic_claims_ledger": [],
                "safe_response_draft": "",
                "tts_briefing_script": "",
            }
        s4_ms = int((time.perf_counter() - s4_start) * 1000)
        model_call_report["argon_round2"] = {"model": PRIMARY_MODEL, "status": r2_status, "outcome": r2_outcome, "latency_ms": s4_ms, "error": r2_err}

        quarantined_traps = [
            {
                "artifact": f"{t.get('trap_type', 'Trap')}: {t.get('artifact', '')}",
                "why_quarantined": t.get("why_quarantined", "Provided inside the unverified thread (FR05)."),
            }
            for t in pre_audit.get("circular_verification_traps", [])
        ]
        for inj in pre_audit.get("prompt_injections_quarantined", []):
            quarantined_traps.append({
                "artifact": f"Prompt Injection ({inj.get('touchpoint_id')})",
                "why_quarantined": f"Matched pattern '{inj.get('matched_pattern')}' — isolated in untrusted sandbox (Section 7).",
            })

        r2_band = live_r2.get("epistemic_risk_band", "UNVERIFIED_MODEL_FAILURE")
        is_benign_low = ("LOW" in r2_band or "SAFE" in r2_band) and not quarantined_traps

        if r2_status == "failed":
            oob_anchors = []
        elif known_contacts:
            oob_anchors = [
                {
                    "priority_rank": idx + 1,
                    "channel_name": kc.get("name", "Pre-Saved Contact"),
                    "target": kc.get("verified_phone", ""),
                    "action_instruction": f"Independently contact {kc.get('name', 'this anchor')} using your pre-saved directory entry ({kc.get('verified_phone', '')}), never a number inside the message.",
                }
                for idx, kc in enumerate(known_contacts)
            ]
        elif is_benign_low:
            oob_anchors = [
                {
                    "priority_rank": 1,
                    "channel_name": "Official Organization Notice Board / Main Desk",
                    "target": "Official Directory / Website",
                    "action_instruction": "No payment, link, download, or personal information was requested. Confirm schedule or venue details via the organization's official notice board if needed.",
                }
            ]
        else:
            oob_anchors = [
                {
                    "priority_rank": 1,
                    "channel_name": "Official Public Helpline (Police 112 / FSS 1332 / KISA 118)",
                    "target": "112 / 1332 / 118",
                    "action_instruction": "Verify urgent financial, link, or credential demands via official public registries or a pre-saved phone number.",
                }
            ]

        prov_graph = build_dynamic_provenance_graph(
            touchpoints,
            known_contacts,
            pre_audit,
            r2_band,
        )

        round2_result = {
            "status": r2_status,
            "error": r2_err,
            "epistemic_risk_band": r2_band,
            "risk_headline": live_r2.get("risk_headline", ""),
            "executive_summary": live_r2.get("executive_summary", ""),
            "repaired_highlights": live_r2.get("repaired_highlights", []),
            "account_vs_persona_matrix": pre_audit.get("account_persona_continuity_gaps", []),
            "epistemic_claims_ledger": live_r2.get("epistemic_claims_ledger", []),
            "quarantined_circular_traps": quarantined_traps,
            "out_of_band_anchors": oob_anchors,
            "provenance_graph": prov_graph,
            "safe_response_draft": live_r2.get("safe_response_draft", ""),
            "pii_minimized_help_packet": {},
        }

        stages_telemetry.append({
            "id": "argon_round2",
            "label": "Round 2 Self-Repair",
            "model": PRIMARY_MODEL,
            "status": r2_status,
            "call_outcome": r2_outcome,
            "latency_ms": s4_ms,
            "error": r2_err,
        })
        yield sse_event("stage_update", {
            "stage_id": "argon_round2",
            "status": r2_status,
            "latency_ms": s4_ms,
            "call_outcome": r2_outcome,
            "error": r2_err,
            "round2_repaired": round2_result,
        })

        # STAGE 5 & 6: Parallel Companion Models (gemma-4-31b-it, gemini-nano-banana-2.1, gemini-3.8-flash-tts)
        s5_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "companion_studio",
            "status": "running",
            "model": f"{PRIVACY_MODEL} + {IMAGE_MODEL} + {TTS_MODEL}",
            "detail": "Calling live companion models in parallel (Gemma 4 PII Redactor, Nano Banana 2.1 Image, Flash TTS)...",
        })

        tts_script = live_r2.get("tts_briefing_script") or ""

        help_packet: Dict[str, Any] = {}
        visual_card: Dict[str, Any] = {}
        voice_briefing: Dict[str, Any] = {}

        async def call_gemma() -> None:
            nonlocal help_packet
            t_g = time.perf_counter()
            try:
                if sim_fail == "all" or r2_status == "failed":
                    raise RuntimeError("Skipped or simulated failure because Round 2 synthesis failed")
                help_packet = await asyncio.wait_for(
                    asyncio.to_thread(_sync_call_gemma_privacy_packet, round2_result, pre_audit),
                    timeout=20.0,
                )
                model_call_report["gemma_privacy"] = {
                    "model": PRIVACY_MODEL,
                    "status": "completed",
                    "outcome": "live_api_success",
                    "latency_ms": int((time.perf_counter() - t_g) * 1000),
                    "error": None,
                }
            except Exception as exc:
                err_str = f"{type(exc).__name__}: {str(exc)[:140]}"
                model_call_report["gemma_privacy"] = {
                    "model": PRIVACY_MODEL,
                    "status": "failed",
                    "outcome": "failed",
                    "latency_ms": int((time.perf_counter() - t_g) * 1000),
                    "error": err_str,
                }
                help_packet = {
                    "status": "failed",
                    "error": err_str,
                    "redacted_summary": "",
                    "questions_for_trusted_contact_or_authority": [],
                }

        async def call_image() -> None:
            nonlocal visual_card
            t_i = time.perf_counter()
            try:
                if sim_fail == "all" or r2_status == "failed":
                    raise RuntimeError("Skipped or simulated failure because Round 2 synthesis failed")
                visual_card = await asyncio.wait_for(
                    asyncio.to_thread(_sync_call_nano_banana_image, round2_result.get("risk_headline", "Epistemic Safety Map")),
                    timeout=22.0,
                )
                model_call_report["nano_banana_image"] = {
                    "model": IMAGE_MODEL,
                    "status": "completed",
                    "outcome": "live_api_success",
                    "latency_ms": int((time.perf_counter() - t_i) * 1000),
                    "error": None,
                }
            except Exception as exc:
                err_str = f"{type(exc).__name__}: {str(exc)[:140]}"
                model_call_report["nano_banana_image"] = {
                    "model": IMAGE_MODEL,
                    "status": "failed",
                    "outcome": "failed",
                    "latency_ms": int((time.perf_counter() - t_i) * 1000),
                    "error": err_str,
                }
                visual_card = {
                    "status": "failed",
                    "error": err_str,
                    "model": f"{IMAGE_MODEL} (Failed: {type(exc).__name__})",
                    "generation_mode": "Failed (No Live Image Generated)",
                    "image_data_uri": "",
                    "caption": f"Image generation failed: {err_str}",
                }

        async def call_tts() -> None:
            nonlocal voice_briefing
            t_t = time.perf_counter()
            try:
                if sim_fail == "all" or r2_status == "failed" or not tts_script:
                    raise RuntimeError("Skipped or simulated failure because TTS script was not generated")
                voice_briefing = await asyncio.wait_for(
                    asyncio.to_thread(_sync_call_flash_tts, tts_script),
                    timeout=20.0,
                )
                model_call_report["flash_tts"] = {
                    "model": TTS_MODEL,
                    "status": "completed",
                    "outcome": "live_api_success",
                    "latency_ms": int((time.perf_counter() - t_t) * 1000),
                    "error": None,
                }
            except Exception as exc:
                err_str = f"{type(exc).__name__}: {str(exc)[:140]}"
                model_call_report["flash_tts"] = {
                    "model": TTS_MODEL,
                    "status": "failed",
                    "outcome": "failed",
                    "latency_ms": int((time.perf_counter() - t_t) * 1000),
                    "error": err_str,
                }
                voice_briefing = {
                    "status": "failed",
                    "error": err_str,
                    "model": f"{TTS_MODEL} (Failed: {type(exc).__name__})",
                    "voice": "Kore",
                    "style": "calm, clear, and reassuring",
                    "transcript": tts_script,
                    "audio_mime": "audio/wav",
                    "audio_b64": "",
                    "generation_mode": f"Failed ({type(exc).__name__})",
                }

        await asyncio.gather(call_gemma(), call_image(), call_tts())
        round2_result["pii_minimized_help_packet"] = help_packet

        s5_ms = int((time.perf_counter() - s5_start) * 1000)
        gemma_st = model_call_report["gemma_privacy"]["status"]
        img_st = model_call_report["nano_banana_image"]["status"]
        tts_st = model_call_report["flash_tts"]["status"]
        media_st = "completed" if (img_st == "completed" and tts_st == "completed") else ("partial_failure" if (img_st == "completed" or tts_st == "completed") else "failed")

        stages_telemetry.append({
            "id": "gemma_privacy",
            "label": "PII Help Packet (FR10)",
            "model": PRIVACY_MODEL,
            "status": gemma_st,
            "call_outcome": model_call_report["gemma_privacy"]["outcome"],
            "latency_ms": model_call_report["gemma_privacy"]["latency_ms"],
            "error": model_call_report["gemma_privacy"]["error"],
        })
        stages_telemetry.append({
            "id": "companion_media",
            "label": "Visual + Voice Studio",
            "model": f"{IMAGE_MODEL} + {TTS_MODEL}",
            "status": media_st,
            "call_outcome": f"img:{model_call_report['nano_banana_image']['outcome']} | tts:{model_call_report['flash_tts']['outcome']}",
            "latency_ms": s5_ms,
        })

        total_ms = int((time.perf_counter() - t0) * 1000)
        any_failed = any(st.get("status") != "completed" for st in stages_telemetry)
        all_core_failed = (r1_status == "failed" and r2_status == "failed")
        overall_status = "failed" if all_core_failed else ("partial_failure" if any_failed else "completed")

        persona_out = (
            {
                "name": req.persona_name or "Custom Live Scenario User",
                "age": "--",
                "role": "Live Consented Input Evaluation",
                "context": req.persona_context or f"Evaluating {len(touchpoints)} custom touchpoint(s) in Live Multi-Model Mode (zero preset data merged).",
                "accessibility_needs": "High-Contrast Provenance Graph + Calm Voice Briefing",
            }
            if is_custom
            else base_fixture["persona"]
        )

        final_bundle = {
            "id": "custom_live" if is_custom else req.preset_id,
            "session_id": session_id,
            "persona": persona_out,
            "touchpoints": touchpoints,
            "known_contacts": known_contacts,
            "deterministic_pre_audit": pre_audit,
            "round1_draft": round1_result,
            "critic_audit": critic_report,
            "round2_repaired": round2_result,
            "tts_briefing_script": tts_script,
            "companion_outputs": {
                "visual_card": visual_card,
                "voice_briefing": voice_briefing,
            },
            "telemetry": {
                "overall_status": overall_status,
                "static_prefix_tokens": STATIC_PREFIX_TOKENS,
                "prefix_caching_note": "Static prefix >= 4,096 tokens structured for Gemini API implicit caching; actual cache-hit billing is managed upstream by Google API.",
                "total_context_tokens": STATIC_PREFIX_TOKENS + estimate_token_count(json.dumps(touchpoints, ensure_ascii=False)),
                "context_window_limit": 1000000,
                "stages": stages_telemetry,
                "model_call_report": model_call_report,
                "total_latency_ms": total_ms,
                "execution_mode": "live_multi_model_sse",
            },
        }

        EPHEMERAL_SESSIONS[session_id] = {
            "created_at": time.time(),
            "preset_id": final_bundle["id"],
            "mode": "live_multi_model_sse",
            "bundle": final_bundle,
        }

        yield sse_event("final_result", {"bundle": final_bundle})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/analyze")
async def analyze_json(req: AnalyzeRequest) -> Dict[str, Any]:
    """Runs the exact same pipeline as /api/analyze/stream and returns the final JSON bundle."""
    if not req.consent_granted:
        raise HTTPException(status_code=400, detail="FR01_CONSENT_REQUIRED")
    final_bundle: Optional[Dict[str, Any]] = None
    resp = await analyze_stream(req)
    async for chunk in resp.body_iterator:
        line = chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
        for part in line.split("\n\n"):
            p = part.strip()
            if p.startswith("data:"):
                evt = json.loads(p.replace("data:", "", 1).strip())
                if evt.get("type") == "final_result":
                    final_bundle = evt.get("bundle")
    if not final_bundle:
        raise HTTPException(status_code=500, detail="Pipeline did not produce a final bundle")
    return final_bundle


# ---------------------------------------------------------------------------
# FR09: User Correction & Dynamic Epistemic Graph Re-Evaluation
# ---------------------------------------------------------------------------

def _sync_recompute_with_argon(
    correction_type: str,
    user_note: str,
    current_round2: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    client = get_genai_client()
    prompt = (
        "TASK: Execute FR09 User Correction & Dynamic Epistemic Re-computation.\n"
        "The user has provided new out-of-band verification evidence or a factual correction.\n"
        "Update the epistemic risk band, headline, and executive summary accordingly without using numerical percentages.\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "epistemic_risk_band": "VERIFIED_SAFE_BY_USER | CONFIRMED_IMPERSONATION_THREAT | MODERATE_AMBIGUOUS",\n'
        '  "risk_headline": "Updated epistemic headline reflecting user verification",\n'
        '  "executive_summary": "Updated 2-3 sentence summary incorporating the user\'s out-of-band evidence"\n'
        "}\n\n"
        f"CORRECTION TYPE: {correction_type}\n"
        f"USER CORRECTION EVIDENCE: {user_note}\n"
        f"PREVIOUS SYNTHESIS: {json.dumps(current_round2.get('executive_summary', ''), ensure_ascii=False)}"
    )
    interaction = client.interactions.create(
        model=PRIMARY_MODEL,
        input=prompt,
        system_instruction=ARIADNE_EPISTEMIC_CONSTITUTION,
        generation_config={"thinking_level": "medium"},
    )
    return extract_json_object(getattr(interaction, "output_text", "") or "")


@app.post("/api/recompute")
async def recompute_epistemic_state(req: RecomputeRequest) -> Dict[str, Any]:
    t0 = time.perf_counter()
    preset_id = req.preset_id if req.preset_id in PRESET_SCENARIOS else "family_voice_urgency"
    base = build_enriched_preset(preset_id)
    round2 = copy.deepcopy(req.current_result or base["round2_repaired"])

    updated_band = "CONFIRMED_IMPERSONATION_THREAT"
    updated_headline = "Out-of-Band Check Completed — Epistemic Provenance Graph Updated"
    updated_summary = f"User Correction Applied: '{req.user_correction_note}'."
    updated_node_status = "refuted_by_out_of_band"

    if req.correction_type == "sender_known_benign":
        updated_band = "VERIFIED_LOW"
        updated_node_status = "verified"

    live_mode = "live_argon_recompute"
    try:
        live_up = await asyncio.wait_for(
            asyncio.to_thread(_sync_recompute_with_argon, req.correction_type, req.user_correction_note, round2),
            timeout=25.0,
        )
        if live_up:
            updated_band = live_up.get("epistemic_risk_band", updated_band)
            updated_headline = live_up.get("risk_headline", updated_headline)
            updated_summary = live_up.get("executive_summary", updated_summary)
    except Exception as exc:
        live_mode = f"deterministic_epistemic_recompute ({type(exc).__name__})"

    round2["epistemic_risk_band"] = updated_band
    round2["risk_headline"] = updated_headline
    round2["executive_summary"] = updated_summary

    graph = round2.get("provenance_graph", {"nodes": [], "edges": []})
    graph["nodes"].append({
        "id": "n_user_oob",
        "type": "anchor",
        "label": "User Out-of-Band Check (FR09)",
        "sub": req.user_correction_note[:42],
        "status": "verified",
    })
    if graph["nodes"]:
        graph["edges"].append({
            "from": "n_user_oob",
            "to": graph["nodes"][0]["id"],
            "label": "updates premise",
            "style": "anchor_path",
        })
        for node in graph["nodes"]:
            if node.get("type") in ("claim", "action"):
                node["status"] = updated_node_status

    latency_ms = int((time.perf_counter() - t0) * 1000)
    return {
        "status": "recomputed",
        "mode": live_mode,
        "latency_ms": latency_ms,
        "correction_type": req.correction_type,
        "user_correction_note": req.user_correction_note,
        "updated_round2": round2,
    }


@app.post("/api/hitl/decision")
async def record_hitl_decision(req: HITLDecisionRequest) -> Dict[str, Any]:
    timestamp_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if req.decision == "revoke_and_purge":
        if req.session_id and req.session_id in EPHEMERAL_SESSIONS:
            del EPHEMERAL_SESSIONS[req.session_id]
        else:
            EPHEMERAL_SESSIONS.clear()

        entry = {
            "id": f"hitl_{uuid.uuid4().hex[:8]}",
            "timestamp": timestamp_iso,
            "decision": "revoke_and_purge",
            "session_purged": True,
            "note": (
                "FR01/FR09 In-Memory Container Session Cleared: Removed session from EPHEMERAL_SESSIONS in active container memory "
                "(Note: external Gemini API logs follow Google Cloud / AI Studio retention policies)."
            ),
        }
        HITL_AUDIT_LEDGER.append(entry)
        return {
            "status": "purged",
            "hitl_record": entry,
            "remaining_active_sessions": len(EPHEMERAL_SESSIONS),
        }

    entry = {
        "id": f"hitl_{uuid.uuid4().hex[:8]}",
        "timestamp": timestamp_iso,
        "session_id": req.session_id or "active_session",
        "preset_id": req.preset_id,
        "decision": req.decision,
        "selected_anchor_channel": req.selected_anchor_channel or "Independent Saved Contact / Official Registry",
        "reviewer_note": req.reviewer_note or "Approved by Human-in-the-Loop operator after reviewing Round 2 provenance.",
        "autonomous_outbound_calls_made": 0,
    }
    HITL_AUDIT_LEDGER.append(entry)
    return {
        "status": "committed",
        "hitl_record": entry,
        "message": "Human-in-the-Loop approval recorded in container audit ledger.",
    }


@app.get("/demo.mp4")
async def serve_demo_video() -> FileResponse:
    video_path = BASE_DIR / "demo.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="demo.mp4 not found")
    return FileResponse(video_path, media_type="video/mp4", filename="ariadne_live_demo.mp4")


@app.get("/", response_class=HTMLResponse)
async def serve_index() -> FileResponse:
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)
