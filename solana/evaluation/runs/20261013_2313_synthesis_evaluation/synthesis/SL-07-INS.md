# Relatorio consolidado: SL-07-INS (`set_value`)

## Resumo

A instrução `set_value` apresenta uma falha crítica de validação de PDA: o bump é fornecido pelo usuário e não é verificado como canônico, permitindo que um atacante sobrescreva o valor de uma conta em um endereço alternativo. A análise dinâmica confirmou que o ataque é executável e causa dano real, comprometendo a integridade dos dados associados ao PDA.

## Vulnerabilidades reportadas

### Improper PDA Validation / Canonicalization (PDA)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que o programa usa `create_program_address` com um bump fornecido pelo usuário, sem validar se é o bump canônico. A análise dinâmica confirmou a exploração: um atacante conseguiu criar uma conta em um endereço alternativo e sobrescrever seu `value` chamando `set_value` com um bump não canônico. O ataque foi aceito e o dano verificado, demonstrando que a vulnerabilidade é real e explorável.
- **Recomendacao:** Substituir o uso de `create_program_address` com bump fornecido pelo usuário pela derivação canônica via `Pubkey::find_program_address` ou, preferencialmente, utilizar a constraint `#[account(seeds = [...], bump)]` do Anchor, que valida automaticamente o bump canônico e impede a aceitação de PDAs não canônicos.
