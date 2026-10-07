use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod target_program {
    use super::*;

    pub fn update_user(ctx: Context<UpdateUser>) -> Result<()> {
        let user = User::try_from_slice(&ctx.accounts.user.data.borrow()).unwrap();
        if ctx.accounts.user.owner != ctx.program_id {
            return Err(ProgramError::IllegalOwner.into());
        }
        if user.authority != ctx.accounts.authority.key() {
            return Err(ProgramError::InvalidAccountData.into());
        }
        if user.discriminant != AccountDiscriminant::User {
            return Err(ProgramError::InvalidAccountData.into());
        }

        Ok(())
    }
}

#[derive(Accounts)]
pub struct UpdateUser<'info> {

    user: AccountInfo<'info>,
    authority: Signer<'info>,
}

#[derive(AnchorSerialize, AnchorDeserialize)]
pub struct User {
    discriminant: AccountDiscriminant,
    authority: Pubkey,
}

#[derive(AnchorSerialize, AnchorDeserialize)]
pub struct Metadata {
    discriminant: AccountDiscriminant,
    account: Pubkey,
}

#[derive(AnchorSerialize, AnchorDeserialize, PartialEq)]
pub enum AccountDiscriminant {
    User,
    Metadata,
}
