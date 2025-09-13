#!/bin/bash
# Script de prueba para el sistema de releases
# Simula el proceso de creación de release sin hacer push a GitHub

set -euo pipefail

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Simulando proceso de release de bintools ===${NC}"

# Leer versión actual
CURRENT_VERSION=$(cat VERSION)
echo -e "${GREEN}Versión actual: $CURRENT_VERSION${NC}"

# Crear directorio temporal para simular el release
TEMP_DIR="/tmp/bintools-release-test"
RELEASE_DIR="$TEMP_DIR/bintools-$CURRENT_VERSION"

echo -e "${YELLOW}Creando directorio de prueba: $RELEASE_DIR${NC}"
mkdir -p "$RELEASE_DIR"

# Simular el proceso del workflow de GitHub Actions
echo -e "${BLUE}Simulando workflow de GitHub Actions...${NC}"

# Copiar archivos principales
echo "Copiando archivos principales..."
cp packages.sh "$RELEASE_DIR/"
cp micursor.py "$RELEASE_DIR/"
cp pymanager.sh "$RELEASE_DIR/"
cp fix_hdmi_audio.sh "$RELEASE_DIR/"
cp videoset.sh "$RELEASE_DIR/"
cp nextcloud-installer.sh "$RELEASE_DIR/"
cp hexroute "$RELEASE_DIR/"

# Copiar directorio de configuraciones
echo "Copiando configuraciones..."
cp -r configs "$RELEASE_DIR/"

# Crear archivo de versión
echo "Creando archivo VERSION..."
echo "$CURRENT_VERSION" > "$RELEASE_DIR/VERSION"

# Crear archivo de información del release
echo "Creando archivo RELEASE_INFO..."
cat > "$RELEASE_DIR/RELEASE_INFO" << EOF
bintools $CURRENT_VERSION
Released: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Repository: https://github.com/maurorosero/bintools
Install: curl -fsSL https://raw.githubusercontent.com/maurorosero/bintools/main/install.sh | bash -s -- --version $CURRENT_VERSION
EOF

# Crear paquete tar.gz
echo "Creando paquete tar.gz..."
cd "$TEMP_DIR"
tar -czf "bintools-$CURRENT_VERSION.tar.gz" "bintools-$CURRENT_VERSION/"

# Mostrar contenido del paquete
echo -e "${GREEN}Contenido del paquete:${NC}"
tar -tzf "bintools-$CURRENT_VERSION.tar.gz"

# Mostrar tamaño del paquete
PACKAGE_SIZE=$(du -h "bintools-$CURRENT_VERSION.tar.gz" | cut -f1)
echo -e "${GREEN}Tamaño del paquete: $PACKAGE_SIZE${NC}"

# Probar el instalador localmente
echo -e "${BLUE}Probando instalador localmente...${NC}"
TEST_INSTALL_DIR="/tmp/bintools-test-install"

# Simular descarga y extracción
echo "Simulando descarga y extracción..."
mkdir -p "$TEST_INSTALL_DIR"
tar -xzf "bintools-$CURRENT_VERSION.tar.gz" -C "$TEST_INSTALL_DIR" --strip-components=1

# Verificar instalación
echo -e "${GREEN}Verificando instalación de prueba...${NC}"
if [[ -f "$TEST_INSTALL_DIR/packages.sh" ]] && [[ -f "$TEST_INSTALL_DIR/VERSION" ]]; then
    INSTALLED_VERSION=$(cat "$TEST_INSTALL_DIR/VERSION")
    echo -e "${GREEN}✓ Instalación exitosa${NC}"
    echo -e "${GREEN}✓ Versión instalada: $INSTALLED_VERSION${NC}"
    echo -e "${GREEN}✓ Ubicación: $TEST_INSTALL_DIR${NC}"
    
    # Mostrar archivos instalados
    echo -e "${BLUE}Archivos instalados:${NC}"
    ls -la "$TEST_INSTALL_DIR" | grep -E '\.(sh|py)$|^[^d].*[^/]$'
    
    # Mostrar configuraciones
    echo -e "${BLUE}Configuraciones:${NC}"
    ls -la "$TEST_INSTALL_DIR/configs/"
    
else
    echo -e "${YELLOW}✗ Error en la instalación de prueba${NC}"
fi

# Probar el script de gestión
echo -e "${BLUE}Probando script de gestión...${NC}"
if [[ -f "./bintools-manager.sh" ]]; then
    echo "Probando comando 'version'..."
    ./bintools-manager.sh version 2>/dev/null || echo "Comando 'version' no funcionó (esperado, no hay instalación real)"
    
    echo "Probando comando 'list'..."
    ./bintools-manager.sh list 2>/dev/null || echo "Comando 'list' no funcionó (esperado, requiere conexión a GitHub)"
fi

# Limpiar archivos temporales
echo -e "${YELLOW}Limpiando archivos temporales...${NC}"
rm -rf "$TEMP_DIR"
rm -rf "$TEST_INSTALL_DIR"

echo -e "${GREEN}=== Prueba completada ===${NC}"
echo -e "${BLUE}Para crear un release real:${NC}"
echo "1. git add ."
echo "2. git commit -m 'Release $CURRENT_VERSION'"
echo "3. git tag -a $CURRENT_VERSION -m 'Release version $CURRENT_VERSION'"
echo "4. git push origin main"
echo "5. git push origin $CURRENT_VERSION"
echo ""
echo -e "${BLUE}El workflow de GitHub Actions se ejecutará automáticamente y creará el release.${NC}"
