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

# --- Nuevas Funciones Auxiliares para Gestión de Entornos ---

# Verifica si una ruta dada es un entorno Python válido (contiene pip ejecutable)
verificar_entorno_python() {
    local venv_path="$1"
    if [[ -d "$venv_path" && -x "$venv_path/bin/pip" ]]; then
        log "DEBUG" "Entorno verificado como válido: $venv_path"
        return 0 # Éxito (entorno válido)
    else
        log "DEBUG" "Entorno verificado como NO válido: $venv_path"
        return 1 # Fracaso (no válido)
    fi
}

# Determina el mejor ejecutable de Python disponible en el sistema
# Devuelve el nombre del ejecutable (ej: python3.11) o "python3" como fallback.
# Sale con error si no se encuentra ninguno.
determinar_python_executable() {
    local python_executable=""
    local versions_to_try=("3.12" "3.11" "3.10" "3.9") # Prioridad
    local found_python=false

    log "INFO" "Determinando ejecutable de Python a usar..."
    for ver in "${versions_to_try[@]}"; do
        if command -v "python${ver}" &> /dev/null; then
            python_executable="python${ver}"
            found_python=true
            log "INFO" "Encontrada versión de Python específica: $python_executable"
            break
        fi
    done

    if ! $found_python; then
        if command -v python3 &> /dev/null; then
            python_executable="python3"
            log "WARN" "No se encontró versión específica (${versions_to_try[*]}). Usando 'python3' por defecto."
            mostrar_advertencia "No se encontró versión específica (${versions_to_try[*]}). Usando 'python3' por defecto."
        else
            log "ERROR" "No se encontró ningún ejecutable de Python (ni específico ni python3)."
            mostrar_error "No se encontró ningún ejecutable de Python (ni específico ni python3) para crear el entorno."
            exit 1
        fi
    fi
    # Devolver el ejecutable encontrado
    echo "$python_executable"
}

# Crea un entorno virtual en la ruta especificada usando el ejecutable Python dado
crear_entorno_python() {
    local venv_path="$1"
    local python_exe="$2"

    log "INFO" "Intentando crear entorno en $venv_path usando $python_exe"
    mostrar_info "Creando entorno virtual en ${COLOR_CYAN}$venv_path${COLOR_RESET} usando ${COLOR_YELLOW}$python_exe${COLOR_RESET}..."

    # Crear directorio padre si no existe (ej: ~/.venv)
    local parent_dir
    parent_dir=$(dirname "$venv_path")
    if [[ ! -d "$parent_dir" ]]; then
        log "INFO" "Creando directorio padre: $parent_dir"
        if ! mkdir -p "$parent_dir"; then
            mostrar_error "No se pudo crear el directorio padre $parent_dir."
            log "ERROR" "Fallo al crear directorio padre $parent_dir"
            return 1
        fi
    fi

    echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Inicializando entorno virtual... "
    # Ejecutar el comando venv, redirigiendo stdout/stderr al log para limpieza
    if "$python_exe" -m venv "$venv_path" >> "$LOG_FILE" 2>&1; then
        echo -e "${COLOR_GREEN}✓${COLOR_RESET}"
        log "INFO" "Entorno creado exitosamente en $venv_path con $python_exe."
        mostrar_exito "Entorno virtual creado en ${COLOR_GREEN}$venv_path${COLOR_RESET}."
        # Mostrar mensaje de activación post-creación
        echo -e "${COLOR_YELLOW}Para activar este entorno, ejecuta:${COLOR_RESET}"
        echo -e "  ${BOLD}source \"$venv_path/bin/activate\"${COLOR_RESET}"
        return 0 # Éxito
    else
        echo -e "${COLOR_RED}✗${COLOR_RESET}"
        log "ERROR" "Falló la creación del entorno en $venv_path con $python_exe. Ver $LOG_FILE."
        mostrar_error "Falló la creación del entorno en ${COLOR_RED}$venv_path${COLOR_RESET}. Consulta $LOG_FILE."
        # Intentar limpiar si falla la creación? Podría dejarlo inconsistente. Mejor no.
        return 1 # Fracaso
    fi
}

# Obtiene la versión de Python de un entorno virtual dado
obtener_version_python_entorno() {
    local venv_path="$1"
    local python_exe="$venv_path/bin/python"
    if [[ -x "$python_exe" ]]; then
        "$python_exe" --version 2>&1 # Devuelve la salida (ej: Python 3.10.12)
    else
        echo "" # Devuelve vacío si no se encuentra python
    fi
}

# --- Fin Funciones Auxiliares ---

# Funciones Principales de Comandos (create, activate, add, remove, etc.)
# =====================================================================

# --- install_default_env Simplified with Output Parsing ---
# ESTA FUNCIÓN SE VUELVE OBSOLETA y será reemplazada/integrada en install_global_package
# Se mantiene por ahora como referencia, pero la llamada en main() se cambiará.
install_default_env() {
    # ... (código existente de install_default_env) ...
    # ... (Será eliminado/refactorizado en la función install_global_package) ...
    mostrar_advertencia "La función install_default_env está obsoleta y será eliminada."
}

# --- Nueva Función para --package-global ---
# Instala un paquete o requirements.txt en el entorno global default
install_global_package() {
    local package_or_reqs_file="$1"
    local venv_path="$BIN_VENV_DIR" # Ruta del entorno global

    mostrar_info "============================================================"
    mostrar_info " Instalando Paquete/Reqs en Entorno GLOBAL (${venv_path}) "
    mostrar_info "============================================================"
    log "INFO" "Iniciando --package-global para '$package_or_reqs_file' en $venv_path"

    # 1. Verificar/Crear Entorno Global
    if ! verificar_entorno_python "$venv_path"; then
        mostrar_advertencia "El entorno global default ${COLOR_YELLOW}${venv_path}${COLOR_RESET} no existe o no es válido."
        local python_exe
        python_exe=$(determinar_python_executable) # Sale si no hay Python
        if ! crear_entorno_python "$venv_path" "$python_exe"; then
             mostrar_error "No se pudo crear el entorno global. Abortando instalación."
             exit 1
        fi
        # Entorno recién creado, continuar
    else
        local py_version
        py_version=$(obtener_version_python_entorno "$venv_path")
        mostrar_info "Entorno global default encontrado. Python: ${COLOR_YELLOW}${py_version:-N/A}${COLOR_RESET}"
        log "INFO" "Entorno global $venv_path existe. Python: ${py_version:-N/A}"
    fi

    # 2. Verificar Conexión y Actualizar Pip
    if ! verificar_conexion_internet; then
        mostrar_advertencia "Sin conexión a internet. No se puede instalar/actualizar."
        log "WARN" "Sin conexión internet, abortando --package-global."
        # Salir aquí podría ser lo más seguro
        exit 1 # O return 1 si prefieres que el script continúe
    fi

    # Setup Temp File for Pip Output
    local TEMP_PIP_LOG="/tmp/pymanager_pip_output.$$.log"
    trap 'rm -f "$TEMP_PIP_LOG"' EXIT SIGINT SIGTERM
    log "INFO" "Usando archivo temporal para salida de pip: $TEMP_PIP_LOG"

    mostrar_info "Actualizando pip en ${COLOR_CYAN}${venv_path}${COLOR_RESET}..."
    echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Actualizando pip... "
    if ("$venv_path/bin/pip" install --upgrade pip >> "$TEMP_PIP_LOG" 2>&1); then
        echo -e "${COLOR_GREEN}✓${COLOR_RESET}"
        log "INFO" "pip actualizado correctamente en $venv_path."
    else
        echo -e "${COLOR_RED}✗${COLOR_RESET}"
        mostrar_advertencia "Fallo al actualizar pip. Ver $TEMP_PIP_LOG. Intentando continuar..."
        log "WARN" "Fallo al actualizar pip en $venv_path. Salida en $TEMP_PIP_LOG."
        # No salimos necesariamente, pip podría funcionar igual
    fi

    # 3. Determinar Comando Pip (Paquete o Reqs)
    local pip_install_cmd=""
    local install_target_display="" # Para mensajes

    if [[ -f "$package_or_reqs_file" ]]; then
        # Es un archivo de requisitos
        install_target_display="archivo de requisitos ${COLOR_CYAN}$package_or_reqs_file${COLOR_RESET}"
        pip_install_cmd="$venv_path/bin/pip install -r \"$package_or_reqs_file\""
        log "INFO" "Detectado archivo de requisitos: $package_or_reqs_file"
    else
        # Asumir que es un nombre de paquete
        install_target_display="paquete ${COLOR_CYAN}$package_or_reqs_file${COLOR_RESET}"
        # Podríamos añadir validación básica del nombre del paquete si quisiéramos
        pip_install_cmd="$venv_path/bin/pip install \"$package_or_reqs_file\""
        log "INFO" "Detectado nombre de paquete: $package_or_reqs_file"
    fi

    # 4. Ejecutar Instalación con Captura de Salida
    mostrar_info "Instalando $install_target_display en ${COLOR_CYAN}${venv_path}${COLOR_RESET} (salida capturada)..."
    log "INFO" "Ejecutando: $pip_install_cmd > $TEMP_PIP_LOG 2>&1"

    # Ejecutar pip install capturando toda la salida
    eval "$pip_install_cmd" > "$TEMP_PIP_LOG" 2>&1
    local pip_ret=$?
    # Copiar salida temporal al log principal también
    cat "$TEMP_PIP_LOG" >> "$LOG_FILE"

    if [ $pip_ret -eq 0 ]; then
        # --- Parse Output on Success (Similar a install_default_env) ---
        local satisfied_count=$(grep -c 'Requirement already satisfied' "$TEMP_PIP_LOG")
        local installed_list=$(grep '^Successfully installed ' "$TEMP_PIP_LOG" | sed 's/^Successfully installed //')
        local installed_count=0; [[ -n "$installed_list" ]] && installed_count=$(echo "$installed_list" | wc -w)
        local ignored_list=$(grep '^Ignoring .* markers' "$TEMP_PIP_LOG" | sed -E 's/^Ignoring ([^:]+):.*/\1/')
        local ignored_count=0; [[ -n "$ignored_list" ]] && ignored_count=$(echo "$ignored_list" | wc -l)

        mostrar_exito "Instalación/actualización desde $install_target_display completada."
        echo -e "${COLOR_BLUE}Resumen:${COLOR_RESET}"
        echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Paquetes ya satisfechos: $satisfied_count"
        if [ "$installed_count" -gt 0 ]; then
             echo -e "  ${COLOR_YELLOW}↑${COLOR_RESET} Paquetes instalados/actualizados ($installed_count):"
             echo "$installed_list" | fold -s -w 70 | sed 's/^/    /'
        fi
        if [ "$ignored_count" -gt 0 ]; then
             echo -e "  ${COLOR_CYAN}- ${COLOR_RESET} Paquetes ignorados (marcador) ($ignored_count):"
             echo "$ignored_list" | sed 's/^/    /'
        fi
        log "INFO" "pip install exitoso para $install_target_display. Satisfechos: $satisfied_count, Instalados/Actualizados: $installed_count, Ignorados: $ignored_count"
    else
        # --- Show Error Details on Failure ---
        mostrar_error "Hubo un error (código $pip_ret) durante la instalación de $install_target_display."
        mostrar_info "Mostrando las últimas 10 líneas de la salida de pip:"
        echo "-------------------- Inicio Salida Pip (Error) --------------------"
        tail -n 10 "$TEMP_PIP_LOG" | sed 's/^/  /' # Indentar salida
        echo "-------------------- Fin Salida Pip (Error) ---------------------"
        mostrar_info "Consulte el archivo completo ${COLOR_YELLOW}$TEMP_PIP_LOG${COLOR_RESET} y ${COLOR_YELLOW}$LOG_FILE${COLOR_RESET} para más detalles."
        # Salir con error si pip falló
        rm -f "$TEMP_PIP_LOG" # Limpiar aunque falle
        trap - EXIT SIGINT SIGTERM
        exit 1
    fi

    log "INFO" "Comando --package-global completado para '$package_or_reqs_file'."
    rm -f "$TEMP_PIP_LOG" # Limpieza explícita si todo va bien
    trap - EXIT SIGINT SIGTERM # Limpiar trap si salimos normalmente
}

# --- Nueva Función para --package-local ---
# Instala un paquete o requirements.txt en un entorno LOCAL existente
install_local_package() {
    local env_name="default"
    local source_arg=""
    local package_or_reqs_file=""
    local target_local_venv_path=""

    # Parseo de argumentos: [<entorno>] [<paquete|reqs.txt>]
    # Si $1 existe Y es un directorio en ./.venv, es el nombre del entorno.
    # Si no, $1 es la fuente. Si hay $2, es la fuente.
    if [[ -n "$1" ]]; then
        if [[ -d "$PWD/.venv/$1" ]]; then
            env_name="$1"
            log "DEBUG" "Argumento 1 detectado como nombre de entorno local: $env_name"
            if [[ -n "$2" ]]; then
                source_arg="$2"
                log "DEBUG" "Argumento 2 detectado como fuente: $source_arg"
            fi
        else
            source_arg="$1"
            log "DEBUG" "Argumento 1 detectado como fuente: $source_arg"
            # $env_name sigue siendo "default"
        fi
    fi
    # Si no se especificó fuente, usar requirements.txt local
    if [[ -z "$source_arg" ]]; then
        package_or_reqs_file="$PWD/requirements.txt"
        log "DEBUG" "No se especificó fuente, usando por defecto: $package_or_reqs_file"
    else
        package_or_reqs_file="$source_arg"
        log "DEBUG" "Fuente especificada: $package_or_reqs_file"
    fi

    target_local_venv_path="$PWD/.venv/$env_name"

    mostrar_info "============================================================="
    mostrar_info " Instalando Paquete/Reqs en Entorno LOCAL (${target_local_venv_path}) "
    mostrar_info "============================================================="
    log "INFO" "Iniciando --package-local para '$package_or_reqs_file' en $target_local_venv_path"

    # 1. Verificar Entorno Local (DEBE EXISTIR)
    if ! verificar_entorno_python "$target_local_venv_path"; then
        mostrar_error "El entorno local especificado ${COLOR_RED}${target_local_venv_path}${COLOR_RESET} no existe o no es válido."
        mostrar_info "El comando ${BOLD}--package-local${COLOR_RESET} requiere que el entorno local exista previamente."
        mostrar_info "Puedes crearlo con: ${BOLD}pymanager.sh --create $env_name${COLOR_RESET}"
        log "ERROR" "--package-local abortado: entorno local no válido/no existe: $target_local_venv_path"
        exit 1
    else
        local py_version
        py_version=$(obtener_version_python_entorno "$target_local_venv_path")
        mostrar_info "Entorno local encontrado (${COLOR_CYAN}$env_name${COLOR_RESET}). Python: ${COLOR_YELLOW}${py_version:-N/A}${COLOR_RESET}"
        log "INFO" "Entorno local $target_local_venv_path existe. Python: ${py_version:-N/A}"
    fi

    # 2. Verificar Fuente (si es un archivo)
    # Asumimos que es un archivo si contiene / o .txt, o si -f lo confirma
    local is_file=false
    if [[ -f "$package_or_reqs_file" ]]; then
        is_file=true
    elif [[ "$package_or_reqs_file" == */* ]] || [[ "$package_or_reqs_file" == *.txt ]]; then
         # Parece una ruta, verificar si existe
         if [[ ! -f "$package_or_reqs_file" ]]; then
             mostrar_error "El archivo de requisitos especificado ${COLOR_RED}$package_or_reqs_file${COLOR_RESET} no se encontró."
             log "ERROR" "--package-local abortado: archivo de requisitos no encontrado: $package_or_reqs_file"
             exit 1
         fi
         is_file=true
    fi
    # Si es el requirements.txt por defecto, también verificamos
    if [[ "$package_or_reqs_file" == "$PWD/requirements.txt" && ! -f "$package_or_reqs_file" ]]; then
        mostrar_error "No se encontró el archivo ${COLOR_RED}requirements.txt${COLOR_RESET} en el directorio actual ($PWD)."
        log "ERROR" "--package-local abortado: requirements.txt por defecto no encontrado en $PWD."
        exit 1
    fi

    # 3. Verificar Conexión y Actualizar Pip
    if ! verificar_conexion_internet; then
        mostrar_advertencia "Sin conexión a internet. No se puede instalar/actualizar."
        log "WARN" "Sin conexión internet, abortando --package-local."
        exit 1
    fi

    local TEMP_PIP_LOG="/tmp/pymanager_pip_output.$$.log"
    trap 'rm -f "$TEMP_PIP_LOG"' EXIT SIGINT SIGTERM
    log "INFO" "Usando archivo temporal para salida de pip: $TEMP_PIP_LOG"

    mostrar_info "Actualizando pip en ${COLOR_CYAN}${target_local_venv_path}${COLOR_RESET}..."
    echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Actualizando pip... "
    if ("$target_local_venv_path/bin/pip" install --upgrade pip >> "$TEMP_PIP_LOG" 2>&1); then
        echo -e "${COLOR_GREEN}✓${COLOR_RESET}"
        log "INFO" "pip actualizado correctamente en $target_local_venv_path."
    else
        echo -e "${COLOR_RED}✗${COLOR_RESET}"
        mostrar_advertencia "Fallo al actualizar pip. Ver $TEMP_PIP_LOG. Intentando continuar..."
        log "WARN" "Fallo al actualizar pip en $target_local_venv_path. Salida en $TEMP_PIP_LOG."
    fi

    # 4. Determinar Comando Pip y Ejecutar
    local pip_install_cmd=""
    local install_target_display=""

    if $is_file; then
        install_target_display="archivo de requisitos ${COLOR_CYAN}$package_or_reqs_file${COLOR_RESET}"
        pip_install_cmd="\"$target_local_venv_path/bin/pip\" install -r \"$package_or_reqs_file\""
    else
        install_target_display="paquete ${COLOR_CYAN}$package_or_reqs_file${COLOR_RESET}"
        pip_install_cmd="\"$target_local_venv_path/bin/pip\" install \"$package_or_reqs_file\""
    fi

    mostrar_info "Instalando $install_target_display en ${COLOR_CYAN}${target_local_venv_path}${COLOR_RESET} (salida capturada)..."
    log "INFO" "Ejecutando: $pip_install_cmd > $TEMP_PIP_LOG 2>&1"

    eval "$pip_install_cmd" > "$TEMP_PIP_LOG" 2>&1
    local pip_ret=$?
    cat "$TEMP_PIP_LOG" >> "$LOG_FILE"

    if [ $pip_ret -eq 0 ]; then
        # Parse Output (copiado/adaptado de install_global_package)
        local satisfied_count=$(grep -c 'Requirement already satisfied' "$TEMP_PIP_LOG")
        local installed_list=$(grep '^Successfully installed ' "$TEMP_PIP_LOG" | sed 's/^Successfully installed //')
        local installed_count=0; [[ -n "$installed_list" ]] && installed_count=$(echo "$installed_list" | wc -w)
        local ignored_list=$(grep '^Ignoring .* markers' "$TEMP_PIP_LOG" | sed -E 's/^Ignoring ([^:]+):.*/\1/')
        local ignored_count=0; [[ -n "$ignored_list" ]] && ignored_count=$(echo "$ignored_list" | wc -l)

        mostrar_exito "Instalación/actualización desde $install_target_display completada en ${COLOR_CYAN}$env_name${COLOR_RESET}."
        echo -e "${COLOR_BLUE}Resumen:${COLOR_RESET}"
        echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Paquetes ya satisfechos: $satisfied_count"
        if [ "$installed_count" -gt 0 ]; then
             echo -e "  ${COLOR_YELLOW}↑${COLOR_RESET} Paquetes instalados/actualizados ($installed_count):"
             echo "$installed_list" | fold -s -w 70 | sed 's/^/    /'
        fi
        if [ "$ignored_count" -gt 0 ]; then
             echo -e "  ${COLOR_CYAN}- ${COLOR_RESET} Paquetes ignorados (marcador) ($ignored_count):"
             echo "$ignored_list" | sed 's/^/    /'
        fi
        log "INFO" "pip install exitoso para $install_target_display en $target_local_venv_path. Satisfechos: $satisfied_count, Instalados/Actualizados: $installed_count, Ignorados: $ignored_count"
    else
        mostrar_error "Hubo un error (código $pip_ret) durante la instalación de $install_target_display en ${COLOR_RED}$env_name${COLOR_RESET}."
        mostrar_info "Mostrando las últimas 10 líneas de la salida de pip:"
        echo "-------------------- Inicio Salida Pip (Error) --------------------"
        tail -n 10 "$TEMP_PIP_LOG" | sed 's/^/  /'
        echo "-------------------- Fin Salida Pip (Error) ---------------------"
        mostrar_info "Consulte el archivo completo ${COLOR_YELLOW}$TEMP_PIP_LOG${COLOR_RESET} y ${COLOR_YELLOW}$LOG_FILE${COLOR_RESET} para más detalles."
        rm -f "$TEMP_PIP_LOG"
        trap - EXIT SIGINT SIGTERM
        exit 1
    fi

    log "INFO" "Comando --package-local completado para '$package_or_reqs_file' en $target_local_venv_path."
    rm -f "$TEMP_PIP_LOG"
    trap - EXIT SIGINT SIGTERM
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
    echo -e "${UNDERLINE}Uso:${COLOR_RESET} ${BOLD}pymanager.sh <comando> [argumentos...]${COLOR_RESET}"
    echo
    echo -e "${UNDERLINE}Comandos:${COLOR_RESET}"
    echo -e "  ${BOLD}--create [<nombre_env>] [--python <ver>]${COLOR_RESET} Crea un entorno virtual LOCAL (${BOLD}./.venv/<nombre_env>${COLOR_RESET})."
    echo -e "                     - Predeterminado: ${BOLD}./.venv/default${COLOR_RESET} con última versión Python."
    echo -e "                     (No instala paquetes)."
    echo -e "  ${BOLD}--activate${COLOR_RESET}       Muestra comando para activar entorno global ${BOLD}~/.venv/default${COLOR_RESET}."
    echo -e "  ${BOLD}--package-global <paquete|reqs.txt>${COLOR_RESET} Instala paquete/requisitos en el entorno GLOBAL"
    echo -e "                     (${BOLD}~/.venv/default${COLOR_RESET}), creándolo si es necesario."
    echo -e "  ${BOLD}--package-local [<entorno>] [<paquete|reqs.txt>]${COLOR_RESET} Instala paquete/requisitos en un"
    echo -e "                     entorno LOCAL ${BOLD}EXISTENTE${COLOR_RESET} (${BOLD}./.venv/<entorno>${COLOR_RESET})."
    echo -e "                     - Si <entorno> se omite: usa ${BOLD}default${COLOR_RESET} (${BOLD}./.venv/default${COLOR_RESET})."
    echo -e "                     - Si <paquete|reqs.txt> se omite: usa ${BOLD}./requirements.txt${COLOR_RESET}."
    echo -e "                     (¡El entorno local DEBE existir! Usa --create primero si no)."
    echo -e "  ${BOLD}--list${COLOR_RESET}           Lista paquetes y versión de Python del entorno seleccionado."
    echo -e "                     (Menú interactivo si hay múltiples entornos locales/global)."
    echo -e "  ${BOLD}--remove-global${COLOR_RESET}  Elimina el entorno virtual global (${BOLD}~/.venv/default${COLOR_RESET})."
    echo -e "                     (Pide confirmación)."
    echo -e "  ${BOLD}--remove-local${COLOR_RESET}   Elimina entornos locales (${BOLD}./.venv/*${COLOR_RESET}) interactivamente."
    echo -e "                     (Lista entornos, permite seleccionar uno/varios/todos)."
    echo -e "                     (Pide confirmación)."
    echo -e "  ${BOLD}--help${COLOR_RESET}, ${BOLD}-h${COLOR_RESET}       Muestra esta ayuda."
    echo -e "  ${BOLD}--version${COLOR_RESET}      Muestra la versión del script."
    echo
    echo -e "${UNDERLINE}Notas:${COLOR_RESET}"
    echo -e "* ${BOLD}--create${COLOR_RESET} es para crear entornos locales (${BOLD}./.venv/${COLOR_RESET})."
    echo -e "* ${BOLD}--package-global${COLOR_RESET} es para instalar en el global (${BOLD}~/.venv/default${COLOR_RESET})."
    echo -e "* ${BOLD}--package-local${COLOR_RESET} es para instalar en locales ${BOLD}existentes${COLOR_RESET} (${BOLD}./.venv/...${COLOR_RESET})."
    echo -e "* Los logs se guardan en ${BOLD}$LOG_FILE${COLOR_RESET}."
}

# --- Nuevas Funciones para Eliminar Entornos ---

# Elimina el entorno virtual global default (~/.venv/default)
remove_global_env() {
    local target_path="$BIN_VENV_DIR"
    log "INFO" "Iniciando --remove-global para $target_path"

    if [[ ! -d "$target_path" ]]; then
        mostrar_info "El entorno virtual global (${COLOR_CYAN}$target_path${COLOR_RESET}) no existe."
        log "INFO" "El entorno global $target_path no existe, nada que hacer."
        exit 0
    fi

    mostrar_advertencia "Está a punto de eliminar permanentemente el entorno global:"
    echo -e "  ${COLOR_YELLOW}$target_path${COLOR_RESET}"

    local confirm_msg="¿Realmente desea eliminar este entorno global?"
    local confirmed=false
    if [[ "$HAS_GUM" == "true" ]] && command -v gum &> /dev/null; then
        if gum confirm "$confirm_msg"; then confirmed=true; fi
    else
        local response
        read -p "$confirm_msg (s/N): " response
        if [[ "$response" =~ ^[Ss]$ ]]; then confirmed=true; fi
    fi

    if ! $confirmed; then
        mostrar_info "Operación cancelada."
        log "INFO" "Eliminación de $target_path cancelada por el usuario."
        exit 0
    fi

    mostrar_info "Eliminando entorno global ${COLOR_CYAN}$target_path${COLOR_RESET}..."
    echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Eliminando $target_path... "
    if rm -rf "$target_path"; then
        echo -e "${COLOR_GREEN}✓${COLOR_RESET}"
        mostrar_exito "Entorno global ${COLOR_GREEN}$target_path${COLOR_RESET} eliminado."
        log "INFO" "Entorno global $target_path eliminado exitosamente."
    else
        echo -e "${COLOR_RED}✗${COLOR_RESET}"
        mostrar_error "No se pudo eliminar el entorno global ${COLOR_RED}$target_path${COLOR_RESET}."
        log "ERROR" "Fallo al eliminar $target_path."
        exit 1
    fi
}

# Elimina uno o más entornos virtuales locales (./.venv/*) interactivamente
remove_local_env() {
    local local_venv_base_dir="$PWD/.venv"
    log "INFO" "Iniciando --remove-local en $local_venv_base_dir"

    if [[ ! -d "$local_venv_base_dir" ]]; then
        mostrar_info "No existe el directorio de entornos locales (${COLOR_CYAN}$local_venv_base_dir${COLOR_RESET})."
        log "INFO" "Directorio $local_venv_base_dir no encontrado, nada que eliminar."
        exit 0
    fi

    local env_names=()
    local env_paths=()
    local options=()
    local found_envs=false

    mostrar_info "Buscando entornos locales en ${COLOR_CYAN}$local_venv_base_dir${COLOR_RESET}..."
    while IFS= read -r -d $'\0' potential_env_path; do
        local env_name
        env_name=$(basename "$potential_env_path")
        # Verificar si es realmente un entorno (opcional, podría eliminar cualquier dir)
        # if verificar_entorno_python "$potential_env_path"; then
            env_names+=("$env_name")
            env_paths+=("$potential_env_path")
            options+=("$env_name") # Añadir solo el nombre a las opciones del menú
            log "INFO" "Entorno local encontrado: $env_name en $potential_env_path"
            found_envs=true
        # fi
    done < <(find "$local_venv_base_dir" -maxdepth 1 -mindepth 1 -type d -print0)

    if ! $found_envs; then
        mostrar_info "No se encontraron entornos locales en ${COLOR_CYAN}$local_venv_base_dir${COLOR_RESET}."
        log "INFO" "No se encontraron subdirectorios en $local_venv_base_dir."
        exit 0
    fi

    # Añadir opciones especiales al menú
    local all_option="[ Eliminar TODOS los listados (${#env_names[@]}) ]"
    local cancel_option="[ Cancelar ]"
    options+=("$all_option" "$cancel_option")

    local selection=() # Array para guardar selecciones
    local choice_str="" # String para selección única de 'select'

    mostrar_info "Seleccione los entornos locales a eliminar:"
    if [[ "$HAS_GUM" == "true" ]] && command -v gum &> /dev/null; then
        # Usar gum choose con selección múltiple
        # Necesitamos pasar las opciones como argumentos separados a gum choose
        local gum_output
        mapfile -t gum_output < <(printf "%s\n" "${options[@]}" | gum choose --no-limit --header="Selecciona entornos (Espacio para marcar, Enter para confirmar)")
        local exit_code=$?
        if [[ $exit_code -ne 0 ]]; then # Gum cancelado (ej: Ctrl+C)
             mostrar_info "Operación cancelada."
             log "INFO" "Selección cancelada en gum choose."
             exit 0
        fi
        # Copiar salida de gum al array selection
         for item in "${gum_output[@]}"; do
             selection+=("$item")
         done
         log "DEBUG" "Selección de gum: ${selection[*]}"
    else
        # Fallback a select de Bash (selección única + TODOS)
        mostrar_advertencia "(Usando menú básico. Instala 'gum' para seleccionar múltiples entornos individualmente)."
        PS3="Selecciona el número del entorno a eliminar (o opción especial, q para salir): "
        select opt in "${options[@]}"; do
            if [[ "$REPLY" == "q" ]]; then
                choice_str="$cancel_option" # Tratar 'q' como cancelar
                break
            elif [[ -n "$opt" ]]; then
                choice_str="$opt"
                break
            else
                echo "Selección inválida. Intenta de nuevo."
            fi
        done
         # Añadir la selección única al array selection (si no es cancelar)
         if [[ "$choice_str" != "$cancel_option" ]]; then
             selection+=("$choice_str")
         fi
         log "DEBUG" "Selección de select: $choice_str"
    fi

    # Procesar selección
    local paths_to_delete=()
    local delete_all=false
    local user_cancelled=false

    if [[ ${#selection[@]} -eq 0 ]]; then # Si gum no devuelve nada o select eligió Cancelar
         user_cancelled=true
    else
         for sel in "${selection[@]}"; do
             if [[ "$sel" == "$cancel_option" ]]; then
                 user_cancelled=true
                 break # Salir del bucle si se encuentra Cancelar
             elif [[ "$sel" == "$all_option" ]]; then
                 delete_all=true
                 # Si se elige TODOS, ignorar otras selecciones individuales
                 paths_to_delete=("${env_paths[@]}") # Marcar todos para borrar
                 log "INFO" "Seleccionado eliminar TODOS los entornos locales."
                 break # Salir del bucle, ya tenemos la acción
             elif [[ "$choice_str" != "" ]]; then # Si usamos select, solo procesar esa opción
                 # Encontrar la ruta correspondiente al nombre seleccionado
                 for i in "${!env_names[@]}"; do
                     if [[ "${env_names[$i]}" == "$sel" ]]; then
                         paths_to_delete+=("${env_paths[$i]}")
                         log "INFO" "Entorno local seleccionado para eliminar: ${env_names[$i]}"
                         break # Encontrado, salir del bucle interno
                     fi
                 done
             fi
         done
    fi

    if $user_cancelled; then
        mostrar_info "Operación cancelada."
        log "INFO" "Eliminación local cancelada por el usuario."
        exit 0
    fi

    if [[ ${#paths_to_delete[@]} -eq 0 ]]; then
        mostrar_info "No se seleccionó ningún entorno para eliminar."
        log "INFO" "No se seleccionaron entornos válidos."
        exit 0
    fi

    # Confirmación final
    local confirm_msg_final=""
    if $delete_all; then
        confirm_msg_final="¿Realmente desea eliminar TODOS (${#paths_to_delete[@]}) los entornos locales listados?"
    else
         local names_to_delete_str=$(printf "'%s', " "${paths_to_delete[@]}" | sed 's|.*/||; s/, $//') # Extraer nombres de rutas
         confirm_msg_final="¿Realmente desea eliminar los siguientes entornos locales (${#paths_to_delete[@]}): $names_to_delete_str?"
    fi

    local confirmed_final=false
    if [[ "$HAS_GUM" == "true" ]] && command -v gum &> /dev/null; then
        if gum confirm "$confirm_msg_final"; then confirmed_final=true; fi
    else
        local response_final
        read -p "$confirm_msg_final (s/N): " response_final
        if [[ "$response_final" =~ ^[Ss]$ ]]; then confirmed_final=true; fi
    fi

    if ! $confirmed_final; then
        mostrar_info "Operación cancelada."
        log "INFO" "Eliminación final cancelada por el usuario."
        exit 0
    fi

    # Proceder con la eliminación
    local errors_occurred=false
    mostrar_info "Eliminando entornos locales seleccionados..."
    for path_del in "${paths_to_delete[@]}"; do
        local env_name_del
        env_name_del=$(basename "$path_del")
        echo -ne "${COLOR_YELLOW}▶${COLOR_RESET} Eliminando ${COLOR_CYAN}$env_name_del${COLOR_RESET} ($path_del)... "
        if rm -rf "$path_del"; then
            echo -e "${COLOR_GREEN}✓${COLOR_RESET}"
            log "INFO" "Entorno local eliminado: $path_del"
        else
            echo -e "${COLOR_RED}✗${COLOR_RESET}"
            mostrar_error "No se pudo eliminar ${COLOR_RED}$path_del${COLOR_RESET}."
            log "ERROR" "Fallo al eliminar $path_del."
            errors_occurred=true
        fi
    done

    if $errors_occurred; then
        mostrar_advertencia "Ocurrieron errores durante la eliminación. Revisa los mensajes anteriores."
        exit 1
    else
        mostrar_exito "Entornos locales seleccionados eliminados correctamente."
    fi
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
        # Antes de mostrar ayuda, verificar si es un nombre de entorno conocido
        # (Lógica futura para activar por nombre?)
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
            # activate_venv # Aún falta definir esta función
            mostrar_info "Para activar el entorno global default, ejecuta:"
            echo -e "  ${BOLD}source \"$BIN_VENV_DIR/bin/activate\"${COLOR_RESET}"
            log "INFO" "Mostrado comando de activación para $BIN_VENV_DIR"
            ;;
        --package-global)
             if [[ -z "$1" ]]; then
                 mostrar_error "El comando --package-global requiere un argumento (nombre de paquete o ruta a requirements.txt)."
                 show_help
                 exit 1
             fi
             install_global_package "$1"
             shift # Consumir el argumento del paquete/archivo
             ;;
        --package-local)
            # Pasar todos los argumentos restantes a la función, ella se encarga del parseo
            install_local_package "$@"
            ;;
        --list)
            list_packages "$@"
            ;;
        --remove-global)
            remove_global_env
            ;;
        --remove-local)
            remove_local_env # No necesita argumentos
            ;;
        --help|-h)
            show_help
            ;;
        --version)
            echo "${APP_NAME} v${VERSION}"
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