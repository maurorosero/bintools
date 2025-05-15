// -----------------------------------------------------------------------------
// Copyright (c) 2025, MAURO ROSERO PÉREZ
// License: GPLV3
// Author: Mauro Rosero P. (mauro.rosero@gmail.com)
// Created: 2025-05-12 21:56:33
// Version: 0.1.0
//
// commitlint.config.js - Minimal commit format configuration
// -----------------------------------------------------------------------------

module.exports = {
  extends: ['@commitlint/config-conventional'],
  parserPreset: {
    parserOpts: {
      headerPattern: /^(.*?)(?:\s\(#(\d+)\))?$/,
      headerCorrespondence: ['subject', 'scope']
    }
  },
  rules: {
    'type-enum': [0], // No restricción en tipos
    'type-case': [0], // No restricción en mayúsculas/minúsculas
    'type-empty': [2, 'always'], // Forzar que el tipo (si el parser lo identifica) esté vacío
    'scope-empty': [0], // Permite commits sin scope (issue)
    'scope-case': [0], // No restricción en mayúsculas/minúsculas del scope (issue)
    'subject-empty': [2, 'never'], // El subject (mensaje principal) es obligatorio
    'subject-case': [0], // No restricción en mayúsculas/minúsculas del subject
    'header-max-length': [2, 'always', 100], // Solo limita la longitud total
    'scope-enum': [0], // No restricción en valores de scope (issue)
    'scope-min-length': [0], // No restricción en longitud mínima del scope (issue)
    'scope-max-length': [0], // No restricción en longitud máxima del scope (issue)
    'subject-min-length': [0], // No restricción en longitud mínima del subject
    'subject-max-length': [0], // No restricción en longitud máxima del subject
    'subject-full-stop': [0], // No restricción en punto final
    'subject-exclamation-mark': [0], // No restricción en signos de exclamación
    'body-leading-blank': [0], // No restricción en línea en blanco inicial
    'body-max-line-length': [0], // No restricción en longitud de línea
    'footer-leading-blank': [0], // No restricción en línea en blanco inicial
    'footer-max-line-length': [0], // No restricción en longitud de línea
    'references-empty': [0] // No restricción en referencias vacías
  }
}; 