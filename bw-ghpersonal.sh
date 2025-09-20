#!/bin/bash

# Script para obtener el token de GitHub personal desde Bitwarden y guardarlo en git-tokens.py
# Reemplaza "MROSERO" por el usuario actual en mayúsculas

# Obtener el usuario actual en mayúsculas
CURRENT_USER=$(whoami | tr '[:lower:]' '[:upper:]')

echo "🔍 Obteniendo token de GitHub personal desde Bitwarden..."
echo "👤 Usuario: $CURRENT_USER"

# Sincronizar con Bitwarden para obtener la información más actualizada
echo "🔄 Sincronizando con Bitwarden..."
if ! bw sync; then
    echo "❌ Error al sincronizar con Bitwarden. Verifica tu contraseña maestra y conexión."
    exit 1
fi

# Verificar que el item GITHUB existe
echo "🔍 Verificando que el item 'GITHUB' existe..."
if ! bw get item "GITHUB" >/dev/null 2>&1; then
    echo "❌ Error: No se encontró el item 'GITHUB' en Bitwarden."
    echo "💡 Asegúrate de que el item existe y se llama exactamente 'GITHUB'."
    exit 1
fi

# Verificar que el campo del token existe
echo "🔍 Verificando que el campo '${CURRENT_USER} FULL TOKEN' existe..."
if ! bw get item "GITHUB" | jq -e ".fields[] | select(.name == \"${CURRENT_USER} FULL TOKEN\")" >/dev/null 2>&1; then
    echo "❌ Error: No se encontró el campo '${CURRENT_USER} FULL TOKEN' en el item GITHUB."
    echo "💡 Campos disponibles en el item GITHUB:"
    bw get item "GITHUB" | jq -r '.fields[] | .name' 2>/dev/null || echo "   (No se pudieron obtener los nombres de campos)"
    exit 1
fi

# Obtener el token completo desde Bitwarden usando jq
echo "🔑 Extrayendo token completo de GitHub..."
TOKEN=$(bw get item "GITHUB" | jq -r ".fields[] | select(.name == \"${CURRENT_USER} FULL TOKEN\") | .value")

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "❌ Error: No se pudo extraer el token del campo '${CURRENT_USER} FULL TOKEN'."
    echo "💡 Verifica que el campo contiene un token válido."
    exit 1
fi

echo "🔐 Guardando token en git-tokens.py..."
echo "$TOKEN" | ./git-tokens.py set github-personal --token -

if [ $? -eq 0 ]; then
    echo "✅ Token de GitHub personal guardado exitosamente"
else
    echo "❌ Error al obtener o guardar el token"
    exit 1
fi
