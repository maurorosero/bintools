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
DEFAULT_WORKSPACE_DEVS="odoodevs"  # Para modo developers (clonación)
DEFAULT_WORKSPACE_INSTALL="odoo"   # Para modo install (latest/version)
DEFAULT_PROTOCOL="https"
ODOO_REPO="https://github.com/opentech-solutions/odoodevs.git"
ODOO_REPO_SSH="git@github.com:opentech-solutions/odoodevs.git"

# Información del repositorio odoodevs
ODOO_REPO_OWNER="opentech-solutions"
ODOO_REPO_NAME="odoodevs"
ODOO_GITHUB_API="https://api.github.com/repos/${ODOO_REPO_OWNER}/${ODOO_REPO_NAME}"
ODOO_RELEASE_URL="https://github.com/${ODOO_REPO_OWNER}/${ODOO_REPO_NAME}/releases/download"

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

Script de instalación de odoodevs

OPCIONES:
    -t, --type TYPE        Tipo de instalación (devs|latest|version) [requerido]
    -v, --version VER      Versión específica (solo para type=version)
    -w, --workspace DIR    Directorio de trabajo [default: odoodevs para devs, odoo para install]
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

# Función para obtener la última versión de odoodevs
get_latest_odoo_version() {
    local latest_version
    if latest_version=$(curl -s "${ODOO_GITHUB_API}/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/'); then
        echo "$latest_version"
    else
        return 1
    fi
}

# Función para verificar si una versión de odoodevs existe
verify_odoo_version() {
    local version="$1"
    
    log_info "Verificando existencia de versión: $version"
    
    if [[ "$version" == "latest" ]]; then
        # Para latest, verificar que podemos obtener la última versión
        if get_latest_odoo_version > /dev/null 2>&1; then
            return 0
        else
            log_error "No se puede obtener la última versión"
            return 1
        fi
    fi
    
    if curl -s "${ODOO_GITHUB_API}/releases/tags/${version}" | grep -q '"tag_name"'; then
        log_info "Versión $version verificada"
        return 0
    else
        log_error "Versión $version no encontrada"
        return 1
    fi
}

# Función para descargar release de odoodevs
download_odoo_release() {
    local version="$1"
    local target_dir="$2"
    
    # Resolver versión si es "latest"
    if [[ "$version" == "latest" ]]; then
        log_info "Obteniendo última versión desde GitHub API..."
        version=$(get_latest_odoo_version)
        if [ $? -ne 0 ]; then
            log_error "No se pudo obtener la última versión de odoodevs"
            exit 1
        fi
        log_info "Última versión encontrada: $version"
    fi
    
    log_info "Descargando odoodevs $version..."
    
    # URL de descarga del release
    local download_url="${ODOO_RELEASE_URL}/${version}/odoodevs-${version}.tar.gz"
    local temp_file="/tmp/odoodevs-${version}.tar.gz"
    
    log_info "URL de descarga: $download_url"
    
    # Descargar archivo
    if curl -fsSL "$download_url" -o "$temp_file"; then
        log "Descarga completada"
    else
        log_error "Error descargando versión $version"
        log_error "URL: $download_url"
        exit 1
    fi
    
    # Verificar integridad del archivo
    if [[ ! -f "$temp_file" ]] || [[ ! -s "$temp_file" ]]; then
        log_error "Archivo descargado está vacío o corrupto"
        exit 1
    fi
    
    # Crear directorio de destino
    mkdir -p "$target_dir"
    
    # Extraer archivo
    log_info "Extrayendo archivo a $target_dir..."
    if tar -xzf "$temp_file" -C "$target_dir" --strip-components=1; then
        log "Extracción completada"
    else
        log_error "Error extrayendo archivo"
        exit 1
    fi
    
    # Limpiar archivo temporal
    rm -f "$temp_file"
    
    # Hacer ejecutables los scripts
    log_info "Configurando permisos de ejecución..."
    chmod +x "$target_dir"/*.sh 2>/dev/null || true
    chmod +x "$target_dir"/*.py 2>/dev/null || true
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
        log_info "Directorio: $(pwd)/$WORKSPACE"
        log_info "Para instalar odoodevs, ejecuta manualmente:"
        log_info "  cd $WORKSPACE && ./install.sh"
    else
        log_error "Error al clonar el repositorio"
        exit 1
    fi
}

# Función para instalar tipo latest
install_latest() {
    log "Instalando última versión de odoodevs..."
    
    # Verificar versión
    if ! verify_odoo_version "latest"; then
        exit 1
    fi
    
    # Descargar e instalar release
    download_odoo_release "latest" "$WORKSPACE"
    
    log "Instalación de última versión completada"
}

# Función para instalar versión específica
install_version() {
    if [ -z "$VERSION" ]; then
        log_error "Versión requerida para type=version"
        log "Usa: $0 --type version --version v1.0.0"
        exit 1
    fi
    
    log "Instalando versión específica: $VERSION"
    
    # Verificar versión
    if ! verify_odoo_version "$VERSION"; then
        exit 1
    fi
    
    # Descargar e instalar release
    download_odoo_release "$VERSION" "$WORKSPACE"
    
    log "Instalación de versión $VERSION completada"
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
WORKSPACE=""  # Se establecerá según el tipo
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

# Establecer workspace por defecto según el tipo
if [ -z "$WORKSPACE" ]; then
    if [ "$TYPE" = "devs" ]; then
        WORKSPACE="$DEFAULT_WORKSPACE_DEVS"
    else
        WORKSPACE="$DEFAULT_WORKSPACE_INSTALL"
    fi
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
