# Relatorio consolidado: SSP-05-A-V (`set_value`)

## Resumo

A instrução `set_value` apresenta uma falha crítica de validação de PDA: o bump é fornecido pelo usuário e usado diretamente em `create_program_address`, sem verificar se é o bump canônico. A análise dinâmica confirmou que um atacante pode fornecer um bump não-canônico e sobrescrever dados em uma conta PDA alternativa, comprometendo a integridade do estado.

## Vulnerabilidades reportadas

### Improper PDA Validation / Canonicalization (PDA)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que o bump é passado como argumento e usado em `create_program_address` sem validação do bump canônico, permitindo PDAs alternativos. A análise dinâmica confirmou o ataque: um bump não-canônico foi aceito e a conta alternativa teve seus campos user/value/bump sobrescritos, demonstrando dano real ao estado. A evidência é conclusiva e a vulnerabilidade é explorável.
- **Recomendacao:** Substituir a derivação manual por `Pubkey::find_program_address` ou utilizar a constraint do Anchor `#[account(seeds = [b"data", user.key().as_ref()], bump)]`, que valida automaticamente o bump canônico e rejeita bumps não-canônicos.
