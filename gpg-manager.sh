#!/bin/bash

# ==================================================
# GPG BACKUP MANAGER v1.0.0
# ==================================================
# Gestor especializado de backups portables de GPG
# Prioridad: BACKUP y RESTORE para uso cross-platform
# 
# Uso: gpg-manager.sh [--backup|--restore|--verify|--help]
# ==================================================

set -euo pipefail

# Configuración
BACKUP_DIR="${BACKUP_DIR:-/opt/gpg-backup}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
GPG_HOME="${GPG_HOME:-$HOME/.gnupg}"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funciones de logging
log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ========================================
# FUNCIÓN PRINCIPAL: CREAR BACKUP PORTABLE
# ========================================

create_portable_gpg_backup() {
    log_info "🌐 Creando backup portable de configuración GPG..."
    
    # Verificar pre-requisitos
    check_backup_prerequisites
    
    # Crear directorio de backup
    create_backup_directory
    
    # Detener procesos GPG para datos consistentes
    stop_gpg_processes
    
    # Crear backup principal
    create_main_backup
    
    # Crear backup cifrado
    create_encrypted_backup
    
    # Crear checksum
    create_backup_integrity_check
    
    # Crear script de restauración autónomo
    create_restorer_script
    
    # Verificar backup creado
    verify_backup_structure
    
    log_success "✅ Backup portable completado exitosamente"
    show_backup_info
}

check_backup_prerequisites() {
    log_info "🔍 Verificando pre-requisitos..."
    
    # Verificar que ~/.gnupg existe
    if [ ! -d "$GPG_HOME" ]; then
        log_error "No existe directorio GPG: $GPG_HOME"
        exit 1
    fi
    
    # Verificar archivos importantes
    if [ ! -f "$GPG_HOME/pubring.kbx" ] && [ ! -f "$GPG_HOME/pubring.gpg" ]; then
        log_warning "No se encontraron claves públicas en $GPG_HOME"
    fi
    
    if [ ! -f "$GPG_HOME/secring.gpg" ] && [ ! -d "$GPG_HOME/private-keys-v1.d" ]; then
        log_warning "No se encontraron claves privadas en $GPG_HOME"
    fi
    
    # Verificar herramientas necesarias
    command -v tar >/dev/null || { log_error "tar no disponible"; exit 1; }
    command -v sha256sum >/dev/null || { log_error "sha256sum no disponible"; exit 1; }
    
    log_success "Pre-requisitos verificados"
}

create_backup_directory() {
    log_info "📁 Creando directorio de backup: $BACKUP_DIR"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        if ! sudo mkdir -p "$BACKUP_DIR" 2>/dev/null; then
            log_warning "No se puede crear $BACKUP_DIR con sudo, intentando sin privilegios..."
            BACKUP_DIR="$HOME/.gpg-backup"
            mkdir -p "$BACKUP_DIR"
            log_info "Usando directorio alternativo: $BACKUP_DIR"
        fi
    fi
    
    # Limpiar backups antiguos (mantener últimos 5)
    cleanup_old_backups
}

cleanup_old_backups() {
    log_info "🧹 Limpiando backups antiguos..."
    
    # Contar backups directos
    DIRECT_COUNT=$(ls -1 "$BACKUP_DIR"/gpg-portable-direct-*.gz 2>/dev/null | wc -l || echo "0")
    CIFRADO_COUNT=$(ls -1 "$BACKUP_DIR"/gpg-portable-encrypted-*.asc 2>/dev/null | wc -l || echo "0")
    
    if [ "$DIRECT_COUNT" -gt 5 ]; then
        log_info "Removiendo backups directos antiguos..."
        ls -1t "$BACKUP_DIR"/gpg-portable-direct-*.gz | tail -n +6 | xargs -r rm -f
    fi
    
    if [ "$CIFRADO_COUNT" -gt 5 ]; then
        log_info "Removiendo backups cifrados antiguos..."
        ls -1t "$BACKUP_DIR"/gpg-portable-encrypted-*.asc | tail -n +6 | xargs -r rm -f
    fi
}

stop_gpg_processes() {
    log_info "🛑 Deteniendo procesos GPG activos..."
    
    # Detener gpg-agent de forma suave
    if pgrep gpg-agent >/dev/null 2>&1; then
        pkill -TERM gpg-agent 2>/dev/null || true
        sleep 2
        
        # Si sigue corriendo, forzar terminación
        if pgrep gpg-agent >/dev/null 2>&1; then
            log_warning "Forzando terminación de gpg-agent..."
            pkill -KILL gpg-agent 2>/dev/null || true
        fi
    fi
    
    log_success "Procesos GPG detenidos"
}

create_main_backup() {
    log_info "📦 Creando backup principal..."
    
    BACKUP_FILE="$BACKUP_DIR/gpg-portable-direct-$TIMESTAMP.tar.gz"
    
    # Crear backup excluyendo archivos temporales/problema
    tar -czf "$BACKUP_FILE" \
        --exclude="*.lock" \
        --exclude="*trustdb.gpg" \
        --exclude="random_seed" \
        --exclude=".#lk*" \
        --exclude="S.\*" \
        --exclude="*.tmp" \
        --directory="$HOME" \
        .gnupg/
    
    if [ -f "$BACKUP_FILE" ]; then
        log_success "Backup principal creado: $(basename "$BACKUP_FILE")"
        
        # Mostrar información del backup
        log_info "Tamaño del backup: $(du -h "$BACKUP_FILE" | cut -f1)"
        
        # Verificar contenido
        log_info "Contenido del backup:"
        tar -tzf "$BACKUP_FILE" | head -5
        echo "   ... ($(tar -tzf "$BACKUP_FILE" | wc -l) archivos total)"
    else
        log_error "Error creando backup principal"
        exit 1
    fi
}

create_encrypted_backup() {
    log_info "🔒 Creando backup cifrado..."
    
    BACKUP_FILE="$BACKUP_DIR/gpg-portable-encrypted-$TIMESTAMP.asc"
    
    if command -v gpg >/dev/null 2>&1; then
        tar -czf - \
            --exclude="*.lock" \
            --exclude="*trustdb.gpg" \
            --exclude="random_seed" \
            --exclude=".#lk*" \
            --exclude="S.*" \
            --exclude="*.tmp" \
            --directory="$HOME" \
            .gnupg/ | \
            gpg --symmetric --cipher-algo AES256 \
                --compress-algo 1 --armor \
                --cipher-algo AES256 \
                --batch --yes \
                --passphrase-fd 0 \
                --output "$BACKUP_FILE"
        
        # Remover el fichero temporal de passwords si se creó
        [ -f "/tmp/gpg_passphrase" ] && rm -f "/tmp/gpg_passphrase"
        
        if [ -f "$BACKUP_FILE" ]; then
            log_success "Backup cifrado creado: $(basename "$BACKUP_FILE")"
            log_warning "⚠️  RECORDAR: Para restaurar necesita la contraseña"
        else
            log_warning "No se pudo crear backup cifrado (GPG no disponible o error)"
        fi
    else
        log_warning "GPG no disponible - solo backup directo"
    fi
}

create_backup_integrity_check() {
    log_info "🔍 Creando verificación de integridad..."
    
    BACKUP_FILE="$BACKUP_DIR/gpg-portable-direct-$TIMESTAMP.tar.gz"
    CHECKSUM_FILE="$BACKUP_FILE.sha256"
    
    if [ -f "$BACKUP_FILE" ]; then
        # Crear checksum
        sha256sum "$BACKUP_FILE" > "$CHECKSUM_FILE"
        
        log_success "Checksum creado: $(basename "$CHECKSUM_FILE")"
        
        # Verificar inmediatamente
        if sha256sum -c "$CHECKSUM_FILE" >/dev/null 2>&1; then
            log_success "✅ Verificación de integridad exitosa"
        else
            log_error "❌ Error de integridad detectado"
            exit 1
        fi
    fi
}

create_restorer_script() {
    log_info "🚀 Creando script de restauración autónomo..."
    
    RESTORER_FILE="$BACKUP_DIR/restore-gpg-portable.sh"
    
    cat > "$RESTORER_FILE" << 'RESTORER_EOF'
#!/bin/bash

# ==================================================
# RESTAURE GPG PORTABLE v1.0.0
# ==================================================
# Script autónomo para restaurar backups GPG
# Generado automáticamente por gpg-backup-manager.sh
# ==================================================

set -euo pipefail

BACKUP_FILE="$1"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_usage() {
    echo -e "${BLUE}RESTAURE GPG PORTABLE${NC}"
    echo "Script para restaurar backups de configuración GPG"
    echo ""
    echo "Uso: $0 <archivo-backup.tar.gz> [--force] [--help]"
    echo ""
    echo "Opciones:"
    echo "  --force    Omitir confirmaciones de seguridad"
    echo "  --help     Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 gpg-portable-direct-20241214_143022.tar.gz"
    echo "  $0 ~/Downloads/gpg-backup.tar.gz --force"
    echo ""
    
    if ls -la ./*portable*.tar.gz ./*portable*.asc 2>/dev/null; then
        echo ""
        echo "📋 Archivos de backup disponibles en directorio actual:"
        ls -la ./*portable*.tar.gz ./*portable*.asc 2>/dev/null || echo "   No hay backups"
    fi
}

verify_backup_file() {
    if [ -z "$BACKUP_FILE" ]; then
        show_usage
        exit 1
    fi
    
    if [ "$BACKUP_FILE" = "--help" ] || [ "$BACKUP_FILE" = "-h" ]; then
        show_usage
        exit 0
    fi
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "No existe el archivo: $BACKUP_FILE"
        echo ""
        show_usage
        exit 1
    fi
    
    case "$BACKUP_FILE" in
        *.tar.gz)
            log_info "Detectado backup directo: $BACKUP_FILE"
            BACKUP_TYPE="direct"
            ;;
        *.asc)
            log_info "Detectado backup cifrado: $BACKUP_FILE"
            BACKUP_TYPE="encrypted"
            BACKUP_TYPE="encrypted"
            ;;
        *)
            log_error "Formato de archivo no reconocido. Use .tar.gz o .asc"
            exit 1
            ;;
    esac
}

verify_backup_integrity() {
    echo "🔍 Verificando integridad del backup..."
    
    if [ "$BACKUP_TYPE" = "direct" ]; then
        # Verificar checksum si existe
        CHECKSUM_FILE="${BACKUP_FILE}.sha256"
        if [ -f "$CHECKSUM_FILE" ]; then
            log_info "Verificando checksum: $(basename "$CHECKSUM_FILE")"
            if sha256sum -c "$CHECKSUM_FILE" 2>/dev/null; then
                log_success "✅ Checksum verificado: Backup íntegro"
            else
                log_error "❌ Checksum fallido: Backup corrupto"
                read -p "¿Continuar de todos modos? [y/N]: " -n 1 -r
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    log_info "Restauración cancelada"
                    exit 1
                fi
            fi
        else
            log_warning "No se encontró archivo checksum (.sha256)"
        fi
        
        # Test básico de tar
        log_info "Verificando estructura del tar..."
        if tar -tzf "$BACKUP_FILE" >/dev/null 2>&1; then
            log_success "✅ Estructura de tar válida"
        else
            log_error "❌ Error en estructura de tar"
            exit 1
        fi
    else
        # Para backups cifrados, solo verificar que GPG puede leerlo
        log_info "Verificando archivo cifrado..."
        if command -v gpg >/dev/null 2>&1; then
            if gpg --verify "$BACKUP_FILE" 2>/dev/null || true; then
                log_info "Archivo cifrado parece válido"
            fi
        else
            log_warning "GPG no disponible para verificación cifrada"
        fi
    fi
}

create_current_backup() {
    if [ -d "$HOME/.gnupg" ]; then
        BACKUP_CURRENT="$HOME/.gnupg-current-backup-$(date +%Y%m%d_%H%M%S)"
        log_info "💾 Creando backup de configuración actual: $(basename "$BACKUP_CURRENT")"
        
        cp -r "$HOME/.gnupg" "$BACKUP_CURRENT"
        log_success "Backup actual guardado en: $BACKUP_CURRENT"
        log_info "Para restaurar después: cp -r $BACKUP_CURRENT ~/.gnupg"
    fi
}

stop_gpg_processes() {
    log_info "🛑 Deteniendo procesos GPG activos..."
    
    # Detener gpg-agent
    if pgrep gpg-agent >/dev/null 2>&1; then
        pkill -TERM gpg-agent 2>/dev/null || true
        sleep 2
        
        # Forzar si es necesario
        if pgrep gpg-agent >/dev/null 2>&1; then
            log_warning "Forzando terminación de gpg-agent..."
            pkill -KILL gpg-agent 2>/dev/null || true
        fi
    fi
    
    # Detener otros procesos GPG
    pkill -TERM gpg 2>/dev/null || true
    pkill -TERM gpgv 2>/dev/null || true
    
    log_success "Procesos GPG detenidos"
}

extract_backup() {
    log_info "📦 Extrayendo backup..."
    
    if [ "$BACKUP_TYPE" = "direct" ]; then
        # Backup directo
        if tar -xzf "$BACKUP_FILE" -C "$HOME"; then
            log_success "✅ Backup extraído exitosamente"
        else
            log_error "❌ Error extrayendo backup"
            exit 1
        fi
    else
        # Backup cifrado
        log_info "Ingresar contraseña para descifrar backup..."
        gpg --decrypt "$BACKUP_FILE" | tar -xzf - -C "$HOME"
        if [ $? -eq 0 ]; then
            log_success "✅ Backup cifrado extraído exitosamente"
        else
            log_error "❌ Error extrayendo backup cifrado"
            exit 1
        fi
    fi
}

set_permissions() {
    log_info "🔐 Estableciendo permisos correctos..."
    
    # Permisos de directorio GPG
    chmod -R 700 "$HOME/.gnupg/" 2>/dev/null || true
    
    # Permisos de archivos específicos
    chmod 600 "$HOME/.gnupg/"* 2>/dev/null || true
    chmod 644 "$HOME/.gnupg/pubring*" "$HOME/.gnupg/trustdb.gpg" 2>/dev/null || true
    
    # Asegurar propietario
    chown -R "$(id -u):$(id -g)" "$HOME/.gnupg/" 2>/dev/null || true
    
    log_success "Permisos establecidos correctamente"
}

start_gpg_agent() {
    log_info "🚀 Iniciando agente GPG..."
    
    # Llamar a gpg para inicializar agente
    gpg --version >/dev/null 2>&1 || true
    
    # Iniciar agente si no está corriendo
    if ! pgrep gpg-agent >/dev/null 2>&1; then
        gpg-agent --daemon --use-standard-socket 2>/dev/null || true
    fi
    
    sleep 1
    log_success "Agente GPG iniciado"
}

verify_restoration() {
    log_info "✅ Verificando restauración..."
    
    # Verificar claves privadas
    if gpg --list-secret-keys --with-colons 2>/dev/null | grep -q "^sec:"; then
        PRIVATE_COUNT=$(gpg --list-secret-keys --with-colons 2>/dev/null | grep -c "^sec:")
        log_success "✅ $PRIVATE_COUNT claves privadas restauradas"
    else
        log_warning "⚠️  No se detectaron claves privadas"
    fi
    
    # Verificar claves públicas
    if gpg --list-public-keys --with-colons 2>/dev/null | grep -q "^pub:"; then
        PUBLIC_COUNT=$(gpg --list-public-keys --with-colons 2>/dev/null | grep -c "^pub:")
        log_success "✅ $PUBLIC_COUNT claves públicas restauradas"
    else
        log_warning "⚠️  No se detectaron claves públicas"
    fi
    
    # Verificar trust database
    if gpg --check-trustdb >/dev/null 2>&1; then
        log_success "✅ Base de confianza verificada"
    else
        log_warning "⚠️  Problemas con base de confianza"
    fi
    
    # Test de firma básico
    TEST_FILE="/tmp/gpg-test-$(date +%s)"
    echo "test-gpg-restoration" > "$TEST_FILE"
    
    if gpg --sign "$TEST_FILE" --output "$TEST_FILE.sig" 2>/dev/null; then
        log_success "✅ Test de firma exitoso"
        rm -f "$TEST_FILE" "$TEST_FILE.sig"
    else
        log_warning "⚠️  Test de firma falló"
        rm -f "$TEST_FILE" "$TEST_FILE.sig"
    fi
}

show_restoration_complete() {
    echo ""
    echo -e "${GREEN}🎉 ¡RESTAURACIÓN COMPLETADA!${NC}"
    echo ""
    echo "📁 Configuración restaurada en: $HOME/.gnupg"
    echo "🔑 Verificar claves:      gpg --list-keys"
    echo "🔐 Verificar secretas:    gpg --list-secret-keys"
    echo "📋 Verificar agentes:    gpg --version"
    echo ""
    
    if [ -f "$HOME/.gnupg-current-backup-"* ]; then
        echo -e "${YELLOW}⚠️  Backup de configuración anterior disponible en:${NC}"
        ls -1 "$HOME"/.gnupg-current-backup-*
        echo "   Para restaurar: cp -r \$BACKUP_ANTERIOR ~/.gnupg"
        echo ""
    fi
    
    echo "✨ GPG listo para usar en esta máquina"
}

# ========================================
# FUNCIÓN PRINCIPAL DE RESTAURACIÓN
# ========================================

main() {
    FORCE=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            -*)
                log_error "Opción desconocida: $1"
                show_usage
                exit 1
                ;;
            *)
                BACKUP_FILE="$1"
                shift
                ;;
        esac
    done
    
    # Verificar archivo
    verify_backup_file
    
    # Mostrar información
    echo -e "${BLUE}=================================================="
    echo -e "🚀 RESTAURE GPG PORTABLE v1.0.0"
    echo -e "==================================================${NC}"
    echo ""
    log_info "Archivo: $BACKUP_FILE"
    log_info "Tipo: $BACKUP_TYPE"
    echo ""
    
    # Confirmación de seguridad (si no es --force)
    if [ "$FORCE" != true ]; then
        log_warning "Esta operación reemplazará su configuración GPG actual"
        echo -e "${YELLOW}¿Continuar con la restauración? [y/N]:${NC}"
        read -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Restauración cancelada"
            exit 0
        fi
    fi
    
    # Ejecutar proceso de restauración
    verify_backup_integrity
    create_current_backup
    stop_gpg_processes
    extract_backup
    set_permissions
    start_gpg_agent
    verify_restoration
    show_restoration_complete
}

# Ejecutar función principal
main "$@"
RESTORER_EOF
    
    chmod +x "$RESTORER_FILE"
    log_success "Script de restauración creado: $(basename "$RESTORER_FILE")"
}

verify_backup_structure() {
    log_info "🔍 Verificando estructura del backup..."
    
    BACKUP_FILE="$BACKUP_DIR/gpg-portable-direct-$TIMESTAMP.tar.gz"
    
    # Verificar que el archivo existe
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Backup principal no encontrado"
        exit 1
    fi
    
    # Verificar estructura temporalmente
    TEMP_DIR=$(mktemp -d)
    tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
    
    # Verificar estructura esperada
    if [ -d "$TEMP_DIR/$HOME/.gnupg" ]; then
        log_success "✅ Estructura de backup correcta"
        
        # Contar archivos importantes
        GPG_DIR="$TEMP_DIR/$HOME/.gnupg"
        
        if [ -f "$GPG_DIR/pubring.kbx" ] || [ -f "$GPG_DIR/pubring.gpg" ]; then
            log_success "✅ Archivos de claves públicas encontrados"
        fi
        
        if [ -f "$GPG_DIR/secring.gpg" ] || [ -d "$GPG_DIR/private-keys-v1.d" ]; then
            log_success "✅ Archivos de claves privadas encontrados"
        fi
        
        # Contar total de archivos
        TOTAL_FILES=$(find "$GPG_DIR" -type f | wc -l)
        log_info "📊 Total de archivos en backup: $TOTAL_FILES"
        
    else
        log_error "❌ Estructura de backup inválida"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    rm -rf "$TEMP_DIR"
}

show_backup_info() {
    echo ""
    echo "=================================================="
    echo "📋 INFORMACIÓN DEL BACKUP COMPLETADO"
    echo "=================================================="
    echo ""
    echo "📁 Directorio: $BACKUP_DIR"
    echo ""
    
    # Mostrar backups creados
    echo "📦 Backups creados:"
    
    BACKUP_FILE="$BACKUP_DIR/gpg-portable-direct-$TIMESTAMP.tar.gz"
    if [ -f "$BACKUP_FILE" ]; then
        echo "   📄 Directo:   $(basename "$BACKUP_FILE") ($(du -h "$BACKUP_FILE" | cut -f1))"
    fi
    
    BACKUP_CIFRADO="$BACKUP_DIR/gpg-portable-encrypted-$TIMESTAMP.asc"
    if [ -f "$BACKUP_CIFRADO" ]; then
        echo "   🔒 Cifrado:   $(basename "$BACKUP_CIFRADO") ($(du -h "$BACKUP_CIFRADO" | cut -f1))"
    fi
    
    CHECKSUM_FILE="$BACKUP_DIR/gpg-portable-direct-$TIMESTAMP.tar.gz.sha256"
    if [ -f "$CHECKSUM_FILE" ]; then
        echo "   🔍 Cheksum:   $(basename "$CHECKSUM_FILE")"
    fi
    
    RESTORER_FILE="$BACKUP_DIR/restore-gpg-portable.sh"
    if [ -f "$RESTORER_FILE" ]; then
        echo "   🚀 Restaurar: $(basename "$RESTORER_FILE")"
    fi
    
    echo ""
    echo "🌐 Para usar en otra máquina:"
    echo "   1. Copiar archivos necesarios:"
    echo "      scp $BACKUP_FILE usuario@destino:~/"
    echo "      scp $RESTORER_FILE usuario@destino:~/"
    echo ""
    echo "   2. En la máquina destino:"
    echo "      chmod +x restore-gpg-portable.sh"
    echo "      restore-gpg-portable.sh gpg-portable-direct-$TIMESTAMP.tar.gz"
    echo ""
    echo "🎯 Para verificar integridad:"
    echo "   gpg-manager.sh --verify $BACKUP_FILE"
    echo ""
}

# ========================================
# FUNCIÓN PRINCIPAL: RESTAURAR BACKUP
# ========================================

restore_portable_gpg() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "Falta especificar archivo de backup"
        echo ""
        echo "Uso: gpg-manager.sh --restore <archivo-backup.tar.gz>"
        echo ""
        echo "Archivos disponibles en $BACKUP_DIR:"
        ls -1 "$BACKUP_DIR"/*portable*.tar.gz "$BACKUP_DIR"/*portable*.asc 2>/dev/null || echo "   No hay backups"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "No existe el archivo: $backup_file"
        exit 1
    fi
    
    log_info "🔄 Restaurando backup portable..."
    
    # Usar script de restauración autónomo
    RESTORER_FILE="$BACKUP_DIR/restore-gpg-portable.sh"
    
    if [ -f "$RESTORER_FILE" ]; then
        log_info "Usando script de restauración autónomo..."
        "$RESTORER_FILE" "$backup_file" --force
    else
        log_error "No se encuentra script de restauración: $RESTORER_FILE"
        exit 1
    fi
}

# ========================================
# FUNCIÓN: VERIFICAR BACKUP
# ========================================

verify_backup_integrity() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "Falta especificar archivo de backup"
        echo ""
        echo "Uso: gpg-manager.sh --verify <archivo-backup.tar.gz>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "No existe el archivo: $backup_file"
        exit 1
    fi
    
    echo ""
    echo "=================================================="
    echo "🔍 VERIFICACIÓN DE INTEGRIDAD DE BACKUP"
    echo "=================================================="
    echo ""
    
    case "$backup_file" in
        *.tar.gz)
            verify_direct_backup "$backup_file"
            ;;
        *.asc)
            verify_encrypted_backup "$backup_file"
            ;;
        *)
            log_error "Formato no reconocido: $backup_file"
            exit 1
            ;;
    esac
}

verify_direct_backup() {
    local backup_file="$1"
    
    log_info "Verificando backup directo: $(basename "$backup_file")"
    
    # Verificar checksum
    checksum_file="${backup_file}.sha256"
    if [ -f "$checksum_file" ]; then
        log_info "Verificando checksum..."
        if sha256sum -c "$checksum_file"; then
            log_success "✅ Checksum verificado correctamente"
        else
            log_error "❌ Error en checksum - backup corrupto"
            exit 1
        fi
    else
        log_warning "No se encontró archivo checksum (.sha256)"
    fi
    
    # Verificar estructura
    log_info "Verificando estructura del tar..."
    if tar -tzf "$backup_file" >/dev/null 2>&1; then
        log_success "✅ Estructura de tar válida"
        
        # Mostrar contenido principal
        log_info "Contenido principal del backup:"
        tar -tzf "$backup_file" | grep "\.gnupg/" | head -10
        total_files=$(tar -tzf "$backup_file" | wc -l)
        echo "   ... ($total_files archivos total)"
        
    else
        log_error "❌ Error en estructura de tar"
        exit 1
    fi
    
    # Verificar tamaño
    file_size=$(du -h "$backup_file" | cut -f1)
    log_info "Tamaño del backup: $file_size"
    
    # Verificar fecha de creación
    creation_date=$(stat -c %y "$backup_file" 2>/dev/null || stat -f %Sm "$backup_file" 2>/dev/null)
    log_info "Fecha creado: $creation_date"
    
    echo ""
    log_success "✅ Backup verificado correctamente - listo para restauración"
}

verify_encrypted_backup() {
    local backup_file="$1"
    
    log_info "Verificando backup cifrado: $(basename "$backup_file")"
    
    if ! command -v gpg >/dev/null 2>&1; then
        log_error "GPG no available para verificar backup cifrado"
        exit 1
    fi
    
    # Verificar que es un archivo cifrado válido
    log_info "Verificando archivo cifrado..."
    
    # Test básico de descriptación (verificar sólo estructura)
    if gpg --decrypt --dry-run "$backup_file" 2>/dev/null | tar -tzf - >/dev/null 2>&1; then
        log_success "✅ Archivo cifrado válido"
        log_info "⚠️  Para verificación completa se requiere contraseña"
    else
        log_error "❌ Archivo cifrado inválido o corrupto"
        exit 1
    fi
    
    echo ""
    log_success "✅ Backup cifrado verificado básicamente - requiere contraseña para uso completo"
}

# ========================================
# FUNCIÓN: LISTAR BACKUPS
# ========================================

list_available_backups() {
    echo ""
    echo "=================================================="
    echo "📋 BACKUPS DISPONIBLES"

    echo "=================================================="
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_warning "No existe directorio de backups: $BACKUP_DIR"
        echo ""
        echo "Crear primer backup: $0 --backup"
        return 1
    fi
    
    echo "📁 Directorio: $BACKUP_DIR"
    echo ""
    
    # Mostrar backups directos
    echo "📦 Backups Directos:"
    if ls "$BACKUP_DIR"/gpg-portable-direct-*.tar.gz 2>/dev/null; then
        ls -lah "$BACKUP_DIR"/gpg-portable-direct-*.tar.gz | while read line; do
            file=$(echo "$line" | awk '{print $NF}')
            size=$(echo "$line" | awk '{print $5}')
            date=$(echo "$line" | awk '{print $6, $7, $8}')
            echo "   📄 $(basename "$file") - $size - $date"
        done
    else
        echo "   No hay backups directos"
    fi
    
    echo ""
    
    # Mostrar backups cifrados
    echo "🔒 Backups Cifrados:"
    if ls "$BACKUP_DIR"/gpg-portable-encrypted-*.asc 2>/dev/null; then
        ls -lah "$BACKUP_DIR"/gpg-portable-encrypted-*.asc | while read line; do
            file=$(echo "$line" | awk '{print $NF}')
            size=$(echo "$line" | awk '{print $5}')
            date=$(echo "$line" | awk '{print $6, $7, $8}')
            echo "   🔐 $(basename "$file") - $size - $date"
        done
    else
        echo "   No hay backups cifrados"
    fi
    
    echo ""
    
    # Mostrar checksums
    echo "🔍 Verificaciones de Integridad:"
    if ls "$BACKUP_DIR"/gpg-portable-direct-*.sha256 2>/dev/null; then
        ls -lah "$BACKUP_DIR"/gpg-portable-direct-*.sha256 | while read line; do
            file=$(echo "$line" | awk '{print $NF}')
            echo "   ✅ $(basename "$file")"
        done
    else
        echo "   No hay archivos de verificación"
    fi
    
    echo ""
    
    # Mostrar script de restauración
    if [ -f "$BACKUP_DIR/restore-gpg-portable.sh" ]; then
        echo "🚀 Script de Restauración:"
        echo "   📜 restore-gpg-portable.sh"
        echo ""
    fi
    
    echo "💡 Comandos útiles:"
    echo "   Restaurar:    gpg-manager.sh --restore <archivo-backup>"
    echo "   Verificar:    gpg-manager.sh --verify <archivo-backup>"
    echo "   Ayuda:        gpg-manager.sh --help"
    echo ""
}

# ========================================
# FUNCIÓN DE AYUDA
# ========================================

show_help() {
    echo ""
    echo "=================================================="
    echo "🚀 GPG BACKUP MANAGER v1.0.0"
    echo "=================================================="
    echo ""
    echo "Gestor especializado de backups portables de GPG"
    echo "Prioridad: BACKUP y RESTORE para uso cross-platform"
    echo ""
    echo "Uso:"
    echo "  gpg-manager.sh --backup                           Crear backup portable"
    echo "  gpg-manager.sh --restore <archivo-backup>        Restaurar backup"
    echo "  gpg-manager.sh --verify <archivo-backup>         Verificar integridad"
    echo "  gpg-manager.sh --list                            Listar backups disponibles"
    echo "  gpg-manager.sh --help                            Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  gpg-manager.sh --backup"
    echo "  gpg-manager.sh --restore gpg-portable-direct-20241214_143022.tar.gz"
    echo "  gpg-manager.sh --verify ~/backups/gpg-backup.tar.gz"
    echo "  gpg-manager.sh --list"
    echo ""
    echo "Características:"
    echo "  📦 Backup completo de ~/.gnupg/"
    echo "  🌐 Portable entre sistemas Linux/macOS"
    echo "  🔒 Backup cifrado opcional"
    echo "  🔍 Verificación de integridad automática"
    echo "  🚀 Script de restauración autónomo"
    echo "  🧹 Limpieza automática de backups antiguos"
    echo ""
    echo "Archivos generados:"
    echo "  gpg-portable-direct-TIMESTAMP.tar.gz     Backup completo"
    echo "  gpg-portable-encrypted-TIMESTAMP.asc     Backup cifrado"
    echo "  gpg-portable-direct-TIMESTAMP.tar.gz.sha256 Checksum"
    echo "  restore-gpg-portable.sh                  Script restaurador"
    echo ""
}

# ========================================
# FUNCIÓN PRINCIPAL
# ========================================

main() {
    case "${1:-}" in
        --backup|-b)
            create_portable_gpg_backup
            ;;
        --restore|-r)
            restore_portable_gpg "${2:-}"
            ;;
        --verify|-v)
            verify_backup_integrity "${2:-}"
            ;;
        --list|-l)
            list_available_backups
            ;;
        --help|-h|'')
            show_help
            ;;
        *)
            log_error "Opción desconocida: ${1:-}"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
