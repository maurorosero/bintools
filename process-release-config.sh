#!/bin/bash
# Script para procesar la configuración de release
# Autor: Mauro Rosero Pérez

set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
CONFIG_FILE="release-config.yml"
TEMP_DIR=""
RELEASE_TYPE=""

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
        "VERBOSE")
            if [[ "${VERBOSE:-false}" == "true" ]]; then
                echo -e "${BLUE}[VERBOSE]${NC} $message"
            fi
            ;;
    esac
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

Script para procesar la configuración de release y crear paquetes

OPCIONES:
    -t, --type TYPE         Tipo de release (full, user, minimal)
    -o, --output DIR        Directorio de salida
    -c, --config FILE       Archivo de configuración (default: release-config.yml)
    -v, --verbose           Modo verbose
    -h, --help              Mostrar esta ayuda

TIPOS DE RELEASE:
    full                    Release completo (incluye todo)
    user                    Release de usuario (solo lo necesario)
    minimal                 Release mínimo (solo archivos principales)

EJEMPLOS:
    $0 --type user --output /tmp/release
    $0 -t full -o /tmp/full-release -v
    $0 --type minimal --config custom-config.yml

EOF
}

# Función para verificar si un archivo existe
file_exists() {
    local file="$1"
    [[ -f "$file" ]]
}

# Función para verificar si un directorio existe
dir_exists() {
    local dir="$1"
    [[ -d "$dir" ]]
}

# Función para verificar si un patrón coincide
matches_pattern() {
    local file="$1"
    local pattern="$2"
    
    # Convertir patrón glob a regex
    local regex=$(echo "$pattern" | sed 's/\./\\./g; s/\*/.*/g; s/\?/./g')
    
    if [[ "$file" =~ $regex ]]; then
        return 0
    else
        return 1
    fi
}

# Función para verificar si un archivo debe ser excluido
should_exclude() {
    local file="$1"
    local exclude_patterns=("${@:2}")
    
    for pattern in "${exclude_patterns[@]}"; do
        if matches_pattern "$file" "$pattern"; then
            return 0
        fi
    done
    
    return 1
}

# Función para leer configuración YAML (versión simple)
read_config() {
    local config_file="$1"
    local key="$2"
    
    # Leer valor de una clave específica del YAML
    awk "/^$key:/{flag=1;next}/^[a-zA-Z]/{flag=0}flag && /^[[:space:]]*-/{print \$0}" "$config_file" | \
    sed 's/^\s*-\s*//' | \
    sed 's/^"//' | sed 's/"$//'
}

# Función para procesar archivos principales
process_main_files() {
    local config_file="$1"
    local output_dir="$2"
    local exclude_patterns=("${@:3}")
    
    log "VERBOSE" "Procesando archivos principales..."
    
    local main_files
    mapfile -t main_files < <(read_config "$config_file" "main_files")
    
    for file in "${main_files[@]}"; do
        if [[ -n "$file" ]]; then
            if should_exclude "$file" "${exclude_patterns[@]}"; then
                log "VERBOSE" "Excluyendo archivo: $file"
                continue
            fi
            
            if file_exists "$file"; then
                log "VERBOSE" "Copiando archivo principal: $file"
                cp "$file" "$output_dir/"
            else
                log "WARNING" "Archivo principal no encontrado: $file"
            fi
        fi
    done
}

# Función para procesar directorios
process_directories() {
    local config_file="$1"
    local output_dir="$2"
    local exclude_patterns=("${@:3}")
    
    log "VERBOSE" "Procesando directorios..."
    
    local directories
    mapfile -t directories < <(read_config "$config_file" "directories")
    
    for dir in "${directories[@]}"; do
        if [[ -n "$dir" ]]; then
            if should_exclude "$dir" "${exclude_patterns[@]}"; then
                log "VERBOSE" "Excluyendo directorio: $dir"
                continue
            fi
            
            if dir_exists "$dir"; then
                log "VERBOSE" "Copiando directorio: $dir"
                cp -r "$dir" "$output_dir/"
            else
                log "WARNING" "Directorio no encontrado: $dir"
            fi
        fi
    done
}

# Función para procesar archivos opcionales según el tipo de release
process_optional_files() {
    local config_file="$1"
    local output_dir="$2"
    local release_type="$3"
    local exclude_patterns=("${@:4}")
    
    log "VERBOSE" "Procesando archivos opcionales para tipo: $release_type..."
    
    # Definir archivos opcionales según el tipo de release
    case "$release_type" in
        "full")
            local optional_categories=("documentation" "development" "project_config")
            ;;
        "user")
            local optional_categories=("documentation")
            ;;
        "minimal")
            local optional_categories=()
            ;;
        *)
            log "WARNING" "Tipo de release desconocido: $release_type"
            return 0
            ;;
    esac
    
    # Procesar cada categoría
    for category in "${optional_categories[@]}"; do
        log "VERBOSE" "Procesando categoría opcional: $category"
        
        local optional_files
        mapfile -t optional_files < <(read_config "$config_file" "optional_files.$category")
        
        for file in "${optional_files[@]}"; do
            if [[ -n "$file" ]]; then
                if should_exclude "$file" "${exclude_patterns[@]}"; then
                    log "VERBOSE" "Excluyendo archivo opcional: $file"
                    continue
                fi
                
                if file_exists "$file"; then
                    log "VERBOSE" "Copiando archivo opcional: $file"
                    cp "$file" "$output_dir/"
                else
                    log "WARNING" "Archivo opcional no encontrado: $file"
                fi
            fi
        done
    done
}

# Función para crear archivos de configuración
create_config_files() {
    local output_dir="$1"
    local version="$2"
    
    log "VERBOSE" "Creando archivos de configuración..."
    
    # Crear archivo VERSION
    echo "$version" > "$output_dir/VERSION"
    
    # Crear archivo RELEASE_INFO
    cat > "$output_dir/RELEASE_INFO" << EOF
bintools $version
Released: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Repository: https://github.com/maurorosero/bintools
Install: curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --version $version
EOF
}

# Función para crear paquete
create_package() {
    local output_dir="$1"
    local version="$2"
    local package_name="bintools-$version"
    
    log "INFO" "Creando paquete: $package_name.tar.gz"
    
    # Crear paquete tar.gz
    cd "$(dirname "$output_dir")"
    tar -czf "$package_name.tar.gz" "$(basename "$output_dir")/"
    
    # Mostrar información del paquete
    log "SUCCESS" "Paquete creado: $package_name.tar.gz"
    log "INFO" "Tamaño: $(du -h "$package_name.tar.gz" | cut -f1)"
    
    # Mostrar contenido
    log "INFO" "Contenido del paquete:"
    tar -tzf "$package_name.tar.gz" | sed 's/^/  /'
    
    echo "$(pwd)/$package_name.tar.gz"
}

# Función principal
main() {
    local release_type=""
    local output_dir=""
    local config_file="$CONFIG_FILE"
    local verbose=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                release_type="$2"
                shift 2
                ;;
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -c|--config)
                config_file="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
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
    if [[ -z "$release_type" ]]; then
        log "ERROR" "Debe especificar un tipo de release con --type"
        show_help
        exit 1
    fi
    
    if [[ -z "$output_dir" ]]; then
        log "ERROR" "Debe especificar un directorio de salida con --output"
        show_help
        exit 1
    fi
    
    # Verificar archivo de configuración
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "Archivo de configuración no encontrado: $config_file"
        exit 1
    fi
    
    # Crear directorio de salida
    mkdir -p "$output_dir"
    
    # Leer patrones de exclusión
    local exclude_patterns
    mapfile -t exclude_patterns < <(read_config "$config_file" "exclude_patterns")
    
    log "INFO" "Procesando release tipo: $release_type"
    log "VERBOSE" "Directorio de salida: $output_dir"
    log "VERBOSE" "Archivo de configuración: $config_file"
    
    # Procesar archivos según la configuración
    process_main_files "$config_file" "$output_dir" "${exclude_patterns[@]}"
    process_directories "$config_file" "$output_dir" "${exclude_patterns[@]}"
    process_optional_files "$config_file" "$output_dir" "$release_type" "${exclude_patterns[@]}"
    
    # Crear archivos de configuración
    local version
    version=$(cat VERSION 2>/dev/null || echo "v1.0.0")
    create_config_files "$output_dir" "$version"
    
    # Crear paquete
    local package_file
    package_file=$(create_package "$output_dir" "$version")
    
    log "SUCCESS" "🎉 Procesamiento completado!"
    log "INFO" "Paquete creado: $package_file"
}

# Ejecutar función principal
main "$@"