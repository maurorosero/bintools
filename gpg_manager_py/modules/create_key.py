# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# create_key.py - Description placeholder
# -----------------------------------------------------------------------------
#
from ..gpg_wrapper import GPGWrapper
from ..tui import ask_key_type, ask_key_length, ask_expiry_date, ask_user_info, ask_question, SpinnerContext
from ..utils import section_header, show_error, show_success, show_warning, confirm_continue, ask_confirmation

"""Handles the creation of new GPG keys."""

def create_key_menu(gpg: GPGWrapper):
    """Guides the user through the key creation process."""
    section_header("Create New GPG Key")

    key_type_choice = ask_key_type()
    if key_type_choice is None or key_type_choice == "CANCEL":
        return

    key_length = ask_key_length(key_type_choice)
    # If key_length is None (e.g., for ECC), we might need a specific curve name later
    if key_length is None and "ECC" not in key_type_choice:
         show_warning("Key length selection cancelled or not applicable.")
         return # Or handle ECC case specifically

    expiry = ask_expiry_date()
    if expiry is None or expiry == "CANCEL":
        return

    real_name, email, comment = ask_user_info()
    if real_name is None or email is None: # Comment can be empty, check name/email
        return

    # Construct the User ID string
    uid = f"{real_name}"
    if comment:
        uid += f" ({comment})"
    uid += f" <{email}>"

    # Prepare GPG batch input
    # Reference: https://www.gnupg.org/documentation/manuals/gnupg/Unattended-GPG-key-generation.html
    batch_input_lines = [
        "%echo Generating a new key...",
        "Key-Type: RSA", # Default, will adjust based on choice
        # "Key-Curve: Ed25519", # Example for ECC
        f"Key-Length: {key_length}" if key_length else "",
        f"Subkey-Type: RSA", # Default, will adjust
        # "Subkey-Curve: Curve25519", # Example for ECC
        f"Subkey-Length: {key_length}" if key_length else "",
        f"Name-Real: {real_name}",
        f"Name-Comment: {comment}" if comment else "",
        f"Name-Email: {email}",
        f"Expire-Date: {expiry}",
        "%no-protection", # Assuming password protection is handled by pinentry/agent
        # "%ask-passphrase", # Alternative to use callback
        "%commit",
        "%echo Key generation complete!"
    ]

    # --- Adjust based on key_type_choice --- #
    if key_type_choice == "RSA_RSA":
        # Defaults are likely RSA/RSA, but explicitly set
        batch_input_lines[2] = "Key-Type: RSA"
        batch_input_lines[5] = "Subkey-Type: RSA"
    elif key_type_choice == "DSA_ELG":
        batch_input_lines[2] = "Key-Type: DSA"
        batch_input_lines[5] = "Subkey-Type: ELG-E"
        # DSA length is usually fixed or limited, ensure key_length is appropriate
        if key_length not in ["2048", "3072"]:
             show_warning(f"Adjusting key length to 3072 for DSA/Elgamal (was {key_length})")
             key_length = "3072"
             batch_input_lines[3] = f"Key-Length: {key_length}"
             batch_input_lines[6] = f"Subkey-Length: {key_length}" # Elgamal can use same
    elif key_type_choice == "ECC_SIGN":
        batch_input_lines[2] = "Key-Type: EDDSA"
        batch_input_lines[3] = "Key-Curve: ed25519" # Curve implies length
        batch_input_lines[4] = "" # No default subkey needed? GPG might add one anyway.
        batch_input_lines[5] = "" # Or specify ECDH for encryption subkey?
        batch_input_lines[6] = "" # Let GPG decide subkey curve/length
    elif key_type_choice == "ECC_BOTH":
        batch_input_lines[2] = "Key-Type: ECDSA" # Signing primary key
        batch_input_lines[3] = "Key-Curve: nistp256" # Default curve for ECDSA often
        # batch_input_lines[3] = "Key-Curve: cv25519" # If using Curve25519 for signing too
        batch_input_lines[5] = "Subkey-Type: ECDH" # Encryption subkey
        batch_input_lines[6] = "Subkey-Curve: cv25519" # Curve25519 is common for ECDH
        # Remove length lines as curves define them
        batch_input_lines[4] = "" # Key-Length removed
        batch_input_lines[7] = "" # Subkey-Length removed

    # Filter out empty lines
    batch_input = "\n".join(line for line in batch_input_lines if line)

    # --- Confirmation --- #
    print("\n--- Key Parameters ---")
    print(f"  Type: {key_type_choice}")
    if key_length:
        print(f"  Length: {key_length} bits")
    # TODO: Show curve for ECC
    print(f"  Expires: {expiry if expiry != '0' else 'Never'}")
    print(f"  User ID: {uid}")
    print("----------------------")

    if not ask_confirmation("Proceed with key generation?", default=True):
        return

    # --- Generate Key --- #
    try:
        with SpinnerContext("Generating key pair... This may take a while."):
            result = gpg.generate_key(batch_input)

        if result and result.fingerprint:
            # Optionally show full result details
            # print(result)
            show_success("Key pair generated successfully!")
            confirm_continue()
        else:
            # Error already shown by gpg_wrapper usually
            confirm_continue()

    except Exception as e:
        show_error(f"An unexpected error occurred during key generation: {e}")
        confirm_continue() 