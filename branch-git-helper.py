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

class ContextDetector:
    """Detector automático de contexto de desarrollo."""
    
    def __init__(self, git_repo: GitRepository):
        self.git_repo = git_repo
    
    def detect_context(self) -> str:
        """
        Detecta automáticamente el contexto de desarrollo.
        
        Returns:
            str: "LOCAL", "HYBRID", o "REMOTE"
        """
        contributors = self.git_repo.get_contributor_count()
        commits = self.git_repo.get_commit_count()
        remotes = self.git_repo.get_remote_count()
        has_ci = self.git_repo.detect_ci_presence()
        has_develop = self.git_repo.branch_exists("develop")
        has_staging = self.git_repo.branch_exists("staging")
        
        # Lógica de detección
        if remotes == 0:
            return "LOCAL"
        elif contributors <= 2 and commits < 100 and not has_ci:
            return "HYBRID"
        elif has_ci or has_staging or contributors > 5:
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
        
        aliases = {
            'new-feature': f'!python {script_path} feature',
            'new-fix': f'!python {script_path} fix',
            'new-hotfix': f'!python {script_path} hotfix',
            'new-docs': f'!python {script_path} docs',
            'new-refactor': f'!python {script_path} refactor',
            'new-test': f'!python {script_path} test',
            'new-chore': f'!python {script_path} chore',
            'branch-status': f'!python {script_path} status'
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
            print(f"\n{Fore.BLUE}Ahora puedes usar:{Style.RESET_ALL}")
            for alias_name in aliases.keys():
                if alias_name != 'branch-status':
                    print(f"{Fore.YELLOW}  git {alias_name} \"descripción\"{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  git branch-status{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  Solo {success_count}/{len(aliases)} aliases se instalaron correctamente{Style.RESET_ALL}")
            return False
    
    @classmethod
    def uninstall_aliases(cls) -> bool:
        """Desinstala los aliases del sistema."""
        aliases = [
            'new-feature', 'new-fix', 'new-hotfix', 'new-docs',
            'new-refactor', 'new-test', 'new-chore', 'branch-status'
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

def show_status():
    """Muestra el estado actual del repositorio y contexto."""
    try:
        git_repo = GitRepository()
        context_detector = ContextDetector(git_repo)
        
        context = context_detector.detect_context()
        context_info = context_detector.get_context_info(context)
        current_branch = git_repo.get_current_branch()
        
        print(f"\n{Fore.CYAN}🔍 Estado del Repositorio{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📍 Rama actual: {Fore.YELLOW}{current_branch}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🎯 Contexto: {Fore.YELLOW}{context}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}👥 Contribuidores: {context_info['contributors']}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📝 Commits: {context_info['commits']}{Style.RESET_ALL}")
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
        description="Branch Git Helper - Gestión inteligente de branches con detección automática de contexto",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s feature "nueva-autenticacion"     # Crear rama de feature
  %(prog)s fix "corregir-validacion"         # Crear rama de fix
  %(prog)s hotfix "vulnerabilidad-critica"   # Crear rama de hotfix
  %(prog)s status                            # Mostrar estado del repositorio
  %(prog)s install-aliases                   # Instalar aliases persistentes
  %(prog)s uninstall-aliases                 # Remover aliases

Aliases disponibles después de instalación:
  git new-feature "descripción"
  git new-fix "descripción"
  git new-hotfix "descripción"
  git branch-status
        """
    )
    
    parser.add_argument(
        'action',
        help='Acción a realizar o tipo de branch a crear'
    )
    
    parser.add_argument(
        'description',
        nargs='?',
        help='Descripción de la rama (requerido para tipos de branch)'
    )
    
    parser.add_argument(
        '--no-push',
        action='store_true',
        help='No hacer push automático al remoto'
    )
    
    parser.add_argument(
        '--no-sync',
        action='store_true',
        help='No sincronizar con remoto antes de crear rama'
    )
    
    parser.add_argument(
        '--repo-path',
        type=Path,
        default=Path.cwd(),
        help='Ruta del repositorio Git (por defecto: directorio actual)'
    )
    
    args = parser.parse_args()
    
    # Comandos especiales
    if args.action == 'status':
        show_status()
        return
    
    if args.action == 'install-aliases':
        success = AliasManager.install_aliases()
        sys.exit(0 if success else 1)
    
    if args.action == 'uninstall-aliases':
        success = AliasManager.uninstall_aliases()
        sys.exit(0 if success else 1)
    
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