# Relatorio consolidado: SSP-03-P-S2 (`burn`)

## Resumo

A instrução `burn` apresenta falhas críticas de autorização e validação de contas: não exige assinatura (SIGNER) e não valida o tipo/discriminador da conta (COSPLAY), permitindo que qualquer usuário debite saldo e supply de contas arbitrárias. A verificação de owner (OWNER) é uma preocupação válida, mas o runtime da Solana impede a gravação em contas de terceiros, tornando o ataque não observável no ambiente testado.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que nenhuma conta é exigida como signer, permitindo que qualquer usuário chame `burn` e reduza saldo/supply de contas arbitrárias. A análise dinâmica confirmou o ataque: a instrução foi executada com sucesso sem assinatura, e o dano (redução de supply e balance) foi verificado. É uma vulnerabilidade crítica de autorização.
- **Recomendacao:** Adicionar verificação `is_signer` na conta `ledger` (ou na conta do proprietário) antes de qualquer débito, garantindo que apenas o dono da conta possa autorizar a queima.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática mostrou desserialização manual por offsets fixos sem verificar discriminador de tipo. A análise dinâmica confirmou que uma conta com discriminador diferente foi aceita e teve seus bytes 40..56 debitados, demonstrando que o programa opera sobre dados de tipo incorreto. Isso permite manipulação de estado de contas que não são do tipo esperado.
- **Recomendacao:** Adicionar um discriminador de tipo (tag) no início dos dados da conta e verificá-lo antes de desserializar, rejeitando contas que não correspondam ao tipo `Ledger` esperado.

## Achados descartados

- **OWNER** (execucao: inconclusive): A análise estática aponta corretamente a ausência de verificação de owner, mas a análise dinâmica mostrou que o ataque resulta em `UnknownError(ExternalAccountDataModified)`, um erro do runtime da Solana que impede a gravação em contas de outros programas. O programa aceita a conta forjada, mas não consegue modificar seus dados, então não há dano observável. A hipótese não se materializa como vulnerabilidade explorável no ambiente testado.
