import numpy as np
from typing import Dict, List
import logging
from sklearn.preprocessing import StandardScaler

class WellbeingAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.psychological_factors = [
            'stress_level',
            'sleep_quality',
            'social_interaction',
            'cognitive_performance'
        ]

    def analyze_wellbeing(self, crew_data: Dict) -> Dict:
        try:
            psychological_scores = self._analyze_psychological_state(crew_data)
            physical_scores = self._analyze_physical_state(crew_data)
            social_scores = self._analyze_social_dynamics(crew_data)
            
            return {
                'psychological_assessment': psychological_scores,
                'physical_assessment': physical_scores,
                'social_assessment': social_scores,
                'overall_wellbeing_score': self._calculate_overall_score(
                    psychological_scores,
                    physical_scores,
                    social_scores
                )
            }
        except Exception as e:
            self.logger.error(f"Wellbeing analysis failed: {str(e)}")
            raise

    def _analyze_psychological_state(self, data: Dict) -> Dict:
        scores = {}
        for factor in self.psychological_factors:
            if factor in data:
                scores[factor] = self._normalize_score(data[factor])
        return scores

    def _analyze_physical_state(self, data: Dict) -> Dict:
        physical_metrics = {
            'heart_rate': data.get('heart_rate', 0),
            'blood_pressure': data.get('blood_pressure', 0),
            'sleep_hours': data.get('sleep_hours', 0),
            'exercise_minutes': data.get('exercise_minutes', 0)
        }
        return {k: self._normalize_score(v) for k, v in physical_metrics.items()}

    def _analyze_social_dynamics(self, data: Dict) -> Dict:
        return {
            'team_cohesion': self._calculate_cohesion(data),
            'communication_quality': self._assess_communication(data),
            'social_support': self._evaluate_support(data)
        }

    def _normalize_score(self, value: float) -> float:
        return max(0, min(1, value / 100))

    def _calculate_cohesion(self, data: Dict) -> float:
        interaction_frequency = data.get('interaction_frequency', 0)
        team_activities = data.get('team_activities', 0)
        return np.mean([interaction_frequency, team_activities]) / 100

    def _assess_communication(self, data: Dict) -> float:
        return data.get('communication_quality', 0) / 100

    def _evaluate_support(self, data: Dict) -> float:
        return data.get('social_support', 0) / 100

    def _calculate_overall_score(self, psych: Dict, phys: Dict, social: Dict) -> float:
        scores = [
            np.mean(list(psych.values())),
            np.mean(list(phys.values())),
            np.mean(list(social.values()))
        ]
        return np.mean(scores)