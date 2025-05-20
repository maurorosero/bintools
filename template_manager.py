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

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

class FileHeaderStandardizer:
    """Clase para estandarizar headers de archivos existentes."""
    
    def __init__(self, template_manager: 'TemplateManager'):
        """Inicializa el estandarizador con una referencia al TemplateManager."""
        self.template_manager = template_manager
        self.logger = logging.getLogger(__name__)
        self.author_name = self.template_manager.config["default_variables"].get("author_name", "MAURO ROSERO PÉREZ")
        
        # Patrones para extraer metadatos específicos
        self.metadata_patterns = {
            'python': {
                'version': r'Version:\s*(.*?)(?:\n|$)',
                'author': r'Author:\s*(.*?)(?:\n|$)',
                'created': r'Created:\s*(.*?)(?:\n|$)',
                'description': r'"""(.*?)(?:\n|$)'
            },
            'bash': {
                'version': r'#\s*Version:\s*(.*?)(?:\n|$)',
                'author': r'#\s*Author:\s*(.*?)(?:\n|$)',
                'created': r'#\s*Created:\s*(.*?)(?:\n|$)',
                'description': r'#\s*Description:\s*(.*?)(?:\n|$)'
            },
            'javascript': {
                'version': r'@version\s*(.*?)(?:\n|$)',
                'author': r'@author\s*(.*?)(?:\n|$)',
                'created': r'@created\s*(.*?)(?:\n|$)',
                'description': r'\*\s*(.*?)(?:\n|$)'
            },
            'typescript': {
                'version': r'@version\s*(.*?)(?:\n|$)',
                'author': r'@author\s*(.*?)(?:\n|$)',
                'created': r'@created\s*(.*?)(?:\n|$)',
                'description': r'\*\s*(.*?)(?:\n|$)'
            },
            'markdown': {
                'version': r'Version:\s*(.*?)(?:\n|$)',
                'author': r'Author:\s*(.*?)(?:\n|$)',
                'created': r'Created:\s*(.*?)(?:\n|$)',
                'description': r'(?:Description|Purpose):\s*(.*?)(?:\n|$)'
            }
        }

    def _has_header_tag(self, content: str, file_type: str) -> bool:
        """
        Verifica si el archivo tiene el HEADER_END_TAG correspondiente a su tipo.
        
        Args:
            content: Contenido del archivo
            file_type: Tipo de archivo (python, bash, etc.)
            
        Returns:
            bool: True si el archivo tiene el tag y es susceptible a fix
        """
        if file_type not in HEADER_END_TAGS:
            return False
            
        tag = HEADER_END_TAGS[file_type]
        return tag in content

    def _extract_existing_metadata(self, content: str, file_type: str) -> Dict[str, str]:
        """
        Extrae metadatos existentes del header del archivo.
        Se enfoca en las variables críticas: author, created, version.
        
        Args:
            content: Contenido del archivo
            file_type: Tipo de archivo
            
        Returns:
            Dict[str, str]: Diccionario con los metadatos extraídos
        """
        metadata = {}
        
        # Obtener patrones específicos para el tipo de archivo
        patterns = self.metadata_patterns.get(file_type, {})
        
        # Extraer descripción usando el CodeAnalyzer
        metadata['description'] = self.template_manager.analyzer.extract_description(content, file_type)
        
        # Extraer metadatos críticos
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                metadata[key] = match.group(1).strip()
        
        # Procesar el autor para separar nombre y email si es necesario
        if 'author' in metadata:
            author_parts = re.match(r'(.*?)\s*<([^>]+)>', metadata['author'])
            if author_parts:
                metadata['author_name'] = author_parts.group(1).strip()
                metadata['author_email'] = author_parts.group(2).strip()
            else:
                metadata['author_name'] = metadata['author']
                metadata['author_email'] = ''
        
        return metadata

    def _remove_existing_header(self, content: str, file_type: str) -> str:
        """
        Elimina el header existente hasta el HEADER_END_TAG.
        
        Args:
            content: Contenido del archivo
            file_type: Tipo de archivo
            
        Returns:
            str: Contenido del archivo sin el header
        """
        if not self._has_header_tag(content, file_type):
            return content
            
        tag = HEADER_END_TAGS[file_type]
        parts = content.split(tag, 1)
        
        if len(parts) > 1:
            return parts[1].lstrip()
        return content

    def _generate_new_header(self, filepath: str, metadata: Dict[str, str], file_type: str) -> str:
        """
        Genera un nuevo header estandarizado usando el TemplateManager.
        
        Args:
            filepath: Ruta del archivo
            metadata: Metadatos extraídos del header actual
            file_type: Tipo de archivo
            
        Returns:
            str: Nuevo header generado
        """
        try:
            # Cargar la plantilla
            template = self.template_manager._load_template(file_type)
            
            # Preparar variables básicas
            variables = {
                "description": metadata.get('description', 'Sin descripción disponible'),
                "content": "",  # El contenido se maneja por separado
                "version": metadata.get('version', '0.1.0'),
                "created": metadata.get('created', ''),
                "author_name": metadata.get('author_name', self.author_name),
                "author_email": metadata.get('author_email', '')
            }
            
            # Obtener valores de todas las variables definidas en config
            for var_name in self.template_manager.config["variables"]:
                var_value = self.template_manager._get_variable_value(var_name, filepath)
                variables[var_name] = var_value
            
            # Añadir variables por defecto
            for var_name, var_value in self.template_manager.config["default_variables"].items():
                if var_name not in variables:  # No sobrescribir valores extraídos
                    variables[var_name] = var_value
            
            # Añadir variables opcionales si es necesario
            for var_name, var_config in self.template_manager.config.get("optional_variables", {}).items():
                if var_config.get("only_when_ai_generated", False):
                    variables[var_name] = var_config.get("value", "")
            
            # Reemplazar variables en la plantilla
            for var_name, var_value in variables.items():
                # Reemplazar tanto {{var_name}} como {{ var_name }}
                template = template.replace(f"{{{{{var_name}}}}}", str(var_value))
                template = template.replace(f"{{{{ {var_name} }}}}", str(var_value))
            
            # Manejar condicionales (como {% if assistant %})
            if "{% if assistant %}" in template:
                if "assistant" in variables and variables["assistant"]:
                    # Mantener el contenido dentro del if
                    template = re.sub(r'{%\s*if\s+assistant\s*%}(.*?){%\s*endif\s*%}', r'\1', template, flags=re.DOTALL)
                else:
                    # Eliminar el contenido dentro del if
                    template = re.sub(r'{%\s*if\s+assistant\s*%}.*?{%\s*endif\s*%}', '', template, flags=re.DOTALL)
            
            # Limpiar cualquier variable no reemplazada
            template = re.sub(r'{{[^}]+}}', '', template)
            template = re.sub(r'{%[^}]+%}', '', template)
            
            # Asegurar que el header termine con una línea en blanco
            if not template.endswith('\n\n'):
                template = template.rstrip() + '\n\n'
            
            return template
            
        except Exception as e:
            self.logger.error(f"Error al generar header para {filepath}: {e}")
            raise

    def standardize_file(self, filepath: str) -> bool:
        """
        Estandariza el header de un archivo existente.
        
        Args:
            filepath: Ruta del archivo a estandarizar
            
        Returns:
            bool: True si se realizaron cambios, False en caso contrario
        """
        try:
            # Verificar si el archivo existe
            if not os.path.isfile(filepath):
                self.logger.warning(f"El archivo {filepath} no existe")
                return False
                
            # Obtener el tipo de archivo
            file_type = self.template_manager._get_file_type(filepath)
            if not file_type:
                self.logger.warning(f"No se pudo determinar el tipo de archivo para {filepath}")
                return False
                
            # Leer el contenido del archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar si el archivo es susceptible a fix
            if not self._has_header_tag(content, file_type):
                self.logger.info(f"El archivo {filepath} no tiene HEADER_END_TAG, ignorando")
                return False
                
            # Extraer metadatos existentes
            metadata = self._extract_existing_metadata(content, file_type)
            
            # Eliminar header existente
            content_without_header = self._remove_existing_header(content, file_type)
            
            # Generar nuevo header
            new_header = self._generate_new_header(filepath, metadata, file_type)
            
            # Combinar nuevo header con el contenido
            new_content = new_header + content_without_header
            
            # Escribir el archivo solo si hay cambios
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.logger.info(f"Header estandarizado en {filepath}")
                return True
            else:
                self.logger.info(f"No se requirieron cambios en {filepath}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error al estandarizar {filepath}: {e}")
            return False

    def standardize_directory(self, directory: str, recursive: bool = True) -> Tuple[int, int]:
        """
        Estandariza los headers de todos los archivos en un directorio.
        
        Args:
            directory: Ruta al directorio a procesar
            recursive: Si es True, procesa subdirectorios recursivamente
            
        Returns:
            Tuple[int, int]: (archivos procesados exitosamente, total de archivos)
        """
        processed = 0
        total = 0
        
        for root, _, files in os.walk(directory):
            if not recursive and root != directory:
                continue
                
            for file in files:
                filepath = os.path.join(root, file)
                if self.template_manager._get_file_type(filepath):
                    total += 1
                    if self.standardize_file(filepath):
                        processed += 1
                        
        return processed, total

class TemplateManager:
    def __init__(self, config_path: str = "templates/config.json"):
        """Inicializa el gestor de plantillas."""
        self.config_path = config_path
        self.config = self._load_config()
        self.templates_dir = Path(self.config["templates_dir"])
        self.analyzer = CodeAnalyzer()
        self.project_version = self._load_project_version()
        self.standardizer = FileHeaderStandardizer(self)  # Añadir el estandarizador

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
            self.logger.error(f"Error al obtener valor para variable {var_name}: {e}")
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
            
            # Preparar las variables
            variables = {
                "description": description,
                "content": content,
                "shebang": self.config["file_types"][file_type].get("shebang", "")
            }

            # Reemplazar variables en la plantilla
            for var_name in self.config["variables"]:
                var_value = self._get_variable_value(var_name, filepath)
                template = template.replace(f"{{{{{var_name}}}}}", var_value)

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

    def standardize_headers(self, path: str, recursive: bool = True) -> Tuple[int, int]:
        """
        Estandariza los headers de los archivos en la ruta especificada.
        
        Args:
            path: Ruta al archivo o directorio a procesar
            recursive: Si es True y path es un directorio, procesa subdirectorios
            
        Returns:
            Tuple[int, int]: (archivos procesados exitosamente, total de archivos)
        """
        path = Path(path)
        if path.is_file():
            success = self.standardizer.standardize_file(str(path))
            return (1, 1) if success else (0, 1)
        elif path.is_dir():
            return self.standardizer.standardize_directory(str(path), recursive)
        else:
            logger.error(f"Ruta no válida: {path}")
            return 0, 0

def main():
    parser = argparse.ArgumentParser(description="Gestor de headers estandarizados")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando create
    create_parser = subparsers.add_parser("create", help="Crear un nuevo archivo con header estandarizado")
    create_parser.add_argument("filepath", help="Ruta del archivo a crear")
    create_parser.add_argument("--content", "-c", default="", help="Contenido inicial del archivo")
    create_parser.add_argument("--config", default="templates/config.json", help="Ruta al archivo de configuración")
    
    # Comando fix (antes standardize)
    fix_parser = subparsers.add_parser("fix", help="Corregir headers de archivos existentes")
    fix_parser.add_argument("path", help="Ruta al archivo o directorio a procesar")
    fix_parser.add_argument("--recursive", "-r", action="store_true", help="Procesar subdirectorios recursivamente")
    fix_parser.add_argument("--config", default="templates/config.json", help="Ruta al archivo de configuración")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    manager = TemplateManager(args.config)
    
    if args.command == "create":
        success = manager.create_file(args.filepath, args.content)
        return 0 if success else 1
    elif args.command == "fix":  # Cambiado de standardize a fix
        processed, total = manager.standardize_headers(args.path, args.recursive)
        logger.info(f"Corregidos {processed} de {total} archivos exitosamente")
        return 0 if processed == total else 1

if __name__ == "__main__":
    exit(main()) 