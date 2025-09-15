#!/bin/bash
# Script para configurar el repositorio de Charm en Fedora
# Permite instalar gum desde repositorio oficial

set -e

echo "🔧 Configurando repositorio de Charm para Fedora..."

# Crear directorio de keyrings si no existe
echo "📁 Creando directorio de keyrings..."
sudo mkdir -p /etc/apt/keyrings

# Descargar y configurar clave GPG
echo "🔑 Descargando y configurando clave GPG..."
curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg

# Agregar repositorio a sources.list
echo "📝 Agregando repositorio a sources.list..."
echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list

# Actualizar lista de paquetes
echo "🔄 Actualizando lista de paquetes..."
sudo apt update

echo "✅ Repositorio de Charm configurado exitosamente!"
echo "📦 Ahora puedes instalar gum con: sudo apt install gum"
