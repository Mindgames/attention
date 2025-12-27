---
name: attention-ping
description: Play an alert sound and speak "Project NAME needs your attention." Use at the end of a run or whenever Codex needs user input or confirmation; derive the project name from the git remote (origin) with fallback to the repo folder or an override.
---

# Attention Ping

## Overview

Play a short audible alert and a spoken prompt indicating which project needs attention. Use this as the final step after completing work or right before asking the user for input. This skill is repo-agnostic and can be used in any repository.

## Workflow

1. Run from inside the target repo so the script can read the git remote.
2. Execute `scripts/attention-ping.sh`.
3. Continue with your response to the user.

### Project name resolution

- Primary: `git remote get-url origin` and extract the repo name.
- Remote override: set `ATTENTION_PING_REMOTE`.
- Fallback: repo folder name.
- Override: set `ATTENTION_PING_PROJECT`.

### Sound and speech

- Sound: macOS `afplay` with `/System/Library/Sounds/Ping.aiff` by default.
- Override sound: set `ATTENTION_PING_SOUND`.
- Disable sound: set `ATTENTION_PING_NO_SOUND=1`.
- Speech: macOS `say`; if unavailable, the message prints to stdout.
- Disable speech: set `ATTENTION_PING_NO_SAY=1`.
- Voice: set `ATTENTION_PING_SAY_VOICE`.
- Rate: set `ATTENTION_PING_SAY_RATE`.

### Message override

- Override the full phrase with `ATTENTION_PING_MESSAGE`.

## Example

```bash
ATTENTION_PING_PROJECT="quiz-juice" ATTENTION_PING_SAY_VOICE="Samantha" scripts/attention-ping.sh
```
