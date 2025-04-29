# Mauro Rosero P.'s Personal Utilities 🛠️

<!-- PARSEABLE_METADATA_START
purpose: A collection of scripts and tools designed to automate tasks and enhance productivity.
technology: Bash, Python
status: Development
PARSEABLE_METADATA_END -->

<!-- CURRENT_VERSION_PLACEHOLDER --> ([View Releases](https://github.com/tu_usuario/tu_repo/releases)) <!-- Replace with your actual repo URL -->

## Descripción

A collection of scripts and tools designed to automate tasks and enhance productivity.

## Tabla de Contenidos (Opcional)

*   [Instalación](#instalación)
*   [Uso](#uso)
*   [Herramientas Disponibles](#herramientas-disponibles)
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

Consulta la [documentación de `binsetup.sh`](docs/binsetup.md) para más opciones como `--disable` y `--remove`.

## Uso

Cada script o herramienta tiene su propio uso. Consulta la sección [Herramientas Disponibles](#herramientas-disponibles) y la [Documentación](#documentación) detallada para cada uno.

## Herramientas Disponibles

Aquí tienes una lista de las herramientas disponibles:

| Comando / Script   | Tecnología | Versión | Ult. Actualización | Breve descripción                                                              |
| :----------------- | :--------- | :------ | :----------------- | :----------------------------------------------------------------------------- |
| `binsetup.sh`      | Bash       | N/A     | 2025-04-24         | Gestiona `~/bin` en tu PATH (persistente o temporal).                           |
| `hexroute`         | Bash       | N/A     | 2025-03-19         | Convierte direcciones IPv4 a formato hexadecimal para tablas de rutas.         |
| `packages.sh`      | Bash       | N/A     | 2025-04-25         | Gestiona paquetes base en múltiples SO (instalación/actualización).            |
| `pymanager.sh`     | Bash       | N/A     | 2025-05-26         | Gestiona entornos virtuales de Python (creación, instalación, actualización). |
| `videoset.sh`      | Bash       | N/A     | 2025-04-24         | Configura la resolución de pantalla a 1600x900@60Hz o auto-detecta.           |
| `email_cleaner.py` | Python     | N/A     | 2025-04-24         | Gestor de correo para categorización y limpieza automática.                    |
| `mcp_manager.py`   | Python     | N/A     | 2025-05-26         | Gestor concurrente para servidores MCP (Node/Python) vía YAML.                 |
| `gh-newrepos.py`   | Python     | N/A     | *Needs Update*     | Crea nuevos repositorios en GitHub.                                            |
| `pritunl-vpn.py`   | Python     | 0.2.0   | *Needs Update*     | Instalador/Desinstalador del cliente Pritunl VPN.                              |
| `context-sync.py`  | Python     | 1.2.5   | *Needs Update*     | Sincroniza archivos de contexto para READMEs.                                  |


## Documentación

La documentación detallada para cada herramienta se encuentra en el directorio [`docs/`](docs/).

## Contribución

Las contribuciones son bienvenidas. Por favor, consulta la [Guía de Contribución](CONTRIBUTING.md) para detalles sobre cómo reportar bugs, sugerir mejoras y enviar Pull Requests, incluyendo el formato de commit requerido.

## Licencia

Distribuido bajo la GNU General Public License v3 (GPLv3). Ver `LICENSE` para más información.

Para uso y licencias comerciales, por favor contactar al autor.

## Créditos

| Item/Script   | Author                | Role/Notes                 |
| :------------ | :-------------------- | :------------------------- |
| Project Lead  | Mauro Rosero P. <mauro@rosero.one> | (From Git Config)          |
| Documentation | AI Assistant (Cursor) | (Generated README structure) |
| `binsetup.sh` | Mauro Rosero P.       | (Detected in code)         |

## Contacto

Para sugerencias o problemas, contacta a Mauro Rosero P. en <mauro.rosero.one>.