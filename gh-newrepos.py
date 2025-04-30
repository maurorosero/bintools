# gh_repo_creator.py (final)

import os
import subprocess
import sys
import requests
import time
from github import Github, GithubObject # Import GithubObject for type hinting create_repo
from github.GithubException import UnknownObjectException, BadCredentialsException, GithubException, RateLimitExceededException

# Importar rich y questionary
from rich.console import Console
from rich.panel import Panel
import questionary

# --- Constantes ---
PROJECT_CONFIG_FILE = ".project"
DESCRIPTION_FILE = ".description"
GITHUB_TOKEN_ENV_VAR = "GITHUB_TOKEN"
GITHUB_API_URL = "https://api.github.com"
INTERNET_CHECK_URL = "https://www.google.com"
REQUEST_TIMEOUT = 15

# --- Consola Rich ---
console = Console(stderr=True) # Usar stderr para mensajes de estado/error

# --- Funciones Auxiliares --- (run_git_command usa console.print)

def run_git_command(command):
    """Ejecuta un comando git y retorna (stdout, stderr, returncode)."""
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=os.getcwd(),
            encoding='utf-8'
        )
        return process.stdout.strip(), process.stderr.strip(), process.returncode
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] El comando 'git' no se encontró. Asegúrate de que Git esté instalado y en tu PATH.")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Inesperado ejecutando git: {e}")
        sys.exit(1)

def print_error_and_exit(message, exit_code=1):
    """Imprime un mensaje de error estilizado y sale."""
    console.print(f"[bold red]Error:[/bold red] {message}")
    sys.exit(exit_code)

def print_success(message):
    """Imprime un mensaje de éxito estilizado."""
    console.print(f"[bold green]Éxito:[/bold green] {message}")

def print_info(message):
     """Imprime un mensaje informativo estilizado."""
     console.print(f"[blue]Info:[/blue] {message}")

def print_step(message):
    """Imprime un paso del proceso."""
    console.print(f"[cyan]-> {message}...[/cyan]")


# --- Verificaciones Iniciales --- (Usan print_step y console.print)

def check_git_repo():
    print_step("Verificando si es un repositorio Git")
    stdout, stderr, returncode = run_git_command(['git', 'rev-parse', '--is-inside-work-tree'])
    if returncode != 0 or stdout != 'true':
        print_error_and_exit("El directorio actual no parece ser un repositorio Git válido.")
    console.print("[green]   Repositorio Git válido.[/green]")

def get_git_root():
    print_step("Obteniendo la raíz del repositorio")
    stdout, stderr, returncode = run_git_command(['git', 'rev-parse', '--show-toplevel'])
    if returncode != 0:
        print_error_and_exit(f"No se pudo determinar la raíz del repositorio Git.\n[grey]{stderr}[/grey]")
    git_root = os.path.normpath(stdout)
    console.print(f"[green]   Raíz encontrada:[/green] {git_root}")
    return git_root

def check_remote_origin():
    print_step("Verificando remoto 'origin'")
    stdout, stderr, returncode = run_git_command(['git', 'remote', 'get-url', 'origin'])
    if returncode == 0:
        print_info(f"Ya existe un remoto 'origin' configurado ([bold]{stdout}[/bold]). El script no continuará.")
        sys.exit(0)
    elif returncode != 128 and returncode != 2:
         console.print(f"[yellow]Advertencia:[/yellow] Comando 'git remote get-url origin' falló (código: {returncode}). Asumiendo que no existe remoto.\n[grey]{stderr}[/grey]")
    console.print("[green]   Remoto 'origin' no encontrado.[/green]")

def check_internet_connection():
    print_step(f"Verificando conexión a internet ({INTERNET_CHECK_URL})")
    try:
        requests.get(INTERNET_CHECK_URL, timeout=REQUEST_TIMEOUT).raise_for_status()
        console.print("[green]   Conexión a internet activa.[/green]")
    except requests.exceptions.RequestException as e:
        print_error_and_exit(f"No se pudo establecer conexión a internet: {e}")

def check_github_status():
    print_step(f"Verificando estado de la API de GitHub ({GITHUB_API_URL})")
    try:
        response = requests.get(GITHUB_API_URL, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            console.print("[green]   API de GitHub accesible.[/green]")
        else:
            try: details = f" ({response.json().get('message', '')})"
            except: details = ""
            print_error_and_exit(f"La API de GitHub parece no estar disponible (Código: {response.status_code}){details}.")
    except requests.exceptions.RequestException as e:
        print_error_and_exit(f"Error verificando el estado de GitHub: {e}")


# --- Autenticación y Configuración --- (Usan print_step y console.print)

def get_github_token():
    print_step(f"Buscando token en variable de entorno '{GITHUB_TOKEN_ENV_VAR}'")
    token = os.getenv(GITHUB_TOKEN_ENV_VAR)
    if not token:
        print_error_and_exit(f"La variable de entorno '{GITHUB_TOKEN_ENV_VAR}' no está definida.")
    console.print("[green]   Token encontrado.[/green]")
    return token

def authenticate_github(token):
    print_step("Autenticando con GitHub")
    try:
        g = Github(token, timeout=REQUEST_TIMEOUT)
        user = g.get_user()
        console.print(f"[green]   Autenticación exitosa como:[/green] [bold]{user.login}[/bold]")
        return g, user
    except BadCredentialsException: print_error_and_exit("Token de GitHub inválido o expirado.")
    except RateLimitExceededException as e: print_error_and_exit(f"Límite de tasa de API de GitHub excedido. Intenta de nuevo en {int(e.rate.reset - time.time())} segundos.")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout): print_error_and_exit("No se pudo conectar a GitHub durante la autenticación.")
    except GithubException as e: print_error_and_exit(f"Error de GitHub ({e.status}) durante autenticación: {e.data.get('message', '')}")
    except Exception as e: print_error_and_exit(f"Error inesperado durante autenticación: {e}")

def read_project_config(git_root):
    print_step(f"Leyendo configuración de '{PROJECT_CONFIG_FILE}'")
    project_file_path = os.path.join(git_root, PROJECT_CONFIG_FILE)
    org_name = None
    repo_name = None
    try:
        with open(project_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    project_spec = line
                    break
            else: print_error_and_exit(f"'{PROJECT_CONFIG_FILE}' está vacío o no contiene una especificación válida.")
    except FileNotFoundError: print_error_and_exit(f"No se encontró el archivo '{PROJECT_CONFIG_FILE}' en la raíz ({git_root}).")
    except Exception as e: print_error_and_exit(f"Error leyendo el archivo '{PROJECT_CONFIG_FILE}': {e}")

    if '/' in project_spec:
        parts = project_spec.split('/', 1)
        if len(parts) == 2 and parts[0] and parts[1]:
            org_name, repo_name = parts[0], parts[1]
            console.print(f"[green]   Configuración:[/green] Org=[bold]{org_name}[/bold], Repo=[bold]{repo_name}[/bold]")
        else: print_error_and_exit(f"Formato inválido en '{PROJECT_CONFIG_FILE}'. Se esperaba '[org]/[repo]', se encontró '{project_spec}'.")
    else:
        if project_spec:
            repo_name = project_spec
            console.print(f"[green]   Configuración:[/green] Repo=[bold]{repo_name}[/bold] (Propietario: usuario actual)")
        else: print_error_and_exit(f"Formato inválido en '{PROJECT_CONFIG_FILE}'. Línea inválida encontrada.")

    if any(c in repo_name for c in r' \/:*?"<>|') or (org_name and any(c in org_name for c in r' \/:*?"<>|')):
        print_error_and_exit(f"Nombre de repo u org contiene caracteres inválidos: '{project_spec}'")

    return org_name, repo_name

# --- Validación y Preparación --- (Usan print_step y console.print)

def validate_org_and_get_owner(g, authenticated_user, org_name_spec):
    if not org_name_spec:
        console.print(f"[green]   Propietario:[/green] Usuario autenticado ([bold]{authenticated_user.login}[/bold])")
        return authenticated_user

    print_step(f"Validando organización '{org_name_spec}' y permisos")
    try:
        org = g.get_organization(org_name_spec)
        console.print(f"[green]   Organización encontrada:[/green] [bold]{org.login}[/bold]")

        membership = org.get_membership(authenticated_user.login)
        if membership.role == 'admin':
            console.print(f"[green]   Permisos: [/green] Usuario '{authenticated_user.login}' tiene rol '[bold]admin[/bold]' en '{org_name_spec}'.")
            return org
        else:
            print_error_and_exit(f"El usuario '{authenticated_user.login}' no tiene permisos de 'admin' en la organización '{org_name_spec}' (rol actual: '{membership.role}').")

    except UnknownObjectException: print_error_and_exit(f"La organización '{org_name_spec}' no existe o no es accesible.")
    except RateLimitExceededException as e: print_error_and_exit(f"Límite de tasa de API excedido validando org. Intenta en {int(e.rate.reset - time.time())} seg.")
    except GithubException as e:
        if e.status == 404: print_error_and_exit(f"La organización '{org_name_spec}' no existe o no es accesible.")
        elif e.status == 403: print_error_and_exit(f"No se pudo verificar la membresía en '{org_name_spec}'. ¿Falta el scope 'read:org' o no eres miembro?")
        else: print_error_and_exit(f"Error de GitHub ({e.status}) validando org '{org_name_spec}': {e.data.get('message', '')}")
    except Exception as e: print_error_and_exit(f"Error inesperado validando organización: {e}")


def check_repo_does_not_exist(owner, repo_name_spec):
    owner_login = owner.login
    full_repo_name = f"{owner_login}/{repo_name_spec}"
    print_step(f"Verificando si el repositorio '{full_repo_name}' ya existe")
    try:
        owner.get_repo(repo_name_spec)
        print_info(f"El repositorio '{full_repo_name}' ya existe en GitHub. El script no continuará.")
        sys.exit(0)
    except UnknownObjectException:
        console.print(f"[green]   El repositorio '{full_repo_name}' no existe.[/green]")
    except RateLimitExceededException as e: print_error_and_exit(f"Límite de tasa de API excedido verificando repo. Intenta en {int(e.rate.reset - time.time())} seg.")
    except GithubException as e: print_error_and_exit(f"Error de GitHub ({e.status}) verificando repo '{full_repo_name}': {e.data.get('message', '')}")
    except Exception as e: print_error_and_exit(f"Error inesperado verificando repositorio: {e}")


def get_description(git_root):
    print_step(f"Buscando descripción en '{DESCRIPTION_FILE}'")
    description_file_path = os.path.join(git_root, DESCRIPTION_FILE)
    description = ""
    try:
        with open(description_file_path, 'r', encoding='utf-8') as f:
            description = f.read().strip()
        if description:
            console.print(f"[green]   Descripción encontrada.[/green]")
            # console.print(Panel(description, title="Descripción", border_style="dim")) # Opcional: mostrarla
        else:
            console.print(f"[yellow]   Archivo '{DESCRIPTION_FILE}' encontrado pero vacío. Se usará descripción vacía.[/yellow]")
    except FileNotFoundError:
        console.print(f"[yellow]   Archivo '{DESCRIPTION_FILE}' no encontrado. Se usará descripción vacía.[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Advertencia:[/yellow] No se pudo leer '{DESCRIPTION_FILE}': {e}. Se usará descripción vacía.")

    return description


# --- Interacción y Creación --- (NUEVO + Uso de Questionary)

def get_repo_visibility():
    """Pregunta al usuario la visibilidad deseada para el repositorio."""
    print_step("Seleccionando visibilidad del repositorio")
    visibility = questionary.select(
        "Elige la visibilidad para el nuevo repositorio:",
        choices=[
            questionary.Choice("🔒 Privado (Private)", "private"),
            questionary.Choice("🌍 Público (Public)", "public"),
        ],
        pointer="▶",
        use_shortcuts=True
    ).ask() # Usar ask() al final

    if visibility is None: # El usuario presionó Ctrl+C
        print_error_and_exit("Operación cancelada por el usuario.", 0) # Salida limpia

    console.print(f"[green]   Visibilidad seleccionada:[/green] [bold]{visibility.capitalize()}[/bold]")
    return visibility == "private" # Devuelve True si es privado, False si es público


def confirm_creation(owner_login, repo_name, is_private, description):
    """Muestra resumen y pide confirmación al usuario."""
    print_step("Confirmación final")
    summary = (
        f"Se creará el siguiente repositorio en GitHub:\n\n"
        f"  [bold]Nombre:[/bold]      {owner_login}/{repo_name}\n"
        f"  [bold]Visibilidad:[/bold] {'Privado' if is_private else 'Público'}\n"
        f"  [bold]Descripción:[/bold]   '{description}'" if description else "[italic] (sin descripción)"
    )
    console.print(Panel(summary, title="Resumen de Creación", border_style="blue", expand=False))

    confirm = questionary.confirm(
        "¿Proceder con la creación?",
        default=False, # Requerir confirmación explícita
        auto_enter=False
    ).ask()

    if not confirm:
        print_info("Creación cancelada por el usuario.")
        sys.exit(0)

    return confirm


def create_github_repo(owner: GithubObject, repo_name: str, description: str, is_private: bool):
    """Crea el repositorio en GitHub."""
    owner_login = owner.login
    full_repo_name = f"{owner_login}/{repo_name}"
    print_step(f"Creando repositorio '{full_repo_name}' en GitHub")

    try:
        repo = owner.create_repo(
            name=repo_name,
            description=description,
            private=is_private,
            auto_init=False # No crear README, .gitignore etc. iniciales desde GitHub
        )
        print_success(f"Repositorio '{repo.full_name}' creado exitosamente.")
        print_info(f"URL del repositorio: {repo.html_url}")
        return repo
    except RateLimitExceededException as e: print_error_and_exit(f"Límite de tasa de API excedido creando repo. Intenta en {int(e.rate.reset - time.time())} seg.")
    except GithubException as e:
        # Errores comunes: 422 (Unprocessable Entity - ej: nombre inválido, ya existe aunque el check falló?)
        # 401/403 (problemas de permisos/autenticación que no se detectaron antes?)
         error_msg = e.data.get('message', '')
         errors = e.data.get('errors', [])
         details = f" ({error_msg})" if error_msg else ""
         if errors:
             details += " Detalles: " + "; ".join([f"{err.get('field', '')}: {err.get('message', '')}" for err in errors])

         print_error_and_exit(f"Error de GitHub ({e.status}) al crear repositorio '{full_repo_name}':{details}")
    except Exception as e:
         print_error_and_exit(f"Error inesperado al crear repositorio: {e}")


def add_git_remote(repo_ssh_url, git_root):
    """Añade el remoto 'origin' al repositorio local usando SSH."""
    print_step(f"Configurando remoto 'origin' localmente ({repo_ssh_url})")
    # Cambiar al directorio raíz de git para ejecutar el comando
    original_cwd = os.getcwd()
    try:
        os.chdir(git_root)
        stdout, stderr, returncode = run_git_command(['git', 'remote', 'add', 'origin', repo_ssh_url])
        if returncode == 0:
            print_success("Remoto 'origin' añadido exitosamente.")
        else:
            # Código 3 podría ser que ya existe (aunque lo chequeamos antes)
            # Código 128 podría ser otro error
            if "remote origin already exists" in stderr.lower():
                 print_info("El remoto 'origin' ya existía (inesperado). No se realizaron cambios.")
            else:
                 print_error_and_exit(f"No se pudo añadir el remoto 'origin'. Código: {returncode}\n[grey]{stderr}[/grey]")
    except Exception as e:
        print_error_and_exit(f"Error inesperado al configurar remoto: {e}")
    finally:
        os.chdir(original_cwd) # Volver al directorio original


# --- Main ---
def main():
    console.rule("[bold blue]GitHub Repo Creator[/bold blue]")

    check_git_repo()
    git_root = get_git_root()
    check_remote_origin()
    check_internet_connection()
    check_github_status()

    console.rule("[bold blue]Autenticación y Configuración[/bold blue]")
    github_token = get_github_token()
    g, authenticated_user = authenticate_github(github_token)
    org_name_spec, repo_name_spec = read_project_config(git_root)

    console.rule("[bold blue]Validación[/bold blue]")
    repo_owner = validate_org_and_get_owner(g, authenticated_user, org_name_spec)
    check_repo_does_not_exist(repo_owner, repo_name_spec)
    description = get_description(git_root)

    console.rule("[bold blue]Creación del Repositorio[/bold blue]")
    is_private = get_repo_visibility()

    if not confirm_creation(repo_owner.login, repo_name_spec, is_private, description):
        # Salida manejada dentro de confirm_creation si es False
        return

    new_repo = create_github_repo(repo_owner, repo_name_spec, description, is_private)

    console.rule("[bold blue]Configuración Local[/bold blue]")
    add_git_remote(new_repo.ssh_url, git_root)

    console.rule("[bold green]Proceso Completado[/bold green]")
    print_info("¡Todo listo! Ahora puedes hacer 'git push -u origin <branch>' para subir tu código.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt):
        print_error_and_exit("\nOperación interrumpida por el usuario.", 0) # Salida limpia en Ctrl+C
    except Exception as e:
        # Captura genérica por si algo no se manejó específicamente
        console.print_exception(show_locals=False) # Muestra traceback estilizado
        sys.exit(1) 