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
        import tomli as tomllib # type: ignore
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
        "allow_direct_push": False,
        "allowed_pr_from": ["hotfix/*", "staging"]
    },
    "develop": {
        "protection_level": "strict",
        "allow_direct_push": False,
        "allowed_pr_from": ["feature/*", "fix/*", "docs/*", "refactor/*", "test/*", "chore/*"]
    },
    "staging": {
        "protection_level": "strict",
        "allow_direct_push": False,
        "allowed_pr_from": ["develop"]
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
        try:
            # Decodificar el token si viene en base64
            try:
                decoded_token = base64.b64decode(token).decode('utf-8')
            except Exception:
                decoded_token = token  # Si no es base64, usar el token tal cual
            
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
            except GithubException as e:
                if e.status == 404:
                    raise ValueError(f"El repositorio {owner}/{repo_name} no existe en GitHub")
                raise
            
        except Exception as e:
            raise ValueError(f"Error inicializando GitHub: {str(e)}")
    
    def configure_branch_protection(self, branch: str, rules: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            # Verificar si la rama existe
            try:
                self.repo.get_branch(branch)
            except GithubException as e:
                if e.status == 404:
                    return False, f"La rama {branch} no existe en el repositorio"
                raise
            
            branch_protection = {
                "required_status_checks": {
                    "strict": True,
                    "contexts": ["ci/check"]
                },
                "enforce_admins": True,
                "required_pull_request_reviews": {
                    "required_approving_review_count": 0
                } if not rules.get("allow_direct_push") else None,
                "restrictions": {
                    "users": ["@maintainers"],
                    "teams": ["@maintainers"]
                } if not rules.get("allow_direct_push") else None
            }
            
            self.repo.get_branch(branch).edit_protection(**branch_protection)
            return True, f"Protección configurada para rama {branch}"
        except Exception as e:
            return False, f"Error configurando protección para {branch}: {str(e)}"
    
    def configure_review_leadership(self, reviewers: List[str], branch_leaders: List[str]) -> Tuple[bool, str]:
        try:
            # Configurar revisores
            if reviewers:
                for reviewer in reviewers:
                    try:
                        self.repo.add_to_collaborators(reviewer, "push")
                    except GithubException as e:
                        if e.status == 404:
                            return False, f"Usuario o equipo {reviewer} no encontrado en GitHub"
                        raise
            
            # Configurar líderes de rama
            if branch_leaders:
                for leader in branch_leaders:
                    try:
                        self.repo.add_to_collaborators(leader, "admin")
                    except GithubException as e:
                        if e.status == 404:
                            return False, f"Usuario o equipo {leader} no encontrado en GitHub"
                        raise
            
            return True, "Liderazgo de revisión configurado"
        except Exception as e:
            return False, f"Error configurando liderazgo: {str(e)}"

def check_and_install_pygithub() -> bool:
    """Verifica si PyGithub está instalado y lo instala si es necesario."""
    try:
        import github
        return True
    except ImportError:
        # Verificar si estamos en un entorno virtual
        in_venv = sys.prefix != sys.base_prefix
        
        if not in_venv:
            questionary.print("Error: No se detectó un entorno virtual Python activo.", style="fg:red")
            questionary.print("Para usar esta funcionalidad, necesitas crear y activar un entorno virtual:", style="fg:yellow")
            questionary.print("  1. Crear entorno: pymanager --create", style="fg:yellow")
            questionary.print("  2. Activar entorno: source .venv/bin/activate", style="fg:yellow")
            return False
        
        # Si estamos en un entorno virtual, intentar instalar PyGithub
        questionary.print("Instalando PyGithub...", style="fg:cyan")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "PyGithub"], 
                         check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            questionary.print(f"Error al instalar PyGithub: {e.stderr}", style="fg:red")
            return False

# Dependencias para GitHub
if not check_and_install_pygithub():
    sys.exit(1)

from github import Github
from github.GithubException import GithubException

# --- Constantes para el Banner ---
APP_NAME = "Gestor de Poryectos de Desarrollo"  # Anteriormente APP_NAME_BANNER
VERSION = "2.0.0"  # Anteriormente SCRIPT_VERSION
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

def save_project_data(data, meta_file_path: Path): # Añadido argumento
    """Guarda los datos en la ruta especificada, creando el directorio si es necesario."""
    project_dir = meta_file_path.parent # Obtener directorio padre
    try:
        project_dir.mkdir(parents=True, exist_ok=True)
        with open(meta_file_path, "wb") as f:
            tomli_w.dump(data, f)
        questionary.print(f"Datos del proyecto guardados en {meta_file_path}", style="fg:green")
    except Exception as e:
        questionary.print(f"Error al guardar {meta_file_path}: {e}", style="fg:red")

def get_default_structure():
    """Retorna la estructura TOML por defecto como diccionario Python."""
    # Mantener claves en inglés para consistencia interna
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
            "title": "", "purpose": "", "status": "planning", "lead": "",
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

        # Preguntar Descripción con validación de longitud
        description = questionary.text(
            "Descripción del Repositorio (máximo 350 caracteres):",
            default=defaults.get("description", ""),
            validate=lambda text: True if len(text) <= 350 else f"La descripción no puede exceder 350 caracteres (actual: {len(text)})"
        ).ask()
        if description is None: return None # Cancelado
        answers['description'] = description

        return answers

    except KeyboardInterrupt:
        # Si se interrumpe en medio de una pregunta
        return None

def edit_repository_info(repo_data, is_initial_setup=False):
    """Formulario para editar info del repo."""
    is_created = repo_data.get("created_flag", False) or repo_data.get("url")

    if is_created:
        questionary.print("--- Info Repositorio (Creado - Campos editables) ---", style="bold")
        questionary.print("Nota: Los campos clave no pueden ser modificados una vez creado el repositorio.", style="fg:yellow")
        questionary.print(f"  Nombre:       {repo_data.get('name', 'N/A')}")
        questionary.print(f"  Propietario:  {repo_data.get('owner_name', 'N/A')} ({repo_data.get('owner_type', 'N/A')})")
        questionary.print(f"  Visibilidad: {repo_data.get('visibility', 'N/A')}")
        platform_display = repo_data.get('platform', 'N/A')
        platform_url_display = repo_data.get('platform_url')
        if platform_url_display:
            platform_display += f" ({platform_url_display})"
        questionary.print(f"  Plataforma:   {platform_display}")
        questionary.print(f"  URL Repo:     {repo_data.get('url', 'No establecido')}")
        
        # Editar campos editables
        description = questionary.text(
            "Descripción:",
            default=repo_data.get('description', "")
        ).ask()
        if description is None: return # Check for cancellation
        repo_data['description'] = description
        
        # Editar opciones de inicialización
        init_options = repo_data.get("init_options", {})
        
        add_readme = questionary.confirm(
            "¿Inicializar con README?",
            default=init_options.get('add_readme', True)
        ).ask()
        if add_readme is None: return # Check for cancellation
        init_options['add_readme'] = add_readme
        
        add_gitignore = questionary.confirm(
            "¿Añadir .gitignore?",
            default=init_options.get('add_gitignore', True)
        ).ask()
        if add_gitignore is None: return # Check for cancellation
        init_options['add_gitignore'] = add_gitignore
        
        if add_gitignore:
            gitignore_template = questionary.text(
                "Plantilla .gitignore (ej., Python, Node, vacío para ninguno):",
                default=init_options.get('gitignore_template', "Python")
            ).ask()
            if gitignore_template is None: return # Check for cancellation
            init_options['gitignore_template'] = gitignore_template
        
        add_license = questionary.confirm(
            "¿Añadir LICENSE?",
            default=init_options.get('add_license', True)
        ).ask()
        if add_license is None: return # Check for cancellation
        init_options['add_license'] = add_license
        
        if add_license:
            license_template = questionary.text(
                "Plantilla Licencia (ID SPDX, ej., mit, gpl-3.0):",
                default=init_options.get('license_template', "mit")
            ).ask()
            if license_template is None: return # Check for cancellation
            init_options['license_template'] = license_template
        
        repo_data["init_options"] = init_options
    else:
        if not is_initial_setup:
            questionary.print("--- Info Repositorio (Campos requeridos *) ---", style="bold")
            questionary.print("Valores actuales:", style="fg:cyan")
            questionary.print(f"  Nombre:       {repo_data.get('name', 'No establecido')}")
            questionary.print(f"  Propietario:  {repo_data.get('owner_name', 'No establecido')} ({repo_data.get('owner_type', 'No establecido')})")
            questionary.print(f"  Visibilidad: {repo_data.get('visibility', 'No establecido')}")
            platform_display = repo_data.get('platform', 'No establecido')
            platform_url_display = repo_data.get('platform_url')
            if platform_url_display:
                platform_display += f" ({platform_url_display})"
            questionary.print(f"  Plataforma:   {platform_display}")
            questionary.print(f"  Descripción: {repo_data.get('description', 'No establecida')}")
            questionary.print("")  # Línea en blanco para separar
            
            answers = prompt_for_required_repo_info(repo_data)
            if not answers: return # User cancelled
            
            # Validar que el nombre no esté vacío
            if not answers.get('name', '').strip():
                questionary.print("Error: El nombre del repositorio no puede estar vacío", style="fg:red")
                return
            
            repo_data.update(answers)
        else:
            questionary.print("--- Info Repositorio (Opciones Adicionales) ---", style="bold")
            questionary.print("Valores actuales:", style="fg:cyan")
            questionary.print(f"  Descripción: {repo_data.get('description', 'No establecida')}")
            questionary.print("")  # Línea en blanco para separar

        description = questionary.text(
            "Descripción:",
            default=repo_data.get('description', "")
        ).ask()
        if description is None: return # Check for cancellation
        repo_data['description'] = description

        init_options = repo_data.get("init_options", {})
        add_readme = questionary.confirm(
            "¿Inicializar con README?",
            default=init_options.get('add_readme', True)
        ).ask()
        if add_readme is None: return # Check for cancellation
        init_options['add_readme'] = add_readme

        add_gitignore = questionary.confirm(
            "¿Añadir .gitignore?",
            default=init_options.get('add_gitignore', True)
        ).ask()
        if add_gitignore is None: return # Check for cancellation
        init_options['add_gitignore'] = add_gitignore

        if add_gitignore:
            gitignore_template = questionary.text(
                "Plantilla .gitignore (ej., Python, Node, vacío para ninguno):",
                default=init_options.get('gitignore_template', "Python")
            ).ask()
            if gitignore_template is None: return # Check for cancellation
            init_options['gitignore_template'] = gitignore_template

        add_license = questionary.confirm(
            "¿Añadir LICENSE?",
            default=init_options.get('add_license', True)
        ).ask()
        if add_license is None: return # Check for cancellation
        init_options['add_license'] = add_license

        if add_license:
            license_template = questionary.text(
                "Plantilla Licencia (ID SPDX, ej., mit, gpl-3.0):",
                default=init_options.get('license_template', "mit")
            ).ask()
            if license_template is None: return # Check for cancellation
            init_options['license_template'] = license_template

        repo_data["init_options"] = init_options


def edit_project_details(details_data):
    """Formulario para editar detalles del proyecto."""
    questionary.print("--- Detalle del Proyecto ---", style="bold")
    details_data['title'] = questionary.text("Título del Proyecto:", default=details_data.get('title', "")).ask() or details_data.get('title', "")
    if details_data['title'] is None: return
    details_data['purpose'] = questionary.text("Propósito/Descripción:", default=details_data.get('purpose', "")).ask() or details_data.get('purpose', "")
    if details_data['purpose'] is None: return
    details_data['status'] = questionary.select("Estado:", choices=STATUS_CHOICES, default=details_data.get('status', "planning")).ask()
    if details_data['status'] is None: return
    details_data['lead'] = questionary.text("Líder del Proyecto:", default=details_data.get('lead', "")).ask() or details_data.get('lead', "")
    if details_data['lead'] is None: return

    # PM Tool Info
    pm_info = details_data.get("pm_tool_info", {})
    pm_info['tool_name'] = questionary.text("Herramienta Gestión Proyectos (Jira, Trello, etc., vacío si ninguna):", default=pm_info.get('tool_name', "")).ask() or pm_info.get('tool_name', "")
    if pm_info['tool_name'] is None: return
    pm_info['project_link'] = questionary.text("URL Proyecto (Gestión):", default=pm_info.get('project_link', "")).ask() or pm_info.get('project_link', "")
    if pm_info['project_link'] is None: return
    pm_info['project_key'] = questionary.text("Clave Proyecto (Gestión, si aplica):", default=pm_info.get('project_key', "")).ask() or pm_info.get('project_key', "")
    if pm_info['project_key'] is None: return
    details_data["pm_tool_info"] = pm_info

    # Editar listas (simplificado por ahora, solo muestra)
    # TODO: Implementar edición de listas (add/remove/edit)
    questionary.print(f"Objetivos: {details_data.get('objectives', [])} (Editar manualmente o mejorar script)")
    questionary.print(f"Interesados: {details_data.get('stakeholders', [])} (Editar manualmente o mejorar script)")
    questionary.print(f"Stack Tecnológico: {details_data.get('technology_stack', [])} (Editar manualmente o mejorar script)")
    # ... etc para risks, assumptions

    # Constraints
    constraints = details_data.get("constraints", {})
    constraints['budget'] = questionary.text("Restricción Presupuesto:", default=constraints.get('budget', 'TBD')).ask() or constraints.get('budget', 'TBD')
    if constraints['budget'] is None: return
    constraints['timeline'] = questionary.text("Restricción Cronograma:", default=constraints.get('timeline', 'TBD')).ask() or constraints.get('timeline', 'TBD')
    if constraints['timeline'] is None: return
    details_data["constraints"] = constraints


def edit_additional_metadata(metadata_data, meta_file_path: Path): # Añadido argumento
     """Abre el archivo TOML en el editor para metadatos adicionales."""
     editor = os.environ.get('EDITOR', 'vim')
     project_dir = meta_file_path.parent # Obtener directorio padre
     questionary.print(f"Abriendo {meta_file_path} en {editor} para editar la sección [additional_metadata].", style="fg:cyan")
     questionary.print("Guarda el archivo en el editor y luego pulsa Enter aquí para recargar.")
     try:
         project_dir.mkdir(parents=True, exist_ok=True)
         # --- Ejecutar editor ---
         status_code = os.system(f"{editor} '{meta_file_path}'") # Añadir comillas por si la ruta tiene espacios
         if status_code != 0:
              questionary.print(f"Comando del editor finalizó con estado {status_code}.", style="fg:cyan")

         # --- Recargar ---
         # Usamos la función de carga global pasándole la ruta
         # Usar try-except básico aquí por si el archivo está mal editado
         try:
             # Pausa breve antes de intentar leer, puede ayudar en algunos sistemas
             import time
             time.sleep(0.2)
             reloaded_data = load_project_data(meta_file_path)
             return reloaded_data.get("additional_metadata", {})
         except Exception as load_err:
             questionary.print(f"Error recargando tras edición: {load_err}", style="fg:red")
             questionary.print("Ediciones manuales podrían ser inválidas. Manteniendo metadatos previos.")
             return metadata_data # Devolver la versión anterior

     except Exception as e:
         questionary.print(f"Error abriendo editor o recargando: {e}", style="fg:red")
         return metadata_data # Devolver sin cambios


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

def push_branches_to_remote() -> Tuple[bool, str]:
    """Realiza push de las ramas existentes al repositorio remoto.
    
    Ramas que se intentan hacer push:
    - main (siempre)
    - develop (si existe)
    - staging (si existe)
    """
    try:
        # Obtener lista de ramas locales
        result = subprocess.run(['git', 'branch', '--format=%(refname:short)'], 
                              capture_output=True, text=True, check=True)
        local_branches = result.stdout.strip().split('\n')
        
        # Hacer push de main primero
        questionary.print("Haciendo push de la rama main...", style="fg:cyan")
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        
        # Hacer push de develop si existe
        if 'develop' in local_branches:
            questionary.print("Haciendo push de la rama develop...", style="fg:cyan")
            subprocess.run(['git', 'push', '-u', 'origin', 'develop'], check=True)
        
        # Hacer push de staging si existe
        if 'staging' in local_branches:
            questionary.print("Haciendo push de la rama staging...", style="fg:cyan")
            subprocess.run(['git', 'push', '-u', 'origin', 'staging'], check=True)
        
        return True, "Ramas subidas exitosamente al repositorio remoto"
        
    except subprocess.CalledProcessError as e:
        return False, f"Error al hacer push de las ramas: {e.stderr}"
    except Exception as e:
        return False, f"Error inesperado al hacer push: {e}"

def create_github_repository(project_data: Dict[str, Any], token: str, use_https: bool = False) -> Tuple[bool, str]:
    """Crea un repositorio en GitHub usando la API.
    
    Args:
        project_data: Datos del proyecto desde el TOML
        token: Token de autenticación de GitHub
        use_https: Si se debe usar HTTPS en lugar de SSH
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    try:
        # 1. CREAR REPOSITORIO EN GITHUB
        g = Github(token)
        repo_data = project_data["repository"]
        repo_name = repo_data.get("name", "").strip()
        
        # Validar nombre del repositorio
        if not repo_name:
            return False, "Error: El nombre del repositorio no puede estar vacío"
        
        description = repo_data.get("description", "")
        private = repo_data.get("visibility", "private") == "private"
        owner_type = repo_data.get("owner_type", "user")
        owner_name = repo_data.get("owner_name", "")
        
        # Determinar el propietario del repositorio
        if owner_type == "organization":
            if not owner_name:
                return False, "Error: Se requiere el nombre de la organización cuando owner_type es 'organization'"
            try:
                owner = g.get_organization(owner_name)
            except GithubException as e:
                return False, f"Error al obtener la organización '{owner_name}': {e}"
        else:  # user
            owner = g.get_user()
        
        # Crear el repositorio
        try:
            repo = owner.create_repo(
                name=repo_name,
                description=description,
                private=private,
                has_issues=True,
                has_wiki=True,
                has_projects=True,
                auto_init=False
            )
        except GithubException as e:
            if e.status == 422 and "name already exists" in str(e.data):
                return False, f"El repositorio '{repo_name}' ya existe en tu cuenta de GitHub. Por favor, elige otro nombre o elimina el repositorio existente."
            raise
        
        # 2. CONFIGURAR REMOTE LOCAL
        if use_https:
            remote_url = repo.clone_url.replace('https://', f'https://{token}@')
        else:
            remote_url = repo.ssh_url
        
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
        
        # 3. INICIALIZAR RAMAS SEGÚN TOML
        protection_config = repo_data.get("protection_config", {})
        branches = protection_config.get("branches", MAIN_BRANCHES)
        
        # Hacer push de main
        questionary.print("Haciendo push de la rama main...", style="fg:cyan")
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        
        # Crear y hacer push de develop si está en la configuración
        if 'develop' in branches:
            questionary.print("Verificando y preparando la rama develop...", style="fg:cyan")
            try:
                # Intentar cambiar a la rama develop si ya existe
                subprocess.run(['git', 'checkout', 'develop'], check=True, capture_output=True, text=True)
                questionary.print("Rama develop ya existe localmente, usando existente.", style="fg:cyan")
            except subprocess.CalledProcessError:
                # Si no existe, crearla
                questionary.print("Creando rama develop localmente...", style="fg:cyan")
                subprocess.run(['git', 'checkout', '-b', 'develop'], check=True)
            
            questionary.print("Haciendo push de la rama develop...", style="fg:cyan")
            subprocess.run(['git', 'push', '-u', 'origin', 'develop', '--force'], check=True)
            
            # Intentar cambiar a main, manejando cambios sin guardar si es necesario
            try:
                questionary.print("Intentando cambiar a la rama main...", style="fg:cyan")
                subprocess.run(['git', 'checkout', 'main'], check=True, capture_output=True, text=True)
                questionary.print("✓ Cambio a rama main exitoso.", style="fg:green")
            except subprocess.CalledProcessError as e:
                if e.returncode == 1 and ("serán sobrescritos por checkout" in e.stderr.lower() or "commit con los cambios o un stash" in e.stderr.lower()):
                    questionary.print("Detectados cambios sin guardar en 'develop'. Guardando automáticamente...", style="fg:yellow")
                    try:
                        subprocess.run(['git', 'add', '.'], check=True)
                        subprocess.run(['git', 'commit', '-m', '[CHORE] Salvaguarda cambios en develop antes de cambiar a main'], check=True)
                        questionary.print("✓ Cambios guardados en 'develop'. Reintentando cambio a 'main'...", style="fg:green")
                        subprocess.run(['git', 'checkout', 'main'], check=True) # Reintentar checkout
                        questionary.print("✓ Cambio a rama main exitoso después de guardar cambios.", style="fg:green")
                    except subprocess.CalledProcessError as commit_e:
                        # Si falla el commit o el segundo checkout, retornamos el error.
                        error_message = f"Error al intentar guardar cambios automáticamente en 'develop' o al cambiar a 'main' después: {commit_e.stderr or commit_e}"
                        questionary.print(error_message, style="fg:red")
                        return False, error_message
                else:
                    # Si es otro error durante el checkout, lo relanzamos para que sea capturado por el try/except principal de la función
                    raise
        
        # 4. APLICAR PROTECCIONES SEGÚN TOML
        questionary.print("Configurando protección de ramas...", style="fg:cyan")
        
        for branch_name, branch_rules in branches.items():
            try:
                protection = {
                    "required_status_checks": {
                        "strict": True,
                        "contexts": ["ci/check"]
                    },
                    "enforce_admins": True,
                    "required_pull_request_reviews": {
                        "required_approving_review_count": 1,
                        "dismiss_stale_reviews": True,
                        "require_code_owner_reviews": branch_name == "main"
                    } if not branch_rules.get("allow_direct_push", False) else None,
                    "restrictions": None  # Permitir push a administradores
                }
                
                repo.get_branch(branch_name).edit_protection(**protection)
                questionary.print(f"✓ Protección configurada para rama {branch_name}", style="fg:green")
            except GithubException as e:
                questionary.print(f"Advertencia: No se pudo configurar la protección para {branch_name}: {e}", style="fg:yellow")
        
        return True, f"Repositorio creado exitosamente en: {repo.html_url}"
        
    except GithubException as e:
        return False, f"Error en la API de GitHub: {e}"
    except Exception as e:
        return False, f"Error inesperado: {e}"

def create_gitlab_repository(project_data: Dict[str, Any], token: str, use_https: bool = False) -> Tuple[bool, str]:
    """Crea un repositorio en GitLab usando la API."""
    # TODO: Implementar soporte para GitLab
    return False, "Soporte para GitLab aún no implementado"

def create_gitea_repository(project_data: Dict[str, Any], token: str, use_https: bool = False) -> Tuple[bool, str]:
    """Crea un repositorio en Gitea usando la API."""
    # TODO: Implementar soporte para Gitea
    return False, "Soporte para Gitea aún no implementado"

def validate_repository_data(project_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida que todos los datos obligatorios para crear un repositorio existan y sean válidos.
    
    Args:
        project_data: Diccionario con los datos del proyecto
        
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    repo_data = project_data.get("repository", {})
    
    # 1. Validar nombre del repositorio
    repo_name = repo_data.get("name", "").strip()
    if not repo_name:
        return False, "Error: El nombre del repositorio no puede estar vacío"
    
    # 2. Validar tipo de propietario
    owner_type = repo_data.get("owner_type", "").lower()
    if not owner_type or owner_type not in ["user", "organization"]:
        return False, "Error: El tipo de propietario debe ser 'user' u 'organization'"
    
    # 3. Validar nombre del propietario si es organización
    if owner_type == "organization":
        owner_name = repo_data.get("owner_name", "").strip()
        if not owner_name:
            return False, "Error: Se requiere el nombre de la organización cuando owner_type es 'organization'"
    
    # 4. Validar visibilidad
    visibility = repo_data.get("visibility", "").lower()
    if not visibility or visibility not in ["private", "public"]:
        return False, "Error: La visibilidad debe ser 'private' o 'public'"
    
    # 5. Validar plataforma
    platform = repo_data.get("platform", "").lower()
    if not platform:
        return False, "Error: No se especificó la plataforma del repositorio"
    
    # 6. Validar URL de plataforma si es requerida
    if platform_requires_url(platform):
        platform_url = repo_data.get("platform_url", "").strip()
        if not platform_url:
            return False, f"Error: Se requiere la URL de la plataforma para {platform}"
    
    return True, "Datos del repositorio validados correctamente"

def create_remote_repo(project_base_path: Path, args: argparse.Namespace) -> None:
    """Función principal para crear un repositorio remoto basado en la plataforma configurada."""
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
    project_meta_file = project_base_path / ".project" / "project_meta.toml"
    if not project_meta_file.is_file():
        questionary.print("Error: No se encontró el archivo de metadatos del proyecto.", style="fg:red")
        questionary.print("Ejecuta primero el comando sin argumentos para crear el proyecto.", style="fg:yellow")
        sys.exit(1)
    
    project_data = load_project_data(project_meta_file)
    
    # 5. Validar datos del repositorio
    is_valid, msg = validate_repository_data(project_data)
    if not is_valid:
        questionary.print(f"Error: {msg}", style="fg:red")
        questionary.print("Por favor, ejecuta 'promanager.py --project' para configurar los datos del repositorio.", style="fg:yellow")
        sys.exit(1)
    questionary.print(msg, style="fg:green")
    
    platform = project_data["repository"].get("platform", "").lower()
    
    # 6. Obtener token
    token = get_token(args, platform)
    if not token:
        sys.exit(1)
    
    # 7. Crear directorio config y copiar TOML como .def
    config_dir = project_base_path / "config"
    config_dir.mkdir(exist_ok=True)
    def_file = config_dir / "project_meta.def"
    try:
        import shutil
        shutil.copy2(project_meta_file, def_file)
        questionary.print(f"✓ Copia de configuración guardada en {def_file}", style="fg:green")
    except Exception as e:
        questionary.print(f"Error al copiar archivo de configuración: {e}", style="fg:red")
        sys.exit(1)
    
    # 8. Crear repositorio según la plataforma
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

def verify_repository_info(repo_data: Dict[str, Any], project_base_path: Path) -> Tuple[bool, str]:
    """Verifica que la información del repositorio en el TOML coincida con el repositorio local.
    
    Args:
        repo_data: Diccionario con la información del repositorio del TOML
        project_base_path: Ruta base del proyecto
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    try:
        # 1. Verificar que es un repositorio git
        result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                              cwd=project_base_path,
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False, "El directorio no es un repositorio git"
        
        # 2. Verificar el remote origin
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                              cwd=project_base_path,
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False, "No hay un remote 'origin' configurado"
        
        remote_url = result.stdout.strip()
        
        # 3. Verificar que la URL coincide con la del TOML
        toml_url = repo_data.get("url", "")
        if toml_url and toml_url != remote_url:
            return False, f"La URL del repositorio en el TOML ({toml_url}) no coincide con el remote origin ({remote_url})"
        
        # 4. Verificar el nombre del repositorio
        repo_name = repo_data.get("name", "")
        if not repo_name:
            return False, "No se especificó el nombre del repositorio en el TOML"
        
        # 5. Verificar que estamos en la rama main
        result = subprocess.run(['git', 'branch', '--show-current'],
                              cwd=project_base_path,
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False, "Error al obtener la rama actual"
        
        current_branch = result.stdout.strip()
        if current_branch != "main":
            return False, f"Debes estar en la rama 'main' para configurar la protección (actual: {current_branch})"
        
        return True, "Información del repositorio verificada correctamente"
        
    except Exception as e:
        return False, f"Error al verificar el repositorio: {str(e)}"

def configure_branch_protection(project_base_path: Path, args: argparse.Namespace) -> None:
    """Configura las reglas de protección de ramas según el tipo de proyecto."""
    # 1. Verificar metadatos
    project_meta_file = project_base_path / ".project" / "project_meta.toml"
    if not project_meta_file.is_file():
        questionary.print("Error: No se encontró el archivo de metadatos del proyecto.", style="fg:red")
        questionary.print("Ejecuta primero el comando sin argumentos para crear el proyecto.", style="fg:yellow")
        sys.exit(1)
    
    project_data = load_project_data(project_meta_file)
    repo_data = project_data.get("repository", {})
    
    # 2. Verificar que es un repositorio Git válido
    is_repo, msg = check_git_repo()
    if not is_repo:
        questionary.print(f"Error: {msg}", style="fg:red")
        sys.exit(1)
    
    # 3. Verificar si existe el repositorio remoto
    has_remote, msg = check_git_remote()
    if not has_remote:
        questionary.print("Error: No hay un repositorio remoto configurado.", style="fg:red")
        questionary.print("Ejecuta '--newrepo' para crear y configurar el repositorio remoto.", style="fg:yellow")
        sys.exit(1)
    
    # 4. Verificar información del repositorio
    success, msg = verify_repository_info(repo_data, project_base_path)
    if not success:
        questionary.print(f"Error: {msg}", style="fg:red")
        sys.exit(1)
    questionary.print(msg, style="fg:green")
    
    # 5. Obtener plataforma del TOML
    platform = repo_data.get("platform", "").lower()
    if not platform:
        questionary.print("Error: No se especificó la plataforma en el archivo TOML.", style="fg:red")
        sys.exit(1)
    
    # 6. Obtener token (ahora obligatorio)
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
    
    # 7. Actualizar configuración en el TOML
    if "protection_config" not in repo_data:
        repo_data["protection_config"] = {}
    
    # Determinar si es proyecto de equipo
    is_team_project = args.team if args.team is not None else not repo_data["protection_config"].get("single_developer", True)
    
    # Obtener revisores y líderes
    reviewers = args.reviewers.split(",") if args.reviewers else repo_data["protection_config"].get("reviewers", [])
    branch_leaders = args.branch_leaders.split(",") if args.branch_leaders else repo_data["protection_config"].get("branch_leaders", [])
    
    # Actualizar configuración en el TOML
    repo_data["protection_config"].update({
        "single_developer": not is_team_project,
        "reviewers": reviewers,
        "branch_leaders": branch_leaders,
        "branches": MAIN_BRANCHES,
        "work_branches": BRANCH_TYPES
    })
    
    # Guardar cambios en el TOML
    save_project_data(project_data, project_meta_file)
    questionary.print("✓ Configuración de protección guardada en project_meta.toml", style="fg:green")
    
    # 8. Aplicar la configuración en el repositorio
    try:
        if platform == "github":
            configurator = GitHubConfigurator(project_data, token)
        elif platform == "gitlab.com" or platform == "gitlab (auto-alojado)":
            # TODO: Implementar GitLabConfigurator
            questionary.print("Soporte para GitLab aún no implementado", style="fg:yellow")
            sys.exit(1)
        elif platform == "gitea":
            # TODO: Implementar GiteaConfigurator
            questionary.print("Soporte para Gitea aún no implementado", style="fg:yellow")
            sys.exit(1)
        else:
            questionary.print(f"Error: La plataforma '{platform}' no está soportada actualmente.", style="fg:red")
            sys.exit(1)
    except ValueError as e:
        questionary.print(f"Error: {str(e)}", style="fg:red")
        sys.exit(1)
    except Exception as e:
        questionary.print(f"Error inesperado: {str(e)}", style="fg:red")
        sys.exit(1)
    
    # 9. Configurar protección de ramas principales
    for branch, rules in MAIN_BRANCHES.items():
        # Ajustar reglas según si es proyecto de equipo o no
        branch_rules = rules.copy()
        if not is_team_project:
            branch_rules["allow_direct_push"] = True
            branch_rules["required_pull_request_reviews"] = None
        
        success, msg = configurator.configure_branch_protection(branch, branch_rules)
        if success:
            questionary.print(f"✓ {msg}", style="fg:green")
        else:
            questionary.print(f"✗ {msg}", style="fg:red")
    
    # 10. Configurar revisores y líderes si se especificaron
    if reviewers or branch_leaders:
        success, msg = configurator.configure_review_leadership(reviewers, branch_leaders)
        if success:
            questionary.print(f"✓ {msg}", style="fg:green")
        else:
            questionary.print(f"✗ {msg}", style="fg:red")

def initialize_project_structure(project_base_path: Path) -> bool:
    """Inicializa la estructura del proyecto verificando y creando los directorios y archivos necesarios.
    
    Args:
        project_base_path: Ruta base del proyecto
        
    Returns:
        bool: True si la inicialización fue exitosa, False si hay error
    """
    try:
        # Crear directorio .project si no existe
        project_dir = project_base_path / ".project"
        project_dir.mkdir(exist_ok=True)
        
        # Verificar si existe project_meta.toml
        meta_file = project_dir / "project_meta.toml"
        if not meta_file.exists():
            # Primero verificar si existe config/project_meta.def
            def_file = project_base_path / "config" / "project_meta.def"
            if def_file.exists():
                # Si existe .def, copiarlo a .toml
                import shutil
                shutil.copy2(def_file, meta_file)
                questionary.print("✓ Configuración del proyecto restaurada desde config/project_meta.def", style="fg:green")
                return True
            else:
                # Si no existe .def, solicitar datos obligatorios
                questionary.print("Creando nueva configuración del proyecto...", style="fg:cyan")
                project_data = get_default_structure()
                
                # Solicitar datos obligatorios
                questionary.print("\n--- Configuración Inicial del Repositorio (Campos Obligatorios) ---", style="bold")
                answers = prompt_for_required_repo_info(project_data["repository"])
                if not answers:
                    questionary.print("Operación cancelada por el usuario.", style="fg:yellow")
                    sys.exit(0)
                
                # Validar que el nombre no esté vacío
                if not answers.get('name', '').strip():
                    questionary.print("Error: El nombre del repositorio no puede estar vacío", style="fg:red")
                    sys.exit(1)
                
                # Actualizar datos del repositorio
                project_data["repository"].update(answers)
                
                # Solicitar descripción
                description = questionary.text(
                    "Descripción del Repositorio:",
                    default=""
                ).ask()
                if description is None:
                    questionary.print("Operación cancelada por el usuario.", style="fg:yellow")
                    sys.exit(0)
                project_data["repository"]["description"] = description
                
                # Solicitar detalles del proyecto
                questionary.print("\n--- Detalles del Proyecto ---", style="bold")
                project_data["project_details"]["title"] = questionary.text(
                    "Título del Proyecto:",
                    default=""
                ).ask() or ""
                if project_data["project_details"]["title"] is None:
                    questionary.print("Operación cancelada por el usuario.", style="fg:yellow")
                    sys.exit(0)
                
                project_data["project_details"]["purpose"] = questionary.text(
                    "Propósito/Descripción del Proyecto:",
                    default=""
                ).ask() or ""
                if project_data["project_details"]["purpose"] is None:
                    questionary.print("Operación cancelada por el usuario.", style="fg:yellow")
                    sys.exit(1)
                
                # Confirmar guardar
                if not questionary.confirm("¿Guardar la configuración del proyecto?").ask():
                    questionary.print("Operación cancelada por el usuario.", style="fg:yellow")
                    sys.exit(0)
                
                # Crear directorio config si no existe
                config_dir = project_base_path / "config"
                config_dir.mkdir(exist_ok=True)
                
                # Guardar en ambos archivos
                save_project_data(project_data, meta_file)
                save_project_data(project_data, config_dir / "project_meta.def")
                
                questionary.print("\n✓ Configuración del proyecto guardada exitosamente.", style="fg:green")
                questionary.print("✓ Archivo project_meta.toml creado en .project/", style="fg:green")
                questionary.print("✓ Archivo project_meta.def creado en config/", style="fg:green")
        
        return True
    except Exception as e:
        questionary.print(f"Error al inicializar la estructura del proyecto: {e}", style="fg:red")
        return False

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
  %(prog)s --configure-protection --team --reviewers "user1,user2"
  %(prog)s --configure-protection --branch-leaders "user1,user2"

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
    
    # Parsear argumentos. Si no hay argumentos, mostrar help y salir
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
        
    args = parser.parse_args()
    # ------------------------------------------

    # --- Definir rutas basadas en el argumento ---
    project_base_path = Path(args.path).resolve() # Resuelve a ruta absoluta
    
    # Inicializar estructura del proyecto
    if not initialize_project_structure(project_base_path):
        sys.exit(1)
        
    project_meta_dir = project_base_path / ".project"
    project_meta_file = project_meta_dir / "project_meta.toml"

    questionary.print(f"Operando en el directorio del proyecto: {project_base_path}")
    # ------------------------------------------

    # --- Manejar comando --project ---
    if args.project:
        # Crear directorio .project si no existe
        project_meta_dir.mkdir(exist_ok=True)
        
        # Si el archivo no existe, crear uno nuevo
        if not project_meta_file.is_file():
            # Intentar copiar desde config/project_meta.def
            def_file = project_base_path / "config" / "project_meta.def"
            if def_file.exists():
                import shutil
                shutil.copy2(def_file, project_meta_file)
                questionary.print("✓ Configuración del proyecto restaurada desde config/project_meta.def", style="fg:green")
            else:
                # Si no existe .def, solicitar datos obligatorios
                questionary.print("Creando nueva configuración del proyecto...", style="fg:cyan")
                project_data = get_default_structure()
                
                # Solicitar datos obligatorios antes de crear el archivo
                questionary.print("\n--- Configuración Inicial del Repositorio (Campos Obligatorios) ---", style="bold")
                answers = prompt_for_required_repo_info(project_data["repository"])
                if not answers:
                    questionary.print("Operación cancelada por el usuario.", style="fg:yellow")
                    sys.exit(0)
                
                # Validar que el nombre no esté vacío
                if not answers.get('name', '').strip():
                    questionary.print("Error: El nombre del repositorio no puede estar vacío", style="fg:red")
                    sys.exit(1)
                
                # Actualizar datos del repositorio
                project_data["repository"].update(answers)
                
                # Solicitar descripción
                description = questionary.text(
                    "Descripción del Repositorio:",
                    default=""
                ).ask()
                if description is None:
                    questionary.print("Operación cancelada por el usuario.", style="fg:yellow")
                    sys.exit(0)
                project_data["repository"]["description"] = description
                
                # Solicitar detalles del proyecto
                questionary.print("\n--- Detalles del Proyecto ---", style="bold")
                project_data["project_details"]["title"] = questionary.text(
                    "Título del Proyecto:",
                    default=""
                ).ask() or ""
                if project_data["project_details"]["title"] is None:
                    questionary.print("Operación cancelada por el usuario.", style="fg:yellow")
                    sys.exit(0)
                
                project_data["project_details"]["purpose"] = questionary.text(
                    "Propósito/Descripción del Proyecto:",
                    default=""
                ).ask() or ""
                if project_data["project_details"]["purpose"] is None:
                    questionary.print("Operación cancelada por el usuario.", style="fg:yellow")
                    sys.exit(1)
                
                # Guardar la configuración inicial
                save_project_data(project_data, project_meta_file)
                questionary.print("\n✓ Archivo project_meta.toml creado exitosamente.", style="fg:green")
                questionary.print("Puedes usar 'promanager.py --project' para editar la configuración más adelante.", style="fg:cyan")
                sys.exit(0)
        
        # Si el archivo existe (ya sea por copia de .def o por creación nueva), entrar al menú de edición
        project_data = load_project_data(project_meta_file)
        original_data_str = str(project_data)
        modified = False

        while True:
            try:
                current_data_str = str(project_data)
                modified = (current_data_str != original_data_str)
                prompt_title = "Selecciona acción:" + (" (Hay cambios sin guardar)" if modified else "")

                action = questionary.select(
                    prompt_title,
                    choices=[
                        "Editar Info Repositorio",
                        "Editar Detalles Proyecto",
                        "Editar Metadatos Adicionales (Manual)",
                        "Guardar Cambios",
                        "Salir (Descartar Cambios)",
                        "Guardar y Salir"
                    ],
                    qmark=">", pointer="->"
                ).ask()
            except KeyboardInterrupt:
                action = None

            if action == "Editar Info Repositorio":
                edit_repository_info(project_data["repository"])
            elif action == "Editar Detalles Proyecto":
                edit_project_details(project_data["project_details"])
            elif action == "Editar Metadatos Adicionales (Manual)":
                new_metadata = edit_additional_metadata(project_data.get("additional_metadata", {}), project_meta_file)
                project_data["additional_metadata"] = new_metadata
            elif action == "Guardar Cambios":
                save_project_data(project_data, project_meta_file)
                original_data_str = str(project_data)
                modified = False
            elif action == "Salir (Descartar Cambios)":
                if modified:
                    confirm_exit = questionary.confirm("¿Descartar cambios sin guardar?").ask()
                    if not confirm_exit:
                        continue
                print("Saliendo.")
                sys.exit(0)
            elif action == "Guardar y Salir":
                save_project_data(project_data, project_meta_file)
                print("Saliendo.")
                sys.exit(0)
            elif action is None:
                if modified:
                    confirm_exit = questionary.confirm("Tienes cambios sin guardar. ¿Salir de todas formas?").ask()
                    if not confirm_exit:
                        continue
                print("Saliendo.")
                sys.exit(0)
        return

    # --- Manejar comando --newrepo ---
    if args.newrepo:
        create_remote_repo(project_base_path, args)
        return

    # --- Manejar comando --configure-protection ---
    if args.configure_protection:
        configure_branch_protection(project_base_path, args)
        return

if __name__ == "__main__":
    # Pequeño ajuste para mejor manejo de interrupciones globales
    try:
        main()
    except KeyboardInterrupt:
        print("Operación interrumpida por el usuario. Saliendo.")
        sys.exit(1) 