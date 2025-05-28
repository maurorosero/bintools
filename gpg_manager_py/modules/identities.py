# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# identities.py - Description placeholder
# -----------------------------------------------------------------------------
#
# NOTE: Similar limitations to subkeys.py apply here.

import subprocess
from ..gpg_wrapper import GPGWrapper
from ..tui import ask_question, select_key_from_list, SpinnerContext, ask_user_info
from ..utils import section_header, show_error, show_success, show_warning, confirm_continue, ask_confirmation, console
from .subkeys import run_gpg_edit_key_command # Reuse the edit command runner

"""Handles managing GPG User IDs (identities) (EXPERIMENTAL)."""

def identities_menu(gpg: GPGWrapper):
    """Main menu for managing identities (User IDs)."""
    section_header("Manage Identities (User IDs - Experimental)")
    show_warning("Identity management often requires direct GPG interaction.")

    secret_keys = gpg.list_keys(secret=True)
    if not secret_keys:
        show_warning("No private keys available to manage identities.")
        confirm_continue()
        return

    key_fpr = select_key_from_list(secret_keys, prompt="Select primary key to manage identities for:")
    if not key_fpr:
        return

    while True:
        key_details = gpg.get_key(key_fpr)
        if not key_details:
            show_error(f"Could not retrieve details for key {key_fpr}")
            break

        display_identity_info(key_details)

        choices = [
            "Add User ID",
            "Set Primary User ID",
            "Revoke User ID",
            "Back to Main Menu"
        ]
        action = ask_question("Select identity action:", q_type='select', choices=choices)

        if action == "Add User ID":
            add_identity(gpg, key_fpr)
        elif action == "Set Primary User ID":
            set_primary_identity(gpg, key_fpr)
        elif action == "Revoke User ID":
            revoke_identity(gpg, key_fpr)
        elif action == "Back to Main Menu" or action is None:
            break
        else:
            break

def display_identity_info(key_details):
    """Displays User ID information for a given key."""
    console.print(f"\n--- Identities for {key_details.get('keyid','N/A')[-8:]} ---")
    uids = key_details.get('uids', [])
    if not uids:
        console.print("  No User IDs found.")
        return

    # Check for primary UID marker (might need gpg --list-keys --with-colons)
    # Simple display for now:
    for i, uid_str in enumerate(uids):
        # TODO: Indicate primary UID (often marked with '*' or similar in gpg output)
        primary_marker = "" # Placeholder
        console.print(f"  {i+1}) {uid_str}{primary_marker}")
    print("-------------------------------")

def select_identity_index(gpg: GPGWrapper, key_fpr: str):
     """Asks the user to select a User ID by index."""
     key_details = gpg.get_key(key_fpr)
     if not key_details or not key_details.get('uids'):
         show_warning("No User IDs found for this key.")
         return None

     display_identity_info(key_details) # Show indices
     num_uids = len(key_details['uids'])
     index_str = ask_question(f"Enter the number (1-{num_uids}) of the User ID to modify:")

     try:
         index = int(index_str)
         if 1 <= index <= num_uids:
             return index
         else:
             show_error("Invalid User ID number.")
             return None
     except (ValueError, TypeError):
         show_error("Invalid input. Please enter a number.")
         return None

def add_identity(gpg: GPGWrapper, key_fpr: str):
    """Adds a new User ID to the key."""
    show_info("Adding a new User ID (identity). Provide the details below.")
    real_name, email, comment = ask_user_info()
    if real_name is None or email is None:
        return

    # Construct the new User ID string for confirmation
    new_uid_str = f"{real_name}"
    if comment:
        new_uid_str += f" ({comment})"
    new_uid_str += f" <{email}>"

    if not ask_confirmation(f"Add this User ID: \"{new_uid_str}\"?", default=True):
        return

    # GPG commands: adduid, <real_name>, <email>, <comment>, O(kay), save
    # Note: GPG prompts are specific here
    gpg_commands = (
        f"adduid\n"
        f"{real_name}\n"
        f"{email}\n"
        f"{comment if comment else ''}\n" # Need newline even if empty
        f"O\n" # Okay
        f"save\n"
    )

    run_gpg_edit_key_command(gpg, key_fpr, gpg_commands)
    confirm_continue()

def set_primary_identity(gpg: GPGWrapper, key_fpr: str):
    """Sets the primary User ID."""
    uid_index = select_identity_index(gpg, key_fpr)
    if uid_index is None:
        return

    # GPG commands: uid <index>, primary, save
    gpg_commands = f"uid {uid_index}\nprimary\nsave\n"

    run_gpg_edit_key_command(gpg, key_fpr, gpg_commands)
    confirm_continue()

def revoke_identity(gpg: GPGWrapper, key_fpr: str):
    """Revokes an existing User ID."""
    uid_index = select_identity_index(gpg, key_fpr)
    if uid_index is None:
        return

    # Get the UID string for confirmation
    key_details = gpg.get_key(key_fpr)
    uid_to_revoke = "Unknown UID"
    if key_details and key_details.get('uids') and len(key_details['uids']) >= uid_index:
        uid_to_revoke = key_details['uids'][uid_index - 1]

    if not ask_confirmation(f"Are you sure you want to revoke User ID {uid_index}: \"{uid_to_revoke}\"?", default=False):
        return

    # GPG commands: uid <index>, revuid, y, save
    gpg_commands = f"uid {uid_index}\nrevuid\ny\nsave\n"

    run_gpg_edit_key_command(gpg, key_fpr, gpg_commands)
    confirm_continue()
