#!/bin/bash
# -*- coding: utf-8 -*-
# Fix HDMI Audio - Script para corregir el formato de audio HDMI con PipeWire.
# ----------------------------------------------------------------------------- 
# Script Name: fix_hdmi_audio.sh
# Version: 0.1.0
# Author: Mauro Rosero P. <mauro.rosero@gmail.com>
# Created: 2025-09-13
# Updated: 2025-09-13

# -----------------------------------------------------------------------------
# Copyright (C) 2025 Mauro Rosero Pérez
# -----------------------------------------------------------------------------
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# This file is managed by template_manager.py.
# Any changes to this header will be overwritten on the next fix.

# HEADER_END_TAG - DO NOT REMOVE OR MODIFY THIS LINE

# Variables
RULE_PATH="$HOME/.config/wireplumber/main.lua.d"
RULE_FILE="$RULE_PATH/99-force-s16le.lua"
EXPECTED_SAMPLE_SPEC="s16le 2ch 48000Hz"
SINK_NAME="alsa_output.pci-0000_00_1f.3.hdmi-stereo"

# Verifica formato actual
echo "🔍 Verificando formato del sink HDMI..."
CURRENT_SPEC=$(pactl list sinks | grep -A5 "$SINK_NAME" | grep 'Especificación de muestra' | awk -F': ' '{print $2}')

if [[ "$CURRENT_SPEC" == "$EXPECTED_SAMPLE_SPEC" ]]; then
  echo "✅ HDMI ya está configurado correctamente: $CURRENT_SPEC"
else
  echo "⚠️  Formato incorrecto: $CURRENT_SPEC"
  echo "🛠️  Aplicando corrección..."

  # Crea el directorio si no existe
  mkdir -p "$RULE_PATH"

  # Escribe la regla forzada
  cat > "$RULE_FILE" << 'EOF'
rule = {
  matches = {
    {
      { "node.name", "matches", "alsa_output.pci-0000_00_1f.3.hdmi-stereo" },
    },
  },
  apply_properties = {
    ["audio.format"] = "S16LE",
    ["audio.rate"] = 48000,
    ["audio.channels"] = 2,
  },
}

table.insert(alsa_monitor.rules, rule)
EOF

  echo "✅ Regla escrita en $RULE_FILE"
  echo "🔄 Reiniciando servicios PipeWire..."

  systemctl --user restart wireplumber pipewire pipewire-pulse

  sleep 2
  NEW_SPEC=$(pactl list sinks | grep -A5 "$SINK_NAME" | grep 'Especificación de muestra' | awk -F': ' '{print $2}')
  if [[ "$NEW_SPEC" == "$EXPECTED_SAMPLE_SPEC" ]]; then
    echo "✅ HDMI corregido exitosamente: $NEW_SPEC"
  else
    echo "❌ La corrección no se aplicó. Revisa logs con: journalctl --user -u wireplumber -f"
  fi
fi
