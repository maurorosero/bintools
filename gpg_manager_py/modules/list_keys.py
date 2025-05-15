# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# list_keys.py - Description placeholder
# -----------------------------------------------------------------------------
#
from ..gpg_wrapper import GPGWrapper
from ..tui import display_keys_elegant, ask_question, select_key_from_list, display_key_details
from ..utils import section_header, show_warning, confirm_continue

"""Handles listing and viewing GPG keys."""

def list_keys_menu(gpg: GPGWrapper):
    """Displays the list/view keys menu."""
    while True:
        section_header("List/View Keys")
        keys_public = gpg.list_keys(secret=False)
        keys_secret = gpg.list_keys(secret=True)

        # Combine public and secret keys, marking secret ones
        combined_keys = []
        secret_fingerprints = {key['fingerprint'] for key in keys_secret if 'fingerprint' in key}
        processed_fingerprints = set()

        for key in keys_public:
            fpr = key.get('fingerprint')
            if not fpr or fpr in processed_fingerprints:
                continue
            key['secret'] = fpr in secret_fingerprints
            combined_keys.append(key)
            processed_fingerprints.add(fpr)

        # Add any secret keys not found in public list (should be rare)
        for key in keys_secret:
            fpr = key.get('fingerprint')
            if fpr and fpr not in processed_fingerprints:
                 key['secret'] = True
                 combined_keys.append(key)
                 processed_fingerprints.add(fpr)

        if not combined_keys:
            show_warning("No GPG keys found in your keyring.")
            confirm_continue()
            return

        display_keys_elegant(combined_keys)

        choices = [
            "View Details of a Key",
            "Refresh List",
            "Back to Main Menu"
        ]
        action = ask_question("Select an action:", q_type='select', choices=choices)

        if action == "View Details of a Key":
            view_key_details(gpg, combined_keys)
        elif action == "Refresh List":
            continue
        elif action == "Back to Main Menu" or action is None:
            break
        else:
             break # Should not happen

def view_key_details(gpg: GPGWrapper, keys: list):
     """Allows selecting a key and viewing its details."""
     selected_fpr = select_key_from_list(keys, prompt="Select key to view details:")
     if not selected_fpr:
         return

     # Find the full key data again (list_keys might not have everything)
     # Alternatively, pass the selected key dict if it's detailed enough
     # For simplicity, let's just display what we have from the list
     key_details = None
     for key in keys:
          if key.get('fingerprint') == selected_fpr:
              key_details = key
              break

     if key_details:
        display_key_details(key_details)
        # TODO: Add option here to perform actions on the selected key?
        # e.g., export, delete, manage subkeys/uids? This might fit better here.
     else:
         show_warning(f"Could not find details for fingerprint {selected_fpr}")

     confirm_continue() 