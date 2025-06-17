#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Heading
Copyright (C) 2025 MAURO ROSERO PÉREZ

Script Name: versioning.py
Author:      Mauro Rosero P. <mauro.rosero@gmail.com>
Assistant:   Cursor AI (https://cursor.com)
Created at:  2025-01-27
Modified:    2025-06-17 10:12:02
Description: Analiza el historial de Git de un archivo específico y calcula la versión
             major.minor.patch basándose en los tags de commit encontrados.
Version:     0.1.0
"""

# 1. Imports de la biblioteca estándar (ordenados alfabéticamente)
import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional


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
        print(f"Error ejecutando git log: {stderr}", file=sys.stderr)
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


def calculate_version(commits: List[str]) -> str:
    """
    Calcula la versión major.minor.patch basándose en los tags de commit.

    Reglas:
    - [REFACTOR], [RELEASE] -> MAJOR (resetea Minor, Patch)
    - [FEAT], [PERF], [UPDATE], [IMPROVE] -> MINOR (resetea Patch)
    - [FIX], [STYLE] -> PATCH
    - [DOCS], [TEST], [BUILD], [CI], [CHORE] -> Ninguno
    """
    major = 0
    minor = 0
    patch = 0

    for commit in commits:
        tag = extract_tag_from_commit(commit)

        if not tag:
            continue

        if tag in ['REFACTOR', 'RELEASE']:
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


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Analiza commits y calcula versión major.minor.patch. Si no se especifica archivo, analiza todo el repositorio.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python versioning.py                    # Analiza todo el repositorio
  python versioning.py micursor.py        # Analiza archivo específico
  python versioning.py -p /path/to/repo   # Analiza repositorio en ruta específica
  python versioning.py -p /path/to/repo micursor.py
  python versioning.py branch-workflow-validator.py  # Busca en historial aunque no exista actualmente

Formatos de commit soportados:
  [FEAT] (#123) Add new feature
  feat: add new feature
  [FIX] (#456) Fix bug
  fix: fix bug
  [REFACTOR] (#789) Refactor code
  refactor: refactor code
  [RELEASE] v1.2.3
  release: v1.2.3
        """
    )

    parser.add_argument(
        'filename',
        nargs='?',
        help='Nombre del archivo a analizar (opcional, si no se especifica analiza todo el repositorio)'
    )

    parser.add_argument(
        '-p', '--path',
        type=Path,
        default=Path.cwd(),
        help='Ruta del repositorio Git (por defecto: carpeta actual)'
    )

    args = parser.parse_args()

    # Validaciones
    if not validate_git_repo(args.path):
        sys.exit(1)

    # Obtener commits según si se especificó archivo o no
    if args.filename:
        validate_file_exists(args.path, args.filename, strict=False)
        commits = get_file_commits(args.path, args.filename)
    else:
        commits = get_repo_commits(args.path)

    if not commits:
        print("0.0.0")
        return

    # Calcular versión
    version = calculate_version(commits)
    print(version)


if __name__ == "__main__":
    main()
