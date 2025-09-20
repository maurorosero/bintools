# Guía para Desarrolladores - bintools

> **📖 [← Volver al README principal](../README.md)**

## 📖 Introducción

Esta guía está dirigida a desarrolladores que quieren contribuir al proyecto bintools. Incluye información sobre instalación del entorno de desarrollo, estructura del proyecto, convenciones de código, proceso de desarrollo y gestión de releases.

## 🚀 Instalación del Entorno de Desarrollo

### Pre-requisitos del Sistema

Para desarrollar en bintools, necesitas:

- **Sistema operativo compatible**: Ubuntu, Debian, Fedora, CentOS, Arch Linux, macOS
- **Git**: Para control de versiones
- **Bash 4.0+**: Para ejecutar scripts
- **Python 3.6+**: Para herramientas Python
- **GitHub CLI**: Para gestión de releases (opcional)

### Instalación de Herramientas Base

```bash
# Instalar herramientas base del sistema
packages.sh --list base

# Instalar herramientas de desarrollo
packages.sh --list devs

# Instalar GitHub CLI (para gestión de releases)
packages.sh --list bwdn  # Incluye GitHub CLI
```

### Configuración del Entorno de Desarrollo

#### Método 1: Clonado del Repositorio

```bash
# Clonar el repositorio
git clone https://github.com/maurorosero/bintools.git
cd bintools

# Establecer permisos correctos y seguros para desarrollo
./btfixperms.sh

# Configurar Git (si no está configurado)
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

#### Método 2: Fork del Repositorio (Recomendado para Contribuidores)

```bash
# 1. Fork el repositorio en GitHub
# 2. Clonar tu fork
git clone https://github.com/TU_USUARIO/bintools.git
cd bintools

# 3. Agregar el repositorio original como upstream
git remote add upstream https://github.com/maurorosero/bintools.git

# 4. Establecer permisos correctos
./btfixperms.sh

# 5. Verificar configuración
git remote -v
```

### Verificación del Entorno

```bash
# Verificar herramientas instaladas
which git bash python3

# Verificar permisos de archivos
ls -la *.sh

# Verificar configuración de Git
git config --list | grep user

# Ejecutar tests básicos
./packages.sh --help
./btfixperms.sh --help
```

## 📁 Estructura del Proyecto

```text
bintools/
├── 📄 Scripts principales
│   ├── packages.sh              # Instalador de paquetes
│   ├── micursor.py              # Gestor de Cursor IDE
│   ├── pymanager.sh             # Gestor de Python
│   ├── fix_hdmi_audio.sh        # Solucionador de audio HDMI
│   ├── videoset.sh              # Configurador de pantalla
│   ├── nxcloud-backup.sh        # Gestor de Nextcloud
│   ├── hexroute                 # Convertidor de rutas
│   ├── bintools-manager.sh      # Gestor del proyecto
│   └── btfixperms.sh            # Gestor de permisos
├── 📁 Configuraciones
│   ├── configs/
│   │   ├── *.pkg               # Listas de paquetes
│   │   ├── release-config.yml   # Configuración de releases
│   │   └── user.pkg            # Paquetes personalizados
│   └── repos/
│       ├── ubuntu/             # Scripts de repositorios Ubuntu
│       ├── debian/             # Scripts de repositorios Debian
│       ├── fedora/             # Scripts de repositorios Fedora
│       └── arch/               # Scripts de repositorios Arch
├── 📚 Documentación
│   ├── docs/
│   │   ├── packages.md         # Guía de packages.sh
│   │   ├── repo.md             # Guía de repo-install.sh
│   │   ├── secrets.md          # Guía de gestión de secretos
│   │   ├── bw.md               # Guía de Bitwarden CLI
│   │   ├── bw-send.md          # Guía de bw-send.sh
│   │   ├── odoodevs.md         # Guía de odoodevs
│   │   ├── pymanager.md        # Guía de pymanager.sh
│   │   ├── cursor-sync-guide.md # Guía de sincronización Cursor
│   │   └── developers.md       # Esta guía
├── 🔧 Herramientas de desarrollo
│   ├── create-release.sh       # Crear releases
│   ├── delete-release.sh       # Eliminar releases
│   ├── release-builder.sh      # Generar paquetes
│   └── install.sh              # Instalador para usuarios
└── 📋 Archivos de proyecto
    ├── README.md               # Documentación principal
    ├── LICENSE                 # Licencia GPL v3
    ├── VERSION                 # Versión actual
    └── .gitignore              # Archivos ignorados por Git
```

## 🔧 Convenciones de Código

### Estilo de Scripts Bash

#### Estructura de Scripts

```bash
#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Nombre del Script - Descripción breve
# -----------------------------------------------------------------------------
# Script Name: nombre-del-script.sh
# Version: 1.0.0
# Author: Tu Nombre <tu@email.com>
# Created: YYYY-MM-DD HH:MM:SS
# Updated: YYYY-MM-DD HH:MM:SS

# -----------------------------------------------------------------------------
# Copyright (C) YYYY Tu Nombre
# -----------------------------------------------------------------------------
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

# Configuración básica
# ==================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
LOG_DIR="$HOME/.logs"
LOG_FILE="$LOG_DIR/script-name.log"
APP_NAME="Nombre de la Aplicación"
VERSION="1.0.0"

# Colores y formatos
COLOR_GREEN="\033[0;32m"
COLOR_YELLOW="\033[0;33m"
COLOR_RED="\033[0;31m"
COLOR_BLUE="\033[0;34m"
COLOR_CYAN="\033[0;36m"
COLOR_RESET="\033[0m"
BOLD="\033[1m"
UNDERLINE="\033[4m"

# Funciones principales
# ===================

# Función de logging
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    mkdir -p "$LOG_DIR"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    case "$level" in
        "ERROR")
            echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $message" >&2
            ;;
        "WARNING")
            echo -e "${COLOR_YELLOW}[WARNING]${COLOR_RESET} $message"
            ;;
        "INFO")
            echo -e "${COLOR_BLUE}[INFO]${COLOR_RESET} $message"
            ;;
        *)
            echo "[$level] $message"
            ;;
    esac
}

# Función principal
main() {
    log "INFO" "=== Inicio ejecución $APP_NAME ==="
    
    # Tu código aquí
    
    log "INFO" "=== Fin ejecución $APP_NAME ==="
}

# Ejecutar main si el script no está siendo "sourced"
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

#### Convenciones de Naming

- **Variables**: `UPPER_CASE` para constantes, `lower_case` para variables locales
- **Funciones**: `snake_case` descriptivo
- **Archivos**: `kebab-case.sh` para scripts, `lowercase.py` para Python

#### Manejo de Errores

```bash
# Usar set -e para salir en errores
set -e

# Manejar errores específicos
if ! command -v herramienta >/dev/null 2>&1; then
    log "ERROR" "Herramienta no encontrada"
    exit 1
fi

# Verificar permisos
if [[ ! -w "$DIRECTORIO" ]]; then
    log "ERROR" "Sin permisos de escritura en $DIRECTORIO"
    exit 1
fi
```

### Estilo de Scripts Python

#### Estructura de Scripts Python

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nombre del Script - Descripción breve
=====================================

Script Name: nombre-del-script.py
Version: 1.0.0
Author: Tu Nombre <tu@email.com>
Created: YYYY-MM-DD HH:MM:SS
Updated: YYYY-MM-DD HH:MM:SS

Copyright (C) YYYY Tu Nombre

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import os
import logging
from pathlib import Path

# Configuración
SCRIPT_DIR = Path(__file__).parent.absolute()
LOG_DIR = Path.home() / ".logs"
LOG_FILE = LOG_DIR / "script-name.log"
APP_NAME = "Nombre de la Aplicación"
VERSION = "1.0.0"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal del script."""
    logger.info(f"=== Inicio ejecución {APP_NAME} ===")
    
    try:
        # Tu código aquí
        pass
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    
    logger.info(f"=== Fin ejecución {APP_NAME} ===")

if __name__ == "__main__":
    main()
```

## 🔄 Proceso de Desarrollo

### Flujo de Trabajo Git

#### 1. Configuración Inicial (Solo una vez)

```bash
# Configurar Git
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# Configurar editor
git config --global core.editor "vim"  # O tu editor preferido
```

#### 2. Flujo de Desarrollo Diario

```bash
# 1. Actualizar desde upstream
git fetch upstream
git checkout main
git merge upstream/main

# 2. Crear rama para nueva feature
git checkout -b feature/nombre-de-la-feature

# 3. Desarrollar y hacer commits
git add archivo.sh
git commit -m "FEAT: Agregar nueva funcionalidad"

# 4. Hacer push de la rama
git push origin feature/nombre-de-la-feature

# 5. Crear Pull Request en GitHub
```

#### 3. Convenciones de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Tipos de commit
FEAT:     # Nueva funcionalidad
FIX:      # Corrección de bug
REFACTOR: # Refactorización de código
IMPROVE:  # Mejora sin cambiar funcionalidad
DOCS:     # Documentación
STYLE:    # Formato, espacios, etc.
TEST:     # Tests
CHORE:    # Tareas de mantenimiento

# Formato
TIPO: Descripción breve (máximo 50 caracteres)

Descripción detallada opcional (máximo 72 caracteres por línea)

# Ejemplos
git commit -m "FEAT: Agregar instalador automático de Docker"
git commit -m "FIX: Corregir detección de sistema operativo en Ubuntu"
git commit -m "DOCS: Actualizar guía de instalación para desarrolladores"
```

### Testing

#### Testing Manual

```bash
# Verificar que el script funciona
./nuevo-script.sh --help

# Verificar en diferentes sistemas
./nuevo-script.sh --dry-run

# Verificar logs
tail -f ~/.logs/script-name.log
```

#### Testing de Integración

```bash
# Verificar que no rompe funcionalidad existente
./packages.sh --list base --dry-run

# Verificar permisos
./btfixperms.sh

# Verificar estructura del proyecto
find . -name "*.sh" -exec bash -n {} \;
```

### Documentación

#### Actualizar Documentación

1. **README.md**: Para cambios que afecten a usuarios
2. **docs/[herramienta].md**: Para documentación específica de herramientas
3. **Comentarios en código**: Para explicar lógica compleja

#### Estilo de Documentación

```markdown
# Título de la Sección

> **📖 [← Volver al README principal](../README.md)**

## 📖 Introducción

Descripción clara de qué hace la herramienta.

### Características Principales

- ✅ Característica 1
- ✅ Característica 2
- ✅ Característica 3

## 🚀 Instalación

Instrucciones de instalación paso a paso.

## 📝 Uso

Ejemplos de uso con código.

## 🚨 Solución de Problemas

Problemas comunes y soluciones.
```

## 📦 Sistema de Releases

### Visión General

Este proyecto usa un sistema de releases directo que se ejecuta **completamente** desde tu máquina local usando GitHub CLI. El script `create-release.sh` crea releases directamente en GitHub sin depender de workflows externos, y usa un sistema de configuración flexible para definir exactamente qué archivos se incluyen en cada release.

### 🛠️ Scripts de Gestión de Releases

El proyecto incluye scripts especializados para gestionar el ciclo completo de releases:

#### 📝 `create-release.sh` - Crear Releases

**Características:**

- ✅ Crea releases directamente usando GitHub CLI (sin workflows)
- ✅ Genera paquetes automáticamente con `release-builder.sh`
- ✅ Gestiona tags de Git automáticamente
- ✅ Sube assets de release
- ✅ Soporte para drafts y prereleases

**Opciones disponibles:**

- `--version, -v`: Versión del release (requerido)
- `--message, -m`: Mensaje del release (requerido)
- `--draft, -d`: Crear como draft
- `--prerelease, -p`: Marcar como prerelease
- `--no-tag`: No crear tag de Git
- `--no-push`: No hacer push automático

#### 🗑️ `delete-release.sh` - Eliminar Releases

**Características:**

- ✅ Elimina releases de GitHub de forma segura
- ✅ Opción de eliminar también el tag de Git
- ✅ Confirmación antes de eliminar
- ✅ Modo force para automatización
- ✅ Lista releases disponibles

**Opciones disponibles:**

- `--version, -v`: Versión del release a eliminar (requerido)
- `--delete-tag, -t`: También eliminar el tag de Git (local y remoto)
- `--force, -f`: No pedir confirmación
- `--list, -l`: Listar releases disponibles
- `--help, -h`: Mostrar ayuda

#### ⚙️ `release-builder.sh` - Generar Paquetes

**Características:**

- ✅ Genera paquetes tar.gz configurables
- ✅ Tres tipos de release: full, user, minimal
- ✅ Configuración flexible via YAML
- ✅ Validación de archivos y directorios
- ✅ Información detallada del paquete

### 🚀 Crear un Release

#### Método 1: Script Automatizado (Recomendado)

```bash
# Crear release básico
./create-release.sh --version v1.0.0 --message "Primera versión estable"

# Crear release como draft
./create-release.sh -v v1.1.0 -m "Nueva funcionalidad" --draft

# Crear prerelease
./create-release.sh -v v1.2.0-beta -m "Versión beta" --prerelease

# Crear sin hacer push automático
./create-release.sh -v v1.0.1 -m "Bug fixes" --no-push
```

#### Método 2: Gestión de Releases

```bash
# Listar releases disponibles
./delete-release.sh --list

# Eliminar solo el release (mantener tag)
./delete-release.sh --version v1.0.0

# Eliminar release y tag
./delete-release.sh --version v1.0.0 --delete-tag

# Eliminar sin confirmación
./delete-release.sh --version v1.0.0 --delete-tag --force
```

#### Método 3: Completamente Manual

```bash
# 1. Actualizar versión
echo "v1.0.0" > VERSION
git add VERSION
git commit -m "Bump version to v1.0.0"

# 2. Crear tag
git tag -a v1.0.0 -m "Release version v1.0.0"

# 3. Hacer push
git push origin main
git push origin v1.0.0

# 4. Crear paquete manualmente usando el sistema de configuración
./release-builder.sh --type user --output /tmp/bintools-v1.0.0
tar -czf bintools-v1.0.0.tar.gz bintools-v1.0.0/

# 5. Crear release en GitHub
# Ve a https://github.com/maurorosero/bintools/releases/new
# Adjunta el archivo bintools-v1.0.0.tar.gz
```

### 📁 Sistema de Configuración de Archivos

#### Archivo de Configuración (`configs/release-config.yml`)

El sistema usa un archivo de configuración que te permite definir exactamente qué archivos se incluyen en cada tipo de release:

```yaml
# Archivos principales que se incluyen en todos los releases
main_files:
  - packages.sh
  - micursor.py
  - pymanager.sh
  - fix_hdmi_audio.sh
  - videoset.sh
  - nxcloud-backup.sh
  - hexroute

# Directorios que se incluyen completos
directories:
  - configs

# Archivos de configuración del proyecto
config_files:
  - VERSION
  - RELEASE_INFO

# Archivos opcionales por categoría
optional_files:
  documentation:
    - README.md
    - LICENSE
  
  development:
    - .gitignore
    - docs/developers.md
    - create-release.sh
    - release-builder.sh
    - bintools-manager.sh
  
  project_config:
    - .github/workflows/release.yml
    - configs/release-config.yml

# Configuración por tipo de release
release_types:
  full:
    include_main: true
    include_directories: true
    include_config: true
    include_optional:
      - documentation
      - development
      - project_config
  
  user:
    include_main: true
    include_directories: true
    include_config: true
    include_optional:
      - documentation
  
  minimal:
    include_main: true
    include_directories: true
    include_config: true
    include_optional: []

# Configuración por defecto
default_release_type: "user"

# Patrones de exclusión
exclude_patterns:
  - "*.tmp"
  - "*.log"
  - ".DS_Store"
  - "Thumbs.db"
  - "*.swp"
  - "*.swo"
  - "*~"
  - ".env"
  - "*.key"
  - "*.pem"
  - "*.p12"
```

### 🚀 Tipos de Release

#### 1. **Release Completo (`full`)**

Incluye todos los archivos del proyecto:

- ✅ Archivos principales
- ✅ Directorios de configuración
- ✅ Archivos de configuración
- ✅ Documentación completa
- ✅ Archivos de desarrollo
- ✅ Configuración del proyecto

**Uso:**

```bash
./release-builder.sh --type full --output /tmp/full-release
```

#### 2. **Release de Usuario (`user`)**

Incluye solo lo necesario para usar bintools:

- ✅ Archivos principales
- ✅ Directorios de configuración
- ✅ Archivos de configuración
- ✅ Documentación básica
- ❌ Archivos de desarrollo
- ❌ Configuración del proyecto

**Uso:**

```bash
./release-builder.sh --type user --output /tmp/user-release
```

#### 3. **Release Mínimo (`minimal`)**

Incluye solo los archivos esenciales:

- ✅ Archivos principales
- ✅ Directorios de configuración
- ✅ Archivos de configuración
- ❌ Documentación
- ❌ Archivos de desarrollo
- ❌ Configuración del proyecto

**Uso:**

```bash
./release-builder.sh --type minimal --output /tmp/minimal-release
```

### 🔧 Personalización de Archivos

#### Agregar Nuevos Archivos

Para agregar un nuevo archivo al release:

1. **Archivo principal** (siempre incluido):

```yaml
main_files:
  - packages.sh
  - micursor.py
  - nuevo-script.sh  # ← Agregar aquí
```

1. **Archivo opcional** (según categoría):

```yaml
optional_files:
  documentation:
    - README.md
    - nuevo-doc.md  # ← Agregar aquí
```

#### Crear Nueva Categoría

```yaml
optional_files:
  nueva_categoria:
    - archivo1.sh
    - archivo2.py
    - archivo3.md
```

#### Modificar Tipos de Release

```yaml
release_types:
  mi_tipo_personalizado:
    include_main: true
    include_directories: true
    include_config: true
    include_optional:
      - nueva_categoria
      - documentation
```

### 📋 Uso del Script de Configuración

#### Opciones Disponibles

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--type` | Tipo de release | `--type user` |
| `--output` | Directorio de salida | `--output /tmp/release` |
| `--config` | Archivo de configuración | `--config custom.yml` |
| `--verbose` | Modo verbose | `--verbose` |
| `--help` | Mostrar ayuda | `--help` |

#### Ejemplos de Uso

```bash
# Release básico
./release-builder.sh --type user --output /tmp/release

# Release completo con verbose
./release-builder.sh --type full --output /tmp/full-release --verbose

# Usar configuración personalizada
./release-builder.sh --type minimal --config mi-config.yml --output /tmp/minimal

# Ver ayuda
./release-builder.sh --help
```

### 📦 Estructura del Paquete

Cada release incluye según el tipo configurado:

```text
bintools-v1.0.0/
├── packages.sh              # Instalador de paquetes
├── micursor.py              # Gestor de Cursor IDE
├── pymanager.sh             # Gestor de Python
├── fix_hdmi_audio.sh        # Solucionador de audio HDMI
├── videoset.sh              # Configurador de pantalla
├── nxcloud-backup.sh        # Gestor de Nextcloud
├── hexroute                 # Convertidor de rutas
├── configs/                 # Configuraciones de paquetes
│   ├── base.pkg
│   ├── devs.pkg
│   ├── orgs.pkg
│   └── user.pkg
├── VERSION                  # Archivo de versión
└── RELEASE_INFO             # Información del release
```

### 🎯 Flujo de Trabajo Recomendado

#### Para Releases Estables

```bash
# 1. Actualizar código
git add .
git commit -m "FEAT: Add new feature"

# 2. Crear release
./create-release.sh --version v1.1.0 --message "Nueva funcionalidad agregada"

# 3. Verificar en GitHub
# Ve a https://github.com/maurorosero/bintools/releases
```

#### Para Releases de Prueba

```bash
# 1. Crear prerelease
./create-release.sh -v v1.1.0-beta -m "Versión beta para testing" --prerelease

# 2. Testing interno del paquete antes de release estable
./release-builder.sh --type user --output /tmp/test-release --config configs/release-config.yml

# 3. Si todo está bien, crear release estable
./create-release.sh -v v1.1.0 -m "Versión estable"
```

### 🔍 Verificación de Release

#### Verificar Release en GitHub

```bash
# Verificar que el release fue creado
curl -s https://api.github.com/repos/maurorosero/bintools/releases/latest | jq '.tag_name'

# Verificar que los assets están disponibles
curl -s https://api.github.com/repos/maurorosero/bintools/releases/latest | jq '.assets[].name'

# Verificar que el workflow completó exitosamente
# Ve a: https://github.com/maurorosero/bintools/actions
```

#### Verificar en GitHub

1. Ve a [Releases](https://github.com/maurorosero/bintools/releases)
2. Verifica que el release aparezca
3. Descarga el archivo tar.gz
4. Verifica el contenido

### 🎯 Ventajas del Sistema

- ✅ **Flexibilidad**: Define exactamente qué incluir
- ✅ **Mantenibilidad**: Un solo archivo de configuración
- ✅ **Reutilización**: Misma configuración para diferentes tipos
- ✅ **Escalabilidad**: Fácil agregar nuevos archivos/categorías
- ✅ **Consistencia**: Mismo proceso para todos los releases
- ✅ **Exclusión**: Patrones para excluir archivos no deseados
- ✅ **Automatización**: Workflow se ejecuta solo desde tu script local
- ✅ **Control total**: Solo se ejecuta cuando tú lo decides

### 🐛 Solución de Problemas

#### Error: "GitHub CLI no está instalado"

```bash
# Instalar GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

#### Error: "Tag ya existe"

```bash
# Eliminar tag local
git tag -d v1.0.0

# Eliminar tag remoto
git push origin :refs/tags/v1.0.0

# Crear nuevo tag
./create-release.sh --version v1.0.0 --message "Release corregido"
```

#### Error: "No se puede hacer push"

```bash
# Verificar estado de git
git status

# Hacer pull antes del push
git pull origin main

# Intentar push nuevamente
git push origin main
```

#### Error: "Archivo no encontrado"

```bash
# Verificar que el archivo existe
ls -la archivo.sh

# Verificar la configuración
grep -A 5 "main_files:" configs/release-config.yml
```

#### Error: "Directorio no encontrado"

```bash
# Verificar que el directorio existe
ls -la directorio/

# Verificar la configuración
grep -A 5 "directories:" configs/release-config.yml
```

#### Error: "Configuración no válida"

```bash
# Verificar sintaxis YAML
python3 -c "import yaml; yaml.safe_load(open('configs/release-config.yml'))"
```

### 📋 Requisitos Técnicos

#### Para `create-release.sh` y `delete-release.sh`

**Herramientas requeridas:**

- ✅ **GitHub CLI (`gh`)**: Para interactuar con GitHub API
- ✅ **Git**: Para gestión de tags y repositorio
- ✅ **jq**: Para procesamiento JSON (solo create-release.sh)

**Configuración necesaria:**

```bash
# Verificar GitHub CLI
gh auth status

# Si no está autenticado
gh auth login

# Verificar permisos
gh api user
```

**Permisos del token GitHub CLI:**

- `repo`: Acceso completo al repositorio
- `write:packages`: Para subir assets
- `delete_repo`: Para eliminar releases (solo delete-release.sh)

#### Para `release-builder.sh`

**Herramientas requeridas:**

- ✅ **tar**: Para crear paquetes
- ✅ **Python 3**: Para validación YAML (opcional)

## 📞 Soporte

Si tienes problemas con el desarrollo:

1. **Verificar autenticación**: `gh auth status`
2. **Verificar permisos**: Revisa que tu token tenga los scopes necesarios
3. **Verificar configuración**: `python3 -c "import yaml; yaml.safe_load(open('configs/release-config.yml'))"`
4. **Verificar archivos**: Asegúrate de que los archivos/directorios existen
5. **Revisar patrones**: Verifica los patrones de exclusión en release-config.yml
6. **Abrir Issue**: [GitHub Issues](https://github.com/maurorosero/bintools/issues)

---

**📖 [← Volver al README principal](../README.md)**
