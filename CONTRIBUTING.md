# Contribuyendo a Utilitarios Personales Monorepo

¡Gracias por tu interés en contribuir y mantener esta colección de utilitarios! Este documento guía el proceso de desarrollo, versionado y release dentro de este monorepo.

## Filosofía del Proyecto

Este es un monorepo que alberga una colección de scripts y utilidades personales, principalmente en Python, Bash y TypeScript/Node.js. Aunque los componentes pueden ser lógicamente independientes, se versionan y gestionan como un todo cohesionado, pero con un sistema de versionado dual:
1.  **Versionado de Archivos Individuales:** Cada script o módulo principal (`.py`, `.sh`, `.js`, `.ts`) dentro del repositorio que contenga una variable `VERSION = "X.Y.Z"` (o formato similar) se versionará individualmente de forma automática.
2.  **Release Unificada del Repositorio:** El repositorio en su conjunto tendrá una versión global (ej. `vA.B.C`) que se gestiona a través de releases en GitHub.

## Código de Conducta

Se espera que todos los participantes sigan el [Código de Conducta](CODE_OF_CONDUCT.md). (Asumido, crear si es necesario).

## Licencia

Al contribuir a este proyecto, aceptas que tus contribuciones se licenciarán bajo la **GNU General Public License v3 (GPLv3)**, como se detalla en el archivo `LICENSE`. Para usos comerciales, se requiere una licencia separada.

## Configuración del Entorno

Asegúrate de tener el entorno base configurado y las herramientas necesarias:
*   **`binsetup.sh`**: Ejecuta `~/bin/binsetup.sh --persistent` para la configuración inicial.
*   **`pre-commit`**: Instálalo (`pip install pre-commit`) y activa los hooks con `pre-commit install --hook-type commit-msg --hook-type pre-commit`. Esto asegurará la validación de mensajes de commit con `commitlint` y otros checks.
*   **`promanager.py`**: Utilidad para la gestión del proyecto y ramas (ver más abajo).
*   **`wfwdevs.py`**: Utilidad para asistir en la creación y gestión de ramas de trabajo.

## Flujo de Trabajo de Git y Ramas

Utilizamos un flujo de Git estructurado para asegurar la estabilidad de `main` y la correcta integración de cambios.

### Ramas Principales:

*   **`main`**: Rama de producción. Contiene el código más estable y desde aquí se generan las releases. Solo recibe fusiones desde `hotfix/*` o desde `develop` (a través de un proceso de promoción, posiblemente involucrando una rama `staging` si se usa). Los pushes directos están desaconsejados y deberían estar protegidos.
*   **`develop`**: Rama de integración principal. Todas las nuevas características (`feature/*`) y correcciones no urgentes (`fix/*`, `docs/*`, etc.) se fusionan aquí primero.
*   **(Opcional) `staging`**: Puede usarse como un paso intermedio entre `develop` y `main` para pruebas de integración finales antes de una release a producción.

### Ramas de Trabajo:

Para cualquier cambio, crea una rama descriptiva a partir de la rama base adecuada. Utiliza `promanager.py` o `wfwdevs.py` para facilitar la creación de estas ramas, o créalas manualmente siguiendo las convenciones:

1.  **`feature/<nombre-feature>`**:
    *   **Propósito**: Nuevas funcionalidades.
    *   **Desde**: `develop`
    *   **Hacia**: `develop` (vía Pull Request)
    *   **Ejemplo**: `git checkout develop; git pull; git checkout -b feature/soporte-multi-idioma`

2.  **`fix/<nombre-fix>`**:
    *   **Propósito**: Correcciones de bugs no urgentes.
    *   **Desde**: `develop`
    *   **Hacia**: `develop` (vía Pull Request)
    *   **Ejemplo**: `git checkout develop; git pull; git checkout -b fix/error-calculo-iva`

3.  **`hotfix/<nombre-hotfix>`**:
    *   **Propósito**: Correcciones críticas en producción.
    *   **Desde**: `main`
    *   **Hacia**: `main` (vía Pull Request) y luego fusionar `main` (o el hotfix directamente) a `develop`.
    *   **Ejemplo**: `git checkout main; git pull; git checkout -b hotfix/vulnerabilidad-pago-urgente`

4.  **`docs/<descripcion-documentacion>`**:
    *   **Propósito**: Cambios exclusivos en documentación (READMEs, guías, etc.).
    *   **Desde**: `develop`
    *   **Hacia**: `develop` (vía Pull Request)
    *   **Ejemplo**: `git checkout develop; git pull; git checkout -b docs/actualizar-api-endpoints`

5.  **`style/<descripcion-estilo>`**, **`refactor/<descripcion-refactor>`**, **`perf/<descripcion-rendimiento>`**, **`test/<descripcion-tests>`**, **`chore/<descripcion-tarea>`**:
    *   **Propósito**: Mejoras de estilo, refactorizaciones, optimizaciones de rendimiento, adición/mejora de tests, o tareas de mantenimiento menores que no son features ni fixes.
    *   **Desde**: `develop`
    *   **Hacia**: `develop` (vía Pull Request)

6.  **`ci/<descripcion-cambio-ci>`**:
    *   **Propósito**: Cambios en la configuración de Integración Continua/Despliegue Continuo (CI/CD), como workflows de GitHub Actions, scripts en `scripts/ci/`, configuración de `pre-commit`, etc.
    *   **Desde**: `main`
    *   **Hacia**: `main` (vía Pull Request)
    *   **Ejemplo**: `git checkout main; git pull; git checkout -b ci/actualizar-version-node-workflow`
    *   **Nota**: Estos cambios buscan mantener la infraestructura de CI/CD de la rama principal actualizada y estable.

### Pull Requests (PRs)

*   Todos los cambios deben integrarse a las ramas principales (`develop`, `main`) a través de Pull Requests.
*   Asegúrate de que tu rama esté actualizada con la rama destino antes de crear el PR (`git pull origin <rama-destino>`).
*   Describe claramente los cambios en el PR. Referencia cualquier Issue de GitHub que resuelva.
*   Los workflows de CI se ejecutarán en el PR. Asegúrate de que todos los checks pasen.
*   Espera la revisión y aprobación antes de fusionar.

## Mensajes de Commit: ¡Formato Estricto Obligatorio!

Utilizamos `commitlint` (configurado vía `pre-commit`) para validar el formato de los mensajes de commit. Es **crucial** para el sistema de versionado automático de archivos y la generación de changelogs para la release unificada.

**Formato:** `[TAG] (#IssueNumber opcional) Descripción corta en presente`

*   **`[TAG]`**: Etiqueta en MAYÚSCULAS que describe el tipo de cambio.
*   **`(#IssueNumber opcional)`**: Referencia a un Issue de GitHub (ej. `(#123)`).
*   **`Descripción corta en presente`**: Imperativo, conciso (ej. "añade X" no "añadido X").

### Tags y su Impacto en el Versionado:

| TAG         | Impacto en `VERSION` del Archivo Modificado (Script `scripts/ci/update_file_versions.py`) | Impacto en Release Unificada (Workflow `.github/workflows/release-on-merge.yml`) |
|-------------|-------------------------------------------------------------------------------|----------------------------------------------------------------|
| `[FEAT]`    | Incrementa **MINOR** (resetea Patch)                                          | Puede llevar a **MINOR** (si PR a `main` no es hotfix/major)   |
| `[FIX]`     | Incrementa **PATCH**                                                          | Puede llevar a **PATCH** (si PR `hotfix/*` a `main`)           |
| `[STYLE]`   | Incrementa **PATCH**                                                          | No influye directamente en el tipo de bump de release          |
| `[REFACTOR]`| Incrementa **MAJOR** (resetea Minor, Patch)                                   | No influye directamente en el tipo de bump de release          |
| `[PERF]`    | Incrementa **MINOR** (resetea Patch)                                          | No influye directamente en el tipo de bump de release          |
| `[RELEASE]` | Incrementa **MAJOR** (generalmente no usado manualmente en archivos)            | Usado por el sistema de release (tag global `vX.Y.Z`)        |
| `[DOCS]`    | Ninguno                                                                       | No influye directamente en el tipo de bump de release          |
| `[TEST]`    | Ninguno                                                                       | No influye directamente en el tipo de bump de release          |
| `[BUILD]`   | Ninguno                                                                       | No influye directamente en el tipo de bump de release          |
| `[CI]`      | Ninguno                                                                       | No influye directamente en el tipo de bump de release          |
| `[CHORE]`   | Ninguno                                                                       | No influye directamente en el tipo de bump de release          |

**Ejemplos de Mensajes de Commit:**
'''
[FEAT] Añade soporte para autenticación OAuth2 en cliente_api.py
[FIX] (#78) Corrige cálculo de descuento en procesador_pedidos.sh
[STYLE] Aplica black a utils/formatters.py
[REFACTOR] Simplifica lógica de manejo de errores en core/scheduler.py
[PERF] Optimiza consulta a base de datos en report_generator.ts
[DOCS] Actualiza sección de instalación en README.md
[TEST] Añade pruebas unitarias para validador_email.py
[CI] Actualiza versión de action de checkout en release-on-merge.yml
[CHORE] Incrementa versión de dependencia 'requests'
'''
**Importante**: El script `scripts/ci/update_file_versions.py` (ejecutado por el workflow `.github/workflows/release-on-merge.yml`) es responsable de actualizar las variables `VERSION` en los archivos basándose en los tags de los commits que los modificaron desde su último tag de versión individual (o desde el inicio si es nuevo). La versión inicial para archivos nuevos con una variable `VERSION` debe ser `0.1.0`.

## Sistema de Versionado y Releases

### 1. Versionado de Archivos Individuales

*   Cuando un PR se fusiona a `main`, el workflow `.github/workflows/release-on-merge.yml` ejecuta `scripts/ci/update_file_versions.py`.
*   Este script analiza los commits aplicados a cada archivo modificado (que contenga una variable `VERSION`) desde la última vez que su versión fue actualizada (o desde su creación).
*   Calcula e implementa el incremento SemVer necesario (Major, Minor, Patch) para la variable `VERSION` de cada archivo afectado, según los tags de commit listados arriba.
*   Los cambios en las versiones de los archivos se commitean automáticamente con un mensaje como `[CI] Auto-update individual file versions [skip ci]`.

### 2. Release Unificada del Repositorio

*   Después de actualizar las versiones de los archivos individuales, el mismo workflow `.github/workflows/release-on-merge.yml` procede a crear una release unificada para todo el repositorio.
*   **Determinación del Tipo de Incremento Global:**
    *   Push directo a `main` (no recomendado, pero cubierto) -> **PATCH**.
    *   PR desde una rama `hotfix/*` fusionado a `main` -> **PATCH**.
    *   PR fusionado a `main` con la etiqueta `release-major` -> **MAJOR**.
    *   Cualquier otro PR fusionado a `main` (típicamente desde `develop` o `staging`) -> **MINOR**.
*   **Proceso de Release:**
    1.  El script `scripts/ci/calculate_next_version.py` calcula la nueva versión global (ej. `v1.2.3`) basándose en el último tag de release global y el tipo de incremento determinado.
    2.  Se crea un tag Git (ej. `v1.2.3`).
    3.  Se empujan los commits (incluyendo el de las versiones individuales actualizadas) y el nuevo tag a `main`.
    4.  Se crea una Release formal en GitHub, generando automáticamente las notas del changelog a partir de los mensajes de commit desde la última release.

## Documentación de Componentes

*   Si modificas un componente existente o añades uno nuevo que tenga una interfaz de usuario o configuración significativa, actualiza o crea su `README.md` correspondiente en el directorio `docs/` (ej. `docs/nombre_componente.md`).
*   Para la documentación de la API de funciones o clases, utiliza docstrings siguiendo las convenciones del lenguaje (ej. Google Style para Python).

## Estilo de Código y Linters

*   Sigue el estilo de código existente en el proyecto.
*   Utilizamos `pre-commit` para ejecutar linters y formateadores automáticamente (ej. `flake8`, `black` para Python; `shellcheck` para Bash; `eslint`/`prettier` para JS/TS).
*   Asegúrate de que tu código pase estos checks antes de hacer commit o al menos antes de crear un PR.

## Pruebas (Testing)

*   Fomentamos la inclusión de pruebas para nuevas funcionalidades y correcciones de bugs.
*   Esto ayuda a mantener la calidad, prevenir regresiones y documentar el comportamiento esperado.
*   Añade pruebas unitarias, de integración o funcionales según sea apropiado para tus cambios.

---
¡Gracias por tu dedicación a mantener este proyecto organizado y robusto! 