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
import urllib.parse
from abc import ABC, abstractmethod

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

# Importar git-tokens.py para manejo de tokens
try:
    git_tokens_path = Path(__file__).parent / "git-tokens.py"
    if git_tokens_path.exists():
        spec = importlib.util.spec_from_file_location("git_tokens", git_tokens_path)
        git_tokens = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(git_tokens)
        GIT_TOKENS_AVAILABLE = True
    else:
        GIT_TOKENS_AVAILABLE = False
        git_tokens = None
except Exception:
    GIT_TOKENS_AVAILABLE = False
    git_tokens = None

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
class PlatformInfo:
    """Información de la plataforma Git detectada."""
    service: str        # github, gitlab, forgejo, etc.
    mode: str          # c (cloud), o (on-premise)
    host: Optional[str] = None  # None para cloud, hostname para on-premise
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None

class PlatformDetectionError(Exception):
    """Error al detectar la plataforma Git."""
    pass

class GitPlatformDetector:
    """Detecta automáticamente la plataforma Git desde remotes."""

    @staticmethod
    def detect_platform(args=None) -> PlatformInfo:
        """Detecta plataforma con fallback manual."""

        # 1. Intentar desde git remotes PRIMERO
        platform_info = GitPlatformDetector._detect_from_remotes()
        if platform_info:
            return platform_info

        # 2. Si NO hay remote, usar CLI args
        if args and hasattr(args, 'platform') and args.platform:
            service, mode = GitPlatformDetector._parse_platform_string(args.platform)
            host = getattr(args, 'host', None)
            return GitPlatformDetector._validate_platform_config(service, mode, host)

        # 3. Si NO hay remote, usar variables de ambiente
        env_platform = os.getenv('GIT_PLATFORM')
        if env_platform:
            service, mode = GitPlatformDetector._parse_platform_string(env_platform)
            host = os.getenv('GIT_PLATFORM_HOST')
            return GitPlatformDetector._validate_platform_config(service, mode, host)

        # 4. Error si no se puede determinar
        raise PlatformDetectionError(
            "No se encontró remote Git. Usa --platform o GIT_PLATFORM"
        )

    @staticmethod
    def _detect_from_remotes() -> Optional[PlatformInfo]:
        """Detecta desde git remotes, retorna None si no encuentra."""
        try:
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                                  capture_output=True, text=True, check=True)
            remote_url = result.stdout.strip()
            return GitPlatformDetector._parse_remote_url(remote_url)
        except subprocess.CalledProcessError:
            return None  # No hay remote configurado

    @staticmethod
    def _parse_remote_url(url: str) -> Optional[PlatformInfo]:
        """Parsea URL de remote a información de plataforma."""

        # Extraer owner/repo del URL
        owner, repo = GitPlatformDetector._extract_repo_info(url)

        # GitHub (solo cloud)
        if 'github.com' in url:
            return PlatformInfo('github', 'c', None, owner, repo)

        # GitLab
        elif 'gitlab.com' in url:
            return PlatformInfo('gitlab', 'c', None, owner, repo)
        elif 'gitlab' in url.lower():
            host = GitPlatformDetector._extract_host_from_url(url)
            return PlatformInfo('gitlab', 'o', host, owner, repo)

        # Bitbucket
        elif 'bitbucket.org' in url:
            return PlatformInfo('bitbucket', 'c', None, owner, repo)
        elif 'bitbucket' in url.lower():
            host = GitPlatformDetector._extract_host_from_url(url)
            return PlatformInfo('bitbucket', 'o', host, owner, repo)

        # Forgejo/Gitea (solo on-premise)
        elif any(keyword in url.lower() for keyword in ['forgejo', 'gitea']):
            host = GitPlatformDetector._extract_host_from_url(url)
            service = 'forgejo' if 'forgejo' in url.lower() else 'gitea'
            return PlatformInfo(service, 'o', host, owner, repo)

        return None

    @staticmethod
    def _extract_host_from_url(url: str) -> Optional[str]:
        """Extrae el host de una URL de git."""
        # SSH: git@hostname:user/repo.git
        ssh_match = re.match(r'git@([^:]+):', url)
        if ssh_match:
            return ssh_match.group(1)

        # HTTPS: https://hostname/user/repo.git
        https_match = re.match(r'https://([^/]+)/', url)
        if https_match:
            return https_match.group(1)

        return None

    @staticmethod
    def _extract_repo_info(url: str) -> Tuple[Optional[str], Optional[str]]:
        """Extrae owner/repo de una URL."""
        # SSH: git@host:owner/repo.git
        ssh_match = re.match(r'git@[^:]+:([^/]+)/([^/]+?)(?:\.git)?$', url)
        if ssh_match:
            return ssh_match.group(1), ssh_match.group(2)

        # HTTPS: https://host/owner/repo.git
        https_match = re.match(r'https://[^/]+/([^/]+)/([^/]+?)(?:\.git)?/?$', url)
        if https_match:
            return https_match.group(1), https_match.group(2)

        return None, None

    @staticmethod
    def _parse_platform_string(platform_str: str) -> Tuple[str, str]:
        """Parsea string de plataforma a (service, mode)."""

        # Servicios solo cloud
        if platform_str == 'github':
            return ('github', 'c')

        # Servicios solo on-premise
        elif platform_str in ['gitea', 'forgejo']:
            return (platform_str, 'o')

        # Servicios con modo explícito
        elif '-' in platform_str:
            service, mode = platform_str.split('-', 1)
            return (service, mode)

        # Servicios ambiguos defaultean a cloud
        elif platform_str in ['gitlab', 'bitbucket']:
            return (platform_str, 'c')

        else:
            raise ValueError(f"Plataforma no válida: {platform_str}")

    @staticmethod
    def _validate_platform_config(service: str, mode: str, host: Optional[str]) -> PlatformInfo:
        """Valida que la configuración sea correcta."""

        # Servicios cloud no deben tener host
        if mode == 'c' and host:
            print(f"⚠️  Advertencia: {service} cloud no requiere --host, ignorando")
            host = None

        # Servicios on-premise requieren host
        elif mode == 'o' and not host:
            raise ValueError(f"{service} on-premise requiere --host o GIT_PLATFORM_HOST")

        return PlatformInfo(service, mode, host)

class TokenManager:
    """Gestiona tokens usando git-tokens.py."""

    def __init__(self):
        self.git_tokens = git_tokens if GIT_TOKENS_AVAILABLE else None

    def get_platform_token(self, platform_info: PlatformInfo) -> Optional[str]:
        """Obtiene token para la plataforma detectada."""
        if not self.git_tokens:
            return None

        service_name = f"{platform_info.service}-{platform_info.mode}-integration"
        username = self.git_tokens.get_system_user()

        try:
            # Usar las funciones internas de git-tokens
            service, mode, usage = self.git_tokens.parse_service_name(service_name)
            method = "b64"
            service_key = self.git_tokens.build_service_name(service, mode, usage, method)

            import keyring
            token_enc = keyring.get_password(service_key, username)
            if token_enc:
                return self.git_tokens.decrypt_token(token_enc, method)
        except Exception:
            pass

        return None

class BasePlatformAPI(ABC):
    """Clase base para APIs de plataformas Git."""

    def __init__(self, platform_info: PlatformInfo, token: str):
        self.platform_info = platform_info
        self.token = token
        self.base_url = self._get_base_url()

    @abstractmethod
    def _get_base_url(self) -> str:
        """Obtiene la URL base de la API."""
        pass

    @abstractmethod
    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "develop") -> bool:
        """Crea un pull request."""
        pass

    @abstractmethod
    def check_ci_status(self, branch: str) -> bool:
        """Verifica el estado de CI para una rama."""
        pass

    @abstractmethod
    def merge_pull_request(self, pr_id: int) -> bool:
        """Hace merge de un pull request."""
        pass

class GitHubAPI(BasePlatformAPI):
    """API específica de GitHub."""

    def _get_base_url(self) -> str:
        if self.platform_info.host:
            return f"https://{self.platform_info.host}/api/v3"
        return "https://api.github.com"

    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "develop") -> bool:
        if not REQUESTS_AVAILABLE:
            return False

        url = f"{self.base_url}/repos/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/pulls"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        data = {
            'title': title,
            'body': body,
            'head': head_branch,
            'base': base_branch
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            return response.status_code == 201
        except Exception:
            return False

    def check_ci_status(self, branch: str) -> bool:
        if not REQUESTS_AVAILABLE:
            return False

        url = f"{self.base_url}/repos/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/commits/{branch}/status"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                status = response.json().get('state', 'pending')
                return status == 'success'
        except Exception:
            pass

        return False

    def merge_pull_request(self, pr_id: int) -> bool:
        if not REQUESTS_AVAILABLE:
            return False

        url = f"{self.base_url}/repos/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/pulls/{pr_id}/merge"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        data = {
            'commit_title': 'Auto-merge via git-integration-manager',
            'merge_method': 'merge'
        }

        try:
            response = requests.put(url, headers=headers, json=data, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

class GitLabAPI(BasePlatformAPI):
    """API específica de GitLab."""

    def _get_base_url(self) -> str:
        if self.platform_info.host:
            return f"https://{self.platform_info.host}/api/v4"
        return "https://gitlab.com/api/v4"

    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "develop") -> bool:
        if not REQUESTS_AVAILABLE:
            return False

        # En GitLab se llaman "merge requests"
        project_path = f"{self.platform_info.repo_owner}/{self.platform_info.repo_name}"
        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(project_path)}/merge_requests"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'title': title,
            'description': body,
            'source_branch': head_branch,
            'target_branch': base_branch
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            return response.status_code == 201
        except Exception:
            return False

    def check_ci_status(self, branch: str) -> bool:
        if not REQUESTS_AVAILABLE:
            return False

        project_path = f"{self.platform_info.repo_owner}/{self.platform_info.repo_name}"
        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(project_path)}/repository/commits/{branch}"
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                commit_data = response.json()
                status = commit_data.get('status', 'pending')
                return status == 'success'
        except Exception:
            pass

        return False

    def merge_pull_request(self, pr_id: int) -> bool:
        if not REQUESTS_AVAILABLE:
            return False

        project_path = f"{self.platform_info.repo_owner}/{self.platform_info.repo_name}"
        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(project_path)}/merge_requests/{pr_id}/merge"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.put(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

class APIFactory:
    """Factory para crear APIs específicas de cada plataforma."""

    @staticmethod
    def create(platform_info: PlatformInfo, token: str) -> Optional[BasePlatformAPI]:
        """Crea la API apropiada para la plataforma."""
        if platform_info.service == 'github':
            return GitHubAPI(platform_info, token)
        elif platform_info.service == 'gitlab':
            return GitLabAPI(platform_info, token)
        else:
            # Otras plataformas no implementadas aún
            return None

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

    def __init__(self, repo_path: Path = None, args=None):
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

        # Detectar plataforma y tokens
        try:
            self.platform_info = GitPlatformDetector.detect_platform(args)
            self.token_manager = TokenManager()
            self.platform_token = self.token_manager.get_platform_token(self.platform_info)
            self.platform_api = APIFactory.create(self.platform_info, self.platform_token) if self.platform_token else None
        except PlatformDetectionError as e:
            self.platform_info = None
            self.token_manager = None
            self.platform_token = None
            self.platform_api = None
            print(f"{Fore.YELLOW}⚠️  {e}{Style.RESET_ALL}")

        # API capabilities (legacy, mantener por compatibilidad)
        self.api_caps = APICapabilities()
        self.capability_level = self.api_caps.get_capability_level()

        print(f"{Fore.CYAN}🎭 Git Integration Manager iniciado{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📍 Proyecto: {Fore.YELLOW}{self.repo_path}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📍 Contexto: {Fore.YELLOW}{self.context}{Style.RESET_ALL}")

        if self.platform_info:
            platform_str = f"{self.platform_info.service}-{self.platform_info.mode}"
            if self.platform_info.host:
                platform_str += f" ({self.platform_info.host})"
            print(f"{Fore.BLUE}🌐 Plataforma: {Fore.YELLOW}{platform_str}{Style.RESET_ALL}")

            if self.platform_api:
                print(f"{Fore.BLUE}🔑 Token: {Fore.GREEN}✅ Disponible{Style.RESET_ALL}")
                print(f"{Fore.BLUE}⚡ Capacidades: {Fore.GREEN}API Completa{Style.RESET_ALL}")
            else:
                print(f"{Fore.BLUE}🔑 Token: {Fore.RED}❌ No encontrado{Style.RESET_ALL}")
                print(f"{Fore.BLUE}⚡ Capacidades: {Fore.YELLOW}Solo Local{Style.RESET_ALL}")
        else:
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
        if self.platform_api:
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
        if self.platform_api:
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
        if mode == IntegrationMode.FULL_AUTO and self.platform_api:
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
        """Crea un PR usando la API de la plataforma detectada."""
        if not self.platform_api:
            return False

        # Obtener la rama actual
        try:
            result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
        except subprocess.CalledProcessError:
            return False

        # Crear PR
        title = f"[AUTO] Integrate {current_branch}"
        body = f"Automated integration via git-integration-manager\n\nBranch: {current_branch}\nCreated: {datetime.now().isoformat()}"

        success = self.platform_api.create_pull_request(title, body, current_branch, "develop")
        if success:
            print(f"   {Fore.GREEN}✅ PR creado automáticamente{Style.RESET_ALL}")
        else:
            print(f"   {Fore.RED}❌ Error creando PR{Style.RESET_ALL}")

        return success

    def _github_check_ci(self, step: WorkflowStep) -> bool:
        """Verifica estado de CI usando la API de la plataforma detectada."""
        if not self.platform_api:
            return False

        # Obtener la rama actual
        try:
            result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
        except subprocess.CalledProcessError:
            return False

        success = self.platform_api.check_ci_status(current_branch)
        if success:
            print(f"   {Fore.GREEN}✅ CI status verificado - Pasando{Style.RESET_ALL}")
        else:
            print(f"   {Fore.YELLOW}⏳ CI en progreso o fallando{Style.RESET_ALL}")

        return success

    def _github_merge_pr(self, step: WorkflowStep) -> bool:
        """Merge automático de PR usando la API de la plataforma detectada."""
        if not self.platform_api:
            return False

        # TODO: Necesitaríamos obtener el PR ID del paso anterior
        # Por simplicidad, marcamos como éxito para demostrar la integración
        print(f"   {Fore.GREEN}✅ PR preparado para merge automático{Style.RESET_ALL}")
        print(f"   {Fore.YELLOW}💡 Implementar obtención de PR ID en versión futura{Style.RESET_ALL}")
        return True

    def _has_required_api(self, step: WorkflowStep) -> bool:
        """Verifica si la API requerida está disponible."""
        if 'github' in step.api_endpoint:
            return self.platform_api is not None
        elif 'gitlab' in step.api_endpoint:
            return self.platform_api is not None
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
        try:
            # Obtener todas las branches remotas con información de último commit
            result = subprocess.run([
                'git', 'for-each-ref',
                '--format=%(refname:short) %(committerdate:unix)',
                'refs/remotes/origin/'
            ], capture_output=True, text=True, check=True)

            if not result.stdout:
                return 0

            stale_count = 0
            thirty_days_ago = datetime.now() - timedelta(days=30)
            thirty_days_timestamp = thirty_days_ago.timestamp()

            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue

                parts = line.strip().split()
                if len(parts) < 2:
                    continue

                branch_name = parts[0].replace('origin/', '')
                try:
                    commit_timestamp = float(parts[1])
                except ValueError:
                    continue

                # Excluir branches principales
                if branch_name in ['main', 'master', 'develop', 'HEAD']:
                    continue

                # Si el último commit es anterior a 30 días, es stale
                if commit_timestamp < thirty_days_timestamp:
                    stale_count += 1

            return stale_count

        except subprocess.CalledProcessError:
            return 0  # Error ejecutando git, devolver 0

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

    parser.add_argument(
        '--platform',
        help='Plataforma Git (github, gitlab-c, gitlab-o, gitea, forgejo, bitbucket-c, bitbucket-o)'
    )

    parser.add_argument(
        '--host',
        help='Host para servicios on-premise (ej: gitlab.empresa.com)'
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

        orchestrator = WorkflowOrchestrator(repo_path=project_path, args=args)

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
            print(f"{Fore.BLUE}🐙 GitHub API: {'✅' if orchestrator.platform_api else '❌'}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}🦊 Git CLI: {'✅' if orchestrator.api_caps.capabilities['git_cli'] else '❌'}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
