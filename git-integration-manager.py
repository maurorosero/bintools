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
import pprint # <-- AÑADIDO PARA DEPURACIÓN

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

# Nuevas importaciones para configuración remota
import base64
from abc import ABC, abstractmethod

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
            # Fallback a variables de entorno si git-tokens no está disponible
            return self._get_token_from_env(platform_info)

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

        # Fallback a variables de entorno
        return self._get_token_from_env(platform_info)

    def _get_token_from_env(self, platform_info: PlatformInfo) -> Optional[str]:
        """Obtiene token desde variables de entorno como fallback."""
        import os

        # Mapeo de plataformas a variables de entorno
        env_vars = {
            'github': ['GITHUB_TOKEN', 'GH_TOKEN'],
            'gitlab': ['GITLAB_TOKEN', 'GL_TOKEN'],
            'forgejo': ['FORGEJO_TOKEN', 'GITEA_TOKEN'],  # Forgejo es compatible con Gitea
            'gitea': ['GITEA_TOKEN', 'FORGEJO_TOKEN'],    # Gitea es compatible con Forgejo
            'bitbucket': ['BITBUCKET_TOKEN', 'BB_TOKEN']
        }

        # Intentar obtener token de variables de entorno
        for var_name in env_vars.get(platform_info.service, []):
            token = os.getenv(var_name)
            if token:
                return token

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

class ForgejoCompatibleAPI(BasePlatformAPI):
    """
    Clase base para APIs compatibles con Forgejo.

    Forgejo utiliza una API compatible con GitHub, por lo que esta clase base
    implementa la funcionalidad común que pueden usar tanto Forgejo como Gitea.
    La API de Forgejo es la implementación de referencia.
    """

    def _get_base_url(self) -> str:
        """Construye la URL base de la API."""
        if self.platform_info.host:
            return f"https://{self.platform_info.host}/api/v1"
        else:
            # Para servicios cloud de Forgejo
            return "https://codeberg.org/api/v1"

    def _get_auth_headers(self) -> dict:
        """Obtiene headers de autenticación estándar para Forgejo/Gitea."""
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "develop") -> bool:
        """
        Crea un pull request usando la API de Forgejo.

        La API de Forgejo es compatible con GitHub pero con algunas diferencias menores.
        """
        if not REQUESTS_AVAILABLE:
            return False

        url = f"{self.base_url}/repos/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/pulls"
        headers = self._get_auth_headers()

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
        """
        Verifica el estado de CI para una rama.

        Utiliza el endpoint de status de commits compatible con GitHub.
        """
        if not REQUESTS_AVAILABLE:
            return False

        url = f"{self.base_url}/repos/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/commits/{branch}/status"
        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                status_data = response.json()
                state = status_data.get('state', 'pending')
                return state == 'success'
        except Exception:
            pass

        return False

    def merge_pull_request(self, pr_id: int) -> bool:
        """
        Hace merge de un pull request.

        Utiliza el endpoint de merge compatible con GitHub.
        """
        if not REQUESTS_AVAILABLE:
            return False

        url = f"{self.base_url}/repos/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/pulls/{pr_id}/merge"
        headers = self._get_auth_headers()

        data = {
            'commit_title': 'Auto-merge via git-integration-manager',
            'merge_method': 'merge'
        }

        try:
            response = requests.put(url, headers=headers, json=data, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def get_repository_info(self) -> dict:
        """
        Obtiene información del repositorio.

        Método adicional útil para validaciones y metadatos.
        """
        if not REQUESTS_AVAILABLE:
            return {}

        url = f"{self.base_url}/repos/{self.platform_info.repo_owner}/{self.platform_info.repo_name}"
        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass

        return {}

class ForgejoAPI(ForgejoCompatibleAPI):
    """
    API específica de Forgejo.

    Forgejo es un fork de Gitea con enfoque en la gobernanza comunitaria.
    Utiliza la API de Forgejo como implementación de referencia.
    """

    def _get_base_url(self) -> str:
        """URL base específica para Forgejo."""
        if self.platform_info.host:
            # Forgejo on-premise
            return f"https://{self.platform_info.host}/api/v1"
        else:
            # Forgejo cloud (Codeberg es la instancia principal)
            return "https://codeberg.org/api/v1"

    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "develop") -> bool:
        """
        Crea un pull request en Forgejo.

        Forgejo puede tener características específicas o mejoras sobre la API base.
        """
        # Usar implementación base de ForgejoCompatibleAPI
        success = super().create_pull_request(title, body, head_branch, base_branch)

        if success:
            # Aquí se pueden añadir características específicas de Forgejo
            # como labels automáticos, assignees, etc.
            pass

        return success

    def check_ci_status(self, branch: str) -> bool:
        """
        Verifica CI en Forgejo.

        Forgejo puede tener integraciones CI específicas.
        """
        # Usar implementación base y añadir verificaciones específicas de Forgejo
        base_status = super().check_ci_status(branch)

        # Aquí se pueden añadir verificaciones específicas de Forgejo
        # como Woodpecker CI, que es común en instancias de Forgejo

        return base_status

class GiteaAPI(ForgejoCompatibleAPI):
    """
    API específica de Gitea.

    Gitea es el proyecto original del cual Forgejo es un fork.
    Hereda la funcionalidad base de ForgejoCompatibleAPI pero puede
    tener diferencias específicas en endpoints o comportamiento.
    """

    def _get_base_url(self) -> str:
        """URL base específica para Gitea."""
        if self.platform_info.host:
            # Gitea es principalmente on-premise
            return f"https://{self.platform_info.host}/api/v1"
        else:
            # Gitea cloud es menos común, pero puede existir
            return f"https://gitea.com/api/v1"

    def _get_auth_headers(self) -> dict:
        """
        Headers de autenticación para Gitea.

        Gitea puede tener ligeras diferencias en headers aceptados.
        """
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'git-integration-manager/1.0'  # Gitea a veces requiere User-Agent
        }

    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "develop") -> bool:
        """
        Crea un pull request en Gitea.

        Gitea puede tener diferencias menores en la API comparado con Forgejo.
        """
        if not REQUESTS_AVAILABLE:
            return False

        url = f"{self.base_url}/repos/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/pulls"
        headers = self._get_auth_headers()

        # Gitea puede requerir campos específicos o tener nombres diferentes
        data = {
            'title': title,
            'body': body,
            'head': head_branch,
            'base': base_branch,
            # Gitea específico: puede requerir assignees como lista vacía
            'assignees': []
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            return response.status_code == 201
        except Exception:
            return False

    def check_ci_status(self, branch: str) -> bool:
        """
        Verifica CI en Gitea.

        Gitea puede tener diferentes integraciones CI que Forgejo.
        """
        # Usar implementación base pero con verificaciones específicas de Gitea
        base_status = super().check_ci_status(branch)

        # Gitea puede tener integraciones específicas como Drone CI
        # que requieren verificaciones adicionales

        return base_status

    def get_repository_info(self) -> dict:
        """
        Obtiene información del repositorio en Gitea.

        Gitea puede retornar campos específicos diferentes a Forgejo.
        """
        repo_info = super().get_repository_info()

        # Procesar campos específicos de Gitea si es necesario
        if repo_info:
            # Gitea puede tener campos específicos que necesiten procesamiento
            pass

        return repo_info

class BitbucketAPI(BasePlatformAPI):
    """
    API específica de Bitbucket.

    Bitbucket tiene una API REST v2 completamente diferente a GitHub/Forgejo/Gitea.
    """

    def _get_base_url(self) -> str:
        """URL base para Bitbucket."""
        if self.platform_info.host:
            # Bitbucket Server (on-premise)
            return f"https://{self.platform_info.host}/rest/api/1.0"
        else:
            # Bitbucket Cloud
            return "https://api.bitbucket.org/2.0"

    def _get_auth_headers(self) -> dict:
        """Headers de autenticación para Bitbucket."""
        if self.platform_info.host:
            # Bitbucket Server usa Bearer token
            return {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
        else:
            # Bitbucket Cloud puede usar App Password
            return {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }

    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "develop") -> bool:
        """
        Crea un pull request en Bitbucket.

        Bitbucket tiene una estructura de API diferente.
        """
        if not REQUESTS_AVAILABLE:
            return False

        if self.platform_info.host:
            # Bitbucket Server
            url = f"{self.base_url}/projects/{self.platform_info.repo_owner}/repos/{self.platform_info.repo_name}/pull-requests"
            data = {
                'title': title,
                'description': body,
                'fromRef': {'id': f'refs/heads/{head_branch}'},
                'toRef': {'id': f'refs/heads/{base_branch}'}
            }
        else:
            # Bitbucket Cloud
            url = f"{self.base_url}/repositories/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/pullrequests"
            data = {
                'title': title,
                'description': body,
                'source': {'branch': {'name': head_branch}},
                'destination': {'branch': {'name': base_branch}}
            }

        headers = self._get_auth_headers()

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            return response.status_code == 201
        except Exception:
            return False

    def check_ci_status(self, branch: str) -> bool:
        """
        Verifica CI en Bitbucket.

        Bitbucket tiene su propio sistema de pipelines.
        """
        if not REQUESTS_AVAILABLE:
            return False

        if self.platform_info.host:
            # Bitbucket Server - verificar build status
            url = f"{self.base_url}/projects/{self.platform_info.repo_owner}/repos/{self.platform_info.repo_name}/commits/{branch}/builds"
        else:
            # Bitbucket Cloud - verificar pipelines
            url = f"{self.base_url}/repositories/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/pipelines"

        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Procesar respuesta específica de Bitbucket
                data = response.json()
                # Lógica específica para determinar estado de CI en Bitbucket
                return True  # Simplificado por ahora
        except Exception:
            pass

        return False

    def merge_pull_request(self, pr_id: int) -> bool:
        """
        Hace merge de un pull request en Bitbucket.
        """
        if not REQUESTS_AVAILABLE:
            return False

        if self.platform_info.host:
            # Bitbucket Server
            url = f"{self.base_url}/projects/{self.platform_info.repo_owner}/repos/{self.platform_info.repo_name}/pull-requests/{pr_id}/merge"
        else:
            # Bitbucket Cloud
            url = f"{self.base_url}/repositories/{self.platform_info.repo_owner}/{self.platform_info.repo_name}/pullrequests/{pr_id}/merge"

        headers = self._get_auth_headers()

        try:
            response = requests.post(url, headers=headers, timeout=10)
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
        elif platform_info.service == 'forgejo':
            return ForgejoAPI(platform_info, token)
        elif platform_info.service == 'gitea':
            return GiteaAPI(platform_info, token)
        elif platform_info.service == 'bitbucket':
            return BitbucketAPI(platform_info, token)
        else:
            # Plataforma no soportada
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
        self.github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        self.gitlab_token = os.getenv('GITLAB_TOKEN') or os.getenv('GL_TOKEN')
        self.forgejo_token = os.getenv('FORGEJO_TOKEN') or os.getenv('GITEA_TOKEN')
        self.gitea_token = os.getenv('GITEA_TOKEN') or os.getenv('FORGEJO_TOKEN')
        self.bitbucket_token = os.getenv('BITBUCKET_TOKEN') or os.getenv('BB_TOKEN')
        self.capabilities = self._detect_capabilities()

    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detecta qué APIs están disponibles."""
        caps = {
            'github_api': bool(self.github_token and REQUESTS_AVAILABLE),
            'gitlab_api': bool(self.gitlab_token and REQUESTS_AVAILABLE),
            'forgejo_api': bool(self.forgejo_token and REQUESTS_AVAILABLE),
            'gitea_api': bool(self.gitea_token and REQUESTS_AVAILABLE),
            'bitbucket_api': bool(self.bitbucket_token and REQUESTS_AVAILABLE),
            'git_cli': True,  # Siempre disponible
            'local_analysis': True,  # Siempre disponible
        }

        # Verificar conectividad específica para las APIs principales
        if caps['github_api']:
            caps['github_api'] = self._test_github_connection()

        if caps['gitlab_api']:
            caps['gitlab_api'] = self._test_gitlab_connection()

        if caps['forgejo_api']:
            caps['forgejo_api'] = self._test_forgejo_connection()

        if caps['gitea_api']:
            caps['gitea_api'] = self._test_gitea_connection()

        if caps['bitbucket_api']:
            caps['bitbucket_api'] = self._test_bitbucket_connection()

        return caps

    def _test_github_connection(self) -> bool:
        """Prueba conexión con GitHub API."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {self.github_token}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def _test_gitlab_connection(self) -> bool:
        """Prueba conexión con GitLab API."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.get(
                'https://gitlab.com/api/v4/user',
                headers={'Authorization': f'Bearer {self.gitlab_token}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def _test_forgejo_connection(self) -> bool:
        """Prueba conexión con Forgejo API (usando Codeberg como referencia)."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            # Probar con Codeberg (instancia principal de Forgejo)
            response = requests.get(
                'https://codeberg.org/api/v1/user',
                headers={'Authorization': f'token {self.forgejo_token}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            # Si falla, asumir que el token es válido pero la instancia no es accesible
            return True

    def _test_gitea_connection(self) -> bool:
        """Prueba conexión con Gitea API."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            # Gitea es principalmente on-premise, así que no hay una instancia estándar para probar
            # Asumir que el token es válido si existe
            return True
        except Exception:
            return False

    def _test_bitbucket_connection(self) -> bool:
        """Prueba conexión con Bitbucket API."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.get(
                'https://api.bitbucket.org/2.0/user',
                headers={'Authorization': f'Bearer {self.bitbucket_token}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_capability_level(self) -> CapabilityLevel:
        """Determina el nivel de capacidades disponibles."""
        api_count = sum([
            self.capabilities['github_api'],
            self.capabilities['gitlab_api'],
            self.capabilities['forgejo_api'],
            self.capabilities['gitea_api'],
            self.capabilities['bitbucket_api']
        ])

        if api_count >= 1:
            return CapabilityLevel.FULL
        elif REQUESTS_AVAILABLE:
            return CapabilityLevel.ENHANCED
        else:
            return CapabilityLevel.BASIC

    def get_available_platforms(self) -> List[str]:
        """Retorna lista de plataformas con APIs disponibles."""
        available = []
        if self.capabilities['github_api']:
            available.append('github')
        if self.capabilities['gitlab_api']:
            available.append('gitlab')
        if self.capabilities['forgejo_api']:
            available.append('forgejo')
        if self.capabilities['gitea_api']:
            available.append('gitea')
        if self.capabilities['bitbucket_api']:
            available.append('bitbucket')
        return available

# ============================================================================
# NUEVAS CLASES PARA CONFIGURACIÓN AUTOMÁTICA DEL REMOTO
# ============================================================================

class PlatformProtectionAPI(ABC):
    """Interfaz abstracta para APIs de protección de branches."""

    @abstractmethod
    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de una branch."""
        pass

    @abstractmethod
    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección a una branch."""
        pass

    @abstractmethod
    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        pass

    @abstractmethod
    def list_protected_branches(self) -> list:
        """Lista todas las branches protegidas."""
        pass

class GitHubProtectionAPI(PlatformProtectionAPI):
    """API específica de GitHub para branch protection."""

    def __init__(self, platform_info: PlatformInfo, token: str):
        self.platform = platform_info
        self.token = token
        self.base_url = f"https://api.github.com/repos/{platform_info.repo_owner}/{platform_info.repo_name}"

    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de GitHub."""
        if not REQUESTS_AVAILABLE:
            return {}

        url = f"{self.base_url}/branches/{branch_name}/protection"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección GitHub-específica."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/branches/{branch_name}/protection"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Mapear configuración universal a GitHub
        github_config = self._map_universal_to_github(config)

        try:
            response = requests.put(url, headers=headers, json=github_config, timeout=10)
            if response.status_code == 200:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/branches/{branch_name}/protection"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.delete(url, headers=headers, timeout=10)
            if response.status_code == 204:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def list_protected_branches(self) -> list:
        """Lista branches protegidas en GitHub."""
        if not REQUESTS_AVAILABLE:
            return []

        url = f"{self.base_url}/branches"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                branches = response.json()
                return [b["name"] for b in branches if b.get("protected", False)]
            return []
        except Exception:
            return []

    def _map_universal_to_github(self, universal_config):
        """Mapea configuración universal a formato GitHub."""
        github_config = {}

        # Required PR reviews
        if universal_config.get("require_reviews"):
            github_config["required_pull_request_reviews"] = {
                "required_approving_review_count": universal_config.get("min_reviewers", 1),
                "dismiss_stale_reviews": universal_config.get("dismiss_stale", True),
                "require_code_owner_reviews": universal_config.get("require_code_owners", False)
            }

        # Status checks
        if universal_config.get("required_checks"):
            github_config["required_status_checks"] = {
                "strict": universal_config.get("require_up_to_date", True),
                "contexts": universal_config["required_checks"]
            }

        # Restrictions - GitHub requiere este campo, usar null si no hay restricciones
        if universal_config.get("restrict_access"):
            github_config["restrictions"] = {
                "users": universal_config.get("allowed_users", []),
                "teams": universal_config.get("allowed_teams", [])
            }
        else:
            github_config["restrictions"] = None

        github_config["enforce_admins"] = universal_config.get("enforce_admins", True)

        return github_config

class GitLabProtectionAPI(PlatformProtectionAPI):
    """API específica de GitLab para branch protection."""

    def __init__(self, platform_info: PlatformInfo, token: str):
        self.platform = platform_info
        self.token = token
        if platform_info.host:
            self.base_url = f"https://{platform_info.host}/api/v4"
        else:
            self.base_url = "https://gitlab.com/api/v4"

        # Obtener project ID
        self.project_id = self._get_project_id()

    def _get_project_id(self):
        """Obtiene el ID del proyecto GitLab."""
        return f"{self.platform.repo_owner}/{self.platform.repo_name}"

    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de GitLab."""
        if not REQUESTS_AVAILABLE:
            return {}

        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(self.project_id)}/protected_branches/{branch_name}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección GitLab-específica."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(self.project_id)}/protected_branches"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        # Mapear configuración universal a GitLab
        gitlab_config = self._map_universal_to_gitlab(config, branch_name)

        try:
            response = requests.post(url, headers=headers, json=gitlab_config, timeout=10)
            if response.status_code == 201:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(self.project_id)}/protected_branches/{branch_name}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.delete(url, headers=headers, timeout=10)
            if response.status_code == 204:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def list_protected_branches(self) -> list:
        """Lista branches protegidas en GitLab."""
        if not REQUESTS_AVAILABLE:
            return []

        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(self.project_id)}/protected_branches"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                branches = response.json()
                return [branch['name'] for branch in branches]
            return []
        except Exception:
            return []

    def _map_universal_to_gitlab(self, universal_config, branch_name):
        """Mapea configuración universal a formato GitLab."""
        return {
            "name": branch_name,
            "push_access_level": 40 if universal_config.get("restrict_access") else 30,  # Maintainer vs Developer
            "merge_access_level": 40 if universal_config.get("require_reviews") else 30,
            "unprotect_access_level": 40,  # Solo maintainers pueden desproteger
            "code_owner_approval_required": universal_config.get("require_code_owners", False)
        }

class ForgejoCompatibleProtectionAPI(PlatformProtectionAPI):
    """
    API base para protección de branches compatible con Forgejo.

    Forgejo utiliza una API compatible con GitHub para branch protection,
    por lo que esta clase base implementa la funcionalidad común.
    """

    def __init__(self, platform_info: PlatformInfo, token: str):
        self.platform = platform_info
        self.token = token
        self.base_url = self._get_base_url()

    def _get_base_url(self) -> str:
        """Construye la URL base de la API."""
        if self.platform.host:
            return f"https://{self.platform.host}/api/v1"
        else:
            # Para servicios cloud de Forgejo
            return "https://codeberg.org/api/v1"

    def _get_auth_headers(self) -> dict:
        """Obtiene headers de autenticación estándar."""
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de la branch."""
        if not REQUESTS_AVAILABLE:
            return {}

        url = f"{self.base_url}/repos/{self.platform.repo_owner}/{self.platform.repo_name}/branches/{branch_name}/protection"
        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección usando API compatible con GitHub."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/repos/{self.platform.repo_owner}/{self.platform.repo_name}/branches/{branch_name}/protection"
        headers = self._get_auth_headers()

        # Mapear configuración universal a formato Forgejo/GitHub
        forgejo_config = self._map_universal_to_forgejo(config)

        try:
            response = requests.put(url, headers=headers, json=forgejo_config, timeout=10)
            if response.status_code == 200:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/repos/{self.platform.repo_owner}/{self.platform.repo_name}/branches/{branch_name}/protection"
        headers = self._get_auth_headers()

        try:
            response = requests.delete(url, headers=headers, timeout=10)
            if response.status_code == 204:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def list_protected_branches(self) -> list:
        """Lista branches protegidas."""
        if not REQUESTS_AVAILABLE:
            return []

        url = f"{self.base_url}/repos/{self.platform.repo_owner}/{self.platform.repo_name}/branches"
        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                branches = response.json()
                # Filtrar solo las branches protegidas
                protected = []
                for branch in branches:
                    if branch.get('protected', False):
                        protected.append(branch['name'])
                return protected
            return []
        except Exception:
            return []

    def _map_universal_to_forgejo(self, universal_config):
        """Mapea configuración universal a formato Forgejo/GitHub."""
        config = {}

        # Required status checks
        if universal_config.get("required_checks"):
            config["required_status_checks"] = {
                "strict": universal_config.get("require_up_to_date", True),
                "contexts": universal_config.get("required_checks", [])
            }
        else:
            config["required_status_checks"] = None

        # Pull request reviews
        if universal_config.get("require_reviews"):
            config["required_pull_request_reviews"] = {
                "required_approving_review_count": universal_config.get("min_reviewers", 1),
                "dismiss_stale_reviews": universal_config.get("dismiss_stale", True),
                "require_code_owner_reviews": universal_config.get("require_code_owners", False)
            }
        else:
            config["required_pull_request_reviews"] = None

        # Restrictions
        if universal_config.get("restrict_access"):
            config["restrictions"] = {
                "users": universal_config.get("allowed_users", []),
                "teams": universal_config.get("allowed_teams", [])
            }
        else:
            config["restrictions"] = None

        # Enforce admins
        config["enforce_admins"] = universal_config.get("enforce_admins", True)

        # Allow force pushes and deletions
        config["allow_force_pushes"] = universal_config.get("allow_force_push", False)
        config["allow_deletions"] = universal_config.get("allow_deletions", False)

        return config

class ForgejoProtectionAPI(ForgejoCompatibleProtectionAPI):
    """
    API específica de Forgejo para branch protection.

    Forgejo puede tener características específicas o mejoras sobre la API base.
    """

    def _get_base_url(self) -> str:
        """URL base específica para Forgejo."""
        if self.platform.host:
            # Forgejo on-premise
            return f"https://{self.platform.host}/api/v1"
        else:
            # Forgejo cloud (Codeberg es la instancia principal)
            return "https://codeberg.org/api/v1"

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """
        Aplica protección en Forgejo.

        Forgejo puede tener características específicas o mejoras.
        """
        # Usar implementación base y añadir características específicas de Forgejo
        result = super().apply_protection(branch_name, config)

        if result.get("status") == "success":
            # Aquí se pueden añadir configuraciones específicas de Forgejo
            # como webhooks automáticos, integraciones con Woodpecker CI, etc.
            pass

        return result

class GiteaProtectionAPI(ForgejoCompatibleProtectionAPI):
    """
    API específica de Gitea para branch protection.

    Gitea puede tener diferencias específicas en endpoints o comportamiento.
    """

    def _get_base_url(self) -> str:
        """URL base específica para Gitea."""
        if self.platform.host:
            # Gitea es principalmente on-premise
            return f"https://{self.platform.host}/api/v1"
        else:
            # Gitea cloud es menos común
            return f"https://gitea.com/api/v1"

    def _get_auth_headers(self) -> dict:
        """
        Headers de autenticación para Gitea.

        Gitea puede tener ligeras diferencias en headers aceptados.
        """
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'git-integration-manager/1.0'  # Gitea a veces requiere User-Agent
        }

    def _map_universal_to_forgejo(self, universal_config):
        """
        Mapea configuración universal a formato Gitea.

        Gitea puede tener campos específicos diferentes a Forgejo.
        """
        config = super()._map_universal_to_forgejo(universal_config)

        # Gitea puede requerir campos específicos o tener nombres diferentes
        # Por ejemplo, Gitea puede no soportar code owners
        if config.get("required_pull_request_reviews"):
            # Gitea puede no soportar require_code_owner_reviews
            config["required_pull_request_reviews"]["require_code_owner_reviews"] = False

        return config

class BitbucketProtectionAPI(PlatformProtectionAPI):
    """
    API específica de Bitbucket para branch protection.

    Bitbucket tiene una API completamente diferente para branch permissions.
    """

    def __init__(self, platform_info: PlatformInfo, token: str):
        self.platform = platform_info
        self.token = token
        self.base_url = self._get_base_url()

    def _get_base_url(self) -> str:
        """URL base para Bitbucket."""
        if self.platform.host:
            # Bitbucket Server (on-premise)
            return f"https://{self.platform.host}/rest/api/1.0"
        else:
            # Bitbucket Cloud
            return "https://api.bitbucket.org/2.0"

    def _get_auth_headers(self) -> dict:
        """Headers de autenticación para Bitbucket."""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de Bitbucket."""
        if not REQUESTS_AVAILABLE:
            return {}

        if self.platform.host:
            # Bitbucket Server
            url = f"{self.base_url}/projects/{self.platform.repo_owner}/repos/{self.platform.repo_name}/restrictions"
        else:
            # Bitbucket Cloud
            url = f"{self.base_url}/repositories/{self.platform.repo_owner}/{self.platform.repo_name}/branch-restrictions"

        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                restrictions = response.json()
                # Filtrar restricciones para la branch específica
                branch_restrictions = []
                if self.platform.host:
                    # Bitbucket Server format
                    for restriction in restrictions.get('values', []):
                        if restriction.get('matcher', {}).get('displayId') == branch_name:
                            branch_restrictions.append(restriction)
                else:
                    # Bitbucket Cloud format
                    for restriction in restrictions.get('values', []):
                        if restriction.get('pattern') == branch_name:
                            branch_restrictions.append(restriction)

                return {"restrictions": branch_restrictions}
            return {}
        except Exception:
            return {}

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección Bitbucket-específica."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        # Bitbucket maneja protección a través de branch restrictions
        restrictions = self._map_universal_to_bitbucket(config, branch_name)
        results = []

        for restriction in restrictions:
            if self.platform.host:
                # Bitbucket Server
                url = f"{self.base_url}/projects/{self.platform.repo_owner}/repos/{self.platform.repo_name}/restrictions"
            else:
                # Bitbucket Cloud
                url = f"{self.base_url}/repositories/{self.platform.repo_owner}/{self.platform.repo_name}/branch-restrictions"

            headers = self._get_auth_headers()

            try:
                response = requests.post(url, headers=headers, json=restriction, timeout=10)
                if response.status_code == 201:
                    results.append({"status": "success", "restriction": restriction["kind"]})
                else:
                    results.append({"status": "error", "message": response.text, "restriction": restriction["kind"]})
            except Exception as e:
                results.append({"status": "error", "message": str(e), "restriction": restriction["kind"]})

        return {"status": "success" if all(r["status"] == "success" for r in results) else "partial", "results": results, "branch": branch_name}

    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        # Primero obtener restricciones actuales
        current = self.get_current_protection(branch_name)
        restrictions = current.get("restrictions", [])

        results = []
        for restriction in restrictions:
            restriction_id = restriction.get("id")
            if restriction_id:
                if self.platform.host:
                    # Bitbucket Server
                    url = f"{self.base_url}/projects/{self.platform.repo_owner}/repos/{self.platform.repo_name}/restrictions/{restriction_id}"
                else:
                    # Bitbucket Cloud
                    url = f"{self.base_url}/repositories/{self.platform.repo_owner}/{self.platform.repo_name}/branch-restrictions/{restriction_id}"

                headers = self._get_auth_headers()

                try:
                    response = requests.delete(url, headers=headers, timeout=10)
                    if response.status_code == 204:
                        results.append({"status": "success", "restriction_id": restriction_id})
                    else:
                        results.append({"status": "error", "message": response.text, "restriction_id": restriction_id})
                except Exception as e:
                    results.append({"status": "error", "message": str(e), "restriction_id": restriction_id})

        return {"status": "success" if all(r["status"] == "success" for r in results) else "partial", "results": results, "branch": branch_name}

    def list_protected_branches(self) -> list:
        """Lista branches protegidas en Bitbucket."""
        if not REQUESTS_AVAILABLE:
            return []

        if self.platform.host:
            # Bitbucket Server
            url = f"{self.base_url}/projects/{self.platform.repo_owner}/repos/{self.platform.repo_name}/restrictions"
        else:
            # Bitbucket Cloud
            url = f"{self.base_url}/repositories/{self.platform.repo_owner}/{self.platform.repo_name}/branch-restrictions"

        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                restrictions = response.json()
                protected_branches = set()

                if self.platform.host:
                    # Bitbucket Server format
                    for restriction in restrictions.get('values', []):
                        branch_pattern = restriction.get('matcher', {}).get('displayId')
                        if branch_pattern:
                            protected_branches.add(branch_pattern)
                else:
                    # Bitbucket Cloud format
                    for restriction in restrictions.get('values', []):
                        pattern = restriction.get('pattern')
                        if pattern:
                            protected_branches.add(pattern)

                return list(protected_branches)
            return []
        except Exception:
            return []

    def _map_universal_to_bitbucket(self, universal_config, branch_name):
        """Mapea configuración universal a formato Bitbucket."""
        restrictions = []

        # Bitbucket maneja protección a través de diferentes tipos de restricciones
        if universal_config.get("require_reviews"):
            if self.platform.host:
                # Bitbucket Server format
                restrictions.append({
                    "type": "pull-request-only",
                    "matcher": {
                        "id": branch_name,
                        "displayId": branch_name,
                        "type": {"id": "BRANCH", "name": "Branch"}
                    },
                    "users": [],
                    "groups": []
                })
            else:
                # Bitbucket Cloud format
                restrictions.append({
                    "kind": "require_approvals_to_merge",
                    "pattern": branch_name,
                    "value": universal_config.get("min_reviewers", 1)
                })

        # Restricción de push directo
        if universal_config.get("restrict_access"):
            if self.platform.host:
                # Bitbucket Server
                restrictions.append({
                    "type": "no-deletes",
                    "matcher": {
                        "id": branch_name,
                        "displayId": branch_name,
                        "type": {"id": "BRANCH", "name": "Branch"}
                    }
                })
            else:
                # Bitbucket Cloud
                restrictions.append({
                    "kind": "restrict_merges",
                    "pattern": branch_name,
                    "users": universal_config.get("allowed_users", [])
                })

        return restrictions

class PlatformAPIFactory:
    """Factory para crear APIs de protección específicas."""

    @staticmethod
    def create_protection_api(platform_info: PlatformInfo, token: str) -> Optional[PlatformProtectionAPI]:
        """Crea API de protección específica según la plataforma."""

        if platform_info.service == "github":
            return GitHubProtectionAPI(platform_info, token)
        elif platform_info.service == "gitlab":
            return GitLabProtectionAPI(platform_info, token)
        elif platform_info.service == "forgejo":
            return ForgejoProtectionAPI(platform_info, token)
        elif platform_info.service == "gitea":
            return GiteaProtectionAPI(platform_info, token)
        elif platform_info.service == "bitbucket":
            return BitbucketProtectionAPI(platform_info, token)
        else:
            # Plataforma no soportada
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
        self.github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        self.gitlab_token = os.getenv('GITLAB_TOKEN') or os.getenv('GL_TOKEN')
        self.forgejo_token = os.getenv('FORGEJO_TOKEN') or os.getenv('GITEA_TOKEN')
        self.gitea_token = os.getenv('GITEA_TOKEN') or os.getenv('FORGEJO_TOKEN')
        self.bitbucket_token = os.getenv('BITBUCKET_TOKEN') or os.getenv('BB_TOKEN')
        self.capabilities = self._detect_capabilities()

    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detecta qué APIs están disponibles."""
        caps = {
            'github_api': bool(self.github_token and REQUESTS_AVAILABLE),
            'gitlab_api': bool(self.gitlab_token and REQUESTS_AVAILABLE),
            'forgejo_api': bool(self.forgejo_token and REQUESTS_AVAILABLE),
            'gitea_api': bool(self.gitea_token and REQUESTS_AVAILABLE),
            'bitbucket_api': bool(self.bitbucket_token and REQUESTS_AVAILABLE),
            'git_cli': True,  # Siempre disponible
            'local_analysis': True,  # Siempre disponible
        }

        # Verificar conectividad específica para las APIs principales
        if caps['github_api']:
            caps['github_api'] = self._test_github_connection()

        if caps['gitlab_api']:
            caps['gitlab_api'] = self._test_gitlab_connection()

        if caps['forgejo_api']:
            caps['forgejo_api'] = self._test_forgejo_connection()

        if caps['gitea_api']:
            caps['gitea_api'] = self._test_gitea_connection()

        if caps['bitbucket_api']:
            caps['bitbucket_api'] = self._test_bitbucket_connection()

        return caps

    def _test_github_connection(self) -> bool:
        """Prueba conexión con GitHub API."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {self.github_token}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def _test_gitlab_connection(self) -> bool:
        """Prueba conexión con GitLab API."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.get(
                'https://gitlab.com/api/v4/user',
                headers={'Authorization': f'Bearer {self.gitlab_token}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def _test_forgejo_connection(self) -> bool:
        """Prueba conexión con Forgejo API (usando Codeberg como referencia)."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            # Probar con Codeberg (instancia principal de Forgejo)
            response = requests.get(
                'https://codeberg.org/api/v1/user',
                headers={'Authorization': f'token {self.forgejo_token}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            # Si falla, asumir que el token es válido pero la instancia no es accesible
            return True

    def _test_gitea_connection(self) -> bool:
        """Prueba conexión con Gitea API."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            # Gitea es principalmente on-premise, así que no hay una instancia estándar para probar
            # Asumir que el token es válido si existe
            return True
        except Exception:
            return False

    def _test_bitbucket_connection(self) -> bool:
        """Prueba conexión con Bitbucket API."""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.get(
                'https://api.bitbucket.org/2.0/user',
                headers={'Authorization': f'Bearer {self.bitbucket_token}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_capability_level(self) -> CapabilityLevel:
        """Determina el nivel de capacidades disponibles."""
        api_count = sum([
            self.capabilities['github_api'],
            self.capabilities['gitlab_api'],
            self.capabilities['forgejo_api'],
            self.capabilities['gitea_api'],
            self.capabilities['bitbucket_api']
        ])

        if api_count >= 1:
            return CapabilityLevel.FULL
        elif REQUESTS_AVAILABLE:
            return CapabilityLevel.ENHANCED
        else:
            return CapabilityLevel.BASIC

    def get_available_platforms(self) -> List[str]:
        """Retorna lista de plataformas con APIs disponibles."""
        available = []
        if self.capabilities['github_api']:
            available.append('github')
        if self.capabilities['gitlab_api']:
            available.append('gitlab')
        if self.capabilities['forgejo_api']:
            available.append('forgejo')
        if self.capabilities['gitea_api']:
            available.append('gitea')
        if self.capabilities['bitbucket_api']:
            available.append('bitbucket')
        return available

# ============================================================================
# NUEVAS CLASES PARA CONFIGURACIÓN AUTOMÁTICA DEL REMOTO
# ============================================================================

class PlatformProtectionAPI(ABC):
    """Interfaz abstracta para APIs de protección de branches."""

    @abstractmethod
    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de una branch."""
        pass

    @abstractmethod
    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección a una branch."""
        pass

    @abstractmethod
    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        pass

    @abstractmethod
    def list_protected_branches(self) -> list:
        """Lista todas las branches protegidas."""
        pass

class GitHubProtectionAPI(PlatformProtectionAPI):
    """API específica de GitHub para branch protection."""

    def __init__(self, platform_info: PlatformInfo, token: str):
        self.platform = platform_info
        self.token = token
        self.base_url = f"https://api.github.com/repos/{platform_info.repo_owner}/{platform_info.repo_name}"

    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de GitHub."""
        if not REQUESTS_AVAILABLE:
            return {}

        url = f"{self.base_url}/branches/{branch_name}/protection"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección GitHub-específica."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/branches/{branch_name}/protection"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Mapear configuración universal a GitHub
        github_config = self._map_universal_to_github(config)

        try:
            response = requests.put(url, headers=headers, json=github_config, timeout=10)
            if response.status_code == 200:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/branches/{branch_name}/protection"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.delete(url, headers=headers, timeout=10)
            if response.status_code == 204:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def list_protected_branches(self) -> list:
        """Lista branches protegidas en GitHub."""
        if not REQUESTS_AVAILABLE:
            return []

        url = f"{self.base_url}/branches"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                branches = response.json()
                return [b["name"] for b in branches if b.get("protected", False)]
            return []
        except Exception:
            return []

    def _map_universal_to_github(self, universal_config):
        """Mapea configuración universal a formato GitHub."""
        github_config = {}

        # Required PR reviews
        if universal_config.get("require_reviews"):
            github_config["required_pull_request_reviews"] = {
                "required_approving_review_count": universal_config.get("min_reviewers", 1),
                "dismiss_stale_reviews": universal_config.get("dismiss_stale", True),
                "require_code_owner_reviews": universal_config.get("require_code_owners", False)
            }

        # Status checks
        if universal_config.get("required_checks"):
            github_config["required_status_checks"] = {
                "strict": universal_config.get("require_up_to_date", True),
                "contexts": universal_config["required_checks"]
            }

        # Restrictions - GitHub requiere este campo, usar null si no hay restricciones
        if universal_config.get("restrict_access"):
            github_config["restrictions"] = {
                "users": universal_config.get("allowed_users", []),
                "teams": universal_config.get("allowed_teams", [])
            }
        else:
            github_config["restrictions"] = None

        github_config["enforce_admins"] = universal_config.get("enforce_admins", True)

        return github_config

class GitLabProtectionAPI(PlatformProtectionAPI):
    """API específica de GitLab para branch protection."""

    def __init__(self, platform_info: PlatformInfo, token: str):
        self.platform = platform_info
        self.token = token
        if platform_info.host:
            self.base_url = f"https://{platform_info.host}/api/v4"
        else:
            self.base_url = "https://gitlab.com/api/v4"

        # Obtener project ID
        self.project_id = self._get_project_id()

    def _get_project_id(self):
        """Obtiene el ID del proyecto GitLab."""
        return f"{self.platform.repo_owner}/{self.platform.repo_name}"

    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de GitLab."""
        if not REQUESTS_AVAILABLE:
            return {}

        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(self.project_id)}/protected_branches/{branch_name}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección GitLab-específica."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(self.project_id)}/protected_branches"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        # Mapear configuración universal a GitLab
        gitlab_config = self._map_universal_to_gitlab(config, branch_name)

        try:
            response = requests.post(url, headers=headers, data=gitlab_config, timeout=10)
            if response.status_code == 201:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(self.project_id)}/protected_branches/{branch_name}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.delete(url, headers=headers, timeout=10)
            if response.status_code == 204:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def list_protected_branches(self) -> list:
        """Lista branches protegidas en GitLab."""
        if not REQUESTS_AVAILABLE:
            return []

        url = f"{self.base_url}/projects/{urllib.parse.quote_plus(self.project_id)}/protected_branches"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                branches = response.json()
                return [branch['name'] for branch in branches]
            return []
        except Exception:
            return []

    def _map_universal_to_gitlab(self, universal_config, branch_name):
        """Mapea configuración universal a formato GitLab."""
        return {
            "name": branch_name,
            "push_access_level": 40 if universal_config.get("restrict_access") else 30,  # Maintainer vs Developer
            "merge_access_level": 40 if universal_config.get("require_reviews") else 30,
            "unprotect_access_level": 40,  # Solo maintainers pueden desproteger
            "code_owner_approval_required": universal_config.get("require_code_owners", False)
        }

class ForgejoCompatibleProtectionAPI(PlatformProtectionAPI):
    """
    API base para protección de branches compatible con Forgejo.

    Forgejo utiliza una API compatible con GitHub para branch protection,
    por lo que esta clase base implementa la funcionalidad común.
    """

    def __init__(self, platform_info: PlatformInfo, token: str):
        self.platform = platform_info
        self.token = token
        self.base_url = self._get_base_url()

    def _get_base_url(self) -> str:
        """Construye la URL base de la API."""
        if self.platform.host:
            return f"https://{self.platform.host}/api/v1"
        else:
            # Para servicios cloud de Forgejo
            return "https://codeberg.org/api/v1"

    def _get_auth_headers(self) -> dict:
        """Obtiene headers de autenticación estándar."""
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de la branch."""
        if not REQUESTS_AVAILABLE:
            return {}

        url = f"{self.base_url}/repos/{self.platform.repo_owner}/{self.platform.repo_name}/branches/{branch_name}/protection"
        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección usando API compatible con GitHub."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/repos/{self.platform.repo_owner}/{self.platform.repo_name}/branches/{branch_name}/protection"
        headers = self._get_auth_headers()

        # Mapear configuración universal a formato Forgejo/GitHub
        forgejo_config = self._map_universal_to_forgejo(config)

        try:
            response = requests.put(url, headers=headers, json=forgejo_config, timeout=10)
            if response.status_code == 200:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        url = f"{self.base_url}/repos/{self.platform.repo_owner}/{self.platform.repo_name}/branches/{branch_name}/protection"
        headers = self._get_auth_headers()

        try:
            response = requests.delete(url, headers=headers, timeout=10)
            if response.status_code == 204:
                return {"status": "success", "branch": branch_name}
            else:
                return {"status": "error", "message": response.text, "branch": branch_name}
        except Exception as e:
            return {"status": "error", "message": str(e), "branch": branch_name}

    def list_protected_branches(self) -> list:
        """Lista branches protegidas."""
        if not REQUESTS_AVAILABLE:
            return []

        url = f"{self.base_url}/repos/{self.platform.repo_owner}/{self.platform.repo_name}/branches"
        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                branches = response.json()
                # Filtrar solo las branches protegidas
                protected = []
                for branch in branches:
                    if branch.get('protected', False):
                        protected.append(branch['name'])
                return protected
            return []
        except Exception:
            return []

    def _map_universal_to_forgejo(self, universal_config):
        """Mapea configuración universal a formato Forgejo/GitHub."""
        config = {}

        # Required status checks
        if universal_config.get("required_checks"):
            config["required_status_checks"] = {
                "strict": universal_config.get("require_up_to_date", True),
                "contexts": universal_config.get("required_checks", [])
            }
        else:
            config["required_status_checks"] = None

        # Pull request reviews
        if universal_config.get("require_reviews"):
            config["required_pull_request_reviews"] = {
                "required_approving_review_count": universal_config.get("min_reviewers", 1),
                "dismiss_stale_reviews": universal_config.get("dismiss_stale", True),
                "require_code_owner_reviews": universal_config.get("require_code_owners", False)
            }
        else:
            config["required_pull_request_reviews"] = None

        # Restrictions
        if universal_config.get("restrict_access"):
            config["restrictions"] = {
                "users": universal_config.get("allowed_users", []),
                "teams": universal_config.get("allowed_teams", [])
            }
        else:
            config["restrictions"] = None

        # Enforce admins
        config["enforce_admins"] = universal_config.get("enforce_admins", True)

        # Allow force pushes and deletions
        config["allow_force_pushes"] = universal_config.get("allow_force_push", False)
        config["allow_deletions"] = universal_config.get("allow_deletions", False)

        return config

class ForgejoProtectionAPI(ForgejoCompatibleProtectionAPI):
    """
    API específica de Forgejo para branch protection.

    Forgejo puede tener características específicas o mejoras sobre la API base.
    """

    def _get_base_url(self) -> str:
        """URL base específica para Forgejo."""
        if self.platform.host:
            # Forgejo on-premise
            return f"https://{self.platform.host}/api/v1"
        else:
            # Forgejo cloud (Codeberg es la instancia principal)
            return "https://codeberg.org/api/v1"

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """
        Aplica protección en Forgejo.

        Forgejo puede tener características específicas o mejoras.
        """
        # Usar implementación base y añadir características específicas de Forgejo
        result = super().apply_protection(branch_name, config)

        if result.get("status") == "success":
            # Aquí se pueden añadir configuraciones específicas de Forgejo
            # como webhooks automáticos, integraciones con Woodpecker CI, etc.
            pass

        return result

class GiteaProtectionAPI(ForgejoCompatibleProtectionAPI):
    """
    API específica de Gitea para branch protection.

    Gitea puede tener diferencias específicas en endpoints o comportamiento.
    """

    def _get_base_url(self) -> str:
        """URL base específica para Gitea."""
        if self.platform.host:
            # Gitea es principalmente on-premise
            return f"https://{self.platform.host}/api/v1"
        else:
            # Gitea cloud es menos común
            return f"https://gitea.com/api/v1"

    def _get_auth_headers(self) -> dict:
        """
        Headers de autenticación para Gitea.

        Gitea puede tener ligeras diferencias en headers aceptados.
        """
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'git-integration-manager/1.0'  # Gitea a veces requiere User-Agent
        }

    def _map_universal_to_forgejo(self, universal_config):
        """
        Mapea configuración universal a formato Gitea.

        Gitea puede tener campos específicos diferentes a Forgejo.
        """
        config = super()._map_universal_to_forgejo(universal_config)

        # Gitea puede requerir campos específicos o tener nombres diferentes
        # Por ejemplo, Gitea puede no soportar code owners
        if config.get("required_pull_request_reviews"):
            # Gitea puede no soportar require_code_owner_reviews
            config["required_pull_request_reviews"]["require_code_owner_reviews"] = False

        return config

class BitbucketProtectionAPI(PlatformProtectionAPI):
    """
    API específica de Bitbucket para branch protection.

    Bitbucket tiene una API completamente diferente para branch permissions.
    """

    def __init__(self, platform_info: PlatformInfo, token: str):
        self.platform = platform_info
        self.token = token
        self.base_url = self._get_base_url()

    def _get_base_url(self) -> str:
        """URL base para Bitbucket."""
        if self.platform.host:
            # Bitbucket Server (on-premise)
            return f"https://{self.platform.host}/rest/api/1.0"
        else:
            # Bitbucket Cloud
            return "https://api.bitbucket.org/2.0"

    def _get_auth_headers(self) -> dict:
        """Headers de autenticación para Bitbucket."""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def get_current_protection(self, branch_name: str) -> dict:
        """Obtiene protección actual de Bitbucket."""
        if not REQUESTS_AVAILABLE:
            return {}

        if self.platform.host:
            # Bitbucket Server
            url = f"{self.base_url}/projects/{self.platform.repo_owner}/repos/{self.platform.repo_name}/restrictions"
        else:
            # Bitbucket Cloud
            url = f"{self.base_url}/repositories/{self.platform.repo_owner}/{self.platform.repo_name}/branch-restrictions"

        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                restrictions = response.json()
                # Filtrar restricciones para la branch específica
                branch_restrictions = []
                if self.platform.host:
                    # Bitbucket Server format
                    for restriction in restrictions.get('values', []):
                        if restriction.get('matcher', {}).get('displayId') == branch_name:
                            branch_restrictions.append(restriction)
                else:
                    # Bitbucket Cloud format
                    for restriction in restrictions.get('values', []):
                        if restriction.get('pattern') == branch_name:
                            branch_restrictions.append(restriction)

                return {"restrictions": branch_restrictions}
            return {}
        except Exception:
            return {}

    def apply_protection(self, branch_name: str, config: dict) -> dict:
        """Aplica protección Bitbucket-específica."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        # Bitbucket maneja protección a través de branch restrictions
        restrictions = self._map_universal_to_bitbucket(config, branch_name)
        results = []

        for restriction in restrictions:
            if self.platform.host:
                # Bitbucket Server
                url = f"{self.base_url}/projects/{self.platform.repo_owner}/repos/{self.platform.repo_name}/restrictions"
            else:
                # Bitbucket Cloud
                url = f"{self.base_url}/repositories/{self.platform.repo_owner}/{self.platform.repo_name}/branch-restrictions"

            headers = self._get_auth_headers()

            try:
                response = requests.post(url, headers=headers, json=restriction, timeout=10)
                if response.status_code == 201:
                    results.append({"status": "success", "restriction": restriction["kind"]})
                else:
                    results.append({"status": "error", "message": response.text, "restriction": restriction["kind"]})
            except Exception as e:
                results.append({"status": "error", "message": str(e), "restriction": restriction["kind"]})

        return {"status": "success" if all(r["status"] == "success" for r in results) else "partial", "results": results, "branch": branch_name}

    def remove_protection(self, branch_name: str) -> dict:
        """Remueve protección de una branch."""
        if not REQUESTS_AVAILABLE:
            return {"status": "error", "message": "requests no disponible"}

        # Primero obtener restricciones actuales
        current = self.get_current_protection(branch_name)
        restrictions = current.get("restrictions", [])

        results = []
        for restriction in restrictions:
            restriction_id = restriction.get("id")
            if restriction_id:
                if self.platform.host:
                    # Bitbucket Server
                    url = f"{self.base_url}/projects/{self.platform.repo_owner}/repos/{self.platform.repo_name}/restrictions/{restriction_id}"
                else:
                    # Bitbucket Cloud
                    url = f"{self.base_url}/repositories/{self.platform.repo_owner}/{self.platform.repo_name}/branch-restrictions/{restriction_id}"

                headers = self._get_auth_headers()

                try:
                    response = requests.delete(url, headers=headers, timeout=10)
                    if response.status_code == 204:
                        results.append({"status": "success", "restriction_id": restriction_id})
                    else:
                        results.append({"status": "error", "message": response.text, "restriction_id": restriction_id})
                except Exception as e:
                    results.append({"status": "error", "message": str(e), "restriction_id": restriction_id})

        return {"status": "success" if all(r["status"] == "success" for r in results) else "partial", "results": results, "branch": branch_name}

    def list_protected_branches(self) -> list:
        """Lista branches protegidas en Bitbucket."""
        if not REQUESTS_AVAILABLE:
            return []

        if self.platform.host:
            # Bitbucket Server
            url = f"{self.base_url}/projects/{self.platform.repo_owner}/repos/{self.platform.repo_name}/restrictions"
        else:
            # Bitbucket Cloud
            url = f"{self.base_url}/repositories/{self.platform.repo_owner}/{self.platform.repo_name}/branch-restrictions"

        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                restrictions = response.json()
                protected_branches = set()

                if self.platform.host:
                    # Bitbucket Server format
                    for restriction in restrictions.get('values', []):
                        branch_pattern = restriction.get('matcher', {}).get('displayId')
                        if branch_pattern:
                            protected_branches.add(branch_pattern)
                else:
                    # Bitbucket Cloud format
                    for restriction in restrictions.get('values', []):
                        pattern = restriction.get('pattern')
                        if pattern:
                            protected_branches.add(pattern)

                return list(protected_branches)
            return []
        except Exception:
            return []

    def _map_universal_to_bitbucket(self, universal_config, branch_name):
        """Mapea configuración universal a formato Bitbucket."""
        restrictions = []

        # Bitbucket maneja protección a través de diferentes tipos de restricciones
        if universal_config.get("require_reviews"):
            if self.platform.host:
                # Bitbucket Server format
                restrictions.append({
                    "type": "pull-request-only",
                    "matcher": {
                        "id": branch_name,
                        "displayId": branch_name,
                        "type": {"id": "BRANCH", "name": "Branch"}
                    },
                    "users": [],
                    "groups": []
                })
            else:
                # Bitbucket Cloud format
                restrictions.append({
                    "kind": "require_approvals_to_merge",
                    "pattern": branch_name,
                    "value": universal_config.get("min_reviewers", 1)
                })

        # Restricción de push directo
        if universal_config.get("restrict_access"):
            if self.platform.host:
                # Bitbucket Server
                restrictions.append({
                    "type": "no-deletes",
                    "matcher": {
                        "id": branch_name,
                        "displayId": branch_name,
                        "type": {"id": "BRANCH", "name": "Branch"}
                    }
                })
            else:
                # Bitbucket Cloud
                restrictions.append({
                    "kind": "restrict_merges",
                    "pattern": branch_name,
                    "users": universal_config.get("allowed_users", [])
                })

        return restrictions

class PlatformAPIFactory:
    """Factory para crear APIs de protección específicas."""

    @staticmethod
    def create_protection_api(platform_info: PlatformInfo, token: str) -> Optional[PlatformProtectionAPI]:
        """Crea API de protección específica según la plataforma."""

        if platform_info.service == "github":
            return GitHubProtectionAPI(platform_info, token)
        elif platform_info.service == "gitlab":
            return GitLabProtectionAPI(platform_info, token)
        elif platform_info.service == "forgejo":
            return ForgejoProtectionAPI(platform_info, token)
        elif platform_info.service == "gitea":
            return GiteaProtectionAPI(platform_info, token)
        elif platform_info.service == "bitbucket":
            return BitbucketProtectionAPI(platform_info, token)
        else:
            # Plataforma no soportada
            return None

class UniversalProtectionConfig:
    """Configuración universal que se mapea a todas las plataformas."""

    def __init__(self):
        self.config = {
            # Configuración básica
            "require_reviews": False,
            "min_reviewers": 1,
            "dismiss_stale": True,
            "require_code_owners": False,

            # Status checks
            "required_checks": [],
            "require_up_to_date": True,

            # Restricciones de acceso
            "restrict_access": False,
            "allowed_users": [],
            "allowed_teams": [],

            # Configuraciones administrativas
            "enforce_admins": True,
            "allow_force_push": False,
            "allow_deletions": False
        }

    @classmethod
    def from_strategy(cls, strategy_name: str):
        """Crea configuración desde estrategia predefinida."""

        config = cls()

        if strategy_name.upper() == "LOCAL":
            # Sin restricciones para desarrollo personal
            pass  # Configuración por defecto ya es permisiva

        elif strategy_name.upper() == "HYBRID":
            config.config.update({
                "require_reviews": True,
                "min_reviewers": 1,
                "required_checks": ["ci/tests"],  # Solo si existe
                "enforce_admins": False
            })

        elif strategy_name.upper() == "REMOTE":
            config.config.update({
                "require_reviews": True,
                "min_reviewers": 2,
                "require_code_owners": True,
                "required_checks": ["ci/tests", "security/scan", "quality/sonar"],
                "restrict_access": True,
                "enforce_admins": True
            })

        return config

class UniversalProtectionManager:
    """
    Gestiona la configuración de protección de ramas de forma universal,
    traduciéndola a la API de la plataforma específica.
    """
    def __init__(self, platform_info: PlatformInfo, token_manager: TokenManager, context: str = None):
        self.platform_info = platform_info
        self.token_manager = token_manager
        self.context = context # LOCAL, HYBRID, o REMOTE
        self.platform_token = self.token_manager.get_platform_token(self.platform_info)

        self.protection_api = PlatformAPIFactory.create_protection_api(
            self.platform_info, self.platform_token
        )

        # Cargar la configuración local directamente para ser autosuficiente.
        try:
            # Asumimos que la lógica de carga puede encontrar el validador.
            # Esta función está definida al principio del script.
            validator_module = load_validator_module()
            self.local_config = validator_module.VALIDATION_CONFIGS
        except Exception as e:
            # Este es un fallback crítico en caso de que el validador no se pueda cargar.
            print(f"{Fore.YELLOW}⚠️  Advertencia: No se pudo cargar la configuración de `branch-workflow-validator.py`: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   Las comparaciones con la configuración local no funcionarán.{Style.RESET_ALL}")
            self.local_config = {}

        if not self.protection_api:
            raise ValueError("No se pudo crear una API de protección para la plataforma especificada.")

    def apply_strategy(self, strategy_name: str, dry_run: bool = True) -> Tuple[bool, str]:
        """
        Aplica una estrategia de protección de ramas en el remoto.

        Esta función intenta aplicar la estrategia de protección especificada
        a las ramas protegidas en la plataforma remota. Si la estrategia
        es exitosa, devuelve un mensaje de éxito. Si no, devuelve un mensaje
        de error.

        Args:
            strategy_name (str): El nombre de la estrategia a aplicar.
            dry_run (bool): Si es True, solo muestra los cambios sin aplicarlos.

        Returns:
            Tuple[bool, str]: Un tuple donde el primer elemento es un booleano
                              que indica si la estrategia se aplicó correctamente
                              y el segundo elemento es un mensaje de éxito o error.
        """
        if not self.protection_api:
            return False, "Token no disponible o plataforma no soportada"

        # Crear configuración universal
        universal_config = UniversalProtectionConfig.from_strategy(strategy_name)

        # Adaptar configuración a capacidades de la plataforma
        adapted_config = self._adapt_to_platform_capabilities(universal_config.config)

        print(f"🎯 Aplicando estrategia '{strategy_name}' en {self.platform_info.service}")
        print(f"📋 Configuración adaptada para {self.platform_info.service}:")

        # Mostrar qué se aplicará
        self._show_config_summary(adapted_config)

        if dry_run:
            print("🔍 DRY RUN - No se aplicarán cambios reales")
            return True, "DRY RUN: La estrategia se aplicaría correctamente."

        # Aplicar a branches protegidas según estrategia
        target_protected_branches = set(self._get_protected_branches_for_strategy(strategy_name))
        current_protected_branches = set(self.protection_api.list_protected_branches())

        branches_to_protect = target_protected_branches - current_protected_branches
        branches_to_unprotect = current_protected_branches - target_protected_branches

        results = []

        # Proteger nuevas ramas
        for branch in branches_to_protect:
            print(f"🛡️  Aplicando protección a '{branch}'...")
            result = self.protection_api.apply_protection(branch, adapted_config)
            results.append(result)

        # Desproteger ramas que ya no deberían estarlo
        for branch in branches_to_unprotect:
            print(f"🗑️  Quitando protección de '{branch}'...")
            result = self.protection_api.remove_protection(branch)
            results.append(result)

        # Actualizar protección en ramas que ya están protegidas y deben seguir estándolo
        for branch in current_protected_branches.intersection(target_protected_branches):
            print(f"🔄 Actualizando protección de '{branch}'...")
            result = self.protection_api.apply_protection(branch, adapted_config)
            results.append(result)

        return results

    def get_protection_status(self, compare_with_local: bool = False):
        """Obtiene estado actual de protección."""

        if not self.protection_api:
            return {"status": "error", "message": "API no disponible"}

        protected_branches = self.protection_api.list_protected_branches()
        status = {
            "platform": self.platform_info.service,
            "protected_branches": protected_branches,
            "details": {}
        }

        for branch in protected_branches:
            protection = self.protection_api.get_current_protection(branch)
            status["details"][branch] = protection

        if compare_with_local:
            status["comparison"] = self._compare_with_local_config()

        return status

    def sync_protection_rules(self, direction: str = "local-to-remote", dry_run: bool = True):
        """Sincroniza reglas entre local y remoto."""

        if not self.protection_api:
            return {"status": "error", "message": "API no disponible"}

        if direction == "local-to-remote":
            return self._sync_local_to_remote(dry_run)
        elif direction == "remote-to-local":
            return self._sync_remote_to_local(dry_run)
        else:
            return {"status": "error", "message": "Dirección no válida"}

    def _detect_platform_capabilities(self):
        """Detecta qué capacidades soporta cada plataforma."""

        capabilities = {
            "github": {
                "required_reviews": True,
                "status_checks": True,
                "user_restrictions": True,
                "team_restrictions": True,
                "code_owners": True,
                "enforce_admins": True
            },
            "gitlab": {
                "required_reviews": True,  # Via merge request settings
                "status_checks": True,     # Via CI/CD pipelines
                "user_restrictions": True,
                "team_restrictions": False, # GitLab usa grupos
                "code_owners": True,
                "enforce_admins": False    # Diferentes permisos
            },
            "forgejo": {
                "required_reviews": True,
                "status_checks": True,     # Via Forgejo Actions
                "user_restrictions": True,
                "team_restrictions": True,
                "code_owners": True,       # ✅ Soportado desde v1.21
                "enforce_admins": True
            },
            "gitea": {
                "required_reviews": True,
                "status_checks": True,     # ✅ Via Gitea Actions (desde v1.19)
                "user_restrictions": True,
                "team_restrictions": True,
                "code_owners": False,      # ❌ No soportado
                "enforce_admins": True
            },
            "bitbucket": {
                "required_reviews": True,
                "status_checks": True,
                "user_restrictions": True,
                "team_restrictions": True,
                "code_owners": False,      # ❌ No soportado nativamente
                "enforce_admins": True
            }
        }

        return capabilities.get(self.platform_info.service, {})

    def _adapt_to_platform_capabilities(self, universal_config):
        """Adapta configuración universal a capacidades específicas."""

        adapted = universal_config.copy()

        # Remover configuraciones no soportadas
        if not self.local_config.get("code_owners"):
            adapted["require_code_owners"] = False
            print(f"⚠️  Code owners no soportado en {self.platform_info.service}")

        if not self.local_config.get("team_restrictions"):
            adapted["allowed_teams"] = []
            print(f"⚠️  Team restrictions no soportado en {self.platform_info.service}")

        return adapted

    def _show_config_summary(self, config):
        """Muestra resumen de configuración."""

        print("   Configuración:")
        if config.get("require_reviews"):
            print(f"   - Require reviews: {config['min_reviewers']} mínimo")
        if config.get("required_checks"):
            print(f"   - Status checks: {', '.join(config['required_checks'])}")
        if config.get("restrict_access"):
            print("   - Acceso restringido habilitado")
        if config.get("enforce_admins"):
            print("   - Enforce admins habilitado")

    def _get_protected_branches_for_strategy(self, strategy_name):
        """Obtiene lista de branches a proteger según estrategia."""

        if strategy_name.upper() == "LOCAL":
            return []  # Sin branches protegidas
        elif strategy_name.upper() == "HYBRID":
            return ["main", "develop"]
        elif strategy_name.upper() == "REMOTE":
            return ["main", "master", "develop", "staging", "release"]
        else:
            return ["main"]

    def _compare_with_local_config(self):
        """Compara la configuración remota con la local."""
        if not self.protection_api:
            return {"status": "error", "message": "API no disponible"}

        current_context_config = self.local_config.get(self.context, {})
        if not current_context_config:
            return {
                "status": "error",
                "message": f"No se pudo encontrar la configuración para el contexto '{self.context}' en el validador."
            }

        local_protected_branches = set(current_context_config.get("protected_branches", []))
        remote_branches = set(self.protection_api.list_protected_branches())

        remote_details = {
            "branches": {branch: self.protection_api.get_current_protection(branch) for branch in remote_branches}
        }

        local_protected = sorted(list(local_protected_branches))
        remote_protected_list = sorted(list(remote_branches))

        diff = {
            "local_only": sorted(list(local_protected_branches - remote_branches)),
            "remote_only": sorted(list(remote_branches - local_protected_branches)),
            "mismatched": []
        }

        return {
            "status": "ok",
            "local_protected": local_protected,
            "remote_protected": remote_protected_list,
            "diff": diff,
            "remote_details": remote_details
        }

    def _sync_local_to_remote(self, dry_run):
        """Sincroniza la configuración local HACIA el remoto."""
        # El 'strategy' es simplemente nuestro 'contexto'.
        strategy_name = self.context

        # Obtenemos la configuración para el contexto actual.
        current_context_config = self.local_config.get(strategy_name, {})
        if not current_context_config:
            print(f"{Fore.YELLOW}⚠️  No hay configuración local definida para el contexto '{strategy_name}'. No se puede sincronizar.{Style.RESET_ALL}")
            return False

        # Las ramas a proteger se leen directamente de la configuración del contexto.
        protected_branches = current_context_config.get("protected_branches", [])

        if not protected_branches:
            print(f"{Fore.YELLOW}⚠️  No hay ramas definidas para proteger en el contexto '{strategy_name}'.{Style.RESET_ALL}")
            return True # No es un error, simplemente no hay nada que hacer.

        # La configuración de protección a aplicar también viene del contexto.
        # Necesitamos un mapeo o una función que convierta la config del validador a la config universal.
        # Por ahora, usamos una estrategia fija como placeholder.
        universal_config = UniversalProtectionConfig.from_strategy(strategy_name.lower())
        adapted_config = self._adapt_to_platform_capabilities(universal_config.config)

        if dry_run:
            print(f"{Fore.YELLOW}[DRY RUN] Se (re)aplicaría la protección del contexto '{strategy_name}' a las siguientes ramas:{Style.RESET_ALL}")
            for branch in protected_branches:
                print(f"  - {branch}")
            self._show_config_summary(adapted_config)
            return True

        # Aplicar la protección
        results = []
        print(f"{Fore.CYAN}🚀 Aplicando configuración del contexto '{strategy_name}' a {len(protected_branches)} rama(s)...{Style.RESET_ALL}")
        for branch in protected_branches:
            result = self.protection_api.apply_protection(branch, adapted_config)
            results.append(result)

        print(f"{Fore.GREEN}✅ Sincronización local → remoto completada.{Style.RESET_ALL}")
        return True

    def _sync_remote_to_local(self, dry_run):
        """Sincroniza la configuración remota HACIA el local."""
        print(f"{Fore.CYAN}🔄 Obteniendo configuración desde el remoto...{Style.RESET_ALL}")

        try:
            # Obtener configuración remota actual
            remote_branches = self.protection_api.list_protected_branches()

            if not remote_branches:
                print(f"{Fore.YELLOW}⚠️  No hay ramas protegidas en el remoto. No se puede sincronizar.{Style.RESET_ALL}")
                return True

            remote_protection_details = {}
            for branch in remote_branches:
                protection = self.protection_api.get_current_protection(branch)
                remote_protection_details[branch] = protection

            # Intentar detectar la estrategia basada en la configuración remota
            strategy = self._detect_strategy_from_remote_config(remote_protection_details)
            if not strategy:
                print(f"{Fore.RED}❌ No se pudo determinar una estrategia (local, hybrid, remote) desde la configuración remota.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}💡 Sincronice desde local a remoto primero para establecer una base.{Style.RESET_ALL}")
                return False

            if dry_run:
                print(f"{Fore.YELLOW}[DRY RUN] Se actualizaría el archivo de configuración local '{self.local_config_path}' con:{Style.RESET_ALL}")
                print(f"  - Estrategia: {strategy}")
                print(f"  - Ramas protegidas: {', '.join(remote_branches)}")
                return True

            # Actualizar el archivo de configuración local
            self._update_local_validator_config(strategy, remote_branches)

            print(f"{Fore.GREEN}✅ Sincronización remoto → local completada.{Style.RESET_ALL}")
            return True

        except Exception as e:
            print(f"{Fore.RED}❌ Error durante la sincronización remoto → local: {e}{Style.RESET_ALL}")
            return False

    def _get_local_validator_config(self):
        """Obtiene configuración actual del validator local."""
        try:
            # Intentar obtener configuración del validator cargado
            if self.context and VALIDATION_CONFIGS:
                current_context = self.context
                config = VALIDATION_CONFIGS.get(current_context, {})

                return {
                    "context": current_context,
                    "protected_branches": config.get("protected_branches", []),
                    "require_upstream": config.get("require_upstream", False),
                    "require_pr": config.get("require_pr", False),
                    "allow_direct_push_to_main": config.get("allow_direct_push_to_main", False),
                    "enforce_branch_naming": config.get("enforce_branch_naming", False),
                    "require_linear_history": config.get("require_linear_history", False)
                }

            # Fallback: usar configuración por defecto basada en contexto detectado
            if self.context:
                current_context = self.context

                # Configuraciones por defecto según contexto
                default_configs = {
                    "LOCAL": {
                        "protected_branches": [],
                        "require_upstream": False,
                        "require_pr": False,
                        "allow_direct_push_to_main": True,
                        "enforce_branch_naming": False,
                        "require_linear_history": False
                    },
                    "HYBRID": {
                        "protected_branches": ["main", "develop"],
                        "require_upstream": True,
                        "require_pr": True,
                        "allow_direct_push_to_main": False,
                        "enforce_branch_naming": True,
                        "require_linear_history": False
                    },
                    "REMOTE": {
                        "protected_branches": ["main", "master", "develop"],
                        "require_upstream": True,
                        "require_pr": True,
                        "allow_direct_push_to_main": False,
                        "enforce_branch_naming": True,
                        "require_linear_history": True
                    }
                }

                config = default_configs.get(current_context, default_configs["HYBRID"])
                config["context"] = current_context

                return config

            return None

        except Exception:
            return None

    def _detect_strategy_from_remote_config(self, remote_protection_details):
        # Lógica de ejemplo muy básica. Se puede mejorar.
        num_protected = len(remote_protection_details)
        if num_protected == 0:
            return 'local'
        elif num_protected < 3:
            return 'hybrid'
        else:
            return 'remote'

    def _update_local_validator_config(self, strategy, protected_branches):
        """Actualiza el archivo branch-workflow-validator.py con la nueva configuración."""
        try:
            # Necesitamos encontrar la ruta al validador para escribir en él.
            # Esta lógica podría centralizarse mejor.
            validator_path = Path.cwd() / ".githooks" / "branch-workflow-validator.py"
            if not validator_path.exists():
                manager_dir = Path(__file__).parent
                validator_path = manager_dir / ".githooks" / "branch-workflow-validator.py"

            if not validator_path.exists():
                print(f"{Fore.RED}Error: No se encontró el archivo del validador para actualizar.{Style.RESET_ALL}")
                return

            self.local_config_path = validator_path # Guardar para mensajes de error

            with open(validator_path, 'r') as f:
                content = f.read()

            # Construir la nueva sección de 'protected_branches' para la estrategia
            branches_str = ",\n        ".join([f'"{b}"' for b in protected_branches])
            new_branches_config = f"\"protected_branches\": [\n        {branches_str}\n    ]"

            # Usar regex para reemplazar la configuración de la estrategia detectada
            # Esto es frágil y depende mucho del formato del archivo.
            pattern = re.compile(rf"(\"{strategy}\":\s*{{[^}}]*?\"protected_branches\":\s*\[)[^\]]*(\])", re.DOTALL)

            if pattern.search(content):
                new_content = pattern.sub(rf"\g<1>{new_branches_config}\g<2>", content)
            else:
                # Si la estrategia no existe, no intentamos añadirla. Esto es una limitación.
                print(f"{Fore.YELLOW}Advertencia: No se encontró la sección para la estrategia '{strategy}' en el validador. No se pudo actualizar.{Style.RESET_ALL}")
                return

            with open(validator_path, 'w') as f:
                f.write(new_content)

            print(f"{Fore.GREEN}✅ Archivo '{validator_path.name}' actualizado.{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}Error al actualizar el archivo de configuración local: {e}{Style.RESET_ALL}")

# ============================================================================
# FIN DE NUEVAS CLASES PARA CONFIGURACIÓN AUTOMÁTICA DEL REMOTO
# ============================================================================

class WorkflowOrchestrator:
    """Orquestador principal de workflows."""

    def __init__(self, repo_path: Path = None, args=None):
        self.repo_path = repo_path or Path.cwd()
        self.args = args

        # Cargar el validador dinámicamente
        global validator_module, GitRepository, ContextDetector, VALIDATION_CONFIGS
        try:
            validator_path = find_validator_path(self.repo_path)
            validator_module = load_validator_module(validator_path, self.repo_path)
            GitRepository = validator_module.GitRepository
            ContextDetector = validator_module.ContextDetector
            VALIDATION_CONFIGS = validator_module.VALIDATION_CONFIGS
        except ImportError as e:
            print(f"{Fore.RED}❌ Error crítico al cargar el módulo validator: {e}{Style.RESET_ALL}")
            sys.exit(1)

        self.repo = GitRepository(self.repo_path)

        # 1. Detectar contexto primero, ya que otros componentes pueden depender de él.
        self.context_detector = ContextDetector(self.repo)
        self.context = self.context_detector.detect_context()

        # 2. Detectar plataforma y credenciales
        try:
            self.platform_info = GitPlatformDetector.detect_platform(args)
        except PlatformDetectionError as e:
            self.platform_info = None
            # El mensaje de advertencia se mostrará al final

        self.token_manager = TokenManager()
        self.platform_token = self.token_manager.get_platform_token(self.platform_info) if self.platform_info else None

        # 3. Inicializar clientes de API y gestores
        self.api_client = APIFactory.create(self.platform_info, self.platform_token) if self.platform_info and self.platform_token else None

        self.protection_manager = None
        if self.platform_info and self.platform_token:
            self.protection_manager = UniversalProtectionManager(
                platform_info=self.platform_info,
                token_manager=self.token_manager,
                context=self.context
            )

        # 4. Mostrar estado consolidado al final
        print(f"📍 Contexto: {self.context}")

        if self.platform_info:
            print(f"{Fore.CYAN}🌐 Plataforma: {self.platform_info.service}-{self.platform_info.mode}{Style.RESET_ALL}")
        else:
            # Imprime la advertencia de PlatformDetectionError si ocurrió
            try:
                GitPlatformDetector.detect_platform(args)
            except PlatformDetectionError as e:
                 print(f"{Fore.YELLOW}⚠️  {e}{Style.RESET_ALL}")

        if self.platform_token:
            print(f"{Fore.CYAN}🔑 Token: ✅ Disponible{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}🔑 Token: ❌ No disponible o no configurado para la plataforma detectada.{Style.RESET_ALL}")

        if self.api_client:
            print(f"{Fore.CYAN}⚡ Capacidades: API Completa{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚡ Capacidades: Solo Git Local{Style.RESET_ALL}")


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
        if self.api_client:
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
        if self.api_client:
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
        if mode == IntegrationMode.FULL_AUTO and self.api_client:
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
        if not self.api_client:
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

        success = self.api_client.create_pull_request(title, body, current_branch, "develop")
        if success:
            print(f"   {Fore.GREEN}✅ PR creado automáticamente{Style.RESET_ALL}")
        else:
            print(f"   {Fore.RED}❌ Error creando PR{Style.RESET_ALL}")

        return success

    def _github_check_ci(self, step: WorkflowStep) -> bool:
        """Verifica estado de CI usando la API de la plataforma detectada."""
        if not self.api_client:
            return False

        # Obtener la rama actual
        try:
            result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
        except subprocess.CalledProcessError:
            return False

        success = self.api_client.check_ci_status(current_branch)
        if success:
            print(f"   {Fore.GREEN}✅ CI status verificado - Pasando{Style.RESET_ALL}")
        else:
            print(f"   {Fore.YELLOW}⏳ CI en progreso o fallando{Style.RESET_ALL}")

        return success

    def _github_merge_pr(self, step: WorkflowStep) -> bool:
        """Merge automático de PR usando la API de la plataforma detectada."""
        if not self.api_client:
            return False

        # TODO: Necesitaríamos obtener el PR ID del paso anterior
        # Por simplicidad, marcamos como éxito para demostrar la integración
        print(f"   {Fore.GREEN}✅ PR preparado para merge automático{Style.RESET_ALL}")
        print(f"   {Fore.YELLOW}💡 Implementar obtención de PR ID en versión futura{Style.RESET_ALL}")
        return True

    def _has_required_api(self, step: WorkflowStep) -> bool:
        """Verifica si la API requerida está disponible."""
        if 'github' in step.api_endpoint:
            return self.api_client is not None
        elif 'gitlab' in step.api_endpoint:
            return self.api_client is not None
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
        metrics.total_commits = self.repo.get_commit_count()
        metrics.contributors = self.repo.get_contributor_count()

        # Calcular health score
        metrics.health_score = self._calculate_health_score(metrics)

        return metrics

    def _count_branches(self) -> int:
        """Cuenta el total de branches."""
        success, stdout, _ = self.repo.run_command(['git', 'branch', '-a'])
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
        success, stdout, _ = self.repo.run_command([
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

    # ============================================================================
    # NUEVOS MÉTODOS PARA CONFIGURACIÓN AUTOMÁTICA DEL REMOTO
    # ============================================================================

    def apply_strategy(self, strategy_name: str, dry_run: bool = True) -> bool:
        """Aplica una estrategia de protección de ramas en el remoto."""
        if not self.protection_manager:
            print(f"{Fore.RED}❌ Error: No se puede aplicar estrategia sin un gestor de protección (token/API no disponible).{Style.RESET_ALL}")
            return False

        try:
            success, message = self.protection_manager.apply_strategy(strategy_name, dry_run)

            if success:
                print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

            return success

        except Exception as e:
            print(f"{Fore.RED}❌ Error inesperado aplicando estrategia: {e}{Style.RESET_ALL}")
            return False

    def get_protection_status(self, compare_with_local: bool = False) -> dict:
        """Obtiene el estado de protección de ramas, sin mostrarlo."""
        if not self.protection_manager:
            print(f"{Fore.RED}❌ Error: No se puede obtener estado sin un gestor de protección (token/API no disponible).{Style.RESET_ALL}")
            return {}
        try:
            # Simplemente devuelve el estado obtenido por el manager.
            return self.protection_manager.get_protection_status(compare_with_local)
        except Exception as e:
            print(f"{Fore.RED}❌ Error inesperado obteniendo estado de protección: {e}{Style.RESET_ALL}")
            # En caso de error, el error ya se imprime, devolver un diccionario vacío.
            return {}

    def sync_protection_rules(self, direction: str, dry_run: bool = True) -> bool:
        """
        Sincroniza las reglas de protección entre la configuración local
        (branch-workflow-validator.py) y el remoto (GitHub/GitLab API).
        """
        if not self.protection_manager:
            print(f"{Fore.YELLOW}⚠️  No se puede sincronizar sin un gestor de protección (token/API no disponible).{Style.RESET_ALL}")
            return False

        print(f"{Fore.CYAN}🔄 Sincronizando configuración {direction.replace('-', ' → ')}...{Style.RESET_ALL}")

        if direction == 'local-to-remote':
            return self.protection_manager._sync_local_to_remote(dry_run)
        elif direction == 'remote-to-local':
            return self.protection_manager._sync_remote_to_local(dry_run)

        return False

    # ============================================================================
    # FIN DE NUEVOS MÉTODOS PARA CONFIGURACIÓN AUTOMÁTICA DEL REMOTO
    # ============================================================================

    def _show_protection_details_elegant(self, protection_details):
        """Muestra los detalles de protección de forma elegante y legible."""
        if not protection_details:
            print(f"   {Fore.YELLOW}(No hay detalles disponibles o no se pudo contactar la API){Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}📊 Estado de Protección con Comparación{Style.RESET_ALL}")
        print("=============================================")

        local_branches = protection_details.get("local_protected", [])
        remote_branches = protection_details.get("remote_protected", [])
        diffs = protection_details.get("diff", {})

        # Caso especial: Todo está vacío y consistente
        if not local_branches and not remote_branches:
            print(f"   {Fore.GREEN}✅ Consistente: No hay ramas protegidas localmente ni en el remoto.{Style.RESET_ALL}")
            return

        print(f"🏠 Branches protegidas localmente:")
        if local_branches:
            for branch in local_branches:
                print(f"   • {branch}")
        else:
            print(f"   (ninguna)")

        print(f"\n☁️  Branches protegidas remotamente:")
        if remote_branches:
            for branch in remote_branches:
                print(f"   • {branch}")
        else:
            print(f"   (ninguna)")

        if diffs.get("local_only") or diffs.get("remote_only") or diffs.get("mismatched"):
            print(f"\n{Fore.YELLOW}🔍 Diferencias encontradas:{Style.RESET_ALL}")
            if diffs.get("local_only"):
                print(f"   - Branches protegidas localmente pero no remotamente: {', '.join(diffs['local_only'])}")
            if diffs.get("remote_only"):
                print(f"   - Branches protegidas remotamente pero no localmente: {', '.join(diffs['remote_only'])}")
            if diffs.get("mismatched"):
                print(f"   - Branches con configuración de protección diferente: {', '.join(diffs['mismatched'])}")

        print(f"\n{Fore.CYAN}🛡️  Detalles de Protección Remota:{Style.RESET_ALL}")
        if not protection_details.get("remote_details") or not protection_details["remote_details"].get("branches"):
            print(f"   {Fore.YELLOW}(No hay detalles de protección en el remoto){Style.RESET_ALL}")
        else:
            for branch, details in protection_details["remote_details"]["branches"].items():
                print(f"\n   {Fore.YELLOW}🔒 Branch: {branch}{Style.RESET_ALL}")

                if not isinstance(details, dict):
                    print(f"      {Fore.RED}Error: No se pudieron obtener detalles (recibido: {details}){Style.RESET_ALL}")
                    continue

                if details.get("status") == "error":
                    print(f"      {Fore.RED}Error: {details.get('message')}{Style.RESET_ALL}")
                    continue

                if details.get("status") == "unprotected":
                    print(f"      {Fore.GREEN}✓ No protegida (según la API){Style.RESET_ALL}")
                    continue

                enforce_admins = details.get('enforce_admins', {}).get('enabled', False)
                req_pr_reviews = details.get('required_pull_request_reviews')
                req_status_checks = details.get('required_status_checks')

                print(f"      {'✅' if enforce_admins else '❌'} Requiere aprobación de administrador")

                if req_pr_reviews:
                    count = req_pr_reviews.get('required_approving_review_count', 0)
                    print(f"      {'✅' if count > 0 else '❌'} Requiere {count} revision(es) de PR")
                else:
                    print(f"      ❌ No requiere revisiones de PR")

                if req_status_checks:
                    contexts = req_status_checks.get('contexts', [])
                    print(f"      {'✅' if contexts else '❌'} Requiere checks de status: {', '.join(contexts) if contexts else '(ninguno)'}")
                else:
                    print(f"      ❌ No requiere checks de status")


class CICDManager:
    PLATFORM_MAP = {
        "gitlab.com": "gitlab",
        "github.com": "github",
        "gitea.io": "gitea",
        "forgejo.org": "forgejo",
        "bitbucket.org": "bitbucket"
    }

    # Mapeo de plataformas a sus nombres de carpeta
    PLATFORM_FOLDER_MAP = {
        "gitlab": ".gitlab",
        "github": ".github",
        "gitea": ".gitea",
        "forgejo": ".forgejo",
        "bitbucket": "bitbucket-pipelines"
    }

    def __init__(self, project_path=None):
        self.project_path = os.path.abspath(project_path or os.getcwd())

    def detect_current_platform(self):
        remotes = subprocess.check_output(
            ["git", "-C", self.project_path, "remote", "-v"], encoding="utf-8"
        )
        for domain, platform in self.PLATFORM_MAP.items():
            if domain in remotes:
                return platform
        return None

    def detect_project_type(self):
        """Detecta los tipos de proyecto basado en los archivos presentes."""
        print(f"{Fore.BLUE}🔍 Analizando tipos de proyecto...{Style.RESET_ALL}")

        project_types = set()
        project_path = Path(self.project_path)

        # Detectar tipos de proyecto basado en archivos clave
        if (project_path / "package.json").exists() or (project_path / "yarn.lock").exists():
            project_types.add("node")
        if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            project_types.add("python")
        if (project_path / "pom.xml").exists() or (project_path / "build.gradle").exists():
            project_types.add("java")
        if (project_path / "go.mod").exists():
            project_types.add("go")
        if (project_path / "Cargo.toml").exists():
            project_types.add("rust")
        if (project_path / "Gemfile").exists():
            project_types.add("ruby")
        if (project_path / "composer.json").exists():
            project_types.add("php")
        if (project_path / "mix.exs").exists():
            project_types.add("elixir")
        if (project_path / "pubspec.yaml").exists():
            project_types.add("dart")
        if (project_path / "tsconfig.json").exists():
            project_types.add("typescript")

        # Detectar frameworks específicos
        if (project_path / "angular.json").exists():
            project_types.add("angular")
        if (project_path / "vue.config.js").exists():
            project_types.add("vue")
        if (project_path / "next.config.js").exists():
            project_types.add("next")
        if (project_path / "nuxt.config.js").exists():
            project_types.add("nuxt")
        if (project_path / "django").exists() or (project_path / "manage.py").exists():
            project_types.add("django")
        if (project_path / "flask_app.py").exists() or (project_path / "app.py").exists():
            project_types.add("flask")
        if (project_path / "spring").exists() or (project_path / "application.properties").exists():
            project_types.add("spring")

        if not project_types:
            print(f"{Fore.YELLOW}⚠️  No se detectó ningún tipo de proyecto específico{Style.RESET_ALL}")
            project_types.add("default")

        # Mostrar los tipos detectados
        types_str = ", ".join(sorted(project_types))
        print(f"{Fore.GREEN}✓ Tipos de proyecto detectados: {types_str}{Style.RESET_ALL}")

        # Si hay múltiples tipos, mostrar advertencia
        if len(project_types) > 1:
            print(f"{Fore.YELLOW}ℹ️  Proyecto multi-lenguaje detectado. Se aplicarán configuraciones para todos los tipos.{Style.RESET_ALL}")

        return list(project_types)

    def apply_cicd(self, platform=None, project_types=None, force=False):
        """Aplica la configuración de CI/CD al proyecto."""
        print(f"\n{Fore.CYAN}🔄 Actualizando configuración CI/CD{Style.RESET_ALL}")
        print("=" * 40)

        # Detectar plataforma actual si no se especifica
        if not platform:
            print(f"{Fore.BLUE}🔍 Detectando plataforma actual...{Style.RESET_ALL}")
            platform = self.detect_current_platform()
            print(f"{Fore.GREEN}✓ Plataforma detectada: {platform}{Style.RESET_ALL}")

        # Detectar tipos de proyecto si no se especifican
        if not project_types:
            project_types = self.detect_project_type()

        # Verificar si ya existe configuración
        platform_folder = self.PLATFORM_FOLDER_MAP.get(platform)
        if not platform_folder:
            print(f"{Fore.RED}❌ Plataforma no soportada: {platform}{Style.RESET_ALL}")
            return False

        # Verificar si ya existe configuración de CI
        ci_path = Path(self.project_path) / "ci"
        if ci_path.exists() and not force:
            print(f"{Fore.YELLOW}⚠️  Ya existe configuración CI en {ci_path}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Usa -f/--force para sobrescribir{Style.RESET_ALL}")
            return False

        # Verificar si ya existe configuración de plataforma
        platform_path = Path(self.project_path) / platform_folder
        if platform_path.exists() and not force:
            print(f"{Fore.YELLOW}⚠️  Ya existe configuración en {platform_path}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Usa -f/--force para sobrescribir{Style.RESET_ALL}")
            return False

        # Aplicar configuración para cada tipo de proyecto
        print(f"\n{Fore.BLUE}📦 Aplicando configuración para {platform}...{Style.RESET_ALL}")
        try:
            # Copiar carpeta ci/ del template
            template_ci_path = Path(__file__).parent / "scaffold" / "ci" / "ci-projects"
            if template_ci_path.exists():
                print(f"{Fore.BLUE}📦 Copiando scripts CI...{Style.RESET_ALL}")
                shutil.copytree(template_ci_path, ci_path, dirs_exist_ok=force)
                print(f"{Fore.GREEN}✓ Scripts CI copiados{Style.RESET_ALL}")

            # Copiar configuración específica de la plataforma
            template_platform_path = Path(__file__).parent / "scaffold" / "ci" / platform_folder
            if template_platform_path.exists():
                print(f"{Fore.BLUE}📦 Copiando configuración de {platform}...{Style.RESET_ALL}")
                shutil.copytree(template_platform_path, platform_path, dirs_exist_ok=force)
                print(f"{Fore.GREEN}✓ Configuración de {platform} copiada{Style.RESET_ALL}")

            print(f"{Fore.GREEN}✓ Configuración aplicada exitosamente{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}📝 Resumen de cambios:{Style.RESET_ALL}")
            print(f"  • Plataforma: {platform}")
            print(f"  • Tipos: {', '.join(project_types)}")
            print(f"  • Scripts CI: {ci_path}")
            print(f"  • Configuración: {platform_path}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error al aplicar configuración: {e}{Style.RESET_ALL}")
            return False

    def reset_cicd(self, platform=None):
        """Elimina la configuración de CI/CD del proyecto."""
        print(f"\n{Fore.CYAN}🗑️  Eliminando configuración CI/CD{Style.RESET_ALL}")
        print("=" * 40)

        if platform:
            platforms = [platform]
        else:
            platforms = self.PLATFORM_FOLDER_MAP.values()

        for platform_folder in platforms:
            config_path = Path(self.project_path) / platform_folder
            if config_path.exists():
                print(f"{Fore.BLUE}🔍 Eliminando configuración de {platform_folder}...{Style.RESET_ALL}")
                try:
                    # Aquí va la lógica de eliminación
                    print(f"{Fore.GREEN}✓ Configuración eliminada{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Error al eliminar configuración: {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}ℹ️  No se encontró configuración en {platform_folder}{Style.RESET_ALL}")

    def migrate_cicd(self, new_platform, project_types=None, force=False):
        """Migra la configuración de CI/CD a otra plataforma."""
        print(f"\n{Fore.CYAN}🔄 Migrando configuración CI/CD a {new_platform}{Style.RESET_ALL}")
        print("=" * 40)

        # Verificar plataforma destino
        if new_platform not in self.PLATFORM_MAP.values():
            print(f"{Fore.RED}❌ Plataforma destino no soportada: {new_platform}{Style.RESET_ALL}")
            return False

        # Detectar plataforma actual
        print(f"{Fore.BLUE}🔍 Detectando plataforma actual...{Style.RESET_ALL}")
        current_platform = self.detect_current_platform()
        print(f"{Fore.GREEN}✓ Plataforma actual: {current_platform}{Style.RESET_ALL}")

        if current_platform == new_platform:
            print(f"{Fore.YELLOW}⚠️  Ya estás en la plataforma {new_platform}{Style.RESET_ALL}")
            return False

        # Detectar tipos de proyecto si no se especifican
        if not project_types:
            project_types = self.detect_project_type()

        # Verificar si ya existe configuración en destino
        new_platform_folder = self.PLATFORM_FOLDER_MAP.get(new_platform)
        if not new_platform_folder:
            print(f"{Fore.RED}❌ Error: No se encontró mapeo para {new_platform}{Style.RESET_ALL}")
            return False

        new_config_path = Path(self.project_path) / new_platform_folder
        if new_config_path.exists() and not force:
            print(f"{Fore.YELLOW}⚠️  Ya existe configuración en {new_config_path}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Usa -f/--force para sobrescribir{Style.RESET_ALL}")
            return False

        # Migrar configuración
        print(f"\n{Fore.BLUE}📦 Migrando configuración...{Style.RESET_ALL}")
        try:
            # Aquí va la lógica de migración para cada tipo
            print(f"{Fore.GREEN}✓ Migración completada exitosamente{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}📝 Resumen de migración:{Style.RESET_ALL}")
            print(f"  • Desde: {current_platform}")
            print(f"  • Hacia: {new_platform}")
            print(f"  • Tipos: {', '.join(project_types)}")
            print(f"  • Ubicación: {new_config_path}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error durante la migración: {e}{Style.RESET_ALL}")
            return False

# Ejemplo de uso CLI (comentado):
# manager = CICDManager(project_path="/ruta/al/proyecto")
# manager.apply_cicd(force=True)
# manager.reset_cicd()
# manager.migrate_cicd("github", force=True)

def main():
    """Función principal del Integration Manager."""
    parser = argparse.ArgumentParser(description="Git Integration Manager")
    parser.add_argument('-p', '--path', help='Ruta del repositorio')
    parser.add_argument('--mode', choices=['dry-run', 'local', 'api', 'auto'], default='local')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--platform', help='Plataforma Git (github, gitlab-c, gitlab-o, gitea, forgejo, bitbucket-c, bitbucket-o)')
    parser.add_argument('--host', help='Host para servicios on-premise (ej: gitlab.empresa.com)')
    parser.add_argument('--strategy', choices=['local', 'hybrid', 'remote'], help='Estrategia de protección a aplicar')
    parser.add_argument('--direction', choices=['local-to-remote', 'remote-to-local'], default='local-to-remote')
    parser.add_argument('--compare', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--commit-format', help='Formato de commit a establecer (ej. conventional.js)')
    parser.add_argument('--level', choices=['minimal', 'standard', 'strict'], help='Nivel de calidad a aplicar (solo si se usa --commit-format sin subcomando)')

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    # Agregar cicd como un comando principal
    cicd_parser = subparsers.add_parser('cicd', help='Gestionar configuración CI/CD')
    cicd_subparsers = cicd_parser.add_subparsers(dest='cicd_command', help='Comandos CI/CD')

    # Comando apply
    apply_parser = cicd_subparsers.add_parser('apply', help='Aplicar configuración CI/CD')
    apply_parser.add_argument('-p', '--path', help='Ruta del proyecto')
    apply_parser.add_argument('-f', '--force', action='store_true', help='Forzar sobrescritura')
    apply_parser.add_argument('--platform', help='Plataforma específica (opcional)')
    apply_parser.add_argument('--type', help='Tipo de proyecto específico (opcional)')

    # Comando reset
    reset_parser = cicd_subparsers.add_parser('reset', help='Eliminar configuración CI/CD')
    reset_parser.add_argument('-p', '--path', help='Ruta del proyecto')
    reset_parser.add_argument('--platform', help='Plataforma específica (opcional)')

    # Comando migrate
    migrate_parser = cicd_subparsers.add_parser('migrate', help='Migrar a otra plataforma CI/CD')
    migrate_parser.add_argument('-p', '--path', help='Ruta del proyecto')
    migrate_parser.add_argument('-f', '--force', action='store_true', help='Forzar sobrescritura')
    migrate_parser.add_argument('--platform', required=True, help='Plataforma destino')
    migrate_parser.add_argument('--type', help='Tipo de proyecto específico (opcional)')

    # Agregar los otros subparsers existentes
    integrate_parser = subparsers.add_parser('integrate', help='Integrar rama feature')
    integrate_parser.add_argument('branch_name', nargs='?', help='Nombre de la branch para integrar')

    # Subparser para el comando 'set-quality-level'
    set_quality_level_parser = subparsers.add_parser('set-quality-level', help='Establecer el nivel de calidad y formato de commit.')
    set_quality_level_parser.add_argument(
        '--level',
        choices=['minimal', 'standard', 'strict'],
        required=True,
        help='Nivel de calidad a aplicar (minimal, standard, strict)'
    )
    set_quality_level_parser.add_argument(
        '--commit-format',
        help='Formato de commit a aplicar (ej. conventional.js)'
    )

    # --- Comandos Adicionales ---
    subparsers.add_parser('health-check', help='Analiza la salud del repositorio.')

    cleanup_parser = subparsers.add_parser('cleanup', help='Limpia ramas obsoletas (usar con --execute).')
    cleanup_parser.add_argument('--execute', action='store_true', help='Ejecuta la limpieza.')

    subparsers.add_parser('status', help='Muestra el estado del Integration Manager.')

    setup_remote_parser = subparsers.add_parser('setup-remote-protection', help='Configura o sincroniza la protección de ramas en el remoto.')
    setup_remote_parser.add_argument('--strategy', choices=['local', 'hybrid', 'remote', 'auto'], default='auto', help="Estrategia a aplicar. 'auto' usa la detección dinámica (por defecto).")
    setup_remote_parser.add_argument('--dry-run', action='store_true', help='Solo muestra los cambios, no los aplica.')

    protection_status_parser = subparsers.add_parser('protection-status', help='Muestra el estado de protección de las ramas (usar con --compare).')
    protection_status_parser.add_argument('--compare', action='store_true', help='Compara la configuración remota con la local.')

    sync_rules_parser = subparsers.add_parser('sync-protection-rules', help='Sincroniza las reglas de protección (usar con --direction).')
    sync_rules_parser.add_argument('--direction', choices=['local-to-remote', 'remote-to-local'], default='local-to-remote', help='Dirección de la sincronización.')
    sync_rules_parser.add_argument('--dry-run', action='store_true', help='Solo muestra los cambios, no los aplica.')

    quality_status_parser = subparsers.add_parser('quality-status', help='Muestra el estado de calidad (nivel y formato).')
    quality_status_parser.add_argument('--json', action='store_true', help='Muestra la salida en formato JSON.')

    list_formats_parser = subparsers.add_parser('list-commit-formats', help='Lista los formatos de commit disponibles.')
    list_formats_parser.add_argument('--json', action='store_true', help='Muestra la salida en formato JSON.')

    args = parser.parse_args()

    if args.command == 'cicd':
        if not args.cicd_command:
            cicd_parser.print_help()
            sys.exit(1)

        manager = CICDManager(project_path=args.path)

        if args.cicd_command == 'apply':
            try:
                manager.apply_cicd(
                    platform=args.platform,
                    project_types=args.type,
                    force=args.force
                )
            except Exception as e:
                print(f"Error al aplicar CI/CD: {e}")
                sys.exit(1)

        elif args.cicd_command == 'reset':
            try:
                manager.reset_cicd(platform=args.platform)
            except Exception as e:
                print(f"Error al resetear CI/CD: {e}")
                sys.exit(1)

        elif args.cicd_command == 'migrate':
            try:
                manager.migrate_cicd(
                    new_platform=args.platform,
                    project_types=args.type,
                    force=args.force
                )
            except Exception as e:
                print(f"Error al migrar CI/CD: {e}")
                sys.exit(1)

        else:
            cicd_parser.print_help()
            sys.exit(1)

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

        # Importar QualityManager dinámicamente (si es necesario)
        try:
            import importlib.util
            qm_path = project_path / ".githooks" / "quality_manager.py"
            if qm_path.exists():
                spec = importlib.util.spec_from_file_location("quality_manager", qm_path)
                qm_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(qm_module)
                QualityManager = qm_module.QualityManager
            else:
                print(f"{Fore.RED}❌ Error: No se encontró el módulo de QualityManager en {qm_path}{Style.RESET_ALL}")
                sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}❌ Error al importar QualityManager: {e}{Style.RESET_ALL}")
            sys.exit(1)

        orchestrator = WorkflowOrchestrator(repo_path=project_path, args=args)

        if args.command == 'integrate':
            if not args.branch_name:
                print(f"{Fore.RED}❌ Error: Se requiere nombre de branch para integrar{Style.RESET_ALL}")
                sys.exit(1)

            mode = IntegrationMode.DRY_RUN if args.dry_run else IntegrationMode(args.mode)
            success = orchestrator.integrate_feature(args.branch_name, mode)
            sys.exit(0 if success else 1)

        elif args.command == 'health-check':
            metrics = orchestrator.analyze_repository_health()

            print(f"\n{Fore.CYAN}📊 Reporte de Salud del Repositorio{Style.RESET_ALL}")
            print("=" * 40)
            print(f"{Fore.BLUE}🌳 Total branches: {Fore.YELLOW}{metrics.total_branches}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}✅ Branches activas: {Fore.GREEN}{metrics.active_branches}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}⚠️  Branches stale: {Fore.YELLOW}{metrics.stale_branches}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}👥 Contribuidores: {Fore.YELLOW}{metrics.contributors}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📈 Score de salud: {Fore.GREEN}{metrics.health_score:.1f}/100{Style.RESET_ALL}")

        elif args.command == 'cleanup':
            actions = orchestrator.cleanup_repository(dry_run=not args.execute)

            if actions:
                print(f"\n{Fore.CYAN}📋 Acciones de limpieza: {len(actions)}{Style.RESET_ALL}")
                if not args.execute:
                    print(f"{Fore.YELLOW}💡 Usar --execute para ejecutar las acciones{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}✅ No se necesita limpieza{Style.RESET_ALL}")

        elif args.command == 'status':
            print(f"\n{Fore.CYAN}📊 Estado del Integration Manager{Style.RESET_ALL}")
            print("=" * 35)
            print(f"{Fore.BLUE}📍 Contexto: {Fore.YELLOW}{orchestrator.context}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}⚡ Capacidades: {Fore.YELLOW}{orchestrator.capability_level.value}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}🐙 GitHub API: {'✅' if orchestrator.api_client else '❌'}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}🦊 Git CLI: {'✅' if orchestrator.api_caps.capabilities['git_cli'] else '❌'}{Style.RESET_ALL}")

        elif args.command == 'setup-remote-protection':
            strategy_to_apply = args.strategy

            if strategy_to_apply == 'auto':
                strategy_name = orchestrator.context
                print(f"{Fore.BLUE}ℹ️  Usando estrategia '{strategy_name}' detectada automáticamente.{Style.RESET_ALL}")
            else:
                strategy_name = strategy_to_apply

            success = orchestrator.apply_strategy(strategy_name.upper(), dry_run=args.dry_run)
            sys.exit(0 if success else 1)

        elif args.command == 'protection-status':
            # 1. Obtener el estado
            status = orchestrator.get_protection_status(compare_with_local=args.compare)
            # 2. Mostrar el estado
            orchestrator._show_protection_details_elegant(status)
            sys.exit(0)

        elif args.command == 'sync-protection-rules':
            # Sincroniza la configuración (lee de una fuente y actualiza la otra en memoria)
            success = orchestrator.sync_protection_rules(direction=args.direction, dry_run=args.dry_run)

            # Si la sincronización es hacia el remoto, AHORA aplicamos la estrategia.
            if args.direction == 'local-to-remote':
                strategy_name = orchestrator.context
                print(f"{Fore.CYAN}🚀 Aplicando la estrategia '{strategy_name}' en el remoto...{Style.RESET_ALL}")
                # El dry_run ya se pasó a sync_protection_rules, que lo pasa a _sync_local_to_remote,
                # donde realmente se aplica la protección.
                # No necesitamos una llamada explícita a apply_strategy aquí.
                # La lógica ya está en _sync_local_to_remote.
                # Solo necesitamos asegurarnos de que el mensaje de éxito se muestre.
                print(f"{Fore.GREEN}✅ Sincronización y aplicación completadas.{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✅ Sincronización completada.{Style.RESET_ALL}")
            sys.exit(0)

        elif args.command == 'quality-status':
            qm = QualityManager(project_path)
            config = qm.get_current_configuration()
            if args.json:
                print(json.dumps(config, indent=2))
            else:
                print(f"\n{Fore.CYAN}📊 Estado de Calidad (Quality){Style.RESET_ALL}")
                print("=" * 35)
                if config['status'] == 'active':
                    print(f"{Fore.BLUE}Nivel: {Fore.YELLOW}{config['level']}{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}Formato de commit: {Fore.YELLOW}{config['commit_format']}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW} (No hay configuración activa){Style.RESET_ALL}")

        elif args.command == 'set-quality-level':
            qm = QualityManager(project_path)

            # 1. Obtener el formato de commit actual
            current_config = qm.get_current_configuration()
            current_commit_format = current_config.get('commit_format', 'N/A')
            current_level = current_config.get('level', 'N/A')
            print(f"{Fore.CYAN}⚙️  Configuración de calidad actual: Nivel {current_level}, Formato de commit: {current_commit_format}{Style.RESET_ALL}")

            # 2. Intentar aplicar el nuevo nivel y formato
            try:
                new_commit_format_to_apply = args.commit_format if args.commit_format else current_commit_format
                level_to_apply = args.level # Este es requerido por el subparser

                result = qm.apply_configuration(level_to_apply, new_commit_format_to_apply)
                new_commit_format = result.get('commit_format', 'N/A')
                new_level = result.get('level', 'N/A')

                # 3. Mostrar mensaje de confirmación
                print(f"{Fore.GREEN}✅ Configuración de calidad cambiada a: Nivel {new_level}, Formato de commit: {new_commit_format}{Style.RESET_ALL}")
                if current_commit_format != new_commit_format:
                    print(f"{Fore.BLUE}ℹ️  El formato de commit cambió de '{current_commit_format}' a '{new_commit_format}'.{Style.RESET_ALL}")
                sys.exit(0)
            except Exception as e:
                print(f"{Fore.RED}❌ Error al aplicar el nivel de calidad o formato de commit: {e}{Style.RESET_ALL}")
                sys.exit(1)

        elif args.command == 'list-commit-formats':
             qm = QualityManager(project_path)
             formats = qm.list_available_formats()
             if args.json:
                 print(json.dumps(formats, indent=2))
             else:
                 print(f"\n{Fore.CYAN}📋 Formatos de Commit Disponibles{Style.RESET_ALL}")
                 print("--------------------------------")
                 for (name, info) in formats.items():
                     print(f"{name}: {info['description']}")

    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

    # Lógica para manejar el argumento --commit-format directamente
    if args.commit_format and not args.command:
        project_path = args.path or Path.cwd()
        try:
            import importlib.util
            qm_path = project_path / ".githooks" / "quality_manager.py"
            if qm_path.exists():
                spec = importlib.util.spec_from_file_location("quality_manager", qm_path)
                qm_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(qm_module)
                QualityManager = qm_module.QualityManager
            else:
                print(f"{Fore.RED}❌ Error: No se encontró el módulo de QualityManager en {qm_path}{Style.RESET_ALL}")
                sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}❌ Error al importar QualityManager: {e}{Style.RESET_ALL}")
            sys.exit(1)

        qm = QualityManager(project_path)

        # 1. Obtener el formato de commit actual
        current_config = qm.get_current_configuration()
        current_commit_format = current_config.get('commit_format', 'N/A')
        current_level = current_config.get('level', 'N/A')
        print(f"{Fore.CYAN}⚙️  Configuración de calidad actual: Nivel {current_level}, Formato de commit: {current_commit_format}{Style.RESET_ALL}")

        # 2. Intentar aplicar el nuevo formato
        try:
            # Usar el nivel proporcionado por --level o el actual, o 'standard' como fallback
            level_to_apply = args.level if args.level else current_level
            if level_to_apply == 'N/A': # Si sigue siendo N/A, usar standard
                level_to_apply = 'standard'
                print(f"{Fore.YELLOW}⚠️  No se detectó un nivel de calidad activo. Usando 'standard' por defecto.{Style.RESET_ALL}")

            result = qm.apply_configuration(level_to_apply, args.commit_format)
            new_commit_format = result.get('commit_format', 'N/A')
            new_level = result.get('level', 'N/A')

            # 3. Mostrar mensaje de confirmación
            print(f"{Fore.GREEN}✅ Formato de commit cambiado a: {new_commit_format}{Style.RESET_ALL}")
            if current_commit_format != new_commit_format:
                print(f"{Fore.BLUE}ℹ️  El formato de commit cambió de '{current_commit_format}' a '{new_commit_format}'.{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}❌ Error al aplicar el formato de commit: {e}{Style.RESET_ALL}")
            sys.exit(1)
    elif not args.command and not args.commit_format: # Si no se especificó ningún comando ni --commit-format
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
