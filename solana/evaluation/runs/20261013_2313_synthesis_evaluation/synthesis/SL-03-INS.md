# Relatorio consolidado: SL-03-INS (`update_user`)

## Resumo

A instrução `update_user` apresenta uma postura de segurança razoável, com a checagem de proprietário da conta `user` efetiva, conforme confirmado pela análise dinâmica. No entanto, a ausência de um discriminador de tipo na desserialização manual da conta `user` representa um risco de type cosplay que não pôde ser confirmado dinamicamente, mas merece atenção. Recomenda-se adotar as práticas do Anchor para validação de contas.

## Vulnerabilidades reportadas

### Type Cosplay (COSPLAY)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** media
- **Confianca:** media
- **Justificativa:** A análise estática identificou que a conta `user` é desserializada manualmente sem verificação de discriminador de tipo, permitindo que contas com layout semelhante (como `Metadata`) sejam interpretadas como `User`. A análise dinâmica foi inconclusiva porque o ataque não foi executado corretamente (não alterou o discriminador), mas a evidência estática é suficiente para indicar um risco real de type cosplay, especialmente se a checagem de proprietário for contornada ou se outras contas do programa tiverem o mesmo layout.
- **Recomendacao:** Substituir a desserialização manual por tipos de conta do Anchor (ex.: `Account<'info, User>`) que incluem um discriminador de 8 bytes e verificam automaticamente o proprietário e o tipo. Se a desserialização manual for necessária, adicionar uma verificação explícita de discriminador antes de desserializar.

## Achados descartados

- **OWNER** (execucao: not_confirmed): A análise estática apontou uma possível vulnerabilidade devido à desserialização antes da verificação de proprietário, mas a análise dinâmica demonstrou que o ataque foi rejeitado com erro `IllegalOwner`, confirmando que a checagem de proprietário subsequente bloqueia efetivamente a exploração. A ordem de operações é subótima, mas não resulta em dano.
