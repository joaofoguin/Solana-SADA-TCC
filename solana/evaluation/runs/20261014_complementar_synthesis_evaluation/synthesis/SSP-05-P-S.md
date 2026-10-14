# Relatorio consolidado: SSP-05-P-S (`set_value`)

## Resumo

A instrucao `set_value` apresenta uma falha critica de autenticacao: a conta `user` e usada como autoridade sem verificacao de assinatura, permitindo escrita nao autorizada em nome de terceiros. A ausencia de verificacao de owner da conta de dados nao pode ser confirmada dinamicamente, mas permanece como risco de defesa em profundidade. Nao ha risco aritmetico relevante.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A analise estatica aponta que a conta `user` e gravada como autoridade sem qualquer verificacao de assinatura (`is_signer` ou tipo `Signer`). A analise dinamica confirmou o ataque: o programa aceitou a transacao sem a assinatura da vitima e gravou sua pubkey e o valor no estado, caracterizando escrita nao autorizada. A evidencia e conclusiva.
- **Recomendacao:** Adicionar verificacao explicita de assinatura para a conta `user`, por exemplo `if !user.is_signer() { return Err(ProgramError::MissingRequiredSignature); }`, ou exigir o tipo `Signer` no parsing das contas.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** media
- **Confianca:** media
- **Justificativa:** A analise estatica indica ausencia de verificacao de que `data_account.owner == program_id` antes de modificar seus dados. A analise dinamica foi inconclusiva: o ataque parou com `UnknownError(ExternalAccountDataModified)`, erro do runtime da Solana, nao do programa, pois nenhum programa pode gravar em conta de dono alheio. Ainda assim, a ausencia de checagem de owner e uma falha de defesa em profundidade que pode permitir que o programa tome decisoes com base em dados forjados de outro programa, mesmo que a gravacao direta seja bloqueada pelo runtime.
- **Recomendacao:** Adicionar verificacao explicita de proprietario da conta de dados: `if data_account.owner() != program_id { return Err(ProgramError::IncorrectProgramId); }`, antes de ler ou modificar seus dados.

## Achados descartados

- **MATH** (execucao: inconclusive): A analise estatica ja concluiu que nao ha operacoes aritmeticas com risco de overflow/underflow nesta instrucao; o valor e apenas convertido de bytes e gravado. A analise dinamica foi inconclusiva por erro de compilacao no harness, mas nao ha hipotese de ataque valida a testar. Portanto, o achado nao se sustenta.
