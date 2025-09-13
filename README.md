# bintools - Herramientas Esenciales del Sistema

![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Una colección de herramientas esenciales para configurar y mantener sistemas Linux y macOS de forma rápida y eficiente.

## 🚀 ¿Qué es bintools?

bintools es un conjunto de scripts que automatizan la instalación y configuración de herramientas esenciales en tu sistema. En lugar de instalar paquete por paquete, simplemente ejecutas un comando y obtienes todo lo que necesitas.

## ✨ Características Principales

- 🎯 **Instalación Automática**: Un comando instala múltiples herramientas
- 🖥️ **Multiplataforma**: Funciona en Ubuntu, Debian, Fedora, CentOS, Arch Linux y macOS
- 🔧 **Configuración Inteligente**: Detecta automáticamente tu sistema y usa el método correcto
- 📦 **Paquetes Organizados**: Herramientas agrupadas por categoría (básicas, desarrollo, productividad)
- 🛡️ **Seguro**: Modo de prueba para ver qué se instalará antes de hacerlo

## 🛠️ Herramientas Incluidas

### 📦 Instalador de Paquetes (`packages.sh`)

El corazón de bintools. Instala automáticamente herramientas esenciales según tu sistema operativo.

**¿Qué puede instalar?**

- **Básicas**: curl, git, wget, python, vim, nano, herramientas de red
- **Desarrollo**: compiladores, Node.js, Visual Studio Code, herramientas de construcción
- **Productividad**: LibreOffice, navegadores, aplicaciones de comunicación
- **Personalizadas**: herramientas que tú elijas

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

### 🔧 Utilidades del Sistema

- **`fix_hdmi_audio.sh`**: Soluciona problemas de audio HDMI
- **`videoset.sh`**: Configura resoluciones de pantalla automáticamente
- **`nextcloud-installer.sh`**: Gestiona backups de Nextcloud
- **`hexroute`**: Convierte rutas de red a formato hexadecimal

## 🚀 Instalación Rápida

```bash
# Descargar bintools
git clone https://github.com/maurorosero/bintools.git
cd bintools

# Hacer ejecutables los scripts principales
chmod +x packages.sh micursor.py

# ¡Listo! Ya puedes usar las herramientas
```

## 📖 Uso Básico

### Instalar Herramientas Esenciales

```bash
# Ver qué se instalaría (recomendado primero)
./packages.sh --list base --dry-run

# Instalar herramientas básicas
./packages.sh --list base

# Instalar herramientas de desarrollo
./packages.sh --list devs

# Instalar todo
./packages.sh --list all
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

## 🖥️ Sistemas Soportados

| Sistema | Estado | Manejador de Paquetes |
|---------|--------|----------------------|
| Ubuntu/Debian | ✅ Completo | apt, snap |
| Fedora/CentOS | ✅ Completo | dnf, yum, snap |
| Arch Linux | ✅ Completo | pacman, yay, snap |
| macOS | ✅ Completo | brew, snap |

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
./packages.sh --list base,devs,user
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
