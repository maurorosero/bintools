#!/bin/bash

# Script de instalación de paquetes multiplataforma
# Compatible con Ubuntu, Debian, Fedora, CentOS, Arch Linux y macOS
# Autor: mrosero
# Versión: 1.0

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables globales
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/configs"
DRY_RUN=false
VERBOSE=false
LIST=""

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

Script de instalación de paquetes multiplataforma

OPCIONES:
    -l, --list LISTA     Lista de paquetes a instalar (base, devs, orgs, user, all)
    -d, --dry-run        Solo mostrar qué se instalaría, sin instalar realmente
    -v, --verbose        Mostrar información detallada
    -h, --help           Mostrar esta ayuda

EJEMPLOS:
    $0 --list base                    # Instalar paquetes base
    $0 --list base,devs              # Instalar múltiples listas
    $0 --list all --dry-run          # Ver qué se instalaría
    $0 --list user --verbose         # Instalar con información detallada

LISTAS DISPONIBLES:
    base    Paquetes esenciales del sistema
    devs    Paquetes para desarrollo
    orgs    Paquetes para organización/productividad
    user    Paquetes personalizados del usuario
    all     Todas las listas disponibles

FORMATO DE ARCHIVOS:
    Los archivos de configuración están en configs/ con formato:
    OS:Manejador:Paquete:Descripción

EOF
}

# Función para logging
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
        "VERBOSE")
            if [[ "$VERBOSE" == "true" ]]; then
                echo -e "${BLUE}[VERBOSE]${NC} $message"
            fi
            ;;
    esac
}

# Función para detectar el OS
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        case "$ID" in
            ubuntu)
                echo "ubuntu"
                ;;
            debian)
                echo "debian"
                ;;
            fedora)
                echo "fedora"
                ;;
            centos|rhel)
                echo "centos"
                ;;
            arch|manjaro)
                echo "arch"
                ;;
            *)
                log "WARNING" "OS no soportado: $ID"
                echo "unknown"
                ;;
        esac
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        log "ERROR" "No se pudo detectar el OS"
        exit 1
    fi
}

# Función para verificar si snap está disponible
check_snap() {
    if command -v snap >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Función para instalar un paquete
install_package() {
    local manager="$1"
    local package="$2"
    local description="$3"
    
    log "INFO" "Instalando: $package - $description"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "[DRY-RUN] Se instalaría: $package usando $manager"
        return 0
    fi
    
    case "$manager" in
        apt)
            if ! sudo apt update >/dev/null 2>&1; then
                log "WARNING" "No se pudo actualizar la lista de paquetes"
            fi
            if sudo apt install -y "$package"; then
                log "SUCCESS" "Instalado: $package"
                return 0
            fi
            ;;
        dnf)
            if sudo dnf install -y "$package"; then
                log "SUCCESS" "Instalado: $package"
                return 0
            fi
            ;;
        yum)
            if sudo yum install -y "$package"; then
                log "SUCCESS" "Instalado: $package"
                return 0
            fi
            ;;
        pacman)
            # Verificar si el paquete ya está instalado
            if pacman -Q "$package" >/dev/null 2>&1; then
                log "INFO" "Paquete $package ya está instalado"
                return 0
            fi
            if sudo pacman -S --noconfirm "$package"; then
                log "SUCCESS" "Instalado: $package"
                return 0
            fi
            ;;
        yay)
            if command -v yay >/dev/null 2>&1; then
                # Verificar si el paquete ya está instalado
                if yay -Q "$package" >/dev/null 2>&1; then
                    log "INFO" "Paquete $package ya está instalado"
                    return 0
                fi
                if yay -S --noconfirm "$package"; then
                    log "SUCCESS" "Instalado: $package"
                    return 0
                fi
            else
                log "WARNING" "yay no está instalado, intentando con pacman para: $package"
                # Verificar si el paquete ya está instalado con pacman
                if pacman -Q "$package" >/dev/null 2>&1; then
                    log "INFO" "Paquete $package ya está instalado"
                    return 0
                fi
                if sudo pacman -S --noconfirm "$package"; then
                    log "SUCCESS" "Instalado: $package (con pacman)"
                    return 0
                fi
            fi
            ;;
        brew)
            if brew install "$package"; then
                log "SUCCESS" "Instalado: $package"
                return 0
            fi
            ;;
        snap)
            if sudo snap install "$package"; then
                log "SUCCESS" "Instalado: $package"
                return 0
            fi
            ;;
        *)
            log "ERROR" "Manejador de paquetes no soportado: $manager"
            return 1
            ;;
    esac
    
    # Si llegamos aquí, la instalación falló
    log "WARNING" "Falló la instalación de $package con $manager"
    return 1
}

# Función para procesar una lista de paquetes
process_package_list() {
    local package_file="$1"
    local os="$2"
    
    if [[ ! -f "$package_file" ]]; then
        log "ERROR" "Archivo no encontrado: $package_file"
        return 1
    fi
    
    log "INFO" "Procesando lista: $(basename "$package_file" .pkg)"
    
    local packages_found=0
    local packages_installed=0
    local packages_failed=0
    
    while IFS= read -r line; do
        # Saltar líneas vacías y comentarios
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Parsear línea: OS:Manejador:Paquete:Descripción
        IFS=':' read -r line_os manager package description <<< "$line"
        
        if [[ "$line_os" == "$os" ]]; then
            packages_found=$((packages_found + 1))
            
            log "VERBOSE" "Procesando: $package ($manager)"
            
            if install_package "$manager" "$package" "$description"; then
                packages_installed=$((packages_installed + 1))
            else
                # Intentar con snap como fallback si está disponible
                if check_snap; then
                    log "INFO" "Intentando con snap como fallback para: $package"
                    if install_package "snap" "$package" "$description"; then
                        packages_installed=$((packages_installed + 1))
                    else
                        packages_failed=$((packages_failed + 1))
                    fi
                else
                    packages_failed=$((packages_failed + 1))
                fi
            fi
        fi
    done < "$package_file"
    
    log "INFO" "Resumen: $packages_found encontrados, $packages_installed instalados, $packages_failed fallaron"
    
    if [[ $packages_failed -gt 0 ]]; then
        return 1
    fi
}

# Función principal
main() {
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -l|--list)
                LIST="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validar argumentos requeridos
    if [[ -z "$LIST" ]]; then
        log "ERROR" "Debe especificar una lista con --list"
        show_help
        exit 1
    fi
    
    # Detectar OS
    local os=$(detect_os)
    log "INFO" "OS detectado: $os"
    
    if [[ "$os" == "unknown" ]]; then
        log "ERROR" "OS no soportado"
        exit 1
    fi
    
    # Verificar si snap está disponible
    if check_snap; then
        log "VERBOSE" "Snap está disponible como fallback"
    else
        log "VERBOSE" "Snap no está disponible"
    fi
    
    # Procesar listas
    local lists
    if [[ "$LIST" == "all" ]]; then
        lists="base devs orgs user"
    else
        lists=$(echo "$LIST" | tr ',' ' ')
    fi
    
    local total_failed=0
    
    for list in $lists; do
        local package_file="$CONFIG_DIR/${list}.pkg"
        
        if [[ -f "$package_file" ]]; then
            if ! process_package_list "$package_file" "$os"; then
                total_failed=$((total_failed + 1))
            fi
        else
            log "WARNING" "Archivo no encontrado: $package_file"
            total_failed=$((total_failed + 1))
        fi
    done
    
    # Resumen final
    if [[ $total_failed -eq 0 ]]; then
        log "SUCCESS" "Todas las listas procesadas exitosamente"
        exit 0
    else
        log "ERROR" "Algunas listas fallaron"
        exit 1
    fi
}

# Ejecutar función principal
main "$@"
