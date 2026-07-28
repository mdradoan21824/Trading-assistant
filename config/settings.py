import os

from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Finnhub
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

# OpenAI (Future)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# IBKR (Future)
IBKR_HOST = os.getenv("IBKR_HOST", "127.0.0.1")
IBKR_PORT = int(os.getenv("IBKR_PORT", "7497"))
IBKR_CLIENT_ID = int(os.getenv("IBKR_CLIENT_ID", "1"))

# Telegram alert recipient (your personal chat ID)
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "6123502479"))

# Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Groq AI (fallback/secondary AI provider)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
