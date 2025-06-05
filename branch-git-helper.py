#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Branch Git Helper - Sistema inteligente de gestión de branches con detección automática de contexto.

Este script proporciona una interfaz unificada para crear y gestionar branches de Git
adaptándose automáticamente al contexto del proyecto (LOCAL, HYBRID, REMOTE).
"""

import argparse
import subprocess
import sys
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum # Importar Enum

# Opcional: Colorama para mejor experiencia visual
try:
    from colorama import Fore, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
    colorama_init(autoreset=True)
except ImportError:
    COLORAMA_AVAILABLE = False
    class DummyColorama:
        def __getattr__(self, name): return ""
    Fore = Style = DummyColorama()

class ValidationLevel(Enum):
    PERMISSIVE = "permissive"
    MODERATE = "moderate"
    STRICT = "strict"

# Configuración de tipos de branch soportados
BRANCH_TYPES = {
    "feature": {
        "description": "Nuevas características y funcionalidades",
        "base_branch_priority": ["develop", "main"]
    },
    "fix": {
        "description": "Correcciones de errores y bugs",
        "base_branch_priority": ["develop", "main"]
    },
    "hotfix": {
        "description": "Correcciones urgentes en producción",
        "base_branch_priority": ["main", "master"]
    },
    "docs": {
        "description": "Documentación y cambios en docs",
        "base_branch_priority": ["develop", "main"]
    },
    "refactor": {
        "description": "Refactorización de código sin cambios funcionales",
        "base_branch_priority": ["develop", "main"]
    },
    "test": {
        "description": "Añadir o mejorar tests",
        "base_branch_priority": ["develop", "main"]
    },
    "chore": {
        "description": "Tareas de mantenimiento y build",
        "base_branch_priority": ["develop", "main"]
    }
}

# Configuración de contextos
CONTEXT_CONFIGS = {
    "LOCAL": {
        "validation_level": "warning",
        "auto_push": False,
        "require_upstream": False,
        "protected_branches": ["main", "master"],  # Mantener master para compatibilidad
        "allow_direct_push_to_main": True,  # Permitir push directo a main/master en LOCAL
        "enforce_branch_naming": False,  # No forzar naming en LOCAL
        "require_linear_history": False,  # No requerir historia lineal en LOCAL
        "require_pr": False,  # No requerir PRs en LOCAL
        "ci_cd_only_main": True  # CI/CD solo en main/master
    },
    "HYBRID": {
        "validation_level": "moderate",
        "auto_push": True,
        "require_upstream": True,
        "protected_branches": ["main", "master", "develop"],  # Mantener master para compatibilidad
        "allow_direct_push_to_main": False,
        "enforce_branch_naming": True,
        "require_linear_history": False,
        "require_pr": False,
        "ci_cd_only_main": True
    },
    "REMOTE": {
        "validation_level": "strict",
        "auto_push": True,
        "require_upstream": True,
        "protected_branches": ["main", "master", "develop", "staging", "release"],  # Mantener master para compatibilidad
        "allow_direct_push_to_main": False,
        "enforce_branch_naming": True,
        "require_linear_history": True,
        "require_pr": True,
        "ci_cd_only_main": False
    }
}

# Configuración de validaciones por contexto
VALIDATION_CONFIGS = {
    "LOCAL": {
        "level": ValidationLevel.PERMISSIVE,
        "protected_branches": ["main", "master"],  # Mantener master para compatibilidad
        "require_upstream": False,
        "require_pr": False,
        "allow_direct_push_to_main": True,  # Permitir push directo a main/master en LOCAL
        "enforce_branch_naming": False,  # No forzar naming en LOCAL
        "require_linear_history": False,  # No requerir historia lineal en LOCAL
        "ci_cd_only_main": True,  # CI/CD solo en main/master
        "require_gpg_verification": True  # Requerir GPG en todos los contextos por buenas prácticas
    },
    "HYBRID": {
        "level": ValidationLevel.MODERATE,
        "protected_branches": ["main", "master", "develop"],  # Mantener master para compatibilidad
        "require_upstream": True,
        "require_pr": False,
        "allow_direct_push_to_main": False,
        "enforce_branch_naming": True,
        "require_linear_history": False,
        "ci_cd_only_main": True,
        "require_gpg_verification": True  # Requerir GPG en todos los contextos por buenas prácticas
    },
    "REMOTE": {
        "level": ValidationLevel.STRICT,
        "protected_branches": ["main", "master", "develop", "staging", "release"],  # Mantener master para compatibilidad
        "require_upstream": True,
        "require_pr": True,
        "allow_direct_push_to_main": False,
        "enforce_branch_naming": True,
        "require_linear_history": True,
        "ci_cd_only_main": False,
        "require_gpg_verification": True  # Requerir GPG en todos los contextos por buenas prácticas
    }
}

class GitRepository:
    """Clase para interactuar con el repositorio Git."""

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self._validate_git_repo()

    def _validate_git_repo(self):
        """Valida que estemos en un repositorio Git válido."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            print(f"{Fore.RED}Error: No se encontró un repositorio Git en '{self.repo_path}'{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Ejecute 'git init' para inicializar un repositorio.{Style.RESET_ALL}")
            sys.exit(1)

    def run_command(self, command: List[str], check: bool = True) -> Tuple[bool, str, str]:
        """Ejecuta un comando Git y retorna (success, stdout, stderr)."""
        try:
            result = subprocess.run(
                command,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=check,
                encoding='utf-8'
            )
            return True, result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else ""
        except Exception as e:
            return False, "", str(e)

    def get_current_branch(self) -> Optional[str]:
        """Obtiene la rama actual."""
        success, stdout, _ = self.run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return stdout if success else None

    def branch_exists(self, branch_name: str) -> bool:
        """Verifica si una rama existe."""
        success, stdout, _ = self.run_command(["git", "branch", "--list", branch_name])
        return bool(stdout.strip())

    def get_remote_count(self) -> int:
        """Obtiene el número de remotos configurados."""
        success, stdout, _ = self.run_command(["git", "remote"])
        return len(stdout.split()) if success and stdout else 0

    def get_contributor_count(self) -> int:
        """Obtiene el número de contribuidores únicos."""
        success, stdout, _ = self.run_command(["git", "shortlog", "-sn"])
        return len(stdout.split('\n')) if success and stdout else 1

    def get_commit_count(self) -> int:
        """Obtiene el número total de commits."""
        success, stdout, _ = self.run_command(["git", "rev-list", "--count", "HEAD"])
        try:
            return int(stdout) if success and stdout else 0
        except ValueError:
            return 0

    def has_uncommitted_changes(self) -> bool:
        """Verifica si hay cambios sin confirmar."""
        success, stdout, _ = self.run_command(["git", "status", "--porcelain"])
        return bool(stdout.strip()) if success else False

    def detect_ci_presence(self) -> bool:
        """Detecta la presencia de archivos CI/CD."""
        ci_indicators = [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".travis.yml",
            "azure-pipelines.yml",
            "bitbucket-pipelines.yml",
            "Jenkinsfile"
        ]

        for indicator in ci_indicators:
            if (self.repo_path / indicator).exists():
                return True
        return False

    def get_branch_state(self, branch_name: str = None) -> Optional[str]:
        """
        Determina el estado de una rama (WIP, MERGED, o DELETED).
        Prioriza tags remotos, luego git notes locales, y finalmente analiza commits.

        Args:
            branch_name: Nombre de la rama a verificar. Si es None, usa la rama actual.

        Returns:
            str: "WIP" si la rama está en desarrollo,
                 "MERGED" si sus commits están mergeados o marcada con tag merged-,
                 "DELETED" si la rama está marcada con tag deleted-,
                 o None si hay error o no se puede determinar.
        """
        branch = branch_name or self.get_current_branch()
        if not branch:
            return None

        # Prioridad 1: Verificar tags remotos (fetch para asegurar que estén actualizados)
        self.run_command(["git", "fetch", "origin", "--tags"], check=False) # Fetch all tags to be sure

        success_merged, stdout_merged, _ = self.run_command(["git", "tag", "-l", f"merged-{branch}"])
        if success_merged and stdout_merged.strip():
            return "MERGED"

        success_deleted, stdout_deleted, _ = self.run_command(["git", "tag", "-l", f"deleted-{branch}"])
        if success_deleted and stdout_deleted.strip():
            return "DELETED"

        # Prioridad 2: Verificar git notes locales
        # Necesitamos el hash del HEAD de la rama para consultar sus notas
        success_head, stdout_head, _ = self.run_command(["git", "rev-parse", branch])
        if success_head and stdout_head:
            commit_hash = stdout_head.strip()
            success_notes, stdout_notes, _ = self.run_command(["git", "notes", "show", commit_hash], check=False)
            if success_notes and stdout_notes:
                for line in stdout_notes.split('\n'):
                    if line.startswith('branch_state:'):
                        forced_state = line.split(':', 1)[1].strip()
                        if forced_state in ['WIP', 'MERGED', 'DELETED']:
                            return forced_state

        # Prioridad 3: Si no hay estado explícito, verificar por commits (solo para ramas existentes)
        if not self.branch_exists(branch): # If branch doesn't exist locally, cannot infer WIP/MERGED from commits
            return None

        branch_type = branch.split('/')[0] if '/' in branch else None
        base_branch = None

        if branch_type in BRANCH_TYPES:
            for base in BRANCH_TYPES[branch_type]["base_branch_priority"]:
                if self.branch_exists(base):
                    base_branch = base
                    break

        if not base_branch:
            for base in ["main", "master"]:
                if self.branch_exists(base):
                    base_branch = base
                    break

        if not base_branch:
            return None

        # Verificar si hay commits únicos en la rama respecto a la base
        success_commits, stdout_commits, _ = self.run_command([
            "git", "rev-list", "--left-right", "--count",
            f"{base_branch}...{branch}"
        ])

        if not success_commits or not stdout_commits:
            return None

        try:
            _, unique_commits = map(int, stdout_commits.split())
            return "WIP" if unique_commits > 0 else "MERGED"
        except (ValueError, IndexError):
            return None

    def set_branch_state(self, branch_name: str, state: str, push_to_remote_tags: bool = True) -> bool:
        """
        Establece el estado de una rama usando tags y git notes.

        Args:
            branch_name: Nombre de la rama.
            state: Estado a establecer ("WIP", "MERGED", o "DELETED").
            push_to_remote_tags: Si True, se empujan los tags de estado al remoto.

        Returns:
            bool: True si el estado se estableció correctamente.
        """
        if state not in ['WIP', 'MERGED', 'DELETED']:
            print(f"{Fore.RED}❌ Estado inválido: {state}{Style.RESET_ALL}")
            return False

        # 1. Eliminar tags de estado existentes (local y remoto)
        existing_tags = []
        success_list_tags, stdout_list_tags, _ = self.run_command(["git", "tag", "-l", f"merged-{branch_name}", f"deleted-{branch_name}"])
        if success_list_tags and stdout_list_tags:
            existing_tags = stdout_list_tags.split()

        for tag in existing_tags:
            print(f"{Fore.CYAN}🗑️  Eliminando tag '{tag}' (local)...{Style.RESET_ALL}")
            self.run_command(["git", "tag", "-d", tag], check=False) # Eliminar localmente
            if push_to_remote_tags:
                print(f"{Fore.CYAN}🗑️  Eliminando tag '{tag}' (remoto)...{Style.RESET_ALL}")
                # Eliminar tag remoto, importante usar ':'
                success_rm_remote, _, error_rm_remote = self.run_command(["git", "push", "origin", f":refs/tags/{tag}"], check=False)
                if not success_rm_remote and "remote ref does not exist" not in error_rm_remote:
                    print(f"{Fore.YELLOW}⚠️  No se pudo eliminar tag remoto '{tag}': {error_rm_remote}{Style.RESET_ALL}")

        # Obtener el HEAD de la rama para las notas
        success_head_hash, stdout_head_hash, _ = self.run_command(["git", "rev-parse", branch_name])
        if not success_head_hash:
            print(f"{Fore.YELLOW}⚠️  No se pudo obtener el HEAD de la rama '{branch_name}' para notas.{Style.RESET_ALL}")
            current_head_hash = "HEAD" # Fallback, might not be accurate if branch is deleted
        else:
            current_head_hash = stdout_head_hash.strip()

        # 2. Actualizar git notes locales (siempre al commit actual)
        print(f"{Fore.CYAN}📝 Actualizando git notes locales para '{branch_name}' a estado '{state}'...{Style.RESET_ALL}")
        # Eliminar notas previas para este commit si existen
        self.run_command(["git", "notes", "--ref=commits", "remove", current_head_hash], check=False)
        success_note_add, _, error_note_add = self.run_command([
            "git", "notes", "--ref=commits", "add", "-m", f"branch_state:{state}", current_head_hash
        ])
        if not success_note_add:
            print(f"{Fore.YELLOW}⚠️  No se pudo actualizar git notes para '{branch_name}': {error_note_add}{Style.RESET_ALL}")
            # No es crítico, el tag es la fuente principal para el remoto

        # 3. Crear y empujar nuevos tags (si el estado es final y se solicita)
        if state in ['MERGED', 'DELETED'] and push_to_remote_tags:
            tag_name = f"{state.lower()}-{branch_name}"
            print(f"{Fore.CYAN}🏷️  Creando tag '{tag_name}' (local)...{Style.RESET_ALL}")
            success_tag_create, _, error_tag_create = self.run_command(["git", "tag", tag_name])
            if not success_tag_create:
                print(f"{Fore.YELLOW}⚠️  No se pudo crear tag '{tag_name}': {error_tag_create}{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}📤 Empujando tag '{tag_name}' al remoto...{Style.RESET_ALL}")
            success_tag_push, _, error_tag_push = self.run_command(["git", "push", "origin", tag_name])
            if not success_tag_push:
                print(f"{Fore.YELLOW}⚠️  No se pudo empujar tag '{tag_name}' al remoto: {error_tag_push}{Style.RESET_ALL}")
                return False

        return True

    def get_branch_info(self, branch_name: str = None) -> Dict:
        """
        Obtiene información detallada de una rama, incluyendo su estado funcional.

        Args:
            branch_name: Nombre de la rama. Si es None, usa la rama actual.

        Returns:
            Dict con información de la rama:
            {
                "name": str,
                "state": str,  # "WIP", "MERGED", o "DELETED"
                "type": str,   # tipo de branch (feature, fix, etc.)
                "base": str,   # rama base
                "last_commit": str,  # último commit
                "last_commit_date": str,  # fecha del último commit
                "unique_commits": int,  # número de commits únicos
                "tags": List[str]  # tags de estado asociados a la rama
            }
        """
        branch = branch_name or self.get_current_branch()
        if not branch:
            return None

        info = {
            "name": branch,
            "state": self.get_branch_state(branch), # Usar el nuevo método
            "type": branch.split('/')[0] if '/' in branch else None,
            "base": None,
            "last_commit": None,
            "last_commit_date": None,
            "unique_commits": 0,
            "tags": []
        }

        # Obtener tags de estado asociados
        success, stdout, _ = self.run_command(["git", "tag", "-l", f"merged-{branch}", f"deleted-{branch}"])
        if success and stdout:
            info["tags"] = stdout.split()

        # Obtener rama base
        if info["type"] in BRANCH_TYPES:
            for base in BRANCH_TYPES[info["type"]]["base_branch_priority"]:
                if self.branch_exists(base):
                    info["base"] = base
                    break

        if not info["base"]:
            for base in ["main", "master"]:
                if self.branch_exists(base):
                    info["base"] = base
                    break

        # Obtener último commit
        success, stdout, _ = self.run_command([
            "git", "log", "-1", "--format=%H|%ai", branch
        ])
        if success and stdout:
            commit_hash, commit_date = stdout.split('|')
            info["last_commit"] = commit_hash
            info["last_commit_date"] = commit_date

        # Obtener número de commits únicos
        if info["base"]:
            success, stdout, _ = self.run_command([
                "git", "rev-list", "--left-right", "--count",
                f"{info['base']}...{branch}"
            ])
            if success and stdout:
                try:
                    _, unique_commits = map(int, stdout.split())
                    info["unique_commits"] = unique_commits
                except (ValueError, IndexError):
                    pass

        return info

    def sync_branch_states(self, dry_run: bool = False) -> Dict[str, List[str]]:
        """
        Sincroniza los estados de las ramas entre local y remoto.

        Args:
            dry_run: Si es True, solo muestra las acciones que se realizarían sin ejecutarlas

        Returns:
            Dict con las acciones realizadas:
            {
                "merged": List[str] - Ramas marcadas como MERGED en remoto
                "deleted": List[str] - Ramas marcadas como DELETED en remoto
                "errors": List[str] - Errores encontrados durante la sincronización
            }
        """
        actions = {
            "merged": [],
            "deleted": [],
            "errors": []
        }

        # Obtener todas las ramas locales
        success, stdout, _ = self.run_command(["git", "branch", "--format=%(refname:short)"])
        if not success:
            actions["errors"].append("No se pudieron obtener las ramas locales")
            return actions

        local_branches = [b.strip() for b in stdout.split('\n') if b.strip()]

        # Obtener todas las ramas remotas
        success, stdout, _ = self.run_command(["git", "branch", "-r", "--format=%(refname:short)"])
        if not success:
            actions["errors"].append("No se pudieron obtener las ramas remotas")
            return actions

        remote_branches = [b.strip().replace('origin/', '') for b in stdout.split('\n')
                         if b.strip() and not b.strip().startswith('origin/HEAD')]

        # Para cada rama local, verificar si está mergeada pero no marcada en remoto
        for branch in local_branches:
            # Ignorar ramas base
            if branch in ['main', 'master', 'develop']:
                continue

            # Verificar si la rama está mergeada localmente
            state = self.get_branch_state(branch)
            if state == "MERGED":
                # Verificar si existe en remoto
                if branch in remote_branches:
                    # Verificar si ya está marcada como MERGED en remoto
                    success, stdout, _ = self.run_command(["git", "ls-remote", "--tags", "origin", f"merged-{branch}"])
                    if not success or not stdout.strip():
                        if dry_run:
                            print(f"{Fore.YELLOW}[DRY RUN] Marcar como MERGED en remoto: {branch}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.CYAN}📝 Marcando como MERGED en remoto: {branch}{Style.RESET_ALL}")
                            if self.set_branch_state(branch, "MERGED"):
                                actions["merged"].append(branch)
                                print(f"{Fore.GREEN}✅ Estado actualizado{Style.RESET_ALL}")
                            else:
                                actions["errors"].append(f"No se pudo marcar {branch} como MERGED en remoto")

        # Para cada rama remota, verificar si no existe localmente
        for branch in remote_branches:
            # Ignorar ramas base
            if branch in ['main', 'master', 'develop']:
                continue

            # Verificar si la rama no existe localmente
            if branch not in local_branches:
                # Verificar si ya está marcada como DELETED en remoto
                success, stdout, _ = self.run_command(["git", "ls-remote", "--tags", "origin", f"deleted-{branch}"])
                if not success or not stdout.strip():
                    if dry_run:
                        print(f"{Fore.YELLOW}[DRY RUN] Marcar como DELETED en remoto: {branch}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.CYAN}📝 Marcando como DELETED en remoto: {branch}{Style.RESET_ALL}")
                        if self.set_branch_state(branch, "DELETED"):
                            actions["deleted"].append(branch)
                            print(f"{Fore.GREEN}✅ Estado actualizado{Style.RESET_ALL}")
                        else:
                            actions["errors"].append(f"No se pudo marcar {branch} como DELETED en remoto")

        return actions

class ContextDetector:
    """Detector automático de contexto de desarrollo."""

    def __init__(self, git_repo: GitRepository):
        self.git_repo = git_repo

    def detect_context(self) -> str:
        """
        Detecta automáticamente el contexto de desarrollo.
        Primero verifica si hay un contexto forzado, luego usa la detección automática.

        Returns:
            str: "LOCAL", "HYBRID", o "REMOTE"
        """
        # Verificar si hay un contexto forzado
        success, stdout, _ = self.git_repo.run_command(["git", "notes", "show", "HEAD"])
        if success and stdout:
            for line in stdout.split('\n'):
                if line.startswith('forced_context:'):
                    forced_context = line.split(':', 1)[1].strip()
                    if forced_context in ['LOCAL', 'HYBRID', 'REMOTE']:
                        return forced_context

        # Si no hay contexto forzado, usar detección automática
        remotes = self.git_repo.get_remote_count()
        has_develop = self.git_repo.branch_exists("develop")
        has_staging = self.git_repo.branch_exists("staging")
        contributors = self.git_repo.get_contributor_count()

        # Es LOCAL si cumple cualquiera de estas condiciones:
        # 1. No tiene remotos
        # 2. No tiene ni develop ni staging
        # 3. Tiene menos de 2 contribuidores
        if (remotes == 0 or
            (not has_develop and not has_staging) or
            contributors < 2):
            return "LOCAL"

        # Si no es LOCAL, determinar entre HYBRID y REMOTE
        has_ci = self.git_repo.detect_ci_presence()

        if has_ci or contributors > 2:  # Más de 2 contribuidores o tiene CI
            return "REMOTE"
        else:
            return "HYBRID"

    def get_context_info(self, context: str) -> Dict:
        """Obtiene información detallada del contexto detectado."""
        contributors = self.git_repo.get_contributor_count()
        commits = self.git_repo.get_commit_count()
        remotes = self.git_repo.get_remote_count()
        has_ci = self.git_repo.detect_ci_presence()

        return {
            "context": context,
            "contributors": contributors,
            "commits": commits,
            "remotes": remotes,
            "has_ci": has_ci,
            "config": CONTEXT_CONFIGS[context]
        }

    def force_context(self, context: str):
        """Forza el contexto actual a uno específico."""
        self.git_repo.run_command(["git", "notes", "add", "-m", f"forced_context:{context}", "HEAD"])
        print(f"{Fore.GREEN}✅ Contexto forzado a '{context}'{Style.RESET_ALL}")

class BranchHelper:
    """Helper principal para gestión de branches."""

    def __init__(self, git_repo: GitRepository):
        self.git_repo = git_repo
        self.context_detector = ContextDetector(git_repo)

    def clean_branch_name(self, name: str) -> str:
        """Limpia y normaliza el nombre de la rama."""
        # Convertir a minúsculas
        name = name.lower()
        # Reemplazar espacios por guiones
        name = re.sub(r'\s+', '-', name)
        # Remover caracteres especiales excepto guiones y underscores
        name = re.sub(r'[^a-z0-9\-_]', '', name)
        # Reemplazar múltiples delimitadores
        name = re.sub(r'[-_]{2,}', '-', name)
        # Limpiar extremos
        name = name.strip('-_')

        return name

    def get_base_branch_for_type(self, branch_type: str, context: str) -> str:
        """Determina la rama base apropiada para el tipo de branch."""
        if branch_type not in BRANCH_TYPES:
            return "main"

        priority_list = BRANCH_TYPES[branch_type]["base_branch_priority"]

        # Para hotfix siempre intentar main/master primero
        if branch_type == "hotfix":
            for branch in ["main", "master"]:
                if self.git_repo.branch_exists(branch):
                    return branch

        # Para otros tipos, seguir la prioridad configurada
        for branch in priority_list:
            if self.git_repo.branch_exists(branch):
                return branch

        # Fallback: buscar main o master
        for branch in ["main", "master"]:
            if self.git_repo.branch_exists(branch):
                return branch

        # Último recurso: usar la rama actual
        return self.git_repo.get_current_branch() or "main"

    def create_branch(self, branch_type: str, description: str, options: Dict) -> bool:
        """Crea una nueva rama con el workflow apropiado."""

        # Detectar contexto
        context = self.context_detector.detect_context()
        context_info = self.context_detector.get_context_info(context)

        print(f"{Fore.CYAN}🔍 Contexto detectado: {Fore.YELLOW}{context}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📊 Contribuidores: {context_info['contributors']}, "
              f"Commits: {context_info['commits']}, "
              f"Remotos: {context_info['remotes']}{Style.RESET_ALL}")

        # Validar tipo de branch
        if branch_type not in BRANCH_TYPES:
            print(f"{Fore.RED}❌ Tipo de rama '{branch_type}' no válido.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Tipos disponibles: {', '.join(BRANCH_TYPES.keys())}{Style.RESET_ALL}")
            return False

        # Limpiar nombre
        clean_description = self.clean_branch_name(description)
        if not clean_description:
            print(f"{Fore.RED}❌ La descripción '{description}' no es válida después de la limpieza.{Style.RESET_ALL}")
            return False

        # Construir nombre completo
        full_branch_name = f"{branch_type}/{clean_description}"

        # Verificar si la rama ya existe
        if self.git_repo.branch_exists(full_branch_name):
            print(f"{Fore.YELLOW}⚠️  La rama '{full_branch_name}' ya existe.{Style.RESET_ALL}")
            response = input(f"{Fore.CYAN}¿Cambiar a la rama existente? (y/N): {Style.RESET_ALL}")
            if response.lower() in ['y', 'yes', 's', 'sí']:
                success, _, error = self.git_repo.run_command(["git", "checkout", full_branch_name])
                if success:
                    print(f"{Fore.GREEN}✅ Cambiado a rama existente '{full_branch_name}'{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}❌ Error al cambiar a rama: {error}{Style.RESET_ALL}")
                    return False
            else:
                print(f"{Fore.YELLOW}Operación cancelada.{Style.RESET_ALL}")
                return False

        # Verificar cambios sin confirmar
        if self.git_repo.has_uncommitted_changes():
            print(f"{Fore.RED}❌ Hay cambios sin confirmar en el repositorio.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Por favor, confirme o guarde sus cambios antes de continuar.{Style.RESET_ALL}")
            return False

        # Determinar rama base
        base_branch = self.get_base_branch_for_type(branch_type, context)
        print(f"{Fore.CYAN}📍 Rama base seleccionada: {Fore.YELLOW}{base_branch}{Style.RESET_ALL}")

        # Cambiar a rama base si es necesario
        current_branch = self.git_repo.get_current_branch()
        if current_branch != base_branch:
            print(f"{Fore.CYAN}🔄 Cambiando a rama base '{base_branch}'...{Style.RESET_ALL}")
            success, _, error = self.git_repo.run_command(["git", "checkout", base_branch])
            if not success:
                print(f"{Fore.RED}❌ Error al cambiar a rama base: {error}{Style.RESET_ALL}")
                return False

        # Actualizar rama base si hay remotos configurados
        if context_info['remotes'] > 0 and not options.get('no_sync', False):
            print(f"{Fore.CYAN}🔄 Actualizando rama base desde remoto...{Style.RESET_ALL}")
            success, output, error = self.git_repo.run_command(["git", "pull", "origin", base_branch])
            if not success:
                print(f"{Fore.YELLOW}⚠️  Advertencia: No se pudo actualizar desde remoto: {error}{Style.RESET_ALL}")
                response = input(f"{Fore.CYAN}¿Continuar sin actualizar? (y/N): {Style.RESET_ALL}")
                if response.lower() not in ['y', 'yes', 's', 'sí']:
                    return False

        # Crear nueva rama
        print(f"{Fore.CYAN}🌟 Creando rama '{full_branch_name}'...{Style.RESET_ALL}")
        success, _, error = self.git_repo.run_command(["git", "checkout", "-b", full_branch_name])
        if not success:
            print(f"{Fore.RED}❌ Error al crear la rama: {error}{Style.RESET_ALL}")
            return False

        # Establecer estado WIP usando el nuevo sistema
        print(f"{Fore.CYAN}📝 Estableciendo estado WIP para '{full_branch_name}'...{Style.RESET_ALL}")
        success = self.git_repo.set_branch_state(full_branch_name, "WIP", push_to_remote_tags=False)
        if not success:
            print(f"{Fore.YELLOW}⚠️  No se pudo establecer estado WIP para '{full_branch_name}'.{Style.RESET_ALL}")
            print(f"{Fore.BLUE}💡 La rama se creó pero sin estado WIP explícito. Considere 'git state wip'.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Estado WIP establecido para '{full_branch_name}'.{Style.RESET_ALL}")

        print(f"{Fore.GREEN}✅ Rama '{full_branch_name}' creada exitosamente{Style.RESET_ALL}")

        # Configurar upstream si es necesario
        config = context_info['config']
        if config['auto_push'] and context_info['remotes'] > 0 and not options.get('no_push', False):
            print(f"{Fore.CYAN}📤 Configurando upstream y haciendo push inicial...{Style.RESET_ALL}")
            success, _, error = self.git_repo.run_command(["git", "push", "-u", "origin", full_branch_name])
            if success:
                print(f"{Fore.GREEN}✅ Rama empujada al remoto y upstream configurado{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️  No se pudo hacer push: {error}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}💡 Puede hacer push manualmente: git push -u origin {full_branch_name}{Style.RESET_ALL}")

        # Mostrar información de siguiente paso
        print(f"\n{Fore.MAGENTA}🎉 ¡Listo para trabajar!{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📝 Rama actual: {full_branch_name}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🎯 Contexto: {context} - {BRANCH_TYPES[branch_type]['description']}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📊 Estado: {Fore.YELLOW}WIP{Style.RESET_ALL}")

        return True

    def mark_branch_state(self, branch_name: str, state: str, options: Dict) -> bool:
        """
        Marca una rama con un estado específico.
        Gestiona el merge (si es MERGED) y la eliminación local (si se solicita).

        Args:
            branch_name: Nombre de la rama a marcar.
            state: Estado a establecer ("WIP", "MERGED", o "DELETED").
            options: Opciones adicionales (e.g., {'delete': True}).

        Returns:
            bool: True si el estado se estableció correctamente.
        """
        if state not in ['WIP', 'MERGED', 'DELETED']:
            print(f"{Fore.RED}❌ Estado inválido: {state}. Use: WIP, MERGED, o DELETED.{Style.RESET_ALL}")
            return False

        if not self.git_repo.branch_exists(branch_name):
            print(f"{Fore.RED}❌ La rama '{branch_name}' no existe localmente.{Style.RESET_ALL}")
            return False

        # Verificar que no estamos en una rama protegida (main/master)
        protected_branches = self.context_detector.get_context_info(self.context_detector.detect_context())['protected_branches']
        if branch_name in protected_branches:
            print(f"{Fore.RED}❌ No se puede cambiar el estado de una rama protegida ({branch_name}).{Style.RESET_ALL}")
            return False

        current_branch = self.git_repo.get_current_branch()
        if not current_branch:
            print(f"{Fore.RED}❌ No se pudo determinar la rama actual. Asegúrese de estar en un repositorio válido.{Style.RESET_ALL}")
            return False

        base_branch = None
        branch_type = branch_name.split('/')[0] if '/' in branch_name else None
        if branch_type and branch_type in BRANCH_TYPES:
            for base in BRANCH_TYPES[branch_type]["base_branch_priority"]:
                if self.git_repo.branch_exists(base):
                    base_branch = base
                    break
        if not base_branch: # Fallback a main/master si no se encuentra base específica
            for base in ["main", "master"]:
                if self.git_repo.branch_exists(base):
                    base_branch = base
                    break

        if not base_branch:
            print(f"{Fore.RED}❌ No se pudo determinar una rama base válida para '{branch_name}'.{Style.RESET_ALL}")
            return False

        # --- Lógica principal para MERGED y DELETED ---
        if state == "MERGED":
            if current_branch != base_branch:
                print(f"{Fore.CYAN}🔄 Cambiando a la rama base '{base_branch}' para el merge...{Style.RESET_ALL}")
                success_checkout, _, error_checkout = self.git_repo.run_command(["git", "checkout", base_branch])
                if not success_checkout:
                    print(f"{Fore.RED}❌ Error al cambiar a rama base '{base_branch}': {error_checkout}{Style.RESET_ALL}")
                    return False

            print(f"{Fore.CYAN}🔄 Realizando merge de '{branch_name}' en '{base_branch}'...{Style.RESET_ALL}")
            success_merge, _, error_merge = self.git_repo.run_command(["git", "merge", branch_name])
            if not success_merge:
                print(f"{Fore.YELLOW}⚠️  Conflictos detectados al mergear '{branch_name}'. Por favor, resuelva los conflictos manualmente, luego:\n{Style.RESET_ALL}")
                print(f"{Fore.BLUE}   1. git add . {Style.RESET_ALL}")
                print(f"{Fore.BLUE}   2. git commit -m \"Merge {branch_name} a {base_branch}\" {Style.RESET_ALL}")
                print(f"{Fore.BLUE}   3. Vuelva a ejecutar: git state merged {'-d' if options.get('delete') else ''}{Style.RESET_ALL}")
                return False

            # Si el merge fue exitoso
            print(f"{Fore.GREEN}✅ Merge de '{branch_name}' en '{base_branch}' completado.{Style.RESET_ALL}")
            
            # Establecer estado MERGED (esto empujará el tag merged- al remoto)
            print(f"{Fore.CYAN}📝 Marcando estado a MERGED para '{branch_name}'...{Style.RESET_ALL}")
            success_set_state = self.git_repo.set_branch_state(branch_name, "MERGED", push_to_remote_tags=True)
            if not success_set_state:
                print(f"{Fore.YELLOW}⚠️  No se pudo establecer el estado MERGED para '{branch_name}'.{Style.RESET_ALL}")
                return False
            
            # Si se solicita borrar localmente, ADEMÁS, se crea el tag deleted- y se elimina localmente
            if options.get('delete', False):
                print(f"{Fore.CYAN}📝 Marcando estado a DELETED (debido a eliminación local) para '{branch_name}'...{Style.RESET_ALL}")
                success_set_deleted_tag = self.git_repo.set_branch_state(branch_name, "DELETED", push_to_remote_tags=True)
                if not success_set_deleted_tag:
                    print(f"{Fore.YELLOW}⚠️  No se pudo establecer el tag DELETED para '{branch_name}' a pesar de la eliminación local.{Style.RESET_ALL}")
                    # No es un error crítico para el flujo, pero se advierte.

                print(f"{Fore.CYAN}🗑️  Eliminando rama local '{branch_name}'...{Style.RESET_ALL}")
                # Importante: Volver a la rama base antes de borrar la rama actual
                if self.git_repo.get_current_branch() != base_branch:
                    self.git_repo.run_command(["git", "checkout", base_branch])
                success_delete, _, error_delete = self.git_repo.run_command(["git", "branch", "-d", branch_name])
                if success_delete:
                    print(f"{Fore.GREEN}✅ Rama '{branch_name}' eliminada localmente.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️  No se pudo eliminar la rama '{branch_name}' localmente: {error_delete}{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}💡 La rama puede tener commits no mergeados. Use 'git branch -D {branch_name}' para forzar la eliminación.{Style.RESET_ALL}")
            
            print(f"\n{Fore.MAGENTA}🎉 Proceso de MERGE y marcación de estado completado para '{branch_name}'.{Style.RESET_ALL}")
            return True

        elif state == "DELETED":
            # Establecer estado DELETED (esto empujará el tag deleted- al remoto)
            print(f"{Fore.CYAN}📝 Marcando estado a DELETED para '{branch_name}'...{Style.RESET_ALL}")
            success_set_state = self.git_repo.set_branch_state(branch_name, "DELETED", push_to_remote_tags=True)
            if not success_set_state:
                print(f"{Fore.YELLOW}⚠️  No se pudo establecer el estado DELETED para '{branch_name}'.{Style.RESET_ALL}")
                return False

            # Si se solicita borrar localmente
            if options.get('delete', False):
                print(f"{Fore.CYAN}🗑️  Eliminando rama local '{branch_name}'...{Style.RESET_ALL}")
                # Asegurarse de no estar en la rama que se va a borrar
                if current_branch == branch_name:
                    # Intentar cambiar a la rama base
                    success_checkout_base, _, error_checkout_base = self.git_repo.run_command(["git", "checkout", base_branch])
                    if not success_checkout_base:
                        print(f"{Fore.RED}❌ No se pudo cambiar a la rama base '{base_branch}' para eliminar '{branch_name}': {error_checkout_base}{Style.RESET_ALL}")
                        print(f"{Fore.BLUE}💡 Por favor, cambie a otra rama antes de eliminar '{branch_name}'.{Style.RESET_ALL}")
                        return False

                success_delete, _, error_delete = self.git_repo.run_command(["git", "branch", "-d", branch_name])
                if success_delete:
                    print(f"{Fore.GREEN}✅ Rama '{branch_name}' eliminada localmente.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️  No se pudo eliminar la rama '{branch_name}' localmente: {error_delete}{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}💡 La rama puede tener commits no mergeados o no se pudo eliminar por otras razones. Use 'git branch -D {branch_name}' para forzar la eliminación.{Style.RESET_ALL}")

            print(f"\n{Fore.MAGENTA}🎉 Estado de '{branch_name}' marcado como DELETED.{Style.RESET_ALL}")
            return True

        elif state == "WIP":
            # Para WIP, simplemente establecemos el estado y limpiamos tags si existen
            print(f"{Fore.CYAN}📝 Marcando estado a WIP para '{branch_name}' (limpiando tags de estado)...{Style.RESET_ALL}")
            success_set_state = self.git_repo.set_branch_state(branch_name, "WIP", push_to_remote_tags=True)
            if not success_set_state:
                print(f"{Fore.YELLOW}⚠️  No se pudo establecer el estado WIP para '{branch_name}'.{Style.RESET_ALL}")
                return False
            print(f"\n{Fore.MAGENTA}🎉 Estado de '{branch_name}' marcado como WIP.{Style.RESET_ALL}")
            return True
        
        return False # Fallback si no se cumple ninguna condición

class AliasManager:
    """Gestor de aliases persistentes de Git."""

    @classmethod
    def install_aliases(cls) -> bool:
        """Instala aliases persistentes para el helper."""
        script_path = cls.get_script_path()

        # Aliases que usan el directorio actual de donde se ejecutan
        aliases = {
            'new-feature': f'!python {script_path} feature',
            'new-fix': f'!python {script_path} fix',
            'new-hotfix': f'!python {script_path} hotfix',
            'new-docs': f'!python {script_path} docs',
            'new-refactor': f'!python {script_path} refactor',
            'new-test': f'!python {script_path} test',
            'new-chore': f'!python {script_path} chore',
            'branch-status': f'!python {script_path} status',
            # Aliases para el comando state
            'state': f'!python {script_path} state',          # Alias general para el comando 'state'
            'merged': f'!python {script_path} state merged',  # Marcar rama como mergeada, dejar local
            'deleted': f'!python {script_path} state deleted', # Marcar rama como eliminada localmente, dejar local
            'wip': f'!python {script_path} state wip',        # Forzar estado WIP (limpia tags de estado remoto)
            'merged-d': f'!python {script_path} state merged -d', # Mergear, señalizar merge y eliminación local, y borrar rama local
            'deleted-d': f'!python {script_path} state deleted -d', # Señalizar eliminación local y borrar rama local
            # Aliases adicionales para trabajo con proyectos específicos
            'new-feature-in': f'!f() {{ python {script_path} -p "$1" feature "$2"; }}; f',
            'new-fix-in': f'!f() {{ python {script_path} -p "$1" fix "$2"; }}; f',
            'branch-status-in': f'!f() {{ python {script_path} -p "$1" status; }}; f'
        }

        print(f"{Fore.CYAN}🔧 Instalando aliases persistentes...{Style.RESET_ALL}")

        # Crear backup
        if not cls.backup_git_config():
            return False

        # Instalar cada alias
        success_count = 0
        for alias_name, command in aliases.items():
            try:
                result = subprocess.run([
                    'git', 'config', '--global', f'alias.{alias_name}', command
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"{Fore.GREEN}  ✅ {alias_name}{Style.RESET_ALL}")
                    success_count += 1
                else:
                    print(f"{Fore.RED}  ❌ {alias_name}: {result.stderr}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}  ❌ {alias_name}: {e}{Style.RESET_ALL}")

        if success_count == len(aliases):
            print(f"\n{Fore.GREEN}🎉 Todos los aliases instalados exitosamente!{Style.RESET_ALL}")
            print(f"\n{Fore.BLUE}Aliases para proyecto actual:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  git new-feature \"descripción\"{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  git new-fix \"descripción\"{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  git new-hotfix \"descripción\"{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  git branch-status{Style.RESET_ALL}")
            print(f"\n{Fore.BLUE}Aliases para proyectos específicos:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  git new-feature-in /path/to/project \"descripción\"{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  git new-fix-in ../mi-proyecto \"descripción\"{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  git branch-status-in /path/to/project{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  Solo {success_count}/{len(aliases)} aliases se instalaron correctamente{Style.RESET_ALL}")
            return False

    @classmethod
    def uninstall_aliases(cls) -> bool:
        """Desinstala los aliases del sistema."""
        aliases = [
            # Aliases de creación de ramas
            'new-feature', 'new-fix', 'new-hotfix', 'new-docs',
            'new-refactor', 'new-test', 'new-chore', 'branch-status',
            # Aliases de estado
            'state', 'merged-d', 'deleted-d', 'merged-r', 'merged-rd',
            # Aliases de sincronización
            'branch-sync', 'branch-sync-in',
            # Aliases multi-proyecto
            'new-feature-in', 'new-fix-in', 'branch-status-in'
        ]

        print(f"{Fore.CYAN}🗑️  Desinstalando aliases...{Style.RESET_ALL}")

        success_count = 0
        for alias_name in aliases:
            try:
                result = subprocess.run([
                    'git', 'config', '--global', '--unset', f'alias.{alias_name}'
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"{Fore.GREEN}  ✅ {alias_name} removido{Style.RESET_ALL}")
                    success_count += 1
                else:
                    print(f"{Fore.YELLOW}  ⚠️  {alias_name} no encontrado{Style.RESET_ALL}")
                    success_count += 1  # No es error si no existe
            except Exception as e:
                print(f"{Fore.RED}  ❌ Error removiendo {alias_name}: {e}{Style.RESET_ALL}")

        print(f"{Fore.GREEN}✅ Desinstalación completada{Style.RESET_ALL}")
        return True

    @staticmethod
    def get_script_path() -> Path:
        """Obtiene la ruta absoluta del script actual."""
        return Path(__file__).absolute()

    @staticmethod
    def check_aliases_installed() -> bool:
        """Verifica si los aliases están instalados."""
        try:
            result = subprocess.run([
                'git', 'config', '--global', '--get-regexp', 'alias.new-'
            ], capture_output=True, text=True)
            return len(result.stdout.strip()) > 0
        except:
            return False

    @staticmethod
    def backup_git_config() -> bool:
        """Crea backup de la configuración de Git."""
        try:
            config_path = Path.home() / '.gitconfig'
            backup_path = Path.home() / '.gitconfig.backup'

            if config_path.exists():
                shutil.copy2(config_path, backup_path)
                print(f"{Fore.GREEN}✅ Backup creado: {backup_path}{Style.RESET_ALL}")
                return True
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error creando backup: {e}{Style.RESET_ALL}")
            return False

def show_status(repo_path: Path = None):
    """Muestra el estado actual del repositorio y contexto."""
    try:
        git_repo = GitRepository(repo_path)
        context_detector = ContextDetector(git_repo)

        context = context_detector.detect_context()
        context_info = context_detector.get_context_info(context)
        current_branch = git_repo.get_current_branch()
        branch_info = git_repo.get_branch_info(current_branch) if current_branch else None

        print(f"\n{Fore.CYAN}🔍 Estado del Repositorio{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📁 Proyecto: {Fore.YELLOW}{git_repo.repo_path}{Style.RESET_ALL}")

        if current_branch:
            print(f"{Fore.BLUE}📍 Rama actual: {Fore.YELLOW}{current_branch}{Style.RESET_ALL}")
            if branch_info:
                state_color = Fore.GREEN if branch_info["state"] == "MERGED" else Fore.YELLOW
                print(f"{Fore.BLUE}📊 Estado: {state_color}{branch_info['state']}{Style.RESET_ALL}")
                if branch_info["type"]:
                    print(f"{Fore.BLUE}🎯 Tipo: {Fore.YELLOW}{branch_info['type']}{Style.RESET_ALL}")
                if branch_info["base"]:
                    print(f"{Fore.BLUE}📌 Base: {Fore.YELLOW}{branch_info['base']}{Style.RESET_ALL}")
                if branch_info["unique_commits"] > 0:
                    print(f"{Fore.BLUE}📝 Commits únicos: {Fore.YELLOW}{branch_info['unique_commits']}{Style.RESET_ALL}")
                if branch_info["last_commit_date"]:
                    print(f"{Fore.BLUE}🕒 Último commit: {Fore.YELLOW}{branch_info['last_commit_date']}{Style.RESET_ALL}")

        print(f"{Fore.BLUE}🎯 Contexto: {Fore.YELLOW}{context}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}👥 Contribuidores: {context_info['contributors']}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📝 Commits totales: {context_info['commits']}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🔗 Remotos: {context_info['remotes']}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🤖 CI/CD: {'Sí' if context_info['has_ci'] else 'No'}{Style.RESET_ALL}")

        # Mostrar ramas protegidas
        protected = context_info['config']['protected_branches']
        print(f"{Fore.BLUE}🛡️  Ramas protegidas: {', '.join(protected)}{Style.RESET_ALL}")

        # Obtener y mostrar la configuración de commitlint
        commitlint_config_path = Path('.githooks/config/active/hooks.yaml')
        if commitlint_config_path.exists():
            try:
                # Usar ruamel.yaml si está disponible, sino el yaml estándar
                try:
                    from ruamel.yaml import YAML
                    yaml = YAML()
                except ImportError:
                    import yaml

                with open(commitlint_config_path, 'r') as f:
                    hooks_config = yaml.safe_load(f)

                commitlint_enabled = hooks_config.get('commitlint', {}).get('enabled', False)
                commitlint_strict = hooks_config.get('commitlint', {}).get('strict', False)

                print(f"{Fore.BLUE}📝 Formato de Commit: {Fore.YELLOW}Commitlint{' (Estricto)' if commitlint_strict else ' (Permisivo)' if commitlint_enabled else ' (Deshabilitado)'}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  No se pudo leer la configuración de commitlint: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Archivo de configuración de commitlint no encontrado en .githooks/config/active/hooks.yaml{Style.RESET_ALL}")

        # Verificar cambios pendientes
        if git_repo.has_uncommitted_changes():
            print(f"{Fore.YELLOW}⚠️  Hay cambios sin confirmar{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Directorio de trabajo limpio{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}❌ Error obteniendo estado: {e}{Style.RESET_ALL}")

def main():
    """Función principal del script."""
    try:
        parser = argparse.ArgumentParser(
            description="""Branch Git Helper - Sistema inteligente de gestión de branches con detección automática de contexto.

Este script proporciona una interfaz unificada para crear y gestionar branches de Git,
adaptándose automáticamente al contexto del proyecto (LOCAL, HYBRID, REMOTE).

Estados de Rama:
  - WIP (Work In Progress): Rama en desarrollo activo
  - MERGED: Rama cuyos commits han sido mergeados a su rama base
  - DELETED: Rama eliminada localmente pero mantenida en remoto como backup

Contextos:
  - LOCAL: Se detecta si:
    * No tiene remotos configurados, O
    * No tiene ni develop ni staging, O
    * Tiene menos de 2 contribuidores
  - HYBRID: Se detecta si:
    * Tiene remotos configurados, Y
    * Tiene develop o staging, Y
    * Tiene 2 o más contribuidores, Y
    * No tiene CI/CD configurado
  - REMOTE: Se detecta si:
    * Tiene remotos configurados, Y
    * Tiene develop o staging, Y
    * Tiene 2 o más contribuidores, Y
    * Tiene CI/CD configurado

Tipos de Rama:
  - feature: Nuevas características y funcionalidades
  - fix: Correcciones de errores y bugs
  - hotfix: Correcciones urgentes en producción
  - docs: Documentación y cambios en docs
  - refactor: Refactorización sin cambios funcionales
  - test: Añadir o mejorar tests
  - chore: Tareas de mantenimiento y build""",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Ejemplos de uso:
  # Creación de ramas (proyecto actual)
  %(prog)s feature "nueva-autenticacion"     # Crear rama de feature
  %(prog)s fix "corregir-validacion"         # Crear rama de fix
  %(prog)s hotfix "vulnerabilidad-critica"   # Crear rama de hotfix
  %(prog)s docs "actualizar-readme"          # Crear rama de documentación
  %(prog)s refactor "optimizar-queries"      # Crear rama de refactorización
  %(prog)s test "cobertura-api"              # Crear rama de tests
  %(prog)s chore "actualizar-deps"           # Crear rama de mantenimiento

  # Opciones para creación de ramas
  %(prog)s feature "login" --no-push         # Crear sin push automático
  %(prog)s fix "bug" --no-sync               # Crear sin sincronizar con remoto
  %(prog)s -p ../mi-proyecto feature "login" # Crear en otro proyecto

  # Gestión de estado de ramas
  %(prog)s state merged                      # Marcar rama como mergeada
  %(prog)s state deleted                     # Marcar rama como eliminada
  %(prog)s state merged -d                   # Mergear y eliminar rama
  %(prog)s state deleted -d                  # Marcar como eliminada y borrar local

  # Gestión de contexto
  %(prog)s force-context LOCAL               # Forzar contexto LOCAL
  %(prog)s force-context HYBRID              # Forzar contexto HYBRID
  %(prog)s force-context REMOTE              # Forzar contexto REMOTE
  %(prog)s force-context AUTO                # Restaurar detección automática

  # Información y estado
  %(prog)s status                            # Mostrar estado del repositorio
  %(prog)s --repo-path /path/to/repo status  # Estado de repositorio específico

  # Gestión de aliases
  %(prog)s install-aliases                   # Instalar aliases de Git persistentes
  %(prog)s uninstall-aliases                 # Remover aliases

Aliases para proyecto actual:
  git new-feature "descripción"              # Crear feature
  git new-fix "descripción"                  # Crear fix
  git new-hotfix "descripción"               # Crear hotfix
  git new-docs "descripción"                 # Crear rama de docs
  git new-refactor "descripción"             # Crear rama de refactor
  git new-test "descripción"                 # Crear rama de tests
  git new-chore "descripción"                # Crear rama de mantenimiento
  git branch-status                          # Estado del proyecto

  # Aliases para gestión de estado
  git state merged                           # Marcar rama como mergeada
  git state deleted                          # Marcar rama como eliminada
  git merged-d                              # Mergear y eliminar rama
  git deleted-d                             # Marcar como eliminada y borrar local

Aliases para proyectos específicos:
  git new-feature-in /path/to/project "desc" # Crear feature en proyecto
  git new-fix-in ../mi-proyecto "desc"       # Crear fix en proyecto
  git branch-status-in /path/to/project      # Estado de proyecto

Notas:
  - Las ramas nuevas se crean en estado WIP
  - El estado WIP se mantiene hasta que los commits se mergean
  - El contexto se detecta automáticamente según la configuración
  - Se pueden forzar contextos específicos según necesidades
  - Los aliases permiten acceso rápido desde cualquier directorio
  - El comando state permite cambiar el estado de una rama
  - La opción --delete elimina la rama después de marcar su estado
  - Los tags se propagan al remoto para mantener consistencia
  - CI/CD solo aplica en la rama main
        """)

        parser.add_argument(
            '-p', '--repo-path',
            type=Path,
            help='Ruta al repositorio Git (por defecto, el directorio actual).',
            default=Path.cwd()
        )

        subparsers = parser.add_subparsers(dest='action', help='Acciones disponibles', required=True)

        # Subparser para el comando 'state'
        state_parser = subparsers.add_parser('state', help='Gestión del estado de ramas.')
        state_parser.add_argument(
            'description',
            type=str,
            choices=['merged', 'deleted', 'wip'],
            help='Estado a establecer para la rama (merged, deleted, o wip).'
        )
        state_parser.add_argument(
            '-d', '--delete',
            action='store_true',
            help='Eliminar la rama local después de marcar su estado.'
        )

        # Subparser para el comando 'status'
        status_parser = subparsers.add_parser('status', help='Muestra el estado del repositorio y las ramas.')

        # Subparser para los comandos de creación de ramas
        for branch_type in BRANCH_TYPES.keys():
            create_parser = subparsers.add_parser(branch_type, help=f'Crear una rama de tipo {branch_type}.')
            create_parser.add_argument(
                'description',
                type=str,
                help='Descripción de la rama.'
            )
            create_parser.add_argument(
                '--no-push',
                action='store_true',
                help='No hacer push automático al remoto al crear la rama.'
            )
            create_parser.add_argument(
                '--no-sync',
                action='store_true',
                help='No sincronizar la rama base con el remoto antes de crear la rama.'
            )

        # Subparser para el comando 'force-context'
        force_context_parser = subparsers.add_parser('force-context', help='Forzar el contexto de desarrollo.')
        force_context_parser.add_argument(
            'context',
            type=str,
            choices=['LOCAL', 'HYBRID', 'REMOTE', 'AUTO'],
            help='Contexto a forzar (LOCAL, HYBRID, REMOTE, o AUTO para restaurar).'
        )

        # Subparser para el comando 'install-aliases'
        install_aliases_parser = subparsers.add_parser('install-aliases', help='Instalar aliases de Git persistentes.')

        # Subparser para el comando 'uninstall-aliases'
        uninstall_aliases_parser = subparsers.add_parser('uninstall-aliases', help='Desinstalar aliases de Git persistentes.')

        args = parser.parse_args()

        # Inicializar GitRepository y BranchHelper
        git_repo = GitRepository(args.repo_path)
        branch_helper = BranchHelper(git_repo)
        context_detector = ContextDetector(git_repo)

        if args.action == 'status':
            show_status(args.repo_path)
        elif args.action == 'state':
            # Logic for 'state' command
            current_branch = git_repo.get_current_branch()

            if not current_branch:
                print(f"{Fore.RED}❌ No se pudo determinar la rama actual{Style.RESET_ALL}")
                sys.exit(1)

            state = args.description.upper()
            options = {
                'delete': args.delete,
            }

            success = branch_helper.mark_branch_state(current_branch, state, options)
            sys.exit(0 if success else 1)
        elif args.action in BRANCH_TYPES.keys():
            # Logic for branch creation commands (feature, fix, etc.)
            options = {
                'no_push': args.no_push,
                'no_sync': args.no_sync
            }
            success = branch_helper.create_branch(args.action, args.description, options)
            sys.exit(0 if success else 1)
        elif args.action == 'force-context':
            if args.context == 'AUTO':
                context_detector.run_command(["git", "notes", "remove", "HEAD"], check=False)
                print(f"{Fore.GREEN}✅ Contexto restaurado a detección automática.{Style.RESET_ALL}")
            else:
                context_detector.force_context(args.context)
            sys.exit(0)
        elif args.action == 'install-aliases':
            success = AliasManager.install_aliases()
            sys.exit(0 if success else 1)
        elif args.action == 'uninstall-aliases':
            success = AliasManager.uninstall_aliases()
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Operación cancelada por el usuario{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}❌ Error inesperado: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
