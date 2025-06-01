#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Commitlint Wrapper - Script wrapper multiplataforma para ejecutar commitlint y validar mensajes de commit.
Este script reemplaza al commitlint-wrapper.sh y funciona en cualquier sistema operativo.

Copyright (C) 2025 MAURO ROSERO PÉREZ
License: GPLv3

File: commitlint-wrapper.py
Version: 0.1.0
Author: Mauro Rosero P. <mauro.rosero@gmail.com>
Created: 2025-05-19 20:48:14

This file is managed by template_manager.py.
Any changes to this header will be overwritten on the next fix.

HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE
"""

import sys
import subprocess
import shutil
import json
import re
from pathlib import Path

def check_npx_installed() -> bool:
    """Verifica si npx está instalado en el sistema."""
    return shutil.which('npx') is not None

def install_commitlint() -> bool:
    """Instala commitlint globalmente si no está instalado."""
    try:
        print("Instalando dependencias de commitlint...")
        subprocess.run(
            ["npm", "install", "-g", "@commitlint/cli"],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar commitlint: {e.stderr}")
        return False

def get_allowed_tags_from_config(config_file: Path) -> list:
    """
    Extrae dinámicamente los tags permitidos desde el archivo de configuración commitlint.config.js.

    Args:
        config_file: Ruta al archivo commitlint.config.js

    Returns:
        Lista de tags permitidos o lista vacía si hay error
    """
    try:
        if not config_file.exists():
            return []

        # Leer el contenido del archivo
        content = config_file.read_text(encoding='utf-8')

        # Buscar el array de type-enum usando regex
        # Patrón que busca 'type-enum': [nivel, 'always', [array_de_tags]]
        pattern = r"'type-enum':\s*\[\s*\d+,\s*'always',\s*\[(.*?)\]"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return []

        # Extraer los tags del array
        tags_section = match.group(1)

        # Buscar todas las cadenas entre comillas simples
        tag_pattern = r"'([A-Z]+)'"
        tags = re.findall(tag_pattern, tags_section)

        return tags

    except Exception as e:
        print(f"Advertencia: No se pudieron extraer los tags de la configuración: {e}")
        # Fallback a tags básicos si hay error
        return ["FEAT", "FIX", "DOCS", "CHORE"]

def get_allowed_tags(config_file: Path) -> list:
    """
    Retorna la lista de TAGS permitidos leyéndolos dinámicamente desde la configuración.

    Args:
        config_file: Ruta al archivo de configuración commitlint

    Returns:
        Lista de tags permitidos
    """
    tags = get_allowed_tags_from_config(config_file)

    # Si no se pudieron extraer, usar fallback básico
    if not tags:
        tags = ["FEAT", "FIX", "DOCS", "CHORE"]

    return tags

def main():
    """Función principal que ejecuta commitlint y maneja los errores."""
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("Error: Se requiere el archivo del mensaje de commit como argumento")
        sys.exit(1)

    commit_msg_file = Path(sys.argv[1])
    if not commit_msg_file.exists():
        print(f"Error: No se encontró el archivo {commit_msg_file}")
        sys.exit(1)

    # Leer el contenido del mensaje de commit para diagnóstico
    try:
        commit_msg = commit_msg_file.read_text()
    except Exception as e:
        commit_msg = f"No se pudo leer el mensaje de commit: {e}"

    # Verificar/instalar npx y commitlint
    if not check_npx_installed():
        print("Error: npx no está instalado. Por favor, instala Node.js y npm")
        sys.exit(1)

    try:
        # Obtener la ruta al archivo de configuración
        config_file = Path(__file__).parent / "commitlint.config.js"
        if not config_file.exists():
            print(f"Error: No se encontró el archivo de configuración: {config_file}")
            sys.exit(1)

        # Intentar ejecutar commitlint con la configuración local y verbosidad
        result = subprocess.run(
            ["npx", "commitlint", "--config", str(config_file), "--edit", str(commit_msg_file), "--verbose"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("\n=== Detalles del Error de Validación de Commit ===", file=sys.stderr)
            print("\nMensaje de commit actual:", file=sys.stderr)
            print("---", file=sys.stderr)
            print(commit_msg, file=sys.stderr)
            print("---", file=sys.stderr)
            if result.stdout:
                print("\nSalida de commitlint:", file=sys.stderr)
                print(result.stdout, file=sys.stderr)
            if result.stderr:
                print("\nError de commitlint:", file=sys.stderr)
                print(result.stderr, file=sys.stderr)
            print("\nFormato esperado:", file=sys.stderr)
            print("[TAG] (#Issue) Descripción", file=sys.stderr)
            print("\nTAGS permitidos:", ", ".join(f"[{tag}]" for tag in get_allowed_tags(config_file)), file=sys.stderr)
            print("\nEjemplos válidos:", file=sys.stderr)
            print("[FEAT] (#123) Agrega nueva funcionalidad", file=sys.stderr)
            print("[FIX] (#456) Corrige error en el login", file=sys.stderr)
            print("[DOCS] (#789) Actualiza documentación de la API", file=sys.stderr)
            print("\nLimpiando archivo temporal...", file=sys.stderr)
            commit_msg_file.unlink(missing_ok=True)
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print("\n=== Error Ejecutando Commitlint ===", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        if e.stdout:
            print("\nSalida estándar:", file=sys.stderr)
            print(e.stdout, file=sys.stderr)
        if e.stderr:
            print("\nError estándar:", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("\n=== Error Inesperado ===", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        print("\nTraceback:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
