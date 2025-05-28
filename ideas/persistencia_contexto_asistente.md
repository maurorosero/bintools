# Persistencia de Contexto del Asistente mediante Archivos Estructurados

## 1. Problema

El asistente de IA (LLM) pierde el contexto específico y el "aprendizaje" acumulado en una sesión cuando se inicia una nueva. Las `.cursorrules` proporcionan directrices persistentes, pero no almacenan el historial detallado de decisiones o preferencias específicas del proyecto que evolucionan con el tiempo.

## 2. Solución Propuesta: Archivos de Contexto Estructurado

Mantener archivos dedicados dentro del proyecto para registrar información clave que el asistente pueda leer en futuras sesiones para recuperar contexto.

## 3. Implementación Sugerida (Híbrida)

Se propone usar dos tipos de archivo, ubicados en el directorio `.project/`:

### 3.1. `.project/memory.md` (Historial y Decisiones)

*   **Propósito:** Registrar decisiones importantes, resúmenes de discusiones, contexto cualitativo, justificaciones (el "por qué").
*   **Formato:** Markdown, por su flexibilidad y legibilidad humana.
*   **Estructura Sugerida:**
    *   Entradas ordenadas cronológicamente (o por tema).
    *   Usar fechas y encabezados claros (ej. `## Decisión X - YYYY-MM-DD`).
    *   Resumen conciso de la decisión/evento en puntos clave.
    *   Opcional: Enlaces a commits, issues, discusiones relevantes.
*   **Ejemplo:**
    ```markdown
    # Memoria del Proyecto

    ## Refactorización de `promanager.py` - 2024-07-26

    *   **Decisión:** Revertir cambios en `main()` por errores y desviación del alcance.
    *   **Contexto:** Cambios no solicitados introdujeron errores.
    *   **Acción:** `git checkout HEAD -- promanager.py`.
    *   **Refuerzo:** Actualización de `.cursorrules` (Ver commit: [hash]).

    ## Persistencia de Contexto - 2024-07-26

    *   **Decisión:** Usar archivos estructurados (`memory.md`, `preferences.toml`).
    *   **Siguiente Paso:** Definir workflow lectura/escritura.
    ```

### 3.2. `.project/preferences.toml` (Preferencias Técnicas)

*   **Propósito:** Registrar preferencias técnicas específicas, flags de configuración, valores constantes que el asistente debe recordar.
*   **Formato:** TOML (o YAML), por su estructura clave-valor fácil de parsear automáticamente.
*   **Estructura Sugerida:**
    *   Secciones claras (`[tabla]`).
    *   Pares clave-valor descriptivos.
*   **Ejemplo:**
    ```toml
    # Preferencias del Asistente para este Proyecto

    [general]
    default_language = "es"
    strict_edit_policy = true # Adherencia estricta requerida

    [commit_style]
    preferred_tags = ["[IMPROVE]", "[FIX]", "[DOCS]", "[STYLE]", "[REFACTOR]", "[PERF]", "[TEST]", "[BUILD]", "[CI]", "[CHORE]"]
    require_issue_number = false

    [linting.python]
    preferred_tool = "flake8"
    enforce_black_formatting = true
    ```

## 4. Workflow de Lectura y Escritura

*   **Lectura (Inicio de Sesión):**
    *   **Manual (Recomendado):** El usuario instruye explícitamente al asistente al inicio: "Lee `.project/memory.md` y `.project/preferences.toml`". (Más fiable).
    *   **Automático (Experimental):** Incluir regla en `.cursorrules` para intentar la lectura proactiva. (Fiabilidad no garantizada).
*   **Escritura/Actualización:**
    *   **Manual (Recomendado):** El usuario edita los archivos directamente.
    *   **Semi-Automático (Iniciado por Usuario):**
        1.  Usuario pide al asistente resumir una decisión.
        2.  Usuario revisa y aprueba el resumen.
        3.  Usuario pide explícitamente al asistente que añada el resumen aprobado al archivo `.md` (requiere `edit_file` y confirmación).

## 5. Limitaciones Importantes

*   **No es aprendizaje real:** Es alimentación de contexto, no una modificación interna persistente del LLM.
*   **Dependencia de la Interpretación:** La efectividad depende de la calidad/claridad de la información almacenada y la capacidad del asistente para interpretarla correctamente *en esa sesión*.
*   **Sobrecarga:** Requiere disciplina para mantener los archivos actualizados y añade un paso extra (lectura/escritura) al flujo de trabajo.
*   **Contexto Limitado:** Solo funciona si los archivos están presentes y accesibles en el contexto de la sesión actual.
