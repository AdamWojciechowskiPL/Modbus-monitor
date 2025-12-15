// WebSocket Connection
const socket = io();

// State
let connectionStatus = 'disconnected';
let signalsData = [];
let alertsData = [];
let charts = {};

// ============= CONNECTION EVENTS =============

socket.on('connect', () => {
    console.log('✓ Połączono z serwerem WebSocket');
    // updateConnectionStatus('connected'); // Will be done when modbus connects
});

socket.on('disconnect', () => {
    console.log('✗ Rozłączono z serwera');
    updateConnectionStatus('disconnected');
});

socket.on('connection_response', (data) => {
    console.log(`Connected clients: ${data.clients}`);
});

socket.on('modbus_connected', (data) => {
    console.log('✓ Modbus connected:', data.message);
    updateConnectionStatus('connected');
    showNotification('success', data.message);
    document.getElementById('btnConnect').style.display = 'none';
    document.getElementById('btnDisconnect').style.display = 'block';
});

socket.on('modbus_disconnected', (data) => {
    console.log('✗ Modbus disconnected');
    updateConnectionStatus('disconnected');
    showNotification('info', data.message);
    document.getElementById('btnConnect').style.display = 'block';
    document.getElementById('btnDisconnect').style.display = 'none';
});

socket.on('modbus_error', (data) => {
    console.error('Modbus error:', data.message);
    showNotification('danger', data.message);
});

// ============= SIGNALS UPDATES =============

socket.on('signals_update', (data) => {
    signalsData = data.signals;
    document.getElementById('readCount').textContent = data.readCount || 0;
    document.getElementById('errorCount').textContent = data.errorCount || 0;
    
    updateSignalsDisplay();
    updateChartsData(signalsData);
});

socket.on('alerts_update', (data) => {
    alertsData = data.alerts || [];
    updateAlertsDisplay();
});

socket.on('alert_rule_added', (data) => {
    showNotification('success', `Reguła dodana: ${data.rule.signal}`);
});

socket.on('alert_rule_removed', (data) => {
    showNotification('info', `Reguła usunięta: ${data.signal}`);
});

// ============= FUNCTIONS =============

function connectModbus() {
    const host = document.getElementById('inputHost').value;
    const port = document.getElementById('inputPort').value;
    const connectionType = document.getElementById('selectConnectionType').value;
    const startAddress = parseInt(document.getElementById('inputStartAddress').value) || 0;
    const registerType = document.getElementById('selectRegisterType').value;
    const count = parseInt(document.getElementById('inputCount').value) || 5;
    const interval = parseInt(document.getElementById('inputInterval').value) || 1000;
    
    if (!host) {
        showNotification('warning', 'Wpisz host/IP');
        return;
    }
    
    socket.emit('connect_modbus', {
        host: host,
        port: parseInt(port),
        connectionType: connectionType,
        start_address: startAddress,
        count: count,
        register_type: registerType,
        interval: interval
    });
}

function disconnectModbus() {
    socket.emit('disconnect_modbus');
}

function updateConnectionStatus(status) {
    connectionStatus = status;
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    
    if (!dot || !text) {
        console.warn('Status indicators not found in DOM');
        return;
    }
    
    if (status === 'connected') {
        dot.classList.remove('disconnected');
        text.textContent = 'Połączono';
    } else {
        dot.classList.add('disconnected');
        text.textContent = 'Brak połączenia';
    }
}

function updateSignalsDisplay() {
    const container = document.getElementById('signalsList');
    
    if (signalsData.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📡</div><p>Brak danych</p></div>';
        return;
    }
    
    let html = '';
    signalsData.forEach(signal => {
        const statusClass = signal.status === 'ok' ? 'badge-success' : 'badge-danger';
        const statusText = signal.status === 'ok' ? '✓ OK' : '✗ ERROR';
        const time = new Date(signal.lastUpdate).toLocaleTimeString('pl-PL', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        html += `
            <div class="card glass signal-item">
                <div class="signal-name">${signal.name}</div>
                <div class="signal-value">${typeof signal.value === 'number' ? signal.value.toFixed(2) : signal.value}</div>
                <div class="signal-meta">
                    <span style="color: var(--text-secondary); font-size: 0.8rem;">Address: ${signal.address}</span>
                    <span class="badge ${statusClass}">${statusText}</span>
                </div>
                <div class="signal-meta" style="padding-top: 0.75rem; border-top: 1px solid var(--glass-border); margin-top: 0.75rem;">
                    <span style="color: var(--text-secondary); font-size: 0.75rem;">${time}</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updateAlertsDisplay() {
    const container = document.getElementById('alertsList');
    
    if (alertsData.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">✔️</div><p>Brak aktywnych alertów</p></div>';
        return;
    }
    
    let html = '';
    alertsData.forEach(alert => {
        const severity = alert.severity || 'warning';
        const time = new Date(alert.timestamp).toLocaleTimeString('pl-PL');
        
        html += `
            <div class="alert-item ${severity === 'critical' ? 'danger' : severity}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">${alert.signal_name}</div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">${alert.alert_type}</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">${alert.message}</div>
                    </div>
                    <span class="badge ${severity === 'critical' ? 'danger' : severity}">${severity.toUpperCase()}</span>
                </div>
                <small style="color: var(--text-secondary); display: block; margin-top: 0.5rem;">${time}</small>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function addAlertRule() {
    const signalName = document.getElementById('alertSignalName').value;
    const alertType = document.getElementById('alertType').value;
    const threshold = document.getElementById('alertThreshold').value;
    const severity = document.getElementById('alertSeverity').value;
    
    if (!signalName || !threshold) {
        showNotification('warning', 'Uzupełnij wszystkie pola');
        return;
    }
    
    socket.emit('add_alert_rule', {
        signal_name: signalName,
        alert_type: alertType,
        threshold: threshold,
        severity: severity
    });
    
    // Wyczyść formularz
    document.getElementById('alertSignalName').value = '';
    document.getElementById('alertThreshold').value = '';
}

function showNotification(type, message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        padding: 1rem 1.5rem;
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid var(--glass-border);
        border-radius: 10px;
        color: var(--text-primary);
        z-index: 1000;
        animation: slideInRight 0.3s ease-out;
        font-weight: 500;
        max-width: 400px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    `;
    
    // Add icon based on type
    let icon = '✓';
    let accentColor = 'var(--success)';
    if (type === 'danger' || type === 'error') {
        icon = '✗';
        accentColor = 'var(--danger)';
    } else if (type === 'warning') {
        icon = '⚠';
        accentColor = 'var(--warning)';
    } else if (type === 'info') {
        icon = 'ℹ';
        accentColor = 'var(--accent)';
    }
    
    notification.innerHTML = `
        <div style="display: flex; gap: 0.75rem; align-items: start;">
            <span style="color: ${accentColor}; font-weight: bold; font-size: 1.2rem;">⚫</span>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(100px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideOutRight {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100px); }
    }
`;
document.head.appendChild(style);

// ============= CHARTS =============

function initCharts() {
    const signalsCtx = document.getElementById('chartSignals');
    const alertsCtx = document.getElementById('chartAlerts');
    
    if (!signalsCtx || !alertsCtx) {
        console.warn('Chart elements not found');
        return;
    }
    
    // Signals Chart
    charts.signals = new Chart(signalsCtx.getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Signal 1',
                    data: [],
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#06b6d4'
                },
                {
                    label: 'Signal 2',
                    data: [],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#8b5cf6'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: 'rgba(203, 213, 225, 0.7)',
                        font: { family: "'Inter', sans-serif" }
                    }
                },
                filler: {
                    propagate: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(100, 200, 220, 0.1)' },
                    ticks: { color: 'rgba(203, 213, 225, 0.5)' }
                },
                x: {
                    grid: { color: 'rgba(100, 200, 220, 0.1)' },
                    ticks: { color: 'rgba(203, 213, 225, 0.5)' }
                }
            }
        }
    });
    
    // Alerts Chart
    charts.alerts = new Chart(alertsCtx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'Warning', 'Info'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(6, 182, 212, 0.8)'
                ],
                borderColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#06b6d4'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'rgba(203, 213, 225, 0.7)',
                        font: { family: "'Inter', sans-serif" },
                        padding: 15
                    }
                }
            }
        }
    });
}

function updateChartsData(signals) {
    if (!charts.signals) return;
    
    const now = new Date().toLocaleTimeString('pl-PL', { 
        hour: '2-digit', 
        minute: '2-digit'
    });
    
    // Add to labels (keep last 20)
    charts.signals.data.labels.push(now);
    if (charts.signals.data.labels.length > 20) {
        charts.signals.data.labels.shift();
    }
    
    // Add signal data
    signals.slice(0, 2).forEach((signal, idx) => {
        if (!charts.signals.data.datasets[idx]) return;
        
        charts.signals.data.datasets[idx].data.push(signal.value);
        if (charts.signals.data.datasets[idx].data.length > 20) {
            charts.signals.data.datasets[idx].data.shift();
        }
    });
    
    charts.signals.update('none');
    
    // Update alerts chart
    const alertCounts = {
        critical: alertsData.filter(a => a.severity === 'critical').length,
        warning: alertsData.filter(a => a.severity === 'warning').length,
        info: alertsData.filter(a => a.severity === 'info').length
    };
    
    charts.alerts.data.datasets[0].data = [
        alertCounts.critical,
        alertCounts.warning,
        alertCounts.info
    ];
    charts.alerts.update('none');
}

// ============= INITIALIZATION =============

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        initCharts();
        socket.emit('request_signals_update');
    }, 500);
});
