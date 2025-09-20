# Guía: Sincronizar Contexto de Cursor con Nextcloud

> **📖 [← Volver al README principal](../README.md)**

## Descripción

Esta guía te permite sincronizar automáticamente el contexto de IA y configuraciones de Cursor entre múltiples equipos usando Nextcloud.

## ¿Qué se sincroniza?

- ✅ Historial de conversaciones con IA
- ✅ Contexto de proyectos guardados
- ✅ Sesiones de chat/edición activas
- ✅ Configuraciones personalizadas
- ✅ Puntos de control de recuperación

## Requisitos Previos

- Nextcloud instalado y configurado en ambos equipos
- Cliente de Nextcloud funcionando
- Cursor instalado en ambos equipos

## Configuración Paso a Paso

### Paso 1: Preparar el Directorio de Sincronización

En **AMBOS equipos**, ejecuta:

```bash
# Crear directorio para sincronización
mkdir -p ~/secure/cursor/sync

# Crear directorio de respaldo local
mkdir -p ~/secure/cursor/backup
```

### Paso 2: Configurar Nextcloud

1. **Abrir Nextcloud Client**
2. **Ir a Settings > Folder Sync**
3. **Agregar nueva carpeta:**
   - **Local folder:** `~/secure/cursor/sync`
   - **Remote folder:** `cursor-sync` (en tu servidor Nextcloud)
4. **Aplicar configuración**

### Paso 3: Configurar Sincronización Automática

#### Opción A: Sincronización Manual (Recomendada para empezar)

**Script de sincronización (`~/bin/cursor-sync.sh`):**

```bash
#!/bin/bash

# Configuración
CURSOR_CONFIG="$HOME/.config/Cursor/User"
SYNC_DIR="$HOME/Nextcloud/cursor-sync"
BACKUP_DIR="$HOME/secure/cursor-backup"

# Crear directorios si no existen
mkdir -p "$SYNC_DIR" "$BACKUP_DIR"

# Función para sincronizar
sync_cursor() {
    echo "🔄 Sincronizando contexto de Cursor..."
    
    # Crear respaldo
    timestamp=$(date +%Y%m%d_%H%M%S)
    tar -czf "$BACKUP_DIR/cursor-backup-$timestamp.tar.gz" "$CURSOR_CONFIG" 2>/dev/null
    
    # Sincronizar archivos críticos
    cp "$CURSOR_CONFIG/globalStorage/storage.json" "$SYNC_DIR/" 2>/dev/null
    cp "$CURSOR_CONFIG/globalStorage/state.vscdb" "$SYNC_DIR/" 2>/dev/null
    
    # Sincronizar directorio de recuperación
    if [ -d "$CURSOR_CONFIG/globalStorage/anysphere.cursor-retrieval" ]; then
        cp -r "$CURSOR_CONFIG/globalStorage/anysphere.cursor-retrieval" "$SYNC_DIR/"
    fi
    
    echo "✅ Sincronización completada"
}

# Función para restaurar
restore_cursor() {
    echo "📥 Restaurando contexto de Cursor..."
    
    # Verificar que existe contenido en sync
    if [ ! -f "$SYNC_DIR/storage.json" ]; then
        echo "❌ No hay datos para restaurar"
        return 1
    fi
    
    # Crear respaldo antes de restaurar
    timestamp=$(date +%Y%m%d_%H%M%S)
    tar -czf "$BACKUP_DIR/cursor-restore-backup-$timestamp.tar.gz" "$CURSOR_CONFIG" 2>/dev/null
    
    # Restaurar archivos
    cp "$SYNC_DIR/storage.json" "$CURSOR_CONFIG/globalStorage/" 2>/dev/null
    cp "$SYNC_DIR/state.vscdb" "$CURSOR_CONFIG/globalStorage/" 2>/dev/null
    
    # Restaurar directorio de recuperación
    if [ -d "$SYNC_DIR/anysphere.cursor-retrieval" ]; then
        cp -r "$SYNC_DIR/anysphere.cursor-retrieval" "$CURSOR_CONFIG/globalStorage/"
    fi
    
    echo "✅ Restauración completada"
}

# Función principal
case "$1" in
    "sync")
        sync_cursor
        ;;
    "restore")
        restore_cursor
        ;;
    *)
        echo "Uso: $0 {sync|restore}"
        echo "  sync    - Sincronizar contexto hacia Nextcloud"
        echo "  restore - Restaurar contexto desde Nextcloud"
        ;;
esac
```

#### Opción B: Sincronización Automática con Cron

**Agregar a crontab (`crontab -e`):**

```bash
# Sincronizar cada 30 minutos
*/30 * * * * /home/$USER/bin/cursor-sync.sh sync

# Limpiar respaldos antiguos (diariamente)
0 2 * * * find /home/$USER/secure/cursor-backup -name "*.tar.gz" -mtime +7 -delete
```

### Paso 4: Uso Diario

#### Al empezar a trabajar

```bash
# 1. Cerrar Cursor completamente
# 2. Restaurar contexto más reciente
cursor-sync.sh restore

# 3. Abrir Cursor
```

#### Al terminar de trabajar

```bash
# 1. Cerrar Cursor completamente
# 2. Sincronizar cambios
cursor-sync.sh sync
```

### Paso 5: Verificación

**Verificar que la sincronización funciona:**

```bash
# Verificar archivos sincronizados
ls -la ~/Nextcloud/cursor-sync/

# Verificar respaldos
ls -la ~/secure/cursor-backup/
```

## Solución de Problemas

### Problema: Conflictos de sincronización

**Solución:** Siempre cerrar Cursor en un equipo antes de abrirlo en otro.

### Problema: Archivos muy grandes (state.vscdb)

**Solución:** El archivo puede ser grande (2-3GB). Considera sincronizar solo cuando sea necesario.

### Problema: Rutas diferentes entre equipos

**Solución:** Los contextos están vinculados a rutas específicas. Usa rutas similares en ambos equipos.

### Problema: Nextcloud no sincroniza automáticamente

**Solución:** Verificar que el cliente de Nextcloud esté ejecutándose y configurado correctamente.

## Comandos Útiles

```bash
# Ver estado de sincronización de Nextcloud
nextcloudcmd --status

# Forzar sincronización manual
cursor-sync.sh sync

# Verificar espacio en Nextcloud
du -sh ~/Nextcloud/cursor-sync/

# Limpiar respaldos antiguos
find ~/secure/cursor-backup -name "*.tar.gz" -mtime +30 -delete
```

## Notas Importantes

- ⚠️ **Nunca usar Cursor en ambos equipos simultáneamente**
- ⚠️ **El archivo `state.vscdb` puede ser muy grande (2-3GB)**
- ⚠️ **Hacer respaldos antes de cualquier operación**
- ⚠️ **Verificar que Nextcloud tenga suficiente espacio**

## Alternativas

Si Nextcloud no funciona bien para archivos grandes, considera:

- Usar `rsync` con servidor SSH
- Usar `syncthing` para sincronización P2P
- Usar `rclone` con servicios cloud

---

## Créditos

Guía creada para sincronizar contexto de IA de Cursor entre múltiples equipos.
