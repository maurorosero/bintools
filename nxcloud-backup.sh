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
    echo "  --clean               Limpiar entradas duplicadas de ~/secure"
    echo "  --help                Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0                    # Crear backup automático"
    echo "  $0 --backup           # Crear backup automático"
    echo "  $0 --restore backup1  # Restaurar backup específico"
    echo "  $0 --list             # Listar backups disponibles"
    echo "  $0 --secure           # Configurar sync de ~/secure con Nextcloud"
    echo "  $0 --clean            # Limpiar duplicados de configuración"
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
    echo "🔧 CONFIGURACIÓN NECESARIA"
    echo "=========================="
    echo ""
    echo "ℹ️  NOTA: Nextcloud requiere configuración manual desde la interfaz gráfica."
    echo "   La configuración automática del archivo no es confiable."
    echo ""
    echo "📋 PASOS PARA CONFIGURAR ~/secure:"
    echo ""
    echo "1. 📱 Abre el cliente de Nextcloud:"
    echo "   • Busca el icono en la bandeja del sistema (área de notificaciones)"
    echo "   • O ejecuta: nextcloud &"
    echo ""
    echo "2. ⚙️  En el cliente de Nextcloud:"
    echo "   • Haz clic en el icono de configuración (⚙️)"
    echo "   • Ve a la pestaña 'Sincronización' o 'Folders'"
    echo ""
    echo "3. 📁 Agregar nueva carpeta:"
    echo "   • Busca el botón 'Agregar carpeta' o 'Add Folder Sync Connection'"
    echo "   • Haz clic para agregar una nueva sincronización"
    echo ""
    echo "4. 🗂️  Configurar rutas:"
    echo "   • Carpeta local: $secure_dir"
    echo "   • Carpeta remota: /secure"
    echo "   • Deja las otras opciones por defecto"
    echo ""
    echo "5. ✅ Confirmar:"
    echo "   • Haz clic en 'Agregar' o 'Add'"
    echo "   • Espera a que aparezca en la lista de carpetas sincronizadas"
    echo ""
    echo "💡 CONSEJOS:"
    echo "   • Si no ves el icono de Nextcloud, puede que necesites iniciarlo"
    echo "   • La carpeta /secure se creará automáticamente en tu servidor"
    echo "   • La sincronización puede tardar unos minutos en comenzar"
    echo ""
    echo -n "¿Quieres que abra el cliente de Nextcloud ahora? (Y/n): "
    read -r open_response
    
    if [[ ! "$open_response" =~ ^[Nn]$ ]]; then
        echo ""
        echo "🚀 Abriendo cliente de Nextcloud..."
        if command -v nextcloud >/dev/null 2>&1; then
            nextcloud &
            echo "✅ Cliente Nextcloud iniciado"
            echo "   Busca la ventana del cliente para continuar con la configuración"
        else
            echo "❌ No se pudo encontrar el comando 'nextcloud'"
            echo "   Busca manualmente el icono en la bandeja del sistema"
        fi
    fi
    
    echo ""
    echo "🔍 VERIFICACIÓN:"
    echo "   Una vez configurado, ejecuta '$0 --secure' para verificar"
    echo "   que la sincronización esté activa."
}

# Función para limpiar entradas duplicadas de secure
clean_secure_duplicates() {
    echo "🧹 LIMPIEZA DE ENTRADAS DUPLICADAS"
    echo "================================="
    echo ""
    
    local secure_dir="$USER_HOME/secure"
    local config_file="$USER_HOME/.config/Nextcloud/nextcloud.cfg"
    
    if [[ ! -f "$config_file" ]]; then
        echo "❌ ERROR: No se encontró el archivo de configuración"
        return 1
    fi
    
    echo "🔍 Buscando entradas duplicadas para ~/secure..."
    
    # Buscar todas las entradas de secure
    local secure_entries=$(grep -n "localPath=${secure_dir}/" "$config_file" | cut -d: -f1)
    local entry_count=$(echo "$secure_entries" | wc -l)
    
    if [[ $entry_count -le 1 ]]; then
        echo "✅ No se encontraron entradas duplicadas"
        return 0
    fi
    
    echo "⚠️  Se encontraron $entry_count entradas para ~/secure"
    echo ""
    echo "📋 Entradas encontradas:"
    grep -E "Folders\\\\[0-9]+\\\\localPath=${secure_dir}/" "$config_file" | sed 's/.*Folders\\\\\\([0-9]\\+\\).*/  • Carpeta #\\1/'
    echo ""
    echo -n "¿Quieres limpiar las entradas duplicadas dejando solo una? (Y/n): "
    read -r clean_response
    
    if [[ "$clean_response" =~ ^[Nn]$ ]]; then
        echo "✅ Se mantienen todas las entradas como están"
        return 0
    fi
    
    echo ""
    echo "🔧 Limpiando entradas duplicadas..."
    
    # Crear backup
    local backup_file="${config_file}.backup.cleanup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Creando backup: $backup_file"
    cp "$config_file" "$backup_file"
    
    # Encontrar la primera entrada (la que funciona)
    local first_folder_num=$(grep -E "Folders\\\\[0-9]+\\\\localPath=${secure_dir}/" "$config_file" | head -1 | sed 's/.*Folders\\\\\\([0-9]\\+\\).*/\\1/')
    
    echo "✅ Manteniendo carpeta #$first_folder_num (la primera/funcional)"
    
    # Remover todas las otras entradas de secure
    local temp_file=$(mktemp)
    local removing_folder=""
    local skip_lines=0
    
    while IFS= read -r line; do
        # Detectar inicio de una carpeta de secure que no es la primera
        if [[ "$line" =~ Folders\\\\([0-9]+)\\\\.*= ]] && [[ "$line" =~ localPath=${secure_dir}/ ]] && [[ "${BASH_REMATCH[1]}" != "$first_folder_num" ]]; then
            removing_folder="${BASH_REMATCH[1]}"
            echo "🗑️  Removiendo carpeta #$removing_folder"
            skip_lines=7  # Saltar las próximas 6 líneas de esta carpeta
            continue
        fi
        
        # Si estamos removiendo una carpeta, saltar líneas relacionadas
        if [[ -n "$removing_folder" ]] && [[ "$line" =~ Folders\\\\${removing_folder}\\\\ ]]; then
            ((skip_lines--))
            if [[ $skip_lines -le 0 ]]; then
                removing_folder=""
            fi
            continue
        fi
        
        # Si no estamos saltando líneas, mantener la línea
        if [[ $skip_lines -le 0 ]]; then
            echo "$line" >> "$temp_file"
        else
            ((skip_lines--))
        fi
    done < "$config_file"
    
    # Reemplazar el archivo original
    mv "$temp_file" "$config_file"
    
    echo "✅ Limpieza completada!"
    echo ""
    echo "📋 Resumen:"
    echo "  ✓ Entrada mantenida: Carpeta #$first_folder_num"
    echo "  ✓ Entradas removidas: $(($entry_count - 1))"
    echo "  ✓ Backup creado: $backup_file"
    echo ""
    echo "🔄 Es recomendable reiniciar Nextcloud para aplicar los cambios"
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
    --clean)
        clean_secure_duplicates
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
