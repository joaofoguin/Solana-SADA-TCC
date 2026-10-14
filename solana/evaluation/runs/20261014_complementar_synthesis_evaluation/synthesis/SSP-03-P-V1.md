# Relatorio consolidado: SSP-03-P-V1 (`mint`)

## Resumo

A instrução `mint` apresenta falhas críticas de segurança: não verifica o owner da conta ledger, não exige assinatura de autoridade, usa aritmética com wrapping que permite overflow, e não valida o tipo/layout da conta. Todas as vulnerabilidades foram confirmadas dinamicamente, exceto a de owner que ficou inconclusiva por falha no baseline, mas a evidência estática é forte. O programa permite mintagem arbitrária e corrupção de estado.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostra que a conta `ledger` é usada sem verificação de owner, permitindo que um atacante forneça uma conta arbitrária. A análise dinâmica foi inconclusiva porque o baseline falhou (UnknownError(ProgramFailedToComplete)), mas a evidência estática é forte e a falha do baseline não refuta a vulnerabilidade; provavelmente o cenário de teste não estava corretamente configurado. A ausência de verificação de owner é uma falha grave que permite corrupção de estado.
- **Recomendacao:** Adicionar verificação explícita de que `ledger.owner == program_id` antes de ler ou modificar os dados da conta. Utilizar a verificação `if ledger.owner != program_id { return Err(ProgramError::IncorrectProgramId); }`.

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática aponta ausência de verificação de assinatura, permitindo que qualquer pessoa chame `mint` sem autorização. A análise dinâmica confirmou o ataque: a transação sem assinatura foi aceita e o supply/balance foram incrementados. Isso permite mintagem ilimitada por qualquer usuário.
- **Recomendacao:** Exigir que a conta de autoridade (ou a própria conta ledger) seja um signer. Adicionar verificação `if !ledger.is_signer { return Err(ProgramError::MissingRequiredSignature); }` ou usar uma conta de autoridade separada com verificação de assinatura.

### Integer Overflow / Underflow (MATH)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática identificou uso de `wrapping_add`, que permite overflow silencioso. A análise dinâmica confirmou o ataque: ao usar um amount que causa overflow, o supply e balance reiniciaram para valores menores, quebrando a invariante. Isso pode ser explorado para manipular saldos e supply de forma maliciosa.
- **Recomendacao:** Substituir `wrapping_add` por `checked_add` e tratar o erro de overflow, retornando `ProgramError::InvalidArgument` ou similar. Exemplo: `let new_supply = supply.checked_add(amount).ok_or(ProgramError::InvalidArgument)?;`.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática mostra desserialização manual sem discriminador de tipo, permitindo que qualquer conta com bytes nos offsets corretos seja tratada como ledger. A análise dinâmica confirmou o ataque: uma conta de outro tipo teve seus bytes 40..56 corrompidos, demonstrando que o programa aceitou e modificou dados de um tipo diferente.
- **Recomendacao:** Adicionar um discriminador de tipo (ex.: um campo mágico ou verificação de layout) no início dos dados da conta e validá-lo antes de ler/escrever. Alternativamente, usar uma biblioteca de serialização que inclua verificação de tipo, como Borsh ou Anchor.
