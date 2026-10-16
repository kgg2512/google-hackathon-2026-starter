# Ariadne — architecture record

The intended product is an accessible personal protection app with scoped consent, source-linked claims and relationship tracing, independent confirmation, understandable uncertainty, correction and deletion. See the [public PRD](docs/2026-10-16/PRD_PUBLIC.md).

The historical prototype uses FastAPI, Python and a single HTML/JavaScript dashboard. Scenario fixtures illustrate several digital safety cases. Later local source adds a streaming model pipeline: initial decomposition, critic, synthesis, privacy summary and optional image/voice outputs. These are implementation paths, not evidence that all model capabilities work in production.

The post-deadline source is preserved under [archive/local-2026-10-16](archive/local-2026-10-16/README.md), with exact original and sanitized-file fingerprints. Model identifiers in that source are recorded as configured identifiers; this review does not independently establish access or successful output from each model.

Known design gaps include default-true consent in the request schema, readiness flags derived from key presence or constants, estimated token counts, local-instance storage limits, unverified media handling, and incomplete evidence that correction/deletion propagate correctly. An LLM critic is not an independent external source. See [verification](docs/2026-10-16/VERIFICATION.md) before relying on any result.
