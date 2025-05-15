#!/bin/bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-12 22:30:00
# Version: 0.1.0
#
# commitlint-wrapper.sh - Wrapper para commitlint que limpia automáticamente el mensaje temporal en caso de error
# -----------------------------------------------------------------------------

# Instalar dependencias si no están instaladas
if ! command -v npx &> /dev/null; then
    echo "Instalando dependencias de commitlint..."
    npm install -g @commitlint/cli
fi

# Ejecutar commitlint con el mensaje de commit
npx commitlint --edit "$1"
status=$?

# Si falla, limpiar el archivo temporal y mostrar sugerencia
if [ $status -ne 0 ]; then
    echo "Mensaje de commit inválido. Limpiando archivo temporal..."
    rm -f "$1"
    echo "Sugerencia: Usa el formato [TAG] descripción"
    echo "TAGS permitidos: [IMPROVE], [FIX], [DOCS], [STYLE], [REFACTOR], [PERF], [TEST], [BUILD], [CI], [CHORE]"
    exit 1
fi

exit 0 