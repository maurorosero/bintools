# 📚 Documentación: binsetup.sh

[⬅️ Volver al Índice Principal](/home/mrosero/bin/README.md)

## Descripción

`binsetup.sh` es un script bash que facilita la gestión de la carpeta `~/bin` en la variable PATH del sistema, permitiendo agregar o quitar esta ruta tanto de forma temporal (para la sesión actual) como permanente (en el archivo de configuración del shell).

## Características

- Agrega `~/bin` al PATH de forma temporal (solo sesión actual)
- Quita `~/bin` del PATH de forma temporal (solo sesión actual)
- Agrega `~/bin` al PATH de forma permanente (modificando .bashrc, .zshrc o .profile)
- Quita `~/bin` del PATH de forma permanente (modificando .bashrc, .zshrc o .profile)
- Detecta automáticamente el shell en uso (bash, zsh u otros)
- Crea respaldos de los archivos de configuración antes de modificarlos

## Sintaxis

```bash
# Agregar a PATH temporalmente
source binsetup.sh

# Quitar de PATH temporalmente
source binsetup.sh --disable

# Agregar a PATH permanentemente
./binsetup.sh --persistent

# Quitar de PATH permanentemente
./binsetup.sh --remove

# Mostrar ayuda
./binsetup.sh --help
```

## Ejemplos de Uso

### Configuración Inicial

Si es la primera vez que utiliza estas herramientas, se recomienda agregar la carpeta `~/bin` al PATH de forma permanente:

```bash
~/bin/binsetup.sh --persistent
source ~/.bashrc  # O el archivo correspondiente a su shell
```

### Uso Temporal

Para usar las herramientas sin modificar la configuración permanente:

```bash
source ~/bin/binsetup.sh
# Ahora puede usar las herramientas en ~/bin
```

### Desactivación Temporal

Si necesita quitar `~/bin` del PATH solo para la sesión actual:

```bash
source ~/bin/binsetup.sh --disable
```

## Nota Técnica

El script identifica automáticamente qué archivo de configuración debe modificar:
- `.bashrc` para usuarios de Bash
- `.zshrc` para usuarios de Zsh
- `.profile` para otros shells

Siempre crea una copia de respaldo (`.bak`) antes de realizar modificaciones permanentes.