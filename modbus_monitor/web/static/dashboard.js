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
    updateConnectionStatus('connected');
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
    
    // Pokaż badge z ilością alertów
    const alertCount = alertsData.length;
    if (alertCount > 0) {
        document.getElementById('alertCount').textContent = alertCount;
        document.getElementById('alertCount').style.display = 'inline-block';
    } else {
        document.getElementById('alertCount').style.display = 'none';
    }
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
    const badge = document.getElementById('connectionStatus');
    
    if (status === 'connected') {
        badge.innerHTML = '<span class="status-dot connected"></span><span>Połączono</span>';
        badge.classList.remove('status-disconnected');
        badge.classList.add('status-connected');
    } else {
        badge.innerHTML = '<span class="status-dot disconnected"></span><span>Brak połączenia</span>';
        badge.classList.remove('status-connected');
        badge.classList.add('status-disconnected');
    }
}

function updateSignalsDisplay() {
    const container = document.getElementById('signalsList');
    
    if (signalsData.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle"></i> Brak danych</div>';
        return;
    }
    
    let html = '';
    signalsData.forEach(signal => {
        const statusColor = signal.status === 'ok' ? '#22c55e' : '#ef4444';
        html += `
            <div class="signal-card">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <div class="signal-name">${signal.name}</div>
                        <div class="signal-value">${signal.value.toFixed(2)}</div>
                        <div class="signal-address">Adres: ${signal.address}</div>
                    </div>
                    <span class="badge" style="background: ${statusColor}; color: white;">
                        ${signal.status === 'ok' ? '✓ OK' : '✗ ERROR'}
                    </span>
                </div>
                <small class="text-muted">Aktualizacja: ${new Date(signal.lastUpdate).toLocaleTimeString('pl-PL')}</small>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updateAlertsDisplay() {
    const container = document.getElementById('alertsList');
    
    if (alertsData.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle"></i> Brak aktywnych alertów</div>';
        return;
    }
    
    let html = '';
    alertsData.forEach(alert => {
        const severityClass = alert.severity || 'warning';
        const time = new Date(alert.timestamp).toLocaleTimeString('pl-PL');
        
        html += `
            <div class="alert-item ${severityClass}">
                <div class="alert-severity ${severityClass}">
                    ${alert.severity.toUpperCase()}
                </div>
                <div><strong>${alert.signal_name}</strong> - ${alert.alert_type}</div>
                <div class="small text-muted">${alert.message}</div>
                <small class="text-muted">${time}</small>
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
    // Bootstrap toast
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" style="margin: 1rem;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert na top of container
    const container = document.querySelector('.container-lg');
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = alertHTML;
    container.insertBefore(tempDiv.firstChild, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) alert.remove();
    }, 5000);
}

// ============= CHARTS =============

function initCharts() {
    // Signals Chart
    const ctxSignals = document.getElementById('chartSignals').getContext('2d');
    charts.signals = new Chart(ctxSignals, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Sygnał 1',
                    data: [],
                    borderColor: '#208080',
                    backgroundColor: 'rgba(32, 128, 128, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Sygnał 2',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // Alerts Chart
    const ctxAlerts = document.getElementById('chartAlerts').getContext('2d');
    charts.alerts = new Chart(ctxAlerts, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'Warning', 'Info'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.5)',
                    'rgba(245, 158, 11, 0.5)',
                    'rgba(59, 130, 246, 0.5)'
                ],
                borderColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#3b82f6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateChartsData(signals) {
    if (!charts.signals) return;
    
    const now = new Date().toLocaleTimeString('pl-PL', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit'
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
    
    charts.signals.update('none'); // Update without animation for performance
    
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
    initCharts();
    
    // Request initial data
    socket.emit('request_signals_update');
});

// Keyboard shortcut: Ctrl+K = Focus connection
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        document.getElementById('inputHost').focus();
    }
});
