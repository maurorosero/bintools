# 📦 Instalador de Paquetes Base (`packages.sh`)

Herramienta para instalar y mantener actualizados paquetes base en diferentes sistemas operativos.

## 🔍 Características

- 🔍 **Detección automática de SO**: Compatible con Debian/Ubuntu, RHEL/CentOS, Fedora, Arch, SUSE, FreeBSD y macOS
- 📋 **Paquetes personalizables**: Utiliza listas definidas en `config/[os]-base.pkg`
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

- `debian-base.pkg`: Paquetes para Debian/Ubuntu
- `redhat-base.pkg`: Paquetes para RHEL/CentOS
- `fedora-base.pkg`: Paquetes para Fedora
- `arch-base.pkg`: Paquetes para Arch Linux
- `suse-base.pkg`: Paquetes para SUSE/openSUSE
- `freebsd-base.pkg`: Paquetes para FreeBSD
- `macos-base.pkg`: Paquetes para macOS
- `snap.pkg`: Paquetes Snap para Ubuntu

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