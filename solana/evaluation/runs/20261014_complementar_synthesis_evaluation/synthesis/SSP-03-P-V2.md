# Relatorio consolidado: SSP-03-P-V2 (`burn`)

## Resumo

A instrução `burn` apresenta falhas críticas de segurança: ausência de verificação de proprietário (owner) e uso de aritmética com wrapping_sub que permite underflow. A análise dinâmica confirmou a exploração do underflow, enquanto a falha de owner foi considerada inconclusiva devido a erro de runtime, mas a evidência estática é forte. Ambas as vulnerabilidades devem ser corrigidas com urgência.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `ledger` é usada sem verificação de proprietário, permitindo que contas forjadas de outros programas sejam passadas. A análise dinâmica foi inconclusiva porque o ataque resultou em erro de runtime (ExternalAccountDataModified), mas isso não invalida a vulnerabilidade: o programa aceitou a entrada e tentou modificar dados de uma conta não pertencente a ele, o que é bloqueado pelo runtime. A ausência de verificação de owner é uma falha crítica que pode levar à manipulação de dados não autenticados.
- **Recomendacao:** Adicione uma verificação explícita de que `ledger.owner == program_id` antes de ler ou modificar os dados da conta. Alternativamente, utilize o tipo `Account<'info, T>` do framework Anchor ou equivalente para garantir a validação automática de proprietário.

### Integer Overflow / Underflow (MATH)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática revelou o uso de `wrapping_sub` para subtrair `amount` de `supply` e `balance`, permitindo underflow silencioso. A análise dinâmica confirmou o ataque: com supply=100 e balance=100, queimar 200 resultou em valores próximos de u64::MAX, demonstrando o wrap-around. O dano é verificado e a exploração é trivial, permitindo inflacionar saldos arbitrariamente.
- **Recomendacao:** Substitua `wrapping_sub` por `checked_sub` e trate o erro adequadamente, ou adicione uma pré-condição `require!(balance >= amount && supply >= amount)` antes das subtrações. Isso garante que a operação falhe de forma segura em caso de underflow.
