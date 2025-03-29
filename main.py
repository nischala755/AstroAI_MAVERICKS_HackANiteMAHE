from flask import Flask, jsonify, request
from flask import render_template
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
from telemetry_processor import TelemetryProcessor
from material_simulator import MaterialSimulator
from habitat_designer import HabitatDesigner
from crisis_manager import CrisisManager
from digital_twin import DigitalTwin
from wellbeing_analyzer import WellbeingAnalyzer
from resource_ledger import ResourceLedger
from quantum_optimizer import QuantumOptimizer
from config import config

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
app.logger.addHandler(handler)

# Initialize components
try:
    telemetry = TelemetryProcessor()
    material_sim = MaterialSimulator()
    habitat = HabitatDesigner()
    crisis = CrisisManager()
    digital_twin = DigitalTwin()
    wellbeing = WellbeingAnalyzer()
    ledger = ResourceLedger()
    optimizer = QuantumOptimizer()
except Exception as e:
    logger.error(f"Failed to initialize components: {str(e)}")
    raise

@app.route('/api/health')
def health_check():
    return jsonify({"status": "operational", "version": "1.0.0"})


@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/telemetry', methods=['POST'])
def process_telemetry():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.json
        logger.info(f"Received telemetry data: {data}")
        
        result = telemetry.process_telemetry(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Telemetry processing error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/habitat/status')
def habitat_status():
    try:
        return jsonify({
            'structural_integrity': 0.95,
            'environmental_systems': 0.88,
            'power_systems': 0.92,
            'life_support': 0.90
        })
    except Exception as e:
        logger.error(f"Habitat status error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/crisis/check')
def crisis_check():
    try:
        return jsonify(crisis.analyze_situation({
            'oxygen': 0.8,
            'water': 0.85,
            'power': 0.9
        }))
    except Exception as e:
        logger.error(f"Crisis check error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/wellbeing/status')
def wellbeing_status():
    try:
        return jsonify(wellbeing.analyze_wellbeing({
            'stress_level': 0.3,
            'sleep_quality': 0.8,
            'social_interaction': 0.7,
            'cognitive_performance': 0.85
        }))
    except Exception as e:
        logger.error(f"Wellbeing status error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)