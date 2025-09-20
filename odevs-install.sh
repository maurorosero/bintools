#!/bin/bash

# Script de instalación de odoodevs
# Autor: mrosero
# Descripción: Instala odoodevs con diferentes opciones según el tipo de instalación

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración por defecto
DEFAULT_WORKSPACE="workdevs"
DEFAULT_PROTOCOL="https"
ODOO_REPO="https://github.com/opentech-solutions/odoodevs.git"
ODOO_REPO_SSH="git@github.com:opentech-solutions/odoodevs.git"

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

Script de instalación de odoodevs

OPCIONES:
    -t, --type TYPE        Tipo de instalación (devs|latest|version) [requerido]
    -v, --version VER      Versión específica (solo para type=version)
    -w, --workspace DIR    Directorio de trabajo [default: $DEFAULT_WORKSPACE]
    -p, --protocol PROTO   Protocolo git (https|ssh) [default: $DEFAULT_PROTOCOL]
    -h, --help            Mostrar esta ayuda

TIPOS DE INSTALACIÓN:
    devs                  Para desarrolladores de odoodevs
    latest                Última versión para desarrolladores usuarios de odoo
    version               Versión específica para desarrollador usuario odoo

EJEMPLOS:
    $0 --type devs
    $0 --type devs --protocol ssh
    $0 --type latest --workspace my-odoo
    $0 --type version --version v1.0.0
    $0 --type version --version v1.0.0 --workspace custom-odoo

EOF
}

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Función para verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    local missing_deps=()
    
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Dependencias faltantes: ${missing_deps[*]}"
        log "Instala las dependencias faltantes y vuelve a ejecutar el script"
        exit 1
    fi
    
    log "Todas las dependencias están disponibles"
}

# Función para verificar conexión SSH
check_ssh_connection() {
    if [ "$PROTOCOL" = "ssh" ]; then
        log "Verificando conexión SSH con GitHub..."
        if ! ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            log_error "No se puede conectar a GitHub via SSH"
            log "Configura tu clave SSH o usa --protocol https"
            exit 1
        fi
        log "Conexión SSH verificada"
    fi
}

# Función para instalar tipo devs
install_devs() {
    log "Instalando odoodevs para desarrolladores..."
    
    local repo_url
    if [ "$PROTOCOL" = "ssh" ]; then
        repo_url="$ODOO_REPO_SSH"
    else
        repo_url="$ODOO_REPO"
    fi
    
    log_info "Clonando repositorio desde: $repo_url"
    log_info "Directorio de trabajo: $WORKSPACE"
    
    if [ -d "$WORKSPACE" ]; then
        log_warning "El directorio $WORKSPACE ya existe"
        read -p "¿Deseas eliminarlo y continuar? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$WORKSPACE"
            log "Directorio anterior eliminado"
        else
            log_error "Instalación cancelada"
            exit 1
        fi
    fi
    
    # Clonar repositorio
    git clone "$repo_url" "$WORKSPACE"
    
    if [ $? -eq 0 ]; then
        log "Repositorio clonado exitosamente"
        log_info "Cambiando al directorio: $WORKSPACE"
        cd "$WORKSPACE"
        
        # Ejecutar script de instalación si existe
        if [ -f "install.sh" ]; then
            log "Ejecutando script de instalación..."
            chmod +x install.sh
            ./install.sh
        else
            log_info "No se encontró script de instalación automática"
            log_info "Sigue las instrucciones en el README del repositorio"
        fi
        
        log "Instalación para desarrolladores completada"
        log_info "Directorio: $(pwd)"
    else
        log_error "Error al clonar el repositorio"
        exit 1
    fi
}

# Función para instalar tipo latest
install_latest() {
    log "Instalando última versión de odoodevs..."
    
    log_info "Descargando e instalando con script oficial..."
    
    # Usar el script oficial de instalación
    curl -fsSL https://raw.githubusercontent.com/opentech-solutions/odoodevs/main/install.sh | bash
    
    if [ $? -eq 0 ]; then
        log "Instalación de última versión completada"
    else
        log_error "Error en la instalación"
        exit 1
    fi
}

# Función para instalar versión específica
install_version() {
    if [ -z "$VERSION" ]; then
        log_error "Versión requerida para type=version"
        log "Usa: $0 --type version --version v1.0.0"
        exit 1
    fi
    
    log "Instalando versión específica: $VERSION"
    
    log_info "Descargando e instalando versión $VERSION..."
    
    # Usar el script oficial con versión específica
    curl -fsSL https://raw.githubusercontent.com/opentech-solutions/odoodevs/main/install.sh | bash -s -- --version "$VERSION"
    
    if [ $? -eq 0 ]; then
        log "Instalación de versión $VERSION completada"
    else
        log_error "Error en la instalación de versión $VERSION"
        exit 1
    fi
}

# Función principal de instalación
main_install() {
    case "$TYPE" in
        "devs")
            install_devs
            ;;
        "latest")
            install_latest
            ;;
        "version")
            install_version
            ;;
        *)
            log_error "Tipo de instalación inválido: $TYPE"
            log "Tipos válidos: devs, latest, version"
            exit 1
            ;;
    esac
}

# Función para mostrar resumen
show_summary() {
    echo
    log "=== RESUMEN DE INSTALACIÓN ==="
    log_info "Tipo: $TYPE"
    if [ "$TYPE" = "version" ]; then
        log_info "Versión: $VERSION"
    fi
    if [ "$TYPE" = "devs" ]; then
        log_info "Protocolo: $PROTOCOL"
        log_info "Workspace: $WORKSPACE"
    fi
    echo
    log "Instalación completada exitosamente!"
}

# Parseo de argumentos
TYPE=""
VERSION=""
WORKSPACE="$DEFAULT_WORKSPACE"
PROTOCOL="$DEFAULT_PROTOCOL"

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TYPE="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -w|--workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        -p|--protocol)
            PROTOCOL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validar argumentos requeridos
if [ -z "$TYPE" ]; then
    log_error "Tipo de instalación requerido"
    show_help
    exit 1
fi

# Validar tipo
if [[ ! "$TYPE" =~ ^(devs|latest|version)$ ]]; then
    log_error "Tipo inválido: $TYPE"
    log "Tipos válidos: devs, latest, version"
    exit 1
fi

# Validar protocolo
if [[ ! "$PROTOCOL" =~ ^(https|ssh)$ ]]; then
    log_error "Protocolo inválido: $PROTOCOL"
    log "Protocolos válidos: https, ssh"
    exit 1
fi

# Banner de inicio
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════╗
║         ODOODEVS INSTALLER           ║
║                                      ║
║  Instalador automático de odoodevs   ║
╚══════════════════════════════════════╝
EOF
echo -e "${NC}"

# Ejecutar instalación
log "Iniciando instalación de odoodevs..."
log_info "Configuración:"
log_info "  Tipo: $TYPE"
log_info "  Protocolo: $PROTOCOL"
log_info "  Workspace: $WORKSPACE"
if [ "$TYPE" = "version" ] && [ -n "$VERSION" ]; then
    log_info "  Versión: $VERSION"
fi
echo

check_dependencies
check_ssh_connection
main_install
show_summary
