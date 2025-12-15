# dashboard_app.py - Flask app z WebSocket real-time dashboard

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit, send
from datetime import datetime
import json
import threading
import time

from modbus_client import ModbusClientManager
from modbus_database import ModbusDatabase
from modbus_alerts import AlertsManager, AlertRule

app = Flask(__name__)
app.config['SECRET_KEY'] = 'modbus-monitor-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Managers
modbus_manager = ModbusClientManager()
database = ModbusDatabase(db_type='sqlite')
alerts_manager = AlertsManager(database=database)

# State
polling_active = False
poll_thread = None
connected_clients = 0

class ModbusDashboardServer:
    """WebSocket server dla dashboard"""
    
    def __init__(self):
        self.signals_data = []
        self.active_alerts = []
        self.connection_status = 'disconnected'
        self.read_count = 0
        self.error_count = 0
    
    def poll_signals(self, settings):
        """Polling thread"""
        global polling_active
        
        while polling_active:
            try:
                values = modbus_manager.read_registers(
                    address=settings.get('start_address', 0),
                    count=settings.get('count', 5),
                    register_type=settings.get('register_type', 'holding')
                )
                
                if values is not None:
                    self.signals_data = []
                    for i, value in enumerate(values):
                        signal = {
                            'id': i,
                            'address': settings.get('start_address', 0) + i,
                            'name': f'Sygnał {i + 1}',
                            'value': value,
                            'unit': '',
                            'status': 'ok',
                            'lastUpdate': datetime.now().isoformat()
                        }
                        self.signals_data.append(signal)
                        
                        # Sprawdzenie alertów
                        alerts_manager.check_signal(signal['name'], value, signal['status'])
                    
                    self.read_count += 1
                    self.active_alerts = alerts_manager.get_active_alerts()
                    
                    # Broadcast do wszystkich klientów
                    socketio.emit('signals_update', {
                        'signals': self.signals_data,
                        'readCount': self.read_count,
                        'errorCount': self.error_count,
                        'timestamp': datetime.now().isoformat()
                    }, broadcast=True)
                    
                    # Jeśli są alerty, wyślij je
                    if self.active_alerts:
                        socketio.emit('alerts_update', {
                            'alerts': self.active_alerts
                        }, broadcast=True)
                
                time.sleep(settings.get('interval', 1000) / 1000.0)
            
            except Exception as e:
                self.error_count += 1

dashboard_server = ModbusDashboardServer()

# ============= ROUTES =============

@app.route('/')
def index():
    """Dashboard main page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Get current status"""
    return jsonify({
        'connected': modbus_manager.is_connected,
        'signals': dashboard_server.signals_data,
        'readCount': dashboard_server.read_count,
        'errorCount': dashboard_server.error_count,
        'alerts': dashboard_server.active_alerts
    })

@app.route('/api/alerts')
def api_alerts():
    """Get alerts history"""
    hours = request.args.get('hours', 24, type=int)
    alerts = database.get_alerts(hours=hours)
    return jsonify([dict(a) if hasattr(a, 'keys') else a for a in alerts])

@app.route('/api/history/<signal_name>')
def api_history(signal_name):
    """Get signal history"""
    minutes = request.args.get('minutes', 60, type=int)
    history = database.get_signal_history(signal_name, minutes=minutes)
    return jsonify(history)

# ============= WEBSOCKET EVENTS =============

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    global connected_clients
    connected_clients += 1
    dashboard_server.connection_status = 'connected'
    
    emit('connection_response', {
        'status': 'connected',
        'clients': connected_clients,
        'timestamp': datetime.now().isoformat()
    })
    
    print(f"✓ Client connected. Total: {connected_clients}")

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    global connected_clients
    connected_clients -= 1
    
    if connected_clients == 0:
        dashboard_server.connection_status = 'disconnected'
    
    print(f"✗ Client disconnected. Total: {connected_clients}")

@socketio.on('connect_modbus')
def handle_connect_modbus(data):
    """Connect to Modbus device"""
    global polling_active, poll_thread
    
    host = data.get('host', '192.168.1.100')
    port = data.get('port', 502)
    connection_type = data.get('connectionType', 'tcp')
    
    success = modbus_manager.connect(
        host=host,
        port=port,
        connection_type=connection_type,
        timeout=5,
        unit_id=1
    )
    
    if success:
        dashboard_server.connection_status = 'connected'
        polling_active = True
        
        # Start polling thread
        poll_thread = threading.Thread(
            target=dashboard_server.poll_signals,
            args=(data,),
            daemon=True
        )
        poll_thread.start()
        
        emit('modbus_connected', {
            'status': 'ok',
            'message': f'Połączono z {host}:{port}',
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)
    else:
        emit('modbus_error', {
            'status': 'error',
            'message': 'Nie udało się połączyć'
        })

@socketio.on('disconnect_modbus')
def handle_disconnect_modbus():
    """Disconnect from Modbus"""
    global polling_active
    
    polling_active = False
    modbus_manager.disconnect()
    dashboard_server.connection_status = 'disconnected'
    
    emit('modbus_disconnected', {
        'status': 'ok',
        'message': 'Rozłączono',
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

@socketio.on('add_alert_rule')
def handle_add_alert_rule(data):
    """Add alert rule"""
    from modbus_alerts import AlertRule
    
    rule = AlertRule(
        signal_name=data.get('signal_name'),
        alert_type=data.get('alert_type'),
        threshold=float(data.get('threshold', 0)),
        severity=data.get('severity', 'warning'),
        enabled=True
    )
    
    alerts_manager.add_rule(rule)
    
    emit('alert_rule_added', {
        'rule': {
            'signal': data.get('signal_name'),
            'type': data.get('alert_type'),
            'threshold': data.get('threshold'),
            'severity': data.get('severity')
        }
    }, broadcast=True)

@socketio.on('remove_alert_rule')
def handle_remove_alert_rule(data):
    """Remove alert rule"""
    alerts_manager.remove_rule(data.get('signal_name'), data.get('alert_type'))
    
    emit('alert_rule_removed', {
        'signal': data.get('signal_name'),
        'type': data.get('alert_type')
    }, broadcast=True)

@socketio.on('request_signals_update')
def handle_request_signals_update():
    """Client requesting signals update"""
    emit('signals_update', {
        'signals': dashboard_server.signals_data,
        'readCount': dashboard_server.read_count,
        'errorCount': dashboard_server.error_count
    })

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# ============= MAIN =============

if __name__ == '__main__':
    print("="*70)
    print("🚀 Modbus Monitor - WebSocket Dashboard")
    print("="*70)
    print("📍 Otwórz: http://localhost:5000")
    print("="*70)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)