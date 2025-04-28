# 🖥️ MCP Server Manager

Sistema para gestionar y lanzar múltiples servidores MCP de forma concurrente.

## 📋 Descripción

MCP Server Manager es una herramienta enfocada en simplificar la configuración de soporte de MCP para Cursor (no estrictamente); que facilita la configuración y el lanzamiento de múltiples servidores MCP desde un único archivo de configuración YAML. El sistema:

- Carga la configuración de servidores desde un archivo YAML
- Verifica la disponibilidad de puertos especificados
- Asigna automáticamente puertos disponibles cuando no se especifican
- Lanza los servidores de manera concurrente mediante subprocesos
- Gestiona el cierre ordenado de los servidores
- Registra todas las operaciones en archivos de log
- Implementa un manejo de errores avanzado con recuperación automática

## 🔧 Uso

### Variables de entorno

El sistema utiliza las siguientes variables de entorno para determinar las rutas base:

- `APPS_HOME`: Directorio base para las aplicaciones. Por defecto es `$HOME/bin`.
- `APPS_CONFIG`: Directorio de configuraciones. Por defecto es `$APPS_HOME/config`.
- `APPS_LOGS`: Directorio de logs. Por defecto es `$APPS_HOME/logs`.

Estas variables pueden ser configuradas en el sistema antes de ejecutar la aplicación.

### Sistema de logs

El sistema implementa un registro de logs que varía según el modo de ejecución:

- **Si se ejecuta como superusuario (root)**: Los logs se almacenan en `/var/log/mcp_manager.log`
- **Si se ejecuta como usuario normal**: Los logs se almacenan en `$APPS_LOGS/mcp_manager.log`

Todos los eventos, errores y advertencias se registran en estos archivos, facilitando la depuración y monitoreo.

### Manejo de errores

El sistema implementa un manejo de errores avanzado que incluye:

- **Excepciones tipadas**: Diferentes tipos de excepciones para cada categoría de error (configuración, red, servidor, validación).
- **Reintentos automáticos**: Las operaciones propensas a fallos temporales (como la carga de configuración o verificación de puertos) se reintentan automáticamente.
- **Monitoreo continuo**: Los servidores son monitoreados constantemente y, si alguno falla, se intenta reiniciar automáticamente.
- **Volcado de información**: En caso de error crítico, se genera un archivo JSON con toda la información necesaria para diagnóstico.
- **Manejo de señales**: El sistema responde adecuadamente a señales del sistema operativo (SIGINT, SIGTERM) para un cierre ordenado.

### Configuración básica

```bash
# Configuración de variables de entorno (opcional)
export APPS_HOME=/ruta/personalizada
export APPS_CONFIG=/ruta/configs/personalizada
export APPS_LOGS=/ruta/logs/personalizada

# Instalación de dependencias
pip install -r requirements.txt

# Ejecución del gestor de servidores
./mcp_manager.py

# Ejecución como superusuario (logs en /var/log/)
sudo ./mcp_manager.py
```

### Archivo de configuración

El sistema utiliza un archivo de configuración que puede estar en cualquiera de las siguientes ubicaciones (en orden de prioridad):

1. `$APPS_CONFIG/mcp_servers.yaml` (ubicación principal)
2. `$APPS_HOME/mcp_manager.yaml` (ubicación alternativa para compatibilidad)

El formato del archivo es:

```yaml
servers:
  - name: "Nombre del Servidor"
    type: "node"  # Tipo: "node" o "python"
    cmd: ["comando", "arg1", "arg2"]
    port: 8000    # Opcional: Si no se especifica, se asigna automáticamente

  - name: "Otro Servidor"
    type: "python"
    cmd: ["comando", "arg1", "arg2"]
    # Puerto no especificado, se asignará automáticamente
```

## 🚀 Características

- **Carga desde YAML**: Configuración centralizada y fácil de mantener
- **Verificación de puertos**: Comprueba si los puertos especificados están disponibles
- **Asignación automática**: Encuentra y asigna puertos disponibles cuando no se especifican
- **Ejecución concurrente**: Lanza todos los servidores en paralelo
- **Gestión de errores**: Manejo robusto de errores y excepciones
- **Cierre seguro**: Termina correctamente todos los servidores al finalizar
- **Sistema de logs**: Registro detallado de todas las operaciones
- **Reintentos automáticos**: Las operaciones propensas a fallos se reintentan automáticamente
- **Recuperación automática**: Los servidores que fallan son reiniciados automáticamente
- **Manejo de señales**: Responde adecuadamente a señales del sistema operativo

## 💻 Ejemplos

### Ejemplo de configuración

```yaml
servers:
  - name: "GitHub MCP"
    type: "node"
    cmd: ["npx", "@mcp/github"]

  - name: "OpenAI MCP"
    type: "node"
    cmd: ["npx", "@mcp/openai-assistant"]

  - name: "My Custom Python MCP"
    type: "python"
    cmd: ["uvicorn", "servers/mcp-server-github/app.py", "--host", "0.0.0.0", "--reload"]
```

### Salida de ejemplo

```
2023-05-26 10:15:30,123 - mcp_manager - INFO - Log configurado en: /home/mrosero/bin/logs/mcp_manager.log
2023-05-26 10:15:30,125 - mcp_manager - INFO - Ejecutando como usuario normal
2023-05-26 10:15:30,126 - mcp_manager - INFO - APPS_HOME: /home/mrosero/bin
2023-05-26 10:15:30,127 - mcp_manager - INFO - APPS_CONFIG: /home/mrosero/bin/config
2023-05-26 10:15:30,128 - mcp_manager - INFO - APPS_LOGS: /home/mrosero/bin/logs
2023-05-26 10:15:30,130 - mcp_manager - INFO - Usando archivo de configuración: /home/mrosero/bin/config/mcp_servers.yaml
2023-05-26 10:15:30,135 - mcp_manager - INFO - Puerto 8000 asignado automáticamente para 'GitHub MCP'
2023-05-26 10:15:30,136 - mcp_manager - INFO - Lanzando GitHub MCP en puerto 8000...
2023-05-26 10:15:30,140 - mcp_manager - INFO - Puerto 8001 asignado automáticamente para 'OpenAI MCP'
2023-05-26 10:15:30,141 - mcp_manager - INFO - Lanzando OpenAI MCP en puerto 8001...
2023-05-26 10:15:30,145 - mcp_manager - INFO - Puerto 8002 asignado automáticamente para 'My Custom Python MCP'
2023-05-26 10:15:30,146 - mcp_manager - INFO - Lanzando My Custom Python MCP en puerto 8002...
2023-05-26 10:15:30,150 - mcp_manager - INFO - ✅ Lanzados 3/3 MCP servers.
```

## 🔍 Detalles técnicos

### Jerarquía de excepciones

```python
class MCPManagerError(Exception):
    """Clase base para todas las excepciones del MCP Manager"""
    pass

class ConfigError(MCPManagerError):
    """Error relacionado con la configuración"""
    pass

class NetworkError(MCPManagerError):
    """Error relacionado con la red o los puertos"""
    pass

class ServerError(MCPManagerError):
    """Error relacionado con el lanzamiento o gestión de servidores"""
    pass

class ValidationError(MCPManagerError):
    """Error en la validación de datos"""
    pass
```

### Sistema de reintentos

El sistema utiliza un decorador para reintentar funciones propensas a fallos temporales:

```python
@retry(max_attempts=3, delay=2.0, exceptions=(yaml.YAMLError, OSError))
def load_config(config_file: str) -> Dict[str, Any]:
    """Carga la configuración desde un archivo YAML con reintentos automáticos"""
    # Implementación...
```

### Validación de configuración

Toda la configuración es validada antes de su uso:

```python
def validate_server_config(server_config: Dict[str, Any]) -> None:
    """Valida que la configuración del servidor contenga todos los campos necesarios y con tipos correctos"""
    # Verificar campos requeridos
    required_fields = ['name', 'type', 'cmd']
    missing_fields = [field for field in required_fields if field not in server_config]
    
    if missing_fields:
        raise ValidationError(f"Campos requeridos faltantes en la configuración: {', '.join(missing_fields)}")
    
    # Más validaciones...
```

### Monitoreo de procesos

El sistema monitorea continuamente los procesos lanzados:

```python
def monitor_processes(processes: List[Tuple[subprocess.Popen, str, int]]) -> None:
    """Monitorea los procesos en ejecución y reporta cualquier cambio de estado"""
    while True:
        for i, (process, name, port) in enumerate(processes[:]):
            # Verificar si el proceso ha terminado
            if process.poll() is not None:
                # Si el proceso terminó con error, intentar reiniciarlo
                if process.returncode != 0:
                    # Intentar reiniciar...
```

### Manejo de señales

El sistema maneja señales del sistema operativo para un cierre ordenado:

```python
def setup_signal_handlers(processes: List[Tuple[subprocess.Popen, str, int]]) -> None:
    """Configura manejadores de señales para gestionar la terminación adecuada"""
    
    def signal_handler(sig, frame):
        """Manejador de señales para cierre ordenado"""
        # Implementación...
    
    # Registrar manejadores para diferentes señales
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill
```

### Volcado de información de error

En caso de error crítico, se genera un archivo JSON con información detallada:

```python
def dump_crash_info(processes: List[Tuple[subprocess.Popen, str, int]], exception: Exception) -> None:
    """Genera un archivo de volcado con información del error para diagnóstico"""
    # Implementación...
```

## 📦 Requisitos

- Python 3.x
- pyyaml>=6.0
- uvicorn>=0.15.0 (para servidores Python)
- Node.js y npm (para servidores Node.js)

## 🛠️ Posibles mejoras

- Añadir capacidad de monitoreo del estado de los servidores en tiempo real
- Implementar un panel web para gestionar los servidores
- Agregar soporte para más tipos de servidores
- Permitir la definición de dependencias entre servidores
- Rotación de archivos de log para evitar que crezcan demasiado
- Configuraciones personalizadas para el sistema de reintentos por tipo de servidor 