# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v14.9.0] - 2025-06-20

### Added
- 🎉 Implementa sistema híbrido de generación de README con análisis global
- 🎉 Agregar configuración del generador de descripciones de proyectos
- 🎉 Implementar analizador de descripciones de proyectos

### Changed
- ⚡ Actualización del changelog
- ⚡ Limpiar archivos obsoletos


## [v14.6.0] - 2025-06-18

### Added
- 🎉 Generación automática de CONTRIBUTING.md usando analizador de hooks y CI/CD

### Fixed
- 🐛 Consistencia en uso de 'Tag' y distribución correcta de versiones en CHANGELOG


## [v14.5.0] - 2025-06-18

### Added
- 🎉 configura formato semántico para commitlint
- 🎉 agrega sistema de gestión de templates
- 🎉 Añadir libsecret y libsecret-tools a la lista de dependencias para gestión segura de tokens
- 🎉 Se agregaron Librerias python: - Dependencias para gestión segura de tokens - Soporte a APIs de GitLab, Gitea y Atlassian
- 🎉 Actualizar wrapper commitlint en scaffold con lectura dinámica de tags
- 🎉 Integrar Branch Workflow Validator en pre-commit hooks
- 🎉 Implementar ecosistema Git Branch Tools completo
- 🎉 Agregar soporte multi-proyecto en Git Branch Tools
- 🎉 Mejoras en git-tokens.py: usuario opcional y manejo elegante de interrupciones
- 🎉 Implementar APIs multi-plataforma completas en git-integration-manager
- 🎉 Implementar APIs adicionales completas para Gitea, Forgejo y Bitbucket
- 🎉 Integración de QualityManager en git-integration-manager
- 🎉 Implementa CICDManager para gestionar configuraciones CI/CD
- 🎉 Mejora detección multi-lenguaje en integrador CI/CD
- 🎉 Reorganiza configuraciones CI/CD existentes
- 🎉 Añade validaciones críticas para CI/CD
- 🎉 Implementación integral de gestión de estados de rama y mejoras de calidad
- 🎉  Make upstream push default and add --no-remote flag
- 🎉 Implementa scripts principales para docgen
- 🎉 Implementa hook validador de headers para metadatos de archivos
- 🎉 Agrega actualización automática de fecha en headers con @check-header
- 🎉 Añade script de análisis de versionado por archivo
- 🎉 Permite análisis de versionado del repositorio completo
- 🎉 Añade opción --update para escribir versión global en .project/version
- 🎉 Permite análisis de grupos de archivos y patrones glob
- 🎉 Soporte para --update en archivo individual: actualiza versión en el header
- 🎉 Soporte --depth y búsqueda correcta en carpetas ocultas para --update-all en versioning.py
- 🎉 Agregar script para instalar licencias establecidas y reemplazar LICENSE
- 🎉 Add changelog generation configuration and system prompts
- 🎉 Add advanced changelog generation to docgen.py
- 🎉 Add release automation script

### Changed
- ⚡ Agrega plantillas de configuración para commitlint
- ⚡ Agrega package.json para commitlint
- ⚡ Agrega script wrapper para commitlint
- ⚡ Actualiza plantillas .def y configuración de pre-commit
- ⚡ Actualiza configuración de pre-commit y scripts
- ⚡ configura flujos y hooks de commit (setup-ci) (6 commits)
- ⚡ configura flujos y hooks de commit (5 commits)
- ⚡ CI: configura flujos y hooks de commit
- ⚡ otro mensaje (#456) (2 commits)
- ⚡ implementa funcionalidad de instalación en micursor.py [micursor.py]
- ⚡ Mejora la visualización de --config-mdc con diseño minimalista
- ⚡ reorganiza estructura de configuración de cursor
- ⚡ añade sistema de reglas mdc
- ⚡ implementa documentación de reglas mdc
- ⚡ añade configuración base de cursor
- ⚡ elimina sistema de gestión de headers y referencias en pre-commit
- ⚡ actualiza configuración y templates de commitlint
- ⚡ actualiza reglas y memoria de cursor
- ⚡ actualiza scripts con nuevos headers
- ⚡ elimina archivos obsoletos
- ⚡ actualiza template de pre-commit
- ⚡ Mejora el formato del header para scripts Bash
- ⚡ Simplifica y mejora el gestor de templates
- ⚡ refactor sistema de reglas y gestión de proyectos
- ⚡ Rediseño en la gestión de secretos - Reestructurar git-tokens.py: migración a keyring - CLI modular en español - y soporte multi-servicio
- ⚡ Agrega textos oficiales a licencias establecidas y prompts a licencias generadas por IA
- ⚡ Reorganización de archivos de commitlint a .githooks/
- ⚡ Implementación de hooks de pre-commit organizados por grupos
- ⚡ Reorganización de archivos de configuración en scaffold/
- ⚡ Actualización de hooks y configuración en scaffold workspace
- ⚡ Elimina archivos reubicados de config/ y scaffold/ws/brain/licenses/
- ⚡ Implementar generación dinámica de .pre-commit-config.yaml con plantilla Jinja2
- ⚡ Aplicar correcciones automáticas de formato de lints
- ⚡ Añadir sistema inteligente de gestión de branches con detección automática de contexto
- ⚡ Actualiza manual git-branch-tools con funcionalidades reales
- ⚡ Refactor manual-git-branch-tools: eliminar duplicaciones y completar sección 6
- ⚡ Actualiza tabla de contenidos del manual Git Branch Tools
- ⚡ Añade sección Git Aliases y mejora contenido del manual
- ⚡ Añade Sección 7: Workflows Completos End-to-End al manual Git Branch Tools
- ⚡ Mejora git-integration-manager y limpia documentación obsoleta
- ⚡ Completar manual git-branch-tools con funcionalidades reales y casos de uso prácticos
- ⚡ Reescribir sección 8 para mostrar solo funcionalidades implementadas
- ⚡ Limpieza final: espacios en blanco y fin de línea en configuraciones y scripts de hooks
- ⚡ actualiza documentación y configuración de calidad
- ⚡ Add metrics workflows for all platforms
- ⚡ Implementa sistema de métricas y badges adaptativo (#45)
- ⚡ Centraliza verificación GPG en branch-workflow-validator
- ⚡ Implementa sistema de sincronización de estados de ramas
- ⚡ Actualiza reglas MDC y agrega sistema de verificación
- ⚡ Mejora sistema de validación de commits y configuración de hooks
- ⚡ Mejorar gestion y visualizacion de commitlint
- ⚡ Actualizar validación de trailing-whitespace
- ⚡ Mejorar y corregir la gestión de protección de ramas
- ⚡ Implementa sistema de configuración para docgen
- ⚡ Actualiza documentación de Git Branch Tools con detalles de workflows y troubleshooting
- ⚡ Reglas cursor-mdc de estilo de codificación para scaffold en bash, js, python y typescript
- ⚡ Elimina archivos mdc antiguos de cursor y brain en favor de la nueva estructura
- ⚡ Reglas cursor-mdc de estilo de codificación en bash, js, python y typescript
- ⚡ Agrega regla de docstrings estilo Google/PEP-257 en reglas de Python
- ⚡ Implementa integración dinámica de Cursor con commitlint
- ⚡ Agregar regla de formato de commit en scaffold
- ⚡ Cambio de headerpara gestión de validación de encabezados
- ⚡ Cambio de header para gestión de validación de encabezados para bash
- ⚡ Cambio de header para gestión de validación de encabezados para js (3 commits)
- ⚡ Refactoriza lógica de headers para reutilizar código y usar tag Check Heading
- ⚡ Actualización automatica de la Fecha de Modificación
- ⚡ Elimina mensajes informativos de la salida del script (3 commits)
- ⚡ Permite actualización de fecha de modificación
- ⚡ REFACTOR ahora suma MINOR en grupos; solo RELEASE suma MAJOR
- ⚡ Implementa cálculo en dos fases para --update-all
- ⚡ Actualiza headers de archivos con información de copyright y versión
- ⚡ Actualiza headers restantes de archivos con información de copyright
- ⚡ Agregar documentación de versionado y releases al manual de git branch tools
- ⚡ Modificación de versión
- ⚡ Actualizaciones de scripts, helpers y mantenimiento
- ⚡ Add changelog generation documentation and initial changelog

### Deprecated
- ⚠️ Elimina archivos legacy y de respaldo

### Fixed
- 🐛 Corregir permisos de ejecución y falsos positivos de detección de secretos
- 🐛 Corregir wrapper commitlint para leer tags dinámicamente y actualizar configuración semantic
- 🐛 Corregir configuración del validador con always_run: true
- 🐛 Refactoriza QualityManager para usar configuración independiente
- 🐛 Usa rutas relativas en QualityManager para mejor portabilidad
- 🐛 Actualiza lógica de detección de contexto para coincidir con branch-git-helper
- 🐛 Corregir acceso a ramas protegidas y robustecer validacion commitlint
- 🐛 Corregir y robustecer la gestión de protecciones y configuraciones
- 🐛 Corrige KeyError en 'show_status' al obtener el contexto La función 'get_context_info' no devolvía los datos dinámicos del repositorio (contribuidores, commits, etc.), lo que causaba un error de clave ('contributors') en el comando 'show_status'. Esta corrección modifica 'get_context_info' para que recopile y devuelva tanto la configuración estática del contexto como los datos dinámicos del repositorio. Además, se ajustan las llamadas a esta función para reflejar la nueva estructura de datos y se mejora la legibilidad de la salida de 'show_status'.
- 🐛 Cambio de header para gestión de validación de encabezados para bash
- 🐛 Cambio de header para gestión de validación de encabezados para js (2 commits)
- 🐛 CAmbios para actualizar la fecha de modificación (2 commits)
- 🐛 Correcciones a la actualización automática de la Fecha de Modificación (7 commits)
- 🐛 Corrección definitiva a la actualización automática de la Fecha de Modificación
- 🐛 Se corrige para que actualice bash y python
- 🐛 Detección [header-validator] funciona para bash, python y js (2 commits)
- 🐛 Error de verbose en header-update pre-commit corregido!
- 🐛 Actualización para fecha de modificación de js corregido
- 🐛 Actualización para fecha de modificación - modificaba fuera del contexto del header
- 🐛 Destruye el archivo aplicando fecha de modificación js - corregido (usa sed)
- 🐛 Destruye el archivo aplicando fecha de modificación bash - corregido (usa sed)
- 🐛 Destruye el archivo aplicando fecha de modificación python - corregido (usa sed)
- 🐛 Corregir Check Heading (2 commits)
- 🐛 Corrige lógica de --update-all para procesar archivos individualmente
- 🐛 Extiende --depth para búsqueda recursiva automática en archivos específicos

### Breaking Changes
- ❌ Comando state: gestión de estados de rama (MERGED/WIP), --delete, --replace y aliases git
- ❌ Implementación completa de la gestión de estados de ramas (WIP, MERGED, DELETED)


## [v0.0.2] - 2025-05-13

### Changed
- ⚡ Introduce flujo para ramas ci/*, actualiza guías y herramientas de desarrollo


## [v0.0.1] - 2025-05-13

### Added
- 🎉 Añadir script context-sync.py y actualizar .gitignore
- 🎉 Añade opción --python a --create y muestra versión en --list [pymanager.sh]
- 🎉 Añade comando --package-global para instalar en entorno global [pymanager.sh]
- 🎉 Añade comando --package-local para instalar en entornos locales existentes [pymanager.sh]
- 🎉 Introduce wfwdevs.py para gestión de flujo de trabajo Git y ajusta archivos relacionados
- 🎉 Integra verificación de cambios no confirmados y stash interactivo en wfwdevs.py
- 🎉 Implementa tarea sync-develop y reestructura argparse en wfwdevs.py

### Changed
- ⚡ Initial project setup with scripts and documentation
- ⚡ Actualizar README con información sobre email_cleaner
- ⚡ Agregar .gitignore para Bash y Python
- ⚡ Agregar documentación para email_cleaner
- ⚡ Actualizar documentación de email_cleaner
- ⚡ Refactorización completa de email_cleaner.py
- ⚡ Actualizar documentación de email_cleaner.py
- ⚡ Agregar script packages.sh y su documentación
- ⚡ Eliminar config.json.example
- ⚡ Actualizar packages.sh y documentación con soporte para Snap
- ⚡ Permitir seguimiento de archivos .def y mejoras en packages.sh
- ⚡ Agregar archivos de definición para paquetes extras y Snap
- ⚡ Actualizar documentación para archivos de definición
- ⚡ Actualizar documentación con nuevas funcionalidades
- ⚡ Actualizar packages.sh y su documentación
- ⚡ Mover y actualizar archivo snap.def con más paquetes disponibles
- ⚡ Actualizar documentación y agregar CLIs de gestión de Git en archivo de definición
- ⚡ Actualizar interfaz de usuario con colores y mejorar manejo de paquetes
- ⚡ Mejorar pymanager.sh - Añadir alias pyunbin para desactivar entornos y actualizar documentación
- ⚡ Actualizar documentación de packages.sh con nuevas características
- ⚡ Agregar documentación para el gestor de entornos Python
- ⚡ Actualizar .gitignore para permitir requirements.txt en la raíz
- ⚡ Añadir función --update para verificar y actualizar paquetes
- ⚡ Actualizar documentación del gestor de entornos Python
- ⚡ Actualizar documentación incluyendo nuevas funcionalidades
- ⚡ Añadir pymanager.sh a la tabla de scripts y créditos del README
- ⚡ Añadir nuevos scripts y documentación para la gestión de servidores MCP
- ⚡ Crear archivo de instrucciones para generación de mensajes de commit
- ⚡ Crear archivo de contribuciones para el proyecto
- ⚡ Añadir archivos de plantilla para contribuciones, issues y pull requests
- ⚡ Actualizar comentario en el script pritunl-vpn.py
- ⚡ Actualizar documentación de `mcp_manager.py` y README.md
- ⚡ configura workflow de release automatizado y actualiza guías
- ⚡ Actualiza directrices de contribución en CONTRIBUTING.md
- ⚡ añade pre-commit, gestión de cabeceras y scripts de entorno
- ⚡ Añade script gh-newrepos.py para crear repositorios en GitHub
- ⚡ añade script gh-newrepos y corrige formato de fecha en cabecera
- ⚡ header script extracts description from Python docstrings
- ⚡ añade regla a .cursorrules para docstrings en python
- ⚡ Add description convention and extraction for header script
- ⚡ Update headers with generated descriptions
- ⚡ Add UTF-8 encoding declaration to generated headers
- ⚡ Add missing UTF-8 encoding declarations to headers
- ⚡ Add shebang line to header_manage.py for improved script execution
- ⚡ Añade guía completa sobre el flujo de trabajo con Git
- ⚡ Add CLI tool wf-git.py to assist with Git workflow management
- ⚡ Update pymanager.sh and pre-commit configuration for better environment management
- ⚡ Correctly ignore .venv/ directory and stop tracking its contents
- ⚡ Update tracked files after index reset
- ⚡ Refine git workflow guide with release options and best practices
- ⚡ Refactorizar pymanager.sh (instalación, salida, comandos); eliminar .project
- ⚡ Eliminar archivos artefacto no usados del directorio bin
- ⚡ Merge branch 'fix/pymanager' into develop
- ⚡ Implementa reglas específicas para CI/CD y configuraciones
- ⚡ Añade mensaje de activación post-install y usa path consistentemente [pymanager.sh]
- ⚡ q
- ⚡ Simplifica "--install" para crear/instalar entorno default [pymanager.sh]
- ⚡ Añade gestión de alias para activación/desactivación global [pymanager.sh] - Introduce los comandos `--set global` y `--unset global` para gestionar   un alias `pyglobalset` en `~/.bashrc`. - El alias `pyglobalset` activa el entorno virtual global   (`~/.venv/default`). - `--set global` añade el alias a `.bashrc` (si no existe) y muestra   instrucciones para recargar `.bashrc` y usar el alias y `deactivate`. - `--unset global` elimina el alias de `.bashrc` usando marcadores   y muestra instrucciones para recargar la configuración. - Elimina el comando `--activate` que solo mostraba el comando source. - Actualiza la función de ayuda (`show_help`) para incluir los nuevos   comandos `--set global` y `--unset global`.
- ⚡ Implementa --set local y asegura permisos de activate [pymanager.sh]
- ⚡ Mejora compatibilidad TOML, flujo de creación y estilos visuales [project_manager.py]
- ⚡ Agrega regla para placeholders de imagen en Markdown [.cursorrules]
- ⚡ Agrega documentación para project_manager.py con placeholders de imagen [project_manager.md]
- ⚡ Elabora y refina guía de usuario detallada para pymanager.sh
- ⚡ Actualiza .cursorrules con nueva regla para banners CLI
- ⚡ Renombra script a promanager.py y actualiza banner
- ⚡ Renombra project_manager a promanager, actualiza banner y elimina CURSOR.md, gh-newrepos.py
- ⚡ Implementa sistema de gestión de tokens Git con SOPS
- ⚡ Merge branch 'main' into develop
- ⚡ Merge pull request #1 from maurorosero/develop (3 commits)
- ⚡ Actualización al README
- ⚡ Configuración de protección de ramas
- ⚡ Merge pull request #2 from maurorosero/feature/create_github_remote_repo
- ⚡ Permite seguimiento del directorio .project
- ⚡ Actualiza reglas de .gitignore para manejar .project y project_meta.toml
- ⚡ Añade archivo de configuración por defecto project_meta.def
- ⚡ Añade inicialización automática de estructura del proyecto
- ⚡ Merge branch 'develop'
- ⚡ Actualiza guía de Git y mejora promanager.py
- ⚡ Salvaguarda cambios en develop antes de cambiar a main
- ⚡ Commit inicial del proyecto
- ⚡ Refina protección de ramas, creación de repos y manejo de editor [promanager.py] (2 commits)
- ⚡ Agrega .gitkeep para rastrear directorio .project
- ⚡ Ignora directorio .project/ completo y elimina su contenido del seguimiento
- ⚡ Merge remote-tracking branch 'origin/develop' into feature/desarrollo-wfwdevs-script
- ⚡ Merge pull request #1 from maurorosero/feature/desarrollo-wfwdevs-script
- ⚡ Aplica manejo detallado de rebase y mejora mensaje de recuperación de stash
- ⚡ Implementa verificación de cambios no commiteados [wfwdevs]
- ⚡ Re-estructura metadatos del proyecto [project_meta]
- ⚡ Refina políticas de IA y proceso de release
- ⚡ Add commitlint for commit message validation
- ⚡ Add automated release and versioning workflow
- ⚡ Merge pull request #2 from maurorosero/feature/ci-develop
- ⚡ Merge pull request #4 from maurorosero/develop primer release CI
- ⚡ Cambio directo a la rama main para corregir error en el CI (2 commits)
- ⚡ Cambio directo a la rama main para corregir error en el CI de creación de release (4 commits)
- ⚡ Auto-update individual file versions [skip ci] (2 commits)

### Fixed
- 🐛 Corrige extracción de paquetes ignorados en salida de pip [pymanager.sh]
- 🐛 Se corrige la ubicación del archivo de logs cuando no es superusuario
- 🐛 Corrige lógica de push opcional para --task new en wfwdevs.py
- 🐛 Re-ensamblaje por destrucción de cursor tratando de ser creativo

### Breaking Changes
- ❌ Implementar remove --package para eliminar paquetes de un entorno
- ❌ Añadir funcionalidad --package al comando remove para eliminar paquetes específicos
- ❌ Remove context-sync.py and ensure .venv is ignored
- ❌ Reemplaza --remove con --remove-global y --remove-local interactivo [pymanager.sh]
- ❌ Mejora --remove-local con gum y añade comando --install [pymanager.sh] - Corrige error en --remove-local donde seleccionar un entorno individual   con `gum` (presionando Enter) no funcionaba o se interpretaba   incorrectamente como cancelación. - Cambia el modo de `gum choose` en --remove-local de multiselección   (`--no-limit`) a selección única. Ahora Enter selecciona directamente   y Escape cancela, eliminando la necesidad de marcar con Espacio. - Refactoriza la lógica de procesamiento de selección en `remove_local_env`   para manejar la elección única con una estructura `case`. - Añade el comando `--install` como atajo para crear/asegurar el entorno   global (`~/.venv/default`) e instalar los requisitos por defecto   (`bin/requirements.txt`) usando `install_global_package`. - Actualiza la función de ayuda (`show_help`) para reflejar el nuevo   comportamiento de selección de `--remove-local` y la nueva opción   `--install`.


## [Unreleased]

### Added
- 🎉 Integrar validación de .project/description.md en generación de README
- 🎉 Mostrar estructura real del proyecto hasta 3 niveles
- 🎉 Usar título del archivo .project/description.md en README
- 🎉 Agregar script para corregir audio HDMI
- 🎉 Agregar dependencias para APIs de IA y generación de PDFs

### Changed
- ⚡ Actualización del CHANGELOG.md
- ⚡ Agregar README.md generado automáticamente
- ⚡ Agregar guía de uso de git-branch-tools
- ⚡ Mejorar README y configuración de gitignore

### Fixed
- 🐛 Mostrar estructura real del proyecto en README
- 🐛 Corregir inconsistencias en estructura del proyecto
- 🐛 Actualizar descripción del proyecto
- 🐛 Actualizar modelo de configuración
- 🐛 Eliminar manual obsoleto de git-branch-tools
- 🐛 Corregir normalización de nombres de secciones excluidas
