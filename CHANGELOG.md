# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-14

### 🎉 Primera Versión Oficial

Primera versión estable de bintools con sistema completo de gestión de paquetes multi-plataforma y herramientas de sistema.

### ✨ Added

#### 🚀 Sistema de Gestión de Releases

- **`create-release.sh`**: Script para crear releases automáticamente
  - Crea releases directamente usando GitHub CLI (sin workflows)
  - Genera paquetes automáticamente con `release-builder.sh`
  - Gestiona tags de Git automáticamente
  - Soporte para drafts y prereleases
  - Opciones: `--version`, `--message`, `--draft`, `--prerelease`, `--no-tag`, `--no-push`

- **`delete-release.sh`**: Script para eliminar releases de forma segura
  - Elimina releases de GitHub con confirmaciones
  - Opción de eliminar también el tag de Git (local y remoto)
  - Modo force para automatización
  - Lista releases disponibles
  - Opciones: `--version`, `--delete-tag`, `--force`, `--list`, `--help`

- **`release-builder.sh`**: Script para generar paquetes configurables
  - Genera paquetes tar.gz configurables
  - Tres tipos de release: full, user, minimal
  - Configuración flexible via YAML (`configs/release-config.yml`)
  - Validación de archivos y directorios

#### 📦 Instalador de Paquetes Multi-plataforma (`packages.sh`)

- **Soporte completo**: Ubuntu, Debian, Fedora, CentOS, Arch Linux, macOS
- **Gestores inteligentes**: apt, dnf, yum, pacman, yay (AUR), brew, snap (fallback)
- **Detección automática**: Sistema operativo y gestor de paquetes apropiado
- **Modo de prueba**: Verificación antes de instalar (`--dry-run`)
- **Instalación de gestores**: Automática de `yay` (AUR) y `snapd` según necesidad
- **Fallback inteligente**: Usa snap como alternativa si el gestor principal falla

#### 🗂️ Listas de Paquetes Dinámicas

- **`base.pkg`**: Herramientas esenciales del sistema (curl, git, wget, python, vim, etc.)
- **`devs.pkg`**: Herramientas de desarrollo (compiladores, IDEs, herramientas de build)
- **`orgs.pkg`**: Aplicaciones de productividad (LibreOffice, navegadores, comunicación)
- **`user.pkg`**: Paquetes personalizables por el usuario
- **`vbox.pkg`**: Herramientas de virtualización (VirtualBox, Vagrant)
- **`cloud.pkg`**: Herramientas de Nextcloud (nextcloud-desktop, nextcloud-client)

#### 💾 Gestión Completa de Nextcloud (`nxcloud-backup.sh`)

- **Backup automático**: Configuración completa del cliente Nextcloud
- **Restauración completa**: Mantiene configuraciones al restaurar
- **Configuración de sincronización**: Guía para configurar carpeta `~/secure`
- **Limpieza inteligente**: Elimina duplicados en configuración (`--clean`)
- **Limpieza de archivos sync**: Remueve archivos `.nextcloudsync.log`, `.sync_*.db*` (`--clean-sync`)
- **Opciones**: `--backup`, `--list`, `--restore`, `--secure`, `--clean`, `--clean-sync`
- **Ubicación**: Backups en `~/secure/nextcloud/`

#### 🔧 Herramientas de Sistema

- **`fix_hdmi_audio.sh`**: Solución automática para problemas de audio HDMI con PipeWire
- **`videoset.sh`**: Configuración inteligente de resoluciones de pantalla y detección de monitores
- **`hexroute`**: Conversor de rutas de red a formato hexadecimal para configuración DHCP
- **`pymanager.sh`**: Gestor completo de entornos Python
- **`micursor.py`**: Instalador y configurador de Cursor IDE con soporte MDC

#### 🏗️ Sistema de Configuración

- **`configs/release-config.yml`**: Configuración flexible para tipos de release
- **Detección dinámica**: Automática de todas las listas `.pkg` en `configs/`
- **Tipos configurables**: full, user, minimal con archivos específicos por tipo
- **Patrones de exclusión**: Configurables para archivos no deseados

#### 📚 Documentación Completa

- **`README.md`**: Documentación completa para usuarios finales
- **`docs/RELEASE.md`**: Guía completa para desarrolladores sobre gestión de releases
- **Instalación flexible**: Soporte para `~/bin`, `~/bintools` o directorio personalizado
- **Gestión de versiones**: Sistema completo de versionado con `bintools-manager.sh`

#### 🛠️ Herramientas de Desarrollo

- **`btfixperms.sh`**: Script para corregir permisos en ambiente de desarrollo
- **`install.sh`**: Instalador universal descargable vía curl/wget
- **`bintools-manager.sh`**: Gestor de versiones para actualizaciones automáticas

### 🔄 Changed

#### Migración del Sistema de Releases

- **Migración a GitHub CLI**: Reemplazado sistema de GitHub Actions por enfoque directo
- **Mejora de confiabilidad**: Eliminadas dependencias de workflows externos
- **Proceso simplificado**: Creación de releases completamente local

#### Gestión de Paquetes

- **Detección dinámica**: Las listas de paquetes se detectan automáticamente
- **Mejora de rendimiento**: Optimización en la detección de sistemas operativos
- **Fallback inteligente**: Mejor manejo de errores con snap como respaldo

### 🗑️ Removed

#### Limpieza de Código

- **GitHub Actions workflow**: Eliminado `release.yml` obsoleto y problemático
- **Referencias obsoletas**: Removidas menciones a `nextcloud-installer.sh`
- **Código muerto**: Eliminadas 83 líneas de código no utilizado

### 🔧 Fixed - Estabilidad y Configuración

#### Separación de Documentación

- **Separación de contenido**: Removido contenido de gestión de versiones del README.md hacia docs/RELEASE.md
- **Enfoque correcto**: README.md ahora 100% enfocado en usuarios finales
- **Eliminación de bintools-manager.sh**: Referencias de desarrollo removidas del README

#### Estabilidad del Sistema

- **Logs separados**: stderr/stdout correctamente separados en scripts de release
- **Captura de output**: Mejorada captura de rutas de paquetes en workflows
- **Formato de documentación**: Corregidos todos los errores de markdown linting
- **Referencias de configuración**: Actualizadas todas las referencias a archivos renombrados
- **Configuración YAML anidada**: Corregido `release-builder.sh` para procesar correctamente `optional_files.documentation`
- **Inclusión de documentación**: Los paquetes de release ahora incluyen correctamente README.md, LICENSE, y CHANGELOG.md
- **Parsing YAML mejorado**: Soporte para claves anidadas en la función `read_config()`

### 🛡️ Security

#### Gestión Segura

- **Confirmaciones obligatorias**: Antes de eliminar releases o tags
- **Validación de archivos**: Verificación de existencia antes de procesamiento
- **Permisos de desarrollo**: Script dedicado para manejo seguro de permisos

### 📋 Requisitos Técnicos

#### Para Usuarios

- **Sistema**: Ubuntu 18.04+, Debian 10+, Fedora 32+, CentOS 8+, Arch Linux, macOS 10.15+
- **Herramientas**: curl o wget para instalación

#### Para Desarrolladores

- **GitHub CLI**: Para gestión de releases (`gh auth login` requerido)
- **Git**: Para gestión de repositorio y tags
- **jq**: Para procesamiento JSON en scripts de release
- **tar**: Para creación de paquetes
- **Python 3**: Para validación YAML (opcional)

### 🔗 Enlaces

- **Release**: [v1.0.0](https://github.com/maurorosero/bintools/releases/tag/v1.0.0)
- **Documentación**: [README.md](README.md)
- **Guía de Desarrollo**: [docs/RELEASE.md](docs/RELEASE.md)
- **Autor**: [Mauro Rosero Pérez](https://mauro.rosero.one)

[1.0.0]: https://github.com/maurorosero/bintools/releases/tag/v1.0.0
