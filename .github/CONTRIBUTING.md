# Contribuyendo a Utilitarios Personales

¡Gracias por tu interés en contribuir a esta colección de utilitarios! Ya sea reportando un bug, sugiriendo una mejora, o escribiendo código, tu ayuda es bienvenida.

## Código de Conducta

Se espera que todos los participantes sigan nuestro [Código de Conducta](CODE_OF_CONDUCT.md). (Nota: necesitarías crear este archivo si aún no existe).

## ¿Cómo Puedo Contribuir?

*   **Reportando Bugs:** Si encuentras un error, por favor, abre un [Issue en GitHub](https://github.com/tu_usuario/tu_repo/issues) (reemplaza con tu URL) describiendo el problema, cómo reproducirlo y tu entorno.
*   **Sugiriendo Mejoras:** ¿Tienes una idea para un nuevo script o una mejora para uno existente? Abre un [Issue en GitHub](https://github.com/tu_usuario/tu_repo/issues) describiendo tu propuesta.
*   **Mediante Pull Requests:** Si quieres contribuir con código o documentación directamente.

## Configuración del Entorno

Asegúrate de tener el entorno base configurado ejecutando:

```bash
# Configuración permanente (recomendado)
~/bin/binsetup.sh --persistent

# O para la sesión actual
source ~/bin/binsetup.sh
```

Para gestionar dependencias de Python, utiliza `pymanager.sh` o gestiona los entornos virtuales como prefieras, usando los archivos `requirements-*.txt` específicos si existen.

## Flujo de Trabajo de Desarrollo

Utilizamos un flujo simple basado en feature branches y Pull Requests.

### 1. Ramas (Branches)

*   La rama principal para la integración suele ser `main` (o `testing` si la usas activamente). Desde aquí se hacen las releases.
*   **Nunca trabajes directamente en `main`**.
*   Crea una nueva rama descriptiva para cada nueva funcionalidad o corrección a partir de la rama principal:
    ```bash
    # Asegúrate de estar en la rama base (ej. main) y tener lo último
    git checkout main
    git pull origin main

    # Crea tu nueva rama
    git checkout -b feature/nombre-corto-descriptivo
    # o para arreglos:
    # git checkout -b fix/descripcion-del-arreglo
    ```

### 2. Realizando Cambios

*   Escribe código claro y mantenible.
*   Si añades una nueva funcionalidad o corriges un bug, **añade pruebas (tests)** que cubran tus cambios.
*   Asegúrate de que tu código pasa los linters configurados (ej. `flake8`, `eslint`, `shellcheck`). Puedes ejecutar los workflows de CI localmente si tienes herramientas como `act`, o esperar a que se ejecuten en el PR.
*   Actualiza la documentación relevante (el `README.md` específico del componente en `docs/` si aplica).

### 3. Mensajes de Commit **¡Importante!**

Utilizamos un formato específico para los mensajes de commit que es **crucial** para la automatización del versionado y la generación del changelog. Sigue este formato:

```
[TAG] (#IssueNumber opcional) Descripción corta y clara en presente
```

*   **`[TAG]`:** Una etiqueta en **MAYÚSCULAS** y entre corchetes que describe el tipo de cambio. Las etiquetas estándar son:
    *   `[FEAT]`: Introduce una nueva funcionalidad (dispara versión **Minor**).
    *   `[FIX]`: Corrige un bug (dispara versión **Patch**).
    *   `[DOCS]`: Cambios únicamente en la documentación (dispara versión **Patch**).
    *   `[STYLE]`: Cambios que no afectan el significado del código (espacios, formato, puntos y comas faltantes, etc.) (dispara versión **Patch**).
    *   `[REFACTOR]`: Un cambio en el código que no corrige un bug ni añade una funcionalidad (dispara versión **Patch**).
    *   `[PERF]`: Un cambio en el código que mejora el rendimiento (dispara versión **Patch**).
    *   `[TEST]`: Añadir tests faltantes o corregir tests existentes (dispara versión **Patch**).
    *   `[BUILD]`: Cambios que afectan al sistema de build o dependencias externas (ej. `requirements.txt`) (dispara versión **Patch**).
    *   `[CI]`: Cambios en nuestros archivos y scripts de configuración de CI (ej. workflows de GitHub Actions) (dispara versión **Patch**).
    *   `[CHORE]`: Otros cambios que no modifican código fuente ni de tests (ej. actualizaciones menores de dependencias) (dispara versión **Patch**).
*   **`(#IssueNumber opcional)`:** Si tu commit resuelve un Issue específico de GitHub, puedes incluir su número aquí (ej. `(#123)`). Es opcional.
*   **`Descripción corta y clara`:** Empieza en minúscula (a menos que sea un nombre propio) y usa el modo imperativo en tiempo presente (ej. "añade soporte para X" en lugar de "añadido soporte" o "añadirá soporte").

**Ejemplos:**

```
[FEAT] Añade opción --verbose a email_cleaner
[FIX] (#45) Corrige error de división por cero en mcp_manager
[DOCS] Actualiza ejemplos en docs/pymanager.md
[STYLE] Aplica formato black a pritunl-vpn.py
[TEST] Añade pruebas unitarias para la función de conversión hex
[CHORE] Actualiza dependencia requests a 2.28.1
```

**¡La correcta utilización de estos tags es esencial para que el proceso de release funcione!**

### 4. Pull Requests (PRs)

*   Una vez que tus cambios estén listos en tu rama, haz push a GitHub:
    ```bash
    git push -u origin feature/nombre-corto-descriptivo
    ```
*   Ve al repositorio en GitHub y abre un Pull Request desde tu rama hacia la rama principal (`main` o `testing`).
*   Rellena la descripción del PR explicando *qué* cambios hiciste y *por qué*. Si resuelve un Issue, referencia el número (`Closes #123`).
*   Los workflows de CI (linting, tests) se ejecutarán automáticamente en tu PR. Asegúrate de que pasen.
*   Alguien revisará tu PR. Puede que te pidan cambios. Haz los cambios necesarios en tu rama y haz push; el PR se actualizará automáticamente.
*   Una vez aprobado y con los checks en verde, tu PR será fusionado.

## Proceso de Release (Unificado y Manual)

Las releases de esta colección de utilitarios se gestionan de forma **unificada** (una única versión para todo el repositorio) y se disparan **manualmente**.

*   **Disparo:** Un mantenedor del repositorio ejecutará el workflow "Unified Custom Release" desde la pestaña "Actions" de GitHub cuando se considere que hay suficientes cambios listos para una nueva versión (normalmente desde la rama `main`).
*   **Versionado Automático (Personalizado):** El workflow calcula la nueva versión (`vX.Y.Z`) automáticamente siguiendo estas reglas:
    1.  **Override Major:** Si el contenido del archivo `.github/major` ha cambiado desde la última release, se fuerza un incremento **Major** (ej. v1.5.2 -> v2.0.0).
    2.  **Detección Minor:** Si no hay override Major, y existe al menos un commit desde la última release con la etiqueta `[FEAT]`, se realiza un incremento **Minor** (ej. v1.5.2 -> v1.6.0).
    3.  **Detección Patch:** Si no hay override Major ni `[FEAT]`, pero existen commits con etiquetas como `[FIX]`, `[DOCS]`, `[STYLE]`, `[REFACTOR]`, `[PERF]`, `[TEST]`, `[BUILD]`, `[CI]`, o `[CHORE]`, se realiza un incremento **Patch** (ej. v1.5.2 -> v1.5.3).
    4.  **Fallback Patch:** Si no se cumple ninguna de las condiciones anteriores, pero *sí* existen commits (con mensajes mal formateados o sin tags estándar) desde la última release, se realiza un incremento **Patch** por seguridad.
    5.  **Sin Release:** Si no hay commits nuevos desde la última release, no se crea ninguna versión nueva.
    6.  **Override Manual:** Al ejecutar el workflow, se puede *forzar* un tipo de incremento específico (major, minor, patch, none), ignorando toda la lógica automática.
*   **Acciones Automáticas:** Si se determina una nueva versión, el workflow:
    1.  Calcula la nueva versión (ej. `v1.2.1`).
    2.  Actualiza el placeholder de versión en el `README.md` principal.
    3.  Genera notas de release (changelog) basadas en los mensajes de commit.
    4.  Crea un commit con el `README.md` actualizado.
    5.  Crea y empuja un tag Git (ej. `v1.2.1`).
    6.  Crea una Release formal en GitHub con el tag y las notas.
    7.  (Opcional) Resetea el archivo `.github/major` si se usó para un override Major.

## Estilo de Código

Intenta seguir el estilo de código existente. Usamos herramientas como `flake8` (Python), `eslint` (JS/TS), `shellcheck` (Bash) para ayudar a mantener la consistencia.

## Pruebas (Testing)

Fomentamos la inclusión de pruebas para asegurar la calidad y evitar regresiones. Si añades código nuevo, por favor, añade también tests.

---

¡Gracias de nuevo por tu contribución! 