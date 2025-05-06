#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# project_manager.py - Herramienta para gestionar metadatos de proyecto en un archivo TOML.
# -----------------------------------------------------------------------------
#
try:
    import tomllib
except ImportError:
    # Fallback para Python < 3.11
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: Se necesita la biblioteca 'tomli' para versiones de Python < 3.11.")
        print("Por favor, instálala con: pip install tomli")
        sys.exit(1)

import tomli_w
import questionary
from pathlib import Path
import sys
import os
import argparse # Importar argparse

# --- Constantes (Ya no globales fijas, se definirán en main) ---
# PROJECT_DIR = Path(".project") # Movido a main
# PROJECT_META_FILENAME = "project_meta.toml" # Movido a main
# PROJECT_META_FILE = PROJECT_DIR / PROJECT_META_FILENAME # Movido a main

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

        return answers

    except KeyboardInterrupt:
        # Si se interrumpe en medio de una pregunta
        return None
    # Eliminar la lógica de fallback compleja, ya que ahora manejamos None en cada .ask()
    # else:
    #    # ... (código fallback eliminado) ...


def edit_repository_info(repo_data, is_initial_setup=False):
    """Formulario para editar info del repo."""
    is_created = repo_data.get("created_flag", False) or repo_data.get("url")

    if is_created:
        questionary.print("--- Info Repositorio (Creado - Campos clave sólo lectura) ---", style="bold")
        questionary.print(f"  Nombre:       {repo_data.get('name', 'N/A')}")
        questionary.print(f"  Propietario:  {repo_data.get('owner_name', 'N/A')} ({repo_data.get('owner_type', 'N/A')})")
        questionary.print(f"  Visibilidad: {repo_data.get('visibility', 'N/A')}")
        # Mostrar plataforma y URL si existe
        platform_display = repo_data.get('platform', 'N/A')
        platform_url_display = repo_data.get('platform_url')
        if platform_url_display:
            platform_display += f" ({platform_url_display})"
        questionary.print(f"  Plataforma:   {platform_display}")
        questionary.print(f"  URL Repo:     {repo_data.get('url', 'No establecido')}")
        repo_data['description'] = questionary.text("Descripción:", default=repo_data.get('description', "")).ask() or repo_data.get('description', "")
    else:
        if not is_initial_setup:
            questionary.print("--- Info Repositorio (Campos requeridos *) ---", style="bold")
            answers = prompt_for_required_repo_info(repo_data)
            if not answers: return # User cancelled
            repo_data.update(answers)
        else:
            questionary.print("--- Info Repositorio (Opciones Adicionales) ---", style="bold")

        repo_data['description'] = questionary.text("Descripción:", default=repo_data.get('description', "")).ask() or repo_data.get('description', "")
        if repo_data['description'] is None: return # Check for cancellation

        init_options = repo_data.get("init_options", {})
        init_options['add_readme'] = questionary.confirm("¿Inicializar con README?", default=init_options.get('add_readme', True)).ask()
        if init_options['add_readme'] is None: return

        init_options['add_gitignore'] = questionary.confirm("¿Añadir .gitignore?", default=init_options.get('add_gitignore', True)).ask()
        if init_options['add_gitignore'] is None: return
        if init_options['add_gitignore']:
            init_options['gitignore_template'] = questionary.text("Plantilla .gitignore (ej., Python, Node, vacío para ninguno):", default=init_options.get('gitignore_template', "Python")).ask() or init_options.get('gitignore_template', "Python")
            if init_options['gitignore_template'] is None: return

        init_options['add_license'] = questionary.confirm("¿Añadir LICENSE?", default=init_options.get('add_license', True)).ask()
        if init_options['add_license'] is None: return
        if init_options['add_license']:
            init_options['license_template'] = questionary.text("Plantilla Licencia (ID SPDX, ej., mit, gpl-3.0):", default=init_options.get('license_template', "mit")).ask() or init_options.get('license_template', "mit")
            if init_options['license_template'] is None: return

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


# --- Lógica Principal (Modificada para usar argparse y pasar rutas) ---

def main():
    """Función principal de la herramienta."""
    # --- Configurar y Parsear Argparse PRIMERO ---
    parser = argparse.ArgumentParser(description="Gestiona el archivo de metadatos del proyecto (project_meta.toml).")
    parser.add_argument(
        "-p", "--path",
        default=".",
        help="Ruta al directorio del proyecto (por defecto: directorio actual)."
    )
    # Parsear argumentos. Si es --help, argparse saldrá aquí.
    args = parser.parse_args()
    # ------------------------------------------

    # --- Definir rutas basadas en el argumento (solo se ejecuta si no fue --help) ---
    project_base_path = Path(args.path).resolve() # Resuelve a ruta absoluta
    project_meta_dir = project_base_path / ".project"
    project_meta_file = project_meta_dir / "project_meta.toml"

    questionary.print(f"Operando en el directorio del proyecto: {project_base_path}")
    # ------------------------------------------

    # --- Check y Flujo de Creación/Edición ---
    if not project_meta_file.is_file():
        if project_meta_file.exists():
             questionary.print(f"Advertencia: La ruta {project_meta_file} existe pero no es un archivo.", style="fg:cyan")

        questionary.print(f"Archivo de metadatos {project_meta_file} no encontrado. ¡Creándolo!", style="fg:cyan")
        project_data = get_default_structure()

        questionary.print("--- Información Repositorio (Requerida*) ---", style="bold")
        # Usar try-except en caso de que questionary falle o sea interrumpido
        try:
            required_answers = prompt_for_required_repo_info(project_data["repository"])
        except Exception as e:
            print(f"Error durante la entrada: {e}")
            required_answers = None

        if required_answers is None:
             print("Operación cancelada.")
             sys.exit(0)
        project_data["repository"].update(required_answers)

        # Asegurar que los flujos de confirmación también manejen None/Cancelación
        try:
            fill_optional_repo = questionary.confirm("¿Rellenar detalles opcionales del repositorio ahora? (Descripción, Opciones Init)").ask()
            if fill_optional_repo is None: raise KeyboardInterrupt # Tratar cancelación como interrupción
            if fill_optional_repo:
                 edit_repository_info(project_data["repository"], is_initial_setup=True)

            fill_project_details = questionary.confirm("¿Rellenar detalles del proyecto ahora?").ask()
            if fill_project_details is None: raise KeyboardInterrupt
            if fill_project_details:
                 edit_project_details(project_data["project_details"])
        except KeyboardInterrupt:
            print("Operación cancelada durante entrada opcional.")
            # Decidir si guardar lo mínimo o salir sin guardar
            save_minimal = questionary.confirm("¿Guardar la información mínima requerida recopilada hasta ahora?").ask()
            if save_minimal:
                 save_project_data(project_data, project_meta_file)
                 questionary.print(f"Metadatos mínimos del proyecto guardados en {project_meta_file}.", style="fg:green")
            else:
                 print("Saliendo sin guardar.")
            sys.exit(0)


        save_project_data(project_data, project_meta_file) # Pasar ruta
        questionary.print(f"Metadatos iniciales del proyecto guardados en {project_meta_file}.", style="fg:green")
        questionary.print("Puedes ejecutar esta herramienta de nuevo para editar detalles.")

    else:
        # --- Flujo de Edición ---
        project_data = load_project_data(project_meta_file) # Pasar ruta
        # Crear copia profunda para detectar cambios reales sería mejor
        # import copy
        # original_data = copy.deepcopy(project_data) # Necesitaría import copy
        original_data_str = str(project_data) # Comparación simple por ahora
        modified = False

        while True:
            try:
                # Reevaluar si hay cambios antes de mostrar el menú
                current_data_str = str(project_data)
                modified = (current_data_str != original_data_str)
                prompt_title = "Selecciona acción:" + (" (Hay cambios sin guardar)" if modified else "")

                action = questionary.select(
                    prompt_title,
                    choices=[
                        "Editar Info Repositorio",
                        "Editar Detalles Proyecto",
                        "Editar Metadatos Adicionales (Manual)",
                        # --- Opción futura ---
                        # questionary.Choice("Crear Repositorio Remoto", disabled=project_data["repository"].get("created_flag")),
                        "Guardar Cambios",
                        "Salir (Descartar Cambios)",
                        "Guardar y Salir"
                    ],
                    qmark=">", pointer="->"
                ).ask()
            except KeyboardInterrupt:
                action = None # Tratar Ctrl+C como None


            if action == "Editar Info Repositorio":
                edit_repository_info(project_data["repository"])
            elif action == "Editar Detalles Proyecto":
                edit_project_details(project_data["project_details"])
            elif action == "Editar Metadatos Adicionales (Manual)":
                 new_metadata = edit_additional_metadata(project_data.get("additional_metadata", {}), project_meta_file)
                 project_data["additional_metadata"] = new_metadata
            # elif action == "Crear Repositorio Remoto":
            #     pass # Lógica futura
            elif action == "Guardar Cambios":
                save_project_data(project_data, project_meta_file) # Pasar ruta
                original_data_str = str(project_data) # Actualizar estado guardado
                modified = False # Marcar como no modificado después de guardar
            elif action == "Salir (Descartar Cambios)":
                if modified:
                    confirm_exit = questionary.confirm("¿Descartar cambios sin guardar?").ask()
                    if not confirm_exit:
                        continue # Volver al menú
                print("Saliendo sin guardar.")
                sys.exit(0)
            elif action == "Guardar y Salir":
                save_project_data(project_data, project_meta_file) # Pasar ruta
                print("Saliendo.")
                sys.exit(0)
            elif action is None: # User pressed Ctrl+C or equivalent
                 if modified:
                     confirm_exit = questionary.confirm("Tienes cambios sin guardar. ¿Salir de todas formas?").ask()
                     if not confirm_exit:
                          continue # Volver al menú si no quiere salir
                 print("Saliendo.") # Añadir newline para limpieza
                 sys.exit(0)


if __name__ == "__main__":
    # Pequeño ajuste para mejor manejo de interrupciones globales
    try:
        main()
    except KeyboardInterrupt:
        print("Operación interrumpida por el usuario. Saliendo.")
        sys.exit(1) 