# Relatorio consolidado: SL-05-RAW (`cpi`)

## Resumo

A instrução `cpi` apresenta uma vulnerabilidade crítica de CPI arbitrária, confirmada dinamicamente, permitindo a invocação de programas maliciosos. A ausência de verificação de signer na conta `authority` não é explorável devido à proteção do runtime do Solana, que rejeita a escalada de privilégio. A postura de segurança é fraca, exigindo correção imediata da validação do programa destino.

## Vulnerabilidades reportadas

### Arbitrary CPI (CPI)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `token_program` é usada diretamente como `program_id` sem validação, permitindo CPI arbitrária. A análise dinâmica confirmou o ataque: um programa malicioso foi invocado com sucesso, demonstrando dano potencial. A evidência é consistente e a exploração é viável.
- **Recomendacao:** Validar que `token_program.key` corresponde ao endereço esperado do Token Program (ex.: `spl_token::id()`), usando `require_keys_eq!` ou tipagem `Program<'info, Token>`. Alternativamente, restringir a CPI a programas conhecidos e confiáveis.

## Achados descartados

- **SIGNER** (execucao: not_confirmed): A análise estática apontou ausência de verificação `is_signer` na conta `authority`. No entanto, a análise dinâmica mostrou que o ataque foi rejeitado pelo runtime com `PrivilegeEscalation`, pois a CPI exige que a autoridade seja signer e o runtime impede a escalada. Portanto, a hipótese não é explorável no ambiente Solana.
