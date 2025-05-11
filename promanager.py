#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# promanager.py - Herramienta para gestionar metadatos de proyecto en un archivo TOML.
# -----------------------------------------------------------------------------
#
try:
    import tomllib
except ImportError:
    # Fallback para Python < 3.11
    try:
        import tomli as tomllib # pylint: disable=import-error
    except ImportError:
        print("Error: Se necesita la biblioteca 'tomli' para versiones de Python < 3.11.")
        print("Por favor, instálala con: pip install tomli")
        sys.exit(1)

import tomli_w
import questionary
from pathlib import Path
import sys
import os
import argparse
import base64
import subprocess
from typing import Optional, Dict, Any, Tuple, List
import fnmatch
import shutil # <--- AÑADIDO IMPORT

# --- Importaciones y Configuración de Colorama ---
try:
    from colorama import Fore, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Crear Clases Dummy si Colorama no está disponible
    class DummyColorama:
        def __getattr__(self, name):
            # Para Fore.GREEN, Style.RESET_ALL, etc., retorna una cadena vacía
            # de modo que la concatenación de cadenas no falle.
            return ""
    Fore = DummyColorama()
    Style = DummyColorama()
    # Back no se usa actualmente, pero podría añadirse aquí si fuera necesario.

if COLORAMA_AVAILABLE:
    colorama_init(autoreset=True) # Inicializar con autoreset

# --- Comprobación e Importaciones de PyGithub ---
PYGITHUB_INSTALLED_CORRECTLY = False
GITHUB_IMPORT_ERROR_MESSAGE = ""
NotSet = object() # Inicializar con un valor dummy default

try:
    # Importar MainClass primero para acceder a NotSet
    from github import MainClass
    NotSet = MainClass.NotSet # Definir NotSet globalmente

    # Luego importar el resto de los componentes necesarios de PyGithub
    from github import Github, GithubException, UnknownObjectException, BadCredentialsException
    # No necesitamos importar MainClass de nuevo aquí si solo se usó para NotSet globalmente.
    # Si GitHubConfigurator u otros necesitan MainClass explícitamente, se puede añadir aquí.
    
    PYGITHUB_INSTALLED_CORRECTLY = True

except ImportError as e_pygithub:
    # Captura si 'github' o alguno de sus componentes principales no se pueden importar
    GITHUB_IMPORT_ERROR_MESSAGE = f"Error importando PyGithub o sus componentes esenciales (ej. MainClass, Github): {e_pygithub}"
    PYGITHUB_INSTALLED_CORRECTLY = False
    # NotSet permanece como el objeto dummy
    pass
except AttributeError as e_attr:
    # Captura si MainClass existe pero MainClass.NotSet no (muy improbable si ImportError no saltó)
    GITHUB_IMPORT_ERROR_MESSAGE = f"PyGithub importado pero falta MainClass.NotSet: {e_attr}. Revisar la instalación de PyGithub."
    PYGITHUB_INSTALLED_CORRECTLY = False
    # NotSet permanece como el objeto dummy
    pass

# --- Constantes para Protección de Ramas ---
BRANCH_TYPES = {
    "feature": {
        "pattern": "feature/*",
        "description": "Nuevas características",
        "target_branch": "develop",
        "allow_direct_push": True
    },
    "fix": {
        "pattern": "fix/*",
        "description": "Correcciones de errores",
        "target_branch": "develop",
        "allow_direct_push": True
    },
    "hotfix": {
        "pattern": "hotfix/*",
        "description": "Correcciones urgentes",
        "target_branch": ["main", "develop"],
        "allow_direct_push": True
    },
    "docs": {
        "pattern": "docs/*",
        "description": "Documentación",
        "target_branch": "develop",
        "allow_direct_push": True
    },
    "refactor": {
        "pattern": "refactor/*",
        "description": "Refactorización",
        "target_branch": "develop",
        "allow_direct_push": True
    },
    "test": {
        "pattern": "test/*",
        "description": "Tests",
        "target_branch": "develop",
        "allow_direct_push": True
    },
    "chore": {
        "pattern": "chore/*",
        "description": "Mantenimiento",
        "target_branch": "develop",
        "allow_direct_push": True
    }
}

MAIN_BRANCHES = {
    "main": {
        "protection_level": "strict",
        "allow_direct_push": False, # Para no-admins
        "allowed_pr_from": ["hotfix/*", "staging", "develop"], 
        "enforce_admins": False # Admins exentos por defecto para main
    },
    "develop": {
        "protection_level": "strict",
        "allow_direct_push": False, # Para no-admins (y admins porque enforce_admins será True)
        "allowed_pr_from": ["feature/*", "fix/*", "docs/*", "refactor/*", "test/*", "chore/*"],
        "enforce_admins": True # Admins DEBEN seguir PRs para develop
    },
    "staging": {
        "protection_level": "strict",
        "allow_direct_push": False, # Para no-admins (y admins porque enforce_admins será True)
        "allowed_pr_from": ["develop"],
        "enforce_admins": True # Admins DEBEN seguir PRs para staging también
    }
}

class GitServerConfigurator:
    """Clase base para configurar servidores Git."""
    
    def __init__(self, project_data: Dict[str, Any], token: str):
        self.project_data = project_data
        self.token = token
        self.repo_data = project_data["repository"]
    
    def configure_branch_protection(self, branch: str, rules: Dict[str, Any]) -> Tuple[bool, str]:
        """Configura protección de rama."""
        raise NotImplementedError
    
    def configure_review_leadership(self, reviewers: List[str], branch_leaders: List[str]) -> Tuple[bool, str]:
        """Configura liderazgo de revisión."""
        raise NotImplementedError
    
    def validate_pull_request(self, source_branch: str, target_branch: str) -> Tuple[bool, str]:
        """Valida si un PR está permitido según las reglas."""
        if target_branch not in MAIN_BRANCHES:
            return False, f"Rama destino {target_branch} no existe"
        
        allowed_branches = MAIN_BRANCHES[target_branch]["allowed_pr_from"]
        
        for pattern in allowed_branches:
            if fnmatch.fnmatch(source_branch, pattern):
                return True, "PR permitido"
        
        return False, f"PR de {source_branch} a {target_branch} no está permitido"

class GitHubConfigurator(GitServerConfigurator):
    """Configurador específico para GitHub."""
    
    def __init__(self, project_data: Dict[str, Any], token: str):
        super().__init__(project_data, token)
        
        if not PYGITHUB_INSTALLED_CORRECTLY:
            # Lanzar un error o manejarlo de forma que la clase no se pueda usar si PyGithub no está.
            # Esto es un re-check por si la importación global falló silenciosamente (aunque el try-except arriba debería salir).
            raise ImportError("PyGithub no está instalado o no se pudo importar correctamente. Por favor, verifica la instalación.")

        try:
            # Decodificar el token si viene en base64
            try:
                decoded_token = base64.b64decode(token).decode('utf-8')
            except Exception:
                decoded_token = token  # Si no es base64, usar el token tal cual
            
            # Las clases de PyGithub ahora se usan directamente desde las importaciones de nivel de módulo
            
            self.github = Github(decoded_token)
            
            # Verificar si el repositorio existe
            owner = self.repo_data.get('owner_name', '')
            if not owner:  # Si no hay owner_name, usar el usuario autenticado
                owner = self.github.get_user().login
            
            repo_name = self.repo_data.get('name', '')
            if not repo_name:
                raise ValueError("No se especificó el nombre del repositorio")
            
            try:
                self.repo = self.github.get_repo(f"{owner}/{repo_name}")
            except GithubException as e: # Usar la clase importada directamente
                if e.status == 404:
                    raise ValueError(f"El repositorio {owner}/{repo_name} no existe en GitHub")
                raise
            
        except Exception as e:
            raise ValueError(f"Error inicializando GitHub: {str(e)}")
    
    def configure_branch_protection(self, branch_name: str, rules: Dict[str, Any]) -> Tuple[bool, str]:
        if not PYGITHUB_INSTALLED_CORRECTLY:
            return False, "Error crítico: PyGithub no está disponible para configurar la protección."
        try:
            branch_obj = None
            try:
                branch_obj = self.repo.get_branch(branch_name)
            except UnknownObjectException:
                if branch_name == "staging" and self.project_data.get("project_details", {}).get("project_type") != "solo":
                    print(f"{Fore.YELLOW}Advertencia: La rama de protección '{branch_name}' no existe en el repositorio remoto. Debería crearla primero para aplicar protecciones.{Style.RESET_ALL}")
                elif branch_name != "staging": # No advertir si staging no existe y es solo_dev
                    print(f"{Fore.YELLOW}Advertencia: La rama de protección '{branch_name}' no existe en el repositorio remoto. Se omitirá.{Style.RESET_ALL}")
                return False, f"Error: La rama '{branch_name}' no existe en el repositorio remoto. Se omitirá su protección."

            print(f"{Fore.CYAN}Configurando protecciones para la rama: {branch_name}{Style.RESET_ALL}")

            # --- Configuración General de Protección (edit_protection) ---
            enforce_admins_value = rules.get("enforce_admins", False) # False por defecto
            
            # Parámetros para edit_protection
            protection_args = {
                "enforce_admins": enforce_admins_value if isinstance(enforce_admins_value, bool) else NotSet,
                "required_linear_history": rules.get("required_linear_history", NotSet),
                "allow_force_pushes": rules.get("allow_force_pushes", NotSet),
                "allow_deletions": rules.get("allow_deletions", NotSet),
                "required_conversation_resolution": rules.get("required_conversation_resolution", NotSet),
                "lock_branch": rules.get("lock_branch", NotSet),
                "allow_fork_syncing": rules.get("allow_fork_syncing", NotSet),
            }
            # Restricciones de push para apps (si existen)
            app_restrictions = rules.get("restrictions", {}).get("apps", NotSet)
            if app_restrictions is not NotSet and app_restrictions: # Solo añadir si no es NotSet y no está vacío
                protection_args["app_push_restrictions"] = app_restrictions
            
            # Filtrar NotSet para no enviarlos si son el valor por defecto de PyGithub
            # (Aunque PyGithub debería manejarlos, es más limpio no enviarlos si no son necesarios)
            final_protection_args = {k: v for k, v in protection_args.items() if v is not NotSet}

            if final_protection_args: # Solo llamar si hay algo que configurar
                print(f"  Aplicando protecciones generales: {final_protection_args}")
                branch_obj.edit_protection(**final_protection_args)


            # --- Revisiones de Pull Request Requeridas ---
            pr_reviews_config = rules.get("required_pull_request_reviews", {})
            if pr_reviews_config: # Solo si hay configuración de PR reviews
                pr_args = {
                    "dismiss_stale_reviews": pr_reviews_config.get("dismiss_stale_reviews", NotSet),
                    "require_code_owner_reviews": pr_reviews_config.get("require_code_owner_reviews", NotSet),
                    "required_approving_review_count": pr_reviews_config.get("required_approving_review_count", NotSet),
                    "require_last_push_approval": pr_reviews_config.get("require_last_push_approval", NotSet),
                }
                dismissal_restrictions_config = pr_reviews_config.get("dismissal_restrictions", {})
                pr_args["dismissal_users"] = dismissal_restrictions_config.get("users", NotSet)
                pr_args["dismissal_teams"] = dismissal_restrictions_config.get("teams", NotSet)
                pr_args["dismissal_apps"] = dismissal_restrictions_config.get("apps", NotSet)
                
                final_pr_args = {k: v for k, v in pr_args.items() if v is not NotSet}
                if final_pr_args:
                    print(f"  Aplicando configuración de revisión de PRs: {final_pr_args}")
                    branch_obj.edit_required_pull_request_reviews(**final_pr_args)
                elif not branch_obj.get_protection().required_pull_request_reviews and not final_pr_args and pr_reviews_config:
                    # Si no hay config de PRs y la configuración está vacía pero existía, intentar removerla
                    try:
                        branch_obj.remove_required_pull_request_reviews()
                        print("  Removiendo configuración de revisión de PRs existente.")
                    except GithubException as e:
                        print(f"{Fore.YELLOW}  No se pudo remover la configuración de revisión de PRs: {e}{Style.RESET_ALL}")


            # --- Verificaciones de Estado Requeridas ---
            status_checks_config = rules.get("required_status_checks", {})
            should_process_status_checks = bool(status_checks_config)
            if not should_process_status_checks:
                try:
                    current_status_protection_obj = branch_obj.get_required_status_checks()
                    if current_status_protection_obj and (current_status_protection_obj.strict or current_status_protection_obj.contexts or (hasattr(current_status_protection_obj, 'checks') and current_status_protection_obj.checks)):
                        should_process_status_checks = True # Hay algo que remover
                except GithubException as e:
                    if e.status != 404: should_process_status_checks = True

            if should_process_status_checks:
                status_args = {
                    "strict": status_checks_config.get("strict", NotSet),
                }
                
                contexts_from_config = status_checks_config.get("contexts", []) # Lista de strings
                checks_in_config = status_checks_config.get("checks", [])     # Puede ser lista de strings o lista de dicts {"context": str, "app_id": int | None}

                # Listas para PyGithub
                pygithub_contexts_list = [] # Debe ser list[str]
                pygithub_checks_list = []   # Debe ser list[tuple[str, int]]

                # Procesar 'contexts_from_config' primero
                for item in contexts_from_config:
                    if isinstance(item, str) and item not in pygithub_contexts_list:
                        pygithub_contexts_list.append(item)

                # Procesar 'checks_in_config'
                for item in checks_in_config:
                    if isinstance(item, str):
                        # Si es un string, tratar como context si no está ya
                        if item not in pygithub_contexts_list:
                            pygithub_contexts_list.append(item)
                    elif isinstance(item, dict) and "context" in item:
                        context_name = item["context"]
                        app_id = item.get("app_id")
                        if app_id is not None:
                            # Si tiene app_id, va a pygithub_checks_list como tupla
                            if (context_name, app_id) not in pygithub_checks_list:
                                pygithub_checks_list.append((context_name, app_id))
                        else:
                            # Si no tiene app_id, tratar como context si no está ya
                            if context_name not in pygithub_contexts_list:
                                pygithub_contexts_list.append(context_name)
                
                if pygithub_contexts_list: # Solo añadir si no está vacía
                    status_args["contexts"] = pygithub_contexts_list
                
                if pygithub_checks_list: # Solo añadir si no está vacía
                    status_args["checks"] = pygithub_checks_list
                
                final_status_args = {k: v for k, v in status_args.items() if v is not NotSet}

                if final_status_args and (final_status_args.get("contexts") or final_status_args.get("checks")):
                    print(f"  Aplicando configuración de status checks: {final_status_args}")
                    branch_obj.edit_required_status_checks(**final_status_args)
                elif status_checks_config: # Si la config original no estaba vacía, pero no hay args finales válidos
                    try:
                        branch_obj.remove_required_status_checks()
                        print("  Removiendo configuración de status checks existente (configuración vacía/default provista).")
                    except GithubException as e:
                        if e.status != 404:
                            print(f"{Fore.YELLOW}  Advertencia: No se pudo remover la configuración de status checks: {e}. Puede que no existiera.{Style.RESET_ALL}")


            # --- Restricciones de Push (Usuarios y Equipos) ---
            restrictions_config = rules.get("restrictions", {})
            user_push_restrictions_from_config = restrictions_config.get("users", []) 
            team_push_restrictions_from_config = restrictions_config.get("teams", [])

            current_user_restrictions = []
            try:
                current_user_restrictions = [user.login for user in branch_obj.get_user_push_restrictions()]
            except GithubException as e:
                if e.status == 404: # Push restrictions not enabled
                    # Es normal si nunca se han configurado antes
                    print(f"  {Fore.BLUE}Info: No hay restricciones de push de usuario preexistentes para '{branch_name}'.{Style.RESET_ALL}")
                else:
                    # Si es otro error, relanzar para que se maneje más arriba o se muestre
                    print(f"  {Fore.YELLOW}Advertencia: Error inesperado al obtener restricciones de usuario: {e}{Style.RESET_ALL}")
                    # Continuar podría ser arriesgado, pero por ahora seguiremos el flujo anterior
                    # Considerar relanzar (raise) en futuras mejoras si este caso se vuelve problemático
                    pass 

            current_team_restrictions = []
            try:
                current_team_restrictions = [team.slug for team in branch_obj.get_team_push_restrictions()]
            except GithubException as e:
                if e.status == 404: # Push restrictions not enabled
                    print(f"  {Fore.BLUE}Info: No hay restricciones de push de equipo preexistentes para '{branch_name}'.{Style.RESET_ALL}")
                else:
                    print(f"  {Fore.YELLOW}Advertencia: Error inesperado al obtener restricciones de equipo: {e}{Style.RESET_ALL}")
                    pass

            # Lógica para reemplazar/remover basada en las listas _from_config y current_
            if user_push_restrictions_from_config:
                print(f"  Estableciendo restricciones de push para usuarios: {user_push_restrictions_from_config}")
                branch_obj.replace_user_push_restrictions(*user_push_restrictions_from_config)
            elif not user_push_restrictions_from_config and current_user_restrictions: 
                print(f"  Removiendo todas las restricciones de push para usuarios (configuración vacía y existían previas).")
                branch_obj.replace_user_push_restrictions() 
            # Si user_push_restrictions_from_config está vacío Y current_user_restrictions está vacío, no hacer nada.

            if team_push_restrictions_from_config:
                print(f"  Estableciendo restricciones de push para equipos: {team_push_restrictions_from_config}")
                branch_obj.replace_team_push_restrictions(*team_push_restrictions_from_config)
            elif not team_push_restrictions_from_config and current_team_restrictions: 
                print(f"  Removiendo todas las restricciones de push para equipos (configuración vacía y existían previas).")
                branch_obj.replace_team_push_restrictions() 
            # Si team_push_restrictions_from_config está vacío Y current_team_restrictions está vacío, no hacer nada.
            
            # --- Requerir Firmas de Commits ---
            require_signatures = rules.get("require_signed_commits", NotSet)
            if require_signatures is True:
                print("  Habilitando requerimiento de firmas de commits.")
                branch_obj.add_required_signatures()
            elif require_signatures is False: # Explícitamente False para remover
                print("  Deshabilitando requerimiento de firmas de commits.")
                branch_obj.remove_required_signatures()
            # Si es NotSet, no hacer nada (dejar como esté)

            return True, f"Protección configurada para rama '{branch_name}'"
            
        except GithubException as ge: # Usar la clase importada directamente
            if ge.status == 422 and isinstance(ge.data, dict) and "errors" in ge.data:
                error_messages = []
                for err in ge.data["errors"]:
                    message = f"Recurso: {err.get('resource')}, Campo: {err.get('field')}, Código: {err.get('code')}, Mensaje: {err.get('message')}"
                    error_messages.append(message)
                detailed_error = "; ".join(error_messages)
                return False, f"Error configurando protección para '{branch_name}' (422 Unprocessable Entity): {detailed_error}. Revise la configuración y permisos."
            return False, f"Error de GitHub API configurando protección para '{branch_name}': {str(ge)} (Status: {ge.status}, Data: {ge.data})"
        except Exception as e:
            return False, f"Error inesperado configurando protección para '{branch_name}': {str(e)}"
    
    def configure_review_leadership(self, reviewers: List[str], branch_leaders: List[str]) -> Tuple[bool, str]:
        if not PYGITHUB_INSTALLED_CORRECTLY:
            return False, "Error crítico: PyGithub no está disponible para configurar liderazgo."
        try:
            # Configurar revisores
            if reviewers:
                for reviewer in reviewers:
                    try:
                        self.repo.add_to_collaborators(reviewer, "push")
                    except GithubException as e: # Usar la clase importada directamente
                        if e.status == 404:
                            return False, f"Usuario o equipo {reviewer} no encontrado en GitHub"
                        raise
            
            # Configurar líderes de rama
            if branch_leaders:
                for leader in branch_leaders:
                    try:
                        self.repo.add_to_collaborators(leader, "admin")
                    except GithubException as e: # Usar la clase importada directamente
                        if e.status == 404:
                            return False, f"Usuario o equipo {leader} no encontrado en GitHub"
                        raise
            
            return True, "Liderazgo de revisión configurado"
        except Exception as e:
            return False, f"Error configurando liderazgo: {str(e)}"

def check_and_install_pygithub() -> bool:
    """Verifica si PyGithub está disponible; si no, intenta instalarlo/reinstalarlo."""
    global PYGITHUB_INSTALLED_CORRECTLY, GITHUB_IMPORT_ERROR_MESSAGE

    if PYGITHUB_INSTALLED_CORRECTLY: # Si ya se importó bien al inicio.
        return True

    # Si llegamos aquí, la importación inicial falló.
    questionary.print(f"Advertencia: No se pudo cargar PyGithub inicialmente (Error: {GITHUB_IMPORT_ERROR_MESSAGE}).", style="fg:yellow")
    
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        questionary.print("Error: No se detectó un entorno virtual Python activo.", style="fg:red")
        questionary.print("Para usar esta funcionalidad, necesitas crear y activar un entorno virtual y luego instalar PyGithub:", style="fg:yellow")
        questionary.print("  1. python -m venv .venv (o similar)", style="fg:yellow")
        questionary.print("  2. source .venv/bin/activate (Linux/macOS) o .venv\\Scripts\\activate (Windows)", style="fg:yellow")
        questionary.print("  3. pip install PyGithub", style="fg:yellow")
        return False
    
    confirm_install = questionary.confirm(
        "La biblioteca PyGithub es necesaria pero no está instalada o no se pudo cargar. ¿Intentar instalarla/reinstalarla ahora?"
    ).ask()

    if not confirm_install:
        questionary.print("Instalación/reinstalación de PyGithub omitida.", style="fg:yellow")
        # Mantener PYGITHUB_INSTALLED_CORRECTLY como False
        return False

    questionary.print("Instalando/Reinstalando PyGithub...", style="fg:cyan")
    try:
        # Usar --upgrade para asegurar que se reinstale o actualice si ya existe pero está corrupta.
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "PyGithub"], 
                     check=True, capture_output=True, text=True)
        
        # Reintentar la importación DESPUÉS de la instalación/actualización
        from github import MainClass # Importar MainClass directamente
        
        global NotSet # Indicar que estamos modificando la variable global NotSet
        NotSet = MainClass.NotSet # Reasignar desde el módulo recién importado/actualizado

        from github import Github, GithubException, UnknownObjectException, BadCredentialsException
        # No es necesario importar MainClass de nuevo aquí si GitHubConfigurator no la necesita directamente
        
        PYGITHUB_INSTALLED_CORRECTLY = True
        GITHUB_IMPORT_ERROR_MESSAGE = "" # Limpiar error previo porque la importación tuvo éxito
        questionary.print("PyGithub instalado/actualizado y cargado correctamente.", style="fg:green")
        return True
    except subprocess.CalledProcessError as e_install:
        questionary.print(f"Error al instalar/actualizar PyGithub: {e_install.stderr}", style="fg:red")
        PYGITHUB_INSTALLED_CORRECTLY = False 
        return False
    except ImportError as e_reimport:
        questionary.print(f"Error: PyGithub se instaló/actualizó pero no se pudo cargar ({e_reimport}). Intenta ejecutar el script de nuevo.", style="fg:red")
        PYGITHUB_INSTALLED_CORRECTLY = False 
        GITHUB_IMPORT_ERROR_MESSAGE = str(e_reimport) 
        return False
    except AttributeError as e_attr_re: # Capturar si MainClass.NotSet no existe tras la reinstalación
        questionary.print(f"Error: PyGithub se instaló/actualizó pero MainClass.NotSet sigue sin estar disponible. Revisa la versión de PyGithub: {e_attr_re}", style="fg:red")
        PYGITHUB_INSTALLED_CORRECTLY = False
        return False

# Dependencias para GitHub
# La lógica de check_and_install_pygithub() se ejecutará bajo demanda o al inicio
# if not check_and_install_pygithub():
#     # Decidir si salir o continuar con funcionalidad limitada.
#     # Por ahora, el script podría fallar más tarde si PYGITHUB_INSTALLED_CORRECTLY es False
#     # y se intenta usar una función que lo requiera (como GitHubConfigurator).
#     pass 


# --- Constantes para el Banner ---
APP_NAME = "Gestor de Poryectos de Desarrollo"  # Anteriormente APP_NAME_BANNER
VERSION = "0.1.0"  # Anteriormente SCRIPT_VERSION
AUTHOR = "Mauro Rosero P."  # Anteriormente SCRIPT_AUTHOR
BANNER_WIDTH = 70 # Ancho ajustado para el nombre más largo

# --- Constantes del Script ---
CURRENT_SCHEMA_VERSION = "1.5"
# Opciones de Plataforma más granulares
PLATFORM_CHOICES = [
    "GitHub",
    "GitLab.com",
    "GitLab (Auto-alojado)",
    "Gitea", # Implícitamente auto-alojado
    # "Forgejo Cloud", # Podríamos añadir si se usa mucho, ej Codeberg
    "Forgejo (Auto-alojado)",
    "Bitbucket Cloud",
    "Bitbucket Server/Data Center", # Auto-alojado
    "Otra"
]
VISIBILITY_CHOICES = ["private", "public"]
OWNER_TYPE_CHOICES = ["user", "organization"]
STATUS_CHOICES = ["planning", "active", "on-hold", "completed", "archived"] # Mantener en inglés puede ser útil para parseo

# Helper function to check if a platform requires a URL
def platform_requires_url(platform_name):
    if not platform_name: return False
    return ("(Auto-alojado)" in platform_name or
            "Server/Data Center" in platform_name or
            platform_name == "Gitea" or
            platform_name == "Otra")

# --- Funciones de Carga/Guardado (Ahora necesitan la ruta como argumento) ---

def load_project_data(meta_file_path: Path): # Añadido argumento
    """Carga datos desde la ruta especificada o retorna estructura por defecto."""
    if meta_file_path.exists() and meta_file_path.is_file():
        try:
            with open(meta_file_path, "rb") as f:
                data = tomllib.load(f)
            # Validar versión de schema (simple check)
            if data.get("schema_version") != CURRENT_SCHEMA_VERSION:
                questionary.print(f"Advertencia: Discrepancia en la versión del esquema (Archivo: {data.get('schema_version', 'N/A')}, Herramienta: {CURRENT_SCHEMA_VERSION}).", style="fg:cyan")
            return data
        except Exception as e:
            questionary.print(f"Error al cargar {meta_file_path}: {e}", style="fg:red")
            sys.exit(1)
    else:
        if meta_file_path.exists():
             questionary.print(f"Advertencia: Se esperaba un archivo pero se encontró un directorio en {meta_file_path}. Usando datos por defecto.", style="fg:cyan")
        return get_default_structure()

def save_project_data(data, meta_file_path: Path, project_base_path: Path):
    """Guarda los datos en el archivo TOML especificado y también en config/project_meta.def."""
    project_dir = meta_file_path.parent # Directorio .project/
    try:
        project_dir.mkdir(parents=True, exist_ok=True)
        # Asegurar que schema_version está actualizado antes de guardar
        data["schema_version"] = CURRENT_SCHEMA_VERSION
        with open(meta_file_path, "wb") as f:
            tomli_w.dump(data, f)
        questionary.print(f"✓ Datos del proyecto guardados en {meta_file_path}", style="fg:green")

        # Ahora, también guardar en config/project_meta.def
        def_dir = project_base_path / "config"
        def_file_path = def_dir / "project_meta.def"
        try:
            def_dir.mkdir(parents=True, exist_ok=True)
            with open(def_file_path, "wb") as f_def:
                tomli_w.dump(data, f_def) # Guardar los mismos datos 'data'
            questionary.print(f"✓ Configuración también guardada en {def_file_path}", style="fg:green")
        except Exception as e_def:
            questionary.print(f"✗ Error al guardar en {def_file_path}: {e_def}", style="fg:red")
            questionary.print(f"  Sin embargo, {meta_file_path} se guardó correctamente.", style="fg:yellow")

    except Exception as e:
        questionary.print(f"✗ Error al guardar {meta_file_path}: {e}", style="fg:red")

def get_git_user_info() -> Dict[str, str]:
    """Obtiene user.name y user.email de la configuración global de Git."""
    user_info = {"name": "", "email": ""}
    try:
        # Obtener user.name
        result_name = subprocess.run(['git', 'config', '--global', 'user.name'], 
                                     capture_output=True, text=True, check=False)
        if result_name.returncode == 0:
            user_info["name"] = result_name.stdout.strip()

        # Obtener user.email
        result_email = subprocess.run(['git', 'config', '--global', 'user.email'], 
                                      capture_output=True, text=True, check=False)
        if result_email.returncode == 0:
            user_info["email"] = result_email.stdout.strip()
            
    except FileNotFoundError: # Git no está instalado o no está en el PATH
        questionary.print("Advertencia: Comando 'git' no encontrado. No se pueden precargar datos de usuario.", style="fg:yellow")
    except Exception as e:
        questionary.print(f"Advertencia: Error al obtener datos de git config: {e}", style="fg:yellow")
    return user_info

def get_default_structure():
    """Retorna la estructura TOML por defecto como diccionario Python, precargando datos de git config."""
    git_user = get_git_user_info()
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "repository": {
            "name": "", "owner_name": "", "owner_type": "user",
            "visibility": "private", "platform": "GitHub", "platform_url": "",
            "description": "", "created_flag": False, "url": "",
            "init_options": {
                "add_readme": True, "add_gitignore": True,
                "gitignore_template": "Python", "add_license": True,
                "license_template": "mit"
            }
        },
        "project_details": {
            "title": "", "purpose": "", "status": "planning", 
            "lead": git_user.get("name", ""), 
            "lead_email": git_user.get("email", ""),
            "pm_tool_info": {"tool_name": "", "project_link": "", "project_key": ""},
            "objectives": [], "stakeholders": [], "technology_stack": [],
            "risks": [], "assumptions": [],
            "constraints": {"budget": "TBD", "timeline": "TBD"}
        },
        "additional_metadata": {}
    }

# --- Funciones de Formularios (Ahora necesitan la ruta base para editar metadata) ---

def prompt_for_required_repo_info(defaults):
    """Pregunta por los campos mínimos obligatorios para crear el repo, secuencialmente."""
    answers = {}
    try:
        # Preguntar Nombre del Repositorio
        answers['name'] = questionary.text(
            "Nombre del Repositorio:",
            default=defaults.get("name", ""),
            validate=lambda text: True if len(text) > 0 else "No puede estar vacío"
        ).ask()
        if answers['name'] is None: return None # Cancelado

        # Preguntar Tipo de Propietario
        answers['owner_type'] = questionary.select(
            "Tipo de Propietario:",
            choices=OWNER_TYPE_CHOICES,
            default=defaults.get("owner_type", "user")
        ).ask()
        if answers['owner_type'] is None: return None # Cancelado

        # Preguntar Nombre del Propietario CONDICIONALMENTE
        if answers['owner_type'] == 'organization':
            answers['owner_name'] = questionary.text(
                "Nombre de la Organización:",
                default=defaults.get("owner_name", ""),
                validate=lambda text: True if len(text) > 0 else "No puede estar vacío"
            ).ask()
            if answers['owner_name'] is None: return None # Cancelado
        else:
            # Si es 'user', no preguntamos y asignamos vacío
            answers['owner_name'] = ""

        # Preguntar Visibilidad
        answers['visibility'] = questionary.select(
            "Visibilidad:",
            choices=VISIBILITY_CHOICES,
            default=defaults.get("visibility", "private")
        ).ask()
        if answers['visibility'] is None: return None # Cancelado

        # Preguntar Plataforma con nuevas opciones
        answers['platform'] = questionary.select(
            "Plataforma:",
            choices=PLATFORM_CHOICES,
            default=defaults.get("platform", "GitHub") # Default a GitHub
        ).ask()
        if answers['platform'] is None: return None # Cancelado

        # Preguntar URL Plataforma CONDICIONALMENTE
        answers['platform_url'] = "" # Default a vacío
        if platform_requires_url(answers['platform']):
            answers['platform_url'] = questionary.text(
                f"URL de la Plataforma ({answers['platform']}):", # Incluir nombre para claridad
                default=defaults.get("platform_url", "")
            ).ask()
            if answers['platform_url'] is None: return None # Cancelado

        return answers

    except KeyboardInterrupt:
        # Si se interrumpe en medio de una pregunta
        return None
    # Eliminar la lógica de fallback compleja, ya que ahora manejamos None en cada .ask()
    # else:
    #    # ... (código fallback eliminado) ...


def edit_repository_info(repo_data, is_initial_setup=False):
    """Edita la información del repositorio de forma interactiva. Devuelve True si éxito, None si se cancela."""
    is_created = repo_data.get("created_flag", False) or repo_data.get("url")

    if is_created:
        questionary.print("--- Info Repositorio (Creado - Campos clave sólo lectura) ---", style="bold")
        questionary.print(f"  Nombre:       {repo_data.get('name', 'N/A')}")
        questionary.print(f"  Propietario:  {repo_data.get('owner_name', 'N/A')} ({repo_data.get('owner_type', 'N/A')})")
        questionary.print(f"  Visibilidad: {repo_data.get('visibility', 'N/A')}")
        platform_display = repo_data.get('platform', 'N/A')
        platform_url_display = repo_data.get('platform_url')
        if platform_url_display:
            platform_display += f" ({platform_url_display})"
        questionary.print(f"  Plataforma:   {platform_display}")
        questionary.print(f"  URL Repo:     {repo_data.get('url', 'No establecido')}")
        
        description_val = questionary.text("Descripción:", default=repo_data.get('description', "")).ask()
        if description_val is None: return None
        repo_data['description'] = description_val
    else:
        if not is_initial_setup:
            questionary.print("--- Info Repositorio (Campos requeridos *) ---", style="bold")
            questionary.print("Nota: Los campos marcados con * son obligatorios.", style="fg:yellow")
        else:
            questionary.print("--- Info Repositorio (Opciones Adicionales) ---", style="bold")

        # Si es setup inicial, el nombre ya debería haber sido pedido por prompt_for_required_repo_info.
        # Si no es setup inicial, o si por alguna razón el nombre falta, se pide aquí.
        if not repo_data.get('name', '').strip() or not is_initial_setup:
            name_val = questionary.text(
                "Nombre del Repositorio:",
                default=repo_data.get('name', ""),
                validate=lambda text: True if len(text.strip()) > 0 else "El nombre no puede estar vacío"
            ).ask()
            if name_val is None: return None
            repo_data['name'] = name_val.strip()
        
        description_val = questionary.text("Descripción:", default=repo_data.get('description', "")).ask()
        if description_val is None: return None
        repo_data['description'] = description_val

        init_options = repo_data.get("init_options", {})
        
        add_readme_val = questionary.confirm("¿Inicializar con README?", default=init_options.get('add_readme', True)).ask()
        if add_readme_val is None: return None
        init_options['add_readme'] = add_readme_val

        add_gitignore_val = questionary.confirm("¿Añadir .gitignore?", default=init_options.get('add_gitignore', True)).ask()
        if add_gitignore_val is None: return None
        init_options['add_gitignore'] = add_gitignore_val
        
        if init_options['add_gitignore']:
            gitignore_template_val = questionary.text("Plantilla .gitignore (ej., Python, Node, vacío para ninguno):", default=init_options.get('gitignore_template', "Python")).ask()
            if gitignore_template_val is None: return None
            init_options['gitignore_template'] = gitignore_template_val
        
        add_license_val = questionary.confirm("¿Añadir LICENSE?", default=init_options.get('add_license', True)).ask()
        if add_license_val is None: return None
        init_options['add_license'] = add_license_val

        if init_options['add_license']:
            license_template_val = questionary.text("Plantilla Licencia (ID SPDX, ej., mit, gpl-3.0):", default=init_options.get('license_template', "mit")).ask()
            if license_template_val is None: return None
            init_options['license_template'] = license_template_val
            
        repo_data["init_options"] = init_options
    return True


def edit_project_details(details_data):
    """Formulario para editar detalles del proyecto. Devuelve True si éxito, None si se cancela."""
    questionary.print("--- Detalle del Proyecto ---", style="bold")
    
    title_val = questionary.text("Título del Proyecto:", default=details_data.get('title', "")).ask()
    if title_val is None: return None
    details_data['title'] = title_val
    
    purpose_val = questionary.text("Propósito/Descripción:", default=details_data.get('purpose', "")).ask()
    if purpose_val is None: return None
    details_data['purpose'] = purpose_val
    
    status_val = questionary.select("Estado:", choices=STATUS_CHOICES, default=details_data.get('status', "planning")).ask()
    if status_val is None: return None
    details_data['status'] = status_val
    
    lead_val = questionary.text("Líder del Proyecto:", default=details_data.get('lead', "")).ask()
    if lead_val is None: return None
    details_data['lead'] = lead_val

    lead_email_val = questionary.text("Email Líder Proyecto:", default=details_data.get('lead_email', "")).ask()
    if lead_email_val is None: return None
    details_data['lead_email'] = lead_email_val

    pm_info = details_data.get("pm_tool_info", {})
    tool_name_val = questionary.text("Herramienta Gestión Proyectos (Jira, Trello, etc., vacío si ninguna):", default=pm_info.get('tool_name', "")).ask()
    if tool_name_val is None: return None
    pm_info['tool_name'] = tool_name_val
    
    project_link_val = questionary.text("URL Proyecto (Gestión):", default=pm_info.get('project_link', "")).ask()
    if project_link_val is None: return None
    pm_info['project_link'] = project_link_val
    
    project_key_val = questionary.text("Clave Proyecto (Gestión, si aplica):", default=pm_info.get('project_key', "")).ask()
    if project_key_val is None: return None
    pm_info['project_key'] = project_key_val
    details_data["pm_tool_info"] = pm_info

    questionary.print(f"Objetivos: {details_data.get('objectives', [])} (Editar manualmente o mejorar script)")
    questionary.print(f"Interesados: {details_data.get('stakeholders', [])} (Editar manualmente o mejorar script)")
    questionary.print(f"Stack Tecnológico: {details_data.get('technology_stack', [])} (Editar manualmente o mejorar script)")

    constraints = details_data.get("constraints", {})
    budget_val = questionary.text("Restricción Presupuesto:", default=constraints.get('budget', 'TBD')).ask()
    if budget_val is None: return None
    constraints['budget'] = budget_val
    
    timeline_val = questionary.text("Restricción Cronograma:", default=constraints.get('timeline', 'TBD')).ask()
    if timeline_val is None: return None
    constraints['timeline'] = timeline_val
    details_data["constraints"] = constraints
    return True

def edit_additional_metadata(metadata_data, meta_file_path: Path): # Añadido argumento
    """Abre el archivo TOML en el editor para metadatos adicionales."""
    
    editor_to_use = os.environ.get('EDITOR')
    editor_found = False

    if editor_to_use:
        # Si EDITOR está configurado, verificar si existe en el PATH
        if shutil.which(editor_to_use):
            editor_found = True
        else:
            questionary.print(f"{Fore.YELLOW}Advertencia: El editor configurado en $EDITOR ('{editor_to_use}') no se encontró en el PATH.{Style.RESET_ALL}")
            editor_to_use = None # Forzar búsqueda de predeterminados
    
    if not editor_to_use: # Si $EDITOR no estaba configurado o el especificado no se encontró
        default_editors = ['nano', 'vim', 'vi'] # Lista de editores a probar
        for editor_candidate in default_editors:
            if shutil.which(editor_candidate):
                editor_to_use = editor_candidate
                editor_found = True
                print(f"{Fore.BLUE}Info: Usando editor predeterminado encontrado: '{editor_to_use}' (ya que $EDITOR no está configurado o el especificado no se encontró).{Style.RESET_ALL}")
                break # Usar el primer editor encontrado de la lista de predeterminados
    
    if not editor_found or not editor_to_use:
        questionary.print(f"{Fore.RED}Error: No se encontró un editor de texto adecuado (probados: $EDITOR, nano, vim, vi).{Style.RESET_ALL}")
        questionary.print(f"{Fore.YELLOW}Por favor, instale uno de estos editores o configure la variable de entorno $EDITOR con la ruta a su editor preferido.{Style.RESET_ALL}")
        return metadata_data # Devolver sin cambios si no se encuentra ningún editor

    # --- Proceder con la edición ---
    project_dir = meta_file_path.parent 
    questionary.print(f"Abriendo {meta_file_path} en {editor_to_use} para editar la sección [additional_metadata].", style="fg:cyan")
    questionary.print("Guarda el archivo en el editor y luego pulsa Enter aquí para recargar.")
    try:
        project_dir.mkdir(parents=True, exist_ok=True)
        # --- Ejecutar editor ---
        # Asegurar comillas alrededor del editor y la ruta del archivo por si contienen espacios.
        # subprocess.run es más robusto, pero os.system es más simple y ya se usaba.
        cmd_str = f'"{editor_to_use}" "{meta_file_path}"'
        status_code = os.system(cmd_str)

        if status_code != 0:
            # Un código de salida distinto de cero no siempre es un error fatal si el usuario guardó,
            # pero es bueno informarlo.
            questionary.print(f"{Fore.CYAN}Comando del editor ('{editor_to_use}') finalizó con estado {status_code}.{Style.RESET_ALL}")

        # --- Recargar ---
        try:
            import time
            time.sleep(0.2) # Pausa breve antes de intentar leer, puede ayudar en algunos sistemas
            reloaded_data = load_project_data(meta_file_path)
            return reloaded_data.get("additional_metadata", {})
        except Exception as load_err:
            questionary.print(f"{Fore.RED}Error recargando tras edición manual: {load_err}{Style.RESET_ALL}")
            questionary.print(f"{Fore.YELLOW}Las ediciones manuales podrían ser inválidas. Se mantienen los metadatos previos.{Style.RESET_ALL}")
            return metadata_data # Devolver la versión anterior si la recarga falla

    except Exception as e:
        questionary.print(f"{Fore.RED}Error abriendo editor o procesando después de la edición: {e}{Style.RESET_ALL}")
        return metadata_data # Devolver sin cambios en caso de otros errores


# --- Funciones de Utilidad para Banner y Limpieza ---
def clear_screen():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    """Muestra el banner de la aplicación."""
    linea_superior_inferior = "=" * BANNER_WIDTH
    titulo_app = f"{APP_NAME} - Versión {VERSION}"
    linea_autor = f"Autor: {AUTHOR}"
    # (Opcional) Eslogan o descripción breve.
    # eslogan = "Gestiona metadatos de tus proyectos fácilmente"

    print(linea_superior_inferior)
    print(f"{titulo_app:^{BANNER_WIDTH}}") # Centrado
    print(f"{linea_autor:^{BANNER_WIDTH}}") # Centrado
    # if eslogan: print(f"{eslogan:^{BANNER_WIDTH}}") # Centrado
    print(linea_superior_inferior)
    print() # Línea vacía después del banner

def check_git_repo() -> Tuple[bool, str]:
    """Verifica si el directorio actual es un repositorio git y lo inicializa si no lo es."""
    try:
        # Verificar si es un repositorio git
        result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True, "El directorio ya es un repositorio git."
        
        # Si no es un repositorio, inicializarlo
        questionary.print("Inicializando nuevo repositorio git...", style="fg:cyan")
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        return True, "Repositorio git inicializado con rama main."
        
    except subprocess.CalledProcessError as e:
        return False, f"Error al inicializar repositorio git: {e}"
    except Exception as e:
        return False, f"Error inesperado: {e}"

def check_git_config() -> Tuple[bool, Dict[str, str]]:
    """Verifica la configuración global de git."""
    config = {}
    required = ['user.name', 'user.email', 'user.signingkey']
    
    try:
        for key in required:
            result = subprocess.run(['git', 'config', '--global', key], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                config[key] = result.stdout.strip()
            else:
                config[key] = ""
        
        missing = [key for key, value in config.items() if not value]
        return len(missing) == 0, config
        
    except Exception as e:
        return False, {"error": str(e)}

def check_git_remote() -> Tuple[bool, str]:
    """Verifica si hay remotes configurados."""
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            return True, "Ya existe un repositorio remoto configurado."
        return False, "No hay repositorios remotos configurados."
    except Exception as e:
        return False, f"Error al verificar repositorios remotos: {e}"

def get_token(args: argparse.Namespace, platform: str) -> Optional[str]:
    """Obtiene el token de autenticación para la plataforma especificada.
    
    Args:
        args: Argumentos de línea de comandos
        platform: Plataforma Git (github, gitlab, gitea)
    
    Returns:
        Token decodificado o None si no se encuentra
    """
    def decode_base64_token(token: str) -> Optional[str]:
        """Intenta decodificar un token de base64."""
        try:
            return base64.b64decode(token).decode('utf-8')
        except Exception:
            return None

    # 1. Intentar obtener del argumento --token
    if args.token:
        decoded_token = decode_base64_token(args.token)
        if decoded_token:
            return decoded_token
        questionary.print("Error: El token proporcionado no es un base64 válido.", style="fg:red")
        return None
    
    # 2. Intentar obtener de la variable de entorno específica de la plataforma
    env_token = os.environ.get(f'{platform.upper()}_TOKEN')
    if env_token:
        decoded_token = decode_base64_token(env_token)
        if decoded_token:
            return decoded_token
        questionary.print(f"Error: El token en la variable de entorno {platform.upper()}_TOKEN no es un base64 válido.", style="fg:red")
        return None
    
    # 3. Si no se encontró en ninguna parte, mostrar error
    questionary.print(f"Error: No se encontró el token para {platform}.", style="fg:red")
    questionary.print("Debes proporcionar el token de una de estas formas:", style="fg:yellow")
    questionary.print("  1. Usando el argumento --token <token_base64>", style="fg:yellow")
    questionary.print(f"  2. Configurando la variable de entorno {platform.upper()}_TOKEN", style="fg:yellow")
    questionary.print("El token debe estar codificado en base64.", style="fg:yellow")
    return None

def push_branches_to_remote(project_base_path: Path) -> Tuple[bool, str]:
    """Realiza push de las ramas existentes al repositorio remoto."""
    try:
        result = subprocess.run(['git', 'branch', '--format=%(refname:short)'], 
                              capture_output=True, text=True, check=True, cwd=project_base_path)
        local_branches = result.stdout.strip().split('\n')
        
        if 'main' in local_branches:
            questionary.print("Haciendo push de la rama main...", style="fg:cyan")
            subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True, cwd=project_base_path)
        else:
            questionary.print("Advertencia: No se encontró la rama 'main' local para hacer push.", style="fg:yellow")

        if 'develop' in local_branches:
            questionary.print("Haciendo push de la rama develop...", style="fg:cyan")
            subprocess.run(['git', 'push', '-u', 'origin', 'develop'], check=True, cwd=project_base_path)
        
        if 'staging' in local_branches:
            questionary.print("Haciendo push de la rama staging...", style="fg:cyan")
            subprocess.run(['git', 'push', '-u', 'origin', 'staging'], check=True, cwd=project_base_path)
        
        return True, "✓ Ramas subidas exitosamente al repositorio remoto"
        
    except subprocess.CalledProcessError as e:
        # Decodificar stderr si es bytes
        error_output = e.stderr.decode('utf-8', 'replace') if isinstance(e.stderr, bytes) else e.stderr
        return False, f"Error al hacer push de las ramas: {error_output}"
    except Exception as e:
        return False, f"Error inesperado al hacer push: {str(e)}"

def verify_repository_info(project_data: Dict[str, Any], project_base_path: Path) -> Tuple[bool, str]:
    """Verifica que la información del repo en TOML coincida con el repo local, ofreciendo actualizar el TOML."""
    repo_data = project_data["repository"] # Obtener la sección del repo para modificarla si es necesario
    try:
        # 1. Verificar que es un repositorio git
        result_is_repo = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                                      cwd=project_base_path,
                                      capture_output=True, text=True, check=False)
        if result_is_repo.returncode != 0:
            return False, "El directorio no es un repositorio git"
        
        # 2. Verificar el remote origin y obtener su URL
        result_remote_url = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                                         cwd=project_base_path,
                                         capture_output=True, text=True, check=False)
        if result_remote_url.returncode != 0:
            return False, "No hay un remote 'origin' configurado"
        
        remote_url_from_git = result_remote_url.stdout.strip()
        
        # 3. Obtener URL del TOML y comparar/actualizar
        toml_url = repo_data.get("url", "").strip()

        if not toml_url or toml_url != remote_url_from_git:
            message = (
                f"La URL del repositorio en project_meta.toml (actual: '{toml_url if toml_url else 'No establecida'}') "
                f"no coincide con la URL del remote 'origin' en Git (esperada: '{remote_url_from_git}') o está vacía."
            )
            questionary.print(message, style="fg:yellow")
            
            confirm_update = questionary.confirm(
                "¿Desea actualizar la URL en project_meta.toml para que coincida con la del remote 'origin' de Git?", 
                default=True
            ).ask()
            
            if confirm_update:
                repo_data["url"] = remote_url_from_git
                project_meta_file = project_base_path / ".project" / "project_meta.toml"
                save_project_data(project_data, project_meta_file, project_base_path)
                questionary.print(f"✓ URL en project_meta.toml actualizada a: {remote_url_from_git}", style="fg:green")
                toml_url = remote_url_from_git 
            else:
                return False, f"Discrepancia de URL no resuelta. TOML: '{toml_url}', Git remote: '{remote_url_from_git}'"
        
        # 4. Verificar el nombre del repositorio (esta verificación puede ser menos crítica si la URL ya coincide)
        repo_name_toml = repo_data.get("name", "").strip()
        if not repo_name_toml:
            # Si el nombre en TOML está vacío, podríamos intentar derivarlo de la URL remota como un fallback.
            # Por ejemplo, de 'git@github.com:user/repo-name.git' o 'https://host.com/user/repo-name'
            # Esto es opcional y puede añadir complejidad.
            # Por ahora, si la URL coincide, asumimos que el nombre también debería ser consistente o no es crítico para esta verificación.
            pass # Opcionalmente, podríamos añadir una validación más estricta aquí si es necesario.

        # 5. Verificar que estamos en la rama main (o la rama por defecto del repo si es configurable)
        # Esta verificación puede ser específica del flujo de 'configure_branch_protection'
        result_branch = subprocess.run(['git', 'branch', '--show-current'],
                                   cwd=project_base_path,
                                   capture_output=True, text=True, check=False)
        if result_branch.returncode != 0:
            # Podría ser un repo sin commits o en estado detached HEAD
            questionary.print("Advertencia: No se pudo determinar la rama actual.", style="fg:yellow")
        else:
            current_branch = result_branch.stdout.strip()
            # Idealmente, la rama por defecto (ej. 'main') debería ser configurable o detectada.
            # Por ahora, se asume 'main' para la protección, pero esta función solo verifica.
            # if current_branch != "main":
            #     return False, f"Debes estar en la rama 'main' para configurar la protección (actual: {current_branch})"
            pass # La lógica de la rama específica se maneja mejor en la función que llama a esta verificación

        return True, f"Información del repositorio verificada. URL Git y TOML: '{toml_url}'"
        
    except Exception as e:
        return False, f"Error inesperado al verificar el repositorio: {str(e)}"

def create_github_repository(project_data: Dict[str, Any], token: str, use_https: bool = True, project_base_path: Path = Path(".")) -> Tuple[bool, str]:
    """Crea un repositorio en GitHub usando la API y hace commit/push inicial del proyecto completo."""
    try:
        g = Github(token)
        repo_data = project_data["repository"]
        repo_name = repo_data.get("name", "").strip()
        
        if not repo_name:
            return False, "Error: El nombre del repositorio no puede estar vacío. Por favor, configura el nombre en project_meta.toml"
        
        description = repo_data.get("description", "")
        private = repo_data.get("visibility", "private") == "private"
        owner_type = repo_data.get("owner_type", "user")
        owner_name = repo_data.get("owner_name", "")
        
        if owner_type == "organization":
            if not owner_name:
                return False, "Error: Se requiere el nombre de la organización cuando owner_type es 'organization'"
            try:
                owner = g.get_organization(owner_name)
            except GithubException as e:
                return False, f"Error al obtener la organización '{owner_name}': {e}"
        else:
            owner = g.get_user()
        
        questionary.print(f"Creando repositorio '{repo_name}' en GitHub para {'la organización ' + owner_name if owner_type == 'organization' else 'el usuario ' + owner.login}...", style="fg:cyan")
        repo = owner.create_repo(
            name=repo_name,
            description=description,
            private=private,
            has_issues=True,
            has_wiki=True,
            has_projects=True,
            auto_init=False
        )
        questionary.print(f"✓ Repositorio '{repo.full_name}' creado en GitHub.", style="fg:green")
        
        actual_remote_url_used = repo.ssh_url 
        if use_https:
            actual_remote_url_used = repo.clone_url 
            if token:
                actual_remote_url_used = actual_remote_url_used.replace("https://", f"https://{token}@")
        
        questionary.print(f"Configurando remote 'origin' a: {actual_remote_url_used.replace(token, '<TOKEN>') if token and use_https else actual_remote_url_used}", style="fg:cyan")
        subprocess.run(['git', 'remote', 'add', 'origin', actual_remote_url_used], check=True, cwd=project_base_path)
        questionary.print("✓ Remote 'origin' configurado.", style="fg:green")

        questionary.print("Añadiendo todos los archivos del proyecto al staging (git add .)...", style="fg:cyan")
        subprocess.run(['git', 'add', '.'], check=True, cwd=project_base_path)
        
        result_staged = subprocess.run(['git', 'diff', '--staged', '--quiet'], check=False, cwd=project_base_path)
        
        if result_staged.returncode == 1:
            commit_message = "[CHORE] Commit inicial del proyecto"
            questionary.print(f"Realizando commit inicial: {commit_message}", style="fg:cyan")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True, cwd=project_base_path)
            questionary.print("✓ Commit inicial del proyecto realizado.", style="fg:green")
        else:
            questionary.print("No se detectaron nuevos cambios en el proyecto para el commit inicial.", style="fg:yellow")

        project_meta_file_rel_path = Path(".project") / "project_meta.toml"
        repo_data["url"] = actual_remote_url_used 
        repo_data["created_flag"] = True
        save_project_data(project_data, project_base_path / project_meta_file_rel_path, project_base_path)
        questionary.print(f"URL del repositorio ({actual_remote_url_used.replace(token, '<TOKEN>') if token and use_https else actual_remote_url_used}) guardada en la configuración.", style="fg:green")

        push_success, push_msg = push_branches_to_remote(project_base_path)
        if not push_success:
            return False, push_msg
        
        display_url = actual_remote_url_used.replace(token, '<TOKEN>') if token and use_https else actual_remote_url_used
        return True, f"Repositorio creado y configurado exitosamente en {display_url}"
        
    except GithubException as ge:
        if ge.status == 422:
            error_details = ge.data.get('message', '')
            if 'name already exists' in error_details:
                return False, f"Error: El repositorio '{repo_name}' ya existe en GitHub para el propietario especificado."
        return False, f"Error de GitHub API: {str(ge)} (Status: {ge.status}, Data: {ge.data})"
    except subprocess.CalledProcessError as cpe:
        error_output = cpe.stderr.strip() if cpe.stderr else cpe.stdout.strip()
        cmd_str = " ".join(cpe.cmd)
        return False, f"Error ejecutando comando git '{cmd_str}': {error_output}"
    except Exception as e:
        return False, f"Error inesperado al crear el repositorio: {str(e)}"

def create_gitlab_repository(project_data: Dict[str, Any], token: str, use_https: bool = False) -> Tuple[bool, str]:
    """Crea un repositorio en GitLab usando la API."""
    # TODO: Implementar soporte para GitLab
    return False, "Soporte para GitLab aún no implementado"

def create_gitea_repository(project_data: Dict[str, Any], token: str, use_https: bool = False) -> Tuple[bool, str]:
    """Crea un repositorio en Gitea usando la API."""
    # TODO: Implementar soporte para Gitea
    return False, "Soporte para Gitea aún no implementado"

def create_remote_repo(project_base_path: Path, args: argparse.Namespace) -> None:
    """Crea un repositorio remoto en la plataforma especificada."""
    project_meta_file = project_base_path / ".project" / "project_meta.toml" # Definir aquí

    # Verificar explícitamente que project_meta.toml exista antes de cualquier otra cosa
    if not project_meta_file.is_file():
        questionary.print(f"✗ Error: El archivo de metadatos del proyecto ({project_meta_file.name}) no existe.", style="fg:red")
        questionary.print("  Ejecuta primero 'promanager.py --project' primero para crear y guardar la configuración.", style="fg:yellow")
        sys.exit(1)
        
    # 1. Verificar repositorio git
    is_repo, msg = check_git_repo()
    if not is_repo:
        questionary.print(f"Error: {msg}", style="fg:red")
        sys.exit(1)
    questionary.print(msg, style="fg:green")
    
    # 2. Verificar configuración git
    has_config, config = check_git_config()
    if not has_config:
        questionary.print("Error: Faltan configuraciones globales de git:", style="fg:red")
        for key, value in config.items():
            if not value:
                questionary.print(f"  - {key}", style="fg:red")
        sys.exit(1)
    
    # 3. Verificar remotes
    has_remote, msg = check_git_remote()
    if has_remote:
        questionary.print(f"Error: {msg}", style="fg:red")
        sys.exit(1)
    
    # 4. Verificar metadatos
    if not project_meta_file.is_file():
        questionary.print("Error: No se encontró el archivo de metadatos del proyecto.", style="fg:red")
        questionary.print("Ejecuta primero el comando sin argumentos para crear el proyecto.", style="fg:yellow")
        sys.exit(1)
    
    project_data = load_project_data(project_meta_file)
    platform = project_data["repository"].get("platform", "").lower()
    
    # 5. Obtener token
    token = get_token(args, platform)
    if not token:
        sys.exit(1)
    
    # 6. Crear repositorio según la plataforma
    success = False
    msg = ""
    
    if platform == "github":
        success, msg = create_github_repository(project_data, token, args.https)
    elif platform == "gitlab.com" or platform == "gitlab (auto-alojado)":
        success, msg = create_gitlab_repository(project_data, token, args.https)
    elif platform == "gitea":
        success, msg = create_gitea_repository(project_data, token, args.https)
    else:
        questionary.print(f"Error: La plataforma '{platform}' no está soportada actualmente.", style="fg:red")
        questionary.print("Plataformas soportadas: GitHub, GitLab, Gitea", style="fg:yellow")
        sys.exit(1)
    
    if success:
        questionary.print(msg, style="fg:green")
    else:
        questionary.print(f"Error: {msg}", style="fg:red")
        sys.exit(1)

def configure_branch_protection(project_base_path: Path, args: argparse.Namespace) -> None:
    """Configura las reglas de protección de ramas según el tipo de proyecto."""
    project_meta_file = project_base_path / ".project" / "project_meta.toml"

    if not project_meta_file.is_file():
        questionary.print(f"✗ Error: El archivo de metadatos del proyecto ({project_meta_file.name}) no existe.", style="fg:red")
        questionary.print(f"  Por favor, ejecute 'promanager.py --project' primero para crear y guardar la configuración.", style="fg:yellow")
        sys.exit(1)
        
    project_data = load_project_data(project_meta_file)
    # No extraer repo_data aquí para pasar a verify_repository_info, 
    # ya que verify_repository_info espera el project_data completo para poder modificarlo y guardarlo.
    # repo_data = project_data.get("repository", {})
    
    is_repo, msg_check_repo = check_git_repo() # check_git_repo no necesita project_data
    if not is_repo:
        questionary.print(f"Error: {msg_check_repo}", style="fg:red")
        sys.exit(1)
    
    has_remote, msg_check_remote = check_git_remote() # check_git_remote no necesita project_data
    if not has_remote:
        questionary.print("Error: No hay un repositorio remoto configurado.", style="fg:red")
        questionary.print("Ejecuta '--newrepo' para crear y configurar el repositorio remoto.", style="fg:yellow")
        sys.exit(1)
    
    # Pasar project_data completo a verify_repository_info
    success_verify, msg_verify = verify_repository_info(project_data, project_base_path)
    if not success_verify:
        questionary.print(f"Error en la verificación del repositorio: {msg_verify}", style="fg:red")
        sys.exit(1)
    questionary.print(f"✓ {msg_verify}", style="fg:green") # Mensaje de éxito de la verificación
    
    # Ahora que project_data puede haber sido actualizado por verify_repository_info (si el usuario aceptó cambiar la URL),
    # podemos obtener la sección repo_data actualizada.
    repo_data = project_data.get("repository", {})

    platform = repo_data.get("platform", "").lower()
    if not platform:
        questionary.print("Error: No se especificó la plataforma en el archivo TOML.", style="fg:red")
        sys.exit(1)
    
    if not args.token and not os.environ.get(f"{platform.upper()}_TOKEN"):
        questionary.print(f"Error: Se requiere un token para {platform}.", style="fg:red")
        questionary.print("Debes proporcionar el token de una de estas formas:", style="fg:yellow")
        questionary.print("  1. Usando el argumento --token <token_base64>", style="fg:yellow")
        questionary.print(f"  2. Configurando la variable de entorno {platform.upper()}_TOKEN", style="fg:yellow")
        questionary.print("El token debe estar codificado en base64.", style="fg:yellow")
        sys.exit(1)
    
    token = get_token(args, platform)
    if not token:
        sys.exit(1)
    
    if "protection_config" not in repo_data:
        repo_data["protection_config"] = {}
    
    is_team_project = args.team if args.team is not None else not repo_data["protection_config"].get("single_developer", True)
    
    reviewers = args.reviewers.split(",") if args.reviewers else repo_data["protection_config"].get("reviewers", [])
    branch_leaders = args.branch_leaders.split(",") if args.branch_leaders else repo_data["protection_config"].get("branch_leaders", [])
    
    repo_data["protection_config"].update({
        "single_developer": not is_team_project,
        "reviewers": reviewers,
        "branch_leaders": branch_leaders,
        "branches": MAIN_BRANCHES, # Usar las constantes globales definidas en el script
        "work_branches": BRANCH_TYPES # Usar las constantes globales definidas en el script
    })
    
    # project_data ya ha sido modificado en memoria, ahora lo guardamos.
    save_project_data(project_data, project_meta_file, project_base_path)
    questionary.print("✓ Configuración de protección actualizada y guardada en project_meta.toml (y .def)", style="fg:green")
    
    # ... (resto de la lógica para aplicar la configuración con el configurador de la plataforma)
    try:
        if platform == "github":
            if not PYGITHUB_INSTALLED_CORRECTLY and not check_and_install_pygithub():
                 questionary.print("PyGithub es necesario para esta operación y no pudo ser cargado o instalado.", style="fg:red")
                 sys.exit(1)
            configurator = GitHubConfigurator(project_data, token)
        # ... (otros elif para GitLab, Gitea) ...
        else:
            questionary.print(f"Error: La plataforma '{platform}' no está soportada actualmente.", style="fg:red")
            sys.exit(1)
    except ValueError as e:
        questionary.print(f"Error inicializando el configurador para {platform}: {str(e)}", style="fg:red")
        sys.exit(1)
    except Exception as e:
        questionary.print(f"Error inesperado al inicializar el configurador: {str(e)}", style="fg:red")
        sys.exit(1)
    
    # Definir nombres clave de ramas
    main_branch_key = "main"
    develop_branch_key = "develop"
    staging_branch_key = "staging" # Usado como clave en MAIN_BRANCHES

    protection_targets = []
    config_branches = repo_data.get("protection_config", {}).get("branches", {})

    # Procesar rama principal (main)
    main_rules = config_branches.get(main_branch_key, {}).copy()
    if not main_rules:
        questionary.print(f"Advertencia: No se encontraron reglas de configuración para la rama '{main_branch_key}'. Se omitirá.", style="fg:yellow")
    else:
        # if not is_team_project: # Modo monodesarrollador  <-- LÍNEA ELIMINADA
        #     main_rules["allow_direct_push"] = True          <-- LÍNEA ELIMINADA
        protection_targets.append({"name": main_branch_key, "rules": main_rules})

    # Procesar rama de desarrollo (develop)
    develop_rules = config_branches.get(develop_branch_key, {}).copy()
    if not develop_rules:
        questionary.print(f"Advertencia: No se encontraron reglas de configuración para la rama '{develop_branch_key}'. Se omitirá.", style="fg:yellow")
    else:
        # if not is_team_project: # Modo monodesarrollador  <-- LÍNEA ELIMINADA
        #     develop_rules["allow_direct_push"] = True       <-- LÍNEA ELIMINADA
        protection_targets.append({"name": develop_branch_key, "rules": develop_rules})

    # Procesar rama de staging (solo si es proyecto de equipo)
    if is_team_project:
        staging_rules = config_branches.get(staging_branch_key, {}).copy()
        if not staging_rules:
            questionary.print(f"Advertencia: No se encontraron reglas de configuración para la rama '{staging_branch_key}' (modo equipo). Se omitirá.", style="fg:yellow")
        else:
            # Para staging en modo equipo, las reglas de MAIN_BRANCHES aplican directamente (allow_direct_push=False)
            protection_targets.append({"name": staging_branch_key, "rules": staging_rules})
    
    if not protection_targets:
        questionary.print("No hay ramas configuradas para protección. Finalizando.", style="fg:yellow")
        return

    questionary.print(f"Aplicando protección de ramas (Modo: {'Equipo' if is_team_project else 'Monodesarrollador'})...", style="fg:cyan")
    for target in protection_targets:
        branch_name_to_protect = target["name"]
        rules_to_apply = target["rules"]
        
        questionary.print(f"  Configurando protección para: '{branch_name_to_protect}'...", style="fg:blue")
        success_protect, msg_protect = configurator.configure_branch_protection(branch_name_to_protect, rules_to_apply)
        if success_protect:
            questionary.print(f"  ✓ {msg_protect}", style="fg:green")
        else:
            questionary.print(f"  ✗ {msg_protect}", style="fg:red")
            # Considerar si se debe continuar con otras ramas o detener en caso de error
    
    # Configuración de liderazgo de revisión (sin cambios en esta lógica)
    if reviewers or branch_leaders:
        # Asegurarse de que los revisores/líderes no estén vacíos antes de intentar configurar
        valid_reviewers = [r for r in reviewers if r.strip()]
        valid_branch_leaders = [bl for bl in branch_leaders if bl.strip()]
        if valid_reviewers or valid_branch_leaders:
            success_review, msg_review = configurator.configure_review_leadership(valid_reviewers, valid_branch_leaders)
            if success_review:
                questionary.print(f"✓ {msg_review}", style="fg:green")
            else:
                questionary.print(f"✗ {msg_review}", style="fg:red")
        else:
            questionary.print("No se especificaron revisores o líderes de rama válidos para configurar.", style="fg:yellow")

def initialize_project_structure(project_base_path: Path) -> Tuple[bool, str]:
    """Verifica la existencia de archivos de configuración. No crea ni copia archivos."""
    meta_file = project_base_path / ".project" / "project_meta.toml"
    def_file = project_base_path / "config" / "project_meta.def"

    if meta_file.is_file():
        return True, f"✓ Archivo de metadatos {meta_file.name} encontrado."
    
    # meta_file no existe
    if def_file.is_file():
        # No es un error per se, pero el .toml principal falta.
        return True, f"ℹ️ Archivo {meta_file.name} no encontrado, pero {def_file.name} existe. Use --project para generar {meta_file.name}."
    
    # Ni meta_file ni def_file existen
    error_message = (
        f"✗ Error: No se encontró {meta_file.name} ni {def_file.name}.\n"
        f"  Por favor, ejecute 'promanager.py --project' para crear una nueva configuración."
    )
    return False, error_message

def main():
    """Función principal de la herramienta."""
    clear_screen()
    show_banner()

    # --- Configurar y Parsear Argparse PRIMERO ---
    parser = argparse.ArgumentParser(
        description="Gestiona el archivo de metadatos del proyecto (project_meta.toml).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Ejemplos:
  %(prog)s --project
  %(prog)s --newrepo
  %(prog)s --newrepo --token <token_base64>
  %(prog)s --newrepo --https
  %(prog)s --configure-protection
  %(prog)s --configure-protection --team --reviewers \"user1,user2\"
  %(prog)s --configure-protection --branch-leaders \"user1,user2\"

Nota: El token es requerido para --newrepo y --configure-protection.
Puede proporcionarse con --token o mediante la variable de entorno <PLATFORM>_TOKEN.
"""
    )
    parser.add_argument(
        "-p", "--path",
        default=".",
        help="Ruta al directorio del proyecto (por defecto: directorio actual)."
    )
    parser.add_argument(
        "--project",
        action="store_true",
        help="Crea o edita el archivo de metadatos del proyecto (project_meta.toml)."
    )
    parser.add_argument(
        "--newrepo",
        action="store_true",
        help="Crea un nuevo repositorio remoto basado en la plataforma configurada en project_meta.toml."
    )
    parser.add_argument(
        "--configure-protection",
        action="store_true",
        help="Configura las reglas de protección de ramas según el tipo de proyecto."
    )
    parser.add_argument(
        "--team",
        action="store_true",
        help="Configura el repositorio como proyecto de equipo (requiere revisión de PRs)."
    )
    parser.add_argument(
        "--reviewers",
        help="Lista de revisores separados por comas (ej: user1,user2,team1)."
    )
    parser.add_argument(
        "--branch-leaders",
        help="Lista de líderes de rama separados por comas (ej: user1,user2,team1)."
    )
    parser.add_argument(
        "--token",
        help="Token de autenticación en base64 (alternativa a GITHUB_TOKEN)."
    )
    parser.add_argument(
        "--https",
        action="store_true",
        help="Usa HTTPS en lugar de SSH para el repositorio remoto."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="Muestra la versión del programa y sale."
    )
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
        
    args = parser.parse_args()
    # ------------------------------------------

    # --- Definir rutas basadas en el argumento ---
    project_base_path = Path(args.path).resolve()
    project_meta_dir = project_base_path / ".project"
    project_meta_file = project_meta_dir / "project_meta.toml"
    config_def_file_path = project_base_path / "config" / "project_meta.def" # Definido para uso general
    
    # --- Manejar comando --project ---
    if args.project:
        # La lógica de initialize_project_structure no es necesaria aquí, 
        # ya que --project maneja la creación/carga en memoria directamente.
        questionary.print(f"Operando en el directorio del proyecto: {project_base_path}")
        
        file_existed_at_start = project_meta_file.is_file()
        project_data: Dict[str, Any]

        if not file_existed_at_start:
            if config_def_file_path.is_file():
                questionary.print(f"ℹ️ Archivo {project_meta_file.name} no encontrado. Iniciando con datos de {config_def_file_path.name}.", style="fg:cyan")
                project_data = load_project_data(config_def_file_path)
            else: # Ni .toml ni .def existen
                questionary.print(f"ℹ️ Archivo {project_meta_file.name} y {config_def_file_path.name} no encontrados. Iniciando configuración nueva.", style="fg:cyan")
                project_data = get_default_structure()
                
                # --- MODO DE CAPTURA INICIAL ---
                questionary.print("--- Configuración Inicial Obligatoria ---", style="bold fg:yellow")
                
                # 1. Información requerida del repositorio
                repo_info_collected = prompt_for_required_repo_info(project_data['repository'])
                if repo_info_collected is None:
                    questionary.print("Configuración inicial cancelada. Saliendo.", style="fg:red")
                    sys.exit(1)
                project_data['repository'].update(repo_info_collected)

                # 2. Opciones adicionales del repositorio (descripción, README, .gitignore, licencia)
                # edit_repository_info ahora devuelve True/None y se le pasa is_initial_setup=True
                if edit_repository_info(project_data['repository'], is_initial_setup=True) is None:
                    questionary.print("Configuración inicial cancelada. Saliendo.", style="fg:red")
                    sys.exit(1)
                
                # 3. Detalles del proyecto
                if edit_project_details(project_data['project_details']) is None:
                    questionary.print("Configuración inicial cancelada. Saliendo.", style="fg:red")
                    sys.exit(1)
                
                questionary.print("✓ Configuración inicial completada. Ahora puede guardar o seguir editando.", style="fg:green")
                # --- FIN MODO DE CAPTURA INICIAL ---
            original_data_str = str(project_data) # Para detectar cambios desde este punto
        else: # .toml sí existe
            project_data = load_project_data(project_meta_file)
            original_data_str = str(project_data)

        while True:
            try:
                current_data_str = str(project_data)
                modified_since_load_or_default = (current_data_str != original_data_str)
                
                prompt_title = "Selecciona acción:"
                if modified_since_load_or_default:
                    prompt_title += " (Hay cambios sin guardar)"

                choices = [
                    "Editar Info Repositorio",
                    "Editar Detalles Proyecto",
                    "Editar Metadatos Adicionales (Manual)",
                ]
                
                can_save = modified_since_load_or_default or not file_existed_at_start
                
                if can_save:
                    choices.append("Guardar Cambios")
                
                choices.append("Salir (Descartar Cambios)")

                if can_save:
                    choices.append("Guardar y Salir")
                
                action = questionary.select(
                    prompt_title,
                    choices=choices,
                    qmark=">", pointer="->"
                ).ask()
            except KeyboardInterrupt:
                action = None

            if action == "Editar Info Repositorio":
                edit_repository_info(project_data["repository"])
            elif action == "Editar Detalles Proyecto":
                edit_project_details(project_data["project_details"])
            elif action == "Editar Metadatos Adicionales (Manual)":
                if not project_meta_file.is_file() and not file_existed_at_start :
                    if questionary.confirm(f"El archivo {project_meta_file.name} aún no se ha creado. ¿Guardar la configuración actual para poder editarla manualmente?").ask():
                        save_project_data(project_data, project_meta_file, project_base_path)
                        original_data_str = str(project_data) 
                        file_existed_at_start = True
                    else:
                        continue 
                elif not project_meta_file.is_file() and file_existed_at_start:
                     questionary.print(f"Advertencia: {project_meta_file.name} parece haber sido borrado externamente. Guarde primero.", style="fg:yellow")
                     continue
                new_metadata = edit_additional_metadata(project_data.get("additional_metadata", {}), project_meta_file)
                project_data["additional_metadata"] = new_metadata
            elif action == "Guardar Cambios":
                save_project_data(project_data, project_meta_file, project_base_path)
                original_data_str = str(project_data) 
                file_existed_at_start = True 
            elif action == "Salir (Descartar Cambios)":
                if modified_since_load_or_default: 
                    confirm_exit = questionary.confirm("¿Descartar cambios no guardados?").ask()
                    if not confirm_exit:
                        continue
                print("Saliendo sin guardar.")
                sys.exit(0)
            elif action == "Guardar y Salir":
                save_project_data(project_data, project_meta_file, project_base_path)
                print("Saliendo.")
                sys.exit(0)
            elif action is None: 
                if modified_since_load_or_default:
                    confirm_exit = questionary.confirm("Tienes cambios no guardados. ¿Salir de todas formas?").ask()
                    if not confirm_exit:
                        continue
                print("Saliendo.")
                sys.exit(0)
        return

    # --- Lógica común para comandos que requieren configuración (--newrepo, --configure-protection) ---
    
    # Verificar estado de la configuración ANTES de continuar con otros comandos
    config_exists = project_meta_file.is_file()
    def_exists = config_def_file_path.is_file()

    if not config_exists and not def_exists and (args.newrepo or args.configure_protection):
        questionary.print("✗ No se encontró configuración de proyecto (.toml ni .def).", style="fg:red")
        questionary.print("  Se solicitará la información mínima para crear el repositorio.", style="fg:yellow")
        
        required_repo_info = prompt_for_required_repo_info({})
        if required_repo_info is None:
            questionary.print("Creación de configuración cancelada. Saliendo.", style="fg:red")
            sys.exit(1)
        
        # Construir project_data mínimo
        project_data_min = get_default_structure()
        # Actualizar solo la sección del repositorio con la info capturada
        # No sobreescribir init_options por defecto con un diccionario vacío si no se capturaron
        for key, value in required_repo_info.items():
            if key in project_data_min["repository"]:
                 project_data_min["repository"][key] = value
            # Considerar si 'platform_url' etc. deben crearse si no están en defaults, 
            # pero prompt_for_required_repo_info los incluye en su retorno. 
            # El .update() directo es más simple si las claves coinciden.
            # Sin embargo, para ser explícito y mantener estructura:
            # project_data_min["repository"]["name"] = required_repo_info.get("name", "") etc.
        
        # Simplificación: prompt_for_required_repo_info devuelve claves que son un subconjunto
        # o coinciden con las de la sección [repository] de get_default_structure.
        # Las init_options y otros campos no retornados por prompt_for_required_repo_info
        # mantendrán sus valores por defecto de get_default_structure.
        project_data_min["repository"].update(required_repo_info)

        questionary.print("Guardando configuración mínima inicial...", style="fg:cyan")
        save_project_data(project_data_min, project_meta_file, project_base_path)
        questionary.print(f"✓ Configuración mínima guardada en {project_meta_file} y {config_def_file_path}.", style="fg:green")
        # Ahora los archivos existen, permitir que el flujo continúe.
    elif not project_meta_file.is_file() and def_exists and (args.newrepo or args.configure_protection):
        # Si .toml no existe PERO .def SÍ existe, para --newrepo y --configure-protection,
        # debemos crear el .toml a partir del .def antes de proceder.
        questionary.print(f"ℹ️ Archivo {project_meta_file.name} no encontrado. Creándolo desde {config_def_file_path.name}...", style="fg:cyan")
        try:
            initial_data_from_def = load_project_data(config_def_file_path)
            # Validar que el .def tenga un nombre de repositorio válido antes de guardarlo como .toml
            if not initial_data_from_def.get("repository", {}).get("name", "").strip():
                questionary.print(f"✗ Error: {config_def_file_path.name} no tiene un nombre de repositorio válido.", style="fg:red")
                questionary.print(f"  Edite {config_def_file_path.name} o use 'promanager.py --project' para configurarlo.", style="fg:yellow")
                sys.exit(1)
            save_project_data(initial_data_from_def, project_meta_file, project_base_path)
            questionary.print(f"✓ {project_meta_file.name} creado desde {config_def_file_path.name}.", style="fg:green")
        except Exception as e_copy:
            questionary.print(f"✗ Error al crear {project_meta_file.name} desde {config_def_file_path.name}: {e_copy}", style="fg:red")
            sys.exit(1)
    elif not project_meta_file.is_file() and (args.newrepo or args.configure_protection):
        # Este caso (ni .toml ni .def) ya debería estar cubierto arriba, pero por seguridad.
        questionary.print(f"✗ Error: No se encontró el archivo de metadatos del proyecto ({project_meta_file.name}).", style="fg:red")
        questionary.print(f"  Por favor, ejecute 'promanager.py --project' primero para crear y guardar la configuración.", style="fg:yellow")
        sys.exit(1)

    questionary.print(f"Operando en el directorio del proyecto: {project_base_path}")
    # El mensaje de "Operando en..." ahora se muestra DESPUÉS de la posible creación de config.

    # --- Manejar comando --newrepo ---
    if args.newrepo:
        create_remote_repo(project_base_path, args)
        return

    # --- Manejar comando --configure-protection ---
    if args.configure_protection:
        configure_branch_protection(project_base_path, args)
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperación interrumpida por el usuario. Saliendo.")
        try:
            sys.exit(130) # Código de salida estándar para Ctrl+C
        except SystemExit:
            os._exit(130) 