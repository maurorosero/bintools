#!/bin/bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-04-30 05:52:19
# Version: 0.1.0
#
# pymanager.sh - Script de Bash para administrar entornos virtuales de Python (crear, listar, instalar paquetes, activar/desactivar, eliminar).
# -----------------------------------------------------------------------------
#

# py_manager.sh - Administrador de Entornos Virtuales de Python
#
# Este script permite administrar entornos virtuales de Python de manera sencilla.
# Funcionalidades:
#  - Crear entornos virtuales
#  - Instalar paquetes desde archivos de requisitos
#  - Listar entornos disponibles
#  - Activar/desactivar entornos mediante alias (pybin/pyunbin)
#  - Eliminar entornos virtuales

# --- Banner --- #
APP_NAME="Python Virtual Environment Manager"
APP_VERSION="0.5.5 (2025/05)"
APP_AUTHOR="Mauro Rosero Pérez (mauro.rosero@gmail.com)"

# Constantes
BIN_DIR="$HOME/bin"
VENV_DIR="$HOME/.venv"
BIN_VENV_DIR="$VENV_DIR/default" # Ruta estándar para el venv predeterminado
DEFAULT_ENV_REQUIREMENTS_PATH="$BIN_DIR/requirements.txt" # Ruta del archivo de requisitos para el venv predeterminado
TIMEOUT_SECONDS=5

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# --- Configuración de Logs --- #
# Ruta de logs siempre en el home del usuario actual
LOG_DIR="$HOME/bin/logs"
mkdir -p "$LOG_DIR" 2>/dev/null || true
LOG_FILE="$LOG_DIR/pymanager.log"

# Guardar argumentos originales para el log
ORIGINAL_ARGS=("$@")

# Función para registrar en el log
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Función para mostrar mensajes de error
mostrar_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR" "$1"
}

# Función para mostrar mensajes de éxito
mostrar_exito() {
    echo -e "${GREEN}$1${NC}"
    log "INFO" "$1"
}

# Función para mostrar advertencias
mostrar_advertencia() {
    echo -e "${YELLOW}ADVERTENCIA: $1${NC}"
    log "WARN" "$1"
}

# Función para mostrar información
mostrar_info() {
    echo -e "${CYAN}$1${NC}"
    log "INFO" "$1"
}

# Función para mostrar debug
mostrar_debug() {
    if [[ "${DEBUG:-0}" -eq 1 ]]; then
        echo -e "${MAGENTA}DEBUG: $1${NC}"
    fi
    log "DEBUG" "$1"
}

# Función para verificar la conexión a internet
verificar_conexion_internet() {
    mostrar_debug "Verificando conexión a internet..."
    # Intentar hacer ping a Google DNS con timeout
    if ping -c 1 -W "$TIMEOUT_SECONDS" 8.8.8.8 &> /dev/null; then
        mostrar_debug "Conexión a internet verificada correctamente"
        return 0 # Hay conexión
    else
        mostrar_error "No hay conexión a internet. No se puede continuar con la operación."
        return 1 # No hay conexión
    fi
}

# Función para verificar si las dependencias requeridas están instaladas
check_prerequisites() {
    local errores=0
    mostrar_debug "Verificando prerrequisitos..."

    if ! command -v python3 &> /dev/null; then
        mostrar_error "python3 no está instalado. Por favor, instálelo primero."
        errores=1
    else
        # Verificar la versión de Python
        local python_version=$(python3 --version | cut -d' ' -f2)
        mostrar_exito "Python versión $python_version encontrada."
    fi
    
    if ! command -v pip &> /dev/null; then
        mostrar_error "pip no está instalado. Por favor, instálelo primero."
        errores=1
    else
        # Verificar la versión de pip
        local pip_version=$(pip --version | awk '{print $2}')
        mostrar_exito "Pip versión $pip_version encontrado."
    fi

    if ! command -v venv &> /dev/null && ! python3 -c "import venv" &> /dev/null; then
        mostrar_advertencia "El módulo venv parece no estar disponible. Intente instalar python3-venv."
        errores=1
    fi

    # Si hay errores, salir
    if [ $errores -ne 0 ]; then
        log "ERROR" "Verificación de prerrequisitos fallida"
        exit 1
    fi
    
    mostrar_debug "Verificación de prerrequisitos completada con éxito"
}

# Función para asegurar que el directorio de entornos virtuales existe
ensure_venv_dir() {
    mostrar_debug "Verificando si existe el directorio de entornos virtuales: $VENV_DIR"
    if [ ! -d "$VENV_DIR" ]; then
        mkdir -p "$VENV_DIR" || {
            mostrar_error "No se pudo crear el directorio $VENV_DIR"
            exit 1
        }
        mostrar_exito "Directorio creado: $VENV_DIR"
    fi
}

# Función para crear un nuevo entorno virtual
create_venv() {
    local env_name="$1"
    local req_file="$2"
    
    if [ -z "$env_name" ]; then
        mostrar_error "Se requiere un nombre para el entorno."
        echo "Uso: $0 create <nombre_entorno> [archivo_requisitos]"
        exit 1
    fi
    
    local env_path="$VENV_DIR/$env_name"
    log "INFO" "Intentando crear entorno virtual: $env_name en $env_path"
    
    # Verificar si el entorno ya existe
    local entorno_existente=false
    if [ -d "$env_path" ]; then
        entorno_existente=true
        mostrar_info "El entorno '$env_name' ya existe en $env_path"
        mostrar_info "Verificando paquetes instalados..."
        log "INFO" "Entorno '$env_name' ya existe, continuando con actualización de paquetes"
    else
        # Crear el entorno virtual si no existe
        mostrar_info "Creando entorno virtual: $env_name"
        python3 -m venv "$env_path" || {
            mostrar_error "Falló la creación del entorno virtual."
            exit 1
        }
        
        mostrar_exito "Entorno virtual creado exitosamente en: $env_path"
    fi
    
    # Si no se proporciona archivo de requisitos, terminar
    if [ -z "$req_file" ]; then
        if [ "$entorno_existente" = true ]; then
            echo "Para instalar paquetes adicionales, proporcione un archivo de requisitos."
        else
            echo "Ejecute el siguiente comando para activar el entorno:"
            mostrar_exito "source $env_path/bin/activate"
        fi
        exit 0
    fi
    
    # Verificar conexión a internet antes de instalar paquetes
    if ! verificar_conexion_internet; then
        mostrar_advertencia "No se instalarán paquetes debido a la falta de conexión a internet."
        echo "Puede instalar los paquetes más tarde cuando tenga conexión."
        echo "Ejecute el siguiente comando para activar el entorno:"
        echo "source $env_path/bin/activate"
        exit 0
    fi
    
    # Instalar paquetes según el archivo de requisitos
    install_packages "$env_name" "$req_file"
    
    echo "Ejecute el siguiente comando para activar el entorno:"
    mostrar_exito "source $env_path/bin/activate"
}

# Función para verificar el estado de un paquete
check_package_status() {
    local pkg_line="$1" # Renombrar para claridad
    local env_path="$2"
    local activate_cmd="source $env_path/bin/activate"

    # Eliminar comentarios y espacios en blanco al final
    local pkg=${pkg_line%%#*} # Elimina todo desde # hasta el final
    pkg=$(echo "$pkg" | xargs) # Elimina espacios en blanco iniciales/finales

    # Si la línea está vacía después de quitar comentarios/espacios, no hacer nada
    if [[ -z "$pkg" ]]; then
        echo "empty_line" # Devolver un estado especial o simplemente retornar
        return
    fi

    # Extraer nombre base del paquete
    local pkg_name=$(echo "$pkg" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr -d ' ')

    # Verificar si se ha especificado alguna versión
    local version_constraint=""
    if [[ "$pkg" == *"="* || "$pkg" == *">"* || "$pkg" == *"<"* || "$pkg" == *"~"* ]]; then
        version_constraint=$(echo "$pkg" | grep -o '[=<>~][=<>~0-9.]*')
    fi
    
    # Verificar si el paquete está instalado
    # Usar subshell para que 'activate' no afecte al script principal
    if ( eval "$activate_cmd" >/dev/null 2>&1 && pip list | grep -i "^$pkg_name " > /dev/null 2>&1 ); then
        # Obtener la versión instalada
        local installed_version=$( (eval "$activate_cmd" >/dev/null 2>&1 && pip list | grep -i "^$pkg_name " | awk '{print $2}') )
        
        # Si hay una restricción de versión, verificar si necesita actualizarse
        if [[ -n "$version_constraint" ]]; then
            # Verificar si está desactualizado
             if ( eval "$activate_cmd" >/dev/null 2>&1 && pip list --outdated | grep -i "^$pkg_name " > /dev/null 2>&1 ); then
                echo "installed_update" # Instalado pero requiere actualización
                return
            fi
        fi
        echo "installed" # Ya instalado
    else
        echo "not_installed" # No instalado
    fi
}

# Función para mostrar lista de paquetes formateada en dos columnas
display_packages_status() {
    local req_file="$1"
    local env_path="$2"
    local env_display_name="$3" # Nombre para mostrar (ej: "local", "mi_entorno")
    local max_pkg_len=25
    local total_pkgs=0
    local installed_count=0
    local update_count=0
    local pending_count=0
    local error_count=0 # Contador para errores de check_package_status

    declare -A pkg_status
    declare -A pkg_name_map # Para manejar nombres originales vs base

    mostrar_info "Verificando estado de paquetes para entorno '$env_display_name' ($env_path)..."

    # Primer bucle: Verificar estado y contar
    while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        ((total_pkgs++))
        local pkg_name_base=$(echo "$pkg" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr -d ' ')
        pkg_name_map["$pkg_name_base"]="$pkg" # Guardar especificación original

        local status
        status=$(check_package_status "$pkg_line" "$env_path")
        local check_ret=$?

        if [ $check_ret -ne 0 ] || [[ "$status" == "invalid_env_path" ]]; then
            # Si check_package_status falla (ej: entorno inválido), marcar como error y no contar más
            mostrar_error "No se pudo verificar el estado de los paquetes (entorno '$env_display_name' inválido?)."
            log "ERROR" "check_package_status falló para $pkg_line en $env_path"
            error_count=$((total_pkgs))
            break # Salir del bucle si hay error grave
        fi
        pkg_status["$pkg_name_base"]="$status"

        case "$status" in
            installed) ((installed_count++)) ;; 
            installed_update) ((update_count++)) ;; 
            not_installed) ((pending_count++)) ;; 
            empty_line) ((total_pkgs--)) ;; # No contar líneas vacías
            *) 
                mostrar_advertencia "Estado desconocido '$status' para $pkg_name_base"
                ((error_count++))
                ;;
        esac
    done < "$req_file"

    # Si hubo un error grave al inicio, no mostrar resumen detallado
    if [ $error_count -gt 0 ] && [ $error_count -eq $total_pkgs ]; then
        return 1 # Indicar fallo
    fi

    # Mostrar encabezado con resumen
    echo -e "\n${WHITE}Estado de paquetes ($total_pkgs total) para '$env_display_name':${NC}"
    echo -e " • ${GREEN}Ya instalados:${NC} $installed_count"
    echo -e " • ${YELLOW}Requieren actualización:${NC} $update_count"
    echo -e " • ${CYAN}Pendientes de instalar:${NC} $pending_count"
    if [ $error_count -gt 0 ]; then
        echo -e " • ${RED}Errores/Desconocidos:${NC} $error_count"
    fi
    echo

    # Segundo bucle: Mostrar listado
    local count=0
    local col_width=$((max_pkg_len + 5))
    echo -e "${WHITE}Listado de paquetes:${NC}"
    # Usamos el mapa para obtener la especificación original si es necesario
    # O iteramos de nuevo sobre el archivo para mantener el orden
     while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        local pkg_name_base=$(echo "$pkg" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr -d ' ')
        local formatted_name
        local current_status=${pkg_status[$pkg_name_base]:-"error"} # Default a error si no se encontró

        case "$current_status" in
            installed) formatted_name="${GREEN}✓${NC} $pkg_name_base" ;; 
            installed_update) formatted_name="${YELLOW}✓${NC} $pkg_name_base ${YELLOW}(u)${NC}" ;; 
            not_installed) formatted_name="${CYAN}•${NC} $pkg_name_base" ;; 
            *) formatted_name="${RED}?${NC} $pkg_name_base ${RED}(err)${NC}" ;; # Manejar error/desconocido
        esac

        local padding=$((col_width - ${#pkg_name_base} - 3)) # Ajustar padding
        [[ $padding -lt 1 ]] && padding=1
        formatted_name="$formatted_name$(printf '%*s' $padding '')"

        if ((count % 2 == 0)); then echo -ne "  $formatted_name"; else echo -e "  $formatted_name"; fi
        ((count++))
    done < "$req_file"

    if ((count % 2 != 0)); then echo; fi
    echo
    return 0 # Éxito
}

# Función auxiliar interna para procesar una lista de paquetes en un entorno
_process_packages_in_env() {
    local env_path="$1"
    local env_display_name="$2"
    local packages_to_process_str="$3" # String con paquetes separados por espacio
    local pip_command="$4" # Ej: "install", "install --upgrade"
    local action_verb="$5" # Ej: "Instalando", "Actualizando"
    local activate_cmd="source $env_path/bin/activate"

    local packages_to_process=($packages_to_process_str)
    local total_pkgs=${#packages_to_process[@]}

    if [ "$total_pkgs" -eq 0 ]; then
        mostrar_info "No hay paquetes para $action_verb en '$env_display_name'."
        return 0 # Éxito, nada que hacer
    fi

    echo -e "\n${WHITE}$action_verb $total_pkgs paquetes en '$env_display_name':${NC}"

    # Ejecutar en subshell
    (
        eval "$activate_cmd" || {
            mostrar_error "(Subshell) No se pudo activar el entorno virtual '$env_display_name'."
            exit 1
        }

        local count=0
        local success_count=0
        local error_count=0

        for pkg_spec in "${packages_to_process[@]}"; do
            local pkg_name_only=$(echo "$pkg_spec" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr -d ' ')
            ((count++))
            echo -ne "${CYAN}[${count}/${total_pkgs}]${NC} $action_verb ${pkg_name_only}... "
            log "DEBUG" "$action_verb paquete: $pkg_spec en $env_display_name"

            # Ejecutar el comando pip
            if pip $pip_command "$pkg_spec" >> "$LOG_FILE" 2>&1; then
                echo -e "${GREEN}✓${NC}"
                log "INFO" "Paquete $pkg_spec procesado ($pip_command) correctamente en $env_display_name"
                ((success_count++))
            else
                echo -e "${RED}✗${NC}"
                log "ERROR" "Fallo al procesar ($pip_command) $pkg_spec en $env_display_name: $(tail -n 10 "$LOG_FILE" | grep -v ERROR)"
                ((error_count++))
            fi
        done

        echo
        if [ $error_count -eq 0 ]; then
            mostrar_exito "$action_verb de paquetes completada exitosamente ($success_count procesados)."
            exit 0 # Éxito del subshell
        else
            mostrar_advertencia "$action_verb completada con $error_count errores ($success_count exitosos)."
            echo -e "Revise el archivo de log para más detalles: $LOG_FILE"
            exit 1 # Error del subshell
        fi
    ) # Fin del subshell

    return $? # Devolver el código de salida del subshell
}

# Función para instalar paquetes desde un archivo de requisitos
install_packages() {
    local env_name="$1"
    local req_file="$2"
    local env_path="$VENV_DIR/$env_name" # Corregido para usar el nombre del entorno
    log "INFO" "Instalando paquetes para $env_name desde $req_file en $env_path"

    if [ ! -f "$req_file" ]; then
        mostrar_error "El archivo de requisitos '$req_file' no fue encontrado."
        exit 1
    fi

    if [ ! -d "$env_path" ]; then
        mostrar_error "El directorio del entorno '$env_path' no existe."
        exit 1
    fi
    
    # Verificar conexión a internet antes de instalar paquetes
    if ! verificar_conexion_internet; then
        exit 1
    fi
    
    mostrar_info "Preparando instalación desde $req_file en el entorno '$env_name'..."
    local activate_cmd="source $env_path/bin/activate"
    local packages_to_install=""
    local pending_count=0

    # Activar temporalmente en subshell para actualizar pip y verificar paquetes
    (
        eval "$activate_cmd" || {
            mostrar_error "(Subshell-check) No se pudo activar el entorno virtual '$env_name'."
            exit 1
        }
        
        # Actualizar pip dentro del entorno virtual
        mostrar_info "Actualizando pip en el entorno virtual '$env_name'..."
        echo -ne "${YELLOW}▶${NC} Actualizando pip... "
        if pip install --upgrade pip >> "$LOG_FILE" 2>&1; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            mostrar_advertencia "No se pudo actualizar pip. Continuando con la instalación de paquetes."
            log "WARN" "Fallo al actualizar pip en $env_name: $(tail -n 5 "$LOG_FILE" | grep -v WARN)"
        fi
    ) # Fin subshell de actualización de pip

    if [ $? -ne 0 ]; then
        mostrar_error "Fallo al actualizar pip en el entorno '$env_name'."
        exit 1
    fi
        
    # Mostrar el estado de los paquetes
    display_packages_status "$req_file" "$env_path" "$env_name"
    
    # Construir la lista de paquetes a instalar
    while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        local status=$(check_package_status "$pkg_line" "$env_path")
        if [[ "$status" == "not_installed" || "$status" == "installed_update" ]]; then
            # No añadir comillas aquí
            packages_to_install+=" $pkg"
            ((pending_count++))
        fi
    done < "$req_file"
    
    # Si no hay nada que instalar, terminar
    if [ "$pending_count" -eq 0 ]; then
        mostrar_exito "Todos los paquetes requeridos ya están instalados y actualizados en '$env_name'."
        exit 0
    fi
    
    # Llamar a la función auxiliar para instalar
    _process_packages_in_env "$env_path" "$env_name" "$packages_to_install" "install" "Instalando"
    local install_exit_code=$?

    if [ $install_exit_code -ne 0 ]; then
        mostrar_error "Ocurrió un error durante la instalación de paquetes."
    else
        mostrar_exito "Proceso de instalación finalizado para '$env_name'."
    fi
    exit $install_exit_code
}

# Función para crear alias pybin
crear_alias_pybin() {
    # Definir el alias apuntando al entorno predeterminado
    local alias_cmd="alias pybin='source $BIN_VENV_DIR/bin/activate'"
    
    # Crear alias para la sesión actual
    eval "$alias_cmd"
    
    # Verificar si ya existe en .bashrc
    if ! grep -q "alias pybin='source $BIN_VENV_DIR/bin/activate'" "$HOME/.bashrc"; then
        # Añadir alias al .bashrc para persistencia
        echo -e "\n# Alias para activar el entorno Python por defecto ($BIN_VENV_DIR)" >> "$HOME/.bashrc"
        echo "$alias_cmd" >> "$HOME/.bashrc"
        mostrar_info "Alias 'pybin' creado y añadido a ~/.bashrc"
        mostrar_info "Para activar el alias en esta sesión ejecute: source ~/.bashrc"
    else
        mostrar_info "Alias 'pybin' ya existía en ~/.bashrc y apunta a '$BIN_VENV_DIR'"
    fi
    
    log "INFO" "Alias pybin configurado para activar $BIN_VENV_DIR"
}

# Función para crear alias pyunbin para desactivar entorno
crear_alias_pyunbin() {
    # Definir el alias
    local alias_cmd="alias pyunbin='deactivate'"
    
    # Crear alias para la sesión actual
    eval "$alias_cmd"
    
    # Verificar si ya existe en .bashrc
    if ! grep -q "alias pyunbin='deactivate'" "$HOME/.bashrc"; then
        # Añadir alias al .bashrc para persistencia
        echo -e "# Alias para desactivar el entorno Python activo" >> "$HOME/.bashrc"
        echo "$alias_cmd" >> "$HOME/.bashrc"
        mostrar_info "Alias 'pyunbin' creado y añadido a ~/.bashrc"
    else
        mostrar_info "Alias 'pyunbin' ya existía en ~/.bashrc"
    fi
    
    log "INFO" "Alias pyunbin configurado para desactivar entornos virtuales"
}

# Función para configurar el autostart del entorno virtual
configurar_autostart() {
    local action="$1"
    log "INFO" "Configurando autostart del entorno virtual predeterminado (acción: $action)"
    
    # Definir el código que se añadirá al .bashrc
    local autostart_code="
# Inicio automático del entorno virtual Python predeterminado
if [ -f \"\$HOME/.venv-auto\" ]; then
    if [ -f \"$BIN_VENV_DIR/bin/activate\" ]; then
        source \"$BIN_VENV_DIR/bin/activate\"
        echo -e \"${GREEN}Entorno virtual Python predeterminado activado automáticamente${NC}\"
    fi
fi"
    
    # Verificar si ya existe la configuración
    if ! grep -q "# Inicio automático del entorno virtual Python predeterminado" "$HOME/.bashrc"; then
        # Añadir código al .bashrc
        echo -e "$autostart_code" >> "$HOME/.bashrc"
        mostrar_exito "Configuración de inicio automático añadida a ~/.bashrc"
        mostrar_info "Para aplicar los cambios en esta sesión ejecute: source ~/.bashrc"
    else
        mostrar_info "La configuración de inicio automático ya existe en ~/.bashrc"
    fi
    
    # Procesar acción según el parámetro
    case "$action" in
        on)
            # Activar autostart creando el archivo indicador
            touch "$HOME/.venv-auto"
            mostrar_exito "Inicio automático del entorno virtual ACTIVADO"
            mostrar_info "El entorno se activará automáticamente en el próximo inicio de sesión"
            ;;
        off)
            # Desactivar autostart eliminando el archivo indicador
            if [ -f "$HOME/.venv-auto" ]; then
                rm -f "$HOME/.venv-auto"
                mostrar_exito "Inicio automático del entorno virtual DESACTIVADO"
                mostrar_info "El entorno ya no se activará automáticamente en los inicios de sesión"
            else
                mostrar_info "El inicio automático ya estaba desactivado"
            fi
            ;;
        *)
            mostrar_error "Acción no válida: $action"
            mostrar_info "Opciones disponibles: 'on' para activar o 'off' para desactivar"
            exit 1
            ;;
    esac
    
    log "INFO" "Configuración de autostart completada"
}

# Función para instalar el entorno por defecto y sus dependencias
install_default_env() {
    mostrar_info "====================================================="
    mostrar_info "  Instalando entorno Python predeterminado (default)"
    mostrar_info "====================================================="
    log "INFO" "Iniciando instalación del entorno por defecto en $BIN_VENV_DIR"
    
    # Verificar si el directorio ya existe
    if [ -d "$BIN_VENV_DIR" ]; then
        read -p "El entorno predeterminado '$BIN_VENV_DIR' ya existe. ¿Desea reinstalarlo? (s/N/c=cancelar): " confirm
        # Verificar la respuesta del usuario
        if [[ "$confirm" =~ ^[Cc]$ ]]; then
            # Opción 'c' - Cancelar completamente la operación
            mostrar_info "Operación cancelada por el usuario."
            log "INFO" "Operación cancelada por el usuario"
            exit 0
        elif [[ -z "$confirm" || ! "$confirm" =~ ^[Ss] ]]; then
            # Opción 'n' (por defecto) - Usar el entorno existente
            mostrar_info "Usando el entorno predeterminado existente."
            # Continuar con la verificación de paquetes sin reinstalar
            log "INFO" "Se usará el entorno existente en $BIN_VENV_DIR"
            
            # Verificar si el archivo de requisitos existe
            if [ ! -f "$DEFAULT_ENV_REQUIREMENTS_PATH" ]; then
                mostrar_error "El archivo de requisitos '$DEFAULT_ENV_REQUIREMENTS_PATH' no fue encontrado."
                exit 1
            fi
            
            # Verificar conexión a internet antes de instalar paquetes
            if ! verificar_conexion_internet; then
                mostrar_advertencia "No se instalarán paquetes debido a la falta de conexión a internet."
                echo "Puede instalar los paquetes más tarde cuando tenga conexión."
                echo "Ejecute el siguiente comando para activar el entorno:"
                echo "source $BIN_VENV_DIR/bin/activate"
                exit 0
            fi
            
            # Mostrar resumen del proceso
            echo -e "\n${WHITE}Resumen de la instalación/actualización:${NC}"
            echo -e " • Entorno: ${CYAN}$BIN_VENV_DIR${NC} (existente)"
            echo -e " • Paquetes: ${CYAN}$DEFAULT_ENV_REQUIREMENTS_PATH${NC}"
            echo -e " • Log: ${CYAN}$LOG_FILE${NC}"
            echo
            
            # Instalar paquetes pendientes (usando la función auxiliar)
            mostrar_info "Verificando paquetes en $DEFAULT_ENV_REQUIREMENTS_PATH..."
            local packages_to_process_default=""
            local pending_count_default=0

            # Activar temporalmente para actualizar pip
            (
                source "$BIN_VENV_DIR/bin/activate" || {
                    mostrar_error "(Subshell-check) No se pudo activar el entorno virtual predeterminado."
                    exit 1
                }
                # Actualizar pip dentro del entorno virtual
                mostrar_info "Actualizando pip en el entorno virtual predeterminado..."
                echo -ne "${YELLOW}▶${NC} Actualizando pip... "
                if pip install --upgrade pip >> "$LOG_FILE" 2>&1; then
                    echo -e "${GREEN}✓${NC}"
                else
                    echo -e "${RED}✗${NC}"
                    mostrar_advertencia "No se pudo actualizar pip. Continuando con la instalación de paquetes."
                    log "WARN" "Fallo al actualizar pip en $BIN_VENV_DIR: $(tail -n 5 "$LOG_FILE" | grep -v WARN)"
                fi
            ) # Fin subshell pip update

            if [ $? -ne 0 ]; then
                mostrar_error "Fallo al actualizar pip en el entorno predeterminado."
                exit 1
            fi

            display_packages_status "$DEFAULT_ENV_REQUIREMENTS_PATH" "$BIN_VENV_DIR"

            while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
                local pkg=${pkg_line%%#*} # Eliminar comentarios
                pkg=$(echo "$pkg" | xargs) # Limpiar espacios
                [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

                # No añadir comillas aquí
                local status=$(check_package_status "$pkg_line" "$BIN_VENV_DIR")
                if [[ "$status" == "not_installed" || "$status" == "installed_update" ]]; then
                    # No añadir comillas aquí
                    packages_to_process_default+=" $pkg"
                    ((pending_count_default++))
                fi
            done < "$DEFAULT_ENV_REQUIREMENTS_PATH"

            if [ "$pending_count_default" -eq 0 ]; then
                mostrar_exito "Todos los paquetes ya están instalados y actualizados en el entorno predeterminado."
            else
                 _process_packages_in_env "$BIN_VENV_DIR" "predeterminado (default)" "$packages_to_process_default" "install" "Instalando"
                 if [ $? -ne 0 ]; then
                     mostrar_error "Ocurrió un error durante la verificación/instalación de paquetes en el entorno predeterminado."
                     exit 1
                 fi
            fi
            
            # Crear alias para activar el entorno
            crear_alias_pybin
            crear_alias_pyunbin
            
            echo -e "\n${WHITE}Para activar este entorno predeterminado:${NC}"
            echo -e "1. Actualice su shell: ${GREEN}source ~/.bashrc${NC}"
            echo -e "2. Use el alias: ${GREEN}pybin${NC}"
            echo -e "\n${WHITE}Para desactivar el entorno:${NC}"
            echo -e "  Use el alias: ${GREEN}pyunbin${NC}"
            log "INFO" "Verificación de paquetes completada con éxito para el entorno predeterminado"
            return
        else
            # Opción 's' - Reinstalar el entorno
            mostrar_info "Eliminando entorno predeterminado existente..."
            echo -ne "${YELLOW}▶${NC} Eliminando $BIN_VENV_DIR... "
            if rm -rf "$BIN_VENV_DIR"; then
                echo -e "${GREEN}✓${NC}"
            else
                echo -e "${RED}✗${NC}"
                mostrar_error "No se pudo eliminar el entorno existente."
                exit 1
            fi
        fi
    fi
    
    # Verificar si el archivo de requisitos existe
    if [ ! -f "$DEFAULT_ENV_REQUIREMENTS_PATH" ]; then
        mostrar_error "El archivo de requisitos '$DEFAULT_ENV_REQUIREMENTS_PATH' no fue encontrado."
        exit 1
    fi
    
    # Crear el directorio padre del entorno virtual si no existe
    echo -ne "${YELLOW}▶${NC} Preparando directorio base $VENV_DIR... "
    if mkdir -p "$VENV_DIR"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        mostrar_error "No se pudo crear el directorio base para el entorno virtual."
        exit 1
    fi
    
    # Crear el entorno virtual
    mostrar_info "Creando entorno virtual predeterminado en: $BIN_VENV_DIR"
    echo -ne "${YELLOW}▶${NC} Inicializando entorno virtual... "
    if python3 -m venv "$BIN_VENV_DIR" >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✓${NC}"
        mostrar_exito "Entorno virtual predeterminado creado exitosamente"
    else
        echo -e "${RED}✗${NC}"
        mostrar_error "Falló la creación del entorno virtual predeterminado."
        log "ERROR" "Creación del entorno fallida en $BIN_VENV_DIR: $(tail -n 10 "$LOG_FILE" | grep -v ERROR)"
        exit 1
    fi
    
    # Verificar conexión a internet antes de instalar paquetes
    if ! verificar_conexion_internet; then
        mostrar_advertencia "Se ha creado el entorno virtual, pero no se instalarán paquetes debido a la falta de conexión a internet."
        echo "Puede instalar los paquetes más tarde cuando tenga conexión."
        echo "Ejecute el siguiente comando para activar el entorno:"
        echo "source $BIN_VENV_DIR/bin/activate"
        exit 0
    fi
    
    # Mostrar resumen del proceso
    echo -e "\n${WHITE}Resumen de la instalación:${NC}"
    echo -e " • Entorno: ${CYAN}$BIN_VENV_DIR${NC} (nuevo)"
    echo -e " • Paquetes: ${CYAN}$DEFAULT_ENV_REQUIREMENTS_PATH${NC}"
    echo -e " • Log: ${CYAN}$LOG_FILE${NC}"
    echo
    
    # Instalar los paquetes (usando la función auxiliar)
    mostrar_info "Instalando paquetes desde $DEFAULT_ENV_REQUIREMENTS_PATH..."
    local packages_to_install_default=""
    local pending_count_install=0

    # Activar temporalmente para actualizar pip
     (
        source "$BIN_VENV_DIR/bin/activate" || {
            mostrar_error "(Subshell-check) No se pudo activar el entorno virtual predeterminado."
            exit 1
        }
        
        # Actualizar pip dentro del entorno virtual
        echo -ne "${YELLOW}▶${NC} Actualizando pip... "
        if pip install --upgrade pip >> "$LOG_FILE" 2>&1; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            mostrar_advertencia "No se pudo actualizar pip. Continuando con la instalación de paquetes."
            log "WARN" "Fallo al actualizar pip en $BIN_VENV_DIR: $(tail -n 5 "$LOG_FILE" | grep -v WARN)"
        fi
    ) # Fin del subshell pip update

    if [ $? -ne 0 ]; then
        mostrar_error "Fallo al actualizar pip en el entorno predeterminado."
        exit 1
    fi
        
    # Mostrar el estado de los paquetes
    display_packages_status "$DEFAULT_ENV_REQUIREMENTS_PATH" "$BIN_VENV_DIR"
    
    # Contar el número total de paquetes a instalar
    while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        # No añadir comillas aquí
        local status=$(check_package_status "$pkg_line" "$BIN_VENV_DIR")
        if [[ "$status" == "not_installed" || "$status" == "installed_update" ]]; then
             # No añadir comillas aquí
             packages_to_install_default+=" $pkg"
             ((pending_count_install++))
        fi
    done < "$DEFAULT_ENV_REQUIREMENTS_PATH"
    
    # Si no hay nada que instalar, informar y continuar para crear alias
    if [ "$pending_count_install" -eq 0 ]; then
        mostrar_exito "Todos los paquetes requeridos ya están instalados y actualizados en el entorno predeterminado."
    else
        # Llamar a la función auxiliar para instalar
        _process_packages_in_env "$BIN_VENV_DIR" "predeterminado (default)" "$packages_to_install_default" "install" "Instalando"
        if [ $? -ne 0 ]; then
            mostrar_error "Ocurrió un error durante la instalación de paquetes."
            exit 1
        fi
    fi

    # Crear alias para activar y desactivar el entorno
    crear_alias_pybin
    crear_alias_pyunbin
    
    echo -e "\n${WHITE}Para activar este entorno predeterminado:${NC}"
    echo -e "1. Actualice su shell: ${GREEN}source ~/.bashrc${NC}"
    echo -e "2. Use el alias: ${GREEN}pybin${NC}"
    echo -e "\n${WHITE}Para desactivar el entorno:${NC}"
    echo -e "  Use el alias: ${GREEN}pyunbin${NC}"
    log "INFO" "Instalación del entorno por defecto completada con éxito"
}

# Función para proporcionar instrucciones de activación
activate_venv() {
    local env_name="$1"
    local env_path
    local is_local=false

    # Si no se da nombre, intentar detectar local
    if [ -z "$env_name" ]; then
        env_path=$(get_local_venv_path)
        if [ -n "$env_path" ]; then
            env_name="."
            is_local=true
            log "INFO" "Solicitando activación del entorno local detectado: $env_path"
        else
            mostrar_error "Se requiere un nombre de entorno (o ejecute desde un directorio con un .venv local)."
            echo "Uso: $0 activate <nombre_entorno | .>"
            list_venvs # Mostrar entornos disponibles
            exit 1
        fi
    # Si se especifica "."
    elif [ "$env_name" == "." ]; then
        env_path=$(get_local_venv_path)
        if [ -z "$env_path" ]; then
            mostrar_error "No se encontró un entorno local (.venv) en el directorio actual: $PWD"
            exit 1
        fi
        is_local=true
        log "INFO" "Solicitando activación del entorno local especificado: $env_path"
    # Si se especifica un nombre
    else
        env_path="$VENV_DIR/$env_name"
        log "INFO" "Solicitando activación del entorno global: $env_name"
    fi
    
    # Verificar existencia (para el caso de nombre global)
    if [ "$is_local" = false ] && [ ! -d "$env_path" ]; then
        mostrar_error "El entorno global '$env_name' no existe en $VENV_DIR"
        echo "Entornos disponibles:"
        list_venvs
        exit 1
    fi

    # Verificar que sea un entorno válido (archivo activate)
     if [ ! -f "$env_path/bin/activate" ]; then
         mostrar_error "La ruta encontrada ($env_path) no parece ser un entorno virtual válido."
         exit 1
     fi
    
    echo "Para activar este entorno, ejecute el siguiente comando:"
    if [ "$is_local" = true ]; then
        mostrar_exito "source $PWD/.venv/bin/activate"
    else
         mostrar_exito "source $env_path/bin/activate"
    fi
}

# Función para listar todos los entornos virtuales
list_venvs() {
    mostrar_info "Entornos virtuales disponibles:"
    log "INFO" "Listando entornos virtuales disponibles"
    local found_any=false

    # Comprobar entorno local
    local local_venv_path=$(get_local_venv_path)
    if [ -n "$local_venv_path" ]; then
        echo -e "  * ${CYAN}.venv (local)${NC} ${YELLOW}[En: $PWD]${NC}"
        found_any=true
    fi

    # Comprobar entornos globales
    if [ ! -d "$VENV_DIR" ] || [ -z "$(ls -A "$VENV_DIR" 2>/dev/null)" ]; then
        if [ "$found_any" = false ]; then
            mostrar_advertencia "No hay entornos virtuales creados (ni local ni globales)."
        fi
        # No retornar todavía, podría haber solo local
    else
        local found_global=false
        for env in "$VENV_DIR"/*; do
            if [ -d "$env" ] && [ -f "$env/bin/activate" ]; then
                # No listar el entorno predeterminado dos veces si estamos en $HOME
                # O si el local coincide con el default (poco probable pero posible)
                if [ "$(basename "$env")" == "default" ] && [ "$local_venv_path" == "$BIN_VENV_DIR" ]; then
                   continue 
                fi
                
                local display_name=$(basename "$env")
                if [ "$env" == "$BIN_VENV_DIR" ]; then
                     echo -e "  * ${GREEN}$display_name (predeterminado)${NC}"
                else
                     echo "  * $display_name"
                fi
                found_any=true
                found_global=true
            fi
        done
         if [ "$found_global" = false ] && [ "$found_any" = false ]; then
             mostrar_advertencia "No hay entornos virtuales globales creados."
         fi
    fi
}

# Función para eliminar entornos o paquetes
remove_venv() {
    local env_name="$1"
    local option="$2"
    local pkg_name="$3"
    local env_path
    local env_display_name
    local is_local=false
    
    if [ -z "$env_name" ]; then
        mostrar_error "Se requiere un nombre de entorno (o '.' para local)."
        echo "Uso: $0 remove <nombre_entorno | .> [--package <paquete>]"
        exit 1
    fi

    # Determinar si es local o global
    if [ "$env_name" == "." ]; then
        env_path=$(get_local_venv_path)
        if [ -z "$env_path" ]; then
             mostrar_error "No se encontró un entorno local (.venv) en el directorio actual: $PWD"
             exit 1
        fi
        env_display_name=".venv (local)"
        is_local=true
        log "INFO" "Solicitando eliminación para entorno local: $env_path"
    else
        env_path="$VENV_DIR/$env_name"
        env_display_name="$env_name"
        is_local=false
         # Verificar si existe el entorno global
        if [ ! -d "$env_path" ]; then
            mostrar_error "El entorno global '$env_name' no existe en $VENV_DIR"
            echo "Entornos disponibles:"
            list_venvs
            exit 1
        fi
        log "INFO" "Solicitando eliminación para entorno global: $env_path"
    fi
    
    # Verificar si es un entorno válido (activate)
    if [ ! -f "$env_path/bin/activate" ]; then
        mostrar_error "La ruta '$env_path' no parece ser un entorno virtual válido."
        exit 1
    fi

    # Si la opción es --package, eliminar un paquete específico
    if [[ "$option" == "--package" ]]; then
        if [ -z "$pkg_name" ]; then
            mostrar_error "Se requiere un nombre de paquete para eliminar."
            echo "Uso: $0 remove <nombre_entorno | .> --package <paquete>"
            exit 1
        fi
        
        log "INFO" "Solicitando eliminación del paquete: $pkg_name del entorno $env_display_name"
        local activate_cmd="source $env_path/bin/activate"
        
        # Activar el entorno en subshell y verificar paquete
        local pkg_exists_ret
        pkg_exists_ret=$( (
            eval "$activate_cmd" >/dev/null 2>&1
            pip list | grep -qi "^$pkg_name "
            echo $?
        ) )

        if [ "$pkg_exists_ret" -ne 0 ]; then # 0 significa que existe
            mostrar_error "El paquete '$pkg_name' no está instalado en el entorno '$env_display_name'."
            exit 1
        fi
        
        read -p "¿Está seguro de que desea eliminar el paquete '$pkg_name' del entorno '$env_display_name'? (s/N): " confirm
        if [[ "$confirm" =~ ^[Ss]$ ]]; then
            mostrar_info "Eliminando paquete $pkg_name del entorno $env_display_name..."
            echo -ne "${YELLOW}▶${NC} Desinstalando $pkg_name... "
            
            # Ejecutar uninstall en subshell
            local uninstall_ret
            (
                 eval "$activate_cmd" >/dev/null 2>&1
                 pip uninstall -y "$pkg_name" >> "$LOG_FILE" 2>&1
            )
            uninstall_ret=$?
            
            if [ $uninstall_ret -eq 0 ]; then
                echo -e "${GREEN}✓${NC}"
                mostrar_exito "Paquete $pkg_name eliminado exitosamente."
                log "INFO" "Paquete $pkg_name eliminado del entorno $env_display_name con éxito"
            else
                echo -e "${RED}✗${NC}"
                mostrar_error "Falló la eliminación del paquete $pkg_name"
                log "ERROR" "Fallo al eliminar el paquete $pkg_name de $env_display_name: $(tail -n 10 "$LOG_FILE" | grep -v ERROR)"
            fi
        else
            mostrar_info "Operación cancelada."
            log "INFO" "Eliminación del paquete $pkg_name cancelada por el usuario"
        fi
    else
        # Eliminar el entorno completo
        log "INFO" "Solicitando eliminación del entorno: $env_display_name"
    
        read -p "¿Está seguro de que desea eliminar el entorno '$env_display_name' en '$env_path'? (s/N): " confirm
        if [[ "$confirm" =~ ^[Ss]$ ]]; then
            mostrar_info "Eliminando entorno virtual: $env_display_name"
            echo -ne "${YELLOW}▶${NC} Eliminando $env_path... "
            if rm -rf "$env_path"; then
                 echo -e "${GREEN}✓${NC}"
                 mostrar_exito "Entorno virtual eliminado exitosamente."
                 log "INFO" "Entorno virtual $env_display_name ($env_path) eliminado con éxito"
            else
                echo -e "${RED}✗${NC}"
                mostrar_error "No se pudo eliminar el entorno virtual en $env_path."
                exit 1
            fi
        else
            mostrar_info "Operación cancelada."
            log "INFO" "Eliminación del entorno $env_display_name ($env_path) cancelada por el usuario"
        fi
    fi
}

# Función para actualizar paquetes en un entorno virtual
update_packages() {
    local env_name_arg="$1" # Puede ser nombre, "." o vacío
    local pkg_name="$2"
    local env_path
    local env_display_name
    local is_local=false

    # Determinar el path y el nombre para mostrar
    if [ -z "$env_name_arg" ]; then
        # Sin argumento: intentar local, luego default global
        env_path=$(get_local_venv_path)
        if [ -n "$env_path" ]; then
            env_display_name=".venv (local)"
            is_local=true
            log "INFO" "Actualizando paquetes en el entorno local detectado: $env_path"
        else
            env_path="$BIN_VENV_DIR"
            env_display_name="predeterminado (default)"
            is_local=false
            log "INFO" "Actualizando paquetes en el entorno predeterminado global: $env_path"
        fi
    elif [ "$env_name_arg" == "." ]; then
        # Argumento ".": usar local
        env_path=$(get_local_venv_path)
         if [ -z "$env_path" ]; then
             mostrar_error "No se encontró un entorno local (.venv) en el directorio actual: $PWD"
             exit 1
        fi
        env_display_name=".venv (local)"
        is_local=true
        log "INFO" "Actualizando paquetes en el entorno local especificado: $env_path"
    else
        # Argumento con nombre: usar global
        env_path="$VENV_DIR/$env_name_arg"
        env_display_name="$env_name_arg"
        is_local=false
        log "INFO" "Actualizando paquetes en el entorno global: $env_path"
    fi

    # Verificar si el entorno (local o global) existe y es válido
    if [ ! -d "$env_path" ] || [ ! -f "$env_path/bin/activate" ]; then
        mostrar_error "El entorno '$env_display_name' no existe o no es válido en '$env_path'"
        if [ "$is_local" = false ]; then
             echo "Entornos globales disponibles:"
             list_venvs
        fi
        exit 1
    fi

    # Verificar conexión a internet
    if ! verificar_conexion_internet; then
        exit 1
    fi

    mostrar_info "Preparando actualización en el entorno '$env_display_name'..."
    local activate_cmd="source $env_path/bin/activate"

    # Actualizar pip primero (en subshell)
    (
        eval "$activate_cmd" || {
            mostrar_error "(Subshell-pip) No se pudo activar el entorno virtual '$env_display_name'."
            exit 1
        }
        mostrar_info "Actualizando pip en el entorno '$env_display_name'..."
        echo -ne "${YELLOW}▶${NC} Actualizando pip... "
        if pip install --upgrade pip >> "$LOG_FILE" 2>&1; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            mostrar_advertencia "No se pudo actualizar pip. La actualización de otros paquetes podría fallar."
            log "WARN" "Fallo al actualizar pip en $env_display_name: $(tail -n 5 "$LOG_FILE" | grep -v WARN)"
            # No salimos con error aquí, pero lo advertimos
        fi
    ) # Fin del subshell pip update

     if [ $? -ne 0 ]; then
        mostrar_error "Fallo grave al intentar actualizar pip en el entorno '$env_display_name'."
        exit 1
    fi

    # Si se especificó un paquete
    if [ -n "$pkg_name" ]; then
        # No añadir comillas aquí
        local package_to_update_str="$pkg_name"
        # Verificar si está instalado (en subshell)
        local installed_check
        installed_check=$( (
            eval "$activate_cmd" >/dev/null 2>&1
            pip list | grep -qi "^$pkg_name "
            echo $?
        ) )

        if [ "$installed_check" -ne 0 ]; then
             mostrar_error "El paquete '$pkg_name' no está instalado en el entorno '$env_display_name'. No se puede actualizar."
             exit 1
        fi
        
        _process_packages_in_env "$env_path" "$env_display_name" "$package_to_update_str" "install --upgrade" "Actualizando"
        local update_exit_code=$?
        if [ $update_exit_code -ne 0 ]; then
             mostrar_error "Ocurrió un error durante la actualización del paquete '$pkg_name'."
        fi
        exit $update_exit_code
    else
        # Actualizar todos los paquetes desactualizados
        mostrar_info "Buscando paquetes desactualizados en '$env_display_name'..."
        local outdated_packages_str
        local outdated_packages_list=""
        local pip_list_ret

        # Obtener lista de desactualizados (en subshell)
        outdated_packages_str=$( (
             eval "$activate_cmd" >/dev/null 2>&1
             pip list --outdated --format=freeze 2>>"$LOG_FILE"
             echo $?
         ) )
         pip_list_ret=$(echo "$outdated_packages_str" | tail -n1) # Código de retorno es la última línea
         outdated_packages_str=$(echo "$outdated_packages_str" | head -n -1) # El resto es la salida

         if [ $pip_list_ret -ne 0 ]; then
             mostrar_error "Hubo un error al listar paquetes desactualizados (código: $pip_list_ret). Revise $LOG_FILE"
             log "ERROR" "pip list --outdated falló en $env_display_name"
             exit 1
         fi

        # Filtrar cabeceras y construir lista para la función auxiliar
        local total_outdated=0
        echo "$outdated_packages_str" | grep '==' | while IFS= read -r line; do
            local pkg_to_update=$(echo "$line" | cut -d'=' -f1)
            # No añadir comillas aquí
            outdated_packages_list+=" $pkg_to_update"
            ((total_outdated++))
        done

        if [ "$total_outdated" -eq 0 ]; then
            mostrar_exito "Todos los paquetes están actualizados en el entorno '$env_display_name'."
            exit 0
        fi

        _process_packages_in_env "$env_path" "$env_display_name" "$outdated_packages_list" "install --upgrade" "Actualizando"
        local update_all_exit_code=$?
        if [ $update_all_exit_code -ne 0 ]; then
             mostrar_advertencia "Ocurrieron errores durante la actualización masiva de paquetes."
        fi
        exit $update_all_exit_code
    fi
}

# Función para mostrar la ayuda
mostrar_ayuda() {
    echo -e "
    ${WHITE}Uso:${NC} $(basename "$0") {create|activate|list|remove|--install|--update|--autostart|help}
    
    ${WHITE}Comandos:${NC}
      ${CYAN}create${NC} <nombre_entorno> [archivo_requisitos]  Crear un nuevo entorno virtual global ($HOME/.venv/<nombre>)
      ${CYAN}create${NC} . [archivo_requisitos]                 Crear un entorno virtual local ($PWD/.venv)
      ${CYAN}activate${NC} <nombre_entorno>                     Mostrar instrucciones de activación para un entorno global
      ${CYAN}activate${NC} .                                    Mostrar instrucciones de activación para un entorno local
      ${CYAN}list${NC}                                          Listar todos los entornos virtuales (local y globales)
      ${CYAN}remove${NC} <nombre_entorno> [--package <paquete>] Eliminar un entorno virtual o un paquete específico
      ${CYAN}--install${NC}                                     Instalar entorno predeterminado en $BIN_VENV_DIR
      ${CYAN}--update${NC} [nombre_entorno] [paquete]           Actualizar paquetes en un entorno virtual
      ${CYAN}--autostart${NC} {on|off}                          Activar/desactivar inicio automático del entorno
      ${CYAN}help${NC}                                          Mostrar esta ayuda
      
    ${WHITE}Aliases creados con --install:${NC}
      ${CYAN}pybin${NC}                                         Activa el entorno predeterminado
      ${CYAN}pyunbin${NC}                                       Desactiva el entorno activo"
    log "INFO" "Se mostró la ayuda al usuario"
}

# Función para mostrar el banner simple y estético
show_banner() {
  # Ancho deseado (aproximado)
  local width=50

  # Línea superior
  printf '%s\n' "$(printf '+%*s+' "$width" '' | tr ' ' '-')"

  # Título centrado
  local title_len=${#APP_NAME}
  local title_pad=$(( (width - title_len) / 2 ))
  printf '%s\n' "$(printf '|%*s%s%*s|' "$title_pad" '' "$APP_NAME" "$((width - title_pad - title_len))" '')"

  # Separador
  printf '%s\n' "$(printf '|%*s|' "$width" '')"

  # Versión alineada
  local version_text="Version: $APP_VERSION"
  local version_len=${#version_text}
  local version_pad=$((width - version_len - 1))
  printf '%s\n' "$(printf '| %s%*s|' "$version_text" "$version_pad" '')"

  # Autor alineado
  local author_text="By: $APP_AUTHOR"
  local author_len=${#author_text}
  local author_pad=$((width - author_len - 1))
  printf '%s\n' "$(printf '| %s%*s|' "$author_text" "$author_pad" '')"

  # Línea inferior
  printf '%s\n' "$(printf '+%*s+' "$width" '' | tr ' ' '-')"

  echo # Línea en blanco después del banner
}

# Función para obtener la ruta de un entorno local si existe y es válido
get_local_venv_path() {
    local local_venv="$PWD/.venv"
    if [ -d "$local_venv" ] && [ -f "$local_venv/bin/activate" ]; then
        echo "$local_venv"
    else
        echo ""
    fi
}

# Función principal
main() {
    # Mostrar banner inicial
    show_banner
    
    # Iniciar log
    log "INFO" "Iniciando $APP_NAME v$APP_VERSION"
    log "INFO" "Comando ejecutado: $0 ${ORIGINAL_ARGS[*]-}"
    
    check_prerequisites
    ensure_venv_dir
    
    local command="$1"
    shift
    
    # Si no se proporciona ningún comando, mostrar la ayuda
    if [ -z "$command" ]; then
        mostrar_ayuda
        exit 0
    fi
    
    case "$command" in
        create)
            local env_name="$1"
            local req_file="$2"
            # Validar si se intenta crear con nombre "." fuera de HOME (prevenir $HOME/.venv/.)
            if [ "$env_name" == "." ] && [ "$PWD" == "$HOME" ]; then
                mostrar_error "No se permite crear un entorno llamado '.' directamente en $HOME. Use un subdirectorio de proyecto."
                exit 1
            fi
            if [ "$env_name" == "." ] && [[ "$PWD" == $HOME/.venv* ]]; then
                 mostrar_error "No se permite crear un entorno local '.' dentro de $HOME/.venv."
                 exit 1
            fi
            create_venv "$env_name" "$req_file"
            ;;
        activate)
            local env_name="$1"
            activate_venv "$env_name"
            ;;
        list)
            list_venvs
            ;;
        remove)
            local env_name="$1"
            local option="$2"
            local pkg_name="$3"
            remove_venv "$env_name" "$option" "$pkg_name"
            ;;
        --install)
            install_default_env
            ;;
        --update)
            local env_name="$1"
            local pkg_name="$2"
            update_packages "$env_name" "$pkg_name"
            ;;
        --autostart)
            local action="$1"
            if [ -z "$action" ]; then
                mostrar_error "Se requiere una acción para --autostart: on u off"
                echo "Uso: $0 --autostart {on|off}"
                exit 1
            fi
            configurar_autostart "$action"
            ;;
        help)
            mostrar_ayuda
            ;;
        *)
            mostrar_error "Comando desconocido: $command"
            mostrar_ayuda
            exit 1
            ;;
    esac
    
    log "INFO" "Finalización exitosa: $0 ${ORIGINAL_ARGS[*]-}"
}

# Ejecutar la función principal con todos los argumentos
main "$@" 