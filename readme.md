# 🤖 BotDC — Bot Multifuncional para Discord

Bot completo para servidores de Discord desenvolvido em Python (`discord.py`), incluindo **player de música do YouTube**, **inteligência artificial para chat e voz (TTS)**, **desafios de maratonas de programação**, **jogos e utilitários de moderação**, além de um **painel web local na porta 8022** para gerenciar todas as chaves e senhas do `.env`.

---

## 🚀 Funcionalidades

### 🎵 Sistema de Música (YouTube)
* `/play <busca ou link>` — Busca no YouTube, adiciona à fila e toca no canal de voz.
* `/pause` e `/resume` — Pausa e retoma a reprodução sem perder a posição.
* `/next` — Pula para a próxima faixa da fila.
* `/queue` — Exibe a fila atual com indicador da faixa em reprodução.
* `/stop` — Interrompe a reprodução, limpa a fila e desconecta o bot.
* **Controles Interativos:** Botões rápidos na mensagem do player (◀, ⏸, ▶, ⏭, ⏹, 💠).

### 🧠 Inteligência Artificial & Voz
* `/chat <pergunta>` — Responde perguntas com IA (EdenAI com fallback inteligente gratuito).
* `/voice <pergunta>` — Responde por voz diretamente no canal de áudio com TTS e gírias temáticas.
* `/conselho` — Gera conselhos aleatórios para o dia a dia.
* `/piada` — Gera piadas engraçadas e de programação.

### 💻 Desafios de Programação
* `/ex` — Gera desafios reais de maratonas de programação (Senac) e do Codewars formatados em Embeds com enunciados e nível de dificuldade.

### 🛡️ Utilitários & Moderação
* `/d <lados>` — Rola dados personalizados (ex: d6, d20, d100).
* `/img <termo>` — Gera imagens dinâmicas por IA baseadas na descrição informada.
* `/plagio <membro>` — Exibe o avatar em alta resolução de um usuário.
* `/punish <membro> <minutos>` — Prende o membro em canal disciplinar com sirene policial.
* `/free <membro>` — Liberta o membro e o retorna ao canal de origem.
* `/stroll <membro>` — Faz o membro passear temporariamente pelos canais de voz.
* `/commands` — Guia completo de todos os comandos disponíveis.

---

## 🔐 Gerenciador Local de Senhas (.env)

O projeto inclui uma interface web integrada para facilitar a visualização e alteração de todas as variáveis de ambiente sem precisar editar arquivos manualmente no servidor:

* **URL:** `http://localhost:8022`
* **Senha padrão:** `admin123` (configurável pela variável `MASTER_PASSWORD`)
* **Recursos do Painel:**
  * Todas as variáveis do `.env` já listadas e abertas para edição (`TOKEN`, `EDENAI_API_KEY`, etc.).
  * Botão **"Salvar Todas as Senhas"** para aplicar modificações de uma só vez.
  * Botão **"👁 Alternar Ocultar/Mostrar"** e cópia rápida de tokens.
  * Adicionar novas variáveis personalizadas ou remover chaves com 1 clique.
  * Atualização instantânea dos arquivos e do processo em tempo real.

---

## 🛠️ Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto (use `.env.example` como base):

```env
TOKEN=seu_discord_bot_token_aqui
EDENAI_API_KEY=sua_chave_edenai_aqui
MASTER_PASSWORD=sua_senha_do_painel_web
DONOS=seu_usuario_discord
GUILD_IDS=
STARTUP_CHANNEL_ID=
PRISAO_CHANNEL_ID=
```

| Variável | Descrição | Padrão / Obrigatório |
| :--- | :--- | :---: |
| `TOKEN` | Token do Bot gerado no Discord Developer Portal | **Obrigatório** |
| `MASTER_PASSWORD` | Senha para acessar o gerenciador em `http://localhost:8022` | `admin123` |
| `EDENAI_API_KEY` | Chave de API da EdenAI (possui fallback gratuito) | Opcional |
| `DONOS` | Nomes de usuário do Discord com permissão total | Opcional |
| `GUILD_IDS` | IDs dos servidores para registrar comandos slash | Opcional |
| `STARTUP_CHANNEL_ID` | Canal de texto para mensagem de inicialização | Opcional |
| `PRISAO_CHANNEL_ID` | Canal de voz de detenção do comando `/punish` | Opcional |

---

## 🐳 Como Executar com Docker (Recomendado)

### 1. Configure as variáveis
Copie o exemplo para criar seu `.env`:
```bash
cp .env.example .env
```

### 2. Inicie os containers
```bash
docker compose up -d --build
```

### 3. Gerenciamento
* Ver logs em tempo real:
  ```bash
  docker compose logs -f
  ```
* Parar o bot:
  ```bash
  docker compose down
  ```

O bot estará online no Discord e o painel de senhas acessível em `http://localhost:8022`.

---

## 💻 Execução Local (Sem Docker)

### Pré-requisitos
* **Python 3.11+**
* **FFmpeg** instalado e adicionado ao `PATH` do sistema

### Passo a passo
1. Clone o repositório e acesse a pasta:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd BotDC2_git
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Inicie o bot:
   ```bash
   python BotDC/main.py
   ```

---

## 📁 Estrutura do Projeto

```text
├── .env.example              # Modelo das variáveis de ambiente
├── docker-compose.yml        # Orquestração do container e portas
├── Dockerfile                # Imagem base com Python 3.11 e FFmpeg
├── requirements.txt          # Dependências do projeto
├── readme.md                 # Documentação do projeto
└── BotDC/
    ├── main.py               # Ponto de entrada, eventos e comandos Slash
    ├── password_manager.py   # Servidor web do gerenciador de senhas (porta 8022)
    ├── ias.py                # Integração com APIs de IA para texto e chat
    ├── exs.py                # Desafios de programação e conselhos
    ├── exs.json              # Banco de questões de maratona locais
    ├── text_to_speech.py     # Conversão de texto para áudio (gTTS)
    ├── Models/
    │   ├── Dj.py             # Gerenciamento de conexões de voz e fila de música
    │   ├── PlayList.py       # Estrutura de dados da playlist
    │   └── Embedders.py      # Estilização visual dos embeds e botões
    └── voices/               # Efeitos sonoros e áudios temporários
```

---

## 📦 Principais Tecnologias
* [discord.py](https://discordpy.readthedocs.io/) — Biblioteca para desenvolvimento de bots Discord.
* [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Extração e download de áudios do YouTube.
* [FFmpeg](https://ffmpeg.org/) — Processamento e streaming de áudio em tempo real.
* [gTTS](https://pypi.org/project/gTTS/) — Síntese de voz (Text-to-Speech).
* [httpx](https://www.python-httpx.org/) — Cliente HTTP assíncrono para consumo de APIs.
