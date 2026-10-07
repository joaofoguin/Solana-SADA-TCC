// VARIANTE CONSTRUIDA PELO AUTOR (SADA-Solana) a partir de
// sealevel-attacks/programs/5-arbitrary-cpi/insecure.
// Unica diferenca: a instrucao de transferencia e montada manualmente,
// em vez de usar spl_token::instruction::transfer, cujo construtor
// valida o program id (check_program_account) e neutraliza o ataque.
use anchor_lang::prelude::*;
use anchor_lang::solana_program;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod arbitrary_cpi_insecure {
    use super::*;

    pub fn cpi(ctx: Context<Cpi>, amount: u64) -> Result<()> {
        let mut data = vec![3u8]; // TokenInstruction::Transfer
        data.extend_from_slice(&amount.to_le_bytes());
        let ix = solana_program::instruction::Instruction {
            program_id: *ctx.accounts.token_program.key,
            accounts: vec![
                solana_program::instruction::AccountMeta::new(*ctx.accounts.source.key, false),
                solana_program::instruction::AccountMeta::new(*ctx.accounts.destination.key, false),
                solana_program::instruction::AccountMeta::new_readonly(*ctx.accounts.authority.key, true),
            ],
            data,
        };
        solana_program::program::invoke(
            &ix,
            &[
                ctx.accounts.source.clone(),
                ctx.accounts.destination.clone(),
                ctx.accounts.authority.clone(),
            ],
        )
        .map_err(Into::into)
    }
}

#[derive(Accounts)]
pub struct Cpi<'info> {
    /// CHECK: PORT - doc exigido pelo Anchor >= 0.24; sem efeito na logica
    source: AccountInfo<'info>,
    /// CHECK: PORT
    destination: AccountInfo<'info>,
    /// CHECK: PORT
    authority: AccountInfo<'info>,
    /// CHECK: PORT
    token_program: AccountInfo<'info>,
}
