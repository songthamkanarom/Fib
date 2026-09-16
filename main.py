import base64
import yfinance as yf
import pandas as pd
import ta
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/calculate-indicators', methods=['POST'])
def calculate_indicators():
    data = request.json
    symbols = data.get("symbols", [])
    
    results = {}
    for symbol in symbols:
        try:
            clean_symbol = symbol.split(":")[-1].strip().upper()
            ticker = yf.Ticker(clean_symbol)
            
            # ดึงข้อมูลย้อนหลัง 30 วันปฏิทิน (ได้ ~20 วันทำการ) หรือ 60 วันแล้วตัดเอา 30 แท่งล่าสุด
            df = ticker.history(period="60d").tail(30)
            
            if df.empty or len(df) < 15:
                results[symbol] = {"rsi": "-", "stoch": "-", "fib618": "-", "news": "-"}
                continue
                
            close_prices = df['Close']
            high_prices = df['High']
            low_prices = df['Low']
            
            # 📌 คำนวณ Fibonacci 61.8% Retracement (ย้อนหลัง 30 แท่ง)
            max_high = high_prices.max()
            min_low = low_prices.min()
            fib_618_val = min_low + ((max_high - min_low) * 0.618)
            current_fib618 = round(float(fib_618_val), 2) if not pd.isna(fib_618_val) else "-"
            
            # คำนวณ RSI (14)
            rsi_series = ta.momentum.rsi(close_prices, window=14)
            rsi_val = rsi_series.iloc[-1]
            current_rsi = round(float(rsi_val), 2) if not pd.isna(rsi_val) else "-"
            
            # คำนวณ Stochastic %K (14, 3)
            stoch_series = ta.momentum.stoch(high_prices, low_prices, close_prices, window=14, smooth_window=3)
            stoch_val = stoch_series.iloc[-1]
            current_stoch = round(float(stoch_val), 2) if not pd.isna(stoch_val) else "-"
            
            # ข่าวสาร/ลิงก์สำรอง
            fallback_link = f"https://finance.yahoo.com/quote/{clean_symbol}"
            hyperlinks = [f'HYPERLINK("{fallback_link}", "ภาพรวม {clean_symbol}")']
            news_formula = "=" + " & CHAR(10) & ".join(hyperlinks)
            
            results[symbol] = {
                "rsi": current_rsi,
                "stoch": current_stoch,
                "fib618": current_fib618, # 📌 ส่งค่า Fib 61.8% กลับไป
                "news": news_formula
            }
        except Exception as e:
            results[symbol] = {"rsi": "-", "stoch": "-", "fib618": "-", "news": "-"}
            
    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
