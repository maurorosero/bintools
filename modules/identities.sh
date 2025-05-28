#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# identities.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# GPG Console Manager - Identities Module
# License: AGPL

# Identities menu
identities_menu() {
  while true; do
    # Texto según idioma
    local menu_title="User Identities Management"
    local add_opt="Add Identity"
    local list_opt="List Identities"
    local primary_opt="Change Primary Identity"
    local delete_opt="Delete Identity"
    local back_opt="Back"

    if [ "$LANG_CODE" = "es" ]; then
      menu_title="Gestión de Identidades de Usuario"
      add_opt="Añadir Identidad"
      list_opt="Listar Identidades"
      primary_opt="Cambiar Identidad Principal"
      delete_opt="Eliminar Identidad"
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
      "$primary_opt" \
      "$delete_opt" \
      "$back_opt")

    case "$choice" in
      "$add_opt")
        add_identity
        ;;
      "$list_opt")
        list_identities
        ;;
      "$primary_opt")
        change_primary_identity
        ;;
      "$delete_opt")
        delete_identity
        ;;
      "$back_opt")
        return
        ;;
    esac
  done
}

# List identities for a key
list_identities() {
  # Texto según idioma
  local select_prompt="Select key to list identities"
  local identities_title="Identities for Key"
  local continue_prompt="Press Enter to continue"

  if [ "$LANG_CODE" = "es" ]; then
    select_prompt="Selecciona clave para listar identidades"
    identities_title="Identidades para la Clave"
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
    "$identities_title: $key_id"

  # Display identities using gpg
  gpg --list-keys "$key_id"

  gum confirm "$continue_prompt" && return
}

# Add a new identity to a key
add_identity() {
  # Texto según idioma
  local select_prompt="Select key to add identity to"
  local name_placeholder="Full Name"
  local email_placeholder="Email Address"
  local comment_placeholder="Comment (optional)"
  local name_error="Name cannot be empty"
  local email_error="Email cannot be empty"
  local adding_text="Adding identity"
  local to_key="To key"
  local proceed_confirm="Proceed?"
  local adding_title="Adding identity..."
  local success_msg="✓ Identity added successfully!"
  local failed_msg="✗ Failed to add identity"
  local continue_prompt="Press Enter to continue"

  if [ "$LANG_CODE" = "es" ]; then
    select_prompt="Selecciona clave para añadir identidad"
    name_placeholder="Nombre Completo"
    email_placeholder="Dirección de Email"
    comment_placeholder="Comentario (opcional)"
    name_error="El nombre no puede estar vacío"
    email_error="El email no puede estar vacío"
    adding_text="Añadiendo identidad"
    to_key="A la clave"
    proceed_confirm="¿Proceder?"
    adding_title="Añadiendo identidad..."
    success_msg="✓ ¡Identidad añadida con éxito!"
    failed_msg="✗ Error al añadir identidad"
    continue_prompt="Presiona Enter para continuar"
  fi

  local key_id=$(select_key "$select_prompt")

  if [ -z "$key_id" ]; then
    return
  fi

  # Get user information
  local name=$(gum input --placeholder "$name_placeholder" --value "")
  if [ -z "$name" ]; then
    gum style --foreground "$COLOR_ERROR" "$name_error"
    gum confirm "$continue_prompt" && return
  fi

  local email=$(gum input --placeholder "$email_placeholder" --value "")
  if [ -z "$email" ]; then
    gum style --foreground "$COLOR_ERROR" "$email_error"
    gum confirm "$continue_prompt" && return
  fi

  local comment=$(gum input --placeholder "$comment_placeholder" --value "")

  # Build user ID string
  local user_id="$name"
  if [ -n "$comment" ]; then
    user_id="$name ($comment)"
  fi
  user_id="$user_id <$email>"

  gum style --foreground "$COLOR_INFO" "$adding_text: $user_id"
  gum style --foreground "$COLOR_INFO" "$to_key: $key_id"

  if ! gum confirm "$proceed_confirm"; then
    return
  fi

  # Create batch file for key editing
  local batch_file=$(mktemp)

  cat > "$batch_file" << EOF
adduid
$name
$comment
$email
save
EOF

  # Execute the edit-key command
  gum spin --title "$adding_title" -- gpg --batch --command-fd 0 --status-fd 2 --edit-key "$key_id" < "$batch_file"

  # Clean up
  rm "$batch_file"

  if [ $? -eq 0 ]; then
    gum style --foreground "$COLOR_SUCCESS" "$success_msg"
  else
    gum style --foreground "$COLOR_ERROR" "$failed_msg"
  fi

  gum confirm "$continue_prompt" && return
}

# Change the primary identity for a key
change_primary_identity() {
  # Texto según idioma
  local select_prompt="Select key to change primary identity"
  local no_identities="No identities found for this key"
  local continue_prompt="Press Enter to continue"
  local select_header="Select new primary identity"
  local cancel_opt="Cancel"
  local primary_text="primary"
  local confirm_change="Set this identity as primary?"
  local changing_title="Changing primary identity..."
  local success_msg="✓ Primary identity changed successfully!"
  local failed_msg="✗ Failed to change primary identity"

  if [ "$LANG_CODE" = "es" ]; then
    select_prompt="Selecciona clave para cambiar identidad principal"
    no_identities="No se encontraron identidades para esta clave"
    continue_prompt="Presiona Enter para continuar"
    select_header="Selecciona nueva identidad principal"
    cancel_opt="Cancelar"
    primary_text="principal"
    confirm_change="¿Establecer esta identidad como principal?"
    changing_title="Cambiando identidad principal..."
    success_msg="✓ ¡Identidad principal cambiada con éxito!"
    failed_msg="✗ Error al cambiar identidad principal"
  fi

  local key_id=$(select_key "$select_prompt")

  if [ -z "$key_id" ]; then
    return
  fi

  # Get UIDs for the selected key
  local uids_raw=$(gpg --list-keys --with-colons "$key_id" | grep "^uid")

  if [ -z "$uids_raw" ]; then
    gum style --foreground "$COLOR_ERROR" "$no_identities"
    gum confirm "$continue_prompt" && return
  fi

  # Parse UIDs into an array
  local uid_indices=()
  local uid_info=()
  local index=1

  while IFS='' read -r line; do
    local uid_validity=$(echo "$line" | cut -d: -f2)
    local uid_name=$(echo "$line" | cut -d: -f10)
    local primary=""

    # Check if this is the primary UID
    if [ "$uid_validity" = "u" ]; then
      primary=" ($primary_text)"
    fi

    uid_indices+=("$index")
    uid_info+=("$index: $uid_name$primary")

    ((index++))
  done <<< "$uids_raw"

  # Let user select a UID
  uid_info+=("$cancel_opt")
  local selection=$(gum choose --header "$select_header" "${uid_info[@]}")

  if [ "$selection" = "$cancel_opt" ]; then
    return
  fi

  # Extract UID index from selection
  local uid_index=$(echo "$selection" | cut -d: -f1)

  # Confirm change
  if ! gum confirm "$confirm_change"; then
    return
  fi

  # Create batch file for key editing
  local batch_file=$(mktemp)

  # GPG uses 1-based indexing for UIDs
  cat > "$batch_file" << EOF
uid $uid_index
primary
save
EOF

  # Execute the edit-key command
  gum spin --title "$changing_title" -- gpg --batch --command-fd 0 --status-fd 2 --edit-key "$key_id" < "$batch_file"

  # Clean up
  rm "$batch_file"

  if [ $? -eq 0 ]; then
    gum style --foreground "$COLOR_SUCCESS" "$success_msg"
  else
    gum style --foreground "$COLOR_ERROR" "$failed_msg"
  fi

  gum confirm "$continue_prompt" && return
}

# Delete an identity from a key
delete_identity() {
  # Texto según idioma
  local select_prompt="Select key to delete identity from"
  local no_identities="No identities found for this key"
  local only_identity="Cannot delete the only identity for this key"
  local continue_prompt="Press Enter to continue"
  local select_header="Select identity to delete"
  local cancel_opt="Cancel"
  local primary_text="primary"
  local primary_error="Cannot delete the primary identity. Change the primary identity first."
  local warning_msg="⚠️  Warning: This will permanently delete the identity"
  local confirm_delete="Are you sure you want to delete this identity?"
  local affirmative_btn="Delete"
  local negative_btn="Cancel"
  local deleting_title="Deleting identity..."
  local success_msg="✓ Identity deleted successfully!"
  local failed_msg="✗ Failed to delete identity"

  if [ "$LANG_CODE" = "es" ]; then
    select_prompt="Selecciona clave para eliminar identidad"
    no_identities="No se encontraron identidades para esta clave"
    only_identity="No se puede eliminar la única identidad para esta clave"
    continue_prompt="Presiona Enter para continuar"
    select_header="Selecciona identidad para eliminar"
    cancel_opt="Cancelar"
    primary_text="principal"
    primary_error="No se puede eliminar la identidad principal. Cambia la identidad principal primero."
    warning_msg="⚠️  Advertencia: Esto eliminará permanentemente la identidad"
    confirm_delete="¿Estás seguro de que quieres eliminar esta identidad?"
    affirmative_btn="Eliminar"
    negative_btn="Cancelar"
    deleting_title="Eliminando identidad..."
    success_msg="✓ ¡Identidad eliminada con éxito!"
    failed_msg="✗ Error al eliminar identidad"
  fi

  local key_id=$(select_key "$select_prompt")

  if [ -z "$key_id" ]; then
    return
  fi

  # Get UIDs for the selected key
  local uids_raw=$(gpg --list-keys --with-colons "$key_id" | grep "^uid")

  # Count UIDs
  local uid_count=$(echo "$uids_raw" | wc -l)

  if [ -z "$uids_raw" ]; then
    gum style --foreground "$COLOR_ERROR" "$no_identities"
    gum confirm "$continue_prompt" && return
  fi

  if [ "$uid_count" -eq 1 ]; then
    gum style --foreground "$COLOR_ERROR" "$only_identity"
    gum confirm "$continue_prompt" && return
  fi

  # Parse UIDs into an array
  local uid_indices=()
  local uid_info=()
  local index=1

  while IFS='' read -r line; do
    local uid_validity=$(echo "$line" | cut -d: -f2)
    local uid_name=$(echo "$line" | cut -d: -f10)
    local primary=""

    # Check if this is the primary UID
    if [ "$uid_validity" = "u" ]; then
      primary=" ($primary_text)"
    fi

    uid_indices+=("$index")
    uid_info+=("$index: $uid_name$primary")

    ((index++))
  done <<< "$uids_raw"

  # Let user select a UID
  uid_info+=("$cancel_opt")
  local selection=$(gum choose --header "$select_header" "${uid_info[@]}")

  if [ "$selection" = "$cancel_opt" ]; then
    return
  fi

  # Check if trying to delete primary UID
  if [[ "$selection" == *"($primary_text)"* ]]; then
    gum style --foreground "$COLOR_ERROR" "$primary_error"
    gum confirm "$continue_prompt" && return
  fi

  # Extract UID index from selection
  local uid_index=$(echo "$selection" | cut -d: -f1)

  # Confirm deletion
  gum style --foreground "$COLOR_WARNING" "$warning_msg"

  if ! gum confirm "$confirm_delete" --affirmative="$affirmative_btn" --negative="$negative_btn"; then
    return
  fi

  # Create batch file for key editing
  local batch_file=$(mktemp)

  # GPG uses 1-based indexing for UIDs
  cat > "$batch_file" << EOF
uid $uid_index
deluid
y
save
EOF

  # Execute the edit-key command
  gum spin --title "$deleting_title" -- gpg --batch --command-fd 0 --status-fd 2 --edit-key "$key_id" < "$batch_file"

  # Clean up
  rm "$batch_file"

  if [ $? -eq 0 ]; then
    gum style --foreground "$COLOR_SUCCESS" "$success_msg"
  else
    gum style --foreground "$COLOR_ERROR" "$failed_msg"
  fi

  gum confirm "$continue_prompt" && return
}
