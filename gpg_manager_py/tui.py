# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# tui.py - Description placeholder
# -----------------------------------------------------------------------------
#
import questionary
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED
from rich.text import Text
from rich.spinner import Spinner
import time

from .utils import (
    format_fingerprint, format_date, format_expiry,
    show_error, show_info, show_warning, section_header,
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR, COLOR_INFO, COLOR_DIM
)

"""Functions for Terminal User Interface using Rich and Questionary."""

console = Console()

def ask_question(message, q_type='text', choices=None, default=None, validate=None):
    """Asks a question using Questionary."""
    try:
        question_map = {
            'text': questionary.text(message, default=default or "", validate=validate),
            'password': questionary.password(message, validate=validate),
            'select': questionary.select(message, choices=choices or [], default=default),
            'checkbox': questionary.checkbox(message, choices=choices or []),
            'confirm': questionary.confirm(message, default=default if default is not None else True),
            'path': questionary.path(message, default=default or "", only_directories=False),
            'rawselect': questionary.rawselect(message, choices=choices or [], default=default),
        }
        if q_type not in question_map:
            raise ValueError(f"Unsupported question type: {q_type}")

        answer = question_map[q_type].ask()

        # Handle cancellation (returns None)
        if answer is None:
            show_warning("Operation cancelled by user.")
        return answer

    except (EOFError, KeyboardInterrupt):
        show_warning("Operation cancelled by user.")
        return None
    except Exception as e:
         show_error(f"An error occurred in the TUI prompt: {e}")
         return None

def select_key_from_list(keys, prompt="Select a GPG key:", include_cancel=True):
    """Prompts the user to select a key from a list of key dicts."""
    if not keys:
        show_warning("No keys available to select from.")
        return None

    choices = []
    key_map = {}
    for key in keys:
        key_id = key.get('keyid', 'N/A')
        key_id_short = key_id[-8:] if len(key_id) >= 8 else key_id
        uids = key.get('uids', ['No User ID'])
        uid_str = uids[0] if uids else 'No User ID'
        # Format: "UID <uid@example.com> (KeyID: ABCDEFGH)"
        choice_text = f"{uid_str} (KeyID: {key_id_short})"
        choices.append(choice_text)
        key_map[choice_text] = key.get('fingerprint', key_id) # Return fingerprint preferably

    if include_cancel:
        choices.append("Cancel")

    selected_choice = ask_question(prompt, q_type='select', choices=choices)

    if selected_choice == "Cancel" or selected_choice is None:
        return None

    return key_map.get(selected_choice)

def display_keys_elegant(keys_data):
    """
    Displays a list of GPG keys in an elegant table using Rich.
    (Adapted from previous example)
    Args:
        keys_data (list): List of key dictionaries from gpg.list_keys().
    """
    if not keys_data:
        console.print(f"[{COLOR_WARNING}]No GPG keys found.[/]")
        return

    table = Table(
        title="🔑 Available GPG Keys",
        box=ROUNDED,
        show_header=True,
        header_style=f"bold {COLOR_PRIMARY}",
        expand=True
    )

    table.add_column("Type", style=COLOR_DIM, width=7, justify="center") # Enough for pub/sec
    table.add_column("Key ID", style=f"bold magenta", min_width=10)
    table.add_column("Created", style=COLOR_SUCCESS, min_width=10)
    table.add_column("Expires", style=COLOR_WARNING, min_width=18) # Wider for expiry warning
    table.add_column("Fingerprint", style=COLOR_DIM, min_width=50)
    table.add_column("User ID(s)", style=COLOR_INFO, ratio=1)

    displayed_fprs = set()

    for key in keys_data:
        fpr = key.get('fingerprint')
        if not fpr or fpr in displayed_fprs:
            continue # Skip if no fingerprint or already displayed
        displayed_fprs.add(fpr)

        # --- Clave Principal ---
        key_type = key.get('type', '?')
        key_id_long = key.get('keyid', 'N/A')
        key_id_short = key_id_long[-8:] if len(key_id_long) >= 8 else key_id_long
        created = format_date(key.get('date'))
        expires = format_expiry(key.get('expires'))
        fingerprint_fmt = format_fingerprint(fpr)
        uids_list = key.get('uids', [])
        uids_text = "\n".join(uid for uid in uids_list if uid) if uids_list else Text("No User ID", style="italic dim")
        ownertrust = key.get('ownertrust', '-')

        # Indicate if secret key is available
        type_display = f"{key_type.upper()}"
        if key.get('secret'): # Check if the secret flag exists from list_keys(True)
             type_display += "/Sec"
        # Add trust level
        type_display += f" [{ownertrust}]"


        table.add_row(
            Text(type_display, justify="center"),
            key_id_short,
            created,
            expires,
            fingerprint_fmt,
            uids_text
        )

        # --- Subclaves --- (Using the subkeys structure from python-gnupg)
        subkeys_list = key.get('subkeys', []) # It's a list of lists/tuples
        for subkey_data in subkeys_list:
             # Format: [keyid, algo, date, expires, fingerprint]
             # Or sometimes includes type at the start: [type, keyid, algo, date, expires]
             if len(subkey_data) < 4: continue # Invalid subkey data

             try:
                # Heuristic to detect if type is included
                if isinstance(subkey_data[0], str) and subkey_data[0] in ['sub', 'ssb']:
                    subkey_type, subkey_id_long, _, subkey_created_ts, subkey_expires_ts, *rest = subkey_data
                else:
                    subkey_type = 'sub' # Assume sub if not specified
                    subkey_id_long, _, subkey_created_ts, subkey_expires_ts, *rest = subkey_data

                subkey_id_short = subkey_id_long[-8:] if len(subkey_id_long) >= 8 else subkey_id_long
                subkey_created = format_date(subkey_created_ts)
                subkey_expires = format_expiry(subkey_expires_ts)
                # Fingerprint might be in rest or not provided by default list_keys
                subkey_fingerprint = "" # Placeholder, need get_key details often
                if rest and len(rest[0]) == 40: # Basic check if fingerprint seems present
                     subkey_fingerprint = format_fingerprint(rest[0])

                subkey_type_display = Text(f"  └─{subkey_type.upper()}", style=COLOR_DIM)
                subkey_id_display = Text(subkey_id_short, style="magenta")

                table.add_row(
                    subkey_type_display,
                    subkey_id_display,
                    subkey_created,
                    subkey_expires,
                    subkey_fingerprint,
                    ""
                )
             except (ValueError, IndexError, TypeError) as e:
                 # Handle potential errors parsing subkey data format variations
                 show_warning(f"Could not parse subkey data: {subkey_data} - Error: {e}")


    console.print(table)

def display_key_details(key_data):
    """Displays detailed information about a single key."""
    if not key_data:
        show_warning("No key data to display.")
        return

    section_header(f"Key Details: {key_data.get('keyid', 'N/A')[-8:]}")
    table = Table(box=None, show_header=False, padding=(0, 1))
    table.add_column(style=f"bold {COLOR_PRIMARY}")
    table.add_column()

    table.add_row("Key ID:", key_data.get('keyid', 'N/A'))
    table.add_row("Fingerprint:", format_fingerprint(key_data.get('fingerprint', 'N/A')))
    table.add_row("Type:", key_data.get('type', 'N/A').upper())
    table.add_row("Algorithm:", key_data.get('algo', 'N/A')) # TODO: Map algo number to name
    table.add_row("Length:", str(key_data.get('length', 'N/A')))
    table.add_row("Created:", format_date(key_data.get('date', 'N/A')))
    table.add_row("Expires:", format_expiry(key_data.get('expires', None)))
    table.add_row("Ownertrust:", key_data.get('ownertrust', 'N/A')) # TODO: Map trust level

    # User IDs
    uids = key_data.get('uids', [])
    if uids:
        table.add_row("User IDs:", "")
        for i, uid in enumerate(uids):
             prefix = "  └─" if i > 0 else "  " # Indent subsequent UIDs
             table.add_row(prefix , uid)

    # Subkeys
    subkeys = key_data.get('subkeys', [])
    if subkeys:
        table.add_row("Subkeys:", "")
        for subkey_data in subkeys:
            try:
                 # Same parsing logic as display_keys_elegant
                 if isinstance(subkey_data[0], str) and subkey_data[0] in ['sub', 'ssb']:
                    subkey_type, subkey_id_long, _, subkey_created_ts, subkey_expires_ts, *rest = subkey_data
                 else:
                    subkey_type = 'sub'
                    subkey_id_long, _, subkey_created_ts, subkey_expires_ts, *rest = subkey_data

                 subkey_id_short = subkey_id_long[-8:] if len(subkey_id_long) >= 8 else subkey_id_long
                 subkey_expires = format_expiry(subkey_expires_ts)
                 subkey_info = f"{subkey_type.upper()} {subkey_id_short} (Expires: {subkey_expires})"
                 table.add_row("  └─", subkey_info)
            except Exception:
                 table.add_row("  └─", f"(Could not parse subkey: {subkey_data})")

    console.print(table)

class SpinnerContext:
    """Context manager for showing a Rich spinner during operations."""
    def __init__(self, title="Processing..."):
        self.title = title
        self.spinner = Spinner("dots", text=Text(title, style=COLOR_INFO))

    def __enter__(self):
        self.start_time = time.monotonic()
        # Start the spinner in a live context
        self.live = console.status(self.spinner)
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.live.stop()
        duration = time.monotonic() - self.start_time
        # Optionally display duration or success/failure based on exception
        # if exc_type:
        #     show_error(f"{self.title} failed after {duration:.2f}s")
        # else:
        #     show_success(f"{self.title} completed in {duration:.2f}s")

# --- Predefined Menus ---

def ask_key_type():
    """Asks the user to select a GPG key type."""
    # Based on GPG defaults and common recommendations
    choices = [
        questionary.Choice("RSA and RSA (default) - Signing & Encryption", value="RSA_RSA"),
        questionary.Choice("DSA and Elgamal - Signing & Encryption (Older)", value="DSA_ELG"),
        questionary.Choice("ECC (EdDSA - ed25519) - Signing Only", value="ECC_SIGN"),
        questionary.Choice("ECC (ECDSA/ECDH - cv25519) - Signing & Encryption", value="ECC_BOTH"),
        # questionary.Choice("RSA - Signing Only", value="RSA_SIGN"), # Less common for primary
        # questionary.Choice("RSA - Encryption Only", value="RSA_ENC"), # Less common for primary
        questionary.Choice("Cancel", value="CANCEL"),
    ]
    return ask_question("Select key type:", q_type='select', choices=choices)

def ask_key_length(key_type="RSA_RSA"):
    """Asks the user for key length based on type."""
    # Suggest appropriate lengths
    if "RSA" in key_type:
        choices = ["3072", "4096"] # 2048 is often considered minimum now
        default = "4096"
    elif key_type == "DSA_ELG":
        choices = ["2048", "3072"] # DSA has length limits
        default = "3072"
    elif "ECC" in key_type:
        # ECC lengths are determined by the curve, not user input usually
        return None # Or return the standard curve length if needed
    else:
        choices = ["2048", "3072", "4096"]
        default = "4096"

    return ask_question("Select key length (bits):", q_type='select', choices=choices, default=default)

def ask_expiry_date():
    """Asks for key expiration."""
    choices = [
        questionary.Choice("0 = Key does not expire", value="0"),
        questionary.Choice("1y = Expires in 1 year", value="1y"),
        questionary.Choice("2y = Expires in 2 years", value="2y"),
        questionary.Choice("Custom (e.g., 18m, 90d)", value="CUSTOM"),
        questionary.Choice("Cancel", value="CANCEL")
    ]
    choice = ask_question("Key expiration:", q_type='select', choices=choices, default="1y")

    if choice == "CUSTOM":
        return ask_question("Enter custom expiration (e.g., 18m, 90d, 2y):", q_type='text')
    elif choice == "CANCEL":
        return None
    return choice

def ask_user_info():
    """Asks for Real Name, Email, and optional Comment."""
    real_name = ask_question("Real name:", q_type='text', validate=lambda t: bool(t) or "Name cannot be empty")
    if real_name is None: return None, None, None

    email = ask_question("Email address:", q_type='text', validate=lambda t: "@" in t or "Invalid email format")
    if email is None: return None, None, None

    comment = ask_question("Comment (optional):", q_type='text')
    if comment is None and comment != "": return None, None, None # Distinguish cancel from empty

    return real_name, email, comment
