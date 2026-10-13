# Relatorio consolidado: SSP-01-P-V (`withdraw`)

## Resumo

A instrução `withdraw` apresenta falhas críticas de autenticação e validação de contas: não verifica assinatura da autoridade (SIGNER) e não valida o dono nem o discriminador de tipo da conta vault (OWNER/COSPLAY). A exploração bem-sucedida nos testes dinâmicos confirma que um atacante pode drenar os lamports do vault sem autorização, tornando a instrução insegura para uso em produção.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática aponta ausência de verificação `authority.is_signer`, permitindo que qualquer pessoa use a chave pública da autoridade sem assinar. O teste dinâmico confirmou o ataque: o saque foi aceito sem assinatura e os lamports foram transferidos do vault para o recipient do atacante.
- **Recomendacao:** Adicionar verificação explícita `if !authority.is_signer { return Err(ProgramError::MissingRequiredSignature); }` antes de comparar a chave pública com a autoridade armazenada.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática indica que os dados do vault são lidos sem verificar `vault.owner == program_id`, permitindo contas forjadas com layout imitado. O teste dinâmico foi inconclusivo devido a erro de compilação no harness, mas a falha é evidente no código e representa risco real de aceitação de dados não autenticados.
- **Recomendacao:** Verificar se `vault.owner == program_id` antes de ler os dados da conta, retornando erro caso contrário.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática aponta ausência de discriminador de tipo no início do buffer, permitindo que contas de outros tipos com layout compatível sejam interpretadas como vault. O teste dinâmico confirmou o ataque: uma conta de outro tipo foi aceita, seus lamports foram debitados e o recipient creditado, demonstrando o type cosplay.
- **Recomendacao:** Incluir um discriminador de tipo (ex.: primeiros 8 bytes) no layout da conta vault e validá-lo antes de interpretar os dados, rejeitando contas com discriminador incorreto.
