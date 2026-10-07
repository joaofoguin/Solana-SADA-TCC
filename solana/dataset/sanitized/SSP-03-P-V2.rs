#![no_std]

pinocchio::nostd_panic_handler!();

use pinocchio::{
    account_info::AccountInfo,
    entrypoint,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
    ProgramResult,
};

entrypoint!(process_instruction);

const IX_BURN: u8 = 1;

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;

    let amount = u64::from_le_bytes(
        instruction_data[1..9]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );

    match *instruction {
        IX_BURN => burn(accounts, amount),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

fn burn(accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let ledger = &accounts[0];

    let mut data = ledger.try_borrow_mut_data()?;

    let supply = u64::from_le_bytes(data[40..48].try_into().unwrap());
    let balance = u64::from_le_bytes(data[48..56].try_into().unwrap());

    let new_supply = supply.wrapping_sub(amount);
    let new_balance = balance.wrapping_sub(amount);

    data[40..48].copy_from_slice(&new_supply.to_le_bytes());
    data[48..56].copy_from_slice(&new_balance.to_le_bytes());

    Ok(())
}
