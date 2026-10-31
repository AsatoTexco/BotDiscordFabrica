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
DEFAULT_KEYS = ["MASTER_PASSWORD", "TOKEN", "EDENAI_API_KEY"]

ACTIVE_SESSIONS: set[str] = set()


def _get_primary_env_path() -> str:
    for path in ENV_PATHS:
        if os.path.exists(path):
            return path
    return ENV_PATHS[0]


def load_env_entries() -> list[tuple[str, str]]:
    """Lê todas as variáveis do .env garantindo que as senhas essenciais fiquem listadas."""
    env_path = _get_primary_env_path()
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()

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
                    if k and k not in seen:
                        entries.append((k, v))
                        seen.add(k)
        except OSError:
            pass

    # Garante que as chaves essenciais sempre estejam listadas para preenchimento
    for def_key in DEFAULT_KEYS:
        if def_key not in seen:
            val = "admin123" if def_key == "MASTER_PASSWORD" else os.getenv(def_key, "")
            entries.append((def_key, val))
            seen.add(def_key)

    return entries


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
    if key in DEFAULT_KEYS:
        # Chaves padrão não são deletadas, apenas limpas
        set_env_key(key, "")
        return True
    os.environ.pop(key, None)
    entries = [(k, v) for k, v in load_env_entries() if k != key]
    save_env_entries(entries)
    return True


STYLE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
body { background: #0f172a; color: #f8fafc; min-height: 100vh; padding: 20px; }
.container { max-width: 920px; margin: 0 auto; }
.card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
h1 { font-size: 1.35rem; color: #38bdf8; display: flex; align-items: center; gap: 8px; }
h2 { font-size: 1.05rem; margin-bottom: 12px; color: #e2e8f0; }
.row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
input { background: #0f172a; border: 1px solid #475569; color: #f8fafc; padding: 9px 12px; border-radius: 6px; font-size: 0.92rem; }
input:focus { outline: none; border-color: #38bdf8; }
button { background: #0284c7; color: #fff; border: none; padding: 9px 14px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: background 0.15s; }
button:hover { background: #0369a1; }
.btn-save-all { background: #10b981; font-size: 1rem; padding: 10px 18px; }
.btn-save-all:hover { background: #059669; }
.btn-danger { background: #dc2626; }
.btn-danger:hover { background: #b91c1c; }
.btn-secondary { background: #475569; }
.btn-secondary:hover { background: #334155; }
.btn-success { background: #059669; padding: 8px 12px; }
.btn-success:hover { background: #047857; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { text-align: left; padding: 12px 8px; border-bottom: 1px solid #334155; font-size: 0.92rem; vertical-align: middle; }
th { color: #94a3b8; font-weight: 600; }
.msg { padding: 12px 14px; border-radius: 6px; margin-bottom: 16px; background: #065f46; color: #d1fae5; font-size: 0.92rem; font-weight: 500; }
.err { background: #7f1d1d; color: #fecaca; }
.topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.key-badge { font-family: monospace; font-weight: 700; color: #38bdf8; background: #0f172a; padding: 6px 10px; border-radius: 5px; border: 1px solid #334155; display: inline-block; word-break: break-all; }
.key-desc { font-size: 0.75rem; color: #94a3b8; margin-top: 3px; }
.val-input { font-family: monospace; width: 100%; }
.actions { display: flex; gap: 6px; align-items: center; justify-content: flex-end; }
.sticky-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid #334155; flex-wrap: wrap; gap: 10px; }
"""


def render_login_page(error: str = "") -> str:
    err_html = f'<div class="msg err">{html.escape(error)}</div>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gerenciador .env - Login</title>
<style>{STYLE_CSS}</style>
</head>
<body>
<div class="container" style="max-width: 400px; margin-top: 80px;">
    <div class="card">
        <h1>🔒 Senhas do .env</h1>
        <p style="color:#94a3b8; font-size:0.88rem; margin: 8px 0 16px 0;">Digite a senha mestre configurada em MASTER_PASSWORD</p>
        {err_html}
        <form method="POST" action="/login">
            <div style="margin-bottom: 12px;">
                <input type="password" name="password" placeholder="Senha Mestre (.env)" required autofocus style="width: 100%;">
            </div>
            <button type="submit" style="width: 100%;">Entrar</button>
        </form>
    </div>
</div>
</body>
</html>"""


def _get_key_label(key: str) -> str:
    descriptions = {
        "MASTER_PASSWORD": "Senha de acesso a este gerenciador",
        "TOKEN": "Token do Bot no Discord Developer Portal",
        "EDENAI_API_KEY": "Chave de API da IA (EdenAI)",
        "PASSWORD_MANAGER_PORT": "Porta da interface web (padrão: 8022)",
    }
    return descriptions.get(key, "Variável de ambiente do .env")


def render_dashboard(msg: str = "", err: str = "") -> str:
    entries = load_env_entries()
    msg_html = f'<div class="msg">{html.escape(msg)}</div>' if msg else ""
    err_html = f'<div class="msg err">{html.escape(err)}</div>' if err else ""

    rows_html = ""
    for idx, (key, value) in enumerate(entries):
        esc_key = html.escape(key)
        esc_val = html.escape(value)
        desc = _get_key_label(key)

        delete_btn = ""
        if key not in ("MASTER_PASSWORD", "TOKEN", "EDENAI_API_KEY"):
            delete_btn = f"""
                <button type="button" class="btn-danger" onclick="deleteKey('{esc_key}')" title="Excluir do .env">🗑</button>
            """

        rows_html += f"""
        <tr class="env-row">
            <td style="width: 30%;">
                <span class="key-badge">{esc_key}</span>
                <div class="key-desc">{desc}</div>
                <input type="hidden" name="key_{idx}" value="{esc_key}">
            </td>
            <td>
                <input type="text" name="val_{idx}" value="{esc_val}" id="val-{idx}" class="val-input" placeholder="Insira o valor de {esc_key}...">
            </td>
            <td style="width: 170px;">
                <div class="actions">
                    <button type="button" class="btn-secondary" onclick="togglePwd('{idx}')" title="Ocultar / Mostrar">👁</button>
                    <button type="button" class="btn-secondary" onclick="copyPwd('{idx}')" title="Copiar">📋</button>
                    <button type="button" class="btn-success" onclick="saveSingle('{idx}')" title="Salvar somente esta">Salvar</button>
                    {delete_btn}
                </div>
            </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gerenciador de Senhas (.env)</title>
<style>{STYLE_CSS}</style>
</head>
<body>
<div class="container">
    <div class="topbar">
        <h1>🔐 Senhas e Configurações (.env)</h1>
        <div class="row">
            <button type="button" class="btn-secondary" onclick="toggleAll()">👁 Alternar Ocultar/Mostrar</button>
            <form method="POST" action="/logout" style="margin:0;">
                <button type="submit" class="btn-secondary">Sair</button>
            </form>
        </div>
    </div>

    {msg_html}
    {err_html}

    <div class="card">
        <form method="POST" action="/save-all" id="main-form">
            <input type="hidden" name="total" value="{len(entries)}">
            <div class="topbar" style="margin-bottom: 8px;">
                <div>
                    <h2 style="margin:0;">📋 Senhas Listadas para Modificação</h2>
                    <p style="color:#94a3b8; font-size:0.85rem; margin-top:4px;">Altere os valores desejados e clique em Salvar.</p>
                </div>
                <button type="submit" class="btn-save-all">💾 Salvar Todas as Senhas</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Nome da Senha / Chave</th>
                        <th>Valor (.env)</th>
                        <th style="text-align: right;">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <div class="sticky-footer">
                <span style="color:#94a3b8; font-size:0.85rem;">Total de variáveis listadas: <strong>{len(entries)}</strong></span>
                <button type="submit" class="btn-save-all">💾 Salvar Todas as Senhas</button>
            </div>
        </form>
    </div>

    <div class="card">
        <h2>➕ Adicionar Outra Variável ao .env</h2>
        <form method="POST" action="/save-single" class="row">
            <input type="text" name="key" placeholder="NOME_DA_VARIAVEL" required style="max-width: 260px; font-family: monospace;">
            <input type="text" name="value" placeholder="Valor da variável / senha" style="flex:1;">
            <button type="submit">Adicionar e Salvar</button>
        </form>
    </div>
</div>

<!-- Form oculto para ações individuais via JS -->
<form id="action-form" method="POST" style="display:none;">
    <input type="hidden" name="key" id="action-key">
    <input type="hidden" name="value" id="action-value">
</form>

<script>
let allHidden = false;

function togglePwd(id) {{
    const el = document.getElementById('val-' + id);
    el.type = el.type === 'password' ? 'text' : 'password';
}}

function toggleAll() {{
    allHidden = !allHidden;
    const inputs = document.querySelectorAll('.val-input');
    inputs.forEach(input => {{
        input.type = allHidden ? 'password' : 'text';
    }});
}}

function copyPwd(id) {{
    const el = document.getElementById('val-' + id);
    if (!el.value) return;
    navigator.clipboard.writeText(el.value).then(() => {{
        alert('Copiado para a área de transferência!');
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
    if (!confirm('Tem certeza que deseja excluir ' + keyName + ' do .env?')) return;
    const form = document.getElementById('action-form');
    form.action = '/delete';
    document.getElementById('action-key').value = keyName;
    form.submit();
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

        # Salva todas as senhas de uma única vez
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
                    self._redirect("/?msg=" + urllib.parse.quote("Todas as senhas foram atualizadas no .env com sucesso!"))
                else:
                    self._redirect("/?err=" + urllib.parse.quote("Nenhuma senha válida enviada."))
            except Exception as e:
                self._redirect("/?err=" + urllib.parse.quote(f"Erro ao salvar senhas: {e}"))
            return

        # Salva apenas uma variável específica
        if self.path in ("/save", "/save-single"):
            key = form.get("key", "").strip().replace("=", "")
            value = form.get("value", "").strip()
            if not key:
                self._redirect("/?err=" + urllib.parse.quote("O nome da chave não pode ser vazio."))
                return
            set_env_key(key, value)
            self._redirect("/?msg=" + urllib.parse.quote(f"Variável '{key}' salva no .env com sucesso!"))
            return

        # Remove uma variável do .env
        if self.path == "/delete":
            key = form.get("key", "").strip()
            if not delete_env_key(key):
                self._redirect("/?err=" + urllib.parse.quote(f"A chave '{key}' não pode ser excluída."))
                return
            self._redirect("/?msg=" + urllib.parse.quote(f"Variável '{key}' removida do .env!"))
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
