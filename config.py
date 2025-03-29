import os
from typing import Dict, Any
import json

class Config:
    def __init__(self):
        self.config = {
            'SYSTEM': {
                'DEBUG_MODE': False,
                'LOG_LEVEL': 'INFO',
                'MAX_THREADS': 4,
                'SIMULATION_TIMESTEP': 0.1
            },
            'TELEMETRY': {
                'SAMPLING_RATE': 1.0,  # Hz
                'BUFFER_SIZE': 1000,
                'CRITICAL_PARAMETERS': [
                    'temperature',
                    'pressure',
                    'oxygen_level',
                    'radiation'
                ]
            },
            'MATERIAL_SIMULATION': {
                'MAX_ITERATIONS': 1000,
                'CONVERGENCE_THRESHOLD': 1e-6,
                'SAFETY_FACTOR': 1.5
            },
            'HABITAT_DESIGN': {
                'MIN_VOLUME_PER_PERSON': 100,  # cubic meters
                'MAX_STRESS_TOLERANCE': 0.8,
                'OPTIMIZATION_EPOCHS': 500
            },
            'CRISIS_MANAGEMENT': {
                'RESPONSE_TIME_THRESHOLD': 300,  # seconds
                'ALERT_LEVELS': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
                'AUTO_RESPONSE_ENABLED': True
            },
            'DIGITAL_TWIN': {
                'UPDATE_FREQUENCY': 5.0,  # Hz
                'PREDICTION_HORIZON': 24,  # hours
                'STATE_VARIABLES': [
                    'structural_integrity',
                    'environmental_systems',
                    'power_systems',
                    'life_support'
                ]
            },
            'WELLBEING_ANALYSIS': {
                'ASSESSMENT_INTERVAL': 3600,  # seconds
                'MIN_WELLBEING_THRESHOLD': 0.7,
                'PSYCHOLOGICAL_WEIGHTS': {
                    'stress': 0.3,
                    'sleep': 0.3,
                    'social': 0.2,
                    'cognitive': 0.2
                }
            },
            'RESOURCE_LEDGER': {
                'BLOCK_SIZE': 100,
                'MINING_INTERVAL': 600,  # seconds
                'CONSENSUS_THRESHOLD': 0.75
            },
            'QUANTUM_OPTIMIZATION': {
                'NUM_QUBITS': 20,
                'ANNEALING_STEPS': 1000,
                'TEMPERATURE_SCHEDULE': 'exponential'
            },
            'VISUALIZATION': {
                'UPDATE_INTERVAL': 1.0,  # seconds
                'MAX_DATA_POINTS': 1000,
                'COLOR_SCHEME': {
                    'primary': '#1f77b4',
                    'secondary': '#ff7f0e',
                    'warning': '#d62728',
                    'success': '#2ca02c'
                }
            }
        }

    def get(self, key: str) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k)
            if value is None:
                return None
        return value

    def set(self, key: str, value: Any) -> bool:
        try:
            keys = key.split('.')
            target = self.config
            for k in keys[:-1]:
                target = target[k]
            target[keys[-1]] = value
            return True
        except Exception:
            return False

    def load_from_file(self, filepath: str) -> bool:
        try:
            with open(filepath, 'r') as f:
                self.config.update(json.load(f))
            return True
        except Exception:
            return False

    def save_to_file(self, filepath: str) -> bool:
        try:
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception:
            return False

    def get_all(self) -> Dict:
        return self.config.copy()

# Global configuration instance
config = Config()