#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quality Manager para el ecosistema Git Branch Manager.
Gestiona los niveles de calidad y formatos de commit de manera independiente.
"""

import yaml
from pathlib import Path
from typing import Dict, Optional
from enum import Enum

class QualityLevel(Enum):
    """Niveles de calidad disponibles."""
    MINIMAL = 'minimal'
    STANDARD = 'standard'
    ENTERPRISE = 'enterprise'

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

    def apply_configuration(self, level: str, commit_format: Optional[str] = None) -> dict:
        """
        Aplica la configuración del nivel y opcionalmente un formato de commit específico.

        Args:
            level: Nivel de calidad a aplicar
            commit_format: Formato de commit opcional (si no se especifica, se usa el predeterminado)

        Raises:
            ValueError: Si el nivel o formato no son válidos
        """
        # Validar nivel
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
        target.symlink_to(format_path)

        # Retornar información sobre la configuración aplicada
        return {
            'level': quality_level.value,
            'commit_format': commit_format or 'predeterminado',
            'format_path': str(format_path)
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

        # Detectar formato actual
        if (self.active_dir / 'commitlint.config.js').exists():
            current_format = (self.active_dir / 'commitlint.config.js').resolve()
            for format_name, format_info in self.list_available_formats().items():
                if current_format.samefile(Path(format_info['path'])):
                    config['commit_format'] = format_name
                    break

        return config

if __name__ == '__main__':
    # Ejemplo de uso
    manager = QualityManager(Path.cwd())

    # Listar formatos disponibles
    print("📋 Formatos de Commit Disponibles")
    print("--------------------------------")
    for name, info in manager.list_available_formats().items():
        print(f"{name}: {info['description']}")

    # Mostrar configuración actual
    print("\n📊 Estado Actual")
    print("---------------")
    config = manager.get_current_configuration()
    if config['status'] == 'active':
        print(f"Nivel: {config['level']}")
        print(f"Formato de commit: {config['commit_format']}")
    else:
        print("No hay configuración activa")
