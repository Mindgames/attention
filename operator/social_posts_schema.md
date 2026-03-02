# Social Post Event Schema v1

This repo uses an append-only JSONL event stream in
`operator/social_posts.jsonl` with explicit event types.  
Each JSON object in the log should include these shared fields:

- `event`: one of `idea_logged`, `post_logged`, `metrics_snapshot`, `decision_note`.
- `timestamp`: ISO8601 datetime with offset.
- `platform`: `linkedin`, `x`, or `instagram`.
- `account`: optional account/profile label.
- `version`: schema version, currently `1`.

## `idea_logged`

Required:

- `idea_id`
- `topic`
- `working_title`
- `hook_candidate`
- `source_type`: `problem_observation`, `audience_question`, `competitor_pattern`, `news`, `old_post_repurpose`, `direct_intent`.
- `source_refs` (`["..."]`) (at least one entry).
- `hypothesis`

Optional:

- `planned_medium`
- `target_audience`
- `tags` (`["..."]`)
- `urgency`

## `post_logged`

Required:

- `post_id`
- `posted_at` (ISO8601)
- `idea_id` (optional if not yet linked)
- `medium`: `post`, `thread`, `reel`, `story`, `carousel`, `video`.

Optional:

- `topic`
- `hook`
- `cta`
- `format`
- `notes`
- `creation_path`: `original`, `repurpose`, `rewrite`, `batch`, `prompted`, `iterated`.
- `url`
- `source`
- `campaign`
- `target_audience`
- `tags` (`["..."]`)
- `scheduled` (`true` / `false`)
- `origin`:
  - `prompt_ref`
  - `asset_source`
  - `tools_used` (`["..."]`)
  - `reviewed_by`
  - `origin_note`

## `metrics_snapshot`

Required:

- `post_id`
- `collected_at` (ISO8601)
- `metrics`: map of `impressions`, `likes`, `comments`, `reposts`, `saves`, `clicks`, `follows`.

Optional:

- `source`: `manual`, `api`, `export_import`.
- `source_url`
- `notes`
- `deriveds` (downstream-calculated values; optional)

## `decision_note`

Required:

- `post_id`
- `period_start` (ISO8601)
- `period_end` (ISO8601)
- `insight`
- `confidence` (1–5)
- `next_experiment`

## Required shared fields for all event types in this schema

Each event also has these shared fields in the same shape:

- `event`
- `timestamp`
- `platform`
- `account`
- `version`

## Backward compatibility

Legacy records logged before schema v1 are still accepted:

- Post events with top-level metric fields are supported in reads.
- Metric snapshots with top-level metrics (no nested `metrics`) are still handled.
