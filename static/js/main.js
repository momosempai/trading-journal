// Global variables for chart
let plChart;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadTrades();
    loadStats();
    initializeChart();
});

// Load trades and populate table
async function loadTrades() {
    const response = await fetch('/api/trades');
    const trades = await response.json();
    
    const tableBody = document.getElementById('tradesTable');
    tableBody.innerHTML = '';
    
    trades.forEach(trade => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(trade.date).toLocaleDateString()}</td>
            <td>${trade.market}</td>
            <td>${trade.setup || '-'}</td>
            <td>${trade.trade_type}</td>
            <td>$${trade.entry_price.toFixed(2)}</td>
            <td>${trade.exit_price ? '$' + trade.exit_price.toFixed(2) : '-'}</td>
            <td>${trade.position_size}</td>
            <td>${trade.risk_reward ? trade.risk_reward.toFixed(2) : '-'}</td>
            <td>${trade.pnl_amount ? '$' + trade.pnl_amount.toFixed(2) : '-'}</td>
            <td>${trade.trade_duration || '-'}</td>
            <td><span class="badge bg-${trade.status === 'OPEN' ? 'warning' : 'success'}">${trade.status}</span></td>
            <td>
                ${trade.status === 'OPEN' ? 
                    `<button class="btn btn-sm btn-outline-primary" onclick="showCloseTradeModal(${trade.id})">
                        Close Trade
                    </button>` : 
                    ''
                }
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Load and update statistics
async function loadStats() {
    const response = await fetch('/api/stats');
    const stats = await response.json();
    
    document.getElementById('totalTrades').textContent = stats.total_trades;
    document.getElementById('winRate').textContent = `${stats.win_rate.toFixed(1)}%`;
    document.getElementById('totalPL').textContent = `$${stats.total_pnl.toFixed(2)}`;
    document.getElementById('avgRR').textContent = stats.average_risk_reward.toFixed(2);
    
    // Update progress bars
    const executionQuality = document.getElementById('executionQuality');
    const tradeManagement = document.getElementById('tradeManagement');
    const psychology = document.getElementById('psychology');
    
    executionQuality.style.width = `${(stats.average_execution / 5) * 100}%`;
    executionQuality.textContent = stats.average_execution.toFixed(1);
    
    tradeManagement.style.width = `${(stats.average_management / 5) * 100}%`;
    tradeManagement.textContent = stats.average_management.toFixed(1);
    
    psychology.style.width = `${(stats.average_psychology / 5) * 100}%`;
    psychology.textContent = stats.average_psychology.toFixed(1);
    
    updateChart(stats);
}

// Initialize Chart.js
function initializeChart() {
    const ctx = document.getElementById('plChart').getContext('2d');
    plChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Cumulative P/L',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Profit/Loss Over Time'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Update chart with new data
function updateChart(stats) {
    // This is a simplified version. In a real application, you'd want to show the P/L progression over time
    if (plChart.data.labels.length === 0) {
        plChart.data.labels = ['Start', 'Current'];
        plChart.data.datasets[0].data = [0, stats.total_pnl];
        plChart.update();
    }
}

// Add new trade
async function addTrade() {
    const form = document.getElementById('addTradeForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/trades', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('addTradeModal')).hide();
            form.reset();
            await loadTrades();
            await loadStats();
        }
    } catch (error) {
        console.error('Error adding trade:', error);
    }
}

// Show close trade modal
function showCloseTradeModal(tradeId) {
    const form = document.getElementById('closeTradeForm');
    form.querySelector('[name="trade_id"]').value = tradeId;
    new bootstrap.Modal(document.getElementById('closeTradeModal')).show();
}

// Close trade
async function closeTrade() {
    const form = document.getElementById('closeTradeForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const tradeId = data.trade_id;
    
    try {
        const response = await fetch(`/api/trades/${tradeId}/close`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('closeTradeModal')).hide();
            form.reset();
            await loadTrades();
            await loadStats();
        }
    } catch (error) {
        console.error('Error closing trade:', error);
    }
}
