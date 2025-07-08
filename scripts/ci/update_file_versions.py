#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-13 00:27:13
# Version: 0.2.1
#
# update_file_versions.py - Actualiza automáticamente las variables VERSION en archivos modificados
# -----------------------------------------------------------------------------
#
# -*- coding: utf-8 -*-

"""
Actualiza automáticamente las variables VERSION en archivos modificados
basándose en los tags de los commits desde el último tag de versión.
"""

import os
import re
import subprocess
import sys
from collections import defaultdict

# --- Constantes ---

SUPPORTED_EXTENSIONS = {'.py', '.sh', '.js', '.ts'}

# Patrones Regex para encontrar la línea de versión
# Captura el grupo 1: la versión actual (X.Y.Z)
VERSION_PATTERNS = {
    '.py': re.compile(r'^VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\']'),
    '.sh': re.compile(r'^readonly\s+VERSION=["\'](\d+\.\d+\.\d+)["\']'),
    '.js': re.compile(r'^(?:const|let|var)\s+VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\'];?'),
    '.ts': re.compile(r'^(?:const|let|var)\s+VERSION\s*:\s*string\s*=\s*["\'](\d+\.\d+\.\d+)["\'];?'),
}

# Mapeo de Tags de Commit a tipo de incremento SemVer
TAG_TO_BUMP_TYPE = {
    'FIX': 'patch',
    'STYLE': 'patch',
    'FEAT': 'minor',
    'FEATURE': 'minor',
    'PERF': 'minor',
    'REFACTOR': 'major',
    'RELEASE': 'major',
}

BUMP_PRECEDENCE = {'major': 3, 'minor': 2, 'patch': 1, None: 0}

# --- Funciones Auxiliares ---

def run_git_command(command_str):
    """Ejecuta un comando Git y devuelve la salida o None en error."""
    try:
        cmd_list = command_str.split()
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True, encoding='utf-8')
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando Git command '{command_str}': {e}\nStderr: {e.stderr}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("Error: Comando 'git' no encontrado. Asegúrate de que Git está instalado y en el PATH.", file=sys.stderr)
        sys.exit(1)

def get_last_version_tag():
    """Encuentra el tag de versión más reciente (vX.Y.Z)."""
    tag = run_git_command("git describe --tags --abbrev=0 --match=v[0-9]*.[0-9]*.[0-9]*")
    if tag:
        return tag
    else:
        print("No se encontró un Tag vX.Y.Z. Usando el primer commit como referencia.", file=sys.stderr)
        first_commit = run_git_command("git rev-list --max-parents=0 HEAD")
        return first_commit

def get_commits_info_since(ref):
    """Obtiene información (hash, mensaje) de commits desde una referencia dada."""
    separator = "<||COMMIT_SEP||>" # Un separador más único
    # %B para cuerpo completo. Añadir un terminador después del cuerpo.
    log_format = f"--format=%H{separator}%B%n<||END_MSG||>"

    full_log_output = run_git_command(f"git log {ref}..HEAD {log_format}")
    if not full_log_output:
        return []

    parsed_commits = []
    # Cada commit termina con <||END_MSG||>\n
    # El último puede no tener el \n final, así que strip() y luego split.
    commit_entries = full_log_output.strip().split("<||END_MSG||>\n")

    for entry in commit_entries:
        if not entry.strip():
            continue
        parts = entry.split(separator, 1) # Dividir solo en el primer separador
        if len(parts) == 2:
            commit_hash = parts[0].strip()
            message_body = parts[1].strip() # Quitar el <||END_MSG||> remanente si es el último
            if message_body.endswith("<||END_MSG||>"): # Para el último commit si no había newline
                 message_body = message_body[:-len("<||END_MSG||>")].strip()
            parsed_commits.append({'hash': commit_hash, 'message': message_body})
    return parsed_commits

def get_changed_files_for_commit(commit_hash):
    """Obtiene la lista de archivos modificados en un commit específico."""
    files_output = run_git_command(f"git show --pretty= --name-only {commit_hash}")
    if files_output:
        return [f for f in files_output.splitlines() if f.strip()]
    return []

# --- Lógica Principal de Versionado ---

def find_version_line(filepath):
    """Encuentra la línea y versión actual en un archivo."""
    _, ext = os.path.splitext(filepath)
    if ext not in VERSION_PATTERNS:
        return None, None, None

    pattern = VERSION_PATTERNS[ext]
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line_content in enumerate(f):
                stripped_line = line_content.strip()
                match = pattern.match(stripped_line)
                if match:
                    return i, match.group(1), stripped_line # line_num, version_str, original_line_content
    except FileNotFoundError:
        print(f"Error: Archivo {filepath} no encontrado al intentar leerlo.", file=sys.stderr)
    except Exception as e:
        print(f"Error leyendo archivo {filepath}: {e}", file=sys.stderr)
    return None, None, None

def calculate_next_version(current_version_str, commit_messages):
    """Calcula la siguiente versión basada en los tags de los commits."""
    highest_bump = None
    commit_tag_pattern = re.compile(r'^\s*\[([A-Z]+)\](?:s*\(#\d+\))?')

    for msg in commit_messages:
        first_line = msg.split('\n', 1)[0].strip()
        match = commit_tag_pattern.match(first_line)
        if match:
            tag = match.group(1)
            bump_type = TAG_TO_BUMP_TYPE.get(tag)
            if BUMP_PRECEDENCE.get(bump_type, 0) > BUMP_PRECEDENCE.get(highest_bump, 0):
                highest_bump = bump_type

    if not highest_bump:
        return None

    try:
        parts = list(map(int, current_version_str.split('.')))
        if len(parts) != 3:
            print(f"Warning: Formato de versión actual inválido '{current_version_str}'.", file=sys.stderr)
            return None

        major, minor, patch = parts
        if highest_bump == 'major':
            major += 1; minor = 0; patch = 0
        elif highest_bump == 'minor':
            minor += 1; patch = 0
        elif highest_bump == 'patch':
            patch += 1
        return f"{major}.{minor}.{patch}"
    except ValueError:
        print(f"Error: Versión '{current_version_str}' contiene partes no numéricas.", file=sys.stderr)
        return None

def update_version_in_file(filepath, new_version, line_num, original_line_content):
    """Actualiza la línea de versión en el archivo."""
    _, ext = os.path.splitext(filepath)
    pattern = VERSION_PATTERNS.get(ext)
    if not pattern: return False

    current_version_match = pattern.match(original_line_content)
    if not current_version_match or not current_version_match.group(1):
        print(f"Error: No se pudo re-parsear la línea original '{original_line_content}' en {filepath}", file=sys.stderr)
        return False

    # Usar re.sub para un reemplazo más seguro dentro del patrón
    def replace_version(match_obj):
        start_idx_in_match = match_obj.start(1) - match_obj.start(0)
        end_idx_in_match = match_obj.end(1) - match_obj.start(0)
        return match_obj.group(0)[:start_idx_in_match] + new_version + match_obj.group(0)[end_idx_in_match:]

    new_line_content = pattern.sub(replace_version, original_line_content, count=1)

    print(f"  Actualizando {filepath}: {current_version_match.group(1)} -> {new_version} (Línea {line_num + 1})")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if 0 <= line_num < len(lines):
            original_ending = '\n' if lines[line_num].endswith('\n') else ''
            lines[line_num] = new_line_content + original_ending
        else:
            print(f"Error: Número de línea {line_num} fuera de rango para {filepath}", file=sys.stderr)
            return False

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print(f"Error escribiendo archivo {filepath}: {e}", file=sys.stderr)
        return False

# --- Flujo Principal ---
def main():
    print("--- Iniciando Script de Versionado por Archivo ---")
    last_tag = get_last_version_tag()
    if not last_tag:
        print("Error: No se pudo determinar la referencia inicial. Abortando.", file=sys.stderr)
        sys.exit(1)
    print(f"Analizando commits desde: {last_tag}")

    commits_info = get_commits_info_since(last_tag)
    if not commits_info:
        print("No hay nuevos commits desde la última referencia. No se necesita versionado.")
        print("::set-output name=updated_files_count::0")
        sys.exit(0)
    print(f"Encontrados {len(commits_info)} commits para analizar.")

    file_to_commit_msgs = defaultdict(list)
    relevant_changed_files = set()

    for commit in commits_info:
        commit_hash = commit['hash']
        commit_message = commit['message']
        changed_files_in_commit = get_changed_files_for_commit(commit_hash)

        for filepath in changed_files_in_commit:
            if os.path.isfile(filepath) and os.path.splitext(filepath)[1] in SUPPORTED_EXTENSIONS:
                file_to_commit_msgs[filepath].append(commit_message)
                relevant_changed_files.add(filepath)

    print(f"Archivos modificados relevantes encontrados: {len(relevant_changed_files)}")
    updated_files_count = 0
    updated_file_names = []

    for filepath in sorted(list(relevant_changed_files)):
        print(f"\nProcesando archivo: {filepath}")
        line_num, current_version, original_line = find_version_line(filepath)

        if current_version is None:
            print(f"  No se encontró línea de versión válida o archivo no soportado. Saltando.")
            continue

        print(f"  Versión actual encontrada: {current_version} en línea {line_num + 1}")

        commit_messages_for_file = file_to_commit_msgs[filepath]
        next_version = calculate_next_version(current_version, commit_messages_for_file)

        if next_version and next_version != current_version:
            print(f"  Nueva versión calculada: {next_version}")
            if update_version_in_file(filepath, next_version, line_num, original_line):
                updated_files_count += 1
                updated_file_names.append(filepath)
        elif next_version == current_version:
            print(f"  La versión calculada ({next_version}) es la misma que la actual.")
        else:
            print(f"  No se requiere incremento de versión para este archivo.")

    print(f"\n--- Finalizado ---")
    print(f"Archivos procesados: {len(relevant_changed_files)}")
    print(f"Archivos cuya versión fue actualizada: {updated_files_count}")

    if updated_files_count > 0:
        updated_files_str = " ".join(updated_file_names)
        print(f"Archivos actualizados: {updated_files_str}")
        if os.getenv("GITHUB_ACTIONS") == "true": # Solo para GitHub Actions
            print(f"::set-output name=updated_files::{updated_files_str}")
            print(f"::set-output name=updated_files_count::{updated_files_count}")
    else:
        print("No se actualizaron versiones de archivos.")
        if os.getenv("GITHUB_ACTIONS") == "true":
            print(f"::set-output name=updated_files_count::0")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR FATAL en script de versionado: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
