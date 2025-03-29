import numpy as np
from typing import Dict, List, Any, Union
import logging
import json
import os
from datetime import datetime

class DataValidator:
    @staticmethod
    def validate_numeric_range(value: float, min_val: float, max_val: float) -> bool:
        return min_val <= value <= max_val

    @staticmethod
    def validate_dict_keys(data: Dict, required_keys: List[str]) -> bool:
        return all(key in data for key in required_keys)

class DataProcessor:
    @staticmethod
    def normalize_array(data: np.ndarray) -> np.ndarray:
        return (data - np.min(data)) / (np.max(data) - np.min(data) + 1e-8)

    @staticmethod
    def smooth_data(data: np.ndarray, window_size: int = 3) -> np.ndarray:
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

class FileHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def save_data(self, data: Dict, filename: str) -> bool:
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save data: {str(e)}")
            return False

    def load_data(self, filename: str) -> Union[Dict, None]:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load data: {str(e)}")
            return None

class MetricsCalculator:
    @staticmethod
    def calculate_sustainability_score(
        resource_usage: Dict,
        efficiency: float,
        recycling_rate: float
    ) -> float:
        base_score = np.mean([
            efficiency,
            recycling_rate,
            1 - np.mean(list(resource_usage.values()))
        ])
        return float(np.clip(base_score, 0, 1))

    @staticmethod
    def calculate_structural_integrity_index(
        stress_factors: Dict,
        material_properties: Dict
    ) -> float:
        weighted_factors = sum(
            stress * material_properties.get('strength', 1)
            for stress in stress_factors.values()
        )
        return float(np.exp(-weighted_factors))

class Logger:
    def __init__(self, log_file: str = "space_habitat.log"):
        self.logger = logging.getLogger(__name__)
        self.log_file = log_file
        self._setup_logger()

    def _setup_logger(self):
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

    def log_event(self, message: str, level: str = "info"):
        getattr(self.logger, level)(message)