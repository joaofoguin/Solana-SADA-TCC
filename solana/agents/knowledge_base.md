## SIGNER - Missing Signer Check
- O que e: Ausencia de verificacao de que a conta responsavel por autorizar uma operacao privilegiada assinou a transacao (`is_signer`).
- Sinais no codigo: Leitura de uma conta de autoridade usando `AccountInfo` ou `UncheckedAccount` sem validar a flag `account_info.is_signer`, ou comparacao de chaves publicas (`pubkey == config.admin`) sem exigir assinatura.
- Mitigacoes aceitas: Uso do tipo `Signer<'info>` na struct de contas do Anchor, ou validacao explicita `require!(account_info.is_signer, ...)` / `assert!(account_info.is_signer)` em Rust nativo.
- Fonte: Anchor Documentation (Account Types: Signer) & Solana Security Patterns (01-missing-signer-check) & Trail of Bits, crytic/building-secure-contracts, not-so-smart-contracts/solana/signer_check.

## OWNER - Improper Owner Check
- O que e: Leitura ou modificacao dos dados de uma conta sem verificar se ela pertence ao programa esperado (`account.owner == expected_program_id`), permitindo o fornecimento de contas forjadas com dados maliciosos.
- Sinais no codigo: Acesso aos dados de uma conta (`AccountInfo`) sem checar o campo `owner`, assumindo que a estrutura recebida e autentica.
- Mitigacoes aceitas: Uso do tipo `Account<'info, T>` no Anchor (que valida automaticamente o proprietario da conta), constraint `#[account(owner = ...)]`, ou verificacao manual `if account.owner != expected_owner` em Rust nativo.
- Fonte: Anchor Documentation (Account Types: Account; Account Constraints: owner) & Solana Security Patterns (02-missing-owner-check) & Trail of Bits, crytic/building-secure-contracts, not-so-smart-contracts/solana/ownership_check.

## CPI - Arbitrary CPI
- O que e: Invocacao entre programas (Cross-Program Invocation) na qual a conta do programa destino (`target_program`) e fornecida pelo usuario sem verificacao de sua chave publica, permitindo que um programa malicioso receba a chamada.
- Sinais no codigo: Chamadas a `solana_program::program::invoke` ou `invoke_signed` passando uma `AccountInfo` generica sem validar se `target_program.key == expected_program_id`.
- Mitigacoes aceitas: Uso do tipo `Program<'info, TargetProgram>` no Anchor (que valida a chave publica do programa esperado) ou verificacao explicita da chave publica `require_keys_eq!(target_program.key(), expected_id)` antes da invocacao.
- Fonte: Anchor Documentation (Account Types: Program) & Trail of Bits, crytic/building-secure-contracts, not-so-smart-contracts/solana/arbitrary_cpi.

## PDA - Improper PDA Validation / Canonicalization
- O que e: Falha na verificacao ou derivacao de Program Derived Addresses (PDAs), aceitando um bump fornecido pelo usuario sem validar se e o bump canonico, ou usando metodos que nao garantem a derivacao correta do PDA.
- Sinais no codigo: Uso de `Pubkey::create_program_address` com um bump fornecido externamente sem verificar se ele coincide com o bump canonico, ou ausencia de derivacao e checagem de PDA.
- Mitigacoes aceitas: Constraint `#[account(seeds = [...], bump)]` do Anchor (que deriva e valida automaticamente o bump canonico), ou derivacao/validacao explicita no codigo usando `Pubkey::find_program_address`.
- Fonte: Anchor Documentation (Account Constraints: seeds, bump) & Solana Security Patterns (05-pda-bump-canonicalization) & Trail of Bits, crytic/building-secure-contracts, not-so-smart-contracts/solana/improper_pda_validation.

## SYSVAR - Sysvar Account Check
- O que e: Leitura de dados de uma conta de sistema (Sysvar, como Clock ou Rent) sem validar se a conta recebida e a conta oficial do Sysvar correspondente.
- Sinais no codigo: Recebimento de uma conta de Sysvar como `AccountInfo` ou `UncheckedAccount` e leitura de seus dados sem comparar sua chave publica com o ID oficial do Sysvar.
- Mitigacoes aceitas: Uso do tipo fortemente tipado `Sysvar<'info, T>` do Anchor (que valida o ID do Sysvar automaticamente), ou verificacao explicita da chave publica da conta contra o ID oficial (`sysvar_account.key() == solana_program::sysvar::...::ID`).
- Fonte: Anchor Documentation (Account Types: Sysvar) & Trail of Bits, crytic/building-secure-contracts, not-so-smart-contracts/solana/sysvar_account_check.

## MATH - Integer Overflow / Underflow
- O que e: Operacoes aritmeticas executadas sem checagem de limites que podem resultar em estouro ou reinicio de valores inteiros, permitindo manipulacao indevida de saldos ou valores de contexto.
- Sinais no codigo: Operacoes aritmeticas diretas (`+`, `-`, `*`) em variaveis numericas sem checagem previa de limites/saldos ou sem o uso de funcoes de aritmetica segura.
- Mitigacoes aceitas: Uso explicito dos metodos de aritmetica segura da biblioteca padrao do Rust (`checked_add`, `checked_sub`, `checked_mul`, `saturating_*`), ou presenca de verificacoes de pre-condicao (como `require!(balance >= amount)` antes da subtracao).
- Fonte: The Rust Reference (Integer overflow) & Solana Security Patterns (03-integer-overflow).

## COSPLAY - Type Cosplay
- O que e: Ataque em que uma conta contendo dados estruturados de um tipo A e passada para uma instrucao que espera um tipo B, aproveitando-se do layout de memoria sem validacao de tipo para burlar a logica do programa.
- Sinais no codigo: Desserializacao manual de dados de conta a partir de `AccountInfo` ou `UncheckedAccount` sem verificar um identificador ou discriminador de tipo unico (mesmo no Anchor).
- Mitigacoes aceitas: Uso do wrapper fortemente tipado `Account<'info, T>` do Anchor (que injeta e valida automaticamente o discriminador de 8 bytes no inicio da conta), ou inclusao e verificacao manual de um discriminador/tag de tipo exclusivo no inicio do buffer de dados.
- Fonte: Anchor Documentation (Account Types: Account; account discriminator) & Solana Security Patterns (06-type-cosplay).

## REINIT - Reinitialization Attacks
- O que e: Permissao para que uma instrucao de inicializacao seja executada novamente sobre uma conta ja criada e inicializada, permitindo que um atacante sobrescreva dados de estado, como a autoridade ou saldo da conta.
- Sinais no codigo: Instrucoes que gravam dados em uma conta sem verificar se uma flag de controle (ex: `is_initialized`) ou discriminador de estado ja foi definido anteriormente.
- Mitigacoes aceitas: Uso da constraint `#[account(init, ...)]` do Anchor (que garante que a conta esta sendo criada e define seu discriminador), ou checagem manual explicita garantindo que a conta nao foi inicializada previamente.
- Fonte: Anchor Documentation (Account Constraints: init) & Solana Security Patterns (04-reinitialization-attack).
