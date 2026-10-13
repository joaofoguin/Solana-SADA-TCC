# Relatorio consolidado: SSP-04-A-V (`init`)

## Resumo

A instrução `init` apresenta uma vulnerabilidade crítica de reinicialização: a conta `config` é recebida sem `init`/`init_if_needed` e o handler sobrescreve `authority`, `is_initialized` e `vault_balance` sem verificar se a conta já foi inicializada. A análise dinâmica confirmou que um atacante pode chamar novamente a instrução e assumir o controle da configuração e do vault. A postura de segurança é inadequada e requer correção imediata.

## Vulnerabilidades reportadas

### Reinitialization Attacks (REINIT)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `config` é recebida como `Account<'info, Config>` sem `init` ou `init_if_needed`, e o handler sobrescreve `authority`, `is_initialized` e `vault_balance` sem verificar se a conta já foi inicializada. A análise dinâmica confirmou o ataque: a instrução `init` foi chamada novamente sobre uma conta já inicializada, resultando na sobrescrita da autoridade pelo atacante e no zeramento do `vault_balance`. O dano foi verificado no estado da conta, caracterizando uma vulnerabilidade crítica de reinicialização.
- **Recomendacao:** Adicionar uma verificação explícita no início do handler para garantir que a conta `config` não esteja inicializada, por exemplo: `require!(!config.is_initialized, ErrorCode::AlreadyInitialized);`. Alternativamente, utilizar a constraint `init` do Anchor para criar a conta de forma segura, ou `init_if_needed` com verificação de autoridade. Também é recomendável usar o campo `is_initialized` para impedir chamadas repetidas.
