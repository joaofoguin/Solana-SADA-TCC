# Relatorio consolidado: SSP-04-P-S (`init`)

## Resumo

A instrução `init` apresenta falhas críticas de validação de assinatura e de propriedade de conta, permitindo que um atacante inicialize a configuração com uma autoridade arbitrária sem assinatura e potencialmente corrompa contas de terceiros. A proteção contra reinicialização existe via flag de estado, mas depende da ausência de verificação de owner, o que não foi confirmado dinamicamente. O programa carece de verificações básicas de segurança e não deve ser implantado sem correções.

## Vulnerabilidades reportadas

### Missing Signer Check (SIGNER)

- **Origem:** Estatica + Dinamica (execucao: confirmed)
- **Severidade:** critica
- **Confianca:** alta
- **Justificativa:** A análise estática identificou que a conta `authority` é gravada como autoridade da configuração sem verificar `is_signer`. A análise dinâmica confirmou o ataque: a inicialização foi bem-sucedida com uma conta `authority` sem assinatura, gravando sua chave pública. Isso permite que qualquer pessoa defina uma autoridade arbitrária sem possuir a chave privada, comprometendo o controle do programa.
- **Recomendacao:** Adicionar verificação explícita de assinatura: `require!(authority.is_signer, ProgramError::MissingRequiredSignature);` ou utilizar o tipo `Signer` do framework para garantir que a conta assinou a transação.

### Improper Owner Check (OWNER)

- **Origem:** Estatica (execucao: inconclusive)
- **Severidade:** alta
- **Confianca:** media
- **Justificativa:** A análise estática aponta que a conta `config` é modificada sem verificar se seu proprietário é o programa, permitindo sobrescrever dados de contas arbitrárias. A análise dinâmica foi inconclusiva devido a erro de compilação no harness, não fornecendo evidência contrária. A ausência de verificação de owner é uma falha grave e plausível, portanto deve ser reportada.
- **Recomendacao:** Verificar se `config.owner == program_id` antes de modificar seus dados, ou utilizar o tipo `Account<'info, T>` que realiza essa checagem automaticamente.

## Achados descartados

- **REINIT** (execucao: not_confirmed): A análise estática levantou a hipótese de que a ausência de verificação de owner permitiria reinicialização. No entanto, a análise dinâmica testou a reexecução da inicialização em uma conta já inicializada (byte 40 = 1) e o programa rejeitou corretamente com `Custom(4001)`. O ataque não foi confirmado, indicando que a flag de inicialização impede a reinicialização mesmo sem checagem de owner. Portanto, a vulnerabilidade de REINIT não se sustenta.
