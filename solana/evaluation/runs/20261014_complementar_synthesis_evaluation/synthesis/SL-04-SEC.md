# Relatorio consolidado: SL-04-SEC (`initialize`)

## Resumo

A instrução `initialize` apresenta falhas graves de validação de contas: não verifica o proprietário da conta `user`, usa um discriminador booleano forjável em vez do discriminador Anchor, e não impede reinicialização. Embora os testes dinâmicos não tenham confirmado os ataques de OWNER e COSPLAY (falhas de execução), a análise estática é robusta e o vetor de REINIT permanece plausível, exigindo correções imediatas.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: not_confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática aponta com alta confiança que a conta `user` é desserializada sem verificação de proprietário, permitindo que dados forjados por outro programa sejam aceitos. A análise dinâmica não confirmou o ataque (ProgramFailedToComplete), mas a falha ocorreu por erro de montagem do cenário (dados sem discriminador Anchor), não por rejeição do programa à conta de dono estranho. A vulnerabilidade permanece no código e é explorável com dados corretamente formatados.
- **Recomendacao:** Substituir `AccountInfo` por `Account<'info, User>` ou adicionar verificação explícita `require!(ctx.accounts.user.owner == program_id, ...)` antes de desserializar os dados.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica (execucao: not_confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática identifica que a desserialização manual com um discriminador booleano simples permite que dados de outro tipo de conta sejam interpretados como `User`. A análise dinâmica não confirmou o ataque devido a falha na montagem do cenário (ProgramFailedToComplete), mas a hipótese é tecnicamente válida: qualquer conta com um booleano `true` no início e 32 bytes seguintes pode ser aceita como `User`. A ausência do discriminador Anchor de 8 bytes é a causa raiz.
- **Recomendacao:** Utilizar o wrapper `Account<'info, User>` do Anchor, que valida automaticamente o discriminador de 8 bytes, ou implementar verificação manual do discriminador Anchor antes de desserializar.

### Reinitialization Attacks (REINIT)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** media
- **Justificativa:** A análise estática mostra que a instrução `initialize` não verifica se a conta já foi inicializada, permitindo sobrescrever a `authority`. A análise dinâmica foi inconclusiva: o ataque executou com sucesso (Success), mas o cenário não exercitou corretamente a hipótese de reinicialização (a conta de ataque não partiu de um estado já inicializado diferente do baseline). Apesar da inconclusividade, a falha lógica é evidente e o vetor é plausível, justificando a reportagem com confiança média.
- **Recomendacao:** Adicionar verificação de inicialização: `require!(!user.discriminator, ProgramError::AccountAlreadyInitialized)` antes de escrever na conta, ou usar a macro `#[account(init)]` do Anchor que impede reinicialização.
