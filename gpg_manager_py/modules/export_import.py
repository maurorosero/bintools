# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# export_import.py - Description placeholder
# -----------------------------------------------------------------------------
#
import os
import datetime
import tempfile
from ..gpg_wrapper import GPGWrapper
from ..tui import ask_question, select_key_from_list, SpinnerContext
from ..utils import (
    section_header, show_error, show_success, show_warning, confirm_continue,
    ask_confirmation, ensure_directory_exists, console
)
from ..network import download_key_from_url

"""Handles exporting and importing GPG keys and related operations (excluding QR)."""

# --- Export Menu & Functions ---

def export_menu(gpg: GPGWrapper):
    """Handles the export key submenu."""
    section_header("Export Keys / Certificates")
    keys = gpg.list_keys(secret=False) # List public keys to select from
    if not keys:
        show_warning("No keys available to export.")
        confirm_continue()
        return

    key_fpr = select_key_from_list(keys, prompt="Select key to export/manage:")
    if not key_fpr:
        return

    key_id_short = key_fpr[-8:]

    export_choices = [
        "Export Public Key (.asc)",
        "Export Private Key (.asc) - BE CAREFUL!",
        # "Export QR Code" - Removed
        "Publish Public Key to Keyserver",
        "Generate Backup Revocation Certificate (.asc)",
        "Back"
    ]
    choice = ask_question("Select export/manage action:", q_type='select', choices=export_choices)

    if choice == "Export Public Key (.asc)":
        export_public_key(gpg, key_fpr)
    elif choice == "Export Private Key (.asc) - BE CAREFUL!":
        export_private_key(gpg, key_fpr)
    elif choice == "Publish Public Key to Keyserver":
        publish_to_keyserver(gpg, key_fpr)
    elif choice == "Generate Backup Revocation Certificate (.asc)":
        generate_backup_revocation_cert(gpg, key_fpr)
    elif choice == "Back" or choice is None:
        return

def export_public_key(gpg: GPGWrapper, key_fpr: str):
    """Exports the public key to an .asc file."""
    key_id_short = key_fpr[-8:]
    default_filename = f"publickey_{key_id_short}.asc"
    output_path = ask_question("Enter filename for public key export:", default=default_filename)
    if not output_path:
        return

    with SpinnerContext(f"Exporting public key {key_id_short}..."):
        success = gpg.export_keys(keyids=[key_fpr], secret=False, armor=True, output_path=output_path)

    if success:
        show_success(f"Public key exported successfully to: {output_path}")
    else:
        show_error("Public key export failed.") # gpg_wrapper shows details
    confirm_continue()

def export_private_key(gpg: GPGWrapper, key_fpr: str):
    """Exports the private key to an encrypted .asc file."""
    key_id_short = key_fpr[-8:]
    default_filename = f"privatekey_{key_id_short}.asc"

    show_warning("Exporting your private key can be a security risk if not handled properly.")
    show_warning("Ensure the exported file is stored securely and encrypted.")
    if not ask_confirmation("Are you sure you want to export the private key?", default=False):
        return

    output_path = ask_question("Enter filename for private key export:", default=default_filename)
    if not output_path:
        return

    # GPG will likely prompt for a passphrase via pinentry to protect the export
    with SpinnerContext(f"Exporting private key {key_id_short}... (Passphrase likely required)"):
        success = gpg.export_keys(keyids=[key_fpr], secret=True, armor=True, output_path=output_path)

    if success:
        show_success(f"Private key exported successfully to: {output_path}")
        show_info("Remember to protect this file securely!")
    else:
        show_error("Private key export failed.") # gpg_wrapper shows details
    confirm_continue()

def publish_to_keyserver(gpg: GPGWrapper, key_fpr: str):
    """Publishes the public key to a keyserver."""
    keyserver = ask_question("Enter keyserver address:", default="keys.openpgp.org")
    if not keyserver:
        return

    show_info(f"Attempting to publish key {key_fpr[-8:]} to {keyserver}...")
    if not ask_confirmation(f"Publish key {key_fpr[-8:]} to {keyserver}?", default=True):
        return

    with SpinnerContext(f"Publishing key to {keyserver}..."):
        success = gpg.send_keys(keyserver, [key_fpr])

    # Success/error messages handled by gpg_wrapper
    confirm_continue()

def generate_backup_revocation_cert(gpg: GPGWrapper, key_fpr: str):
    """Generates a revocation certificate for backup purposes."""
    key_id_short = key_fpr[-8:]
    section_header("Generate Backup Revocation Certificate")
    console.print("A revocation certificate allows you to revoke your key if the private key is lost or compromised.")
    show_warning("Store this certificate securely and separately from your private key!")

    # Create secure directory
    secure_dir = os.path.expanduser("~/secure/gpg/revocations")
    if not ensure_directory_exists(secure_dir):
        show_error("Could not create secure directory for revocation certificate.")
        confirm_continue()
        return

    date_stamp = datetime.datetime.now().strftime("%Y%m%d")
    default_path = os.path.join(secure_dir, f"backup_revoke_{key_id_short}_{date_stamp}.asc")

    output_path = ask_question("Enter path to save revocation certificate:", default=default_path)
    if not output_path:
        return

    # Create directory if it doesn't exist
    cert_dir = os.path.dirname(output_path)
    if not ensure_directory_exists(cert_dir):
         show_error(f"Could not create directory: {cert_dir}")
         confirm_continue()
         return

    # Select revocation reason
    reason_choices = {
        "1: Key has been compromised": "1",
        "2: Key is superseded": "2",
        "3: Key is no longer used": "3",
        "0: No reason specified (default)": "0",
        "Custom Reason": "custom"
    }
    reason_desc = ask_question("Select revocation reason:", q_type='select', choices=list(reason_choices.keys()))
    if not reason_desc:
        return

    reason_code = reason_choices[reason_desc]
    reason_string = ""
    if reason_code == "custom":
        reason_code = "0" # GPG code for custom is 0
        reason_string = ask_question("Enter custom reason text:")
        if reason_string is None: return # Handle cancel

    show_info("Generating revocation certificate... (May require passphrase)")
    with SpinnerContext("Generating certificate..."):
        success = gpg.generate_revocation_certificate(
            key_fpr,
            reason_code=reason_code,
            reason_string=reason_string,
            output_path=output_path
        )

    # Success/error messages handled by gpg_wrapper
    if success:
        show_info(f"Permissions set to 600 on {output_path} (if possible).")
        show_warning("IMPORTANT: Store this file safely and securely!")

    confirm_continue()

# --- Import Menu & Functions ---

def import_menu(gpg: GPGWrapper):
    """Handles the import key submenu."""
    while True:
        section_header("Import GPG Keys")
        import_choices = [
            "Import from File (.asc, .gpg)",
            "Import from Keyserver",
            "Import from URL",
            "Import from Pasted Text",
            "Import Revocation Certificate",
            "Back to Main Menu"
        ]
        choice = ask_question("Select import source:", q_type='select', choices=import_choices)

        if choice == "Import from File (.asc, .gpg)":
            import_from_file(gpg)
        elif choice == "Import from Keyserver":
            import_from_keyserver(gpg)
        elif choice == "Import from URL":
            import_from_url(gpg)
        elif choice == "Import from Pasted Text":
            import_from_text(gpg)
        elif choice == "Import Revocation Certificate":
             import_revocation_cert(gpg)
        elif choice == "Back to Main Menu" or choice is None:
            break

def import_from_file(gpg: GPGWrapper):
    """Imports a key from a local file."""
    file_path = ask_question("Enter path to key file:", q_type='path')
    if not file_path:
        return
    if not os.path.exists(file_path):
        show_error(f"File not found: {file_path}")
        confirm_continue()
        return

    with SpinnerContext(f"Importing key from {os.path.basename(file_path)}..."):
        result = gpg.import_keys(filepath=file_path)

    # Result summary handled by gpg_wrapper
    if result and result.imported > 0:
        ask_sign_imported_keys(gpg, result.fingerprints)

    confirm_continue()

def import_from_keyserver(gpg: GPGWrapper):
    """Imports a key from a keyserver."""
    keyserver = ask_question("Enter keyserver address:", default="keys.openpgp.org")
    if not keyserver:
        return

    search_term = ask_question("Enter email, key ID, fingerprint, or name to search:")
    if not search_term:
        return

    # Search first
    with SpinnerContext(f"Searching for '{search_term}' on {keyserver}..."):
         search_output = gpg.search_keys(keyserver, search_term)

    if not search_output:
         # Error or no keys found handled by wrapper
         confirm_continue()
         return

    # Display raw search results
    console.print("--- Search Results ---")
    console.print(search_output)
    console.print("----------------------")

    key_id_to_import = ask_question("Enter the Key ID or Fingerprint to import (or leave blank to cancel):")
    if not key_id_to_import:
        return

    # Import the selected key
    with SpinnerContext(f"Importing key {key_id_to_import} from {keyserver}..."):
        result = gpg.receive_keys(keyserver, [key_id_to_import])

    # Result summary handled by gpg_wrapper
    if result and result.imported > 0:
        ask_sign_imported_keys(gpg, result.fingerprints)

    confirm_continue()

def import_from_url(gpg: GPGWrapper):
    """Imports a key by downloading it from a URL."""
    url = ask_question("Enter URL of the key file:")
    if not url:
        return

    key_data = download_key_from_url(url) # Uses requests

    if key_data:
        with SpinnerContext("Importing downloaded key..."):
            result = gpg.import_keys(key_data=key_data)

        if result and result.imported > 0:
            ask_sign_imported_keys(gpg, result.fingerprints)
    else:
         show_error("Could not retrieve or validate key data from URL.")

    confirm_continue()

def import_from_text(gpg: GPGWrapper):
    """Imports a key from text pasted by the user."""
    console.print("Paste the PGP key block below. Press Ctrl-D (Unix) or Ctrl-Z+Enter (Windows) when done:")
    pasted_lines = []
    try:
        while True:
            line = input()
            pasted_lines.append(line)
    except EOFError:
        pass # Expected way to end input
    except KeyboardInterrupt:
         show_warning("Input cancelled.")
         confirm_continue()
         return

    key_data = "\n".join(pasted_lines)

    if not key_data or "BEGIN PGP" not in key_data:
        show_error("No valid key data pasted.")
        confirm_continue()
        return

    with SpinnerContext("Importing pasted key..."):
        result = gpg.import_keys(key_data=key_data)

    if result and result.imported > 0:
        ask_sign_imported_keys(gpg, result.fingerprints)

    confirm_continue()

def import_revocation_cert(gpg: GPGWrapper):
    """Imports a revocation certificate from a file."""
    section_header("Import Revocation Certificate")
    console.print("Importing a revocation certificate will mark the corresponding key as revoked in your keyring.")
    show_warning("This action cannot be easily undone!")

    file_path = ask_question("Enter path to revocation certificate file (.asc):", q_type='path')
    if not file_path:
        return
    if not os.path.exists(file_path):
        show_error(f"File not found: {file_path}")
        confirm_continue()
        return

    # Basic validation
    try:
        with open(file_path, 'r') as f:
            content = f.read(500) # Read start of file
            if "BEGIN PGP" not in content or "REVOCATION" not in content.upper():
                show_error("File does not appear to be a valid revocation certificate.")
                confirm_continue()
                return
    except Exception as e:
        show_error(f"Could not read file: {e}")
        confirm_continue()
        return

    if not ask_confirmation("Are you sure you want to import this revocation certificate?", default=False):
        return

    with SpinnerContext(f"Importing revocation certificate from {os.path.basename(file_path)}..."):
        result = gpg.import_keys(filepath=file_path)

    # Check results (look for key marked revoked)
    if result and result.results:
         revoked_fpr = None
         for res_detail in result.results:
              # Check for indications of revocation import
              # This parsing is fragile, depends on GPG output
              if res_detail.get('revoked') == '1' or "revoked" in res_detail.get('text','').lower():
                  revoked_fpr = res_detail.get('fingerprint')
                  show_success(f"Revocation certificate imported successfully for key {revoked_fpr}")
                  break
         if revoked_fpr:
             # Ask to publish the revoked key
             if ask_confirmation("Do you want to publish this revocation to a keyserver?", default=True):
                 publish_to_keyserver(gpg, revoked_fpr)
         else:
              show_warning("Revocation certificate processed, but could not confirm which key was revoked from output.")
    elif result:
         show_warning("Revocation import status unclear from GPG output.")
    # Error handled by wrapper

    confirm_continue()


# --- Helper for Signing Imported Keys ---

def ask_sign_imported_keys(gpg: GPGWrapper, imported_fingerprints: list):
    """Asks the user if they want to sign newly imported keys."""
    if not imported_fingerprints:
        return

    keys_to_sign = []
    for fpr in imported_fingerprints:
        key_info = gpg.get_key(fpr)
        if key_info:
             keys_to_sign.append(key_info)

    if not keys_to_sign:
         return

    console.print("\nThe following key(s) were imported:")
    for key in keys_to_sign:
         uids = key.get('uids', ['Unknown UID'])
         console.print(f"  - {uids[0]} ({key.get('fingerprint', 'N/A')[-16:]})")

    if not ask_confirmation("Do you want to sign any of these keys to certify them? (Requires your private key)", default=True):
        return

    # Select signing key
    secret_keys = gpg.list_keys(secret=True)
    if not secret_keys:
        show_error("You don't have any private keys available to sign with.")
        return

    signing_key_fpr = select_key_from_list(secret_keys, prompt="Select YOUR key to sign with:")
    if not signing_key_fpr:
        return

    # Choose trust level
    trust_choices = {
        "0: I don't know or won't say": "0",
        "1: I do not trust": "1",
        "2: I trust marginally": "2",
        "3: I trust fully": "3"
        # 4: I trust ultimately (only for your own key)
    }
    trust_desc = ask_question("How much do you trust the key owner's identity verification?",
                              q_type='select', choices=list(trust_choices.keys()), default="2: I trust marginally")
    if not trust_desc:
        return
    trust_level = trust_choices[trust_desc]

    # Sign each selected imported key
    for key_to_sign in keys_to_sign:
        target_fpr = key_to_sign.get('fingerprint')
        if not target_fpr:
             continue
        uid_str = key_to_sign.get('uids', ['Unknown UID'])[0]
        if ask_confirmation(f"Sign key {uid_str} ({target_fpr[-8:]}) with your key {signing_key_fpr[-8:]}?", default=True):
            with SpinnerContext(f"Signing key {target_fpr[-8:]}... (Passphrase likely required)"):
                 gpg.sign_key(target_fpr, signing_key_fpr, trust_level)
            # Success/error handled by wrapper