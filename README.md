# bintools - Herramientas Esenciales del Sistema

![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)

Una colección de herramientas esenciales para instalar paquetes, resolver problemas del sistema y automatizar tareas comunes en Linux y macOS.

## 🚀 ¿Qué es bintools?

bintools es un conjunto de scripts que automatizan tareas comunes del sistema operativo. Desde resolver problemas de audio HDMI hasta instalar paquetes masivamente, bintools simplifica el trabajo diario con Linux y macOS.

## ✨ Características Principales

- 🛠️ **Resolución de Problemas**: Solución automática de problemas comunes (audio HDMI, pantallas, backups)
- 📦 **Instalación Masiva**: Un comando instala múltiples herramientas organizadas por categoría
- 🖥️ **Multiplataforma**: Funciona en Ubuntu, Debian, Fedora, CentOS, Arch Linux y macOS
- 🔧 **Detección Automática**: Identifica tu sistema y usa el método correcto automáticamente
- 🖥️ **Detección de GUI**: Filtrado automático de paquetes GUI en servidores headless
- 🔐 **Sudo Inteligente**: Una sola contraseña para toda la instalación
- 🐍 **Gestión de Python**: Entornos virtuales profesionales con configuración automática
- 🎯 **Editor con IA**: Instalación y configuración completa de Cursor IDE
- 🌐 **Herramientas de Red**: Conversión de rutas y configuración DHCP automática
- 🛡️ **Modo Seguro**: Prueba antes de ejecutar para evitar cambios no deseados
- 🚀 **Instalador Universal**: Sistema de instalación sin dependencias de Git

## 🛠️ Herramientas Incluidas

### 📋 Herramientas

- **`packages.sh`**: Instalador masivo de paquetes organizados por categoría
- **`fix_hdmi_audio.sh`**: Soluciona problemas de audio HDMI con PipeWire automáticamente
- **`videoset.sh`**: Configura resoluciones de pantalla y detecta monitores automáticamente
- **`nxcloud-backup.sh`**: Gestor completo de backups y configuración de Nextcloud
- **`hexroute`**: Convierte rutas de red a formato hexadecimal para configuración DHCP
- **`git-tokens.py`**: Gestor seguro de tokens de autenticación para servicios Git
- **`bw-send.sh`**: Envío seguro extendido con múltiples canales de distribución
- **`bw-ghpersonal.sh`**: Obtención automática de token GitHub desde Bitwarden
- **`odevs-install.sh`**: Instalador automático de odoodevs con múltiples opciones
- **`micursor.py`**: Gestor de Cursor IDE con configuración automática
- **`pymanager.sh`**: Configuración profesional de entornos Python
- **`repo-install.sh`**: Gestor de repositorios OS-específicos
- **`bintools-manager.sh`**: Gestor principal de bintools
- **`btfixperms.sh`**: Gestor de permisos para desarrollo

### 📚 Documentación

- **`docs/secrets.md`**: Guía completa de gestión segura de secretos
- **`docs/bw.md`**: Documentación completa de Bitwarden CLI
- **`docs/bw-send.md`**: Guía completa de bw-send.sh (envío seguro extendido)
- **`docs/odoodevs.md`**: Documentación completa de odoodevs
- **`docs/cursor-sync-guide.md`**: Guía para sincronizar contexto de Cursor con Nextcloud
- **`docs/RELEASE.md`**: Guía de releases para desarrolladores

## 🚀 Instalación

### Pre-requisitos del Sistema

Para instalar y usar bintools, necesitas:

- **Sistema operativo compatible**: Ubuntu, Debian, Fedora, CentOS, Arch Linux, macOS
- **Acceso a internet**: Para descargar herramientas y paquetes
- **Permisos de administrador**: Para instalar paquetes del sistema
- **Shell compatible**: Bash o Zsh

### Métodos de Instalación

#### Método 1: Instalación Automática (Recomendado)

```bash
# Instalación rápida en tu sistema
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash

# Instalación en directorio personalizado
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --dir /opt/bintools
```

**Lógica de Directorio de Instalación:**

- **Por defecto**: `~/bin` (`$HOME/bin`)
- **Si `~/bin` existe**: Pregunta si extender ese directorio o usar `~/bintools`
- **Si `~/bin` no existe**: Se crea `~/bin` automáticamente
- **Directorio personalizado**: Usa `--dir /ruta/personalizada`
- **PATH automático**: Se agrega automáticamente a tu PATH en `~/.bashrc` o `~/.zshrc`

**Opciones Avanzadas del Instalador:**

```bash
# Instalación con opciones específicas
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --version v1.1.0 --dir /opt/bintools

# Ver qué haría sin instalar
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --dry-run --verbose
```

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--version` | Versión específica a instalar | `--version v1.1.0` |
| `--dir` | Directorio de instalación personalizado | `--dir /opt/bintools` |
| `--extend-bin` | Extender directorio ~/bin existente | `--extend-bin` |
| `--dry-run` | Solo mostrar qué se haría | `--dry-run` |
| `--verbose` | Mostrar información detallada | `--verbose` |

#### Método 2: Clonado Manual (Para Desarrollo)

```bash
# Clonar el repositorio
git clone https://github.com/maurorosero/bintools.git
cd bintools

# Establecer permisos correctos y seguros para desarrollo
./btfixperms.sh

# ¡Listo! Ya puedes usar las herramientas para desarrollo
```

**Nota para Desarrolladores:**

- Ejecuta `./btfixperms.sh` después de clonar para establecer permisos correctos
- Vuelve a ejecutarlo si experimentas problemas de permisos
- El script solo afecta el ambiente de desarrollo, no es necesario para usuarios finales

### Verificación de Instalación

```bash
# Verificar que bintools está instalado
packages.sh --version

# Verificar que las herramientas están en el PATH
which packages.sh

# Listar herramientas disponibles
ls ~/bin/bintools*  # O el directorio donde instalaste
```

### Actualización

```bash
# Actualizar a la última versión
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash

# O si ya tienes bintools instalado
bintools-update  # Si está disponible
```

## 📖 Descripción de Herramientas

### 📦 Instalador de Paquetes (`packages.sh`)

Instala automáticamente herramientas esenciales según tu sistema operativo con gestión inteligente de actualizaciones.

**¿Qué puede instalar?**

- **Básicas**: curl, git, wget, python, vim, nano, herramientas de red
- **Desarrollo**: compiladores, Node.js, Visual Studio Code, herramientas de construcción
- **Productividad**: LibreOffice, navegadores, aplicaciones de comunicación
- **DevOps**: AWS CLI, Azure CLI, Terraform, Ansible, herramientas de red
- **Contenedores**: Docker completo, Podman, Kubernetes local
- **Arduino**: IDE, herramientas AVR, comunicación serial, IoT
- **Personalizadas**: herramientas que tú elijas

**Características avanzadas:**

- ✅ **Instalación de gestores**: Instala automáticamente `yay` (AUR) y `snapd`
- ✅ **Detección inteligente**: Usa el gestor de paquetes correcto para tu sistema
- ✅ **Detección de GUI**: Filtra automáticamente paquetes GUI en servidores headless
- ✅ **Sudo inteligente**: Una sola contraseña para toda la instalación
- ✅ **Modo de prueba**: Verifica qué se instalaría antes de ejecutar
- ✅ **Gestión de repositorios**: Sistema OS-específico para configurar repositorios externos

**📖 Documentación completa**: Para información detallada sobre instalación, uso, listas disponibles y configuración de repositorios, consulta la [guía completa de packages.sh](docs/packages.md) y la [documentación de repo-install.sh](docs/repo.md).

### 🔧 Herramientas de Sistema

#### `fix_hdmi_audio.sh` - Solucionador de Audio HDMI

**Problema que resuelve**: Audio HDMI que no funciona en Linux con PipeWire

**Pre-requisitos:**

- Sistema Linux con PipeWire instalado
- Permisos para reiniciar servicios de audio

**¿Qué hace?**

- Detecta automáticamente dispositivos HDMI
- Configura PipeWire para usar el dispositivo correcto
- Reinicia servicios de audio automáticamente
- Funciona con múltiples monitores y tarjetas de audio

**Uso**: `./fix_hdmi_audio.sh`

#### `videoset.sh` - Configurador de Pantalla

**Problema que resuelve**: Resoluciones incorrectas o monitores no detectados

**Pre-requisitos:**

- Sistema Linux con X11 o Wayland
- Herramientas base del sistema (`packages.sh --list base`)

**¿Qué hace?**

- Detecta automáticamente todos los monitores conectados
- Lista resoluciones disponibles
- Configura la resolución óptima automáticamente
- Soporte para múltiples monitores

**Uso**: `./videoset.sh --auto`

#### `nxcloud-backup.sh` - Gestor Completo de Nextcloud

**Problema que resuelve**: Gestión integral de configuración y sincronización de Nextcloud

**Pre-requisitos:**

- Nextcloud Desktop instalado y configurado
- Herramientas base del sistema (`packages.sh --list base`)

**¿Qué hace?**

- **🛡️ Backups automáticos**: Respalda toda la configuración de Nextcloud de forma segura
- **🔄 Restauración completa**: Restaura configuración con un solo comando
- **🔗 Configuración de sync**: Guía para sincronizar carpeta `~/secure` con servidor
- **🧹 Limpieza inteligente**: Elimina configuraciones duplicadas automáticamente
- **🗑️ Limpieza de archivos sync**: Elimina archivos `.nextcloudsync.log` y `.sync_*.db*` no deseados
- **📋 Gestión de versiones**: Maneja múltiples backups con timestamps únicos
- **🌐 Sincronización automática**: Los backups se sincronizan con tu servidor Nextcloud

**Funcionalidades principales:**

```bash
# Crear backup de configuración
./nxcloud-backup.sh --backup

# Listar todos los backups disponibles  
./nxcloud-backup.sh --list

# Restaurar backup específico (mantiene autenticación)
./nxcloud-backup.sh --restore backup_name

# Configurar sincronización de carpeta segura
./nxcloud-backup.sh --secure

# Limpiar entradas duplicadas de configuración
./nxcloud-backup.sh --clean

# Limpiar archivos de sincronización no deseados (.nextcloudsync.log, .sync_*.db*)
./nxcloud-backup.sh --clean-sync
```

#### `hexroute` - Convertidor de Rutas de Red

**Problema que resuelve**: Configuración de rutas de red en formato hexadecimal para DHCP

**Pre-requisitos:**

- Herramientas base del sistema (`packages.sh --list base`)
- Conocimientos básicos de redes y DHCP

**¿Qué hace?**

- Convierte rutas CIDR a formato hexadecimal
- Genera configuración DHCP automáticamente
- Soporte para múltiples gateways
- Formato compatible con routers empresariales

**Uso**: `./hexroute 172.16.0.0/16 gw 192.168.1.1`

### 🔐 Gestión de Secretos

### 🔐 Gestor de Tokens Git (`git-tokens.py`)

Gestiona tokens de autenticación de servicios Git de forma segura usando el keyring del sistema.

**Pre-requisitos:**

- Python 3.6+ instalado en el sistema
- Herramientas base del sistema (`packages.sh --list base`)

**¿Qué servicios soporta?**

- **GitHub**: Tokens para API, repositorios privados, GitHub CLI
- **GitLab**: Tokens para API, CI/CD, repositorios privados
- **Forgejo**: Tokens para API y repositorios
- **Gitea**: Tokens para API y repositorios
- **Bitbucket Cloud**: Tokens para API y repositorios
- **Bitbucket Server**: Tokens para API y repositorios on-premise

**¿Qué hace?**

- 🔐 **Almacenamiento seguro**: Usa keyring del sistema operativo
- 🔄 **Encriptación automática**: Tokens encriptados con base64
- 👤 **Gestión por usuario**: Soporte para múltiples usuarios por servicio
- 🏷️ **Etiquetado inteligente**: Formato `[servicio]-[modo]-[uso]`
- 🔍 **Búsqueda fácil**: Lista y recupera tokens por servicio
- 🗑️ **Eliminación segura**: Borra tokens sin dejar rastros

**Uso básico:**

```bash
# Ver ayuda completa
./git-tokens.py --help

# Guardar token
./git-tokens.py set github-dev-api --token ghp_xxxxx

# Recuperar token
./git-tokens.py get github-dev-api
```

Para información completa, ejemplos detallados y mejores prácticas, consulta la [documentación completa de gestión de secretos](docs/secrets.md).

### 🔐 Scripts de Bitwarden CLI

Herramientas para integrar Bitwarden CLI con otras aplicaciones y automatizar tareas de gestión de contraseñas.

**¿Qué es Bitwarden?**

Bitwarden es un gestor de contraseñas de código abierto y gratuito que permite almacenar, sincronizar y gestionar credenciales de forma segura. Incluye una interfaz de línea de comandos (CLI) que permite automatizar tareas de gestión de contraseñas y tokens desde scripts y aplicaciones.

**¿Para qué sirve?**

- 🔐 **Gestión segura de contraseñas**: Almacena credenciales encriptadas
- 🔄 **Sincronización multiplataforma**: Acceso desde cualquier dispositivo
- 🛠️ **Automatización**: CLI para integrar con scripts y aplicaciones
- 📤 **Envío seguro**: Compartir archivos y texto de forma temporal y segura
- 🔑 **Gestión de tokens**: Almacenar y recuperar tokens de API automáticamente

**Instalación de Bitwarden CLI:**

```bash
# Instalar Bitwarden CLI automáticamente
./packages.sh --list bwdn

# Esto instalará:
# - Bitwarden Desktop (cliente oficial)
# - Bitwarden CLI (bw) para automatización
# - Configuración básica del entorno
```

Para información completa sobre configuración, uso avanzado y mejores prácticas, consulta la [documentación completa de Bitwarden CLI](docs/bw.md) y la [guía de gestión de secretos](docs/secrets.md).

#### `bw-send.sh` - Envío Seguro Extendido

Wrapper que extiende la funcionalidad de `bw send` para permitir el envío seguro de secretos a través de múltiples canales de comunicación (Telegram, email, WhatsApp), no solo vía texto en consola.

**Pre-requisitos:**

- Bitwarden CLI (`bw`) instalado y configurado (`packages.sh --list bwdn`)
- Herramientas base del sistema (`packages.sh --list base`)

**¿Qué hace?**

- 📁 **Envía archivos**: Sube archivos individuales o múltiples archivos
- 📝 **Envía texto**: Comparte texto directamente desde línea de comandos
- ⏰ **Expiración configurable**: Establece cuándo expira el enlace (por defecto: 2 días)
- 🔒 **Contraseña opcional**: Protege el enlace con contraseña
- 🔢 **Límite de accesos**: Controla cuántas veces se puede acceder al enlace
- 📋 **Notas**: Agrega notas descriptivas al envío
- 📱 **Múltiples canales**: Telegram, email, WhatsApp (en desarrollo)

**Uso básico:**

```bash
# Ver ayuda completa
./bw-send.sh --help

# Enviar texto simple
./bw-send.sh --text "Información confidencial"

# Enviar archivo
./bw-send.sh --file documento.pdf
```

Para información completa sobre todas las opciones, canales de envío y ejemplos detallados, consulta la [documentación completa de bw-send](docs/bw-send.md) y la [guía de gestión de secretos](docs/secrets.md).

#### `bw-ghpersonal.sh` - Obtención Automática de Token GitHub

Obtiene automáticamente el token de GitHub personal desde Bitwarden y lo guarda en `git-tokens.py`.

**¿Qué hace?**

- 🔍 **Búsqueda automática**: Busca el token de GitHub en Bitwarden usando el usuario actual
- 👤 **Usuario dinámico**: Reemplaza automáticamente "[TU_USUARIO]" por tu usuario actual en mayúsculas
- 🔄 **Integración completa**: Usa pipe para pasar el token directamente a `git-tokens.py`
- ✅ **Verificación**: Confirma que el token se guardó correctamente

**Uso:**

```bash
# Obtener y guardar token de GitHub personal automáticamente
./bw-ghpersonal.sh
```

**¿Cómo funciona?**

1. Obtiene tu usuario actual del sistema (`whoami`)
2. Convierte el usuario a mayúsculas (ej: `[TU_USUARIO]` → `[TU_USUARIO EN MAYÚSCULA]`)
3. Busca en Bitwarden el campo `"[TU_USUARIO] FULL TOKEN"` en el item "GITHUB" (el elemento en tu vault debe llamarse exactamente "GITHUB")
4. Extrae el token usando `grep` y `sed`
5. Pasa el token a `git-tokens.py set github-personal --token -`
6. Confirma que se guardó exitosamente

**Requisitos:**

- Tener instalado bintools (contiene `git-tokens.py`) e instalados los pre-requisitos (`packages.sh --list base`)
- Bitwarden CLI (`bw`) instalado y configurado (`packages.sh --list bwdn`)
- Item llamado exactamente "GITHUB" en Bitwarden/Vaultwarden con campo `"[TU_USUARIO] FULL TOKEN"`

### 🚀 Herramientas de Desarrollo

#### `odevs-install.sh` - Instalador de OdooDevs

Instalador automático de odoodevs, un entorno de desarrollo profesional para Odoo con herramientas, configuraciones y scripts optimizados. Incluye setup completo con Docker, herramientas de debugging y configuraciones predefinidas.

Para mayor información, consulta la [documentación completa de odoodevs](docs/odoodevs.md).

**Pre-requisitos:**

- Herramientas base del sistema (`packages.sh --list base`)
- Herramientas de desarrollo (`packages.sh --list devs`)
- Docker instalado y configurado (`packages.sh --list dckr`)

**Características:**

- 🛠️ **Instalación automática**: Setup completo con un solo comando
- 🔄 **Múltiples tipos**: Soporte para desarrolladores, usuarios y versiones específicas
- 🔐 **Protocolos flexibles**: HTTPS y SSH para clonado del repositorio
- 📁 **Workspace personalizable**: Directorio de trabajo configurable
- ✅ **Validación completa**: Verificación de dependencias y conexiones

**Ejemplos de uso:**

```bash
# Instalación para desarrolladores
./odevs-install.sh --type devs

# Instalación última versión
./odevs-install.sh --type latest

# Instalación versión específica
./odevs-install.sh --type version --version v1.0.0

# Con workspace personalizado
./odevs-install.sh --type devs --workspace mi-odoo
```

Para información completa, consulta la [documentación detallada](docs/odoodevs.md).

#### `pymanager.sh` - Gestor de Entornos Python

Gestor completo de entornos virtuales Python con instalación automática, creación de entornos y gestión de dependencias. Simplifica el desarrollo Python con herramientas modernas y configuración automática.

Para mayor información, consulta la [documentación completa de pymanager](docs/pymanager.md).

**Pre-requisitos:**

- Python 3.6+ instalado en el sistema
- pip (gestor de paquetes Python)
- Herramientas base del sistema (`packages.sh --list base`)
- Herramientas de desarrollo (`packages.sh --list devs`)

**Características:**

- 🐍 **Instalación automática de Python**: Detecta e instala versiones requeridas
- 🌐 **Gestión de entornos virtuales**: Creación, activación y gestión automática
- 📦 **Gestión de dependencias**: Instalación y actualización de paquetes
- 🔧 **Configuración automática**: Setup completo de entorno de desarrollo
- ✅ **Multiplataforma**: Compatible con Linux, macOS y Windows
- 🛠️ **Integración con herramientas**: Compatible con pip, poetry, pipenv

## 🤝 Contribuir

¿Tienes una herramienta que te gustaría agregar? ¡Es fácil!

1. Fork el proyecto
2. Agrega tu herramienta al archivo correspondiente en `configs/`
3. Haz un Pull Request

## 📝 Licencia

GNU General Public License v3.0 - Software libre que puedes usar, modificar y distribuir bajo los términos de la GPL v3.

## 👨‍💻 Autor

### Mauro Rosero Pérez

- Website: [mauro.rosero.one](https://mauro.rosero.one)
- Email: [mauro.rosero@gmail.com](mailto:mauro.rosero@gmail.com)
- GitHub: [@maurorosero](https://github.com/maurorosero)

## 📚 Documentación

Para información detallada sobre desarrollo:

- **[Guía de Releases](docs/RELEASE.md)** - Creación y gestión de releases (desarrolladores)

## 🙏 Agradecimientos

- Comunidad de desarrolladores de Linux y macOS
- Mantenedores de los repositorios de paquetes
- Desarrolladores de las herramientas incluidas

---

⭐ **¿Te ha sido útil? ¡Dale una estrella al proyecto!**

## 📞 Soporte

Si tienes problemas o sugerencias:

1. Abre un [Issue](https://github.com/maurorosero/bintools/issues)
2. Visita [mauro.rosero.one](https://mauro.rosero.one) para más información
3. Contacta al autor por email
4. Revisa la documentación de las herramientas específicas
