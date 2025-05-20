#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GIT TOKENS - Este script gestiona de forma segura los tokens de servidor Git usando SOPS.

Copyright (C) 2025 MAURO ROSERO PÉREZ
License: GPLv3

File: git-tokens.py
Version: 0.1.0
Author: Mauro Rosero P. <mauro.rosero@gmail.com>
Assistant: Cursor AI (https://cursor.com)
Created: 2025-05-19 20:56:28

This file is managed by template_manager.py.
Any changes to this header will be overwritten on the next fix.
"""

# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

# Description: Este script gestiona de forma segura los tokens de servidor Git usando SOPS.

import os
import subprocess
import shutil
import tempfile
import base64
import getpass
import pathlib
import sys
import argparse
import re

# ==============================================
# Constantes y Configuración
# ==============================================

AUTHOR = "Mauro Rosero Pérez <mauro@rosero.one>"
APPS_FUNCTION = "GESTOR DE TOKENS GIT"

# Rutas
SCRIPT_PATH = pathlib.Path(__file__).resolve()  # Ruta completa al archivo git-tokens.py
HOME_DIR = pathlib.Path.home()
WORK_DIR = pathlib.Path.cwd()
SCRIPT_DIR = SCRIPT_PATH.parent                 # Directorio que contiene git-tokens.py (e.g., /home/mrosero/bin)
ROOT_DIR = SCRIPT_DIR.parent                    # Directorio raíz del proyecto (e.g., /home/mrosero)

# Estructura de directorios y archivos (similar al script Bash original)
LOG_DIR = HOME_DIR / ".logs"                    # Logs en el home del usuario (decisión de diseño actual)
DEFS_DIR = SCRIPT_DIR / "config"                # Plantillas y definiciones por defecto
CONF_DIR = HOME_DIR / ".sops"                   # Archivos de configuración (plural como en original)
SOPS_DIR = SCRIPT_DIR / "sops"
TOKENS_DEFAULT_DIR = CONF_DIR                   # Ubicación por defecto para tokens si devspath.def no existe

TOKEN_FILENAME_FORMAT = "token_%s.git.sops.yaml"

# Archivos de definición (en DEFS_DIR)
GITSERVER_DEFS_FILE = DEFS_DIR / "gitservers.def"
DEVS_PATH_FILE = SOPS_DIR / "devspath.def"          # Define dónde se guardan los tokens
GIT_TOKEN_FILE_TEMPLATE = DEFS_DIR / "token_git_sops.def"
SOPS_TEMPLATE_FILE = DEFS_DIR / "sops_rules.def"

# Archivos de configuración (en CONF_DIR o ROOT_DIR)
GITSERVER_CONF_FILE = SOPS_DIR / "gitservers.cfg"   # Se copia de GITSERVER_DEFS_FILE si no existe
SOPS_CONFIG_FILE = SCRIPT_DIR / ".sops.yaml"          # Reglas de encriptación SOPS

# Etiquetas para mensajes (se pueden ampliar si es necesario)
LABEL_INFO = "INFO"
LABEL_WARNING = "ADVERTENCIA"
LABEL_ERROR = "ERROR"
LABEL_SUCCESS = "ÉXITO"
LABEL_AFFIRMATIVE = "Sí"
LABEL_NEGATIVE = "No"
MSG_OPERATION_CANCELLED = "Operación cancelada por el usuario."

# Constantes para el banner
APP_NAME = "ADMINISTRADOR DE TOKENS PARA SRVIDORES GIT"
VERSION = "0.1.0"
BANNER_WIDTH = 70

# ==============================================
# Funciones Auxiliares de UI y Sistema
# ==============================================

def clear_screen():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    """Muestra el banner de la aplicación."""
    clear_screen()
    banner_lines = [
        "=" * BANNER_WIDTH,
        f"{APP_NAME} - Versión {VERSION}".center(BANNER_WIDTH),
        f"Autor: {AUTHOR}".center(BANNER_WIDTH),
        f"Función: {APPS_FUNCTION}".center(BANNER_WIDTH),
        "=" * BANNER_WIDTH,
    ]
    print("\n".join(banner_lines))
    print() # Línea vacía después del banner

def show_message(label, message, color_code=""):
    """Muestra un mensaje formateado."""
    if color_code:
        print(f"\033[{color_code}m{label}: {message}\033[0m")
    else:
        print(f"{label}: {message}")

def show_error(message):
    """Muestra un mensaje de error y termina el script."""
    show_message(f"✗ {LABEL_ERROR}", message, "1;31") # Rojo brillante
    sys.exit(1)

def show_success(message):
    """Muestra un mensaje de éxito."""
    show_message(f"✓ {LABEL_SUCCESS}", message, "1;32") # Verde brillante

def show_info(message):
    """Muestra un mensaje informativo."""
    show_message(f"ℹ {LABEL_INFO}", message, "1;34") # Azul brillante

def show_warning(message):
    """Muestra un mensaje de advertencia."""
    show_message(f"⚠ {LABEL_WARNING}", message, "1;33") # Amarillo brillante

def confirm_action(message):
    """Pide confirmación al usuario (Sí/No)."""
    while True:
        try:
            response = input(f"{message} ({LABEL_AFFIRMATIVE}/{LABEL_NEGATIVE}): ").strip().lower()
            if response in [LABEL_AFFIRMATIVE.lower(), 's', 'si', 'yes', 'y']:
                return True
            if response in [LABEL_NEGATIVE.lower(), 'n', 'no']:
                return False
            show_warning("Respuesta no válida. Por favor, ingrese 'Sí' o 'No'.")
        except KeyboardInterrupt:
            print() # Nueva línea tras Ctrl+C
            show_info(MSG_OPERATION_CANCELLED)
            sys.exit(0)

def run_command(command_list, capture_output=False, check=True, suppress_errors=False):
    """Ejecuta un comando del sistema."""
    try:
        process = subprocess.run(command_list, capture_output=capture_output, text=True, check=check)
        return process
    except subprocess.CalledProcessError as e:
        if not suppress_errors:
            show_error(f"Error ejecutando comando: {' '.join(command_list)}\n{e.stderr or e.stdout or str(e)}")
        raise # Re-lanza la excepción para que el llamador la maneje si es necesario
    except FileNotFoundError:
        show_error(f"Comando no encontrado: {command_list[0]}. Asegúrese de que esté instalado y en el PATH.")
        raise

# ==============================================
# Lógica Principal de la Aplicación
# ==============================================

def check_dependencies():
    """Verifica la existencia de sops y gpg."""
    show_info("Verificando dependencias...")
    if not shutil.which("sops"):
        show_error("SOPS no está instalado o no se encuentra en el PATH. Visite: https://github.com/getsops/sops")
    if not shutil.which("gpg"):
        show_error("GPG no está instalado o no se encuentra en el PATH.")
    show_success("Dependencias encontradas (sops, gpg).")

def check_git_config():
    """Valida la configuración de user.name, user.email y user.signingkey en Git."""
    show_info("Verificando configuración de Git...")
    git_global_config_ok = False
    git_signing_key_ok = False
    has_config = False

    try:
        user_name_global = run_command(["git", "config", "--global", "--get", "user.name"], capture_output=True, check=False).stdout.strip()
        user_email_global = run_command(["git", "config", "--global", "--get", "user.email"], capture_output=True, check=False).stdout.strip()
        if user_name_global and user_email_global:
            git_global_config_ok = True
            has_config = True
    except Exception:
        pass # No fallar si git no está configurado

    try:
        user_name_local = run_command(["git", "config", "--local", "--get", "user.name"], capture_output=True, check=False).stdout.strip()
        user_email_local = run_command(["git", "config", "--local", "--get", "user.email"], capture_output=True, check=False).stdout.strip()
        if user_name_local and user_email_local:
            # No necesitamos marcar git_local_config_ok, la presencia es suficiente
            has_config = True
    except Exception:
        pass # No fallar si git no está configurado en un repo local

    try:
        signing_key = run_command(["git", "config", "--get", "user.signingkey"], capture_output=True, check=False).stdout.strip()
        if signing_key:
            git_signing_key_ok = True
    except Exception:
        pass

    if not has_config:
        show_warning("No se encontró configuración de Git (user.name, user.email). Por favor, configure Git antes de continuar.")
        show_info("Puede usar MR*Developer GPG Manager para configurar Git y GPG.")
        if confirm_action("¿Desea salir para configurar Git?"):
            sys.exit(0)
    elif not git_signing_key_ok:
        show_warning("No se encontró una clave de firma GPG (user.signingkey) en la configuración de Git.")
        show_info("Puede usar MR*Developer GPG Manager para configurar una clave de firma GPG.")
        if confirm_action("¿Desea salir para configurar una clave de firma GPG?"):
            sys.exit(0)
    else:
        show_success("Configuración de Git y clave de firma GPG verificadas.")

def ensure_sops_config():
    """Asegura que el archivo .sops.yaml exista y esté configurado."""
    show_info("Verificando configuración de SOPS...")
    if SOPS_CONFIG_FILE.exists():
        show_success(f"Archivo de configuración SOPS encontrado en {SOPS_CONFIG_FILE}")
        return

    show_warning(f"Archivo de configuración SOPS ({SOPS_CONFIG_FILE}) no encontrado.")
    if not SOPS_TEMPLATE_FILE.exists():
        show_error(f"No se encontró la plantilla de configuración SOPS en {SOPS_TEMPLATE_FILE}")

    show_info("Intentando obtener huella digital GPG para la configuración de SOPS...")
    try:
        # Intenta obtener la clave de firma de Git primero
        git_signing_key = run_command(["git", "config", "--get", "user.signingkey"], capture_output=True, check=False).stdout.strip()
        
        gpg_fingerprint = ""
        if git_signing_key:
            # Obtener el fingerprint completo de la signing key
            # Comandos GPG pueden ser complejos, esto es una simplificación
            result = run_command(
                ["gpg", "--list-keys", "--with-colons", git_signing_key], 
                capture_output=True, 
                check=False,
                suppress_errors=True # Suprimir errores si la clave no existe o es un short ID
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith("fpr:::::::::"):
                        gpg_fingerprint = line.split(":")[9]
                        break
        
        if not gpg_fingerprint:
            # Si no hay signing key en git o no se pudo obtener fingerprint, buscar la primera clave secreta
            result = run_command(
                ["gpg", "--list-secret-keys", "--with-colons", "--fingerprint"],
                capture_output=True,
                check=True
            )
            for line in result.stdout.splitlines():
                if line.startswith("fpr:::::::::"): # Formato de fingerprint
                    gpg_fingerprint = line.split(":")[9]
                    break
        
        if not gpg_fingerprint:
            show_error("No se pudo encontrar una huella digital GPG adecuada. Asegúrese de tener una clave GPG y/o configúrela en Git (user.signingkey).")
            return

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        show_error(f"Error al obtener la huella GPG: {e}\nAsegúrese de que GPG esté instalado y configurado.")
        return
    except Exception as e: # Captura más genérica para errores inesperados
        show_error(f"Error inesperado al obtener la huella GPG: {e}")
        return

    show_info(f"Usando huella GPG: {gpg_fingerprint} para la configuración de SOPS.")
    
    try:
        template_content = SOPS_TEMPLATE_FILE.read_text(encoding='utf-8')
        sops_config_content = template_content.replace("${git_fingerprint}", gpg_fingerprint)
        SOPS_CONFIG_FILE.write_text(sops_config_content, encoding='utf-8')
        show_success(f"Archivo de configuración SOPS creado en {SOPS_CONFIG_FILE}")
    except IOError as e:
        show_error(f"No se pudo escribir el archivo de configuración SOPS en {SOPS_CONFIG_FILE}: {e}")
    except Exception as e:
        show_error(f"Error inesperado al crear {SOPS_CONFIG_FILE}: {e}")


def load_providers():
    """
    Carga los proveedores desde GITSERVER_CONF_FILE.
    Si no existe, lo copia desde GITSERVER_DEFS_FILE.
    Retorna una lista de diccionarios, cada uno representando un proveedor.
    """
    show_info("Cargando proveedores Git...")
    if not GITSERVER_DEFS_FILE.exists():
        show_error(f"Archivo de definiciones de servidores Git no encontrado: {GITSERVER_DEFS_FILE}")

    if not CONF_DIR.exists():
        try:
            CONF_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            show_error(f"No se pudo crear el directorio de configuración {CONF_DIR}: {e}")

    if not GITSERVER_CONF_FILE.exists():
        try:
            shutil.copy(GITSERVER_DEFS_FILE, GITSERVER_CONF_FILE)
            show_info(f"Archivo de configuración de proveedores copiado a {GITSERVER_CONF_FILE}")
        except IOError as e:
            show_error(f"No se pudo copiar el archivo de definiciones a {GITSERVER_CONF_FILE}: {e}")

    providers = []
    try:
        with open(GITSERVER_CONF_FILE, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = [part.strip('"') for part in line.split(',')]
                if len(parts) == 4:
                    providers.append({
                        "code": parts[0],
                        "desc": parts[1],
                        "type": parts[2], # e.g., github, gitlab, gitea
                        "mode": parts[3]  # 0 for standard, 1 for custom URL
                    })
                else:
                    show_warning(f"Línea {line_number} mal formada en {GITSERVER_CONF_FILE}: {line}")
    except IOError as e:
        show_error(f"No se pudo leer el archivo de configuración de proveedores {GITSERVER_CONF_FILE}: {e}")
    
    if not providers:
        show_error(f"No se encontraron proveedores Git en {GITSERVER_CONF_FILE}.")
    
    show_success(f"Cargados {len(providers)} proveedores Git.")
    return providers

def get_tokens_path():
    """
    Obtiene la ruta para guardar los tokens.
    Lee desde DEVS_PATH_FILE. Si no existe o es inválido, usa TOKENS_DEFAULT_DIR.
    Asegura que el directorio exista.
    """
    default_path = TOKENS_DEFAULT_DIR # Usar la nueva constante
    tokens_save_path = default_path

    if DEVS_PATH_FILE.exists(): # DEVS_PATH_FILE ahora usa DEFS_DIR
        try:
            path_from_config = DEVS_PATH_FILE.read_text(encoding='utf-8').strip()
            if path_from_config:
                # Expandir tilde (~)
                expanded_path = pathlib.Path(path_from_config).expanduser()
                tokens_save_path = expanded_path
        except IOError as e:
            show_warning(f"No se pudo leer {DEVS_PATH_FILE}, usando ruta por defecto: {e}")
        except Exception as e: # Captura más genérica
            show_warning(f"Error procesando {DEVS_PATH_FILE}, usando ruta por defecto: {e}")


    try:
        tokens_save_path.mkdir(parents=True, exist_ok=True)
        show_info(f"Los tokens se guardarán en: {tokens_save_path}")
        return tokens_save_path
    except OSError as e:
        show_warning(f"No se pudo crear o acceder a la ruta {tokens_save_path}: {e}. Usando ruta por defecto {default_path} si es posible.")
        try:
            default_path.mkdir(parents=True, exist_ok=True)
            show_info(f"Los tokens se guardarán en: {default_path}")
            return default_path
        except OSError as e_default:
             show_error(f"No se pudo crear o acceder a la ruta por defecto {default_path}: {e_default}")


def show_provider_menu(providers):
    """Muestra un menú numerado para seleccionar el proveedor, con opción de cancelar."""
    show_info("Seleccione el servicio Git para su token (o '0' para cancelar):") # Prompt modificado
    
    # Mostrar opciones, incluyendo "0. Cancelar"
    print("  0. Cancelar / Salir") # Opción de cancelación explícita
    for i, provider in enumerate(providers):
        print(f"  {i + 1}. {provider['code']} - {provider['desc']}")
    
    while True:
        try:
            choice = input("Seleccione una opción (número): ").strip()

            if not choice: # Si el usuario presiona Enter sin entrada
                if confirm_action("No ha ingresado nada. ¿Desea cancelar la selección?"):
                    show_info(MSG_OPERATION_CANCELLED)
                    sys.exit(0)
                else:
                    continue # Volver a pedir la opción
            
            if choice == "0": # Nueva opción de cancelación explícita
                show_info(MSG_OPERATION_CANCELLED)
                sys.exit(0)

            selected_index = int(choice) - 1 
            if 0 <= selected_index < len(providers):
                return providers[selected_index]
            else:
                show_warning("Selección fuera de rango. Intente de nuevo.")
        except ValueError:
            show_warning("Entrada no válida. Por favor, ingrese un número.")
        except KeyboardInterrupt:
            print() # Nueva línea tras Ctrl+C
            show_info(MSG_OPERATION_CANCELLED)
            sys.exit(0)

def get_token_input(provider_name, provider_code):
    """Solicita el token al usuario de forma segura."""
    show_info(f"Token para {provider_name} ({provider_code})")
    while True:
        try:
            token_str = getpass.getpass(prompt=f"Ingrese su token para {provider_code} (o Enter vacío para cancelar): ")
            if not token_str:
                if confirm_action("El token está vacío. ¿Desea cancelar la operación?"):
                    return None # Indica cancelación
                else:
                    continue # Volver a pedir

            if len(token_str) < 20: # Validación básica
                show_warning("El token parece ser demasiado corto.")
                if not confirm_action("¿Desea continuar de todos modos con este token?"):
                    continue
            return token_str
        except KeyboardInterrupt:
            print()
            return None # Indica cancelación

def get_server_url(provider_name, provider_code):
    """Pide la URL del servidor Git si es necesario."""
    show_info(f"Configuración de URL para {provider_name} ({provider_code})")
    while True:
        try:
            url_str = input(f"Indique la URL del servidor Git (ej: https://git.example.com): ").strip()
            if not url_str:
                if confirm_action("La URL está vacía. ¿Desea cancelar la operación?"):
                    return None # Indica cancelación
                else:
                    continue # Volver a pedir

            if not (url_str.startswith("http://") or url_str.startswith("https://")):
                show_warning("La URL debe comenzar con http:// o https://.")
                if confirm_action(f"¿Desea usar https://{url_str}?"):
                    url_str = f"https://{url_str}"
                else:
                    continue
            return url_str
        except KeyboardInterrupt:
            print()
            return None # Indica cancelación

def encrypt_token(provider_code, token_str, server_url_str, tokens_dir):
    """Prepara el YAML y lo encripta con SOPS."""
    show_info(f"Encriptando token para {provider_code}...")
    
    provider_code_lower = provider_code.lower()
    output_file = tokens_dir / (TOKEN_FILENAME_FORMAT % provider_code_lower)

    if not GIT_TOKEN_FILE_TEMPLATE.exists():
        show_error(f"No se encontró la plantilla para el token: {GIT_TOKEN_FILE_TEMPLATE}")
        return False

    try:
        template_content = GIT_TOKEN_FILE_TEMPLATE.read_text(encoding='utf-8')
        
        base64_provider_token = base64.b64encode(token_str.encode('utf-8')).decode('utf-8')
        
        yaml_server_url = server_url_str if server_url_str else "none" # YAML 'none'
        
        yaml_content = template_content.replace("base64_provider_token", base64_provider_token)
        yaml_content = yaml_content.replace("server_url", yaml_server_url)

        # Verificar reemplazos
        if "base64_provider_token" in yaml_content or ("server_url" in yaml_content and "server_url:" not in yaml_content.lower()):
             # La segunda condición es para evitar falsos positivos si la palabra "server_url" aparece en un comentario
             # o en un valor que no sea el placeholder específico que buscamos reemplazar.
             # Una mejor aproximación sería usar marcadores más únicos.
             show_error("Error al reemplazar los marcadores en la plantilla YAML. Verifique la plantilla y las variables.")
             return False


        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding='utf-8', suffix=".yaml") as tmp_yaml:
            tmp_yaml.write(yaml_content)
            temp_yaml_path = tmp_yaml.name
        
        try:
            run_command(["sops", "-e", temp_yaml_path], capture_output=True) # Prueba de encriptación
            # La salida de sops -e va a stdout, así que la leemos para guardarla
            encrypt_process = run_command(["sops", "-e", temp_yaml_path], capture_output=True)
            
            with open(output_file, 'wb') as f_out: # SOPS output es binario
                f_out.write(encrypt_process.stdout.encode('utf-8')) # stdout es texto, sops -e output es binario cifrado. Debe ser bytes.
                                                                    # Corrección: sops -e <file> > <output_file> es lo más seguro.
                                                                    # O leer como bytes directamente de stdout si es posible.

            # Mejor enfoque para SOPS encryption:
            with open(temp_yaml_path, 'r', encoding='utf-8') as f_in, open(output_file, 'wb') as f_out:
                encrypt_process_direct = subprocess.run(
                    ["sops", "--config", str(SOPS_CONFIG_FILE), "-e", "/dev/stdin"],
                    input=f_in.read().encode('utf-8'), 
                    stdout=f_out,             # Salida estándar al archivo f_out
                    stderr=subprocess.PIPE,   # Capturar stderr por separado
                    check=True                # check=True seguirá lanzando un error si sops falla
                )
                if encrypt_process_direct.stderr: # sops a veces manda info a stderr incluso en éxito
                    # Intentar decodificar stderr, puede ser binario en algunos casos
                    try:
                        sops_stderr_output = encrypt_process_direct.stderr.decode('utf-8', errors='ignore').strip()
                        if sops_stderr_output and "DEPRECATION" not in sops_stderr_output.upper() and "INFO" not in sops_stderr_output.upper():
                             show_warning(f"Salida de SOPS (stderr) durante encriptación:\n{sops_stderr_output}")
                    except Exception:
                        show_warning("SOPS produjo salida en stderr (posiblemente binaria) durante la encriptación.")


            os.chmod(output_file, 0o600)
            show_success(f"Token encriptado y guardado en: {output_file}")

            # Verificar el archivo recién encriptado
            if not verify_sops_encryption(output_file):
                show_error("La verificación post-encriptación falló. El archivo del token podría no ser utilizable o la configuración SOPS es incorrecta.")
                # Opcionalmente, se podría intentar eliminar el output_file aquí si se considera corrupto.
                # try:
                #     os.remove(output_file)
                #     show_info(f"Archivo corrupto {output_file} eliminado.")
                # except OSError as e_del:
                #     show_warning(f"No se pudo eliminar el archivo corrupto {output_file}: {e_del}")
                return False # Indicar fallo en encrypt_token
            
            return True # La encriptación y verificación fueron exitosas
        except subprocess.CalledProcessError as e:
            sops_error_output = e.stderr or e.stdout or "Error desconocido de SOPS."
            # Intentar decodificar el error si es bytes
            if isinstance(sops_error_output, bytes):
                sops_error_output = sops_error_output.decode('utf-8', errors='replace')
            show_error(f"Falló la encriptación del token con SOPS.\n{sops_error_output}")
            return False
        finally:
            os.remove(temp_yaml_path)
            
    except IOError as e:
        show_error(f"Error de E/S durante la preparación del token: {e}")
        return False
    except Exception as e:
        show_error(f"Error inesperado durante la encriptación del token: {e}")
        return False

def handle_remove_token(token_id_to_remove, tokens_dir):
    """Maneja la eliminación de un archivo de token SOPS."""
    if not token_id_to_remove:
        show_warning("No se especificó un ID de token para eliminar.")
        # Podríamos listar tokens aquí si quisiéramos
        return

    token_file_name = TOKEN_FILENAME_FORMAT % token_id_to_remove.lower()
    token_file_path = tokens_dir / token_file_name

    show_info(f"Intentando eliminar el token: {token_id_to_remove} (archivo: {token_file_path})")

    if token_file_path.exists():
        if confirm_action(f"¿Está seguro de que desea eliminar el archivo de token {token_file_path}?"):
            try:
                os.remove(token_file_path)
                show_success(f"Archivo de token {token_file_path} eliminado exitosamente.")
            except OSError as e:
                show_error(f"No se pudo eliminar el archivo de token {token_file_path}: {e}")
        else:
            show_info(MSG_OPERATION_CANCELLED)
    else:
        show_warning(f"El archivo de token {token_file_path} no existe.")
        # Listar archivos sops en tokens_dir para ayudar al usuario
        try:
            sops_files = list(tokens_dir.glob("token_*.sops.yaml"))
            if sops_files:
                show_info("Tokens existentes en el directorio:")
                for f in sops_files:
                    # Extraer el ID del nombre del archivo
                    match = re.search(r"token_(.+?)\.git\.sops\.yaml", f.name)
                    if match:
                        token_list_id = match.group(1)
                        print(f"  - {token_list_id} ({f.name})")
                    else:
                        print(f"  - {f.name} (ID no reconocido)")

            else:
                show_info(f"No se encontraron archivos de token en {tokens_dir}.")
        except Exception as e:
            show_warning(f"No se pudo listar los tokens existentes: {e}")

def verify_sops_encryption(file_path):
    """
    Verifica si el archivo SOPS recién creado se puede procesar (desencriptar)
    usando la configuración SOPS actual.
    """
    show_info(f"Verificando la integridad del archivo SOPS: {file_path}")
    try:
        verify_process = subprocess.run(
            ["sops", "--config", str(SOPS_CONFIG_FILE), "-d", str(file_path)],
            stdout=subprocess.DEVNULL, # No queremos ver el contenido desencriptado aquí
            stderr=subprocess.PIPE,
            check=True # Lanza excepción si sops falla
        )
        # Comprobar stderr incluso en caso de éxito, ya que SOPS puede emitir advertencias
        if verify_process.stderr:
            stderr_output = verify_process.stderr.decode('utf-8', errors='ignore').strip()
            if stderr_output and "DEPRECATION" not in stderr_output.upper() and "INFO" not in stderr_output.upper():
                 show_warning(f"Salida de SOPS (stderr) durante la verificación:\n{stderr_output}")
        show_success(f"Verificación del archivo SOPS {file_path} exitosa.")
        return True
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8', errors='replace').strip() if e.stderr else str(e)
        show_warning(f"Falló la verificación del archivo SOPS {file_path}.\n"
                     f"SOPS no pudo procesar el archivo con la configuración actual (¿clave GPG correcta en .sops.yaml y en el llavero?).\n"
                     f"Error de SOPS: {error_output}")
        return False
    except FileNotFoundError: # Si sops no se encuentra
        show_error("Comando 'sops' no encontrado durante la verificación. Asegúrese de que SOPS esté instalado y en el PATH.")
        return False
    except Exception as e_gen: # Otros errores inesperados
        show_warning(f"Ocurrió un error inesperado durante la verificación del archivo SOPS {file_path}: {e_gen}")
        return False

# ==============================================
# Función Main y Argumentos CLI
# ==============================================

def main():
    """Función principal del script."""

    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - {AUTHOR}",
        formatter_class=argparse.RawTextHelpFormatter # Para preservar saltos de línea en la ayuda
    )
    parser.add_argument(
        "--remove",
        metavar="TOKEN_ID",
        type=str,
        help="ID del token (ej: github, codeberg) a eliminar."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="Muestra la versión del script y sale."
    )
    # Podríamos añadir un argumento --list para listar tokens

    args = parser.parse_args()

    try:
        show_banner()
        check_dependencies()
        
        # La ruta de tokens se obtiene una vez, ya sea para añadir o eliminar
        tokens_path = get_tokens_path()

        if args.remove:
            handle_remove_token(args.remove, tokens_path)
            sys.exit(0)

        # Flujo normal de creación/actualización
        check_git_config()
        ensure_sops_config()
        
        providers = load_providers()
        if not providers: # load_providers ya muestra error, pero por si acaso
            sys.exit(1) 
            
        selected_provider = show_provider_menu(providers)
        if not selected_provider: # El usuario canceló
            sys.exit(0)

        provider_code = selected_provider["code"]
        provider_desc = selected_provider["desc"]
        provider_mode = selected_provider["mode"] # "0" o "1"

        # Verificar si el archivo de token ya existe
        provider_code_lower = provider_code.lower()
        sops_file_path = tokens_path / (TOKEN_FILENAME_FORMAT % provider_code_lower)
        if sops_file_path.exists():
            if not confirm_action(f"El archivo de token para '{provider_code}' ya existe en {sops_file_path}.\n¿Desea sobrescribirlo?"):
                show_info(MSG_OPERATION_CANCELLED)
                sys.exit(0)
        
        show_info(f"Proveedor seleccionado: {provider_code} - {provider_desc}")

        token_value = get_token_input(provider_desc, provider_code)
        if token_value is None: # Usuario canceló
            show_info(MSG_OPERATION_CANCELLED)
            sys.exit(0)
        
        server_url_value = None
        if provider_mode == "1": # Requiere URL personalizada
            server_url_value = get_server_url(provider_desc, provider_code)
            if server_url_value is None: # Usuario canceló
                show_info(MSG_OPERATION_CANCELLED)
                sys.exit(0)
            show_info(f"Servidor Git registrado: {server_url_value}")
        
        # Simular espera como en el script original
        # En Python, podríamos usar time.sleep(1) si quisiéramos,
        # pero la encriptación misma tomará algo de tiempo.
        # Por ahora, el mensaje "Encriptando token..." es suficiente.
        
        if encrypt_token(provider_code, token_value, server_url_value, tokens_path):
            # show_success ya se muestra dentro de encrypt_token
            pass
        else:
            # show_error ya se muestra dentro de encrypt_token
            sys.exit(1) # Asegurar salida con error

    except KeyboardInterrupt:
        print() # Nueva línea tras Ctrl+C
        show_info(f"\n{MSG_OPERATION_CANCELLED}")
        sys.exit(0)
    except Exception as e:
        show_error(f"Ocurrió un error inesperado: {e}")
        # Considerar traceback.format_exc() para depuración si es necesario
        sys.exit(1)

if __name__ == "__main__":
    main()
