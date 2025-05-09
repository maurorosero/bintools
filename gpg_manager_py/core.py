# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# core.py - Description placeholder
# -----------------------------------------------------------------------------
#
import sys
from rich.panel import Panel
from rich.text import Text

from .gpg_wrapper import GPGWrapper
from .tui import ask_question, SpinnerContext
from .utils import (
    section_header, show_error, show_success, show_warning,
    confirm_continue, ask_confirmation, console, COLOR_PRIMARY,
    COLOR_SUCCESS
)

# Import module functions
from .modules import list_keys, create_key, export_import, subkeys, identities, git_config

"""Core application logic and main menu for GPG Manager."""

# --- Application Info --- #
APP_NAME = "GPG Manager Py"
APP_VERSION = "0.1.0 (Python Refactor)"
APP_AUTHOR = "Mauro Rosero Pérez (Original Bash Script Author)"

def display_welcome():
    """Displays the application header."""
    header = Panel(
        Text(f"{APP_NAME} v{APP_VERSION}\nby {APP_AUTHOR}", justify="center"),
        title="Welcome",
        border_style=COLOR_PRIMARY,
        expand=False
    )
    console.print(header)

def delete_key(gpg: GPGWrapper):
    """Handles deleting a key (public and/or secret)."""
    section_header("Delete Key")
    show_warning("Deleting keys is irreversible!")

    # Select key to delete (show both public and secret)
    pub_keys = gpg.list_keys(secret=False)
    sec_keys = gpg.list_keys(secret=True)
    all_keys_dict = {k['fingerprint']: k for k in pub_keys if 'fingerprint' in k}
    for sk in sec_keys:
        fpr = sk.get('fingerprint')
        if fpr:
             all_keys_dict[fpr] = sk # Overwrite with secret key info if exists

    all_keys = list(all_keys_dict.values())

    if not all_keys:
        show_warning("No keys available to delete.")
        confirm_continue()
        return

    key_fpr = select_key_from_list(all_keys, prompt="Select key to DELETE:")
    if not key_fpr:
        return

    key_id_short = key_fpr[-8:]
    key_info = all_keys_dict.get(key_fpr)
    uid_str = key_info.get('uids', ['Unknown UID'])[0] if key_info else 'Unknown Key'

    # Determine if we have the secret key
    has_secret = any(sk.get('fingerprint') == key_fpr for sk in sec_keys)

    console.print(f"You selected to delete: [bold red]{uid_str} ({key_id_short})[/]")

    delete_secret = False
    if has_secret:
        if ask_confirmation(f"DELETE SECRET key {key_id_short}? (Irreversible!) This will also delete the public key.", default=False):
             delete_secret = True
        elif ask_confirmation(f"DELETE ONLY PUBLIC key {key_id_short}?", default=False):
             delete_secret = False
        else:
             show_info("Deletion cancelled.")
             return
    else:
        # Only public key exists
        if not ask_confirmation(f"DELETE PUBLIC key {key_id_short}? (Irreversible!) Did you intend to delete a secret key?", default=False):
            show_info("Deletion cancelled.")
            return
        delete_secret = False

    # Perform deletion
    action = "secret and public key" if delete_secret else "public key"
    with SpinnerContext(f"Attempting to delete {action} {key_id_short}... (Confirmation likely required)"):
        # python-gnupg delete_keys deletes BOTH if the fingerprint matches a secret key
        # To delete only public, we pass secret=False. To delete secret (and thus public), we pass secret=True.
        results = gpg.delete_keys([key_fpr], secret=delete_secret)

    # Results summary handled by gpg_wrapper
    confirm_continue()

def main_menu(gpg: GPGWrapper):
    """Displays the main application menu and handles user selection."""
    while True:
        console.clear() # Clear screen for main menu
        display_welcome()
        print()

        # Define menu options
        menu_options = {
            "Create New GPG Key": create_key.create_key_menu,
            "List/View Keys": list_keys.list_keys_menu,
            "Manage Subkeys (Experimental)": subkeys.subkeys_menu,
            "Manage Identities (Experimental)": identities.identities_menu,
            "Export Keys / Certificates": export_import.export_menu,
            "Import Keys / Certificates": export_import.import_menu,
            # "Revoke Key" - Merged into Export (Generate Revoke Cert) & Import (Import Revoke Cert)
            "Delete Key": delete_key, # Add dedicated delete option
            "Git Integration": git_config.git_integration_menu,
            # "Select Language" - Removed for now
            "Exit": None # Special case for exit
        }

        # Use ask_question for menu selection
        choice = ask_question(
            "Select an action:",
            q_type='select',
            choices=list(menu_options.keys())
        )

        if choice == "Exit" or choice is None:
            console.print(Panel(f"[bold {COLOR_SUCCESS}]Thank you for using {APP_NAME}! Goodbye.[/]", expand=False))
            sys.exit(0)

        # Get the function associated with the choice
        selected_function = menu_options.get(choice)

        if selected_function:
            try:
                # Call the function, passing the gpg handler
                selected_function(gpg)
            except Exception as e:
                 # Catch unexpected errors in module functions
                 show_error(f"An unexpected error occurred in the selected module ({choice}): {e}")
                 import traceback
                 console.print_exception(show_locals=False) # Print traceback for debugging
                 confirm_continue("Press Enter to return to the main menu...")
        else:
            show_warning(f"Invalid choice or function not implemented: {choice}")
            confirm_continue()
