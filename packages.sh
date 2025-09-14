#!/bin/bash

# Script de instalación de paquetes multiplataforma
# Compatible con Ubuntu, Debian, Fedora, CentOS, Arch Linux y macOS
# Autor: Mauro Rosero Pérez
# Website: https://mauro.rosero.one
# Versión: 1.1.0

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
HEADLESS=false
GUI_DETECTED=false
NO_SUDO=false
SUDO_MAINTAINED=false

# Función para mostrar listas disponibles dinámicamente
show_available_lists() {
    for pkg_file in "$CONFIG_DIR"/*.pkg; do
        if [[ -f "$pkg_file" ]]; then
            local pkg_name=$(basename "$pkg_file" .pkg)
            local description=""
            
            # Intentar obtener descripción del primer comentario del archivo
            local first_comment=$(grep -m 1 "^#.*[a-zA-Z]" "$pkg_file" 2>/dev/null | sed 's/^#\s*//')
            if [[ -n "$first_comment" ]]; then
                description="$first_comment"
            else
                description="Paquetes de $pkg_name"
            fi
            
            printf "    %-8s %s\n" "$pkg_name" "$description"
        fi
    done
    echo "    all      Todas las listas disponibles"
}

# Función para mostrar ayuda
show_help() {
    # Generar lista de archivos disponibles dinámicamente
    local available_lists=""
    for pkg_file in "$CONFIG_DIR"/*.pkg; do
        if [[ -f "$pkg_file" ]]; then
            local pkg_name=$(basename "$pkg_file" .pkg)
            available_lists="$available_lists$pkg_name, "
        fi
    done
    available_lists="${available_lists%, }, all"  # Remover última coma y agregar 'all'
    
    cat << EOF
Uso: $0 [OPCIONES]

Script de instalación de paquetes multiplataforma

OPCIONES:
    -l, --list LISTA     Lista de paquetes a instalar ($available_lists)
    -d, --dry-run        Solo mostrar qué se instalaría, sin instalar realmente
    -v, --verbose        Mostrar información detallada
    --headless           Instalar paquetes GUI incluso sin ambiente gráfico
    --no-sudo            Ejecutar sin privilegios sudo (para usuarios root)
    --install-yay        Instalar yay (AUR helper) en Arch Linux
    --install-snap       Instalar snapd en sistemas compatibles
    -h, --help           Mostrar esta ayuda

EJEMPLOS:
    $0 --list base                    # Instalar paquetes base
    $0 --list base,devs              # Instalar múltiples listas
    $0 --list vbox                   # Instalar VirtualBox y Vagrant
    $0 --list all --dry-run          # Ver qué se instalaría
    $0 --list user --verbose         # Instalar con información detallada
    $0 --list orgs --headless        # Instalar paquetes GUI sin ambiente gráfico
    $0 --list all --headless         # Instalar todo incluyendo GUI
    $0 --list base --no-sudo         # Instalar sin sudo (usuario root)
    $0 --install-yay                 # Instalar yay en Arch Linux
    $0 --install-snap                # Instalar snapd en sistemas compatibles

LISTAS DISPONIBLES:
$(show_available_lists)

FORMATO DE ARCHIVOS:
    Los archivos de configuración están en configs/ con formato:
    OS:Manejador:Paquete:Descripción

DETECCIÓN AUTOMÁTICA DE GUI:
    El script detecta automáticamente si hay ambiente gráfico disponible:
    - Variables de entorno: DISPLAY, WAYLAND_DISPLAY, XDG_SESSION_TYPE
    - Servidor X corriendo: xset
    - Procesos gráficos: Xorg, Xwayland, gnome-session, kde, etc.
    - macOS: TERM_PROGRAM
    
    Sin ambiente gráfico, los paquetes GUI se omiten automáticamente.
    Use --headless para instalar paquetes GUI sin ambiente gráfico.

GESTIÓN DE PRIVILEGIOS SUDO:
    El script solicita privilegios sudo una sola vez al inicio y los mantiene
    durante todo el proceso de instalación:
    - Solicita sudo al inicio con sudo -v
    - Mantiene la sesión activa en background
    - Evita múltiples solicitudes de contraseña
    - Use --no-sudo para ejecutar sin privilegios (usuario root)

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

# Función para mantener sesión sudo
maintain_sudo() {
    if [[ "$NO_SUDO" == "true" ]]; then
        return 0
    fi
    
    # Verificar si ya tenemos privilegios sudo
    if sudo -n true 2>/dev/null; then
        log "VERBOSE" "Privilegios sudo ya disponibles"
        SUDO_MAINTAINED=true
        return 0
    fi
    
    # Solicitar privilegios sudo una sola vez
    log "INFO" "Solicitando privilegios sudo para todo el proceso..."
    if sudo -v; then
        log "SUCCESS" "Privilegios sudo obtenidos"
        SUDO_MAINTAINED=true
        
        # Mantener la sesión sudo activa en background
        (
            while true; do
                sleep 60
                sudo -n true 2>/dev/null || break
            done
        ) &
        
        return 0
    else
        log "ERROR" "No se pudieron obtener privilegios sudo"
        return 1
    fi
}

# Función para ejecutar comandos con sudo mantenido
sudo_cmd() {
    if [[ "$NO_SUDO" == "true" ]]; then
        "$@"
    elif [[ "$SUDO_MAINTAINED" == "true" ]]; then
        sudo "$@"
    else
        log "ERROR" "Sesión sudo no mantenida. Ejecutando: $*"
        sudo "$@"
    fi
}

# Función para detectar ambiente gráfico
detect_gui() {
    # Verificar variables de entorno comunes
    if [[ -n "${DISPLAY:-}" ]] || [[ -n "${WAYLAND_DISPLAY:-}" ]] || [[ -n "${XDG_SESSION_TYPE:-}" ]]; then
        return 0  # GUI detectado
    fi
    
    # Verificar si hay servidor X corriendo
    if command -v xset >/dev/null 2>&1 && xset q >/dev/null 2>&1; then
        return 0  # GUI detectado
    fi
    
    # Verificar si estamos en macOS con GUI
    if [[ "$OSTYPE" == "darwin"* ]] && [[ -n "${TERM_PROGRAM:-}" ]]; then
        return 0  # GUI detectado en macOS
    fi
    
    # Verificar si hay procesos gráficos corriendo
    if pgrep -x "Xorg\|Xwayland\|gnome-session\|kde\|xfce\|mate\|lxde\|i3\|sway" >/dev/null 2>&1; then
        return 0  # GUI detectado
    fi
    
    return 1  # No GUI detectado
}

# Función para identificar si un paquete es GUI
is_gui_package() {
    local package="$1"
    local description="$2"
    
    # Lista de paquetes GUI conocidos
    local gui_packages=(
        "firefox" "chromium" "chrome" "brave" "vivaldi" "opera"
        "libreoffice" "libreoffice-writer" "libreoffice-calc" "libreoffice-impress"
        "gimp" "inkscape" "blender" "krita" "darktable"
        "vlc" "mpv" "totem" "parole"
        "thunderbird" "evolution" "geary"
        "filezilla" "remmina" "vinagre"
        "simple-scan" "xsane"
        "drawio" "draw.io"
        "projectlibre" "project-libre"
        "whatsapp-for-linux" "whatsapp"
        "discord" "slack" "telegram"
        "wireshark" "wireshark-qt" "wireshark-gtk"
        "k9s" "k9s-gui"
        "docker-desktop" "docker-desktop-data"
        "virtualbox" "vmware" "qemu-system"
        "steam" "lutris" "heroic"
        "notion" "obsidian" "joplin"
        "calibre" "calibre-gui"
        "audacity" "ardour" "lmms"
        "code" "vscode" "atom" "sublime-text"
        "android-studio" "intellij-idea" "pycharm"
        "eclipse" "netbeans"
        "mysql-workbench" "pgadmin" "dbeaver"
        "postman" "insomnia"
        "figma" "sketch"
        "zoom" "teams" "webex"
        "spotify" "spotify-client"
        "spotify" "spotify-client"
    )
    
    # Verificar si el paquete está en la lista
    for gui_pkg in "${gui_packages[@]}"; do
        if [[ "$package" == *"$gui_pkg"* ]] || [[ "$gui_pkg" == *"$package"* ]]; then
            return 0  # Es paquete GUI
        fi
    done
    
    # Verificar por palabras clave en la descripción
    local gui_keywords=("GUI" "interfaz gráfica" "escritorio" "ventana" "aplicación" "cliente" "editor" "visor" "reproductor" "navegador" "oficina" "diseño" "imagen" "video" "audio" "juego" "chat" "mensajería" "correo" "escritorio" "terminal" "IDE" "editor" "desarrollo" "diseño" "multimedia")
    
    for keyword in "${gui_keywords[@]}"; do
        if [[ "$description" == *"$keyword"* ]]; then
            return 0  # Es paquete GUI
        fi
    done
    
    return 1  # No es paquete GUI
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

# Función para instalar yay en Arch Linux
install_yay() {
    local os=$(detect_os)
    
    if [[ "$os" != "arch" ]]; then
        log "ERROR" "yay solo está disponible en Arch Linux"
        return 1
    fi
    
    if command -v yay >/dev/null 2>&1; then
        log "INFO" "yay ya está instalado"
        return 0
    fi
    
    log "INFO" "Instalando yay (AUR helper)..."
    
    # Instalar dependencias necesarias
    if ! sudo_cmd pacman -S --noconfirm base-devel git; then
        log "ERROR" "No se pudieron instalar las dependencias necesarias"
        return 1
    fi
    
    # Clonar y compilar yay
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    if git clone https://aur.archlinux.org/yay.git; then
        cd yay
        if makepkg -si --noconfirm; then
            log "SUCCESS" "yay instalado correctamente"
            cd /
            rm -rf "$temp_dir"
            return 0
        else
            log "ERROR" "Falló la compilación de yay"
            cd /
            rm -rf "$temp_dir"
            return 1
        fi
    else
        log "ERROR" "No se pudo clonar el repositorio de yay"
        cd /
        rm -rf "$temp_dir"
        return 1
    fi
}

# Función para instalar snapd
install_snap() {
    local os=$(detect_os)
    
    if check_snap; then
        log "INFO" "snap ya está instalado"
        return 0
    fi
    
    log "INFO" "Instalando snapd..."
    
    case "$os" in
        ubuntu|debian)
            if sudo_cmd apt update && sudo_cmd apt install -y snapd; then
                log "SUCCESS" "snapd instalado correctamente"
                log "INFO" "Reinicia tu sesión para usar snap"
                return 0
            else
                log "ERROR" "Falló la instalación de snapd"
                return 1
            fi
            ;;
        fedora)
            if sudo_cmd dnf install -y snapd; then
                log "SUCCESS" "snapd instalado correctamente"
                log "INFO" "Habilita el socket de snap: sudo systemctl enable --now snapd.socket"
                return 0
            else
                log "ERROR" "Falló la instalación de snapd"
                return 1
            fi
            ;;
        arch)
            if sudo_cmd pacman -S --noconfirm snapd; then
                log "SUCCESS" "snapd instalado correctamente"
                log "INFO" "Habilita el socket de snap: sudo systemctl enable --now snapd.socket"
                return 0
            else
                log "ERROR" "Falló la instalación de snapd"
                return 1
            fi
            ;;
        *)
            log "ERROR" "snapd no está disponible para $os"
            return 1
            ;;
    esac
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
            if ! sudo_cmd apt update >/dev/null 2>&1; then
                log "WARNING" "No se pudo actualizar la lista de paquetes"
            fi
            # Verificar si el paquete ya está instalado
            if dpkg -l "$package" >/dev/null 2>&1; then
                # Verificar si hay actualizaciones disponibles
                if apt list --upgradable 2>/dev/null | grep -q "^$package/"; then
                    log "INFO" "Actualizando $package (hay actualizaciones disponibles)"
                    if sudo_cmd apt install -y "$package"; then
                        log "SUCCESS" "Actualizado: $package"
                        return 0
                    fi
                else
                    log "INFO" "Paquete $package ya está actualizado"
                    return 0
                fi
            else
                log "INFO" "Instalando $package (no está instalado)"
                if sudo_cmd apt install -y "$package"; then
                    log "SUCCESS" "Instalado: $package"
                    return 0
                fi
            fi
            ;;
        dnf)
            # Verificar si el paquete ya está instalado
            if rpm -q "$package" >/dev/null 2>&1; then
                # Verificar si hay actualizaciones disponibles
                if dnf check-update "$package" >/dev/null 2>&1; then
                    log "INFO" "Actualizando $package (hay actualizaciones disponibles)"
                    if sudo_cmd dnf update -y "$package"; then
                        log "SUCCESS" "Actualizado: $package"
                        return 0
                    fi
                else
                    log "INFO" "Paquete $package ya está actualizado"
                    return 0
                fi
            else
                log "INFO" "Instalando $package (no está instalado)"
                if sudo_cmd dnf install -y "$package"; then
                    log "SUCCESS" "Instalado: $package"
                    return 0
                fi
            fi
            ;;
        yum)
            if sudo_cmd yum install -y "$package"; then
                log "SUCCESS" "Instalado: $package"
                return 0
            fi
            ;;
        pacman)
            # Verificar si el paquete ya está instalado
            if pacman -Q "$package" >/dev/null 2>&1; then
                # Verificar si hay actualizaciones disponibles
                if pacman -Qu "$package" >/dev/null 2>&1; then
                    log "INFO" "Actualizando $package (hay actualizaciones disponibles)"
                    if sudo_cmd pacman -S --noconfirm "$package"; then
                        log "SUCCESS" "Actualizado: $package"
                        return 0
                    fi
                else
                    log "INFO" "Paquete $package ya está actualizado"
                    return 0
                fi
            else
                log "INFO" "Instalando $package (no está instalado)"
                if sudo_cmd pacman -S --noconfirm "$package"; then
                    log "SUCCESS" "Instalado: $package"
                    return 0
                fi
            fi
            ;;
        yay)
            if command -v yay >/dev/null 2>&1; then
                # Verificar si el paquete ya está instalado
                if yay -Q "$package" >/dev/null 2>&1; then
                    # Verificar si hay actualizaciones disponibles
                    if yay -Qu "$package" >/dev/null 2>&1; then
                        log "INFO" "Actualizando $package (hay actualizaciones disponibles)"
                        if yay -S --noconfirm "$package"; then
                            log "SUCCESS" "Actualizado: $package"
                            return 0
                        fi
                    else
                        log "INFO" "Paquete $package ya está actualizado"
                        return 0
                    fi
                else
                    log "INFO" "Instalando $package (no está instalado)"
                    if yay -S --noconfirm "$package"; then
                        log "SUCCESS" "Instalado: $package"
                        return 0
                    fi
                fi
            else
                log "WARNING" "yay no está instalado, intentando con pacman para: $package"
                # Verificar si el paquete ya está instalado con pacman
                if pacman -Q "$package" >/dev/null 2>&1; then
                    # Verificar si hay actualizaciones disponibles
                    if pacman -Qu "$package" >/dev/null 2>&1; then
                        log "INFO" "Actualizando $package (hay actualizaciones disponibles)"
                        if sudo_cmd pacman -S --noconfirm "$package"; then
                            log "SUCCESS" "Actualizado: $package (con pacman)"
                            return 0
                        fi
                    else
                        log "INFO" "Paquete $package ya está actualizado"
                        return 0
                    fi
                else
                    log "INFO" "Instalando $package (no está instalado)"
                    if sudo_cmd pacman -S --noconfirm "$package"; then
                        log "SUCCESS" "Instalado: $package (con pacman)"
                        return 0
                    fi
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
            if sudo_cmd snap install "$package"; then
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
            
            # Verificar si es paquete GUI y si debemos filtrarlo
            if is_gui_package "$package" "$description"; then
                if [[ "$HEADLESS" == "true" ]]; then
                    log "VERBOSE" "Instalando paquete GUI (modo headless): $package ($manager)"
                elif [[ "$GUI_DETECTED" == "false" ]]; then
                    log "VERBOSE" "Saltando paquete GUI (sin ambiente gráfico): $package ($manager)"
                    continue
                else
                    log "VERBOSE" "Procesando paquete GUI: $package ($manager)"
                fi
            else
                log "VERBOSE" "Procesando: $package ($manager)"
            fi
            
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
            --headless)
                HEADLESS=true
                shift
                ;;
            --no-sudo)
                NO_SUDO=true
                shift
                ;;
            --install-yay)
                install_yay
                exit $?
                ;;
            --install-snap)
                install_snap
                exit $?
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
        log "ERROR" "Debe especificar una lista con --list o usar --install-yay/--install-snap"
        show_help
        exit 1
    fi
    
    # Detectar OS
    local os=$(detect_os)
    log "INFO" "OS detectado: $os"
    
    # Mantener sesión sudo si es necesario
    if [[ "$NO_SUDO" == "false" ]]; then
        if ! maintain_sudo; then
            log "ERROR" "No se pudo mantener la sesión sudo"
            exit 1
        fi
    else
        log "INFO" "Modo sin sudo activado"
    fi
    
    # Detectar ambiente gráfico
    if detect_gui; then
        GUI_DETECTED=true
        log "INFO" "Ambiente gráfico detectado"
    else
        GUI_DETECTED=false
        log "INFO" "Sin ambiente gráfico detectado (modo headless)"
    fi
    
    # Mostrar información sobre filtrado de paquetes GUI
    if [[ "$GUI_DETECTED" == "false" ]] && [[ "$HEADLESS" == "false" ]]; then
        log "INFO" "Los paquetes GUI serán omitidos. Use --headless para instalarlos de todos modos."
    elif [[ "$HEADLESS" == "true" ]]; then
        log "INFO" "Modo headless activado: instalando todos los paquetes incluyendo GUI"
    fi
    
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
        # Leer dinámicamente todos los archivos .pkg disponibles
        lists=""
        for pkg_file in "$CONFIG_DIR"/*.pkg; do
            if [[ -f "$pkg_file" ]]; then
                local pkg_name=$(basename "$pkg_file" .pkg)
                lists="$lists $pkg_name"
            fi
        done
        lists=$(echo "$lists" | xargs)  # Limpiar espacios extra
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
