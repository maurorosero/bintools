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
```

## 🚀 Uso Básico

### Sintaxis General

```bash
./repo-install.sh [OPCIÓN] [ARGUMENTO]
```

### Opciones Principales

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--list` | Listar scripts disponibles para el OS actual | `./repo-install.sh --list` |
| `--configure SCRIPT` | Ejecutar script de configuración | `./repo-install.sh --configure base-charm-repo` |
| `--help` | Mostrar ayuda completa | `./repo-install.sh --help` |

### Ejemplos Básicos

```bash
# Listar scripts disponibles
./repo-install.sh --list

# Configurar repositorio de Charm
./repo-install.sh --configure base-charm-repo

# Ver ayuda
./repo-install.sh --help
```

## 📦 Scripts de Repositorio Disponibles

### 🔧 base-charm-repo

**Descripción**: Configura el repositorio oficial de Charm para instalar `gum` y otras herramientas modernas de línea de comandos.

**Sistemas que requieren configuración de repositorio Charm:**

- Ubuntu: Requiere repositorio de Charm
- Debian: Requiere repositorio de Charm
- CentOS/RHEL: Requiere repositorio de Charm

**Sistemas que NO requieren este script:**

- Fedora: Disponible en repositorios oficiales
- Arch Linux: Disponible en repositorios oficiales
- macOS: Disponible via Homebrew

**¿Qué hace?**

- Descarga y configura la clave GPG de Charm
- Agrega el repositorio oficial a las fuentes del sistema
- Actualiza la lista de paquetes disponibles

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
```

## 🔧 Instalación por Sistema

### Ubuntu/Debian

```bash
# Configurar repositorio
./repo-install.sh --configure base-charm-repo

# Instalar gum
sudo apt install gum
```

### Fedora

```bash
# gum está disponible en repositorios oficiales, no requiere configuración
sudo dnf install gum
```

### CentOS/RHEL

```bash
# Configurar repositorio
./repo-install.sh --configure base-charm-repo

# Instalar gum
sudo dnf install gum
```

### Arch Linux

```bash
# gum está disponible en repositorios oficiales
sudo pacman -S gum
```

### macOS

```bash
# gum está disponible via Homebrew
brew install gum
```

## 🔗 Integración con packages.sh

### Flujo de Trabajo Completo

```bash
# 1. Configurar repositorio (solo para sistemas que lo requieren)
./repo-install.sh --configure base-charm-repo

# 2. Instalar paquetes que dependen del repositorio
./packages.sh --list gums
```

### Script de Setup Automático

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
```

## 🚨 Solución de Problemas

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| **Sistema no detectado** | Verificar que `/etc/os-release` existe |
| **Script no encontrado** | Usar `--list` para ver scripts disponibles |
| **Sin permisos de ejecución** | Verificar permisos del script |
| **Error de clave GPG** | Verificar conectividad a internet |
| **Repositorio no se agrega** | Verificar permisos sudo |

### Verificación de Configuración

#### Sistemas APT (Ubuntu/Debian)

```bash
# Verificar clave GPG
ls -la /etc/apt/keyrings/charm.gpg

# Verificar repositorio
cat /etc/apt/sources.list.d/charm.list

# Verificar paquetes disponibles
apt search gum
```

#### Sistemas DNF/YUM (CentOS/RHEL)

```bash
# Verificar repositorio
cat /etc/yum.repos.d/charm.repo

# Verificar paquetes disponibles
dnf search gum
```

### Debugging

```bash
# Ver scripts disponibles
./repo-install.sh --list

# Ver ayuda completa
./repo-install.sh --help

# Verificar permisos de script
ls -la repos/ubuntu/base-charm-repo.sh

# Ejecutar con información detallada
bash -x ./repo-install.sh --configure base-charm-repo
```

## 🔄 Mantenimiento

### Agregar Nuevos Scripts

1. **Crear directorio** si no existe:

   ```bash
   mkdir -p repos/nuevo-os
   ```

2. **Crear script** de configuración:

   ```bash
   # repos/nuevo-os/nuevo-repo.sh
   #!/bin/bash
   echo "Configurando nuevo repositorio..."
   # Comandos de configuración
   ```

3. **Dar permisos** de ejecución:

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
```

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
```

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

---

**¡Disfruta usando repo-install.sh para gestionar repositorios externos de forma segura!** 🚀
