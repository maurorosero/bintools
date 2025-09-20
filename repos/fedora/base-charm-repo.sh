#!/bin/bash
# Script para instalar gum en Fedora
# gum está disponible en repositorios oficiales de Fedora

set -e

echo "🔧 Instalando gum en Fedora..."

# Verificar si gum ya está instalado
if command -v gum >/dev/null 2>&1; then
    echo "✅ gum ya está instalado"
    gum --version
    exit 0
fi

# Instalar gum desde repositorios oficiales
echo "📦 Instalando gum desde repositorios oficiales..."
sudo dnf install -y gum

# Verificar instalación
if command -v gum >/dev/null 2>&1; then
    echo "✅ gum instalado exitosamente!"
    gum --version
else
    echo "❌ Error instalando gum"
    exit 1
fi
