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
        "protected_branches": ["main", "master"]
    },
    "HYBRID": {
        "validation_level": "moderate",
        "auto_push": True,
        "require_upstream": True,
        "protected_branches": ["main", "master", "develop"]
    },
    "REMOTE": {
        "validation_level": "strict",
        "auto_push": True,
        "require_upstream": True,
        "protected_branches": ["main", "master", "develop", "staging", "release"]
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

    def get_branch_state(self, branch_name: str = None) -> str:
        """
        Determina el estado de una rama (WIP, MERGED o DELETED).

        Args:
            branch_name: Nombre de la rama a verificar. Si es None, usa la rama actual.

        Returns:
            str: "WIP" si la rama tiene commits no mergeados o está marcada como WIP,
                 "MERGED" si todos sus commits están mergeados en la rama base,
                 "DELETED" si la rama está marcada como eliminada,
                 o None si hay error.
        """
        branch = branch_name or self.get_current_branch()
        if not branch:
            return None

        # Verificar tags primero
        success, stdout, _ = self.run_command(["git", "tag", "-l", f"deleted-{branch}"])
        if success and stdout.strip():
            return "DELETED"

        success, stdout, _ = self.run_command(["git", "tag", "-l", f"merged-{branch}"])
        if success and stdout.strip():
            return "MERGED"

        # Si no hay tags, verificar notas
        success, stdout, _ = self.run_command(["git", "notes", "show", "HEAD"])
        if success and stdout:
            for line in stdout.split('\n'):
                if line.startswith('branch_state:'):
                    forced_state = line.split(':', 1)[1].strip()
                    if forced_state in ['WIP', 'MERGED', 'DELETED']:
                        return forced_state

        # Si no hay estado forzado, verificar por commits
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

        # Verificar si hay commits únicos en la rama
        success, stdout, _ = self.run_command([
            "git", "rev-list", "--left-right", "--count",
            f"{base_branch}...{branch}"
        ])

        if not success or not stdout:
            return None

        try:
            _, unique_commits = map(int, stdout.split())
            return "WIP" if unique_commits > 0 else "MERGED"
        except (ValueError, IndexError):
            return None

    def set_branch_state(self, branch_name: str, state: str, push: bool = True) -> bool:
        """
        Establece el estado de una rama usando tags.

        Args:
            branch_name: Nombre de la rama
            state: Estado a establecer ("WIP", "MERGED", "DELETED")
            push: Si se debe hacer push de los tags al remoto

        Returns:
            bool: True si se estableció el estado correctamente
        """
        if state not in ["WIP", "MERGED", "DELETED"]:
            return False

        # Eliminar tags existentes
        for tag in [f"merged-{branch_name}", f"deleted-{branch_name}"]:
            self.run_command(["git", "tag", "-d", tag], check=False)
            if push:
                self.run_command(["git", "push", "origin", f":refs/tags/{tag}"], check=False)

        # Crear nuevo tag según el estado
        if state != "WIP":
            tag_name = f"{state.lower()}-{branch_name}"
            success, _, error = self.run_command(["git", "tag", tag_name])
            if not success:
                print(f"{Fore.YELLOW}⚠️  No se pudo crear tag {tag_name}: {error}{Style.RESET_ALL}")
                return False

            if push:
                success, _, error = self.run_command(["git", "push", "origin", tag_name])
                if not success:
                    print(f"{Fore.YELLOW}⚠️  No se pudo hacer push del tag {tag_name}: {error}{Style.RESET_ALL}")
                    return False

        return True

    def get_branch_info(self, branch_name: str = None) -> Dict:
        """
        Obtiene información detallada de una rama.

        Args:
            branch_name: Nombre de la rama. Si es None, usa la rama actual.

        Returns:
            Dict con información de la rama:
            {
                "name": str,
                "state": str,  # "WIP", "MERGED" o "DELETED"
                "type": str,   # tipo de branch (feature, fix, etc.)
                "base": str,   # rama base
                "last_commit": str,  # último commit
                "last_commit_date": str,  # fecha del último commit
                "unique_commits": int,  # número de commits únicos
                "tags": List[str]  # tags asociados a la rama
            }
        """
        branch = branch_name or self.get_current_branch()
        if not branch:
            return None

        info = {
            "name": branch,
            "state": self.get_branch_state(branch),
            "type": branch.split('/')[0] if '/' in branch else None,
            "base": None,
            "last_commit": None,
            "last_commit_date": None,
            "unique_commits": 0,
            "tags": []
        }

        # Obtener tags asociados
        success, stdout, _ = self.run_command(["git", "tag", "-l", f"*-{branch}"])
        if success and stdout:
            info["tags"] = [tag.strip() for tag in stdout.split('\n') if tag.strip()]

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

        # Establecer estado WIP usando git notes
        print(f"{Fore.CYAN}📝 Estableciendo estado WIP...{Style.RESET_ALL}")
        success, _, error = self.git_repo.run_command([
            "git", "notes", "add", "-m", "branch_state:WIP", "HEAD"
        ])
        if not success:
            print(f"{Fore.YELLOW}⚠️  No se pudo establecer estado WIP: {error}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}💡 La rama se creó pero sin estado WIP explícito{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Estado WIP establecido{Style.RESET_ALL}")

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

class AliasManager:
    """Gestor de aliases de Git."""

    @staticmethod
    def get_alias_commands() -> Dict[str, str]:
        """Retorna los comandos de alias a instalar."""
        script_path = Path(__file__).resolve()
        return {
            # Aliases para creación de ramas
            "new-feature": f"!{script_path} feature",
            "new-fix": f"!{script_path} fix",
            "new-hotfix": f"!{script_path} hotfix",
            "new-docs": f"!{script_path} docs",
            "new-refactor": f"!{script_path} refactor",
            "new-test": f"!{script_path} test",
            "new-chore": f"!{script_path} chore",
            "branch-status": f"!{script_path} status",

            # Aliases para gestión de estado
            "state": f"!{script_path} state",
            "merged-d": f"!{script_path} state merged -d",
            "deleted-d": f"!{script_path} state deleted -d",
            "merged-r": f"!{script_path} state merged -r",
            "merged-rd": f"!{script_path} state merged -r -d",

            # Aliases para sincronización
            "branch-sync": f"!{script_path} sync",
            "branch-sync-in": f"!f() {{ {script_path} -p \"$1\" sync \"$@\"; }}; f",

            # Aliases para proyectos específicos
            "new-feature-in": f"!f() {{ {script_path} -p \"$1\" feature \"$2\"; }}; f",
            "new-fix-in": f"!f() {{ {script_path} -p \"$1\" fix \"$2\"; }}; f",
            "branch-status-in": f"!f() {{ {script_path} -p \"$1\" status; }}; f"
        }

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

    @classmethod
    def install_aliases(cls) -> bool:
        """Instala aliases persistentes para el helper."""
        script_path = cls.get_script_path()

        # Aliases que usan el directorio actual de donde se ejecutan
        aliases = cls.get_alias_commands()

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
        parser = argparse.ArgumentParser(description='Herramienta de gestión de ramas Git')
        parser.add_argument('action', choices=['create', 'delete', 'list', 'cleanup', 'sync'],
                          help='Acción a realizar')
        parser.add_argument('description', nargs='?', default=None,
                          help='Descripción de la rama')
        parser.add_argument('--type', '-t', choices=list(BRANCH_TYPES.keys()),
                          help='Tipo de rama a crear')
        parser.add_argument('--delete', '-d', action='store_true',
                          help='Eliminar la rama después de la acción')
        parser.add_argument('--replace', '-r', action='store_true',
                          help='Reemplazar rama base en lugar de merge')
        parser.add_argument('--no-sync', action='store_true',
                          help='No sincronizar con remoto al crear rama')
        parser.add_argument('--dry-run', action='store_true',
                          help='Mostrar acciones sin ejecutarlas')
        parser.add_argument('--force', '-f', action='store_true',
                          help='Forzar operación sin confirmación')
        parser.add_argument('--context', choices=['LOCAL', 'HYBRID', 'REMOTE'],
                          help='Forzar contexto específico')

        args = parser.parse_args()
        git_repo = GitRepository()
        branch_helper = BranchHelper(git_repo)

        # Detectar contexto
        context_detector = ContextDetector(git_repo)
        context = args.context or context_detector.detect_context()
        context_info = context_detector.get_context_info(context)

        if args.action == 'create':
            if not args.type:
                print(f"{Fore.RED}❌ Error: Se requiere --type para crear rama{Style.RESET_ALL}")
                sys.exit(1)
            if not args.description:
                print(f"{Fore.RED}❌ Error: Se requiere descripción para crear rama{Style.RESET_ALL}")
                sys.exit(1)

            options = {
                'no_sync': args.no_sync,
                'force': args.force
            }
            if not branch_helper.create_branch(args.type, args.description, options):
                sys.exit(1)

        elif args.action == 'delete':
            current_branch = git_repo.get_current_branch()
            if not current_branch:
                print(f"{Fore.RED}❌ Error: No hay rama actual{Style.RESET_ALL}")
                sys.exit(1)

            # Verificar si la rama existe en remoto
            success, stdout, _ = git_repo.run_command(["git", "ls-remote", "--heads", "origin", current_branch])
            branch_exists_remote = success and stdout.strip()

            # Eliminar rama local
            print(f"\n{Fore.CYAN}🗑️  Eliminando rama '{current_branch}'...{Style.RESET_ALL}")
            success, _, error = git_repo.run_command(["git", "branch", "-d", current_branch])
            if success:
                print(f"{Fore.GREEN}✅ Rama eliminada exitosamente{Style.RESET_ALL}")
                # Si existe en remoto, marcarla como DELETED
                if branch_exists_remote:
                    print(f"{Fore.CYAN}📝 Marcando rama remota como DELETED...{Style.RESET_ALL}")
                    if git_repo.set_branch_state(current_branch, "DELETED"):
                        print(f"{Fore.GREEN}✅ Estado actualizado a DELETED{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️  No se pudo actualizar estado{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️  No se pudo eliminar la rama: {error}{Style.RESET_ALL}")
                if args.force:
                    print(f"{Fore.CYAN}🔄 Intentando eliminación forzada...{Style.RESET_ALL}")
                    success, _, error = git_repo.run_command(["git", "branch", "-D", current_branch])
                    if success:
                        print(f"{Fore.GREEN}✅ Rama eliminada forzadamente{Style.RESET_ALL}")
                        # Si existe en remoto, marcarla como DELETED
                        if branch_exists_remote:
                            print(f"{Fore.CYAN}📝 Marcando rama remota como DELETED...{Style.RESET_ALL}")
                            if git_repo.set_branch_state(current_branch, "DELETED"):
                                print(f"{Fore.GREEN}✅ Estado actualizado a DELETED{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.YELLOW}⚠️  No se pudo actualizar estado{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Error al eliminar forzadamente: {error}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.BLUE}   Si está seguro, puede forzar la eliminación con:{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}   git branch -D {current_branch}{Style.RESET_ALL}")

        elif args.action == 'list':
            show_status(git_repo.repo_path)
            sys.exit(0)

        elif args.action == 'cleanup':
            # Implementa la lógica para limpiar ramas no utilizadas
            print(f"{Fore.YELLOW}⚠️  La función de limpieza no está implementada{Style.RESET_ALL}")
            sys.exit(1)

        elif args.action == 'sync':
            print(f"{Fore.CYAN}🔄 Sincronizando estados de ramas...{Style.RESET_ALL}")
            actions = git_repo.sync_branch_states(dry_run=args.dry_run)

            if actions["merged"] or actions["deleted"]:
                print(f"\n{Fore.MAGENTA}📊 Resumen de acciones:{Style.RESET_ALL}")
                if actions["merged"]:
                    print(f"{Fore.GREEN}✅ Ramas marcadas como MERGED:{Style.RESET_ALL}")
                    for branch in actions["merged"]:
                        print(f"   - {branch}")
                if actions["deleted"]:
                    print(f"{Fore.YELLOW}🗑️  Ramas marcadas como DELETED:{Style.RESET_ALL}")
                    for branch in actions["deleted"]:
                        print(f"   - {branch}")

            if actions["errors"]:
                print(f"\n{Fore.RED}❌ Errores encontrados:{Style.RESET_ALL}")
                for error in actions["errors"]:
                    print(f"   - {error}")

            if not any(actions.values()):
                print(f"{Fore.BLUE}💡 No se requirieron acciones de sincronización{Style.RESET_ALL}")

        else:
            print(f"{Fore.RED}❌ Acción '{args.action}' no reconocida{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Acciones disponibles: create, delete, list, cleanup, sync{Style.RESET_ALL}")
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Operación cancelada por el usuario{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}❌ Error inesperado: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
