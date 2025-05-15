# Project Manager Tool

<!-- PARSEABLE_METADATA_START
purpose: Herramienta para gestionar metadatos de proyecto en un archivo TOML, facilitando la inicialización y edición interactiva de la información del proyecto y repositorio.
technology: Python, tomli, tomli-w, questionary
status: Development
PARSEABLE_METADATA_END -->

<!-- CURRENT_VERSION_PLACEHOLDER -->

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
<!-- Puedes añadir más badges relevantes aquí -->

## Descripción General

`promanager.py` es una herramienta de línea de comandos diseñada para simplificar la gestión de los metadatos de un proyecto. Estos metadatos se almacenan en un archivo llamado `project_meta.toml`, ubicado en el directorio `.project/` dentro de la raíz de tu proyecto. La herramienta facilita la creación inicial de este archivo, así como la edición interactiva de la información del repositorio, detalles del proyecto y otros metadatos configurables.

El objetivo principal es centralizar la información crucial del proyecto de una manera estructurada y accesible, tanto para humanos como para posibles automatizaciones futuras.

## Características Principales

*   **Inicialización de Metadatos**: Crea automáticamente un archivo `project_meta.toml` con una estructura predefinida si no existe en el proyecto.
*   **Edición Interactiva del Repositorio**: Permite definir y modificar información como:
    *   Nombre del repositorio.
        *   <!-- IMAGE_PLACEHOLDER id="1" name="init_repo_name_prompt.png" context="Captura de pantalla de la terminal mostrando la pregunta 'Nombre del Repositorio:' del questionary." -->
    *   Propietario (usuario u organización) y su nombre.
    *   Plataforma de alojamiento (GitHub, GitLab, Gitea, Bitbucket, etc.), incluyendo URLs para instancias auto-alojadas.
        *   <!-- IMAGE_PLACEHOLDER id="2" name="init_platform_prompt.png" context="Captura de pantalla de la terminal mostrando la selección de 'Plataforma:' con las opciones disponibles." -->
    *   Visibilidad (público o privado).
    *   Descripción corta.
    *   Opciones de inicialización para el repositorio remoto (añadir README, .gitignore con plantilla específica, y LICENSE con plantilla SPDX).
*   **Edición Interactiva de Detalles del Proyecto**: Gestiona información como:
    *   Título del proyecto.
    *   Propósito o descripción detallada.
    *   Estado actual (planificación, activo, en espera, completado, archivado).
    *   Líder del proyecto.
    *   Información de la herramienta de gestión de proyectos (nombre, enlace, clave).
    *   Listas para objetivos, interesados, stack tecnológico, riesgos y supuestos (actualmente se muestran, la edición interactiva de listas es una mejora futura).
    *   Restricciones del proyecto (presupuesto, cronograma).
*   **Edición Manual de Metadatos Adicionales**: Abre el archivo `project_meta.toml` en el editor de texto por defecto del sistema (`$EDITOR` o `vim`) para añadir o modificar campos en la sección `[additional_metadata]`.
*   **Gestión de Rutas**: Permite especificar el directorio del proyecto a través del argumento `-p` o `--path`. Por defecto, opera en el directorio actual.
*   **Detección de Cambios**: Informa al usuario si hay cambios sin guardar y ofrece opciones para guardar, descartar o guardar y salir.
*   **Interfaz Amigable**: Utiliza la biblioteca `questionary` para ofrecer una experiencia de usuario interactiva y guiada en la terminal.

## Instalación

La herramienta es un script de Python 3 y requiere las siguientes bibliotecas:

*   `tomli`: Para leer archivos TOML (integrado como `tomllib` en Python 3.11+).
*   `tomli-w`: Para escribir archivos TOML.
*   `questionary`: Para los prompts interactivos en la terminal.

Puedes instalar estas dependencias usando pip:

```bash
pip install "tomli<2.0.0,>=1.1.0" tomli-w questionary
```
(Asegúrate de que la versión de `tomli` sea compatible si usas Python < 3.11).

## Uso

Puedes ejecutar el script directamente si tiene permisos de ejecución, o usando el intérprete de Python.

Ejecución básica (opera en el directorio actual):
```bash
./promanager.py
# o
python promanager.py
```

Especificar la ruta del proyecto:
```bash
python promanager.py -p /ruta/a/mi/proyecto
```
o
```bash
python promanager.py --path ../otro-proyecto
```

### Flujo de Inicialización

Si el archivo `.project/project_meta.toml` no existe en la ruta especificada, la herramienta iniciará el flujo de creación:

1.  **Notificación**: Se te informará que el archivo de metadatos no fue encontrado y se procederá a crearlo.
2.  **Información del Repositorio (Requerida)**:
    *   Se te pedirá secuencialmente la información mínima para definir el repositorio:
        *   Nombre del Repositorio.
            *   <!-- IMAGE_PLACEHOLDER id="1" name="init_repo_name_prompt.png" context="Captura de pantalla de la terminal mostrando la pregunta 'Nombre del Repositorio:' del questionary." -->
        *   Tipo de Propietario (user/organization).
        *   Nombre de la Organización (si el tipo es "organization").
        *   Visibilidad (private/public).
        *   Plataforma (GitHub, GitLab, Gitea, etc.).
            *   <!-- IMAGE_PLACEHOLDER id="2" name="init_platform_prompt.png" context="Captura de pantalla de la terminal mostrando la selección de 'Plataforma:' con las opciones disponibles." -->
        *   URL de la Plataforma (si es auto-alojada o tipo "Otra").
3.  **Información Opcional del Repositorio**:
    *   Se te preguntará si deseas rellenar detalles opcionales del repositorio, que incluyen:
        *   Descripción del repositorio.
        *   Opciones de inicialización (`init_options`):
            *   ¿Inicializar con README?
            *   ¿Añadir .gitignore? (y plantilla a usar, ej: Python, Node)
            *   ¿Añadir LICENSE? (y plantilla SPDX, ej: mit, gpl-3.0)
4.  **Detalles del Proyecto**:
    *   Se te preguntará si deseas rellenar los detalles del proyecto (título, propósito, estado, etc.).
5.  **Guardado**: Finalmente, la información recopilada se guardará en `.project/project_meta.toml`.

Si cancelas (`Ctrl+C`) durante la entrada de datos requeridos, la operación se detendrá. Si cancelas durante la entrada de datos opcionales, se te preguntará si deseas guardar la información mínima recopilada hasta ese momento.

### Flujo de Edición

Si el archivo `.project/project_meta.toml` ya existe, la herramienta cargará los datos y presentará un menú principal:

<!-- IMAGE_PLACEHOLDER id="3" name="edit_main_menu.png" context="Captura de pantalla de la terminal mostrando el menú principal de questionary con las acciones: 'Editar Info Repositorio', 'Editar Detalles Proyecto', 'Editar Metadatos Adicionales (Manual)', 'Guardar Cambios', 'Salir (Descartar Cambios)', 'Guardar y Salir'. El título del prompt indicará si hay cambios sin guardar." -->

Descripción de las opciones del menú:

*   **Editar Info Repositorio**:
    *   Si el repositorio se considera "creado" (es decir, ya tiene una URL establecida en los metadatos o el flag `created_flag` es `true`), algunos campos clave (nombre, propietario, visibilidad, plataforma) se mostrarán como solo lectura. Podrás editar la descripción.
    *   Si el repositorio no está "creado", podrás editar todos los campos, incluyendo las `init_options` (README, .gitignore, LICENSE).
    *   <!-- IMAGE_PLACEHOLDER id="4" name="edit_repo_info_form.png" context="Captura de pantalla del formulario para editar la información del repositorio, mostrando campos como Nombre, Propietario, Visibilidad, etc." -->

*   **Editar Detalles Proyecto**:
    *   Permite editar campos como el título del proyecto, propósito, estado, líder, información de la herramienta de gestión de proyectos (Jira, Trello, etc.), y restricciones (presupuesto, cronograma).
    *   Las listas como `objectives`, `stakeholders`, `technology_stack` se mostrarán pero su edición interactiva aún no está implementada (se indica "Editar manualmente o mejorar script").

*   **Editar Metadatos Adicionales (Manual)**:
    *   Esta opción abre el archivo `project_meta.toml` directamente en el editor de texto configurado en tu sistema (variable de entorno `$EDITOR`, o `vim` por defecto).
    *   Se te instruirá que realices los cambios deseados en la sección `[additional_metadata]` (o cualquier otra, con cuidado), guardes el archivo en el editor, cierres el editor, y luego presiones Enter en la terminal donde corre `promanager.py`.
    *   La herramienta intentará recargar el archivo TOML. Si hay errores de formato, se te notificará y los metadatos previos (antes de la edición manual) se conservarán.
    *   <!-- IMAGE_PLACEHOLDER id="5" name="edit_manual_metadata_prompt.png" context="Captura de pantalla mostrando el mensaje que indica que el archivo se abrirá en el editor (ej. 'Abriendo .project/project_meta.toml en vim...') y la instrucción para guardar, cerrar el editor y pulsar Enter para recargar." -->

*   **Guardar Cambios**: Guarda todas las modificaciones realizadas en la sesión actual al archivo `project_meta.toml`.
*   **Salir (Descartar Cambios)**: Sale de la herramienta. Si hay cambios sin guardar, se pedirá confirmación antes de descartarlos.
*   **Guardar y Salir**: Guarda todas las modificaciones y luego sale de la herramienta.

Si se presiona `Ctrl+C` en el menú principal, se pedirá confirmación para salir si hay cambios no guardados.

## Estructura del Archivo `project_meta.toml`

La herramienta espera y gestiona un archivo TOML con la siguiente estructura principal. Las claves se mantienen en inglés para consistencia interna y facilitar el parseo por otras herramientas.

```toml
schema_version = "1.5" # Versión del esquema del archivo

[repository]
name = "nombre-del-repositorio"
owner_name = "nombre_usuario_o_org" # Vacío si owner_type es "user" y el repo es del usuario actual
owner_type = "user" # "user" u "organization"
visibility = "private" # "private" o "public"
platform = "GitHub" # "GitHub", "GitLab.com", "GitLab (Auto-alojado)", "Gitea", "Forgejo (Auto-alojado)", etc.
platform_url = "" # URL base para plataformas auto-alojadas
description = "Descripción corta del repositorio."
created_flag = false # Indica si el repositorio remoto ya ha sido creado
url = "" # URL completa al repositorio remoto (ej. https://github.com/user/repo.git)

[repository.init_options]
add_readme = true
add_gitignore = true
gitignore_template = "Python" # Plantilla de .gitignore (ej. Python, Node, Java)
add_license = true
license_template = "mit" # Identificador SPDX de la licencia (ej. mit, gpl-3.0)

[project_details]
title = "Título Completo del Proyecto"
purpose = "Propósito detallado y objetivos principales del proyecto."
status = "planning" # planning, active, on-hold, completed, archived
lead = "Nombre del Líder del Proyecto"
objectives = ["Objetivo 1", "Objetivo 2"] # Lista de objetivos clave
stakeholders = ["Stakeholder A", "Stakeholder B"] # Lista de interesados
technology_stack = ["Python", "Docker", "PostgreSQL"] # Tecnologías principales
risks = ["Riesgo identificado 1", "Descripción del riesgo 2"] # Riesgos potenciales
assumptions = ["Supuesto A", "Supuesto B"] # Supuestos del proyecto

[project_details.pm_tool_info]
tool_name = "Jira" # Nombre de la herramienta de gestión (Jira, Trello, Asana, etc.)
project_link = "https://jira.example.com/browse/PROJ" # Enlace al proyecto en la herramienta
project_key = "PROJ" # Clave o ID del proyecto en la herramienta

[project_details.constraints]
budget = "TBD" # Presupuesto asignado o por definir
timeline = "TBD" # Cronograma o fecha límite

[additional_metadata]
# Esta sección es para cualquier metadato adicional específico del proyecto.
# Puedes añadir cualquier par clave-valor que necesites.
# Ejemplo:
# client_name = "ACME Corp"
# internal_project_id = "XYZ-123"
```

<!-- IMAGE_PLACEHOLDER id="6" name="example_project_meta_toml.png" context="Un fragmento de código mostrando un ejemplo bien formateado del archivo project_meta.toml con algunas secciones (repository, project_details, additional_metadata) y claves rellenas para ilustrar la estructura." -->

## Contribución

Las contribuciones son bienvenidas. Por favor, consulta `CONTRIBUTING.md` (si existe en el repositorio padre, o adapta este mensaje) para más detalles sobre cómo contribuir, el formato de los mensajes de commit y el proceso de release.

## Licencia

Distribuido bajo la Licencia GPLv3. Ver `LICENSE` (si existe en el repositorio padre, o adapta este mensaje) para más información.

## Contacto

Para reportar bugs, solicitar características o hacer preguntas, por favor abre un issue en el repositorio del proyecto.
<!-- Reemplaza con el enlace real a los issues si aplica -->

---
*Documentación generada con asistencia de IA.* 