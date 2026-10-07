use anchor_lang::prelude::*;

declare_id!("3w5jyYEgbsnHjFcTUH9xdyH3KfN2YRppPCFUkskyYSxA");

#[program]
pub mod target_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, initial_supply: u64) -> Result<()> {
        let ledger = &mut ctx.accounts.ledger;
        ledger.authority = ctx.accounts.authority.key();
        ledger.total_supply = initial_supply;
        ledger.user_balance = 0;

        Ok(())
    }

    pub fn mint(ctx: Context<Operate>, amount: u64) -> Result<()> {
        let ledger = &mut ctx.accounts.ledger;

        ledger.total_supply = ledger
            .total_supply
            .checked_add(amount)
            .ok_or(ErrorCode::ArithmeticOverflow)?;

        ledger.user_balance = ledger
            .user_balance
            .checked_add(amount)
            .ok_or(ErrorCode::ArithmeticOverflow)?;

        Ok(())
    }

}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Ledger::INIT_SPACE,
    )]
    pub ledger: Account<'info, Ledger>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Operate<'info> {
    #[account(mut, has_one = authority)]
    pub ledger: Account<'info, Ledger>,
    pub authority: Signer<'info>,
}

#[account]
#[derive(InitSpace)]
pub struct Ledger {
    pub authority: Pubkey,
    pub total_supply: u64,
    pub user_balance: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Arithmetic overflow")]
    ArithmeticOverflow,
    #[msg("Arithmetic underflow")]
    ArithmeticUnderflow,
}
