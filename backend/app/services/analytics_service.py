from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from app.models.student import StudentKnowledgeProfile, LearningSession

class AdvancedAnalyticsService:
    """
    Advanced analytics service for comprehensive learning insights
    """
    
    def __init__(self):
        self.learning_sessions = {}  # student_id -> List[LearningSession]
        self.interaction_logs = {}   # student_id -> List[interaction_data]
        self.cohort_data = {}        # cohort_id -> cohort_analytics
        
    def track_learning_session(self, session: LearningSession):
        """Track a learning session for analytics"""
        if session.student_id not in self.learning_sessions:
            self.learning_sessions[session.student_id] = []
        
        self.learning_sessions[session.student_id].append(session)
    
    def generate_student_analytics(self, student_id: str, 
                                 time_period: int = 30) -> Dict:
        """Generate comprehensive analytics for a student"""
        
        # Get recent sessions
        cutoff_date = datetime.now() - timedelta(days=time_period)
        recent_sessions = [
            session for session in self.learning_sessions.get(student_id, [])
            if session.start_time >= cutoff_date
        ]
        
        if not recent_sessions:
            return self._empty_analytics()
        
        analytics = {
            'student_id': student_id,
            'time_period_days': time_period,
            'learning_metrics': self._calculate_learning_metrics(recent_sessions),
            'engagement_analysis': self._analyze_engagement(recent_sessions),
            'progress_tracking': self._track_progress(recent_sessions),
            'learning_patterns': self._identify_learning_patterns(recent_sessions),
            'recommendations': self._generate_recommendations(recent_sessions),
            'performance_trends': self._calculate_performance_trends(recent_sessions),
            'time_analysis': self._analyze_time_usage(recent_sessions)
        }
        
        return analytics
    
    def generate_cohort_heatmap(self, cohort_students: List[str], 
                              topics: List[str]) -> Dict:
        """Generate cohort performance heatmap"""
        
        heatmap_data = {}
        
        for topic in topics:
            topic_scores = []
            student_scores = {}
            
            for student_id in cohort_students:
                sessions = self.learning_sessions.get(student_id, [])
                topic_sessions = [s for s in sessions if topic in s.learning_progress]
                
                if topic_sessions:
                    # Calculate average progress for this topic
                    progress_scores = [
                        s.learning_progress.get(topic, 0) 
                        for s in topic_sessions
                    ]
                    avg_score = statistics.mean(progress_scores) if progress_scores else 0
                else:
                    avg_score = 0
                
                student_scores[student_id] = avg_score
                topic_scores.append(avg_score)
            
            heatmap_data[topic] = {
                'student_scores': student_scores,
                'cohort_average': statistics.mean(topic_scores) if topic_scores else 0,
                'cohort_median': statistics.median(topic_scores) if topic_scores else 0,
                'score_distribution': self._calculate_distribution(topic_scores)
            }
        
        return {
            'heatmap_data': heatmap_data,
            'cohort_size': len(cohort_students),
            'topics_analyzed': len(topics),
            'generated_at': datetime.now().isoformat()
        }
    
    def predict_at_risk_students(self, student_ids: List[str]) -> List[Dict]:
        """Predict students at risk of falling behind"""
        
        at_risk_students = []
        
        for student_id in student_ids:
            risk_score = self._calculate_risk_score(student_id)
            
            if risk_score > 0.6:  # High risk threshold
                risk_factors = self._identify_risk_factors(student_id)
                
                at_risk_students.append({
                    'student_id': student_id,
                    'risk_score': risk_score,
                    'risk_level': self._get_risk_level(risk_score),
                    'risk_factors': risk_factors,
                    'recommended_interventions': self._recommend_interventions(risk_factors),
                    'predicted_outcome': self._predict_outcome(risk_score)
                })
        
        # Sort by risk score (highest first)
        at_risk_students.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return at_risk_students
    
    def generate_engagement_report(self, student_ids: List[str], 
                                 time_period: int = 7) -> Dict:
        """Generate detailed engagement report"""
        
        cutoff_date = datetime.now() - timedelta(days=time_period)
        engagement_data = {}
        
        for student_id in student_ids:
            sessions = [
                s for s in self.learning_sessions.get(student_id, [])
                if s.start_time >= cutoff_date
            ]
            
            if sessions:
                engagement_metrics = {
                    'total_sessions': len(sessions),
                    'total_time_minutes': sum(
                        (s.end_time - s.start_time).total_seconds() / 60
                        for s in sessions if s.end_time
                    ),
                    'average_session_length': self._calculate_avg_session_length(sessions),
                    'engagement_score': statistics.mean([s.engagement_score for s in sessions]),
                    'activity_diversity': len(set(
                        activity for s in sessions for activity in s.activities
                    )),
                    'consistency_score': self._calculate_consistency_score(sessions),
                    'peak_activity_hours': self._identify_peak_hours(sessions)
                }
            else:
                engagement_metrics = self._empty_engagement_metrics()
            
            engagement_data[student_id] = engagement_metrics
        
        # Calculate cohort statistics
        cohort_stats = self._calculate_cohort_engagement_stats(engagement_data)
        
        return {
            'individual_engagement': engagement_data,
            'cohort_statistics': cohort_stats,
            'time_period_days': time_period,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_learning_metrics(self, sessions: List[LearningSession]) -> Dict:
        """Calculate comprehensive learning metrics"""
        
        total_time = sum(
            (s.end_time - s.start_time).total_seconds() / 3600
            for s in sessions if s.end_time
        )
        
        all_progress = []
        topic_progress = defaultdict(list)
        
        for session in sessions:
            for topic, progress in session.learning_progress.items():
                all_progress.append(progress)
                topic_progress[topic].append(progress)
        
        return {
            'total_learning_hours': round(total_time, 2),
            'total_sessions': len(sessions),
            'average_progress_per_session': statistics.mean(all_progress) if all_progress else 0,
            'topics_studied': len(topic_progress),
            'topic_mastery_levels': {
                topic: statistics.mean(progress_list)
                for topic, progress_list in topic_progress.items()
            },
            'learning_velocity': self._calculate_learning_velocity(sessions),
            'consistency_index': self._calculate_consistency_index(sessions)
        }
    
    def _analyze_engagement(self, sessions: List[LearningSession]) -> Dict:
        """Analyze student engagement patterns"""
        
        engagement_scores = [s.engagement_score for s in sessions]
        activity_counts = defaultdict(int)
        
        for session in sessions:
            for activity in session.activities:
                activity_counts[activity] += 1
        
        return {
            'average_engagement': statistics.mean(engagement_scores) if engagement_scores else 0,
            'engagement_trend': self._calculate_trend(engagement_scores),
            'most_engaging_activities': sorted(
                activity_counts.items(), key=lambda x: x[1], reverse=True
            )[:3],
            'engagement_consistency': statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0,
            'peak_engagement_sessions': [
                i for i, score in enumerate(engagement_scores) if score > 0.8
            ]
        }
    
    def _track_progress(self, sessions: List[LearningSession]) -> Dict:
        """Track learning progress over time"""
        
        progress_timeline = []
        cumulative_progress = defaultdict(float)
        
        for session in sessions:
            session_progress = {}
            for topic, progress in session.learning_progress.items():
                cumulative_progress[topic] += progress
                session_progress[topic] = cumulative_progress[topic]
            
            progress_timeline.append({
                'date': session.start_time.date().isoformat(),
                'session_progress': session_progress,
                'overall_progress': sum(session_progress.values()) / len(session_progress) if session_progress else 0
            })
        
        return {
            'progress_timeline': progress_timeline,
            'total_progress_by_topic': dict(cumulative_progress),
            'overall_progress_rate': self._calculate_progress_rate(progress_timeline),
            'milestone_achievements': self._identify_milestones(cumulative_progress)
        }
    
    def _identify_learning_patterns(self, sessions: List[LearningSession]) -> Dict:
        """Identify learning patterns and preferences"""
        
        # Time-based patterns
        hour_activity = defaultdict(int)
        day_activity = defaultdict(int)
        
        for session in sessions:
            hour_activity[session.start_time.hour] += 1
            day_activity[session.start_time.strftime('%A')] += 1
        
        # Activity preferences
        activity_time = defaultdict(float)
        for session in sessions:
            if session.end_time:
                session_duration = (session.end_time - session.start_time).total_seconds() / 60
                for activity in session.activities:
                    activity_time[activity] += session_duration / len(session.activities)
        
        return {
            'preferred_study_hours': sorted(hour_activity.items(), key=lambda x: x[1], reverse=True)[:3],
            'preferred_study_days': sorted(day_activity.items(), key=lambda x: x[1], reverse=True)[:3],
            'activity_time_distribution': dict(activity_time),
            'session_length_preference': self._analyze_session_lengths(sessions),
            'learning_rhythm': self._identify_learning_rhythm(sessions)
        }
    
    def _generate_recommendations(self, sessions: List[LearningSession]) -> List[str]:
        """Generate personalized recommendations based on analytics"""
        
        recommendations = []
        
        # Analyze recent performance
        recent_engagement = statistics.mean([s.engagement_score for s in sessions[-5:]])
        
        if recent_engagement < 0.5:
            recommendations.append("Consider taking shorter, more frequent study sessions to improve engagement")
            recommendations.append("Try different learning activities to find what works best for you")
        
        # Analyze consistency
        session_gaps = self._calculate_session_gaps(sessions)
        if statistics.mean(session_gaps) > 3:  # More than 3 days between sessions
            recommendations.append("Try to maintain more consistent study schedule for better retention")
        
        # Analyze topic balance
        topic_progress = defaultdict(list)
        for session in sessions:
            for topic, progress in session.learning_progress.items():
                topic_progress[topic].append(progress)
        
        if len(topic_progress) > 1:
            topic_averages = {topic: statistics.mean(progress) for topic, progress in topic_progress.items()}
            min_topic = min(topic_averages, key=topic_averages.get)
            max_topic = max(topic_averages, key=topic_averages.get)
            
            if topic_averages[max_topic] - topic_averages[min_topic] > 0.3:
                recommendations.append(f"Focus more attention on {min_topic} to balance your learning")
        
        return recommendations
    
    def _calculate_risk_score(self, student_id: str) -> float:
        """Calculate risk score for a student (0-1, higher = more risk)"""
        
        sessions = self.learning_sessions.get(student_id, [])
        if not sessions:
            return 1.0  # No activity = high risk
        
        recent_sessions = [
            s for s in sessions 
            if s.start_time >= datetime.now() - timedelta(days=14)
        ]
        
        risk_factors = []
        
        # Factor 1: Recent activity
        if len(recent_sessions) == 0:
            risk_factors.append(0.8)  # No recent activity
        elif len(recent_sessions) < 3:
            risk_factors.append(0.5)  # Low activity
        else:
            risk_factors.append(0.1)  # Good activity
        
        # Factor 2: Engagement trend
        if recent_sessions:
            engagement_scores = [s.engagement_score for s in recent_sessions]
            avg_engagement = statistics.mean(engagement_scores)
            if avg_engagement < 0.3:
                risk_factors.append(0.7)
            elif avg_engagement < 0.5:
                risk_factors.append(0.4)
            else:
                risk_factors.append(0.1)
        else:
            risk_factors.append(0.8)
        
        # Factor 3: Progress rate
        if len(sessions) > 1:
            progress_values = []
            for session in sessions:
                if session.learning_progress:
                    progress_values.append(sum(session.learning_progress.values()) / len(session.learning_progress))
            
            if progress_values:
                recent_progress = statistics.mean(progress_values[-3:]) if len(progress_values) >= 3 else statistics.mean(progress_values)
                if recent_progress < 0.2:
                    risk_factors.append(0.6)
                elif recent_progress < 0.4:
                    risk_factors.append(0.3)
                else:
                    risk_factors.append(0.1)
            else:
                risk_factors.append(0.5)
        else:
            risk_factors.append(0.4)
        
        return statistics.mean(risk_factors)
    
    def _empty_analytics(self) -> Dict:
        """Return empty analytics structure"""
        return {
            'learning_metrics': {},
            'engagement_analysis': {},
            'progress_tracking': {},
            'learning_patterns': {},
            'recommendations': ["Start learning to see personalized insights!"],
            'performance_trends': {},
            'time_analysis': {}
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = list(range(len(values)))
        correlation = np.corrcoef(x, values)[0, 1] if len(values) > 1 else 0
        
        if correlation > 0.3:
            return "improving"
        elif correlation < -0.3:
            return "declining"
        else:
            return "stable"
    
    def _calculate_learning_velocity(self, sessions: List[LearningSession]) -> float:
        """Calculate how quickly student is learning"""
        if len(sessions) < 2:
            return 0.0
        
        progress_over_time = []
        for session in sessions:
            if session.learning_progress:
                avg_progress = sum(session.learning_progress.values()) / len(session.learning_progress)
                progress_over_time.append(avg_progress)
        
        if len(progress_over_time) < 2:
            return 0.0
        
        # Calculate slope of progress over time
        x = list(range(len(progress_over_time)))
        velocity = np.polyfit(x, progress_over_time, 1)[0] if len(progress_over_time) > 1 else 0
        
        return max(0, velocity)  # Ensure non-negative

# Global instance
analytics_service = AdvancedAnalyticsService()