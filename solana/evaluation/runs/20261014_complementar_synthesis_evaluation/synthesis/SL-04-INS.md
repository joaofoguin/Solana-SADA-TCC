# Relatorio consolidado: SL-04-INS (`initialize`)

## Resumo

A instrução `initialize` apresenta falhas críticas de validação de contas: não verifica o owner da conta `user`, não usa discriminador de tipo e não impede reinicialização. As análises dinâmicas confirmaram que as vulnerabilidades de COSPLAY e REINIT são exploráveis, enquanto a de OWNER foi rejeitada por um erro de desserialização, mas a ausência de verificação de owner permanece um risco latente. A postura de segurança é fraca, exigindo correções imediatas no tratamento de contas.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: not_confirmed)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática aponta que a conta `user` é um `AccountInfo` sem verificação de owner, permitindo que contas de outros programas sejam passadas. A análise dinâmica não confirmou o ataque devido a um erro de desserialização (ProgramFailedToComplete), mas isso não invalida a vulnerabilidade: o ataque pode ser ajustado para contornar o erro (ex.: conta com 32 bytes e owner malicioso). A ausência de verificação de owner é uma falha grave que pode levar à manipulação de contas não pertencentes ao programa.
- **Recomendacao:** Adicione uma verificação explícita de que `ctx.accounts.user.owner == program_id` ou utilize o tipo `Account<'info, User>` do Anchor, que valida automaticamente o owner e o discriminador.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou desserialização manual sem discriminador de tipo, permitindo que uma conta com layout compatível seja interpretada como `User`. A análise dinâmica confirmou o ataque: uma conta de outro tipo com 32 bytes foi aceita e o campo `authority` foi sobrescrito com a chave do atacante. Isso permite que um atacante assuma o controle de contas que não são do tipo `User`.
- **Recomendacao:** Substitua a desserialização manual por `Account<'info, User>` do Anchor, que inclui um discriminador de 8 bytes e valida o tipo da conta. Se a desserialização manual for necessária, adicione um discriminador explícito e verifique-o antes de desserializar.

### Reinitialization Attacks (REINIT)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostrou que a instrução `initialize` não verifica se a conta já foi inicializada, permitindo sobrescrever o campo `authority`. A análise dinâmica confirmou o ataque: chamar `initialize` novamente em uma conta já inicializada sobrescreveu o `authority` com a chave do atacante. Isso permite que um atacante assuma o controle de contas já inicializadas.
- **Recomendacao:** Adicione uma flag `is_initialized` na estrutura `User` e verifique-a no início da instrução, rejeitando a chamada se já estiver inicializada. Alternativamente, use a constraint `init` do Anchor para garantir que a conta seja criada apenas uma vez.
