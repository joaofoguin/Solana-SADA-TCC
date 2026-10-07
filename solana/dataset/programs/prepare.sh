#!/usr/bin/env bash
# Copia os fontes Pinocchio do SSP (sem alteracao) e semeia o Cargo.lock
# com as versoes ja comprovadas no SSP. Nao altera nenhum repositorio-fonte.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SSP="$HOME/sada-tcc/solana/solana-security-pattern"
declare -A P=( [01]=01-missing-signer-check [02]=02-missing-owner-check [03]=03-integer-overflow
               [04]=04-reinitialization-attack [05]=05-pda-bump-canonicalization [06]=06-type-cosplay )
for n in "${!P[@]}"; do
  cp "$SSP/patterns/${P[$n]}/pinocchio/src/lib.rs" "$HERE/pinocchio/ssp_${n}_p/src/lib.rs"
done
[ -f "$HERE/Cargo.lock" ] || cp "$SSP/Cargo.lock" "$HERE/Cargo.lock"
echo "Pinocchio copiado e Cargo.lock semeado."
