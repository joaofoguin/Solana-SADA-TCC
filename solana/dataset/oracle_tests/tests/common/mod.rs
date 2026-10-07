//! Utilitarios compartilhados pelos testes-oraculo.
#![allow(dead_code)]

use mollusk_svm::{result::ProgramResult as MolluskResult, Mollusk};
use sha2::{Digest, Sha256};
use solana_sdk::{
    account::{AccountSharedData, WritableAccount},
    bpf_loader_upgradeable,
    instruction::{AccountMeta, Instruction},
    native_loader,
    pubkey::Pubkey,
    system_program,
};

pub const TOKEN_PROGRAM_ID: Pubkey =
    solana_sdk::pubkey!("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA");

fn sha8(prefix: &str, name: &str) -> [u8; 8] {
    let mut h = Sha256::new();
    h.update(format!("{prefix}:{name}").as_bytes());
    let out = h.finalize();
    let mut d = [0u8; 8];
    d.copy_from_slice(&out[..8]);
    d
}

/// Discriminador de instrucao Anchor: sha256("global:<nome>")[..8]
pub fn ix_disc(name: &str) -> [u8; 8] {
    sha8("global", name)
}

/// Discriminador de conta Anchor: sha256("account:<Tipo>")[..8]
pub fn acc_disc(name: &str) -> [u8; 8] {
    sha8("account", name)
}

pub fn anchor_ix(program_id: Pubkey, name: &str, args: &[u8], metas: Vec<AccountMeta>) -> Instruction {
    let mut data = ix_disc(name).to_vec();
    data.extend_from_slice(args);
    Instruction::new_with_bytes(program_id, &data, metas)
}

pub fn account(lamports: u64, data: &[u8], owner: &Pubkey) -> AccountSharedData {
    let mut a = AccountSharedData::new(lamports, data.len(), owner);
    a.set_data_from_slice(data);
    a
}

/// Carteira comum (owner = System Program), com saldo para pagar contas.
pub fn wallet() -> (Pubkey, AccountSharedData) {
    (
        Pubkey::new_unique(),
        AccountSharedData::new(10_000_000_000, 0, &system_program::ID),
    )
}

/// Conta executavel do System Program (necessaria quando o programa faz CPI nele).
pub fn system_program_account() -> (Pubkey, AccountSharedData) {
    let mut a = AccountSharedData::new(1, 0, &native_loader::id());
    a.set_executable(true);
    (system_program::ID, a)
}

/// Conta executavel de um programa carregado com o loader v3 (upgradeable).
pub fn program_account_v3(program_id: &Pubkey) -> AccountSharedData {
    let (programdata, _) =
        Pubkey::find_program_address(&[program_id.as_ref()], &bpf_loader_upgradeable::id());
    let mut data = 2u32.to_le_bytes().to_vec(); // UpgradeableLoaderState::Program
    data.extend_from_slice(programdata.as_ref());
    let mut a = account(1_000_000, &data, &bpf_loader_upgradeable::id());
    a.set_executable(true);
    a
}

/// Usado quando o codigo de erro exato nao e o objeto da verificacao:
/// basta que a instrucao seja rejeitada. Sempre pareado com um teste de sanidade.
pub fn expect_failure(mollusk: &Mollusk, ix: &Instruction, accounts: &[(Pubkey, AccountSharedData)]) {
    let r = mollusk.process_instruction(ix, accounts);
    println!("ORACLE_RESULT {:?}", r.program_result);
    assert!(
        !matches!(r.program_result, MolluskResult::Success),
        "esperava falha, mas a instrucao foi aceita"
    );
}

/// Conta SPL Token (layout Pack, 165 bytes) no estado Initialized.
pub fn spl_token_account_data(mint: &Pubkey, owner: &Pubkey, amount: u64) -> Vec<u8> {
    let mut d = Vec::with_capacity(165);
    d.extend_from_slice(mint.as_ref());
    d.extend_from_slice(owner.as_ref());
    d.extend_from_slice(&amount.to_le_bytes());
    d.extend_from_slice(&[0u8; 36]); // delegate: COption::None
    d.push(1); // state: Initialized
    d.extend_from_slice(&[0u8; 12]); // is_native: COption::None
    d.extend_from_slice(&0u64.to_le_bytes()); // delegated_amount
    d.extend_from_slice(&[0u8; 36]); // close_authority: COption::None
    assert_eq!(d.len(), 165);
    d
}

/// PDA valido com bump NAO canonico (abaixo do canonico) para as mesmas seeds.
pub fn non_canonical_pda(seeds: &[&[u8]], program_id: &Pubkey) -> (Pubkey, u8) {
    let (_, canonical) = Pubkey::find_program_address(seeds, program_id);
    for bump in (0..canonical).rev() {
        let b = [bump];
        let mut s: Vec<&[u8]> = seeds.to_vec();
        s.push(&b);
        if let Ok(pda) = Pubkey::create_program_address(&s, program_id) {
            return (pda, bump);
        }
    }
    panic!("nenhum bump nao canonico encontrado");
}
