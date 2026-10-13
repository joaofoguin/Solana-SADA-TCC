# Relatorio consolidado: SL-04-INS (`initialize`)

## Resumo

A instrução `initialize` apresenta falhas críticas de segurança: não verifica o proprietário da conta `user`, não valida discriminador de tipo e não impede reinicialização. Embora a análise dinâmica não tenha confirmado os ataques por falhas no cenário de teste, a análise estática é robusta e as vulnerabilidades são reais e exploráveis. Recomenda-se corrigir urgentemente usando tipos Anchor e constraints de inicialização.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: not_confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática aponta que a conta `user` é um `AccountInfo` sem verificação de owner, permitindo que uma conta forjada de outro programa seja passada e tenha seus dados sobrescritos. A análise dinâmica não confirmou o ataque devido a um panic na desserialização (UnknownError(ProgramFailedToComplete)), mas isso não invalida a vulnerabilidade: o ataque pode ser ajustado para fornecer dados de 32 bytes válidos, contornando o panic e explorando a falta de verificação de owner. A evidência estática é forte e a hipótese é plausível.
- **Recomendacao:** Substituir `AccountInfo` por `Account<'info, User>` ou adicionar verificação explícita `require!(ctx.accounts.user.owner == program_id, ...)` antes de qualquer leitura/escrita. Alternativamente, usar a constraint `#[account(owner = program_id)]`.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática mostra desserialização manual via `User::try_from_slice` sem verificação de discriminador, permitindo que uma conta com layout compatível seja interpretada como `User`. A análise dinâmica foi inconclusiva porque o baseline falhou (UnknownError(ProgramFailedToComplete)), impedindo a avaliação do ataque. No entanto, a vulnerabilidade é teoricamente válida e pode ser explorada se o atacante fornecer uma conta com os 32 bytes iniciais corretos. A confiança é média devido à falta de confirmação dinâmica.
- **Recomendacao:** Utilizar o tipo `Account<'info, User>` do Anchor, que inclui um discriminador de 8 bytes e verifica automaticamente o tipo. Se a desserialização manual for necessária, adicionar um discriminador explícito e verificá-lo antes de desserializar.

### Reinitialization Attacks (REINIT)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática evidencia que a instrução `initialize` grava dados sem verificar se a conta já foi inicializada, permitindo que um atacante chame novamente e sobrescreva o campo `authority`. A análise dinâmica foi inconclusiva porque o ataque não exercitou corretamente a hipótese (o baseline e o ataque não usaram a mesma instrução com estados diferentes), mas o resultado 'Success' no ataque sugere que a sobrescrita pode ocorrer. A falta de flag `is_initialized` ou constraint `init` é uma falha crítica.
- **Recomendacao:** Adicionar uma flag `is_initialized` na struct `User` e verificar no início da instrução, ou usar a constraint `#[account(init, payer = authority, space = 8 + 32)]` do Anchor para garantir que a conta seja inicializada apenas uma vez.
