# 📚 Documentación: videoset.sh

[⬅️ Volver al Índice Principal](/home/mrosero/bin/README.md)

## Descripción

`videoset.sh` es un script bash que facilita la configuración de resoluciones de pantalla específicas, especialmente útil para monitores externos que necesitan modos personalizados.

## Características

- Configura resolución 1600x900 a 60Hz en monitor HDMI
- Detección automática de monitores conectados
- Aplicación de modos personalizados a través de xrandr
- Manejo de errores para modos ya existentes

## Sintaxis

```bash
# Sin argumentos (aplica 1600x900@60Hz a HDMI-A-0)
videoset.sh

# Con argumentos específicos
videoset.sh [OPCIÓN]
```

## Opciones

- `--1600x900_60`: Establece resolución 1600x900 a 60Hz en el monitor HDMI-A-0
- `--auto`: Detecta automáticamente el monitor conectado y aplica resolución 1600x900@60Hz
- `--help`, `-h`: Muestra la ayuda del script

## Ejemplos de Uso

### Configuración Básica

```bash
# Aplicar resolución 1600x900@60Hz al monitor HDMI-A-0
videoset.sh
```

### Detección Automática

```bash
# Detectar automáticamente el monitor y aplicar resolución
videoset.sh --auto
```

## Nota Técnica

El script utiliza `xrandr` para:
1. Crear un nuevo modo de video con la resolución y frecuencia específicas
2. Agregar el modo creado al monitor designado
3. Cambiar la configuración del monitor para usar el nuevo modo

Si intenta agregar un modo que ya existe, el script está diseñado para ignorar el error y continuar con la configuración.
