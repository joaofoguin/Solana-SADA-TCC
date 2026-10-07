#!/usr/bin/env bash
# Compila cada programa isoladamente para .so; uma falha nao interrompe as demais.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
mkdir -p deploy logs
: > logs/RESUMO.txt
for toml in sealevel/*/Cargo.toml hacks/*/Cargo.toml pinocchio/*/Cargo.toml aux/*/Cargo.toml; do
  d=$(dirname "$toml"); n=$(basename "$d")
  if cargo build-sbf --manifest-path "$toml" --sbf-out-dir "$HERE/deploy" > "logs/$n.log" 2>&1; then
    echo "[OK  ] $n" | tee -a logs/RESUMO.txt
  else
    echo "[FAIL] $n  -> logs/$n.log" | tee -a logs/RESUMO.txt
    grep -m3 -E '^error' "logs/$n.log" | sed 's/^/        /' | tee -a logs/RESUMO.txt
  fi
done
echo; ls -la deploy/*.so 2>/dev/null | awk '{print $5, $9}'
