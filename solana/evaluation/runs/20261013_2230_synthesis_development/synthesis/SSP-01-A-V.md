# Relatorio consolidado: SSP-01-A-V (`withdraw`)

## Resumo

A instrução `withdraw` apresenta uma falha crítica de controle de acesso: a conta `authority` é declarada como `AccountInfo` em vez de `Signer`, permitindo que qualquer pessoa drene o vault sem a assinatura da autoridade. A análise dinâmica confirmou a exploração com sucesso, tornando esta vulnerabilidade uma ameaça imediata e de alto impacto.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `authority` é do tipo `AccountInfo`, não `Signer`, e a constraint `has_one = authority` apenas compara chaves, sem verificar `is_signer`. A análise dinâmica confirmou o ataque: a instrução `withdraw` foi executada com sucesso sem a assinatura da autoridade, resultando na perda de lamports do vault e ganho pelo atacante. Portanto, a vulnerabilidade é real e explorável.
- **Recomendacao:** Alterar o tipo da conta `authority` para `Signer<'info>` na struct da instrução `withdraw`, garantindo que o Anchor exija a assinatura da autoridade. Adicionalmente, manter a constraint `has_one = authority` para assegurar que a conta assinante corresponde à autoridade armazenada no vault.
