# Relatorio consolidado: SSP-02-P-V (`process`)

## Resumo

A instrução `process` apresenta falhas críticas de autorização e validação de contas: não verifica assinatura da autoridade, não valida o proprietário da conta de tesouraria e não confere discriminador de tipo. Todas as hipóteses de ataque foram confirmadas dinamicamente, permitindo execução não autorizada e manipulação de dados. A postura de segurança é inadequada, exigindo correções imediatas.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou ausência de verificação `is_signer` e de comparação entre a chave da conta `authority` e a autoridade armazenada. A análise dinâmica confirmou o ataque: uma conta não assinante foi aceita e a operação privilegiada foi executada sem autorização. Evidência estática e dinâmica convergem para vulnerabilidade explorável.
- **Recomendacao:** Adicionar verificação obrigatória de assinatura e correspondência de chave: `require!(authority.is_signer, ErrorCode::MissingSignature); require!(authority.key() == stored_authority, ErrorCode::Unauthorized);` antes de qualquer operação privilegiada.

### Improper Owner Check (OWNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostrou que os dados da conta `treasury` são lidos sem verificar `treasury.owner == program_id`. A análise dinâmica confirmou que uma conta forjada com owner diferente (System Program) foi aceita e seus dados maliciosos foram lidos, incluindo `balance = 999999`. A falha permite que atacantes controlem dados críticos da tesouraria.
- **Recomendacao:** Validar explicitamente o proprietário da conta: `require!(treasury.owner == program_id, ErrorCode::InvalidOwner);` antes de ler ou modificar seus dados.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática apontou desserialização manual por offsets fixos sem validação de discriminador de tipo. A análise dinâmica confirmou que uma conta com discriminador diferente mas layout compatível foi aceita como tesouraria, permitindo que dados de outro tipo sejam interpretados como válidos. A confirmação dinâmica eleva a confiança de média para alta.
- **Recomendacao:** Incluir um discriminador único no início dos dados da conta e verificá-lo antes da desserialização: `require!(data[0..8] == TREASURY_DISCRIMINATOR, ErrorCode::InvalidAccountType);`.
