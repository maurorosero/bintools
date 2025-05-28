#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Este script se ejecuta antes de que cookiecutter genere el proyecto.
Su propósito es validar las opciones seleccionadas y asegurar que todo esté correcto
antes de la generación del proyecto.
"""

import sys
import re

def validate_workspace_slug(slug: str) -> bool:
    """
    Valida que el slug del workspace sea válido.
    Debe ser un nombre de directorio válido y no contener caracteres especiales.
    """
    if not slug:
        print("Error: El nombre del workspace no puede estar vacío")
        return False

    # Validar que sea un nombre de directorio válido
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', slug):
        print("Error: El nombre del workspace solo puede contener letras, números, guiones y guiones bajos")
        print("       y debe comenzar con una letra o número")
        return False

    return True

def main():
    """
    Función principal que valida todas las opciones seleccionadas.
    """
    # Obtener las variables de cookiecutter
    workspace_slug = "{{ cookiecutter.workspace_slug }}"

    # Validar todas las opciones
    validations = [
        validate_workspace_slug(workspace_slug)
    ]

    # Si alguna validación falla, terminar con error
    if not all(validations):
        sys.exit(1)

if __name__ == "__main__":
    main()
