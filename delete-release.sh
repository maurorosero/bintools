#!/bin/bash
# delete-release.sh - Script para eliminar releases de bintools
# Autor: Mauro Rosero Pérez
# Versión: 1.0.0

# Configuración
REPO_OWNER="maurorosero"
REPO_NAME="bintools"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    local level="$1"
    shift
    local message="$*"
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message" >&2
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message" >&2
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message" >&2
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
        "VERBOSE")
            if [[ "${VERBOSE:-false}" == "true" ]]; then
                echo -e "${BLUE}[VERBOSE]${NC} $message" >&2
            fi
            ;;
    esac
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

DESCRIPCIÓN:
    Script para eliminar releases de bintools de forma segura.
    Puede eliminar solo el release de GitHub o también el tag de Git.

OPCIONES:
    -v, --version VERSION    Versión del release a eliminar (requerido)
    -t, --delete-tag         También eliminar el tag de Git (local y remoto)
    --tag-only               Solo eliminar el tag de Git, no el release
    -f, --force             No pedir confirmación
    -l, --list              Listar releases disponibles
    -h, --help              Mostrar esta ayuda

EJEMPLOS:
    # Listar releases disponibles
    $0 --list

    # Eliminar solo el release (mantener tag)
    $0 --version v1.0.0

    # Eliminar release y tag
    $0 --version v1.0.0 --delete-tag

    # Eliminar solo el tag (mantener release)
    $0 --version v1.0.0 --tag-only

    # Eliminar sin confirmación
    $0 --version v1.0.0 --delete-tag --force

NOTAS:
    - Por defecto solo elimina el release de GitHub, no el tag de Git
    - Usa --delete-tag para eliminar también el tag local y remoto
    - Usa --tag-only para eliminar solo el tag, no el release
    - Usa --force para saltar confirmaciones (útil para scripts)
    - Requiere GitHub CLI (gh) instalado y autenticado

EOF
}

# Función para listar releases
list_releases() {
    log "INFO" "Releases disponibles en $REPO_OWNER/$REPO_NAME:"
    echo
    
    if command -v gh >/dev/null 2>&1; then
        gh release list --repo "$REPO_OWNER/$REPO_NAME" || {
            log "ERROR" "No se pudieron listar los releases"
            return 1
        }
    else
        log "ERROR" "GitHub CLI no está instalado"
        log "INFO" "Instala GitHub CLI: https://cli.github.com/"
        return 1
    fi
}

# Función para confirmar acción
confirm_action() {
    local message="$1"
    local force="$2"
    
    if [[ "$force" == "true" ]]; then
        return 0
    fi
    
    echo -e "${YELLOW}[CONFIRMACIÓN]${NC} $message"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        log "INFO" "Operación cancelada por el usuario"
        return 1
    fi
}

# Función para verificar si el release existe
release_exists() {
    local version="$1"
    
    if gh release view "$version" --repo "$REPO_OWNER/$REPO_NAME" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Función para verificar si el tag existe
tag_exists() {
    local version="$1"
    
    if git tag -l | grep -q "^$version$"; then
        return 0
    else
        return 1
    fi
}

# Función para verificar si el tag existe en remoto
remote_tag_exists() {
    local version="$1"
    
    if git ls-remote --tags origin | grep -q "refs/tags/$version$"; then
        return 0
    else
        return 1
    fi
}

# Función para eliminar release de GitHub
delete_github_release() {
    local version="$1"
    local force="$2"
    
    log "INFO" "Verificando si el release $version existe..."
    
    if ! release_exists "$version"; then
        log "ERROR" "El release $version no existe en GitHub"
        return 1
    fi
    
    log "SUCCESS" "Release $version encontrado"
    
    # Mostrar información del release
    log "INFO" "Información del release:"
    gh release view "$version" --repo "$REPO_OWNER/$REPO_NAME" | head -10
    echo
    
    if ! confirm_action "¿Eliminar el release $version de GitHub?" "$force"; then
        return 1
    fi
    
    log "INFO" "Eliminando release $version de GitHub..."
    
    if gh release delete "$version" --repo "$REPO_OWNER/$REPO_NAME" --yes; then
        log "SUCCESS" "Release $version eliminado de GitHub"
        return 0
    else
        log "ERROR" "Error eliminando el release $version"
        return 1
    fi
}

# Función para eliminar tag de Git
delete_git_tag() {
    local version="$1"
    local force="$2"
    
    log "INFO" "Verificando tags de Git..."
    
    local local_exists=false
    local remote_exists=false
    
    if tag_exists "$version"; then
        local_exists=true
        log "INFO" "Tag $version existe localmente"
    fi
    
    if remote_tag_exists "$version"; then
        remote_exists=true
        log "INFO" "Tag $version existe en el remoto"
    fi
    
    if [[ "$local_exists" == "false" && "$remote_exists" == "false" ]]; then
        log "WARNING" "El tag $version no existe ni local ni remotamente"
        return 0
    fi
    
    if ! confirm_action "¿Eliminar el tag $version (local y remoto)?" "$force"; then
        return 1
    fi
    
    # Eliminar tag local
    if [[ "$local_exists" == "true" ]]; then
        log "INFO" "Eliminando tag local $version..."
        if git tag -d "$version"; then
            log "SUCCESS" "Tag local $version eliminado"
        else
            log "ERROR" "Error eliminando tag local $version"
            return 1
        fi
    fi
    
    # Eliminar tag remoto
    if [[ "$remote_exists" == "true" ]]; then
        log "INFO" "Eliminando tag remoto $version..."
        if git push --delete origin "$version"; then
            log "SUCCESS" "Tag remoto $version eliminado"
        else
            log "ERROR" "Error eliminando tag remoto $version"
            return 1
        fi
    fi
    
    return 0
}

# Función principal
main() {
    local version=""
    local delete_tag=false
    local tag_only=false
    local force=false
    local list_only=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--version)
                version="$2"
                shift 2
                ;;
            -t|--delete-tag)
                delete_tag=true
                shift
                ;;
            --tag-only)
                tag_only=true
                shift
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -l|--list)
                list_only=true
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
    
    # Si solo se pide listar releases
    if [[ "$list_only" == "true" ]]; then
        list_releases
        exit $?
    fi
    
    # Validar argumentos requeridos
    if [[ -z "$version" ]]; then
        log "ERROR" "Debe especificar una versión con --version"
        show_help
        exit 1
    fi
    
    # Validar opciones mutuamente excluyentes
    if [[ "$delete_tag" == "true" && "$tag_only" == "true" ]]; then
        log "ERROR" "Las opciones --delete-tag y --tag-only son mutuamente excluyentes"
        show_help
        exit 1
    fi
    
    # Verificar que GitHub CLI esté instalado
    if ! command -v gh >/dev/null 2>&1; then
        log "ERROR" "GitHub CLI no está instalado"
        log "INFO" "Instala GitHub CLI: https://cli.github.com/"
        exit 1
    fi
    
    # Verificar autenticación de GitHub CLI
    if ! gh auth status >/dev/null 2>&1; then
        log "ERROR" "GitHub CLI no está autenticado"
        log "INFO" "Ejecuta: gh auth login"
        exit 1
    fi
    
    # Determinar qué acción realizar
    if [[ "$tag_only" == "true" ]]; then
        log "INFO" "Iniciando eliminación de tag $version (mantener release)..."
        
        # Solo eliminar tag de Git
        if ! delete_git_tag "$version" "$force"; then
            log "ERROR" "Error eliminando el tag $version"
            exit 1
        fi
        
        log "SUCCESS" "🎉 Tag $version eliminado exitosamente!"
        log "INFO" "Tag eliminado, release conservado en GitHub"
        
    else
        log "INFO" "Iniciando eliminación de release $version..."
        
        # Eliminar release de GitHub
        if ! delete_github_release "$version" "$force"; then
            exit 1
        fi
        
        # Eliminar tag de Git si se solicita
        if [[ "$delete_tag" == "true" ]]; then
            if ! delete_git_tag "$version" "$force"; then
                log "WARNING" "Release eliminado pero hubo problemas con el tag"
                exit 1
            fi
        else
            log "INFO" "Tag $version conservado (usa --delete-tag para eliminarlo)"
        fi
        
        log "SUCCESS" "🎉 Release $version eliminado exitosamente!"
        
        if [[ "$delete_tag" == "true" ]]; then
            log "INFO" "Release y tag eliminados completamente"
        else
            log "INFO" "Solo release eliminado, tag conservado"
        fi
    fi
}

# Ejecutar función principal
main "$@"
