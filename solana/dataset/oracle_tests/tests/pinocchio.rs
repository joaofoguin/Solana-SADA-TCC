//! Testes-oraculo das variantes Pinocchio do Solana Security Patterns.
//! Cada .so contem as duas instrucoes (vulneravel e segura), selecionadas
//! pelo primeiro byte dos dados da instrucao (tag).
mod common;

use common::*;
use mollusk_svm::{result::Check, Mollusk};
use solana_sdk::{
    account::AccountSharedData,
    instruction::{AccountMeta, Instruction},
    program_error::ProgramError,
    pubkey::Pubkey,
    system_program,
};

fn pid(n: u8) -> Pubkey {
    Pubkey::new_from_array([n; 32])
}

// ===========================================================================
// SSP-01-P  Missing Signer Check   tags: 0 = vulneravel, 1 = seguro
// ===========================================================================
fn p01(tag: u8, authority_signs: bool, check: Check) {
    let id = pid(0x01);
    let mollusk = Mollusk::new(&id, "ssp_01_p");
    let (auth, auth_acc) = wallet();
    let (vault, recipient) = (Pubkey::new_unique(), Pubkey::new_unique());
    let mut d = vec![0u8; 8];
    d.extend_from_slice(auth.as_ref());
    d.extend_from_slice(&500_000u64.to_le_bytes());
    let mut ixd = vec![tag];
    ixd.extend_from_slice(&500_000u64.to_le_bytes());
    let ix = Instruction::new_with_bytes(
        id,
        &ixd,
        vec![
            AccountMeta::new(vault, false),
            AccountMeta::new_readonly(auth, authority_signs),
            AccountMeta::new(recipient, false),
        ],
    );
    mollusk.process_and_validate_instruction(
        &ix,
        &[
            (vault, account(1_000_000, &d, &id)),
            (auth, auth_acc),
            (recipient, AccountSharedData::new(0, 0, &system_program::ID)),
        ],
        &[check],
    );
}

#[test]
fn ssp_01_p_v_attack() {
    p01(0, false, Check::success());
}
#[test]
fn ssp_01_p_s_attack() {
    p01(1, false, Check::err(ProgramError::Custom(1001)));
}
#[test]
fn ssp_01_p_s_sanity() {
    p01(1, true, Check::success());
}

// ===========================================================================
// SSP-02-P  Improper Owner Check   tags: 0 = vulneravel, 1 = seguro
// ===========================================================================
fn p02(tag: u8, owned_by_program: bool, check: Check) {
    let id = pid(0x02);
    let mollusk = Mollusk::new(&id, "ssp_02_p");
    let (auth, auth_acc) = wallet();
    let treasury = Pubkey::new_unique();
    let mut d = vec![0u8; 8];
    d.extend_from_slice(auth.as_ref());
    d.extend_from_slice(&999_999_999u64.to_le_bytes());
    d.push(1); // is_active
    let owner = if owned_by_program { id } else { Pubkey::new_unique() };
    let ix = Instruction::new_with_bytes(
        id,
        &[tag],
        vec![AccountMeta::new_readonly(treasury, false), AccountMeta::new_readonly(auth, true)],
    );
    mollusk.process_and_validate_instruction(
        &ix,
        &[(treasury, account(1_000_000, &d, &owner)), (auth, auth_acc)],
        &[check],
    );
}

#[test]
fn ssp_02_p_v_attack() {
    p02(0, false, Check::success());
}
#[test]
fn ssp_02_p_s_attack() {
    p02(1, false, Check::err(ProgramError::Custom(2001)));
}
#[test]
fn ssp_02_p_s_sanity() {
    p02(1, true, Check::success());
}

// ===========================================================================
// SSP-03-P  Integer Overflow / Underflow
//   tags: 0 = mint vulneravel, 1 = burn vulneravel, 2 = mint seguro, 3 = burn seguro
// ===========================================================================
fn p03(tag: u8, supply: u64, balance: u64, amount: u64, check: Check) {
    let id = pid(0x03);
    let mollusk = Mollusk::new(&id, "ssp_03_p");
    let ledger = Pubkey::new_unique();
    let mut d = vec![0u8; 8];
    d.extend_from_slice(Pubkey::new_unique().as_ref()); // authority
    d.extend_from_slice(&supply.to_le_bytes());
    d.extend_from_slice(&balance.to_le_bytes());
    let mut ixd = vec![tag];
    ixd.extend_from_slice(&amount.to_le_bytes());
    let ix = Instruction::new_with_bytes(id, &ixd, vec![AccountMeta::new(ledger, false)]);
    mollusk.process_and_validate_instruction(&ix, &[(ledger, account(10_000_000, &d, &id))], &[check]);
}

#[test]
fn ssp_03_p_v1_attack() {
    p03(0, u64::MAX, 0, 1, Check::success());
}
#[test]
fn ssp_03_p_v2_attack() {
    p03(1, 1_000, 10, 11, Check::success());
}
#[test]
fn ssp_03_p_s1_attack() {
    p03(2, u64::MAX, 0, 1, Check::err(ProgramError::Custom(3001)));
}
#[test]
fn ssp_03_p_s1_sanity() {
    p03(2, 1_000, 500, 100, Check::success());
}
#[test]
fn ssp_03_p_s2_attack() {
    p03(3, 1_000, 10, 11, Check::err(ProgramError::Custom(3002)));
}
#[test]
fn ssp_03_p_s2_sanity() {
    p03(3, 1_000, 500, 100, Check::success());
}

// ===========================================================================
// SSP-04-P  Reinitialization   tags: 0 = vulneravel, 1 = seguro
// ===========================================================================
fn p04(tag: u8, already_initialized: bool, check: Check) {
    let id = pid(0x04);
    let mollusk = Mollusk::new(&id, "ssp_04_p");
    let (attacker, attacker_acc) = wallet();
    let config = Pubkey::new_unique();
    let mut d = vec![1u8, 2, 3, 4, 5, 6, 7, 8];
    d.extend_from_slice(Pubkey::new_unique().as_ref()); // authority de Alice
    d.push(already_initialized as u8);
    d.extend_from_slice(&1_000_000u64.to_le_bytes());
    let ix = Instruction::new_with_bytes(
        id,
        &[tag],
        vec![AccountMeta::new(config, false), AccountMeta::new_readonly(attacker, true)],
    );
    mollusk.process_and_validate_instruction(
        &ix,
        &[(config, account(5_000_000, &d, &id)), (attacker, attacker_acc)],
        &[check],
    );
}

#[test]
fn ssp_04_p_v_attack() {
    p04(0, true, Check::success());
}
#[test]
fn ssp_04_p_s_attack() {
    p04(1, true, Check::err(ProgramError::Custom(4001)));
}
#[test]
fn ssp_04_p_s_sanity() {
    p04(1, false, Check::success());
}

// ===========================================================================
// SSP-05-P  PDA Canonicalization
//   tag 0 (vulneravel): [0, bump, value(8)]   tag 1 (seguro): [1, value(8)]
// ===========================================================================
fn p05(tag: u8, canonical: bool, check: Check) {
    let id = pid(0x05);
    let mollusk = Mollusk::new(&id, "ssp_05_p");
    let (user, user_acc) = wallet();
    let seeds: &[&[u8]] = &[b"data", user.as_ref()];
    let (pda, bump) = if canonical {
        Pubkey::find_program_address(seeds, &id)
    } else {
        non_canonical_pda(seeds, &id)
    };
    let mut ixd = vec![tag];
    if tag == 0 {
        ixd.push(bump);
    }
    ixd.extend_from_slice(&999_999u64.to_le_bytes());
    let ix = Instruction::new_with_bytes(
        id,
        &ixd,
        vec![AccountMeta::new(pda, false), AccountMeta::new_readonly(user, true)],
    );
    mollusk.process_and_validate_instruction(
        &ix,
        &[(pda, account(5_000_000, &[0u8; 49], &id)), (user, user_acc)],
        &[check],
    );
}

#[test]
fn ssp_05_p_v_attack() {
    p05(0, false, Check::success());
}
#[test]
fn ssp_05_p_s_attack() {
    p05(1, false, Check::err(ProgramError::Custom(5002)));
}
#[test]
fn ssp_05_p_s_sanity() {
    p05(1, true, Check::success());
}

// ===========================================================================
// SSP-06-P  Type Cosplay   tags: 0 = vulneravel, 1 = seguro
// ===========================================================================
const ADMIN_CONFIG_DISC: [u8; 8] = [0xAD, 0x11, 0x1C, 0x0F, 0x19, 0x00, 0x00, 0x01];
const USER_DATA_DISC: [u8; 8] = [0x05, 0xE7, 0xDA, 0x7A, 0x00, 0x00, 0x00, 0x02];

fn p06(tag: u8, disc: [u8; 8], check: Check) {
    let id = pid(0x06);
    let mollusk = Mollusk::new(&id, "ssp_06_p");
    let (signer, signer_acc) = wallet();
    let config = Pubkey::new_unique();
    let mut d = disc.to_vec();
    d.extend_from_slice(signer.as_ref()); // admin (ou authority do UserData)
    d.extend_from_slice(&100u64.to_le_bytes());
    let mut ixd = vec![tag];
    ixd.extend_from_slice(&9_999u64.to_le_bytes());
    let ix = Instruction::new_with_bytes(
        id,
        &ixd,
        vec![AccountMeta::new(config, false), AccountMeta::new_readonly(signer, true)],
    );
    mollusk.process_and_validate_instruction(
        &ix,
        &[(config, account(5_000_000, &d, &id)), (signer, signer_acc)],
        &[check],
    );
}

#[test]
fn ssp_06_p_v_attack() {
    p06(0, USER_DATA_DISC, Check::success());
}
#[test]
fn ssp_06_p_s_attack() {
    p06(1, USER_DATA_DISC, Check::err(ProgramError::Custom(6002)));
}
#[test]
fn ssp_06_p_s_sanity() {
    p06(1, ADMIN_CONFIG_DISC, Check::success());
}
