#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Videoset - Establece la resolución de pantalla para monitores conectados usando `xrandr`.
#
# Copyright (C) 2025 MAURO ROSERO PÉREZ
# License: GPLv3
#
# File: videoset.sh
# Version: 0.2.2
# Author: Mauro Rosero P. <mauro.rosero@gmail.com>
# Created: 2025-05-19 20:53:17
#
# This file is managed by template_manager.py.
# Any changes to this header will be overwritten on the next fix.
#
# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

# Función para mostrar ayuda
show_help() {
    echo "Uso: videoset.sh [OPCIÓN]"
    echo "Establece la resolución de pantalla."
    echo ""
    echo "Opciones:"
    echo "  --1600x900_60    Establece resolución 1600x900 a 60Hz en HDMI-A-0"
    echo "  --auto           Detecta automáticamente el monitor y aplica 1600x900@60Hz"
    echo "  --help, -h       Muestra esta ayuda"
    exit 1
}

# Función para establecer resolución 1600x900@60Hz en HDMI-A-0
set_1600x900_60() {
    echo "Configurando resolución 1600x900@60Hz en HDMI-A-0..."
    xrandr --newmode "1600x900_60.00" 118.25 1600 1696 1856 2112 900 903 908 934 -hsync +vsync
    xrandr --addmode "HDMI-A-0" "1600x900_60.00"
    xrandr --output "HDMI-A-0" --mode "1600x900_60.00"
    echo "Resolución configurada correctamente"
}

# Función para detectar automáticamente el monitor y aplicar resolución
auto_detect() {
    # Obtener el nombre de la pantalla HDMI
    local display_name=$(xrandr --current | grep -v disconnected | grep "HDMI" | grep connected | cut -d' ' -f1 | head -n 1)

    # Si no hay HDMI, intentar con cualquier pantalla conectada
    if [ -z "$display_name" ]; then
        display_name=$(xrandr --current | grep -v disconnected | grep connected | cut -d' ' -f1 | head -n 1)
    fi

    # Verificar si se encontró la pantalla
    if [ -z "$display_name" ]; then
        echo "Error: No se pudo detectar ninguna pantalla conectada"
        exit 1
    fi

    echo "Pantalla detectada: $display_name"

    # Establecer la resolución
    echo "Configurando resolución 1600x900@60Hz..."
    xrandr --newmode "1600x900_60.00" 118.25 1600 1696 1856 2112 900 903 908 934 -hsync +vsync

    # Es posible que el modo ya exista, así que usamos || true para ignorar errores
    xrandr --addmode "$display_name" "1600x900_60.00" || true
    xrandr --output "$display_name" --mode "1600x900_60.00"

    echo "Resolución configurada correctamente en $display_name"
}

# Verificar si no hay argumentos
if [ $# -eq 0 ]; then
    # Sin argumentos, ejecutar la configuración por defecto
    set_1600x900_60
    exit 0
fi

# Procesar argumentos
while [ "$1" != "" ]; do
    case $1 in
        --1600x900_60 )    set_1600x900_60
                          exit 0
                          ;;
        --auto )         auto_detect
                          exit 0
                          ;;
        -h | --help )    show_help
                          ;;
        * )              show_help
                          ;;
    esac
    shift
done
