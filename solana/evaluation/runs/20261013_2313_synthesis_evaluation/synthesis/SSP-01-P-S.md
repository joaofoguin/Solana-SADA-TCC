# Relatorio consolidado: SSP-01-P-S (`withdraw`)

## Resumo

A instrução `withdraw` apresenta falhas críticas de validação de contas: não verifica o proprietário da conta `vault` e não valida um discriminador de tipo, permitindo que contas forjadas ou de tipos diferentes sejam tratadas como vaults legítimos. A análise dinâmica confirmou a exploração do type cosplay, enquanto a falha de owner permaneceu inconclusiva por limitação do ambiente de teste, mas com forte evidência estática de risco.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática aponta com alta confiança que a conta `vault` é lida sem verificar `vault.owner`, permitindo que um atacante forneça uma conta forjada com dados arbitrários. A análise dinâmica foi inconclusiva porque o ataque esbarrou em uma restrição do runtime (ReadonlyDataModified), não em uma defesa do programa. O erro ocorreu justamente porque o programa tentou modificar uma conta que não lhe pertence, confirmando que a checagem de owner está ausente. A hipótese de ataque é plausível e o dano pode ser demonstrado por outra via, como uma decisão baseada nos dados forjados.
- **Recomendacao:** Adicionar verificação explícita de que `vault.owner == program_id` antes de ler ou modificar seus dados. Utilizar a verificação de owner fornecida pelo framework (ex.: `vault.owner() == program_id`) ou validar via `AccountInfo::owner`.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática identificou desserialização manual por offsets fixos sem validação de discriminador de tipo. A análise dinâmica confirmou o ataque: uma conta de outro tipo com layout compatível foi aceita como vault, teve seu saldo debitado de 1000 para 500 e o recipient recebeu lamports. O dano foi verificado no estado das contas, comprovando a vulnerabilidade de type cosplay.
- **Recomendacao:** Incluir um discriminador de tipo (tag) no início dos dados da conta e validá-lo antes de qualquer leitura. Alternativamente, utilizar uma biblioteca de desserialização segura (ex.: Borsh) que verifique o tipo da conta, ou adicionar uma verificação explícita do discriminador esperado.
