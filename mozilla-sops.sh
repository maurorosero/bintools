#!/bin/bash
#Script     	: mozilla-sops.sh
#Apps			: MRDEVS TOOLS
#Description	: Instalador multiplataforma de Mozilla SOPS
#Author			: Mauro Rosero Pérez
#Company Email	: mauro@rosero.one
#Personal Email	: mauro.rosero@gmail.com
#Created		: 2025/01/20 15:30:00
#Modified		: 2025/01/20 15:30:00
#Version		: 1.0.0
#Use Notes		:
#	- SOPS (Secrets OPerationS): Editor de archivos cifrados
#	- Soporte para múltiples sistemas operativos
#	- Instalación automática desde GitHub releases
#==============================================================================
# Derechos de Autor [2025] [Mauro Rosero P. <mauro@rosero.one>]
#==============================================================================
# Este programa es software libre: usted puede redistribuirlo y/o modificarlo
# bajo los términos de la Licencia Pública Affero General de GNU tal como
# lo publica la Free Software Foundation, ya sea la versión 3 de la licencia,
# o (a su elección) cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil,
# pero SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de
# COMERCIABILIDAD o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulte la
# Licencia Pública Affero General de GNU para obtener más detalles.
#
# Debería haber recibido una copia de la Licencia Pública Affero General
# junto con este programa. Si no la recibió, consulte <https://www.gnu.org/licenses/>.

# Configuración inicial
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"
SOPS_VERSION="latest"
INSTALL_DIR="/usr/local/bin"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes con colores
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para mostrar banner
show_banner() {
    clear
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    MOZILLA SOPS INSTALLER v$VERSION"
    echo "=================================================="
    echo -e "${NC}"
    echo "Instalador multiplataforma de Mozilla SOPS"
    echo "SOPS (Secrets OPerationS) - Editor de archivos cifrados"
    echo ""
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Instalador multiplataforma de Mozilla SOPS"
    echo ""
    echo "OPCIONES:"
    echo "  --install       Instalar SOPS en el sistema"
    echo "  --remove        Desinstalar SOPS del sistema"
    echo "  --check-updates Verificar si hay actualizaciones disponibles"
    echo "  --version       Mostrar versión del script"
    echo "  --help          Mostrar esta ayuda"
    echo ""
    echo "EJEMPLOS:"
    echo "  $0 --install       # Instalar SOPS"
    echo "  $0 --remove        # Desinstalar SOPS"
    echo "  $0 --check-updates # Verificar actualizaciones"
    echo "  $0 --help          # Mostrar ayuda"
    echo ""
    echo "SISTEMAS SOPORTADOS:"
    echo "  - Linux (Ubuntu, Debian, Fedora, CentOS, Arch Linux)"
    echo "  - macOS (Intel y Apple Silicon)"
    echo "  - Windows (Git Bash, WSL)"
    echo ""
}

# Función para detectar el sistema operativo (compatible con packages.sh)
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        case "$ID" in
            ubuntu)
                OS="ubuntu"
                ;;
            debian)
                OS="debian"
                ;;
            fedora)
                OS="fedora"
                ;;
            centos|rhel)
                OS="centos"
                ;;
            arch|manjaro)
                OS="arch"
                ;;
            *)
                log_warning "Distribución Linux no reconocida: $ID, usando detección genérica"
                OS="linux"
                ;;
        esac
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        log_warning "Sistema operativo no reconocido: $OSTYPE"
        OS="unknown"
    fi
    
    log_info "Sistema operativo detectado: $OS"
}

# Función para detectar la arquitectura
detect_arch() {
    case "$(uname -m)" in
        x86_64)
            ARCH="amd64"
            ;;
        arm64|aarch64)
            ARCH="arm64"
            ;;
        armv7l)
            ARCH="arm"
            ;;
        *)
            ARCH="amd64"
            log_warning "Arquitectura no reconocida, usando amd64 por defecto"
            ;;
    esac
    
    log_info "Arquitectura detectada: $ARCH"
}

# Función para verificar requisitos previos
check_prerequisites() {
    log_info "Verificando requisitos previos..."
    
    local missing_deps=()
    
    # Verificar herramientas de descarga
    if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
        missing_deps+=("curl o wget")
    fi
    
    # Verificar herramientas de compresión
    if ! command -v tar >/dev/null 2>&1 && ! command -v unzip >/dev/null 2>&1; then
        missing_deps+=("tar o unzip")
    fi
    
    # Verificar sudo en sistemas Unix (excepto si es root o Windows)
    if [[ "$OS" != "windows" ]] && [[ "$OS" != "unknown" ]]; then
        if [ "$EUID" -ne 0 ] && ! command -v sudo >/dev/null 2>&1; then
            missing_deps+=("sudo")
        fi
    fi
    
    # Mostrar dependencias faltantes
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Faltan las siguientes dependencias:"
        for dep in "${missing_deps[@]}"; do
            log_error "  - $dep"
        done
        echo ""
        log_info "Instala las dependencias faltantes y vuelve a ejecutar el script."
        log_info "En Ubuntu/Debian: sudo apt install curl wget tar"
        log_info "En Fedora/CentOS: sudo dnf install curl wget tar"
        log_info "En Arch Linux: sudo pacman -S curl wget tar"
        log_info "En macOS: brew install curl wget gnu-tar"
        return 1
    fi
    
    log_success "Todos los requisitos previos están disponibles"
    return 0
}

# Función para verificar si SOPS está instalado
check_sops_installed() {
    if command -v sops >/dev/null 2>&1; then
        local installed_version=$(sops --version 2>/dev/null | head -n1 | cut -d' ' -f2)
        log_success "SOPS ya está instalado (versión: $installed_version)"
        return 0
    else
        log_info "SOPS no está instalado"
        return 1
    fi
}

# Función para obtener solo la versión instalada (sin logs)
get_installed_version() {
    if command -v sops >/dev/null 2>&1; then
        # Usar --check-for-updates para evitar el warning de deprecación
        # y obtener solo la versión sin verificaciones adicionales
        sops --version --check-for-updates 2>/dev/null | head -n1 | cut -d' ' -f2
    else
        echo ""
    fi
}

# Función para comparar versiones (formato semver)
compare_versions() {
    local version1=$1
    local version2=$2
    
    # Verificar que ambas versiones no estén vacías
    if [ -z "$version1" ] || [ -z "$version2" ]; then
        echo "error"
        return 1
    fi
    
    # Remover 'v' prefix si existe y limpiar espacios
    version1=$(echo "${version1#v}" | tr -d ' ')
    version2=$(echo "${version2#v}" | tr -d ' ')
    
    # Convertir a números para comparación
    local v1_parts=($(echo $version1 | tr '.' ' '))
    local v2_parts=($(echo $version2 | tr '.' ' '))
    
    # Comparar cada parte de la versión
    for i in {0..2}; do
        local v1_part=${v1_parts[$i]:-0}
        local v2_part=${v2_parts[$i]:-0}
        
        # Verificar que sean números válidos
        if ! [[ "$v1_part" =~ ^[0-9]+$ ]] || ! [[ "$v2_part" =~ ^[0-9]+$ ]]; then
            echo "error"
            return 1
        fi
        
        if [ "$v1_part" -gt "$v2_part" ]; then
            echo "newer"
            return 0
        elif [ "$v1_part" -lt "$v2_part" ]; then
            echo "older"
            return 0
        fi
    done
    
    echo "same"
    return 0
}

# Función para obtener la última versión de SOPS
get_latest_version() {
    log_info "Obteniendo última versión de SOPS..."
    
    local version_obtained=false
    
    # Intentar con curl primero
    if command -v curl >/dev/null 2>&1; then
        log_info "Intentando obtener versión con curl..."
        SOPS_VERSION=$(curl -s --connect-timeout 10 --max-time 30 \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/mozilla/sops/releases/latest | \
            grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | sed 's/v//')
        
        if [ -n "$SOPS_VERSION" ] && [ "$SOPS_VERSION" != "null" ]; then
            version_obtained=true
        fi
    fi
    
    # Si curl falló, intentar con wget
    if [ "$version_obtained" = false ] && command -v wget >/dev/null 2>&1; then
        log_info "Intentando obtener versión con wget..."
        SOPS_VERSION=$(wget -qO- --timeout=30 --tries=3 \
            --header="Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/mozilla/sops/releases/latest | \
            grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | sed 's/v//')
        
        if [ -n "$SOPS_VERSION" ] && [ "$SOPS_VERSION" != "null" ]; then
            version_obtained=true
        fi
    fi
    
    # Si ambos fallaron, usar versión por defecto
    if [ "$version_obtained" = false ]; then
        log_warning "No se pudo obtener la última versión desde GitHub"
        log_info "Posibles causas: problemas de conectividad, rate limiting, o cambios en la API"
        SOPS_VERSION="3.10.2"  # Versión por defecto
        log_warning "Usando versión por defecto: $SOPS_VERSION"
    fi
    
    log_info "Última versión disponible: $SOPS_VERSION"
}

# Función para verificar actualizaciones disponibles
check_for_updates() {
    local installed_version=$1
    
    log_info "Verificando actualizaciones disponibles..."
    get_latest_version
    
    # Verificar que tenemos versiones válidas
    if [ -z "$installed_version" ] || [ -z "$SOPS_VERSION" ]; then
        log_error "No se pudo obtener las versiones para comparar"
        return 1
    fi
    
    log_info "Comparando versiones: instalada=$installed_version, disponible=$SOPS_VERSION"
    
    local comparison=$(compare_versions "$installed_version" "$SOPS_VERSION")
    
    case "$comparison" in
        "same")
            log_success "SOPS ya está en la última versión ($installed_version)"
            return 1  # No hay actualizaciones
            ;;
        "newer")
            log_warning "Versión instalada ($installed_version) es más nueva que la disponible ($SOPS_VERSION)"
            log_info "Esto puede indicar una versión de desarrollo o un error en la detección"
            return 1  # No hay actualizaciones
            ;;
        "older")
            log_warning "Versión instalada ($installed_version) es más antigua que la disponible ($SOPS_VERSION)"
            echo ""
            log_info "¡Actualización disponible!"
            echo "  Versión actual: $installed_version"
            echo "  Última versión: $SOPS_VERSION"
            echo ""
            return 0  # Hay actualizaciones disponibles
            ;;
        "error")
            log_error "Error al comparar versiones: instalada='$installed_version', disponible='$SOPS_VERSION'"
            return 1
            ;;
        *)
            log_error "Resultado inesperado de comparación de versiones: '$comparison'"
            return 1
            ;;
    esac
}

# Función para solicitar actualización
prompt_for_update() {
    echo ""
    read -p "¿Deseas actualizar SOPS a la versión $SOPS_VERSION? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Iniciando actualización de SOPS..."
        return 0
    else
        log_info "Actualización cancelada"
        return 1
    fi
}

# Función para instalar SOPS en Ubuntu/Debian
install_ubuntu() {
    log_info "Instalando SOPS en Ubuntu/Debian..."
    
    # Intentar instalar desde repositorios oficiales primero
    if command -v apt >/dev/null 2>&1; then
        log_info "Intentando instalar desde repositorios oficiales..."
        sudo apt update && sudo apt install -y sops
        if [ $? -eq 0 ]; then
            log_success "SOPS instalado exitosamente desde repositorios oficiales"
            return 0
        else
            log_warning "Instalación desde repositorios falló, probando otros métodos..."
        fi
    fi
    
    # Verificar si snap está disponible
    if command -v snap >/dev/null 2>&1; then
        log_info "Intentando instalar SOPS via Snap..."
        sudo snap install sops
        if [ $? -eq 0 ]; then
            log_success "SOPS instalado exitosamente via Snap"
            return 0
        else
            log_warning "Instalación via Snap falló"
        fi
    fi
    
    # Instalar via descarga directa como último recurso
    log_info "Instalando via descarga directa..."
    install_direct_download
}

# Función para instalar SOPS en Fedora
install_fedora() {
    log_info "Instalando SOPS en Fedora..."
    
    # Intentar instalar desde repositorios
    if command -v dnf >/dev/null 2>&1; then
        log_info "Intentando instalar desde repositorios oficiales..."
        sudo dnf install -y sops
        if [ $? -eq 0 ]; then
            log_success "SOPS instalado exitosamente desde repositorios"
            return 0
        fi
    fi
    
    # Instalar via descarga directa
    install_direct_download
}

# Función para instalar SOPS en CentOS
install_centos() {
    log_info "Instalando SOPS en CentOS..."
    
    # Intentar instalar desde repositorios
    if command -v yum >/dev/null 2>&1; then
        log_info "Intentando instalar desde repositorios oficiales..."
        sudo yum install -y sops
        if [ $? -eq 0 ]; then
            log_success "SOPS instalado exitosamente desde repositorios"
            return 0
        fi
    fi
    
    # Instalar via descarga directa
    install_direct_download
}

# Función para instalar SOPS en Arch Linux
install_arch() {
    log_info "Instalando SOPS en Arch Linux..."
    
    # Intentar instalar desde AUR
    if command -v yay >/dev/null 2>&1; then
        log_info "Instalando SOPS via yay (AUR)..."
        yay -S sops-bin
        if [ $? -eq 0 ]; then
            log_success "SOPS instalado exitosamente via yay"
            return 0
        fi
    elif command -v pacman >/dev/null 2>&1; then
        log_info "Intentando instalar desde repositorios oficiales..."
        sudo pacman -S sops
        if [ $? -eq 0 ]; then
            log_success "SOPS instalado exitosamente desde repositorios"
            return 0
        fi
    fi
    
    # Instalar via descarga directa
    install_direct_download
}

# Función para instalar SOPS en macOS
install_macos() {
    log_info "Instalando SOPS en macOS..."
    
    # Intentar instalar via Homebrew
    if command -v brew >/dev/null 2>&1; then
        log_info "Instalando SOPS via Homebrew..."
        brew install sops
        if [ $? -eq 0 ]; then
            log_success "SOPS instalado exitosamente via Homebrew"
            return 0
        fi
    fi
    
    # Instalar via descarga directa
    install_direct_download
}

# Función para instalar SOPS en Windows
install_windows() {
    log_info "Instalando SOPS en Windows..."
    
    # Intentar instalar via Chocolatey
    if command -v choco >/dev/null 2>&1; then
        log_info "Instalando SOPS via Chocolatey..."
        choco install sops
        if [ $? -eq 0 ]; then
            log_success "SOPS instalado exitosamente via Chocolatey"
            return 0
        fi
    fi
    
    # Instalar via descarga directa
    install_direct_download
}

# Función para instalar SOPS via descarga directa
install_direct_download() {
    log_info "Instalando SOPS via descarga directa..."
    
    get_latest_version
    
    # Crear directorio temporal
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    # URL de descarga basada en OS y arquitectura
    local download_url=""
    
    case "$OS" in
        "ubuntu"|"debian"|"fedora"|"centos"|"arch"|"linux")
            download_url="https://github.com/mozilla/sops/releases/download/v${SOPS_VERSION}/sops-v${SOPS_VERSION}.linux.${ARCH}"
            ;;
        "macos")
            if [[ "$ARCH" == "arm64" ]]; then
                download_url="https://github.com/mozilla/sops/releases/download/v${SOPS_VERSION}/sops-v${SOPS_VERSION}.darwin.arm64"
            else
                download_url="https://github.com/mozilla/sops/releases/download/v${SOPS_VERSION}/sops-v${SOPS_VERSION}.darwin"
            fi
            ;;
        "windows")
            download_url="https://github.com/mozilla/sops/releases/download/v${SOPS_VERSION}/sops-v${SOPS_VERSION}.exe"
            ;;
        *)
            log_error "Sistema operativo no soportado para descarga directa: $OS"
            rm -rf "$temp_dir"
            return 1
            ;;
    esac
    
    log_info "Descargando SOPS desde: $download_url"
    
    # Descargar SOPS con manejo de errores
    local download_success=false
    
    if command -v curl >/dev/null 2>&1; then
        if curl -L -o sops "$download_url" --fail --silent --show-error; then
            download_success=true
        else
            log_warning "Descarga con curl falló, probando con wget..."
        fi
    fi
    
    if [ "$download_success" = false ] && command -v wget >/dev/null 2>&1; then
        if wget -O sops "$download_url" --quiet --show-progress; then
            download_success=true
        else
            log_error "Descarga con wget también falló"
        fi
    fi
    
    if [ "$download_success" = false ]; then
        log_error "No se pudo descargar SOPS. Verifica tu conexión a internet."
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Verificar que el archivo se descargó correctamente
    if [ ! -f sops ] || [ ! -s sops ]; then
        log_error "El archivo descargado está vacío o no existe"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Hacer ejecutable (excepto en Windows)
    if [[ "$OS" != "windows" ]]; then
        chmod +x sops
        
        # Verificar que es ejecutable
        if ! ./sops --version >/dev/null 2>&1; then
            log_error "El binario descargado no es ejecutable o está corrupto"
            rm -rf "$temp_dir"
            return 1
        fi
    fi
    
    # Instalar en el sistema
    case "$OS" in
        "windows")
            # En Windows, copiar a un directorio en el PATH
            local windows_bin_dir="$HOME/bin"
            mkdir -p "$windows_bin_dir"
            cp sops "$windows_bin_dir/"
            log_success "SOPS instalado en $windows_bin_dir"
            log_info "Asegúrate de que $windows_bin_dir esté en tu PATH"
            ;;
        *)
            # En Unix-like systems
            if [ -w "$INSTALL_DIR" ]; then
                cp sops "$INSTALL_DIR/"
            else
                sudo cp sops "$INSTALL_DIR/"
            fi
            log_success "SOPS instalado en $INSTALL_DIR"
            ;;
    esac
    
    # Limpiar directorio temporal
    cd - >/dev/null
    rm -rf "$temp_dir"
}

# Función para desinstalar SOPS
uninstall_sops() {
    log_info "Desinstalando SOPS..."
    
    # Verificar si está instalado
    if ! check_sops_installed; then
        log_warning "SOPS no está instalado"
        return 0
    fi
    
    case "$OS" in
        "ubuntu")
            if command -v snap >/dev/null 2>&1; then
                sudo snap remove sops
            fi
            sudo rm -f "$INSTALL_DIR/sops"
            ;;
        "fedora"|"centos")
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf remove -y sops
            elif command -v yum >/dev/null 2>&1; then
                sudo yum remove -y sops
            fi
            sudo rm -f "$INSTALL_DIR/sops"
            ;;
        "arch")
            if command -v yay >/dev/null 2>&1; then
                yay -R sops-bin
            elif command -v pacman >/dev/null 2>&1; then
                sudo pacman -R sops
            fi
            sudo rm -f "$INSTALL_DIR/sops"
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                brew uninstall sops
            fi
            sudo rm -f "$INSTALL_DIR/sops"
            ;;
        "windows")
            if command -v choco >/dev/null 2>&1; then
                choco uninstall sops
            fi
            rm -f "$HOME/bin/sops"
            ;;
        *)
            sudo rm -f "$INSTALL_DIR/sops"
            ;;
    esac
    
    log_success "SOPS desinstalado exitosamente"
}

# Función para verificar la instalación
verify_installation() {
    log_info "Verificando instalación de SOPS..."
    
    if command -v sops >/dev/null 2>&1; then
        local version=$(sops --version 2>/dev/null | head -n1 | cut -d' ' -f2)
        log_success "SOPS instalado correctamente (versión: $version)"
        
        # Mostrar información adicional
        echo ""
        log_info "Información de SOPS:"
        sops --version
        echo ""
        log_info "Ejemplos de uso:"
        echo "  sops --help                    # Mostrar ayuda"
        echo "  sops --version                 # Mostrar versión"
        echo "  sops file.yaml                 # Editar archivo cifrado"
        echo "  sops -d file.yaml              # Descifrar archivo"
        echo "  sops -e file.yaml              # Cifrar archivo"
        return 0
    else
        log_error "Error: SOPS no se pudo instalar o no está en el PATH"
        return 1
    fi
}

# Función principal de instalación
install_sops() {
    log_info "Iniciando instalación de SOPS..."
    
    # Verificar si ya está instalado
    if check_sops_installed; then
        # SOPS está instalado, obtener versión y verificar actualizaciones
        local installed_version=$(get_installed_version)
        if check_for_updates "$installed_version"; then
            # Hay actualizaciones disponibles
            if prompt_for_update; then
                log_info "Procediendo con la actualización..."
            else
                log_info "Operación cancelada"
                return 0
            fi
        else
            # No hay actualizaciones, preguntar si quiere reinstalar
            echo ""
            read -p "SOPS ya está instalado y actualizado. ¿Deseas reinstalarlo? (y/N): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Instalación cancelada"
                return 0
            fi
        fi
    fi
    
    # Detectar sistema operativo y arquitectura
    detect_os
    detect_arch
    
    # Verificar requisitos previos
    if ! check_prerequisites; then
        return 1
    fi
    
    # Instalar según el sistema operativo
    case "$OS" in
        "ubuntu"|"debian")
            install_ubuntu
            ;;
        "fedora")
            install_fedora
            ;;
        "centos")
            install_centos
            ;;
        "arch")
            install_arch
            ;;
        "macos")
            install_macos
            ;;
        "windows")
            install_windows
            ;;
        "linux"|"unknown")
            log_warning "Sistema operativo no reconocido, intentando instalación genérica..."
            install_direct_download
            ;;
        *)
            log_error "Sistema operativo no soportado: $OS"
            return 1
            ;;
    esac
    
    # Verificar instalación
    verify_installation
}

# Función para verificar actualizaciones
check_updates() {
    log_info "Verificando estado de SOPS..."
    
    # Verificar si está instalado
    if check_sops_installed; then
        # SOPS está instalado, obtener versión y verificar actualizaciones
        local installed_version=$(get_installed_version)
        if check_for_updates "$installed_version"; then
            # Hay actualizaciones disponibles
            echo ""
            read -p "¿Deseas actualizar ahora? (y/N): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                log_info "Iniciando actualización..."
                detect_os
                detect_arch
                
                # Instalar según el sistema operativo
                case "$OS" in
                    "ubuntu"|"debian")
                        install_ubuntu
                        ;;
                    "fedora")
                        install_fedora
                        ;;
                    "centos")
                        install_centos
                        ;;
                    "arch")
                        install_arch
                        ;;
                    "macos")
                        install_macos
                        ;;
                    "windows")
                        install_windows
                        ;;
                    "linux"|"unknown")
                        log_warning "Sistema operativo no reconocido, intentando instalación genérica..."
                        install_direct_download
                        ;;
                    *)
                        log_error "Sistema operativo no soportado: $OS"
                        return 1
                        ;;
                esac
                
                # Verificar instalación
                verify_installation
            else
                log_info "Actualización cancelada"
            fi
        fi
    else
        log_info "SOPS no está instalado. Usa --install para instalarlo."
    fi
}

# Función principal
main() {
    show_banner
    
    # Verificar argumentos
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    case "$1" in
        "--install")
            install_sops
            ;;
        "--remove")
            detect_os
            uninstall_sops
            ;;
        "--check-updates")
            check_updates
            ;;
        "--version")
            echo "Mozilla SOPS Installer v$VERSION"
            ;;
        "--help"|"-h")
            show_help
            ;;
        *)
            log_error "Opción no válida: $1"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
