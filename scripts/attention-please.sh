#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/attention-please.sh
  scripts/attention-please.sh --sound on|off|toggle|status

Plays a sound and speaks "Project NAME needs your attention."

Environment variables:
  ATTENTION_PLEASE_PROJECT   Override project name.
  ATTENTION_PLEASE_REMOTE    Git remote to derive name from (default: origin).
  ATTENTION_PLEASE_MESSAGE   Full message override.
  ATTENTION_PLEASE_SOUND     Sound file path (default: /System/Library/Sounds/Ping.aiff).
  ATTENTION_PLEASE_NO_SOUND  Disable sound when set to 1/true/yes/on.
  ATTENTION_PLEASE_CONFIG_FILE
                             Override persistent config file path.
  ATTENTION_PLEASE_NO_SAY    Disable speech when set to 1/true/yes/on.
  ATTENTION_PLEASE_SAY_VOICE Voice for say (e.g., "Samantha").
  ATTENTION_PLEASE_SAY_RATE  Rate for say (words per minute).
  ATTENTION_PLEASE_VERBOSE   Emit warnings when set to 1/true/yes/on.

Sound commands:
  --sound off                Disable the afplay sound for future runs.
  --sound on                 Enable the afplay sound for future runs.
  --sound toggle             Toggle the persisted sound preference.
  --sound status             Print the current sound preference.
EOF
}

is_truthy() {
  case "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" in
    1|true|yes|on|y) return 0 ;;
    *) return 1 ;;
  esac
}

normalize_sound_state() {
  case "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" in
    1|true|yes|on|y|enabled) printf '%s\n' "on" ;;
    0|false|no|off|n|disabled) printf '%s\n' "off" ;;
    *) return 1 ;;
  esac
}

default_config_file() {
  if [ -n "${ATTENTION_PLEASE_CONFIG_FILE:-}" ]; then
    printf '%s\n' "$ATTENTION_PLEASE_CONFIG_FILE"
  elif [ -n "${XDG_CONFIG_HOME:-}" ]; then
    printf '%s\n' "${XDG_CONFIG_HOME%/}/attention-please/config"
  elif [ -n "${HOME:-}" ]; then
    printf '%s\n' "${HOME%/}/.config/attention-please/config"
  fi
}

read_sound_preference() {
  if [ -z "$config_file" ] || [ ! -f "$config_file" ]; then
    return 1
  fi

  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      sound_enabled=*)
        normalize_sound_state "${line#sound_enabled=}" && return 0
        return 1
        ;;
    esac
  done < "$config_file"

  return 1
}

current_sound_state() {
  read_sound_preference || printf '%s\n' "on"
}

write_sound_preference() {
  local next_state
  next_state="$(normalize_sound_state "$1")"

  if [ -z "$config_file" ]; then
    printf '%s\n' "attention-please: unable to resolve a config file path." >&2
    return 1
  fi

  mkdir -p "$(dirname "$config_file")"
  local tmp_file="${config_file}.tmp.$$"

  {
    if [ -f "$config_file" ]; then
      while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in
          sound_enabled=*) continue ;;
        esac
        printf '%s\n' "$line"
      done < "$config_file"
    fi
    printf 'sound_enabled=%s\n' "$next_state"
  } > "$tmp_file"

  mv "$tmp_file" "$config_file"
}

print_sound_state() {
  printf 'attention-please sound is %s\n' "$(current_sound_state)"
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
config_file="$(default_config_file)"
sound_command=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --sound)
      if [ "$#" -lt 2 ]; then
        printf '%s\n' "attention-please: --sound requires on, off, toggle, or status." >&2
        exit 2
      fi
      sound_command="$2"
      shift 2
      ;;
    --sound=*)
      sound_command="${1#--sound=}"
      shift
      ;;
    *)
      printf '%s\n' "attention-please: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

warn() {
  if is_truthy "$verbose"; then
    printf '%s\n' "attention-please: $*" >&2
  fi
}

if [ -n "$sound_command" ]; then
  sound_command="$(printf '%s' "$sound_command" | tr '[:upper:]' '[:lower:]')"
  case "$sound_command" in
    status)
      print_sound_state
      exit 0
      ;;
    toggle)
      if [ "$(current_sound_state)" = "on" ]; then
        write_sound_preference "off"
      else
        write_sound_preference "on"
      fi
      print_sound_state
      exit 0
      ;;
    *)
      if ! next_state="$(normalize_sound_state "$sound_command")"; then
        printf '%s\n' "attention-please: --sound requires on, off, toggle, or status." >&2
        exit 2
      fi
      write_sound_preference "$next_state"
      print_sound_state
      exit 0
      ;;
  esac
fi

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

sound_state="$(current_sound_state)"
if ! is_truthy "$no_sound" && [ "$sound_state" != "off" ]; then
  if command -v afplay >/dev/null 2>&1; then
    if [ -f "$sound_path" ]; then
      if is_truthy "$verbose"; then
        afplay "$sound_path" &
      else
        afplay "$sound_path" >/dev/null 2>&1 &
      fi
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
    if [ -n "$say_rate" ]; then
      if [[ "$say_rate" =~ ^[0-9]+$ ]]; then
        say_args+=(-r "$say_rate")
      else
        warn "Invalid ATTENTION_PLEASE_SAY_RATE='${say_rate}', expected digits."
      fi
    fi
    if [ -n "$say_voice" ]; then
      say_args+=(-v "$say_voice")
    fi
    say_args+=("$message")

    say_failed=0
    if is_truthy "$verbose"; then
      say "${say_args[@]}" || say_failed=1
    else
      say "${say_args[@]}" >/dev/null 2>&1 || say_failed=1
    fi

    if [ "$say_failed" -ne 0 ]; then
      warn "say failed; printing message."
      printf '%s\n' "$message"
    fi
  else
    warn "say not available; printing message."
    printf '%s\n' "$message"
  fi
fi
