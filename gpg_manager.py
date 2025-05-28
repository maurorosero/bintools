#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Textual GPG Manager - Interactive GPG Key Management Tool.

Copyright (C) 2025 MAURO ROSERO PÉREZ
License: GPLV3

File: gpg_manager.py
Version: 0.1.0
Author: Mauro Rosero P. <mauro.rosero@gmail.com>
Assistant: Cursor AI (https://cursor.com)
Created: 2025-05-19 21:01:28

This file is managed by template_manager.py.
Any changes to this header will be overwritten on the next fix.
"""

# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

# Description: Textual GPG Manager - Interactive GPG Key Management Tool
# Refactored from the original Bash script by Mauro Rosero Pérez.
# Uses the Textual TUI framework.

import sys
import argparse
import datetime
import os
import platform
import subprocess
import time
import tempfile
from typing import Any, Coroutine

# --- Third-party Libraries ---
import questionary # Still useful for simple prompts within screens
import gnupg
import requests
from rich.text import Text
from rich.panel import Panel
from rich.console import Console

from textual.app import App, ComposeResult, Binding
from textual.containers import Container, VerticalScroll, Horizontal # Import Horizontal
from textual.reactive import var
from textual.screen import Screen, ModalScreen
from textual.widgets import (
    Header, Footer, DataTable, Static, Button, Input, Select, Log, LoadingIndicator, Label
)
from textual.validation import Validator, ValidationResult, Length, Regex
from textual.message import Message
from textual.css.query import NoMatches
from textual.coordinate import Coordinate
from textual.worker import Worker #, WorkerStateChanged # Import Worker stuff
from textual import events # Import events for WipScreen

# --- Constants (from utils.py) ---
COLOR_SUCCESS = "green"
COLOR_WARNING = "yellow"
COLOR_ERROR = "bold red"
COLOR_INFO = "blue"
COLOR_PRIMARY = "cyan"
COLOR_DIM = "dim"

# --- Global Console (from utils.py) ---
console = Console()

# --- Formatting Functions (from utils.py) ---

def format_fingerprint(fingerprint):
    """Formats a fingerprint by adding spaces every 4 characters."""
    if not fingerprint:
        return ""
    return ' '.join(fingerprint[i:i+4] for i in range(0, len(fingerprint), 4))

def format_date(timestamp):
    """Converts a UNIX timestamp (str or int) to a YYYY-MM-DD string."""
    if not timestamp:
        return "N/A"
    try:
        ts = int(timestamp)
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    except (ValueError, TypeError, OSError): # Handle potential invalid timestamps or dates far in the past/future
        return "Invalid Date"

def format_expiry(timestamp):
    """Converts an expiry timestamp to YYYY-MM-DD or 'Never' with color coding."""
    if not timestamp:
        return Text("Never", style=COLOR_SUCCESS)
    try:
        ts = int(timestamp)
        expiry_date = datetime.datetime.fromtimestamp(ts)
        now = datetime.datetime.now()
        date_str = expiry_date.strftime('%Y-%m-%d')
        if expiry_date < now:
            return Text(date_str, style=COLOR_ERROR)
        elif (expiry_date - now).days <= 30:
             return Text(f"{date_str} (Expires Soon!)", style=COLOR_WARNING)
        return Text(date_str, style=COLOR_WARNING) # Future expiration
    except (ValueError, TypeError, OSError):
        return Text("Invalid Date", style=COLOR_ERROR)

# --- Console Output Functions (from utils.py) ---

def show_success(message):
    """Displays a success message."""
    console.print(f"[bold {COLOR_SUCCESS}]✔ Success:[/bold {COLOR_SUCCESS}] {message}")

def show_warning(message):
    """Displays a warning message."""
    console.print(f"[bold {COLOR_WARNING}]⚠ Warning:[/bold {COLOR_WARNING}] {message}")

def show_error(message, details=None):
    """Displays an error message."""
    console.print(f"[bold {COLOR_ERROR}]✖ Error:[/bold {COLOR_ERROR}] {message}")
    if details:
        console.print(f"  [dim]Details: {details}[/dim]")

def show_info(message):
    """Displays an informational message."""
    console.print(f"[bold {COLOR_INFO}]ℹ Info:[/bold {COLOR_INFO}] {message}")

def section_header(title):
    """Displays a styled section header."""
    console.print(Panel(Text(title, justify="center", style=f"bold {COLOR_PRIMARY}"), expand=False))

def confirm_continue(message="Press Enter to continue..."):
    """Pauses execution and waits for Enter key."""
    try:
        input(f"\n{message}")
    except (EOFError, KeyboardInterrupt):
        console.print("\nOperation cancelled.")

# --- Common Prompts (from utils.py) ---

def ask_confirmation(message, default=True):
    """Asks a yes/no confirmation question."""
    try:
        # Use questionary directly here
        return questionary.confirm(message, default=default).ask()
    except (EOFError, KeyboardInterrupt):
        show_warning("Confirmation cancelled.")
        return False # Treat cancellation as 'no'

# --- System/Environment (from utils.py) ---

def check_dependency(command, install_info=None, package_name=None):
    """Checks if a command-line tool is available in the system PATH."""
    try:
        subprocess.run([command, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pkg_name = package_name or command
        show_error(f"'{command}' command not found or not executable.")
        if install_info:
            console.print(f"Please install '{pkg_name}' to use this feature.")
            console.print(f"  Installation hints: {install_info}")
        else:
            console.print(f"Please ensure '{pkg_name}' is installed and in your system's PATH.")
        return False

def get_default_gpg_home():
    """Gets the default GPG home directory based on the OS."""
    if platform.system() == "Windows":
        appdata = os.getenv('APPDATA')
        return os.path.join(appdata, 'gnupg') if appdata else None
    else:
        return os.path.expanduser("~/.gnupg")

def ensure_directory_exists(dir_path, mode=0o700):
    """Ensures a directory exists, creating it with specified permissions if not."""
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, mode=mode, exist_ok=True)
            parent_dir = os.path.dirname(dir_path)
            if "secure" in parent_dir.lower() and parent_dir == os.path.expanduser("~/secure"):
                 if platform.system() != "Windows": os.chmod(parent_dir, mode)
            if platform.system() != "Windows": os.chmod(dir_path, mode) # Explicitly set mode after creation
            show_info(f"Created directory: {dir_path}")
            return True
        except OSError as e:
            show_error(f"Failed to create directory {dir_path}: {e}")
            return False
    elif platform.system() != "Windows":
         try:
             os.chmod(dir_path, mode)
         except OSError as e:
             show_warning(f"Could not set permissions on existing directory {dir_path}: {e}")
    return True

# --- Network Functions (from network.py) ---

class SpinnerContext:
    """Context manager for showing a Rich spinner during operations."""
    def __init__(self, title="Processing..."):
        self.title = title
        self.spinner = Spinner("dots", text=Text(title, style=COLOR_INFO))

    def __enter__(self):
        self.start_time = time.monotonic()
        self.live = console.status(self.spinner)
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.live.stop()
        duration = time.monotonic() - self.start_time
        # Optional: Log duration or status based on exceptions

def download_key_from_url(url):
    """Downloads key data from a given URL."""
    show_info(f"Attempting to download key from: {url}")
    try:
        with SpinnerContext(f"Downloading key from {url[:50]}..."):
            response = requests.get(url, timeout=15)
            response.raise_for_status()

        content_type = response.headers.get('content-type', '').lower()
        key_data = response.text

        if "BEGIN PGP" not in key_data:
            show_warning("Downloaded content doesn't look like a PGP key.")
            show_info(f"Content type: {content_type}")
            show_info(f"Content preview:\n{key_data[:200]}...")
            return None

        show_info("Download successful.")
        return key_data

    except requests.exceptions.RequestException as e:
        show_error(f"Failed to download key from URL: {e}")
        return None
    except Exception as e:
        show_error(f"An unexpected error occurred during download: {e}")
        return None

# --- TUI Functions (from tui.py) ---

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
        choice_text = f"{uid_str} (KeyID: {key_id_short})"
        choices.append(choice_text)
        key_map[choice_text] = key.get('fingerprint', key_id)

    if include_cancel:
        choices.append("Cancel")

    selected_choice = ask_question(prompt, q_type='select', choices=choices)

    if selected_choice == "Cancel" or selected_choice is None:
        return None

    return key_map.get(selected_choice)

def display_keys_elegant(keys_data):
    """Displays a summarized list of GPG keys elegantly using Rich."""
    if not keys_data:
        console.print(f"[{COLOR_WARNING}]No GPG keys found.[/]")
        return

    table = Table(
        title="🔑 Available GPG Keys (Summary)",
        box=ROUNDED,
        show_header=True,
        header_style=f"bold {COLOR_PRIMARY}",
        expand=True,
        padding=(0, 1),
        show_edge=False
    )

    # Simplified Columns with adjusted width for Type/Trust
    table.add_column("Type/Trust", style=COLOR_DIM, width=12, justify="center", no_wrap=True)
    table.add_column("Key ID", style="bold magenta", width=10, no_wrap=True)
    table.add_column("Expires", style=COLOR_WARNING, min_width=12, no_wrap=True)
    table.add_column("Primary User ID", style=COLOR_INFO, ratio=1)

    displayed_fprs = set()

    for key in keys_data:
        fpr = key.get('fingerprint')
        if not fpr or fpr in displayed_fprs: continue
        displayed_fprs.add(fpr)

        # key_type = key.get('type', '?') # Original type, usually 'pub'
        has_secret = key.get('secret', False)
        key_id_long = key.get('keyid', 'N/A')
        key_id_short = key_id_long[-8:] if len(key_id_long) >= 8 else key_id_long
        expires = format_expiry(key.get('expires'))
        uids_list = key.get('uids', [])
        primary_uid_text = uids_list[0] if uids_list else Text("No User ID", style="italic dim")
        ownertrust = key.get('ownertrust', '-')

        # Clearer type description
        if has_secret:
            type_text = "Pub+Sec"
        else:
            type_text = "Public " # Pad with space for alignment

        type_display = f"{type_text} [{ownertrust}]" # e.g., "Pub+Sec [u]" or "Public  [f]"

        table.add_row(
            type_display,
            key_id_short,
            expires,
            primary_uid_text
        )
        # Do NOT show subkeys or full fingerprint in this summary view

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
    table.add_row("Algorithm:", key_data.get('algo', 'N/A'))
    table.add_row("Length:", str(key_data.get('length', 'N/A')))
    table.add_row("Created:", format_date(key_data.get('date', 'N/A')))
    table.add_row("Expires:", format_expiry(key_data.get('expires', None)))
    table.add_row("Ownertrust:", key_data.get('ownertrust', 'N/A'))

    uids = key_data.get('uids', [])
    if uids:
        table.add_row("User IDs:", "")
        for i, uid in enumerate(uids):
             prefix = "  └─" if i > 0 else "  "
             table.add_row(prefix , uid)

    subkeys = key_data.get('subkeys', [])
    if subkeys:
        table.add_row("Subkeys:", "")
        for subkey_data in subkeys:
            try:
                 if isinstance(subkey_data[0], str) and subkey_data[0] in ['sub', 'ssb']:
                    stype, skid, _, _, sexp_ts, *rest = subkey_data
                 else:
                    stype = 'sub'
                    skid, _, _, sexp_ts, *rest = subkey_data
                 skid_short = skid[-8:] if len(skid) >= 8 else skid
                 sexp = format_expiry(sexp_ts)
                 sinfo = f"{stype.upper()} {skid_short} (Expires: {sexp})"
                 table.add_row("  └─", sinfo)
            except Exception:
                 table.add_row("  └─", f"(Could not parse subkey: {subkey_data})")

    console.print(table)

def ask_key_type():
    """Asks the user to select a GPG key type."""
    choices = [
        questionary.Choice("RSA and RSA (default) - Signing & Encryption", value="RSA_RSA"),
        questionary.Choice("DSA and Elgamal - Signing & Encryption (Older)", value="DSA_ELG"),
        questionary.Choice("ECC (EdDSA - ed25519) - Signing Only", value="ECC_SIGN"),
        questionary.Choice("ECC (ECDSA/ECDH - cv25519) - Signing & Encryption", value="ECC_BOTH"),
        questionary.Choice("Cancel", value="CANCEL"),
    ]
    return ask_question("Select key type:", q_type='select', choices=choices)

def ask_key_length(key_type="RSA_RSA"):
    """Asks the user for key length based on type."""
    if "RSA" in key_type:
        choices = ["3072", "4096"]; default = "4096"
    elif key_type == "DSA_ELG":
        choices = ["2048", "3072"]; default = "3072"
    elif "ECC" in key_type: return None # Length determined by curve
    else: choices = ["2048", "3072", "4096"]; default = "4096"
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
    if choice == "CUSTOM": return ask_question("Enter custom expiration (e.g., 18m, 90d, 2y):", q_type='text')
    elif choice == "CANCEL": return None
    return choice

def ask_user_info():
    """Asks for Real Name, Email, and optional Comment."""
    real_name = ask_question("Real name:", q_type='text', validate=lambda t: bool(t) or "Name cannot be empty")
    if real_name is None: return None, None, None
    email = ask_question("Email address:", q_type='text', validate=lambda t: "@" in t or "Invalid email format")
    if email is None: return None, None, None
    comment = ask_question("Comment (optional):", q_type='text')
    if comment is None and comment != "": return None, None, None
    return real_name, email, comment

# --- GPG Wrapper Class (from gpg_wrapper.py) ---

class GPGWrapper:
    """A class to manage interactions with GPG."""
    def __init__(self, gpg_home=None, gpg_binary='gpg'):
        self.gpg_home = gpg_home or get_default_gpg_home()
        self.gpg_binary = self._find_gpg_binary(gpg_binary)

        if not self.gpg_binary:
            show_error("GPG executable not found. Please install GnuPG.")
            os_name = platform.system()
            if os_name == "Linux": show_info("Hint: sudo apt install gnupg / sudo dnf install gnupg2 / sudo pacman -S gnupg")
            elif os_name == "Darwin": show_info("Hint: brew install gnupg")
            elif os_name == "Windows": show_info("Hint: Install Gpg4win from https://www.gpg4win.org/")
            raise FileNotFoundError("GPG executable not found")

        try:
            # Force GPG to use UTF-8 for both display and data output
            gpg_options = ['--display-charset', 'utf-8', '--charset', 'utf-8']
            self.gpg = gnupg.GPG(gnupghome=self.gpg_home, gpgbinary=self.gpg_binary, options=gpg_options)
            self.gpg.list_keys() # Test connection
        except Exception as e:
            show_error(f"Failed to initialize GPG: {e}", details=f"GPG Home: {self.gpg_home}, GPG Binary: {self.gpg_binary}")
            raise

    def _find_gpg_binary(self, preferred_binary='gpg'):
        candidates = [preferred_binary, 'gpg2']
        if platform.system() == "Windows":
            candidates.extend(['gpg.exe', 'gpg2.exe'])
            program_files = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            gpg4win_path = os.path.join(program_files, "GnuPG", "bin", "gpg.exe")
            if os.path.exists(gpg4win_path): return gpg4win_path
        for candidate in candidates:
            try:
                gnupg.GPG(gpgbinary=candidate).list_keys()
                return candidate
            except OSError: continue
            except Exception: continue
        return None

    def list_keys(self, secret=False):
        try: return self.gpg.list_keys(secret)
        except Exception as e: show_error(f"Failed to list keys: {e}"); return []

    def get_key(self, key_id):
        # Match suffix of fingerprint or key ID
        search_id = key_id.upper()
        keys = self.list_keys(False) + self.list_keys(True)
        for key in keys:
             fpr = key.get('fingerprint')
             kid = key.get('keyid')
             if (fpr and fpr.endswith(search_id)) or (kid and kid.endswith(search_id)):
                 return key
        return None

    def export_keys(self, keyids, secret=False, armor=True, output_path=None):
        try:
            export_args = {'armor': armor, 'output': output_path, 'secret': secret}
            export_args = {k: v for k, v in export_args.items() if v is not None}
            result = self.gpg.export_keys(keyids, **export_args)
            if output_path:
                return os.path.exists(output_path) and os.path.getsize(output_path) > 0
            elif result: return result
            else: show_error("Export failed: No data returned."); return None
        except Exception as e: show_error(f"Failed to export key(s) {keyids}: {e}"); return None

    def import_keys(self, key_data=None, filepath=None):
        if not key_data and not filepath: show_error("Import: No data/file."); return None
        if filepath and not os.path.exists(filepath): show_error(f"Import: File not found '{filepath}'"); return None
        try:
            if filepath:
                 with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: key_data = f.read()
            result = self.gpg.import_keys(key_data)
            if result and result.count > 0:
                show_info(f"Import Results: Processed={result.count}, Imported={result.imported}, Unchanged={result.unchanged}")
                if result.fingerprints: console.print(f"  Fingerprints: {result.fingerprints}")
                if hasattr(result, 'results'):
                    for res in result.results:
                        if res.get('problem') and res.get('problem') != '0':
                            show_warning(f"  Problem importing {res.get('fingerprint', '')}: {res.get('text', 'Unknown')}")
                return result
            elif result: show_warning(f"GPG reported 0 keys imported. Status: {result.status}"); return None
            else: show_error("Import failed: No result object."); return None
        except Exception as e: show_error(f"Failed to import keys: {e}"); return None

    def delete_keys(self, keyids, secret=False):
        action = "secret/public key" if secret else "public key"
        try:
            results = []
            for keyid in keyids:
                 key_info = self.get_key(keyid)
                 fingerprint = key_info.get('fingerprint') if key_info else keyid
                 if not fingerprint: show_warning(f"No fingerprint for {keyid}. Skipping delete."); continue

                 show_info(f"Attempting delete: {action} {fingerprint[-16:]}...")
                 result = self.gpg.delete_keys(fingerprint, secret) # Deletes both if secret=True and secret exists
                 results.append(result)
                 if 'deleted' in result.status.lower() or 'ok' in result.status.lower():
                     show_success(f"Deletion initiated for {fingerprint[-16:]}.")
                 elif 'not found' in result.status.lower(): show_warning(f"Key {fingerprint[-16:]} not found.")
                 else: show_error(f"Delete failed for {fingerprint[-16:]}. Status: {result.status}", details=result.stderr)
            return results
        except Exception as e: show_error(f"Key deletion error: {e}"); return []

    def generate_key(self, input_data):
        try:
            result = self.gpg.gen_key(input_data)
            if result and result.fingerprint: show_success(f"Key generated! Fingerprint: {result.fingerprint}"); return result
            elif result: show_error("Key generation failed.", details=f"Status: {result.status}, Stderr: {result.stderr}"); return None
            else: show_error("Key generation failed: No result object."); return None
        except Exception as e: show_error(f"Failed to generate key: {e}"); return None

    def receive_keys(self, keyserver, keyids):
        try:
            result = self.gpg.recv_keys(keyserver, *keyids)
            if result and result.count > 0:
                show_info(f"Received {result.count} key(s) from {keyserver}.")
                if result.fingerprints: console.print(f"  Fingerprints: {result.fingerprints}")
                return result
            elif result: show_warning(f"GPG reported 0 keys received from {keyserver}. Status: {result.status}"); return None
            else: show_error(f"Receive keys failed: No result from {keyserver}."); return None
        except Exception as e: show_error(f"Failed to receive keys from {keyserver}: {e}"); return None

    def send_keys(self, keyserver, keyids):
        try:
            result = self.gpg.send_keys(keyserver, *keyids)
            if result and 'request_status' in result.data and result.data['request_status'] == 'ok':
                 show_success(f"Sent {len(keyids)} key(s) to {keyserver}.")
                 return True
            elif result:
                status = result.status or result.data.get('reason', 'Unknown')
                show_error(f"Failed to send keys to {keyserver}. Status: {status}", details=result.stderr); return False
            else: show_error(f"Send keys failed: No result from {keyserver}."); return False
        except Exception as e: show_error(f"Failed to send keys to {keyserver}: {e}"); return False

    def sign_key(self, key_id, signing_key_id, trust_level):
        show_warning("Direct key signing API is limited. Attempting via --edit-key.")
        show_info("Attempting sign via GPG (may require interaction)...")
        gpg_commands = f"sign\n{trust_level}\ny\nsave\n"
        return self._run_gpg_edit_key(key_id, gpg_commands)

    def generate_revocation_certificate(self, key_id, reason_code="0", reason_string="", output_path=None):
        if not output_path: show_error("Output path required for revoke cert."); return False
        try:
            # Note: python-gnupg doesn't wrap --gen-revoke well for batch. Direct call.
            command = [
                self.gpg_binary, '--batch', '--yes', '--status-fd=1', '--command-fd=0',
                f'--homedir={self.gpg_home}' if self.gpg_home else '',
                f'--output={output_path}', '--gen-revoke', key_id
            ]
            command = [c for c in command if c]
            # Provide reason via command fd
            batch_input = f"key {key_id}\nrevocation-reason {reason_code} {reason_string}\ny\ny\n".encode('utf-8')

            process = subprocess.run(command, input=batch_input, capture_output=True, check=False)

            if process.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                 show_success(f"Revocation certificate generated: {output_path}")
                 try: os.chmod(output_path, 0o600)
                 except OSError as chmod_err: show_warning(f"Could not set permissions on {output_path}: {chmod_err}")
                 return True
            else:
                 stderr = process.stderr.decode('utf-8', errors='ignore') if process.stderr else "No stderr"
                 show_error("Failed to generate revocation certificate.", details=stderr)
                 if os.path.exists(output_path) and os.path.getsize(output_path) == 0: os.remove(output_path)
                 return False
        except Exception as e: show_error(f"Failed to generate revoke cert for {key_id}: {e}"); return False

    def search_keys(self, keyserver, query):
         try:
             show_info(f"Searching for '{query}' on {keyserver}...")
             command = [
                 self.gpg_binary, '--batch', '--status-fd=1',
                 f'--homedir={self.gpg_home}' if self.gpg_home else '',
                 '--keyserver', keyserver, '--search-keys', query
             ]
             command = [c for c in command if c]
             process = subprocess.run(command, capture_output=True, text=True, check=False)
             stdout, stderr = process.stdout, process.stderr
             if process.returncode == 0 and stdout: return stdout # Return raw output
             elif "No keys found" in stdout or "No keys found" in stderr: show_info("No keys found."); return None
             else: show_error("Search failed.", details=stderr or stdout); return None
         except Exception as e: show_error(f"Failed search keys '{query}' on {keyserver}: {e}"); return None

    # --- Helper for edit-key operations ---
    def _run_gpg_edit_key(self, key_fpr: str, commands: str):
        """Internal helper to run gpg --edit-key with batch commands."""
        show_info("Running GPG edit-key command (may require interaction/passphrase)...")
        command = [
            self.gpg_binary, '--status-fd=1', '--command-fd=0', '--yes',
            f'--homedir={self.gpg_home}' if self.gpg_home else '',
            '--edit-key', key_fpr
        ]
        command = [c for c in command if c]
        try:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input=commands)
            if process.returncode == 0:
                show_success("GPG edit-key command finished successfully.")
                return True
            else:
                show_error(f"GPG edit-key command failed (Code: {process.returncode}).", details=stderr)
                return False
        except FileNotFoundError: show_error(f"GPG command not found: {self.gpg_binary}"); return False
        except Exception as e: show_error(f"An error occurred running GPG edit-key: {e}"); return False

# --- Module Functions (Combined) ---

# --- list_keys Functions ---
def list_keys_menu(gpg: GPGWrapper):
    """Displays the list/view keys menu."""
    while True:
        section_header("List/View Keys")
        keys_public = gpg.list_keys(secret=False)
        keys_secret = gpg.list_keys(secret=True)
        combined_keys = []
        secret_fingerprints = {key['fingerprint'] for key in keys_secret if 'fingerprint' in key}
        processed_fingerprints = set()
        for key in keys_public:
            fpr = key.get('fingerprint')
            if not fpr or fpr in processed_fingerprints: continue
            key['secret'] = fpr in secret_fingerprints
            combined_keys.append(key); processed_fingerprints.add(fpr)
        for key in keys_secret:
            fpr = key.get('fingerprint')
            if fpr and fpr not in processed_fingerprints:
                 key['secret'] = True; combined_keys.append(key); processed_fingerprints.add(fpr)

        if not combined_keys: show_warning("No GPG keys found."); confirm_continue(); return
        display_keys_elegant(combined_keys)
        choices = ["View Details of a Key", "Refresh List", "Back to Main Menu"]
        action = ask_question("Select an action:", q_type='select', choices=choices)
        if action == "View Details of a Key": view_key_details(gpg, combined_keys)
        elif action == "Refresh List": continue
        elif action == "Back to Main Menu" or action is None: break
        else: break

def view_key_details(gpg: GPGWrapper, keys: list):
     selected_fpr = select_key_from_list(keys, prompt="Select key to view details:")
     if not selected_fpr: return
     key_details = next((key for key in keys if key.get('fingerprint') == selected_fpr), None)
     if key_details: display_key_details(key_details)
     else: show_warning(f"Could not find details for fingerprint {selected_fpr}")
     confirm_continue()

# --- create_key Functions ---
def create_key_menu(gpg: GPGWrapper):
    section_header("Create New GPG Key")
    key_type_choice = ask_key_type()
    if key_type_choice is None or key_type_choice == "CANCEL": return
    key_length = ask_key_length(key_type_choice)
    if key_length is None and "ECC" not in key_type_choice: show_warning("Key length selection needed/cancelled."); return
    expiry = ask_expiry_date()
    if expiry is None or expiry == "CANCEL": return
    real_name, email, comment = ask_user_info()
    if real_name is None or email is None: return
    uid = f"{real_name}{f' ({comment})' if comment else ''} <{email}>"

    batch_lines = [
        "%echo Generating a new key...", "Key-Type: RSA", f"Key-Length: {key_length}",
        "Subkey-Type: RSA", f"Subkey-Length: {key_length}", f"Name-Real: {real_name}",
        f"Name-Comment: {comment}", f"Name-Email: {email}", f"Expire-Date: {expiry}",
        "%no-protection", "%commit", "%echo Key generation complete!"
    ]
    # Adjustments based on key_type_choice (simplified)
    if key_type_choice == "DSA_ELG": batch_lines[1:6] = ["Key-Type: DSA", "Key-Length: 3072", "Subkey-Type: ELG-E", "Subkey-Length: 3072", ""]
    elif key_type_choice == "ECC_SIGN": batch_lines[1:6] = ["Key-Type: EDDSA", "Key-Curve: ed25519", "", "", ""]
    elif key_type_choice == "ECC_BOTH": batch_lines[1:6] = ["Key-Type: ECDSA", "Key-Curve: nistp256", "Subkey-Type: ECDH", "Subkey-Curve: cv25519", ""]
    batch_input = "\n".join(line for line in batch_lines if line)

    print(f"\n--- Key Parameters ---\n Type: {key_type_choice}\n Length: {key_length or 'Default'}\n Expires: {expiry if expiry != '0' else 'Never'}\n User ID: {uid}\n----------------------")
    if not ask_confirmation("Proceed with key generation?", default=True): return

    try:
        with SpinnerContext("Generating key pair..."): result = gpg.generate_key(batch_input)
        if not result or not result.fingerprint: show_error("Key generation seemed to fail.")
    except Exception as e: show_error(f"Unexpected error during key generation: {e}")
    confirm_continue()

# --- export_import Functions ---
def export_menu(gpg: GPGWrapper):
    section_header("Export Keys / Certificates")
    keys = gpg.list_keys(secret=False)
    if not keys: show_warning("No keys available."); confirm_continue(); return
    key_fpr = select_key_from_list(keys, prompt="Select key to export/manage:")
    if not key_fpr: return
    choices = ["Export Public Key (.asc)", "Export Private Key (.asc) - CAREFUL!", "Publish Public Key to Keyserver", "Generate Backup Revocation Certificate (.asc)", "Back"]
    choice = ask_question("Select action:", q_type='select', choices=choices)
    if choice == choices[0]: export_public_key(gpg, key_fpr)
    elif choice == choices[1]: export_private_key(gpg, key_fpr)
    elif choice == choices[2]: publish_to_keyserver(gpg, key_fpr)
    elif choice == choices[3]: generate_backup_revocation_cert(gpg, key_fpr)

def export_public_key(gpg: GPGWrapper, key_fpr: str):
    fname = f"publickey_{key_fpr[-8:]}.asc"
    output_path = ask_question("Filename for public key:", default=fname)
    if not output_path: return
    with SpinnerContext(f"Exporting public key {key_fpr[-8:]}..."): success = gpg.export_keys([key_fpr], False, True, output_path)
    if success: show_success(f"Public key exported to: {output_path}")
    else: show_error("Public key export failed.")
    confirm_continue()

def export_private_key(gpg: GPGWrapper, key_fpr: str):
    fname = f"privatekey_{key_fpr[-8:]}.asc"
    show_warning("Exporting private key is risky! Store securely.")
    if not ask_confirmation("Sure you want to export private key?", default=False): return
    output_path = ask_question("Filename for private key:", default=fname)
    if not output_path: return
    with SpinnerContext(f"Exporting private key {key_fpr[-8:]}..."): success = gpg.export_keys([key_fpr], True, True, output_path)
    if success: show_success(f"Private key exported to: {output_path}")
    else: show_error("Private key export failed.")
    confirm_continue()

def publish_to_keyserver(gpg: GPGWrapper, key_fpr: str):
    keyserver = ask_question("Keyserver address:", default="keys.openpgp.org")
    if not keyserver: return
    if not ask_confirmation(f"Publish key {key_fpr[-8:]} to {keyserver}?"): return
    with SpinnerContext(f"Publishing key to {keyserver}..."): gpg.send_keys(keyserver, [key_fpr])
    confirm_continue()

def generate_backup_revocation_cert(gpg: GPGWrapper, key_fpr: str):
    key_id_short = key_fpr[-8:]
    section_header("Generate Backup Revocation Cert")
    console.print("Used to revoke key if private key lost. Store securely & separately!")
    secure_dir = os.path.expanduser("~/secure/gpg/revocations")
    if not ensure_directory_exists(secure_dir): confirm_continue(); return
    fname = os.path.join(secure_dir, f"backup_revoke_{key_id_short}_{datetime.date.today():%Y%m%d}.asc")
    output_path = ask_question("Save revocation cert to:", default=fname)
    if not output_path: return
    if not ensure_directory_exists(os.path.dirname(output_path)): confirm_continue(); return
    reason_choices = {"1: Compromised": "1", "2: Superseded": "2", "3: No longer used": "3", "0: No reason (default)": "0", "Custom": "custom"}
    r_desc = ask_question("Revocation reason:", q_type='select', choices=list(reason_choices.keys()))
    if not r_desc: return
    r_code = reason_choices[r_desc]; r_str = ""
    if r_code == "custom": r_code = "0"; r_str = ask_question("Custom reason text:");
    if r_str is None: return
    with SpinnerContext("Generating certificate..."): success = gpg.generate_revocation_certificate(key_fpr, r_code, r_str, output_path)
    if success: show_warning("Store this revocation file safely!")
    confirm_continue()

def import_menu(gpg: GPGWrapper):
    while True:
        section_header("Import GPG Keys")
        choices = ["From File", "From Keyserver", "From URL", "From Pasted Text", "Import Revocation Cert", "Back"]
        choice = ask_question("Select import source:", q_type='select', choices=choices)
        if choice == choices[0]: import_from_file(gpg)
        elif choice == choices[1]: import_from_keyserver(gpg)
        elif choice == choices[2]: import_from_url(gpg)
        elif choice == choices[3]: import_from_text(gpg)
        elif choice == choices[4]: import_revocation_cert(gpg)
        elif choice == choices[5] or choice is None: break

def import_from_file(gpg: GPGWrapper):
    fpath = ask_question("Path to key file:", q_type='path')
    if not fpath or not os.path.exists(fpath): show_error(f"File not found: {fpath}"); confirm_continue(); return
    with SpinnerContext(f"Importing from {os.path.basename(fpath)}..."): result = gpg.import_keys(filepath=fpath)
    if result and result.imported > 0: ask_sign_imported_keys(gpg, result.fingerprints)
    confirm_continue()

def import_from_keyserver(gpg: GPGWrapper):
    keyserver = ask_question("Keyserver address:", default="keys.openpgp.org")
    if not keyserver: return
    search = ask_question("Email, key ID, fingerprint, or name to search:")
    if not search: return
    with SpinnerContext(f"Searching '{search}' on {keyserver}..."): output = gpg.search_keys(keyserver, search)
    if not output: confirm_continue(); return
    console.print("--- Search Results ---\n" + output + "----------------------")
    import_id = ask_question("Key ID or Fingerprint to import (or blank to cancel):")
    if not import_id: return
    with SpinnerContext(f"Importing {import_id} from {keyserver}..."): result = gpg.receive_keys(keyserver, [import_id])
    if result and result.imported > 0: ask_sign_imported_keys(gpg, result.fingerprints)
    confirm_continue()

def import_from_url(gpg: GPGWrapper):
    url = ask_question("URL of the key file:")
    if not url: return
    key_data = download_key_from_url(url)
    if key_data:
        with SpinnerContext("Importing downloaded key..."): result = gpg.import_keys(key_data=key_data)
        if result and result.imported > 0: ask_sign_imported_keys(gpg, result.fingerprints)
    else: show_error("Could not get key data from URL.")
    confirm_continue()

def import_from_text(gpg: GPGWrapper):
    console.print("Paste PGP key block below. Ctrl-D (Unix) or Ctrl-Z+Enter (Win) when done:")
    lines = [];
    try:
        while True: lines.append(input())
    except EOFError: pass
    except KeyboardInterrupt: show_warning("Input cancelled."); confirm_continue(); return
    key_data = "\n".join(lines)
    if not key_data or "BEGIN PGP" not in key_data: show_error("No valid key data."); confirm_continue(); return
    with SpinnerContext("Importing pasted key..."): result = gpg.import_keys(key_data=key_data)
    if result and result.imported > 0: ask_sign_imported_keys(gpg, result.fingerprints)
    confirm_continue()

def import_revocation_cert(gpg: GPGWrapper):
    section_header("Import Revocation Certificate")
    console.print("Marks the key as revoked. Cannot be easily undone!")
    fpath = ask_question("Path to revocation cert file:", q_type='path')
    if not fpath or not os.path.exists(fpath): show_error(f"File not found: {fpath}"); confirm_continue(); return
    try:
        with open(fpath, 'r') as f: content = f.read(500)
        if "BEGIN PGP" not in content or "REVOCATION" not in content.upper(): show_error("Not a valid revocation cert."); confirm_continue(); return
    except Exception as e: show_error(f"Could not read file: {e}"); confirm_continue(); return
    if not ask_confirmation("Import this revocation certificate?", default=False): return
    with SpinnerContext(f"Importing revocation cert..."): result = gpg.import_keys(filepath=fpath)
    # Checking result for specific revocation confirmation is fragile
    if result and result.results:
         revoked_fpr = next((res.get('fingerprint') for res in result.results if res.get('revoked') == '1' or "revoked" in res.get('text','').lower()), None)
         if revoked_fpr: show_success(f"Revocation imported for key {revoked_fpr}"); ask_publish_revoked(gpg, revoked_fpr)
         else: show_warning("Revocation processed, but couldn't confirm which key.")
    elif result: show_warning("Revocation import status unclear.")
    confirm_continue()

def ask_publish_revoked(gpg: GPGWrapper, fpr: str):
    if ask_confirmation("Publish this revocation to keyserver?", default=True):
         publish_to_keyserver(gpg, fpr) # Reuses export function

def ask_sign_imported_keys(gpg: GPGWrapper, imported_fingerprints: list):
    if not imported_fingerprints: return
    keys_to_sign = [gpg.get_key(fpr) for fpr in imported_fingerprints if gpg.get_key(fpr)]
    if not keys_to_sign: return
    console.print("\nImported Keys:")
    for key in keys_to_sign: console.print(f"  - {key.get('uids', ['?'])[0]} ({key.get('fingerprint', 'N/A')[-16:]})")
    if not ask_confirmation("Sign any of these keys to certify them?", default=True): return
    secret_keys = gpg.list_keys(secret=True)
    if not secret_keys: show_error("No private keys available to sign with."); return
    signing_fpr = select_key_from_list(secret_keys, prompt="Select YOUR key to sign with:")
    if not signing_fpr: return
    trust_choices = {"0: Don't know": "0", "1: Do not trust": "1", "2: Trust marginally": "2", "3: Trust fully": "3"}
    trust_desc = ask_question("Trust level for owner verification?", q_type='select', choices=list(trust_choices.keys()), default="2: Trust marginally")
    if not trust_desc: return
    trust_level = trust_choices[trust_desc]
    for key in keys_to_sign:
        target_fpr = key.get('fingerprint')
        if not target_fpr: continue
        uid_str = key.get('uids', ['?'])[0]
        if ask_confirmation(f"Sign key {uid_str} ({target_fpr[-8:]}) with {signing_fpr[-8:]}?", default=True):
            with SpinnerContext(f"Signing key {target_fpr[-8:]}..."): gpg.sign_key(target_fpr, signing_fpr, trust_level)

# --- subkeys Functions (Experimental) ---
def subkeys_menu(gpg: GPGWrapper):
    section_header("Manage Subkeys (Experimental)")
    show_warning("Subkey management uses direct GPG calls (may need interaction).")
    secret_keys = gpg.list_keys(secret=True)
    if not secret_keys: show_warning("No private keys found."); confirm_continue(); return
    key_fpr = select_key_from_list(secret_keys, prompt="Select primary key:")
    if not key_fpr: return
    while True:
        key_details = gpg.get_key(key_fpr)
        if not key_details: show_error(f"Cannot get key details {key_fpr}"); break
        display_subkey_info(key_details)
        choices = ["Add Subkey", "Change Subkey Expiration", "Revoke Subkey", "Back"]
        action = ask_question("Subkey action:", q_type='select', choices=choices)
        if action == choices[0]: add_subkey(gpg, key_fpr)
        elif action == choices[1]: change_subkey_expiration(gpg, key_fpr)
        elif action == choices[2]: revoke_subkey(gpg, key_fpr)
        elif action == choices[3] or action is None: break

def display_subkey_info(key_details):
    console.print(f"\n--- Subkeys for {key_details.get('keyid','N/A')[-8:]} ---")
    subkeys = key_details.get('subkeys', [])
    if not subkeys: console.print("  No subkeys found."); return
    for i, subkey_data in enumerate(subkeys):
        try:
            if isinstance(subkey_data[0], str) and subkey_data[0] in ['sub', 'ssb']: stype, skid, _, _, sexp_ts, *srest = subkey_data
            else: stype = 'sub'; skid, _, _, sexp_ts, *srest = subkey_data
            skid_short = skid[-8:]; sexp = format_expiry(sexp_ts)
            sfpr = f" (fpr: ...{srest[0][-16:]})" if srest and len(srest[0]) == 40 else ""
            console.print(f"  {i+1}) Type: {stype.upper()}, KeyID: {skid_short}, Expires: {sexp}{sfpr}")
        except Exception: console.print(f"  {i+1}) (Parse error: {subkey_data})")
    print("---------------------------")

# Reuse gpg._run_gpg_edit_key internal helper

def add_subkey(gpg: GPGWrapper, key_fpr: str):
    show_warning("Adding subkeys requires interactive GPG.")
    show_info("Launching 'gpg --edit-key'. Type 'addkey', follow prompts, then 'save'.")
    if not ask_confirmation("Launch interactive session?", default=True): return
    command = [gpg.gpg_binary, f'--homedir={gpg.gpg_home}' if gpg.gpg_home else '', '--edit-key', key_fpr]
    command = [c for c in command if c]
    try:
        console.print(f"\nRunning: {' '.join(command)}")
        subprocess.run(command, check=False)
        show_success("Interactive GPG finished.")
    except Exception as e: show_error(f"Failed to launch GPG: {e}")
    confirm_continue()

def select_subkey_index(gpg: GPGWrapper, key_fpr: str):
     key_details = gpg.get_key(key_fpr)
     if not key_details or not key_details.get('subkeys'): show_warning("No subkeys."); return None
     display_subkey_info(key_details)
     num = len(key_details['subkeys'])
     idx_str = ask_question(f"Enter subkey number (1-{num}):")
     try: idx = int(idx_str); return idx if 1 <= idx <= num else None
     except: show_error("Invalid number."); return None

def change_subkey_expiration(gpg: GPGWrapper, key_fpr: str):
    idx = select_subkey_index(gpg, key_fpr)
    if idx is None: return
    expiry = ask_expiry_date()
    if expiry is None or expiry == "CANCEL": return
    commands = f"key {idx}\nexpire\n{expiry}\ny\nsave\n"
    gpg._run_gpg_edit_key(key_fpr, commands)
    confirm_continue()

def revoke_subkey(gpg: GPGWrapper, key_fpr: str):
    idx = select_subkey_index(gpg, key_fpr)
    if idx is None: return
    if not ask_confirmation(f"Revoke subkey {idx}?", default=False): return
    # TODO: Ask for reason
    reason_code = "3"; reason_text = "Subkey revoked via manager."
    commands = f"key {idx}\nrevkey\n{reason_code}\n{reason_text}\ny\nsave\n"
    gpg._run_gpg_edit_key(key_fpr, commands)
    confirm_continue()

# --- identities Functions (Experimental) ---
def identities_menu(gpg: GPGWrapper):
    section_header("Manage Identities (User IDs - Experimental)")
    show_warning("Identity management uses direct GPG calls (may need interaction).")
    secret_keys = gpg.list_keys(secret=True)
    if not secret_keys: show_warning("No private keys found."); confirm_continue(); return
    key_fpr = select_key_from_list(secret_keys, prompt="Select primary key:")
    if not key_fpr: return
    while True:
        key_details = gpg.get_key(key_fpr)
        if not key_details: show_error(f"Cannot get key details {key_fpr}"); break
        display_identity_info(key_details)
        choices = ["Add User ID", "Set Primary User ID", "Revoke User ID", "Back"]
        action = ask_question("Identity action:", q_type='select', choices=choices)
        if action == choices[0]: add_identity(gpg, key_fpr)
        elif action == choices[1]: set_primary_identity(gpg, key_fpr)
        elif action == choices[2]: revoke_identity(gpg, key_fpr)
        elif action == choices[3] or action is None: break

def display_identity_info(key_details):
    console.print(f"\n--- Identities for {key_details.get('keyid','N/A')[-8:]} ---")
    uids = key_details.get('uids', [])
    if not uids: console.print("  No User IDs found."); return
    for i, uid_str in enumerate(uids):
        # TODO: Indicate primary UID
        console.print(f"  {i+1}) {uid_str}")
    print("-------------------------------")

def select_identity_index(gpg: GPGWrapper, key_fpr: str):
     key_details = gpg.get_key(key_fpr)
     if not key_details or not key_details.get('uids'): show_warning("No UIDs."); return None
     display_identity_info(key_details)
     num = len(key_details['uids'])
     idx_str = ask_question(f"Enter User ID number (1-{num}):")
     try: idx = int(idx_str); return idx if 1 <= idx <= num else None
     except: show_error("Invalid number."); return None

def add_identity(gpg: GPGWrapper, key_fpr: str):
    show_info("Adding new User ID.")
    rname, email, comment = ask_user_info()
    if rname is None or email is None: return
    uid_str = f"{rname}{f' ({comment})' if comment else ''} <{email}>"
    if not ask_confirmation(f"Add User ID: \"{uid_str}\"?"): return
    commands = f"adduid\n{rname}\n{email}\n{comment or ''}\nO\nsave\n"
    gpg._run_gpg_edit_key(key_fpr, commands)
    confirm_continue()

def set_primary_identity(gpg: GPGWrapper, key_fpr: str):
    idx = select_identity_index(gpg, key_fpr)
    if idx is None: return
    commands = f"uid {idx}\nprimary\nsave\n"
    gpg._run_gpg_edit_key(key_fpr, commands)
    confirm_continue()

def revoke_identity(gpg: GPGWrapper, key_fpr: str):
    idx = select_identity_index(gpg, key_fpr)
    if idx is None: return
    key_details = gpg.get_key(key_fpr)
    uid_rev = key_details['uids'][idx-1] if key_details and key_details.get('uids') and len(key_details['uids']) >= idx else '?'
    if not ask_confirmation(f"Revoke User ID {idx}: \"{uid_rev}\"?", default=False): return
    commands = f"uid {idx}\nrevuid\ny\nsave\n"
    gpg._run_gpg_edit_key(key_fpr, commands)
    confirm_continue()

# --- git_config Functions ---
def git_integration_menu(gpg: GPGWrapper):
    section_header("Git Integration")
    if not check_dependency("git", "Install Git from https://git-scm.com/downloads"): confirm_continue(); return
    while True:
        signingkey = get_git_config("user.signingkey")
        gpgsign = get_git_config("commit.gpgsign")
        program = get_git_config("gpg.program")
        console.print(f"\nCurrent Git Config:\n Signing Key: [cyan]{signingkey or 'Not Set'}\n Sign Commits: [cyan]{gpgsign or 'Not Set'}\n GPG Program: [cyan]{program or 'Default'}\n")
        choices = ["Set/Change Signing Key", "Enable Commit Signing", "Disable Commit Signing", "Set GPG Program Path", "Back"]
        action = ask_question("Git config action:", q_type='select', choices=choices)
        if action == choices[0]: set_git_signing_key(gpg)
        elif action == choices[1]: set_git_config("commit.gpgsign", "true")
        elif action == choices[2]: set_git_config("commit.gpgsign", "false")
        elif action == choices[3]: set_git_gpg_program(gpg)
        elif action == choices[4] or action is None: break

def run_git_config(args: list):
    try:
        cmd = ["git", "config", "--global"] + args
        res = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return res.stdout.strip()
    except FileNotFoundError: show_error("Git not found."); return None
    except subprocess.CalledProcessError as e: show_error(f"Git config failed: {e}", details=e.stderr.strip()); return None
    except Exception as e: show_error(f"Git config error: {e}"); return None

def get_git_config(key: str): return run_git_config(["--get", key])

def set_git_config(key: str, value: str):
    res = run_git_config([key, value])
    if res is not None: show_success(f"Git config '{key}' set globally.")
    confirm_continue()

def set_git_signing_key(gpg: GPGWrapper):
    keys = gpg.list_keys(secret=True)
    if not keys: show_warning("No private keys available."); confirm_continue(); return
    fpr = select_key_from_list(keys, prompt="Select key for Git signing:")
    if not fpr: return
    if ask_confirmation(f"Set Git signing key to {fpr[-16:]}?"): set_git_config("user.signingkey", fpr)

def set_git_gpg_program(gpg: GPGWrapper):
     curr = get_git_config("gpg.program")
     show_info(f"Current gpg.program: {curr or 'Default'}")
     show_info(f"Detected GPG: {gpg.gpg_binary}")
     path = ask_question("Enter GPG path for Git (blank to unset):", default=gpg.gpg_binary)
     if path is None: return
     elif path == "":
          if curr and ask_confirmation("Remove gpg.program setting?"): run_git_config(["--unset", "gpg.program"]); show_success("gpg.program unset."); confirm_continue()
     else:
          if ask_confirmation(f"Set gpg.program to '{path}'?"): set_git_config("gpg.program", path)

# --- Core Logic (from core.py) ---
APP_NAME = "GPG Manager TUI"
APP_VERSION = "0.2.0 (Textual Refactor)"
APP_AUTHOR = "Mauro Rosero Pérez (Original Bash Author)"

def display_welcome():
    header = Panel(Text(f"{APP_NAME} v{APP_VERSION}\\nby {APP_AUTHOR}", justify="center"), title="Welcome", border_style=COLOR_PRIMARY, expand=False)
    console.print(header)

def delete_key(gpg: GPGWrapper):
    section_header("Delete Key")
    show_warning("Deleting keys is irreversible!")
    pub_keys = gpg.list_keys(False); sec_keys = gpg.list_keys(True)
    all_keys_dict = {k['fingerprint']: k for k in pub_keys if 'fingerprint' in k}
    for sk in sec_keys:
        if fpr := sk.get('fingerprint'): all_keys_dict[fpr] = sk
    all_keys = list(all_keys_dict.values())
    if not all_keys: show_warning("No keys to delete."); confirm_continue(); return
    key_fpr = select_key_from_list(all_keys, prompt="Select key to DELETE:")
    if not key_fpr: return
    key_id_short = key_fpr[-8:]
    key_info = all_keys_dict.get(key_fpr)
    uid_str = key_info.get('uids', ['?'])[0] if key_info else '?'
    has_secret = any(sk.get('fingerprint') == key_fpr for sk in sec_keys)
    console.print(f"Selected delete: [bold red]{uid_str} ({key_id_short})[/]")
    del_secret = False
    if has_secret:
        if ask_confirmation(f"DELETE SECRET key {key_id_short}? (Also deletes public!)", default=False): del_secret = True
        elif ask_confirmation(f"DELETE ONLY PUBLIC key {key_id_short}?", default=False): del_secret = False
        else: show_info("Deletion cancelled."); return
    else:
        if not ask_confirmation(f"DELETE PUBLIC key {key_id_short}?", default=False): show_info("Deletion cancelled."); return
        del_secret = False
    action = "secret/public key" if del_secret else "public key"
    with SpinnerContext(f"Deleting {action} {key_id_short}..."): gpg.delete_keys([key_fpr], secret=del_secret)
    confirm_continue()

def main_menu(gpg: GPGWrapper):
    """Displays the main application menu and handles user selection."""
    # Map menu items directly to functions in this file
    menu_map = {
        "Create New GPG Key": create_key_menu,
        "List/View Keys": list_keys_menu,
        "Manage Subkeys (Experimental)": subkeys_menu,
        "Manage Identities (Experimental)": identities_menu,
        "Export Keys / Certificates": export_menu,
        "Import Keys / Certificates": import_menu,
        "Delete Key": delete_key,
        "Git Integration": git_integration_menu,
        "Exit": None
    }
    while True:
        console.clear()
        display_welcome()
        print()
        choice = ask_question("Select an action:", q_type='select', choices=list(menu_map.keys()))
        if choice == "Exit" or choice is None:
            console.print(Panel(f"[bold {COLOR_SUCCESS}]Goodbye![/]")); sys.exit(0)
        selected_function = menu_map.get(choice)
        if selected_function:
            try: selected_function(gpg) # Call function directly
            except Exception as e:
                 show_error(f"Unexpected error in module ({choice}): {e}")
                 console.print_exception(show_locals=False)
                 confirm_continue("Press Enter to return...")
        else: show_warning(f"Invalid choice: {choice}"); confirm_continue()

# --- Textual Screens ---

class KeyListScreen(Screen):
    """Screen to display the list of GPG keys in a DataTable."""
    BINDINGS = [
        Binding("r", "refresh", "Refresh List", show=True),
        Binding("n", "new_key", "New Key", show=True),
        Binding("i", "import_key", "Import", show=True),
        Binding("e", "export_key", "Export", show=True),
        Binding("d", "delete_key", "Delete", show=True),
        Binding("v", "view_details", "View Details", show=False), # Triggered by Enter
        Binding("ctrl+q", "quit", "Quit", show=True),
    ]

    keys = var([]) # Reactive variable to hold key data

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            DataTable(id="key-table", cursor_type="row", zebra_stripes=True),
            LoadingIndicator(id="loading"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load keys when the screen is mounted."""
        self.query_one(DataTable).add_column("Trust", key="trust")
        self.query_one(DataTable).add_column("Key ID", key="keyid")
        self.query_one(DataTable).add_column("Expires", key="expires")
        self.query_one(DataTable).add_column("User ID", key="uid")
        self.query_one(DataTable).add_column("Fingerprint", key="fingerprint", width=0) # Hidden column for data
        self.query_one("#loading").display = True
        self.run_worker(self.load_keys, exclusive=True)

    async def load_keys(self) -> None:
        """Worker function to load keys asynchronously."""
        loading_indicator = self.query_one("#loading")
        datatable = self.query_one(DataTable)
        gpg_handler = self.app.gpg_handler
        datatable.clear()
        loading_indicator.display = True

        try:
            if not gpg_handler:
                datatable.add_row(Text("Error: GPG Handler not initialized.", style="bold red"))
                return

            # Blocking calls are okay here because load_keys runs in a worker
            keys_public = gpg_handler.list_keys(secret=False)
            keys_secret = gpg_handler.list_keys(secret=True)

            secret_fingerprints = {key.get('fingerprint') for key in keys_secret if 'fingerprint' in key}
            combined_keys = []
            processed_fingerprints = set()

            for key in keys_public:
                fpr = key.get('fingerprint')
                if not fpr or fpr in processed_fingerprints: continue
                key['secret'] = fpr in secret_fingerprints
                combined_keys.append(key)
                processed_fingerprints.add(fpr)
            for key in keys_secret:
                fpr = key.get('fingerprint')
                if fpr and fpr not in processed_fingerprints:
                     key['secret'] = True
                     combined_keys.append(key)
                     processed_fingerprints.add(fpr)

            self.keys = combined_keys # Update reactive variable

            if not self.keys:
                datatable.add_row(Text("No GPG keys found.", style=COLOR_WARNING))
                return

            for key in self.keys:
                fpr = key.get('fingerprint')
                key_id_long = key.get('keyid', 'N/A')
                key_id_short = key_id_long[-8:] if len(key_id_long) >= 8 else key_id_long
                expires = format_expiry(key.get('expires'))
                uids_list = key.get('uids', [])
                primary_uid_text_raw = uids_list[0] if uids_list else "No User ID"
                primary_uid_text_obj: Text | str
                if not uids_list:
                    primary_uid_text_obj = Text("No User ID", style="italic dim")
                else:
                    try:
                        # Attempt to decode if it's bytes, or re-encode/decode if mis-decoded
                        if isinstance(primary_uid_text_raw, bytes):
                            primary_uid_text = primary_uid_text_raw.decode('utf-8', errors='replace')
                        else:
                            # Try re-encoding to latin1 (common misinterpretation) and then decoding as utf-8
                            try:
                                primary_uid_text = primary_uid_text_raw.encode('latin1').decode('utf-8', errors='replace')
                            except (UnicodeEncodeError, UnicodeDecodeError):
                                # If it contains chars not in latin1 or decoding fails, assume original is best guess
                                primary_uid_text = primary_uid_text_raw
                    except Exception:
                        primary_uid_text = "Error decoding UID" # Fallback
                    primary_uid_text_obj = primary_uid_text
                ownertrust = key.get('ownertrust', '-')
                type_text = "Pub+Sec" if key.get('secret') else "Public "
                type_display = f"{type_text} [{ownertrust}]"

                datatable.add_row(
                    Text(type_display, style=COLOR_DIM, overflow="ellipsis"),
                    Text(key_id_short, style="bold magenta"),
                    expires,
                    # Pass the potentially fixed string or Text object
                    Text(primary_uid_text_obj, overflow="ellipsis") if isinstance(primary_uid_text_obj, str) else primary_uid_text_obj,
                    fpr, # Add fingerprint to hidden column
                    key=fpr # Use fingerprint as row key
                )

        except Exception as e:
            datatable.clear()
            datatable.add_row(Text(f"Error loading keys: {e}", style="bold red"))
        finally:
            loading_indicator.display = False # Hide loading indicator

    def action_refresh(self) -> None:
        """Reload the keys."""
        self.run_worker(self.load_keys, exclusive=True)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection (e.g., Enter key press)."""
        fingerprint = event.row_key.value
        if fingerprint:
            self.action_view_details(fingerprint)

    def action_view_details(self, fingerprint: str | None = None) -> None:
        """Show the detail screen for the selected key."""
        if fingerprint is None:
            try:
                 cursor_coordinate = self.query_one(DataTable).cursor_coordinate
                 if not self.query_one(DataTable).is_valid_coordinate(cursor_coordinate):
                     self.app.bell()
                     return
                 fingerprint = self.query_one(DataTable).get_row_at(cursor_coordinate.row)[-1] # Get from hidden column
            except NoMatches:
                 self.app.bell()
                 return
            except IndexError:
                 self.app.bell() # Cursor might be on header or empty table
                 return

        if not fingerprint:
            self.app.bell()
            self.notify("Could not get fingerprint for selected row.", severity="warning")
            return

        key_data = next((key for key in self.keys if key.get('fingerprint') == fingerprint), None)
        if key_data:
            self.app.push_screen(KeyDetailScreen(key_data))
        else:
            self.notify(f"Could not find details for key {fingerprint[-8:]}", severity="error")

    def action_new_key(self) -> None:
        # self.app.push_screen(WipScreen("Create New Key")) # Original placeholder
        self.app.push_screen(CreateKeyScreen()) # Push the new screen

    def action_import_key(self) -> None:
        self.app.push_screen(WipScreen("Import Key"))

    def action_export_key(self) -> None:
        self.app.push_screen(WipScreen("Export Key"))

    def action_delete_key(self) -> None:
        try:
            table = self.query_one(DataTable)
            cursor_coordinate = table.cursor_coordinate
            if not table.is_valid_coordinate(cursor_coordinate):
                self.notify("No key selected.", severity="warning", title="Delete Key")
                return
            fingerprint = table.get_row_at(cursor_coordinate.row)[-1]
        except (NoMatches, IndexError):
            self.notify("Please select a key from the table first.", severity="warning", title="Delete Key")
            return

        if not fingerprint:
            self.notify("Could not get fingerprint for selected row.", severity="error", title="Delete Key")
            return

        key_data = next((key for key in self.keys if key.get('fingerprint') == fingerprint), None)
        if not key_data:
            self.notify(f"Could not find data for key {fingerprint[-8:]}. Please refresh.", severity="error", title="Delete Key")
            return

        # --- Use Textual Modal Dialog for confirmation --- #
        self.log(f"Pushing ConfirmDeleteDialog for {fingerprint[-8:]}")
        self.app.push_screen(
            ConfirmDeleteDialog(key_data=key_data, fingerprint=fingerprint)
            # Remove the callback argument
            # callback=self._handle_delete_confirmation_dialog
        )

    # --- Add the new message handler --- #
    def on_confirm_delete_dialog_deleted(self, message: "ConfirmDeleteDialog.Deleted") -> None:
        """Handle the custom message sent by ConfirmDeleteDialog."""
        self.log("---> ENTERED on_confirm_delete_dialog_deleted") # Log 1: Handler Entry
        action = message.action
        self.log(f"     Action received: {action!r}") # Log 2: Action value

        if action is None:
            self.log("     Action is None (Cancel), notifying and returning.") # Log 3a: Cancel path
            self.notify("Deletion cancelled.", title="Delete Key")
            return

        # Get the fingerprint from the currently selected row
        # (Assuming selection hasn't changed significantly while dialog was open)
        try:
            table = self.query_one(DataTable)
            cursor_coordinate = table.cursor_coordinate
            if not table.is_valid_coordinate(cursor_coordinate):
                 self.notify("Key selection changed or lost after confirmation.", severity="error")
                 return
            fingerprint = table.get_row_at(cursor_coordinate.row)[-1]
        except (NoMatches, IndexError):
            self.notify("Key selection lost after confirmation.", severity="error")
            return

        if not fingerprint:
             self.notify("Fingerprint missing after confirmation dialog.", severity="error")
             return

        # User confirmed, trigger the actual delete worker
        delete_secret = action == 'delete_secret'
        action_desc = "secret and public key" if delete_secret else "public key"
        self.log(f"on_confirm_delete_dialog_deleted: Triggering worker for {action_desc} - Fingerprint: {fingerprint[-8:]}")
        self.query_one("#loading").display = True
        self.run_worker(
            self._trigger_delete(fingerprint, delete_secret),
            exclusive=True,
            group="delete_key"
        )

    # _trigger_delete method remains the same
    async def _trigger_delete(self, fingerprint: str, secret: bool):
        """Worker coroutine to call the GPG delete function."""
        self.log(f"---> ENTER _trigger_delete: fpr={fingerprint[-8:]}, secret={secret}") # Log worker entry
        gpg_handler = self.app.gpg_handler
        if not gpg_handler:
            self.log("Worker: GPG Handler not found for delete.")
            return {"error": "GPG Handler not available."}
        try:
            result = gpg_handler.delete_keys([fingerprint], secret=secret)
            self.log(f"Worker: gpg_handler.delete_keys returned: {result}")
            # Check result status - delete_keys returns a list of result objects
            if result and isinstance(result, list) and len(result) > 0:
                status = result[0].status.lower()
                if 'deleted' in status or 'ok' in status:
                    return {"success": True, "message": f"Key {fingerprint[-8:]} deleted."}
                else:
                    details = f"Status: {result[0].status}, Stderr: {getattr(result[0], 'stderr', 'N/A')}"
                    self.log(f"Worker: Delete failed according to GPG. {details}")
                    return {"error": f"GPG reported delete failed.\nDetails: {details}"}
            else:
                self.log.warning(f"Worker: Unexpected result from delete_keys: {result}")
                return {"error": "Unexpected result from GPG delete operation."}
        except Exception as e:
            self.log.error(f"Worker: Exception during key deletion: {e}", exc_info=True)
            return {"error": f"An unexpected error occurred during key deletion: {e}"}

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle completion of background workers (load, delete, etc.)."""
        # ... (rest of method is unchanged) ...
        if event.worker.group == "delete_key":
            self.query_one("#loading").display = False # Hide list loading indicator
            self.log(f"Actual delete worker finished with state: {event.state}")
            if event.state == "SUCCESS":
                result = event.worker.result
                if isinstance(result, dict) and "error" in result:
                    self.app.push_screen(ErrorDialog("Deletion Failed", result['error']))
                elif isinstance(result, dict) and "success" in result:
                    self.notify(result.get("message", "Key deleted."), title="Success", severity="information")
                    self.action_refresh() # Refresh list after successful delete
                else:
                     self.app.push_screen(ErrorDialog("Delete Error", f"Unexpected result from delete worker: {result}"))
            elif event.state == "ERRORED":
                 error_details = f"Delete worker errored: {event.worker.error}"
                 self.log.error(error_details, exc_info=event.worker.error)
                 self.app.push_screen(ErrorDialog("Worker Error", error_details))
            return # Stop processing here for delete worker

        # --- Handle other workers (e.g., create key - though that's handled in CreateKeyScreen now) ---
        # ... (existing on_worker_state_changed logic for other workers if any) ...

        # Note: The on_worker_state_changed for CreateKeyScreen handles its own worker.
        # This handler in KeyListScreen is primarily for workers started *by* KeyListScreen.

    def action_quit(self) -> None:
        self.app.exit()

class KeyDetailScreen(Screen):
    """Screen to display details of a single GPG key."""
    BINDINGS = [
        Binding("escape,q", "back", "Back", show=True),
    ]

    def __init__(self, key_data: dict, name: str | None = None, id: str | None = None, classes: str | None = None):
        super().__init__(name=name, id=id, classes=classes)
        self.key_data = key_data

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="detail-container"):
            key_id_short = self.key_data.get('keyid', 'N/A')[-8:]
            yield Static(f"[bold cyan]Key Details: {key_id_short}[/]", id="detail-title")
            yield Static(self._format_details())
        yield Footer()

    def _format_details(self) -> Text:
        """Format key details into a Rich Text object."""
        t = Text()
        kd = self.key_data
        t.append("Key ID:      ", style="bold cyan").append(f"{kd.get('keyid', 'N/A')}\n")
        t.append("Fingerprint: ", style="bold cyan").append(f"{format_fingerprint(kd.get('fingerprint', 'N/A'))}\n")
        t.append("Type:        ", style="bold cyan").append(f"{kd.get('type', '?').upper()} / {kd.get('algo', '?')} / {kd.get('length', '?')} bits\n")
        t.append("Created:     ", style="bold cyan").append(f"{format_date(kd.get('date', 'N/A'))}\n")
        t.append("Expires:     ", style="bold cyan").append(format_expiry(kd.get('expires', None))).append("\n")
        t.append("Ownertrust:  ", style="bold cyan").append(f"{kd.get('ownertrust', 'N/A')}\n")

        uids = kd.get('uids', [])
        if uids:
            t.append("\nUser IDs:\n", style="bold cyan")
            for uid_raw in uids:
                uid: str
                try:
                    # Attempt to decode if it's bytes, or re-encode/decode if mis-decoded
                    if isinstance(uid_raw, bytes):
                        uid = uid_raw.decode('utf-8', errors='replace')
                    else:
                         # Try re-encoding to latin1 and then decoding as utf-8
                         try:
                             uid = uid_raw.encode('latin1').decode('utf-8', errors='replace')
                         except (UnicodeEncodeError, UnicodeDecodeError):
                             uid = uid_raw # Keep original if re-encoding fails
                except Exception:
                    uid = "Error decoding UID" # Fallback
                t.append(f"  - {uid}\\n")

        subkeys = kd.get('subkeys', [])
        if subkeys:
            t.append("\nSubkeys:\n", style="bold cyan")
            for subkey_data in subkeys:
                try:
                    if isinstance(subkey_data[0], str) and subkey_data[0] in ['sub', 'ssb']:
                        stype, skid, _, _, sexp_ts, *srest = subkey_data
                    else:
                        stype = 'sub'; skid, _, _, sexp_ts, *srest = subkey_data
                    skid_short = skid[-8:] if len(skid) >= 8 else skid
                    sexp = format_expiry(sexp_ts)
                    sfpr = f" (fpr: ...{srest[0][-16:]})" if srest and len(srest[0]) == 40 else ""
                    t.append(f"  - {stype.upper()} {skid_short} Expires: ").append(sexp).append(f"{sfpr}\n")
                except Exception:
                    t.append(f"  - (Error parsing subkey: {subkey_data})\n")
        return t

    def action_back(self) -> None:
        self.app.pop_screen()

class WipScreen(ModalScreen[bool]):
    """Modal screen indicating Work In Progress."""
    def __init__(self, feature_name: str = "Feature"):
        super().__init__()
        self.feature_name = feature_name

    def compose(self) -> ComposeResult:
        with VerticalScroll():
             yield Label("🚧 Work In Progress 🚧", id="wip-label")
             yield Static(f"The '{self.feature_name}' feature is not yet implemented.")
             yield Static("Press Escape or click OK to return.")
             yield Button("OK", variant="primary", id="wip-ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wip-ok":
            self.dismiss(True)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss(True)

# --- Modal Dialog for Deletion Confirmation ---

class ConfirmDeleteDialog(ModalScreen):
    """Modal dialog to confirm key deletion."""

    # Define a custom message for the result
    class Deleted(Message):
        def __init__(self, action: str | None) -> None:
            self.action = action
            super().__init__()

    def __init__(self, key_data: dict, fingerprint: str):
        super().__init__()
        self.key_data = key_data
        self.fingerprint = fingerprint
        self.has_secret = key_data.get('secret', False)

    def compose(self) -> ComposeResult:
        key_id_short = self.key_data.get('keyid', 'N/A')[-8:]
        uid_str = self.key_data.get('uids', ['(No User ID)'])[0]
        fpr_short = format_fingerprint(self.fingerprint)[-19:] # Last 4 blocks + spaces

        with VerticalScroll(id="delete-dialog"):
            yield Label("Confirm Deletion", id="delete-title")
            yield Static(f"Are you sure you want to delete this key?\nUID: {uid_str}\nKeyID: {key_id_short}\nFpr: ...{fpr_short}\n")
            if self.has_secret:
                yield Static("[bold red]This key has a secret key component![/]")
                yield Label("Choose action:")
                with Horizontal(id="delete-buttons"):
                     yield Button("DELETE SECRET+PUBLIC", variant="error", id="delete-secret")
                     yield Button("Delete Public Only", variant="warning", id="delete-public")
                     yield Button("Cancel", id="delete-cancel")
            else:
                 yield Static("[bold yellow]This is a PUBLIC key only.[/]")
                 with Horizontal(id="delete-buttons"):
                     yield Button("DELETE PUBLIC Key", variant="error", id="delete-public")
                     yield Button("Cancel", id="delete-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        action: str | None = None
        self.log(f"ConfirmDeleteDialog: Button '{button_id}' pressed.") # Log entry
        if button_id == "delete-cancel":
            action = None
        elif button_id == "delete-public":
            action = 'delete_public'
        elif button_id == "delete-secret":
            action = 'delete_secret'

        # Post the message first, then close the screen
        if action is not None or button_id == "delete-cancel": # Ensure cancel also posts a message
             self.log(f"ConfirmDeleteDialog: Posting message Deleted(action={action!r})") # Log before post
             self.post_message(self.Deleted(action=action))
             self.log("ConfirmDeleteDialog: Popping screen after posting message.") # Log before pop
             self.app.pop_screen()
        else:
             self.log(f"ConfirmDeleteDialog: Unknown button ID '{button_id}', doing nothing.") # Log unknown button

    def on_key(self, event: events.Key) -> None:
        self.log(f"ConfirmDeleteDialog: Key '{event.key}' pressed.") # Log entry
        if event.key == "escape":
             # Post the message first, then close the screen
             self.log("ConfirmDeleteDialog: Posting message Deleted(action=None) for Escape key") # Log before post
             self.post_message(self.Deleted(action=None))
             self.log("ConfirmDeleteDialog: Popping screen after posting Escape message.") # Log before pop
             self.app.pop_screen()

# --- Fin de ConfirmDeleteDialog ---

# --- New Screen for Key Creation ---

class CreateKeyScreen(Screen):
    """Screen for creating a new GPG key."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with VerticalScroll(id="create-key-form"):
            yield Label("Key Type:", classes="label")
            yield Select(
                [
                    ("RSA and RSA (default)", "RSA_RSA"),
                    ("DSA and Elgamal (Older)", "DSA_ELG"),
                    ("ECC (EdDSA - ed25519) - Sign Only", "ECC_SIGN"),
                    ("ECC (ECDSA/ECDH - cv25519) - Sign & Encrypt", "ECC_BOTH"),
                ],
                prompt="Select key type...",
                id="key-type"
            )

            yield Label("Key Length (bits):", classes="label", id="key-length-label")
            yield Select(
                [("3072", 3072), ("4096", 4096)],
                prompt="Select key length...",
                value=4096,
                id="key-length"
            )
            # Note: We will hide/show or change options dynamically based on type

            yield Label("Key Expiration:", classes="label")
            yield Select(
                [
                    ("Never (0)", "0"),
                    ("1 Year (1y)", "1y"),
                    ("2 Years (2y)", "2y"),
                    ("Custom...", "CUSTOM"),
                ],
                prompt="Select expiration...",
                value="1y",
                id="key-expiry"
            )
            yield Input(placeholder="e.g., 18m, 90d", id="key-expiry-custom", classes="hidden")

            yield Label("Real Name:", classes="label")
            yield Input(
                placeholder="Your full name",
                id="real-name",
                validators=[Length(minimum=1, failure_description="Real name cannot be empty.")]
            )

            yield Label("Email Address:", classes="label")
            yield Input(
                placeholder="your.email@example.com",
                id="email",
                validators=[
                    Length(minimum=1, failure_description="Email address cannot be empty."),
                    Regex(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", failure_description="Invalid email format.")
                ]
            )

            yield Label("Comment (Optional):", classes="label")
            yield Input(placeholder="e.g., Work key, Personal", id="comment")

            # TODO: Add Summary Section?

            yield Static(id="validation-summary", classes="error-text hidden") # For errors

            # Use Horizontal container for buttons
            with Horizontal(id="create-buttons"):
                 yield Button("Generate Key", variant="primary", id="generate")
                 yield Button("Cancel", id="cancel")

            # Add loading indicator (initially hidden)
            yield LoadingIndicator(id="create-loading")

        yield Footer()

    def on_mount(self) -> None:
        """Hide loading indicator initially."""
        self.query_one("#create-loading").display = False

    def action_cancel(self) -> None:
        """Called when the user presses escape or clicks Cancel."""
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "cancel":
            self.action_cancel() # Call the existing cancel action
        elif event.button.id == "generate":
            # --- Validation --- #
            validation_summary = self.query_one("#validation-summary")
            valid = True
            messages = []
            for widget_id in ["real-name", "email"]:
                widget = self.query_one(f"#{widget_id}", Input)
                validation = widget.validate(widget.value)
                if not validation.is_valid:
                    valid = False
                    messages.extend(validation.failure_descriptions)
            # TODO: Add validation for custom expiry if visible

            if valid:
                validation_summary.update("")
                validation_summary.add_class("hidden")
                # --- Gather Data --- #
                key_type = self.query_one("#key-type", Select).value
                key_length_widget = self.query_one("#key-length", Select)
                key_length = key_length_widget.value if key_length_widget.display else None
                expiry_choice = self.query_one("#key-expiry", Select).value
                expiry_custom = self.query_one("#key-expiry-custom", Input).value
                real_name = self.query_one("#real-name", Input).value
                email = self.query_one("#email", Input).value
                comment = self.query_one("#comment", Input).value

                # --- Format Batch Input --- #
                expiry = expiry_custom if expiry_choice == "CUSTOM" else expiry_choice
                batch_lines = [
                    "%echo Generating a new key...",
                    # Key type and length/curve
                    # Subkey type and length/curve
                    f"Name-Real: {real_name}",
                    f"Name-Comment: {comment}",
                    f"Name-Email: {email}",
                    f"Expire-Date: {expiry}",
                    "%no-protection", # Assuming no passphrase for batch for now
                    "%commit",
                    "%echo Key generation complete!"
                ]

                # Adjustments based on key_type (simplified from original)
                key_type_line = "Key-Type: RSA" # Default
                key_len_line = f"Key-Length: {key_length}"
                subkey_type_line = "Subkey-Type: RSA"
                subkey_len_line = f"Subkey-Length: {key_length}"
                key_curve_line = ""
                subkey_curve_line = ""

                if key_type == "DSA_ELG":
                    key_type_line = "Key-Type: DSA"
                    key_len_line = f"Key-Length: {key_length or 3072}"
                    subkey_type_line = "Subkey-Type: ELG-E"
                    subkey_len_line = f"Subkey-Length: {key_length or 3072}"
                elif key_type == "ECC_SIGN":
                    key_type_line = "Key-Type: EDDSA"
                    key_curve_line = "Key-Curve: ed25519"
                    key_len_line = "" # Determined by curve
                    subkey_type_line = "" # No default encryption subkey
                    subkey_len_line = ""
                elif key_type == "ECC_BOTH":
                    key_type_line = "Key-Type: ECDSA"
                    key_curve_line = "Key-Curve: nistp256" # Or cv25519? GPG default differs
                    key_len_line = "" # Determined by curve
                    subkey_type_line = "Subkey-Type: ECDH"
                    subkey_curve_line = "Subkey-Curve: cv25519"
                    subkey_len_line = ""

                # Insert the dynamic parts
                batch_lines.insert(1, key_type_line)
                if key_len_line: batch_lines.insert(2, key_len_line)
                if key_curve_line: batch_lines.insert(2, key_curve_line)
                if subkey_type_line: batch_lines.insert(3, subkey_type_line)
                if subkey_len_line: batch_lines.insert(4, subkey_len_line)
                if subkey_curve_line: batch_lines.insert(4, subkey_curve_line)

                batch_input = "\n".join(line for line in batch_lines if line) # Filter empty lines

                # --- Run Worker --- #
                self.log(f"Starting key generation worker with input:\n{batch_input}")
                # Show loading indicator
                self.query_one("#create-loading").display = True
                # Disable button to prevent double-clicks
                self.query_one("#generate", Button).disabled = True
                self.query_one("#cancel", Button).disabled = True
                self.run_worker(
                    self._trigger_generation(batch_input),
                    exclusive=True,
                    group="generate_key"
                )
            else:
                validation_summary.remove_class("hidden")
                validation_summary.update("\n".join(f"- {msg}" for msg in messages))
                self.app.bell()

    def watch_key_type(self, new_value: str) -> None:
        """Dynamically update key length options based on type."""
        key_length_select = self.query_one("#key-length", Select)
        key_length_label = self.query_one("#key-length-label")
        is_ecc = "ECC" in new_value

        key_length_select.display = not is_ecc
        key_length_label.display = not is_ecc

        if not is_ecc:
            if new_value == "RSA_RSA":
                key_length_select.set_options([("3072", 3072), ("4096", 4096)])
                key_length_select.value = 4096 # Default for RSA
            elif new_value == "DSA_ELG":
                key_length_select.set_options([("2048", 2048), ("3072", 3072)])
                key_length_select.value = 3072 # Default for DSA
            # Add other types if needed

    def watch_key_expiry(self, new_value: str) -> None:
        """Show/hide custom expiration input."""
        custom_input = self.query_one("#key-expiry-custom")
        if new_value == "CUSTOM":
            custom_input.remove_class("hidden")
        else:
            custom_input.add_class("hidden")
            custom_input.value = "" # Clear it when hidden

    async def _trigger_generation(self, batch_input: str):
        """Worker coroutine to call the GPG generate function."""
        self.log("Worker: Calling gpg_handler.generate_key")
        gpg_handler = self.app.gpg_handler
        if not gpg_handler:
            self.log("Worker: GPG Handler not found.")
            # Return an error indicator instead of notifying here
            return {"error": "GPG Handler not available."}

        try:
            result = gpg_handler.generate_key(batch_input)
            self.log(f"Worker: gpg_handler.generate_key returned: {result}")
            # Return the result object OR an error structure if result is bad
            if result and result.fingerprint:
                return result
            else:
                details = f"Status: {getattr(result, 'status', 'N/A')}, Stderr: {getattr(result, 'stderr', 'N/A')}"
                self.log(f"Worker: Key generation failed or no fingerprint. {details}")
                return {"error": f"Key generation failed or no fingerprint returned.\nDetails: {details}"}
        except Exception as e:
            self.log.error(f"Worker: Exception during key generation: {e}", exc_info=True)
            # Return an error indicator
            return {"error": f"An unexpected error occurred during key generation: {e}"}

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle completion or failure of the generation worker."""
        # Hide loading indicator and re-enable buttons regardless of outcome
        self.query_one("#create-loading").display = False
        try:
            self.query_one("#generate", Button).disabled = False
            self.query_one("#cancel", Button).disabled = False

            # Check if the worker is the one we are interested in
            if event.worker.group != "generate_key":
                return

            self.log(f"Worker {event.worker.name} finished with state: {event.state}")

            if event.state == "SUCCESS":
                result = event.worker.result
                # Check if the result indicates an error we packaged
                if isinstance(result, dict) and "error" in result:
                    self.log.error(f"Generation failed (reported by worker): {result['error']}")
                    self.app.push_screen(ErrorDialog("Generation Failed", result['error']))
                # Check if the result is a valid GPG result with a fingerprint
                elif hasattr(result, 'fingerprint') and result.fingerprint:
                    self.log.info(f"Key generated successfully: {result.fingerprint[-16:]}")
                    self.notify(f"Key generated successfully!\nFingerprint: {result.fingerprint[-16:]}", severity="information", title="Success", timeout=10)
                    self.app.pop_screen() # Go back to key list
                # Handle cases where GPG returned something unexpected (no fingerprint, no error packaged)
                else:
                    details = f"Unexpected GPG result: {result}"
                    self.log.warning(details)
                    self.app.push_screen(ErrorDialog("Generation Result Invalid", details))

            elif event.state == "ERRORED":
                error_details = f"Worker errored: {event.worker.error}"
                self.log.error(error_details, exc_info=event.worker.error)
                self.app.push_screen(ErrorDialog("Worker Error", error_details))

        except NoMatches:
            self.log.warning("Screen dismissed before worker finished, buttons not found.")
            pass # Screen was dismissed before worker finished

# --- Main Textual App ---

class GpgManagerApp(App):
    """The main Textual application for GPG Manager."""
    TITLE = APP_NAME
    SUB_TITLE = f"v{APP_VERSION}"
    CSS = """
    # Basic styling
    Screen {
        layers: base info;
    }
    KeyListScreen Container {
        padding: 1;
        border: round $accent;
    }
    DataTable {
        height: 1fr;
        border: none;
    }
    #loading {
        dock: bottom;
        layer: info;
        width: 100%;
        height: auto;
        display: block;
        text-style: bold dim;
        text-align: center;
        margin-top: 1;
    }
    KeyDetailScreen #detail-container {
        padding: 1 2;
        border: round $accent;
    }
    WipScreen {
         align: center middle;
         # background: $panel-darken-2;
         border: thick $accent;
    }
    WipScreen VerticalScroll {
         width: auto; height: auto; padding: 2 4;
         border: double $accent-lighten-1;
         background: $panel;
    }
    WipScreen #wip-label { margin-bottom: 1; }

    /* Style for CreateKeyScreen */
    CreateKeyScreen #create-key-form {
        padding: 1 2;
        border: round $accent;
    }
    CreateKeyScreen .label {
        margin-top: 1;
    }
    CreateKeyScreen .hidden {
        display: none;
    }
    CreateKeyScreen .error-text {
        color: $error;
        margin-top: 1;
    }
    CreateKeyScreen #create-buttons {
        margin-top: 1;
        height: auto; /* Let height be determined by buttons */
        align: right middle; /* Align buttons to the right */
        width: 100%;
    }
    CreateKeyScreen #create-buttons Button {
        margin-left: 1; /* Add spacing between buttons */
    }
    /* Style for the loading indicator in CreateKeyScreen */
    CreateKeyScreen #create-loading {
        margin-top: 1;
        /* You might want to center it too */
        /* width: 100%; */
        /* align: center middle; */
    }

    /* Style for ErrorDialog */
    ErrorDialog #error-dialog {
        width: auto; max-width: 80%;
        height: auto; max-height: 80%;
        padding: 1 2;
        border: thick $error;
        background: $panel;
    }
    ErrorDialog #error-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    ErrorDialog #error-message {
        margin-bottom: 1;
    }
    ErrorDialog #error-ok {
        margin-top: 1;
        width: 100%; /* Make OK button fill width */
    }

    /* Style for SuccessDialog */
    SuccessDialog #success-dialog {
        width: auto; max-width: 80%;
        height: auto; max-height: 80%;
        padding: 1 2;
        border: thick $success;
        background: $panel;
    }
    SuccessDialog #success-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    SuccessDialog #success-message {
        margin-bottom: 1;
    }
    SuccessDialog #success-ok {
        margin-top: 1;
        width: 100%;
    }

    /* Style for ConfirmDeleteDialog */
    ConfirmDeleteDialog #delete-dialog {
        /* Try a fixed width and smaller max height */
        width: 70;
        height: auto; max-height: 20;
        padding: 1 2;
        border: thick $warning;
        background: $panel;
    }
    ConfirmDeleteDialog #delete-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: $warning;
    }
    ConfirmDeleteDialog #delete-buttons {
        margin-top: 2;
        height: auto;
        align: right middle;
        width: 100%;
    }
    ConfirmDeleteDialog #delete-buttons Button {
        margin-left: 1;
    }

    """

    # Global GPG Handler
    gpg_handler: GPGWrapper | None = None

    def on_mount(self) -> None:
        """Initialize GPG handler and push the main screen."""
        try:
            # Show loading while initializing GPG
            # TODO: Add a proper loading screen or indicator here
            self.gpg_handler = GPGWrapper()
            self.push_screen(KeyListScreen())
        except FileNotFoundError:
            # Handle GPG not found gracefully (e.g., show error screen)
            # For now, just exit after showing error in GPGWrapper
            self.exit(message="GPG executable not found. Exiting.")
        except Exception as e:
            self.exit(message=f"Critical GPG initialization error: {e}")

# --- Main Execution --- (Moved to the end)
# def main():
# ...

# if __name__ == "__main__":
#     main()

# --- Previous main_menu and main function definitions are now obsolete ---
# They are replaced by the Textual App structure above and the main() below.

# --- Main Execution --- (Moved from original spot)
def main():
    parser = argparse.ArgumentParser(prog='gpg_manager_tui.py', description=f'{APP_NAME} v{APP_VERSION}', epilog="Interactive GPG Tool using Textual")
    # Add args here if needed
    args = parser.parse_args()

    # Check dependencies needed by Textual/Rich and GPGWrapper
    # (questionary, gnupg, requests, textual)
    try:
        import textual # Quick check
        app = GpgManagerApp() # Now GpgManagerApp is defined
        app.run()
    except ImportError as e:
         print(f"[ERROR] Missing dependency: {e}", file=sys.stderr)
         print("Please install required packages: pip install textual python-gnupg rich questionary requests", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
         # Catch other potential errors during app setup or run
         print(f"[ERROR] An unexpected error occurred: {e}", file=sys.stderr)
         import traceback
         traceback.print_exc()
         sys.exit(1)

if __name__ == "__main__":
    main()
