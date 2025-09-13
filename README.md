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
- 🐍 **Gestión de Python**: Entornos virtuales profesionales con configuración automática
- 🎯 **Editor con IA**: Instalación y configuración completa de Cursor IDE
- 🌐 **Herramientas de Red**: Conversión de rutas y configuración DHCP automática
- 🛡️ **Modo Seguro**: Prueba antes de ejecutar para evitar cambios no deseados
- 🚀 **Instalador Universal**: Sistema de instalación sin dependencias de Git

## 🛠️ Herramientas Incluidas

### 🔧 Herramientas de Sistema

Herramientas especializadas para resolver problemas comunes y automatizar tareas del sistema.

- **`fix_hdmi_audio.sh`**: Soluciona problemas de audio HDMI con PipeWire automáticamente
- **`videoset.sh`**: Configura resoluciones de pantalla y detecta monitores automáticamente
- **`nextcloud-installer.sh`**: Gestiona backups y restauración completa de Nextcloud
- **`hexroute`**: Convierte rutas de red a formato hexadecimal para configuración DHCP

### 📦 Instalador de Paquetes (`packages.sh`)

Instala automáticamente herramientas esenciales según tu sistema operativo con gestión inteligente de actualizaciones.

**¿Qué puede instalar?**

- **Básicas**: curl, git, wget, python, vim, nano, herramientas de red
- **Desarrollo**: compiladores, Node.js, Visual Studio Code, herramientas de construcción
- **Productividad**: LibreOffice, navegadores, aplicaciones de comunicación
- **Personalizadas**: herramientas que tú elijas

**Características avanzadas:**

- ✅ **Instalación de gestores**: Instala automáticamente `yay` (AUR) y `snapd`
- ✅ **Detección inteligente**: Usa el gestor de paquetes correcto para tu sistema
- ✅ **Modo de prueba**: Verifica qué se instalaría antes de ejecutar
- ✅ **Fallback automático**: Usa snap como alternativa si el gestor preferido no está disponible

### 🎯 Gestor de Cursor IDE (`micursor.py`)

Instala y configura Cursor IDE (editor de código con IA) automáticamente.

**¿Qué hace?**

- Descarga e instala la última versión de Cursor
- Configura reglas MDC para mejor experiencia
- Crea backups de tu configuración
- Funciona en Linux, macOS y Windows

### 🐍 Gestor de Python (`pymanager.sh`)

Configura entornos Python de forma profesional.

**¿Qué hace?**

- Instala Python y herramientas necesarias
- Crea entornos virtuales para proyectos
- Gestiona paquetes Python de forma organizada
- Configura alias para acceso rápido

## 🚀 Instalación Rápida

### Método 1: Instalador Automático (Recomendado)

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
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --version v1.0.0 --dir /opt/bintools

# Ver qué haría sin instalar
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --dry-run --verbose
```

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--version` | Versión específica a instalar | `--version v1.0.0` |
| `--dir` | Directorio de instalación personalizado | `--dir /opt/bintools` |
| `--extend-bin` | Extender directorio ~/bin existente | `--extend-bin` |
| `--dry-run` | Solo mostrar qué se haría | `--dry-run` |
| `--verbose` | Mostrar información detallada | `--verbose` |

### Método 2: Clonado Manual (Para Desarrollo)

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

## 🔧 Gestión de Versiones

Una vez instalado, puedes gestionar `bintools` con el gestor de versiones incluido:

```bash
# Verificar versión instalada
bintools-manager.sh version

# Actualizar a la última versión
bintools-manager.sh update

# Instalar versión específica
bintools-manager.sh install v1.0.0

# Listar versiones disponibles  
bintools-manager.sh list

# Verificar integridad de la instalación
bintools-manager.sh check

# Ver información completa
bintools-manager.sh info

# Desinstalar completamente
bintools-manager.sh uninstall
```

## 📖 Uso Básico

### Resolver Problemas del Sistema

```bash
# Solucionar problemas de audio HDMI
./fix_hdmi_audio.sh

# Configurar resoluciones de pantalla automáticamente
./videoset.sh --auto

# Backup completo de Nextcloud
./nextcloud-installer.sh --backup

# Convertir rutas de red a formato hexadecimal
./hexroute 172.16.0.0/16 gw 192.168.1.1
```

### Instalar Herramientas Esenciales

```bash
# Ver qué se instalaría (recomendado primero)
./packages.sh --list base --dry-run

# Instalar herramientas básicas
./packages.sh --list base

# Instalar herramientas de desarrollo
./packages.sh --list devs

# Instalar herramientas de organización
./packages.sh --list orgs

# Instalar herramientas personalizadas
./packages.sh --list user

# Instalar herramientas de virtualización (VirtualBox + Vagrant)
./packages.sh --list vbox

# Instalar herramientas de Nextcloud
./packages.sh --list cloud

# Instalar todo
./packages.sh --list all

# Instalar yay (AUR helper) en Arch Linux
./packages.sh --install-yay

# Instalar snapd en sistemas compatibles
./packages.sh --install-snap

# Instalar con información detallada
./packages.sh --list base --verbose
```

### Instalar Cursor IDE

```bash
# Instalar Cursor IDE
python micursor.py --install

# Crear backup de configuración
python micursor.py --backup-login
```

### Configurar Python

```bash
# Instalar Python completo
./pymanager.sh --install-python

# Crear entorno para un proyecto
./pymanager.sh --create mi-proyecto
```

## 🚀 Características Avanzadas del Instalador

### Gestión Inteligente de Paquetes

El instalador `packages.sh` incluye características avanzadas que lo hacen único:

#### **Modo de Prueba**

- ✅ Verifica qué se instalaría antes de ejecutar
- ✅ Permite revisar cambios antes de aplicarlos
- ✅ Evita instalaciones no deseadas

#### **Instalación de Gestores de Paquetes**

```bash
# Instalar yay (AUR helper) en Arch Linux
./packages.sh --install-yay

# Instalar snapd en sistemas compatibles
./packages.sh --install-snap
```

#### **Detección Inteligente**

- 🔍 Detecta automáticamente tu sistema operativo
- 🎯 Usa el gestor de paquetes correcto (apt, dnf, pacman, brew)
- 🔄 Cambia automáticamente a alternativas si el gestor preferido no está disponible

#### **Ejemplos de Uso**

```bash
# Ver qué se instalaría sin hacer cambios
./packages.sh --list base --dry-run

# Ver información detallada del proceso
./packages.sh --list devs --verbose
```

## 🖥️ Sistemas Soportados

| Sistema | Estado | Manejador de Paquetes | Características |
|---------|--------|----------------------|----------------|
| Ubuntu/Debian | ✅ Completo | apt, snap | Actualización automática, instalación de snapd |
| Fedora/CentOS | ✅ Completo | dnf, yum, snap | Actualización automática, instalación de snapd |
| Arch Linux | ✅ Completo | pacman, yay, snap | Actualización automática, instalación de yay y snapd |
| macOS | ✅ Completo | brew, snap | Actualización automática, instalación de snapd |

## 📋 Listas de Paquetes Disponibles

El sistema detecta automáticamente todas las listas disponibles en `configs/`. Actualmente incluye:

### `base` - Paquetes Esenciales del Sistema

- curl, git, wget
- python3, python3-pip
- vim, nano
- jq, yq (procesadores de JSON/YAML)
- gnupg, dialog
- tree, rsync, net-tools
- gum, fzf (herramientas modernas)

### `devs` - Paquetes para Desarrollo

- Compiladores (gcc, g++)
- Herramientas de construcción (make, cmake)
- Node.js y npm
- Visual Studio Code
- Headers de desarrollo Python

### `orgs` - Paquetes para Organización y Productividad

- LibreOffice
- Navegadores (Firefox, Chromium)
- Thunderbird (correo)
- Discord, Slack
- Calibre (libros electrónicos)

### `user` - Paquetes Personalizados del Usuario

- htop (monitor de procesos)
- neofetch (info del sistema)
- bat, exa (herramientas modernas)
- Spotify

### `vbox` - VirtualBox y Vagrant para Virtualización

- VirtualBox (plataforma de virtualización)
- VirtualBox Extension Pack (extensiones)
- Vagrant (gestión de entornos virtualizados)

### `cloud` - Herramientas de Nextcloud

- Nextcloud Desktop (cliente oficial de escritorio)

### Crear Listas Personalizadas

Puedes crear tus propias listas agregando archivos `.pkg` en `configs/`:

```bash
# Crear lista personalizada
echo "# Mi lista de herramientas" > configs/mitools.pkg
echo "ubuntu:apt:htop:Monitor de procesos" >> configs/mitools.pkg

# Automáticamente disponible
./packages.sh --list mitools
```

## 🔧 Utilidades del Sistema Detalladas

### `fix_hdmi_audio.sh` - Solucionador de Audio HDMI

**Problema que resuelve**: Audio HDMI que no funciona en Linux con PipeWire

**¿Qué hace?**

- Detecta automáticamente dispositivos HDMI
- Configura PipeWire para usar el dispositivo correcto
- Reinicia servicios de audio automáticamente
- Funciona con múltiples monitores y tarjetas de audio

**Uso**: `./fix_hdmi_audio.sh`

### `videoset.sh` - Configurador de Pantalla

**Problema que resuelve**: Resoluciones incorrectas o monitores no detectados

**¿Qué hace?**

- Detecta automáticamente todos los monitores conectados
- Lista resoluciones disponibles
- Configura la resolución óptima automáticamente
- Soporte para múltiples monitores

**Uso**: `./videoset.sh --auto`

### `nextcloud-installer.sh` - Gestor de Nextcloud

**Problema que resuelve**: Backup y restauración de configuración Nextcloud

**¿Qué hace?**

- Crea backups completos de configuración
- Restaura configuración desde backup
- Gestiona archivos de configuración de forma segura
- Soporte para múltiples instancias

**Uso**: `./nextcloud-installer.sh --backup`

### `hexroute` - Convertidor de Rutas de Red

**Problema que resuelve**: Configuración de rutas de red en formato hexadecimal para DHCP

**¿Qué hace?**

- Convierte rutas CIDR a formato hexadecimal
- Genera configuración DHCP automáticamente
- Soporte para múltiples gateways
- Formato compatible con routers empresariales

**Uso**: `./hexroute 172.16.0.0/16 gw 192.168.1.1`

### `fixperms.sh` - Gestor de Permisos para Desarrollo

**Problema que resuelve**: Permisos incorrectos en archivos del proyecto después de clonar

**¿Qué hace?**

- Establece permisos seguros basándose en `configs/release-config.yml`
- Scripts ejecutables obtienen permisos 755 (rwxr-xr-x)
- Archivos de configuración obtienen permisos 644 (rw-r--r--)
- Detecta y protege archivos sensibles con permisos 600 (rw-------)
- Soporte para modo de prueba antes de aplicar cambios

**Uso**: `./fixperms.sh --verbose --dry-run`

## 🔧 Opciones Avanzadas

### Modo de Prueba (Dry-run)

```bash
# Ver exactamente qué se instalaría
./packages.sh --list base --dry-run
```

### Instalación Detallada

```bash
# Ver información detallada del proceso
./packages.sh --list devs --verbose
```

### Instalación Múltiple

```bash
# Instalar varias listas a la vez
./packages.sh --list base,devs,orgs
```

## 🐛 Solución de Problemas Comunes

### "Permisos insuficientes"

```bash
# Ejecutar con sudo si es necesario
sudo ./packages.sh --list base
```

### "OS no soportado"

- Verifica que tu distribución esté en la lista soportada
- El script detecta automáticamente Ubuntu, Debian, Fedora, CentOS, Arch y macOS

### "Paquete no encontrado"

- El script intentará automáticamente con snap como alternativa
- Si snap no está disponible, se mostrará un error claro

### "Python no encontrado"

```bash
# Instalar Python automáticamente
./pymanager.sh --install-python
```

### "Permisos insuficientes en desarrollo"

Si experimentas problemas con permisos de archivos en ambiente de desarrollo:

```bash
# Establecer permisos correctos para todos los archivos
./btfixperms.sh

# Ver qué cambios se aplicarían sin ejecutarlos
./btfixperms.sh --dry-run

# Ver información detallada del proceso
./btfixperms.sh --verbose
```

### "Versión no encontrada"

```bash
# Verificar versiones disponibles
bintools-manager.sh list

# Instalar versión específica válida
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --version v1.0.0
```

### "Error de instalación"

```bash
# Verificar instalación
bintools-manager.sh check

# Reinstalar completamente
bintools-manager.sh uninstall
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash

# Instalación con información detallada
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --verbose
```

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
