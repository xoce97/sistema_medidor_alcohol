// Gráfico de muestras de alcohol
function initChart() {
    if (!muestrasData || muestrasData.length === 0) return;
    
    const ctx = document.getElementById('alcoholChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: muestrasData.map(m => m.fecha),
            datasets: [{
                label: 'Nivel de Alcohol (ppm)',
                data: muestrasData.map(m => m.alcohol_ppm),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', initChart);