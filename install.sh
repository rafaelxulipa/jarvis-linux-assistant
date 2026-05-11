#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  JARVIS Linux Assistant — Instalador
#  Compatível com: Ubuntu 22.04+, Zorin OS 16+, Linux Mint 21+, Debian 12+
# ══════════════════════════════════════════════════════════
set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

JARVIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOSTART_DIR="$HOME/.config/autostart"
VENV_DIR="$JARVIS_DIR/.venv"
CONFIG_FILE="$JARVIS_DIR/config/jarvis.json"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       J.A.R.V.I.S  —  INSTALADOR v3.0               ║${NC}"
echo -e "${CYAN}║       Just A Rather Very Intelligent System          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Verificar Python 3 ───────────────────────────────
echo -e "${CYAN}[1/7]${NC} Verificando Python 3..."
if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}  Python 3 não encontrado. Instalando...${NC}"
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip python3-venv
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}  ✔ $PYTHON_VERSION${NC}"

# ── 2. Dependências do sistema ──────────────────────────
echo -e "${CYAN}[2/7]${NC} Instalando dependências do sistema..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-pyqt6 \
    python3-psutil \
    python3-distro \
    espeak-ng \
    mpg123 \
    2>/dev/null || true
echo -e "${GREEN}  ✔ Dependências instaladas${NC}"

# ── 3. Ambiente virtual ─────────────────────────────────
echo -e "${CYAN}[3/7]${NC} Criando ambiente virtual Python..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR" --system-site-packages
fi
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}  ✔ Ambiente em $VENV_DIR${NC}"

# ── 4. Dependências Python ──────────────────────────────
echo -e "${CYAN}[4/7]${NC} Instalando dependências Python..."
pip install --quiet --upgrade pip
pip install --quiet -r "$JARVIS_DIR/requirements.txt"
# edge-tts requer Python 3.9+ — instalar separado para garantir compatibilidade
pip install --quiet "edge-tts>=6.1.9" 2>/dev/null || true
echo -e "${GREEN}  ✔ Dependências Python instaladas${NC}"

# ── 5. Configuração do usuário ──────────────────────────
echo -e "${CYAN}[5/7]${NC} Configuração do usuário..."
echo -n "  Qual é o seu nome? (Enter para pular): "
read USER_NAME

if [ -n "$USER_NAME" ]; then
    python3 - <<PYEOF
import json
with open("$CONFIG_FILE") as f:
    cfg = json.load(f)
cfg["user_name"] = """$USER_NAME"""
with open("$CONFIG_FILE", "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
PYEOF
    echo -e "${GREEN}  ✔ Nome salvo: $USER_NAME${NC}"
else
    echo -e "  Mantendo nome padrão. Edite ${CYAN}config/jarvis.json${NC} depois."
fi

# ── 6. Autostart ────────────────────────────────────────
echo -e "${CYAN}[6/7]${NC} Configurando inicialização automática..."
mkdir -p "$AUTOSTART_DIR"
PYTHON_BIN="$VENV_DIR/bin/python3"

cat > "$AUTOSTART_DIR/jarvis-assistant.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=JARVIS Linux Assistant
Comment=Personal AI Development Assistant
Exec=$PYTHON_BIN $JARVIS_DIR/src/main.py
Icon=$JARVIS_DIR/assets/icons/jarvis.png
Terminal=false
Categories=Utility;System;
StartupNotify=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
EOF

chmod +x "$AUTOSTART_DIR/jarvis-assistant.desktop"
echo -e "${GREEN}  ✔ Autostart configurado${NC}"

# ── 7. Comando de execução ──────────────────────────────
echo -e "${CYAN}[7/7]${NC} Criando comando 'jarvis'..."
LAUNCHER="$JARVIS_DIR/jarvis.sh"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
cd "$JARVIS_DIR"
exec python3 src/main.py "\$@"
EOF
chmod +x "$LAUNCHER"

mkdir -p "$HOME/.local/bin"
ln -sf "$LAUNCHER" "$HOME/.local/bin/jarvis"

# Garantir que ~/.local/bin está no PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo -e "${YELLOW}  PATH atualizado em ~/.bashrc — reabra o terminal para usar 'jarvis' diretamente.${NC}"
fi
echo -e "${GREEN}  ✔ Comando 'jarvis' criado${NC}"

# ── Piper TTS (opcional) ─────────────────────────────────
echo ""
echo -e "${YELLOW}╔══════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  OPCIONAL: Piper TTS (voz mais realista)     ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════╝${NC}"
echo -n "  Instalar Piper? [s/N]: "
read INSTALL_PIPER

if [[ "$INSTALL_PIPER" =~ ^[Ss]$ ]]; then
    PIPER_BIN="$HOME/.local/bin/piper"
    PIPER_MODELS="$HOME/.local/share/piper"
    mkdir -p "$PIPER_MODELS"

    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz"
    elif [ "$ARCH" = "aarch64" ]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/latest/download/piper_linux_aarch64.tar.gz"
    else
        echo -e "${RED}  Arquitetura $ARCH não suportada pelo Piper.${NC}"
        INSTALL_PIPER=""
    fi

    if [[ "$INSTALL_PIPER" =~ ^[Ss]$ ]]; then
        echo "  Baixando Piper..."
        wget -q --show-progress -O /tmp/piper.tar.gz "$PIPER_URL"
        tar -xzf /tmp/piper.tar.gz -C /tmp/
        cp /tmp/piper/piper "$HOME/.local/bin/"
        chmod +x "$HOME/.local/bin/piper"
        rm -rf /tmp/piper /tmp/piper.tar.gz
        echo -e "${GREEN}  ✔ Piper instalado${NC}"
        echo ""
        echo -e "  Baixe um modelo de voz em português e salve em:"
        echo -e "  ${CYAN}$PIPER_MODELS/${NC}"
        echo -e "  Modelos: https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR"
    fi
fi

# ── Resumo ──────────────────────────────────────────────
echo ""
echo -e "${CYAN}══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  J.A.R.V.I.S instalado com sucesso!${NC}"
echo ""
echo -e "  ${CYAN}Executar agora:${NC}  bash $LAUNCHER"
echo -e "  ${CYAN}Ou (novo terminal):${NC}  jarvis"
echo -e "  ${CYAN}Configuração:${NC}    $CONFIG_FILE"
echo -e "  ${CYAN}Autostart:${NC}       ativo (inicia com o sistema)"
echo -e "${CYAN}══════════════════════════════════════════════════════${NC}"
echo ""
