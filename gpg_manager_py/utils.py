# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# utils.py - Description placeholder
# -----------------------------------------------------------------------------
#
import datetime
import os
import platform
import subprocess
import questionary
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

"""Utility functions for the GPG Manager application."""

# Constants
COLOR_SUCCESS = "green"
COLOR_WARNING = "yellow"
COLOR_ERROR = "bold red"
COLOR_INFO = "blue"
COLOR_PRIMARY = "cyan"
COLOR_DIM = "dim"

console = Console()

# --- Formatting Functions ---

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
        # Add warning for keys expiring soon (e.g., within 30 days)
        elif (expiry_date - now).days <= 30:
             return Text(f"{date_str} (Expires Soon!)", style=COLOR_WARNING)
        return Text(date_str, style=COLOR_WARNING) # Future expiration
    except (ValueError, TypeError, OSError):
        return Text("Invalid Date", style=COLOR_ERROR)

# --- Console Output Functions ---

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
        # questionary.press_any_key_to_continue(message) # Alternative using questionary
    except (EOFError, KeyboardInterrupt):
        # Handle cases where input stream is closed or user interrupts
        console.print("\nOperation cancelled.")
        # Optionally raise an exception or exit here if needed

# --- Common Prompts ---

def ask_confirmation(message, default=True):
    """Asks a yes/no confirmation question."""
    # Clear previous input buffer if any issue arises
    # sys.stdin.flush() # May not be needed with questionary
    try:
        return questionary.confirm(message, default=default).ask()
    except (EOFError, KeyboardInterrupt):
        show_warning("Confirmation cancelled.")
        return False # Treat cancellation as 'no'

# --- System/Environment ---

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
            # Ensure the parent directory also has restricted permissions if creating ~/secure
            parent_dir = os.path.dirname(dir_path)
            if "secure" in parent_dir.lower() and parent_dir == os.path.expanduser("~/secure"):
                 os.chmod(parent_dir, mode)
            os.chmod(dir_path, mode) # Explicitly set mode after creation
            show_info(f"Created directory: {dir_path}")
            return True
        except OSError as e:
            show_error(f"Failed to create directory {dir_path}: {e}")
            return False
    # Ensure existing directory has correct permissions if possible
    elif platform.system() != "Windows": # chmod doesn't work the same on Windows
         try:
             os.chmod(dir_path, mode)
         except OSError as e:
             show_warning(f"Could not set permissions on existing directory {dir_path}: {e}")
    return True 