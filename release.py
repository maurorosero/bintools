#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Check Heading
Copyright (C) <2025> MAURO ROSERO PÉREZ (ROSERO ONE DEVELOPMENT)

Script Name: release.py
Version:     0.0.0
Description: Script para automatizar el proceso de release.
Created:     2025-06-18 14:40:00
Modified:    2025-06-18 15:45:05
Author:      Mauro Rosero Pérez <mauro@rosero.one>
Assistant:   Cursor AI (https://cursor.com)
"""

"""
Script para automatizar el proceso de release.
Crea un tag, lo sube al repositorio y regenera el CHANGELOG.
"""

import subprocess
import sys
import click
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

console = Console()

def run_command(command, cwd=None, check=True):
    """Ejecuta un comando y retorna el resultado."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd or Path.cwd()
        )
        if check and result.returncode != 0:
            console.print(f"[red]Error ejecutando: {command}[/red]")
            console.print(f"[red]Error: {result.stderr}[/red]")
            return None
        return result
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return None

def get_current_branch(cwd=None):
    """Obtiene la rama actual."""
    result = run_command("git branch --show-current", cwd=cwd)
    return result.stdout.strip() if result else None

def get_latest_tag(cwd=None):
    """Obtiene el último tag."""
    # Obtener todos los tags
    result = run_command("git tag --list", cwd=cwd)
    if not result or not result.stdout.strip():
        return None

    all_tags = [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]

    # Filtrar solo tags que son versiones válidas (semantic versioning)
    import re
    version_pattern = re.compile(r'^v?\d+\.\d+\.\d+.*$')
    valid_versions = []

    for tag in all_tags:
        if version_pattern.match(tag):
            # Normalizar: añadir 'v' si no lo tiene
            if not tag.startswith('v'):
                tag = f"v{tag}"
            valid_versions.append(tag)

    if not valid_versions:
        return None

    # Ordenar versiones correctamente (semantic versioning)
    def version_key(tag):
        # Remover 'v' prefix para ordenamiento
        version = tag[1:] if tag.startswith('v') else tag
        # Split por puntos y convertir a números
        parts = version.split('.')
        # Asegurar que tenemos al menos 3 partes (major.minor.patch)
        while len(parts) < 3:
            parts.append('0')
        # Convertir a números para ordenamiento correcto
        return [int(part) for part in parts[:3]]

    # Ordenar de más reciente a más antigua
    valid_versions.sort(key=version_key, reverse=True)

    return valid_versions[0]

def get_commits_since_tag(tag, cwd=None):
    """Obtiene commits desde un tag específico."""
    if not tag:
        result = run_command("git log --oneline | wc -l", cwd=cwd)
        return int(result.stdout.strip()) if result else 0

    result = run_command(f"git log {tag}..HEAD --oneline | wc -l", cwd=cwd)
    return int(result.stdout.strip()) if result else 0

def validate_version(version):
    """Valida el formato de versión semántica."""
    import re
    pattern = r'^v?\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'
    return bool(re.match(pattern, version))

def suggest_next_version(current_tag):
    """Sugiere la siguiente versión basada en el último tag."""
    if not current_tag:
        return "v1.0.0"

    # Remover 'v' si existe
    version = current_tag.lstrip('v')
    parts = version.split('.')

    if len(parts) >= 3:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        return f"v{major}.{minor}.{patch + 1}"

    return "v1.0.0"

@click.command()
@click.option('--version', help='Versión del release (ej: v1.0.0)')
@click.option('--message', help='Mensaje del release')
@click.option('--push', is_flag=True, help='Subir tag al repositorio remoto')
@click.option('--regenerate-changelog', is_flag=True, default=True, help='Regenerar CHANGELOG después del release')
@click.option('--dry-run', is_flag=True, help='Mostrar qué se haría sin ejecutar')
@click.option('-p', '--path', default='.', help='Ruta del proyecto (por defecto: directorio actual)')
@click.option('--force-main', is_flag=True, help='Forzar checkout a main antes del release')
def release(version, message, push, regenerate_changelog, dry_run, path, force_main):
    """Crea un release con tag, push y regeneración de CHANGELOG."""

    console.print(Panel.fit("🚀 [bold blue]Release Manager[/bold blue]", style="blue"))

    project_path = Path(path).resolve()

    # Verificar que estamos en un repositorio Git
    if not (project_path / '.git').exists():
        console.print(f"[red]Error: No se encontró un repositorio Git en {project_path}[/red]")
        sys.exit(1)

    # Obtener información del repositorio
    current_branch = get_current_branch(project_path)
    latest_tag = get_latest_tag(project_path)

    console.print(f"[blue]Rama actual:[/blue] {current_branch}")
    console.print(f"[blue]Último Tag:[/blue] {latest_tag or 'Ninguno'}")
    console.print(f"[blue]Directorio del proyecto:[/blue] {project_path}")

    # Verificar que estamos en main
    if current_branch != 'main':
        if force_main:
            console.print("[blue]Forzando checkout a 'main'...[/blue]")
            checkout_command = "git checkout main"
            if not run_command(checkout_command, cwd=project_path):
                console.print("[red]Error haciendo checkout a main[/red]")
                sys.exit(1)
            console.print("[green]✓ Checkout a 'main' completado[/green]")
            current_branch = "main"
        else:
            console.print(f"[yellow]⚠️  Estás en la rama '{current_branch}', no en 'main'[/yellow]")
            console.print("[blue]Opciones:[/blue]")
            console.print("1. Hacer checkout a 'main' y continuar")
            console.print("2. Continuar desde la rama actual (no recomendado)")
            console.print("3. Cancelar el release")

            choice = Prompt.ask(
                "¿Qué quieres hacer?",
                choices=["1", "2", "3"],
                default="1"
            )

            if choice == "1":
                console.print("[blue]Haciendo checkout a 'main'...[/blue]")
                checkout_command = "git checkout main"
                if not run_command(checkout_command, cwd=project_path):
                    console.print("[red]Error haciendo checkout a main[/red]")
                    sys.exit(1)
                console.print("[green]✓ Checkout a 'main' completado[/green]")
                current_branch = "main"
            elif choice == "2":
                if not Confirm.ask(f"¿Estás seguro de hacer release desde la rama '{current_branch}'? Esto puede causar problemas."):
                    console.print("[yellow]Release cancelado[/yellow]")
                    return
                console.print(f"[yellow]⚠️  Continuando desde rama '{current_branch}'[/yellow]")
            else:
                console.print("[yellow]Release cancelado[/yellow]")
                return

    # Obtener versión desde .project/version si no se especifica
    if not version:
        version_file = project_path / '.project' / 'version'
        if version_file.exists():
            try:
                with open(version_file, 'r') as f:
                    version = f.read().strip()
                console.print(f"[blue]Versión leída desde:[/blue] {version_file}")
            except Exception as e:
                console.print(f"[red]Error leyendo versión desde {version_file}: {e}[/red]")
                version = None

        # Si no se pudo leer del archivo, sugerir basada en el último tag
        if not version:
            suggested = suggest_next_version(latest_tag)
            version = Prompt.ask(
                f"Versión del release",
                default=suggested
            )

    # Validar versión
    if not validate_version(version):
        console.print("[red]Error: Formato de versión inválido. Usa formato semántico (ej: v1.0.0)[/red]")
        sys.exit(1)

    # Asegurar que la versión tenga prefijo 'v'
    if not version.startswith('v'):
        version = f"v{version}"
        console.print(f"[blue]Versión normalizada:[/blue] {version}")

    # Obtener mensaje
    if not message:
        message = Prompt.ask(
            "Mensaje del release",
            default=f"Release {version}"
        )

    # Mostrar resumen
    commits_since_tag = get_commits_since_tag(latest_tag, project_path)

    table = Table(title="📊 Resumen del Release")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="magenta")

    table.add_row("Versión", version)
    table.add_row("Mensaje", message)
    table.add_row("Commits desde último tag", str(commits_since_tag))
    table.add_row("Push al remoto", "Sí" if push else "No")
    table.add_row("Regenerar CHANGELOG", "Sí" if regenerate_changelog else "No")
    table.add_row("Directorio del proyecto", str(project_path))
    table.add_row("Forzar checkout a main", "Sí" if force_main else "No")

    console.print(table)

    if dry_run:
        console.print("[yellow]Modo dry-run: No se ejecutarán cambios[/yellow]")
        return

    # Confirmar
    if not Confirm.ask("¿Proceder con el release?"):
        console.print("[yellow]Release cancelado[/yellow]")
        return

    # Ejecutar release
    console.print("\n[green]🚀 Iniciando release...[/green]")

    # 1. Crear tag
    console.print("[blue]1. Creando Tag...[/blue]")
    tag_command = f'git tag -a {version} -m "{message}"'
    if not run_command(tag_command, cwd=project_path):
        console.print("[red]Error creando Tag[/red]")
        sys.exit(1)
    console.print(f"[green]✓ Tag {version} creado[/green]")

    # 2. Push del tag
    if push:
        console.print("[blue]2. Subiendo Tag al remoto...[/blue]")
        push_command = f"git push origin {version}"
        if not run_command(push_command, cwd=project_path):
            console.print("[red]Error subiendo Tag[/red]")
            sys.exit(1)
        console.print(f"[green]✓ Tag {version} subido al remoto[/green]")

    # 3. Regenerar CHANGELOG
    if regenerate_changelog:
        console.print("[blue]3. Regenerando CHANGELOG...[/blue]")
        changelog_command = f"python docgen.py generate --doc-type changelog --output CHANGELOG.md --base-path {project_path}"
        if not run_command(changelog_command, cwd=project_path):
            console.print("[red]Error regenerando CHANGELOG[/red]")
            sys.exit(1)
        console.print("[green]✓ CHANGELOG regenerado[/green]")

    # 4. Commit del CHANGELOG actualizado
    if regenerate_changelog:
        console.print("[blue]4. Commit del CHANGELOG actualizado...[/blue]")
        add_command = "git add CHANGELOG.md"
        commit_command = f'git commit -m "[CI] Auto-update changelog for {version}"'

        if run_command(add_command, cwd=project_path) and run_command(commit_command, cwd=project_path):
            console.print("[green]✓ CHANGELOG committeado[/green]")

            if push:
                push_main_command = "git push origin main"
                if run_command(push_main_command, cwd=project_path):
                    console.print("[green]✓ Cambios subidos a main[/green]")

    console.print(Panel.fit(f"🎉 [bold green]Release {version} completado exitosamente![/bold green]", style="green"))

    # Mostrar próximos pasos
    console.print("\n[blue]📋 Próximos pasos sugeridos:[/blue]")
    console.print("• Revisar el CHANGELOG generado")
    console.print("• Crear release notes en GitHub/GitLab si es necesario")
    console.print("• Notificar al equipo sobre el nuevo release")

if __name__ == "__main__":
    release()
