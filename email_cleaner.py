#!/usr/bin/env python3

import sys
import os
import subprocess

# --- Re-launch using venv Python if not already doing so ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(SCRIPT_DIR, '.venv', 'bin', 'python')

# Check if the .venv Python exists and if we are NOT currently running with it
if os.path.exists(VENV_PYTHON) and sys.executable != VENV_PYTHON:
    print(f"Re-launching script using virtual environment: {VENV_PYTHON}")
    # Re-execute the script with the venv Python, passing arguments
    try:
        # os.execv replaces the current process
        os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)
    except OSError as e:
        print(f"Error re-launching with venv Python: {e}", file=sys.stderr)
        sys.exit(1)
# --- End re-launch check ---

# Original imports should follow
import imaplib
import email
from email.header import decode_header
import datetime
import json
from typing import List, Dict, Any
import logging
from pathlib import Path
import argparse
import signal
import shutil
import venv
import socket
import urllib.request
import urllib.error
import time
import traceback
import re
from email.utils import parsedate_to_datetime

# Importaciones opcionales (se importarán después de instalar)
OPTIONAL_IMPORTS = {
    'dns.resolver': 'dnspython',
    'bs4': 'beautifulsoup4',
    'html2text': 'html2text',
    'requests': 'requests'
}

# Configuración de rutas
BASE_DIR = os.path.expanduser("~/emails")
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
PROGRESS_FILE = os.path.join(BASE_DIR, 'progress.json')
LOG_FILE = os.path.join(BASE_DIR, 'email_cleaner.log')
CATEGORIES_FILE = os.path.join(BASE_DIR, 'categories.dat')
SPAM_RULES_FILE = os.path.join(BASE_DIR, 'spam_rules.json')

# Crear directorio si no existe
os.makedirs(BASE_DIR, exist_ok=True)

# Crear archivo de categorías si no existe
if not os.path.exists(CATEGORIES_FILE):
    with open(CATEGORIES_FILE, 'w') as f:
        f.write("# Formato: categoria|palabras_clave|dominios|emails\n")
        f.write("# Ejemplo: redes_sociales|facebook,twitter,instagram|facebook.com,twitter.com|noreply@facebook.com,info@twitter.com\n")
        f.write("# Las palabras clave, dominios y emails son opcionales, separados por comas\n")

# Configuración de logging
debug_mode = os.environ.get('EMAIL_CLEAN_DEBUG') == '1'
logging.basicConfig(
    level=logging.DEBUG if debug_mode else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Variables para colores (se inicializarán después de instalar colorama)
COLORS = {
    'RED': '',
    'GREEN': '',
    'BLUE': '',
    'YELLOW': '',
    'CYAN': '',
    'RESET': ''
}

def init_colors():
    """Inicializa los colores para la terminal"""
    try:
        from colorama import init, Fore, Style
        init()
        COLORS.update({
            'RED': Fore.RED,
            'GREEN': Fore.GREEN,
            'BLUE': Fore.BLUE,
            'YELLOW': Fore.YELLOW,
            'CYAN': Fore.CYAN,
            'RESET': Style.RESET_ALL
        })
    except ImportError:
        pass

def print_error(message):
    """Imprime un mensaje de error en rojo"""
    print(f"{COLORS['RED']}Error: {message}{COLORS['RESET']}")

def print_success(message):
    """Imprime un mensaje de éxito en verde"""
    print(f"{COLORS['GREEN']}✓ {message}{COLORS['RESET']}")

def print_info(message):
    """Imprime un mensaje informativo en azul"""
    print(f"{COLORS['BLUE']}ℹ {message}{COLORS['RESET']}")

def print_warning(message):
    """Imprime un mensaje de advertencia en amarillo"""
    print(f"{COLORS['YELLOW']}⚠ {message}{COLORS['RESET']}")

def check_script_location():
    """Verifica que el script esté en la ubicación correcta"""
    script_path = os.path.abspath(__file__)
    if not os.path.exists(script_path):
        print_error(f"""
No se puede encontrar el script en: {script_path}

Por favor, asegúrate de que:
1. El script está en el directorio correcto
2. Tienes permisos de ejecución
3. Estás ejecutando el comando desde el directorio correcto

Para ejecutar el script:
1. Navega al directorio donde está el script:
   cd /ruta/al/directorio

2. Ejecuta el script:
   python3 email_cleaner.py --help
""")
        sys.exit(1)

# Verificar ubicación del script al inicio
check_script_location()

# Obtener el nombre del script
SCRIPT_NAME = os.path.basename(sys.argv[0])

# Configuración de timeouts
IMAP_TIMEOUT = 30  # segundos
INTERNET_CHECK_TIMEOUT = 5  # segundos
MAX_RETRIES = 3  # número máximo de intentos de conexión

# Lista de DNSBLs gratuitas
DNSBL_SERVERS = [
    'zen.spamhaus.org',
    'bl.spamcop.net',
    'dnsbl.sorbs.net',
    'spam.spamrats.com'
]

# Reglas básicas de SpamAssassin
DEFAULT_SPAM_RULES = {
    'subject_rules': [
        r'(?i)viagra|cialis|levitra',
        r'(?i)lottery|winner|prize',
        r'(?i)urgent|emergency|help',
        r'(?i)inheritance|money transfer',
        r'(?i)bank|account|password',
        r'(?i)free|offer|discount',
        r'(?i)click here|unsubscribe',
        r'(?i)congratulations|you won',
        r'(?i)verify|confirm|account',
        r'(?i)security|alert|warning'
    ],
    'body_rules': [
        r'(?i)click here to claim',
        r'(?i)unsubscribe from this list',
        r'(?i)click the link below',
        r'(?i)verify your email',
        r'(?i)confirm your account',
        r'(?i)your account has been',
        r'(?i)your password has been',
        r'(?i)your account will be',
        r'(?i)your account is about to',
        r'(?i)your account has been locked'
    ],
    'header_rules': [
        r'(?i)X-Spam-Flag: YES',
        r'(?i)X-Spam-Status: Yes',
        r'(?i)X-Spam-Level: \*\*\*\*',
        r'(?i)X-Spam-Score: [5-9]',
        r'(?i)X-Spam-Bar: \+\+\+\+'
    ]
}

def check_optional_imports():
    """Verifica si las importaciones opcionales están disponibles directamente"""
    missing = []
    try:
        # Intentar importar directamente. Si el script se ejecuta correctamente
        # (ej. activando venv o con python -m), esto debería funcionar.
        import dns.resolver
        import bs4
        import html2text
        import requests
        logging.debug("Todas las dependencias opcionales se importaron correctamente.")
    except ImportError as e:
        logging.warning(f"Error al importar dependencias opcionales: {e}")
        # Identificar qué paquete falta basado en el error de importación
        module_name = str(e).split("'")[-2]
        for mod, pkg in OPTIONAL_IMPORTS.items():
             # Usamos startswith porque dns.resolver viene de dnspython
            if mod.startswith(module_name):
                missing.append(pkg)

        # Si no pudimos identificarlo, añadimos todos como potencialmente faltantes
        if not missing:
             missing.extend(list(OPTIONAL_IMPORTS.values()))

        logging.warning(f"Faltan dependencias para detección de spam: {', '.join(missing)}")
        print(f"\n{COLORS['YELLOW']}Advertencia: Faltan algunas dependencias para la detección de spam{COLORS['RESET']}")
        print("Para instalar las dependencias faltantes, ejecuta:")
        print(f"{SCRIPT_NAME} --install")

    return missing

def check_spam_rules(email_message):
    """Verifica reglas de spam en el correo"""
    global dns, BeautifulSoup, html2text, requests # Marcar como globales para asignación

    # Intentar importar módulos necesarios al inicio de la función
    try:
        import dns.resolver
        from bs4 import BeautifulSoup
        import html2text
        import requests
    except ImportError:
        missing = check_optional_imports() # Llama a la función actualizada
        if missing:
            logging.warning(f"Faltan dependencias para detección de spam: {', '.join(missing)}")
            return 0, ["Detección de spam deshabilitada por falta de dependencias"]
        else:
            # Si check_optional_imports no encontró faltantes pero la importación falló, hay otro problema
            logging.error("Error inesperado al importar dependencias opcionales, aunque parecen estar instaladas.")
            return 0, ["Error al cargar dependencias de detección de spam"]

    spam_score = 0
    spam_reasons = []

    # Verificar reglas de asunto
    subject_header = email_message.get('subject', '')
    # Ensure subject is a string before regex
    if isinstance(subject_header, email.header.Header):
        subject = _decode_header(subject_header)
    elif isinstance(subject_header, str):
        subject = subject_header
    else:
        # Fallback if it's something unexpected
        subject = str(subject_header)
        logging.warning(f"Tipo inesperado para asunto: {type(subject_header)}, convirtiendo a string.")

    for rule in DEFAULT_SPAM_RULES['subject_rules']:
        try:
            if re.search(rule, subject):
                spam_score += 1
                spam_reasons.append(f"Asunto coincide con patrón de spam: {rule}")
        except TypeError as te:
            # This should ideally not happen now, but log if it does
            logging.error(f"TypeError en re.search de asunto: {te}. Asunto: '{subject}' (Tipo: {type(subject)}), Regla: '{rule}'")
            logging.error(traceback.format_exc())

    # Verificar reglas de cuerpo
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            charset = part.get_content_charset() or 'utf-8' # Default to utf-8
            if content_type == "text/plain":
                try:
                    body += part.get_payload(decode=True).decode(charset, errors='replace')
                except (UnicodeDecodeError, LookupError):
                    # Fallback to latin-1 or replace errors
                    try:
                         body += part.get_payload(decode=True).decode('latin-1', errors='replace')
                    except Exception as e:
                        logging.warning(f"Error decodificando parte plain: {e}")
            elif content_type == "text/html":
                try:
                    html = part.get_payload(decode=True).decode(charset, errors='replace')
                    body += html2text.html2text(html)
                except (UnicodeDecodeError, LookupError):
                     try:
                         html = part.get_payload(decode=True).decode('latin-1', errors='replace')
                         body += html2text.html2text(html)
                     except Exception as e:
                        logging.warning(f"Error decodificando parte html: {e}")
    else:
        # Single part message
        charset = email_message.get_content_charset() or 'utf-8'
        try:
            body = email_message.get_payload(decode=True).decode(charset, errors='replace')
            # Convert HTML if necessary
            if email_message.get_content_type() == "text/html":
                body = html2text.html2text(body)
        except (UnicodeDecodeError, LookupError):
            try:
                 body = email_message.get_payload(decode=True).decode('latin-1', errors='replace')
                 if email_message.get_content_type() == "text/html":
                     body = html2text.html2text(body)
            except Exception as e:
                 logging.warning(f"Error decodificando cuerpo: {e}")

    for rule in DEFAULT_SPAM_RULES['body_rules']:
        if re.search(rule, body):
            spam_score += 1
            spam_reasons.append(f"Cuerpo coincide con patrón de spam: {rule}")

    # Verificar reglas de encabezados
    for rule in DEFAULT_SPAM_RULES['header_rules']:
        for header_key in email_message.keys():
            try:
                raw_header_value = email_message.get(header_key, "")
                # Decode the header value using the standalone function
                decoded_value = _decode_header(raw_header_value)
                header_line = f"{header_key}: {decoded_value}"
                if re.search(rule, header_line):
                    spam_score += 1
                    spam_reasons.append(f"Encabezado '{header_key}' coincide con patrón de spam: {rule}")
                    # Optimization: if one rule matches this header, no need to check other rules for the same header
                    break 
            except Exception as e:
                logging.warning(f"Error procesando encabezado '{header_key}' para reglas de spam: {e}")

    # Verificar DNSBL
    try:
        received_headers = email_message.get_all('Received', [])
        for header in received_headers:
            ip_match = re.search(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]', header)
            if ip_match:
                ip = ip_match.group(1)
                if check_dnsbl(ip):
                    spam_score += 2
                    spam_reasons.append(f"IP {ip} encontrada en lista negra")
    except Exception as e:
        logging.error(f"Error al verificar DNSBL: {str(e)}")

    return spam_score, spam_reasons

def check_dnsbl(ip_address):
    """Verifica una IP contra listas negras de DNS"""
    try:
        # Obtener la IP en formato DNSBL
        ip_parts = ip_address.split('.')
        ip_reversed = '.'.join(reversed(ip_parts))
        
        for dnsbl in DNSBL_SERVERS:
            try:
                query = f"{ip_reversed}.{dnsbl}"
                dns.resolver.resolve(query, 'A')
                return True  # IP encontrada en lista negra
            except dns.resolver.NXDOMAIN:
                continue
            except Exception as e:
                logging.debug(f"Error al consultar {dnsbl}: {str(e)}")
                continue
    except Exception as e:
        logging.error(f"Error al verificar DNSBL: {str(e)}")
    
    return False

def debug_log(func):
    """Decorador para logging de funciones"""
    def wrapper(*args, **kwargs):
        logging.debug(f"Entrando en {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logging.debug(f"Saliendo de {func.__name__}")
            return result
        except Exception as e:
            logging.error(f"Error en {func.__name__}: {str(e)}")
            logging.error(traceback.format_exc())
            raise
    return wrapper

@debug_log
def check_internet_connection():
    """Verifica la conexión a internet usando IPv4 e IPv6"""
    logging.debug("Iniciando verificación de conexión a internet")
    # Lista de servidores DNS para probar
    dns_servers = {
        'ipv4': [
            '8.8.8.8',  # Google DNS
            '1.1.1.1',  # Cloudflare DNS
            '9.9.9.9'   # Quad9 DNS
        ],
        'ipv6': [
            '2001:4860:4860::8888',  # Google DNS
            '2606:4700:4700::1111',  # Cloudflare DNS
            '2620:fe::fe'            # Quad9 DNS
        ]
    }

    def try_connect(host, timeout):
        logging.debug(f"Intentando conectar a {host}")
        try:
            # Crear socket según el tipo de IP
            if ':' in host:  # IPv6
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:  # IPv4
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            sock.settimeout(timeout)
            sock.connect((host, 53))  # Puerto 53 para DNS
            sock.close()
            logging.debug(f"Conexión exitosa a {host}")
            return True
        except (socket.error, socket.timeout) as e:
            logging.debug(f"Error al conectar a {host}: {str(e)}")
            return False

    # Intentar conexión IPv4
    for server in dns_servers['ipv4']:
        if try_connect(server, INTERNET_CHECK_TIMEOUT):
            logging.debug("Conexión IPv4 establecida")
            return True

    # Intentar conexión IPv6
    for server in dns_servers['ipv6']:
        if try_connect(server, INTERNET_CHECK_TIMEOUT):
            logging.debug("Conexión IPv6 establecida")
            return True

    logging.debug("No se pudo establecer conexión a internet")
    return False

@debug_log
def wait_for_internet():
    """Espera hasta que haya conexión a internet (IPv4 o IPv6)"""
    while not check_internet_connection():
        logging.warning("No hay conexión a internet (IPv4/IPv6). Esperando...")
        time.sleep(5)
    logging.info("Conexión a internet establecida")

@debug_log
def setup_virtual_env():
    """Configura un entorno virtual para el script si no existe"""
    # Usar .venv en el directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(current_dir, '.venv')

    logging.debug(f"Verificando entorno virtual en {venv_path}")

    python_path = None
    pip_path = None

    # Obtener las rutas esperadas del Python y Pip del entorno virtual
    if sys.platform == 'win32':
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
        pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
    else:
        python_path = os.path.join(venv_path, 'bin', 'python')
        pip_path = os.path.join(venv_path, 'bin', 'pip')

    # Crear entorno virtual solo si no existe
    if not os.path.exists(venv_path):
        logging.info(f"Entorno virtual no encontrado en {venv_path}. Creándolo...")
        try:
            venv.create(venv_path, with_pip=True)
            logging.info("Entorno virtual creado exitosamente.")
        except Exception as e:
            logging.error(f"Error al crear entorno virtual: {str(e)}")
            return None, None # Retornar None si la creación falla
    else:
        logging.debug("Entorno virtual ya existe.")

    # Verificar que el Python y Pip existan en las rutas esperadas
    if not os.path.exists(python_path) or not os.path.exists(pip_path):
        logging.error(f"Python ({python_path}) o Pip ({pip_path}) no encontrados en el entorno virtual.")
        # Intentar recrear si hay problemas? Podría ser una opción, pero por ahora solo logueamos.
        # Opcionalmente, se podría intentar eliminar y recrear aquí.
        return None, None # Retornar None si falta algo esencial

    logging.debug(f"Python path: {python_path}")
    logging.debug(f"Pip path: {pip_path}")

    return python_path, pip_path

def check_package_installed(package_name, python_path):
    """Verifica silenciosamente si un paquete está instalado"""
    try:
        # Verificación específica para cada paquete
        if package_name == 'beautifulsoup4':
            # Verificar que bs4 se pueda importar y usar
            test_script = """
import bs4
from bs4 import BeautifulSoup
html = '<p>test</p>'
soup = BeautifulSoup(html, 'html.parser')
print(soup.p.text)
"""
            result = subprocess.run(
                [python_path, '-c', test_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print(f"Error al verificar beautifulsoup4: {result.stderr}")
                return False
            return True

        elif package_name == 'dnspython':
            # Verificar que dns.resolver se pueda importar y usar
            test_script = """
import dns.resolver
resolver = dns.resolver.Resolver()
"""
            result = subprocess.run(
                [python_path, '-c', test_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print(f"Error al verificar dnspython: {result.stderr}")
                return False
            return True

        else:
            # Verificación general para otros paquetes
            result = subprocess.run(
                [python_path, '-c', f'import {package_name}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print(f"Error al verificar {package_name}: {result.stderr}")
                return False
            return True

    except Exception as e:
        print(f"Error al verificar {package_name}: {str(e)}")
        return False

@debug_log
def install_packages():
    """Instala los paquetes necesarios en el entorno virtual"""
    print("Configurando entorno virtual...")
    
    # Configurar el entorno virtual primero
    python_path, pip_path = setup_virtual_env()
    if not python_path or not pip_path:
        print("Error: No se pudo configurar el entorno virtual")
        return False
    
    # Lista de paquetes requeridos
    required_packages = [
        'pandas',           # Para manejo de datos y reportes
        'colorama',         # Para colores en la terminal
        'dnspython',        # Para verificación DNSBL
        'beautifulsoup4',   # Para análisis de HTML
        'html2text',        # Para convertir HTML a texto
        'requests'          # Para peticiones HTTP
    ]
    
    print("Instalando dependencias necesarias...")
    installed_successfully = True
    
    # Primero actualizar pip y herramientas básicas
    try:
        print("Actualizando herramientas básicas...")
        result = subprocess.run(
            [pip_path, 'install', '--no-cache-dir', '--upgrade', 'pip', 'setuptools', 'wheel'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"{COLORS['GREEN']}✓ Herramientas básicas actualizadas{COLORS['RESET']}")
        else:
            print(f"{COLORS['YELLOW']}Advertencia: No se pudieron actualizar las herramientas básicas: {result.stderr}{COLORS['RESET']}")
    except Exception as e:
        print(f"{COLORS['YELLOW']}Advertencia: No se pudieron actualizar las herramientas básicas: {str(e)}{COLORS['RESET']}")
    
    # Instalar paquetes uno por uno
    for package in required_packages:
        print(f"Instalando {package}...")
        try:
            # Intentar instalar el paquete
            result = subprocess.run(
                [pip_path, 'install', '--no-cache-dir', '--upgrade', package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                # Verificar que realmente se instaló
                if check_package_installed(package, python_path):
                    print(f"{COLORS['GREEN']}✓ {package} instalado exitosamente{COLORS['RESET']}")
                else:
                    print(f"{COLORS['RED']}✗ {package} no se instaló correctamente{COLORS['RESET']}")
                    if package == 'beautifulsoup4':
                        print("  Intentando instalar soupsieve...")
                        subprocess.run(
                            [pip_path, 'install', '--no-cache-dir', '--upgrade', 'soupsieve'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                    elif package == 'dnspython':
                        print("  Intentando instalar pycparser...")
                        subprocess.run(
                            [pip_path, 'install', '--no-cache-dir', '--upgrade', 'pycparser'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                    installed_successfully = False
            else:
                print(f"{COLORS['RED']}✗ Error al instalar {package}:{COLORS['RESET']}")
                print(result.stderr)
                installed_successfully = False
                
        except Exception as e:
            print(f"{COLORS['RED']}✗ Error al instalar {package}: {str(e)}{COLORS['RESET']}")
            installed_successfully = False
    
    if installed_successfully:
        print(f"\n{COLORS['GREEN']}✓ Todas las dependencias instaladas correctamente{COLORS['RESET']}")
        return True
    else:
        print(f"\n{COLORS['RED']}✗ Algunas dependencias no se instalaron correctamente{COLORS['RESET']}")
        print("Por favor, ejecuta nuevamente:")
        print(f"{SCRIPT_NAME} --install")
        return False

def load_custom_categories():
    """Carga categorías personalizadas desde el archivo categories.dat"""
    custom_categories = {}
    if os.path.exists(CATEGORIES_FILE):
        try:
            with open(CATEGORIES_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Ignorar líneas vacías y comentarios
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parsear la línea: categoria|palabras_clave|dominios|emails
                    parts = line.split('|')
                    if len(parts) >= 1:
                        category = parts[0].strip().lower()
                        keywords = parts[1].split(',') if len(parts) > 1 else []
                        domains = parts[2].split(',') if len(parts) > 2 else []
                        emails = parts[3].split(',') if len(parts) > 3 else []
                        
                        # Limpiar espacios en blanco
                        keywords = [k.strip() for k in keywords if k.strip()]
                        domains = [d.strip() for d in domains if d.strip()]
                        emails = [e.strip().lower() for e in emails if e.strip()]
                        
                        custom_categories[category] = {
                            'keywords': keywords,
                            'domains': domains,
                            'emails': emails
                        }
            
            logging.info(f"Cargadas {len(custom_categories)} categorías personalizadas")
            return custom_categories
        except Exception as e:
            logging.error(f"Error al cargar categorías personalizadas: {str(e)}")
    return {}

def _load_progress() -> Dict[str, Any]:
    """Carga el progreso guardado desde el archivo"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error al cargar el progreso desde {PROGRESS_FILE}: {str(e)}")
    return {'last_processed': 0, 'categories': {}}

def _decode_header(header: str) -> str:
    """Decodifica un encabezado de correo electrónico potencialmente codificado."""
    if not header:
        return ""
    decoded_parts = []
    try:
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                try:
                    # Intenta decodificar con el encoding proporcionado o utf-8
                    decoded_parts.append(part.decode(encoding or 'utf-8', errors='replace'))
                except LookupError:
                    # Fallback a latin-1 si el encoding no es conocido
                    decoded_parts.append(part.decode('latin-1', errors='replace'))
                except Exception as e:
                    # Otros errores de decodificación, reemplazar caracteres
                    logging.debug(f"Error decodificando parte del encabezado: {e}")
                    decoded_parts.append(part.decode('utf-8', errors='replace'))
            else:
                # Ya es un string (raro, pero posible)
                decoded_parts.append(str(part))
    except Exception as e:
         logging.error(f"Error general decodificando encabezado: {e}, Header: {header}")
         # Devuelve una representación segura si falla la decodificación
         return str(header) if isinstance(header, str) else repr(header)
    return ' '.join(decoded_parts)

class EmailManager:
    def __init__(self, email: str, password: str, server: str):
        self.email = email
        self.password = password
        self.server = server
        self.imap = None
        self.categories = {} # Restore in-memory categories for analysis run
        self.progress = _load_progress() # Load persistent progress
        self.custom_categories = load_custom_categories()

    def connect(self) -> bool:
        """Conecta al servidor IMAP"""
        try:
            self.imap = imaplib.IMAP4_SSL(self.server)
            self.imap.login(self.email, self.password)
            logging.info("Conexión exitosa al servidor IMAP")
            return True
        except Exception as e:
            logging.error(f"Error al conectar: {str(e)}")
            return False

    def close(self):
        """Cierra la conexión IMAP"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass

    def analyze_emails(self, limit: str = None, force_init: bool = False):
        """Analiza y categoriza los correos"""
        if not self.imap:
            logging.error("No hay conexión al servidor IMAP")
            return

        try:
            self.imap.select('INBOX')
            # Reset in-memory categories for this analysis run
            self.categories = {} if force_init else self.progress.get('categories', {})

            _, messages = self.imap.search(None, 'ALL')
            message_numbers = messages[0].split()

            if limit and limit.lower() != 'all':
                try:
                    limit = int(limit)
                    message_numbers = message_numbers[-limit:]
                except ValueError:
                    logging.error("El límite debe ser un número o 'all'")

            if force_init:
                # Clear progress file categories as well if starting fresh
                self.progress = {'last_processed': 0, 'categories': {}}
                self.categories = {}
            else:
                 # Load last processed ID but keep existing categories in progress
                 self.progress = _load_progress()
                 self.categories = self.progress.get('categories', {})

            total_messages = len(message_numbers)
            logging.info(f"Analizando {total_messages} correos...")
            print_info(f"Analizando {total_messages} correos...") # Inform user

            processed_count = 0
            for i, num_bytes in enumerate(message_numbers):
                num_str = num_bytes.decode() # Convert bytes to string for printing/logging
                num_int = int(num_str)

                # Inform user about progress
                print_info(f"Procesando correo {i+1}/{total_messages} (ID: {num_str})")

                if num_int <= self.progress['last_processed'] and not force_init:
                    logging.debug(f"Saltando correo ya procesado: {num_str}")
                    continue

                # --- Fetch Email --- 
                try:
                    _, msg_data = self.imap.fetch(num_bytes, '(RFC822)')
                    # Check if fetch returned data
                    if not msg_data or msg_data[0] is None:
                         logging.warning(f"No se pudo obtener datos para el correo ID: {num_str}")
                         continue # Skip this email if fetch returned no data

                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                except Exception as fetch_error:
                    logging.error(f"Error al obtener correo ID {num_str}: {fetch_error}")
                    logging.error(traceback.format_exc()) # Log fetch error traceback
                    continue # Skip this email if fetch fails
                
                # --- Process Email (Categorize & Save) --- 
                # Extraer información del correo usando la función standalone
                subject = _decode_header(email_message['subject'])
                from_addr = _decode_header(email_message['from'])
                date = email_message['date'] # Date usually doesn't need decode_header

                # Verificar si tiene adjuntos
                has_attachments = False
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is not None:
                        has_attachments = True
                        break
                
                # Inner try-except for categorization/saving part
                try:
                    # Categorizar el correo
                    category = self._categorize_email(subject, from_addr, email_message)
                    # Use self.categories for the current run
                    if category not in self.categories:
                        self.categories[category] = []
                    self.categories[category].append({
                        'subject': subject,
                        'from': from_addr,
                        'date': date,
                        'message_id': num_str,
                        'has_attachments': has_attachments
                    })

                    self.progress['last_processed'] = num_int
                    # Save current state of self.categories to self.progress before saving file
                    self.progress['categories'] = self.categories
                    self._save_progress()
                
                except TypeError as te:
                    logging.error(f"TypeError durante categorización/guardado para correo ID {num_str}: {te}")
                    logging.error(f"Subject: {subject}") # Log potentially problematic data
                    logging.error(f"From: {from_addr}")
                    logging.error(traceback.format_exc()) # Log full traceback for this specific error
                    # Loop continues automatically to next iteration
                except Exception as inner_e:
                    # Catch other potential errors within this specific block
                    logging.error(f"Error inesperado durante categorización/guardado para correo ID {num_str}: {inner_e}")
                    logging.error(traceback.format_exc())
                    # Loop continues automatically to next iteration

            # --- Loop End ---
            logging.info(f"Análisis completado. {len(self.categories)} categorías encontradas.") # Note: This log runs after the loop finishes successfully.

        except Exception as e:
            # This outer except block catches errors occurring *outside* the per-email processing loop,
            # such as issues during initial connection, mailbox selection, email ID search,
            # or other unexpected errors not caught by the inner handlers.
            logging.error(f"Error general fuera del bucle de procesamiento de correos: {e}")
            logging.error(traceback.format_exc())
            # Consider re-raising or handling appropriately depending on desired program behavior on fatal errors.
    
    def _categorize_email(self, subject: str, from_addr: str, email_message) -> str:
        """Categoriza un correo basado en su asunto, remitente y contenido"""
        subject = subject.lower()
        from_addr = from_addr.lower()

        # Verificar spam primero
        spam_score, spam_reasons = check_spam_rules(email_message)
        if spam_score >= 3:  # Umbral para considerar spam
            logging.info(f"Correo marcado como spam (score: {spam_score})")
            logging.debug(f"Razones: {', '.join(spam_reasons)}")
            return 'spam'

        # Get email date for time-based categorization
        email_date_str = email_message['date']
        email_datetime = None
        if email_date_str:
            try:
                email_datetime = parsedate_to_datetime(email_date_str)
                # Ensure it's offset-aware for comparison
                if email_datetime.tzinfo is None or email_datetime.tzinfo.utcoffset(email_datetime) is None:
                     # Naive datetime, assume UTC? Or local? Assuming UTC is safer for comparison.
                     # email_datetime = email_datetime.replace(tzinfo=datetime.timezone.utc)
                     # Let's try to make it timezone aware based on local offset if possible, fallback UTC
                     try:
                        local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
                        email_datetime = email_datetime.astimezone(local_tz) # Try converting
                     except:
                        email_datetime = email_datetime.replace(tzinfo=datetime.timezone.utc)
            except (TypeError, ValueError):
                logging.warning(f"No se pudo parsear la fecha: '{email_date_str}'")
                email_datetime = None # Mark as unparseable

        # Lista de palabras clave para cada categoría
        categories = {
            # 'accesos' rules are used below, but not returned directly if date is valid
            'accesos': {
                'keywords': ['login', 'acceso', 'access', 'contraseña', 'password', 'verificación', 'verification', 'código', 'code', '2fa'],
                'domains': ['google', 'microsoft', 'apple', 'amazon', 'facebook', 'twitter', 'instagram', 'linkedin'],
                'emails': ['noreply@google.com', 'security@microsoft.com', 'appleid@apple.com']
            },
            'redes_sociales': {
                'keywords': ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok', 'pinterest', 'youtube', 'whatsapp', 'telegram'],
                'domains': ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'tiktok.com', 'pinterest.com', 'youtube.com', 'whatsapp.com', 'telegram.org'],
                'emails': ['noreply@facebook.com', 'info@twitter.com', 'no-reply@instagram.com', 'notifications@linkedin.com']
            },
            'promociones': {
                'keywords': ['promo', 'descuento', 'oferta', 'sale', 'discount', 'coupon', 'cupón', 'rebaja', 'black friday', 'cyber monday'],
                'domains': ['amazon', 'ebay', 'walmart', 'target', 'bestbuy', 'mercadolibre', 'falabella', 'ripley'],
                'emails': ['deals@amazon.com', 'offers@ebay.com', 'promotions@walmart.com']
            },
            'cobros': {
                'keywords': ['factura', 'invoice', 'pago', 'payment', 'cobro', 'charge', 'deuda', 'debt', 'recibo', 'bill'],
                'domains': ['paypal', 'stripe', 'mercadopago', 'banco', 'bank', 'visa', 'mastercard', 'american express'],
                'emails': ['payments@paypal.com', 'billing@stripe.com', 'facturas@mercadopago.com']
            },
            'personales': {
                'keywords': ['familia', 'family', 'amigo', 'friend', 'personal', 'private', 'privado'],
                'domains': ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com'],
                'emails': []
            },
            'newsletter': {
                'keywords': ['newsletter', 'news', 'update', 'digest', 'weekly', 'monthly', 'boletín', 'actualización'],
                'domains': ['medium.com', 'substack.com', 'newsletter', 'blog'],
                'emails': ['newsletter@medium.com', 'updates@substack.com']
            },
            'trabajo': {
                'keywords': ['meeting', 'reunión', 'report', 'reporte', 'project', 'proyecto', 'task', 'tarea', 'deadline', 'fecha límite'],
                'domains': ['slack.com', 'teams.microsoft.com', 'zoom.us', 'meet.google.com', 'trello.com', 'asana.com'],
                'emails': ['notifications@slack.com', 'meetings@teams.microsoft.com']
            }
            # 'spam' category is handled earlier
        }

        # Combinar categorías predefinidas con personalizadas
        all_categories = {**categories, **self.custom_categories}
        # Remove 'accesos' from the combined list as it's handled specially
        if 'accesos' in all_categories and 'accesos' in categories:
            del all_categories['accesos']

        # --- Check for 'accesos' category first --- 
        accesos_rules = categories.get('accesos', {})
        is_accesos = False
        if accesos_rules:
            if any(keyword in subject for keyword in accesos_rules.get('keywords', [])) or \
               any(domain in from_addr for domain in accesos_rules.get('domains', [])) or \
               any(email in from_addr for email in accesos_rules.get('emails', [])):
                is_accesos = True

        if is_accesos:
            if email_datetime:
                now = datetime.datetime.now(datetime.timezone.utc)
                # Ensure 'now' and email_datetime are comparable (same awareness)
                try:
                     if now.tzinfo != email_datetime.tzinfo:
                         # Basic approach: convert email time to UTC if possible
                         email_datetime_utc = email_datetime.astimezone(datetime.timezone.utc)
                     else:
                         email_datetime_utc = email_datetime
                     delta = now - email_datetime_utc
                except Exception as tz_error:
                     logging.error(f"Error comparing dates due to timezone issues: {tz_error}. Falling back.")
                     return 'accesos' # Fallback if timezone conversion fails

                # Apply time-based rules
                if delta <= datetime.timedelta(hours=48):
                    return 'accesos_recientes'
                elif delta <= datetime.timedelta(days=365 * 2):
                    return 'accesos_a_revisar'
                else:
                    return 'accesos_a_borrar'
            else:
                # Date couldn't be parsed
                return 'accesos_fecha_invalida'

        # --- Check other categories --- 
        for category, data in all_categories.items():
            # Verificar palabras clave en el asunto
            if any(keyword in subject for keyword in data.get('keywords', [])):
                return category
            
            # Verificar dominios en el remitente
            if any(domain in from_addr for domain in data.get('domains', [])):
                return category
            
            # Verificar direcciones de correo específicas
            if any(email in from_addr for email in data.get('emails', [])):
                return category

        return 'otros'

    def generate_report(self):
        """Genera un reporte de categorías en formato CSV"""
        # Load latest progress to generate report based on last saved state
        report_progress = _load_progress()
        report_categories = report_progress.get('categories', {})

        if not report_categories:
            logging.warning("No hay categorías en el progreso guardado para generar el reporte")
            return

        try:
            import pandas as pd
            report_data = []
            for category, emails in report_categories.items():
                for email in emails:
                    report_data.append({
                        'category': category,
                        'subject': email['subject'],
                        'from': email['from'],
                        'date': email['date']
                    })

            df = pd.DataFrame(report_data)
            report_file = os.path.join(BASE_DIR, 'email_report.csv')
            df.to_csv(report_file, index=False)
            logging.info(f"Reporte generado: {report_file}")

        except Exception as e:
            logging.error(f"Error al generar el reporte: {str(e)}")

    def list_categories(self):
        """Lista las categorías y cantidad de correos"""
        # Load latest progress to list categories based on last saved state
        list_progress = _load_progress()
        list_categories = list_progress.get('categories', {})

        if not list_categories:
            print_warning("No hay categorías para mostrar (basado en el último progreso guardado)")
            print_info(f"Archivo de progreso: {PROGRESS_FILE}")
            print_info("Ejecuta --analyze para procesar nuevos correos.")
            return

        print("\nCategorías de correos (basado en el último progreso guardado):")
        print("-" * 70)
        print(f"{COLORS['CYAN']}{'Categoría':<20} {'Total':<10} {'Con Adjuntos':<15} {'Tipo':<10}{COLORS['RESET']}")
        print("-" * 70)
        
        # Recalculate attachment counts if not stored (optional, adds overhead)
        # For now, relying on data stored during analysis
        # If attachment info isn't in progress.json, we need to adjust

        for category, emails in sorted(list_categories.items()):
            total_emails = len(emails)
            # Attempt to get attachment info if stored, default to N/A
            emails_with_attachments = sum(1 for email in emails if isinstance(email, dict) and email.get('has_attachments', False))
            category_type = "Personalizada" if category in self.custom_categories else "Predefinida"
            print(f"{COLORS['CYAN']}{category:<20}{COLORS['RESET']} {total_emails:<10} {emails_with_attachments:<15} {category_type:<10}")
        print("-" * 70)
        print(f"\nPara agregar categorías personalizadas, edita el archivo: {CATEGORIES_FILE}")
        print("Formato: categoria|palabras_clave|dominios|emails")
        print("Ejemplo: redes_sociales|facebook,twitter,instagram|facebook.com,twitter.com|noreply@facebook.com,info@twitter.com")

    def delete_emails_by_category(self, category: str, dry_run: bool = True):
        """Elimina correos de una categoría específica"""
        if not self.imap:
            logging.error("No hay conexión al servidor IMAP")
            return

        # Load latest progress to get emails for deletion based on last saved state
        delete_progress = _load_progress()
        delete_categories = delete_progress.get('categories', {})

        if category not in delete_categories:
            logging.error(f"Categoría '{category}' no encontrada en el progreso guardado")
            return

        try:
            self.imap.select('INBOX')
            emails_to_delete = delete_categories[category]
            
            if dry_run:
                print(f"\nModo de prueba - Se eliminarían {len(emails_to_delete)} correos de la categoría '{category}'")
                return

            for email in emails_to_delete:
                try:
                    self.imap.store(email['message_id'], '+FLAGS', '\\Deleted')
                except Exception as e:
                    logging.error(f"Error al eliminar correo {email['message_id']}: {str(e)}")

            self.imap.expunge()
            logging.info(f"Se eliminaron {len(emails_to_delete)} correos de la categoría '{category}'")

        except Exception as e:
            logging.error(f"Error durante la eliminación: {str(e)}")

    def _save_progress(self):
        """Guarda el progreso actual"""
        try:
            # Ensure categories are included in the progress before saving
            self.progress['categories'] = self.categories
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(self.progress, f)
        except Exception as e:
            logging.error(f"Error al guardar el progreso: {str(e)}")

def show_gmail_instructions():
    """Muestra instrucciones específicas para Gmail"""
    print(f"\n{COLORS['YELLOW']}Instrucciones para Gmail:{COLORS['RESET']}")
    print("Para usar Gmail, necesitas una 'Contraseña de aplicación':")
    print("1. Activa la verificación en dos pasos en tu cuenta de Google")
    print("2. Ve a https://myaccount.google.com/security")
    print("3. Busca 'Contraseñas de aplicación'")
    print("4. Genera una nueva contraseña para esta aplicación")
    print("5. Usa esa contraseña en lugar de tu contraseña normal de Gmail")
    print("\nSi ya tienes una contraseña de aplicación, asegúrate de usarla en la configuración.")

def check_gmail_config():
    """Verifica si la configuración de Gmail es correcta"""
    if not os.path.exists(CONFIG_FILE):
        return False
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            email = config.get('email', '').lower()
            if email.endswith('@gmail.com'):
                return True
    except Exception:
        pass
    return False

def create_config_file():
    """Crea o actualiza el archivo de configuración"""
    print(f"\n{COLORS['CYAN']}Configuración del correo electrónico{COLORS['RESET']}")
    print("-" * 50)
    
    # Valores por defecto si el archivo existe
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            print(f"Archivo de configuración existente encontrado en: {CONFIG_FILE}")
        except Exception as e:
            print(f"Error al leer el archivo de configuración: {str(e)}")
    
    # Solicitar información
    print("\nIngresa la información solicitada (deja en blanco para mantener el valor actual):")
    
    # Email
    current_email = config.get('email', '')
    email = input(f"Dirección de correo electrónico [{current_email}]: ").strip()
    if not email and current_email:
        email = current_email
    elif not email:
        print(f"{COLORS['RED']}Error: La dirección de correo es obligatoria{COLORS['RESET']}")
        return False
    
    # Verificar si es Gmail
    is_gmail = email.lower().endswith('@gmail.com')
    if is_gmail:
        print(f"\n{COLORS['YELLOW']}Detectado correo de Gmail{COLORS['RESET']}")
        print("Para Gmail, necesitas usar una 'Contraseña de aplicación':")
        print("1. Activa la verificación en dos pasos en tu cuenta de Google")
        print("2. Ve a https://myaccount.google.com/security")
        print("3. Luego ve a https://myaccount.google.com/apppasswords")
        print("4. Genera una nueva contraseña para esta aplicación")
        print("5. Usa esa contraseña en lugar de tu contraseña normal de Gmail")
    
    # Password
    current_password = config.get('password', '')
    password = input(f"Contraseña del correo [{('*' * len(current_password)) if current_password else ''}]: ").strip()
    if not password and current_password:
        password = current_password
    elif not password:
        print(f"{COLORS['RED']}Error: La contraseña es obligatoria{COLORS['RESET']}")
        return False
    
    # Server
    current_server = config.get('server', '')
    server = input(f"Servidor IMAP [{current_server}]: ").strip()
    if not server and current_server:
        server = current_server
    elif not server:
        # Sugerir servidor basado en el dominio del correo
        domain = email.split('@')[-1].lower()
        common_servers = {
            'gmail.com': 'imap.gmail.com',
            'outlook.com': 'outlook.office365.com',
            'hotmail.com': 'outlook.office365.com',
            'yahoo.com': 'imap.mail.yahoo.com',
            'aol.com': 'imap.aol.com',
            'icloud.com': 'imap.mail.me.com'
        }
        if domain in common_servers:
            server = common_servers[domain]
            print(f"Servidor sugerido: {server}")
        else:
            print(f"{COLORS['RED']}Error: El servidor IMAP es obligatorio{COLORS['RESET']}")
            return False
    
    # Guardar configuración
    config = {
        'email': email,
        'password': password,
        'server': server
    }
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"\n{COLORS['GREEN']}✓ Configuración guardada en: {CONFIG_FILE}{COLORS['RESET']}")
        
        # Mostrar información de seguridad
        print(f"\n{COLORS['YELLOW']}Notas de seguridad:{COLORS['RESET']}")
        print("1. El archivo de configuración contiene información sensible")
        print("2. Asegúrate de que el archivo tenga permisos restrictivos")
        if is_gmail:
            print("3. Para Gmail, asegúrate de usar una 'Contraseña de aplicación'")
            print("4. Si tienes problemas, verifica que la verificación en dos pasos esté activada")
        print("5. No compartas este archivo con nadie")
        
        # Establecer permisos restrictivos
        os.chmod(CONFIG_FILE, 0o600)
        print(f"\n{COLORS['GREEN']}✓ Permisos del archivo actualizados a 600 (solo lectura para el propietario){COLORS['RESET']}")
        
        return True
    except Exception as e:
        print(f"{COLORS['RED']}Error al guardar la configuración: {str(e)}{COLORS['RESET']}")
        return False

def main():
    try:
        # Configurar argumentos de línea de comandos
        parser = argparse.ArgumentParser(
            description='Gestor de correos electrónicos',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
{COLORS['CYAN']}Ejemplos de uso:{COLORS['RESET']}
  # Instalar dependencias necesarias
  {SCRIPT_NAME} --install

  # Configurar credenciales de correo
  {SCRIPT_NAME} --config

  # Analizar correos (últimos 100)
  {SCRIPT_NAME} --analyze --limit 100

  # Generar reporte de categorías
  {SCRIPT_NAME} --report

  # Listar categorías disponibles
  {SCRIPT_NAME} --list

  # Eliminar correos de una categoría específica
  {SCRIPT_NAME} --delete "newsletter" --force
            """
        )

        # Argumentos de configuración
        parser.add_argument('--email', help='Dirección de correo electrónico')
        parser.add_argument('--password', help='Contraseña del correo')
        parser.add_argument('--server', help='Servidor IMAP (ej: imap.gmail.com)')
        parser.add_argument('--config', action='store_true', 
                           help='Configurar credenciales de correo')
        
        # Argumentos de funcionalidad
        parser.add_argument('--init', action='store_true', 
                           help='Iniciar análisis desde cero (ignora el progreso guardado)')
        parser.add_argument('--limit', 
                           help='Límite de correos a procesar (número o "all" para todos)')
        parser.add_argument('--analyze', action='store_true', 
                           help='Analizar correos y categorizarlos')
        parser.add_argument('--report', action='store_true', 
                           help='Generar reporte de categorías en formato CSV')
        parser.add_argument('--list', action='store_true', 
                           help='Listar categorías disponibles y cantidad de correos')
        parser.add_argument('--delete', 
                           help='Eliminar correos de una categoría específica')
        parser.add_argument('--force', action='store_true', 
                           help='Forzar eliminación (sin modo de prueba)')
        parser.add_argument('--install', action='store_true', 
                           help='Instalar dependencias necesarias')

        # Si es una solicitud de instalación, instalar y salir
        if '--install' in sys.argv:
            if install_packages():
                print("Instalación completada exitosamente")
            else:
                print("Error durante la instalación")
            sys.exit(0)

        # Si es una solicitud de configuración, configurar y salir
        if '--config' in sys.argv:
            if create_config_file():
                print("Configuración completada exitosamente")
            else:
                print("Error durante la configuración")
            sys.exit(0)

        # --- Argument Parsing --- 
        args = parser.parse_args()

        # --- List Only Mode --- 
        # Check if only list is requested (and not other actions requiring connection)
        if args.list and not (args.analyze or args.delete or args.email or args.password or args.server):
            print_info("Modo 'Listar categorías':")
            init_colors() # Initialize colors for output
            # Load data directly from files
            list_progress = _load_progress()
            list_categories_data = list_progress.get('categories', {})
            custom_categories = load_custom_categories()

            # Display categories (mimicking the relevant part of list_categories method)
            if not list_categories_data:
                print_warning("No hay categorías para mostrar (basado en el último progreso guardado)")
                print_info(f"Archivo de progreso: {PROGRESS_FILE}")
                print_info("Ejecuta --analyze para procesar nuevos correos.")
            else:
                print("\nCategorías de correos (basado en el último progreso guardado):")
                print("-" * 70)
                print(f"{COLORS['CYAN']}{'Categoría':<20} {'Total':<10} {'Con Adjuntos':<15} {'Tipo':<10}{COLORS['RESET']}")
                print("-" * 70)
                for category, emails in sorted(list_categories_data.items()):
                    total_emails = len(emails)
                    emails_with_attachments = sum(1 for email in emails if isinstance(email, dict) and email.get('has_attachments', False))
                    category_type = "Personalizada" if category in custom_categories else "Predefinida"
                    print(f"{COLORS['CYAN']}{category:<20}{COLORS['RESET']} {total_emails:<10} {emails_with_attachments:<15} {category_type:<10}")
                print("-" * 70)
                print(f"\nPara agregar categorías personalizadas, edita el archivo: {CATEGORIES_FILE}")
                print("Formato: categoria|palabras_clave|dominios|emails")
                print("Ejemplo: redes_sociales|facebook,twitter,instagram|facebook.com,twitter.com|noreply@facebook.com,info@twitter.com")
            sys.exit(0)

        # --- Standard Mode (Requires Connection) --- 
        print_info("Modo estándar: Conectando al servidor...")

        # Si es una solicitud de ayuda, mostrar ayuda y salir
        # Moved this check down as --list only mode should bypass connection
        if len(sys.argv) == 1 or '-h' in sys.argv or '--help' in sys.argv:
            parser.print_help()
            sys.exit(0)

        # Verificar si se necesita configuración
        if not os.path.exists(CONFIG_FILE):
            print(f"{COLORS['RED']}Error: No se encontró el archivo de configuración{COLORS['RESET']}")
            print("Por favor, ejecuta primero:")
            print(f"{SCRIPT_NAME} --config")
            sys.exit(1)

        # Cargar configuración
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                email = config.get('email', '')
                password = config.get('password', '')
                server = config.get('server', '')
        except Exception as e:
            print(f"{COLORS['RED']}Error al leer la configuración: {str(e)}{COLORS['RESET']}")
            sys.exit(1)

        # Verificar si es Gmail y mostrar instrucciones si es necesario
        if email.lower().endswith('@gmail.com'):
            show_gmail_instructions()
            print("\nPresiona Enter para continuar o Ctrl+C para cancelar...")
            try:
                input()
            except KeyboardInterrupt:
                print("\nOperación cancelada por el usuario")
                sys.exit(0)

        # Verificar configuración necesaria
        if not all([email, password, server]):
            print(f"{COLORS['RED']}Error: Configuración incompleta{COLORS['RESET']}")
            print("Por favor, ejecuta:")
            print(f"{SCRIPT_NAME} --config")
            sys.exit(1)

        # Crear instancia del gestor de correos
        manager = EmailManager(email, password, server)

        # Conectar al servidor
        if not manager.connect():
            if email.lower().endswith('@gmail.com'):
                print(f"\n{COLORS['RED']}Error de autenticación con Gmail{COLORS['RESET']}")
                print("Asegúrate de:")
                print("1. Usar una 'Contraseña de aplicación' en lugar de tu contraseña normal")
                print("2. Tener la verificación en dos pasos activada")
                print("3. Haber generado la contraseña de aplicación correctamente")
                print("\nEjecuta nuevamente:")
                print(f"{SCRIPT_NAME} --config")
            sys.exit(1)

        try:
            # Ejecutar acciones según los argumentos
            if args.analyze:
                manager.analyze_emails(limit=args.limit, force_init=args.init)
            
            if args.report:
                manager.generate_report()
            
            if args.delete:
                manager.delete_emails_by_category(args.delete, dry_run=not args.force)

        finally:
            manager.close()

    except KeyboardInterrupt:
        print_info("\nOperación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"""
Ha ocurrido un error inesperado:
{str(e)}

Para más detalles, consulta el archivo de log:
{LOG_FILE}
""")
        sys.exit(1)

if __name__ == "__main__":
    main() 