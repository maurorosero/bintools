#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gestor de plantillas para estandarizar headers en archivos de código.

Copyright (C) 2025 MAURO ROSERO PÉREZ
License: GPLV3

File: template_manager.py
Version: 0.1.0
Author: Mauro Rosero P. <mauro.rosero@gmail.com>
Assistant: Cursor AI (https://cursor.com)
Created: 2025-05-19 21:01:28

This file is managed by template_manager.py.
Any changes to this header will be overwritten on the next fix.
"""

# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

import os
import json
import ast
import datetime
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import argparse
import logging

# Constantes para el banner
APP_NAME = "GESTOR DE HEADERS ESTANDARIZADOS"
VERSION = "0.1.0"  # Se actualizará dinámicamente si existe project/version
AUTHOR = "MAURO ROSERO PÉREZ"
BANNER_WIDTH = 70

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clear_screen():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    """Muestra el banner de la aplicación."""
    clear_screen()
    
    # Centrar el texto
    def center_text(text: str, width: int = BANNER_WIDTH) -> str:
        return text.center(width)
    
    # Construir el banner
    banner = [
        "=" * BANNER_WIDTH,
        center_text(f"{APP_NAME} - Versión {VERSION}"),
        center_text(f"Autor: {AUTHOR}"),
        center_text("Gestor de headers estandarizados para archivos de código"),
        "=" * BANNER_WIDTH,
        ""  # Línea en blanco al final
    ]
    
    # Imprimir el banner
    print("\n".join(banner))

# Definición de los tags de fin de header por tipo de archivo
HEADER_END_TAGS = {
    'python': '# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE',
    'bash': '# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE',
    'javascript': '// HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE',
    'typescript': '// HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE',
    'markdown': '<!-- HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE -->'
}

class CodeAnalyzer:
    """Analiza el código para extraer su descripción."""
    
    @staticmethod
    def extract_description(code: str, file_type: str) -> str:
        """
        Extrae la descripción del código según su tipo.
        
        Para Python:
        - Primero busca un docstring al inicio del módulo
        - Si no hay docstring, busca un comentario # Description:
        
        Para Bash/Shell:
        - Busca un comentario # Description:
        
        Para JavaScript/TypeScript:
        - Busca un comentario // Description:
        """
        if not code.strip():
            return "Sin descripción disponible"
            
        lines = code.strip().split('\n')
        
        if file_type == 'python':
            # Intentar extraer de docstring
            try:
                tree = ast.parse(code)
                # Obtener solo el primer docstring del módulo
                for node in ast.walk(tree):
                    if isinstance(node, ast.Module) and ast.get_docstring(node, clean=True):
                        return ast.get_docstring(node, clean=True).split('\n')[0].strip()
            except:
                pass
                
            # Buscar comentario # Description:
            for line in lines[:5]:  # Buscar en las primeras 5 líneas
                if line.strip().startswith('# Description:'):
                    return line.split(':', 1)[1].strip()
                    
        elif file_type in ['bash', 'shellscript']:
            # Buscar comentario # Description:
            for line in lines[:5]:
                if line.strip().startswith('# Description:'):
                    return line.split(':', 1)[1].strip()
                    
        elif file_type in ['javascript', 'typescript']:
            # Buscar comentario // Description:
            for line in lines[:5]:
                if line.strip().startswith('// Description:'):
                    return line.split(':', 1)[1].strip()
        
        return "Sin descripción disponible"

class TemplateManager:
    def __init__(self, config_path: str = "templates/config.json"):
        """Inicializa el gestor de plantillas."""
        self.config_path = config_path
        self.config = self._load_config()
        self.templates_dir = Path(self.config["templates_dir"])
        self.analyzer = CodeAnalyzer()
        self.project_version = self._load_project_version()

    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo JSON."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error al cargar la configuración: {e}")
            raise

    def _load_project_version(self) -> Optional[str]:
        """Intenta cargar la versión desde ./project/version.
        
        Returns:
            Optional[str]: La versión si el archivo existe y es válido, None en caso contrario.
        """
        version_file = Path("./project/version")
        try:
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    version = f.read().strip()
                    if version:  # Verificar que no esté vacío
                        return version
        except Exception as e:
            logger.warning(f"No se pudo leer la versión desde {version_file}: {e}")
        return None

    def _get_file_type(self, filepath: str) -> Optional[str]:
        """Determina el tipo de archivo basado en su extensión."""
        ext = Path(filepath).suffix.lower()
        for file_type, info in self.config["file_types"].items():
            if ext in info["extensions"]:
                return file_type
        return None

    def _load_template(self, file_type: str) -> str:
        """Carga la plantilla para el tipo de archivo especificado."""
        template_path = self.templates_dir / self.config["file_types"][file_type]["template"]
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error al cargar la plantilla {template_path}: {e}")
            raise

    def _get_variable_value(self, var_name: str, filepath: str) -> str:
        """Obtiene el valor de una variable según su tipo."""
        try:
            # Variables dinámicas (CURRENT_YEAR, CURRENT_DATE, etc.)
            if var_name in self.config["variables"]:
                var_config = self.config["variables"][var_name]
                if var_config["type"] == "date":
                    return datetime.datetime.now().strftime(var_config["format"])
                elif var_config["type"] == "file":
                    if var_config["property"] == "name":
                        return Path(filepath).name
                    elif var_config["property"] == "path":
                        return str(Path(filepath).absolute())
                elif var_config["type"] == "default":
                    return var_config.get("value", "")
            
            # Variables con valores por defecto
            if var_name in self.config["default_variables"]:
                return self.config["default_variables"][var_name]
            
            # Variables opcionales
            if var_name in self.config.get("optional_variables", {}):
                var_config = self.config["optional_variables"][var_name]
                if var_config.get("only_when_ai_generated", False):
                    return var_config.get("value", "")
                return ""
            
            # Si no se encuentra un valor, usar cadena vacía
            return ""
            
        except Exception as e:
            logger.error(f"Error al obtener valor para variable {var_name}: {e}")
            return ""

    def create_file(self, filepath: str, content: str = "") -> bool:
        """
        Crea un nuevo archivo con el header apropiado.
        La descripción se extrae automáticamente del contenido.
        """
        try:
            file_type = self._get_file_type(filepath)
            if not file_type:
                logger.error(f"Tipo de archivo no soportado: {filepath}")
                return False

            # Extraer descripción del código
            description = self.analyzer.extract_description(content, file_type)
            
            # Cargar la plantilla
            template = self._load_template(file_type)
            
            # Preparar las variables básicas
            variables = {
                "description": description,
                "content": content,
                "shebang": self.config["file_types"][file_type].get("shebang", "")
            }

            # 1. Reemplazar variables dinámicas (CURRENT_YEAR, etc.)
            for var_name in self.config["variables"]:
                var_value = self._get_variable_value(var_name, filepath)
                template = template.replace(f"{{{{{var_name}}}}}", var_value)

            # 2. Reemplazar variables por defecto
            for var_name, var_value in self.config["default_variables"].items():
                template = template.replace(f"{{{{{var_name}}}}}", var_value)

            # 3. Reemplazar variables opcionales
            for var_name, var_config in self.config.get("optional_variables", {}).items():
                var_value = var_config.get("value", "")
                if var_config.get("only_when_ai_generated", False):
                    # Reemplazar el bloque condicional
                    pattern = f"{{{{#if {var_name}}}}}(.*?){{{{/if}}}}"
                    if var_value:
                        template = re.sub(pattern, r"\1", template, flags=re.DOTALL)
                        # También reemplazar la variable dentro del bloque
                        template = template.replace(f"{{{{{var_name}}}}}", var_value)
                    else:
                        template = re.sub(pattern, "", template, flags=re.DOTALL)
                else:
                    # Si no es condicional, reemplazar directamente
                    template = template.replace(f"{{{{{var_name}}}}}", var_value)

            # 4. Reemplazar variables básicas (description, content, shebang)
            for var_name, var_value in variables.items():
                template = template.replace(f"{{{{{var_name}}}}}", var_value)

            # Crear el archivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)

            logger.info(f"Archivo creado exitosamente: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error al crear el archivo {filepath}: {e}")
            return False

def main():
    # Mostrar el banner al inicio
    show_banner()
    
    parser = argparse.ArgumentParser(
        description="""
Gestor de headers estandarizados para archivos de código.

Este script permite crear nuevos archivos con headers estandarizados según el tipo de archivo.
Los headers incluyen metadatos como descripción, versión, autor, fecha de creación, etc.

Tipos de archivo soportados:
- Python (.py)
- Bash/Shell (.sh)
- JavaScript (.js)
- TypeScript (.ts)
- Markdown (.md)

El script utiliza plantillas definidas en el directorio templates/ para generar
los headers según el tipo de archivo. La configuración se carga desde
templates/config.json por defecto.

La descripción del archivo se extrae automáticamente:
- Para Python: del docstring del módulo o del comentario # Description:
- Para Bash: del comentario # Description:
- Para JavaScript/TypeScript: del comentario // Description:

Ejemplos de uso:
  # Crear un nuevo archivo Python con contenido inicial
  template_manager.py create script.py --content "print('Hola mundo')"

  # Crear un nuevo archivo Bash vacío
  template_manager.py create script.sh

  # Usar una configuración personalizada
  template_manager.py create script.py --config mi_config.json
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando create
    create_parser = subparsers.add_parser(
        "create",
        help="Crear un nuevo archivo con header estandarizado",
        description="""
Crea un nuevo archivo con un header estandarizado según su tipo.

El header incluirá:
- Descripción del archivo (extraída automáticamente del contenido)
- Versión (por defecto 0.1.0 o desde project/version)
- Autor (desde git config o valor por defecto)
- Fecha de creación
- Copyright y licencia
- Tags de gestión del header

El archivo se creará en la ruta especificada, y si ya existe, será sobrescrito.
"""
    )
    create_parser.add_argument(
        "filepath",
        help="Ruta donde se creará el archivo (ej: src/script.py, docs/README.md)"
    )
    create_parser.add_argument(
        "--content", "-c",
        default="",
        help="Contenido inicial del archivo. La descripción se extraerá de este contenido"
    )
    create_parser.add_argument(
        "--config",
        default="templates/config.json",
        help="Ruta al archivo de configuración JSON que define las plantillas y variables"
    )

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    manager = TemplateManager(args.config)
    
    if args.command == "create":
        success = manager.create_file(args.filepath, args.content)
        return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 