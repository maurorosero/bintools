# Guía Completa de Usuario - repo-install.sh

## 📖 Introducción

`repo-install.sh` es un gestor de repositorios OS-específicos que automatiza la configuración de repositorios externos según tu sistema operativo. Está diseñado para facilitar la instalación de herramientas que no están disponibles en los repositorios oficiales por defecto.

**⚠️ Importante**: Este script gestiona la configuración de repositorios externos que pueden contener software adicional. Siempre revisa qué repositorios se van a configurar antes de ejecutar.

### 🎯 Características Principales

- **🌍 Multiplataforma**: Compatible con Ubuntu, Debian, Fedora, CentOS, Arch Linux y macOS
- **🧠 Detección Automática**: Detecta automáticamente tu sistema operativo
- **📦 Gestión de Repositorios**: Configura repositorios específicos por OS
- **🔧 Scripts Modulares**: Cada repositorio tiene su propio script de configuración
- **🛡️ Seguridad**: Verifica claves GPG y configuraciones antes de aplicar
- **📋 Listado Dinámico**: Muestra solo los scripts disponibles para tu sistema
- **⚡ Ejecución Segura**: Verifica permisos y existencia antes de ejecutar

## 🖥️ Compatibilidad del Sistema

### ✅ Sistemas Soportados

| Sistema | Versiones | Estado | Directorio |
|---------|-----------|---------|------------|
| **Ubuntu** | 20.04+ | ✅ Funcional | `repos/ubuntu/` |
| **Debian** | 11+ | ✅ Funcional | `repos/debian/` |
| **Fedora** | 38+ | ✅ Funcional | `repos/fedora/` |
| **CentOS/RHEL** | 8+ | ✅ Funcional | `repos/centos/` |
| **Arch Linux** | Rolling | ✅ Funcional | `repos/arch/` |
| **macOS** | 11+ | ✅ Funcional | `repos/macos/` |

### 🔧 Detección Automática

El script detecta automáticamente tu sistema operativo mediante:

```bash

# Archivos de detección
/etc/os-release    # Sistemas Linux
OSTYPE            # macOS

# Sistemas detectados
ubuntu, debian, fedora, centos, rhel, rocky, almalinux
arch, manjaro, macos
```bash


## 🚀 Instalación y Uso

### Sintaxis General

```bash

./repo-install.sh [OPCIÓN] [ARGUMENTO]
```bash


### Opciones Principales

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--list` | Listar scripts disponibles para el OS actual | `./repo-install.sh --list` |
| `--configure SCRIPT` | Ejecutar script de configuración | `./repo-install.sh --configure base-charm-repo` |
| `--help` | Mostrar ayuda completa | `./repo-install.sh --help` |

### Ejemplos de Uso

```bash

# Listar scripts disponibles
./repo-install.sh --list

# Configurar repositorio de Charm
./repo-install.sh --configure base-charm-repo

# Ver ayuda
./repo-install.sh --help
```bash


## 📦 Scripts de Repositorio Disponibles

### 🔧 base-charm-repo

**Descripción**: Configura el repositorio oficial de Charm para instalar `gum` y otras herramientas modernas de línea de comandos.

**Sistemas Soportados**:
- Ubuntu (requiere repositorio Charm)
- Debian (requiere repositorio Charm)
- Fedora (disponible en repositorios oficiales)
- CentOS/RHEL (requiere repositorio Charm)

**Sistemas que NO requieren este script**:
- Arch Linux (disponible en repositorios oficiales)
- macOS (disponible via Homebrew)

**¿Qué hace?**
- Descarga y configura la clave GPG de Charm
- Agrega el repositorio oficial a las fuentes del sistema
- Actualiza la lista de paquetes disponibles

**Comandos de configuración**:

#### Ubuntu/Debian

```bash

# Configurar repositorio
./repo-install.sh --configure base-charm-repo

# Instalar gum
sudo apt install gum
```bash


#### Fedora

```bash

# gum está disponible en repositorios oficiales, no requiere configuración
sudo dnf install gum
```bash


#### CentOS/RHEL

```bash

# Configurar repositorio
./repo-install.sh --configure base-charm-repo

# Instalar gum
sudo yum install gum
```bash


### 📁 Estructura de Directorios

```bash

repos/
├── ubuntu/
│   └── base-charm-repo.sh
├── debian/
│   └── base-charm-repo.sh
├── fedora/
│   └── base-charm-repo.sh (instala desde repositorios oficiales)
├── centos/
│   └── base-charm-repo.sh
├── arch/
│   └── (vacío - gum disponible en repositorios oficiales)
└── macos/
    └── (vacío - gum disponible via Homebrew)
```bash


## 🔧 Funcionalidades Avanzadas

### Detección Automática de OS

```bash

# El script detecta automáticamente tu sistema
./repo-install.sh --list
# [INFO] Sistema operativo detectado: ubuntu
# [INFO] Buscando scripts en: repos/ubuntu
```bash


### Verificación de Scripts

El script verifica:

- ✅ **Existencia del directorio** del sistema operativo

- ✅ **Existencia del script** solicitado

- ✅ **Permisos de ejecución** del script

- ✅ **Código de salida** del script ejecutado

### Manejo de Errores

```bash

# Sistema no soportado
./repo-install.sh --list
# [ERROR] Directorio repos/unknown no existe
# [INFO] Sistemas soportados: ubuntu, debian, fedora, centos, arch, macos

# Script no encontrado
./repo-install.sh --configure script-inexistente
# [ERROR] Script 'script-inexistente.sh' no encontrado en repos/ubuntu
# [INFO] Scripts disponibles:
# ✓ base-charm-repo
```bash


## 📋 Casos de Uso

### 1. Configurar Repositorio de Charm

```bash

# Listar scripts disponibles
./repo-install.sh --list

# Configurar repositorio de Charm
./repo-install.sh --configure base-charm-repo

# Instalar gum
sudo apt install gum  # Ubuntu/Debian
sudo dnf install gum  # Fedora
sudo yum install gum  # CentOS/RHEL
```bash


### 2. Verificar Configuración

```bash

# Verificar que el repositorio se agregó correctamente
cat /etc/apt/sources.list.d/charm.list  # Ubuntu/Debian
cat /etc/yum.repos.d/charm.repo        # Fedora/CentOS
```bash


### 3. Integración con packages.sh

```bash

# Primero configurar repositorio
./repo-install.sh --configure base-charm-repo

# Luego instalar paquetes que dependen del repositorio
./packages.sh --list gums
```bash


## 🚨 Solución de Problemas

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| **Sistema no detectado** | Verificar que `/etc/os-release` existe |
| **Script no encontrado** | Usar `--list` para ver scripts disponibles |
| **Sin permisos de ejecución** | Verificar permisos del script |
| **Error de clave GPG** | Verificar conectividad a internet |
| **Repositorio no se agrega** | Verificar permisos sudo |

### Logs y Debugging

```bash

# Ver scripts disponibles
./repo-install.sh --list

# Ver ayuda completa
./repo-install.sh --help

# Verificar permisos de script
ls -la repos/ubuntu/base-charm-repo.sh

# Ejecutar con información detallada
bash -x ./repo-install.sh --configure base-charm-repo
```bash


### Verificación de Configuración

#### Ubuntu/Debian

```bash

# Verificar clave GPG
ls -la /etc/apt/keyrings/charm.gpg

# Verificar repositorio
cat /etc/apt/sources.list.d/charm.list

# Verificar paquetes disponibles
apt search gum
```bash


#### Fedora/CentOS

```bash

# Verificar repositorio
cat /etc/yum.repos.d/charm.repo

# Verificar paquetes disponibles
dnf search gum  # Fedora
yum search gum  # CentOS
```bash


## 🔄 Mantenimiento

### Agregar Nuevos Scripts

1. **Crear directorio** si no existe:

   ```bash
   mkdir -p repos/nuevo-os
   ```

1. **Crear script** de configuración:

   ```bash
   # repos/nuevo-os/nuevo-repo.sh
   #!/bin/bash
   echo "Configurando nuevo repositorio..."
   # Comandos de configuración
   ```

1. **Dar permisos** de ejecución:

   ```bash
   chmod +x repos/nuevo-os/nuevo-repo.sh
   ```

### Actualizar Scripts Existentes

```bash

# Editar script existente
vim repos/ubuntu/base-charm-repo.sh

# Verificar sintaxis
bash -n repos/ubuntu/base-charm-repo.sh

# Probar ejecución
./repo-install.sh --configure base-charm-repo
```bash


## 🔗 Integración

### Con packages.sh

```bash

# Configurar repositorio primero
./repo-install.sh --configure base-charm-repo

# Luego instalar paquetes
./packages.sh --list gums
```bash


### Con Scripts Personalizados

```bash

# Crear script de setup completo
cat > mi-setup-repos.sh << 'EOF'
#!/bin/bash
echo "Configurando repositorios..."
./repo-install.sh --configure base-charm-repo
echo "Repositorios configurados"
EOF

chmod +x mi-setup-repos.sh
./mi-setup-repos.sh
```bash


## ⚠️ Consideraciones de Seguridad

### Verificación de Claves GPG

Los scripts verifican automáticamente:

- ✅ **Claves GPG válidas** antes de agregar repositorios

- ✅ **Firmas digitales** de los repositorios

- ✅ **Conectividad segura** (HTTPS) a los repositorios

### Mejores Prácticas

1. **Siempre verificar** qué repositorio se va a configurar
2. **Revisar scripts** antes de ejecutar en sistemas de producción
3. **Mantener backups** de configuraciones originales
4. **Monitorear logs** de instalación de paquetes

### Ejemplo de Verificación

```bash

# Verificar script antes de ejecutar
cat repos/ubuntu/base-charm-repo.sh

# Verificar claves GPG
curl -fsSL https://repo.charm.sh/apt/gpg.key | gpg --show-keys

# Ejecutar solo después de verificar
./repo-install.sh --configure base-charm-repo
```bash


## 📚 Referencias

### Documentación Oficial

- **bintools**: [GitHub Repository](https://github.com/maurorosero/bintools)
- **Autor**: [Mauro Rosero Pérez](https://mauro.rosero.one)

### Repositorios Configurados

- **Charm**: [Charm Repository](https://repo.charm.sh/)
- **gum**: [gum Documentation](https://github.com/charmbracelet/gum)

### Gestores de Repositorios

- **APT**: [Ubuntu Package Management](https://help.ubuntu.com/lts/serverguide/apt.html)
- **DNF**: [Fedora Package Management](https://docs.fedoraproject.org/en-US/fedora/f35/system-administrators-guide/package-management/DNF/)
- **YUM**: [CentOS Package Management](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/managing_software_with_the_dnf_tool/index)

## 💡 Mejores Prácticas

### 1. Siempre Listar Primero

```bash

# Ver qué scripts están disponibles
./repo-install.sh --list
```bash


### 2. Verificar Antes de Configurar

```bash

# Revisar script antes de ejecutar
cat repos/ubuntu/base-charm-repo.sh
```bash


### 3. Integrar con packages.sh

```bash

# Configurar repositorio
./repo-install.sh --configure base-charm-repo

# Instalar paquetes
./packages.sh --list gums
```bash


### 4. Mantener Scripts Actualizados

```bash

# Revisar scripts regularmente
ls -la repos/*/

# Verificar permisos
find repos/ -name "*.sh" -exec ls -la {} \;
```bash


---

**¡Disfruta usando repo-install.sh para gestionar repositorios externos de forma segura!** 🚀
