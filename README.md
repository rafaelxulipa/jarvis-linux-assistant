# J.A.R.V.I.S — Linux Assistant

> **Just A Rather Very Intelligent System**  
> Assistente pessoal sci-fi para Linux, inspirado no JARVIS do Homem de Ferro.

![JARVIS Preview](assets/images/preview.png)

---

## Visão Geral

O **JARVIS Linux Assistant** é um inicializador futurista que executa automaticamente ao ligar o sistema. Ele exibe um HUD cinematográfico com:

- Animação de boot estilo Iron Man
- Relógio digital neon com data
- Dashboard de métricas do sistema em tempo real
- Detecção de ferramentas de desenvolvimento
- Saudação inteligente por voz (TTS)
- Ações rápidas de desenvolvedor

---

## Compatibilidade

| Distro | Status |
|---|---|
| Ubuntu 22.04+ | ✔ Testado |
| Zorin OS 16+ | ✔ Compatível |
| Linux Mint 21+ | ✔ Compatível |
| Debian 12+ | ✔ Compatível |

---

## Instalação

Escolha o método que preferir:

### Opção 1 — Pacote `.deb` (recomendado)

Instale como qualquer programa — clique duplo no Nautilus/Nemo ou via terminal:

```bash
# 1. Gerar o pacote .deb (uma vez)
git clone <repo>
cd jarvis-linux-assistant
chmod +x packaging/build-deb.sh
./packaging/build-deb.sh
# → Gera: dist/jarvis-assistant_3.0.0_all.deb

# 2. Instalar
sudo dpkg -i dist/jarvis-assistant_3.0.0_all.deb
sudo apt-get install -f    # resolve dependências, se necessário

# 3. Executar
jarvis-assistant
```

O que o `.deb` faz automaticamente:
- Copia os arquivos para `/usr/share/jarvis-assistant/`
- Cria o comando `jarvis-assistant` em `/usr/bin/`
- Adiciona atalho no menu de aplicativos do sistema
- Configura autostart em `~/.config/autostart/`
- Instala dependências Python ausentes

Para desinstalar:
```bash
sudo dpkg -r jarvis-assistant
```

---

### Opção 2 — Script `install.sh`

```bash
git clone <repo>
cd jarvis-linux-assistant
chmod +x install.sh
./install.sh
```

O script:
1. Instala dependências do sistema (PyQt6, espeak-ng, etc.)
2. Cria um ambiente virtual Python em `.venv/`
3. Instala dependências Python
4. Pergunta seu nome para personalizar a saudação
5. Configura autostart (`~/.config/autostart/jarvis.desktop`)
6. Cria o comando `jarvis` em `~/.local/bin/`

---

### Opção 3 — Instalação Manual

```bash
# Dependências do sistema
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-pyqt6 espeak-ng mpg123

# Ambiente virtual
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt

# Executar
python3 src/main.py
```

---

## TTS — Voz

O sistema usa três engines em cascata (da melhor para a pior qualidade):

| Engine | Qualidade | Requer |
|---|---|---|
| **Piper** | ★★★★★ | Instalação separada |
| **espeak-ng** | ★★★☆☆ | `sudo apt install espeak-ng` |
| **gTTS** | ★★★★☆ | Internet + `mpg123` |

### Instalar Piper (recomendado)

```bash
# O instalador oferece instalar automaticamente.
# Manual:
wget https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz
tar xzf piper_linux_x86_64.tar.gz
cp piper/piper ~/.local/bin/

# Baixar modelo de voz português
mkdir -p ~/.local/share/piper
# Acesse: https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR
# Baixe os arquivos .onnx e .onnx.json
```

---

## Configuração

Edite `config/jarvis.json`:

```json
{
  "user_name": "Otávio",
  "voice_enabled": true,
  "tts_engine": "auto",
  "scanlines": true,
  "animations_enabled": true,
  "terminal": "gnome-terminal",
  "browser": "firefox",
  "editor": "code"
}
```

| Campo | Descrição |
|---|---|
| `user_name` | Nome usado na saudação |
| `tts_engine` | `"auto"`, `"piper"`, `"espeak"`, `"gtts"` |
| `voice_enabled` | Habilitar/desabilitar narração |
| `scanlines` | Efeito de scanlines |
| `terminal` | Emulador de terminal padrão |
| `editor` | Editor de código padrão |

---

## Autostart

O autostart é configurado automaticamente pelo instalador em:

```
~/.config/autostart/jarvis.desktop
```

Para **desativar** o autostart:

```bash
rm ~/.config/autostart/jarvis.desktop
```

Para **reativar**:

```bash
cp jarvis.desktop ~/.config/autostart/
# Edite o caminho Exec= no arquivo
```

---

## Atalhos de Teclado

| Tecla | Ação |
|---|---|
| `ESC` | Fechar o JARVIS |
| `F11` | Alternar tela cheia |

---

## Estrutura do Projeto

```
jarvis-linux-assistant/
├── src/
│   ├── main.py                   # Entry point
│   ├── ui/
│   │   ├── main_window.py        # Janela principal
│   │   ├── boot_sequence.py      # Animação de boot
│   │   ├── dashboard.py          # Dashboard principal
│   │   └── widgets/
│   │       ├── clock_widget.py   # Relógio digital HUD
│   │       ├── system_stats.py   # Métricas do sistema
│   │       ├── quick_actions.py  # Ações rápidas Dev
│   │       └── hud_elements.py   # Widgets decorativos
│   ├── services/
│   │   ├── system_info.py        # Coleta dados do sistema
│   │   ├── greeting.py           # Lógica de saudação
│   │   ├── tts_service.py        # Serviço de voz TTS
│   │   ├── dev_tools.py          # Detecção de ferramentas
│   │   └── voice_recognition.py  # Reconhecimento de voz
│   └── config/
│       └── settings.py           # Cores, fontes, config
├── assets/
│   ├── fonts/
│   ├── icons/
│   └── images/
├── sounds/
├── config/
│   └── jarvis.json               # Configuração do usuário
├── requirements.txt
├── install.sh
└── jarvis.desktop
```

---

## Funcionalidades

### Dashboard do Sistema
- CPU, RAM e Disco com barras de progresso neon
- Temperatura do processador
- Hostname e IP local
- Status de internet (online/offline)
- Tempo ligado do sistema (uptime)
- Contador de processos

### Detecção de Ferramentas
Detecta automaticamente: Docker, Git, Node.js, Python, Java, VS Code, npm, pip, Rust, Go

### Ações Rápidas
- Abrir VS Code
- Abrir terminal
- Abrir navegador
- Executar `docker ps`

### Voz
- Saudação personalizada (Bom dia/Boa tarde/Boa noite)
- Informa dia, data e hora
- Mensagem final de boas-vindas

---

## Roadmap (Extras Futuros)

- [ ] Reconhecimento de voz com wake-word "Jarvis"
- [ ] Integração com OpenAI API (GPT)
- [ ] Widget de clima atual
- [ ] Painel de notícias
- [ ] Integração com agenda
- [ ] Spotify / controle de música
- [ ] Efeitos sonoros de boot

---

## Solução de Problemas

**PyQt6 não encontrado:**
```bash
pip install PyQt6
# ou
sudo apt install python3-pyqt6
```

**Sem voz / TTS:**
```bash
sudo apt install espeak-ng
# Teste:
espeak-ng -v pt "Olá mundo"
```

**Erro de permissão no autostart:**
```bash
chmod +x ~/.config/autostart/jarvis.desktop
```

**Tela preta / sem janela:**
```bash
# Verificar se DISPLAY está setado
echo $DISPLAY
# Deve mostrar :0 ou :1
```

---

## Licença

MIT — use, modifique e distribua livremente.

---

*"Bem-vindo, senhor. Todos os sistemas operacionais."*
