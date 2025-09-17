#!/bin/bash

# Script para obtener el token de GitHub personal desde Bitwarden y guardarlo en git-tokens.py
# Reemplaza "MROSERO" por el usuario actual en mayúsculas

# Obtener el usuario actual en mayúsculas
CURRENT_USER=$(whoami | tr '[:lower:]' '[:upper:]')

echo "🔍 Obteniendo token de GitHub personal desde Bitwarden..."
echo "👤 Usuario: $CURRENT_USER"

# Obtener el token desde Bitwarden y guardarlo en git-tokens.py
bw get item "GITHUB" | grep -o "\"${CURRENT_USER} FULL TOKEN\",\"value\":\"[^\"]*\"" | sed "s/.*\"value\":\"\([^\"]*\)\".*/\1/" | ./git-tokens.py set github-personal --token -

if [ $? -eq 0 ]; then
    echo "✅ Token de GitHub personal guardado exitosamente"
else
    echo "❌ Error al obtener o guardar el token"
    exit 1
fi
