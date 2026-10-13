# Relatorio consolidado: SSP-02-P-V (`process`)

## Resumo

A instrução `process` apresenta falhas graves de validação de contas: não verifica assinatura de autoridade, não valida o proprietário da conta de tesouraria e não usa discriminador de tipo. A análise dinâmica confirmou a exploração de type cosplay, enquanto os achados de signer e owner ficaram inconclusivos por falhas no harness, mas a evidência estática é forte. O programa é inseguro e requer correções imediatas.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática mostra que a conta `authority` (accounts[1]) é lida mas nunca verificada como signer nem comparada com a autoridade armazenada, permitindo que qualquer conta sem assinatura execute operações privilegiadas. A análise dinâmica foi inconclusiva devido a erro de compilação no harness, mas a evidência estática é clara e suficiente para reportar.
- **Recomendacao:** Adicionar verificação explícita: `require!(authority.is_signer, ProgramError::MissingRequiredSignature);` e comparar `authority.key()` com `stored_authority` usando `require!(authority.key() == stored_authority, ProgramError::InvalidAccountData);`.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática indica que os dados da conta `treasury` são lidos sem verificar se `treasury.owner == program_id`, permitindo que uma conta forjada com dados maliciosos seja usada. A análise dinâmica foi inconclusiva porque o baseline falhou, mas a hipótese de ataque é plausível e a ausência de verificação é uma vulnerabilidade conhecida.
- **Recomendacao:** Adicionar verificação de proprietário: `require!(treasury.owner == program_id, ProgramError::InvalidAccountOwner);` antes de ler os dados.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática aponta que os dados são desserializados por offsets fixos sem validar um discriminador de tipo, permitindo que uma conta de outro tipo seja interpretada como tesouraria. A análise dinâmica confirmou o ataque: uma conta com discriminador diferente foi aceita e os dados foram lidos como se fossem da tesouraria.
- **Recomendacao:** Adicionar um discriminador único no início dos dados da conta (ex.: primeiros 8 bytes) e verificar antes de qualquer leitura: `require!(data[0..8] == TREASURY_DISCRIMINATOR, ProgramError::InvalidAccountData);`.
