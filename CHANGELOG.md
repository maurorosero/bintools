<!-- markdownlint-disable MD024 -->
# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-09-20

### 🚀 Nueva Versión Mayor - Documentación y Testing Ágil

Versión 1.2.0 introduce una expansión significativa de la documentación del proyecto, incluyendo guías completas para desarrolladores, documentación y testing ágil, además de reconocimiento especial a las tecnologías de IA que han acelerado el desarrollo.

### ✨ Added

#### 📚 Documentación Completa para Desarrolladores

- **`docs/developers.md`**: Guía exhaustiva para desarrolladores
  - Instalación y configuración del entorno de desarrollo
  - Estructura completa del proyecto con explicaciones detalladas
  - Convenciones de código para scripts Bash y Python
  - Proceso de desarrollo con flujo de trabajo Git
  - Convenciones de commits usando Conventional Commits
  - Guía completa de releases y sistema de versionado
  - Integración de contenido de RELEASE.md en guía unificada
  - Scripts de gestión de releases: create-release.sh, delete-release.sh, release-builder.sh
  - Sistema de configuración de archivos con release-config.yml
  - Tipos de release: full, user, minimal
  - Flujos de trabajo recomendados para releases
  - Solución de problemas comunes en desarrollo
  - Proporciona guía completa para nuevos contribuidores de código

#### 📖 Guía de Contribución de Documentación

- **`docs/documentation-guide.md`**: Guía completa para contribuir con documentación
  - Estilo y formato estándar del proyecto
  - Proceso paso a paso para crear/mejorar documentación
  - Convenciones de estructura y navegación
  - Checklist de calidad y revisión
  - Tipos de contribuciones: guías de herramientas, tutoriales, troubleshooting, mejoras del README, traducciones
  - Proceso de contribución en 4 fases: identificación, desarrollo, integración, pull request
  - Herramientas útiles para validación y desarrollo
  - Prioridades de contribución: alta y media prioridad
  - Mantiene consistencia con filosofía del proyecto de documentación concisa

#### 🧪 Guía de Testing Ágil

- **`docs/testing-guide.md`**: Guía completa de testing ágil
  - Metodologías ágiles: TDD, BDD, ATDD con explicaciones concisas
  - Proceso de testing continuo e iterativo
  - Estrategias de testing por niveles: unitario, integración, sistema
  - Testing multiplataforma específico para todos los SO soportados
  - Herramientas y entornos: máquinas virtuales, contenedores Docker, entornos cloud
  - Proceso de testing ágil en 5 fases: planificación, preparación, ejecución, análisis, seguimiento
  - Formato de reporte de testing estándar
  - Criterios de calidad para cobertura y calidad del testing
  - Solución de problemas comunes y herramientas de testing automatizado
  - Integra metodologías modernas con estrategias específicas para bintools

#### 🔗 Sincronización de Cursor IDE

- **`docs/cursor-sync-guide.md`**: Guía para sincronizar contexto de IA de Cursor
  - Configuración de sincronización usando Nextcloud
  - Script de sincronización automatizada
  - Automatización con cron e inotify
  - Verificación y solución de problemas
  - Respaldos automáticos y restauración
  - Optimización de archivos grandes (state.vscdb)

#### 🚀 Instalador de OdooDevs

- **`odevs-install.sh`**: Instalador automático de odoodevs
  - Soporte para tres tipos de instalación: devs, latest, version
  - Protocolos HTTPS y SSH configurables
  - Workspace personalizable (workdevs por defecto)
  - Integración completa con Docker
  - Pre-requisitos: base, devs, dckr packages
  - Documentación completa en `docs/odoodevs.md`

### 🔄 Changed

#### 📖 Reestructuración Completa del README

- **Sección "Contribuir" expandida**:
  - Nueva subsección "💻 Código" con tipos de contribución claros
  - Nueva subsección "📚 Documentación" con proceso de contribución
  - Nueva subsección "🧪 Testing" con metodologías ágiles
  - Referencias a guías completas en docs/

- **Sección "Instalación" mejorada**:
  - Pre-requisitos del sistema claramente definidos
  - Métodos de instalación con lógica de directorio explicada
  - Opciones avanzadas del instalador documentadas
  - Verificación y actualización con bintools-manager.sh

- **Pre-requisitos agregados**:
  - Todos los scripts ahora tienen pre-requisitos explícitos
  - Referencias a packages.sh para instalación de dependencias
  - Docker y herramientas específicas documentadas

#### 👨‍💻 Reconocimiento de Autores

- **Cursor IDE como coautor**:
  - Agregado como coautor oficial del proyecto
  - Información de contacto y descripción incluida
  - Reconocimiento del impacto en el desarrollo mediante vibe coding

#### 🙏 Agradecimientos Especiales

- **Agradecimiento especial a Cursor IDE**:
  - Reconocimiento de la plataforma y motores de IA
  - Destacar la aceleración del desarrollo mediante vibe coding
  - Enfatizar la colaboración sinérgica entre humano e IA
  - Agregar equipos de desarrollo de Cursor IDE a la lista de agradecimientos

#### 🗑️ Limpieza de Estructura

- **Sección Documentación eliminada**:
  - Removida sección redundante del nivel principal
  - Mantenidas referencias en sección Contribuir
  - README más limpio y enfocado

### 🔧 Fixed

#### 📝 Correcciones de Linting

- **Errores de markdown corregidos**:
  - Líneas en blanco alrededor de listas y títulos
  - Múltiples líneas en blanco consecutivas
  - Formato consistente en toda la documentación
  - Enlaces bidireccionales funcionando correctamente

#### 🔗 Enlaces y Navegación

- **Enlaces de retorno agregados**:
  - Todos los documentos en docs/ tienen enlace de retorno al README
  - Navegación bidireccional mejorada
  - Consistencia en formato de enlaces

#### 🛠️ Mejoras en Herramientas de Gestión

- **`delete-release.sh` mejorado**:
  - Nueva opción `--tag-only` para eliminar solo tags sin afectar releases
  - Validación de opciones mutuamente excluyentes (--delete-tag y --tag-only)
  - Mensajes informativos mejorados para distinguir entre acciones
  - Útil para casos donde solo el tag está causando problemas
  - Mantiene compatibilidad con funcionalidad existente

#### 🔐 Mejoras en Gestión de Tokens GitHub

- **`bw-ghpersonal.sh` completamente refactorizado**:
  - Nueva función `--get`: Obtiene token desde Bitwarden y lo guarda en git-tokens.py
  - Nueva función `--login`: Autentica GitHub CLI con token guardado usando `gh auth login --with-token`
  - Nueva función `--help`: Muestra ayuda completa (comportamiento por defecto)
  - Sincronización automática con Bitwarden (`bw sync`) para datos actualizados
  - Detección mejorada de errores de contraseña maestra y campos faltantes
  - Uso de `jq` para extracción robusta de tokens completos
  - Validaciones mejoradas para existencia de campos y tokens
  - Comportamiento por defecto seguro (mostrar ayuda en lugar de ejecutar automáticamente)
  - Separación clara de funcionalidades en funciones modulares
  - Mejor experiencia de usuario con opciones explícitas

#### 📚 Actualización de Documentación

- **README.md actualizado**:
  - Descripción actualizada de `bw-ghpersonal.sh`: "Gestión completa de tokens GitHub"
  - Funcionalidades documentadas: `--get`, `--login`, `--help`
  - Ejemplos de uso actualizados con opciones específicas
  - Requisitos actualizados (incluyendo GitHub CLI)

- **`docs/secrets.md` actualizado**:
  - Sección `bw-ghpersonal.sh` completamente actualizada
  - Funcionalidades detalladas con todas las opciones
  - Ejemplos de uso con opciones específicas
  - Configuración actualizada en sección de desarrolladores

- **`docs/documentation-guide.md` corregido**:
  - Error de linting MD047 corregido (nueva línea al final del archivo)
  - Estructura verificada y coherente

#### 🧹 Limpieza de Archivos

- **Archivos temporales eliminados**:
  - `docs/packages.md.backup` eliminado
  - Archivos de diagnóstico temporales eliminados
  - Mantenimiento de estructura de proyecto limpia

#### 🛠️ Mejoras en Gestión de Versiones

- **`bintools-manager.sh` mejorado**:
  - Referencias relativas en lugar de listas absolutas de comandos
  - Ejemplos del help actualizados para usar nombre del comando (`bintools-manager`) en lugar de `$0`
  - Verificación dinámica de permisos de ejecución usando `find` en lugar de listas hardcodeadas
  - Verificación dinámica de archivos principales usando `release-config.yml` en lugar de lista hardcodeada
  - Extracción automática de archivos principales desde configuración YAML
  - Información de comandos disponibles ahora referencia al README.md
  - Mejor experiencia de usuario con ejemplos más claros y consistentes
  - Sistema de verificación completamente dinámico y mantenible

#### 📝 Correcciones del Changelog

- **Reorganización y corrección de fechas**:
  - Fecha de v1.2.0 corregida de `2025-01-27` a `2025-09-20`
  - Eliminada versión inexistente v1.1.3 del changelog
  - Contenido de herramientas de gestión de secretos movido correctamente a v1.1.2
  - Estructura de changelog reorganizada y consistente
  - Todas las fechas actualizadas y verificadas

- **Configuración de releases actualizada**:
  - `configs/release-config.yml` actualizado con nuevos archivos de documentación
  - Agregadas guías: developers.md, documentation-guide.md, testing-guide.md
  - Agregadas guías de herramientas: packages.md, pymanager.md, repo.md, bw-send.md
  - Agregado `pritunl-vpn.py` a archivos principales
  - Comentarios descriptivos actualizados para todas las nuevas guías

### 📋 Requisitos Técnicos

#### Para Usuarios - v1.2.0

- **Sistema**: Ubuntu, Debian, Fedora, CentOS, Arch Linux, macOS
- **Herramientas**: curl o wget para instalación
- **Pre-requisitos**: Definidos por script específico
- **Documentación**: Acceso completo a guías especializadas

#### Para Desarrolladores - v1.2.0

- **GitHub CLI**: Para gestión de releases
- **Git**: Para control de versiones
- **jq**: Para procesamiento JSON
- **Python 3**: Para herramientas Python
- **Docker**: Para odoodevs (opcional)

### 🔗 Enlaces

- **Release**: [v1.2.0](https://github.com/maurorosero/bintools/releases/tag/v1.2.0)
- **Documentación**: [README.md](README.md)
- **Guía de Desarrolladores**: [docs/developers.md](docs/developers.md)
- **Guía de Documentación**: [docs/documentation-guide.md](docs/documentation-guide.md)
- **Guía de Testing**: [docs/testing-guide.md](docs/testing-guide.md)
- **Sincronización Cursor**: [docs/cursor-sync-guide.md](docs/cursor-sync-guide.md)
- **OdooDevs**: [docs/odoodevs.md](docs/odoodevs.md)
- **Autores**: [Mauro Rosero Pérez](https://mauro.rosero.one) y [Cursor IDE](https://cursor.sh)

## [1.1.2] - 2025-09-14

### ✨ Added

#### 🔐 Herramientas de Gestión de Secretos

- **`bw-send.sh`**: Envío seguro de archivos y texto mediante Bitwarden Send
  - Soporte para envío de archivos y texto plano
  - Configuración de expiración personalizable (1, 7, 30 días, etc.)
  - Protección con contraseña opcional
  - Límite de accesos configurable
  - Notas adicionales para contexto
  - Integración completa con Bitwarden CLI

- **`bw-ghpersonal.sh`**: Obtención automática de tokens GitHub desde Bitwarden
  - Recuperación automática de tokens GitHub desde Bitwarden
  - Integración con `git-tokens.py` para almacenamiento seguro
  - Configuración automática de credenciales Git
  - Soporte para múltiples cuentas GitHub
  - Autenticación transparente para operaciones Git

- **`git-tokens.py`**: Gestión avanzada de tokens Git usando keyring del sistema
  - Soporte para múltiples servicios Git: GitHub, GitLab, Gitea, Forgejo, Bitbucket
  - Modos cloud y on-premise para servicios compatibles
  - Almacenamiento seguro usando keyring del sistema operativo
  - Gestión de tokens por uso (personal, work, empresa, etc.)
  - Comandos: `set`, `get`, `list`, `delete`, `services`
  - Integración con `bw-ghpersonal.sh` para flujo automatizado

#### 📚 Documentación Completa de Gestión de Secretos

- **`docs/secrets.md`**: Documentación exhaustiva sobre gestión segura de secretos
  - Introducción a la importancia de la gestión segura de contraseñas
  - Guía completa de Vaultwarden (alternativa open-source a Bitwarden)
  - Comparación detallada entre Bitwarden y Vaultwarden
  - Información sobre servidor público `vault.vaultwarden.net`
  - Mejores prácticas para desarrolladores y equipos DevOps
  - Gestión de 2FA mediante Bitwarden CLI
  - Importancia de la gestión CLI para equipos de desarrollo
  - Cómo `bintools` contribuye al manejo seguro de contraseñas
  - Ejemplos prácticos y casos de uso reales

### 🔄 Changed

#### 📦 Configuración de Releases Actualizada

- **`configs/release-config.yml`**: Actualización completa para incluir herramientas de secretos
  - Agregadas herramientas de secrets a archivos principales:
    - `bw-send.sh`: Envío seguro de archivos y texto
    - `bw-ghpersonal.sh`: Obtención automática de tokens GitHub
    - `git-tokens.py`: Gestión de tokens Git usando keyring
  - Incluido directorio `docs/` para documentación completa
  - Nueva sección `secrets_tools` en archivos opcionales
  - Asegurado que herramientas de secrets estén disponibles en todos los tipos de release:
    - **full**: Incluye documentación y herramientas de secrets
    - **user**: Incluye documentación y herramientas de secrets  
    - **minimal**: Incluye herramientas de secrets
  - Agregada `docs/secrets.md` a archivos de documentación
  - Comentarios explicativos sobre las herramientas de gestión de secretos

### 🛡️ Security

#### Gestión Segura de Credenciales

- **Almacenamiento seguro**: Todas las herramientas usan keyring del sistema operativo
- **Integración con Bitwarden**: Flujo automatizado para recuperación de credenciales
- **Envío seguro**: `bw-send.sh` permite compartir información sensible de forma segura
- **Gestión de tokens**: `git-tokens.py` maneja tokens de autenticación de forma segura
- **Documentación de seguridad**: Guía completa sobre mejores prácticas de seguridad

### 🔧 Fixed

#### Corrección de Soporte de Paquetes para Arch Linux

- **Mejora completa en configuraciones de paquetes para Arch Linux**:
  - Corregidas configuraciones incorrectas en todos los archivos `.pkg`
  - Cambiado de paquetes `pacman` a `yay` (AUR) donde corresponde
  - Bitwarden: `arch:pacman:bitwarden` → `arch:yay:bitwarden-bin`
  - Docker: usar paquetes oficiales (docker, docker-compose, docker-buildx)
  - VirtualBox: usar virtualbox y virtualbox-host-dkms oficiales
  - Kubernetes: usar yay para kubectl-neat y kubectl-tree (AUR)
  - WhatsApp: usar whatsapp-for-linux-git (AUR)
  - ProjectLibre: usar yay (AUR)
  - Arduino: usar arduino-mk-git y stm32flash (AUR)
  - Google Cloud SDK: usar snap como alternativa
  - Arduino IDE: usar snap como alternativa completa
  - Eliminados fallbacks problemáticos con pacman para paquetes de AUR
  - Mensajes de error claros cuando yay no está instalado

### 📚 Documentation

#### Mejoras en Documentación

- **Actualización de documentación de releases**:
  - Mejorada precisión en fechas de releases
  - Corregida fecha del release v1.1.1 en CHANGELOG.md
  - Mejorada consistencia en documentación de cambios

### 📋 Requisitos Técnicos

#### Para Usuarios - v1.1.2

- **Sistema**: Ubuntu 18.04+, Debian 10+, Fedora 32+, CentOS 8+, Arch Linux, macOS 10.15+
- **Herramientas**: curl o wget para instalación
- **Bitwarden CLI**: Para funcionalidades de `bw-send.sh` y `bw-ghpersonal.sh`
- **Python 3**: Para `git-tokens.py` (incluye keyring)
- **Privilegios**: sudo (una sola vez) o usuario root con `--no-sudo`

#### Para Desarrolladores - v1.1.2

- **GitHub CLI**: Para gestión de releases (`gh auth login` requerido)
- **Git**: Para gestión de repositorio y tags
- **jq**: Para procesamiento JSON en scripts de release
- **tar**: Para creación de paquetes
- **Python 3**: Para validación YAML y herramientas de secrets

### 🔗 Enlaces

- **Release**: [v1.1.2](https://github.com/maurorosero/bintools/releases/tag/v1.1.2)
- **Documentación**: [README.md](README.md)
- **Gestión de Secretos**: [docs/secrets.md](docs/secrets.md)
- **Guía de Desarrollo**: [docs/RELEASE.md](docs/RELEASE.md)
- **Autor**: [Mauro Rosero Pérez](https://mauro.rosero.one)

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

### 🔧 Correcciones v1.1.1

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

### 📚 Documentación v1.1.1

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
