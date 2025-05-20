#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Binsetup - Script para añadir o quitar el directorio `~/bin` del PATH, temporalmente o de forma persistente.
#
# Copyright (C) 2025 MAURO ROSERO PÉREZ
# License: GPLv3
#
# File: binsetup.sh
# Version: 0.1.0
# Author: Mauro Rosero P. <mauro.rosero@gmail.com>
# Assistant: Cursor AI (https://cursor.com)
# Created: 2025-05-19 20:53:17
#
# This file is managed by template_manager.py.
# Any changes to this header will be overwritten on the next fix.
#
# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

# Función para añadir temporalmente al PATH
add_to_path_temporary() {
    # Add ~/bin to PATH for current session
    export PATH="$HOME/bin:$PATH"
    echo "~/bin added to PATH for current session"
}

remove_from_path_temporary() {
    # Check if ~/bin is in the PATH
    if [[ ":$PATH:" == *":$HOME/bin:"* ]]; then
        # Remove ~/bin from PATH for current session
        export PATH=$(echo "$PATH" | sed -E "s|:?$HOME/bin:?|:|g" | sed -E "s|^:|//|g" | sed -E "s|:$||g" | sed -E "s|//||g")
        echo "~/bin removed from PATH for current session"
    else
        echo "~/bin is not in your current PATH"
    fi
}

add_to_path_persistent() {
    # Check which shell is being used
    local shell_rc=""
    if [ -n "$BASH_VERSION" ]; then
        shell_rc="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        shell_rc="$HOME/.zshrc"
    else
        # Default to .profile for other shells
        shell_rc="$HOME/.profile"
    fi
    
    # Check if PATH already contains ~/bin
    if grep -q "PATH=\"\$HOME/bin:\$PATH\"" "$shell_rc" 2>/dev/null; then
        echo "~/bin is already in your PATH configuration in $shell_rc"
        return
    fi
    
    # Add ~/bin to PATH in shell configuration file
    echo -e "\n# Add ~/bin to PATH\nexport PATH=\"\$HOME/bin:\$PATH\"" >> "$shell_rc"
    echo "~/bin added to PATH permanently in $shell_rc"
    echo "Please run 'source $shell_rc' to apply changes to current session"
}

remove_from_path_persistent() {
    # Check which shell is being used
    local shell_rc=""
    if [ -n "$BASH_VERSION" ]; then
        shell_rc="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        shell_rc="$HOME/.zshrc"
    else
        # Default to .profile for other shells
        shell_rc="$HOME/.profile"
    fi
    
    # Check if file exists
    if [ ! -f "$shell_rc" ]; then
        echo "Configuration file $shell_rc not found"
        return 1
    fi
    
    # Create a backup before making changes
    cp "$shell_rc" "${shell_rc}.bak"
    
    # Remove the ~/bin from PATH configuration
    local removed=0
    if grep -q "PATH=\"\$HOME/bin:\$PATH\"" "$shell_rc"; then
        sed -i '/# Add ~\/bin to PATH/d' "$shell_rc"
        sed -i '/export PATH="\$HOME\/bin:\$PATH"/d' "$shell_rc"
        removed=1
    fi
    
    # Show appropriate message
    if [ $removed -eq 1 ]; then
        echo "~/bin removed from PATH configuration in $shell_rc"
        echo "Please run 'source $shell_rc' to apply changes to current session"
    else
        echo "~/bin configuration not found in $shell_rc"
        # Restore backup if no changes were made
        mv "${shell_rc}.bak" "$shell_rc"
    fi
}

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage:"
    echo "  source $0            - Add ~/bin to PATH for current session only"
    echo "  source $0 --disable  - Remove ~/bin from PATH for current session only"
    echo "  $0 --persistent      - Add ~/bin to PATH permanently"
    echo "  $0 --remove          - Remove ~/bin from PATH configuration permanently"
    echo "  $0 --help            - Show this help message"
    exit 0
fi

# Check if script is being sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    # Script is being sourced
    if [[ "$1" == "--disable" ]]; then
        remove_from_path_temporary
    else
        add_to_path_temporary
    fi
else
    # Script is being executed
    if [[ "$1" == "--persistent" ]]; then
        add_to_path_persistent
    elif [[ "$1" == "--remove" ]]; then
        remove_from_path_persistent
    else
        echo "Usage:"
        echo "  source $0            - Add ~/bin to PATH for current session only"
        echo "  source $0 --disable  - Remove ~/bin from PATH for current session only"
        echo "  $0 --persistent      - Add ~/bin to PATH permanently"
        echo "  $0 --remove          - Remove ~/bin from PATH configuration permanently"
        echo "  $0 --help            - Show this help message"
    fi
fi