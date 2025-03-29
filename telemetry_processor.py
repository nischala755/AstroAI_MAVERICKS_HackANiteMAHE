import numpy as np
from typing import Dict, List
import logging
from scipy.signal import savgol_filter

class TelemetryProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_buffer = {}
        
    def process_telemetry(self, data: Dict) -> Dict:
        try:
            processed_data = {}
            for key, values in data.items():
                if len(values) >= 3:  # Ensure minimum length for processing
                    processed_data[key] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'trend': self._calculate_trend(values),
                        'smoothed': self._smooth_data(values)
                    }
                else:
                    processed_data[key] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'trend': 0.0,
                        'smoothed': values
                    }
            
            return {
                'processed_telemetry': processed_data,
                'status': 'success',
                'timestamp': np.datetime64('now').astype(str)
            }
        except Exception as e:
            self.logger.error(f"Telemetry processing failed: {str(e)}")
            raise

    def _smooth_data(self, data: List[float]) -> List[float]:
        if len(data) < 3:
            return data
        return np.convolve(data, [0.3, 0.4, 0.3], 'same').tolist()

    def _calculate_trend(self, data: List[float]) -> float:
        if len(data) < 2:
            return 0.0
        return (data[-1] - data[0]) / len(data)