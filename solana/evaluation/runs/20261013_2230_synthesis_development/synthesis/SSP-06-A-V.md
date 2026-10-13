# Relatorio consolidado: SSP-06-A-V (`update_fee`)

## Resumo

A instrução `update_fee` apresenta falhas críticas de validação de contas: não verifica o proprietário da conta `config` (UncheckedAccount) e desserializa dados manualmente sem validar o discriminador do Anchor, permitindo type cosplay. A análise dinâmica confirmou a exploração do type cosplay, enquanto a falha de owner foi inconclusiva por limitação do ambiente, mas permanece um risco real.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática aponta com alta confiança que a conta `config` é um `UncheckedAccount` sem verificação de proprietário, permitindo que qualquer conta com layout similar seja usada. A análise dinâmica foi inconclusiva devido a um erro de runtime (`ExternalAccountDataModified`) que impediu a demonstração do dano, mas não refutou a vulnerabilidade. A ausência de validação de owner é uma falha grave que pode levar à corrupção de dados ou escalação de privilégios.
- **Recomendacao:** Substituir `UncheckedAccount` por `Account<'info, AdminConfig>` ou adicionar verificação explícita `require_keys_eq!(config.owner, program_id)` antes de qualquer leitura/escrita nos dados da conta.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que os dados são desserializados manualmente sem validar o discriminador de 8 bytes do Anchor, permitindo que contas de tipos diferentes (ex.: `UserData`) sejam passadas como `AdminConfig`. A análise dinâmica confirmou o ataque: uma conta `UserData` foi aceita e seu campo de fee foi sobrescrito, demonstrando o dano real.
- **Recomendacao:** Utilizar o tipo `Account<'info, AdminConfig>` para que o Anchor valide automaticamente o discriminador e o proprietário, ou adicionar verificação manual do discriminador antes de desserializar os dados.
