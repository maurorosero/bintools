#!/bin/bash

# Script para obtener el token de GitHub personal desde Bitwarden y guardarlo en git-tokens.py
# Reemplaza "MROSERO" por el usuario actual en mayúsculas

# Obtener el usuario actual en mayúsculas
CURRENT_USER=$(whoami | tr '[:lower:]' '[:upper:]')

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIÓN]

DESCRIPCIÓN:
    Script para obtener el token de GitHub personal desde Bitwarden y gestionar autenticación con GitHub CLI.

OPCIONES:
    --get     Obtener token desde Bitwarden y guardarlo en git-tokens.py (por defecto)
    --login   Usar token guardado para autenticar GitHub CLI
    -h, --help    Mostrar esta ayuda

EJEMPLOS:
    # Obtener token desde Bitwarden y guardarlo
    $0 --get

    # Autenticar GitHub CLI con token guardado
    $0 --login

    # Mostrar ayuda (comportamiento por defecto)
    $0

NOTAS:
    - El token se guarda usando el usuario actual en mayúsculas
    - Requiere que el campo se llame "[USUARIO] FULL TOKEN" en Bitwarden
    - Requiere Bitwarden CLI (bw) instalado y configurado
    - Requiere GitHub CLI (gh) para la opción --login

EOF
}

# Función para obtener token desde Bitwarden
get_token() {
    echo "🔍 Obteniendo token de GitHub personal desde Bitwarden..."
    echo "👤 Usuario: $CURRENT_USER"

    # Sincronizar con Bitwarden para obtener la información más actualizada
    echo "🔄 Sincronizando con Bitwarden..."
    bw sync

    # Obtener el token desde Bitwarden y guardarlo en git-tokens.py
    bw get item "GITHUB" | grep -o "\"${CURRENT_USER} FULL TOKEN\",\"value\":\"[^\"]*\"" | sed "s/.*\"value\":\"\([^\"]*\)\".*/\1/" | ./git-tokens.py set github-personal --token -

    if [ $? -eq 0 ]; then
        echo "✅ Token de GitHub personal guardado exitosamente"
    else
        echo "❌ Error al obtener o guardar el token"
        exit 1
    fi
}

# Función para autenticar GitHub CLI
login_github() {
    echo "🔐 Autenticando GitHub CLI con token guardado..."
    
    # Verificar que git-tokens.py existe
    if [ ! -f "./git-tokens.py" ]; then
        echo "❌ Error: No se encontró git-tokens.py en el directorio actual"
        exit 1
    fi
    
    # Verificar que GitHub CLI está instalado
    if ! command -v gh >/dev/null 2>&1; then
        echo "❌ Error: GitHub CLI (gh) no está instalado"
        echo "💡 Instala GitHub CLI: https://cli.github.com/"
        exit 1
    fi
    
    # Usar el token guardado para autenticar GitHub CLI
    ./git-tokens.py get github-personal --raw | gh auth login --with-token
    
    if [ $? -eq 0 ]; then
        echo "✅ GitHub CLI autenticado exitosamente"
    else
        echo "❌ Error al autenticar GitHub CLI"
        exit 1
    fi
}

# Función principal
main() {
    case "${1:-}" in
        --get)
            get_token
            ;;
        --login)
            login_github
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        "")
            # Sin argumentos, mostrar ayuda por defecto
            show_help
            exit 0
            ;;
        *)
            echo "❌ Error: Opción desconocida '$1'"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"