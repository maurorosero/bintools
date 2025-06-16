#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (C) <2025> MAURO ROSERO PÉREZ (ROSERO ONE DEVELOPMENT)

Script Name: quality_manager.py
Version:     0.1.2
Description: Gestiona los niveles de calidad y formatos de commit de manera independiente.
Created:     2025-06-14
Modified:    2025-06-16 17:00:02
Author:      Mauro Rosero Pérez <mauro@rosero.one>
Assistant:   Cursor AI (https://cursor.com)
"""

"""
Quality Manager para el ecosistema Git Branch Manager.
"""

import yaml
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Any, Union
from enum import Enum
import traceback
import os
import re
from datetime import datetime

class QualityLevel(Enum):
    """Niveles de calidad disponibles."""
    MINIMAL = 'minimal'
    STANDARD = 'standard'
    ENTERPRISE = 'enterprise'

class HookType(Enum):
    """Tipos de hooks disponibles."""
    FORMAT = 'format'
    EXEC = 'exec'
    SIZE = 'size'
    DETECT_SECRETS = 'detect-secrets'  # pragma: allowlist secret
    COMMITLINT = 'commitlint'
    BRANCH_WORKFLOW_COMMIT = 'branch-workflow-commit'
    BRANCH_WORKFLOW_PUSH = 'branch-workflow-push'
    HEADER_VALIDATOR = 'header-validator'  # Nuevo tipo de hook
    HEADER_UPDATE = 'header-update'  # Nuevo tipo de hook para actualización de headers

class QualityManager:
    """Gestiona los niveles de calidad y formatos de commit."""

    def __init__(self, workspace_root: Path):
        """
        Inicializa el QualityManager.

        Args:
            workspace_root: Ruta raíz del workspace
        """
        # Si workspace_root termina en .githooks, lo removemos
        if workspace_root.name == '.githooks':
            self.workspace_root = workspace_root.parent
        else:
            self.workspace_root = workspace_root

        self.config_dir = self.workspace_root / '.githooks/config'
        self.levels_dir = self.config_dir / 'levels'
        self.active_dir = self.config_dir / 'active'
        self.commit_formats_dir = self.workspace_root / 'scaffold/commit-format'

        # Asegurar directorios
        self.active_dir.mkdir(parents=True, exist_ok=True)

        # Cargar configuración activa
        self.active_config = self._load_active_config()
        self._validate_active_config()

        # Cargar el detector de contexto
        try:
            # Intentar importación directa
            sys.path.append(str(Path(__file__).parent))
            import importlib.util
            import types
            validator_path = Path(__file__).parent / 'branch-workflow-validator.py'
            if validator_path.exists():
                spec = importlib.util.spec_from_file_location('branch_workflow_validator', str(validator_path))
                validator_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(validator_module)
                self.git_repo = validator_module.GitRepository(self.workspace_root)
                self.context_detector = validator_module.ContextDetector(self.git_repo)
            else:
                print("⚠️  No se pudo cargar el detector de contexto (no se encontró branch-workflow-validator.py)")
                print("⚠️  Usando configuración manual")
                self.context_detector = None
        except ImportError:
            # Intentar carga dinámica con importlib
            import importlib.util
            import types
            validator_path = Path(__file__).parent / 'branch-workflow-validator.py'
            if validator_path.exists():
                spec = importlib.util.spec_from_file_location('branch_workflow_validator', str(validator_path))
                validator_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(validator_module)
                self.git_repo = validator_module.GitRepository(self.workspace_root)
                self.context_detector = validator_module.ContextDetector(self.git_repo)
            else:
                print("⚠️  No se pudo cargar el detector de contexto (no se encontró branch-workflow-validator.py)")
                print("⚠️  Usando configuración manual")
                self.context_detector = None

    def _load_active_config(self) -> dict:
        """Carga la configuración activa desde los archivos YAML."""
        config = {
            'workflow': {},
            'hooks': {}
        }

        # Cargar workflow.yaml
        workflow_path = self.active_dir / 'workflow.yaml'
        if workflow_path.exists():
            with open(workflow_path) as f:
                config['workflow'] = yaml.safe_load(f) or {}

        # Cargar hooks.yaml
        hooks_path = self.active_dir / 'hooks.yaml'
        if hooks_path.exists():
            with open(hooks_path) as f:
                config['hooks'] = yaml.safe_load(f) or {}

        return config

    def _validate_active_config(self) -> None:
        """Valida que la configuración activa sea válida."""
        if not self.active_config['hooks']:
            return  # No hay configuración activa, es válido

        # Validar estructura de hooks
        required_sections = ['format', 'exec', 'size', 'detect-secrets',
                           'commitlint', 'branch-workflow-commit', 'branch-workflow-push',
                           'header-validator']  # Agregar la nueva sección

        for section in required_sections:
            if section not in self.active_config['hooks']:
                raise ValueError(f"Sección '{section}' no encontrada en hooks.yaml")

        # Validar valores específicos
        hooks_config = self.active_config['hooks']

        # Validar format
        format_hooks = ['trailing-whitespace', 'end-of-file-fixer',
                       'mixed-line-ending', 'fix-byte-order-marker']
        for hook in format_hooks:
            if hook not in hooks_config['format']:
                raise ValueError(f"Hook de formato '{hook}' no encontrado")

        # Validar exec
        exec_hooks = ['check-shebang', 'check-executable']
        for hook in exec_hooks:
            if hook not in hooks_config['exec']:
                raise ValueError(f"Hook de ejecutable '{hook}' no encontrado")

        # Validar size
        if 'max_kb' not in hooks_config['size']:
            raise ValueError("Configuración de tamaño 'max_kb' no encontrada")

        # Validar detect-secrets
        if 'enabled' not in hooks_config['detect-secrets']:
            raise ValueError("Configuración 'enabled' no encontrada en detect-secrets")

        # Validar commitlint
        commitlint_required = ['enabled', 'strict', 'allow_empty', 'allow_merge']
        for key in commitlint_required:
            if key not in hooks_config['commitlint']:
                raise ValueError(f"Configuración '{key}' no encontrada en commitlint")

        # Validar branch-workflow
        for workflow in ['branch-workflow-commit', 'branch-workflow-push']:
            workflow_required = ['enabled', 'strict']
            for key in workflow_required:
                if key not in hooks_config[workflow]:
                    raise ValueError(f"Configuración '{key}' no encontrada en {workflow}")

    def _get_hook_config(self, hook_type: HookType) -> Dict[str, Any]:
        """
        Obtiene la configuración de un hook específico.

        Args:
            hook_type: Tipo de hook

        Returns:
            Dict con la configuración del hook
        """
        if not self.active_config['hooks']:
            raise ValueError("No hay configuración activa de hooks")

        config = self.active_config['hooks'].get(hook_type.value, {})
        if not config:
            raise ValueError(f"No hay configuración para el hook {hook_type.value}")

        return config

    def run_hook(self, hook_type: str) -> Tuple[bool, str]:
        """
        Ejecuta un hook específico según el tipo y la configuración activa.

        Args:
            hook_type: Tipo de hook a ejecutar (de HookType)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        log_file = "/tmp/commit_hook_error.log"
        try:
            hook = HookType(hook_type)
            config = self._get_hook_config(hook)

            # Verificar si el hook está habilitado
            if not config.get('enabled', True):
                return True, f"✅ Hook {hook.value} deshabilitado en la configuración actual"

            # Ejecutar el hook según su tipo
            if hook == HookType.FORMAT:
                return self._run_format_hooks(config)
            elif hook == HookType.EXEC:
                return self._run_exec_hooks(config)
            elif hook == HookType.SIZE:
                return self._run_size_hooks(config)
            elif hook == HookType.DETECT_SECRETS:
                success, msg = self._run_detect_secrets(config)
                if not success:
                    with open(log_file, "w") as f:
                        f.write(msg)
                return success, msg
            elif hook == HookType.COMMITLINT:
                success, msg = self._run_commitlint(config)
                if not success:
                    with open(log_file, "w") as f:
                        f.write(msg)
                return success, msg
            elif hook == HookType.BRANCH_WORKFLOW_COMMIT:
                return self._run_branch_workflow_commit(config)
            elif hook == HookType.BRANCH_WORKFLOW_PUSH:
                return self._run_branch_workflow_push(config)
            elif hook == HookType.HEADER_VALIDATOR:
                return self._run_header_validator(config)
            elif hook == HookType.HEADER_UPDATE:
                return self._run_header_update(config)
            else:
                return False, f"❌ Tipo de hook no válido: {hook_type}"

        except ValueError as e:
            err_msg = f"❌ Error: {str(e)}"
            with open(log_file, "w") as f:
                f.write(err_msg)
            return False, err_msg
        except Exception as e:
            err_msg = f"❌ Error inesperado: {str(e)}"
            with open(log_file, "w") as f:
                f.write(err_msg)
            return False, err_msg

    def _run_format_hooks(self, config: dict) -> Tuple[bool, str]:
        """Ejecuta los hooks de formato."""
        hooks = [
            ('trailing-whitespace', 'trailing-whitespace'),
            ('end-of-file-fixer', 'end-of-file-fixer'),
            ('mixed-line-ending', 'mixed-line-ending'),
            ('fix-byte-order-marker', 'fix-byte-order-marker')
        ]

        results = []
        for hook_name, hook_id in hooks:
            if config.get(hook_name, True):  # Por defecto True si no está especificado
                try:
                    # Ejecutar el hook y capturar tanto stdout como stderr
                    result = subprocess.run(['pre-commit', 'run', hook_id, '--verbose'],
                                         capture_output=True, text=True)

                    # Si el hook modificó archivos (returncode=1) pero no hay error real, considerarlo éxito
                    if result.returncode == 1 and not result.stderr and "Files were modified by this hook" in result.stdout:
                        results.append(f"✅ {hook_name} (archivos modificados)")
                    elif result.returncode != 0:
                        error_msg = result.stderr or result.stdout or "Error desconocido"
                        results.append(f"❌ {hook_name}: {error_msg}")
                    else:
                        results.append(f"✅ {hook_name}")
                except Exception as e:
                    results.append(f"❌ {hook_name}: {str(e)}")

        return len(results) > 0 and all('❌' not in r for r in results), '\n'.join(results)

    def _run_exec_hooks(self, config: dict) -> Tuple[bool, str]:
        """Ejecuta los hooks de verificación de ejecutables."""
        hooks = [
            ('check-shebang', 'check-shebang-scripts-are-executable'),
            ('check-executable', 'check-executables-have-shebangs')
        ]

        results = []
        for hook_name, hook_id in hooks:
            if config.get(hook_name, True):  # Por defecto True si no está especificado
                try:
                    # Los hooks oficiales se ejecutan automáticamente por pre-commit
                    # Solo verificamos si están habilitados en la configuración
                    results.append(f"✅ {hook_name} (ejecutado por pre-commit)")
                except Exception as e:
                    results.append(f"❌ {hook_name}: {str(e)}")

        return len(results) > 0 and all('❌' not in r for r in results), '\n'.join(results)

    def _run_size_hooks(self, config: dict) -> Tuple[bool, str]:
        """Ejecuta los hooks de control de tamaño."""
        max_kb = config.get('max_kb', 500)
        max_total_kb = config.get('max_total_kb', None)

        results = []

        # Verificar tamaño individual
        try:
            # El hook check-added-large-files se ejecuta automáticamente por pre-commit
            # Solo verificamos si está habilitado en la configuración
            results.append(f"✅ Control de tamaño individual ({max_kb}KB) (ejecutado por pre-commit)")
        except Exception as e:
            results.append(f"❌ Control de tamaño individual: {str(e)}")

        # Verificar tamaño total si está configurado
        if max_total_kb:
            try:
                # Implementar verificación de tamaño total
                # TODO: Implementar lógica de verificación de tamaño total
                results.append(f"ℹ️ Verificación de tamaño total ({max_total_kb}KB) no implementada")
            except Exception as e:
                results.append(f"❌ Control de tamaño total: {str(e)}")

        return len(results) > 0 and all('❌' not in r for r in results), '\n'.join(results)

    def _run_detect_secrets(self, config: dict) -> Tuple[bool, str]:
        """Ejecuta el hook de detección de secretos."""
        if not config.get('enabled', False):
            return True, "✅ Detección de secretos deshabilitada"

        try:
            # Obtener el archivo de mensaje de commit
            commit_msg_file = Path(".git/COMMIT_EDITMSG")
            if not commit_msg_file.exists():
                return False, "❌ No se encontró el archivo de mensaje de commit"

            # Leer el contenido del mensaje
            content = commit_msg_file.read_text().strip()

            # Preparar argumentos según la configuración
            args = ['scan', str(commit_msg_file)]
            if 'exclude_patterns' in config:
                for pattern in config['exclude_patterns']:
                    if pattern.strip():
                        escaped_pattern = pattern.strip().replace('*', '.*')
                        args.extend(['--exclude-files', escaped_pattern])

            # Ejecutar detect-secrets
            sys.stderr.write("\nEjecutando detect-secrets con argumentos: " + ' '.join(args) + "\n")
            result = subprocess.run(['detect-secrets', *args],
                                 capture_output=True, text=True)

            if result.returncode != 0:
                error_msg = []
                error_msg.append("=== Detalles del Error de Detección de Secretos ===")

                if result.stdout:
                    error_msg.append("\nSalida estándar:")
                    error_msg.append(result.stdout.strip())
                if result.stderr:
                    error_msg.append("\nError estándar:")
                    error_msg.append(result.stderr.strip())

                error_msg.append("\nContenido del mensaje de commit:")
                error_msg.append("---")
                error_msg.append(content)
                error_msg.append("---")

                error_msg.append("\nConfiguración actual:")
                error_msg.append(f"- fail_on_secret: {config.get('fail_on_secret', True)}")
                error_msg.append(f"- audit_history: {config.get('audit_history', False)}")
                if 'exclude_patterns' in config:
                    error_msg.append("\nPatrones excluidos:")
                    for pattern in config['exclude_patterns']:
                        error_msg.append(f"- {pattern}")

                if not error_msg:
                    error_msg.append("Error desconocido en la detección de secretos")

                msg = f"❌ Detección de secretos falló:\n{chr(10).join(error_msg)}"
                sys.stderr.write(msg + "\n")
                return False, msg
            return True, "✅ Detección de secretos"
        except Exception as e:
            import traceback
            msg = f"❌ Error en detección de secretos: {str(e)}\nTraceback: {traceback.format_exc()}"
            sys.stderr.write(msg + "\n")
            return False, msg

    def _run_commitlint(self, config: dict) -> Tuple[bool, str]:
        """Ejecuta el hook de validación de commits."""
        try:
            # Obtener el archivo de mensaje de commit
            commit_msg_file = Path(".git/COMMIT_EDITMSG")
            if not commit_msg_file.exists():
                return False, "❌ No se encontró el archivo de mensaje de commit"

            # Leer el contenido del mensaje
            content = commit_msg_file.read_text().strip()

            # Obtener la ruta relativa del archivo de configuración
            config_file = Path('.githooks/config/active/commitlint.config.js')
            if not config_file.exists():
                return False, f"❌ No se encontró el archivo de configuración: {config_file}"

            # Preparar argumentos para commitlint usando rutas relativas
            args = ['--config', str(config_file), '--edit', str(commit_msg_file)]

            # Configurar el entorno para commitlint
            env = os.environ.copy()
            # Usar la configuración de require_references del nivel actual
            env["REQUIRE_ISSUE_FROM_META"] = "true" if config.get('require_references', False) else "false"

            # Ejecutar commitlint
            result = subprocess.run(
                ["npx", "commitlint"] + args,
                env=env,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                error_msg = []
                error_msg.append("=== Detalles del Error de Validación de Commit ===")

                if result.stdout:
                    error_msg.append("\nSalida estándar:")
                    error_msg.append(result.stdout.strip())
                if result.stderr:
                    error_msg.append("\nError estándar:")
                    error_msg.append(result.stderr.strip())

                error_msg.append("\nMensaje de commit actual:")
                error_msg.append("---")
                error_msg.append(content)
                error_msg.append("---")

                if not error_msg:
                    error_msg.append("Error desconocido en la validación del commit")

                msg = f"❌ Validación de commit falló:\n{chr(10).join(error_msg)}"
                sys.stderr.write(msg + "\n")
                return False, msg
            return True, "✅ Validación de commit"
        except Exception as e:
            import traceback
            msg = f"❌ Error en validación de commit: {str(e)}\nTraceback: {traceback.format_exc()}"
            sys.stderr.write(msg + "\n")
            return False, msg

    def _run_branch_workflow_commit(self, config: dict) -> Tuple[bool, str]:
        """Ejecuta el hook de validación de workflow en commits."""
        if not config.get('enabled', False):
            return True, "✅ Validación de workflow en commits deshabilitada"

        try:
            # Preparar argumentos según la configuración
            args = ['commit']
            # if config.get('strict', False):
            #     args.append('--strict')

            result = subprocess.run(['.githooks/branch-workflow-validator.py', *args],
                                 capture_output=True, text=True)

            if result.returncode != 0:
                return False, f"❌ Validación de workflow: {result.stderr}"
            return True, "✅ Validación de workflow"
        except Exception as e:
            return False, f"❌ Validación de workflow: {str(e)}"

    def _run_branch_workflow_push(self, config: dict) -> Tuple[bool, str]:
        """Ejecuta el hook de validación de workflow en push."""
        if not config.get('enabled', False):
            return True, "✅ Validación de workflow en push deshabilitada"

        try:
            # Preparar argumentos según la configuración
            args = ['push']
            # if config.get('strict', False):
            #     args.append('--strict')

            result = subprocess.run(['.githooks/branch-workflow-validator.py', *args],
                                 capture_output=True, text=True)

            if result.returncode != 0:
                return False, f"❌ Validación de workflow: {result.stderr}"
            return True, "✅ Validación de workflow"
        except Exception as e:
            return False, f"❌ Validación de workflow: {str(e)}"

    def _extract_header_metadata(self, file_path: Path, check_heading_lines: int = 10) -> Tuple[bool, Union[Dict[str, str], str], str, str]:
        """
        Extrae metadatos del header de un archivo usando la lógica común.

        Args:
            file_path: Ruta al archivo
            check_heading_lines: Número de líneas a revisar (default: 10)

        Returns:
            Tuple[bool, Union[Dict[str, str], str], str, str]: (éxito, metadatos o mensaje de error, tipo de archivo, contenido del header)
        """
        try:
            # Determinar el tipo de archivo
            file_type = self._get_file_type(file_path)
            if not file_type:
                return False, f"Tipo de archivo no soportado: {file_path.suffix}", "", ""

            # Leer las primeras líneas del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(check_heading_lines * 100)  # Leer suficientes caracteres para cubrir las líneas

            # Extraer el bloque de comentario según el tipo de archivo
            header_content = ""
            if file_type == 'python':
                # Para Python, buscar comentarios de bloque usando triple comillas
                match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if match:
                    header_content = match.group(1).strip()
            elif file_type == 'javascript':
                # Para JavaScript, buscar comentarios de bloque usando /* */
                match = re.search(r'/\*(.*?)\*/', content, re.DOTALL)
                if match:
                    # Limpiar los asteriscos al inicio de cada línea
                    header_content = re.sub(r'^\s*\*\s*', '', match.group(1).strip(), flags=re.MULTILINE)
            else:
                # Para otros tipos, buscar comentarios de línea
                lines = content.split('\n')
                header_lines = []
                found_tag = False
                for i, line in enumerate(lines[:check_heading_lines]):
                    # Limpiar la línea
                    clean_line = line.strip()

                    # Buscar comentarios de línea según el tipo de archivo
                    if file_type in ['shell', 'bash'] and clean_line.startswith('#'):
                        # Para shell/bash, remover el # y espacios
                        clean_line = clean_line[1:].strip()
                        if "Check Heading" in clean_line:
                            found_tag = True
                            header_lines.append(clean_line)
                        elif found_tag and clean_line:  # Solo agregar líneas no vacías después de encontrar el tag
                            header_lines.append(clean_line)
                    elif file_type == 'yaml' and clean_line.startswith('#'):
                        clean_line = clean_line[1:].strip()
                        if "Check Heading" in clean_line:
                            found_tag = True
                            header_lines.append(clean_line)
                        elif found_tag and clean_line:
                            header_lines.append(clean_line)
                    elif file_type == 'markdown' and clean_line.startswith('<!--'):
                        if clean_line.endswith('-->'):
                            clean_line = clean_line[4:-3].strip()
                            if "Check Heading" in clean_line:
                                found_tag = True
                                header_lines.append(clean_line)
                            elif found_tag and clean_line:
                                header_lines.append(clean_line)

                if found_tag:
                    header_content = '\n'.join(header_lines)

            if not header_content:
                return False, "No se encontró contenido en el header", file_type, ""

            # Verificar que el header contiene el tag Check Heading
            if "Check Heading" not in header_content:
                return False, "No se encontró el tag 'Check Heading'", file_type, header_content

            # Extraer metadatos usando expresiones regulares más flexibles
            metadata = {}

            # Patrones para diferentes formatos de campos
            patterns = [
                # Patrón para campos en formato "Campo: valor"
                r'(?m)^\s*([^:]+?)\s*:\s*(.+?)(?=\n|$)',
                # Patrón para campos en formato "@campo valor"
                r'(?m)^\s*@(\w+)\s+(.+?)(?=\n|$)',
                # Patrón para campos en formato "Campo = valor"
                r'(?m)^\s*([^=]+?)\s*=\s*(.+?)(?=\n|$)',
                # Patrón para campos en formato "Campo: valor" con múltiples líneas
                r'(?m)^\s*([^:]+?)\s*:\s*((?:.+\n)+?)(?=\n\S|\Z)'
            ]

            # Procesar cada línea del header
            lines = header_content.split('\n')
            current_field = None
            current_value = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Limpiar cualquier asterisco restante al inicio de la línea
                line = re.sub(r'^\s*\*\s*', '', line)

                # Intentar cada patrón en la línea actual
                field_found = False
                for pattern in patterns:
                    matches = re.finditer(pattern, line, re.MULTILINE)
                    for match in matches:
                        field = match.group(1).strip()
                        value = match.group(2).strip()

                        # Normalizar el nombre del campo
                        if field.startswith('@'):
                            field = field[1:]  # Remover @ si existe
                            if field == 'file':
                                field = 'Script Name'  # Normalizar @file a Script Name

                        # Limpiar cualquier asterisco restante en el campo o valor
                        field = re.sub(r'^\s*\*\s*', '', field)
                        value = re.sub(r'^\s*\*\s*', '', value)

                        # Normalizar campos específicos
                        if field == 'Created at':
                            field = 'Created'

                        # Si el campo ya existe, actualizar su valor
                        if field in metadata:
                            if isinstance(metadata[field], list):
                                metadata[field].append(value)
                            else:
                                metadata[field] = [metadata[field], value]
                        else:
                            metadata[field] = value

                        field_found = True
                        break
                    if field_found:
                        break

                # Si no se encontró un campo en esta línea, podría ser una continuación
                if not field_found and current_field:
                    current_value.append(line)
                    metadata[current_field] = '\n'.join(current_value)
                else:
                    current_field = None
                    current_value = []

            return True, metadata, file_type, header_content

        except Exception as e:
            return False, f"Error al extraer metadatos: {str(e)}", "", ""

    def _run_header_validator(self, config: dict) -> Tuple[bool, str]:
        """
        Ejecuta el hook de validación de headers.

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not config.get('enabled', True):
            return True, "✅ Validación de headers deshabilitada"

        # Obtener el número de líneas a revisar, con valor por defecto de 10
        check_heading_lines = config.get('check_heading_lines', 10)
        if not isinstance(check_heading_lines, int) or check_heading_lines < 1:
            return False, f"❌ Configuración inválida: check_heading_lines debe ser un entero positivo, se recibió {check_heading_lines}"

        # Mapeo de alias a nombres normalizados para validación
        field_aliases = {
            'Created at': 'Created',
            'file': 'Script Name',
            '@file': 'Script Name',
            'Script': 'Script Name',
            'Script Name': 'Script Name'
        }

        # Función para normalizar nombres de campos
        def normalize_field_name(key: str) -> str:
            key = key.strip()
            return field_aliases.get(key, key)

        try:
            # Obtener archivos a validar de los argumentos de línea de comandos
            files = sys.argv[1:] if len(sys.argv) > 1 else []

            if not files:
                return True, "✅ No hay archivos para validar"

            # Filtrar archivos que tienen el tag Check Heading y no son archivos de configuración
            files_with_tag = []
            for file_path in files:
                # Excluir archivos de configuración
                if '.githooks/config/' in file_path:
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(check_heading_lines * 100)  # Leer suficientes caracteres para cubrir las líneas
                        if "Check Heading" in content:
                            files_with_tag.append(file_path)
                except Exception:
                    continue  # Ignorar archivos que no se pueden leer

            if not files_with_tag:
                return True, "✅ No hay archivos con tag 'Check Heading' para validar"

            # Usar sets para errores y advertencias para evitar duplicados desde el inicio
            all_errors = set()
            all_warnings = set()

            for file_path in files_with_tag:
                path = Path(file_path)
                if not path.exists():
                    all_errors.add(f"❌ Archivo no encontrado: {file_path}")
                    continue

                # Extraer metadatos usando la lógica común
                success, result, file_type, header_content = self._extract_header_metadata(path, check_heading_lines)
                if not success:
                    all_errors.add(f"❌ {file_path}: {result}")  # result es el mensaje de error
                    continue

                metadata = result  # En caso de éxito, result es el diccionario de metadatos

                # Normalizar los nombres de los campos en los metadatos
                normalized_metadata = {normalize_field_name(k): v for k, v in metadata.items()}

                # Validar campos requeridos
                required_fields = config.get('required_fields', [])
                for field in required_fields:
                    # Verificar si el campo o cualquiera de sus alias está presente
                    field_found = any(normalize_field_name(k) == field for k in metadata.keys())
                    if not field_found:
                        all_errors.add(f"❌ {file_path}: Falta campo requerido '{field}'")

                # Validar campos opcionales
                optional_fields = config.get('optional_fields', [])
                for field in optional_fields:
                    # Verificar si el campo o cualquiera de sus alias está presente
                    if not any(normalize_field_name(k) == field for k in metadata.keys()):
                        all_warnings.add(f"⚠️  {file_path}: Falta campo opcional '{field}'")

            if all_errors:
                error_msg = "\n".join(sorted(all_errors))
                if all_warnings:
                    warning_msg = "\n".join(sorted(all_warnings))
                    return False, f"{error_msg}\n{warning_msg}"
                return False, error_msg
            elif all_warnings:
                warning_msg = "\n".join(sorted(all_warnings))
                return True, warning_msg
            return True, "✅ Todos los headers son válidos"

        except Exception as e:
            return False, f"❌ Error en validación de headers: {str(e)}"

    def _run_header_update(self, config: dict) -> Tuple[bool, str]:
        """
        Ejecuta el hook de actualización de headers.
        Actualiza la fecha de modificación en los headers de los archivos que tienen el tag Check Heading.
        Este hook siempre retorna éxito para no bloquear el commit, incluso si hay errores en la actualización.

        Args:
            config: Configuración del hook que puede incluir:
                - enabled: bool - Si el hook está habilitado
                - date_format: str - Formato de fecha (default: "YYYY-MM-DD HH:MM:SS")
                - check_heading_lines: int - Número de líneas a revisar para el tag Check heading
                - update_fields: list - Lista de campos a actualizar (default: ["Modified"])

        Returns:
            Tuple[bool, str]: (éxito, mensaje) - Siempre retorna True para no bloquear el commit
        """
        if not config.get('enabled', False):
            return True, "✅ Actualización de headers deshabilitada"

        try:
            files_to_update = sys.argv[1:]  # Usamos los archivos pasados como argumentos
            updated_files = []
            errors = []
            staged_files = []

            for file_path in files_to_update:
                try:
                    # Excluir archivos de configuración
                    if '.githooks/config/' in file_path:
                        continue

                    # Extraer metadatos sin validar
                    success, metadata, file_type, header_content = self._extract_header_metadata(Path(file_path), config.get('check_heading_lines', 10))
                    if not success:
                        continue

                    # Obtener el formato de fecha del hook y generar la fecha actual
                    date_format = config.get('date_format', 'YYYY-MM-DD HH:MM:SS')
                    strftime_format = (date_format
                        .replace('YYYY', '%Y')
                        .replace('DD', '%d')
                        .replace('HH', '%H')
                        .replace('SS', '%S')
                        .replace('MM', '%m')
                        .replace('mm', '%M'))
                    current_date = datetime.now().strftime(strftime_format)

                    # Leer el archivo y actualizar solo la línea de Modified
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Obtener los campos a actualizar de la configuración
                    update_fields = config.get('update_fields', ['Modified'])
                    new_content = content
                    file_modified = False

                    # Para cada campo en update_fields, buscar y actualizar su línea
                    for field in update_fields:
                        # Usar un patrón diferente según el tipo de archivo
                        if file_type == 'python':
                            pattern = rf'{field}:.*$'
                            replacement = f'{field}:    {current_date}'
                        elif file_type == 'javascript':
                            # Para JavaScript, buscar líneas con asteriscos al inicio y campos con o sin @
                            pattern = rf'^\s*\*\s*(?:@)?{field}:.*$'
                            replacement = f' * {field}:    {current_date}'
                        else:  # bash y otros
                            pattern = rf'# {field}:.*$'
                            replacement = f'# {field}:    {current_date}'

                        if field == 'Modified':
                            # Para Modified, actualizar con la fecha actual
                            new_content = re.sub(pattern, replacement, new_content, flags=re.MULTILINE | re.IGNORECASE)
                            file_modified = True
                        else:
                            # Para otros campos, mantener su valor actual
                            continue

                    if file_modified:
                        try:
                            # Escribir el archivo modificado
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            updated_files.append(file_path)

                            # Agregar el archivo modificado al staging area
                            try:
                                result = subprocess.run(['git', 'add', file_path],
                                                      check=True,
                                                      capture_output=True,
                                                      text=True)
                                if result.returncode == 0:
                                    staged_files.append(file_path)
                                else:
                                    errors.append(f"Error al agregar {file_path} al staging: {result.stderr}")
                            except subprocess.CalledProcessError as e:
                                errors.append(f"Error al agregar {file_path} al staging: {e.stderr}")
                            except Exception as e:
                                errors.append(f"Error inesperado al agregar {file_path} al staging: {str(e)}")
                        except Exception as e:
                            errors.append(f"Error al escribir {file_path}: {str(e)}")

                except Exception as e:
                    errors.append(f"Error en {file_path}: {str(e)}")
                    continue

            # Construir mensaje final
            message_parts = []
            if updated_files:
                message_parts.append(f"✅ Headers actualizados en {len(updated_files)} archivos: {', '.join(updated_files)}")
            if staged_files:
                message_parts.append(f"✅ Archivos agregados al staging: {', '.join(staged_files)}")
            if errors:
                message_parts.append(f"⚠️ Errores encontrados: {'; '.join(errors)}")
            if not message_parts:
                message_parts.append("✅ No se encontraron archivos que requieran actualización de headers")

            # Siempre retornamos True para no bloquear el commit
            return True, "\n".join(message_parts)

        except Exception as e:
            # Incluso si hay un error general, retornamos éxito para no bloquear el commit
            return True, f"⚠️ Error general en actualización de headers: {str(e)}"

    def list_available_formats(self) -> Dict[str, dict]:
        """
        Lista los formatos de commit disponibles.

        Returns:
            Dict con los formatos disponibles y sus descripciones
        """
        formats = {}
        for config_file in self.commit_formats_dir.glob('commitlint.config.*.js.def'):
            format_name = config_file.stem.replace('commitlint.config.', '').replace('.js.def', '')
            formats[format_name] = {
                'path': str(config_file),
                'description': self._get_format_description(format_name)
            }
        return formats

    def _get_format_description(self, format_name: str) -> str:
        """
        Obtiene la descripción del formato.

        Args:
            format_name: Nombre del formato

        Returns:
            Descripción del formato
        """
        descriptions = {
            'minimal': 'Formato básico para commits simples',
            'simple': 'Formato simple con scope y referencias',
            'conventional': 'Formato convencional completo',
            'semantic': 'Formato semántico con versionado',
            'angular': 'Formato Angular con convenciones estrictas'
        }
        return descriptions.get(format_name, f'Formato {format_name}')

    def _detect_quality_level(self) -> QualityLevel:
        """
        Detecta el nivel de calidad apropiado basado en el contexto del repositorio.

        Returns:
            QualityLevel: Nivel de calidad detectado
        """
        if not self.context_detector:
            return QualityLevel.STANDARD  # Nivel por defecto si no hay detector

        context = self.context_detector.detect_context()
        contributors = self.git_repo.get_contributor_count()
        commits = self.git_repo.get_commit_count()
        has_ci = self.git_repo.detect_ci_presence()

        # Mapeo de contexto a nivel de calidad
        if context == "LOCAL":
            return QualityLevel.MINIMAL
        elif context == "HYBRID":
            # En HYBRID, considerar factores adicionales
            if contributors > 2 or commits > 100 or has_ci:
                return QualityLevel.STANDARD
            return QualityLevel.MINIMAL
        else:  # REMOTE
            # En REMOTE, si la cantidad de contribuidores es menor a 3, asignar STANDARD.
            if contributors < 3:
                 return QualityLevel.STANDARD
            # En caso contrario, si (contribuidores >= 3) y (contribuidores > 5 o se detecta CI), asignar ENTERPRISE.
            if (contributors >= 3) and (contributors > 5 or has_ci):
                 return QualityLevel.ENTERPRISE
            return QualityLevel.STANDARD

    def apply_configuration(self, level: Optional[str] = None, commit_format: Optional[str] = None) -> dict:
        """
        Aplica la configuración del nivel y opcionalmente un formato de commit específico.
        Si no se especifica nivel, se detecta automáticamente.

        Args:
            level: Nivel de calidad a aplicar (opcional)
            commit_format: Formato de commit opcional (si no se especifica, se usa el predeterminado)

        Raises:
            ValueError: Si el nivel o formato no son válidos
        """
        # Si no se especifica nivel, detectar automáticamente
        if not level:
            quality_level = self._detect_quality_level()
            print(f"🎯 Nivel de calidad detectado: {quality_level.value}")
        else:
            try:
                quality_level = QualityLevel(level)
            except ValueError:
                raise ValueError(f"Nivel de calidad no válido: {level}. "
                               f"Niveles disponibles: {', '.join(l.value for l in QualityLevel)}")

        # Aplicar configuración de nivel
        level_dir = self.levels_dir / quality_level.value

        # Aplicar workflow y hooks
        for config_type in ['workflow', 'hooks']:
            source = level_dir / f"{config_type}.yaml"
            if not source.exists():
                raise ValueError(f"Configuración {config_type} no encontrada para nivel {level}")

            target = self.active_dir / f"{config_type}.yaml"
            if target.exists():
                target.unlink()
            target.symlink_to(source)

        # Aplicar formato de commit
        available_formats = self.list_available_formats()

        if commit_format:
            if commit_format not in available_formats:
                raise ValueError(f"Formato de commit no válido: {commit_format}. "
                               f"Formatos disponibles: {', '.join(available_formats.keys())}")
            format_path = Path(available_formats[commit_format]['path'])
        else:
            # Usar formato predeterminado del nivel
            format_path = self._get_default_format_for_level(quality_level)

        if not format_path.exists():
            raise ValueError(f"Formato de commit no encontrado: {format_path}")

        # Aplicar el formato de commit
        target = self.active_dir / 'commitlint.config.js'
        if target.exists():
            target.unlink()

        # Determinar el nombre del formato final para inyectar en la configuración
        format_name_to_inject = commit_format if commit_format else format_path.stem.replace('commitlint.config.', '').replace('.js.def', '')

        # Leer el contenido del archivo de formato fuente
        original_content = format_path.read_text(encoding='utf-8')

        # Inyectar la propiedad activeFormat en el objeto module.exports
        # Buscar la línea "module.exports = {"
        module_exports_pattern = r"module\.exports\s*=\s*{"
        match = re.search(module_exports_pattern, original_content)

        if match:
            insertion_point = match.end()
            # Asegurarse de que la inyección sea dentro del objeto y bien formateada
            injected_property = f"\n  activeFormat: '{format_name_to_inject}',"
            content_to_write = original_content[:insertion_point] + injected_property + original_content[insertion_point:]
        else:
            # Fallback si no se encuentra el patrón (no debería pasar si los templates son correctos)
            print(f"\n⚠️  Advertencia: No se pudo inyectar 'activeFormat' en {format_path.name}. Verifique el template.")
            content_to_write = original_content # Escribir el contenido original sin la inyección

        # Copiar el contenido modificado al archivo de destino
        target.write_text(content_to_write, encoding='utf-8')

        # Retornar información sobre la configuración aplicada
        return {
            'level': quality_level.value,
            'commit_format': commit_format or 'predeterminado',
            'format_path': str(format_path),
            'detected': level is None
        }

    def _get_default_format_for_level(self, level: QualityLevel) -> Path:
        """
        Obtiene el formato predeterminado para un nivel.

        Args:
            level: Nivel de calidad

        Returns:
            Path al archivo de formato predeterminado
        """
        # Mapeo de niveles a formatos predeterminados
        default_formats = {
            QualityLevel.MINIMAL: 'minimal',
            QualityLevel.STANDARD: 'simple',
            QualityLevel.ENTERPRISE: 'conventional'
        }
        format_name = default_formats.get(level, 'minimal')
        return self.commit_formats_dir / f'commitlint.config.{format_name}.js.def'

    def get_current_configuration(self) -> dict:
        """
        Obtiene la configuración actual.

        Returns:
            Dict con la configuración actual
        """
        if not self.active_dir.exists():
            return {'status': 'no_config'}

        config = {
            'status': 'active',
            'level': None,
            'commit_format': None
        }

        # Detectar nivel actual
        for level in QualityLevel:
            level_dir = self.levels_dir / level.value
            if (self.active_dir / 'workflow.yaml').samefile(level_dir / 'workflow.yaml'):
                config['level'] = level.value
                break

        # Detectar formato actual leyendo la propiedad 'activeFormat' del archivo JavaScript
        commitlint_config_file = self.active_dir / 'commitlint.config.js'
        if commitlint_config_file.exists():
            try:
                file_content = commitlint_config_file.read_text(encoding='utf-8')

                # Buscar la propiedad activeFormat
                format_pattern = r"activeFormat:\s*'([^']+)'"
                match = re.search(format_pattern, file_content)

                if match:
                    config['commit_format'] = match.group(1)
                else:
                    # Fallback para compatibilidad si la propiedad no existe (versiones antiguas o cambios manuales)
                    current_format_path = commitlint_config_file.resolve()
                    for format_name, format_info in self.list_available_formats().items():
                        if current_format_path.samefile(Path(format_info['path'])) and current_format_path.suffix == '.def': # Solo si es un enlace simbólico a un .def original
                            config['commit_format'] = format_name
                            break
                    if not config['commit_format']:
                        config['commit_format'] = 'unknown' # Si no se puede determinar
            except Exception:
                config['commit_format'] = 'error_reading_file' # Manejo de errores de lectura

        return config

    def _get_file_type(self, file_path: Path) -> Optional[str]:
        """
        Determina el tipo de archivo basado en su extensión y contenido.
        Soporta archivos de plantilla con extensión .def (ej: .py.def, .js.def, etc.)

        Args:
            file_path: Ruta al archivo

        Returns:
            Optional[str]: Tipo de archivo ('python', 'bash', 'javascript', etc.) o None si no se puede determinar
        """
        # Mapeo de extensiones a tipos de archivo
        FILE_TYPES = {
            '.py': 'python',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'bash',  # Tratamos zsh como bash para los headers
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.mjs': 'javascript',
            '.cjs': 'javascript'
        }

        # Obtener la extensión del archivo
        file_ext = file_path.suffix.lower()

        # Si es un archivo .def, obtener la extensión base
        if file_ext == '.def':
            # Obtener la extensión base (ej: .js.def -> .js)
            # Convertir el stem a Path para poder usar suffix
            base_name = Path(file_path.stem)
            base_ext = base_name.suffix.lower()
            if base_ext in FILE_TYPES:
                return FILE_TYPES[base_ext]
        elif file_ext in FILE_TYPES:
            return FILE_TYPES[file_ext]

        # Si no se encontró por extensión, verificar el contenido
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                # Detectar varios tipos de shebang para scripts bash
                if any(first_line.startswith(shebang) for shebang in [
                    '#!/bin/bash',
                    '#!/usr/bin/bash',
                    '#!/usr/bin/env bash',
                    '#!/bin/sh',
                    '#!/usr/bin/sh',
                    '#!/usr/bin/env sh',
                    '#!/bin/zsh',
                    '#!/usr/bin/zsh',
                    '#!/usr/bin/env zsh'
                ]):
                    return 'bash'
        except Exception:
            pass

        return None

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Quality Manager para Git Branch Manager')
    subparsers = parser.add_subparsers(dest='action', help='Acción a realizar')

    # Subparser para list-formats
    subparsers.add_parser('list-formats', help='Lista los formatos de commit disponibles.')

    # Subparser para set-level
    set_level_parser = subparsers.add_parser('set-level', help='Aplica un nivel de calidad (opcional) y un formato de commit (opcional).')
    set_level_parser.add_argument('--level', choices=[l.value for l in QualityLevel], help='Nivel de calidad a aplicar (opcional). Si no se especifica, se respeta la configuración manual o se usa el predeterminado.')
    set_level_parser.add_argument('--format', help='Formato de commit a aplicar (por ejemplo, --format semantic.js)')
    set_level_parser.add_argument('--auto', action='store_true', help='Ignorar la configuración manual y aplicar la detección automática del nivel de calidad')

    # Subparser para show-status
    subparsers.add_parser('show-status', help='Muestra el estado actual de la configuración.')

    # Subparser para run-hook
    run_hook_parser = subparsers.add_parser('run-hook', help='Ejecuta un hook específico según el tipo y la configuración activa.')
    run_hook_parser.add_argument('--hook-type', required=True, help='Tipo de hook a ejecutar (de HookType)')
    run_hook_parser.add_argument('--verbose', action='store_true', help='Mostrar información detallada')
    run_hook_parser.add_argument('files', nargs='*', help='Archivos a validar')

    # Configurar el parser para ignorar argumentos desconocidos
    parser._optionals.title = 'Opciones'
    parser._optionals.description = 'Opciones disponibles'
    parser._optionals.argument_default = argparse.SUPPRESS

    # Parsear argumentos ignorando los desconocidos
    args, unknown = parser.parse_known_args()
    if unknown:
        print(f"⚠️  Argumentos adicionales ignorados: {unknown}", file=sys.stderr)

    manager = QualityManager(Path.cwd())

    if args.action == 'list-formats':
        print("📋 Formatos de Commit Disponibles")
        print("--------------------------------")
        for name, info in manager.list_available_formats().items():
            print(f"{name}: {info['description']}")

    elif args.action == 'set-level':
        if args.auto:
            # Ignorar la configuración manual y detectar automáticamente.
            result = manager.apply_configuration(None, args.format)
            print(f"✅ Configuración aplicada automáticamente: Nivel {result['level']}, Formato: {result['commit_format']}")
        else:
            # Respetar la configuración manual (o usar el predeterminado si no se especifica --level).
            result = manager.apply_configuration(args.level, args.format)
            print(f"✅ Configuración aplicada: Nivel {result['level']}, Formato: {result['commit_format']}")

    elif args.action == 'show-status':
        config = manager.get_current_configuration()
        if config['status'] == 'active':
            print(f"📊 Estado Actual")
            print(f"Nivel: {config['level']}")
            print(f"Formato de commit: {config['commit_format']}")
        else:
            print("❌ No hay configuración activa")

    elif args.action == 'run-hook':
        if not args.hook_type:
            print("❌ Error: Se requiere especificar --hook-type")
            sys.exit(1)
        # Usar los archivos pasados como argumentos
        if hasattr(args, 'files'):
            sys.argv = [sys.argv[0]] + args.files
        success, message = manager.run_hook(args.hook_type)
        if not success or '❌' in message:
            print(message, file=sys.stderr)
            sys.exit(1)
        if '⚠️' in message:
            print(message, file=sys.stderr)
        sys.exit(0)

    else:
        parser.print_usage()
        sys.exit(1)
