# ADVANCED_FEATURES.md - Zaawansowane Funkcje

# 🚀 Zaawansowane Funkcje - Modbus Monitor

Dokumentacja czterech nowych funkcji dodanych do aplikacji desktop PyQt6.

## 📊 1. Wykresy Real-Time (QChart)

### Opis
Wykresy liniowe pokazujące historię ostatnich 500 pomiarów każdego sygnału w real-time.

### Funkcje
- **Działanie na żywo** - aktualizuje się w czasie rzeczywistym
- **Wiele serii** - każdy sygnał ma swoją linię
- **Skalowanie** - automatyczne dopasowanie osi Y
- **Przewijanie** - widok ostatnich pomiarów

### Kod

```python
from PyQt6.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis

# W modbus_monitor_pyqt.py dodaj:
class SignalChartWidget(QChartView):
    def __init__(self, signal_name):
        super().__init__()
        self.signal_name = signal_name
        self.chart = QChart()
        self.series = QLineSeries()
        self.chart.addSeries(self.series)
        self.setChart(self.chart)
        self.data_points = []
    
    def add_point(self, timestamp, value):
        """Dodaj punkt do wykresu"""
        self.data_points.append((timestamp, value))
        
        # Przechowuj ostatnie 500 punktów
        if len(self.data_points) > 500:
            self.data_points.pop(0)
        
        # Aktualizuj serię
        self.series.clear()
        for t, v in self.data_points:
            self.series.append(QPointF(t.timestamp(), v))
```

### Użycie

```python
# Inicjalizacja
self.chart_widget = SignalChartWidget("Sygnał 1")

# Dodawanie danych
self.chart_widget.add_point(datetime.now(), value)

# UI
self.layout.addWidget(self.chart_widget)
```

---

## 💾 2. Baza Danych (SQLite/PostgreSQL)

### Opis
Automatyczne przechowywanie historii sygnałów, alertów i zdarzeń w bazie danych.

### Obsługiwane Opcje

#### SQLite (Domyślnie)
- ✅ Lokalnie na komputerze
- ✅ Brak konfiguracji
- ✅ Plik: `modbus_data.db`
- ✅ Do testów i lokalnego użytku

```python
from modbus_database import ModbusDatabase

db = ModbusDatabase(db_type='sqlite', db_path='modbus_data.db')
db.save_signal(signal_name='Temp', value=25.5, unit='°C', address=0)
```

#### PostgreSQL
- ✅ Serwer bazodanowy
- ✅ Współpracę wieloużytkownicze
- ✅ Lepsze skalowanie
- ✅ Do produkcji

```python
db = ModbusDatabase(
    db_type='postgresql',
    db_url='postgresql://user:password@localhost:5432/modbus'
)
db.save_signal(signal_name='Pressure', value=101.3, unit='kPa')
```

### Tabele

1. **signals** - Historia pomiarów
   ```sql
   id | signal_name | signal_address | value | unit | status | timestamp
   ```

2. **alerts** - Historia alertów
   ```sql
   id | signal_name | alert_type | message | severity | timestamp
   ```

3. **events** - Historia zdarzeń
   ```sql
   id | event_type | message | timestamp
   ```

### Funkcje

```python
# Zapisz pomiar
db.save_signal('Temperatura', 25.5, '°C', 'ok', 0)

# Pobierz historię (ostatnie 60 minut)
history = db.get_signal_history('Temperatura', minutes=60)

# Pobierz alerty (ostatnie 24 godziny)
alerts = db.get_alerts(hours=24)

# Wyczyść stare dane (starsze niż 30 dni)
db.cleanup_old_data(days=30)
```

---

## 🚨 3. Alerty i Powiadomienia

### Opis
System automatycznych alertów z powiadomieniami na pulpicie.

### Typy Alertów

```python
from modbus_alerts import AlertRule, AlertsManager

# 1. Próg maksymalny
rule = AlertRule(
    signal_name='Temperatura',
    alert_type='threshold_high',
    threshold=50.0,
    severity='critical'
)

# 2. Próg minimalny
rule = AlertRule(
    signal_name='Temperatura',
    alert_type='threshold_low',
    threshold=10.0,
    severity='warning'
)

# 3. Utrata połączenia
rule = AlertRule(
    signal_name='Ciśnienie',
    alert_type='connection_lost',
    severity='critical'
)
```

### Poziomy Ważności

| Poziom | Opis | Działanie |
|--------|------|----------|
| `info` | Informacja | Log |
| `warning` | Ostrzeżenie | Log + powiadomienie |
| `critical` | Krytyczne | Log + powiadomienie + dźwięk |

### Użycie

```python
alerts_manager = AlertsManager(database=db)

# Dodaj reguły
alerts_manager.add_rule(AlertRule('Temp', 'threshold_high', 50.0))
alerts_manager.add_rule(AlertRule('Temp', 'threshold_low', 10.0))

# Sprawdzaj sygnały
alerts_manager.check_signal('Temp', value=55.0)  # → Alert!

# Aktywne alerty
active = alerts_manager.get_active_alerts()
```

### Powiadomienia Desktop

```python
from modbus_alerts import NotificationManager

notif_mgr = NotificationManager()
notif_mgr.desktop_notifications = True

# Włącz email (opcjonalnie)
notif_mgr.email_enabled = True
notif_mgr.email_recipients = ['admin@example.com']
```

---

## 📝 4. Logging do Pliku

### Opis
Automatyczne logowanie wszystkich zdarzeń do pliku.

### Lokalizacja

```
logs/
├── modbus_monitor_20251215.log
├── modbus_monitor_20251214.log
└── modbus_monitor_20251213.log
```

### Używanie

```python
from modbus_logger import get_modbus_logger

logger_mgr = get_modbus_logger(log_dir='logs')
logger = logger_mgr.get_logger('main')

logger.info('Aplikacja uruchomiona')
logger.warning('Brak połączenia')
logger.error('Błąd krytyczny')

# Pobierz ostatnie logi
recent_logs = logger_mgr.get_logs(days=1)

# Wyczyść stare logi (starsze niż 30 dni)
logger_mgr.cleanup_old_logs(days=30)
```

### Format Logów

```
2025-12-15 11:34:22 - modbus_monitor - INFO - ✓ Połączono z 192.168.1.100:502
2025-12-15 11:34:28 - modbus_monitor - WARNING - 🚨 ALERT: Temperatura > 50°C
2025-12-15 11:35:10 - modbus_monitor - ERROR - Błąd odczytu sygnału: Connection timeout
```

### Rotacja Plików

- 📄 Nowy plik każdego dnia
- 📊 Max 10MB na plik
- 🗑️ Przechowuj 7 ostatnich plików
- ⏰ Auto czyszczenie starszych niż 30 dni

---

## 🔧 Integracja w Aplikacji

### Kompletny Przykład

```python
from modbus_database import ModbusDatabase
from modbus_alerts import AlertsManager, AlertRule, NotificationManager
from modbus_logger import get_modbus_logger

# 1. Inicjalizacja
db = ModbusDatabase(db_type='sqlite')
logger_mgr = get_modbus_logger()
logger = logger_mgr.get_logger('main')

notif_mgr = NotificationManager()
alerts_mgr = AlertsManager(database=db, notification_callback=notif_mgr.send_notification)

# 2. Dodaj reguły alertów
alerts_mgr.add_rule(AlertRule('Temperatura', 'threshold_high', 50.0, severity='critical'))
alerts_mgr.add_rule(AlertRule('Ciśnienie', 'threshold_low', 100.0, severity='warning'))

# 3. Połączenie
logger.info('Aplikacja uruchomiona')

# 4. Pętla główna
for signal in signals:
    # Zapisz do bazy
    db.save_signal(signal['name'], signal['value'], signal['unit'], signal['status'])
    
    # Sprawdź alerty
    alerts_mgr.check_signal(signal['name'], signal['value'], signal['status'])
    
    # Log
    logger.info(f"Pomiar: {signal['name']} = {signal['value']}")
```

---

## 📊 Statystyki Bazy Danych

### SQLite
```
Plik: modbus_data.db (~10MB na 100k pomiarów)
Rekordów: ~100k
Okres: ~7 dni (przy 1s interwale)
```

### PostgreSQL
```
Server: postgresql://user:pass@localhost/modbus
Storage: ~15MB na 100k pomiarów
Queries/sec: ~100 (w zależności od serwera)
```

---

## 🚀 Następne Kroki

1. **Zainstaluj zależności**
   ```bash
   pip install -r requirements_desktop_extended.txt
   ```

2. **Włącz funkcje w aplikacji**
   - Zmodyfikuj `modbus_monitor_pyqt.py`
   - Dodaj import modułów
   - Dodaj UI dla alertów i logów

3. **Skonfiguruj**
   - Ustaw reguły alertów
   - Włącz database
   - Konfiguruj powiadomienia

4. **Testuj**
   - Monitoruj wykresy
   - Wyzwalaj alerty
   - Sprawdzaj logi i bazę

---

## 💡 Wskazówki

- 🎯 **Dla produkcji** → Użyj PostgreSQL
- 🎯 **Dla testów** → Użyj SQLite
- 🎯 **Alerty** → Zacznij od threshold_high/low
- 🎯 **Logi** → Przechowuj 30 dni max

---

**Gotowe do użytku! 🚀**