# Crypto Bot Telegram

A Telegram bot that allows users to check cryptocurrency price changes over different time intervals using the free [CoinGecko API](https://www.coingecko.com/).

---

## Features

- Choose from three cryptocurrencies: **Bitcoin (BTC), Ethereum (ETH), XRP Ledger (XRP)**.
- Select time intervals: 1 hour, 12 hours, 1 day, 7 days, 30 days, and 1 year.
- Fetch the current price and calculate the percentage change for the selected period.
- User-friendly interface with Telegram inline buttons.
- Secure configuration using a `config.txt` file to store the bot token and other parameters.

---

## Technologies

- Python 3.12+
- [python-telegram-bot](https://python-telegram-bot.org/)
- Public [CoinGecko API](https://www.coingecko.com/api/documentations/v3)
- Standard Python modules: `requests`, `time`, `schedule`, `os`
- Secure token management via `config.txt`


