//! Teste-oraculo do Solana Hacks (reinitialization, Rust nativo).
mod common;

use common::*;
use mollusk_svm::{result::Check, Mollusk};
use solana_sdk::{
    account::AccountSharedData,
    instruction::{AccountMeta, Instruction},
    pubkey::Pubkey,
    system_program,
};

#[test]
fn hk_reinit_attack() {
    // Conta ja inicializada com a authority de Alice; o atacante chama Init
    // de novo (MyInstruction::Init = byte 0) e sobrescreve a authority.
    let id = Pubkey::new_from_array([0x0A; 32]);
    let mollusk = Mollusk::new(&id, "hk_reinit");
    let alice = Pubkey::new_unique();
    let attacker = Pubkey::new_unique();
    let user = Pubkey::new_unique();
    let ix = Instruction::new_with_bytes(
        id,
        &[0u8],
        vec![AccountMeta::new(user, false), AccountMeta::new_readonly(attacker, false)],
    );
    mollusk.process_and_validate_instruction(
        &ix,
        &[
            (user, account(5_000_000, alice.as_ref(), &id)),
            (attacker, AccountSharedData::new(1_000_000, 0, &system_program::ID)),
        ],
        &[Check::success()],
    );
}
