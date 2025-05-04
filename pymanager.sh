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
UNDERLINE="\033[4m"
ITALIC="\033[3m"

# === Funciones de Utilidad (Logging, Mensajes) ===
# Mover definiciones aquí, ANTES de usarlas

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

# === Comprobaciones Iniciales y otras utilidades ===

# Detectar si gum está disponible (Ahora puede llamar a log)
HAS_GUM=false
if command -v gum &> /dev/null; then
    HAS_GUM=true
    log "INFO" "Comando 'gum' detectado. Se usarán menús mejorados."
else
    log "INFO" "Comando 'gum' no encontrado. Se usarán menús básicos."
fi

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
    local target_venv_path="$1" # Siempre es BIN_VENV_DIR para --install
    local python_executable=""

    mostrar_info "====================================================="
    mostrar_info "  Instalando/Actualizando entorno GLOBAL default    "
    mostrar_info "====================================================="
    log "INFO" "Iniciando --install para el entorno global: $target_venv_path"

    # --- Determinar y mostrar versión de Python --- 
    if [ -d "$target_venv_path" ] && [ -x "$target_venv_path/bin/python" ]; then
        # El entorno ya existe, obtener versión interna
        python_executable="$target_venv_path/bin/python"
        local existing_version=$($python_executable --version 2>&1)
        mostrar_info "El entorno global default ya existe. Se usará su Python: $existing_version"
        log "INFO" "Entorno global $target_venv_path existe. Python: $existing_version"
    else
        # El entorno NO existe, determinar qué Python se USARÁ para crearlo
        mostrar_info "El entorno global default no existe. Se creará."
        # Buscar última versión disponible (lógica copiada/adaptada de create_venv)
        local versions_to_try=("3.12" "3.11" "3.10" "3.9") 
        local found_python=false
        for ver in "${versions_to_try[@]}"; do
            if command -v "python${ver}" &> /dev/null; then
                python_executable="python${ver}"
                found_python=true
                break
            fi
        done
        if ! $found_python; then
            if command -v python3 &> /dev/null; then
                python_executable="python3"
                mostrar_warning "No se encontró versión específica (3.12, ...). Se usará 'python3' por defecto para crear el entorno."
            else
                mostrar_error "No se encontró ningún ejecutable de Python para crear el entorno."
                exit 1
            fi
        fi
        mostrar_info "Se usará '$python_executable' para crear el entorno global default."
        log "INFO" "Se usará $python_executable para crear $target_venv_path"
    fi
    # --- Fin Determinar versión --- 

    # --- Setup Temp File for Pip Output --- 
    local TEMP_PIP_LOG="/tmp/pymanager_pip_output.$$.log"
    trap 'rm -f "$TEMP_PIP_LOG"' EXIT SIGINT SIGTERM
    log "INFO" "Usando archivo temporal para salida de pip: $TEMP_PIP_LOG"

    # --- Lógica de Creación / Reinstalación --- 
    local reinstall_env=false
    if [ -d "$target_venv_path" ]; then
        # Ya mostramos info sobre la versión existente, solo preguntar si reinstalar
        read -p "¿Desea reinstalar el entorno global default existente? (s/N/c=cancelar): " confirm
        if [[ "$confirm" =~ ^[Cc]$ ]]; then mostrar_info "Operación cancelada."; exit 0;
        elif [[ "$confirm" =~ ^[Ss]$ ]]; then 
            reinstall_env=true
            # Si reinstalamos, necesitamos saber qué Python usar (el determinado antes si no existía, o podríamos volver a buscar)
            # Para consistencia, usemos el determinado al principio
            mostrar_info "Se reinstalará usando $python_executable"
            log "INFO" "Se reinstalará $target_venv_path usando $python_executable"
        else 
            mostrar_info "Se usarán los paquetes del entorno existente."
            reinstall_env=false # Asegurar que no se reinstala
        fi
    else
        reinstall_env=true # Si no existe, siempre se "reinstala" (crea)
    fi

    # Reinstalar si es necesario
    if [ "$reinstall_env" = true ] && [ -d "$target_venv_path" ]; then
        mostrar_info "Eliminando entorno global default existente..."
        echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Eliminando $target_venv_path... "; if rm -rf "$target_venv_path"; then echo -e "${COLOR_GREEN}✓${COLOR_RESET}"; else echo -e "${COLOR_RED}✗${COLOR_RESET}"; mostrar_error "No se pudo eliminar."; exit 1; fi
    fi

    # Crear si no existe (o se acaba de borrar)
    if [ ! -d "$target_venv_path" ]; then
        ensure_venv_dir # Asegurar $HOME/.venv
        mostrar_info "Creando entorno virtual global default con $python_executable en: $target_venv_path"
        echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Inicializando entorno virtual... "
        # Usar el python_executable determinado
        if "$python_executable" -m venv "$target_venv_path" >> "$LOG_FILE" 2>&1; then 
             echo -e "${COLOR_GREEN}✓${COLOR_RESET}"; log "INFO" "Entorno $target_venv_path creado con $python_executable.";
             mostrar_exito "Entorno global default creado en $target_venv_path."
             # Mensaje de activación específico para entorno global
             echo -e "${COLOR_YELLOW}Para activar este entorno global, ejecuta:${COLOR_RESET}"
             echo -e "  ${BOLD}source $target_venv_path/bin/activate${COLOR_RESET}"
        else 
             echo -e "${COLOR_RED}✗${COLOR_RESET}"; mostrar_error "Falló la creación del entorno global con $python_executable."; exit 1; 
        fi
    fi
    # --- Fin Lógica Creación --- 

    # --- Determinar qué requirements.txt usar --- 
    local requirements_path_to_use=""
    local home_reqs="$HOME/requirements.txt"
    local script_dir_reqs="$SCRIPT_DIR/requirements.txt" # $DEFAULT_ENV_REQUIREMENTS_PATH original

    if [ -f "$home_reqs" ]; then
        requirements_path_to_use="$home_reqs"
        mostrar_info "Usando archivo de requisitos encontrado en HOME: $requirements_path_to_use"
        log "INFO" "Se usará $requirements_path_to_use (desde HOME) para la instalación."
    elif [ -f "$script_dir_reqs" ]; then
        requirements_path_to_use="$script_dir_reqs"
        mostrar_info "Usando archivo de requisitos encontrado en el directorio del script: $requirements_path_to_use"
        log "INFO" "Se usará $requirements_path_to_use (desde SCRIPT_DIR) para la instalación."
    else
        mostrar_error "No se encontró archivo 'requirements.txt' ni en '$HOME' ni en '$SCRIPT_DIR'."
        log "ERROR" "No se encontró requirements.txt en $HOME ni en $SCRIPT_DIR."
        # Decidir si salir con error o continuar sin instalar paquetes
        # Optamos por continuar pero mostrar advertencia, ya que el entorno base puede haberse creado
        mostrar_advertencia "No se instalarán paquetes."
        # Salir aquí si prefieres que sea un error fatal:
        # exit 1 
        # O simplemente salir de la función si el resto no debe ejecutarse:
        return 0 # O 1 si quieres indicar un estado de "advertencia"
    fi
    # --- Fin Determinar requirements.txt --- 

    # Verificación de conexión a internet (puede ir antes o después de buscar reqs)
    if ! verificar_conexion_internet; then mostrar_advertencia "Sin conexión, no se instalarán paquetes."; return 0; fi

    # Actualizar pip (usando el pip del entorno)
    mostrar_info "Actualizando pip..."; echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Actualizando pip... "
    # Capturar salida de actualización de pip también, por si acaso
    if ("$target_venv_path/bin/pip" install --upgrade pip >> "$TEMP_PIP_LOG" 2>&1); then echo -e "${COLOR_GREEN}✓${COLOR_RESET}"; else echo -e "${COLOR_RED}✗${COLOR_RESET}"; mostrar_advertencia "Fallo al actualizar pip. Ver $TEMP_PIP_LOG"; log "WARN" "Fallo pip update"; fi

    # --- INSTALLATION WITH OUTPUT CAPTURE ---
    mostrar_info "Instalando/actualizando paquetes desde $requirements_path_to_use (salida capturada)..."
    # Usar la ruta determinada
    local pip_install_cmd="$target_venv_path/bin/pip install -r \"$requirements_path_to_use\""
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

        mostrar_exito "Instalación/actualización desde $requirements_path_to_use completada."
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

    log "INFO" "Comando --install completado para $target_venv_path. Mensaje de activación mostrado."
    rm -f "$TEMP_PIP_LOG" # Limpieza explícita si todo va bien
    trap - EXIT SIGINT SIGTERM # Limpiar trap si salimos normally
}

# Comando: Listar paquetes instalados (seleccionando entre locales/global)
list_packages() {
    local options=()
    local env_paths=()
    local global_env_valid=false
    local local_envs_found=false
    # Asumimos que HAS_GUM se define al inicio del script
    # HAS_GUM=false; if command -v gum &> /dev/null; then HAS_GUM=true; fi

    # --- Detectar Global ---
    if [ -d "$BIN_VENV_DIR" ] && [ -x "$BIN_VENV_DIR/bin/pip" ]; then
        global_env_valid=true
        options+=("Global: $BIN_VENV_DIR")
        env_paths+=("$BIN_VENV_DIR")
        log "INFO" "Entorno global default detectado y válido."
    else
         log "INFO" "Entorno global default no encontrado o inválido."
    fi

    # --- Detectar Locales ---
    local local_venv_base_dir="$PWD/.venv"
    if [ -d "$local_venv_base_dir" ]; then
        log "INFO" "Directorio local .venv encontrado. Buscando entornos..."
        local found_local=false
        # Usar find para buscar directorios que contengan un bin/pip ejecutable
        while IFS= read -r -d $'\0' potential_env_path; do
            local env_name=$(basename "$potential_env_path")
            # Añadir solo si es un directorio y pip es ejecutable
             if [ -d "$potential_env_path" ] && [ -x "$potential_env_path/bin/pip" ]; then
                 # Formato de opción mejorado para claridad
                 local display_name="Local: $env_name ($potential_env_path)"
                 if [[ "$env_name" == "default" ]]; then
                    display_name="Local: default ($potential_env_path)"
                 fi 
                 options+=("$display_name")
                 env_paths+=("$potential_env_path")
                 log "INFO" "Entorno local válido encontrado: $env_name en $potential_env_path"
                 found_local=true
             else
                log "WARN" "Directorio $potential_env_path encontrado pero no es un entorno válido (falta pip ejecutable?)."
             fi
        done < <(find "$local_venv_base_dir" -maxdepth 1 -mindepth 1 -type d -print0) # Buscar solo directorios en el primer nivel

        if $found_local; then
             local_envs_found=true
        else
            log "INFO" "Directorio local .venv existe pero no contiene entornos válidos."
        fi
    else
        log "INFO" "Directorio local .venv no encontrado."
    fi

    # --- Decidir qué listar ---
    local target_venv_path=""
    local env_name_display=""

    if [ ${#options[@]} -eq 0 ]; then
        # No hay entornos válidos
        mostrar_error "No se encontraron entornos virtuales válidos (ni global ni locales)."
        mostrar_info "Usa 'pymanager.sh --create' para crear uno local o 'pymanager.sh --install' para el global."
        exit 1
    elif [ ${#options[@]} -eq 1 ]; then
        # Solo hay una opción, usarla directamente
        target_venv_path="${env_paths[0]}"
        env_name_display="${options[0]}" # Usar la etiqueta completa (ej: "Global: ...")
        mostrar_info "Listando paquetes del único entorno disponible: $env_name_display"
    else
        # Hay múltiples opciones, mostrar menú
        mostrar_info "Múltiples entornos encontrados. Por favor, selecciona cuál listar:"
        local choice=""
        # Comprobar HAS_GUM aquí o asumir que está definida globalmente
        if [[ "${HAS_GUM:-false}" == "true" ]] && command -v gum &> /dev/null; then # Doble check por si acaso
             # Usar gum choose
             choice=$(printf "%s\n" "${options[@]}" | gum choose --header "Selecciona el entorno")
             # Comprobar si el usuario canceló en gum (salida vacía)
             if [ -z "$choice" ]; then
                mostrar_info "Operación cancelada."
                exit 0
             fi
        else
            # Fallback a select de Bash
            mostrar_info "(Usando menú básico. Instala 'gum' para una mejor experiencia)."
            PS3="Selecciona el número del entorno (o q para salir): " # Prompt mejorado
            select opt in "${options[@]}" "Salir"; do
                if [[ "$REPLY" == "q" || "$opt" == "Salir" ]]; then
                    mostrar_info "Operación cancelada."
                    exit 0
                elif [[ -n "$opt" ]]; then
                    choice="$opt"
                    break
                else
                    echo "Selección inválida. Intenta de nuevo."
                fi
            done
        fi

        # Procesar la elección (ya no necesitamos verificar si está vacío por los checks anteriores)
        # Encontrar la ruta correspondiente a la opción elegida
        for i in "${!options[@]}"; do
            if [[ "${options[$i]}" == "$choice" ]]; then
                target_venv_path="${env_paths[$i]}"
                env_name_display="$choice"
                break
            fi
        done

        # Fallback por si algo muy raro pasa
        if [ -z "$target_venv_path" ]; then
             mostrar_error "Error interno: No se pudo encontrar la ruta para la selección '$choice'."
             exit 1
        fi
        mostrar_info "Listando paquetes del entorno seleccionado: $env_name_display"
    fi


    # --- Listar paquetes del entorno seleccionado ---
    log "INFO" "Ejecutando 'pip list' en $target_venv_path ($env_name_display)"
    echo -e "${COLOR_BLUE}--- Paquetes en entorno '$env_name_display' ---${COLOR_RESET}"

    # Obtener y mostrar versión de Python
    local python_ver="N/A"
    if [ -x "$target_venv_path/bin/python" ]; then
        python_ver=$("$target_venv_path/bin/python" --version 2>&1)
        echo -e "${COLOR_CYAN}Versión de Python:${COLOR_RESET} $python_ver"
        log "INFO" "Versión de Python en $target_venv_path: $python_ver"
    else
        mostrar_advertencia "No se pudo encontrar el ejecutable python en $target_venv_path para determinar la versión."
        log "WARN" "No se encontró python ejecutable en $target_venv_path"
    fi
    echo # Línea extra para separar

    # Ejecutar pip list y capturar error explícitamente
    if ! "$target_venv_path/bin/pip" list; then
        local pip_ret=$?
        mostrar_error "Fallo al ejecutar 'pip list' (código $pip_ret) en el entorno '$env_name_display'."
        mostrar_info "El entorno '$target_venv_path' puede estar dañado."
        mostrar_info "Consulta $LOG_FILE para más detalles."
        exit 1
    fi

    echo -e "${COLOR_BLUE}-------------------------------------------------${COLOR_RESET}"
    log "INFO" "'pip list' completado para $target_venv_path ($env_name_display)"
}

# Comando: Crear entorno virtual LOCAL (default o nombrado)
# Uso: create_venv [--python <version>] [<nombre_env>]
create_venv() {
    local python_version_requested=""
    local env_name="default"
    local target_venv_path=""
    local venv_type=""
    local python_executable=""

    # Procesar argumentos para create_venv (más complejo ahora)
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --python)
                if [ -z "$2" ]; then
                    mostrar_error "La opción --python requiere un argumento de versión (ej: 3.10)."
                    exit 1
                fi
                # Validar formato básico de versión (ej: 3.10, 3.11)
                if [[ ! "$2" =~ ^[0-9]+\.[0-9]+$ ]]; then
                     mostrar_error "Formato de versión inválido para --python: '$2'. Use X.Y (ej: 3.10)."
                     exit 1
                fi
                python_version_requested="$2"
                log "INFO" "Versión de Python solicitada: $python_version_requested"
                shift 2 # Consume --python y la versión
                ;;
            --*)
                mostrar_error "Opción no reconocida para --create: $1"
                show_help
                exit 1
                ;;
            *)
                # Asumir nombre de entorno
                if [ -z "$env_name" ] || [ "$env_name" == "default" ]; then # Permitir sobrescribir default si es el primer arg
                    if [[ "$1" == --* ]]; then # No permitir nombres que parezcan opciones
                        mostrar_error "Nombre de entorno inválido: '$1'. No debe empezar con --."
                        exit 1
                    fi
                    env_name="$1"
                else
                    mostrar_error "Demasiados argumentos de nombre de entorno para --create: $1"
                    show_help
                    exit 1
                fi
                shift # Consume nombre del entorno
                ;;
        esac
    done

    # Determinar el ejecutable de Python a usar
    if [ -n "$python_version_requested" ]; then
        # Versión específica solicitada
        python_executable="python${python_version_requested}"
        if ! command -v "$python_executable" &> /dev/null; then
            mostrar_error "No se encontró la versión de Python solicitada ($python_executable) en el sistema."
            mostrar_info "Versiones comunes disponibles podrían ser python3.9, python3.10, python3.11, etc."
            exit 1
        fi
        mostrar_info "Usando la versión de Python solicitada: $python_executable"
    else
        # Ninguna versión solicitada, buscar la última disponible (ej: 3.12 -> 3.11 -> 3.10 -> 3.9 -> python3)
        mostrar_info "No se especificó versión de Python. Buscando la última disponible..."
        local versions_to_try=("3.12" "3.11" "3.10" "3.9") # Añadir/quitar según sea necesario
        local found_python=false
        for ver in "${versions_to_try[@]}"; do
            if command -v "python${ver}" &> /dev/null; then
                python_executable="python${ver}"
                mostrar_info "Encontrada versión: $python_executable"
                found_python=true
                break
            fi
        done
        # Si no se encontró ninguna versión específica, usar 'python3' por defecto
        if ! $found_python; then
            if command -v python3 &> /dev/null; then
                python_executable="python3"
                mostrar_warning "No se encontró una versión específica (3.12, 3.11, ...). Usando 'python3' por defecto."
            else
                mostrar_error "No se encontró ningún ejecutable de Python (ni específico ni python3)."
                exit 1
            fi
        fi
    fi
    log "INFO" "Ejecutable de Python seleccionado para venv: $python_executable"

    # Determinar tipo y ruta (SIEMPRE LOCAL)
    if [ "$env_name" == "default" ]; then
        venv_type="local_default"
    else
        venv_type="local_named"
    fi
    local local_venv_base_dir="$PWD/.venv"
    target_venv_path="$local_venv_base_dir/$env_name"

    mostrar_info "Preparando para crear entorno $venv_type '$env_name': $target_venv_path"
    log "INFO" "Intentando crear entorno $venv_type en $target_venv_path usando $python_executable"

    # Crear directorio base local .venv si no existe
    if [ ! -d "$local_venv_base_dir" ]; then
        log "INFO" "Creando directorio base local $local_venv_base_dir"
        if ! mkdir -p "$local_venv_base_dir"; then mostrar_error "No se pudo crear $local_venv_base_dir"; exit 1; fi
    fi

    # --- Lógica de creación / reinstalación --- 
    local reinstall_env=false
    if [ -d "$target_venv_path" ]; then
        read -p "El entorno local '$target_venv_path' ya existe. ¿Desea reinstalarlo? (s/N/c=cancelar): " confirm_create
        if [[ "$confirm_create" =~ ^[Cc]$ ]]; then mostrar_info "Operación cancelada."; exit 0;
        elif [[ "$confirm_create" =~ ^[Ss]$ ]]; then reinstall_env=true;
        else mostrar_info "Operación cancelada. No se reinstalará el entorno existente."; exit 0; fi # Si no es S o C, cancelar
    else
        reinstall_env=true # Si no existe, siempre crear
    fi

    # Reinstalar si es necesario
    if [ "$reinstall_env" = true ] && [ -d "$target_venv_path" ]; then
        mostrar_info "Eliminando entorno local existente en '$target_venv_path'..."
        echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Eliminando $target_venv_path... ";
        if rm -rf "$target_venv_path"; then echo -e "${COLOR_GREEN}✓${COLOR_RESET}"; log "INFO" "Directorio local eliminado: $target_venv_path";
        else echo -e "${COLOR_RED}✗${COLOR_RESET}"; mostrar_error "No se pudo eliminar $target_venv_path."; exit 1; fi
    fi

    # Crear si no existe (o se acaba de borrar)
    if [ ! -d "$target_venv_path" ]; then
        mostrar_info "Creando estructura de entorno virtual local con $python_executable en: $target_venv_path"
        echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Inicializando entorno virtual... "
        # Usar el ejecutable de Python seleccionado
        if "$python_executable" -m venv "$target_venv_path" >> "$LOG_FILE" 2>&1; then
             echo -e "${COLOR_GREEN}✓${COLOR_RESET}"; log "INFO" "Entorno local $target_venv_path creado.";
             mostrar_exito "Entorno local '$env_name' creado en $target_venv_path."
             # Mensaje de activación específico para entorno local
             echo -e "${COLOR_YELLOW}Para activar este entorno local, desde este directorio ejecuta:${COLOR_RESET}"
             echo -e "  ${BOLD}source $target_venv_path/bin/activate${COLOR_RESET}"
        else
             echo -e "${COLOR_RED}✗${COLOR_RESET}"; mostrar_error "Falló la creación del entorno en $target_venv_path."; exit 1;
        fi
    fi
    # --- Fin lógica creación / reinstalación ---

    log "INFO" "Comando --create completado para $target_venv_path ($venv_type)."
    # No hay instalación de paquetes aquí
}

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

# Función para mostrar la ayuda (estilo packages.sh)
show_help() {
    # ... (líneas de título, uso, etc.) ...
    echo
    echo -e "${UNDERLINE}Comandos:${COLOR_RESET}"
    echo -e "  ${BOLD}--create [<nombre_env>] [--python <ver>]${COLOR_RESET} Crea un entorno virtual LOCAL."
    echo -e "                     - Sin <nombre_env>: Usa nombre 'default'."
    echo -e "                     - Con <nombre_env>: Usa ese nombre para el directorio en ./.venv/"
    echo -e "                     - Con --python <ver> (ej: 3.10): Usa esa versión de Python."
    echo -e "                     - Sin --python: Intenta usar la última versión disponible (3.12, 3.11, etc.)."
    echo -e "                     (Siempre crea en ${BOLD}./.venv/${COLOR_RESET}, no instala paquetes)."
    echo -e "  ${BOLD}--activate${COLOR_RESET}       Muestra comando para activar entorno global ${BOLD}~/.venv/default${COLOR_RESET}."
    echo -e "                     (No activa entornos locales automáticamente)."
    echo -e "  ${BOLD}--list${COLOR_RESET}           Lista paquetes y versión de Python del entorno seleccionado."
    echo -e "                     (Presenta menú si hay múltiples entornos locales/global)."
    echo -e "  ${BOLD}--remove [<nombre_env>]${COLOR_RESET} Elimina un entorno virtual."
    echo -e "                     - Sin <nombre_env>: Intenta eliminar ${BOLD}./.venv/default${COLOR_RESET}. Si no existe,"
    echo -e "                       intenta eliminar el global ${BOLD}~/.venv/default${COLOR_RESET}."
    echo -e "                     - Con <nombre_env>: Elimina el local ${BOLD}./.venv/<nombre_env>${COLOR_RESET}."
    echo -e "                     (Pide confirmación)."
    echo -e "  ${BOLD}--install${COLOR_RESET}        Crea/actualiza el entorno GLOBAL ${BOLD}~/.venv/default/${COLOR_RESET} e instala"
    echo -e "                     paquetes desde ${BOLD}requirements.txt${COLOR_RESET} en él."
    echo -e "  ${BOLD}--help${COLOR_RESET}, ${BOLD}-h${COLOR_RESET}       Muestra esta ayuda."
    echo -e "  ${BOLD}--version${COLOR_RESET}      Muestra la versión del script."
    echo
    echo -e "${UNDERLINE}Notas:${COLOR_RESET}"
    echo -e "* ${BOLD}--create${COLOR_RESET} es siempre para entornos locales (${BOLD}./.venv/${COLOR_RESET}) y permite especificar versión con ${BOLD}--python${COLOR_RESET}."
    echo -e "* ${BOLD}--install${COLOR_RESET} es siempre para el entorno global default (${BOLD}~/.venv/default${COLOR_RESET})."
    echo -e "* Los logs se guardan en ${BOLD}/home/mrosero/.logs/pymanager.log${COLOR_RESET}."
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
        show_help
        exit 1
    fi
    shift # Quitar el comando de la lista de argumentos para procesar opciones

    case "$comando" in
        --create)
            # Pasar todos los argumentos restantes a create_venv
            create_venv "$@"
            ;;
        --activate)
            activate_venv
            ;;
        --list)
            list_packages
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
            show_help
            ;;
        --version)
            echo "${APP_NAME} v${APP_VERSION}"
            exit 0
            ;;
        *)
            mostrar_error "Comando '$comando' no reconocido."
            show_help
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