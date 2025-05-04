# Guía del Flujo de Trabajo Git

Este documento describe el flujo de trabajo de Git utilizado en este repositorio, asistido por el script `bin/wf-git.py`. El modelo se basa en Gitflow con la adición de una rama `staging` **opcional**, permitiendo flexibilidad según las necesidades de la release.

## Ramas Principales (Persistentes)

Estas ramas existen permanentemente en el repositorio:

*   ### `main`
    *   **Propósito:** Refleja el código estable y en producción. Es la fuente de las releases oficiales.
    *   **Reglas:**
        *   **NUNCA** hacer commit directamente en `main`.
        *   Solo recibe merges desde `staging` (Opción A de Release), `develop` (Opción B de Release), o `hotfix/*` (para correcciones urgentes).
        *   Cada commit en `main` debe corresponder a una versión de release y estar tageado (ej. `v1.2.3`).

*   ### `develop`
    *   **Propósito:** Rama principal de desarrollo e integración. Contiene las últimas funcionalidades completadas y consideradas estables (pero no necesariamente listas para producción).
    *   **Reglas:**
        *   Sirve como base para crear nuevas ramas `feature/*`, `fix/*`, y `chore/*`.
        *   Recibe merges desde las ramas de tarea completadas (vía Pull Requests).
        *   Recibe merges desde `main` después de cada release o hotfix para incorporar los cambios de producción de vuelta al desarrollo.
        *   **Puede ser directamente probada en un entorno de Staging y fusionada a `main` si se elige la Opción B del flujo de release (requiere CI/pruebas robustas).**

*   ### `staging` (Opcional)
    *   **Propósito:** (Opcional) Rama para estabilizar una versión candidata y realizar pruebas formales (UAT, regresión) sobre un conjunto de características congelado antes de ir a `main`. Útil para ciclos de prueba largos, integración compleja, o cuando `develop` es muy activa.
    *   **Reglas (Si se usa - Ver Flujo Release Opción A):**
        *   Se crea/resetea a partir de `develop` cuando se decide preparar una release (`wf-git release prepare`).
        *   Las pruebas de aceptación (UAT), regresión y rendimiento se realizan sobre esta rama.
        *   Una vez aprobada, se fusiona en `main` (normalmente mediante un Pull Request de `staging` a `main`) para iniciar la release.

## Ramas de Soporte (Temporales)

Estas ramas se crean para tareas específicas y se eliminan una vez completadas y fusionadas.

*   ### `feature/*`
    *   **Creada desde:** `develop`
    *   **Fusionada en:** `develop` (vía PR)
    *   **Propósito:** Desarrollar nuevas funcionalidades.
    *   **Nombrado:** `feature/nombre-corto-descriptivo` (ej. `feature/user-authentication`)
    *   **Comando:** `wf-git start feature <descripcion>`

*   ### `fix/*`
    *   **Creada desde:** `develop`
    *   **Fusionada en:** `develop` (vía PR)
    *   **Propósito:** Corregir bugs no críticos detectados en `develop`.
    *   **Nombrado:** `fix/[issue#-]nombre-corto-descriptivo` (ej. `fix/45-division-by-zero`, `fix/login-button-alignment`)
    *   **Comando:** `wf-git start fix <descripcion>` o `wf-git start fix <issue_num> <descripcion>`

*   ### `chore/*`
    *   **Creada desde:** `develop`
    *   **Fusionada en:** `develop` (vía PR)
    *   **Propósito:** Tareas que no son features ni fixes (refactors, actualizaciones, limpieza).
    *   **Nombrado:** `chore/nombre-corto-descriptivo` (ej. `chore/update-dependencies`)
    *   **Comando:** `wf-git start chore <descripcion>`

*   ### `hotfix/*`
    *   **Creada desde:** `main`
    *   **Fusionada en:** `main` **Y** `develop` (vía PR a `main`, luego merge automático de `main` a `develop`)
    *   **Propósito:** Corregir bugs críticos detectados en producción (`main`). Requiere acción inmediata.
    *   **Nombrado:** `hotfix/nombre-corto-descriptivo` (ej. `hotfix/security-vulnerability-patch`)
    *   **Comando:** `wf-git hotfix start <descripcion>`

## Flujos Comunes (Asistidos por `wf-git.py`)

El script `bin/wf-git.py` ayuda a automatizar partes clave de estos flujos, **principalmente el flujo de release con `staging` (Opción A)**. El flujo sin `staging` (Opción B) requiere más pasos manuales o adaptaciones futuras del script.

### Flujo 1: Inicialización del Repositorio

*   **Comando:** `wf-git init-repo <url_remoto>`
*   **Acciones:**
    1.  Inicializa Git (`git init`).
    2.  Crea `README.md` y `.gitignore` básicos.
    3.  Hace el commit inicial en `main`.
    4.  Crea las ramas `develop` (desde `main`) y `staging` (desde `develop`).
    5.  Añade el repositorio remoto.
    6.  Hace push inicial de `main`, `develop`, y `staging`.

### Flujo 2: Desarrollo de Tareas (Features, Fixes, Chores)

1.  **Iniciar Tarea:** `wf-git start <tipo> [issue#] <descripcion>`
    *   Cambia a `develop`, actualiza (`pull`).
    *   Crea la rama de tarea (ej. `feature/mi-tarea`).
2.  **Desarrollar:**
    *   Realiza los cambios necesarios en la rama de tarea.
    *   Haz commits siguiendo el formato requerido (Ver sección "Mensajes de Commit"). Puedes usar `wf-git commit` para ayuda interactiva.
    *   **Mejor Práctica:** Asegúrate de incluir pruebas automatizadas para tus cambios.
3.  **Empujar Cambios:** `wf-git push`
    *   Empuja la rama de tarea al remoto (configura upstream si es necesario).
4.  **Pull Request (PR):**
    *   Ve a la interfaz web (GitHub, GitLab, etc.).
    *   Crea un Pull Request desde tu rama de tarea hacia `develop`.
    *   **Mejor Práctica:** Asegúrate de que todos los checks de CI (linting, pruebas) pasan en el PR.
    *   Espera la revisión, aprobación y fusión.
5.  **Finalizar Tarea (Limpieza):** `wf-git finish`
    *   **Importante:** Ejecutar *después* de que el PR haya sido fusionado en `develop`.
    *   Cambia a `develop`, actualiza (`pull`).
    *   Borra la rama de tarea local.
    *   Pregunta si borrar también la rama remota.

### Flujo 3: Proceso de Release (Dos Opciones)

Existen dos maneras de realizar una release, dependiendo de la necesidad de un ciclo de pruebas formal sobre una versión candidata congelada.

#### Opción A: Con Rama `staging` (Ciclo Formal / Flujo por Defecto en `wf-git.py`)

**Cuándo usar:** Necesitas un ciclo de UAT formal, pruebas de regresión extensivas sobre una versión candidata estable, o si `develop` cambia muy rápidamente.

1.  **Preparar Release:** `wf-git release prepare`
    *   Cambia a `develop`, actualiza (`pull`).
    *   Crea/resetea `staging` para que coincida con `develop`.
    *   Hace push forzado de `staging` al remoto.
    *   **Paso Manual:** Realizar pruebas exhaustivas sobre la rama/entorno de `staging`.
2.  **Fusionar a Main (Manual):**
    *   **Importante:** Este paso **NO** lo hace el script `wf-git.py`.
    *   Una vez `staging` está aprobado, crear un Pull Request desde `staging` hacia `main`.
    *   Revisar y fusionar este PR en `main`.
3.  **Ejecutar Release:** `wf-git release perform <version>` (ej. `v1.2.0`)
    *   **Importante:** Ejecutar *después* de fusionar `staging` en `main`.
    *   Verifica que estás seguro de que `staging` fue probada y fusionada en `main`.
    *   Cambia a `main`, actualiza (`pull`).
    *   Crea el tag Git con la versión especificada (activará `release.yml`).
    *   Hace push de `main` y del nuevo tag.
    *   Intenta fusionar `main` de vuelta en `develop` (maneja conflictos si ocurren) y hace push de `develop`.

#### Opción B: Sin Rama `staging` (Ciclo Ágil)

**Cuándo usar:** Tienes alta confianza en la estabilidad de `develop` (gracias a pruebas CI robustas), puedes probar `develop` directamente en un *entorno* de staging, y prefieres un flujo más rápido.

**Prerrequisitos:**
    *   **CI sólida:** Pruebas automatizadas (unitarias, integración, etc.) que se ejecutan y deben pasar en cada PR a `develop`.
    *   **Disciplina:** Revisiones de código rigurosas y disciplina al fusionar a `develop`.
    *   **Entorno de Staging:** Capacidad de desplegar y probar la rama `develop` fácilmente en un entorno similar a producción.

**Pasos (Mayormente Manuales):**

1.  **Asegurar Estabilidad y Pruebas:**
    *   Verifica que `develop` contiene todas las features/fixes para la release y está estable (CI en verde).
    *   Despliega `develop` a un **entorno** de staging/pre-producción.
    *   Realiza las pruebas necesarias (UAT, etc.) en ese entorno.
2.  **Fusionar a Main (Manual):**
    *   Una vez `develop` (probada en el entorno de staging) está aprobada para release, crea un Pull Request desde `develop` hacia `main`.
    *   Revisar y fusionar este PR en `main`.
3.  **Tagear y Sincronizar (Manual):**
    *   Cambia a `main`, actualiza (`pull`).
    *   Crea el tag Git manually: `git tag vX.Y.Z` (esto activará `release.yml`).
    *   Haz push de `main` y del tag: `git push origin main --tags`.
    *   Cambia a `develop`, actualiza (`pull`).
    *   Fusiona `main` de vuelta en `develop`: `git merge --no-ff main`. Resuelve conflictos si los hay.
    *   Haz push de `develop`: `git push origin develop`.
    *   *(Nota: `wf-git.py` actualmente no soporta directamente este flujo de release. Los pasos de tageo y sincronización son manuales).*

### Flujo 4: Proceso de Hotfix

1.  **Iniciar Hotfix:** `wf-git hotfix start <descripcion>`
    *   Cambia a `main`, actualiza (`pull`).
    *   Crea la rama `hotfix/descripcion-corta`.
2.  **Desarrollar Fix Urgente:**
    *   Realiza los cambios mínimos necesarios en la rama `hotfix/*`.
    *   Haz commit(s) con el tag `[FIX]`.
3.  **Pull Request a Main (Manual):**
    *   Crea un Pull Request desde tu rama `hotfix/*` hacia `main`.
    *   Revisar y fusionar **urgentemente** este PR en `main`.
4.  **Finalizar Hotfix:** `wf-git hotfix finish <version>` (ej. `v1.2.1`)
    *   **Importante:** Ejecutar *después* de fusionar el hotfix en `main`.
    *   Verifica que estás seguro de que el PR fue fusionado en `main`.
    *   Cambia a `main`, actualiza (`pull`).
    *   Crea el tag Git con la versión del hotfix (activará `release.yml`).
    *   Hace push de `main` y del nuevo tag.
    *   Intenta fusionar `main` de vuelta en `develop` (maneja conflictos) y hace push de `develop`.
    *   Borra la rama `hotfix/*` local y (si se confirma) remotamente.

## Mensajes de Commit

Sigue **estrictamente** el formato requerido para asegurar el versionado automático correcto:

```
[TAG] (#IssueNumber opcional) Descripción corta y clara en presente
```

*   **`[TAG]`:** Indica el tipo de cambio y determina el incremento de versión en las releases automáticas (según `release.yml`):
    *   `[FEAT]`: Nueva funcionalidad -> Incremento **Minor** (ej. v1.2.3 -> v1.3.0).
    *   `[FIX]`, `[DOCS]`, `[STYLE]`, `[REFACTOR]`, `[PERF]`, `[TEST]`, `[BUILD]`, `[CI]`, `[CHORE]`: Otros cambios -> Incremento **Patch** (ej. v1.2.3 -> v1.2.4).
    *   *(Nota: Un cambio en `.github/major` o un override manual puede forzar un incremento Major).*
*   **`(#IssueNumber opcional)`:** Referencia a un Issue de GitHub (ej. `(#123)`).
*   **`Descripción`:** En presente, imperativo, empezando en minúscula (ej. `añade soporte para xyz`).

El script `wf-git commit` te guiará interactivamente para seleccionar el tag y escribir el mensaje correctamente. **El uso adecuado de los tags es crucial.** Consulta `CONTRIBUTING.md` para ejemplos detallados.

## Mejores Prácticas Clave

*   **Integración Continua (CI):** Configura y mantén un pipeline de CI robusto (GitHub Actions, etc.) que ejecute linters y pruebas automatizadas en cada PR a `develop`. Bloquea merges si los checks fallan.
*   **Pruebas Automatizadas:** Escribe pruebas unitarias, de integración y (si aplica) E2E para todo el código nuevo o modificado. Una buena cobertura de pruebas es fundamental para la confianza en `develop` y habilita el flujo de release ágil (Opción B).
*   **Revisión de Código:** Realiza revisiones de código exhaustivas en los Pull Requests antes de fusionar a `develop`.
*   **Paridad de Entornos:** Esfuérzate por mantener los entornos de prueba (especialmente el usado para probar `develop` o `staging`) lo más parecidos posible al entorno de producción. 