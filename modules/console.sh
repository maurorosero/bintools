#!/bin/bash
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2025, MAURO ROSERO PÉREZ
# License: GPLV3
# Author: Mauro Rosero P. (mauro.rosero@gmail.com)
# Created: 2025-05-02 10:51:06
# Version: 0.1.0
#
# console.sh - Console Developers Library
# -----------------------------------------------------------------------------
#
#
# Library: console.lib
# Description: Console Developers Library
# Modified: 2024/12/04 12:27:00
# Derechos de Autor (C) [2024] [Mauro Rosero P. <mauro@roser.one>]
#
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

# Global Default Variables
CWIDTH=70
CROWS=8
CX=4
CY=2

# Test console library
function consolelib_test() {
  echo "Console Library loaded!"
}

# Dialog Yes/No Question
function dialog_yesno() {

  local label="$1"
  local rows="${2:-$CROWS}"
  local width="${3:-$CWIDTH}"

  dialog --keep-window --begin  ${CX} ${CY} --colors --no-shadow --backtitle "${title}" --title "${apps_title}" --yesno "\n${label}" ${rows} ${width}
  result=$?

  return ${result}

}

# Dialog Input Box
function dialog_input_box() {

  local label="$1"
  local helper="$2"
  local v_default="$3"
  local rows="${4:-$CROWS}"
  local width="${5:-$CWIDTH}"

  exec 3>&1;
  value=$(dialog --keep-window --begin  ${CX} ${CY} --colors --no-shadow --backtitle "${title}" --title "${apps_title}" --inputbox "\n${label}\n${helper}" ${rows} ${width} "${v_default}" 2>&1 1>&3);
  codex=$?;
  exec 3>&-;

  return ${codex}

}

# Dialog Password Box
function dialog_input_pass(){

  local label="$1"
  local helper="$2"
  local v_default="$3"
  local rows="${4:-$CROWS}"
  local width="${5:-$CWIDTH}"

  exec 3>&1;
  value=$(dialog --keep-window --begin  ${CX} ${CY} --colors --no-shadow --backtitle "${title}" --title "${apps_title}" --passwordbox "\n${label}\n${helper}" ${rows} ${width} "${v_default}" 2>&1 1>&3);
  codex=$?;
  exec 3>&-;

  return ${codex}

}

# Dialog Radio List
function dialog_input_radio() {

  local label="$1"
  local helper="$2"
  local options="$3"
  local rows="${4:-$CROWS}"
  local forced_rows="${5:-${rows}}"
  local width="${6:-$CWIDTH}"

  # Calcular el número de elementos
  local elements=$(echo "$options" | awk '{print NF/3 + 1}')
  ((rows += elements))

  exec 3>&1;
  value=$(dialog --keep-window --begin ${CX} ${CY} --colors --no-shadow --backtitle "${title}" --title "${apps_title}" --radiolist "\n${label}\n${helper}" ${forced_rows} ${width} ${elements} ${options} 2>&1 1>&3)
  codex=$?
  exec 3>&-;

  return ${codex}

}

# Dialog Menu Select
function dialog_input_menu() {

  local label="$1"
  local helper="$2"
  local options="$3"
  local rows="${4:-$CROWS}"
  local width="${5:-$CWIDTH}"

  # Calcular el número de elementos
  local elements=$(echo "$options" | awk '{print NF/2 + 1}')
  ((rows += elements))

  exec 3>&1;
  value=$(dialog --keep-window --begin ${CX} ${CY} --colors --no-shadow --backtitle "${title}" --title "${apps_title}" --menu "\n${label}\n${helper}" ${rows} ${width} ${elements} ${options} 2>&1 1>&3)
  codex=$?
  exec 3>&-;

  return ${codex}

}

# Dialog Main Menu
function menu_actions() {
  local head_menu="$1"
  local keys=$(echo -e "$2")
  local rows=$3
  options=()


  while IFS= read -r line
  do
    name=$(echo "$line" | cut -d':' -f2)
    index=$(echo "$line" | cut -d':' -f1)
    options+=("${index}" "${name}")
    ((rows++))
  done <<< "$keys"

  choice=$(dialog --clear \
                  --erase-on-exit \
                  --cancel-label "${head_exit}" \
                  --backtitle "${title}" \
                  --title "${apps_title}" \
                  --menu "\n${head_menu}" \
                  ${rows} 56 2 \
                  "${options[@]}" \
                  2>&1 >/dev/tty)
  if [ $? -ne 0 ]
  then
    choice="${head_key_end}"
  fi
  echo "${choice}"
}

# Dialog Select File Box Input
function dialog_input_filepath() {

  local valid_file="0"
  local file_path=$1

  while [ "$valid_file" == "0" ]
  do
    exec 3>&1;
    result=$(dialog --begin 2 2 --title "${apps_title} - $2" --backtitle "${title}" --fselect ${file_path} 7 0 2>&1 1>&3);
    exitcode=$?;
    exec 3>&-;
    if [ "$exitcode" == "0" ]
    then
      if [ -f "$result" ]
      then
        file_path=${result}
        valid_file="1"
      fi
    else
      valid_file="2"
    fi
  done

}

# Dialog Error Box
function dialog_error_box() {

  local msgtype="$1"
  local message="$2"

  # Redirigir la salida de error al descriptor de archivo 3
  exec 3>&1;

  # Mostrar el cuadro de diálogo
  dialog --backtitle "${title}" --title "${msgtype} - ${apps_title}" --msgbox "\n${message}" 8 ${CWIDTH}
  #dialog --and-widget --msgbox "\n${message}"

  exec 3>&-;

}

# Dialog Validation for input
function dialog_validate_input() {

  local value="$2"
  local label="$3"
  local valid_data="$4"

  local email_regex='^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
  local gpg_duration_regex="^[0-9]+([dmy])?$"
  local domain_regex="^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9]+[a-zA-Z0-9-]*[a-zA-Z0-9]+))(\.([a-zA-Z]{2,})){1,}$"

  # Verificar si se proporcionó un argumento
  if [ $# -ne 0 ]; then
    # Convertir el argumento en un array
    arr=($1)

    # Iterar sobre el array y llamar a process_element para cada elemento
    for vcode in "${arr[@]}"
    do
      case ${vcode} in
        000)
          return 0
          ;;
        001)
          if [ -z "${value}"  ]
          then
            dialog_error_box "${head_error}" "${label} ${vldt_001}"
            return 1
          fi
          ;;
        010)
          if [[ ! "${value}" =~ ${email_regex} ]]
          then
            dialog_error_box "${head_error}" "${vldt_010}"
            return 1
          fi
          ;;
        011)
          if [[ ! "${value}" =~ ${gpg_duration_regex} ]]
          then
            dialog_error_box "${head_error}" "${vldt_011}"
            return 1
          fi
          ;;
        012)
          if [[ ! "${value}" =~ ${domain_regex} ]]
          then
            dialog_error_box "${head_error}" "${vldt_012}"
            return 1
          fi
          ;;
        013)
          local -a elements=(${valid_data})
          for item in "${elements[@]}"
          do
            if [[ "$item" == "$value" ]]
            then
              return 0
            fi
          done
          dialog_error_box "${head_error}" "${vldt_013} ${valid_data}"
          return 1
          ;;
        014)
          local -a rangos=($valid_data)
          if [ $((value)) -ge ${rangos[0]} ] && [ $((value)) -le ${rangos[0]} ]
          then
            return 0
          fi
          dialog_error_box "${head_error}" "${vldt_014} ${rangos[0]} y ${rangos[1]}"
          return 1
          ;;
      esac
    done
  fi

  return 0

}

# Dialog data input form
function dialog_form() {

  # Ciclo de captura de datos
  clear
  control=0
  while [ ${control} -lt ${c_end} ]
  do
    case ${c_mod[control]} in
      1)
        dialog_input_box "[${control}] ${c_lbl[control]}" "${c_hlp[control]}" "${c_def[control]}"
        if [ ${codex} -eq 0 ]
        then
          dialog_validate_input "${c_val[control]}" "${value}" "${c_lbl[control]}" "${c_dat[control]}"
          if [ $? -eq 0 ]
          then
            response[control]="${value}"
            ((control++))
          fi
        else
          case ${codex} in
            1)
              if [ ${control} -gt 0 ]
              then
                ((control--))
              else
                control=${c_end}
                return 1
              fi
              ;;
            255)
              return 1
              control=${c_end}
              ;;
          esac
        fi
        ;;
      2)
        dialog_input_pass "[${control}] ${c_lbl[control]}" "${c_hlp[control]}"
        if [ ${codex} -eq 0 ]
        then
          response[control]="${value}"
          dialog_input_pass "[${control}] ${c_lbl[control]} ${head_confirm}" "${c_hlp[control]}"
          if [ ${codex} -eq 0 ]
          then
            if [ "${response[control]}" == "${value}" ] && [ ! -z "${response[control]}" ]
            then
              ((control++))
              sleep 1
            else
              dialog_error_box "${head_error}" "${vldt_002}"
            fi
          else
            if [ ${codex} -eq 255 ]
            then
              control=${c_end}
              return 1
            fi
          fi
        else
          case ${codex} in
            1)
              if [ ${control} -gt 0 ]
              then
                ((control--))
              else
                control=${c_end}
                return 1
              fi
              ;;
            255)
              return 1
              control=${c_end}
              ;;
          esac
        fi
        ;;
      3)
        dialog_input_radio "[${control}] ${c_lbl[control]}" "${c_hlp[control]}" "${c_opt[control]}"
        if [ ${codex} -eq 0 ]
        then
          response[control]="${value}"
          ((control++))
        else
          case ${codex} in
            1)
              if [ ${control} -gt 0 ]
              then
                ((control--))
              else
                control=${c_end}
                return 1
              fi
              ;;
            255)
              return 1
              control=${c_end}
              ;;
          esac
        fi
        ;;
      4)
        dialog_input_menu "[${control}] ${c_lbl[control]}" "${c_hlp[control]}" "${c_opt[control]}"
        if [ ${codex} -eq 0 ]
        then
          response[control]="${value}"
          ((control++))
        else
          case ${codex} in
            1)
              if [ ${control} -gt 0 ]
              then
                ((control--))
              else
                control=${c_end}
                return 1
              fi
              ;;
            255)
              return 1
              control=${c_end}
              ;;
          esac
        fi
        ;;
    esac
  done

  return 0

}
