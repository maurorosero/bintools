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
        """Inicializa el analizador con la configuración proporcionada."""
        if self._analyzer_initialized:
            return

        # Para CHANGELOG, usar ChangelogAnalyzer
        if config.get('doc_type') == 'changelog':
            self.analyzer = ChangelogAnalyzer(self.base_path, config)
            if not self.analyzer:
                raise RuntimeError("No se pudo inicializar el analizador de CHANGELOG")
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

        # 2. Cargar configuración de análisis
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

        return config

    def generate_documentation(self, output_file: str, custom_instructions: Optional[str] = None, use_ai: bool = False) -> None:
        """Genera la documentación usando el modelo de Anthropic."""
        try:
            # Para CHANGELOG, usar generación sin IA por defecto
            if self.config.get('doc_type') == 'changelog':
                self._generate_changelog(output_file, custom_instructions, use_ai)
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

            self.console.print(f"[green]✓ Documentación generada y guardada en: {output_file}[/green]")

        except Exception as e:
            self.console.print(Panel(
                f"[bold red]✗ Error[/bold red]\n{str(e)}",
                border_style="red"
            ))
            raise click.Abort()

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

    def _analyze_codebase(self) -> Dict:
        """Analiza el código base para generar documentación."""
        if not self.analyzer:
            raise RuntimeError("El analizador no está inicializado")

        # Usar el método _analyze_codebase del analizador
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

Ejemplo:
  python docgen.py generate --doc-type changelog --output CHANGELOG.md
  python docgen.py generate --doc-type changelog --output CHANGELOG.md --use-ai
""",
    context_settings={"help_option_names": ["--help", "-h"]}
)
@click.option('--doc-type', required=True, help='Tipo de documentación a generar. Ej: changelog, readme, user_guide, api_docs.')
@click.option('--output', required=True, help='Archivo de salida para la documentación.')
@click.option('--context', help='Contexto específico a usar para la generación.')
@click.option('--custom-type', help='Tipo personalizado para cargar configuraciones específicas de análisis y TOC.')
@click.option('--custom-instructions', help='Instrucciones personalizadas para añadir al prompt.')
@click.option('--model', help='Modelo de IA a usar (sobrescribe la configuración).')
@click.option('--base-path', default=os.getcwd(), help='Ruta base del proyecto.')
@click.option('--use-ai', is_flag=True, help='Usar IA para mejorar el contenido (solo para CHANGELOG).')
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
