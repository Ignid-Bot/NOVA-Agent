import os
import re
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from nova_engine import NovaEngine


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "nova-webhook")


if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN belum diset.")


engine = NovaEngine()


def parse_amount(text: str):
    s = (
        text.lower()
        .replace("rp", "")
        .replace("idr", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )

    m = re.search(
        r"(\d+(?:\.\d+)?)\s*(juta|jt|ribu|rb|k)?",
        s
    )

    if not m:
        return None

    value = float(m.group(1))
    unit = m.group(2)

    if unit in ("juta", "jt"):
        value *= 1_000_000
    elif unit in ("ribu", "rb", "k"):
        value *= 1_000

    return int(value)


def parse_text(text: str):
    t = text.strip()
    low = t.lower()

    amount = parse_amount(t)

    if amount is None:
        return None

    income_words = [
        "gaji",
        "bonus",
        "thr",
        "pendapatan",
        "penghasilan",
        "tambahan dari kerja",
    ]

    tx_type = (
        "Pendapatan"
        if any(word in low for word in income_words)
        else "Pengeluaran"
    )

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": tx_type,
        "description": t,
        "source": "Telegram",
        "amount": amount,
        "status": "FINAL",
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 NOVA aktif!\n\n"
        "Contoh transaksi:\n"
        "• jajan 50k\n"
        "• beli kabel cas 60k\n"
        "• gaji 5 juta\n"
        "• bonus 500k\n\n"
        "Kirim transaksi dan NOVA akan mencatatnya."
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "📖 Contoh penggunaan NOVA:\n\n"
        "jajan 50k\n"
        "beli pulsa 100k\n"
        "gaji 5 juta\n"
        "bonus 500k"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text or ""

    tx = parse_text(text)

    if not tx:
        await update.message.reply_text(
            "⚠️ NOVA belum memahami transaksi tersebut.\n\n"
            "Coba contoh:\n"
            "jajan 50k\n"
            "gaji 5 juta"
        )
        return

    result = engine.add_transaction(tx)

    await update.message.reply_text(result)


def main():

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    if not RENDER_EXTERNAL_URL:
        raise RuntimeError(
            "RENDER_EXTERNAL_URL belum tersedia."
        )

    webhook_url = (
        f"{RENDER_EXTERNAL_URL}/telegram/{WEBHOOK_SECRET}"
    )

    print("================================")
    print("NOVA Telegram Bot")
    print("Mode: Webhook")
    print(f"Port: {PORT}")
    print(f"Webhook: {webhook_url}")
    print("================================")

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=f"telegram/{WEBHOOK_SECRET}",
        webhook_url=webhook_url,
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
