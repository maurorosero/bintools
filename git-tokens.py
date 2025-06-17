#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script CLI para gestionar tokens de autenticación de servicios Git
(GitHub, GitLab, Forgejo, Gitea, Bitbucket Cloud y Bitbucket on-premise)
usando keyring de forma multiplataforma.

Copyright (C) 2025 MAURO ROSERO PÉREZ
License: GPLV3

File: git-tokens.py
Version: 1.1.0
Author: Mauro Rosero P. <mauro.rosero@gmail.com>
Assistant: Cursor AI (https://cursor.com)
Created: 2025-05-24 13:11:33
Last modified: 2025-05-24 13:11:33

This file is managed by template_manager.py.
Any changes to this header will be overwritten on the next fix.
"""

# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

# --- Importaciones ---
import sys
import argparse
import re
import os
import subprocess
import base64
import signal

# --- Instalar keyring si no está disponible ---
try:
    import keyring  # type: ignore
except ImportError:
    print("[ERROR] La librería 'keyring' es requerida pero no está instalada.")
    print("Instalando keyring...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "keyring"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("keyring instalado exitosamente.")
        print("Por favor, vuelve a ejecutar el script para continuar.")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudo instalar keyring: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error inesperado al instalar keyring: {e!s}")
        sys.exit(1)

GIT_SERVICES = ["github", "gitlab", "forgejo", "gitea", "bitbucket"]
SERVICE_LABELS = {
    "github": "GitHub",
    "gitlab": "GitLab",
    "forgejo": "Forgejo",
    "gitea": "Gitea",
    "bitbucket": "Bitbucket"
}
MODE_LABELS = {
    "c": "Cloud",
    "o": "On Premise"
}
# Restricciones por servicio
ONLY_CLOUD = ["github"]
ONLY_ONPREM = ["gitea"]

def handle_signal(signum, frame):
    """Maneja las señales de interrupción de forma elegante."""
    signal_names = {
        signal.SIGINT: "SIGINT (Ctrl+C)",
        signal.SIGTERM: "SIGTERM"
    }
    signal_name = signal_names.get(signum, f"Señal {signum}")
    print(f"\n\n🛑 Operación cancelada por el usuario ({signal_name})")
    print("📝 No se realizaron cambios en el keyring.")
    sys.exit(0)

def setup_signal_handlers():
    """Configura los manejadores de señales para salidas elegantes."""
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

def get_system_user() -> str:
    """Obtiene el usuario del sistema operativo (prioridad única)."""
    return (
        os.getenv('USER') or
        os.getenv('USERNAME') or
        os.getenv('LOGNAME') or
        'default'
    )

# --- Interactivo con Rich ---
def interactive_prompt(command):
    try:
        from rich.console import Console
        from rich.prompt import Prompt, IntPrompt
        from rich.table import Table
    except ImportError:
        print("[ERROR] El modo interactivo requiere la librería 'rich'. Instálala con: pip install rich")
        sys.exit(1)

    try:
        console = Console()
        # Elegir servicio
        table = Table(title="Servicios Git soportados", show_lines=True)
        table.add_column("N°", style="cyan", justify="right")
        table.add_column("Servicio", style="bold")
        table.add_column("Modos válidos", style="magenta")
        table.add_column("Ejemplo de uso", style="green")
        for idx, svc in enumerate(GIT_SERVICES, 1):
            if svc in ONLY_CLOUD:
                modos = "c (cloud)"
                ejemplo = f"{svc}-personal"
            elif svc in ONLY_ONPREM:
                modos = "o (onpremise)"
                ejemplo = f"{svc}-personal"
            else:
                modos = "c (cloud), o (onpremise)"
                ejemplo = f"{svc}-c-personal"
            table.add_row(str(idx), SERVICE_LABELS[svc], modos, ejemplo)
        console.print(table)
        svc_idx = IntPrompt.ask("Selecciona el servicio (número)", choices=[str(i) for i in range(1, len(GIT_SERVICES)+1)])
        service = GIT_SERVICES[int(svc_idx)-1]
        # Elegir modo
        if service in ONLY_CLOUD:
            mode = "c"
        elif service in ONLY_ONPREM:
            mode = "o"
        else:
            mode = Prompt.ask("Modo", choices=["c", "o"], default="c")
        # Uso
        usage = Prompt.ask("Identificador de uso (ej: personal, work, empresaX)", default="personal")
        # Usuario
        username = Prompt.ask("Usuario o identificador para el servicio", default=get_system_user())
        # Token (solo para set)
        token = None
        if command == "set":
            from getpass import getpass
            token = getpass("Introduce el token de acceso: ")
        service_name = f"{service}-{mode}-{usage}"
        return service_name, username, token
    except KeyboardInterrupt:
        print(f"\n\n🛑 Operación cancelada por el usuario")
        print("📝 No se realizaron cambios en el keyring.")
        sys.exit(0)
    except EOFError:
        print(f"\n\n🛑 Entrada terminada inesperadamente")
        print("📝 No se realizaron cambios en el keyring.")
        sys.exit(0)

def parse_service_name(service_name):
    parts = service_name.split("-")
    if len(parts) == 3:
        service, mode, usage = parts
    elif len(parts) == 2:
        service, usage = parts
        if service in ONLY_CLOUD:
            mode = "c"
        elif service in ONLY_ONPREM:
            mode = "o"
        else:
            print(f"Error: Debes especificar el modo (c/o) para el servicio '{service}'. Ejemplo: gitlab-c-personal")
            sys.exit(1)
    else:
        print("Error: El formato del nombre de servicio debe ser '[service]-[modo]-[uso]' o '[service]-[uso]'.")
        sys.exit(1)
    if service not in GIT_SERVICES:
        print(f"Error: Servicio '{service}' no soportado. Usa 'list-services' para ver los válidos.")
        sys.exit(1)
    if service in ONLY_CLOUD and mode != "c":
        print(f"Error: {SERVICE_LABELS[service]} solo permite modo 'c' (cloud). Ejemplo: github-personal")
        sys.exit(1)
    if service in ONLY_ONPREM and mode != "o":
        print(f"Error: {SERVICE_LABELS[service]} solo permite modo 'o' (onpremise). Ejemplo: gitea-personal")
        sys.exit(1)
    if mode not in ("c", "o"):
        print("Error: El modo debe ser 'c' (cloud) u 'o' (onpremise).")
        sys.exit(1)
    return service, mode, usage

def build_service_name(service, mode, usage, encrypt_method):
    if encrypt_method == "b64":
        return f"{service}-{mode}-{usage}"
    else:
        return f"{service}-{mode}-{usage}-{encrypt_method}"

def prompt_token():
    import getpass
    try:
        return getpass.getpass("Introduce el token de acceso: ")
    except KeyboardInterrupt:
        print(f"\n\n🛑 Operación cancelada por el usuario")
        print("📝 No se realizaron cambios en el keyring.")
        sys.exit(0)
    except EOFError:
        print(f"\n\n🛑 Entrada terminada inesperadamente")
        print("📝 No se realizaron cambios en el keyring.")
        sys.exit(0)

def encrypt_token(token, method="b64"):
    if method == "b64":
        return base64.b64encode(token.encode("utf-8")).decode("utf-8")
    else:
        print(f"[ERROR] Método de encriptación '{method}' no soportado.")
        sys.exit(1)

def decrypt_token(token_enc, method="b64"):
    if method == "b64":
        try:
            return base64.b64decode(token_enc.encode("utf-8")).decode("utf-8")
        except Exception:
            return token_enc  # Para compatibilidad con tokens antiguos no codificados
    else:
        print(f"[ERROR] Método de desencriptación '{method}' no soportado.")
        sys.exit(1)

def set_token(service_name, username, token=None, method="b64"):
    service, mode, usage = parse_service_name(service_name)
    if token is None:
        token = prompt_token()
    token_enc = encrypt_token(token, method)
    keyring.set_password(build_service_name(service, mode, usage, method), username, token_enc)
    print(f"✓ Token guardado para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}] (método: {method})")

def get_token(service_name, username, method="b64"):
    service, mode, usage = parse_service_name(service_name)
    token_enc = keyring.get_password(build_service_name(service, mode, usage, method), username)
    if token_enc:
        token = decrypt_token(token_enc, method)
        print(f"Token para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}]:\n{token}")
    else:
        print(f"No se encontró token para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}]")

def delete_token(service_name, username):
    service, mode, usage = parse_service_name(service_name)
    try:
        keyring.delete_password(build_service_name(service, mode, usage, "b64"), username)
        print(f"✓ Token eliminado para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}]")
    except keyring.errors.PasswordDeleteError:
        print(f"No se encontró token para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}]")

def list_services():
    print("Servicios soportados y formatos válidos:")
    print("  github: solo modo 'c' (cloud). Ejemplo: github-c-personal o github-personal")
    print("  gitea: solo modo 'o' (onpremise). Ejemplo: gitea-o-personal o gitea-personal")
    print("  gitlab, forgejo, bitbucket: ambos modos 'c' (cloud) y 'o' (onpremise). Ejemplo: gitlab-c-work, forgejo-o-empresaX")
    print("  El campo 'uso' es un identificador libre, por ejemplo: personal, work, empresaX, etc.")
    print("Ejemplo de nombre de servicio generado: gitlab-c-personal")

def print_version():
    """Imprime la versión, autor y fecha de última modificación extraídos del header del archivo."""
    version = "0.0.0"
    author = None
    last_modified = None
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                elif line.strip().startswith("Author:"):
                    author = line.split(":", 1)[1].strip()
                elif line.strip().startswith("Last modified:"):
                    last_modified = line.split(":", 1)[1].strip()
                if line.strip().startswith("# HEADER_END_TAG"):
                    break
    except Exception:
        pass
    print(f"git-tokens.py versión {version}")
    if author:
        print(f"Autor: {author}")
    if last_modified:
        print(f"Última modificación: {last_modified}")

def get_header_metadata():
    version = "0.0.0"
    author = None
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                elif line.strip().startswith("Author:"):
                    author = line.split(":", 1)[1].strip()
                if line.strip().startswith("# HEADER_END_TAG"):
                    break
    except Exception:
        pass
    return version, author

def command_set(args):
    method = "b64" if getattr(args, "b64", True) else None
    if not args.service_name:
        service_name, username, token = interactive_prompt("set")
    else:
        service_name = args.service_name
        username = args.username or get_system_user()  # Usuario del SO por defecto
        token = args.token
    service, mode, usage = parse_service_name(service_name)
    if token is None:
        token = prompt_token()
    token_enc = encrypt_token(token, method)
    keyring.set_password(build_service_name(service, mode, usage, method), username, token_enc)
    print(f"✓ Token guardado para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}] (método: {method})")

def command_get(args):
    method = "b64" if getattr(args, "b64", True) else None
    if not args.service_name:
        service_name, username, _ = interactive_prompt("get")
    else:
        service_name = args.service_name
        username = args.username or get_system_user()  # Usuario del SO por defecto
    service, mode, usage = parse_service_name(service_name)
    token_enc = keyring.get_password(build_service_name(service, mode, usage, method), username)
    if token_enc:
        token = decrypt_token(token_enc, method)
        print(f"Token para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}]:\n{token}")
    else:
        print(f"No se encontró token para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}]")

def command_delete(args):
    method = "b64" if getattr(args, "b64", True) else None
    if not args.service_name:
        service_name, username, _ = interactive_prompt("delete")
    else:
        service_name = args.service_name
        username = args.username or get_system_user()  # Usuario del SO por defecto
    service, mode, usage = parse_service_name(service_name)
    try:
        keyring.delete_password(build_service_name(service, mode, usage, method), username)
        print(f"✓ Token eliminado para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}] (método: {method})")
    except keyring.errors.PasswordDeleteError:
        print(f"No se encontró token para {SERVICE_LABELS[service]} {MODE_LABELS[mode]} ({usage}) [{username}]")

def command_list_services(args=None):
    print("Servicios soportados y formatos válidos:")
    print("  github: solo modo 'c' (cloud). Ejemplo: github-c-personal o github-personal")
    print("  gitea: solo modo 'o' (onpremise). Ejemplo: gitea-o-personal o gitea-personal")
    print("  gitlab, forgejo, bitbucket: ambos modos 'c' (cloud) y 'o' (onpremise). Ejemplo: gitlab-c-work, forgejo-o-empresaX")
    print("  El campo 'uso' es un identificador libre, por ejemplo: personal, work, empresaX, etc.")
    print("Ejemplo de nombre de servicio generado: gitlab-c-personal")
    print("\nEjemplo de uso con base64 (por defecto):")
    print("  git-tokens.py set github-personal              # Usuario del SO automático")
    print("  git-tokens.py set github-personal otrouser     # Usuario específico")
    print("  git-tokens.py get github-personal              # Usuario del SO automático")
    print("  git-tokens.py get github-personal otrouser     # Usuario específico")

def main():
    # Configurar manejadores de señales para salidas elegantes
    setup_signal_handlers()

    try:
        version, author = get_header_metadata()
        epilog = "\n\nEjemplo de uso con base64 (por defecto):\n  git-tokens.py set github-personal              # Usuario del SO automático\n  git-tokens.py set github-personal otrouser     # Usuario específico\n  git-tokens.py get github-personal              # Usuario del SO automático"
        parser = argparse.ArgumentParser(
            description="Gestor de tokens de autenticación para servicios Git usando keyring.",
            add_help=False,
            epilog=epilog
        )
        parser.add_argument(
            "-h", "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Muestra este mensaje de ayuda y sale"
        )
        parser.add_argument("-v", "--version", action="store_true", help="Mostrar la versión del script y salir")

        # Grupos personalizados en español
        pos_group = parser.add_argument_group("argumentos posicionales")
        opt_group = parser.add_argument_group("argumentos opcionales")

        subparsers = parser.add_subparsers(dest="command", required=False, title="subcomandos", description="Acciones disponibles")

        # set
        parser_set = subparsers.add_parser("set", help="Guardar o actualizar un token", add_help=False)
        set_pos_group = parser_set.add_argument_group("argumentos posicionales")
        set_opt_group = parser_set.add_argument_group("argumentos opcionales")
        set_pos_group.add_argument("service_name", nargs="?", help="Nombre de servicio en formato '[service]-[modo]-[uso]' o '[service]-[uso]'")
        set_pos_group.add_argument("username", nargs="?", help="Usuario o identificador para el servicio (opcional, default: usuario del SO)")
        set_opt_group.add_argument("--token", help="Token de acceso (si no se especifica, se pedirá por consola)")
        set_opt_group.add_argument("--b64", action="store_true", default=True, help="Encriptar el token usando base64 (por defecto)")
        parser_set.add_argument(
            "-h", "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Muestra este mensaje de ayuda y sale"
        )

        # get
        parser_get = subparsers.add_parser("get", help="Obtener un token guardado", add_help=False)
        get_pos_group = parser_get.add_argument_group("argumentos posicionales")
        get_pos_group.add_argument("service_name", nargs="?", help="Nombre de servicio en formato '[service]-[modo]-[uso]' o '[service]-[uso]'")
        get_pos_group.add_argument("username", nargs="?", help="Usuario o identificador para el servicio (opcional, default: usuario del SO)")
        get_pos_group.add_argument("--b64", action="store_true", default=True, help="Desencriptar el token usando base64 (por defecto)")
        parser_get.add_argument(
            "-h", "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Muestra este mensaje de ayuda y sale"
        )

        # delete
        parser_delete = subparsers.add_parser("delete", help="Eliminar un token guardado", add_help=False)
        del_pos_group = parser_delete.add_argument_group("argumentos posicionales")
        del_pos_group.add_argument("service_name", nargs="?", help="Nombre de servicio en formato '[service]-[modo]-[uso]' o '[service]-[uso]'")
        del_pos_group.add_argument("username", nargs="?", help="Usuario o identificador para el servicio (opcional, default: usuario del SO)")
        parser_delete.add_argument(
            "-h", "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Muestra este mensaje de ayuda y sale"
        )

        # list
        parser_list = subparsers.add_parser("list-services", help="Listar los servicios soportados y estructura de nombre", add_help=False)
        parser_list.add_argument(
            "-h", "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Muestra este mensaje de ayuda y sale"
        )

        args = parser.parse_args()

        if args.version:
            print_version()
            sys.exit(0)

        if not args.command:
            parser.print_help()
            sys.exit(0)

        if args.command == "set":
            command_set(args)
        elif args.command == "get":
            command_get(args)
        elif args.command == "delete":
            command_delete(args)
        elif args.command == "list-services":
            command_list_services(args)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print(f"\n\n🛑 Operación cancelada por el usuario")
        print("📝 No se realizaron cambios en el keyring.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        print("📝 Verifica los parámetros y vuelve a intentarlo.")
        sys.exit(1)

if __name__ == "__main__":
    main()
