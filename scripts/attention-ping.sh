#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/attention-ping.sh

Plays a sound and speaks "Project NAME needs your attention."

Environment variables:
  ATTENTION_PING_PROJECT   Override project name.
  ATTENTION_PING_REMOTE    Git remote to derive name from (default: origin).
  ATTENTION_PING_MESSAGE   Full message override.
  ATTENTION_PING_SOUND     Sound file path (default: /System/Library/Sounds/Ping.aiff).
  ATTENTION_PING_NO_SOUND  Disable sound when set to 1/true/yes/on.
  ATTENTION_PING_NO_SAY    Disable speech when set to 1/true/yes/on.
  ATTENTION_PING_SAY_VOICE Voice for say (e.g., "Samantha").
  ATTENTION_PING_SAY_RATE  Rate for say (words per minute).
  ATTENTION_PING_VERBOSE   Emit warnings when set to 1/true/yes/on.
EOF
}

is_truthy() {
  case "${1:-}" in
    1|true|TRUE|yes|YES|on|ON) return 0 ;;
    *) return 1 ;;
  esac
}

project_name="${ATTENTION_PING_PROJECT:-}"
sound_path="${ATTENTION_PING_SOUND:-/System/Library/Sounds/Ping.aiff}"
remote_name="${ATTENTION_PING_REMOTE:-origin}"
message_override="${ATTENTION_PING_MESSAGE:-}"
say_voice="${ATTENTION_PING_SAY_VOICE:-}"
say_rate="${ATTENTION_PING_SAY_RATE:-}"
no_sound="${ATTENTION_PING_NO_SOUND:-}"
no_say="${ATTENTION_PING_NO_SAY:-}"
verbose="${ATTENTION_PING_VERBOSE:-}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

warn() {
  if is_truthy "$verbose"; then
    printf '%s\n' "attention-ping: $*" >&2
  fi
}

repo_root=""
if command -v git >/dev/null 2>&1; then
  if git rev-parse --show-toplevel >/dev/null 2>&1; then
    repo_root="$(git rev-parse --show-toplevel)"
  fi
else
  warn "git not found; unable to resolve project name from remote."
fi

if [ -z "$project_name" ] && [ -n "$repo_root" ]; then
  remote_url="$(git -C "$repo_root" remote get-url "$remote_name" 2>/dev/null || true)"
  if [ -n "$remote_url" ]; then
    clean="${remote_url%.git}"
    path="$clean"
    if [[ "$clean" == *"://"* ]]; then
      path="${clean#*://}"
      path="${path#*@}"
      path="${path#*/}"
    elif [[ "$clean" == *":"* ]]; then
      path="${clean#*:}"
    fi
    path="${path%/}"
    project_name="${path##*/}"
  else
    warn "No git remote named '${remote_name}' found."
  fi
fi

if [ -z "$project_name" ] && [ -n "$repo_root" ]; then
  project_name="$(basename "$repo_root")"
fi

if [ -z "$project_name" ]; then
  project_name="this project"
fi

if [ -n "$message_override" ]; then
  message="$message_override"
else
  message="Project ${project_name} needs your attention."
fi

if ! is_truthy "$no_sound"; then
  if command -v afplay >/dev/null 2>&1; then
    if [ -f "$sound_path" ]; then
      afplay "$sound_path" &
    else
      warn "Sound file not found: ${sound_path}"
    fi
  else
    warn "afplay not available; skipping sound."
  fi
fi

if is_truthy "$no_say"; then
  printf '%s\n' "$message"
else
  if command -v say >/dev/null 2>&1; then
    say_args=()
    if [ -n "$say_voice" ]; then
      say_args+=("-v" "$say_voice")
    fi
    if [ -n "$say_rate" ]; then
      say_args+=("-r" "$say_rate")
    fi
    say "${say_args[@]}" "$message"
  else
    warn "say not available; printing message."
    printf '%s\n' "$message"
  fi
fi
