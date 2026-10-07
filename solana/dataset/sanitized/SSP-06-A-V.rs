use anchor_lang::prelude::*;

declare_id!("HS241bzcteDvCTi6UMEfecj3o8JieRvZVL3F1zhZGPxP");

#[program]
pub mod target_program {
    use super::*;

    pub fn update_fee(
        ctx: Context<UpdateFee>,
        new_fee: u64,
    ) -> Result<()> {
        let data = ctx.accounts.config.try_borrow_data()?;

        let admin_bytes: [u8; 32] = data[8..40]
            .try_into()
            .map_err(|_| ErrorCode::DeserializationFailed)?;
        let admin = Pubkey::from(admin_bytes);

        require_keys_eq!(admin, ctx.accounts.authority.key(), ErrorCode::Unauthorized);

        drop(data);

        let mut data = ctx.accounts.config.try_borrow_mut_data()?;
        data[40..48].copy_from_slice(&new_fee.to_le_bytes());

        Ok(())
    }

}

#[derive(Accounts)]
pub struct UpdateFee<'info> {

    #[account(mut)]
    pub config: UncheckedAccount<'info>,
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
