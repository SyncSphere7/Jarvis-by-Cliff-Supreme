"""
Unit tests for security monitoring system
"""

import unittest
import time
from unittest.mock import Mock

from core.security.security_monitor import (
    SecurityMonitor, ThreatLevel, ThreatType, SecurityRule, SecurityEvent
)
from core.ethics.validator import EthicsValidator

class TestSecurityMonitor(unittest.TestCase):
    """Test cases for Security Monitor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.alert_callback = Mock()
        self.monitor = SecurityMonitor(alert_callback=self.alert_callback)
    
    def test_initialization(self):
        """Test security monitor initialization"""
        self.assertIsNotNone(self.monitor.security_rules)
        self.assertGreater(len(self.monitor.security_rules), 0)
        self.assertFalse(self.monitor.monitoring_active)
    
    def test_malicious_command_detection(self):
        """Test detection of malicious commands"""
        malicious_commands = [
            "hack into the system",
            "crack the password",
            "exploit the vulnerability",
            "install malware"
        ]
        
        for command in malicious_commands:
            event = self.monitor.log_security_event(
                source="voice_command",
                event_data=command,
                user_id="test_user"
            )
            
            self.assertIsNotNone(event)
            self.assertEqual(event.threat_type, ThreatType.MALICIOUS_COMMAND)
            self.assertEqual(event.threat_level, ThreatLevel.HIGH)
    
    def test_injection_attempt_detection(self):
        """Test detection of injection attempts"""
        injection_attempts = [
            "'; DROP TABLE users; --",
            "UNION SELECT * FROM passwords",
            "; rm -rf /",
            "&& cat /etc/passwd"
        ]
        
        for attempt in injection_attempts:
            event = self.monitor.log_security_event(
                source="api_request",
                event_data=attempt,
                user_id="test_user"
            )
            
            self.assertIsNotNone(event)
            self.assertEqual(event.threat_type, ThreatType.INJECTION_ATTEMPT)
            self.assertEqual(event.threat_level, ThreatLevel.CRITICAL)
    
    def test_rate_limiting(self):
        """Test rate limiting detection"""
        # Send many requests quickly
        events = []
        for i in range(105):  # Exceed default threshold of 100
            event = self.monitor.log_security_event(
                source="api_request",
                event_data=f"request {i}",
                user_id="test_user"
            )
            if event:
                events.append(event)
        
        # Should detect rate limiting violation
        rate_limit_events = [e for e in events if e.threat_type == ThreatType.RATE_LIMIT_EXCEEDED]
        self.assertGreater(len(rate_limit_events), 0)
    
    def test_benign_commands(self):
        """Test that benign commands don't trigger alerts"""
        benign_commands = [
            "what time is it",
            "play some music",
            "turn on the lights",
            "what's the weather like"
        ]
        
        for command in benign_commands:
            event = self.monitor.log_security_event(
                source="voice_command",
                event_data=command,
                user_id="test_user"
            )
            
            self.assertIsNone(event)
    
    def test_alert_callback(self):
        """Test that alert callback is triggered"""
        self.monitor.log_security_event(
            source="test",
            event_data="hack the system",
            user_id="test_user"
        )
        
        # Verify callback was called
        self.alert_callback.assert_called_once()
        
        # Verify callback received SecurityEvent
        args = self.alert_callback.call_args[0]
        self.assertIsInstance(args[0], SecurityEvent)
    
    def test_security_rule_management(self):
        """Test adding and managing security rules"""
        # Add custom rule
        custom_rule = SecurityRule(
            rule_id="test_rule",
            name="Test Rule",
            threat_type=ThreatType.SUSPICIOUS_PATTERN,
            pattern=r"test_pattern",
            threshold=1,
            time_window_minutes=5,
            threat_level=ThreatLevel.LOW
        )
        
        success = self.monitor.add_security_rule(custom_rule)
        self.assertTrue(success)
        self.assertIn("test_rule", self.monitor.security_rules)
        
        # Test custom rule detection
        event = self.monitor.log_security_event(
            source="test",
            event_data="this contains test_pattern",
            user_id="test_user"
        )
        
        self.assertIsNotNone(event)
        self.assertEqual(event.threat_type, ThreatType.SUSPICIOUS_PATTERN)
        
        # Disable rule
        disabled = self.monitor.disable_security_rule("test_rule")
        self.assertTrue(disabled)
        self.assertFalse(self.monitor.security_rules["test_rule"].enabled)
    
    def test_event_resolution(self):
        """Test resolving security events"""
        # Create a security event
        event = self.monitor.log_security_event(
            source="test",
            event_data="malware detected",
            user_id="test_user"
        )
        
        self.assertIsNotNone(event)
        self.assertFalse(event.resolved)
        
        # Resolve the event
        resolved = self.monitor.resolve_security_event(
            event.event_id, 
            "False positive - legitimate security discussion"
        )
        
        self.assertTrue(resolved)
        self.assertTrue(event.resolved)
        self.assertIn("resolution_notes", event.details)
    
    def test_security_statistics(self):
        """Test security statistics generation"""
        # Generate some events
        self.monitor.log_security_event("test", "hack attempt", "user1")
        self.monitor.log_security_event("test", "malware found", "user2")
        
        stats = self.monitor.get_security_stats()
        
        self.assertIn('monitoring_active', stats)
        self.assertIn('total_threats_detected', stats)
        self.assertIn('threat_levels_24h', stats)
        self.assertIn('threat_types_24h', stats)
        self.assertGreater(stats['total_threats_detected'], 0)
    
    def test_security_report_generation(self):
        """Test security report generation"""
        # Generate some test events
        self.monitor.log_security_event("voice", "hack the system", "user1")
        self.monitor.log_security_event("api", "'; DROP TABLE", "user2")
        
        report = self.monitor.generate_security_report(hours=1)
        
        self.assertIn('report_period_hours', report)
        self.assertIn('summary', report)
        self.assertIn('threat_breakdown', report)
        self.assertIn('recommendations', report)
        
        self.assertGreater(report['summary']['total_events'], 0)
    
    def test_monitoring_lifecycle(self):
        """Test starting and stopping monitoring"""
        # Start monitoring
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.monitoring_active)
        self.assertIsNotNone(self.monitor.monitor_thread)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring_active)

class TestEthicsValidatorIntegration(unittest.TestCase):
    """Test ethics validator integration with security monitor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = SecurityMonitor()
        self.validator = EthicsValidator(security_monitor=self.monitor)
    
    def test_ethics_violation_logging(self):
        """Test that ethics violations are logged to security monitor"""
        # Test unethical command
        result = self.validator.validate_command("hack into the database", "test_user")
        
        self.assertFalse(result["is_valid"])
        self.assertGreater(len(result["violations"]), 0)
        
        # Check that security event was logged
        events = self.monitor.get_security_events()
        ethics_events = [e for e in events if e.source == "ethics_validator"]
        
        self.assertGreater(len(ethics_events), 0)
        self.assertEqual(ethics_events[0].user_id, "test_user")
    
    def test_ethical_command_no_logging(self):
        """Test that ethical commands don't create security events"""
        initial_event_count = len(self.monitor.get_security_events())
        
        # Test ethical command
        result = self.validator.validate_command("what time is it", "test_user")
        
        self.assertTrue(result["is_valid"])
        
        # Check that no new security events were created
        final_event_count = len(self.monitor.get_security_events())
        self.assertEqual(initial_event_count, final_event_count)

if __name__ == '__main__':
    unittest.main(verbosity=1)