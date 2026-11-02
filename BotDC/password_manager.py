import hmac
import html
import http.cookies
import os
import secrets
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
ENV_PATHS = [
    os.path.join(ROOT_DIR, ".env"),
    os.path.join(BASE_DIR, ".env"),
]
DEFAULT_PORT = int(os.getenv("PASSWORD_MANAGER_PORT", "8022"))

DEFAULT_KEYS = [
    "MASTER_PASSWORD",
    "TOKEN",
    "EDENAI_API_KEY",
    "DONOS",
    "PROTECTED_USERS",
    "GUILD_IDS",
    "STARTUP_CHANNEL_ID",
    "PRISAO_CHANNEL_ID",
]

KEY_METADATA = {
    "MASTER_PASSWORD": {
        "label": "Senha do Painel Web",
        "desc": "Senha mestra para login neste gerenciador (http://localhost:8022)",
        "badge": "badge-amber",
        "default": "admin123",
    },
    "TOKEN": {
        "label": "Token do Bot Discord",
        "desc": "Token secreto da aplicação gerado no Discord Developer Portal",
        "badge": "badge-cyan",
        "default": "",
    },
    "EDENAI_API_KEY": {
        "label": "Chave da API EdenAI",
        "desc": "Token de autenticação para as respostas de IA (/chat e /voice)",
        "badge": "badge-violet",
        "default": "",
    },
    "DONOS": {
        "label": "Administradores do Bot",
        "desc": "Nomes de usuário do Discord com permissão máxima (separados por vírgula)",
        "badge": "badge-emerald",
        "default": "",
    },
    "PROTECTED_USERS": {
        "label": "Usuários Protegidos (Anti-Sequestro)",
        "desc": "IDs ou nomes de usuários imunes a /stroll e /punish — quem tentar usá-los como alvo é punido (separados por vírgula)",
        "badge": "badge-amber",
        "default": "408471589366136833,asatotexco",
    },
    "GUILD_IDS": {
        "label": "IDs dos Servidores",
        "desc": "IDs dos servidores Discord para registro instantâneo dos Slash Commands",
        "badge": "badge-indigo",
        "default": "722857509659869204,1046231965872967690",
    },
    "STARTUP_CHANNEL_ID": {
        "label": "Canal de Inicialização",
        "desc": "ID do canal de texto onde o bot envia a mensagem de 'online'",
        "badge": "badge-indigo",
        "default": "1176698533039059055",
    },
    "PRISAO_CHANNEL_ID": {
        "label": "Canal de Voz da Prisão",
        "desc": "ID do canal de voz para onde os membros punidos são movidos (/punish)",
        "badge": "badge-rose",
        "default": "1269379224129634434",
    },
}

ACTIVE_SESSIONS: set[str] = set()


def _get_primary_env_path() -> str:
    for path in ENV_PATHS:
        if os.path.exists(path):
            return path
    return ENV_PATHS[0]


def load_env_entries() -> list[tuple[str, str]]:
    """Lê todas as variáveis do .env garantindo que as chaves padrão fiquem listadas."""
    env_path = _get_primary_env_path()
    entries_map: dict[str, str] = {}
    order: list[str] = []

    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and k not in entries_map:
                        entries_map[k] = v
                        order.append(k)
        except OSError:
            pass

    # Garante a presença das chaves conhecidas
    for def_key in DEFAULT_KEYS:
        if def_key not in entries_map:
            default_val = KEY_METADATA.get(def_key, {}).get("default", "")
            val = os.getenv(def_key, default_val)
            entries_map[def_key] = val
            order.append(def_key)

    return [(k, entries_map[k]) for k in order]


def save_env_entries(entries: list[tuple[str, str]]) -> None:
    """Salva todas as variáveis nos arquivos .env e atualiza os.environ."""
    content = "".join(f"{k}={v}\n" for k, v in entries if k.strip())

    for k, v in entries:
        if k.strip():
            os.environ[k.strip()] = v

    written = False
    for path in ENV_PATHS:
        if os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                written = True
            except OSError:
                pass

    if not written:
        with open(ENV_PATHS[0], "w", encoding="utf-8") as f:
            f.write(content)


def get_master_password() -> str:
    for k, v in load_env_entries():
        if k == "MASTER_PASSWORD":
            return v
    return os.getenv("MASTER_PASSWORD", "admin123")


def set_env_key(key: str, value: str) -> None:
    key = key.strip()
    if not key:
        return
    entries = load_env_entries()
    updated = False
    new_entries: list[tuple[str, str]] = []
    for k, v in entries:
        if k == key:
            new_entries.append((key, value))
            updated = True
        else:
            new_entries.append((k, v))
    if not updated:
        new_entries.append((key, value))
    save_env_entries(new_entries)


def delete_env_key(key: str) -> bool:
    if key == "MASTER_PASSWORD":
        return False
    if key in DEFAULT_KEYS:
        set_env_key(key, "")
        return True
    os.environ.pop(key, None)
    entries = [(k, v) for k, v in load_env_entries() if k != key]
    save_env_entries(entries)
    return True


STYLE_CSS = """
:root {
    --bg-base: #090d16;
    --bg-card: rgba(18, 26, 43, 0.75);
    --bg-card-border: rgba(148, 163, 184, 0.12);
    --bg-input: #0c1322;
    --text-main: #f1f5f9;
    --text-muted: #94a3b8;
    --primary: #0284c7;
    --primary-hover: #0369a1;
    --accent: #38bdf8;
    --success: #10b981;
    --success-hover: #059669;
    --danger: #ef4444;
    --danger-hover: #dc2626;
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif; }
body {
    background: radial-gradient(circle at 50% 0%, #172554 0%, var(--bg-base) 60%);
    color: var(--text-main);
    min-height: 100vh;
    padding: 24px 16px;
    line-height: 1.5;
}
.container { max-width: 980px; margin: 0 auto; }

.glass-card {
    background: var(--bg-card);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--bg-card-border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
}

h1 {
    font-size: 1.45rem;
    font-weight: 700;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: -0.02em;
}
h2 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-main);
}
.subtitle {
    color: var(--text-muted);
    font-size: 0.88rem;
    margin-top: 2px;
}

.row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }

input {
    background: var(--bg-input);
    border: 1px solid rgba(148, 163, 184, 0.2);
    color: #fff;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 0.92rem;
    transition: all 0.2s ease;
}
input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.18);
    background: #0f172a;
}
.val-input {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.88rem;
    width: 100%;
}

button {
    background: var(--primary);
    color: #fff;
    border: none;
    padding: 9px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.9rem;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.18s ease;
}
button:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
}
button:active {
    transform: translateY(0);
}

.btn-save-all {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    font-size: 0.98rem;
    padding: 11px 22px;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
}
.btn-save-all:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    box-shadow: 0 6px 18px rgba(16, 185, 129, 0.45);
}

.btn-secondary {
    background: rgba(51, 65, 85, 0.8);
    color: #cbd5e1;
    border: 1px solid rgba(148, 163, 184, 0.15);
}
.btn-secondary:hover {
    background: #334155;
    color: #fff;
}

.btn-success {
    background: #059669;
    padding: 8px 12px;
    font-size: 0.85rem;
}
.btn-success:hover { background: #047857; }

.btn-danger {
    background: rgba(220, 38, 38, 0.85);
    padding: 8px 10px;
    font-size: 0.85rem;
}
.btn-danger:hover { background: #b91c1c; }

table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 8px;
    margin-top: 10px;
}
th {
    text-align: left;
    padding: 8px 12px;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
td {
    padding: 12px;
    background: rgba(15, 23, 42, 0.55);
    border-top: 1px solid rgba(148, 163, 184, 0.08);
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
    vertical-align: middle;
}
td:first-child {
    border-left: 1px solid rgba(148, 163, 184, 0.08);
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
}
td:last-child {
    border-right: 1px solid rgba(148, 163, 184, 0.08);
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}
tr.env-row:hover td {
    background: rgba(30, 41, 59, 0.65);
    border-color: rgba(56, 189, 248, 0.25);
}

.msg {
    padding: 12px 18px;
    border-radius: 8px;
    margin-bottom: 20px;
    background: rgba(6, 95, 70, 0.35);
    border: 1px solid #059669;
    color: #a7f3d0;
    font-size: 0.92rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: fadeIn 0.25s ease;
}
.err {
    background: rgba(127, 29, 29, 0.35);
    border-color: #dc2626;
    color: #fca5a5;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
}

.key-badge {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-weight: 700;
    font-size: 0.88rem;
    padding: 4px 8px;
    border-radius: 6px;
    display: inline-block;
}
.badge-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-cyan { background: rgba(6, 182, 212, 0.15); color: #38bdf8; border: 1px solid rgba(6, 182, 212, 0.3); }
.badge-violet { background: rgba(139, 92, 246, 0.15); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.3); }
.badge-emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-indigo { background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
.badge-rose { background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }

.key-desc {
    font-size: 0.76rem;
    color: var(--text-muted);
    margin-top: 4px;
    line-height: 1.35;
}

.actions { display: flex; gap: 6px; align-items: center; justify-content: flex-end; }
.sticky-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--bg-card-border);
    flex-wrap: wrap;
    gap: 12px;
}

#toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #1e293b;
    border: 1px solid #38bdf8;
    color: #fff;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 0.9rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    display: none;
    z-index: 9999;
    animation: fadeIn 0.2s ease;
}
"""


def render_login_page(error: str = "") -> str:
    err_html = f'<div class="msg err">⚠️ {html.escape(error)}</div>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gerenciador .env — Login</title>
<style>{STYLE_CSS}</style>
</head>
<body>
<div class="container" style="max-width: 420px; margin-top: 90px;">
    <div class="glass-card" style="text-align: center;">
        <div style="font-size: 2.4rem; margin-bottom: 8px;">🔐</div>
        <h1 style="justify-content: center;">Cofre de Configurações</h1>
        <p class="subtitle" style="margin-bottom: 20px;">Insira a senha mestra configurada em <code>MASTER_PASSWORD</code></p>
        {err_html}
        <form method="POST" action="/login">
            <div style="margin-bottom: 16px;">
                <input type="password" name="password" placeholder="Sua senha mestre (.env)" required autofocus style="width: 100%; text-align: center; font-size: 1rem;">
            </div>
            <button type="submit" class="btn-save-all" style="width: 100%; justify-content: center;">Acessar Painel</button>
        </form>
    </div>
</div>
</body>
</html>"""


def render_dashboard(msg: str = "", err: str = "") -> str:
    entries = load_env_entries()
    msg_html = f'<div class="msg">✅ {html.escape(msg)}</div>' if msg else ""
    err_html = f'<div class="msg err">⚠️ {html.escape(err)}</div>' if err else ""

    rows_html = ""
    for idx, (key, value) in enumerate(entries):
        esc_key = html.escape(key)
        esc_val = html.escape(value)
        meta = KEY_METADATA.get(key, {})
        label = meta.get("label", esc_key)
        desc = meta.get("desc", "Variável de ambiente do projeto")
        badge_class = meta.get("badge", "badge-cyan")

        delete_btn = ""
        if key != "MASTER_PASSWORD":
            delete_btn = f"""
                <button type="button" class="btn-danger" onclick="deleteKey('{esc_key}')" title="Excluir variável do .env">🗑</button>
            """

        rows_html += f"""
        <tr class="env-row" data-key="{esc_key.lower()}" data-label="{label.lower()}">
            <td style="width: 32%;">
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span class="key-badge {badge_class}">{esc_key}</span>
                </div>
                <div style="font-weight: 600; font-size: 0.84rem; color: #e2e8f0; margin-top: 4px;">{label}</div>
                <div class="key-desc">{desc}</div>
                <input type="hidden" name="key_{idx}" value="{esc_key}">
            </td>
            <td>
                <input type="text" name="val_{idx}" value="{esc_val}" id="val-{idx}" class="val-input" placeholder="Definir valor de {esc_key}...">
            </td>
            <td style="width: 180px;">
                <div class="actions">
                    <button type="button" class="btn-secondary" onclick="togglePwd('{idx}')" title="Ocultar / Mostrar">👁</button>
                    <button type="button" class="btn-secondary" onclick="copyPwd('{idx}')" title="Copiar valor">📋</button>
                    <button type="button" class="btn-success" onclick="saveSingle('{idx}')" title="Salvar apenas esta linha">Salvar</button>
                    {delete_btn}
                </div>
            </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gerenciador de Configurações (.env)</title>
<style>{STYLE_CSS}</style>
</head>
<body>
<div class="container">
    <div class="topbar">
        <div>
            <h1>⚙️ Gerenciador de Senhas e Configurações</h1>
            <p class="subtitle">Modifique os valores do arquivo <code>.env</code> diretamente com aplicação instantânea.</p>
        </div>
        <div class="row">
            <button type="button" class="btn-secondary" onclick="toggleAll()">👁 Ocultar / Mostrar Todas</button>
            <form method="POST" action="/logout" style="margin:0;">
                <button type="submit" class="btn-secondary">Sair</button>
            </form>
        </div>
    </div>

    {msg_html}
    {err_html}

    <div class="glass-card">
        <form method="POST" action="/save-all" id="main-form">
            <input type="hidden" name="total" value="{len(entries)}">
            <div class="topbar" style="margin-bottom: 12px;">
                <div>
                    <h2>📋 Variáveis Listadas para Modificação</h2>
                    <span id="counter" class="subtitle">Mostrando {len(entries)} configurações</span>
                </div>
                <div class="row">
                    <input type="text" id="search" placeholder="🔍 Filtrar chave..." oninput="filterRows()" style="width: 200px; padding: 7px 12px; font-size: 0.85rem;">
                    <button type="submit" class="btn-save-all">💾 Salvar Todas as Senhas</button>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Variável (.env)</th>
                        <th>Valor / Senha</th>
                        <th style="text-align: right;">Ações Rápidas</th>
                    </tr>
                </thead>
                <tbody id="table-body">
                    {rows_html}
                </tbody>
            </table>

            <div class="sticky-footer">
                <span class="subtitle">Total de configurações salvas: <strong>{len(entries)}</strong></span>
                <button type="submit" class="btn-save-all">💾 Salvar Todas as Senhas</button>
            </div>
        </form>
    </div>

    <div class="glass-card">
        <h2>➕ Adicionar Outra Variável Personalizada</h2>
        <p class="subtitle" style="margin-bottom: 14px;">Adicione qualquer nova variável ao <code>.env</code> com facilidade.</p>
        <form method="POST" action="/save-single" class="row">
            <input type="text" name="key" placeholder="NOME_DA_VARIAVEL" required style="width: 250px; font-family: monospace;">
            <input type="text" name="value" placeholder="Valor da variável" style="flex: 1; min-width: 200px;">
            <button type="submit">Adicionar e Salvar</button>
        </form>
    </div>
</div>

<div id="toast">Copiado com sucesso!</div>

<!-- Form oculto para ações pontuais via JS -->
<form id="action-form" method="POST" style="display:none;">
    <input type="hidden" name="key" id="action-key">
    <input type="hidden" name="value" id="action-value">
</form>

<script>
let allHidden = false;

function showToast(text) {{
    const t = document.getElementById('toast');
    t.innerText = text;
    t.style.display = 'block';
    setTimeout(() => {{ t.style.display = 'none'; }}, 2200);
}}

function togglePwd(id) {{
    const el = document.getElementById('val-' + id);
    el.type = el.type === 'password' ? 'text' : 'password';
}}

function toggleAll() {{
    allHidden = !allHidden;
    document.querySelectorAll('.val-input').forEach(input => {{
        input.type = allHidden ? 'password' : 'text';
    }});
    showToast(allHidden ? 'Valores ocultados' : 'Valores visíveis');
}}

function copyPwd(id) {{
    const el = document.getElementById('val-' + id);
    if (!el.value) return;
    navigator.clipboard.writeText(el.value).then(() => {{
        showToast('📋 Copiado para a área de transferência!');
    }});
}}

function saveSingle(idx) {{
    const keyInput = document.querySelector(`input[name="key_${{idx}}"]`);
    const valInput = document.getElementById('val-' + idx);
    const form = document.getElementById('action-form');
    form.action = '/save-single';
    document.getElementById('action-key').value = keyInput.value;
    document.getElementById('action-value').value = valInput.value;
    form.submit();
}}

function deleteKey(keyName) {{
    if (!confirm('Deseja realmente remover ' + keyName + ' do .env?')) return;
    const form = document.getElementById('action-form');
    form.action = '/delete';
    document.getElementById('action-key').value = keyName;
    form.submit();
}}

function filterRows() {{
    const q = document.getElementById('search').value.toLowerCase().trim();
    let count = 0;
    document.querySelectorAll('.env-row').forEach(row => {{
        const k = row.getAttribute('data-key') || '';
        const l = row.getAttribute('data-label') || '';
        const match = k.includes(q) || l.includes(q);
        row.style.display = match ? '' : 'none';
        if (match) count++;
    }});
    document.getElementById('counter').innerText = 'Mostrando ' + count + ' configurações';
}}
</script>
</body>
</html>"""


class PasswordManagerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _is_authenticated(self) -> bool:
        cookie_header = self.headers.get("Cookie", "")
        cookies = http.cookies.SimpleCookie()
        cookies.load(cookie_header)
        sid = cookies.get("pm_session")
        return bool(sid and sid.value in ACTIVE_SESSIONS)

    def _send_html(self, content: str, status: int = 200, cookie: str = None):
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str, cookie: str = None):
        self.send_response(303)
        self.send_header("Location", location)
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def _parse_post(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(raw, keep_blank_values=True)
        return {k: v[0] for k, v in parsed.items()}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        msg = params.get("msg", [""])[0]
        err = params.get("err", [""])[0]

        if not self._is_authenticated():
            self._send_html(render_login_page(error=err))
            return

        self._send_html(render_dashboard(msg=msg, err=err))

    def do_POST(self):
        form = self._parse_post()

        if self.path == "/login":
            submitted = form.get("password", "")
            master = get_master_password()
            if hmac.compare_digest(submitted, master):
                token = secrets.token_hex(24)
                ACTIVE_SESSIONS.add(token)
                self._redirect("/", cookie=f"pm_session={token}; HttpOnly; Path=/; SameSite=Lax")
            else:
                self._send_html(render_login_page(error="Senha incorreta! Verifique MASTER_PASSWORD no .env."), status=401)
            return

        if not self._is_authenticated():
            self._redirect("/")
            return

        if self.path == "/logout":
            cookie_header = self.headers.get("Cookie", "")
            cookies = http.cookies.SimpleCookie()
            cookies.load(cookie_header)
            sid = cookies.get("pm_session")
            if sid:
                ACTIVE_SESSIONS.discard(sid.value)
            self._redirect("/", cookie="pm_session=; HttpOnly; Path=/; Max-Age=0")
            return

        # Salva todas as variáveis de uma única vez
        if self.path == "/save-all":
            try:
                total = int(form.get("total", "0"))
                new_entries: list[tuple[str, str]] = []
                for i in range(total):
                    k = form.get(f"key_{i}", "").strip().replace("=", "")
                    v = form.get(f"val_{i}", "").strip()
                    if k:
                        new_entries.append((k, v))

                if new_entries:
                    save_env_entries(new_entries)
                    self._redirect("/?msg=" + urllib.parse.quote("Todas as configurações foram salvas no .env com sucesso!"))
                else:
                    self._redirect("/?err=" + urllib.parse.quote("Nenhuma configuração válida para salvar."))
            except Exception as e:
                self._redirect("/?err=" + urllib.parse.quote(f"Erro ao salvar: {e}"))
            return

        # Salva apenas uma chave específica
        if self.path in ("/save", "/save-single"):
            key = form.get("key", "").strip().replace("=", "")
            value = form.get("value", "").strip()
            if not key:
                self._redirect("/?err=" + urllib.parse.quote("O nome da chave não pode ser vazio."))
                return
            set_env_key(key, value)
            self._redirect("/?msg=" + urllib.parse.quote(f"Variável '{key}' salva com sucesso no .env!"))
            return

        # Deleta uma chave
        if self.path == "/delete":
            key = form.get("key", "").strip()
            if not delete_env_key(key):
                self._redirect("/?err=" + urllib.parse.quote(f"A chave '{key}' não pode ser excluída."))
                return
            self._redirect("/?msg=" + urllib.parse.quote(f"Variável '{key}' removida com sucesso!"))
            return

        self._redirect("/")


def start_password_manager_server(port: int = DEFAULT_PORT, background: bool = True):
    server = ThreadingHTTPServer(("0.0.0.0", port), PasswordManagerHandler)
    print(f"🔐 Gerenciador do .env ativo em http://localhost:{port}")
    if background:
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        return server
    server.serve_forever()


if __name__ == "__main__":
    start_password_manager_server(port=DEFAULT_PORT, background=False)
