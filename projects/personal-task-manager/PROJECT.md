---
title: Personal Task Manager (Codex-Driven)
status: In Progress
owner: Mathias Asberg
updated: 2026-02-26
north_star_metric: Daily top-3 completion rate (%)
roi_window: 4 weeks
weekly_time_budget_hours: 10
milestone:
  name: V0 daily loop live
  target: 2026-01-03
  dod: "5 consecutive workdays with: morning check-in, schedule.md generated, tasks.md updated, shutdown review logged."
kill_criteria: "If the loop is not used 5 days/week by 2026-01-10, simplify to weekly-only review."
cadence:
  standup_day: Mon
  review_day: Fri
---

# Personal Task Manager

## Summary

A Codex-driven personal task manager that keeps a single source of truth for tasks, plans a realistic day, and closes the loop with a daily review.

## Value & Purpose

- Primary value: execution velocity and focus
- Why now: current tasks are scattered and overdue; a driver loop will reduce drift
- Success looks like: top 3 daily outcomes completed 4/5 days per week within the ROI window

## Scope

- In-scope: task capture in `tasks.md`, daily scheduling in `schedule.md`, weekly review of `projects/*/PROJECT.md`, reminders
- Out-of-scope / Guardrails: no auto-scheduling without review; no calendar writes; no PII in logs
- Dependencies: OpenAI Agents SDK, `python -m operator.main`

## Current Milestone

- **Name**: V0 daily loop live
- **Target**: 2026-01-03
- **Definition of Done**: Daily check-in + schedule + shutdown flow run for 5 consecutive workdays; `tasks.md` kept current; `schedule.md` generated each day.

## Operating Model (V0)

- Morning check-in (Codex driver): review due tasks, pick top 3 outcomes, and run scheduling.
- Midday pulse (optional): adjust schedule if a block slips; add blockers or new tasks.
- Shutdown: mark completes, roll over tasks, capture 1-3 wins, set tomorrow's top 3.
- Weekly review (Fri): run project review, prune backlog, update project docs and Top Tasks.
- Focus sessions: 60-90 min blocks for high-value tasks with explicit break sessions.
- Default focus block length: 90 minutes.
- Break sessions: 10-15 min resets; include stretching and breathing exercises.
- Well-being baseline: 100 pushups daily (split across the day).
- Scheduling anchor: rolling "start-now" blocks instead of fixed start times.
- Rolling plan: generate the next 2-3 blocks, then re-plan based on progress.
- Fixed break length: 15 minutes between 90-minute focus blocks.
- Blocks per check-in: 2 rolling focus blocks.

## Social Intelligence Loop

- Purpose: track social output and convert outcomes into reusable posting patterns across LinkedIn, X, and Instagram.
- Canonical store: `operator/social_posts.jsonl` using `operator/social_posts_schema.md`.
- Canonical capture path:  
  1) `python -m operator.social_posts idea`  
  2) `python -m operator.social_posts log`  
  3) `python -m operator.social_posts metrics` (at +24h and +72h when possible)  
  4) `python -m operator.social_posts audit` for quality checks  
  5) `python -m operator.social_posts review` for weekly pattern extraction
- Data to capture per idea: topic, hook candidate, source type, hypothesis, tags, target audience, references.
- Data to capture per post: linked idea id, medium, hook, campaign, creation path, origin trace, url, metrics.
- Pattern extraction outputs: topic lift, hook ranking, best time windows, recurring pattern reports, top hypotheses.
- Review cadence: daily checkup + weekly in-depth review.
- Target throughput: 1 post/day.
- Research prep artifact: `operator/social_posts_research_plan.md`.
- Drafting/research and post-performance capture can use `grais-tab-webdata-reader` (`/Users/mathiasasberg/.codex/skills/private/grais-tab-webdata-reader/SKILL.md`) for manual extraction.
- Daily automation entrypoint: `.codex/skills/private/social-intelligence-loop` with run command:
  - `python3 .codex/skills/private/social-intelligence-loop/scripts/social_intelligence_daily.py --mode full`.

## Task Data Rules

- Canonical format: `- [ ] Title :: priority=H|M|L; due=YYYY-MM-DD; time=30m; project=<slug>; owner=@mathias`
- Keep tasks outcome-oriented; prefer 5-60 minute units.
- Use `project=<slug>` when tied to a project; otherwise omit.

## Codex Driver Contract

- Codex runs the daily loop, proposes a schedule, and keeps tasks consistent.
- Mathias confirms priorities and time blocks; Codex updates files accordingly.

## Top Tasks (next up)

- [ ] Define the daily loop checklist (morning, midday, shutdown) in this doc :: impact=H; effort=1h; due=2025-12-30; owner=@mathias
- [ ] Triage `tasks.md`: tag top 10 with priority + due and flag stale items :: impact=H; effort=1.5h; due=2025-12-31; owner=@mathias
- [ ] Define rolling schedule parameters (focus block length, break length, blocks per check-in) :: impact=M; effort=0.5h; due=2025-12-31; owner=@mathias
- [ ] Run the operator once and validate that `schedule.md` matches reality :: impact=M; effort=0.5h; due=2025-12-31; owner=@mathias
- [ ] Finalize focus/break rhythm and well-being menu (stretching, breathing, pushups) :: impact=M; effort=0.5h; due=2025-12-31; owner=@mathias
- [ ] Draft weekly review template (project health + backlog cleanup) :: impact=M; effort=1h; due=2026-01-03; owner=@mathias

## Plan (next 7 days)

- Confirm operating model and daily ritual.
- Triage backlog and reset near-term priorities.
- Test schedule generation and adjust time-block rules.

## Recent Activity (last 7 days)

- 2025-12-26 - Created project and initial plan.
- 2025-12-26 - Added baseline well-being menu (stretching, breathing, pushups).

## Risks / Blocks

- Backlog sprawl -> mitigation: weekly prune and cap Top Tasks to 5-7.
- Low adherence to schedule -> mitigation: smaller blocks and explicit buffer time.

## Decision Log

- 2025-12-26 - Use `tasks.md` as the single source of truth - why: keep capture simple - alt: per-project task lists.

## Open Questions

- [ ] Which days are light or off limits for scheduling? -- owner: @mathias -- needed by: 2025-12-30

## Links

- `tasks.md`
- `schedule.md`
- `operator/main.py`

---

## Ops & Reflection Log (agent-written)

> One entry per action. First line = facts, second line = evaluation. Keep it terse.

**Entry format**
YYYY-MM-DDThh:mmZ - RUN - - link:<url or -> - result: success|partial|fail - time:<Xm|Xh> - impact:H|M|L
EVAL - value:+|=|- - why:<1 sentence> - risk:low|med|high - confidence:<0.0-1.0> - next:<1 concrete step or ->

**Example**
2025-12-26T10:00Z - RUN - - link:<url or -> - result: success - time:1h - impact:H
EVAL - value:+ - why:<1 sentence> - risk:low - confidence:0.9 - next:<1 concrete step or ->

**Daily Review**

- Summarize the day's work
- Reflect on the results
- Plan the next day's work
- Update the project status, tasks, plan, risks, etc.

---

<!--
AGENT NOTES (keep this comment):
- On every write, update front-matter `updated:`.
- Top Tasks: compute ICE = Impact x Confidence / Effort(hours); append `priority=ICE:x.x` if helpful; keep only 3-7 tasks here.
- If a RUN result is "fail" or "partial", add/adjust a task in Top Tasks and reference it in `next:`.
- When kill_criteria is met or due will slip, add a Risk and a Decision Log entry, and surface in the next Review.
- Keep Recent Activity to last 5 lines; move older entries into a sidecar LOG.md if needed (same folder).
-->
