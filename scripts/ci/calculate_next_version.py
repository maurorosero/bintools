#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-13 00:27:13
# Version: 0.1.0
#
# calculate_next_version.py - Calcula la siguiente versión SemVer global basándose en el último release de GitHub
# -----------------------------------------------------------------------------
#
# -*- coding: utf-8 -*-

"""
Calcula la siguiente versión SemVer global basándose en el último release de GitHub
y el tipo de incremento determinado (major, minor, patch) o la falta de él.
"""

import os
import re
import subprocess
import sys
import argparse

# Tags de commit que cuentan para el número de PATCH en un release MINOR
PATCH_COUNT_TAGS = re.compile(r'^\s*\[(FIX|STYLE)\]')

def run_command(command_str, check=True):
    """Ejecuta un comando y devuelve la salida o None en error."""
    try:
        cmd_list = command_str.split()
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=check, encoding='utf-8')
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # No imprimir error si check=False y falla (ej. git describe sin tags)
        if check:
            print(f"Error ejecutando command '{command_str}': {e}\nStderr: {e.stderr}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: Comando '{cmd_list[0]}' no encontrado.", file=sys.stderr)
        sys.exit(1)

def get_latest_release_tag():
    """Obtiene el tag del último release de GitHub usando gh CLI."""
    # Asume que gh está instalado y autenticado en el runner de CI
    tag = run_command("gh release list --limit 1 --json tagName --jq .[0].tagName")
    if tag and tag.startswith('v'):
        print(f"Último tag de release encontrado: {tag}", file=sys.stderr)
        return tag
    else:
        print("No se encontró un último release válido (tag vX.Y.Z).", file=sys.stderr)
        return None

def parse_version(version_str):
    """Parsea 'X.Y.Z' -> (X, Y, Z). Devuelve (0,0,0) si es inválido."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if match:
        return tuple(map(int, match.groups()))
    return (0, 0, 0) # Default para casos inválidos o iniciales

def count_patch_commits(since_ref):
    """Cuenta commits con [FIX] o [STYLE] desde una referencia dada."""
    if not since_ref: # Si no hay referencia previa, no hay commits relevantes para contar
        return 0

    log_output = run_command(f"git log {since_ref}..HEAD --pretty=%s")
    if not log_output:
        return 0

    count = 0
    for line in log_output.splitlines():
        if PATCH_COUNT_TAGS.match(line):
            count += 1
    print(f"Encontrados {count} commits tipo PATCH ([FIX]/[STYLE]) desde {since_ref}", file=sys.stderr)
    return count

def calculate_next_version(current_version_tuple, increment_type, last_tag_name):
    """Calcula la tupla de la siguiente versión."""
    major, minor, patch = current_version_tuple

    if increment_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif increment_type == 'minor':
        minor += 1
        # El patch se calcula contando commits [FIX]/[STYLE] desde el último tag
        patch = count_patch_commits(last_tag_name)
    elif increment_type == 'patch':
        patch += 1
    else: # increment_type es None o desconocido
        return None # No hay cambio

    return (major, minor, patch)

def main():
    parser = argparse.ArgumentParser(description="Calcula la siguiente versión SemVer global.")
    parser.add_argument("increment_type",
                        choices=['major', 'minor', 'patch', 'none'],
                        help="Tipo de incremento determinado por el workflow (major, minor, patch, none).")

    args = parser.parse_args()

    if args.increment_type == 'none':
        print("No se requiere incremento de versión.", file=sys.stderr)
        print("NONE") # Salida para indicar que no hay nueva versión
        sys.exit(0)

    last_tag_name = get_latest_release_tag()
    current_version_str = "0.0.0"
    if last_tag_name:
        # Quita la 'v' inicial si existe
        current_version_str = last_tag_name[1:] if last_tag_name.startswith('v') else last_tag_name

    current_version_tuple = parse_version(current_version_str)
    if current_version_tuple == (0, 0, 0) and last_tag_name:
         print(f"Warning: No se pudo parsear la versión del último tag '{last_tag_name}'. Tratando como 0.0.0.", file=sys.stderr)

    # Determinar la siguiente versión
    next_version_tuple = None
    if not last_tag_name: # Caso: No hay releases previos
        if args.increment_type == 'patch':
            print("Primer release detectado (tipo patch). Estableciendo versión a 0.0.1.", file=sys.stderr)
            next_version_tuple = (0, 0, 1)
        else: # minor o major
            print(f"Primer release detectado (tipo {args.increment_type}). Estableciendo versión a 0.1.0.", file=sys.stderr)
            next_version_tuple = (0, 1, 0)
    else: # Caso: Hay releases previos
        next_version_tuple = calculate_next_version(current_version_tuple, args.increment_type, last_tag_name)

    if next_version_tuple is None:
        # Esto podría pasar si calculate_next_version devuelve None (ej. increment_type inválido)
        # O si el tipo era 'none' y no se manejó antes (aunque el if al principio debería atraparlo)
        print(f"No se pudo calcular la siguiente versión para el tipo de incremento '{args.increment_type}'.", file=sys.stderr)
        print("NONE") # Indicar que no hay nueva versión
        sys.exit(0)

    # Comprobar si la versión calculada es realmente nueva
    if next_version_tuple == current_version_tuple:
         print(f"La versión calculada ({'.'.join(map(str, next_version_tuple))}) es la misma que la actual. No se creará nuevo release.", file=sys.stderr)
         print("NONE")
    else:
        next_version_str = '.'.join(map(str, next_version_tuple))
        print(f"Próxima versión calculada: {next_version_str}", file=sys.stderr)
        # Imprimir la versión calculada a stdout para que el workflow la capture
        print(next_version_str)

if __name__ == "__main__":
    main()
