#!/usr/bin/env bash
# Gera o diff de cada port (original da fonte -> versao portada) em docs/ports/.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../../docs/ports"; mkdir -p "$OUT"
SL="$HOME/fontes/sealevel-attacks/programs"
declare -A M=( [00]=0-signer-authorization [02]=2-owner-checks [03]=3-type-cosplay [04]=4-initialization
               [05]=5-arbitrary-cpi [07]=7-bump-seed-canonicalization [10]=10-sysvar-address-checking )
declare -A V=( [ins]=insecure [sec]=secure [rec]=recommended )
for n in "${!M[@]}"; do for v in ins sec rec; do
  diff -u "$SL/${M[$n]}/${V[$v]}/src/lib.rs" "$HERE/sealevel/sl_${n}_${v}/src/lib.rs" > "$OUT/sl_${n}_${v}.diff"
done; done
diff -u "$HOME/sada-tcc/solana/solana-hacks/reinitialization/reinit-attack/src/lib.rs" \
        "$HERE/hacks/hk_reinit/src/lib.rs" > "$OUT/hk_reinit.diff"
wc -l "$OUT"/*.diff | tail -1
grep -h '^[-+][^-+]' "$OUT"/sl_*.diff "$OUT"/hk_reinit.diff | grep -v 'PORT' | sort | uniq -c | sort -rn | head -40
