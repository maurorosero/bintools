#!/usr/bin/env bash

set -euo pipefail

# --- Banner --- #
APP_NAME="Personal Packages Installer"
APP_VERSION="0.9.4 (2025/04)"
APP_AUTHOR="Mauro Rosero Pérez (mauro.rosero@gmail.com)"

# Capturar los argumentos originales
ORIGINAL_ARGS=("$@")

# Función para mostrar el banner simple y estético
show_banner() {
  clear
  # Ancho deseado (aproximado)
  local width=50

  # Línea superior
  printf '+%*s+
' "$width" '' | tr ' ' '-'

  # Título centrado
  local title_len=${#APP_NAME}
  local title_pad=$(( (width - title_len) / 2 ))
  printf '|%*s%s%*s|
' "$title_pad" '' "$APP_NAME" "$((width - title_pad - title_len))" ''

  # Separador
  printf '|%*s|
' "$width" ''

  # Versión alineada
  local version_text="Version: $APP_VERSION"
  local version_len=${#version_text}
  local version_pad=$((width - version_len - 1))
  printf '| %s%*s|
' "$version_text" "$version_pad" ''

  # Autor alineado
  local author_text="By: $APP_AUTHOR"
  local author_len=${#author_text}
  local author_pad=$((width - author_len - 1))
  printf '| %s%*s|
' "$author_text" "$author_pad" ''

  # Línea inferior
  printf '+%*s+
' "$width" '' | tr ' ' '-'

  echo # Línea en blanco después del banner
}

# Mostrar banner inicial
show_banner

# --- Configuración Inicial --- #
# Detectar $HOME del usuario que invocó sudo, si aplica
if [[ -n "${SUDO_USER-}" ]]; then
  USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
  USER_HOME=$HOME
fi

# Determinar ruta de logs según si se ejecuta como root o usuario normal
if [[ "$(id -u)" -eq 0 ]]; then
  # Si se ejecuta con privilegios escalados (root/sudo), siempre usar /var/log
  LOG_DIR="/var/log"
else
  # Solo para procesos sin escalar, usar directorio en home
  LOG_DIR="$USER_HOME/bin/logs"
fi
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/packages.log"

echo "--- Inicio de ejecución (${ORIGINAL_ARGS[*]-}): $(date) ---" >> "$LOG_FILE"

# Directorio de configuración
CONFIG_DIR="$USER_HOME/bin/config"

# Variables globales
OS=""
PKG_MANAGER=""
UPDATE_CMD=""
INSTALL_CMD=""
UPGRADE_CMD=""
PKG_FILE=""
INSTALL_SOPS=true
ONLY_SOPS=false
NO_SNAP=false
# Versión predeterminada de SOPS para usar en caso de fallo
SOPS_DEFAULT_VERSION="3.10.2"
# Forzar uso de versión predeterminada (útil cuando GitHub API falla)
FORCE_DEFAULT_SOPS_VERSION=false
# Modo de operación (install o update)
OPERATION_MODE=""
# Indicador de conectividad a internet
INTERNET_AVAILABLE=true

# Función para comparar versiones
# Retorna 0 si la versión1 es mayor que la versión2
# Retorna 1 si la versión2 es mayor que la versión1
# Retorna 2 si son iguales
compare_versions() {
  if [[ "$1" == "$2" ]]; then
    return 2  # Versiones iguales
  fi
  
  local IFS=.
  local i ver1=($1) ver2=($2)
  
  # Rellenar con ceros para tener el mismo número de elementos
  for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
    ver1[i]=0
  done
  for ((i=${#ver2[@]}; i<${#ver1[@]}; i++)); do
    ver2[i]=0
  done
  
  # Comparar cada componente de la versión
  for ((i=0; i<${#ver1[@]}; i++)); do
    if [[ ${ver1[i]} -gt ${ver2[i]} ]]; then
      return 0  # version1 > version2
    elif [[ ${ver1[i]} -lt ${ver2[i]} ]]; then
      return 1  # version1 < version2
    fi
  done
  
  return 2  # Versiones iguales (no debería llegar aquí, pero por si acaso)
}

# Función de error
error_exit() {
  echo "Error: $1" >&2
  echo "Error: $1 - $(date)" >> "$LOG_FILE"
  exit 1
}

# Función para verificar la conexión a internet
check_internet_connection() {
  echo "Verificando conexión a internet..." >> "$LOG_FILE"
  
  # Sitios comunes y confiables para probar la conectividad
  local test_hosts=("google.com" "github.com" "cloudflare.com")
  INTERNET_AVAILABLE=false
  
  # Verificar si tenemos curl o wget disponibles
  if command -v curl &>/dev/null; then
    for host in "${test_hosts[@]}"; do
      if curl --max-time 5 -s "https://${host}" -o /dev/null &>/dev/null; then
        INTERNET_AVAILABLE=true
        echo "Conexión a internet verificada a través de ${host}" >> "$LOG_FILE"
        break
      fi
    done
  elif command -v wget &>/dev/null; then
    for host in "${test_hosts[@]}"; do
      if wget -T 5 -q --spider "https://${host}" &>/dev/null; then
        INTERNET_AVAILABLE=true
        echo "Conexión a internet verificada a través de ${host}" >> "$LOG_FILE"
        break
      fi
    done
  elif command -v ping &>/dev/null; then
    # Alternativa utilizando ping si curl o wget no están disponibles
    for host in "${test_hosts[@]}"; do
      if ping -c 1 -W 5 "${host}" &>/dev/null; then
        INTERNET_AVAILABLE=true
        echo "Conexión a internet verificada a través de ping a ${host}" >> "$LOG_FILE"
        break
      fi
    done
  fi
  
  if [[ "$INTERNET_AVAILABLE" == false ]]; then
    echo "No se pudo verificar la conexión a internet" >> "$LOG_FILE"
    echo "ADVERTENCIA: No se detecta conexión a internet. Algunas funciones pueden no estar disponibles." >&2
  fi
  
  return 0
}

# Función para verificar y solicitar privilegios de root
check_root() {
  if [[ "$(id -u)" -ne 0 ]]; then
    if command -v sudo >/dev/null 2>&1; then
      echo "Se requieren privilegios de superusuario. Intentando ejecutar con sudo..."
      exec sudo -- "$0" "${ORIGINAL_ARGS[@]-}"
    else
      error_exit "Este script debe ejecutarse como root o con sudo, pero sudo no está disponible."
    fi
  fi
}

# Función detect_os
detect_os() {
  if [[ "$(uname)" == "Darwin" ]]; then
    OS="macos"
    if ! command -v brew >/dev/null 2>&1; then
      error_exit "Homebrew no está instalado. Por favor, instálalo primero: https://brew.sh/"
    fi
    PKG_MANAGER="brew"
    UPDATE_CMD="brew update"
    INSTALL_CMD="brew install"
    UPGRADE_CMD="brew upgrade" # Comando para actualizar todo
    PKG_FILE="${CONFIG_DIR}/macos-base.pkg"
  elif [[ "$(uname)" == "FreeBSD" ]]; then
    OS="freebsd"
    PKG_MANAGER="pkg"
    UPDATE_CMD="pkg update"
    INSTALL_CMD="pkg install -y"
    UPGRADE_CMD="pkg upgrade -y" # Comando para actualizar todo
    PKG_FILE="${CONFIG_DIR}/freebsd-base.pkg"
  elif [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    OS_ID="$ID"
    OS_ID_LIKE="${ID_LIKE:-}"

    if [[ "$OS_ID" == "arch" || "$OS_ID_LIKE" == *"arch"* ]]; then
      OS="arch"
      PKG_MANAGER="pacman"
      UPDATE_CMD="" # Pacman actualiza al instalar/actualizar
      INSTALL_CMD="pacman -S --noconfirm"
      UPGRADE_CMD="pacman -Syu --noconfirm" # -Syu actualiza todo
      PKG_FILE="${CONFIG_DIR}/arch-base.pkg"
    elif [[ "$OS_ID" == "debian" || "$OS_ID" == "ubuntu" || "$OS_ID_LIKE" == *"debian"* || "$OS_ID_LIKE" == *"ubuntu"* ]]; then
      OS="debian"
      PKG_MANAGER="apt-get"
      UPDATE_CMD="apt-get update"
      INSTALL_CMD="apt-get install -y"
      UPGRADE_CMD="apt-get dist-upgrade -y" # O 'upgrade -y' si prefieres no manejar cambios mayores automáticamente
      PKG_FILE="${CONFIG_DIR}/debian-base.pkg"
    elif [[ "$OS_ID" == "fedora" || "$OS_ID_LIKE" == *"fedora"* ]]; then
      OS="fedora"
      PKG_MANAGER="dnf"
      UPDATE_CMD="dnf check-update"
      INSTALL_CMD="dnf install -y"
      UPGRADE_CMD="dnf upgrade -y" # Comando para actualizar todo
      PKG_FILE="${CONFIG_DIR}/fedora-base.pkg"
    elif [[ "$OS_ID" == "rhel" || "$OS_ID" == "centos" || "$OS_ID_LIKE" == *"rhel"* || "$OS_ID_LIKE" == *"centos"* ]]; then
      OS="redhat"
      if command -v dnf >/dev/null 2>&1; then
        PKG_MANAGER="dnf"
        UPDATE_CMD="dnf check-update"
        INSTALL_CMD="dnf install -y"
        UPGRADE_CMD="dnf upgrade -y"
      else
        PKG_MANAGER="yum"
        UPDATE_CMD="yum check-update"
        INSTALL_CMD="yum install -y"
        UPGRADE_CMD="yum update -y" # yum usa 'update' para actualizar todo
      fi
      PKG_FILE="${CONFIG_DIR}/redhat-base.pkg"
    elif [[ "$OS_ID" == "sles" || "$OS_ID" == "opensuse" || "$OS_ID_LIKE" == *"suse"* ]]; then
      OS="suse"
      PKG_MANAGER="zypper"
      UPDATE_CMD="zypper refresh"
      INSTALL_CMD="zypper install -y"
      UPGRADE_CMD="zypper dup -y" # 'dup' para Distribution Upgrade en suse
      PKG_FILE="${CONFIG_DIR}/suse-base.pkg"
    else
      error_exit "Sistema operativo Linux no soportado: $ID"
    fi
  else
    error_exit "No se pudo detectar el sistema operativo."
  fi
}

# Función para verificar si un paquete está instalado según el sistema operativo
is_package_installed() {
  local pkg="$1"
  local is_installed=false
  
  case "$OS" in
    macos)
      # En macOS (Homebrew)
      if brew list "$pkg" &>/dev/null; then
        is_installed=true
      fi
      ;;
    debian|ubuntu)
      # En Debian/Ubuntu
      if dpkg -s "$pkg" &>/dev/null; then
        is_installed=true
      fi
      ;;
    fedora|redhat)
      # En Fedora/RHEL
      if rpm -q "$pkg" &>/dev/null; then
        is_installed=true
      fi
      ;;
    arch)
      # En Arch Linux
      if pacman -Q "$pkg" &>/dev/null; then
        is_installed=true
      fi
      ;;
    suse)
      # En SUSE
      if rpm -q "$pkg" &>/dev/null; then
        is_installed=true
      fi
      ;;
    freebsd)
      # En FreeBSD
      if pkg info -e "$pkg" &>/dev/null; then
        is_installed=true
      fi
      ;;
    *)
      # Método genérico para otros sistemas
      if command -v "$pkg" &>/dev/null; then
        is_installed=true
      fi
      ;;
  esac
  
  echo "$is_installed"
}

# Función para obtener la última versión de SOPS disponible
get_latest_sops_version() {
  local latest_version="$SOPS_DEFAULT_VERSION"
  local source_info="versión predeterminada"
  
  echo "Consultando última versión de SOPS disponible..." >> "$LOG_FILE"
  
  # Verificar conexión a internet antes de intentar consultas externas
  check_internet_connection
  
  if [[ "$INTERNET_AVAILABLE" == false ]]; then
    echo "Sin conexión a internet. Usando versión predeterminada de SOPS: $latest_version" >> "$LOG_FILE"
    echo "ADVERTENCIA: Sin conexión a internet. Usando versión predeterminada de SOPS: $latest_version" >&2
    echo "$latest_version"
    return 0
  fi
  
  # PASO 1: Intentar obtener la versión directamente del sitio web de GitHub (prioridad más alta)
  if command -v curl &>/dev/null; then
    echo "Intentando obtener versión desde la página web de GitHub releases..." >> "$LOG_FILE"
    
    # Método 1: Consultar directamente la página web de releases
    local github_html
    if github_html=$(curl -s -m 15 "https://github.com/mozilla/sops/releases"); then
      # Buscar el patrón de la última versión en la página HTML
      # Esto busca patrones como "releases/tag/v3.10.2" o similares
      if [[ "$github_html" =~ releases\/tag\/v([0-9]+\.[0-9]+\.[0-9]+) ]]; then
        latest_version="${BASH_REMATCH[1]}"
        source_info="GitHub web releases"
        echo "Versión obtenida desde la página web de GitHub: $latest_version" >> "$LOG_FILE"
      fi
    else
      echo "Falló la consulta a la página web de GitHub. Error de conexión o timeout." >> "$LOG_FILE"
    fi
    
    # Si no se pudo obtener desde la web, intentar con la API
    if [[ "$source_info" == "versión predeterminada" && "$FORCE_DEFAULT_SOPS_VERSION" != "true" ]]; then
      if command -v jq &>/dev/null; then
        echo "Intentando obtener versión desde GitHub API..." >> "$LOG_FILE"
        local github_version
        if github_version=$(curl -s -m 10 https://api.github.com/repos/mozilla/sops/releases/latest | jq -r .tag_name 2>/dev/null) && \
           [[ -n "$github_version" && "$github_version" != "null" ]]; then
          # Quitar 'v' inicial si está presente
          github_version=${github_version#v}
          latest_version="$github_version"
          source_info="GitHub API"
          echo "Versión obtenida desde GitHub API: $latest_version" >> "$LOG_FILE"
        else
          echo "Falló la consulta a GitHub API. Intentando con Tags..." >> "$LOG_FILE"
          # Intentar con tags como alternativa
          echo "Intentando obtener versión desde GitHub Tags..." >> "$LOG_FILE"
          if github_version=$(curl -s -m 10 https://api.github.com/repos/mozilla/sops/tags | jq -r '.[0].name' 2>/dev/null) && \
             [[ -n "$github_version" && "$github_version" != "null" ]]; then
            # Quitar 'v' inicial si está presente
            github_version=${github_version#v}
            latest_version="$github_version"
            source_info="GitHub Tags"
            echo "Versión obtenida desde GitHub Tags: $latest_version" >> "$LOG_FILE"
          else
            echo "Falló la consulta a GitHub Tags. Posible problema de conexión." >> "$LOG_FILE"
          fi
        fi
      else
        echo "No se pudo consultar GitHub API - jq no disponible" >> "$LOG_FILE"
      fi
    fi
  else
    echo "No se pudo consultar GitHub web - curl no disponible" >> "$LOG_FILE"
  fi
  
  # PASO 2: Si no se pudo obtener de GitHub, intentar con los repos del sistema operativo
  if [[ "$source_info" == "versión predeterminada" ]]; then
    case "$OS" in
      macos)
        if command -v brew &>/dev/null; then
          # Intentar obtener versión disponible en Homebrew
          local brew_info
          if brew_info=$(brew info sops 2>/dev/null); then
            # Extraer la versión del output
            if [[ "$brew_info" =~ [0-9]+\.[0-9]+\.[0-9]+ ]]; then
              latest_version="${BASH_REMATCH[0]}"
              source_info="repositorio Homebrew"
              echo "Versión de SOPS en Homebrew: $latest_version" >> "$LOG_FILE"
            fi
          else
            echo "Error al consultar información de sops en Homebrew" >> "$LOG_FILE"
          fi
        fi
        ;;
      debian)
        if command -v apt-cache &>/dev/null; then
          # Intentar obtener versión disponible en repos de Debian/Ubuntu
          local apt_info
          if apt_info=$(apt-cache policy sops 2>/dev/null); then
            # Extraer la versión del output (buscar en Candidate:)
            if [[ "$apt_info" =~ Candidate:[[:space:]]([0-9]+\.[0-9]+\.[0-9]+) ]]; then
              latest_version="${BASH_REMATCH[1]}"
              source_info="repositorio APT"
              echo "Versión de SOPS en repos APT: $latest_version" >> "$LOG_FILE"
            fi
          else
            echo "Error al consultar información de sops en APT" >> "$LOG_FILE"
          fi
        fi
        ;;
      fedora|redhat)
        if command -v dnf &>/dev/null; then
          # Intentar obtener versión disponible en repos de Fedora/RHEL
          local dnf_info
          if dnf_info=$(dnf info sops 2>/dev/null); then
            # Extraer la versión del output
            if [[ "$dnf_info" =~ Version[[:space:]]*:[[:space:]]([0-9]+\.[0-9]+\.[0-9]+) ]]; then
              latest_version="${BASH_REMATCH[1]}"
              source_info="repositorio DNF"
              echo "Versión de SOPS en repos DNF: $latest_version" >> "$LOG_FILE"
            fi
          else
            echo "Error al consultar información de sops en DNF" >> "$LOG_FILE"
          fi
        elif command -v yum &>/dev/null; then
          # Fallback a yum para sistemas más antiguos
          local yum_info
          if yum_info=$(yum info sops 2>/dev/null); then
            # Extraer la versión del output
            if [[ "$yum_info" =~ Version[[:space:]]*:[[:space:]]([0-9]+\.[0-9]+\.[0-9]+) ]]; then
              latest_version="${BASH_REMATCH[1]}"
              source_info="repositorio YUM"
              echo "Versión de SOPS en repos YUM: $latest_version" >> "$LOG_FILE"
            fi
          else
            echo "Error al consultar información de sops en YUM" >> "$LOG_FILE"
          fi
        fi
        ;;
      arch)
        if command -v pacman &>/dev/null; then
          # Intentar obtener versión disponible en repos de Arch
          local pacman_info
          if pacman_info=$(pacman -Si sops 2>/dev/null); then
            # Extraer la versión del output
            if [[ "$pacman_info" =~ Version[[:space:]]*:[[:space:]]([0-9]+\.[0-9]+\.[0-9]+) ]]; then
              latest_version="${BASH_REMATCH[1]}"
              source_info="repositorio Pacman"
              echo "Versión de SOPS en repos Pacman: $latest_version" >> "$LOG_FILE"
            fi
          else
            echo "Error al consultar información de sops en Pacman" >> "$LOG_FILE"
          fi
        fi
        ;;
      freebsd)
        if command -v pkg &>/dev/null; then
          # Intentar obtener versión disponible en ports de FreeBSD
          local pkg_info
          if pkg_info=$(pkg search -e sops 2>/dev/null); then
            # Extraer la versión del output
            if [[ "$pkg_info" =~ sops-([0-9]+\.[0-9]+\.[0-9]+) ]]; then
              latest_version="${BASH_REMATCH[1]}"
              source_info="ports de FreeBSD"
              echo "Versión de SOPS en ports FreeBSD: $latest_version" >> "$LOG_FILE"
            fi
          else
            echo "Error al consultar información de sops en pkg" >> "$LOG_FILE"
          fi
        fi
        ;;
      *)
        echo "Sistema operativo no soportado para consulta de versión: $OS" >> "$LOG_FILE"
        ;;
    esac
  fi
  
  # PASO 3: Si no se pudo obtener de ninguna fuente, usar la versión predeterminada
  if [[ "$source_info" == "versión predeterminada" ]]; then
    echo "Usando versión predeterminada: $latest_version" >> "$LOG_FILE"
  fi
  
  echo "Última versión de SOPS: $latest_version (fuente: $source_info)" >> "$LOG_FILE"
  
  # Devolver solo la versión sin texto adicional
  echo "$latest_version"
}

# Actualiza la función install_sops para usar get_latest_sops_version
install_sops() {
  echo "Acción: Instalar/Actualizar SOPS"
  echo "Acción: Instalar/Actualizar SOPS" >> "$LOG_FILE"

  # Verificar conectividad a internet
  check_internet_connection
  
  # Obtener última versión disponible
  local latest_version
  latest_version=$(get_latest_sops_version)
  
  local current_version="desconocida"
  local is_installed=false
  local need_update=false

  # Verificar si ya está instalado
  if command -v sops >/dev/null 2>&1; then
    is_installed=true

    # Intentar obtener la versión actual con un manejo de errores mejorado
    if sops_output=$(sops --version 2>&1); then
      # Tratar de extraer solo el número de versión
      if [[ "$sops_output" =~ [0-9]+\.[0-9]+\.[0-9]+ ]]; then
        current_version="${BASH_REMATCH[0]}"
      fi
    fi
    
    echo "SOPS ya está instalado (versión $current_version)."
    echo "SOPS ya está instalado (versión $current_version)." >> "$LOG_FILE"
    
    # Comparar versión actual con versión disponible si la versión actual no es desconocida
    if [[ "$current_version" != "desconocida" ]]; then
      compare_versions "$latest_version" "$current_version"
      local compare_result=$?
      
      if [[ $compare_result -eq 0 ]]; then
        # Versión disponible es mayor que la instalada
        need_update=true
        echo "Hay una nueva versión disponible: $latest_version"
        echo "Hay una nueva versión disponible: $latest_version" >> "$LOG_FILE"
      elif [[ $compare_result -eq 2 ]]; then
        # Versiones iguales
        echo "SOPS ya está en la última versión ($current_version)."
        echo "SOPS ya está en la última versión ($current_version)." >> "$LOG_FILE"
      else
        # La versión instalada es mayor que la disponible (raro, pero posible)
        echo "La versión instalada ($current_version) es más reciente que la versión de referencia ($latest_version)."
        echo "La versión instalada ($current_version) es más reciente que la versión de referencia ($latest_version)." >> "$LOG_FILE"
      fi
    else
      # Si no se pudo determinar la versión actual, asumir que necesita actualización
      need_update=true
      echo "No se pudo determinar la versión instalada. Versión disponible: $latest_version"
      echo "No se pudo determinar la versión instalada. Versión disponible: $latest_version" >> "$LOG_FILE"
    fi
  else
    # SOPS no está instalado
    is_installed=false
    need_update=true
    echo "SOPS no está instalado. Versión disponible: $latest_version"
    echo "SOPS no está instalado. Versión disponible: $latest_version" >> "$LOG_FILE"
  fi

  # Determinar si se debe instalar/actualizar según el modo de operación
  local should_install=false
  
  if [[ "$OPERATION_MODE" == "install" ]]; then
    # En modo install, instalar solo si no está instalado
    if [[ "$is_installed" == false ]]; then
      should_install=true
      echo "Procediendo con la instalación de SOPS..."
      echo "Procediendo con la instalación de SOPS..." >> "$LOG_FILE"
    else
      echo "No se realizará la instalación porque SOPS ya está instalado."
      echo "No se realizará la instalación porque SOPS ya está instalado." >> "$LOG_FILE"
    fi
  elif [[ "$OPERATION_MODE" == "update" ]]; then
    # En modo update, actualizar solo si está instalado y hay una versión más reciente
    if [[ "$is_installed" == true && "$need_update" == true ]]; then
      should_install=true
      echo "Procediendo con la actualización de SOPS a la versión $latest_version..."
      echo "Procediendo con la actualización de SOPS a la versión $latest_version..." >> "$LOG_FILE"
    else
      if [[ "$is_installed" == false ]]; then
        echo "No se realizará la actualización porque SOPS no está instalado."
        echo "No se realizará la actualización porque SOPS no está instalado." >> "$LOG_FILE"
      else
        echo "No se realizará la actualización porque SOPS ya está en la última versión."
        echo "No se realizará la actualización porque SOPS ya está en la última versión." >> "$LOG_FILE"
      fi
    fi
  fi

  # Si no se debe instalar, terminar aquí pero sin salir de la función
  if [[ "$should_install" == false ]]; then
    # Evitar return aquí y permitir que el script continúe
    # Solo salir si es ONLY_SOPS, de lo contrario continuar con el flujo
    if [[ "$ONLY_SOPS" == true ]]; then
      return 0
    else
      # Continuar con el resto del script
      echo "Continuando con el resto del proceso de instalación..." >> "$LOG_FILE" 
    fi
  fi

  # Si no hay internet disponible y se requiere instalación/actualización, advertir y salir
  if [[ "$INTERNET_AVAILABLE" == false && "$should_install" == true ]]; then
    echo "ERROR: Se requiere conexión a internet para instalar/actualizar SOPS." >&2
    echo "ERROR: Se requiere conexión a internet para instalar/actualizar SOPS." >> "$LOG_FILE"
    return 1
  fi

  # Determinar método de instalación según el SO
  case "$OS" in
    macos)
      echo "Instalando/Actualizando SOPS vía Homebrew..."
      if brew install sops >> "$LOG_FILE" 2>&1; then
        echo "SOPS instalado/actualizado correctamente vía Homebrew."
      else
        echo "Error: Falló la instalación de SOPS vía Homebrew. Ver $LOG_FILE para detalles." >&2
        return 1
      fi
      ;;
    debian|fedora|redhat|suse)
      # Obtener arquitectura del sistema
      local arch
      arch=$(uname -m)
      local target_arch
      
      case "$arch" in
        x86_64) target_arch="amd64" ;;
        aarch64|arm64) target_arch="arm64" ;;
        *) error_exit "Arquitectura no soportada para SOPS: $arch" ;;
      esac

      # Asegurarse de que tenemos los comandos necesarios
      for cmd in curl; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
          echo "Instalando dependencia: $cmd..."
          if eval "$INSTALL_CMD" "$cmd" >> "$LOG_FILE" 2>&1; then
            echo "Dependencia $cmd instalada correctamente."
          else
            error_exit "No se pudo instalar $cmd, necesario para la instalación de SOPS."
          fi
        fi
      done
      
      echo "Usando versión de SOPS: $latest_version"
      echo "Usando versión de SOPS: $latest_version" >> "$LOG_FILE"
      
      # Descargar el binario
      local temp_dir
      temp_dir=$(mktemp -d)
      
      # Construir URL
      local download_url="https://github.com/mozilla/sops/releases/download/v${latest_version}/sops-v${latest_version}.linux.${target_arch}"
      
      echo "Descargando SOPS desde: $download_url"
      echo "Descargando SOPS desde: $download_url" >> "$LOG_FILE"
      
      if ! curl -L -s -o "$temp_dir/sops" "$download_url"; then
        echo "Falló la descarga desde $download_url - intentando URL alternativa..." >> "$LOG_FILE"
        
        # Probar URL alternativa sin 'v' en el nombre del archivo
        download_url="https://github.com/mozilla/sops/releases/download/v${latest_version}/sops-${latest_version}.linux.${target_arch}"
        echo "Intentando con URL alternativa: $download_url"
        echo "Descargando SOPS desde URL alternativa: $download_url" >> "$LOG_FILE"
        
        if ! curl -L -s -o "$temp_dir/sops" "$download_url"; then
          # Probar otra variante de URL
          download_url="https://github.com/getsops/sops/releases/download/v${latest_version}/sops-v${latest_version}.linux.${target_arch}"
          echo "Intentando con segunda URL alternativa: $download_url"
          echo "Descargando SOPS desde segunda URL alternativa: $download_url" >> "$LOG_FILE"
          
          if ! curl -L -s -o "$temp_dir/sops" "$download_url"; then
            echo "ERROR: Falló la descarga de SOPS desde GitHub usando todos los formatos de URL." >&2
            echo "ERROR: Falló la descarga de SOPS desde GitHub usando todos los formatos de URL." >> "$LOG_FILE"
            rm -rf "$temp_dir"
            return 1
          fi
        fi
      fi
      
      # Verificar que el archivo se descargó correctamente
      if [[ ! -s "$temp_dir/sops" ]]; then
        echo "ERROR: Archivo descargado está vacío o no existe." >&2
        echo "ERROR: Archivo descargado está vacío o no existe." >> "$LOG_FILE"
        rm -rf "$temp_dir"
        return 1
      fi
      
      # Hacer ejecutable e instalar
      chmod +x "$temp_dir/sops"
      if mv "$temp_dir/sops" /usr/local/bin/sops; then
        echo "SOPS instalado en /usr/local/bin/sops"
        echo "SOPS instalado en /usr/local/bin/sops" >> "$LOG_FILE"
      else
        echo "ERROR: No se pudo mover el binario de SOPS a /usr/local/bin/." >&2
        echo "ERROR: No se pudo mover el binario de SOPS a /usr/local/bin/." >> "$LOG_FILE"
        rm -rf "$temp_dir"
        return 1
      fi
      
      # Limpiar
      rm -rf "$temp_dir"
      ;;
    arch)
      # En Arch Linux, SOPS está disponible en los repositorios community
      echo "Instalando/Actualizando SOPS desde los repositorios de Arch..."
      if pacman -S --noconfirm sops >> "$LOG_FILE" 2>&1; then
        echo "SOPS instalado/actualizado correctamente desde los repositorios de Arch."
      else
        echo "Error: Falló la instalación de SOPS desde los repositorios de Arch. Ver $LOG_FILE para detalles." >&2
        return 1
      fi
      ;;
    freebsd)
      # En FreeBSD, SOPS está disponible en los ports
      echo "Instalando/Actualizando SOPS desde los ports de FreeBSD..."
      if pkg install -y sops >> "$LOG_FILE" 2>&1; then
        echo "SOPS instalado/actualizado correctamente desde los ports de FreeBSD."
      else
        echo "Error: Falló la instalación de SOPS desde los ports de FreeBSD. Ver $LOG_FILE para detalles." >&2
        return 1
      fi
      ;;
    *)
      error_exit "Instalación de SOPS no implementada para este sistema operativo: $OS"
      ;;
  esac

  # Verificar instalación
  local installed_version="desconocida"
  if command -v sops >/dev/null 2>&1; then
    # Intentar obtener la versión instalada con manejo de errores mejorado
    if sops_output=$(sops --version 2>&1); then
      # Tratar de extraer solo el número de versión
      if [[ "$sops_output" =~ [0-9]+\.[0-9]+\.[0-9]+ ]]; then
        installed_version="${BASH_REMATCH[0]}"
      fi
    fi
    
    echo "SOPS instalado/actualizado correctamente (versión $installed_version)."
    echo "SOPS instalado/actualizado correctamente (versión $installed_version)." >> "$LOG_FILE"
    return 0
  else
    echo "Error: No se pudo verificar la instalación de SOPS." >&2
    echo "Error: No se pudo verificar la instalación de SOPS." >> "$LOG_FILE"
    return 1
  fi
}

# Función para instalar paquetes Snap
install_snap_packages() {
  # Solo ejecutar en Ubuntu genuino (no en Mint ni derivados similares)
  if [[ "$OS" != "debian" || ! -f /etc/lsb-release ]]; then
    echo "La instalación de paquetes Snap no está disponible en este sistema." >> "$LOG_FILE"
    echo "La instalación de paquetes Snap no está disponible en este sistema."
    return 0
  fi
  
  # Verificar si es Linux Mint u otro derivado que no use Snap por defecto
  if grep -qi "mint" /etc/os-release 2>/dev/null || grep -qi "mint" /etc/lsb-release 2>/dev/null; then
    echo "Se detectó Linux Mint. Snap no se instalará en este sistema." >> "$LOG_FILE"
    echo "Se detectó Linux Mint. Snap no se instalará en este sistema."
    return 0
  fi
  
  # Verificar si es Elementary OS u otro derivado que no use Snap por defecto
  if grep -qi "elementary" /etc/os-release 2>/dev/null || grep -qi "elementary" /etc/lsb-release 2>/dev/null; then
    echo "Se detectó Elementary OS. Snap no se instalará en este sistema." >> "$LOG_FILE"
    echo "Se detectó Elementary OS. Snap no se instalará en este sistema."
    return 0
  fi
  
  # Verificar si existe el archivo snap.pkg
  local snap_pkg_file="${CONFIG_DIR}/snap.pkg"
  if [[ ! -f "$snap_pkg_file" ]]; then
    echo "No se encontró el archivo de paquetes Snap: $snap_pkg_file" >> "$LOG_FILE"
    echo "No se encontró el archivo de paquetes Snap: $snap_pkg_file"
    return 0
  fi
  
  echo "Acción: Instalar paquetes Snap"
  echo "Acción: Instalar paquetes Snap desde $snap_pkg_file" >> "$LOG_FILE"
  
  # Verificar conectividad a internet
  check_internet_connection
  if [[ "$INTERNET_AVAILABLE" == false ]]; then
    echo "ADVERTENCIA: Sin conexión a internet. No se pueden instalar paquetes Snap." >&2
    echo "ADVERTENCIA: Sin conexión a internet. No se pueden instalar paquetes Snap." >> "$LOG_FILE"
    return 1
  fi
  
  # Verificar si gum está instalado
  local USE_GUM=false
  if command -v gum >/dev/null 2>&1; then
    USE_GUM=true
    echo "Usando gum para visualización mejorada" >> "$LOG_FILE"
  else
    echo "gum no está disponible. Usando visualización estándar." >> "$LOG_FILE"
  fi
  
  # Verificar si snapd está instalado
  if ! command -v snap >/dev/null 2>&1; then
    if [[ "$USE_GUM" == true ]]; then
      gum style --border normal --margin "1" --padding "1 2" --border-foreground 212 "Snapd no está instalado. Instalando..."
    else
      echo "Snapd no está instalado. Instalando..."
    fi
    
    echo "Instalando snapd..." >> "$LOG_FILE"
    
    if ! apt-get update >> "$LOG_FILE" 2>&1; then
      echo "ERROR: No se pudo actualizar los repositorios de APT." >&2
      echo "ERROR: No se pudo actualizar los repositorios de APT." >> "$LOG_FILE"
      return 1
    fi
    
    if ! apt-get install -y snapd >> "$LOG_FILE" 2>&1; then
      echo "ERROR: No se pudo instalar snapd." >&2
      echo "ERROR: No se pudo instalar snapd." >> "$LOG_FILE"
      return 1
    fi
    
    # Esperar a que el servicio de snap se inicie
    if [[ "$USE_GUM" == true ]]; then
      gum spin --spinner dot --title "Esperando a que el servicio snapd se inicie..." -- sleep 5
    else
      echo "Esperando a que el servicio snapd se inicie..."
      sleep 5
    fi
    
    echo "Snapd instalado correctamente." >> "$LOG_FILE"
    
    # Asegurarse de que snap está disponible en el PATH
    export PATH=$PATH:/snap/bin
    
    # Verificar nuevamente si snap está disponible
    if ! command -v snap >/dev/null 2>&1; then
      echo "ERROR: Snap se instaló pero no está disponible en el PATH. Intente reiniciar su sesión." >&2
      echo "ERROR: Snap se instaló pero no está disponible en el PATH." >> "$LOG_FILE"
      return 1
    fi
  fi
  
  # Leer paquetes desde el archivo, excluyendo líneas de comentarios
  mapfile -t SNAP_PACKAGES < <(grep -vE '^\s*(#|$)' "$snap_pkg_file" | awk '{print $1}')
  
  if [[ ${#SNAP_PACKAGES[@]} -eq 0 ]]; then
    if [[ "$USE_GUM" == true ]]; then
      gum style --foreground 208 "No hay paquetes Snap para instalar."
    else
      echo "No hay paquetes Snap para instalar."
    fi
    echo "No hay paquetes Snap para instalar desde $snap_pkg_file." >> "$LOG_FILE"
    return 0
  fi
  
  # Identificar paquetes que ya están instalados
  already_installed=()
  to_install=()
  
  for pkg in "${SNAP_PACKAGES[@]}"; do
    # Verificar si el paquete ya está instalado por snap
    if snap list 2>/dev/null | grep -q "^$pkg"; then
      already_installed+=("$pkg")
      continue
    fi
    
    # Verificar si el comando está disponible en el sistema (instalado por otros medios)
    if command -v "$pkg" >/dev/null 2>&1; then
      already_installed+=("$pkg")
      echo "El paquete $pkg está disponible en el sistema pero no fue instalado con snap." >> "$LOG_FILE"
      continue
    fi
    
    # Si no está instalado de ninguna forma, agregarlo a la lista de pendientes
    to_install+=("$pkg")
  done
  
  echo "DEBUG: Total paquetes: ${#SNAP_PACKAGES[@]}, Ya instalados: ${#already_installed[@]}, A instalar: ${#to_install[@]}" >> "$LOG_FILE"
  
  # Mostrar lista de paquetes a instalar y ya instalados
  if [[ "$USE_GUM" == true ]]; then
    gum style \
      --border double \
      --border-foreground 212 \
      --margin "1" \
      --padding "1 2" \
      "$(gum style --foreground 213 --bold "Paquetes Snap (${#SNAP_PACKAGES[@]} total)")"
    
    if [[ ${#already_installed[@]} -gt 0 ]]; then
      gum style --foreground 35 "✓ Ya instalados (${#already_installed[@]}):"
      for pkg in "${already_installed[@]}"; do
        echo "  - $pkg"
      done
    fi
    
    if [[ ${#to_install[@]} -gt 0 ]]; then
      gum style --foreground 39 "→ Paquetes a instalar (${#to_install[@]}):"
      for pkg in "${to_install[@]}"; do
        echo "  - $pkg"
      done
    else
      gum style --foreground 35 "✓ ¡Todos los paquetes Snap ya están instalados!"
      return 0
    fi
  else
    echo -e "\n=== Paquetes Snap (${#SNAP_PACKAGES[@]} total) ==="
    
    if [[ ${#already_installed[@]} -gt 0 ]]; then
      echo -e "\n✓ Ya instalados (${#already_installed[@]}):"
      for pkg in "${already_installed[@]}"; do
        echo "  - $pkg"
      done
    fi
    
    if [[ ${#to_install[@]} -gt 0 ]]; then
      echo -e "\n→ Paquetes a instalar (${#to_install[@]}):"
      for pkg in "${to_install[@]}"; do
        echo "  - $pkg"
      done
    else
      echo -e "\n✓ ¡Todos los paquetes Snap ya están instalados!"
      return 0
    fi
    
    echo "======================================================"
  fi
  
  echo "Paquetes Snap a instalar: ${to_install[*]}" >> "$LOG_FILE"
  
  # Instalar cada paquete
  local success_count=0
  local failed_packages=()
  local total_packages=${#to_install[@]}
  
  for ((i=0; i<total_packages; i++)); do
    pkg="${to_install[$i]}"
    
    if [[ "$USE_GUM" == true ]]; then
      gum style --foreground 39 "⟢ Instalando $pkg ($(($i+1))/$total_packages) ⟣"
    else
      echo -e "\n[$((i+1))/$total_packages] Instalando: $pkg"
    fi
    
    echo "Instalando paquete Snap: $pkg" >> "$LOG_FILE"
    
    # Ejecutar el comando con salida detallada
    snap_output=$(snap install "$pkg" 2>&1)
    snap_result=$?
    echo "Salida del comando snap install $pkg: $snap_output" >> "$LOG_FILE"
    
    if [[ $snap_result -eq 0 ]]; then
      ((success_count++))
      if [[ "$USE_GUM" == true ]]; then
        gum style --foreground 35 "✓ $pkg instalado correctamente"
      else
        echo "✓ $pkg instalado correctamente"
      fi
    else
      failed_packages+=("$pkg")
      if [[ "$USE_GUM" == true ]]; then
        gum style --foreground 196 "✗ Error al instalar $pkg: $snap_output"
      else
        echo "✗ Error al instalar $pkg: $snap_output"
      fi
      echo "ERROR: Falló la instalación del paquete Snap: $pkg - $snap_output" >> "$LOG_FILE"
    fi
    
    # Pequeña pausa para visualización
    if [[ "$USE_GUM" == true ]]; then
      sleep 0.5
    fi
  done
  
  # Resumen final
  if [[ "$USE_GUM" == true ]]; then
    gum style \
      --border normal \
      --border-foreground 39 \
      --margin "1" \
      --padding "1 2" \
      "$(gum style --foreground 147 --bold "Resumen de la instalación de Snap:")" \
      "$(if [[ ${#already_installed[@]} -gt 0 ]]; then gum style --foreground 35 "✓ Paquetes ya instalados: ${#already_installed[@]}"; fi)" \
      "$(gum style --foreground 35 "✓ Paquetes instalados correctamente: $success_count/$total_packages")" \
      "$(if [[ ${#failed_packages[@]} -gt 0 ]]; then gum style --foreground 196 "✗ Paquetes con errores: ${#failed_packages[@]}"; for p in "${failed_packages[@]}"; do echo "  - $p"; done; fi)"
  else
    echo -e "\n=== Resumen de la instalación de Snap ==="
    if [[ ${#already_installed[@]} -gt 0 ]]; then
      echo "✓ Paquetes ya instalados: ${#already_installed[@]}"
    fi
    echo "✓ Paquetes instalados correctamente: $success_count/$total_packages"
    if [[ ${#failed_packages[@]} -gt 0 ]]; then
      echo "✗ Paquetes con errores: ${#failed_packages[@]}"
      for p in "${failed_packages[@]}"; do
        echo "  - $p"
      done
    fi
  fi
  
  echo "Instalación de paquetes Snap completada. Éxito: $success_count/$total_packages. Fallidos: ${#failed_packages[@]}" >> "$LOG_FILE"
  
  if [[ ${#failed_packages[@]} -gt 0 ]]; then
    echo "ADVERTENCIA: Algunos paquetes Snap no pudieron ser instalados. Ver $LOG_FILE para detalles." >&2
    return 1
  fi
  
  return 0
}

# Función para instalar paquetes extras definidos por el usuario
install_extra_packages() {
  echo "Acción: Instalar paquetes extras"
  echo "Acción: Instalar paquetes extras" >> "$LOG_FILE"
  
  # Determinar el archivo de paquetes extras según el SO
  local extras_pkg_file=""
  case "$OS" in
    macos)
      extras_pkg_file="${CONFIG_DIR}/macos-extras.pkg"
      ;;
    debian)
      extras_pkg_file="${CONFIG_DIR}/debian-extras.pkg"
      ;;
    fedora)
      extras_pkg_file="${CONFIG_DIR}/fedora-extras.pkg"
      ;;
    redhat)
      extras_pkg_file="${CONFIG_DIR}/redhat-extras.pkg"
      ;;
    arch)
      extras_pkg_file="${CONFIG_DIR}/arch-extras.pkg"
      ;;
    suse)
      extras_pkg_file="${CONFIG_DIR}/suse-extras.pkg"
      ;;
    freebsd)
      extras_pkg_file="${CONFIG_DIR}/freebsd-extras.pkg"
      ;;
    *)
      echo "Sistema operativo no soportado para paquetes extras: $OS" >> "$LOG_FILE"
      return 0
      ;;
  esac
  
  # Verificar si existe el archivo de paquetes extras
  if [[ ! -f "$extras_pkg_file" ]]; then
    echo "No se encontró el archivo de paquetes extras: $extras_pkg_file" >> "$LOG_FILE"
    echo "Omitiendo la instalación de paquetes extras."
    return 0
  fi
  
  # Verificar conectividad a internet
  check_internet_connection
  if [[ "$INTERNET_AVAILABLE" == false ]]; then
    echo "ADVERTENCIA: Sin conexión a internet. No se pueden instalar paquetes extras." >&2
    echo "ADVERTENCIA: Sin conexión a internet. No se pueden instalar paquetes extras." >> "$LOG_FILE"
    return 1
  fi
  
  # Leer paquetes desde el archivo, excluyendo líneas de comentarios
  mapfile -t EXTRAS_TO_INSTALL < <(grep -vE '^\s*(#|$)' "$extras_pkg_file" | awk '{print $1}')
  
  if [[ ${#EXTRAS_TO_INSTALL[@]} -eq 0 ]]; then
    echo "No hay paquetes extras para instalar desde $extras_pkg_file."
    echo "No hay paquetes extras para instalar desde $extras_pkg_file." >> "$LOG_FILE"
    return 0
  fi
  
  echo "Paquetes extras a instalar: ${EXTRAS_TO_INSTALL[*]}" >> "$LOG_FILE"
  
  # Identificar paquetes que ya están instalados
  already_installed=()
  to_install=()
  
  for pkg in "${EXTRAS_TO_INSTALL[@]}"; do
    if [[ "$(is_package_installed "$pkg")" == "true" ]]; then
      already_installed+=("$pkg")
    else
      to_install+=("$pkg")
    fi
  done
  
  # Mostrar lista de paquetes a instalar y ya instalados
  echo -e "\n=== Paquetes extras (${#EXTRAS_TO_INSTALL[@]} total) ==="
  
  if [[ ${#already_installed[@]} -gt 0 ]]; then
    echo -e "\n✓ Ya instalados (${#already_installed[@]}):"
    for pkg in "${already_installed[@]}"; do
      echo "  - $pkg"
    done
  fi
  
  if [[ ${#to_install[@]} -gt 0 ]]; then
    echo -e "\n→ Paquetes a instalar (${#to_install[@]}):"
    for pkg in "${to_install[@]}"; do
      echo "  - $pkg"
    done
  else
    echo -e "\n✓ ¡Todos los paquetes extras ya están instalados!"
    return 0
  fi
  
  echo "======================================================"
  
  if [[ -n "$UPDATE_CMD" ]]; then
    echo "Actualizando repositorios antes de instalar paquetes extras..."
    if ! eval "$UPDATE_CMD" >> "$LOG_FILE" 2>&1; then
      echo "Error: Falló la actualización de repositorios. Ver $LOG_FILE para detalles." >&2
      echo "Posible causa: problemas de conexión a internet o repositorios no disponibles." >&2
      return 1
    fi
  fi
  
  # Instalar paquetes uno por uno para mayor visibilidad
  echo "Instalando paquetes extras..."
  local success_count=0
  local failed_packages=()
  local total_packages=${#to_install[@]}
  
  for ((i=0; i<total_packages; i++)); do
    pkg="${to_install[$i]}"
    echo -e "\n[$((i+1))/$total_packages] Instalando: $pkg"
    
    echo "Instalando paquete extra: $pkg" >> "$LOG_FILE"
    if eval "$INSTALL_CMD" "$pkg" >> "$LOG_FILE" 2>&1; then
      echo "✓ Paquete $pkg instalado correctamente"
      ((success_count++))
    else
      echo "✗ Error al instalar el paquete $pkg"
      failed_packages+=("$pkg")
      echo "ERROR: Falló la instalación del paquete: $pkg" >> "$LOG_FILE"
    fi
  done
  
  # Mostrar resumen de la instalación
  echo -e "\n=== Resumen de la instalación de paquetes extras ==="
  if [[ ${#already_installed[@]} -gt 0 ]]; then
    echo "✓ Paquetes ya instalados: ${#already_installed[@]}"
  fi
  echo "✓ Paquetes instalados correctamente: $success_count/$total_packages"
  if [[ ${#failed_packages[@]} -gt 0 ]]; then
    echo "✗ Paquetes con errores (${#failed_packages[@]}):"
    for p in "${failed_packages[@]}"; do
      echo "  - $p"
    done
    echo "Ver $LOG_FILE para más detalles."
    return 1
  fi
  
  echo "Instalación de paquetes extras completada."
  echo "Instalación de paquetes extras completada." >> "$LOG_FILE"
  return 0
}

# --- Funciones de Acción --- #

install_base_packages() {
  echo "Acción: Instalar paquetes base"
  echo "Acción: Instalar paquetes base" >> "$LOG_FILE"
  
  if [[ ! -f "$PKG_FILE" ]]; then
    error_exit "Archivo de paquetes base no encontrado: $PKG_FILE"
  fi
  
  # Verificar conectividad a internet
  check_internet_connection
  
  if [[ "$INTERNET_AVAILABLE" == false ]]; then
    echo "ADVERTENCIA: Sin conexión a internet. No se pueden instalar paquetes." >&2
    echo "ADVERTENCIA: Sin conexión a internet. No se pueden instalar paquetes." >> "$LOG_FILE"
    return 1
  fi

  mapfile -t PACKAGES_TO_INSTALL < <(grep -vE '^\s*(#|$)' "$PKG_FILE" | awk '{print $1}')

  if [[ ${#PACKAGES_TO_INSTALL[@]} -eq 0 ]]; then
    echo "No hay paquetes base para instalar desde $PKG_FILE."
    echo "No hay paquetes base para instalar desde $PKG_FILE." >> "$LOG_FILE"
    return 0
  fi

  echo "Paquetes base a instalar: ${PACKAGES_TO_INSTALL[*]}" >> "$LOG_FILE"
  
  # Identificar paquetes que ya están instalados
  already_installed=()
  to_install=()
  
  for pkg in "${PACKAGES_TO_INSTALL[@]}"; do
    if [[ "$(is_package_installed "$pkg")" == "true" ]]; then
      already_installed+=("$pkg")
    else
      to_install+=("$pkg")
    fi
  done
  
  # Mostrar lista de paquetes a instalar y ya instalados
  echo -e "\n=== Paquetes base (${#PACKAGES_TO_INSTALL[@]} total) ==="
  
  if [[ ${#already_installed[@]} -gt 0 ]]; then
    echo -e "\n✓ Ya instalados (${#already_installed[@]}):"
    for pkg in "${already_installed[@]}"; do
      echo "  - $pkg"
    done
  fi
  
  if [[ ${#to_install[@]} -gt 0 ]]; then
    echo -e "\n→ Paquetes a instalar (${#to_install[@]}):"
    for pkg in "${to_install[@]}"; do
      echo "  - $pkg"
    done
  else
    echo -e "\n✓ ¡Todos los paquetes base ya están instalados!"
    return 0
  fi
  
  echo "======================================================"

  if [[ -n "$UPDATE_CMD" ]]; then
    echo "Actualizando repositorios..."
    if ! eval "$UPDATE_CMD" >> "$LOG_FILE" 2>&1; then
      echo "Error: Falló la actualización de repositorios. Ver $LOG_FILE para detalles." >&2
      echo "Posible causa: problemas de conexión a internet o repositorios no disponibles." >&2
      return 1
    fi
  fi

  # Instalar paquetes uno por uno para mayor visibilidad
  echo "Instalando paquetes base..."
  local success_count=0
  local failed_packages=()
  local total_packages=${#to_install[@]}
  
  for ((i=0; i<total_packages; i++)); do
    pkg="${to_install[$i]}"
    echo -e "\n[$((i+1))/$total_packages] Instalando: $pkg"
    
    echo "Instalando paquete base: $pkg" >> "$LOG_FILE"
    if eval "$INSTALL_CMD" "$pkg" >> "$LOG_FILE" 2>&1; then
      echo "✓ Paquete $pkg instalado correctamente"
      ((success_count++))
    else
      echo "✗ Error al instalar el paquete $pkg"
      failed_packages+=("$pkg")
      echo "ERROR: Falló la instalación del paquete: $pkg" >> "$LOG_FILE"
    fi
  done
  
  # Mostrar resumen de la instalación
  echo -e "\n=== Resumen de la instalación de paquetes base ==="
  if [[ ${#already_installed[@]} -gt 0 ]]; then
    echo "✓ Paquetes ya instalados: ${#already_installed[@]}"
  fi
  echo "✓ Paquetes instalados correctamente: $success_count/$total_packages"
  if [[ ${#failed_packages[@]} -gt 0 ]]; then
    echo "✗ Paquetes con errores (${#failed_packages[@]}):"
    for p in "${failed_packages[@]}"; do
      echo "  - $p"
    done
    echo "Ver $LOG_FILE para más detalles."
    return 1
  fi

  echo "Instalación de paquetes base completada."
  echo "Instalación de paquetes base completada." >> "$LOG_FILE"
}

update_system_packages() {
  echo "Acción: Actualizar todos los paquetes del sistema"
  echo "Acción: Actualizar todos los paquetes del sistema" >> "$LOG_FILE"

  # Verificar conectividad a internet
  check_internet_connection
  
  if [[ "$INTERNET_AVAILABLE" == false ]]; then
    echo "ADVERTENCIA: Sin conexión a internet. No se pueden actualizar paquetes." >&2
    echo "ADVERTENCIA: Sin conexión a internet. No se pueden actualizar paquetes." >> "$LOG_FILE"
    return 1
  fi

  if [[ -z "$UPGRADE_CMD" ]]; then
    error_exit "El comando de actualización completa del sistema no está definido para $OS."
  fi

  if [[ -n "$UPDATE_CMD" ]]; then
     echo "Actualizando repositorios antes de la actualización completa..."
     if ! eval "$UPDATE_CMD" >> "$LOG_FILE" 2>&1; then
       echo "Error: Falló la actualización de repositorios previa a la actualización completa. Ver $LOG_FILE para detalles." >&2
       echo "Posible causa: problemas de conexión a internet o repositorios no disponibles." >&2
       return 1
     fi
  fi

  echo "Ejecutando la actualización completa del sistema..."
  if ! eval "$UPGRADE_CMD" >> "$LOG_FILE" 2>&1; then
    echo "Error: Falló la actualización completa del sistema. Ver $LOG_FILE para detalles." >&2
    echo "Posible causa: problemas de conexión a internet, repositorios no disponibles o conflictos de paquetes." >&2
    return 1
  fi

  echo "Actualización completa del sistema completada."
  echo "Actualización completa del sistema completada." >> "$LOG_FILE"
}

# ---- Procesamiento de argumentos ----
ACTION="help" # Acción por defecto es ahora mostrar la ayuda

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install)
      ACTION="install"
      OPERATION_MODE="install"
      shift # consume el argumento
      ;;
    --update)
      ACTION="update"
      OPERATION_MODE="update"
      shift # consume el argumento
      ;;
    --nosops)
      INSTALL_SOPS=false
      shift # consume el argumento
      ;;
    --sops)
      ONLY_SOPS=true
      INSTALL_SOPS=true
      shift # consume el argumento
      ;;
    --nosnap)
      NO_SNAP=true
      shift # consume el argumento
      ;;
    -h|--help)
      ACTION="help" # Asegurarse de que la acción sea help
      shift # opcionalmente consumir --help/-h si lo hubiera
      ;;
    *)
      echo "Argumento desconocido: $1." >&2
      ACTION="help" # Si hay argumento desconocido, mostrar ayuda
      break # Salir del bucle para procesar la acción 'help'
      ;;
  esac
done

# Validar combinaciones de parámetros
if [[ "$ONLY_SOPS" == true && "$ACTION" == "help" ]]; then
  error_exit "El parámetro --sops debe usarse solo en combinación con --install o --update."
elif [[ "$ONLY_SOPS" == true && "$INSTALL_SOPS" == false ]]; then
  error_exit "No se pueden usar --sops y --nosops juntos."
elif [[ "$NO_SNAP" == true && "$ACTION" != "install" ]]; then
  error_exit "El parámetro --nosnap solo puede usarse con --install, ya que snap tiene su propio mecanismo de actualización."
fi

# ---- Ejecución de la acción ----
# Solo detectar OS si la acción no es help, para evitar trabajo innecesario
if [[ "$ACTION" != "help" ]]; then
  detect_os
  # Verificar privilegios de root para acciones que lo requieren
  if [[ "$ACTION" == "install" || "$ACTION" == "update" ]]; then
    check_root
  fi
fi

case "$ACTION" in
  install)
    if [[ "$ONLY_SOPS" == true ]]; then
      # Si solo se quiere SOPS, solo intentamos instalar SOPS
      install_sops
    else
      # Instalar paquetes base
      install_base_packages
      
      # Instalar paquetes extras definidos por el usuario
      install_extra_packages
            
      # Verificar si se debe instalar Snap
      echo "Verificando si se deben instalar paquetes Snap..." >> "$LOG_FILE"
      echo "Verificando si se deben instalar paquetes Snap..."
      
      # Instalar paquetes snap si no se ha desactivado y es un sistema compatible
      if [[ "$NO_SNAP" == false ]]; then
        echo "Verificando instalación de paquetes Snap..." >> "$LOG_FILE"
        echo "Verificando instalación de paquetes Snap..."
        echo "DEBUG: NO_SNAP=$NO_SNAP, OS=$OS, lsb-release=$(test -f /etc/lsb-release && echo 'existe' || echo 'no existe'), snap.pkg=$(test -f ${CONFIG_DIR}/snap.pkg && echo 'existe' || echo 'no existe')" >> "$LOG_FILE"
        # Verifica si el sistema es Ubuntu genuino (no Mint ni otro derivado incompatible) 
        # y si existe snap.pkg antes de intentar instalar
        if [[ "$OS" == "debian" && -f /etc/lsb-release && -f "${CONFIG_DIR}/snap.pkg" ]]; then
          # Verificar si es un derivado que no usa Snap por defecto
          if ! grep -qi "mint\|elementary" /etc/os-release 2>/dev/null && \
             ! grep -qi "mint\|elementary" /etc/lsb-release 2>/dev/null; then
            echo "Sistema compatible con Snap detectado. Procediendo con la instalación de paquetes Snap." >> "$LOG_FILE"
            echo "Sistema compatible con Snap detectado. Procediendo con la instalación de paquetes Snap."
            install_snap_packages
          else
            echo "Sistema derivado de Ubuntu detectado. Omitiendo instalación de Snap." >> "$LOG_FILE"
            echo "Sistema derivado de Ubuntu detectado. Omitiendo instalación de Snap."
          fi
        else
          if [[ "$OS" != "debian" ]]; then
            echo "No es un sistema Debian/Ubuntu. Omitiendo instalación de Snap." >> "$LOG_FILE"
            echo "No es un sistema Debian/Ubuntu. Omitiendo instalación de Snap."
          elif [[ ! -f /etc/lsb-release ]]; then
            echo "No es un sistema basado en Ubuntu. Omitiendo instalación de Snap." >> "$LOG_FILE"
            echo "No es un sistema basado en Ubuntu. Omitiendo instalación de Snap."
          elif [[ ! -f "${CONFIG_DIR}/snap.pkg" ]]; then
            echo "No se encontró el archivo ${CONFIG_DIR}/snap.pkg. Omitiendo instalación de Snap." >> "$LOG_FILE"
            echo "No se encontró el archivo ${CONFIG_DIR}/snap.pkg. Omitiendo instalación de Snap."
          fi
        fi
      else
        echo "Instalación de Snap desactivada con --nosnap." >> "$LOG_FILE"
        echo "Instalación de Snap desactivada con --nosnap."
      fi

            # Verificar/instalar SOPS después si está habilitado
      if [[ "$INSTALL_SOPS" == true ]]; then
        install_sops
      fi
      
    fi
    ;;
  update)
    if [[ "$ONLY_SOPS" == true ]]; then
      # Si solo se quiere SOPS, solo intentamos actualizar SOPS
      install_sops
    else
      # Actualizar sistema
      update_system_packages
      # Verificar/actualizar SOPS después si está habilitado
      if [[ "$INSTALL_SOPS" == true ]]; then
        install_sops
      fi
      # No actualizamos paquetes snap porque tienen su propio mecanismo de actualización automática
    fi
    ;;
  help)
    # Mostrar banner antes de la ayuda
    show_banner
    echo "Uso: $0 [--install | --update] [--sops | --nosops] [--nosnap] | [--help]"
    echo
    echo "Descripción:"
    echo "  Herramienta para gestionar paquetes base en diferentes sistemas operativos."
    echo "  Instala paquetes esenciales o actualiza el sistema según el SO detectado."
    echo "  También puede instalar paquetes extras y herramientas adicionales como SOPS."
    echo
    echo "Parámetros principales:"
    echo "  --install  : Instala los paquetes base definidos en config/[os]-base.pkg."
    echo "               También instala paquetes extras desde config/[os]-extras.pkg si existe."
    echo "               Si se usa con --sops, instala SOPS solo si no está instalado."
    echo "  --update   : Actualiza todos los paquetes instalados en el sistema."
    echo "               Si se usa con --sops, actualiza SOPS solo si hay versión nueva."
    echo "  --help     : Muestra esta ayuda."
    echo
    echo "Parámetros adicionales:"
    echo "  --sops     : Instala o actualiza únicamente SOPS (Mozilla Secrets OPerationS)."
    echo "               Debe usarse en combinación con --install o --update."
    echo "  --nosops   : Evita la instalación/actualización de SOPS al usar --install o --update."
    echo "  --nosnap   : Evita la instalación automática de paquetes Snap al usar --install."
    echo "               Solo aplica con --install, ya que Snap tiene su propio mecanismo de actualización."
    echo
    echo " Acción por defecto si no se especifican parámetros: --help"
    echo
    echo " Sistemas Operativos Soportados:"
    echo "   - Debian / Ubuntu y derivados (apt-get) [debian]"
    echo "   - Red Hat / CentOS / Rocky Linux / AlmaLinux y derivados (dnf/yum) [redhat]"
    echo "   - Fedora (dnf) [fedora]"
    echo "   - Arch Linux y derivados (pacman) [arch]"
    echo "   - SUSE / openSUSE (zypper) [suse]"
    echo "   - FreeBSD (pkg) [freebsd]"
    echo "   - macOS (Homebrew) [macos]"
    exit 0
    ;;
  *)
    # Esto no debería ocurrir
    error_exit "Acción desconocida interna: $ACTION"
    ;;
esac

echo "--- Fin de ejecución: $(date) ---" >> "$LOG_FILE"
exit 0
