import torch
import torch.nn as nn
from models import HabitatGAN
import numpy as np
from typing import Dict, Tuple
import logging

class HabitatDesigner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gan = HabitatGAN()
        self.optimizer = torch.optim.Adam(self.gan.parameters(), lr=0.0002)
        
    def generate_design(self, constraints: Dict) -> Dict:
        try:
            noise = torch.randn(1, 100)
            design = self.gan.generator(noise)
            
            # Validate design against constraints
            valid = self._validate_design(design.detach().numpy(), constraints)
            if not valid:
                self.logger.warning("Generated design does not meet constraints")
                return self._optimize_design(design, constraints)
                
            return {
                'layout': design.detach().numpy(),
                'metrics': self._calculate_metrics(design)
            }
        except Exception as e:
            self.logger.error(f"Design generation failed: {str(e)}")
            raise

    def _validate_design(self, design: np.ndarray, constraints: Dict) -> bool:
        space_efficiency = self._calculate_space_efficiency(design)
        return space_efficiency > constraints.get('min_efficiency', 0.7)

    def _optimize_design(self, design: torch.Tensor, constraints: Dict) -> Dict:
        for _ in range(100):
            self.optimizer.zero_grad()
            loss = self._calculate_constraint_loss(design, constraints)
            loss.backward()
            self.optimizer.step()
        return {'layout': design.detach().numpy()}

    def _calculate_metrics(self, design: torch.Tensor) -> Dict:
        return {
            'space_efficiency': self._calculate_space_efficiency(design.detach().numpy()),
            'structural_integrity': self._calculate_structural_integrity(design.detach().numpy())
        }

    def _calculate_space_efficiency(self, design: np.ndarray) -> float:
        return float(np.mean(design > 0))

    def _calculate_structural_integrity(self, design: np.ndarray) -> float:
        return float(np.min(np.abs(design)))