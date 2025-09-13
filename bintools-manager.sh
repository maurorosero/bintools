#!/bin/bash
# bintools version manager
# Author: Mauro Rosero Pérez
# Repository: https://github.com/maurorosero/bintools

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
PROJECT_NAME="bintools"
REPO_OWNER="maurorosero"
REPO_NAME="bintools"
GITHUB_API="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}"
INSTALLER_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/install.sh"

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 COMANDO [OPCIONES]

Gestor de versiones de bintools

COMANDOS:
    install VERSION     Instalar versión específica
    update             Actualizar a la última versión
    version            Mostrar versión instalada
    list               Listar versiones disponibles
    uninstall          Desinstalar bintools
    info               Mostrar información de la instalación
    check              Verificar integridad de la instalación

EJEMPLOS:
    $0 install v1.0.0          # Instalar versión específica
    $0 update                  # Actualizar a última versión
    $0 version                 # Ver versión instalada
    $0 list                    # Ver versiones disponibles
    $0 uninstall               # Desinstalar completamente
    $0 info                    # Información de instalación
    $0 check                   # Verificar instalación

OPCIONES:
    -h, --help         Mostrar esta ayuda
    --verbose          Mostrar información detallada

EOF
}

# Función para logging
log() {
    local level="$1"
    shift
    local message="$*"
    
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
    esac
}

# Función para encontrar directorio de instalación
find_installation() {
    local possible_dirs=("$HOME/bin" "$HOME/bintools" "/opt/bintools" "/usr/local/bin/bintools")
    
    for dir in "${possible_dirs[@]}"; do
        if [[ -f "$dir/packages.sh" ]] && [[ -f "$dir/VERSION" ]]; then
            echo "$dir"
            return 0
        fi
    done
    
    return 1
}

# Función para obtener la última versión
get_latest_version() {
    curl -s "${GITHUB_API}/releases/latest" | \
    grep '"tag_name":' | \
    sed -E 's/.*"([^"]+)".*/\1/'
}

# Función para listar versiones disponibles
list_versions() {
    log "INFO" "Obteniendo versiones disponibles..."
    
    local versions
    versions=$(curl -s "${GITHUB_API}/releases" | \
               grep '"tag_name":' | \
               sed -E 's/.*"([^"]+)".*/\1/' | \
               head -10)
    
    if [[ -n "$versions" ]]; then
        echo "Versiones disponibles:"
        echo "$versions" | while read -r version; do
            echo "  - $version"
        done
    else
        log "ERROR" "No se pudieron obtener las versiones"
        return 1
    fi
}

# Función para instalar versión específica
install_version() {
    local version="$1"
    
    if [[ -z "$version" ]]; then
        log "ERROR" "Debe especificar una versión"
        return 1
    fi
    
    log "INFO" "Instalando ${PROJECT_NAME} $version..."
    
    if curl -fsSL "$INSTALLER_URL" | bash -s -- --version "$version"; then
        log "SUCCESS" "Instalación completada"
    else
        log "ERROR" "Error en la instalación"
        return 1
    fi
}

# Función para actualizar a última versión
update_to_latest() {
    local latest_version
    latest_version=$(get_latest_version)
    
    if [[ -z "$latest_version" ]]; then
        log "ERROR" "No se pudo obtener la última versión"
        return 1
    fi
    
    log "INFO" "Actualizando a $latest_version..."
    install_version "$latest_version"
}

# Función para mostrar versión instalada
show_version() {
    local install_dir
    if install_dir=$(find_installation); then
        local version
        version=$(cat "$install_dir/VERSION")
        log "SUCCESS" "Versión instalada: $version"
        log "INFO" "Ubicación: $install_dir"
    else
        log "ERROR" "${PROJECT_NAME} no está instalado"
        return 1
    fi
}

# Función para mostrar información de instalación
show_info() {
    local install_dir
    if install_dir=$(find_installation); then
        local version
        version=$(cat "$install_dir/VERSION")
        
        echo "=== Información de ${PROJECT_NAME} ==="
        echo "Versión: $version"
        echo "Ubicación: $install_dir"
        echo "Fecha de instalación: $(stat -c %y "$install_dir/VERSION" 2>/dev/null || echo "Desconocida")"
        
        echo ""
        echo "Archivos instalados:"
        ls -la "$install_dir" | grep -E '\.(sh|py)$|^[^d].*[^/]$' | while read -r line; do
            echo "  $line"
        done
        
        echo ""
        echo "Configuraciones disponibles:"
        if [[ -d "$install_dir/configs" ]]; then
            ls -la "$install_dir/configs" | grep '\.pkg$' | while read -r line; do
                echo "  $line"
            done
        fi
        
        echo ""
        echo "Comandos disponibles:"
        echo "  packages, micursor, pymanager, fix_hdmi_audio, videoset, nextcloud-installer, hexroute"
        
    else
        log "ERROR" "${PROJECT_NAME} no está instalado"
        return 1
    fi
}

# Función para verificar instalación
check_installation() {
    local install_dir
    if install_dir=$(find_installation); then
        log "INFO" "Verificando instalación en $install_dir..."
        
        local version
        version=$(cat "$install_dir/VERSION")
        
        # Verificar archivos principales
        local required_files=("packages.sh" "micursor.py" "pymanager.sh" "VERSION")
        local missing_files=()
        
        for file in "${required_files[@]}"; do
            if [[ -f "$install_dir/$file" ]]; then
                log "SUCCESS" "✓ $file"
            else
                missing_files+=("$file")
                log "ERROR" "✗ $file (faltante)"
            fi
        done
        
        # Verificar directorio de configuraciones
        if [[ -d "$install_dir/configs" ]]; then
            log "SUCCESS" "✓ Directorio configs"
        else
            log "ERROR" "✗ Directorio configs (faltante)"
        fi
        
        # Verificar permisos de ejecución
        local executable_files=("packages.sh" "micursor.py" "pymanager.sh" "fix_hdmi_audio.sh" "videoset.sh" "nextcloud-installer.sh" "hexroute")
        for file in "${executable_files[@]}"; do
            if [[ -f "$install_dir/$file" ]]; then
                if [[ -x "$install_dir/$file" ]]; then
                    log "SUCCESS" "✓ $file (ejecutable)"
                else
                    log "WARNING" "⚠ $file (no ejecutable)"
                fi
            fi
        done
        
        if [[ ${#missing_files[@]} -eq 0 ]]; then
            log "SUCCESS" "Instalación verificada correctamente"
            log "INFO" "Versión: $version"
        else
            log "ERROR" "Instalación incompleta o corrupta"
            return 1
        fi
        
    else
        log "ERROR" "${PROJECT_NAME} no está instalado"
        return 1
    fi
}

# Función para desinstalar
uninstall() {
    local install_dir
    if install_dir=$(find_installation); then
        local version
        version=$(cat "$install_dir/VERSION")
        
        log "WARNING" "Esto eliminará completamente ${PROJECT_NAME} $version de $install_dir"
        echo -n "¿Continuar con la desinstalación? (y/n): "
        read -r confirm
        
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            log "INFO" "Desinstalando ${PROJECT_NAME}..."
            
            # Eliminar archivos de bintools
            rm -rf "$install_dir"
            
            log "SUCCESS" "${PROJECT_NAME} desinstalado completamente"
            log "INFO" "Los archivos fueron eliminados de $install_dir"
        else
            log "INFO" "Desinstalación cancelada"
        fi
    else
        log "ERROR" "${PROJECT_NAME} no está instalado"
        return 1
    fi
}

# Función principal
main() {
    local command=""
    local verbose=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            install|update|version|list|uninstall|info|check)
                command="$1"
                shift
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                if [[ -z "$command" ]]; then
                    log "ERROR" "Comando desconocido: $1"
                    show_help
                    exit 1
                else
                    # Argumento para el comando
                    break
                fi
                ;;
        esac
    done
    
    if [[ -z "$command" ]]; then
        log "ERROR" "Debe especificar un comando"
        show_help
        exit 1
    fi
    
    # Ejecutar comando
    case "$command" in
        "install")
            install_version "$1"
            ;;
        "update")
            update_to_latest
            ;;
        "version")
            show_version
            ;;
        "list")
            list_versions
            ;;
        "uninstall")
            uninstall
            ;;
        "info")
            show_info
            ;;
        "check")
            check_installation
            ;;
        *)
            log "ERROR" "Comando no implementado: $command"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
