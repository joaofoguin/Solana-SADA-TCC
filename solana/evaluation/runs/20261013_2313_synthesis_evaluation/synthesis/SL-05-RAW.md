# Relatorio consolidado: SL-05-RAW (`cpi`)

## Resumo

A instrução `cpi` apresenta duas falhas de validação de contas: não verifica o program_id do programa invocado (Arbitrary CPI) e não valida a assinatura da autoridade (Missing Signer Check). Ambas as hipóteses de ataque são plausíveis e de alto impacto, mas a análise dinâmica não conseguiu confirmá-las devido a erros de compilação nos testes, deixando a exploração sem evidência empírica. A postura de segurança é frágil, exigindo correções imediatas nas validações de contas.

## Vulnerabilidades reportadas

### Arbitrary CPI (CPI)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática aponta com alta confiança que a conta `token_program` é usada diretamente como `program_id` na CPI sem validação, permitindo que um atacante forneça um programa malicioso. A análise dinâmica foi inconclusiva por erro de compilação no teste, não refutando a vulnerabilidade. A ausência de validação é um padrão conhecido de Arbitrary CPI, com potencial de drenar fundos ou manipular contas.
- **Recomendacao:** Validar explicitamente que `ctx.accounts.token_program.key` corresponde ao endereço esperado do Token Program (ex.: `require_keys_eq!(ctx.accounts.token_program.key, spl_token::id())`) ou utilizar o tipo `Program<'info, Token>` do Anchor para garantir a verificação automática.

### Missing Signer Check (SIGNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática indica que a conta `authority` é marcada como signer apenas no `AccountMeta` da CPI interna, mas o programa não verifica `ctx.accounts.authority.is_signer`. Isso permite que uma autoridade arbitrária seja usada sem assinatura, possibilitando operações privilegiadas indevidas. A análise dinâmica foi inconclusiva por erro de compilação, não fornecendo evidência contrária. A falha é crítica em contextos que exigem autorização.
- **Recomendacao:** Adicionar verificação explícita `require!(ctx.accounts.authority.is_signer, ErroCustomizado::NaoAssinado)` ou utilizar o tipo `Signer<'info>` do Anchor para a conta `authority`, garantindo que a assinatura seja validada antes de qualquer CPI.
