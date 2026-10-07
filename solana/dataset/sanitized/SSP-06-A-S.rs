use anchor_lang::prelude::*;

declare_id!("HS241bzcteDvCTi6UMEfecj3o8JieRvZVL3F1zhZGPxP");

#[program]
pub mod target_program {
    use super::*;

    pub fn update_fee(
        ctx: Context<UpdateFee>,
        new_fee: u64,
    ) -> Result<()> {
        let config = &mut ctx.accounts.config;

        require_keys_eq!(
            config.admin,
            ctx.accounts.authority.key(),
            ErrorCode::Unauthorized
        );

        config.fee_basis_points = new_fee;

        Ok(())
    }
}

#[derive(Accounts)]
pub struct UpdateFee<'info> {
    #[account(mut)]
    pub config: Account<'info, AdminConfig>,
    pub authority: Signer<'info>,
}

#[account]
#[derive(InitSpace)]
pub struct AdminConfig {
    pub admin: Pubkey,
    pub fee_basis_points: u64,
}

#[account]
#[derive(InitSpace)]
pub struct UserData {
    pub authority: Pubkey,
    pub balance: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Unauthorized: signer is not admin")]
    Unauthorized,
    #[msg("Failed to deserialize account data")]
    DeserializationFailed,
}
