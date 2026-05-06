// Visualization page JavaScript
let stateChart, trendChart, monthChart, comparisonChart;

document.addEventListener('DOMContentLoaded', function() {
    loadVisualizationData();
});

async function loadVisualizationData() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    try {
        loadingIndicator.classList.remove('hidden');
        
        const response = await fetch('/api/visualization-data');
        const data = await response.json();
        
        if (data.success) {
            // Update statistics cards
            updateStatsCards(data.stats_data);
            
            // Create charts
            createStateChart(data.state_data);
            createTrendChart(data.trend_data);
            createMonthChart(data.month_data);
            createComparisonChart(data.stats_data);
            
            loadingIndicator.classList.add('hidden');
        } else {
            console.error('Failed to load data:', data.error);
            showNotification('Failed to load visualization data', 'error');
        }
    } catch (error) {
        console.error('Error loading visualization data:', error);
        showNotification('Error loading visualization data', 'error');
        loadingIndicator.classList.add('hidden');
    }
}

function updateStatsCards(stats) {
    document.getElementById('so2Mean').textContent = stats.so2.mean.toFixed(2);
    document.getElementById('so2Max').textContent = stats.so2.max.toFixed(2);
    
    document.getElementById('no2Mean').textContent = stats.no2.mean.toFixed(2);
    document.getElementById('no2Max').textContent = stats.no2.max.toFixed(2);
    
    document.getElementById('pm25Mean').textContent = stats.pm2_5.mean.toFixed(2);
    document.getElementById('pm25Max').textContent = stats.pm2_5.max.toFixed(2);
}

function createStateChart(data) {
    const ctx = document.getElementById('stateChart').getContext('2d');
    
    stateChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.states,
            datasets: [
                {
                    label: 'SO2 (μg/m³)',
                    data: data.so2,
                    backgroundColor: 'rgba(255, 107, 107, 0.7)',
                    borderColor: 'rgba(255, 107, 107, 1)',
                    borderWidth: 2
                },
                {
                    label: 'NO2 (μg/m³)',
                    data: data.no2,
                    backgroundColor: 'rgba(78, 205, 196, 0.7)',
                    borderColor: 'rgba(78, 205, 196, 1)',
                    borderWidth: 2
                },
                {
                    label: 'PM2.5 (μg/m³)',
                    data: data.pm2_5,
                    backgroundColor: 'rgba(69, 183, 209, 0.7)',
                    borderColor: 'rgba(69, 183, 209, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Concentration (μg/m³)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'States'
                    }
                }
            }
        }
    });
}

function createTrendChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.years,
            datasets: [
                {
                    label: 'SO2 (μg/m³)',
                    data: data.so2,
                    borderColor: 'rgba(255, 107, 107, 1)',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3
                },
                {
                    label: 'NO2 (μg/m³)',
                    data: data.no2,
                    borderColor: 'rgba(78, 205, 196, 1)',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3
                },
                {
                    label: 'PM2.5 (μg/m³)',
                    data: data.pm2_5,
                    borderColor: 'rgba(69, 183, 209, 1)',
                    backgroundColor: 'rgba(69, 183, 209, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Average Concentration (μg/m³)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    }
                }
            }
        }
    });
}

function createMonthChart(data) {
    const ctx = document.getElementById('monthChart').getContext('2d');
    
    monthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months,
            datasets: [
                {
                    label: 'SO2 (μg/m³)',
                    data: data.so2,
                    borderColor: 'rgba(255, 107, 107, 1)',
                    backgroundColor: 'rgba(255, 107, 107, 0.2)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'NO2 (μg/m³)',
                    data: data.no2,
                    borderColor: 'rgba(78, 205, 196, 1)',
                    backgroundColor: 'rgba(78, 205, 196, 0.2)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'PM2.5 (μg/m³)',
                    data: data.pm2_5,
                    borderColor: 'rgba(69, 183, 209, 1)',
                    backgroundColor: 'rgba(69, 183, 209, 0.2)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Average Concentration (μg/m³)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                }
            }
        }
    });
}

function createComparisonChart(stats) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    comparisonChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Mean', 'Median', 'Max', 'Min'],
            datasets: [
                {
                    label: 'SO2',
                    data: [stats.so2.mean, stats.so2.median, stats.so2.max / 10, stats.so2.min],
                    backgroundColor: 'rgba(255, 107, 107, 0.2)',
                    borderColor: 'rgba(255, 107, 107, 1)',
                    borderWidth: 2
                },
                {
                    label: 'NO2',
                    data: [stats.no2.mean, stats.no2.median, stats.no2.max / 10, stats.no2.min],
                    backgroundColor: 'rgba(78, 205, 196, 0.2)',
                    borderColor: 'rgba(78, 205, 196, 1)',
                    borderWidth: 2
                },
                {
                    label: 'PM2.5',
                    data: [stats.pm2_5.mean, stats.pm2_5.median, stats.pm2_5.max / 10, stats.pm2_5.min],
                    backgroundColor: 'rgba(69, 183, 209, 0.2)',
                    borderColor: 'rgba(69, 183, 209, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }
    });
}

