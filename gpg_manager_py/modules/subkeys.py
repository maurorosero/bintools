# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# subkeys.py - Description placeholder
# -----------------------------------------------------------------------------
#
# NOTE: This module is highly complex due to the limitations of non-interactively
# editing keys via GPG batch mode or python-gnupg's API.
# The implementation below uses direct GPG calls and might be fragile or incomplete.

import subprocess
from ..gpg_wrapper import GPGWrapper
from ..tui import ask_question, select_key_from_list, SpinnerContext
from ..utils import section_header, show_error, show_success, show_warning, confirm_continue, ask_confirmation, console

"""Handles managing GPG subkeys (EXPERIMENTAL)."""

def subkeys_menu(gpg: GPGWrapper):
    """Main menu for managing subkeys."""
    section_header("Manage Subkeys (Experimental)")
    show_warning("Subkey management often requires direct GPG interaction.")
    show_warning("python-gnupg API has limitations here. Using direct GPG calls.")

    secret_keys = gpg.list_keys(secret=True)
    if not secret_keys:
        show_warning("No private keys available to manage subkeys.")
        confirm_continue()
        return

    key_fpr = select_key_from_list(secret_keys, prompt="Select primary key to manage subkeys for:")
    if not key_fpr:
        return

    while True:
        # Refresh key details each time
        key_details = gpg.get_key(key_fpr) # Assuming get_key refetches
        if not key_details:
             show_error(f"Could not retrieve details for key {key_fpr}")
             break

        display_subkey_info(key_details)

        choices = [
            "Add Subkey",
            "Change Subkey Expiration",
            "Revoke Subkey",
            # "Delete Subkey" - Revocation is preferred
            "Back to Main Menu"
        ]
        action = ask_question("Select subkey action:", q_type='select', choices=choices)

        if action == "Add Subkey":
            add_subkey(gpg, key_fpr)
        elif action == "Change Subkey Expiration":
            change_subkey_expiration(gpg, key_fpr)
        elif action == "Revoke Subkey":
            revoke_subkey(gpg, key_fpr)
        elif action == "Back to Main Menu" or action is None:
            break
        else:
            break

def display_subkey_info(key_details):
    """Displays subkey information for a given key."""
    console.print(f"\n--- Subkeys for {key_details.get('keyid','N/A')[-8:]} ---")
    subkeys = key_details.get('subkeys', [])
    if not subkeys:
        console.print("  No subkeys found.")
        return

    for i, subkey_data in enumerate(subkeys):
        try:
            # Same parsing as in tui.py
            if isinstance(subkey_data[0], str) and subkey_data[0] in ['sub', 'ssb']:
                stype, skid, _, scrt_ts, sexp_ts, *srest = subkey_data
            else:
                stype = 'sub'
                skid, _, scrt_ts, sexp_ts, *srest = subkey_data

            skid_short = skid[-8:]
            sexpires = format_expiry(sexp_ts)
            # Try to get fingerprint if available
            sfpr = ""
            if srest and len(srest[0]) == 40:
                sfpr = f" (fpr: ...{srest[0][-16:]})"
            # Indicate index for selection
            console.print(f"  {i+1}) Type: {stype.upper()}, KeyID: {skid_short}, Expires: {sexpires}{sfpr}")
        except Exception:
             console.print(f"  {i+1}) (Error parsing subkey data: {subkey_data}) ")
    print("---------------------------")

def run_gpg_edit_key_command(gpg: GPGWrapper, key_fpr: str, commands: str):
    """Runs gpg --edit-key with provided batch commands."""
    show_info("Running GPG edit-key command (may require interaction/passphrase)...")
    command = [
        gpg.gpg_binary,
        '--status-fd=1',
        '--command-fd=0',
        '--yes', # Try to auto-confirm simple things
        f'--homedir={gpg.gpg_home}' if gpg.gpg_home else '',
        '--edit-key', key_fpr
    ]
    command = [c for c in command if c]

    try:
        # Using subprocess directly for better control over stdin/stdout/stderr
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=commands)

        if process.returncode == 0:
            show_success("GPG edit-key command finished successfully.")
            # print("GPG Output:\n", stdout) # Optional debug
            return True
        else:
            show_error(f"GPG edit-key command failed (Code: {process.returncode}).", details=stderr)
            return False
    except FileNotFoundError:
         show_error(f"GPG command not found: {gpg.gpg_binary}")
         return False
    except Exception as e:
        show_error(f"An error occurred running GPG edit-key: {e}")
        return False

def add_subkey(gpg: GPGWrapper, key_fpr: str):
    """Adds a new subkey (requires interaction)."""
    show_warning("Adding subkeys requires interactive GPG session.")
    show_info("This function will launch 'gpg --edit-key'. Follow the prompts there.")
    if not ask_confirmation("Launch interactive GPG session to add subkey?", default=True):
        return

    command = [gpg.gpg_binary, f'--homedir={gpg.gpg_home}' if gpg.gpg_home else '', '--edit-key', key_fpr]
    command = [c for c in command if c]

    try:
        # Run interactively
        console.print(f"\nRunning: {' '.join(command)}")
        console.print("Type 'addkey', follow prompts, then 'save' when done.")
        subprocess.run(command, check=False) # Let user interact
        show_success("Interactive GPG session finished.")
    except FileNotFoundError:
        show_error(f"GPG command not found: {gpg.gpg_binary}")
    except Exception as e:
        show_error(f"Failed to launch interactive GPG session: {e}")
    confirm_continue()

def select_subkey_index(gpg: GPGWrapper, key_fpr: str):
     """Asks the user to select a subkey by index."""
     key_details = gpg.get_key(key_fpr)
     if not key_details or not key_details.get('subkeys'):
         show_warning("No subkeys found for this key.")
         return None

     display_subkey_info(key_details) # Show indices
     num_subkeys = len(key_details['subkeys'])
     index_str = ask_question(f"Enter the number (1-{num_subkeys}) of the subkey to modify:")

     try:
         index = int(index_str)
         if 1 <= index <= num_subkeys:
             return index
         else:
             show_error("Invalid subkey number.")
             return None
     except (ValueError, TypeError):
         show_error("Invalid input. Please enter a number.")
         return None

def change_subkey_expiration(gpg: GPGWrapper, key_fpr: str):
    """Changes the expiration date of a subkey."""
    subkey_index = select_subkey_index(gpg, key_fpr)
    if subkey_index is None:
        return

    new_expiry = ask_expiry_date()
    if new_expiry is None or new_expiry == "CANCEL":
        return

    # GPG commands: key <index>, expire, <new_expiry>, y, save
    gpg_commands = f"key {subkey_index}\nexpire\n{new_expiry}\ny\nsave\n"

    run_gpg_edit_key_command(gpg, key_fpr, gpg_commands)
    confirm_continue()

def revoke_subkey(gpg: GPGWrapper, key_fpr: str):
    """Revokes an existing subkey."""
    subkey_index = select_subkey_index(gpg, key_fpr)
    if subkey_index is None:
        return

    if not ask_confirmation(f"Are you sure you want to revoke subkey {subkey_index}?", default=False):
        return

    # GPG commands: key <index>, revkey, <reason_code>, <reason_text>, y, save
    # TODO: Ask for reason code/text like in generate_revocation_cert
    reason_code = "3" # Default: Key is no longer used
    reason_text = "Subkey revoked via manager."

    gpg_commands = f"key {subkey_index}\nrevkey\n{reason_code}\n{reason_text}\ny\nsave\n"

    run_gpg_edit_key_command(gpg, key_fpr, gpg_commands)
    confirm_continue()
