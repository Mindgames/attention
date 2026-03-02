#!/usr/bin/env python3
"""Run the social intelligence loop for a daily cadence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any


def safe_float(value: Any) -> float:
    """Convert any metric-like value to float for ranking."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def load_export_rows(export_path: Path) -> list[dict[str, Any]]:
    """Load export rows from a JSON file when available."""
    if not export_path.exists():
        return []
    try:
        loaded = json.loads(export_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(loaded, list):
        return [row for row in loaded if isinstance(row, dict)]
    return []


def get_repo_root() -> Path:
    """Return repository root (sibling of .codex when available)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == ".codex":
            return parent.parent
    return Path.cwd()


def run_social_posts(args: list[str], cwd: Path, capture: bool = False) -> tuple[int, str]:
    """Run operator.social_posts with a given argument list."""
    command = [sys.executable, "-m", "operator.social_posts", *args]
    result = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=capture,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr if result.stdout or result.stderr else ""
    if capture:
        return result.returncode, output
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    return result.returncode, output


def get_export_rows(state: dict[str, Any], run_args: argparse.Namespace, repo_root: Path) -> list[dict[str, Any]]:
    """Ensure a JSON export exists for the requested scope and load rows."""
    export_path = run_args.out_dir / f"social_posts_export_{state['stamp']}.json"
    if not export_path.exists():
        platform_args = ["--platform", run_args.platform] if run_args.platform else []
        run_social_posts(
            [
                "export",
                "--days",
                str(run_args.days),
                "--format",
                "json",
                "--out",
                str(export_path),
                *platform_args,
            ],
            repo_root,
        )
    return load_export_rows(export_path)


def write_report_section(handle, title: str, body: str) -> None:
    """Append titled section to a text report."""
    handle.write(f"## {title}\n")
    if body.strip():
        handle.write(body.rstrip())
        if not body.endswith("\n"):
            handle.write("\n")
    handle.write("\n\n")


def run_collect(state: dict[str, Any], run_args: argparse.Namespace, repo_root: Path) -> int:
    """Collect checkup/review/audit and export outputs for the period."""
    days = str(run_args.days)
    platform_args = ["--platform", run_args.platform] if run_args.platform else []

    out_dir = run_args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = state["stamp"]
    report_path = out_dir / f"social_report_{stamp}.md"

    status = 0

    with report_path.open("w", encoding="utf-8") as report:
        report.write(f"# Social Intelligence Daily Report ({stamp})\n\n")
        report.write(f"Scope: platform={run_args.platform or 'all'}, days={run_args.days}\n\n")

        code, out = run_social_posts(
            ["checkup", "--days", days, "--min-age-hours", "24", "--max-age-days", days, "--stale-hours", "72", *platform_args],
            repo_root,
            capture=True,
        )
        status = max(status, code)
        write_report_section(report, "Collect: checkup", out or "(no output)\n")

        code, out = run_social_posts(
            ["review", "--days", days, "--top", "10", "--pattern-min-count", "2", *platform_args],
            repo_root,
            capture=True,
        )
        status = max(status, code)
        write_report_section(report, "Collect: review", out or "(no output)\n")

        code, out = run_social_posts(
            [
                "audit",
                "--days",
                days,
                "--min-age-hours",
                "24",
                "--max-age-days",
                days,
                "--stale-hours",
                "72",
                "--coverage-threshold",
                "0.80",
                *platform_args,
            ],
            repo_root,
            capture=True,
        )
        status = max(status, code)
        write_report_section(report, "Collect: audit", out or "(no output)\n")

    json_export = out_dir / f"social_posts_export_{stamp}.json"
    csv_export = out_dir / f"social_posts_export_{stamp}.csv"

    run_social_posts(
        [
            "export",
            "--days",
            days,
            "--format",
            "json",
            "--out",
            str(json_export),
            *platform_args,
        ],
        repo_root,
    )
    run_social_posts(
        [
            "export",
            "--days",
            days,
            "--format",
            "csv",
            "--out",
            str(csv_export),
            *platform_args,
        ],
        repo_root,
    )

    with report_path.open("a", encoding="utf-8") as report:
        report.write("## Exports\n")
        report.write(f"- JSON: {json_export}\n")
        report.write(f"- CSV:  {csv_export}\n")

    return status


def write_research_file(
    state: dict[str, Any],
    run_args: argparse.Namespace,
    out_dir: Path,
    rows: list[dict[str, Any]],
) -> Path:
    """Write a research checklist for the next draft cycle."""
    stamp = state["stamp"]
    path = out_dir / f"social_research_{stamp}.md"

    today = state["today"]
    platform = run_args.platform or "all"

    hypothesis_scores: dict[str, list[float]] = {}
    pattern_scores: dict[str, list[float]] = {}
    for row in rows:
        hypothesis = str(row.get("hypothesis") or "untracked").strip() or "untracked"
        score = safe_float(row.get("score"))
        hypothesis_scores.setdefault(hypothesis, []).append(score)
        pattern = str(row.get("pattern_tags") or row.get("best_pattern_tags") or "untagged").strip()
        pattern_scores.setdefault(pattern, []).append(score)

    top_hypotheses = sorted(
        ((name, mean(values)) for name, values in hypothesis_scores.items()),
        key=lambda item: item[1],
        reverse=True,
    )
    top_patterns = sorted(
        ((name, mean(values), len(values)) for name, values in pattern_scores.items() if len(values) >= 2),
        key=lambda item: item[1],
        reverse=True,
    )
    top_hypothesis = top_hypotheses[0][0] if top_hypotheses else "higher_comment_reply_rate"
    top_patterns_text = ", ".join(name for name, _, _ in top_patterns[:3]) if top_patterns else "not enough data"

    path.write_text(
        "\n".join(
            [
                f"# Social Research Checklist ({stamp})",
                "",
                "## Scope",
                f"- Platform filter: {platform}",
                f"- Data window: {run_args.days} day(s)",
                "",
                "## Top signals (auto)",
                f"- Best tracked hypothesis: `{top_hypothesis}`",
                f"- Recurring pattern candidates: `{top_patterns_text}`",
                f"- Total rows in scope: `{len(rows)}`",
                "",
                "## Step 1: Evidence capture",
                "- Open target platform analytics tabs and capture visible metrics for the previous cycle.",
                "- Record one evidence reference per source (URL/note/screenshot path) in idea notes and CLI `--source-refs` fields.",
                "- For manual metric collection, keep values for: impressions, likes, comments, reposts, saves, clicks, follows.",
                "",
                "## Step 2: Policy check",
                "- Confirm current platform policy notes for collection method before any automation step.",
                "- If policy is ambiguous, keep data path manual and skip scraping/API automation.",
                "",
                "## Step 3: Metric parity mapping",
                "- Map platform metric labels into canonical fields in `social_posts.py` scope.",
                "- Normalize missing values as 0; preserve raw values in snapshots.",
                "",
                "## Step 4: Time normalization",
                "- Use local timezone when writing new posts and metric snapshot times.",
                "- Keep day-bucket targets by weekday + hour window (HH:00).",
                "",
                "## Step 5: Draft readiness",
                "- Prioritize one hypothesis from prior `review` output and 1-2 reusable pattern tags.",
                "- Draft 3 candidate posts for tomorrow's test window.",
                "",
                "## Grais data capture",
                "- If using grais tab reader, verify active tab state before extraction:",
                "  `node ~/.codex/skills/private/grais-tab-webdata-reader/scripts/read-active-tab.js --host \"${GRAIS_RELAY_HOST:-127.0.0.1}\" --port \"${GRAIS_RELAY_PORT:-18793}\" --check --wait-for-attach --attach-timeout-ms \"${GRAIS_ATTACH_TIMEOUT_MS:-120000}\"`",
                "- Capture DOM/text payloads and screenshots as evidence links/references.",
                "",
                f"## Generated on\n- date: {today}",
            ]
        ),
        encoding="utf-8",
    )
    return path


def build_draft_plan(rows: list[dict[str, Any]], count: int) -> tuple[str, list[dict[str, Any]]]:
    """Build draft summary text and candidate rows from export JSON."""
    if not rows:
        return "No recent rows available. Log at least one idea and post to run the cycle.", []

    rows_with_scores = [row for row in rows if isinstance(row, dict)]
    rows_with_scores.sort(key=lambda row: safe_float(row.get("score")), reverse=True)

    hypothesis_scores: dict[str, list[float]] = {}
    for row in rows_with_scores:
        hypothesis = str(row.get("hypothesis") or "untracked").strip() or "untracked"
        hypothesis_scores.setdefault(hypothesis, []).append(safe_float(row.get("score")))

    top_hypotheses = sorted(
        ((name, mean(values)) for name, values in hypothesis_scores.items()),
        key=lambda item: item[1],
        reverse=True,
    )
    best_hypothesis = top_hypotheses[0][0] if top_hypotheses else "higher_comment_reply_rate"

    pattern_scores: dict[str, list[float]] = {}
    for row in rows_with_scores:
        pattern = str(row.get("pattern_tags") or "untagged").strip()
        pattern_scores.setdefault(pattern, []).append(safe_float(row.get("score")))
    top_patterns = sorted(
        ((name, mean(values), len(values)) for name, values in pattern_scores.items() if len(values) >= 2),
        key=lambda item: item[1],
        reverse=True,
    )
    pattern_list = ", ".join(name for name, _, _ in top_patterns[:3]) if top_patterns else "none yet"

    candidate_rows = rows_with_scores[: max(1, count)]
    lines = [
        "# Social Draft Pack",
        "",
        "## Reusable signal summary",
        f"- Best hypothesis: `{best_hypothesis}`",
        f"- Strong recurring patterns: {pattern_list}",
        "",
        "## Draft candidates",
    ]

    for index, row in enumerate(candidate_rows, start=1):
        platform = str(row.get("platform") or "linkedin")
        topic = str(row.get("topic") or "(fill)")
        hook = str(row.get("hook") or "(fill)")
        medium = str(row.get("medium") or "post")
        creation_path = str(row.get("creation_path") or "original")
        score = safe_float(row.get("score"))
        hypothesis = str(row.get("hypothesis") or "higher_comment_reply_rate")

        lines.extend(
            [
                f"### Candidate {index}",
                f"- platform={platform}",
                f"- topic={topic}",
                f"- expected pattern: `{pattern_list or 'platform/topic/hook + medium'}`",
                f"- anchor metric: `score={score:.1f}`",
                f"- seed hook: `{hook}`",
                f"- medium={medium}, creation_path={creation_path}",
                "- source_type=audience_question (or replace with strongest observed source signal)",
                "- working_title: draft placeholder",
                "- hypothesis: `higher_comment_reply_rate`",
                "- source_refs: `<capture evidence URL(s)>`",
                f"- suggested log command:",
                "```bash",
                f"python3 -m operator.social_posts idea \\",
                f"  --platform {platform} \\",
                f"  --working-title \"{topic}\" \\",
                f"  --hook-candidate \"{hook}\" \\",
                f"  --source-type audience_question \\",
                f"  --source-refs \"https://example.com/capture\" \\",
                f"  --hypothesis {hypothesis} \\",
                f"  --target-audience \"{str(row.get('target_audience') or 'audience') }\"",
                "```",
                "",
            ]
        )

    return "\n".join(lines), candidate_rows


def run_draft(state: dict[str, Any], run_args: argparse.Namespace, repo_root: Path) -> int:
    """Create draft candidates for the next posting batch."""
    out_dir = run_args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = state["stamp"]
    platform_args = ["--platform", run_args.platform] if run_args.platform else []

    export_path = out_dir / f"social_posts_export_{stamp}.json"
    if not export_path.exists():
        run_social_posts(
            ["export", "--days", str(run_args.days), "--format", "json", "--out", str(export_path), *platform_args],
            repo_root,
        )

    rows = load_export_rows(export_path)

    content, _selected_rows = build_draft_plan(rows, run_args.draft_count)
    draft_path = out_dir / f"social_drafts_{stamp}.md"
    draft_path.write_text(content + "\n", encoding="utf-8")

    return 0 if rows else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run social intelligence loop phases.")
    parser.add_argument(
        "--mode",
        choices=("collect", "research", "draft", "full"),
        default="full",
        help="Mode to run.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Window in days for review/export/report sections.",
    )
    parser.add_argument("--platform", default="", help="Filter by platform.")
    parser.add_argument(
        "--out-dir",
        default="operator/social_intelligence",
        help="Output directory for report/research/draft artifacts.",
    )
    parser.add_argument(
        "--draft-count",
        type=int,
        default=3,
        help="Number of draft candidates to produce in draft mode/full mode.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo_root = get_repo_root()
    out_dir = repo_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    args.out_dir = out_dir

    today = datetime.now().astimezone()
    state = {
        "stamp": today.strftime("%Y-%m-%d"),
        "today": today.isoformat(),
        "out_dir": out_dir,
    }

    status = 0
    if args.mode in {"collect", "full"}:
        status = max(status, run_collect(state, args, repo_root))
    if args.mode in {"research", "full"}:
        rows = get_export_rows(state, args, repo_root)
        path = write_research_file(state, args, out_dir, rows)
        print(f"Wrote research file: {path}")
    if args.mode in {"draft", "full"}:
        status = max(status, run_draft(state, args, repo_root))

    if args.mode == "research":
        print(f"Research workflow prepared in {out_dir}")
    elif args.mode == "draft":
        print(f"Draft pack prepared in {out_dir}")
    elif args.mode == "collect":
        print(f"Collect artifacts written to {out_dir}")
    elif args.mode == "full":
        print(f"Full daily workflow complete. Artifacts in {out_dir}")

    return status


if __name__ == "__main__":
    raise SystemExit(main())
