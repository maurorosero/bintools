# 🐍 Administrador de Entornos Virtuales de Python (`pymanager.sh`)

Herramienta para gestionar entornos virtuales de Python de manera sencilla y eficiente.

## 🔍 Características

- 🧠 **Gestión inteligente**: Crea, activa, lista y elimina entornos virtuales de Python
- 📦 **Instalación automática**: Detecta y gestiona dependencias desde archivos de requisitos
- 🔄 **Actualización de pip**: Actualización automática de pip en cada entorno creado
- 📊 **Visualización colorida**: Interfaces con colores para mejor legibilidad
- 🔍 **Comprobación de estado**: Verifica paquetes que ya están instalados vs. pendientes
- 📈 **Barra de progreso**: Indica claramente el progreso durante instalaciones largas
- 🔄 **Alias convenientes**: Crea alias (`pybin`/`pyunbin`) para activar/desactivar entornos
- 📋 **Funciones por defecto**: Opción para instalar un entorno por defecto con requisitos básicos
- 📊 **Registro detallado**: Guarda todas las operaciones en `/var/log/pymanager.log` o `~/bin/logs/pymanager.log`

## 💡 Uso

```bash
pymanager.sh {create|activate|list|remove|--install|help}
```

### Comandos

| Comando | Descripción |
|:--------|:------------|
| `create <env_name> [req_file]` | Crea un nuevo entorno virtual e instala paquetes desde un archivo de requisitos |
| `activate <env_name>` | Muestra instrucciones para activar un entorno existente |
| `list` | Lista todos los entornos virtuales disponibles |
| `remove <env_name>` | Elimina un entorno virtual existente |
| `--install` | Instala un entorno predeterminado con alias `pybin` |
| `help` | Muestra la ayuda |

## 📋 Ejemplos

```bash
# Crear un nuevo entorno con requisitos
./pymanager.sh create proyecto1 requirements.txt

# Crear un entorno sin requisitos
./pymanager.sh create entorno_vacio

# Obtener instrucciones para activar un entorno
./pymanager.sh activate proyecto1

# Listar todos los entornos virtuales
./pymanager.sh list

# Eliminar un entorno
./pymanager.sh remove proyecto1

# Instalar entorno predeterminado con alias
./pymanager.sh --install
```

## 🔄 Instalación predeterminada

Al ejecutar `pymanager.sh --install`, se realizan las siguientes acciones:

1. Crea un entorno virtual en `~/bin/venv/$USER`
2. Instala los paquetes listados en `~/bin/requirements.txt`
3. Crea los siguientes alias en `.bashrc`:
   - `pybin`: Activa el entorno predeterminado
   - `pyunbin`: Desactiva el entorno activo

## 📊 Características de interfaz

El script incluye una interfaz de usuario con colores para mejor legibilidad:

- 🟢 **Verde**: Éxito, confirmación, tareas completadas
- 🟡 **Amarillo**: Advertencias, progreso actual
- 🔴 **Rojo**: Errores, fallos
- 🔵 **Cyan**: Información, estado
- 🟣 **Magenta**: Mensajes de depuración (solo con DEBUG=1)
- ⚪ **Blanco**: Títulos, encabezados importantes

## 📋 Verificación de paquetes

El gestor realiza verificaciones inteligentes de los paquetes:

- ✅ Detecta paquetes ya instalados
- 🔄 Identifica paquetes que requieren actualización
- 🆕 Lista paquetes pendientes de instalar
- 📊 Muestra resumen estadístico de los paquetes
- 🔍 Presenta los paquetes en columnas organizadas con indicadores visuales

## 📝 Registro de actividades

Todas las operaciones se registran detalladamente:

- Si se ejecuta como usuario normal: `~/bin/logs/pymanager.log`
- Si se ejecuta como superusuario: `/var/log/pymanager.log`

## ⚙️ Requisitos

- Bash 4.0 o superior
- Python 3.x
- Módulo `venv` de Python (generalmente incluido como `python3-venv` en distribuciones Linux)
- Terminal que soporte colores ANSI