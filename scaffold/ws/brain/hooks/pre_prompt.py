#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Este script se ejecuta antes de que cookiecutter genere el proyecto.
Su propósito es preparar o modificar variables que se usarán en la generación.
"""

import json
import subprocess
from pathlib import Path
from typing import List
import os
import sys

# Lista de fallback en caso de error
FALLBACK_LICENSES = [
    "No",
    "MIT",
    "Apache-2.0",
    "GPL-3.0",
    "LGPL-3.0",
    "BSD-3-Clause",
    "Mozilla Public License 2.0",
    "Unlicense",
    "Proprietary"
    ]

FALLBACK_COMMITLINT = [
    "No",
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert"
]

def get_git_config_value(key, fallback):
    try:
        return subprocess.check_output(
            ["git", "config", "--global", key],
            text=True
        ).strip() or fallback
    except subprocess.CalledProcessError:
        return fallback

def get_template_dir() -> Path | None:
    """
    Obtiene la ruta del template buscando el directorio de licencias.
    Primero busca en $HOME/bin/scaffold/licenses, luego busca recursivamente
    cualquier directorio scaffold/licenses dentro de $HOME.
    Retorna la ruta del template (scaffold/ws/brain) si encuentra el directorio de licencias.
    Retorna None si no se puede determinar.
    """
    try:
        # Obtener $HOME
        home = Path.home()
        
        # Intentar primero en $HOME/bin/scaffold
        bin_scaffold = home / "bin" / "scaffold"
        if bin_scaffold.exists():
            return home / "bin" / "scaffold" / "ws" / "brain"
            
        # Si no está en bin, buscar recursivamente en $HOME
        for scaffold_dir in home.rglob("scaffold"):
            if scaffold_dir.is_dir():
                template_dir = scaffold_dir.parent / "ws" / "brain"
                if template_dir.exists():
                    return template_dir
                    
        return None
        
    except Exception as e:
        print(f"Error al buscar el directorio scaffolding: {e}")
        return None

def get_license_list() -> List[str]:
    """
    Obtiene la lista de licencias desde los archivos .md en la carpeta licenses.
    Retorna una lista con 'No' como primer elemento y el resto ordenado alfabéticamente.
    Si hay algún error, retorna la lista de fallback.
    """
    try:
        # Obtener la ruta del template
        template_dir = get_template_dir()
        if template_dir is None:
            licenses_dir = Path("~/bin/scaffold/licenses")
        else:
            # Construir la ruta al directorio de licencias relativa al template
            licenses_dir = template_dir.parent.parent / "licenses"
            
        if not licenses_dir.exists():
            return FALLBACK_LICENSES
            
        # Obtener todos los archivos .md
        license_files = list(licenses_dir.glob("*.md"))
        if not license_files:
            return FALLBACK_LICENSES
            
        # Extraer nombres sin extensión y ordenar
        licenses = ["No"] + sorted([f.stem for f in license_files])
        return licenses
        
    except Exception as e:
        print(f"Error al obtener la lista de licencias: {e}")
        return FALLBACK_LICENSES

def get_commitlint_list() -> List[str]:
    """
    Obtiene la lista de commitlint desde los archivos commitlint.config.*.js.def en la carpeta commit-format.
    Retorna una lista con 'No' como primer elemento y el resto ordenado alfabéticamente.
    Si hay algún error, retorna la lista de fallback.
    """
    try:
        # Obtener la ruta del template
        template_dir = get_template_dir()
        if template_dir is None:
            commitlint_dir = Path("~/bin/scaffold/commit-format")
        else:
            # Construir la ruta al directorio de licencias relativa al template
            commitlint_dir = template_dir.parent.parent / "commit-format"
            
        if not commitlint_dir.exists():
            return FALLBACK_COMMITLINT
            
        # Obtener todos los archivos commitlint.config.*.js.def
        commitlint_files = list(commitlint_dir.glob("commitlint.config.*.js.def"))
        if not commitlint_files:
            return FALLBACK_COMMITLINT
            
            
        # Extraer nombres sin extensión y ordenar
        commitlints = ["No"] + sorted([f.stem.split(".")[2] for f in commitlint_files])
        return commitlints
        
    except Exception as e:
        print(f"Error al obtener la lista de commit formats: {e}")
        return FALLBACK_COMMITLINT
    
def update_cookiecutter_json():
    """
    Actualiza el archivo cookiecutter.json con la lista de licencias.
    Si no se pueden obtener las licencias del directorio, usa la lista de fallback.
    """
    try:
        # Obtener la ruta al cookiecutter.json
        current_dir = Path(__file__).parent
        cookiecutter_path = current_dir.parent / "cookiecutter.json"
        
        if not cookiecutter_path.exists():
            print(f"Error: No se encontró cookiecutter.json en {cookiecutter_path}")
            return
            
        # Leer el archivo actual
        with open(cookiecutter_path, 'r', encoding='utf-8') as f:
            cookiecutter_data = json.load(f)
            
        # Obtener la nueva lista de licencias (usará fallback si es necesario)
        new_licenses = get_license_list()

        # Obtener la nueva lista de commit formats (usará fallback si es necesario)
        new_commitlints = get_commitlint_list()

        # Actualizar la lista de licencias
        cookiecutter_data["license"] = new_licenses

        # Actualizar la lista de commit formats
        cookiecutter_data["commit_format"] = new_commitlints

        # Valores por defecto si git no los tiene
        default_name = "Jane Doe"
        default_email = "jane.doe@example.com"

        # Obtener desde git o usar fallback
        cookiecutter_data["author_name"] = get_git_config_value("user.name", default_name)
        cookiecutter_data["author_email"] = get_git_config_value("user.email", default_email)

        # Guardar los cambios con formato correcto
        with open(cookiecutter_path, 'w', encoding='utf-8') as f:
            json.dump(cookiecutter_data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error al actualizar cookiecutter.json: {e}")

if __name__ == "__main__":
    update_cookiecutter_json()
