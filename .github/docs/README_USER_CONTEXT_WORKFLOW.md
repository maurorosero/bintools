# Flujo de Trabajo para Editar Contexto README de Usuario

Este documento describe el proceso acordado para crear o modificar el archivo de contexto global de README para el usuario (`~/.developer/contexts/user_readme.md`) utilizando el asistente AI y el script `context-sync.py`.

## Propósito

El asistente AI opera dentro de los límites del workspace actual y no puede acceder directamente a archivos fuera de él (como los ubicados en `~/.developer/`). Para sortear esta limitación, utilizamos el directorio `tmp/` (ignorado por Git, excepto por `.gitkeep`) como un área de "staging" temporal.

## Componentes Clave

*   **Archivo Maestro:** `~/.developer/contexts/user_readme.md` (la ubicación real del contexto).
*   **Archivo Temporal:** `tmp/context_user_readme.md` (o similar, ej. `tmp/context-user-readme.md`). Es la copia dentro del workspace sobre la que trabaja el AI.
*   **Directorio `tmp/`:** Carpeta dentro del workspace para alojar archivos temporales. Su contenido es ignorado por Git.
*   **Script `context-sync.py`:** Herramienta que:
    1.  Busca el archivo temporal en `tmp/`.
    2.  Lo copia a la ubicación del Archivo Maestro.
    3.  Elimina el archivo temporal de `tmp/`.
    4.  (Adicionalmente) Asegura que el enlace simbólico del contexto global esté configurado correctamente en el proyecto (`.github/readme-context-personal-global.md`).
*   **Asistente AI (Yo):** Realiza la edición del archivo *temporal* basándose en tus instrucciones.
*   **Convención de Keywords:** Usar frases como "contexto de readme de usuario", "contexto de usuario", "contexto personal" al dar instrucciones al AI para indicar que nos referimos a este flujo de trabajo.

## Flujo de Trabajo Paso a Paso

1.  **PREPARACIÓN (Solo si modificas un archivo existente):**
    *   Abre tu terminal en la raíz de tu workspace (ej. `~/bin`).
    *   Copia el archivo maestro a la carpeta `tmp/` con un nombre reconocible por el script (ej. `context_user_readme.md`).
      ```bash
      cp ~/.developer/contexts/user_readme.md ./tmp/context_user_readme.md
      ```

2.  **INSTRUCCIÓN AL AI:**
    *   Indica al asistente qué quieres hacer usando una de las **keywords**.
    *   *Ejemplo Creación:* "Crea el contexto de usuario con secciones X, Y, Z."
    *   *Ejemplo Modificación:* "Actualiza el contexto de readme de usuario, añade detalles sobre la licencia MIT."

3.  **CONFIRMACIÓN DEL AI:**
    *   El asistente reconocerá la keyword y te pedirá confirmación para operar sobre el archivo en `tmp/`.
    *   *Respuesta Esperada del AI:* "Entendido. ¿Quieres que cree/modifique el archivo `tmp/context_user_readme.md` para [tu solicitud]?"

4.  **TU CONFIRMACIÓN:**
    *   Responde afirmativamente al asistente ("Sí", "Ok", "Adelante").

5.  **EDICIÓN POR EL AI:**
    *   El asistente usará sus herramientas para crear o modificar el archivo `tmp/context_user_readme.md`.

6.  **FINALIZACIÓN Y LIMPIEZA:**
    *   Una vez que el asistente haya completado la edición en `tmp/` y estés satisfecho:
    *   Abre tu terminal en la raíz del workspace.
    *   Ejecuta el script de sincronización:
      ```bash
      ./context-sync.py
      ```
    *   El script copiará el archivo de `tmp/` a `~/.developer/contexts/user_readme.md` y eliminará la copia de `tmp/`. Verifica los mensajes del script para asegurarte de que todo funcionó correctamente.

Siguiendo estos pasos, podemos colaborar eficientemente en la gestión del contexto README de usuario, a pesar de las limitaciones del workspace. 