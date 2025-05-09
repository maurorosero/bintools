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
=======
# Guía Completa y Detallada: Nuestro Flujo de Trabajo con Git

**(¡Para Torpes y No Tan Torpes!)**

**Objetivo:** Esta guía explica paso a paso cómo usamos Git en nuestro equipo. Seguir estos pasos nos ayuda a mantener el código ordenado, evitar problemas y lanzar nuevas versiones de forma segura. ¡No te asustes! Iremos detalle a detalle.

**Filosofía General:**

*   **`main` es Sagrado:** La rama `main` SIEMPRE contiene la versión estable que está en producción (la que usan los usuarios finales). Nunca trabajamos directamente en `main`.
*   **`develop` es el Campo de Pruebas:** La rama `develop` es donde integramos todas las nuevas funcionalidades y correcciones. Es como la versión "beta" interna. TODO el trabajo nuevo empieza desde aquí.
*   **Trabajo en Ramas Separadas:** Cada nueva tarea (funcionalidad, corrección) se hace en su propia rama temporal (`feature/algo`, `fix/otro-algo`). Esto aísla los cambios y facilita la revisión.
*   **Pull Requests (PRs) para Revisar:** Antes de que el código de una rama de trabajo llegue a `develop` (y luego a `main`), pasa por un "Pull Request". Es como pedir permiso para fusionar, permitiendo que otros revisen el código y que se ejecuten pruebas automáticas.
*   **Tags para Versiones:** Cada vez que lanzamos una nueva versión a producción desde `main`, le ponemos una "etiqueta" (tag) como `v1.0.0`, `v1.1.0`, etc., para saber exactamente qué código corresponde a qué versión.
*   **Mensajes de Commit Claros:** Cada "guardado" (commit) debe tener un mensaje que explique QUÉ se cambió y POR QUÉ, siguiendo un formato específico.

**Las Ramas Principales:**

1.  **`main`:**
    *   **Contiene:** Código de producción 100% estable y lanzado.
    *   **Se actualiza:** SOLO desde `staging` (para releases) o `hotfix/*` (para emergencias).
    *   **Etiquetado:** Cada merge de release se etiqueta (ej. `v1.2.3`).
    *   **¡PROHIBIDO TRABAJAR DIRECTAMENTE AQUÍ!**

2.  **`develop`:**
    *   **Contiene:** Las últimas funcionalidades y correcciones ya terminadas y probadas (al menos individualmente). Es la versión "en desarrollo" más reciente.
    *   **Se actualiza:** Desde ramas `feature/*`, `fix/*`, `chore/*` (vía PR) y desde `main` (después de un hotfix).
    *   **Origen de TODO trabajo nuevo.**

3.  **`staging` (Opcional, pero lo usamos):**
    *   **Contiene:** Una copia de `develop` cuando nos preparamos para lanzar una nueva versión.
    *   **Propósito:** Probar la versión candidata en un entorno MUY parecido a producción antes del lanzamiento final. Aquí se hacen las últimas pruebas de integración (QA, UAT).
    *   **Se actualiza:** Desde `develop` (al iniciar la preparación de release) y quizás con ajustes mínimos específicos para esa release.
    *   **Destino:** Se fusiona a `main` (vía PR) cuando está lista para lanzar.

4.  **Ramas Temporales (¡Donde trabajas tú!):**
    *   `feature/*`: Para desarrollar una nueva funcionalidad (ej. `feature/login-usuario`).
    *   `fix/*`: Para corregir un bug que NO es urgente (ej. `fix/error-calculo-iva`).
    *   `chore/*`: Para tareas de mantenimiento que no son ni features ni fixes (ej. `chore/actualizar-librerias`, `chore/limpiar-codigo-viejo`).
    *   `hotfix/*`: ¡SOLO EMERGENCIAS! Para corregir bugs críticos en producción (ej. `hotfix/caida-servidor-login`). Se crean desde `main`.

---

**Flujo 1: Empezando desde CERO (Nuevo Proyecto)**

*   **Paso 1: Crear el proyecto y Git inicial**
    ```bash
    # 1.1: Crea una carpeta para tu proyecto y entra en ella
    mkdir mi-proyecto-genial
    cd mi-proyecto-genial

    # 1.2: ¡Inicia Git! (Crea la carpeta oculta .git)
    git init

    # 1.3: Crea archivos básicos (README, .gitignore para ignorar archivos)
    echo "# Mi Proyecto Genial" > README.md
    echo ".env
node_modules/
__pycache__/" > .gitignore # Añade lo que no quieras subir

    # 1.4: Añade estos archivos para que Git los rastree
    git add .

    # 1.5: Haz tu primer "guardado" (commit). Git crea la rama 'main' automáticamente.
    #      ¡Recuerda nuestro formato de mensaje!
    git commit -m "[BUILD] Initial project setup"
    ```

*   **Paso 2: Crear la rama `develop`**
    ```bash
    # 2.1: Crea la rama 'develop' exactamente igual que 'main' en este punto
    git branch develop main
    ```

*   **Paso 3: (Opcional pero recomendado) Crear la rama `staging`**
    ```bash
    # 3.1: Crea la rama 'staging' exactamente igual que 'develop'
    git branch staging develop
    ```
    *   *Ahora tienes `main`, `develop` y `staging` apuntando al mismo punto inicial.*

*   **Paso 4: Conectar con el Repositorio Remoto (GitHub, GitLab...)**
    *   Ve a GitHub/GitLab, crea un **repositorio vacío** (sin README, sin .gitignore).
    *   Copia la URL del repositorio (la que termina en `.git`).
    ```bash
    # 4.1: Dile a tu Git local dónde está el servidor remoto (llamado 'origin')
    git remote add origin <URL_DEL_REPOSITORIO_REMOTO.git>

    # 4.2: Verifica que se añadió bien
    git remote -v

    # 4.3: Sube tu rama 'main' local al servidor 'origin' y establece el seguimiento
    git push -u origin main

    # 4.4: Sube tu rama 'develop' local al servidor 'origin' y establece el seguimiento
    git push -u origin develop

    # 4.5: (Opcional) Sube tu rama 'staging' local al servidor 'origin' y establece el seguimiento
    git push -u origin staging
    ```
    *   **¡LISTO!** El proyecto base está configurado local y remotamente. Ahora puedes empezar a trabajar siguiendo el Flujo 2.

---

**Flujo 2: ¡A Trabajar! (Desarrollar una Nueva Funcionalidad o Corrección)**

*   **Paso 1: Preparar tu espacio de trabajo**
    ```bash
    # 1.1: Asegúrate de estar en la rama 'develop'
    git checkout develop

    # 1.2: ¡MUY IMPORTANTE! Descarga los últimos cambios de 'develop' del servidor.
    #      (Puede que otros compañeros hayan añadido cosas mientras no mirabas)
    git pull origin develop

    # 1.3: Crea TU rama de trabajo desde 'develop'. Usa un nombre descriptivo.
    #      Reemplaza <tipo> por feature, fix, o chore.
    #      Reemplaza <nombre-descriptivo> por algo corto que explique la tarea.
    #      Ej: git checkout -b feature/nuevo-boton-guardar
    #      Ej: git checkout -b fix/login-no-funciona
    git checkout -b <tipo>/<nombre-descriptivo>

    # --- ¡Ahora estás en tu propia burbuja de trabajo! ---
    ```

*   **Paso 2: Hacer los cambios (¡El trabajo real!)**
    *   Edita archivos, crea nuevos, borra... haz lo que tengas que hacer para tu tarea.

*   **Paso 3: Guardar tus cambios (Commits)**
    *   Haz "commits" pequeños y frecuentes. Cada commit debe ser un paso lógico.
    ```bash
    # 3.1: Revisa qué archivos has modificado
    git status

    # 3.2: Añade los archivos que quieres incluir en este "guardado"
    #      Para añadir TODO lo modificado/nuevo:
    git add .
    #      Para añadir solo archivos específicos:
    #      git add archivo1.py ruta/otro_archivo.js

    # 3.3: Haz el "guardado" (commit) con un mensaje CLARO y FORMATEADO.
    #      Formato: [TAG] (#IssueNum opcional) Descripción corta en presente
    #      Ej: git commit -m "[FEATURE] Añade botón de guardar en formulario"
    #      Ej: git commit -m "[FIX] (#45) Corrige validación de email"
    #      Ej: git commit -m "[CHORE] Actualiza dependencia React a v18"
    git commit -m "[TAG] (#IssueNum) Descripción"

    # 3.4: Repite los pasos 3.1 a 3.3 hasta que termines tu tarea.
    ```

*   **Paso 4: Subir tu trabajo al servidor**
    *   Es bueno subir tu rama al servidor de vez en cuando (al final del día, o al terminar la tarea) como copia de seguridad y para que otros puedan verla si es necesario.
    ```bash
    # 4.1: Sube tu rama local al servidor remoto ('origin').
    #      La primera vez que subes ESTA rama, usa '-u' para establecer el seguimiento.
    git push -u origin <tipo>/<nombre-descriptivo>
    #      Las siguientes veces para esta MISMA rama, solo necesitas:
    #      git push
    ```

*   **Paso 5: Pedir Revisión (Crear un Pull Request - PR)**
    *   Cuando tu tarea esté **COMPLETA** y creas que funciona:
    *   Ve a la página web de GitHub/GitLab/etc.
    *   Busca un botón que diga "New Pull Request" o similar.
    *   Selecciona tu rama (`<tipo>/<nombre-descriptivo>`) como la rama "desde" (source/compare).
    *   Selecciona la rama `develop` como la rama "hacia" (target/base).
    *   Escribe un título y descripción claros para el PR (explica qué hace tu cambio y por qué). Si hay un Issue asociado, menciónalo (#NumeroIssue).
    *   Asigna revisores (tus compañeros de equipo o el líder técnico).
    *   ¡Crea el PR!

*   **Paso 6: Responder a la Revisión**
    *   Tus compañeros revisarán tu código y pueden dejar comentarios o pedir cambios.
    *   Si necesitas hacer cambios:
        ```bash
        # 6.1: Asegúrate de estar en tu rama de trabajo
        git checkout <tipo>/<nombre-descriptivo>

        # 6.2: Haz los cambios solicitados...
        #      (Editar archivos...)

        # 6.3: Guarda los cambios con nuevos commits (con el formato!)
        git add .
        git commit -m "[FIX] Aplica sugerencias de revisión del PR" # O un mensaje más específico

        # 6.4: Sube los nuevos commits a tu rama en el servidor.
        #      ¡El PR se actualizará automáticamente!
        git push
        ```
    *   Repite hasta que el PR sea aprobado.

*   **Paso 7: ¡Fusión! (Merge)**
    *   Una vez aprobado el PR (y si pasan las pruebas automáticas), alguien (tú o un revisor, según las reglas del equipo) le dará al botón "Merge Pull Request" en la web de GitHub/GitLab.
    *   ¡Tu código ahora está en la rama `develop`! 🎉

*   **Paso 8: Limpieza (¡Importante!)**
    *   Después de que tu PR se haya fusionado en `develop`:
    ```bash
    # 8.1: Vuelve a la rama 'develop'
    git checkout develop

    # 8.2: Actualiza tu 'develop' local para incluir tus cambios recién fusionados
    git pull origin develop

    # 8.3: Borra tu rama de trabajo local (ya no la necesitas)
    git branch -d <tipo>/<nombre-descriptivo>

    # 8.4: (Opcional, pero recomendado) Borra tu rama de trabajo del servidor.
    #      Normalmente hay un botón en la web del PR para hacerlo, o puedes usar:
    git push origin --delete <tipo>/<nombre-descriptivo>
    ```
    *   ¡Estás listo para empezar la siguiente tarea volviendo al Paso 1 de este Flujo!

---

**Flujo 3: Preparando el Lanzamiento (Release)**

*   *Nota: Esto normalmente lo hace el líder técnico o la persona encargada de las releases, pero es bueno que sepas cómo funciona.*

*   **Paso 1: Decidir qué va en la release y preparar `staging`**
    *   Se revisa `develop` para asegurar que todas las funcionalidades/fixes previstos están ahí y funcionan.
    ```bash
    # 1.1: Asegúrate de que 'develop' está actualizada
    git checkout develop
    git pull origin develop

    # 1.2: Crea o actualiza la rama 'staging' desde 'develop'
    #      Usa -B para crearla si no existe, o resetearla si ya existe:
    git checkout -B staging develop
    #      (-B es como borrarla y volverla a crear desde develop en un paso)

    # 1.3: Sube 'staging' al servidor (forzando si la reseteaste)
    #      --force-with-lease es más seguro que --force
    git push --force-with-lease origin staging
    ```

*   **Paso 2: Pruebas en `staging`**
    *   Se despliega la rama `staging` a un entorno de pruebas (QA, UAT) que sea lo más parecido posible a producción.
    *   El equipo de QA (o el propio equipo de desarrollo) realiza pruebas exhaustivas.
    *   **Si se encuentran BUGS:**
       *   Se corrigen creando una rama `fix/staging-ajuste-X` DESDE `staging`.
       *   Se hace un PR de esa `fix/*` hacia `staging`.
       *   Se fusiona en `staging`.
       *   Se vuelve a probar.
       *   **¡IMPORTANTE!** Estos arreglos hechos en `staging` DEBEN volver a `develop` eventualmente (ver Paso 4).

*   **Paso 3: ¡Lanzamiento! (Merge a `main` y Tag)**
    *   Cuando `staging` está APROBADA y lista:
    *   Se crea un Pull Request desde `staging` hacia `main`.
    *   Revisión final del PR (¡última oportunidad para parar!).
    *   Se fusiona (Merge) el PR en `main`. ¡El código está casi en producción!
    ```bash
    # 3.1: Cambia a 'main' localmente y actualízala (ahora tiene el código de la release)
    git checkout main
    git pull origin main

    # 3.2: ¡CREA LA ETIQUETA (TAG) DE VERSIÓN! Sigue la versión semántica (vMajor.Minor.Patch)
    #      Ej: Si la última fue v1.1.0, esta podría ser v1.2.0 (nueva funcionalidad) o v1.1.1 (solo fixes)
    git tag v1.2.0 # Reemplaza con la versión correcta

    # 3.3: Sube 'main' Y la nueva etiqueta al servidor
    git push origin main --tags
    ```
    *   Se despliega la versión **etiquetada** (`v1.2.0` en el ejemplo) de `main` a producción.

*   **Paso 4: Sincronizar `develop` (¡No te olvides!)**
    *   Es crucial que `develop` reciba los cambios que se hicieron en `main` (la fusión desde `staging`, cualquier ajuste hecho en staging y cualquier posible hotfix futuro).
    ```bash
    # 4.1: Vuelve a 'develop'
    git checkout develop

    # 4.2: Asegúrate de tener lo último de develop
    git pull origin develop

    # 4.3: Fusiona los cambios de 'main' en 'develop'
    git merge main # Trae la versión tageada y cualquier ajuste/hotfix que llegó a main

    # 4.4: Resuelve conflictos si los hay (Git te avisará)
    #      Abre los archivos marcados, edítalos para dejar el código correcto,
    #      luego: git add <archivo_resuelto> y git commit (Git propondrá un mensaje de merge)

    # 4.5: Sube 'develop' actualizada al servidor
    git push origin develop
    ```
    *   (Opcional: Se puede borrar `staging` si ya no se necesita: `git branch -d staging`, `git push origin --delete staging`)

---

**Flujo 4: ¡Fuego! (Hotfix - Arreglo Urgente en Producción)**

*   *¡Solo para emergencias reales que afectan a los usuarios en producción AHORA MISMO!*

*   **Paso 1: Crear la rama hotfix desde `main`**
    ```bash
    # 1.1: Ve a 'main' y asegúrate de tener la última versión (la que está rota)
    git checkout main
    git pull origin main

    # 1.2: Crea tu rama 'hotfix/*' desde 'main'. Sé específico.
    #      Ej: git checkout -b hotfix/login-caido-totalmente
    git checkout -b hotfix/<descripcion-urgente>
    ```

*   **Paso 2: Arreglar el problema**
    *   Haz los cambios MÍNIMOS necesarios para solucionar el bug crítico. ¡No es momento de añadir cosas nuevas ni refactorizar!
    *   Haz commit(s) con el formato correcto:
        ```bash
        git add .
        git commit -m "[FIX] Corrige error crítico que impedía login"
        ```

*   **Paso 3: Lanzar el Hotfix (¡Rápido!)**
    *   Sube tu rama hotfix: `git push -u origin hotfix/<descripcion-urgente>`
    *   Crea un Pull Request desde `hotfix/<descripcion-urgente>` hacia `main`.
    *   Revisión URGENTE y aprobación (puede ser más laxa que una release normal, pero alguien debe mirar).
    *   Fusiona (Merge) el PR en `main`.
    ```bash
    # 3.1: Ve a 'main' y actualiza
    git checkout main
    git pull origin main

    # 3.2: ¡ETIQUETA la versión del hotfix! Incrementa el número de parche.
    #      Ej: Si la versión rota era v1.2.0, el hotfix será v1.2.1
    git tag v1.2.1 # Reemplaza con la versión correcta

    # 3.3: Sube 'main' Y la nueva etiqueta
    git push origin main --tags
    ```
    *   Despliega la versión **etiquetada** del hotfix (`v1.2.1`) a producción INMEDIATAMENTE.

*   **Paso 4: Integrar el Hotfix en `develop` (¡Muy Importante!)**
    *   El arreglo debe estar también en `develop` para que no vuelva a aparecer en la siguiente release normal.
    ```bash
    # 4.1: Ve a 'develop' y actualiza
    git checkout develop
    git pull origin develop

    # 4.2: Fusiona 'main' (que ahora contiene el hotfix) en 'develop'
    git merge main

    # 4.3: Resuelve conflictos si los hay.

    # 4.4: Sube 'develop' actualizada
    git push origin develop
    ```

*   **Paso 5: Limpiar la rama hotfix**
    ```bash
    # 5.1 Borra la rama hotfix localmente
    git branch -d hotfix/<descripcion-urgente>

    # 5.2 Borra la rama hotfix del servidor
    git push origin --delete hotfix/<descripcion-urgente>
    ```

---

**¡Consejos Finales para Torpes (y Listos)!**

*   **`git status` es tu amigo:** Úsalo constantemente para ver en qué rama estás y qué cambios tienes sin guardar o confirmar.
*   **`git pull origin <rama>` antes de empezar a trabajar:** SIEMPRE actualiza tu rama (`develop` principalmente) antes de crear una nueva rama o empezar a hacer cambios importantes. Evita merges dolorosos después.
*   **Commits pequeños y frecuentes:** Es más fácil deshacer (`git reset` o `git revert`) o entender cambios pequeños si algo sale mal.
*   **Mensajes de commit claros y formateados:** ¡Piensa en tu yo del futuro (o en tus compañeros)! El formato `[TAG] (#Issue) Descripción` es obligatorio y ayuda muchísimo a generar changelogs y entender el historial.
*   **No tengas miedo de crear ramas:** Son baratas y te salvan de líos. `git checkout -b nombre-temporal` es fácil para experimentar.
*   **Pull Requests para todo (hacia `develop` y `main`):** Es la red de seguridad. Permite revisión y pruebas automáticas.
*   **Si te atascas (Conflictos de Merge, etc.):** Pide ayuda. Es mejor preguntar que intentar arreglarlo a ciegas y empeorarlo. Busca tutoriales específicos para resolver conflictos de merge.
*   **Lee la documentación:** Esta guía y el `CONTRIBUTING.md` son tus referencias principales. Consúltalos.

¡Con práctica, este flujo se volverá natural! 😊

---

**Preguntas Frecuentes (FAQ)**

Aquí respondemos algunas dudas comunes que pueden surgir al seguir este flujo de trabajo:

**Tema: Protección de la Rama `main`**

*   **P: ¿Cómo evito hacer cambios (commits/push) directamente en `main` por accidente?**
    *   **R:** La forma **más segura y recomendada** es configurar **Reglas de Protección de Rama** en tu plataforma de hosting (GitHub, GitLab, etc.). Estas reglas *impiden* los pushes directos a `main` a nivel del servidor y obligan a usar Pull Requests (PRs) revisados. Adicionalmente, como **medida de seguridad personal** en tu máquina local, puedes configurar Git Hooks (scripts `pre-commit` o `pre-push`) que te adviertan o bloqueen si intentas hacer commit o push directamente a `main`. Sin embargo, la protección en el servidor es la fundamental. Y por supuesto, ¡seguir disciplinadamente el flujo de trabajo descrito es clave!

*   **P: Si `main` es tan delicada, ¿no sería más seguro borrarla de mi repositorio local?**
    *   **R:** No es recomendable ni práctico. Necesitas tener una copia local actualizada de `main` para tareas esenciales definidas en nuestro flujo, como crear ramas `hotfix/*` o fusionar `main` de vuelta a `develop` tras un release o hotfix. Borrarla no ofrece protección real (siempre puedes volver a descargarla del servidor) y te impediría realizar operaciones necesarias del flujo.

*   **P: Ya que no debo borrar `main` localmente, ¿hay alguna forma de *protegerla* en mi máquina?**
    *   **R:** Sí, mediante **Git Hooks locales**. Puedes crear scripts (por ejemplo, en `.git/hooks/pre-commit` o `.git/hooks/pre-push`) que detecten si estás intentando operar directamente sobre la rama `main` y te lo impidan o te avisen. Son una buena salvaguarda *personal*, pero recuerda que solo aplican a tu copia local y pueden ser omitidos (`--no-verify`). La protección principal siempre debe ser la del servidor remoto.

*   **P: ¿Qué pasa si modifico `main` en local y hago `git push origin main`?**
    *   **R:** Idealmente, si se han seguido las recomendaciones y configurado **Reglas de Protección de Rama en el servidor**, tu `push` será **rechazado** por el servidor remoto (GitHub/GitLab), impidiendo el cambio directo. Si tienes un **hook `pre-push` local**, este podría detener el `push` en tu máquina. Sin embargo, **si no existe ninguna protección** (ni en servidor ni local), el `push` tendrá éxito, **modificando `main` directamente** sin revisión, lo cual **contradice nuestro flujo de trabajo** y es altamente riesgoso.

**Tema: Entendiendo los Pull Requests (PRs)**

*   **P: ¿Puedo crear un Pull Request (PR) directamente desde mi Git local?**
    *   **R:** No. Un Pull Request **no es un comando de Git local**. Es una funcionalidad de la **plataforma de alojamiento** (GitHub, GitLab, etc.). El flujo es: 1) Trabajas en tu rama local (`feature/algo`), haces commits. 2) Subes (`git push`) tu rama al servidor remoto. 3) Vas a la **interfaz web** de GitHub/GitLab y creas el Pull Request, proponiendo fusionar tu rama (`feature/algo`) en otra (`develop` o `main`) *en el servidor*. La revisión y la fusión final ocurren en la plataforma remota.

Esperamos que estas aclaraciones te ayuden a navegar el flujo de trabajo con más confianza. 
