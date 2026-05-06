from flask import Flask, render_template, request, jsonify
import joblib
import pickle
import pandas as pd
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)

# Paths
MODEL_PATH = 'india_air_quality_model_random_forest.pkl'
SCALER_PATH = 'scaler.pkl'
FEATURE_INFO_PATH = 'feature_info.pkl'

# Initialize
model = None
scaler = None
feature_info = None
df = None

# ================= LOAD MODEL =================
try:
    model = joblib.load(MODEL_PATH)
    print("✓ Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

try:
    scaler = joblib.load(SCALER_PATH)
    print("✓ Scaler loaded successfully!")
except Exception as e:
    print(f"Error loading scaler: {e}")

try:
    with open(FEATURE_INFO_PATH, 'rb') as f:
        feature_info = pickle.load(f)
    print("✓ Feature info loaded successfully!")
except Exception as e:
    print(f"Error loading feature info: {e}")
    feature_info = {
        'feature_columns': ['so2', 'no2', 'rspm', 'spm', 'year', 'month', 'state_encoded', 'type_encoded'],
        'target_column': 'pm2_5'
    }

# ================= LOAD DATA =================
# Fixed Google Drive direct download link
url = "https://drive.google.com/uc?export=download&id=1LMrWjjKy7U6gs0OuCGBMXAGXIJEqyDd4"

try:
    df = pd.read_csv("data.csv")   # 👈 IMPORTANT: local file

    print("DF SHAPE:", df.shape)
    print("COLUMNS:", df.columns)

    if df.shape[0] == 0:
        raise Exception("Empty dataset")

    # Clean data
    for col in ['so2', 'no2', 'rspm', 'spm', 'pm2_5']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col].fillna(df[col].median(), inplace=True)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    print("✅ Data loaded successfully!")

except Exception as e:
    print("❌ DATA ERROR:", e)
    df = None

# ================= ROUTES =================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')


# ================= PREDICTION API =================
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if model is None:
            return jsonify({'success': False, 'error': 'Model not loaded'}), 500

        data = request.get_json()

        so2 = float(data.get('so2', 0))
        no2 = float(data.get('no2', 0))
        rspm = float(data.get('rspm', 0))
        spm = float(data.get('spm', 0))
        year = int(data.get('year', datetime.now().year))
        month = int(data.get('month', datetime.now().month))

        input_data = {
            'so2': [so2],
            'no2': [no2],
            'rspm': [rspm],
            'spm': [spm],
            'year': [year],
            'month': [month]
        }

        if feature_info and 'feature_columns' in feature_info:
            if 'state_encoded' in feature_info['feature_columns']:
                input_data['state_encoded'] = [0]
            if 'type_encoded' in feature_info['feature_columns']:
                input_data['type_encoded'] = [0]

        input_df = pd.DataFrame(input_data)

        if feature_info:
            cols = [c for c in feature_info['feature_columns'] if c in input_df.columns]
            input_df = input_df[cols]

        prediction = model.predict(input_df)[0]

        if np.isnan(prediction) or np.isinf(prediction):
            prediction = 50.0

        aqi_category, aqi_color, health_impact = calculate_aqi_category(prediction)

        return jsonify({
            'success': True,
            'pm2_5_prediction': round(float(prediction), 2),
            'aqi_category': aqi_category,
            'aqi_color': aqi_color,
            'health_impact': health_impact
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ================= AQI LOGIC =================
def calculate_aqi_category(pm25_value):
    try:
        pm25_value = float(pm25_value)

        if pm25_value <= 30:
            return "Good", "#00e400", "Air quality is satisfactory"
        elif pm25_value <= 60:
            return "Satisfactory", "#ffff00", "Air quality is acceptable"
        elif pm25_value <= 90:
            return "Moderate", "#ff7e00", "Sensitive groups affected"
        elif pm25_value <= 120:
            return "Poor", "#ff0000", "Health risk increases"
        elif pm25_value <= 250:
            return "Very Poor", "#8f3f97", "Serious health effects"
        else:
            return "Severe", "#7e0023", "Emergency conditions"

    except:
        return "Unknown", "#999999", "Error"


# ================= VISUALIZATION API =================
@app.route('/api/visualization-data')
def get_visualization_data():
    try:
        if df is None or len(df) == 0:
            return jsonify({
                'success': True,
                'states': [],
                'so2': [],
                'no2': [],
                'pm2_5': []
            })

        print("Columns:", df.columns)

        # Required columns check
        for col in ['so2', 'no2', 'pm2_5']:
            if col not in df.columns:
                return jsonify({
                    'success': False,
                    'error': f'Missing column: {col}'
                })

        # If state exists
        if 'state' in df.columns:
            data = df.groupby('state')[['so2', 'no2', 'pm2_5']].mean().round(2)

            return jsonify({
                'success': True,
                'states': data.index.tolist()[:10],
                'so2': data['so2'].tolist()[:10],
                'no2': data['no2'].tolist()[:10],
                'pm2_5': data['pm2_5'].tolist()[:10]
            })

        # Fallback (no state column)
        return jsonify({
            'success': True,
            'states': ['Average'],
            'so2': [float(df['so2'].mean())],
            'no2': [float(df['no2'].mean())],
            'pm2_5': [float(df['pm2_5'].mean())]
        })

    except Exception as e:
        print("Error:", str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        })

    


# ================= RUN =================
if __name__ == '__main__':
    print("\n🚀 Starting Flask Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
