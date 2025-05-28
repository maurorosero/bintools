#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# en.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# English language file for GitHub CLI Installer
# License: AGPL-3.0

# Color settings using unique names to avoid conflicts with common.sh
TERM_COLOR_INFO="\033[1;34m"    # Bold Blue
TERM_COLOR_SUCCESS="\033[1;32m" # Bold Green
TERM_COLOR_WARNING="\033[1;33m" # Bold Yellow
TERM_COLOR_ERROR="\033[1;31m"   # Bold Red
TERM_COLOR_RESET="\033[0m"      # Reset color

# Register translations in the TRANSLATIONS associative array
# This is how the i18n system in gpg-manager.sh expects them
TRANSLATIONS["main_menu_title"]="GPG Key Manager"
TRANSLATIONS["main_menu_subtitle"]="MR*Developer Tools"
TRANSLATIONS["msg_banner_title"]="GitHub CLI Installer"
TRANSLATIONS["msg_banner_subtitle"]="MR*Developer Tools"
TRANSLATIONS["msg_start"]="Starting GitHub CLI installation..."
TRANSLATIONS["msg_root_required"]="This script requires root privileges for installation."
TRANSLATIONS["msg_root_attempt"]="Attempting to escalate privileges..."
TRANSLATIONS["msg_root_unavailable"]="Sudo is not available. Please run this script as root."
TRANSLATIONS["msg_check_system"]="Checking system requirements..."
TRANSLATIONS["msg_pkg_detected"]="Package manager detected:"
TRANSLATIONS["msg_install_curl"]="Installing curl..."
TRANSLATIONS["msg_curl_fail"]="Failed to install curl. Please install it manually."
TRANSLATIONS["msg_system_success"]="System check completed successfully."
TRANSLATIONS["msg_install_gh"]="Installing GitHub CLI..."
TRANSLATIONS["msg_install_debian"]="Installing for Debian/Ubuntu..."
TRANSLATIONS["msg_install_fedora"]="Installing for Fedora/RHEL/CentOS..."
TRANSLATIONS["msg_install_suse"]="Installing for openSUSE..."
TRANSLATIONS["msg_install_arch"]="Installing for Arch Linux..."
TRANSLATIONS["msg_install_brew"]="Installing with Homebrew..."
TRANSLATIONS["msg_install_unsupported"]="Unsupported package manager. Please install GitHub CLI manually."
TRANSLATIONS["msg_install_success"]="GitHub CLI installed successfully!"
TRANSLATIONS["msg_install_fail"]="GitHub CLI installation failed. Please try installing manually."
TRANSLATIONS["msg_usage_intro"]="GitHub CLI has been installed. Here are some common commands:"
TRANSLATIONS["msg_auth_section"]="Authentication:"
TRANSLATIONS["msg_repo_section"]="Repository operations:"
TRANSLATIONS["msg_pr_section"]="Pull requests and issues:"
TRANSLATIONS["msg_help_section"]="For more information:"
TRANSLATIONS["msg_docs_link"]="For complete documentation, visit: https://cli.github.com/manual/"
TRANSLATIONS["msg_complete"]="Installation completed successfully!"
TRANSLATIONS["msg_no_pkg_manager"]="No supported package manager found. Please install GitHub CLI manually."

# Add essential core translations for the GPG manager to function
TRANSLATIONS["menu_create_key"]="Create GPG Key"
TRANSLATIONS["menu_list_keys"]="List/View Keys"
TRANSLATIONS["menu_manage_subkeys"]="Manage Subkeys"
TRANSLATIONS["menu_manage_identities"]="Manage Identities"
TRANSLATIONS["menu_export_keys"]="Export Keys"
TRANSLATIONS["menu_import_keys"]="Import Keys"
TRANSLATIONS["menu_revoke_key"]="Revoke Key"
TRANSLATIONS["menu_delete_key"]="Delete Key"
TRANSLATIONS["menu_git_integration"]="Git Integration"
TRANSLATIONS["language_select"]="Select Language"
TRANSLATIONS["menu_exit"]="Exit"

# Keys management section
TRANSLATIONS["keys_management"]="GPG Keys Management"
TRANSLATIONS["list_all_keys"]="List All Keys"
TRANSLATIONS["view_key_details"]="View Key Details"
TRANSLATIONS["back"]="Back"
TRANSLATIONS["show_all_keys"]="Show All Keys"
TRANSLATIONS["show_my_keys"]="Show My Keys"
TRANSLATIONS["show_public_keys"]="Show Public Keys"
TRANSLATIONS["gpg_keys_title"]="GPG Keys"
TRANSLATIONS["my_keys_header"]="My Keys (with Private Key)"
TRANSLATIONS["public_keys_header"]="Public Keys (from Others)"
TRANSLATIONS["key_filter_prompt"]="Filter Keys to Display"

# Import keys section
TRANSLATIONS["import_keys_title"]="Import GPG Keys"
TRANSLATIONS["import_from_file"]="Import from File"
TRANSLATIONS["import_from_keyserver"]="Import from Keyserver"
TRANSLATIONS["import_from_url"]="Import from URL"
TRANSLATIONS["import_from_text"]="Import from Text"
TRANSLATIONS["import_from_qr"]="Import from QR Code"
TRANSLATIONS["import_revocation_cert"]="Import Revocation Certificate"

# Create key section
TRANSLATIONS["create_key_title"]="Create New GPG Key"
TRANSLATIONS["key_type_rsa"]="RSA 4096"
TRANSLATIONS["key_type_ecc"]="ECC (Ed25519)"
TRANSLATIONS["full_name"]="Full Name"
TRANSLATIONS["email_address"]="Email Address"
TRANSLATIONS["comment_optional"]="Comment (Optional)"
TRANSLATIONS["never_expire"]="Never Expire"
TRANSLATIONS["expire_after"]="Expire After..."
TRANSLATIONS["error_name_empty"]="Name cannot be empty"
TRANSLATIONS["error_email_empty"]="Email cannot be empty"
