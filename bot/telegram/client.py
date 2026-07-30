from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

import datetime as dt

from telegram.ext import ContextTypes as _ContextTypes

from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from bot.telegram.handler import handle_message
from core.overview import build_overview
from core.news_monitor import check_watchlist_news
from storage.settings import get_news_alert_enabled, set_news_alert_enabled
from utils.logger import logger


class TelegramService:

    def get_user(self, update: Update):
        return {
            "id": update.effective_user.id,
            "name": update.effective_user.full_name,
            "username": update.effective_user.username or "",
        }

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👋 Welcome to Trading Assistant\n\n"
            "Type /help to see available commands."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "/help\n"
            "/start\n"
            "/status\n"
            "/whoami\n"
            "/portfolio\n"
            "/connection\n"
            "/price SYMBOL\n"
            "/signal SYMBOL\n"
            "/watchlist\n"
            "/watchlist add SYMBOL\n"
            "/watchlist remove SYMBOL\n"
            "/market\n"
            "/overview\n"
            "/analyze SYMBOL\n"
            "/recap"
        )

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_message("/status")
        data = response["data"]

        await update.message.reply_text(
            f"🤖 {data['app']}\n\n"
            f"Status : Running ✅\n"
            f"Version : {data['version']}"
        )

    async def whoami(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_message("/whoami", user=self.get_user(update))
        data = response["data"]

        await update.message.reply_text(
            "👤 User Information\n\n"
            f"Name : {data['name']}\n"
            f"Username : @{data['username']}\n"
            f"User ID : {data['id']}"
        )

    async def portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_message("/portfolio", user=self.get_user(update))

        if not response["success"]:
            await update.message.reply_text(response["message"])
            return

        data = response["data"]

        await update.message.reply_text(
            "📈 Portfolio\n\n"
            f"Broker : {data['broker']}\n"
            f"Connected : {data['connected']}"
        )

    async def connection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_message("/connection", user=self.get_user(update))

        if not response["success"]:
            await update.message.reply_text(response["message"])
            return

        data = response["data"]
        status = "Connected ✅" if data["connected"] else "Disconnected ❌"

        await update.message.reply_text(
            "🔌 IBKR Connection\n\n"
            f"Broker : {data['broker']}\n"
            f"Status : {status}"
        )

    async def price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage:\n/price SYMBOL")
            return

        response = handle_message(f"/price {context.args[0].upper()}")

        if not response["success"]:
            await update.message.reply_text(response["message"])
            return

        data = response["data"]

        await update.message.reply_text(
            f"💲 {data['symbol']}\n\n"
            f"Current : {data['price']}\n"
            f"Open : {data['open']}\n"
            f"High : {data['high']}\n"
            f"Low : {data['low']}\n"
            f"Previous Close : {data['previous_close']}"
        )

    async def market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_message("/market")

        if not response["success"]:
            await update.message.reply_text(response["message"])
            return

        prices = response["data"]["prices"]
        is_open = response["data"].get("is_open", False)

        text = "🌍 US Market\n\n"
        text += "```\n"

        names = {
            "SPY": "S&P 500",
            "QQQ": "Nasdaq",
            "DIA": "Dow Jones",
        }

        for item in prices:
            price = item["price"]
            previous = item["previous_close"]

            change = (price - previous) / previous * 100

            dot = "🟢" if change >= 0 else "🔴"
            sign = "+" if change >= 0 else ""

            text += (
                f"{dot} "
                f"{names.get(item['symbol'], item['symbol']):<10} "
                f"{sign}{change:.2f}%\n"
            )

        text += "```\n\n"

        status_dot = "🟢" if is_open else "🔴"
        status_label = "OPEN" if is_open else "CLOSED"

        text += f"Market Status:\n{status_dot} {status_label}"

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
        )

    async def signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage:\n/signal SYMBOL")
            return

        response = handle_message(f"/signal {context.args[0].upper()}")

        if not response["success"]:
            await update.message.reply_text(response["message"])
            return

        data = response["data"]

        text = f"📐 {data['symbol']}\n\n"
        text += f"Stage : {data['stage_label']}\n\n"

        for label, passed in data["checks"]:
            mark = "✔" if passed else "✖"
            text += f"{mark} {label}\n"

        if not data["checks"]:
            text += "No price action setup detected.\n"

        text += "\n"
        text += "```\n"
        text += f"Close        : {data['close']}\n"
        text += f"RSI(14)      : {data['rsi']}\n"
        text += f"RSI EMA9     : {data['rsi_ema9']}\n"
        text += f"MACD         : {data['macd']}\n"
        text += f"MACD Signal  : {data['macd_signal']}\n"
        text += f"MACD Hist    : {data['macd_histogram']}\n"
        text += "```"

        await update.message.reply_text(text, parse_mode="Markdown")

    async def forextest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage:\n/forextest SYMBOL [timeframe]")
            return

        symbol = context.args[0]
        timeframe = context.args[1] if len(context.args) > 1 else "D"

        command = f"/forextest {symbol} {timeframe}"
        response = handle_message(command)

        if not response["success"]:
            await update.message.reply_text(response["message"])
            return

        data = response["data"]
        candles = data["candles"]

        text = f"📐 {data['symbol']} ({data['interval']})\n\n"
        text += f"Total candles received: {len(candles)}\n\n"
        text += "Last 3 candles:\n"
        text += "```\n"

        for candle in candles[-3:]:
            text += f"{candle}\n"

        text += "```"

        await update.message.reply_text(text, parse_mode="Markdown")

    async def recap(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_message("/recap")

        if not response["success"]:
            await update.message.reply_text(response["message"])
            return

        data = response["data"]

        if not data["has_data"]:
            await update.message.reply_text(
                "📊 No signal history yet.\n"
                "Check back after a few days of daily overviews."
            )
            return

        text = f"📊 Weekly Recap (last {data['days_back']} days)\n\n"

        for s in data["symbols"]:
            text += f"*{s['symbol']}*\n"
            if s["buy_count"]:
                text += f"  🟢 BUY signals: {s['buy_count']}\n"
            if s["sell_count"]:
                text += f"  🔴 SELL signals: {s['sell_count']}\n"
            text += f"  First: {s['first_direction']} @ ${s['first_price']} ({s['first_date']})\n"
            if s["first_date"] != s["last_date"]:
                text += f"  Latest: {s['last_direction']} @ ${s['last_price']} ({s['last_date']})\n"
            text += "\n"

        await update.message.reply_text(text, parse_mode="Markdown")

    async def overview(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = self._build_overview_text("📊 Overview")
        await update.message.reply_text(text, parse_mode="Markdown")

    async def newsalert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            current = "ON" if get_news_alert_enabled() else "OFF"
            await update.message.reply_text(
                f"News alert is currently: {current}\n\n"
                "Usage:\n/newsalert on\n/newsalert off"
            )
            return

        arg = context.args[0].lower()

        if arg == "on":
            set_news_alert_enabled(True)
            await update.message.reply_text("✅ Automatic news alerts turned ON.")
        elif arg == "off":
            set_news_alert_enabled(False)
            await update.message.reply_text("🔕 Automatic news alerts turned OFF.")
        else:
            await update.message.reply_text("Usage:\n/newsalert on\n/newsalert off")

    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage:\n/analyze SYMBOL")
            return

        await update.message.reply_text("🔍 Analyzing, please wait...")

        response = handle_message(f"/analyze {context.args[0].upper()}")

        if not response["success"]:
            await update.message.reply_text(response["message"])
            return

        data = response["data"]

        text = f"📊 {data['symbol']} Analysis\n\n"

        text += f"💲 Price: ${data['price']} ({data['change_pct']:+.2f}%)\n"

        if data["position_pct"] is not None:
            text += f"📍 52-Week Position: {data['position_pct']}% of range\n"
        if data.get("recent_position_pct") is not None:
            text += f"📍 10-Day Position: {data['recent_position_pct']}% of range\n"
            if data.get("recent_low") and data.get("recent_high"):
                text += f"   Key Levels: ${data['recent_low']} - ${data['recent_high']}\n"

        text += f"\n📈 Technical\n{data['stage_label']}\n"

        text += f"\n📰 News\n{data['news_summary']}"
        if data["news_counts"]:
            pos, neu, neg = data["news_counts"]
            text += f" ({pos} Positive, {neu} Neutral, {neg} Negative)"
        text += "\n"

        text += f"\n🏢 Company\n"
        text += f"Market Cap : {data['market_cap']}\n"
        text += f"P/E Ratio  : {data['pe_ratio']}\n"
        text += f"EPS        : {data['eps']}\n"
        if data["dividend_yield"]:
            text += f"Dividend   : {data['dividend_yield']}%\n"

        text += f"\n📊 Trend\n{data['trend']}\n"

        text += f"\n⚠ Risk\n{data['risk']}\n"

        text += f"\n📝 AI Summary\n{data['ai_summary']}"

        await update.message.reply_text(text)

    def _format_watchlist_line(self, item):
        symbol = item.get("symbol", "?")
        price = item.get("price")
        previous_close = item.get("previous_close")

        if price is None:
            return f"⚪ {symbol}"

        if previous_close:
            change_pct = (price - previous_close) / previous_close * 100
            dot = "🟢" if change_pct >= 0 else "🔴"
            sign = "+" if change_pct >= 0 else ""
            change_str = f"{sign}{change_pct:.2f}%"
        else:
            dot = "⚪"
            change_str = "N/A"

        return f"{dot} {symbol:<6} ${price:<9.2f} {change_str}"

    async def watchlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args if context.args else ["list"]
        command = "/watchlist " + " ".join(args)

        response = handle_message(command)

        if not response["success"]:
            await update.message.reply_text(response["message"])
            return

        prices = response["data"].get("prices")

        if prices is None:
            symbols = response["data"].get("watchlist", [])
            if not symbols:
                await update.message.reply_text("📋 Watchlist is empty.")
                return
            text = "📋 Watchlist\n\n"
            for symbol in symbols:
                text += f"• {symbol}\n"
            await update.message.reply_text(text)
            return

        if not prices:
            await update.message.reply_text("📋 Watchlist is empty.")
            return

        text = "📋 Watchlist\n\n"
        text += "```\n"

        for item in prices:
            text += self._format_watchlist_line(item) + "\n"

        text += "```\n\n"

        now_uae = datetime.now(ZoneInfo("Asia/Dubai"))
        time_str = now_uae.strftime("%I:%M %p UAE").lstrip("0")

        text += f"Last Updated:\n{time_str}"

        await update.message.reply_text(text, parse_mode="Markdown")

    def _build_overview_text(self, title):
        result = build_overview()
        data = result["data"]

        text = f"{title}\n\n"

        market_prices = data["market"]
        if market_prices:
            names = {"SPY": "S&P 500", "QQQ": "Nasdaq", "DIA": "Dow Jones"}
            parts = []
            for item in market_prices:
                price = item.get("price")
                previous = item.get("previous_close")
                if price and previous:
                    change = (price - previous) / previous * 100
                    sign = "+" if change >= 0 else ""
                    parts.append(f"{names.get(item['symbol'], item['symbol'])} {sign}{change:.2f}%")
            if parts:
                text += "🌍 " + " | ".join(parts) + "\n\n"

        text += "📋 Watchlist\n```\n"

        for item in data["watchlist"]:
            marker = " 🔔" if item["changed"] else ""
            text += f"{item['symbol']:<6} {item['stage_label']}{marker}\n"

        text += "```"

        return text

    async def _send_overview(self, context, title):
        text = self._build_overview_text(title)
        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            parse_mode="Markdown",
        )

    async def pre_market_overview(self, context: _ContextTypes.DEFAULT_TYPE):
        await self._send_overview(context, "🌅 Pre-Market Overview")

    async def post_market_overview(self, context: _ContextTypes.DEFAULT_TYPE):
        await self._send_overview(context, "🌙 Post-Market Overview")

    async def news_check_job(self, context: _ContextTypes.DEFAULT_TYPE):
        if not get_news_alert_enabled():
            return

        result = await check_watchlist_news()

        if not result["success"]:
            return

        alerts = result["data"]["alerts"]

        if not alerts:
            return

        for alert in alerts:
            text = (
                f"📰 {alert['symbol']} News Alert\n\n"
                f"{alert['headline']}\n\n"
                f"{alert['analysis']}"
            )
            await context.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=text,
            )

    def start(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.warning("Telegram token not configured.")
            return

        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("status", self.status))
        app.add_handler(CommandHandler("whoami", self.whoami))
        app.add_handler(CommandHandler("portfolio", self.portfolio))
        app.add_handler(CommandHandler("connection", self.connection))
        app.add_handler(CommandHandler("price", self.price))
        app.add_handler(CommandHandler("watchlist", self.watchlist))
        app.add_handler(CommandHandler("market", self.market))
        app.add_handler(CommandHandler("signal", self.signal))
        app.add_handler(CommandHandler("overview", self.overview))
        app.add_handler(CommandHandler("newsalert", self.newsalert))
        app.add_handler(CommandHandler("analyze", self.analyze))
        app.add_handler(CommandHandler("recap", self.recap))
        app.add_handler(CommandHandler("forextest", self.forextest))

        app.job_queue.run_daily(
            self.pre_market_overview,
            time=dt.time(hour=15, minute=30, tzinfo=ZoneInfo("Asia/Dubai")),
        )

        app.job_queue.run_daily(
            self.post_market_overview,
            time=dt.time(hour=0, minute=30, tzinfo=ZoneInfo("Asia/Dubai")),
        )

        app.job_queue.run_repeating(
            self.news_check_job,
            interval=1200,
            first=60,
        )

        logger.info("Telegram bot is starting...")

        app.run_polling()
