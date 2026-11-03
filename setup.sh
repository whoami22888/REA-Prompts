#!/usr/bin/env bash
# Install the checked-in REAP skills. Regeneration is an explicit developer step.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT="${1:-all}"
if (( $# > 1 )); then
  echo 'usage: setup.sh [hermes|claude-code|codex|all]' >&2
  exit 2
fi

targets=()
case "$AGENT" in
  hermes) targets+=("$HOME/.hermes/skills") ;;
  claude|claude-code) targets+=("$HOME/.claude/skills") ;;
  codex) targets+=("$HOME/.codex/skills") ;;
  all)
    [[ ! -d "$HOME/.hermes" ]] || targets+=("$HOME/.hermes/skills")
    [[ ! -d "$HOME/.claude" ]] || targets+=("$HOME/.claude/skills")
    [[ ! -d "$HOME/.codex" ]] || targets+=("$HOME/.codex/skills")
    ;;
  *) echo "unknown agent: $AGENT" >&2; exit 2 ;;
esac
if (( ${#targets[@]} == 0 )); then
  echo 'No supported agent directory found. Specify hermes, claude-code, or codex to create one.' >&2
  exit 1
fi

for target in "${targets[@]}"; do
  mkdir -p "$target"
  count=0
  for source in "$ROOT"/Skills/reap-*/; do
    [[ -f "${source}SKILL.md" ]] || continue
    name="$(basename "$source")"
    dest="$target/$name"
    stage="$(mktemp -d "$target/.reap-stage.XXXXXXXX")"
    if ! cp -R "${source}." "$stage/"; then
      rm -rf "$stage"
      echo "Failed to stage $name" >&2
      exit 1
    fi
    backup=""
    if [[ -e "$dest" ]]; then
      backup="$(mktemp -d "$target/.reap-backup.XXXXXXXX")"
      if ! mv "$dest" "$backup/$name"; then
        rm -rf "$stage" "$backup"
        echo "Failed to back up $name" >&2
        exit 1
      fi
    fi
    if ! mv "$stage" "$dest"; then
      [[ -z "$backup" ]] || mv "$backup/$name" "$dest"
      rm -rf "$stage"
      [[ -z "$backup" ]] || rm -rf "$backup"
      echo "Failed to install $name" >&2
      exit 1
    fi
    [[ -z "$backup" ]] || rm -rf "$backup"
    count=$((count + 1))
  done
  if (( count != 26 )); then
    echo "Warning: expected 26 REAP skills; installed $count" >&2
    exit 1
  fi
  echo "installed $count skill packs -> $target"
done
printf '\nREAP installed. Reload your agent session to discover the skills.\n'
printf 'For a single prompt document, use %s/system_prompt.md\n' "$ROOT"