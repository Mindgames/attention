---
title: Urban SAR Micro-Swarm
status: In Progress
owner: Mathias Asberg
updated: 2026-03-02
north_star_metric: Median time-to-locate-survivor in GPS-denied buildings
roi_window: 8-12 weeks
weekly_time_budget_hours: 8
milestone:
  name: 3-Unit Architecture Spec + Under-$100 Compute BOM
  target: 2026-03-09
  dod: Whitepaper includes locked 3-unit architecture, 100-unit swarm role split, mesh behavior, and source-backed under-$100 compute plan.
kill_criteria: If v0.1 simulation cannot show >=3x lower per-node compute and >=2x better building-cell coverage cost versus single-platform baseline by 2026-04-15 -> pause.
cadence:
  standup_day: Mon
  review_day: Fri
---

# Urban SAR Micro-Swarm

## Summary

Design a non-weaponized urban SAR solution based on three units: carrier, observer, and a 100-drone indoor swarm. The strategy is role specialization with strict per-node compute budgets and resilient mesh behavior for degraded indoor communication. The immediate outcome is a prototype-ready architecture and cost envelope.

## Value & Purpose

- Primary value: Strategic + learning
- Why now: Low-cost edge-AI modules and mesh stacks make large specialized swarms more feasible than single all-domain drones.
- Success looks like: A validated system design with source-backed compute/cost assumptions and a clear phased test path.

## Scope

- In-scope: 3-unit architecture definition (carrier, observer, 100-unit swarm).
- In-scope: Under-$100 onboard compute strategy for swarm nodes.
- In-scope: Mesh networking strategy with auto-alignment/range-extension behavior.
- In-scope: Indoor SAR localization and marker landing/perching workflow.
- Out-of-scope / Guardrails: No weaponization guidance or targeting logic.
- Out-of-scope / Guardrails: No assumption that buildings contain only hostile actors.
- Dependencies: Public hardware docs, mesh documentation, and indoor autonomy references.

## Current Milestone

- **Name**: 3-Unit Architecture Spec + Under-$100 Compute BOM
- **Target**: 2026-03-09
- **Definition of Done**: Whitepaper and initial material updated with concrete role split (`60/25/15`), cost ranges, mesh doctrine, and validation plan.

## Top Tasks (next up)

- [ ] Build a tunable compute-and-cost calculator for scout/mapper/relay roles :: impact=H; effort=3h; due=2026-03-04; owner=@mathias
- [ ] Implement a 100-node mesh simulation harness with link-quality auto-alignment logic :: impact=H; effort=4h; due=2026-03-05; owner=@mathias
- [ ] Define observer flight doctrine (adaptive altitude bands + fallback mode) :: impact=M; effort=2h; due=2026-03-05; owner=@mathias
- [ ] Specify mapper LiDAR penetration ratio experiments (10/25/40%) :: impact=H; effort=2h; due=2026-03-06; owner=@mathias
- [ ] Draft v0.1 indoor trial protocol and acceptance thresholds :: impact=H; effort=4h; due=2026-03-08; owner=@mathias

## Plan (next 7 days)

- Convert architecture into a spreadsheet/simulator with sensitivity sweeps.
- Validate under-$100 compute options against required perception latency.
- Stress-test mesh assumptions for 100-node operational load.
- Freeze minimal viable role doctrine for v0.1 hardware trial.

## Recent Activity (last 7 days)

- 2026-03-02 — Created project folder and drafted initial SAR material + whitepaper.
- 2026-03-02 — Added source-backed 3-unit architecture and heterogeneous 100-unit swarm split (`60/25/15`).
- 2026-03-02 — Added under-$100 compute references and mesh auto-alignment baseline.
- 2026-03-02 — Added one-pager with value/cost/mesh focus and method comparisons.

## Risks / Blocks

- Mesh saturation risk at 100 active nodes — **mitigation**: role-based bandwidth and event-driven telemetry — **owner**: @mathias — **review**: 2026-03-09
- LiDAR cost/weight creep risk — **mitigation**: mapper-only LiDAR policy and strict BOM gates — **owner**: @mathias — **review**: 2026-03-09
- Observer single-point-of-failure risk — **mitigation**: adaptive altitude doctrine and fallback observer mode — **owner**: @mathias — **review**: 2026-03-09

## Decision Log

- 2026-03-02 — Locked system to 3 units (carrier, observer, 100-unit swarm) — **why**: improves operational clarity and deployability — **alt**: undefined mixed topology — **owner**: @mathias
- 2026-03-02 — Replaced homogeneous 100-LiDAR concept with heterogeneous `60/25/15` swarm — **why**: better cost/weight/power while preserving mission goals — **alt**: LiDAR on all nodes — **owner**: @mathias

## Open Questions

- [ ] Should relay units be aerial-only or include throwable static relays for stairwells? — **owner**: @mathias — **needed by**: 2026-03-06
- [ ] What minimum confidence threshold should trigger marker landing near survivor candidates? — **owner**: @mathias — **needed by**: 2026-03-06

## Links

- ./INITIAL_MATERIAL.md
- ./WHITEPAPER.md
- ./ONE_PAGER.md
- ./SOURCES.md

## Ops & Reflection Log (agent-written)

2026-03-02T15:45Z — RUN — — link:- — result: success — time:2h — impact:H
EVAL — value:+ — why: Built first source-backed baseline for architecture and compute comparison. — risk:med — confidence:0.82 — next: Convert assumptions into tunable model.

2026-03-02T16:30Z — RUN — — link:- — result: success — time:1h — impact:H
EVAL — value:+ — why: Converted concept into locked 3-unit system with concrete role split and under-$100 compute strategy. — risk:med — confidence:0.84 — next: Validate mesh and latency assumptions in simulation.
