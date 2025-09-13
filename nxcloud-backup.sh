#!/usr/bin/env bash
# nxcloud-backup.sh - Script para crear, restaurar y gestionar backups de configuración de Nextcloud
#
# Copyright (C) 2025 Mauro Rosero Pérez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Configuración básica
USER_HOME="$HOME"
BACKUP_DIR="$USER_HOME/secure/nextcloud"

# Función para mostrar ayuda
show_help() {
    echo "🚀 NEXTCLOUD CONFIGURATION BACKUP & RESTORE"
    echo "=========================================="
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --backup              Crear backup de configuración (por defecto)"
    echo "  --restore NOMBRE      Restaurar backup específico"
    echo "  --list                Listar backups disponibles"
    echo "  --secure              Configurar sincronización de carpeta ~/secure"
    echo "  --help                Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0                    # Crear backup automático"
    echo "  $0 --backup           # Crear backup automático"
    echo "  $0 --restore backup1  # Restaurar backup específico"
    echo "  $0 --list             # Listar backups disponibles"
    echo "  $0 --secure           # Configurar sync de ~/secure con Nextcloud"
    echo ""
    echo "Ubicación de backups: $BACKUP_DIR"
}

# Función para crear backup
create_backup() {
    echo "🚀 CREANDO BACKUP DE CONFIGURACIÓN NEXTCLOUD"
    echo "============================================"
    
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    BACKUP_NAME="nextcloud_config_$TIMESTAMP"
    
    # Crear directorio de backup
    echo "📁 Creando directorio de backup..."
    mkdir -p "$BACKUP_DIR"
    
    # Verificar si existe configuración de Nextcloud
    if [[ ! -d "$USER_HOME/.config/Nextcloud" ]]; then
        echo "❌ No se encontró configuración de Nextcloud en ~/.config/Nextcloud/"
        echo "   El directorio no existe o está vacío."
        exit 1
    fi
    
    echo "✅ Directorio de configuración encontrado: ~/.config/Nextcloud/"
    echo ""
    
    # Crear directorio temporal
    TEMP_DIR=$(mktemp -d)
    echo "📁 Directorio temporal creado: $TEMP_DIR"
    
    # Copiar SOLO archivos de configuración
    echo "🔍 Copiando archivos de configuración..."
    cd "$USER_HOME/.config/Nextcloud"
    
    # Lista de archivos de configuración conocidos
    CONFIG_FILES=("nextcloud.cfg" "nextcloud-client.conf" "nextcloud.conf" "sync-exclude.lst")
    
    FILES_COPIED=0
    for file in "${CONFIG_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            echo "  ✓ Copiando $file"
            cp "$file" "$TEMP_DIR/"
            FILES_COPIED=$((FILES_COPIED + 1))
        else
            echo "  - No existe $file"
        fi
    done
    
    if [[ $FILES_COPIED -eq 0 ]]; then
        echo "⚠️  No se encontraron archivos de configuración conocidos"
        echo "   Verificando si hay otros archivos..."
        
        # Buscar cualquier archivo .conf, .cfg, .ini
        OTHER_FILES=$(find . -maxdepth 1 -type f \( -name "*.conf" -o -name "*.cfg" -o -name "*.ini" \) 2>/dev/null | head -10)
        
        if [[ -n "$OTHER_FILES" ]]; then
            echo "   Archivos encontrados:"
            echo "$OTHER_FILES" | while read -r file; do
                if [[ -f "$file" ]]; then
                    echo "  ✓ Copiando $(basename "$file")"
                    cp "$file" "$TEMP_DIR/"
                    FILES_COPIED=$((FILES_COPIED + 1))
                fi
            done
        fi
    fi
    
    echo ""
    echo "📊 Total de archivos copiados: $FILES_COPIED"
    
    if [[ $FILES_COPIED -eq 0 ]]; then
        echo "❌ No se pudo copiar ningún archivo de configuración"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    # Crear archivo de información
    echo "📝 Creando archivo de información..."
    cat > "$TEMP_DIR/backup-info.txt" << EOF
# Nextcloud Configuration Backup
# Generated: $(date)
# Backup Name: $BACKUP_NAME
# User: $USER
# Files: $FILES_COPIED
EOF
    
    # Crear backup comprimido
    BACKUP_FILE="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    echo ""
    echo "🗜️  Creando archivo comprimido: $BACKUP_FILE"
    
    cd "$TEMP_DIR"
    if tar -czf "$BACKUP_FILE" . 2>/dev/null; then
        echo "✅ BACKUP COMPLETADO EXITOSAMENTE!"
        
        # Mostrar información del backup
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo ""
        echo "📋 RESUMEN DEL BACKUP:"
        echo "   📁 Archivo: $BACKUP_FILE"
        echo "   📊 Tamaño: $BACKUP_SIZE"
        echo "   📋 Archivos: $FILES_COPIED"
        echo "   🕐 Fecha: $(date)"
        
        # Limpiar
        rm -rf "$TEMP_DIR"
        
        echo ""
        echo "🎉 Backup de configuración completado en: $BACKUP_FILE"
    else
        echo "❌ ERROR: Falló la creación del backup"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
}

# Función para listar backups
list_backups() {
    echo "📋 BACKUPS DISPONIBLES"
    echo "======================"
    echo ""
    
    if [[ ! -d "$BACKUP_DIR" ]] || [[ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]]; then
        echo "❌ No se encontraron backups en: $BACKUP_DIR"
        return 0
    fi
    
    local backup_count=0
    for backup_file in "$BACKUP_DIR"/*.tar.gz; do
        if [[ -f "$backup_file" ]]; then
            local backup_name=$(basename "$backup_file" .tar.gz)
            local backup_size=$(du -h "$backup_file" | cut -f1)
            local backup_date=$(stat -c %y "$backup_file" 2>/dev/null || stat -f %Sm "$backup_file" 2>/dev/null || echo "Fecha desconocida")
            
            echo "✅ $backup_name"
            echo "   📊 Tamaño: $backup_size"
            echo "   🕐 Fecha: $backup_date"
            echo ""
            ((backup_count++))
        fi
    done
    
    echo "📊 Total de backups: $backup_count"
}

# Función para restaurar backup
restore_backup() {
    local backup_name="$1"
    local backup_file="$BACKUP_DIR/${backup_name}.tar.gz"
    
    echo "🔄 RESTAURANDO BACKUP: $backup_name"
    echo "================================"
    echo ""
    
    if [[ ! -f "$backup_file" ]]; then
        echo "❌ ERROR: Backup no encontrado: $backup_file"
        echo "   Usa '$0 --list' para ver backups disponibles"
        exit 1
    fi
    
    echo "📁 Archivo de backup: $backup_file"
    echo "📊 Tamaño: $(du -h "$backup_file" | cut -f1)"
    echo ""
    
    # Crear directorio temporal para extraer
    local temp_dir=$(mktemp -d)
    echo "📁 Extrayendo backup a directorio temporal: $temp_dir"
    
    # Extraer backup
    if ! tar -xzf "$backup_file" -C "$temp_dir" 2>/dev/null; then
        echo "❌ ERROR: Falló la extracción del backup"
        rm -rf "$temp_dir"
        exit 1
    fi
    
    echo "✅ Backup extraído correctamente"
    
    # Mostrar contenido del backup
    echo ""
    echo "📋 Contenido del backup:"
    if [[ -f "$temp_dir/backup-info.txt" ]]; then
        cat "$temp_dir/backup-info.txt"
        echo ""
    fi
    
    # Confirmar restauración
    echo "⚠️  ADVERTENCIA: Esto sobrescribirá la configuración actual de Nextcloud"
    echo -n "¿Continuar con la restauración? (y/N): "
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ Restauración cancelada por el usuario"
        rm -rf "$temp_dir"
        exit 0
    fi
    
    echo ""
    echo "🔄 Restaurando archivos de configuración..."
    
    # Restaurar archivos de configuración
    local restored_files=0
    
    # Verificar si hay archivos en el directorio raíz del backup
    echo "🔍 Verificando contenido del backup..."
    ls -la "$temp_dir/"
    
    # Restaurar archivos de configuración (pueden estar en el directorio raíz)
    for config_file in "$temp_dir"/*; do
        if [[ -f "$config_file" ]]; then
            local filename=$(basename "$config_file")
            # No restaurar el archivo de información
            if [[ "$filename" != "backup-info.txt" ]]; then
                echo "  ✓ Restaurando $filename"
                cp "$config_file" "$USER_HOME/.config/Nextcloud/"
                restored_files=$((restored_files + 1))
            fi
        fi
    done
    
    # También verificar si hay un subdirectorio Nextcloud
    if [[ -d "$temp_dir/Nextcloud" ]]; then
        echo "  📁 Encontrado subdirectorio Nextcloud, restaurando archivos..."
        mkdir -p "$USER_HOME/.config/Nextcloud"
        
        for config_file in "$temp_dir/Nextcloud"/*; do
            if [[ -f "$config_file" ]]; then
                local filename=$(basename "$config_file")
                echo "  ✓ Restaurando $filename"
                cp "$config_file" "$USER_HOME/.config/Nextcloud/"
                restored_files=$((restored_files + 1))
            fi
        done
    fi
    
    # Limpiar
    rm -rf "$temp_dir"
    
    if [[ $restored_files -gt 0 ]]; then
        echo ""
        echo "✅ RESTAURACIÓN COMPLETADA EXITOSAMENTE!"
        echo "   📋 Archivos restaurados: $restored_files"
        echo "   📁 Ubicación: ~/.config/Nextcloud/"
    else
        echo ""
        echo "⚠️  ADVERTENCIA: No se restauraron archivos de configuración"
    fi
}

# Función para configurar sincronización de carpeta secure
configure_secure_sync() {
    echo "🔒 CONFIGURACIÓN DE SINCRONIZACIÓN SEGURA"
    echo "========================================"
    echo ""
    
    local secure_dir="$USER_HOME/secure"
    local config_file="$USER_HOME/.config/Nextcloud/nextcloud.cfg"
    
    # Verificar si Nextcloud está instalado y configurado
    if [[ ! -f "$config_file" ]]; then
        echo "❌ ERROR: Nextcloud no está configurado"
        echo "   No se encontró: $config_file"
        echo "   Primero configura una cuenta de Nextcloud en el cliente de escritorio"
        return 1
    fi
    
    echo "✅ Cliente Nextcloud encontrado: $config_file"
    
    # Verificar si la carpeta secure existe
    if [[ ! -d "$secure_dir" ]]; then
        echo "📁 Creando carpeta secure: $secure_dir"
        mkdir -p "$secure_dir"
    else
        echo "✅ Carpeta secure encontrada: $secure_dir"
    fi
    
    # Verificar configuración actual de forma más simple
    echo "🔍 Verificando configuración de sincronización..."
    
    # Buscar cualquier referencia a la carpeta secure
    local secure_configs=""
    if [[ -r "$config_file" ]]; then
        secure_configs=$(grep "localPath=${secure_dir}/" "$config_file" 2>/dev/null || true)
    fi
    
    if [[ -n "$secure_configs" ]]; then
        echo "✅ La carpeta ~/secure YA está sincronizada con Nextcloud:"
        echo "$secure_configs" | sed 's/.*localPath=/  ✓ /'
        echo ""
        echo "📝 La sincronización está configurada. Los backups en ~/secure/nextcloud se sincronizarán automáticamente."
        return 0
    fi
    
    echo "⚠️  La carpeta ~/secure no está sincronizada con Nextcloud"
    echo ""
    echo "🤖 CONFIGURACIÓN AUTOMÁTICA"
    echo "==========================="
    echo ""
    echo -n "¿Quieres que configure automáticamente la sincronización de ~/secure? (Y/n): "
    read -r auto_response
    
    if [[ "$auto_response" =~ ^[Nn]$ ]]; then
        echo ""
        echo "🔧 CONFIGURACIÓN MANUAL"
        echo "======================="
        echo ""
        echo "Para sincronizar ~/secure con Nextcloud manualmente:"
        echo ""
        echo "1. 📱 Abre el cliente de Nextcloud (icono en la bandeja del sistema)"
        echo "2. ⚙️  Ve a 'Configuración' → 'Sincronización'"
        echo "3. 📁 Haz clic en 'Agregar carpeta'"
        echo "4. 🗂️  Carpeta local: $secure_dir"
        echo "5. 🌐 Carpeta remota: /secure"
        echo "6. ✅ Confirma para agregar"
        echo ""
        return 0
    fi
    
    echo ""
    echo "🔧 Configurando sincronización automática..."
    
    # Crear backup de la configuración
    local config_backup="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Creando backup de configuración: $config_backup"
    cp "$config_file" "$config_backup"
    
    # Encontrar el próximo número de carpeta disponible
    local next_folder_num=$(grep -oE "0\\\\Folders\\\\[0-9]+" "$config_file" | grep -oE "[0-9]+" | sort -n | tail -1)
    next_folder_num=$((next_folder_num + 1))
    
    echo "📁 Agregando carpeta ~/secure como carpeta #$next_folder_num"
    
    # Generar un ID único para el journal (8 caracteres hex)
    local journal_id=$(openssl rand -hex 6 | cut -c1-12)
    
    # Agregar la nueva configuración de carpeta al archivo
    echo "" >> "$config_file"
    echo "0\\Folders\\${next_folder_num}\\ignoreHiddenFiles=false" >> "$config_file"
    echo "0\\Folders\\${next_folder_num}\\journalPath=.sync_${journal_id}.db" >> "$config_file"
    echo "0\\Folders\\${next_folder_num}\\localPath=${secure_dir}/" >> "$config_file"
    echo "0\\Folders\\${next_folder_num}\\paused=false" >> "$config_file"
    echo "0\\Folders\\${next_folder_num}\\targetPath=/secure" >> "$config_file"
    echo "0\\Folders\\${next_folder_num}\\version=2" >> "$config_file"
    echo "0\\Folders\\${next_folder_num}\\virtualFilesMode=off" >> "$config_file"
    
    echo "✅ Configuración agregada exitosamente!"
    echo ""
    echo "🔄 Reiniciando cliente Nextcloud para aplicar cambios..."
    
    # Cerrar y reiniciar Nextcloud
    if pgrep -x "nextcloud" > /dev/null; then
        echo "🛑 Cerrando cliente Nextcloud..."
        pkill -x "nextcloud" 2>/dev/null || true
        sleep 2
    fi
    
    echo "🚀 Iniciando cliente Nextcloud..."
    nohup nextcloud > /dev/null 2>&1 &
    sleep 1
    
    echo ""
    echo "✅ ¡CONFIGURACIÓN COMPLETADA!"
    echo "=========================="
    echo ""
    echo "📋 Resumen:"
    echo "  ✓ Carpeta local: $secure_dir/"
    echo "  ✓ Carpeta remota: /secure"
    echo "  ✓ Backups en: $secure_dir/nextcloud/"
    echo "  ✓ Cliente Nextcloud reiniciado"
    echo ""
    echo "📝 IMPORTANTE:"
    echo "  • La sincronización puede tardar unos minutos en iniciar"
    echo "  • Verifica en el cliente Nextcloud que aparezca la carpeta 'secure'"
    echo "  • Los backups creados se sincronizarán automáticamente"
    echo ""
    echo "🔍 Para verificar: ejecuta '$0 --secure' nuevamente"
}

# Procesamiento de argumentos
case "${1:-}" in
    --restore)
        if [[ -z "${2:-}" ]]; then
            echo "❌ ERROR: Debes especificar un nombre de backup para restaurar"
            echo "   Uso: $0 --restore NOMBRE_BACKUP"
            exit 1
        fi
        restore_backup "$2"
        ;;
    --list)
        list_backups
        ;;
    --secure)
        configure_secure_sync
        ;;
    --help|-h)
        show_help
        ;;
    --backup|"")
        create_backup
        ;;
    *)
        echo "❌ ERROR: Opción desconocida: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
