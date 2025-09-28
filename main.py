# For the token
from typing import Final

# Connection with the API and for messaging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder, CallbackContext, CallbackQueryHandler
from telegram import Bot
from telegram.error import TelegramError

# For APIs calls
import requests

# To execute periodic functions
import schedule
import time

# For managing the bot
from dotenv import load_dotenv
import os


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    crypto_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Bitcoin", callback_data="BTC"), 
         InlineKeyboardButton(text="Ethereum", callback_data="ETH"),
         InlineKeyboardButton(text="XRP Ledger", callback_data="XRP")]
    ])

    if update.message:  # llamado desde /start
        await update.message.reply_text(
            f'Hello {update.message.chat.first_name}!\nThanks for choosing me as your crypto bot\n',
            reply_markup=crypto_keyboard
        )
    elif update.callback_query:  # llamado desde un botón
        await update.callback_query.message.reply_text(
            "Choose your crypto:",
            reply_markup=crypto_keyboard
        )
        
async def button_controller(update: Update, context: CallbackContext):
    global crypto_chosen, time_monitorize
    time_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="1 Hour", callback_data="1h"), 
         InlineKeyboardButton(text="12 Hour", callback_data="12h"),
         InlineKeyboardButton(text="1 Day", callback_data="1d")]
    ,
        [InlineKeyboardButton(text="7 Days", callback_data="7d"), 
         InlineKeyboardButton(text="30 Days", callback_data="30d"),
         InlineKeyboardButton(text="1 Year", callback_data="1y")]]
    )
    update.callback_query.answer()
    print(f'Button pressed: {update.callback_query.data}')
    
    if update.callback_query.data in ('BTC', 'ETH', 'XRP'):
        crypto_chosen = update.callback_query.data
        await update.callback_query.message.reply_text('*'*30+f'\nYou have chosen: {crypto_chosen}\nWhat '
        'period of time do you want to monitorize', reply_markup=time_keyboard)
    if update.callback_query.data in ('1h', '12h', '1d', '7d', '30d', '1y'):
        time_monitorize = update.callback_query.data
        
        price, variation = market_API_check(crypto_chosen, time_monitorize)
        await update.callback_query.message.reply_text(f'Results for {crypto_chosen} in {time_monitorize}: {price}$ with {variation}%')
        await start_command(update, context)

def market_API_check(crypto, period):
    # Mapeo de tickers a IDs de CoinGecko
    crypto_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "XRP": "ripple"
        # Puedes añadir más monedas aquí si quieres
    }

    if crypto not in crypto_map:
        raise ValueError(f"Crypto {crypto} no soportada")

    crypto_id = crypto_map[crypto]

    # Equivalencias de periodos
    period_map = {
        "1h": {"days": 1, "hours_back": 1},
        "12h": {"days": 1, "hours_back": 12},
        "1d": {"days": 1, "hours_back": 24},
        "7d": {"days": 7, "hours_back": None},
        "30d": {"days": 30, "hours_back": None},
        "1y": {"days": 365, "hours_back": None},
    }

    if period not in period_map:
        raise ValueError(f"Time period {period} is not supported")

    # Construir URL
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {"vs_currency": "usd", "days": period_map[period]["days"]}

    # Llamar a la API
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Error en la API: {response.status_code}, {response.text}")

    data = response.json()

    if "prices" not in data:
        raise ValueError(f"La API no devolvió precios. Respuesta: {data}")

    prices = data["prices"]

    # Precio actual = último
    current_price = prices[-1][1]

    # Precio anterior (depende del periodo)
    if period_map[period]["hours_back"]:
        hours_back = period_map[period]["hours_back"]
        target_timestamp = (time.time() - hours_back * 3600) * 1000  # en ms
        old_price = min(prices, key=lambda x: abs(x[0] - target_timestamp))[1]
    else:
        old_price = prices[0][1]

    # Variación porcentual
    change = (current_price/old_price - 1) * 100

    return round(current_price, 2), round(change, 2)





config = {}
with open("config.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        config[key] = value

TEL_TOKEN = config["TEL_TOKEN"]
TEL_NICK = config["TEL_NICK"]

application = ApplicationBuilder().token(TEL_TOKEN).build()
application.add_handler( CommandHandler("start", start_command) )
application.add_handler( CallbackQueryHandler(button_controller))
application.run_polling(allowed_updates=Update.ALL_TYPES)



