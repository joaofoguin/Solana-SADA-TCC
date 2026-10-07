use anchor_lang::prelude::*;
use std::ops::DerefMut;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod target_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let mut user = User::try_from_slice(&ctx.accounts.user.data.borrow()).unwrap();
        if !user.discriminator {
            return Err(ProgramError::InvalidAccountData.into());
        }

        user.authority = ctx.accounts.authority.key();
        user.discriminator = true;

        let mut storage = ctx.accounts.user.try_borrow_mut_data()?;
        user.serialize(storage.deref_mut()).unwrap();

        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {

    user: AccountInfo<'info>,
    authority: Signer<'info>,
}

#[derive(AnchorSerialize, AnchorDeserialize)]
pub struct User {
    discriminator: bool,
    authority: Pubkey,
}
