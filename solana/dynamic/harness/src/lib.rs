//! dynamic/harness (SADA-Solana)
//!
//! Harness do Dynamic Agent. O LLM escreve apenas o corpo de um cenario de
//! ataque (tests/attempt.rs, gerado a cada tentativa); este arquivo fornece o
//! carregamento do programa, a montagem das instrucoes e das contas e o registro
//! do que aconteceu em cada execucao.
//!
//! Cada execucao emite uma linha `@@DYN {json}` na saida padrao. O agente em
//! Python le essas linhas e decide pela execucao, nao pelo texto do LLM:
//!   - "baseline": uso legitimo; precisa ter sucesso (prova que o cenario esta
//!     montado corretamente, como os testes de sanidade do Ground Truth);
//!   - "attack": a tentativa de ataque;
//!   - "effect": condicao sobre o estado depois do ataque que demonstra o dano.
//!
//! Configuracao (variaveis de ambiente definidas pelo agente):
//!   DYN_SO_PATH      caminho do .so do programa-alvo
//!   DYN_PROGRAM_ID   program id (declare_id! do codigo analisado)
//!   DYN_TARGET_NAME  nome da instrucao-alvo no codigo sanitizado
//!   DYN_TARGET_DISC  discriminador Anchor real da instrucao-alvo (hex, 8 bytes)
//!   DYN_ATTACKER_SO  (opcional) programa do atacante que aceita qualquer chamada
//!
//! O discriminador real e fornecido pelo agente porque a sanitizacao renomeia a
//! instrucao-alvo (ex.: o binario foi compilado com outro nome). O valor e um
//! hash opaco, sem o nome original.

pub use mollusk_svm::result::{InstructionResult, ProgramResult};
pub use mollusk_svm::Mollusk;
use sha2::{Digest, Sha256};
pub use solana_sdk::{
    account::{AccountSharedData, ReadableAccount, WritableAccount},
    instruction::{AccountMeta, Instruction},
    program_error::ProgramError,
    pubkey::Pubkey,
    rent::Rent,
    system_program,
};
use std::cell::RefCell;

pub mod prelude {
    pub use super::*;
    pub use solana_sdk::pubkey;
    /// Alias: codigo que use `solana_program::...` compila com o SDK.
    pub use solana_sdk as solana_program;
    /// Alias minimo: `anchor_lang::solana_program::...` e `anchor_lang::system_program`.
    pub mod anchor_lang {
        pub use solana_sdk as solana_program;
        pub use solana_sdk::system_program;
    }
}

/// Serializacao no formato Borsh (o que o Anchor usa para argumentos e contas).
/// Inteiros em little-endian, bool = 1 byte, Pubkey = 32 bytes, tuplas e arrays
/// fixos = campos concatenados. `Vec<u8>` e `&[u8]` sao tratados como bytes JA
/// serializados (concatenados sem prefixo de tamanho).
pub trait Fields {
    fn write(&self, out: &mut Vec<u8>);
    fn bytes(&self) -> Vec<u8> {
        let mut v = vec![];
        self.write(&mut v);
        v
    }
}
macro_rules! fields_int { ($($t:ty),*) => { $(impl Fields for $t { fn write(&self, o: &mut Vec<u8>) { o.extend_from_slice(&self.to_le_bytes()) } })* } }
fields_int!(u8, u16, u32, u64, u128, i8, i16, i32, i64, i128);
impl Fields for bool { fn write(&self, o: &mut Vec<u8>) { o.push(*self as u8) } }
impl Fields for Pubkey { fn write(&self, o: &mut Vec<u8>) { o.extend_from_slice(self.as_ref()) } }
impl Fields for () { fn write(&self, _: &mut Vec<u8>) {} }
impl Fields for Vec<u8> { fn write(&self, o: &mut Vec<u8>) { o.extend_from_slice(self) } }
impl Fields for [u8] { fn write(&self, o: &mut Vec<u8>) { o.extend_from_slice(self) } }
impl<T: Fields, const N: usize> Fields for [T; N] { fn write(&self, o: &mut Vec<u8>) { for x in self { x.write(o) } } }
impl<T: Fields + ?Sized> Fields for &T { fn write(&self, o: &mut Vec<u8>) { (**self).write(o) } }
macro_rules! fields_tuple { ($($n:ident),+) => {
    impl<$($n: Fields),+> Fields for ($($n,)+) {
        #[allow(non_snake_case)]
        fn write(&self, o: &mut Vec<u8>) { let ($($n,)+) = self; $($n.write(o);)+ }
    }
} }
fields_tuple!(A);
fields_tuple!(A, B);
fields_tuple!(A, B, C);
fields_tuple!(A, B, C, D);
fields_tuple!(A, B, C, D, E);
fields_tuple!(A, B, C, D, E, F);
fields_tuple!(A, B, C, D, E, F, G);
fields_tuple!(A, B, C, D, E, F, G, H);
impl<T: Fields> Fields for Option<T> {
    fn write(&self, o: &mut Vec<u8>) { match self { None => o.push(0), Some(x) => { o.push(1); x.write(o) } } }
}

const LOADER: Pubkey = solana_sdk::bpf_loader_upgradeable::ID;

/// Ambiente de execucao de um cenario.
pub struct Env {
    pub mollusk: Mollusk,
    pub program_id: Pubkey,
    /// Programa do atacante (aceita qualquer instrucao), se configurado.
    pub attacker_program: Option<Pubkey>,
    target_name: String,
    target_disc: Option<[u8; 8]>,
    steps: RefCell<Vec<String>>,
}

fn env(name: &str) -> Option<String> {
    std::env::var(name).ok().filter(|v| !v.is_empty())
}

impl Env {
    pub fn load() -> Self {
        let so = env("DYN_SO_PATH").expect("DYN_SO_PATH nao definido");
        let program_id: Pubkey = env("DYN_PROGRAM_ID")
            .expect("DYN_PROGRAM_ID nao definido")
            .parse()
            .expect("DYN_PROGRAM_ID invalido");
        let mut mollusk = Mollusk::default();
        let elf = std::fs::read(&so).unwrap_or_else(|e| panic!("nao foi possivel ler {so}: {e}"));
        mollusk.add_program_with_elf_and_loader(&program_id, &elf, &LOADER);

        let attacker_program = env("DYN_ATTACKER_SO").map(|path| {
            let id = Pubkey::new_unique();
            let elf = std::fs::read(&path).expect("DYN_ATTACKER_SO ilegivel");
            mollusk.add_program_with_elf_and_loader(&id, &elf, &LOADER);
            id
        });

        let target_disc = env("DYN_TARGET_DISC").map(|h| {
            let b: Vec<u8> = (0..16).step_by(2).map(|i| u8::from_str_radix(&h[i..i + 2], 16).unwrap()).collect();
            b.try_into().unwrap()
        });
        println!(
            "@@DYN {{\"step\":\"setup\",\"attacker_program\":\"{}\"}}",
            attacker_program.map(|p| p.to_string()).unwrap_or_default()
        );
        Env {
            mollusk,
            program_id,
            attacker_program,
            target_name: env("DYN_TARGET_NAME").unwrap_or_default(),
            target_disc,
            steps: RefCell::new(vec![]),
        }
    }

    /// Instrucao Anchor: discriminador de `name` + argumentos ja serializados (Borsh).
    pub fn anchor_ix<A: Fields + ?Sized>(&self, name: &str, args: &A, metas: Vec<AccountMeta>) -> Instruction {
        let disc = match self.target_disc {
            Some(d) if name == self.target_name => d,
            _ => anchor_ix_discriminator(name),
        };
        let mut data = disc.to_vec();
        args.write(&mut data);
        Instruction::new_with_bytes(self.program_id, &data, metas)
    }

    /// Instrucao com dados brutos (Rust nativo / Pinocchio).
    pub fn raw_ix<A: Fields + ?Sized>(&self, data: &A, metas: Vec<AccountMeta>) -> Instruction {
        Instruction::new_with_bytes(self.program_id, &data.bytes(), metas)
    }

    fn record(&self, step: &str, note: &str, ix: &Instruction, r: &InstructionResult) {
        let result = match &r.program_result {
            ProgramResult::Success => "Success".to_string(),
            ProgramResult::Failure(e) => format!("Failure({e:?})"),
            ProgramResult::UnknownError(e) => format!("UnknownError({e:?})"),
        };
        let metas: Vec<String> = ix
            .accounts
            .iter()
            .map(|m| format!("{}{}", if m.is_signer { "s" } else { "-" }, if m.is_writable { "w" } else { "r" }))
            .collect();
        println!(
            "@@DYN {{\"step\":\"{step}\",\"note\":{},\"result\":\"{}\",\"compute_units\":{},\"account_flags\":\"{}\"}}",
            json_str(note),
            result.replace('"', "'"),
            r.compute_units_consumed,
            metas.join(",")
        );
        self.steps.borrow_mut().push(step.to_string());
    }

    /// Uso legitimo da instrucao (ou preparacao de estado). Deve ter sucesso.
    pub fn baseline(&self, note: &str, ix: &Instruction, accounts: &[(Pubkey, AccountSharedData)]) -> InstructionResult {
        let r = self.mollusk.process_instruction(ix, accounts);
        self.record("baseline", note, ix, &r);
        r
    }

    /// A tentativa de ataque.
    pub fn attack(&self, note: &str, ix: &Instruction, accounts: &[(Pubkey, AccountSharedData)]) -> InstructionResult {
        let r = self.mollusk.process_instruction(ix, accounts);
        self.record("attack", note, ix, &r);
        r
    }

    /// Condicao sobre o estado depois do ataque que demonstra o dano
    /// (ex.: autoridade sobrescrita, saldo que deu a volta, lamports transferidos).
    pub fn effect(&self, note: &str, holds: bool) {
        println!("@@DYN {{\"step\":\"effect\",\"note\":{},\"holds\":{holds}}}", json_str(note));
    }
}

fn json_str(s: &str) -> String {
    let mut o = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            c if (c as u32) < 0x20 => {}
            c => o.push(c),
        }
    }
    o.push('"');
    o
}

fn sha8(s: &str) -> [u8; 8] {
    let h = Sha256::digest(s.as_bytes());
    h[..8].try_into().unwrap()
}

/// sha256("global:<nome>")[..8]
pub fn anchor_ix_discriminator(name: &str) -> [u8; 8] {
    sha8(&format!("global:{name}"))
}

/// sha256("account:<Tipo>")[..8]
pub fn anchor_account_discriminator(type_name: &str) -> [u8; 8] {
    sha8(&format!("account:{type_name}"))
}

/// Dados de uma conta Anchor: discriminador do tipo + campos ja serializados.
pub fn anchor_account_data<A: Fields + ?Sized>(type_name: &str, fields: &A) -> Vec<u8> {
    let mut d = anchor_account_discriminator(type_name).to_vec();
    fields.write(&mut d);
    d
}

/// Conta com dono, dados e lamports (minimo isento de aluguel se `lamports` for None).
pub fn account(owner: &Pubkey, data: &[u8], lamports: Option<u64>) -> AccountSharedData {
    let lamports = lamports.unwrap_or_else(|| Rent::default().minimum_balance(data.len()));
    let mut a = AccountSharedData::new(lamports, data.len(), owner);
    a.set_data_from_slice(data);
    a
}

/// Conta de carteira (dono: System Program, sem dados).
pub fn wallet(lamports: u64) -> AccountSharedData {
    AccountSharedData::new(lamports, 0, &system_program::ID)
}

/// Conta inexistente (ainda nao criada), para instrucoes que criam a conta.
pub fn empty_account() -> AccountSharedData {
    AccountSharedData::default()
}

/// Conta do System Program, para instrucoes que fazem CPI de criacao de conta.
pub fn system_program_account() -> (Pubkey, AccountSharedData) {
    mollusk_svm::program::keyed_account_for_system_program()
}

/// Conta executavel do programa do atacante, para passar no lugar de um programa esperado.
pub fn program_account(program_id: &Pubkey) -> AccountSharedData {
    mollusk_svm::program::create_program_account_loader_v3(program_id)
}

/// Busca uma conta no resultado de uma execucao.
pub fn after<'a>(r: &'a InstructionResult, key: &Pubkey) -> &'a AccountSharedData {
    r.get_account(key).expect("conta nao encontrada no resultado")
}

pub fn read_u64(data: &[u8], offset: usize) -> u64 {
    u64::from_le_bytes(data[offset..offset + 8].try_into().unwrap())
}

pub fn read_pubkey(data: &[u8], offset: usize) -> Pubkey {
    Pubkey::try_from(&data[offset..offset + 32]).unwrap()
}
