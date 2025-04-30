// -----------------------------------------------------------------------------
// Copyright (c) 2025, MAURO ROSERO PÉREZ
// License: GPLV3
// Author: Mauro Rosero P. (mauro.rosero@gmail.com)
// Created: 2025-04-30 05:52:19
// Version: 0.1.0
//
// context.js - Description placeholder
// -----------------------------------------------------------------------------
//
const fs = require("fs");
const path = require("path");
const context_file = 'CURSOR.md';

const possiblePaths = [
  path.resolve(__dirname, '..', context_file),
  path.resolve(__dirname, '../config', context_file),
  path.resolve(__dirname, '../.github', context_file),
  path.resolve(__dirname, '../.vscode', context_file)
];

function findInstructionFile() {
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  return null;
}

module.exports = async ({ file, selection }) => {
  const instructionPath = findInstructionFile();
  let instructions = "";

  if (instructionPath) {
    try {
      instructions = fs.readFileSync(instructionPath, "utf8");
      console.log(`[Cursor Context] Instrucciones cargadas desde: ${instructionPath}`);
    } catch (e) {
      console.warn(`[Cursor Context] Error al leer ${instructionPath}:`, e.message);
    }
  } else {
    console.warn("[Cursor Context] No se encontró 'copilot-instruction.md' en rutas conocidas.");
  }

  return {
    instructions,
    temperature: 0.4
  };
};
