# Guía de Instalación de bintools

## 🚀 Instalación Rápida

### Instalar Última Versión
```bash
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash
```

### Instalar Versión Específica
```bash
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --version v1.0.0
```

### Instalar en Directorio Personalizado
```bash
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --dir /opt/bintools
```

## 📋 Opciones de Instalación

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--version` | Versión específica a instalar | `--version v1.0.0` |
| `--dir` | Directorio de instalación personalizado | `--dir /opt/bintools` |
| `--extend-bin` | Extender directorio ~/bin existente | `--extend-bin` |
| `--dry-run` | Solo mostrar qué se haría | `--dry-run` |
| `--verbose` | Mostrar información detallada | `--verbose` |

## 🎯 Comportamiento del Instalador

### Directorio de Instalación por Defecto
- **Por defecto**: `~/bin`
- **Si ~/bin existe**: Pregunta si extender o usar `~/bintools`
- **Con --dir**: Usa el directorio especificado

### Configuración Automática
- ✅ Crea directorio de instalación
- ✅ Descarga archivos necesarios
- ✅ Configura permisos de ejecución
- ✅ Actualiza PATH automáticamente
- ✅ Verifica instalación

## 🔧 Gestión de Versiones

### Usar el Gestor de Versiones
```bash
# Descargar el gestor
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/bintools-manager.sh -o bintools-manager.sh
chmod +x bintools-manager.sh

# Comandos disponibles
./bintools-manager.sh install v1.0.0    # Instalar versión específica
./bintools-manager.sh update             # Actualizar a última versión
./bintools-manager.sh version            # Ver versión instalada
./bintools-manager.sh list               # Listar versiones disponibles
./bintools-manager.sh info               # Información de instalación
./bintools-manager.sh check              # Verificar instalación
./bintools-manager.sh uninstall          # Desinstalar completamente
```

## 📦 Estructura de Instalación

### Instalación en ~/bin (por defecto)
```
~/bin/
├── packages.sh
├── micursor.py
├── pymanager.sh
├── fix_hdmi_audio.sh
├── videoset.sh
├── nextcloud-installer.sh
├── hexroute
├── configs/
│   ├── base.pkg
│   ├── devs.pkg
│   ├── orgs.pkg
│   └── user.pkg
├── VERSION
└── RELEASE_INFO
```

### Instalación en ~/bintools
```
~/bintools/
├── packages.sh
├── micursor.py
├── pymanager.sh
├── fix_hdmi_audio.sh
├── videoset.sh
├── nextcloud-installer.sh
├── hexroute
├── configs/
│   ├── base.pkg
│   ├── devs.pkg
│   ├── orgs.pkg
│   └── user.pkg
├── VERSION
└── RELEASE_INFO
```

## 🌐 Sistema de Releases

### Versiones Disponibles
- **latest**: Última versión disponible
- **v1.0.0, v1.1.0, etc.**: Versiones específicas

### Crear Nueva Versión (Desarrolladores)
```bash
# 1. Actualizar versión
echo "v1.1.0" > VERSION
git add VERSION
git commit -m "Bump version to v1.1.0"

# 2. Crear release
git tag -a v1.1.0 -m "Release version v1.1.0"
git push origin main
git push origin v1.1.0

# 3. GitHub Actions automáticamente:
#    - Crea el release
#    - Genera el paquete tar.gz
#    - Lo sube como asset
```

## 🔍 Verificación de Instalación

### Verificar Instalación
```bash
# Verificar versión instalada
bintools-manager.sh version

# Verificar integridad
bintools-manager.sh check

# Ver información completa
bintools-manager.sh info
```

### Comandos Disponibles
Después de la instalación, estos comandos estarán disponibles:
- `packages` - Instalador de paquetes multiplataforma
- `micursor` - Gestor de Cursor IDE
- `pymanager` - Gestor de entornos Python
- `fix_hdmi_audio` - Solucionador de audio HDMI
- `videoset` - Configurador de pantalla
- `nextcloud-installer` - Gestor de Nextcloud
- `hexroute` - Convertidor de rutas de red

## 🐛 Solución de Problemas

### Error: "Versión no encontrada"
```bash
# Verificar versiones disponibles
bintools-manager.sh list

# Instalar versión específica válida
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --version v1.0.0
```

### Error: "Permisos insuficientes"
```bash
# Instalar con sudo si es necesario
sudo curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | sudo bash
```

### Error: "Directorio no encontrado"
```bash
# Verificar instalación
bintools-manager.sh check

# Reinstalar si es necesario
bintools-manager.sh uninstall
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash
```

## 📞 Soporte

Si tienes problemas con la instalación:
1. Verifica la instalación: `bintools-manager.sh check`
2. Revisa los logs con `--verbose`
3. Abre un [Issue](https://github.com/maurorosero/bintools/issues)
4. Contacta al autor: [mauro.rosero@gmail.com](mailto:mauro.rosero@gmail.com)
