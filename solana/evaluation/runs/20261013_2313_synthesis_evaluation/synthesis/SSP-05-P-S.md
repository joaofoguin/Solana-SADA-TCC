# Relatorio consolidado: SSP-05-P-S (`set_value`)

## Resumo

A instrucao `set_value` apresenta uma falha critica de autorizacao: a conta `user` e usada como autoridade sem verificacao de assinatura, permitindo que qualquer atacante grave dados em nome de outra pubkey. A ausencia de checagem de owner nao pode ser explorada diretamente por limitacoes do runtime, e nao ha aritmetica vulneravel. A postura de seguranca e inadequada para uma operacao que grava estado associado a um usuario.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A analise estatica aponta que a conta `user` e usada como autoridade (sua chave e gravada no estado) sem qualquer verificacao de assinatura (`is_signer` ou tipo `Signer`). A analise dinamica confirmou o ataque: o cenario executado com sucesso gravou a pubkey da vitima e o valor no estado sem que a vitima assinasse a transacao. O dano foi verificado no estado da conta, caracterizando escrita nao autorizada em nome de terceiros.
- **Recomendacao:** Exigir que a conta `user` seja signataria da transacao, verificando `user.is_signer` ou recebendo-a como `Signer` no tipo de contas. Adicionalmente, validar que o PDA `data_account` foi derivado das seeds `["data", user.key()]` para vincular a autoridade ao estado gravado.

## Achados descartados

- **OWNER** (execucao: inconclusive): A analise estatica levanta a ausencia de verificacao `data_account.owner == program_id`. A analise dinamica foi inconclusiva: o ataque tentado resultou em `UnknownError(ExternalAccountDataModified)`, erro do runtime da Solana que ocorre quando um programa tenta modificar dados de conta cujo dono e outro programa. Isso demonstra que o runtime impede a exploracao direta, e o proprio harness nao conseguiu demonstrar dano por via alternativa. A hipotese de ataque descrita (conta de outro programa com mesmo endereco PDA) e improvavel e nao foi comprovada.
- **MATH** (execucao: inconclusive): A analise estatica concluiu, com confianca baixa, que nao ha operacoes aritmeticas com risco de overflow/underflow: o valor e apenas convertido de bytes e gravado. A analise dinamica foi inconclusiva por erro de compilacao no harness, mas o cenario descrito (execucao com u64::MAX) nao indicaria dano aritmetico, pois nao ha aritmetica. Nao ha evidencia de vulnerabilidade nesta categoria.
