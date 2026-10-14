# Relatorio consolidado: SSP-05-P-V (`set_value`)

## Resumo

A instrução `set_value` apresenta falhas graves de validação de autoridade e de contas: não exige assinatura do usuário, aceita bumps não-canônicos de PDA e não valida o tipo/discriminador da conta de dados. As análises dinâmicas confirmaram explorações bem-sucedidas para SIGNER, PDA e COSPLAY, enquanto OWNER ficou inconclusiva por limitação do ambiente de simulação, mas permanece um risco real de projeto.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostra que a chave de `accounts[1]` é gravada como autoridade sem qualquer verificação de assinatura (`is_signer`/tipo `Signer`). A análise dinâmica confirmou o ataque: foi possível gravar a pubkey da vítima e o `value` do atacante no PDA da vítima sem que ela assinasse a transação, com sucesso e dano verificado no estado.
- **Recomendacao:** Exigir que a conta do usuário seja signatária, validando `user.is_signer` ou recebendo-a como `Signer` no contexto de contas, e rejeitar a instrução caso a assinatura esteja ausente.

### Improper PDA Validation / Canonicalization (PDA)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** O bump é fornecido pelo chamador e validado apenas com `create_program_address`, sem garantir que seja o bump canônico (`find_program_address`). A análise dinâmica confirmou que um bump não-canônico gera um PDA alternativo aceito pelo programa, permitindo gravar dados em um endereço diferente do PDA canônico esperado.
- **Recomendacao:** Derivar o PDA com `find_program_address` a partir das seeds lógicas e comparar com a conta recebida, ou validar explicitamente que o bump fornecido é o bump canônico retornado por `find_program_address`, rejeitando bumps alternativos.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática aponta ausência de verificação de que `data_account.owner == program_id` antes de ler/gravar seus dados. A análise dinâmica foi inconclusiva porque o runtime da Solana bloqueou a escrita em conta de outro owner (`ExternalAccountDataModified`), mas isso não invalida a falha: o programa aceitou a conta forjada e tentou operar sobre ela, e a ausência de checagem pode permitir decisões incorretas ou exploração em cenários onde a escrita não seja o único efeito.
- **Recomendacao:** Validar explicitamente que `data_account.owner == program_id` (e, se aplicável, que a conta é writable) antes de qualquer leitura ou escrita, rejeitando contas cujo owner não seja o programa.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática mostra escrita direta por offsets fixos sem validar discriminador de tipo no início do buffer. A análise dinâmica confirmou o ataque: uma conta de outro tipo no mesmo endereço PDA foi aceita e teve os bytes 8..40 sobrescritos com a chave do usuário, corrompendo o layout alheio.
- **Recomendacao:** Adicionar um discriminador de tipo (ex.: magic/version) no início dos dados da conta e validá-lo antes de interpretar ou escrever os campos, rejeitando contas cujo layout não corresponda ao tipo esperado.
