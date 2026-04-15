# Naver Stock News Telegram Monitor

Python project that polls the **Naver News Search API** for a configurable list of Korean stock names and sends **Telegram alerts** only for newly detected articles.

## Features

- Configurable stock watchlist in `config.yaml`
- Environment-variable based secrets (`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `OPENAI_API_KEY`)
- Polling loop with default interval of 60 seconds
- SQLite deduplication store for seen articles
- Persists `title`, `link`, `pubDate`, `stock name`, `first_seen_at`
- Telegram alerts only for newly found articles
- Optional AI conservative summary via OpenAI Responses API
- Retry logic for Naver/Telegram API calls
- Logging + basic error handling
- Windows-friendly quick start

## Project structure

- `main.py` - startup, config/env loading, dependency wiring
- `scheduler.py` - polling loop and alert workflow
- `naver_news.py` - Naver API client
- `telegram_sender.py` - Telegram API sender
- `dedup_store.py` - SQLite dedup + persistence
- `ai_summarizer.py` - optional OpenAI analysis formatter
- `config.yaml` - watchlist/poll settings

## 1) Prerequisites

- Python 3.10+
- Naver Developers app credentials for News Search API
- Telegram bot token + target chat ID
- (Optional) OpenAI API key when AI summarization is enabled

## 2) Install

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Windows (cmd)
.\.venv\Scripts\activate.bat
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 3) Configure stocks (`config.yaml`)

```yaml
stocks:
  - 삼성전자
  - SK하이닉스
  - LG에너지솔루션
poll_interval_seconds: 60
news_page_size: 20
ai_summarization:
  enabled: false
  model: gpt-4.1-mini
```

## 4) Set environment variables

### Windows PowerShell

```powershell
$env:NAVER_CLIENT_ID="your_id"
$env:NAVER_CLIENT_SECRET="your_secret"
$env:TELEGRAM_BOT_TOKEN="123456:ABCDEF..."
$env:TELEGRAM_CHAT_ID="123456789"
$env:OPENAI_API_KEY="sk-..."   # only required if ai_summarization.enabled=true
```

### Windows CMD

```cmd
set NAVER_CLIENT_ID=your_id
set NAVER_CLIENT_SECRET=your_secret
set TELEGRAM_BOT_TOKEN=123456:ABCDEF...
set TELEGRAM_CHAT_ID=123456789
set OPENAI_API_KEY=sk-...
```

### macOS/Linux

```bash
export NAVER_CLIENT_ID="your_id"
export NAVER_CLIENT_SECRET="your_secret"
export TELEGRAM_BOT_TOKEN="123456:ABCDEF..."
export TELEGRAM_CHAT_ID="123456789"
export OPENAI_API_KEY="sk-..."
```

> Tip: You can also store these in a local `.env` file. `python-dotenv` is loaded at startup.

## 5) Run

```bash
python main.py
```

The monitor will poll every 60 seconds by default and send Telegram alerts for newly inserted articles only.

## SQLite schema

Database file: `news_store.db`

Table `articles` stores:

- `stock_name`
- `title`
- `link`
- `pub_date`
- `first_seen_at` (UTC ISO-8601 timestamp)

Dedup key: `UNIQUE(stock_name, link)`

## Optional AI summarization output format

When `ai_summarization.enabled: true`, each alert may include:

1. stock name
2. sentiment: bullish / bearish / neutral
3. key catalyst in one sentence
4. short-term trading checkpoint
5. caution note

The prompt enforces conservative language and explicit uncertainty to avoid overconfident conclusions.

## Running as a long-lived background process

### Windows (recommended: Task Scheduler)

1. Create `run_monitor.bat`:

```bat
@echo off
cd /d C:\path\to\project
call .venv\Scripts\activate.bat
python main.py >> monitor.log 2>&1
```

2. Open **Task Scheduler** → **Create Task**
3. Trigger: At startup (or At log on)
4. Action: Start Program = path to `run_monitor.bat`
5. Enable **Restart on failure** in task settings

### Linux (systemd example)

```ini
[Unit]
Description=Naver Stock News Monitor
After=network.target

[Service]
WorkingDirectory=/opt/naver-news-monitor
ExecStart=/opt/naver-news-monitor/.venv/bin/python /opt/naver-news-monitor/main.py
Restart=always
RestartSec=5
Environment=NAVER_CLIENT_ID=...
Environment=NAVER_CLIENT_SECRET=...
Environment=TELEGRAM_BOT_TOKEN=...
Environment=TELEGRAM_CHAT_ID=...
Environment=OPENAI_API_KEY=...

[Install]
WantedBy=multi-user.target
```

## Notes

- This project is for alerting/monitoring, not investment advice.
- Headline-level AI summaries can be wrong; always verify with full article context and filings.
