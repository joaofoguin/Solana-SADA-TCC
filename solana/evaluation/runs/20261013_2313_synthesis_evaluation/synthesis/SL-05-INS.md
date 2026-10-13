# Relatorio consolidado: SL-05-INS (`cpi`)

## Resumo

A instrução `cpi` apresenta falhas de validação de contas que, em teoria, permitem ataques de CPI arbitrária, falta de verificação de assinatura e verificação inadequada de proprietário. No entanto, a análise dinâmica não conseguiu confirmar nenhum dos ataques devido a falhas nos cenários de baseline, resultando em vereditos inconclusivos. Portanto, os achados são reportados com confiança média, mas severidade alta, pois as vulnerabilidades são plausíveis e exigem correção.

## Vulnerabilidades reportadas

### Arbitrary CPI (CPI)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática identificou que a conta `token_program` é usada diretamente na CPI sem validação contra o ID oficial do SPL Token, permitindo que um atacante forneça um programa malicioso. A análise dinâmica tentou explorar a hipótese, mas o baseline falhou com `InvalidAccountData`, impossibilitando a confirmação do ataque. Apesar do veredito inconclusivo, a evidência estática é forte e a vulnerabilidade é plausível, justificando a inclusão no relatório.
- **Recomendacao:** Validar a conta `token_program` contra o ID oficial do SPL Token (ex: `require!(ctx.accounts.token_program.key() == spl_token::ID)`) ou usar o tipo `Program<'info, Token>` do Anchor para garantir que a CPI seja feita apenas para o programa correto.

### Missing Signer Check (SIGNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática mostrou que a conta `authority` é usada como autoridade na transferência SPL sem verificar `is_signer`, permitindo que um atacante forneça uma autoridade não assinante. A análise dinâmica não conseguiu confirmar o ataque porque o baseline falhou com `InvalidAccountData`, mas a hipótese é plausível e a falta de verificação é uma falha grave. Portanto, o achado deve ser reportado.
- **Recomendacao:** Adicionar verificação explícita de assinatura para a conta `authority`, como `require!(ctx.accounts.authority.is_signer, ErrorCode::MissingSignature)`, ou usar o tipo `Signer<'info>` do Anchor para garantir que a conta assinou a transação.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** media
- **Confianca:** media
- **Justificativa:** A análise estática indicou que as contas `source`, `destination` e `authority` não têm verificação de proprietário (deveriam pertencer ao SPL Token). A análise dinâmica não confirmou o ataque devido a falhas no baseline (`InvalidAccountData`), mas a ausência de verificação de proprietário é uma vulnerabilidade que pode levar a operações em contas inválidas. Embora a confiança estática seja média, a falha é relevante e deve ser corrigida.
- **Recomendacao:** Verificar que as contas `source`, `destination` e `authority` pertencem ao programa SPL Token, por exemplo, com `require!(ctx.accounts.source.owner == &spl_token::ID)` (e similar para as outras), ou utilizar os tipos `Account<'info, TokenAccount>` do Anchor que já realizam essa verificação automaticamente.
