#![no_std]

pinocchio::nostd_panic_handler!();

use pinocchio::{
    account_info::AccountInfo,
    entrypoint,
    msg,
    program_error::ProgramError,
    pubkey::{create_program_address, find_program_address, Pubkey},
    ProgramResult,
};

entrypoint!(process_instruction);

const IX_SET_VALUE: u8 = 0;

const ERR_INVALID_BUMP: u32 = 5001;
const ERR_PDA_MISMATCH: u32 = 5002;

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;

    match *instruction {
        IX_SET_VALUE => set_value(program_id, accounts, instruction_data),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

fn set_value(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let data_account = &accounts[0];
    let user = &accounts[1];

    let bump = instruction_data[1];

    let value = u64::from_le_bytes(
        instruction_data[2..10]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );

    let seeds: &[&[u8]] = &[b"data", user.key().as_ref(), &[bump]];

    let expected_pda = create_program_address(seeds, program_id)
        .map_err(|_| ProgramError::Custom(ERR_INVALID_BUMP))?;

    if expected_pda != *data_account.key() {
        return Err(ProgramError::Custom(ERR_PDA_MISMATCH));
    }

    let mut data = data_account.try_borrow_mut_data()?;
    data[8..40].copy_from_slice(user.key().as_ref());
    data[40..48].copy_from_slice(&value.to_le_bytes());
    data[48] = bump;

    Ok(())
}
