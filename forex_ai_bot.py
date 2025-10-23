import os
import time
import requests
import telebot

# ================== تنظیمات اصلی ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))  # ثانیه
THRESHOLD = float(os.getenv("THRESHOLD", 0.5))  # درصد تغییر برای هشدار

bot = telebot.TeleBot(TOKEN)

# لیست جفت ارزها
symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"]

# ذخیره آخرین قیمت‌ها
prices = {}

# ارسال پیام شروع
bot.send_message(CHAT_ID, "🤖 ربات فعال شد و در حال مانیتور بازار است...")

# ================== توابع ==================
def get_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey=demo"
    try:
        res = requests.get(url).json()
        return float(res["price"])
    except:
        return None

def get_ma_rsi(symbol, period_ma=109, period_rsi=7):
    """MA109 و RSI7"""
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize={period_ma + period_rsi}&apikey=demo"
    try:
        data = requests.get(url).json()
        close_prices = [float(x['close']) for x in data['values']]
        if len(close_prices) < period_ma:
            return None, None
        ma = sum(close_prices[:period_ma])/period_ma
        # محاسبه RSI ساده
        gains = []
        losses = []
        for i in range(1, period_rsi+1):
            diff = close_prices[i-1] - close_prices[i]
            if diff >=0:
                losses.append(diff)
                gains.append(0)
            else:
                gains.append(abs(diff))
                losses.append(0)
        avg_gain = sum(gains)/period_rsi
        avg_loss = sum(losses)/period_rsi
        rsi = 100 - (100 / (1 + avg_gain/(avg_loss+1e-10)))  # جلوگیری از صفر
        return ma, rsi
    except:
        return None, None

# ================== حلقه اصلی ==================
while True:
    for sym in symbols:
        price = get_price(sym)
        if price is None:
            continue
        # محاسبه درصد تغییر
        last_price = prices.get(sym, price)
        change = (price - last_price)/last_price*100
        if abs(change) >= THRESHOLD:
            msg = f"⚠️ تغییر {THRESHOLD}% یا بیشتر در {sym}\n📈 قیمت: {price:.3f} ({change:+.2f}%)"
            bot.send_message(CHAT_ID, msg)
        prices[sym] = price

        # بررسی MA109 و RSI7
        ma, rsi = get_ma_rsi(sym)
        if ma and rsi:
            if price > ma and rsi > 70:
                bot.send_message(CHAT_ID, f"📊 هشدار SELL در {sym}\nقیمت بالای MA109 و RSI7={rsi:.1f}")
            elif price < ma and rsi < 30:
                bot.send_message(CHAT_ID, f"📊 هشدار BUY در {sym}\nقیمت پایین MA109 و RSI7={rsi:.1f}")
    time.sleep(INTERVAL)
