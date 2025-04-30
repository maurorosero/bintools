#!/bin/bash
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
VENV_DIR="$BIN_DIR/venv"
BIN_VENV_DIR="$BIN_DIR/venv/$USER"
BI_REQUIREMENTS="$BIN_DIR/requirements.txt"
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
# Detectar $HOME del usuario que invocó sudo, si aplica
if [[ -n "${SUDO_USER-}" ]]; then
  USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
  USER_HOME=$HOME
fi

# Determinar ruta de logs según si se ejecuta como root o usuario normal
if [[ "$(id -u)" -eq 0 ]]; then
  # Si se ejecuta con privilegios escalados (root/sudo), siempre usar /var/log
  LOG_DIR="/var/log"
else
  # Solo para procesos sin escalar, usar directorio en home
  LOG_DIR="$USER_HOME/bin/logs"
fi
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
    if $activate_cmd && pip list | grep -i "^$pkg_name " > /dev/null 2>&1; then
        # Obtener la versión instalada
        local installed_version=$($activate_cmd && pip list | grep -i "^$pkg_name " | awk '{print $2}')
        
        # Si hay una restricción de versión, verificar si necesita actualizarse
        if [[ -n "$version_constraint" ]]; then
            if ! $activate_cmd && pip list --outdated | grep -i "^$pkg_name " > /dev/null 2>&1; then
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
    local max_pkg_len=25
    local total_pkgs=0 # Calcular dinámicamente
    local installed_count=0
    local update_count=0
    local pending_count=0

    declare -A pkg_status

    # Primer bucle: Verificar estado y contar total válido
    while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        ((total_pkgs++))
        local pkg_name=$(echo "$pkg" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr -d ' ')
        local status=$(check_package_status "$pkg_line" "$env_path") # Pasar la línea original
        pkg_status["$pkg_name"]="$status"

        case "$status" in
            installed) ((installed_count++)) ;; 
            installed_update) ((update_count++)) ;; 
            not_installed) ((pending_count++)) ;; 
        esac
    done < "$req_file"

    # Mostrar encabezado con resumen
    echo -e "\n${WHITE}Estado de paquetes ($total_pkgs total):${NC}"
    echo -e " • ${GREEN}Ya instalados:${NC} $installed_count"
    echo -e " • ${YELLOW}Requieren actualización:${NC} $update_count"
    echo -e " • ${CYAN}Pendientes de instalar:${NC} $pending_count"
    echo

    # Segundo bucle: Mostrar listado
    local count=0
    local col_width=$((max_pkg_len + 5))
    echo -e "${WHITE}Listado de paquetes:${NC}"
    while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        local pkg_name=$(echo "$pkg" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr -d ' ')
        local formatted_name
        case "${pkg_status[$pkg_name]}" in
            installed) formatted_name="${GREEN}✓${NC} $pkg_name" ;; 
            installed_update) formatted_name="${YELLOW}✓${NC} $pkg_name ${YELLOW}(u)${NC}" ;; 
            not_installed) formatted_name="${CYAN}•${NC} $pkg_name" ;; 
        esac

        local padding=$((col_width - ${#pkg_name} - 3)) # Ajustar padding si es necesario
        [[ $padding -lt 1 ]] && padding=1
        formatted_name="$formatted_name$(printf '%*s' $padding '')"

        if ((count % 2 == 0)); then echo -ne "  $formatted_name"; else echo -e "  $formatted_name"; fi
        ((count++))
    done < "$req_file"

    if ((count % 2 != 0)); then echo; fi
    echo
}

# Función para instalar paquetes desde un archivo de requisitos
install_packages() {
    local env_name="$1"
    local req_file="$2"
    local env_path="$VENV_DIR/$env_name"
    log "INFO" "Instalando paquetes para $env_name desde $req_file"

    if [ ! -f "$req_file" ]; then
        mostrar_error "El archivo de requisitos '$req_file' no fue encontrado."
        exit 1
    fi
    
    # Verificar conexión a internet antes de instalar paquetes
    if ! verificar_conexion_internet; then
        exit 1
    fi
    
    mostrar_info "Instalando paquetes desde $req_file..."
    source "$env_path/bin/activate" || {
        mostrar_error "No se pudo activar el entorno virtual."
        exit 1
    }
    
    # Actualizar pip dentro del entorno virtual
    mostrar_info "Actualizando pip en el entorno virtual..."
    echo -ne "${YELLOW}▶${NC} Actualizando pip... "
    if pip install --upgrade pip >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        mostrar_advertencia "No se pudo actualizar pip. Continuando con la instalación de paquetes."
        log "WARN" "Fallo al actualizar pip: $(tail -n 5 "$LOG_FILE" | grep -v WARN)"
    fi
    
    # Mostrar el estado de los paquetes
    display_packages_status "$req_file" "$env_path"
    
    # Contar el número total de paquetes a instalar
    local pending_count=0
    while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        local status=$(check_package_status "$pkg_line" "$env_path") # Pasar la línea original
        if [[ "$status" == "not_installed" || "$status" == "installed_update" ]]; then
            ((pending_count++))
        fi
    done < "$req_file"
    
    # Si no hay nada que instalar, terminar
    if [ "$pending_count" -eq 0 ]; then
        mostrar_exito "Todos los paquetes ya están instalados y actualizados."
        deactivate
        return
    fi
    
    # Mostrar cabecera para instalación
    echo -e "\n${WHITE}Instalando $pending_count paquetes pendientes:${NC}"
    
    # Contador para paquetes instalados
    local count=0
    
    # Leer línea por línea e instalar los pendientes
    while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        local pkg_name=$(echo "$pkg" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr -d ' ')
        local status=$(check_package_status "$pkg_line" "$env_path") # Pasar la línea original

        if [[ "$status" == "not_installed" || "$status" == "installed_update" ]]; then
            ((count++))
            
            # Formato de progreso: [1/10] instalando numpy...
            echo -ne "${CYAN}[${count}/${pending_count}]${NC} ${pkg_name}... "
            log "DEBUG" "Instalando paquete: $pkg"
            
            if pip install "$pkg" >> "$LOG_FILE" 2>&1; then
                echo -e "${GREEN}✓${NC}"
                log "INFO" "Paquete $pkg_name instalado correctamente"
            else
                echo -e "${RED}✗${NC}"
                mostrar_error "Falló la instalación del paquete $pkg_name"
                log "ERROR" "Fallo en la instalación de $pkg_name: $(tail -n 10 "$LOG_FILE" | grep -v ERROR)"
                echo -e "\nRevise el archivo de log para más detalles: $LOG_FILE"
                deactivate
                exit 1
            fi
        fi
    done < "$req_file"
    
    echo
    mostrar_exito "Paquetes instalados exitosamente."
    deactivate
}

# Función para crear alias pybin
crear_alias_pybin() {
    # Definir el alias
    local alias_cmd="alias pybin='source $BIN_VENV_DIR/bin/activate'"
    
    # Crear alias para la sesión actual
    eval "$alias_cmd"
    
    # Verificar si ya existe en .bashrc
    if ! grep -q "alias pybin='source $BIN_VENV_DIR/bin/activate'" "$HOME/.bashrc"; then
        # Añadir alias al .bashrc para persistencia
        echo -e "\n# Alias para activar el entorno Python por defecto" >> "$HOME/.bashrc"
        echo "$alias_cmd" >> "$HOME/.bashrc"
        mostrar_info "Alias 'pybin' creado y añadido a ~/.bashrc"
        mostrar_info "Para activar el alias en esta sesión ejecute: source ~/.bashrc"
    else
        mostrar_info "Alias 'pybin' ya existía en ~/.bashrc"
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
    log "INFO" "Configurando autostart del entorno virtual (acción: $action)"
    
    # Definir el código que se añadirá al .bashrc
    local autostart_code="
# Inicio automático del entorno virtual Python
if [ -f \"\$HOME/.venv-auto\" ]; then
    if [ -f \"$BIN_VENV_DIR/bin/activate\" ]; then
        source \"$BIN_VENV_DIR/bin/activate\"
        echo -e \"${GREEN}Entorno virtual Python activado automáticamente${NC}\"
    fi
fi"
    
    # Verificar si ya existe la configuración
    if ! grep -q "# Inicio automático del entorno virtual Python" "$HOME/.bashrc"; then
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
    mostrar_info "========================================="
    mostrar_info "  Instalando entorno Python por defecto"
    mostrar_info "========================================="
    log "INFO" "Iniciando instalación del entorno por defecto en $BIN_VENV_DIR"
    
    # Verificar si el directorio ya existe
    if [ -d "$BIN_VENV_DIR" ]; then
        read -p "El entorno '$USER' ya existe. ¿Desea reinstalarlo? (s/N/c=cancelar): " confirm
        # Verificar la respuesta del usuario
        if [[ "$confirm" =~ ^[Cc]$ ]]; then
            # Opción 'c' - Cancelar completamente la operación
            mostrar_info "Operación cancelada por el usuario."
            log "INFO" "Operación cancelada por el usuario"
            exit 0
        elif [[ -z "$confirm" || ! "$confirm" =~ ^[Ss] ]]; then
            # Opción 'n' (por defecto) - Usar el entorno existente
            mostrar_info "Usando el entorno existente."
            # Continuar con la verificación de paquetes sin reinstalar
            log "INFO" "Se usará el entorno existente en $BIN_VENV_DIR"
            
            # Verificar si el archivo de requisitos existe
            if [ ! -f "$BI_REQUIREMENTS" ]; then
                mostrar_error "El archivo de requisitos '$BI_REQUIREMENTS' no fue encontrado."
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
            echo -e "\n${WHITE}Resumen de la instalación:${NC}"
            echo -e " • Entorno: ${CYAN}$BIN_VENV_DIR${NC} (existente)"
            echo -e " • Paquetes: ${CYAN}$BI_REQUIREMENTS${NC}"
            echo -e " • Log: ${CYAN}$LOG_FILE${NC}"
            echo
            
            # Instalar paquetes pendientes
            mostrar_info "Verificando paquetes en $BI_REQUIREMENTS..."
            install_packages "$USER" "$BI_REQUIREMENTS"
            
            # Crear alias para activar el entorno
            crear_alias_pybin
            crear_alias_pyunbin
            
            echo -e "\n${WHITE}Para activar este entorno:${NC}"
            echo -e "1. Actualice su shell: ${GREEN}source ~/.bashrc${NC}"
            echo -e "2. Use el alias: ${GREEN}pybin${NC}"
            echo -e "\n${WHITE}Para desactivar el entorno:${NC}"
            echo -e "  Use el alias: ${GREEN}pyunbin${NC}"
            log "INFO" "Verificación de paquetes completada con éxito"
            return
        else
            # Opción 's' - Reinstalar el entorno
            mostrar_info "Eliminando entorno existente..."
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
    if [ ! -f "$BI_REQUIREMENTS" ]; then
        mostrar_error "El archivo de requisitos '$BI_REQUIREMENTS' no fue encontrado."
        exit 1
    fi
    
    # Crear el directorio del entorno virtual si no existe
    echo -ne "${YELLOW}▶${NC} Preparando directorio... "
    if mkdir -p "$(dirname "$BIN_VENV_DIR")"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        mostrar_error "No se pudo crear el directorio para el entorno virtual."
        exit 1
    fi
    
    # Crear el entorno virtual
    mostrar_info "Creando entorno virtual en: $BIN_VENV_DIR"
    echo -ne "${YELLOW}▶${NC} Inicializando entorno virtual... "
    if python3 -m venv "$BIN_VENV_DIR" >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✓${NC}"
        mostrar_exito "Entorno virtual creado exitosamente"
    else
        echo -e "${RED}✗${NC}"
        mostrar_error "Falló la creación del entorno virtual."
        log "ERROR" "Creación del entorno fallida: $(tail -n 10 "$LOG_FILE" | grep -v ERROR)"
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
    echo -e " • Paquetes: ${CYAN}$BI_REQUIREMENTS${NC}"
    echo -e " • Log: ${CYAN}$LOG_FILE${NC}"
    echo
    
    # Instalar los paquetes
    mostrar_info "Instalando paquetes desde $BI_REQUIREMENTS..."
    source "$BIN_VENV_DIR/bin/activate" || {
        mostrar_error "No se pudo activar el entorno virtual."
        exit 1
    }
    
    # Actualizar pip dentro del entorno virtual
    echo -ne "${YELLOW}▶${NC} Actualizando pip... "
    if pip install --upgrade pip >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        mostrar_advertencia "No se pudo actualizar pip. Continuando con la instalación de paquetes."
        log "WARN" "Fallo al actualizar pip: $(tail -n 5 "$LOG_FILE" | grep -v WARN)"
    fi
    
    # Mostrar el estado de los paquetes
    display_packages_status "$BI_REQUIREMENTS" "$BIN_VENV_DIR"
    
    # Contar el número total de paquetes a instalar
    local pending_count=0
    while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        local status=$(check_package_status "$pkg_line" "$BIN_VENV_DIR") # Pasar la línea original
        if [[ "$status" == "not_installed" || "$status" == "installed_update" ]]; then
            ((pending_count++))
        fi
    done < "$BI_REQUIREMENTS"
    
    # Si no hay nada que instalar, terminar
    if [ "$pending_count" -eq 0 ]; then
        mostrar_exito "Todos los paquetes ya están instalados y actualizados."
        deactivate
        
        # Crear alias para activar y desactivar el entorno
        crear_alias_pybin
        crear_alias_pyunbin
        
        echo -e "\n${WHITE}Para activar este entorno:${NC}"
        echo -e "1. Actualice su shell: ${GREEN}source ~/.bashrc${NC}"
        echo -e "2. Use el alias: ${GREEN}pybin${NC}"
        echo -e "\n${WHITE}Para desactivar el entorno:${NC}"
        echo -e "  Use el alias: ${GREEN}pyunbin${NC}"
        log "INFO" "Instalación del entorno por defecto completada con éxito"
        return
    fi
    
    # Mostrar cabecera para instalación
    echo -e "\n${WHITE}Instalando $pending_count paquetes pendientes:${NC}"
    
    # Contador para paquetes instalados
    local count=0
    
    # Leer línea por línea e instalar
    while IFS= read -r pkg_line || [ -n "$pkg_line" ]; do
        local pkg=${pkg_line%%#*} # Eliminar comentarios
        pkg=$(echo "$pkg" | xargs) # Limpiar espacios
        [[ -z "$pkg" ]] && continue # Saltar líneas vacías/comentadas

        local pkg_name=$(echo "$pkg" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr -d ' ')
        local status=$(check_package_status "$pkg_line" "$BIN_VENV_DIR") # Pasar la línea original

        if [[ "$status" == "not_installed" || "$status" == "installed_update" ]]; then
            ((count++))
            
            # Formato de progreso: [1/10] instalando numpy...
            echo -ne "${CYAN}[${count}/${pending_count}]${NC} ${pkg_name}... "
            log "DEBUG" "Instalando paquete: $pkg"
            
            if pip install "$pkg" >> "$LOG_FILE" 2>&1; then
                echo -e "${GREEN}✓${NC}"
                log "INFO" "Paquete $pkg_name instalado correctamente"
            else
                echo -e "${RED}✗${NC}"
                mostrar_error "Falló la instalación del paquete $pkg_name"
                log "ERROR" "Fallo en la instalación de $pkg_name: $(tail -n 10 "$LOG_FILE" | grep -v ERROR)"
                echo -e "\nRevise el archivo de log para más detalles: $LOG_FILE"
                deactivate
                exit 1
            fi
        fi
    done < "$BI_REQUIREMENTS"
    
    echo
    mostrar_exito "Instalación completada exitosamente."
    deactivate
    
    # Crear alias para activar y desactivar el entorno
    crear_alias_pybin
    crear_alias_pyunbin
    
    echo -e "\n${WHITE}Para activar este entorno:${NC}"
    echo -e "1. Actualice su shell: ${GREEN}source ~/.bashrc${NC}"
    echo -e "2. Use el alias: ${GREEN}pybin${NC}"
    echo -e "\n${WHITE}Para desactivar el entorno:${NC}"
    echo -e "  Use el alias: ${GREEN}pyunbin${NC}"
    log "INFO" "Instalación del entorno por defecto completada con éxito"
}

# Función para proporcionar instrucciones de activación
activate_venv() {
    local env_name="$1"
    
    if [ -z "$env_name" ]; then
        mostrar_error "Se requiere un nombre para el entorno."
        echo "Uso: $0 activate <nombre_entorno>"
        exit 1
    fi
    
    local env_path="$VENV_DIR/$env_name"
    log "INFO" "Solicitando activación del entorno: $env_name"
    
    if [ ! -d "$env_path" ]; then
        mostrar_error "El entorno '$env_name' no existe en $env_path"
        echo "Entornos disponibles:"
        list_venvs
        exit 1
    fi
    
    echo "Para activar este entorno, ejecute el siguiente comando:"
    mostrar_exito "source $env_path/bin/activate"
}

# Función para listar todos los entornos virtuales
list_venvs() {
    mostrar_info "Entornos virtuales disponibles:"
    log "INFO" "Listando entornos virtuales disponibles"
    
    if [ ! -d "$VENV_DIR" ] || [ -z "$(ls -A "$VENV_DIR" 2>/dev/null)" ]; then
        mostrar_advertencia "No hay entornos virtuales creados aún."
        return
    fi
    
    for env in "$VENV_DIR"/*; do
        if [ -d "$env" ] && [ -f "$env/bin/activate" ]; then
            echo "  * $(basename "$env")"
        fi
    done
}

# Función para eliminar entornos o paquetes
remove_venv() {
    local env_name="$1"
    local option="$2"
    local pkg_name="$3"
    
    if [ -z "$env_name" ]; then
        mostrar_error "Se requiere un nombre para el entorno."
        echo "Uso: $0 remove <nombre_entorno> [--package <paquete>]"
        exit 1
    fi
    
    local env_path="$VENV_DIR/$env_name"
    
    # Verificar si existe el entorno
    if [ ! -d "$env_path" ]; then
        mostrar_error "El entorno '$env_name' no existe en $env_path"
        echo "Entornos disponibles:"
        list_venvs
        exit 1
    fi
    
    # Si la opción es --package, eliminar un paquete específico
    if [[ "$option" == "--package" ]]; then
        if [ -z "$pkg_name" ]; then
            mostrar_error "Se requiere un nombre de paquete para eliminar."
            echo "Uso: $0 remove <nombre_entorno> --package <paquete>"
            exit 1
        fi
        
        log "INFO" "Solicitando eliminación del paquete: $pkg_name del entorno $env_name"
        
        # Activar el entorno
        source "$env_path/bin/activate" || {
            mostrar_error "No se pudo activar el entorno virtual."
            exit 1
        }
        
        # Verificar si el paquete está instalado
        if ! pip list | grep -i "^$pkg_name " > /dev/null 2>&1; then
            mostrar_error "El paquete '$pkg_name' no está instalado en este entorno."
            deactivate
            exit 1
        fi
        
        read -p "¿Está seguro de que desea eliminar el paquete '$pkg_name' del entorno '$env_name'? (s/N): " confirm
        if [[ "$confirm" =~ ^[Ss]$ ]]; then
            mostrar_info "Eliminando paquete $pkg_name del entorno $env_name..."
            echo -ne "${YELLOW}▶${NC} Desinstalando $pkg_name... "
            
            if pip uninstall -y "$pkg_name" >> "$LOG_FILE" 2>&1; then
                echo -e "${GREEN}✓${NC}"
                mostrar_exito "Paquete $pkg_name eliminado exitosamente."
                log "INFO" "Paquete $pkg_name eliminado del entorno $env_name con éxito"
            else
                echo -e "${RED}✗${NC}"
                mostrar_error "Falló la eliminación del paquete $pkg_name"
                log "ERROR" "Fallo al eliminar el paquete $pkg_name: $(tail -n 10 "$LOG_FILE" | grep -v ERROR)"
            fi
            
            deactivate
        else
            mostrar_info "Operación cancelada."
            log "INFO" "Eliminación del paquete $pkg_name cancelada por el usuario"
            deactivate
        fi
    else
        # Eliminar el entorno completo
        log "INFO" "Solicitando eliminación del entorno: $env_name"
    
        read -p "¿Está seguro de que desea eliminar el entorno '$env_name'? (s/N): " confirm
        if [[ "$confirm" =~ ^[Ss]$ ]]; then
            mostrar_info "Eliminando entorno virtual: $env_name"
            rm -rf "$env_path" || {
                mostrar_error "No se pudo eliminar el entorno virtual."
                exit 1
            }
            mostrar_exito "Entorno virtual eliminado exitosamente."
            log "INFO" "Entorno virtual $env_name eliminado con éxito"
        else
            mostrar_info "Operación cancelada."
            log "INFO" "Eliminación del entorno $env_name cancelada por el usuario"
        fi
    fi
}

# Función para mostrar la ayuda
mostrar_ayuda() {
    echo -e "
    ${WHITE}Uso:${NC} $0 {create|activate|list|remove|--install|--update|--autostart|help}
    
    ${WHITE}Comandos:${NC}
      ${CYAN}create${NC} <nombre_entorno> [archivo_requisitos]  Crear un nuevo entorno virtual
      ${CYAN}activate${NC} <nombre_entorno>                     Mostrar instrucciones de activación para un entorno
      ${CYAN}list${NC}                                          Listar todos los entornos virtuales disponibles
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