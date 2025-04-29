# Contexto General para READMEs (Usuario)

Este archivo define las directrices generales para generar y actualizar los archivos README.md de los proyectos personales. El objetivo es asegurar consistencia, claridad y utilidad, especialmente en conjunción con flujos de trabajo automatizados.

## Principios Generales

*   **Claridad y Concisión:** El README debe ser fácil de entender para alguien que llega al proyecto por primera vez. Evitar jerga innecesaria y ser directo.
*   **Completitud:** Debe contener toda la información esencial para que alguien pueda entender qué hace el proyecto, cómo instalarlo y cómo usarlo.
*   **Mantenimiento:** Mantener el README actualizado a medida que el proyecto evoluciona.
*   **Tono:** Generalmente informativo y profesional, pero accesible.
*   **Formato de Commits:** ¡Importante! Utilizar prefijos convencionales en los mensajes de commit (ej. `[FEAT]`, `[FIX]`, `[DOCS]`, etc.) ya que el flujo `release.yml` los usa para determinar el tipo de versión (major/minor/patch) y generar automáticamente las notas del changelog para las releases de GitHub.

## Estructura Estándar Obligatoria

Todo README debe incluir, como mínimo, las siguientes secciones en este orden:

1.  **Título del Proyecto:** Claro y descriptivo. (Normalmente H1 `# Nombre del Proyecto`)
2.  **Metadatos Parseables (Para CI/CD) y Descripción Humana:**

    *   **Bloque de Metadatos (Obligatorio):** Incluir **al inicio** de esta sección (o justo después del título/placeholder de versión) el siguiente bloque de comentarios HTML. Este bloque contiene datos clave diseñados para ser extraídos por scripts (ej., CI/CD) de forma independiente del idioma del resto del README.
        ```html
        <!-- PARSEABLE_METADATA_START
        purpose: [Descripción concisa y principal del proyecto en una línea - ESTA SE EXTRAERÁ para GitHub/GitLab etc.]
        technology: [Tecnologías principales, ej. Python, Go, Bash]
        status: [Estado actual, ej. Development, Beta, Stable, Archived]
        # Añadir otras claves relevantes aquí si es necesario (una por línea: clave_fija_en_ingles: valor en idioma del readme)
        PARSEABLE_METADATA_END -->
        ```
        **Instrucciones Importantes para este Bloque:**
        *   Los delimitadores `<!-- PARSEABLE_METADATA_START` y `PARSEABLE_METADATA_END -->` deben ser **exactos**.
        *   Las **claves** dentro del bloque ( `purpose`, `technology`, `status`, etc.) deben ser **siempre las mismas (ej. en inglés y minúsculas)** para que el parser las encuentre.
        *   Los **valores** asociados a esas claves (después de los dos puntos `:`) pueden y deben estar en el **idioma principal del README**.
        *   La clave `purpose` es la designada para la descripción externa que usarán los scripts de CI/CD.

    *   **Descripción Humana (Opcional pero Recomendada):** *Después* del bloque de metadatos, puedes añadir un párrafo introductorio (1-3 frases) para la lectura humana, explicando qué es y qué hace el proyecto en el idioma del README. Esta parte **no** será parseada automáticamente para la descripción externa.
3.  **Placeholder de Versión (¡CRÍTICO!):** Incluir el siguiente comentario HTML **exactamente** en el lugar donde debe aparecer la versión actual (usualmente cerca del título o badges). El workflow `release.yml` lo reemplazará automáticamente:
    ```html
    <!-- CURRENT_VERSION_PLACEHOLDER -->
    ```
4.  **Badges (Opcional pero Muy Recomendado):** Si aplica (estado de build, cobertura, licencia, etc.), colocar aquí. Un badge que muestre la versión/último tag es altamente recomendable.
5.  **Tabla de Contenidos (Opcional pero Recomendado para READMEs largos):** Facilita la navegación.
6.  **Instalación:** Instrucciones claras y paso a paso sobre cómo instalar y configurar el proyecto/software. Incluir pre-requisitos.
7.  **Uso:** Cómo ejecutar o utilizar el proyecto. Incluir ejemplos básicos. Si es una biblioteca, mostrar ejemplos de código. Si es una app, cómo lanzarla.
8.  **Contribución (Si aplica):** Directrices para quienes deseen contribuir:
    *   Cómo reportar bugs, proponer features, enviar Pull Requests.
    *   **Mencionar la importancia de seguir el formato de commits convencional** (ej. `[FEAT]`, `[FIX]`) para la correcta generación del changelog y versionado automático.
    *   Puede enlazar a un `CONTRIBUTING.md` si es complejo.
9.  **Licencia:** Indicar bajo qué licencia se distribuye el proyecto. Idealmente, enlazar al archivo `LICENSE` completo. (Ej: "Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.")
10. **Contacto (Opcional):** Información de contacto del autor o enlaces relevantes (perfil de GitHub, sitio web).

## Secciones Adicionales Recomendadas (Según Proyecto)

Considerar añadir estas secciones si son relevantes:

*   **Características Principales:** Lista detallada de lo que hace el proyecto.
*   **Ejemplos Avanzados:** Casos de uso más complejos o específicos.
*   **Configuración:** Detalles sobre archivos de configuración o variables de entorno.
*   **Despliegue:** Instrucciones para desplegar la aplicación.
*   **FAQ (Preguntas Frecuentes):** Respuestas a preguntas comunes.
*   **Agradecimientos:** Reconocimiento a colaboradores o recursos utilizados.
*   **Hoja de Ruta (Roadmap):** Planes futuros para el proyecto.
*   **Changelog:** (Nota: Las *notas de release* se generan automáticamente por `release.yml` y se adjuntan a la release de GitHub. No es estrictamente necesario mantener un archivo `CHANGELOG.md` manual en el repositorio si se sigue el formato de commits, a menos que se desee por otras razones.)

## Formato y Estilo

*   Utilizar Markdown estándar.
*   Formatear bloques de código adecuadamente con resaltado de sintaxis (```python ... ```).
*   Usar encabezados (`##`, `###`) para estructurar el contenido.
*   Utilizar listas (numeradas o con viñetas) para enumerar pasos o características.
*   Revisar la ortografía y gramática.

---
*Este es el contexto base. Puede ser sobrescrito o complementado por un contexto específico del proyecto si existe (`.github/readme-context.md`).* 