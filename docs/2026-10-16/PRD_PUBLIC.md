# Ariadne PRD v0.5 — public product requirements

This English public edition preserves product requirements from the final event-day Korean PRD. It omits personal development instructions, account operations and private submission procedures. Requirements and target metrics are not implementation achievements.

## Purpose and users

Prevent differences in understanding and using AI from becoming differences in personal digital safety. The vision covers ordinary people worldwide, including people with limited AI experience or access to trusted help. A first demonstration may focus on a smaller audience without permanently narrowing the product to that group.

An attacker may manipulate familiar voices, images, relationships, urgency, authority or secrecy. Ariadne should help a person understand a request and find independent confirmation before an irreversible action. Differences in AI literacy causing differences in victimization remain a product hypothesis, not an established causal finding.

The name recalls Ariadne's thread guiding Theseus through a labyrinth. The product metaphor is a traceable route back to evidence and help; it does not label people as monsters. REA inspired reverse decomposition, source tracing and cross-checking. No specific REA skill or package is mandatory, and use of that package was not established.

## Experience

Scoped consent → permitted digital inputs → identity, relationship, claim, evidence and action decomposition → source-linked timeline → independent verification → clear facts, unknowns and next steps → user correction and deletion.

Target situations include impersonation, suspicious romantic or authority relationships, coercion involving synthetic media, and ordinary benign messages. Authentic media does not imply safety; synthetic media does not itself prove fraud; uncertainty does not imply safety. Do not infer criminal intent or fabricate crime probabilities.

## Requirements and acceptance criteria

| ID | Requirement | Acceptance criterion |
| --- | --- | --- |
| FR01 | Scoped consent | Explain input/app/time scope, cloud transfer and retention; collect nothing outside it; allow refusal, stop and withdrawal; stop new collection and pending work on withdrawal. |
| FR02 | Decompose claims and actions | Structure identity, relationship, authority, evidence, requested action, urgency and secrecy; link major items to text spans, audio times or image locations; invent nothing absent from input. |
| FR03 | Timeline and provenance | Track event/collection times, channel, source and transformations; expose missing provenance and possible edits; do not count forwarded duplicates as independent corroboration. |
| FR04 | Relationships across touchpoints | Separate account IDs, phone numbers, display names and claimed people; record link evidence and uncertainty; permit correction; do not merge on name/photo alone. |
| FR05 | Independent verification | Compare contradictions and independently obtained official or pre-existing contact sources; model agreement is not independent verification; in-message contacts and links are not independent anchors. |
| FR06 | Media in context | Treat synthesis signals, provenance and quality as evidence with limits; no signal, inadequate quality or unavailable tools do not establish safety. |
| FR07 | Understandable results | Separate confirmed/observed facts, risk signals, unknowns and next actions; give evidence and limitations for each warning; disclose scope even when no warning appears. |
| FR08 | Confirmation and help | Offer verified regional support and existing contacts; prepare minimal summaries; user checks recipient and content before sharing; invent no institution or phone number. |
| FR09 | Correction and deletion | Correct extraction and relationship errors and refresh affected results; explain deletion of originals, transcripts, embeddings and caches, including exceptions. |
| FR10 | Accessibility | Plain language, screen-reader support, text-size response and non-color state indicators; check translated institution names and contacts separately. |
| FR11 | Connection state and continued protection | Update only from permitted new inputs, reduce duplicate alerts, disclose expired permissions, disconnected/missing/unsupported sources and current analysis coverage. |

FR labels in prototype prompts drift from this original mapping: privacy/help packets sometimes appear as FR10 in code although PRD FR10 is accessibility. This table preserves the actual PRD mapping.

## Platform, privacy and safety

Framework, language, screens, data structures and build order remain implementation choices. Integrations must use supported platform permissions and APIs. Consent does not grant blanket access to encrypted chats, phone calls or every application. Manual/synthetic inputs may support a clearly labeled prototype while broader permitted connections remain a future goal.

Minimize collection and retention; separate permissions; explain cloud processing; avoid sensitive logs and default training use. No covert monitoring, automatic transfers, account blocking, reporting, third-party contact or publication of victim material. Correction and consent withdrawal must have an explained scope; no promise of deleting provider-side data without evidence.

Treat input text, transcripts, files and web pages as untrusted evidence, including embedded instructions. Parse files safely. Link retrieval requires SSRF controls, checks for local/private/metadata addresses, redirect review and isolation; never visit suspicious links with personal cookies or credentials. Attacking an alleged attacker's systems is outside scope.

## Demonstration and quality

Choose one feasible input-to-result path and label unsupported connectors. Show the timeline, evidence and requested action, actual checks and failures, correction by a user, and a normal benign request. Use fictional people and authorized synthetic material, not victim records. Distinguish live API outputs, local deterministic analysis and fixtures.

Proposed measures include independent confirmation before action, detection of risky requested actions, false alarms on benign cases, false reassurance on insufficient evidence, traceability, user comprehension and latency (median/p95). Evaluate by scenario, language and user group. Initial guidance within 5 seconds and text results within 30 seconds at p95 are suggested targets, not measured achievements.

Regression coverage should include prompt injection, duplicate evidence, same name/different person, new-number impersonation, benign transfers, fraud using authentic media, harmless synthetic media, and failed tools. Resolve severe false reassurance, privacy leakage and automatic unauthorized action before public testing. Small synthetic tests do not establish field efficacy or clinical, legal or financial outcomes.

## Event deliverables

The supplied final PRD and organizer-guide extract specify Google AI use, a Google Cloud service that works with actual input, an English explanation, public GitHub source and a demo video URL. Recommended filenames, seven Pillars, a 95% cache rate or a 98-point score are not official requirements. The deadline was 15:20 KST, not the 17:00 event end. Submission was missed.

Preserve legitimate source and explanations before temporary event accounts/projects are deleted; do not promise that their URLs will remain available. Long-term hosting is separate work. This public PRD does not assert a playable video, confirmed submission, connector access or model availability.

## Source and interpretation limits

The final Korean PRD was read in full from the user-selected Library item, written to a local UTF-8 file, and reread successfully (37,146 bytes). It remains local; this is a curated public edition. Background examples and statistics in that PRD are motivations with their own uncertainty, not independently reverified research in this preservation task. The [organizer guide](https://docs.google.com/document/d/13hG3aETJ54oKULF3JZUgM5VYHv7o2ZM4a4AZeqinbRg/edit) is the referenced event source; no private guide/account extract is republished.
