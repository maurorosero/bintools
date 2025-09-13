# bintools - Colección de Herramientas de Desarrollo y Utilidades del Sistema

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)
![Shell](https://img.shields.io/badge/Shell-Bash%20%7C%20Zsh-orange.svg)

Una colección completa de herramientas de desarrollo y utilidades del sistema para Linux, diseñadas para automatizar tareas comunes y mejorar la productividad del desarrollador.

## ✨ Características Destacadas

- 🚀 **Instalación Automática**: Configuración completa de Cursor IDE y Python con un solo comando
- 🔧 **Multi-Distro**: Soporte nativo para Arch Linux, Debian, Ubuntu, Fedora y derivadas
- 🐍 **Gestión Avanzada de Python**: Entornos virtuales locales y globales con detección automática de shell
- 🎯 **Automatización Inteligente**: Detección automática de sistema operativo, arquitectura y configuración
- 🛠️ **Utilidades del Sistema**: Solución automática de problemas comunes (audio HDMI, resoluciones, backups)
- 📦 **Gestión de Paquetes**: Instalación inteligente con manejo de errores y dependencias

## 🛠️ Herramientas Incluidas

### 🎯 **micursor.py** - Gestor Completo de Cursor IDE

- ✅ **Instalación automática** en Linux (especialmente Arch Linux con AUR)
- ✅ **Desinstalación completa** con limpieza de archivos
- ✅ **Gestión de configuración** con backup y restore automático
- ✅ **Configuración de reglas MDC** para Cursor
- ✅ **Multiplataforma** (Linux, macOS, Windows)
- ✅ **Detección automática** de sistema operativo y arquitectura
- ✅ **Descarga inteligente** de la última versión disponible

### 🐍 **pymanager.sh** - Gestor Avanzado de Entornos Python

- ✅ **Gestión de entornos virtuales** locales y globales
- ✅ **Instalación automática** de Python y dependencias del sistema
- ✅ **Soporte multi-distro** (Arch, Debian, Fedora, CentOS)
- ✅ **Detección automática** de shell (Bash/Zsh)
- ✅ **Instalación de paquetes** con manejo inteligente de errores
- ✅ **Alias automáticos** para activación rápida de entornos

### 📦 **packages.sh** - Instalador Multiplataforma de Paquetes

- ✅ **Multiplataforma**: Ubuntu, Debian, Fedora, CentOS, Arch Linux, macOS
- ✅ **Múltiples manejadores**: apt, dnf, yum, pacman, yay, brew, snap
- ✅ **Fallback automático**: Snap como respaldo cuando el método principal falla
- ✅ **Listas organizadas**: base, devs, orgs, user con descripciones detalladas
- ✅ **Modo dry-run**: Ver qué se instalaría sin instalar realmente
- ✅ **Logging detallado**: Con colores y niveles de información
- ✅ **Manejo de errores**: Robusto y con mensajes claros

### 🔧 **Scripts de Utilidad del Sistema**

- **fix_hdmi_audio.sh** - Soluciona problemas de audio HDMI con PipeWire
- **hexroute** - Convertidor de rutas de red a formato hexadecimal para DHCP
- **nextcloud-installer.sh** - Gestor de backup/restore de configuración Nextcloud
- **videoset.sh** - Configurador automático de resoluciones de pantalla

## 📋 Requisitos

### Para micursor.py

- Python 3.7 o superior
- Conexión a Internet (para descargas)
- Permisos de administrador (para instalación)

### Para pymanager.sh

- Bash 4.0+ o Zsh
- Python 3.7+ (se instala automáticamente si no está presente)
- Conexión a Internet (para instalación de paquetes)
- Permisos de administrador (para instalación del sistema)

### Para packages.sh

- Bash 4.0+ o Zsh
- Permisos de administrador (para instalación de paquetes)
- Conexión a Internet (para instalación de paquetes)
- Snap opcional (para fallback automático)

### Para scripts de utilidad

- Linux con soporte para PipeWire (fix_hdmi_audio.sh)
- xrandr instalado (videoset.sh)
- Herramientas básicas: tar, gzip, find

## 🛠️ Instalación

```bash
# Clonar el repositorio (HTTPS)
git clone https://github.com/maurorosero/bintools.git
cd bintools

# O usando SSH (recomendado)
git clone git@github.com:maurorosero/bintools.git
cd bintools

# Hacer ejecutables los scripts
chmod +x micursor.py packages.sh
```

## 📖 Uso

### 🎯 Gestión de Cursor IDE (micursor.py)

```bash
# Instalar Cursor IDE
python micursor.py --install

# Desinstalar Cursor IDE
python micursor.py --remove

# Crear backup de configuración
python micursor.py --backup-login

# Restaurar configuración desde backup
python micursor.py --restore-login

# Configurar reglas MDC para Cursor
python micursor.py --config-mdc
```

### 🐍 Gestión de Entornos Python (pymanager.sh)

```bash
# Instalar Python completo del sistema
./pymanager.sh --install-python

# Crear entorno virtual local
./pymanager.sh --create mi-proyecto

# Instalar paquetes en entorno global
./pymanager.sh --package-global requests

# Instalar desde requirements.txt en entorno local
./pymanager.sh --package-local mi-proyecto requirements.txt

# Configurar alias para activación rápida
./pymanager.sh --set global

# Listar paquetes instalados
./pymanager.sh --list
```

### 📦 Instalación de Paquetes Multiplataforma (packages.sh)

```bash
# Instalar paquetes base del sistema
./packages.sh --list base

# Instalar paquetes de desarrollo
./packages.sh --list devs

# Instalar paquetes de organización/productividad
./packages.sh --list orgs

# Instalar paquetes personalizados del usuario
./packages.sh --list user

# Instalar múltiples listas
./packages.sh --list base,devs,user

# Instalar todas las listas disponibles
./packages.sh --list all

# Modo dry-run (solo mostrar qué se instalaría)
./packages.sh --list base --dry-run

# Instalar con información detallada
./packages.sh --list devs --verbose

# Mostrar ayuda
./packages.sh --help
```

**Listas de Paquetes Disponibles:**

- **base**: Paquetes esenciales (curl, git, wget, python3, vim, nano, etc.)
- **devs**: Herramientas de desarrollo (gcc, cmake, nodejs, Visual Studio Code, etc.)
- **orgs**: Aplicaciones de productividad (libreoffice, thunderbird, discord, etc.)
- **user**: Paquetes personalizados (htop, neofetch, spotify, etc.)

### 🔧 Utilidades del Sistema

```bash
# Solucionar problemas de audio HDMI
./fix_hdmi_audio.sh

# Configurar resolución de pantalla
./videoset.sh --auto

# Backup de configuración Nextcloud
./nextcloud-installer.sh --backup

# Convertir rutas de red a formato DHCP
./hexroute 172.16.0.0/16 gw 192.168.1.1
```

## 🖥️ Soporte por Sistema Operativo

### Linux

- **Arch Linux**: Instalación automática vía AUR (yay)
- **Otras distribuciones**: Descarga e instalación de AppImage
- **Ubicaciones**: `~/.local/share/cursor`, `~/.local/bin/cursor`

### macOS

- Instrucciones detalladas para instalación manual
- **Ubicación**: `/Applications/Cursor.app`

### Windows

- Instrucciones detalladas para instalación manual
- **Ubicaciones**: `Program Files`, `%APPDATA%\Cursor`

## 📁 Estructura del Proyecto

```text
bintools/
├── configs/             # Archivos de configuración de paquetes
│   ├── base.pkg        # Paquetes esenciales del sistema
│   ├── devs.pkg        # Paquetes para desarrollo
│   ├── orgs.pkg        # Paquetes para organización/productividad
│   └── user.pkg        # Paquetes personalizados del usuario
├── micursor.py          # Gestor de Cursor IDE
├── packages.sh          # Instalador multiplataforma de paquetes
├── fix_hdmi_audio.sh    # Script para arreglar audio HDMI
├── hexroute             # Herramienta de rutas hexadecimales
├── nextcloud-installer.sh # Instalador de Nextcloud
├── pymanager.sh         # Gestor de Python
├── videoset.sh          # Configurador de video
├── README.md            # Este archivo
├── .gitignore           # Archivos ignorados por Git
└── LICENSE              # Licencia MIT
```

## 🔧 Funcionalidades Detalladas

### 🎯 micursor.py - Características Avanzadas

- **Instalación Automática**: Detecta Arch Linux y usa AUR, descarga AppImage para otras distros
- **Gestión de Configuración**: Backup automático en `~/secure/cursor/` con restauración inteligente
- **Reglas MDC**: Configuración automática de reglas para Cursor IDE
- **Multiplataforma**: Soporte completo para Linux, macOS y Windows
- **Detección Inteligente**: Identifica automáticamente SO y arquitectura

### 🐍 pymanager.sh - Gestión Avanzada de Python

- **Instalación del Sistema**: Soporte para Arch, Debian, Fedora, CentOS y derivadas
- **Entornos Virtuales**: Gestión de entornos locales (`./.venv/`) y globales (`~/.venv/`)
- **Detección de Shell**: Compatibilidad automática con Bash y Zsh
- **Instalación de Paquetes**: Manejo inteligente de errores y dependencias
- **Alias Automáticos**: Configuración automática de `pyglobalset` para activación rápida

### 📦 packages.sh - Instalación Multiplataforma de Paquetes

- **Detección Automática de OS**: Ubuntu, Debian, Fedora, CentOS, Arch Linux, macOS
- **Múltiples Manejadores**: apt, dnf, yum, pacman, yay, brew, snap
- **Fallback Inteligente**: Snap como respaldo automático cuando el método principal falla
- **Listas Organizadas**: base (esenciales), devs (desarrollo), orgs (productividad), user (personalizados)
- **Modo Dry-Run**: Verificación previa sin instalación real
- **Logging Detallado**: Colores y niveles de información para seguimiento completo
- **Manejo de Errores**: Robusto con mensajes claros y recuperación automática

### 🔧 Scripts de Utilidad

- **fix_hdmi_audio.sh**: Solución automática de problemas de audio HDMI con PipeWire
- **videoset.sh**: Configuración automática de resoluciones de pantalla con xrandr
- **nextcloud-installer.sh**: Backup y restore completo de configuración Nextcloud
- **hexroute**: Conversión de rutas de red a formato hexadecimal para DHCP

## 🐛 Solución de Problemas

### micursor.py

- **"No se pudo obtener la URL de descarga"**: Verifica conexión a Internet
- **"Permisos insuficientes"**: Ejecuta con `sudo` si es necesario
- **"AUR helper no encontrado"**: Instala `yay` o usa `paru`

### pymanager.sh

- **"Python no encontrado"**: Usa `--install-python` para instalación automática
- **"Shell no detectado"**: Verifica que tienes Bash 4.0+ o Zsh instalado
- **"Entorno no válido"**: Usa `--create` para crear el entorno antes de instalar paquetes

### packages.sh

- **"OS no soportado"**: Verifica que tu distribución esté en la lista soportada
- **"Permisos insuficientes"**: Ejecuta con `sudo` si es necesario
- **"Paquete no encontrado"**: El script intentará automáticamente con snap como fallback
- **"Snap no disponible"**: Instala snap si quieres usar el fallback automático

### Scripts de Utilidad

- **fix_hdmi_audio.sh**: Verifica que PipeWire esté instalado y ejecutándose
- **videoset.sh**: Asegúrate de que xrandr esté instalado (`sudo apt install x11-xserver-utils`)
- **nextcloud-installer.sh**: Verifica que Nextcloud esté instalado y configurado

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

### Mauro Rosero Pérez

- Email: [mauro.rosero@gmail.com](mailto:mauro.rosero@gmail.com)
- GitHub: [@maurorosero](https://github.com/maurorosero)

## 🙏 Agradecimientos

- [Cursor AI](https://cursor.com) por crear un excelente editor de código con IA
- La comunidad de Arch Linux por mantener el AUR y sus herramientas
- [oslook/cursor-ai-downloads](https://github.com/oslook/cursor-ai-downloads) por mantener enlaces de descarga actualizados
- La comunidad Python por las herramientas de desarrollo y virtualización
- Los desarrolladores de PipeWire por la excelente gestión de audio en Linux

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:

1. Abre un [Issue](https://github.com/maurorosero/bintools/issues)
2. Contacta al autor por email
3. Revisa la documentación de [Cursor IDE](https://cursor.com/docs)

---

⭐ **¡Si este proyecto te ha sido útil, considera darle una estrella en GitHub!**
