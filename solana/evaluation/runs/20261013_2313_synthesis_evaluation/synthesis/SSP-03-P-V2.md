# Relatorio consolidado: SSP-03-P-V2 (`burn`)

## Resumo

A instrução `burn` apresenta uma vulnerabilidade crítica de underflow aritmético confirmada dinamicamente, permitindo inflar saldo e supply via wrap-around. A ausência de verificação de proprietário da conta `ledger` é um risco relevante, mas a análise dinâmica foi inconclusiva para demonstrar exploração direta; ainda assim, a falta de autenticação da conta é uma falha de segurança que deve ser corrigida.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática aponta que a conta `ledger` é usada sem verificação de `owner`, permitindo que uma conta forjada com dados controlados pelo atacante seja passada. A análise dinâmica foi inconclusiva: o ataque não conseguiu exercitar a hipótese de owner diferente, pois o runtime impede gravação em contas de outros programas, e o cenário alternativo (conta do próprio programa) não demonstrou dano real. No entanto, a ausência de autenticação da conta é uma falha de segurança que pode viabilizar ataques se combinada com outras vulnerabilidades ou em cenários específicos.
- **Recomendacao:** Adicionar verificação explícita de que `ledger.owner == program_id` antes de ler ou modificar os dados da conta. Alternativamente, utilizar o tipo `Account<'info, Ledger>` do framework Pinocchio/Anchor para garantir a checagem automática de proprietário e a desserialização segura.

### Integer Overflow / Underflow (MATH)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou o uso de `wrapping_sub` para subtrair `amount` de `supply` e `balance`, sem verificação prévia de saldo suficiente. A análise dinâmica confirmou a exploração: um ataque com `amount` maior que o saldo causou underflow, resultando em valores próximos de `u64::MAX` para saldo e supply, conforme verificado no estado das contas. Isso permite a criação arbitrária de tokens, quebrando a integridade do sistema.
- **Recomendacao:** Substituir `wrapping_sub` por `checked_sub` e tratar o erro adequadamente, ou adicionar uma verificação explícita `require!(balance >= amount && supply >= amount, ErrorCode::InsufficientFunds)` antes de realizar as subtrações. Utilizar tipos seguros como `u64` com operações verificadas.
