#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# GPG Manager - Script que proporciona una interfaz CLI interactiva para gestionar claves GPG.
#
# Copyright (C) 2025 MAURO ROSERO PÉREZ
# License: GPLv3
#
# File: gpg-manager.sh
# Version: 0.1.0
# Author: Mauro Rosero P. <mauro.rosero@gmail.com>
# Assistant: Cursor AI (https://cursor.com)
# Created: 2025-05-19 20:53:17
#
# This file is managed by template_manager.py.
# Any changes to this header will be overwritten on the next fix.
#
# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

main() {
  # Check dependencies
  check_dependencies
  local deps_status=$?
  
  if [ $deps_status -ne 0 ]; then
    exit $deps_status
  fi

  # Ensure translations are loaded
  ensure_translations_loaded
  
  # Debug translations
  debug_translations
  
  # No need to display welcome message here, it's already handled in the main menu
  # main_menu will display the header
  main_menu
}

# Run main function
main
