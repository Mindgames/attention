---
name: social-intelligence-loop
description: Run the social media learning loop daily (collect prior-day metrics, prepare research checkpoints, and draft post ideas) for LinkedIn/X/Instagram using operator/social_posts.py. Use at each daily automation cycle or when scheduling recurring social-output work.
---

# Social Intelligence Loop

## Purpose

Run a daily routine that turns logged social data into reusable output decisions:
1) collect previous-period stats,
2) prepare research checkpoints for drafting,
3) draft the next candidates.

## When to use

Trigger this skill when you need:
- a daily habit check,
- an evidence-based research pass,
- and fresh draft candidates linked to observed patterns.

## Quick Start

Run full daily loop:

`python3 .codex/skills/private/social-intelligence-loop/scripts/social_intelligence_daily.py --mode full`

Run one phase:

- collect only: `python3 .codex/skills/private/social-intelligence-loop/scripts/social_intelligence_daily.py --mode collect`
- research prep: `python3 .codex/skills/private/social-intelligence-loop/scripts/social_intelligence_daily.py --mode research`
- draft pack: `python3 .codex/skills/private/social-intelligence-loop/scripts/social_intelligence_daily.py --mode draft`

## Default Behavior

- Scope: last 7 days for stats and pattern extraction (override with `--days`).
- Output directory: `operator/social_intelligence/`.
- Files created each run:
  - `social_report_YYYY-MM-DD.md` (checkup + review + audit text sections)
  - `social_posts_export_YYYY-MM-DD.json` (machine-readable export)
  - `social_posts_export_YYYY-MM-DD.csv` (spreadsheet-ready export)
  - `social_research_YYYY-MM-DD.md` (research checklist + target fields)
  - `social_drafts_YYYY-MM-DD.md` (draft-ready idea prompts)

## Workflow

1. `collect`
   - Runs:
     - `social_posts.py checkup`
     - `social_posts.py review`
     - `social_posts.py audit`
     - `social_posts.py export --format json|csv`
   - Detects missing/stale metrics and returns a daily snapshot for this run.

2. `research`
   - Before starting this phase, attach the target analytics tab through
     [`grais-tab-webdata-reader`](/Users/mathiasasberg/.codex/skills/private/grais-tab-webdata-reader/SKILL.md).
   - Writes a platform-by-platform research checklist for the next cycle.
   - Includes explicit placeholders for:
     - manual evidence refs,
     - policy notes,
     - metric parity notes,
     - planned hooks/topics.
   - Appends explicit commands for tab verification and evidence capture so the research notes stay link-backed.

3. `draft`
   - Reads the latest JSON export.
   - Produces candidate idea prompts using the top-performing hypotheses and recurring patterns.
   - Appends exact CLI examples for logging idea records with required fields.

4. `full`
   - Runs collect + research + draft in one command.

## Scheduling

Use your scheduler/cron/automation runner for one command per day:

`cd /Users/mathiasasberg/Projects/satcom && python3 .codex/skills/private/social-intelligence-loop/scripts/social_intelligence_daily.py --mode full`

For a shorter daily pulse, run:

`python3 .codex/skills/private/social-intelligence-loop/scripts/social_intelligence_daily.py --mode collect`

### Recommended daily cadence

1. Morning: `--mode collect` (previous 7 days, or configured `--days`).
2. After capture: update manual evidence links with `grais-tab-webdata-reader`.
3. Afternoon/evening: `--mode draft` for next-post candidate ideas.

## Recommended flags

- `--platform linkedin` / `x` / `instagram` to narrow reporting.
- `--days 7` to tune review/export window.
- `--out-dir operator/social_intelligence` to override output location.
- `--draft-count 3` to generate 3 draft ideas.

## Recommended automation command

- One command per day:
  - `python3 .codex/skills/private/social-intelligence-loop/scripts/social_intelligence_daily.py --mode full`
- If you only want collection+checks:
  - `python3 .codex/skills/private/social-intelligence-loop/scripts/social_intelligence_daily.py --mode collect --days 7`

## Inputs and Outputs

- Input: `operator/social_posts.py`, `operator/social_posts_schema.md`, `operator/social_posts_research_plan.md`, `operator/social_posts_idea_template.md`
- Outputs:
  - `operator/social_intelligence/social_report_YYYY-MM-DD.md`
  - `operator/social_intelligence/social_posts_export_YYYY-MM-DD.json`
  - `operator/social_intelligence/social_posts_export_YYYY-MM-DD.csv`
  - `operator/social_intelligence/social_research_YYYY-MM-DD.md`
  - `operator/social_intelligence/social_drafts_YYYY-MM-DD.md`

## Integration with `grais-tab-webdata-reader`

When research includes manual tab capture, run against the attached platform tabs as needed:

- Use fixed relay commands from the grais skill (do not invent alternates):
  - `npm run relay:start`
  - `npm run relay:status -- --status-timeout-ms 3000`
  - `npm run relay:status -- --all --status-timeout-ms 3000`
  - `node ~/.codex/skills/private/grais-tab-webdata-reader/scripts/read-active-tab.js --host "${GRAIS_RELAY_HOST:-127.0.0.1}" --port "${GRAIS_RELAY_PORT:-18793}" --check --wait-for-attach --attach-timeout-ms "${GRAIS_ATTACH_TIMEOUT_MS:-120000}"`
  - `node ~/.codex/skills/private/grais-tab-webdata-reader/scripts/read-active-tab.js --host "${GRAIS_RELAY_HOST:-127.0.0.1}" --port "${GRAIS_RELAY_PORT:-18793}" --tab-id "<TAB_ID>" --pretty false`

- Set relay env:
  - `export GRAIS_RELAY_HOST=127.0.0.1`
  - `export GRAIS_RELAY_PORT=18793`
  - `export GRAIS_ATTACH_TIMEOUT_MS=120000`
- Attach target tab per the grais skill docs.
- Verify with:
  - `node ~/.codex/skills/private/grais-tab-webdata-reader/scripts/read-active-tab.js --host "${GRAIS_RELAY_HOST:-127.0.0.1}" --port "${GRAIS_RELAY_PORT:-18793}" --check --wait-for-attach --attach-timeout-ms "${GRAIS_ATTACH_TIMEOUT_MS:-120000}"`
- Capture analytics evidence, competitor posts, and topic hooks, then add those links/notes into idea `--source-refs`.

- For multi-agent/repeated reads, always add `--tab-id <TAB_ID>` and do not run relay checks in parallel.
- Add one evidence reference per hypothesis/observation in your `idea` logs.

Collect evidence refs there, then map them into idea notes and `--source-refs`.

## Notes

- Run from repo root so module paths resolve.
- Keep the skill private to this project.
- This skill does not publish content. It creates logs, exports, research notes, and draft candidates.
