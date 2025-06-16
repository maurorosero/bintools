#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Check Heading
# Copyright (C) <2025> MAURO ROSERO PÉREZ
#
# Script Name: packages.sh
# Author:      Mauro Rosero P. <mauro.rosero@gmail.com>
# Assistant:   Cursor AI (https://cursor.com)
# Created at:  2025-06-14 20:53:10
# Modified:    2025-06-16 17:55:20
# Description: Script para instalar y actualizar paquetes del sistema en diferentes distribuciones Linux y macOS, incluyendo SOPS.
# Version:     0.1.12
#
# Usage: packages.sh [opciones]
#
# Exit codes:
#   0 - Éxito
#   1 - Error general (ej: fallo en instalación de paquetes)
#   2 - Error de sintaxis (ej: comando inválido)
#   3 - Error de permisos (ej: no sudo)
#   4 - Error de dependencias (ej: pip no instalado)
#   5 - Error de configuración (ej: archivo de configuración corrupto)
#   6 - Error de sistema operativo no soportado
#   7 - Error de red (ej: no hay conexión)
#   8 - Error de espacio en disco


set -uo pipefail

# --- Banner --- #
APP_NAME="Personal Packages Installer"
APP_VERSION="0.9.4 (2025/04)"
APP_AUTHOR="Mauro Rosero Pérez (mauro.rosero@gmail.com)"

# Capturar los argumentos originales
ORIGINAL_ARGS=("$@")

# Colores y formatos (añadir al inicio de la sección Variables globales)
COLOR_GREEN="\033[0;32m"
COLOR_YELLOW="\033[0;33m"
COLOR_RED="\033[0;31m"
COLOR_CYAN="\033[0;36m"
COLOR_BLUE="\033[0;34m"
COLOR_MAGENTA="\033[0;35m"
COLOR_RESET="\033[0m"
BOLD="\033[1m"

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
  LOG_DIR="$USER_HOME/.logs"
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
      # En Debian/Ubuntu - verificación mejorada
      if dpkg -s "$pkg" &>/dev/null; then
        is_installed=true
      else
        # Verificaciones adicionales para ciertos paquetes
        case "$pkg" in
          arduino-core)
            # Arduino core puede instalarse como arduino-core-avr
            if apt list --installed 2>/dev/null | grep -q "arduino-core"; then
              is_installed=true
              echo "INFO: arduino-core detectado mediante apt list" >> "$LOG_FILE"
            fi
            ;;
          netcat)
            # netcat puede estar como netcat-openbsd o netcat-traditional
            if command -v nc &>/dev/null || dpkg -s "netcat-openbsd" &>/dev/null || dpkg -s "netcat-traditional" &>/dev/null; then
              is_installed=true
              echo "INFO: Implementación de netcat detectada" >> "$LOG_FILE"
            fi
            ;;
          awscli)
            # awscli podría estar instalado vía pip
            if command -v aws &>/dev/null; then
              is_installed=true
              echo "INFO: awscli detectado en el PATH" >> "$LOG_FILE"
            fi
            ;;
          *)
            # Verificación genérica adicional, útil para paquetes instalados por diversos medios
            if command -v "$pkg" &>/dev/null; then
              is_installed=true
              echo "INFO: $pkg detectado como comando disponible" >> "$LOG_FILE"
            elif apt list --installed 2>/dev/null | grep -qi "$pkg"; then
              is_installed=true
              echo "INFO: Posible variante de $pkg detectada con apt list" >> "$LOG_FILE"
            fi
            ;;
        esac
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

# Función para mostrar un mensaje de acción con formato atractivo
show_action() {
  local action="$1"
  local width=60
  local padding=2
  local border=$(printf '%*s' $((width-4)) '' | tr ' ' '-')

  echo
  echo -e "${COLOR_MAGENTA}${BOLD}+${border}+${COLOR_RESET}"
  printf "${COLOR_MAGENTA}${BOLD}|${COLOR_RESET}${COLOR_CYAN} %-$((width-padding-2))s${COLOR_MAGENTA}${BOLD}|${COLOR_RESET}\n" "$action"
  echo -e "${COLOR_MAGENTA}${BOLD}+${border}+${COLOR_RESET}"
  echo

  # También registrar en el log pero sin formato
  echo "Acción: $action" >> "$LOG_FILE"
}

# Añadir una nueva función para mostrar inicio de instalación
show_install_start() {
  local type="$1"
  local count="$2"

  echo
  echo -e "${COLOR_CYAN}${BOLD}▶ Iniciando instalación de paquetes $type...${COLOR_RESET}"
  echo -e "${COLOR_CYAN}${BOLD}  Total de paquetes a instalar: $count${COLOR_RESET}"
  echo -e "${COLOR_CYAN}${BOLD}  $(date '+%H:%M:%S')${COLOR_RESET}"
  echo -e "${COLOR_CYAN}${BOLD}▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔${COLOR_RESET}"
  echo
}

# Añadir una función para mostrar progreso de paquete
show_package_progress() {
  local current="$1"
  local total="$2"
  local pkg="$3"

  echo
  local progress=$((current * 100 / total))
  local bar_width=30
  local fill_width=$((progress * bar_width / 100))
  local empty_width=$((bar_width - fill_width))

  local bar=""
  if [[ $fill_width -gt 0 ]]; then
    bar=$(printf '%*s' $fill_width '' | tr ' ' '█')
  fi
  if [[ $empty_width -gt 0 ]]; then
    bar="${bar}$(printf '%*s' $empty_width '' | tr ' ' '░')"
  fi

  echo -e "${COLOR_BLUE}${BOLD}[$current/$total]${COLOR_RESET} ${COLOR_YELLOW}$pkg${COLOR_RESET}"
  echo -e "${COLOR_BLUE}[${bar}] ${progress}%${COLOR_RESET}"
}

# Añadir función para mostrar éxito o error en la instalación
show_package_result() {
  local result="$1"
  local pkg="$2"
  local duration="$3"

  if [[ "$result" == "success" ]]; then
    echo -e "  ${COLOR_GREEN}${BOLD}✓ Paquete $pkg instalado correctamente ${COLOR_RESET}${COLOR_CYAN}(${duration}s)${COLOR_RESET}"
  elif [[ "$result" == "already" ]]; then
    echo -e "  ${COLOR_GREEN}${BOLD}✓ El paquete $pkg ya está instalado ${COLOR_RESET}"
  elif [[ "$result" == "partial" ]]; then
    echo -e "  ${COLOR_GREEN}${BOLD}✓ El paquete $pkg se instaló a pesar del error ${COLOR_RESET}${COLOR_CYAN}(${duration}s)${COLOR_RESET}"
  else
    echo -e "  ${COLOR_RED}${BOLD}✗ Error al instalar el paquete $pkg ${COLOR_RESET}${COLOR_CYAN}(${duration}s)${COLOR_RESET}"
    # Sugerir alternativas o soluciones según el paquete
    case "$pkg" in
      python3-distutils)
        echo -e "  ${COLOR_YELLOW}  ↳ Sugerencia: Prueba instalar 'python3-dev' que incluye distutils${COLOR_RESET}"
        ;;
      awscli)
        echo -e "  ${COLOR_YELLOW}  ↳ Sugerencia: Considera usar 'pip install awscli' como alternativa${COLOR_RESET}"
        ;;
      netcat)
        echo -e "  ${COLOR_YELLOW}  ↳ Sugerencia: Prueba con paquetes alternativos como 'nc' o 'ncat'${COLOR_RESET}"
        ;;
      *)
        echo -e "  ${COLOR_YELLOW}  ↳ Consulta los logs para más detalles: $LOG_FILE${COLOR_RESET}"
        ;;
    esac
  fi
}

# Añadir una función para mostrar mensaje de finalización con formato
show_completion_message() {
  local message="$1"

  echo
  echo -e "${COLOR_GREEN}${BOLD}✓ ${message}${COLOR_RESET}"
  printf '%*s\n' 60 '' | tr ' ' '─'
  echo

  # También registrar en el log pero sin formato
  echo "Completado: $message" >> "$LOG_FILE"
}

# Añadir después de show_completion_message
# Añadir una función para mostrar mensajes de verificación con formato
show_verification_message() {
  local message="$1"

  echo
  echo -e "${COLOR_BLUE}${BOLD}♦ ${message}${COLOR_RESET}"
  echo

  # También registrar en el log pero sin formato
  echo "Verificación: $message" >> "$LOG_FILE"
}

# Añadir función para mostrar mensajes de estado
show_status() {
  local message="$1"

  echo
  echo -e "${COLOR_CYAN}${BOLD}• ${message}${COLOR_RESET}"

  # También registrar en el log pero sin formato
  echo "Estado: $message" >> "$LOG_FILE"
}

# Añadir función para mostrar mensajes de éxito
show_success() {
  local message="$1"

  echo
  echo -e "${COLOR_GREEN}${BOLD}✓ ${message}${COLOR_RESET}"

  # También registrar en el log pero sin formato
  echo "Éxito: $message" >> "$LOG_FILE"
}

# Añadir función para mostrar mensajes de advertencia
show_warning() {
  local message="$1"

  echo
  echo -e "${COLOR_YELLOW}${BOLD}⚠ ${message}${COLOR_RESET}"

  # También registrar en el log pero sin formato
  echo "Advertencia: $message" >> "$LOG_FILE"
}

# Añadir función para mostrar mensajes de error
show_error() {
  local message="$1"

  echo
  echo -e "${COLOR_RED}${BOLD}✗ ${message}${COLOR_RESET}"

  # También registrar en el log pero sin formato
  echo "Error: $message" >> "$LOG_FILE"
}

# Actualiza la función install_sops para usar get_latest_sops_version
install_sops() {
  show_action "Instalar/Actualizar SOPS"

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

    show_status "SOPS ya está instalado (versión $current_version)"

    # Comparar versión actual con versión disponible si la versión actual no es desconocida
    if [[ "$current_version" != "desconocida" ]]; then
      compare_versions "$latest_version" "$current_version"
      local compare_result=$?

      if [[ $compare_result -eq 0 ]]; then
        # Versión disponible es mayor que la instalada
        need_update=true
        show_status "Hay una nueva versión disponible: $latest_version"
      elif [[ $compare_result -eq 2 ]]; then
        # Versiones iguales
        show_success "SOPS ya está en la última versión ($current_version)"
      else
        # La versión instalada es mayor que la disponible (raro, pero posible)
        show_warning "La versión instalada ($current_version) es más reciente que la versión de referencia ($latest_version)"
      fi
    else
      # Si no se pudo determinar la versión actual, asumir que necesita actualización
      need_update=true
      show_warning "No se pudo determinar la versión instalada. Versión disponible: $latest_version"
    fi
  else
    # SOPS no está instalado
    is_installed=false
    need_update=true
    show_status "SOPS no está instalado. Versión disponible: $latest_version"
  fi

  # Determinar si se debe instalar/actualizar según el modo de operación
  local should_install=false

  if [[ "$OPERATION_MODE" == "install" ]]; then
    # En modo install, instalar solo si no está instalado
    if [[ "$is_installed" == false ]]; then
      should_install=true
      show_status "Procediendo con la instalación de SOPS..."
    else
      show_status "No se realizará la instalación porque SOPS ya está instalado"
    fi
  elif [[ "$OPERATION_MODE" == "update" ]]; then
    # En modo update, actualizar solo si está instalado y hay una versión más reciente
    if [[ "$is_installed" == true && "$need_update" == true ]]; then
      should_install=true
      show_status "Procediendo con la actualización de SOPS a la versión $latest_version..."
    else
      if [[ "$is_installed" == false ]]; then
        show_status "No se realizará la actualización porque SOPS no está instalado"
      else
        show_status "No se realizará la actualización porque SOPS ya está en la última versión"
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
    show_error "Se requiere conexión a internet para instalar/actualizar SOPS"
    return 1
  fi

  # Determinar método de instalación según el SO
  case "$OS" in
    macos)
      show_status "Instalando/Actualizando SOPS vía Homebrew..."
      if brew install sops >> "$LOG_FILE" 2>&1; then
        show_success "SOPS instalado/actualizado correctamente vía Homebrew"
      else
        show_error "Falló la instalación de SOPS vía Homebrew. Ver $LOG_FILE para detalles"
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
        *)
          show_error "Arquitectura no soportada para SOPS: $arch"
          return 1
          ;;
      esac

      # Asegurarse de que tenemos los comandos necesarios
      for cmd in curl; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
          show_status "Instalando dependencia: $cmd..."
          if eval "$INSTALL_CMD" "$cmd" >> "$LOG_FILE" 2>&1; then
            show_success "Dependencia $cmd instalada correctamente"
          else
            show_error "No se pudo instalar $cmd, necesario para la instalación de SOPS"
            return 1
          fi
        fi
      done

      show_status "Usando versión de SOPS: $latest_version"

      # Descargar el binario
      local temp_dir
      temp_dir=$(mktemp -d)

      # Construir URL
      local download_url="https://github.com/mozilla/sops/releases/download/v${latest_version}/sops-v${latest_version}.linux.${target_arch}"

      show_status "Descargando SOPS desde: $download_url"

      if ! curl -L -s -o "$temp_dir/sops" "$download_url"; then
        show_warning "Falló la descarga desde $download_url - intentando URL alternativa..."

        # Probar URL alternativa sin 'v' en el nombre del archivo
        download_url="https://github.com/mozilla/sops/releases/download/v${latest_version}/sops-${latest_version}.linux.${target_arch}"
        show_status "Intentando con URL alternativa: $download_url"

        if ! curl -L -s -o "$temp_dir/sops" "$download_url"; then
          # Probar otra variante de URL
          download_url="https://github.com/getsops/sops/releases/download/v${latest_version}/sops-v${latest_version}.linux.${target_arch}"
          show_status "Intentando con segunda URL alternativa: $download_url"

          if ! curl -L -s -o "$temp_dir/sops" "$download_url"; then
            show_error "Falló la descarga de SOPS desde GitHub usando todos los formatos de URL"
            rm -rf "$temp_dir"
            return 1
          fi
        fi
      fi

      # Verificar que el archivo se descargó correctamente
      if [[ ! -s "$temp_dir/sops" ]]; then
        show_error "Archivo descargado está vacío o no existe"
        rm -rf "$temp_dir"
        return 1
      fi

      # Hacer ejecutable e instalar
      chmod +x "$temp_dir/sops"
      if mv "$temp_dir/sops" /usr/local/bin/sops; then
        show_success "SOPS instalado en /usr/local/bin/sops"
      else
        show_error "No se pudo mover el binario de SOPS a /usr/local/bin/"
        rm -rf "$temp_dir"
        return 1
      fi

      # Limpiar
      rm -rf "$temp_dir"
      ;;
    arch)
      # En Arch Linux, SOPS está disponible en los repositorios community
      show_status "Instalando/Actualizando SOPS desde los repositorios de Arch..."
      if pacman -S --noconfirm sops >> "$LOG_FILE" 2>&1; then
        show_success "SOPS instalado/actualizado correctamente desde los repositorios de Arch"
      else
        show_error "Falló la instalación de SOPS desde los repositorios de Arch. Ver $LOG_FILE para detalles"
        return 1
      fi
      ;;
    freebsd)
      # En FreeBSD, SOPS está disponible en los ports
      show_status "Instalando/Actualizando SOPS desde los ports de FreeBSD..."
      if pkg install -y sops >> "$LOG_FILE" 2>&1; then
        show_success "SOPS instalado/actualizado correctamente desde los ports de FreeBSD"
      else
        show_error "Falló la instalación de SOPS desde los ports de FreeBSD. Ver $LOG_FILE para detalles"
        return 1
      fi
      ;;
    *)
      show_error "Instalación de SOPS no implementada para este sistema operativo: $OS"
      return 1
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

    show_success "SOPS instalado/actualizado correctamente (versión $installed_version)"
    return 0
  else
    show_error "No se pudo verificar la instalación de SOPS"
    return 1
  fi
}

# Función para instalar paquetes Snap
install_snap_packages() {
  # Función para instalar paquetes del repositorio Snap
  local result=0
  local os_name=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')
  local snap_list=""

  show_action "Instalar paquetes Snap"

  # Verificar que sea un sistema apto para Snap
  if [ "$os_name" != "ubuntu" ]; then
    echo "ADVERTENCIA: Snap solo está soportado oficialmente en Ubuntu, la instalación podría fallar." >> "$LOG_FILE"
    show_warning "Snap solo está soportado oficialmente en Ubuntu, la instalación podría fallar"
  fi

  # Verificar conexión a internet
  if ! check_internet_connection; then
    echo "ERROR: No hay conexión a Internet. No se pueden instalar paquetes Snap." >> "$LOG_FILE"
    show_error "No hay conexión a Internet. No se pueden instalar paquetes Snap"
    return 1
  fi

  # Verificar que snapd esté instalado
  if ! command -v snap &> /dev/null; then
    echo "El servicio snap no está instalado. Intentando instalar snapd..." >> "$LOG_FILE"
    show_status "El servicio snap no está instalado. Intentando instalar snapd..."

    if [[ "$os_name" == "ubuntu" || "$os_name" == "debian" ]]; then
      sudo apt-get update &>> "$LOG_FILE"
      sudo apt-get install -y snapd &>> "$LOG_FILE"
      result=$?
      if [ $result -ne 0 ]; then
        echo "ERROR: No se pudo instalar snapd. Código de error: $result" >> "$LOG_FILE"
        show_error "No se pudo instalar snapd. Código de error: $result"
        return 1
      else
        echo "Instalación de snapd completada correctamente." >> "$LOG_FILE"
        show_success "Instalación de snapd completada correctamente"
      fi
    else
      echo "ADVERTENCIA: No se puede instalar snapd automáticamente en este sistema." >> "$LOG_FILE"
      show_warning "No se puede instalar snapd automáticamente en este sistema"
      return 1
    fi
  else
    echo "El servicio snapd ya está instalado." >> "$LOG_FILE"
    show_status "El servicio snapd ya está instalado"
  fi

  # Leer archivo de paquetes snap y filtrar comentarios y líneas vacías
  if [ -f "${CONFIG_DIR}/snap.pkg" ]; then
    mapfile -t snap_packages < <(grep -v "^\s*#\|^\s*$" "${CONFIG_DIR}/snap.pkg")

    # Verificar paquetes ya instalados
    local installed_count=0
    local already_installed=()
    local to_install=()

    echo "Verificando paquetes snap instalados..." >> "$LOG_FILE"

    for package in "${snap_packages[@]}"; do
      # Extraer nombre y parámetros si los hay
      local pkg_name
      local params=""

      if [[ "$package" == *" "* ]]; then
        pkg_name=$(echo "$package" | cut -d' ' -f1)
        params=$(echo "$package" | cut -d' ' -f2-)
      else
        pkg_name="$package"
      fi

      # Verificar si el paquete ya está instalado vía snap
      if snap list | grep -q "^$pkg_name "; then
        echo "Paquete snap '$pkg_name' ya instalado vía Snap." >> "$LOG_FILE"
        already_installed+=("$pkg_name")
        continue
      fi

      # Verificar si el comando asociado al paquete está disponible por otros medios
      local cmd_exists=false
      local binary_names=()

      # Mapeo de nombres de paquetes snap a posibles comandos/binarios
      case "$pkg_name" in
        chromium)
          binary_names=("chromium" "chromium-browser" "google-chrome" "chrome")
          ;;
        firefox)
          binary_names=("firefox" "firefox-esr")
          ;;
        vlc)
          binary_names=("vlc")
          ;;
        code|vscode)
          binary_names=("code" "vscode" "codium" "vscodium")
          ;;
        spotify)
          binary_names=("spotify")
          ;;
        slack)
          binary_names=("slack")
          ;;
        discord)
          binary_names=("discord")
          ;;
        gimp)
          binary_names=("gimp")
          ;;
        inkscape)
          binary_names=("inkscape")
          ;;
        *)
          # Para otros paquetes, usar el mismo nombre
          binary_names=("$pkg_name")
          ;;
      esac

      # Verificar si alguno de los binarios está disponible
      for binary in "${binary_names[@]}"; do
        if command -v "$binary" &>/dev/null; then
          cmd_exists=true
          echo "Paquete '$pkg_name' disponible como comando '$binary' en el sistema." >> "$LOG_FILE"
          break
        fi
      done

      # Si es un sistema Debian/Ubuntu, verificar instalación vía apt
      if [[ "$os_name" == "ubuntu" || "$os_name" == "debian" ]]; then
        # Mapeo de nombres de paquetes snap a posibles paquetes apt
        local apt_pkgs=()
        case "$pkg_name" in
          chromium)
            apt_pkgs=("chromium-browser" "chromium")
            ;;
          firefox)
            apt_pkgs=("firefox" "firefox-esr")
            ;;
          *)
            # Para otros paquetes, intentamos el mismo nombre
            apt_pkgs=("$pkg_name")
            ;;
        esac

        # Verificar instalación vía apt
        for apt_pkg in "${apt_pkgs[@]}"; do
          if dpkg -l | grep -q "ii  $apt_pkg "; then
            cmd_exists=true
            echo "Paquete '$pkg_name' instalado vía APT como '$apt_pkg'." >> "$LOG_FILE"
            break
          fi
        done
      fi

      # Verificar instalación vía flatpak si está disponible
      if command -v flatpak &>/dev/null; then
        if flatpak list | grep -qi "$pkg_name"; then
          cmd_exists=true
          echo "Paquete '$pkg_name' instalado vía Flatpak." >> "$LOG_FILE"
        fi
      fi

      # Si el comando existe o está instalado por otros medios, marcarlo como ya instalado
      if [[ "$cmd_exists" == true ]]; then
        already_installed+=("$pkg_name (instalado por otro método)")
        echo "Paquete '$pkg_name' ya disponible en el sistema por un método alternativo. No se instalará vía Snap." >> "$LOG_FILE"
      else
        to_install+=("$package")
      fi
    done

    # Mostrar lista de paquetes a instalar y ya instalados
    show_title "PAQUETES SNAP (${#snap_packages[@]} total)"

    show_packages_list "Paquetes ya instalados" "$COLOR_GREEN" "${already_installed[@]}"
    show_pending_packages "Paquetes a instalar" "$COLOR_YELLOW" "${to_install[@]}"

    # Informar paquetes ya instalados
    if [ ${#already_installed[@]} -eq ${#snap_packages[@]} ]; then
      echo -e "\n${COLOR_GREEN}${BOLD}✓ ¡Todos los paquetes Snap ya están instalados!${COLOR_RESET}"
      return 0
    fi

    # Instalar paquetes pendientes
    if [ ${#to_install[@]} -gt 0 ]; then
      echo "Instalando ${#to_install[@]} paquetes snap pendientes..." >> "$LOG_FILE"

      show_install_start "Snap" "${#to_install[@]}"

      local success_count=0
      local failed_packages=()
      local total_packages=${#to_install[@]}

      for ((i=0; i<total_packages; i++)); do
        package="${to_install[$i]}"

        # Extraer nombre y parámetros si los hay
        local pkg_name
        local params=""

        if [[ "$package" == *" "* ]]; then
          pkg_name=$(echo "$package" | cut -d' ' -f1)
          params=$(echo "$package" | cut -d' ' -f2-)
        else
          pkg_name="$package"
        fi

        show_package_progress $((i+1)) $total_packages "$pkg_name"

        echo "Instalando snap '$package'..." >> "$LOG_FILE"

        # Medir el tiempo de instalación
        start_time=$(date +%s)

        # Instalar el paquete con o sin parámetros
        set +e  # Desactivar salida por error temporalmente para este comando
        if [ -n "$params" ]; then
          sudo snap install "$pkg_name" $params &>> "$LOG_FILE"
        else
          sudo snap install "$pkg_name" &>> "$LOG_FILE"
        fi

        result=$?
        end_time=$(date +%s)
        duration=$((end_time - start_time))

        if [ $result -ne 0 ]; then
          echo "ERROR: No se pudo instalar el paquete snap '$package'. Código de error: $result" >> "$LOG_FILE"
          show_package_result "error" "$pkg_name" "$duration"
          failed_packages+=("$pkg_name")
        else
          echo "Paquete snap '$package' instalado correctamente." >> "$LOG_FILE"
          show_package_result "success" "$pkg_name" "$duration"
          ((success_count++))
        fi
        set -u  # Reactivar opciones pero sin incluir -e
      done

      # Mostrar resumen de la instalación
      show_title "RESUMEN DE INSTALACIÓN"
      if [[ ${#already_installed[@]} -gt 0 ]]; then
        echo -e "${COLOR_GREEN}✓ Paquetes ya instalados: ${#already_installed[@]}${COLOR_RESET}"
      fi
      echo -e "${COLOR_GREEN}✓ Paquetes instalados correctamente: $success_count/$total_packages${COLOR_RESET}"

      if [[ ${#failed_packages[@]} -gt 0 ]]; then
        echo -e "${COLOR_RED}✗ Paquetes con errores (${#failed_packages[@]}):${COLOR_RESET}"
        for p in "${failed_packages[@]}"; do
          echo -e "${COLOR_RED}  - $p${COLOR_RESET}"
        done
        echo -e "${COLOR_YELLOW}Ver $LOG_FILE para más detalles.${COLOR_RESET}"
      fi

      show_completion_message "Instalación de paquetes Snap completada"
    fi
  else
    echo "ERROR: El archivo de paquetes snap '${CONFIG_DIR}/snap.pkg' no existe." >> "$LOG_FILE"
    show_error "El archivo de paquetes Snap '${CONFIG_DIR}/snap.pkg' no existe"
    return 1
  fi

  return 0
}

# Función para instalar paquetes extras definidos por el usuario
install_extra_packages() {
  show_action "Instalar paquetes extras"

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
  show_title "PAQUETES EXTRAS (${#EXTRAS_TO_INSTALL[@]} total)"

  show_packages_list "Paquetes ya instalados" "$COLOR_GREEN" "${already_installed[@]}"
  show_pending_packages "Paquetes a instalar" "$COLOR_YELLOW" "${to_install[@]}"

  if [[ ${#to_install[@]} -eq 0 ]]; then
    echo -e "\n${COLOR_GREEN}${BOLD}✓ ¡Todos los paquetes extras ya están instalados!${COLOR_RESET}"
    return 0
  fi

  show_install_start "extras" "${#to_install[@]}"

  # Instalar paquetes uno por uno para mayor visibilidad
  echo "Instalando paquetes extras..."
  local success_count=0
  local failed_packages=()
  local total_packages=${#to_install[@]}

  for ((i=0; i<total_packages; i++)); do
    pkg="${to_install[$i]}"
    show_package_progress $((i+1)) $total_packages "$pkg"

    # Verificar nuevamente si el paquete ya está instalado
    if [[ "$(is_package_installed "$pkg")" == "true" ]]; then
      show_package_result "already" "$pkg" ""
      ((success_count++))
      continue
    fi

    # Medir el tiempo de instalación
    start_time=$(date +%s)

    echo "Instalando paquete extra: $pkg" >> "$LOG_FILE"
    set +e  # Desactivar salida por error temporalmente para este comando
    if eval "$INSTALL_CMD" "$pkg" >> "$LOG_FILE" 2>&1; then
      end_time=$(date +%s)
      duration=$((end_time - start_time))
      show_package_result "success" "$pkg" "$duration"
      ((success_count++))
    else
      end_time=$(date +%s)
      duration=$((end_time - start_time))
      # Verificar si después de un intento fallido el paquete está instalado
      if [[ "$(is_package_installed "$pkg")" == "true" ]]; then
        show_package_result "partial" "$pkg" "$duration"
        ((success_count++))
      else
        show_package_result "error" "$pkg" "$duration"
        failed_packages+=("$pkg")
        echo "ERROR: Falló la instalación del paquete: $pkg" >> "$LOG_FILE"
      fi
    fi
    set -u  # Reactivar opciones pero sin incluir -e
  done

  # Mostrar resumen de la instalación
  show_title "RESUMEN DE INSTALACIÓN"
  if [[ ${#already_installed[@]} -gt 0 ]]; then
    echo -e "${COLOR_GREEN}✓ Paquetes ya instalados: ${#already_installed[@]}${COLOR_RESET}"
  fi
  echo -e "${COLOR_GREEN}✓ Paquetes instalados correctamente: $success_count/$total_packages${COLOR_RESET}"

  if [[ ${#failed_packages[@]} -gt 0 ]]; then
    echo -e "${COLOR_RED}✗ Paquetes con errores (${#failed_packages[@]}):${COLOR_RESET}"
    for p in "${failed_packages[@]}"; do
      echo -e "${COLOR_RED}  - $p${COLOR_RESET}"
    done
    echo -e "${COLOR_YELLOW}Ver $LOG_FILE para más detalles.${COLOR_RESET}"
  fi

  show_completion_message "Instalación de paquetes extras completada"
}

# --- Funciones de Acción --- #

install_base_packages() {
  show_action "Instalar paquetes base"

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
  show_title "PAQUETES BASE (${#PACKAGES_TO_INSTALL[@]} total)"

  show_packages_list "Paquetes ya instalados" "$COLOR_GREEN" "${already_installed[@]}"
  show_pending_packages "Paquetes a instalar" "$COLOR_YELLOW" "${to_install[@]}"

  if [[ ${#to_install[@]} -eq 0 ]]; then
    echo -e "\n${COLOR_GREEN}${BOLD}✓ ¡Todos los paquetes base ya están instalados!${COLOR_RESET}"
    return 0
  fi

  show_install_start "base" "${#to_install[@]}"

  if [[ -n "$UPDATE_CMD" ]]; then
    echo "Actualizando repositorios antes de instalar paquetes extras..."
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
    show_package_progress $((i+1)) $total_packages "$pkg"

    # Verificar nuevamente si el paquete ya está instalado
    if [[ "$(is_package_installed "$pkg")" == "true" ]]; then
      show_package_result "already" "$pkg" ""
      ((success_count++))
      continue
    fi

    # Medir el tiempo de instalación
    start_time=$(date +%s)

    echo "Instalando paquete base: $pkg" >> "$LOG_FILE"
    set +e  # Desactivar salida por error temporalmente para este comando
    if eval "$INSTALL_CMD" "$pkg" >> "$LOG_FILE" 2>&1; then
      end_time=$(date +%s)
      duration=$((end_time - start_time))
      show_package_result "success" "$pkg" "$duration"
      ((success_count++))
    else
      end_time=$(date +%s)
      duration=$((end_time - start_time))
      # Verificar si después de un intento fallido el paquete está instalado
      if [[ "$(is_package_installed "$pkg")" == "true" ]]; then
        show_package_result "partial" "$pkg" "$duration"
        ((success_count++))
      else
        show_package_result "error" "$pkg" "$duration"
        failed_packages+=("$pkg")
        echo "ERROR: Falló la instalación del paquete: $pkg" >> "$LOG_FILE"
      fi
    fi
    set -u  # Reactivar opciones pero sin incluir -e
  done

  # Mostrar resumen de la instalación
  show_title "RESUMEN DE INSTALACIÓN"
  if [[ ${#already_installed[@]} -gt 0 ]]; then
    echo -e "${COLOR_GREEN}✓ Paquetes ya instalados: ${#already_installed[@]}${COLOR_RESET}"
  fi
  echo -e "${COLOR_GREEN}✓ Paquetes instalados correctamente: $success_count/$total_packages${COLOR_RESET}"

  if [[ ${#failed_packages[@]} -gt 0 ]]; then
    echo -e "${COLOR_RED}✗ Paquetes con errores (${#failed_packages[@]}):${COLOR_RESET}"
    for p in "${failed_packages[@]}"; do
      echo -e "${COLOR_RED}  - $p${COLOR_RESET}"
    done
    echo -e "${COLOR_YELLOW}Ver $LOG_FILE para más detalles.${COLOR_RESET}"
  fi

  show_completion_message "Instalación de paquetes base completada"
}

update_system_packages() {
  show_action "Actualizar todos los paquetes del sistema"

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

  show_completion_message "Actualización completa del sistema completada"
}

# Función para mostrar un título con formato
show_title() {
  local title="$1"
  local width=60
  local border_char="="
  local border_line=$(printf "%${width}s" | tr " " "$border_char")

  echo
  echo -e "$border_line"
  echo -e "$border_char ${COLOR_CYAN}${BOLD}$title${COLOR_RESET} $border_char"
  echo -e "$border_line"
  echo
}

# Función para mostrar paquetes con formato
show_packages_list() {
  local title="$1"
  local color="$2"
  shift 2
  local packages=("$@")
  local count=${#packages[@]}

  # Si no hay paquetes, no mostrar nada
  if [[ $count -eq 0 ]]; then
    return
  fi

  # Encontrar la longitud máxima para alinear
  local max_length=0
  for pkg in "${packages[@]}"; do
    if [[ ${#pkg} -gt $max_length ]]; then
      max_length=${#pkg}
    fi
  done

  # Usar siempre 2 columnas como solicitado
  local columns=2

  # Añadir padding amplio para mayor separación entre columnas (incluyendo "✓ ")
  max_length=$((max_length + 2 + 8))  # +2 para "✓ " y +8 para espaciado amplio

  # Mostrar título y contador
  echo -e "${color}${BOLD}$title ($count)${COLOR_RESET}"
  echo -e "${color}─────────────────────${COLOR_RESET}"

  # Calcular elementos por columna
  local items_per_column=$(( (count + columns - 1) / columns ))

  # Mostrar en filas
  for ((i = 0; i < items_per_column; i++)); do
    for ((j = 0; j < columns; j++)); do
      local index=$((i + j * items_per_column))
      if [[ $index -lt $count ]]; then
        printf "${color}%-${max_length}s${COLOR_RESET}" "✓ ${packages[$index]}"
      fi
    done
    echo
  done
  echo
}

# Función para mostrar paquetes pendientes con formato
show_pending_packages() {
  local title="$1"
  local color="$2"
  shift 2
  local packages=("$@")
  local count=${#packages[@]}

  # Si no hay paquetes, no mostrar nada
  if [[ $count -eq 0 ]]; then
    return
  fi

  # Encontrar la longitud máxima para alinear
  local max_length=0
  for pkg in "${packages[@]}"; do
    if [[ ${#pkg} -gt $max_length ]]; then
      max_length=${#pkg}
    fi
  done

  # Usar siempre 2 columnas como solicitado
  local columns=2

  # Añadir padding amplio para mayor separación entre columnas (incluyendo "→ ")
  max_length=$((max_length + 2 + 8))  # +2 para "→ " y +8 para espaciado amplio

  # Mostrar título y contador
  echo -e "${color}${BOLD}$title ($count)${COLOR_RESET}"
  echo -e "${color}─────────────────────${COLOR_RESET}"

  # Calcular elementos por columna
  local items_per_column=$(( (count + columns - 1) / columns ))

  # Mostrar en filas
  for ((i = 0; i < items_per_column; i++)); do
    for ((j = 0; j < columns; j++)); do
      local index=$((i + j * items_per_column))
      if [[ $index -lt $count ]]; then
        printf "${color}%-${max_length}s${COLOR_RESET}" "→ ${packages[$index]}"
      fi
    done
    echo
  done
  echo
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
      show_verification_message "Verificando instalación de paquetes Snap"

      # Instalar paquetes snap si no se ha desactivado y es un sistema compatible
      if [[ "$NO_SNAP" == false ]]; then
        echo "Verificando instalación de paquetes Snap..." >> "$LOG_FILE"
        echo "DEBUG: NO_SNAP=$NO_SNAP, OS=$OS, lsb-release=$(test -f /etc/lsb-release && echo 'existe' || echo 'no existe'), snap.pkg=$(test -f ${CONFIG_DIR}/snap.pkg && echo 'existe' || echo 'no existe')" >> "$LOG_FILE"
        # Verifica si el sistema es Ubuntu genuino (no Mint ni otro derivado incompatible)
        # y si existe snap.pkg antes de intentar instalar
        if [[ "$OS" == "debian" && -f /etc/lsb-release && -f "${CONFIG_DIR}/snap.pkg" ]]; then
          # Verificar si es un derivado que no usa Snap por defecto
          if ! grep -qi "mint\|elementary" /etc/os-release 2>/dev/null && \
             ! grep -qi "mint\|elementary" /etc/lsb-release 2>/dev/null; then
            echo "Sistema compatible con Snap detectado. Procediendo con la instalación de paquetes Snap." >> "$LOG_FILE"
            show_verification_message "Sistema compatible con Snap detectado, procediendo con la instalación"
            install_snap_packages
          else
            echo "Sistema derivado de Ubuntu detectado. Omitiendo instalación de Snap." >> "$LOG_FILE"
            show_verification_message "Sistema derivado de Ubuntu detectado, omitiendo instalación de Snap"
          fi
        else
          if [[ "$OS" != "debian" ]]; then
            echo "No es un sistema Debian/Ubuntu. Omitiendo instalación de Snap." >> "$LOG_FILE"
            show_verification_message "No es un sistema Debian/Ubuntu, omitiendo instalación de Snap"
          elif [[ ! -f /etc/lsb-release ]]; then
            echo "No es un sistema basado en Ubuntu. Omitiendo instalación de Snap." >> "$LOG_FILE"
            show_verification_message "No es un sistema basado en Ubuntu, omitiendo instalación de Snap"
          elif [[ ! -f "${CONFIG_DIR}/snap.pkg" ]]; then
            echo "No se encontró el archivo ${CONFIG_DIR}/snap.pkg. Omitiendo instalación de Snap." >> "$LOG_FILE"
            show_verification_message "No se encontró el archivo ${CONFIG_DIR}/snap.pkg, omitiendo instalación"
          fi
        fi
      else
        echo "Instalación de Snap desactivada con --nosnap." >> "$LOG_FILE"
        show_verification_message "Instalación de Snap desactivada con --nosnap"
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
