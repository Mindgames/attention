---
name: attention-please
description: Play an alert sound and speak "Project NAME needs your attention." Use only when the user explicitly asks for an alert, a long-running task blocks on human input, or a background process finishes and needs attention.
---

# Attention Please

## Overview

Play a short audible alert and a spoken prompt indicating which project needs attention.

Use this only when:
- the user explicitly asks for an audible alert
- a long-running task blocks on human input or confirmation
- a background process finishes and the user should be brought back to the thread

## Source Of Truth And Publishing

- GitHub repository: `https://github.com/Mindgames/attention-please`
- Local development repository: `~/Projects/attention-please`
- Do not edit installed copies in `~/.agents/skills/...` or `~/.codex/skills/...` directly.
- Update this repository, push to GitHub, open a PR, then reinstall via `skills`.

## Install Or Refresh

This repository uses `skills.sh` as the primary install path for Codex, Claude, and most agentic CLI/IDE clients.

Install globally (recommended):

```bash
npx skills add Mindgames/attention-please -g -y
```

Project scope (default):

```bash
npx skills add Mindgames/attention-please
```

Target specific agents (optional):

```bash
npx skills add Mindgames/attention-please --agent codex
```

```bash
npx skills add Mindgames/attention-please --agent claude-code
```

Install for multiple agents in one command:

```bash
npx skills add Mindgames/attention-please --agent codex claude-code -g -y
```

After reinstall, restart your agent client if needed so it reloads skills.

## Path Resolution (avoid missing-skill errors)

- Always open this skill using the absolute path from the active session skills list.
- Do not guess repo-relative `.codex/skills/...` paths unless that exact path was listed by the session.

## Rules

- Do not run this script at the end of ordinary responses.
- Do not run this script at the start of a later turn to compensate for a previous non-run.
- When used, run it immediately before asking for input or reporting the completed background result.

## Workflow

1. Run from inside the target repo so the script can read the git remote.
2. Execute the installed script using the absolute path from the active session skill list:

   ```bash
   /absolute/path/to/attention-please/scripts/attention-please.sh
   ```

   If your environment does not expose the session skill path directly, use the actual install location used in that session (for example under `~/.agents/...` or `~/.codex/...`) as that absolute path.

3. Run this immediately before the attention-worthy user prompt or completion notice.
4. Continue with your response to the user.

### Project name resolution

- Primary: `git remote get-url origin` and extract the repo name.
- Remote override: set `ATTENTION_PLEASE_REMOTE`.
- Fallback: repo folder name.
- Override: set `ATTENTION_PLEASE_PROJECT`.

### Sound and speech

- Sound: macOS `afplay` with `/System/Library/Sounds/Ping.aiff` by default.
- Override sound: set `ATTENTION_PLEASE_SOUND`.
- Disable sound: set `ATTENTION_PLEASE_NO_SOUND=1`.
- Persistently disable sound: run `/absolute/path/to/attention-please/scripts/attention-please.sh --sound off`.
- Persistently enable sound: run `/absolute/path/to/attention-please/scripts/attention-please.sh --sound on`.
- Toggle persisted sound: run `/absolute/path/to/attention-please/scripts/attention-please.sh --sound toggle`.
- Check persisted sound: run `/absolute/path/to/attention-please/scripts/attention-please.sh --sound status`.
- Sound preference is stored in `${XDG_CONFIG_HOME:-~/.config}/attention-please/config`; override with `ATTENTION_PLEASE_CONFIG_FILE`.
- Speech: macOS `say`; if unavailable, the message prints to stdout.
- Disable speech: set `ATTENTION_PLEASE_NO_SAY=1`.
- Voice: set `ATTENTION_PLEASE_SAY_VOICE`.
- Rate: set `ATTENTION_PLEASE_SAY_RATE`.
- If you see `AudioQueueStart failed`, set `ATTENTION_PLEASE_NO_SAY=1` (or `ATTENTION_PLEASE_NO_SOUND=1`) to avoid audio device errors.

### Message override

- Override the full phrase with `ATTENTION_PLEASE_MESSAGE`.

## Example

```bash
ATTENTION_PLEASE_PROJECT="project-name" ATTENTION_PLEASE_SAY_VOICE="Samantha" /absolute/path/to/attention-please/scripts/attention-please.sh
```

```bash
/absolute/path/to/attention-please/scripts/attention-please.sh --sound toggle
```
