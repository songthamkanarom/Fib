# ==========================================
# Endpoint คำนวณ Fibonacci 61.8% (ย้อนหลัง 30 วัน)
# ==========================================
@app.route('/calculate-fibonacci', methods=['POST'])
def calculate_fibonacci():
    data = request.json
    symbols = data.get("symbols", [])
    results = {}
    
    for symbol in symbols:
        try:
            clean_symbol = symbol.split(":")[-1].strip().upper()
            ticker = yf.Ticker(clean_symbol)
            # ดึงข้อมูลย้อนหลัง แล้วตัดเอา 30 แท่งล่าสุด
            df = ticker.history(period="60d").tail(30)
            
            if df.empty or len(df) < 5:
                results[symbol] = {"fib618": "-"}
                continue
                
            high_prices, low_prices = df['High'], df['Low']
            max_high = high_prices.max()
            min_low = low_prices.min()
            
            # คำนวณ Fibonacci 61.8% Retracement
            fib_618_val = min_low + ((max_high - min_low) * 0.618)
            current_fib618 = round(float(fib_618_val), 2) if not pd.isna(fib_618_val) else "-"
            
            results[symbol] = {"fib618": current_fib618}
        except Exception:
            results[symbol] = {"fib618": "-"}
            
    return jsonify({"status": "success", "data": results})
