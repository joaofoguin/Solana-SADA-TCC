# Relatorio consolidado: SSP-05-P-V (`set_value`)

## Resumo

A instrução `set_value` apresenta falhas críticas de validação de contas: ausência de verificação de assinante, aceitação de bump não-canônico para PDA, falta de verificação de owner e ausência de discriminador de tipo. As análises estática e dinâmica confirmaram três dessas vulnerabilidades como exploráveis, permitindo que um atacante grave dados em nome de qualquer usuário, crie PDAs alternativos e corrompa contas de outros tipos. A postura de segurança é inadequada, exigindo correções imediatas.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `user` é usada como autoridade sem verificação de assinatura. A análise dinâmica confirmou o ataque: foi possível gravar dados no PDA da vítima sem que ela assinasse a transação, resultando em dano verificado (gravação da pubkey da vítima e do value do atacante).
- **Recomendacao:** Adicionar verificação explícita de que a conta `user` assinou a transação, por exemplo: `if !user.is_signer() { return Err(ProgramError::MissingRequiredSignature); }`.

### Improper PDA Validation / Canonicalization (PDA)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática mostrou que o bump é fornecido pelo usuário e validado apenas com `create_program_address`, permitindo bumps não-canônicos. A análise dinâmica confirmou que um bump não-canônico foi aceito e gravado, contornando a unicidade do PDA canônico.
- **Recomendacao:** Utilizar `find_program_address` para derivar o PDA canônico e comparar com a conta fornecida, ou validar que o bump fornecido é o canônico (por exemplo, verificando que `create_program_address` com bump+1 falha).

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática apontou ausência de verificação de owner da conta de dados. A análise dinâmica foi inconclusiva: o ataque direto falhou com erro de runtime (`ExternalAccountDataModified`), pois o programa tentou modificar uma conta de outro owner. No entanto, a ausência de verificação é uma falha real que pode ser explorada indiretamente (ex.: leitura de dados forjados para decisões). Portanto, deve ser reportada com confiança média.
- **Recomendacao:** Adicionar verificação de que `data_account.owner == program_id` antes de qualquer leitura ou escrita nos dados da conta.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática indicou ausência de discriminador de tipo, permitindo que contas de layout diferente sejam tratadas como a conta de dados. A análise dinâmica confirmou o ataque: uma conta de outro tipo no mesmo endereço PDA foi aceita e teve seus offsets sobrescritos, corrompendo o estado.
- **Recomendacao:** Incluir um discriminador de tipo (ex.: um byte mágico ou hash do nome da estrutura) no início dos dados da conta e verificá-lo antes de qualquer acesso, rejeitando contas com layout incompatível.
