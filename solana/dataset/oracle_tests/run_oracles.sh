#!/usr/bin/env bash
# Executa os testes-oraculo contra os .so em dataset/programs/deploy
# e registra o resultado no Ground Truth.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DS="$(cd "$HERE/.." && pwd)"
LOGS="$DS/../evaluation/oracle_runs"; mkdir -p "$LOGS"
STAMP=$(date +%F_%H%M)
[ -f "$HERE/Cargo.lock" ] || cp "$HOME/sada-tcc/solana/solana-security-pattern/Cargo.lock" "$HERE/Cargo.lock"

export SBF_OUT_DIR="$DS/programs/deploy"
export RUST_LOG=error
cargo test --manifest-path "$HERE/Cargo.toml" -- --test-threads=1 \
  > "$LOGS/oracle_$STAMP.out" 2> "$LOGS/oracle_$STAMP.err"
echo "cargo test terminou com codigo $?"

if ! grep -q '^test result' "$LOGS/oracle_$STAMP.out"; then
  echo "Nenhum teste executou (provavel erro de compilacao). Ultimas linhas:"
  grep -E '^(error|warning: unused)' -A6 "$LOGS/oracle_$STAMP.err" | head -60
  exit 1
fi
grep -E '^test result' "$LOGS/oracle_$STAMP.out"
python3 "$DS/apply_oracles.py" "$LOGS/oracle_$STAMP.out"
