# Relatorio consolidado: HK-REINIT-V (`initialize`)

## Resumo

A instrução `initialize` apresenta falhas críticas de segurança: ausência de verificação de assinatura, falta de controle de proprietário, possibilidade de reinicialização e vulnerabilidade a type cosplay. Os ataques de SIGNER, REINIT e COSPLAY foram confirmados dinamicamente, enquanto OWNER não pôde ser testado por erro de compilação, mas a evidência estática é forte. A postura geral é insegura, permitindo que atacantes assumam o controle de contas de usuário.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a autoridade é definida sem verificar `is_signer`. A análise dinâmica confirmou o ataque: a conta `user` teve sua autoridade definida para a chave do atacante sem assinatura, com sucesso e dano verificado.
- **Recomendacao:** Adicionar verificação `authority_info.is_signer` antes de atribuir a autoridade, garantindo que a chave fornecida assinou a transação.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática aponta ausência de verificação de proprietário, permitindo manipular contas de outros programas. A análise dinâmica foi inconclusiva devido a erro de compilação no harness, mas a evidência estática é forte e a falha é plausível.
- **Recomendacao:** Verificar se `user_info.owner == program_id` antes de desserializar e modificar os dados da conta.

### Reinitialization Attacks (REINIT)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostra que não há verificação de inicialização. A análise dinâmica confirmou o ataque: a autoridade original foi sobrescrita pela chave do atacante ao reexecutar `initialize` sobre uma conta já inicializada.
- **Recomendacao:** Implementar uma flag de inicialização (ex.: `is_initialized`) e verificar antes de permitir a reinicialização, ou usar o mecanismo `init` do Anchor que impede reexecução.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática indica desserialização sem discriminador de tipo. A análise dinâmica confirmou o ataque: uma conta de outro tipo (Vault) com 32 bytes teve seus primeiros 32 bytes sobrescritos com a chave do atacante.
- **Recomendacao:** Adicionar um discriminador de tipo (ex.: campo `discriminator` ou uso de `#[account]` do Anchor) e verificar antes de desserializar, garantindo que a conta seja do tipo `User`.
