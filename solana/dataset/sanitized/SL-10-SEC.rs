use anchor_lang::prelude::*;
use anchor_lang::solana_program::sysvar;
declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod target_program {
    use super::*;

    pub fn check_sysvar_address(ctx: Context<CheckSysvarAddress>) -> Result<()> {
        require_eq!(ctx.accounts.rent.key(), sysvar::rent::ID);

        Ok(())
    }
}

#[derive(Accounts)]
pub struct CheckSysvarAddress<'info> {

    rent: AccountInfo<'info>,
}
