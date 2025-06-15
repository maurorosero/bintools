#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (C) <2025> MAURO ROSERO PÉREZ (ROSERO ONE DEVELOPMENT)

Script Name: quality_manager.py
Version:     0.1.0
Description: Gestiona los niveles de calidad y formatos de commit de manera independiente.
Created:     2025-06-14
Modified:    2025-06-14
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
from typing import Dict, Optional, List, Tuple, Any
from enum import Enum
import traceback
import os
import re

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

    def _extract_header_metadata(self, file_path: Path, check_heading_lines: int = 10) -> Tuple[bool, Optional[dict], Optional[str], Optional[str]]:
        """
        Extrae los metadatos del header de un archivo.

        Args:
            file_path: Ruta del archivo
            check_heading_lines: Número de líneas a revisar para el tag Check heading

        Returns:
            Tuple[bool, Optional[dict], Optional[str], Optional[str]]:
                (éxito, metadatos, tipo_archivo, contenido_del_header)
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return False, None, None, None

        lines = content.split('\n')[:check_heading_lines]

        # Mapeo de metadatos y sus variantes (case-insensitive)
        METADATA_VARIANTS = {
            'version': {'version', 'versión', 'release', 'v', '@version', '@release'},
            'description': {'description', 'descripción', 'desc', 'about', '@description', '@desc'},
            'created': {'created', 'created at', 'creation date', 'creation', 'date created', '@created', '@created at'},
            'modified': {'modified', 'modified at', 'updated', 'updated at',
                        'last modified', 'last updated', 'modification date', 'update date',
                        '@modified', '@modified at', '@updated', '@updated at'},
            'author': {'author', 'autor', 'by', 'created by', 'maintainer', 'maintained by',
                      '@author', '@by', '@maintainer'}
        }

        # Mapeo de extensiones base a tipos de archivo
        FILE_TYPES = {
            '.py': 'python',
            '.sh': 'bash',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.mjs': 'javascript',
            '.cjs': 'javascript'
        }

        # Determinar el tipo de archivo inicialmente por extensión
        file_type = None
        file_name = file_path.name.lower()

        # Primero intentar con la extensión completa
        file_ext = file_path.suffix.lower()
        if file_ext in FILE_TYPES:
            file_type = FILE_TYPES[file_ext]
        # Si no se encontró, buscar patrones como *.js.*, *.py.*, etc.
        if not file_type:
            for ext, type_name in FILE_TYPES.items():
                if f"{ext}." in file_name:
                    file_type = type_name
                    break
        # Si aún no se encontró, verificar si es un script bash
        if not file_type and content.startswith('#!/bin/bash'):
            file_type = 'bash'

        # Patrones regex compilados para mejor rendimiento
        check_heading_pattern = re.compile(r'(?i)Check\s*Head(?:er|ing)(?:\s+\.([a-z0-9]+))?')
        metadata_pattern = re.compile(r'^\s*(?:@)?([a-zA-Z0-9-]+)(?:\s*:\s*|\s+)(.+?)\s*$', re.IGNORECASE)

        # Buscar tag Check heading y extraer metadatos
        check_heading_found = False
        excluded_metadata = set()
        metadata = {}
        declared_file_type = None
        header_content = None

        # Procesar según el tipo de archivo
        if file_type == 'python':
            # Procesar archivo Python usando la lógica de docstring
            in_docstring = False
            docstring_lines = []
            first_docstring_processed = False

            for line in lines:
                # Buscar inicio de docstring
                if '"""' in line and not in_docstring and not first_docstring_processed:
                    in_docstring = True
                    docstring_lines = []
                    # Si el docstring termina en la misma línea, procesarlo
                    if line.count('"""') == 2:
                        in_docstring = False
                        first_docstring_processed = True
                        docstring_content = line.split('"""')[1].strip()
                        if docstring_content:
                            docstring_lines.append(docstring_content)
                    continue

                # Buscar fin de docstring
                if in_docstring and '"""' in line:
                    in_docstring = False
                    first_docstring_processed = True
                    # Procesar las líneas del docstring
                    for doc_line in docstring_lines:
                        # Buscar tag Check heading
                        if not check_heading_found:
                            match = check_heading_pattern.search(doc_line)
                            if match:
                                check_heading_found = True
                                declared_file_type = match.group(1)
                                if ':' in doc_line:
                                    _, exceptions = doc_line.split(':', 1)
                                    excluded_metadata = {
                                        exc.strip() for exc in exceptions.split(',')
                                    }
                                continue

                        # Buscar metadatos usando regex
                        match = metadata_pattern.match(doc_line)
                        if match:
                            key, value = match.groups()
                            key = key.lower().strip()
                            value = value.strip()
                            # Verificar si la clave coincide con algún metadato requerido
                            for meta_type, variants in METADATA_VARIANTS.items():
                                if f'no-{meta_type}' in excluded_metadata:
                                    continue
                                if key in variants:
                                    metadata[meta_type] = value
                                    break
                    header_content = '\n'.join(docstring_lines)
                    continue

                # Agregar línea al docstring si estamos dentro de uno
                if in_docstring and not first_docstring_processed:
                    docstring_lines.append(line.strip())

        else:  # bash, javascript, typescript y otros
            # Procesar archivo usando lógica de comentarios
            header_lines = []
            in_jsdoc = False
            comment_start = '#' if file_type == 'bash' else '//'

            # Primero recolectar todas las líneas de comentario hasta encontrar una línea no comentario
            for line in lines:
                # Manejar bloques de comentario JSDoc /** */
                if line.strip().startswith('/**'):
                    in_jsdoc = True
                    continue
                elif line.strip().startswith('*/'):
                    in_jsdoc = False
                    continue
                elif in_jsdoc:
                    clean_line = line.strip()
                    if clean_line.startswith('*'):
                        clean_line = clean_line[1:].strip()
                    if clean_line:  # Solo agregar líneas no vacías
                        header_lines.append(clean_line)
                    continue
                # Manejar comentarios de línea //
                elif line.strip().startswith(comment_start):
                    clean_line = line.lstrip(comment_start).strip()
                    if clean_line:  # Solo agregar líneas no vacías
                        header_lines.append(clean_line)
                    continue
                # Si encontramos una línea que no es comentario y no estamos en un bloque JSDoc, terminar
                elif not in_jsdoc:
                    break

            # Procesar las líneas del header
            for line in header_lines:
                # Buscar tag Check heading
                if not check_heading_found:
                    match = check_heading_pattern.search(line)
                    if match:
                        check_heading_found = True
                        declared_file_type = match.group(1)
                        if ':' in line:
                            _, exceptions = line.split(':', 1)
                            excluded_metadata = {
                                exc.strip() for exc in exceptions.split(',')
                            }
                        continue

                # Si encontramos el tag, procesar todas las líneas como metadatos
                if check_heading_found:
                    # Intentar primero con el patrón de JSDoc (@clave valor)
                    match = metadata_pattern.match(line)
                    if match:
                        key, value = match.groups()
                        key = key.lower().strip()
                        value = value.strip()
                        # Verificar si la clave coincide con algún metadato requerido
                        for meta_type, variants in METADATA_VARIANTS.items():
                            if f'no-{meta_type}' in excluded_metadata:
                                continue
                            # Verificar la clave con y sin @
                            if key in variants or key.lstrip('@') in variants:
                                metadata[meta_type] = value
                                break

            header_content = '\n'.join(header_lines)

            # Si se declaró un tipo de archivo en el Check heading, usarlo
            if declared_file_type and declared_file_type in FILE_TYPES:
                file_type = FILE_TYPES[f'.{declared_file_type}']

        if not check_heading_found or not file_type:
            return False, None, None, None

        return True, metadata, file_type, header_content

    def _run_header_validator(self, config: dict) -> Tuple[bool, str]:
        """
        Ejecuta el hook de validación de headers.

        Args:
            config: Configuración del hook que puede incluir:
                - enabled: bool - Si el hook está habilitado
                - check_heading_lines: int - Número de líneas a revisar para el tag Check heading

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not config.get('enabled', True):
            return True, "✅ Validación de headers deshabilitada"

        # Obtener el número de líneas a revisar, con valor por defecto de 10
        check_heading_lines = config.get('check_heading_lines', 10)
        if not isinstance(check_heading_lines, int) or check_heading_lines < 1:
            return False, f"❌ Configuración inválida: check_heading_lines debe ser un entero positivo, se recibió {check_heading_lines}"

        try:
            # Obtener archivos a validar de los argumentos de línea de comandos
            files = sys.argv[1:] if len(sys.argv) > 1 else []

            if not files:
                return True, "✅ No hay archivos para validar"

            # Usar sets para errores y advertencias para evitar duplicados desde el inicio
            all_errors = set()
            all_warnings = set()
            processed_files = set()
            file_results = {}  # Para almacenar el resultado de cada archivo

            # Determinar metadatos obligatorios según el nivel
            current_level = self.get_current_configuration().get('level', 'minimal')

            if current_level == 'minimal':
                required_metadata = {'version', 'description', 'created'}
                optional_metadata = {'modified', 'author'}
            else:  # standard o enterprise
                required_metadata = {'version', 'description', 'created', 'modified', 'author'}
                optional_metadata = set()

            # Procesar cada archivo
            for file_path in files:
                path = Path(file_path)
                if not path.exists() or str(path) in processed_files:
                    continue

                processed_files.add(str(path))
                file_errors = set()
                file_warnings = set()

                success, metadata, file_type, _ = self._extract_header_metadata(path, check_heading_lines)
                if not success:
                    error_msg = f"❌ {path}: No se encontró Check heading o tipo de archivo no soportado"
                    file_errors.add(error_msg)
                    file_results[str(path)] = {'status': 'error', 'errors': file_errors, 'warnings': file_warnings}
                    continue

                # Validar metadatos obligatorios
                missing_required = required_metadata - set(metadata.keys())
                if missing_required:
                    error_msg = f"❌ {path}: Faltan metadatos obligatorios: {', '.join(missing_required)}"
                    file_errors.add(error_msg)

                # Validar metadatos opcionales
                for meta in optional_metadata:
                    if meta not in metadata:
                        warning_msg = f"⚠️ {path}: Falta metadato opcional: {meta}"
                        file_warnings.add(warning_msg)

                # Actualizar resultados
                if file_errors:
                    all_errors.update(file_errors)
                    file_results[str(path)] = {'status': 'error', 'errors': file_errors, 'warnings': file_warnings}
                elif file_warnings:
                    all_warnings.update(file_warnings)
                    file_results[str(path)] = {'status': 'warning', 'errors': set(), 'warnings': file_warnings}
                else:
                    file_results[str(path)] = {'status': 'success', 'errors': set(), 'warnings': set()}

            # Preparar mensaje final
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

        Args:
            config: Configuración del hook que puede incluir:
                - enabled: bool - Si el hook está habilitado
                - date_format: str - Formato de fecha (default: "YYYY-MM-DD HH:MM:SS")
                - check_heading_lines: int - Número de líneas a revisar para el tag Check heading

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not config.get('enabled', False):
            return True, "✅ Actualización de headers deshabilitada"

        try:
            from datetime import datetime

            # Obtener la configuración
            date_format = config.get('date_format', "YYYY-MM-DD HH:MM:SS")
            check_heading_lines = config.get('check_heading_lines', 10)

            # Obtener la fecha actual
            now = datetime.now()
            current_date = now.strftime(date_format.replace("YYYY", "%Y")
                                              .replace("MM", "%m")
                                              .replace("DD", "%d")
                                              .replace("HH", "%H")
                                              .replace("MM", "%M")
                                              .replace("SS", "%S"))

            # Obtener los archivos modificados en el último commit
            result = subprocess.run(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
                                 capture_output=True, text=True)
            if result.returncode != 0:
                return False, f"❌ Error al obtener archivos modificados: {result.stderr}"

            modified_files = result.stdout.strip().split('\n')
            if not modified_files or modified_files[0] == '':
                return True, "✅ No hay archivos modificados en el último commit"

            updated_files = []
            for file_path in modified_files:
                path = Path(file_path)
                if not path.exists():
                    continue

                # Extraer metadatos usando la lógica común
                success, metadata, file_type, header_content = self._extract_header_metadata(path, check_heading_lines)
                if not success:
                    continue

                try:
                    # Leer el archivo completo
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Actualizar el campo Modified en el header
                    if file_type == 'python':
                        # Para Python, buscar el docstring y actualizar el campo Modified
                        docstring_pattern = re.compile(r'^"""\s*\n(.*?)\n"""', re.DOTALL)
                        docstring_match = docstring_pattern.search(content)
                        if docstring_match:
                            header_lines = docstring_match.group(1).split('\n')
                            new_header_lines = []
                            modified_updated = False
                            for line in header_lines:
                                if re.match(r'^\s*Modified\s*:', line, re.IGNORECASE):
                                    new_header_lines.append(f"Modified:     {current_date}")
                                    modified_updated = True
                                else:
                                    new_header_lines.append(line)
                            if not modified_updated:
                                # Si no existe el campo Modified, agregarlo después de Created
                                for i, line in enumerate(header_lines):
                                    if re.match(r'^\s*Created\s*:', line, re.IGNORECASE):
                                        header_lines.insert(i + 1, f"Modified:     {current_date}")
                                        break
                            new_header = '"""\n' + '\n'.join(new_header_lines) + '\n"""'
                            new_content = content[:docstring_match.start()] + new_header + content[docstring_match.end():]
                    else:
                        # Para otros tipos de archivo, buscar el bloque de comentarios y actualizar el campo Modified
                        comment_pattern = re.compile(r'^(?:\s*#|\s*//|\s*\*|\s*/\*|\s*\*/).*?$', re.MULTILINE)
                        comment_blocks = list(comment_pattern.finditer(content))
                        if comment_blocks:
                            # Encontrar el bloque que contiene el header
                            header_block = None
                            for block in comment_blocks:
                                block_content = block.group(0)
                                if 'Check Heading' in block_content:
                                    header_block = block
                                    break
                            if header_block:
                                header_lines = header_block.group(0).split('\n')
                                new_header_lines = []
                                modified_updated = False
                                for line in header_lines:
                                    if re.match(r'^\s*(?:#|//|\*)\s*Modified\s*:', line, re.IGNORECASE):
                                        comment_char = '#' if file_type == 'bash' else '//'
                                        new_header_lines.append(f"{comment_char} Modified:     {current_date}")
                                        modified_updated = True
                                    else:
                                        new_header_lines.append(line)
                                if not modified_updated:
                                    # Si no existe el campo Modified, agregarlo después de Created
                                    for i, line in enumerate(header_lines):
                                        if re.match(r'^\s*(?:#|//|\*)\s*Created\s*:', line, re.IGNORECASE):
                                            comment_char = '#' if file_type == 'bash' else '//'
                                            header_lines.insert(i + 1, f"{comment_char} Modified:     {current_date}")
                                            break
                                new_header = '\n'.join(new_header_lines)
                                new_content = content[:header_block.start()] + new_header + content[header_block.end():]
                            else:
                                continue
                        else:
                            continue

                    # Escribir el archivo actualizado
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    updated_files.append(file_path)

                except Exception as e:
                    return False, f"❌ Error al actualizar {path}: {str(e)}"

            if updated_files:
                return True, f"✅ Headers actualizados en {len(updated_files)} archivos: {', '.join(updated_files)}"
            return True, "✅ No se encontraron archivos que requieran actualización de headers"

        except Exception as e:
            return False, f"❌ Error en actualización de headers: {str(e)}"

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
