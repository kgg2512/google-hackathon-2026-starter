# Preservation inventory — 16 October 2026

## Version boundaries

- Public baseline: `25ce8588a0d17528b8c47302fb56f60a026b9fa8`, committed at 14:39:58 KST. GitHub `main` and the original local HEAD matched this SHA when inspected.
- Uncommitted later work: seven modified tracked paths (table below); no untracked source/video deliverable was reported by Git status. Local source and documentation include post-deadline timestamps.
- Live service: earlier HTML/health and synthetic-probe evidence only. No current revision-to-source mapping was established.
- This preservation branch: documentation and an explicitly archived sanitized snapshot. It does not promote later source to the root runtime or claim it was deployed.

## Capture and active work

Antigravity remained running with six observed processes. No process was terminated and no UI focus was changed. The original checkout was only read: no reset, stash, checkout, commit or overwrite. Copy-time SHA-256 checks matched before/after for all 17 tracked files; a second comparison at 06:43:10 UTC (15:43:10 KST) found no changes in them. Stable copies are a point-in-time record; any subsequent edits are outside that capture.

| Modified source path | Public preservation |
| --- | --- |
| `app.py` | Sanitized source in archive; assigned temporary project ID removed |
| `index.html` | Sanitized source; realistic sample contact/account/domain values replaced |
| `scenarios.py` | Sanitized source; fictional fixture contacts further de-identified |
| `.github/workflows/verify.yml` | Archived as inert `.txt`; active root workflow unchanged |
| `README.md` | Unsupported test/video/latency assertions not republished as fact; replaced with evidence-based summary |
| `DESIGN.md` | Architecture intent and local changes summarized with limits |
| `SUBMISSION_PACKAGE.md` | Corrected to missed-deadline and unverified-artifact status |

The [source manifest](../../archive/local-2026-10-16/manifest.json) records original/published hashes and exact paths. [Capture fingerprints](capture-fingerprints.json) retain the hashes and file times of all seven modified paths, including prose whose assertions were not endorsed.

## Requirements source

The user-selected final Korean PRD v0.5 was read completely through the existing Library connector, saved as a real local file (37,146 UTF-8 bytes) and reread. No cloud filesystem path was assumed to exist on the laptop. A [public English requirements edition](PRD_PUBLIC.md) retains FR01–FR11, product vision, uncertainty, privacy/safety and artifact expectations. Personal agent directions and internal account/submission operations were omitted. The full original PRD is retained locally, not uploaded.

The local organizer-ground-truth extract was reviewed for event requirements, but it also contained temporary account and access details. It is excluded from publication. Preparation, connection audit and private operational files were not copied wholesale.

## Exclusions and limits

Excluded: `.env` (not opened), credentials/authentication files, account configuration, raw conversation/email/message material, raw audit responses/logs, agent instructions, caches and dependencies, private preparation/connection records, and realistic sample contact/account identifiers in the newly archived source. No credential value was needed. Existing public history is not rewritten or certified free of every sensitive value.

No video existed in the inspected project file listing or tracked baseline. URLs in local prose were claims, not evidence of playback. No new video was generated. No file was withheld because it changed during capture; changes after the last hash comparison are unpreserved. No broader whole-laptop scan was performed.

A shell clone was blocked by automatic approval review under the no-new-connections constraint. Preservation uses the already-connected GitHub API and an isolated remote branch instead; no clone workaround or new authentication flow was attempted. No force push, merge, redeployment or paid model call was performed.
