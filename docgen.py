#!/usr/bin/env python3
"""
Generador de documentación para el ecosistema Git Branch Tools.
Utiliza Claude 3.7 para generar documentación basada en el código y configuración.
"""

import os
import click
import yaml
import ast
import keyring
import getpass
import base64
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel
from rich import print as rprint
import re
import subprocess

# Importar el analizador de project_description
try:
    from scripts.project_description_analyzer import ProjectDescriptionAnalyzer
except ImportError:
    # Si no se puede importar, crear una clase dummy
    class ProjectDescriptionAnalyzer:
        def __init__(self, base_path, config=None):
            self.base_path = base_path
            self.config = config or {}

        def analyze_project(self):
            return {}

console = Console()

class AnthropicAuth:
    """Gestión de autenticación con Anthropic API."""
    SERVICE_NAME = "ai-anthropic-docs"

    @classmethod
    def get_current_user(cls) -> str:
        """Obtiene el usuario actual del sistema."""
        return getpass.getuser()

    @classmethod
    def get_api_token(cls) -> Optional[str]:
        """Obtiene el token de API para el usuario actual."""
        current_user = cls.get_current_user()
        try:
            encoded_token = keyring.get_password(cls.SERVICE_NAME, current_user)
            if not encoded_token:
                raise RuntimeError(
                    f"No se encontró token para {current_user}. "
                    "Usa el script de configuración de tokens para configurarlo."
                )
            # Decodificar el token de base64
            return base64.b64decode(encoded_token).decode('utf-8')
        except keyring.errors.KeyringError as e:
            raise RuntimeError(
                f"Error al obtener el token de API para {current_user}: {str(e)}"
            )

class CodeAnalyzer:
    """Analizador profundo de código para documentación."""

    def __init__(self, base_path: Path, config: Optional[Dict] = None):
        """Inicializa el analizador de código.

        Args:
            base_path: Ruta base donde buscar archivos
            config: Configuración del analizador (opcional)
        """
        self.base_path = base_path
        self.config = config or {}
        self.workflows = {}  # Flujos de trabajo detectados
        self.examples = {}   # Ejemplos de uso
        self.configs = {}    # Configuraciones
        self.dependencies = {}  # Dependencias entre funciones
        self.use_cases = {}  # Casos de uso
        self.functionality = {}  # Análisis funcional
        self.console = Console()  # Agregar console para logging

        # Mapeo de nombres de métodos de análisis
        self.analysis_method_map = {
            'detect_new_functions': '_analyze_functions',
            'analyze_parameters': '_analyze_parameters',
            'check_docstrings': '_analyze_docstrings',
            'validate_metadata': '_validate_metadata',
            'detect_new_commands': '_analyze_commands',
            'analyze_validation_rules': '_analyze_validation_rules',
            'analyze_context_detection': '_analyze_context_detection',
            'analyze_workflows': '_analyze_workflows',
            'analyze_integrations': '_analyze_integrations',
            'check_hook_integration': '_analyze_hook_integration'
        }

        # Inicializar métodos de análisis según la configuración
        self.analysis_methods = self.config.get('analysis_methods', {}).get('code_analysis', {}).get('tools', [])
        self.validation_checks = self.config.get('validation', {}).get('checks', [])

    def configure(self, config: Dict):
        """Configura el analizador con una nueva configuración.

        Args:
            config: Nueva configuración del analizador
        """
        self.config = config
        self.analysis_methods = self.config.get('analysis_methods', {}).get('code_analysis', {}).get('tools', [])
        self.validation_checks = self.config.get('validation', {}).get('checks', [])

    def analyze_file(self, file_path: Path) -> Dict:
        """Analiza un archivo Python en detalle."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            return {
                'workflows': self._analyze_workflows(tree, file_path),
                'examples': self._analyze_examples(tree, file_path),
                'configs': self._analyze_configs(tree, file_path),
                'dependencies': self._analyze_dependencies(tree, file_path),
                'use_cases': self._analyze_use_cases(tree, file_path)
            }
        except Exception as e:
            click.echo(f"Error analizando {file_path}: {str(e)}")
            return {}

    def _analyze_workflows(self, tree: ast.AST, file_path: Path) -> List[Dict]:
        """Detecta flujos de trabajo en el código."""
        workflows = []

        # Buscar funciones que orquestan otras funciones
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Buscar patrones de flujo de trabajo
                if self._is_workflow_function(node):
                    workflow = {
                        'name': node.name,
                        'description': self._get_docstring(node),
                        'steps': self._extract_workflow_steps(node),
                        'file': str(file_path)
                    }
                    workflows.append(workflow)

        return workflows

    def _analyze_examples(self, tree: ast.AST, file_path: Path) -> List[Dict]:
        """Extrae ejemplos de uso del código."""
        examples = []

        # Buscar en docstrings y comentarios
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = self._get_docstring(node)
                if docstring:
                    # Buscar bloques de código en docstrings
                    code_blocks = self._extract_code_blocks(docstring)
                    if code_blocks:
                        examples.append({
                            'name': node.name,
                            'type': 'function' if isinstance(node, ast.FunctionDef) else 'class',
                            'examples': code_blocks,
                            'file': str(file_path)
                        })

        return examples

    def _analyze_configs(self, tree: ast.AST, file_path: Path) -> List[Dict]:
        """Analiza configuraciones disponibles."""
        configs = []

        # Buscar variables de configuración
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Buscar nombres que sugieran configuración
                        if any(term in target.id.lower() for term in ['config', 'setting', 'option']):
                            configs.append({
                                'name': target.id,
                                'value': self._get_literal_value(node.value),
                                'file': str(file_path)
                            })

        return configs

    def _analyze_dependencies(self, tree: ast.AST, file_path: Path) -> Dict[str, List[str]]:
        """Analiza dependencias entre funciones."""
        deps = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                calls = self._get_function_calls(node)
                if calls:
                    deps[node.name] = calls

        return deps

    def _analyze_use_cases(self, tree: ast.AST, file_path: Path) -> List[Dict]:
        """Detecta casos de uso comunes."""
        use_cases = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Buscar patrones de caso de uso
                if self._is_use_case(node):
                    use_case = {
                        'name': node.name,
                        'description': self._get_docstring(node),
                        'steps': self._extract_use_case_steps(node),
                        'file': str(file_path)
                    }
                    use_cases.append(use_case)

        return use_cases

    def _is_workflow_function(self, node: ast.FunctionDef) -> bool:
        """Determina si una función es un flujo de trabajo."""
        # Buscar patrones que sugieran un flujo de trabajo
        patterns = [
            'workflow', 'process', 'pipeline', 'sequence',
            'flow', 'orchestrate', 'coordinate'
        ]

        # Verificar nombre y docstring
        name_lower = node.name.lower()
        docstring = self._get_docstring(node) or ''

        return (
            any(p in name_lower for p in patterns) or
            any(p in docstring.lower() for p in patterns) or
            self._has_sequential_calls(node)
        )

    def _is_use_case(self, node: ast.FunctionDef) -> bool:
        """Determina si una función representa un caso de uso."""
        # Buscar patrones de caso de uso
        patterns = [
            'use case', 'scenario', 'example', 'demonstrate',
            'show how to', 'illustrate'
        ]

        docstring = self._get_docstring(node) or ''
        return any(p in docstring.lower() for p in patterns)

    def _get_docstring(self, node: ast.AST) -> Optional[str]:
        """Extrae el docstring de un nodo."""
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            if ast.get_docstring(node):
                return ast.get_docstring(node)
        return None

    def _extract_code_blocks(self, docstring: str) -> List[str]:
        """Extrae bloques de código de un docstring."""
        blocks = []
        in_block = False
        current_block = []

        for line in docstring.split('\n'):
            if line.strip().startswith('```'):
                if in_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                in_block = not in_block
            elif in_block:
                current_block.append(line)

        return blocks

    def _get_literal_value(self, node: ast.AST) -> any:
        """Obtiene el valor literal de una expresión."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Dict):
            return {self._get_literal_value(k): self._get_literal_value(v)
                   for k, v in zip(node.keys, node.values)}
        elif isinstance(node, ast.List):
            return [self._get_literal_value(e) for e in node.elts]
        return None

    def _get_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Obtiene las llamadas a funciones dentro de una función."""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return calls

    def _has_sequential_calls(self, node: ast.FunctionDef) -> bool:
        """Determina si una función tiene llamadas secuenciales."""
        calls = self._get_function_calls(node)
        return len(calls) > 2  # Más de 2 llamadas sugiere un flujo

    def _extract_workflow_steps(self, node: ast.FunctionDef) -> List[str]:
        """Extrae los pasos de un flujo de trabajo."""
        steps = []
        for call in self._get_function_calls(node):
            steps.append(f"Llamada a {call}")
        return steps

    def _extract_use_case_steps(self, node: ast.FunctionDef) -> List[str]:
        """Extrae los pasos de un caso de uso."""
        docstring = self._get_docstring(node) or ''
        steps = []

        # Buscar pasos numerados en el docstring
        for line in docstring.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                steps.append(line.strip())

        return steps

    def _analyze_functions(self, file_path: Path) -> Dict:
        """Analiza las funciones definidas en el archivo."""
        result = {'functions': []}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node),
                        'returns': self._get_return_type(node),
                        'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                    }
                    result['functions'].append(func_info)
        except Exception as e:
            self.console.print(f"[red]Error analizando funciones en {file_path}: {str(e)}[/red]")
        return result

    def _analyze_parameters(self, file_path: Path) -> Dict:
        """Analiza los parámetros de las funciones."""
        result = {'parameters': {}}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    params = {}
                    for arg in node.args.args:
                        param_info = {
                            'type': self._get_annotation_type(arg.annotation),
                            'default': self._get_default_value(arg),
                            'doc': self._get_param_doc(node, arg.arg)
                        }
                        params[arg.arg] = param_info
                    result['parameters'][node.name] = params
        except Exception as e:
            self.console.print(f"[red]Error analizando parámetros en {file_path}: {str(e)}[/red]")
        return result

    def _analyze_docstrings(self, file_path: Path) -> Dict:
        """Analiza los docstrings del código."""
        result = {'docstrings': {}}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    doc = ast.get_docstring(node)
                    if doc:
                        result['docstrings'][node.name if hasattr(node, 'name') else 'module'] = {
                            'content': doc,
                            'type': type(node).__name__,
                            'has_args': bool(re.search(r':param|:arg|Args:', doc)),
                            'has_returns': bool(re.search(r':return|:rtype|Returns:', doc))
                        }
        except Exception as e:
            self.console.print(f"[red]Error analizando docstrings en {file_path}: {str(e)}[/red]")
        return result

    def _validate_metadata(self, file_path: Path) -> Dict:
        """Valida los metadatos del archivo."""
        result = {'metadata': {}}
        try:
            # Verificar metadatos en docstrings
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            module_doc = ast.get_docstring(tree)
            if module_doc:
                metadata = {
                    'has_description': bool(module_doc.strip()),
                    'has_version': bool(re.search(r'version|v\d+\.\d+', module_doc, re.I)),
                    'has_author': bool(re.search(r'author|created by', module_doc, re.I)),
                    'has_license': bool(re.search(r'license|copyright', module_doc, re.I))
                }
                result['metadata']['module'] = metadata

            # Verificar metadatos en clases y funciones
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    doc = ast.get_docstring(node)
                    if doc:
                        metadata = {
                            'has_description': bool(doc.strip()),
                            'has_args': bool(re.search(r':param|:arg|Args:', doc)),
                            'has_returns': bool(re.search(r':return|:rtype|Returns:', doc)),
                            'has_examples': bool(re.search(r':example|Example:', doc))
                        }
                        result['metadata'][node.name] = metadata
        except Exception as e:
            self.console.print(f"[red]Error validando metadatos en {file_path}: {str(e)}[/red]")
        return result

    def _analyze_commands(self, file_path: Path) -> Dict:
        """Analiza los comandos CLI definidos."""
        result = {'commands': []}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                # Detectar decoradores de click
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Name) and decorator.func.id == 'command':
                                cmd_info = {
                                    'name': node.name,
                                    'docstring': ast.get_docstring(node),
                                    'options': self._get_click_options(node),
                                    'arguments': self._get_click_arguments(node)
                                }
                                result['commands'].append(cmd_info)
        except Exception as e:
            self.console.print(f"[red]Error analizando comandos en {file_path}: {str(e)}[/red]")
        return result

    def _analyze_validation_rules(self, file_path: Path) -> Dict:
        """Analiza las reglas de validación definidas."""
        result = {'validation_rules': []}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Buscar funciones de validación
                    if 'validate' in node.name.lower() or 'check' in node.name.lower():
                        rule_info = {
                            'name': node.name,
                            'docstring': ast.get_docstring(node),
                            'conditions': self._get_validation_conditions(node),
                            'error_messages': self._get_validation_messages(node)
                        }
                        result['validation_rules'].append(rule_info)
        except Exception as e:
            self.console.print(f"[red]Error analizando reglas de validación en {file_path}: {str(e)}[/red]")
        return result

    def _analyze_context_detection(self, file_path: Path) -> Dict:
        """Analiza la detección de contexto."""
        result = {'context_detection': {}}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if 'detect' in node.name.lower() and 'context' in node.name.lower():
                        context_info = {
                            'name': node.name,
                            'docstring': ast.get_docstring(node),
                            'contexts': self._get_detected_contexts(node),
                            'conditions': self._get_context_conditions(node)
                        }
                        result['context_detection'][node.name] = context_info
        except Exception as e:
            self.console.print(f"[red]Error analizando detección de contexto en {file_path}: {str(e)}[/red]")
        return result

    def _analyze_integrations(self, file_path: Path) -> Dict:
        """Analiza las integraciones definidas."""
        result = {'integrations': []}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Buscar clases de integración
                    if 'integration' in node.name.lower() or 'manager' in node.name.lower():
                        integration_info = {
                            'name': node.name,
                            'docstring': ast.get_docstring(node),
                            'methods': self._get_integration_methods(node),
                            'dependencies': self._get_integration_dependencies(node)
                        }
                        result['integrations'].append(integration_info)
        except Exception as e:
            self.console.print(f"[red]Error analizando integraciones en {file_path}: {str(e)}[/red]")
        return result

    def _analyze_hook_integration(self, file_path: Path) -> Dict:
        """Analiza la integración con hooks de Git."""
        result = {'hook_integration': {}}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Buscar funciones relacionadas con hooks
                    if 'hook' in node.name.lower():
                        hook_info = {
                            'name': node.name,
                            'docstring': ast.get_docstring(node),
                            'hook_type': self._get_hook_type(node),
                            'validations': self._get_hook_validations(node)
                        }
                        result['hook_integration'][node.name] = hook_info
        except Exception as e:
            self.console.print(f"[red]Error analizando integración de hooks en {file_path}: {str(e)}[/red]")
        return result

    def _get_click_options(self, node: ast.FunctionDef) -> List[Dict]:
        """Extrae las opciones de click de una función."""
        options = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'option':
                    option_info = {
                        'name': self._get_option_name(decorator),
                        'help': self._get_option_help(decorator),
                        'type': self._get_option_type(decorator),
                        'required': self._get_option_required(decorator)
                    }
                    options.append(option_info)
        return options

    def _get_click_arguments(self, node: ast.FunctionDef) -> List[Dict]:
        """Extrae los argumentos de click de una función."""
        arguments = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'argument':
                    arg_info = {
                        'name': self._get_argument_name(decorator),
                        'help': self._get_argument_help(decorator),
                        'type': self._get_argument_type(decorator),
                        'required': self._get_argument_required(decorator)
                    }
                    arguments.append(arg_info)
        return arguments

    def _get_validation_conditions(self, node: ast.FunctionDef) -> List[str]:
        """Extrae las condiciones de validación de una función."""
        conditions = []
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.If):
                condition = self._get_condition_description(stmt.test)
                if condition:
                    conditions.append(condition)
        return conditions

    def _get_validation_messages(self, node: ast.FunctionDef) -> List[str]:
        """Extrae los mensajes de error de validación."""
        messages = []
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Raise):
                if isinstance(stmt.exc, ast.Call):
                    if isinstance(stmt.exc.args[0], ast.Constant):
                        messages.append(stmt.exc.args[0].value)
        return messages

    def _get_detected_contexts(self, node: ast.FunctionDef) -> List[str]:
        """Extrae los contextos detectados."""
        contexts = []
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Return):
                if isinstance(stmt.value, ast.Constant):
                    contexts.append(stmt.value.value)
        return contexts

    def _get_context_conditions(self, node: ast.FunctionDef) -> List[Dict]:
        """Extrae las condiciones para cada contexto."""
        conditions = []
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.If):
                condition = self._get_condition_description(stmt.test)
                if condition:
                    context = self._get_context_from_condition(stmt)
                    if context:
                        conditions.append({
                            'context': context,
                            'condition': condition
                        })
        return conditions

    def _get_integration_methods(self, node: ast.ClassDef) -> List[Dict]:
        """Extrae los métodos de integración de una clase."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    'name': item.name,
                    'docstring': ast.get_docstring(item),
                    'args': [arg.arg for arg in item.args.args],
                    'returns': self._get_return_type(item)
                }
                methods.append(method_info)
        return methods

    def _get_integration_dependencies(self, node: ast.ClassDef) -> List[str]:
        """Extrae las dependencias de una integración."""
        dependencies = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.Call):
                        if isinstance(stmt.func, ast.Name):
                            dependencies.append(stmt.func.id)
                        elif isinstance(stmt.func, ast.Attribute):
                            dependencies.append(f"{stmt.func.value.id}.{stmt.func.attr}")
        return list(set(dependencies))

    def _get_hook_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Determina el tipo de hook."""
        doc = ast.get_docstring(node)
        if doc:
            for hook_type in ['pre-commit', 'post-commit', 'pre-push', 'post-push']:
                if hook_type in doc.lower():
                    return hook_type
        return None

    def _get_hook_validations(self, node: ast.FunctionDef) -> List[Dict]:
        """Extrae las validaciones de un hook."""
        validations = []
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                if isinstance(stmt.func, ast.Attribute) and 'validate' in stmt.func.attr:
                    validation_info = {
                        'type': stmt.func.attr,
                        'args': [self._get_ast_value(arg) for arg in stmt.args],
                        'kwargs': {kw.arg: self._get_ast_value(kw.value) for kw in stmt.keywords}
                    }
                    validations.append(validation_info)
        return validations

    def _get_option_name(self, decorator: ast.Call) -> str:
        """Extrae el nombre de una opción de click."""
        for kw in decorator.keywords:
            if kw.arg == 'name':
                return self._get_ast_value(kw.value)
        return ''

    def _get_option_help(self, decorator: ast.Call) -> str:
        """Extrae el texto de ayuda de una opción de click."""
        for kw in decorator.keywords:
            if kw.arg == 'help':
                return self._get_ast_value(kw.value)
        return ''

    def _get_option_type(self, decorator: ast.Call) -> str:
        """Extrae el tipo de una opción de click."""
        for kw in decorator.keywords:
            if kw.arg == 'type':
                return self._get_ast_value(kw.value).__name__
        return 'str'

    def _get_option_required(self, decorator: ast.Call) -> bool:
        """Determina si una opción de click es requerida."""
        for kw in decorator.keywords:
            if kw.arg == 'required':
                return self._get_ast_value(kw.value)
        return False

    def _get_argument_name(self, decorator: ast.Call) -> str:
        """Extrae el nombre de un argumento de click."""
        for kw in decorator.keywords:
            if kw.arg == 'name':
                return self._get_ast_value(kw.value)
        return ''

    def _get_argument_help(self, decorator: ast.Call) -> str:
        """Extrae el texto de ayuda de un argumento de click."""
        for kw in decorator.keywords:
            if kw.arg == 'help':
                return self._get_ast_value(kw.value)
        return ''

    def _get_argument_type(self, decorator: ast.Call) -> str:
        """Extrae el tipo de un argumento de click."""
        for kw in decorator.keywords:
            if kw.arg == 'type':
                return self._get_ast_value(kw.value).__name__
        return 'str'

    def _get_argument_required(self, decorator: ast.Call) -> bool:
        """Determina si un argumento de click es requerido."""
        for kw in decorator.keywords:
            if kw.arg == 'required':
                return self._get_ast_value(kw.value)
        return False

    def _get_context_from_condition(self, node: ast.If) -> Optional[str]:
        """Extrae el contexto de una condición if."""
        for stmt in node.body:
            if isinstance(stmt, ast.Return):
                if isinstance(stmt.value, ast.Constant):
                    return stmt.value.value
        return None

    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extrae el tipo de retorno de una función."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                return f"{node.returns.value.id}.{node.returns.attr}"
        return None

    def _get_return_description(self, node: ast.FunctionDef) -> Optional[str]:
        """Extrae la descripción del retorno de una función."""
        doc = ast.get_docstring(node)
        if doc:
            match = re.search(r':return:|:rtype:|Returns:(.*?)(?=:|\Z)', doc, re.DOTALL)
            if match:
                return match.group(1).strip()
        return None

    def _get_param_doc(self, node: ast.AST, param_name: str) -> Optional[str]:
        """Extrae la documentación de un parámetro específico del docstring."""
        doc = ast.get_docstring(node)
        if not doc:
            return None
        # Usar $ en lugar de \Z para el final de la cadena
        match = re.search(f':param {param_name}:(.*?)(?=:param|:return|:rtype|$)', doc, re.DOTALL)
        return match.group(1).strip() if match else None

    def _get_default_value(self, arg: ast.arg) -> Optional[str]:
        """Extrae el valor por defecto de un argumento."""
        if arg.default:
            return self._get_ast_value(arg.default)
        return None

    def _get_annotation_type(self, annotation: Optional[ast.AST]) -> Optional[str]:
        """Extrae el tipo de una anotación."""
        if annotation:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Attribute):
                return f"{annotation.value.id}.{annotation.attr}"
        return None

    def _analyze_codebase(self, doc_type: str, custom_type: Optional[str] = None) -> Dict:
        """Analiza el código base para generar documentación."""
        analysis = {
            'workflows': [],
            'examples': [],
            'configs': [],
            'dependencies': [],
            'use_cases': [],
            'functions': {},
            'parameters': {},
            'docstrings': {},
            'metadata': {},
            'commands': [],
            'validation_rules': [],
            'context_detection': {},
            'integrations': {},
            'hook_integration': {}
        }

        # Usar la configuración que ya está en self.config
        analysis_config = self.config.get('analysis', {})
        analysis_types = analysis_config.get('types', [])

        # Obtener archivos a analizar
        main_files = [
            'branch-git-helper.py',
            'git-integration-manager.py',
            '.githooks/branch-workflow-validator.py'
        ]

        # Calcular el progreso por archivo
        progress_per_file = 100 / len(main_files)
        current_progress = 0

        # Analizar cada archivo
        for py_file in main_files:
            if not os.path.exists(py_file):
                self.console.print(f"[yellow]Archivo no encontrado: {py_file}[/yellow]")
                current_progress += progress_per_file
                continue

            self.console.print(f"[blue]Analizando {py_file}...[/blue]")
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)

                # Analizar según los tipos configurados
                file_analysis = {}

                # Mapeo de tipos de análisis a métodos del CodeAnalyzer
                analysis_methods = {
                    'workflows': lambda t, f: self._analyze_workflows(t, f),
                    'examples': lambda t, f: self._analyze_examples(t, f),
                    'configs': lambda t, f: self._analyze_configs(t, f),
                    'dependencies': lambda t, f: self._analyze_dependencies(t, f),
                    'use_cases': lambda t, f: self._analyze_use_cases(t, f),
                    'functions': lambda t, f: self._analyze_functions(Path(f)),
                    'parameters': lambda t, f: self._analyze_parameters(Path(f)),
                    'docstrings': lambda t, f: self._analyze_docstrings(Path(f)),
                    'metadata': lambda t, f: self._validate_metadata(Path(f)),
                    'commands': lambda t, f: self._analyze_commands(Path(f)),
                    'validation_rules': lambda t, f: self._analyze_validation_rules(Path(f)),
                    'context_detection': lambda t, f: self._analyze_context_detection(Path(f)),
                    'integrations': lambda t, f: self._analyze_integrations(Path(f)),
                    'hook_integration': lambda t, f: self._analyze_hook_integration(Path(f))
                }

                # Ejecutar análisis según configuración
                for analysis_type in analysis_types:
                    if analysis_type in analysis_methods:
                        method = analysis_methods[analysis_type]
                        try:
                            result = method(tree, py_file)
                            if isinstance(result, dict):
                                file_analysis.update(result)
                            elif isinstance(result, list):
                                if analysis_type in file_analysis:
                                    if isinstance(file_analysis[analysis_type], list):
                                        file_analysis[analysis_type].extend(result)
                                else:
                                    file_analysis[analysis_type] = result
                        except Exception as e:
                            self.console.print(f"[red]Error en análisis {analysis_type}: {str(e)}[/red]")
                    else:
                        self.console.print(f"[yellow]Método de análisis no encontrado: {analysis_type}[/yellow]")

                # Actualizar análisis general
                for key in analysis:
                    if key in file_analysis:
                        if isinstance(analysis[key], list) and isinstance(file_analysis[key], list):
                            analysis[key].extend(file_analysis[key])
                        elif isinstance(analysis[key], dict) and isinstance(file_analysis[key], dict):
                            analysis[key].update(file_analysis[key])
                        elif isinstance(analysis[key], list) and isinstance(file_analysis[key], dict):
                            analysis[key].append(file_analysis[key])
                        elif isinstance(analysis[key], dict) and isinstance(file_analysis[key], list):
                            for item in file_analysis[key]:
                                if isinstance(item, dict):
                                    analysis[key].update(item)

                # Actualizar progreso
                current_progress += progress_per_file
                if hasattr(self, 'progress') and hasattr(self, 'analysis_task'):
                    self.progress.update(self.analysis_task, completed=int(current_progress))

            except Exception as e:
                self.console.print(f"[red]Error analizando {py_file}: {str(e)}[/red]")
                current_progress += progress_per_file
                if hasattr(self, 'progress') and hasattr(self, 'analysis_task'):
                    self.progress.update(self.analysis_task, completed=int(current_progress))
                continue

        # Asegurar que el progreso llegue al 100%
        if hasattr(self, 'progress') and hasattr(self, 'analysis_task'):
            self.progress.update(self.analysis_task, completed=100)

        return analysis

class ChangelogAnalyzer:
    """Analizador específico para generación de CHANGELOG."""

    def __init__(self, base_path: Path, config: Optional[Dict] = None):
        """Inicializa el analizador de CHANGELOG.

        Args:
            base_path: Ruta base del repositorio
            config: Configuración del analizador
        """
        self.base_path = base_path
        self.config = config or {}
        self.console = Console()

        # Mapeo de tags a categorías Keep a Changelog
        self.CATEGORY_MAP = {
            'FEAT': 'Added',
            'FIX': 'Fixed',
            'REFACTOR': 'Changed',
            'PERF': 'Changed',
            'STYLE': 'Changed',
            'DOCS': 'Changed',
            'TEST': 'Changed',
            'BUILD': 'Changed',
            'CI': 'Changed',
            'CHORE': 'Changed',
            'REVERT': 'Changed',
            'BREAKING': 'Breaking Changes'
        }

        # Palabras clave para detectar deprecaciones
        self.DEPRECATED_KEYWORDS = [
            "deprecate", "deprecated", "deprecation",
            "obsolete", "legacy", "will be removed",
            "no longer supported", "use instead",
            "replaced by", "migration"
        ]

        # Patrones para detectar deprecaciones
        self.DEPRECATED_PATTERNS = [
            r"deprecat[ei].*function",
            r"deprecat[ei].*method",
            r"deprecat[ei].*api",
            r"mark.*as.*deprecated",
            r"deprecat[ei].*in favor of"
        ]

        # Emojis para cada categoría
        self.CATEGORY_EMOJIS = {
            'Added': '🎉',
            'Changed': '⚡',
            'Deprecated': '⚠️',
            'Removed': '🗑️',
            'Fixed': '🐛',
            'Security': '🔒',
            'Breaking Changes': '❌'
        }

    def analyze_git_history(self, since_tag: Optional[str] = None) -> Dict:
        """Analiza el historial de Git para generar CHANGELOG.

        Args:
            since_tag: Tag desde el cual analizar (opcional)

        Returns:
            Diccionario con commits categorizados
        """
        try:
            # Obtener commits desde el último tag o desde el inicio
            commits = self._get_commits_since_tag(since_tag)

            # Parsear y categorizar commits
            parsed_commits = self._parse_commits(commits)

            # Categorizar por tipo de cambio
            categorized = self._categorize_commits(parsed_commits)

            # Obtener información de versiones
            versions = self._get_version_info(since_tag)

            return {
                'commits': parsed_commits,
                'categorized': categorized,
                'versions': versions,
                'statistics': self._calculate_statistics(categorized)
            }

        except Exception as e:
            self.console.print(f"[red]Error analizando historial de Git: {str(e)}[/red]")
            return {}

    def _get_commits_since_tag(self, since_tag: Optional[str] = None) -> List[str]:
        """Obtiene commits desde un tag específico o desde el inicio."""
        try:
            if since_tag:
                # Commits desde un tag específico
                result = subprocess.run([
                    'git', 'log', '--oneline', '--reverse', f'{since_tag}..HEAD'
                ], capture_output=True, text=True, cwd=self.base_path)
            else:
                # Todos los commits
                result = subprocess.run([
                    'git', 'log', '--oneline', '--reverse'
                ], capture_output=True, text=True, cwd=self.base_path)

            if result.returncode == 0 and result.stdout:
                return [line.strip() for line in result.stdout.split('\n') if line.strip()]
            else:
                self.console.print("[yellow]No se encontraron commits o error en git log[/yellow]")
                return []

        except Exception as e:
            self.console.print(f"[red]Error ejecutando git log: {str(e)}[/red]")
            return []

    def _parse_commits(self, commits: List[str]) -> List[Dict]:
        """Parsea los commits según diferentes formatos."""
        parsed_commits = []

        # Palabras clave para identificar commits de prueba
        test_keywords = ['prueba', 'test', 'testing', 'línea de prueba', 'línea adicional']

        for commit in commits:
            # Extraer hash del commit
            parts = commit.split(' ', 1)
            if len(parts) < 2:
                continue

            commit_hash = parts[0]
            message = parts[1]

            # Verificar si es un commit de prueba
            message_lower = message.lower()
            if any(keyword in message_lower for keyword in test_keywords):
                continue

            # Patrón 1: [TAG] (#Issue) Descripción
            pattern1 = r'^\[([A-Z]+)\](?: \(#(\d+)\))? (.+)$'
            match1 = re.match(pattern1, message)

            if match1:
                tag, issue, description = match1.groups()
                # Excluir commits de TEST
                if tag == 'TEST':
                    continue
                parsed_commits.append({
                    'hash': commit_hash,
                    'tag': tag,
                    'issue': issue,
                    'description': description,
                    'full_message': message,
                    'is_deprecation': self._is_deprecation_commit(description),
                    'is_security': self._is_security_commit(description),
                    'is_breaking': self._is_breaking_commit(description)
                })
                continue

            # Patrón 2: tag: descripción (formato convencional)
            pattern2 = r'^([a-z]+): (.+)$'
            match2 = re.match(pattern2, message)

            if match2:
                tag, description = match2.groups()
                # Convertir a mayúsculas para consistencia
                tag = tag.upper()
                # Excluir commits de TEST
                if tag == 'TEST':
                    continue
                parsed_commits.append({
                    'hash': commit_hash,
                    'tag': tag,
                    'issue': None,
                    'description': description,
                    'full_message': message,
                    'is_deprecation': self._is_deprecation_commit(description),
                    'is_security': self._is_security_commit(description),
                    'is_breaking': self._is_breaking_commit(description)
                })
                continue

            # Patrón 3: tag(scope): descripción (formato angular)
            pattern3 = r'^([a-z]+)(?:\(([^)]+)\))?: (.+)$'
            match3 = re.match(pattern3, message)

            if match3:
                tag, scope, description = match3.groups()
                # Convertir a mayúsculas para consistencia
                tag = tag.upper()
                # Excluir commits de TEST
                if tag == 'TEST':
                    continue
                parsed_commits.append({
                    'hash': commit_hash,
                    'tag': tag,
                    'issue': None,
                    'description': description,
                    'full_message': message,
                    'is_deprecation': self._is_deprecation_commit(description),
                    'is_security': self._is_security_commit(description),
                    'is_breaking': self._is_breaking_commit(description)
                })
                continue

            # Patrón 4: TAG descripción (formato simple)
            pattern4 = r'^([A-Z]+)\s+(.+)$'
            match4 = re.match(pattern4, message)

            if match4:
                tag, description = match4.groups()
                # Excluir commits de TEST
                if tag == 'TEST':
                    continue
                parsed_commits.append({
                    'hash': commit_hash,
                    'tag': tag,
                    'issue': None,
                    'description': description,
                    'full_message': message,
                    'is_deprecation': self._is_deprecation_commit(description),
                    'is_security': self._is_security_commit(description),
                    'is_breaking': self._is_breaking_commit(description)
                })
                continue

            # Si no coincide con ningún patrón, tratar como CHORE
            parsed_commits.append({
                'hash': commit_hash,
                'tag': 'CHORE',
                'issue': None,
                'description': message,
                'full_message': message,
                'is_deprecation': self._is_deprecation_commit(message),
                'is_security': self._is_security_commit(message),
                'is_breaking': self._is_breaking_commit(message)
            })

        return parsed_commits

    def _categorize_commits(self, commits: List[Dict]) -> Dict[str, List[Dict]]:
        """Categoriza los commits según Keep a Changelog."""
        categorized = {
            'Added': [],
            'Changed': [],
            'Deprecated': [],
            'Removed': [],
            'Fixed': [],
            'Security': [],
            'Breaking Changes': []
        }

        for commit in commits:
            # Determinar categoría principal
            if commit['is_breaking']:
                category = 'Breaking Changes'
            elif commit['is_deprecation']:
                category = 'Deprecated'
            elif commit['is_security']:
                category = 'Security'
            else:
                category = self.CATEGORY_MAP.get(commit['tag'], 'Changed')

            # Agregar emoji a la descripción
            emoji = self.CATEGORY_EMOJIS.get(category, '')
            commit['emoji'] = emoji
            commit['category'] = category

            categorized[category].append(commit)

        # Aplicar deduplicación a cada categoría
        for category in categorized:
            categorized[category] = self._deduplicate_commits(categorized[category])

        return categorized

    def _is_deprecation_commit(self, description: str) -> bool:
        """Determina si un commit es de deprecación."""
        description_lower = description.lower()

        # Buscar palabras clave
        if any(keyword in description_lower for keyword in self.DEPRECATED_KEYWORDS):
            return True

        # Buscar patrones específicos
        if any(re.search(pattern, description_lower) for pattern in self.DEPRECATED_PATTERNS):
            return True

        return False

    def _is_security_commit(self, description: str) -> bool:
        """Determina si un commit es de seguridad."""
        security_keywords = ['security', 'vulnerability', 'auth', 'permission', 'cve']
        return any(keyword in description.lower() for keyword in security_keywords)

    def _is_breaking_commit(self, description: str) -> bool:
        """Determina si un commit es breaking change."""
        breaking_keywords = ['breaking', 'remove', 'delete', 'drop', 'eliminate']
        return any(keyword in description.lower() for keyword in breaking_keywords)

    def _get_version_info(self, since_tag: Optional[str] = None) -> Dict:
        """Obtiene información de versiones."""
        try:
            # Obtener tags
            result = subprocess.run([
                'git', 'tag', '--sort=-version:refname'
            ], capture_output=True, text=True, cwd=self.base_path)

            tags = []
            if result.returncode == 0 and result.stdout:
                tags = [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]

            # Filtrar solo tags que son versiones válidas (semantic versioning)
            import re
            version_pattern = re.compile(r'^v?\d+\.\d+\.\d+$')  # Solo versiones exactas, sin sufijos
            valid_versions = []

            for tag in tags:
                if version_pattern.match(tag):
                    valid_versions.append(tag)  # Mantener el nombre original del tag

            # Ordenar versiones correctamente (semantic versioning)
            def version_key(tag):
                # Remover 'v' prefix si existe para ordenamiento
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

            # Obtener fecha del último commit
            result = subprocess.run([
                'git', 'log', '-1', '--format=%cd', '--date=short'
            ], capture_output=True, text=True, cwd=self.base_path)

            last_commit_date = result.stdout.strip() if result.returncode == 0 else None

            return {
                'tags': valid_versions,
                'latest_tag': valid_versions[0] if valid_versions else None,
                'last_commit_date': last_commit_date
            }

        except Exception as e:
            self.console.print(f"[red]Error obteniendo información de versiones: {str(e)}[/red]")
            return {}

    def _calculate_statistics(self, categorized: Dict) -> Dict:
        """Calcula estadísticas de los cambios."""
        total_commits = sum(len(commits) for commits in categorized.values())

        return {
            'total_commits': total_commits,
            'by_category': {category: len(commits) for category, commits in categorized.items()},
            'has_breaking_changes': len(categorized['Breaking Changes']) > 0,
            'has_security_updates': len(categorized['Security']) > 0,
            'has_deprecations': len(categorized['Deprecated']) > 0
        }

    def generate_changelog_content(self, analysis: Dict, use_ai: bool = False) -> str:
        """Genera el contenido del CHANGELOG."""
        if use_ai:
            return self._generate_with_ai(analysis)
        else:
            return self._generate_without_ai(analysis)

    def _generate_without_ai(self, analysis: Dict) -> str:
        """Genera CHANGELOG usando solo templates y datos."""
        versions = analysis.get('versions', {})
        statistics = analysis.get('statistics', {})

        # Template del CHANGELOG
        changelog = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""

        # Obtener tags ordenados
        tags = versions.get('tags', [])

        if not tags:
            # Si no hay tags, mostrar solo commits unreleased
            all_commits = analysis.get('commits', [])
            if all_commits:
                changelog += "## [Unreleased]\n\n"
                parsed_commits = self._parse_commits(all_commits)
                categorized = self._categorize_commits(parsed_commits)
                changelog += self._format_section(categorized)
                changelog += "\n"
        else:
            # Distribuir commits por versiones
            for i, tag in enumerate(tags):
                # Obtener commits para esta versión
                if i == 0:
                    # Para la versión más reciente, obtener commits entre esta versión y la anterior
                    if len(tags) > 1:
                        previous_tag = tags[1]
                        commits = self._get_commits_between_tags(previous_tag, tag)
                    else:
                        # Si solo hay una versión, obtener todos los commits hasta ese tag
                        commits = self._get_commits_until_tag(tag)
                else:
                    # Para versiones anteriores, obtener commits entre este tag y el anterior
                    if i + 1 < len(tags):
                        previous_tag = tags[i + 1]
                        commits = self._get_commits_between_tags(previous_tag, tag)
                    else:
                        # Para la versión más antigua, obtener commits desde el inicio hasta ese tag
                        commits = self._get_commits_until_tag(tag)

                if commits:
                    parsed_commits = self._parse_commits(commits)
                    # Obtener fecha del tag
                    tag_date = self._get_tag_date(tag)

                    # Categorizar commits
                    categorized = self._categorize_commits(parsed_commits)

                    # Añadir sección de versión
                    changelog += f"## [{tag}] - {tag_date}\n\n"
                    changelog += self._format_section(categorized)
                    changelog += "\n"

            # Sección Unreleased (commits después del tag más reciente)
            latest_tag = tags[0]
            unreleased_commits = self._get_commits_since_tag(latest_tag)
            if unreleased_commits:
                parsed_commits = self._parse_commits(unreleased_commits)
                changelog += "## [Unreleased]\n\n"
                categorized = self._categorize_commits(parsed_commits)
                changelog += self._format_section(categorized)
                changelog += "\n"

        return changelog

    def _get_commits_between_tags(self, from_tag: str, to_tag: str) -> List[str]:
        """Obtiene commits entre dos tags específicos como líneas de git log."""
        try:
            # Obtener commits entre tags
            result = subprocess.run([
                'git', 'log', '--oneline', '--reverse', f'{from_tag}..{to_tag}'
            ], capture_output=True, text=True, cwd=self.base_path)

            if result.returncode == 0 and result.stdout:
                return [line.strip() for line in result.stdout.split('\n') if line.strip()]

            return []
        except Exception as e:
            self.console.print(f"[red]Error obteniendo commits entre {from_tag} y {to_tag}: {str(e)}[/red]")
            return []

    def _get_tag_date(self, tag: str) -> str:
        """Obtiene la fecha de un tag específico."""
        try:
            result = subprocess.run([
                'git', 'log', '-1', '--format=%ad', '--date=short', tag
            ], capture_output=True, text=True, cwd=self.base_path)

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()

            return 'TBD'
        except Exception as e:
            self.console.print(f"[red]Error obteniendo fecha del Tag {tag}: {str(e)}[/red]")
            return 'TBD'

    def _get_commits_until_tag(self, tag: str) -> List[str]:
        """Obtiene commits hasta el tag especificado (desde el inicio hasta el tag)."""
        try:
            # Obtener commits hasta el tag especificado
            result = subprocess.run([
                'git', 'log', '--oneline', '--reverse', f'..{tag}'
            ], capture_output=True, text=True, cwd=self.base_path)

            if result.returncode == 0 and result.stdout:
                return [line.strip() for line in result.stdout.split('\n') if line.strip()]
            else:
                self.console.print("[yellow]No se encontraron commits o error en git log[/yellow]")
                return []

        except Exception as e:
            self.console.print(f"[red]Error ejecutando git log: {str(e)}[/red]")
            return []

    def _format_section(self, categorized: Dict) -> str:
        """Formatea una sección del CHANGELOG."""
        section = ""

        for category, commits in categorized.items():
            if commits:
                section += f"### {category}\n"
                for commit in commits:
                    emoji = commit.get('emoji', '')
                    description = commit['description']
                    issue = commit.get('issue')

                    if issue:
                        section += f"- {emoji} {description} (#{issue})\n"
                    else:
                        section += f"- {emoji} {description}\n"

                section += "\n"

        return section

    def _generate_with_ai(self, analysis: Dict) -> str:
        """Genera CHANGELOG mejorado con IA."""
        try:
            # Primero generar el CHANGELOG básico
            basic_changelog = self._generate_without_ai(analysis)

            # Construir prompt para mejorar con IA
            prompt = self._build_ai_prompt(basic_changelog, analysis)

            # Llamar a la API de Claude
            client = anthropic.Anthropic(api_key=AnthropicAuth.get_api_token())

            response = client.messages.create(
                model="claude-4-sonnet-20250514",
                max_tokens=6000,
                temperature=0.8,
                system=prompt,
                messages=[
                    {
                        "role": "user",
                        "content": "Mejora este CHANGELOG haciéndolo más profesional y claro."
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            self.console.print(f"[yellow]⚠ Error usando IA, generando sin IA: {str(e)}[/yellow]")
            return self._generate_without_ai(analysis)

    def _build_ai_prompt(self, basic_changelog: str, analysis: Dict) -> str:
        """Construye el prompt para mejorar el CHANGELOG con IA."""
        statistics = analysis.get('statistics', {})

        prompt = f"""Eres un experto en generar CHANGELOGs profesionales siguiendo el estándar Keep a Changelog.

Tu tarea es mejorar este CHANGELOG haciéndolo más profesional, claro y útil para usuarios y desarrolladores.

CHANGELOG actual:
{basic_changelog}

Estadísticas del análisis:
- Total de commits: {statistics.get('total_commits', 0)}
- Breaking changes: {statistics.get('has_breaking_changes', False)}
- Security updates: {statistics.get('has_security_updates', False)}
- Deprecations: {statistics.get('has_deprecations', False)}

Instrucciones para mejorar:
1. Mantén la estructura Keep a Changelog
2. Mejora las descripciones para que sean más claras y específicas
3. Agrupa cambios relacionados cuando sea apropiado
4. Añade contexto útil cuando sea necesario
5. Usa emojis apropiados para mejorar la legibilidad
6. Mantén un tono profesional pero accesible
7. Asegúrate de que breaking changes estén claramente marcados
8. Incluye información de seguridad cuando sea relevante

Reglas importantes:
- NO cambies la estructura básica del CHANGELOG
- NO elimines información importante
- NO inventes cambios que no existan
- SÍ mejora la claridad y profesionalismo
- SÍ agrupa cambios relacionados
- SÍ añade contexto útil cuando sea necesario

Devuelve solo el CHANGELOG mejorado en formato Markdown."""

        return prompt

    def _deduplicate_commits(self, commits: List[Dict]) -> List[Dict]:
        """Deduplica commits similares agrupándolos por descripción."""
        if not commits:
            return commits

        # Agrupar commits por descripción normalizada
        grouped_commits = {}

        for commit in commits:
            # Normalizar descripción para comparación
            normalized_desc = self._normalize_description(commit['description'])

            if normalized_desc not in grouped_commits:
                grouped_commits[normalized_desc] = {
                    'commits': [],
                    'count': 0,
                    'representative': commit
                }

            grouped_commits[normalized_desc]['commits'].append(commit)
            grouped_commits[normalized_desc]['count'] += 1

        # Crear lista deduplicada
        deduplicated = []

        for normalized_desc, group in grouped_commits.items():
            if group['count'] == 1:
                # Commit único, mantener como está
                deduplicated.append(group['representative'])
            else:
                # Commits duplicados, crear uno consolidado
                consolidated = self._consolidate_commits(group['commits'])
                deduplicated.append(consolidated)

        return deduplicated

    def _normalize_description(self, description: str) -> str:
        """Normaliza una descripción para comparación."""
        # Convertir a minúsculas
        normalized = description.lower()

        # Remover palabras comunes que no aportan significado
        common_words = ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'de', 'del', 'a', 'al', 'en', 'con', 'por', 'para', 'sin', 'sobre', 'entre', 'tras', 'durante', 'mediante', 'según', 'contra', 'hacia', 'hasta', 'desde', 'hacia', 'cerca', 'lejos', 'dentro', 'fuera', 'arriba', 'abajo', 'antes', 'después', 'ahora', 'siempre', 'nunca', 'también', 'tampoco', 'muy', 'más', 'menos', 'poco', 'mucho', 'todo', 'nada', 'algo', 'nadie', 'alguien', 'cualquier', 'cualquiera', 'cada', 'varios', 'varias', 'algunos', 'algunas', 'ningún', 'ninguna', 'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'aquel', 'aquella', 'aquellos', 'aquellas', 'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras']

        # Remover palabras comunes
        words = normalized.split()
        filtered_words = [word for word in words if word not in common_words and len(word) > 2]

        # Unir palabras filtradas
        return ' '.join(filtered_words)

    def _consolidate_commits(self, commits: List[Dict]) -> Dict:
        """Consolida múltiples commits similares en uno solo."""
        if not commits:
            return {}

        # Usar el primer commit como base
        consolidated = commits[0].copy()

        # Si hay más de un commit, agregar indicador de cantidad
        if len(commits) > 1:
            count = len(commits)
            if count == 2:
                consolidated['description'] = f"{consolidated['description']} (2 commits)"
            else:
                consolidated['description'] = f"{consolidated['description']} ({count} commits)"

            # Agregar información de hashes para referencia
            hashes = [commit['hash'][:8] for commit in commits]
            consolidated['related_hashes'] = hashes

        return consolidated

class ContributingAnalyzer:
    """Analizador específico para generación de CONTRIBUTING.md."""

    def __init__(self, base_path: Path, config: Optional[Dict] = None):
        """Inicializa el analizador de CONTRIBUTING.

        Args:
            base_path: Ruta base del repositorio
            config: Configuración del analizador
        """
        self.base_path = base_path
        self.config = config or {}
        self.console = Console()

    def analyze_project(self) -> Dict:
        """Analiza el proyecto para generar CONTRIBUTING.md.

        Returns:
            Diccionario con análisis completo del proyecto
        """
        try:
            analysis = {
                'project_structure': self._analyze_project_structure(),
                'technologies': self._analyze_technologies(),
                'workflow': self._analyze_workflow(),
                'configuration': self._analyze_configuration(),
                'versioning': self._analyze_versioning_system(),
                'testing': self._analyze_testing_framework(),
                'documentation': self._analyze_documentation(),
                'security': self._analyze_security_tools()
            }

            # Determinar tipo de proyecto
            analysis['project_type'] = self._determine_project_type(analysis)

            return analysis

        except Exception as e:
            self.console.print(f"[red]Error analizando proyecto: {str(e)}[/red]")
            return {}

    def _analyze_project_structure(self) -> Dict:
        """Analiza la estructura del proyecto."""
        structure = {
            'is_monorepo': False,
            'main_components': [],
            'directory_structure': {},
            'package_files': []
        }

        # Detectar archivos de paquete
        package_files = []
        for pattern in ['package.json', 'setup.py', 'pyproject.toml', 'Pipfile', 'Cargo.toml', 'go.mod']:
            files = list(self.base_path.glob(pattern))
            package_files.extend([str(f) for f in files])

        structure['package_files'] = package_files
        structure['is_monorepo'] = len(package_files) > 1

        # Analizar estructura de directorios
        main_dirs = ['src', 'lib', 'app', 'backend', 'frontend', 'api', 'docs', 'tests', 'scripts']
        for dir_name in main_dirs:
            dir_path = self.base_path / dir_name
            if dir_path.exists():
                structure['directory_structure'][dir_name] = {
                    'exists': True,
                    'files': len(list(dir_path.rglob('*')))
                }
                structure['main_components'].append(dir_name)

        return structure

    def _analyze_technologies(self) -> Dict:
        """Analiza las tecnologías utilizadas en el proyecto."""
        technologies = {
            'languages': [],
            'frameworks': [],
            'build_tools': [],
            'dependencies': {}
        }

        # Detectar lenguajes de programación
        language_patterns = {
            'python': ['*.py', 'requirements.txt', 'setup.py', 'pyproject.toml'],
            'javascript': ['*.js', 'package.json'],
            'typescript': ['*.ts', 'tsconfig.json'],
            'bash': ['*.sh'],
            'go': ['*.go', 'go.mod'],
            'rust': ['*.rs', 'Cargo.toml']
        }

        for lang, patterns in language_patterns.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    technologies['languages'].append(lang)
                    break

        # Detectar frameworks
        framework_indicators = {
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py'],
            'react': ['package.json'],  # Solo si contiene dependencias de React
            'vue': ['vue.config.js', '*.vue'],
            'angular': ['angular.json']
        }

        for framework, indicators in framework_indicators.items():
            for indicator in indicators:
                files = list(self.base_path.glob(indicator))
                if files:
                    # Para React, verificar que realmente sea un proyecto React
                    if framework == 'react':
                        for file in files:
                            try:
                                import json
                                with open(file, 'r') as f:
                                    pkg_data = json.load(f)
                                    dependencies = pkg_data.get('dependencies', {})
                                    dev_dependencies = pkg_data.get('devDependencies', {})
                                    all_deps = {**dependencies, **dev_dependencies}

                                    # Solo detectar React si tiene dependencias específicas de React
                                    react_deps = ['react', 'react-dom', '@types/react', '@types/react-dom']
                                    if any(dep in all_deps for dep in react_deps):
                                        technologies['frameworks'].append(framework)
                                        break
                            except:
                                continue
                    else:
                        technologies['frameworks'].append(framework)
                    break

        # Detectar herramientas de build
        build_tools = {
            'webpack': ['webpack.config.js'],
            'vite': ['vite.config.js'],
            'poetry': ['pyproject.toml'],
            'pipenv': ['Pipfile']
        }

        for tool, indicators in build_tools.items():
            for indicator in indicators:
                files = list(self.base_path.glob(indicator))
                if files:
                    technologies['build_tools'].append(tool)
                    break

        return technologies

    def _analyze_workflow(self) -> Dict:
        """Analiza el flujo de trabajo de Git y CI/CD."""
        workflow = {
            'git_workflow': 'unknown',
            'ci_cd_tools': [],
            'code_quality_tools': [],
            'branch_strategy': 'unknown',
            'commit_hooks': [],
            'commit_format': 'unknown',
            'pre_commit_hooks': [],
            'ci_pipelines': []
        }

        # Detectar herramientas de CI/CD
        ci_patterns = {
            'github_actions': ['.github/workflows/*.yml', '.github/workflows/*.yaml'],
            'gitlab_ci': ['.gitlab-ci.yml'],
            'jenkins': ['Jenkinsfile', 'Jenkinsfile.groovy'],
            'circleci': ['.circleci/config.yml'],
            'bitbucket_pipelines': ['bitbucket-pipelines.yml'],
            'azure_devops': ['.azure-pipelines.yml', 'azure-pipelines.yml'],
            'travis_ci': ['.travis.yml']
        }

        for ci_tool, patterns in ci_patterns.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    workflow['ci_cd_tools'].append(ci_tool)
                    workflow['ci_pipelines'].extend([str(f) for f in files])
                    break

        # Detectar configuración de commitlint y formato de commits
        commitlint_configs = [
            'commitlint.config.js',
            'commitlint.config.ts',
            '.commitlintrc.js',
            '.commitlintrc.json',
            '.commitlintrc.yml'
        ]

        for config_file in commitlint_configs:
            config_path = self.base_path / config_file
            if config_path.exists():
                workflow['commit_hooks'].append('commitlint')
                # Intentar determinar el formato de commits
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                        if 'conventional' in content.lower():
                            workflow['commit_format'] = 'conventional'
                        elif 'semantic' in content.lower():
                            workflow['commit_format'] = 'semantic'
                        elif 'angular' in content.lower():
                            workflow['commit_format'] = 'angular'
                        elif 'minimal' in content.lower():
                            workflow['commit_format'] = 'minimal'
                        else:
                            workflow['commit_format'] = 'custom'
                except:
                    workflow['commit_format'] = 'unknown'
                break

        # Detectar configuración de pre-commit hooks
        pre_commit_configs = [
            '.pre-commit-config.yaml',
            '.pre-commit-config.yml',
            'pre-commit-config.yaml',
            'pre-commit-config.yml'
        ]

        for config_file in pre_commit_configs:
            config_path = self.base_path / config_file
            if config_path.exists():
                workflow['pre_commit_hooks'].append('pre-commit')
                # Intentar leer los hooks configurados
                try:
                    import yaml
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                        if 'repos' in config:
                            for repo in config['repos']:
                                if 'hooks' in repo:
                                    for hook in repo['hooks']:
                                        hook_name = hook.get('id', 'unknown')
                                        workflow['pre_commit_hooks'].append(hook_name)
                except:
                    pass
                break

        # Detectar configuración de Git hooks personalizados
        git_hooks_dirs = ['.githooks', '.git/hooks', 'hooks']
        for hook_dir in git_hooks_dirs:
            hook_path = self.base_path / hook_dir
            if hook_path.exists():
                workflow['commit_hooks'].append('custom_git_hooks')
                # Listar hooks disponibles
                hook_files = list(hook_path.glob('*'))
                for hook_file in hook_files:
                    if hook_file.is_file() and not hook_file.name.startswith('.'):
                        workflow['commit_hooks'].append(f"hook_{hook_file.name}")

        # Detectar herramientas de calidad de código
        quality_tools = {
            'eslint': ['.eslintrc*', 'eslint.config.js'],
            'flake8': ['.flake8', 'setup.cfg'],
            'black': ['pyproject.toml', 'setup.cfg'],
            'pylint': ['.pylintrc', 'pyproject.toml'],
            'shellcheck': ['.shellcheckrc', '.shellcheck'],
            'stylelint': ['.stylelintrc*', 'stylelint.config.js'],
            'prettier': ['.prettierrc*', 'prettier.config.js'],
            'rubocop': ['.rubocop.yml', '.rubocop.yaml'],
            'gofmt': ['go.mod'],  # Indicador de Go
            'rustfmt': ['Cargo.toml']  # Indicador de Rust
        }

        for tool, patterns in quality_tools.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    workflow['code_quality_tools'].append(tool)
                    break

        # Determinar estrategia de ramas y workflow
        if (self.base_path / '.githooks').exists() or 'pre-commit' in workflow['pre_commit_hooks']:
            workflow['branch_strategy'] = 'gitflow'
        elif 'github_actions' in workflow['ci_cd_tools']:
            workflow['git_workflow'] = 'github_flow'
        elif 'gitlab_ci' in workflow['ci_cd_tools']:
            workflow['git_workflow'] = 'gitlab_flow'

        # Detectar estrategia de ramas basada en configuración
        if (self.base_path / '.gitflow').exists() or (self.base_path / 'gitflow').exists():
            workflow['branch_strategy'] = 'gitflow'
        elif any('main' in str(f) for f in self.base_path.glob('.github/workflows/*.yml')):
            workflow['branch_strategy'] = 'trunk_based'

        return workflow

    def _analyze_configuration(self) -> Dict:
        """Analiza la configuración del proyecto."""
        config = {
            'git_hooks': [],
            'linting_config': {},
            'formatting_config': {},
            'editor_config': {},
            'active_hooks': [],
            'hook_configurations': {}
        }

        # Detectar configuración de Git hooks activos
        hook_patterns = {
            'pre_commit': ['.pre-commit-config.yaml', '.pre-commit-config.yml'],
            'husky': ['package.json'],  # Buscar scripts de husky
            'git_hooks': ['.githooks/*'],
            'custom_hooks': ['hooks/*', '.git/hooks/*']
        }

        for hook_type, patterns in hook_patterns.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    config['git_hooks'].append(hook_type)
                    config['active_hooks'].append(hook_type)

                    # Analizar configuración específica de cada tipo de hook
                    if hook_type == 'pre_commit':
                        for file in files:
                            try:
                                import yaml
                                with open(file, 'r') as f:
                                    hook_config = yaml.safe_load(f)
                                    config['hook_configurations']['pre_commit'] = {
                                        'file': str(file),
                                        'repos': len(hook_config.get('repos', [])),
                                        'hooks': []
                                    }
                                    for repo in hook_config.get('repos', []):
                                        for hook in repo.get('hooks', []):
                                            config['hook_configurations']['pre_commit']['hooks'].append({
                                                'id': hook.get('id', 'unknown'),
                                                'name': hook.get('name', ''),
                                                'stages': hook.get('stages', [])
                                            })
                            except Exception as e:
                                config['hook_configurations']['pre_commit'] = {'error': str(e)}

                    elif hook_type == 'husky':
                        for file in files:
                            try:
                                import json
                                with open(file, 'r') as f:
                                    pkg_config = json.load(f)
                                    if 'husky' in pkg_config:
                                        config['hook_configurations']['husky'] = {
                                            'file': str(file),
                                            'hooks': list(pkg_config['husky'].keys())
                                        }
                            except Exception as e:
                                config['hook_configurations']['husky'] = {'error': str(e)}

                    elif hook_type == 'git_hooks':
                        for file in files:
                            if file.is_file():
                                config['hook_configurations']['git_hooks'] = {
                                    'file': str(file),
                                    'type': 'custom_git_hook'
                                }
                    break

        # Detectar configuración de commitlint activa
        commitlint_configs = [
            'commitlint.config.js',
            'commitlint.config.ts',
            '.commitlintrc.js',
            '.commitlintrc.json',
            '.commitlintrc.yml'
        ]

        for config_file in commitlint_configs:
            config_path = self.base_path / config_file
            if config_path.exists():
                config['active_hooks'].append('commitlint')
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                        config['hook_configurations']['commitlint'] = {
                            'file': str(config_path),
                            'content_preview': content[:200] + '...' if len(content) > 200 else content
                        }
                except Exception as e:
                    config['hook_configurations']['commitlint'] = {'error': str(e)}
                break

        # Detectar configuración de linting
        linting_configs = {
            'eslint': ['.eslintrc*', 'eslint.config.js'],
            'flake8': ['.flake8', 'setup.cfg'],
            'pylint': ['.pylintrc', 'pyproject.toml'],
            'shellcheck': ['.shellcheckrc', '.shellcheck'],
            'stylelint': ['.stylelintrc*', 'stylelint.config.js'],
            'rubocop': ['.rubocop.yml', '.rubocop.yaml']
        }

        for linter, patterns in linting_configs.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    config['linting_config'][linter] = {
                        'active': True,
                        'files': [str(f) for f in files]
                    }
                    break
                else:
                    config['linting_config'][linter] = {'active': False}

        # Detectar configuración de formateo
        formatting_configs = {
            'black': ['pyproject.toml', 'setup.cfg'],
            'prettier': ['.prettierrc*', 'prettier.config.js'],
            'gofmt': ['go.mod'],
            'rustfmt': ['Cargo.toml']
        }

        for formatter, patterns in formatting_configs.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    config['formatting_config'][formatter] = {
                        'active': True,
                        'files': [str(f) for f in files]
                    }
                    break
                else:
                    config['formatting_config'][formatter] = {'active': False}

        # Detectar configuración del editor
        editor_configs = {
            'vscode': ['.vscode/settings.json', '.vscode/launch.json'],
            'vim': ['.vimrc', '.vim'],
            'emacs': ['.emacs', '.emacs.d'],
            'editorconfig': ['.editorconfig']
        }

        for editor, patterns in editor_configs.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    config['editor_config'][editor] = {
                        'active': True,
                        'files': [str(f) for f in files]
                    }
                    break
                else:
                    config['editor_config'][editor] = {'active': False}

        return config

    def _analyze_versioning_system(self) -> Dict:
        """Analiza el sistema de versionado."""
        versioning = {
            'type': 'unknown',
            'semantic_versioning': False,
            'conventional_commits': False,
            'auto_versioning': False,
            'version_files': []
        }

        # Detectar archivos de versión
        version_patterns = ['VERSION', 'version.py', 'version.txt']
        for pattern in version_patterns:
            files = list(self.base_path.glob(f'**/{pattern}'))
            versioning['version_files'].extend([str(f) for f in files])

        # Detectar conventional commits
        if (self.base_path / 'commitlint.config.js').exists():
            versioning['conventional_commits'] = True
            versioning['type'] = 'conventional'

        # Detectar versionado semántico
        if versioning['version_files'] or 'conventional_commits' in versioning:
            versioning['semantic_versioning'] = True

        return versioning

    def _analyze_testing_framework(self) -> Dict:
        """Analiza el framework de testing."""
        testing = {
            'frameworks': [],
            'coverage_tools': [],
            'test_directories': []
        }

        # Detectar frameworks de testing
        test_frameworks = {
            'pytest': ['pytest.ini', 'pyproject.toml'],
            'jest': ['package.json'],
            'mocha': ['package.json'],
            'cypress': ['cypress.config.js'],
            'playwright': ['playwright.config.js']
        }

        for framework, patterns in test_frameworks.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    testing['frameworks'].append(framework)
                    break

        # Detectar directorios de tests
        test_dirs = ['tests', 'test', '__tests__', 'spec']
        for dir_name in test_dirs:
            dir_path = self.base_path / dir_name
            if dir_path.exists():
                testing['test_directories'].append(dir_name)

        return testing

    def _analyze_documentation(self) -> Dict:
        """Analiza la documentación del proyecto."""
        documentation = {
            'tools': [],
            'formats': [],
            'directories': []
        }

        # Detectar herramientas de documentación
        doc_tools = {
            'sphinx': ['docs/conf.py'],
            'mkdocs': ['mkdocs.yml'],
            'docusaurus': ['docusaurus.config.js'],
            'storybook': ['.storybook/main.js']
        }

        for tool, patterns in doc_tools.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    documentation['tools'].append(tool)
                    break

        # Detectar formatos de documentación
        doc_formats = ['*.md', '*.rst', '*.txt']
        for pattern in doc_formats:
            files = list(self.base_path.glob(pattern))
            if files:
                ext = pattern.split('.')[-1]
                if ext not in documentation['formats']:
                    documentation['formats'].append(ext)

        # Detectar directorios de documentación
        doc_dirs = ['docs', 'documentation', 'doc']
        for dir_name in doc_dirs:
            dir_path = self.base_path / dir_name
            if dir_path.exists():
                documentation['directories'].append(dir_name)

        return documentation

    def _analyze_security_tools(self) -> Dict:
        """Analiza las herramientas de seguridad."""
        security = {
            'tools': [],
            'practices': []
        }

        # Detectar herramientas de seguridad
        security_tools = {
            'snyk': ['.snyk'],
            'bandit': ['pyproject.toml'],
            'safety': ['requirements.txt'],
            'npm_audit': ['package.json']
        }

        for tool, patterns in security_tools.items():
            for pattern in patterns:
                files = list(self.base_path.glob(pattern))
                if files:
                    security['tools'].append(tool)
                    break

        return security

    def _determine_project_type(self, analysis: Dict) -> str:
        """Determina el tipo de proyecto basado en el análisis."""
        structure = analysis.get('project_structure', {})
        technologies = analysis.get('technologies', {})

        if structure.get('is_monorepo'):
            return 'monorepo'

        frameworks = technologies.get('frameworks', [])
        if 'django' in frameworks or 'flask' in frameworks:
            return 'web_app'
        elif 'react' in frameworks or 'vue' in frameworks or 'angular' in frameworks:
            return 'web_app'

        languages = technologies.get('languages', [])
        if 'bash' in languages and len(languages) == 1:
            return 'cli_tool'

        if 'python' in languages and 'javascript' not in languages:
            return 'library'

        return 'single_repo'

class DocumentationGenerator:
    """Generador de documentación usando IA."""

    def __init__(self, base_path: Path, doc_type: str, context: Optional[str] = None, custom_type: Optional[str] = None, model: Optional[str] = None):
        """Inicializa el generador de documentación y carga toda la configuración."""
        self.base_path = Path(base_path)
        self.console = Console()
        self.client = anthropic.Anthropic(api_key=AnthropicAuth.get_api_token())
        self.analyzer = None
        self._analyzer_initialized = False

        # Cargar toda la configuración en el constructor
        self.config = self._load_config(doc_type, context, custom_type)

        # Usar el modelo de la configuración si no se proporcionó uno
        self.model = model or self.config.get('model')

        # Inicializar el analizador
        if not self._analyzer_initialized:
            self._initialize_analyzer(self.config)

    def _initialize_analyzer(self, config: Dict) -> None:
        """Inicializa el analizador apropiado según el tipo de documento."""
        if self._analyzer_initialized:
            return

        # Para CHANGELOG, usar ChangelogAnalyzer
        if self.config.get('doc_type') == 'changelog':
            self.analyzer = ChangelogAnalyzer(self.base_path, config)
            if not self.analyzer:
                raise RuntimeError("No se pudo inicializar el analizador de CHANGELOG")
        # Para CONTRIBUTING, usar ContributingAnalyzer
        elif self.config.get('doc_type') == 'contributing':
            self.analyzer = ContributingAnalyzer(self.base_path, config)
            if not self.analyzer:
                raise RuntimeError("No se pudo inicializar el analizador de CONTRIBUTING")
        # Para PROJECT_DESCRIPTION, usar ProjectDescriptionAnalyzer
        elif self.config.get('doc_type') == 'project_description':
            self.analyzer = ProjectDescriptionAnalyzer(self.base_path, config)
            if not self.analyzer:
                raise RuntimeError("No se pudo inicializar el analizador de PROJECT_DESCRIPTION")
        # Para README, usar ProjectDescriptionAnalyzer también
        elif self.config.get('doc_type') == 'readme':
            self.analyzer = ProjectDescriptionAnalyzer(self.base_path, config)
            if not self.analyzer:
                raise RuntimeError("No se pudo inicializar el analizador de README")
        else:
            # Para otros tipos de documento, usar CodeAnalyzer
            self.analyzer = CodeAnalyzer(self.base_path, config)
            if not self.analyzer:
                raise RuntimeError("No se pudo inicializar el analizador de código")

            required_methods = ['_analyze_workflows', '_analyze_examples', '_analyze_configs', '_analyze_dependencies', '_analyze_use_cases']
            for method in required_methods:
                if not hasattr(self.analyzer, method):
                    raise RuntimeError(f"El analizador no tiene el método requerido: {method}")

        self._analyzer_initialized = True
        self.console.print("✓ [green]Analizador inicializado correctamente[/green]")

    def _load_config(self, doc_type: str, context: Optional[str] = None, custom_type: Optional[str] = None) -> Dict:
        """Carga toda la configuración necesaria desde los archivos YAML."""
        # Configuración base con valores por defecto
        config = {
            'model': 'claude-3-sonnet-20240229',  # Modelo por defecto
            'max_tokens': 4000,
            'temperature': 0.7,
            'doc_type': doc_type,
            'context': context,
            'custom_type': custom_type,
            'analysis': {
                'types': ['workflows', 'examples', 'configs', 'dependencies', 'use_cases']
            }
        }

        # 1. Cargar configuración del modelo
        model_config_path = self.base_path / 'docs/config/model.yaml'
        if model_config_path.exists():
            try:
                with open(model_config_path, 'r', encoding='utf-8') as f:
                    model_config = yaml.safe_load(f)

                # Usar configuración específica del tipo de documento si existe
                doc_type_config = model_config.get('document_types', {}).get(doc_type, {})
                if doc_type_config:
                    config.update({
                        'model': doc_type_config.get('model', config['model']),
                        'max_tokens': doc_type_config.get('max_tokens', config['max_tokens']),
                        'temperature': doc_type_config.get('temperature', config['temperature'])
                    })
                else:
                    # Usar configuración por defecto
                    default_config = model_config.get('default', {})
                    config.update({
                        'model': default_config.get('model', config['model']),
                        'max_tokens': default_config.get('max_tokens', config['max_tokens']),
                        'temperature': default_config.get('temperature', config['temperature'])
                    })
            except Exception as e:
                self.console.print(f"[yellow]⚠ Advertencia: Error cargando configuración del modelo: {str(e)}[/yellow]")
        else:
            self.console.print("[yellow]⚠ Advertencia: No se encontró docs/config/model.yaml[/yellow]")

        # 2. Cargar configuración de análisis específica por tipo de documento
        if doc_type == 'contributing':
            # Para CONTRIBUTING.md, cargar configuración específica
            analysis_config_path = self.base_path / 'docs/config/analysis/contributing.yaml'
            if analysis_config_path.exists():
                try:
                    with open(analysis_config_path, 'r', encoding='utf-8') as f:
                        analysis_config = yaml.safe_load(f)
                        config['analysis'].update(analysis_config.get('analysis_methods', {}))
                except Exception as e:
                    self.console.print(f"[yellow]⚠ Advertencia: Error cargando configuración de análisis de CONTRIBUTING: {str(e)}[/yellow]")
            else:
                self.console.print("[yellow]⚠ Advertencia: No se encontró docs/config/analysis/contributing.yaml[/yellow]")
        elif doc_type == 'project_description':
            # Para PROJECT_DESCRIPTION, cargar configuración específica
            analysis_config_path = self.base_path / 'docs/config/analysis/project_description.yaml'
            if analysis_config_path.exists():
                try:
                    with open(analysis_config_path, 'r', encoding='utf-8') as f:
                        analysis_config = yaml.safe_load(f)
                        config['analysis'].update(analysis_config.get('project_description_analysis', {}))
                except Exception as e:
                    self.console.print(f"[yellow]⚠ Advertencia: Error cargando configuración de análisis de PROJECT_DESCRIPTION: {str(e)}[/yellow]")
            else:
                self.console.print("[yellow]⚠ Advertencia: No se encontró docs/config/analysis/project_description.yaml[/yellow]")
        else:
            # Para otros tipos, cargar configuración por defecto
            analysis_config_path = self.base_path / 'docs/config/analysis/default.yaml'
            if analysis_config_path.exists():
                try:
                    with open(analysis_config_path, 'r', encoding='utf-8') as f:
                        analysis_config = yaml.safe_load(f)
                        config['analysis'].update(analysis_config.get('default_analysis', {}))
                except Exception as e:
                    self.console.print(f"[yellow]⚠ Advertencia: Error cargando configuración de análisis: {str(e)}[/yellow]")
            else:
                self.console.print("[yellow]⚠ Advertencia: No se encontró docs/config/analysis/default.yaml[/yellow]")

        # 3. Cargar configuración específica si existe
        if custom_type:
            # 3.1 Cargar configuración de análisis personalizada
            custom_config_path = self.base_path / f'docs/config/analysis/{custom_type}.yaml'
            if custom_config_path.exists():
                try:
                    with open(custom_config_path, 'r', encoding='utf-8') as f:
                        custom_config = yaml.safe_load(f)
                        # Actualizar configuración con valores específicos
                        if custom_type in custom_config:
                            config['analysis'].update(custom_config[custom_type].get('analysis', {}))
                except Exception as e:
                    self.console.print(f"[yellow]⚠ Advertencia: Error cargando configuración personalizada: {str(e)}[/yellow]")
            else:
                self.console.print(f"[yellow]⚠ Advertencia: No se encontró docs/config/analysis/{custom_type}.yaml[/yellow]")

            # 3.2 Cargar configuración TOC personalizada
            custom_toc_path = self.base_path / f'docs/config/toc/custom/{custom_type}.yaml'
            if custom_toc_path.exists():
                try:
                    with open(custom_toc_path, 'r', encoding='utf-8') as f:
                        custom_toc = yaml.safe_load(f)
                        config['toc'] = custom_toc
                except Exception as e:
                    self.console.print(f"[yellow]⚠ Advertencia: Error cargando TOC personalizado: {str(e)}[/yellow]")
            else:
                self.console.print(f"[yellow]⚠ Advertencia: No se encontró docs/config/toc/custom/{custom_type}.yaml[/yellow]")

        # 4. Cargar TOC base para CONTRIBUTING.md si no hay TOC personalizado
        if doc_type == 'contributing' and 'toc' not in config:
            toc_path = self.base_path / 'docs/config/toc/base/contributing.yaml'
            if toc_path.exists():
                try:
                    with open(toc_path, 'r', encoding='utf-8') as f:
                        toc_config = yaml.safe_load(f)
                        config['toc'] = toc_config
                except Exception as e:
                    self.console.print(f"[yellow]⚠ Advertencia: Error cargando TOC base de CONTRIBUTING: {str(e)}[/yellow]")

        # 5. Cargar TOC base para PROJECT_DESCRIPTION si no hay TOC personalizado
        if doc_type == 'project_description' and 'toc' not in config:
            toc_path = self.base_path / 'docs/config/toc/base/project_description.yaml'
            if toc_path.exists():
                try:
                    with open(toc_path, 'r', encoding='utf-8') as f:
                        toc_config = yaml.safe_load(f)
                        config['toc'] = toc_config
                except Exception as e:
                    self.console.print(f"[yellow]⚠ Advertencia: Error cargando TOC base de PROJECT_DESCRIPTION: {str(e)}[/yellow]")

        return config

    def generate_documentation(self, output_file: str, custom_instructions: Optional[str] = None, use_ai: bool = False) -> None:
        """Genera la documentación usando el modelo de Anthropic."""
        try:
            # Para CHANGELOG, usar generación sin IA por defecto
            if self.config.get('doc_type') == 'changelog':
                self._generate_changelog(output_file, custom_instructions, use_ai)
                return

            # Para CONTRIBUTING, usar análisis de proyecto
            if self.config.get('doc_type') == 'contributing':
                self._generate_contributing(output_file, custom_instructions, use_ai)
                return

            # Para README, usar nuestro sistema híbrido
            if self.config.get('doc_type') == 'readme':
                self._generate_readme_hybrid(output_file, custom_instructions, use_ai)
                return

            # Para PROJECT_DESCRIPTION, usar análisis de proyecto específico
            if self.config.get('doc_type') == 'project_description':
                self._generate_project_description(output_file, custom_instructions, use_ai)
                return

            # Para otros tipos de documento, usar el flujo normal con IA
            # 1. Analizar el código base
            if hasattr(self, 'progress') and hasattr(self, 'analysis_task'):
                self.analyzer.progress = self.progress
                self.analyzer.analysis_task = self.analysis_task

            analysis = self._analyze_codebase()

            # 2. Construir el prompt
            prompt = self._build_prompt(self.config, analysis, custom_instructions)

            # 3. Generar la documentación con el modelo
            self.console.print("[blue]Generando documentación con IA...[/blue]")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config.get('max_tokens', 4000),
                temperature=self.config.get('temperature', 0.7),
                system=prompt,
                messages=[
                    {
                        "role": "user",
                        "content": "Genera la documentación técnica completa basada en el análisis del código proporcionado."
                    }
                ]
            )

            # 4. Guardar la documentación
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.content[0].text)

            self.console.print(f"✓ Documentación generada y guardada en: {output_file}")

        except Exception as e:
            self.console.print(f"[red]Error generando documentación: {str(e)}[/red]")
            raise

    def _generate_changelog(self, output_file: str, custom_instructions: Optional[str] = None, use_ai: bool = False) -> None:
        """Genera CHANGELOG específicamente."""
        try:
            self.console.print("[blue]Analizando historial de Git para CHANGELOG...[/blue]")

            # Analizar historial de Git
            analysis = self.analyzer.analyze_git_history()

            if not analysis:
                self.console.print("[yellow]No se encontraron commits para generar CHANGELOG[/yellow]")
                return

            # Generar contenido del CHANGELOG
            if use_ai:
                self.console.print("[blue]Generando contenido del CHANGELOG con IA...[/blue]")
            else:
                self.console.print("[blue]Generando contenido del CHANGELOG sin IA...[/blue]")

            changelog_content = self.analyzer.generate_changelog_content(analysis, use_ai=use_ai)

            # Guardar el CHANGELOG
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(changelog_content)

            # Mostrar estadísticas
            statistics = analysis.get('statistics', {})
            self.console.print(f"[green]✓ CHANGELOG generado y guardado en: {output_file}[/green]")
            self.console.print(f"[blue]📊 Estadísticas: {statistics.get('total_commits', 0)} commits analizados[/blue]")

            if statistics.get('has_breaking_changes'):
                self.console.print("[red]⚠ Breaking changes detectados[/red]")
            if statistics.get('has_security_updates'):
                self.console.print("[orange]🔒 Actualizaciones de seguridad detectadas[/orange]")
            if statistics.get('has_deprecations'):
                self.console.print("[yellow]⚠ Deprecaciones detectadas[/yellow]")

        except Exception as e:
            self.console.print(Panel(
                f"[bold red]✗ Error generando CHANGELOG[/bold red]\n{str(e)}",
                border_style="red"
            ))
            raise click.Abort()

    def _generate_contributing(self, output_file: str, custom_instructions: Optional[str] = None, use_ai: bool = False) -> None:
        """Genera CONTRIBUTING.md específicamente."""
        try:
            self.console.print("[blue]Analizando estructura del proyecto para CONTRIBUTING.md...[/blue]")

            # Analizar proyecto
            analysis = self.analyzer.analyze_project()

            if not analysis:
                self.console.print("[yellow]No se pudo analizar el proyecto para generar CONTRIBUTING.md[/yellow]")
                return

            # Generar contenido del CONTRIBUTING.md
            if use_ai:
                self.console.print("[blue]Generando contenido del CONTRIBUTING.md con IA...[/blue]")
                content = self._generate_contributing_with_ai(analysis, custom_instructions)
            else:
                self.console.print("[blue]Generando contenido del CONTRIBUTING.md sin IA...[/blue]")
                content = self._generate_contributing_without_ai(analysis)

            # Guardar el CONTRIBUTING.md
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Mostrar información del análisis
            project_type = analysis.get('project_type', 'unknown')
            technologies = analysis.get('technologies', {})
            languages = technologies.get('languages', [])

            self.console.print(f"[green]✓ CONTRIBUTING.md generado y guardado en: {output_file}[/green]")
            self.console.print(f"[blue]📊 Tipo de proyecto: {project_type}[/blue]")
            self.console.print(f"[blue]🔧 Tecnologías detectadas: {', '.join(languages)}[/blue]")

        except Exception as e:
            self.console.print(Panel(
                f"[bold red]✗ Error generando CONTRIBUTING.md[/bold red]\n{str(e)}",
                border_style="red"
            ))
            raise click.Abort()

    def _generate_project_description(self, output_file: str, custom_instructions: Optional[str] = None, use_ai: bool = False) -> None:
        """Genera README.md usando enfoque híbrido con mejores prácticas."""
        try:
            # 1. Analizar el proyecto
            self.console.print("Analizando proyecto para README.md...")
            analysis = self.analyzer.analyze_project()

            # 2. Generar contenido base sin IA
            self.console.print("Generando contenido base de README.md...")
            base_content = self._generate_readme_without_ai(analysis)

            # 3. Si se solicita IA, mejorar el contenido
            if use_ai:
                self.console.print("Mejorando contenido con IA...")
                enhanced_content = self._enhance_readme_with_ai(base_content, analysis, custom_instructions)
                final_content = enhanced_content
            else:
                final_content = base_content

            # 4. Guardar el archivo
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            self.console.print(f"✓ README.md generado y guardado en: {output_file}")

        except Exception as e:
            self.console.print(f"[red]Error generando README.md: {str(e)}[/red]")
            raise

    def _generate_contributing_without_ai(self, analysis: Dict) -> str:
        """Genera CONTRIBUTING.md sin usar IA, basado en el análisis del proyecto."""
        project_type = analysis.get('project_type', 'unknown')
        structure = analysis.get('structure', {})
        technologies = analysis.get('technologies', {})
        workflow = analysis.get('workflow', {})
        configuration = analysis.get('configuration', {})
        versioning = analysis.get('versioning', {})
        testing = analysis.get('testing', {})
        documentation = analysis.get('documentation', {})
        security = analysis.get('security', {})

        # Leer descripción del proyecto si existe
        project_description = ""
        project_desc_path = self.base_path / '.project/description'
        if project_desc_path.exists():
            try:
                with open(project_desc_path, 'r', encoding='utf-8') as f:
                    project_description = f.read().strip()
            except:
                pass

        content = []

        # Título
        content.append("# Contributing")
        content.append("")

        # Descripción del proyecto
        if project_description:
            content.append(f"## Sobre este proyecto")
            content.append("")
            content.append(project_description)
            content.append("")
        else:
            content.append(f"## Sobre este proyecto")
            content.append("")
            content.append(f"Este es un proyecto de tipo **{project_type}** que utiliza las siguientes tecnologías principales:")
            content.append("")

            languages = technologies.get('languages', [])
            if languages:
                content.append(f"- **Lenguajes de programación**: {', '.join(languages)}")

            frameworks = technologies.get('frameworks', [])
            if frameworks:
                content.append(f"- **Frameworks**: {', '.join(frameworks)}")

            databases = technologies.get('databases', [])
            if databases:
                content.append(f"- **Bases de datos**: {', '.join(databases)}")
            content.append("")

        # Cómo contribuir
        content.append("## Cómo contribuir")
        content.append("")
        content.append("Agradecemos tu interés en contribuir a este proyecto. Aquí encontrarás toda la información necesaria para comenzar.")
        content.append("")

        # Configuración del entorno
        content.append("### Configuración del entorno de desarrollo")
        content.append("")

        # Detectar herramientas de gestión de dependencias
        package_managers = []
        if (self.base_path / 'requirements.txt').exists():
            package_managers.append("pip")
        if (self.base_path / 'package.json').exists():
            package_managers.append("npm")
        if (self.base_path / 'Cargo.toml').exists():
            package_managers.append("cargo")
        if (self.base_path / 'go.mod').exists():
            package_managers.append("go modules")

        if package_managers:
            content.append("#### Instalación de dependencias")
            content.append("")
            for pm in package_managers:
                if pm == "pip":
                    content.append("```bash")
                    content.append("pip install -r requirements.txt")
                    content.append("```")
                elif pm == "npm":
                    content.append("```bash")
                    content.append("npm install")
                    content.append("```")
                elif pm == "cargo":
                    content.append("```bash")
                    content.append("cargo build")
                    content.append("```")
                elif pm == "go modules":
                    content.append("```bash")
                    content.append("go mod download")
                    content.append("```")
            content.append("")

        # Configuración de hooks y herramientas de calidad
        active_hooks = configuration.get('active_hooks', [])
        if active_hooks:
            content.append("#### Configuración de hooks y herramientas de calidad")
            content.append("")

            if 'pre-commit' in active_hooks:
                content.append("Este proyecto utiliza **pre-commit hooks** para mantener la calidad del código:")
                content.append("")
                content.append("```bash")
                content.append("pip install pre-commit")
                content.append("pre-commit install")
                content.append("```")
                content.append("")

                # Mostrar hooks configurados
                pre_commit_config = configuration.get('hook_configurations', {}).get('pre_commit', {})
                if 'hooks' in pre_commit_config:
                    content.append("**Hooks configurados:**")
                    content.append("")
                    for hook in pre_commit_config['hooks']:
                        hook_id = hook.get('id', 'unknown')
                        hook_name = hook.get('name', '')
                        if hook_name:
                            content.append(f"- **{hook_id}**: {hook_name}")
                        else:
                            content.append(f"- **{hook_id}**")
                    content.append("")

            if 'commitlint' in active_hooks:
                content.append("Este proyecto utiliza **commitlint** para validar el formato de los mensajes de commit:")
                content.append("")
                commit_format = workflow.get('commit_format', 'unknown')
                if commit_format != 'unknown':
                    content.append(f"**Formato de commits**: {commit_format}")
                    content.append("")
                    if commit_format == 'conventional':
                        content.append("Los commits deben seguir el formato Conventional Commits:")
                        content.append("")
                        content.append("```")
                        content.append("<type>[optional scope]: <description>")
                        content.append("")
                        content.append("[optional body]")
                        content.append("")
                        content.append("[optional footer(s)]")
                        content.append("```")
                        content.append("")
                        content.append("**Tipos válidos**: feat, fix, docs, style, refactor, test, chore")
                        content.append("")

            # Mostrar otros hooks activos
            other_hooks = [hook for hook in active_hooks if hook not in ['pre-commit', 'commitlint']]
            if other_hooks:
                content.append("**Otros hooks activos:**")
                content.append("")
                for hook in other_hooks:
                    content.append(f"- **{hook}**")
                content.append("")

        # Flujo de trabajo
        content.append("### Flujo de trabajo")
        content.append("")

        git_workflow = workflow.get('git_workflow', 'unknown')
        branch_strategy = workflow.get('branch_strategy', 'unknown')

        if branch_strategy != 'unknown':
            content.append(f"**Estrategia de ramas**: {branch_strategy}")
            content.append("")

            if branch_strategy == 'gitflow':
                content.append("1. Crea una rama feature desde `develop`")
                content.append("2. Realiza tus cambios y commits")
                content.append("3. Crea un Pull Request hacia `develop`")
                content.append("4. Después de la revisión, se mergea a `develop`")
                content.append("5. Para releases, se crea una rama desde `develop` hacia `main`")
            elif branch_strategy == 'trunk_based':
                content.append("1. Crea una rama feature desde `main`")
                content.append("2. Realiza tus cambios y commits")
                content.append("3. Crea un Pull Request hacia `main`")
                content.append("4. Después de la revisión, se mergea a `main`")
        else:
            content.append("1. Crea una rama feature desde la rama principal")
            content.append("2. Realiza tus cambios y commits")
            content.append("3. Crea un Pull Request")
            content.append("4. Después de la revisión, se mergea")
        content.append("")

        # Herramientas de CI/CD
        ci_cd_tools = workflow.get('ci_cd_tools', [])
        if ci_cd_tools:
            content.append("### Integración Continua")
            content.append("")
            content.append("Este proyecto utiliza las siguientes herramientas de CI/CD:")
            content.append("")
            for tool in ci_cd_tools:
                content.append(f"- **{tool}**")
            content.append("")
            content.append("Los pipelines se ejecutan automáticamente en cada Pull Request.")
            content.append("")

        # Estándares de código
        content.append("### Estándares de código")
        content.append("")

        # Herramientas de linting activas
        linting_config = configuration.get('linting_config', {})
        active_linters = [linter for linter, config in linting_config.items() if config.get('active', False)]

        if active_linters:
            content.append("**Herramientas de linting configuradas:**")
            content.append("")
            for linter in active_linters:
                content.append(f"- **{linter}**")
            content.append("")
            content.append("Asegúrate de que tu código pase todas las validaciones antes de hacer commit.")
            content.append("")
        else:
            content.append("Este proyecto no tiene herramientas de linting específicas configuradas.")
            content.append("")

        # Herramientas de formateo
        formatting_config = configuration.get('formatting_config', {})
        active_formatters = [formatter for formatter, config in formatting_config.items() if config.get('active', False)]

        if active_formatters:
            content.append("**Herramientas de formateo configuradas:**")
            content.append("")
            for formatter in active_formatters:
                content.append(f"- **{formatter}**")
            content.append("")
            content.append("Utiliza estas herramientas para mantener un estilo de código consistente.")
            content.append("")
        else:
            content.append("Este proyecto no tiene herramientas de formateo específicas configuradas.")
            content.append("")

        # Testing
        content.append("### Testing")
        content.append("")

        test_frameworks = testing.get('frameworks', [])
        if test_frameworks:
            content.append("**Frameworks de testing:**")
            content.append("")
            for framework in test_frameworks:
                content.append(f"- **{framework}**")
            content.append("")

            test_dirs = testing.get('test_directories', [])
            if test_dirs:
                content.append("**Directorios de tests:**")
                content.append("")
                for test_dir in test_dirs:
                    content.append(f"- `{test_dir}/`")
                content.append("")

            content.append("**Ejecutar tests:**")
            content.append("")
            for framework in test_frameworks:
                if framework == 'pytest':
                    content.append("```bash")
                    content.append("pytest")
                    content.append("```")
                elif framework == 'jest':
                    content.append("```bash")
                    content.append("npm test")
                    content.append("```")
                elif framework == 'mocha':
                    content.append("```bash")
                    content.append("npm test")
                    content.append("```")
            content.append("")
            content.append("Asegúrate de que todos los tests pasen antes de hacer commit.")
        else:
            content.append("Este proyecto no tiene frameworks de testing configurados específicamente.")
            content.append("")

        # Documentación
        content.append("### Documentación")
        content.append("")

        doc_tools = documentation.get('tools', [])
        if doc_tools:
            content.append("**Herramientas de documentación:**")
            content.append("")
            for tool in doc_tools:
                content.append(f"- **{tool}**")
            content.append("")

        doc_dirs = documentation.get('directories', [])
        if doc_dirs:
            content.append("**Directorios de documentación:**")
            content.append("")
            for doc_dir in doc_dirs:
                content.append(f"- `{doc_dir}/`")
            content.append("")

        content.append("Mantén la documentación actualizada con tus cambios.")
        content.append("")

        # Proceso de Pull Request
        content.append("### Proceso de Pull Request")
        content.append("")
        content.append("1. **Fork del repositorio** (si no tienes acceso directo)")
        content.append("2. **Crea una rama** para tu feature/fix")
        content.append("3. **Realiza tus cambios** siguiendo los estándares del proyecto")
        content.append("4. **Ejecuta los tests** localmente")
        content.append("5. **Haz commit** con mensajes descriptivos")
        content.append("6. **Crea el Pull Request** con una descripción clara")
        content.append("7. **Espera la revisión** y responde a los comentarios")
        content.append("8. **Una vez aprobado**, se mergeará al repositorio")
        content.append("")

        # Código de conducta
        content.append("### Código de conducta")
        content.append("")
        content.append("Este proyecto se compromete a proporcionar un entorno de contribución abierto y acogedor para todos.")
        content.append("")
        content.append("Al participar en este proyecto, aceptas respetar el código de conducta del proyecto.")
        content.append("")

        # Contacto
        content.append("### Contacto")
        content.append("")
        content.append("Si tienes preguntas sobre cómo contribuir, puedes:")
        content.append("")
        content.append("- Abrir un issue en el repositorio")
        content.append("- Contactar a los mantenedores del proyecto")
        content.append("")
        content.append("¡Gracias por contribuir!")
        content.append("")

        return "\n".join(content)

    def _generate_contributing_with_ai(self, analysis: Dict, custom_instructions: Optional[str] = None) -> str:
        """Genera CONTRIBUTING.md usando IA."""
        # Construir prompt específico para CONTRIBUTING.md
        prompt = self._build_contributing_prompt(analysis, custom_instructions)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.config.get('max_tokens', 8000),
            temperature=self.config.get('temperature', 0.8),
            system=prompt,
            messages=[
                {
                    "role": "user",
                    "content": "Genera un CONTRIBUTING.md completo y profesional basado en el análisis del proyecto proporcionado."
                }
            ]
        )

        return response.content[0].text

    def _build_contributing_prompt(self, analysis: Dict, custom_instructions: Optional[str] = None) -> str:
        """Construye el prompt específico para CONTRIBUTING.md."""
        # Cargar prompt base para CONTRIBUTING.md
        prompt_path = self.base_path / 'docs/config/prompts/system/contributing.yaml'
        base_prompt = ""
        if prompt_path.exists():
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    base_prompt = config.get('prompt', '')
            except Exception as e:
                self.console.print(f"[yellow]⚠ Advertencia: Error cargando prompt de CONTRIBUTING: {str(e)}[/yellow]")

        # Cargar TOC para CONTRIBUTING.md
        toc_path = self.base_path / 'docs/config/toc/base/contributing.yaml'
        toc_config = {}
        if toc_path.exists():
            try:
                with open(toc_path, 'r', encoding='utf-8') as f:
                    toc_config = yaml.safe_load(f)
            except Exception as e:
                self.console.print(f"[yellow]⚠ Advertencia: Error cargando TOC de CONTRIBUTING: {str(e)}[/yellow]")

        # Construir prompt completo
        prompt_parts = [
            base_prompt,
            f"\n\nAnálisis del proyecto:",
            yaml.dump(analysis, default_flow_style=False),
            f"\n\nEstructura requerida:",
            yaml.dump(toc_config, default_flow_style=False)
        ]

        if custom_instructions:
            prompt_parts.append(f"\n\nInstrucciones personalizadas:\n{custom_instructions}")

        return "\n".join(prompt_parts)

    def _get_commit_message_format(self, versioning: Dict) -> str:
        """Obtiene el formato de mensajes de commit."""
        if versioning.get('conventional_commits'):
            return """Utilizamos Conventional Commits:

- `feat:` Nuevas funcionalidades
- `fix:` Correcciones de bugs
- `docs:` Documentación
- `style:` Cambios de estilo
- `refactor:` Refactorización
- `test:` Pruebas
- `chore:` Tareas de mantenimiento"""
        else:
            return """Utilizamos el formato: `[TAG] Descripción`

- `[FEAT]` Nuevas funcionalidades
- `[FIX]` Correcciones de bugs
- `[DOCS]` Documentación
- `[STYLE]` Cambios de estilo
- `[REFACTOR]` Refactorización
- `[TEST]` Pruebas
- `[CHORE]` Tareas de mantenimiento"""

    def _get_versioning_info(self, versioning: Dict) -> str:
        """Obtiene información del sistema de versionado."""
        if versioning.get('semantic_versioning'):
            return """Utilizamos Semantic Versioning (MAJOR.MINOR.PATCH):

- MAJOR: Cambios incompatibles con versiones anteriores
- MINOR: Nuevas funcionalidades compatibles
- PATCH: Correcciones de bugs compatibles"""
        else:
            return """El versionado se maneja automáticamente basado en los commits."""

    def _get_code_style_info(self, technologies: Dict, workflow: Dict) -> str:
        """Obtiene información del estilo de código."""
        info = []

        # Linters detectados
        code_quality_tools = workflow.get('code_quality_tools', [])
        if 'pre_commit' in code_quality_tools:
            info.append("- Pre-commit hooks configurados")
        if 'eslint' in code_quality_tools:
            info.append("- ESLint para JavaScript/TypeScript")
        if 'flake8' in code_quality_tools:
            info.append("- Flake8 para Python")
        if 'shellcheck' in code_quality_tools:
            info.append("- ShellCheck para Bash")

        # Frameworks de formateo
        languages = technologies.get('languages', [])
        if 'python' in languages:
            info.append("- Black para formateo de Python")
        if 'javascript' in languages or 'typescript' in languages:
            info.append("- Prettier para formateo de JavaScript/TypeScript")

        return "\n".join(info) if info else "Sigue las convenciones estándar del lenguaje."

    def _get_testing_info(self, testing: Dict) -> str:
        """Obtiene información de testing."""
        frameworks = testing.get('frameworks', [])
        if frameworks:
            return f"""Utilizamos {', '.join(frameworks)} para las pruebas.

Ejecuta las pruebas con:
{chr(10).join([f"- {framework}" for framework in frameworks])}"""
        else:
            return "Se recomienda incluir pruebas para nuevas funcionalidades."

    def _get_documentation_info(self, documentation: Dict) -> str:
        """Obtiene información de documentación."""
        tools = documentation.get('tools', [])
        if tools:
            return f"""Utilizamos {', '.join(tools)} para la documentación.

Mantén actualizada la documentación cuando hagas cambios."""
        else:
            return "Documenta tus cambios en el código y actualiza la documentación cuando sea necesario."

    def _analyze_codebase(self) -> Dict:
        """Analiza el código base para generar documentación."""
        if not self.analyzer:
            raise RuntimeError("El analizador no está inicializado")

        # Para ContributingAnalyzer, usar analyze_project
        if isinstance(self.analyzer, ContributingAnalyzer):
            return self.analyzer.analyze_project()

        # Para otros analizadores, usar el método _analyze_codebase
        return self.analyzer._analyze_codebase(self.config.get('doc_type'), self.config.get('custom_type'))

    def _build_prompt(self, config: Dict, analysis: Dict, custom_instructions: Optional[str] = None) -> str:
        """Construye el prompt completo para el modelo."""
        prompt_parts = []

        # 1. Instrucciones base
        prompt_parts.append("Eres un experto en documentación técnica. Tu tarea es generar documentación técnica completa y detallada.")

        # 2. Tipo de documento y contexto
        prompt_parts.append(f"\nTipo de documento: {config['doc_type']}")
        if config.get('context'):
            prompt_parts.append(f"Contexto: {config['context']}")

        # 3. Configuración del modelo
        prompt_parts.append("\nConfiguración del modelo:")
        prompt_parts.append(f"- Modelo: {config.get('model', 'claude-3-sonnet-20240229')}")
        prompt_parts.append(f"- Temperatura: {config.get('temperature', 0.7)}")
        prompt_parts.append(f"- Tokens máximos: {config.get('max_tokens', 4000)}")

        # 4. Análisis del código
        prompt_parts.append("\nAnálisis del código:")
        prompt_parts.append(yaml.dump(analysis, default_flow_style=False))

        # 5. Configuración personalizada si existe
        custom_config = {}
        if config.get('custom_type'):
            # Cargar configuración personalizada
            custom_config_path = self.base_path / f'docs/config/prompts/custom/{config["custom_type"]}.yaml'
            if custom_config_path.exists():
                try:
                    with open(custom_config_path, 'r', encoding='utf-8') as f:
                        custom_config = yaml.safe_load(f)
                except Exception as e:
                    self.console.print(f"[yellow]⚠ Advertencia: Error cargando configuración personalizada: {str(e)}[/yellow]")

        # 6. Incluir configuración del TOC si existe
        if config.get('toc'):
            prompt_parts.append("\nEstructura de la tabla de contenidos:")
            prompt_parts.append(yaml.dump(config['toc'], default_flow_style=False))

        # 7. Incluir estilo y secciones requeridas si existen
        if custom_config.get('style'):
            prompt_parts.append("\nConfiguración de formato:")
            prompt_parts.append(yaml.dump(custom_config['style'], default_flow_style=False))

        if custom_config.get('sections'):
            prompt_parts.append("\nSecciones requeridas:")
            sections = [f"- {section['name']}: {', '.join(section['focus'])}"
                       for section in custom_config['sections']
                       if section.get('required', False)]
            prompt_parts.append("\n".join(sections))

        # 8. Instrucciones personalizadas si existen
        if custom_instructions:
            prompt_parts.append(f"\nInstrucciones personalizadas:\n{custom_instructions}")

        return "\n".join(prompt_parts)

    def _generate_project_description_with_ai(self, analysis: Dict, custom_instructions: Optional[str] = None) -> str:
        """Genera PROJECT_DESCRIPTION usando IA."""
        try:
            # Construir prompt específico para PROJECT_DESCRIPTION
            prompt = self._build_project_description_prompt(analysis, custom_instructions)

            # Generar con IA
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config.get('max_tokens', 4000),
                temperature=self.config.get('temperature', 0.7),
                system=prompt,
                messages=[
                    {
                        "role": "user",
                        "content": "Genera el archivo .project/description.md basado en el análisis del proyecto proporcionado."
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            self.console.print(f"[red]Error generando PROJECT_DESCRIPTION con IA: {str(e)}[/red]")
            # Fallback a generación sin IA
            return self._generate_project_description_without_ai(analysis)

    def _generate_project_description_without_ai(self, analysis: Dict) -> str:
        """Genera PROJECT_DESCRIPTION sin usar IA."""
        try:
            # Extraer información del análisis
            project_structure = analysis.get('project_structure', {})
            functionality = analysis.get('functionality', {})
            technologies = analysis.get('technologies', {})
            purpose = analysis.get('purpose', {})
            differentiators = analysis.get('differentiators', {})
            metadata = analysis.get('metadata', {})
            global_analysis = analysis.get('global_analysis', {})

            # Construir contenido básico
            content = []
            content.append("# Descripción del Proyecto")
            content.append("")

            # Descripción del Repositorio
            project_name = project_structure.get('project_name', 'Proyecto')
            project_type = project_structure.get('project_type', 'general_project')
            content.append("## 📖 Descripción del Repositorio")
            content.append(f"Ecosistema de herramientas y utilidades para {project_name.lower()}.")
            content.append("")

            # Propósito
            main_purpose = purpose.get('main_purpose', f'Proporcionar herramientas y utilidades para {project_name.lower()}')
            content.append("## 🎯 Propósito")
            content.append(main_purpose)
            content.append("")

            # Problema que Resuelve
            problems = purpose.get('problems_solved', ['Automatización de tareas repetitivas'])
            content.append("## 🔍 Problema que Resuelve")
            for problem in problems:
                content.append(f"- {problem}")
            content.append("")

            # Solución
            content.append("## 💡 Solución")
            content.append("Conjunto de herramientas y scripts que automatizan y optimizan los flujos de trabajo.")
            content.append("")

            # Público Objetivo
            audience = purpose.get('target_audience', ['Desarrolladores', 'Administradores de sistemas'])
            content.append("## 👥 Público Objetivo")
            for target in audience:
                content.append(f"- {target}")
            content.append("")

            # Diferenciadores
            unique_features = differentiators.get('unique_features', ['Herramientas multiplataforma'])
            content.append("## 🚀 Diferenciadores")
            for feature in unique_features:
                content.append(f"- {feature}")
            content.append("")

            # Estado del Proyecto
            status = metadata.get('status', 'Development')
            content.append("## 📊 Estado del Proyecto")
            content.append(status)
            content.append("")

            # Enlaces Relacionados
            content.append("## 🔗 Enlaces Relacionados")
            content.append("- [Documentación](docs/)")
            content.append("- [Issues](.githooks/)")
            content.append("- [Discusiones](ideas/)")
            content.append("- [Wiki](docs/)")
            content.append("")

            # Tags y Temas
            tags = metadata.get('tags', ['tools', 'automation', 'productivity'])
            content.append("## 🏷️ Tags y Temas")
            content.append(", ".join(tags))
            content.append("")

            return "\n".join(content)

        except Exception as e:
            self.console.print(f"[red]Error generando PROJECT_DESCRIPTION sin IA: {str(e)}[/red]")
            return "# Error generando descripción del proyecto"

    def _build_project_description_prompt(self, analysis: Dict, custom_instructions: Optional[str] = None) -> str:
        """Construye el prompt específico para PROJECT_DESCRIPTION usando solo un resumen compacto."""
        prompt_parts = []

        # Cargar prompt base desde configuración
        prompt_config_path = self.base_path / 'docs/config/prompts/system/project_description.yaml'
        if prompt_config_path.exists():
            try:
                with open(prompt_config_path, 'r', encoding='utf-8') as f:
                    prompt_config = yaml.safe_load(f)
                    base_prompt = prompt_config.get('prompt', '')
                    prompt_parts.append(base_prompt)
            except Exception as e:
                self.console.print(f"[yellow]⚠ Advertencia: Error cargando prompt de PROJECT_DESCRIPTION: {str(e)}[/yellow]")
        else:
            self.console.print("[yellow]⚠ Advertencia: No se encontró docs/config/prompts/system/project_description.yaml[/yellow]")

        # Crear un resumen muy compacto del análisis
        compact_summary = self._create_compact_summary(analysis)
        prompt_parts.append("\nRESUMEN COMPACTO DEL PROYECTO:")
        prompt_parts.append(compact_summary)

        # Agregar instrucciones personalizadas si existen
        if custom_instructions:
            prompt_parts.append(f"\nINSTRUCCIONES PERSONALIZADAS:\n{custom_instructions}")

        return "\n".join(prompt_parts)

    def _enhance_readme_with_ai(self, base_content: str, analysis: Dict, custom_instructions: Optional[str] = None) -> str:
        """Mejora el contenido base del README usando IA con resumen compacto."""
        try:
            # Debug: mostrar qué modelo se está usando
            self.console.print(f"[blue]🔧 Usando modelo: {self.model}[/blue]")
            self.console.print(f"[blue]🔧 Max tokens: {self.config.get('max_tokens', 4000)}[/blue]")
            self.console.print(f"[blue]🔧 Temperature: {self.config.get('temperature', 0.7)}[/blue]")

            # Crear resumen compacto del análisis
            compact_analysis = self._create_compact_analysis_summary(analysis)

            # Construir prompt para mejora
            prompt = self._build_readme_enhancement_prompt(base_content, compact_analysis, custom_instructions)

            # Generar mejora con IA usando streaming
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.config.get('max_tokens', 4000),
                temperature=self.config.get('temperature', 0.7),
                system=prompt,
                messages=[
                    {
                        "role": "user",
                        "content": "Mejora el contenido del archivo README.md basado en el análisis del proyecto."
                    }
                ]
            ) as stream:
                enhanced_content = ""
                for chunk in stream:
                    if chunk.type == "content_block_delta":
                        enhanced_content += chunk.delta.text

                return enhanced_content

        except Exception as e:
            self.console.print(f"[red]Error mejorando README con IA: {str(e)}[/red]")
            # Fallback al contenido base
            return base_content

    def _build_readme_enhancement_prompt(self, base_content: str, compact_analysis: str, custom_instructions: Optional[str] = None) -> str:
        """Construye el prompt para mejorar el README base."""
        prompt_parts = []

        # Cargar prompt base desde configuración
        prompt_config_path = self.base_path / 'docs/config/prompts/system/project_description.yaml'
        if prompt_config_path.exists():
            try:
                with open(prompt_config_path, 'r', encoding='utf-8') as f:
                    prompt_config = yaml.safe_load(f)
                    base_prompt = prompt_config.get('prompt', '')
                    prompt_parts.append(base_prompt)
            except Exception as e:
                self.console.print(f"[yellow]⚠ Advertencia: Error cargando prompt de README: {str(e)}[/yellow]")

        # Agregar instrucciones específicas para mejora de README
        enhancement_instructions = """
INSTRUCCIONES PARA MEJORA DE README:
- Mejora el contenido existente sin cambiar la estructura básica
- Añade detalles específicos basados en el análisis del proyecto
- Mejora las descripciones para que sean más informativas y atractivas
- Mantén el formato markdown y la estructura de secciones
- Asegúrate de que el contenido sea preciso y útil para desarrolladores
- Optimiza los ejemplos de código para que sean más realistas
- Mejora las instrucciones de instalación y configuración
- Añade información específica del proyecto donde sea relevante
"""
        prompt_parts.append(enhancement_instructions)

        # Agregar contenido base actual
        prompt_parts.append("CONTENIDO ACTUAL DEL README:")
        prompt_parts.append(base_content)

        # Agregar resumen compacto del análisis
        prompt_parts.append("\nRESUMEN DEL ANÁLISIS DEL PROYECTO:")
        prompt_parts.append(compact_analysis)

        # Agregar instrucciones personalizadas si existen
        if custom_instructions:
            prompt_parts.append(f"\nINSTRUCCIONES PERSONALIZADAS:\n{custom_instructions}")

        return "\n".join(prompt_parts)

    def _generate_readme_without_ai(self, analysis: Dict) -> str:
        """Genera README.md completo con mejores prácticas sin IA."""
        try:
            content = []

            # Verificar si existe .project/description.md
            project_description_path = self.base_path / ".project" / "description.md"
            has_project_description = project_description_path.exists()

            # Extraer información del análisis
            project_name = analysis.get('project_name', 'Proyecto')
            project_type = analysis.get('project_type', 'unknown')
            technologies = analysis.get('technologies', {})
            structure = analysis.get('structure', {})
            purpose = analysis.get('purpose', {})
            metadata = analysis.get('metadata', {})
            differentiators = analysis.get('differentiators', {})
            global_analysis = analysis.get('global_analysis', {})

            # Si existe .project/description.md, obtener las secciones excluidas
            excluded_sections = set()
            if has_project_description:
                try:
                    with open(project_description_path, 'r', encoding='utf-8') as f:
                        project_description_content = f.read()

                    # Extraer secciones del archivo de descripción para ver cuáles están excluidas
                    project_sections = self._extract_project_sections(project_description_content)
                    for section_name, section_info in project_sections.items():
                        if section_name != '__title__':
                            attributes = section_info.get('attributes', {})
                            if attributes.get('exclude', 'false').lower() == 'true':
                                # Normalizar el nombre de la sección para comparación
                                normalized_name = self._normalize_section_name(section_name)
                                excluded_sections.add(normalized_name)
                                self.console.print(f"[blue]DEBUG: Sección excluida detectada: '{section_name}' -> '{normalized_name}'[/blue]")

                    self.console.print(f"[blue]DEBUG: Secciones excluidas: {excluded_sections}[/blue]")
                except Exception as e:
                    self.console.print(f"[yellow]Advertencia: Error leyendo secciones excluidas: {e}[/yellow]")

            # Si existe .project/description.md, generar un README base más simple
            if has_project_description:
                # NO generar título aquí - el título vendrá del archivo de descripción
                # NO generar badges aquí - los badges vendrán del archivo de descripción si existen
                # Solo generar secciones básicas que no estén en el archivo de descripción

                # Sección de descripción básica (será reemplazada si existe en .project/description.md)
                main_purpose = purpose.get('main_purpose', f'Ecosistema de herramientas y utilidades para {project_name.lower()}')
                content.append("## 📖 Descripción")
                content.append(main_purpose)
                content.append("")

                # Sección de características básica (solo si no está excluida)
                if 'características' not in excluded_sections:
                    content.append("## ✨ Características")
                    features = differentiators.get('unique_features', [])
                    if features:
                        for feature in features[:5]:  # Máximo 5 características
                            content.append(f"- {feature}")
                    else:
                        content.append("- Herramientas multiplataforma")
                        content.append("- Automatización de tareas")
                        content.append("- Configuración flexible")
                    content.append("")
                else:
                    pass

                # Sección de instalación básica (solo si no está excluida)
                if 'instalacion' not in excluded_sections and 'instalación' not in excluded_sections:
                    content.append("## 🚀 Instalación")
                    content.append("")
                    content.append("```bash")
                    languages = technologies.get('languages', [])
                    if 'Python' in languages:
                        content.append("pip install -r requirements.txt")
                    content.append("```")
                    content.append("")
                else:
                    pass

                # Sección de uso básica (solo si no está excluida)
                if 'uso rapido' not in excluded_sections and 'uso rápido' not in excluded_sections:
                    content.append("## 🎯 Uso Rápido")
                    content.append("")
                    content.append("```bash")
                    main_files = global_analysis.get('main_functions', [])
                    if main_files:
                        main_file = main_files[0].split('/')[-1]
                        content.append(f"# Ejemplo básico de uso")
                        content.append(f"python {main_file} --help")
                    else:
                        content.append("# Ejemplo básico de uso")
                        content.append("python main.py --help")
                    content.append("```")
                    content.append("")
                else:
                    pass

                # Sección de documentación básica
                content.append("## 📚 Documentación")
                content.append("")
                doc_files = global_analysis.get('file_categories', {}).get('documentation', [])
                if doc_files:
                    for doc_file in doc_files[:5]:
                        if doc_file.endswith('.md'):
                            name = doc_file.replace('.md', '').replace('_', ' ').title()
                            content.append(f"- [{name}]({doc_file})")
                content.append("- [Contributing](CONTRIBUTING.md)")
                content.append("- [Changelog](CHANGELOG.md)")
                content.append("")

                # Sección de estructura básica
                content.append("## 📁 Estructura del Proyecto")
                content.append("")
                real_directories = self._get_real_project_structure()
                if real_directories:
                    for directory in real_directories[:10]:  # Máximo 10 directorios
                        content.append(f"`{directory}/`")
                else:
                    content.append("`src/` - Código fuente")
                    content.append("`docs/` - Documentación")
                    content.append("`tests/` - Tests")
                content.append("")

                # Sección de contribución básica
                content.append("## 🤝 Contribución")
                content.append("")
                content.append("Las contribuciones son bienvenidas. Por favor, lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles.")
                content.append("")

                # Sección de licencia básica (solo si no está excluida)
                if 'licencia' not in excluded_sections:
                    content.append("## 📄 Licencia")
                    content.append("")
                    content.append("Este proyecto está bajo la Licencia GPLv3. Ver [LICENSE.md](LICENSE.md) para más detalles.")
                    content.append("")

            else:
                # Generar README completo como antes (código original)
                # 1. TÍTULO Y BADGES
                content.append(f"# {project_name}")
                content.append("")

                # Badges basados en tecnologías detectadas
                languages = technologies.get('languages', [])
                if 'Python' in languages:
                    content.append("![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)")
                if 'Bash' in languages:
                    content.append("![Bash](https://img.shields.io/badge/Bash-5.0+-green.svg)")
                if 'Go' in languages:
                    content.append("![Go](https://img.shields.io/badge/Go-1.19+-00ADD8.svg)")
                if 'Rust' in languages:
                    content.append("![Rust](https://img.shields.io/badge/Rust-1.65+-orange.svg)")

                content.append("![License](https://img.shields.io/badge/License-GPLv3-green.svg)")
                content.append("![Status](https://img.shields.io/badge/Status-Development-orange.svg)")
                content.append("")

                # 2. DESCRIPCIÓN BREVE
                main_purpose = purpose.get('main_purpose', f'Ecosistema de herramientas y utilidades para {project_name.lower()}')
                content.append("## 📖 Descripción")
                content.append(main_purpose)
                content.append("")

                # 3. CARACTERÍSTICAS PRINCIPALES
                content.append("## ✨ Características")
                features = differentiators.get('unique_features', [])
                if features:
                    for feature in features:
                        content.append(f"- {feature}")
                else:
                    content.append("- Herramientas multiplataforma")
                    content.append("- Automatización de tareas")
                    content.append("- Configuración flexible")
                    content.append("- Integración con sistemas existentes")
                content.append("")

                # 4. INSTALACIÓN
                content.append("## 🚀 Instalación")
                content.append("")
                content.append("```bash")
                languages = technologies.get('languages', [])
                if 'Python' in languages:
                    content.append("pip install -r requirements.txt")
                content.append("```")
                content.append("")

                # 5. USO RÁPIDO (más realista)
                content.append("## 🎯 Uso Rápido")
                content.append("")
                content.append("```bash")

                # Basado en archivos principales detectados
                main_files = global_analysis.get('main_functions', [])
                if main_files:
                    # Usar el primer archivo principal encontrado
                    main_file = main_files[0].split('/')[-1]  # Solo el nombre del archivo
                    content.append(f"# Ejemplo básico de uso")
                    content.append(f"python {main_file} --help")
                else:
                    content.append("# Ejemplo básico de uso")
                    content.append("python main.py --help")

                content.append("```")
                content.append("")

                # 6. DOCUMENTACIÓN
                content.append("## 📚 Documentación")
                content.append("")

                # Basado en archivos de documentación detectados
                doc_files = global_analysis.get('file_categories', {}).get('documentation', [])
                if doc_files:
                    for doc_file in doc_files[:5]:  # Máximo 5 archivos
                        if doc_file.endswith('.md'):
                            name = doc_file.replace('.md', '').replace('_', ' ').title()
                            content.append(f"- [{name}]({doc_file})")

                # Enlaces estándar
                content.append("- [Contributing](CONTRIBUTING.md)")
                content.append("- [Changelog](CHANGELOG.md)")
                content.append("")

                # 7. ESTRUCTURA DEL PROYECTO
                content.append("## 📁 Estructura del Proyecto")
                content.append("")

                # Usar estructura real del proyecto
                real_directories = self._get_real_project_structure()
                if real_directories:
                    for directory in real_directories[:15]:  # Máximo 15 directorios
                        content.append(f"`{directory}/`")
                else:
                    content.append("`src/` - Código fuente")
                    content.append("`docs/` - Documentación")
                    content.append("`tests/` - Tests")
                    content.append("`config/` - Configuraciones")
                content.append("")

                # 8. CONTRIBUCIÓN
                content.append("## 🤝 Contribución")
                content.append("")
                content.append("Las contribuciones son bienvenidas. Por favor, lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre nuestro código de conducta y el proceso para enviar pull requests.")
                content.append("")

                # 9. LICENCIA
                content.append("## 📄 Licencia")
                content.append("")
                content.append("Este proyecto está bajo la Licencia GPLv3. Ver [LICENSE.md](LICENSE.md) para más detalles.")
                content.append("")

            return "\n".join(content)

        except Exception as e:
            self.console.print(f"[red]Error generando README base: {str(e)}[/red]")
            raise

    def _create_compact_analysis_summary(self, analysis: Dict) -> str:
        """Crea un resumen muy compacto del análisis para evitar problemas de tokens."""
        summary_parts = []

        # Información básica del proyecto
        project_name = analysis.get('project_name', 'Unknown')
        project_type = analysis.get('project_type', 'unknown')
        summary_parts.append(f"PROYECTO: {project_name} (Tipo: {project_type})")

        # Tecnologías principales (solo las más importantes)
        technologies = analysis.get('technologies', {})
        languages = technologies.get('languages', [])
        if languages:
            summary_parts.append(f"TECNOLOGÍAS: {', '.join(languages[:5])}")  # Máximo 5 lenguajes

        # Estructura del proyecto (solo directorios principales)
        structure = analysis.get('structure', {})
        main_dirs = structure.get('main_directories', [])
        if main_dirs:
            summary_parts.append(f"DIRECTORIOS: {', '.join(main_dirs[:5])}")  # Máximo 5 directorios

        # Propósito del proyecto
        purpose = analysis.get('purpose', {})
        main_purpose = purpose.get('main_purpose', 'Herramientas y utilidades')
        summary_parts.append(f"PROPÓSITO: {main_purpose}")

        # Problemas que resuelve (solo los principales)
        problems = purpose.get('problems_solved', [])
        if problems:
            summary_parts.append(f"PROBLEMAS: {', '.join(problems[:3])}")  # Máximo 3 problemas

        # Público objetivo
        audience = purpose.get('target_audience', [])
        if audience:
            summary_parts.append(f"PÚBLICO: {', '.join(audience[:3])}")  # Máximo 3 tipos

        # Estado del proyecto
        metadata = analysis.get('metadata', {})
        status = metadata.get('status', 'Development')
        summary_parts.append(f"ESTADO: {status}")

        return "\n".join(summary_parts)

    def _generate_readme_hybrid(self, output_file: str, custom_instructions: Optional[str] = None, use_ai: bool = False) -> None:
        """Genera README.md usando enfoque híbrido con mejores prácticas."""
        try:
            # 1. Analizar el proyecto
            self.console.print("Analizando proyecto para README.md...")
            analysis = self.analyzer.analyze_project()

            # 2. Generar contenido base sin IA
            self.console.print("Generando contenido base de README.md...")
            base_content = self._generate_readme_without_ai(analysis)

            # 3. Validar y usar .project/description.md si existe
            project_description_path = self.base_path / ".project" / "description.md"
            if project_description_path.exists():
                self.console.print("Encontrado .project/description.md, fusionando secciones...")
                final_content = self._merge_with_project_description(base_content, str(project_description_path))
            else:
                self.console.print("No se encontró .project/description.md, usando contenido base")
                final_content = base_content

            # 4. Si se solicita IA, mejorar el contenido
            if use_ai:
                self.console.print("Mejorando contenido con IA...")
                enhanced_content = self._enhance_readme_with_ai(final_content, analysis, custom_instructions)
                final_content = enhanced_content

            # 5. Guardar el archivo
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            self.console.print(f"✓ README.md generado y guardado en: {output_file}")

        except Exception as e:
            self.console.print(f"[red]Error generando README.md: {str(e)}[/red]")
            raise

    def _merge_with_project_description(self, base_content: str, project_description_path: str) -> str:
        """Fusiona el contenido base con el archivo de descripción del proyecto."""
        try:
            # Leer el archivo de descripción del proyecto
            with open(project_description_path, 'r', encoding='utf-8') as f:
                project_description_content = f.read()

            # Extraer título del archivo de descripción del proyecto
            project_title = self._extract_title_from_project_description(project_description_content)

            # Extraer secciones del archivo de descripción del proyecto
            project_sections = self._extract_project_sections(project_description_content)

            # Extraer secciones del README generado
            readme_sections = self._extract_readme_sections(base_content)

            # Fusionar secciones
            merged_content = self._merge_sections(readme_sections, project_sections, project_title)

            self.console.print(f"  ✓ Contenido fusionado con {project_description_path}")
            return merged_content

        except Exception as e:
            self.console.print(f"  ⚠️ Error fusionando con {project_description_path}: {e}")
            return base_content

    def _extract_title_from_project_description(self, content: str) -> Optional[str]:
        """Extrae el título del archivo de descripción del proyecto."""
        sections = self._extract_markdown_sections(content)

        if '__title__' in sections:
            title_content = sections['__title__']['content']
            # Extraer solo el texto del título (sin #) y cualquier contenido adicional
            lines = title_content.split('\n')
            title_line = None
            additional_content = []

            for line in lines:
                if line.strip().startswith('#'):
                    title_line = line.strip().lstrip('#').strip()
                else:
                    additional_content.append(line)

            # Si hay contenido adicional (como badges), incluirlo
            if additional_content:
                return f"{title_line}\n\n{''.join(additional_content)}"
            else:
                return title_line

        return None

    def _extract_markdown_sections(self, content: str) -> Dict[str, Dict]:
        """Extrae TODAS las secciones ## ... como bloques markdown literales, respetando subsecciones y formato."""
        import re
        sections = {}
        lines = content.split('\n')
        title_content = []
        in_title = True
        section_starts = []
        # Encontrar los índices de todos los encabezados ## (pero no ###)
        for idx, line in enumerate(lines):
            if line.strip().startswith('##') and not line.strip().startswith('###'):
                section_starts.append(idx)
        # Agregar el final del archivo como último límite
        section_starts.append(len(lines))
        # Extraer el título (antes del primer ##)
        if section_starts and section_starts[0] > 0:
            title_content = lines[:section_starts[0]]
        # Extraer cada sección como bloque literal
        for i in range(len(section_starts)-1):
            start = section_starts[i]
            end = section_starts[i+1]
            header_line = lines[start]
            # Extraer nombre y atributos
            section_info = self._parse_section_header(header_line)
            section_name = section_info['name']
            section_block = '\n'.join(lines[start+1:end]).strip()

            # Procesar el bloque para detectar prompts GENERATE
            has_generate = False
            generate_prompt = None
            processed_content = []

            for line in section_block.split('\n'):
                if '<!-- GENERATE:' in line:
                    has_generate = True
                    generate_prompt = line.split('<!-- GENERATE:')[1].split('-->')[0].strip()
                    # No incluir la línea del prompt en el contenido final
                else:
                    processed_content.append(line)

            # Unir el contenido procesado
            final_content = '\n'.join(processed_content).strip()

            sections[section_name] = {
                'content': final_content,
                'attributes': section_info.get('attributes', {}),
                'has_generate': has_generate,
                'generate_prompt': generate_prompt
            }
        # Agregar el título como una sección especial
        if title_content:
            sections['__title__'] = {
                'content': '\n'.join(title_content).strip(),
                'attributes': {},
                'has_generate': False,
                'generate_prompt': None
            }
        return sections

    def _parse_section_header(self, line: str) -> Dict:
        """Parsea el encabezado de una sección y extrae atributos."""
        line = line.strip()

        # Extraer el nombre de la sección (sin ##)
        section_name = line.lstrip('#').strip()

        # Buscar atributos en formato {atributo: valor}
        attributes = {}
        import re

        # Buscar patrones como {position: after descripción} o {exclude: true}
        attr_pattern = r'\{([^}]+)\}'
        matches = re.findall(attr_pattern, section_name)

        for match in matches:
            # Limpiar el nombre de la sección removiendo los atributos
            section_name = re.sub(attr_pattern, '', section_name).strip()

            # Parsear atributos
            for attr in match.split(','):
                attr = attr.strip()
                if ':' in attr:
                    key, value = attr.split(':', 1)
                    attributes[key.strip()] = value.strip()

        return {
            'name': section_name,
            'attributes': attributes,
            'has_generate': False,
            'generate_prompt': None
        }

    def _merge_sections(self, readme_sections: Dict[str, str], project_sections: Dict[str, Dict], project_title: Optional[str] = None) -> str:
        """Fusiona secciones del README con las del archivo de descripción del proyecto."""
        merged_content = []

        # Solo agregar el título si existe en el archivo de descripción del proyecto
        if project_title:
            # Verificar si el título tiene contenido adicional (como badges)
            title_lines = project_title.split('\n')
            if len(title_lines) > 1:
                # El primer elemento es el título, el resto es contenido adicional
                main_title = title_lines[0]
                additional_content = '\n'.join(title_lines[1:])

                merged_content.append(f"# {main_title}")
                merged_content.append("")  # Línea en blanco después del título

                # Agregar contenido adicional (como badges)
                if additional_content.strip():
                    merged_content.append(additional_content)
                    merged_content.append("")  # Línea en blanco después del contenido adicional
            else:
                # Solo título, sin contenido adicional
                merged_content.append(f"# {project_title}")
                merged_content.append("")  # Línea en blanco después del título

        # Crear un mapeo de secciones del README para facilitar la búsqueda
        readme_section_map = {}
        for section_name, content in readme_sections.items():
            normalized_name = self._normalize_section_name(section_name)
            readme_section_map[normalized_name] = {
                'original_name': section_name,
                'content': content
            }

        # Procesar secciones del proyecto con sus atributos
        positioned_sections = []  # Secciones con posicionamiento específico
        regular_sections = []     # Secciones sin posicionamiento
        processed_sections = set()

        for section_name, section_info in project_sections.items():
            if section_name == '__title__':
                continue  # El título ya se procesó arriba

            attributes = section_info.get('attributes', {})
            content = section_info.get('content', '')
            has_generate = section_info.get('has_generate', False)
            generate_prompt = section_info.get('generate_prompt', None)

            # Verificar si la sección debe excluirse
            if attributes.get('exclude', 'false').lower() == 'true':
                continue

            # Verificar si tiene posicionamiento específico
            position_after = attributes.get('position', '').replace('after ', '').strip()
            if position_after:
                positioned_sections.append({
                    'name': section_name,
                    'content': content,
                    'has_generate': has_generate,
                    'generate_prompt': generate_prompt,
                    'position_after': position_after
                })
            else:
                regular_sections.append({
                    'name': section_name,
                    'content': content,
                    'has_generate': has_generate,
                    'generate_prompt': generate_prompt
                })

        # Crear una lista ordenada de todas las secciones
        all_sections = []

        # Agregar secciones regulares del proyecto (sin posicionamiento) primero
        for section in regular_sections:
            all_sections.append({
                'name': section['name'],
                'content': section['content'],
                'source': 'project',
                'has_generate': section['has_generate'],
                'generate_prompt': section['generate_prompt'],
                'processed': False
            })
            processed_sections.add(self._normalize_section_name(section['name']))

        # Procesar secciones con posicionamiento específico
        for positioned_section in positioned_sections:
            target_section = positioned_section['position_after']
            target_normalized = self._normalize_section_name(target_section)

            # Buscar la sección objetivo en la lista
            insert_index = -1
            for i, section in enumerate(all_sections):
                if self._normalize_section_name(section['name']) == target_normalized:
                    insert_index = i + 1
                    break

            # Si no se encuentra la sección objetivo, agregar al final
            if insert_index == -1:
                insert_index = len(all_sections)

            # Insertar la sección posicionada
            all_sections.insert(insert_index, {
                'name': positioned_section['name'],
                'content': positioned_section['content'],
                'source': 'project',
                'has_generate': positioned_section['has_generate'],
                'generate_prompt': positioned_section['generate_prompt'],
                'processed': False
            })
            processed_sections.add(self._normalize_section_name(positioned_section['name']))

        # Agregar secciones del README que no fueron procesadas por el proyecto
        for section_name, content in readme_sections.items():
            normalized_name = self._normalize_section_name(section_name)
            if normalized_name not in processed_sections:
                all_sections.append({
                    'name': section_name,
                    'content': content,
                    'source': 'readme',
                    'processed': False
                })

        # Generar el contenido final respetando el orden
        for section in all_sections:
            section_name = section['name']
            content = section['content']
            source = section['source']
            has_generate = section.get('has_generate', False)
            generate_prompt = section.get('generate_prompt', None)

            # Si es una sección del proyecto con generación de IA
            if source == 'project' and has_generate and generate_prompt:
                generated_content = self._generate_section_content(generate_prompt, section_name)
                if generated_content:
                    content = generated_content

            # Si es una sección del proyecto sin contenido, generar contenido automático para ciertas secciones
            if source == 'project' and not content.strip():
                auto_content = self._generate_auto_content(section_name)
                if auto_content:
                    content = auto_content

            # Agregar la sección al contenido final
            merged_content.append(f"## {section_name}")
            merged_content.append("")
            merged_content.append(content)
            merged_content.append("")

        return '\n'.join(merged_content)

    def _generate_section_content(self, prompt: str, section_name: str) -> Optional[str]:
        """Genera contenido para una sección usando IA."""
        try:
            # Construir el prompt completo
            full_prompt = f"""Genera contenido para la sección '{section_name}' del README.

Prompt específico: {prompt}

Genera solo el contenido de la sección, sin incluir el encabezado. El contenido debe ser:
- Relevante para el proyecto
- Bien estructurado en Markdown
- Conciso pero informativo
- Sin incluir el título de la sección

Contenido:"""

            # Usar el modelo de IA configurado
            response = self._call_ai_model(full_prompt, max_tokens=1000)
            return response.strip() if response else None

        except Exception as e:
            print(f"Error generando contenido para sección '{section_name}': {e}")
            return None

    def _get_real_project_structure(self) -> List[str]:
        """Obtiene la estructura real del proyecto escaneando el filesystem hasta 4 niveles con formato gráfico."""
        structure_lines = []

        # Directorios a ignorar (estándar para cualquier proyecto)
        ignore_dirs = {
            '.git', '.gitignore', '.gitattributes', '.github',
            '__pycache__', '.pytest_cache', '.coverage',
            'node_modules', '.venv', 'venv', 'env',
            '.vscode', '.idea', '.DS_Store', 'Thumbs.db',
            '.mypy_cache', '.ruff_cache', '.tox'
            # Removido '.cursor' para que se incluya si existe
        }

        # Extensiones de archivos importantes (detectadas dinámicamente)
        important_extensions = {'.py', '.js', '.ts', '.json', '.yml', '.yaml', '.md', '.sh', '.txt', '.toml', '.ini', '.cfg'}

        # Leer .gitignore y agregar patrones a ignorar
        gitignore_patterns = self._read_gitignore_patterns()

        # Directorios que siempre se deben mostrar (excepciones al .gitignore)
        always_show = {'.githooks', '.project', '.cursor'}

        try:
            # Agregar el repositorio raíz
            repo_name = self.base_path.name
            structure_lines.append(f"🌳 {repo_name}/")

            # Escanear directorios y archivos de primer nivel
            items = sorted(self.base_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

            # Separar directorios y archivos para mejor organización
            dirs = [item for item in items if item.is_dir() and not item.name.startswith('.') and item.name not in ignore_dirs]
            files = [item for item in items if item.is_file() and (item.suffix in important_extensions or self._is_important_file(item.name))]

            # Incluir directorios .cursor y .project si existen
            cursor_dir = self.base_path / '.cursor'
            project_dir = self.base_path / '.project'

            if cursor_dir.exists() and cursor_dir.is_dir():
                dirs.append(cursor_dir)
            if project_dir.exists() and project_dir.is_dir():
                dirs.append(project_dir)

            # Filtrar directorios según .gitignore
            dirs = [item for item in dirs if not self._should_ignore_path(item, gitignore_patterns) or item.name in always_show]

            # Procesar directorios primero
            for i, item in enumerate(dirs):
                is_last_dir = i == len(dirs) - 1 and len(files) == 0
                is_last = i == len(dirs) - 1

                # Icono dinámico basado en el nombre del directorio
                icon = self._get_directory_icon(item.name)

                connector = "└── " if is_last_dir else "├── "
                structure_lines.append(f"   {connector}{icon} {item.name}/")

                # Escanear subdirectorios de segundo nivel
                try:
                    subitems = sorted(item.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                    subitems = [x for x in subitems if not x.name.startswith('.') and x.name not in ignore_dirs]

                    # Filtrar subdirectorios según .gitignore
                    subitems = [x for x in subitems if not self._should_ignore_path(x, gitignore_patterns)]

                    for j, subitem in enumerate(subitems):
                        sub_is_last = j == len(subitems) - 1

                        if subitem.is_dir():
                            sub_icon = self._get_directory_icon(subitem.name)
                            sub_connector = "    └── " if sub_is_last else "    ├── "
                            structure_lines.append(f"   {sub_connector}{sub_icon} {subitem.name}/")

                            # Escanear subdirectorios de tercer nivel
                            try:
                                subsubitems = sorted(subitem.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                                subsubitems = [x for x in subsubitems if not x.name.startswith('.') and x.name not in ignore_dirs]

                                # Filtrar subsubdirectorios según .gitignore
                                subsubitems = [x for x in subsubitems if not self._should_ignore_path(x, gitignore_patterns)]

                                for k, subsubitem in enumerate(subsubitems):
                                    subsub_is_last = k == len(subsubitems) - 1

                                    if subsubitem.is_dir():
                                        subsub_icon = "📁"
                                        subsub_connector = "        └── " if subsub_is_last else "        ├── "
                                        structure_lines.append(f"   {subsub_connector}{subsub_icon} {subsubitem.name}/")

                                        # Escanear archivos importantes en cuarto nivel
                                        try:
                                            files = [x for x in subsubitem.iterdir() if x.is_file() and (x.suffix in important_extensions or self._is_important_file(x.name))]
                                            # Filtrar archivos según .gitignore
                                            files = [x for x in files if not self._should_ignore_path(x, gitignore_patterns)]
                                            for l, file in enumerate(files):
                                                file_is_last = l == len(files) - 1
                                                file_icon = self._get_file_icon(file.name)
                                                file_connector = "            └── " if file_is_last else "            ├── "
                                                structure_lines.append(f"   {file_connector}{file_icon} {file.name}")
                                        except PermissionError:
                                            pass
                                        except Exception:
                                            pass
                                    else:
                                        # Archivo en tercer nivel
                                        if subsubitem.suffix in important_extensions or self._is_important_file(subsubitem.name):
                                            file_icon = self._get_file_icon(subsubitem.name)
                                            subsub_connector = "        └── " if subsub_is_last else "        ├── "
                                            structure_lines.append(f"   {subsub_connector}{file_icon} {subsubitem.name}")

                            except PermissionError:
                                pass
                            except Exception:
                                pass
                        else:
                            # Archivo en segundo nivel
                            if subitem.suffix in important_extensions or self._is_important_file(subitem.name):
                                file_icon = self._get_file_icon(subitem.name)
                                sub_connector = "    └── " if sub_is_last else "    ├── "
                                structure_lines.append(f"   {sub_connector}{file_icon} {subitem.name}")

                except PermissionError:
                    pass
                except Exception:
                    pass

            # Procesar archivos importantes en primer nivel
            for i, item in enumerate(files):
                is_last = i == len(files) - 1

                file_icon = self._get_file_icon(item.name)
                connector = "   └── " if is_last else "   ├── "
                structure_lines.append(f"{connector}{file_icon} {item.name}")

            # Limitar el número total de líneas para evitar READMEs muy largos
            return structure_lines[:100]  # Aumentado a 100 líneas para mostrar más estructura

        except Exception as e:
            self.console.print(f"[yellow]Advertencia: Error al escanear estructura del proyecto: {str(e)}[/yellow]")
            return []

    def _read_gitignore_patterns(self) -> List[str]:
        """Lee los patrones del archivo .gitignore."""
        patterns = []
        gitignore_path = self.base_path / '.gitignore'

        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Ignorar líneas vacías y comentarios
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                self.console.print(f"[yellow]Advertencia: Error leyendo .gitignore: {str(e)}[/yellow]")

        return patterns

    def _should_ignore_path(self, path: Path, gitignore_patterns: List[str]) -> bool:
        """Determina si un path debe ser ignorado según los patrones de .gitignore."""
        if not gitignore_patterns:
            return False

        # Convertir el path a string relativo para comparar con patrones
        try:
            relative_path = str(path.relative_to(self.base_path))
        except ValueError:
            # Si no es relativo, usar el nombre del archivo/directorio
            relative_path = path.name

        # Normalizar separadores de path
        relative_path = relative_path.replace('\\', '/')

        for pattern in gitignore_patterns:
            # Normalizar el patrón
            pattern = pattern.replace('\\', '/')

            # Patrones que coinciden con archivos/directorios específicos
            if pattern == relative_path or pattern == path.name:
                return True

            # Patrones con wildcards
            if '*' in pattern:
                if self._matches_pattern(relative_path, pattern):
                    return True

            # Patrones de directorios (terminan en /)
            if pattern.endswith('/'):
                if relative_path.startswith(pattern) or path.is_dir() and path.name == pattern[:-1]:
                    return True

            # Patrones de archivos específicos
            if pattern.startswith('/'):
                # Patrón absoluto desde la raíz del proyecto
                if relative_path == pattern[1:]:
                    return True
            else:
                # Patrón relativo
                if relative_path == pattern or relative_path.endswith('/' + pattern):
                    return True

        return False

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Verifica si un path coincide con un patrón con wildcards."""
        import fnmatch

        # Convertir patrón de .gitignore a patrón de fnmatch
        fnmatch_pattern = pattern.replace('*', '*')

        # Si el patrón termina en /, es un directorio
        if pattern.endswith('/'):
            fnmatch_pattern = fnmatch_pattern[:-1] + '*'

        return fnmatch.fnmatch(path, fnmatch_pattern) or fnmatch.fnmatch(path.split('/')[-1], fnmatch_pattern)

    def _is_important_file(self, filename: str) -> bool:
        """Determina si un archivo es importante basándose en su nombre."""
        important_names = {
            'readme', 'license', 'changelog', 'contributing', 'contributors',
            'requirements', 'package', 'setup', 'makefile', 'dockerfile',
            'docker-compose', '.env.example', 'pyproject', 'cargo', 'composer',
            'gemfile', 'pom.xml', 'build.gradle', 'package.json', 'tsconfig',
            'webpack', 'rollup', 'vite', 'jest', 'eslint', 'prettier',
            'gitignore', 'gitattributes', 'editorconfig', 'travis', 'circle',
            'github', 'gitlab', 'bitbucket', 'azure', 'jenkins', 'sonar'
        }

        name_lower = filename.lower()
        return any(important_name in name_lower for important_name in important_names)

    def _get_directory_icon(self, dirname: str) -> str:
        """Obtiene el icono apropiado para un directorio basándose en su nombre."""
        name_lower = dirname.lower()

        # Mapeo dinámico de iconos basado en patrones de nombres
        icon_mapping = {
            'docs': '📚', 'documentation': '📚', 'doc': '📚',
            'src': '💻', 'source': '💻', 'app': '💻', 'lib': '💻', 'libs': '💻',
            'tests': '🧪', 'test': '🧪', 'spec': '🧪', 'testing': '🧪',
            'config': '⚙️', 'conf': '⚙️', 'settings': '⚙️', 'cfg': '⚙️',
            'scripts': '🔧', 'tools': '🔧', 'bin': '🔧', 'utils': '🔧',
            'assets': '🎨', 'static': '🎨', 'public': '🎨', 'resources': '🎨',
            'data': '🗄️', 'db': '🗄️', 'database': '🗄️', 'storage': '🗄️',
            'deploy': '🚀', 'deployment': '🚀', 'dist': '🚀', 'build': '🚀',
            'ci': '🔄', 'cd': '🔄', 'pipeline': '🔄', 'workflows': '🔄',
            'vendor': '📦', 'third_party': '📦', 'deps': '📦', 'dependencies': '📦',
            'scaffold': '🏗️', 'templates': '🏗️', 'boilerplate': '🏗️',
            'ideas': '💡', 'brainstorming': '💡', 'concepts': '💡',
            'logs': '📋', 'tmp': '📋', 'temp': '📋', 'cache': '📋',
            'api': '🔌', 'endpoints': '🔌', 'routes': '🔌',
            'models': '🏗️', 'entities': '🏗️', 'schemas': '🏗️',
            'middleware': '🔗', 'interceptors': '🔗', 'filters': '🔗',
            'migrations': '🗃️', 'schema': '🗃️', 'seeds': '🗃️',
            'analysis': '📊', 'prompts': '📊', 'toc': '📊',
            'rules': '⚙️', 'licenses': '📜', 'license': '📜',
            'bitbucket-pipelines': '🔄', 'ci-projects': '🔄',
            'commit-format': '🔧', 'cursor': '🔧'
        }

        # Buscar coincidencias exactas primero
        for pattern, icon in icon_mapping.items():
            if pattern in name_lower:
                return icon

        # Si no hay coincidencias, usar icono genérico
        return "📁"

    def _get_file_icon(self, filename: str) -> str:
        """Obtiene el icono apropiado para un archivo basándose en su extensión y nombre."""
        name_lower = filename.lower()

        # Mapeo por extensión
        extension_mapping = {
            '.py': '🐍', '.js': '🟨', '.ts': '🔷', '.jsx': '🟨', '.tsx': '🔷',
            '.json': '📋', '.yml': '⚙️', '.yaml': '⚙️', '.md': '📝',
            '.sh': '🐚', '.bash': '🐚', '.zsh': '🐚', '.fish': '🐚',
            '.txt': '📄', '.toml': '📋', '.ini': '⚙️', '.cfg': '⚙️',
            '.xml': '📋', '.html': '🌐', '.css': '🎨', '.scss': '🎨',
            '.sass': '🎨', '.less': '🎨', '.vue': '🟢', '.svelte': '🟠',
            '.rs': '🦀', '.go': '🔵', '.java': '☕', '.kt': '🟣',
            '.swift': '🍎', '.c': '🔵', '.cpp': '🔵', '.h': '🔵',
            '.php': '🟣', '.rb': '💎', '.scala': '🔴', '.clj': '🟢',
            '.hs': '🟣', '.ml': '🟠', '.f90': '🔵', '.r': '🔵',
            '.sql': '🗄️', '.db': '🗄️', '.sqlite': '🗄️',
            '.dockerfile': '🐳', '.docker': '🐳', '.compose': '🐳',
            '.gitignore': '📝', '.gitattributes': '📝', '.editorconfig': '⚙️'
        }

        # Buscar por extensión
        for ext, icon in extension_mapping.items():
            if name_lower.endswith(ext):
                return icon

        # Buscar por nombres específicos
        name_icon_mapping = {
            'readme': '📖', 'license': '📜', 'changelog': '📋',
            'contributing': '🤝', 'contributors': '👥',
            'requirements': '📦', 'package': '📦', 'setup': '⚙️',
            'makefile': '🔧', 'dockerfile': '🐳', 'docker-compose': '🐳',
            'pyproject': '🐍', 'cargo': '🦀', 'composer': '🟣',
            'gemfile': '💎', 'pom.xml': '☕', 'build.gradle': '☕',
            'webpack': '📦', 'rollup': '📦', 'vite': '⚡',
            'jest': '🧪', 'eslint': '🔍', 'prettier': '💅',
            'travis': '🔄', 'circle': '🔄', 'github': '🐙',
            'gitlab': '🦊', 'bitbucket': '🦘', 'azure': '☁️',
            'jenkins': '🤖', 'sonar': '🔍', 'hexroute': '🌐'
        }

        for pattern, icon in name_icon_mapping.items():
            if pattern in name_lower:
                return icon

        # Icono genérico para archivos
        return "📄"

    def _extract_readme_sections(self, content: str) -> Dict[str, str]:
        """Extrae secciones del README generado."""
        sections = self._extract_markdown_sections(content)

        # Convertir la nueva estructura a la estructura simple esperada por _merge_sections
        simple_sections = {}
        for section_name, section_info in sections.items():
            # NO incluir la sección __title__ del README base, ya que el título debe venir del archivo de descripción
            if section_name != '__title__':
                simple_sections[section_name] = section_info['content']

        return simple_sections

    def _extract_project_sections(self, content: str) -> Dict[str, Dict]:
        """Extrae secciones del archivo de descripción del proyecto con sus atributos."""
        return self._extract_markdown_sections(content)

    def _normalize_section_name(self, section_name: str) -> str:
        """Normaliza el nombre de una sección para comparación flexible."""
        # Remover emojis y caracteres especiales, convertir a minúsculas
        import re
        normalized = re.sub(r'[^\w\s]', '', section_name.lower())
        return normalized.strip()

    def _call_ai_model(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Llama al modelo de IA para generar contenido."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=self.config.get('temperature', 0.7),
                system="Eres un asistente experto en documentación técnica. Genera contenido claro, conciso y bien estructurado en Markdown.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error llamando al modelo de IA: {e}")
            return None

    def _generate_auto_content(self, section_name: str) -> Optional[str]:
        """Genera contenido automático para secciones específicas basándose en el análisis del proyecto."""
        try:
            # Obtener el análisis del proyecto
            analysis = self.analyzer.analyze_project()

            # Generar contenido según el tipo de sección
            if 'estructura' in section_name.lower() or 'structure' in section_name.lower():
                return self._generate_structure_content(analysis)
            elif 'características' in section_name.lower() or 'features' in section_name.lower():
                return self._generate_features_content(analysis)
            elif 'instalación' in section_name.lower() or 'installation' in section_name.lower():
                return self._generate_installation_content(analysis)
            elif 'uso' in section_name.lower() or 'usage' in section_name.lower():
                return self._generate_usage_content(analysis)
            elif 'licencia' in section_name.lower() or 'license' in section_name.lower():
                return self._generate_license_content(analysis)

            return None

        except Exception as e:
            self.console.print(f"[yellow]Advertencia: Error generando contenido automático para '{section_name}': {e}[/yellow]")
            return None

    def _generate_structure_content(self, analysis: Dict) -> str:
        """Genera contenido para la sección de estructura del proyecto con formato gráfico mejorado."""
        content = []

        # Obtener estructura real del proyecto
        real_directories = self._get_real_project_structure()

        if real_directories:
            content.append("")
            content.append("```")
            content.append("📁 Estructura del Proyecto")
            content.append("")
            for line in real_directories:
                content.append(line)
            content.append("```")
            content.append("")
            content.append("### 📋 Descripción de Directorios")
            content.append("")

            # Generar descripciones dinámicamente basándose en los directorios encontrados
            dir_descriptions = self._generate_directory_descriptions()

            for dir_icon, description in dir_descriptions.items():
                content.append(f"- **{dir_icon}** {description}")

            content.append("")
            content.append("### 📄 Archivos Principales")
            content.append("")

            # Generar descripciones de archivos dinámicamente
            file_descriptions = self._generate_file_descriptions()

            for file_icon, description in file_descriptions.items():
                content.append(f"- **{file_icon}** {description}")
        else:
            content.append("")
            content.append("```")
            content.append("📁 Estructura Básica")
            content.append("")
            content.append("🌳 proyecto/")
            content.append("   ├── 📚 docs/")
            content.append("   ├── 💻 src/")
            content.append("   ├── 🧪 tests/")
            content.append("   ├── ⚙️ config/")
            content.append("   └── 📄 README.md")
            content.append("```")

        return '\n'.join(content)

    def _generate_directory_descriptions(self) -> Dict[str, str]:
        """Genera descripciones de directorios dinámicamente basándose en los encontrados."""
        descriptions = {}

        # Leer patrones de .gitignore
        gitignore_patterns = self._read_gitignore_patterns()

        # Directorios que siempre se deben mostrar (excepciones al .gitignore)
        always_show = {'.githooks', '.project', '.cursor'}

        # Directorios a ignorar (mismas reglas que en _get_real_project_structure)
        ignore_dirs = {
            '.git', '.gitignore', '.gitattributes', '.github',
            '__pycache__', '.pytest_cache', '.coverage',
            'node_modules', '.venv', 'venv', 'env',
            '.vscode', '.idea', '.DS_Store', 'Thumbs.db',
            '.mypy_cache', '.ruff_cache', '.tox'
        }

        # Escanear directorios reales del proyecto
        try:
            for item in self.base_path.iterdir():
                if item.is_dir():
                    # Aplicar las mismas reglas de filtrado que en _get_real_project_structure
                    should_include = True

                    # Verificar si está en la lista de directorios a ignorar
                    if item.name in ignore_dirs:
                        should_include = False
                    # Verificar si debe ser ignorado según .gitignore
                    elif self._should_ignore_path(item, gitignore_patterns) and item.name not in always_show:
                        should_include = False

                    if should_include:
                        icon = self._get_directory_icon(item.name)
                        description = self._get_directory_description(item.name)
                        descriptions[f"{icon} {item.name}/"] = description
        except Exception:
            pass

        # Si no se encontraron directorios, usar descripciones genéricas
        if not descriptions:
            descriptions = {
                "📚 docs/": "Documentación del proyecto, guías y manuales",
                "💻 src/": "Código fuente principal de la aplicación",
                "🧪 tests/": "Tests unitarios, de integración y e2e",
                "⚙️ config/": "Archivos de configuración y settings",
                "🔧 scripts/": "Scripts de automatización y utilidades",
                "🎨 assets/": "Recursos estáticos (imágenes, CSS, JS)",
                "🗄️ data/": "Datos, bases de datos y archivos de datos",
                "🚀 deploy/": "Configuración de despliegue y Docker",
                "🔄 ci/": "Configuración de CI/CD y pipelines",
                "📦 vendor/": "Dependencias de terceros y librerías"
            }

        return descriptions

    def _get_directory_description(self, dirname: str) -> str:
        """Obtiene una descripción para un directorio basándose en su nombre."""
        name_lower = dirname.lower()

        descriptions = {
            'docs': 'Documentación del proyecto, guías y manuales',
            'documentation': 'Documentación del proyecto, guías y manuales',
            'src': 'Código fuente principal de la aplicación',
            'source': 'Código fuente principal de la aplicación',
            'app': 'Aplicación principal',
            'lib': 'Librerías y módulos reutilizables',
            'tests': 'Tests unitarios, de integración y e2e',
            'test': 'Tests unitarios, de integración y e2e',
            'config': 'Archivos de configuración y settings',
            'conf': 'Archivos de configuración y settings',
            'scripts': 'Scripts de automatización y utilidades',
            'tools': 'Scripts de automatización y utilidades',
            'bin': 'Scripts ejecutables y herramientas',
            'assets': 'Recursos estáticos (imágenes, CSS, JS)',
            'static': 'Recursos estáticos (imágenes, CSS, JS)',
            'public': 'Archivos públicos y estáticos',
            'data': 'Datos, bases de datos y archivos de datos',
            'db': 'Bases de datos y esquemas',
            'deploy': 'Configuración de despliegue y Docker',
            'dist': 'Archivos de distribución y build',
            'build': 'Archivos de construcción y compilación',
            'ci': 'Configuración de CI/CD y pipelines',
            'cd': 'Configuración de CI/CD y pipelines',
            'vendor': 'Dependencias de terceros y librerías',
            'deps': 'Dependencias de terceros y librerías',
            'scaffold': 'Plantillas y estructuras base',
            'templates': 'Plantillas y estructuras base',
            'ideas': 'Ideas y conceptos del proyecto',
            'logs': 'Archivos de log y temporales',
            'tmp': 'Archivos temporales',
            'api': 'Endpoints y APIs del proyecto',
            'models': 'Modelos de datos y entidades',
            'schemas': 'Esquemas de datos y validaciones',
            'migrations': 'Migraciones de base de datos',
            'analysis': 'Análisis y reportes',
            'licenses': 'Licencias y archivos legales',
            'cursor': 'Configuración del editor Cursor IDE',
            'project': 'Configuración y metadatos del proyecto',
            'githooks': 'Hooks de Git y configuraciones de commit',
            'sops': 'Archivos de configuración SOPS',
            'mo': 'Archivos de modelo y configuración',
            'pr': 'Configuración de Pull Requests',
            'ws': 'Configuración de workspace',
            'brain': 'Configuración de IA y contexto del proyecto'
        }

        for pattern, description in descriptions.items():
            if pattern in name_lower:
                return description

        return f"Directorio {dirname} del proyecto"

    def _generate_file_descriptions(self) -> Dict[str, str]:
        """Genera descripciones de archivos dinámicamente basándose en los encontrados."""
        descriptions = {}

        # Extensiones comunes con descripciones
        extension_descriptions = {
            "🐍 *.py": "Scripts y módulos Python",
            "🟨 *.js": "Archivos JavaScript",
            "🔷 *.ts": "Archivos TypeScript",
            "📋 *.json": "Configuraciones y metadatos",
            "⚙️ *.yml/*.yaml": "Configuraciones de servicios",
            "📝 *.md": "Documentación en Markdown",
            "🐚 *.sh": "Scripts de shell y bash",
            "📄 *.txt": "Archivos de texto y documentación",
            "📋 *.toml": "Configuraciones en formato TOML",
            "⚙️ *.ini/*.cfg": "Archivos de configuración",
            "🌐 *.html": "Archivos HTML",
            "🎨 *.css": "Hojas de estilo CSS",
            "🟢 *.vue": "Componentes Vue.js",
            "🟠 *.svelte": "Componentes Svelte",
            "🦀 *.rs": "Código Rust",
            "🔵 *.go": "Código Go",
            "☕ *.java": "Código Java",
            "🟣 *.kt": "Código Kotlin",
            "🍎 *.swift": "Código Swift",
            "🔵 *.c/*.cpp": "Código C/C++",
            "🟣 *.php": "Código PHP",
            "💎 *.rb": "Código Ruby",
            "🗄️ *.sql": "Consultas y esquemas SQL",
            "🐳 Dockerfile": "Configuración de contenedores Docker",
            "📖 README": "Documentación principal del proyecto",
            "📜 LICENSE": "Licencia del proyecto",
            "📋 CHANGELOG": "Registro de cambios del proyecto",
            "🤝 CONTRIBUTING": "Guía de contribución al proyecto"
        }

        return extension_descriptions

    def _generate_features_content(self, analysis: Dict) -> str:
        """Genera contenido para la sección de características."""
        content = []

        # Obtener características del análisis
        differentiators = analysis.get('differentiators', {})
        features = differentiators.get('unique_features', [])

        if features:
            for feature in features[:8]:  # Máximo 8 características
                content.append(f"- {feature}")
        else:
            content.append("- Herramientas multiplataforma")
            content.append("- Automatización de tareas")
            content.append("- Configuración flexible")
            content.append("- Integración con sistemas existentes")

        return '\n'.join(content)

    def _generate_installation_content(self, analysis: Dict) -> str:
        """Genera contenido para la sección de instalación."""
        content = []

        # Obtener tecnologías del análisis
        technologies = analysis.get('technologies', {})
        languages = technologies.get('languages', [])

        content.append("")
        content.append("```bash")
        if 'Python' in languages:
            content.append("pip install -r requirements.txt")
        content.append("```")

        return '\n'.join(content)

    def _generate_usage_content(self, analysis: Dict) -> str:
        """Genera contenido para la sección de uso."""
        content = []

        # Obtener archivos principales del análisis
        global_analysis = analysis.get('global_analysis', {})
        main_files = global_analysis.get('main_functions', [])

        content.append("")
        content.append("```bash")
        if main_files:
            main_file = main_files[0].split('/')[-1]
            content.append(f"# Ejemplo básico de uso")
            content.append(f"python {main_file} --help")
        else:
            content.append("# Ejemplo básico de uso")
            content.append("python main.py --help")
        content.append("```")

        return '\n'.join(content)

    def _generate_license_content(self, analysis: Dict) -> str:
        """Genera contenido para la sección de licencia."""
        content = []

        content.append("")
        content.append("Este proyecto está bajo la Licencia GPLv3. Ver [LICENSE.md](LICENSE.md) para más detalles.")

        return '\n'.join(content)

@click.group()
def cli():
    """Generador de documentación para el ecosistema Git Branch Tools."""
    pass

@cli.command(
    help="""
Genera la documentación para un tipo de documento específico.

Para CHANGELOG:
- Filtra automáticamente commits de prueba y testing.
- Deduplica mensajes repetidos y consolida cambios similares.
- Sigue el estándar Keep a Changelog.
- No usa IA por defecto (opcional con --use-ai).
- El resultado es un CHANGELOG profesional, limpio y legible.

Para CONTRIBUTING:
- Analiza automáticamente la estructura del proyecto.
- Detecta tecnologías, flujo de trabajo y configuración.
- Genera CONTRIBUTING.md adaptado al proyecto.
- Opcional con --use-ai para mejorar el contenido.

Para PROJECT_DESCRIPTION:
- Analiza automáticamente el proyecto.
- Genera un archivo PROJECT_DESCRIPTION.md con información detallada.
- Opcional con --use-ai para mejorar el contenido.

Ejemplo:
  python docgen.py generate --doc-type changelog --output CHANGELOG.md
  python docgen.py generate --doc-type changelog --output CHANGELOG.md --use-ai
  python docgen.py generate --doc-type contributing --output CONTRIBUTING.md
  python docgen.py generate --doc-type contributing --output CONTRIBUTING.md --use-ai
  python docgen.py generate --doc-type project_description --output PROJECT_DESCRIPTION.md
  python docgen.py generate --doc-type project_description --output PROJECT_DESCRIPTION.md --use-ai
""",
    context_settings={"help_option_names": ["--help", "-h"]}
)
@click.option('--doc-type', required=True, help='Tipo de documentación a generar. Ej: changelog, contributing, readme, user_guide, api_docs.')
@click.option('--output', required=True, help='Archivo de salida para la documentación.')
@click.option('--context', help='Contexto específico a usar para la generación.')
@click.option('--custom-type', help='Tipo personalizado para cargar configuraciones específicas de análisis y TOC.')
@click.option('--custom-instructions', help='Instrucciones personalizadas para añadir al prompt.')
@click.option('--model', help='Modelo de IA a usar (sobrescribe la configuración).')
@click.option('--base-path', default=os.getcwd(), help='Ruta base del proyecto.')
@click.option('--use-ai', is_flag=True, help='Usar IA para mejorar el contenido (solo para CHANGELOG y CONTRIBUTING).')
def generate(doc_type, output, context, custom_instructions, custom_type, model, base_path, use_ai):
    """Genera la documentación para un tipo de documento específico."""
    console = Console()
    try:
        # 1. Inicializar el generador (esto carga la config y el analizador)
        generator = DocumentationGenerator(
            base_path=Path(base_path) if base_path else Path.cwd(),
            doc_type=doc_type,
            context=context,
            custom_type=custom_type,
            model=model
        )

        # 2. Mostrar banner y verificaciones
        console.print(Panel(
            f"[bold blue]Generando documentación[/bold blue]\n"
            f"Tipo: {doc_type}\n"
            f"Salida: {output}\n"
            f"Contexto: {context or 'Ninguno'}\n"
            f"Modelo: {generator.model}\n"
            f"Tipo personalizado: {custom_type or 'Ninguno'}",
            border_style="blue"
        ))

        # 3. Generar documentación con barras de progreso
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            # Tarea de análisis
            analysis_task = progress.add_task(
                "[cyan]Analizando código base...",
                total=100
            )

            # Pasar el objeto de progreso al generador
            generator.progress = progress
            generator.analysis_task = analysis_task

            # Llamar al método de generación
            try:
                generator.generate_documentation(
                    output_file=output,
                    custom_instructions=custom_instructions,
                    use_ai=use_ai
                )
                progress.update(analysis_task, completed=100)
                console.print("[green]✓ Proceso completado exitosamente[/green]")
            except Exception as e:
                progress.update(analysis_task, completed=100)
                raise e

    except Exception as e:
        console.print(Panel(
            f"[bold red]✗ Error[/bold red]\n{str(e)}",
            border_style="red"
        ))
        raise click.Abort()

if __name__ == '__main__':
    cli()
