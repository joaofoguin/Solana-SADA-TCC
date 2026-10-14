# Relatorio consolidado: SSP-04-P-S (`init`)

## Resumo

A instrução `init` apresenta uma falha crítica de verificação de assinatura (SIGNER), confirmada dinamicamente, permitindo inicializar a configuração com uma autoridade que não assinou a transação. A ausência de verificação de proprietário (OWNER) não pôde ser confirmada como explorável no ambiente simulado, e a proteção contra reinicialização (REINIT) mostrou-se eficaz no teste dinâmico, embora dependa da flag de inicialização. No geral, a postura de segurança é fraca devido à falta de validação de signatário.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `authority` é gravada como autoridade da configuração sem verificar `is_signer`. A análise dinâmica confirmou o ataque: a configuração foi inicializada com sucesso mesmo sem a assinatura da autoridade, permitindo que um atacante defina uma autoridade sem possuir a chave privada correspondente.
- **Recomendacao:** Adicionar verificação explícita de assinatura: `require!(authority.is_signer, ProgramError::MissingRequiredSignature);` ou utilizar o tipo `Signer` do framework para garantir que a conta assinou a transação.

## Achados descartados

- **OWNER** (execucao: inconclusive): A análise estática apontou ausência de verificação de proprietário da conta `config`. No entanto, a análise dinâmica foi inconclusiva: o ataque não conseguiu exercitar a hipótese de passar uma conta com proprietário diferente, pois o runtime da Solana impede a modificação de contas de terceiros. O cenário testado usou uma conta forjada com o mesmo proprietário do programa, não representando a vulnerabilidade de OWNER. Portanto, não há evidência de exploração bem-sucedida.
- **REINIT** (execucao: not_confirmed): A análise estática levantou a hipótese de reinicialização devido à falta de verificação de proprietário. Contudo, a análise dinâmica demonstrou que a flag de inicialização em `data[40]` bloqueia a reexecução, resultando em erro `AlreadyInitialized`. O ataque foi rejeitado, indicando que a vulnerabilidade não se confirma na prática.
