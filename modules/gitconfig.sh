#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# gitconfig.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# GPG Console Manager - Git Integration Module
# License: AGPL

# Git integration menu
git_integration_menu() {
  # Check if git is available
  if ! command -v git &> /dev/null; then
    if [ "$LANG_CODE" = "es" ]; then
      gum style --foreground "$COLOR_ERROR" "Git no está instalado. No se puede configurar la integración con Git."
      gum confirm "Presione Enter para continuar" && return
    else
      gum style --foreground "$COLOR_ERROR" "Git is not installed. Cannot configure Git integration."
      gum confirm "Press Enter to continue" && return
    fi
  fi
  
  while true; do
    # Título del menú según idioma
    local menu_title="Git GPG Integration"
    if [ "$LANG_CODE" = "es" ]; then
      menu_title="Integración de Git con GPG"
    fi
    
    gum style \
      --border double \
      --border-foreground "$COLOR_PRIMARY" \
      --padding "1" \
      --width 50 \
      --align center \
      --bold \
      "$menu_title"
    
    # Opciones según idioma
    local opt_identity="Set Git Identity and Signing Key"
    local opt_subkey="Use Subkey for Signing"
    local opt_toggle="Enable/Disable GPG Signing"
    local opt_view="View Current Git GPG Configuration"
    local opt_back="Back"
    
    if [ "$LANG_CODE" = "es" ]; then
      opt_identity="Configurar Identidad y Clave de Firma en Git"
      opt_subkey="Usar Subclave para Firmar"
      opt_toggle="Activar/Desactivar Firma GPG"
      opt_view="Ver Configuración Actual de Git GPG"
      opt_back="Volver"
    fi
    
    local choice=$(gum choose \
      "$opt_identity" \
      "$opt_subkey" \
      "$opt_toggle" \
      "$opt_view" \
      "$opt_back")
    
    case "$choice" in
      "$opt_identity")
        set_git_identity
        ;;
      "$opt_subkey")
        set_git_subkey
        ;;
      "$opt_toggle")
        toggle_git_signing
        ;;
      "$opt_view")
        view_git_gpg_config
        ;;
      "$opt_back")
        return
        ;;
    esac
  done
}

# Configure git with user details and signing key
configure_git() {
  local email="$1"
  local name="$2"
  local key_id="$3"
  local scope=""
  
  if [ -z "$email" ] || [ -z "$name" ] || [ -z "$key_id" ]; then
    # If parameters aren't provided, get them interactively
    set_git_identity
    return
  fi
  
  # Choose configuration scope
  scope=$(gum choose "Global (all repositories)" "Local (current repository only)" "Cancel")
  
  if [ "$scope" = "Cancel" ]; then
    return
  fi
  
  local scope_arg=""
  if [ "$scope" = "Global (all repositories)" ]; then
    scope_arg="--global"
  elif [ "$scope" = "Local (current repository only)" ]; then
    scope_arg="--local"
    
    # Check if current directory is a git repository
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
      gum style --foreground "$COLOR_ERROR" "Current directory is not a git repository"
      gum confirm "Press Enter to continue" && return
    fi
  fi
  
  gum style --foreground "$COLOR_INFO" "Configuring Git with:"
  gum style "Name: $name"
  gum style "Email: $email"
  gum style "Signing Key: $key_id"
  gum style "Scope: ${scope%% *}"
  
  if ! gum confirm "Apply these settings?"; then
    return
  fi
  
  # Configure git
  git config $scope_arg user.name "$name"
  git config $scope_arg user.email "$email"
  git config $scope_arg user.signingkey "$key_id"
  
  # Ask about enabling automatic signing
  if gum confirm "Enable automatic commit signing?"; then
    git config $scope_arg commit.gpgsign true
    git config $scope_arg tag.gpgsign true
  fi
  
  gum style --foreground "$COLOR_SUCCESS" "✓ Git configured successfully"
  gum confirm "Press Enter to continue" && return
}

# Configure git to use a specific subkey for signing
set_git_subkey() {
  # Choose configuration scope
  local scope=$(gum choose "Global (all repositories)" "Local (current repository only)" "Cancel")
  
  if [ "$scope" = "Cancel" ]; then
    return
  fi
  
  local scope_arg=""
  if [ "$scope" = "Global (all repositories)" ]; then
    scope_arg="--global"
  elif [ "$scope" = "Local (current repository only)" ]; then
    scope_arg="--local"
    
    # Check if current directory is a git repository
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
      gum style --foreground "$COLOR_ERROR" "Current directory is not a git repository"
      gum confirm "Press Enter to continue" && return
    fi
  fi
  
  # First, select a primary key
  gum style --foreground "$COLOR_INFO" "First, select the primary key that contains your subkeys"
  local primary_key=$(select_key "Select primary key")
  
  if [ -z "$primary_key" ]; then
    return
  fi
  
  # Get subkeys for the selected primary key
  local subkeys_raw=$(gpg --list-keys --with-colons "$primary_key" | grep -E "^sub|^ssb")
  
  if [ -z "$subkeys_raw" ]; then
    gum style --foreground "$COLOR_ERROR" "No subkeys found for this primary key"
    gum style --foreground "$COLOR_INFO" "Create subkeys first before trying to use them for signing"
    gum confirm "Press Enter to continue" && return
  fi
  
  # Parse subkeys into arrays
  local subkey_ids=()
  local subkey_info=()
  
  while IFS='' read -r line; do
    local rec_type=${line%%:*}
    local key_id=$(echo "$line" | cut -d: -f5)
    local created=$(echo "$line" | cut -d: -f6)
    local capabilities=$(echo "$line" | cut -d: -f12)
    local created_date=$(date -d @"$created" +"%Y-%m-%d" 2>/dev/null || date -r "$created" +"%Y-%m-%d" 2>/dev/null)
    
    # Only show subkeys that have signing capability
    if [[ "$capabilities" == *"s"* ]]; then
      subkey_ids+=("$key_id")
      
      # Map capability flags to descriptions
      local cap_desc=""
      [[ "$capabilities" == *"s"* ]] && cap_desc="${cap_desc}Sign "
      [[ "$capabilities" == *"e"* ]] && cap_desc="${cap_desc}Encrypt "
      [[ "$capabilities" == *"a"* ]] && cap_desc="${cap_desc}Auth "
      [[ "$capabilities" == *"c"* ]] && cap_desc="${cap_desc}Cert "
      
      # Get the fingerprint
      local subkey_fpr=""
      local next_line=""
      if read -r next_line <<< "$(gpg --list-keys --with-colons "$primary_key" | grep -A 1 "${key_id}" | tail -n 1)"; then
        if [[ "${next_line%%:*}" = "fpr" ]]; then
          subkey_fpr=$(echo "$next_line" | cut -d: -f10)
        fi
      fi
      
      local fpr_display=""
      if [ -n "$subkey_fpr" ]; then
        fpr_display=" [${subkey_fpr:(-8)}]"
      fi
      
      subkey_info+=("$key_id (${cap_desc:0:-1}, created $created_date)$fpr_display")
    fi
  done <<< "$subkeys_raw"
  
  if [ ${#subkey_ids[@]} -eq 0 ]; then
    gum style --foreground "$COLOR_ERROR" "No signing subkeys found for this primary key"
    gum style --foreground "$COLOR_INFO" "Only subkeys with signing capability can be used"
    gum confirm "Press Enter to continue" && return
  fi
  
  # Add a "Back" option
  subkey_info+=("Cancel")
  
  # Let user select a subkey
  local selection=$(gum choose --header "Select signing subkey" "${subkey_info[@]}")
  
  if [ "$selection" = "Cancel" ]; then
    return
  fi
  
  # Extract subkey ID from selection
  local subkey_id=$(echo "$selection" | cut -d' ' -f1)
  
  # Get the parent key's email to configure Git user.email
  local key_info=$(gpg --list-keys --with-colons "$primary_key" | grep "^uid" | head -n 1)
  local uid=$(echo "$key_info" | cut -d: -f10)
  
  # Extract name and email using regex
  local name=$(echo "$uid" | sed -E 's/([^<]*)<.*>/\1/' | xargs)
  local email=$(echo "$uid" | grep -o '<[^>]*>' | tr -d '<>')
  
  # For the signing key, we'll use the format "KEYID!" which tells Git to use a specific subkey
  local signing_key="${subkey_id}!"
  
  gum style --foreground "$COLOR_INFO" "Configuring Git with:"
  gum style "Name: $name"
  gum style "Email: $email"
  gum style "Signing Subkey: $signing_key"
  gum style "Scope: ${scope%% *}"
  
  # Allow user to modify details if needed
  if gum confirm "Modify these details?"; then
    name=$(gum input --placeholder "Name" --value "$name")
    email=$(gum input --placeholder "Email" --value "$email")
  fi
  
  if ! gum confirm "Apply these settings?"; then
    return
  fi
  
  # Configure git
  git config $scope_arg user.name "$name"
  git config $scope_arg user.email "$email"
  git config $scope_arg user.signingkey "$signing_key"
  
  # Ask about enabling automatic signing
  if gum confirm "Enable automatic commit signing?"; then
    git config $scope_arg commit.gpgsign true
    git config $scope_arg tag.gpgsign true
  fi
  
  gum style --foreground "$COLOR_SUCCESS" "✓ Git configured with signing subkey"
  gum confirm "Press Enter to continue" && return
}

# Set git identity and signing key
set_git_identity() {
  # Choose configuration scope
  local scope=$(gum choose "Global (all repositories)" "Local (current repository only)" "Cancel")
  
  if [ "$scope" = "Cancel" ]; then
    return
  fi
  
  local scope_arg=""
  if [ "$scope" = "Global (all repositories)" ]; then
    scope_arg="--global"
  elif [ "$scope" = "Local (current repository only)" ]; then
    scope_arg="--local"
    
    # Check if current directory is a git repository
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
      gum style --foreground "$COLOR_ERROR" "Current directory is not a git repository"
      gum confirm "Press Enter to continue" && return
    fi
  fi
  
  # Select a key for signing
  local key_id=$(select_key "Select GPG key for Git signing")
  
  if [ -z "$key_id" ]; then
    return
  fi
  
  # Get associated email and name for the key
  local key_info=$(gpg --list-keys --with-colons "$key_id" | grep "^uid" | head -n 1)
  local uid=$(echo "$key_info" | cut -d: -f10)
  
  # Extract name and email using regex
  local name=$(echo "$uid" | sed -E 's/([^<]*)<.*>/\1/' | xargs)
  local email=$(echo "$uid" | grep -o '<[^>]*>' | tr -d '<>')
  
  gum style --foreground "$COLOR_INFO" "Configuring Git with:"
  gum style "Name: $name"
  gum style "Email: $email"
  gum style "Signing Key: $key_id"
  gum style "Scope: ${scope%% *}"
  
  # Allow user to modify details if needed
  if gum confirm "Modify these details?"; then
    name=$(gum input --placeholder "Name" --value "$name")
    email=$(gum input --placeholder "Email" --value "$email")
  fi
  
  if ! gum confirm "Apply these settings?"; then
    return
  fi
  
  # Configure git
  git config $scope_arg user.name "$name"
  git config $scope_arg user.email "$email"
  git config $scope_arg user.signingkey "$key_id"
  
  # Ask about enabling automatic signing
  if gum confirm "Enable automatic commit signing?"; then
    git config $scope_arg commit.gpgsign true
    git config $scope_arg tag.gpgsign true
  fi
  
  gum style --foreground "$COLOR_SUCCESS" "✓ Git configured successfully"
  gum confirm "Press Enter to continue" && return
}

# Configure git to use a specific subkey for signing
set_git_subkey() {
  # Choose configuration scope
  local scope=$(gum choose "Global (all repositories)" "Local (current repository only)" "Cancel")
  
  if [ "$scope" = "Cancel" ]; then
    return
  fi
  
  local scope_arg=""
  if [ "$scope" = "Global (all repositories)" ]; then
    scope_arg="--global"
  elif [ "$scope" = "Local (current repository only)" ]; then
    scope_arg="--local"
    
    # Check if current directory is a git repository
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
      gum style --foreground "$COLOR_ERROR" "Current directory is not a git repository"
      gum confirm "Press Enter to continue" && return
    fi
  fi
  
  # First, select a primary key
  gum style --foreground "$COLOR_INFO" "First, select the primary key that contains your subkeys"
  local primary_key=$(select_key "Select primary key")
  
  if [ -z "$primary_key" ]; then
    return
  fi
  
  # Get subkeys for the selected primary key
  local subkeys_raw=$(gpg --list-keys --with-colons "$primary_key" | grep -E "^sub|^ssb")
  
  if [ -z "$subkeys_raw" ]; then
    gum style --foreground "$COLOR_ERROR" "No subkeys found for this primary key"
    gum style --foreground "$COLOR_INFO" "Create subkeys first before trying to use them for signing"
    gum confirm "Press Enter to continue" && return
  fi
  
  # Parse subkeys into arrays
  local subkey_ids=()
  local subkey_info=()
  
  while IFS='' read -r line; do
    local rec_type=${line%%:*}
    local key_id=$(echo "$line" | cut -d: -f5)
    local created=$(echo "$line" | cut -d: -f6)
    local capabilities=$(echo "$line" | cut -d: -f12)
    local created_date=$(date -d @"$created" +"%Y-%m-%d" 2>/dev/null || date -r "$created" +"%Y-%m-%d" 2>/dev/null)
    
    # Only show subkeys that have signing capability
    if [[ "$capabilities" == *"s"* ]]; then
      subkey_ids+=("$key_id")
      
      # Map capability flags to descriptions
      local cap_desc=""
      [[ "$capabilities" == *"s"* ]] && cap_desc="${cap_desc}Sign "
      [[ "$capabilities" == *"e"* ]] && cap_desc="${cap_desc}Encrypt "
      [[ "$capabilities" == *"a"* ]] && cap_desc="${cap_desc}Auth "
      [[ "$capabilities" == *"c"* ]] && cap_desc="${cap_desc}Cert "
      
      # Get the fingerprint
      local subkey_fpr=""
      local next_line=""
      if read -r next_line <<< "$(gpg --list-keys --with-colons "$primary_key" | grep -A 1 "${key_id}" | tail -n 1)"; then
        if [[ "${next_line%%:*}" = "fpr" ]]; then
          subkey_fpr=$(echo "$next_line" | cut -d: -f10)
        fi
      fi
      
      local fpr_display=""
      if [ -n "$subkey_fpr" ]; then
        fpr_display=" [${subkey_fpr:(-8)}]"
      fi
      
      subkey_info+=("$key_id (${cap_desc:0:-1}, created $created_date)$fpr_display")
    fi
  done <<< "$subkeys_raw"
  
  if [ ${#subkey_ids[@]} -eq 0 ]; then
    gum style --foreground "$COLOR_ERROR" "No signing subkeys found for this primary key"
    gum style --foreground "$COLOR_INFO" "Only subkeys with signing capability can be used"
    gum confirm "Press Enter to continue" && return
  fi
  
  # Add a "Back" option
  subkey_info+=("Cancel")
  
  # Let user select a subkey
  local selection=$(gum choose --header "Select signing subkey" "${subkey_info[@]}")
  
  if [ "$selection" = "Cancel" ]; then
    return
  fi
  
  # Extract subkey ID from selection
  local subkey_id=$(echo "$selection" | cut -d' ' -f1)
  
  # Get the parent key's email to configure Git user.email
  local key_info=$(gpg --list-keys --with-colons "$primary_key" | grep "^uid" | head -n 1)
  local uid=$(echo "$key_info" | cut -d: -f10)
  
  # Extract name and email using regex
  local name=$(echo "$uid" | sed -E 's/([^<]*)<.*>/\1/' | xargs)
  local email=$(echo "$uid" | grep -o '<[^>]*>' | tr -d '<>')
  
  # For the signing key, we'll use the format "KEYID!" which tells Git to use a specific subkey
  local signing_key="${subkey_id}!"
  
  gum style --foreground "$COLOR_INFO" "Configuring Git with:"
  gum style "Name: $name"
  gum style "Email: $email"
  gum style "Signing Subkey: $signing_key"
  gum style "Scope: ${scope%% *}"
  
  # Allow user to modify details if needed
  if gum confirm "Modify these details?"; then
    name=$(gum input --placeholder "Name" --value "$name")
    email=$(gum input --placeholder "Email" --value "$email")
  fi
  
  if ! gum confirm "Apply these settings?"; then
    return
  fi
  
  # Configure git
  git config $scope_arg user.name "$name"
  git config $scope_arg user.email "$email"
  git config $scope_arg user.signingkey "$signing_key"
  
  # Ask about enabling automatic signing
  if gum confirm "Enable automatic commit signing?"; then
    git config $scope_arg commit.gpgsign true
    git config $scope_arg tag.gpgsign true
  fi
  
  gum style --foreground "$COLOR_SUCCESS" "✓ Git configured with signing subkey"
  gum confirm "Press Enter to continue" && return
}

# Toggle Git GPG signing
toggle_git_signing() {
  # Choose configuration scope
  local scope=$(gum choose "Global (all repositories)" "Local (current repository only)" "Cancel")
  
  if [ "$scope" = "Cancel" ]; then
    return
  fi
  
  local scope_arg=""
  if [ "$scope" = "Global (all repositories)" ]; then
    scope_arg="--global"
  elif [ "$scope" = "Local (current repository only)" ]; then
    scope_arg="--local"
    
    # Check if current directory is a git repository
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
      gum style --foreground "$COLOR_ERROR" "Current directory is not a git repository"
      gum confirm "Press Enter to continue" && return
    fi
  fi
  
  # Get current signing status
  local current_commit_sign=$(git config $scope_arg --get commit.gpgsign)
  local current_tag_sign=$(git config $scope_arg --get tag.gpgsign)
  
  local current_status="disabled"
  if [ "$current_commit_sign" = "true" ]; then
    current_status="enabled"
  fi
  
  gum style "Current signing status: $current_status"
  
  local toggle_action="Enable"
  if [ "$current_status" = "enabled" ]; then
    toggle_action="Disable"
  fi
  
  local choice=$(gum choose "$toggle_action automatic signing" "Cancel")
  
  if [ "$choice" = "Cancel" ]; then
    return
  fi
  
  # Make sure user has a signing key configured
  local signing_key=$(git config $scope_arg --get user.signingkey)
  
  if [ "$toggle_action" = "Enable" ] && [ -z "$signing_key" ]; then
    gum style --foreground "$COLOR_WARNING" "No signing key configured. Please set a signing key first."
    
    if gum confirm "Configure signing key now?"; then
      set_git_identity
      return
    else
      return
    fi
  fi
  
  # Toggle signing
  local new_value="true"
  if [ "$toggle_action" = "Disable" ]; then
    new_value="false"
  fi
  
  git config $scope_arg commit.gpgsign $new_value
  git config $scope_arg tag.gpgsign $new_value
  
  gum style --foreground "$COLOR_SUCCESS" "✓ Automatic signing $toggle_action"d
  gum confirm "Press Enter to continue" && return
}

# View current Git GPG configuration
view_git_gpg_config() {
  # Choose configuration scope
  local scope=$(gum choose "Global (all repositories)" "Local (current repository only)" "Both" "Cancel")
  
  if [ "$scope" = "Cancel" ]; then
    return
  fi
  
  # Título según idioma
  local config_title="Git GPG Configuration"
  if [ "$LANG_CODE" = "es" ]; then
    config_title="Configuración GPG de Git"
  fi
  
  gum style \
    --border rounded \
    --border-foreground "$COLOR_PRIMARY" \
    --padding "1" \
    --width 60 \
    --align center \
    --bold \
    "$config_title"
  
  if [ "$scope" = "Global (all repositories)" ] || [ "$scope" = "Both" ]; then
    gum style --foreground "$COLOR_INFO" --bold --underline "Global Configuration"
    gum style --foreground "$COLOR_INFO" "User Name:     $(git config --global --get user.name || echo "(not set)")"
    gum style --foreground "$COLOR_INFO" "User Email:    $(git config --global --get user.email || echo "(not set)")"
    gum style --foreground "$COLOR_INFO" "Signing Key:   $(git config --global --get user.signingkey || echo "(not set)")"
    
    local global_sign_key=$(git config --global --get user.signingkey)
    
    # Check if this is a subkey (ends with !)
    if [[ "$global_sign_key" == *! ]]; then
      gum style --foreground "$COLOR_INFO" "Using Subkey:  Yes (subkey of $(echo $global_sign_key | tr -d '!'))"
    fi
    
    gum style --foreground "$COLOR_INFO" "Commit Sign:   $(git config --global --get commit.gpgsign || echo "(not set)")"
    gum style --foreground "$COLOR_INFO" "Tag Sign:      $(git config --global --get tag.gpgsign || echo "(not set)")"
    gum style --foreground "$COLOR_INFO" "GPG Program:   $(git config --global --get gpg.program || echo "(default)")"
    echo ""
  fi
  
  if [ "$scope" = "Local (current repository only)" ] || [ "$scope" = "Both" ]; then
    # Check if current directory is a git repository
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
      gum style --foreground "$COLOR_ERROR" "Current directory is not a git repository"
    else
      gum style --foreground "$COLOR_INFO" --bold --underline "Local Repository Configuration"
      gum style --foreground "$COLOR_INFO" "Repository:    $(basename $(git rev-parse --show-toplevel))"
      gum style --foreground "$COLOR_INFO" "User Name:     $(git config --local --get user.name || echo "(not set, using global)")"
      gum style --foreground "$COLOR_INFO" "User Email:    $(git config --local --get user.email || echo "(not set, using global)")"
      gum style --foreground "$COLOR_INFO" "Signing Key:   $(git config --local --get user.signingkey || echo "(not set, using global)")"
      
      local local_sign_key=$(git config --local --get user.signingkey)
      
      # Check if this is a subkey (ends with !)
      if [[ "$local_sign_key" == *! ]]; then
        local subkey_id=$(echo $local_sign_key | tr -d '!')
        gum style --foreground "$COLOR_INFO" "Using Subkey:  Yes (subkey ID: $subkey_id)"
      fi
      
      gum style --foreground "$COLOR_INFO" "Commit Sign:   $(git config --local --get commit.gpgsign || echo "(not set, using global)")"
      gum style --foreground "$COLOR_INFO" "Tag Sign:      $(git config --local --get tag.gpgsign || echo "(not set, using global)")"
    fi
  fi
  
  echo ""
  gum confirm "Press Enter to continue" && return
}

# Configure git to use a specific subkey for signing
set_git_subkey() {
  # Choose configuration scope
  local scope=$(gum choose "Global (all repositories)" "Local (current repository only)" "Cancel")
  
  if [ "$scope" = "Cancel" ]; then
    return
  fi
  
  local scope_arg=""
  if [ "$scope" = "Global (all repositories)" ]; then
    scope_arg="--global"
  elif [ "$scope" = "Local (current repository only)" ]; then
    scope_arg="--local"
    
    # Check if current directory is a git repository
    if ! git rev-parse --is-inside-work-tree &> /dev/null; then
      gum style --foreground "$COLOR_ERROR" "Current directory is not a git repository"
      gum confirm "Press Enter to continue" && return
    fi
  fi
  
  # First, select a primary key
  gum style --foreground "$COLOR_INFO" "First, select the primary key that contains your subkeys"
  local primary_key=$(select_key "Select primary key")
  
  if [ -z "$primary_key" ]; then
    return
  fi
  
  # Get subkeys for the selected primary key
  local subkeys_raw=$(gpg --list-keys --with-colons "$primary_key" | grep -E "^sub|^ssb")
  
  if [ -z "$subkeys_raw" ]; then
    gum style --foreground "$COLOR_ERROR" "No subkeys found for this primary key"
    gum style --foreground "$COLOR_INFO" "Create subkeys first before trying to use them for signing"
    gum confirm "Press Enter to continue" && return
  fi
  
  # Parse subkeys into arrays
  local subkey_ids=()
  local subkey_info=()
  
  while IFS='' read -r line; do
    local rec_type=${line%%:*}
    local key_id=$(echo "$line" | cut -d: -f5)
    local created=$(echo "$line" | cut -d: -f6)
    local capabilities=$(echo "$line" | cut -d: -f12)
    local created_date=$(date -d @"$created" +"%Y-%m-%d" 2>/dev/null || date -r "$created" +"%Y-%m-%d" 2>/dev/null)
    
    # Only show subkeys that have signing capability
    if [[ "$capabilities" == *"s"* ]]; then
      subkey_ids+=("$key_id")
      
      # Map capability flags to descriptions
      local cap_desc=""
      [[ "$capabilities" == *"s"* ]] && cap_desc="${cap_desc}Sign "
      [[ "$capabilities" == *"e"* ]] && cap_desc="${cap_desc}Encrypt "
      [[ "$capabilities" == *"a"* ]] && cap_desc="${cap_desc}Auth "
      [[ "$capabilities" == *"c"* ]] && cap_desc="${cap_desc}Cert "
      
      # Get the fingerprint
      local subkey_fpr=""
      local next_line=""
      if read -r next_line <<< "$(gpg --list-keys --with-colons "$primary_key" | grep -A 1 "${key_id}" | tail -n 1)"; then
        if [[ "${next_line%%:*}" = "fpr" ]]; then
          subkey_fpr=$(echo "$next_line" | cut -d: -f10)
        fi
      fi
      
      local fpr_display=""
      if [ -n "$subkey_fpr" ]; then
        fpr_display=" [${subkey_fpr:(-8)}]"
      fi
      
      subkey_info+=("$key_id (${cap_desc:0:-1}, created $created_date)$fpr_display")
    fi
  done <<< "$subkeys_raw"
  
  if [ ${#subkey_ids[@]} -eq 0 ]; then
    gum style --foreground "$COLOR_ERROR" "No signing subkeys found for this primary key"
    gum style --foreground "$COLOR_INFO" "Only subkeys with signing capability can be used"
    gum confirm "Press Enter to continue" && return
  fi
  
  # Add a "Back" option
  subkey_info+=("Cancel")
  
  # Let user select a subkey
  local selection=$(gum choose --header "Select signing subkey" "${subkey_info[@]}")
  
  if [ "$selection" = "Cancel" ]; then
    return
  fi
  
  # Extract subkey ID from selection
  local subkey_id=$(echo "$selection" | cut -d' ' -f1)
  
  # Get the parent key's email to configure Git user.email
  local key_info=$(gpg --list-keys --with-colons "$primary_key" | grep "^uid" | head -n 1)
  local uid=$(echo "$key_info" | cut -d: -f10)
  
  # Extract name and email using regex
  local name=$(echo "$uid" | sed -E 's/([^<]*)<.*>/\1/' | xargs)
  local email=$(echo "$uid" | grep -o '<[^>]*>' | tr -d '<>')
  
  # For the signing key, we'll use the format "KEYID!" which tells Git to use a specific subkey
  local signing_key="${subkey_id}!"
  
  gum style --foreground "$COLOR_INFO" "Configuring Git with:"
  gum style "Name: $name"
  gum style "Email: $email"
  gum style "Signing Subkey: $signing_key"
  gum style "Scope: ${scope%% *}"
  
  # Allow user to modify details if needed
  if gum confirm "Modify these details?"; then
    name=$(gum input --placeholder "Name" --value "$name")
    email=$(gum input --placeholder "Email" --value "$email")
  fi
  
  if ! gum confirm "Apply these settings?"; then
    return
  fi
  
  # Configure git
  git config $scope_arg user.name "$name"
  git config $scope_arg user.email "$email"
  git config $scope_arg user.signingkey "$signing_key"
  
  # Ask about enabling automatic signing
  if gum confirm "Enable automatic commit signing?"; then
    git config $scope_arg commit.gpgsign true
    git config $scope_arg tag.gpgsign true
  fi
  
  gum style --foreground "$COLOR_SUCCESS" "✓ Git configured with signing subkey"
  gum confirm "Press Enter to continue" && return
}
