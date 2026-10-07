use anchor_lang::prelude::*;

declare_id!("x1rqubJg3BK9Q5FbHqaxSW4cU5toBeAQkWyw8cELaRm");

#[program]
pub mod target_program {
    use super::*;

    pub fn set_value(
        ctx: Context<SetValue>,
        bump: u8,
        value: u64,
    ) -> Result<()> {

        let seeds = &[b"data" as &[u8], ctx.accounts.user.key.as_ref(), &[bump]];

        let pda = Pubkey::create_program_address(seeds, ctx.program_id)
            .map_err(|_| ErrorCode::InvalidBump)?;

        require_keys_eq!(pda, ctx.accounts.data_account.key(), ErrorCode::PdaMismatch);

        let data_account = &mut ctx.accounts.data_account;
        data_account.user = ctx.accounts.user.key();
        data_account.value = value;
        data_account.bump = bump;

        Ok(())
    }

}

#[derive(Accounts)]
pub struct SetValue<'info> {
    #[account(mut)]
    pub data_account: Account<'info, DataAccount>,
    pub user: Signer<'info>,
}

#[account]
#[derive(InitSpace)]
pub struct DataAccount {
    pub user: Pubkey,
    pub value: u64,
    pub bump: u8,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid bump seed")]
    InvalidBump,
    #[msg("PDA address mismatch")]
    PdaMismatch,
}
