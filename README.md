# attention-ping

A tiny macOS helper that plays a ping and speaks: "Project NAME needs your attention."
Built as a Codex skill, but it works anywhere you can run bash.

## Features

- Derives the project name from your git remote (with a repo folder fallback).
- Custom sound, message, voice, and speaking rate.
- Optional silent mode for sound or speech.
- Verbose warnings when tools or sound files are missing.

## Requirements

- macOS for `afplay` and `say` (falls back to printing the message if `say` is unavailable).

## Install

Clone into your Codex skills folder:

```bash
git clone https://github.com/Mindgames/attention-ping.git ~/.codex/skills/public/attention-ping
```

Or clone anywhere and run the script directly.

## Usage

Run from inside a git repo so the script can derive the project name:

```bash
scripts/attention-ping.sh
```

Get help:

```bash
scripts/attention-ping.sh --help
```

## Configuration

Set these as environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `ATTENTION_PING_PROJECT` | empty | Override project name. |
| `ATTENTION_PING_REMOTE` | `origin` | Git remote to derive name from. |
| `ATTENTION_PING_MESSAGE` | empty | Full message override. |
| `ATTENTION_PING_SOUND` | `/System/Library/Sounds/Ping.aiff` | Sound file path. |
| `ATTENTION_PING_NO_SOUND` | empty | Disable sound when set to `1`, `true`, `yes`, or `on`. |
| `ATTENTION_PING_NO_SAY` | empty | Disable speech when set to `1`, `true`, `yes`, or `on`. |
| `ATTENTION_PING_SAY_VOICE` | empty | Voice for `say` (example: `Samantha`). |
| `ATTENTION_PING_SAY_RATE` | empty | Rate for `say` (words per minute). |
| `ATTENTION_PING_VERBOSE` | empty | Emit warnings when set to `1`, `true`, `yes`, or `on`. |

## Examples

Override the project name or sound:

```bash
ATTENTION_PING_PROJECT="quiz-juice" scripts/attention-ping.sh
ATTENTION_PING_SOUND="/System/Library/Sounds/Glass.aiff" scripts/attention-ping.sh
```

Choose a different remote and message:

```bash
ATTENTION_PING_REMOTE="upstream" \
ATTENTION_PING_MESSAGE="Heads up: the repo needs you." \
scripts/attention-ping.sh
```

Customize the voice and rate:

```bash
ATTENTION_PING_SAY_VOICE="Samantha" ATTENTION_PING_SAY_RATE=210 scripts/attention-ping.sh
```

Disable sound or speech:

```bash
ATTENTION_PING_NO_SOUND=1 scripts/attention-ping.sh
ATTENTION_PING_NO_SAY=1 scripts/attention-ping.sh
```

Enable verbose warnings:

```bash
ATTENTION_PING_VERBOSE=1 scripts/attention-ping.sh
```

## Troubleshooting

- No sound: check `ATTENTION_PING_SOUND` and enable `ATTENTION_PING_VERBOSE=1` for warnings.
- No speech: `say` may be missing or disabled; the message prints to stdout.
- Wrong project name: set `ATTENTION_PING_PROJECT` or `ATTENTION_PING_REMOTE`.

## How it works

- Uses `git remote get-url` to infer the repo name.
- Falls back to the repo folder name or "this project".
- Plays a short sound and speaks the message.

## Contributing

See `CONTRIBUTING.md` for development and PR guidance.
