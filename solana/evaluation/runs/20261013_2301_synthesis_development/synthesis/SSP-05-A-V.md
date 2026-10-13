# Relatorio consolidado: SSP-05-A-V (`set_value`)

## Resumo

A instrução `set_value` apresenta uma falha crítica de validação de PDA: o bump é fornecido pelo usuário e usado diretamente em `create_program_address`, sem verificar se é o bump canônico. A análise dinâmica confirmou que um atacante pode explorar um bump não-canônico para sobrescrever dados em uma conta PDA alternativa, comprometendo a integridade do estado.

## Vulnerabilidades reportadas

### Improper PDA Validation / Canonicalization (PDA)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que o bump é passado como argumento e validado apenas com `create_program_address`, que não garante o bump canônico. A análise dinâmica confirmou o ataque: um bump não-canônico foi aceito e a conta PDA alternativa teve seus dados sobrescritos, enquanto o PDA canônico permaneceu intacto. Isso permite que um atacante controle contas em endereços PDA não-canônicos e modifique estado indevidamente.
- **Recomendacao:** Substituir a validação manual por `Pubkey::find_program_address` ou utilizar a constraint `#[account(seeds = [b"data", user.key().as_ref()], bump)]` do Anchor, que deriva e valida automaticamente o bump canônico, rejeitando bumps não-canônicos.
