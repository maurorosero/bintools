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
        """Configurar GPG para automatización con pinentry-mode loopback"""
        gpg_conf = self.gpg_home / "gpg.conf"
        gpg_agent_conf = self.gpg_home / "gpg-agent.conf"
        
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
        
        # Crear backup automático
        self.log_info("💾 Creando backup automático de subclaves...")
        self.create_portable_gpg_backup()
        
        self.log_success("✅ Llave maestra y subclaves generadas exitosamente")
        
    def initialize_gpg(self):
        """Inicializar configuración GPG"""
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
        gpg_conf.write_text("""# Configuración básica de GPG
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
pinentry-mode loopback

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
        gpg_agent_conf.write_text("""# Configuración del agente GPG
# Generada automáticamente por gpg-manager.py --init

# Configuración de pinentry
pinentry-program /usr/bin/pinentry-gtk-2

# Configuración de caché
default-cache-ttl 600
max-cache-ttl 7200

# Configuración de SSH
enable-ssh-support

# Configuración de scdaemon
scdaemon-program /usr/lib/gnupg/scdaemon
""")
        
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
        self.log_info("🌐 Creando backup portable de configuración GPG...")
        
        # Verificar pre-requisitos
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
        print("  gpg-manager.py --backup                           Crear backup portable")
        print("  gpg-manager.py --restore <archivo-backup>        Restaurar backup")
        print("  gpg-manager.py --verify <archivo-backup>         Verificar integridad")
        print("  gpg-manager.py --list                            Listar backups disponibles")
        print("  gpg-manager.py --help                            Mostrar esta ayuda")
        print()
        
        print("Ejemplos:")
        print("  gpg-manager.py --init")
        print("  gpg-manager.py --gen-key")
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
