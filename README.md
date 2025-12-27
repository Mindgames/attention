# attention-please

A tiny macOS helper that plays a ping and speaks: "Project NAME needs your attention."
Built as a Codex skill and compatible with Claude Code / Claude CLI, but it works anywhere you can run bash.

## Features

- Derives the project name from your git remote (with a repo folder fallback).
- Custom sound, message, voice, and speaking rate.
- Optional silent mode for sound or speech.
- Verbose warnings when tools or sound files are missing.

## Requirements

- macOS for `afplay` and `say` (falls back to printing the message if `say` is unavailable).

## Install

### Codex (global)

Clone into your Codex skills folder:

```bash
git clone https://github.com/Mindgames/attention-please.git ~/.codex/skills/public/attention-please
```

Run it directly from that location:

```bash
~/.codex/skills/public/attention-please/scripts/attention-please.sh
```

### Claude Code / Claude CLI (global)

Clone into your Claude skills folder:

```bash
git clone https://github.com/Mindgames/attention-please.git ~/.claude/skills/attention-please
```

Restart Claude Code/CLI so it loads the skill.

### Install in a specific repo (shared)

Use a submodule to keep updates clean:

```bash
git submodule add https://github.com/Mindgames/attention-please.git tools/attention-please
git submodule update --init --recursive
```

Then run it from your repo:

```bash
tools/attention-please/scripts/attention-please.sh
```

If you want Claude Code/CLI to load it as a project skill, add a second checkout under `.claude/skills/`:

```bash
git submodule add https://github.com/Mindgames/attention-please.git .claude/skills/attention-please
```

Restart Claude Code/CLI so it picks up the project skill.

## Usage

Run from inside a git repo so the script can derive the project name:

```bash
scripts/attention-please.sh
```

Get help:

```bash
scripts/attention-please.sh --help
```

## Configuration

Set these as environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `ATTENTION_PLEASE_PROJECT` | empty | Override project name. |
| `ATTENTION_PLEASE_REMOTE` | `origin` | Git remote to derive name from. |
| `ATTENTION_PLEASE_MESSAGE` | empty | Full message override. |
| `ATTENTION_PLEASE_SOUND` | `/System/Library/Sounds/Ping.aiff` | Sound file path. |
| `ATTENTION_PLEASE_NO_SOUND` | empty | Disable sound when set to `1`, `true`, `yes`, or `on`. |
| `ATTENTION_PLEASE_NO_SAY` | empty | Disable speech when set to `1`, `true`, `yes`, or `on`. |
| `ATTENTION_PLEASE_SAY_VOICE` | empty | Voice for `say` (example: `Samantha`). |
| `ATTENTION_PLEASE_SAY_RATE` | empty | Rate for `say` (words per minute). |
| `ATTENTION_PLEASE_VERBOSE` | empty | Emit warnings when set to `1`, `true`, `yes`, or `on`. |

## Examples

Override the project name or sound:

```bash
ATTENTION_PLEASE_PROJECT="quiz-juice" scripts/attention-please.sh
ATTENTION_PLEASE_SOUND="/System/Library/Sounds/Glass.aiff" scripts/attention-please.sh
```

Choose a different remote and message:

```bash
ATTENTION_PLEASE_REMOTE="upstream" \
ATTENTION_PLEASE_MESSAGE="Heads up: the repo needs you." \
scripts/attention-please.sh
```

Customize the voice and rate:

```bash
ATTENTION_PLEASE_SAY_VOICE="Samantha" ATTENTION_PLEASE_SAY_RATE=210 scripts/attention-please.sh
```

Disable sound or speech:

```bash
ATTENTION_PLEASE_NO_SOUND=1 scripts/attention-please.sh
ATTENTION_PLEASE_NO_SAY=1 scripts/attention-please.sh
```

Enable verbose warnings:

```bash
ATTENTION_PLEASE_VERBOSE=1 scripts/attention-please.sh
```

## Automatic usage

### Codex (AGENTS.md in your target repo)

Add a short instruction so Codex runs the skill automatically when it needs your attention:

```markdown
## Codex
- Use the attention-please skill at the end of a run or before asking for input by running `tools/attention-please/scripts/attention-please.sh`.
```

If you installed it globally or vendored it into `scripts/`, adjust the path accordingly.

### Claude Code / Claude CLI

Claude loads skills automatically from `~/.claude/skills/` (personal) or `.claude/skills/` (project).
Once installed, just restart Claude and it will apply the skill when your request matches the description.

## Troubleshooting

- No sound: check `ATTENTION_PLEASE_SOUND` and enable `ATTENTION_PLEASE_VERBOSE=1` for warnings.
- No speech: `say` may be missing or disabled; the message prints to stdout.
- Wrong project name: set `ATTENTION_PLEASE_PROJECT` or `ATTENTION_PLEASE_REMOTE`.

## How it works

- Uses `git remote get-url` to infer the repo name.
- Falls back to the repo folder name or "this project".
- Plays a short sound and speaks the message.

## Contributing

See `CONTRIBUTING.md` for development and PR guidance.
