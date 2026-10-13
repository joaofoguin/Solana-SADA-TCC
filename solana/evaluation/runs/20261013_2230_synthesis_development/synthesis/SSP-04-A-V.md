# Relatorio consolidado: SSP-04-A-V (`init`)

## Resumo

A instrução `init` apresenta uma vulnerabilidade crítica de reinicialização: a conta `config` é recebida sem `init`/`init_if_needed` e o handler sobrescreve `authority`, `is_initialized` e `vault_balance` sem verificar se a conta já foi inicializada. A análise dinâmica confirmou o ataque, demonstrando que um atacante pode assumir o controle da configuração e zerar o saldo do vault. A postura de segurança é inadequada e requer correção imediata.

## Vulnerabilidades reportadas

### Reinitialization Attacks (REINIT)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `config` é recebida como `Account<'info, Config>` sem `init` ou `init_if_needed`, e o handler sobrescreve `authority`, `is_initialized` e `vault_balance` sem verificar se a conta já foi inicializada. O campo `is_initialized` e o erro `AlreadyInitialized` existem mas não são usados. A análise dinâmica confirmou o ataque: a instrução `init` foi chamada novamente sobre uma conta já inicializada, resultando em sucesso com sobrescrita da autoridade pelo atacante e zeramento do `vault_balance`. Portanto, a vulnerabilidade é real e explorável.
- **Recomendacao:** Adicionar uma verificação explícita no início do handler para garantir que a conta não está inicializada, por exemplo: `require!(!config.is_initialized, ErrorCode::AlreadyInitialized);`. Alternativamente, usar a constraint `init` do Anchor para criar a conta de forma segura, ou `init_if_needed` com verificação de autoridade. Também é recomendado remover a sobrescrita de `authority` e `vault_balance` em chamadas subsequentes, tratando a instrução como inicialização única.
