# Relatorio consolidado: SSP-01-P-S (`withdraw`)

## Resumo

A instrução `withdraw` apresenta falhas críticas de validação de contas: não verifica o owner da conta vault e não valida um discriminador de tipo, permitindo que contas forjadas ou de tipos diferentes sejam tratadas como vault. A análise dinâmica confirmou a exploração do type cosplay, enquanto a falha de owner ficou inconclusiva por limitação do harness, mas a evidência estática é forte. Recomenda-se corrigir ambas as validações antes de qualquer implantação.

## Vulnerabilidades reportadas

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática aponta com alta confiança que a conta `vault` é lida sem verificar `vault.owner`, permitindo que um atacante forneça uma conta forjada com dados arbitrários. A análise dinâmica foi inconclusiva devido a um erro de configuração do harness (conta do System Program ausente), não por rejeição do programa. A ausência de verificação de owner é uma vulnerabilidade clássica e crítica, e a evidência estática é suficiente para reportar.
- **Recomendacao:** Adicionar verificação explícita de que `vault.owner == program_id` (ou o owner esperado) antes de ler ou modificar os dados da conta. Utilizar `vault.try_borrow_data()` somente após confirmar o owner, ou usar tipos de conta validados pelo framework (ex.: `Account<'info, Vault>` no Anchor).

### Type Cosplay (COSPLAY)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** alta
- **Confianca:** alta
- **Justificativa:** A análise estática identificou desserialização manual por offsets fixos sem validação de discriminador de tipo. A análise dinâmica confirmou o ataque: uma conta de outro tipo com layout compatível foi aceita como vault, teve seu saldo decrementado e lamports transferidos para o recipient. O dano foi verificado, confirmando a vulnerabilidade de type cosplay.
- **Recomendacao:** Incluir um discriminador de tipo (tag) no início dos dados da conta e validá-lo antes de qualquer leitura. Preferencialmente, utilizar um framework que faça essa validação automaticamente (ex.: `Account<'info, Vault>` no Anchor) ou implementar verificação manual do discriminador (ex.: primeiros 8 bytes) e rejeitar contas com tag incorreta.
