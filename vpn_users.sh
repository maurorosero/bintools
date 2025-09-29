#!/bin/bash
#Script     	: vpn_users.sh
#Apps			: MRDEVS TOOLS
#Description	: Administra Usuarios VPN en PRITUNL
#Author			: Mauro Rosero Pérez
#Company Email	: mauro@rosero.one
#Personal Email	: mauro.rosero@gmail.com
#Created		: 2024/12/01 15:27:00
#Modified		: 2025/03/19 11:57:08
#Version		: 1.2.0
#Use Notes		:
#	- pritunl-orgs.dat: Contiene organizaciones para desarrolladores del VPN
#	- pritunl_users.yaml: Contiene el acceso de desarroladores del VPN
#==============================================================================
# Derechos de Autor [2025] [Mauro Rosero P. <mauro@rosero.one>]
#==============================================================================
# Este programa es software libre: usted puede redistribuirlo y/o modificarlo
# bajo los términos de la Licencia Pública Affero General de GNU tal como
# lo publica la Free Software Foundation, ya sea la versión 3 de la licencia,
# o (a su elección) cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil,
# pero SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de
# COMERCIABILIDAD o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulte la
# Licencia Pública Affero General de GNU para obtener más detalles.
#
# Debería haber recibido una copia de la Licencia Pública Affero General
# junto con este programa. Si no la recibió, consulte <https://www.gnu.org/licenses/>.

# Configuración inicial
# Usar DEVELOPER_DIR de base.lib
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_BASE="bin"
BIN_LIBS="lib"
BIN_MESG="msg"
BIN_CFGS="config"
BIN_ANSIBLE="ansible"

# Leer DEVSPATH desde el archivo de configuración o usar "devs" por defecto
if [ -f "$SCRIPT_DIR/$BIN_CFGS/devspath.dat" ]; then
  DEVSPATH=$(cat "$SCRIPT_DIR/$BIN_CFGS/devspath.dat")
else
  DEVSPATH="devs"
fi

BIN_HOME="$HOME/$DEVSPATH"
BIN_PATH=$BIN_HOME/$BIN_BASE
VERSION=$(cat "$BIN_HOME/$BIN_BASE/$BIN_CFGS/version")

# CHECK SHELL LANGUAGE
BIN_LANG=${LANG:0:2}

# LOAD BASE BASH LIBRARY
source $BIN_HOME/$BIN_BASE/$BIN_LIBS/base.lib
#baselib_test

# LOAD CONSOLE BASH LIBRARY
source $BIN_HOME/$BIN_BASE/$BIN_LIBS/console.lib
#consolelib_test


# Load head messages
load_messages $BIN_HOME/$BIN_BASE $BIN_MESG $BIN_LANG "head"

# Load head messages
load_messages $BIN_HOME/$BIN_BASE $BIN_MESG $BIN_LANG "pritunl"

# Function to display help message
function help() {
  echo "$plmsg_003_1 $0 $plmsg_003_2"
  echo "$plmsg_004"
  echo "$plmsg_005"
  echo "$plmsg_006"
  echo "$plmsg_007"
}

# Function to capture data to add, enable, disable, remove pritunl vpn users
function vpn_pritunl_users_form() {

  local action=$1

  declare -a response c_lbl, c_hlp, c_mod, c_opt, c_val, c_dat, c_def

  declare -a ARRAY
  c_val[0]=013
  read_file_to_array "${BIN_HOME}/${BIN_BASE}/${BIN_CFGS}/pritunl-orgs.dat"
  if [ $? -ne 0 ]; then
    ARRAY[0]=""
    c_val[0]=0
  fi

  # Input: Organization Pritunl VPN
  c_lbl[0]="${pllbl_000}"
  c_hlp[0]="${plhlp_000}"
  c_mod[0]=1
  c_opt[0]=0
  c_def[0]="${ARRAY[0]}"
  c_dat[0]="${ARRAY[@]}"
  # Input: User Pritunl VPN
  c_lbl[1]="${pllbl_001}"
  c_hlp[1]="${plhlp_001}"
  c_mod[1]=1
  c_opt[1]=0
  c_def[1]=""
  c_val[1]=0
  c_dat[1]=""
  # Input count
  c_end=2
  if [ "${action}" != "remove" ]; then
    # Input count
    c_end=3
    # Input: User Email Pritunl VPN
    i=2
    c_lbl[$i]="${pllbl_002}"
    c_hlp[$i]="${plhlp_002}"
    c_mod[$i]=1
    c_opt[$i]=0
    c_def[$i]=""
    c_val[$i]=010
    c_dat[$i]=""
  fi

  dialog_form
  if [ $? -eq 0 ]
  then
    display_devstools_header "${plmsg_000}"
    if [ "${action}" != "remove" ]
    then
      ansible-playbook -i ${BIN_HOME}/inventory/base.ini ${BIN_HOME}/${BIN_BASE}/${BIN_ANSIBLE}/pritunl_users.yaml \
        -e "input_pritunl_action=${action} input_pritunl_org=${response[0]} input_pritunl_user=${response[1]} input_pritunl_email=${response[2]}"
    else
      ansible-playbook -i $BIN_HOME/inventory/base.ini ${BIN_HOME}/${BIN_BASE}/${BIN_ANSIBLE}/pritunl_users.yaml \
        -e "input_pritunl_action=${action} input_pritunl_org=${response[0]} input_pritunl_user=${response[1]}"
    fi
    read -p "${head_pause}"
    return 0
  fi
}

########### MAIN PROGRAM ###########

# Check if dialog is not installed, exited!
if ! command -v dialog >/dev/null 2>&1
then
  display_devstools_header "${plmsg_000}"
  echo "${head_001}"
  exit 200
fi

# Check if ansible-playbook is not installed, exited!
if ! command -v ansible-playbook >/dev/null 2>&1
then
  display_devstools_header "${plmsg_000}"
  echo "${plmsg_002}"
  exit 210
fi

# Check for arguments option
help=false
version=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --help)
        help=true
        shift
        ;;
    --version)
        version=true
        shift
        ;;
  esac
done

# Check to show help
if $help; then
  help
  exit 0
fi

# Check to show command version
if $version; then
  echo "${head_version} ${VERSION}"
  exit 0
fi

# Set program title
APPS_NAME="${head_000} ${head_002}"
title="${APPS_NAME} ${plmsg_001}"
apps_title="${plmsg_101}"

# Check if os is valid!
get_osname
if [ "${os_name}" == "${head_unknow}" ]
then
  dialog_error_box "${head_error}" "${head_os_error}"
  exit 3
fi

# Main Menu (users actions)
menu_option=""
menu_action=""
while [ "${menu_option}" != "${head_key_end}" ]
do
  menu_option=$(menu_actions "${plmsg_100}" "${plmnu_000}" 8)
  case "${menu_option}" in
    "${plmnu_k01}")
        menu_action="add"
        vpn_pritunl_users_form "${menu_action}"
        ;;
    "${plmnu_k02}")
       menu_action="enable"
       #vpn_pritunl_users_form "${menu_action}"
       ;;
    "${plmnu_k03}")
       menu_action="disable"
       #vpn_pritunl_users_form "${menu_action}"
       ;;
    "${plmnu_k04}")
       menu_action="remove"
       vpn_pritunl_users_form "${menu_action}"
       ;;
    esac
done

# Clear console and exit
clear
exit 0
