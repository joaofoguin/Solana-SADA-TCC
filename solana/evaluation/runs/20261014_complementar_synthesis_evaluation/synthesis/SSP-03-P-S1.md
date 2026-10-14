# Relatorio consolidado: SSP-03-P-S1 (`mint`)

## Resumo

A instrução `mint` apresenta falhas críticas de segurança: ausência de verificação de assinatura (SIGNER) e de tipo de conta (COSPLAY), ambas confirmadas dinamicamente, permitindo cunhagem não autorizada e manipulação de contas de outros tipos. A verificação de owner (OWNER) não pôde ser confirmada dinamicamente, mas a evidência estática sugere risco potencial. A postura geral é insegura, exigindo correções imediatas.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática aponta ausência de verificação de owner da conta ledger, permitindo que uma conta forjada com dados arbitrários seja usada. A análise dinâmica foi inconclusiva: o ataque resultou em erro de runtime (ExternalAccountDataModified) porque o programa tentou gravar em conta de outro dono, mas o plano executado não conseguiu demonstrar dano por outra via. Apesar da inconclusividade, a falha é real e pode ser explorada em cenários onde a conta forjada é usada apenas para leitura e a gravação ocorre em conta do programa, como sugerido no motivo. Portanto, deve ser reportada.
- **Recomendacao:** Adicionar verificação explícita de que `ledger.owner == program_id` antes de acessar ou modificar seus dados. Em Pinocchio, usar `if ledger.owner != program_id { return Err(ProgramError::IncorrectProgramId); }` ou equivalente.

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou ausência de verificação de assinatura na instrução mint, permitindo cunhagem não autorizada. A análise dinâmica confirmou o ataque: a instrução foi executada com sucesso sem a assinatura da conta ledger, e o dano foi verificado (supply e balance aumentaram). Isso representa uma vulnerabilidade crítica que permite a qualquer usuário cunhar tokens arbitrariamente.
- **Recomendacao:** Exigir que a conta de autoridade (ou a própria ledger) seja signatária da transação. Adicionar verificação `if !ledger.is_signer { return Err(ProgramError::MissingRequiredSignature); }` ou usar um mecanismo de autoridade explícito.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática apontou desserialização manual sem verificação de discriminador de tipo, permitindo que contas de outros tipos com layout compatível sejam tratadas como ledger. A análise dinâmica confirmou o ataque: uma conta com discriminador diferente (0xBB) foi aceita e teve supply e balance atualizados, demonstrando a exploração bem-sucedida. Isso pode levar à corrupção de dados de outras contas.
- **Recomendacao:** Adicionar um discriminador de tipo no início dos dados da conta e verificá-lo antes de qualquer desserialização. Por exemplo, reservar os primeiros 8 bytes como identificador único e checar se corresponde ao esperado para a conta ledger.
