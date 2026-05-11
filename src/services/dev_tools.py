import shutil
import subprocess
import os


def _cmd_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _get_version(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        return result.stdout.strip().splitlines()[0] if result.stdout else result.stderr.strip().splitlines()[0]
    except Exception:
        return ""


def detect_tools() -> list[dict]:
    tools = []

    # Docker
    found = _cmd_exists("docker")
    version = ""
    if found:
        version = _get_version(["docker", "--version"])
    tools.append({"name": "Docker", "found": found, "version": version, "icon": "🐳"})

    # Git
    found = _cmd_exists("git")
    version = _get_version(["git", "--version"]) if found else ""
    tools.append({"name": "Git", "found": found, "version": version, "icon": "🔀"})

    # Node.js
    found = _cmd_exists("node")
    version = _get_version(["node", "--version"]) if found else ""
    tools.append({"name": "Node.js", "found": found, "version": version, "icon": "⬡"})

    # Python
    found = _cmd_exists("python3")
    version = _get_version(["python3", "--version"]) if found else ""
    tools.append({"name": "Python 3", "found": found, "version": version, "icon": "🐍"})

    # Java
    found = _cmd_exists("java")
    version = _get_version(["java", "-version"]) if found else ""
    tools.append({"name": "Java", "found": found, "version": version, "icon": "☕"})

    # VSCode
    found = _cmd_exists("code")
    version = _get_version(["code", "--version"]) if found else ""
    tools.append({"name": "VS Code", "found": found, "version": version.splitlines()[0] if version else "", "icon": "💻"})

    # npm
    found = _cmd_exists("npm")
    version = _get_version(["npm", "--version"]) if found else ""
    tools.append({"name": "npm", "found": found, "version": version, "icon": "📦"})

    # pip
    found = _cmd_exists("pip3") or _cmd_exists("pip")
    cmd = "pip3" if _cmd_exists("pip3") else "pip"
    version = _get_version([cmd, "--version"]) if found else ""
    tools.append({"name": "pip", "found": found, "version": version, "icon": "📦"})

    # Rust
    found = _cmd_exists("rustc")
    version = _get_version(["rustc", "--version"]) if found else ""
    tools.append({"name": "Rust", "found": found, "version": version, "icon": "🦀"})

    # Go
    found = _cmd_exists("go")
    version = _get_version(["go", "version"]) if found else ""
    tools.append({"name": "Go", "found": found, "version": version, "icon": "🐹"})

    return tools


def run_docker_ps() -> str:
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout if result.stdout else "Nenhum container em execução."
    except Exception as e:
        return f"Erro: {e}"


def run_git_status(path: str) -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, timeout=5, cwd=path
        )
        return result.stdout if result.stdout else "Working tree limpa."
    except Exception as e:
        return f"Erro: {e}"


def open_application(app: str, args: list[str] = None) -> None:
    cmd = [app] + (args or [])
    subprocess.Popen(cmd, start_new_session=True)


def open_vscode(path: str = None) -> None:
    args = [path] if path else []
    open_application("code", args)


def open_terminal() -> None:
    for term in ("gnome-terminal", "xterm", "konsole", "xfce4-terminal", "tilix"):
        if _cmd_exists(term):
            open_application(term)
            return


def open_browser(url: str = None) -> None:
    for browser in ("firefox", "chromium-browser", "chromium", "google-chrome"):
        if _cmd_exists(browser):
            args = [url] if url else []
            open_application(browser, args)
            return


def get_favorite_projects(base_paths: list[str] = None) -> list[str]:
    if base_paths:
        return base_paths
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "WORKSPACE"),
        os.path.join(home, "workspace"),
        os.path.join(home, "Projects"),
        os.path.join(home, "projects"),
        os.path.join(home, "dev"),
    ]
    projects = []
    for base in candidates:
        if os.path.isdir(base):
            try:
                for item in sorted(os.listdir(base))[:10]:
                    full = os.path.join(base, item)
                    if os.path.isdir(full) and os.path.exists(os.path.join(full, ".git")):
                        projects.append(full)
            except Exception:
                pass
    return projects[:8]
