#!/usr/bin/env python
"""
test_modbus_alerts.py - Unit Tests for Alert System

Tests cover:
- AlertRule creation
- AlertsManager initialization
- Rule management (add, remove)
- Alert triggering and checking
- Notification handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from pathlib import Path
import sys

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modbus_monitor.modbus_alerts import AlertRule, AlertsManager, NotificationManager


@pytest.mark.unit
class TestAlertRule:
    """Test AlertRule dataclass"""
    
    def test_alert_rule_creation(self):
        """Test creating an AlertRule"""
        rule = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_high',
            threshold=50.0,
            enabled=True,
            severity='critical'
        )
        
        assert rule.signal_name == 'Temperature'
        assert rule.alert_type == 'threshold_high'
        assert rule.threshold == 50.0
        assert rule.enabled is True
        assert rule.severity == 'critical'
    
    def test_alert_rule_defaults(self):
        """Test AlertRule with default values"""
        rule = AlertRule(
            signal_name='Pressure',
            alert_type='connection_lost'
        )
        
        assert rule.signal_name == 'Pressure'
        assert rule.alert_type == 'connection_lost'
        assert rule.threshold is None
        assert rule.enabled is True
        assert rule.severity == 'warning'


@pytest.mark.unit
class TestAlertsManagerInit:
    """Test AlertsManager initialization"""
    
    def test_init_defaults(self):
        """Test default initialization"""
        alerts = AlertsManager()
        
        assert alerts.database is None
        assert alerts.notification_callback is None
        assert alerts.rules == {}
        assert alerts.alert_history == []
        assert alerts.max_history == 1000
    
    def test_init_with_dependencies(self, mock_database, mock_notification_callback):
        """Test initialization with dependencies"""
        alerts = AlertsManager(
            database=mock_database,
            notification_callback=mock_notification_callback
        )
        
        assert alerts.database is mock_database
        assert alerts.notification_callback is mock_notification_callback


@pytest.mark.unit
class TestAlertsManagerRuleManagement:
    """Test alert rule management"""
    
    def test_add_rule(self):
        """Test adding a rule"""
        alerts = AlertsManager()
        rule = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_high',
            threshold=50.0
        )
        
        alerts.add_rule(rule)
        
        assert 'Temperature' in alerts.rules
        assert rule in alerts.rules['Temperature']
    
    def test_add_multiple_rules_same_signal(self):
        """Test adding multiple rules for same signal"""
        alerts = AlertsManager()
        rule1 = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_high',
            threshold=50.0
        )
        rule2 = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_low',
            threshold=0.0
        )
        
        alerts.add_rule(rule1)
        alerts.add_rule(rule2)
        
        assert len(alerts.rules['Temperature']) == 2
    
    def test_remove_rule(self):
        """Test removing a rule"""
        alerts = AlertsManager()
        rule = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_high',
            threshold=50.0
        )
        alerts.add_rule(rule)
        
        alerts.remove_rule('Temperature', 'threshold_high')
        
        assert len(alerts.rules.get('Temperature', [])) == 0
    
    def test_remove_rule_preserves_others(self):
        """Test that removing rule preserves other rules"""
        alerts = AlertsManager()
        rule1 = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_high',
            threshold=50.0
        )
        rule2 = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_low',
            threshold=0.0
        )
        alerts.add_rule(rule1)
        alerts.add_rule(rule2)
        
        alerts.remove_rule('Temperature', 'threshold_high')
        
        assert len(alerts.rules['Temperature']) == 1
        assert alerts.rules['Temperature'][0].alert_type == 'threshold_low'


@pytest.mark.unit
class TestAlertsManagerAlertChecking:
    """Test alert checking logic"""
    
    def test_check_threshold_high_triggered(self, mock_notification_callback):
        """Test threshold_high alert is triggered"""
        alerts = AlertsManager(notification_callback=mock_notification_callback)
        rule = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_high',
            threshold=50.0,
            severity='critical'
        )
        alerts.add_rule(rule)
        
        alerts.check_signal('Temperature', 60.0)  # Value > threshold
        
        assert len(alerts.alert_history) == 1
        assert alerts.alert_history[0]['alert_type'] == 'threshold_high'
        mock_notification_callback.assert_called_once()
    
    def test_check_threshold_high_not_triggered(self, mock_notification_callback):
        """Test threshold_high alert is not triggered when below threshold"""
        alerts = AlertsManager(notification_callback=mock_notification_callback)
        rule = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_high',
            threshold=50.0
        )
        alerts.add_rule(rule)
        
        alerts.check_signal('Temperature', 40.0)  # Value < threshold
        
        assert len(alerts.alert_history) == 0
        mock_notification_callback.assert_not_called()
    
    def test_check_threshold_low_triggered(self, mock_notification_callback):
        """Test threshold_low alert is triggered"""
        alerts = AlertsManager(notification_callback=mock_notification_callback)
        rule = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_low',
            threshold=0.0,
            severity='warning'
        )
        alerts.add_rule(rule)
        
        alerts.check_signal('Temperature', -5.0)  # Value < threshold
        
        assert len(alerts.alert_history) == 1
        assert alerts.alert_history[0]['alert_type'] == 'threshold_low'
    
    def test_check_connection_lost_triggered(self, mock_notification_callback):
        """Test connection_lost alert is triggered"""
        alerts = AlertsManager(notification_callback=mock_notification_callback)
        rule = AlertRule(
            signal_name='Temperature',
            alert_type='connection_lost',
            severity='critical'
        )
        alerts.add_rule(rule)
        
        alerts.check_signal('Temperature', 0.0, status='error')
        
        assert len(alerts.alert_history) == 1
        assert alerts.alert_history[0]['alert_type'] == 'connection_lost'
    
    def test_check_signal_no_rules(self):
        """Test checking signal with no rules"""
        alerts = AlertsManager()
        
        alerts.check_signal('Unknown', 50.0)
        
        assert len(alerts.alert_history) == 0
    
    def test_check_signal_disabled_rule(self):
        """Test that disabled rules don't trigger"""
        alerts = AlertsManager()
        rule = AlertRule(
            signal_name='Temperature',
            alert_type='threshold_high',
            threshold=50.0,
            enabled=False
        )
        alerts.add_rule(rule)
        
        alerts.check_signal('Temperature', 60.0)
        
        assert len(alerts.alert_history) == 0


@pytest.mark.unit
class TestAlertsManagerAlertTriggering:
    """Test alert triggering"""
    
    def test_trigger_alert_adds_to_history(self, sample_alert_data):
        """Test that triggered alert is added to history"""
        alerts = AlertsManager()
        
        alerts.trigger_alert(sample_alert_data)
        
        assert len(alerts.alert_history) == 1
        assert alerts.alert_history[0] == sample_alert_data
    
    def test_trigger_alert_saves_to_db(self, sample_alert_data, mock_database):
        """Test that triggered alert is saved to database"""
        alerts = AlertsManager(database=mock_database)
        
        alerts.trigger_alert(sample_alert_data)
        
        mock_database.save_alert.assert_called_once()
    
    def test_trigger_alert_sends_notification(self, sample_alert_data, mock_notification_callback):
        """Test that triggered alert sends notification"""
        alerts = AlertsManager(notification_callback=mock_notification_callback)
        
        alerts.trigger_alert(sample_alert_data)
        
        mock_notification_callback.assert_called_once_with(sample_alert_data)
    
    def test_alert_history_max_length(self):
        """Test that alert history respects max_history"""
        alerts = AlertsManager()
        alerts.max_history = 5
        
        # Add more alerts than max_history
        for i in range(10):
            alert = {
                'signal_name': f'Signal_{i}',
                'alert_type': 'test',
                'message': f'Alert {i}'
            }
            alerts.trigger_alert(alert)
        
        # Only last 5 should remain
        assert len(alerts.alert_history) == 5
        assert alerts.alert_history[0]['signal_name'] == 'Signal_5'


@pytest.mark.unit
class TestAlertsManagerActiveAlerts:
    """Test active alerts retrieval"""
    
    def test_get_active_alerts_empty(self):
        """Test getting active alerts when empty"""
        alerts = AlertsManager()
        
        active = alerts.get_active_alerts()
        
        assert active == []
    
    def test_get_active_alerts_returns_last_10(self):
        """Test that get_active_alerts returns last 10"""
        alerts = AlertsManager()
        
        # Add 15 alerts
        for i in range(15):
            alert = {
                'signal_name': f'Signal_{i}',
                'alert_type': 'test',
                'message': f'Alert {i}'
            }
            alerts.trigger_alert(alert)
        
        active = alerts.get_active_alerts()
        
        assert len(active) == 10
        assert active[0]['signal_name'] == 'Signal_5'
        assert active[-1]['signal_name'] == 'Signal_14'
    
    def test_clear_alert_history(self):
        """Test clearing alert history"""
        alerts = AlertsManager()
        
        for i in range(5):
            alert = {'signal_name': f'Signal_{i}'}
            alerts.trigger_alert(alert)
        
        assert len(alerts.alert_history) == 5
        
        alerts.clear_alert_history()
        
        assert len(alerts.alert_history) == 0


@pytest.mark.unit
class TestNotificationManager:
    """Test NotificationManager"""
    
    def test_init_defaults(self):
        """Test default initialization"""
        notif = NotificationManager()
        
        assert notif.enabled is True
        assert notif.desktop_notifications is True
        assert notif.email_enabled is False
        assert notif.email_recipients == []
    
    @pytest.mark.skip(reason="notification module not available in test environment")
    def test_send_desktop_notification(self, mock_notify, sample_alert_data):
        """Test sending desktop notification"""
        notif = NotificationManager()
        
        notif.send_desktop_notification(sample_alert_data)
        
        mock_notify.assert_called_once()
        call_kwargs = mock_notify.call_args[1]
        assert 'title' in call_kwargs
        assert 'message' in call_kwargs
    
    def test_send_notification_disabled(self, sample_alert_data):
        """Test that disabled notifications don't send"""
        notif = NotificationManager()
        notif.enabled = False
        
        with patch.object(notif, 'send_desktop_notification') as mock_desktop:
            notif.send_notification(sample_alert_data)
            mock_desktop.assert_not_called()
