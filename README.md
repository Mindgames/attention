# Mathias Asberg — Personal Projects

This repository tracks Mathias’s personal projects. Each project lives under `projects/` in its own folder and includes a `PROJECT.md` describing the project, milestones, tasks, and any associated files/code for that project.

## Structure

- `projects/<project-name>/` — One folder per project
  - `PROJECT.md` — Project description, milestones, tasks
  - Other files specific to the project (code, notes, assets)

See `projects/README.md` for the current project index.

## OpenAI Agents SDK

This repo keeps tools that use the OpenAI Agents SDK. The `research_bot` project is an example of a personal tool built on it.

- Run: `python -m projects.research_bot.main`
- Run daily focus assistant & coach: `python -m operator.main`
- Requires Python 3.10+ and a configured `.env` with your API key(s)
  - Optional: set `OPERATOR_TZ` (IANA tz like `Europe/Stockholm`) to pin timezone.

## Documentation

- Technical overview of agents and key functions: `archive/technical.md`

## Coaching Flow

- The operator now includes a coaching agent that keeps momentum in chat:
  - Proposes 1–3 bite‑sized next actions and captures them in `tasks.md`.
  - Asks brief clarifying questions when needed and can route to scheduling or project review on demand.
  - Saves a lightweight transcript per day under `operator/sessions/`.
  - Detects future events in your messages and offers to set reminders; reminders are stored in `operator/reminders.jsonl` and surfaced when due.

## Social Posting Routine

Use the social tracking CLI to log posts, capture metrics, and review performance trends.

- Log a new post right after publishing:
  - `python -m operator.social_posts log --platform linkedin --medium post --url "..." --topic "agentic ai" --hook "The dirty reality of agentic AI:"`
- List recent logged posts and IDs:
  - `python -m operator.social_posts list --platform linkedin --days 30`
- Check which posts need metrics updates:
  - `python -m operator.social_posts checkup --platform linkedin`
- Record a metrics snapshot for a post:
  - `python -m operator.social_posts metrics --post-id <id> --impressions 0 --likes 0 --comments 0 --reposts 0`
- Weekly learning review (best hooks, mediums, windows):
  - `python -m operator.social_posts review --platform linkedin --days 30`
- Print the full operating routine:
  - `python -m operator.social_posts routine`

## Add a New Project

1. Create a folder: `projects/<your-project-name>/`
2. Add a `PROJECT.md` (use `projects/PROJECT_TEMPLATE.md` as a starting point) with:
   - Purpose and scope
   - Milestones and tasks
   - Notes on any included files
3. Place all project-specific files inside that folder.

For multi-part programs (e.g., iGaming Change Intelligence), create a parent folder with a program-level `PROJECT.md` and put subprojects as subfolders, each with its own `PROJECT.md`.

## Archived Material

Prior company/investor documents and tools have moved to `archive/` to keep this repository focused on personal projects.
