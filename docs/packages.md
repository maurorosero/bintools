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

## 🖥️ Compatibilidad del Sistema

### ✅ Sistemas Probados

| Sistema | Versiones | Gestores | Estado |
|---------|-----------|----------|---------|
| **Ubuntu** | 20.04+, 22.04+, 23.10, 24.04+ | `apt`, `snap` | ✅ Funcional |
| **Debian** | 11 (Bullseye), 12 (Bookworm) | `apt`, `snap` | ✅ Funcional |
| **Arch Linux** | Rolling Release | `pacman`, `yay` | ✅ Funcional |
| **Manjaro** | Rolling Release | `pacman`, `yay` | ✅ Funcional |

### 🔶 Sistemas Teóricamente Compatibles

| Sistema | Versiones | Gestores | Notas |
|---------|-----------|----------|-------|
| **Fedora** | 38+ | `dnf`, `snap` | Requiere `snapd` manual |
| **CentOS/RHEL** | 8+ | `yum`/`dnf` | Soporte limitado `snap` |
| **macOS** | 11+ | `brew` | Requiere Homebrew |

### ❌ Sistemas No Soportados

| Sistema | Razón | Alternativa |
|---------|-------|-------------|
| **Windows** | No soporta gestores Linux | WSL2 + Ubuntu/Debian |
| **openSUSE** | `zypper` no implementado | Configuración manual |
| **Alpine Linux** | `apk` no implementado | Configuración manual |
| **BSD variants** | Gestores diferentes | Configuración manual |

### 🚧 Estado de Desarrollo

**Funcionalidades en desarrollo:**

- Soporte para `zypper` (openSUSE)
- Soporte para `apk` (Alpine Linux)
- Mejoras en gestión de Flatpak
- Interfaz web (futuro)

## 🚀 Instalación y Uso

### Instalación Rápida (Sin instalar bintools)

```bash
# Ejemplo: Instalar herramientas básicas del sistema (curl, git, vim, etc.)
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/packages.sh | bash -s -- --list base

# Otros ejemplos de listas disponibles:
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/packages.sh | bash -s -- --list devs    # Herramientas de desarrollo
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/packages.sh | bash -s -- --list dckr    # Docker completo
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/packages.sh | bash -s -- --list bwdn    # Bitwarden CLI
```

### Instalación Completa (Con bintools)

```bash
# Instalar bintools completo primero
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash

# Luego usar packages.sh globalmente (ejemplo: herramientas básicas)
packages.sh --list base
```

### Sintaxis y Opciones

```bash
./packages.sh [OPCIONES]

# Opciones principales
-l, --list LISTA     # Lista de paquetes (base, devs, cloud, etc.)
-d, --dry-run        # Solo mostrar qué se instalaría
-v, --verbose        # Información detallada
--headless           # Instalar paquetes GUI sin ambiente gráfico
--no-sudo            # Sin privilegios sudo (usuario root)
--install-yay        # Instalar yay (AUR helper)
--install-snap       # Instalar snapd
-h, --help           # Mostrar ayuda
```

### Ejemplos de Uso

```bash
# Instalación básica
./packages.sh --list base

# Múltiples listas
./packages.sh --list base,devs,cloud

# Modo de prueba
./packages.sh --list base --dry-run

# Servidor headless
./packages.sh --list base,devs,cloud

# Con información detallada
./packages.sh --list base --verbose
```

## 📦 Listas de Paquetes

### Listas Principales

| Lista | Descripción | Incluye |
|-------|-------------|---------|
| **`base`** | Paquetes esenciales | curl, git, wget, python, vim, nano, jq, yq |
| **`devs`** | Herramientas de desarrollo | build-essential, cmake, nodejs, npm, code |
| **`cloud`** | Cloud y DevOps | awscli, azure-cli, terraform, ansible, kubectl |
| **`dckr`** | Docker completo | docker-ce, docker-compose, kubernetes, portainer |
| **`kube`** | Kubernetes especializado | kubectl, helm, k9s, skaffold, tilt |
| **`orgs`** | Ofimática y productividad | libreoffice, firefox, thunderbird, filezilla |
| **`vbox`** | Virtualización | virtualbox, vagrant, qemu |
| **`bwdn`** | Gestión de contraseñas | bitwarden, vaultwarden |
| **`ardu`** | Arduino | arduino-ide, herramientas AVR |

### Ver Listas Disponibles

```bash
# Ver todas las listas
./packages.sh --help

# Ver qué se instalaría
./packages.sh --list base --dry-run
```

## 🔧 Características Avanzadas

### Detección Automática de GUI

El script detecta automáticamente el ambiente gráfico:

```bash
# Variables verificadas
DISPLAY, WAYLAND_DISPLAY, XDG_SESSION_TYPE

# Servidores gráficos
xset, Xorg, Xwayland, gnome-session, kde, etc.
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

### Detección de Paquetes GUI

**Paquetes GUI conocidos:**

- Navegadores: firefox, chromium, brave
- Oficina: libreoffice, thunderbird
- Desarrollo: code, android-studio, mysql-workbench
- Multimedia: vlc, gimp, blender

**Palabras clave en descripción:**

GUI, interfaz gráfica, escritorio, ventana, aplicación, cliente, editor, visor, reproductor, navegador, oficina, diseño, imagen, video, audio, juego, chat, mensajería, correo, IDE, editor, desarrollo, diseño, multimedia

## 🔧 Instalación de Gestores

### yay (AUR Helper para Arch)

```bash
# Instalar yay
./packages.sh --install-yay

# Luego usar para paquetes AUR
./packages.sh --list base
```

### snapd

```bash
# Instalar snapd
./packages.sh --install-snap

# Sistemas soportados: Ubuntu, Debian, Fedora, Arch Linux
# No compatible: macOS, CentOS/RHEL
```

## 📦 Gestión de Repositorios Adicionales

### Configurar Repositorios Externos

Algunos paquetes requieren repositorios externos que no están configurados por defecto en tu sistema. Para estos casos, usa `repo-install.sh`:

```bash
# Listar scripts de repositorio disponibles
./repo-install.sh --list

# Configurar repositorio específico
./repo-install.sh --configure base-charm-repo
```

### ⚠️ Importante: Repositorio de Charm para gum

**Para instalar `gum`** (herramienta moderna de línea de comandos), **algunos sistemas requieren configuración previa de repositorios**:

**Sistemas que requieren configuración de repositorio Charm:**

- Ubuntu/Debian: Requiere repositorio de Charm
- CentOS/RHEL: Requiere repositorio de Charm

**Sistemas que NO requieren configuración (disponible en repositorios oficiales):**

- Fedora: Disponible en repositorios oficiales
- Arch Linux: Disponible en repositorios oficiales
- macOS: Disponible via Homebrew

```bash
# Para sistemas que requieren configuración previa:
# 1. Configurar repositorio de Charm
./repo-install.sh --configure base-charm-repo

# 2. Instalar gum
./packages.sh --list gums

# Para sistemas con repositorios oficiales:
# Instalar directamente
./packages.sh --list gums
```

### Flujo de Trabajo Completo

```bash
# Configurar repositorios necesarios
./repo-install.sh --configure base-charm-repo

# Instalar paquetes básicos
./packages.sh --list base

# Instalar paquetes que dependen de repositorios externos
./packages.sh --list gums

# Instalar todo (incluyendo paquetes con dependencias externas)
./packages.sh --list all
```

### Documentación Completa

Para información detallada sobre gestión de repositorios, consulta la [guía completa de repo-install.sh](repo.md).

## 🚨 Solución de Problemas

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| **Error de permisos** | Usar `sudo ./packages.sh` |
| **Paquetes no encontrados** | Usar `--dry-run` para verificar |
| **GUI en servidor** | Usar `--headless` para forzar |
| **yay no instalado** | Ejecutar `--install-yay` primero |
| **snapd no disponible** | Verificar compatibilidad del sistema |
| **gum no se instala** | En Ubuntu/Debian/CentOS: `./repo-install.sh --configure base-charm-repo` |

### Logs y Debugging

```bash
# Modo verbose
./packages.sh --list base --verbose

# Ver ayuda completa
./packages.sh --help

# Ver listas disponibles
./packages.sh --help | grep "LISTAS DISPONIBLES" -A 20
```

## 📁 Formato de Archivos

### Estructura de Archivos .pkg

Los archivos de configuración están en `configs/` con formato:

```text
OS:Manejador:Paquete:Descripción
```

### Ejemplo

```bash
# Ubuntu/Debian
ubuntu:apt:curl:Herramienta para transferir datos desde servidores
ubuntu:apt:git:Sistema de control de versiones distribuido

# Arch Linux
arch:pacman:curl:Herramienta para transferir datos desde servidores
arch:pacman:git:Sistema de control de versiones distribuido

# macOS
macos:brew:curl:Herramienta para transferir datos desde servidores
macos:brew:git:Sistema de control de versiones distribuido
```

## 📚 Casos de Uso

### 1. Configuración de Servidor de Desarrollo

```bash
./packages.sh --list base,devs,dckr,kube
```

### 2. Configuración de Estación de Trabajo

```bash
./packages.sh --list all
```

### 3. Configuración de Servidor Headless

```bash
./packages.sh --list base,devs,cloud,dckr,kube
```

### 4. Configuración de Arduino

```bash
./packages.sh --list ardu
```

### 5. Configuración de Virtualización

```bash
./packages.sh --list vbox
```

## ⚠️ Limitaciones y Consideraciones

### Limitaciones Conocidas

- **Paquetes específicos**: Algunos paquetes pueden no estar disponibles en todas las distribuciones
- **Versiones variables**: Las versiones pueden variar entre distribuciones
- **Dependencias**: Algunos paquetes pueden requerir dependencias adicionales
- **Repositorios externos**: Algunos paquetes requieren repositorios adicionales

### Consideraciones de Seguridad

- **Privilegios sudo**: El script requiere privilegios de administrador
- **Repositorios externos**: Algunos paquetes provienen de repositorios no oficiales
- **Verificación**: Siempre revisa qué se va a instalar con `--dry-run`

### Limitaciones de Gestores

- **Snap en CentOS/RHEL**: Soporte limitado y puede causar conflictos
- **yay en Arch**: Requiere instalación manual del AUR helper
- **brew en macOS**: Requiere instalación previa de Homebrew
- **flatpak**: No está instalado por defecto en todos los sistemas

## 🔄 Mantenimiento

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
echo "ubuntu:apt:nuevo-paquete:Descripción" >> configs/base.pkg
```

## 🔗 Integración

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

## 💡 Mejores Prácticas

### 1. Siempre Usar Modo de Prueba Primero

```bash
./packages.sh --list base --dry-run
```

### 2. Instalar por Categorías

```bash
./packages.sh --list base
./packages.sh --list devs
./packages.sh --list cloud
```

### 3. Usar Modo Verbose para Debugging

```bash
./packages.sh --list base --verbose
```

### 4. Configurar Alias para Uso Frecuente

```bash
# Agregar a .bashrc o .zshrc
alias pkg-install='./packages.sh --list'
alias pkg-test='./packages.sh --dry-run --list'
alias pkg-verbose='./packages.sh --verbose --list'
```

## 📖 Referencias

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

**¡Disfruta usando packages.sh para automatizar tu instalación de paquetes!** 🚀
