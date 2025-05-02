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
- 🗑️ **Gestión granular**: Eliminar entornos completos o paquetes individuales
- 🔄 **Actualización de paquetes**: Actualiza paquetes específicos o todos los del entorno
- 🧪 **Verificación de requisitos**: Comprueba automáticamente si Python y venv están disponibles
- 🚀 **Inicio automático**: Opción para activar/desactivar el entorno al iniciar una sesión de terminal

## 💡 Uso

```bash
pymanager.sh {create|activate|list|remove|--install|--update|--autostart|help}
```

### Comandos

| Comando | Descripción |
|:--------|:------------|
| `create <env_name> [req_file]` | Crea un nuevo entorno virtual e instala paquetes desde un archivo de requisitos |
| `activate <env_name>` | Muestra instrucciones para activar un entorno existente |
| `list` | Lista todos los entornos virtuales disponibles |
| `remove <env_name> [--package <pkg>]` | Elimina un entorno virtual completo o un paquete específico |
| `--install` | Instala un entorno predeterminado con alias `pybin` |
| `--update [env_name] [pkg]` | Actualiza todos los paquetes o uno específico en un entorno |
| `--autostart {on|off}` | Activa o desactiva el inicio automático del entorno al iniciar sesión |
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

# Eliminar un paquete específico de un entorno
./pymanager.sh remove proyecto1 --package numpy

# Instalar entorno predeterminado con alias
./pymanager.sh --install

# Actualizar todos los paquetes en un entorno
./pymanager.sh --update proyecto1

# Actualizar un paquete específico
./pymanager.sh --update proyecto1 pandas

# Activar inicio automático del entorno al iniciar sesión
./pymanager.sh --autostart on

# Desactivar inicio automático
./pymanager.sh --autostart off
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

Cada entrada del log incluye:
- Marca de tiempo exacta
- Nivel de gravedad (INFO, ERROR, DEBUG, WARN)
- Mensaje detallado
- En caso de error, información adicional para diagnóstico

## ⚙️ Requisitos

- Bash 4.0 o superior
- Python 3.x
- Módulo `venv` de Python (generalmente incluido como `python3-venv` en distribuciones Linux)
- Terminal que soporte colores ANSI

## 🛠️ Conectividad a internet

El script verifica automáticamente la conexión a internet antes de intentar instalar paquetes:

- Realiza una prueba de conectividad mediante `ping` a servidores DNS confiables
- Implementa un timeout configurable para evitar bloqueos en entornos sin conexión
- Proporciona mensajes claros al usuario cuando no hay conexión disponible
- Ofrece rutas de uso alternativas cuando la conectividad es limitada

## 🧩 Funcionalidades avanzadas

### Gestión de dependencias

El script puede leer y procesar archivos de requisitos complejos con:
- Restricciones de versión (`==`, `>=`, `<=`, etc.)
- Extras opcionales de paquetes con sintaxis `[extra]`
- Comentarios y metadata en el formato estándar de `requirements.txt`

### Manejo inteligente de errores

- Captura y registra errores de manera detallada para facilitar el diagnóstico
- Proporciona mensajes específicos de error con posibles soluciones
- Implementa rollback automático en caso de fallos críticos durante la instalación
- Ofrece recomendaciones de pasos a seguir en caso de error