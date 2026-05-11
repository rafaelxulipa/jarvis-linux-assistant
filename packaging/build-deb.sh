#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  Gera jarvis-assistant_3.0.0_all.deb
#  Execute na raiz do projeto: ./packaging/build-deb.sh
# ══════════════════════════════════════════════════════════
set -e

CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEB_ROOT="$SCRIPT_DIR/deb/jarvis-assistant"
INSTALL_DIR="$DEB_ROOT/usr/share/jarvis-assistant"
OUT_DIR="$PROJECT_DIR/dist"

echo -e "${CYAN}Construindo pacote .deb...${NC}"

# Verificar dpkg-deb
if ! command -v dpkg-deb &>/dev/null; then
    echo -e "${RED}dpkg-deb não encontrado. Instale: sudo apt install dpkg${NC}"
    exit 1
fi

# Copiar código-fonte para usr/share/jarvis-assistant/
echo "  Copiando arquivos do projeto..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

cp -r "$PROJECT_DIR/src"         "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/config"      "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/assets"      "$INSTALL_DIR/" 2>/dev/null || mkdir -p "$INSTALL_DIR/assets"
cp -r "$PROJECT_DIR/sounds"      "$INSTALL_DIR/" 2>/dev/null || mkdir -p "$INSTALL_DIR/sounds"
cp    "$PROJECT_DIR/requirements.txt" "$INSTALL_DIR/"

# Ajustar permissões
chmod -R 755 "$DEB_ROOT/DEBIAN"
chmod 755    "$DEB_ROOT/usr/bin/jarvis-assistant"

# Calcular tamanho instalado (em KB)
INSTALLED_SIZE=$(du -sk "$INSTALL_DIR" | cut -f1)
sed -i "s/^Installed-Size:.*/Installed-Size: $INSTALLED_SIZE/" "$DEB_ROOT/DEBIAN/control" 2>/dev/null || \
    echo "Installed-Size: $INSTALLED_SIZE" >> "$DEB_ROOT/DEBIAN/control"

# Build
mkdir -p "$OUT_DIR"
DEB_FILE="$OUT_DIR/jarvis-assistant_3.0.0_all.deb"

dpkg-deb --build --root-owner-group "$DEB_ROOT" "$DEB_FILE"

echo -e "${GREEN}"
echo "  ✔ Pacote gerado: $DEB_FILE"
echo "  Instalar com:"
echo "    sudo dpkg -i $DEB_FILE"
echo "    sudo apt-get install -f   # resolver dependências se necessário"
echo -e "${NC}"
