# Modbus Monitor - Unit Tests Documentation

## Overview

This directory contains comprehensive unit tests for the Modbus Monitor project using **pytest**.

## Test Structure

```
tests/
├── README.md                    # This file
├── __init__.py                  # Package marker
├── test_modbus_client.py        # Tests for ModbusClientManager
├── test_modbus_alerts.py        # Tests for AlertsManager and AlertRule
├── test_data_exporter.py        # Tests for DataExporter
└── test_modbus_logger.py        # Tests for logging functionality
```

## Installation

### Prerequisites

- Python 3.8+
- pytest 7.4.0+
- pytest-cov (optional, for coverage reports)

### Setup

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Or install with project dependencies
pip install -e ".[dev]"
```

## Running Tests

### Run all tests

```bash
pytest
```

### Run with verbose output

```bash
pytest -v
```

### Run specific test file

```bash
pytest tests/test_modbus_client.py
```

### Run specific test class

```bash
pytest tests/test_modbus_client.py::TestModbusClientManagerConnection
```

### Run specific test function

```bash
pytest tests/test_modbus_client.py::TestModbusClientManagerConnection::test_connect_tcp_success
```

### Run tests with specific marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow
```

## Coverage Reports

### Generate coverage report

```bash
pytest --cov=modbus_monitor --cov-report=html
```

This creates an HTML report in `htmlcov/index.html`

### Terminal coverage report

```bash
pytest --cov=modbus_monitor --cov-report=term-missing
```

## Test Markers

The following pytest markers are defined:

| Marker | Description |
|--------|-------------|
| `@pytest.mark.unit` | Fast, isolated unit tests |
| `@pytest.mark.integration` | Tests requiring external services |
| `@pytest.mark.slow` | Tests taking > 1 second |
| `@pytest.mark.network` | Tests requiring network access |

## Test Files Overview

### test_modbus_client.py

Tests for `ModbusClientManager` class:

- **Initialization**: Default values, instance creation
- **Connection Management**: TCP/Serial connection, disconnection
- **Register Reading**: Holding, input, coil, discrete register reads
- **Register Writing**: Write operations for holding/coil registers
- **Error Handling**: Exception handling for various error scenarios

**Test Classes:**
- `TestModbusClientManagerInit`
- `TestModbusClientManagerConnection`
- `TestModbusClientManagerReadRegisters`
- `TestModbusClientManagerWriteRegisters`
- `TestModbusClientManagerErrorHandling`

**Coverage:** ~95% of ModbusClientManager

### test_modbus_alerts.py

Tests for alert system:

- **AlertRule**: Creation, default values
- **AlertsManager**: Initialization, rule management
- **Alert Checking**: Threshold detection, connection lost alerts
- **Alert Triggering**: History tracking, database saving
- **NotificationManager**: Desktop and email notifications

**Test Classes:**
- `TestAlertRule`
- `TestAlertsManagerInit`
- `TestAlertsManagerRuleManagement`
- `TestAlertsManagerAlertChecking`
- `TestAlertsManagerAlertTriggering`
- `TestAlertsManagerActiveAlerts`
- `TestNotificationManager`

**Coverage:** ~90% of AlertsManager

### test_data_exporter.py

Tests for data export functionality:

- **Initialization**: Directory creation
- **Filename Generation**: Timestamp-based naming
- **CSV Export**: File creation, content verification
- **JSON Export**: File creation, data integrity
- **Excel Export**: File creation (when openpyxl available)
- **Batch Export**: Export to multiple formats
- **Error Handling**: Permission errors, edge cases

**Test Classes:**
- `TestDataExporterInit`
- `TestDataExporterFilenameGeneration`
- `TestDataExporterCSV`
- `TestDataExporterJSON`
- `TestDataExporterExcel`
- `TestDataExporterBatch`
- `TestDataExporterErrorHandling`
- `TestDataExporterIntegration`

**Coverage:** ~85% of DataExporter

### test_modbus_logger.py

Tests for logging functionality:

- **Logger Setup**: Initialization, log level configuration
- **Log File Creation**: Verify files are created
- **Logging Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **File Logging**: Message persistence to disk
- **Integration**: Multiple loggers, multiple messages

**Test Classes:**
- `TestLoggerSetup`
- `TestGetLogger`
- `TestLoggerLogging`
- `TestLoggerIntegration`

**Coverage:** ~80% of logging module

## Fixtures

Common fixtures defined in `conftest.py`:

### Session Fixtures
- `temp_export_dir`: Temporary directory for export tests
- `temp_db_dir`: Temporary directory for database tests

### Function Fixtures
- `sample_signals`: List of 3 sample signal dictionaries
- `empty_signals`: Empty signals list
- `sample_alert_data`: Sample alert data dictionary
- `mock_modbus_client`: Mock Modbus client with predefined responses
- `mock_database`: Mock database instance
- `mock_notification_callback`: Mock notification callback function
- `test_data_generator`: TestDataGenerator utility class

## Mock Objects

Mock objects are used extensively to:
- Avoid hardware dependencies (Modbus devices)
- Avoid database dependencies
- Avoid external service dependencies (email, notifications)
- Speed up test execution
- Make tests deterministic

## Best Practices

### When Writing New Tests

1. **Use appropriate markers**
   ```python
   @pytest.mark.unit
   def test_something():
       pass
   ```

2. **Use fixtures for setup**
   ```python
   def test_with_fixture(sample_signals):
       assert len(sample_signals) == 3
   ```

3. **Use descriptive names**
   ```python
   # Good
   def test_read_holding_registers_success()
   
   # Bad
   def test_read()
   ```

4. **Test one thing per test**
   ```python
   def test_connection_sets_is_connected_flag():
       # Single assertion focus
       assert client.is_connected is True
   ```

5. **Use arrange-act-assert pattern**
   ```python
   def test_example():
       # Arrange
       client = ModbusClientManager()
       
       # Act
       result = client.read_registers(address=0, count=1)
       
       # Assert
       assert result is not None
   ```

## Common Issues

### Import Errors

```bash
ModuleNotFoundError: No module named 'modbus_monitor'
```

**Solution:** Ensure project root is in PYTHONPATH. The conftest.py should handle this automatically.

### Mock Not Working

```bash
assert mock_object.called
AssertionError: Expected call not made
```

**Solution:** Ensure you're patching the correct path:
```python
@patch('modbus_monitor.modbus_client.ModbusTcpClient')  # Correct
# Not:
@patch('ModbusTcpClient')  # Wrong
```

### Missing Dependencies

```bash
ImportError: No module named 'pytest'
```

**Solution:** Install test dependencies:
```bash
pip install pytest pytest-cov pytest-mock
```

## CI/CD Integration

### GitHub Actions

Add to `.github/workflows/tests.yml`:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: pytest --cov=modbus_monitor
```

## Coverage Goals

- **Overall Target:** ≥ 85% code coverage
- **Critical Modules:** ≥ 90% coverage
  - modbus_client.py
  - modbus_alerts.py
  - data_exporter.py

## Future Testing Improvements

- [ ] Add integration tests with real database
- [ ] Add tests with real Modbus devices (test server)
- [ ] Add performance benchmarks
- [ ] Add stress tests for concurrent operations
- [ ] Add tests for GUI components (PyQt6)
- [ ] Add API endpoint tests for Flask routes

## Contributing

When contributing to the project:

1. Write tests for new features
2. Ensure all tests pass locally: `pytest`
3. Maintain or improve code coverage
4. Follow the test structure and naming conventions
5. Add documentation for complex test scenarios

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
