# Relatorio consolidado: SSP-03-A-V2 (`burn`)

## Resumo

A instrução `burn` apresenta uma vulnerabilidade crítica de underflow aritmético devido ao uso de `wrapping_sub` sem verificação prévia de saldo, permitindo que um atacante infle seu saldo e corrompa o suprimento total. A análise dinâmica confirmou que o ataque é bem-sucedido, resultando em saldo `u64::MAX` e suprimento corrompido. A postura de segurança é falha e requer correção imediata.

## Vulnerabilidades reportadas

### Integer Overflow / Underflow (MATH)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou o uso de `wrapping_sub` sem verificação de saldo, permitindo underflow. A análise dinâmica confirmou a exploração: chamar `burn` com `amount=1` quando `user_balance=0` resultou em `user_balance = u64::MAX` e `total_supply` corrompido, com sucesso na execução. Evidência consistente e dano verificado.
- **Recomendacao:** Substituir `wrapping_sub` por `checked_sub` e tratar o erro com `ErrorCode::ArithmeticUnderflow`. Adicionar verificação explícita `require!(ledger.user_balance >= amount, ErrorCode::ArithmeticUnderflow);` antes da subtração. Considerar também verificar `total_supply >= amount` para evitar underflow no suprimento total.
