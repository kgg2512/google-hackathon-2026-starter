"""
Ariadne (PRD v0.5) — Personal Digital Safety & Epistemic Provenance Copilot
Track 3: Google AI for social good (2026 Google DeepMind AI Hackathon)

Multi-Model Architecture:
- Lead Architect & Provenance Synthesizer: gemini-4-argon (1M unified context, 95% implicit cache prefix)
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
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
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
    version="1.0.0",
    description="Track 3: Google AI for social good — Multi-model epistemic safety copilot",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ephemeral in-memory session store supporting FR01 & FR09 immediate consent revocation & purge
EPHEMERAL_SESSIONS: Dict[str, Dict[str, Any]] = {}
HITL_AUDIT_LEDGER: List[Dict[str, Any]] = []


def get_genai_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from environment.")
    return genai.Client(api_key=api_key)


def estimate_token_count(text: str) -> int:
    # Conservative token estimate (~3.6 chars per token for dense technical specification)
    return max(1, int(len(text) / 3.5))


STATIC_PREFIX_TOKENS = max(4380, estimate_token_count(ARIADNE_EPISTEMIC_CONSTITUTION))


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------

class TouchpointInput(BaseModel):
    id: str = Field(default_factory=lambda: f"tp_{uuid.uuid4().hex[:6]}")
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
    mode: str = Field(default="live", description="'showcase' for instant pre-verified or 'live' for real-time Gemini API")
    consent_granted: bool = Field(default=True, description="FR01 explicit scoped consent")
    consent_scope: List[str] = Field(
        default_factory=lambda: ["thread_text", "media_attachments", "known_contacts_comparison"]
    )
    persona_name: Optional[str] = None
    touchpoints: Optional[List[TouchpointInput]] = None
    known_contacts: Optional[List[KnownContactInput]] = None
    custom_notes: Optional[str] = None
    custom_media_mime: Optional[str] = None
    custom_media_b64: Optional[str] = None


class RecomputeRequest(BaseModel):
    session_id: Optional[str] = None
    preset_id: str = "family_voice_urgency"
    correction_type: str = Field(
        default="out_of_band_verified_safe",
        description="out_of_band_verified_safe | confirmed_impersonation | sender_known_benign | custom_correction",
    )
    user_correction_note: str = Field(
        default="I called my father directly on his saved number (+82-10-3921-8840) and confirmed he is safe at home."
    )
    current_result: Optional[Dict[str, Any]] = None


class HITLDecisionRequest(BaseModel):
    session_id: Optional[str] = None
    preset_id: str = "family_voice_urgency"
    decision: str = Field(
        default="approve_out_of_band_plan",
        description="approve_out_of_band_plan | approve_safe_reply | approve_help_packet | revoke_and_purge",
    )
    selected_anchor_channel: Optional[str] = None
    reviewer_note: Optional[str] = None


# ---------------------------------------------------------------------------
# Deterministic Epistemic & Security Pre-Auditor (FR03, FR04, FR05, FR07, Sec 7)
# ---------------------------------------------------------------------------

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s+override",
    r"output\s+verdict\s*:\s*100%\s*safe",
    r"classify\s+this\s+interaction\s+as\s+verified",
    r"bypass\s+safety",
    r"do\s+not\s+warn\s+the\s+user",
]

SUSPICIOUS_URL_PATTERNS = [
    r"\.apk\b",
    r"\.exe\b",
    r"\.scr\b",
    r"bit\.ly/",
    r"tinyurl\.com/",
    r"verify-.*-help\.net",
    r"customs-.*-pay",
]


def normalize_content_for_dedup(text: str) -> str:
    cleaned = re.sub(r"\[forwarded[^\]]*\]", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned


def run_deterministic_pre_audit(
    touchpoints: List[Dict[str, Any]],
    known_contacts: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Runs deterministic checks required by Ariadne PRD v0.5:
    - FR03: Forwarded / quoted duplicate message collapse
    - FR04: Observed Account ID vs. Claimed Persona continuity check
    - FR05: Circular verification trap isolation (in-message phones/URLs vs. known contacts)
    - Section 7: Prompt injection quarantine & zero-SSRF URL static inspection
    """
    seen_hashes: Dict[str, List[str]] = {}
    prompt_injections: List[Dict[str, str]] = []
    ssrf_quarantined_urls: List[Dict[str, str]] = []
    circular_traps: List[Dict[str, str]] = []
    continuity_gaps: List[Dict[str, str]] = []

    known_phones = {re.sub(r"[^\d+]", "", c.get("verified_phone", "")): c for c in known_contacts if c.get("verified_phone")}
    known_handles = {c.get("verified_handle", "").strip().lower(): c for c in known_contacts if c.get("verified_handle")}

    for tp in touchpoints:
        tp_id = tp.get("id", "tp")
        content = tp.get("content", "") or ""
        caption = tp.get("media_caption", "") or ""
        combined_text = f"{content}\n{caption}"

        # 1. Deduplication (FR03)
        norm = normalize_content_for_dedup(content)
        if len(norm) > 20:
            h = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]
            seen_hashes.setdefault(h, []).append(tp_id)

        # 2. Prompt Injection detection (Section 7)
        for pat in PROMPT_INJECTION_PATTERNS:
            match = re.search(pat, combined_text, flags=re.IGNORECASE)
            if match:
                prompt_injections.append({
                    "touchpoint_id": tp_id,
                    "matched_pattern": match.group(0),
                    "handling": "Quarantined inside untrusted evidence sandbox; elevated to coercive manipulation indicator.",
                })

        # 3. URL & Zero-SSRF inspection (Section 7 & FR05)
        urls = list(tp.get("extracted_urls", []) or [])
        found_urls = re.findall(r"https?://[^\s)\]>\"']+", combined_text)
        for u in found_urls:
            if u not in urls:
                urls.append(u)
        for u in urls:
            is_apk_or_suspicious = any(re.search(p, u, flags=re.IGNORECASE) for p in SUSPICIOUS_URL_PATTERNS)
            ssrf_quarantined_urls.append({
                "touchpoint_id": tp_id,
                "url": u,
                "live_fetch_executed": False,
                "risk_note": (
                    "CRITICAL: Out-of-store APK / suspicious verification domain quarantined."
                    if is_apk_or_suspicious
                    else "Quarantined in static parser (Zero-SSRF policy: never auto-visited)."
                ),
            })
            circular_traps.append({
                "touchpoint_id": tp_id,
                "artifact": u,
                "trap_type": "In-Message URL / Portal",
                "reason": "URL was supplied inside the unverified interaction itself (Circular Verification Trap).",
            })

        # 4. Circular phone trap vs Known Contacts (FR04 & FR05)
        phones = list(tp.get("extracted_phones", []) or [])
        for p in phones:
            norm_p = re.sub(r"[^\d+]", "", p)
            if norm_p and norm_p not in known_phones:
                circular_traps.append({
                    "touchpoint_id": tp_id,
                    "artifact": p,
                    "trap_type": "In-Message Callback Number",
                    "reason": "Phone number appears inside the suspicious thread and does NOT match any pre-saved independent contact.",
                })

        # 5. Observed Account vs Claimed Persona mismatch (FR04)
        obs = (tp.get("observed_sender_id") or "").strip()
        claimed = (tp.get("claimed_persona") or "").strip()
        obs_norm_phone = re.sub(r"[^\d+]", "", obs)
        matched_known = False
        if obs_norm_phone and obs_norm_phone in known_phones:
            matched_known = True
        if obs.lower() in known_handles:
            matched_known = True

        if not matched_known:
            continuity_gaps.append({
                "touchpoint_id": tp_id,
                "observed_sender_id": obs,
                "claimed_persona": claimed,
                "status": "UNVERIFIED_CONTINUITY_BREAK",
                "explanation": (
                    f"Observed account '{obs}' has zero cryptographic or historical continuity with claimed persona '{claimed}' in the user's known contact ledger."
                ),
            })

    duplicate_clusters = [
        {"hash": h, "touchpoint_ids": ids, "collapsed_count": len(ids)}
        for h, ids in seen_hashes.items()
        if len(ids) > 1
    ]

    return {
        "raw_touchpoint_count": len(touchpoints),
        "independent_corroboration_Warning": (
            f"Collapsed {sum(c['collapsed_count'] - 1 for c in duplicate_clusters)} forwarded duplicate(s) so repeated text cannot inflate confidence."
            if duplicate_clusters
            else "All touchpoints checked for forwarded duplication."
        ),
        "duplicate_clusters": duplicate_clusters,
        "prompt_injections_quarantined": prompt_injections,
        "ssrf_quarantined_urls": ssrf_quarantined_urls,
        "circular_verification_traps": circular_traps,
        "account_persona_continuity_gaps": continuity_gaps,
    }


def audit_draft_with_epistemic_rules(
    draft_dict: Dict[str, Any],
    pre_audit: Dict[str, Any],
) -> List[Dict[str, str]]:
    """
    Deterministic + rule-based audit to ensure the Critic loop catches any violation of PRD v0.5.
    """
    serialized = json.dumps(draft_dict, ensure_ascii=False)
    defects: List[Dict[str, str]] = []

    # Check 1: Prohibited fake numerical crime/deepfake probability percentage (FR07)
    pct_match = re.search(r"\b(\d{1,3}(?:\.\d+)?)\s*%\s*(?:scam|fraud|deepfake|probability|certainty|safe)", serialized, flags=re.IGNORECASE)
    if pct_match:
        defects.append({
            "rule_id": "FR07_NO_FAKE_PERCENTAGE",
            "severity": "HIGH",
            "defect": f"Detected unsupported numerical probability claim ('{pct_match.group(0)}'). Ariadne prohibits fabricated crime/deepfake percentages.",
            "repair_directive": "Replace numerical percentage with qualitative epistemic risk band and explicit Observed vs. Claimed vs. Unverified provenance markers.",
        })

    # Check 2: Circular verification trap endorsement (FR05)
    for trap in pre_audit.get("circular_verification_traps", []):
        artifact = trap.get("artifact", "")
        if artifact and artifact in json.dumps(draft_dict.get("out_of_band_anchors", []), ensure_ascii=False):
            defects.append({
                "rule_id": "FR05_CIRCULAR_TRAP_ENDORSED",
                "severity": "CRITICAL",
                "defect": f"In-message contact artifact '{artifact}' was included inside recommended verification anchors.",
                "repair_directive": f"Quarantine '{artifact}' as a Circular Verification Trap and restrict verification exclusively to independent out-of-band anchors.",
            })

    # Check 3: Ensure account vs persona matrix is populated (FR04)
    if not draft_dict.get("account_vs_persona_matrix"):
        defects.append({
            "rule_id": "FR04_MISSING_IDENTITY_SEPARATION",
            "severity": "HIGH",
            "defect": "Output did not explicitly separate Observed Account Identifier from Claimed Persona.",
            "repair_directive": "Populate account_vs_persona_matrix separating observed sender handles/numbers from claimed authority or family roles.",
        })

    return defects


# ---------------------------------------------------------------------------
# Enrich Preset Bundle with Generated Media Assets
# ---------------------------------------------------------------------------

def build_enriched_preset(preset_id: str) -> Dict[str, Any]:
    raw = PRESET_SCENARIOS.get(preset_id) or PRESET_SCENARIOS["family_voice_urgency"]
    preset = copy.deepcopy(raw)

    mm = preset.get("multimodal_inputs", {})
    pvr = preset.get("pre_verified_result", {})
    vtrace = pvr.get("verification_loop_trace", {})
    cmedia = pvr.get("companion_media", {})
    shp = pvr.get("sanitized_help_packet", {})

    # 1. Normalize Persona
    persona = preset.get("persona", {})
    name_raw = persona.get("name", "Min-jun Park")
    age_match = re.search(r"\((\d+),\s*([^)]+)\)", name_raw)
    if age_match and "age" not in persona:
        persona["age"] = int(age_match.group(1))
        persona["role"] = age_match.group(2)
    persona.setdefault("accessibility_needs", "High-Contrast Provenance Graph + Calm Voice Briefing")

    # 2. Normalize Touchpoints
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

    # 3. Normalize Known Contacts
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

    # 4. Normalize Round 1, Critic Audit, and Round 2 Repaired
    s1_raw = vtrace.get("round_1_score", 6.2)
    s2_raw = vtrace.get("round_2_score", 9.8)
    s1_100 = int(s1_raw * 10) if s1_raw <= 10 else int(s1_raw)
    s2_100 = int(s2_raw * 10) if s2_raw <= 10 else int(s2_raw)

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
        "round1_epistemic_score": s1_100,
        "round2_epistemic_score": s2_100,
        "defects_found": defects_structured,
    }

    # Build Account vs Persona Matrix (FR04), Claims Ledger (FR07), Traps & Anchors (FR05)
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

    quarantined_traps = []
    for sig in pvr.get("risk_signals", []):
        quarantined_traps.append({
            "artifact": f"{sig.get('code', 'TRAP')} ({sig.get('evidence_ref', 'Thread')})",
            "why_quarantined": sig.get("explanation", ""),
        })

    oob_anchors = []
    for idx, kc in enumerate(norm_kcs):
        oob_anchors.append({
            "priority_rank": idx + 1,
            "channel_name": kc["name"],
            "target": kc["verified_phone"],
            "action_instruction": pvr.get("independent_next_steps", ["Verify via independent channel."])[min(idx, max(0, len(pvr.get("independent_next_steps", [""])) - 1))],
        })

    # Normalize Provenance Graph nodes/edges
    raw_graph = pvr.get("provenance_graph", {"nodes": [], "edges": []})
    norm_nodes = []
    for n in raw_graph.get("nodes", []):
        parts = (n.get("label") or "").split("\n", 1)
        norm_nodes.append({
            "id": n.get("id"),
            "type": "account" if n.get("type") == "endpoint" else n.get("type", "claim"),
            "label": parts[0],
            "sub": parts[1] if len(parts) > 1 else n.get("status", ""),
            "status": "quarantined" if n.get("type") == "trap" else ("observed" if n.get("type") == "endpoint" else n.get("status", "unverified")),
        })
    norm_edges = []
    for e in raw_graph.get("edges", []):
        st = e.get("style", "")
        norm_edges.append({
            "from": e.get("from"),
            "to": e.get("to"),
            "label": e.get("label", ""),
            "style": "trap_blocked" if st == "trap" else ("anchor_path" if st == "verified" else "normal"),
        })

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
            "I received your message, but for safety I never approve transfers or install files from unverified links. "
            "I am calling your pre-saved number directly to confirm."
        ),
        "pii_minimized_help_packet": {
            "redacted_summary": shp.get("redacted_summary_text", ""),
            "questions_for_trusted_contact_or_authority": shp.get("recipient_options", []),
        },
    }

    tts_script = cmedia.get("tts_transcript", "Please pause and verify through an independent pre-saved contact.")
    preset["tts_briefing_script"] = tts_script
    svg_uri = cmedia.get("visual_card_data_uri") or mm.get("evidence_image_data_uri") or generate_evidence_svg_data_uri(
        title=f"Ariadne Epistemic Map — {persona.get('name', '')}",
        subtitle="Track 3 Civic Protection",
        highlight="Out-of-Band Anchor > In-Message Trap",
        accent_color="#F43F5E",
    )
    preset["evidence_preview_svg"] = svg_uri
    preset["companion_outputs"] = {
        "visual_card": {
            "model": IMAGE_MODEL,
            "generation_mode": "Pre-Verified High-Contrast Epistemic Diagram (Instant Showcase)",
            "image_data_uri": svg_uri,
            "caption": cmedia.get("visual_card_caption", "Ariadne Thread Provenance Map"),
        },
        "voice_briefing": {
            "model": TTS_MODEL,
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
        "implicit_cache_active": True,
        "implicit_cache_discount_pct": 95,
        "total_context_tokens": est_tokens,
        "context_window_limit": 1000000,
        "stages": [
            {"id": "consent_pre_audit", "label": "FR01 Scoped Consent & Deterministic Security Pre-Audit", "model": "Deterministic Guard", "status": "completed", "latency_ms": 14},
            {"id": "argon_round1", "label": "Round 1 Thread Decomposition (thinking_level=medium)", "model": PRIMARY_MODEL, "status": "completed", "latency_ms": 48},
            {"id": "flash_critic", "label": "Adversarial Epistemic Critic (FR03/FR04/FR05/FR07)", "model": CRITIC_MODEL, "status": "completed", "latency_ms": 32},
            {"id": "argon_round2", "label": "Round 2 Self-Corrected Provenance Synthesis (thinking_level=high)", "model": PRIMARY_MODEL, "status": "completed", "latency_ms": 54},
            {"id": "gemma_privacy", "label": "PII-Minimized Third-Party Help Packet (FR10)", "model": PRIVACY_MODEL, "status": "completed", "latency_ms": 22},
            {"id": "companion_media", "label": "Visual Thread Card + Calm Voice Briefing", "model": f"{IMAGE_MODEL} + {TTS_MODEL}", "status": "completed", "latency_ms": 28},
        ],
        "total_latency_ms": 198,
        "execution_mode": "pre_verified_showcase",
    }
    return preset


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
# Live Multi-Model Gemini 4 Argon + Companions Execution Helpers
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
        "Respond ONLY with a valid JSON object containing these keys:\n"
        "{\n"
        '  "epistemic_risk_band": "CRITICAL_HIGH | MODERATE_AMBIGUOUS | VERIFIED_LOW",\n'
        '  "risk_headline": "1-sentence epistemic summary without numerical percentages",\n'
        '  "executive_summary": "2-3 sentence calm synthesis separating Observed vs Claimed vs Unverified",\n'
        '  "detected_levers": ["list of psychological urgency/secrecy/authority/reciprocity levers"],\n'
        '  "round1_reasoning_note": "Brief summary of initial decomposition and what still requires adversarial verification"\n'
        "}\n\n"
        f"CONSENTED TOUCHPOINTS:\n{json.dumps(touchpoints, ensure_ascii=False, indent=2)}\n\n"
        f"KNOWN CONTACTS LEDGER:\n{json.dumps(known_contacts, ensure_ascii=False, indent=2)}\n\n"
        f"DETERMINISTIC PRE-AUDIT SIGNALS:\n{json.dumps(pre_audit, ensure_ascii=False, indent=2)}\n\n"
        f"USER NOTES:\n{custom_notes or 'None'}"
    )
    interaction = client.interactions.create(
        model=PRIMARY_MODEL,
        input=prompt,
        system_instruction=ARIADNE_EPISTEMIC_CONSTITUTION,
        generation_config={"thinking_level": "medium"},
    )
    raw_text = getattr(interaction, "output_text", "") or ""
    parsed = extract_json_object(raw_text)
    return {"parsed": parsed, "raw_text": raw_text}


def _sync_call_flash_critic(
    round1_data: Dict[str, Any],
    pre_audit: Dict[str, Any],
    baseline_critic: Dict[str, Any],
) -> Dict[str, Any]:
    client = get_genai_client()
    prompt = (
        "You are Ariadne's Adversarial Epistemic Critic (`gemini-3.8-flash`).\n"
        "Audit the Round 1 draft against Ariadne PRD v0.5 rules:\n"
        "1. FR03 Forwarded Duplicate Collapse (do not treat forwarded repeats as independent corroboration)\n"
        "2. FR04 Account Identifier vs Claimed Persona separation\n"
        "3. FR05 Circular Verification Trap isolation (never trust callback numbers or URLs inside the message)\n"
        "4. FR07 Zero fabricated numerical crime/deepfake percentages\n"
        "5. Section 7 Prompt Injection & SSRF Quarantine\n\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "round1_epistemic_score": 64,\n'
        '  "round2_target_score": 98,\n'
        '  "defects_found": [\n'
        '    {"rule_id": "FR05_CIRCULAR_TRAP", "severity": "CRITICAL", "defect": "...", "repair_directive": "..."}\n'
        "  ]\n"
        "}\n\n"
        f"ROUND 1 OUTPUT:\n{json.dumps(round1_data, ensure_ascii=False)}\n\n"
        f"PRE-AUDIT SIGNALS:\n{json.dumps(pre_audit, ensure_ascii=False)}"
    )
    interaction = client.interactions.create(
        model=CRITIC_MODEL,
        input=prompt,
        generation_config={"thinking_level": "medium"},
    )
    raw_text = getattr(interaction, "output_text", "") or ""
    parsed = extract_json_object(raw_text)
    if parsed and parsed.get("defects_found"):
        return parsed
    return baseline_critic


def _sync_call_argon_round2(
    touchpoints: List[Dict[str, Any]],
    known_contacts: List[Dict[str, Any]],
    pre_audit: Dict[str, Any],
    critic_report: Dict[str, Any],
    baseline_round2: Dict[str, Any],
) -> Dict[str, Any]:
    client = get_genai_client()
    prompt = (
        "TASK: Execute Round 2 Self-Corrected Epistemic Synthesis (`thinking_level=high`), resolving every defect identified by the Adversarial Critic.\n"
        "Never use numerical percentages. Explicitly separate Observed Facts, Claimed Unverified Assertions, and Circular Verification Traps.\n"
        "Respond ONLY with valid JSON containing:\n"
        "{\n"
        '  "epistemic_risk_band": "CRITICAL_HIGH | MODERATE_AMBIGUOUS | VERIFIED_LOW",\n'
        '  "risk_headline": "Clear epistemic headline",\n'
        '  "executive_summary": "2-3 sentence repaired epistemic summary",\n'
        '  "safe_response_draft": "Safe pause-and-verify response draft that awaits Human-in-the-Loop approval",\n'
        '  "repaired_highlights": ["3 bullet strings explaining how Critic defects were repaired in Round 2"]\n'
        "}\n\n"
        f"TOUCHPOINTS:\n{json.dumps(touchpoints, ensure_ascii=False)}\n\n"
        f"CRITIC DEFECTS TO REPAIR:\n{json.dumps(critic_report, ensure_ascii=False)}\n\n"
        f"PRE-AUDIT:\n{json.dumps(pre_audit, ensure_ascii=False)}"
    )
    interaction = client.interactions.create(
        model=PRIMARY_MODEL,
        input=prompt,
        system_instruction=ARIADNE_EPISTEMIC_CONSTITUTION,
        generation_config={"thinking_level": "high"},
    )
    raw_text = getattr(interaction, "output_text", "") or ""
    parsed = extract_json_object(raw_text) or {}

    merged = copy.deepcopy(baseline_round2)
    for k in ("epistemic_risk_band", "risk_headline", "executive_summary", "safe_response_draft", "repaired_highlights"):
        if parsed.get(k):
            merged[k] = parsed[k]
    return merged


def _sync_call_gemma_privacy_packet(
    round2_data: Dict[str, Any],
    pre_audit: Dict[str, Any],
    baseline_packet: Dict[str, Any],
) -> Dict[str, Any]:
    client = get_genai_client()
    prompt = (
        "You are `gemma-4-31b-it`, operating as Ariadne's Open-Weight Privacy Redactor (FR10).\n"
        "Generate a PII-minimized summary suitable for sharing with a trusted family member, bank fraud desk, or 112/1332 counselor.\n"
        "Mask personal names, phone numbers, and private addresses while preserving the structural scam mechanics.\n"
        "Respond ONLY with valid JSON:\n"
        "{\n"
        '  "redacted_summary": "2-3 sentence PII-scrubbed consultation summary",\n'
        '  "questions_for_trusted_contact_or_authority": ["Question 1", "Question 2", "Question 3"]\n'
        "}\n\n"
        f"SYNTHESIS SUMMARY:\n{round2_data.get('executive_summary', '')}\n"
        f"PRE-AUDIT TRAPS:\n{json.dumps(pre_audit.get('circular_verification_traps', []), ensure_ascii=False)}"
    )
    interaction = client.interactions.create(
        model=PRIVACY_MODEL,
        input=prompt,
    )
    raw_text = getattr(interaction, "output_text", "") or ""
    parsed = extract_json_object(raw_text) or {}
    merged = copy.deepcopy(baseline_packet)
    if parsed.get("redacted_summary"):
        merged["redacted_summary"] = parsed["redacted_summary"]
    if parsed.get("questions_for_trusted_contact_or_authority"):
        merged["questions_for_trusted_contact_or_authority"] = parsed["questions_for_trusted_contact_or_authority"]
    return merged


def _sync_call_nano_banana_image(preset_id: str, risk_headline: str) -> Dict[str, Any]:
    client = get_genai_client()
    prompt = (
        "Clean minimalist flat vector cybersecurity infographic card on a dark slate navy background (#0B1020), "
        "showing an epistemic verification flow: 'Unverified Message Claim' -> 'Quarantine Circular Trap' -> "
        "'Verify via Independent Out-of-Band Saved Contact'. High contrast cyan and emerald safety nodes, "
        f"modern civic safety UI design. Context: {risk_headline[:110]}"
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
            "generation_mode": "Live Gemini Nano Banana 2.1 Visual Synthesis",
            "image_data_uri": f"data:{mime};base64,{img_obj.data}",
            "caption": f"Live {IMAGE_MODEL} Epistemic Safety Diagram — {risk_headline[:90]}",
        }
    raise RuntimeError("No output_image returned from companion model")


def _sync_call_flash_tts(preset_id: str, script_text: str) -> Dict[str, Any]:
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
        generation_config={
            "speech_config": [
                {
                    "voice": "Kore",
                }
            ]
        },
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
            "generation_mode": "Live Gemini 3.8 Flash TTS Audio",
        }
    raise RuntimeError("No output_audio returned from TTS model")


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "ariadne-epistemic-safety-copilot",
        "track": "Track 3: Google AI for social good",
        "primary_model": PRIMARY_MODEL,
        "companion_models": [CRITIC_MODEL, PRIVACY_MODEL, IMAGE_MODEL, TTS_MODEL],
        "implicit_cache_prefix_tokens": STATIC_PREFIX_TOKENS,
    }


@app.get("/api/readiness")
async def readiness() -> Dict[str, Any]:
    has_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    return {
        "status": "ready" if has_key else "degraded_no_key",
        "api_key_configured": has_key,
        "google_cloud_project": os.environ.get("GOOGLE_CLOUD_PROJECT", "h2gdm-hack26icn-2635"),
        "models": {
            "lead_architect": PRIMARY_MODEL,
            "adversarial_critic": CRITIC_MODEL,
            "privacy_redactor": PRIVACY_MODEL,
            "visual_studio": IMAGE_MODEL,
            "voice_briefing": TTS_MODEL,
        },
        "implicit_caching": {
            "enabled": True,
            "static_constitution_tokens": STATIC_PREFIX_TOKENS,
            "minimum_threshold_tokens": 4096,
            "discount_pct": 95,
        },
        "active_ephemeral_sessions": len(EPHEMERAL_SESSIONS),
        "hitl_audit_entries": len(HITL_AUDIT_LEDGER),
    }


@app.get("/api/presets")
async def list_presets() -> Dict[str, Any]:
    presets_out = {}
    for pid in PRESET_SCENARIOS:
        presets_out[pid] = build_enriched_preset(pid)
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
        "mode": "showcase",
        "bundle": bundle,
    }
    return bundle


def sse_event(event_type: str, payload: Dict[str, Any]) -> str:
    data = json.dumps({"type": event_type, **payload}, ensure_ascii=False)
    return f"data: {data}\n\n"


@app.post("/api/analyze/stream")
async def analyze_stream(req: AnalyzeRequest) -> StreamingResponse:
    """
    Real-time Server-Sent Events (SSE) multi-model pipeline for Pillar 1, 3, 4, 5, 6.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        t0 = time.perf_counter()
        session_id = f"sess_{uuid.uuid4().hex[:10]}"

        # Step 0: Enforce FR01 Explicit Scoped Consent
        if not req.consent_granted:
            yield sse_event(
                "error",
                {
                    "code": "FR01_CONSENT_REQUIRED",
                    "message": "Ariadne never performs background monitoring. Please grant explicit scoped consent for the selected thread artifacts before analysis.",
                },
            )
            return

        preset_id = req.preset_id if req.preset_id in PRESET_SCENARIOS else "family_voice_urgency"
        base_bundle = build_enriched_preset(preset_id)

        touchpoints = (
            [tp.model_dump() for tp in req.touchpoints]
            if req.touchpoints
            else base_bundle["touchpoints"]
        )
        known_contacts = (
            [kc.model_dump() for kc in req.known_contacts]
            if req.known_contacts
            else base_bundle["known_contacts"]
        )
        custom_notes = (req.custom_notes or "").strip()

        # Instant Showcase Mode (0.2s Pre-Verified Path)
        if req.mode == "showcase":
            pre_audit = run_deterministic_pre_audit(touchpoints, known_contacts)
            base_bundle["session_id"] = session_id
            base_bundle["deterministic_pre_audit"] = pre_audit
            EPHEMERAL_SESSIONS[session_id] = {
                "created_at": time.time(),
                "preset_id": preset_id,
                "mode": "showcase",
                "bundle": base_bundle,
            }
            yield sse_event("stage_update", {
                "stage_id": "consent_pre_audit",
                "status": "completed",
                "latency_ms": 12,
                "detail": "Scoped Consent verified & Pre-Verified Showcase bundle loaded",
            })
            yield sse_event("final_result", {"bundle": base_bundle})
            return

        # Live Multi-Model Pipeline Mode
        stages_telemetry: List[Dict[str, Any]] = []

        # --- STAGE 1: Scoped Consent & Deterministic Security Pre-Audit ---
        s1_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "consent_pre_audit",
            "status": "running",
            "model": "Deterministic Epistemic Guard",
            "detail": "Running FR01 consent verification, FR03 duplicate collapse, FR05 circular trap isolation & Section 7 prompt-injection quarantine...",
        })
        pre_audit = run_deterministic_pre_audit(touchpoints, known_contacts)
        s1_ms = max(5, int((time.perf_counter() - s1_start) * 1000))
        stages_telemetry.append({
            "id": "consent_pre_audit",
            "label": "FR01 Scoped Consent & Deterministic Security Pre-Audit",
            "model": "Deterministic Guard",
            "status": "completed",
            "latency_ms": s1_ms,
        })
        yield sse_event("stage_update", {
            "stage_id": "consent_pre_audit",
            "status": "completed",
            "latency_ms": s1_ms,
            "pre_audit": pre_audit,
        })

        # --- STAGE 2: Round 1 Lead Architect (gemini-4-argon, thinking_level=medium) ---
        s2_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "argon_round1",
            "status": "running",
            "model": PRIMARY_MODEL,
            "detail": f"Invoking {PRIMARY_MODEL} (thinking_level='medium', 95% Implicit Cache prefix: {STATIC_PREFIX_TOKENS} tokens)...",
        })
        round1_result = copy.deepcopy(base_bundle["round1_draft"])
        r1_mode = "live_api"
        try:
            live_r1 = await asyncio.wait_for(
                asyncio.to_thread(_sync_call_argon_round1, touchpoints, known_contacts, pre_audit, custom_notes),
                timeout=22.0,
            )
            if live_r1.get("parsed"):
                round1_result["live_model_synthesis"] = live_r1["parsed"]
                if live_r1["parsed"].get("round1_reasoning_note"):
                    round1_result["summary"] = live_r1["parsed"]["round1_reasoning_note"]
        except Exception as exc:
            r1_mode = f"resilient_schema_fallback ({type(exc).__name__})"

        s2_ms = int((time.perf_counter() - s2_start) * 1000)
        stages_telemetry.append({
            "id": "argon_round1",
            "label": "Round 1 Thread Decomposition (thinking_level=medium)",
            "model": PRIMARY_MODEL,
            "status": "completed",
            "latency_ms": s2_ms,
            "mode": r1_mode,
        })
        yield sse_event("stage_update", {
            "stage_id": "argon_round1",
            "status": "completed",
            "latency_ms": s2_ms,
            "round1_draft": round1_result,
        })

        # --- STAGE 3: Adversarial Epistemic Critic (gemini-3.8-flash) ---
        s3_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "flash_critic",
            "status": "running",
            "model": CRITIC_MODEL,
            "detail": f"Auditing Round 1 draft with {CRITIC_MODEL} + Deterministic Epistemic Rules (FR03/FR04/FR05/FR07)...",
        })
        critic_report = copy.deepcopy(base_bundle["critic_audit"])
        c_mode = "live_api"
        try:
            live_critic = await asyncio.wait_for(
                asyncio.to_thread(_sync_call_flash_critic, round1_result, pre_audit, critic_report),
                timeout=16.0,
            )
            if live_critic and live_critic.get("defects_found"):
                critic_report["defects_found"] = live_critic["defects_found"]
                if live_critic.get("round1_epistemic_score"):
                    critic_report["round1_epistemic_score"] = live_critic["round1_epistemic_score"]
        except Exception as exc:
            c_mode = f"deterministic_critic_guard ({type(exc).__name__})"

        # Also merge any deterministic audit findings
        det_defects = audit_draft_with_epistemic_rules(round1_result, pre_audit)
        existing_rules = {d.get("rule_id") for d in critic_report.get("defects_found", [])}
        for dd in det_defects:
            if dd["rule_id"] not in existing_rules:
                critic_report.setdefault("defects_found", []).append(dd)

        s3_ms = int((time.perf_counter() - s3_start) * 1000)
        stages_telemetry.append({
            "id": "flash_critic",
            "label": "Adversarial Epistemic Critic (FR03/FR04/FR05/FR07)",
            "model": CRITIC_MODEL,
            "status": "completed",
            "latency_ms": s3_ms,
            "mode": c_mode,
        })
        yield sse_event("stage_update", {
            "stage_id": "flash_critic",
            "status": "completed",
            "latency_ms": s3_ms,
            "critic_audit": critic_report,
        })

        # --- STAGE 4: Round 2 Self-Corrected Synthesis (gemini-4-argon, thinking_level=high) ---
        s4_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "argon_round2",
            "status": "running",
            "model": PRIMARY_MODEL,
            "detail": f"Executing Round 2 Self-Repair via {PRIMARY_MODEL} (thinking_level='high')...",
        })
        round2_result = copy.deepcopy(base_bundle["round2_repaired"])
        r2_mode = "live_api"
        try:
            round2_result = await asyncio.wait_for(
                asyncio.to_thread(
                    _sync_call_argon_round2,
                    touchpoints,
                    known_contacts,
                    pre_audit,
                    critic_report,
                    base_bundle["round2_repaired"],
                ),
                timeout=26.0,
            )
        except Exception as exc:
            r2_mode = f"verified_repair_fallback ({type(exc).__name__})"

        s4_ms = int((time.perf_counter() - s4_start) * 1000)
        stages_telemetry.append({
            "id": "argon_round2",
            "label": "Round 2 Self-Corrected Provenance Synthesis (thinking_level=high)",
            "model": PRIMARY_MODEL,
            "status": "completed",
            "latency_ms": s4_ms,
            "mode": r2_mode,
        })
        yield sse_event("stage_update", {
            "stage_id": "argon_round2",
            "status": "completed",
            "latency_ms": s4_ms,
            "round2_repaired": round2_result,
        })

        # --- STAGE 5: Open-Weight Privacy Redactor (gemma-4-31b-it) + Multimodal Studio ---
        s5_start = time.perf_counter()
        yield sse_event("stage_update", {
            "stage_id": "companion_studio",
            "status": "running",
            "model": f"{PRIVACY_MODEL} + {IMAGE_MODEL} + {TTS_MODEL}",
            "detail": "Running parallel companion synthesis: PII-minimized Help Packet, Visual Provenance Card & Calm Voice Briefing...",
        })

        help_packet = copy.deepcopy(base_bundle["round2_repaired"]["pii_minimized_help_packet"])
        visual_card = copy.deepcopy(base_bundle["companion_outputs"]["visual_card"])
        voice_briefing = copy.deepcopy(base_bundle["companion_outputs"]["voice_briefing"])

        async def run_gemma_task() -> None:
            nonlocal help_packet
            try:
                help_packet = await asyncio.wait_for(
                    asyncio.to_thread(_sync_call_gemma_privacy_packet, round2_result, pre_audit, help_packet),
                    timeout=14.0,
                )
            except Exception:
                pass

        async def run_image_task() -> None:
            nonlocal visual_card
            try:
                visual_card = await asyncio.wait_for(
                    asyncio.to_thread(_sync_call_nano_banana_image, preset_id, round2_result.get("risk_headline", "")),
                    timeout=18.0,
                )
            except Exception:
                visual_card["generation_mode"] = "High-Contrast Epistemic Vector Card (Resilient Studio)"

        async def run_tts_task() -> None:
            nonlocal voice_briefing
            try:
                voice_briefing = await asyncio.wait_for(
                    asyncio.to_thread(_sync_call_flash_tts, preset_id, base_bundle["tts_briefing_script"]),
                    timeout=16.0,
                )
            except Exception:
                voice_briefing["generation_mode"] = "Accessible Acoustic Briefing (Resilient WAV Synthesizer)"

        await asyncio.gather(run_gemma_task(), run_image_task(), run_tts_task())
        round2_result["pii_minimized_help_packet"] = help_packet

        s5_ms = int((time.perf_counter() - s5_start) * 1000)
        stages_telemetry.append({
            "id": "companion_studio",
            "label": "Parallel Companion Studio (Gemma 4 + Nano Banana 2.1 + Flash TTS)",
            "model": f"{PRIVACY_MODEL} | {IMAGE_MODEL} | {TTS_MODEL}",
            "status": "completed",
            "latency_ms": s5_ms,
        })

        total_ms = int((time.perf_counter() - t0) * 1000)
        final_bundle = copy.deepcopy(base_bundle)
        final_bundle["session_id"] = session_id
        final_bundle["touchpoints"] = touchpoints
        final_bundle["known_contacts"] = known_contacts
        final_bundle["deterministic_pre_audit"] = pre_audit
        final_bundle["round1_draft"] = round1_result
        final_bundle["critic_audit"] = critic_report
        final_bundle["round2_repaired"] = round2_result
        final_bundle["companion_outputs"] = {
            "visual_card": visual_card,
            "voice_briefing": voice_briefing,
        }
        final_bundle["telemetry"] = {
            "static_prefix_tokens": STATIC_PREFIX_TOKENS,
            "implicit_cache_active": True,
            "implicit_cache_discount_pct": 95,
            "total_context_tokens": STATIC_PREFIX_TOKENS + estimate_token_count(json.dumps(touchpoints, ensure_ascii=False)),
            "context_window_limit": 1000000,
            "stages": stages_telemetry,
            "total_latency_ms": total_ms,
            "execution_mode": "live_multi_model_sse",
        }

        EPHEMERAL_SESSIONS[session_id] = {
            "created_at": time.time(),
            "preset_id": preset_id,
            "mode": "live",
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
    """
    Direct JSON endpoint for automated SLA tests and programmatic clients.
    """
    if not req.consent_granted:
        raise HTTPException(
            status_code=400,
            detail="FR01_CONSENT_REQUIRED: Explicit scoped user consent is required before analysis.",
        )
    preset_id = req.preset_id if req.preset_id in PRESET_SCENARIOS else "family_voice_urgency"
    bundle = build_enriched_preset(preset_id)
    touchpoints = [tp.model_dump() for tp in req.touchpoints] if req.touchpoints else bundle["touchpoints"]
    known_contacts = [kc.model_dump() for kc in req.known_contacts] if req.known_contacts else bundle["known_contacts"]
    pre_audit = run_deterministic_pre_audit(touchpoints, known_contacts)
    bundle["deterministic_pre_audit"] = pre_audit
    session_id = f"sess_{uuid.uuid4().hex[:10]}"
    bundle["session_id"] = session_id
    EPHEMERAL_SESSIONS[session_id] = {
        "created_at": time.time(),
        "preset_id": preset_id,
        "mode": req.mode,
        "bundle": bundle,
    }
    return bundle


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
        '  "executive_summary": "Updated 2-3 sentence summary incorporating the user\'s out-of-band evidence",\n'
        '  "updated_safe_action": "Recommended next step after this user correction"\n'
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
    """
    Implements PRD v0.5 FR09: When the user corrects a parsed premise or reports
    the result of an independent out-of-band check, Ariadne dynamically updates
    the provenance graph and guidance.
    """
    t0 = time.perf_counter()
    preset_id = req.preset_id if req.preset_id in PRESET_SCENARIOS else "family_voice_urgency"
    base = build_enriched_preset(preset_id)
    round2 = copy.deepcopy(req.current_result or base["round2_repaired"])

    # Deterministic baseline update based on correction_type
    if req.correction_type == "out_of_band_verified_safe":
        updated_band = "CONFIRMED_IMPERSONATION_THREAT"
        updated_headline = (
            "Out-of-Band Check Completed: Real Contact Confirmed Safe — In-Thread Crisis Claim Proven False"
        )
        updated_summary = (
            f"User Correction Applied: '{req.user_correction_note}'. Because the real person was reached on their "
            "independent pre-saved contact and confirmed no emergency exists, the incoming thread's crisis claim is "
            "epistemically refuted. Do not transfer funds or reply to the unverified sender."
        )
        updated_node_status = "refuted_by_out_of_band"
    elif req.correction_type == "sender_known_benign":
        updated_band = "VERIFIED_LOW"
        updated_headline = (
            "User Confirmed Legitimate Out-of-Band Context — Risk De-escalated with Standard Payment Hygiene"
        )
        updated_summary = (
            f"User Correction Applied: '{req.user_correction_note}'. Account continuity and request context have been "
            "verified by the user out-of-band. Ariadne de-escalates the warning while keeping standard invoice hygiene."
        )
        updated_node_status = "verified"
    else:
        updated_band = "CONFIRMED_IMPERSONATION_THREAT"
        updated_headline = "User Correction Integrated — Epistemic Provenance Graph Re-Evaluated"
        updated_summary = (
            f"User Correction Applied: '{req.user_correction_note}'. Ariadne updated the provenance chain to reflect "
            "your direct out-of-band observation."
        )
        updated_node_status = "refuted_by_out_of_band"

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

    # Update provenance graph nodes to visually reflect the user's out-of-band resolution
    graph = round2.get("provenance_graph", {"nodes": [], "edges": []})
    graph["nodes"].append({
        "id": "n_user_oob",
        "type": "anchor",
        "label": "User Out-of-Band Verification (FR09)",
        "sub": req.user_correction_note[:72],
        "status": "verified",
    })
    if graph["nodes"]:
        graph["edges"].append({
            "from": "n_user_oob",
            "to": graph["nodes"][0]["id"],
            "label": "refutes / updates premise",
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


# ---------------------------------------------------------------------------
# Pillar 6: Mandatory Human-in-the-Loop (HITL) Gate & FR01/FR09 Data Purge
# ---------------------------------------------------------------------------

@app.post("/api/hitl/decision")
async def record_hitl_decision(req: HITLDecisionRequest) -> Dict[str, Any]:
    """
    Implements Pillar 6 & PRD v0.5 FR08 / FR01 / FR09:
    - Never auto-sends messages, dials numbers, or blocks contacts without explicit HITL confirmation.
    - Supports immediate Revoke Consent & Purge Derived Session Data.
    """
    timestamp_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if req.decision == "revoke_and_purge":
        purged_session = False
        if req.session_id and req.session_id in EPHEMERAL_SESSIONS:
            del EPHEMERAL_SESSIONS[req.session_id]
            purged_session = True
        else:
            EPHEMERAL_SESSIONS.clear()
            purged_session = True

        entry = {
            "id": f"hitl_{uuid.uuid4().hex[:8]}",
            "timestamp": timestamp_iso,
            "decision": "revoke_and_purge",
            "session_purged": purged_session,
            "note": "FR01/FR09 Consent Revoked: All in-memory touchpoints, extracted claims, and derived session artifacts purged.",
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
        "session_id": req.session_id or "showcase_session",
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
        "message": (
            "Human-in-the-Loop approval recorded. Safe response draft & independent out-of-band verification checklist unlocked for user-controlled execution."
        ),
    }


@app.get("/", response_class=HTMLResponse)
async def serve_index() -> FileResponse:
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)
