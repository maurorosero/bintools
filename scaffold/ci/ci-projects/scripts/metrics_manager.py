#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestor de Métricas y Badges
===========================

Este módulo gestiona la generación y actualización de métricas y badges
de forma adaptativa según el contexto y nivel del proyecto.
"""

import os
import json
import yaml
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Añadir .githooks al path para poder importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent / '.githooks'))
from quality_manager import QualityManager, QualityLevel
from branch_workflow_validator import ContextDetector

class MetricType(Enum):
    """Tipos de métricas soportadas."""
    BUILD = "build"
    TEST = "test"
    COVERAGE = "coverage"
    QUALITY = "quality"
    SECURITY = "security"
    DEPENDENCIES = "dependencies"
    COMPLEXITY = "complexity"

@dataclass
class MetricConfig:
    """Configuración de una métrica."""
    type: MetricType
    enabled: bool = True
    threshold: Optional[float] = None
    badge_template: Optional[str] = None
    report_template: Optional[str] = None
    level: QualityLevel = QualityLevel.STANDARD
    command: Optional[str] = None
    extract: Optional[str] = None

class MetricsManager:
    """Gestiona métricas y badges de forma adaptativa."""

    def __init__(self, quality_manager: QualityManager):
        """Inicializa el gestor de métricas."""
        self.quality_manager = quality_manager
        self.context_detector = quality_manager.context_detector
        self.metrics_dir = Path(".metrics")
        self.badges_dir = Path(".badges")
        self._ensure_dirs()
        self._load_config()

    def _ensure_dirs(self) -> None:
        """Asegura que existan los directorios necesarios."""
        self.metrics_dir.mkdir(exist_ok=True)
        self.badges_dir.mkdir(exist_ok=True)

    def _load_config(self) -> None:
        """Carga la configuración de métricas."""
        config_path = Path("ci/config/metric-definitions.yml")
        if not config_path.exists():
            self._create_default_config(config_path)

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def _create_default_config(self, config_path: Path) -> None:
        """Crea configuración por defecto de métricas."""
        # Asegurar que el directorio existe
        config_path.parent.mkdir(parents=True, exist_ok=True)

        default_config = {
            "metrics": {
                "build": {
                    "enabled": True,
                    "level": "MINIMAL",
                    "badge_template": "https://img.shields.io/badge/build-{status}-{color}",
                    "threshold": None,
                    "command": "echo 'Build passing'",
                    "extract": "status=passing"
                },
                "test": {
                    "enabled": True,
                    "level": "STANDARD",
                    "badge_template": "https://img.shields.io/badge/tests-{passed}/{total}-{color}",
                    "threshold": 80.0,
                    "command": "pytest --cov=./ --cov-report=term-missing",
                    "extract": """
                        COVERAGE=$(grep -o 'TOTAL.*[0-9]*%' test_report.txt | grep -o '[0-9]*%' | tr -d '%')
                        TESTS_PASSED=$(grep -o '[0-9]* passed' test_report.txt | grep -o '[0-9]*')
                        TESTS_TOTAL=$(grep -o '[0-9]* collected' test_report.txt | grep -o '[0-9]*')
                        echo "$COVERAGE"
                        echo "passed=$TESTS_PASSED" >&2
                        echo "total=$TESTS_TOTAL" >&2
                    """
                },
                "coverage": {
                    "enabled": True,
                    "level": "STANDARD",
                    "badge_template": "https://img.shields.io/badge/coverage-{percentage}%25-{color}",
                    "threshold": 80.0,
                    "command": "pytest --cov=./ --cov-report=term-missing",
                    "extract": "grep -o 'TOTAL.*[0-9]*%' | grep -o '[0-9]*%' | tr -d '%'"
                },
                "quality": {
                    "enabled": True,
                    "level": "STANDARD",
                    "badge_template": "https://img.shields.io/badge/quality-{grade}-{color}",
                    "threshold": 8.0,
                    "command": "flake8 . && pylint .",
                    "extract": "grep -o 'Your code has been rated at [0-9]*\\.[0-9]*' | grep -o '[0-9]*\\.[0-9]*'"
                },
                "security": {
                    "enabled": True,
                    "level": "ENTERPRISE",
                    "badge_template": "https://img.shields.io/badge/security-{status}-{color}",
                    "threshold": 0.0,
                    "command": "safety check && bandit -r .",
                    "extract": """
                        VULNS=$(grep -o 'Vulnerabilities found: [0-9]*' | grep -o '[0-9]*')
                        echo "$VULNS"
                        echo "status=$(if [ $VULNS -eq 0 ]; then echo 'secure'; else echo 'vulnerable'; fi)" >&2
                    """
                },
                "complexity": {
                    "enabled": True,
                    "level": "ENTERPRISE",
                    "badge_template": "https://img.shields.io/badge/complexity-{score}-{color}",
                    "threshold": 10.0,
                    "command": "radon cc . -a -nc",
                    "extract": "grep -o 'Average complexity: [0-9]*\\.[0-9]*' | grep -o '[0-9]*\\.[0-9]*'"
                }
            }
        }

        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)

    def get_active_metrics(self) -> List[MetricConfig]:
        """Obtiene las métricas activas según el nivel actual."""
        current_level = self.quality_manager.current_level
        active_metrics = []

        for metric_type, config in self.config["metrics"].items():
            metric_level = QualityLevel[config["level"]]
            if metric_level.value <= current_level.value:
                active_metrics.append(MetricConfig(
                    type=MetricType(metric_type),
                    enabled=config["enabled"],
                    threshold=config.get("threshold"),
                    badge_template=config.get("badge_template"),
                    report_template=config.get("report_template"),
                    level=metric_level,
                    command=config.get("command"),
                    extract=config.get("extract")
                ))

        return active_metrics

    def run_all_metrics(self) -> None:
        """Ejecuta todas las métricas activas según el nivel actual."""
        for metric in self.get_active_metrics():
            if not metric.enabled or not metric.command:
                continue

            try:
                # Ejecutar comando
                result = subprocess.run(
                    metric.command,
                    shell=True,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    print(f"⚠️  Error ejecutando {metric.type.value}: {result.stderr}")
                    continue

                # Extraer métricas si hay script
                if metric.extract:
                    extract_env = os.environ.copy()
                    extract_env['METRIC_OUTPUT'] = result.stdout

                    extract_result = subprocess.run(
                        metric.extract,
                        shell=True,
                        capture_output=True,
                        text=True,
                        env=extract_env
                    )

                    if extract_result.returncode != 0:
                        print(f"⚠️  Error extrayendo métricas de {metric.type.value}: {extract_result.stderr}")
                        continue

                    # Procesar salida
                    value = float(extract_result.stdout.strip())
                    status = None

                    # Extraer status de stderr si existe
                    for line in extract_result.stderr.splitlines():
                        if '=' in line:
                            key, val = line.split('=', 1)
                            if key == 'status':
                                status = val
                            elif key in ['passed', 'total']:
                                if not hasattr(metric, 'extra_data'):
                                    metric.extra_data = {}
                                metric.extra_data[key] = val

                    # Actualizar métrica
                    self.update_metric(
                        metric.type,
                        value,
                        status=status,
                        **getattr(metric, 'extra_data', {})
                    )

            except Exception as e:
                print(f"⚠️  Error procesando {metric.type.value}: {str(e)}")

    def update_metric(self, metric_type: MetricType, value: float,
                     status: str = None, color: str = None, **extra_data) -> None:
        """Actualiza una métrica y genera su badge."""
        metric_config = next(
            (m for m in self.get_active_metrics() if m.type == metric_type),
            None
        )

        if not metric_config or not metric_config.enabled:
            return

        # Guardar métrica
        metric_data = {
            "value": value,
            "status": status,
            "color": color or self._get_color(value, metric_config.threshold),
            "timestamp": self._get_timestamp(),
            **extra_data
        }

        metric_file = self.metrics_dir / f"{metric_type.value}.json"
        with open(metric_file, 'w') as f:
            json.dump(metric_data, f, indent=2)

        # Generar badge si hay template
        if metric_config.badge_template:
            self._generate_badge(metric_type, metric_data, metric_config)

    def _get_color(self, value: float, threshold: Optional[float]) -> str:
        """Determina el color del badge basado en el valor y umbral."""
        if threshold is None:
            return "blue"
        if value >= threshold:
            return "green"
        if value >= threshold * 0.8:
            return "yellow"
        return "red"

    def _get_timestamp(self) -> str:
        """Obtiene timestamp actual en formato ISO."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def _generate_badge(self, metric_type: MetricType,
                       data: Dict, config: MetricConfig) -> None:
        """Genera el badge para una métrica."""
        if not config.badge_template:
            return

        # Formatear badge URL
        badge_url = config.badge_template.format(
            status=data.get("status", str(data["value"])),
            color=data["color"],
            percentage=int(data["value"]) if isinstance(data["value"], float) else data["value"],
            passed=data.get("passed", 0),
            total=data.get("total", 0),
            grade=data.get("grade", "unknown"),
            score=data.get("score", "unknown")
        )

        # Guardar badge
        badge_file = self.badges_dir / f"{metric_type.value}.svg"
        import requests
        response = requests.get(badge_url)
        if response.status_code == 200:
            with open(badge_file, 'wb') as f:
                f.write(response.content)

    def update_readme_badges(self) -> None:
        """Actualiza la sección de badges en el README."""
        badges = self.generate_readme_badges()

        # Actualizar README.md
        with open('README.md', 'r') as f:
            content = f.read()

        # Buscar sección de badges
        import re
        badge_section = re.search(r'<!-- BADGES_START -->(.*?)<!-- BADGES_END -->',
                                content, re.DOTALL)

        if badge_section:
            # Reemplazar sección existente
            new_content = content[:badge_section.start()] + \
                         '<!-- BADGES_START -->\n' + badges + '\n<!-- BADGES_END -->' + \
                         content[badge_section.end():]
        else:
            # Añadir nueva sección después del título
            new_content = re.sub(r'(# .*?\n)',
                               r'\1\n<!-- BADGES_START -->\n' + badges + '\n<!-- BADGES_END -->\n\n',
                               content)

        with open('README.md', 'w') as f:
            f.write(new_content)

    def generate_readme_badges(self) -> str:
        """Genera la sección de badges para el README."""
        badges = []
        for metric in self.get_active_metrics():
            if not metric.enabled:
                continue

            badge_file = self.badges_dir / f"{metric.type.value}.svg"
            if badge_file.exists():
                badge_url = f"![{metric.type.value}](.badges/{metric.type.value}.svg)"
                badges.append(badge_url)

        return "\n".join(badges)

    def get_metrics_report(self) -> Dict:
        """Genera reporte de métricas actuales."""
        report = {}
        for metric in self.get_active_metrics():
            if not metric.enabled:
                continue

            metric_file = self.metrics_dir / f"{metric.type.value}.json"
            if metric_file.exists():
                with open(metric_file) as f:
                    report[metric.type.value] = json.load(f)

        return report
