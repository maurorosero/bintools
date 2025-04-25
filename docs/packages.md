# 📦 Instalador de Paquetes Base (`packages.sh`)

Herramienta para instalar y mantener actualizados paquetes base en diferentes sistemas operativos.

## 🔍 Características

- 🔍 **Detección automática de SO**: Compatible con Debian/Ubuntu, RHEL/CentOS, Fedora, Arch, SUSE, FreeBSD y macOS
- 📋 **Paquetes personalizables**: Utiliza listas definidas en `config/[os]-base.pkg`
- 📚 **Paquetes extras**: Soporte para paquetes adicionales mediante archivos `config/[os]-extras.pkg`
- 🧩 **SOPS integrado**: Instalación y actualización de Mozilla SOPS para gestión segura de secretos
- 📱 **Soporte para Snap**: Instala paquetes Snap en sistemas Ubuntu compatibles
- 🔄 **Actualización del sistema**: Función para actualizar todos los paquetes instalados
- 📊 **Registro detallado**: Guarda todas las operaciones en `/var/log/packages.log` o `~/bin/logs/packages.log`

## 💡 Uso

```bash
packages.sh [--install | --update] [--sops | --nosops | --nosnap] | [--help]
```

### Parámetros principales

| Parámetro | Descripción |
|:----------|:------------|
| `--install` | Instala los paquetes base para el SO detectado |
| `--update` | Actualiza todos los paquetes del sistema |
| `--help` | Muestra la ayuda del script (opción por defecto) |

### Parámetros adicionales

| Parámetro | Descripción |
|:----------|:------------|
| `--sops` | Con `--install` o `--update`, gestiona únicamente SOPS |
| `--nosops` | Evita la instalación/actualización de SOPS |
| `--nosnap` | Evita la instalación de paquetes Snap en Ubuntu |

## 📋 Ejemplos

```bash
# Instalar paquetes base para el SO (requiere root)
sudo packages.sh --install

# Actualizar todos los paquetes del sistema
sudo packages.sh --update

# Solo instalar o actualizar SOPS
sudo packages.sh --install --sops

# Instalar paquetes base sin paquetes Snap
sudo packages.sh --install --nosnap

# Actualizar sistema sin modificar SOPS
sudo packages.sh --update --nosops

# Mostrar ayuda
packages.sh --help
```

## 🛠️ Configuración

Los paquetes a instalar se definen en archivos de texto en `~/bin/config/`:

### Archivos de paquetes
- `[os]-base.pkg`: Paquetes básicos por sistema operativo (debian, redhat, fedora, arch, suse, freebsd, macos)
- `[os]-extras.pkg`: Paquetes personalizados adicionales para cada SO (definidos por el usuario)
- `snap.pkg`: Paquetes Snap para Ubuntu

### Archivos de definición
El repositorio incluye archivos de definición que sirven como plantillas:

- `[os]-extras.def`: Plantillas para paquetes extras recomendados
- `snap.def`: Plantilla para configuración de Snap

## 📄 Sistema de archivos

| Tipo de archivo | Incluido en el repo | Descripción |
|:----------------|:-------------------:|:------------|
| `*.pkg` | ✅ (base) / ❌ (extras/snap) | Archivos de configuración de paquetes activos |
| `*.def` | ✅ | Archivos de definición/plantilla |

Para crear tu configuración personalizada, puedes copiar un archivo `.def` a su versión `.pkg` correspondiente y editarlo según tus necesidades.

```bash
# Ejemplo para crear tu lista personalizada de paquetes extras para Debian
cp ~/bin/config/debian-extras.def ~/bin/config/debian-extras.pkg
# Editar el archivo para descomentar o agregar paquetes según necesidades
```

## 📊 Registros

Las operaciones se registran en:
- Como root: `/var/log/packages.log`
- Como usuario normal: `~/bin/logs/packages.log`

## 🔄 Actualización de SOPS

El script detecta automáticamente la última versión disponible de SOPS:

1. Consulta la API de GitHub de mozilla/sops
2. Verifica repositorios del sistema operativo
3. Utiliza una versión predeterminada como respaldo

## 📱 Gestión de Snap

En sistemas Ubuntu compatibles, el script:

1. Verifica si el sistema es compatible con Snap (exclusiones: Linux Mint, ElementaryOS)
2. Instala el servicio snapd si no está presente
3. Instala los paquetes listados en `config/snap.pkg`
4. Muestra un resumen de instalación con interfaz mejorada si gum está disponible

## ⚙️ Requisitos

- Bash 4.0 o superior
- Privilegios root para instalar paquetes
- Conexión a internet para actualizaciones