import yfinance as yf
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/calculate-fibonacci', methods=['POST'])
def calculate_fibonacci():
    data = request.json
    symbols = data.get("symbols", [])
    results = {}
    
    for symbol in symbols:
        try:
            # 1. จัดการชื่อสัญลักษณ์หุ้น
            raw_symbol = str(symbol).strip()
            clean_symbol = raw_symbol.split(":")[-1].strip().upper()
            
            ticker = yf.Ticker(clean_symbol)
            
            # 2. ดึงข้อมูล 60 วัน
            df = ticker.history(period="60d")
            
            # ป้องกันปัญหา MultiIndex สำหรับหุ้นบางตัว
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # ลบแถวที่มี NaN และตัดเอา 30 แท่งล่าสุด
            df_clean = df.dropna(subset=['High', 'Low']).tail(30)
            
            if df_clean.empty or len(df_clean) < 5:
                results[symbol] = {"fib618": "-"}
                continue
            
            # 3. ดึงราคา High และ Low เป็น Float
            max_high = float(df_clean['High'].max())
            min_low = float(df_clean['Low'].min())
            
            # 4. คำนวณ Fib 61.8%
            fib_val = min_low + ((max_high - min_low) * 0.618)
            
            if pd.isna(fib_val):
                results[symbol] = {"fib618": "-"}
            else:
                results[symbol] = {"fib618": round(fib_val, 2)}
                
        except Exception as e:
            print(f"Error for {symbol}: {str(e)}")
            results[symbol] = {"fib618": "-"}
            
    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
