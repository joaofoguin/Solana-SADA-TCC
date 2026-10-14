# Relatorio consolidado: SSP-04-P-V (`init`)

## Resumo

A instrução `init` apresenta falhas críticas de validação de contas: não verifica assinatura da autoridade, não valida o owner da conta de configuração, permite reinicialização e não valida o discriminador de tipo. As análises dinâmicas confirmaram as explorações para SIGNER, REINIT e COSPLAY, enquanto OWNER foi considerada inconclusiva por não exercitar a hipótese de owner diferente. A postura de segurança é inadequada, permitindo tomada de controle e sobrescrita indevida de dados.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou ausência de verificação `is_signer` para a conta `authority`, permitindo que qualquer chave pública seja gravada como autoridade. A análise dinâmica confirmou o ataque: a instrução aceitou uma autoridade sem assinatura e gravou sua chave na configuração, demonstrando dano real.
- **Recomendacao:** Adicionar verificação explícita `require!(authority.is_signer, ErrorCode::MissingSignature)` ou utilizar o tipo `Signer` do Pinocchio para garantir que a conta assinou a transação.

### Reinitialization Attacks (REINIT)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostrou que a instrução `init` não verifica se a conta já foi inicializada, permitindo sobrescrever discriminador, autoridade e saldo. A análise dinâmica confirmou: chamar `init` novamente sobre uma conta já inicializada sobrescreveu a autoridade com a chave do atacante.
- **Recomendacao:** Adicionar verificação de estado de inicialização, como checar um flag `is_initialized` antes de escrever, ou utilizar a constraint `init` do Anchor (se aplicável) para garantir que a conta não foi previamente inicializada.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática indicou que os dados são acessados via `AccountInfo` sem validar discriminador de tipo. A análise dinâmica confirmou: uma conta de outro tipo com layout compatível teve seu discriminador sobrescrito com o da config, demonstrando que o programa trata dados de tipos diferentes como config.
- **Recomendacao:** Validar o discriminador de tipo antes de acessar os dados, por exemplo, verificando os primeiros 8 bytes contra o discriminador esperado para o tipo `Config`, ou utilizar o tipo `Account<'info, Config>` que realiza essa validação automaticamente.

## Achados descartados

- **OWNER** (execucao: inconclusive): A análise estática apontou ausência de verificação de owner, mas a análise dinâmica foi inconclusiva: o ataque não exercitou a hipótese de fornecer uma conta com owner diferente, pois o runtime bloqueia modificações em contas de outros programas. Não há evidência de que o programa aceite e modifique contas de owner externo.
