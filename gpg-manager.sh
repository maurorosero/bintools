#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# gpg-manager.sh - Description placeholder
# -----------------------------------------------------------------------------
#


# GPG Console Manager - Interactive GPG Key Management Tool
# License: AGPL-3.0

# Purpose:
# This script provides an interactive CLI interface for managing GPG keys, allowing
# users to create, list, export, import, and manage GPG keys and their properties
# through a user-friendly menu system using gum for better CLI experience.
#
# Examples:
# ./gpg-manager.sh - Run the manager with interactive menu
# ./gpg-manager.sh --lang es - Run the manager in Spanish
# ./gpg-manager.sh --lang zh - Run the manager in Chinese

# Global variables
readonly SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
readonly MODULES_DIR="${SCRIPT_DIR}/modules"
readonly I18N_DIR="${SCRIPT_DIR}/i18n"

set -uo pipefail

# --- Banner --- #
APP_NAME="Personal Packages Installer"
APP_VERSION="0.9.4 (2025/04)"
APP_AUTHOR="Mauro Rosero Pérez (mauro.rosero@gmail.com)"

# Parse command line arguments
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --lang|-l)
        LANG_CODE="$2"
        shift 2
        ;;
      --help|-h)
        show_help
        exit 0
        ;;
      *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
    esac
  done
}

# Show help
show_help() {
  gum style --bold "$(_t "main_menu_title") - $(_t "main_menu_subtitle")"
  echo
  echo "$(_t "usage_text"): $(basename "$0") [OPTIONS]"
  echo
  echo "$(_t "options_text"):"
  echo "  --lang, -l CODE   $(_t "lang_option_text")"
  echo "  --help, -h        $(_t "help_option_text")"
  echo
  echo "$(_t "languages_text"):"
  echo "  en - English ($(_t "default_text"))"
  echo "  es - Español (Spanish)"
  echo "  zh - 中文 (Chinese)"
  echo "  hi - हिन्दी (Hindi)"
  echo "  ar - العربية (Arabic)"
  echo "  fr - Français (French)"
  echo
}

# Import common library first
source "${MODULES_DIR}/common.sh"

# Initialize the translations array as a global variable
# Only unset if it's already defined, otherwise it will cause issues in functions
if declare -p TRANSLATIONS &>/dev/null; then
  unset TRANSLATIONS
fi
# Export the variable to make sure it's at global scope
export TRANSLATIONS
# Declare as global associative array
declare -gA TRANSLATIONS

# Parse command-line arguments
parse_args "$@"

# Set language based on command-line arguments or system locale
if [ -z "$LANG_CODE" ]; then
  # First, try to detect language from environment variables in order of preference
  for env_var in LC_ALL LC_MESSAGES LANG; do
    if [ -n "${!env_var}" ]; then
      # Extract language code (handling formats like en_US.UTF-8)
      SYSTEM_LANG=$(echo "${!env_var}" | cut -d_ -f1 | cut -d. -f1)
      [ -n "$SYSTEM_LANG" ] && break
    fi
  done
  
  # Debug language detection
  if [ -n "${GPG_MANAGER_DEBUG}" ]; then
    echo "Detected system language code: $SYSTEM_LANG"
  fi
  
  # Check if the detected language is supported
  is_supported=false
  for lang in "${AVAILABLE_LANGS[@]}"; do
    if [ "$lang" = "$SYSTEM_LANG" ]; then
      is_supported=true
      LANG_CODE="$SYSTEM_LANG"
      break
    fi
  done
  
  # Default to English if system language is not supported
  if [ "$is_supported" = "false" ]; then
    if [ -n "${GPG_MANAGER_DEBUG}" ]; then
      echo "System language '$SYSTEM_LANG' is not supported, using English as default"
    fi
    LANG_CODE="en"
  else
    if [ -n "${GPG_MANAGER_DEBUG}" ]; then
      echo "Using system language: $LANG_CODE"
    fi
  fi
fi

# Load translations directly from the language file
LANG_FILE="${SCRIPT_DIR}/i18n/${LANG_CODE}.sh"

# Check if the language file exists, if not fall back to English
if [ -f "$LANG_FILE" ]; then
  source "$LANG_FILE"
  
  # Debug information - verify translations loaded correctly
  if [ -n "${GPG_MANAGER_DEBUG}" ]; then
    echo "Initial language: $LANG_CODE"
    echo "Loaded ${#TRANSLATIONS[@]} translations"
    echo "Sample: menu_create_key = ${TRANSLATIONS["menu_create_key"]}"
  fi
else
  # If requested language file doesn't exist, fall back to English
  echo "Language file for $LANG_CODE not found, falling back to English"
  LANG_CODE="en"
  source "${SCRIPT_DIR}/i18n/en.sh"
fi

# Debug information - only show during development, remove or comment out for production
# if [ -n "${GPG_MANAGER_DEBUG}" ]; then
#   echo "==== GPG Manager Language Settings ===="
#   echo "Language: $LANG_CODE"
#   echo "Translations loaded: ${#TRANSLATIONS[@]}"
#   echo "Sample translations:"
#   echo "- Main title: $(_t "main_menu_title")"
#   echo "- Create key: $(_t "menu_create_key")"
#   echo "======================================="
# fi

# Import other modules
source "${MODULES_DIR}/create_key.sh"
source "${MODULES_DIR}/list_keys.sh"
source "${MODULES_DIR}/subkeys.sh"
source "${MODULES_DIR}/identities.sh"
source "${MODULES_DIR}/gitconfig.sh"

# Change language menu
# Description: Displays language selection menu and changes application language
change_language() {
  # Save the current language for reference
  local current_lang="$LANG_CODE"
  local options=()
  
  # Build array of options with nice formatting
  for i in "${!AVAILABLE_LANGS[@]}"; do
    local lang_code="${AVAILABLE_LANGS[$i]}"
    local lang_name="${LANG_NAMES[$i]}"
    
    # Mark current language
    if [ "$lang_code" = "$current_lang" ]; then
      options+=("$lang_name ($lang_code) ✓")
    else
      options+=("$lang_name ($lang_code)")
    fi
  done
  
  # Show language selection menu with current language strings
  local header="${TRANSLATIONS["language_select"]}"
  if [ -z "$header" ]; then
    header="Select Language"
  fi
  
  local selection=$(gum choose --header "$header" "${options[@]}")
  
  # If user made a selection, extract language code and change to it
  if [ -n "$selection" ]; then
    local new_lang=$(echo "$selection" | grep -o '([a-z][a-z])' | tr -d '()')
    
    if [ -n "$new_lang" ] && [ "$new_lang" != "$current_lang" ]; then
      # Change language code
      LANG_CODE="$new_lang"
      
      # Save current shell options and enable global exports
      local old_shell_opts=$(set +o)
      set -o allexport
      
      # IMPORTANT: Reset translations array at the global scope
      unset TRANSLATIONS
      declare -gA TRANSLATIONS
      
      # Source language file directly
      local lang_file="${SCRIPT_DIR}/i18n/${LANG_CODE}.sh"
      if [ -f "$lang_file" ]; then
        # Load translations directly to global scope
        source "$lang_file"
        
        # Restore previous shell options
        eval "$old_shell_opts"
        
        # Debug info
        #if [ -n "${GPG_MANAGER_DEBUG}" ]; then
        #  echo "Switched to language: $LANG_CODE"
        #  echo "Loaded ${#TRANSLATIONS[@]} translations"
        #  echo "Sample: menu_create_key = ${TRANSLATIONS["menu_create_key"]}"
        #fi
        
        if [ ${#TRANSLATIONS[@]} -eq 0 ]; then
          echo "ERROR: No translations loaded from $lang_file"
          # Fall back to original language
          LANG_CODE="$current_lang"
          
          # Try to load original language again
          set -o allexport
          source "${SCRIPT_DIR}/i18n/${LANG_CODE}.sh"
          eval "$old_shell_opts"
        else          
          # Confirmation message using new translations
          if [ -n "${TRANSLATIONS["language_changed"]}" ]; then
            # Use the translation mechanism to allow parameter replacements
            gum style --foreground "$COLOR_SUCCESS" "$(_t "language_changed" "$LANG_CODE")"
          else
            # Fallback if translation is missing
            gum style --foreground "$COLOR_SUCCESS" "Language changed to: $LANG_CODE"
          fi
          sleep 1
        fi
      else
        echo "Language file for $LANG_CODE not found! Falling back to English."
        LANG_CODE="en"
        
        # Load English translations 
        set -o allexport
        source "${SCRIPT_DIR}/i18n/en.sh"
        eval "$old_shell_opts"
      fi
    fi
  fi
}

# Main menu
# Description: Displays the main menu with all available options
main_menu() {
  while true; do
    # Ensure translations are loaded before displaying menu
    ensure_translations_loaded
    
    # Display elegant header
    display_welcome
    
    # Print all loaded keys in TRANSLATIONS for debugging
    if [ -n "${GPG_MANAGER_DEBUG}" ]; then
      echo "============ TRANSLATIONS DUMP ============"
      for key in "${!TRANSLATIONS[@]}"; do
        echo "Key: '$key' = '${TRANSLATIONS[$key]}'"
      done
      echo "==========================================="
      echo "Total translations: ${#TRANSLATIONS[@]}"
    fi
    
    # Fallback to English menu items if translations are missing
    local menu_create_key="${TRANSLATIONS["menu_create_key"]:-Create GPG Key}"
    local menu_list_keys="${TRANSLATIONS["menu_list_keys"]:-List/View Keys}"
    local menu_manage_subkeys="${TRANSLATIONS["menu_manage_subkeys"]:-Manage Subkeys}"
    local menu_manage_identities="${TRANSLATIONS["menu_manage_identities"]:-Manage Identities}" 
    local menu_export_keys="${TRANSLATIONS["menu_export_keys"]:-Export Keys}"
    local menu_import_keys="${TRANSLATIONS["menu_import_keys"]:-Import Keys}"
    local menu_revoke_key="${TRANSLATIONS["menu_revoke_key"]:-Revoke Key}"
    local menu_delete_key="${TRANSLATIONS["menu_delete_key"]:-Delete Key}"
    local menu_git_integration="${TRANSLATIONS["menu_git_integration"]:-Git Integration}"
    local menu_language_select="${TRANSLATIONS["language_select"]:-Select Language}"
    local menu_exit="${TRANSLATIONS["menu_exit"]:-Exit}"
    
    # Debug the local variables to see if they're properly set
    if [ -n "${GPG_MANAGER_DEBUG}" ]; then
      echo "Local variables:"
      echo "menu_create_key = '$menu_create_key'"
      echo "menu_list_keys = '$menu_list_keys'"
    fi
    
    # Configure gum display settings
    # Adjust pager height
    local gum_pager_height=15
    GUMPTION_PAGER_HEIGHT=$gum_pager_height
    export GUMPTION_PAGER_HEIGHT
    
    # Intentar configurar el texto de navegación en español
    # Nota: esto puede no funcionar en todas las versiones de gum
    if [ "$LANG_CODE" = "es" ]; then
      export GUM_CHOOSE_HEADER=""
      export GUM_CHOOSE_CURSOR="▶"
      export GUM_CHOOSE_SELECTED_PREFIX="▶"
      export GUM_CHOOSE_UNSELECTED_PREFIX=" "
      
      # Algunos entornos pueden soportar estas variables
      export GUM_CHOOSE_FOOTER="←↓↑→ navegar • enter seleccionar"
      export GUM_CHOOSE_ELLIPSIS="..."
    else
      # Restablecer a valores predeterminados para otros idiomas
      unset GUM_CHOOSE_HEADER
      unset GUM_CHOOSE_CURSOR
      unset GUM_CHOOSE_SELECTED_PREFIX
      unset GUM_CHOOSE_UNSELECTED_PREFIX
      unset GUM_CHOOSE_FOOTER
      unset GUM_CHOOSE_ELLIPSIS
    fi
    
    # Comprueba que todas las traducciones están presentes
    if [ -n "${GPG_MANAGER_DEBUG}" ]; then
      echo "Verificando traducciones del menú principal:"
      echo "menu_exit = '${TRANSLATIONS["menu_exit"]}'"
      echo "valor de menu_exit = '$menu_exit'"
    fi
    
    # Reduzca el número de elementos para asegurar que "Salir" aparezca en la primera página
    # Primero, define todas las opciones sin "Salir"
    local regular_options=(
      "$menu_create_key"
      "$menu_list_keys"
      "$menu_manage_subkeys"
      "$menu_manage_identities"
      "$menu_export_keys"
      "$menu_import_keys"
      "$menu_revoke_key"
      "$menu_delete_key"
      "$menu_git_integration"
      "$menu_language_select"
    )
    
    # Determina cuántos elementos mostrar para asegurar que "Salir" aparezca en la primera página
    # Supongamos que la pantalla muestra 10 elementos a la vez
    local max_visible_items=10
    local num_options=${#regular_options[@]}
    local num_to_show=$((max_visible_items - 1)) # -1 para dejar espacio para "Salir"
    
    # Asegúrate de no intentar mostrar más opciones de las que existen
    if [ $num_to_show -gt $num_options ]; then
      num_to_show=$num_options
    fi
    
    # Crea el menú final con las opciones limitadas más "Salir"
    local menu_items=()
    for (( i=0; i<$num_to_show; i++ )); do
      menu_items+=("${regular_options[$i]}")
    done
    menu_items+=("Salir")
    
    local choice=$(gum choose "${menu_items[@]}")
    
    # Log some debug information
    if [ -n "${GPG_MANAGER_DEBUG}" ]; then
      echo "Menu selection: '$choice'"
      echo "First menu item: '${menu_items[0]}'"
      echo "Languages keys available: ${#TRANSLATIONS[@]}"
    fi
    
    case "$choice" in
      "$menu_create_key")
        create_key_menu
        ;;
      "$menu_list_keys")
        list_keys_menu
        ;;
      "$menu_manage_subkeys")
        subkeys_menu
        ;;
      "$menu_manage_identities")
        identities_menu
        ;;
      "$menu_export_keys")
        export_menu
        ;;
      "$menu_import_keys")
        import_keys_menu
        ;;
      "$menu_revoke_key")
        revoke_key
        ;;
      "$menu_delete_key")
        delete_key
        ;;
      "$menu_git_integration")
        git_integration_menu
        ;;
      "$menu_language_select")
        change_language
        # Force reload menu after language change
        continue
        ;;
      "$menu_exit"|"Salir")
        clear
        local thanks_message="${TRANSLATIONS["thanks_message"]:-¡Gracias por usar el Gestor de Claves GPG!}"
        gum style --foreground "$COLOR_PRIMARY" "$thanks_message"
        exit 0
        ;;
      *)
        return
        ;;
    esac
  done
}

# Export keys menu
# Description: Provides options to export keys in different formats
export_menu() {
  local key_id=$(select_key "$(_t "select_key_export")")
  
  if [ -z "$key_id" ]; then
    return
  fi
  
  local export_type=$(gum choose \
    "$(_t "export_public_key")" \
    "$(_t "export_private_key")" \
    "$(_t "export_qr_code")" \
    "$(_t "publish_to_keyserver")" \
    "$(_t "generate_revoke_cert")" \
    "$(_t "back")")
  
  case "$export_type" in
    "$(_t "export_public_key")")
      export_public_key "$key_id"
      ;;
    "$(_t "export_private_key")")
      export_private_key "$key_id"
      ;;
    "$(_t "export_qr_code")")
      export_qr_code "$key_id"
      ;;
    "$(_t "publish_to_keyserver")")
      publish_to_keyserver "$key_id"
      ;;
    "$(_t "generate_revoke_cert")")
      generate_revocation_certificate "$key_id"
      ;;
    "$(_t "back")")
      return
      ;;
  esac
}

# Export public key
# Usage: export_public_key <key_id>
# Description: Exports the public key to an .asc file
# Arguments:
#   $1: Key ID to export
export_public_key() {
  local key_id="$1"
  local filename="publickey_${key_id}.asc"
  
  gum spin --title "$(_t "exporting_public_key")" -- gpg --armor --export "$key_id" > "$filename"
  local export_status=$?
  
  if [ $export_status -eq 0 ]; then
    show_success "$(_t "key_exported_to" "$(_t "public_key")" "$filename")"
  else
    show_error "$(_t "export_failed" "$(_t "public_key")")"
  fi
  
  confirm_continue
  return
}

# Export private key
# Usage: export_private_key <key_id>
# Description: Exports the private key to an encrypted .asc file
# Arguments:
#   $1: Key ID to export
export_private_key() {
  local key_id="$1"
  local filename="privatekey_${key_id}.asc"
  
  show_warning "$(_t "private_key_warning")"
  
  if gum confirm "$(_t "continue_private_export")"; then
    gum spin --title "$(_t "exporting_private_key")" -- gpg --armor --export-secret-key "$key_id" > "$filename"
    local export_status=$?
    
    if [ $export_status -eq 0 ]; then
      show_success "$(_t "key_exported_to" "$(_t "private_key")" "$filename")"
    else
      show_error "$(_t "export_failed" "$(_t "private_key")")"
    fi
  fi
  
  confirm_continue
  return
}

# Export key as QR code
# Usage: export_qr_code <key_id>
# Description: Exports the public key as a QR code
# Arguments:
#   $1: Key ID to export
export_qr_code() {
  local key_id="$1"
  
  if ! command -v qrencode &> /dev/null; then
    show_error "$(_t "qrencode_not_installed")"
    gum style "$(_t "install_instructions")"
    gum style "  Debian/Ubuntu: sudo apt install qrencode"
    gum style "  Fedora: sudo dnf install qrencode"
    gum style "  Arch: sudo pacman -S qrencode"
    gum style "  macOS: brew install qrencode"
    confirm_continue
    return
  fi
  
  # Get key info to display a more informative message
  local key_info=$(gpg --list-keys --with-colons "$key_id" 2>/dev/null | grep "^uid" | head -n 1 | cut -d: -f10)
  local key_short="${key_id:(-8)}" # Last 8 characters of the key ID
  
  show_info "$(_t "exporting_qr_code")"
  show_info "Key: $key_short ($key_info)"
  
  # Use the specific path requested: ~/secure/gpg
  local secure_dir="$HOME/secure/gpg"
  
  # Create secure directory if it doesn't exist
  if [ ! -d "$secure_dir" ]; then
    mkdir -p "$secure_dir"
    
    # Secure the directory permissions (only user can read/write)
    chmod 700 "$HOME/secure"
    chmod 700 "$secure_dir"
    
    show_info "Created secure directory for GPG files at $secure_dir"
  fi
  
  # Generate filename with date and time for uniqueness
  local date_stamp=$(date "+%Y%m%d_%H%M%S")
  local qr_filename="$secure_dir/gpg_key_${key_short}_${date_stamp}.png"
  
  # Get fingerprint for a more optimal QR code
  local fingerprint=$(gpg --list-keys --with-colons "$key_id" 2>/dev/null | grep "^fpr" | head -n 1 | cut -d: -f10)
  
  if [ -n "$fingerprint" ]; then
    # Create a URL that links to the key on keyservers instead of including full key
    show_info "Creating QR code with fingerprint URL (more compact)"
    echo "https://keys.openpgp.org/search?q=0x$fingerprint" | qrencode -o "$qr_filename"
    
    if [ $? -eq 0 ]; then
      show_success "QR code created at: $qr_filename"
      show_info "The QR code contains a URL to find this key on keyservers"
      show_info "You might want to publish this key to keys.openpgp.org first"
      
      # Check if key is already published on keys.openpgp.org
      show_info "Checking if key is already published on keys.openpgp.org..."
      # Use curl to directly check the key's existence on the server (more reliable than gpg search)
      local server_check
      if command -v curl &>/dev/null; then
        server_check=$(curl -s --max-time 10 "https://keys.openpgp.org/vks/v1/by-fingerprint/$fingerprint" -o /dev/null -w "%{http_code}")
        
        local key_exists=false
        if [ "$server_check" = "200" ]; then
          # HTTP 200 means the key exists
          show_success "Key is already published on keys.openpgp.org"
          show_info "QR code URL will work correctly to find your key"
          key_exists=true
        elif [ "$server_check" = "404" ]; then
          # HTTP 404 means the key doesn't exist on the server
          show_info "Key is not yet published on keys.openpgp.org"
        else 
          # Other HTTP codes mean there was an error or unexpected response
          show_warning "Could not verify if key exists on server (HTTP code: $server_check)"
          # Try an alternative method using gpg in batch mode
          server_check=$(gpg --batch --keyserver keys.openpgp.org --recv-keys "$fingerprint" 2>&1)
          if echo "$server_check" | grep -q "imported" || echo "$server_check" | grep -q "unchanged"; then
            show_success "Key is already published on keys.openpgp.org"
            show_info "QR code URL will work correctly to find your key"
            key_exists=true
          else
            show_info "Key is likely not yet published on keys.openpgp.org"
          fi
        fi
      else
        # Fallback to batch gpg command when curl is not available
        server_check=$(gpg --batch --keyserver keys.openpgp.org --recv-keys "$fingerprint" 2>&1)
        local key_exists=false
        if echo "$server_check" | grep -q "imported" || echo "$server_check" | grep -q "unchanged"; then
          show_success "Key is already published on keys.openpgp.org"
          show_info "QR code URL will work correctly to find your key"
          key_exists=true
        else
          show_info "Key is likely not yet published on keys.openpgp.org"
        fi
      fi
      
      if [ "$key_exists" = true ]; then
        # Key already exists, no need to publish
        :
      else
        # Ask if they want to publish the key to make the URL work
        if gum confirm "Would you like to publish this key to keys.openpgp.org now?"; then
          # Publish key to keys.openpgp.org 
          show_info "Publishing key to keys.openpgp.org..."
          gum spin --title "Publishing key..." -- gpg --keyserver keys.openpgp.org --send-keys "$key_id"
          
          if [ $? -eq 0 ]; then
            show_success "Key published successfully. QR code URL will now work correctly."
            show_info "Note: For keys.openpgp.org, you will need to verify your email to make your identity information visible to others."
          else
            show_error "Failed to publish key."
          fi
        fi
      fi
    else
      show_error "Failed to create QR code image."
    fi
  else
    # Try to generate a PNG file with the full key data
    show_warning "Creating QR code with full key data (may fail if key is too large)"
    gpg --armor --export "$key_id" | qrencode -o "$qr_filename" 2>/dev/null
    
    if [ $? -ne 0 ]; then
      show_error "Failed to encode the key as QR code: Key data too large"
      show_info "Try exporting to a file instead with the 'Export Public Key' option"
    else
      show_success "QR code created at: $qr_filename"
      show_info "The QR code contains your full public key data"
    fi
  fi
  
  confirm_continue
  return
}

# Import keys menu
# Description: Provides options to import keys from different sources
import_keys_menu() {
  while true; do
    # Título según idioma
    local import_title="Import GPG Keys"
    if [ "$LANG_CODE" = "es" ]; then
      import_title="Importar Claves GPG"
    fi
    
    section_header "$import_title"
    
    # Opciones según idioma
    local file_opt="Import from File"
    local server_opt="Import from Keyserver"
    local url_opt="Import from URL"
    local text_opt="Import from Text"
    local qr_opt="Import from QR Code"
    local revoke_opt="Import Revocation Certificate"
    local back_opt="Back"
    
    if [ "$LANG_CODE" = "es" ]; then
      file_opt="Importar desde Archivo"
      server_opt="Importar desde Servidor de Claves"
      url_opt="Importar desde URL"
      text_opt="Importar desde Texto"
      qr_opt="Importar desde Código QR"
      revoke_opt="Importar Certificado de Revocación"
      back_opt="Volver"
    fi
    
    local choice=$(gum choose \
      "$file_opt" \
      "$server_opt" \
      "$url_opt" \
      "$text_opt" \
      "$qr_opt" \
      "$revoke_opt" \
      "$back_opt")
    
    case "$choice" in
      "$file_opt")
        import_from_file
        ;;
      "$server_opt")
        import_from_keyserver
        ;;
      "$url_opt")
        import_from_url
        ;;
      "$text_opt")
        import_from_text
        ;;
      "$qr_opt")
        import_from_qr
        ;;
      "$revoke_opt")
        import_revocation_cert
        ;;
      "$back_opt")
        return
        ;;
    esac
  done
}

# Import key from QR code
# Usage: import_from_qr
# Description: Imports a GPG key from a QR code (image file or camera)
import_from_qr() {
  section_header "$(_t "import_qr_title")"
  
  # Check if zbarimg is installed for QR code scanning
  if ! command -v zbarimg &> /dev/null; then
    show_error "$(_t "zbarimg_not_installed")"
    gum style "$(_t "install_instructions")"
    gum style "  Debian/Ubuntu: sudo apt install zbar-tools"
    gum style "  Fedora: sudo dnf install zbar"
    gum style "  Arch: sudo pacman -S zbar"
    gum style "  macOS: brew install zbar"
    confirm_continue
    return
  fi
  
  # Choose scan method
  local scan_method=$(gum choose --header "$(_t "qr_scan_options")" \
    "$(_t "load_qr_image")" \
    "$(_t "scan_qr_camera")" \
    "$(_t "back")")
  
  case "$scan_method" in
    "$(_t "back")")
      return
      ;;
    "$(_t "load_qr_image")")
      # Get image path
      local qr_path=$(gum input --placeholder "$(_t "enter_qr_path")" --value "$HOME/secure/gpg/")
      
      if [ -z "$qr_path" ]; then
        show_error "$(_t "error_no_file_path")"
        confirm_continue
        return
      fi
      
      if [ ! -f "$qr_path" ]; then
        show_error "$(_t "error_file_not_exist")"
        confirm_continue
        return
      fi
      
      # Scan the QR code from image
      show_info "$(_t "scanning_qr")"
      local qr_content=$(zbarimg -q --raw "$qr_path" 2>/dev/null)
      
      if [ -z "$qr_content" ]; then
        show_error "$(_t "qr_scan_error")"
        confirm_continue
        return
      fi
      ;;
    "$(_t "scan_qr_camera")")
      # Check if we have zbarcam available
      if ! command -v zbarcam &> /dev/null; then
        show_error "zbarcam not installed or not available"
        confirm_continue
        return
      fi
      
      show_info "$(_t "camera_scanning")"
      
      # Use zbarcam to scan from camera
      local qr_content=$(zbarcam --raw --prescale=640x480 -1 2>/dev/null)
      
      if [ -z "$qr_content" ]; then
        show_error "$(_t "qr_scan_error")"
        confirm_continue
        return
      fi
      ;;
  esac
  
  # Process the QR content
  # Check if it's a URL or a GPG key
  if [[ "$qr_content" == https://keys.openpgp.org/* ]] || [[ "$qr_content" == http://keys.openpgp.org/* ]]; then
    # It's a key URL
    show_success "$(_t "detected_key_url")"
    show_info "URL: $qr_content"
    
    # Extract key ID or fingerprint from URL
    local key_id=""
    if [[ "$qr_content" == *"/by-fingerprint/"* ]]; then
      key_id=$(echo "$qr_content" | sed -n 's/.*\/by-fingerprint\/\([A-F0-9]*\).*/\1/p')
    elif [[ "$qr_content" == *"search?q=0x"* ]]; then
      key_id=$(echo "$qr_content" | sed -n 's/.*search?q=0x\([A-F0-9]*\).*/\1/p')
    fi
    
    if [ -n "$key_id" ]; then
      show_info "Key ID/Fingerprint: $key_id"
      
      if gum confirm "$(_t "import_key_prompt")"; then
        show_info "$(_t "fetching_key_from_url")"
        gum spin --title "$(_t "importing_key")" -- gpg --keyserver keys.openpgp.org --recv-keys "$key_id"
        
        if [ $? -eq 0 ]; then
          show_success "$(_t "key_imported_success")"
          
          # Show imported key details
          local key_info=$(gpg --list-keys --with-colons "$key_id" | grep "^uid" | head -n 1 | cut -d: -f10)
          local fingerprint=$(gpg --list-keys --with-colons "$key_id" | grep "^fpr" | head -n 1 | cut -d: -f10)
          show_info "$(_t "imported_key_fingerprint" "$fingerprint")"
          show_info "User ID: $key_info"
          
          # Ask if the user wants to sign the imported key to trust it
          if gum confirm "$(_t "sign_key_prompt")"; then
            sign_imported_key "$key_id"
          fi
        else
          show_error "$(_t "import_failed")"
        fi
      fi
    else
      # If we couldn't extract the key ID, try to download the key from the URL
      show_info "Downloading key from URL..."
      
      # Check if curl is available
      if command -v curl &> /dev/null; then
        local temp_file=$(mktemp)
        curl -s "$qr_content" > "$temp_file"
        
        if [ $? -ne 0 ] || [ ! -s "$temp_file" ]; then
          show_error "Failed to download key from URL"
          rm -f "$temp_file"
          confirm_continue
          return
        fi
        
        # Import the key
        gum spin --title "$(_t "importing_key")" -- gpg --import "$temp_file"
        
        if [ $? -eq 0 ]; then
          show_success "$(_t "key_imported_success")"
          
          # Clean up
          rm -f "$temp_file"
          
          # Show imported key details
          local recent_import=$(gpg --list-keys --with-colons | tail -n 20)
          local fingerprint=$(echo "$recent_import" | grep "^fpr" | tail -n 1 | cut -d: -f10)
          
          if [ -n "$fingerprint" ]; then
            show_info "$(_t "imported_key_fingerprint" "$fingerprint")"
            
            # Ask if the user wants to sign the imported key to trust it
            if gum confirm "$(_t "sign_key_prompt")"; then
              sign_imported_key "$fingerprint"
            fi
          fi
        else
          show_error "$(_t "import_failed")"
          rm -f "$temp_file"
        fi
      else
        show_error "Curl is not installed. Cannot download key from URL."
      fi
    fi
  elif [[ "$qr_content" == -----BEGIN\ PGP\ PUBLIC\ KEY\ BLOCK----- ]]; then
    # It's a full PGP key
    show_success "$(_t "detected_full_key")"
    
    # Import the key from the QR content
    local temp_file=$(mktemp)
    echo "$qr_content" > "$temp_file"
    
    gum spin --title "$(_t "importing_key")" -- gpg --import "$temp_file"
    local import_status=$?
    
    # Clean up
    rm -f "$temp_file"
    
    if [ $import_status -eq 0 ]; then
      show_success "$(_t "key_imported_success")"
      
      # Show imported key details
      local recent_import=$(gpg --list-keys --with-colons | tail -n 20)
      local fingerprint=$(echo "$recent_import" | grep "^fpr" | tail -n 1 | cut -d: -f10)
      
      if [ -n "$fingerprint" ]; then
        show_info "$(_t "imported_key_fingerprint" "$fingerprint")"
        
        # Ask if the user wants to sign the imported key to trust it
        if gum confirm "$(_t "sign_key_prompt")"; then
          sign_imported_key "$fingerprint"
        fi
      fi
    else
      show_error "$(_t "import_failed")"
    fi
  else
    # Unknown content format
    show_error "Unrecognized QR code content"
    gum style "Content: ${qr_content:0:50}..."
    
    # Ask user if they want to try to import it anyway as a key
    if gum confirm "Try to import content as a key anyway?"; then
      local temp_file=$(mktemp)
      echo "$qr_content" > "$temp_file"
      
      gum spin --title "$(_t "importing_key")" -- gpg --import "$temp_file"
      local import_status=$?
      
      # Clean up
      rm -f "$temp_file"
      
      if [ $import_status -eq 0 ]; then
        show_success "$(_t "key_imported_success")"
      else
        show_error "$(_t "import_failed")"
      fi
    fi
  fi
  
  confirm_continue
  return
}

# Import key from file
# Description: Imports a GPG key from a local file
import_from_file() {
  section_header "$(_t "import_file_title")"
  
  local file_path=$(gum input --placeholder "$(_t "enter_file_path")" --value "")
  
  if [ -z "$file_path" ]; then
    show_error "$(_t "error_no_file_path")"
    confirm_continue
    return
  fi
  
  if [ ! -f "$file_path" ]; then
    show_error "$(_t "error_file_not_exist")"
    confirm_continue
    return
  fi
  
  gum spin --title "$(_t "importing_key")" -- gpg --import "$file_path"
  local import_status=$?
  
  if [ $import_status -eq 0 ]; then
    show_success "$(_t "key_imported_success")"
    
    # Show imported key details
    local key_info=$(gpg --list-keys --with-colons | tail -n 20)
    local fingerprint=$(echo "$key_info" | grep "^fpr" | tail -n 1 | cut -d: -f10)
    
    if [ -n "$fingerprint" ]; then
      show_info "$(_t "imported_key_fingerprint" "$(echo $fingerprint | sed 's/\(.\{4\}\)/\1 /g')")"
      
      # Ask if the user wants to sign the imported key to trust it
      if gum confirm "$(_t "sign_key_prompt")"; then
        sign_imported_key "$fingerprint"
      fi
    fi
  else
    show_error "$(_t "import_failed")"
  fi
  
  confirm_continue
  return
}

# Import key from keyserver
# Description: Searches for and imports a GPG key from a keyserver
import_from_keyserver() {
  section_header "$(_t "import_keyserver_title")"
  
  # Choose keyserver
  local keyserver=$(gum choose \
    "keys.openpgp.org" \
    "keyserver.ubuntu.com" \
    "pgp.mit.edu" \
    "keyring.debian.org" \
    "$(_t "other_specify")")
  
  if [ "$keyserver" = "$(_t "other_specify")" ]; then
    keyserver=$(gum input --placeholder "$(_t "enter_keyserver_url")" --value "")
    
    if [ -z "$keyserver" ]; then
      show_error "$(_t "error_no_keyserver")"
      confirm_continue
      return
    fi
  fi
  
  # Get search criteria
  local search_type=$(gum choose \
    "$(_t "search_email")" \
    "$(_t "search_key_id")" \
    "$(_t "search_fingerprint")" \
    "$(_t "search_name")")
  
  local search_term=""
  case "$search_type" in
    "$(_t "search_email")")
      search_term=$(gum input --placeholder "$(_t "enter_email")" --value "")
      ;;
    "$(_t "search_key_id")")
      search_term=$(gum input --placeholder "$(_t "enter_key_id")" --value "")
      ;;
    "$(_t "search_fingerprint")")
      search_term=$(gum input --placeholder "$(_t "enter_fingerprint")" --value "")
      search_term=$(echo "$search_term" | tr -d ' ')
      ;;
    "$(_t "search_name")")
      search_term=$(gum input --placeholder "$(_t "enter_name")" --value "")
      ;;
  esac
  
  if [ -z "$search_term" ]; then
    show_error "$(_t "error_no_search_term")"
    confirm_continue
    return
  fi
  
  # First, search for the key to show available options
  show_info "$(_t "searching_key" "$keyserver")"
  local search_results=$(gpg --keyserver "$keyserver" --search-keys "$search_term" 2>&1)
  local exit_code=$?
  
  if [ $exit_code -ne 0 ]; then
    show_error "$(_t "search_error")"
    gum style --foreground 3 "$search_results"
    confirm_continue
    return
  fi
  
  # Check if key was found
  if echo "$search_results" | grep -q "not found"; then
    show_error "$(_t "no_keys_found")"
    confirm_continue
    return
  fi
  
  # Display search results
  show_info "$(_t "search_results")"
  echo "$search_results"
  
  # Ask user to confirm import
  if ! gum confirm "$(_t "import_key_prompt")"; then
    return
  fi
  
  # Get key ID for direct import
  local key_id=$(gum input --placeholder "$(_t "enter_key_import")" --value "")
  
  if [ -z "$key_id" ]; then
    show_error "$(_t "error_no_key_id")"
    confirm_continue
    return
  fi
  
  # Import the key
  gum spin --title "$(_t "importing_from" "$keyserver")" -- gpg --keyserver "$keyserver" --recv-keys "$key_id"
  local import_status=$?
  
  if [ $import_status -eq 0 ]; then
    show_success "$(_t "key_imported_success")"
    
    # Show details of the imported key
    gpg --list-keys "$key_id"
    
    # Ask if the user wants to sign the imported key to trust it
    if gum confirm "$(_t "sign_key_prompt")"; then
      sign_imported_key "$key_id"
    fi
  else
    show_error "$(_t "import_failed")"
  fi
  
  confirm_continue
  return
}

# Import key from URL
# Usage: import_from_url
# Description: Downloads and imports a GPG key from a URL
import_from_url() {
  section_header "$(_t "import_url_title")"
  
  local url=$(gum input --placeholder "$(_t "enter_key_url")" --value "")
  
  if [ -z "$url" ]; then
    show_error "$(_t "error_no_url")"
    confirm_continue
    return
  fi
  
  # Check if curl or wget is available
  local downloader=""
  if command -v curl &> /dev/null; then
    downloader="curl -s"
  elif command -v wget &> /dev/null; then
    downloader="wget -qO-"
  else
    show_error "$(_t "downloader_missing")"
    gum style "$(_t "install_instructions")"
    gum style "  Debian/Ubuntu: sudo apt install curl"
    gum style "  Fedora: sudo dnf install curl"
    gum style "  Arch: sudo pacman -S curl"
    gum style "  macOS: brew install curl"
    confirm_continue
    return
  fi
  
  # Download and import the key
  show_info "$(_t "downloading_key")"
  local temp_file=$(mktemp)
  
  # Download the key
  gum spin --title "$(_t "downloading_key")" -- bash -c "$downloader '$url' > $temp_file"
  
  if [ ! -s "$temp_file" ]; then
    show_error "$(_t "download_failed")"
    rm -f "$temp_file"
    confirm_continue
    return
  fi
  
  # Check if file contains a PGP key
  if ! grep -q "BEGIN PGP" "$temp_file"; then
    show_error "$(_t "downloaded_not_key")"
    gum style --foreground 3 "$(_t "content_preview")"
    head -n 10 "$temp_file"
    rm -f "$temp_file"
    confirm_continue
    return
  fi
  
  # Import the key
  gum spin --title "$(_t "importing_key")" -- gpg --import "$temp_file"
  local import_status=$?
  
  # Clean up
  rm -f "$temp_file"
  
  if [ $import_status -eq 0 ]; then
    show_success "$(_t "key_imported_success")"
    
    # Show imported key details
    local key_info=$(gpg --list-keys --with-colons | tail -n 20)
    local fingerprint=$(echo "$key_info" | grep "^fpr" | tail -n 1 | cut -d: -f10)
    
    if [ -n "$fingerprint" ]; then
      show_info "$(_t "imported_key_fingerprint" "$(echo $fingerprint | sed 's/\(.\{4\}\)/\1 /g')")"
      
      # Ask if the user wants to sign the imported key to trust it
      if gum confirm "$(_t "sign_key_prompt")"; then
        sign_imported_key "$fingerprint"
      fi
    fi
  else
    show_error "$(_t "import_failed")"
  fi
  
  confirm_continue
  return
}

# Generate revocation certificate without importing it
# Usage: generate_revocation_certificate <key_id>
# Description: Creates a revocation certificate as a backup in case the private key is lost
# Arguments:
#   $1: Key ID to generate revocation certificate for
generate_revocation_certificate() {
  local key_id="$1"
  
  if [ -z "$key_id" ]; then
    show_error "$(_t "error_no_key_id")"
    return 1
  fi
  
  # Get key details for confirmation
  local fingerprint=$(gpg --list-keys --with-colons "$key_id" 2>/dev/null | grep "^fpr" | head -n 1 | cut -d: -f10)
  local uid=$(gpg --list-keys --with-colons "$key_id" 2>/dev/null | grep "^uid" | head -n 1 | cut -d: -f10)
  local key_short="${key_id:(-8)}" # Last 8 characters of the key ID
  
  # Section header
  section_header "$(_t "backup_revoke_title")"
  
  # Display key info
  gum style \
    --border normal \
    --border-foreground "$COLOR_PRIMARY" \
    --padding "1" \
    --width 80 \
    "$(gum style --foreground "$COLOR_PRIMARY" --bold "$(_t "backup_revoke_title")")" \
    "$(gum style --foreground "$COLOR_PRIMARY" "$(_t "key_id" "$(gum style --foreground 74 "$key_id")")")" \
    "$(gum style --foreground "$COLOR_PRIMARY" "$(_t "fingerprint_fmt" "$(gum style --foreground 74 "$(echo $fingerprint | sed 's/\(.\{4\}\)/\1 /g')")")")" \
    "$(gum style --foreground "$COLOR_PRIMARY" "$(_t "identity" "$uid")")"
  
  # Explain revocation certificates
  gum style ""
  gum style "$(_t "backup_revoke_info")"
  show_warning "$(_t "backup_revoke_warn")"
  gum style ""
  
  # Create secure directory for revocation certificates if it doesn't exist
  local secure_dir="$HOME/secure/gpg/revocations"
  if [ ! -d "$secure_dir" ]; then
    mkdir -p "$secure_dir"
    chmod 700 "$secure_dir"
  fi
  
  # Default filename with date
  local date_stamp=$(date "+%Y%m%d")
  local default_path="$secure_dir/backup_revoke_${key_short}_${date_stamp}.asc"
  
  # Ask for custom path
  local cert_path=$(gum input --placeholder "$(_t "backup_revoke_path")" --value "$default_path" --width 80)
  
  if [ -z "$cert_path" ]; then
    cert_path="$default_path"
  fi
  
  # Create directory for the certificate if it doesn't exist
  local cert_dir=$(dirname "$cert_path")
  if [ ! -d "$cert_dir" ]; then
    mkdir -p "$cert_dir"
    chmod 700 "$cert_dir"
  fi
  
  # Select revocation reason
  gum style ""
  gum style --foreground "$COLOR_PRIMARY" --bold "$(_t "revoke_reason_prompt")"
  local reason=$(gum choose \
    "$(_t "revoke_reason_comp")" \
    "$(_t "revoke_reason_replaced")" \
    "$(_t "revoke_reason_unused")" \
    "$(_t "revoke_reason_custom")")
  
  local reason_code=""
  local custom_reason=""
  
  case "$reason" in
    "$(_t "revoke_reason_comp")")
      reason_code="1"
      ;;
    "$(_t "revoke_reason_replaced")")
      reason_code="2"
      ;;
    "$(_t "revoke_reason_unused")")
      reason_code="3"
      ;;
    "$(_t "revoke_reason_custom")")
      reason_code="0"
      custom_reason=$(gum input --placeholder "$(_t "enter_custom_reason")" --width 80)
      ;;
  esac
  
  # Create batch file for the generation process to avoid interactive prompts
  local batch_file=$(mktemp)
  
  # Add answers to prompts to the batch file
  echo "y" > "$batch_file"
  echo "$reason_code" >> "$batch_file"
  
  if [ "$reason_code" = "0" ] && [ -n "$custom_reason" ]; then
    echo "$custom_reason" >> "$batch_file"
  fi
  
  echo "y" >> "$batch_file"
  
  # Generate the revocation certificate
  gum spin --title "$(_t "backup_revoke_generating")" -- \
    gpg --batch --yes --command-fd 0 --output "$cert_path" --gen-revoke "$key_id" < "$batch_file"
  local gen_status=$?
  
  # Clean up batch file
  rm -f "$batch_file"
  
  if [ $gen_status -ne 0 ]; then
    show_error "$(_t "backup_revoke_failed")"
    gum confirm "$(_t "press_enter")" && return 1
  fi
  
  # Set restrictive permissions
  chmod 600 "$cert_path"
  
  show_success "$(_t "backup_revoke_success" "$cert_path")"
  show_info "$(_t "backup_revoke_perms")"
  
  # Final reminder
  gum style ""
  gum style --foreground "$COLOR_WARNING" --bold "$(_t "backup_revoke_warn")"
  
  confirm_continue
  return 0
}

# Import key from pasted text
# Usage: import_from_text
# Description: Imports a GPG key from pasted text input
import_from_text() {
  section_header "$(_t "import_text_title")"
  
  gum style "$(_t "paste_key_instructions")"
  gum style "$(_t "press_ctrl_d")"
  
  local temp_file=$(mktemp)
  cat > "$temp_file"
  
  if [ ! -s "$temp_file" ]; then
    show_error "$(_t "error_no_input")"
    rm -f "$temp_file"
    confirm_continue
    return
  fi
  
  # Check if file contains a PGP key
  if ! grep -q "BEGIN PGP" "$temp_file"; then
    show_error "$(_t "error_invalid_key")"
    gum style --foreground 3 "$(_t "content_preview")"
    head -n 10 "$temp_file"
    rm -f "$temp_file"
    confirm_continue
    return
  fi
  
  # Import the key
  gum spin --title "$(_t "importing_key")" -- gpg --import "$temp_file"
  local import_status=$?
  
  # Clean up
  rm -f "$temp_file"
  
  if [ $import_status -eq 0 ]; then
    show_success "$(_t "key_imported_success")"
    
    # Show imported key details
    local key_info=$(gpg --list-keys --with-colons | tail -n 20)
    local fingerprint=$(echo "$key_info" | grep "^fpr" | tail -n 1 | cut -d: -f10)
    
    if [ -n "$fingerprint" ]; then
      show_info "$(_t "imported_key_fingerprint" "$(echo $fingerprint | sed 's/\(.\{4\}\)/\1 /g')")"
      
      # Ask if the user wants to sign the imported key to trust it
      if gum confirm "$(_t "sign_key_prompt")"; then
        sign_imported_key "$fingerprint"
      fi
    fi
  else
    show_error "$(_t "import_failed")"
  fi
  
  confirm_continue
  return
}

# Import revocation certificate
# Usage: import_revocation_cert
# Description: Imports a GPG key revocation certificate from a file
import_revocation_cert() {
  section_header "$(_t "import_revocation_title")"
  
  # Explain what a revocation certificate does
  gum style "$(_t "revocation_cert_info")"
  gum style ""
  
  # Get the path to the revocation certificate
  local revoke_cert_path=$(gum input --placeholder "$(_t "enter_revocation_path")" --width 80)
  
  if [ -z "$revoke_cert_path" ]; then
    show_error "$(_t "error_no_file_path")"
    confirm_continue
    return
  fi
  
  # Check if the file exists
  if [ ! -f "$revoke_cert_path" ]; then
    show_error "$(_t "error_file_not_exist")"
    confirm_continue
    return
  fi
  
  # Check if it's a valid revocation certificate
  if ! grep -q "BEGIN PGP PUBLIC KEY BLOCK" "$revoke_cert_path" || ! grep -q "REVOCATION" "$revoke_cert_path"; then
    show_error "$(_t "error_invalid_key")"
    gum style --foreground 3 "$(_t "content_preview")"
    head -n 10 "$revoke_cert_path"
    confirm_continue
    return
  fi
  
  # Confirm before importing
  show_warning "$(_t "revoke_warning")"
  if ! gum confirm "$(_t "proceed")"; then
    return
  fi
  
  # Import the revocation certificate
  gum spin --title "$(_t "importing_revocation")" -- gpg --import "$revoke_cert_path"
  local import_status=$?
  
  if [ $import_status -eq 0 ]; then
    show_success "$(_t "revocation_success")"
    
    # Check which key was revoked
    local revoked_key_info=$(gpg --list-keys --with-colons | grep -B 2 -A 2 "r:::" | grep "^pub")
    
    if [ -n "$revoked_key_info" ]; then
      local key_id=$(echo "$revoked_key_info" | cut -d: -f5)
      local uid=$(gpg --list-keys --with-colons "$key_id" 2>/dev/null | grep "^uid" | head -n 1 | cut -d: -f10)
      
      show_info "$(_t "key_id" "$key_id")"
      if [ -n "$uid" ]; then
        show_info "$(_t "identity" "$uid")"
      fi
      
      # Ask if they want to publish the revoked key
      if gum confirm "$(_t "publish_revoked_key")"; then
        # Choose keyserver
        local keyserver=$(gum choose \
          "keys.openpgp.org" \
          "keyserver.ubuntu.com" \
          "pgp.mit.edu" \
          "keyring.debian.org" \
          "$(_t "other_specify")")
        
        if [ "$keyserver" = "$(_t "other_specify")" ]; then
          keyserver=$(gum input --placeholder "$(_t "enter_keyserver_url")" --value "")
          
          if [ -z "$keyserver" ]; then
            show_error "$(_t "error_no_keyserver")"
            confirm_continue
            return
          fi
        fi
        
        # Publish the revoked key
        gum spin --title "$(_t "publishing_revoke" "$keyserver")" -- gpg --keyserver "$keyserver" --send-keys "$key_id"
        
        if [ $? -eq 0 ]; then
          show_success "$(_t "revoke_publish_success" "$keyserver")"
        else
          show_error "$(_t "revoke_publish_failed")"
        fi
      fi
    fi
  else
    show_error "$(_t "import_failed")"
  fi
  
  confirm_continue
  return
}

# Sign an imported key to trust it
# Usage: sign_imported_key <key_id>
# Description: Signs an imported key with one of the user's own keys
# Arguments:
#   $1: Key ID to sign
# Returns: 0 on success, non-zero on failure
sign_imported_key() {
  local key_id="$1"
  
  if [ -z "$key_id" ]; then
    show_error "$(_t "error_no_key_id")"
    return 1
  fi
  
  # Get user's own keys for signing
  local secret_keys_raw=$(gpg --list-secret-keys --with-colons 2>/dev/null)
  local secret_key_ids=()
  local secret_key_uids=()
  
  # Extract secret key IDs and UIDs
  if [ -n "$secret_keys_raw" ]; then
    local current_key=""
    
    while IFS='' read -r line; do
      local rec_type=${line%%:*}
      
      if [ "$rec_type" = "sec" ]; then
        current_key=$(echo "$line" | cut -d: -f5)
      elif [ "$rec_type" = "uid" ] && [ -n "$current_key" ]; then
        secret_key_ids+=("$current_key")
        secret_key_uids+=("$(echo "$line" | cut -d: -f10)")
        current_key=""
      fi
    done <<< "$secret_keys_raw"
  fi
  
  if [ ${#secret_key_ids[@]} -eq 0 ]; then
    show_error "$(_t "no_private_keys")"
    return 1
  fi
  
  # Build options for gum choose
  local options=()
  for i in "${!secret_key_uids[@]}"; do
    options+=("${secret_key_uids[$i]} (${secret_key_ids[$i]})")
  done
  options+=("$(_t "cancel")")
  
  # Let user select a key for signing
  local selection=$(gum choose --header "$(_t "select_sign_key")" "${options[@]}")
  
  if [ "$selection" = "$(_t "cancel")" ]; then
    return 1
  fi
  
  # Extract key ID from selection
  local signing_key_id=$(echo "$selection" | grep -o '([A-Z0-9]*)' | tr -d '()')
  
  # Choose trust level
  local trust_level=$(gum choose \
    "$(_t "trust_level_0")" \
    "$(_t "trust_level_1")" \
    "$(_t "trust_level_2")" \
    "$(_t "trust_level_3")")
  
  local trust_value=""
  case "$trust_level" in
    "$(_t "trust_level_0")") trust_value="0" ;;
    "$(_t "trust_level_1")") trust_value="1" ;;
    "$(_t "trust_level_2")") trust_value="2" ;;
    "$(_t "trust_level_3")") trust_value="3" ;;
  esac
  
  # Create batch file for key signing
  local batch_file=$(mktemp)
  
  # GPG command to sign key
  cat > "$batch_file" << EOF
y
$trust_value
y
EOF
  
  # Sign the key
  gum spin --title "$(_t "signing_key")" -- gpg --batch --command-fd 0 --local-user "$signing_key_id" --sign-key "$key_id" < "$batch_file"
  local sign_status=$?
  
  # Clean up
  rm -f "$batch_file"
  
  if [ $sign_status -eq 0 ]; then
    show_success "$(_t "sign_success")"
  else
    show_error "$(_t "sign_failed")"
  fi
  
  return 0
}

# Debug translations
# Usage: debug_translations
# Description: Prints some translation values for debugging
debug_translations() {
  # Only output debug information if DEBUG mode is enabled
  if [ -n "${GPG_MANAGER_DEBUG}" ]; then
    echo "Traducciones cargadas: ${#TRANSLATIONS[@]} entradas"
    echo "Idioma: $LANG_CODE"
    
    # Verificar algunas traducciones clave
    echo "menu_create_key: ${TRANSLATIONS["menu_create_key"]}"
    echo "menu_list_keys: ${TRANSLATIONS["menu_list_keys"]}"
    echo "menu_exit: ${TRANSLATIONS["menu_exit"]}"
    
    # Probar la función _t
    echo "Prueba _t() - menu_create_key: $(_t "menu_create_key")"
  fi
}

# Ensure translations are available globally
# Usage: ensure_translations_loaded
# Description: Makes sure translations are properly loaded and available
ensure_translations_loaded() {
  # If TRANSLATIONS array is empty, attempt to reload it
  if [ ${#TRANSLATIONS[@]} -eq 0 ]; then
    # Only show this message in debug mode
    if [ -n "${GPG_MANAGER_DEBUG}" ]; then
      echo "Reloading translations for $LANG_CODE as they appear to be missing"
    fi
    
    local lang_file="${SCRIPT_DIR}/i18n/${LANG_CODE}.sh"
    
    if [ -f "$lang_file" ]; then
      # Export here ensures that any variables defined in the language file 
      # will be exported to child processes (though that's not needed here)
      export LANG_CODE
      
      # Clear any existing values, but maintain the array type
      # This is important - we're keeping the same array but changing its contents
      if declare -p TRANSLATIONS &>/dev/null; then
        # Use a loop to clear individual keys while preserving the array
        for key in "${!TRANSLATIONS[@]}"; do
          unset "TRANSLATIONS[$key]"
        done
      else
        # Recreate the array if it doesn't exist
        declare -gA TRANSLATIONS
      fi
      
      # Source the language file directly
      source "$lang_file"
      
      # Debug information about what's loaded
      if [ ${#TRANSLATIONS[@]} -eq 0 ]; then
        echo "ERROR: Still no translations loaded from $lang_file"
        # Fall back to English
        LANG_CODE="en"
        source "${SCRIPT_DIR}/i18n/en.sh"
      fi
      
      # Show debug info only in debug mode
      if [ -n "${GPG_MANAGER_DEBUG}" ]; then
        echo "Loaded ${#TRANSLATIONS[@]} translations for $LANG_CODE"
        echo "Sample translation test: menu_create_key = '${TRANSLATIONS["menu_create_key"]}'"
      fi
    fi
  fi
}

# Main function
# Description: Entry point for the script
main() {
  # Check dependencies
  check_dependencies
  local deps_status=$?
  
  if [ $deps_status -ne 0 ]; then
    exit $deps_status
  fi

  # Ensure translations are loaded
  ensure_translations_loaded
  
  # Debug translations
  debug_translations
  
  # No need to display welcome message here, it's already handled in the main menu
  # main_menu will display the header
  main_menu
}

# Run main function
main
