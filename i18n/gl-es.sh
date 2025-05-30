#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# gl-es.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# Spanish language file for GitLab CLI Installer
# License: AGPL-3.0

# Color settings using unique names to avoid conflicts with common.sh
TERM_COLOR_INFO="\033[1;34m"    # Bold Blue
TERM_COLOR_SUCCESS="\033[1;32m" # Bold Green
TERM_COLOR_WARNING="\033[1;33m" # Bold Yellow
TERM_COLOR_ERROR="\033[1;31m"   # Bold Red
TERM_COLOR_RESET="\033[0m"      # Reset color

# Register translations in the TRANSLATIONS associative array
TRANSLATIONS["msg_banner_title"]="Instalador de GitLab CLI"
TRANSLATIONS["msg_banner_subtitle"]="MR*Developer Tools"
TRANSLATIONS["msg_start"]="Iniciando instalación de GitLab CLI..."
TRANSLATIONS["msg_root_required"]="Este script requiere privilegios de administrador para la instalación."
TRANSLATIONS["msg_root_attempt"]="Intentando elevar privilegios..."
TRANSLATIONS["msg_root_unavailable"]="Sudo no está disponible. Por favor, ejecute este script como root."
TRANSLATIONS["msg_check_system"]="Verificando requisitos del sistema..."
TRANSLATIONS["msg_pkg_detected"]="Gestor de paquetes detectado:"
TRANSLATIONS["msg_install_deps"]="Instalando dependencias..."
TRANSLATIONS["msg_deps_fail"]="Error al instalar dependencias. Por favor, instálelas manualmente."
TRANSLATIONS["msg_system_success"]="Verificación del sistema completada con éxito."
TRANSLATIONS["msg_install_glab"]="Instalando GitLab CLI..."
TRANSLATIONS["msg_install_debian"]="Instalando para Debian/Ubuntu..."
TRANSLATIONS["msg_install_fedora"]="Instalando para Fedora/RHEL/CentOS..."
TRANSLATIONS["msg_install_suse"]="Instalando para openSUSE..."
TRANSLATIONS["msg_install_arch"]="Instalando para Arch Linux..."
TRANSLATIONS["msg_install_brew"]="Instalando con Homebrew..."
TRANSLATIONS["msg_install_unsupported"]="Gestor de paquetes no compatible. Por favor, instale GitLab CLI manualmente."
TRANSLATIONS["msg_install_success"]="¡GitLab CLI instalado con éxito!"
TRANSLATIONS["msg_install_fail"]="Error al instalar GitLab CLI. Por favor, intente instalarlo manualmente."
TRANSLATIONS["msg_usage_intro"]="GitLab CLI ha sido instalado. Aquí hay algunos comandos comunes:"
TRANSLATIONS["msg_auth_section"]="Autenticación:"
TRANSLATIONS["msg_repo_section"]="Operaciones con repositorios:"
TRANSLATIONS["msg_mr_section"]="Merge requests e issues:"
TRANSLATIONS["msg_help_section"]="Para más información:"
TRANSLATIONS["msg_docs_link"]="Para documentación completa, visite: https://gitlab.com/gitlab-org/cli/-/blob/main/docs/index.md"
TRANSLATIONS["msg_complete"]="¡Instalación completada con éxito!"
TRANSLATIONS["msg_no_pkg_manager"]="No se encontró un gestor de paquetes compatible. Por favor, instale GitLab CLI manualmente."