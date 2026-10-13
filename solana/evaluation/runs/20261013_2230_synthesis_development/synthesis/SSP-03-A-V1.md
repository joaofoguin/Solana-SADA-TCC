# Relatorio consolidado: SSP-03-A-V1 (`mint`)

## Resumo

A instrução `mint` apresenta uma vulnerabilidade crítica de overflow aritmético devido ao uso de `wrapping_add` para atualizar `total_supply` e `user_balance`, permitindo que um atacante manipule os saldos e o suprimento total. A análise dinâmica confirmou que o ataque é bem-sucedido, resultando em valores inconsistentes. Portanto, a instrução não é segura e requer correção imediata.

## Vulnerabilidades reportadas

### Integer Overflow / Underflow (MATH)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou o uso de `wrapping_add` para atualizar `total_supply` e `user_balance`, o que permite overflow silencioso. A análise dinâmica confirmou a exploração: um ataque com `amount=10` e saldo inicial próximo de `u64::MAX` resultou em wrap-around, corrompendo o estado. O dano foi verificado, e o ataque foi aceito pelo programa.
- **Recomendacao:** Substituir `wrapping_add` por `checked_add` e tratar o erro `ArithmeticOverflow` (já definido no enum ErrorCode) para garantir que a transação falhe em caso de overflow. Exemplo: `ledger.total_supply = ledger.total_supply.checked_add(amount).ok_or(ErrorCode::ArithmeticOverflow)?;` e o mesmo para `user_balance`.
