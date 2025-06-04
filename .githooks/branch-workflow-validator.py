#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Branch Workflow Validator - Sistema de validación contextual para operaciones de Git.

Este script valida y controla operaciones de Git (commits, pushes, merges) adaptándose
automáticamente al contexto del proyecto (LOCAL, HYBRID, REMOTE) y aplicando diferentes
niveles de validación según el entorno detectado.
"""

import argparse
import subprocess
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum

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
    """Niveles de validación disponibles."""
    PERMISSIVE = "permissive"  # Solo warnings
    MODERATE = "moderate"      # Warnings + algunos bloqueos
    STRICT = "strict"          # Validación estricta con bloqueos

class OperationType(Enum):
    """Tipos de operaciones Git que se pueden validar."""
    COMMIT = "commit"
    PUSH = "push"
    MERGE = "merge"
    BRANCH_CREATE = "branch_create"
    BRANCH_DELETE = "branch_delete"

# Configuración de validaciones por contexto
VALIDATION_CONFIGS = {
    "LOCAL": {
        "level": ValidationLevel.PERMISSIVE,
        "protected_branches": ["main", "master"],
        "require_upstream": False,
        "require_pr": False,
        "allow_direct_push_to_main": True,
        "enforce_branch_naming": False,
        "require_linear_history": False
    },
    "HYBRID": {
        "level": ValidationLevel.MODERATE,
        "protected_branches": ["main", "master", "develop"],
        "require_upstream": True,
        "require_pr": False,  # Moderado: sugerido pero no obligatorio
        "allow_direct_push_to_main": False,
        "enforce_branch_naming": True,
        "require_linear_history": False
    },
    "REMOTE": {
        "level": ValidationLevel.STRICT,
        "protected_branches": ["main", "master", "develop", "staging", "release"],
        "require_upstream": True,
        "require_pr": True,
        "allow_direct_push_to_main": False,
        "enforce_branch_naming": True,
        "require_linear_history": True
    }
}

# Patrones de naming para branches
BRANCH_NAME_PATTERNS = {
    "feature": r"^feature/[a-z0-9\-_]+$",
    "fix": r"^fix/[a-z0-9\-_]+$",
    "hotfix": r"^hotfix/[a-z0-9\-_]+$",
    "docs": r"^docs/[a-z0-9\-_]+$",
    "refactor": r"^refactor/[a-z0-9\-_]+$",
    "test": r"^test/[a-z0-9\-_]+$",
    "chore": r"^chore/[a-z0-9\-_]+$",
    "release": r"^release/v?\d+\.\d+\.\d+$",
    "main_branches": r"^(main|master|develop|staging)$"
}

class GitRepository:
    """Clase para interactuar con el repositorio Git (reutilizada del helper)."""

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self._validate_git_repo()

    def _validate_git_repo(self):
        """Valida que estemos en un repositorio Git válido."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise Exception(f"No se encontró un repositorio Git en '{self.repo_path}'")

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

    def has_upstream_tracking(self, branch_name: str = None) -> bool:
        """Verifica si una rama tiene upstream tracking configurado."""
        branch = branch_name or self.get_current_branch()
        if not branch:
            return False

        success, stdout, _ = self.run_command([
            "git", "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"
        ], check=False)
        return success

    def get_conflicting_files(self) -> List[str]:
        """Obtiene lista de archivos con conflictos de merge."""
        success, stdout, _ = self.run_command(["git", "diff", "--name-only", "--diff-filter=U"])
        return stdout.split('\n') if success and stdout else []

    def is_branch_ahead_of(self, branch1: str, branch2: str) -> bool:
        """Verifica si branch1 está adelante de branch2."""
        success, stdout, _ = self.run_command([
            "git", "rev-list", "--count", f"{branch2}..{branch1}"
        ], check=False)
        try:
            return int(stdout) > 0 if success else False
        except ValueError:
            return False

class ContextDetector:
    """Detector automático de contexto de desarrollo (reutilizado del helper)."""

    def __init__(self, git_repo: GitRepository):
        self.git_repo = git_repo

    def detect_context(self) -> str:
        """Detecta automáticamente el contexto de desarrollo."""
        contributors = self.git_repo.get_contributor_count()
        commits = self.git_repo.get_commit_count()
        remotes = self.git_repo.get_remote_count()
        has_ci = self.git_repo.detect_ci_presence()
        has_develop = self.git_repo.branch_exists("develop")
        has_staging = self.git_repo.branch_exists("staging")

        # Es LOCAL si cumple cualquiera de estas condiciones:
        # 1. No tiene remotos
        # 2. No tiene ni develop ni staging
        # 3. Tiene menos de 2 contribuidores
        if (remotes == 0 or
            (not has_develop and not has_staging) or
            contributors < 2):
            return "LOCAL"

        # Si no es LOCAL, determinar entre HYBRID y REMOTE
        if has_ci or contributors > 2:  # Más de 2 contribuidores o tiene CI
            return "REMOTE"
        else:
            return "HYBRID"

class ValidationResult:
    """Resultado de una validación."""

    def __init__(self, success: bool, message: str, level: str = "info"):
        self.success = success
        self.message = message
        self.level = level  # info, warning, error

    def __str__(self):
        colors = {
            "info": Fore.BLUE,
            "warning": Fore.YELLOW,
            "error": Fore.RED
        }
        icons = {
            "info": "ℹ️ ",
            "warning": "⚠️ ",
            "error": "❌"
        }

        color = colors.get(self.level, Fore.WHITE)
        icon = icons.get(self.level, "")

        return f"{color}{icon} {self.message}{Style.RESET_ALL}"

class BranchValidator:
    """Validador principal de operaciones de branches."""

    def __init__(self, git_repo: GitRepository):
        self.git_repo = git_repo
        self.context_detector = ContextDetector(git_repo)
        self.context = self.context_detector.detect_context()
        self.config = VALIDATION_CONFIGS[self.context]

    def validate_branch_name(self, branch_name: str) -> ValidationResult:
        """Valida el formato del nombre de una rama."""
        if not self.config["enforce_branch_naming"]:
            return ValidationResult(True, f"Validación de nombres deshabilitada en contexto {self.context}")

        # Verificar si es una rama principal válida
        if re.match(BRANCH_NAME_PATTERNS["main_branches"], branch_name):
            return ValidationResult(True, f"Rama principal válida: {branch_name}")

        # Verificar patrones por tipo
        for branch_type, pattern in BRANCH_NAME_PATTERNS.items():
            if branch_type == "main_branches":
                continue
            if re.match(pattern, branch_name):
                return ValidationResult(True, f"Nombre válido para rama {branch_type}: {branch_name}")

        # Si no coincide con ningún patrón
        expected_formats = [
            "feature/descripcion", "fix/descripcion", "hotfix/descripcion",
            "docs/descripcion", "refactor/descripcion", "test/descripcion",
            "chore/descripcion", "release/v1.0.0"
        ]

        message = (f"Nombre de rama '{branch_name}' no sigue las convenciones.\n"
                  f"Formatos esperados: {', '.join(expected_formats)}")

        if self.config["level"] == ValidationLevel.STRICT:
            return ValidationResult(False, message, "error")
        else:
            return ValidationResult(True, message, "warning")

    def validate_protected_branch_operation(self, operation: OperationType, branch_name: str) -> ValidationResult:
        """Valida operaciones en ramas protegidas."""
        protected_branches = self.config["protected_branches"]

        if branch_name not in protected_branches:
            return ValidationResult(True, f"Rama '{branch_name}' no está protegida")

        # Validaciones específicas por operación
        if operation == OperationType.PUSH:
            if not self.config["allow_direct_push_to_main"]:
                message = f"Push directo a rama protegida '{branch_name}' no permitido. Usar Pull Request."

                if self.config["level"] == ValidationLevel.STRICT:
                    return ValidationResult(False, message, "error")
                else:
                    return ValidationResult(True, message, "warning")

        elif operation == OperationType.BRANCH_DELETE:
            message = f"Eliminación de rama protegida '{branch_name}' no permitida."
            return ValidationResult(False, message, "error")

        return ValidationResult(True, f"Operación {operation.value} permitida en '{branch_name}'")

    def validate_upstream_tracking(self, branch_name: str = None) -> ValidationResult:
        """Valida que la rama tenga upstream tracking configurado."""
        if not self.config["require_upstream"]:
            return ValidationResult(True, "Upstream tracking no requerido en este contexto")

        branch = branch_name or self.git_repo.get_current_branch()
        if not branch:
            return ValidationResult(False, "No se pudo determinar la rama actual", "error")

        if self.git_repo.has_upstream_tracking(branch):
            return ValidationResult(True, f"Rama '{branch}' tiene upstream tracking configurado")
        else:
            message = f"Rama '{branch}' no tiene upstream tracking. Usar: git push -u origin {branch}"

            if self.config["level"] == ValidationLevel.STRICT:
                return ValidationResult(False, message, "error")
            else:
                return ValidationResult(True, message, "warning")

    def validate_branch_source(self, branch_name: str) -> ValidationResult:
        """Valida que la rama se haya creado desde la rama base correcta."""
        # Detectar tipo de rama
        branch_type = None
        for btype in ["feature", "fix", "hotfix", "docs", "refactor", "test", "chore"]:
            if branch_name.startswith(f"{btype}/"):
                branch_type = btype
                break

        if not branch_type:
            return ValidationResult(True, f"Tipo de rama no reconocido para '{branch_name}'", "info")

        # Definir ramas base esperadas por tipo
        expected_base = {
            "hotfix": ["main", "master"],
            "feature": ["develop", "main"],
            "fix": ["develop", "main"],
            "docs": ["develop", "main"],
            "refactor": ["develop", "main"],
            "test": ["develop", "main"],
            "chore": ["develop", "main"]
        }

        expected_bases = expected_base.get(branch_type, ["develop", "main"])

        # Verificar desde qué rama se creó (usando merge-base)
        for base in expected_bases:
            if not self.git_repo.branch_exists(base):
                continue

            # Verificar si la rama actual es descendiente de la base
            success, stdout, _ = self.git_repo.run_command([
                "git", "merge-base", "--is-ancestor", base, branch_name
            ], check=False)

            if success:
                return ValidationResult(True, f"Rama '{branch_name}' creada correctamente desde '{base}'")

        message = f"Rama '{branch_name}' debería crearse desde: {' o '.join(expected_bases)}"

        if self.config["level"] == ValidationLevel.STRICT:
            return ValidationResult(False, message, "error")
        else:
            return ValidationResult(True, message, "warning")

    def validate_merge_conflicts(self) -> ValidationResult:
        """Valida que no haya conflictos de merge pendientes."""
        conflicting_files = self.git_repo.get_conflicting_files()

        if not conflicting_files:
            return ValidationResult(True, "No hay conflictos de merge pendientes")

        message = f"Conflictos de merge detectados en: {', '.join(conflicting_files)}"
        return ValidationResult(False, message, "error")

    def validate_pr_requirement(self, target_branch: str) -> ValidationResult:
        """Valida si se requiere Pull Request para la operación."""
        if not self.config["require_pr"]:
            return ValidationResult(True, "Pull Request no requerido en este contexto")

        if target_branch in self.config["protected_branches"]:
            message = f"Se requiere Pull Request para cambios en '{target_branch}'"

            if self.config["level"] == ValidationLevel.STRICT:
                return ValidationResult(False, message, "error")
            else:
                return ValidationResult(True, message, "warning")

        return ValidationResult(True, f"Pull Request no requerido para '{target_branch}'")

    def validate_gpg_verification(self) -> ValidationResult:
        """Valida la configuración GPG para commits firmados."""
        if not self.config.get('require_gpg_verification', False):
            return ValidationResult(True, "Verificación GPG no requerida en este nivel")

        try:
            # Verificar configuración local de commit.gpgsign
            success, stdout, stderr = self.git_repo.run_command(
                ['git', 'config', '--local', 'commit.gpgsign'],
                check=False
            )

            if not success or stdout.strip() != 'true':
                return ValidationResult(
                    False,
                    "❌ Verificación GPG falló: commit.gpgsign debe estar configurado como 'true' localmente",
                    "error"
                )

            return ValidationResult(
                True,
                "✅ Verificación GPG: commit.gpgsign está configurado correctamente"
            )
        except Exception as e:
            return ValidationResult(
                False,
                f"❌ Error en verificación GPG: {str(e)}",
                "error"
            )

    def run_validation_suite(self, operation: OperationType, **kwargs) -> List[ValidationResult]:
        """Ejecuta suite completa de validaciones según la operación."""
        results = []
        current_branch = self.git_repo.get_current_branch()

        # Información de contexto
        results.append(ValidationResult(
            True,
            f"Contexto detectado: {self.context} (nivel: {self.config['level'].value})",
            "info"
        ))

        if operation == OperationType.COMMIT:
            # Validaciones para commits
            if current_branch:
                results.append(self.validate_branch_name(current_branch))
                results.append(self.validate_branch_source(current_branch))
            results.append(self.validate_merge_conflicts())
            # Agregar validación GPG
            results.append(self.validate_gpg_verification())

        elif operation == OperationType.PUSH:
            target_branch = kwargs.get("target_branch", current_branch)
            if target_branch:
                results.append(self.validate_branch_name(target_branch))
                results.append(self.validate_protected_branch_operation(operation, target_branch))
                results.append(self.validate_upstream_tracking(target_branch))
                results.append(self.validate_pr_requirement(target_branch))

        elif operation == OperationType.BRANCH_CREATE:
            branch_name = kwargs.get("branch_name")
            if branch_name:
                results.append(self.validate_branch_name(branch_name))

        elif operation == OperationType.BRANCH_DELETE:
            branch_name = kwargs.get("branch_name")
            if branch_name:
                results.append(self.validate_protected_branch_operation(operation, branch_name))

        return results

def show_validation_results(results: List[ValidationResult]) -> bool:
    """Muestra los resultados de validación y retorna si todas pasaron."""
    print(f"\n{Fore.CYAN}🔍 Resultados de Validación{Style.RESET_ALL}")

    all_passed = True
    errors = []
    warnings = []

    for result in results:
        print(f"  {result}")

        if not result.success:
            all_passed = False
            errors.append(result.message)
        elif result.level == "warning":
            warnings.append(result.message)

    # Resumen
    if errors:
        print(f"\n{Fore.RED}❌ {len(errors)} error(es) encontrado(s){Style.RESET_ALL}")

    if warnings:
        print(f"\n{Fore.YELLOW}⚠️  {len(warnings)} advertencia(s){Style.RESET_ALL}")

    if all_passed and not warnings:
        print(f"\n{Fore.GREEN}✅ Todas las validaciones pasaron exitosamente{Style.RESET_ALL}")

    return all_passed

def main():
    """Función principal del validador."""
    parser = argparse.ArgumentParser(
        description="Branch Workflow Validator - Validación contextual de operaciones Git",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s commit                           # Validar antes de commit
  %(prog)s push                            # Validar antes de push
  %(prog)s push --target-branch main       # Validar push a rama específica
  %(prog)s branch-create --name feature/new # Validar creación de rama
  %(prog)s status                          # Mostrar estado de validación
        """
    )

    parser.add_argument(
        'operation',
        choices=['commit', 'push', 'merge', 'branch-create', 'branch-delete', 'status'],
        help='Tipo de operación a validar'
    )

    parser.add_argument(
        '--target-branch',
        help='Rama destino para operaciones push/merge'
    )

    parser.add_argument(
        '--branch-name',
        help='Nombre de rama para operaciones de creación/eliminación'
    )

    parser.add_argument(
        '--repo-path',
        type=Path,
        default=Path.cwd(),
        help='Ruta del repositorio Git (por defecto: directorio actual)'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Forzar validación estricta independientemente del contexto'
    )

    args = parser.parse_args()

    try:
        git_repo = GitRepository(args.repo_path)
        validator = BranchValidator(git_repo)

        # Override nivel si se especifica strict
        if args.strict:
            validator.config["level"] = ValidationLevel.STRICT

        # Comando status especial
        if args.operation == 'status':
            print(f"\n{Fore.CYAN}🔍 Estado del Validador de Workflow{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📍 Contexto: {Fore.YELLOW}{validator.context}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}⚖️  Nivel de validación: {Fore.YELLOW}{validator.config['level'].value}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}🛡️  Ramas protegidas: {', '.join(validator.config['protected_branches'])}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}🔗 Require upstream: {'Sí' if validator.config['require_upstream'] else 'No'}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📋 Require PR: {'Sí' if validator.config['require_pr'] else 'No'}{Style.RESET_ALL}")
            return

        # Mapear operaciones
        operation_map = {
            'commit': OperationType.COMMIT,
            'push': OperationType.PUSH,
            'merge': OperationType.MERGE,
            'branch-create': OperationType.BRANCH_CREATE,
            'branch-delete': OperationType.BRANCH_DELETE
        }

        operation = operation_map[args.operation]

        # Preparar kwargs para validación
        kwargs = {}
        if args.target_branch:
            kwargs['target_branch'] = args.target_branch
        if args.branch_name:
            kwargs['branch_name'] = args.branch_name

        # Ejecutar validaciones
        results = validator.run_validation_suite(operation, **kwargs)

        # Mostrar resultados
        all_passed = show_validation_results(results)

        # Exit code
        sys.exit(0 if all_passed else 1)

    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
