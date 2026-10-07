use anchor_lang::prelude::*;
use anchor_lang::solana_program;
use anchor_spl::token::spl_token; // PORT: spl_token via anchor_spl

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod arbitrary_cpi_secure {
    use super::*;

    pub fn cpi_secure(ctx: Context<Cpi>, amount: u64) -> Result<()> {
        if &spl_token::ID != ctx.accounts.token_program.key {
            return Err(ProgramError::IncorrectProgramId.into());
        }
        solana_program::program::invoke(
            &spl_token::instruction::transfer(
                ctx.accounts.token_program.key,
                ctx.accounts.source.key,
                ctx.accounts.destination.key,
                ctx.accounts.authority.key,
                &[],
                amount,
            )?,
            &[
                ctx.accounts.source.clone(),
                ctx.accounts.destination.clone(),
                ctx.accounts.authority.clone(),
            ],
        )
        .map_err(Into::into) // PORT: ProgramResult -> anchor Result
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
