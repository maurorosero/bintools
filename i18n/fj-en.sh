#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# fj-en.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# English language file for Forgejo CLI Installer
# License: AGPL-3.0

# Color settings using unique names to avoid conflicts with common.sh
TERM_COLOR_INFO="\033[1;34m"    # Bold Blue
TERM_COLOR_SUCCESS="\033[1;32m" # Bold Green
TERM_COLOR_WARNING="\033[1;33m" # Bold Yellow
TERM_COLOR_ERROR="\033[1;31m"   # Bold Red
TERM_COLOR_RESET="\033[0m"      # Reset color

# Register translations in the TRANSLATIONS associative array
TRANSLATIONS["msg_banner_title"]="Forgejo CLI Installer"
TRANSLATIONS["msg_banner_subtitle"]="MR*Developer Tools"
TRANSLATIONS["msg_start"]="Starting Forgejo CLI installation..."
TRANSLATIONS["msg_root_required"]="This script requires root privileges for installation."
TRANSLATIONS["msg_root_attempt"]="Attempting to escalate privileges..."
TRANSLATIONS["msg_root_unavailable"]="Sudo is not available. Please run this script as root."
TRANSLATIONS["msg_check_system"]="Checking system requirements..."
TRANSLATIONS["msg_pkg_detected"]="Package manager detected:"
TRANSLATIONS["msg_install_rust"]="Installing Rust toolchain..."
TRANSLATIONS["msg_rust_fail"]="Failed to install Rust. Please install it manually."
TRANSLATIONS["msg_system_success"]="System check completed successfully."
TRANSLATIONS["msg_install_berg"]="Installing Forgejo CLI (berg)..."
TRANSLATIONS["msg_install_cargo"]="Installing with cargo..."
TRANSLATIONS["msg_install_unsupported"]="Unsupported system. Please install Forgejo CLI manually."
TRANSLATIONS["msg_install_success"]="Forgejo CLI installed successfully!"
TRANSLATIONS["msg_install_fail"]="Forgejo CLI installation failed. Please try installing manually."
TRANSLATIONS["msg_usage_intro"]="Forgejo CLI has been installed. Here are some common commands:"
TRANSLATIONS["msg_auth_section"]="Authentication:"
TRANSLATIONS["msg_repo_section"]="Repository operations:"
TRANSLATIONS["msg_pr_section"]="Pull requests and issues:"
TRANSLATIONS["msg_help_section"]="For more information:"
TRANSLATIONS["msg_docs_link"]="For complete documentation, run: berg --help"
TRANSLATIONS["msg_complete"]="Installation completed successfully!"
TRANSLATIONS["msg_no_rust"]="Rust toolchain not found. Please install Rust before continuing."
