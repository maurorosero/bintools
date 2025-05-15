// -----------------------------------------------------------------------------
// Copyright (c) 2025, MAURO ROSERO PÉREZ
// License: GPLV3
// Author: Mauro Rosero P. (mauro.rosero@gmail.com)
// Created: 2025-05-12 21:56:33
// Version: 0.1.0
//
// commitlint.config.js - Description placeholder
// -----------------------------------------------------------------------------
//
const VERSION = "0.1.0"; // Version para el script de versionado
module.exports = {
  extends: ['@commitlint/config-conventional'], // Extend default rules
  parserPreset: { // Override parser to allow our TAG format
    parserOpts: {
        // Regex to capture:
        // 1. The TAG (e.g., [FIX], [FEAT])
        // 2. Optional scope in parentheses (#IssueNumber)
        // 3. The description
        headerPattern: /^\[([A-Z]+)\](?:\s\(#(\d+)\))?\s(.*)$/,
        headerCorrespondence: ['type', 'scope', 'subject'] // Map matches to conventional names (type becomes our TAG)
    }
  },
  rules: {
    // Override default rules slightly if needed, for now defaults are mostly ok
    'type-enum': [0], // Disable the default check for specific types (feat, fix, etc.) as we use TAGs
    'type-case': [0], // Allow uppercase TAGs (effectively disabled as type-enum is disabled for specific values)
    'type-empty': [2, 'never'], // TAG must not be empty
    'scope-case': [0], // Disable scope case check (for #IssueNumber)
    'subject-empty': [2, 'never'], // Description must not be empty
    'subject-case': [
      2, // Nivel de error (0=disable, 1=warning, 2=error)
      'always', // Aplicar siempre
      ['sentence-case', 'lower-case'] // Permitir sentence-case Y lower-case
    ],
    'header-max-length': [2, 'always', 100] // Keep subject line concise (increased from 72)
  }
}; 