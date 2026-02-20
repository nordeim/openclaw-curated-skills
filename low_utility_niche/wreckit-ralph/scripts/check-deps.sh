#!/usr/bin/env bash
# wreckit — verify declared dependencies exist in registries
# Usage: ./check-deps.sh [project-path]
# Outputs hallucinated deps to stdout (one per line)
# Exit 0 = all deps real, Exit 1 = hallucinated deps found

set -euo pipefail
PROJECT="${1:-.}"
cd "$PROJECT"
HALLUCINATED=()

check_npm() {
  local pkg="$1"
  # Skip scoped packages with complex names, builtins
  [[ "$pkg" == node:* ]] && return 0
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://registry.npmjs.org/$pkg" 2>/dev/null || echo "000")
  if [ "$status" = "404" ]; then
    HALLUCINATED+=("npm:$pkg")
  fi
}

check_pypi() {
  local pkg="$1"
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/pypi/$pkg/json" 2>/dev/null || echo "000")
  if [ "$status" = "404" ]; then
    HALLUCINATED+=("pypi:$pkg")
  fi
}

check_crate() {
  local pkg="$1"
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://crates.io/api/v1/crates/$pkg" 2>/dev/null || echo "000")
  if [ "$status" = "404" ]; then
    HALLUCINATED+=("crate:$pkg")
  fi
}

# npm/yarn
if [ -f "package.json" ]; then
  deps=$(python3 -c "
import json,sys
d=json.load(open('package.json'))
for k in ['dependencies','devDependencies']:
  for p in d.get(k,{}):
    if not p.startswith('@types/'): print(p)
" 2>/dev/null || true)
  for pkg in $deps; do
    check_npm "$pkg"
  done
fi

# Python
if [ -f "requirements.txt" ]; then
  while IFS= read -r line; do
    pkg=$(echo "$line" | sed 's/[>=<!\[].*//;s/#.*//' | tr -d '[:space:]')
    [ -n "$pkg" ] && check_pypi "$pkg"
  done < requirements.txt
elif [ -f "pyproject.toml" ]; then
  deps=$(python3 -c "
try:
  import tomllib
except: import tomli as tomllib
with open('pyproject.toml','rb') as f: d=tomllib.load(f)
for dep in d.get('project',{}).get('dependencies',[]):
  print(dep.split('>')[0].split('<')[0].split('=')[0].split('[')[0].strip())
" 2>/dev/null || true)
  for pkg in $deps; do
    check_pypi "$pkg"
  done
fi

# Rust
if [ -f "Cargo.toml" ]; then
  deps=$(python3 -c "
try:
  import tomllib
except: import tomli as tomllib
with open('Cargo.toml','rb') as f: d=tomllib.load(f)
for dep in d.get('dependencies',{}):
  print(dep)
" 2>/dev/null || true)
  for pkg in $deps; do
    check_crate "$pkg"
  done
fi

if [ ${#HALLUCINATED[@]} -gt 0 ]; then
  echo "HALLUCINATED DEPENDENCIES FOUND:"
  for h in "${HALLUCINATED[@]}"; do
    echo "  ❌ $h"
  done
  exit 1
else
  echo "All dependencies verified in registries."
  exit 0
fi
