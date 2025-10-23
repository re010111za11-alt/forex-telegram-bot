import os
import time
import requests
import telebot

TOKEN = os.getenv(8478687425:AAEN3a1T1961ZVrkcikH8GRbbJcCU0ycHHo)
CHAT_ID = os.getenv(111310449)
INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))

bot = telebot.TeleBot(TOKEN)

symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"]

def get_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey=demo"
    try:
        res = requests.get(url).json()
        return float(res["price"])
    except:
        return None

prices = {s: get_price(s) for s in symbols}
bot.send_message(CHAT_ID, "🤖 ربات فعال شد و در حال مانیتور بازار است...")

while True:
    for sym in symbols:
        new_price = get_price(sym)
        if new_price and prices[sym]:
            change = (new_price - prices[sym]) / prices[sym] * 100
            if abs(change) > 0.5:
                msg = f"⚠️ تغییر بیش از 0.5% در {sym}\n📈 قیمت جدید: {new_price:.3f} ({change:+.2f}%)"
                bot.send_message(CHAT_ID, msg)
                prices[sym] = new_price
    time.sleep(INTERVAL)
