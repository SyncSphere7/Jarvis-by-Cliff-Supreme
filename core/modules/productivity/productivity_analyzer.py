"""
Productivity analytics and insights for Jarvis AI Assistant
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class ProductivityMetric(Enum):
    """Types of productivity metrics"""
    TASK_COMPLETION_RATE = "task_completion_rate"
    AVERAGE_TASK_DURATION = "average_task_duration"
    DAILY_PRODUCTIVITY_SCORE = "daily_productivity_score"
    FOCUS_TIME = "focus_time"
    BREAK_FREQUENCY = "break_frequency"
    GOAL_ACHIEVEMENT = "goal_achievement"

@dataclass
class ProductivityInsight:
    """Productivity insight data structure"""
    metric: ProductivityMetric
    value: float
    trend: str  # "improving", "declining", "stable"
    recommendation: str
    confidence: float
    period: str  # "daily", "weekly", "monthly"

class ProductivityAnalyzer:
    """Analyzes productivity patterns and provides insights"""
    
    def __init__(self, task_manager, reminder_system, calendar_integration):
        self.task_manager = task_manager
        self.reminder_system = reminder_system
        self.calendar_integration = calendar_integration
        
        # Historical data storage (simplified)
        self.productivity_history: Dict[str, List[Dict]] = {}  # user_id -> history
        
        logger.info("Productivity Analyzer initialized")
    
    def analyze_user_productivity(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze user productivity over specified period
        
        Args:
            user_id: User identifier
            days_back: Number of days to analyze
            
        Returns:
            Comprehensive productivity analysis
        """
        try:
            analysis = {
                'user_id': user_id,
                'analysis_period': f"{days_back} days",
                'generated_at': datetime.now().isoformat(),
                'metrics': {},
                'insights': [],
                'recommendations': [],
                'productivity_score': 0.0
            }
            
            # Get task completion metrics
            task_metrics = self._analyze_task_completion(user_id, days_back)
            analysis['metrics']['tasks'] = task_metrics
            
            # Get calendar utilization metrics
            calendar_metrics = self._analyze_calendar_utilization(user_id, days_back)
            analysis['metrics']['calendar'] = calendar_metrics
            
            # Get reminder effectiveness metrics
            reminder_metrics = self._analyze_reminder_effectiveness(user_id, days_back)
            analysis['metrics']['reminders'] = reminder_metrics
            
            # Calculate overall productivity score
            analysis['productivity_score'] = self._calculate_productivity_score(
                task_metrics, calendar_metrics, reminder_metrics
            )
            
            # Generate insights
            analysis['insights'] = self._generate_insights(
                task_metrics, calendar_metrics, reminder_metrics
            )
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(
                analysis['productivity_score'], analysis['insights']
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing productivity: {e}")
            return {"error": str(e)}
    
    def _analyze_task_completion(self, user_id: str, days_back: int) -> Dict[str, Any]:
        """Analyze task completion patterns"""
        try:
            # Get user tasks (simplified - in real implementation would query historical data)
            if hasattr(self.task_manager, 'tasks') and user_id in self.task_manager.tasks:
                user_tasks = list(self.task_manager.tasks[user_id].values())
            else:
                user_tasks = []
            
            total_tasks = len(user_tasks)
            completed_tasks = len([t for t in user_tasks if t.status.value == 'completed'])
            pending_tasks = total_tasks - completed_tasks
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Analyze task priorities
            high_priority_tasks = len([t for t in user_tasks if t.priority.value >= 3])
            completed_high_priority = len([t for t in user_tasks 
                                         if t.status.value == 'completed' and t.priority.value >= 3])
            
            high_priority_completion_rate = (completed_high_priority / high_priority_tasks * 100) if high_priority_tasks > 0 else 0
            
            return {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'completion_rate': round(completion_rate, 1),
                'high_priority_tasks': high_priority_tasks,
                'high_priority_completion_rate': round(high_priority_completion_rate, 1),
                'average_tasks_per_day': round(total_tasks / max(days_back, 1), 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing task completion: {e}")
            return {}
    
    def _analyze_calendar_utilization(self, user_id: str, days_back: int) -> Dict[str, Any]:
        """Analyze calendar utilization patterns"""
        try:
            # Get user events
            if hasattr(self.calendar_integration, 'events') and user_id in self.calendar_integration.events:
                user_events = list(self.calendar_integration.events[user_id].values())
            else:
                user_events = []
            
            total_events = len(user_events)
            
            # Calculate time utilization
            total_scheduled_hours = 0
            meeting_hours = 0
            
            for event in user_events:
                duration = (event.end_time - event.start_time).total_seconds() / 3600
                total_scheduled_hours += duration
                
                if event.event_type.value == 'meeting':
                    meeting_hours += duration
            
            # Calculate utilization metrics
            working_hours_per_day = 8  # Assume 8-hour workday
            total_available_hours = days_back * working_hours_per_day
            utilization_rate = (total_scheduled_hours / total_available_hours * 100) if total_available_hours > 0 else 0
            
            return {
                'total_events': total_events,
                'total_scheduled_hours': round(total_scheduled_hours, 1),
                'meeting_hours': round(meeting_hours, 1),
                'utilization_rate': round(utilization_rate, 1),
                'average_events_per_day': round(total_events / max(days_back, 1), 1),
                'average_event_duration': round(total_scheduled_hours / max(total_events, 1), 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing calendar utilization: {e}")
            return {}
    
    def _analyze_reminder_effectiveness(self, user_id: str, days_back: int) -> Dict[str, Any]:
        """Analyze reminder system effectiveness"""
        try:
            reminder_stats = self.reminder_system.get_reminder_stats(user_id)
            
            total_reminders = reminder_stats.get('total_reminders', 0)
            acknowledged_reminders = reminder_stats.get('acknowledged_reminders', 0)
            
            effectiveness_rate = (acknowledged_reminders / total_reminders * 100) if total_reminders > 0 else 0
            
            return {
                'total_reminders': total_reminders,
                'acknowledged_reminders': acknowledged_reminders,
                'pending_reminders': reminder_stats.get('pending_reminders', 0),
                'effectiveness_rate': round(effectiveness_rate, 1),
                'average_reminders_per_day': round(total_reminders / max(days_back, 1), 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing reminder effectiveness: {e}")
            return {}
    
    def _calculate_productivity_score(self, task_metrics: Dict, calendar_metrics: Dict, reminder_metrics: Dict) -> float:
        """Calculate overall productivity score (0-100)"""
        try:
            scores = []
            
            # Task completion score (40% weight)
            task_completion_rate = task_metrics.get('completion_rate', 0)
            high_priority_rate = task_metrics.get('high_priority_completion_rate', 0)
            task_score = (task_completion_rate * 0.7 + high_priority_rate * 0.3)
            scores.append(task_score * 0.4)
            
            # Calendar utilization score (30% weight)
            utilization_rate = calendar_metrics.get('utilization_rate', 0)
            # Optimal utilization is around 70-80%
            if utilization_rate <= 80:
                calendar_score = utilization_rate
            else:
                calendar_score = max(0, 100 - (utilization_rate - 80))
            scores.append(calendar_score * 0.3)
            
            # Reminder effectiveness score (30% weight)
            reminder_effectiveness = reminder_metrics.get('effectiveness_rate', 0)
            scores.append(reminder_effectiveness * 0.3)
            
            overall_score = sum(scores)
            return round(min(100, max(0, overall_score)), 1)
            
        except Exception as e:
            logger.error(f"Error calculating productivity score: {e}")
            return 0.0
    
    def _generate_insights(self, task_metrics: Dict, calendar_metrics: Dict, reminder_metrics: Dict) -> List[ProductivityInsight]:
        """Generate productivity insights"""
        insights = []
        
        try:
            # Task completion insights
            completion_rate = task_metrics.get('completion_rate', 0)
            if completion_rate >= 80:
                insights.append(ProductivityInsight(
                    metric=ProductivityMetric.TASK_COMPLETION_RATE,
                    value=completion_rate,
                    trend="stable",
                    recommendation="Great job maintaining high task completion! Keep up the excellent work.",
                    confidence=0.9,
                    period="current"
                ))
            elif completion_rate >= 60:
                insights.append(ProductivityInsight(
                    metric=ProductivityMetric.TASK_COMPLETION_RATE,
                    value=completion_rate,
                    trend="stable",
                    recommendation="Good task completion rate. Consider prioritizing high-impact tasks.",
                    confidence=0.8,
                    period="current"
                ))
            else:
                insights.append(ProductivityInsight(
                    metric=ProductivityMetric.TASK_COMPLETION_RATE,
                    value=completion_rate,
                    trend="declining",
                    recommendation="Task completion could be improved. Try breaking large tasks into smaller ones.",
                    confidence=0.7,
                    period="current"
                ))
            
            # Calendar utilization insights
            utilization_rate = calendar_metrics.get('utilization_rate', 0)
            if utilization_rate > 90:
                insights.append(ProductivityInsight(
                    metric=ProductivityMetric.FOCUS_TIME,
                    value=utilization_rate,
                    trend="declining",
                    recommendation="Your calendar is very full. Consider blocking time for focused work.",
                    confidence=0.8,
                    period="current"
                ))
            elif utilization_rate < 40:
                insights.append(ProductivityInsight(
                    metric=ProductivityMetric.FOCUS_TIME,
                    value=utilization_rate,
                    trend="stable",
                    recommendation="You have good availability. Consider scheduling more strategic activities.",
                    confidence=0.7,
                    period="current"
                ))
            
            # Reminder effectiveness insights
            reminder_effectiveness = reminder_metrics.get('effectiveness_rate', 0)
            if reminder_effectiveness < 60:
                insights.append(ProductivityInsight(
                    metric=ProductivityMetric.BREAK_FREQUENCY,
                    value=reminder_effectiveness,
                    trend="declining",
                    recommendation="Consider adjusting reminder timing or reducing reminder frequency.",
                    confidence=0.6,
                    period="current"
                ))
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
        
        return insights
    
    def _generate_recommendations(self, productivity_score: float, insights: List[ProductivityInsight]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            if productivity_score >= 80:
                recommendations.extend([
                    "🎉 Excellent productivity! You're performing at a high level.",
                    "💡 Consider mentoring others or taking on stretch goals.",
                    "🔄 Maintain your current systems and routines."
                ])
            elif productivity_score >= 60:
                recommendations.extend([
                    "👍 Good productivity levels with room for improvement.",
                    "📋 Focus on completing high-priority tasks first.",
                    "⏰ Consider time-blocking for better focus.",
                    "🎯 Set specific daily goals to increase completion rates."
                ])
            else:
                recommendations.extend([
                    "🚀 Let's boost your productivity! Start with small wins.",
                    "📝 Break large tasks into smaller, manageable pieces.",
                    "⏱️ Use the Pomodoro technique for better focus.",
                    "🎯 Prioritize 2-3 important tasks per day.",
                    "📱 Consider reducing distractions during work time."
                ])
            
            # Add specific recommendations from insights
            for insight in insights:
                if insight.recommendation not in [r.split(' ', 1)[1] if ' ' in r else r for r in recommendations]:
                    recommendations.append(f"💡 {insight.recommendation}")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    def get_productivity_summary(self, user_id: str) -> str:
        """Get a brief productivity summary"""
        try:
            analysis = self.analyze_user_productivity(user_id, days_back=7)
            
            if 'error' in analysis:
                return "I couldn't analyze your productivity right now."
            
            score = analysis.get('productivity_score', 0)
            task_metrics = analysis.get('metrics', {}).get('tasks', {})
            
            completion_rate = task_metrics.get('completion_rate', 0)
            total_tasks = task_metrics.get('total_tasks', 0)
            
            if score >= 80:
                performance = "excellent"
                emoji = "🌟"
            elif score >= 60:
                performance = "good"
                emoji = "👍"
            else:
                performance = "needs improvement"
                emoji = "📈"
            
            summary = f"""{emoji} Your productivity this week is {performance}!
            
📊 Productivity Score: {score}/100
📋 Task Completion: {completion_rate}% ({task_metrics.get('completed_tasks', 0)}/{total_tasks} tasks)
📅 Calendar Utilization: {analysis.get('metrics', {}).get('calendar', {}).get('utilization_rate', 0)}%

{analysis.get('recommendations', ['Keep up the great work!'])[0]}"""
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting productivity summary: {e}")
            return "I encountered an error while analyzing your productivity."