#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# fj-es.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# Spanish language file for Forgejo CLI Installer
# License: AGPL-3.0

# Color settings using unique names to avoid conflicts with common.sh
TERM_COLOR_INFO="\033[1;34m"    # Bold Blue
TERM_COLOR_SUCCESS="\033[1;32m" # Bold Green
TERM_COLOR_WARNING="\033[1;33m" # Bold Yellow
TERM_COLOR_ERROR="\033[1;31m"   # Bold Red
TERM_COLOR_RESET="\033[0m"      # Reset color

# Register translations in the TRANSLATIONS associative array
TRANSLATIONS["msg_banner_title"]="Instalador de Forgejo CLI"
TRANSLATIONS["msg_banner_subtitle"]="MR*Developer Tools"
TRANSLATIONS["msg_start"]="Iniciando instalación de Forgejo CLI..."
TRANSLATIONS["msg_root_required"]="Este script requiere privilegios de administrador para la instalación."
TRANSLATIONS["msg_root_attempt"]="Intentando elevar privilegios..."
TRANSLATIONS["msg_root_unavailable"]="Sudo no está disponible. Por favor, ejecute este script como root."
TRANSLATIONS["msg_check_system"]="Verificando requisitos del sistema..."
TRANSLATIONS["msg_pkg_detected"]="Gestor de paquetes detectado:"
TRANSLATIONS["msg_install_rust"]="Instalando entorno Rust..."
TRANSLATIONS["msg_rust_fail"]="Error al instalar Rust. Por favor, instálelo manualmente."
TRANSLATIONS["msg_system_success"]="Verificación del sistema completada con éxito."
TRANSLATIONS["msg_install_berg"]="Instalando Forgejo CLI (berg)..."
TRANSLATIONS["msg_install_cargo"]="Instalando con cargo..."
TRANSLATIONS["msg_install_unsupported"]="Sistema no compatible. Por favor, instale Forgejo CLI manualmente."
TRANSLATIONS["msg_install_success"]="¡Forgejo CLI instalado con éxito!"
TRANSLATIONS["msg_install_fail"]="Error al instalar Forgejo CLI. Por favor, intente instalarlo manualmente."
TRANSLATIONS["msg_usage_intro"]="Forgejo CLI ha sido instalado. Aquí hay algunos comandos comunes:"
TRANSLATIONS["msg_auth_section"]="Autenticación:"
TRANSLATIONS["msg_repo_section"]="Operaciones con repositorios:"
TRANSLATIONS["msg_pr_section"]="Pull requests e issues:"
TRANSLATIONS["msg_help_section"]="Para más información:"
TRANSLATIONS["msg_docs_link"]="Para documentación completa, ejecute: berg --help"
TRANSLATIONS["msg_complete"]="¡Instalación completada con éxito!"
TRANSLATIONS["msg_no_rust"]="No se encontró el entorno Rust. Por favor, instale Rust antes de continuar."