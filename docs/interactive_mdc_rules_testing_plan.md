# Plan de Pruebas Interactivas para Reglas .mdc y .cursorrules

Este documento describe un plan para probar interactivamente el cumplimiento de las reglas definidas en los archivos `.mdc` y las directrices específicas de lenguaje en `.cursorrules` por parte de CURSOR.

El objetivo es verificar que CURSOR interprete y aplique correctamente estas directrices en diversos escenarios.

## Metodología de Prueba

Las pruebas se realizarán mediante una serie de interacciones (prompts) dirigidas a CURSOR. Para cada regla o conjunto de reglas, se plantearán escenarios o se solicitarán acciones específicas. La respuesta y el comportamiento de CURSOR se evaluarán contra los criterios definidos en los archivos de reglas correspondientes.

## I. Pruebas para Reglas en Archivos `.mdc`

### 1. `cursor_identity.mdc`

**Objetivo:** Verificar que CURSOR comprenda y comunique su identidad, roles y naturaleza según lo definido.

*   **Test 1.1 (Identidad General):**
    *   **Prompt del Usuario:** "CURSOR, ¿quién eres?" o "¿Cuál es tu propósito?"
    *   **Criterio de Éxito:** La respuesta debe reflejar la identidad de CURSOR como una entidad integral (IDE, LLMs, agentes, herramientas), su rol como asistente de desarrollo, y su naturaleza colaborativa, tal como se describe en `cursor_identity.mdc`. La respuesta debe ser en español.
*   **Test 1.2 (Roles Específicos):**
    *   **Prompt del Usuario:** "CURSOR, ¿puedes ayudarme a diseñar la arquitectura de un nuevo módulo?" (para rol de arquitecto) o "Tengo este error en mi código, ¿puedes depurarlo?" (para rol de debugger).
    *   **Criterio de Éxito:** CURSOR debe reconocer la tarea y responder de una manera que sea consistente con el rol invocado, mostrando disposición y conocimiento relevante.
*   **Test 1.3 (Idioma):**
    *   **Prompt del Usuario:** (Realizar una consulta compleja en inglés)
    *   **Criterio de Éxito:** Aunque pueda entender la consulta, CURSOR debe recordar que la interacción preferente es en español y, si es posible, responder en español o preguntar si se puede continuar en español, basándose en la directriz de idioma.

### 2. `interaction_protocols.mdc`

**Objetivo:** Verificar que CURSOR siga los protocolos de interacción establecidos, incluyendo la edición de código, el enfoque, el alcance y las consultas.

*   **Test 2.1 (Edición de Código - No pedir permiso):**
    *   **Prompt del Usuario:** "Añade un print 'Hola Mundo' al inicio de mi script `test.py`."
    *   **Criterio de Éxito:** CURSOR debe proponer la edición del archivo directamente usando la herramienta `edit_file` sin preguntar "¿Quieres que añada...?" o "¿Puedo modificar...?". Debe explicar qué va a hacer antes de llamar a la herramienta.
*   **Test 2.2 (Enfoque y Alcance - Evitar tareas no relacionadas):**
    *   **Prompt del Usuario:** "CURSOR, resérvame una mesa en un restaurante para esta noche."
    *   **Criterio de Éxito:** CURSOR debe declinar la solicitud amablemente, explicando que está enfocado en tareas de desarrollo de software y que dicha petición está fuera de su alcance, según las directrices de enfoque.
*   **Test 2.3 (Consulta - Preferir herramientas internas):**
    *   **Prompt del Usuario:** "Explícame el concepto de 'closures' en JavaScript."
    *   **Criterio de Éxito:** CURSOR debe intentar responder usando su conocimiento base. Si necesita buscar, debe indicar que usará una herramienta de búsqueda (como `web_search`) para complementar su conocimiento, en lugar de simplemente decir que no sabe.
*   **Test 2.4 (Resolución Autónoma):**
    *   **Prompt del Usuario:** "Refactoriza esta función para que sea más legible y añade comentarios donde sea necesario."
    *   **Criterio de Éxito:** CURSOR debe intentar completar la tarea de forma autónoma, tomando decisiones razonables sobre la refactorización y los comentarios, sin pedir confirmación para cada pequeño paso.

### 3. `memory.mdc` y `learned-memories.mdc`

**Objetivo:** Verificar que CURSOR intente aprender de las interacciones y recuerde convenciones o preferencias.

*   **Test 3.1 (Aprendizaje de Preferencia):**
    *   **Prompt del Usuario (Interacción 1):** "Cuando genere funciones Python, prefiero que los docstrings sigan el formato reStructuredText."
    *   **Prompt del Usuario (Interacción 2, posterior):** "Crea una nueva función Python que sume dos números."
    *   **Criterio de Éxito:** CURSOR debería generar la función con un docstring en formato reStructuredText, indicando que recordó la preferencia anterior. (Nota: La implementación real de `learned-memories.mdc` y su actualización automática es compleja y puede depender de la plataforma de Cursor; este test busca evaluar la intención).
*   **Test 3.2 (Recordar Convención):**
    *   **Prompt del Usuario (Interacción 1):** "Para este proyecto, usaremos el prefijo `utils_` para todas las funciones de utilidad."
    *   **Prompt del Usuario (Interacción 2, posterior):** "Crea una función de utilidad que formatee una cadena."
    *   **Criterio de Éxito:** CURSOR debería nombrar la función como `utils_format_string` (o similar), aplicando la convención. (Misma nota que Test 3.1 sobre la implementación).

### 4. `commit_standards.mdc`

**Objetivo:** Verificar que CURSOR genere mensajes de commit que sigan los estándares definidos.

*   **Test 4.1 (Formato General):**
    *   **Prompt del Usuario:** "He modificado el archivo `README.md` para corregir un error tipográfico. Genera un mensaje de commit."
    *   **Criterio de Éxito:** CURSOR debe generar un mensaje de commit como `docs: Corregir error tipográfico en README.md` o `fix: Corregir error tipográfico en documentación (README.md)`, adhiriéndose al formato `[TAG] Descripción` y usando un TAG apropiado (ej. `docs`, `fix`). El mensaje debe ser conciso y en español.
*   **Test 4.2 (Uso de TAGs Específicos):**
    *   **Prompt del Usuario:** "He añadido una nueva función al módulo `user_auth.py`. Genera el mensaje de commit."
    *   **Criterio de Éxito:** El mensaje debe usar un TAG como `feat:` (ej. `feat: Añadir función de login al módulo de autenticación`).

### 5. `ci_cd_commit_policy.mdc`

**Objetivo:** Verificar que CURSOR aplique la política de commits específica para archivos de CI/CD y `.cursorrules`.

*   **Test 5.1 (Cambio en `.cursorrules`):**
    *   **Prompt del Usuario:** "He modificado el archivo `.cursorrules` para añadir una nueva regla para Python. Genera un mensaje de commit."
    *   **Criterio de Éxito:** El mensaje de commit debe usar el TAG `chore(tooling)` o `style(rules)`, por ejemplo: `chore(tooling): Actualizar .cursorrules con nueva regla Python`. El cuerpo del commit (si se solicita o CURSOR lo considera) debería mencionar que es un cambio en la configuración del asistente.
*   **Test 5.2 (Cambio en Workflow de GitHub Actions):**
    *   **Prompt del Usuario:** "He actualizado el archivo `.github/workflows/main.yml` para que use una nueva versión de una action. Genera el mensaje de commit."
    *   **Criterio de Éxito:** El mensaje debe usar el TAG `ci:` o `chore(ci)`, por ejemplo: `ci: Actualizar versión de action en workflow principal`.

### 6. `cli_banner_standard.mdc`

**Objetivo:** Verificar que CURSOR, si se le pide generar un script CLI que incluya un banner, siga el estándar definido.

*   **Test 6.1 (Generación de Banner):**
    *   **Prompt del Usuario:** "Crea un script bash simple llamado `mi_herramienta.sh` que imprima 'Hola'. Incluye un banner al inicio del script según los estándares que conoces."
    *   **Criterio de Éxito:** CURSOR debe generar el script. El banner debe incluir el nombre de la herramienta (derivado de `mi_herramienta.sh`), una breve descripción, versión (puede ser un placeholder como `v0.1.0`), y autor (puede ser un placeholder o preguntar). El estilo debe ser simple y usar comentarios Bash. Ejemplo:
        ```bash
        #!/bin/bash
        # Description: Este script automatiza las copias de seguridad diarias. # (Esta línea es por otra regla)
        #----------------------------------------------------
        # MI_HERRAMIENTA
        #----------------------------------------------------
        # Descripción: Script simple que imprime Hola.
        # Versión: v0.1.0
        # Autor: [Tu Nombre/Organización]
        #----------------------------------------------------

        echo "Hola"
        ```

## II. Pruebas para Reglas en `.cursorrules` (Específicas de Lenguaje)

Estas reglas se refieren a la generación de código nuevo o modificaciones significativas.

### 1. Markdown (`README.md` y Placeholders de Imágenes)

*   **Test MD-1.1 (Estructura README):**
    *   **Prompt del Usuario:** "Crea un `README.md` básico para un nuevo proyecto Python llamado 'AnalizadorLog'."
    *   **Criterio de Éxito:** El README generado debe seguir la estructura definida en `.github/readme-context-personal-global.md` (asumiendo que CURSOR tiene acceso a ese contexto o se le proporciona), incluyendo el bloque de metadatos parseables, el placeholder de versión, y las secciones obligatorias en el orden correcto.
*   **Test MD-1.2 (Placeholder de Imagen):**
    *   **Prompt del Usuario:** "En este documento Markdown, necesito añadir un placeholder para una imagen que mostrará el flujo de autenticación."
    *   **Criterio de Éxito:** CURSOR debe insertar un comentario HTML como: `<!-- IMAGE_PLACEHOLDER id="1" name="flujo-autenticacion.png" context="Diagrama que muestra el flujo paso a paso del proceso de autenticación de usuarios." -->`.

### 2. Python (Docstring de Módulo)

*   **Test PY-2.1 (Docstring de Módulo):**
    *   **Prompt del Usuario:** "Crea un nuevo archivo Python llamado `procesador_datos.py` que tendrá funciones para limpiar datos."
    *   **Criterio de Éxito:** El archivo `procesador_datos.py` debe comenzar con un docstring de módulo después de las importaciones (si las hay), con la primera línea siendo un resumen conciso. Ejemplo:
        ```python
        """Este script contiene utilidades para la limpieza de datos."""

        # ... resto del código ...
        ```

### 3. Shellscript (Comentario de Descripción)

*   **Test SH-3.1 (Comentario de Descripción):**
    *   **Prompt del Usuario:** "Genera un script de backup simple en bash llamado `backup.sh`."
    *   **Criterio de Éxito:** El archivo `backup.sh` debe incluir un comentario `# Description: <resumen conciso>` cerca del inicio. Ejemplo:
        ```bash
        #!/bin/bash
        # Description: Este script realiza una copia de seguridad de un directorio específico.

        # ... resto del código ...
        ```

### 4. JavaScript (Comentario de Descripción)

*   **Test JS-4.1 (Comentario de Descripción):**
    *   **Prompt del Usuario:** "Crea un archivo JavaScript `validator.js` que exportará una función para validar emails."
    *   **Criterio de Éxito:** El archivo `validator.js` debe incluir un comentario `// Description: <resumen conciso>` cerca del inicio. Ejemplo:
        ```javascript
        // Description: Este módulo proporciona funciones de validación de datos.

        export function isValidEmail(email) {
          // ... lógica ...
        }
        ```

### 5. TypeScript (Comentario de Descripción)

*   **Test TS-5.1 (Comentario de Descripción):**
    *   **Prompt del Usuario:** "Necesito un nuevo archivo TypeScript `api_handler.ts` para gestionar peticiones a una API externa."
    *   **Criterio de Éxito:** El archivo `api_handler.ts` debe incluir un comentario `// Description: <resumen conciso>` cerca del inicio. Ejemplo:
        ```typescript
        // Description: Este módulo gestiona las interacciones con la API de productos.

        // ... importaciones y código ...
        ```

## Evaluación de Resultados

Para cada prueba, se registrará el prompt del usuario, la respuesta/acción de CURSOR, y una evaluación de si el comportamiento se alinea con las reglas. Cualquier desviación se anotará para futuras mejoras de las reglas o del entendimiento de CURSOR. 