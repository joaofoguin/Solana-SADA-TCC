# Coleta GT — saídas complementares

## 01 Estado do repositório (SSP)
```
a128ce9ceacadda7bb8ed686ce6a694439277dc5
 M Anchor.toml
 M Cargo.lock
 M Cargo.toml
 Anchor.toml |  10 +-
 Cargo.lock  | 449 ++++++++++++++++++++++++------------------------------------
 Cargo.toml  |  16 ++-
 3 files changed, 200 insertions(+), 275 deletions(-)
```

## 02 Inventário de arquivos
```
== patterns/01-missing-signer-check/
patterns/01-missing-signer-check/anchor/Cargo.toml
patterns/01-missing-signer-check/anchor/src/lib.rs
patterns/01-missing-signer-check/pinocchio/Cargo.toml
patterns/01-missing-signer-check/pinocchio/src/lib.rs
patterns/01-missing-signer-check/tests/Cargo.toml
patterns/01-missing-signer-check/tests/src/lib.rs
patterns/01-missing-signer-check/tests/tests/exploit.rs
== patterns/02-missing-owner-check/
patterns/02-missing-owner-check/anchor/Cargo.toml
patterns/02-missing-owner-check/anchor/src/lib.rs
patterns/02-missing-owner-check/pinocchio/Cargo.toml
patterns/02-missing-owner-check/pinocchio/src/lib.rs
patterns/02-missing-owner-check/tests/Cargo.toml
patterns/02-missing-owner-check/tests/src/lib.rs
patterns/02-missing-owner-check/tests/tests/exploit.rs
== patterns/03-integer-overflow/
patterns/03-integer-overflow/anchor/Cargo.toml
patterns/03-integer-overflow/anchor/src/lib.rs
patterns/03-integer-overflow/pinocchio/Cargo.toml
patterns/03-integer-overflow/pinocchio/src/lib.rs
patterns/03-integer-overflow/tests/Cargo.toml
patterns/03-integer-overflow/tests/src/lib.rs
patterns/03-integer-overflow/tests/tests/exploit.rs
== patterns/04-reinitialization-attack/
patterns/04-reinitialization-attack/anchor/Cargo.toml
patterns/04-reinitialization-attack/anchor/src/lib.rs
patterns/04-reinitialization-attack/pinocchio/Cargo.toml
patterns/04-reinitialization-attack/pinocchio/src/lib.rs
patterns/04-reinitialization-attack/tests/Cargo.toml
patterns/04-reinitialization-attack/tests/src/lib.rs
patterns/04-reinitialization-attack/tests/tests/exploit.rs
== patterns/05-pda-bump-canonicalization/
patterns/05-pda-bump-canonicalization/anchor/Cargo.toml
patterns/05-pda-bump-canonicalization/anchor/src/lib.rs
patterns/05-pda-bump-canonicalization/pinocchio/Cargo.toml
patterns/05-pda-bump-canonicalization/pinocchio/src/lib.rs
patterns/05-pda-bump-canonicalization/tests/Cargo.toml
patterns/05-pda-bump-canonicalization/tests/src/lib.rs
patterns/05-pda-bump-canonicalization/tests/tests/exploit.rs
== patterns/06-type-cosplay/
patterns/06-type-cosplay/anchor/Cargo.toml
patterns/06-type-cosplay/anchor/src/lib.rs
patterns/06-type-cosplay/pinocchio/Cargo.toml
patterns/06-type-cosplay/pinocchio/src/lib.rs
patterns/06-type-cosplay/tests/Cargo.toml
patterns/06-type-cosplay/tests/src/lib.rs
patterns/06-type-cosplay/tests/tests/exploit.rs
```

## 05 Binários .so
```
-rwxrwxr-x 1 tcc tcc 560248 Oct  6 19:12 ./target/release/deps/libanchor_attribute_constant-29442ec4f3d5153d.so
-rwxrwxr-x 1 tcc tcc 2770408 Oct  6 19:09 ./target/release/deps/libborsh_derive-8338d9cfec899427.so
-rwxrwxr-x 1 tcc tcc 1834320 Oct  6 19:12 ./target/release/deps/libanchor_attribute_event-542351c0964d2422.so
-rwxrwxr-x 1 tcc tcc 1985008 Oct  6 19:12 ./target/release/deps/libanchor_derive_serde-a552eb7d305ecb7f.so
-rwxrwxr-x 1 tcc tcc 2599224 Oct  6 19:12 ./target/release/deps/libanchor_derive_accounts-f1f68ea65cafa739.so
-rwxrwxr-x 1 tcc tcc 2383664 Oct  6 19:09 ./target/release/deps/libborsh_derive-9a6934c8c9e79eb4.so
-rwxrwxr-x 1 tcc tcc 1990720 Oct  6 19:11 ./target/release/deps/libnum_derive-03e0483a73e987e1.so
-rwxrwxr-x 1 tcc tcc 1792416 Oct  6 19:10 ./target/release/deps/libsolana_sdk_macro-611cb33b3d5a4753.so
-rwxrwxr-x 1 tcc tcc 2146504 Oct  6 19:10 ./target/release/deps/libbytemuck_derive-d988b80fb625cfcb.so
-rwxrwxr-x 1 tcc tcc 3512136 Oct  6 19:12 ./target/release/deps/libanchor_attribute_program-492b2983e02e6451.so
-rwxrwxr-x 1 tcc tcc 1937456 Oct  6 19:12 ./target/release/deps/libanchor_attribute_account-33e8825766fa1698.so
-rwxrwxr-x 1 tcc tcc 2166880 Oct  6 19:10 ./target/release/deps/libthiserror_impl-10323945422acbda.so
-rwxrwxr-x 1 tcc tcc 2021144 Oct  6 19:12 ./target/release/deps/libanchor_derive_space-b454fef99c0969ce.so
-rwxrwxr-x 1 tcc tcc 1657320 Oct  6 19:12 ./target/release/deps/libanchor_attribute_access_control-225023b596f1da9d.so
-rwxrwxr-x 1 tcc tcc 1977912 Oct  6 19:12 ./target/release/deps/libanchor_attribute_error-3ddb864fd1e0cbc2.so
-rwxrwxr-x 1 tcc tcc 2657824 Oct  6 19:08 ./target/release/deps/libserde_derive-44123c65aa172c1d.so
-rwxrwxr-x 2 tcc tcc 293136 Oct  6 19:14 ./target/sbf-solana-solana/release/integer_overflow.so
-rwxrwxr-x 2 tcc tcc 272848 Oct  6 19:14 ./target/sbf-solana-solana/release/type_cosplay.so
-rwxrwxr-x 2 tcc tcc 298328 Oct  6 19:13 ./target/sbf-solana-solana/release/missing_owner.so
-rwxrwxr-x 2 tcc tcc 273720 Oct  6 19:14 ./target/sbf-solana-solana/release/pda_bump.so
-rwxrwxr-x 2 tcc tcc 318680 Oct  6 19:12 ./target/sbf-solana-solana/release/missing_signer.so
-rwxrwxr-x 2 tcc tcc 293136 Oct  6 19:14 ./target/sbf-solana-solana/release/deps/integer_overflow.so
-rwxrwxr-x 2 tcc tcc 272848 Oct  6 19:14 ./target/sbf-solana-solana/release/deps/type_cosplay.so
-rwxrwxr-x 2 tcc tcc 298328 Oct  6 19:13 ./target/sbf-solana-solana/release/deps/missing_owner.so
-rwxrwxr-x 2 tcc tcc 273720 Oct  6 19:14 ./target/sbf-solana-solana/release/deps/pda_bump.so
-rwxrwxr-x 2 tcc tcc 318680 Oct  6 19:12 ./target/sbf-solana-solana/release/deps/missing_signer.so
-rwxrwxr-x 2 tcc tcc 295272 Oct  6 19:14 ./target/sbf-solana-solana/release/deps/reinitialization.so
-rwxrwxr-x 1 tcc tcc 4992 Oct  6 19:12 ./target/sbf-solana-solana/release/deps/solana_program-c6c29a8e5b9a4cec.so
-rwxrwxr-x 2 tcc tcc 295272 Oct  6 19:14 ./target/sbf-solana-solana/release/reinitialization.so
-rwxrwxr-x 1 tcc tcc 9121304 Oct  6 19:22 ./target/debug/deps/libbytemuck_derive-afcb537fe312102c.so
-rwxrwxr-x 1 tcc tcc 10438576 Oct  6 19:23 ./target/debug/deps/libdarling_macro-09d4bf507eb268b0.so
-rwxrwxr-x 1 tcc tcc 9854136 Oct  6 19:23 ./target/debug/deps/libserde_with_macros-2809eef3c6fee2fa.so
-rwxrwxr-x 1 tcc tcc 8587656 Oct  6 19:22 ./target/debug/deps/libark_ff_asm-030ecfc4703c1e9b.so
-rwxrwxr-x 1 tcc tcc 8569872 Oct  6 19:22 ./target/debug/deps/libcurve25519_dalek_derive-d7fc43810b48481e.so
-rwxrwxr-x 1 tcc tcc 6225832 Oct  6 19:23 ./target/debug/deps/libcfg_eval-e3c1fc9c422efcb9.so
-rwxrwxr-x 1 tcc tcc 10496160 Oct  6 19:23 ./target/debug/deps/libnum_enum_derive-07ed57d23696a27b.so
-rwxrwxr-x 1 tcc tcc 8337872 Oct  6 19:22 ./target/debug/deps/libsolana_sdk_macro-9543a7fb351985de.so
-rwxrwxr-x 1 tcc tcc 10318968 Oct  6 19:21 ./target/debug/deps/libserde_derive-051a83739a606bb3.so
-rwxrwxr-x 1 tcc tcc 9116296 Oct  6 19:24 ./target/debug/deps/libenum_iterator_derive-f7d9795351dfa75c.so
-rwxrwxr-x 1 tcc tcc 11484216 Oct  6 19:22 ./target/debug/deps/libborsh_derive-7e0adc3ffb55cb89.so
-rwxrwxr-x 1 tcc tcc 9001728 Oct  6 19:22 ./target/debug/deps/libark_ff_macros-a6ca1b68c2eea98b.so
-rwxrwxr-x 1 tcc tcc 5963216 Oct  6 19:22 ./target/debug/deps/libpaste-06e23744eedb31a5.so
-rwxrwxr-x 1 tcc tcc 9949200 Oct  6 19:22 ./target/debug/deps/libzerofrom_derive-fdf098a4ead0af96.so
-rwxrwxr-x 1 tcc tcc 6022312 Oct  6 19:23 ./target/debug/deps/librustversion-cf3dba27378dc437.so
-rwxrwxr-x 1 tcc tcc 9648320 Oct  6 19:22 ./target/debug/deps/libborsh_derive-df860bcd52fdc884.so
-rwxrwxr-x 1 tcc tcc 9155736 Oct  6 19:22 ./target/debug/deps/libthiserror_impl-81441806d41d9472.so
-rwxrwxr-x 1 tcc tcc 5693560 Oct  6 19:24 ./target/debug/deps/libmultiversion_no_op-c52514c69287ce98.so
-rwxrwxr-x 1 tcc tcc 17768424 Oct  6 19:23 ./target/debug/deps/libsolana_program-0f6836399e53ae7c.so
-rwxrwxr-x 1 tcc tcc 9133248 Oct  6 19:22 ./target/debug/deps/libzerovec_derive-ea3564b08194904f.so
-rwxrwxr-x 1 tcc tcc 8276144 Oct  6 19:22 ./target/debug/deps/libark_serialize_derive-daa5a1386c4da7bc.so
-rwxrwxr-x 1 tcc tcc 10209432 Oct  6 19:22 ./target/debug/deps/libderivative-c138f87f2dc97399.so
-rwxrwxr-x 1 tcc tcc 8618048 Oct  6 19:23 ./target/debug/deps/libnum_derive-def4ea9948c2ac79.so
-rwxrwxr-x 1 tcc tcc 9567272 Oct  6 19:22 ./target/debug/deps/libyoke_derive-ceab26e345ca5b6b.so
-rwxrwxr-x 1 tcc tcc 28172952 Oct  6 19:23 ./target/debug/deps/libsolana_sdk-c2b9ab955311a750.so
-rwxrwxr-x 1 tcc tcc 8857352 Oct  6 19:21 ./target/debug/deps/libzeroize_derive-271b80b3b0935a51.so
-rwxrwxr-x 1 tcc tcc 8845072 Oct  6 19:23 ./target/debug/deps/libdisplaydoc-d1e8ea25b1991505.so
-rwxrwxr-x 1 tcc tcc 212456 Oct  6 19:14 ./target/deploy/integer_overflow.so
-rwxrwxr-x 1 tcc tcc 194288 Oct  6 19:14 ./target/deploy/type_cosplay.so
-rwxrwxr-x 1 tcc tcc 215624 Oct  6 19:13 ./target/deploy/missing_owner.so
-rwxrwxr-x 1 tcc tcc 194696 Oct  6 19:14 ./target/deploy/pda_bump.so
-rwxrwxr-x 1 tcc tcc 234096 Oct  6 19:12 ./target/deploy/missing_signer.so
-rwxrwxr-x 1 tcc tcc 212264 Oct  6 19:14 ./target/deploy/reinitialization.so
```

## 06 Origem do solana-hacks
```
160000 commit 7a0bebc9f40591eeb7e273ce57d166c759ec0d7f	solana/solana-hacks
160000 commit a128ce9ceacadda7bb8ed686ce6a694439277dc5	solana/solana-security-pattern
160000 7a0bebc9f40591eeb7e273ce57d166c759ec0d7f 0	solana/solana-hacks
10:Those topics were widely covered including [this repo](https://github.com/MerovingioOps/Solana-hacking-stuff)
43:- https://github.com/coral-xyz/sealevel-attacks/
LICENSE
README.md
account-data-match
bump-seed-canonicalization
cast_truncation
close-account
cosplay
duplicated
error-not-handled
malicious-simulation
other-bugs
reinitialization
```

## 07 Diff local (Anchor.toml / Cargo.toml)
```
diff --git a/Anchor.toml b/Anchor.toml
index f7cbd3f..d503542 100644
--- a/Anchor.toml
+++ b/Anchor.toml
@@ -1,5 +1,10 @@
 [toolchain]
-channel = "1.88.0"
+#channel = "1.88.0"
+
+[workspace]
+members = [
+	"patterns/*"
+]
 
 [features]
 resolution = true
@@ -9,8 +14,7 @@ skip-lint = false
 missing_signer = "HF33f3iZYeK7qz7AE1aWWGvQuxArTudNjKVseAhTYCRC"
 missing_owner = "8anCcUkKVms75R4HYTnkbM6YGzAra9WTmXhNEY5RSaNw"
 
-[registry]
-url = "https://api.apr.dev"
+#url = "https://api.apr.dev"
 
 [provider]
 cluster = "localnet"
diff --git a/Cargo.toml b/Cargo.toml
index 9d5c66f..cbfb03c 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -1,12 +1,20 @@
 [workspace]
 members = [
-    "patterns/*/anchor",
-    "patterns/*/pinocchio",
-    "patterns/*/tests",
+    "patterns/01-missing-signer-check/anchor",
+    "patterns/02-missing-owner-check/anchor",
+    "patterns/03-integer-overflow/anchor",
+    "patterns/04-reinitialization-attack/anchor",
+    "patterns/05-pda-bump-canonicalization/anchor",
+    "patterns/06-type-cosplay/anchor",
+    "patterns/01-missing-signer-check/tests",
+    "patterns/02-missing-owner-check/tests",
+    "patterns/03-integer-overflow/tests",
+    "patterns/04-reinitialization-attack/tests",
+    "patterns/05-pda-bump-canonicalization/tests",
+    "patterns/06-type-cosplay/tests",
 ]
 resolver = "2"
 
-# Pin blake3 to avoid edition 2024 incompatibility with Solana Platform Tools' Cargo 1.84
 [workspace.dependencies]
 blake3 = "=1.5.5"
 
```

## 08 Variantes Pinocchio
### patterns/01-missing-signer-check/pinocchio/src/lib.rs
```rust
//! # Pattern 1: Missing Signer Check (Pinocchio)
//!
//! Demonstrates the vulnerability using Pinocchio's low-level approach.
//! Unlike Anchor, Pinocchio requires explicit manual checks for everything.

#![no_std]

// Required for no_std
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

/// Instruction discriminators (first byte of instruction data)
const IX_WITHDRAW_VULNERABLE: u8 = 0;
const IX_WITHDRAW_SECURE: u8 = 1;

/// Custom error codes
const ERR_MISSING_SIGNER: u32 = 1001;
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
        IX_WITHDRAW_VULNERABLE => withdraw_vulnerable(accounts, instruction_data),
        IX_WITHDRAW_SECURE => withdraw_secure(accounts, instruction_data),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

// ============================================================================
// VULNERABLE: Does NOT check is_signer on authority
// ============================================================================
// ISSUE: We read the authority pubkey and compare it to the vault's stored
//        authority, but we NEVER verify that the authority actually signed
//        the transaction. Anyone can pass any pubkey as the authority.
//
// ATTACK:
//   1. Attacker finds a vault with funds
//   2. Reads the vault's authority pubkey from on-chain data
//   3. Passes that pubkey as the authority account (without signing)
//   4. Drains the vault to their own account
// ============================================================================
fn withdraw_vulnerable(accounts: &[AccountInfo], instruction_data: &[u8]) -> ProgramResult {
    let vault = &accounts[0];
    let authority = &accounts[1];
    let recipient = &accounts[2];

    // Parse withdrawal amount from instruction data (bytes 1-8)
    let amount = u64::from_le_bytes(
        instruction_data[1..9]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );

    // Read stored authority from vault data (skip 8-byte discriminator)
    let vault_data = vault.try_borrow_data()?;
    let stored_authority = read_pubkey(&vault_data[8..40]);

    // VULNERABLE: Only checks pubkey match, NOT signature!
    // This check passes even if authority didn't sign the transaction.
    if stored_authority != *authority.key() {
        return Err(ProgramError::Custom(ERR_INVALID_AUTHORITY));
    }

    // NOTE: We're NOT checking authority.is_signer() here!
    // That's the vulnerability.

    // Read balance from vault (offset 40)
    let balance = u64::from_le_bytes(
        vault_data[40..48]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );
    if balance < amount {
        return Err(ProgramError::Custom(ERR_INSUFFICIENT_FUNDS));
    }
    drop(vault_data);

    // Update vault balance
    let mut vault_data = vault.try_borrow_mut_data()?;
    let new_balance = balance - amount;
    vault_data[40..48].copy_from_slice(&new_balance.to_le_bytes());
    drop(vault_data);

    // Transfer lamports
    unsafe {
        *vault.borrow_mut_lamports_unchecked() -= amount;
        *recipient.borrow_mut_lamports_unchecked() += amount;
    }

    msg!("VULNERABLE: Withdrew without signer check");
    Ok(())
}

// ============================================================================
// SECURE: Explicitly checks is_signer on authority
// ============================================================================
// FIX: Before trusting the authority account, verify that:
//   1. The pubkey matches the stored authority (authorization)
//   2. The account actually signed the transaction (authentication)
//
// This is what Anchor's Signer<'info> type does automatically.
// In Pinocchio/native, we must do it ourselves.
// ============================================================================
fn withdraw_secure(accounts: &[AccountInfo], instruction_data: &[u8]) -> ProgramResult {
    let vault = &accounts[0];
    let authority = &accounts[1];
    let recipient = &accounts[2];

    let amount = u64::from_le_bytes(
        instruction_data[1..9]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );

    // SECURE: Check that authority signed the transaction FIRST
    if !authority.is_signer() {
        msg!("ERROR: Authority must sign the transaction");
        return Err(ProgramError::Custom(ERR_MISSING_SIGNER));
    }

    // Now verify the authority matches the vault's stored authority
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

    // Update vault balance
    let mut vault_data = vault.try_borrow_mut_data()?;
    let new_balance = balance - amount;
    vault_data[40..48].copy_from_slice(&new_balance.to_le_bytes());
    drop(vault_data);

    // Transfer lamports
    unsafe {
        *vault.borrow_mut_lamports_unchecked() -= amount;
        *recipient.borrow_mut_lamports_unchecked() += amount;
    }

    msg!("SECURE: Withdrew with signer verification");
    Ok(())
}

/// Helper to read a Pubkey from a byte slice
#[inline]
fn read_pubkey(data: &[u8]) -> Pubkey {
    let mut bytes = [0u8; 32];
    bytes.copy_from_slice(&data[..32]);
    Pubkey::from(bytes)
}
```

### patterns/02-missing-owner-check/pinocchio/src/lib.rs
```rust
//! # Pattern 2: Missing Owner Check (Pinocchio)
//!
//! Demonstrates trusting account data without verifying account ownership.
//! This is the vulnerability that led to the $326M Wormhole hack.

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

const IX_PROCESS_VULNERABLE: u8 = 0;
const IX_PROCESS_SECURE: u8 = 1;

const ERR_INVALID_OWNER: u32 = 2001;
const ERR_TREASURY_INACTIVE: u32 = 2002;

/// Our program ID - accounts we trust must be owned by this
const PROGRAM_ID: [u8; 32] = [
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
        IX_PROCESS_VULNERABLE => process_vulnerable(accounts),
        IX_PROCESS_SECURE => process_secure(program_id, accounts),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

// ============================================================================
// VULNERABLE: Does NOT check account owner
// ============================================================================
// ISSUE: We read data from the treasury account without verifying that it
//        is owned by our program. An attacker can create a fake account
//        with arbitrary data and pass it in.
//
// WORMHOLE ATTACK (Feb 2022, $326M):
//   1. Attacker created a fake SignatureSet account (not owned by Wormhole)
//   2. Filled it with data that looked like valid guardian signatures
//   3. Passed it to Wormhole's verify function
//   4. Wormhole trusted the data and approved a 120,000 ETH transfer
// ============================================================================
fn process_vulnerable(accounts: &[AccountInfo]) -> ProgramResult {
    let treasury = &accounts[0];
    let authority = &accounts[1];

    // VULNERABLE: Directly reading account data without checking owner!
    // This data could come from ANY program - completely fabricated.
    let data = treasury.try_borrow_data()?;

    // Skip 8-byte discriminator, read authority at offset 8
    let stored_authority = read_pubkey(&data[8..40]);

    // Read balance at offset 40
    let balance = u64::from_le_bytes(
        data[40..48].try_into().map_err(|_| ProgramError::InvalidInstructionData)?
    );

    // Read is_active flag at offset 48
    let is_active = data[48] != 0;

    if !is_active {
        return Err(ProgramError::Custom(ERR_TREASURY_INACTIVE));
    }

    // NOTE: We never checked treasury.owner() == our program_id!
    // An attacker's fake account passes all these checks.

    msg!("VULNERABLE: Processed treasury without owner check");
    msg!("Authority and balance could be completely fake!");

    Ok(())
}

// ============================================================================
// SECURE: Verifies account owner before trusting data
// ============================================================================
// FIX: Check that the account is owned by our program before reading data.
// If the owner doesn't match, reject the account immediately.
//
// This is what Anchor's Account<T> type does automatically.
// ============================================================================
fn process_secure(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let treasury = &accounts[0];
    let authority = &accounts[1];

    // SECURE: Verify the treasury account is owned by our program
    // Note: owner() is unsafe in Pinocchio as it's a raw pointer dereference
    let treasury_owner = unsafe { treasury.owner() };
    if treasury_owner != program_id {
        msg!("ERROR: Treasury not owned by this program");
        return Err(ProgramError::Custom(ERR_INVALID_OWNER));
    }

    // Now we can trust the data
    let data = treasury.try_borrow_data()?;

    let stored_authority = read_pubkey(&data[8..40]);
    let balance = u64::from_le_bytes(
        data[40..48].try_into().map_err(|_| ProgramError::InvalidInstructionData)?
    );
    let is_active = data[48] != 0;

    if !is_active {
        return Err(ProgramError::Custom(ERR_TREASURY_INACTIVE));
    }

    // Verify signer matches stored authority
    if !authority.is_signer() || stored_authority != *authority.key() {
        return Err(ProgramError::IllegalOwner);
    }

    msg!("SECURE: Processed treasury with owner verification");

    Ok(())
}

#[inline]
fn read_pubkey(data: &[u8]) -> Pubkey {
    let mut bytes = [0u8; 32];
    bytes.copy_from_slice(&data[..32]);
    Pubkey::from(bytes)
}
```

### patterns/03-integer-overflow/pinocchio/src/lib.rs
```rust
//! # Pattern 3: Integer Overflow/Underflow (Pinocchio)
//!
//! Demonstrates arithmetic that wraps instead of failing.
//! Solana BPF programs run in release mode where overflow wraps silently.

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

const IX_MINT_VULNERABLE: u8 = 0;
const IX_BURN_VULNERABLE: u8 = 1;
const IX_MINT_SECURE: u8 = 2;
const IX_BURN_SECURE: u8 = 3;

const ERR_OVERFLOW: u32 = 3001;
const ERR_UNDERFLOW: u32 = 3002;

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;

    let amount = u64::from_le_bytes(
        instruction_data[1..9]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );

    match *instruction {
        IX_MINT_VULNERABLE => mint_vulnerable(accounts, amount),
        IX_BURN_VULNERABLE => burn_vulnerable(accounts, amount),
        IX_MINT_SECURE => mint_secure(accounts, amount),
        IX_BURN_SECURE => burn_secure(accounts, amount),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

// ============================================================================
// VULNERABLE: Uses wrapping arithmetic
// ============================================================================
// ISSUE: In release mode (how Solana BPF compiles), overflow wraps silently.
//   - u64::MAX + 1 = 0
//   - 0 - 1 = u64::MAX
//
// ATTACK:
//   1. Attacker has balance = 10 tokens
//   2. Calls burn(11) on vulnerable instruction
//   3. balance = 10 - 11 = 18446744073709551615 (u64::MAX)
//   4. Attacker now has quintillions of tokens
// ============================================================================
fn mint_vulnerable(accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let ledger = &accounts[0];

    let mut data = ledger.try_borrow_mut_data()?;

    // Read current supply (offset 40 after discriminator + authority)
    let supply = u64::from_le_bytes(data[40..48].try_into().unwrap());
    let balance = u64::from_le_bytes(data[48..56].try_into().unwrap());

    // VULNERABLE: wrapping_add - if supply is near max, wraps to 0
    let new_supply = supply.wrapping_add(amount);
    let new_balance = balance.wrapping_add(amount);

    data[40..48].copy_from_slice(&new_supply.to_le_bytes());
    data[48..56].copy_from_slice(&new_balance.to_le_bytes());

    msg!("VULNERABLE MINT: supply wrapped without error");
    Ok(())
}

fn burn_vulnerable(accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let ledger = &accounts[0];

    let mut data = ledger.try_borrow_mut_data()?;

    let supply = u64::from_le_bytes(data[40..48].try_into().unwrap());
    let balance = u64::from_le_bytes(data[48..56].try_into().unwrap());

    // VULNERABLE: wrapping_sub - if balance < amount, wraps to huge number
    let new_supply = supply.wrapping_sub(amount);
    let new_balance = balance.wrapping_sub(amount);

    data[40..48].copy_from_slice(&new_supply.to_le_bytes());
    data[48..56].copy_from_slice(&new_balance.to_le_bytes());

    msg!("VULNERABLE BURN: balance wrapped without error");
    Ok(())
}

// ============================================================================
// SECURE: Uses checked arithmetic
// ============================================================================
// FIX: Use checked_add/checked_sub which return None on overflow/underflow.
// Convert None to a program error.
// ============================================================================
fn mint_secure(accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let ledger = &accounts[0];

    let mut data = ledger.try_borrow_mut_data()?;

    let supply = u64::from_le_bytes(data[40..48].try_into().unwrap());
    let balance = u64::from_le_bytes(data[48..56].try_into().unwrap());

    // SECURE: checked_add returns None on overflow
    let new_supply = supply
        .checked_add(amount)
        .ok_or(ProgramError::Custom(ERR_OVERFLOW))?;
    let new_balance = balance
        .checked_add(amount)
        .ok_or(ProgramError::Custom(ERR_OVERFLOW))?;

    data[40..48].copy_from_slice(&new_supply.to_le_bytes());
    data[48..56].copy_from_slice(&new_balance.to_le_bytes());

    msg!("SECURE MINT: overflow would be rejected");
    Ok(())
}

fn burn_secure(accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let ledger = &accounts[0];

    let mut data = ledger.try_borrow_mut_data()?;

    let supply = u64::from_le_bytes(data[40..48].try_into().unwrap());
    let balance = u64::from_le_bytes(data[48..56].try_into().unwrap());

    // SECURE: checked_sub returns None on underflow
    let new_balance = balance
        .checked_sub(amount)
        .ok_or(ProgramError::Custom(ERR_UNDERFLOW))?;
    let new_supply = supply
        .checked_sub(amount)
        .ok_or(ProgramError::Custom(ERR_UNDERFLOW))?;

    data[40..48].copy_from_slice(&new_supply.to_le_bytes());
    data[48..56].copy_from_slice(&new_balance.to_le_bytes());

    msg!("SECURE BURN: underflow would be rejected");
    Ok(())
}
```

### patterns/04-reinitialization-attack/pinocchio/src/lib.rs
```rust
//! # Pattern 4: Re-initialization Attack (Pinocchio)
//!
//! Demonstrates allowing accounts to be initialized multiple times,
//! enabling attackers to overwrite authority and steal funds.

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

const IX_INIT_VULNERABLE: u8 = 0;
const IX_INIT_SECURE: u8 = 1;

const ERR_ALREADY_INITIALIZED: u32 = 4001;

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;

    match *instruction {
        IX_INIT_VULNERABLE => init_vulnerable(accounts),
        IX_INIT_SECURE => init_secure(accounts),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

// ============================================================================
// VULNERABLE: No initialization guard
// ============================================================================
// ISSUE: This instruction writes config data without checking if the account
//        was already initialized. An attacker can:
//
//   1. Wait for legitimate owner to initialize config
//   2. Call init_vulnerable again with attacker's key as authority
//   3. Config is overwritten - attacker now controls the account
//
// ATTACK SCENARIO:
//   - Alice creates config with authority = Alice
//   - Alice deposits 1000 SOL to associated vault
//   - Attacker calls init_vulnerable with authority = Attacker
//   - Config now has authority = Attacker
//   - Attacker withdraws all funds
// ============================================================================
fn init_vulnerable(accounts: &[AccountInfo]) -> ProgramResult {
    let config = &accounts[0];
    let authority = &accounts[1];

    let mut data = config.try_borrow_mut_data()?;

    // VULNERABLE: No check for existing initialization!
    // Just blindly write the new authority.

    // Write discriminator (8 bytes)
    data[0..8].copy_from_slice(&[1, 2, 3, 4, 5, 6, 7, 8]);

    // Write authority pubkey (32 bytes at offset 8)
    data[8..40].copy_from_slice(authority.key().as_ref());

    // Write is_initialized = true (1 byte at offset 40)
    data[40] = 1;

    // Write vault_balance = 0 (8 bytes at offset 41)
    data[41..49].copy_from_slice(&0u64.to_le_bytes());

    msg!("VULNERABLE INIT: Authority overwritten without check");
    Ok(())
}

// ============================================================================
// SECURE: Checks is_initialized before writing
// ============================================================================
// FIX: Check the is_initialized flag before writing. If already true, reject.
//
// This ensures initialization is a one-time operation.
// ============================================================================
fn init_secure(accounts: &[AccountInfo]) -> ProgramResult {
    let config = &accounts[0];
    let authority = &accounts[1];

    let mut data = config.try_borrow_mut_data()?;

    // SECURE: Check if already initialized
    let is_initialized = data[40] != 0;

    if is_initialized {
        msg!("ERROR: Config already initialized");
        return Err(ProgramError::Custom(ERR_ALREADY_INITIALIZED));
    }

    // Safe to initialize - first time only
    data[0..8].copy_from_slice(&[1, 2, 3, 4, 5, 6, 7, 8]);
    data[8..40].copy_from_slice(authority.key().as_ref());
    data[40] = 1; // is_initialized = true
    data[41..49].copy_from_slice(&0u64.to_le_bytes());

    msg!("SECURE INIT: Authority set (one-time only)");
    Ok(())
}
```

### patterns/05-pda-bump-canonicalization/pinocchio/src/lib.rs
```rust
//! # Pattern 5: PDA Bump Seed Canonicalization (Pinocchio)
//!
//! Demonstrates accepting non-canonical bumps, allowing duplicate PDAs.

#![no_std]

pinocchio::nostd_panic_handler!();

use pinocchio::{
    account_info::AccountInfo,
    entrypoint,
    msg,
    program_error::ProgramError,
    pubkey::{create_program_address, find_program_address, Pubkey},
    ProgramResult,
};

entrypoint!(process_instruction);

const IX_SET_VALUE_VULNERABLE: u8 = 0;
const IX_SET_VALUE_SECURE: u8 = 1;

const ERR_INVALID_BUMP: u32 = 5001;
const ERR_PDA_MISMATCH: u32 = 5002;

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;

    match *instruction {
        IX_SET_VALUE_VULNERABLE => set_value_vulnerable(program_id, accounts, instruction_data),
        IX_SET_VALUE_SECURE => set_value_secure(program_id, accounts, instruction_data),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

// ============================================================================
// VULNERABLE: Accepts user-supplied bump
// ============================================================================
// ISSUE: The program accepts `bump` as an instruction argument and uses it
//        directly. Multiple valid bumps can exist for the same seeds.
//
// ATTACK:
//   1. Legitimate user creates PDA with canonical bump (e.g., 253)
//   2. Attacker finds another valid bump (e.g., 251) for same seeds
//   3. Attacker creates account at non-canonical PDA
//   4. Program now has TWO accounts for same logical entity
//   5. Attacker manipulates the shadow account
//
// find_program_address returns the HIGHEST valid bump (canonical).
// create_program_address accepts ANY valid bump.
// ============================================================================
fn set_value_vulnerable(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let data_account = &accounts[0];
    let user = &accounts[1];

    // Parse bump from instruction data (byte 1)
    let bump = instruction_data[1];

    // Parse value from instruction data (bytes 2-9)
    let value = u64::from_le_bytes(
        instruction_data[2..10]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );

    // VULNERABLE: Uses caller-supplied bump without validation
    // Attacker can use any valid bump, not just the canonical one
    let seeds: &[&[u8]] = &[b"data", user.key().as_ref(), &[bump]];

    let expected_pda = create_program_address(seeds, program_id)
        .map_err(|_| ProgramError::Custom(ERR_INVALID_BUMP))?;

    if expected_pda != *data_account.key() {
        return Err(ProgramError::Custom(ERR_PDA_MISMATCH));
    }

    // Write data
    let mut data = data_account.try_borrow_mut_data()?;
    data[8..40].copy_from_slice(user.key().as_ref());
    data[40..48].copy_from_slice(&value.to_le_bytes());
    data[48] = bump; // Stores whatever bump was provided

    msg!("VULNERABLE: Value set at user-supplied bump");
    Ok(())
}

// ============================================================================
// SECURE: Derives canonical bump internally
// ============================================================================
// FIX: Use find_program_address to derive the canonical bump (highest valid).
// Reject any PDA that doesn't match the canonical derivation.
//
// This guarantees one PDA per seed set.
// ============================================================================
fn set_value_secure(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let data_account = &accounts[0];
    let user = &accounts[1];

    let value = u64::from_le_bytes(
        instruction_data[1..9]
            .try_into()
            .map_err(|_| ProgramError::InvalidInstructionData)?,
    );

    // SECURE: Derive canonical bump (highest valid bump)
    let seeds: &[&[u8]] = &[b"data", user.key().as_ref()];
    let (expected_pda, canonical_bump) = find_program_address(seeds, program_id);

    if expected_pda != *data_account.key() {
        msg!("ERROR: PDA does not match canonical derivation");
        return Err(ProgramError::Custom(ERR_PDA_MISMATCH));
    }

    // Write data with canonical bump
    let mut data = data_account.try_borrow_mut_data()?;
    data[8..40].copy_from_slice(user.key().as_ref());
    data[40..48].copy_from_slice(&value.to_le_bytes());
    data[48] = canonical_bump; // Always stores canonical bump

    msg!("SECURE: Value set at canonical bump only");
    Ok(())
}
```

### patterns/06-type-cosplay/pinocchio/src/lib.rs
```rust
//! # Pattern 6: Type Cosplay (Pinocchio)
//!
//! Demonstrates passing wrong account type with same binary layout.

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

const IX_UPDATE_FEE_VULNERABLE: u8 = 0;
const IX_UPDATE_FEE_SECURE: u8 = 1;

const ERR_UNAUTHORIZED: u32 = 6001;
const ERR_WRONG_DISCRIMINATOR: u32 = 6002;

// Discriminators (first 8 bytes) to distinguish account types
const ADMIN_CONFIG_DISCRIMINATOR: [u8; 8] = [0xAD, 0x11, 0x1C, 0x0F, 0x19, 0x00, 0x00, 0x01];
const USER_DATA_DISCRIMINATOR: [u8; 8] = [0x05, 0xE7, 0xDA, 0x7A, 0x00, 0x00, 0x00, 0x02];

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
        IX_UPDATE_FEE_VULNERABLE => update_fee_vulnerable(accounts, new_fee),
        IX_UPDATE_FEE_SECURE => update_fee_secure(accounts, new_fee),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

// ============================================================================
// VULNERABLE: Does NOT check account discriminator
// ============================================================================
// ISSUE: We read fields at fixed byte offsets without verifying the account
//        type via its discriminator. Two different types with same layout:
//
//   AdminConfig: [8-byte disc][admin: Pubkey][fee: u64]
//   UserData:    [8-byte disc][authority: Pubkey][balance: u64]
//
// Both have a Pubkey at offset 8. If we only read offset 8 without checking
// the discriminator, a UserData account looks like an AdminConfig.
//
// ATTACK:
//   1. Attacker creates UserData with authority = attacker's key
//   2. Passes UserData to update_fee_vulnerable (expects AdminConfig)
//   3. Program reads attacker's key at offset 8 as "admin"
//   4. Attacker passes admin check and modifies fees
// ============================================================================
fn update_fee_vulnerable(accounts: &[AccountInfo], new_fee: u64) -> ProgramResult {
    let config = &accounts[0];
    let authority = &accounts[1];

    let data = config.try_borrow_data()?;

    // VULNERABLE: Reading "admin" at offset 8 without checking discriminator!
    // This could be a UserData account where offset 8 is "authority", not "admin"
    let admin = read_pubkey(&data[8..40]);

    if admin != *authority.key() {
        return Err(ProgramError::Custom(ERR_UNAUTHORIZED));
    }

    if !authority.is_signer() {
        return Err(ProgramError::Custom(ERR_UNAUTHORIZED));
    }

    drop(data);

    // Write new fee at offset 40
    let mut data = config.try_borrow_mut_data()?;
    data[40..48].copy_from_slice(&new_fee.to_le_bytes());

    msg!("VULNERABLE: Fee updated without type check");
    Ok(())
}

// ============================================================================
// SECURE: Checks discriminator before trusting data
// ============================================================================
// FIX: Verify the 8-byte discriminator matches the expected account type.
// This is what Anchor's Account<T> does automatically.
//
// Different types have different discriminators:
//   AdminConfig: sha256("account:AdminConfig")[..8]
//   UserData: sha256("account:UserData")[..8]
// ============================================================================
fn update_fee_secure(accounts: &[AccountInfo], new_fee: u64) -> ProgramResult {
    let config = &accounts[0];
    let authority = &accounts[1];

    let data = config.try_borrow_data()?;

    // SECURE: Check discriminator FIRST
    let discriminator: [u8; 8] = data[0..8]
        .try_into()
        .map_err(|_| ProgramError::InvalidInstructionData)?;

    if discriminator != ADMIN_CONFIG_DISCRIMINATOR {
        msg!("ERROR: Wrong account type - expected AdminConfig");
        return Err(ProgramError::Custom(ERR_WRONG_DISCRIMINATOR));
    }

    // Now safe to read as AdminConfig
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

    msg!("SECURE: Fee updated with discriminator verification");
    Ok(())
}

#[inline]
fn read_pubkey(data: &[u8]) -> Pubkey {
    let mut bytes = [0u8; 32];
    bytes.copy_from_slice(&data[..32]);
    Pubkey::from(bytes)
}
```

## 09 Testes que usam Pinocchio?
```
patterns/01-missing-signer-check/pinocchio/Cargo.toml:2:name = "missing-signer-pinocchio"
patterns/01-missing-signer-check/pinocchio/Cargo.toml:10:pinocchio = "0.8"
patterns/02-missing-owner-check/pinocchio/Cargo.toml:2:name = "missing-owner-pinocchio"
patterns/02-missing-owner-check/pinocchio/Cargo.toml:10:pinocchio = "0.8"
patterns/03-integer-overflow/pinocchio/Cargo.toml:2:name = "integer-overflow-pinocchio"
patterns/03-integer-overflow/pinocchio/Cargo.toml:10:pinocchio = "0.8"
patterns/04-reinitialization-attack/pinocchio/Cargo.toml:2:name = "reinitialization-pinocchio"
patterns/04-reinitialization-attack/pinocchio/Cargo.toml:10:pinocchio = "0.8"
patterns/05-pda-bump-canonicalization/pinocchio/Cargo.toml:2:name = "pda-bump-pinocchio"
patterns/05-pda-bump-canonicalization/pinocchio/Cargo.toml:10:pinocchio = "0.8"
patterns/06-type-cosplay/pinocchio/Cargo.toml:2:name = "type-cosplay-pinocchio"
patterns/06-type-cosplay/pinocchio/Cargo.toml:10:pinocchio = "0.8"
```
