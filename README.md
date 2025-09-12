# bintools - Herramientas de Desarrollo

## micursor.py - Gestor de Cursor IDE

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)

Una colección de herramientas de desarrollo útiles para Linux, incluyendo un gestor completo para **Cursor IDE** y otros scripts de utilidad.

## 🛠️ Herramientas Incluidas

### micursor.py - Gestor de Cursor IDE
- ✅ **Instalación automática** en Linux (especialmente Arch Linux con AUR)
- ✅ **Desinstalación completa** con limpieza de archivos
- ✅ **Gestión de configuración** con backup y restore
- ✅ **Configuración de reglas MDC** para Cursor
- ✅ **Multiplataforma** (Linux, macOS, Windows)
- ✅ **Detección automática** de sistema operativo y arquitectura
- ✅ **Descarga inteligente** de la última versión disponible

### Otros Scripts de Utilidad
- **fix_hdmi_audio.sh** - Soluciona problemas de audio HDMI
- **hexroute** - Herramienta para manejo de rutas hexadecimales
- **nextcloud-installer.sh** - Instalador automatizado de Nextcloud
- **pymanager.sh** - Gestor de entornos Python
- **videoset.sh** - Configurador de resoluciones de video

## 📋 Requisitos

- Python 3.7 o superior
- Conexión a Internet (para descargas)
- Permisos de administrador (para instalación)

## 🛠️ Instalación

```bash
# Clonar el repositorio
git clone https://github.com/maurorosero/bintools.git
cd bintools

# Hacer ejecutable el script
chmod +x micursor.py
```

## 📖 Uso

### Instalación de Cursor IDE

```bash
# Instalar Cursor IDE
python micursor.py --install
```

### Desinstalación

```bash
# Desinstalar Cursor IDE
python micursor.py --remove
```

### Gestión de Configuración

```bash
# Crear backup de configuración
python micursor.py --backup-login

# Restaurar configuración desde backup
python micursor.py --restore-login
```

### Configuración de Reglas MDC

```bash
# Configurar reglas MDC para Cursor
python micursor.py --config-mdc
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

```
bintools/
├── micursor.py          # Gestor de Cursor IDE
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

### Instalación Automática (Linux)
1. Detecta si es Arch Linux y usa AUR
2. Descarga la última versión desde GitHub
3. Instala el AppImage en `~/.local/bin/`
4. Crea entrada en el menú de aplicaciones
5. Configura permisos de ejecución

### Gestión de Configuración
- **Backup**: Guarda toda la configuración de Cursor en `~/secure/cursor/`
- **Restore**: Restaura configuración desde el backup más reciente
- **Validación**: Verifica que Cursor no esté ejecutándose durante la restauración

### Reglas MDC
- Copia plantillas de reglas a `.cursor/rules/`
- Configura archivo `.cursorrules` en la raíz del proyecto
- Proporciona instrucciones para configuración manual

## 🐛 Solución de Problemas

### Error: "No se pudo obtener la URL de descarga"
- Verifica tu conexión a Internet
- El script usa GitHub para obtener las últimas versiones

### Error: "Permisos insuficientes"
- Ejecuta con `sudo` si es necesario
- Verifica que tienes permisos de escritura en los directorios de destino

### Error: "AUR helper no encontrado" (Arch Linux)
- Instala `yay` siguiendo las instrucciones que muestra el script
- O usa otro AUR helper como `paru`

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

**Mauro Rosero Pérez**
- Email: mauro.rosero@gmail.com
- GitHub: [@maurorosero](https://github.com/maurorosero)

## 🙏 Agradecimientos

- [Cursor AI](https://cursor.com) por crear un excelente editor
- La comunidad de Arch Linux por mantener el AUR
- [oslook/cursor-ai-downloads](https://github.com/oslook/cursor-ai-downloads) por mantener enlaces de descarga

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:

1. Abre un [Issue](https://github.com/maurorosero/bintools/issues)
2. Contacta al autor por email
3. Revisa la documentación de [Cursor IDE](https://cursor.com/docs)

---

⭐ **¡Si este proyecto te ha sido útil, considera darle una estrella en GitHub!**
