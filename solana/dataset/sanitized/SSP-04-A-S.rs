use anchor_lang::prelude::*;

declare_id!("2P1GgtagVaYR8B6FhrPHdP4Mmy3pUFAZtSyeWFK293vg");

#[program]
pub mod target_program {
    use super::*;

    pub fn init(ctx: Context<Init>) -> Result<()> {
        let config = &mut ctx.accounts.config;

        require!(!config.is_initialized, ErrorCode::AlreadyInitialized);

        config.authority = ctx.accounts.authority.key();
        config.is_initialized = true;
        config.vault_balance = 0;

        Ok(())
    }

}

#[derive(Accounts)]
pub struct Init<'info> {
    #[account(mut)]
    pub config: Account<'info, Config>,
    pub authority: Signer<'info>,
}

#[account]
#[derive(InitSpace)]
pub struct Config {
    pub authority: Pubkey,
    pub is_initialized: bool,
    pub vault_balance: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Account already initialized")]
    AlreadyInitialized,
}
