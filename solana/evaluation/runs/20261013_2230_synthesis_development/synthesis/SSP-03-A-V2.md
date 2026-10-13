# Relatorio consolidado: SSP-03-A-V2 (`burn`)

## Resumo

A instrução `burn` apresenta uma falha crítica de segurança: usa `wrapping_sub` sem verificação de saldo, permitindo underflow que infla o saldo do usuário e corrompe o `total_supply`. A análise dinâmica confirmou que o ataque é aceito e causa dano real (saldo torna-se `u64::MAX`), apesar do veredito automático ter sido `not_confirmed` por erro na avaliação do estado. A postura de segurança é inadequada, exigindo correção imediata.

## Vulnerabilidades reportadas

### Integer Overflow / Underflow (MATH)

- **Origem:** Estatica (execucao: not_confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou o uso de `wrapping_sub` sem verificação prévia de saldo, permitindo underflow. A análise dinâmica executou o ataque com `amount=1` e `user_balance=0`, resultando em `user_balance = u64::MAX` (conforme estado da conta: `ffffffffffffffff` no offset do saldo). O veredito automático `not_confirmed` está incorreto, pois o dano ocorreu: o saldo foi inflado e o `total_supply` corrompido. A evidência dinâmica confirma a exploração bem-sucedida.
- **Recomendacao:** Substituir `wrapping_sub` por `checked_sub` e tratar o erro com `ErrorCode::ArithmeticUnderflow`. Adicionar verificação explícita `require!(ledger.user_balance >= amount, ErrorCode::ArithmeticUnderflow)` antes da subtração. Para o `total_supply`, usar `checked_sub` e garantir que não haja underflow.
