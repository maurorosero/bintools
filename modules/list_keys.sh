#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# list_keys.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# GPG Console Manager - List Keys Module
# License: AGPL-3.0

# List keys menu
list_keys_menu() {
  while true; do
    # Título según idioma
    local keys_title="GPG Keys Management"
    local list_opt="List All Keys"
    local view_opt="View Key Details"
    local back_opt="Back"
    
    if [ "$LANG_CODE" = "es" ]; then
      keys_title="Gestión de Claves GPG"
      list_opt="Listar Todas las Claves"
      view_opt="Ver Detalles de Clave"
      back_opt="Volver"
    fi
    
    gum style \
      --border double \
      --border-foreground "$COLOR_PRIMARY" \
      --padding "1" \
      --width 50 \
      --align center \
      --bold \
      "$keys_title"
    
    local choice=$(gum choose \
      "$list_opt" \
      "$view_opt" \
      "$back_opt")
    
    case "$choice" in
      "$list_opt")
        list_all_keys
        ;;
      "$view_opt")
        view_key_details
        ;;
      "$back_opt")
        return
        ;;
    esac
  done
}

# List all keys with improved formatting and separation between own keys and others
list_all_keys() {
  # Opciones según idioma
  local show_all="Show All Keys"
  local show_my="Show My Keys"
  local show_public="Show Public Keys"
  local back_opt="Back"
  local keys_title="GPG Keys"
  
  if [ "$LANG_CODE" = "es" ]; then
    show_all="Mostrar Todas las Claves"
    show_my="Mostrar Mis Claves"
    show_public="Mostrar Claves Públicas"
    back_opt="Volver"
    keys_title="Claves GPG"
  fi
  
  local list_option=$(gum choose \
    "$show_all" \
    "$show_my" \
    "$show_public" \
    "$back_opt")
  
  if [ "$list_option" = "$back_opt" ]; then
    return
  fi
  
  # Different border styles for each section
  gum style \
    --border double \
    --border-foreground "$COLOR_PRIMARY" \
    --padding "1" \
    --width 60 \
    --bold \
    --align center \
    "$keys_title"
  
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
  
  # Get all keys in colon format for better parsing
  local keys_out=$(gpg --list-keys --with-colons)
  
  if [ -z "$keys_out" ]; then
    # Mensaje de error según idioma
    local error_msg="No GPG keys found"
    local press_enter="Press Enter to continue"
    
    if [ "$LANG_CODE" = "es" ]; then
      error_msg="No se encontraron claves GPG"
      press_enter="Presione Enter para continuar"
    fi
    
    gum style --foreground "$COLOR_ERROR" "$error_msg"
    gum confirm "$press_enter" && return
  fi
  
  # Variables to store key information
  local my_key_count=0
  local public_key_count=0
  local current_key=""
  local current_fingerprint=""
  local current_created=""
  local current_expires=""
  local current_uids=()
  local current_subkeys=()
  local in_key=false
  local is_own_key=false
  
  # Títulos de secciones según idioma
  local my_keys_header="My Keys (with Private Key)"
  local public_keys_header="Public Keys (from Others)"
  
  if [ "$LANG_CODE" = "es" ]; then
    my_keys_header="Mis Claves (con Clave Privada)"
    public_keys_header="Claves Públicas (de Otros)"
  fi
  
  # Print section header for own keys first
  if [ "$list_option" = "$show_all" ] || [ "$list_option" = "$show_my" ]; then
    gum style \
      --border rounded \
      --border-foreground "$COLOR_OWN_KEY" \
      --padding "0 1" \
      --width 60 \
      --bold \
      --align center \
      --foreground "$COLOR_OWN_KEY" \
      "$my_keys_header"
    echo ""
  fi
  
  # Process output line by line
  while IFS='' read -r line; do
    local rec_type=${line%%:*}
    
    if [ "$rec_type" = "pub" ]; then
      # If we were processing a key, print its information before starting a new one
      if [ "$in_key" = true ]; then
        # Only print the key if it matches the filter
        if [ "$list_option" = "$(_t "show_all_keys")" ] || \
           ( [ "$list_option" = "$(_t "show_only_my_keys")" ] && [ "$is_own_key" = true ] ) || \
           ( [ "$list_option" = "$(_t "show_only_public_keys")" ] && [ "$is_own_key" = false ] ); then
          print_key_info "$current_key" "$current_fingerprint" "$current_created" "$current_expires" "${current_uids[@]}" "${current_subkeys[@]}" "$is_own_key"
          echo ""
        fi
      fi
      
      # Start a new key
      in_key=true
      current_key=$(echo "$line" | cut -d: -f5)
      current_fingerprint=""
      current_created=$(echo "$line" | cut -d: -f6)
      current_expires=$(echo "$line" | cut -d: -f7)
      current_uids=()
      current_subkeys=()
      
      # Check if this is our own key (has a private key)
      is_own_key=false
      for secret_id in "${secret_key_ids[@]}"; do
        if [ "$current_key" = "$secret_id" ]; then
          is_own_key=true
          my_key_count=$((my_key_count + 1))
          break
        fi
      done
      
      if [ "$is_own_key" = false ]; then
        public_key_count=$((public_key_count + 1))
      fi
      
    elif [ "$rec_type" = "fpr" ] && [ -z "$current_fingerprint" ]; then
      current_fingerprint=$(echo "$line" | cut -d: -f10)
      
    elif [ "$rec_type" = "uid" ]; then
      # Add user ID to array
      current_uids+=("$(echo "$line" | cut -d: -f10)")
      
    elif [ "$rec_type" = "sub" ] || [ "$rec_type" = "ssb" ]; then
      # Extract subkey ID, creation date, expiration, and capabilities
      local subkey_id=$(echo "$line" | cut -d: -f5)
      local subkey_created=$(echo "$line" | cut -d: -f6)
      local subkey_expires=$(echo "$line" | cut -d: -f7)
      local subkey_capabilities=$(echo "$line" | cut -d: -f12)
      
      # Textos de capacidades según idioma
      local sign_cap="Sign"
      local encrypt_cap="Encrypt"
      local auth_cap="Auth"
      local cert_cap="Cert"
      local never_exp="Never expires"
      
      if [ "$LANG_CODE" = "es" ]; then
        sign_cap="Firma"
        encrypt_cap="Cifrado"
        auth_cap="Autenticación"
        cert_cap="Certificación"
        never_exp="Nunca expira"
      fi
      
      # Map capability flags to descriptions
      local cap_desc=""
      [[ "$subkey_capabilities" == *"s"* ]] && cap_desc="${cap_desc}${sign_cap} "
      [[ "$subkey_capabilities" == *"e"* ]] && cap_desc="${cap_desc}${encrypt_cap} "
      [[ "$subkey_capabilities" == *"a"* ]] && cap_desc="${cap_desc}${auth_cap} "
      [[ "$subkey_capabilities" == *"c"* ]] && cap_desc="${cap_desc}${cert_cap} "
      
      local created_date=$(format_date "$subkey_created")
      local expires_info=""
      
      if [ "$subkey_expires" = "0" ]; then
        expires_info="$never_exp"
      else
        expires_info=$(date -d @"$subkey_expires" +"%Y-%m-%d" 2>/dev/null || date -r "$subkey_expires" +"%Y-%m-%d" 2>/dev/null)
      fi
      
      # Store the next line to check for fingerprint
      local next_line=""
      local subkey_fpr=""
      if IFS='' read -r next_line <<< "$(echo "$keys_out" | grep -A 1 "^sub:.*:$subkey_id:" | tail -n 1)"; then
        if [[ "${next_line%%:*}" = "fpr" ]]; then
          subkey_fpr=$(echo "$next_line" | cut -d: -f10)
        fi
      fi
      
      # Store subkey with fingerprint
      current_subkeys+=("$subkey_id:${cap_desc:0:-1}:$created_date:$expires_info:$subkey_fpr")
    fi
  done <<< "$keys_out"
  
  # Print the last key if there was one
  if [ "$in_key" = true ]; then
    # Only print the key if it matches the filter
    if [ "$list_option" = "$show_all" ] || \
       ( [ "$list_option" = "$show_my" ] && [ "$is_own_key" = true ] ) || \
       ( [ "$list_option" = "$show_public" ] && [ "$is_own_key" = false ] ); then
      print_key_info "$current_key" "$current_fingerprint" "$current_created" "$current_expires" "${current_uids[@]}" "${current_subkeys[@]}" "$is_own_key"
      echo ""
    fi
  fi
  
  # Print section header for public keys
  if [ "$my_key_count" -gt 0 ] && [ "$public_key_count" -gt 0 ] && [ "$list_option" = "$show_all" ]; then
    gum style \
      --border rounded \
      --border-foreground "$COLOR_PUBLIC_KEY" \
      --padding "0 1" \
      --width 60 \
      --bold \
      --align center \
      --foreground "$COLOR_PUBLIC_KEY" \
      "$public_keys_header"
    echo ""
    
    # Reprocess to show public keys
    in_key=false
    
    while IFS='' read -r line; do
      local rec_type=${line%%:*}
      
      if [ "$rec_type" = "pub" ]; then
        # If we were processing a key, print its information before starting a new one
        if [ "$in_key" = true ]; then
          if [ "$is_own_key" = false ]; then
            print_key_info "$current_key" "$current_fingerprint" "$current_created" "$current_expires" "${current_uids[@]}" "${current_subkeys[@]}" "$is_own_key"
            echo ""
          fi
        fi
        
        # Start a new key
        in_key=true
        current_key=$(echo "$line" | cut -d: -f5)
        current_fingerprint=""
        current_created=$(echo "$line" | cut -d: -f6)
        current_expires=$(echo "$line" | cut -d: -f7)
        current_uids=()
        current_subkeys=()
        
        # Check if this is our own key (has a private key)
        is_own_key=false
        for secret_id in "${secret_key_ids[@]}"; do
          if [ "$current_key" = "$secret_id" ]; then
            is_own_key=true
            break
          fi
        done
        
      elif [ "$rec_type" = "fpr" ] && [ -z "$current_fingerprint" ]; then
        current_fingerprint=$(echo "$line" | cut -d: -f10)
        
      elif [ "$rec_type" = "uid" ]; then
        # Add user ID to array
        current_uids+=("$(echo "$line" | cut -d: -f10)")
        
      elif [ "$rec_type" = "sub" ] || [ "$rec_type" = "ssb" ]; then
        # Extract subkey ID, creation date, expiration, and capabilities
        local subkey_id=$(echo "$line" | cut -d: -f5)
        local subkey_created=$(echo "$line" | cut -d: -f6)
        local subkey_expires=$(echo "$line" | cut -d: -f7)
        local subkey_capabilities=$(echo "$line" | cut -d: -f12)
        
        # Textos de capacidades según idioma
        local sign_cap="Sign"
        local encrypt_cap="Encrypt"
        local auth_cap="Auth"
        local cert_cap="Cert"
        local never_exp="Never expires"
        
        if [ "$LANG_CODE" = "es" ]; then
          sign_cap="Firma"
          encrypt_cap="Cifrado"
          auth_cap="Autenticación"
          cert_cap="Certificación"
          never_exp="Nunca expira"
        fi
        
        # Map capability flags to descriptions
        local cap_desc=""
        [[ "$subkey_capabilities" == *"s"* ]] && cap_desc="${cap_desc}${sign_cap} "
        [[ "$subkey_capabilities" == *"e"* ]] && cap_desc="${cap_desc}${encrypt_cap} "
        [[ "$subkey_capabilities" == *"a"* ]] && cap_desc="${cap_desc}${auth_cap} "
        [[ "$subkey_capabilities" == *"c"* ]] && cap_desc="${cap_desc}${cert_cap} "
        
        # Format dates
        local created_date=""
        if [ -n "$subkey_created" ]; then
          created_date=$(date -d @"$subkey_created" +"%Y-%m-%d" 2>/dev/null || date -r "$subkey_created" +"%Y-%m-%d" 2>/dev/null)
        fi
        
        local expires_info=""
        if [ "$subkey_expires" = "0" ]; then
          expires_info="$never_exp"
        elif [ -n "$subkey_expires" ]; then
          expires_info=$(date -d @"$subkey_expires" +"%Y-%m-%d" 2>/dev/null || date -r "$subkey_expires" +"%Y-%m-%d" 2>/dev/null)
        fi
        
        # Store the next line to check for fingerprint
        local next_line=""
        local subkey_fpr=""
        if IFS='' read -r next_line <<< "$(echo "$keys_out" | grep -A 1 "^sub:.*:$subkey_id:" | tail -n 1)"; then
          if [[ "${next_line%%:*}" = "fpr" ]]; then
            subkey_fpr=$(echo "$next_line" | cut -d: -f10)
          fi
        fi
        
        # Store subkey with fingerprint
        current_subkeys+=("$subkey_id:${cap_desc:0:-1}:$created_date:$expires_info:$subkey_fpr")
      fi
    done <<< "$keys_out"
    
    # Print the last key if there was one
    if [ "$in_key" = true ] && [ "$is_own_key" = false ]; then
      print_key_info "$current_key" "$current_fingerprint" "$current_created" "$current_expires" "${current_uids[@]}" "${current_subkeys[@]}" "$is_own_key"
      echo ""
    fi
  fi
  
  # Resumen para mostrar según el idioma
  local total_keys_msg="Total: %d keys (%d personal, %d public)"
  local total_my_keys_msg="Total: %d personal keys"
  local total_public_keys_msg="Total: %d public keys"
  
  if [ "$LANG_CODE" = "es" ]; then
    total_keys_msg="Total: %d claves (%d personales, %d públicas)"
    total_my_keys_msg="Total: %d claves personales"
    total_public_keys_msg="Total: %d claves públicas"
  fi
  
  # Print summary
  case "$list_option" in
    "$show_all")
      gum style --bold --foreground "$COLOR_SUCCESS" "$(printf "$total_keys_msg" "$((my_key_count + public_key_count))" "$my_key_count" "$public_key_count")"
      ;;
    "$show_my")
      gum style --bold --foreground "$COLOR_SUCCESS" "$(printf "$total_my_keys_msg" "$my_key_count")"
      ;;
    "$show_public")
      gum style --bold --foreground "$COLOR_SUCCESS" "$(printf "$total_public_keys_msg" "$public_key_count")"
      ;;
  esac
  
  echo ""
  
  # Texto según idioma para continuar
  local continue_prompt="Press Enter to continue"
  if [ "$LANG_CODE" = "es" ]; then
    continue_prompt="Presiona Enter para continuar"
  fi
  
  gum confirm "$continue_prompt" && return
}

# Print formatted key information
print_key_info() {
  local key="$1"
  local fingerprint="$2"
  local created="$3"
  local expires="$4"
  shift 4
  
  # Texto según idioma
  local key_id_text="Key ID"
  local fingerprint_text="Fingerprint"
  local created_text="Created"
  local expires_text="Expires"
  local user_identities_title="User Identities"
  local subkeys_title="Subkeys"
  
  if [ "$LANG_CODE" = "es" ]; then
    key_id_text="ID de Clave"
    fingerprint_text="Huella digital"
    created_text="Creada"
    expires_text="Caduca"
    user_identities_title="Identidades de Usuario"
    subkeys_title="Subclaves"
  fi
  
  # Get UIDs from remaining args until we encounter a subkey
  local uids=()
  while [ $# -gt 0 ] && [[ "$1" != *:*:*:* ]]; do
    uids+=("$1")
    shift
  done
  
  # Remaining args are subkeys
  local subkeys=()
  while [ $# -gt 0 ] && [[ "$1" != "true" ]] && [[ "$1" != "false" ]]; do
    subkeys+=("$1")
    shift
  done
  
  # Last argument is a flag indicating if this is our own key
  local is_own_key="false"
  if [ $# -gt 0 ]; then
    is_own_key="$1"
  fi
  
  # Format creation and expiration dates
  local created_date=""
  if [ -n "$created" ]; then
    created_date=$(date -d @"$created" +"%Y-%m-%d" 2>/dev/null || date -r "$created" +"%Y-%m-%d" 2>/dev/null)
  fi
  
  local expires_info=""
  local never_expires="Never expires"
  if [ "$LANG_CODE" = "es" ]; then
    never_expires="Nunca caduca"
  fi
  
  if [ "$expires" = "0" ]; then
    expires_info="$never_expires"
  elif [ -n "$expires" ]; then
    expires_info=$(date -d @"$expires" +"%Y-%m-%d" 2>/dev/null || date -r "$expires" +"%Y-%m-%d" 2>/dev/null)
  fi
  
  # Choose colors based on whether this is our own key or a public key
  local border_color="$COLOR_PUBLIC_KEY"  # Blue for public keys
  local title_color="$COLOR_PUBLIC_KEY"
  local key_type_label=""
  
  if [ "$is_own_key" = "true" ]; then
    border_color="$COLOR_OWN_KEY"  # Yellow for own keys
    title_color="$COLOR_OWN_KEY"
    # Use last 8 characters of key ID as identifier
    local key_id_short="${key:(-8)}" 
    key_type_label="$(gum style --foreground "$COLOR_OWN_KEY" --bold "[${key_id_short}]") "
  fi
  
  # Print key information with color and formatting
  gum style --border rounded --border-foreground $border_color --padding "1" --width 80 "" 
  
  # Key ID and fingerprint
  gum style --foreground $title_color --bold "${key_type_label}$key_id_text: $(gum style --foreground 74 "$key")"
  gum style --foreground $title_color "$fingerprint_text: $(gum style --foreground 74 "$(echo $fingerprint | sed 's/\(.\{4\}\)/\1 /g')")"
  gum style --foreground $title_color "$created_text: $(gum style --foreground 74 "$created_date")"
  gum style --foreground $title_color "$expires_text: $(gum style --foreground 74 "$expires_info")"
  
  # Print UIDs
  gum style --foreground $title_color --underline "$user_identities_title"
  for uid in "${uids[@]}"; do
    gum style --foreground 74 "  • $uid"
  done
  
  # Print subkeys if any
  if [ ${#subkeys[@]} -gt 0 ]; then
    gum style --foreground $title_color --underline "$subkeys_title"
    for subkey_info in "${subkeys[@]}"; do
      IFS=':' read -r subkey_id capabilities subkey_created subkey_expires subkey_fpr <<< "$subkey_info"
      # Show the subkey with its fingerprint if available
      if [ -n "$subkey_fpr" ]; then
        gum style --foreground 255 "  • $(gum style --foreground 27 "$subkey_id") ($(gum style --foreground 126 "$capabilities"))"
        gum style --foreground 57 "    $fingerprint_text: $(echo $subkey_fpr | sed 's/\(.\{4\}\)/\1 /g')"
        gum style --foreground 57 "    $created_text: $subkey_created, $expires_text: $subkey_expires"
      else
        gum style --foreground 255 "  • $(gum style --foreground 27 "$subkey_id") ($(gum style --foreground 126 "$capabilities"), $(gum style --foreground 57 "$created_text: $subkey_created, $expires_text: $subkey_expires"))"
      fi
    done
  fi
  
  gum style --border rounded --border-foreground $border_color --padding "1" --width 80 ""
}

# Select a key from available keys
select_key() {
  local prompt="$1"
  
  # Texto según idioma
  local select_key_text="Select a key"
  local error_no_keys="No GPG keys found"
  local show_all_keys="Show All Keys"
  local show_my_keys="Show My Keys"
  local show_public_keys="Show Public Keys"
  local key_filter_prompt="Filter keys to show"
  local showing_own="showing only your keys"
  local showing_public="showing only public keys"
  local showing_all="showing all keys"
  local cancel_text="Cancel"
  local no_keys_filter="No keys match the selected filter"
  
  if [ "$LANG_CODE" = "es" ]; then
    select_key_text="Selecciona una clave"
    error_no_keys="No se encontraron claves GPG"
    show_all_keys="Mostrar Todas las Claves"
    show_my_keys="Mostrar Mis Claves"
    show_public_keys="Mostrar Claves Públicas"
    key_filter_prompt="Filtrar claves a mostrar"
    showing_own="mostrando solo tus claves"
    showing_public="mostrando solo claves públicas"
    showing_all="mostrando todas las claves"
    cancel_text="Cancelar"
    no_keys_filter="Ninguna clave coincide con el filtro seleccionado"
  fi
  
  if [ -z "$prompt" ]; then
    prompt="$select_key_text"
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
    gum style --foreground "$COLOR_ERROR" "$error_no_keys"
    return ""
  fi
  
  # Build options for gum choose with color coding for own vs public keys
  local options=()
  local options_header="$select_key_text"
  
  # Option for showing only certain types of keys
  local filter_type=""
  local filter_options=("$show_all_keys" "$show_my_keys" "$show_public_keys")
  local filter_selection=$(gum choose --header "$key_filter_prompt" "${filter_options[@]}")
  
  case "$filter_selection" in
    "$show_my_keys")
      filter_type="own"
      options_header="$prompt ($showing_own)"
      ;;
    "$show_public_keys")
      filter_type="public"
      options_header="$prompt ($showing_public)"
      ;;
    *)
      options_header="$prompt ($showing_all)"
      ;;
  esac
  
  # Add keys based on filter
  for i in "${!key_ids[@]}"; do
    # Skip keys that don't match the filter
    if [ -n "$filter_type" ] && [ "${key_types[$i]}" != "$filter_type" ]; then
      continue
    fi
    
    if [ "${key_types[$i]}" = "own" ]; then
      # Format own keys with key ID as identifier
      local key_id_short="${key_ids[$i]:(-8)}" # Use last 8 characters of key ID
      options+=("$(gum style --foreground "$COLOR_OWN_KEY" "[${key_id_short}]") ${key_uids[$i]} (${key_ids[$i]})")
    else
      # Format public keys normally
      options+=("${key_uids[$i]} (${key_ids[$i]})")
    fi
  done
  
  if [ ${#options[@]} -eq 0 ]; then
    gum style --foreground "$COLOR_ERROR" "$no_keys_filter"
    return ""
  fi
  
  options+=("$cancel_text")
  
  # Let user select a key
  local selection=$(gum choose --header "$options_header" "${options[@]}")
  
  if [ "$selection" = "$cancel_text" ]; then
    return ""
  fi
  
  # Extract key ID from selection (we need to get what's inside the parentheses at the end)
  # The format is either:
  # 1. For own keys: "[A1E9DB07] Mauro Rosero (DEVOPS) <email@example.com> (A17ADF8EA1E9DB07)"
  # 2. For public keys: "Richard Stallman <rms@gnu.org> (2C6464AF2A8E4C02)"
  # We want to extract what's in the last parentheses pair
  local key_id=$(echo "$selection" | grep -o '([A-Z0-9]*)$' | tr -d '()')
  echo "$key_id"
}

# View key details with improved formatting
view_key_details() {
  # Texto según idioma
  local select_prompt="Select key to view details"
  local key_details_title="Key Details"
  local key_not_found="Key not found"
  local primary_key_info_title="Primary Key Information"
  local key_id_text="Key ID"
  local fingerprint_text="Fingerprint"
  local created_text="Created"
  local expires_text="Expires"
  local user_identities_title="User Identities"
  local validity_text="Validity"
  local subkeys_title="Subkeys"
  local subkey_id_text="Subkey ID"
  local type_text="Type"
  local usage_text="Usage"
  local keyserver_info_title="Keyserver Information"
  local press_enter_text="Press Enter to continue"
  
  # Map validity to a human-readable format
  local trust_level_0="Unknown"
  local invalid_trust="Invalid"
  local disabled_trust="Disabled"
  local revoked_trust="Revoked"
  local expired_trust="Expired"
  local undefined_trust="Undefined"
  local not_valid_trust="Not Valid"
  local trust_level_2="Marginally Trusted"
  local trust_level_3="Fully Trusted"
  local ultimately_valid_trust="Ultimately Trusted"
  
  # Algorithm names
  local algo_rsa="RSA"
  local algo_elgamal="ElGamal"
  local algo_dsa="DSA"
  local algo_ecdh="ECDH"
  local algo_ecdsa="ECDSA"
  local algo_ed25519="Ed25519"
  local algo_unknown_fmt="Unknown (%s)"
  
  # Dates
  local never_expires="Never expires"
  
  if [ "$LANG_CODE" = "es" ]; then
    select_prompt="Selecciona clave para ver detalles"
    key_details_title="Detalles de Clave"
    key_not_found="Clave no encontrada"
    primary_key_info_title="Información de Clave Primaria"
    key_id_text="ID de Clave"
    fingerprint_text="Huella digital"
    created_text="Creada"
    expires_text="Caduca"
    user_identities_title="Identidades de Usuario"
    validity_text="Validez"
    subkeys_title="Subclaves"
    subkey_id_text="ID de Subclave"
    type_text="Tipo"
    usage_text="Uso"
    keyserver_info_title="Información de Servidor de Claves"
    press_enter_text="Presiona Enter para continuar"
    
    # Validity translations
    trust_level_0="Desconocida"
    invalid_trust="Inválida"
    disabled_trust="Deshabilitada"
    revoked_trust="Revocada"
    expired_trust="Expirada"
    undefined_trust="Indefinida"
    not_valid_trust="No válida"
    trust_level_2="Confianza marginal"
    trust_level_3="Confianza plena"
    ultimately_valid_trust="Confianza absoluta"
    
    # Algorithm names in Spanish
    algo_rsa="RSA"
    algo_elgamal="ElGamal"
    algo_dsa="DSA"
    algo_ecdh="ECDH"
    algo_ecdsa="ECDSA"
    algo_ed25519="Ed25519"
    algo_unknown_fmt="Desconocido (%s)"
    
    # Dates in Spanish
    never_expires="Nunca caduca"
  fi
  
  local key_id=$(select_key "$select_prompt")
  
  if [ -z "$key_id" ]; then
    return
  fi
  
  gum style \
    --border double \
    --border-foreground "$COLOR_PRIMARY" \
    --padding "1" \
    --width 60 \
    --bold \
    --align center \
    "$key_details_title"
  
  # Get key details in colon format for better parsing
  local key_out=$(gpg --list-keys --with-colons "$key_id" 2>&1)
  
  # Check if the key was found
  if echo "$key_out" | grep -q "error reading key"; then
    show_error "$key_not_found"
    confirm_continue
    return
  fi
  
  # Variables to store key information
  local current_key=""
  local current_fingerprint=""
  local current_created=""
  local current_expires=""
  local current_uids=()
  local current_subkeys=()
  local current_subkey_fingerprints=()
  
  # Process output line by line
  echo ""
  while IFS='' read -r line; do
    local rec_type=${line%%:*}
    
    if [ "$rec_type" = "pub" ]; then
      current_key=$(echo "$line" | cut -d: -f5)
      current_created=$(echo "$line" | cut -d: -f6)
      current_expires=$(echo "$line" | cut -d: -f7)
      
    elif [ "$rec_type" = "fpr" ]; then
      # If this fingerprint follows a pub record, it's the primary key fingerprint
      # If it follows a sub/ssb record, it's a subkey fingerprint
      local fpr=$(echo "$line" | cut -d: -f10)
      if [ -z "$current_fingerprint" ]; then
        current_fingerprint=$fpr
      else
        current_subkey_fingerprints+=("$fpr")
      fi
      
    elif [ "$rec_type" = "uid" ]; then
      # Add user ID with validity and trust information
      local validity=$(echo "$line" | cut -d: -f2)
      local uid=$(echo "$line" | cut -d: -f10)
      
      # Map validity to a human-readable format
      local validity_str=""
      case "$validity" in
        o) validity_str="$trust_level_0" ;;
        i) validity_str="$invalid_trust" ;;
        d) validity_str="$disabled_trust" ;;
        r) validity_str="$revoked_trust" ;;
        e) validity_str="$expired_trust" ;;
        q) validity_str="$undefined_trust" ;;
        n) validity_str="$not_valid_trust" ;;
        m) validity_str="$trust_level_2" ;;
        f) validity_str="$trust_level_3" ;;
        u) validity_str="$ultimately_valid_trust" ;;
        -) validity_str="$trust_level_0" ;;
        *) validity_str="$trust_level_0 ($validity)" ;;
      esac
      
      current_uids+=("$uid:$validity_str")
      
    elif [ "$rec_type" = "sub" ] || [ "$rec_type" = "ssb" ]; then
      # Extract subkey ID, creation date, expiration, and capabilities
      local subkey_id=$(echo "$line" | cut -d: -f5)
      local subkey_created=$(echo "$line" | cut -d: -f6)
      local subkey_expires=$(echo "$line" | cut -d: -f7)
      local subkey_algo=$(echo "$line" | cut -d: -f4)
      local subkey_size=$(echo "$line" | cut -d: -f3)
      local subkey_capabilities=$(echo "$line" | cut -d: -f12)
      
      # Map algorithm to name
      local algo_name=""
      case "$subkey_algo" in
        1) algo_name="$algo_rsa" ;;
        2) algo_name="$algo_rsa" ;;
        3) algo_name="$algo_rsa" ;;
        16) algo_name="$algo_elgamal" ;;
        17) algo_name="$algo_dsa" ;;
        18) algo_name="$algo_ecdh" ;;
        19) algo_name="$algo_ecdsa" ;;
        22) algo_name="$algo_ed25519" ;;
        *) 
          if [ "$LANG_CODE" = "es" ]; then
            algo_name=$(printf "$algo_unknown_fmt" "$subkey_algo")
          else
            algo_name=$(printf "$algo_unknown_fmt" "$subkey_algo")
          fi
          ;;
      esac
      
      # Textos de capacidades según idioma
      local sign_cap="Sign"
      local encrypt_cap="Encrypt"
      local auth_cap="Auth"
      local cert_cap="Cert"
      
      if [ "$LANG_CODE" = "es" ]; then
        sign_cap="Firma"
        encrypt_cap="Cifrado"
        auth_cap="Autenticación"
        cert_cap="Certificación"
      fi
      
      # Map capability flags to descriptions
      local cap_desc=""
      [[ "$subkey_capabilities" == *"s"* ]] && cap_desc="${cap_desc}${sign_cap} "
      [[ "$subkey_capabilities" == *"e"* ]] && cap_desc="${cap_desc}${encrypt_cap} "
      [[ "$subkey_capabilities" == *"a"* ]] && cap_desc="${cap_desc}${auth_cap} "
      [[ "$subkey_capabilities" == *"c"* ]] && cap_desc="${cap_desc}${cert_cap} "
      
      current_subkeys+=("$subkey_id:${cap_desc:0:-1}:$subkey_created:$subkey_expires:$algo_name:$subkey_size")
    fi
  done <<< "$key_out"
  
  # Format creation and expiration dates
  local created_date=""
  if [ -n "$current_created" ]; then
    created_date=$(date -d @"$current_created" +"%Y-%m-%d" 2>/dev/null || date -r "$current_created" +"%Y-%m-%d" 2>/dev/null)
  fi
  
  local expires_info=""
  if [ "$current_expires" = "0" ]; then
    expires_info="$never_expires"
  elif [ -n "$current_expires" ]; then
    expires_info=$(date -d @"$current_expires" +"%Y-%m-%d" 2>/dev/null || date -r "$current_expires" +"%Y-%m-%d" 2>/dev/null)
  fi
  
  # Display key information in a structured format with improved styling
  # Primary key details
  gum style --foreground "$COLOR_PRIMARY" --bold --align center --width 60 --underline "$primary_key_info_title"
  echo ""
  
  # Use more neutral colors for text that will be visible on both light/dark backgrounds
  gum style --foreground "$COLOR_PRIMARY" "$key_id_text: $(gum style --foreground 74 "$current_key")"
  gum style --foreground "$COLOR_PRIMARY" "$fingerprint_text: $(gum style --foreground 74 "$(echo $current_fingerprint | sed 's/\(.\{4\}\)/\1 /g')")"
  gum style --foreground "$COLOR_PRIMARY" "$created_text: $(gum style --foreground 74 "$created_date")"
  gum style --foreground "$COLOR_PRIMARY" "$expires_text: $(gum style --foreground 74 "$expires_info")"
  
  # Display user IDs
  gum style ""
  gum style --foreground "$COLOR_PRIMARY" --bold --align center --width 60 --underline "$user_identities_title"
  echo ""
  for uid_info in "${current_uids[@]}"; do
    IFS=':' read -r uid validity_str <<< "$uid_info"
    # Use a more neutral color that works on both backgrounds
    gum style --foreground 74 "• $uid"
    gum style --foreground 103 "  $validity_text: $validity_str"
  done
  
  # Display subkeys with more details
  if [ ${#current_subkeys[@]} -gt 0 ]; then
    gum style ""
    gum style --foreground "$COLOR_PRIMARY" --bold --align center --width 60 --underline "$subkeys_title"
    echo ""
    local subkey_index=0
    for subkey_info in "${current_subkeys[@]}"; do
      IFS=':' read -r subkey_id capabilities subkey_created subkey_expires algo_name subkey_size <<< "$subkey_info"
      
      # Format subkey dates
      local sub_created_date=""
      if [ -n "$subkey_created" ]; then
        sub_created_date=$(date -d @"$subkey_created" +"%Y-%m-%d" 2>/dev/null || date -r "$subkey_created" +"%Y-%m-%d" 2>/dev/null)
      fi
      
      local sub_expires_info=""
      if [ "$subkey_expires" = "0" ]; then
        sub_expires_info="$never_expires"
      elif [ -n "$subkey_expires" ]; then
        sub_expires_info=$(date -d @"$subkey_expires" +"%Y-%m-%d" 2>/dev/null || date -r "$subkey_expires" +"%Y-%m-%d" 2>/dev/null)
      fi
      
      # Get the fingerprint for this subkey if available
      local subkey_fpr=""
      if [ $subkey_index -lt ${#current_subkey_fingerprints[@]} ]; then
        subkey_fpr=${current_subkey_fingerprints[$subkey_index]}
      fi
      
      # Use colors that work well on both light and dark backgrounds
      gum style --foreground 172 "• $subkey_id_text: $(gum style --foreground 74 "$subkey_id")"
      gum style --foreground 103 "  $type_text: $algo_name ($subkey_size bits)"
      gum style --foreground 103 "  $usage_text: $capabilities"
      gum style --foreground 103 "  $created_text: $sub_created_date"
      gum style --foreground 103 "  $expires_text: $sub_expires_info"
      
      if [ -n "$subkey_fpr" ]; then
        gum style --foreground 103 "  $fingerprint_text: $(echo $subkey_fpr | sed 's/\(.\{4\}\)/\1 /g')"
      fi
      
      gum style ""
      
      ((subkey_index++))
    done
  fi
  
  # Keyserver information if available
  local keyserver_info=$(gpg --list-options show-keyserver-urls --list-keys "$key_id" | grep -o 'hkp://[^ ]*')
  if [ -n "$keyserver_info" ]; then
    gum style ""
    gum style --foreground "$COLOR_PRIMARY" --bold --align center --width 60 --underline "$keyserver_info_title"
    echo ""
    gum style --foreground 103 "$keyserver_info"
    gum style ""
  fi
  
  gum confirm "$press_enter_text" && return
}

# Publish key to keyserver
# If provided with a key_id, uses that key directly
publish_to_keyserver() {
  section_header "$(_t "publish_key_title")"
  
  # Select key to publish if not provided
  local key_id="$1"
  if [ -z "$key_id" ]; then
    key_id=$(select_key "$(_t "select_key_publish")")
    
    if [ -z "$key_id" ]; then
      return
    fi
  fi
  
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
  
  # Confirm publication
  show_warning "$(_t "publish_warning")"
  
  if ! gum confirm "$(_t "publish_confirm")"; then
    return
  fi
  
  # Publish the key
  gum spin --title "$(_t "publishing_key" "$keyserver")" -- gpg --keyserver "$keyserver" --send-keys "$key_id"
  local publish_status=$?
  
  if [ $publish_status -eq 0 ]; then
    show_success "$(_t "publish_success" "$keyserver")"
    
    # If using keys.openpgp.org, remind about email verification
    if [[ "$keyserver" == *"keys.openpgp.org"* ]]; then
      show_info "$(_t "verify_email_reminder")"
    fi
  else
    show_error "$(_t "publish_failed")"
  fi
  
  confirm_continue
  return
}

# Revoke a key
# Usage: revoke_key
# Description: Revokes a GPG key through a user-friendly process that handles
# key selection, revocation reason, certificate generation, optional backup,
# and optional publication to keyservers.
revoke_key() {
  # Select a key to revoke
  local key_id=$(select_key "$(_t "select_key_revoke")")
  
  if [ -z "$key_id" ]; then
    return
  fi
  
  # Get key details for confirmation
  local fingerprint=$(gpg --list-keys --with-colons "$key_id" 2>/dev/null | grep "^fpr" | head -n 1 | cut -d: -f10)
  local uid=$(gpg --list-keys --with-colons "$key_id" 2>/dev/null | grep "^uid" | head -n 1 | cut -d: -f10)
  local key_short="${key_id:(-8)}" # Last 8 characters of the key ID
  
  # Section header
  section_header "$(_t "revoke_key_title")"
  
  # Display key info that will be revoked
  gum style \
    --border normal \
    --border-foreground "$COLOR_WARNING" \
    --padding "1" \
    --width 80 \
    "$(gum style --foreground "$COLOR_WARNING" --bold "$(_t "revoking_key")")" \
    "$(gum style --foreground "$COLOR_PRIMARY" "$(_t "key_id" "$(gum style --foreground 74 "$key_id")")")" \
    "$(gum style --foreground "$COLOR_PRIMARY" "$(_t "fingerprint_fmt" "$(gum style --foreground 74 "$(echo $fingerprint | sed 's/\(.\{4\}\)/\1 /g')")")")" \
    "$(gum style --foreground "$COLOR_PRIMARY" "$(_t "identity" "$uid")")"
  
  # Explain revocation consequences
  gum style ""
  show_warning "$(_t "revoke_warning")"
  gum style "$(_t "revoke_explain_1")"
  gum style "$(_t "revoke_explain_2")"
  gum style "$(_t "revoke_explain_3")"
  gum style ""
  
  # Final confirmation
  if ! gum confirm "$(_t "revoke_confirm")" --affirmative="$(_t "revoke_key")" --negative="$(_t "cancel")"; then
    return
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
  
  # Ask if the user wants to save the revocation certificate
  gum style ""
  local save_cert=false
  if gum confirm "$(_t "save_revoke_cert")"; then
    save_cert=true
    
    # Create secure directory for revocation certificate if it doesn't exist
    local secure_dir="$HOME/secure/gpg/revocations"
    if [ ! -d "$secure_dir" ]; then
      mkdir -p "$secure_dir"
      chmod 700 "$secure_dir"
    fi
    
    local date_stamp=$(date "+%Y%m%d")
    local cert_path="$secure_dir/revoke_${key_short}_${date_stamp}.asc"
    gum style "$(_t "revoke_cert_path" "$cert_path")"
  fi
  
  # Generate revocation certificate
  local revoke_cert=$(mktemp)
  local revoke_options=""
  
  # Create batch file for revocation to avoid interactive prompts
  local batch_file=$(mktemp)
  
  # Adding commands to the batch file
  echo "y" > "$batch_file"
  echo "$reason_code" >> "$batch_file"
  
  if [ "$reason_code" = "0" ] && [ -n "$custom_reason" ]; then
    echo "$custom_reason" >> "$batch_file"
  fi
  
  echo "y" >> "$batch_file"
  
  # Generate the revocation certificate
  gum spin --title "$(_t "generating_revoke")" -- \
    gpg --batch --yes --command-fd 0 --output "$revoke_cert" --gen-revoke "$key_id" < "$batch_file"
  local gen_status=$?
  
  # Clean up batch file
  rm -f "$batch_file"
  
  if [ $gen_status -ne 0 ]; then
    show_error "$(_t "revoke_gen_failed")"
    rm -f "$revoke_cert"
    gum confirm "$(_t "press_enter")" && return
  fi
  
  # Save certificate if requested
  if [ "$save_cert" = true ]; then
    cp "$revoke_cert" "$cert_path"
    chmod 600 "$cert_path"
    show_success "$(_t "revoke_cert_saved" "$cert_path")"
  fi
  
  # Import the revocation certificate
  gum spin --title "$(_t "importing_revoke")" -- gpg --import "$revoke_cert"
  local import_status=$?
  
  # Clean up
  rm -f "$revoke_cert"
  
  if [ $import_status -ne 0 ]; then
    show_error "$(_t "revoke_import_failed")"
    gum confirm "$(_t "press_enter")" && return
  else
    show_success "$(_t "revoke_success")"
  fi
  
  # Ask if the user wants to distribute the revocation
  gum style ""
  gum style "$(_t "revoke_distribute_prompt")"
  
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
    
    # Send the revoked key to the keyserver
    gum spin --title "$(_t "publishing_revoke" "$keyserver")" -- gpg --keyserver "$keyserver" --send-keys "$key_id"
    
    if [ $? -eq 0 ]; then
      show_success "$(_t "revoke_publish_success" "$keyserver")"
    else
      show_error "$(_t "revoke_publish_failed")"
    fi
  fi
  
  # Final information
  gum style ""
  gum style "$(_t "revoke_final_note")"
  
  confirm_continue
  return
}

# Delete a key
delete_key() {
  local key_id=$(select_key "$(_t "select_key_delete")")
  
  if [ -z "$key_id" ]; then
    return
  fi
  
  show_warning "$(_t "delete_warning")"
  
  local delete_type=$(gum choose \
    "$(_t "delete_public_only")" \
    "$(_t "delete_public_private")" \
    "$(_t "cancel")")
  
  case "$delete_type" in
    "$(_t "delete_public_only")")
      if gum confirm "$(_t "delete_public_confirm")" --affirmative="$(_t "delete")" --negative="$(_t "cancel")"; then
        gpg --delete-key "$key_id"
        
        if [ $? -eq 0 ]; then
          show_success "$(_t "delete_success" "$(_t "public_key")")"
        else
          show_error "$(_t "delete_failed" "$(_t "public_key")")"
        fi
      fi
      ;;
    "$(_t "delete_public_private")")
      show_warning "$(_t "delete_both_warning")"
      show_warning "$(_t "delete_both_warning2")"
      
      if gum confirm "$(_t "delete_both_confirm")" --affirmative="$(_t "delete_both")" --negative="$(_t "cancel")"; then
        gpg --delete-secret-and-public-key "$key_id"
        
        if [ $? -eq 0 ]; then
          show_success "$(_t "delete_success" "$(_t "public_and_private_keys")")"
        else
          show_error "$(_t "delete_failed" "$(_t "keys")")"
        fi
      fi
      ;;
    "$(_t "cancel")")
      return
      ;;
  esac
  
  gum confirm "$(_t "press_enter")" && return
}