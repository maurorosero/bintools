#!/usr/bin/env python3
"""
Analizador para generar descripciones de proyectos universales.
Este módulo se integra con docgen.py para generar .project/description.md
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import yaml
import json

class ProjectDescriptionAnalyzer:
    """Analizador universal para generar descripciones de proyectos."""

    def __init__(self, base_path: Path, config: Optional[Dict] = None):
        """Inicializa el analizador."""
        self.base_path = base_path
        self.config = config or {}
        self.analysis_results = {}

    def analyze_project(self) -> Dict:
        """Analiza el proyecto completo para generar descripción global."""
        print("Iniciando análisis global del proyecto...")

        # Análisis completo y global
        analysis = {
            'project_name': self.base_path.name,
            'project_type': 'unknown',
            'structure': self._analyze_project_structure(),
            'technologies': self._analyze_technologies_summary(),
            'purpose': self._analyze_global_purpose(),
            'differentiators': self._analyze_differentiators_summary(),
            'metadata': self._analyze_metadata_summary(),
            'global_analysis': self._perform_global_analysis()
        }

        # Determinar tipo de proyecto basado en análisis global
        analysis['project_type'] = self._determine_project_type_from_global_analysis(analysis)

        self.analysis_results = analysis
        return analysis

    def _analyze_project_structure(self) -> Dict:
        """Analiza la estructura del proyecto."""
        structure = {
            'project_name': self.base_path.name,
            'project_path': str(self.base_path),
            'directories': [],
            'files': [],
            'config_files': [],
            'main_components': [],
            'project_type': 'unknown'
        }

        # Escanear estructura de directorios
        for item in self.base_path.rglob("*"):
            if item.is_file() and not item.name.startswith("."):
                structure['files'].append(str(item.relative_to(self.base_path)))
            elif item.is_dir() and not item.name.startswith("."):
                structure['directories'].append(str(item.relative_to(self.base_path)))

        # Detectar archivos de configuración
        config_patterns = [
            'requirements.txt', 'package.json', 'setup.py', 'pyproject.toml',
            'Cargo.toml', 'go.mod', 'composer.json', 'Gemfile',
            'README.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'LICENSE',
            'Dockerfile', 'docker-compose.yml', '.gitignore'
        ]

        for pattern in config_patterns:
            if (self.base_path / pattern).exists():
                structure['config_files'].append(pattern)

        # Detectar componentes principales
        structure['main_components'] = self._detect_main_components()

        # Determinar tipo de proyecto
        structure['project_type'] = self._determine_project_type(structure)

        return structure

    def _analyze_functionality_summary(self) -> Dict:
        """Analiza las funcionalidades del proyecto de forma resumida."""
        functionality = {
            'main_tools': [],
            'total_tools': 0,
            'categories': set()
        }

        # Analizar archivos Python principales
        python_files = list(self.base_path.rglob("*.py"))
        for py_file in python_files[:10]:  # Limitar a 10 archivos
            func_info = self._analyze_python_file_summary(py_file)
            if func_info:
                functionality['main_tools'].append(func_info)
                functionality['categories'].add(func_info.get('type', 'tool'))

        # Analizar scripts de shell principales
        shell_files = list(self.base_path.rglob("*.sh"))[:5]  # Limitar a 5 archivos
        for shell_file in shell_files:
            func_info = self._analyze_shell_file_summary(shell_file)
            if func_info:
                functionality['main_tools'].append(func_info)
                functionality['categories'].add(func_info.get('type', 'script'))

        functionality['total_tools'] = len(python_files) + len(shell_files)
        functionality['categories'] = list(functionality['categories'])

        return functionality

    def _analyze_technologies_summary(self) -> Dict:
        """Analiza las tecnologías utilizadas de forma resumida."""
        technologies = {
            'languages': set(),
            'platforms': set(),
            'main_dependencies': {}
        }

        # Detectar lenguajes principales
        file_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.sh': 'Bash',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.toml': 'TOML',
            '.md': 'Markdown'
        }

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in file_extensions:
                    technologies['languages'].add(file_extensions[ext])

        # Analizar dependencias principales
        technologies['main_dependencies'] = self._analyze_dependencies_summary()

        # Detectar plataformas
        if (self.base_path / "Dockerfile").exists():
            technologies['platforms'].add("Docker")

        technologies['languages'] = list(technologies['languages'])
        technologies['platforms'] = list(technologies['platforms'])

        return technologies

    def _analyze_purpose_summary(self) -> Dict:
        """Analiza el propósito del proyecto de forma resumida."""
        purpose = {
            'main_purpose': '',
            'problems_solved': [],
            'target_audience': []
        }

        # 1. Analizar README existente para extraer propósito
        readme_path = self.base_path / "README.md"
        if readme_path.exists():
            try:
                readme_content = readme_path.read_text(encoding='utf-8')
                purpose_info = self._extract_purpose_from_readme(readme_content)
                if purpose_info.get('main_purpose'):
                    purpose['main_purpose'] = purpose_info['main_purpose']
                    purpose['problems_solved'].extend(purpose_info.get('problems_solved', []))
                    purpose['target_audience'].extend(purpose_info.get('target_audience', []))
            except Exception:
                pass

        # 2. Analizar archivos de configuración para inferir propósito
        if not purpose['main_purpose']:
            config_purpose = self._analyze_purpose_from_configs()
            if config_purpose:
                purpose['main_purpose'] = config_purpose

        # 3. Analizar estructura de directorios para propósito general
        if not purpose['main_purpose']:
            structure_purpose = self._analyze_purpose_from_structure()
            if structure_purpose:
                purpose['main_purpose'] = structure_purpose

        # 4. Inferir propósito basado en contenido de archivos principales
        if not purpose['main_purpose']:
            content_purpose = self._analyze_purpose_from_content()
            if content_purpose:
                purpose['main_purpose'] = content_purpose

        # 5. Propósito por defecto más general
        if not purpose['main_purpose']:
            purpose['main_purpose'] = f'Ecosistema completo de herramientas y utilidades para {self.base_path.name}'
            purpose['problems_solved'].append('Automatización de tareas repetitivas')
            purpose['problems_solved'].append('Gestión eficiente de flujos de trabajo')
            purpose['problems_solved'].append('Integración de herramientas de desarrollo')

        # 6. Audiencia objetivo más amplia
        if not purpose['target_audience']:
            purpose['target_audience'] = [
                'Desarrolladores',
                'Administradores de sistemas',
                'DevOps Engineers',
                'Equipos de desarrollo',
                'Organizaciones que buscan automatización'
            ]

        return purpose

    def _analyze_purpose_from_configs(self) -> Optional[str]:
        """Analiza archivos de configuración para inferir propósito."""
        config_files = [
            'package.json', 'setup.py', 'pyproject.toml', 'Cargo.toml',
            'go.mod', 'composer.json', 'Gemfile', 'pom.xml'
        ]

        for config_file in config_files:
            config_path = self.base_path / config_file
            if config_path.exists():
                try:
                    if config_file == 'package.json':
                        with open(config_path, 'r') as f:
                            data = json.load(f)
                            if 'description' in data:
                                return data['description']
                    elif config_file in ['setup.py', 'pyproject.toml']:
                        # Buscar descripción en archivos Python
                        content = config_path.read_text()
                        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
                        if desc_match:
                            return desc_match.group(1)
                except Exception:
                    continue

        return None

    def _analyze_purpose_from_structure(self) -> Optional[str]:
        """Analiza estructura de directorios para inferir propósito general."""
        dir_names = [d.name.lower() for d in self.base_path.iterdir() if d.is_dir()]
        file_names = [f.name.lower() for f in self.base_path.iterdir() if f.is_file()]

        # Detectar patrones de propósito
        if 'docs' in dir_names and 'scripts' in dir_names:
            return "Sistema integral de documentación y automatización"
        elif 'tools' in dir_names and 'config' in dir_names:
            return "Suite completa de herramientas y configuraciones"
        elif 'ci' in dir_names and 'scripts' in dir_names:
            return "Plataforma de integración continua y automatización"
        elif 'scaffold' in dir_names:
            return "Sistema de scaffolding y generación de proyectos"
        elif any('workflow' in name for name in file_names):
            return "Gestión avanzada de flujos de trabajo y automatización"
        elif any('manager' in name for name in file_names):
            return "Sistema de gestión y administración de recursos"

        return None

    def _analyze_purpose_from_content(self) -> Optional[str]:
        """Analiza contenido de archivos principales para inferir propósito."""
        # Buscar en archivos Python principales
        main_files = ['main.py', 'app.py', 'cli.py', 'manager.py']
        for main_file in main_files:
            main_path = self.base_path / main_file
            if main_path.exists():
                try:
                    content = main_path.read_text()
                    # Buscar docstrings o comentarios que describan el propósito
                    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                    if docstring_match:
                        docstring = docstring_match.group(1).strip()
                        if len(docstring) > 20:  # Solo si es sustancial
                            return docstring.split('\n')[0]  # Primera línea
                except Exception:
                    continue

        return None

    def _analyze_differentiators_summary(self) -> Dict:
        """Analiza los diferenciadores del proyecto de forma resumida."""
        differentiators = {
            'unique_features': [],
            'special_capabilities': []
        }

        # Analizar funcionalidades únicas
        if self.analysis_results.get('functionality'):
            funcs = self.analysis_results['functionality']['main_tools']
            tool_types = [f.get('type', '') for f in funcs]

            if 'python_tool' in tool_types and 'shell_script' in tool_types:
                differentiators['unique_features'].append("Combinación de herramientas Python y scripts de shell")

            if len(funcs) > 5:
                differentiators['unique_features'].append("Ecosistema completo de herramientas")

        # Analizar tecnologías especiales
        if self.analysis_results.get('technologies'):
            techs = self.analysis_results['technologies']
            languages = techs.get('languages', [])

            if 'Python' in languages and 'Bash' in languages:
                differentiators['special_capabilities'].append("Desarrollo multiplataforma Python/Shell")

            if len(languages) > 3:
                differentiators['special_capabilities'].append("Multi-tecnología")

        return differentiators

    def _analyze_metadata_summary(self) -> Dict:
        """Analiza metadatos del proyecto de forma resumida."""
        metadata = {
            'status': 'Development',
            'tags': []
        }

        # Generar tags relevantes
        if self.analysis_results.get('technologies'):
            techs = self.analysis_results['technologies']
            metadata['tags'].extend(techs.get('languages', [])[:5])  # Limitar a 5 tags

        if self.analysis_results.get('functionality'):
            funcs = self.analysis_results['functionality']
            metadata['tags'].extend(funcs.get('categories', []))

        return metadata

    def _analyze_python_file_summary(self, file_path: Path) -> Optional[Dict]:
        """Analiza un archivo Python para extraer funcionalidad de forma resumida."""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Buscar docstring principal
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            description = docstring_match.group(1).strip()[:100] if docstring_match else ""

            # Buscar funciones principales
            functions = re.findall(r'def\s+(\w+)\s*\(', content)

            if functions or description:
                return {
                    'name': file_path.stem,
                    'type': 'python_tool',
                    'description': description,
                    'functions_count': len(functions)
                }
        except Exception:
            pass

        return None

    def _analyze_shell_file_summary(self, file_path: Path) -> Optional[Dict]:
        """Analiza un archivo de shell para extraer funcionalidad de forma resumida."""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Buscar comentarios de descripción
            description_match = re.search(r'#\s*(.+?)(?:\n|$)', content)
            description = description_match.group(1).strip()[:100] if description_match else ""

            if description:
                return {
                    'name': file_path.stem,
                    'type': 'shell_script',
                    'description': description
                }
        except Exception:
            pass

        return None

    def _analyze_dependencies_summary(self) -> Dict:
        """Analiza las dependencias del proyecto de forma resumida."""
        dependencies = {}

        # Python dependencies (solo las principales)
        requirements_path = self.base_path / "requirements.txt"
        if requirements_path.exists():
            try:
                deps = requirements_path.read_text(encoding='utf-8').split('\n')
                python_deps = [dep.strip() for dep in deps if dep.strip() and not dep.startswith('#')]
                dependencies['python'] = python_deps[:10]  # Limitar a 10 dependencias
            except Exception:
                pass

        return dependencies

    def _detect_main_components(self) -> List[str]:
        """Detecta los componentes principales del proyecto."""
        components = []

        # Buscar directorios principales
        main_dirs = ['src', 'lib', 'app', 'bin', 'scripts', 'tools', 'config', 'docs']
        for dir_name in main_dirs:
            if (self.base_path / dir_name).exists():
                components.append(dir_name)

        # Buscar archivos principales
        main_files = ['main.py', 'app.py', 'index.js', 'main.go', 'Cargo.toml', 'package.json']
        for file_name in main_files:
            if (self.base_path / file_name).exists():
                components.append(file_name)

        return components

    def _determine_project_type(self, structure: Dict) -> str:
        """Determina el tipo de proyecto."""
        config_files = structure['config_files']
        components = structure['main_components']

        if 'package.json' in config_files:
            return 'nodejs_application'
        elif 'setup.py' in config_files or 'pyproject.toml' in config_files:
            return 'python_package'
        elif 'Cargo.toml' in config_files:
            return 'rust_project'
        elif 'go.mod' in config_files:
            return 'go_project'
        elif 'Dockerfile' in config_files:
            return 'containerized_application'
        elif 'scripts' in components or 'tools' in components:
            return 'tool_collection'
        elif 'docs' in components:
            return 'documentation_project'
        else:
            return 'general_project'

    def _analyze_technologies(self) -> Dict:
        """Analiza las tecnologías utilizadas."""
        technologies = {
            'languages': set(),
            'frameworks': set(),
            'dependencies': {},
            'platforms': set(),
            'tools': set()
        }

        # Detectar lenguajes de programación
        file_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.sh': 'Bash',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.toml': 'TOML',
            '.md': 'Markdown'
        }

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in file_extensions:
                    technologies['languages'].add(file_extensions[ext])

        # Analizar dependencias
        technologies['dependencies'] = self._analyze_dependencies()

        # Detectar plataformas
        technologies['platforms'] = self._detect_platforms()

        # Convertir sets a listas para serialización
        technologies['languages'] = list(technologies['languages'])
        technologies['platforms'] = list(technologies['platforms'])

        return technologies

    def _analyze_purpose(self) -> Dict:
        """Analiza el propósito del proyecto."""
        purpose = {
            'main_purpose': '',
            'problems_solved': [],
            'target_audience': [],
            'use_cases': [],
            'value_proposition': ''
        }

        # Analizar README existente
        readme_path = self.base_path / "README.md"
        if readme_path.exists():
            readme_content = readme_path.read_text(encoding='utf-8')
            purpose.update(self._extract_purpose_from_readme(readme_content))

        # Analizar docstrings y comentarios
        purpose.update(self._extract_purpose_from_code())

        # Analizar nombre del proyecto y estructura
        purpose.update(self._infer_purpose_from_structure())

        return purpose

    def _analyze_differentiators(self) -> Dict:
        """Analiza los diferenciadores del proyecto."""
        differentiators = {
            'unique_features': [],
            'competitive_advantages': [],
            'value_propositions': [],
            'special_capabilities': []
        }

        # Analizar funcionalidades únicas
        if self.analysis_results.get('functionality'):
            funcs = self.analysis_results['functionality']['all_functionalities']
            differentiators['unique_features'] = self._identify_unique_features(funcs)

        # Analizar combinación de tecnologías
        if self.analysis_results.get('technologies'):
            techs = self.analysis_results['technologies']
            differentiators['special_capabilities'] = self._identify_special_capabilities(techs)

        return differentiators

    def _analyze_metadata(self) -> Dict:
        """Analiza metadatos del proyecto."""
        metadata = {
            'status': 'Development',
            'related_links': {},
            'tags': [],
            'version': '',
            'license': '',
            'repository_info': {}
        }

        # Detectar estado del proyecto
        metadata['status'] = self._determine_project_status()

        # Encontrar enlaces relacionados
        metadata['related_links'] = self._find_related_links()

        # Generar tags relevantes
        metadata['tags'] = self._generate_relevant_tags()

        # Obtener información del repositorio
        metadata['repository_info'] = self._get_repository_info()

        return metadata

    def _analyze_dependencies(self) -> Dict:
        """Analiza las dependencias del proyecto."""
        dependencies = {}

        # Python dependencies
        requirements_path = self.base_path / "requirements.txt"
        if requirements_path.exists():
            try:
                deps = requirements_path.read_text(encoding='utf-8').split('\n')
                dependencies['python'] = [dep.strip() for dep in deps if dep.strip() and not dep.startswith('#')]
            except Exception:
                pass

        # Node.js dependencies
        package_json_path = self.base_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    dependencies['nodejs'] = {
                        'dependencies': list(package_data.get('dependencies', {}).keys()),
                        'devDependencies': list(package_data.get('devDependencies', {}).keys())
                    }
            except Exception:
                pass

        return dependencies

    def _detect_platforms(self) -> Set[str]:
        """Detecta las plataformas soportadas."""
        platforms = set()

        # Buscar indicadores de plataforma
        if (self.base_path / "Dockerfile").exists():
            platforms.add("Docker")

        # Buscar scripts específicos de plataforma
        platform_scripts = {
            'Windows': ['*.bat', '*.cmd', '*.ps1'],
            'macOS': ['*.sh'],
            'Linux': ['*.sh']
        }

        for platform, patterns in platform_scripts.items():
            for pattern in patterns:
                if list(self.base_path.rglob(pattern)):
                    platforms.add(platform)

        return platforms

    def _extract_purpose_from_readme(self, content: str) -> Dict:
        """Extrae propósito del README."""
        purpose = {
            'main_purpose': '',
            'problems_solved': [],
            'target_audience': []
        }

        # Buscar descripción principal
        desc_match = re.search(r'#\s*\w+\s*\n+(.+?)(?:\n##|\n#|\n$)', content, re.DOTALL)
        if desc_match:
            purpose['main_purpose'] = desc_match.group(1).strip()

        return purpose

    def _extract_purpose_from_code(self) -> Dict:
        """Extrae propósito del código."""
        purpose = {
            'use_cases': [],
            'value_proposition': ''
        }

        # Analizar docstrings en archivos Python
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if docstring_match:
                    docstring = docstring_match.group(1)
                    # Buscar casos de uso en docstrings
                    if 'use case' in docstring.lower() or 'ejemplo' in docstring.lower():
                        purpose['use_cases'].append({
                            'file': str(py_file.relative_to(self.base_path)),
                            'description': docstring[:200] + "..."
                        })
            except Exception:
                pass

        return purpose

    def _infer_purpose_from_structure(self) -> Dict:
        """Infiere propósito basado en la estructura."""
        purpose = {
            'main_purpose': '',
            'problems_solved': []
        }

        # Inferir basado en nombres de directorios y archivos
        dir_names = [d.name.lower() for d in self.base_path.iterdir() if d.is_dir()]
        file_names = [f.name.lower() for f in self.base_path.iterdir() if f.is_file()]

        if 'tools' in dir_names or 'scripts' in dir_names:
            purpose['main_purpose'] = 'Colección de herramientas y scripts de utilidad'
            purpose['problems_solved'].append('Automatización de tareas repetitivas')

        if 'docs' in dir_names:
            purpose['main_purpose'] = 'Documentación y recursos'
            purpose['problems_solved'].append('Organización de información')

        return purpose

    def _identify_unique_features(self, functionalities: List[Dict]) -> List[str]:
        """Identifica características únicas."""
        unique_features = []

        # Analizar combinaciones únicas de funcionalidades
        tool_types = [f.get('type', '') for f in functionalities]

        if 'python_tool' in tool_types and 'shell_script' in tool_types:
            unique_features.append("Combinación de herramientas Python y scripts de shell")

        if len(functionalities) > 5:
            unique_features.append("Ecosistema completo de herramientas")

        return unique_features

    def _identify_special_capabilities(self, technologies: Dict) -> List[str]:
        """Identifica capacidades especiales."""
        capabilities = []

        languages = technologies.get('languages', [])
        platforms = technologies.get('platforms', [])

        if 'Python' in languages and 'Bash' in languages:
            capabilities.append("Desarrollo multiplataforma Python/Shell")

        if 'Docker' in platforms:
            capabilities.append("Containerización y despliegue")

        if len(languages) > 3:
            capabilities.append("Multi-tecnología")

        return capabilities

    def _determine_project_status(self) -> str:
        """Determina el estado del proyecto."""
        # Buscar indicadores de estado
        if (self.base_path / "CHANGELOG.md").exists():
            return "Development"
        elif (self.base_path / "README.md").exists():
            return "Development"
        else:
            return "Development"

    def _find_related_links(self) -> Dict:
        """Encuentra enlaces relacionados."""
        links = {
            'documentation': '',
            'issues': '',
            'discussions': '',
            'wiki': ''
        }

        # Buscar enlaces en README
        readme_path = self.base_path / "README.md"
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8')
                # Buscar enlaces de documentación
                doc_links = re.findall(r'\[.*?\]\((https?://[^)]+)\)', content)
                if doc_links:
                    links['documentation'] = doc_links[0]
            except Exception:
                pass

        return links

    def _generate_relevant_tags(self) -> List[str]:
        """Genera tags relevantes."""
        tags = []

        # Basado en tecnologías
        if self.analysis_results.get('technologies'):
            techs = self.analysis_results['technologies']
            tags.extend(techs.get('languages', []))

        # Basado en funcionalidades
        if self.analysis_results.get('functionality'):
            funcs = self.analysis_results['functionality']['all_functionalities']
            for func in funcs:
                tags.append(func.get('type', ''))

        # Basado en tipo de proyecto
        if self.analysis_results.get('project_structure'):
            project_type = self.analysis_results['project_structure']['project_type']
            tags.append(project_type)

        return list(set(tags))  # Eliminar duplicados

    def _get_repository_info(self) -> Dict:
        """Obtiene información del repositorio."""
        repo_info = {
            'url': '',
            'type': 'unknown'
        }

        # Intentar obtener información de git
        try:
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                                  capture_output=True, text=True, cwd=self.base_path)
            if result.returncode == 0:
                repo_info['url'] = result.stdout.strip()
                if 'github.com' in repo_info['url']:
                    repo_info['type'] = 'github'
                elif 'gitlab.com' in repo_info['url']:
                    repo_info['type'] = 'gitlab'
        except Exception:
            pass

        return repo_info

    def _perform_global_analysis(self) -> Dict:
        """Realiza un análisis global del proyecto examinando todos los archivos."""
        global_analysis = {
            'file_categories': {},
            'main_themes': set(),
            'project_focus': '',
            'key_components': [],
            'integration_points': [],
            'automation_level': 'low',
            'complexity_level': 'low'
        }

        # 1. Categorizar todos los archivos
        file_categories = self._categorize_all_files()
        global_analysis['file_categories'] = file_categories

        # 2. Analizar contenido de archivos clave
        key_files_analysis = self._analyze_key_files_content()
        global_analysis.update(key_files_analysis)

        # 3. Detectar temas principales
        main_themes = self._detect_main_themes(file_categories, key_files_analysis)
        global_analysis['main_themes'] = list(main_themes)

        # 4. Determinar enfoque del proyecto
        project_focus = self._determine_project_focus(global_analysis)
        global_analysis['project_focus'] = project_focus

        # 5. Identificar componentes clave
        key_components = self._identify_key_components(global_analysis)
        global_analysis['key_components'] = key_components

        # 6. Detectar puntos de integración
        integration_points = self._detect_integration_points(global_analysis)
        global_analysis['integration_points'] = integration_points

        # 7. Evaluar nivel de automatización
        automation_level = self._evaluate_automation_level(global_analysis)
        global_analysis['automation_level'] = automation_level

        # 8. Evaluar complejidad
        complexity_level = self._evaluate_complexity_level(global_analysis)
        global_analysis['complexity_level'] = complexity_level

        return global_analysis

    def _categorize_all_files(self) -> Dict:
        """Categoriza todos los archivos del proyecto."""
        categories = {
            'python_scripts': [],
            'shell_scripts': [],
            'config_files': [],
            'documentation': [],
            'templates': [],
            'data_files': [],
            'build_files': [],
            'test_files': [],
            'other': []
        }

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                rel_path = str(file_path.relative_to(self.base_path))

                if file_path.suffix == '.py':
                    categories['python_scripts'].append(rel_path)
                elif file_path.suffix in ['.sh', '.bash']:
                    categories['shell_scripts'].append(rel_path)
                elif file_path.suffix in ['.yaml', '.yml', '.json', '.toml', '.ini', '.cfg']:
                    categories['config_files'].append(rel_path)
                elif file_path.suffix in ['.md', '.txt', '.rst']:
                    categories['documentation'].append(rel_path)
                elif 'template' in file_path.name.lower() or 'template' in rel_path.lower():
                    categories['templates'].append(rel_path)
                elif file_path.suffix in ['.csv', '.xml', '.sql']:
                    categories['data_files'].append(rel_path)
                elif file_path.suffix in ['.dockerfile', '.yml', '.yaml'] and 'docker' in file_path.name.lower():
                    categories['build_files'].append(rel_path)
                elif 'test' in file_path.name.lower() or 'test' in rel_path.lower():
                    categories['test_files'].append(rel_path)
                else:
                    categories['other'].append(rel_path)

        return categories

    def _analyze_key_files_content(self) -> Dict:
        """Analiza el contenido de archivos clave para entender el proyecto."""
        key_analysis = {
            'main_functions': [],
            'integrations': [],
            'workflows': [],
            'configurations': {},
            'dependencies': []
        }

        # Analizar archivos Python principales
        python_files = list(self.base_path.rglob("*.py"))[:20]  # Top 20 archivos
        for py_file in python_files:
            try:
                content = py_file.read_text()

                # Detectar funciones principales
                if 'def main(' in content or 'if __name__' in content:
                    key_analysis['main_functions'].append(str(py_file.relative_to(self.base_path)))

                # Detectar integraciones
                if any(term in content.lower() for term in ['api', 'http', 'request', 'integration']):
                    key_analysis['integrations'].append(str(py_file.relative_to(self.base_path)))

                # Detectar workflows
                if any(term in content.lower() for term in ['workflow', 'pipeline', 'process', 'orchestrate']):
                    key_analysis['workflows'].append(str(py_file.relative_to(self.base_path)))

                # Detectar dependencias
                if 'import ' in content or 'from ' in content:
                    imports = re.findall(r'(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                    key_analysis['dependencies'].extend(imports[:5])  # Top 5 imports

            except Exception:
                continue

        # Analizar archivos de configuración
        config_files = ['requirements.txt', 'package.json', 'setup.py', 'pyproject.toml']
        for config_file in config_files:
            config_path = self.base_path / config_file
            if config_path.exists():
                try:
                    content = config_path.read_text()
                    key_analysis['configurations'][config_file] = content[:500]  # Primeros 500 chars
                except Exception:
                    continue

        return key_analysis

    def _detect_main_themes(self, file_categories: Dict, key_analysis: Dict) -> Set[str]:
        """Detecta los temas principales del proyecto."""
        themes = set()

        # Analizar categorías de archivos
        if file_categories['python_scripts']:
            themes.add('python_development')
        if file_categories['shell_scripts']:
            themes.add('automation')
        if file_categories['config_files']:
            themes.add('configuration_management')
        if file_categories['templates']:
            themes.add('templating')
        if file_categories['documentation']:
            themes.add('documentation')

        # Analizar contenido clave
        if key_analysis['integrations']:
            themes.add('integration')
        if key_analysis['workflows']:
            themes.add('workflow_management')
        if key_analysis['main_functions']:
            themes.add('application_development')

        # Detectar temas específicos
        if any('git' in f.lower() for f in file_categories['python_scripts']):
            themes.add('git_management')
        if any('ci' in f.lower() or 'cd' in f.lower() for f in file_categories['python_scripts']):
            themes.add('ci_cd')
        if any('test' in f.lower() for f in file_categories['python_scripts']):
            themes.add('testing')

        return themes

    def _determine_project_focus(self, global_analysis: Dict) -> str:
        """Determina el enfoque principal del proyecto."""
        themes = global_analysis['main_themes']
        file_categories = global_analysis['file_categories']

        # Priorizar temas principales
        if 'git_management' in themes and 'workflow_management' in themes:
            return "Gestión avanzada de flujos de trabajo Git y automatización de desarrollo"
        elif 'ci_cd' in themes and 'automation' in themes:
            return "Plataforma de integración continua y automatización de procesos"
        elif 'integration' in themes and 'configuration_management' in themes:
            return "Sistema de integración y gestión de configuraciones"
        elif 'templating' in themes and 'documentation' in themes:
            return "Sistema de generación de templates y documentación"
        elif 'python_development' in themes and 'application_development' in themes:
            return "Suite de herramientas de desarrollo Python"
        elif 'automation' in themes:
            return "Sistema de automatización y herramientas de productividad"
        else:
            return "Ecosistema de herramientas y utilidades para desarrollo"

    def _identify_key_components(self, global_analysis: Dict) -> List[str]:
        """Identifica los componentes clave del proyecto."""
        components = []
        file_categories = global_analysis['file_categories']

        # Componentes basados en archivos
        if file_categories['python_scripts']:
            components.append("Scripts Python para automatización")
        if file_categories['shell_scripts']:
            components.append("Scripts de shell para tareas del sistema")
        if file_categories['config_files']:
            components.append("Sistema de configuración")
        if file_categories['templates']:
            components.append("Generador de templates")
        if file_categories['documentation']:
            components.append("Sistema de documentación")

        # Componentes basados en análisis de contenido
        if global_analysis['integrations']:
            components.append("Integraciones con APIs externas")
        if global_analysis['workflows']:
            components.append("Gestión de workflows")

        return components

    def _detect_integration_points(self, global_analysis: Dict) -> List[str]:
        """Detecta los puntos de integración del proyecto."""
        integrations = []

        # Analizar archivos de integración
        for integration_file in global_analysis['integrations']:
            try:
                content = (self.base_path / integration_file).read_text()
                if 'github' in content.lower():
                    integrations.append("GitHub API")
                if 'gitlab' in content.lower():
                    integrations.append("GitLab API")
                if 'docker' in content.lower():
                    integrations.append("Docker")
                if 'jenkins' in content.lower():
                    integrations.append("Jenkins")
                if 'slack' in content.lower():
                    integrations.append("Slack")
            except Exception:
                continue

        return list(set(integrations))  # Eliminar duplicados

    def _evaluate_automation_level(self, global_analysis: Dict) -> str:
        """Evalúa el nivel de automatización del proyecto."""
        automation_indicators = 0

        if global_analysis['file_categories']['shell_scripts']:
            automation_indicators += 2
        if global_analysis['file_categories']['python_scripts']:
            automation_indicators += 2
        if global_analysis['workflows']:
            automation_indicators += 3
        if global_analysis['integrations']:
            automation_indicators += 2
        if 'ci_cd' in global_analysis['main_themes']:
            automation_indicators += 3

        if automation_indicators >= 8:
            return "high"
        elif automation_indicators >= 4:
            return "medium"
        else:
            return "low"

    def _evaluate_complexity_level(self, global_analysis: Dict) -> str:
        """Evalúa el nivel de complejidad del proyecto."""
        complexity_indicators = 0

        total_files = sum(len(files) for files in global_analysis['file_categories'].values())
        if total_files > 50:
            complexity_indicators += 3
        elif total_files > 20:
            complexity_indicators += 2
        elif total_files > 10:
            complexity_indicators += 1

        if len(global_analysis['main_themes']) > 5:
            complexity_indicators += 2
        elif len(global_analysis['main_themes']) > 3:
            complexity_indicators += 1

        if global_analysis['integrations']:
            complexity_indicators += 2

        if global_analysis['automation_level'] == 'high':
            complexity_indicators += 1

        if complexity_indicators >= 6:
            return "high"
        elif complexity_indicators >= 3:
            return "medium"
        else:
            return "low"

    def _determine_project_type_from_global_analysis(self, analysis: Dict) -> str:
        """Determina el tipo de proyecto basado en el análisis global."""
        global_analysis = analysis.get('global_analysis', {})
        themes = global_analysis.get('main_themes', [])
        focus = global_analysis.get('project_focus', '')

        if 'git_management' in themes and 'workflow_management' in themes:
            return "git_workflow_management"
        elif 'ci_cd' in themes:
            return "ci_cd_platform"
        elif 'integration' in themes:
            return "integration_platform"
        elif 'templating' in themes:
            return "template_generator"
        elif 'automation' in themes:
            return "automation_suite"
        elif 'python_development' in themes:
            return "python_toolkit"
        else:
            return "general_utilities"

    def _analyze_global_purpose(self) -> Dict:
        """Analiza el propósito global del proyecto basado en el análisis completo."""
        purpose = {
            'main_purpose': '',
            'problems_solved': [],
            'target_audience': []
        }

        # Usar el análisis global para determinar el propósito
        if hasattr(self, 'analysis_results') and 'global_analysis' in self.analysis_results:
            global_analysis = self.analysis_results['global_analysis']
            focus = global_analysis.get('project_focus', '')

            if focus:
                purpose['main_purpose'] = focus
            else:
                purpose['main_purpose'] = f'Ecosistema completo de herramientas para {self.base_path.name}'

            # Determinar problemas resueltos basado en componentes
            components = global_analysis.get('key_components', [])
            if 'Scripts Python para automatización' in components:
                purpose['problems_solved'].append('Automatización de tareas repetitivas')
            if 'Gestión de workflows' in components:
                purpose['problems_solved'].append('Gestión eficiente de flujos de trabajo')
            if 'Integraciones con APIs externas' in components:
                purpose['problems_solved'].append('Integración de servicios externos')
            if 'Sistema de configuración' in components:
                purpose['problems_solved'].append('Gestión centralizada de configuraciones')

            # Audiencia objetivo basada en complejidad y enfoque
            complexity = global_analysis.get('complexity_level', 'low')
            if complexity == 'high':
                purpose['target_audience'] = ['Equipos de desarrollo avanzados', 'DevOps Engineers', 'Arquitectos de sistemas']
            elif complexity == 'medium':
                purpose['target_audience'] = ['Desarrolladores', 'Administradores de sistemas', 'Equipos de desarrollo']
            else:
                purpose['target_audience'] = ['Desarrolladores', 'Administradores de sistemas']

        return purpose
