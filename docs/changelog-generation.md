# Generación de CHANGELOG con docgen.py

Esta funcionalidad permite generar CHANGELOGs profesionales y elaborados usando tu herramienta `docgen.py` existente, siguiendo el estándar **Keep a Changelog**.

## 🎯 **Características**

- ✅ **Análisis automático del historial de Git**
- ✅ **Categorización inteligente de commits**
- ✅ **Detección de breaking changes, deprecaciones y seguridad**
- ✅ **Formato Keep a Changelog estándar**
- ✅ **Generación con o sin IA**
- ✅ **Integración con tu sistema de commits existente**
- ✅ **Emojis y formato profesional**

## 🚀 **Uso Básico**

### **Generar CHANGELOG sin IA (Recomendado)**
```bash
# Generar CHANGELOG básico
python docgen.py --doc-type changelog --output CHANGELOG.md

# Con contexto específico
python docgen.py --doc-type changelog --output CHANGELOG.md --context "release-v1.2.0"

# Con instrucciones personalizadas
python docgen.py --doc-type changelog --output CHANGELOG.md --custom-instructions "Incluir solo cambios desde v1.1.0"
```

### **Generar CHANGELOG con IA (Opcional)**
```bash
# Generar CHANGELOG mejorado con IA
python docgen.py --doc-type changelog --output CHANGELOG.md --use-ai
```

## 📋 **Formato de Commits Soportado**

Tu sistema actual de commits ya es compatible:

```bash
# Formato estándar
[FEAT] (#123) Añade nueva funcionalidad de autenticación
[FIX] (#124) Corrige error en validación de formularios
[REFACTOR] Optimiza consultas a base de datos
[STYLE] Aplica black a utils/formatters.py
[PERF] Mejora rendimiento de procesamiento
[DOCS] Actualiza documentación de API
[TEST] Añade pruebas unitarias
[BUILD] Actualiza dependencias
[CI] Configura GitHub Actions
[CHORE] Limpia código obsoleto
```

## 🏗️ **Categorización Automática**

El sistema categoriza automáticamente según Keep a Changelog:

| Tag | Categoría | Descripción |
|-----|-----------|-------------|
| `[FEAT]` | **Added** | Nuevas características |
| `[FIX]` | **Fixed** | Correcciones de bugs |
| `[REFACTOR]`, `[PERF]`, `[STYLE]`, `[DOCS]`, `[TEST]`, `[BUILD]`, `[CI]`, `[CHORE]` | **Changed** | Cambios en funcionalidad existente |
| `[BREAKING]` | **Breaking Changes** | Cambios que rompen compatibilidad |

### **Detección Inteligente**

El sistema detecta automáticamente:

- **Deprecaciones**: Palabras como "deprecate", "obsolete", "legacy"
- **Seguridad**: Palabras como "security", "vulnerability", "auth"
- **Breaking Changes**: Palabras como "breaking", "remove", "delete"

## 📁 **Estructura de Archivos**

```
docs/config/
├── analysis/
│   └── changelog.yaml          # Configuración de análisis
├── prompts/
│   └── system/
│       └── changelog.yaml      # Prompt del sistema
├── toc/
│   └── base/
│       └── changelog.yaml      # Estructura TOC
└── model.yaml                  # Configuración de modelo (actualizada)
```

## 🔧 **Configuración**

### **Configuración de Análisis (`changelog.yaml`)**

```yaml
changelog_analysis:
  tools:
    - git_history
    - commit_parser
    - version_analyzer
    - change_categorizer

  change_detection:
    commit_patterns:
      - pattern: "^\\[([A-Z]+)\\](?: \\(#(\\d+)\\))? (.+)$"
        groups: ["type", "issue", "description"]

    impact_analysis:
      breaking_changes:
        - keywords: ["breaking", "deprecate", "remove"]
      security_changes:
        - keywords: ["security", "vulnerability", "auth"]
```

### **Configuración de Modelo (`model.yaml`)**

```yaml
document_types:
  changelog:
    model: "claude-4-sonnet-20250514"
    max_tokens: 6000
    temperature: 0.8
```

## 📊 **Ejemplo de Salida**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 🎉 Nueva API para gestión de usuarios
- 📊 Dashboard de estadísticas mejorado

### Changed
- ⚡ Optimización del rendimiento de consultas
- 🔧 Refactorización del sistema de autenticación

### Fixed
- 🐛 Corrección de error en validación de formularios
- 🔒 Parche de seguridad para vulnerabilidad XSS

### Breaking Changes
- ❌ Eliminada función `deprecated_function()`
- ⚠️ Cambio en la estructura de respuesta de API

## [1.2.0] - 2024-01-15

### Added
- 🎉 Implementación de autenticación OAuth2
- 📊 Sistema de métricas en tiempo real

### Fixed
- 🐛 Corrección de bug crítico en validación
- 🔒 Actualización de dependencias de seguridad
```

## 🧪 **Pruebas**

Ejecuta el script de pruebas para verificar la funcionalidad:

```bash
python test_changelog.py
```

Esto generará:
- `test_changelog.md` - CHANGELOG usando ChangelogAnalyzer
- `test_changelog_generator.md` - CHANGELOG usando DocumentationGenerator

## 🔄 **Integración con CI/CD**

### **Generación Automática en Releases**

```yaml
# .github/workflows/release.yml
- name: Generate Changelog
  run: |
    python docgen.py --doc-type changelog --output CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "[CI] Auto-update changelog"
```

### **Pre-commit Hook**

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: update-changelog
      name: Update Changelog
      entry: python docgen.py --doc-type changelog --output CHANGELOG.md
      language: system
      files: ^CHANGELOG\.md$
```

## 🎛️ **Opciones Avanzadas**

### **Análisis desde un Tag Específico**

```python
# En código Python
analyzer = ChangelogAnalyzer(Path.cwd())
analysis = analyzer.analyze_git_history(since_tag="v1.1.0")
```

### **Personalización de Categorías**

```python
# Modificar mapeo de categorías
analyzer.CATEGORY_MAP = {
    'FEAT': 'Added',
    'FIX': 'Fixed',
    'REFACTOR': 'Changed',
    # ... más categorías
}
```

### **Configuración de Emojis**

```python
# Personalizar emojis
analyzer.CATEGORY_EMOJIS = {
    'Added': '🚀',
    'Changed': '⚡',
    'Fixed': '🐛',
    # ... más emojis
}
```

## 🚨 **Troubleshooting**

### **Problemas Comunes**

1. **"No se encontraron commits"**
   - Verifica que estés en un repositorio Git
   - Asegúrate de que haya commits en el historial

2. **"Error ejecutando git log"**
   - Verifica permisos de Git
   - Asegúrate de que Git esté instalado

3. **"Error usando IA"**
   - Verifica configuración de tokens de Anthropic
   - El sistema fallback a generación sin IA

### **Comandos de Diagnóstico**

```bash
# Verificar commits disponibles
git log --oneline

# Verificar formato de commits
git log --oneline | head -10

# Verificar tags
git tag --sort=-version:refname
```

## 🔮 **Futuras Mejoras**

- [ ] **Integración con issues**: Enlaces automáticos a GitHub/GitLab issues
- [ ] **Análisis de impacto**: Métricas de impacto de cambios
- [ ] **Comparación entre versiones**: Diferencias entre releases
- [ ] **Templates personalizables**: Diferentes formatos de CHANGELOG
- [ ] **Integración con Jira**: Soporte para sistemas de tickets empresariales

## 📞 **Soporte**

Para problemas o sugerencias:
1. Revisa la sección de troubleshooting
2. Ejecuta `python test_changelog.py` para diagnóstico
3. Verifica la configuración en `docs/config/`

---

**¡Tu herramienta `docgen.py` ahora puede generar CHANGELOGs profesionales sin esfuerzo!** 🎉
