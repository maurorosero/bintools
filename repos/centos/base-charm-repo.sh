#!/bin/bash
# Script para configurar el repositorio de Charm en CentOS
# Permite instalar gum desde repositorio oficial

set -e

echo "🔧 Configurando repositorio de Charm para CentOS..."

# Verificar si gum ya está instalado
if command -v gum >/dev/null 2>&1; then
    echo "✅ gum ya está instalado"
    gum --version
    exit 0
fi

# Crear directorio para repositorios
echo "📁 Creando directorio para repositorios..."
sudo mkdir -p /etc/yum.repos.d

# Descargar y configurar clave GPG
echo "🔑 Descargando y configurando clave GPG..."
sudo rpm --import https://repo.charm.sh/yum/gpg.key

# Crear archivo de repositorio
echo "📝 Creando archivo de repositorio..."
sudo tee /etc/yum.repos.d/charm.repo > /dev/null <<EOF
[charm]
name=Charm
baseurl=https://repo.charm.sh/yum/
enabled=1
gpgcheck=1
gpgkey=https://repo.charm.sh/yum/gpg.key
EOF

# Actualizar caché de paquetes
echo "🔄 Actualizando caché de paquetes..."
sudo dnf makecache

# Instalar gum
echo "📦 Instalando gum..."
sudo dnf install -y gum

# Verificar instalación
if command -v gum >/dev/null 2>&1; then
    echo "✅ Repositorio de Charm configurado y gum instalado exitosamente!"
    gum --version
else
    echo "❌ Error instalando gum"
    exit 1
fi
