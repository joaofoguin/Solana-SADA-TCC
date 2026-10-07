//! Testes-oraculo do Sealevel Attacks (portado para anchor-lang 0.31.1).
//!
//! Convencao de nomes:
//!   <programa>_attack  -> o ataque da categoria-alvo; decide o rotulo
//!                         (aceito = vulneravel, rejeitado = seguro)
//!   <programa>_sanity  -> uso legitimo deve funcionar; prova que a rejeicao
//!                         do ataque nao e um bloqueio generico
mod common;

use common::*;
use mollusk_svm::{result::Check, Mollusk};
use solana_sdk::{
    account::AccountSharedData, bpf_loader_upgradeable, instruction::AccountMeta,
    program_error::ProgramError, pubkey::Pubkey, system_program, sysvar,
};

/// Todos os programas do sealevel declaram este ID (declare_id!).
const SL_ID: Pubkey = solana_sdk::pubkey!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");
/// Programa do atacante para o caso de Arbitrary CPI (evil_noop.so).
const EVIL_ID: Pubkey = Pubkey::new_from_array([7u8; 32]);

fn sl(name: &str) -> Mollusk {
    Mollusk::new(&SL_ID, name)
}

// ===========================================================================
// SL-00  Missing Signer Check  (ataque: authority NAO assina)
// ===========================================================================
fn sl00(prog: &str, authority_signs: bool, check: Check) {
    let mollusk = sl(prog);
    let (auth, auth_acc) = wallet();
    let ix = anchor_ix(SL_ID, "log_message", &[], vec![AccountMeta::new_readonly(auth, authority_signs)]);
    mollusk.process_and_validate_instruction(&ix, &[(auth, auth_acc)], &[check]);
}

#[test]
fn sl_00_ins_attack() {
    sl00("sl_00_ins", false, Check::success());
}
#[test]
fn sl_00_sec_attack() {
    sl00("sl_00_sec", false, Check::err(ProgramError::MissingRequiredSignature));
}
#[test]
fn sl_00_sec_sanity() {
    sl00("sl_00_sec", true, Check::success());
}
#[test]
fn sl_00_rec_attack() {
    // Anchor 3010 = AccountNotSigner
    sl00("sl_00_rec", false, Check::err(ProgramError::Custom(3010)));
}
#[test]
fn sl_00_rec_sanity() {
    sl00("sl_00_rec", true, Check::success());
}

// ===========================================================================
// SL-02  Improper Owner Check  (ataque: conta de token falsa, owner != SPL Token)
// ===========================================================================
fn sl02(prog: &str, token_account_owner: Pubkey, check: Check) {
    let mollusk = sl(prog);
    let (auth, auth_acc) = wallet();
    let token = Pubkey::new_unique();
    let data = spl_token_account_data(&Pubkey::new_unique(), &auth, 1_000);
    let token_acc = account(10_000_000, &data, &token_account_owner);
    let ix = anchor_ix(
        SL_ID,
        "log_message",
        &[],
        vec![AccountMeta::new_readonly(token, false), AccountMeta::new_readonly(auth, true)],
    );
    mollusk.process_and_validate_instruction(&ix, &[(token, token_acc), (auth, auth_acc)], &[check]);
}

#[test]
fn sl_02_ins_attack() {
    sl02("sl_02_ins", Pubkey::new_unique(), Check::success());
}
#[test]
fn sl_02_sec_attack() {
    sl02("sl_02_sec", Pubkey::new_unique(), Check::err(ProgramError::InvalidAccountData));
}
#[test]
fn sl_02_sec_sanity() {
    sl02("sl_02_sec", TOKEN_PROGRAM_ID, Check::success());
}
#[test]
fn sl_02_rec_attack() {
    // Anchor 3007 = AccountOwnedByWrongProgram
    sl02("sl_02_rec", Pubkey::new_unique(), Check::err(ProgramError::Custom(3007)));
}
#[test]
fn sl_02_rec_sanity() {
    sl02("sl_02_rec", TOKEN_PROGRAM_ID, Check::success());
}

// ===========================================================================
// SL-03  Type Cosplay  (ataque: conta Metadata passada onde se espera User)
// ===========================================================================
fn sl03(prog: &str, make_data: impl Fn(&Pubkey) -> Vec<u8>, check: Check) {
    let mollusk = sl(prog);
    let (auth, auth_acc) = wallet();
    let user = Pubkey::new_unique();
    let user_acc = account(10_000_000, &make_data(&auth), &SL_ID); // owner correto
    let ix = anchor_ix(
        SL_ID,
        "update_user",
        &[],
        vec![AccountMeta::new_readonly(user, false), AccountMeta::new_readonly(auth, true)],
    );
    mollusk.process_and_validate_instruction(&ix, &[(user, user_acc), (auth, auth_acc)], &[check]);
}

#[test]
fn sl_03_ins_attack() {
    // Metadata { account } tem o mesmo layout de User { authority }
    sl03("sl_03_ins", |k| k.as_ref().to_vec(), Check::success());
}
#[test]
fn sl_03_sec_attack() {
    // Metadata { discriminant: Metadata (=1), account }
    sl03("sl_03_sec", |k| [&[1u8][..], k.as_ref()].concat(), Check::err(ProgramError::InvalidAccountData));
}
#[test]
fn sl_03_sec_sanity() {
    // User { discriminant: User (=0), authority }
    sl03("sl_03_sec", |k| [&[0u8][..], k.as_ref()].concat(), Check::success());
}
#[test]
fn sl_03_rec_attack() {
    // Anchor 3002 = AccountDiscriminatorMismatch
    sl03("sl_03_rec", |k| [&acc_disc("Metadata")[..], k.as_ref()].concat(), Check::err(ProgramError::Custom(3002)));
}
#[test]
fn sl_03_rec_sanity() {
    sl03("sl_03_rec", |k| [&acc_disc("User")[..], k.as_ref()].concat(), Check::success());
}

// ===========================================================================
// SL-04  Reinitialization  (ataque: reinicializar conta ja inicializada por Alice)
// ===========================================================================
fn sl04_manual(prog: &str, existing_data: Vec<u8>, check: Check) {
    let mollusk = sl(prog);
    let (attacker, attacker_acc) = wallet();
    let user = Pubkey::new_unique();
    let user_acc = account(10_000_000, &existing_data, &SL_ID);
    let ix = anchor_ix(
        SL_ID,
        "initialize",
        &[],
        vec![AccountMeta::new(user, false), AccountMeta::new_readonly(attacker, true)],
    );
    mollusk.process_and_validate_instruction(&ix, &[(user, user_acc), (attacker, attacker_acc)], &[check]);
}

#[test]
fn sl_04_ins_attack() {
    let alice = Pubkey::new_unique();
    sl04_manual("sl_04_ins", alice.as_ref().to_vec(), Check::success());
}
#[test]
fn sl_04_sec_attack() {
    // Conta JA inicializada (discriminator = true). Se o rotulo da fonte
    // ("secure") estivesse certo, isto falharia. Sucesso = vulneravel.
    let alice = Pubkey::new_unique();
    sl04_manual("sl_04_sec", [&[1u8][..], alice.as_ref()].concat(), Check::success());
}
#[test]
fn sl_04_sec_first_init_blocked() {
    // Evidencia da condicao invertida: a PRIMEIRA inicializacao e bloqueada.
    sl04_manual("sl_04_sec", vec![0u8; 33], Check::err(ProgramError::InvalidAccountData));
}

fn sl04_rec(user_acc: AccountSharedData, attack: bool) {
    let mollusk = sl("sl_04_rec");
    let (payer, payer_acc) = wallet();
    let (sys, sys_acc) = system_program_account();
    let user = Pubkey::new_unique();
    let ix = anchor_ix(
        SL_ID,
        "init",
        &[],
        vec![
            AccountMeta::new(user, true),
            AccountMeta::new(payer, true),
            AccountMeta::new_readonly(sys, false),
        ],
    );
    let accounts = [(user, user_acc), (payer, payer_acc), (sys, sys_acc)];
    if attack {
        expect_failure(&mollusk, &ix, &accounts);
    } else {
        mollusk.process_and_validate_instruction(&ix, &accounts, &[Check::success()]);
    }
}

#[test]
fn sl_04_rec_attack() {
    let alice = Pubkey::new_unique();
    let data = [&acc_disc("User")[..], alice.as_ref()].concat();
    sl04_rec(account(10_000_000, &data, &SL_ID), true);
}
#[test]
fn sl_04_rec_sanity() {
    sl04_rec(AccountSharedData::new(0, 0, &system_program::ID), false);
}

// ===========================================================================
// SL-05  Arbitrary CPI  (ataque: token_program = programa do atacante)
// ===========================================================================
fn sl05(prog: &str, ix_name: &str, check: Check) {
    let mut mollusk = sl(prog);
    mollusk.add_program(&EVIL_ID, "evil_noop", &bpf_loader_upgradeable::id());
    let (auth, auth_acc) = wallet();
    let mint = Pubkey::new_unique();
    let (src, dst) = (Pubkey::new_unique(), Pubkey::new_unique());
    let src_acc = account(10_000_000, &spl_token_account_data(&mint, &auth, 1_000), &TOKEN_PROGRAM_ID);
    let dst_acc = account(10_000_000, &spl_token_account_data(&mint, &Pubkey::new_unique(), 0), &TOKEN_PROGRAM_ID);
    let ix = anchor_ix(
        SL_ID,
        ix_name,
        &100u64.to_le_bytes(),
        vec![
            AccountMeta::new(src, false),
            AccountMeta::new(dst, false),
            AccountMeta::new_readonly(auth, true),
            AccountMeta::new_readonly(EVIL_ID, false),
        ],
    );
    mollusk.process_and_validate_instruction(
        &ix,
        &[
            (src, src_acc),
            (dst, dst_acc),
            (auth, auth_acc),
            (EVIL_ID, program_account_v3(&EVIL_ID)),
        ],
        &[check],
    );
}

#[test]
fn sl_05_ins_attack() {
    // Fonte rotula como insecure, mas o construtor spl_token::instruction::transfer
    // rejeita program ids diferentes do SPL Token (check_program_account) antes
    // do CPI. Comportamento verificado: ataque rejeitado.
    sl05("sl_05_ins", "cpi", Check::err(ProgramError::IncorrectProgramId));
}
#[test]
fn sl_05_raw_attack() {
    // Variante do autor sem o construtor da biblioteca.
    // Sucesso = o programa do atacante foi invocado no lugar do SPL Token.
    sl05("sl_05_raw", "cpi", Check::success());
}
#[test]
fn sl_05_sec_attack() {
    sl05("sl_05_sec", "cpi_secure", Check::err(ProgramError::IncorrectProgramId));
}
#[test]
fn sl_05_rec_attack() {
    // Anchor 3008 = InvalidProgramId
    sl05("sl_05_rec", "cpi", Check::err(ProgramError::Custom(3008)));
}

// ===========================================================================
// SL-07  PDA Canonicalization  (ataque: PDA com bump nao canonico)
// ===========================================================================
fn sl07(prog: &str, ix_name: &str, canonical: bool, pass_bump: bool, check: Check) {
    let mollusk = sl(prog);
    let key: u64 = 42;
    let kb = key.to_le_bytes();
    let seeds: &[&[u8]] = &[&kb];
    let (pda, bump) = if canonical {
        Pubkey::find_program_address(seeds, &SL_ID)
    } else {
        non_canonical_pda(seeds, &SL_ID)
    };
    let mut args = kb.to_vec();
    args.extend_from_slice(&999u64.to_le_bytes()); // new_value
    if pass_bump {
        args.push(bump);
    }
    let data = [&acc_disc("Data")[..], &0u64.to_le_bytes()[..]].concat();
    let ix = anchor_ix(SL_ID, ix_name, &args, vec![AccountMeta::new(pda, false)]);
    mollusk.process_and_validate_instruction(&ix, &[(pda, account(5_000_000, &data, &SL_ID))], &[check]);
}

#[test]
fn sl_07_ins_attack() {
    sl07("sl_07_ins", "set_value", false, true, Check::success());
}
#[test]
fn sl_07_sec_attack() {
    sl07("sl_07_sec", "set_value_secure", false, true, Check::err(ProgramError::InvalidArgument));
}
#[test]
fn sl_07_sec_sanity() {
    sl07("sl_07_sec", "set_value_secure", true, true, Check::success());
}
#[test]
fn sl_07_rec_attack() {
    // Anchor 2006 = ConstraintSeeds
    sl07("sl_07_rec", "set_value", false, false, Check::err(ProgramError::Custom(2006)));
}
#[test]
fn sl_07_rec_sanity() {
    sl07("sl_07_rec", "set_value", true, false, Check::success());
}

// ===========================================================================
// SL-10  Sysvar Account Check  (ataque: conta falsa no lugar do sysvar Rent)
// ===========================================================================
fn rent_sysvar() -> (Pubkey, AccountSharedData) {
    let mut d = 3480u64.to_le_bytes().to_vec(); // lamports_per_byte_year
    d.extend_from_slice(&2.0f64.to_le_bytes()); // exemption_threshold
    d.push(50); // burn_percent
    (sysvar::rent::ID, account(1_000_000, &d, &sysvar::ID))
}

fn sl10(prog: &str, real_sysvar: bool, check: Check) {
    let mollusk = sl(prog);
    let (key, acc) = if real_sysvar {
        rent_sysvar()
    } else {
        (Pubkey::new_unique(), account(1_000_000, &[0u8; 17], &Pubkey::new_unique()))
    };
    let ix = anchor_ix(SL_ID, "check_sysvar_address", &[], vec![AccountMeta::new_readonly(key, false)]);
    mollusk.process_and_validate_instruction(&ix, &[(key, acc)], &[check]);
}

#[test]
fn sl_10_ins_attack() {
    sl10("sl_10_ins", false, Check::success());
}
#[test]
fn sl_10_sec_attack() {
    // Anchor 2501 = RequireEqViolated
    sl10("sl_10_sec", false, Check::err(ProgramError::Custom(2501)));
}
#[test]
fn sl_10_sec_sanity() {
    sl10("sl_10_sec", true, Check::success());
}
#[test]
fn sl_10_rec_attack() {
    // Anchor 3015 = AccountSysvarMismatch
    sl10("sl_10_rec", false, Check::err(ProgramError::Custom(3015)));
}
#[test]
fn sl_10_rec_sanity() {
    sl10("sl_10_rec", true, Check::success());
}
