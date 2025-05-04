#!/bin/bash
# Description: Gestor de entornos virtuales Python con múltiples versiones

# === Configuración inicial ========================================
VERSION="0.4.1"
AUTHOR="Mauro Rosero P."

# === Funciones de gestión de entornos ==============================
activate_venv() {
    local venv_path="$1"
    if [ -f "${venv_path}/bin/activate" ]; then
        source "${venv_path}/bin/activate"
        echo "Entorno virtual activado: ${venv_path}"
        return 0
    else
        error "Estructura inválida de entorno virtual en: ${venv_path}"
        return 1
    fi
}

# === Procesamiento de argumentos ==================================
while [[ $# -gt 0 ]]; do
    case "$1" in
        --activate)
            venv_path="$2"
            if [ ! -d "$venv_path" ]; then
                error "Directorio no encontrado: $venv_path"
                exit 1
            fi
            activate_venv "$venv_path" || exit 1
            shift 2
            ;;
        # ... otros casos ...
    esac
done 