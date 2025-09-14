# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-09-14

### ✨ Added

#### Nueva Lista de Paquetes Bitwarden

- **Lista bwdn.pkg para instalación de Bitwarden**:
  - Gestor de contraseñas seguro y de código abierto
  - Múltiples métodos de instalación por sistema operativo
  - Snap para Ubuntu, Debian, Fedora, Arch Linux
  - Flatpak para todos los sistemas Linux
  - AUR (yay) para Arch Linux
  - Homebrew para macOS
  - CentOS usa solo Flatpak (evita problemas con Snap)
  - Lista disponible automáticamente en packages.sh --help

### 🔧 Fixed

#### Compatibilidad de Snap en packages.sh

- **Exclusión de macOS y CentOS de instalación de Snap**:
  - Agregadas verificaciones de compatibilidad antes de instalar snapd
  - macOS: Bloqueo completo con explicación detallada sobre incompatibilidad
  - CentOS: Advertencia con instrucciones manuales y recomendación de usar RPM nativo
  - Mejorados mensajes de error con explicaciones específicas
  - Actualizada documentación para reflejar sistemas soportados
  - Snap solo compatible con Ubuntu, Debian, Fedora y Arch Linux

#### Configuración de Release

- **Inclusión de bintools-manager.sh en todos los releases**:
  - Movido `bintools-manager.sh` de `optional_files.development` a `main_files`
  - Asegura que el gestor principal esté disponible en todos los métodos de instalación
  - Mejora la cobertura de instalación del gestor de versiones
  - Corrige problema donde `bintools-manager.sh` no se incluía en releases de tipo "user" y "minimal"

#### Funcionalidad --secure en nxcloud-backup.sh

- **Corrección de detección de carpetas disponibles**:
  - Arreglada lógica de búsqueda de números de carpeta en configuración
  - Mejorada expresión regular para detectar carpetas ocupadas
  - Cambio a configuración manual guiada siguiendo mejores prácticas de Nextcloud
  - Eliminada configuración automática problemática del archivo de configuración

- **Mejora en experiencia de usuario**:
  - Instrucciones detalladas para configuración manual desde interfaz gráfica
  - Opción para abrir automáticamente el cliente de Nextcloud
  - Guía paso a paso para configurar sincronización de carpeta `~/secure`
  - Seguimiento de recomendaciones oficiales de Nextcloud

#### Problema de Entrada Interactiva en install.sh

- **Corrección completa de entrada interactiva**:
  - Agregada detección robusta de modo no interactivo (curl | bash)
  - Verificación múltiple: stdin (-t 0), stdout (-t 1) y BASH_SOURCE
  - Separación completa de lógica de logging de función de decisión
  - Uso automático de ~/bin por defecto en modo no interactivo
  - Eliminado problema de cuelgue esperando entrada manual
  - Corregido output mezclado en instalaciones automáticas
  - Garantizado funcionamiento perfecto con `curl | bash`

### 📚 Documentation

#### Actualización del README

- **Nueva lista bwdn documentada**:
  - Agregada en sección de instalación de herramientas esenciales
  - Documentación completa con múltiples métodos de instalación
  - Tabla de sistemas soportados actualizada (macOS sin Snap)
  - Nota sobre compatibilidad de Snap por sistema operativo
  - Corregido error de linting MD032 en listas
  - Documentadas limitaciones de Snap en CentOS/RHEL y macOS

### 🔗 Enlaces

- **Release**: [v1.1.1](https://github.com/maurorosero/bintools/releases/tag/v1.1.1)
- **Documentación**: [README.md](README.md)
- **Guía de Desarrollo**: [docs/RELEASE.md](docs/RELEASE.md)
- **Autor**: [Mauro Rosero Pérez](https://mauro.rosero.one)

## [1.1.0] - 2025-09-14

### 🚀 Nueva Versión Mayor - Experiencia de Usuario Mejorada

Versión 1.1.0 introduce funcionalidades avanzadas de detección automática y gestión inteligente de privilegios para una experiencia de instalación completamente optimizada.

### ✨ Nuevas Características

#### 🖥️ Sistema de Detección Automática de GUI

- **Detección inteligente de ambiente gráfico**:
  - Variables de entorno: `DISPLAY`, `WAYLAND_DISPLAY`, `XDG_SESSION_TYPE`
  - Servidor X corriendo: Comando `xset`
  - Procesos gráficos: `Xorg`, `Xwayland`, `gnome-session`, `kde`, etc.
  - macOS: Variable `TERM_PROGRAM`

- **Identificación automática de paquetes GUI**:
  - Lista completa de paquetes GUI conocidos (navegadores, oficina, multimedia, etc.)
  - Detección por palabras clave en descripciones
  - Filtrado inteligente entre paquetes GUI y CLI

- **Filtrado automático de paquetes**:
  - Sin GUI detectado: Omite automáticamente paquetes GUI
  - Con GUI detectado: Instala todos los paquetes normalmente
  - Logging detallado de paquetes filtrados

#### 🔐 Gestión Inteligente de Privilegios Sudo

- **Sesión sudo única**:
  - Solicita privilegios sudo una sola vez al inicio (`sudo -v`)
  - Mantiene sesión activa en background automáticamente
  - Refresco automático cada 60 segundos
  - Evita múltiples solicitudes de contraseña

- **Función `maintain_sudo()`**:
  - Verificación de privilegios existentes
  - Solicitud única de autenticación
  - Proceso background para mantener sesión
  - Manejo de errores de autenticación

- **Función `sudo_cmd()`**:
  - Wrapper para todos los comandos sudo
  - Usa sesión mantenida automáticamente
  - Fallback a sudo normal si es necesario
  - Soporte para modo `--no-sudo`

#### 🎛️ Nuevas Opciones de Línea de Comandos

- **`--headless`**: Instala paquetes GUI incluso sin ambiente gráfico
- **`--no-sudo`**: Ejecuta sin privilegios sudo (para usuarios root)

#### 📦 Nuevas Listas de Paquetes Especializadas

- **`kube.pkg`**: Toolkit completo para desarrollo local de Kubernetes
  - Clusters locales: `minikube`, `kind`, `k3d`
  - CLI mejorado: `kubectl` + extensiones (`kubectl-neat`, `kubectl-tree`)
  - Interfaz interactiva: `k9s`
  - Monitoreo y debugging: `stern`
  - Herramientas de productividad: `kubectx`, `kubens`, `helm`, `kustomize`

- **`wapp.pkg`**: Cliente oficial de WhatsApp para Linux
  - Cliente oficial: `whatsapp-for-linux` (snap)

- **`pdmn.pkg`**: Toolkit completo para Podman
  - Motor: `podman`, `podman-compose`
  - Networking: `slirp4netns`, `uidmap`, `fuse-overlayfs`
  - Utilidades: `containers-common`, `skopeo`, `buildah`, `crun`

- **`dckr.pkg`**: Toolkit completo para Docker
  - Engine: `docker-ce`, `docker-ce-cli`, `containerd.io`
  - Plugins: `docker-compose-plugin`, `docker-buildx-plugin`, `docker-scan-plugin`
  - Utilidades: `docker-dockerfile`, `docker-compose` (V1 & V2)

- **`dkrc.pkg`**: Docker CLI remoto (sin engine local)
  - CLI: `docker-ce-cli`, `docker-compose`, plugins
  - macOS: `docker-machine`, `docker-credential-helper`
  - Sin engine local: Excluye `docker-ce` y `containerd.io`

- **`ardu.pkg`**: Toolkit completo para desarrollo con Arduino
  - IDE: `arduino`, `arduino-cli`, `arduino-mk`
  - AVR tools: `avrdude`, `gcc-avr`, `avr-libc`, `avr-gcc`, `avr-binutils`
  - Comunicación serial: `picocom`, `minicom`, `cu`, `moserial`, `python3-serial`
  - IoT platforms: `platformio`
  - Flashing tools: `stm32flash`, `esptool`
  - Debugger: `openocd`

- **`dops.pkg`**: Toolkit DevOps optimizado
  - Cloud CLIs: `awscli`, `azure-cli`, `google-cloud-sdk`
  - Network analysis: `httpie`, `dnsutils`, `tcpdump`, `mtr`, `netcat`, `nmap`
  - Automation: `ansible`, `terraform`
  - Sin duplicados: Paquetes ya en `base.pkg` eliminados

#### 🔧 Mejoras en Listas Existentes

- **`orgs.pkg`**: Suite ofimática completa
  - LibreOffice completo con idiomas (ES/EN) y ayuda
  - Herramientas PDF avanzadas: `pdftk`, `ghostscript`, `poppler-utils`
  - OCR: `tesseract` con idiomas ES/EN
  - Suite gráfica: `GIMP`, `Inkscape`
  - Impresión: `cups`, `simple-scan`
  - Conectividad: `remmina`, `filezilla`
  - Diagramas: `drawio`
  - Gestión de proyectos: `ProjectLibre` con Java 11

- **`base.pkg`**: Herramientas esenciales expandidas
  - Terminal: `screen` (multiplexor)
  - USB: `usbutils` (incluye `lsusb`)
  - Markdown: `glow`, `mdcat`
  - CSV: `csvkit`
  - Hex: `hexyl`, `xxd`, `hexedit`

- **`devs.pkg`**: Herramientas de desarrollo optimizadas
  - Base de datos: `sqlite3`
  - Sin GUI: `sqlitebrowser` eliminado para enfoque CLI

### 🔄 Changed

#### Optimización del Sistema de Instalación

- **Gestión de privilegios mejorada**:
  - Todas las funciones de instalación actualizadas para usar `sudo_cmd()`
  - `install_package()`: Usa sesión sudo mantenida
  - `install_yay()`: Usa `sudo_cmd()` para dependencias
  - `install_snap()`: Usa `sudo_cmd()` para instalación

- **Gestores de paquetes optimizados**:
  - `apt`: `sudo_cmd apt install/update`
  - `dnf`: `sudo_cmd dnf install/update`
  - `yum`: `sudo_cmd yum install`
  - `pacman`: `sudo_cmd pacman -S`
  - `snap`: `sudo_cmd snap install`

#### Limpieza de Duplicados

- **`dops.pkg` optimizado**:
  - Eliminados paquetes duplicados con `base.pkg`
  - Removidos: `curl`, `wget`, `rsync`, `jq`, `yq`, `htop`, `iotop`
  - Removidos: `wireshark`, `docker-compose`, SSH tools
  - Removidos: `kubernetes-cli`, `helm`
  - Enfoque específico en DevOps sin duplicados

#### Separación de Responsabilidades

- **Configuración modular**:
  - `base.pkg`: Herramientas básicas del sistema
  - `dops.pkg`: DevOps básico (cloud, red, automatización)
  - `dckr.pkg`: Docker completo
  - `pdmn.pkg`: Podman completo
  - `kube.pkg`: Kubernetes local

### 🗑️ Removed

#### Limpieza de Paquetes Duplicados

- **De `dops.pkg`**:
  - Paquetes ya en `base.pkg`: `curl`, `wget`, `rsync`, `jq`, `yq`, `htop`, `iotop`
  - Herramientas GUI: `wireshark`
  - Orquestación: `docker-compose`
  - SSH: `ssh`, `openssh-clients`, `openssh-server`, `openssh`
  - Kubernetes: `kubernetes-cli`, `kubectl`, `helm`

- **De `devs.pkg`**:
  - GUI: `sqlitebrowser` (mantenido enfoque CLI)

### 🔧 Correcciones

#### Experiencia de Usuario

- **Instalación sin interrupciones**:
  - Una sola contraseña para toda la instalación
  - Sesión sudo mantenida automáticamente
  - Sin múltiples prompts de contraseña

- **Detección automática mejorada**:
  - Filtrado inteligente de paquetes GUI
  - Logging claro de paquetes omitidos
  - Override flexible con `--headless`

#### Compatibilidad

- **Soporte para contenedores**:
  - Modo `--no-sudo` para usuarios root
  - Detección automática de ambiente headless
  - Instalación optimizada para servidores

### 🛡️ Security

#### Gestión Segura de Privilegios

- **Sesión sudo mantenida**:
  - Refresco automático cada 60 segundos
  - Manejo seguro de expiración de sesión
  - Proceso background aislado

- **Modo sin privilegios**:
  - Opción `--no-sudo` para casos especiales
  - Ejecución directa sin prompts
  - Ideal para contenedores y automatización

### 📋 Requisitos Técnicos

#### Para Usuarios - v1.1.0

- **Sistema**: Ubuntu 18.04+, Debian 10+, Fedora 32+, CentOS 8+, Arch Linux, macOS 10.15+
- **Herramientas**: curl o wget para instalación
- **Privilegios**: sudo (una sola vez) o usuario root con `--no-sudo`

#### Para Desarrolladores - v1.1.0

- **GitHub CLI**: Para gestión de releases (`gh auth login` requerido)
- **Git**: Para gestión de repositorio y tags
- **jq**: Para procesamiento JSON en scripts de release
- **tar**: Para creación de paquetes
- **Python 3**: Para validación YAML (opcional)

### 🔗 Enlaces de la Versión

- **Release**: [v1.1.0](https://github.com/maurorosero/bintools/releases/tag/v1.1.0)
- **Documentación**: [README.md](README.md)
- **Guía de Desarrollo**: [docs/RELEASE.md](docs/RELEASE.md)
- **Autor**: [Mauro Rosero Pérez](https://mauro.rosero.one)

## [1.0.0] - 2025-09-14

### 🎉 Primera Versión Oficial

Primera versión estable de bintools con sistema completo de gestión de paquetes multi-plataforma y herramientas de sistema.

### ✨ Added - Primera Versión

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

### 🔄 Changed - Primera Versión

#### Migración del Sistema de Releases

- **Migración a GitHub CLI**: Reemplazado sistema de GitHub Actions por enfoque directo
- **Mejora de confiabilidad**: Eliminadas dependencias de workflows externos
- **Proceso simplificado**: Creación de releases completamente local

#### Gestión de Paquetes

- **Detección dinámica**: Las listas de paquetes se detectan automáticamente
- **Mejora de rendimiento**: Optimización en la detección de sistemas operativos
- **Fallback inteligente**: Mejor manejo de errores con snap como respaldo

### 🗑️ Removed - Primera Versión

#### Limpieza de Código

- **GitHub Actions workflow**: Eliminado `release.yml` obsoleto y problemático
- **Referencias obsoletas**: Removidas menciones a `nextcloud-installer.sh`
- **Código muerto**: Eliminadas 83 líneas de código no utilizado

### 🔧 Fixed - Primera Versión

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

### 🛡️ Security - Primera Versión

#### Gestión Segura

- **Confirmaciones obligatorias**: Antes de eliminar releases o tags
- **Validación de archivos**: Verificación de existencia antes de procesamiento
- **Permisos de desarrollo**: Script dedicado para manejo seguro de permisos

### 📋 Requisitos Técnicos - Primera Versión

#### Para Usuarios - Primera Versión

- **Sistema**: Ubuntu 18.04+, Debian 10+, Fedora 32+, CentOS 8+, Arch Linux, macOS 10.15+
- **Herramientas**: curl o wget para instalación

#### Para Desarrolladores - Primera Versión

- **GitHub CLI**: Para gestión de releases (`gh auth login` requerido)
- **Git**: Para gestión de repositorio y tags
- **jq**: Para procesamiento JSON en scripts de release
- **tar**: Para creación de paquetes
- **Python 3**: Para validación YAML (opcional)

### 🔗 Enlaces - Primera Versión

- **Release**: [v1.0.0](https://github.com/maurorosero/bintools/releases/tag/v1.0.0)
- **Documentación**: [README.md](README.md)
- **Guía de Desarrollo**: [docs/RELEASE.md](docs/RELEASE.md)
- **Autor**: [Mauro Rosero Pérez](https://mauro.rosero.one)

[1.0.0]: https://github.com/maurorosero/bintools/releases/tag/v1.0.0
