#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Heading
Copyright (C) 2025 MAURO ROSERO PÉREZ

Script Name: licensing.py
Author:      Mauro Rosero P. <mauro.rosero@gmail.com>
Assistant:   Cursor AI (https://cursor.com)
Created at:  2025-01-27
Modified:    2025-06-18 14:39:34
Description: Gestiona las licencias de software en proyectos Git.
Version:     0.1.1
"""

"""
- Descubre licencias en scaffold/licenses/ (solo requires_ai_generation: false)
- Permite seleccionar por argumento o menú interactivo
- Copia la licencia como LICENSE.md en el proyecto (cwd o --path)
- Si existe LICENSE.md, pide confirmación (o usa --yes para sobrescribir)
"""

import argparse
import os
from pathlib import Path
import sys
import re

def find_scaffold_licenses_dir() -> Path:
    """Busca el directorio scaffold/licenses/ relativo a este script o cwd."""
    # Busca primero relativo al script
    script_dir = Path(__file__).resolve().parent
    candidate = script_dir / "scaffold" / "licenses"
    if candidate.exists():
        return candidate
    # Busca relativo al cwd
    cwd_candidate = Path.cwd() / "scaffold" / "licenses"
    if cwd_candidate.exists():
        return cwd_candidate
    # Busca hacia arriba desde cwd
    for parent in Path.cwd().parents:
        up_candidate = parent / "scaffold" / "licenses"
        if up_candidate.exists():
            return up_candidate
    print("Error: No se encontró el directorio scaffold/licenses/.")
    sys.exit(1)

def parse_license_metadata(license_path: Path) -> dict:
    """Extrae la metadata YAML del inicio del archivo de licencia."""
    content = license_path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---\n", 4)
    if end == -1:
        return {}
    import yaml
    try:
        meta = yaml.safe_load(content[4:end])
        return meta if isinstance(meta, dict) else {}
    except Exception:
        return {}

def list_established_licenses(licenses_dir: Path) -> list:
    """Lista las licencias con requires_ai_generation: false."""
    licenses = []
    for lic_file in licenses_dir.glob("*.md"):
        meta = parse_license_metadata(lic_file)
        if meta.get("metadata", {}).get("requires_ai_generation", False) is False:
            licenses.append((lic_file.stem, lic_file))
    return sorted(licenses)

def select_license_interactive(licenses: list) -> tuple:
    print("Licencias disponibles:")
    for idx, (name, _) in enumerate(licenses, 1):
        print(f"  {idx}. {name}")
    while True:
        sel = input("Selecciona una licencia (número): ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(licenses):
            return licenses[int(sel)-1]
        print("Opción inválida.")

def strip_license_metadata(license_path: Path) -> str:
    """Devuelve el texto de la licencia sin la metadata YAML."""
    content = license_path.read_text(encoding="utf-8")
    if content.startswith("---\n"):
        end = content.find("\n---\n", 4)
        if end != -1:
            return content[end+5:].lstrip()
    return content

def confirm_overwrite(target: Path, auto_yes: bool) -> bool:
    if not target.exists():
        return True
    if auto_yes:
        return True
    resp = input(f"El archivo {target} ya existe. ¿Sobrescribir? [y/N]: ").strip().lower()
    return resp == "y"

def main():
    parser = argparse.ArgumentParser(description="Instala una licencia establecida en el proyecto.")
    parser.add_argument("-l", "--license", help="Nombre de la licencia a instalar (ej: mit, apache-2-0)")
    parser.add_argument("-p", "--path", help="Ruta del proyecto (por defecto cwd)")
    parser.add_argument("-y", "--yes", action="store_true", help="Sobrescribe LICENSE.md sin preguntar")
    args = parser.parse_args()

    project_dir = Path(args.path).resolve() if args.path else Path.cwd()
    licenses_dir = find_scaffold_licenses_dir()
    licenses = list_established_licenses(licenses_dir)
    if not licenses:
        print("No se encontraron licencias establecidas disponibles.")
        sys.exit(1)

    if args.license:
        lic_tuple = next(((n, p) for n, p in licenses if n.lower() == args.license.lower()), None)
        if not lic_tuple:
            print(f"Licencia '{args.license}' no encontrada o no es válida.")
            print("Licencias disponibles:", ", ".join(n for n, _ in licenses))
            sys.exit(1)
    else:
        lic_tuple = select_license_interactive(licenses)

    lic_name, lic_path = lic_tuple
    license_text = strip_license_metadata(lic_path)
    target_license = project_dir / "LICENSE.md"

    if not confirm_overwrite(target_license, args.yes):
        print("Operación cancelada.")
        sys.exit(0)

    target_license.write_text(license_text, encoding="utf-8")
    print(f"Licencia '{lic_name}' instalada en {target_license}")

if __name__ == "__main__":
    main()
