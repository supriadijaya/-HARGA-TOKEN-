import logging
import re
import asyncio
import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CMC_API_KEY = os.getenv("CMC_API_KEY")

# Setup logging
logging.basicConfig(level=logging.INFO)

# Ambil harga token dari CoinMarketCap
def get_token_price(symbol: str):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
    }
    params = {
        "symbol": symbol.upper(),
        "convert": "USD"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if "data" in data and symbol.upper() in data["data"]:
        return data["data"][symbol.upper()]["quote"]["USD"]["price"]
    return None

# Ambil kurs USD ke IDR
def get_usd_to_idr():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD")
        data = res.json()
        return data["rates"]["IDR"]
    except:
        return 15500  # fallback jika error

# Tangani pesan masuk
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()
    match = re.match(r"^(\d*\.?\d+)\s+([a-zA-Z]{2,10})$", message)

    if match:
        jumlah = float(match.group(1))
        symbol = match.group(2).upper()

        price_usd = get_token_price(symbol)
        if price_usd:
            kurs_idr = get_usd_to_idr()
            total_usd = price_usd * jumlah
            total_idr = total_usd * kurs_idr

            reply = (
                f"LIVE HARGA {symbol.upper()}\n\n"
                f"{jumlah} {symbol.upper()} = ${total_usd:,.4f} USDT\n"
                f"{jumlah} {symbol.upper()} = Rp{total_idr:,.0f} RUPIAH\n\n"
                f"==> Seller  @annisaazzahra123   ✔️\n"
                f"➡️ jual/beli coin ecer\n"
                f"➡️ jual star Telegram\n"
                f"➡️ jual telegram premium"
            )

            sent = await update.message.reply_text(reply)

            # Hapus pesan bot setelah 60 detik
            await asyncio.sleep(60)
            await context.bot.delete_message(chat_id=sent.chat_id, message_id=sent.message_id)

# Jalankan bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot jalan... Ketik: 1 bnb / 0.5 sol / 1 doge dsb")
app.run_polling()

