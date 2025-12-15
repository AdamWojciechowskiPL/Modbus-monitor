# dashboard_app.py - Flask app z WebSocket real-time dashboard

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, send
from datetime import datetime
import json
import threading
import time
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Relative imports from parent package
from ..modbus_client import ModbusClientManager
from ..modbus_database import ModbusDatabase
from ..modbus_alerts import AlertsManager, AlertRule

app = Flask(__name__,
            template_folder=str(Path(__file__).parent / 'templates'),
            static_folder=str(Path(__file__).parent / 'static'))
app.config['SECRET_KEY'] = 'modbus-monitor-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Managers
modbus_manager = ModbusClientManager()
database = ModbusDatabase(db_type='sqlite')
alerts_manager = AlertsManager(database=database)

# State
poll_thread = None
connected_clients = 0

class ModbusDashboardServer:
    """WebSocket server dla dashboard"""
    
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.signals_data = []
        self.active_alerts = []
        self.connection_status = 'disconnected'
        self.read_count = 0
        self.error_count = 0
        self.polling_active = False
    
    def broadcast_signals(self):
        """Send signals to all connected clients"""
        with self.app.app_context():
            self.socketio.emit('signals_update', {
                'signals': self.signals_data,
                'readCount': self.read_count,
                'errorCount': self.error_count,
                'timestamp': datetime.now().isoformat()
            }, to=None)  # Broadcast to all
    
    def broadcast_alerts(self):
        """Send alerts to all connected clients"""
        if self.active_alerts:
            with self.app.app_context():
                self.socketio.emit('alerts_update', {
                    'alerts': self.active_alerts
                }, to=None)  # Broadcast to all
    
    def poll_signals(self, settings):
        """Polling thread"""
        logger.info(f"Starting polling with settings: {settings}")
        
        poll_count = 0
        while self.polling_active:
            try:
                start_addr = settings.get('start_address', 0)
                count = settings.get('count', 5)
                reg_type = settings.get('register_type', 'holding')
                
                logger.debug(f"Poll #{poll_count}: Reading {count} {reg_type} registers from address {start_addr}")
                
                values = modbus_manager.read_registers(
                    address=start_addr,
                    count=count,
                    register_type=reg_type
                )
                
                logger.debug(f"Read result: {values}")
                
                if values is not None and len(values) > 0:
                    logger.info(f"Received {len(values)} values: {values[:5]}...")  # Log first 5 values
                    
                    self.signals_data = []
                    for i, value in enumerate(values):
                        try:
                            # Ensure value is float
                            float_value = float(value) if value is not None else 0.0
                        except (ValueError, TypeError):
                            logger.warning(f"Could not convert value {value} to float, using 0")
                            float_value = 0.0
                        
                        signal = {
                            'id': i,
                            'address': start_addr + i,
                            'name': f'Sygnał {i + 1}',
                            'value': float_value,
                            'unit': '',
                            'status': 'ok',
                            'lastUpdate': datetime.now().isoformat()
                        }
                        self.signals_data.append(signal)
                    
                    self.read_count += 1
                    logger.info(f"Processed {len(self.signals_data)} signals. Read count: {self.read_count}")
                    
                    # Check alerts
                    for signal in self.signals_data:
                        alerts_manager.check_signal(signal['name'], signal['value'], signal['status'])
                    
                    self.active_alerts = alerts_manager.get_active_alerts()
                    
                    # Broadcast signals
                    logger.debug(f"Broadcasting {len(self.signals_data)} signals")
                    self.broadcast_signals()
                    
                    # Broadcast alerts if any
                    if self.active_alerts:
                        logger.info(f"Broadcasting {len(self.active_alerts)} alerts")
                        self.broadcast_alerts()
                else:
                    self.error_count += 1
                    logger.error(f"No values returned from read_registers: {values}")
                
                poll_count += 1
                interval = settings.get('interval', 1000) / 1000.0
                logger.debug(f"Sleeping for {interval}s before next poll")
                time.sleep(interval)
            
            except Exception as e:
                self.error_count += 1
                logger.exception(f"Exception in polling: {e}")
                time.sleep(1)  # Wait before retry
        
        logger.info("Polling stopped")

dashboard_server = ModbusDashboardServer(app, socketio)

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
    
    logger.info(f"✓ Client connected. Total: {connected_clients}")
    
    emit('connection_response', {
        'status': 'connected',
        'clients': connected_clients,
        'timestamp': datetime.now().isoformat()
    })
    
    # Send current status to new client
    emit('signals_update', {
        'signals': dashboard_server.signals_data,
        'readCount': dashboard_server.read_count,
        'errorCount': dashboard_server.error_count
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    global connected_clients
    connected_clients -= 1
    
    if connected_clients == 0:
        dashboard_server.connection_status = 'disconnected'
    
    logger.info(f"✗ Client disconnected. Total: {connected_clients}")

@socketio.on('connect_modbus')
def handle_connect_modbus(data):
    """Connect to Modbus device"""
    global poll_thread
    
    host = data.get('host', '192.168.1.100')
    port = data.get('port', 502)
    connection_type = data.get('connectionType', 'tcp')
    
    logger.info(f"Connecting to {connection_type.upper()} {host}:{port}")
    logger.info(f"Settings: start_address={data.get('start_address')}, count={data.get('count')}, register_type={data.get('register_type')}, interval={data.get('interval')}ms")
    
    success = modbus_manager.connect(
        host=host,
        port=port,
        connection_type=connection_type,
        timeout=5,
        unit_id=1
    )
    
    if success:
        dashboard_server.connection_status = 'connected'
        dashboard_server.polling_active = True
        
        # Start polling thread
        poll_thread = threading.Thread(
            target=dashboard_server.poll_signals,
            args=(data,),
            daemon=True
        )
        poll_thread.start()
        
        with app.app_context():
            socketio.emit('modbus_connected', {
                'status': 'ok',
                'message': f'Połączono z {host}:{port}',
                'timestamp': datetime.now().isoformat()
            }, to=None)  # Broadcast to all
        
        logger.info(f"✓ Modbus connected successfully")
    else:
        logger.error("Failed to connect to Modbus")
        emit('modbus_error', {
            'status': 'error',
            'message': 'Nie udało się połączyć'
        })

@socketio.on('disconnect_modbus')
def handle_disconnect_modbus():
    """Disconnect from Modbus"""
    dashboard_server.polling_active = False
    modbus_manager.disconnect()
    dashboard_server.connection_status = 'disconnected'
    
    logger.info("Modbus disconnected")
    
    with app.app_context():
        socketio.emit('modbus_disconnected', {
            'status': 'ok',
            'message': 'Rozłączono',
            'timestamp': datetime.now().isoformat()
        }, to=None)  # Broadcast to all

@socketio.on('add_alert_rule')
def handle_add_alert_rule(data):
    """Add alert rule"""
    rule = AlertRule(
        signal_name=data.get('signal_name'),
        alert_type=data.get('alert_type'),
        threshold=float(data.get('threshold', 0)),
        severity=data.get('severity', 'warning'),
        enabled=True
    )
    
    alerts_manager.add_rule(rule)
    logger.info(f"Alert rule added: {data.get('signal_name')} {data.get('alert_type')} {data.get('threshold')}")
    
    with app.app_context():
        socketio.emit('alert_rule_added', {
            'rule': {
                'signal': data.get('signal_name'),
                'type': data.get('alert_type'),
                'threshold': data.get('threshold'),
                'severity': data.get('severity')
            }
        }, to=None)  # Broadcast to all

@socketio.on('remove_alert_rule')
def handle_remove_alert_rule(data):
    """Remove alert rule"""
    alerts_manager.remove_rule(data.get('signal_name'), data.get('alert_type'))
    logger.info(f"Alert rule removed: {data.get('signal_name')}")
    
    with app.app_context():
        socketio.emit('alert_rule_removed', {
            'signal': data.get('signal_name'),
            'type': data.get('alert_type')
        }, to=None)  # Broadcast to all

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
