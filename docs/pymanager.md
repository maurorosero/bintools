# Gestor de Entornos Python (pymanager.sh)

> **📖 [← Volver al README principal](../README.md)**

## 📖 Introducción

`pymanager.sh` es un gestor completo de entornos virtuales Python que simplifica la creación, gestión y configuración de entornos de desarrollo Python. Proporciona una interfaz unificada para manejar entornos locales y globales, instalación de paquetes y configuración automática.

### Características Principales

- 🐍 **Gestión de Entornos Virtuales**: Creación, activación y gestión de entornos locales y globales
- 📦 **Instalación de Paquetes**: Gestión de dependencias en entornos específicos
- 🔧 **Configuración Automática**: Setup completo de entorno de desarrollo
- ✅ **Multiplataforma**: Compatible con Linux, macOS y Windows
- 🛠️ **Integración**: Compatible con pip, poetry, pipenv
- 📝 **Logging**: Sistema de logs para seguimiento de operaciones

## 🔧 Pre-requisitos

### Requisitos del Sistema

- **Python 3.6+** instalado en el sistema
- **pip** (gestor de paquetes Python)
- **Herramientas base del sistema** (`packages.sh --list base`)
- **Herramientas de desarrollo** (`packages.sh --list devs`)

### Verificación de Requisitos

```bash
# Verificar Python instalado
python3 --version

# Verificar pip instalado
pip3 --version

# Instalar herramientas base si es necesario
packages.sh --list base

# Instalar herramientas de desarrollo si es necesario
packages.sh --list devs
```

### Instalación de Python

Si no tienes Python instalado, puedes usar el propio `pymanager.sh`:

```bash
# Instalar Python del sistema
./pymanager.sh --install-python
```

## 🚀 Uso Básico

### Estructura de Comandos

```bash
./pymanager.sh <comando> [argumentos...]
```

### Comandos Principales

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `--create` | Crear entorno virtual local | `./pymanager.sh --create mi-proyecto` |
| `--install` | Crear entorno global e instalar dependencias | `./pymanager.sh --install` |
| `--package-global` | Instalar paquete en entorno global | `./pymanager.sh --package-global requests` |
| `--package-local` | Instalar paquete en entorno local | `./pymanager.sh --package-local requests` |
| `--list` | Listar entornos disponibles | `./pymanager.sh --list` |
| `--set global` | Configurar alias global | `./pymanager.sh --set global` |
| `--set local` | Mostrar comandos para entorno local | `./pymanager.sh --set local` |
| `--help` | Mostrar ayuda completa | `./pymanager.sh --help` |

## 📦 Gestión de Entornos

### Entornos Locales (Proyecto)

Los entornos locales se crean en `./.venv/` dentro del directorio del proyecto.

#### Crear Entorno Local

```bash
# Crear entorno con nombre por defecto
./pymanager.sh --create

# Crear entorno con nombre específico
./pymanager.sh --create mi-proyecto

# Crear entorno con versión específica de Python
./pymanager.sh --create mi-proyecto --python 3.9
```

#### Activar Entorno Local

```bash
# Obtener comandos de activación
./pymanager.sh --set local

# Activar entorno específico
source ./.venv/mi-proyecto/bin/activate

# Desactivar entorno
deactivate
```

### Entornos Globales (Sistema)

Los entornos globales se crean en `~/.venv/default/` para uso general.

#### Crear Entorno Global

```bash
# Crear entorno global e instalar dependencias por defecto
./pymanager.sh --install
```

#### Configurar Alias Global

```bash
# Configurar alias 'pyglobalset' para activar entorno global
./pymanager.sh --set global

# Usar el alias
pyglobalset

# Eliminar alias
./pymanager.sh --unset global
```

## 📋 Gestión de Paquetes

### Instalación en Entorno Global

```bash
# Instalar paquete individual
./pymanager.sh --package-global requests

# Instalar desde requirements.txt
./pymanager.sh --package-global requirements.txt

# Instalar múltiples paquetes
./pymanager.sh --package-global "requests numpy pandas"
```

### Instalación en Entornos Locales

```bash
# Listar entornos locales disponibles
./pymanager.sh --list

# Instalar en entorno específico
./pymanager.sh --package-local mi-proyecto requests

# Instalar en entorno por defecto
./pymanager.sh --package-local requests
```

### Gestión de Dependencias

```bash
# Crear requirements.txt desde entorno activo
pip freeze > requirements.txt

# Instalar desde requirements.txt
pip install -r requirements.txt

# Actualizar paquetes
pip install --upgrade package-name
```

## 🔧 Configuración Avanzada

### Estructura de Directorios

```text
~/.venv/                    # Entornos globales
├── default/               # Entorno global por defecto
└── logs/                  # Logs del sistema

./.venv/                   # Entornos locales (en proyecto)
├── default/              # Entorno local por defecto
├── mi-proyecto/          # Entorno específico del proyecto
└── otro-proyecto/        # Otro entorno local
```

### Variables de Entorno

```bash
# Directorio base de entornos virtuales
VENV_DIR="$HOME/.venv"

# Entorno global por defecto
BIN_VENV_DIR="$VENV_DIR/default"

# Directorio de logs
LOG_FILE="$HOME/.logs/pymanager.log"
```

### Configuración de Shell

#### Bash

```bash
# Agregar al ~/.bashrc
alias pyglobalset='source ~/.venv/default/bin/activate'
```

#### Zsh

```bash
# Agregar al ~/.zshrc
alias pyglobalset='source ~/.venv/default/bin/activate'
```

## 📝 Ejemplos de Uso

### Flujo de Trabajo Completo

```bash
# 1. Crear proyecto
mkdir mi-proyecto
cd mi-proyecto

# 2. Crear entorno virtual
./pymanager.sh --create mi-proyecto

# 3. Activar entorno
source ./.venv/mi-proyecto/bin/activate

# 4. Instalar dependencias
pip install requests numpy

# 5. Crear requirements.txt
pip freeze > requirements.txt

# 6. Trabajar en el proyecto
python mi-script.py

# 7. Desactivar entorno
deactivate
```

### Desarrollo con Múltiples Entornos

```bash
# Crear entornos para diferentes versiones de Python
./pymanager.sh --create proyecto-py39 --python 3.9
./pymanager.sh --create proyecto-py310 --python 3.10

# Instalar paquetes específicos en cada entorno
./pymanager.sh --package-local proyecto-py39 "requests==2.28.0"
./pymanager.sh --package-local proyecto-py310 "requests==2.31.0"

# Cambiar entre entornos según necesidad
source ./.venv/proyecto-py39/bin/activate
# Trabajar con Python 3.9
deactivate

source ./.venv/proyecto-py310/bin/activate
# Trabajar con Python 3.10
deactivate
```

### Configuración de Entorno Global

```bash
# Crear entorno global con herramientas comunes
./pymanager.sh --install

# Configurar alias para uso fácil
./pymanager.sh --set global

# Instalar herramientas de desarrollo
./pymanager.sh --package-global "jupyter notebook black flake8"

# Usar entorno global
pyglobalset
jupyter notebook
```

## 🛠️ Integración con Herramientas

### Poetry

```bash
# Crear entorno con Poetry
poetry init
poetry install

# Activar entorno de Poetry
poetry shell
```

### Pipenv

```bash
# Crear entorno con Pipenv
pipenv install

# Activar entorno de Pipenv
pipenv shell
```

### Virtualenv

```bash
# Crear entorno con virtualenv
virtualenv .venv/mi-proyecto

# Activar entorno
source .venv/mi-proyecto/bin/activate
```

## 🚨 Solución de Problemas

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| **Python no encontrado** | `./pymanager.sh --install-python` |
| **Permisos insuficientes** | `sudo ./pymanager.sh --install-python` |
| **Entorno no se activa** | Verificar PATH y permisos del directorio |
| **Paquetes no se instalan** | Verificar conexión a internet y repositorios |
| **Conflicto de versiones** | Usar entornos separados para diferentes versiones |

### Verificación del Sistema

```bash
# Verificar Python instalado
python3 --version

# Verificar pip funcionando
pip3 --version

# Verificar entornos disponibles
./pymanager.sh --list

# Verificar logs
tail -f ~/.logs/pymanager.log
```

### Limpieza de Entornos

```bash
# Eliminar entorno global
./pymanager.sh --remove-global

# Eliminar entorno local
./pymanager.sh --remove-local

# Limpiar cache de pip
pip cache purge
```

## 📊 Logs y Monitoreo

### Sistema de Logs

Los logs se guardan en `~/.logs/pymanager.log` y incluyen:

- Creación de entornos
- Instalación de paquetes
- Errores y advertencias
- Información de configuración

### Verificación de Logs

```bash
# Ver logs recientes
tail -20 ~/.logs/pymanager.log

# Buscar errores específicos
grep ERROR ~/.logs/pymanager.log

# Limpiar logs antiguos
rm ~/.logs/pymanager.log
```

## 🔒 Seguridad y Mejores Prácticas

### Seguridad

1. **No ejecutar como root**: Usar usuarios normales para desarrollo
2. **Verificar paquetes**: Revisar dependencias antes de instalar
3. **Actualizar regularmente**: Mantener Python y paquetes actualizados
4. **Usar entornos aislados**: Separar proyectos con entornos diferentes

### Mejores Prácticas

1. **Un entorno por proyecto**: Evitar conflictos de dependencias
2. **Documentar dependencias**: Mantener requirements.txt actualizado
3. **Versionar entornos**: Usar nombres descriptivos para entornos
4. **Limpiar regularmente**: Eliminar entornos no utilizados

## 🚀 Casos de Uso Avanzados

### CI/CD

```bash
# En scripts de CI/CD
./pymanager.sh --create test-env
source ./.venv/test-env/bin/activate
pip install -r requirements.txt
python -m pytest
```

### Desarrollo Multi-proyecto

```bash
# Configurar múltiples proyectos
./pymanager.sh --create proyecto-web
./pymanager.sh --create proyecto-api
./pymanager.sh --create proyecto-data

# Cambiar entre proyectos fácilmente
alias web='cd ~/proyectos/web && source ./.venv/proyecto-web/bin/activate'
alias api='cd ~/proyectos/api && source ./.venv/proyecto-api/bin/activate'
alias data='cd ~/proyectos/data && source ./.venv/proyecto-data/bin/activate'
```

### Entornos de Producción

```bash
# Crear entorno de producción
./pymanager.sh --create prod --python 3.9

# Instalar solo dependencias de producción
./pymanager.sh --package-local prod -r requirements-prod.txt

# Verificar entorno
source ./.venv/prod/bin/activate
python -c "import sys; print(sys.version)"
```

## 📚 Referencias

### Documentación Relacionada

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Pipenv Documentation](https://pipenv.pypa.io/en/latest/)

### Herramientas Complementarias

- **packages.sh**: Instalación de herramientas base del sistema
- **repo-install.sh**: Configuración de repositorios adicionales
- **git-tokens.py**: Gestión de tokens de Git
- **bw-send.sh**: Envío seguro de archivos

---

**📖 [← Volver al README principal](../README.md)**
