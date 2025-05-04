#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-04-27 10:15:53
# Version: 0.4.0
#
# pymanager.sh - Gestión simplificada de entornos virtuales Python
# -----------------------------------------------------------------------------
#
# Description: Script para crear, activar, listar y eliminar entornos virtuales Python (.venv)

# Configuración básica
# ==================
VENV_BASE_DIR_RELATIVE=".venv"
VENV_DIR="$HOME/$VENV_BASE_DIR_RELATIVE"
BIN_VENV_DIR="$VENV_DIR/default"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
DEFAULT_ENV_REQUIREMENTS_PATH="$SCRIPT_DIR/requirements.txt"
LOG_DIR="$HOME/.logs"
LOG_FILE="$LOG_DIR/pymanager.log"
APP_NAME="Gestor de Entornos Python (pymanager)"
VERSION="0.4.0"
AUTHOR="Mauro Rosero P."
ORIGINAL_ARGS=("$@")

# Colores y formatos (estilo packages.sh)
COLOR_GREEN="\033[0;32m"
COLOR_YELLOW="\033[0;33m"
COLOR_RED="\033[0;31m"
COLOR_CYAN="\033[0;36m"
COLOR_BLUE="\033[0;34m"
COLOR_MAGENTA="\033[0;35m"
COLOR_RESET="\033[0m"
BOLD="\033[1m"
UNDERLINE="\033[4m" # Añadido para compatibilidad con ayuda anterior
ITALIC="\033[3m"    # Añadido si se quiere usar

# Funciones de Utilidad (Logging, Mensajes, Prerrequisitos, etc.)
# ============================================================

# Función de logging
log() {
    local level="$1"; local message="$2"; mkdir -p "$LOG_DIR"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] - $message" >> "$LOG_FILE"
}
# Funciones para mostrar mensajes coloreados
mostrar_error() { echo -e "${COLOR_RED}${BOLD}Error:${COLOR_RESET}${COLOR_RED} $1${COLOR_RESET}" >&2; log "ERROR" "$1"; }
mostrar_advertencia() { echo -e "${COLOR_YELLOW}${BOLD}Advertencia:${COLOR_RESET}${COLOR_YELLOW} $1${COLOR_RESET}"; log "WARN" "$1"; }
mostrar_exito() { echo -e "${COLOR_GREEN}${BOLD}Éxito:${COLOR_RESET}${COLOR_GREEN} $1${COLOR_RESET}"; log "INFO" "$1"; }
mostrar_info() { echo -e "${COLOR_BLUE}Info:${COLOR_RESET} $1"; }

# Verificar prerrequisitos (Python3 y venv)
check_prerequisites() {
    log "INFO" "Verificando prerrequisitos (python3, python3-venv)"
    local error_found=0
    if ! command -v python3 &> /dev/null; then mostrar_error "Python 3 no está instalado..."; error_found=1; fi
    if ! python3 -c "import venv" &> /dev/null; then mostrar_error "Módulo 'venv' no disponible..."; error_found=1; fi
    if [ "$error_found" -eq 1 ]; then exit 1; fi
    log "INFO" "Prerrequisitos verificados."
}
# Asegurar que el directorio base de venv exista
ensure_venv_dir() {
    if [ ! -d "$VENV_DIR" ]; then
        log "INFO" "Creando $VENV_DIR"; if ! mkdir -p "$VENV_DIR"; then mostrar_error "No se pudo crear $VENV_DIR"; exit 1; fi
        log "INFO" "$VENV_DIR creado."
    fi
}
# Verificar conexión a internet
verificar_conexion_internet() {
    if ping -c 1 8.8.8.8 > /dev/null 2>&1 || ping -c 1 1.1.1.1 > /dev/null 2>&1; then
        log "INFO" "Conexión internet OK."; return 0
    else
        mostrar_advertencia "No se detectó conexión a internet."; log "WARN" "Sin conexión internet."; return 1
    fi
}
# Función para obtener la ruta de un entorno local si existe y es válido
get_local_venv_path() {
    local local_venv="$PWD/.venv"
    if [ -d "$local_venv" ] && [ -f "$local_venv/bin/activate" ]; then echo "$local_venv"; else echo ""; fi
}

# Funciones Principales de Comandos (create, activate, add, remove, etc.)
# =====================================================================

# --- install_default_env Simplified with Output Parsing ---
install_default_env() {
    local target_venv_path="$1"
    mostrar_info "====================================================="
    mostrar_info "  Instalando entorno Python predeterminado (default)"
    mostrar_info "====================================================="
    log "INFO" "Iniciando instalación del entorno por defecto en $target_venv_path"

    # --- Setup Temp File for Pip Output --- 
    local TEMP_PIP_LOG="/tmp/pymanager_pip_output.$$.log"
    # Ensure cleanup on exit
    trap 'rm -f "$TEMP_PIP_LOG"' EXIT SIGINT SIGTERM
    log "INFO" "Usando archivo temporal para salida de pip: $TEMP_PIP_LOG"
    # --- End Setup ---

    local reinstall_env=false
    if [ -d "$target_venv_path" ]; then
        read -p "El entorno predeterminado '$target_venv_path' ya existe. ¿Desea reinstalarlo? (s/N/c=cancelar): " confirm
        if [[ "$confirm" =~ ^[Cc]$ ]]; then mostrar_info "Operación cancelada."; exit 0;
        elif [[ "$confirm" =~ ^[Ss]$ ]]; then reinstall_env=true;
        else mostrar_info "Usando el entorno predeterminado existente."; fi
    else
        reinstall_env=true # Si no existe, es como reinstalar
    fi

    # Reinstalar si es necesario
    if [ "$reinstall_env" = true ] && [ -d "$target_venv_path" ]; then
        mostrar_info "Eliminando entorno predeterminado existente..."
        echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Eliminando $target_venv_path... "; if rm -rf "$target_venv_path"; then echo -e "${COLOR_GREEN}✓${COLOR_RESET}"; else echo -e "${COLOR_RED}✗${COLOR_RESET}"; mostrar_error "No se pudo eliminar."; exit 1; fi
    fi

    # Crear si no existe (o se acaba de borrar)
    if [ ! -d "$target_venv_path" ]; then
        ensure_venv_dir # Asegurar $VENV_DIR
        mostrar_info "Creando entorno virtual predeterminado en: $target_venv_path"
        echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Inicializando entorno virtual... "
        if python3 -m venv "$target_venv_path" >> "$LOG_FILE" 2>&1; then echo -e "${COLOR_GREEN}✓${COLOR_RESET}"; else echo -e "${COLOR_RED}✗${COLOR_RESET}"; mostrar_error "Falló la creación."; exit 1; fi
        log "INFO" "Entorno $target_venv_path creado."
    fi

    # Verificaciones comunes
    if [ ! -f "$DEFAULT_ENV_REQUIREMENTS_PATH" ]; then mostrar_error "Archivo requisitos '$DEFAULT_ENV_REQUIREMENTS_PATH' no encontrado."; exit 1; fi
    if ! verificar_conexion_internet; then mostrar_advertencia "Sin conexión, no se instalarán paquetes."; exit 0; fi

    # Actualizar pip
    mostrar_info "Actualizando pip..."; echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Actualizando pip... "
    # Capturar salida de actualización de pip también, por si acaso
    if ("$target_venv_path/bin/pip" install --upgrade pip >> "$TEMP_PIP_LOG" 2>&1); then echo -e "${COLOR_GREEN}✓${COLOR_RESET}"; else echo -e "${COLOR_RED}✗${COLOR_RESET}"; mostrar_advertencia "Fallo al actualizar pip. Ver $TEMP_PIP_LOG"; log "WARN" "Fallo pip update"; fi

    # --- INSTALLATION WITH OUTPUT CAPTURE ---
    mostrar_info "Instalando/actualizando paquetes desde $DEFAULT_ENV_REQUIREMENTS_PATH (salida capturada)..."
    local pip_install_cmd="$target_venv_path/bin/pip install -r \"$DEFAULT_ENV_REQUIREMENTS_PATH\""
    log "INFO" "Ejecutando: $pip_install_cmd > $TEMP_PIP_LOG 2>&1"

    # Ejecutar pip install -r capturando toda la salida
    eval "$pip_install_cmd" > "$TEMP_PIP_LOG" 2>&1
    local pip_ret=$?
    # Copiar salida temporal al log principal también
    cat "$TEMP_PIP_LOG" >> "$LOG_FILE"

    if [ $pip_ret -eq 0 ]; then
        # --- Parse Output on Success --- 
        local satisfied_count=$(grep -c 'Requirement already satisfied' "$TEMP_PIP_LOG")
        
        # Extract the list of successfully installed/updated packages
        local installed_list=$(grep '^Successfully installed ' "$TEMP_PIP_LOG" | sed 's/^Successfully installed //')
        local installed_count=0
        if [ -n "$installed_list" ]; then
            installed_count=$(echo "$installed_list" | wc -w)
        fi
        
        # Extract the list of ignored packages
        local ignored_list=$(grep '^Ignoring .* markers' "$TEMP_PIP_LOG" | sed -E 's/^Ignoring ([^:]+):.*/\1/')
        local ignored_count=0
        if [ -n "$ignored_list" ]; then
             # Count lines in the list
             ignored_count=$(echo "$ignored_list" | wc -l)
        fi

        mostrar_exito "Instalación/actualización desde $DEFAULT_ENV_REQUIREMENTS_PATH completada."
        echo -e "${COLOR_BLUE}Resumen:${COLOR_RESET}"
        # Always show satisfied count
        echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Paquetes ya satisfechos: $satisfied_count"
        # Show installed/updated list if any
        if [ "$installed_count" -gt 0 ]; then
             echo -e "  ${COLOR_YELLOW}↑${COLOR_RESET} Paquetes instalados/actualizados ($installed_count):"
             echo "$installed_list" | fold -s -w 70 | sed 's/^/    /' 
        fi
        # Show ignored list if any
        if [ "$ignored_count" -gt 0 ]; then
             echo -e "  ${COLOR_CYAN}- ${COLOR_RESET} Paquetes ignorados (marcador) ($ignored_count):"
             # Indent the list for clarity
             echo "$ignored_list" | sed 's/^/    /' 
        fi
        
        log "INFO" "pip install -r exitoso. Satisfechos: $satisfied_count, Instalados/Actualizados: $installed_count, Ignorados: $ignored_count"

    else
        # --- Show Error Details on Failure --- 
        mostrar_error "Hubo un error (código $pip_ret) durante la instalación con 'pip install -r'."
        mostrar_info "Mostrando las últimas 10 líneas de la salida de pip:"
        echo "-------------------- Inicio Salida Pip (Error) --------------------" 
        tail -n 10 "$TEMP_PIP_LOG" | sed 's/^/  /' # Indentar salida
        echo "-------------------- Fin Salida Pip (Error) ---------------------"
        mostrar_info "Consulte el archivo completo $TEMP_PIP_LOG y $LOG_FILE para más detalles."
        exit 1 # Salir con error si pip falló
    fi
    # --- END OF INSTALLATION WITH OUTPUT CAPTURE ---

    # --- Mensaje final sobre activación --- 
    mostrar_info "Entorno '$target_venv_path' listo."
    # Sugerir el comando source estándar
    echo -e "${COLOR_YELLOW}Para activar este entorno global, ejecuta:${COLOR_RESET}"
    echo -e "  ${BOLD}source $target_venv_path/bin/activate${COLOR_RESET}"
    # Opcional: Si tienes un alias específico, puedes sugerirlo también
    # if command -e pybin &> /dev/null; then # Ejemplo de comprobación de alias
    #     echo -e "${COLOR_YELLOW}O usa tu alias:${COLOR_RESET} ${BOLD}pybin${COLOR_RESET}"
    # fi

    log "INFO" "Comando --install completado para $target_venv_path. Mensaje de activación mostrado."
    rm -f "$TEMP_PIP_LOG" # Limpieza explícita si todo va bien
    trap - EXIT SIGINT SIGTERM # Limpiar trap si salimos normally
}

# Comando: Listar paquetes instalados (default o local)
list_packages() {
    local target_venv_path="$BIN_VENV_DIR"
    local env_name="default (global)"

    local local_venv_path=$(get_local_venv_path)
    if [ -n "$local_venv_path" ]; then
        target_venv_path=$local_venv_path
        env_name="local ($(basename "$PWD"))"
        mostrar_info "Listando paquetes del entorno local: $target_venv_path"
    else
        ensure_venv_dir # Asegurar ~/.venv si usamos el global
        mostrar_info "Listando paquetes del entorno predeterminado global: $target_venv_path"
    fi

    if [ ! -d "$target_venv_path" ] || [ ! -f "$target_venv_path/bin/pip" ]; then
        mostrar_error "Entorno '$env_name' no encontrado o incompleto en $target_venv_path"; exit 1
    fi

    log "INFO" "Listando paquetes en $target_venv_path ($env_name)"
    echo -e "${COLOR_BLUE}--- Paquetes en entorno '$env_name' ---${COLOR_RESET}"
    if ! "$target_venv_path/bin/pip" list; then
        mostrar_error "Fallo al listar paquetes con pip list."; exit 1
    fi
    echo -e "${COLOR_BLUE}--------------------------------------${COLOR_RESET}"
}

# ... (Resto de funciones: create_venv, activate_venv, add_package, remove_venv, update_packages, mostrar_ayuda, show_banner, main) ...

# Función para mostrar el banner simple y estético
show_banner() {
  # Ancho deseado (aproximado)
  local width=50

  # Línea superior
  printf '+%*s+\n' "$width" '' | tr ' ' '-'

  # Título centrado
  local title_len=${#APP_NAME}
  local title_pad=$(( (width - title_len) / 2 ))
  printf '|%*s%s%*s|\n' "$title_pad" '' "$APP_NAME" "$((width - title_pad - title_len))" ''

  # Separador
  printf '|%*s|\n' "$width" ''

  # Versión alineada
  local version_text="Version: $VERSION"
  local version_len=${#version_text}
  local version_pad=$((width - version_len - 1))
  printf '| %s%*s|\n' "$version_text" "$version_pad" ''

  # Autor alineado
  local author_text="By: $AUTHOR"
  local author_len=${#author_text}
  local author_pad=$((width - author_len - 1))
  printf '| %s%*s|\n' "$author_text" "$author_pad" ''

  # Línea inferior
  printf '+%*s+\n' "$width" '' | tr ' ' '-'

  echo # Línea en blanco después del banner
}

# Ayuda
usage() {
    # Usar echo -e y las variables de estilo definidas
    echo -e "${BOLD}${COLOR_BLUE}$APP_NAME (pymanager) v${VERSION}${COLOR_RESET} por ${AUTHOR}"
    echo -e "${ITALIC}${COLOR_CYAN}Gestión simplificada de entornos virtuales Python.${COLOR_RESET}"
    echo
    echo -e "${UNDERLINE}Uso:${COLOR_RESET} ${BOLD}pymanager.sh${COLOR_RESET} --comando [opciones]"
    echo
    echo -e "${UNDERLINE}Comandos:${COLOR_RESET}"
    echo -e "  ${BOLD}--create${COLOR_RESET}         Crea el entorno virtual predeterminado (${BOLD}~/.venv/default${COLOR_RESET})"
    echo -e "                     o un entorno local (${BOLD}./.venv${COLOR_RESET}) si existe un ${BOLD}./.venv${COLOR_RESET} vacío."
    echo -e "                     Si ya existe, solo muestra advertencia (a menos que se use con ${BOLD}--install${COLOR_RESET})."
    echo -e "  ${BOLD}--activate${COLOR_RESET}       Muestra el comando para activar el entorno 'default' global."
    echo -e "                     (No activa el entorno local automáticamente)."
    echo -e "  ${BOLD}--list${COLOR_RESET}           Lista los paquetes instalados en el entorno 'default' o local."
    echo -e "  ${BOLD}--remove${COLOR_RESET}         Elimina el entorno 'default' o local (pide confirmación)."
    echo -e "  ${BOLD}--install${COLOR_RESET}        (Opción para ${BOLD}--create${RESET}) Instala/actualiza paquetes desde ${BOLD}requirements.txt${COLOR_RESET}."
    echo -e "                     *Nota: Ahora se usa principalmente con ${BOLD}--create${COLOR_RESET}, o solo si el venv ya existe.*"
    echo -e "  ${BOLD}--help${COLOR_RESET}, ${BOLD}-h${COLOR_RESET}       Muestra esta ayuda."
    echo -e "  ${BOLD}--version${COLOR_RESET}      Muestra la versión del script."
    echo
    echo -e "${UNDERLINE}Notas:${COLOR_RESET}"
    echo -e "* El script prioriza un entorno local (${BOLD}./.venv${COLOR_RESET}) si existe para ${BOLD}--create${COLOR_RESET}, ${BOLD}--list${COLOR_RESET}, ${BOLD}--remove${COLOR_RESET}."
    echo -e "* La activación (${BOLD}--activate${COLOR_RESET}) siempre se refiere al entorno global 'default'."
    echo -e "* La instalación con ${BOLD}--install${COLOR_RESET} usa ${BOLD}requirements.txt${COLOR_RESET} del directorio del script."
    echo -e "* Los logs se guardan en ${BOLD}/home/mrosero/.logs/pymanager.log${COLOR_RESET}."
    # exit 0
}

# --- Flujo Principal ---
main() {
    log "INFO" "=== Inicio ejecución pymanager.sh ==="
    show_banner # Llamada única aquí
    log "INFO" "Argumentos originales: ${ORIGINAL_ARGS[*]}"
    check_prerequisites

    # El primer argumento ahora DEBE ser un comando con --
    local comando=${1}
    # Si no se proporciona comando o no empieza con --, mostrar ayuda
    if [[ -z "$comando" || "$comando" != --* ]]; then
        usage
        exit 1
    fi
    shift # Quitar el comando de la lista de argumentos para procesar opciones

    case "$comando" in
        --create)
            # Pasar el resto de argumentos a create_venv para que pueda ver --install
            create_venv "$@"
            ;;
        --activate)
            activate_venv
            ;;
        --list)
            list_packages # Asumiendo que list_packages no toma argumentos
            ;;
        --remove)
            remove_venv
            ;;
        --install)
            # --install solo ahora actúa como --create --install para el entorno default
            mostrar_info "Ejecutando --install (creará el entorno default si no existe)..."
            # Llamar directamente a la función que crea/instala el default
            # Pasamos la ruta del entorno default como argumento
            install_default_env "$BIN_VENV_DIR"
            ;;
        --help|-h)
            usage
            ;;
        --version)
            echo "${APP_NAME} v${APP_VERSION}"
            exit 0
            ;;
        *)
            mostrar_error "Comando '$comando' no reconocido."
            usage
            exit 1
            ;;
    esac
    log "INFO" "=== Fin ejecución pymanager.sh ==="
    exit 0
}

# Ejecutar main si el script no está siendo "sourced"
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 