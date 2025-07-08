#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Check Heading
Copyright (C) <2025> MAURO ROSERO PÉREZ (ROSERO ONE DEVELOPMENT)

Script Name: release.py
Version:     0.0.0
Description: Script para automatizar el proceso de release con integración de APIs de plataformas Git.
Created:     2025-06-18 14:40:00
Modified:    2025-07-07 21:46:23
Author:      Mauro Rosero Pérez <mauro@rosero.one>
Assistant:   Cursor AI (https://cursor.com)
"""

"""
Script para automatizar el proceso de release.
Crea un tag, lo sube al repositorio, regenera el CHANGELOG y crea releases en plataformas Git.
"""

import subprocess
import sys
import click
import os
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
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

def get_system_user():
    """Obtiene el usuario del sistema."""
    return os.getenv('USER') or os.getenv('USERNAME') or 'default'

def decrypt_token(token_enc, method="b64"):
    """Desencripta un token usando el mismo método que git-tokens.py."""
    if method == "b64":
        try:
            import base64
            return base64.b64decode(token_enc.encode("utf-8")).decode("utf-8")
        except Exception:
            return token_enc  # Para compatibilidad con tokens antiguos no codificados
    else:
        return token_enc

def get_token_from_keyring(service, mode):
    """Obtiene token desde keyring con fallback a variables de entorno."""
    try:
        import keyring

        # Construir nombre del servicio para keyring (mismo formato que git-integration-manager)
        service_name = f"{service}-{mode}-integration"
        username = get_system_user()

        # Obtener token encriptado desde keyring
        token_enc = keyring.get_password(service_name, username)

        if token_enc:
            # Desencriptar el token usando el mismo método que git-tokens.py
            token = decrypt_token(token_enc, "b64")
            console.print(f"[blue]Token obtenido desde keyring para {service} ({service_name})[/blue]")
            return token
        else:
            console.print(f"[yellow]Token no encontrado en keyring para {service} ({service_name})[/yellow]")

    except ImportError:
        console.print("[yellow]keyring no disponible, usando variables de entorno[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Error accediendo keyring: {e}[/yellow]")

    # Fallback a variables de entorno (mismo mapeo que git-integration-manager)
    env_vars = {
        'github': ['GITHUB_TOKEN', 'GH_TOKEN'],
        'gitlab': ['GITLAB_TOKEN', 'GL_TOKEN'],
        'forgejo': ['FORGEJO_TOKEN', 'GITEA_TOKEN'],  # Forgejo es compatible con Gitea
        'gitea': ['GITEA_TOKEN', 'FORGEJO_TOKEN'],    # Gitea es compatible con Forgejo
        'bitbucket': ['BITBUCKET_TOKEN', 'BB_TOKEN']
    }

    # Intentar obtener token de variables de entorno
    for var_name in env_vars.get(service, []):
        token = os.getenv(var_name)
        if token:
            console.print(f"[blue]Token obtenido desde variable de entorno {var_name}[/blue]")
            return token

    console.print(f"[red]No se pudo obtener token para {service}[/red]")
    return None

def detect_git_platform_and_token(project_path):
    """Detecta la plataforma y obtiene el token desde keyring con fallback a variables de entorno."""
    result = run_command("git remote get-url origin", cwd=project_path)
    if not result:
        return None

    url = result.stdout.strip()

    # Mapeo de URLs a plataformas
    platform_map = {
        'github.com': {
            'service': 'github',
            'mode': 'c',
            'api_base': 'https://api.github.com'
        },
        'gitlab.com': {
            'service': 'gitlab',
            'mode': 'c',
            'api_base': 'https://gitlab.com/api/v4'
        },
        'git.rosero.one': {
            'service': 'forgejo',
            'mode': 'c',
            'api_base': 'https://git.rosero.one/api/v1'
        },
        'codeberg.org': {
            'service': 'forgejo',
            'mode': 'c',
            'api_base': 'https://codeberg.org/api/v1'
        },
        'gitea.com': {
            'service': 'gitea',
            'mode': 'c',
            'api_base': 'https://gitea.com/api/v1'
        }
    }

    # Detectar plataforma
    platform_info = None
    for domain, info in platform_map.items():
        if domain in url:
            platform_info = info.copy()
            break

    if not platform_info:
        console.print(f"[red]Plataforma no soportada para URL: {url}[/red]")
        return None

    # Obtener token
    token = get_token_from_keyring(platform_info['service'], platform_info['mode'])
    if not token:
        return None

    # Extraer owner/repo de la URL
    import re

    # Manejar URLs SSH (git@github.com:owner/repo.git)
    if url.startswith('git@'):
        # git@github.com:owner/repo.git
        match = re.search(r'git@([^:]+):([^/]+)/([^/]+?)(?:\.git)?$', url)
        if match:
            domain, owner, repo = match.groups()
            # Verificar que el dominio coincide con la plataforma detectada
            if any(platform_domain in domain for platform_domain in platform_map.keys()):
                platform_info['owner'] = owner
                platform_info['repo'] = repo
                platform_info['token'] = token
                return platform_info

    # Manejar URLs HTTPS
    if 'github.com' in url or 'gitlab.com' in url or 'git.rosero.one' in url or 'codeberg.org' in url or 'gitea.com' in url:
        # https://github.com/owner/repo.git o https://gitlab.com/owner/repo.git
        match = re.search(r'/([^/]+)/([^/]+?)(?:\.git)?$', url)
        if match:
            owner, repo = match.groups()
            platform_info['owner'] = owner
            platform_info['repo'] = repo
            platform_info['token'] = token
            return platform_info

    console.print(f"[red]No se pudo extraer owner/repo de la URL: {url}[/red]")
    return None

def create_github_release(platform_info, tag, message, changelog_content):
    """Crea un release en GitHub."""
    headers = {
        'Authorization': f'token {platform_info["token"]}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }

    data = {
        'tag_name': tag,
        'name': f'Release {tag}',
        'body': changelog_content,
        'draft': False,
        'prerelease': False
    }

    url = f"{platform_info['api_base']}/repos/{platform_info['owner']}/{platform_info['repo']}/releases"

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error creando release en GitHub: {e}[/red]")
        return None

def create_gitlab_release(platform_info, tag, message, changelog_content):
    """Crea un release en GitLab."""
    headers = {
        'Authorization': f'Bearer {platform_info["token"]}',
        'Content-Type': 'application/json'
    }

    data = {
        'name': f'Release {tag}',
        'tag_name': tag,
        'description': changelog_content,
        'ref': tag
    }

    url = f"{platform_info['api_base']}/projects/{platform_info['owner']}%2F{platform_info['repo']}/releases"

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error creando release en GitLab: {e}[/red]")
        return None

def create_forgejo_release(platform_info, tag, message, changelog_content):
    """Crea un release en Forgejo/Gitea."""
    headers = {
        'Authorization': f'token {platform_info["token"]}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {
        'tag_name': tag,
        'name': f'Release {tag}',
        'body': changelog_content,
        'draft': False,
        'prerelease': False
    }

    url = f"{platform_info['api_base']}/repos/{platform_info['owner']}/{platform_info['repo']}/releases"

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error creando release en Forgejo: {e}[/red]")
        return None

def create_gitea_release(platform_info, tag, message, changelog_content):
    """Crea un release en Gitea."""
    # Gitea usa la misma API que Forgejo
    return create_forgejo_release(platform_info, tag, message, changelog_content)

def create_platform_release_func(platform_info, tag, message, changelog_content):
    """Crea un release en la plataforma correspondiente."""
    service = platform_info['service']

    if service == 'github':
        return create_github_release(platform_info, tag, message, changelog_content)
    elif service == 'gitlab':
        return create_gitlab_release(platform_info, tag, message, changelog_content)
    elif service == 'forgejo':
        return create_forgejo_release(platform_info, tag, message, changelog_content)
    elif service == 'gitea':
        return create_gitea_release(platform_info, tag, message, changelog_content)
    else:
        console.print(f"[red]Plataforma no soportada: {service}[/red]")
        return None

def read_changelog_content(project_path, tag=None):
    """Lee el contenido del CHANGELOG.md o la sección específica de un tag."""
    changelog_file = project_path / 'CHANGELOG.md'
    if not changelog_file.exists():
        return None

    try:
        with open(changelog_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Si se especifica un tag, extraer solo esa sección
        if tag:
            import re
            # Patrón para encontrar la sección específica del tag
            # Busca desde ## [tag] hasta el siguiente ## o el final del archivo
            pattern = rf'## \[{re.escape(tag)}\] - [^\n]*\n(.*?)(?=\n## \[|$)'
            match = re.search(pattern, content, re.DOTALL)

            if match:
                section_content = match.group(1).strip()
                console.print(f"[blue]Extraída sección específica para {tag}[/blue]")
                return section_content
            else:
                console.print(f"[yellow]No se encontró sección específica para {tag}, usando todo el changelog[/yellow]")
                return content

        # Si no se especifica tag, devolver todo el contenido
        return content

    except Exception as e:
        console.print(f"[red]Error leyendo CHANGELOG.md: {e}[/red]")
        return None

@click.group()
def cli():
    """Release Manager - Herramienta para gestionar releases."""
    pass

@cli.command()
@click.option('--version', help='Versión del release (ej: v1.0.0)')
@click.option('--message', help='Mensaje del release')
@click.option('--push', is_flag=True, help='Subir tag al repositorio remoto')
@click.option('--regenerate-changelog/--no-regenerate-changelog', default=True, help='Regenerar CHANGELOG después del release')
@click.option('--dry-run', is_flag=True, help='Mostrar qué se haría sin ejecutar')
@click.option('-p', '--path', default='.', help='Ruta del proyecto (por defecto: directorio actual)')
@click.option('--force-main', is_flag=True, help='Forzar checkout a main antes del release')
def set_release(version, message, push, regenerate_changelog, dry_run, path, force_main):
    """Crea un release con tag, push y regeneración de CHANGELOG (funcionalidad original)."""

    console.print(Panel.fit("🏷️ [bold blue]Set Release - Gestión Local[/bold blue]", style="blue"))

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

    table = Table(title="📊 Resumen del Set Release")
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
    if not Confirm.ask("¿Proceder con el set-release?"):
        console.print("[yellow]Set-release cancelado[/yellow]")
        return

    # Ejecutar set-release
    console.print("\n[green]🏷️ Iniciando set-release...[/green]")

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

    console.print(Panel.fit(f"🎉 [bold green]Set Release {version} completado exitosamente![/bold green]", style="green"))

    # Mostrar próximos pasos
    console.print("\n[blue]📋 Próximos pasos sugeridos:[/blue]")
    console.print("• Revisar el CHANGELOG generado")
    console.print("• Crear release notes en GitHub/GitLab si es necesario")
    console.print("• Notificar al equipo sobre el nuevo release")

@cli.command()
@click.option('--version', help='Versión del release (ej: v1.0.0)')
@click.option('--message', help='Mensaje del release')
@click.option('--push', is_flag=True, help='Subir tag al repositorio remoto')
@click.option('--regenerate-changelog/--no-regenerate-changelog', default=True, help='Regenerar CHANGELOG después del release')
@click.option('--dry-run', is_flag=True, help='Mostrar qué se haría sin ejecutar')
@click.option('-p', '--path', default='.', help='Ruta del proyecto (por defecto: directorio actual)')
@click.option('--force-main', is_flag=True, help='Forzar checkout a main antes del release')
@click.option('--from-tag', help='Crear release desde un tag existente')
@click.option('--create-platform-release', is_flag=True, default=True, help='Crear release en la plataforma Git')
def release(version, message, push, regenerate_changelog, dry_run, path, force_main, from_tag, create_platform_release):
    """Crea un release completo con integración de APIs de plataformas Git."""

    console.print(Panel.fit("🚀 [bold blue]Release Manager - Integración Completa[/bold blue]", style="blue"))

    project_path = Path(path).resolve()

    # Verificar que estamos en un repositorio Git
    if not (project_path / '.git').exists():
        console.print(f"[red]Error: No se encontró un repositorio Git en {project_path}[/red]")
        sys.exit(1)

    # Detectar plataforma y token
    platform_info = detect_git_platform_and_token(project_path)
    if not platform_info:
        console.print("[red]Error: No se pudo detectar la plataforma Git o obtener el token[/red]")
        sys.exit(1)

    console.print(f"[blue]Plataforma detectada:[/blue] {platform_info['service'].upper()}")
    console.print(f"[blue]Repositorio:[/blue] {platform_info['owner']}/{platform_info['repo']}")

    # Obtener información del repositorio
    current_branch = get_current_branch(project_path)
    latest_tag = get_latest_tag(project_path)

    console.print(f"[blue]Rama actual:[/blue] {current_branch}")
    console.print(f"[blue]Último Tag:[/blue] {latest_tag or 'Ninguno'}")
    console.print(f"[blue]Directorio del proyecto:[/blue] {project_path}")

    # Determinar tag a usar
    target_tag = None
    if from_tag:
        target_tag = from_tag
        console.print(f"[blue]Usando tag especificado:[/blue] {target_tag}")
    elif version:
        target_tag = version if version.startswith('v') else f"v{version}"
        console.print(f"[blue]Creando nuevo tag:[/blue] {target_tag}")
    else:
        # Usar el último tag disponible
        target_tag = latest_tag
        if target_tag:
            console.print(f"[blue]Usando último tag disponible:[/blue] {target_tag}")
        else:
            console.print("[red]Error: No hay tags disponibles y no se especificó versión[/red]")
            sys.exit(1)

    # Si se especifica versión pero no existe el tag, crear el tag primero
    if version and not from_tag:
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
                if not Confirm.ask("¿Continuar desde la rama actual?"):
                    console.print("[yellow]Release cancelado[/yellow]")
                    return

        # Validar versión
        if not validate_version(version):
            console.print("[red]Error: Formato de versión inválido. Usa formato semántico (ej: v1.0.0)[/red]")
            sys.exit(1)

        # Asegurar que la versión tenga prefijo 'v'
        if not version.startswith('v'):
            version = f"v{version}"
            target_tag = version

        # Obtener mensaje
        if not message:
            message = Prompt.ask(
                "Mensaje del release",
                default=f"Release {target_tag}"
            )

        # Crear tag
        console.print(f"[blue]Creando tag {target_tag}...[/blue]")
        tag_command = f'git tag -a {target_tag} -m "{message}"'
        if not run_command(tag_command, cwd=project_path):
            console.print("[red]Error creando Tag[/red]")
            sys.exit(1)
        console.print(f"[green]✓ Tag {target_tag} creado[/green]")

        # Push del tag
        if push:
            console.print("[blue]Subiendo Tag al remoto...[/blue]")
            push_command = f"git push origin {target_tag}"
            if not run_command(push_command, cwd=project_path):
                console.print("[red]Error subiendo Tag[/red]")
                sys.exit(1)
            console.print(f"[green]✓ Tag {target_tag} subido al remoto[/green]")

    # Regenerar CHANGELOG si es necesario
    if regenerate_changelog:
        console.print("[blue]Regenerando CHANGELOG...[/blue]")
        changelog_command = f"python docgen.py generate --doc-type changelog --output CHANGELOG.md --base-path {project_path}"
        if not run_command(changelog_command, cwd=project_path):
            console.print("[red]Error regenerando CHANGELOG[/red]")
            sys.exit(1)
        console.print("[green]✓ CHANGELOG regenerado[/green]")

        # Commit del CHANGELOG actualizado
        console.print("[blue]Commit del CHANGELOG actualizado...[/blue]")
        add_command = "git add CHANGELOG.md"
        commit_command = f'git commit -m "[CI] Auto-update changelog for {target_tag}"'

        if run_command(add_command, cwd=project_path) and run_command(commit_command, cwd=project_path):
            console.print("[green]✓ CHANGELOG committeado[/green]")

            if push:
                push_main_command = "git push origin main"
                if run_command(push_main_command, cwd=project_path):
                    console.print("[green]✓ Cambios subidos a main[/green]")

    # Crear release en la plataforma
    if create_platform_release:
        console.print(f"[blue]Creando release en {platform_info['service'].upper()}...[/blue]")

        # Leer contenido del CHANGELOG específico para el tag
        changelog_content = read_changelog_content(project_path, target_tag)
        if not changelog_content:
            changelog_content = f"Release {target_tag}"
            console.print("[yellow]No se pudo leer CHANGELOG.md, usando mensaje por defecto[/yellow]")

        # Crear release en la plataforma
        release_result = create_platform_release_func(platform_info, target_tag, message or f"Release {target_tag}", changelog_content)

        if release_result:
            console.print(f"[green]✓ Release creado en {platform_info['service'].upper()}[/green]")
            if 'html_url' in release_result:
                console.print(f"[blue]URL del release:[/blue] {release_result['html_url']}")
        else:
            console.print(f"[red]Error creando release en {platform_info['service'].upper()}[/red]")

    console.print(Panel.fit(f"🎉 [bold green]Release {target_tag} completado exitosamente![/bold green]", style="green"))

    # Mostrar próximos pasos
    console.print("\n[blue]📋 Próximos pasos sugeridos:[/blue]")
    console.print("• Revisar el release creado en la plataforma")
    console.print("• Verificar que el CHANGELOG esté correcto")
    console.print("• Notificar al equipo sobre el nuevo release")

if __name__ == "__main__":
    cli()
