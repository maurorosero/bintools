#!/bin/bash

# btfixperms.sh - Establece permisos correctos y seguros para ambiente de desarrollo
# Autor: Mauro Rosero Pérez
# Descripción: Usa configs/release-config.yml para determinar qué archivos necesitan permisos específicos

set -euo pipefail

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/configs/release-config.yml"
VERBOSE=false
DRY_RUN=false

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función de logging
log() {
    local level="$1"
    shift
    local message="$*"
    
    case "$level" in
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "VERBOSE")
            if [[ "$VERBOSE" == "true" ]]; then
                echo -e "${BLUE}[VERBOSE]${NC} $message"
            fi
            ;;
    esac
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
btfixperms.sh - Establece permisos correctos y seguros para ambiente de desarrollo

USO:
    $0 [OPCIONES]

OPCIONES:
    -v, --verbose      Mostrar información detallada
    -d, --dry-run      Mostrar qué cambios se harían sin ejecutarlos
    -h, --help         Mostrar esta ayuda

DESCRIPCIÓN:
    Este script establece permisos seguros para todos los archivos del proyecto
    basándose en la configuración de configs/release-config.yml:
    
    • Scripts ejecutables: 755 (rwxr-xr-x)
    • Archivos de configuración: 644 (rw-r--r--)
    • Archivos de documentación: 644 (rw-r--r--)
    • Archivos sensibles: 600 (rw-------)
    • Directorios: 755 (rwxr-xr-x)

EJEMPLOS:
    $0                    # Aplicar permisos
    $0 --dry-run          # Ver qué cambios se harían
    $0 --verbose          # Mostrar información detallada

EOF
}

# Función para leer configuración YAML
read_yaml_list() {
    local config_file="$1"
    local key="$2"
    
    awk "
        /^$key:/ { in_section = 1; next }
        /^[a-zA-Z]/ && in_section { in_section = 0 }
        in_section && /^[[:space:]]*-/ {
            gsub(/^[[:space:]]*-[[:space:]]*/, \"\")
            gsub(/[\"']/, \"\")
            print
        }
    " "$config_file"
}

# Función para leer archivos opcionales por categoría
read_optional_files() {
    local config_file="$1"
    local category="$2"
    
    awk "
        /^[[:space:]]*$category:/ { in_category = 1; next }
        /^[[:space:]]*[a-zA-Z]/ && in_category { in_category = 0 }
        in_category && /^[[:space:]]*-/ {
            gsub(/^[[:space:]]*-[[:space:]]*/, \"\")
            gsub(/[\"']/, \"\")
            print
        }
    " "$config_file"
}

# Función para establecer permisos de un archivo
set_file_permissions() {
    local file="$1"
    local permissions="$2"
    local description="$3"
    
    if [[ ! -e "$file" ]]; then
        log "WARNING" "Archivo no encontrado: $file"
        return 1
    fi
    
    local current_perms
    current_perms=$(stat -c "%a" "$file" 2>/dev/null || echo "???")
    
    if [[ "$current_perms" == "$permissions" ]]; then
        log "VERBOSE" "✓ $file ya tiene permisos correctos ($permissions) - $description"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "SECO: chmod $permissions $file - $description (actual: $current_perms)"
    else
        if chmod "$permissions" "$file" 2>/dev/null; then
            log "SUCCESS" "✓ chmod $permissions $file - $description"
        else
            log "ERROR" "✗ Error estableciendo permisos para $file"
            return 1
        fi
    fi
}

# Función para establecer permisos de directorio
set_directory_permissions() {
    local dir="$1"
    local permissions="$2"
    local description="$3"
    
    if [[ ! -d "$dir" ]]; then
        log "WARNING" "Directorio no encontrado: $dir"
        return 1
    fi
    
    local current_perms
    current_perms=$(stat -c "%a" "$dir" 2>/dev/null || echo "???")
    
    if [[ "$current_perms" == "$permissions" ]]; then
        log "VERBOSE" "✓ $dir ya tiene permisos correctos ($permissions) - $description"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "SECO: chmod $permissions $dir - $description (actual: $current_perms)"
    else
        if chmod "$permissions" "$dir" 2>/dev/null; then
            log "SUCCESS" "✓ chmod $permissions $dir - $description"
        else
            log "ERROR" "✗ Error estableciendo permisos para $dir"
            return 1
        fi
    fi
}

# Función principal para establecer permisos
fix_permissions() {
    local errors=0
    
    log "INFO" "Estableciendo permisos seguros basados en $CONFIG_FILE"
    
    # 1. Scripts principales ejecutables (755)
    log "INFO" "📝 Estableciendo permisos para scripts principales..."
    while IFS= read -r file; do
        [[ -n "$file" ]] && set_file_permissions "$file" "755" "Script ejecutable principal" || ((errors++))
    done < <(read_yaml_list "$CONFIG_FILE" "main_files")
    
    # 2. Scripts de desarrollo ejecutables (755)
    log "INFO" "🔧 Estableciendo permisos para scripts de desarrollo..."
    while IFS= read -r file; do
        if [[ -n "$file" && "$file" == *.sh ]]; then
            set_file_permissions "$file" "755" "Script de desarrollo" || ((errors++))
        fi
    done < <(read_optional_files "$CONFIG_FILE" "development")
    
    # 3. Archivos de configuración (644)
    log "INFO" "⚙️ Estableciendo permisos para archivos de configuración..."
    while IFS= read -r file; do
        [[ -n "$file" ]] && set_file_permissions "$file" "644" "Archivo de configuración" || ((errors++))
    done < <(read_yaml_list "$CONFIG_FILE" "config_files")
    
    # 4. Archivos de documentación (644)
    log "INFO" "📚 Estableciendo permisos para archivos de documentación..."
    while IFS= read -r file; do
        [[ -n "$file" ]] && set_file_permissions "$file" "644" "Archivo de documentación" || ((errors++))
    done < <(read_optional_files "$CONFIG_FILE" "documentation")
    
    # 5. Archivos de configuración del proyecto (644)
    log "INFO" "🏗️ Estableciendo permisos para configuración del proyecto..."
    while IFS= read -r file; do
        [[ -n "$file" ]] && set_file_permissions "$file" "644" "Configuración del proyecto" || ((errors++))
    done < <(read_optional_files "$CONFIG_FILE" "project_config")
    
    # 6. Directorios principales (755)
    log "INFO" "📁 Estableciendo permisos para directorios..."
    while IFS= read -r dir; do
        [[ -n "$dir" ]] && set_directory_permissions "$dir" "755" "Directorio del proyecto" || ((errors++))
    done < <(read_yaml_list "$CONFIG_FILE" "directories")
    
    # 7. Directorios especiales
    for special_dir in ".github" "docs"; do
        if [[ -d "$special_dir" ]]; then
            set_directory_permissions "$special_dir" "755" "Directorio especial" || ((errors++))
        fi
    done
    
    # 8. Archivos específicos de configuración en configs/ (644)
    if [[ -d "configs" ]]; then
        log "INFO" "🔧 Estableciendo permisos para archivos en configs/..."
        find configs -type f -name "*.yml" -o -name "*.yaml" -o -name "*.pkg" | while IFS= read -r file; do
            set_file_permissions "$file" "644" "Archivo de configuración" || ((errors++))
        done
    fi
    
    # 9. Archivos sensibles (600) - si existen
    log "INFO" "🔒 Verificando archivos sensibles..."
    local sensitive_patterns=("*.key" "*.pem" "*.p12" ".env" "*secret*" "*password*")
    for pattern in "${sensitive_patterns[@]}"; do
        # Buscar archivos que coincidan con patrones sensibles (si existen)
        if compgen -G "$pattern" > /dev/null 2>&1; then
            for file in $pattern; do
                if [[ -f "$file" ]]; then
                    set_file_permissions "$file" "600" "Archivo sensible" || ((errors++))
                fi
            done
        fi
    done
    
    # 10. El propio btfixperms.sh debe ser ejecutable
    set_file_permissions "$0" "755" "Script de permisos" || ((errors++))
    
    # Resumen
    echo
    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "🔍 Modo de prueba completado. Use sin --dry-run para aplicar cambios."
    elif [[ $errors -eq 0 ]]; then
        log "SUCCESS" "🎉 Permisos establecidos correctamente para ambiente de desarrollo"
    else
        log "WARNING" "⚠️ Proceso completado con $errors errores/advertencias"
    fi
    
    return $errors
}

# Función para verificar dependencias
check_dependencies() {
    local missing_deps=()
    
    if ! command -v awk >/dev/null 2>&1; then
        missing_deps+=("awk")
    fi
    
    if ! command -v stat >/dev/null 2>&1; then
        missing_deps+=("stat")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log "ERROR" "Dependencias faltantes: ${missing_deps[*]}"
        log "INFO" "Instala las dependencias y vuelve a intentar"
        return 1
    fi
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log "ERROR" "Archivo de configuración no encontrado: $CONFIG_FILE"
        log "INFO" "Asegúrate de ejecutar este script desde la raíz del proyecto"
        return 1
    fi
    
    return 0
}

# Función principal
main() {
    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Opción desconocida: $1"
                log "INFO" "Usa --help para ver las opciones disponibles"
                exit 1
                ;;
        esac
    done
    
    # Verificar dependencias
    if ! check_dependencies; then
        exit 1
    fi
    
    # Mostrar información inicial
    log "INFO" "=== Fix Permissions for Development Environment ==="
    log "INFO" "Directorio de trabajo: $SCRIPT_DIR"
    log "INFO" "Archivo de configuración: $CONFIG_FILE"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "🔍 MODO DE PRUEBA: Se mostrarán los cambios sin aplicarlos"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        log "INFO" "📊 MODO VERBOSE: Se mostrará información detallada"
    fi
    
    echo
    
    # Ejecutar corrección de permisos
    if fix_permissions; then
        exit 0
    else
        exit 1
    fi
}

# Ejecutar función principal si el script es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
