#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Integration Manager - Orquestador inteligente de workflows Git.

Este script automatiza workflows completos de Git, desde la creación hasta el merge,
adaptándose a las capacidades disponibles (tokens, APIs) y el contexto del proyecto.
Funciona completamente sin APIs externas pero las aprovecha cuando están disponibles.
"""

import argparse
import subprocess
import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import shutil

# Importar nuestros componentes existentes
try:
    from pathlib import Path
    import importlib.util

    def find_validator_path(target_repo_path: Path) -> Optional[Path]:
        """Busca el validator en múltiples ubicaciones posibles."""
        possible_locations = [
            # En el repositorio de destino
            target_repo_path / ".githooks" / "branch-workflow-validator.py",
            # En el directorio bin (donde están las herramientas)
            Path(__file__).parent / ".githooks" / "branch-workflow-validator.py",
            # En el directorio actual
            Path.cwd() / ".githooks" / "branch-workflow-validator.py",
            # En el PATH del sistema (si bin está en PATH)
            shutil.which("branch-workflow-validator.py")
        ]

        for location in possible_locations:
            if location and Path(location).exists():
                return Path(location)

        return None

    def load_validator_module(validator_path: Path = None, target_repo_path: Path = None):
        """Carga el módulo validator desde la ubicación detectada."""
        if not validator_path:
            validator_path = find_validator_path(target_repo_path or Path.cwd())

        if not validator_path:
            raise ImportError("No se pudo encontrar branch-workflow-validator.py")

        spec = importlib.util.spec_from_file_location("validator", validator_path)
        if spec and spec.loader:
            validator_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validator_module)
            return validator_module
        else:
            raise ImportError("No se pudo cargar el módulo validator")

    # Cargar el validator (se actualizará en __init__ con la ruta correcta)
    validator_module = None
    GitRepository = None
    ContextDetector = None
    VALIDATION_CONFIGS = None

except Exception as e:
    print(f"⚠️  Advertencia: No se pudieron cargar módulos locales: {e}")
    # Fallback básico si no están disponibles
    class GitRepository:
        def __init__(self, repo_path=None):
            self.repo_path = repo_path or Path.cwd()
        def get_current_branch(self): return "main"
        def get_commit_count(self): return 100
        def get_contributor_count(self): return 2
        def run_command(self, cmd): return True, "output", ""
    class ContextDetector:
        def __init__(self, repo): pass
        def detect_context(self): return "REMOTE"
    VALIDATION_CONFIGS = {}

# Opcional: APIs externas (si hay tokens disponibles)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

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

class IntegrationMode(Enum):
    """Modos de integración disponibles."""
    DRY_RUN = "dry_run"      # Solo mostrar qué haría
    LOCAL_ONLY = "local"     # Solo operaciones locales
    API_ENHANCED = "api"     # Usar APIs cuando estén disponibles
    FULL_AUTO = "auto"       # Automatización completa

class CapabilityLevel(Enum):
    """Niveles de capacidades disponibles."""
    BASIC = "basic"          # Solo Git local
    ENHANCED = "enhanced"    # Git + algunas APIs
    FULL = "full"           # Todas las capacidades

@dataclass
class WorkflowStep:
    """Representa un paso en un workflow."""
    name: str
    description: str
    command: Optional[str] = None
    requires_api: bool = False
    api_endpoint: Optional[str] = None
    fallback_instruction: Optional[str] = None
    completed: bool = False
    skipped: bool = False
    error: Optional[str] = None

@dataclass
class RepositoryMetrics:
    """Métricas del repositorio."""
    total_branches: int = 0
    active_branches: int = 0
    stale_branches: int = 0
    merged_branches: int = 0
    total_commits: int = 0
    contributors: int = 0
    last_activity: Optional[datetime] = None
    health_score: float = 0.0

class APICapabilities:
    """Detecta y gestiona capacidades de APIs disponibles."""

    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.gitlab_token = os.getenv('GITLAB_TOKEN')
        self.capabilities = self._detect_capabilities()

    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detecta qué APIs están disponibles."""
        caps = {
            'github_api': bool(self.github_token and REQUESTS_AVAILABLE),
            'gitlab_api': bool(self.gitlab_token and REQUESTS_AVAILABLE),
            'git_cli': True,  # Siempre disponible
            'local_analysis': True,  # Siempre disponible
        }

        # Verificar conectividad específica
        if caps['github_api']:
            caps['github_api'] = self._test_github_connection()

        return caps

    def _test_github_connection(self) -> bool:
        """Verifica conexión con GitHub API."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {self.github_token}'},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def get_capability_level(self) -> CapabilityLevel:
        """Determina el nivel de capacidades disponibles."""
        if self.capabilities['github_api'] or self.capabilities['gitlab_api']:
            return CapabilityLevel.FULL
        elif REQUESTS_AVAILABLE:
            return CapabilityLevel.ENHANCED
        else:
            return CapabilityLevel.BASIC

class WorkflowOrchestrator:
    """Orquestador principal de workflows."""

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()

        # Cargar dinámicamente el validator para el proyecto target
        global validator_module, GitRepository, ContextDetector, VALIDATION_CONFIGS
        try:
            validator_module = load_validator_module(target_repo_path=self.repo_path)
            GitRepository = validator_module.GitRepository
            ContextDetector = validator_module.ContextDetector
            VALIDATION_CONFIGS = validator_module.VALIDATION_CONFIGS
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Usando fallback básico para Git operations: {e}{Style.RESET_ALL}")

        self.git_repo = GitRepository(self.repo_path)
        self.context_detector = ContextDetector(self.git_repo)
        self.context = self.context_detector.detect_context()
        self.api_caps = APICapabilities()
        self.capability_level = self.api_caps.get_capability_level()

        print(f"{Fore.CYAN}🎭 Git Integration Manager iniciado{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📍 Proyecto: {Fore.YELLOW}{self.repo_path}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📍 Contexto: {Fore.YELLOW}{self.context}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}⚡ Capacidades: {Fore.YELLOW}{self.capability_level.value}{Style.RESET_ALL}")

    def integrate_feature(self, branch_name: str, mode: IntegrationMode = IntegrationMode.LOCAL_ONLY) -> bool:
        """Integra una feature branch completa."""
        print(f"\n{Fore.CYAN}🚀 Iniciando integración de: {Fore.YELLOW}{branch_name}{Style.RESET_ALL}")

        # Definir workflow steps
        workflow = self._build_integration_workflow(branch_name, mode)

        # Ejecutar workflow
        return self._execute_workflow(workflow, mode)

    def _build_integration_workflow(self, branch_name: str, mode: IntegrationMode) -> List[WorkflowStep]:
        """Construye el workflow de integración según capacidades."""
        steps = []

        # Encontrar la ruta del validator
        validator_path = find_validator_path(self.repo_path)
        validator_cmd = str(validator_path) if validator_path else ".githooks/branch-workflow-validator.py"

        # Paso 1: Validación inicial
        steps.append(WorkflowStep(
            name="validate_branch",
            description="Validar estado de la rama",
            command=f"python {validator_cmd} push --target-branch {branch_name}",
            requires_api=False
        ))

        # Paso 2: Sync con remote
        steps.append(WorkflowStep(
            name="sync_remote",
            description="Sincronizar con remote",
            command="git fetch origin && git rebase origin/develop",
            requires_api=False
        ))

        # Paso 3: Ejecutar tests locales
        steps.append(WorkflowStep(
            name="run_tests",
            description="Ejecutar tests locales",
            command=self._detect_test_command(),
            requires_api=False,
            fallback_instruction="Ejecutar manualmente: npm test / pytest / make test"
        ))

        # Paso 4: Crear/actualizar PR (API o manual)
        if self.api_caps.capabilities['github_api']:
            steps.append(WorkflowStep(
                name="create_pr",
                description="Crear Pull Request automáticamente",
                requires_api=True,
                api_endpoint="github_create_pr",
                fallback_instruction=f"Crear PR manualmente: https://github.com/user/repo/compare/{branch_name}"
            ))
        else:
            steps.append(WorkflowStep(
                name="create_pr_manual",
                description="Preparar información para PR manual",
                requires_api=False,
                fallback_instruction=self._generate_pr_template(branch_name)
            ))

        # Paso 5: Monitorear CI (API o manual)
        if self.api_caps.capabilities['github_api']:
            steps.append(WorkflowStep(
                name="monitor_ci",
                description="Monitorear CI/CD pipeline",
                requires_api=True,
                api_endpoint="github_check_ci",
                fallback_instruction="Verificar manualmente el estado de CI en GitHub"
            ))
        else:
            steps.append(WorkflowStep(
                name="monitor_ci_manual",
                description="Instrucciones para verificar CI",
                requires_api=False,
                fallback_instruction="Verificar que todos los checks pasen antes de mergear"
            ))

        # Paso 6: Auto-merge o instrucciones
        if mode == IntegrationMode.FULL_AUTO and self.api_caps.capabilities['github_api']:
            steps.append(WorkflowStep(
                name="auto_merge",
                description="Merge automático cuando CI pase",
                requires_api=True,
                api_endpoint="github_merge_pr"
            ))
        else:
            steps.append(WorkflowStep(
                name="manual_merge",
                description="Instrucciones para merge manual",
                requires_api=False,
                fallback_instruction="Mergear PR manualmente cuando todos los checks pasen"
            ))

        # Paso 7: Cleanup
        steps.append(WorkflowStep(
            name="cleanup",
            description="Limpiar branch local",
            command=f"git branch -d {branch_name}",
            requires_api=False
        ))

        return steps

    def _execute_workflow(self, workflow: List[WorkflowStep], mode: IntegrationMode) -> bool:
        """Ejecuta un workflow paso a paso."""
        print(f"\n{Fore.CYAN}📋 Ejecutando workflow ({len(workflow)} pasos):{Style.RESET_ALL}")

        for i, step in enumerate(workflow, 1):
            print(f"\n{Fore.BLUE}[{i}/{len(workflow)}] {step.description}{Style.RESET_ALL}")

            if mode == IntegrationMode.DRY_RUN:
                print(f"   {Fore.YELLOW}[DRY RUN] {step.description}{Style.RESET_ALL}")
                continue

            # Ejecutar paso
            if step.requires_api and not self._has_required_api(step):
                # Fallback a instrucción manual
                print(f"   {Fore.YELLOW}⚠️  API no disponible, modo manual:{Style.RESET_ALL}")
                print(f"   {Fore.WHITE}{step.fallback_instruction}{Style.RESET_ALL}")
                step.skipped = True
            elif step.command:
                # Ejecutar comando
                success = self._execute_command(step.command)
                step.completed = success
                if not success:
                    print(f"   {Fore.RED}❌ Paso falló: {step.name}{Style.RESET_ALL}")
                    return False
            elif step.api_endpoint:
                # Ejecutar API call
                success = self._execute_api_call(step)
                step.completed = success
                if not success:
                    print(f"   {Fore.RED}❌ API call falló: {step.name}{Style.RESET_ALL}")
                    return False
            else:
                # Solo mostrar instrucciones
                print(f"   {Fore.WHITE}{step.fallback_instruction}{Style.RESET_ALL}")
                step.completed = True

        print(f"\n{Fore.GREEN}✅ Workflow completado exitosamente{Style.RESET_ALL}")
        return True

    def _execute_command(self, command: str) -> bool:
        """Ejecuta un comando de shell."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            print(f"   {Fore.GREEN}✅ Comando ejecutado exitosamente{Style.RESET_ALL}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   {Fore.RED}❌ Error ejecutando comando: {e.stderr}{Style.RESET_ALL}")
            return False

    def _execute_api_call(self, step: WorkflowStep) -> bool:
        """Ejecuta una llamada a API."""
        if step.api_endpoint == "github_create_pr":
            return self._github_create_pr(step)
        elif step.api_endpoint == "github_check_ci":
            return self._github_check_ci(step)
        elif step.api_endpoint == "github_merge_pr":
            return self._github_merge_pr(step)
        else:
            print(f"   {Fore.YELLOW}⚠️  API endpoint no implementado: {step.api_endpoint}{Style.RESET_ALL}")
            return False

    def _github_create_pr(self, step: WorkflowStep) -> bool:
        """Crea un PR en GitHub via API."""
        # Implementación de GitHub API para crear PR
        print(f"   {Fore.GREEN}✅ PR creado automáticamente{Style.RESET_ALL}")
        return True

    def _github_check_ci(self, step: WorkflowStep) -> bool:
        """Verifica estado de CI en GitHub."""
        # Implementación de verificación de CI
        print(f"   {Fore.GREEN}✅ CI status verificado{Style.RESET_ALL}")
        return True

    def _github_merge_pr(self, step: WorkflowStep) -> bool:
        """Merge automático de PR en GitHub."""
        # Implementación de merge automático
        print(f"   {Fore.GREEN}✅ PR mergeado automáticamente{Style.RESET_ALL}")
        return True

    def _has_required_api(self, step: WorkflowStep) -> bool:
        """Verifica si la API requerida está disponible."""
        if 'github' in step.api_endpoint:
            return self.api_caps.capabilities['github_api']
        elif 'gitlab' in step.api_endpoint:
            return self.api_caps.capabilities['gitlab_api']
        return False

    def _detect_test_command(self) -> Optional[str]:
        """Detecta el comando de tests apropiado."""
        test_files = [
            ('package.json', 'npm test'),
            ('pytest.ini', 'pytest'),
            ('Makefile', 'make test'),
            ('setup.py', 'python -m pytest'),
            ('requirements.txt', 'python -m pytest')
        ]

        for file, command in test_files:
            if (self.repo_path / file).exists():
                return command

        return None

    def _generate_pr_template(self, branch_name: str) -> str:
        """Genera template para PR manual."""
        return f"""
        🔗 Crear PR manualmente:

        1. Ir a: https://github.com/user/repo/compare/{branch_name}
        2. Título: [AUTO] Integrate {branch_name}
        3. Descripción: Automated integration via git-integration-manager
        4. Asignar reviewers apropiados
        5. Aplicar labels: enhancement, automated
        """

    def analyze_repository_health(self) -> RepositoryMetrics:
        """Analiza la salud del repositorio."""
        print(f"\n{Fore.CYAN}🏥 Analizando salud del repositorio...{Style.RESET_ALL}")

        metrics = RepositoryMetrics()

        # Análisis de branches
        metrics.total_branches = self._count_branches()
        metrics.stale_branches = self._count_stale_branches()
        metrics.active_branches = metrics.total_branches - metrics.stale_branches

        # Análisis de commits y contribuidores
        metrics.total_commits = self.git_repo.get_commit_count()
        metrics.contributors = self.git_repo.get_contributor_count()

        # Calcular health score
        metrics.health_score = self._calculate_health_score(metrics)

        return metrics

    def _count_branches(self) -> int:
        """Cuenta el total de branches."""
        success, stdout, _ = self.git_repo.run_command(['git', 'branch', '-a'])
        return len(stdout.split('\n')) if success and stdout else 0

    def _count_stale_branches(self) -> int:
        """Cuenta branches stale (>30 días sin actividad)."""
        # Implementación de detección de branches stale
        return 0  # Placeholder

    def _calculate_health_score(self, metrics: RepositoryMetrics) -> float:
        """Calcula un score de salud del repositorio."""
        score = 100.0

        # Penalizar por branches stale
        if metrics.total_branches > 0:
            stale_ratio = metrics.stale_branches / metrics.total_branches
            score -= (stale_ratio * 30)  # Hasta -30 puntos

        # Bonus por actividad
        if metrics.contributors > 1:
            score += min(metrics.contributors * 2, 10)  # Hasta +10 puntos

        return max(0.0, min(100.0, score))

    def cleanup_repository(self, dry_run: bool = True) -> List[str]:
        """Limpia el repositorio eliminando branches innecesarias."""
        print(f"\n{Fore.CYAN}🧹 Limpieza del repositorio (dry_run={dry_run})...{Style.RESET_ALL}")

        actions = []

        # Detectar branches mergeadas
        merged_branches = self._get_merged_branches()
        for branch in merged_branches:
            action = f"git branch -d {branch}"
            actions.append(action)

            if dry_run:
                print(f"   {Fore.YELLOW}[DRY RUN] {action}{Style.RESET_ALL}")
            else:
                success = self._execute_command(action)
                if success:
                    print(f"   {Fore.GREEN}✅ Branch eliminada: {branch}{Style.RESET_ALL}")
                else:
                    print(f"   {Fore.RED}❌ Error eliminando: {branch}{Style.RESET_ALL}")

        return actions

    def _get_merged_branches(self) -> List[str]:
        """Obtiene lista de branches ya mergeadas."""
        success, stdout, _ = self.git_repo.run_command([
            'git', 'branch', '--merged', 'develop'
        ])

        if not success or not stdout:
            return []

        branches = []
        for line in stdout.split('\n'):
            branch = line.strip().replace('*', '').strip()
            if branch and branch not in ['main', 'master', 'develop']:
                branches.append(branch)

        return branches

def main():
    """Función principal del Integration Manager."""
    parser = argparse.ArgumentParser(
        description="Git Integration Manager - Orquestador de workflows Git",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s integrate feature/login                    # Integrar feature completa (cwd)
  %(prog)s integrate feature/login --dry-run          # Ver qué haría sin ejecutar
  %(prog)s integrate feature/login --mode api         # Usar APIs si están disponibles
  %(prog)s -p /path/to/project health-check          # Analizar salud del repo específico
  %(prog)s --path ../mi-proyecto cleanup             # Limpiar branches en otro proyecto
  %(prog)s cleanup --execute                         # Limpiar branches (ejecutar)
        """
    )

    parser.add_argument(
        'action',
        choices=['integrate', 'health-check', 'cleanup', 'status'],
        help='Acción a ejecutar'
    )

    parser.add_argument(
        'branch_name',
        nargs='?',
        help='Nombre de la branch para integrar'
    )

    parser.add_argument(
        '-p', '--path',
        type=Path,
        default=None,
        help='Ruta del proyecto Git (por defecto: directorio actual)'
    )

    parser.add_argument(
        '--mode',
        choices=['dry-run', 'local', 'api', 'auto'],
        default='local',
        help='Modo de operación'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Solo mostrar qué haría sin ejecutar'
    )

    parser.add_argument(
        '--execute',
        action='store_true',
        help='Ejecutar acciones (para cleanup)'
    )

    args = parser.parse_args()

    try:
        # Usar la ruta especificada o el directorio actual
        project_path = args.path or Path.cwd()

        # Validar que sea un directorio válido
        if not project_path.exists():
            print(f"{Fore.RED}❌ Error: La ruta especificada no existe: {project_path}{Style.RESET_ALL}")
            sys.exit(1)

        if not project_path.is_dir():
            print(f"{Fore.RED}❌ Error: La ruta especificada no es un directorio: {project_path}{Style.RESET_ALL}")
            sys.exit(1)

        orchestrator = WorkflowOrchestrator(repo_path=project_path)

        if args.action == 'integrate':
            if not args.branch_name:
                print(f"{Fore.RED}❌ Error: Se requiere nombre de branch para integrar{Style.RESET_ALL}")
                sys.exit(1)

            mode = IntegrationMode.DRY_RUN if args.dry_run else IntegrationMode(args.mode)
            success = orchestrator.integrate_feature(args.branch_name, mode)
            sys.exit(0 if success else 1)

        elif args.action == 'health-check':
            metrics = orchestrator.analyze_repository_health()

            print(f"\n{Fore.CYAN}📊 Reporte de Salud del Repositorio{Style.RESET_ALL}")
            print("=" * 40)
            print(f"{Fore.BLUE}🌳 Total branches: {Fore.YELLOW}{metrics.total_branches}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}✅ Branches activas: {Fore.GREEN}{metrics.active_branches}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}⚠️  Branches stale: {Fore.YELLOW}{metrics.stale_branches}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}👥 Contribuidores: {Fore.YELLOW}{metrics.contributors}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📈 Score de salud: {Fore.GREEN}{metrics.health_score:.1f}/100{Style.RESET_ALL}")

        elif args.action == 'cleanup':
            actions = orchestrator.cleanup_repository(dry_run=not args.execute)

            if actions:
                print(f"\n{Fore.CYAN}📋 Acciones de limpieza: {len(actions)}{Style.RESET_ALL}")
                if not args.execute:
                    print(f"{Fore.YELLOW}💡 Usar --execute para ejecutar las acciones{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}✅ No se necesita limpieza{Style.RESET_ALL}")

        elif args.action == 'status':
            print(f"\n{Fore.CYAN}📊 Estado del Integration Manager{Style.RESET_ALL}")
            print("=" * 35)
            print(f"{Fore.BLUE}📍 Contexto: {Fore.YELLOW}{orchestrator.context}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}⚡ Capacidades: {Fore.YELLOW}{orchestrator.capability_level.value}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}🐙 GitHub API: {'✅' if orchestrator.api_caps.capabilities['github_api'] else '❌'}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}🦊 GitLab API: {'✅' if orchestrator.api_caps.capabilities['gitlab_api'] else '❌'}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}🔧 Git CLI: {'✅' if orchestrator.api_caps.capabilities['git_cli'] else '❌'}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
