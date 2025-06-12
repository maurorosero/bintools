#!/usr/bin/env python3
"""
Analizador de documentación para el ecosistema Git Branch Tools.
Detecta cambios en funcionalidades y gaps en la documentación.
"""

import click
import yaml
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.public_functions = set()
        self.command_functions = set()
        self.argparse_functions = set()
        self._current_class = None
        self._in_argparse = False
        self._in_click = False

    def visit_ClassDef(self, node: ast.ClassDef):
        prev_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = prev_class

    def visit_Call(self, node: ast.Call):
        # Detectar uso de argparse
        if isinstance(node.func, ast.Name):
            if node.func.id in ('ArgumentParser', 'add_argument'):
                self._in_argparse = True
        # Detectar uso de click
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in ('command', 'option', 'argument'):
                self._in_click = True
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Ignorar funciones privadas
        if node.name.startswith('_'):
            return

        # Verificar si es una función main o entry point
        is_main = (node.name == 'main' or
                  node.name == 'cli' or
                  'entry' in node.name.lower())

        # Verificar si está decorada con click.command
        has_click_decorator = any(
            isinstance(d, ast.Call) and
            isinstance(d.func, ast.Attribute) and
            d.func.attr == 'command'
            for d in node.decorator_list
        )

        # Verificar si está en un contexto de argparse
        is_argparse = self._in_argparse

        # Si cumple alguna condición, agregarla a la lista correspondiente
        if is_main or has_click_decorator:
            self.command_functions.add(node.name)
        elif is_argparse:
            self.argparse_functions.add(node.name)
        elif not node.name.startswith('_'):
            self.public_functions.add(node.name)

        self.generic_visit(node)

def analyze_file(file_path: Path) -> Dict:
    """Analiza un archivo Python y retorna información sobre sus funciones públicas."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        visitor = FunctionVisitor()
        visitor.visit(tree)

        return {
            'commands': sorted(visitor.command_functions),
            'argparse_functions': sorted(visitor.argparse_functions),
            'public_functions': sorted(visitor.public_functions -
                                     visitor.command_functions -
                                     visitor.argparse_functions)
        }
    except Exception as e:
        click.echo(f"Error analizando {file_path}: {str(e)}")
        return {'commands': [], 'argparse_functions': [], 'public_functions': []}

def load_config(config_path: Path) -> Dict:
    """Carga la configuración del analizador."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        click.echo(f"Error cargando configuración: {str(e)}")
        return {}

def analyze_tools(config: Dict, base_path: Path) -> Dict:
    """Analiza las herramientas según la configuración."""
    results = {}
    changes_detected = False

    for tool_name, tool_config in config.get('tools', {}).items():
        tool_path = base_path / tool_config['path']
        if not tool_path.exists():
            click.echo(f"Error: La herramienta {tool_name} no existe en {tool_path}")
            continue

        analysis = analyze_file(tool_path)
        if analysis['commands'] or analysis['argparse_functions'] or analysis['public_functions']:
            results[tool_name] = analysis
            changes_detected = True

    return results, changes_detected

@click.command()
@click.option('--config', '-c',
              default='docs/config/git_tools_analyzer.yaml',
              help='Ruta al archivo de configuración')
@click.option('--base-path', '-b',
              default=str(Path.cwd()),
              help='Ruta base donde buscar las herramientas')
@click.option('--output', '-o',
              default='reports/changes.yaml',
              help='Archivo de salida para el reporte')
def main(config: str, base_path: str, output: str):
    """Analiza las herramientas Git y detecta cambios que necesitan documentación."""
    config_path = Path(config)
    base_path = Path(base_path)
    output_path = Path(output)

    if not config_path.exists():
        click.echo(f"Error: El archivo de configuración {config} no existe")
        return

    config_data = load_config(config_path)
    if not config_data:
        return

    results, changes_detected = analyze_tools(config_data, base_path)

    # Crear directorio de reportes si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Guardar resultados
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump({
            'changes_detected': changes_detected,
            'tools': results
        }, f, default_flow_style=False, sort_keys=False)

    click.echo(f"changes_detected: {str(changes_detected).lower()}")
    if changes_detected:
        click.echo(f"Reporte guardado en: {output_path}")

if __name__ == '__main__':
    main()
