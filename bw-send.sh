#!/bin/bash

# Script para enviar archivos o texto mediante Bitwarden CLI
# Autor: Mauro Rosero Pérez
# Website: https://mauro.rosero.one
# Versión: 1.0.0

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables globales
SCRIPT_NAME="bw-send.sh"
DEFAULT_EXPIRATION="2"
SEND_METHOD="console"
EXPIRATION=""
PASSWORD=""
MAX_ACCESS_COUNT=""
NOTES=""
FILES=()
TEXT=""
BW_SESSION=""

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $SCRIPT_NAME [OPCIONES] [ARCHIVOS...]

Script para enviar archivos o texto mediante Bitwarden CLI

OPCIONES:
    -t, --text TEXT        Texto a enviar
    -e, --expiration DAYS  Días hasta expiración (1, 7, 30, etc.) [default: 2]
    -p, --password PASS   Contraseña para acceder al send
    -m, --max-access NUM   Número máximo de accesos
    -n, --notes NOTES      Notas adicionales
    --console              Mostrar URL en consola (default)
    --telegram             Enviar por Telegram (no implementado)
    --email                Enviar por email (no implementado)
    -h, --help             Mostrar esta ayuda y salir
    -v, --version          Mostrar versión y salir

EJEMPLOS:
    # Enviar texto
    $SCRIPT_NAME --text "Información confidencial"

    # Enviar archivo
    $SCRIPT_NAME documento.pdf

    # Enviar múltiples archivos
    $SCRIPT_NAME archivo1.txt archivo2.pdf

    # Enviar con contraseña y expiración
    $SCRIPT_NAME --text "Token secreto" --password "miPass123" --expiration 7d

    # Enviar archivo con máximo de accesos
    $SCRIPT_NAME config.json --max-access 5 --expiration 1d

NOTAS:
    - Si no se especifica --text, se asume que los argumentos son archivos
    - La expiración por defecto es 2 días
    - El máximo de accesos por defecto es 1
    - El método de envío por defecto es --console
EOF
}

# Función para mostrar versión
show_version() {
    echo "$SCRIPT_NAME v1.0.0"
    echo "Autor: Mauro Rosero Pérez"
    echo "Website: https://mauro.rosero.one"
}

# Función para logging
log() {
    local level="$1"
    shift
    local message="$*"
    
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
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac
}

# Función para verificar si bw está instalado
check_bw_installed() {
    if ! command -v bw >/dev/null 2>&1; then
        log "ERROR" "Bitwarden CLI (bw) no está instalado"
        log "INFO" "Instálalo con: sudo snap install bw"
        exit 1
    fi
}

# Función para verificar y configurar la sesión
check_bw_auth() {
    local status=$(bw status 2>/dev/null)
    if [[ -z "$status" ]]; then
        log "ERROR" "No se pudo obtener el estado de Bitwarden CLI"
        log "INFO" "Verifica que bw esté instalado y configurado correctamente"
        exit 1
    fi
    
    if echo "$status" | grep -q '"status":"unauthenticated"'; then
        log "ERROR" "No estás autenticado en Bitwarden CLI"
        log "INFO" "Autentícate con: bw login"
        exit 1
    fi
    
    log "INFO" "Bitwarden CLI está configurado correctamente"
    log "INFO" "Se te pedirá la contraseña maestra cuando sea necesario"
}

# Función para crear send con texto
create_text_send() {
    local text="$1"
    
    # Construir comando con opciones de línea de comandos
    local cmd="bw send"
    
    # Agregar opciones por defecto si no se especificaron
    if [[ -z "$EXPIRATION" ]]; then
        EXPIRATION="2"  # Por defecto 2 días
    fi
    cmd="$cmd -d $EXPIRATION"
    
    if [[ -z "$MAX_ACCESS_COUNT" ]]; then
        MAX_ACCESS_COUNT="1"  # Por defecto 1 acceso
    fi
    cmd="$cmd -a $MAX_ACCESS_COUNT"
    
    if [[ -n "$PASSWORD" ]]; then
        cmd="$cmd --password \"$PASSWORD\""
    fi
    
    if [[ -n "$NOTES" ]]; then
        cmd="$cmd --notes \"$NOTES\""
    fi
    
    # Agregar el texto al final
    cmd="$cmd \"$text\""
    
    log "INFO" "Creando send con texto..."
    log "INFO" "Comando: $cmd"
    
    local result
    result=$(eval "$cmd")
    
    log "DEBUG" "Resultado del comando: $result"
    echo "$result"
}

# Función para crear send con archivo
create_file_send() {
    local file="$1"
    
    # Verificar si el archivo existe
    if [[ ! -f "$file" ]]; then
        log "ERROR" "El archivo '$file' no existe"
        return 1
    fi
    
    # Construir comando con opciones de línea de comandos
    local cmd="bw send -f"
    
    # Agregar opciones por defecto si no se especificaron
    if [[ -z "$EXPIRATION" ]]; then
        EXPIRATION="2"  # Por defecto 2 días
    fi
    cmd="$cmd -d $EXPIRATION"
    
    if [[ -z "$MAX_ACCESS_COUNT" ]]; then
        MAX_ACCESS_COUNT="1"  # Por defecto 1 acceso
    fi
    cmd="$cmd -a $MAX_ACCESS_COUNT"
    
    if [[ -n "$PASSWORD" ]]; then
        cmd="$cmd --password \"$PASSWORD\""
    fi
    
    if [[ -n "$NOTES" ]]; then
        cmd="$cmd --notes \"$NOTES\""
    fi
    
    # Agregar el archivo al final
    cmd="$cmd \"$file\""
    
    log "INFO" "Creando send con archivo: $file"
    log "INFO" "Comando: $cmd"
    
    local result
    result=$(eval "$cmd")
    
    echo "$result"
}

# Función para procesar el resultado del send
process_send_result() {
    local result="$1"
    local url=""
    
    log "DEBUG" "Procesando resultado: $result"
    
    # Extraer URL del resultado JSON
    url=$(echo "$result" | grep -o '"accessUrl":"[^"]*"' | sed 's/"accessUrl":"\([^"]*\)"/\1/')
    
    if [[ -z "$url" ]]; then
        log "ERROR" "No se pudo extraer la URL del send"
        return 1
    fi
    
    log "SUCCESS" "Send creado exitosamente"
    echo
    echo "🔗 URL del Send:"
    echo "$url"
    echo
    
    # Mostrar información adicional
    local access_id=$(echo "$result" | grep -o '"accessId":"[^"]*"' | sed 's/"accessId":"\([^"]*\)"/\1/')
    local expiration=$(echo "$result" | grep -o '"expirationDate":"[^"]*"' | sed 's/"expirationDate":"\([^"]*\)"/\1/')
    
    if [[ -n "$access_id" ]]; then
        echo "🆔 Access ID: $access_id"
    fi
    
    if [[ -n "$expiration" ]]; then
        echo "⏰ Expira: $expiration"
    fi
    
    if [[ -n "$PASSWORD" ]]; then
        echo "🔐 Contraseña: $PASSWORD"
    fi
    
    echo
    log "INFO" "Comparte esta URL con el destinatario"
}

# Función para enviar por consola (default)
send_console() {
    local result="$1"
    process_send_result "$result"
}

# Función para enviar por Telegram (no implementado)
send_telegram() {
    log "WARNING" "Envío por Telegram no implementado aún"
    log "INFO" "Mostrando URL en consola..."
    process_send_result "$1"
}

# Función para enviar por email (no implementado)
send_email() {
    log "WARNING" "Envío por email no implementado aún"
    log "INFO" "Mostrando URL en consola..."
    process_send_result "$1"
}

# Función principal
main() {
    # Parsear argumentos primero para verificar si es --help o --version
    local temp_args=("$@")
    for arg in "${temp_args[@]}"; do
        if [[ "$arg" == "-h" || "$arg" == "--help" || "$arg" == "-v" || "$arg" == "--version" ]]; then
            # Mostrar ayuda o versión sin verificar autenticación
            if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
                show_help
            else
                show_version
            fi
            exit 0
        fi
    done
    
    # Verificar dependencias solo si no es ayuda/versión
    check_bw_installed
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--text)
                TEXT="$2"
                shift 2
                ;;
            -e|--expiration)
                EXPIRATION="$2"
                shift 2
                ;;
            -p|--password)
                PASSWORD="$2"
                shift 2
                ;;
            -m|--max-access)
                MAX_ACCESS_COUNT="$2"
                shift 2
                ;;
            -n|--notes)
                NOTES="$2"
                shift 2
                ;;
            --console)
                SEND_METHOD="console"
                shift
                ;;
            --telegram)
                SEND_METHOD="telegram"
                shift
                ;;
            --email)
                SEND_METHOD="email"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                show_version
                exit 0
                ;;
            -*)
                log "ERROR" "Opción desconocida: $1"
                show_help
                exit 1
                ;;
            *)
                FILES+=("$1")
                shift
                ;;
        esac
    done
    
    # Establecer expiración por defecto si no se especificó
    if [[ -z "$EXPIRATION" ]]; then
        EXPIRATION="$DEFAULT_EXPIRATION"
    fi
    
    # Verificar autenticación de Bitwarden
    check_bw_auth
    
    # Verificar que se proporcione contenido
    if [[ -z "$TEXT" && ${#FILES[@]} -eq 0 ]]; then
        log "ERROR" "Debes especificar texto (--text) o al menos un archivo"
        show_help
        exit 1
    fi
    
    # Crear send
    local result=""
    
    if [[ -n "$TEXT" ]]; then
        # Enviar texto
        result=$(create_text_send "$TEXT")
    else
        # Enviar archivo(s)
        if [[ ${#FILES[@]} -eq 1 ]]; then
            # Un solo archivo
            result=$(create_file_send "${FILES[0]}")
        else
            # Múltiples archivos - crear send para cada uno
            log "INFO" "Creando sends para ${#FILES[@]} archivo(s)..."
            for file in "${FILES[@]}"; do
                echo
                log "INFO" "Procesando: $file"
                result=$(create_file_send "$file")
                send_console "$result"
            done
            exit 0
        fi
    fi
    
    # Enviar según el método especificado
    case "$SEND_METHOD" in
        "console")
            send_console "$result"
            ;;
        "telegram")
            send_telegram "$result"
            ;;
        "email")
            send_email "$result"
            ;;
        *)
            log "ERROR" "Método de envío no válido: $SEND_METHOD"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
