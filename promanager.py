#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROMANAGER - Gestor de Proyectos de Desarrollo.

Copyright (C) 2025 MAURO ROSERO PÉREZ
License: GPLv3

File: promanager.py
Version: 0.1.0
Author: Mauro Rosero P. <mauro.rosero@gmail.com>
Assistant: Cursor AI (https://cursor.com)
Created: 2025-05-19 20:56:28

This file is managed by template_manager.py.
Any changes to this header will be overwritten on the next fix.
"""

# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

# Description: Gestor de Metadatos para Proyectos de Desarrollo.

import sys
import os # Para os.system y os.name
import argparse
from typing import Optional
import copy # <--- AÑADIDO para deepcopy
import shutil # <--- AÑADIDO para shutil
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import tomllib
    import tomli_w
except ImportError as e:
    print(f"Error: No se pudo importar un módulo requerido: {e}")
    print("Por favor, asegúrate de tener activado tu entorno virtual (venv) y todas las dependencias necesarias instaladas.")
    sys.exit(1)

# --- Constantes de Aplicación (Según .cursorrules) ---
APP_NAME = "Gestor de Proyectos de Desarrollo" # ACTUALIZADO
VERSION = "0.1.0" # Versión inicial para este nuevo script
AUTHOR = "Mauro Rosero Pérez" # Tomado de tus datos, ajustar si es necesario
BANNER_WIDTH = 80 # Ancho sugerido para el banner

# --- NUEVAS CONSTANTES para Configuración y Estados del Proyecto ---
CONFIG_DIR_NAME = "config"
PROJECT_STATUS_DEF_FILE_NAME = "pmstatus.def"
DEFAULT_PROJECT_STATUSES = [
    "Planificación",
    "Activo",
    "En Espera",
    "Bloqueado",
    "Completado",
    "Cancelado",
    "Archivado",
]
SCRIPT_DEBUG_MODE = os.getenv("PROMANAGER_DEBUG", "false").lower() == "true"
NO_CHANGE_SENTINEL = object() # Mover a global si estaba local, o añadir si no existe

# --- NUEVAS CONSTANTES para Scaffold ---
DEFAULT_SCAFFOLD_TYPE = "No"
SCAFFOLD_TYPES_FILE = "project_types.def"

# --- NUEVAS CONSTANTES para Herramientas de Gestión de Proyectos ---
PM_APPS_DEF_FILE_NAME = "pmapps.def"
DEFAULT_PM_APPS = [
    "Ninguna", "Jira", "Asana", "Trello", "Monday.com", "ClickUp", 
    "GitLab Issues", "GitHub Issues", "Redmine", "OpenProject", 
    "Taiga", "Linear", "Notion", "Airtable", "Other" 
]
# --- FIN NUEVAS CONSTANTES ---

# --- Constantes del Script ---
META_FILE_NAME = ".project/project_meta.toml"
INDENT_STRING = "  " # Dos espacios por nivel de indentación
DEFAULT_SCAFFOLD_TYPE = "No"  # Valor por defecto para scaffold

# --- Constantes Adicionales ---
KNOWN_HOSTED_PLATFORMS = ["GitHub", "gitlab.com", "Bitbucket"] # Plataformas donde la URL es implícita
VALUE_ONLY_KEYS = ["title", "description"] # Claves para las que solo se muestra el valor (si es string)

# --- Nuevo: Opciones Predefinidas para Ciertas Claves ---
PREDEFINED_CHOICES_FOR_KEYS = {
    "owner_type": ["user", "organization"],
    "visibility": ["public", "private", "internal"], # 'internal' es una suposición, ajustar si es necesario
    "platform": ["GitHub", "gitlab.com", "GitLab", "Bitbucket", "Gitea", "Forgejo", "Other"], # Se usa 'Other' para indicar auto-hospedado u otro no listado
    "status": [], # NUEVO: Se llenará dinámicamente desde pmstatus.def
    "tool_name": [], # NUEVO: Se llenará dinámicamente desde pmapps.def
    "license_template": ["MIT", "GPL-3.0-only", "Apache-2.0", "BSD-3-Clause", "unlicensed", "Other"], # Lista de ejemplo de SPDX IDs comunes + Other
    "gitignore_template": ["Python", "Node", "Java", "VisualStudio", "Ruby", "None", "Other"], # NUEVA LISTA DE EJEMPLO
}

# --- Nuevo: Claves de Repositorio Editables Cuando created_flag es True ---
EDITABLE_REPO_KEYS_WHEN_CREATED = ["visibility", "description", "license_template"]
# Considerar si 'tags' o algo de 'project_details' debería ser editable post-creación también.

# --- Nuevo: Claves de Project Details de solo lectura cuando pm_tool_created_flag es True ---
PROJECT_DETAILS_READONLY_WHEN_PM_TOOL_CREATED = [
    "title", "purpose", "status", "lead", "lead_email"
]

# Mapeo de nombres de sección a español para la interfaz de usuario
SECTION_NAME_MAP_ES = {
    "repository": "Información del Repositorio (General)",
    "project_details": "Detalles del Proyecto",
    "additional_metadata": "Metadatos Adicionales",
    "protection_config": "Reglas de Protección de Ramas",
    "workflow_config": "Flujo de Trabajo CI",  # NUEVA SECCIÓN
}

# Diccionario inverso para mapear de español a clave original
ES_TO_KEY_MAP = {v: k for k, v in SECTION_NAME_MAP_ES.items()}

# --- Nuevo: Mapa de Traducción para Claves Internas de Secciones ---
KEY_TRANSLATION_MAP_ES = {
    "repository": { # Clave original de la sección
        "name": "Nombre del Repositorio", # AÑADIDO
        "description": "Descripción del Repositorio", # AÑADIDO
        "owner_name": "Propietario", # Se filtrará en la vista detallada si es necesario
        "owner_type": "Tipo de Propietario",
        "visibility": "Visibilidad",
        "platform": "Plataforma",
        "platform_url": "URL Plataforma",
        "created_flag": "Repositorio Creado",  # MODIFICADO
        "url": "URL Repositorio (Git)",
        "init_options": "Opciones de Inicialización",
        # Claves dentro de init_options (deben estar a este nivel para ser encontradas)
        "add_readme": "Añadir README",
        "add_gitignore": "Añadir .gitignore",
        "gitignore_template": "Plantilla .gitignore",
        "add_license": "Añadir Licencia",
        "license_template": "Plantilla de Licencia",
        "scaffold": "Estructura Inicial",  # AÑADIDO
        "initialized": "Inicializado",  # AÑADIDO
        # 'name' y 'description' se manejan fuera de este scope para 'repository'
    },
    "project_details": { # ACTUALIZADO COMPLETAMENTE
        "title": "Título del Proyecto", # Asegurarse que esté si se usa como VALUE_ONLY_KEY
        "purpose": "Propósito Principal",
        "status": "Estado del Proyecto", # Clave 'status' (antes project_status)
        "tags": "Etiquetas (separadas por coma)",  # Se mantiene ya que es un campo útil para metadata
        "target_audience": "Público Objetivo",
        "lead": "Líder del Proyecto",
        "lead_email": "Email del Líder",
        "pm_tool_info": "Info. Herramienta Gestión de Proyectos",
        "tool_name": "Nombre Herramienta PM", # Anidada bajo pm_tool_info
        "project_link": "Enlace Proyecto (PM Tool)", # Anidada bajo pm_tool_info
        "project_key": "Clave Proyecto (PM Tool)", # Anidada bajo pm_tool_info
        "pm_tool_created_flag": "Proyecto Creado en Herramienta PM", # NUEVO


    },
    "additional_metadata": {
        # Las claves aquí suelen ser dinámicas, pero podemos poner ejemplos
        # "custom_key_1": "Valor Personalizado 1",
    },
    "protection_config": {
        "default_branch": "Rama por Defecto (del repo)",
        "main_branches": "Configuración Ramas Principales Protegidas", # El valor es un dict
        "work_branches": "Configuración de Ramas de Trabajo", # El valor es un dict
        
        # Nuevas claves directas bajo protection_config
        "single_developer": "Desarrollador Único",
        "reviewers": "Revisores (Usuarios/Equipos)",
        "branch_leaders": "Líderes de Rama (Usuarios/Equipos)",
        "branches": "Configuración Específica por Rama Principal", # Contiene main, develop, etc.

        # Claves comunes DENTRO de cada rama principal (ej. protection_config.branches.main.ESTA_CLAVE)
        "protection_level": "Nivel de Protección",
        "allow_direct_push": "Permitir Push Directo", # Reutilizable
        "allowed_pr_from": "PRs Permitidos Desde",
        "enforce_admins": "Forzar Reglas para Admins",

        # Claves comunes DENTRO de cada tipo de rama de trabajo (ej. protection_config.work_branches.feature.ESTA_CLAVE)
        "pattern": "Patrón de Nombre",
        "description": "Descripción", # Ya en VALUE_ONLY_KEYS, se mostrará solo el valor
        "target_branch": "Rama(s) Destino para Fusión",
        # "allow_direct_push" ya está arriba,
        # "strict_naming" y "auto_delete_merged" eran para work_branches en general, no por tipo.
        # Ajusto las de work_branches que estaban antes, pueden ser a nivel general de work_branches si existen ahí.
        "prefix": "Prefijo Ramas de Trabajo (General)", # Si aplica a work_branches directamente
        "strict_naming": "Nomenclatura Estricta (Ramas Trabajo - General)", # Si aplica a work_branches directamente
        "auto_delete_merged": "Auto-eliminar fusionadas (General)", # Si aplica a work_branches directamente
    },
    "workflow_config": {  # NUEVA ENTRADA PARA WORKFLOW_CONFIG
        "commit_format": "Formato de Commits",
        "require_issue": "Requiere Issue Asociado",
        "require_issue_format": "Valida Formato de Issue",
        "require_component_docs": "Requiere Docs de Componente (docs/[componente].md)",
        "require_parseable_metadata": "Requiere Metadatos Parseables en README",
        "require_version_placeholder": "Requiere Placeholder de Versión en README",
        "require_tests_new_features": "Requiere Tests para Nuevas Funcionalidades/Correcciones",
        "require_linting": "Requiere Validación de Estilo (Linting)",
        "require_type_hints": "Requiere Type Hints (Python)",
        "release_process": "Proceso de Release Definido",
        "require_versioning": "Requiere Versionado (según CONTRIBUTING.md)",
        "require_changelog": "Requiere Registro de Cambios (Changelog)"
    }
    # Se pueden añadir más secciones y sus claves aquí
}

# --- Configuración de Colorama (ya debería estar en el esqueleto original) ---
try:
    from colorama import Fore, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
    # La inicialización se hace en show_banner o al inicio de main si es necesario globalmente
    # Para asegurar que esté activa antes de _print_node, llamaremos a colorama_init()
    # explícitamente si no lo hace show_banner. show_banner lo hace.
except ImportError:
    COLORAMA_AVAILABLE = False
    class DummyColorama:
        def __getattr__(self, name): return ""
    Fore = Style = DummyColorama()

# --- Opcional: Questionary ---
try:
    import questionary
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False
    # Definir un mock de questionary si no está disponible para evitar errores
    # en la lógica que podría intentar acceder a él, aunque lo ideal es evitar
    # llamar a sus funciones si QUESTIONARY_AVAILABLE es False.
    class DummyQuestionary:
        def select(self, *args, **kwargs): return self # Devolver algo para que no falle el .ask()
        def ask(self, *args, **kwargs): return None # Simular cancelación
        def confirm(self, *args, **kwargs): return self
    questionary = DummyQuestionary()

# --- Funciones de Banner (Según .cursorrules) ---
def clear_screen():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner(schema_version_val: Optional[str] = None, config_file_name: Optional[str] = None, project_name_val: Optional[str] = None):
    """Muestra el banner de la aplicación, opcionalmente con info de proyecto, esquema y config."""
    if COLORAMA_AVAILABLE:
        colorama_init(autoreset=True)
    clear_screen()
    
    banner_lines = [
        "=" * BANNER_WIDTH,
        f"{APP_NAME} - Versión {VERSION}".center(BANNER_WIDTH),
        f"Autor: {AUTHOR}".center(BANNER_WIDTH),
        "=" * BANNER_WIDTH,
    ]
    print("\n".join(banner_lines))

    # Construir la línea de información adicional
    info_line_parts = []
    if project_name_val:
        info_line_parts.append(f"{Style.BRIGHT}{Fore.BLUE}[{project_name_val}]{Style.RESET_ALL}")
    if schema_version_val:
        info_line_parts.append(f"{Style.DIM}Esquema: {Style.NORMAL}{Fore.YELLOW}{schema_version_val}{Style.RESET_ALL}")
    
    # Solo mostrar Config si el archivo existe en .project
    if config_file_name:
        meta_file_path = Path(".") / ".project" / config_file_name
        if meta_file_path.exists():
            info_line_parts.append(f"{Style.DIM}Config: {Style.NORMAL}{Fore.YELLOW}{config_file_name}{Style.RESET_ALL}")
    
    if info_line_parts:
        print(f"  {"  ".join(info_line_parts)}") # Unir partes con doble espacio
        
    print() # Línea vacía después del banner e info adicional

# --- Nueva función para imprimir la descripción del repositorio ---
def _print_repository_description(description: Optional[str]):
    if not description:
        return
    
    print(f"  {Style.DIM}Descripción del Repositorio:{Style.RESET_ALL}")
    for line in description.splitlines():
        print(f"    {Fore.GREEN}{line}{Style.RESET_ALL}")
    print() # Línea vacía después de la descripción

# --- Funciones Principales de Gestión del TOML ---

def get_meta_file_path(project_base_path: Path = Path(".")) -> Path:
    """Devuelve la ruta absoluta al archivo project_meta.toml."""
    return project_base_path.resolve() / META_FILE_NAME

def load_project_data(meta_file_path: Path) -> dict:
    """
    Carga los datos del proyecto desde el archivo TOML especificado.
    Devuelve un diccionario vacío si el archivo no existe o hay un error.
    """
    # --- INICIO DE LA MODIFICACIÓN ---
    # Asegurar que el directorio .project (padre de meta_file_path) exista
    try:
        meta_file_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        # Opcional: Manejo de error si la creación del directorio falla.
        # print(f"Advertencia: No se pudo crear el directorio '{meta_file_path.parent}': {e}", file=sys.stderr)
        pass 
    # --- FIN DE LA MODIFICACIÓN ---

    if not meta_file_path.exists():
        # Esta es tu lógica de mensaje existente, se mantiene.
        print(f"Advertencia: El archivo de metadatos '{meta_file_path}' no existe.", file=sys.stderr)
        return {} 
    
    # Si el archivo existe, procedemos a intentar leerlo (código existente)
    try:
        with open(meta_file_path, "rb") as f:
            data = tomllib.load(f)
        return data
    except tomllib.TOMLDecodeError as e:
        print(f"Error al parsear el archivo TOML '{meta_file_path}': {e}", file=sys.stderr)
        return {}
    except IOError as e:
        print(f"Error al leer el archivo '{meta_file_path}': {e}", file=sys.stderr)
        return {}

def save_project_data(data: dict, meta_file_path: Path) -> bool:
    """
    Guarda los datos del proyecto en el archivo TOML especificado.
    Devuelve True si fue exitoso, False en caso contrario.
    """
    try:
        meta_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(meta_file_path, "wb") as f:
            tomli_w.dump(data, f)
        # Eliminamos el mensaje redundante de aquí
        return True
    except IOError as e:
        print(f"Error al escribir en el archivo '{meta_file_path}': {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error inesperado al guardar los datos: {e}", file=sys.stderr)
        return False

# --- NUEVAS FUNCIONES para Cargar Estados del Proyecto ---

def get_config_dir_path(project_base_path: Path = Path(".")) -> Path:
    """Devuelve la ruta absoluta al directorio de configuración del script."""
    script_dir = Path(__file__).parent.resolve()
    return script_dir / CONFIG_DIR_NAME

def get_project_statuses_file_path(config_dir_path: Path) -> Path:
    """Devuelve la ruta absoluta al archivo de definición de estados del proyecto."""
    return config_dir_path / PROJECT_STATUS_DEF_FILE_NAME

def load_project_statuses(debug_mode: bool = False) -> list[str]:
    """
    Carga la lista de estados del proyecto desde el archivo pmstatus.def.
    Si el archivo no existe, lo crea con valores predeterminados.
    Si está vacío o hay un error al leerlo, usa DEFAULT_PROJECT_STATUSES.
    """
    config_dir = get_config_dir_path()
    statuses_file = get_project_statuses_file_path(config_dir)

    # --- NUEVO: Crear archivo .def si no existe ---
    if not statuses_file.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(statuses_file, "w", encoding="utf-8") as f:
                for status in DEFAULT_PROJECT_STATUSES:
                    f.write(f"{status}\n")
            if COLORAMA_AVAILABLE and debug_mode:
                print(f"  {Style.DIM}[DEBUG] Archivo '{statuses_file.name}' no encontrado. Creado con valores predeterminados.{Style.RESET_ALL}")
            elif debug_mode:
                print(f"  [DEBUG] Archivo '{statuses_file.name}' no encontrado. Creado con valores predeterminados.")
        except Exception as e:
            if COLORAMA_AVAILABLE and debug_mode:
                print(f"  {Style.DIM}[DEBUG] Error al crear '{statuses_file.name}' con valores predeterminados: {e}{Style.RESET_ALL}")
            elif debug_mode:
                print(f"  [DEBUG] Error al crear '{statuses_file.name}' con valores predeterminados: {e}")
            # Si falla la creación, se procederá igualmente e intentará cargar (fallará) o usará defaults más abajo.
    # --- FIN NUEVO ---
    
    if COLORAMA_AVAILABLE and debug_mode:
        print(f"  {Style.DIM}[DEBUG] Intentando cargar estados desde: {statuses_file}{Style.RESET_ALL}")
    elif debug_mode:
        print(f"  [DEBUG] Intentando cargar estados desde: {statuses_file}")

    if statuses_file.exists() and statuses_file.is_file():
        try:
            with open(statuses_file, "r", encoding="utf-8") as f:
                statuses = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
            if statuses:
                if COLORAMA_AVAILABLE and debug_mode:
                    print(f"  {Style.DIM}[DEBUG] Estados cargados desde archivo: {statuses}{Style.RESET_ALL}")
                elif debug_mode:
                    print(f"  [DEBUG] Estados cargados desde archivo: {statuses}")
                return statuses
            else:
                if COLORAMA_AVAILABLE and debug_mode:
                    print(f"  {Style.DIM}[DEBUG] Archivo de estados vacío, usando predeterminados.{Style.RESET_ALL}")
                elif debug_mode:
                    print(f"  [DEBUG] Archivo de estados vacío, usando predeterminados.")
                return DEFAULT_PROJECT_STATUSES[:]
        except Exception as e:
            if COLORAMA_AVAILABLE and debug_mode:
                print(f"  {Style.DIM}[DEBUG] Error leyendo archivo de estados ({e}), usando predeterminados.{Style.RESET_ALL}")
            elif debug_mode:
                print(f"  [DEBUG] Error leyendo archivo de estados ({e}), usando predeterminados.")
            return DEFAULT_PROJECT_STATUSES[:]
    else:
        if COLORAMA_AVAILABLE and debug_mode:
            print(f"  {Style.DIM}[DEBUG] Archivo de estados no encontrado, usando predeterminados.{Style.RESET_ALL}")
        elif debug_mode:
            print(f"  [DEBUG] Archivo de estados no encontrado, usando predeterminados.")
        return DEFAULT_PROJECT_STATUSES[:]

# --- NUEVAS FUNCIONES para Cargar Aplicaciones de PM ---
def load_pm_apps(debug_mode: bool = False) -> list[str]:
    """
    Carga la lista de aplicaciones de PM desde el archivo pmapps.def.
    Si el archivo no existe, lo crea con valores predeterminados.
    Si está vacío o hay un error al leerlo, usa DEFAULT_PM_APPS.
    """
    config_dir = get_config_dir_path() # Reutilizamos la función existente
    pm_apps_file = config_dir / PM_APPS_DEF_FILE_NAME

    # --- NUEVO: Crear archivo .def si no existe ---
    if not pm_apps_file.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(pm_apps_file, "w", encoding="utf-8") as f:
                for app_name in DEFAULT_PM_APPS:
                    f.write(f"{app_name}\n")
            if COLORAMA_AVAILABLE and debug_mode:
                print(f"  {Style.DIM}[DEBUG] Archivo '{pm_apps_file.name}' no encontrado. Creado con valores predeterminados.{Style.RESET_ALL}")
            elif debug_mode:
                print(f"  [DEBUG] Archivo '{pm_apps_file.name}' no encontrado. Creado con valores predeterminados.")
        except Exception as e:
            if COLORAMA_AVAILABLE and debug_mode:
                print(f"  {Style.DIM}[DEBUG] Error al crear '{pm_apps_file.name}' con valores predeterminados: {e}{Style.RESET_ALL}")
            elif debug_mode:
                print(f"  [DEBUG] Error al crear '{pm_apps_file.name}' con valores predeterminados: {e}")
            # Si falla la creación, se procederá igualmente.
    # --- FIN NUEVO ---
    
    if COLORAMA_AVAILABLE and debug_mode:
        print(f"  {Style.DIM}[DEBUG] Intentando cargar apps PM desde: {pm_apps_file}{Style.RESET_ALL}")
    elif debug_mode:
        print(f"  [DEBUG] Intentando cargar apps PM desde: {pm_apps_file}")

    if pm_apps_file.exists() and pm_apps_file.is_file():
        try:
            with open(pm_apps_file, "r", encoding="utf-8") as f:
                apps = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
            if apps:
                if COLORAMA_AVAILABLE and debug_mode:
                    print(f"  {Style.DIM}[DEBUG] Apps PM cargadas desde archivo: {apps}{Style.RESET_ALL}")
                elif debug_mode:
                    print(f"  [DEBUG] Apps PM cargadas desde archivo: {apps}")
                return apps
            else:
                if COLORAMA_AVAILABLE and debug_mode:
                    print(f"  {Style.DIM}[DEBUG] Archivo de apps PM vacío, usando predeterminadas.{Style.RESET_ALL}")
                elif debug_mode:
                    print(f"  [DEBUG] Archivo de apps PM vacío, usando predeterminadas.")
                return DEFAULT_PM_APPS[:]
        except Exception as e:
            if COLORAMA_AVAILABLE and debug_mode:
                print(f"  {Style.DIM}[DEBUG] Error leyendo archivo de apps PM ({e}), usando predeterminadas.{Style.RESET_ALL}")
            elif debug_mode:
                print(f"  [DEBUG] Error leyendo archivo de apps PM ({e}), usando predeterminadas.")
            return DEFAULT_PM_APPS[:]
    else:
        if COLORAMA_AVAILABLE and debug_mode:
            print(f"  {Style.DIM}[DEBUG] Archivo de apps PM no encontrado, usando predeterminadas.{Style.RESET_ALL}")
        elif debug_mode:
            print(f"  [DEBUG] Archivo de apps PM no encontrado, usando predeterminadas.")
        return DEFAULT_PM_APPS[:]

# --- Funciones de Acceso a la Configuración (Ejemplos) ---

def get_repository_config(project_data: dict) -> dict:
    """Devuelve la sección [repository] de los datos del proyecto."""
    return project_data.get("repository", {})

def get_main_branch_names(project_data: dict) -> list[str]:
    """Devuelve los nombres de las ramas principales configuradas."""
    protection_config = project_data.get("repository", {}).get("protection_config", {})
    main_branches = protection_config.get("main_branches", {})
    return list(main_branches.keys())

def get_work_branch_config(project_data: dict) -> dict:
    """Devuelve la configuración de las ramas de trabajo."""
    protection_config = project_data.get("repository", {}).get("protection_config", {})
    return protection_config.get("work_branches", {})

# --- Nueva función recursiva para pretty-printing ---
def _print_node(data, indent_level, section_key_original: Optional[str] = None):
    current_indent = INDENT_STRING * indent_level
    
    if isinstance(data, dict):
        max_label_len = 0
        for key, value in data.items():
            is_value_only_str = key in VALUE_ONLY_KEYS and isinstance(value, str)
            if not is_value_only_str and not isinstance(value, (dict, list)):
                label_text = key
                if section_key_original and section_key_original in KEY_TRANSLATION_MAP_ES:
                    label_text = KEY_TRANSLATION_MAP_ES[section_key_original].get(key, key)
                elif key in KEY_TRANSLATION_MAP_ES:
                    label_text = KEY_TRANSLATION_MAP_ES.get(key, key)
                max_label_len = max(max_label_len, len(label_text))

        item_processed_in_this_level_was_value_only_str = False
        
        for i, (key, value) in enumerate(data.items()):
            current_key_is_value_only_and_str = key in VALUE_ONLY_KEYS and isinstance(value, str)

            if item_processed_in_this_level_was_value_only_str and not current_key_is_value_only_and_str:
                # El item anterior fue solo valor (string), y este actual NO lo es (o no es string)
                # así que este actual mostrará una etiqueta o es una estructura.
                # Imprimir separador antes del item actual.
                print(f"{current_indent}{Style.DIM}{'-' * (BANNER_WIDTH // 2 - len(current_indent))}{Style.RESET_ALL}")
            
            display_key = key
            if section_key_original and section_key_original in KEY_TRANSLATION_MAP_ES:
                display_key = KEY_TRANSLATION_MAP_ES[section_key_original].get(key, key)
            elif key in KEY_TRANSLATION_MAP_ES:
                display_key = KEY_TRANSLATION_MAP_ES.get(key, key)

            if current_key_is_value_only_and_str:
                val_str = str(value)
                val_color = Fore.GREEN 
                if '\\n' in val_str:
                    for line_part in val_str.splitlines():
                        print(f"{current_indent}{val_color}{line_part}{Style.RESET_ALL}")
                else: 
                    print(f"{current_indent}{val_color}{val_str}{Style.RESET_ALL}")
                item_processed_in_this_level_was_value_only_str = True
            elif section_key_original == "project_details" and key == "pm_tool_info" and isinstance(value, dict):
                print(f"{current_indent}{Style.BRIGHT}=== {display_key} ==={Style.RESET_ALL}")
                _print_node(value, indent_level + 1, section_key_original) # Se procesa el contenido del dict
                item_processed_in_this_level_was_value_only_str = False # Esto no es un "solo valor str"
            elif isinstance(value, (dict, list)): # Caso general para otros dicts/lists
                print(f"{current_indent}{Fore.CYAN}{display_key}:{Style.RESET_ALL}")
                _print_node(value, indent_level + 1, section_key_original)
                item_processed_in_this_level_was_value_only_str = False
            else: # Caso para valores escalares (strings no VALUE_ONLY, bools, numbers)
                label_part = f"{Fore.CYAN}{display_key.ljust(max_label_len)}{Style.RESET_ALL}"
                print(f"{current_indent}{label_part} : ", end="")
                val_str = str(value)
                val_color = Fore.GREEN
                if isinstance(value, bool):
                    val_color = Fore.YELLOW
                    val_str = "Sí" if value else "No"
                elif isinstance(value, (int, float)):
                    val_color = Fore.YELLOW
                
                if isinstance(value, str) and '\\n' in value:
                    print() 
                    for line_part in value.splitlines():
                        print(f"{current_indent}{INDENT_STRING}{val_color}{line_part}{Style.RESET_ALL}")
                else:
                    print(f"{val_color}{val_str}{Style.RESET_ALL}")
                item_processed_in_this_level_was_value_only_str = False
        
        # No se necesita devolver el estado si se maneja iterativamente dentro del nivel.

    elif isinstance(data, list):
        # Para listas, el separador entre elementos no se aplica de la misma forma.
        # Si un elemento de la lista es un dict, la lógica de _print_node para dicts se aplicará internamente.
        for i, item in enumerate(data):
            print(f"{current_indent}{Fore.MAGENTA}-{Style.RESET_ALL} ", end="")
            if isinstance(item, (dict, list)):
                print() 
                _print_node(item, indent_level + 1, section_key_original)
            else: # Manejar elementos simples dentro de la lista
                val_str = str(item)
                val_color = Fore.GREEN
                if isinstance(item, bool):
                    val_str = "Sí" if item else "No"
                    val_color = Fore.YELLOW
                elif isinstance(item, (int, float)):
                    val_color = Fore.YELLOW
                
                if isinstance(item, str) and '\\n' in item: # Chequear \\n en strings literales
                    print() 
                    for line_part in item.splitlines():
                        print(f"{current_indent}{INDENT_STRING}{val_color}{line_part}{Style.RESET_ALL}")
                else:
                    print(f"{val_color}{val_str}{Style.RESET_ALL}")
    else: # Para data que no es ni dict ni list (escalar)
        print(f"{current_indent}{Fore.GREEN}{str(data)}{Style.RESET_ALL}")

# --- Nueva función para imprimir una sección con su marco ---
def _print_section_with_frame(section_name: str, section_data: dict):
    """Imprime una sección completa con su marco y contenido."""
    padding_char = "═"
    header_title = f" Sección: {section_name.upper()} "
    inner_width = BANNER_WIDTH - 2
    padding_total = inner_width - len(header_title)
    pad_left = padding_total // 2
    pad_right = padding_total - pad_left
    
    print(f"\n{Style.BRIGHT}{Fore.WHITE}╔{padding_char * pad_left}{header_title}{padding_char * pad_right}╗{Style.RESET_ALL}")
    _print_node(section_data, indent_level=1)
    print(f"{Style.BRIGHT}{Fore.WHITE}╚{padding_char * inner_width}╝{Style.RESET_ALL}")

# --- Lógica de la CLI ---

def handle_show_config(args: argparse.Namespace, project_data: dict):
    """Muestra la configuración actual del proyecto de forma estructurada."""
    # Verificar si existe la carpeta .project
    project_dir = args.path / ".project"
    if not project_dir.exists() or not project_dir.is_dir():
        print(f"{Fore.YELLOW}⚠️  Esta ruta no es un proyecto válido.{Style.RESET_ALL}")
        print(f"   No se encontró la carpeta '.project' en: {args.path}")
        print(f"\n   Use 'promanager.py init' para inicializar un nuevo proyecto.")
        return

    # Verificar si existe el archivo de metadatos
    meta_file = get_meta_file_path(args.path)
    if not meta_file.exists():
        print(f"{Fore.YELLOW}⚠️  Esta ruta no es un proyecto válido.{Style.RESET_ALL}")
        print(f"\n   Use 'promanager.py init' para inicializar un nuevo proyecto.")
        return

    if not project_data:
        print(f"{Fore.RED}Error: No se pudieron cargar los datos de configuración.{Style.RESET_ALL}")
        print(f"   Verifique que el archivo '{meta_file}' es válido.")
        return
    
    # La información del nombre del proyecto, esquema, config y descripción del repo ya se muestran antes.
    # Esta función ahora se enfoca en el resto de las secciones.

    # Preparar datos de sección para el menú/visualización
    sections_for_menu = {}
    
    # Extraer datos para cada sección definida en el MAPA
    if "repository" in project_data and isinstance(project_data["repository"], dict):
        repo_data = dict(project_data["repository"]) # Copia
        # Para "Información del Repositorio (General)"
        repo_general_data = {k: v for k, v in repo_data.items() if k not in ["name", "description", "protection_config", "workflow_config"]}
        if repo_general_data:
            sections_for_menu[SECTION_NAME_MAP_ES["repository"]] = repo_general_data
        
        # Para "Reglas de Protección de Ramas"
        if "protection_config" in repo_data and isinstance(repo_data["protection_config"], dict):
            sections_for_menu[SECTION_NAME_MAP_ES["protection_config"]] = repo_data["protection_config"]

        # --- INICIO: Añadir workflow_config al menú de handle_show_config ---
        if "workflow_config" in repo_data and isinstance(repo_data["workflow_config"], dict):
            sections_for_menu[SECTION_NAME_MAP_ES["workflow_config"]] = repo_data["workflow_config"]
        # --- FIN: Añadir workflow_config al menú de handle_show_config ---

    if "project_details" in project_data and isinstance(project_data["project_details"], dict):
        sections_for_menu[SECTION_NAME_MAP_ES["project_details"]] = project_data["project_details"]
        
    if "additional_metadata" in project_data and isinstance(project_data["additional_metadata"], dict):
        sections_for_menu[SECTION_NAME_MAP_ES["additional_metadata"]] = project_data["additional_metadata"]
    
    # Añadir otras secciones principales directamente si no están en el mapa pero son diccionarios
    for section_key, section_data_original in project_data.items():
        if section_key not in ["schema_version", "repository", "project_details", "additional_metadata"] and isinstance(section_data_original, dict):
            # Usar el nombre original si no está en el mapa, o añadirlo al mapa y usar la traducción
            display_name = SECTION_NAME_MAP_ES.get(section_key, section_key.replace("_", " ").title())
            sections_for_menu[display_name] = section_data_original

    if not sections_for_menu:
        print(f"  {Style.DIM}(No hay más secciones de configuración para mostrar.){Style.RESET_ALL}")
        return

    # --- Inicio del bucle interactivo del menú ---
    # La primera vez que se entra, el banner y descripción ya fueron mostrados por main().
    # Si se selecciona una sección, se limpiará y se volverá a mostrar todo.
    
    first_run_in_loop = True # Para no limpiar la pantalla la primera vez que se muestra el menú

    while True:
        if not first_run_in_loop:
            # Para cualquier vuelta al menú que no sea la primera, limpiar la pantalla
            # y volver a mostrar el banner/descripción para un estado consistente
            # antes de que questionary.select() se pinte.
            # Opcional: podríamos decidir no hacer esto si el menú de questionary se repinta bien.
            # Por ahora, lo mantenemos para asegurar limpieza.
            clear_screen()
            
            # Recalcular datos para el banner y descripción (igual que en main)
            schema_val = project_data.get("schema_version")
            schema_str = str(schema_val) if schema_val is not None else None
            repo_config_loop = project_data.get("repository", {})
            repo_name_val_loop = str(repo_config_loop.get("name", "")).upper()
            owner_name_val_loop = str(repo_config_loop.get("owner_name", "")).strip()
            project_name_for_banner_loop = None
            if owner_name_val_loop:
                project_name_for_banner_loop = f"{owner_name_val_loop.upper()}/{repo_name_val_loop}"
            elif repo_name_val_loop:
                project_name_for_banner_loop = repo_name_val_loop
            
            repo_description_loop = str(repo_config_loop.get("description")) if "description" in repo_config_loop else None

            show_banner(
                project_name_val=project_name_for_banner_loop,
                schema_version_val=schema_str,
                config_file_name=meta_file.name
            )
            if repo_description_loop: # Usar la descripción recalculada
                _print_repository_description(repo_description_loop)
        
        first_run_in_loop = False # Ya no es la primera ejecución

        # Preparar opciones del menú (lógica movida dentro del bucle por si sections_for_menu cambia)
        # Aunque en este caso, sections_for_menu se define una vez fuera del bucle.
        # Si sections_for_menu fuera dinámico, esto sería crucial aquí.
        all_section_labels = list(sections_for_menu.keys())
        repo_general_label = SECTION_NAME_MAP_ES.get("repository")
        additional_meta_label = SECTION_NAME_MAP_ES.get("additional_metadata")
        ordered_choices = []
        if repo_general_label and repo_general_label in all_section_labels:
            ordered_choices.append(repo_general_label)
            if repo_general_label in all_section_labels: all_section_labels.remove(repo_general_label) # Evitar error si no estaba
        
        temp_other_sections = [lbl for lbl in all_section_labels if lbl != additional_meta_label]
        temp_other_sections.sort()
        ordered_choices.extend(temp_other_sections)

        if additional_meta_label and additional_meta_label in sections_for_menu: # Chequear si existe en los datos originales
            if additional_meta_label in all_section_labels : # Si no fue removido como repo_general
                 ordered_choices.append(additional_meta_label)
            elif additional_meta_label not in ordered_choices: #Asegurar que se añada si fue filtrado por error antes
                 ordered_choices.append(additional_meta_label)


        choices = ordered_choices[:] # Copiar
        choices.append(questionary.Separator())
        choices.append("Salir")
        
        selected_choice = questionary.select(
            "Seleccione una sección para ver o una acción:",
            choices=choices,
            use_shortcuts=True
        ).ask()

        if selected_choice is None or selected_choice == "Salir":
            print(f"  {Style.DIM}Saliendo del visor de configuración.{Style.RESET_ALL}")
            break
        elif selected_choice in sections_for_menu:
            clear_screen()
            
            # Mostrar Banner y Descripción del Repositorio
            schema_val = project_data.get("schema_version")
            schema_str = str(schema_val) if schema_val is not None else None
            repo_config_selected = project_data.get("repository", {}) # Siempre tomar la config general del repo
            repo_name_val_selected = str(repo_config_selected.get("name", "")).upper()
            owner_name_val_selected = str(repo_config_selected.get("owner_name", "")).strip()
            project_name_for_banner_selected = None
            if owner_name_val_selected:
                project_name_for_banner_selected = f"{owner_name_val_selected.upper()}/{repo_name_val_selected}"
            elif repo_name_val_selected:
                project_name_for_banner_selected = repo_name_val_selected

            repo_description_selected = str(repo_config_selected.get("description")) if "description" in repo_config_selected else None
            
            show_banner(
                project_name_val=project_name_for_banner_selected,
                schema_version_val=schema_str,
                config_file_name=meta_file.name
            )
            if repo_description_selected:
                _print_repository_description(repo_description_selected)

            # Preparar datos de la sección seleccionada
            original_section_key = ES_TO_KEY_MAP.get(selected_choice)
            section_data_for_node = dict(sections_for_menu[selected_choice]) # Copia

            # Filtrar claves específicas si es la sección de repositorio general
            if original_section_key == "repository":
                section_data_for_node.pop("owner_name", None) # Ya en banner
                # name y description ya están filtrados al crear 'repo_general_data'
                # que se usa para poblar sections_for_menu[SECTION_NAME_MAP_ES["repository"]]
                
                # Ocultar platform_url si la plataforma es conocida y no auto-hospedada
                platform_value = section_data_for_node.get("platform")
                if platform_value and platform_value in KNOWN_HOSTED_PLATFORMS:
                    section_data_for_node.pop("platform_url", None)
                
                # Ocultar url si created_flag es False
                created_flag_value = section_data_for_node.get("created_flag", False)
                if not created_flag_value:
                    section_data_for_node.pop("url", None)

                # Resaltar estado de scaffold
                scaffold_value = section_data_for_node.get("scaffold", DEFAULT_SCAFFOLD_TYPE)
                initialized_value = section_data_for_node.get("initialized", False)
                if scaffold_value == DEFAULT_SCAFFOLD_TYPE:
                    section_data_for_node["scaffold"] = f"{Style.DIM}{scaffold_value}{Style.RESET_ALL}"
                elif initialized_value:
                    section_data_for_node["scaffold"] = f"{Style.GREEN}{scaffold_value} (Inicializado){Style.RESET_ALL}"
                else:
                    section_data_for_node["scaffold"] = f"{Style.YELLOW}{scaffold_value} (Pendiente){Style.RESET_ALL}"

            # NUEVO: Filtrar pm_tool_info si tool_name es "Ninguna"
            if original_section_key == "project_details":
                pm_tool_info_data = section_data_for_node.get("pm_tool_info")
                if isinstance(pm_tool_info_data, dict) and pm_tool_info_data.get("tool_name") == "Ninguna":
                    # Hacemos una copia de pm_tool_info para modificarla
                    pm_tool_info_copy = dict(pm_tool_info_data)
                    pm_tool_info_copy.pop("project_link", None)
                    pm_tool_info_copy.pop("project_key", None)
                    # Reasignamos la copia modificada a la sección principal
                    section_data_for_node["pm_tool_info"] = pm_tool_info_copy
            
            # Nuevo formato para el título de la sección individual
            section_title_display = f" {selected_choice.upper()} "
            padding_char_title = "─" # Usar un carácter más ligero para el título
            title_padding_total = BANNER_WIDTH - len(section_title_display) -2 # -2 for potential color codes len issues
            pad_left_title = max(0, title_padding_total // 2)
            pad_right_title = max(0, title_padding_total - pad_left_title)
            
            print(f"\n{Style.BRIGHT}{Fore.WHITE}{padding_char_title * pad_left_title}{Style.NORMAL}{Fore.CYAN}{section_title_display}{Style.BRIGHT}{Fore.WHITE}{padding_char_title * pad_right_title}{Style.RESET_ALL}")
            
            # Añadir espacio si el primer elemento es VALUE_ONLY y string
            if section_data_for_node: # Asegurarse de que no está vacío
                first_key = next(iter(section_data_for_node))
                if first_key in VALUE_ONLY_KEYS and isinstance(section_data_for_node[first_key], str):
                    print() # Línea en blanco de separación
                
                # Plan Específico: Añadir separador entre 'title' y 'purpose' en 'project_details'
                if original_section_key == "project_details" and \
                   "title" in section_data_for_node and \
                   section_data_for_node.get("title") and isinstance(section_data_for_node.get("title"), str) and \
                   "title" in VALUE_ONLY_KEYS and \
                   "purpose" in section_data_for_node:
                    # Asegurarse de que title es el *primer* elemento para aplicar este separador después de él
                    # y antes de purpose. O, más simple, si title existe y purpose también, y title es VALUE_ONLY.
                    # La lógica actual de _print_node imprimirá title, luego si purpose es el siguiente, se imprimirá purpose.
                    # Este separador se imprimirá *antes* de la llamada a _print_node si se cumplen las condiciones.
                    # Esto no es del todo correcto. El separador debe ir *después* de que se imprima title
                    # y *antes* de que se imprima purpose. Esto debe manejarse en _print_node.
                    # REVISIÓN: La implementación de esto aquí es compleja porque _print_node maneja el orden.
                    # VAMOS A INTENTAR LA MODIFICACIÓN EN _PRINT_NODE con estado.
                    pass # Se manejará en _print_node como se discutió para la solución general

            _print_node(section_data_for_node, indent_level=1, section_key_original=original_section_key)
            
            input(f"\n{Style.DIM}Presione Enter para volver al menú...{Style.RESET_ALL}")
            # El bucle continuará, volviendo a mostrar el menú de questionary.
        else:
            print(f"{Fore.RED}Opción desconocida: {selected_choice}{Style.RESET_ALL}") # No debería ocurrir
    # --- Fin del bucle interactivo del menú ---

    # Fallback si questionary no está disponible
    else:
        print(f"  {Style.DIM}(Librería 'questionary' no disponible. Mostrando todas las secciones restantes.){Style.RESET_ALL}")
        for name_es, data in sorted(sections_for_menu.items()):
            original_key_fallback = ES_TO_KEY_MAP.get(name_es)
            # Si quisiéramos el mismo filtrado para 'repository' aquí:
            data_to_print_fallback = dict(data)
            if original_key_fallback == "repository":
                 data_to_print_fallback.pop("owner_name", None)
                 # Ocultar platform_url también en el fallback
                 platform_value_fallback = data_to_print_fallback.get("platform")
                 if platform_value_fallback and platform_value_fallback in KNOWN_HOSTED_PLATFORMS:
                     data_to_print_fallback.pop("platform_url", None)

                 # NUEVO: Ocultar url en fallback si created_flag es False
                 created_flag_value_fallback = data_to_print_fallback.get("created_flag", False)
                 if not created_flag_value_fallback:
                     data_to_print_fallback.pop("url", None)

                 # Filtrar init_options en fallback
                 init_options_data_fallback = data_to_print_fallback.get("init_options")

            # NUEVO: Filtrar pm_tool_info en fallback si tool_name es "Ninguna"
            if original_key_fallback == "project_details":
                pm_tool_info_data_fallback = data_to_print_fallback.get("pm_tool_info")
                if isinstance(pm_tool_info_data_fallback, dict) and pm_tool_info_data_fallback.get("tool_name") == "Ninguna":
                    pm_tool_info_copy_fallback = dict(pm_tool_info_data_fallback)
                    pm_tool_info_copy_fallback.pop("project_link", None)
                    pm_tool_info_copy_fallback.pop("project_key", None)
                    data_to_print_fallback["pm_tool_info"] = pm_tool_info_copy_fallback

            # Usar el nuevo formato de título también en el fallback
            section_title_display_fallback = f" {name_es.upper()} "
            padding_char_title_fallback = "─"
            title_padding_total_fallback = BANNER_WIDTH - len(section_title_display_fallback) - 2
            pad_left_title_fallback = max(0, title_padding_total_fallback // 2)
            pad_right_title_fallback = max(0, title_padding_total_fallback - pad_left_title_fallback)

            print(f"\n{Style.BRIGHT}{Fore.WHITE}{padding_char_title_fallback * pad_left_title_fallback}{Style.NORMAL}{Fore.CYAN}{section_title_display_fallback}{Style.BRIGHT}{Fore.WHITE}{padding_char_title_fallback * pad_right_title_fallback}{Style.RESET_ALL}")

            # Añadir espacio también en fallback si el primer elemento es VALUE_ONLY y string
            if data_to_print_fallback: # Asegurarse de que no está vacío
                first_key_fallback = next(iter(data_to_print_fallback))
                if first_key_fallback in VALUE_ONLY_KEYS and isinstance(data_to_print_fallback[first_key_fallback], str):
                    print() # Línea en blanco de separación
                
                # Plan Específico para fallback - similarmente, esto sería mejor en _print_node
                if original_key_fallback == "project_details" and \
                   "title" in data_to_print_fallback and \
                   data_to_print_fallback.get("title") and isinstance(data_to_print_fallback.get("title"), str) and \
                   "title" in VALUE_ONLY_KEYS and \
                   "purpose" in data_to_print_fallback:
                    pass # Se manejará en _print_node

            _print_node(data_to_print_fallback, indent_level=1, section_key_original=original_key_fallback)

def handle_init_config(args: argparse.Namespace, project_data: dict):
    """
    Etapa 1: Inicialización del workspace.
    Habilita la funcionalidad de inicializar un workspace.
    
    Etapa 2: Configuración de reglas Cursor.
    Crea .cursor/rules y copia los archivos .def a .mdc.
    Si existen, no hace nada a menos que se use -f.
    
    Etapa 3: Creación del archivo .ws.
    Crea el archivo .ws en el workspace si no existe.
    Si existe, no hace nada a menos que se use -f.
    
    Args:
        args: Argumentos parseados que incluyen:
            - workspace: Ruta del workspace (opcional)
            - force: Si se debe forzar la actualización del workspace existente
        project_data: Datos del proyecto (no usado en esta etapa)
    """
    try:
        # Etapa 1: Configuración del workspace
        if args.workspace:
            workspace_path = Path(args.workspace).expanduser().resolve()
        else:
            workspace_path = get_default_workspace()
            
        # Verificar si el workspace existe
        if workspace_path.exists():
            if not args.force:
                print(f"El workspace ya existe en: {workspace_path}")
                print("Use -f para forzar la actualización del workspace")
                return
            print(f"Actualizando workspace existente: {workspace_path}")
        else:
            print(f"Creando nuevo workspace en: {workspace_path}")
            
        # Crear el workspace si no existe o si se usa -f
        workspace_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Workspace configurado en: {workspace_path}")

        # Etapa 2: Configuración de reglas Cursor
        script_dir = Path(__file__).parent
        cursor_rules_dir = workspace_path / ".cursor" / "rules"
        config_dir = script_dir / "config"

        if not config_dir.exists():
            print(f"❌ Error: No se encontró la carpeta config en: {config_dir}")
            return

        # Crear directorio .cursor/rules si no existe
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)

        # Verificar si ya existen archivos .mdc
        existing_mdc = list(cursor_rules_dir.glob("*.mdc"))
        if existing_mdc and not args.force:
            print(f"Ya existen archivos de reglas en: {cursor_rules_dir}")
            print("Use -f para forzar la actualización de las reglas")
            return

        # Si se usa -f, eliminar archivos .mdc existentes
        if args.force and existing_mdc:
            print("Actualizando archivos de reglas existentes...")
            for mdc_file in existing_mdc:
                mdc_file.unlink()

        # Buscar solo archivos .mdc.def
        def_files = list(config_dir.glob("*.mdc.def"))
        if not def_files:
            print(f"❌ Error: No se encontraron archivos .mdc.def en: {config_dir}")
            return

        print("Copiando archivos de reglas...")
        for def_file in def_files:
            # Remover .def del nombre final
            mdc_file = cursor_rules_dir / f"{def_file.stem[:-4]}.mdc"
            shutil.copy2(def_file, mdc_file)
            print(f"  ✓ {def_file.name} -> {mdc_file.name}")

        print(f"✅ Reglas Cursor configuradas en: {cursor_rules_dir}")

        # Copiar .cursorrules.def a .cursorrules en el workspace
        cursorrules_src = config_dir / ".cursorrules.def"
        cursorrules_dst = workspace_path / ".cursorrules"

        if not cursorrules_src.exists():
            print(f"❌ Error: No se encontró el archivo .cursorrules.def en: {config_dir}")
            return

        if cursorrules_dst.exists() and not args.force:
            print(f"El archivo .cursorrules ya existe en: {workspace_path}")
            print("Use -f para forzar la actualización del archivo")
            return

        if args.force and cursorrules_dst.exists():
            print("Actualizando archivo .cursorrules existente...")
            cursorrules_dst.unlink()

        shutil.copy2(cursorrules_src, cursorrules_dst)
        print(f"✅ Archivo .cursorrules copiado a: {workspace_path}")

        # Etapa 3: Creación del archivo .ws
        ws_file = workspace_path / ".ws"
        
        if ws_file.exists() and not args.force:
            print(f"El archivo .ws ya existe en: {workspace_path}")
            print("Use -f para forzar la actualización del archivo")
            return

        if args.force and ws_file.exists():
            print("Actualizando archivo .ws existente...")
            ws_file.unlink()

        # Crear el archivo .ws con la fecha de creación/actualización
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws_content = f"""# Archivo de configuración del workspace
# Creado/Actualizado: {current_time}
# Workspace: {workspace_path}

# Este archivo indica que este directorio es un workspace válido
# y contiene la configuración básica del workspace.

[workspace]
path = "{workspace_path}"
created_at = "{current_time}"
"""
        ws_file.write_text(ws_content, encoding='utf-8')
        print(f"✅ Archivo .ws creado en: {workspace_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

def handle_edit_config(args: argparse.Namespace, project_data: dict):
    """Permite editar la configuración del proyecto de forma interactiva."""
    # Verificar si existe la carpeta .project
    project_dir = args.path / ".project"
    if not project_dir.exists() or not project_dir.is_dir():
        print(f"{Fore.YELLOW}⚠️  Esta ruta no es un proyecto válido.{Style.RESET_ALL}")
        print(f"   No se encontró la carpeta '.project' en: {args.path}")
        print(f"\n   Use 'promanager.py init' para inicializar un nuevo proyecto.")
        return

    if not project_data:
        print(f"{Fore.RED}No hay datos de configuración para editar. ¿Existe '.project/project_meta.toml'?{Style.RESET_ALL}", file=sys.stderr)
        return

    # Cargar estados del proyecto dinámicamente
    project_statuses = load_project_statuses(debug_mode=SCRIPT_DEBUG_MODE)
    # Cargar aplicaciones de PM dinámicamente
    project_pm_apps = load_pm_apps(debug_mode=SCRIPT_DEBUG_MODE)
    
    # Hacer una copia de PREDEFINED_CHOICES_FOR_KEYS para modificarla localmente en esta función
    editable_predefined_choices = copy.deepcopy(PREDEFINED_CHOICES_FOR_KEYS)
    editable_predefined_choices["status"] = project_statuses # Poblar con los estados cargados
    editable_predefined_choices["tool_name"] = project_pm_apps # Poblar con las apps PM cargadas

    # Agregar opciones predefinidas para workflow_config
    editable_predefined_choices["commit_format"] = [  # NUEVO PARA WORKFLOW
        "conventional",  # [TAG] (#Issue) descripción
        "angular",       # feat(scope): descripción
        "semantic",      # type(scope): descripción
        "simple",        # type: descripción
        "minimal"        # descripción
    ]
    editable_predefined_choices["release_process"] = ["unified_custom"] # NUEVO PARA WORKFLOW

    # NO_CHANGE_SENTINEL ya es global

    # Similar a handle_show_config, preparamos las secciones disponibles
    sections_for_menu = {}
    if "repository" in project_data and isinstance(project_data["repository"], dict):
        repo_data = dict(project_data["repository"])
        # Excluir workflow_config y protection_config de la información general
        repo_general_data = {k: v for k, v in repo_data.items() if k not in ["name", "description", "protection_config", "workflow_config"]}
        if repo_general_data:
            sections_for_menu[SECTION_NAME_MAP_ES["repository"]] = repo_general_data
        
        if "protection_config" in repo_data and isinstance(repo_data["protection_config"], dict):
            sections_for_menu[SECTION_NAME_MAP_ES["protection_config"]] = repo_data["protection_config"]
        
        # --- INICIO: Manejo de workflow_config para el menú de secciones ---
        if "workflow_config" in repo_data and isinstance(repo_data["workflow_config"], dict):
            sections_for_menu[SECTION_NAME_MAP_ES["workflow_config"]] = repo_data["workflow_config"]
        elif "workflow_config" not in repo_data:  # Si no existe en los datos cargados, la creamos vacía para el menú
            if "repository" not in project_data: # Asegurar que 'repository' exista
                project_data["repository"] = {}
            project_data["repository"]["workflow_config"] = {} # Crear la subsección vacía
            sections_for_menu[SECTION_NAME_MAP_ES["workflow_config"]] = project_data["repository"]["workflow_config"]
        # --- FIN: Manejo de workflow_config para el menú de secciones ---

    if "project_details" in project_data and isinstance(project_data["project_details"], dict):
        sections_for_menu[SECTION_NAME_MAP_ES["project_details"]] = project_data["project_details"]
        
    if "additional_metadata" in project_data and isinstance(project_data["additional_metadata"], dict):
        sections_for_menu[SECTION_NAME_MAP_ES["additional_metadata"]] = project_data["additional_metadata"]
    
    for section_key, section_data_original in project_data.items():
        if section_key not in ["schema_version", "repository", "project_details", "additional_metadata"] and isinstance(section_data_original, dict):
            display_name = SECTION_NAME_MAP_ES.get(section_key, section_key.replace("_", " ").title())
            sections_for_menu[display_name] = section_data_original

    if not sections_for_menu:
        print(f"  {Style.DIM}(No hay secciones de configuración para editar.){Style.RESET_ALL}")
        return

    first_run_in_loop = True
    # Usar deepcopy para asegurar que los datos anidados también se copien
    original_project_data_backup = copy.deepcopy(project_data)

    while True:
        if not first_run_in_loop:
            clear_screen()
            schema_val = project_data.get("schema_version")
            schema_str = str(schema_val) if schema_val is not None else None
            repo_config_loop = project_data.get("repository", {})
            repo_name_val_loop = str(repo_config_loop.get("name", "")).upper()
            owner_name_val_loop = str(repo_config_loop.get("owner_name", "")).strip()
            project_name_for_banner_loop = repo_name_val_loop
            if owner_name_val_loop: project_name_for_banner_loop = f"{owner_name_val_loop.upper()}/{repo_name_val_loop}"
            
            repo_description_loop = str(repo_config_loop.get("description")) if "description" in repo_config_loop else None
            show_banner(project_name_val=project_name_for_banner_loop, schema_version_val=schema_str, config_file_name=Path(META_FILE_NAME).name) # Usar .name
            if repo_description_loop: _print_repository_description(repo_description_loop)
        
        first_run_in_loop = False

        all_section_labels = list(sections_for_menu.keys())
        repo_general_label = SECTION_NAME_MAP_ES.get("repository")
        additional_meta_label = SECTION_NAME_MAP_ES.get("additional_metadata")
        ordered_choices = []
        if repo_general_label and repo_general_label in all_section_labels:
            ordered_choices.append(repo_general_label)
            if repo_general_label in all_section_labels: all_section_labels.remove(repo_general_label)
        
        temp_other_sections = [lbl for lbl in all_section_labels if lbl != additional_meta_label]
        temp_other_sections.sort()
        ordered_choices.extend(temp_other_sections)

        if additional_meta_label and additional_meta_label in sections_for_menu:
            if additional_meta_label in all_section_labels : ordered_choices.append(additional_meta_label)
            elif additional_meta_label not in ordered_choices: ordered_choices.append(additional_meta_label)

        choices = ordered_choices[:]
        choices.append(questionary.Separator())
        choices.append("Guardar Cambios y Salir")
        choices.append("Descartar Cambios y Salir")
        
        selected_choice_section_to_edit = questionary.select(
            "Seleccione una sección para EDITAR o una acción:",
            choices=choices,
            use_shortcuts=True
        ).ask()

        if selected_choice_section_to_edit is None or selected_choice_section_to_edit == "Descartar Cambios y Salir":
            project_data.clear()
            project_data.update(original_project_data_backup)
            print(f"  {Style.DIM}Cambios descartados. Saliendo del editor de configuración.{Style.RESET_ALL}")
            break
        elif selected_choice_section_to_edit == "Guardar Cambios y Salir":
            if "project_details" in project_data and \
               isinstance(project_data["project_details"], dict) and \
               "pm_tool_info" in project_data["project_details"] and \
               isinstance(project_data["project_details"]["pm_tool_info"], dict):
                
                pm_tool_info_ref = project_data["project_details"]["pm_tool_info"]
                if pm_tool_info_ref.get("tool_name") is None:
                    pm_tool_info_ref.pop("tool_name", None)
            
            meta_file_path = get_meta_file_path(args.path.resolve()) # Usar args.path de main
            if save_project_data(project_data, meta_file_path):
                print(f"  {Style.BRIGHT}{Fore.GREEN}Cambios guardados exitosamente en '{meta_file_path}'.{Style.RESET_ALL}")
            else:
                print(f"  {Style.BRIGHT}{Fore.RED}Error al guardar los cambios.{Style.RESET_ALL}")
            break 
        elif selected_choice_section_to_edit in sections_for_menu:
            clear_screen()
            
            schema_val_edit = project_data.get("schema_version")
            schema_str_edit = str(schema_val_edit) if schema_val_edit is not None else None
            repo_config_edit = project_data.get("repository", {})
            repo_name_val_edit = str(repo_config_edit.get("name", "")).upper()
            owner_name_val_edit = str(repo_config_edit.get("owner_name", "")).strip()
            project_name_for_banner_edit = repo_name_val_edit
            if owner_name_val_edit: project_name_for_banner_edit = f"{owner_name_val_edit.upper()}/{repo_name_val_edit}"
            repo_description_edit = str(repo_config_edit.get("description")) if "description" in repo_config_edit else None
            
            show_banner(project_name_val=project_name_for_banner_edit, schema_version_val=schema_str_edit, config_file_name=Path(META_FILE_NAME).name) # Usar .name
            if repo_description_edit: _print_repository_description(repo_description_edit)

            original_section_key = ES_TO_KEY_MAP.get(selected_choice_section_to_edit)
            section_data_to_edit = project_data.get(original_section_key)
            
            if original_section_key == "repository": 
                section_data_to_edit = project_data["repository"] 
            elif original_section_key == "protection_config":
                if "repository" in project_data and "protection_config" in project_data["repository"]:
                    section_data_to_edit = project_data["repository"]["protection_config"]
                else: 
                    print(f"{Fore.RED}Error: No se encontró 'protection_config' en 'repository'.{Style.RESET_ALL}")
                    input(f"{Style.DIM}Presione Enter para continuar...{Style.RESET_ALL}")
                    continue
            elif original_section_key == "workflow_config":
                if "repository" not in project_data:
                    project_data["repository"] = {}
                if "workflow_config" not in project_data["repository"]:
                    project_data["repository"]["workflow_config"] = {}
                section_data_to_edit = project_data["repository"]["workflow_config"]
            elif original_section_key == "project_details":
                section_data_to_edit = project_data["project_details"]
            elif original_section_key == "additional_metadata":
                section_data_to_edit = project_data.setdefault("additional_metadata", {})
            else: # Fallback si la sección original no es una de las principales conocidas
                # Intentar obtenerla directamente de project_data, si no, error.
                section_data_to_edit = project_data.get(original_section_key)
                if section_data_to_edit is None:
                    print(f"{Fore.RED}Error: Clave de sección original '{original_section_key}' no encontrada en project_data.{Style.RESET_ALL}")
                    input(f"{Style.DIM}Presione Enter para continuar...{Style.RESET_ALL}")
                    continue

            if not isinstance(section_data_to_edit, dict):
                print(f"{Fore.RED}Error: La sección '{selected_choice_section_to_edit}' no es un diccionario editable.{Style.RESET_ALL}")
                input(f"{Style.DIM}Presione Enter para continuar...{Style.RESET_ALL}")
                continue
            
            section_title_display_edit = f" EDITANDO: {selected_choice_section_to_edit.upper()} "
            padding_char_title_edit = "─"
            title_padding_total_edit = BANNER_WIDTH - len(section_title_display_edit) - 2
            pad_left_title_edit = max(0, title_padding_total_edit // 2)
            pad_right_title_edit = max(0, title_padding_total_edit - pad_left_title_edit)
            
            print(f"\n{Style.BRIGHT}{Fore.WHITE}{padding_char_title_edit * pad_left_title_edit}{Style.NORMAL}{Fore.CYAN}{section_title_display_edit}{Style.BRIGHT}{Fore.WHITE}{padding_char_title_edit * pad_right_title_edit}{Style.RESET_ALL}")
            print()

            while True:
                field_choices = []
                repo_created_for_current_section = False
                if original_section_key == "repository":
                    repo_created_for_current_section = section_data_to_edit.get("created_flag", False)
                    if repo_created_for_current_section:
                        # Si el repositorio ya está creado, solo permitir editar ciertas claves
                        editable_keys = EDITABLE_REPO_KEYS_WHEN_CREATED
                    else:
                        # Si no está creado, permitir editar todas las claves excepto las que dependen de la creación
                        editable_keys = [k for k in section_data_to_edit.keys() if k not in ["url"]]
                else:
                    editable_keys = list(section_data_to_edit.keys())

                for key in editable_keys:
                    if key in VALUE_ONLY_KEYS and isinstance(section_data_to_edit[key], str):
                        field_choices.append(f"{key} (texto)")
                    elif key in editable_predefined_choices:
                        field_choices.append(f"{key} (opciones)")
                    elif isinstance(section_data_to_edit[key], bool):
                        field_choices.append(f"{key} (sí/no)")
                    elif isinstance(section_data_to_edit[key], (int, float)):
                        field_choices.append(f"{key} (número)")
                    elif isinstance(section_data_to_edit[key], str):
                        field_choices.append(f"{key} (texto)")
                    elif isinstance(section_data_to_edit[key], dict):
                        field_choices.append(f"{key} (subsección)")
                    elif isinstance(section_data_to_edit[key], list):
                        field_choices.append(f"{key} (lista)")
                    else:
                        field_choices.append(f"{key} (tipo desconocido)")

                field_choices.append(questionary.Separator())
                field_choices.append("Volver al Menú Principal")

                selected_field = questionary.select(
                    "Seleccione un campo para editar:",
                    choices=field_choices,
                    use_shortcuts=True
                ).ask()

                if selected_field is None or selected_field == "Volver al Menú Principal":
                    break

                field_name = selected_field.split(" (")[0]
                field_type = selected_field.split("(")[1].rstrip(")")

                if field_type == "subsección":
                    print(f"\n{Style.YELLOW}⚠️  La edición de subsecciones aún no está implementada.{Style.RESET_ALL}")
                    input(f"{Style.DIM}Presione Enter para continuar...{Style.RESET_ALL}")
                    continue
                elif field_type == "lista":
                    print(f"\n{Style.YELLOW}⚠️  La edición de listas aún no está implementada.{Style.RESET_ALL}")
                    input(f"{Style.DIM}Presione Enter para continuar...{Style.RESET_ALL}")
                    continue
                elif field_type == "tipo desconocido":
                    print(f"\n{Style.YELLOW}⚠️  No se puede editar este tipo de campo.{Style.RESET_ALL}")
                    input(f"{Style.DIM}Presione Enter para continuar...{Style.RESET_ALL}")
                    continue

                current_value = section_data_to_edit.get(field_name)
                if field_type == "opciones":
                    if field_name in editable_predefined_choices:
                        choices = editable_predefined_choices[field_name]
                        if field_name == "tool_name" and current_value == "Ninguna":
                            # Si tool_name es "Ninguna", no permitir editar project_link ni project_key
                            if "project_details" in project_data and \
                               isinstance(project_data["project_details"], dict) and \
                               "pm_tool_info" in project_data["project_details"] and \
                               isinstance(project_data["project_details"]["pm_tool_info"], dict):
                                pm_tool_info_ref = project_data["project_details"]["pm_tool_info"]
                                pm_tool_info_ref.pop("project_link", None)
                                pm_tool_info_ref.pop("project_key", None)
                        new_value = questionary.select(
                            f"Seleccione un valor para '{field_name}':",
                            choices=choices,
                            default=current_value if current_value in choices else None
                        ).ask()
                        if new_value is None:
                            continue
                        section_data_to_edit[field_name] = new_value
                    else:
                        print(f"\n{Style.YELLOW}⚠️  No hay opciones predefinidas para '{field_name}'.{Style.RESET_ALL}")
                        input(f"{Style.DIM}Presione Enter para continuar...{Style.RESET_ALL}")
                        continue
                elif field_type == "sí/no":
                    new_value = questionary.confirm(
                        f"¿Establecer '{field_name}' como 'Sí'?",
                        default=current_value
                    ).ask()
                    if new_value is None:
                        continue
                    section_data_to_edit[field_name] = new_value
                elif field_type == "número":
                    try:
                        new_value = questionary.text(
                            f"Ingrese un número para '{field_name}':",
                            default=str(current_value) if current_value is not None else None
                        ).ask()
                        if new_value is None:
                            continue
                        if isinstance(current_value, int):
                            section_data_to_edit[field_name] = int(new_value)
                        else:
                            section_data_to_edit[field_name] = float(new_value)
                    except ValueError:
                        print(f"\n{Style.RED}Error: El valor ingresado no es un número válido.{Style.RESET_ALL}")
                        input(f"{Style.DIM}Presione Enter para continuar...{Style.RESET_ALL}")
                        continue
                else: # texto
                    new_value = questionary.text(
                        f"Ingrese un texto para '{field_name}':",
                        default=current_value if current_value is not None else None
                    ).ask()
                    if new_value is None:
                        continue
                    section_data_to_edit[field_name] = new_value

                print(f"\n{Style.GREEN}✓ Campo '{field_name}' actualizado.{Style.RESET_ALL}")
                input(f"{Style.DIM}Presione Enter para continuar...{Style.RESET_ALL}")

def setup_pre_commit_and_deps(config_dir, root_dir, workflow_config):
    """Configura pre-commit y sus dependencias.
    
    Args:
        config_dir: Directorio de configuración
        root_dir: Directorio raíz del proyecto
        workflow_config: Configuración del flujo de trabajo
    """
    print("\nConfigurando pre-commit y dependencias...")
    
    # Ya no se necesita el intento inicial de desconfigurar core.hooksPath si no usamos Husky.

    # 1. Verificar entorno Python
    if not os.path.exists(os.path.join(root_dir, ".venv")):
        print("[ERROR] No se encontró el entorno virtual Python (.venv)")
        return False
    
    # 2. Verificar dependencias Python requeridas
    try:
        import pre_commit
    except ImportError:
        print("[ERROR] pre-commit no está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit"], check=True)
    
    # 3. Copiar configuración de pre-commit
    pre_commit_config_src = os.path.join(config_dir, "pre-commit-config.yaml.def")
    pre_commit_config_dst = os.path.join(root_dir, ".pre-commit-config.yaml")
    shutil.copy2(pre_commit_config_src, pre_commit_config_dst)
    print("[OK] Configuración de pre-commit copiada")
    
    # 4. Copiar script wrapper de commitlint
    wrapper_src = os.path.join(config_dir, "commitlint-wrapper.sh.def")
    wrapper_dst = os.path.join(root_dir, "commitlint-wrapper.sh")
    shutil.copy2(wrapper_src, wrapper_dst)
    os.chmod(wrapper_dst, 0o755)  # Dar permisos de ejecución
    print("[OK] Script wrapper de commitlint copiado")
    
    # 5. Instalar pre-commit (hooks generales)
    try:
        subprocess.run(["pre-commit", "install"], check=True)
        print("[OK] pre-commit instalado")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudo instalar pre-commit: {e}")
        # Si esto falla, podría ser por un core.hooksPath preexistente de otra fuente.
        # El usuario tendría que limpiarlo manualmente.
        print(f"Hint: Si el error menciona 'core.hooksPath', verifícalo con 'git config core.hooksPath' y elimínalo si es necesario.")
        return False
    
    # 6. Instalar @commitlint/cli (necesario para el wrapper)
    try:
        subprocess.run(["npm", "install", "--save-dev", "@commitlint/cli"], check=True)
        print("[OK] @commitlint/cli instalado")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudo instalar @commitlint/cli: {e}")
        return False
    
    # Los pasos 7 (Instalar Husky) y 8 (Configurar Husky) se eliminan.
    # El bloque "NUEVO" para desconfigurar core.hooksPath también se elimina.

    # 7. Copiar configuración de commitlint (anteriormente paso 9)
    commit_format = workflow_config.get("commit_format", "conventional")
    source_file = os.path.join(config_dir, f"commitlint.config.{commit_format}.js.def")
    destination_file = os.path.join(root_dir, "commitlint.config.js")
    
    if os.path.exists(source_file):
        shutil.copy2(source_file, destination_file)
        print(f"[OK] Configuración de commitlint copiada para formato {commit_format}")
    else:
        print(f"[ERROR] No se encontró configuración para el formato {commit_format}: {source_file}")
        return False
   
    # 8. Instalar hook commit-msg (anteriormente parte del paso 9)
    try:
        subprocess.run(["pre-commit", "install", "--hook-type", "commit-msg"], check=True)
        print("[OK] Hook commit-msg instalado")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudo instalar el hook commit-msg: {e}")
        # Si esto falla, podría ser por un core.hooksPath preexistente de otra fuente.
        print(f"Hint: Si el error menciona 'core.hooksPath', verifícalo con 'git config core.hooksPath' y elimínalo si es necesario.")
        return False
    
    print("\n[OK] Configuración de pre-commit y dependencias completada")
    return True

def handle_setup_ci(args: argparse.Namespace, project_data: dict):
    """Configura las herramientas de CI y pre-commit según la configuración del proyecto."""
    # Verificar si existe la carpeta .project
    project_dir = args.path / ".project"
    if not project_dir.exists() or not project_dir.is_dir():
        print(f"{Fore.YELLOW}⚠️  Esta ruta no es un proyecto válido.{Style.RESET_ALL}")
        print(f"   No se encontró la carpeta '.project' en: {args.path}")
        print(f"\n   Use 'promanager.py init' para inicializar un nuevo proyecto.")
        return

    print(f"{Style.BRIGHT}Configurando herramientas de CI y pre-commit...{Style.RESET_ALL}")
    
    # Obtener la configuración de workflow
    workflow_config = project_data.get("repository", {}).get("workflow_config", {})
    commit_format = workflow_config.get("commit_format", "conventional")
    
    # Definir rutas
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    root_dir = os.getcwd()
    
    # Configurar pre-commit y dependencias
    if not setup_pre_commit_and_deps(config_dir, root_dir, workflow_config):
        print(f"{Fore.YELLOW}Advertencia: La configuración de pre-commit y dependencias no fue completamente exitosa{Style.RESET_ALL}")
        return False

    # Verificar si hay cambios para commitear
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True)
        if result.stdout.strip():
            # Hay cambios, proceder con el commit automático
            subprocess.run(['git', 'add', '.'], check=True)
            
            # --- INICIO DE CAMBIOS ---
            require_issue_flag = workflow_config.get("require_issue", False)
            issue_ref = " (#0)" if require_issue_flag else "" # Espacio inicial importante si hay issue

            commit_subject = "configura flujos y hooks de commit (setup-ci)"
            commit_body = "\n\nAutomatiza la configuración de pre-commit, commitlint y archivos auxiliares para el flujo CI."
            
            # Mensaje de commit estandarizado para promanager.py al configurar CI
            # Siempre usará [CI] como TAG y el formato [TAG](issue_ref_opcional) subject
            commit_msg = f"[CI]{issue_ref} {commit_subject}{commit_body}"
            # --- FIN DE CAMBIOS ---
            
            try:
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                print(f"{Fore.GREEN}✓ Commit automático realizado correctamente.{Style.RESET_ALL}")
            except subprocess.CalledProcessError as e:
                print(f"{Fore.YELLOW}Advertencia: Error al realizar el commit automático: {e}{Style.RESET_ALL}")
                print(f"{Style.DIM}Por favor, revisa el estado del repositorio y realiza el commit manualmente.{Style.RESET_ALL}")
        else:
            print(f"{Style.DIM}No hay cambios para commitear.{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.YELLOW}Advertencia: Error al verificar el estado de git: {e}{Style.RESET_ALL}")
        return False

    return True

def load_scaffold_types(debug_mode: bool = False) -> list:
    """Carga los tipos de scaffold disponibles desde project_types.def.
    
    Args:
        debug_mode (bool): Si es True, muestra mensajes de depuración.
        
    Returns:
        list: Lista ordenada alfabéticamente de tipos de scaffold disponibles, o lista vacía si hay error.
    """
    config_dir = get_config_dir_path()
    scaffold_types_file = config_dir / SCAFFOLD_TYPES_FILE
    
    if not scaffold_types_file.exists():
        if debug_mode:
            print(f"[DEBUG] Archivo de tipos de scaffold no encontrado: {scaffold_types_file}", file=sys.stderr)
        return []
    
    try:
        scaffold_types = []
        current_type = None
        
        with open(scaffold_types_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                
                # Ignorar líneas vacías y comentarios
                if not line or line.startswith("#"):
                    continue
                
                # Detectar inicio de sección [types]
                if line == "[types]":
                    continue
                
                # Detectar definición de tipo (termina con = {)
                if line.endswith("= {"):
                    current_type = line[:-3].strip()
                    scaffold_types.append(current_type)
                    continue
                
                # Ignorar líneas dentro de la definición del tipo
                if current_type and line.startswith("}"):
                    current_type = None
        
        # Ordenar la lista alfabéticamente
        scaffold_types.sort()
        
        if debug_mode:
            print(f"[DEBUG] Tipos de scaffold cargados (ordenados): {scaffold_types}", file=sys.stderr)
            
        return scaffold_types
        
    except Exception as e:
        if debug_mode:
            print(f"[DEBUG] Error al cargar tipos de scaffold: {e}", file=sys.stderr)
        return []

# --- Constantes para Workspaces ---
WORKSPACES_DEF_FILE_NAME = "workspaces.def"
DEFAULT_WORKSPACE = "~/devs"  # Workspace por defecto si no se especifica otro

def get_workspaces_file_path(config_dir_path: Path) -> Path:
    """Devuelve la ruta absoluta al archivo de definición de workspaces."""
    return config_dir_path / WORKSPACES_DEF_FILE_NAME

def load_workspaces(debug_mode: bool = False) -> list[str]:
    """
    Carga la lista de workspaces desde el archivo workspaces.def.
    Si el archivo no existe, lo crea con el workspace por defecto.
    Si está vacío o hay un error al leerlo, usa DEFAULT_WORKSPACE.
    
    Returns:
        list[str]: Lista de rutas de workspaces, expandidas (sin ~)
    """
    config_dir = get_config_dir_path()
    workspaces_file = get_workspaces_file_path(config_dir)

    # Crear archivo .def si no existe
    if not workspaces_file.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(workspaces_file, "w", encoding="utf-8") as f:
                f.write(f"{DEFAULT_WORKSPACE}\n")
            if debug_mode:
                print(f"[DEBUG] Archivo '{workspaces_file.name}' no encontrado. Creado con workspace por defecto.")
        except Exception as e:
            if debug_mode:
                print(f"[DEBUG] Error al crear '{workspaces_file.name}': {e}")
            return [str(Path(DEFAULT_WORKSPACE).expanduser())]

    # Leer workspaces
    try:
        with open(workspaces_file, "r", encoding="utf-8") as f:
            workspaces = [
                str(Path(line.strip()).expanduser())
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
        if workspaces:
            if debug_mode:
                print(f"[DEBUG] Workspaces cargados: {workspaces}")
            return workspaces
        else:
            if debug_mode:
                print("[DEBUG] Archivo de workspaces vacío, usando workspace por defecto.")
            return [str(Path(DEFAULT_WORKSPACE).expanduser())]
    except Exception as e:
        if debug_mode:
            print(f"[DEBUG] Error leyendo archivo de workspaces ({e}), usando workspace por defecto.")
        return [str(Path(DEFAULT_WORKSPACE).expanduser())]

def get_default_workspace() -> Path:
    """Obtiene el workspace por defecto (el primero de la lista)."""
    workspaces = load_workspaces()
    return Path(workspaces[0]) if workspaces else Path(DEFAULT_WORKSPACE).expanduser()

def validate_workspace_path(workspace_path: str | Path) -> Path:
    """
    Valida y normaliza una ruta de workspace.
    
    Args:
        workspace_path: Ruta del workspace (puede ser relativa o absoluta)
        
    Returns:
        Path: Ruta absoluta normalizada del workspace
        
    Raises:
        ValueError: Si la ruta no es válida o no se puede crear
    """
    try:
        # Convertir a Path y expandir ~
        path = Path(workspace_path).expanduser().resolve()
        
        # Crear el directorio si no existe
        path.mkdir(parents=True, exist_ok=True)
        
        return path
    except Exception as e:
        raise ValueError(f"Ruta de workspace inválida: {e}")

def validate_project_path(workspace_path: Path, project_name: str) -> Path:
    """
    Valida y normaliza una ruta de proyecto dentro de un workspace.
    
    Args:
        workspace_path: Ruta del workspace (debe ser absoluta)
        project_name: Nombre del proyecto (solo nombre de carpeta)
        
    Returns:
        Path: Ruta absoluta normalizada del proyecto
        
    Raises:
        ValueError: Si el nombre del proyecto no es válido o la ruta no se puede crear
    """
    if not workspace_path.is_absolute():
        raise ValueError("La ruta del workspace debe ser absoluta")
        
    # Validar nombre del proyecto
    if not project_name or "/" in project_name or "\\" in project_name:
        raise ValueError("El nombre del proyecto debe ser un nombre de carpeta válido")
        
    try:
        # Construir y normalizar la ruta del proyecto
        project_path = (workspace_path / project_name).resolve()
        
        # Crear el directorio si no existe
        project_path.mkdir(parents=True, exist_ok=True)
        
        return project_path
    except Exception as e:
        raise ValueError(f"Error al crear/validar ruta del proyecto: {e}")

def main():
    # 1. Crear parser base con argumento --path
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "-p", "--path",
        type=Path,
        default=Path("."),
        help="Ruta al directorio raíz del proyecto"
    )

    # 2. Parser principal
    parser = argparse.ArgumentParser(
        description="Gestor de metadatos para proyectos de desarrollo",
        parents=[base_parser]
    )
    
    # 3. Configurar subcomandos con parser base
    subparsers = parser.add_subparsers(
        dest="command",
        title="subcomandos",
        help="Acciones disponibles",
        required=True  # Obligar a usar un subcomando
    )
    
    # Subcomando 'show'
    parser_show = subparsers.add_parser(
        "show",
        help="Muestra la configuración actual del proyecto",
        parents=[base_parser]
    )
    parser_show.set_defaults(func=handle_show_config)
    
    # Subcomando 'init'
    parser_init = subparsers.add_parser(
        "init",
        help="Inicializa un nuevo proyecto",
        parents=[base_parser]
    )
    # Agregar argumentos específicos para init
    parser_init.add_argument(
        "-w", "--workspace",
        type=str,
        help="Ruta del workspace donde se creará el proyecto"
    )
    parser_init.add_argument(
        "-f", "--force",
        action="store_true",
        help="Forzar la actualización del workspace existente"
    )
    parser_init.set_defaults(func=handle_init_config)
    
    # Subcomando 'edit'
    parser_edit = subparsers.add_parser(
        "edit", 
        help="Edita la configuración interactivamente",
        parents=[base_parser]
    )
    parser_edit.set_defaults(func=handle_edit_config)

    # Subcomando 'setup-ci'
    parser_setup_ci = subparsers.add_parser(
        "setup-ci",
        help="Configura herramientas de CI y pre-commit",
        parents=[base_parser]
    )
    parser_setup_ci.set_defaults(func=handle_setup_ci)
    
    # 4. Parsear argumentos
    args = parser.parse_args()
    
    # 5. Procesar ruta y cargar datos
    project_base_dir = args.path.resolve()
    meta_file = get_meta_file_path(project_base_dir)
    project_data = load_project_data(meta_file)
    
    # 6. Ejecutar lógica principal con manejo de errores
    try:
        # Mostrar banner con información del proyecto
        show_banner(
            schema_version_val=project_data.get("schema_version"),
            config_file_name=meta_file.name,
            project_name_val=project_data.get("repository", {}).get("name")
        )
        
        # Ejecutar el comando seleccionado
        args.func(args, project_data)
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        if SCRIPT_DEBUG_MODE:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()