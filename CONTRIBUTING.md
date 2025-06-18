# Contribuyendo a este Proyecto

## Introducción

¡Gracias por tu interés en contribuir a este proyecto! Este es un repositorio de herramientas y scripts de desarrollo que incluye múltiples tecnologías (Python, JavaScript, Bash) con un enfoque en la calidad de código y la automatización de procesos.

### Filosofía del Proyecto

- **Calidad ante todo**: Priorizamos código limpio, bien documentado y probado
- **Automatización**: Utilizamos hooks y herramientas para mantener estándares consistentes
- **Colaboración**: Fomentamos un ambiente inclusivo y constructivo
- **Mejora continua**: Siempre buscamos optimizar procesos y herramientas

## Configuración del Entorno de Desarrollo

### Prerrequisitos

- **Python 3.12+** (requerido para scripts de Python)
- **Node.js 16+** (requerido para herramientas de JavaScript)
- **Git 2.30+** (requerido para hooks avanzados)
- **Bash 4.0+** (para scripts de shell)

### Instalación

1. **Clona el repositorio**:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Configura el entorno virtual de Python**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Instala dependencias de Node.js**:
   ```bash
   npm install
   ```

4. **Configura pre-commit hooks**:
   ```bash
   pre-commit install --install-hooks
   pre-commit install --hook-type commit-msg
   pre-commit install --hook-type pre-push
   ```

5. **Configura hooks personalizados**:
   ```bash
   # Los hooks personalizados se configuran automáticamente
   # Verifica que estén activos:
   ls -la .git/hooks/
   ```

### Verificación de la Configuración

```bash
# Verifica Python
python --version
pip list

# Verifica Node.js
node --version
npm list

# Verifica pre-commit
pre-commit --version
pre-commit run --all-files

# Verifica hooks personalizados
python .githooks/branch-workflow-validator.py --help
```

## Flujo de Trabajo de Git

### Estrategia de Ramas (GitFlow)

Utilizamos GitFlow como estrategia principal:

- **`main`**: Rama principal de producción
- **`develop`**: Rama de desarrollo e integración
- **`feature/*`**: Ramas para nuevas funcionalidades
- **`hotfix/*`**: Ramas para correcciones urgentes
- **`release/*`**: Ramas para preparar releases

### Convenciones de Nombres de Ramas

```bash
# Funcionalidades
feature/descripcion-corta
feature/TICKET-123-descripcion

# Correcciones
hotfix/bug-critico
hotfix/TICKET-456-fix-security

# Releases
release/v1.2.0
release/2023.10.1
```

### Proceso de Contribución

1. **Crea una rama desde `develop`**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/mi-nueva-funcionalidad
   ```

2. **Desarrolla tu funcionalidad**:
   - Escribe código siguiendo las convenciones
   - Añade pruebas para tu código
   - Actualiza documentación si es necesario

3. **Commit tus cambios**:
   ```bash
   git add .
   git commit -m "feat: añadir nueva funcionalidad"
   ```

4. **Push y crea Pull Request**:
   ```bash
   git push origin feature/mi-nueva-funcionalidad
   # Crea PR desde GitHub/GitLab hacia develop
   ```

### Validación de Ramas

El proyecto incluye validadores automáticos que verifican:
- Nombres de ramas según convenciones
- Flujo de trabajo GitFlow
- Commits válidos en cada rama
- Integración correcta entre ramas

## Mensajes de Commit

### Formato Conventional Commits

Utilizamos el formato de Conventional Commits:

```
<tipo>[ámbito opcional]: <descripción>

[cuerpo opcional]

[pie opcional]
```

### Tipos de Commit

- **feat**: Nueva funcionalidad
- **fix**: Corrección de bug
- **docs**: Cambios en documentación
- **style**: Cambios de formato (espacios, punto y coma, etc.)
- **refactor**: Refactorización de código
- **test**: Añadir o modificar pruebas
- **chore**: Tareas de mantenimiento

### Ejemplos

```bash
# Funcionalidad simple
git commit -m "feat: añadir validador de archivos"

# Corrección con contexto
git commit -m "fix(hooks): corregir validación de ramas en pre-commit"

# Cambio con breaking change
git commit -m "feat!: cambiar formato de configuración

BREAKING CHANGE: El formato de configuración ha cambiado de YAML a JSON"
```

### Validación de Commits

Los commits se validan automáticamente usando:
- **commitlint**: Verifica formato de conventional commits
- **Hook personalizado**: Valida coherencia con el flujo de trabajo

## Sistema de Versionado

### Semantic Versioning (SemVer)

Seguimos Semantic Versioning:
- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Correcciones compatibles

### Proceso de Release

1. **Crear rama de release**:
   ```bash
   git checkout develop
   git checkout -b release/v1.2.0
   ```

2. **Actualizar versión**:
   ```bash
   # Actualizar package.json, __version__.py, etc.
   npm version 1.2.0
   ```

3. **Finalizar release**:
   ```bash
   git checkout main
   git merge release/v1.2.0
   git tag v1.2.0
   git checkout develop
   git merge release/v1.2.0
   ```

4. **Publicar**:
   ```bash
   git push origin main develop --tags
   ```

## Estilo de Código

### Herramientas de Calidad

El proyecto utiliza múltiples herramientas para mantener la calidad:

#### Pre-commit Hooks Activos

- **trailing-whitespace**: Elimina espacios al final de línea
- **end-of-file-fixer**: Asegura nueva línea al final de archivos
- **mixed-line-ending**: Normaliza terminaciones de línea
- **check-executables-have-shebangs**: Verifica shebangs en ejecutables
- **check-added-large-files**: Previene archivos grandes en Git

#### Hooks Personalizados

- **format-all**: Formatea código en todos los lenguajes
- **exec-check-all**: Verifica permisos de ejecución
- **size-check-all**: Verifica tamaño de archivos
- **header-validate**: Valida headers de archivos
- **header-update**: Actualiza headers automáticamente

#### Seguridad

- **detect-secrets**: Detecta secretos en el código
- **safety**: Verifica vulnerabilidades en dependencias Python
- **npm audit**: Verifica vulnerabilidades en dependencias Node.js

### Convenciones por Lenguaje

#### Python
```python
# Usar type hints
def process_data(data: List[str]) -> Dict[str, Any]:
    """Procesa datos de entrada.

    Args:
        data: Lista de strings a procesar

    Returns:
        Diccionario con datos procesados
    """
    return {"processed": data}
```

#### JavaScript
```javascript
// Usar JSDoc para documentación
/**
 * Procesa datos de entrada
 * @param {string[]} data - Array de strings
 * @returns {Object} Datos procesados
 */
function processData(data) {
    return { processed: data };
}
```

#### Bash
```bash
#!/bin/bash
# Usar set -euo pipefail para seguridad
set -euo pipefail

# Documentar funciones
# Procesa datos de entrada
# Argumentos:
#   $1: Archivo de entrada
# Retorna:
#   0: Éxito, 1: Error
process_data() {
    local input_file="$1"
    # Implementación...
}
```

## Pruebas

### Frameworks de Testing

- **Jest**: Para código JavaScript
- **Mocha**: Para pruebas adicionales de JavaScript
- **Python unittest/pytest**: Para scripts Python (configurar según necesidad)
- **Bash testing**: Para scripts de shell

### Ejecutar Pruebas

```bash
# Pruebas JavaScript
npm test
npm run test:coverage

# Pruebas Python (si están configuradas)
python -m pytest tests/
python -m pytest --cov=src tests/

# Validación de scripts Bash
shellcheck scripts/*.sh
```

### Escribir Pruebas

#### JavaScript (Jest)
```javascript
// tests/utils.test.js
describe('Utils', () => {
    test('should process data correctly', () => {
        const result = processData(['a', 'b']);
        expect(result.processed).toEqual(['a', 'b']);
    });
});
```

#### Python (pytest)
```python
# tests/test_utils.py
def test_process_data():
    """Test data processing function."""
    result = process_data(['a', 'b'])
    assert result['processed'] == ['a', 'b']
```

## Documentación

### Estándares de Documentación

- **README.md**: Documentación principal del proyecto
- **docs/**: Documentación detallada en Markdown
- **Código**: Comentarios inline y docstrings
- **API**: Documentación generada automáticamente

### Estructura de Documentación

```
docs/
├── README.md              # Documentación principal
├── installation.md        # Guía de instalación
├── usage.md              # Guía de uso
├── api/                  # Documentación de API
├── examples/             # Ejemplos de uso
└── troubleshooting.md    # Solución de problemas
```

### Convenciones de Documentación

- Usar Markdown para toda la documentación
- Incluir ejemplos de código
- Mantener documentación actualizada con cambios
- Usar enlaces relativos para referencias internas

## Proceso de Contribución

### Reportar Bugs

1. **Busca issues existentes** para evitar duplicados
2. **Usa el template de bug report** si está disponible
3. **Incluye información relevante**:
   - Versión del proyecto
   - Sistema operativo
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Logs o capturas de pantalla

### Solicitar Funcionalidades

1. **Describe el problema** que resuelve la funcionalidad
2. **Propón una solución** con detalles técnicos
3. **Considera alternativas** y sus pros/contras
4. **Discute antes de implementar** funcionalidades grandes

### Proceso de Revisión

#### Criterios de Aceptación

- ✅ Código sigue las convenciones del proyecto
- ✅ Incluye pruebas apropiadas
- ✅ Documentación actualizada
- ✅ Pasa todos los checks automáticos
- ✅ No introduce breaking changes sin justificación
- ✅ Commit messages siguen convenciones

#### Timeline de Revisión

- **Bugs críticos**: 24-48 horas
- **Funcionalidades**: 3-7 días
- **Documentación**: 1-3 días
- **Refactoring**: 5-10 días

### Integración Continua

El proyecto utiliza GitHub Actions para:
- **Lint**: Verificación de estilo de código
- **Critical Validations**: Validaciones críticas
- **Update Metrics**: Actualización de métricas del proyecto

Los workflows se ejecutan automáticamente en:
- Pull requests
- Push a ramas principales
- Releases

## Hooks y Automatización

### Pre-commit Hooks

Los hooks se ejecutan automáticamente antes de cada commit:

```bash
# Ejecutar manualmente todos los hooks
pre-commit run --all-files

# Ejecutar hook específico
pre-commit run trailing-whitespace
pre-commit run detect-secrets
```

### Hooks Personalizados

#### Branch Workflow Validator
```bash
# Validar flujo de trabajo de ramas
python .githooks/branch-workflow-validator.py
```

#### Quality Manager
```bash
# Gestionar calidad de código
python .githooks/quality_manager.py
```

### Configuración de Hooks

Los hooks están configurados en:
- `.pre-commit-config.yaml`: Configuración de pre-commit
- `.githooks/`: Scripts personalizados
- `package.json`: Configuración de husky (si aplica)

## Solución de Problemas

### Problemas Comunes

#### Pre-commit Hooks Fallan
```bash
# Reinstalar hooks
pre-commit uninstall
pre-commit install --install-hooks

# Limpiar cache
pre-commit clean
```

#### Errores de Validación de Ramas
```bash
# Verificar nombre de rama
git branch --show-current

# Cambiar nombre de rama
git branch -m nuevo-nombre-valido
```

#### Problemas con Entorno Virtual
```bash
# Recrear entorno virtual
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Obtener Ayuda

- **Issues**: Crear issue en el repositorio
- **Documentación**: Revisar carpeta `docs/`
- **Logs**: Revisar logs de CI/CD para errores específicos

## Recursos Adicionales

- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitFlow Workflow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)
- [Pre-commit Documentation](https://pre-commit.com/)

---

¡Gracias por contribuir! Tu participación hace que este proyecto sea mejor para toda la comunidad. 🚀
