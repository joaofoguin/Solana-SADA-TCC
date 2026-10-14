# Relatorio consolidado: SL-10-INS (`check_sysvar_address`)

## Resumo

A instrução `check_sysvar_address` apresenta uma falha de validação de endereço de Sysvar: a conta `rent` é recebida como `AccountInfo` genérico sem verificação de que seu endereço corresponde ao ID oficial do Sysvar Rent. A análise dinâmica confirmou que uma conta forjada com dados controlados pelo atacante é aceita no lugar do Sysvar, permitindo manipulação de lógica dependente do Rent. A postura de segurança é inadequada para operações que confiam em Sysvars.

## Vulnerabilidades reportadas

### Sysvar Account Check (SYSVAR)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `rent` é recebida como `AccountInfo` sem validação de que seu endereço corresponde ao ID oficial do Sysvar Rent. A análise dinâmica confirmou o ataque: uma conta forjada com dados controlados pelo atacante foi aceita no lugar do Sysvar, demonstrando a falta de validação de endereço e o dano potencial (manipulação de lógica dependente do Rent).
- **Recomendacao:** Substituir o tipo `AccountInfo<'info>` por `Sysvar<'info, Rent>` ou validar explicitamente que `rent.key == &solana_program::sysvar::rent::ID` antes de usar os dados. Alternativamente, usar `Sysvar::from_account_info` para garantir a validação automática do endereço.
