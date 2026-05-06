from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
import requests
from io import StringIO
from datetime import datetime
import os

app = Flask(__name__)

# ================= LOAD MODEL =================
try:
    model = joblib.load("india_air_quality_model_random_forest.pkl")
    print("✅ Model loaded")
except Exception as e:
    print("❌ Model error:", e)
    model = None

# ================= LOAD DATA (OPTIMIZED) =================
df = None

try:
    file_id = "1LMrWjjKy7U6gs0OuCGBMXAGXIJEqyDd4"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    response = requests.get(url)
    data = StringIO(response.text)

    # 🔥 LIMIT DATA (IMPORTANT FOR MEMORY)
    df = pd.read_csv(
        data,
        usecols=['so2','no2','rspm','spm','pm2_5','date'],
        nrows=50000
    )

    # Clean data
    for col in ['so2','no2','rspm','spm','pm2_5']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col].fillna(df[col].median(), inplace=True)

    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    print("✅ Data loaded:", df.shape)

except Exception as e:
    print("❌ Data error:", e)
    df = None

# ================= ROUTES =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

# ================= PREDICTION =================

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        input_data = pd.DataFrame({
            'so2': [float(data['so2'])],
            'no2': [float(data['no2'])],
            'rspm': [float(data['rspm'])],
            'spm': [float(data['spm'])],
            'year': [int(data.get('year', 2024))],
            'month': [int(data.get('month', 1))]
        })

        pred = model.predict(input_data)[0]

        return jsonify({
            "success": True,
            "pm2_5": round(float(pred), 2)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ================= VISUALIZATION =================

@app.route('/api/visualization-data')
def visualization_data():
    try:
        if df is None:
            raise Exception("No data")

        # Year column
        df['year'] = df['date'].dt.year

        yearly = df.groupby('year')[['so2','no2','pm2_5']].mean().dropna()

        return jsonify({
            "success": True,
            "years": yearly.index.tolist(),
            "so2": yearly['so2'].tolist(),
            "no2": yearly['no2'].tolist(),
            "pm2_5": yearly['pm2_5'].tolist()
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ================= RUN =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
