# Guía Completa de Usuario - packages.sh

## 📖 Introducción

`packages.sh` es un instalador masivo de paquetes multiplataforma que automatiza la instalación de herramientas esenciales según tu sistema operativo. Está diseñado para ser inteligente, eficiente y fácil de usar.

**⚠️ Importante**: Las listas de paquetes incluidas son una selección personal de herramientas de uso común, escogidas inicialmente por el autor según sus necesidades y experiencia. Pueden no incluir todas las herramientas que necesites, pero proporcionan una base sólida para comenzar.

### 🎯 Características Principales


- **🌍 Multiplataforma**: Compatible con Ubuntu, Debian, Fedora, CentOS, Arch Linux y macOS

- **🧠 Detección Inteligente**: Detecta automáticamente tu sistema operativo y ambiente gráfico

- **📦 Gestión de Paquetes**: Soporte para múltiples gestores (apt, dnf, yum, pacman, yay, brew, snap, flatpak)

- **🖥️ Detección GUI**: Filtra automáticamente paquetes GUI en servidores headless

- **🔐 Sudo Inteligente**: Una sola contraseña para toda la instalación

- **🧪 Modo de Prueba**: Verifica qué se instalaría antes de ejecutar

- **📋 Listas Organizadas**: Paquetes organizados por categorías funcionales

## 🖥️ Sistemas Operativos Soportados

### ✅ Sistemas Probados y Verificados

Estos sistemas han sido probados exhaustivamente y funcionan correctamente:

| Sistema Operativo | Versiones | Estado | Notas |
|------------------|-----------|---------|-------|
| **Ubuntu** | 20.04 LTS, 22.04 LTS, 23.10, 24.04 LTS | ✅ **Completamente Funcional** | Gestor: `apt`, `snap` |
| **Debian** | 11 (Bullseye), 12 (Bookworm) | ✅ **Completamente Funcional** | Gestor: `apt`, `snap` |
| **Arch Linux** | Rolling Release | ✅ **Completamente Funcional** | Gestor: `pacman`, `yay` |
| **Manjaro** | Rolling Release | ✅ **Completamente Funcional** | Gestor: `pacman`, `yay` |

### 🔄 Sistemas Teóricamente Compatibles

Estos sistemas deberían funcionar asumiendo que tienen el gestor de paquetes correcto, pero no han sido probados exhaustivamente:

| Sistema Operativo | Versiones | Estado | Gestor Requerido | Notas |
|------------------|-----------|---------|------------------|-------|
| **Fedora** | 38, 39, 40, 41 | 🔶 **Debería Funcionar** | `dnf`, `snap` | Requiere instalación manual de `snapd` |
| **CentOS** | 8, 9 | 🔶 **Debería Funcionar** | `yum`/`dnf` | Soporte limitado para `snap` |
| **RHEL** | 8, 9 | 🔶 **Debería Funcionar** | `yum`/`dnf` | Soporte limitado para `snap` |
| **openSUSE** | Leap 15.x, Tumbleweed | 🔶 **Debería Funcionar** | `zypper` | Requiere configuración manual |
| **Alpine Linux** | Latest | 🔶 **Debería Funcionar** | `apk` | Requiere configuración manual |
| **macOS** | 11+, 12+, 13+, 14+ | 🔶 **Debería Funcionar** | `brew` | Requiere Homebrew instalado |

### ❌ Sistemas No Soportados

Estos sistemas no son compatibles o no están soportados:

| Sistema Operativo | Razón | Alternativas |
|------------------|-------|--------------|
| **Windows** | No soporta gestores de paquetes Linux | WSL2 con Ubuntu/Debian |
| **FreeBSD** | Gestores de paquetes diferentes | Configuración manual |
| **OpenBSD** | Gestores de paquetes diferentes | Configuración manual |
| **NetBSD** | Gestores de paquetes diferentes | Configuración manual |
| **Solaris** | Arquitectura y gestores diferentes | Configuración manual |

### 🔧 Gestores de Paquetes por Sistema

#### Ubuntu/Debian

```bash

# Gestores principales
apt          # Gestor nativo (siempre disponible)
snap         # Instalable con --install-snap

# Comandos de verificación
apt --version
snap --version
```

#### Arch Linux/Manjaro

```bash

# Gestores principales
pacman       # Gestor nativo (siempre disponible)
yay          # Instalable con --install-yay

# Comandos de verificación
pacman --version
yay --version
```

#### Fedora

```bash

# Gestores principales
dnf          # Gestor nativo (siempre disponible)
snap         # Instalable con --install-snap

# Comandos de verificación
dnf --version
snap --version
```

#### CentOS/RHEL

```bash

# Gestores principales
yum/dnf      # Gestor nativo (siempre disponible)
snap         # Soporte limitado, no recomendado

# Comandos de verificación
yum --version
dnf --version
```

#### macOS

```bash

# Gestores principales
brew         # Requiere instalación previa

# Comandos de verificación
brew --version
```

### 🧪 Estado de Pruebas por Lista

| Lista | Ubuntu | Debian | Arch | Manjaro | Fedora | CentOS | macOS |
|-------|--------|--------|------|---------|--------|--------|-------|
| `base` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `devs` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `cloud` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `dckr` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `kube` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `orgs` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | ❌ |
| `user` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `vbox` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | ❌ |
| `wapp` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | ❌ |
| `bwdn` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `gums` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `pdmn` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `dops` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `dkrc` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |
| `ardu` | ✅ | ✅ | ✅ | ✅ | 🔶 | 🔶 | 🔶 |

**Leyenda:**

- ✅ **Probado y Funcional** - Verificado completamente
- 🔶 **Debería Funcionar** - No probado, pero compatible teóricamente
- ❌ **No Compatible** - Paquetes GUI o específicos del sistema
- 🚧 **WIP** - Work In Progress (en desarrollo)

### 🚧 Estado de Desarrollo (WIP)

**Nota importante**: Este proyecto está en constante desarrollo. Algunas funcionalidades pueden estar incompletas o en proceso de mejora.

#### Funcionalidades WIP


- **Soporte para openSUSE**: Configuración de `zypper` en desarrollo

- **Soporte para Alpine Linux**: Configuración de `apk` en desarrollo

- **Gestión de Flatpak**: Mejoras en detección y configuración

- **Soporte para más distribuciones**: Expansión a más sistemas Linux

- **Interfaz web**: Posible desarrollo de interfaz web para gestión

#### Mejoras Planificadas


- **Detección automática de gestores**: Mejor detección de gestores disponibles

- **Configuración automática de repositorios**: Setup automático de repositorios externos

- **Modo interactivo**: Interfaz interactiva para selección de paquetes

- **Sincronización de configuraciones**: Sincronización entre múltiples sistemas

- **Logs detallados**: Sistema de logging más avanzado

#### Contribuciones

Si encuentras problemas o tienes sugerencias para sistemas no probados, por favor:
1. Reporta el problema con detalles del sistema
2. Proporciona logs de la ejecución
3. Sugiere mejoras o correcciones

### 📋 Requisitos por Sistema

#### Ubuntu/Debian

```bash

# Requisitos mínimos
- Ubuntu 20.04+ o Debian 11+
- Acceso a repositorios oficiales
- Privilegios sudo

# Verificar compatibilidad
lsb_release -a
sudo apt update
```

#### Arch Linux/Manjaro

```bash

# Requisitos mínimos
- Arch Linux o Manjaro actualizado
- Repositorios oficiales configurados
- Privilegios sudo

# Verificar compatibilidad
cat /etc/os-release
sudo pacman -Sy
```

#### Fedora

```bash

# Requisitos mínimos
- Fedora 38+
- Repositorios oficiales configurados
- Privilegios sudo

# Verificar compatibilidad
cat /etc/fedora-release
sudo dnf check-update
```

#### CentOS/RHEL

```bash

# Requisitos mínimos
- CentOS 8+ o RHEL 8+
- Repositorios EPEL habilitados
- Privilegios sudo

# Verificar compatibilidad
cat /etc/redhat-release
sudo yum check-update
```

#### macOS

```bash

# Requisitos mínimos
- macOS 11+ (Big Sur o superior)
- Homebrew instalado
- Acceso a internet

# Verificar compatibilidad
sw_vers
brew --version
```

### ⚠️ Limitaciones y Consideraciones

#### Limitaciones Conocidas


- **Paquetes específicos del sistema**: Algunos paquetes pueden no estar disponibles en todas las distribuciones

- **Versiones de paquetes**: Las versiones pueden variar entre distribuciones

- **Dependencias**: Algunos paquetes pueden requerir dependencias adicionales no incluidas

- **Repositorios externos**: Algunos paquetes requieren repositorios adicionales no configurados automáticamente

#### Consideraciones de Seguridad


- **Privilegios sudo**: El script requiere privilegios de administrador

- **Repositorios externos**: Algunos paquetes provienen de repositorios no oficiales

- **Scripts de instalación**: Ejecuta comandos del sistema con privilegios elevados

- **Verificación**: Siempre revisa qué se va a instalar con `--dry-run`

#### Limitaciones de Gestores


- **Snap en CentOS/RHEL**: Soporte limitado y puede causar conflictos

- **yay en Arch**: Requiere instalación manual del AUR helper

- **brew en macOS**: Requiere instalación previa de Homebrew

- **flatpak**: No está instalado por defecto en todos los sistemas

#### Compatibilidad de Paquetes GUI


- **Servidores headless**: Los paquetes GUI se omiten automáticamente

- **Entornos de escritorio**: Algunos paquetes requieren entornos específicos

- **Dependencias gráficas**: Pueden requerir librerías gráficas adicionales

## 🚀 Instalación Rápida

### Método 1: Instalación Directa

```bash

# Descargar y ejecutar
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/packages.sh | bash -s -- --list base

# O clonar el repositorio completo
git clone https://github.com/maurorosero/bintools.git
cd bintools
./packages.sh --list base
```

### Método 2: Con bintools

```bash

# Si ya tienes bintools instalado
./packages.sh --list base
```

## 📋 Uso Básico

### Sintaxis General

```bash

./packages.sh [OPCIONES]
```

### Opciones Principales

| Opción | Descripción |
|--------|-------------|
| `-l, --list LISTA` | Lista de paquetes a instalar |
| `-d, --dry-run` | Solo mostrar qué se instalaría, sin instalar realmente |
| `-v, --verbose` | Mostrar información detallada |
| `--headless` | Instalar paquetes GUI incluso sin ambiente gráfico |
| `--no-sudo` | Ejecutar sin privilegios sudo (para usuarios root) |
| `--install-yay` | Instalar yay (AUR helper) en Arch Linux |
| `--install-snap` | Instalar snapd en sistemas compatibles |
| `-h, --help` | Mostrar ayuda completa |

## 📦 Listas de Paquetes Disponibles

### 📋 Lista Completa

```bash

# Ver todas las listas disponibles
./packages.sh --help
```

### 🏗️ Listas Principales

#### `base` - Paquetes Esenciales
Herramientas básicas del sistema y utilidades fundamentales.

```bash

./packages.sh --list base
```

**Incluye:**


- **Herramientas de red**: curl, wget, git

- **Lenguajes**: Python 3, pip, keyring

- **Procesamiento**: jq, yq

- **Seguridad**: gnupg, libsecret-tools

- **Editores**: vim, nano

- **Compresión**: unzip, p7zip-full

#### `devs` - Desarrollo
Herramientas esenciales para desarrollo de software.

```bash

./packages.sh --list devs
```

**Incluye:**


- **Compiladores**: build-essential, cmake, make, gcc, g++

- **JavaScript**: nodejs, npm, yarn, typescript, eslint

- **Python**: python3-dev, pip, virtualenv

- **Editores**: code (VS Code), vim, nano

- **Herramientas**: git, docker, vagrant

#### `cloud` - Cloud y DevOps
Herramientas para desarrollo en la nube y DevOps.

```bash

./packages.sh --list cloud
```

**Incluye:**


- **AWS**: awscli, aws-vault

- **Azure**: azure-cli

- **Google Cloud**: google-cloud-cli

- **Terraform**: terraform

- **Ansible**: ansible

- **Kubernetes**: kubectl, helm, k9s

#### `dckr` - Docker
Ecosistema completo de Docker y contenedores.

```bash

./packages.sh --list dckr
```

**Incluye:**


- **Docker**: docker-ce, docker-compose

- **Herramientas**: docker-desktop, lazydocker

- **Orquestación**: kubernetes, minikube

- **Monitoreo**: portainer

#### `kube` - Kubernetes
Herramientas especializadas para Kubernetes.

```bash

./packages.sh --list kube
```

**Incluye:**


- **CLI**: kubectl, kustomize

- **Gestores**: helm, k9s, kubectx

- **Desarrollo**: skaffold, tilt

- **Monitoreo**: prometheus, grafana

#### `orgs` - Ofimática
Aplicaciones de productividad y ofimática.

```bash

./packages.sh --list orgs
```

**Incluye:**


- **Oficina**: libreoffice, libreoffice-writer, libreoffice-calc

- **Navegadores**: firefox, chromium, brave

- **Comunicación**: thunderbird, evolution

- **Herramientas**: filezilla, remmina

#### `user` - Usuario
Paquetes personalizados y herramientas del usuario.

```bash

./packages.sh --list user
```

#### `vbox` - VirtualBox
VirtualBox y herramientas de virtualización.

```bash

./packages.sh --list vbox
```

**Incluye:**


- **VirtualBox**: virtualbox, virtualbox-ext-pack

- **Vagrant**: vagrant

- **Herramientas**: qemu, kvm

#### `wapp` - WhatsApp
WhatsApp para Linux y herramientas de mensajería.

```bash

./packages.sh --list wapp
```

#### `bwdn` - Bitwarden
Bitwarden CLI y herramientas de gestión de contraseñas.

```bash

./packages.sh --list bwdn
```

**Incluye:**


- **Bitwarden CLI**: bw

- **Herramientas**: bitwarden, vaultwarden

#### `gums` - Gum
Herramientas de línea de comandos modernas.

```bash

./packages.sh --list gums
```

#### `pdmn` - Productividad
Herramientas de productividad y gestión.

```bash

./packages.sh --list pdmn
```

#### `dops` - DevOps
Herramientas adicionales de DevOps.

```bash

./packages.sh --list dops
```

#### `dkrc` - Docker Compose
Herramientas específicas de Docker Compose.

```bash

./packages.sh --list dkrc
```

#### `ardu` - Arduino
Herramientas para desarrollo con Arduino.

```bash

./packages.sh --list ardu
```

## 🔧 Ejemplos de Uso

### Instalación Básica

```bash

# Instalar paquetes base
./packages.sh --list base

# Instalar múltiples listas
./packages.sh --list base,devs

# Instalar todo
./packages.sh --list all
```

### Modo de Prueba

```bash

# Ver qué se instalaría sin instalar realmente
./packages.sh --list base --dry-run

# Ver instalación detallada
./packages.sh --list devs --verbose
```

### Instalación en Servidores

```bash

# Instalar en servidor headless (sin GUI)
./packages.sh --list base,devs,cloud

# Forzar instalación de paquetes GUI en servidor
./packages.sh --list orgs --headless
```

### Instalación Específica por Sistema

#### Ubuntu/Debian
```bash

# Instalación básica
./packages.sh --list base

# Con snapd
./packages.sh --install-snap
./packages.sh --list base
```

#### Arch Linux
```bash

# Instalar yay primero
./packages.sh --install-yay

# Luego instalar paquetes
./packages.sh --list base,devs
```

#### macOS
```bash

# Instalar con Homebrew
./packages.sh --list base,devs
```

#### CentOS/RHEL
```bash

# Instalación básica
./packages.sh --list base

# Sin sudo (usuario root)
./packages.sh --list base --no-sudo
```

## 🧠 Características Avanzadas

### Detección Automática de GUI

El script detecta automáticamente si hay ambiente gráfico disponible:

```bash

# Variables de entorno verificadas
DISPLAY
WAYLAND_DISPLAY
XDG_SESSION_TYPE

# Servidores gráficos verificados
xset q
pgrep -x "Xorg|Xwayland|gnome-session|kde|xfce|mate|lxde|i3|sway"
```

**Comportamiento:**


- **Con GUI**: Instala todos los paquetes

- **Sin GUI**: Omite paquetes GUI automáticamente

- **Modo headless**: Instala todo incluyendo GUI

### Gestión Inteligente de Sudo

```bash

# Una sola contraseña para todo el proceso
./packages.sh --list base,devs,cloud

# Sin sudo (usuario root)
./packages.sh --list base --no-sudo
```

**Características:**

- Solicita sudo una sola vez al inicio
- Mantiene la sesión activa en background
- Evita múltiples solicitudes de contraseña

### Detección de Paquetes GUI

El script identifica automáticamente paquetes GUI:

```bash

# Paquetes GUI conocidos
firefox, chromium, libreoffice, gimp, vlc, thunderbird
code, android-studio, mysql-workbench, postman
zoom, teams, spotify, steam, notion, obsidian
```

**Palabras clave en descripción:**

- GUI, interfaz gráfica, escritorio, ventana
- aplicación, cliente, editor, visor, reproductor
- navegador, oficina, diseño, imagen, video, audio
- juego, chat, mensajería, correo, IDE

## 📁 Formato de Archivos de Configuración

### Estructura de Archivos .pkg

Los archivos de configuración están en `configs/` con formato:

```text
OS:Manejador:Paquete:Descripción
```

### Ejemplo de Archivo base.pkg

```bash

# Paquetes esenciales del sistema
# Formato: OS:Manejador:Paquete:Descripción

# Ubuntu/Debian
ubuntu:apt:curl:Herramienta para transferir datos desde servidores
ubuntu:apt:git:Sistema de control de versiones distribuido
ubuntu:apt:wget:Herramienta para descargar archivos desde la web

# Arch Linux
arch:pacman:curl:Herramienta para transferir datos desde servidores
arch:pacman:git:Sistema de control de versiones distribuido
arch:pacman:wget:Herramienta para descargar archivos desde la web

# macOS
macos:brew:curl:Herramienta para transferir datos desde servidores
macos:brew:git:Sistema de control de versiones distribuido
macos:brew:wget:Herramienta para descargar archivos desde la web
```

### Gestores de Paquetes Soportados

| Gestor | Sistemas | Descripción |
|--------|----------|-------------|
| `apt` | Ubuntu, Debian | Gestor nativo de paquetes |
| `dnf` | Fedora | Gestor moderno de paquetes |
| `yum` | CentOS, RHEL | Gestor tradicional de paquetes |
| `pacman` | Arch Linux | Gestor nativo de Arch |
| `yay` | Arch Linux | Helper para AUR |
| `brew` | macOS | Homebrew para macOS |
| `snap` | Ubuntu, Debian, Fedora, Arch | Paquetes universales |
| `flatpak` | Linux | Paquetes universales |

## 🔧 Instalación de Gestores Adicionales

### Instalar yay (AUR Helper)

```bash

# Solo en Arch Linux
./packages.sh --install-yay

# Luego usar yay para paquetes AUR
./packages.sh --list base
```

### Instalar snapd

```bash

# En sistemas compatibles
./packages.sh --install-snap

# Sistemas soportados: Ubuntu, Debian, Fedora, Arch Linux
# No compatible: macOS, CentOS/RHEL
```

## 🚨 Solución de Problemas

### Problemas Comunes

#### 1. Error de Permisos
```bash

# Solución: Usar sudo
sudo ./packages.sh --list base

# O ejecutar como root
./packages.sh --list base --no-sudo
```

#### 2. Paquetes No Encontrados
```bash

# Verificar qué se instalaría
./packages.sh --list base --dry-run

# Instalar con información detallada
./packages.sh --list base --verbose
```

#### 3. Problemas con GUI en Servidor
```bash

# Forzar instalación de paquetes GUI
./packages.sh --list orgs --headless
```

#### 4. yay No Instalado en Arch
```bash

# Instalar yay primero
./packages.sh --install-yay

# Luego instalar paquetes
./packages.sh --list base
```

#### 5. snapd No Disponible
```bash

# Verificar compatibilidad
./packages.sh --install-snap

# Alternativa: usar flatpak
sudo apt install flatpak
./packages.sh --list base
```

### Logs y Debugging

```bash

# Modo verbose para debugging
./packages.sh --list base --verbose

# Ver ayuda completa
./packages.sh --help

# Ver listas disponibles
./packages.sh --help | grep "LISTAS DISPONIBLES" -A 20
```

## 🔄 Actualizaciones y Mantenimiento

### Actualizar Paquetes

```bash

# El script actualiza automáticamente paquetes existentes
./packages.sh --list base

# Verificar actualizaciones disponibles
./packages.sh --list base --dry-run
```

### Mantener Listas Actualizadas

```bash

# Editar archivos en configs/
vim configs/base.pkg

# Agregar nuevos paquetes
echo "ubuntu:apt:nuevo-paquete:Descripción del paquete" >> configs/base.pkg
```

## 📚 Casos de Uso Comunes

### 1. Configuración de Servidor de Desarrollo

```bash

# Instalar herramientas básicas
./packages.sh --list base

# Instalar herramientas de desarrollo
./packages.sh --list devs

# Instalar Docker
./packages.sh --list dckr

# Instalar Kubernetes
./packages.sh --list kube
```

### 2. Configuración de Estación de Trabajo

```bash

# Instalar todo
./packages.sh --list all

# O por partes
./packages.sh --list base,devs,orgs,cloud
```

### 3. Configuración de Servidor Headless

```bash

# Solo herramientas de servidor
./packages.sh --list base,devs,cloud,dckr,kube

# Sin paquetes GUI
```

### 4. Configuración de Arduino

```bash

# Instalar herramientas de Arduino
./packages.sh --list ardu
```

### 5. Configuración de Virtualización

```bash

# Instalar VirtualBox
./packages.sh --list vbox
```

## 🔗 Integración con Otros Scripts

### Con bintools

```bash

# Instalar bintools primero
./packages.sh --list base

# Luego usar otras herramientas
./git-tokens.py --help
./bw-send.sh --help
```

### Con Scripts Personalizados

```bash

# Crear script personalizado
cat > mi-setup.sh << 'EOF'
#!/bin/bash
echo "Configurando sistema..."
./packages.sh --list base,devs
echo "Configuración completada"
EOF

chmod +x mi-setup.sh
./mi-setup.sh
```

## 📖 Referencias y Enlaces

### Documentación Oficial


- **bintools**: [GitHub Repository](https://github.com/maurorosero/bintools)

- **Autor**: [Mauro Rosero Pérez](https://mauro.rosero.one)

### Gestores de Paquetes


- **APT**: [Ubuntu Package Management](https://help.ubuntu.com/lts/serverguide/apt.html)

- **DNF**: [Fedora Package Management](https://docs.fedoraproject.org/en-US/fedora/f35/system-administrators-guide/package-management/DNF/)

- **Pacman**: [Arch Linux Package Management](https://wiki.archlinux.org/title/Pacman)

- **Homebrew**: [macOS Package Manager](https://brew.sh/)

### Herramientas Relacionadas


- **Docker**: [Docker Documentation](https://docs.docker.com/)

- **Kubernetes**: [Kubernetes Documentation](https://kubernetes.io/docs/)

- **Bitwarden CLI**: [Bitwarden CLI Documentation](https://bitwarden.com/help/cli/)

---

## 💡 Consejos y Mejores Prácticas

### 1. Siempre Usar Modo de Prueba Primero

```bash

# Verificar antes de instalar
./packages.sh --list base --dry-run
```

### 2. Instalar por Categorías

```bash

# Instalar paso a paso
./packages.sh --list base
./packages.sh --list devs
./packages.sh --list cloud
```

### 3. Mantener Listas Actualizadas

```bash

# Revisar archivos de configuración regularmente
ls -la configs/
```

### 4. Usar Modo Verbose para Debugging

```bash

# Ver información detallada
./packages.sh --list base --verbose
```

### 5. Configurar Alias para Uso Frecuente

```bash

# Agregar a .bashrc o .zshrc
alias pkg-install='./packages.sh --list'
alias pkg-test='./packages.sh --dry-run --list'
alias pkg-verbose='./packages.sh --verbose --list'
```

---

**¡Disfruta usando packages.sh para automatizar tu instalación de paquetes!** 🚀
