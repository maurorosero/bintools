# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# git_config.py - Description placeholder
# -----------------------------------------------------------------------------
#
import subprocess
from ..gpg_wrapper import GPGWrapper
from ..tui import ask_question, select_key_from_list
from ..utils import section_header, show_error, show_success, show_warning, confirm_continue, ask_confirmation, check_dependency, console

"""Handles GPG integration with Git configuration."""

def git_integration_menu(gpg: GPGWrapper):
    """Main menu for Git integration."""
    section_header("Git Integration")

    if not check_dependency("git", "Install Git from https://git-scm.com/downloads"):
        confirm_continue()
        return

    while True:
        current_signing_key = get_git_config("user.signingkey")
        current_gpgsign = get_git_config("commit.gpgsign")
        current_program = get_git_config("gpg.program")

        console.print("\nCurrent Git GPG Configuration:")
        console.print(f"  Signing Key (user.signingkey): [cyan]{current_signing_key or 'Not Set'}[/]")
        console.print(f"  Sign Commits (commit.gpgsign): [cyan]{current_gpgsign or 'Not Set'}[/]")
        console.print(f"  GPG Program (gpg.program):     [cyan]{current_program or 'Default'}[/]")
        print()

        choices = [
            "Set/Change Signing Key",
            "Enable Commit Signing Globally",
            "Disable Commit Signing Globally",
            "Set GPG Program Path",
            "Back to Main Menu"
        ]
        action = ask_question("Select Git configuration action:", q_type='select', choices=choices)

        if action == "Set/Change Signing Key":
            set_git_signing_key(gpg)
        elif action == "Enable Commit Signing Globally":
            set_git_config("commit.gpgsign", "true")
        elif action == "Disable Commit Signing Globally":
            set_git_config("commit.gpgsign", "false")
        elif action == "Set GPG Program Path":
            set_git_gpg_program(gpg)
        elif action == "Back to Main Menu" or action is None:
            break
        else:
            break

def run_git_config(args: list):
    """Runs a 'git config --global' command."""
    try:
        command = ["git", "config", "--global"] + args
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except FileNotFoundError:
        show_error("Git command not found. Is Git installed and in PATH?")
        return None
    except subprocess.CalledProcessError as e:
        show_error(f"Git config command failed: {e}", details=e.stderr.strip())
        return None
    except Exception as e:
         show_error(f"An unexpected error occurred running git config: {e}")
         return None

def get_git_config(key: str):
    """Gets a specific global Git config value."""
    # Add --get to retrieve the value
    return run_git_config(["--get", key])

def set_git_config(key: str, value: str):
    """Sets a specific global Git config value."""
    result = run_git_config([key, value])
    if result is not None: # Command succeeded (even if output is empty)
         show_success(f"Git config '{key}' set to '{value}' globally.")
    # Error handled by run_git_config
    confirm_continue()

def set_git_signing_key(gpg: GPGWrapper):
    """Prompts user to select a key and sets it in Git config."""
    secret_keys = gpg.list_keys(secret=True)
    if not secret_keys:
        show_warning("No private keys available to use for signing.")
        confirm_continue()
        return

    key_fpr = select_key_from_list(secret_keys, prompt="Select the key to use for Git commit signing:")
    if not key_fpr:
        return

    key_id_short = key_fpr[-16:] # Git usually uses the long ID or fingerprint

    if ask_confirmation(f"Set Git signing key to {key_id_short}?", default=True):
        set_git_config("user.signingkey", key_fpr) # Use fingerprint for precision

def set_git_gpg_program(gpg: GPGWrapper):
     """Sets the gpg.program path in Git config."""
     current_program = get_git_config("gpg.program")
     show_info(f"Current gpg.program path: {current_program or 'Default'}")
     show_info(f"The detected GPG executable for this tool is: {gpg.gpg_binary}")

     new_path = ask_question("Enter the full path to the GPG executable for Git (or leave blank to use default/remove setting):",
                           default=gpg.gpg_binary)

     if new_path is None: # User cancelled
          return
     elif new_path == "": # User wants to remove setting
          if current_program and ask_confirmation("Remove the gpg.program setting and use Git's default?", default=True):
               run_git_config(["--unset", "gpg.program"])
               show_success("gpg.program setting removed globally.")
               confirm_continue()
     else:
          if ask_confirmation(f"Set gpg.program to '{new_path}'?", default=True):
               set_git_config("gpg.program", new_path) 