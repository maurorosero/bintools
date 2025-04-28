#!/usr/bin/env python3
"""
MCP Manager - Sistema para cargar, configurar y lanzar servidores MCP desde un archivo YAML
"""

import yaml
import socket
import subprocess
import random
import time
import sys
import os
import pathlib
import logging
import signal
import traceback
import json
from functools import wraps
from typing import Dict, List, Any, Optional, Tuple, Callable, Union, TypeVar


# Definición de tipos para anotaciones
T = TypeVar('T')
RetryFunction = Callable[..., T]


# Excepciones personalizadas
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


# Sistema de reintentos
def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, 
          exceptions: Union[Exception, Tuple[Exception, ...]] = Exception) -> Callable[[RetryFunction], RetryFunction]:
    """
    Decorador para reintentar funciones que pueden fallar temporalmente.
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Tiempo inicial de espera entre intentos (en segundos)
        backoff: Factor multiplicativo para aumentar el delay después de cada intento
        exceptions: Excepciones que activarán un reintento
    """
    def decorator(func: RetryFunction) -> RetryFunction:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            mtries, mdelay = max_attempts, delay
            last_exception = None
            
            while mtries > 0:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    mtries -= 1
                    if mtries == 0:
                        break
                    
                    logger.warning(f"Reintentando '{func.__name__}' tras error: {str(e)}. "
                                  f"Intentos restantes: {mtries}")
                    
                    time.sleep(mdelay)
                    mdelay *= backoff
            
            # Si llegamos aquí, se agotaron los reintentos
            logger.error(f"Se agotaron los reintentos para '{func.__name__}'")
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


# Definir las rutas de aplicación usando variables de entorno
def get_app_paths() -> Dict[str, str]:
    """
    Determina las rutas base para la aplicación usando variables de entorno.
    APPS_HOME: Directorio base para aplicaciones (por defecto $HOME/bin)
    APPS_CONFIG: Directorio de configuraciones (por defecto $APPS_HOME/config)
    APPS_LOGS: Directorio de logs (por defecto $APPS_HOME/logs)
    """
    # Determinar APPS_HOME (default: $HOME/bin)
    apps_home = os.environ.get('APPS_HOME', os.path.join(os.environ.get('HOME', '/'), 'bin'))
    
    # Determinar APPS_CONFIG (default: $APPS_HOME/config)
    apps_config = os.environ.get('APPS_CONFIG', os.path.join(apps_home, 'config'))
    
    # Determinar APPS_LOGS (default: $APPS_HOME/logs)
    apps_logs = os.environ.get('APPS_LOGS', os.path.join(apps_home, 'logs'))
    
    return {
        'apps_home': apps_home,
        'apps_config': apps_config,
        'apps_logs': apps_logs
    }


def setup_logging() -> logging.Logger:
    """
    Configura el sistema de logging dependiendo de si se ejecuta como root o usuario normal.
    Si se ejecuta como root, el log se guarda en /var/log/mcp_manager.log
    Si se ejecuta como usuario, el log se guarda en $APPS_LOGS/mcp_manager.log
    """
    script_name = os.path.basename(__file__).split('.')[0]  # mcp_manager
    log_filename = f"{script_name}.log"
    
    # Determinar si el script se ejecuta como root
    is_root = os.geteuid() == 0
    
    if is_root:
        log_path = os.path.join('/var/log', log_filename)
    else:
        paths = get_app_paths()
        logs_dir = paths['apps_logs']
        
        # Asegurar que el directorio de logs exista
        os.makedirs(logs_dir, exist_ok=True)
        
        log_path = os.path.join(logs_dir, log_filename)
    
    # Configurar el logger
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.INFO)
    
    # Limpiar handlers existentes para evitar duplicados
    if logger.handlers:
        logger.handlers.clear()
    
    # Formato del log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.info(f"Log configurado en: {log_path}")
    logger.info(f"Ejecutando como {'superusuario' if is_root else 'usuario normal'}")
    
    return logger


@retry(max_attempts=3, delay=2.0, exceptions=(yaml.YAMLError, OSError))
def load_config(config_file: str) -> Dict[str, Any]:
    """Carga la configuración desde un archivo YAML con reintentos automáticos"""
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            
        if not config:
            raise ConfigError(f"El archivo de configuración {config_file} está vacío")
            
        return config
    except FileNotFoundError:
        error_msg = f"Error: No se encontró el archivo de configuración {config_file}"
        logger.error(error_msg)
        raise ConfigError(error_msg) from None
    except yaml.YAMLError as e:
        error_msg = f"Error al parsear el archivo YAML: {e}"
        logger.error(error_msg)
        raise ConfigError(error_msg) from e
    except Exception as e:
        error_msg = f"Error inesperado al cargar la configuración: {e}"
        logger.error(error_msg)
        raise ConfigError(error_msg) from e


def validate_server_config(server_config: Dict[str, Any]) -> None:
    """Valida que la configuración del servidor contenga todos los campos necesarios y con tipos correctos"""
    # Verificar campos requeridos
    required_fields = ['name', 'type', 'cmd']
    missing_fields = [field for field in required_fields if field not in server_config]
    
    if missing_fields:
        raise ValidationError(f"Campos requeridos faltantes en la configuración: {', '.join(missing_fields)}")
    
    # Validar tipos de datos
    if not isinstance(server_config['name'], str):
        raise ValidationError(f"El campo 'name' debe ser un string, no {type(server_config['name'])}")
    
    if not isinstance(server_config['type'], str):
        raise ValidationError(f"El campo 'type' debe ser un string, no {type(server_config['type'])}")
    
    if not isinstance(server_config['cmd'], list) or not all(isinstance(item, str) for item in server_config['cmd']):
        raise ValidationError(f"El campo 'cmd' debe ser una lista de strings")
    
    # Validar puerto si está especificado
    if 'port' in server_config:
        if not isinstance(server_config['port'], int):
            raise ValidationError(f"El campo 'port' debe ser un entero, no {type(server_config['port'])}")
        
        if server_config['port'] < 1 or server_config['port'] > 65535:
            raise ValidationError(f"Puerto inválido: {server_config['port']}. Debe estar entre 1 y 65535")


@retry(max_attempts=5, delay=0.5, exceptions=(socket.error,))
def is_port_available(port: int, host: str = '127.0.0.1') -> bool:
    """Verifica si un puerto está disponible en el host especificado, con reintentos automáticos"""
    if port < 1 or port > 65535:
        raise NetworkError(f"Puerto inválido: {port}. Debe estar entre 1 y 65535")
        
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except socket.error as e:
        logger.debug(f"Puerto {port} no disponible: {e}")
        return False


def find_available_port(start_port: int = 8000, end_port: int = 8100) -> Optional[int]:
    """Busca un puerto disponible en el rango especificado"""
    if start_port < 1 or start_port > 65535 or end_port < 1 or end_port > 65535:
        raise NetworkError(f"Rango de puertos inválido: {start_port}-{end_port}. Debe estar entre 1 y 65535")
        
    if start_port > end_port:
        raise NetworkError(f"Puerto inicial ({start_port}) mayor que puerto final ({end_port})")
    
    # Intentamos primero puertos secuenciales
    for port in range(start_port, end_port + 1):
        if is_port_available(port):
            return port
    
    # Si no encontramos puertos secuenciales, intentamos aleatoriamente
    ports_to_try = min(10, end_port - start_port + 1)  # Intentar un máximo de 10 puertos aleatorios
    for _ in range(ports_to_try):
        port = random.randint(start_port, end_port)
        if is_port_available(port):
            return port
            
    return None


def launch_server(server_config: Dict[str, Any]) -> Tuple[subprocess.Popen, int]:
    """Lanza un servidor según la configuración proporcionada"""
    try:
        # Validar la configuración
        validate_server_config(server_config)
        
        name = server_config['name']
        server_type = server_config['type']
        cmd = server_config['cmd'].copy()  # Hacer una copia para no modificar el original
        
        # Verificar si el tipo de servidor es válido
        valid_types = ['node', 'python']
        if server_type not in valid_types:
            logger.warning(f"Advertencia: El tipo de servidor '{server_type}' no es reconocido para '{name}'. "
                          f"Tipos válidos: {', '.join(valid_types)}")
        
        # Asignar puerto si no está especificado
        port = server_config.get('port')
        if port is None:
            port = find_available_port()
            if port is None:
                msg = f"Error: No se pudo encontrar un puerto disponible para '{name}'"
                logger.error(msg)
                raise NetworkError(msg)
            logger.info(f"Puerto {port} asignado automáticamente para '{name}'")
        else:
            # Verificar que el puerto esté disponible
            if not is_port_available(port):
                msg = f"Error: El puerto {port} especificado para '{name}' no está disponible"
                logger.error(msg)
                raise NetworkError(msg)
        
        # Agregar el puerto a los argumentos del comando si es necesario
        # Nota: Esto depende de cómo cada servidor acepta el puerto como parámetro
        # Adaptamos según el tipo de servidor
        if server_type == "node":
            cmd.extend(["--port", str(port)])
        elif server_type == "python":
            # Asumiendo que es uvicorn y el puerto se pasa con --port
            if "uvicorn" in cmd[0]:
                cmd.extend(["--port", str(port)])
        
        # Ejecutar el servidor
        logger.info(f"Lanzando {name} en puerto {port}...")
        
        # Usando subprocess.Popen para lanzar el proceso de forma no bloqueante
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Verificar que el proceso haya iniciado correctamente
        if process.poll() is not None:
            # El proceso ya terminó (error)
            stdout, stderr = process.communicate()
            msg = f"Error al iniciar el servidor '{name}': {stderr or 'Error desconocido'}"
            logger.error(msg)
            logger.debug(f"Salida estándar: {stdout}")
            raise ServerError(msg)
            
        return process, port
    
    except ValidationError as e:
        logger.error(f"Error de validación para el servidor '{server_config.get('name', 'desconocido')}': {e}")
        raise
    except NetworkError as e:
        logger.error(f"Error de red para el servidor '{server_config.get('name', 'desconocido')}': {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al lanzar el servidor '{server_config.get('name', 'desconocido')}': {e}")
        logger.debug(traceback.format_exc())
        raise ServerError(f"Error al lanzar servidor: {e}") from e


def find_config_file() -> str:
    """Busca el archivo de configuración en las ubicaciones posibles"""
    paths = get_app_paths()
    apps_home = paths['apps_home']
    apps_config = paths['apps_config']
    
    # Orden de prioridad para buscar el archivo de configuración
    config_paths = [
        os.path.join(apps_config, 'mcp_servers.yaml'),  # Ubicación principal en APPS_CONFIG
        os.path.join(apps_home, 'mcp_manager.yaml')     # Ubicación alternativa en APPS_HOME
    ]
    
    for path in config_paths:
        if pathlib.Path(path).exists():
            return path
    
    # Si no encuentra ninguno, devuelve la ubicación principal
    logger.warning(f"No se encontró ningún archivo de configuración existente. Se usará la ubicación predeterminada.")
    return os.path.join(apps_config, 'mcp_servers.yaml')


def dump_crash_info(processes: List[Tuple[subprocess.Popen, str, int]], exception: Exception) -> None:
    """Genera un archivo de volcado con información del error para diagnóstico"""
    crash_time = time.strftime("%Y%m%d-%H%M%S")
    paths = get_app_paths()
    logs_dir = paths['apps_logs']
    crash_file = os.path.join(logs_dir, f"mcp_crash_{crash_time}.json")
    
    # Información a guardar
    crash_info = {
        "timestamp": time.time(),
        "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "traceback": traceback.format_exc(),
        "processes": [
            {
                "name": name,
                "port": port,
                "pid": process.pid,
                "returncode": process.returncode
            }
            for process, name, port in processes
        ],
        "environment": {
            "python_version": sys.version,
            "platform": sys.platform,
            "apps_home": paths['apps_home'],
            "apps_config": paths['apps_config'],
            "apps_logs": paths['apps_logs']
        }
    }
    
    try:
        os.makedirs(logs_dir, exist_ok=True)
        with open(crash_file, 'w') as f:
            json.dump(crash_info, f, indent=2)
        logger.info(f"Información de error guardada en {crash_file}")
    except Exception as e:
        logger.error(f"No se pudo guardar la información de error: {e}")


def setup_signal_handlers(processes: List[Tuple[subprocess.Popen, str, int]]) -> None:
    """Configura manejadores de señales para gestionar la terminación adecuada"""
    
    def signal_handler(sig, frame):
        """Manejador de señales para cierre ordenado"""
        signal_name = {
            signal.SIGINT: "SIGINT",
            signal.SIGTERM: "SIGTERM",
            signal.SIGHUP: "SIGHUP"
        }.get(sig, str(sig))
        
        logger.info(f"Recibida señal {signal_name}. Iniciando cierre ordenado...")
        
        # Detener todos los procesos
        for process, name, port in processes:
            if process.poll() is None:  # Solo si el proceso sigue ejecutándose
                logger.info(f"Deteniendo {name} (puerto {port}, PID {process.pid})...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"El servidor {name} no respondió al terminar. Forzando cierre...")
                    process.kill()
        
        logger.info("Todos los servidores detenidos. Saliendo.")
        sys.exit(0)
    
    # Registrar manejadores para diferentes señales
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill
    if hasattr(signal, 'SIGHUP'):  # No disponible en Windows
        signal.signal(signal.SIGHUP, signal_handler)  # Terminal cerrada


def monitor_processes(processes: List[Tuple[subprocess.Popen, str, int]]) -> None:
    """Monitorea los procesos en ejecución y reporta cualquier cambio de estado"""
    while True:
        for i, (process, name, port) in enumerate(processes[:]):
            # Verificar si el proceso ha terminado
            if process.poll() is not None:
                returncode = process.returncode
                stdout, stderr = process.communicate()
                
                if returncode != 0:
                    logger.error(f"El servidor {name} (puerto {port}) terminó con código {returncode}")
                    if stderr:
                        logger.error(f"Error: {stderr.strip()}")
                    if stdout:
                        logger.debug(f"Salida: {stdout.strip()}")
                        
                    # Intentar reiniciar el servidor
                    try:
                        logger.info(f"Intentando reiniciar {name}...")
                        # Recuperar la configuración original
                        server_config = {
                            "name": name,
                            "type": "node" if "--port" in process.args else "python",  # Inferencia básica
                            "cmd": process.args[:-2] if "--port" in process.args else process.args,
                            "port": port
                        }
                        
                        new_process, _ = launch_server(server_config)
                        processes[i] = (new_process, name, port)
                        logger.info(f"Servidor {name} reiniciado en puerto {port}")
                    except Exception as e:
                        logger.error(f"No se pudo reiniciar el servidor {name}: {e}")
                else:
                    logger.info(f"El servidor {name} (puerto {port}) terminó normalmente")
                    # Eliminar el proceso de la lista de monitoreo
                    processes.remove((process, name, port))
                    
        # Si no quedan servidores, salir
        if not processes:
            logger.info("Todos los servidores han terminado. Saliendo.")
            return
            
        # Dormir antes de la siguiente verificación
        time.sleep(5)


def main():
    """Función principal que coordina la carga de configuración y lanzamiento de servidores"""
    # Configurar logging
    global logger
    logger = setup_logging()
    
    processes = []
    
    try:
        # Mostrar rutas de entorno
        paths = get_app_paths()
        logger.info(f"APPS_HOME: {paths['apps_home']}")
        logger.info(f"APPS_CONFIG: {paths['apps_config']}")
        logger.info(f"APPS_LOGS: {paths['apps_logs']}")
        
        # Buscar y cargar el archivo de configuración
        config_file = find_config_file()
        logger.info(f"Usando archivo de configuración: {config_file}")
        
        config = load_config(config_file)
        
        # Validar la estructura básica de la configuración
        if not isinstance(config, dict):
            raise ConfigError(f"Formato de configuración inválido. Se esperaba un diccionario, se obtuvo {type(config)}")
            
        if 'servers' not in config:
            raise ConfigError("Error: La clave 'servers' no existe en el archivo de configuración")
            
        if not isinstance(config['servers'], list):
            raise ConfigError(f"La clave 'servers' debe ser una lista, se obtuvo {type(config['servers'])}")
            
        if not config['servers']:
            raise ConfigError("Error: No hay servidores configurados en el archivo YAML")
        
        # Lanzar cada servidor
        for server_config in config['servers']:
            try:
                process, port = launch_server(server_config)
                processes.append((process, server_config['name'], port))
            except (ValidationError, NetworkError, ServerError) as e:
                logger.error(f"Error al lanzar el servidor {server_config.get('name', 'desconocido')}: {e}")
                logger.warning("Continuando con los siguientes servidores...")
                continue
        
        if not processes:
            logger.error("No se pudo lanzar ningún servidor. Abortando.")
            return
            
        logger.info(f"✅ Lanzados {len(processes)}/{len(config['servers'])} MCP servers.")
        
        # Configurar manejadores de señales
        setup_signal_handlers(processes)
        
        # Monitorear los procesos
        monitor_processes(processes)
            
    except KeyboardInterrupt:
        logger.info("\nDetención solicitada por el usuario.")
    except ConfigError as e:
        logger.error(f"Error de configuración: {e}")
    except Exception as e:
        logger.error(f"Error durante la ejecución: {e}")
        logger.debug(traceback.format_exc())
        # Generar archivo de volcado para diagnóstico
        dump_crash_info(processes, e)
    finally:
        # Detener todos los procesos que aún estén en ejecución
        for process, name, port in processes:
            if process.poll() is None:  # Solo si el proceso sigue ejecutándose
                logger.info(f"Deteniendo {name} (puerto {port})...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"El servidor {name} no respondió al terminar. Forzando cierre...")
                    process.kill()


if __name__ == "__main__":
    main() 