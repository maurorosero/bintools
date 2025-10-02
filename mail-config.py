#!/usr/bin/env python3
"""
mail-config.py - Configurador SMTP con SOPS
Compatible con Ansible, Kubernetes, Docker, Terraform, etc.

Autor: Mauro Rosero Pérez
Fecha: 2025-01-20
Versión: 1.0.0
"""

import argparse
import json
import os
import sys
import subprocess
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass
import re

# Configuración
SCRIPT_VERSION = "1.0.0"
CONFIG_DIR = Path.home() / "secure" / "sops" / "mail"
CONFIG_FILE = CONFIG_DIR / "mail-config.yml"
BACKUP_DIR = CONFIG_DIR / "backups"
LOG_DIR = Path.home() / ".logs" / "sops"
LOG_FILE = LOG_DIR / "mail-config.log"

# Colores para output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

# Proveedores SMTP predefinidos
SMTP_PROVIDERS = {
    "gmail": {
        "host": "smtp.gmail.com",
        "port": 587,
        "security": "tls",
        "description": "Google Gmail"
    },
    "outlook": {
        "host": "smtp-mail.outlook.com",
        "port": 587,
        "security": "tls",
        "description": "Microsoft Outlook"
    },
    "yahoo": {
        "host": "smtp.mail.yahoo.com",
        "port": 587,
        "security": "tls",
        "description": "Yahoo Mail"
    },
    "office365": {
        "host": "smtp.office365.com",
        "port": 587,
        "security": "tls",
        "description": "Office 365"
    },
    "custom": {
        "host": "",
        "port": 587,
        "security": "tls",
        "description": "Servidor personalizado"
    }
}

class MailConfig:
    def __init__(self):
        self.config = {}
        self.setup_directories()
    
    def setup_directories(self):
        """Crear directorios necesarios"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    def log(self, level: str, message: str):
        """Logging con colores"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if level == "INFO":
            print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")
        elif level == "SUCCESS":
            print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
        elif level == "WARNING":
            print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
        elif level == "ERROR":
            print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
        
        # Escribir a archivo de log
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} [{level}] {message}\n")
    
    def show_banner(self):
        """Mostrar banner del script"""
        print(f"{Colors.CYAN}")
        print("=" * 50)
        print(f"    MAIL CONFIG v{SCRIPT_VERSION}")
        print("=" * 50)
        print(f"{Colors.NC}")
        print("Configurador SMTP con SOPS")
        print("Compatible con Ansible, Kubernetes, Docker, Terraform, etc.")
        print()
    
    def check_sops_installed(self) -> bool:
        """Verificar si SOPS está instalado y configurado"""
        try:
            # Verificar instalación
            result = subprocess.run(["sops", "--version"], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip().split()[1]
            self.log("SUCCESS", f"✅ SOPS está instalado (versión: {version})")
            
            # Verificar configuración
            sops_config_file = Path.home() / ".config" / "sops" / "sops.yaml"
            if sops_config_file.exists():
                self.log("SUCCESS", f"✅ Configuración SOPS encontrada: {sops_config_file}")
                
                # Verificar que hay claves GPG configuradas
                try:
                    gpg_result = subprocess.run(["gpg", "--list-secret-keys", "--keyid-format", "LONG"], 
                                              capture_output=True, text=True, check=True)
                    if gpg_result.stdout.strip():
                        self.log("SUCCESS", "✅ Claves GPG disponibles para SOPS")
                        return True
                    else:
                        self.log("WARNING", "⚠️  No hay claves GPG secretas disponibles")
                        self.log("INFO", "🔧 Ejecuta: gpg-manager.py --gen-key")
                        return False
                except subprocess.CalledProcessError:
                    self.log("WARNING", "⚠️  Error verificando claves GPG")
                    return False
            else:
                self.log("WARNING", "⚠️  Archivo de configuración SOPS no encontrado")
                self.log("INFO", "🔧 Ejecuta: gpg-manager.py --sops-config")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log("ERROR", f"❌ Error ejecutando SOPS: {e.stderr.strip() if e.stderr else str(e)}")
            self.log("INFO", "🔧 Instala SOPS con: mozilla-sops.sh --install")
            return False
        except FileNotFoundError:
            self.log("ERROR", "❌ SOPS no está instalado")
            self.log("INFO", "🔧 Instala SOPS con: mozilla-sops.sh --install")
            return False
        except Exception as e:
            self.log("ERROR", f"❌ Error inesperado verificando SOPS: {str(e)}")
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validar formato de email"""
        try:
            if not email or not isinstance(email, str):
                return False
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None
        except Exception as e:
            self.log("ERROR", f"Error validando email: {str(e)}")
            return False
    
    def validate_port(self, port: int) -> bool:
        """Validar puerto"""
        try:
            if not isinstance(port, int):
                return False
            return 1 <= port <= 65535
        except Exception as e:
            self.log("ERROR", f"Error validando puerto: {str(e)}")
            return False
    
    def interactive_config(self) -> Dict[str, Any]:
        """Configuración interactiva"""
        self.log("INFO", "Iniciando configuración interactiva...")
        
        config = {}
        
        # Seleccionar proveedor
        print(f"\n{Colors.WHITE}Proveedores disponibles:{Colors.NC}")
        for i, (key, provider) in enumerate(SMTP_PROVIDERS.items(), 1):
            print(f"  {i}. {provider['description']} ({key})")
        
        while True:
            try:
                choice = input(f"\nSelecciona proveedor (1-{len(SMTP_PROVIDERS)}): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(SMTP_PROVIDERS):
                    provider_key = list(SMTP_PROVIDERS.keys())[choice_idx]
                    config['provider'] = provider_key
                    break
                else:
                    print(f"{Colors.RED}Opción inválida. Intenta de nuevo.{Colors.NC}")
            except ValueError:
                print(f"{Colors.RED}Por favor ingresa un número válido.{Colors.NC}")
        
        provider = SMTP_PROVIDERS[config['provider']]
        
        # Configuración del servidor
        if config['provider'] == 'custom':
            while True:
                host = input("Servidor SMTP: ").strip()
                if host:
                    config['host'] = host
                    break
                print(f"{Colors.RED}El servidor SMTP es requerido.{Colors.NC}")
        else:
            config['host'] = provider['host']
            self.log("INFO", f"Servidor SMTP: {config['host']}")
        
        # Puerto
        while True:
            port_input = input(f"Puerto SMTP [{provider['port']}]: ").strip()
            if not port_input:
                config['port'] = provider['port']
                break
            try:
                port = int(port_input)
                if self.validate_port(port):
                    config['port'] = port
                    break
                else:
                    print(f"{Colors.RED}Puerto inválido. Debe estar entre 1 y 65535.{Colors.NC}")
            except ValueError:
                print(f"{Colors.RED}Por favor ingresa un número válido.{Colors.NC}")
        
        # Seguridad
        security_options = ['tls', 'ssl', 'none']
        while True:
            security = input(f"Seguridad (tls/ssl/none) [{provider['security']}]: ").strip().lower()
            if not security:
                config['security'] = provider['security']
                break
            if security in security_options:
                config['security'] = security
                break
            print(f"{Colors.RED}Opción inválida. Usa: tls, ssl o none.{Colors.NC}")
        
        # Username/Email
        while True:
            username = input("Email/Username: ").strip()
            if self.validate_email(username):
                config['username'] = username
                break
            print(f"{Colors.RED}Formato de email inválido.{Colors.NC}")
        
        # Password
        while True:
            password = getpass.getpass("Contraseña: ")
            if password:
                config['password'] = password
                break
            print(f"{Colors.RED}La contraseña es requerida.{Colors.NC}")
        
        # From name
        from_name = input("Nombre del remitente: ").strip()
        if not from_name:
            from_name = username.split('@')[0].title()
        config['from_name'] = from_name
        
        # From email
        while True:
            from_email = input(f"Email del remitente [{username}]: ").strip()
            if not from_email:
                config['from_email'] = username
                break
            if self.validate_email(from_email):
                config['from_email'] = from_email
                break
            print(f"{Colors.RED}Formato de email inválido.{Colors.NC}")
        
        return config
    
    def test_smtp_connection(self, config: Dict[str, Any], test_recipient: Optional[str] = None) -> bool:
        """Probar conexión SMTP"""
        self.log("INFO", "Probando conexión SMTP...")
        
        server = None
        try:
            # Validar configuración requerida
            required_fields = ['host', 'port', 'security', 'username', 'password']
            for field in required_fields:
                if field not in config or not config[field]:
                    self.log("ERROR", f"Campo requerido faltante: {field}")
                    return False
            
            # Validar email del destinatario si se proporciona
            if test_recipient and not self.validate_email(test_recipient):
                self.log("ERROR", f"Email de destinatario inválido: {test_recipient}")
                return False
            
            # Crear conexión SMTP con timeout
            timeout = 30
            if config['security'] == 'ssl':
                server = smtplib.SMTP_SSL(config['host'], config['port'], timeout=timeout)
            else:
                server = smtplib.SMTP(config['host'], config['port'], timeout=timeout)
                if config['security'] == 'tls':
                    server.starttls()
            
            # Configurar debug si es necesario
            # server.set_debuglevel(1)  # Descomentar para debug
            
            # Autenticación
            server.login(config['username'], config['password'])
            
            # Enviar email de prueba si se especifica destinatario
            if test_recipient:
                self.log("INFO", f"Enviando email de prueba a {test_recipient}...")
                
                msg = MIMEMultipart()
                msg['From'] = f"{config['from_name']} <{config['from_email']}>"
                msg['To'] = test_recipient
                msg['Subject'] = "Prueba de configuración SMTP"
                
                body = f"""
Este es un email de prueba enviado desde mail-config.py

Configuración:
- Servidor: {config['host']}:{config['port']}
- Seguridad: {config['security']}
- Usuario: {config['username']}
- Remitente: {config['from_name']} <{config['from_email']}>

Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                msg.attach(MIMEText(body, 'plain'))
                
                server.send_message(msg)
                self.log("SUCCESS", f"Email de prueba enviado exitosamente a {test_recipient}")
            
            self.log("SUCCESS", "Conexión SMTP exitosa")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.log("ERROR", f"Error de autenticación SMTP: {str(e)}")
            self.log("INFO", "Verifica el usuario y contraseña")
            return False
        except smtplib.SMTPConnectError as e:
            self.log("ERROR", f"Error conectando al servidor SMTP: {str(e)}")
            self.log("INFO", f"Verifica el host ({config.get('host', 'N/A')}) y puerto ({config.get('port', 'N/A')})")
            return False
        except smtplib.SMTPException as e:
            self.log("ERROR", f"Error SMTP: {str(e)}")
            return False
        except ConnectionError as e:
            self.log("ERROR", f"Error de conexión: {str(e)}")
            self.log("INFO", "Verifica la conectividad de red")
            return False
        except TimeoutError as e:
            self.log("ERROR", f"Timeout de conexión: {str(e)}")
            self.log("INFO", "El servidor no respondió en el tiempo esperado")
            return False
        except Exception as e:
            self.log("ERROR", f"Error inesperado en conexión SMTP: {str(e)}")
            return False
        finally:
            if server:
                try:
                    server.quit()
                except Exception as e:
                    self.log("WARNING", f"Error cerrando conexión SMTP: {str(e)}")
    
    def create_config_yaml(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crear estructura YAML de configuración"""
        now = datetime.now().isoformat()
        
        yaml_config = {
            'smtp': {
                'host': config['host'],
                'port': config['port'],
                'security': config['security'],
                'username': config['username'],
                'password': config['password'],  # Se encriptará con SOPS
                'from': {
                    'name': config['from_name'],
                    'email': config['from_email']
                },
                'timeout': 30,
                'retry_attempts': 3,
                'retry_delay': 5
            },
            'providers': SMTP_PROVIDERS,
            'metadata': {
                'created_at': now,
                'updated_at': now,
                'version': SCRIPT_VERSION,
                'tool': 'mail-config.py',
                'compatible_with': [
                    'ansible', 'kubernetes', 'docker', 'terraform', 
                    'python', 'nodejs', 'bash'
                ]
            },
            'ansible': {
                'env_vars': {
                    'SMTP_HOST': '{{ smtp.host }}',
                    'SMTP_PORT': '{{ smtp.port }}',
                    'SMTP_USERNAME': '{{ smtp.username }}',
                    'SMTP_PASSWORD': '{{ smtp.password }}',
                    'SMTP_FROM_NAME': '{{ smtp.from.name }}',
                    'SMTP_FROM_EMAIL': '{{ smtp.from.email }}'
                }
            },
            'kubernetes': {
                'secret_name': 'mail-config',
                'secret_type': 'Opaque',
                'data_keys': {
                    'host': 'smtp.host',
                    'port': 'smtp.port',
                    'username': 'smtp.username',
                    'password': 'smtp.password',
                    'from_name': 'smtp.from.name',
                    'from_email': 'smtp.from.email'
                }
            },
            'docker': {
                'environment': [
                    'SMTP_HOST={{ smtp.host }}',
                    'SMTP_PORT={{ smtp.port }}',
                    'SMTP_USERNAME={{ smtp.username }}',
                    'SMTP_PASSWORD={{ smtp.password }}',
                    'SMTP_FROM_NAME={{ smtp.from.name }}',
                    'SMTP_FROM_EMAIL={{ smtp.from.email }}'
                ]
            },
            'terraform': {
                'variables': {
                    'input_variables': [
                        {
                            'name': 'mail_host',
                            'type': 'string',
                            'description': 'Mail server hostname',
                            'default': '{{ smtp.host }}'
                        },
                        {
                            'name': 'mail_port',
                            'type': 'number',
                            'description': 'Mail server port',
                            'default': '{{ smtp.port }}'
                        },
                        {
                            'name': 'mail_username',
                            'type': 'string',
                            'description': 'Mail username',
                            'default': '{{ smtp.username }}'
                        },
                        {
                            'name': 'mail_password',
                            'type': 'string',
                            'description': 'Mail password',
                            'sensitive': True,
                            'default': '{{ smtp.password }}'
                        },
                        {
                            'name': 'mail_from_name',
                            'type': 'string',
                            'description': 'Mail from name',
                            'default': '{{ smtp.from.name }}'
                        },
                        {
                            'name': 'mail_from_email',
                            'type': 'string',
                            'description': 'Mail from email',
                            'default': '{{ smtp.from.email }}'
                        }
                    ]
                }
            },
            'validation': {
                'rules': [
                    {
                        'field': 'smtp.host',
                        'type': 'string',
                        'required': True,
                        'pattern': '^[a-zA-Z0-9.-]+$'
                    },
                    {
                        'field': 'smtp.port',
                        'type': 'integer',
                        'required': True,
                        'min': 1,
                        'max': 65535
                    },
                    {
                        'field': 'smtp.username',
                        'type': 'email',
                        'required': True
                    },
                    {
                        'field': 'smtp.password',
                        'type': 'string',
                        'required': True,
                        'min_length': 1
                    },
                    {
                        'field': 'smtp.from.email',
                        'type': 'email',
                        'required': True
                    }
                ]
            },
            'logging': {
                'level': 'info',
                'format': 'json',
                'file': str(LOG_FILE)
            },
            'monitoring': {
                'health_check': {
                    'enabled': True,
                    'interval': 300,
                    'timeout': 30,
                    'retry_attempts': 3
                }
            }
        }
        
        return yaml_config
    
    def save_config(self, config: Dict[str, Any], backup: bool = True) -> bool:
        """Guardar configuración encriptada con SOPS"""
        tmp_file_path = None
        try:
            # Validar configuración
            if not config:
                self.log("ERROR", "Configuración vacía")
                return False
            
            # Crear backup si existe configuración anterior
            if backup and CONFIG_FILE.exists():
                try:
                    backup_file = BACKUP_DIR / f"mail-config-{datetime.now().strftime('%Y%m%d-%H%M%S')}.yml"
                    subprocess.run(["cp", str(CONFIG_FILE), str(backup_file)], check=True)
                    self.log("INFO", f"Backup creado: {backup_file}")
                except subprocess.CalledProcessError as e:
                    self.log("WARNING", f"Error creando backup: {str(e)}")
                    self.log("INFO", "Continuando sin backup...")
                except Exception as e:
                    self.log("WARNING", f"Error inesperado creando backup: {str(e)}")
                    self.log("INFO", "Continuando sin backup...")
            
            # Crear archivo temporal con configuración
            yaml_config = self.create_config_yaml(config)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tmp_file:
                yaml.dump(yaml_config, tmp_file, default_flow_style=False, sort_keys=False)
                tmp_file_path = tmp_file.name
            
            # Verificar que el archivo temporal se creó correctamente
            if not os.path.exists(tmp_file_path) or os.path.getsize(tmp_file_path) == 0:
                self.log("ERROR", "Error creando archivo temporal")
                return False
            
            # Encriptar con SOPS
            try:
                sops_config_file = Path.home() / ".config" / "sops" / "sops.yaml"
                if sops_config_file.exists():
                    result = subprocess.run([
                        "sops", "--config", str(sops_config_file),
                        "--encrypt", "--in-place", tmp_file_path
                    ], capture_output=True, text=True, check=True)
                else:
                    result = subprocess.run([
                        "sops", "--encrypt", "--in-place", tmp_file_path
                    ], capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else str(e)
                
                # Análisis específico de errores SOPS
                if "config file not found" in error_msg or "no creation rules" in error_msg:
                    self.log("ERROR", "❌ SOPS no está configurado correctamente")
                    self.log("INFO", "🔧 Soluciones:")
                    self.log("INFO", "   1. Ejecuta: gpg-manager.py --sops-config")
                    self.log("INFO", "   2. Verifica que tienes claves GPG: gpg --list-secret-keys")
                    self.log("INFO", "   3. Verifica el archivo: ~/.config/sops/sops.yaml")
                elif "no keys provided" in error_msg:
                    self.log("ERROR", "❌ No hay claves GPG disponibles para SOPS")
                    self.log("INFO", "🔧 Soluciones:")
                    self.log("INFO", "   1. Genera una clave GPG: gpg-manager.py --gen-key")
                    self.log("INFO", "   2. Configura SOPS: gpg-manager.py --sops-config")
                elif "permission denied" in error_msg.lower():
                    self.log("ERROR", "❌ Error de permisos al acceder al archivo")
                    self.log("INFO", "🔧 Verifica los permisos del archivo temporal")
                elif "timeout" in error_msg.lower():
                    self.log("ERROR", "❌ Timeout al encriptar con SOPS")
                    self.log("INFO", "🔧 SOPS está tardando demasiado, verifica el sistema")
                else:
                    self.log("ERROR", f"❌ Error inesperado de SOPS: {error_msg}")
                
                self.log("INFO", f"📋 Comando fallido: {' '.join(e.cmd)}")
                self.log("INFO", f"📋 Código de salida: {e.returncode}")
                return False
            
            # Verificar que el archivo se encriptó correctamente
            if not os.path.exists(tmp_file_path) or os.path.getsize(tmp_file_path) == 0:
                self.log("ERROR", "Error encriptando archivo")
                return False
            
            # Mover archivo encriptado a ubicación final
            try:
                subprocess.run(["mv", tmp_file_path, str(CONFIG_FILE)], check=True)
                tmp_file_path = None  # Marcar como movido para no eliminar
            except subprocess.CalledProcessError as e:
                self.log("ERROR", f"Error moviendo archivo: {str(e)}")
                return False
            
            # Establecer permisos seguros
            try:
                os.chmod(CONFIG_FILE, 0o600)
            except Exception as e:
                self.log("WARNING", f"Error estableciendo permisos: {str(e)}")
            
            # Verificar que el archivo final existe y tiene contenido
            if not CONFIG_FILE.exists() or CONFIG_FILE.stat().st_size == 0:
                self.log("ERROR", "Archivo de configuración no se creó correctamente")
                return False
            
            self.log("SUCCESS", f"Configuración guardada en: {CONFIG_FILE}")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Error inesperado al guardar configuración: {str(e)}")
            return False
        finally:
            # Limpiar archivo temporal si existe
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                except Exception as e:
                    self.log("WARNING", f"Error eliminando archivo temporal: {str(e)}")
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Cargar configuración desencriptada"""
        try:
            if not CONFIG_FILE.exists():
                self.log("INFO", "Archivo de configuración no existe")
                return None
            
            if CONFIG_FILE.stat().st_size == 0:
                self.log("ERROR", "Archivo de configuración está vacío")
                return None
            
            sops_config_file = Path.home() / ".config" / "sops" / "sops.yaml"
            if sops_config_file.exists():
                result = subprocess.run([
                    "sops", "--config", str(sops_config_file),
                    "--decrypt", str(CONFIG_FILE)
                ], capture_output=True, text=True, check=True)
            else:
                result = subprocess.run([
                    "sops", "--decrypt", str(CONFIG_FILE)
                ], capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                self.log("ERROR", "SOPS no devolvió contenido")
                return None
            
            config = yaml.safe_load(result.stdout)
            if not config:
                self.log("ERROR", "Configuración YAML inválida o vacía")
                return None
            
            return config
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            
            # Análisis específico de errores SOPS para desencriptación
            if "config file not found" in error_msg or "no creation rules" in error_msg:
                self.log("ERROR", "❌ SOPS no está configurado correctamente")
                self.log("INFO", "🔧 Soluciones:")
                self.log("INFO", "   1. Ejecuta: gpg-manager.py --sops-config")
                self.log("INFO", "   2. Verifica que tienes claves GPG: gpg --list-secret-keys")
                self.log("INFO", "   3. Verifica el archivo: ~/.config/sops/sops.yaml")
            elif "no keys provided" in error_msg or "no decryption keys" in error_msg:
                self.log("ERROR", "❌ No hay claves GPG disponibles para desencriptar")
                self.log("INFO", "🔧 Soluciones:")
                self.log("INFO", "   1. Verifica que tienes la clave correcta: gpg --list-secret-keys")
                self.log("INFO", "   2. Importa la clave si es necesario: gpg --import clave.asc")
                self.log("INFO", "   3. Configura SOPS: gpg-manager.py --sops-config")
            elif "failed to decrypt" in error_msg or "decryption failed" in error_msg:
                self.log("ERROR", "❌ Error al desencriptar el archivo")
                self.log("INFO", "🔧 Posibles causas:")
                self.log("INFO", "   1. El archivo fue encriptado con una clave diferente")
                self.log("INFO", "   2. La clave GPG no está disponible o ha expirado")
                self.log("INFO", "   3. El archivo está corrupto")
            elif "permission denied" in error_msg.lower():
                self.log("ERROR", "❌ Error de permisos al acceder al archivo")
                self.log("INFO", "🔧 Verifica los permisos del archivo de configuración")
            else:
                self.log("ERROR", f"❌ Error inesperado al desencriptar: {error_msg}")
            
            self.log("INFO", f"📋 Comando fallido: {' '.join(e.cmd)}")
            self.log("INFO", f"📋 Código de salida: {e.returncode}")
            return None
        except yaml.YAMLError as e:
            self.log("ERROR", f"Error parseando YAML: {str(e)}")
            return None
        except Exception as e:
            self.log("ERROR", f"Error inesperado al cargar configuración: {str(e)}")
            return None
    
    def generate_output(self, output_format: str, output_file: Optional[str] = None, 
                       output_dir: Optional[str] = None, terraform_provider: Optional[str] = None):
        """Generar salida en diferentes formatos"""
        config = self.load_config()
        if not config:
            self.log("ERROR", "No hay configuración disponible")
            return False
        
        try:
            if output_format == "json":
                output_data = {
                    "status": "success",
                    "message": "Configuración SMTP",
                    "timestamp": datetime.now().isoformat(),
                    "data": config
                }
                
                if output_file:
                    try:
                        with open(output_file, 'w') as f:
                            json.dump(output_data, f, indent=2)
                        self.log("SUCCESS", f"Configuración JSON guardada en: {output_file}")
                    except IOError as e:
                        self.log("ERROR", f"Error escribiendo archivo JSON: {str(e)}")
                        return False
                else:
                    print(json.dumps(output_data, indent=2))
            
            elif output_format == "yaml":
                if output_file:
                    try:
                        with open(output_file, 'w') as f:
                            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                        self.log("SUCCESS", f"Configuración YAML guardada en: {output_file}")
                    except IOError as e:
                        self.log("ERROR", f"Error escribiendo archivo YAML: {str(e)}")
                        return False
                else:
                    print(yaml.dump(config, default_flow_style=False, sort_keys=False))
            
            elif output_format == "env":
                try:
                    # Validar que la configuración SMTP existe
                    if 'smtp' not in config:
                        self.log("ERROR", "Configuración SMTP no encontrada")
                        return False
                    
                    smtp_config = config['smtp']
                    required_fields = ['host', 'port', 'username', 'password', 'from']
                    
                    for field in required_fields:
                        if field not in smtp_config:
                            self.log("ERROR", f"Campo SMTP requerido faltante: {field}")
                            return False
                    
                    if 'name' not in smtp_config['from'] or 'email' not in smtp_config['from']:
                        self.log("ERROR", "Campos 'from.name' y 'from.email' requeridos")
                        return False
                    
                    env_vars = [
                        f"SMTP_HOST={smtp_config['host']}",
                        f"SMTP_PORT={smtp_config['port']}",
                        f"SMTP_USERNAME={smtp_config['username']}",
                        f"SMTP_PASSWORD={smtp_config['password']}",
                        f"SMTP_FROM_NAME={smtp_config['from']['name']}",
                        f"SMTP_FROM_EMAIL={smtp_config['from']['email']}"
                    ]
                    
                    if output_file:
                        try:
                            with open(output_file, 'w') as f:
                                f.write('\n'.join(env_vars))
                            self.log("SUCCESS", f"Variables de entorno guardadas en: {output_file}")
                        except IOError as e:
                            self.log("ERROR", f"Error escribiendo archivo ENV: {str(e)}")
                            return False
                    else:
                        print('\n'.join(env_vars))
                        
                except KeyError as e:
                    self.log("ERROR", f"Campo de configuración faltante: {str(e)}")
                    return False
            
            elif output_format == "terraform":
                if not terraform_provider:
                    self.log("ERROR", "Proveedor Terraform requerido para formato terraform")
                    return False
                self.generate_terraform_config(config, output_dir, terraform_provider)
            
            else:
                self.log("ERROR", f"Formato de salida no soportado: {output_format}")
                return False
            
            return True
            
        except Exception as e:
            self.log("ERROR", f"Error inesperado al generar salida: {str(e)}")
            return False
    
    def generate_terraform_config(self, config: Dict[str, Any], output_dir: Optional[str], 
                                 provider: Optional[str]):
        """Generar configuración Terraform"""
        try:
            # Validar configuración
            if 'smtp' not in config:
                self.log("ERROR", "Configuración SMTP no encontrada")
                return
            
            smtp_config = config['smtp']
            required_fields = ['host', 'port', 'username', 'password', 'from']
            
            for field in required_fields:
                if field not in smtp_config:
                    self.log("ERROR", f"Campo SMTP requerido faltante: {field}")
                    return
            
            if 'name' not in smtp_config['from'] or 'email' not in smtp_config['from']:
                self.log("ERROR", "Campos 'from.name' y 'from.email' requeridos")
                return
            
            if not output_dir:
                output_dir = "./terraform"
            
            output_path = Path(output_dir)
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.log("ERROR", f"Error creando directorio de salida: {str(e)}")
                return
            
            providers = ["aws", "azure", "gcp", "kubernetes"] if provider == "all" else [provider]
            
            for prov in providers:
                try:
                    prov_dir = output_path / prov
                    prov_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Generar variables.tf
                    variables_content = f'''# Variables para configuración SMTP
# Generado automáticamente por mail-config.py

variable "mail_host" {{
  description = "Mail server hostname"
  type        = string
  default     = "{smtp_config['host']}"
}}

variable "mail_port" {{
  description = "Mail server port"
  type        = number
  default     = {smtp_config['port']}
}}

variable "mail_username" {{
  description = "Mail username"
  type        = string
  default     = "{smtp_config['username']}"
}}

variable "mail_password" {{
  description = "Mail password"
  type        = string
  sensitive   = true
  default     = "{smtp_config['password']}"
}}

variable "mail_from_name" {{
  description = "Mail from name"
  type        = string
  default     = "{smtp_config['from']['name']}"
}}

variable "mail_from_email" {{
  description = "Mail from email"
  type        = string
  default     = "{smtp_config['from']['email']}"
}}
'''
                    
                    with open(prov_dir / "variables.tf", 'w') as f:
                        f.write(variables_content)
                    
                    # Generar main.tf según el proveedor
                    if prov == "aws":
                        main_content = f'''# Configuración SMTP para AWS
# Generado automáticamente por mail-config.py

resource "aws_secretsmanager_secret" "mail_config" {{
  name        = "mail-config"
  description = "Mail configuration for applications"
  
  tags = {{
    Name        = "mail-config"
    Environment = "production"
    ManagedBy   = "terraform"
  }}
}}

resource "aws_secretsmanager_secret_version" "mail_config" {{
  secret_id = aws_secretsmanager_secret.mail_config.id
  secret_string = jsonencode({{
    host      = var.mail_host
    port      = var.mail_port
    username  = var.mail_username
    password  = var.mail_password
    from_name = var.mail_from_name
    from_email = var.mail_from_email
  }})
}}
'''
                    elif prov == "azure":
                        main_content = f'''# Configuración SMTP para Azure
# Generado automáticamente por mail-config.py

resource "azurerm_key_vault_secret" "mail_config" {{
  name         = "mail-config"
  value        = jsonencode({{
    host      = var.mail_host
    port      = var.mail_port
    username  = var.mail_username
    password  = var.mail_password
    from_name = var.mail_from_name
    from_email = var.mail_from_email
  }})
  key_vault_id = var.key_vault_id
  
  tags = {{
    Name        = "mail-config"
    Environment = "production"
    ManagedBy   = "terraform"
  }}
}}
'''
                    elif prov == "gcp":
                        main_content = f'''# Configuración SMTP para Google Cloud Platform
# Generado automáticamente por mail-config.py

resource "google_secret_manager_secret" "mail_config" {{
  secret_id = "mail-config"
  
  replication {{
    automatic = true
  }}
  
  labels = {{
    name        = "mail-config"
    environment = "production"
    managed_by  = "terraform"
  }}
}}

resource "google_secret_manager_secret_version" "mail_config" {{
  secret = google_secret_manager_secret.mail_config.id
  secret_data = jsonencode({{
    host      = var.mail_host
    port      = var.mail_port
    username  = var.mail_username
    password  = var.mail_password
    from_name = var.mail_from_name
    from_email = var.mail_from_email
  }})
}}
'''
                    elif prov == "kubernetes":
                        main_content = f'''# Configuración SMTP para Kubernetes
# Generado automáticamente por mail-config.py

resource "kubernetes_secret" "mail_config" {{
  metadata {{
    name      = "mail-config"
    namespace = var.namespace
  }}
  
  type = "Opaque"
  
  data = {{
    host      = base64encode(var.mail_host)
    port      = base64encode(tostring(var.mail_port))
    username  = base64encode(var.mail_username)
    password  = base64encode(var.mail_password)
    from_name = base64encode(var.mail_from_name)
    from_email = base64encode(var.mail_from_email)
  }}
}}
'''
            
                    with open(prov_dir / "main.tf", 'w') as f:
                        f.write(main_content)
                    
                    # Generar outputs.tf
                    outputs_content = f'''# Outputs para configuración SMTP
# Generado automáticamente por mail-config.py

output "mail_host" {{
  description = "Mail host"
  value       = var.mail_host
}}

output "mail_port" {{
  description = "Mail port"
  value       = var.mail_port
}}

output "mail_username" {{
  description = "Mail username"
  value       = var.mail_username
}}

output "mail_from_name" {{
  description = "Mail from name"
  value       = var.mail_from_name
}}

output "mail_from_email" {{
  description = "Mail from email"
  value       = var.mail_from_email
}}
'''
                    
                    with open(prov_dir / "outputs.tf", 'w') as f:
                        f.write(outputs_content)
                    
                    self.log("SUCCESS", f"Configuración Terraform para {prov} generada en: {prov_dir}")
                    
                except Exception as e:
                    self.log("ERROR", f"Error generando configuración para {prov}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.log("ERROR", f"Error inesperado generando configuración Terraform: {str(e)}")
    
    def list_providers(self):
        """Listar proveedores disponibles"""
        print(f"\n{Colors.WHITE}Proveedores SMTP disponibles:{Colors.NC}")
        for key, provider in SMTP_PROVIDERS.items():
            print(f"  {key}: {provider['description']}")
            print(f"    Host: {provider['host']}")
            print(f"    Puerto: {provider['port']}")
            print(f"    Seguridad: {provider['security']}")
            print()
    
    def show_config(self):
        """Mostrar configuración actual"""
        config = self.load_config()
        if not config:
            self.log("WARNING", "No hay configuración disponible")
            return
        
        try:
            # Validar estructura de configuración
            if 'smtp' not in config:
                self.log("ERROR", "Configuración SMTP no encontrada")
                return
            
            smtp_config = config['smtp']
            required_fields = ['host', 'port', 'security', 'username', 'from']
            
            for field in required_fields:
                if field not in smtp_config:
                    self.log("ERROR", f"Campo SMTP requerido faltante: {field}")
                    return
            
            if 'name' not in smtp_config['from'] or 'email' not in smtp_config['from']:
                self.log("ERROR", "Campos 'from.name' y 'from.email' requeridos")
                return
            
            print(f"\n{Colors.WHITE}Configuración SMTP actual:{Colors.NC}")
            print(f"  Servidor: {smtp_config['host']}:{smtp_config['port']}")
            print(f"  Seguridad: {smtp_config['security']}")
            print(f"  Usuario: {smtp_config['username']}")
            print(f"  Remitente: {smtp_config['from']['name']} <{smtp_config['from']['email']}>")
            
            # Mostrar metadatos si están disponibles
            if 'metadata' in config:
                metadata = config['metadata']
                if 'created_at' in metadata:
                    print(f"  Creado: {metadata['created_at']}")
                if 'updated_at' in metadata:
                    print(f"  Actualizado: {metadata['updated_at']}")
                if 'version' in metadata:
                    print(f"  Versión: {metadata['version']}")
                if 'tool' in metadata:
                    print(f"  Herramienta: {metadata['tool']}")
                    
        except Exception as e:
            self.log("ERROR", f"Error mostrando configuración: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description="Configurador SMTP con SOPS - Compatible con Ansible, Kubernetes, Docker, Terraform, etc.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s --interactive                    # Configuración interactiva
  %(prog)s --provider gmail --username user@gmail.com --password pass
  %(prog)s --test --test-recipient test@example.com
  %(prog)s --output-format json --output-file config.json
  %(prog)s --output-format terraform --terraform-provider aws --output-dir ./terraform
        """
    )
    
    # Configuración
    parser.add_argument("--interactive", action="store_true", 
                       help="Modo interactivo (por defecto)")
    parser.add_argument("--provider", choices=list(SMTP_PROVIDERS.keys()),
                       help="Proveedor SMTP")
    parser.add_argument("--host", help="Servidor SMTP")
    parser.add_argument("--port", type=int, help="Puerto SMTP")
    parser.add_argument("--security", choices=['tls', 'ssl', 'none'], help="Seguridad")
    parser.add_argument("--username", help="Nombre de usuario/email")
    parser.add_argument("--password", help="Contraseña (o - para leer desde stdin)")
    parser.add_argument("--from-name", help="Nombre del remitente")
    parser.add_argument("--from-email", help="Email del remitente")
    
    # Validación y testing
    parser.add_argument("--test", action="store_true", help="Probar configuración")
    parser.add_argument("--test-recipient", help="Email de destino para prueba")
    parser.add_argument("--validate-only", action="store_true", 
                       help="Solo validar configuración sin guardar")
    
    # Salidas estándar
    parser.add_argument("--output-format", 
                       choices=['json', 'yaml', 'env', 'terraform'],
                       help="Formato de salida")
    parser.add_argument("--output-file", help="Archivo de salida")
    parser.add_argument("--output-dir", help="Directorio de salida (para terraform)")
    parser.add_argument("--terraform-provider", 
                       choices=['aws', 'azure', 'gcp', 'kubernetes', 'all'],
                       help="Proveedor Terraform")
    parser.add_argument("--export-env", action="store_true", 
                       help="Exportar variables de entorno")
    
    # Utilidades
    parser.add_argument("--backup", action="store_true", 
                       help="Crear backup antes de sobrescribir")
    parser.add_argument("--restore", help="Restaurar desde backup")
    parser.add_argument("--list-providers", action="store_true", 
                       help="Listar proveedores disponibles")
    parser.add_argument("--show-config", action="store_true", 
                       help="Mostrar configuración actual")
    
    args = parser.parse_args()
    
    # Crear instancia del configurador
    mail_config = MailConfig()
    
    # Mostrar banner
    mail_config.show_banner()
    
    # Verificar SOPS
    if not mail_config.check_sops_installed():
        sys.exit(1)
    
    # Procesar argumentos
    if args.list_providers:
        mail_config.list_providers()
        return
    
    if args.show_config:
        mail_config.show_config()
        return
    
    if args.output_format:
        mail_config.generate_output(
            args.output_format, 
            args.output_file, 
            args.output_dir, 
            args.terraform_provider
        )
        return
    
    # Configuración
    try:
        if args.test:
            # Modo test - cargar configuración existente
            config_data = mail_config.load_config()
            if not config_data:
                mail_config.log("ERROR", "No hay configuración disponible para probar")
                mail_config.log("INFO", "Ejecuta primero: mail-config.py --interactive")
                sys.exit(1)
            
            # Extraer configuración SMTP del formato YAML
            if 'smtp' not in config_data:
                mail_config.log("ERROR", "Configuración SMTP no encontrada en el archivo")
                sys.exit(1)
            
            smtp_config = config_data['smtp']
            config = {
                'host': smtp_config['host'],
                'port': smtp_config['port'],
                'security': smtp_config['security'],
                'username': smtp_config['username'],
                'password': smtp_config['password'],
                'from_name': smtp_config['from']['name'],
                'from_email': smtp_config['from']['email']
            }
        elif args.interactive or not any([args.provider, args.host, args.username]):
            # Modo interactivo
            config = mail_config.interactive_config()
        else:
            # Modo automático
            if not args.provider or not args.username:
                mail_config.log("ERROR", "Se requieren --provider y --username para modo automático")
                sys.exit(1)
            
            # Validar proveedor
            if args.provider not in SMTP_PROVIDERS:
                mail_config.log("ERROR", f"Proveedor no válido: {args.provider}")
                mail_config.log("INFO", f"Proveedores disponibles: {', '.join(SMTP_PROVIDERS.keys())}")
                sys.exit(1)
            
            # Obtener contraseña de forma segura
            password = args.password
            if not password:
                try:
                    password = getpass.getpass("Contraseña: ")
                except (EOFError, KeyboardInterrupt):
                    mail_config.log("ERROR", "Entrada de contraseña cancelada")
                    sys.exit(1)
            
            config = {
                'provider': args.provider,
                'host': args.host or SMTP_PROVIDERS[args.provider]['host'],
                'port': args.port or SMTP_PROVIDERS[args.provider]['port'],
                'security': args.security or SMTP_PROVIDERS[args.provider]['security'],
                'username': args.username,
                'password': password,
                'from_name': args.from_name or args.username.split('@')[0].title(),
                'from_email': args.from_email or args.username
            }
        
        # Validar configuración
        if not mail_config.validate_email(config['username']):
            mail_config.log("ERROR", "Formato de email inválido")
            sys.exit(1)
        
        if not mail_config.validate_port(config['port']):
            mail_config.log("ERROR", "Puerto inválido")
            sys.exit(1)
        
        # Validar email del remitente
        if not mail_config.validate_email(config['from_email']):
            mail_config.log("ERROR", "Formato de email del remitente inválido")
            sys.exit(1)
        
        # Probar conexión si se solicita
        if args.test or args.test_recipient:
            if not mail_config.test_smtp_connection(config, args.test_recipient):
                mail_config.log("ERROR", "Prueba de conexión falló")
                sys.exit(1)
        
        # Solo validar si se especifica
        if args.validate_only:
            mail_config.log("SUCCESS", "Configuración válida")
            return
        
        # Guardar configuración
        if mail_config.save_config(config, args.backup):
            mail_config.log("SUCCESS", "Configuración completada exitosamente")
        else:
            mail_config.log("ERROR", "Error al guardar configuración")
            sys.exit(1)
            
    except KeyboardInterrupt:
        mail_config.log("INFO", "Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        mail_config.log("ERROR", f"Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
