# Port dos programas do Evaluation Set

Base: anchor-lang 0.31.1 (mesma versao que compila o SSP nesta VM).

Regras do port (somente sintaxe/API; logica preservada):
1. `ProgramResult` -> `Result<()>`; `Err(ProgramError::X)` -> `Err(ProgramError::X.into())`.
2. `invoke(...)` retorna `ProgramResult`: `.map_err(Into::into)`.
3. `/// CHECK:` em campos `AccountInfo` (exigido pelo Anchor >= 0.24).
4. `BorshSerialize/BorshDeserialize` -> `AnchorSerialize/AnchorDeserialize` (mesmo borsh do Anchor).
5. `spl_token` importado via `anchor_spl::token::spl_token` (versao compativel com anchor 0.31.1).
6. sl_07: `#[account(mut)]` em `data`, pois o Anchor atual so persiste `Account<T>` gravavel;
   `create_program_address` (PubkeyError) mapeado para `ProgramError::InvalidSeeds`.
7. hk_reinit: solana-program 1.15 -> 2.1, borsh 0.9 -> 1.5; entrypoint sob `no-entrypoint`.
8. Pinocchio: copia sem alteracao (prepare.sh).

Toda linha alterada esta marcada com `// PORT` e o diff completo fica em docs/ports/.
