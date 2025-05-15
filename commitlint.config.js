// -----------------------------------------------------------------------------
// Copyright (c) 2025, MAURO ROSERO PÉREZ
// License: GPLV3
// Author: Mauro Rosero P. (mauro.rosero@gmail.com)
// Created: 2025-05-12 21:56:33
// Version: 0.1.0
//
// commitlint.config.js - Configuración de commitlint para formato simple
// -----------------------------------------------------------------------------
//
const VERSION = "0.1.0"; // Version para el script de versionado
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'FIX',    // Correcciones y bugs
        'FEAT',   // Nuevas características
        'DOCS',   // Documentación
        'CHORE',  // Mantenimiento y tareas generales
        'CI'      // Para cambios en configuración/scripts de CI/CD
      ]
    ],
    'type-case': [2, 'always', 'upper-case'],
    'type-empty': [2, 'never'],
    'subject-empty': [2, 'never'],
    'subject-case': [0],
    'header-max-length': [2, 'always', 100]
  }
}; 