import numpy as np
from typing import Dict, List
import logging
from scipy.optimize import linear_sum_assignment

class CrisisManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.resource_levels = {}
        self.critical_thresholds = {
            'oxygen': 0.2,
            'water': 0.15,
            'power': 0.1
        }

    def analyze_situation(self, telemetry_data: Dict) -> Dict:
        try:
            risk_levels = self._calculate_risk_levels(telemetry_data)
            response_plan = self._generate_response_plan(risk_levels)
            
            return {
                'risk_assessment': risk_levels,
                'response_plan': response_plan,
                'estimated_resolution_time': self._estimate_resolution_time(risk_levels)
            }
        except Exception as e:
            self.logger.error(f"Crisis analysis failed: {str(e)}")
            raise

    def _calculate_risk_levels(self, telemetry_data: Dict) -> Dict:
        risk_levels = {}
        for resource, current_level in telemetry_data.items():
            if resource in self.critical_thresholds:
                threshold = self.critical_thresholds[resource]
                risk_levels[resource] = max(0, threshold - current_level) / threshold
        return risk_levels

    def _generate_response_plan(self, risk_levels: Dict) -> List[Dict]:
        prioritized_actions = []
        for resource, risk in sorted(risk_levels.items(), key=lambda x: x[1], reverse=True):
            if risk > 0:
                prioritized_actions.append({
                    'resource': resource,
                    'action': self._determine_action(resource, risk),
                    'priority': risk
                })
        return prioritized_actions

    def _determine_action(self, resource: str, risk_level: float) -> str:
        if risk_level > 0.8:
            return f"IMMEDIATE: Emergency {resource} restoration required"
        elif risk_level > 0.5:
            return f"URGENT: Initiate {resource} recovery protocol"
        else:
            return f"MONITOR: Optimize {resource} usage"

    def _estimate_resolution_time(self, risk_levels: Dict) -> float:
        return max(risk_levels.values()) * 60  # minutes