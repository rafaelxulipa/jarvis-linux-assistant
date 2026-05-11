#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  JARVIS Linux Assistant — Instalador
#  Compatível com: Ubuntu, Zorin OS, Linux Mint
# ══════════════════════════════════════════════════════════
set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

JARVIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/jarvis.desktop"
VENV_DIR="$JARVIS_DIR/.venv"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       J.A.R.V.I.S  —  INSTALADOR v3.0               ║${NC}"
echo -e "${CYAN}║       Just A Rather Very Intelligent System          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Verificar Python 3 ───────────────────────────────
echo -e "${CYAN}[1/7]${NC} Verificando Python 3..."
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Erro: Python 3 não encontrado. Instalando...${NC}"
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
    espeak-ng \
    ffmpeg \
    mpg123 \
    libportaudio2 \
    portaudio19-dev \
    alsa-utils \
    2>/dev/null || true
echo -e "${GREEN}  ✔ Dependências do sistema instaladas${NC}"

# ── 3. Ambiente virtual ─────────────────────────────────
echo -e "${CYAN}[3/7]${NC} Criando ambiente virtual Python..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR" --system-site-packages
fi
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}  ✔ Venv em $VENV_DIR${NC}"

# ── 4. Dependências Python ──────────────────────────────
echo -e "${CYAN}[4/7]${NC} Instalando dependências Python..."
pip install --quiet --upgrade pip
pip install --quiet -r "$JARVIS_DIR/requirements.txt"
echo -e "${GREEN}  ✔ Dependências Python instaladas${NC}"

# ── 5. Configuração do usuário ──────────────────────────
echo -e "${CYAN}[5/7]${NC} Configurando usuário..."
read -p "  Qual é o seu nome? (padrão: Otávio): " USER_NAME
USER_NAME="${USER_NAME:-Otávio}"

CONFIG_FILE="$JARVIS_DIR/config/jarvis.json"
# Atualizar nome no config usando python
python3 -c "
import json, sys
with open('$CONFIG_FILE') as f:
    cfg = json.load(f)
cfg['user_name'] = '$USER_NAME'
with open('$CONFIG_FILE', 'w') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
print('  Config salvo.')
"
echo -e "${GREEN}  ✔ Usuário configurado: $USER_NAME${NC}"

# ── 6. Autostart ────────────────────────────────────────
echo -e "${CYAN}[6/7]${NC} Configurando inicialização automática..."
mkdir -p "$AUTOSTART_DIR"

PYTHON_BIN="$VENV_DIR/bin/python3"

cat > "$DESKTOP_FILE" <<EOF
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

chmod +x "$DESKTOP_FILE"
echo -e "${GREEN}  ✔ Autostart configurado em $DESKTOP_FILE${NC}"

# ── 7. Script de execução ───────────────────────────────
echo -e "${CYAN}[7/7]${NC} Criando script de execução..."
LAUNCHER="$JARVIS_DIR/jarvis.sh"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
cd "$JARVIS_DIR"
exec python3 src/main.py "\$@"
EOF
chmod +x "$LAUNCHER"

# Symlink opcional em ~/.local/bin
mkdir -p "$HOME/.local/bin"
ln -sf "$LAUNCHER" "$HOME/.local/bin/jarvis" 2>/dev/null || true
echo -e "${GREEN}  ✔ Execute com: jarvis  (ou $LAUNCHER)${NC}"

# ── Piper TTS (opcional) ─────────────────────────────────
echo ""
echo -e "${YELLOW}╔══════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  TTS OPCIONAL: Piper (voz mais realista)     ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════╝${NC}"
read -p "  Instalar Piper TTS para voz mais realista? [s/N]: " INSTALL_PIPER
if [[ "$INSTALL_PIPER" =~ ^[Ss]$ ]]; then
    PIPER_DIR="$HOME/.local/share/piper"
    mkdir -p "$PIPER_DIR"
    echo "  Baixando Piper..."
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz"
    else
        PIPER_URL="https://github.com/rhasspy/piper/releases/latest/download/piper_linux_aarch64.tar.gz"
    fi
    wget -q --show-progress -O /tmp/piper.tar.gz "$PIPER_URL"
    tar -xzf /tmp/piper.tar.gz -C /tmp/
    cp /tmp/piper/piper "$HOME/.local/bin/" 2>/dev/null || true
    echo -e "${GREEN}  ✔ Piper instalado${NC}"
    echo "  Baixe modelos em: https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR"
    echo "  Salve em: $PIPER_DIR/"
fi

# ── Resumo ──────────────────────────────────────────────
echo ""
echo -e "${CYAN}══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  JARVIS instalado com sucesso!${NC}"
echo ""
echo -e "  ${CYAN}Para executar agora:${NC}  jarvis"
echo -e "  ${CYAN}Ou:${NC}                   $LAUNCHER"
echo -e "  ${CYAN}Autostart:${NC}            ativo (iniciará com o sistema)"
echo -e "  ${CYAN}Configuração:${NC}         $CONFIG_FILE"
echo -e "${CYAN}══════════════════════════════════════════════════════${NC}"
echo ""
