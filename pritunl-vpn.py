#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Check Heading
Copyright (C) <2025> MAURO ROSERO PÉREZ (ROSERO ONE DEVELOPMENT)

Script Name: pritunl-vpn.py
Version:     1.0.4
Description: Script multiplataforma para instalar o desinstalar el cliente VPN de Pritunl.
Created:     2025-05-19 20:56:28
Modified:    2025-06-18 14:39:34
Author:      Mauro Rosero Pérez <mauro@rosero.one>
Assistant:   Cursor AI (https://cursor.com)
"""

# Test: Modificación para probar actualización automática de fecha
"""
PRITUNL VPN - Instalar o Desinstalar el cliente VPN de Pritunl.
"""

import argparse
import os
import platform
import subprocess
import sys
import logging
import shutil
from pathlib import Path
import shlex # Para dividir comandos de forma segura si es necesario
import time # Para añadir pausas si es necesario
import requests # Añadido para descargas
import ctypes # Añadido para la comprobación de administrador en Windows

# --- Dependencias Externas (necesitan requirements.txt) ---
# Verificar si se solicita ayuda antes de importar dependencias
SHOW_HELP = any(arg in sys.argv for arg in ['--help', '-h', '--version'])

if not SHOW_HELP:
    try:
        from rich.console import Console
        from rich.logging import RichHandler
        from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
        from rich.panel import Panel # Importar Panel
        from rich.align import Align # Importar Align para centrar
        import questionary
    except ImportError:
        print(
            "ERROR: Faltan dependencias. Ejecuta: ./packages.sh --list base para instalar los prerrequisitos.",
            file=sys.stderr
        )
        sys.exit(1)
else:
    # Para help/version, usar imports básicos
    from rich.console import Console
    from rich.panel import Panel
    from rich.align import Align

# --- Constantes y Configuración Global ---
APP_NAME = "Instalador del Cliente Pritunl VPN "
APP_VERSION = "0.2.0"
APP_AUTHOR = "Mauro Rosero Pérez (mauro.rosero@gmail.com)" # Añadido
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_DIR = SCRIPT_DIR / "config"
SIGN_FILE = CONFIG_DIR / "pritunl-client.sign"
DEFAULT_LOG_DIR_USER = SCRIPT_DIR / "logs" # Log de usuario por defecto en subdir del script

# Variables globales (se establecerán en setup_logging y load_signature_key)
log = logging.getLogger(APP_NAME)
console = Console()
PRITUNL_SIGN = "" # Clave GPG global

# --- Función para mostrar Banner ---
def show_banner():
    """Muestra un banner estilizado sin recuadros."""
    banner_content = (
        f"[bold cyan]{APP_NAME}[/bold cyan]\\n\\n"
        f"Versión: [yellow]{APP_VERSION}[/yellow]\\n"
        f"Por: [green]{APP_AUTHOR}[/green]"
    )
    console.print(Align.center(banner_content))
    console.print() # Línea en blanco después del banner

# --- Función para mostrar Banner Simple (para help) ---
def show_banner_simple():
    """Muestra un banner simple para cuando no hay dependencias completas."""
    banner_content = (
        f"{APP_NAME}\\n"
        f"Versión: {APP_VERSION}\\n"
        f"Por: {APP_AUTHOR}"
    )
    console.print(Align.center(banner_content))
    console.print()

# --- Configuración de Logging ---
def setup_logging():
    """Configura el sistema de logging usando rich."""
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    log_type = os.getenv("PRITUNL_LOG_TYPE", "system").lower()
    log_file_path = None
    log_to_file = True

    if log_type == "system":
        # Solo root puede escribir aquí normalmente
        log_dir = Path("/var/log")
        log_filename = os.getenv("PRITUNL_LOG_FILENAME", f"{Path(sys.argv[0]).stem}.log")
        log_file_path = log_dir / log_filename
    elif log_type == "user":
        user_log_file_env = os.getenv("PRITUNL_USER_LOG_FILE")
        if user_log_file_env:
            log_file_path = Path(user_log_file_env)
        else:
            # Por defecto en subdirectorio 'logs' si no se especifica
            log_dir = DEFAULT_LOG_DIR_USER
            log_filename = os.getenv("PRITUNL_LOG_FILENAME", f"{Path(sys.argv[0]).stem}.log")
            log_file_path = log_dir / log_filename
    else:
        console.print(f"[yellow]Advertencia:[/yellow] PRITUNL_LOG_TYPE inválido ('{log_type}'). Deshabilitando log a archivo.")
        log_to_file = False

    # Configuración básica del logger
    log.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Handler para la consola con Rich
    # Usamos stderr=True para que los logs no interfieran con posible salida de datos a stdout
    rich_handler = RichHandler(console=console, show_path=False, log_time_format="[%Y-%m-%d %H:%M:%S]")
    rich_handler.setFormatter(logging.Formatter("%(message)s")) # Rich maneja el formato
    log.addHandler(rich_handler)

    # Handler para el archivo (si aplica)
    if log_to_file and log_file_path:
        try:
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            log.addHandler(file_handler)
            log.info(f"Logging configurado. Consola: {log_level_str}, Archivo ({log_type}): {log_file_path}")
        except PermissionError:
            log.warning(f"Permiso denegado para escribir en {log_file_path}. Logging a archivo deshabilitado.")
        except Exception as e:
            log.warning(f"No se pudo configurar el log a archivo ({log_file_path}): {e}. Logging a archivo deshabilitado.")
    else:
         log.info(f"Logging configurado. Consola: {log_level_str}, Archivo: Deshabilitado")


# --- Funciones Auxiliares ---
def print_info(message):
    log.info(message)
    # console.print(f"[cyan]INFO:[/cyan] {message}") # RichHandler ya imprime logs INFO

def print_success(message):
    log.info(message) # Loguear como INFO pero mostrar como éxito
    console.print(f"[green]✓[/green] {message}")

def print_warning(message):
    log.warning(message)
    # console.print(f"[yellow]Advertencia:[/yellow] {message}") # RichHandler ya imprime logs WARNING

def print_error(message, exit_code=None):
    log.error(message)
    # console.print(f"[bold red]ERROR:[/bold red] {message}", file=sys.stderr) # RichHandler ya imprime logs ERROR
    if exit_code is not None:
        sys.exit(exit_code)

def command_exists(cmd):
    """Verifica si un comando existe en el PATH."""
    return shutil.which(cmd) is not None

def run_command(cmd_list, check=True, capture_output=False, text=True, sudo=False, shell=False, env=None, input=None, status_message=None):
    """Ejecuta un comando de forma segura, opcionalmente con un spinner."""
    if not isinstance(cmd_list, list) and not shell:
        cmd_list = shlex.split(cmd_list)
    if sudo and os.geteuid() != 0:
         cmd_list.insert(0, 'sudo')

    log.debug(f"Ejecutando comando: {' '.join(cmd_list)}")

    # Determinar si ocultar salida para spinner
    stdout_pipe = subprocess.PIPE if status_message else None
    stderr_pipe = subprocess.PIPE if status_message else None

    try:
        if status_message:
            with console.status(f"[bold green]{status_message}...", spinner="dots") as status:
                process = subprocess.run(
                    cmd_list, check=check, capture_output=True, text=text,
                    shell=shell, env=env, input=input
                )
        else:
            # Ejecutar normalmente si no hay mensaje de estado
            process = subprocess.run(
                cmd_list, check=check, capture_output=capture_output, text=text,
                shell=shell, env=env, input=input
            )

        # Loguear salida si se capturó (especialmente útil si se ocultó por el spinner)
        if process.stdout:
            log.debug(f"Salida stdout: {process.stdout.strip()}")
        if process.stderr:
            log.debug(f"Salida stderr: {process.stderr.strip()}")

        return process

    except subprocess.CalledProcessError as e:
        # Loguear salida completa del error aunque se usara spinner
        if hasattr(e, 'stdout') and e.stdout:
            log.error(f"Salida stdout del comando fallido: {e.stdout.strip()}")
        if hasattr(e, 'stderr') and e.stderr:
             log.error(f"Salida stderr del comando fallido: {e.stderr.strip()}")
        print_error(f"El comando falló con código {e.returncode}: {' '.join(e.cmd)}")
        raise
    except FileNotFoundError:
        print_error(f"Comando no encontrado: {cmd_list[0]}")
        raise
    except Exception as e:
        log.exception("Error inesperado ejecutando el comando:")
        print_error(f"Error inesperado al ejecutar {' '.join(cmd_list)}: {e}")
        raise

def load_signature_key():
    """Carga la clave GPG de firma desde el archivo de configuración."""
    global PRITUNL_SIGN
    print_info(f"Buscando archivo de firma en: {SIGN_FILE}")
    if not SIGN_FILE.is_file():
        print_error(f"Archivo de firma no encontrado en '{SIGN_FILE}'.")
        print_error("Por favor, cree el archivo y pegue la clave GPG dentro.")
        return False
    try:
        content = SIGN_FILE.read_text().strip()
        if not content:
            print_error(f"El archivo de firma '{SIGN_FILE}' está vacío.")
            return False
        PRITUNL_SIGN = content
        print_success(f"Clave de firma cargada exitosamente desde {SIGN_FILE}.")
        return True
    except Exception as e:
        print_error(f"Error al leer el archivo de firma '{SIGN_FILE}': {e}")
        return False

def check_internet(timeout=3):
    """Verifica la conexión a internet intentando conectar a un servidor DNS."""
    print_info("Verificando conexión a internet...")
    try:
        # Intenta resolver y conectar a un host conocido (Google DNS)
        run_command(["ping", "-c", "1", f"-W", str(timeout), "8.8.8.8"], check=True, capture_output=True)
        print_success("Conexión a internet verificada.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Si ping falla, intentar con curl como fallback
        try:
            run_command(["curl", "-s", "--head", "--fail", "--connect-timeout", str(timeout), "https://google.com"], check=True, capture_output=True)
            print_success("Conexión a internet verificada (vía curl).")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error("No hay conexión a internet.")
            return False

def check_prerequisites_common():
    """Verifica requisitos comunes como internet y comandos básicos."""
    if not check_internet():
        return False

    essentials = []
    system = platform.system()
    if system == "Linux":
        essentials = ["curl", "gpg", "tee"]
    elif system == "Darwin": # macOS
        essentials = ["curl", "installer"]
    elif system == "Windows":
        # En Windows, 'requests' maneja la descarga, y ejecutamos .exe/.msi
        # No hay requisitos de comandos externos específicos como en Linux/Mac
        # Podríamos verificar PowerShell si fuera necesario más adelante.
        print_info("Verificación de requisitos en Windows omitida (se usa requests y ejecución directa).")
        return True # Asumir OK por ahora
    else:
        print_error(f"Sistema operativo '{system}' no compatible para la verificación de requisitos.")
        return False

    # Esta parte solo se ejecuta para Linux/macOS
    print_info(f"Verificando comandos esenciales ({', '.join(essentials)})...")
    missing = [cmd for cmd in essentials if not command_exists(cmd)]
    if missing:
        for cmd in missing:
            print_error(f"Comando esencial '{cmd}' no encontrado. Por favor, instálalo.")
        return False
    print_success("Comandos esenciales encontrados.")
    return True

def get_os_info():
    """Obtiene información detallada del sistema operativo."""
    system = platform.system()
    info = {"system": system, "distro": None, "version": None, "codename": None, "pretty_name": None}

    if system == "Linux":
        try:
            # Usar platform.freedesktop_os_release() que es más robusto
            os_release = platform.freedesktop_os_release()
            info["distro"] = os_release.get("ID", "").lower()
            info["version"] = os_release.get("VERSION_ID", "").lower()
            info["codename"] = os_release.get("VERSION_CODENAME", "").lower()
            info["pretty_name"] = os_release.get('PRETTY_NAME', 'Linux')
            print_info(f"Detectada distribución: {info['pretty_name']}")
        except OSError:
             print_warning("No se pudo leer /etc/os-release o /usr/lib/os-release. Detección de distro limitada.")
             # Podríamos intentar usar platform.linux_distribution() como fallback (obsoleto)
    elif system == "Darwin":
        info["distro"] = "macos"
        info["version"] = platform.mac_ver()[0]
        info["pretty_name"] = f"macOS {info['version']}"
        print_info(f"Detectado sistema operativo: {info['pretty_name']}")
    elif system == "Windows":
        info["distro"] = "windows"
        # platform.version() puede dar la build N. ej: '10.0.19042'
        info["version"] = platform.version()
        info["pretty_name"] = f"Windows {platform.release()} ({info['version']})"
        print_info(f"Detectado sistema operativo: {info['pretty_name']}")
    else:
        print_error(f"Sistema operativo no compatible: {system}")

    return info

def check_if_client_installed(os_info):
    """Verifica si el cliente Pritunl ya está instalado."""
    print_info("Verificando si Pritunl Client ya está instalado...")
    system = os_info["system"]
    installed = False

    if system == "Linux":
        # Intentar con los gestores de paquetes comunes
        pkg_name = "pritunl-client-electron" # El paquete principal
        try:
            if command_exists("dpkg"): # Debian/Ubuntu
                result = run_command(["dpkg-query", "-W", "-f='${Status}'", pkg_name], check=False, capture_output=True)
                installed = "install ok installed" in result.stdout
            elif command_exists("rpm"): # RHEL/Fedora/etc.
                result = run_command(["rpm", "-q", pkg_name], check=False, capture_output=True)
                installed = result.returncode == 0
            elif command_exists("pacman"): # Arch
                 result = run_command(["pacman", "-Q", pkg_name], check=False, capture_output=True)
                 installed = result.returncode == 0
            elif command_exists(pkg_name): # Último recurso
                 print_warning("Gestor de paquetes no detectado claramente, usando 'command_exists'.")
                 installed = True
        except Exception as e:
            log.debug(f"Error al verificar el paquete {pkg_name}: {e}")
            installed = False # Asumir no instalado si hay error

    elif system == "Darwin":
        app_path = Path("/Applications/Pritunl.app")
        installed = app_path.is_dir()

    elif system == "Windows":
        # Comprobar la existencia de la carpeta de instalación por defecto
        # La ruta puede variar ligeramente (Program Files vs Program Files (x86))
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        app_path = Path(program_files) / "Pritunl"
        app_path_x86 = Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "Pritunl"

        # Comprobar también la existencia del ejecutable principal como doble check
        exe_path = app_path / "pritunl.exe"
        exe_path_x86 = app_path_x86 / "pritunl.exe"

        installed = (app_path.is_dir() and exe_path.is_file()) or \
                    (app_path_x86.is_dir() and exe_path_x86.is_file())

    if installed:
        print_success("Pritunl Client ya se encuentra instalado.")
    else:
        print_info("Pritunl Client no está instalado.")

    return installed

# --- Lógica de Instalación Específica por OS ---

def _install_ubuntu_common(codename, gpg_key):
    """Lógica común para instalar en Ubuntu con spinners."""
    print_info(f"Instalando Pritunl Client para Ubuntu {codename.capitalize()}...")
    try:
        # Asegurar dependencias iniciales
        run_command(["sudo", "apt-get", "update", "-qq"], status_message="Actualizando lista de paquetes (apt update)")
        run_command(["sudo", "apt-get", "install", "-y", "gnupg", "curl"], status_message="Instalando dependencias (gnupg, curl)")

        # Añadir repo
        repo_line = f"deb https://repo.pritunl.com/stable/apt {codename} main"
        run_command(["sudo", "tee", "/etc/apt/sources.list.d/pritunl.list"], input=repo_line, status_message="Añadiendo repositorio Pritunl")

        # Añadir clave GPG
        gpg_status_msg = "Importando clave GPG"
        if codename == "noble":
            keyring_path = "/usr/share/keyrings/pritunl-archive-keyring.gpg"
            run_command(["sudo", "rm", "-f", keyring_path], check=False)
            run_command([
                "sudo", "gpg", "--no-default-keyring", "--keyring", keyring_path,
                "--keyserver", "hkp://keyserver.ubuntu.com", "--recv-keys", gpg_key
            ], status_message=gpg_status_msg)
            run_command(["sudo", "sed", "-i", f"s|^deb https|deb [signed-by={keyring_path}] https|", "/etc/apt/sources.list.d/pritunl.list"], status_message="Configurando firma de repositorio")
        else:
            run_command([
                "sudo", "apt-key", "adv", "--keyserver", "hkp://keyserver.ubuntu.com", "--recv", gpg_key
            ], status_message=gpg_status_msg)

        # Actualizar e instalar
        run_command(["sudo", "apt-get", "update", "-qq"], status_message="Actualizando lista de paquetes (post-repo)")
        run_command(["sudo", "apt-get", "install", "-y", "pritunl-client-electron"], status_message="Instalando pritunl-client-electron")
        print_success(f"Cliente Pritunl instalado exitosamente para Ubuntu {codename.capitalize()}." )
        return True
    except Exception as e:
        # run_command ya debería haber mostrado el error
        log.error(f"Fallo general en la instalación de Ubuntu {codename.capitalize()}: {e}")
        return False

def _install_ubuntu_noble(gpg_key):
    return _install_ubuntu_common("noble", gpg_key)

def _install_ubuntu_jammy(gpg_key):
    return _install_ubuntu_common("jammy", gpg_key)

def _install_rhel9(gpg_key):
    """Instala en RHEL 9 y derivados con spinners."""
    print_info("Instalando Pritunl Client para RHEL 9 y derivados...")
    pkg_manager = "dnf" if command_exists("dnf") else "yum"
    if not pkg_manager: print_error("dnf/yum no encontrado."); return False

    try: os_release = platform.freedesktop_os_release(); distro_id = os_release.get("ID", "oraclelinux")
    except OSError: distro_id = "oraclelinux"
    print_info(f"Usando ID de distribución para el repositorio: {distro_id}")

    repo_content = f"""[pritunl]
name=Pritunl Stable Repository
baseurl=https://repo.pritunl.com/stable/yum/{distro_id}/9/
gpgcheck=1
enabled=1
gpgkey=https://raw.githubusercontent.com/pritunl/pgp/master/pritunl_repo_pub.asc
"""
    try:
        run_command(["sudo", "tee", "/etc/yum.repos.d/pritunl.repo"], input=repo_content, status_message="Añadiendo repositorio Pritunl")
        run_command(["sudo", pkg_manager, "-y", "install", "pritunl-client-electron"], status_message=f"Instalando pritunl-client-electron ({pkg_manager})")
        print_success(f"Cliente Pritunl instalado (RHEL 9 / {distro_id}).")
        return True
    except Exception as e: return False

def _install_arch(gpg_key):
    """Instala en Arch Linux con spinners."""
    print_info("Instalando Pritunl Client para Arch Linux...")
    pacman_conf = Path("/etc/pacman.conf")
    repo_entry = "\n[pritunl]\nServer = https://repo.pritunl.com/stable/pacman\n"
    try:
        content = run_command(["sudo", "cat", str(pacman_conf)], capture_output=True, status_message="Verificando pacman.conf").stdout
        if "[pritunl]" not in content:
             run_command(["sudo", "tee", "-a", str(pacman_conf)], input=repo_entry, status_message="Añadiendo repositorio Pritunl a pacman.conf")
        else: print_info("Repositorio [pritunl] ya existe.")

        run_command(["sudo", "pacman-key", "--keyserver", "hkp://keyserver.ubuntu.com", "-r", gpg_key], status_message="Importando clave GPG")
        run_command(["sudo", "pacman-key", "--lsign-key", gpg_key], status_message="Firmando clave GPG localmente")
        run_command(["sudo", "pacman", "-Sy", "--noconfirm"], status_message="Sincronizando bases de datos (pacman -Sy)")
        run_command(["sudo", "pacman", "-S", "--noconfirm", "pritunl-client-electron"], status_message="Instalando pritunl-client-electron (pacman -S)")
        print_success("Cliente Pritunl instalado (Arch Linux).")
        return True
    except Exception as e: return False

def _install_macos(gpg_key):
    """Instala en macOS con barra de progreso para descarga."""
    print_info("Instalando Pritunl Client para macOS...")
    pkg_url = "https://client.pritunl.com/dist/Pritunl.pkg"
    tmp_pkg = Path(f"/tmp/Pritunl_{os.getpid()}.pkg")

    try:
        # Descarga con requests y barra de progreso de rich
        print_info(f"Descargando {pkg_url}...")
        response = requests.get(pkg_url, stream=True)
        response.raise_for_status() # Lanza excepción si hay error HTTP
        total_size = int(response.headers.get('content-length', 0))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            download_task = progress.add_task("Descargando", total=total_size)
            with open(tmp_pkg, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress.update(download_task, advance=len(chunk))
        print_success(f"Paquete descargado a {tmp_pkg}.")

        # Instalación con spinner
        run_command(["sudo", "installer", "-pkg", str(tmp_pkg), "-target", "/"], status_message="Instalando paquete (.pkg)")
        print_success("Cliente Pritunl instalado (macOS).")
        return True
    except requests.exceptions.RequestException as e:
        print_error(f"Error de descarga: {e}")
        return False
    except Exception as e:
        print_error(f"Falló la instalación en macOS: {e}")
        return False
    finally:
        if tmp_pkg.exists():
            print_info(f"Limpiando {tmp_pkg}...")
            try: tmp_pkg.unlink()
            except OSError as e: print_warning(f"No se pudo eliminar {tmp_pkg}: {e}")

def _install_windows():
    """Instala en Windows con barra de progreso y ejecución silenciosa."""
    print_info("Instalando Pritunl Client para Windows...")
    installer_url = "https://client.pritunl.com/dist/Pritunl.exe"
    # Usar %TEMP% para el archivo descargado
    temp_dir = Path(os.environ.get("TEMP", "C:\\Windows\\Temp"))
    tmp_exe = temp_dir / f"Pritunl_{os.getpid()}.exe"

    try:
        # Descarga con requests y barra de progreso de rich
        print_info(f"Descargando {installer_url}...")
        response = requests.get(installer_url, stream=True)
        response.raise_for_status() # Lanza excepción si hay error HTTP
        total_size = int(response.headers.get('content-length', 0))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            download_task = progress.add_task("Descargando", total=total_size)
            with open(tmp_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress.update(download_task, advance=len(chunk))
        print_success(f"Instalador descargado a {tmp_exe}.")

        # Instalación silenciosa
        # Flags comunes para Inno Setup: /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
        install_cmd = [str(tmp_exe), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]
        # No usamos sudo aquí, la ejecución ya debe ser como admin
        run_command(install_cmd, status_message="Instalando Pritunl Client (silencioso)")
        print_success("Cliente Pritunl instalado (Windows).")
        return True

    except requests.exceptions.RequestException as e:
        print_error(f"Error de descarga: {e}")
        return False
    except subprocess.CalledProcessError as e:
        # run_command ya loguea el error
        print_error(f"Falló la ejecución del instalador.")
        return False
    except PermissionError as e:
        print_error(f"Error de permisos al intentar instalar. ¿Se está ejecutando como Administrador? Error: {e}")
        return False
    except Exception as e:
        print_error(f"Falló la instalación en Windows: {e}")
        log.exception("Detalles del error de instalación en Windows:")
        return False
    finally:
        if tmp_exe.exists():
            print_info(f"Limpiando {tmp_exe}...")
            try:
                tmp_exe.unlink()
            except OSError as e:
                print_warning(f"No se pudo eliminar {tmp_exe}: {e}")

# --- Lógica de Desinstalación Específica por OS ---

def _uninstall_linux(os_info):
    """Desinstala en distribuciones Linux soportadas."""
    print_info("Desinstalando Pritunl Client (Linux)...")
    pkg_manager = None; remove_cmd = []; pkg_name = "pritunl-client-electron"

    if command_exists("dpkg"): pkg_manager = "apt-get"; remove_cmd = ["sudo", pkg_manager, "remove", "-y", pkg_name]
    elif command_exists("rpm"): pkg_manager = "dnf" if command_exists("dnf") else "yum"; remove_cmd = ["sudo", pkg_manager, "remove", "-y", pkg_name] if pkg_manager else []
    elif command_exists("pacman"): pkg_manager = "pacman"; remove_cmd = ["sudo", pkg_manager, "-Rs", "--noconfirm", pkg_name]

    if not remove_cmd: print_error("Gestor de paquetes no compatible."); return False

    try:
        run_command(remove_cmd, status_message=f"Desinstalando {pkg_name} ({pkg_manager})")
        print_success(f"Paquete {pkg_name} desinstalado.")
        return True
    except Exception as e: return False

def _uninstall_macos():
    """Desinstala en macOS con spinner."""
    print_info("Desinstalando Pritunl Client (macOS)...")
    app_path = Path("/Applications/Pritunl.app")
    if not app_path.exists(): print_info("Aplicación no encontrada."); return True
    try:
        run_command(["sudo", "rm", "-rf", str(app_path)], status_message=f"Eliminando {app_path}")
        print_success("Aplicación eliminada.")
        print_warning("Pueden quedar archivos en ~/Library/Application Support/Pritunl")
        return True
    except Exception as e: return False

def _uninstall_windows():
    """Desinstala Pritunl Client en Windows de forma silenciosa."""
    print_info("Desinstalando Pritunl Client (Windows)...")
    uninstaller_path = None
    # Buscar el desinstalador en las rutas comunes
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    app_path = Path(program_files) / "Pritunl"
    app_path_x86 = Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "Pritunl"

    potential_uninstaller = app_path / "unins000.exe"
    potential_uninstaller_x86 = app_path_x86 / "unins000.exe"

    if potential_uninstaller.is_file():
        uninstaller_path = potential_uninstaller
    elif potential_uninstaller_x86.is_file():
        uninstaller_path = potential_uninstaller_x86

    if not uninstaller_path:
        print_warning("No se encontró el desinstalador automático (unins000.exe). Puede que necesite desinstalarlo manualmente desde 'Agregar o quitar programas'.")
        # Consideramos éxito parcial si no lo encontramos, ya que no está donde debería.
        return True

    try:
        print_info(f"Ejecutando desinstalador: {uninstaller_path}")
        # Flags comunes para Inno Setup: /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
        uninstall_cmd = [str(uninstaller_path), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]
        # No usamos sudo, se asume ejecución como admin
        run_command(uninstall_cmd, status_message="Desinstalando Pritunl Client (silencioso)")
        print_success("Cliente Pritunl desinstalado (Windows).")
        # Podríamos añadir limpieza de directorios residuales si fuera necesario
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Falló la ejecución del desinstalador.")
        return False
    except PermissionError as e:
         print_error(f"Error de permisos al intentar desinstalar. ¿Se está ejecutando como Administrador? Error: {e}")
         return False
    except Exception as e:
        print_error(f"Falló la desinstalación en Windows: {e}")
        log.exception("Detalles del error de desinstalación en Windows:")
        return False

# --- Funciones Principales de Acción ---

def install_client_os(os_info, gpg_key):
    """Instala el cliente Pritunl basado en la información del OS."""
    system = os_info["system"]
    distro = os_info["distro"]
    codename = os_info["codename"]
    version = os_info["version"]

    install_func = None

    if system == "Linux":
        if distro == "ubuntu":
            if codename == "noble": install_func = _install_ubuntu_noble
            elif codename == "jammy": install_func = _install_ubuntu_jammy
            else: print_error(f"Versión de Ubuntu no compatible: {os_info.get('pretty_name', codename)}")
        elif distro in ["almalinux", "rhel", "rocky", "oracle"]:
            if version and version.startswith("9"): install_func = _install_rhel9
            else: print_error(f"Versión de {os_info.get('pretty_name', distro)} no compatible ({version}). Se requiere v9.")
        elif distro == "arch":
            install_func = _install_arch
        else:
            print_error(f"Distribución Linux no reconocida o no compatible: {os_info.get('pretty_name', distro)}")
    elif system == "Darwin":
        install_func = _install_macos
    elif system == "Windows":
        install_func = _install_windows
    else:
        print_error(f"Sistema operativo no compatible: {system}")

    if install_func:
        return install_func(gpg_key)
    else:
        return False

def uninstall_client_os(os_info):
    """Desinstala el cliente Pritunl basado en la información del OS."""
    system = os_info["system"]

    if system == "Linux":
        return _uninstall_linux(os_info)
    elif system == "Darwin":
        return _uninstall_macos()
    elif system == "Windows":
        return _uninstall_windows()
    else:
        print_error(f"Sistema operativo no compatible para desinstalación: {system}")
        return False


# --- Flujo Principal ---
def main():
    # --- Limpiar pantalla y mostrar banner al inicio ---
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Usar banner apropiado según el contexto
    if SHOW_HELP:
        show_banner_simple()
    else:
        show_banner()

    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{APP_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplo:\\n  %(prog)s --install\\n  %(prog)s --remove"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Verifica si Pritunl Client está instalado y lo instala si no lo está."
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Verifica si Pritunl Client está instalado y lo desinstala si lo está."
    )
    parser.add_argument(
        '--version', action='version', version=f'%(prog)s {APP_VERSION}'
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # --- 1. Determinar Acción ---
    action_to_perform = None
    if args.install:
        action_to_perform = "install"
    elif args.remove:
        action_to_perform = "remove"
    else:
        # Should be caught by argparse if len(sys.argv) > 1, but defensive check
        print("ERROR: No se especificó una acción válida (--install o --remove).", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    # --- Early Checks (No Root/Admin Needed Yet) ---
    # Use basic print/stderr for messages before logging is set up in root context
    os_info = get_os_info() # get_os_info uses print_info internally which logs if setup
    if not os_info.get("system"):
         # Use print directly as logging might not be available or configured yet
         print("ERROR: No se pudo determinar el sistema operativo.", file=sys.stderr)
         sys.exit(1)

    # check_if_client_installed uses logging, which is fine, it just might not go to file yet
    is_installed = check_if_client_installed(os_info)

    # --- 2. Check Preconditions & Exit if Action Not Needed ---
    if action_to_perform == "install" and is_installed:
        # Use standard print here as logging might not be fully configured yet
        # and we want to ensure the user sees this message before exiting.
        print("INFO: Cliente ya instalado. No se necesita ninguna acción.")
        sys.exit(0)
    elif action_to_perform == "remove" and not is_installed:
        # Use standard print for the same reason as above.
        print("INFO: Cliente no instalado. No hay nada que desinstalar.")
        sys.exit(0)

    # --- Action is needed (installing on non-installed, or removing on installed) ---

    # --- 3. Handle Permissions (If Action is Needed) ---
    needs_elevation = True # Install/Remove always needs elevation
    has_elevation = False
    system = os_info["system"]

    if system == "Windows":
        try:
            has_elevation = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except AttributeError:
            print_warning("No se pudo verificar el estado de administrador (AttributeError en ctypes). Asumiendo que no es administrador.")
            has_elevation = False
        except Exception as e:
            print_warning(f"Error inesperado verificando estado de administrador: {e}. Asumiendo que no.")
            has_elevation = False

        if needs_elevation and not has_elevation:
            print_error("Se requieren privilegios de Administrador para instalar o desinstalar.", exit_code=None)
            print_error("Por favor, ejecuta este script de nuevo haciendo clic derecho -> Ejecutar como administrador.", exit_code=1)
        # Si ya tiene elevación, continuamos...

    elif system in ["Linux", "Darwin"]:
        has_elevation = os.geteuid() == 0
        if needs_elevation and not has_elevation:
            # Re-execute with sudo
            print("INFO: Se requieren privilegios de superusuario. Intentando re-ejecutar con sudo...")
            try:
                cmd_to_rerun = ['sudo', sys.executable, *sys.argv]
                print(f"INFO: Ejecutando: {' '.join(cmd_to_rerun)}")
                process = subprocess.run(cmd_to_rerun, check=True)
                sys.exit(process.returncode) # Exit with the code from the sudo'd process
            except subprocess.CalledProcessError as e:
                print(f"ERROR: Fallo al ejecutar con sudo (código: {e.returncode}). Puede requerir contraseña.", file=sys.stderr)
                sys.exit(e.returncode)
            except FileNotFoundError:
                print("ERROR: Comando 'sudo' no encontrado.", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"ERROR: Error inesperado al intentar ejecutar con sudo: {e}", file=sys.stderr)
                sys.exit(1)
        # Si ya tiene elevación (root), continuamos...
    else:
        # Sistema no compatible (ya se debería haber detectado antes, pero por si acaso)
        if needs_elevation:
            print_error(f"Sistema operativo '{system}' no compatible para operaciones que requieren elevación.", exit_code=1)

    # --- Execution from here assumes ELEVATED privileges (Root or Administrator) ---

    # --- 4. Setup Logging & Prerequisites (Now with elevation) ---
    setup_logging() # Configure logging properly now we have permissions
    log.info(f"Iniciando {APP_NAME} v{APP_VERSION} (con privilegios)")
    log.debug(f"Argumentos: {sys.argv}")
    if system in ["Linux", "Darwin"]:
        log.debug(f"Ejecutando como UID: {os.geteuid()}")
    elif system == "Windows":
        log.debug("Ejecutando con privilegios de Administrador")

    if not check_prerequisites_common():
        print_error("Verificación de requisitos falló.", exit_code=1)

    try:
        # --- 5. Load GPG Key (If Installing, and not on Windows) ---
        # Windows installer (.exe) is typically signed, GPG key less relevant for it
        gpg_key_loaded = False
        if action_to_perform == "install" and system != "Windows":
            if not load_signature_key():
                sys.exit(1)
            gpg_key_loaded = True

        # --- 6. Perform Action ---
        success = True
        if action_to_perform == "install":
            log.info("Cliente no instalado. Procediendo con la instalación...")
            # Pass gpg_key=None for Windows, required for others
            gpg_key_arg = PRITUNL_SIGN if system != "Windows" else None
            if gpg_key_arg is None and system != "Windows":
                 print_error("Error interno: clave GPG no cargada para la instalación.", exit_code=1)

            # Llamar a la función correcta (con o sin gpg_key)
            if system != "Windows":
                 if not install_client_os(os_info, gpg_key_arg): success = False
            else:
                 if not install_client_os(os_info, None): success = False # Pasar None para Windows

        elif action_to_perform == "remove":
            log.info("Cliente instalado. Procediendo con la desinstalación...")
            if not uninstall_client_os(os_info):
                success = False

        # --- 7. Final Exit ---
        if success:
            log.info("Script finalizado exitosamente.")
            sys.exit(0)
        else:
            log.error("Script finalizado con errores.")
            sys.exit(1)

    except Exception as e:
        # Catch any unexpected errors during the root execution phase
        log.exception("Ocurrió un error inesperado durante la ejecución principal:")
        print_error(f"Error inesperado: {e}", exit_code=1)


if __name__ == "__main__":
    main()
