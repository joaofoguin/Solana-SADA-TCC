use anchor_lang::prelude::*;
use anchor_lang::solana_program;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod target_program {
    use super::*;

    pub fn cpi(ctx: Context<Cpi>, amount: u64) -> Result<()> {
        let mut data = vec![3u8];
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

    source: AccountInfo<'info>,

    destination: AccountInfo<'info>,

    authority: AccountInfo<'info>,

    token_program: AccountInfo<'info>,
}
