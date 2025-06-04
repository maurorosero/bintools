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
        Determina el estado de una rama (WIP o MERGED).

        Args:
            branch_name: Nombre de la rama a verificar. Si es None, usa la rama actual.

        Returns:
            str: "WIP" si la rama tiene commits no mergeados o está marcada como WIP,
                 "MERGED" si todos sus commits están mergeados en la rama base,
                 o None si hay error.
        """
        branch = branch_name or self.get_current_branch()
        if not branch:
            return None

        # Primero verificar si hay un estado forzado en las notas
        success, stdout, _ = self.run_command(["git", "notes", "show", "HEAD"])
        if success and stdout:
            for line in stdout.split('\n'):
                if line.startswith('branch_state:'):
                    forced_state = line.split(':', 1)[1].strip()
                    if forced_state in ['WIP', 'MERGED']:
                        return forced_state

        # Si no hay estado forzado, verificar por commits
        # Obtener la rama base según el tipo de branch
        branch_type = branch.split('/')[0] if '/' in branch else None
        base_branch = None

        if branch_type in BRANCH_TYPES:
            for base in BRANCH_TYPES[branch_type]["base_branch_priority"]:
                if self.branch_exists(base):
                    base_branch = base
                    break

        # Si no se encontró rama base, usar main/master
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
            # El formato es "X Y" donde X son commits en base_branch que no están en branch
            # y Y son commits en branch que no están en base_branch
            _, unique_commits = map(int, stdout.split())
            return "WIP" if unique_commits > 0 else "MERGED"
        except (ValueError, IndexError):
            return None

    def get_branch_info(self, branch_name: str = None) -> Dict:
        """
        Obtiene información detallada de una rama.

        Args:
            branch_name: Nombre de la rama. Si es None, usa la rama actual.

        Returns:
            Dict con información de la rama:
            {
                "name": str,
                "state": str,  # "WIP" o "MERGED"
                "type": str,   # tipo de branch (feature, fix, etc.)
                "base": str,   # rama base
                "last_commit": str,  # último commit
                "last_commit_date": str,  # fecha del último commit
                "unique_commits": int  # número de commits únicos
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
            "unique_commits": 0
        }

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
    """Gestor de aliases persistentes de Git."""

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
            'state': f'!python {script_path} state',
            'merged': f'!python {script_path} state merged',
            'merged-d': f'!python {script_path} state merged -d',
            'merged-r': f'!python {script_path} state merged -r',
            'merged-rd': f'!python {script_path} state merged -r -d',
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
            'state', 'merged', 'merged-d', 'merged-r', 'merged-rd',
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
    parser = argparse.ArgumentParser(
        description="""Branch Git Helper - Sistema inteligente de gestión de branches con detección automática de contexto.

Este script proporciona una interfaz unificada para crear y gestionar branches de Git,
adaptándose automáticamente al contexto del proyecto (LOCAL, HYBRID, REMOTE).

Estados de Rama:
  - WIP (Work In Progress): Rama en desarrollo activo
  - MERGED: Rama cuyos commits han sido mergeados a su rama base

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
  %(prog)s state merged -d                   # Mergear y eliminar rama
  %(prog)s state merged -r                   # Reemplazar rama base (solo LOCAL)
  %(prog)s state merged -r -d                # Reemplazar y eliminar rama

  # Gestión de contexto
  %(prog)s force-context LOCAL               # Forzar contexto LOCAL
  %(prog)s force-context HYBRID              # Forzar contexto HYBRID
  %(prog)s force-context REMOTE              # Forzar contexto REMOTE
  %(prog)s force-context AUTO                # Restaurar detección automática

  # Información y estado
  %(prog)s status                            # Mostrar estado del repositorio
  %(prog)s --repo-path /path/to/repo status  # Estado de repositorio específico

  # Gestión de aliases
  %(prog)s install-aliases                   # Instalar aliases persistentes
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
  git merged-d                              # Mergear y eliminar rama
  git merged-r                              # Reemplazar rama base (solo LOCAL)
  git merged-rd                             # Reemplazar y eliminar rama

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
  - El comando state permite cambiar el estado de una rama a MERGED
  - La opción --replace solo está disponible en contexto LOCAL
  - La opción --replace no se puede usar con ramas hotfix
  - La opción --delete elimina la rama después de un merge exitoso
        """)

    parser.add_argument(
        'action',
        choices=['status', 'force-context', 'state', 'help', 'install-aliases', 'uninstall-aliases'] + list(BRANCH_TYPES.keys()),
        help='Acción a realizar o tipo de branch a crear'
    )

    parser.add_argument(
        'description',
        nargs='?',
        help='Descripción de la rama (requerido para tipos de branch) o estado (merged/wip) para el comando state'
    )

    parser.add_argument(
        '--no-push',
        action='store_true',
        help='No hacer push automático al remoto (útil para desarrollo local)'
    )

    parser.add_argument(
        '--no-sync',
        action='store_true',
        help='No sincronizar con remoto antes de crear rama (útil para conexión lenta)'
    )

    parser.add_argument(
        '-p', '--repo-path',
        type=Path,
        default=Path.cwd(),
        help='Ruta del repositorio Git (por defecto: directorio actual)'
    )

    parser.add_argument(
        '-d', '--delete',
        action='store_true',
        help='Eliminar la rama de trabajo después de un merge exitoso'
    )

    parser.add_argument(
        '-r', '--replace',
        action='store_true',
        help='Reemplazar completamente la rama base con la rama de trabajo (solo en contexto LOCAL, no aplica para hotfix)'
    )

    args = parser.parse_args()

    # Comandos especiales
    if args.action == 'status':
        show_status(args.repo_path)
        return

    if args.action == 'install-aliases':
        success = AliasManager.install_aliases()
        sys.exit(0 if success else 1)

    if args.action == 'uninstall-aliases':
        success = AliasManager.uninstall_aliases()
        sys.exit(0 if success else 1)

    if args.action == 'state':
        if not args.description or args.description not in ['merged', 'wip']:
            print(f"{Fore.RED}❌ Estado inválido. Use: merged o wip{Style.RESET_ALL}")
            sys.exit(1)

        try:
            git_repo = GitRepository(args.repo_path)
            current_branch = git_repo.get_current_branch()

            if not current_branch:
                print(f"{Fore.RED}❌ No se pudo determinar la rama actual{Style.RESET_ALL}")
                sys.exit(1)

            # Verificar que no estamos en una rama protegida
            branch_type = current_branch.split('/')[0] if '/' in current_branch else None
            if not branch_type or branch_type not in BRANCH_TYPES:
                print(f"{Fore.RED}❌ No se puede cambiar estado de ramas sin tipo (main, master, etc){Style.RESET_ALL}")
                sys.exit(1)

            # Verificar contexto LOCAL para --replace
            if args.replace:
                context_detector = ContextDetector(git_repo)
                context = context_detector.detect_context()
                if context != "LOCAL":
                    print(f"{Fore.RED}❌ El modificador --replace solo está disponible en contexto LOCAL{Style.RESET_ALL}")
                    sys.exit(1)

                # Verificar que --replace no se use con hotfix
                if branch_type == 'hotfix':
                    print(f"{Fore.RED}❌ El modificador --replace no puede usarse con ramas hotfix{Style.RESET_ALL}")
                    sys.exit(1)

            # Obtener rama base según el tipo
            base_branch = None
            for base in BRANCH_TYPES[branch_type]["base_branch_priority"]:
                if git_repo.branch_exists(base):
                    base_branch = base
                    break

            if not base_branch:
                print(f"{Fore.RED}❌ No se encontró rama base para {branch_type}{Style.RESET_ALL}")
                sys.exit(1)

            if args.description == 'merged':
                # Guardar nombre de la rama actual para posible eliminación
                working_branch = current_branch

                # Cambiar a rama base
                print(f"{Fore.CYAN}🔄 Cambiando a rama base '{base_branch}'...{Style.RESET_ALL}")
                success, _, error = git_repo.run_command(["git", "checkout", base_branch])
                if not success:
                    print(f"{Fore.RED}❌ Error al cambiar a rama base: {error}{Style.RESET_ALL}")
                    sys.exit(1)

                if args.replace:
                    # Verificar que no hay cambios sin commitear en la rama base
                    success, output, _ = git_repo.run_command(["git", "status", "--porcelain"])
                    if output.strip():
                        print(f"{Fore.RED}❌ Hay cambios sin commitear en {base_branch}. Por favor, haga commit o stash de los cambios antes de usar --replace{Style.RESET_ALL}")
                        sys.exit(1)

                    # Hacer reset hard a la rama de trabajo
                    print(f"{Fore.CYAN}🔄 Reemplazando '{base_branch}' con '{working_branch}'...{Style.RESET_ALL}")
                    success, _, error = git_repo.run_command(["git", "reset", "--hard", working_branch])
                    if not success:
                        print(f"{Fore.RED}❌ Error al reemplazar rama: {error}{Style.RESET_ALL}")
                        sys.exit(1)

                    print(f"{Fore.GREEN}✅ Rama {base_branch} reemplazada exitosamente con {working_branch}{Style.RESET_ALL}")
                else:
                    # Hacer merge normal
                    print(f"{Fore.CYAN}🔄 Haciendo merge de '{working_branch}' a '{base_branch}'...{Style.RESET_ALL}")
                    success, _, error = git_repo.run_command(["git", "merge", working_branch])
                    if not success:
                        print(f"{Fore.YELLOW}⚠️  Conflictos detectados. Resuelva los conflictos y luego:{Style.RESET_ALL}")
                        print(f"{Fore.BLUE}   git add .{Style.RESET_ALL}")
                        print(f"{Fore.BLUE}   git commit -m \"Merge {working_branch} a {base_branch}\"{Style.RESET_ALL}")
                        sys.exit(1)

                # Actualizar estado usando git notes
                print(f"{Fore.CYAN}📝 Actualizando estado a MERGED...{Style.RESET_ALL}")
                success, _, error = git_repo.run_command([
                    "git", "notes", "add", "-m", "branch_state:MERGED", "HEAD"
                ])
                if not success:
                    print(f"{Fore.YELLOW}⚠️  No se pudo actualizar estado: {error}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ Estado actualizado a MERGED{Style.RESET_ALL}")

                # Mostrar resumen
                print(f"\n{Fore.MAGENTA}🎉 {'Reemplazo' if args.replace else 'Merge'} completado{Style.RESET_ALL}")
                print(f"{Fore.BLUE}📝 Rama: {working_branch}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}📌 Base: {base_branch}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}📊 Estado: {Fore.GREEN}MERGED{Style.RESET_ALL}")

                # Eliminar rama si se solicitó y la operación fue exitosa
                if args.delete:
                    print(f"\n{Fore.CYAN}🗑️  Eliminando rama '{working_branch}'...{Style.RESET_ALL}")
                    success, _, error = git_repo.run_command(["git", "branch", "-d", working_branch])
                    if success:
                        print(f"{Fore.GREEN}✅ Rama eliminada exitosamente{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️  No se pudo eliminar la rama: {error}{Style.RESET_ALL}")
                        print(f"{Fore.BLUE}   Si está seguro, puede forzar la eliminación con:{Style.RESET_ALL}")
                        print(f"{Fore.BLUE}   git branch -D {working_branch}{Style.RESET_ALL}")

            # TODO: Implementar cambio a WIP si se necesita

            sys.exit(0)

        except Exception as e:
            print(f"{Fore.RED}❌ Error inesperado: {e}{Style.RESET_ALL}")
            sys.exit(1)

    if args.action == 'force-context':
        if not args.description or args.description not in ['LOCAL', 'HYBRID', 'REMOTE', 'AUTO']:
            print(f"{Fore.RED}❌ Contexto inválido. Use: LOCAL, HYBRID, REMOTE, o AUTO{Style.RESET_ALL}")
            sys.exit(1)

        try:
            git_repo = GitRepository(args.repo_path)
            if args.description == 'AUTO':
                # Eliminar la nota de contexto forzado si existe
                success, _, error = git_repo.run_command(["git", "notes", "remove", "HEAD"])
                if success:
                    print(f"{Fore.GREEN}✅ Contexto restaurado a detección automática{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}ℹ️  No había contexto forzado que eliminar{Style.RESET_ALL}")
            else:
                # Guardar el contexto forzado en una nota de Git
                success, _, error = git_repo.run_command(
                    ["git", "notes", "add", "-m", f"forced_context:{args.description}", "HEAD"]
                )
                if success:
                    print(f"{Fore.GREEN}✅ Contexto forzado a {args.description}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Error al forzar contexto: {error}{Style.RESET_ALL}")

            # Mostrar el nuevo estado
            show_status(args.repo_path)
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"{Fore.RED}❌ Error inesperado: {e}{Style.RESET_ALL}")
            sys.exit(1)

    # Crear rama
    if args.action in BRANCH_TYPES:
        if not args.description:
            print(f"{Fore.RED}❌ Se requiere una descripción para crear una rama de tipo '{args.action}'{Style.RESET_ALL}")
            parser.print_help()
            sys.exit(1)

        try:
            git_repo = GitRepository(args.repo_path)
            branch_helper = BranchHelper(git_repo)

            options = {
                'no_push': args.no_push,
                'no_sync': args.no_sync
            }

            success = branch_helper.create_branch(args.action, args.description, options)
            sys.exit(0 if success else 1)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  Operación cancelada por el usuario{Style.RESET_ALL}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}❌ Error inesperado: {e}{Style.RESET_ALL}")
            sys.exit(1)
    else:
        print(f"{Fore.RED}❌ Acción '{args.action}' no reconocida{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Acciones disponibles: {', '.join(list(BRANCH_TYPES.keys()) + ['status', 'install-aliases', 'uninstall-aliases'])}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
