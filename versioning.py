#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Heading
Copyright (C) 2025 MAURO ROSERO PÉREZ

Script Name: versioning.py
Author:      Mauro Rosero P. <mauro.rosero@gmail.com>
Assistant:   Cursor AI (https://cursor.com)
Created at:  2025-01-27
Modified:    2025-06-18 14:39:34
Description: Analiza el historial de Git de un archivo específico y calcula la versión
             major.minor.patch basándose en los tags de commit encontrados.
Version:     2.1.1
"""

# 1. Imports de la biblioteca estándar (ordenados alfabéticamente)
import argparse
import re
import subprocess
import sys
import glob
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set


def run_git_command(command: List[str], repo_path: Path) -> Tuple[bool, str, str]:
    """Ejecuta un comando Git y retorna (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            command,
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8'
        )
        return True, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def validate_git_repo(repo_path: Path) -> bool:
    """Valida que la ruta sea un repositorio Git válido."""
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        print(f"Error: No se encontró un repositorio Git en '{repo_path}'", file=sys.stderr)
        return False
    return True


def validate_file_exists(repo_path: Path, filename: str, strict: bool = True) -> bool:
    """Valida que el archivo existe en el repositorio."""
    file_path = repo_path / filename
    if file_path.exists():
        return True

    if strict:
        print(f"Error: El archivo '{filename}' no existe en '{repo_path}'", file=sys.stderr)
        return False

    # Si no es estricto, simplemente retornar True para permitir búsqueda en historial
    return True


def get_repo_commits(repo_path: Path) -> List[str]:
    """Obtiene todos los commits del repositorio en orden cronológico."""
    success, stdout, stderr = run_git_command(
        ["git", "log", "--oneline", "--reverse"],
        repo_path
    )

    if not success:
        print(f"Error ejecutando git log: {stderr}", file=sys.stderr)
        return []

    if not stdout:
        return []

    commits = [line.strip() for line in stdout.split('\n') if line.strip()]
    return commits


def get_file_commits(repo_path: Path, filename: str) -> List[str]:
    """Obtiene todos los commits que afectan al archivo especificado en orden cronológico."""

    # Primero intentar con --follow para el archivo actual
    success, stdout, stderr = run_git_command(
        ["git", "log", "--follow", "--oneline", "--reverse", filename],
        repo_path
    )

    if success and stdout:
        # Si encontramos commits, usarlos
        commits = [line.strip() for line in stdout.split('\n') if line.strip()]
        return commits

    # Si no hay commits con --follow, buscar en todo el historial
    # Buscar por nombre de archivo en cualquier ubicación
    success, stdout, stderr = run_git_command(
        ["git", "log", "--all", "--full-history", "--oneline", "--reverse", "--name-only", "--", f"**/{filename}"],
        repo_path
    )

    if not success:
        return []

    if not stdout:
        return []

    # Filtrar solo las líneas que son commits (no nombres de archivos)
    commits = []
    lines = stdout.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith(filename) and not line.endswith(filename):
            # Es un commit, no un nombre de archivo
            commits.append(line)

    return commits


def extract_tag_from_commit(commit_message: str) -> Optional[str]:
    """
    Extrae el tag de un mensaje de commit usando múltiples formatos.
    Retorna el tag en mayúsculas o None si no se encuentra.
    """
    # Lista de tags válidos
    valid_tags = ['feat', 'fix', 'style', 'refactor', 'perf', 'release',
                  'docs', 'test', 'build', 'ci', 'chore', 'update', 'improve']

    # Patrones para diferentes formatos de commit
    patterns = [
        # [TAG] (#Issue) Descripción
        r'\[(feat|fix|style|refactor|perf|release|docs|test|build|ci|chore|update|improve)\]\s*\(#[0-9]+\)',
        # [TAG] Descripción (sin número de issue)
        r'\[(feat|fix|style|refactor|perf|release|docs|test|build|ci|chore|update|improve)\]\s+',
        # TAG: Descripción
        r'(feat|fix|style|refactor|perf|release|docs|test|build|ci|chore|update|improve):\s*',
        # TAG al inicio de la línea
        r'^(feat|fix|style|refactor|perf|release|docs|test|build|ci|chore|update|improve)\s+',
        # TAG con espacios después
        r'^(feat|fix|style|refactor|perf|release|docs|test|build|ci|chore|update|improve)\s*',
    ]

    # Buscar en cada patrón
    for pattern in patterns:
        match = re.search(pattern, commit_message, re.IGNORECASE)
        if match:
            tag = match.group(1).upper()
            if tag in [t.upper() for t in valid_tags]:
                return tag

    return None


def calculate_version(commits: List[str], is_group_analysis: bool = False) -> str:
    """
    Calcula la versión major.minor.patch basándose en los tags de commit.

    Reglas para análisis individual:
    - [REFACTOR], [RELEASE] -> MAJOR (resetea Minor, Patch)
    - [FEAT], [PERF], [UPDATE], [IMPROVE] -> MINOR (resetea Patch)
    - [FIX], [STYLE] -> PATCH
    - [DOCS], [TEST], [BUILD], [CI], [CHORE] -> Ninguno

    Reglas para análisis de grupo:
    - [RELEASE] -> MAJOR (resetea Minor, Patch)
    - [REFACTOR], [FEAT], [PERF], [UPDATE], [IMPROVE] -> MINOR (resetea Patch)
    - [FIX], [STYLE] -> PATCH
    - [DOCS], [TEST], [BUILD], [CI], [CHORE] -> Ninguno
    """
    major = 0
    minor = 0
    patch = 0

    for i, commit in enumerate(commits):
        tag = extract_tag_from_commit(commit)

        if not tag:
            continue

        if tag == 'RELEASE':
            major += 1
            minor = 0
            patch = 0
        elif tag == 'REFACTOR':
            if is_group_analysis:
                # Para grupos, REFACTOR incrementa MINOR
                minor += 1
                patch = 0
            else:
                # Para archivos individuales, REFACTOR incrementa MAJOR
                major += 1
                minor = 0
                patch = 0
        elif tag in ['FEAT', 'PERF', 'UPDATE', 'IMPROVE']:
            minor += 1
            patch = 0
        elif tag in ['FIX', 'STYLE']:
            patch += 1
        # [DOCS], [TEST], [BUILD], [CI], [CHORE] no afectan la versión

    return f"{major}.{minor}.{patch}"


def write_version_to_file(repo_path: Path, version: str) -> bool:
    """Escribe la versión calculada en el archivo .project/version."""
    project_dir = repo_path / ".project"
    version_file = project_dir / "version"

    try:
        # Crear directorio .project si no existe
        project_dir.mkdir(exist_ok=True)

        # Escribir la versión en el archivo
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version)

        return True
    except Exception as e:
        print(f"Error escribiendo versión en {version_file}: {e}", file=sys.stderr)
        return False


def expand_file_patterns(repo_path: Path, patterns: List[str], recursive: bool = True) -> Set[str]:
    """Expande patrones glob y retorna un conjunto de archivos únicos."""
    files = set()

    for pattern in patterns:
        # Si es solo un nombre de archivo (sin **/), agregar **/ para búsqueda recursiva
        if recursive and not pattern.startswith('**/') and '/' not in pattern and '*' not in pattern:
            pattern = f"**/{pattern}"

        # Buscar archivos que coincidan con el patrón
        if recursive:
            matches = list(repo_path.glob(pattern))
        else:
            # Para búsqueda no recursiva, solo buscar en el directorio actual
            matches = list(repo_path.glob(pattern))
            # Filtrar solo archivos en el directorio actual (no subdirectorios)
            matches = [m for m in matches if m.parent == repo_path]

        for match in matches:
            if match.is_file():
                # Convertir a ruta relativa al repositorio
                files.add(str(match.relative_to(repo_path)))

    return files


def get_group_commits(repo_path: Path, file_patterns: List[str], recursive: bool = True) -> List[str]:
    """Obtiene todos los commits que afectan a cualquiera de los archivos del grupo."""
    # Expandir patrones glob
    files = expand_file_patterns(repo_path, file_patterns, recursive=recursive)

    if not files:
        print(f"Advertencia: No se encontraron archivos que coincidan con los patrones: {file_patterns}", file=sys.stderr)
        return []

    # Obtener commits para cada archivo
    all_commits = set()

    for filename in files:
        file_commits = get_file_commits(repo_path, filename)
        all_commits.update(file_commits)

    # Convertir a lista y ordenar cronológicamente
    commits_list = list(all_commits)
    commits_list.sort()  # Los commits ya vienen en orden cronológico de get_file_commits

    return commits_list


def update_file_version_header(filepath: Path, new_version: str) -> bool:
    """
    Busca en las primeras 20 líneas del archivo una línea con 'version' o 'versión' (case-insensitive)
    y un patrón major.minor.patch, y reemplaza ese valor por la nueva versión usando sed.
    """
    try:
        # Leer las primeras 20 líneas
        with open(filepath, 'r', encoding='utf-8') as f:
            header_lines = [next(f) for _ in range(20)]
    except (FileNotFoundError, StopIteration):
        return False
    except Exception as e:
        return False

    # Buscar línea con version/versión y patrón de versión
    import re
    version_pattern = re.compile(r'(version|versión)[^\n\d]*([0-9]+\.[0-9]+\.[0-9]+)', re.IGNORECASE)
    for idx, line in enumerate(header_lines):
        match = version_pattern.search(line)
        if match:
            old_version = match.group(2)
            # Usar sed para reemplazar solo en la línea encontrada
            try:
                subprocess.run([
                    'sed',
                    '-i',
                    f'1,20s/{old_version}/{new_version}/',
                    str(filepath)
                ], check=True)
                return True
            except subprocess.CalledProcessError as e:
                return False
    return False


def get_all_project_files(repo_path: Path, recursive: bool = True) -> List[str]:
    """Obtiene todos los archivos del proyecto (excluyendo .git, __pycache__, etc.)."""
    files = []
    exclude_patterns = {'.git', '__pycache__', '.pytest_cache', '.venv', 'venv', 'node_modules', '.vscode', '.idea'}

    if recursive:
        # Búsqueda recursiva (incluye directorio actual y subdirectorios)
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                # Verificar que no esté en directorios excluidos
                # Solo excluir si el directorio completo coincide con un patrón de exclusión
                should_exclude = False
                for exclude in exclude_patterns:
                    if exclude in file_path.parts:
                        should_exclude = True
                        break

                if not should_exclude:
                    # Convertir a ruta relativa
                    relative_path = str(file_path.relative_to(repo_path))
                    files.append(relative_path)
    else:
        # Búsqueda solo en el directorio actual
        for file_path in repo_path.iterdir():
            if file_path.is_file():
                # Verificar que no esté en directorios excluidos
                should_exclude = False
                for exclude in exclude_patterns:
                    if exclude in file_path.parts:
                        should_exclude = True
                        break

                if not should_exclude:
                    # Convertir a ruta relativa
                    relative_path = str(file_path.relative_to(repo_path))
                    files.append(relative_path)

    return files


def calculate_and_update_file_version(repo_path: Path, filename: str) -> str:
    """Calcula la versión individual de un archivo y la actualiza en el header. Devuelve la versión calculada o None si falla."""
    file_commits = get_file_commits(repo_path, filename)
    if file_commits:
        version = calculate_version(file_commits, is_group_analysis=False)
        file_path = repo_path / filename
        update_file_version_header(file_path, version)
        return version
    else:
        return None


def main():
    parser = argparse.ArgumentParser(description="Herramienta de versionado SemVer por archivo y global.")
    parser.add_argument('files', nargs='*', help='Archivos o patrones glob a analizar')
    parser.add_argument('--update', action='store_true', help='Actualiza la versión en el archivo o en .project/version')
    parser.add_argument('--update-all', action='store_true', help='Actualiza la versión en todos los archivos del proyecto')
    parser.add_argument('--path', type=str, default='.', help='Ruta al repositorio (por defecto: .)')
    parser.add_argument('--verbose', action='store_true', help='Muestra archivo y versión calculada (solo con --update-all)')
    parser.add_argument('--depth', action='store_true', default=True, help='Busca archivos de forma recursiva (por defecto: True)')
    parser.add_argument('--no-depth', action='store_true', help='Busca archivos solo en el directorio actual')
    args = parser.parse_args()

    repo_path = Path(args.path).resolve()

    # Determinar si usar búsqueda recursiva
    recursive = args.depth and not args.no_depth

    if args.update_all:
        all_files = get_all_project_files(repo_path, recursive=recursive)
        # Fase 1: Calcular versiones
        version_map = {}
        for filename in all_files:
            file_commits = get_file_commits(repo_path, filename)
            if file_commits:
                version = calculate_version(file_commits, is_group_analysis=False)
                version_map[filename] = version
            else:
                version_map[filename] = None
        # Fase 2: Actualizar archivos
        for filename, version in version_map.items():
            if version:
                success = update_file_version_header(repo_path / filename, version)
                if args.verbose and success and version != "0.0.0":
                    print(f"{filename}: {version}")
        return

    # Obtener commits según si se especificaron archivos o no
    if args.files:
        commits = get_group_commits(repo_path, args.files, recursive=recursive)
    else:
        commits = get_repo_commits(repo_path)

    if not commits:
        version = "0.0.0"
    else:
        # Determinar si es análisis de grupo o individual
        is_group = len(args.files) > 1 if args.files else False
        version = calculate_version(commits, is_group_analysis=is_group)

    print(version)

    # Si se especificó --update y no hay archivos específicos, escribir en .project/version
    if args.update and not args.files:
        if not write_version_to_file(repo_path, version):
            sys.exit(1)

    # Si se especificó --update y hay un solo archivo, actualizar header
    if args.update and args.files and len(args.files) == 1:
        calculate_and_update_file_version(repo_path, args.files[0])
        return


if __name__ == "__main__":
    main()
