// Prediction page JavaScript
let pollutantChart;

document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('predictionForm');
    
    if (predictionForm) {
        predictionForm.addEventListener('submit', handlePrediction);
    }
});

async function handlePrediction(event) {
    event.preventDefault();
    
    const loadingIndicator = document.getElementById('predictionLoading');
    const resultsPlaceholder = document.getElementById('resultsPlaceholder');
    const predictionResults = document.getElementById('predictionResults');
    
    // Show loading
    loadingIndicator.classList.remove('hidden');
    resultsPlaceholder.classList.add('hidden');
    predictionResults.classList.add('hidden');
    
    // Get form data
    const formData = {
        so2: parseFloat(document.getElementById('so2').value),
        no2: parseFloat(document.getElementById('no2').value),
        rspm: parseFloat(document.getElementById('rspm').value),
        spm: parseFloat(document.getElementById('spm').value),
        year: parseInt(document.getElementById('year').value),
        month: parseInt(document.getElementById('month').value),
        state: document.getElementById('state').value,
        type: document.getElementById('type').value
    };
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
            showNotification('Prediction completed successfully!', 'success');
        } else {
            showNotification('Prediction failed: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error during prediction:', error);
        showNotification('Error during prediction. Please try again.', 'error');
    } finally {
        loadingIndicator.classList.add('hidden');
    }
}

function displayResults(data) {
    const predictionResults = document.getElementById('predictionResults');
    const resultsPlaceholder = document.getElementById('resultsPlaceholder');
    
    // Update PM2.5 value
    document.getElementById('pm25Value').textContent = data.pm2_5_prediction;
    
    // Update AQI badge
    const aqiBadge = document.getElementById('aqiBadge');
    const aqiCategory = document.getElementById('aqiCategory');
    aqiBadge.style.background = data.aqi_color;
    aqiCategory.textContent = data.aqi_category;
    
    // Update health impact
    document.getElementById('healthImpact').textContent = data.health_impact;
    
    // Update input summary
    document.getElementById('summSo2').textContent = data.input_data.so2 + ' μg/m³';
    document.getElementById('summNo2').textContent = data.input_data.no2 + ' μg/m³';
    document.getElementById('summRspm').textContent = data.input_data.rspm + ' μg/m³';
    document.getElementById('summSpm').textContent = data.input_data.spm + ' μg/m³';
    
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    document.getElementById('summDate').textContent = monthNames[data.input_data.month - 1] + ' ' + data.input_data.year;
    document.getElementById('summLocation').textContent = data.input_data.state + ' (' + data.input_data.type + ')';
    
    // Create pollutant chart
    createPollutantChart(data.input_data, data.pm2_5_prediction);
    
    // Show results
    resultsPlaceholder.classList.add('hidden');
    predictionResults.classList.remove('hidden');
    
    // Scroll to results
    predictionResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function createPollutantChart(inputData, pm25Prediction) {
    const ctx = document.getElementById('pollutantChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (pollutantChart) {
        pollutantChart.destroy();
    }
    
    pollutantChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['SO2', 'NO2', 'RSPM', 'SPM', 'PM2.5 (Predicted)'],
            datasets: [{
                data: [
                    inputData.so2,
                    inputData.no2,
                    inputData.rspm,
                    inputData.spm,
                    pm25Prediction
                ],
                backgroundColor: [
                    'rgba(255, 107, 107, 0.8)',
                    'rgba(78, 205, 196, 0.8)',
                    'rgba(69, 183, 209, 0.8)',
                    'rgba(255, 126, 0, 0.8)',
                    'rgba(152, 216, 200, 0.8)'
                ],
                borderColor: [
                    'rgba(255, 107, 107, 1)',
                    'rgba(78, 205, 196, 1)',
                    'rgba(69, 183, 209, 1)',
                    'rgba(255, 126, 0, 1)',
                    'rgba(152, 216, 200, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.toFixed(2) + ' μg/m³';
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function resetForm() {
    document.getElementById('predictionForm').reset();
    document.getElementById('predictionResults').classList.add('hidden');
    document.getElementById('resultsPlaceholder').classList.remove('hidden');
    
    // Destroy chart
    if (pollutantChart) {
        pollutantChart.destroy();
        pollutantChart = null;
    }
    
    // Scroll to form
    document.getElementById('predictionForm').scrollIntoView({ behavior: 'smooth' });
}
