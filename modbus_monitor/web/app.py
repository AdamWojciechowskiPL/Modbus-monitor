# app.py - Aplikacja Flask do monitorowania Modbus

from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime
import json
import threading
import time
import os
from pathlib import Path

# Relative imports from parent package
from ..modbus_client import ModbusClientManager
from ..data_exporter import DataExporter

app = Flask(__name__, 
            template_folder=str(Path(__file__).parent / 'templates'),
            static_folder=str(Path(__file__).parent / 'static'))
app.config['JSON_SORT_KEYS'] = False

# Globalna instancja managera Modbus
modbus_manager = ModbusClientManager()
data_exporter = DataExporter()

# Store dla danych sygnałów
signals_storage = {
    'signals': [],
    'connected': False,
    'last_update': None,
    'read_count': 0,
    'error_count': 0
}

# ============= ROUTES =============

@app.route('/')
def index():
    """Strona główna"""
    return render_template('index.html')

@app.route('/api/connect', methods=['POST'])
def api_connect():
    """Połącz z urządzeniem Modbus"""
    try:
        data = request.json
        host = data.get('host', '192.168.1.100')
        port = data.get('port', 502)
        connection_type = data.get('connectionType', 'tcp')
        timeout = data.get('timeout', 5)
        unit_id = data.get('unitId', 1)
        serial_port = data.get('serialPort', 'COM3')
        baud_rate = data.get('baudRate', 9600)
        
        # Połącz do Modbus
        success = modbus_manager.connect(
            host=host,
            port=port,
            connection_type=connection_type,
            timeout=timeout,
            unit_id=unit_id,
            serial_port=serial_port,
            baud_rate=baud_rate
        )
        
        if success:
            signals_storage['connected'] = True
            return jsonify({'status': 'ok', 'message': 'Połączono pomyślnie'})
        else:
            return jsonify({'status': 'error', 'message': 'Nie udało się połączyć'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    """Rozłącz z urządzeniem Modbus"""
    try:
        modbus_manager.disconnect()
        signals_storage['connected'] = False
        return jsonify({'status': 'ok', 'message': 'Rozłączono'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/read-signals', methods=['POST'])
def api_read_signals():
    """Odczytaj sygnały z urządzenia"""
    try:
        data = request.json
        start_address = data.get('startAddress', 0)
        count = data.get('count', 5)
        register_type = data.get('registerType', 'holding')
        
        if not signals_storage['connected']:
            return jsonify({'status': 'error', 'message': 'Brak połączenia'}), 400
        
        # Odczytaj z Modbus
        values = modbus_manager.read_registers(
            address=start_address,
            count=count,
            register_type=register_type
        )
        
        if values is not None:
            # Aktualizuj storage
            signals_storage['signals'] = []
            for i, value in enumerate(values):
                signals_storage['signals'].append({
                    'id': i,
                    'address': start_address + i,
                    'name': f'Sygnał {i + 1}',
                    'value': value,
                    'unit': '',
                    'status': 'ok',
                    'lastUpdate': datetime.now().isoformat()
                })
            
            signals_storage['last_update'] = datetime.now().isoformat()
            signals_storage['read_count'] += 1
            
            return jsonify({
                'status': 'ok',
                'signals': signals_storage['signals'],
                'readCount': signals_storage['read_count'],
                'errorCount': signals_storage['error_count']
            })
        else:
            signals_storage['error_count'] += 1
            return jsonify({'status': 'error', 'message': 'Błąd odczytu sygnałów'}), 400
            
    except Exception as e:
        signals_storage['error_count'] += 1
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/status', methods=['GET'])
def api_status():
    """Pobierz status aplikacji"""
    return jsonify({
        'connected': signals_storage['connected'],
        'signals': signals_storage['signals'],
        'readCount': signals_storage['read_count'],
        'errorCount': signals_storage['error_count'],
        'lastUpdate': signals_storage['last_update']
    })

@app.route('/api/export/csv', methods=['POST'])
def api_export_csv():
    """Eksportuj dane do CSV"""
    try:
        data = request.json
        signals = data.get('signals', signals_storage['signals'])
        filename = data.get('filename', 'modbus_data.csv')
        
        filepath = data_exporter.export_to_csv(signals, filename)
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/export/excel', methods=['POST'])
def api_export_excel():
    """Eksportuj dane do Excel"""
    try:
        data = request.json
        signals = data.get('signals', signals_storage['signals'])
        filename = data.get('filename', 'modbus_data.xlsx')
        
        filepath = data_exporter.export_to_excel(signals, filename)
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/export/json', methods=['POST'])
def api_export_json():
    """Eksportuj dane do JSON"""
    try:
        data = request.json
        signals = data.get('signals', signals_storage['signals'])
        filename = data.get('filename', 'modbus_data.json')
        
        filepath = data_exporter.export_to_json(signals, filename)
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/export/all', methods=['POST'])
def api_export_all():
    """Eksportuj wszystkie dane (CSV + JSON + Excel)"""
    try:
        signals = request.json.get('signals', signals_storage['signals'])
        
        files = data_exporter.export_all(signals)
        return jsonify({
            'status': 'ok',
            'files': files,
            'message': 'Dane wyeksportowane do folderu "exports"'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# ============= MAIN =============

if __name__ == '__main__':
    # Upewnij się, że folder exports istnieje
    os.makedirs('exports', exist_ok=True)
    
    print("="*70)
    print("🚀 Modbus Monitor - Flask")
    print("="*70)
    print("📍 Otwórz: http://localhost:5000")
    print("="*70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
