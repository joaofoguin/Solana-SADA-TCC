use anchor_lang::prelude::*;

declare_id!("8anCcUkKVms75R4HYTnkbM6YGzAra9WTmXhNEY5RSaNw");

#[program]
pub mod target_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, amount: u64) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        treasury.authority = ctx.accounts.authority.key();
        treasury.balance = amount;
        treasury.is_active = true;

        Ok(())
    }

    pub fn process(ctx: Context<Process>) -> Result<()> {

        let data = ctx.accounts.treasury.try_borrow_data()?;

        let authority = Pubkey::try_from(&data[8..40]).map_err(|_| ErrorCode::InvalidData)?;
        let balance = u64::from_le_bytes(
            data[40..48].try_into().map_err(|_| ErrorCode::InvalidData)?,
        );
        let is_active = data[48] != 0;

        require!(is_active, ErrorCode::TreasuryInactive);

        Ok(())
    }

}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Treasury::INIT_SPACE,
    )]
    pub treasury: Account<'info, Treasury>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Process<'info> {

    pub treasury: AccountInfo<'info>,
    pub authority: Signer<'info>,
}

#[account]
#[derive(InitSpace)]
pub struct Treasury {
    pub authority: Pubkey,
    pub balance: u64,
    pub is_active: bool,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid account data")]
    InvalidData,
    #[msg("Treasury is not active")]
    TreasuryInactive,
}
