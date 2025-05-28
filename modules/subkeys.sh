#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# subkeys.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# GPG Console Manager - Subkeys Module
# License: AGPL

# Subkeys menu
subkeys_menu() {
  while true; do
    # Título según idioma
    local menu_title="Subkeys Management"
    local add_opt="Add Subkey"
    local list_opt="List Subkeys"
    local revoke_opt="Revoke Subkey"
    local back_opt="Back"

    if [ "$LANG_CODE" = "es" ]; then
      menu_title="Gestión de Subclaves"
      add_opt="Añadir Subclave"
      list_opt="Listar Subclaves"
      revoke_opt="Revocar Subclave"
      back_opt="Volver"
    fi

    gum style \
      --border double \
      --border-foreground "$COLOR_PRIMARY" \
      --padding "1" \
      --width 50 \
      --align center \
      --bold \
      "$menu_title"

    local choice=$(gum choose \
      "$add_opt" \
      "$list_opt" \
      "$revoke_opt" \
      "$back_opt")

    case "$choice" in
      "$add_opt")
        add_subkey
        ;;
      "$list_opt")
        list_subkeys
        ;;
      "$revoke_opt")
        revoke_subkey
        ;;
      "$back_opt")
        return
        ;;
    esac
  done
}

# List subkeys for a given key
list_subkeys() {
  # Texto según idioma
  local select_prompt="Select key to list subkeys"
  local subkeys_title="Subkeys for Key"
  local continue_prompt="Press Enter to continue"

  if [ "$LANG_CODE" = "es" ]; then
    select_prompt="Selecciona clave para listar subclaves"
    subkeys_title="Subclaves para la Clave"
    continue_prompt="Presiona Enter para continuar"
  fi

  local key_id=$(select_key "$select_prompt")

  if [ -z "$key_id" ]; then
    return
  fi

  gum style \
    --border rounded \
    --foreground "$COLOR_INFO" \
    --border-foreground "$COLOR_INFO" \
    --padding "1" \
    --width 60 \
    --align center \
    "$subkeys_title: $key_id"

  # Get key details showing subkeys
  gpg --list-keys --with-subkey-fingerprints "$key_id"

  gum confirm "$continue_prompt" && return
}

# Add a subkey to an existing key
add_subkey() {
  # Texto según idioma
  local select_prompt="Select primary key to add a subkey to"
  local signing_subkey="Signing subkey"
  local encryption_subkey="Encryption subkey"
  local auth_subkey="Authentication subkey"
  local sign_encrypt_subkey="Sign + Encrypt subkey"
  local back_opt="Back"
  local never_expire="Never expire"
  local expire_after="Expire after..."
  local year_one="1 year"
  local years_two="2 years"
  local years_five="5 years"
  local custom_opt="Custom..."
  local expiry_placeholder="Enter expiry (e.g., 30d, 6m, 3y)"

  if [ "$LANG_CODE" = "es" ]; then
    select_prompt="Selecciona clave primaria para añadir subclave"
    signing_subkey="Subclave de firma"
    encryption_subkey="Subclave de cifrado"
    auth_subkey="Subclave de autenticación"
    sign_encrypt_subkey="Subclave de firma + cifrado"
    back_opt="Volver"
    never_expire="Nunca caduca"
    expire_after="Caducar después de..."
    year_one="1 año"
    years_two="2 años"
    years_five="5 años"
    custom_opt="Personalizado..."
    expiry_placeholder="Introduce caducidad (ej. 30d, 6m, 3y)"
  fi

  local primary_key=$(select_key "$select_prompt")

  if [ -z "$primary_key" ]; then
    return
  fi

  # Choose subkey type
  local subkey_type=$(gum choose \
    "$signing_subkey" \
    "$encryption_subkey" \
    "$auth_subkey" \
    "$sign_encrypt_subkey" \
    "$back_opt")

  if [ "$subkey_type" = "$back_opt" ]; then
    return
  fi

  # Choose key algorithm
  local algorithm=$(gum choose "RSA" "ECC (Ed25519/CV25519)" "$back_opt")

  if [ "$algorithm" = "$back_opt" ]; then
    return
  fi

  # Ask for key expiration
  local expiry_type=$(gum choose "$never_expire" "$expire_after" "$back_opt")

  if [ "$expiry_type" = "$back_opt" ]; then
    return
  fi

  local expiry="0"
  if [ "$expiry_type" = "$expire_after" ]; then
    local expiry_option=$(gum choose "$year_one" "$years_two" "$years_five" "$custom_opt")

    case "$expiry_option" in
      "$year_one")
        expiry="1y"
        ;;
      "$years_two")
        expiry="2y"
        ;;
      "$years_five")
        expiry="5y"
        ;;
      "$custom_opt")
        expiry=$(gum input --placeholder "$expiry_placeholder" --value "")
        ;;
    esac
  fi

  # Create the subkey
  create_subkey "$primary_key" "$subkey_type" "$algorithm" "$expiry"
}

# Create a subkey with given parameters
create_subkey() {
  local primary_key="$1"
  local subkey_type="$2"
  local algorithm="$3"
  local expiry="$4"

  # Texto según idioma
  local ecc_note="Note: Creating two separate ECC subkeys for signing and encryption"
  local adding_text="Adding"
  local to_primary="to primary key"
  local algorithm_text="Algorithm"
  local expiry_text="Expiry"
  local never_expires="Never expires"
  local proceed_prompt="Proceed with subkey creation?"
  local creating_title="Creating subkey (this may take a while)..."
  local success_msg="✓ Subkey added successfully!"
  local failed_msg="✗ Failed to add subkey"
  local continue_prompt="Press Enter to continue"

  if [ "$LANG_CODE" = "es" ]; then
    ecc_note="Nota: Creando dos subclaves ECC separadas para firma y cifrado"
    adding_text="Añadiendo"
    to_primary="a clave primaria"
    algorithm_text="Algoritmo"
    expiry_text="Caducidad"
    never_expires="Nunca caduca"
    proceed_prompt="¿Proceder con la creación de subclave?"
    creating_title="Creando subclave (esto puede tardar un poco)..."
    success_msg="✓ ¡Subclave añadida con éxito!"
    failed_msg="✗ Error al añadir subclave"
    continue_prompt="Presiona Enter para continuar"
  fi

  # Map subkey type to capability flags
  local capability=""
  local subkey_type_english="Signing subkey"

  case "$subkey_type" in
    "Signing subkey"|"Subclave de firma")
      capability="sign"
      subkey_type_english="Signing subkey"
      ;;
    "Encryption subkey"|"Subclave de cifrado")
      capability="encrypt"
      subkey_type_english="Encryption subkey"
      ;;
    "Authentication subkey"|"Subclave de autenticación")
      capability="auth"
      subkey_type_english="Authentication subkey"
      ;;
    "Sign + Encrypt subkey"|"Subclave de firma + cifrado")
      capability="sign,encrypt"
      subkey_type_english="Sign + Encrypt subkey"
      ;;
  esac

  # Create batch instructions based on algorithm
  local batch_file=$(mktemp)

  echo "addkey" > "$batch_file"

  # Generate algo-specific parameters
  if [ "$algorithm" = "RSA" ]; then
    cat >> "$batch_file" << EOF
4
2048
$expiry
$capability
EOF
  elif [ "$algorithm" = "ECC (Ed25519/CV25519)" ]; then
    # Different ECC types depending on capability
    if [[ "$capability" == *"sign"* ]] && [[ "$capability" != *"encrypt"* ]]; then
      # Ed25519 for signing
      cat >> "$batch_file" << EOF
19
$expiry
$capability
EOF
    elif [[ "$capability" == *"encrypt"* ]] && [[ "$capability" != *"sign"* ]]; then
      # Curve25519 for encryption
      cat >> "$batch_file" << EOF
18
$expiry
$capability
EOF
    elif [[ "$capability" == *"sign"* ]] && [[ "$capability" == *"encrypt"* ]]; then
      # Need separate keys for sign+encrypt with ECC
      gum style --foreground "$COLOR_WARNING" "$ecc_note"

      # First add Ed25519 for signing
      cat >> "$batch_file" << EOF
19
$expiry
sign
EOF

      # Then add Curve25519 for encryption
      echo "addkey" >> "$batch_file"
      cat >> "$batch_file" << EOF
18
$expiry
encrypt
EOF
    else
      # Auth key uses Ed25519
      cat >> "$batch_file" << EOF
19
$expiry
$capability
EOF
    fi
  fi

  echo "save" >> "$batch_file"

  # Show summary before proceeding
  gum style --foreground "$COLOR_INFO" "$adding_text $subkey_type $to_primary: $primary_key"
  gum style --foreground "$COLOR_INFO" "$algorithm_text: $algorithm"
  gum style --foreground "$COLOR_INFO" "$expiry_text: $([ "$expiry" = "0" ] && echo "$never_expires" || echo "$expiry")"

  if ! gum confirm "$proceed_prompt"; then
    rm "$batch_file"
    return
  fi

  # Execute the edit-key command
  gum spin --title "$creating_title" -- gpg --batch --command-fd 0 --status-fd 2 --edit-key "$primary_key" < "$batch_file"

  # Clean up
  rm "$batch_file"

  if [ $? -eq 0 ]; then
    gum style --foreground "$COLOR_SUCCESS" "$success_msg"
  else
    gum style --foreground "$COLOR_ERROR" "$failed_msg"
  fi

  gum confirm "$continue_prompt" && return
}

# Revoke a subkey
revoke_subkey() {
  # Texto según idioma
  local select_prompt="Select primary key containing the subkey to revoke"
  local no_subkeys="No subkeys found for this primary key"
  local continue_prompt="Press Enter to continue"
  local select_header="Select subkey to revoke"
  local cancel_opt="Cancel"
  local warning_msg="⚠️  Warning: Revoking a subkey is a permanent action!"
  local confirm_revoke="Are you sure you want to revoke this subkey?"
  local affirmative_btn="Revoke Subkey"
  local negative_btn="Cancel"
  local index_error="Could not determine subkey index"
  local revoking_title="Revoking subkey..."
  local success_msg="✓ Subkey revoked successfully!"
  local failed_msg="✗ Failed to revoke subkey"
  local created_text="created"

  # Map capability flags translations
  local sign_cap="Sign"
  local encrypt_cap="Encrypt"
  local authenticate_cap="Authenticate"
  local certify_cap="Certify"

  if [ "$LANG_CODE" = "es" ]; then
    select_prompt="Selecciona clave primaria que contiene la subclave a revocar"
    no_subkeys="No se encontraron subclaves para esta clave primaria"
    continue_prompt="Presiona Enter para continuar"
    select_header="Selecciona subclave para revocar"
    cancel_opt="Cancelar"
    warning_msg="⚠️  Advertencia: ¡Revocar una subclave es una acción permanente!"
    confirm_revoke="¿Estás seguro de que quieres revocar esta subclave?"
    affirmative_btn="Revocar Subclave"
    negative_btn="Cancelar"
    index_error="No se pudo determinar el índice de la subclave"
    revoking_title="Revocando subclave..."
    success_msg="✓ ¡Subclave revocada con éxito!"
    failed_msg="✗ Error al revocar subclave"
    created_text="creada"

    sign_cap="Firma"
    encrypt_cap="Cifrado"
    authenticate_cap="Autenticación"
    certify_cap="Certificación"
  fi

  local primary_key=$(select_key "$select_prompt")

  if [ -z "$primary_key" ]; then
    return
  fi

  # Get subkeys for the selected primary key
  local subkeys_raw=$(gpg --list-keys --with-colons "$primary_key" | grep -E "^sub|^ssb")

  if [ -z "$subkeys_raw" ]; then
    gum style --foreground "$COLOR_ERROR" "$no_subkeys"
    gum confirm "$continue_prompt" && return
  fi

  # Parse subkeys into an array
  local subkey_ids=()
  local subkey_info=()

  while IFS='' read -r line; do
    local key_id=$(echo "$line" | cut -d: -f5)
    local created=$(echo "$line" | cut -d: -f6)
    local capabilities=$(echo "$line" | cut -d: -f12)
    created_date=$(date -d @"$created" +"%Y-%m-%d" 2>/dev/null || date -r "$created" +"%Y-%m-%d" 2>/dev/null)

    # Map capability flags to descriptions
    local cap_desc=""
    if [[ "$capabilities" == *"s"* ]]; then
      cap_desc="${cap_desc}$sign_cap "
    fi
    if [[ "$capabilities" == *"e"* ]]; then
      cap_desc="${cap_desc}$encrypt_cap "
    fi
    if [[ "$capabilities" == *"a"* ]]; then
      cap_desc="${cap_desc}$authenticate_cap "
    fi
    if [[ "$capabilities" == *"c"* ]]; then
      cap_desc="${cap_desc}$certify_cap "
    fi

    subkey_ids+=("$key_id")
    subkey_info+=("$key_id (${cap_desc:0:-1}, $created_text $created_date)")
  done <<< "$subkeys_raw"

  # Let user select a subkey
  subkey_info+=("$cancel_opt")
  local selection=$(gum choose --header "$select_header" "${subkey_info[@]}")

  if [ "$selection" = "$cancel_opt" ]; then
    return
  fi

  # Extract subkey ID from selection
  local subkey_id=$(echo "$selection" | cut -d' ' -f1)

  # Confirm revocation
  gum style --foreground "$COLOR_WARNING" "$warning_msg"

  if ! gum confirm "$confirm_revoke" --affirmative="$affirmative_btn" --negative="$negative_btn"; then
    return
  fi

  # Create batch file for key editing
  local batch_file=$(mktemp)

  # Find the index of the subkey in the list
  local subkey_index=0
  local found_index=""

  # Get list of subkeys with indices from gpg
  local key_edit_output=$(gpg --command-fd 0 --status-fd 1 --edit-key "$primary_key" << EOF
quit
EOF
)

  while IFS='' read -r line; do
    if [[ "$line" == *"ssb"* ]] && [[ "$line" == *"$subkey_id"* ]]; then
      # Extract the subkey index, typically appears as something like "ssb/1"
      found_index=$(echo "$line" | grep -o 'ssb/[0-9]\+' | cut -d'/' -f2)
      break
    fi
  done <<< "$key_edit_output"

  if [ -z "$found_index" ]; then
    gum style --foreground "$COLOR_ERROR" "$index_error"
    rm "$batch_file"
    gum confirm "$continue_prompt" && return
  fi

  # Create batch commands for revoking the subkey
  cat > "$batch_file" << EOF
key $found_index
revkey
y
save
EOF

  # Execute the edit-key command
  gum spin --title "$revoking_title" -- gpg --batch --command-fd 0 --edit-key "$primary_key" < "$batch_file"

  # Clean up
  rm "$batch_file"

  if [ $? -eq 0 ]; then
    gum style --foreground "$COLOR_SUCCESS" "$success_msg"
  else
    gum style --foreground "$COLOR_ERROR" "$failed_msg"
  fi

  gum confirm "$continue_prompt" && return
}
