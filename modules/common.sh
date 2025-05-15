#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# common.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# GPG Console Manager - Common Functions Library
# License: AGPL-3.0

# Colores y formatos (añadir al inicio de la sección Variables globales)
COLOR_GREEN="\033[0;32m"
COLOR_YELLOW="\033[0;33m"
COLOR_RED="\033[0;31m"
COLOR_CYAN="\033[0;36m"
COLOR_BLUE="\033[0;34m"
COLOR_MAGENTA="\033[0;35m"
COLOR_RESET="\033[0m"
BOLD="\033[1m"

# Initialize translations array if not already initialized
if ! declare -p TRANSLATIONS &>/dev/null; then
  # Export the variable to make sure it's at global scope
  export TRANSLATIONS
  # Declare as global associative array
  declare -gA TRANSLATIONS
fi

# Error codes
readonly ERR_SUCCESS=0
readonly ERR_MISSING_DEPS=1
readonly ERR_NO_KEYS=2
readonly ERR_USER_CANCEL=3
readonly ERR_OPERATION_FAILED=4
readonly ERR_INVALID_INPUT=5

# Color codes for gum - chosen for good visibility on both light and dark backgrounds
# Magenta shades - good contrast on both light/dark
readonly COLOR_PRIMARY=135      # A medium purple that works well on both backgrounds
# Green/Red/Yellow shades - high contrast
readonly COLOR_SUCCESS=35       # A medium green that's visible on both backgrounds
readonly COLOR_ERROR=160        # A muted red visible on both backgrounds
readonly COLOR_WARNING=178      # An amber color visible on both backgrounds
# Info and key colors - neutral tones
readonly COLOR_INFO=67          # A blue-ish gray visible on both backgrounds
readonly COLOR_OWN_KEY=172      # A soft orange for own keys - good contrast
readonly COLOR_PUBLIC_KEY=67    # A subdued blue for public keys

# Common Functions

# Check dependencies
# Usage: check_dependencies
# Description: Verifies that required dependencies are installed
# Returns: 0 if all dependencies are present, 1 otherwise
check_dependencies() {
  local missing_deps=false
  
  if ! command -v gpg &> /dev/null; then
    gum style --foreground "$COLOR_ERROR" "Error: gpg is not installed"
    missing_deps=true
  fi
  
  if ! command -v gum &> /dev/null; then
    echo "Error: gum is not installed"
    echo "Visit https://github.com/charmbracelet/gum for installation instructions"
    missing_deps=true
  fi
  
  if ! command -v git &> /dev/null; then
    gum style --foreground "$COLOR_WARNING" "Warning: git is not installed. Git integration will not be available."
  fi
  
  if [ "$missing_deps" = true ]; then
    return "$ERR_MISSING_DEPS"
  fi
  
  return "$ERR_SUCCESS"
}

# Select a key
# Usage: select_key "prompt text"
# Description: Displays a list of GPG keys for user selection
# Arguments:
#   $1: Prompt text to display
# Returns: Selected key ID or empty string if canceled
select_key() {
  local prompt="$1"
  if [ -z "$prompt" ]; then
    prompt="Select a key"
  fi
  
  # Get secret keys first (keys with private components) for distinguishing own keys
  local secret_keys_raw=$(gpg --list-secret-keys --with-colons 2>/dev/null)
  local secret_key_ids=()
  
  # Extract secret key IDs to identify own keys
  if [ -n "$secret_keys_raw" ]; then
    while IFS='' read -r line; do
      local rec_type=${line%%:*}
      if [ "$rec_type" = "sec" ]; then
        local key_id=$(echo "$line" | cut -d: -f5)
        secret_key_ids+=("$key_id")
      fi
    done <<< "$secret_keys_raw"
  fi
  
  # Get all keys
  local keys_out=$(gpg --list-keys --with-colons)
  local key_ids=()
  local key_uids=()
  local key_types=()  # To indicate if a key is own key or public
  local current_key=""
  
  while IFS='' read -r line; do
    local rec_type=${line%%:*}
    
    if [ "$rec_type" = "pub" ]; then
      current_key=$(echo "$line" | cut -d: -f5)
    elif [ "$rec_type" = "uid" ] && [ -n "$current_key" ]; then
      key_ids+=("$current_key")
      key_uids+=("$(echo "$line" | cut -d: -f10)")
      
      # Check if this is our own key (has a private key)
      local is_own_key=false
      for secret_id in "${secret_key_ids[@]}"; do
        if [ "$current_key" = "$secret_id" ]; then
          is_own_key=true
          break
        fi
      done
      
      if [ "$is_own_key" = true ]; then
        key_types+=("own")
      else
        key_types+=("public")
      fi
      
      current_key=""
    fi
  done <<< "$keys_out"
  
  if [ ${#key_ids[@]} -eq 0 ]; then
    gum style --foreground "$COLOR_ERROR" "No GPG keys found"
    return ""
  fi
  
  # Build options for gum choose with color coding for own vs public keys
  local options=()
  local options_header="Select a key"
  
  # Option for showing only certain types of keys
  local filter_type=""
  local filter_options=("$(_t "show_all_keys")" "$(_t "show_my_keys")" "$(_t "show_public_keys")")
  local filter_selection=$(gum choose --header "$(_t "key_filter_prompt")" "${filter_options[@]}")
  
  case "$filter_selection" in
    "$(_t "show_my_keys")")
      filter_type="own"
      options_header="$(_t "select_key_prompt" "$prompt" "$(_t "showing_own")")"
      ;;
    "$(_t "show_public_keys")")
      filter_type="public" 
      options_header="$(_t "select_key_prompt" "$prompt" "$(_t "showing_public")")"
      ;;
    *)
      options_header="$(_t "select_key_prompt" "$prompt" "$(_t "showing_all")")"
      ;;
  esac
  
  # Add keys based on filter
  for i in "${!key_ids[@]}"; do
    # Skip keys that don't match the filter
    if [ -n "$filter_type" ] && [ "${key_types[$i]}" != "$filter_type" ]; then
      continue
    fi
    
    # Format key entries based on key type (own or public)
    if [ "${key_types[$i]}" = "own" ]; then
      # Format own keys with the key ID as identifier
      local key_id_short="${key_ids[$i]:(-8)}" # Use last 8 characters of key ID
      options+=("$(gum style --foreground "$COLOR_OWN_KEY" "[${key_id_short}] ${key_uids[$i]} (${key_ids[$i]})")")
    else
      # Format public keys normally
      options+=("${key_uids[$i]} (${key_ids[$i]})")
    fi
  done
  
  if [ ${#options[@]} -eq 0 ]; then
    gum style --foreground "$COLOR_ERROR" "No keys match the selected filter"
    return ""
  fi
  
  options+=("Cancel")
  
  # Let user select a key
  local selection=$(gum choose --header "$options_header" "${options[@]}")
  
  if [ "$selection" = "Cancel" ]; then
    return ""
  fi
  
  # Extract key ID from selection (get what's inside the last parentheses)
  # The format is either:
  # 1. For own keys: "[A1E9DB07] Mauro Rosero (DEVOPS) <email@example.com> (A17ADF8EA1E9DB07)"
  # 2. For public keys: "Richard Stallman <rms@gnu.org> (2C6464AF2A8E4C02)"
  # We want to extract what's in the last parentheses pair
  local key_id=$(echo "$selection" | grep -o '([A-Z0-9]*)$' | tr -d '()')
  echo "$key_id"
}

# Display a confirmation prompt
# Usage: confirm_continue
# Description: Shows a confirmation prompt to continue
# Returns: 0 if confirmed, 1 if canceled
confirm_continue() {
  gum confirm "$(_t "press_enter")" && return "$ERR_SUCCESS" || return "$ERR_USER_CANCEL"
}

# Display welcome message
# Usage: display_welcome
# Description: Shows a formatted welcome message
display_welcome() {
  clear
  # Ancho deseado (aproximado)
  local width=50

  # Línea superior
  printf '+%*s+
' "$width" '' | tr ' ' '-'

  # Título centrado
  local title_len=${#APP_NAME}
  local title_pad=$(( (width - title_len) / 2 ))
  printf '|%*s%s%*s|
' "$title_pad" '' "$APP_NAME" "$((width - title_pad - title_len))" ''

  # Separador
  printf '|%*s|
' "$width" ''

  # Versión alineada
  local version_text="Version: $APP_VERSION"
  local version_len=${#version_text}
  local version_pad=$((width - version_len - 1))
  printf '| %s%*s|
' "$version_text" "$version_pad" ''

  # Autor alineado
  local author_text="By: $APP_AUTHOR"
  local author_len=${#author_text}
  local author_pad=$((width - author_len - 1))
  printf '| %s%*s|
' "$author_text" "$author_pad" ''

  # Línea inferior
  printf '+%*s+
' "$width" '' | tr ' ' '-'

  echo # Línea en blanco después del banner
}

# Format a date from unix timestamp
# Usage: format_date <timestamp>
# Description: Formats a unix timestamp to a readable date
# Arguments:
#   $1: Unix timestamp
# Returns: Formatted date string
format_date() {
  local timestamp="$1"
  
  if [ "$timestamp" = "0" ]; then
    echo "$(_t "never_expires")"
  else
    date -d @"$timestamp" +"%Y-%m-%d" 2>/dev/null || date -r "$timestamp" +"%Y-%m-%d" 2>/dev/null
  fi
}

# Display a section header
# Usage: section_header <text> [color] [subtitle]
# Description: Shows a formatted section header
# Arguments:
#   $1: Header text
#   $2: Color (optional, defaults to primary color)
#   $3: Subtitle (optional)
section_header() {
  local text="$1"
  local color="${2:-$COLOR_PRIMARY}"
  local subtitle="${3:-}"
  
  # Clear screen for clean display
  clear
  
  if [ -n "$subtitle" ]; then
    gum style \
      --border double \
      --border-foreground "$color" \
      --padding "1" \
      --width 60 \
      --align center \
      --bold \
      "$text" \
      "$subtitle"
  else
    gum style \
      --border double \
      --border-foreground "$color" \
      --padding "1" \
      --width 60 \
      --align center \
      --bold \
      "$text"
  fi
  
  # Add a little space after the header
  echo ""
}

# Convert GPG capability flags to descriptions
# Usage: get_capability_desc <flags>
# Description: Converts GPG capability flags to human-readable descriptions
# Arguments:
#   $1: Capability flags string
# Returns: Human-readable capability description
get_capability_desc() {
  local capabilities="$1"
  local cap_desc=""
  
  [[ "$capabilities" == *"s"* ]] && cap_desc="${cap_desc}$(_t "capability_sign") "
  [[ "$capabilities" == *"e"* ]] && cap_desc="${cap_desc}$(_t "capability_encrypt") "
  [[ "$capabilities" == *"a"* ]] && cap_desc="${cap_desc}$(_t "capability_auth") "
  [[ "$capabilities" == *"c"* ]] && cap_desc="${cap_desc}$(_t "capability_cert") "
  
  # Remove trailing space
  echo "${cap_desc:0:-1}"
}

# Display a success message
# Usage: show_success <message>
# Description: Shows a formatted success message
# Arguments:
#   $1: Message text
show_success() {
  gum style --foreground "$COLOR_SUCCESS" "✓ $1"
}

# Display an error message
# Usage: show_error <message>
# Description: Shows a formatted error message
# Arguments:
#   $1: Message text
show_error() {
  gum style --foreground "$COLOR_ERROR" "✗ $1"
}

# Display a warning message
# Usage: show_warning <message>
# Description: Shows a formatted warning message
# Arguments:
#   $1: Message text
show_warning() {
  gum style --foreground "$COLOR_WARNING" "⚠️  $1"
}

# Display an info message
# Usage: show_info <message>
# Description: Shows a formatted info message
# Arguments:
#   $1: Message text
show_info() {
  gum style --foreground "$COLOR_INFO" "$1"
}

# Available languages - this should match the language files in i18n/ directory
readonly AVAILABLE_LANGS=("en" "es" "zh" "hi" "ar" "fr")
# Language names for display
readonly LANG_NAMES=("English" "Español" "中文" "हिन्दी" "العربية" "Français")
# Default language - will be overridden by system locale if available
LANG_CODE=""

# Set language
# Usage: set_language <lang_code>
# Description: Sets the application language
# Arguments:
#   $1: Language code (e.g., "en", "es", "zh", "hi", "ar", "fr")
set_language() {
  local lang="$1"
  
  # Validate language
  local valid_lang=false
  for i in "${!AVAILABLE_LANGS[@]}"; do
    if [ "${AVAILABLE_LANGS[$i]}" = "$lang" ]; then
      valid_lang=true
      break
    fi
  done
  
  if [ "$valid_lang" = true ]; then
    LANG_CODE="$lang"
    
    # IMPORTANT: Reset translations array at the global scope
    unset TRANSLATIONS
    # Export the variable to make sure it's at global scope
    export TRANSLATIONS
    # Redeclare as global associative array
    declare -gA TRANSLATIONS
    
    # Load translations directly
    local lang_file="${SCRIPT_DIR}/i18n/${LANG_CODE}.sh"
    
    # Check if language file exists
    if [ -f "$lang_file" ]; then
      echo "Loading translations from $lang_file"
      source "$lang_file"
    else
      # Fall back to English if language file doesn't exist
      echo "Language file $lang_file not found, falling back to English"
      LANG_CODE="en"
      source "${SCRIPT_DIR}/i18n/en.sh"
    fi
    
    echo "Loaded ${#TRANSLATIONS[@]} translations for $LANG_CODE"
  else
    show_error "Invalid language code: $lang"
    return 1
  fi
  
  return 0
}

# Get localized string
# Usage: _t <key> [replacement1] [replacement2] ...
# Description: Gets a localized string for the given key
# Arguments:
#   $1: Translation key
#   $2-$n: Optional replacements for placeholders
# Returns: Translated string
_t() {
  local key="$1"
  shift
  
  # Debug information for translation lookup
  if [ -n "${GPG_MANAGER_DEBUG}" ]; then
    echo "DEBUG _t: Looking up key '$key', TRANSLATIONS has ${#TRANSLATIONS[@]} items" >&2
  fi
  
  # Check if translation exists
  if [ -n "${TRANSLATIONS[$key]}" ]; then
    local text="${TRANSLATIONS[$key]}"
    
    # Replace placeholders
    local i=1
    for replacement in "$@"; do
      text="${text//\{\{$i\}\}/$replacement}"
      i=$((i + 1))
    done
    
    echo "$text"
  else
    # If translation doesn't exist, print debug info
    if [ -n "${GPG_MANAGER_DEBUG}" ]; then
      echo "DEBUG _t: Missing translation for '$key'" >&2
    fi
    # Return key if translation doesn't exist
    echo "$key"
  fi
}

# Language selection menu
# Usage: language_selection_menu
# Description: Displays a menu for selecting language
language_selection_menu() {
  local options=()
  
  for i in "${!AVAILABLE_LANGS[@]}"; do
    options+=("${LANG_NAMES[$i]} (${AVAILABLE_LANGS[$i]})")
  done
  
  local selection=$(gum choose --header "Select Language / Seleccione Idioma / 选择语言 / भाषा चुनें / اختر لغة / Choisir une langue" "${options[@]}")
  
  # Extract language code from selection
  if [ -n "$selection" ]; then
    local lang_code=$(echo "$selection" | grep -o '([a-z][a-z])' | tr -d '()')
    set_language "$lang_code"
  fi
}