#!/bin/bash
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-04-30 05:52:19
# Version: 0.1.0
#
# devenv-setup.sh - Script para configurar el entorno de desarrollo: instala dependencias de Python, hooks de pre-commit y snippets de VS Code.
# -----------------------------------------------------------------------------
#

# Script para configurar el entorno de desarrollo básico para este proyecto.
# Instala dependencias de Python y activa los hooks de pre-commit.

# --- Obtener directorio del script y cargar baselib ---
# Determinar el directorio donde reside el script de forma robusta

#!/usr/bin/env bash

set -uo pipefail

# --- Banner --- #
APP_NAME="Configurador de Entorno de Desarrollo"
APP_VERSION="0.2.4 (2025/04)"
APP_AUTHOR="Mauro Rosero Pérez (mauro.rosero@gmail.com)"


SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # Resolve $SOURCE until the file is no longer a symlink
  SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$SCRIPT_DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

if [[ -z "$SCRIPT_DIR" ]]; then
    echo "Error crítico: No se pudo determinar el directorio del script." >&2
    exit 1
fi

BASELIB_PATH="${SCRIPT_DIR}/lib/baselib.sh"

if [[ -f "$BASELIB_PATH" ]]; then
    # shellcheck source=lib/baselib.sh
    source "$BASELIB_PATH"
else
    echo "Error: No se encontró lib/baselib.sh en '$BASELIB_PATH'" >&2
    exit 1
fi

# Desactivar logging a archivo para este script específico
disable_file_logging

# --- Inicio del Script ---
clear
show_banner
echo -e "${BLUE}${BOLD}--- Configurando Entorno de Desarrollo ---${NC}"
echo ""

# 1. Verificar existencia de pip
echo -e "\n${CYAN}➜ ${BOLD}Verificando 'pip'...${NC}"
if ! command_exists pip; then # Usar command_exists de baselib
    mostrar_error "Comando 'pip' no encontrado en el PATH." 
    mostrar_info "  Por favor, asegúrate de que Python y pip estén instalados."
    exit 1
fi
mostrar_exito "'pip' encontrado."

# 2. Instalar dependencias
echo -e "\n${CYAN}➜ ${BOLD}Instalando dependencias desde requirements.txt...${NC}"
# Ejecutar pip en modo silencioso (-q) para evitar mucho output, mostrar mensajes propios
if pip install -q -r requirements.txt; then
    mostrar_exito "Dependencias instaladas correctamente."
else
    mostrar_error "Error al instalar dependencias."
    mostrar_info "  Ejecuta 'pip install -r requirements.txt' manualmente para ver detalles."
    exit 1
fi

# 3. Verificar existencia de pre-commit
echo -e "\n${CYAN}➜ ${BOLD}Verificando 'pre-commit'...${NC}"
if ! command_exists pre-commit; then # Usar command_exists de baselib
    mostrar_error "Comando 'pre-commit' no encontrado después de la instalación."
    mostrar_info "  La instalación de dependencias pudo haber fallado."
    exit 1
fi
mostrar_exito "'pre-commit' encontrado."

# 4. Instalar los hooks de git
echo -e "\n${CYAN}➜ ${BOLD}Instalando hooks de pre-commit en el repositorio local...${NC}"
# Capturar salida de pre-commit install para mostrarla sólo si hay error
PRE_COMMIT_OUTPUT=$(pre-commit install 2>&1)
if [ $? -eq 0 ]; then
    mostrar_exito "Hooks de pre-commit instalados/actualizados."
    mostrar_info "  Los chequeos se ejecutarán automáticamente antes de cada 'git commit'."
else
    mostrar_error "Error al instalar los hooks de pre-commit."
    mostrar_info "  Salida del comando:"
    echo -e "${YELLOW}${PRE_COMMIT_OUTPUT}${NC}" # Mostrar salida del error en amarillo
    exit 1
fi

# --- Añadir Snippets al Portapapeles ---
echo -e "\n${CYAN}➜ ${BOLD}Preparando snippets de VS Code/Cursor...${NC}"

# Leer el JSON desde el archivo de definición
HEADERS_DEF_FILE="${SCRIPT_DIR}/config/headers.def"
if [[ -f "$HEADERS_DEF_FILE" ]]; then
    SNIPPETS_JSON=$(cat "$HEADERS_DEF_FILE")
else
    mostrar_error "No se encontró el archivo de definición de snippets: $HEADERS_DEF_FILE"
    exit 1
fi

# Validar que SNIPPETS_JSON no esté vacío (por si el archivo estaba vacío)
if [[ -z "$SNIPPETS_JSON" ]]; then
    mostrar_error "El archivo de definición de snippets está vacío: $HEADERS_DEF_FILE"
    exit 1
fi

VSCODE_DIR=".vscode"
VSCODE_SNIPPETS_FILE="$PWD/$VSCODE_DIR/headers.code-snippets"

function copy_to_clipboard() {
    CLIPBOARD_CMD=""
    if command_exists xclip; then
        CLIPBOARD_CMD="xclip -selection clipboard"
    elif command_exists wl-copy; then
      CLIPBOARD_CMD="wl-copy"
    elif command_exists pbcopy; then # macOS
        CLIPBOARD_CMD="pbcopy"
    fi

    if [ -n "$CLIPBOARD_CMD" ]; then
        echo "$SNIPPETS_JSON" | $CLIPBOARD_CMD
        mostrar_exito "JSON de snippets copiado al portapapeles."
        mostrar_info "  Abre Cursor: Archivo > Preferencias > Configurar fragmentos... y pega el contenido."
    else
        mostrar_error "No hay utilidad de portapapeles (xclip, wl-copy, pbcopy)."
        mostrar_error "  Copia manualmente el siguiente JSON y pégalo en tu archivo de snippets."
        echo -e "${GREEN}------------------------- SNIPPETS JSON -------------------------${NC}"
        echo "$SCRIPT_DIR/$SNIPPETS_JSON"
        echo -e "${GREEN}-----------------------------------------------------------------${NC}"
        return 1
    fi

    return 0
}

# Crear el directorio .vscode si no existe o en su defecto intentar copiar al portapapeles
if [ ! -d "$VSCODE_DIR" ]; then
    mostrar_info "  Creando directorio $VSCODE_DIR..."
    mkdir -p "$VSCODE_DIR"
    if [ $? -ne 0 ]; then
        # Intentar copiar al portapapeles
        copy_to_clipboard
        if [ $? -ne 0 ]; then
            mostrar_error "No se pudo copiar el JSON de snippets al portapapeles."
            exit 1
        else 
            mostrar_exito "JSON de snippets copiado al portapapeles."
            exit 0
        fi
    fi
fi

# Escribir los snippets en el archivo, solo si el directorio existe o se pudo crear
if [ -d "$VSCODE_DIR" ]; then
    mostrar_info "  Escribiendo snippets en $VSCODE_SNIPPETS_FILE..."
    # Usar cat para preservar el formato JSON original leido del archivo .def
    echo "$SNIPPETS_JSON" > "$VSCODE_SNIPPETS_FILE"
    if [ $? -eq 0 ]; then
        mostrar_exito "Snippets guardados correctamente en $VSCODE_SNIPPETS_FILE."
        mostrar_info "  Puede que necesites reiniciar o recargar VS Code/Cursor para que los reconozca."
    else
        # Intentar copiar al portapapeles
        copy_to_clipboard
        if [ $? -ne 0 ]; then
            mostrar_error "No se pudo escribir en el archivo $VSCODE_SNIPPETS_FILE."
            mostrar_error "No se pudo copiar el JSON de snippets al portapapeles."
            exit 1
        else 
            mostrar_exito "JSON de snippets copiado al portapapeles."
            exit 0
        fi
    fi
fi

echo ""
echo -e "${GREEN}${BOLD}--- Configuración del Entorno Completada ---${NC}"
exit 0 