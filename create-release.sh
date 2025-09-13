#!/bin/bash
# Script para crear releases manuales de bintools
# Autor: Mauro Rosero Pérez

set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
PROJECT_NAME="bintools"
REPO_OWNER="maurorosero"
REPO_NAME="bintools"

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

Script para crear releases manuales de bintools

OPCIONES:
    -v, --version VERSION     Versión a crear (ej: v1.0.0)
    -m, --message MESSAGE    Mensaje del release
    -d, --draft              Crear como draft
    -p, --prerelease         Marcar como prerelease
    --no-tag                 No crear tag automáticamente
    --no-push                No hacer push automáticamente
    -h, --help               Mostrar esta ayuda

EJEMPLOS:
    $0 --version v1.0.0 --message "Primera versión estable"
    $0 -v v1.1.0-beta -m "Versión beta" --prerelease
    $0 -v v1.0.1 -m "Bug fixes" --draft

EOF
}

# Función para logging
log() {
    local level="$1"
    shift
    local message="$*"
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
    esac
}

# Función para crear el paquete de release
create_release_package() {
    local version="$1"
    local temp_dir="/tmp/bintools-release-$$"
    local package_dir="$temp_dir/bintools-$version"
    
    log "INFO" "Creando paquete para versión $version..."
    
    # Crear directorio temporal
    mkdir -p "$package_dir"
    
    # Copiar archivos principales
    log "VERBOSE" "Copiando archivos principales..."
    cp packages.sh "$package_dir/"
    cp micursor.py "$package_dir/"
    cp pymanager.sh "$package_dir/"
    cp fix_hdmi_audio.sh "$package_dir/"
    cp videoset.sh "$package_dir/"
    cp nextcloud-installer.sh "$package_dir/"
    cp hexroute "$package_dir/"
    
    # Copiar directorio de configuraciones
    log "VERBOSE" "Copiando configuraciones..."
    cp -r configs "$package_dir/"
    
    # Crear archivo de versión
    log "VERBOSE" "Creando archivo VERSION..."
    echo "$version" > "$package_dir/VERSION"
    
    # Crear archivo de información del release
    log "VERBOSE" "Creando archivo RELEASE_INFO..."
    cat > "$package_dir/RELEASE_INFO" << EOF
bintools $version
Released: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Repository: https://github.com/$REPO_OWNER/$REPO_NAME
Install: curl -fsSL https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/main/install.sh | bash -s -- --version $version
EOF
    
    # Crear paquete tar.gz
    log "VERBOSE" "Creando paquete tar.gz..."
    cd "$temp_dir"
    tar -czf "bintools-$version.tar.gz" "bintools-$version/"
    
    # Mostrar información del paquete
    log "SUCCESS" "Paquete creado: $temp_dir/bintools-$version.tar.gz"
    log "INFO" "Tamaño: $(du -h "bintools-$version.tar.gz" | cut -f1)"
    
    # Mostrar contenido
    log "INFO" "Contenido del paquete:"
    tar -tzf "bintools-$version.tar.gz" | sed 's/^/  /'
    
    echo "$temp_dir/bintools-$version.tar.gz"
}

# Función para crear tag
create_tag() {
    local version="$1"
    local message="$2"
    
    log "INFO" "Creando tag $version..."
    
    if git tag -a "$version" -m "$message"; then
        log "SUCCESS" "Tag $version creado"
    else
        log "ERROR" "Error creando tag $version"
        return 1
    fi
}

# Función para hacer push
push_changes() {
    local version="$1"
    
    log "INFO" "Haciendo push de cambios..."
    
    # Push del código
    if git push origin main; then
        log "SUCCESS" "Código subido a main"
    else
        log "ERROR" "Error subiendo código"
        return 1
    fi
    
    # Push del tag
    if git push origin "$version"; then
        log "SUCCESS" "Tag $version subido"
    else
        log "ERROR" "Error subiendo tag $version"
        return 1
    fi
}

# Función para disparar el workflow de GitHub Actions
trigger_github_workflow() {
    local version="$1"
    local message="$2"
    local draft="$3"
    local prerelease="$4"
    
    log "INFO" "Disparando workflow de GitHub Actions..."
    
    # Preparar payload
    local payload=$(cat << EOF
{
  "version": "$version",
  "message": "$message",
  "draft": $draft,
  "prerelease": $prerelease,
  "release_type": "user"
}
EOF
)
    
    # Disparar el workflow usando GitHub CLI
    if command -v gh >/dev/null 2>&1; then
        log "VERBOSE" "Usando GitHub CLI para disparar workflow..."
        
        if echo "$payload" | jq '{event_type: "create-release", client_payload: .}' | \
            gh api repos/$REPO_OWNER/$REPO_NAME/dispatches --method POST --input -; then
            log "SUCCESS" "Workflow disparado exitosamente"
            log "INFO" "Puedes ver el progreso en: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
        else
            log "ERROR" "Error disparando workflow"
            return 1
        fi
    else
        log "WARNING" "GitHub CLI no está instalado"
        log "INFO" "Instala GitHub CLI: https://cli.github.com/"
        log "INFO" "O dispara el workflow manualmente usando la API de GitHub"
        return 1
    fi
}

# Función para crear release directamente con GitHub CLI
create_github_release_direct() {
    local version="$1"
    local message="$2"
    local draft="$3"
    local prerelease="$4"
    
    log "INFO" "Creando release $version directamente..."
    
    # Crear el paquete usando release-builder.sh
    log "INFO" "Generando paquete de release..."
    local package_path
    package_path=$(./release-builder.sh \
        --type user \
        --output "/tmp/bintools-$version" \
        --config configs/release-config.yml 2>&1 | tail -1)
    
    if [[ ! -f "$package_path" ]]; then
        log "ERROR" "No se pudo crear el paquete de release"
        return 1
    fi
    
    log "SUCCESS" "Paquete creado: $package_path"
    
    # Copiar el paquete al directorio actual con el nombre correcto
    local local_package="bintools-$version.tar.gz"
    cp "$package_path" "$local_package"
    
    # Preparar flags para gh release create
    local gh_flags=()
    if [[ "$draft" == "true" ]]; then
        gh_flags+=(--draft)
    fi
    if [[ "$prerelease" == "true" ]]; then
        gh_flags+=(--prerelease)
    fi
    
    # Crear el release con GitHub CLI
    log "INFO" "Creando release en GitHub..."
    if gh release create "$version" "$local_package" \
        --title "bintools $version" \
        --notes "$message" \
        "${gh_flags[@]}"; then
        
        log "SUCCESS" "Release $version creado exitosamente en GitHub"
        log "INFO" "URL del release: https://github.com/$REPO_OWNER/$REPO_NAME/releases/tag/$version"
        
        # Limpiar archivo temporal
        rm -f "$local_package"
        
        return 0
    else
        log "ERROR" "Error creando el release en GitHub"
        rm -f "$local_package"
        return 1
    fi
}

# Función principal
main() {
    local version=""
    local message=""
    local draft=false
    local prerelease=false
    local no_tag=false
    local no_push=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--version)
                version="$2"
                shift 2
                ;;
            -m|--message)
                message="$2"
                shift 2
                ;;
            -d|--draft)
                draft=true
                shift
                ;;
            -p|--prerelease)
                prerelease=true
                shift
                ;;
            --no-tag)
                no_tag=true
                shift
                ;;
            --no-push)
                no_push=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validar argumentos requeridos
    if [[ -z "$version" ]]; then
        log "ERROR" "Debe especificar una versión con --version"
        show_help
        exit 1
    fi
    
    if [[ -z "$message" ]]; then
        message="Release version $version"
    fi
    
    log "INFO" "Iniciando creación de release $version..."
    log "VERBOSE" "Mensaje: $message"
    log "VERBOSE" "Draft: $draft"
    log "VERBOSE" "Prerelease: $prerelease"
    log "VERBOSE" "No tag: $no_tag"
    log "VERBOSE" "No push: $no_push"
    
    # Verificar que estamos en el directorio correcto
    if [[ ! -f "packages.sh" ]] || [[ ! -f "VERSION" ]]; then
        log "ERROR" "No se encontraron archivos de bintools. Ejecuta desde el directorio raíz del proyecto."
        exit 1
    fi
    
    # Actualizar archivo VERSION
    log "INFO" "Actualizando archivo VERSION..."
    echo "$version" > VERSION
    
    # Crear tag si se solicita
    if [[ "$no_tag" != "true" ]]; then
        create_tag "$version" "$message"
    fi
    
    # Hacer push si se solicita
    if [[ "$no_push" != "true" ]]; then
        push_changes "$version"
    fi
    
    # Crear release directamente usando GitHub CLI
    create_github_release_direct "$version" "$message" "$draft" "$prerelease"
    
    log "SUCCESS" "🎉 Release $version creado exitosamente!"
    log "INFO" "Los usuarios pueden instalar con:"
    log "INFO" "curl -fsSL https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/main/install.sh | bash -s -- --version $version"
}

# Ejecutar función principal
main "$@"
