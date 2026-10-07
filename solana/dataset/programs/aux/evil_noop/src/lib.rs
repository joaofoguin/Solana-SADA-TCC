//! Programa do "atacante" usado apenas pelos testes-oraculo de Arbitrary CPI.
//! Aceita qualquer instrucao: se for invocado, o CPI arbitrario aconteceu.
use solana_program::{account_info::AccountInfo, entrypoint::ProgramResult, pubkey::Pubkey};

#[cfg(not(feature = "no-entrypoint"))]
solana_program::entrypoint!(process_instruction);

pub fn process_instruction(_program_id: &Pubkey, _accounts: &[AccountInfo], _data: &[u8]) -> ProgramResult {
    Ok(())
}
