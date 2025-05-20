#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Commitlint Wrapper - Script wrapper para ejecutar commitlint y validar mensajes de commit.
#
# Copyright (C) 2025 MAURO ROSERO PÉREZ
# License: GPLv3
#
# File: commitlint-wrapper.sh
# Version: 0.1.0
# Author: Mauro Rosero P. <mauro.rosero@gmail.com>
# Created: 2025-05-19 20:48:14
#
# This file is managed by template_manager.py.
# Any changes to this header will be overwritten on the next fix.
#
# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

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