/**
 * Configuración de commitlint que implementa un formato de commits personalizado
 * basado en el convencional pero adaptado al formato [TAG] (#Issue) Descripción.
 * Define reglas para validar el formato de los mensajes de commit, incluyendo
 * validación de tipos, scope (issue numbers) y descripción.
 *
 * Copyright (C) 2025 MAURO ROSERO PÉREZ
 * License: GPLv3
 *
 * @file commitlint.config.js
 * @version 0.1.0
 * @author Mauro Rosero P. <mauro.rosero@gmail.com>
 * @created 2025-05-19 20:56:28
 *
 * This file is managed by template_manager.py.
 * Any changes to this header will be overwritten on the next fix.
 *
 * HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE
 */


const requireIssueFromMeta = process.env.REQUIRE_ISSUE_FROM_META === 'true';

module.exports = {
  // extends: ['@commitlint/config-conventional'], // Eliminado para control total con el parserPreset personalizado
  parserPreset: {
    parserOpts: {
      // Consistente con los otros archivos: [TAG] (#IssueNumber opcional) Descripción
      headerPattern: /^\[([A-Z]+)\](?: \((#\d+)\))? (.*)$/,
      headerCorrespondence: ['type', 'scope', 'subject'],
    },
  },
  rules: {
    // --- Reglas para TYPE (el TAG) ---
    // 'type-enum': [0], // Sin restricción de enum de TAGs por defecto para esta config "conventional"
    'type-case': [2, 'always', 'upper-case'], // Asegurar que el TAG sea mayúsculas
    'type-empty': [2, 'never'], // El TAG es obligatorio

    // --- Reglas para SCOPE (el #IssueNumber) ---
    'scope-empty': [requireIssueFromMeta ? 2 : 0, 'never'], 
    'scope-case': [2, 'always', 'lower-case'], // Consistente con otros archivos
    // No se añade 'scope-pattern' ya que el headerPattern del parserPreset lo maneja.

    // --- Reglas para SUBJECT (la descripción) ---
    'subject-empty': [2, 'never'],
    'subject-case': [
      2,
      'always',
      ['sentence-case', 'lower-case'] // Se mantiene como estaba
    ],
    
    // --- Reglas generales del HEADER ---
    'header-max-length': [2, 'always', 100]
    
    // Otras reglas de config-conventional que se deseen replicar deberían añadirse explícitamente aquí.
  }
}; 