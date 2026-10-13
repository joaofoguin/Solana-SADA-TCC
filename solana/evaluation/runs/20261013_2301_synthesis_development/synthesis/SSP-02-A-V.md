# Relatorio consolidado: SSP-02-A-V (`process`)

## Resumo

A instrução `process` apresenta falhas críticas de validação de contas: tanto a verificação de proprietário quanto a validação do discriminador de tipo estão ausentes, permitindo que contas forjadas ou de tipos diferentes sejam aceitas e processadas. Ambas as vulnerabilidades foram confirmadas dinamicamente, resultando em alto risco de manipulação de estado e bypass de lógica de negócio.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `treasury` é do tipo `AccountInfo` e seus dados são lidos diretamente sem verificar se o proprietário é o programa atual. A análise dinâmica confirmou o ataque: uma conta forjada com dono diferente do programa foi aceita e usada com sucesso, mantendo os dados forjados. Isso permite que atacantes contornem a validação de estado e manipulem a lógica do programa.
- **Recomendacao:** Substituir `AccountInfo` por `Account<'info, Treasury>` para que o Anchor valide automaticamente o proprietário da conta. Caso seja necessário manter `AccountInfo`, adicionar uma verificação explícita: `require!(ctx.accounts.treasury.owner == ctx.program_id, ErrorCode::InvalidOwner);` antes de acessar os dados.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostrou que os dados são desserializados manualmente a partir de offsets fixos sem validar o discriminador de 8 bytes do Anchor. A análise dinâmica confirmou que uma conta com discriminador incorreto (de outro tipo) foi processada com sucesso, demonstrando que o programa aceita contas que não são do tipo `Treasury`. Isso permite que atacantes forneçam contas com layout semelhante para manipular campos como `authority`, `balance` e `is_active`.
- **Recomendacao:** Utilizar o tipo `Account<'info, Treasury>` em vez de `AccountInfo` para que o Anchor valide automaticamente o discriminador. Se a desserialização manual for necessária, verificar explicitamente os primeiros 8 bytes do buffer contra o discriminador esperado de `Treasury` antes de ler os campos: `require!(&data[0..8] == Treasury::DISCRIMINATOR, ErrorCode::InvalidDiscriminator);`.
