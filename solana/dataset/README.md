# Dataset e Ground Truth

Esta pasta contém a organização dos casos de segurança utilizados no TCC SADA-Solana.

## Objetivo

O catálogo registra casos vulneráveis e, quando disponível na fonte, suas variantes seguras e testes de exploração. O catálogo é a camada de rastreabilidade entre:

- fonte original;
- commit utilizado;
- arquivo/caso de referência;
- categoria de vulnerabilidade;
- evidência de ground truth;
- possibilidade de execução com Mollusk;
- uso posterior em desenvolvimento ou avaliação.

## Categorias adotadas

1. Missing Signer Check
2. Improper Owner Check
3. Arbitrary CPI
4. Improper PDA Validation / Canonicalization
5. Sysvar Account Check
6. Integer Overflow / Underflow
7. Type Cosplay
8. Reinitialization Attacks

## Organização

`catalog.json` é o inventário mestre. Os campos de desenvolvimento e avaliação permanecem explícitos para evitar que um caso seja usado simultaneamente como exemplo de desenvolvimento e como teste independente sem registro.

O catálogo não substitui a validação experimental. Antes de um caso entrar na avaliação final, devem ser confirmados o código, a versão/commit da fonte, o comportamento vulnerável, a variante segura quando disponível e a execução correspondente.

## Fontes iniciais

- justFiveDev/solana-security-pattern
- El-Merovingio/solana-hacks
- crytic/building-secure-contracts (Solana / Not So Smart Contracts)

As fontes externas são referências do TCC; os agentes e o pipeline de avaliação serão implementados separadamente dentro de `solana/`.
