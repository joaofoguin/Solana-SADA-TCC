# Relatorio consolidado: SSP-01-A-V (`withdraw`)

## Resumo

A instrução `withdraw` apresenta uma falha crítica de segurança: a conta `authority` é declarada como `AccountInfo` em vez de `Signer`, permitindo que qualquer pessoa drene o vault sem a assinatura da autoridade legítima. A análise dinâmica confirmou que o ataque é executável e causa dano real, drenando os lamports do vault. Portanto, a instrução não é segura e requer correção imediata.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `authority` é do tipo `AccountInfo`, não `Signer`, e a constraint `has_one = authority` não verifica `is_signer`. A análise dinâmica confirmou o ataque: um withdraw sem assinatura da authority foi aceito e drenou o vault, com dano verificado. A evidência é conclusiva e a vulnerabilidade é crítica.
- **Recomendacao:** Alterar o tipo da conta `authority` para `Signer<'info>` e/ou adicionar a constraint `#[account(signer)]` ou usar `Signer` no struct da conta. Isso garante que a transação exija a assinatura da autoridade legítima.
