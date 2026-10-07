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

const IX_UPDATE_FEE: u8 = 0;

const ERR_UNAUTHORIZED: u32 = 6001;

 8] = [0xAD, 0x11, 0x1C, 0x0F, 0x19, 0x00, 0x00, 0x01];
 8] = [0x05, 0xE7, 0xDA, 0x7A, 0x00, 0x00, 0x00, 0x02];

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;

    let new_fee = u64::from_le_bytes(
        instruction_data[1..9]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );

    match *instruction {
        IX_UPDATE_FEE => update_fee(accounts, new_fee),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

fn update_fee(accounts: &[AccountInfo], new_fee: u64) -> ProgramResult {
    let config = &accounts[0];
    let authority = &accounts[1];

    let data = config.try_borrow_data()?;

    let admin = read_pubkey(&data[8..40]);

    if admin != *authority.key() {
        return Err(ProgramError::Custom(ERR_UNAUTHORIZED));
    }

    if !authority.is_signer() {
        return Err(ProgramError::Custom(ERR_UNAUTHORIZED));
    }

    drop(data);

    let mut data = config.try_borrow_mut_data()?;
    data[40..48].copy_from_slice(&new_fee.to_le_bytes());

    Ok(())
}

#[inline]
fn read_pubkey(data: &[u8]) -> Pubkey {
    let mut bytes = [0u8; 32];
    bytes.copy_from_slice(&data[..32]);
    Pubkey::from(bytes)
}
