#!/usr/bin/env bash
# Install REAP skills for installed coding agents.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: Python 3 is required to regenerate REAP skills." >&2
  exit 1
fi

python3 tools/build_skills.py
python3 tools/build_system_prompt.py

agent="${1:-all}"
targets=()
case "$agent" in
  hermes) targets=("$HOME/.hermes/skills") ;;
  claude-code|claude) targets=("$HOME/.claude/skills") ;;
  codex) targets=("$HOME/.codex/skills") ;;
  all)
    [[ ! -d "$HOME/.hermes" ]] || targets+=("$HOME/.hermes/skills")
    [[ ! -d "$HOME/.claude" ]] || targets+=("$HOME/.claude/skills")
    [[ ! -d "$HOME/.codex" ]] || targets+=("$HOME/.codex/skills")
    ;;
  *)
    echo "ERROR: Invalid agent '$agent' (hermes | claude-code | codex | all)." >&2
    exit 2
    ;;
esac

if (( ${#targets[@]} == 0 )); then
  echo "ERROR: No agent directory detected; choose hermes, claude-code or codex explicitly." >&2
  exit 1
fi

shopt -s nullglob
packs=(Skills/reap-*/)
if (( ${#packs[@]} != 26 )); then
  echo "ERROR: Expected 26 REAP skill directories, found ${#packs[@]}." >&2
  exit 1
fi

for target in "${targets[@]}"; do
  mkdir -p -- "$target"
  count=0
  for src in "${packs[@]}"; do
    name="${src#Skills/}"
    name="${name%/}"
    mkdir -p -- "$target/$name"
    cp -R -- "$src/." "$target/$name/"
    ((count+=1))
  done
  echo "Installed $count skills into $target"
done
echo "Reload your agent to load the updated REAP skills."
