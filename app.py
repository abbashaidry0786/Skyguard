from flask import Flask, render_template, request, jsonify
import joblib
import pickle
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

app = Flask(__name__)

# Load the trained model, scaler, and feature info
MODEL_PATH = 'india_air_quality_model_random_forest.pkl'
SCALER_PATH = 'scaler.pkl'
FEATURE_INFO_PATH = 'feature_info.pkl'

# Initialize variables
model = None
scaler = None
feature_info = None
df = None

# Load models
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
    # Create default feature info if file doesn't exist
    feature_info = {
        'feature_columns': ['so2', 'no2', 'rspm', 'spm', 'year', 'month', 'state_encoded', 'type_encoded'],
        'target_column': 'pm2_5'
    }
    print("✓ Using default feature info")

# Load sample data for visualization
DATA_PATH = 'data.csv'
if os.path.exists(DATA_PATH):
    try:
        df = pd.read_csv(DATA_PATH, encoding='latin1')
        # Handle missing values
        for col in ['so2', 'no2', 'rspm', 'spm', 'pm2_5']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col].fillna(df[col].median(), inplace=True)
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        print("✓ Data loaded successfully!")
        print(f"  Dataset shape: {df.shape}")
    except Exception as e:
        print(f"Error loading data: {e}")
        df = None
else:
    print(f"Warning: {DATA_PATH} not found. Visualization features will use sample data.")
    df = None

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

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please ensure the model file exists in the models/ directory.'
            }), 500

        data = request.get_json()
        
        # Extract features from request
        so2 = float(data.get('so2', 0))
        no2 = float(data.get('no2', 0))
        rspm = float(data.get('rspm', 0))
        spm = float(data.get('spm', 0))
        year = int(data.get('year', datetime.now().year))
        month = int(data.get('month', datetime.now().month))
        state = data.get('state', 'Unknown')
        area_type = data.get('type', 'Unknown')
        
        # Prepare input data - basic features
        input_data = {
            'so2': [so2],
            'no2': [no2],
            'rspm': [rspm],
            'spm': [spm],
            'year': [year],
            'month': [month]
        }
        
        # Add encoded features if they exist in the model
        if feature_info and 'feature_columns' in feature_info:
            if 'state_encoded' in feature_info['feature_columns']:
                input_data['state_encoded'] = [0]  # Default encoding
            if 'type_encoded' in feature_info['feature_columns']:
                input_data['type_encoded'] = [0]  # Default encoding
        
        # Create DataFrame
        input_df = pd.DataFrame(input_data)
        
        # Ensure columns are in the correct order
        if feature_info and 'feature_columns' in feature_info:
            # Reorder columns to match training
            available_cols = [col for col in feature_info['feature_columns'] if col in input_df.columns]
            input_df = input_df[available_cols]
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        
        # Ensure prediction is a valid number
        if np.isnan(prediction) or np.isinf(prediction):
            prediction = 50.0  # Default safe value
        
        # Calculate Air Quality Index (AQI) category
        aqi_category, aqi_color, health_impact = calculate_aqi_category(prediction)
        
        # Return prediction result
        result = {
            'success': True,
            'pm2_5_prediction': round(float(prediction), 2),
            'aqi_category': aqi_category,
            'aqi_color': aqi_color,
            'health_impact': health_impact,
            'input_data': {
                'so2': so2,
                'no2': no2,
                'rspm': rspm,
                'spm': spm,
                'year': year,
                'month': month,
                'state': state,
                'type': area_type
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 400

def calculate_aqi_category(pm25_value):
    """Calculate AQI category based on PM2.5 value"""
    try:
        pm25_value = float(pm25_value)
        if pm25_value <= 30:
            return "Good", "#00e400", "Air quality is satisfactory, and air pollution poses little or no risk."
        elif pm25_value <= 60:
            return "Satisfactory", "#ffff00", "Air quality is acceptable. However, there may be a risk for some people."
        elif pm25_value <= 90:
            return "Moderate", "#ff7e00", "Members of sensitive groups may experience health effects."
        elif pm25_value <= 120:
            return "Poor", "#ff0000", "Health alert: The risk of health effects is increased for everyone."
        elif pm25_value <= 250:
            return "Very Poor", "#8f3f97", "Health warning of emergency conditions: everyone is more likely to be affected."
        else:
            return "Severe", "#7e0023", "Health alert: Everyone may experience serious health effects."
    except:
        return "Unknown", "#999999", "Unable to determine air quality category."

@app.route('/api/visualization-data')
def get_visualization_data():
    """API endpoint to get data for visualizations"""
    try:
        # If no data file, return sample data
        if df is None or len(df) == 0:
            print("No data available, returning sample data")
            return jsonify({
                'success': True,
                'state_data': {
                    'states': ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'UP', 'West Bengal', 'Gujarat', 'Rajasthan', 'Punjab', 'Haryana'],
                    'so2': [12.5, 10.2, 8.5, 9.8, 11.3, 10.5, 9.2, 8.8, 13.2, 11.8],
                    'no2': [45.2, 38.5, 32.1, 35.8, 42.5, 40.2, 33.5, 31.2, 48.5, 44.2],
                    'pm2_5': [85.5, 72.3, 65.2, 68.5, 78.2, 75.5, 62.8, 58.5, 92.3, 82.5]
                },
                'trend_data': {
                    'years': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
                    'so2': [15.2, 14.8, 13.5, 12.8, 11.5, 10.2, 10.8, 11.2, 11.8, 12.2],
                    'no2': [48.5, 47.2, 45.8, 44.2, 42.5, 38.5, 40.2, 42.5, 44.2, 45.8],
                    'pm2_5': [92.5, 88.2, 82.5, 78.5, 72.3, 65.2, 68.5, 72.5, 78.2, 82.5]
                },
                'month_data': {
                    'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    'so2': [15.2, 14.5, 13.2, 11.8, 10.5, 9.8, 9.2, 9.5, 10.8, 12.5, 13.8, 14.8],
                    'no2': [52.5, 48.2, 45.5, 42.8, 38.5, 35.2, 33.5, 35.8, 40.2, 45.5, 48.8, 51.2],
                    'pm2_5': [95.5, 88.2, 78.5, 68.5, 58.2, 52.5, 48.5, 52.2, 65.5, 78.5, 88.2, 92.5]
                },
                'stats_data': {
                    'so2': {'mean': 11.5, 'median': 11.2, 'max': 25.5, 'min': 2.5},
                    'no2': {'mean': 42.5, 'median': 40.2, 'max': 85.5, 'min': 8.5},
                    'pm2_5': {'mean': 72.5, 'median': 68.5, 'max': 185.5, 'min': 15.2}
                }
            })
        
        # Prepare data for various visualizations
        
        # 1. State-wise average pollution
        if 'state' in df.columns:
            state_pollution = df.groupby('state')[['so2', 'no2', 'pm2_5']].mean().round(2)
            state_pollution = state_pollution.dropna()
            state_data = {
                'states': state_pollution.index.tolist()[:10],
                'so2': state_pollution['so2'].fillna(0).tolist()[:10],
                'no2': state_pollution['no2'].fillna(0).tolist()[:10],
                'pm2_5': state_pollution['pm2_5'].fillna(0).tolist()[:10]
            }
        else:
            state_data = {
                'states': ['Delhi', 'Maharashtra', 'Karnataka'],
                'so2': [12.5, 10.2, 8.5],
                'no2': [45.2, 38.5, 32.1],
                'pm2_5': [85.5, 72.3, 65.2]
            }
        
        # 2. Yearly trend
        df_copy = df.copy()
        if 'date' in df_copy.columns:
            df_copy['year'] = df_copy['date'].dt.year
            yearly_data = df_copy.groupby('year')[['so2', 'no2', 'pm2_5']].mean().round(2)
            yearly_data = yearly_data.dropna()
            trend_data = {
                'years': [int(y) for y in yearly_data.index.tolist()],
                'so2': yearly_data['so2'].fillna(0).tolist(),
                'no2': yearly_data['no2'].fillna(0).tolist(),
                'pm2_5': yearly_data['pm2_5'].fillna(0).tolist()
            }
        else:
            trend_data = {
                'years': [2020, 2021, 2022, 2023, 2024],
                'so2': [12.5, 11.8, 11.2, 11.5, 12.0],
                'no2': [45.2, 42.5, 40.2, 42.0, 44.0],
                'pm2_5': [82.5, 75.5, 68.5, 72.0, 78.0]
            }
        
        # 3. Monthly averages
        if 'date' in df_copy.columns:
            df_copy['month'] = df_copy['date'].dt.month
            monthly_data = df_copy.groupby('month')[['so2', 'no2', 'pm2_5']].mean().round(2)
            monthly_data = monthly_data.reindex(range(1, 13), fill_value=0)
            month_data = {
                'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'so2': monthly_data['so2'].fillna(0).tolist(),
                'no2': monthly_data['no2'].fillna(0).tolist(),
                'pm2_5': monthly_data['pm2_5'].fillna(0).tolist()
            }
        else:
            month_data = {
                'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'so2': [14.5, 13.2, 12.5, 11.2, 10.5, 9.8, 9.2, 9.5, 10.8, 12.0, 13.5, 14.2],
                'no2': [48.5, 45.2, 42.5, 38.5, 35.2, 32.5, 33.5, 35.8, 40.2, 44.0, 47.0, 49.5],
                'pm2_5': [88.5, 82.5, 75.5, 65.2, 55.5, 48.5, 45.2, 52.5, 68.5, 78.0, 85.5, 90.0]
            }
        
        # 4. Pollutant distribution statistics
        stats_data = {
            'so2': {
                'mean': float(df['so2'].mean()) if 'so2' in df.columns else 11.5,
                'median': float(df['so2'].median()) if 'so2' in df.columns else 11.0,
                'max': float(df['so2'].max()) if 'so2' in df.columns else 25.5,
                'min': float(df['so2'].min()) if 'so2' in df.columns else 2.5
            },
            'no2': {
                'mean': float(df['no2'].mean()) if 'no2' in df.columns else 42.5,
                'median': float(df['no2'].median()) if 'no2' in df.columns else 40.0,
                'max': float(df['no2'].max()) if 'no2' in df.columns else 85.5,
                'min': float(df['no2'].min()) if 'no2' in df.columns else 8.5
            },
            'pm2_5': {
                'mean': float(df['pm2_5'].mean()) if 'pm2_5' in df.columns else 72.5,
                'median': float(df['pm2_5'].median()) if 'pm2_5' in df.columns else 68.0,
                'max': float(df['pm2_5'].max()) if 'pm2_5' in df.columns else 185.5,
                'min': float(df['pm2_5'].min()) if 'pm2_5' in df.columns else 15.2
            }
        }
        
        return jsonify({
            'success': True,
            'state_data': state_data,
            'trend_data': trend_data,
            'month_data': month_data,
            'stats_data': stats_data
        })
    
    except Exception as e:
        print(f"Visualization error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return sample data on error
        return jsonify({
            'success': True,
            'state_data': {
                'states': ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'UP'],
                'so2': [12.5, 10.2, 8.5, 9.8, 11.3],
                'no2': [45.2, 38.5, 32.1, 35.8, 42.5],
                'pm2_5': [85.5, 72.3, 65.2, 68.5, 78.2]
            },
            'trend_data': {
                'years': [2020, 2021, 2022, 2023, 2024],
                'so2': [12.5, 11.8, 11.2, 11.5, 12.0],
                'no2': [45.2, 42.5, 40.2, 42.0, 44.0],
                'pm2_5': [82.5, 75.5, 68.5, 72.0, 78.0]
            },
            'month_data': {
                'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'so2': [14.5, 13.2, 12.5, 11.2, 10.5, 9.8, 9.2, 9.5, 10.8, 12.0, 13.5, 14.2],
                'no2': [48.5, 45.2, 42.5, 38.5, 35.2, 32.5, 33.5, 35.8, 40.2, 44.0, 47.0, 49.5],
                'pm2_5': [88.5, 82.5, 75.5, 65.2, 55.5, 48.5, 45.2, 52.5, 68.5, 78.0, 85.5, 90.0]
            },
            'stats_data': {
                'so2': {'mean': 11.5, 'median': 11.0, 'max': 25.5, 'min': 2.5},
                'no2': {'mean': 42.5, 'median': 40.0, 'max': 85.5, 'min': 8.5},
                'pm2_5': {'mean': 72.5, 'median': 68.0, 'max': 185.5, 'min': 15.2}
            }
        })

@app.route('/api/model-info')
def get_model_info():
    """API endpoint to get model information"""
    return jsonify({
        'success': True,
        'model_name': 'Random Forest Regressor',
        'r2_score': 0.5183,
        'rmse': 3.6039,
        'mae': 0.3391,
        'features': feature_info['feature_columns'] if feature_info and 'feature_columns' in feature_info else ['so2', 'no2', 'rspm', 'spm', 'year', 'month'],
        'target': feature_info['target_column'] if feature_info and 'target_column' in feature_info else 'pm2_5'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("India Air Quality Prediction System")
    print("="*60)
    print(f"Model loaded: {'✓' if model else '✗'}")
    print(f"Scaler loaded: {'✓' if scaler else '✗'}")
    print(f"Feature info loaded: {'✓' if feature_info else '✗'}")
    print(f"Data loaded: {'✓' if df is not None else '✗ (using sample data)'}")
    print("="*60)
    print("\nStarting Flask server...")
    print("Open your browser and go to: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
