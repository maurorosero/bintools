#!/bin/bash

# Script para corregir problemas de locale en sistemas Debian/Ubuntu
# Funciona tanto local como remotamente
# Autor: Mauro Rosero Pérez
# Proyecto: bintools

set -euo pipefail

# Colores modernos y elegantes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Símbolos modernos
CHECKMARK='✅'
CROSSMARK='❌'
WARNING='⚠️'
INFO='ℹ️'
ROCKET='🚀'
GEAR='⚙️'
GLOBE='🌐'
SHIELD='🛡️'
SPARKLES='✨'

# Función de logging moderna y elegante
log() {
    local level="$1"
    shift
    local message="$*"
    
    case "$level" in
        "INFO")
            echo -e "${CYAN}${INFO}${NC} ${message}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}${CHECKMARK}${NC} ${message}"
            ;;
        "WARNING")
            echo -e "${YELLOW}${WARNING}${NC} ${message}"
            ;;
        "ERROR")
            echo -e "${RED}${CROSSMARK}${NC} ${message}"
            ;;
        "STEP")
            echo -e "${PURPLE}${GEAR}${NC} ${message}"
            ;;
        "HEADER")
            echo -e "${WHITE}${ROCKET}${NC} ${message}"
            ;;
        *)
            echo -e "${GRAY}[$level]${NC} ${message}"
            ;;
    esac
}

# Función para ejecutar comandos con sudo inteligente
run_with_sudo() {
    local cmd="$1"
    local description="$2"
    
    log "INFO" "${description}..."
    
    # Verificar si ya tenemos permisos sudo
    if sudo -n true 2>/dev/null; then
        # Ya tenemos permisos, ejecutar directamente
        sudo $cmd
    else
        # Solicitar permisos una sola vez
        log "WARNING" "Se requieren permisos de administrador"
        sudo $cmd
    fi
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES] [HOST]

DESCRIPCIÓN:
    Script para corregir problemas de locale en sistemas Debian/Ubuntu.
    Resuelve errores como "Can't set locale" y "Setting locale failed".

OPCIONES:
    -r, --remote HOST     Ejecutar en servidor remoto via SSH
    -l, --list            Listar locales disponibles
    -g, --generate        Generar locales (requiere sudo)
    -c, --check           Solo verificar configuración actual
    -f, --fix             Corregir configuración (requiere sudo)
    -a, --all             Ejecutar todas las correcciones
    -h, --help            Mostrar esta ayuda

EJEMPLOS:
    # Verificar configuración local
    $0 --check

    # Corregir configuración local
    $0 --fix

    # Ejecutar todas las correcciones localmente
    $0 --all

    # Verificar configuración remota
    $0 --remote user@server --check

    # Corregir configuración remota
    $0 --remote user@server --fix

    # Listar locales disponibles
    $0 --list

REQUISITOS:
    - Sistema Debian/Ubuntu
    - locales package instalado
    - Para correcciones: permisos sudo

EOF
}

# Función para verificar si locales está instalado
check_locales_package() {
    if ! dpkg -l | grep -q "^ii.*locales "; then
        log "WARNING" "Package 'locales' no está instalado"
        log "INFO" "Instalando locales package..."
        
        # Usar función inteligente de sudo
        run_with_sudo "apt-get update" "Actualizando repositorios"
        run_with_sudo "apt-get install -y locales" "Instalando package locales"
    else
        log "SUCCESS" "Package 'locales' está instalado"
    fi
}

# Función para listar locales disponibles
list_locales() {
    log "HEADER" "Locales disponibles en el sistema"
    echo
    
    if command -v locale >/dev/null 2>&1; then
        echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        locale -a | sort | column -c 80 | sed 's/^/  /'
        echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    else
        log "WARNING" "Comando 'locale' no disponible"
    fi
    
    echo
    log "HEADER" "Configuración actual de locales"
    echo -e "${GRAY}┌─────────────────────────────────────────────────────────────────────────────────┐${NC}"
    printf "${GRAY}│${NC} %-20s ${GRAY}│${NC} %-50s ${GRAY}│${NC}\n" "Variable" "Valor"
    echo -e "${GRAY}├─────────────────────────────────────────────────────────────────────────────────┤${NC}"
    printf "${GRAY}│${NC} %-20s ${GRAY}│${NC} %-50s ${GRAY}│${NC}\n" "LANG" "${LANG}"
    printf "${GRAY}│${NC} %-20s ${GRAY}│${NC} %-50s ${GRAY}│${NC}\n" "LC_ALL" "${LC_ALL:-unset}"
    printf "${GRAY}│${NC} %-20s ${GRAY}│${NC} %-50s ${GRAY}│${NC}\n" "LC_TIME" "${LC_TIME}"
    printf "${GRAY}│${NC} %-20s ${GRAY}│${NC} %-50s ${GRAY}│${NC}\n" "LC_MONETARY" "${LC_MONETARY}"
    printf "${GRAY}│${NC} %-20s ${GRAY}│${NC} %-50s ${GRAY}│${NC}\n" "LANGUAGE" "${LANGUAGE:-unset}"
    echo -e "${GRAY}└─────────────────────────────────────────────────────────────────────────────────┘${NC}"
}

# Función para generar locales
generate_locales() {
    log "STEP" "Generando locales del sistema"
    
    # Verificar si locales está instalado
    check_locales_package
    
    # Generar locales comunes
    local common_locales=(
        "en_US.UTF-8"
        "es_ES.UTF-8"
        "es_PA.UTF-8"
        "C.UTF-8"
    )
    
    log "INFO" "Configurando locales comunes..."
    echo -e "${GRAY}┌─ Locales a configurar ──────────────────────────────────────────────────────────┐${NC}"
    for locale in "${common_locales[@]}"; do
        printf "${GRAY}│${NC} ${CYAN}${SPARKLES}${NC} %-60s ${GRAY}│${NC}\n" "$locale"
    done
    echo -e "${GRAY}└───────────────────────────────────────────────────────────────────────────────────┘${NC}"
    
    for locale in "${common_locales[@]}"; do
        if grep -q "^# $locale" /etc/locale.gen 2>/dev/null; then
            log "INFO" "Habilitando $locale..."
            run_with_sudo "sed -i \"s/^# $locale/$locale/\" /etc/locale.gen" "Habilitando $locale"
        else
            log "INFO" "Agregando $locale..."
            echo "$locale UTF-8" | run_with_sudo "tee -a /etc/locale.gen" "Agregando $locale"
        fi
    done
    
    # Regenerar locales
    log "INFO" "Regenerando locales (esto puede tomar un momento)..."
    run_with_sudo "locale-gen" "Regenerando locales del sistema"
    
    log "SUCCESS" "Locales generados exitosamente"
}

# Función para verificar configuración actual
check_locale_config() {
    log "INFO" "Verificando configuración de locale..."
    echo
    
    # Verificar variables de entorno
    log "INFO" "Variables de entorno actuales:"
    echo "LANG=$LANG"
    echo "LC_ALL=${LC_ALL:-unset}"
    echo "LANGUAGE=${LANGUAGE:-unset}"
    echo
    
    # Verificar si el locale está disponible
    if [[ -n "$LANG" && "$LANG" != "C" ]]; then
        if locale -a | grep -q "^$LANG$"; then
            log "SUCCESS" "Locale $LANG está disponible"
        else
            log "WARNING" "Locale $LANG no está disponible en el sistema"
        fi
    else
        log "WARNING" "LANG está configurado como 'C' o vacío"
    fi
    
    # Verificar archivos de configuración
    log "INFO" "Verificando archivos de configuración..."
    
    if [[ -f "/etc/default/locale" ]]; then
        log "INFO" "Contenido de /etc/default/locale:"
        cat /etc/default/locale | grep -v "^#" | grep -v "^$"
    else
        log "WARNING" "/etc/default/locale no existe"
    fi
    
    echo
    if [[ -f "$HOME/.bashrc" ]]; then
        if grep -q "export LANG\|export LC_" "$HOME/.bashrc"; then
            log "INFO" "Configuraciones de locale en ~/.bashrc encontradas:"
            grep "export LANG\|export LC_" "$HOME/.bashrc"
        else
            log "INFO" "No hay configuraciones de locale en ~/.bashrc"
        fi
    fi
    
    # Verificar si hay problemas
    if [[ "$LANG" == "C" || -z "$LANG" ]]; then
        log "WARNING" "Configuración de locale puede estar causando problemas"
        return 1
    else
        log "SUCCESS" "Configuración de locale parece correcta"
        return 0
    fi
}

# Función para corregir configuración
fix_locale_config() {
    log "STEP" "Corrigiendo configuración de locale"
    
    # Detectar locale preferido
    local preferred_locale=""
    
    # Intentar detectar desde el sistema
    if command -v locale >/dev/null 2>&1; then
        if locale -a | grep -q "es_PA.UTF-8"; then
            preferred_locale="es_PA.UTF-8"
        elif locale -a | grep -q "es_ES.UTF-8"; then
            preferred_locale="es_ES.UTF-8"
        elif locale -a | grep -q "en_US.UTF-8"; then
            preferred_locale="en_US.UTF-8"
        else
            preferred_locale="C.UTF-8"
        fi
    else
        preferred_locale="C.UTF-8"
    fi
    
    echo -e "${GRAY}┌─ Locale detectado ───────────────────────────────────────────────────────────────┐${NC}"
    printf "${GRAY}│${NC} ${GREEN}${CHECKMARK}${NC} %-60s ${GRAY}│${NC}\n" "$preferred_locale"
    echo -e "${GRAY}└───────────────────────────────────────────────────────────────────────────────────┘${NC}"
    
    # Configurar variables de entorno para la sesión actual
    export LANG="$preferred_locale"
    export LC_ALL="$preferred_locale"
    export LANGUAGE="$preferred_locale"
    
    # Configurar sistema completo
    log "INFO" "Configurando locale del sistema..."
    
    # Crear/actualizar /etc/default/locale
    cat << EOF | run_with_sudo "tee /etc/default/locale" "Configurando /etc/default/locale"
LANG="$preferred_locale"
LC_ALL="$preferred_locale"
LANGUAGE="$preferred_locale"
EOF
    
    # Configurar para el usuario actual
    log "INFO" "Configurando locale para usuario actual..."
    
    # Agregar a .bashrc si no existe
    if ! grep -q "export LANG=" "$HOME/.bashrc" 2>/dev/null; then
        {
            echo ""
            echo "# Configuración de locale"
            echo "export LANG=\"$preferred_locale\""
            echo "export LC_ALL=\"$preferred_locale\""
            echo "export LANGUAGE=\"$preferred_locale\""
        } >> "$HOME/.bashrc"
        log "SUCCESS" "Configuración agregada a ~/.bashrc"
    else
        log "INFO" "Configuración ya existe en ~/.bashrc"
    fi
    
    # Configurar para el perfil del sistema
    log "INFO" "Configurando perfil del sistema..."
    cat << EOF | run_with_sudo "tee /etc/environment" "Configurando /etc/environment"
LANG="$preferred_locale"
LC_ALL="$preferred_locale"
LANGUAGE="$preferred_locale"
EOF
    
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "SUCCESS" "Configuración de locale aplicada exitosamente"
    log "INFO" "Los cambios tomarán efecto en la próxima sesión"
    log "INFO" "Para aplicar inmediatamente, ejecuta: ${CYAN}source ~/.bashrc${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Función para ejecutar todas las correcciones
run_all_fixes() {
    echo -e "${PURPLE}${ROCKET}${NC} ${WHITE}Iniciando corrección completa de locales${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # 1. Verificar configuración actual
    log "HEADER" "PASO 1: Verificando configuración actual"
    check_locale_config
    echo
    
    # 2. Listar locales disponibles
    log "HEADER" "PASO 2: Locales disponibles en el sistema"
    list_locales
    echo
    
    # 3. Generar locales si es necesario
    log "HEADER" "PASO 3: Generando locales del sistema"
    generate_locales
    echo
    
    # 4. Corregir configuración
    log "HEADER" "PASO 4: Corrigiendo configuración"
    fix_locale_config
    echo
    
    # 5. Verificación final
    log "HEADER" "PASO 5: Verificación final"
    check_locale_config
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        log "SUCCESS" "Todas las correcciones aplicadas exitosamente"
        log "INFO" "Reinicia tu terminal o ejecuta: ${CYAN}source ~/.bashrc${NC}"
        echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    else
        log "WARNING" "Algunas configuraciones pueden necesitar ajuste manual"
    fi
}

# Función para ejecutar comando remoto
run_remote() {
    local host="$1"
    shift
    local args="$*"
    
    log "INFO" "Ejecutando en servidor remoto: $host"
    log "INFO" "Argumentos: $args"
    
    # Copiar script al servidor remoto
    local script_name=$(basename "$0")
    local remote_script="/tmp/$script_name"
    
    log "INFO" "Copiando script al servidor remoto..."
    scp "$0" "$host:$remote_script"
    
    # Ejecutar en servidor remoto
    log "INFO" "Ejecutando script en servidor remoto..."
    ssh "$host" "chmod +x $remote_script && $remote_script $args"
    
    # Limpiar script remoto
    ssh "$host" "rm -f $remote_script"
    
    log "SUCCESS" "Comando ejecutado en servidor remoto"
}

# Función principal
main() {
    local remote_host=""
    local action=""
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--remote)
                remote_host="$2"
                shift 2
                ;;
            -l|--list)
                action="list"
                shift
                ;;
            -g|--generate)
                action="generate"
                shift
                ;;
            -c|--check)
                action="check"
                shift
                ;;
            -f|--fix)
                action="fix"
                shift
                ;;
            -a|--all)
                action="all"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                if [[ -z "$remote_host" && -z "$action" ]]; then
                    remote_host="$1"
                else
                    log "ERROR" "Argumento desconocido: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Si no se especifica acción, mostrar ayuda
    if [[ -z "$action" ]]; then
        log "ERROR" "No se especificó ninguna acción"
        show_help
        exit 1
    fi
    
    # Ejecutar acción remota o local
    if [[ -n "$remote_host" ]]; then
        run_remote "$remote_host" "--$action"
    else
        case "$action" in
            "list")
                list_locales
                ;;
            "generate")
                generate_locales
                ;;
            "check")
                check_locale_config
                ;;
            "fix")
                fix_locale_config
                ;;
            "all")
                run_all_fixes
                ;;
            *)
                log "ERROR" "Acción desconocida: $action"
                exit 1
                ;;
        esac
    fi
}

# Ejecutar función principal
main "$@"
