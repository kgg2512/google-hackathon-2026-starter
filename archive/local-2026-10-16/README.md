# Sanitized post-deadline source snapshot

This directory preserves selected local files captured on 16 October 2026 after the missed deadline. They are **not** the source of a verified deployment. Antigravity remained running; process activity does not prove whether an agent was editing. All 17 tracked files were stable across copy-time hashes and a later comparison at 06:43:10 UTC (15:43:10 KST).

The original checkout had seven modified tracked files: app.py, index.html, scenarios.py, README.md, DESIGN.md, SUBMISSION_PACKAGE.md and .github/workflows/verify.yml. The three application files and workflow content are preserved here, together with unchanged container/dependency/ignore configuration. The workflow is stored as `workflow-verify.yml.txt` so the archived copy is inert. Original local documentation contained unsupported completion claims; its factual changes and limitations are recorded in the review, with fingerprints in the preservation inventory.

This is a sanitized snapshot. Realistic fixture phone/account identifiers were replaced with explicit example markers, sample email/domain/handle values were replaced with fictional values, and the assigned temporary project identifier was removed. The [manifest](manifest.json) distinguishes original byte hashes from published byte hashes. Sanitization may affect fixture-matching behavior; it is not a functional patch.

No environment file, authentication data, raw audit output, private conversation, local agent instruction file, or video is included. No dependencies were installed and no deployment was performed by this preservation task. The preserved dependency pins include `google-genai==2.30.1`; local prose claiming SDK v1.73.1 did not match those pins.

For the narrow offline control-flow audit, use the existing Python environment with the required packages already installed:

```text
python -B docs/2026-10-16/offline_audit.py archive/local-2026-10-16
```

The audit blocks connections after Windows event-loop initialization and mocks every successful model helper. It does not validate production, media generation, actual model responses or browser rendering. Do not interpret mocked `live_api_success` labels as live model evidence.
