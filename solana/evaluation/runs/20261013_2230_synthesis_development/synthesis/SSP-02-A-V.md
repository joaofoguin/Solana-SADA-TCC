# Relatorio consolidado: SSP-02-A-V (`process`)

## Resumo

A instrução `process` apresenta falhas críticas de validação de contas: tanto a verificação de proprietário quanto a de discriminador de tipo estão ausentes, permitindo que contas forjadas ou de tipos diferentes sejam aceitas e usadas. Ambas as vulnerabilidades foram confirmadas dinamicamente, indicando alto risco de manipulação de estado e bypass de lógica de negócio.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `treasury` é do tipo `AccountInfo` e seus dados são lidos sem verificar se o proprietário é o programa atual. A análise dinâmica confirmou o ataque: uma conta forjada com dono diferente foi aceita e usada pela instrução, resultando em sucesso e dano verificado. A ausência de verificação de owner permite que atacantes forneçam contas maliciosas com dados arbitrários, comprometendo a integridade do estado.
- **Recomendacao:** Substituir `AccountInfo` por `Account<'info, Treasury>` para que o Anchor valide automaticamente o proprietário da conta. Caso seja necessário manter `AccountInfo`, adicionar verificação explícita: `require!(treasury.owner == program_id, ErroCustomizado::OwnerInvalido);` antes de ler os dados.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostrou que os dados são desserializados manualmente a partir de offsets fixos sem validar o discriminador de 8 bytes do Anchor. A análise dinâmica confirmou que uma conta com discriminador diferente de `Treasury` foi aceita e processada com sucesso, caracterizando type cosplay. Isso permite que contas de outros tipos ou com dados arbitrários sejam interpretadas como `Treasury`, burlando a lógica de negócio.
- **Recomendacao:** Utilizar o tipo `Account<'info, Treasury>` para que o Anchor valide automaticamente o discriminador. Se a desserialização manual for inevitável, verificar explicitamente os primeiros 8 bytes contra o discriminador esperado: `require!(&data[0..8] == Treasury::DISCRIMINATOR, ErroCustomizado::DiscriminadorInvalido);` antes de ler os campos.
