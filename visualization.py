import plotly.graph_objects as go
from typing import Dict, List
import logging
import numpy as np
from plotly.subplots import make_subplots

class Visualizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'warning': '#d62728',
            'success': '#2ca02c'
        }

    def create_dashboard(self, data: Dict) -> Dict:
        try:
            return {
                'habitat_3d': self._create_habitat_visualization(data['habitat']),
                'telemetry': self._create_telemetry_plots(data['telemetry']),
                'wellbeing': self._create_wellbeing_dashboard(data['wellbeing']),
                'resources': self._create_resource_charts(data['resources'])
            }
        except Exception as e:
            self.logger.error(f"Dashboard creation failed: {str(e)}")
            raise

    def _create_habitat_visualization(self, habitat_data: Dict) -> go.Figure:
        fig = go.Figure(data=[
            go.Mesh3d(
                x=habitat_data['vertices'][:, 0],
                y=habitat_data['vertices'][:, 1],
                z=habitat_data['vertices'][:, 2],
                i=habitat_data['faces'][:, 0],
                j=habitat_data['faces'][:, 1],
                k=habitat_data['faces'][:, 2],
                colorscale='Viridis',
                intensity=habitat_data['structural_integrity']
            )
        ])
        
        fig.update_layout(
            scene=dict(
                aspectmode='data',
                camera=dict(
                    up=dict(x=0, y=1, z=0),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            )
        )
        return fig

    def _create_telemetry_plots(self, telemetry_data: Dict) -> go.Figure:
        fig = make_subplots(rows=2, cols=2)
        
        metrics = ['temperature', 'pressure', 'oxygen', 'radiation']
        positions = [(1,1), (1,2), (2,1), (2,2)]
        
        for metric, pos in zip(metrics, positions):
            fig.add_trace(
                go.Scatter(
                    x=telemetry_data['time'],
                    y=telemetry_data[metric],
                    name=metric.capitalize()
                ),
                row=pos[0], col=pos[1]
            )
            
        return fig

    def _create_wellbeing_dashboard(self, wellbeing_data: Dict) -> go.Figure:
        fig = go.Figure(data=[
            go.Indicator(
                mode="gauge+number",
                value=wellbeing_data['overall_score'],
                title={'text': "Crew Wellbeing Index"},
                gauge={'axis': {'range': [0, 1]}}
            )
        ])
        return fig

    def _create_resource_charts(self, resource_data: Dict) -> go.Figure:
        fig = go.Figure(data=[
            go.Bar(
                x=list(resource_data.keys()),
                y=list(resource_data.values()),
                marker_color=self.color_scheme['primary']
            )
        ])
        return fig