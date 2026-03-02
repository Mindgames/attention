#!/usr/bin/env python3
"""Track social posts and extract reusable posting patterns."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4


VERSION = 1
DEFAULT_DAILY_POST_TARGET = 1
DEFAULT_DAILY_CHECK_DAYS = 1
DEFAULT_METRIC_COVERAGE = 0.80

PLATFORMS = {"linkedin", "x", "instagram"}
MEDIUMS = {"post", "thread", "reel", "story", "carousel", "video"}
CREATION_PATHS = {"original", "repurpose", "rewrite", "batch", "prompted", "iterated"}
SOURCE_TYPES = {
    "problem_observation",
    "audience_question",
    "competitor_pattern",
    "news",
    "old_post_repurpose",
    "direct_intent",
}
METRIC_FIELDS = (
    "impressions",
    "likes",
    "comments",
    "reposts",
    "saves",
    "clicks",
    "follows",
)
METRIC_SOURCES = {"manual", "api", "export_import"}
SCORE_WEIGHTS = {
    "likes": 1.0,
    "comments": 3.0,
    "reposts": 4.0,
    "saves": 2.0,
    "clicks": 1.0,
    "follows": 3.0,
}


def get_project_root() -> Path:
    """Return the repository root based on this module's location."""
    return Path(__file__).resolve().parents[1]


def get_log_path() -> Path:
    """Return the social posts JSONL log path."""
    return get_project_root() / "operator" / "social_posts.jsonl"


def now_local() -> datetime:
    """Return current local datetime with timezone."""
    return datetime.now().astimezone()


def now_iso() -> str:
    """Return current local timestamp in ISO format."""
    return now_local().isoformat()


def parse_iso(value: str) -> datetime | None:
    """Parse an ISO datetime string."""
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def as_clean_text(value: str) -> str:
    """Normalize text fields for logging."""
    return value.strip()


def split_csv_list(value: str) -> list[str]:
    """Split a comma-delimited list into normalized strings."""
    if not value:
        return []
    out: list[str] = []
    for item in value.split(","):
        token = item.strip().strip("#")
        if token:
            out.append(token.lower())
    return out


def parse_platform(value: str) -> str:
    """Normalize and validate a platform."""
    text = as_clean_text(value).lower()
    if text in PLATFORMS:
        return text
    raise ValueError(
        f"Unsupported platform '{value}'. Expected one of: {', '.join(sorted(PLATFORMS))}"
    )


def parse_json_tags(value: Any) -> list[str]:
    """Return normalized tags from list or CSV-like string."""
    if isinstance(value, list):
        tags: list[str] = []
        for raw in value:
            if isinstance(raw, str):
                tag = raw.strip().lower()
                if tag:
                    tags.append(tag)
        return tags
    if isinstance(value, str):
        return split_csv_list(value)
    return []


def append_event(payload: dict[str, Any]) -> None:
    """Append one event to the social log."""
    path = get_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def load_events() -> list[dict[str, Any]]:
    """Load all social post events from JSONL."""
    path = get_log_path()
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(payload)
    return events


def parse_posted_at(post: dict[str, Any]) -> datetime | None:
    """Extract post timestamp from a post event."""
    value = post.get("posted_at")
    if isinstance(value, str):
        parsed = parse_iso(value)
        if parsed:
            return parsed
    value = post.get("timestamp")
    if isinstance(value, str):
        parsed = parse_iso(value)
        if parsed:
            return parsed
    return None


def parse_collected_at(snapshot: dict[str, Any]) -> datetime | None:
    """Extract collection timestamp from metrics snapshot."""
    for key in ("collected_at", "timestamp"):
        value = snapshot.get(key)
        if isinstance(value, str):
            parsed = parse_iso(value)
            if parsed:
                return parsed
    return None


def latest_snapshot(snapshots: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the most recent metrics snapshot."""
    if not snapshots:
        return None
    return max(
        snapshots,
        key=lambda item: parse_collected_at(item) or datetime.min.astimezone(),
    )


def metric_value(snapshot: dict[str, Any], field: str) -> float:
    """Return numeric metric value, defaulting to 0."""
    metrics_map = snapshot.get("metrics")
    value = None
    if isinstance(metrics_map, dict):
        value = metrics_map.get(field)
    if value is None:
        value = snapshot.get(field, 0)
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def score_snapshot(snapshot: dict[str, Any]) -> float:
    """Compute weighted performance score for one snapshot."""
    score = 0.0
    for field, weight in SCORE_WEIGHTS.items():
        score += metric_value(snapshot, field) * weight
    return score


def engagement_rate(snapshot: dict[str, Any]) -> float | None:
    """Compute score/impressions percentage if impressions is available."""
    impressions = metric_value(snapshot, "impressions")
    if impressions <= 0:
        return None
    return (score_snapshot(snapshot) / impressions) * 100.0


def classify_hook_type(hook: str) -> str:
    """Classify hook style into coarse buckets."""
    text = hook.strip().lower()
    if not text:
        return "unknown"
    if "?" in text:
        return "question"
    if re.search(r"\b\d+(/\d+)?\b", text):
        return "data"
    if any(token in text for token in ("dirty reality", "unpopular", "secret", "truth")):
        return "contrarian"
    if text.startswith("how ") or text.startswith("why "):
        return "education"
    return "statement"


def create_id(prefix: str, at_time: datetime) -> str:
    """Generate a stable-ish unique id."""
    suffix = uuid4().hex[:6]
    return f"{prefix}-{at_time.strftime('%Y%m%d-%H%M%S')}-{suffix}"


def build_index(
    events: list[dict[str, Any]],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, list[dict[str, Any]]],
    dict[str, dict[str, Any]],
    dict[str, list[dict[str, Any]]],
    int,
]:
    """Build indexes from event stream."""
    posts: dict[str, dict[str, Any]] = {}
    metrics_by_post: dict[str, list[dict[str, Any]]] = defaultdict(list)
    ideas: dict[str, dict[str, Any]] = {}
    decisions_by_post: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unknown_events = 0

    for event in events:
        kind = event.get("event")
        if kind == "post_logged":
            post_id = event.get("post_id")
            if isinstance(post_id, str) and post_id.strip():
                posts[post_id] = event
            continue
        if kind == "metrics_snapshot":
            post_id = event.get("post_id")
            if isinstance(post_id, str) and post_id.strip():
                metrics_by_post[post_id].append(event)
            continue
        if kind == "idea_logged":
            idea_id = event.get("idea_id")
            if isinstance(idea_id, str) and idea_id.strip():
                ideas[idea_id] = event
            continue
        if kind == "decision_note":
            post_id = event.get("post_id")
            if isinstance(post_id, str) and post_id.strip():
                decisions_by_post[post_id].append(event)
            continue
        if kind:
            unknown_events += 1
    return posts, metrics_by_post, ideas, decisions_by_post, unknown_events


def get_origin_value(origin: Any, key: str) -> str:
    """Read optional origin field values."""
    if not isinstance(origin, dict):
        return ""
    value = origin.get(key, "")
    if value is None:
        return ""
    if isinstance(value, list):
        return "|".join([str(item).strip() for item in value if str(item).strip()])
    return str(value).strip()


def _avg(values: list[float]) -> float:
    """Compute average safely."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def command_idea(args: argparse.Namespace) -> int:
    """Log a discovered or drafted idea."""
    if args.source_type not in SOURCE_TYPES:
        print("Unsupported --source-type.")
        print("Expected: problem_observation, audience_question, competitor_pattern, news, old_post_repurpose, direct_intent")
        return 1
    if not as_clean_text(args.working_title) and not as_clean_text(args.topic):
        print("Provide --working-title or --topic.")
        return 1
    if not split_csv_list(args.source_refs):
        print("Provide --source-refs (at least one evidence reference).")
        return 1
    if not as_clean_text(args.hypothesis):
        print("Provide --hypothesis (for example: higher_comment_reply_rate).")
        return 1

    source_refs = split_csv_list(args.source_refs)
    tags = split_csv_list(args.tags)
    try:
        platform = parse_platform(args.platform)
    except ValueError as error:
        print(str(error))
        return 1
    now = now_local()
    idea_id = create_id("idea", now)
    payload: dict[str, Any] = {
        "event": "idea_logged",
        "timestamp": now_iso(),
        "version": VERSION,
        "platform": platform,
        "account": as_clean_text(args.account),
        "idea_id": idea_id,
        "topic": as_clean_text(args.topic),
        "working_title": as_clean_text(args.working_title),
        "hook_candidate": as_clean_text(args.hook_candidate),
        "source_type": args.source_type,
        "source_refs": source_refs,
        "hypothesis": as_clean_text(args.hypothesis),
        "planned_medium": as_clean_text(args.planned_medium),
        "target_audience": as_clean_text(args.target_audience),
        "tags": tags,
        "urgency": as_clean_text(args.urgency),
    }
    append_event(payload)
    print(f"Logged idea {idea_id}.")
    return 0


def command_log(args: argparse.Namespace) -> int:
    """Log a newly published post."""
    posted_at = parse_iso(args.posted_at) if args.posted_at else now_local()
    if not posted_at:
        print("Invalid --posted-at. Use ISO format, for example: 2026-02-23T14:30:00+01:00")
        return 1
    medium = as_clean_text(args.medium).lower()
    if medium not in MEDIUMS:
        print(f"Unsupported --medium '{args.medium}'. Expected: {', '.join(sorted(MEDIUMS))}")
        return 1
    creation_path = as_clean_text(args.creation_path).lower()
    if creation_path not in CREATION_PATHS:
        print(
            f"Unsupported --creation-path '{args.creation_path}'. Expected: {', '.join(sorted(CREATION_PATHS))}"
        )
        return 1
    try:
        platform = parse_platform(args.platform)
    except ValueError as error:
        print(str(error))
        return 1

    events = load_events()
    _, _, ideas, _, _ = build_index(events)
    idea_id = as_clean_text(args.idea_id)
    if idea_id and idea_id not in ideas:
        print(f"Warning: idea id {idea_id} is not logged.")
    if args.posted_from_idea and not idea_id:
        print(
            "Info: --posted-from-idea was set but no --idea-id was provided."
        )
    if not idea_id:
        print("Warning: post logged without idea_id. Add --idea-id where possible.")

    origin = {
        "prompt_ref": as_clean_text(args.origin_source),
        "asset_source": as_clean_text(args.asset_source),
        "tools_used": split_csv_list(args.tools_used),
        "reviewed_by": as_clean_text(args.reviewed_by),
        "origin_note": as_clean_text(args.origin_note),
    }
    origin = {key: value for key, value in origin.items() if value}
    post_id = create_id("post", posted_at)
    payload: dict[str, Any] = {
        "event": "post_logged",
        "timestamp": now_iso(),
        "version": VERSION,
        "post_id": post_id,
        "platform": platform,
        "account": as_clean_text(args.account),
        "posted_at": posted_at.isoformat(),
        "idea_id": idea_id,
        "medium": medium,
        "url": as_clean_text(args.url),
        "topic": as_clean_text(args.topic),
        "hook": as_clean_text(args.hook),
        "format": as_clean_text(args.format),
        "cta": as_clean_text(args.cta),
        "notes": as_clean_text(args.notes),
        "creation_path": creation_path,
        "source": as_clean_text(args.source),
        "campaign": as_clean_text(args.campaign),
        "target_audience": as_clean_text(args.target_audience),
        "tags": split_csv_list(args.tags),
        "scheduled": bool(args.scheduled),
        "origin": origin,
    }
    append_event(payload)
    print(f"Logged post {post_id}.")
    return 0


def command_list(args: argparse.Namespace) -> int:
    """List recent logged posts."""
    events = load_events()
    posts, _, ideas, _, _ = build_index(events)
    if not posts:
        print("No logged social posts.")
        return 0
    now = now_local()
    cutoff = now - timedelta(days=args.days)

    rows: list[tuple[datetime, dict[str, Any]]] = []
    for post in posts.values():
        posted_at = parse_posted_at(post)
        if not posted_at:
            continue
        platform = str(post.get("platform") or "").lower()
        if args.platform and platform != args.platform.lower():
            continue
        if posted_at < cutoff:
            continue
        rows.append((posted_at, post))

    if not rows:
        print("No posts in the selected window.")
        return 0

    rows.sort(key=lambda item: item[0], reverse=True)
    print(f"Recent posts (last {args.days} days):")
    for posted_at, post in rows[: args.limit]:
        post_id = post.get("post_id", "unknown")
        platform = str(post.get("platform") or "unknown")
        medium = str(post.get("medium") or "unknown")
        idea_id = str(post.get("idea_id") or "")
        hook = str(post.get("hook") or "")
        url = str(post.get("url") or "")
        tags = parse_json_tags(post.get("tags"))
        status = "linked" if idea_id in ideas else "orphan"
        if idea_id and idea_id not in ideas:
            status = "unlinked"
        print(f"- {post_id} :: {platform}/{medium} :: {posted_at.isoformat()} :: {status}")
        if hook:
            print(f"  hook: {hook}")
        if url:
            print(f"  url: {url}")
        if idea_id:
            print(f"  idea_id: {idea_id}")
        if tags:
            print(f"  tags: {', '.join(tags)}")
        origin = post.get("origin")
        if isinstance(origin, dict):
            prompt_ref = as_clean_text(str(origin.get("prompt_ref") or ""))
            if prompt_ref:
                print(f"  prompt: {prompt_ref}")

    return 0


def command_metrics(args: argparse.Namespace) -> int:
    """Append a metrics snapshot for an existing post."""
    events = load_events()
    posts, _, _, _, _ = build_index(events)
    if args.post_id not in posts:
        print(f"Unknown post id: {args.post_id}")
        print("Tip: run `python -m operator.social_posts list --days 30`")
        return 1

    collected_at = parse_iso(args.collected_at) if args.collected_at else now_local()
    if not collected_at:
        print("Invalid --collected-at. Use ISO format, for example: 2026-02-23T14:30:00+01:00")
        return 1

    source = as_clean_text(args.source) or "manual"
    if source not in METRIC_SOURCES:
        print(f"Unsupported --source '{source}'. Expected: manual, api, export_import")
        return 1

    metrics: dict[str, int] = {}
    for field in METRIC_FIELDS:
        value = getattr(args, field)
        if value is not None:
            metrics[field] = value
    if not metrics:
        print("Provide at least one metric field.")
        return 1

    payload: dict[str, Any] = {
        "event": "metrics_snapshot",
        "timestamp": now_iso(),
        "version": VERSION,
        "post_id": args.post_id,
        "collected_at": collected_at.isoformat(),
        "source": source,
        "source_url": as_clean_text(args.source_url),
        "notes": as_clean_text(args.notes),
        "metrics": metrics,
    }
    append_event(payload)
    print(f"Recorded metrics for {args.post_id}.")
    return 0


def command_checkup(args: argparse.Namespace) -> int:
    """List posts that need metrics collection or refresh."""
    events = load_events()
    posts, metrics_by_post, _, _, unknown_events = build_index(events)
    if not posts:
        print("No logged social posts.")
        return 0

    now = now_local()
    min_age = timedelta(hours=args.min_age_hours)
    max_age = timedelta(days=args.max_age_days)
    stale_after = timedelta(hours=args.stale_hours)
    needs_update: list[tuple[datetime, str, dict[str, Any], str]] = []

    for post_id, post in posts.items():
        posted_at = parse_posted_at(post)
        if not posted_at:
            continue
        age = now - posted_at
        if age < min_age or age > max_age:
            continue
        platform = str(post.get("platform") or "").lower()
        if args.platform and platform != args.platform.lower():
            continue

        snapshots = metrics_by_post.get(post_id, [])
        latest = latest_snapshot(snapshots)
        if not latest:
            needs_update.append((posted_at, post_id, post, "missing_metrics"))
            continue
        collected_at = parse_collected_at(latest)
        if not collected_at or (now - collected_at) > stale_after:
            needs_update.append((posted_at, post_id, post, "stale_metrics"))

    if not needs_update:
        print("No posts need metrics checkup.")
        if unknown_events:
            print(f"- unknown events ignored: {unknown_events}")
        return 0

    needs_update.sort(key=lambda item: item[0], reverse=True)
    print("Posts that need metrics checkup:")
    for posted_at, post_id, post, reason in needs_update:
        platform = post.get("platform", "unknown")
        medium = post.get("medium", "unknown")
        url = post.get("url", "")
        print(f"- {post_id} :: {platform}/{medium} :: {posted_at.isoformat()} :: {reason}")
        if url:
            print(f"  url: {url}")

    return 0


def _enrich_review_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Add score and rate columns and return enriched rows."""
    scored_rows: list[dict[str, Any]] = []
    skipped = 0
    for row in rows:
        snapshot = row.get("snapshot")
        if not isinstance(snapshot, dict):
            skipped += 1
            continue
        score = score_snapshot(snapshot)
        rate = engagement_rate(snapshot)
        row["score"] = score
        row["rate"] = rate
        for field in METRIC_FIELDS:
            row[field] = int(metric_value(snapshot, field))
        scored_rows.append(row)
    return scored_rows, skipped


def command_review(args: argparse.Namespace) -> int:
    """Generate an analytics summary for recent posts."""
    events = load_events()
    posts, metrics_by_post, ideas, decisions_by_post, unknown_events = build_index(events)
    if not posts:
        print("No logged social posts.")
        return 0

    now = now_local()
    cutoff = now - timedelta(days=args.days)
    rows: list[dict[str, Any]] = []

    for post_id, post in posts.items():
        posted_at = parse_posted_at(post)
        if not posted_at or posted_at < cutoff:
            continue
        platform = str(post.get("platform") or "").lower()
        if args.platform and platform != args.platform.lower():
            continue
        medium = str(post.get("medium") or "").lower()
        if args.medium and medium != args.medium.lower():
            continue
        snapshot = latest_snapshot(metrics_by_post.get(post_id, []))
        idea_id = as_clean_text(str(post.get("idea_id") or ""))
        idea = ideas.get(idea_id, {})
        row = {
            "post_id": post_id,
            "posted_at": posted_at,
            "platform": platform,
            "medium": medium,
            "hook": as_clean_text(str(post.get("hook") or "")),
            "topic": as_clean_text(str(post.get("topic") or "")),
            "idea_id": idea_id,
            "hypothesis": as_clean_text(str(idea.get("hypothesis") or "")),
            "snapshot": snapshot,
            "tags": parse_json_tags(post.get("tags")),
            "creation_path": as_clean_text(str(post.get("creation_path") or "")),
            "origin": post.get("origin") if isinstance(post.get("origin"), dict) else {},
            "decision_notes": decisions_by_post.get(post_id, []),
        }
        rows.append(row)

    if not rows:
        print("No posts in selected window.")
        return 0

    with_metrics = [row for row in rows if row["snapshot"]]
    print(f"Social post review :: last {args.days} days")
    print(f"- posts logged: {len(rows)}")
    print(f"- posts with metrics: {len(with_metrics)}")
    coverage = (len(with_metrics) / len(rows)) * 100.0
    print(f"- metrics coverage: {coverage:.1f}%")
    if unknown_events:
        print(f"- unknown events ignored: {unknown_events}")

    if not with_metrics:
        print("No metrics snapshots found. Run checkup and add metrics first.")
        return 0

    scored_rows, skipped = _enrich_review_rows(with_metrics)
    if skipped:
        print(f"- rows without usable metrics: {skipped}")

    scored_rows.sort(key=lambda item: item["score"], reverse=True)
    print("")
    print(f"Top {min(args.top, len(scored_rows))} posts by weighted score:")
    for row in scored_rows[: args.top]:
        label = (
            f"- {row['post_id']} :: {row['platform']}/{row['medium']} "
            f":: score={row['score']:.1f} :: topic={row['topic']}"
        )
        if row["rate"] is not None:
            label += f" :: rate={row['rate']:.2f}%"
        label += (
            f" :: impressions={row['impressions']} likes={row['likes']} "
            f"comments={row['comments']} reposts={row['reposts']}"
        )
        print(label)
        if row["hook"]:
            print(f"  hook: {row['hook']}")
        if row["hypothesis"]:
            print(f"  hypothesis: {row['hypothesis']}")

    medium_scores: dict[str, list[float]] = defaultdict(list)
    for row in scored_rows:
        medium_scores[str(row["medium"])].append(float(row["score"]))
    medium_rank = sorted(medium_scores.items(), key=lambda item: _avg(item[1]), reverse=True)
    print("")
    print("Average score by medium:")
    for medium, scores in medium_rank:
        print(f"- {medium}: avg_score={_avg(scores):.1f} across {len(scores)} post(s)")

    hook_rank_by_platform: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in scored_rows:
        platform = str(row["platform"] or "unknown")
        hook_type = classify_hook_type(str(row["hook"]))
        hook_rank_by_platform[platform][hook_type].append(float(row["score"]))
    print("")
    print("Hook-by-platform ranking:")
    for platform, hook_map in sorted(hook_rank_by_platform.items()):
        print(f"- {platform}")
        for hook_type, scores in sorted(hook_map.items(), key=lambda item: _avg(item[1]), reverse=True):
            print(f"  - {hook_type}: avg_score={_avg(scores):.1f} across {len(scores)} post(s)")

    slot_scores: dict[str, list[float]] = defaultdict(list)
    for row in scored_rows:
        posted_at = row["posted_at"]
        if isinstance(posted_at, datetime):
            slot = posted_at.strftime("%a %H:00")
            slot_scores[slot].append(float(row["score"]))
    best_slots = sorted(slot_scores.items(), key=lambda item: _avg(item[1]), reverse=True)[:3]
    if best_slots:
        print("")
        print("Best posting windows by average score:")
        for slot, scores in best_slots:
            print(f"- {slot}: avg_score={_avg(scores):.1f} across {len(scores)} post(s)")

    topic_scores: dict[str, list[float]] = defaultdict(list)
    for row in scored_rows:
        topic = row["topic"] or "untagged"
        topic_scores[topic].append(float(row["score"]))
    topic_rank = sorted(topic_scores.items(), key=lambda item: _avg(item[1]), reverse=True)
    print("")
    print("Topic lift (avg score):")
    for topic, scores in topic_rank[:10]:
        print(f"- {topic}: avg_score={_avg(scores):.1f} across {len(scores)} post(s)")

    pattern_scores: dict[str, list[float]] = defaultdict(list)
    for row in scored_rows:
        pattern = " | ".join(
            filter(
                None,
                [
                    str(row["platform"]),
                    row["topic"] or "untagged",
                    classify_hook_type(row["hook"]),
                    str(row["medium"]),
                ],
            )
        )
        pattern_scores[pattern].append(float(row["score"]))
    recurring_patterns = sorted(
        (
            (pattern, scores)
            for pattern, scores in pattern_scores.items()
            if len(scores) >= 2
        ),
        key=lambda item: _avg(item[1]),
        reverse=True,
    )
    if recurring_patterns:
        print("")
        print("Recurring patterns:")
        for pattern, scores in recurring_patterns[:10]:
            print(
                f"- {pattern} | count={len(scores)} | avg_score={_avg(scores):.1f}"
            )
    else:
        print("")
        print("Recurring patterns: none yet (need at least two posts per pattern).")

    hypothesis_scores: dict[str, list[float]] = defaultdict(list)
    for row in scored_rows:
        hypothesis = row["hypothesis"] or "untracked"
        hypothesis_scores[hypothesis].append(float(row["score"]))
    reusable_hypotheses = sorted(
        hypothesis_scores.items(),
        key=lambda item: _avg(item[1]),
        reverse=True,
    )
    print("")
    print("Top reusable hypotheses:")
    for hypothesis, scores in reusable_hypotheses[:10]:
        print(
            f"- {hypothesis}: avg_score={_avg(scores):.1f} across {len(scores)} post(s)"
        )

    print("")
    best_hypothesis = reusable_hypotheses[0][0] if reusable_hypotheses else "unknown"
    print("Suggested next-step routine:")
    print("- Log every post immediately with platform, medium, topic, hook, and origin notes.")
    print("- Add metrics snapshots at +24h and +72h for each post.")
    print(
        f"- Prioritize this hypothesis pattern for the next 5 posts: {best_hypothesis}"
    )

    decision_count = 0
    for row in rows:
        notes = row["decision_notes"]
        if isinstance(notes, list):
            decision_count += len(notes)
    if decision_count:
        print(f"- Decision notes available: {decision_count}")

    return 0


def command_export(args: argparse.Namespace) -> int:
    """Export posts and metrics rows for spreadsheet review."""
    events = load_events()
    posts, metrics_by_post, ideas, _, _ = build_index(events)
    if not posts:
        print("No logged social posts.")
        return 0

    now = now_local()
    cutoff = now - timedelta(days=args.days)
    rows: list[dict[str, Any]] = []

    for post_id, post in posts.items():
        posted_at = parse_posted_at(post)
        if not posted_at or posted_at < cutoff:
            continue
        platform = str(post.get("platform") or "").lower()
        if args.platform and platform != args.platform.lower():
            continue
        snapshot = latest_snapshot(metrics_by_post.get(post_id, []))
        if not snapshot and not args.include_without_metrics:
            continue
        if not snapshot:
            snapshot = {}
        origin = post.get("origin") if isinstance(post.get("origin"), dict) else {}
        idea_id = as_clean_text(str(post.get("idea_id") or ""))
        idea = ideas.get(idea_id, {})
        row = {
            "posted_at": posted_at.isoformat(),
            "platform": platform,
            "account": as_clean_text(str(post.get("account") or "")),
            "medium": as_clean_text(str(post.get("medium") or "")),
            "topic": as_clean_text(str(post.get("topic") or "")),
            "hook": as_clean_text(str(post.get("hook") or "")),
            "creation_path": as_clean_text(str(post.get("creation_path") or "")),
            "pattern_tags": " | ".join(
                filter(
                    None,
                    [
                        platform,
                        as_clean_text(str(post.get("topic") or "")) or "untagged",
                        classify_hook_type(as_clean_text(str(post.get("hook") or ""))),
                        as_clean_text(str(post.get("medium") or "")),
                    ],
                )
            ),
            "idea_id": idea_id,
            "hypothesis": as_clean_text(str(idea.get("hypothesis") or "")),
            "url": as_clean_text(str(post.get("url") or "")),
            "source": as_clean_text(str(post.get("source") or "")),
            "campaign": as_clean_text(str(post.get("campaign") or "")),
            "target_audience": as_clean_text(str(post.get("target_audience") or "")),
            "tags": "|".join(parse_json_tags(post.get("tags"))),
            "origin_prompt_ref": get_origin_value(origin, "prompt_ref"),
            "origin_asset_source": get_origin_value(origin, "asset_source"),
            "origin_tools_used": "|".join(parse_json_tags(origin.get("tools_used"))),
            "post_id": post_id,
            "collected_at": parse_collected_at(snapshot).isoformat() if parse_collected_at(snapshot) else "",
        }
        for field in METRIC_FIELDS:
            row[field] = int(metric_value(snapshot, field))
        row["score"] = score_snapshot(snapshot) if snapshot else 0.0
        row_rate = engagement_rate(snapshot) if snapshot else None
        row["engagement_rate"] = f"{row_rate:.4f}" if row_rate is not None else ""
        rows.append(row)

    pattern_scores: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        pattern_scores[row["pattern_tags"]].append(float(row.get("score", 0.0)))
    recurring_patterns = sorted(
        (
            (pattern, scores)
            for pattern, scores in pattern_scores.items()
            if len(scores) >= 2
        ),
        key=lambda item: _avg(item[1]),
        reverse=True,
    )
    top_patterns = ", ".join(pattern for pattern, _ in recurring_patterns[:3])
    for row in rows:
        row["best_pattern_tags"] = top_patterns

    if not rows:
        print("No posts to export.")
        return 0

    if args.format == "json":
        print(json.dumps(rows, ensure_ascii=True, indent=2))
        return 0

    fieldnames = [
        "posted_at",
        "platform",
        "account",
        "medium",
        "topic",
        "hook",
        "creation_path",
        "idea_id",
        "hypothesis",
        "url",
        "campaign",
        "source",
        "target_audience",
        "tags",
        "origin_prompt_ref",
        "origin_asset_source",
        "origin_tools_used",
        "pattern_tags",
        "best_pattern_tags",
        "post_id",
        "collected_at",
    ]
    fieldnames.extend(METRIC_FIELDS)
    fieldnames.extend(["score", "engagement_rate"])
    writer_rows = sorted(rows, key=lambda item: item["posted_at"], reverse=True)
    if args.out == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for row in writer_rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
        return 0

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in writer_rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    print(f"Exported {len(writer_rows)} rows to {args.out}.")
    return 0


def command_audit(args: argparse.Namespace) -> int:
    """Run stricter checks on data quality and policy compliance."""
    events = load_events()
    posts, metrics_by_post, ideas, _, unknown_events = build_index(events)
    if not posts:
        print("No logged social posts.")
        print("Daily habit check failed: no posts are currently logged.")
        return 1

    now = now_local()
    cutoff = now - timedelta(days=args.days)
    age_min = timedelta(hours=args.min_age_hours)
    age_max = timedelta(days=args.max_age_days)
    stale_after = timedelta(hours=args.stale_hours)
    coverage_threshold = max(0.0, min(1.0, args.coverage_threshold))

    missing_idea: list[tuple[str, str]] = []
    missing_origin: list[tuple[str, str]] = []
    missing_tags: list[tuple[str, str]] = []
    missing_metrics: list[tuple[str, str]] = []
    stale_metrics: list[tuple[str, str]] = []
    eligible_posts = 0
    eligible_with_metrics = 0

    for post_id, post in posts.items():
        posted_at = parse_posted_at(post)
        if not posted_at or posted_at < cutoff:
            continue
        platform = str(post.get("platform") or "").lower()
        if args.platform and platform != args.platform.lower():
            continue
        age = now - posted_at
        if age < age_min or age > age_max:
            continue
        eligible_posts += 1

        idea_id = as_clean_text(str(post.get("idea_id") or ""))
        if not idea_id or idea_id not in ideas:
            missing_idea.append((post_id, platform))

        if not parse_json_tags(post.get("tags")):
            missing_tags.append((post_id, platform))

        origin = post.get("origin") if isinstance(post.get("origin"), dict) else {}
        missing_parts: list[str] = []
        for required_field in ("prompt_ref", "asset_source"):
            if not as_clean_text(str(origin.get(required_field, ""))):
                missing_parts.append(required_field)
        tools = origin.get("tools_used")
        if not isinstance(tools, list) or not tools:
            missing_parts.append("tools_used")
        if missing_parts:
            missing_origin.append((post_id, f"{platform} missing: {', '.join(missing_parts)}"))

        snapshots = metrics_by_post.get(post_id, [])
        latest = latest_snapshot(snapshots)
        if not latest:
            missing_metrics.append((post_id, platform))
            continue
        eligible_with_metrics += 1
        collected_at = parse_collected_at(latest)
        if not collected_at or (now - collected_at) > stale_after:
            stale_metrics.append((post_id, platform))

    if unknown_events:
        print(f"- unknown events ignored: {unknown_events}")
    print(f"Social audit :: last {args.days} days")
    print(f"- eligible posts: {eligible_posts}")
    print(f"- missing idea_id: {len(missing_idea)}")
    print(f"- missing tags: {len(missing_tags)}")
    print(f"- incomplete origin: {len(missing_origin)}")
    print(f"- missing metrics: {len(missing_metrics)}")
    print(f"- stale metrics: {len(stale_metrics)}")

    if missing_idea:
        print("Posts without linked idea:")
        for post_id, detail in missing_idea[:20]:
            print(f"- {post_id} :: {detail}")
    if missing_tags:
        print("Posts missing tags:")
        for post_id, platform in missing_tags[:20]:
            print(f"- {post_id} :: {platform}")
    if missing_origin:
        print("Posts missing required origin fields:")
        for post_id, detail in missing_origin[:20]:
            print(f"- {post_id} :: {detail}")
    if missing_metrics:
        print("Posts missing metrics:")
        for post_id, platform in missing_metrics[:20]:
            print(f"- {post_id} :: {platform}")
    if stale_metrics:
        print("Posts with stale metrics:")
        for post_id, platform in stale_metrics[:20]:
            print(f"- {post_id} :: {platform}")

    coverage = (eligible_with_metrics / eligible_posts) if eligible_posts else 1.0
    if coverage < coverage_threshold:
        print(
            f"Warning: metrics coverage {coverage:.1%} is below threshold {coverage_threshold:.0%}."
        )
    else:
        print(f"Metrics coverage {coverage:.1%} meets threshold.")

    habit_window_start = now - timedelta(days=args.habit_window_days)
    recent_posts = [
        post
        for post in posts.values()
        if (parse_posted_at(post) or habit_window_start) >= habit_window_start
    ]
    if args.platform:
        recent_posts = [
            post
            for post in recent_posts
            if str(post.get("platform") or "").lower() == args.platform.lower()
        ]
    if len(recent_posts) < args.min_posts_per_day:
        print(
            f"Daily habit check failed: {len(recent_posts)} post(s) in last {args.habit_window_days} day(s), "
            f"minimum is {args.min_posts_per_day}."
        )
        return 2

    print("Daily habit check: post frequency is on track.")
    if not (missing_idea or missing_tags or missing_origin):
        return 0
    return 1


def command_decision(args: argparse.Namespace) -> int:
    """Log a decision note connected to a post review period."""
    events = load_events()
    posts, _, _, _, _ = build_index(events)
    post = posts.get(args.post_id)
    if not post:
        print(f"Unknown post id: {args.post_id}")
        return 1
    if not 1 <= args.confidence <= 5:
        print("Invalid --confidence. Use an integer from 1 to 5.")
        return 1

    period_start = parse_iso(args.period_start)
    period_end = parse_iso(args.period_end)
    if not period_start or not period_end:
        print("Use ISO format for --period-start and --period-end.")
        return 1
    if period_start > period_end:
        print("--period-start must be before --period-end.")
        return 1

    payload: dict[str, Any] = {
        "event": "decision_note",
        "timestamp": now_iso(),
        "version": VERSION,
        "post_id": args.post_id,
        "platform": as_clean_text(str(post.get("platform") or "")),
        "account": as_clean_text(str(post.get("account") or "")),
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "insight": as_clean_text(args.insight),
        "confidence": args.confidence,
        "next_experiment": as_clean_text(args.next_experiment),
        "notes": as_clean_text(args.notes),
    }
    append_event(payload)
    print(f"Logged decision note for post {args.post_id}.")
    return 0


def command_routine(_: argparse.Namespace) -> int:
    """Print the operating routine for posting and review."""
    print("Social posting routine:")
    print("- After ideation: log idea, then log post immediately after publishing.")
    print("- Daily: run checkup and audit for posts missing or stale metrics.")
    print("- Daily: add metrics for posts at least 24h old.")
    print("- Weekly: run review and use top hooks/slots in next post batch.")
    print("")
    print("Core commands:")
    print(
        "- python -m operator.social_posts idea --platform linkedin --topic \"...\" --working-title \"...\" "
        "--hook-candidate \"...\" --source-type audience_question --hypothesis \"higher_comment_reply_rate\""
    )
    print(
        "- python -m operator.social_posts log --platform linkedin --medium post --idea-id <id> "
        "--url \"...\" --topic \"...\" --hook \"...\" --creation-path original "
        "--origin-source \"Prompt URL\" --asset-source \"screenshot.png\" --tools-used \"chatgpt\""
    )
    print(
        "- python -m operator.social_posts metrics --post-id <id> --source manual "
        "--impressions 0 --likes 0 --comments 0 --reposts 0"
    )
    print("- python -m operator.social_posts checkup --platform linkedin")
    print("- python -m operator.social_posts audit --days 30 --platform linkedin")
    print("- python -m operator.social_posts review --platform linkedin --days 30")
    print(
        "- python -m operator.social_posts export --platform linkedin --days 7 --format csv --out /tmp/social_week.csv"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create CLI parser for social post operations."""
    parser = argparse.ArgumentParser(description="Track social posting and review performance.")
    subparsers = parser.add_subparsers(dest="command")

    idea_parser = subparsers.add_parser("idea", help="Log a drafted post idea.")
    idea_parser.add_argument("--platform", required=True, help="Platform (linkedin, x, instagram).")
    idea_parser.add_argument("--account", default="", help="Optional account/profile label.")
    idea_parser.add_argument("--topic", default="", help="Idea topic.")
    idea_parser.add_argument("--working-title", required=True, help="Working title for the idea.")
    idea_parser.add_argument("--hook-candidate", default="", help="Candidate hook line.")
    idea_parser.add_argument(
        "--source-type",
        required=True,
        help="problem_observation | audience_question | competitor_pattern | news | old_post_repurpose | direct_intent",
    )
    idea_parser.add_argument(
        "--source-refs",
        default="",
        help="Comma-separated evidence refs (URLs, notes). Required.",
    )
    idea_parser.add_argument(
        "--hypothesis",
        default="",
        help="Hypothesis to test (for example: higher_comment_reply_rate).",
    )
    idea_parser.add_argument("--planned-medium", default="", help="Planned medium.")
    idea_parser.add_argument("--target-audience", default="", help="Target audience.")
    idea_parser.add_argument("--tags", default="", help="Comma-separated tags.")
    idea_parser.add_argument("--urgency", default="", help="Urgency or priority label.")

    log_parser = subparsers.add_parser("log", help="Log a published post.")
    log_parser.add_argument("--platform", required=True, help="Platform (linkedin, x, instagram).")
    log_parser.add_argument(
        "--medium",
        required=True,
        help="Medium (post, thread, reel, story, carousel, video).",
    )
    log_parser.add_argument("--account", default="", help="Optional account/profile label.")
    log_parser.add_argument("--url", default="", help="Post URL.")
    log_parser.add_argument("--topic", default="", help="Post topic.")
    log_parser.add_argument("--hook", default="", help="Opening hook text.")
    log_parser.add_argument("--format", default="", help="Post format label.")
    log_parser.add_argument("--cta", default="", help="Call-to-action used.")
    log_parser.add_argument("--notes", default="", help="Extra notes.")
    log_parser.add_argument("--idea-id", default="", help="Related idea id.")
    log_parser.add_argument(
        "--creation-path",
        default="original",
        help="Creation path: original, repurpose, rewrite, batch, prompted, iterated.",
    )
    log_parser.add_argument("--origin-source", default="", help="Origin prompt reference.")
    log_parser.add_argument("--origin-note", default="", help="How this was created.")
    log_parser.add_argument("--target-audience", default="", help="Target audience.")
    log_parser.add_argument("--tags", default="", help="Comma-separated tags.")
    log_parser.add_argument("--source", default="", help="Source label for this post.")
    log_parser.add_argument("--campaign", default="", help="Campaign label.")
    log_parser.add_argument(
        "--posted-from-idea",
        action="store_true",
        help="Assert this post is from a prior idea draft.",
    )
    log_parser.add_argument("--scheduled", action="store_true", help="Post was scheduled.")
    log_parser.add_argument(
        "--posted-at",
        default="",
        help="ISO datetime when posted. Defaults to now.",
    )
    log_parser.add_argument(
        "--asset-source",
        default="",
        help="Asset source used (for example: screenshot, doc).",
    )
    log_parser.add_argument("--tools-used", default="", help="Comma-separated tools used.")
    log_parser.add_argument("--reviewed-by", default="", help="Reviewer name.")

    list_parser = subparsers.add_parser("list", help="List recent logged posts.")
    list_parser.add_argument("--days", type=int, default=30, help="Lookback window in days.")
    list_parser.add_argument("--limit", type=int, default=20, help="Max rows.")
    list_parser.add_argument("--platform", default="", help="Filter by platform.")

    metrics_parser = subparsers.add_parser("metrics", help="Append metrics snapshot for a post.")
    metrics_parser.add_argument("--post-id", required=True, help="Target post id.")
    metrics_parser.add_argument(
        "--collected-at",
        default="",
        help="ISO datetime for metric collection time. Defaults to now.",
    )
    for field in METRIC_FIELDS:
        metrics_parser.add_argument(f"--{field}", type=int, default=None, help=f"{field} value.")
    metrics_parser.add_argument("--source", default="manual", help="manual | api | export_import.")
    metrics_parser.add_argument("--source-url", default="", help="Source URL for metrics evidence.")
    metrics_parser.add_argument("--notes", default="", help="Extra notes.")

    checkup_parser = subparsers.add_parser(
        "checkup",
        help="List posts that need metrics collection or refresh.",
    )
    checkup_parser.add_argument("--platform", default="", help="Filter by platform.")
    checkup_parser.add_argument("--min-age-hours", type=int, default=24, help="Minimum post age before checkup.")
    checkup_parser.add_argument("--max-age-days", type=int, default=30, help="Maximum post age to include in checkup.")
    checkup_parser.add_argument("--stale-hours", type=int, default=72, help="Mark metrics stale after this many hours.")

    audit_parser = subparsers.add_parser("audit", help="Run stricter data validation on logs.")
    audit_parser.add_argument("--platform", default="", help="Filter by platform.")
    audit_parser.add_argument("--days", type=int, default=30, help="Lookback window in days.")
    audit_parser.add_argument("--min-age-hours", type=int, default=24, help="Minimum post age before check.")
    audit_parser.add_argument("--max-age-days", type=int, default=30, help="Maximum post age to include.")
    audit_parser.add_argument("--stale-hours", type=int, default=72, help="Mark metrics stale after this many hours.")
    audit_parser.add_argument("--coverage-threshold", type=float, default=DEFAULT_METRIC_COVERAGE, help="Minimum metrics coverage threshold.")
    audit_parser.add_argument("--habit-window-days", type=int, default=DEFAULT_DAILY_CHECK_DAYS, help="Window for daily habit check.")
    audit_parser.add_argument(
        "--min-posts-per-day",
        type=int,
        default=DEFAULT_DAILY_POST_TARGET,
        help="Minimum posts expected in habit window.",
    )
    decision_parser = subparsers.add_parser("decision", help="Log a review decision for a post.")
    decision_parser.add_argument("--post-id", required=True, help="Target post id.")
    decision_parser.add_argument(
        "--period-start",
        required=True,
        help="ISO date for decision period start.",
    )
    decision_parser.add_argument(
        "--period-end",
        required=True,
        help="ISO date for decision period end.",
    )
    decision_parser.add_argument(
        "--insight",
        required=True,
        help="Insight summary (for example: question hooks improved comments).",
    )
    decision_parser.add_argument(
        "--confidence",
        type=int,
        required=True,
        help="Confidence score from 1-5.",
    )
    decision_parser.add_argument(
        "--next-experiment",
        required=True,
        help="Actionable next experiment.",
    )
    decision_parser.add_argument("--notes", default="", help="Extra notes.")

    review_parser = subparsers.add_parser(
        "review",
        help="Review post performance and generate tactical insights.",
    )
    review_parser.add_argument("--platform", default="", help="Filter by platform.")
    review_parser.add_argument("--medium", default="", help="Filter by medium.")
    review_parser.add_argument("--days", type=int, default=30, help="Lookback window.")
    review_parser.add_argument("--top", type=int, default=5, help="Top posts to print.")
    review_parser.add_argument(
        "--pattern-min-count",
        type=int,
        default=2,
        help="Minimum posts in a pattern before reporting recurrence.",
    )

    export_parser = subparsers.add_parser("export", help="Export snapshots for spreadsheet review.")
    export_parser.add_argument("--days", type=int, default=7, help="Lookback window.")
    export_parser.add_argument("--platform", default="", help="Filter by platform.")
    export_parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format.",
    )
    export_parser.add_argument("--out", default="-", help="Output path; '-' prints to stdout.")
    export_parser.add_argument(
        "--include-without-metrics",
        action="store_true",
        help="Include posts without metrics in export.",
    )

    subparsers.add_parser("routine", help="Print the routine and core commands.")
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "idea":
        return command_idea(args)
    if args.command == "log":
        return command_log(args)
    if args.command == "list":
        return command_list(args)
    if args.command == "metrics":
        return command_metrics(args)
    if args.command == "checkup":
        return command_checkup(args)
    if args.command == "audit":
        return command_audit(args)
    if args.command == "decision":
        return command_decision(args)
    if args.command == "review":
        return command_review(args)
    if args.command == "export":
        return command_export(args)
    if args.command == "routine":
        return command_routine(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
