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

const IX_WITHDRAW: u8 = 0;

const ERR_INVALID_AUTHORITY: u32 = 1002;
const ERR_INSUFFICIENT_FUNDS: u32 = 1003;

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;

    match *instruction {
        IX_WITHDRAW => withdraw(accounts, instruction_data),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

fn withdraw(accounts: &[AccountInfo], instruction_data: &[u8]) -> ProgramResult {
    let vault = &accounts[0];
    let authority = &accounts[1];
    let recipient = &accounts[2];

    let amount = u64::from_le_bytes(
        instruction_data[1..9]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );

    let vault_data = vault.try_borrow_data()?;
    let stored_authority = read_pubkey(&vault_data[8..40]);

    if stored_authority != *authority.key() {
        return Err(ProgramError::Custom(ERR_INVALID_AUTHORITY));
    }

    let balance = u64::from_le_bytes(
        vault_data[40..48]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );
    if balance < amount {
        return Err(ProgramError::Custom(ERR_INSUFFICIENT_FUNDS));
    }
    drop(vault_data);

    let mut vault_data = vault.try_borrow_mut_data()?;
    let new_balance = balance - amount;
    vault_data[40..48].copy_from_slice(&new_balance.to_le_bytes());
    drop(vault_data);

    unsafe {
        *vault.borrow_mut_lamports_unchecked() -= amount;
        *recipient.borrow_mut_lamports_unchecked() += amount;
    }

    Ok(())
}

#[inline]
fn read_pubkey(data: &[u8]) -> Pubkey {
    let mut bytes = [0u8; 32];
    bytes.copy_from_slice(&data[..32]);
    Pubkey::from(bytes)
}
