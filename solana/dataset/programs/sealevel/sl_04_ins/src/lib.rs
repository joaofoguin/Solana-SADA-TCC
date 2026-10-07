use anchor_lang::prelude::*;
use std::ops::DerefMut;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod initialization_insecure {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let mut user = User::try_from_slice(&ctx.accounts.user.data.borrow()).unwrap();

        user.authority = ctx.accounts.authority.key();

        let mut storage = ctx.accounts.user.try_borrow_mut_data()?;
        user.serialize(storage.deref_mut()).unwrap();
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    /// CHECK: PORT - doc exigido pelo Anchor >= 0.24; sem efeito na logica
    user: AccountInfo<'info>,
    authority: Signer<'info>,
}

#[derive(AnchorSerialize, AnchorDeserialize)] // PORT: Borsh* -> Anchor* (mesmo borsh)
pub struct User {
    authority: Pubkey,
}
