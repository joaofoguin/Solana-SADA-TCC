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

const IX_PROCESS: u8 = 1;

const ERR_INVALID_OWNER: u32 = 2001;
const ERR_TREASURY_INACTIVE: u32 = 2002;

 32] = [
    0x6d, 0x8d, 0xa3, 0x9c, 0x42, 0x7f, 0x1b, 0x2a,
    0x5e, 0x9f, 0x3c, 0x8b, 0x7d, 0x4e, 0x6a, 0x1f,
    0x2b, 0x9c, 0x8d, 0x5e, 0x3f, 0x7a, 0x4c, 0x6b,
    0x1d, 0x8e, 0x9f, 0x2a, 0x5b, 0x3c, 0x7d, 0x4e,
];

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;

    match *instruction {
        IX_PROCESS => process(program_id, accounts),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

fn process(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let treasury = &accounts[0];
    let authority = &accounts[1];

    let treasury_owner = unsafe { treasury.owner() };
    if treasury_owner != program_id {

        return Err(ProgramError::Custom(ERR_INVALID_OWNER));
    }

    let data = treasury.try_borrow_data()?;

    let stored_authority = read_pubkey(&data[8..40]);
    let balance = u64::from_le_bytes(
        data[40..48].try_into().map_err(|_| ProgramError::InvalidInstructionData)?
    );
    let is_active = data[48] != 0;

    if !is_active {
        return Err(ProgramError::Custom(ERR_TREASURY_INACTIVE));
    }

    if !authority.is_signer() || stored_authority != *authority.key() {
        return Err(ProgramError::IllegalOwner);
    }

    Ok(())
}

#[inline]
fn read_pubkey(data: &[u8]) -> Pubkey {
    let mut bytes = [0u8; 32];
    bytes.copy_from_slice(&data[..32]);
    Pubkey::from(bytes)
}
