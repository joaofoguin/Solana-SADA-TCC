# Relatorio consolidado: SSP-03-P-S1 (`mint`)

## Resumo

A instrução `mint` apresenta falhas críticas de segurança: ausência de verificação de assinatura (SIGNER) e de tipo de conta (COSPLAY), ambas confirmadas dinamicamente, permitindo cunhagem não autorizada e manipulação de contas de outros tipos. A verificação de owner (OWNER) não pôde ser confirmada dinamicamente, mas a evidência estática é forte e a falha é plausível, devendo ser reportada com confiança média.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática mostra que a instrução acessa e modifica dados de accounts[0] sem verificar se o owner é o programa, permitindo que uma conta forjada seja usada. A análise dinâmica foi inconclusiva porque o baseline falhou (UnknownError), impedindo a confirmação do ataque. No entanto, a ausência de verificação de owner é uma vulnerabilidade clara e potencialmente explorável, justificando o reporte com confiança média.
- **Recomendacao:** Adicionar verificação explícita de que `ledger.owner == program_id` antes de qualquer acesso ou modificação dos dados da conta. Em Pinocchio, usar `if ledger.owner != program_id { return Err(ProgramError::IncorrectProgramId); }` ou equivalente.

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou ausência de verificação de assinatura na instrução mint, permitindo cunhagem não autorizada. A análise dinâmica confirmou o ataque: a conta ledger não assinou a transação e mesmo assim o supply e o balance foram incrementados, com sucesso. Isso demonstra uma vulnerabilidade crítica e explorável.
- **Recomendacao:** Exigir que a conta de autoridade (ou a própria ledger) seja signatária da transação. Adicionar verificação `if !ledger.is_signer { return Err(ProgramError::MissingRequiredSignature); }` ou usar um mecanismo de autoridade explícito com verificação de assinatura.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática apontou desserialização manual sem discriminador de tipo, permitindo que contas de outros tipos sejam interpretadas como ledger. A análise dinâmica confirmou o ataque: uma conta de outro tipo teve seus bytes 40..56 incrementados, demonstrando que o programa aceitou e modificou dados de uma conta não destinada a ser ledger.
- **Recomendacao:** Adicionar um discriminador de tipo (tag) no início dos dados da conta e verificá-lo antes de desserializar. Alternativamente, usar um layout de conta com verificação explícita de tipo, como um campo `account_type` ou um identificador único, e rejeitar contas que não correspondam ao tipo esperado.
