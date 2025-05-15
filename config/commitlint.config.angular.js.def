// -----------------------------------------------------------------------------
// Copyright (c) 2025, MAURO ROSERO PÉREZ
// License: GPLV3
// Author: Mauro Rosero P. (mauro.rosero@gmail.com)
// Created: 2025-05-12 21:56:33
// Version: 0.1.0
//
// commitlint.config.js - Angular commit format configuration (Adaptado a [TAG] (#Issue) Descripcion)
// -----------------------------------------------------------------------------

const requireIssueFromMeta = process.env.REQUIRE_ISSUE_FROM_META === 'true';

module.exports = {
  // extends: ['@commitlint/config-angular'], // Eliminado para control total con el parserPreset personalizado
  parserPreset: {
    parserOpts: {
      // Captura: [TAG] (#IssueNumber opcional) Descripción
      // 1: TAG (type)
      // 2: #IssueNumber (scope) - opcional
      // 3: Descripción (subject)
      headerPattern: /^\[([A-Z]+)\](?: \((#\d+)\))? (.*)$/,
      headerCorrespondence: ['type', 'scope', 'subject'],
    },
  },
  rules: {
    // --- Reglas para TYPE (el TAG) ---
    'type-enum': [
      2,
      'always',
      [ // Valores en MAYÚSCULAS para coincidir con el TAG de nuestro parserPreset
        'FEAT',
        'FIX',
        'DOCS',
        'STYLE',
        'REFACTOR',
        'PERF',
        'TEST',
        'BUILD',
        'CI',
        'CHORE',
        'REVERT'
      ]
    ],
    'type-case': [2, 'always', 'upper-case'], // Cambiado a upper-case
    'type-empty': [2, 'never'],

    // --- Reglas para SCOPE (el #IssueNumber) ---
    'scope-empty': [requireIssueFromMeta ? 2 : 0, 'never'], 
    'scope-case': [2, 'always', 'lower-case'], // Se mantiene, es compatible
    // No se añade 'scope-pattern' ya que el headerPattern del parserPreset lo maneja.

    // --- Reglas para SUBJECT (la descripción) ---
    'subject-empty': [2, 'never'],
    'subject-case': [
      2,
      'always',
      ['sentence-case', 'lower-case'] // Se mantiene como estaba en la config original de angular
    ],
    
    // --- Reglas generales del HEADER ---
    'header-max-length': [2, 'always', 100]
    
    // Otras reglas de config-angular que se deseen replicar deberían añadirse explícitamente aquí.
  }
}; 