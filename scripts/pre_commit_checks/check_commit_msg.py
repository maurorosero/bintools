#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-15 17:09:10
# Version: 0.1.0
#
# check_commit_msg.py - Description placeholder
# -----------------------------------------------------------------------------
#
import toml
import subprocess
import sys
import os

"""
Script de pre-commit para validar mensajes de commit con commitlint,
ajustando dinámicamente la obligatoriedad de referenciar un issue
basado en la configuración en .project/project_meta.toml.
"""

PROJECT_META_PATH = ".project/project_meta.toml"
COMMITLINT_CONFIG_FILE = "commitlint.config.js" # Asegúrate que esta ruta es correcta

def main():
    """
    Función principal del script.
    1. Lee la configuración de 'require_issue' desde project_meta.toml.
    2. Establece la variable de entorno REQUIRE_ISSUE_FROM_META.
    3. Ejecuta commitlint con el mensaje de commit proporcionado.
    """
    require_issue_flag = False
    try:
        # Navegar a la raíz del repositorio para encontrar .project/project_meta.toml
        # Esto es importante porque pre-commit puede ejecutar hooks desde .git/hooks
        git_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
        meta_file_path = os.path.join(git_root, PROJECT_META_PATH)

        if not os.path.exists(meta_file_path):
            print(f"Advertencia: Archivo de metadatos del proyecto no encontrado en '{meta_file_path}'.")
            print("Se asumirá 'require_issue = false'.")
        else:
            with open(meta_file_path, "r", encoding="utf-8") as f:
                meta_config = toml.load(f)
            require_issue_flag = meta_config.get("repository", {}).get("workflow_config", {}).get("require_issue", False)
            if require_issue_flag:
                print(f"Info: '{PROJECT_META_PATH}' indica 'require_issue = true'. Se forzará la referencia a un issue.")
            else:
                print(f"Info: '{PROJECT_META_PATH}' indica 'require_issue = false'. La referencia a un issue es opcional.")

    except FileNotFoundError:
        # Esto no debería ocurrir si la lógica de git_root es correcta y el archivo existe
        print(f"Advertencia: Archivo de metadatos del proyecto no encontrado en '{PROJECT_META_PATH}'.")
        print("Se asumirá 'require_issue = false'.")
    except Exception as e:
        print(f"Advertencia: Error al leer o parsear '{PROJECT_META_PATH}': {e}")
        print("Se asumirá 'require_issue = false'.")

    # El mensaje de commit es pasado como el primer argumento por pre-commit (en modo commit-msg)
    if len(sys.argv) < 2:
        print("Error: No se proporcionó la ruta al archivo del mensaje de commit.", file=sys.stderr)
        sys.exit(1)
    commit_msg_filepath = sys.argv[1]

    # Configurar variable de entorno para commitlint.config.js
    env = os.environ.copy()
    env["REQUIRE_ISSUE_FROM_META"] = "true" if require_issue_flag else "false"

    # Asegúrate que commitlint y su configuración son accesibles.
    # Si commitlint.config.js no está en la raíz, ajusta la ruta.
    config_file_path_abs = os.path.join(git_root, COMMITLINT_CONFIG_FILE)
    if not os.path.exists(config_file_path_abs):
        print(f"Error: Archivo de configuración de commitlint no encontrado en '{config_file_path_abs}'.", file=sys.stderr)
        sys.exit(1)

    command = [
        "npx",
        "commitlint",
        "--edit", commit_msg_filepath,
        "--config", config_file_path_abs
    ]

    try:
        # print(f"Debug: Ejecutando comando: {' '.join(command)}")
        # print(f"Debug: Con entorno: REQUIRE_ISSUE_FROM_META={env['REQUIRE_ISSUE_FROM_META']}")
        # print(f"Debug: Contenido del mensaje de commit en '{commit_msg_filepath}':")
        # with open(commit_msg_filepath, 'r', encoding='utf-8') as f_msg:
        #     print(f_msg.read())

        process = subprocess.run(command, env=env, capture_output=True, text=True, check=False, cwd=git_root)

        if process.returncode != 0:
            print(f"⛔ Error de validación del mensaje de commit (por commitlint):")
            # commitlint suele dar buena salida en stdout incluso con errores
            if process.stdout:
                print(process.stdout.strip())
            if process.stderr:
                print(process.stderr.strip(), file=sys.stderr)
            sys.exit(process.returncode)
        else:
            print("✅ Mensaje de commit validado exitosamente por commitlint.")
            if process.stdout: # Mostrar output si lo hay (puede ser informativo)
                print(process.stdout.strip())
            sys.exit(0)

    except FileNotFoundError:
        print("Error: 'npx' (y por tanto 'commitlint') no encontrado. Asegúrate de que Node.js y npm estén instalados y en el PATH.", file=sys.stderr)
        print("Puedes necesitar instalar commitlint globalmente o como dependencia del proyecto.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado al ejecutar commitlint: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
