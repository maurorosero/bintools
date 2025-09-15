#!/bin/bash
# Script para gestionar instalación de repositorios por sistema operativo
# Autor: Mauro Rosero Pérez

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIÓN] [ARGUMENTO]"
    echo ""
    echo "OPCIONES:"
    echo "  --list                    Listar scripts de repositorio disponibles para el OS actual"
    echo "  --configure SCRIPT_NAME   Ejecutar script de configuración (sin extensión .sh)"
    echo "  --help                    Mostrar esta ayuda"
    echo ""
    echo "EJEMPLOS:"
    echo "  $0 --list                              # Listar scripts disponibles"
    echo "  $0 --configure setup-charm-repo        # Ejecutar script de configuración"
    echo ""
}

# Función para detectar el sistema operativo
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
            centos|rhel|rocky|almalinux)
                echo "centos"
                ;;
            arch|manjaro)
                echo "arch"
                ;;
            *)
                echo "unknown"
                ;;
        esac
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Función para listar scripts disponibles
list_scripts() {
    local os=$(detect_os)
    local repos_dir="repos/$os"
    
    echo -e "${BLUE}[INFO]${NC} Sistema operativo detectado: $os"
    echo -e "${BLUE}[INFO]${NC} Buscando scripts en: $repos_dir"
    echo ""
    
    if [[ ! -d "$repos_dir" ]]; then
        echo -e "${RED}[ERROR]${NC} Directorio $repos_dir no existe"
        echo -e "${YELLOW}[INFO]${NC} Sistemas soportados: ubuntu, debian, fedora, centos, arch, macos"
        return 1
    fi
    
    local scripts_found=0
    
    # Buscar archivos .sh en el directorio del OS
    for script in "$repos_dir"/*.sh; do
        if [[ -f "$script" ]]; then
            local script_name=$(basename "$script" .sh)
            echo -e "${GREEN}✓${NC} $script_name"
            ((scripts_found++))
        fi
    done
    
    if [[ $scripts_found -eq 0 ]]; then
        echo -e "${YELLOW}[WARNING]${NC} No se encontraron scripts en $repos_dir"
        return 1
    fi
    
    echo ""
    echo -e "${BLUE}[INFO]${NC} Total de scripts encontrados: $scripts_found"
}

# Función para ejecutar script de configuración
configure_script() {
    local script_name="$1"
    
    if [[ -z "$script_name" ]]; then
        echo -e "${RED}[ERROR]${NC} Se requiere el nombre del script"
        echo -e "${YELLOW}[INFO]${NC} Uso: $0 --configure SCRIPT_NAME"
        echo -e "${YELLOW}[INFO]${NC} Ejecuta '$0 --list' para ver scripts disponibles"
        return 1
    fi
    
    local os=$(detect_os)
    local repos_dir="repos/$os"
    local script_path="$repos_dir/$script_name.sh"
    
    echo -e "${BLUE}[INFO]${NC} Sistema operativo detectado: $os"
    echo -e "${BLUE}[INFO]${NC} Buscando script: $script_path"
    echo ""
    
    if [[ ! -d "$repos_dir" ]]; then
        echo -e "${RED}[ERROR]${NC} Directorio $repos_dir no existe"
        echo -e "${YELLOW}[INFO]${NC} Sistemas soportados: ubuntu, debian, fedora, centos, arch, macos"
        return 1
    fi
    
    if [[ ! -f "$script_path" ]]; then
        echo -e "${RED}[ERROR]${NC} Script '$script_name.sh' no encontrado en $repos_dir"
        echo -e "${YELLOW}[INFO]${NC} Scripts disponibles:"
        list_scripts
        return 1
    fi
    
    if [[ ! -x "$script_path" ]]; then
        echo -e "${RED}[ERROR]${NC} Script '$script_path' no tiene permisos de ejecución"
        return 1
    fi
    
    echo -e "${GREEN}[SUCCESS]${NC} Ejecutando script: $script_path"
    echo ""
    
    # Ejecutar el script
    "$script_path"
    local exit_code=$?
    
    echo ""
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}[SUCCESS]${NC} Script ejecutado exitosamente"
    else
        echo -e "${RED}[ERROR]${NC} Script falló con código de salida: $exit_code"
    fi
    
    return $exit_code
}

# Función principal
main() {
    case "${1:-}" in
        --list)
            list_scripts
            ;;
        --configure)
            configure_script "$2"
            ;;
        --help|-h)
            show_help
            ;;
        "")
            echo -e "${RED}[ERROR]${NC} Se requiere una opción"
            echo ""
            show_help
            exit 1
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Opción desconocida: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
