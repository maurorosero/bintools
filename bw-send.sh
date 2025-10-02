#!/bin/bash

# Script para enviar archivos o texto mediante Bitwarden CLI
# Autor: Mauro Rosero Pérez
# Website: https://mauro.rosero.one
# Versión: 1.0.0

set -euo pipefail

echo "DEBUG: Script iniciado"

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
EMAIL_RECIPIENTS=""

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
    --email EMAIL          Enviar por email a destinatario(s) (separados por comas)
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

    # Enviar por email
    $SCRIPT_NAME --text "Información confidencial" --email user@example.com

    # Enviar archivo por email a múltiples destinatarios
    $SCRIPT_NAME documento.pdf --email user1@example.com,user2@example.com

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

# Función para verificar dependencias
check_dependencies() {
    log "DEBUG" "Verificando dependencias..."
    local missing_deps=()
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Verificar SOPS
    if ! command -v sops &> /dev/null; then
        missing_deps+=("sops")
    fi
    
    # Verificar Bitwarden CLI
    if ! command -v bw &> /dev/null; then
        missing_deps+=("bw")
    fi
    
    # Mostrar dependencias faltantes con instrucciones específicas
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log "ERROR" "Dependencias faltantes: ${missing_deps[*]}"
        
        for dep in "${missing_deps[@]}"; do
            case $dep in
                "python3")
                    log "INFO" "Instala con: packages.sh --list base"
                    ;;
                "sops")
                    log "INFO" "Instala SOPS con: mozilla-sops.sh --install"
                    ;;
                "bw")
                    log "INFO" "Instala Bitwarden CLI con: packages.sh --list bwdn"
                    ;;
            esac
        done
        exit 1
    fi
}

# Función para verificar si bw está instalado (mantener compatibilidad)
check_bw_installed() {
    check_dependencies
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
    
    # Ejecutar comando: stderr va a la terminal (para el prompt), stdout se captura
    local result
    result=$(eval "$cmd" 2>/dev/tty)
    local exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        log "ERROR" "Error al crear send con Bitwarden (código: $exit_code)"
        log "ERROR" "Salida: $result"
        return 1
    fi
    
    # Guardar el resultado en una variable global para que main() pueda usarlo
    export BW_SEND_RESULT="$result"
    return 0
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
    
    # Ejecutar comando: stderr va a la terminal, stdout se captura
    local result
    result=$(eval "$cmd" 2>/dev/tty)
    local exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        log "ERROR" "Error al crear send con Bitwarden (código: $exit_code)"
        log "ERROR" "Salida: $result"
        return 1
    fi
    
    # Guardar el resultado en una variable global
    export BW_SEND_RESULT="$result"
    return 0
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

# Función para verificar configuración SMTP
check_smtp_config() {
    if [[ ! -f ~/secure/sops/mail/mail-config.yml ]]; then
        log "ERROR" "Configuración SMTP no encontrada: ~/secure/sops/mail/mail-config.yml"
        log "INFO" "Ejecuta: mail-config.py --interactive"
        exit 1
    fi
}

# Función para cargar configuración SMTP
load_smtp_config() {
    local config_file="$HOME/secure/sops/mail/mail-config.yml"
    
    # Desencriptar configuración con SOPS
    local config
    config=$(sops --decrypt "$config_file" 2>/dev/null)
    
    if [[ $? -ne 0 ]]; then
        log "ERROR" "Error al desencriptar configuración SMTP"
        log "INFO" "Verifica que SOPS esté configurado correctamente"
        exit 1
    fi
    
    # Extraer configuración SMTP usando Python
    python3 -c "
import yaml
import sys
import json

try:
    config = yaml.safe_load('''$config''')
    smtp = config['smtp']
    
    result = {
        'host': smtp['host'],
        'port': smtp['port'],
        'security': smtp['security'],
        'username': smtp['username'],
        'password': smtp['password'],
        'from_name': smtp['from']['name'],
        'from_email': smtp['from']['email']
    }
    
    print(json.dumps(result))
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# Función para enviar por email
send_email() {
    local result="$1"
    local recipients="$2"
    
    # Verificar configuración SMTP
    check_smtp_config
    
    # Cargar configuración
    local smtp_config
    smtp_config=$(load_smtp_config)
    
    if [[ $? -ne 0 ]]; then
        log "ERROR" "Error al cargar configuración SMTP"
        exit 1
    fi
    
    # Extraer URL del resultado
    local url
    url=$(echo "$result" | grep -o '"accessUrl":"[^"]*"' | sed 's/"accessUrl":"\([^"]*\)"/\1/')
    
    if [[ -z "$url" ]]; then
        log "ERROR" "No se pudo extraer la URL del send"
        return 1
    fi
    
    # Extraer fecha de expiración
    local expiration_date
    expiration_date=$(echo "$result" | grep -o '"expirationDate":"[^"]*"' | sed 's/"expirationDate":"\([^"]*\)"/\1/')
    
    # Formatear fecha de expiración si existe
    local expiration_text=""
    if [[ -n "$expiration_date" ]]; then
        # Convertir fecha ISO a formato legible
        expiration_text=$(date -d "$expiration_date" "+%d/%m/%Y a las %H:%M" 2>/dev/null || echo "$expiration_date")
    fi
    
    # Crear directorio de logs si no existe
    mkdir -p ~/.logs
    
    # Crear archivo temporal para el script Python
    local python_script=$(mktemp)
    cat > "$python_script" << 'EOF'
import smtplib
import json
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

try:
    # Cargar configuración
    smtp_config = json.loads(sys.argv[1])
    url = sys.argv[2]
    recipients = sys.argv[3].split(',')
    expiration_text = sys.argv[4]
    
    # Leer plantilla de email
    template_file = os.path.expanduser('~/secure/mail/email.bw.template')
    
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    else:
        # Plantilla por defecto (anti-spam)
        html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archivo Compartido</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; }
        .container { background: #ffffff; border: 1px solid #dddddd; border-radius: 8px; overflow: hidden; }
        .header { background: #175ddc; color: #ffffff; padding: 25px 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; font-weight: normal; }
        .header p { margin: 8px 0 0 0; font-size: 14px; opacity: 0.9; }
        .content { padding: 30px 25px; }
        .greeting { font-size: 16px; margin-bottom: 15px; color: #333333; }
        .description { font-size: 14px; margin-bottom: 25px; color: #666666; }
        .button-container { text-align: center; margin: 25px 0; }
        .button { display: inline-block; background: #175ddc; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: normal; font-size: 14px; }
        .info-section { background: #f8f9fa; border: 1px solid #e9ecef; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .info-section h3 { margin: 0 0 10px 0; color: #495057; font-size: 14px; font-weight: normal; }
        .info-section ul { margin: 0; padding-left: 20px; color: #495057; font-size: 13px; }
        .info-section li { margin-bottom: 3px; }
        .details { background: #e3f2fd; border: 1px solid #bbdefb; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .details h4 { margin: 0 0 8px 0; color: #1976d2; font-size: 13px; font-weight: normal; }
        .details p { margin: 0; color: #1976d2; font-size: 13px; }
        .footer { background: #f8f9fa; padding: 20px 25px; text-align: center; color: #6c757d; font-size: 12px; border-top: 1px solid #e9ecef; }
        .footer p { margin: 0; }
        .divider { height: 1px; background: #e9ecef; margin: 20px 0; }
        .contact-info { font-size: 12px; color: #6c757d; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Archivo Compartido</h1>
            <p>Has recibido un archivo compartido de forma segura</p>
        </div>
        <div class="content">
            <div class="greeting">Estimado/a destinatario,</div>
            <div class="description">Se ha compartido un archivo contigo de forma segura. Este archivo está protegido y solo tú puedes acceder a él mediante el enlace proporcionado.</div>
            <div class="button-container">
                <a href="{{LINK}}" class="button">Acceder al Archivo</a>
            </div>
            <div class="info-section">
                <h3>Información importante sobre este archivo:</h3>
                <ul>
                    <li>{{EXPIRES}}</li>
                    <li>No compartas este enlace con otras personas</li>
                    <li>El archivo está protegido con encriptación</li>
                    <li>Accede desde un dispositivo confiable</li>
                </ul>
            </div>
            <div class="details">
                <h4>Detalles del envío</h4>
                <p>Fecha de envío: {{DATE}} | Método: Bitwarden Send</p>
            </div>
            <div class="divider"></div>
            <div class="contact-info">Si no esperabas recibir este archivo o tienes problemas para acceder, contacta al remitente para obtener asistencia.</div>
        </div>
        <div class="footer">
            <p>Este mensaje fue enviado de forma segura usando Bitwarden Send</p>
        </div>
    </div>
</body>
</html>'''
    
    # Reemplazar variables en la plantilla
    html_content = html_content.replace('{{LINK}}', url)
    html_content = html_content.replace('{{DATE}}', datetime.now().strftime('%d/%m/%Y %H:%M'))
    
    # Reemplazar fecha de expiración si existe
    if expiration_text:
        html_content = html_content.replace('{{EXPIRES}}', f'El enlace expirará el {expiration_text}')
    else:
        html_content = html_content.replace('{{EXPIRES}}', '')
    
    # Crear mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Archivo Compartido - Acceso Seguro'
    msg['From'] = f"{smtp_config['smtp']['from']['name']} <{smtp_config['smtp']['from']['email']}>"
    msg['To'] = ', '.join(recipients)
    
    # Agregar contenido HTML
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    # Conectar y enviar
    if smtp_config['smtp']['security'] == 'tls':
        server = smtplib.SMTP(smtp_config['smtp']['host'], smtp_config['smtp']['port'])
        server.starttls()
    elif smtp_config['smtp']['security'] == 'ssl':
        server = smtplib.SMTP_SSL(smtp_config['smtp']['host'], smtp_config['smtp']['port'])
    else:
        server = smtplib.SMTP(smtp_config['smtp']['host'], smtp_config['smtp']['port'])
    
    server.login(smtp_config['smtp']['username'], smtp_config['smtp']['password'])
    server.send_message(msg)
    server.quit()
    
    print('SUCCESS')
    
except Exception as e:
    print(f'ERROR: {str(e)}')
    sys.exit(1)
EOF

    # Ejecutar script Python
    local python_result
    python_result=$(python3 "$python_script" "$smtp_config" "$url" "$recipients" "$expiration_text" 2>&1)
    local python_exit_code=$?
    
    # Limpiar archivo temporal
    rm -f "$python_script"
    
    # Verificar resultado
    if [[ $python_exit_code -ne 0 ]]; then
        log "ERROR" "Error al enviar email: $python_result"
        return 1
    fi
    
    if echo "$python_result" | grep -q "SUCCESS"; then
        log "SUCCESS" "Email enviado exitosamente a: $recipients"
        return 0
    else
        log "ERROR" "Error al enviar email: $python_result"
        return 1
    fi
}

# Función principal
main() {
    log "DEBUG" "Iniciando función main..."
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
                EMAIL_RECIPIENTS="$2"
                shift 2
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
    
    # Debug: mostrar variables después del parseo
    log "DEBUG" "Después del parseo:"
    log "DEBUG" "TEXT: '$TEXT'"
    log "DEBUG" "FILES: ${FILES[@]}"
    log "DEBUG" "SEND_METHOD: '$SEND_METHOD'"
    log "DEBUG" "EMAIL_RECIPIENTS: '$EMAIL_RECIPIENTS'"
    
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
    
    # Debug: mostrar variables
    log "DEBUG" "TEXT: '$TEXT'"
    log "DEBUG" "FILES: ${FILES[@]}"
    log "DEBUG" "Cantidad de archivos: ${#FILES[@]}"
    
    # Crear send
    if [[ -n "$TEXT" ]]; then
        if ! create_text_send "$TEXT"; then
            exit 1
        fi
    else
        # (lógica para archivos no cambia)
        if [[ ${#FILES[@]} -eq 1 ]]; then
            if ! create_file_send "${FILES[0]}"; then
                exit 1
            fi
        else
            # (bucle para múltiples archivos no cambia)
            for file in "${FILES[@]}"; do
                if create_file_send "$file"; then
                    log "SUCCESS" "Send creado para: $file"
                    echo "$BW_SEND_RESULT"
                else
                    log "ERROR" "Error al crear send para: $file"
                fi
            done
            exit 0
        fi
    fi

    # Extraer URL del resultado capturado
    local url
    url=$(echo "$BW_SEND_RESULT" | grep -o '"accessUrl":"[^"]*"' | sed 's/"accessUrl":"\([^"]*\)"/\1/')

    if [[ -z "$url" ]]; then
        log "ERROR" "No se pudo extraer la URL del send. Mostrando resultado completo:"
        echo "$BW_SEND_RESULT"
        exit 1
    fi

    log "SUCCESS" "Send creado exitosamente"
    log "INFO" "URL: $url"

    # Enviar según el método especificado
    if [[ "$SEND_METHOD" == "email" ]]; then
        if [[ -z "$EMAIL_RECIPIENTS" ]]; then
            log "ERROR" "Debes especificar destinatarios con --email"
            exit 1
        fi
        send_email "$BW_SEND_RESULT" "$EMAIL_RECIPIENTS"
    else
        # Para el método 'console', la URL ya se mostró arriba
        :
    fi
}

# Ejecutar función principal
main "$@"
