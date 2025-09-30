#!/usr/bin/env python3
"""
GPG Backup Manager v1.0.0
Gestor especializado de backups portables de GPG
Prioridad: BACKUP y RESTORE para uso cross-platform

Uso: gpg-manager.py [--init|--gen-key|--backup|--restore|--verify|--list|--help]
"""

import os
import sys
import subprocess
import argparse
import tempfile
import shutil
import hashlib
import getpass
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

# Configuración
BACKUP_DIR = os.path.expanduser("~/secure/gpg/backup")
GPG_HOME = os.path.expanduser("~/.gnupg")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class Colors:
    """Colores para output en terminal"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class GPGManager:
    """Gestor principal de GPG"""
    
    def __init__(self):
        self.backup_dir = Path(BACKUP_DIR)
        self.gpg_home = Path(GPG_HOME)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log_info(self, message: str):
        """Log de información"""
        print(f"{Colors.CYAN}[INFO]{Colors.NC} {message}")
        
    def log_success(self, message: str):
        """Log de éxito"""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
        
    def log_warning(self, message: str):
        """Log de advertencia"""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
        
    def log_error(self, message: str):
        """Log de error"""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
        
    def run_command(self, cmd: List[str], input_data: Optional[str] = None, 
                   capture_output: bool = True, extra_fd: Optional[int] = None,
                   extra_fd_data: Optional[str] = None) -> subprocess.CompletedProcess:
        """Ejecutar comando con manejo de errores"""
        try:
            stdin = subprocess.PIPE if input_data else None
            extra_files = {}
            
            if extra_fd and extra_fd_data:
                # Crear un pipe para el descriptor de archivo extra
                r, w = os.pipe()
                extra_files[extra_fd] = w
                
                # Escribir datos extra en el pipe
                os.write(w, extra_fd_data.encode())
                os.close(w)
                
                result = subprocess.run(
                    cmd,
                    input=input_data,
                    capture_output=capture_output,
                    text=True,
                    check=False,
                    pass_fds=list(extra_files.keys())
                )
                
                # Cerrar el pipe de lectura
                os.close(r)
            else:
                result = subprocess.run(
                    cmd,
                    input=input_data,
                    capture_output=capture_output,
                    text=True,
                    check=False
                )
            
            return result
        except Exception as e:
            self.log_error(f"Error ejecutando comando: {e}")
            raise
            
    def check_gpg_available(self) -> bool:
        """Verificar que GPG esté disponible"""
        result = self.run_command(["gpg", "--version"])
        return result.returncode == 0

    def check_git_available(self) -> bool:
        """Verificar que Git esté disponible"""
        result = self.run_command(["git", "--version"])
        return result.returncode == 0

    def check_tool_available(self, tool: str) -> bool:
        """Verificar que una herramienta esté disponible"""
        result = self.run_command(["which", tool])
        return result.returncode == 0

    def check_prerequisites_for_operation(self, operation: str) -> bool:
        """Verificar prerequisitos para una operación específica"""
        self.log_info(f"🔍 Verificando prerequisitos para: {operation}")
        
        missing_tools = []
        
        # Prerequisitos básicos (siempre necesarios)
        if not self.check_gpg_available():
            missing_tools.append("gpg")
        
        # Prerequisitos específicos por operación
        if operation in ["git-config", "configure_git"]:
            if not self.check_git_available():
                missing_tools.append("git")
                
        elif operation in ["backup", "create_backup"]:
            required_tools = ["tar", "sha256sum"]
            for tool in required_tools:
                if not self.check_tool_available(tool):
                    missing_tools.append(tool)
                    
        elif operation in ["restore", "verify"]:
            required_tools = ["tar"]
            for tool in required_tools:
                if not self.check_tool_available(tool):
                    missing_tools.append(tool)
        
        # Mostrar resultados
        if missing_tools:
            self.log_error(f"❌ Prerequisitos faltantes para {operation}:")
            for tool in missing_tools:
                self.log_error(f"   - {tool}")
            self.log_info("💡 Instale las herramientas faltantes y vuelva a intentar")
            return False
        else:
            self.log_success(f"✅ Todos los prerequisitos para {operation} están disponibles")
            return True
        
    def get_user_key_info(self) -> Dict[str, str]:
        """Obtener información del usuario para la llave"""
        print("\n" + "="*50)
        print("🔑 INFORMACIÓN DE LA LLAVE MAESTRA")
        print("="*50 + "\n")
        
        try:
            # Obtener nombre
            name = input("Nombre completo: ").strip()
            if not name:
                self.log_error("El nombre es requerido")
                sys.exit(1)
                
            # Obtener email
            email = input("Email: ").strip()
            if not email:
                self.log_error("El email es requerido")
                sys.exit(1)
                
            # Obtener comentario (opcional)
            comment = input("Comentario (opcional): ").strip()
            
            # Obtener contraseña
            print("\n🔐 Contraseña para la llave maestra:")
            passphrase = getpass.getpass("Contraseña: ")
            if not passphrase:
                self.log_error("La contraseña es requerida")
                sys.exit(1)
                
            passphrase_confirm = getpass.getpass("Confirmar contraseña: ")
            if passphrase != passphrase_confirm:
                self.log_error("Las contraseñas no coinciden")
                sys.exit(1)
                
        except (EOFError, KeyboardInterrupt):
            self.log_error("Entrada cancelada o no disponible")
            sys.exit(1)
            
        return {
            "name": name,
            "email": email,
            "comment": comment,
            "passphrase": passphrase
        }
        
    def generate_master_key(self, user_info: Dict[str, str]) -> str:
        """Generar llave maestra"""
        self.log_info("🔑 Generando llave maestra (RSA 4096, Certificación + Firma)...")
        
        # Crear archivo de configuración temporal
        config_content = f"""Key-Type: RSA
Key-Length: 4096
Key-Usage: cert,sign
Name-Real: {user_info['name']}
Name-Email: {user_info['email']}"""
        
        if user_info['comment']:
            config_content += f"\nName-Comment: {user_info['comment']}"
            
        config_content += """
Expire-Date: 0
Passphrase: """ + user_info['passphrase'] + """
%commit"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write(config_content)
            config_file = f.name
            
        try:
            # Generar llave maestra
            result = self.run_command(["gpg", "--batch", "--full-generate-key", config_file])
            if result.returncode != 0:
                self.log_error("❌ Error generando llave maestra")
                sys.exit(1)
                
            self.log_success("✅ Llave maestra generada")
            
            # Obtener huella digital completa de la llave maestra
            result = self.run_command(["gpg", "--list-secret-keys", "--with-colons", "--fingerprint"])
            if result.returncode != 0:
                self.log_error("No se pudo obtener ID de la llave maestra")
                sys.exit(1)
                
            # Buscar la huella digital completa
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('sec:'):
                    # Buscar la línea fpr: siguiente
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].startswith('fpr:'):
                            # Formato: fpr:::::::::FINGERPRINT:
                            fingerprint = lines[j].split(':')[9]
                            if fingerprint:
                                self.log_success(f"ID de llave maestra: {fingerprint[-16:]}")
                                return fingerprint
                        
            self.log_error("No se pudo obtener huella digital de la llave maestra")
            sys.exit(1)
            
        finally:
            # Limpiar archivo temporal
            os.unlink(config_file)
            
    def configure_gpg_for_automation(self):
        """Configurar GPG para automatización con pinentry-mode loopback solo si no hay entorno gráfico"""
        gpg_conf = self.gpg_home / "gpg.conf"
        gpg_agent_conf = self.gpg_home / "gpg-agent.conf"
        
        # Verificar si ya hay configuración de pinentry gráfico
        has_graphical_pinentry = False
        if gpg_agent_conf.exists():
            with open(gpg_agent_conf, 'r') as f:
                content = f.read()
                if 'pinentry-program' in content:
                    has_graphical_pinentry = True
        
        # Solo configurar loopback si no hay pinentry gráfico
        if not has_graphical_pinentry:
            self.log_info("📟 Configurando pinentry loopback para automatización")
            
            # Configurar gpg.conf
            with open(gpg_conf, 'a') as f:
                f.write("\n# Configuración para automatización\n")
                f.write("use-agent\n")
                f.write("pinentry-mode loopback\n")
            
            # Configurar gpg-agent.conf
            with open(gpg_agent_conf, 'a') as f:
                f.write("\n# Configuración para automatización\n")
                f.write("allow-loopback-pinentry\n")
            
            # Recargar gpg-agent
            self.run_command(["gpg-connect-agent", "reloadagent", "/bye"])
        else:
            self.log_info("🖥️  Pinentry gráfico detectado - manteniendo configuración existente")
    
    def generate_subkeys(self, master_key_id: str, passphrase: str):
        """Generar subclaves usando --quick-add-key"""
        self.log_info("🔑 Generando subclaves...")
        
        # Configurar GPG para automatización
        self.configure_gpg_for_automation()
        
        # Subclaves a crear: [algoritmo, uso, expiración]
        subkeys = [
            ("rsa4096", "sign", "1y"),
            ("rsa4096", "encrypt", "1y"),
            ("rsa4096", "auth", "1y")
        ]
        
        for algo, usage, expire in subkeys:
            try:
                self.log_info(f"Generando subclave {usage.upper()} ({algo})...")
                
                # Crear subclave usando --quick-add-key
                result = self.run_command([
                    "gpg", "--batch", "--yes",
                    "--pinentry-mode", "loopback",
                    "--passphrase-fd", "0",
                    "--quick-add-key", master_key_id,
                    algo, usage, expire
                ], input_data=passphrase)
                
                if result.returncode == 0:
                    self.log_success(f"✅ Subclave {usage.upper()} creada")
                else:
                    self.log_warning(f"⚠️  Error creando subclave {usage.upper()}")
                    self.log_error(result.stderr)
                    
            except Exception as e:
                self.log_error(f"Error creando subclave {usage}: {e}")
            
    def create_revocation_certificate(self, master_key_id: str, passphrase: str):
        """Crear certificado de revocación"""
        self.log_info("🔒 Creando certificado de revocación...")
        
        # Guardar en ~/secure/gpg/ en lugar de backup/
        secure_gpg_dir = Path.home() / "secure" / "gpg"
        secure_gpg_dir.mkdir(parents=True, exist_ok=True)
        
        revocation_file = secure_gpg_dir / f"revocation-cert-{master_key_id}.asc"
        
        try:
            # GPG genera automáticamente un certificado de revocación al crear la clave
            # Se guarda en ~/.gnupg/openpgp-revocs.d/
            revocs_dir = self.gpg_home / "openpgp-revocs.d"
            
            if revocs_dir.exists():
                # Buscar el archivo de revocación generado automáticamente
                for rev_file in revocs_dir.glob("*.rev"):
                    if master_key_id in rev_file.name:
                        # Copiar el certificado a ~/secure/gpg/
                        import shutil
                        shutil.copy2(rev_file, revocation_file)
                        self.log_success(f"✅ Certificado de revocación copiado: {revocation_file.name}")
                        self.log_info(f"📁 Ubicación: {revocation_file}")
                        return
                        
            # Si no se encuentra el certificado automático, informar al usuario
            self.log_warning("⚠️  No se encontró certificado de revocación automático")
            self.log_info("GPG debería haber generado uno automáticamente en ~/.gnupg/openpgp-revocs.d/")
            self.log_info(f"Ejecute manualmente: gpg --output {revocation_file} --gen-revoke {master_key_id}")
                
        except Exception as e:
            self.log_error(f"Error copiando certificado de revocación: {e}")
            self.log_info(f"Ejecute manualmente: gpg --output {revocation_file} --gen-revoke {master_key_id}")
            
    def show_generated_keys_info(self, master_key_id: str):
        """Mostrar información de las claves generadas"""
        print("\n" + "="*50)
        print("🎉 LLAVES GENERADAS EXITOSAMENTE")
        print("="*50 + "\n")
        
        print("🔑 Llave Maestra:")
        print(f"   ID: {master_key_id}")
        print("   Uso: Certificación (C) + Firma (S)")
        print("   Expiración: Nunca")
        print()
        
        print("🔑 Subclaves:")
        result = self.run_command(["gpg", "--list-keys", "--with-colons", master_key_id])
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('sub:'):
                    parts = line.split(':')
                    key_id = parts[4]
                    key_usage = parts[11]
                    key_expiry = parts[6]
                    
                    if key_expiry == "0":
                        expiry_text = "Nunca"
                    else:
                        try:
                            expiry_date = datetime.fromtimestamp(int(key_expiry))
                            expiry_text = expiry_date.strftime("%Y-%m-%d")
                        except:
                            expiry_text = "Desconocido"
                    
                    if 'e' in key_usage:
                        print(f"   📧 Cifrado (E): {key_id} - Expira: {expiry_text}")
                    elif 'a' in key_usage:
                        print(f"   🔐 Autenticación (A): {key_id} - Expira: {expiry_text}")
                    elif 's' in key_usage:
                        print(f"   ✍️  Firma (S): {key_id} - Expira: {expiry_text}")
        
        print()
        print("💡 Próximos pasos:")
        print(f"   1. Configurar Git: git config --global user.signingkey {master_key_id}")
        print(f"   2. Subir claves: gpg --send-keys {master_key_id}")
        print("   3. Verificar claves: gpg --list-keys")
        print()
        
    def generate_master_key_and_subkeys(self):
        """Generar llave maestra y subclaves"""
        # Verificar prerequisitos
        if not self.check_prerequisites_for_operation("gen-key"):
            return False
            
        self.log_info("🔑 Generando llave maestra y subclaves para desarrollo...")
        
        # Verificar que GPG esté inicializado
        if not self.gpg_home.exists():
            self.log_error("GPG no está inicializado. Ejecute: gpg-manager.py --init")
            sys.exit(1)
            
        # Obtener información del usuario
        user_info = self.get_user_key_info()
        
        # Generar llave maestra
        master_key_id = self.generate_master_key(user_info)
        
        # Generar subclaves
        self.generate_subkeys(master_key_id, user_info['passphrase'])
        
        # Crear certificado de revocación
        self.create_revocation_certificate(master_key_id, user_info['passphrase'])
        
        # Mostrar información de las claves generadas
        self.show_generated_keys_info(master_key_id)
        
        # Exportar llave maestra para almacenamiento offline
        self.log_info("🔐 Exportando llave maestra para almacenamiento offline...")
        self.export_master_key_offline(master_key_id, user_info['passphrase'])
        
        # Crear backup automático
        self.log_info("💾 Creando backup automático de subclaves...")
        self.create_portable_gpg_backup()
        
        self.log_success("✅ Llave maestra y subclaves generadas exitosamente")
        
    def export_master_key_offline(self, master_key_id: str, passphrase: str):
        """Exportar llave maestra para almacenamiento offline cifrado"""
        secure_gpg_dir = Path.home() / "secure" / "gpg"
        secure_gpg_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivos de exportación
        master_key_file = secure_gpg_dir / f"master-key-{master_key_id}.asc"
        
        try:
            # Exportar llave maestra (solo certificación)
            result = self.run_command([
                "gpg", "--armor", "--export-secret-keys", 
                "--pinentry-mode", "loopback",
                "--passphrase-fd", "0",
                master_key_id
            ], input_data=passphrase)
            
            if result.returncode != 0:
                self.log_error(f"Error exportando llave maestra: {result.stderr}")
                return False
                
            # Guardar llave maestra
            with open(master_key_file, 'w') as f:
                f.write(result.stdout)
            
            self.log_success(f"✅ Llave maestra exportada: {master_key_file.name}")
            
            
            # Exportar solo las subclaves secretas y eliminar la llave maestra
            self.log_info("🗑️  Exportando subclaves y eliminando llave maestra del keyring local...")
            
            # Exportar solo las subclaves secretas
            subkeys_file = secure_gpg_dir / f"subkeys-{master_key_id}.asc"
            subkeys_result = self.run_command([
                "gpg", "--armor", "--export-secret-subkeys", 
                "--pinentry-mode", "loopback",
                "--passphrase-fd", "0",
                master_key_id
            ], input_data=passphrase)
            
            if subkeys_result.returncode == 0:
                # Guardar las subclaves
                with open(subkeys_file, 'w') as f:
                    f.write(subkeys_result.stdout)
                self.log_success(f"✅ Subclaves exportadas: {subkeys_file.name}")
                
                # Eliminar la clave maestra secreta (esto mantiene las subclaves)
                delete_result = self.run_command([
                    "gpg", "--delete-secret-key", "--batch", "--yes",
                    master_key_id
                ])
                
                if delete_result.returncode == 0:
                    self.log_success("✅ Llave maestra eliminada del keyring local")
                    
                    # Importar las subclaves de vuelta
                    import_result = self.run_command([
                        "gpg", "--import", str(subkeys_file)
                    ])
                    
                    if import_result.returncode == 0:
                        self.log_success("✅ Subclaves importadas de vuelta al keyring")
                    else:
                        self.log_error("Error importando subclaves")
                        return False
                else:
                    self.log_error("Error eliminando llave maestra")
                    return False
            else:
                self.log_error("Error exportando subclaves")
                return False
                
            print("\n" + "="*60)
            print("🔐 LLAVE MAESTRA EXPORTADA PARA ALMACENAMIENTO OFFLINE")
            print("="*60)
            print(f"🔑 ID de llave maestra: {master_key_id}")
            print(f"📁 Ubicación: {secure_gpg_dir}")
            print(f"📄 Archivo: {master_key_file.name}")
            print(f"📄 Subclaves: {subkeys_file.name}")
            print()
            print("⚠️  IMPORTANTE:")
            print("1. Guarde la llave maestra en un lugar seguro (USB, papel)")
            print("2. NO la mantenga en el sistema de archivos local")
            print("3. Use solo para revocar subclaves o crear nuevas")
            print("4. Las subclaves siguen funcionando normalmente")
            print("="*60)
            
            return True
                
        except Exception as e:
            self.log_error(f"Error en exportación offline: {e}")
            return False
        
    def initialize_gpg(self):
        """Inicializar configuración GPG"""
        # Verificar prerequisitos
        if not self.check_prerequisites_for_operation("init"):
            return False
            
        self.log_info("🚀 Inicializando configuración GPG...")
        
        # Verificar si ya existe
        if self.gpg_home.exists():
            self.log_warning(f"El directorio GPG ya existe: {self.gpg_home}")
            try:
                response = input("¿Desea continuar y sobrescribir la configuración? [y/N]: ")
                if response.lower() != 'y':
                    self.log_info("Inicialización cancelada")
                    return
            except (EOFError, KeyboardInterrupt):
                self.log_info("Inicialización cancelada")
                return
                
            # Crear backup de la configuración existente
            self.log_info("💾 Creando backup de configuración existente...")
            self.create_portable_gpg_backup()
            self.log_success("Backup de configuración existente completado")
            
            # Remover configuración existente
            shutil.rmtree(self.gpg_home)
            
        # Crear directorio GPG
        self.log_info(f"📁 Creando directorio GPG: {self.gpg_home}")
        self.gpg_home.mkdir(parents=True, exist_ok=True)
        
        # Establecer permisos correctos
        self.log_info("🔐 Estableciendo permisos de seguridad...")
        os.chmod(self.gpg_home, 0o700)
        
        # Crear archivo de configuración básico
        self.log_info("⚙️  Creando configuración básica...")
        gpg_conf = self.gpg_home / "gpg.conf"
        
        # Detectar si hay entorno gráfico disponible
        has_display = os.environ.get('DISPLAY') is not None
        has_wayland = os.environ.get('WAYLAND_DISPLAY') is not None
        has_graphical = has_display or has_wayland
        
        if has_graphical:
            self.log_info("🖥️  Entorno gráfico detectado - configurando pinentry gráfico")
            pinentry_config = ""
        else:
            self.log_info("📟 Solo terminal detectado - configurando pinentry loopback")
            pinentry_config = "pinentry-mode loopback\n"
        
        gpg_conf.write_text(f"""# Configuración básica de GPG
# Generada automáticamente por gpg-manager.py --init

# Configuración de claves
keyid-format 0xlong
with-fingerprint
with-keygrip

# Configuración de cifrado
cipher-algo AES256
digest-algo SHA512
cert-digest-algo SHA512
compress-algo 1

# Configuración de agent
use-agent
{pinentry_config}
# Configuración de salida
armor
emit-version
no-comments
no-greeting

# Configuración de confianza
trust-model tofu+pgp
auto-key-locate keyserver
keyserver hkps://keys.openpgp.org

# Configuración de listado
list-options show-uid-validity
verify-options show-uid-validity
""")
        
        # Crear configuración del agente
        self.log_info("🤖 Configurando agente GPG...")
        gpg_agent_conf = self.gpg_home / "gpg-agent.conf"
        
        # Configurar pinentry según el entorno
        if has_graphical:
            # Detectar el mejor pinentry gráfico disponible
            pinentry_programs = [
                "/usr/bin/pinentry-gnome3",
                "/usr/bin/pinentry-gtk-2", 
                "/usr/bin/pinentry-gtk",
                "/usr/bin/pinentry-qt",
                "/usr/bin/pinentry"
            ]
            
            pinentry_program = "/usr/bin/pinentry"
            for program in pinentry_programs:
                if shutil.which(program):
                    pinentry_program = program
                    break
            
            self.log_info(f"🖥️  Usando pinentry gráfico: {pinentry_program}")
            agent_config = f"""# Configuración del agente GPG
# Generada automáticamente por gpg-manager.py --init

# Configuración de pinentry
pinentry-program {pinentry_program}

# Configuración de caché
default-cache-ttl 600
max-cache-ttl 7200

# Configuración de SSH
enable-ssh-support

# Configuración de scdaemon
scdaemon-program /usr/lib/gnupg/scdaemon
"""
        else:
            self.log_info("📟 Configurando pinentry loopback para terminal")
            agent_config = """# Configuración del agente GPG
# Generada automáticamente por gpg-manager.py --init

# Configuración de pinentry para terminal
allow-loopback-pinentry

# Configuración de caché
default-cache-ttl 600
max-cache-ttl 7200

# Configuración de SSH
enable-ssh-support

# Configuración de scdaemon
scdaemon-program /usr/lib/gnupg/scdaemon
"""
        
        gpg_agent_conf.write_text(agent_config)
        
        # Establecer permisos en archivos de configuración
        os.chmod(gpg_conf, 0o600)
        os.chmod(gpg_agent_conf, 0o600)
        
        # Crear archivo de trust básico
        self.log_info("🔒 Inicializando base de confianza...")
        self.run_command(["gpg", "--check-trustdb"])
        
        # Verificar instalación
        self.log_info("✅ Verificando instalación...")
        if self.check_gpg_available():
            self.log_success("GPG funcionando correctamente")
        else:
            self.log_error("Error: GPG no está funcionando correctamente")
            sys.exit(1)
            
        # Mostrar información de la instalación
        self.show_initialization_info()
        
    def show_initialization_info(self):
        """Mostrar información de la inicialización"""
        print("\n" + "="*50)
        print("🎉 ¡INICIALIZACIÓN COMPLETADA!")
        print("="*50 + "\n")
        
        print(f"📁 Directorio GPG: {self.gpg_home}")
        print(f"⚙️  Configuración: {self.gpg_home}/gpg.conf")
        print(f"🤖 Agente: {self.gpg_home}/gpg-agent.conf")
        print()
        
        print("🔑 Próximos pasos:")
        print("   1. Generar una clave: gpg --gen-key")
        print("   2. Listar claves: gpg --list-keys")
        print("   3. Crear backup: gpg-manager.py --backup")
        print()
        
        print("💾 Backup de configuración anterior:")
        print("   Si existía configuración previa, se creó un backup automático")
        print("   Ver backups disponibles: gpg-manager.py --list")
        print()
        
        print("💡 Comandos útiles:")
        print("   gpg --gen-key                    Generar nueva clave")
        print("   gpg --list-keys                  Ver claves públicas")
        print("   gpg --list-secret-keys           Ver claves privadas")
        print("   gpg --edit-key <keyid>           Editar clave")
        print("   gpg --send-keys <keyid>          Subir clave a servidor")
        print()
        
        print("🌐 Para usar en otra máquina:")
        print("   gpg-manager.py --backup          Crear backup portable")
        print("   gpg-manager.py --restore <file>  Restaurar backup")
        print()
        
    def create_portable_gpg_backup(self):
        """Crear backup portable de GPG"""
        # Verificar prerequisitos
        if not self.check_prerequisites_for_operation("backup"):
            return False
            
        self.log_info("🌐 Creando backup portable de configuración GPG...")
        
        # Verificar pre-requisitos específicos de backup
        self.check_backup_prerequisites()
        
        # Crear directorio de backup
        self.create_backup_directory()
        
        # Detener procesos GPG
        self.stop_gpg_processes()
        
        # Crear backup principal
        self.create_main_backup()
        
        # Crear checksum
        self.create_backup_integrity_check()
        
        # Verificar backup creado
        self.verify_backup_structure()
        
        backup_file = self.backup_dir / f"gpg-{self.timestamp}.tar.gz"
        self.log_success(f"✅ Backup completado: {backup_file.name}")
        
    def check_backup_prerequisites(self):
        """Verificar pre-requisitos para backup"""
        if not self.gpg_home.exists():
            self.log_error(f"No existe directorio GPG: {self.gpg_home}")
            sys.exit(1)
            
        # Verificar herramientas necesarias
        for tool in ["tar", "sha256sum"]:
            result = self.run_command(["which", tool])
            if result.returncode != 0:
                self.log_error(f"{tool} no disponible")
                sys.exit(1)
                
    def create_backup_directory(self):
        """Crear directorio de backup"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.cleanup_old_backups()
        
    def cleanup_old_backups(self):
        """Limpiar backups antiguos (mantener últimos 5)"""
        backup_files = list(self.backup_dir.glob("gpg-*.tar.gz"))
        if len(backup_files) > 5:
            # Ordenar por fecha de modificación y eliminar los más antiguos
            backup_files.sort(key=lambda x: x.stat().st_mtime)
            for old_file in backup_files[:-5]:
                old_file.unlink()
                
    def stop_gpg_processes(self):
        """Detener procesos GPG"""
        try:
            # Detener gpg-agent
            result = self.run_command(["pkill", "-TERM", "gpg-agent"])
            if result.returncode == 0:
                time.sleep(2)
                # Si sigue corriendo, forzar terminación
                self.run_command(["pkill", "-KILL", "gpg-agent"])
        except Exception:
            pass  # Ignorar errores
            
    def create_main_backup(self):
        """Crear backup principal"""
        backup_file = self.backup_dir / f"gpg-{self.timestamp}.tar.gz"
        
        # Crear backup excluyendo archivos temporales
        result = self.run_command([
            "tar", "-czf", str(backup_file),
            "--exclude=*.lock",
            "--exclude=*trustdb.gpg",
            "--exclude=random_seed",
            "--exclude=.#lk*",
            "--exclude=S.*",
            "--exclude=*.tmp",
            "--directory", str(self.gpg_home.parent),
            ".gnupg/"
        ])
        
        if result.returncode != 0 or not backup_file.exists():
            self.log_error("Error creando backup principal")
            sys.exit(1)
            
    def create_backup_integrity_check(self):
        """Crear verificación de integridad"""
        backup_file = self.backup_dir / f"gpg-{self.timestamp}.tar.gz"
        checksum_file = backup_file.with_suffix(".tar.gz.sha256")
        
        if backup_file.exists():
            # Crear checksum
            result = self.run_command(["sha256sum", str(backup_file)])
            if result.returncode == 0:
                checksum_file.write_text(result.stdout)
                
                # Verificar inmediatamente
                verify_result = self.run_command(["sha256sum", "-c", str(checksum_file)])
                if verify_result.returncode != 0:
                    self.log_error("❌ Error de integridad detectado")
                    sys.exit(1)
                    
    def verify_backup_structure(self):
        """Verificar estructura del backup"""
        backup_file = self.backup_dir / f"gpg-{self.timestamp}.tar.gz"
        
        if not backup_file.exists():
            self.log_error("Backup principal no encontrado")
            sys.exit(1)
            
        # Verificar estructura temporalmente
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_command(["tar", "-xzf", str(backup_file), "-C", temp_dir])
            if result.returncode != 0:
                self.log_error("❌ Error extrayendo backup")
                sys.exit(1)
                
            # Verificar estructura esperada
            if not Path(temp_dir, ".gnupg").exists():
                self.log_error("❌ Estructura de backup inválida")
                sys.exit(1)
                
    def restore_portable_gpg(self, backup_file: str):
        """Restaurar backup portable"""
        # Verificar prerequisitos
        if not self.check_prerequisites_for_operation("restore"):
            return False
            
        if not backup_file:
            self.log_error("Falta especificar archivo de backup")
            sys.exit(1)
            
        backup_path = Path(backup_file)
        if not backup_path.exists():
            self.log_error(f"No existe el archivo: {backup_file}")
            sys.exit(1)
            
        self.log_info("🔄 Restaurando backup portable...")
        
        # Crear backup de la configuración actual
        if self.gpg_home.exists():
            self.log_info("💾 Creando backup de configuración actual...")
            self.create_portable_gpg_backup()
            
        # Extraer backup
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_command(["tar", "-xzf", str(backup_path), "-C", temp_dir])
            if result.returncode != 0:
                self.log_error("Error extrayendo backup")
                sys.exit(1)
                
            # Remover configuración actual
            if self.gpg_home.exists():
                shutil.rmtree(self.gpg_home)
                
            # Copiar nueva configuración
            source_gnupg = Path(temp_dir, ".gnupg")
            if source_gnupg.exists():
                shutil.copytree(source_gnupg, self.gpg_home)
                os.chmod(self.gpg_home, 0o700)
                self.log_success("✅ Backup restaurado exitosamente")
            else:
                self.log_error("❌ Estructura de backup inválida")
                sys.exit(1)
                
    def verify_backup_integrity(self, backup_file: str):
        """Verificar integridad del backup"""
        # Verificar prerequisitos
        if not self.check_prerequisites_for_operation("verify"):
            return False
            
        if not backup_file:
            self.log_error("Falta especificar archivo de backup")
            sys.exit(1)
            
        backup_path = Path(backup_file)
        if not backup_path.exists():
            self.log_error(f"No existe el archivo: {backup_file}")
            sys.exit(1)
            
        print("\n" + "="*50)
        print("🔍 VERIFICACIÓN DE INTEGRIDAD DE BACKUP")
        print("="*50 + "\n")
        
        if backup_path.suffix == ".gz" and backup_path.name.endswith(".tar.gz"):
            self.verify_direct_backup(backup_path)
        elif backup_path.suffix == ".asc":
            self.verify_encrypted_backup(backup_path)
        else:
            self.log_error(f"Formato no reconocido: {backup_file}")
            sys.exit(1)
            
    def verify_direct_backup(self, backup_file: Path):
        """Verificar backup directo"""
        self.log_info(f"Verificando backup directo: {backup_file.name}")
        
        # Verificar checksum
        checksum_file = backup_file.with_suffix(".tar.gz.sha256")
        if checksum_file.exists():
            self.log_info("Verificando checksum...")
            result = self.run_command(["sha256sum", "-c", str(checksum_file)])
            if result.returncode == 0:
                self.log_success("✅ Checksum verificado correctamente")
            else:
                self.log_error("❌ Error en checksum - backup corrupto")
                sys.exit(1)
        else:
            self.log_warning("No se encontró archivo checksum (.sha256)")
            
        # Verificar estructura
        self.log_info("Verificando estructura del tar...")
        result = self.run_command(["tar", "-tzf", str(backup_file)])
        if result.returncode == 0:
            self.log_success("✅ Estructura de tar válida")
            
            # Mostrar contenido principal
            self.log_info("Contenido principal del backup:")
            lines = result.stdout.split('\n')
            gnupg_files = [line for line in lines if '.gnupg/' in line][:10]
            for file in gnupg_files:
                print(f"   {file}")
            print(f"   ... ({len(lines)} archivos total)")
        else:
            self.log_error("❌ Error en estructura de tar")
            sys.exit(1)
            
        # Verificar tamaño
        file_size = backup_file.stat().st_size
        size_mb = file_size / (1024 * 1024)
        self.log_info(f"Tamaño del backup: {size_mb:.1f} MB")
        
        # Verificar fecha de creación
        creation_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        self.log_info(f"Fecha creado: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print()
        self.log_success("✅ Backup verificado correctamente - listo para restauración")
        
    def verify_encrypted_backup(self, backup_file: Path):
        """Verificar backup cifrado"""
        self.log_info(f"Verificando backup cifrado: {backup_file.name}")
        
        # Verificar que es un archivo cifrado válido
        self.log_info("Verificando archivo cifrado...")
        result = self.run_command(["gpg", "--decrypt", "--dry-run", str(backup_file)])
        if result.returncode == 0:
            self.log_success("✅ Archivo cifrado válido")
            self.log_info("⚠️  Para verificación completa se requiere contraseña")
        else:
            self.log_error("❌ Archivo cifrado inválido o corrupto")
            sys.exit(1)
            
        print()
        self.log_success("✅ Backup cifrado verificado básicamente - requiere contraseña para uso completo")
        
    def list_available_backups(self):
        """Listar backups disponibles"""
        print("\n" + "="*50)
        print("📋 BACKUPS DISPONIBLES")
        print("="*50 + "\n")
        
        if not self.backup_dir.exists():
            self.log_warning(f"No existe directorio de backups: {self.backup_dir}")
            return
            
        print(f"📁 Directorio: {self.backup_dir}")
        print()
        
        # Mostrar backups directos
        print("📦 Backups Directos:")
        backup_files = list(self.backup_dir.glob("gpg-*.tar.gz"))
        if backup_files:
            for backup_file in sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True):
                size_mb = backup_file.stat().st_size / (1024 * 1024)
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                print(f"   📄 {backup_file.name} - {size_mb:.1f} MB - {mtime.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("   No hay backups directos")
            
        print()
        
        # Mostrar checksums si existen
        checksum_files = list(self.backup_dir.glob("gpg-*.sha256"))
        if checksum_files:
            print("🔍 Verificaciones de Integridad:")
            for checksum_file in checksum_files:
                print(f"   ✅ {checksum_file.name}")
                
        print()
        
    def get_latest_valid_signing_key(self) -> str:
        """Obtiene la llave de firma más reciente y válida"""
        try:
            # Listar todas las llaves públicas
            result = self.run_command(['gpg', '--list-keys', '--with-colons'])
            
            valid_keys = []
            for line in result.stdout.split('\n'):
                if line.startswith('pub:'):
                    # Parsear información de la llave
                    parts = line.split(':')
                    key_id = parts[4]
                    created = parts[5]
                    expires = parts[6]
                    usage = parts[11]
                    validity = parts[1]
                    
                    # Verificar que es válida (estrategia 2)
                    if (validity in ['u', 'f', 'm'] and  # No revocada
                        'S' in usage and  # Tiene capacidad de firma
                        (expires == '' or int(expires) > int(time.time()))):  # No expirada
                        valid_keys.append((key_id, created))
            
            # Ordenar por fecha de creación (más reciente primero - estrategia 1)
            valid_keys.sort(key=lambda x: x[1], reverse=True)
            
            if valid_keys:
                return valid_keys[0][0]
            else:
                return None
                
        except Exception as e:
            self.log_error(f"Error obteniendo llave de firma: {e}")
            return None

    def get_single_key_if_only_one(self) -> Optional[str]:
        """Devuelve el único key id si solo hay una llave pública en el keyring."""
        try:
            result = self.run_command(['gpg', '--list-keys', '--with-colons'])
            key_ids = []
            for line in result.stdout.split('\n'):
                if line.startswith('pub:'):
                    parts = line.split(':')
                    key_id = parts[4]
                    if key_id:
                        key_ids.append(key_id)
            if len(key_ids) == 1:
                return key_ids[0]
            return None
        except Exception as e:
            self.log_error(f"Error detectando única llave pública: {e}")
            return None

    def verify_signing_key(self, key_id: str) -> bool:
        """Verifica que una llave es válida para firma"""
        try:
            result = self.run_command(['gpg', '--list-keys', '--with-colons', key_id])
            
            for line in result.stdout.split('\n'):
                if line.startswith('pub:'):
                    parts = line.split(':')
                    validity = parts[1]
                    usage = parts[11]
                    expires = parts[6]
                    
                    # Verificar que es válida
                    if (validity in ['u', 'f', 'm'] and  # No revocada
                        'S' in usage and  # Tiene capacidad de firma
                        (expires == '' or int(expires) > int(time.time()))):  # No expirada
                        return True
            
            return False
            
        except Exception as e:
            self.log_error(f"Error verificando llave: {e}")
            return False

    def disable_git_gpg(self):
        """Deshabilita el uso de GPG en Git"""
        try:
            self.log_info("🔧 Deshabilitando GPG en Git...")
            
            # Deshabilitar firma de commits
            self.run_command(['git', 'config', '--global', '--unset', 'commit.gpgsign'])
            
            # Deshabilitar firma de tags
            self.run_command(['git', 'config', '--global', '--unset', 'tag.gpgSign'])
            
            # Remover configuración de llave de firma
            self.run_command(['git', 'config', '--global', '--unset', 'user.signingkey'])
            
            # Remover configuración de programa GPG
            self.run_command(['git', 'config', '--global', '--unset', 'gpg.program'])
            
            self.log_success("✅ GPG deshabilitado en Git")
            self.log_info("💡 Para habilitar nuevamente: gpg-manager.py --git-config")
            
        except Exception as e:
            self.log_error(f"Error deshabilitando GPG: {e}")

    def get_user_info_from_key(self, key_id: str) -> dict:
        """Obtiene información del usuario desde una llave GPG"""
        try:
            result = self.run_command(['gpg', '--list-keys', '--with-colons', key_id])
            
            user_info = {'name': None, 'email': None}
            
            for line in result.stdout.split('\n'):
                if line.startswith('uid:'):
                    parts = line.split(':')
                    uid = parts[9]
                    
                    # Parsear UID (formato: "Nombre <email>")
                    if '<' in uid and '>' in uid:
                        name_part = uid.split('<')[0].strip()
                        email_part = uid.split('<')[1].split('>')[0].strip()
                        
                        if name_part:
                            user_info['name'] = name_part
                        if email_part:
                            user_info['email'] = email_part
                    else:
                        # Solo nombre sin email
                        user_info['name'] = uid.strip()
            
            return user_info
            
        except Exception as e:
            self.log_error(f"Error obteniendo información del usuario: {e}")
            return {'name': None, 'email': None}

    def _configure_git_with_key(self, signing_key: str):
        """Configura Git con una llave específica"""
        try:
            # Obtener información del usuario desde la llave
            user_info = self.get_user_info_from_key(signing_key)
            
            # Configurar nombre y email
            if user_info['name']:
                self.run_command(['git', 'config', '--global', 'user.name', user_info['name']])
                self.log_success(f"✅ Git configurado: user.name = {user_info['name']}")
            
            if user_info['email']:
                self.run_command(['git', 'config', '--global', 'user.email', user_info['email']])
                self.log_success(f"✅ Git configurado: user.email = {user_info['email']}")
            
            # Configurar llave de firma
            self.run_command(['git', 'config', '--global', 'user.signingkey', signing_key])
            self.log_success(f"✅ Git configurado: user.signingkey = {signing_key}")
            
            # Habilitar firma de commits
            self.run_command(['git', 'config', '--global', 'commit.gpgsign', 'true'])
            self.log_success("✅ Git configurado: commit.gpgsign = true")
            
            # Habilitar firma de tags
            self.run_command(['git', 'config', '--global', 'tag.gpgSign', 'true'])
            self.log_success("✅ Git configurado: tag.gpgSign = true")
            
            # Configurar programa GPG
            self.run_command(['git', 'config', '--global', 'gpg.program', 'gpg'])
            self.log_success("✅ Git configurado: gpg.program = gpg")
            
            # Configurar GPG_TTY si está disponible
            try:
                tty_result = os.popen('tty').read().strip()
                if tty_result and 'not a tty' not in tty_result:
                    os.environ['GPG_TTY'] = tty_result
                    self.log_success(f"✅ GPG_TTY configurado: {tty_result}")
                else:
                    self.log_warning("⚠️  No se pudo configurar GPG_TTY (entorno sin TTY)")
            except Exception as e:
                self.log_warning(f"⚠️  Error configurando GPG_TTY: {e}")
            
        except Exception as e:
            self.log_error(f"Error configurando Git: {e}")
            raise

    def configure_git_for_gpg(self, key_id: str = None):
        """Configura Git para GPG con selección inteligente de llave"""
        try:
            # Verificar prerequisitos
            if not self.check_prerequisites_for_operation("git-config"):
                return False
                
            self.log_info("🔧 Configurando Git para GPG...")
            
            # 1. Determinar qué llave usar
            if key_id:
                # Usar llave específica proporcionada
                signing_key = key_id
                self.log_info(f"Usando llave específica: {signing_key}")
            else:
                # Selección automática (estrategia 1 + 2)
                signing_key = self.get_latest_valid_signing_key()
                if not signing_key:
                    self.log_error("No se encontraron llaves de firma válidas")
                    self.log_warning("⚠️ Deshabilitando uso de GPG en Git")
                    self.disable_git_gpg()
                    return False
                self.log_info(f"Usando llave automática: {signing_key}")
            
            # 2. Verificar que la llave existe y es válida
            if not self.verify_signing_key(signing_key):
                self.log_error(f"Llave {signing_key} no es válida para firma")
                self.log_warning("⚠️ Deshabilitando uso de GPG en Git")
                self.disable_git_gpg()
                return False
            
            # 3. Configurar Git
            self._configure_git_with_key(signing_key)
            
            # 4. Verificar configuración
            self.log_info("🔍 Verificando configuración...")
            result = self.run_command(["git", "config", "--global", "--get", "user.signingkey"])
            if result.returncode == 0 and result.stdout.strip() == signing_key:
                self.log_success("✅ Git configurado correctamente para GPG")
                
                # Obtener información del usuario para mostrar
                user_info = self.get_user_info_from_key(signing_key)
                
                print("\n" + "="*50)
                print("🎉 CONFIGURACIÓN GIT-GPG COMPLETADA")
                print("="*50)
                print(f"🔑 Subclave de firma: {signing_key}")
                if user_info['name']:
                    print(f"👤 Nombre: {user_info['name']}")
                if user_info['email']:
                    print(f"📧 Email: {user_info['email']}")
                print("📝 Commits firmados: Activado")
                print("🏷️  Tags firmados: Activado")
                print("🔧 GPG program: gpg")
                print()
                print("💡 Próximos pasos:")
                print("1. Probar firma: git commit --allow-empty -m 'Test GPG signature'")
                print("2. Verificar: git log --show-signature")
                print("3. Configurar GitHub: Agregar clave pública en Settings > SSH and GPG keys")
                print()
                print("⚠️  Nota sobre entornos sin TTY (Cursor, scripts):")
                print("   - GPG puede requerir configuración manual de GPG_TTY")
                print("   - En terminal interactivo: export GPG_TTY=$(tty)")
                print("   - Para scripts: configurar pinentry-mode loopback")
                print("="*50)
                
                return True
            else:
                self.log_error("❌ Error en la configuración de Git")
                self.log_warning("⚠️ Deshabilitando uso de GPG en Git")
                self.disable_git_gpg()
                return False
            
        except Exception as e:
            self.log_error(f"Error configurando Git: {e}")
            self.log_warning("⚠️ Deshabilitando uso de GPG en Git")
            self.disable_git_gpg()
            return False

    def load_keyserver_config(self) -> Dict[str, Any]:
        """Cargar configuración de keyservers desde YAML"""
        try:
            config_file = Path("configs/gpg-keyservers.yml")
            if not config_file.exists():
                self.log_error("Archivo de configuración de keyservers no encontrado")
                return {}
            
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return config.get('keyservers', {})
            
        except Exception as e:
            self.log_error(f"Error cargando configuración de keyservers: {e}")
            return {}

    def validate_keyserver_list(self, servers_list: str) -> bool:
        """Validar que la lista de keyservers existe"""
        try:
            config = self.load_keyserver_config()
            
            if not config:
                return False
            
            if servers_list not in config:
                available_lists = list(config.keys())
                self.log_error(f"❌ Lista de servers '{servers_list}' no encontrada")
                self.log_info(f"💡 Listas disponibles: {', '.join(available_lists)}")
                return False
            
            return True
            
        except Exception as e:
            self.log_error(f"Error validando lista de servers: {e}")
            return False

    def get_keyserver_list(self, servers_list: str = None) -> List[Dict[str, str]]:
        """Obtener lista de keyservers para publicar"""
        try:
            # Usar lista por defecto si no se especifica
            if not servers_list:
                servers_list = "recommended"
            
            # Validar que la lista existe
            if not self.validate_keyserver_list(servers_list):
                return []
            
            # Cargar configuración
            config = self.load_keyserver_config()
            if not config:
                return []
            
            # Obtener lista de keyservers
            keyservers = config.get(servers_list, [])
            
            # Ordenar por prioridad
            keyservers.sort(key=lambda x: x.get('priority', 999))
            
            return keyservers
            
        except Exception as e:
            self.log_error(f"Error obteniendo lista de keyservers: {e}")
            return []

    def publish_to_keyserver(self, key_id: str, keyserver: Dict[str, str]) -> bool:
        """Publicar llave en un keyserver específico"""
        try:
            name = keyserver.get('name', 'Unknown')
            url = keyserver.get('url', '')
            
            if not url:
                self.log_warning(f"⚠️ URL no válida para keyserver: {name}")
                return False
            
            # Publicar en keyserver
            result = self.run_command([
                'gpg', '--keyserver', url, '--send-keys', key_id
            ])
            
            if result.returncode == 0:
                self.log_success(f"✅ Publicado en {name}")
                return True
            else:
                self.log_warning(f"⚠️ Error en {name}: {result.stderr.strip()}")
                return False
                
        except Exception as e:
            self.log_warning(f"⚠️ Error publicando en {keyserver.get('name', 'Unknown')}: {e}")
            return False

    def verify_key_publication(self, key_id: str, keyserver: Dict[str, str]) -> bool:
        """Verificar que la llave se publicó correctamente"""
        try:
            name = keyserver.get('name', 'Unknown')
            url = keyserver.get('url', '')
            
            if not url:
                return False
            
            # Usar --recv-keys que es más confiable y funciona con ambos keyservers
            # Este método no tiene problemas con /dev/tty
            result = self.run_command([
                'gpg', '--batch', '--no-tty', '--keyserver', url, '--recv-keys', key_id
            ])
            
            if result.returncode == 0:
                # Verificar que la respuesta indica que la llave existe
                if 'sin cambios' in result.stdout or 'unchanged' in result.stdout:
                    self.log_success(f"✅ Verificado en {name}")
                    return True
                elif 'importada' in result.stdout or 'imported' in result.stdout:
                    self.log_success(f"✅ Verificado en {name} (nueva importación)")
                    return True
                else:
                    # Si no hay mensaje claro, pero el comando fue exitoso, asumir que está disponible
                    self.log_success(f"✅ Verificado en {name}")
                    return True
            else:
                self.log_warning(f"⚠️ No verificado en {name}")
                return False
                
        except Exception as e:
            self.log_warning(f"⚠️ Error verificando en {keyserver.get('name', 'Unknown')}: {e}")
            return False

    def publish_key_to_keyserver(self, servers_list: str = None):
        """Publicar llave pública en keyservers"""
        try:
            # Verificar prerequisitos
            if not self.check_prerequisites_for_operation("publish"):
                return False
            
            # Determinar qué llave publicar
            signing_key = self.get_latest_valid_signing_key()
            if not signing_key:
                self.log_error("No se encontraron llaves de firma válidas")
                return False
            
            self.log_info(f"Usando llave: {signing_key}")
            
            # Obtener lista de keyservers
            keyservers = self.get_keyserver_list(servers_list)
            if not keyservers:
                return False
            
            # Usar lista por defecto si no se especifica
            if not servers_list:
                servers_list = "recommended"
            
            self.log_info(f"📤 Publicando llave en keyservers de lista '{servers_list}'...")
            
            # Publicar en cada keyserver
            successful = 0
            failed = 0
            failed_servers = []
            
            for i, keyserver in enumerate(keyservers, 1):
                name = keyserver.get('name', 'Unknown')
                url = keyserver.get('url', '')
                
                self.log_info(f"🌐 Keyserver {i}/{len(keyservers)}: {name} ({url})")
                
                if self.publish_to_keyserver(signing_key, keyserver):
                    successful += 1
                else:
                    failed += 1
                    failed_servers.append(name)
            
            # Mostrar resumen
            print()
            if successful > 0:
                self.log_success(f"✅ Publicación completada en lista '{servers_list}': {successful}/{len(keyservers)} keyservers exitosos")
            else:
                self.log_error(f"❌ Publicación completada en lista '{servers_list}': 0/{len(keyservers)} keyservers exitosos")
            
            if failed > 0:
                self.log_warning(f"⚠️ {failed} keyserver(s) fallaron: {', '.join(failed_servers)}")
            
            # Informar sobre verificación manual
            if successful > 0:
                print()
                self.log_info("💡 Para verificar la publicación, use:")
                self.log_info(f"   gpg-manager.py --confirm-publish --servers {servers_list}")
                self.log_info("   (Espere 5-15 minutos para sincronización de keyservers)")
            
            return successful > 0
            
        except Exception as e:
            self.log_error(f"Error publicando llave: {e}")
            return False

    def confirm_key_publication(self, servers_list: str = None, key_id: str = None):
        """Verificar publicación de llave en keyservers"""
        try:
            # Verificar prerequisitos
            if not self.check_prerequisites_for_operation("publish"):
                return False
            
            # Determinar qué llave verificar
            if key_id:
                signing_key = key_id
                self.log_info(f"Verificando llave específica: {signing_key}")
            else:
                # Si solo existe una llave pública, usarla automáticamente
                signing_key = self.get_single_key_if_only_one()
                if not signing_key:
                    signing_key = self.get_latest_valid_signing_key()
                if not signing_key:
                    self.log_error("No se encontraron llaves de firma válidas")
                    return False
                self.log_info(f"Verificando llave automática: {signing_key}")
            
            # Obtener lista de keyservers
            keyservers = self.get_keyserver_list(servers_list)
            if not keyservers:
                return False
            
            # Usar lista por defecto si no se especifica
            if not servers_list:
                servers_list = "recommended"
            
            self.log_info(f"🔍 Verificando publicación en keyservers de lista '{servers_list}'...")
            
            # Verificar en cada keyserver
            verified = 0
            failed = 0
            failed_servers = []
            
            for i, keyserver in enumerate(keyservers, 1):
                name = keyserver.get('name', 'Unknown')
                url = keyserver.get('url', '')
                
                self.log_info(f"🌐 Keyserver {i}/{len(keyservers)}: {name} ({url})")
                
                if self.verify_key_publication(signing_key, keyserver):
                    verified += 1
                else:
                    failed += 1
                    failed_servers.append(name)
            
            # Mostrar resumen
            print()
            if verified > 0:
                self.log_success(f"✅ Verificación completada en lista '{servers_list}': {verified}/{len(keyservers)} keyservers verificados")
            else:
                self.log_warning(f"⚠️ Verificación completada en lista '{servers_list}': 0/{len(keyservers)} keyservers verificados")
            
            if failed > 0:
                self.log_warning(f"⚠️ {failed} keyserver(s) no verificados: {', '.join(failed_servers)}")
                self.log_info("💡 Los keyservers pueden tardar 5-15 minutos en sincronizar")
            
            return verified > 0
            
        except Exception as e:
            self.log_error(f"Error verificando publicación: {e}")
            return False

    def show_help(self):
        """Mostrar ayuda"""
        print("\n" + "="*50)
        print("🚀 GPG BACKUP MANAGER v1.0.0")
        print("="*50 + "\n")
        
        print("Gestor especializado de backups portables de GPG")
        print("Prioridad: BACKUP y RESTORE para uso cross-platform")
        print()
        
        print("Uso:")
        print("  gpg-manager.py --init                            Inicializar configuración GPG")
        print("  gpg-manager.py --gen-key                         Generar llave maestra y subclaves")
        print("  gpg-manager.py --git-config                      Configurar Git para GPG")
        print("  gpg-manager.py --publish                         Publicar llave pública en keyserver")
        print("  gpg-manager.py --confirm-publish                 Verificar publicación en keyservers")
        print("  gpg-manager.py --backup                           Crear backup portable")
        print("  gpg-manager.py --restore <archivo-backup>        Restaurar backup")
        print("  gpg-manager.py --verify <archivo-backup>         Verificar integridad")
        print("  gpg-manager.py --list                            Listar backups disponibles")
        print("  gpg-manager.py --help                            Mostrar esta ayuda")
        print()
        print("Prerequisitos:")
        print("  - gpg: Herramienta GPG (siempre requerida)")
        print("  - git: Para --git-config")
        print("  - tar: Para --backup, --restore, --verify")
        print("  - sha256sum: Para --backup")
        print()
        
        print("Ejemplos:")
        print("  gpg-manager.py --init")
        print("  gpg-manager.py --gen-key")
        print("  gpg-manager.py --git-config")
        print("  gpg-manager.py --publish")
        print("  gpg-manager.py --confirm-publish")
        print("  gpg-manager.py --confirm-publish --servers ubuntu")
        print("  gpg-manager.py --backup")
        print("  gpg-manager.py --restore gpg-20241214_143022.tar.gz")
        print("  gpg-manager.py --verify ~/backups/gpg-backup.tar.gz")
        print("  gpg-manager.py --list")
        print()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="GPG Backup Manager v1.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  gpg-manager.py --init
  gpg-manager.py --gen-key
  gpg-manager.py --git-config
  gpg-manager.py --publish
  gpg-manager.py --confirm-publish
  gpg-manager.py --confirm-publish --servers ubuntu
  gpg-manager.py --backup
  gpg-manager.py --restore gpg-20241214_143022.tar.gz
  gpg-manager.py --verify ~/backups/gpg-backup.tar.gz
  gpg-manager.py --list
        """
    )
    
    parser.add_argument("--init", "-i", action="store_true", 
                       help="Inicializar configuración GPG")
    parser.add_argument("--gen-key", "-g", action="store_true",
                       help="Generar llave maestra y subclaves")
    parser.add_argument("--git-config", action="store_true",
                       help="Configurar Git para GPG")
    parser.add_argument("--publish", action="store_true",
                       help="Publicar llave pública en keyserver")
    parser.add_argument("--confirm-publish", action="store_true",
                       help="Verificar publicación de llave en keyservers")
    parser.add_argument("--servers", metavar="LISTA",
                       help="Lista específica de keyservers (recommended, ubuntu, mit)")
    parser.add_argument("--key-id", metavar="KEY_ID",
                       help="ID específico de llave para publicar/verificar")
    parser.add_argument("--backup", "-b", action="store_true",
                       help="Crear backup portable")
    parser.add_argument("--restore", "-r", metavar="ARCHIVO",
                       help="Restaurar backup")
    parser.add_argument("--verify", "-v", metavar="ARCHIVO",
                       help="Verificar integridad")
    parser.add_argument("--list", "-l", action="store_true",
                       help="Listar backups disponibles")
    
    args = parser.parse_args()
    
    # Si no se proporcionan argumentos, mostrar ayuda
    if not any(vars(args).values()):
        parser.print_help()
        return
        
    # Crear instancia del gestor
    gpg_manager = GPGManager()
    
    try:
        if args.init:
            gpg_manager.initialize_gpg()
        elif args.gen_key:
            gpg_manager.generate_master_key_and_subkeys()
        elif args.git_config:
            gpg_manager.configure_git_for_gpg()
        elif args.publish:
            gpg_manager.publish_key_to_keyserver(args.servers)
        elif args.confirm_publish:
            gpg_manager.confirm_key_publication(args.servers, args.key_id)
        elif args.backup:
            gpg_manager.create_portable_gpg_backup()
        elif args.restore:
            gpg_manager.restore_portable_gpg(args.restore)
        elif args.verify:
            gpg_manager.verify_backup_integrity(args.verify)
        elif args.list:
            gpg_manager.list_available_backups()
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        gpg_manager.log_error(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
