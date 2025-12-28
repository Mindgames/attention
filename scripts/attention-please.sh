#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/attention-please.sh

Plays a sound and speaks "Project NAME needs your attention."

Environment variables:
  ATTENTION_PLEASE_PROJECT   Override project name.
  ATTENTION_PLEASE_REMOTE    Git remote to derive name from (default: origin).
  ATTENTION_PLEASE_MESSAGE   Full message override.
  ATTENTION_PLEASE_SOUND     Sound file path (default: /System/Library/Sounds/Ping.aiff).
  ATTENTION_PLEASE_NO_SOUND  Disable sound when set to 1/true/yes/on.
  ATTENTION_PLEASE_NO_SAY    Disable speech when set to 1/true/yes/on.
  ATTENTION_PLEASE_SAY_VOICE Voice for say (e.g., "Samantha").
  ATTENTION_PLEASE_SAY_RATE  Rate for say (words per minute).
  ATTENTION_PLEASE_VERBOSE   Emit warnings when set to 1/true/yes/on.
EOF
}

is_truthy() {
  case "${1:-}" in
    1|true|TRUE|yes|YES|on|ON) return 0 ;;
    *) return 1 ;;
  esac
}

project_name="${ATTENTION_PLEASE_PROJECT:-}"
sound_path="${ATTENTION_PLEASE_SOUND:-/System/Library/Sounds/Ping.aiff}"
remote_name="${ATTENTION_PLEASE_REMOTE:-origin}"
message_override="${ATTENTION_PLEASE_MESSAGE:-}"
say_voice="${ATTENTION_PLEASE_SAY_VOICE:-}"
say_rate="${ATTENTION_PLEASE_SAY_RATE:-}"
no_sound="${ATTENTION_PLEASE_NO_SOUND:-}"
no_say="${ATTENTION_PLEASE_NO_SAY:-}"
verbose="${ATTENTION_PLEASE_VERBOSE:-}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

warn() {
  if is_truthy "$verbose"; then
    printf '%s\n' "attention-please: $*" >&2
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
    if [ "${#say_args[@]}" -gt 0 ]; then
      say "${say_args[@]}" "$message"
    else
      say "$message"
    fi
  else
    warn "say not available; printing message."
    printf '%s\n' "$message"
  fi
fi
