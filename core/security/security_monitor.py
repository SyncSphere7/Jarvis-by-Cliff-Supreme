"""
Security monitoring and threat detection system
"""

import logging
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict, deque
import re
import hashlib

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    INJECTION_ATTEMPT = "injection_attempt"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    MALICIOUS_COMMAND = "malicious_command"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    PRIVILEGE_ESCALATION = "privilege_escalation"

@dataclass
class SecurityEvent:
    """Represents a security event"""
    event_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    source: str
    description: str
    details: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    resolved: bool = False

@dataclass
class SecurityRule:
    """Security monitoring rule"""
    rule_id: str
    name: str
    threat_type: ThreatType
    pattern: str
    threshold: int
    time_window_minutes: int
    threat_level: ThreatLevel
    enabled: bool = True

class SecurityMonitor:
    """Monitors system for security threats and suspicious activity"""
    
    def __init__(self, alert_callback: Optional[Callable] = None):
        self.alert_callback = alert_callback
        self.security_events: List[SecurityEvent] = []
        self.event_history = deque(maxlen=10000)  # Keep last 10k events
        
        # Rate limiting tracking
        self.request_counts = defaultdict(lambda: deque())
        self.failed_attempts = defaultdict(lambda: deque())
        
        # Security rules
        self.security_rules = self._initialize_security_rules()
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Statistics
        self.stats = {
            'total_events': 0,
            'threats_detected': 0,
            'threats_blocked': 0,
            'false_positives': 0
        }
        
        logger.info("Security Monitor initialized")
    
    def _initialize_security_rules(self) -> Dict[str, SecurityRule]:
        """Initialize default security rules"""
        rules = {}
        
        # Brute force detection
        rules['brute_force_login'] = SecurityRule(
            rule_id='brute_force_login',
            name='Brute Force Login Detection',
            threat_type=ThreatType.BRUTE_FORCE,
            pattern=r'failed.*login|authentication.*failed|invalid.*credentials',
            threshold=5,
            time_window_minutes=10,
            threat_level=ThreatLevel.HIGH
        )
        
        # Injection attempt detection
        rules['sql_injection'] = SecurityRule(
            rule_id='sql_injection',
            name='SQL Injection Detection',
            threat_type=ThreatType.INJECTION_ATTEMPT,
            pattern=r'(union.*select|drop.*table|insert.*into|delete.*from|exec.*sp_|xp_cmdshell)',
            threshold=1,
            time_window_minutes=1,
            threat_level=ThreatLevel.CRITICAL
        )
        
        # Command injection
        rules['command_injection'] = SecurityRule(
            rule_id='command_injection',
            name='Command Injection Detection',
            threat_type=ThreatType.INJECTION_ATTEMPT,
            pattern=r'(;.*rm\s|;.*cat\s|;.*ls\s|&&.*rm|&&.*cat|\|.*rm|\|.*cat|`.*rm|`.*cat)',
            threshold=1,
            time_window_minutes=1,
            threat_level=ThreatLevel.CRITICAL
        )
        
        # Malicious commands
        rules['malicious_commands'] = SecurityRule(
            rule_id='malicious_commands',
            name='Malicious Command Detection',
            threat_type=ThreatType.MALICIOUS_COMMAND,
            pattern=r'(hack|crack|exploit|backdoor|malware|virus|trojan|keylogger|rootkit)',
            threshold=1,
            time_window_minutes=1,
            threat_level=ThreatLevel.HIGH
        )
        
        # Rate limiting
        rules['rate_limit'] = SecurityRule(
            rule_id='rate_limit',
            name='Rate Limit Exceeded',
            threat_type=ThreatType.RATE_LIMIT_EXCEEDED,
            pattern=r'.*',  # Applies to all requests
            threshold=100,
            time_window_minutes=1,
            threat_level=ThreatLevel.MEDIUM
        )
        
        # Suspicious patterns
        rules['suspicious_patterns'] = SecurityRule(
            rule_id='suspicious_patterns',
            name='Suspicious Activity Pattern',
            threat_type=ThreatType.SUSPICIOUS_PATTERN,
            pattern=r'(password.*dump|credential.*harvest|data.*exfil|privilege.*escalat)',
            threshold=1,
            time_window_minutes=5,
            threat_level=ThreatLevel.HIGH
        )
        
        return rules
    
    def start_monitoring(self):
        """Start security monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Security monitoring started")
    
    def stop_monitoring(self):
        """Stop security monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("Security monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Clean up old tracking data
                self._cleanup_old_data()
                
                # Check for pattern-based threats in recent events
                self._check_pattern_threats()
                
                # Sleep before next check
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def log_security_event(self, 
                          source: str, 
                          event_data: str, 
                          user_id: Optional[str] = None,
                          additional_details: Optional[Dict[str, Any]] = None) -> Optional[SecurityEvent]:
        """
        Log a security event and check for threats
        
        Args:
            source: Source of the event (e.g., 'voice_command', 'api_request')
            event_data: The actual data/command to analyze
            user_id: User associated with the event
            additional_details: Additional context
            
        Returns:
            SecurityEvent if threat detected, None otherwise
        """
        try:
            # Update statistics
            self.stats['total_events'] += 1
            
            # Add to event history
            event_record = {
                'timestamp': datetime.now(),
                'source': source,
                'data': event_data,
                'user_id': user_id,
                'details': additional_details or {}
            }
            self.event_history.append(event_record)
            
            # Check for immediate threats
            threat_event = self._analyze_event(source, event_data, user_id, additional_details)
            
            if threat_event:
                self.security_events.append(threat_event)
                self.stats['threats_detected'] += 1
                
                # Trigger alert if callback is set
                if self.alert_callback:
                    try:
                        self.alert_callback(threat_event)
                    except Exception as e:
                        logger.error(f"Error in alert callback: {e}")
                
                logger.warning(f"Security threat detected: {threat_event.threat_type.value} - {threat_event.description}")
                
                return threat_event
            
            return None
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
            return None
    
    def _analyze_event(self, 
                      source: str, 
                      event_data: str, 
                      user_id: Optional[str],
                      additional_details: Optional[Dict[str, Any]]) -> Optional[SecurityEvent]:
        """Analyze an event for security threats"""
        
        # Check rate limiting
        rate_limit_event = self._check_rate_limiting(source, user_id)
        if rate_limit_event:
            return rate_limit_event
        
        # Check against security rules
        for rule in self.security_rules.values():
            if not rule.enabled:
                continue
            
            # Check if pattern matches
            if re.search(rule.pattern, event_data.lower(), re.IGNORECASE):
                # Check if threshold is exceeded within time window
                if self._check_rule_threshold(rule, source, user_id):
                    return self._create_security_event(
                        rule.threat_type,
                        rule.threat_level,
                        source,
                        f"{rule.name}: Pattern '{rule.pattern}' detected in {source}",
                        {
                            'rule_id': rule.rule_id,
                            'pattern': rule.pattern,
                            'matched_data': event_data,
                            'additional_details': additional_details
                        },
                        user_id
                    )
        
        return None
    
    def _check_rate_limiting(self, source: str, user_id: Optional[str]) -> Optional[SecurityEvent]:
        """Check for rate limiting violations"""
        key = f"{source}:{user_id or 'anonymous'}"
        current_time = time.time()
        
        # Add current request
        self.request_counts[key].append(current_time)
        
        # Get rate limit rule
        rate_rule = self.security_rules.get('rate_limit')
        if not rate_rule or not rate_rule.enabled:
            return None
        
        # Count requests in time window
        time_window = rate_rule.time_window_minutes * 60
        cutoff_time = current_time - time_window
        
        # Remove old requests
        while self.request_counts[key] and self.request_counts[key][0] < cutoff_time:
            self.request_counts[key].popleft()
        
        # Check if threshold exceeded
        if len(self.request_counts[key]) > rate_rule.threshold:
            return self._create_security_event(
                ThreatType.RATE_LIMIT_EXCEEDED,
                ThreatLevel.MEDIUM,
                source,
                f"Rate limit exceeded: {len(self.request_counts[key])} requests in {rate_rule.time_window_minutes} minutes",
                {
                    'request_count': len(self.request_counts[key]),
                    'threshold': rate_rule.threshold,
                    'time_window_minutes': rate_rule.time_window_minutes,
                    'source': source
                },
                user_id
            )
        
        return None
    
    def _check_rule_threshold(self, rule: SecurityRule, source: str, user_id: Optional[str]) -> bool:
        """Check if a rule's threshold has been exceeded"""
        # For most rules, threshold of 1 means immediate trigger
        if rule.threshold <= 1:
            return True
        
        # For rules with higher thresholds, check recent history
        current_time = datetime.now()
        time_window = timedelta(minutes=rule.time_window_minutes)
        cutoff_time = current_time - time_window
        
        # Count matching events in time window
        matching_events = 0
        for event in reversed(list(self.event_history)):
            if event['timestamp'] < cutoff_time:
                break
            
            if (event['source'] == source and 
                event.get('user_id') == user_id and
                re.search(rule.pattern, event['data'].lower(), re.IGNORECASE)):
                matching_events += 1
        
        return matching_events >= rule.threshold
    
    def _create_security_event(self, 
                              threat_type: ThreatType,
                              threat_level: ThreatLevel,
                              source: str,
                              description: str,
                              details: Dict[str, Any],
                              user_id: Optional[str] = None) -> SecurityEvent:
        """Create a security event"""
        event_id = hashlib.md5(
            f"{threat_type.value}:{source}:{user_id}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        return SecurityEvent(
            event_id=event_id,
            threat_type=threat_type,
            threat_level=threat_level,
            source=source,
            description=description,
            details=details,
            timestamp=datetime.now(),
            user_id=user_id
        )
    
    def _check_pattern_threats(self):
        """Check for pattern-based threats in recent events"""
        # This could be expanded to detect more complex patterns
        # across multiple events, user behavior analysis, etc.
        pass
    
    def _cleanup_old_data(self):
        """Clean up old tracking data"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1 hour
        
        # Clean up request counts
        for key in list(self.request_counts.keys()):
            while (self.request_counts[key] and 
                   self.request_counts[key][0] < cutoff_time):
                self.request_counts[key].popleft()
            
            # Remove empty deques
            if not self.request_counts[key]:
                del self.request_counts[key]
        
        # Clean up failed attempts
        for key in list(self.failed_attempts.keys()):
            while (self.failed_attempts[key] and 
                   self.failed_attempts[key][0] < cutoff_time):
                self.failed_attempts[key].popleft()
            
            if not self.failed_attempts[key]:
                del self.failed_attempts[key]
    
    def get_security_events(self, 
                           limit: int = 100,
                           threat_level: Optional[ThreatLevel] = None,
                           resolved: Optional[bool] = None) -> List[SecurityEvent]:
        """Get security events with optional filtering"""
        events = self.security_events
        
        # Filter by threat level
        if threat_level:
            events = [e for e in events if e.threat_level == threat_level]
        
        # Filter by resolved status
        if resolved is not None:
            events = [e for e in events if e.resolved == resolved]
        
        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]
    
    def resolve_security_event(self, event_id: str, resolution_notes: str = "") -> bool:
        """Mark a security event as resolved"""
        for event in self.security_events:
            if event.event_id == event_id:
                event.resolved = True
                event.details['resolution_notes'] = resolution_notes
                event.details['resolved_at'] = datetime.now().isoformat()
                logger.info(f"Security event {event_id} marked as resolved")
                return True
        
        return False
    
    def add_security_rule(self, rule: SecurityRule) -> bool:
        """Add a custom security rule"""
        try:
            self.security_rules[rule.rule_id] = rule
            logger.info(f"Added security rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding security rule: {e}")
            return False
    
    def disable_security_rule(self, rule_id: str) -> bool:
        """Disable a security rule"""
        if rule_id in self.security_rules:
            self.security_rules[rule_id].enabled = False
            logger.info(f"Disabled security rule: {rule_id}")
            return True
        return False
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security monitoring statistics"""
        current_time = datetime.now()
        last_24h = current_time - timedelta(hours=24)
        
        # Count recent events
        recent_events = [e for e in self.security_events if e.timestamp > last_24h]
        
        # Count by threat level
        threat_levels = {}
        for level in ThreatLevel:
            threat_levels[level.value] = len([e for e in recent_events if e.threat_level == level])
        
        # Count by threat type
        threat_types = {}
        for threat_type in ThreatType:
            threat_types[threat_type.value] = len([e for e in recent_events if e.threat_type == threat_type])
        
        return {
            'monitoring_active': self.monitoring_active,
            'total_events_logged': self.stats['total_events'],
            'total_threats_detected': self.stats['threats_detected'],
            'threats_last_24h': len(recent_events),
            'unresolved_threats': len([e for e in self.security_events if not e.resolved]),
            'threat_levels_24h': threat_levels,
            'threat_types_24h': threat_types,
            'active_rules': len([r for r in self.security_rules.values() if r.enabled]),
            'total_rules': len(self.security_rules)
        }
    
    def generate_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate a comprehensive security report"""
        current_time = datetime.now()
        start_time = current_time - timedelta(hours=hours)
        
        # Get events in time range
        period_events = [e for e in self.security_events if e.timestamp > start_time]
        
        # Analyze events
        report = {
            'report_period_hours': hours,
            'generated_at': current_time.isoformat(),
            'summary': {
                'total_events': len(period_events),
                'critical_threats': len([e for e in period_events if e.threat_level == ThreatLevel.CRITICAL]),
                'high_threats': len([e for e in period_events if e.threat_level == ThreatLevel.HIGH]),
                'resolved_events': len([e for e in period_events if e.resolved]),
                'unresolved_events': len([e for e in period_events if not e.resolved])
            },
            'threat_breakdown': {},
            'top_sources': {},
            'recommendations': []
        }
        
        # Threat type breakdown
        for threat_type in ThreatType:
            count = len([e for e in period_events if e.threat_type == threat_type])
            if count > 0:
                report['threat_breakdown'][threat_type.value] = count
        
        # Top sources
        source_counts = {}
        for event in period_events:
            source_counts[event.source] = source_counts.get(event.source, 0) + 1
        
        report['top_sources'] = dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Generate recommendations
        if report['summary']['critical_threats'] > 0:
            report['recommendations'].append("Immediate attention required for critical threats")
        
        if report['summary']['unresolved_events'] > 10:
            report['recommendations'].append("High number of unresolved security events - review and resolve")
        
        if len(report['threat_breakdown']) > 5:
            report['recommendations'].append("Multiple threat types detected - consider security audit")
        
        return report