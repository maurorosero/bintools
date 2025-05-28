#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# create_key.sh - Displays the menu for creating a new GPG key
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# GPG Console Manager - Create Key Module
# License: AGPL-3.0

# Purpose:
# This module provides functionality for creating new GPG keys with various
# algorithms and expiration settings. Supports both RSA and ECC key types.

# Create key menu
# Description: Displays the menu for creating a new GPG key
create_key_menu() {
  # Títulos según idioma
  local title="Create New GPG Key"
  local rsa_opt="RSA 4096"
  local ecc_opt="ECC (Ed25519)"
  local back_opt="Back"
  local fullname_prompt="Full Name"
  local email_prompt="Email Address"
  local comment_prompt="Comment (Optional)"
  local never_opt="Never Expire"
  local expire_opt="Expire After..."
  local name_error="Name cannot be empty"
  local email_error="Email cannot be empty"

  if [ "$LANG_CODE" = "es" ]; then
    title="Crear Nueva Clave GPG"
    # RSA y ECC son iguales en todos los idiomas
    back_opt="Volver"
    fullname_prompt="Nombre Completo"
    email_prompt="Dirección de Correo"
    comment_prompt="Comentario (Opcional)"
    never_opt="Nunca Expira"
    expire_opt="Expira Después de..."
    name_error="El nombre no puede estar vacío"
    email_error="El correo no puede estar vacío"
  fi

  section_header "$title"

  # Choose key type
  local key_type=$(gum choose "$rsa_opt" "$ecc_opt" "$back_opt")

  if [ "$key_type" = "$back_opt" ]; then
    return
  fi

  # Get user information
  local name=$(gum input --placeholder "$fullname_prompt" --value "")
  if [ -z "$name" ]; then
    show_error "$name_error"
    confirm_continue
    return
  fi

  local email=$(gum input --placeholder "$email_prompt" --value "")
  if [ -z "$email" ]; then
    show_error "$email_error"
    confirm_continue
    return
  fi

  local comment=$(gum input --placeholder "$comment_prompt" --value "")

  # Ask for key expiration
  local expiry_type=$(gum choose "$never_opt" "$expire_opt" "$back_opt")

  if [ "$expiry_type" = "$back_opt" ]; then
    return
  fi

  local expiry="0"
  if [ "$expiry_type" = "$expire_opt" ]; then
    # Opciones de expiración
    local year_one="1 Year"
    local years_two="2 Years"
    local years_five="5 Years"
    local custom_opt="Custom..."

    if [ "$LANG_CODE" = "es" ]; then
      year_one="1 Año"
      years_two="2 Años"
      years_five="5 Años"
      custom_opt="Personalizado..."
    fi

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
        # Mensaje para expiración personalizada
        local expiry_prompt="Enter expiry (e.g.: 30d, 6m, 3y)"
        if [ "$LANG_CODE" = "es" ]; then
          expiry_prompt="Ingrese expiración (ej: 30d, 6m, 3y)"
        fi
        expiry=$(gum input --placeholder "$expiry_prompt" --value "1y")
        ;;
    esac
  fi

  # Generate the key
  if [ "$key_type" = "$rsa_opt" ]; then
    create_rsa_key "$name" "$email" "$comment" "$expiry"
  elif [ "$key_type" = "$ecc_opt" ]; then
    create_ecc_key "$name" "$email" "$comment" "$expiry"
  fi
}

# Create RSA 4096 key
# Usage: create_rsa_key <name> <email> <comment> <expiry>
# Description: Creates a new RSA 4096 key with the provided information
# Arguments:
#   $1: Real name
#   $2: Email address
#   $3: Comment (optional)
#   $4: Expiry period
create_rsa_key() {
  local name="$1"
  local email="$2"
  local comment="$3"
  local expiry="$4"

  local user_id="$name"
  if [ -n "$comment" ]; then
    user_id="$name ($comment)"
  fi
  user_id="$user_id <$email>"

  show_info "$(_t "creating_key_for" "RSA 4096" "$user_id")"
  show_info "$([ "$expiry" = "0" ] && echo "$(_t "never_expires")" || echo "$(_t "with_expiry" "$expiry")")"

  if ! gum confirm "$(_t "proceed_key_creation")"; then
    return
  fi

  # Create temp batch file
  local batch_file=$(mktemp)

  cat > "$batch_file" << EOF
%echo Generating a RSA 4096 key
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: $name
EOF

  if [ -n "$comment" ]; then
    echo "Name-Comment: $comment" >> "$batch_file"
  fi

  cat >> "$batch_file" << EOF
Name-Email: $email
Expire-Date: $expiry
%commit
%echo Key generation completed
EOF

  # Generate the key
  gum spin --title "$(_t "generating_key" "RSA 4096")" -- gpg --batch --generate-key "$batch_file"
  local create_status=$?

  # Clean up
  rm "$batch_file"

  if [ $create_status -ne 0 ]; then
    show_error "$(_t "key_creation_failed")"
    confirm_continue
    return
  fi

  # Get the fingerprint of the new key
  local fingerprint=$(gpg --list-keys --with-colons "$email" | grep -m 1 "^fpr" | cut -d: -f10)

  show_success "$(_t "key_created_success")"
  gum style --foreground "$COLOR_INFO" "$(_t "fingerprint" "$(echo $fingerprint | sed 's/\(.\{4\}\)/\1 /g')")"

  # Ask to configure Git with this key
  if gum confirm "$(_t "configure_git_prompt")"; then
    configure_git "$email" "$name" "$fingerprint"
  fi

  confirm_continue
  return
}

# Create ECC key (Ed25519)
# Usage: create_ecc_key <name> <email> <comment> <expiry>
# Description: Creates a new Ed25519 ECC key with the provided information
# Arguments:
#   $1: Real name
#   $2: Email address
#   $3: Comment (optional)
#   $4: Expiry period
create_ecc_key() {
  local name="$1"
  local email="$2"
  local comment="$3"
  local expiry="$4"

  local user_id="$name"
  if [ -n "$comment" ]; then
    user_id="$name ($comment)"
  fi
  user_id="$user_id <$email>"

  show_info "$(_t "creating_key_for" "Ed25519" "$user_id")"
  show_info "$([ "$expiry" = "0" ] && echo "$(_t "never_expires")" || echo "$(_t "with_expiry" "$expiry")")"

  if ! gum confirm "$(_t "proceed_key_creation")"; then
    return
  fi

  # Create temp batch file
  local batch_file=$(mktemp)

  cat > "$batch_file" << EOF
%echo Generating an Ed25519 key
Key-Type: EDDSA
Key-Curve: ed25519
Subkey-Type: EDDSA
Subkey-Curve: ed25519
Name-Real: $name
EOF

  if [ -n "$comment" ]; then
    echo "Name-Comment: $comment" >> "$batch_file"
  fi

  cat >> "$batch_file" << EOF
Name-Email: $email
Expire-Date: $expiry
%commit
%echo Key generation completed
EOF

  # Generate the key
  gum spin --title "$(_t "generating_key" "Ed25519")" -- gpg --batch --generate-key "$batch_file"
  local create_status=$?

  # Clean up
  rm "$batch_file"

  if [ $create_status -ne 0 ]; then
    show_error "$(_t "key_creation_failed")"
    confirm_continue
    return
  fi

  # Get the fingerprint of the new key
  local fingerprint=$(gpg --list-keys --with-colons "$email" | grep -m 1 "^fpr" | cut -d: -f10)

  show_success "$(_t "key_created_success")"
  gum style --foreground "$COLOR_INFO" "$(_t "fingerprint" "$(echo $fingerprint | sed 's/\(.\{4\}\)/\1 /g')")"

  # Ask to configure Git with this key
  if gum confirm "$(_t "configure_git_prompt")"; then
    configure_git "$email" "$name" "$fingerprint"
  fi

  confirm_continue
  return
}
