# Guía de fix-locale.sh - Corrección de Locales

> **📖 [← Volver al README principal](../README.md)**

## 📖 Introducción

`fix-locale.sh` es un script moderno y elegante que resuelve problemas comunes de configuración de locale en sistemas Debian/Ubuntu, especialmente los errores:

- `apt-listchanges: Can't set locale; make sure $LC_* and $LANG are correct!`
- `perl: warning: Setting locale failed.`
- `perl: warning: Please check that your locale settings`

### ✨ Características Modernas

- **🎨 Interfaz elegante**: Output colorizado con emojis y tablas ASCII
- **🔐 Sudo inteligente**: Minimiza peticiones de contraseña
- **🌐 Soporte remoto**: Ejecución via SSH en servidores remotos
- **📊 Diagnóstico visual**: Tablas y gráficos para mejor comprensión
- **⚡ Ejecución eficiente**: Operaciones optimizadas y batch

## 🚀 Instalación

### Pre-requisitos

- **Sistema**: Debian/Ubuntu
- **Permisos**: sudo (para correcciones)
- **Paquetes**: locales (se instala automáticamente si falta)

### Uso Básico

```bash
# Verificar configuración actual
./fix-locale.sh --check

# Listar locales disponibles
./fix-locale.sh --list

# Corregir configuración (requiere sudo)
./fix-locale.sh --fix

# Ejecutar todas las correcciones
./fix-locale.sh --all
```

## 🔧 Opciones Disponibles

### Opciones Principales

| Opción | Descripción |
|--------|-------------|
| `-c, --check` | Solo verificar configuración actual |
| `-l, --list` | Listar locales disponibles en el sistema |
| `-g, --generate` | Generar locales comunes (requiere sudo) |
| `-f, --fix` | Corregir configuración (requiere sudo) |
| `-a, --all` | Ejecutar todas las correcciones |
| `-h, --help` | Mostrar ayuda completa |

### Opciones Remotas

| Opción | Descripción |
|--------|-------------|
| `-r, --remote HOST` | Ejecutar en servidor remoto via SSH |

## 📝 Ejemplos de Uso

### Uso Local

```bash
# 1. Verificar problema actual
./fix-locale.sh --check

# 2. Ver locales disponibles
./fix-locale.sh --list

# 3. Corregir configuración
./fix-locale.sh --fix

# 4. Verificar corrección
./fix-locale.sh --check

# 5. Aplicar cambios inmediatamente
source ~/.bashrc
```

### Uso Remoto

```bash
# Verificar configuración en servidor remoto
./fix-locale.sh --remote user@server.example.com --check

# Corregir configuración remota
./fix-locale.sh --remote user@server.example.com --fix

# Ejecutar todas las correcciones remotamente
./fix-locale.sh --remote user@server.example.com --all
```

### Flujo Completo de Corrección

```bash
# Paso 1: Diagnóstico
./fix-locale.sh --check

# Paso 2: Ver locales disponibles
./fix-locale.sh --list

# Paso 3: Corrección automática
./fix-locale.sh --all

# Paso 4: Aplicar cambios
source ~/.bashrc

# Paso 5: Verificar solución
./fix-locale.sh --check
```

## 🔍 Diagnóstico de Problemas

### Problemas Comunes

#### 1. **Locale no disponible**

```text
[WARNING] Locale es_PA.UTF-8 no está disponible en el sistema
```

**Solución**: Usar `--generate` para crear locales comunes

#### 2. **Variables sin configurar**

```bash
LANG=C.UTF-8
LC_ALL=unset
```

**Solución**: Usar `--fix` para configurar variables correctamente

#### 3. **Paquete locales faltante**

```bash
Package 'locales' no está instalado
```

**Solución**: El script lo instala automáticamente

### Verificación Manual

```bash
# Verificar variables de entorno
echo $LANG
echo $LC_ALL
echo $LANGUAGE

# Verificar locales disponibles
locale -a

# Verificar archivos de configuración
cat /etc/default/locale
cat ~/.bashrc | grep -E "LANG|LC_"
```

## 🛠️ Configuración Automática

### Locales Generados Automáticamente

El script genera automáticamente estos locales:

- `en_US.UTF-8` - Inglés (Estados Unidos)
- `es_ES.UTF-8` - Español (España)
- `es_PA.UTF-8` - Español (Panamá)
- `C.UTF-8` - Locale por defecto del sistema

### Archivos Modificados

1. **`/etc/default/locale`** - Configuración del sistema
2. **`/etc/environment`** - Variables de entorno globales
3. **`~/.bashrc`** - Configuración del usuario
4. **`/etc/locale.gen`** - Locales generados

## 🚨 Solución de Problemas

### Error: "Permission denied"

```bash
# Asegurar permisos de ejecución
chmod +x fix-locale.sh

# Usar sudo para operaciones del sistema
sudo ./fix-locale.sh --fix
```

### Error: "Package locales not found"

```bash
# Actualizar repositorios
sudo apt-get update

# El script instalará automáticamente locales si falta
./fix-locale.sh --generate
```

### Error: "SSH connection failed"

```bash
# Verificar conectividad SSH
ssh user@server.example.com

# Verificar configuración SSH
cat ~/.ssh/config
```

### Los cambios no se aplican

```bash
# Recargar configuración del shell
source ~/.bashrc

# O reiniciar terminal
exit
# Abrir nueva terminal

# Verificar en nueva sesión
./fix-locale.sh --check
```

## 🔐 Seguridad y Sudo Inteligente

### Sudo Inteligente

El script implementa un sistema de sudo inteligente que minimiza las peticiones de contraseña:

```bash
# Verifica si ya tiene permisos sudo activos
if sudo -n true 2>/dev/null; then
    # Ejecuta directamente sin pedir contraseña
    sudo comando
else
    # Solicita contraseña una sola vez
    sudo comando
fi
```

**Beneficios:**

- ✅ **Una sola petición**: Solicita contraseña solo cuando es necesario
- ✅ **Reutilización**: Aprovecha sesiones sudo activas
- ✅ **Eficiencia**: Evita múltiples peticiones de contraseña
- ✅ **Transparencia**: Informa claramente cuándo se requieren permisos

### Permisos Requeridos

- **Lectura**: `/etc/locale.gen`, `/etc/default/locale`
- **Escritura**: `/etc/locale.gen`, `/etc/default/locale`, `/etc/environment`, `~/.bashrc`
- **Ejecución**: `locale-gen`, `apt-get`

### Operaciones Seguras

- ✅ Solo modifica archivos de configuración de locale
- ✅ No modifica configuraciones críticas del sistema
- ✅ Crea respaldos automáticos de archivos modificados
- ✅ Usa permisos mínimos necesarios
- ✅ Validaciones de seguridad en todas las operaciones

## 📞 Soporte

### Logs y Diagnóstico

```bash
# Verificar logs del sistema
journalctl -u systemd-locale

# Verificar configuración actual
./fix-locale.sh --check

# Generar reporte completo
./fix-locale.sh --all > locale-fix.log 2>&1
```

### Información del Sistema

```bash
# Información del sistema
uname -a
lsb_release -a

# Información de locale
locale
localectl status
```

---

**📖 [← Volver al README principal](../README.md)**
