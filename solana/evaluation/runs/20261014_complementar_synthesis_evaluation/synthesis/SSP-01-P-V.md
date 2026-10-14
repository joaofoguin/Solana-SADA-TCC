# Relatorio consolidado: SSP-01-P-V (`withdraw`)

## Resumo

A instrução `withdraw` apresenta falhas críticas de autenticação e validação de contas: não verifica a assinatura da autoridade (SIGNER) e não valida o dono da conta vault (OWNER), permitindo que um atacante drene os fundos. Além disso, a ausência de um discriminador de tipo (COSPLAY) possibilita a interpretação de contas de outros tipos como vault, ampliando a superfície de ataque. A postura de segurança é inadequada, exigindo correções imediatas nas verificações de propriedade e assinatura.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a instrução compara a chave pública da autoridade armazenada, mas não verifica `authority.is_signer`. A análise dinâmica confirmou o ataque: sem a assinatura da autoridade, o saque foi aceito e os lamports foram transferidos do vault para o recipient do atacante. A evidência é conclusiva e o dano é direto.
- **Recomendacao:** Adicionar a verificação `authority.is_signer` antes de comparar a chave pública, garantindo que a autoridade assine a transação. Exemplo: `if !authority.is_signer { return Err(ProgramError::MissingRequiredSignature); }`.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática aponta que os dados do vault são lidos sem verificar `vault.owner == program_id`. A análise dinâmica foi inconclusiva porque o ataque proposto não exercitou a hipótese corretamente (a conta forjada tinha o mesmo dono do programa). No entanto, a falha é evidente no código e representa risco real: um atacante pode criar uma conta com layout similar e dono diferente, mas o programa a aceitaria se não houver verificação. A ausência de confirmação dinâmica não invalida a vulnerabilidade estática.
- **Recomendacao:** Adicionar verificação de propriedade: `if vault.owner != program_id { return Err(ProgramError::IncorrectProgramId); }` antes de ler os dados do vault.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática identificou a ausência de um discriminador de tipo no início do buffer, permitindo que contas de outros tipos com layout compatível sejam interpretadas como vault. A análise dinâmica confirmou o ataque: uma conta com discriminador diferente foi aceita, seu saldo foi debitado e os lamports foram transferidos para o recipient. O dano foi verificado.
- **Recomendacao:** Incluir um discriminador de tipo (ex.: um campo de 8 bytes no início dos dados) e verificar seu valor antes de interpretar a conta como vault. Exemplo: `if vault_data[0..8] != VAULT_DISCRIMINATOR { return Err(ProgramError::InvalidAccountData); }`.
