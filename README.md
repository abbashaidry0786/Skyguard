# India Air Quality Prediction

A web application that predicts PM2.5 levels and Air Quality Index (AQI) for locations in India based on various air pollutant measurements.

![Air Quality Prediction](https://media.istockphoto.com/id/1134364154/vector/environment-ecology-infographic-elements-risks-and-pollution-ecosystem.jpg?s=612x612&w=0&k=20&c=1ta5F_oWmXHgCEVbmgX_V-zgXJ38OXASEuI50PDRwsU=)

## Overview

This project provides a machine learning-based solution to predict PM2.5 levels in India using historical air quality data. The application features:

- **Air Quality Prediction**: Predict PM2.5 levels based on input parameters (SO2, NO2, RSPM, SPM)
- **AQI Classification**: Automatically categorize predictions into AQI categories with health impact information
- **Data Visualization**: Interactive charts and graphs to explore air quality trends
- **User-friendly Interface**: Clean, responsive web interface for easy interaction

## Features

- **Real-time Prediction**: Get instant PM2.5 predictions based on your input parameters
- **AQI Classification**: Results include AQI category, color coding, and health impact information
- **Interactive Visualizations**: Explore air quality data through interactive charts
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Backend**: Flask (Python)
- **Machine Learning**: Scikit-learn (Random Forest model)
- **Data Processing**: Pandas, NumPy
- **Frontend**: HTML, CSS, JavaScript
- **Visualization**: JavaScript charting libraries

## Installation

1. Clone the repository:
   ```
   Clone the repo or extract the given project file 
   go inside the project folder
   then open terminal with that project folder
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Prediction

1. Navigate to the "Prediction" page
2. Enter values for SO2, NO2, RSPM, SPM
3. Select the year, month, state, and area type
4. Click "Predict" to get the PM2.5 prediction and AQI category

### Visualization

1. Navigate to the "Visualization" page
2. Explore various charts showing air quality trends across India
3. Use filters to customize the visualization

## Project Structure

```
├── app.py                                  # Main Flask application
├── data.csv                                # Dataset for training and visualization
├── feature_info.pkl                        # Feature information for the model
├── india_air_quality_model_random_forest.pkl  # Trained Random Forest model
├── requirements.txt                        # Project dependencies
├── scaler.pkl                              # Feature scaler for preprocessing
├── static/                                 # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── prediction.js
│       ├── script.js
│       └── visualization.js
└── templates/                              # HTML templates
    ├── about.html
    ├── index.html
    ├── prediction.html
    └── visualization.html
```

## Model Information

The prediction model is built using Random Forest Regression trained on historical air quality data from various locations in India. The model takes the following features as input:

- SO2 (Sulfur Dioxide) levels
- NO2 (Nitrogen Dioxide) levels
- RSPM (Respirable Suspended Particulate Matter)
- SPM (Suspended Particulate Matter)
- Year and Month
- State and Area Type (encoded)

## Air Quality Index (AQI) Categories

| PM2.5 Range | AQI Category | Health Impact |
|-------------|--------------|---------------|
| ≤ 30        | Good         | Air quality is satisfactory, and air pollution poses little or no risk |
| 31-60       | Satisfactory | Air quality is acceptable. However, there may be a risk for some people |
| 61-90       | Moderate     | Members of sensitive groups may experience health effects |
| 91-120      | Poor         | Health alert: The risk of health effects is increased for everyone |
| 121-250     | Very Poor    | Health warning of emergency conditions: everyone is more likely to be affected |
| > 250       | Severe       | Health alert: Everyone may experience serious health effects |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Data source: Central Pollution Control Board (CPCB), India
- Special thanks to all contributors who helped in developing this project
