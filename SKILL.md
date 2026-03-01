---
name: attention-please
description: Play an alert sound and speak "Project NAME needs your attention." Always use at the end of every response or whenever Codex needs user input or confirmation; derive the project name from the git remote (origin) with fallback to the repo folder or an override.
---

# Attention Please

## Overview

Play a short audible alert and a spoken prompt indicating which project needs attention. Use this as the final step after completing work on every response, and also right before asking the user for input.

## Source Of Truth And Publishing

- GitHub repository: `https://github.com/Mindgames/attention-please`
- Local development repository: `~/Projects/skills/attention-please`
- Do not edit installed copies in `~/.agents/skills/...` or `~/.codex/skills/...` directly.
- Update this repository, push to GitHub, open a PR, then reinstall via `skills`.

## Install Or Refresh

Install globally (recommended):

```bash
npx skills add Mindgames/attention-please -g -y
```

Install interactively:

```bash
npx skills add Mindgames/attention-please
```

After reinstall, restart your agent client if needed so it reloads skills.

## Path Resolution (avoid missing-skill errors)

- Always open this skill using the absolute path from the active session skills list.
- Do not guess repo-relative `.codex/skills/...` paths unless that exact path was listed by the session.

## Rules (non-negotiable)

- Always run this script at the end of every response, even if you are not asking for input.
- If you missed it in the previous turn, run it immediately at the start of the next turn before doing anything else, then continue.
- Treat a missed run as a bug; prioritize correcting it as soon as you notice.

## Workflow

1. Run from inside the target repo so the script can read the git remote.
2. Execute the installed script using the absolute path from the active session skill list:

   ```bash
   /absolute/path/to/attention-please/scripts/attention-please.sh
   ```

   If your environment does not expose the session skill path directly, use the actual install location used in that session (for example under `~/.agents/...` or `~/.codex/...`) as that absolute path.

3. Run this immediately before sending your final response to the user.
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
