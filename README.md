# BINTOOLS - Utilitarios Personales de Mauro Rosero P. 🛠️

<!-- PARSEABLE_METADATA_START
purpose: A collection of scripts and tools designed to automate tasks and enhance productivity.
technology: Bash, Python
status: Development
PARSEABLE_METADATA_END -->

<!-- CURRENT_VERSION_PLACEHOLDER --> ([View Releases](https://github.com/maurorosero/bintools/releases))

## Descripción

**BINTOOLS** es una colección de utilidades diseñadas para simplificar tu mundo digital, comando a comando. Estas herramientas actúan como tu asistente personal, manejando la complejidad y los detalles para que tú no tengas que hacerlo. El proyecto está disponible en [github.com/maurorosero/bintools](https://github.com/maurorosero/bintools).

¿Qué resuelve BINTOOLS?
- 🛠️ **Gestión de Entorno**: Configuración automática de tu entorno de desarrollo con `binsetup.sh` y `packages.sh`
- 🔐 **Seguridad**: Gestión de claves GPG y tokens de autenticación con `gpg_manager.py` y `git-tokens.py`
- 📧 **Productividad**: Automatización de tareas de correo y gestión de proyectos con `email_cleaner.py` y `promanager.py`
- 🖥️ **Sistema**: Configuración de resolución de pantalla y gestión de paquetes del sistema con `videoset.sh` y `packages.sh`
- 🐍 **Desarrollo**: Gestión de entornos virtuales Python y servidores MCP con `pymanager.sh` y `mcp_manager.py`
- 🔄 **DevOps**: Creación y gestión de repositorios remotos con `promanager.py` y configuración de VPN con `pritunl-vpn.py`

## Tabla de Contenidos

*   [Instalación](#instalación)
*   [Herramientas Disponibles](#herramientas-disponibles)
*   [Hooks de Pre-commit](#hooks-de-pre-commit)
*   [Documentación](#documentación)
*   [Contribución](#contribución)
*   [Licencia](#licencia)
*   [Créditos](#créditos)
*   [Contacto](#contacto)

## Instalación

Para empezar a usar estas utilidades:

```bash
# Configuración persistente (recomendado)
~/bin/binsetup.sh --persistent

# O solo para la sesión actual
source ~/bin/binsetup.sh
```

## Herramientas Disponibles

Aquí tienes una lista de las herramientas disponibles:

| Comando / Script   | Tecnología | Versión | Ult. Actualización | Breve descripción                                                              |
| :----------------- | :--------- | :------ | :----------------- | :----------------------------------------------------------------------------- |
| [`binsetup.sh`](docs/binsetup.md)      | Bash       | 0.1.0   | 2025-04-24         | Gestiona `~/bin` en tu PATH (persistente o temporal).                           |
| [`hexroute`](docs/hexroute.md)         | Bash       | 1.0     | 2025-03-19         | Convierte direcciones IPv4 a formato hexadecimal para tablas de rutas.         |
| [`packages.sh`](docs/packages.md)      | Bash       | 0.9.4   | 2025-04-25         | Gestiona paquetes base en múltiples SO (instalación/actualización).            |
| [`pymanager.sh`](docs/pymanager.md)     | Bash       | 0.1.0   | 2025-05-26         | Gestiona entornos virtuales de Python (creación, instalación, actualización). |
| [`videoset.sh`](docs/videoset.md)      | Bash       | 0.1.0   | 2025-04-24         | Configura la resolución de pantalla a 1600x900@60Hz o auto-detecta.           |
| [`email_cleaner.py`](docs/email_cleaner.md) | Python     | 0.1.0   | 2025-04-24         | Gestor de correo para categorización y limpieza automática.                    |
| [`git-tokens.py`](docs/git-tokens.md)    | Python     | 0.1.0   | 2025-05-26         | Gestor de tokens de autenticación para servicios Git (GitHub, GitLab, etc.).   |
| [`header_manager.py`](docs/header_manager.md)| Python     | 0.1.0   | 2025-05-26         | Gestiona y estandariza encabezados en archivos de código fuente.               |
| [`mcp_manager.py`](docs/mcp_manager.md)   | Python     | 0.1.0   | 2025-05-26         | Gestor concurrente para servidores MCP (Node/Python) vía YAML.                 |
| [`promanager.py`](docs/promanager.md)    | Python     | 0.1.0   | 2025-05-26         | Gestor de metadatos de proyecto y creación de repositorios remotos.            |
| [`pritunl-vpn.py`](docs/pritunl-vpn.md)   | Python     | 0.2.0   | 2025-05-26         | Instalador/Desinstalador del cliente Pritunl VPN.                              |
| [`gpg_manager.py`](docs/gpg_manager.md)   | Python     | 0.2.0   | 2025-05-26         | Gestor de claves GPG y configuración de Git.                                   |

## Hooks de Pre-commit

Este repositorio incluye hooks de pre-commit para mantener la consistencia en los encabezados de los archivos:

```bash
# Instalar los hooks
pre-commit install

# Ejecutar los hooks en todos los archivos
pre-commit run --all-files
```

El hook configurado:
- Verifica y actualiza los encabezados de los archivos
- Se aplica a archivos Python (.py), TypeScript (.ts), Shell (.sh) y JavaScript (.js)
- Utiliza el script `header_manage.py` para la gestión de encabezados

Para más detalles, consulta el archivo `.pre-commit-config.yaml` y la [documentación de pre-commit](https://pre-commit.com/).

## Documentación

La documentación detallada para cada herramienta se encuentra en el directorio [`docs/`](docs/).

### Otras guías y tutoriales

Además de la documentación específica de cada herramienta, el directorio `docs/` contiene guías y tutoriales generales:

| Documento | Descripción |
| :-------- | :---------- |
| [`guia-git-workflow.md`](docs/guia-git-workflow.md) | Guía detallada del flujo de trabajo Git para gestión de proyectos de desarrollo |
| [`requirements.md`](docs/requirements.md) | Requisitos del sistema y dependencias necesarias para todas las herramientas |
| [`sops.md`](docs/sops.md) | Guía de uso de SOPS (Secrets OPerationS) para el manejo seguro de secretos |

## Asistencia con IA

Este proyecto utiliza Cursor como asistente de desarrollo para todas las aplicaciones. Cursor es una herramienta de IA que ayuda en el desarrollo de código, proporcionando sugerencias, completado de código y asistencia en la resolución de problemas.

### Configuración de Cursor

El proyecto incluye un archivo `.cursorrules` que define reglas específicas para la asistencia de IA. Estas reglas aseguran la consistencia en el desarrollo y mantienen los estándares del proyecto:

1. **Reglas de Commit**:
   - Tags permitidos: [CHORE], [CI], [FIX], [DOCS]
   - Formato: `[TAG] (#Issue) Descripción específica [Componente]`
   - Ejemplos: `[CI] (#45) Optimiza caché de dependencias [Workflow Tests]`

2. **Estándares de Banners**:
   - Aplicable a herramientas CLI (Python, Bash, JavaScript, TypeScript)
   - Requiere limpieza de pantalla, implementación encapsulada
   - Debe mostrar: nombre de la aplicación, versión y autor
   - Formato visual consistente con delimitadores y espaciado adecuado

3. **Reglas de Documentación**:
   - Estructura estandarizada para READMEs
   - Formato específico para metadatos parseables
   - Convenciones para placeholders de imágenes
   - Docstrings y comentarios descriptivos en todos los archivos

4. **Política de Edición**:
   - Requiere descripción detallada de cambios
   - Necesita confirmación explícita antes de aplicar cambios
   - Mantiene un registro claro de modificaciones

5. **Convenciones de Idioma**:
   - Contenido en español por defecto
   - Excepciones para términos técnicos y convenciones de código
   - Nombres de variables y funciones en inglés

## Contribución

Las contribuciones son bienvenidas. Por favor, consulta la [Guía de Contribución](CONTRIBUTING.md) para detalles sobre cómo reportar bugs, sugerir mejoras y enviar Pull Requests, incluyendo el formato de commit requerido.

## Licencia

Distribuido bajo la GNU General Public License v3 (GPLv3). Ver `LICENSE` para más información.

Para uso y licencias comerciales, por favor contactar al autor.

## Créditos

| Script   | Autor                | Role/Notes                 |
| :------------ | :-------------------- | :------------------------- |
| Autor Principal  | Mauro Rosero P. <mauro@rosero.one> | Líder del proyecto y autor principal |
| Asistente IA | Cursor | Asistente de desarrollo para todas las aplicaciones escritas por Mauro Rosero P.|
| `binsetup.sh` | Mauro Rosero P. | Script de configuración del entorno |
| `hexroute`    | Karl McMurdo | Utilidad de conversión de rutas (integración) |
| `packages.sh` | Mauro Rosero P. | Gestor de paquetes del sistema |
| `pymanager.sh`| Mauro Rosero P. | Gestor de entornos Python |
| `videoset.sh` | Mauro Rosero P. | Configurador de resolución de pantalla |
| `email_cleaner.py` | Mauro Rosero P. | Gestor de correo electrónico |
| `git-tokens.py` | Mauro Rosero P. | Gestor de tokens de autenticación |
| `header_manager.py` | Mauro Rosero P. | Gestor de encabezados de archivos |
| `mcp_manager.py` | Mauro Rosero P. | Gestor de servidores MCP |
| `promanager.py` | Mauro Rosero P. | Gestor de metadatos de proyecto |
| `pritunl-vpn.py` | Mauro Rosero P. | Gestor del cliente VPN |
| `gpg_manager.py` | Mauro Rosero P. | Gestor de claves GPG |


## Contacto

Para sugerencias o problemas, contacta a Mauro Rosero P. en <mauro.rosero.one>.