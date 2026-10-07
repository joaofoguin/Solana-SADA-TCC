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

const IX_INIT: u8 = 0;

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;

    match *instruction {
        IX_INIT => init(accounts),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

fn init(accounts: &[AccountInfo]) -> ProgramResult {
    let config = &accounts[0];
    let authority = &accounts[1];

    let mut data = config.try_borrow_mut_data()?;

    data[0..8].copy_from_slice(&[1, 2, 3, 4, 5, 6, 7, 8]);

    data[8..40].copy_from_slice(authority.key().as_ref());

    data[40] = 1;

    data[41..49].copy_from_slice(&0u64.to_le_bytes());

    Ok(())
}
