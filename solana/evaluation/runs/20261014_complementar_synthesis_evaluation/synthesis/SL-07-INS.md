# Relatorio consolidado: SL-07-INS (`set_value`)

## Resumo

A instrução `set_value` apresenta uma falha crítica de validação de PDA, permitindo que um atacante use um bump não canônico para sobrescrever o valor de uma conta controlada. A análise dinâmica confirmou que o ataque é bem-sucedido, resultando em dano verificado. A postura de segurança é inadequada, necessitando correção imediata.

## Vulnerabilidades reportadas

### Improper PDA Validation / Canonicalization (PDA)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou o uso de `create_program_address` com bump fornecido pelo usuário, sem validar se é o bump canônico. A análise dinâmica confirmou que um atacante pode fornecer um bump não canônico e uma conta controlada nesse endereço alternativo, conseguindo alterar o valor da conta. O ataque foi aceito e o dano verificado, comprovando a vulnerabilidade.
- **Recomendacao:** Substituir a validação manual por `Pubkey::find_program_address` para derivar o bump canônico, ou utilizar a constraint `#[account(seeds = [...], bump)]` do Anchor, que automaticamente valida o bump canônico e a propriedade da conta.
