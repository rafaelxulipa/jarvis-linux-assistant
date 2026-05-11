from datetime import datetime


WEEKDAYS_PT = [
    "segunda-feira", "terça-feira", "quarta-feira",
    "quinta-feira", "sexta-feira", "sábado", "domingo",
]

MONTHS_PT = [
    "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def get_period_greeting() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Bom dia"
    elif 12 <= hour < 18:
        return "Boa tarde"
    else:
        return "Boa noite"


def get_greeting_text(user_name: str) -> str:
    now = datetime.now()
    period   = get_period_greeting()
    weekday  = WEEKDAYS_PT[now.weekday()]
    month    = MONTHS_PT[now.month]
    day      = now.day
    year     = now.year
    hour     = now.hour
    minute   = now.minute

    hour_text   = f"{hour:02d}"
    minute_text = f"{minute:02d}"

    return (
        f"{period}, {user_name}. "
        f"Hoje é {weekday}, {day} de {month} de {year}. "
        f"Agora são {hour_text} horas e {minute_text} minutos."
    )


def get_ready_message(user_name: str) -> str:
    return (
        f"Todos os sistemas online. "
        f"Tudo pronto, {user_name}. "
        f"Tenha um excelente dia. Vamos trabalhar."
    )


def get_boot_lines() -> list[str]:
    return [
        "JARVIS SYSTEM v3.0 — BOOT SEQUENCE INITIATED",
        "Carregando núcleo principal...",
        "Inicializando módulos de inteligência artificial...",
        "Verificando integridade dos sistemas...",
        "Carregando ambiente de desenvolvimento...",
        "Conectando à rede neural...",
        "Calibrando interface holográfica...",
        "Sincronizando dados do sistema...",
        "Ativando assistente de voz...",
        "Neural assistant online.",
        "All systems nominal.",
    ]
