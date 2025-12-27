# Contributing

Thanks for helping improve attention-ping!

## Guidelines

- Keep changes focused and small.
- Bash only: keep `#!/usr/bin/env bash` and `set -euo pipefail`.
- Use 2-space indentation inside conditionals.
- Avoid network or destructive operations; keep the script side-effect light.
- If behavior changes, update `README.md` and `SKILL.md`.
- If you add tests, place them under `tests/`.

## Development

- Bash syntax check: `bash -n scripts/attention-ping.sh`
- Manual verification: run `scripts/attention-ping.sh` inside a repo and confirm sound, speech, and fallback behavior.

## Pull Requests

- Include a short description of the change.
- List manual verification steps.
- Note any macOS-specific behavior.
