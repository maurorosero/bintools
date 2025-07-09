#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Install Gemini CLI - Script para instalar Google Gemini CLI usando npx
#
# Copyright (C) 2025 MAURO ROSERO PÉREZ
# License: GPLv3
#
# File: gemini-install.sh
# Version: 0.3.0
# Author: Mauro Rosero P. <mauro.rosero@gmail.com>
# Assistant: Cursor AI (https://cursor.com)
# Created: 2025-01-27
#
# This file is managed by template_manager.py.
# Any changes to this header will be overwritten on the next fix.
#
# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

set -uo pipefail

# --- Variables globales --- #
SCRIPT_NAME="gemini-install.sh"
SCRIPT_VERSION="0.3.0"
SCRIPT_AUTHOR="Mauro Rosero P. <mauro.rosero@gmail.com>"

# Colores para output
COLOR_GREEN="\033[0;32m"
COLOR_YELLOW="\033[0;33m"
COLOR_RED="\033[0;31m"
COLOR_CYAN="\033[0;36m"
COLOR_BLUE="\033[0;34m"
COLOR_RESET="\033[0m"
BOLD="\033[1m"

# Configuración
GEMINI_CLI_PACKAGE="@google/gemini-cli"
LOG_DIR="$HOME/.logs"
LOG_FILE="$LOG_DIR/gemini-cli-install.log"

# --- Funciones de utilidad --- #

# Función para mostrar mensajes con colores
log_info() {
    echo -e "${COLOR_CYAN}[INFO]${COLOR_RESET} $1"
    echo "[INFO] $1 - $(date)" >> "$LOG_FILE"
}

log_success() {
    echo -e "${COLOR_GREEN}[SUCCESS]${COLOR_RESET} $1"
    echo "[SUCCESS] $1 - $(date)" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${COLOR_YELLOW}[WARNING]${COLOR_RESET} $1"
    echo "[WARNING] $1 - $(date)" >> "$LOG_FILE"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $1" >&2
    echo "[ERROR] $1 - $(date)" >> "$LOG_FILE"
}

# Función para mostrar el banner
show_banner() {
    clear
    local width=60

    printf '+%*s+\n' "$width" '' | tr ' ' '-'
    printf '|%*s%s%*s|\n' "$(( (width - 19) / 2 ))" '' "Gemini CLI Manager" "$(( (width - 19) / 2 ))" ''
    printf '|%*s|\n' "$width" ''
    printf '|%*s%s%*s|\n' "$(( (width - 12) / 2 ))" '' "Version: $SCRIPT_VERSION" "$(( (width - 12) / 2 ))" ''
    printf '|%*s%s%*s|\n' "$(( (width - ${#SCRIPT_AUTHOR}) / 2 ))" '' "$SCRIPT_AUTHOR" "$(( (width - ${#SCRIPT_AUTHOR}) / 2 ))" ''
    printf '+%*s+\n' "$width" '' | tr ' ' '-'
    echo
}

# Función para mostrar ayuda
show_help() {
    echo "Usage: $SCRIPT_NAME [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  install              Install Gemini CLI (default command)"
    echo "  uninstall            Uninstall Gemini CLI"
    echo "  update               Update Gemini CLI to latest version"
    echo "  check                Check if Gemini CLI is installed"
    echo "  version              Show current Gemini CLI version"
    echo "  set-alias [TYPE]     Set gemini alias (permanent|session|unset)"
    echo
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -v, --verbose        Enable verbose output"
    echo "  --force              Force installation/update"
    echo
    echo "Examples:"
    echo "  $SCRIPT_NAME                    # Install Gemini CLI"
    echo "  $SCRIPT_NAME install            # Install Gemini CLI"
    echo "  $SCRIPT_NAME uninstall          # Uninstall Gemini CLI"
    echo "  $SCRIPT_NAME update             # Update Gemini CLI"
    echo "  $SCRIPT_NAME check              # Check installation status"
    echo "  $SCRIPT_NAME version            # Show version"
    echo "  $SCRIPT_NAME set-alias permanent # Set permanent alias"
    echo "  $SCRIPT_NAME set-alias session  # Set session alias"
    echo "  $SCRIPT_NAME set-alias unset    # Remove permanent alias"
}

# Función para verificar dependencias
check_dependencies() {
    log_info "Verificando dependencias..."

    local missing_deps=()

    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("Node.js")
    fi

    # Verificar npm
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi

    # Verificar npx
    if ! command -v npx &> /dev/null; then
        missing_deps+=("npx")
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Dependencias faltantes: ${missing_deps[*]}"
        log_info "Por favor, instala Node.js y npm antes de continuar."
        log_info "Puedes descargarlos desde: https://nodejs.org/"
        exit 1
    fi

    # Verificar versiones mínimas
    local node_version
    node_version=$(node --version | sed 's/v//')
    local npm_version
    npm_version=$(npm --version)

    log_info "Node.js versión: $node_version"
    log_info "npm versión: $npm_version"

    # Verificar versión mínima de Node.js (20.0.0)
    local node_major
    node_major=$(echo "$node_version" | cut -d. -f1)

    if [[ "$node_major" -lt 20 ]]; then
        log_error "Node.js versión 20 o superior es requerida. Versión actual: $node_version"
        log_info "Por favor, actualiza Node.js desde: https://nodejs.org/"
        log_info "O usa un gestor de versiones como nvm:"
        log_info "  nvm install 20"
        log_info "  nvm use 20"
        exit 1
    fi

    log_success "Todas las dependencias están disponibles"
}

# Función para verificar conexión a internet
check_internet() {
    log_info "Verificando conexión a internet..."

    if ! curl --max-time 10 -s "https://google.com" > /dev/null; then
        log_error "No se puede conectar a internet"
        exit 1
    fi

    log_success "Conexión a internet verificada"
}

# Función para verificar si Gemini CLI está instalado
is_gemini_installed() {
    if npx --yes "$GEMINI_CLI_PACKAGE" --version &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Función para obtener la versión actual de Gemini CLI
get_gemini_version() {
    if is_gemini_installed; then
        npx --yes "$GEMINI_CLI_PACKAGE" --version 2>/dev/null | head -n1
    else
        echo "No instalado"
    fi
}

# Función para instalar Gemini CLI
install_gemini_cli() {
    log_info "Instalando Gemini CLI..."

    if is_gemini_installed; then
        local current_version
        current_version=$(get_gemini_version)
        log_warning "Gemini CLI ya está instalado (versión: $current_version)"

        if [[ "${FORCE:-false}" == "true" ]]; then
            log_info "Forzando reinstalación..."
        else
            read -p "¿Deseas reinstalar? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Instalación cancelada"
                return 0
            fi
        fi
    fi

    # Instalar usando npx
    log_info "Ejecutando: npx --yes $GEMINI_CLI_PACKAGE --help"

    if npx --yes "$GEMINI_CLI_PACKAGE" --help &> /dev/null; then
        log_success "Gemini CLI instalado correctamente"

        # Mostrar información de la instalación
        local version
        version=$(get_gemini_version)
        log_info "Versión instalada: $version"

        # Mostrar comandos disponibles
        log_info "Comandos disponibles:"
        npx --yes "$GEMINI_CLI_PACKAGE" --help 2>/dev/null | head -20

        return 0
    else
        log_error "Error al instalar Gemini CLI"
        return 1
    fi
}

# Función para desinstalar Gemini CLI
uninstall_gemini_cli() {
    log_info "Desinstalando Gemini CLI..."

    if ! is_gemini_installed; then
        log_warning "Gemini CLI no está instalado"
        return 0
    fi

    # Limpiar caché de npx
    log_info "Limpiando caché de npx..."
    npx --yes "$GEMINI_CLI_PACKAGE" --help &> /dev/null || true

    # Limpiar caché de npm
    if npm cache clean --force &> /dev/null; then
        log_success "Caché de npm limpiado"
    else
        log_warning "No se pudo limpiar el caché de npm"
    fi

    log_success "Gemini CLI desinstalado"
    log_info "Nota: npx descarga automáticamente los paquetes cuando se necesitan"
}

# Función para actualizar Gemini CLI
update_gemini_cli() {
    log_info "Actualizando Gemini CLI..."

    if ! is_gemini_installed; then
        log_warning "Gemini CLI no está instalado. Instalando..."
        install_gemini_cli
        return $?
    fi

    local current_version
    current_version=$(get_gemini_version)
    log_info "Versión actual: $current_version"

    # Limpiar caché para forzar descarga de la última versión
    log_info "Limpiando caché para obtener la última versión..."
    npm cache clean --force &> /dev/null

    # Ejecutar para descargar la última versión
    log_info "Descargando la última versión..."
    if npx --yes "$GEMINI_CLI_PACKAGE" --version &> /dev/null; then
        local new_version
        new_version=$(get_gemini_version)
        log_success "Gemini CLI actualizado correctamente"
        log_info "Nueva versión: $new_version"
        return 0
    else
        log_error "Error al actualizar Gemini CLI"
        return 1
    fi
}

# Función para verificar la instalación
check_installation() {
    log_info "Verificando instalación de Gemini CLI..."

    if is_gemini_installed; then
        local version
        version=$(get_gemini_version)
        log_success "Gemini CLI está instalado"
        log_info "Versión: $version"

        # Probar un comando básico
        log_info "Probando comando básico..."
        if npx --yes "$GEMINI_CLI_PACKAGE" --help &> /dev/null; then
            log_success "Gemini CLI funciona correctamente"
            return 0
        else
            log_error "Gemini CLI no funciona correctamente"
            return 1
        fi
    else
        log_error "Gemini CLI no está instalado"
        return 1
    fi
}

# Función para mostrar la versión
show_version() {
    local version
    version=$(get_gemini_version)

    if [[ "$version" == "No instalado" ]]; then
        log_warning "Gemini CLI no está instalado"
        exit 1
    else
        log_success "Versión de Gemini CLI: $version"
    fi
}

# Función para ejecutar un comando de Gemini CLI
run_gemini_command() {
    local command="$1"
    shift

    log_info "Ejecutando: gemini $command $*"

    if npx --yes "$GEMINI_CLI_PACKAGE" "$command" "$@"; then
        log_success "Comando ejecutado correctamente"
        return 0
    else
        log_error "Error al ejecutar el comando"
        return 1
    fi
}

# Función para detectar el archivo de configuración del shell
get_shell_config_file() {
    if [[ -n "$BASH_VERSION" ]]; then
        echo "$HOME/.bashrc"
    elif [[ -n "$ZSH_VERSION" ]]; then
        echo "$HOME/.zshrc"
    else
        echo "$HOME/.profile"
    fi
}

# Función para verificar si el alias ya existe
alias_exists() {
    local config_file="$1"
    if grep -q "^alias gemini=" "$config_file" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Función para establecer alias permanente
set_permanent_alias() {
    local config_file
    config_file=$(get_shell_config_file)

    log_info "Configurando alias permanente en $config_file"

    # Verificar si el alias ya existe
    if alias_exists "$config_file"; then
        log_warning "El alias 'gemini' ya existe en $config_file"
        read -p "¿Deseas sobrescribirlo? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Operación cancelada"
            return 0
        fi

        # Remover alias existente
        sed -i '/^alias gemini=/d' "$config_file"
        log_info "Alias anterior removido"
    fi

    # Agregar nuevo alias
    echo -e "\n# Gemini CLI alias\nalias gemini=\"npx @google/gemini-cli\"" >> "$config_file"

    log_success "Alias 'gemini' configurado permanentemente en $config_file"
    log_info "El alias estará disponible en nuevas sesiones de terminal"
    log_info "Para usar en la sesión actual, ejecuta: source $config_file"
}

# Función para establecer alias de sesión
set_session_alias() {
    log_info "Configurando alias para la sesión actual"

    # Establecer el alias directamente
    alias gemini="npx @google/gemini-cli"

    # Verificar que se estableció correctamente
    if alias | grep -q "gemini="; then
        log_success "Alias 'gemini' configurado para esta sesión"
        log_info "Puedes usar 'gemini' directamente en esta terminal"
        log_info "Nota: Este alias se perderá al cerrar la terminal"

        # Mostrar el alias configurado
        log_info "Alias configurado: $(alias gemini)"

        # Mostrar instrucciones para usar el alias
        echo -e "\n${COLOR_GREEN}Para usar el alias en esta sesión, ejecuta:${COLOR_RESET}"
        echo "alias gemini=\"npx @google/gemini-cli\""

        return 0
    else
        log_error "Error al configurar el alias de sesión"
        return 1
    fi
}

# Función para remover alias permanente
unset_permanent_alias() {
    local config_file
    config_file=$(get_shell_config_file)

    log_info "Removiendo alias permanente de $config_file"

    if alias_exists "$config_file"; then
        # Crear backup antes de modificar
        cp "$config_file" "${config_file}.bak"

        # Remover alias
        sed -i '/^# Gemini CLI alias$/d' "$config_file"
        sed -i '/^alias gemini=/d' "$config_file"

        log_success "Alias 'gemini' removido de $config_file"
        log_info "Backup guardado en ${config_file}.bak"
        log_info "Los cambios se aplicarán en nuevas sesiones de terminal"
    else
        log_warning "No se encontró alias 'gemini' en $config_file"
    fi
}

# Función para gestionar alias
manage_alias() {
    local alias_type="$1"

    case "$alias_type" in
        permanent)
            set_permanent_alias
            ;;
        session)
            set_session_alias
            ;;
        unset)
            unset_permanent_alias
            ;;
        *)
            log_error "Tipo de alias inválido: $alias_type"
            log_info "Tipos válidos: permanent, session, unset"
            return 1
            ;;
    esac
}

# --- Función principal --- #
main() {
    # Crear directorio de logs
    mkdir -p "$LOG_DIR"

    # Mostrar banner
    show_banner

    # Variables para opciones
    local command="install"
    local verbose=false
    local force=false
    local alias_type=""

    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            install|uninstall|update|check|version)
                command="$1"
                shift
                ;;
            set-alias)
                command="set-alias"
                shift
                if [[ $# -gt 0 && "$1" != -* ]]; then
                    alias_type="$1"
                    shift
                else
                    log_error "Tipo de alias requerido para set-alias"
                    log_info "Tipos válidos: permanent, session, unset"
                    exit 1
                fi
                ;;

            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            *)
                log_error "Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Configurar modo verbose
    if [[ "$verbose" == "true" ]]; then
        set -x
    fi

    # Configurar modo force
    if [[ "$force" == "true" ]]; then
        FORCE=true
    fi

    # Ejecutar comando
    case "$command" in
        install)
            check_dependencies
            check_internet
            install_gemini_cli
            ;;
        uninstall)
            uninstall_gemini_cli
            ;;
        update)
            check_dependencies
            check_internet
            update_gemini_cli
            ;;
        check)
            check_installation
            ;;
        version)
            show_version
            ;;
        set-alias)
            manage_alias "$alias_type"
            ;;

        *)
            log_error "Comando desconocido: $command"
            show_help
            exit 1
            ;;
    esac

    exit $?
}

# Ejecutar función principal
main "$@"
