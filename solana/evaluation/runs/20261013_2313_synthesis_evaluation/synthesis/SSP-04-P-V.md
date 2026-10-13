# Relatorio consolidado: SSP-04-P-V (`init`)

## Resumo

A instrução `init` apresenta falhas críticas de validação de contas: não verifica assinatura da autoridade (SIGNER) e não valida o proprietário da conta de configuração (OWNER), permitindo que um atacante grave uma autoridade arbitrária sem assinatura e potencialmente sobrescreva dados de contas de outros programas. As hipóteses de reinitialization (REINIT) e type cosplay (COSPLAY) não puderam ser confirmadas dinamicamente por falhas de compilação no harness, mas permanecem plausíveis estaticamente e devem ser tratadas como riscos a corrigir.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática aponta ausência de verificação `is_signer` para a conta `authority` (accounts[1]), cuja chave é gravada como autoridade da config. A análise dinâmica confirmou o ataque: uma chamada `init` com a chave de uma vítima sem assinatura foi aceita e a chave foi gravada como autoridade, permitindo que um atacante assuma o controle da configuração.
- **Recomendacao:** Adicionar verificação explícita `require!(authority.is_signer, ErrorCode::MissingSignature)` ou usar o tipo `Signer` do framework para garantir que a conta authority assine a transação antes de gravar sua chave como autoridade.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática mostra que os dados da conta `config` são escritos diretamente sem verificar `config.owner == program_id`. A análise dinâmica foi inconclusiva: o ataque com conta de dono diferente falhou com `ExternalAccountDataModified`, erro do runtime que indica que o programa tentou escrever em conta de outro dono, mas não confirma se o programa aceitou a entrada. Ainda assim, a ausência de verificação de owner é uma vulnerabilidade real que pode permitir sobrescrita de dados de contas de outros programas em cenários onde o runtime permita ou onde o dano ocorra indiretamente.
- **Recomendacao:** Validar que `config.owner == program_id` antes de qualquer escrita, preferencialmente usando o tipo `Account<'info, T>` do framework ou uma verificação explícita `require!(config.owner == program_id, ErrorCode::InvalidOwner)`.

### Reinitialization Attacks (REINIT)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática indica que a instrução `init` grava discriminador, autoridade e flag sem verificar se a conta já foi inicializada, permitindo sobrescrever uma configuração existente. A análise dinâmica foi inconclusiva devido a erro de compilação no harness, não fornecendo evidência contrária. A hipótese é plausível e o impacto potencial é alto (tomada de controle da config).
- **Recomendacao:** Adicionar verificação de inicialização: ler o discriminador ou flag `is_initialized` e rejeitar a instrução se a conta já estiver inicializada, ou usar a constraint `init` do Anchor (ou equivalente) que impede reinicialização.

### Type Cosplay (COSPLAY)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** media
- **Confianca:** baixa
- **Justificativa:** A análise estática aponta que os dados da conta são acessados via `AccountInfo` sem validar um discriminador de tipo pré-existente, permitindo que uma conta de outro tipo com layout compatível seja tratada como config. A análise dinâmica foi inconclusiva por erro de compilação no harness, sem evidência contrária. Embora a confiança seja baixa, a falha de validação de tipo é um vetor conhecido e deve ser corrigida.
- **Recomendacao:** Validar o discriminador de tipo da conta antes de tratá-la como config, por exemplo verificando os primeiros 8 bytes contra um valor esperado ou usando o tipo `Account<'info, T>` que faz essa validação automaticamente.
