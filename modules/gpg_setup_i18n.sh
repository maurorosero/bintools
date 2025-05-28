#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# gpg_setup_i18n.sh - Description placeholder
# -----------------------------------------------------------------------------
#

# [Author] Cortana Rosero One <cortana@rosero.one>
# [Created] 2025-04-12 02:08:53
# [Modified] 2025-04-12 02:43:27
# [Generated] Created by Claude Code (claude-3-7-sonnet-20250304)
# Version: See bin/.version/VERSION

# GPG Manager - Installation Translations
# License: AGPL-3.0

# English translations
declare -A EN_TRANSLATIONS

EN_TRANSLATIONS["setup_title"]="GPG Key Manager - Setup Script"
EN_TRANSLATIONS["setup_description"]="This script will install all required dependencies for GPG Manager."
EN_TRANSLATIONS["sudo_required"]="Sudo privileges may be required to install system packages."
EN_TRANSLATIONS["detecting_os"]="Detecting operating system..."
EN_TRANSLATIONS["detected_os"]="Detected operating system: "
EN_TRANSLATIONS["checking_sudo"]="Checking for sudo privileges..."
EN_TRANSLATIONS["sudo_available"]="Sudo is available"
EN_TRANSLATIONS["sudo_not_available"]="Sudo is not available. You may need to run this script with 'sudo' or as root."

EN_TRANSLATIONS["installing_for_debian"]="Installing packages for Debian/Ubuntu..."
EN_TRANSLATIONS["installing_for_redhat"]="Installing packages for Fedora/RHEL/CentOS..."
EN_TRANSLATIONS["installing_for_arch"]="Installing packages for Arch Linux..."
EN_TRANSLATIONS["installing_for_macos"]="Installing packages for macOS..."
EN_TRANSLATIONS["installing_gpg"]="Installing GnuPG..."
EN_TRANSLATIONS["installing_gum"]="Installing Charm Gum..."
EN_TRANSLATIONS["adding_charm_repo"]="Adding Charm repository..."
EN_TRANSLATIONS["homebrew_not_found"]="Homebrew not found. Installing Homebrew..."
EN_TRANSLATIONS["yay_not_found"]="Warning: AUR helper 'yay' not found. Trying to install gum from source..."

EN_TRANSLATIONS["checking_deps"]="Checking for required dependencies..."
EN_TRANSLATIONS["required_deps_ok"]="✓ All required dependencies are installed"
EN_TRANSLATIONS["missing_required_deps"]="! Missing required dependencies: "
EN_TRANSLATIONS["optional_deps_ok"]="✓ All optional dependencies are installed"
EN_TRANSLATIONS["missing_optional_deps"]="! Missing optional dependencies: "

EN_TRANSLATIONS["optional_deps_info"]="Optional dependencies enable features like QR code generation/scanning and Git integration."
EN_TRANSLATIONS["install_optional_deps"]="Do you want to install optional dependencies? (y/n): "
EN_TRANSLATIONS["installing_qrencode"]="Installing qrencode for QR code generation..."
EN_TRANSLATIONS["installing_zbar"]="Installing zbar for QR code scanning..."
EN_TRANSLATIONS["installing_git"]="Installing git for version control..."
EN_TRANSLATIONS["optional_deps_success"]="Optional dependencies installed successfully!"
EN_TRANSLATIONS["skipping_optional_deps"]="Skipping optional dependencies installation."

EN_TRANSLATIONS["unsupported_os"]="Unsupported operating system: "
EN_TRANSLATIONS["install_manual_required"]="Please install the following required dependencies manually:"
EN_TRANSLATIONS["optional_deps_enhance"]="The following optional dependencies enhance functionality:"
EN_TRANSLATIONS["install_optional_info"]="Do you want information on how to install these optional dependencies? (y/n): "

EN_TRANSLATIONS["creating_secure_dirs"]="Creating secure directories..."
EN_TRANSLATIONS["secure_dirs_created"]="✓ Created secure directories with proper permissions"
EN_TRANSLATIONS["setup_gpg_manager"]="Setting up GPG Manager..."
EN_TRANSLATIONS["setup_complete"]="✓ GPG Manager setup complete"
EN_TRANSLATIONS["start_info"]="✓ You can now run './gpg-manager.sh' to start the application"

EN_TRANSLATIONS["installation_success"]="Installation successful! All dependencies are installed."
EN_TRANSLATIONS["run_command"]="Run ./gpg-manager.sh to start using GPG Manager."
EN_TRANSLATIONS["installation_partial"]="Installation partially complete."
EN_TRANSLATIONS["deps_not_installed"]="Some dependencies could not be installed automatically: "

# Spanish translations
declare -A ES_TRANSLATIONS

ES_TRANSLATIONS["setup_title"]="Gestor de Claves GPG - Script de Instalación"
ES_TRANSLATIONS["setup_description"]="Este script instalará todas las dependencias necesarias para el Gestor de Claves GPG."
ES_TRANSLATIONS["sudo_required"]="Es posible que se requieran privilegios de sudo para instalar paquetes del sistema."
ES_TRANSLATIONS["detecting_os"]="Detectando sistema operativo..."
ES_TRANSLATIONS["detected_os"]="Sistema operativo detectado: "
ES_TRANSLATIONS["checking_sudo"]="Verificando privilegios de sudo..."
ES_TRANSLATIONS["sudo_available"]="Sudo está disponible"
ES_TRANSLATIONS["sudo_not_available"]="Sudo no está disponible. Es posible que necesite ejecutar este script con 'sudo' o como root."

ES_TRANSLATIONS["installing_for_debian"]="Instalando paquetes para Debian/Ubuntu..."
ES_TRANSLATIONS["installing_for_redhat"]="Instalando paquetes para Fedora/RHEL/CentOS..."
ES_TRANSLATIONS["installing_for_arch"]="Instalando paquetes para Arch Linux..."
ES_TRANSLATIONS["installing_for_macos"]="Instalando paquetes para macOS..."
ES_TRANSLATIONS["installing_gpg"]="Instalando GnuPG..."
ES_TRANSLATIONS["installing_gum"]="Instalando Charm Gum..."
ES_TRANSLATIONS["adding_charm_repo"]="Añadiendo repositorio de Charm..."
ES_TRANSLATIONS["homebrew_not_found"]="Homebrew no encontrado. Instalando Homebrew..."
ES_TRANSLATIONS["yay_not_found"]="Advertencia: Asistente AUR 'yay' no encontrado. Intentando instalar gum desde el código fuente..."

ES_TRANSLATIONS["checking_deps"]="Verificando dependencias necesarias..."
ES_TRANSLATIONS["required_deps_ok"]="✓ Todas las dependencias requeridas están instaladas"
ES_TRANSLATIONS["missing_required_deps"]="! Faltan dependencias requeridas: "
ES_TRANSLATIONS["optional_deps_ok"]="✓ Todas las dependencias opcionales están instaladas"
ES_TRANSLATIONS["missing_optional_deps"]="! Faltan dependencias opcionales: "

ES_TRANSLATIONS["optional_deps_info"]="Las dependencias opcionales habilitan funciones como generación/escaneo de códigos QR e integración con Git."
ES_TRANSLATIONS["install_optional_deps"]="¿Desea instalar las dependencias opcionales? (s/n): "
ES_TRANSLATIONS["installing_qrencode"]="Instalando qrencode para generación de códigos QR..."
ES_TRANSLATIONS["installing_zbar"]="Instalando zbar para escaneo de códigos QR..."
ES_TRANSLATIONS["installing_git"]="Instalando git para control de versiones..."
ES_TRANSLATIONS["optional_deps_success"]="¡Dependencias opcionales instaladas con éxito!"
ES_TRANSLATIONS["skipping_optional_deps"]="Omitiendo instalación de dependencias opcionales."

ES_TRANSLATIONS["unsupported_os"]="Sistema operativo no soportado: "
ES_TRANSLATIONS["install_manual_required"]="Por favor, instale manualmente las siguientes dependencias requeridas:"
ES_TRANSLATIONS["optional_deps_enhance"]="Las siguientes dependencias opcionales mejoran la funcionalidad:"
ES_TRANSLATIONS["install_optional_info"]="¿Desea información sobre cómo instalar estas dependencias opcionales? (s/n): "

ES_TRANSLATIONS["creating_secure_dirs"]="Creando directorios seguros..."
ES_TRANSLATIONS["secure_dirs_created"]="✓ Se crearon directorios seguros con permisos adecuados"
ES_TRANSLATIONS["setup_gpg_manager"]="Configurando el Gestor de Claves GPG..."
ES_TRANSLATIONS["setup_complete"]="✓ Instalación del Gestor de Claves GPG completada"
ES_TRANSLATIONS["start_info"]="✓ Ahora puede ejecutar './gpg-manager.sh' para iniciar la aplicación"

ES_TRANSLATIONS["installation_success"]="¡Instalación exitosa! Todas las dependencias están instaladas."
ES_TRANSLATIONS["run_command"]="Ejecute ./gpg-manager.sh para comenzar a usar el Gestor de Claves GPG."
ES_TRANSLATIONS["installation_partial"]="Instalación parcialmente completada."
ES_TRANSLATIONS["deps_not_installed"]="Algunas dependencias no pudieron instalarse automáticamente: "

# Set active translations array based on system language
detect_language() {
    # Try to detect language from environment variables
    local SYSTEM_LANG=""
    for env_var in LC_ALL LC_MESSAGES LANG; do
        if [ -n "${!env_var}" ]; then
            # Extract language code (handling formats like en_US.UTF-8)
            SYSTEM_LANG=$(echo "${!env_var}" | cut -d_ -f1 | cut -d. -f1)
            [ -n "$SYSTEM_LANG" ] && break
        fi
    done

    # Set default language to English if no language detected
    if [ -z "$SYSTEM_LANG" ]; then
        SYSTEM_LANG="en"
    fi

    # Assign the appropriate translation array
    case "$SYSTEM_LANG" in
        es)
            # Use Spanish translations
            TRANSLATIONS=("${!ES_TRANSLATIONS[@]}")
            for key in "${!ES_TRANSLATIONS[@]}"; do
                TRANSLATIONS[$key]="${ES_TRANSLATIONS[$key]}"
            done
            ;;
        *)
            # Default to English translations
            TRANSLATIONS=("${!EN_TRANSLATIONS[@]}")
            for key in "${!EN_TRANSLATIONS[@]}"; do
                TRANSLATIONS[$key]="${EN_TRANSLATIONS[$key]}"
            done
            ;;
    esac
}

# Function to get translated text
# Usage: t "key"
t() {
    local key="$1"
    echo "${TRANSLATIONS[$key]}"
}

# Initialize translations
declare -A TRANSLATIONS
detect_language
