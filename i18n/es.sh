#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# es.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# Spanish language file for GitHub CLI Installer
# License: AGPL-3.0

# Color settings using unique names to avoid conflicts with common.sh
TERM_COLOR_INFO="\033[1;34m"    # Bold Blue
TERM_COLOR_SUCCESS="\033[1;32m" # Bold Green
TERM_COLOR_WARNING="\033[1;33m" # Bold Yellow
TERM_COLOR_ERROR="\033[1;31m"   # Bold Red
TERM_COLOR_RESET="\033[0m"      # Reset color

# Register translations in the TRANSLATIONS associative array
# This is how the i18n system in gpg-manager.sh expects them
TRANSLATIONS["main_menu_title"]="Gestor de Claves GPG"
TRANSLATIONS["main_menu_subtitle"]="MR*Developer Tools"
TRANSLATIONS["msg_banner_title"]="Instalador de GitHub CLI"
TRANSLATIONS["msg_banner_subtitle"]="MR*Developer Tools"
TRANSLATIONS["msg_start"]="Iniciando instalación de GitHub CLI..."
TRANSLATIONS["msg_root_required"]="Este script requiere privilegios de administrador para la instalación."
TRANSLATIONS["msg_root_attempt"]="Intentando elevar privilegios..."
TRANSLATIONS["msg_root_unavailable"]="Sudo no está disponible. Por favor, ejecute este script como root."
TRANSLATIONS["msg_check_system"]="Verificando requisitos del sistema..."
TRANSLATIONS["msg_pkg_detected"]="Gestor de paquetes detectado:"
TRANSLATIONS["msg_install_curl"]="Instalando curl..."
TRANSLATIONS["msg_curl_fail"]="Error al instalar curl. Por favor, instálelo manualmente."
TRANSLATIONS["msg_system_success"]="Verificación del sistema completada con éxito."
TRANSLATIONS["msg_install_gh"]="Instalando GitHub CLI..."
TRANSLATIONS["msg_install_debian"]="Instalando para Debian/Ubuntu..."
TRANSLATIONS["msg_install_fedora"]="Instalando para Fedora/RHEL/CentOS..."
TRANSLATIONS["msg_install_suse"]="Instalando para openSUSE..."
TRANSLATIONS["msg_install_arch"]="Instalando para Arch Linux..."
TRANSLATIONS["msg_install_brew"]="Instalando con Homebrew..."
TRANSLATIONS["msg_install_unsupported"]="Gestor de paquetes no compatible. Por favor, instale GitHub CLI manualmente."
TRANSLATIONS["msg_install_success"]="¡GitHub CLI instalado con éxito!"
TRANSLATIONS["msg_install_fail"]="Error al instalar GitHub CLI. Por favor, intente instalarlo manualmente."
TRANSLATIONS["msg_usage_intro"]="GitHub CLI ha sido instalado. Aquí hay algunos comandos comunes:"
TRANSLATIONS["msg_auth_section"]="Autenticación:"
TRANSLATIONS["msg_repo_section"]="Operaciones con repositorios:"
TRANSLATIONS["msg_pr_section"]="Pull requests e issues:"
TRANSLATIONS["msg_help_section"]="Para más información:"
TRANSLATIONS["msg_docs_link"]="Para documentación completa, visite: https://cli.github.com/manual/"
TRANSLATIONS["msg_complete"]="¡Instalación completada con éxito!"
TRANSLATIONS["msg_no_pkg_manager"]="No se encontró un gestor de paquetes compatible. Por favor, instale GitHub CLI manualmente."

# Add essential core translations for the GPG manager to function
TRANSLATIONS["menu_create_key"]="Crear Clave GPG"
TRANSLATIONS["menu_list_keys"]="Listar/Ver Claves"
TRANSLATIONS["menu_manage_subkeys"]="Gestionar Subclaves"
TRANSLATIONS["menu_manage_identities"]="Gestionar Identidades"
TRANSLATIONS["menu_export_keys"]="Exportar Claves"
TRANSLATIONS["menu_import_keys"]="Importar Claves"
TRANSLATIONS["menu_revoke_key"]="Revocar Clave"
TRANSLATIONS["menu_delete_key"]="Eliminar Clave"
TRANSLATIONS["menu_git_integration"]="Integración con Git"
TRANSLATIONS["language_select"]="Seleccionar Idioma"
TRANSLATIONS["menu_exit"]="Salir"

# Keys management section
TRANSLATIONS["keys_management"]="Gestión de Claves GPG"
TRANSLATIONS["list_all_keys"]="Listar Todas las Claves"
TRANSLATIONS["view_key_details"]="Ver Detalles de Clave"
TRANSLATIONS["back"]="Volver"
TRANSLATIONS["show_all_keys"]="Mostrar Todas las Claves"
TRANSLATIONS["show_my_keys"]="Mostrar Mis Claves"
TRANSLATIONS["show_public_keys"]="Mostrar Claves Públicas"
TRANSLATIONS["gpg_keys_title"]="Claves GPG"
TRANSLATIONS["my_keys_header"]="Mis Claves (con Clave Privada)"
TRANSLATIONS["public_keys_header"]="Claves Públicas (de Otros)"
TRANSLATIONS["key_filter_prompt"]="Filtrar Claves a Mostrar"

# Import keys section
TRANSLATIONS["import_keys_title"]="Importar Claves GPG"
TRANSLATIONS["import_from_file"]="Importar desde Archivo"
TRANSLATIONS["import_from_keyserver"]="Importar desde Servidor de Claves"
TRANSLATIONS["import_from_url"]="Importar desde URL"
TRANSLATIONS["import_from_text"]="Importar desde Texto"
TRANSLATIONS["import_from_qr"]="Importar desde Código QR"
TRANSLATIONS["import_revocation_cert"]="Importar Certificado de Revocación"

# Create key section
TRANSLATIONS["create_key_title"]="Crear Nueva Clave GPG"
TRANSLATIONS["key_type_rsa"]="RSA 4096"
TRANSLATIONS["key_type_ecc"]="ECC (Ed25519)"
TRANSLATIONS["full_name"]="Nombre Completo"
TRANSLATIONS["email_address"]="Dirección de Correo"
TRANSLATIONS["comment_optional"]="Comentario (Opcional)"
TRANSLATIONS["never_expire"]="Nunca Expira"
TRANSLATIONS["expire_after"]="Expira Después de..."
TRANSLATIONS["error_name_empty"]="El nombre no puede estar vacío"
TRANSLATIONS["error_email_empty"]="El correo no puede estar vacío"