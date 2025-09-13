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
BACKUP_DIR="$USER_HOME/.local/share/nxcloud-backup/backups"

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
    echo "  --help                Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0                    # Crear backup automático"
    echo "  $0 --backup           # Crear backup automático"
    echo "  $0 --restore backup1  # Restaurar backup específico"
    echo "  $0 --list             # Listar backups disponibles"
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
