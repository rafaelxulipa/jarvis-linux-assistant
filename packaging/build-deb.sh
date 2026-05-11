#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  Gera jarvis-assistant_3.0.0_all.deb
#  Execute na raiz do projeto: ./packaging/build-deb.sh
# ══════════════════════════════════════════════════════════
set -e

CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEB_ROOT="$SCRIPT_DIR/deb/jarvis-assistant"
INSTALL_DIR="$DEB_ROOT/usr/share/jarvis-assistant"
OUT_DIR="$PROJECT_DIR/dist"
DEB_FILE="$OUT_DIR/jarvis-assistant_3.0.0_all.deb"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║   JARVIS — Build .deb v3.0.0                         ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar dpkg-deb
if ! command -v dpkg-deb &>/dev/null; then
    echo -e "${RED}dpkg-deb não encontrado. Instale: sudo apt install dpkg${NC}"
    exit 1
fi

# Copiar código-fonte para usr/share/jarvis-assistant/
echo "  Copiando arquivos do projeto..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

cp -r "$PROJECT_DIR/src"              "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/config"           "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/assets"           "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/sounds"           "$INSTALL_DIR/"
cp    "$PROJECT_DIR/requirements.txt" "$INSTALL_DIR/"

# Garantir que os ícones existem
if [ ! -f "$INSTALL_DIR/assets/icons/jarvis.png" ]; then
    echo -e "${YELLOW}  Ícones não encontrados. Gerando...${NC}"
    python3 "$PROJECT_DIR/packaging/generate_icons.py"
    cp -r "$PROJECT_DIR/assets" "$INSTALL_DIR/"
fi

# Ajustar permissões
echo "  Ajustando permissões..."
find "$DEB_ROOT" -type d -exec chmod 755 {} \;
find "$DEB_ROOT" -type f -exec chmod 644 {} \;
chmod 755 "$DEB_ROOT/DEBIAN/postinst"
chmod 755 "$DEB_ROOT/DEBIAN/prerm"
chmod 755 "$DEB_ROOT/usr/bin/jarvis-assistant"

# Calcular tamanho instalado (em KB)
INSTALLED_SIZE=$(du -sk "$INSTALL_DIR" | cut -f1)
sed -i "s/^Installed-Size:.*/Installed-Size: $INSTALLED_SIZE/" "$DEB_ROOT/DEBIAN/control"

# Build
mkdir -p "$OUT_DIR"
dpkg-deb --build --root-owner-group "$DEB_ROOT" "$DEB_FILE"

SIZE_MB=$(du -sh "$DEB_FILE" | cut -f1)
echo -e "${GREEN}"
echo "  ✔ Pacote gerado: $DEB_FILE  ($SIZE_MB)"
echo ""
echo "  Instalar:"
echo "    sudo dpkg -i $DEB_FILE"
echo "    sudo apt-get install -f   # resolver dependências, se necessário"
echo -e "${NC}"
