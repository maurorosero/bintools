# Guía Completa de Releases de bintools

## 🎯 Sistema de Releases Automatizado

Este proyecto usa un sistema de releases automatizado que se ejecuta **únicamente** cuando ejecutas el script `create-release.sh` localmente. El workflow de GitHub Actions se dispara automáticamente desde tu máquina y usa un sistema de configuración flexible para definir exactamente qué archivos se incluyen en cada release.

## 🚀 Crear un Release

### Método 1: Script Automatizado (Recomendado)

```bash
# Crear release básico
./create-release.sh --version v1.0.0 --message "Primera versión estable"

# Crear release como draft
./create-release.sh -v v1.1.0 -m "Nueva funcionalidad" --draft

# Crear prerelease
./create-release.sh -v v1.2.0-beta -m "Versión beta" --prerelease

# Crear sin hacer push automático
./create-release.sh -v v1.0.1 -m "Bug fixes" --no-push
```

### Método 2: GitHub Actions Automático

El workflow de GitHub Actions se ejecuta automáticamente cuando usas el script `create-release.sh`. No necesitas hacer nada manualmente en GitHub.

### Método 3: Completamente Manual

```bash
# 1. Actualizar versión
echo "v1.0.0" > VERSION
git add VERSION
git commit -m "Bump version to v1.0.0"

# 2. Crear tag
git tag -a v1.0.0 -m "Release version v1.0.0"

# 3. Hacer push
git push origin main
git push origin v1.0.0

# 4. Crear paquete manualmente usando el sistema de configuración
./release-builder.sh --type user --output /tmp/bintools-v1.0.0
tar -czf bintools-v1.0.0.tar.gz bintools-v1.0.0/

# 5. Crear release en GitHub
# Ve a https://github.com/maurorosero/bintools/releases/new
# Adjunta el archivo bintools-v1.0.0.tar.gz
```

## 📋 Opciones del Script de Release

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--version` | Versión a crear | `--version v1.0.0` |
| `--message` | Mensaje del release | `--message "Bug fixes"` |
| `--draft` | Crear como draft | `--draft` |
| `--prerelease` | Marcar como prerelease | `--prerelease` |
| `--no-tag` | No crear tag automáticamente | `--no-tag` |
| `--no-push` | No hacer push automáticamente | `--no-push` |

## 🔧 Requisitos

### Para el Script Automatizado

- Bash 4.0+
- Git
- GitHub CLI (requerido para disparar el workflow)

### Para GitHub Actions

- El workflow se ejecuta automáticamente desde tu script local
- No necesitas acceso manual a GitHub Actions

### Para Método Manual

- Git
- Acceso web a GitHub

## 📁 Sistema de Configuración de Archivos

### Archivo de Configuración (`configs/release-config.yml`)

El sistema usa un archivo de configuración que te permite definir exactamente qué archivos se incluyen en cada tipo de release:

```yaml
# Archivos principales que se incluyen en todos los releases
main_files:
  - packages.sh
  - micursor.py
  - pymanager.sh
  - fix_hdmi_audio.sh
  - videoset.sh
  - nextcloud-installer.sh
  - hexroute

# Directorios que se incluyen completos
directories:
  - configs

# Archivos de configuración del proyecto
config_files:
  - VERSION
  - RELEASE_INFO

# Archivos opcionales por categoría
optional_files:
  documentation:
    - README.md
    - docs/INSTALL.md
    - LICENSE
  
  development:
    - .gitignore
    - docs/RELEASE.md
    - create-release.sh
    - release-builder.sh
    - bintools-manager.sh
  
  project_config:
    - .github/workflows/release.yml
    - configs/release-config.yml

# Configuración por tipo de release
release_types:
  full:
    include_main: true
    include_directories: true
    include_config: true
    include_optional:
      - documentation
      - development
      - project_config
  
  user:
    include_main: true
    include_directories: true
    include_config: true
    include_optional:
      - documentation
  
  minimal:
    include_main: true
    include_directories: true
    include_config: true
    include_optional: []

# Configuración por defecto
default_release_type: "user"

# Patrones de exclusión
exclude_patterns:
  - "*.tmp"
  - "*.log"
  - ".DS_Store"
  - "Thumbs.db"
  - "*.swp"
  - "*.swo"
  - "*~"
  - ".env"
  - "*.key"
  - "*.pem"
  - "*.p12"
```

## 🚀 Tipos de Release

### 1. **Release Completo (`full`)**

Incluye todos los archivos del proyecto:

- ✅ Archivos principales
- ✅ Directorios de configuración
- ✅ Archivos de configuración
- ✅ Documentación completa
- ✅ Archivos de desarrollo
- ✅ Configuración del proyecto

**Uso:**

```bash
./release-builder.sh --type full --output /tmp/full-release
```

### 2. **Release de Usuario (`user`)**

Incluye solo lo necesario para usar bintools:

- ✅ Archivos principales
- ✅ Directorios de configuración
- ✅ Archivos de configuración
- ✅ Documentación básica
- ❌ Archivos de desarrollo
- ❌ Configuración del proyecto

**Uso:**

```bash
./release-builder.sh --type user --output /tmp/user-release
```

### 3. **Release Mínimo (`minimal`)**

Incluye solo los archivos esenciales:

- ✅ Archivos principales
- ✅ Directorios de configuración
- ✅ Archivos de configuración
- ❌ Documentación
- ❌ Archivos de desarrollo
- ❌ Configuración del proyecto

**Uso:**

```bash
./release-builder.sh --type minimal --output /tmp/minimal-release
```

## 🔧 Personalización de Archivos

### Agregar Nuevos Archivos

Para agregar un nuevo archivo al release:

1. **Archivo principal** (siempre incluido):

```yaml
main_files:
  - packages.sh
  - micursor.py
  - nuevo-script.sh  # ← Agregar aquí
```

1. **Archivo opcional** (según categoría):

```yaml
optional_files:
  documentation:
    - README.md
    - nuevo-doc.md  # ← Agregar aquí
```

### Crear Nueva Categoría

```yaml
optional_files:
  nueva_categoria:
    - archivo1.sh
    - archivo2.py
    - archivo3.md
```

### Modificar Tipos de Release

```yaml
release_types:
  mi_tipo_personalizado:
    include_main: true
    include_directories: true
    include_config: true
    include_optional:
      - nueva_categoria
      - documentation
```

## 📋 Uso del Script de Configuración

### Opciones Disponibles

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--type` | Tipo de release | `--type user` |
| `--output` | Directorio de salida | `--output /tmp/release` |
| `--config` | Archivo de configuración | `--config custom.yml` |
| `--verbose` | Modo verbose | `--verbose` |
| `--help` | Mostrar ayuda | `--help` |

### Ejemplos de Uso

```bash
# Release básico
./release-builder.sh --type user --output /tmp/release

# Release completo con verbose
./release-builder.sh --type full --output /tmp/full-release --verbose

# Usar configuración personalizada
./release-builder.sh --type minimal --config mi-config.yml --output /tmp/minimal

# Ver ayuda
./release-builder.sh --help
```

## 📦 Estructura del Paquete

Cada release incluye según el tipo configurado:

```text
bintools-v1.0.0/
├── packages.sh              # Instalador de paquetes
├── micursor.py              # Gestor de Cursor IDE
├── pymanager.sh             # Gestor de Python
├── fix_hdmi_audio.sh        # Solucionador de audio HDMI
├── videoset.sh              # Configurador de pantalla
├── nextcloud-installer.sh   # Gestor de Nextcloud
├── hexroute                 # Convertidor de rutas
├── configs/                 # Configuraciones de paquetes
│   ├── base.pkg
│   ├── devs.pkg
│   ├── orgs.pkg
│   └── user.pkg
├── VERSION                  # Archivo de versión
└── RELEASE_INFO             # Información del release
```

## 🎯 Flujo de Trabajo Recomendado

### Para Releases Estables

```bash
# 1. Actualizar código
git add .
git commit -m "FEAT: Add new feature"

# 2. Crear release
./create-release.sh --version v1.1.0 --message "Nueva funcionalidad agregada"

# 3. Verificar en GitHub
# Ve a https://github.com/maurorosero/bintools/releases
```

### Para Releases de Prueba

```bash
# 1. Crear prerelease
./create-release.sh -v v1.1.0-beta -m "Versión beta para testing" --prerelease

# 2. Probar instalación
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --version v1.1.0-beta

# 3. Si todo está bien, crear release estable
./create-release.sh -v v1.1.0 -m "Versión estable"
```

## 🔄 Integración con GitHub Actions

El workflow de GitHub Actions usa automáticamente el sistema de configuración:

```yaml
# En .github/workflows/release.yml
- name: Create release package
  run: |
    ./release-builder.sh \
      --type user \
      --output "/tmp/bintools-release/bintools-${VERSION}" \
      --config configs/release-config.yml \
      --verbose
```

## 🔍 Verificación de Release

### Verificar Instalación

```bash
# Instalar versión específica
curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --version v1.0.0

# Verificar instalación
bintools-manager.sh version
bintools-manager.sh check
```

### Verificar en GitHub

1. Ve a [Releases](https://github.com/maurorosero/bintools/releases)
2. Verifica que el release aparezca
3. Descarga el archivo tar.gz
4. Verifica el contenido

## 🎯 Ventajas del Sistema

- ✅ **Flexibilidad**: Define exactamente qué incluir
- ✅ **Mantenibilidad**: Un solo archivo de configuración
- ✅ **Reutilización**: Misma configuración para diferentes tipos
- ✅ **Escalabilidad**: Fácil agregar nuevos archivos/categorías
- ✅ **Consistencia**: Mismo proceso para todos los releases
- ✅ **Exclusión**: Patrones para excluir archivos no deseados
- ✅ **Automatización**: Workflow se ejecuta solo desde tu script local
- ✅ **Control total**: Solo se ejecuta cuando tú lo decides

## 🐛 Solución de Problemas

### Error: "GitHub CLI no está instalado"

```bash
# Instalar GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### Error: "Tag ya existe"

```bash
# Eliminar tag local
git tag -d v1.0.0

# Eliminar tag remoto
git push origin :refs/tags/v1.0.0

# Crear nuevo tag
./create-release.sh --version v1.0.0 --message "Release corregido"
```

### Error: "No se puede hacer push"

```bash
# Verificar estado de git
git status

# Hacer pull antes del push
git pull origin main

# Intentar push nuevamente
git push origin main
```

### Error: "Archivo no encontrado"

```bash
# Verificar que el archivo existe
ls -la archivo.sh

# Verificar la configuración
grep -A 5 "main_files:" configs/release-config.yml
```

### Error: "Directorio no encontrado"

```bash
# Verificar que el directorio existe
ls -la directorio/

# Verificar la configuración
grep -A 5 "directories:" configs/release-config.yml
```

### Error: "Configuración no válida"

```bash
# Verificar sintaxis YAML
python3 -c "import yaml; yaml.safe_load(open('configs/release-config.yml'))"
```

## 📞 Soporte

Si tienes problemas con los releases:

1. Verifica que tienes permisos de escritura en el repositorio
2. Asegúrate de que GitHub CLI esté configurado correctamente
3. Revisa los logs de GitHub Actions si usas ese método
4. Verifica la sintaxis YAML del archivo de configuración
5. Asegúrate de que los archivos/directorios existen
6. Revisa los patrones de exclusión
7. Abre un [Issue](https://github.com/maurorosero/bintools/issues)
