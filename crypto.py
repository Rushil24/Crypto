import requests
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime
from plyer import notification
from sklearn.linear_model import LinearRegression
import yagmail

# ✅ Email Configuration
EMAIL_SENDER = "rushilpajni@gmail.com"
EMAIL_PASSWORD = "Enter Your Code Here"
EMAIL_RECEIVER = "rushil20csu090@ncuindia.edu"

# ✅ Crypto Settings
CRYPTOCURRENCIES = ["bitcoin", "ethereum"]
LOG_FILE = "crypto_prices.json"

# ✅ Fetch real-time crypto prices from CoinGecko (No API Key Required)
def get_crypto_prices():
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(CRYPTOCURRENCIES)}&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching prices: {e}")
        return {}

# ✅ Log price data to a JSON file
def log_price_data(data):
    try:
        with open(LOG_FILE, "r") as file:
            history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        history = {}

    history[str(datetime.now())] = data  # Add new data with timestamp

    with open(LOG_FILE, "w") as file:
        json.dump(history, file, indent=4)

# ✅ AI/ML-Based Trend Prediction: Buy, Sell, Hold
def predict_trend(prices):
    if len(prices) < 5:
        return "Hold"

    df = pd.DataFrame(prices, columns=["price"])
    df["day"] = np.arange(len(df)).reshape(-1, 1)

    model = LinearRegression()
    model.fit(df[["day"]], df["price"])
    prediction = model.predict(np.array([[len(df)]]))[0]

    print(f"🔮 Predicted next price: {prediction:.2f}, Last price: {df['price'].iloc[-1]:.2f}")

    if prediction > df["price"].iloc[-1] * 1.002:  # 0.2% increase (More Sensitive)
        return "Buy"
    elif prediction < df["price"].iloc[-1] * 0.998:  # 0.2% decrease (More Sensitive)
        return "Sell"
    return "Hold"

# ✅ Moving Average for Trend Analysis
def moving_average(prices, window=3):
    if len(prices) < window:
        return "Hold"
    
    avg_past = np.mean(prices[-window-1:-1])
    avg_current = np.mean(prices[-window:])

    print(f"📊 Moving Averages - Past: {avg_past:.2f}, Current: {avg_current:.2f}")

    if avg_current > avg_past * 1.002:  # 0.2% increase
        return "Buy"
    elif avg_current < avg_past * 0.998:  # 0.2% decrease
        return "Sell"
    return "Hold"

# ✅ Send system notifications
def send_notification(title, message):
    try:
        print(f"🔔 Sending Notification: {title} - {message}")
        notification.notify(title=title, message=message, timeout=5)
    except Exception as e:
        print(f"❌ Notification Error: {e}")

# ✅ Send email alerts for trade actions
def send_email_alert(crypto, price, action):
    subject = f"🚀 {crypto.capitalize()} Trade Alert: {action}"
    body = f"The AI suggests: {action} {crypto} at ${price}!\n\nCheck your trading app for action."
    
    try:
        print(f"📧 Sending Email: {subject}")
        yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD)
        yag.send(to=EMAIL_RECEIVER, subject=subject, contents=body)
    except Exception as e:
        print(f"❌ Email Error: {e}")

# ✅ Store past prices for AI/ML
past_prices = {crypto: [] for crypto in CRYPTOCURRENCIES}

# ✅ Main loop for tracking
while True:
    prices = get_crypto_prices()
    if prices:
        log_price_data(prices)

        for crypto in CRYPTOCURRENCIES:
            price = prices[crypto]["usd"]
            print(f"💰 {crypto.capitalize()} Price: ${price}")

            # Store past prices for ML trend prediction
            past_prices[crypto].append(price)
            if len(past_prices[crypto]) > 20:
                past_prices[crypto].pop(0)

            # AI/ML Model Prediction
            trend_ml = predict_trend(past_prices[crypto])
            trend_ma = moving_average(past_prices[crypto])

            # Final Decision (Based on both AI Model + Moving Average)
            final_decision = "Hold"
            if trend_ml == "Buy" and trend_ma == "Buy":
                final_decision = "Buy"
            elif trend_ml == "Sell" and trend_ma == "Sell":
                final_decision = "Sell"

            print(f"🔍 AI Suggestion for {crypto}: {final_decision}")

            # **Debugging: Check if email should be triggered**
            if final_decision in ["Buy", "Sell"]:
                print(f"✅ Triggering email alert for {crypto} at price ${price} - Action: {final_decision}")
                send_notification("📊 Crypto Trade Alert!", f"{final_decision} {crypto} at ${price}")
                send_email_alert(crypto, price, final_decision)

    else:
        print("❌ Failed to fetch price data.")

    time.sleep(300)  # Check every 5 minutes

