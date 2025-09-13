# bintools - Herramientas Esenciales del Sistema

![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

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

### Método 2: Clonado Manual (Para Desarrollo)

```bash
# Clonar el repositorio
git clone https://github.com/maurorosero/bintools.git
cd bintools

# Hacer ejecutables los scripts principales
chmod +x packages.sh micursor.py

# ¡Listo! Ya puedes usar las herramientas
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

### `base` - Herramientas Esenciales

- curl, git, wget
- python3, python3-pip
- vim, nano
- jq, yq (procesadores de JSON/YAML)
- gnupg, dialog
- tree, rsync, net-tools
- gum, fzf (herramientas modernas)

### `devs` - Desarrollo

- Compiladores (gcc, g++)
- Herramientas de construcción (make, cmake)
- Node.js y npm
- Visual Studio Code
- Headers de desarrollo Python

### `orgs` - Productividad

- LibreOffice
- Navegadores (Firefox, Chromium)
- Thunderbird (correo)
- Discord, Slack
- Calibre (libros electrónicos)

### `user` - Personalizados

- htop (monitor de procesos)
- neofetch (info del sistema)
- bat, exa (herramientas modernas)
- Spotify

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

## 🤝 Contribuir

¿Tienes una herramienta que te gustaría agregar? ¡Es fácil!

1. Fork el proyecto
2. Agrega tu herramienta al archivo correspondiente en `configs/`
3. Haz un Pull Request

## 📝 Licencia

MIT License - Puedes usar, modificar y distribuir libremente.

## 👨‍💻 Autor

### Mauro Rosero Pérez

- Email: [mauro.rosero@gmail.com](mailto:mauro.rosero@gmail.com)
- GitHub: [@maurorosero](https://github.com/maurorosero)

## 📚 Documentación

Para información detallada sobre instalación, configuración y desarrollo:

- **[Guía de Instalación](docs/INSTALL.md)** - Instalación completa y gestión de versiones
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
2. Contacta al autor por email
3. Revisa la documentación de las herramientas específicas
