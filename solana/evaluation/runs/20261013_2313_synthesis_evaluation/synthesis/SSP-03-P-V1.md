# Relatorio consolidado: SSP-03-P-V1 (`mint`)

## Resumo

A instrucao `mint` apresenta falhas criticas de seguranca: nao verifica a assinatura da autoridade, nao valida o owner da conta ledger, nao usa aritmetica segura e nao possui discriminador de tipo. As analises dinamicas confirmaram exploracoes bem-sucedidas para SIGNER, MATH e COSPLAY, enquanto o achado OWNER ficou inconclusivo por falha no cenario baseline, mas a evidencia estatica e forte o suficiente para reporta-lo.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A analise estatica mostra que a conta `ledger` e usada sem verificar `ledger.owner`, permitindo que um atacante forneca uma conta arbitraria com dados forjados. A analise dinamica foi inconclusiva porque o baseline falhou com ProgramFailedToComplete, mas isso nao invalida a evidencia estatica; a ausencia de verificacao de owner e uma vulnerabilidade critica que permite corrupcao de estado arbitrario.
- **Recomendacao:** Adicionar verificacao explicita de que `ledger.owner == program_id` antes de ler ou modificar os dados da conta. Exemplo: `if ledger.owner != program_id { return Err(ProgramError::IncorrectProgramId); }`.

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A analise estatica aponta ausencia de verificacao de assinatura em `accounts[0]` ou qualquer outra conta. A analise dinamica confirmou o ataque: mint sem assinatura foi aceito e o supply/balance foram incrementados, comprovando que qualquer pessoa pode mintar tokens sem autorizacao.
- **Recomendacao:** Exigir que a conta da autoridade (ou a conta ledger, conforme o design) seja signer: `if !ledger.is_signer { return Err(ProgramError::MissingRequiredSignature); }` ou verificar uma conta de autoridade separada com `is_signer`.

### Integer Overflow / Underflow (MATH)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A analise estatica identifica uso de `wrapping_add` para supply e balance, permitindo overflow silencioso. A analise dinamica confirmou o ataque: com valores proximos de u64::MAX, um mint de 10 causou wrap-around, reduzindo supply e balance, quebrando a invariante do ledger.
- **Recomendacao:** Substituir `wrapping_add` por `checked_add` e retornar erro em caso de overflow: `let new_supply = supply.checked_add(amount).ok_or(ProgramError::InvalidArgument)?;` e analogamente para balance.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A analise estatica mostra desserializacao manual de offsets fixos sem discriminador de tipo. A analise dinamica confirmou o ataque: uma conta de outro tipo com bytes 40..56 interpretaveis como supply/balance foi aceita e teve seus dados corrompidos pelo mint, demonstrando type cosplay.
- **Recomendacao:** Adicionar um discriminador de tipo (ex.: primeiros 8 bytes) e verifica-lo antes de desserializar. Alternativamente, usar uma biblioteca de serializacao com validacao de tipo (ex.: Borsh) e garantir que apenas contas com o layout esperado sejam aceitas.
