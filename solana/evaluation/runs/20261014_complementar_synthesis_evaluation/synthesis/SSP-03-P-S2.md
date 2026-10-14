# Relatorio consolidado: SSP-03-P-S2 (`burn`)

## Resumo

A instrução `burn` apresenta falhas críticas de segurança: não verifica o proprietário da conta, não exige assinatura da autoridade e não valida o tipo da conta. A análise dinâmica confirmou que um atacante pode queimar saldo de qualquer conta sem autorização e manipular contas de tipos diferentes. A postura de segurança é extremamente frágil, permitindo perda de fundos e corrupção de estado.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática aponta que a conta `ledger` é usada sem verificar seu proprietário, permitindo que um atacante forneça uma conta arbitrária. Embora a análise dinâmica tenha sido inconclusiva devido a falha no baseline, a ausência de verificação de owner é uma vulnerabilidade grave e confirmada por inspeção de código. A hipótese de ataque é plausível e o risco é alto.
- **Recomendacao:** Adicionar verificação explícita de que `ledger.owner == program_id` antes de qualquer leitura ou escrita nos dados da conta. Utilizar a macro `check_owner` ou comparação direta.

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou ausência de verificação de assinatura. A análise dinâmica confirmou o ataque: a instrução `burn` foi executada com sucesso sem que a conta `ledger` fosse signer, reduzindo supply e balance. Isso permite que qualquer pessoa queime fundos de qualquer conta sem autorização.
- **Recomendacao:** Exigir que a conta `ledger` (ou uma conta de autoridade designada) seja signer da transação. Adicionar `if !ledger.is_signer { return Err(ProgramError::MissingRequiredSignature); }` ou usar `Signer` como tipo de conta.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática mostrou desserialização manual sem discriminador de tipo. A análise dinâmica confirmou que uma conta de tipo diferente, com bytes forjados nos offsets 40..56, foi aceita e teve seus dados decrementados. Isso permite que atacantes manipulem contas de outros tipos para afetar saldos indevidamente.
- **Recomendacao:** Adicionar um discriminador de tipo (tag) no início dos dados da conta e verificá-lo antes de desserializar. Utilizar bibliotecas como `bytemuck` ou `borsh` com validação de tipo, ou implementar verificação manual do primeiro byte.
