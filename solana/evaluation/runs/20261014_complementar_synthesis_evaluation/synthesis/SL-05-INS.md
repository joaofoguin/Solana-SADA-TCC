# Relatorio consolidado: SL-05-INS (`cpi`)

## Resumo

A instrução `cpi` apresenta falhas de validação de contas que, embora não tenham sido confirmadas dinamicamente por problemas de setup do ambiente de teste, são claramente identificáveis no código-fonte e representam riscos reais. A ausência de verificação do programa destino (CPI arbitrária) e da assinatura da autoridade são vulnerabilidades críticas que podem levar à execução de lógica maliciosa e movimentação não autorizada de tokens. A falta de verificação de proprietário das contas de token também é um risco, embora de menor severidade.

## Vulnerabilidades reportadas

### Arbitrary CPI (CPI)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostra que a conta `token_program` é recebida como `AccountInfo` genérica e usada diretamente na construção da CPI sem validação contra o ID oficial do SPL Token. Isso permite que um atacante forneça um programa malicioso no lugar do token_program, resultando em execução de lógica arbitrária. A análise dinâmica foi inconclusiva porque o baseline falhou com `IncorrectProgramId` devido a problemas de montagem das contas SPL Token, mas isso não invalida a evidência estática robusta. A vulnerabilidade é crítica e deve ser corrigida.
- **Recomendacao:** Validar explicitamente que `token_program.key == &spl_token::ID` antes de realizar a CPI, ou utilizar o tipo `Program<'info, Token>` do Anchor, que realiza essa verificação automaticamente.

### Missing Signer Check (SIGNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática revela que a conta `authority` é recebida como `AccountInfo` genérica e usada como autoridade na transferência SPL sem verificar `is_signer`. Não há `Signer<'info>` nem verificação explícita. Isso permite que um atacante forneça uma autoridade que não assinou a transação, possibilitando movimentar tokens sem consentimento. A análise dinâmica foi inconclusiva devido a falhas no baseline (layout incorreto das contas SPL Token), mas a evidência estática é suficiente para confirmar a vulnerabilidade crítica.
- **Recomendacao:** Exigir que a conta `authority` seja um signatário, utilizando o tipo `Signer<'info>` do Anchor ou adicionando `require!(ctx.accounts.authority.is_signer, ErrorCode::Unauthorized)`.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** media
- **Confianca:** media
- **Justificativa:** A análise estática indica que as contas `source`, `destination` e `authority` são recebidas como `AccountInfo` genéricas sem verificação de que pertencem ao programa SPL Token (`account.owner == spl_token::ID`). Isso pode permitir que contas de outros programas com layout forjado sejam usadas, levando a operações inesperadas. A análise dinâmica foi inconclusiva porque o baseline falhou com `InvalidAccountData` devido a problemas de montagem, mas a evidência estática é razoável. A severidade é média, pois a exploração depende de outras condições, mas a correção é recomendada.
- **Recomendacao:** Verificar que as contas `source`, `destination` e `authority` pertencem ao programa SPL Token, utilizando o tipo `Account<'info, TokenAccount>` do Anchor ou checando explicitamente `account.owner == &spl_token::ID`.
