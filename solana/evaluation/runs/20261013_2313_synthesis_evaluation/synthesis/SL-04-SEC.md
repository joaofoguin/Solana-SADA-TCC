# Relatorio consolidado: SL-04-SEC (`initialize`)

## Resumo

A instrução `initialize` apresenta falhas graves de validação de contas: não verifica o proprietário da conta `user`, não utiliza o discriminador de 8 bytes do Anchor e não impede reinicialização. Embora a análise dinâmica não tenha confirmado as explorações por limitações de cenário, as evidências estáticas são fortes e indicam risco crítico de tomada de controle da conta.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: not_confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostra que a conta `user` é recebida como `AccountInfo` e desserializada sem verificar se o proprietário é o programa esperado. A análise dinâmica não confirmou o ataque devido a erro de execução (ProgramFailedToComplete), mas isso não invalida a vulnerabilidade: a ausência de verificação de owner é uma falha crítica que permite forjar dados de conta. A confiança é alta porque a evidência estática é clara e o erro dinâmico pode ser contornado com um cenário mais elaborado.
- **Recomendacao:** Substituir `AccountInfo` por `Account<'info, User>` ou adicionar verificação explícita `if ctx.accounts.user.owner != ctx.program_id { return Err(ProgramError::IncorrectProgramId.into()); }` antes de desserializar os dados.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática evidencia que a desserialização manual com `try_from_slice` e um discriminador booleano simples permite que dados de outro tipo de conta sejam interpretados como `User`. A análise dinâmica foi inconclusiva porque o ataque não exercitou corretamente a hipótese (não alterou o discriminador de 8 bytes), mas a falha permanece: qualquer conta com o primeiro byte `true` pode ser aceita como `User`. A confiança é alta devido à clareza do código.
- **Recomendacao:** Utilizar o wrapper `Account<'info, User>` do Anchor, que valida automaticamente o discriminador de 8 bytes, ou implementar um discriminador único e robusto (ex.: hash de 8 bytes) em vez de um booleano.

### Reinitialization Attacks (REINIT)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostra que a instrução `initialize` não verifica se a conta já foi inicializada, permitindo sobrescrever a authority repetidamente. A análise dinâmica foi inconclusiva porque o ataque não reutilizou o estado resultante do baseline, mas a lógica do programa claramente não impede reinicialização. A confiança é alta pois a ausência de verificação é explícita no código.
- **Recomendacao:** Adicionar verificação de inicialização: `if user.discriminator { return Err(ProgramError::AccountAlreadyInitialized.into()); }` antes de escrever os dados, ou utilizar a macro `#[account(init)]` do Anchor que impede reinicialização.
