# ==========================================
# Endpoint คำนวณ Fibonacci 61.8% (ย้อนหลัง 30 วัน)
# ==========================================
import yfinance as yf
import pandas as pd
from flask import Flask, request, jsonify

# 📌 ประกาศตัวแปร app
app = Flask(__name__)

@app.route('/calculate-fibonacci', methods=['POST'])
def calculate_fibonacci():
    data = request.json
    symbols = data.get("symbols", [])
    results = {}
    
    for symbol in symbols:
        try:
            clean_symbol = str(symbol).split(":")[-1].strip().upper()
            ticker = yf.Ticker(clean_symbol)
            
            # ดึงข้อมูล 60 วัน และตัดเอา 30 แท่งล่าสุด
            df = ticker.history(period="60d")
            
            if df.empty or len(df) < 5:
                results[symbol] = {"fib618": "-"}
                continue
            
            # ดึง 30 แท่งราคาล่าสุด
            df_30 = df.tail(30)
            
            # 📌 แปลง Series เป็น NumPy values เพื่อป้องกันปัญหา Pandas Index/Data Type เพี้ยน
            high_vals = df_30['High'].to_numpy()
            low_vals = df_30['Low'].to_numpy()
            
            max_high = float(high_vals.max())
            min_low = float(low_vals.min())
            
            # คำนวณ Fibonacci 61.8%
            fib_val = min_low + ((max_high - min_low) * 0.618)
            
            results[symbol] = {"fib618": f"{fib_val:.2f}"}
            
        except Exception as e:
            print(f"Error Fib calculation for {symbol}: {str(e)}")
            results[symbol] = {"fib618": "-"}
            
    return jsonify({"status": "success", "data": results})
