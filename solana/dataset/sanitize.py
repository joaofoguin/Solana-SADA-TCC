#!/usr/bin/env python3
"""Sanitiza o codigo-fonte de cada caso do Ground Truth antes do Static Agent.

Passos (na ordem):
  1. remove comentarios (//, ///, //!, /* */), preservando strings;
  2. remove chamadas msg!(...) (logs que descrevem a vulnerabilidade);
  3. remove os itens irmaos listados em sanitize.drop_items
     (fn / struct / enum com atributos) e bracos de match que os chamam;
  4. remove consts que ficaram sem uso;
  5. renomeia o modulo do programa para 'target_program';
  6. remove dos identificadores os tokens que entregam o rotulo
     (vulnerable, insecure, secure, recommended);
  7. normaliza linhas em branco e verifica se restou algum termo revelador.

Uso:
  python3 sanitize.py                 # todos os casos
  python3 sanitize.py SSP-01-A-V      # um caso
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = Path.home()
ROOTS = {
    "ssp": HOME / "sada-tcc/solana/solana-security-pattern",
    "sealevel": HOME / "fontes/sealevel-attacks",
    "hacks": HOME / "sada-tcc/solana/solana-hacks",
}
OUT = HERE / "sanitized"
LEAK = re.compile(r"vulnerab|insecure|secure|recommended|exploit|attack|cosplay|canonical",
                  re.IGNORECASE)
LABEL_TOKENS = ["insecure", "vulnerable", "secure", "recommended", "canonical", r"anchor_?native"]


# --------------------------------------------------------------------------- 1
def strip_comments(src: str) -> str:
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c == '"':                                   # string literal
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1]); i = j + 1
        elif src.startswith("//", i):                  # line comment
            j = src.find("\n", i)
            i = n if j == -1 else j
        elif src.startswith("/*", i):                  # block comment (nested)
            depth, j = 1, i + 2
            while j < n and depth:
                if src.startswith("/*", j): depth += 1; j += 2
                elif src.startswith("*/", j): depth -= 1; j += 2
                else: j += 1
            i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def _match_close(src: str, open_idx: int, open_ch: str, close_ch: str) -> int:
    """indice do fechamento correspondente, ignorando strings."""
    depth, j, n = 0, open_idx, len(src)
    while j < n:
        ch = src[j]
        if ch == '"':
            j += 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return j
        j += 1
    raise ValueError("delimitador sem fechamento")


# --------------------------------------------------------------------------- 2
def strip_msg(src: str) -> str:
    while True:
        m = re.search(r"\bmsg!\s*\(", src)
        if not m:
            return src
        end = _match_close(src, m.end() - 1, "(", ")")
        k = end + 1
        while k < len(src) and src[k] in " \t":
            k += 1
        if k < len(src) and src[k] == ";":
            k += 1
        src = src[:m.start()] + src[k:]


# --------------------------------------------------------------------------- 3
def drop_item(src: str, name: str) -> str:
    pat = re.compile(r"(?m)^[ \t]*(?:pub(?:\([^)]*\))?\s+)?(?:fn|struct|enum)\s+" +
                     re.escape(name) + r"\b")
    m = pat.search(src)
    if not m:
        raise ValueError(f"item '{name}' nao encontrado")
    start = m.start()
    # inclui atributos #[...] imediatamente anteriores
    before = src[:start]
    while True:
        mm = re.search(r"(?s)(#\[[^\]]*(?:\[[^\]]*\][^\]]*)*\]\s*)$", before)
        if not mm:
            break
        before = before[:mm.start()]
    start = len(before)
    brace = src.index("{", m.end())
    semi = src.find(";", m.end())
    if semi != -1 and semi < brace:                    # struct tupla / unit
        end = semi
    else:
        end = _match_close(src, brace, "{", "}")
    src = src[:start] + src[end + 1:]
    # bracos de match / dispatch que chamam o item removido
    src = re.sub(r"(?m)^[^\n]*=>\s*" + re.escape(name) + r"\s*\([^\n]*\n", "", src)
    return src


# --------------------------------------------------------------------------- 4
def drop_unused_consts(src: str) -> str:
    changed = True
    while changed:
        changed = False
        for m in re.finditer(r"(?m)^[ \t]*(?:pub\s+)?const\s+([A-Z0-9_]+)\s*:", src):
            name = m.group(1)
            if len(re.findall(r"\b" + name + r"\b", src)) == 1:
                end = src.index(";", m.end())
                src = src[:m.start()] + src[end + 1:]
                changed = True
                break
    return src


# --------------------------------------------------------------------------- 5/6
def rename(src: str) -> str:
    src = re.sub(r"\bmod\s+[A-Za-z_][A-Za-z0-9_]*", "mod target_program", src)

    def clean(tok: str) -> str:
        t = tok
        for w in LABEL_TOKENS:                         # 'insecure' antes de 'secure'
            t = re.sub(w, "", t, flags=re.IGNORECASE)
        t = re.sub(r"__+", "_", t).strip("_")
        return t or "handler"

    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1]); i = j + 1
            continue
        m = re.compile(r"[A-Za-z_][A-Za-z0-9_]*").match(src, i)
        if m and (i == 0 or not (src[i - 1].isalnum() or src[i - 1] == "_")):
            tok = m.group(0)
            out.append(clean(tok) if re.search("|".join(LABEL_TOKENS), tok, re.I) else tok)
            i = m.end()
        else:
            out.append(c); i += 1
    return "".join(out)


# --------------------------------------------------------------------------- 7
def tidy(src: str) -> str:
    src = re.sub(r"[ \t]+\n", "\n", src)
    src = re.sub(r"\n{3,}", "\n\n", src)
    return src.strip() + "\n"


def sanitize_case(case: dict) -> tuple[str, list[str]]:
    if case.get("ported_path"):                        # codigo que vira .so
        path = HERE / case["ported_path"]
    else:
        path = ROOTS[case["source_key"]] / case["program_path"]
    src = path.read_text(encoding="utf-8")
    src = strip_comments(src)
    src = strip_msg(src)
    for item in case["sanitize"]["drop_items"]:
        src = drop_item(src, item)
    src = drop_unused_consts(src)
    src = rename(src)
    src = tidy(src)
    leaks = sorted({m.group(0).lower() for m in LEAK.finditer(src)})
    return src, leaks


def main():
    gt = json.loads((HERE / "ground_truth.json").read_text(encoding="utf-8"))
    only = set(sys.argv[1:])
    OUT.mkdir(exist_ok=True)
    manifest, problems = [], 0
    for case in gt["cases"]:
        if only and case["id"] not in only:
            continue
        try:
            src, leaks = sanitize_case(case)
        except Exception as e:                         # noqa: BLE001
            print(f"[ERRO] {case['id']}: {e}")
            problems += 1
            continue
        (OUT / f"{case['id']}.rs").write_text(src, encoding="utf-8")
        target = rename(case["instruction"])
        ok_target = re.search(r"\bfn\s+" + re.escape(target) + r"\b", src) is not None
        status = "OK " if not leaks and ok_target else "REV"
        if status == "REV":
            problems += 1
        print(f"[{status}] {case['id']:14s} fn={target:22s} vazamentos={leaks or '-'}"
              + ("" if ok_target else "  (instrucao-alvo nao encontrada!)"))
        manifest.append({"id": case["id"], "file": f"sanitized/{case['id']}.rs",
                         "target_instruction": target, "leak_terms": leaks})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(manifest)} arquivos gerados em {OUT}; {problems} para revisar.")


if __name__ == "__main__":
    main()
