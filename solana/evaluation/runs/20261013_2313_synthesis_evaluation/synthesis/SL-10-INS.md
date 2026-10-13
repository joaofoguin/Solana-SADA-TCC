# Relatorio consolidado: SL-10-INS (`check_sysvar_address`)

## Resumo

A instrução `check_sysvar_address` recebe o Sysvar Rent como `AccountInfo` genérico sem validar seu endereço oficial, o que representa uma falha de verificação de identidade de conta. A análise dinâmica não pôde confirmar a exploração devido a um erro de compilação no harness, deixando a hipótese de ataque sem evidência empírica. A postura de segurança é frágil, pois a validação de Sysvar é responsabilidade do programa e não foi implementada.

## Vulnerabilidades reportadas

### Sysvar Account Check (SYSVAR)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática identificou com alta confiança que a conta Sysvar Rent é recebida como `AccountInfo` sem verificação de que sua chave pública corresponde ao ID oficial do Sysvar Rent. Isso permite que um atacante forneça uma conta forjada com dados arbitrários, potencialmente manipulando a lógica do programa que depende do Rent. A análise dinâmica foi inconclusiva devido a um erro de compilação no harness de teste, não fornecendo evidência contrária. Portanto, a vulnerabilidade é plausível e deve ser reportada.
- **Recomendacao:** Validar explicitamente que a conta fornecida é o Sysvar Rent oficial, verificando se `rent.key() == solana_program::sysvar::rent::ID`. Alternativamente, utilizar o tipo `Sysvar<'info, Rent>` do Anchor, que realiza essa validação automaticamente, ou adicionar uma restrição `address = solana_program::sysvar::rent::ID` na struct de contas.
