# Social Intelligence Research Plan (Phase 0/1 prep)

Use this plan before any API automation work. Phase 1 remains manual-first collection.

## 1) Measurement source mapping

- Map each platform’s analytics UI location:
  - LinkedIn: post analytics + Creator Analytics exports (if available).
  - X: Tweet/impression/reply/retweet/favorite activity panels and any CSV/export endpoint.
  - Instagram: post/reel metrics in Insights and any export options per account type.
- For each source, document:
  - minimum data fields we can view
  - screenshot path to evidence
  - refresh frequency
  - retention and visibility limitations

## 2) Platform policy check

- Before scraping/API use:
  - verify automation terms for each platform
  - confirm what activity is explicitly allowed (manual collection, scraping, API usage)
  - capture policy version/date and owner of approval.
- Decision rule: if policy is ambiguous, keep this step manual in phase 1.

## 3) Metric parity matrix

- Build a mapping table from source metric labels to the canonical scope:
  - `impressions`, `likes`, `comments`, `reposts`, `saves`, `clicks`, `follows`
- Define normalization:
  - missing fields = 0
  - impossible values clamp to 0 for aggregate scoring
  - keep raw values in metric snapshots for traceability

## 4) Time normalization

- Use local timezone for posting windowing and review buckets.
- Posting bucket standard: `Weekday HH:00`.
- Keep `posted_at` and `collected_at` in ISO8601 with offset at entry time.

## 5) Tooling feasibility matrix

- Compare three options:
  1) manual-only entries with CLI
  2) scheduled/manual-assisted CSV imports
  3) official API or third-party integrations (Buffer/Hootsuite/native scheduling)
- Score each option on:
  - reliability
  - policy risk
  - implementation effort
  - review speed

## 6) Output integration

- Keep CSV/manual export in scope 1.
- Evaluate phase 2 outputs:
  - Notion/Airtable/GSheets imports from `social_posts.py export --format csv`
  - Dashboard-only view for pattern review
  - campaign-level rollups and hypothesis re-use tags

## Tooling for this phase

- Core capture stays in `operator/social_posts.py`.
- Research/drafting + performance copy capture should be done by reading platform tabs through:
  - `grais-tab-webdata-reader` (`/Users/mathiasasberg/.codex/skills/private/grais-tab-webdata-reader/SKILL.md`)

