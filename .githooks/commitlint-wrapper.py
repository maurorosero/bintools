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

def get_allowed_tags() -> list:
    """Retorna la lista de TAGS permitidos para mostrar en el mensaje de error."""
    return [
        "IMPROVE", "FIX", "DOCS", "STYLE", "REFACTOR",
        "PERF", "TEST", "BUILD", "CI", "CHORE"
    ]

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

        # Intentar ejecutar commitlint con la configuración local
        result = subprocess.run(
            ["npx", "commitlint", "--config", str(config_file), "--edit", str(commit_msg_file)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # Si falla, limpiar el archivo y mostrar sugerencia
            print("Mensaje de commit inválido. Limpiando archivo temporal...")
            commit_msg_file.unlink(missing_ok=True)
            
            print("\nSugerencia: Usa el formato [TAG] descripción")
            print("TAGS permitidos:", ", ".join(f"[{tag}]" for tag in get_allowed_tags()))
            
            # Mostrar el error de commitlint si existe
            if result.stdout:
                print("\nDetalles del error:")
                print(result.stdout)
            if result.stderr:
                print("\nError:")
                print(result.stderr)
                
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando commitlint: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main() 