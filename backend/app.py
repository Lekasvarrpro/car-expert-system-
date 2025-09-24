from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# ------------------------------
# Brands and Models
# ------------------------------
car_options = {
    "Toyota": ["Corolla", "Camry", "Fortuner", "Innova", "Yaris"],
    "Honda": ["Civic", "Accord", "City", "CR-V", "Jazz"],
    "Hyundai": ["i10", "i20", "Creta", "Verna", "Tucson"],
    "Ford": ["Figo", "EcoSport", "Endeavour", "Mustang"],
    "BMW": ["3 Series", "5 Series", "X1", "X3", "X5"],
    "Mercedes": ["C-Class", "E-Class", "GLA", "GLC", "S-Class"],
    "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7"],
    "Volkswagen": ["Polo", "Vento", "Jetta", "Passat", "Tiguan"],
    "Nissan": ["Micra", "Sunny", "Kicks", "Magnite", "Terrano"],
    "Renault": ["Kwid", "Triber", "Duster", "Captur"],
    "Kia": ["Seltos", "Sonet", "Carens", "EV6"],
    "Tata": ["Nano", "Tiago", "Altroz", "Harrier", "Safari", "Punch"],
    "Mahindra": ["Thar", "XUV300", "XUV500", "Scorpio", "Bolero"],
    "Jeep": ["Compass", "Wrangler", "Cherokee", "Grand Cherokee"],
    "Skoda": ["Rapid", "Octavia", "Superb", "Kushaq"],
    "MarutiSuzuki": ["Alto", "Swift", "Baleno", "Dzire", "Celerio", "Ertiga"],
    "Volvo": ["XC40", "XC60", "XC90", "S60", "S90"],
    "Jaguar": ["XE", "XF", "F-Pace", "F-Type"],
    "LandRover": ["Discovery", "Range Rover Evoque", "Range Rover Sport"],
    "Lexus": ["ES", "LS", "NX", "RX"],
    "Mitsubishi": ["Pajero", "Outlander", "Lancer"],
    "Chevrolet": ["Spark", "Beat", "Cruze", "Trailblazer"],
    "Fiat": ["Punto", "Linea", "500", "Tipo"],
    "Peugeot": ["208", "308", "2008", "3008"],
    "Citroen": ["C3", "C5 Aircross", "Berlingo"],
    "Subaru": ["Impreza", "Forester", "Outback", "WRX"],
    "Porsche": ["Cayenne", "Macan", "Panamera", "911"],
    "Ferrari": ["488", "F8 Tributo", "Roma", "SF90"],
    "Lamborghini": ["Huracan", "Aventador", "Urus"],
    "Maserati": ["Ghibli", "Levante", "Quattroporte"],
    "RollsRoyce": ["Phantom", "Ghost", "Cullinan"],
    "Bentley": ["Continental GT", "Flying Spur", "Bentayga"],
}

# ------------------------------
# Symptoms → Cause + Solution
# ------------------------------
diagnosis_map = {
    "Fuel empty / low fuel": {"cause": "The car is out of fuel or very low.", "solution": "Refuel the tank."},
    "Battery dead / weak": {"cause": "Battery is discharged or weak.", "solution": "Jumpstart or replace the battery."},
    "Car not starting": {"cause": "Car fails to start.", "solution": "Check battery, fuel, and starter motor."},
    "Overheating (coolant issue)": {"cause": "Engine coolant is low or radiator issue.", "solution": "Check coolant level, radiator, and thermostat."},
    "Brake failure / worn pads": {"cause": "Brake pads worn or fluid leakage.", "solution": "Replace brake pads and check brake fluid."},
    "Oil leak": {"cause": "Engine oil is leaking.", "solution": "Check gaskets, seals, and oil filter."},
    "Transmission slipping": {"cause": "Transmission fluid low or damaged gearbox.", "solution": "Refill/replace transmission fluid or service gearbox."},
    "Sensor failure": {"cause": "Faulty engine sensor.", "solution": "Run diagnostic scan and replace faulty sensor."},
    "ECU malfunction": {"cause": "Car's ECU not functioning properly.", "solution": "Reset or replace ECU after diagnostic."},
    "Hybrid battery degradation": {"cause": "Hybrid battery losing capacity.", "solution": "Replace or service the hybrid battery pack."},
    "EV charging issue": {"cause": "Charging port or cable fault.", "solution": "Inspect charging station, cable, and port."},
    "EV battery overheating": {"cause": "Battery temperature too high.", "solution": "Stop charging/driving and let battery cool down."},
}

# ------------------------------
# Symptom keywords for flexible matching
# ------------------------------
symptom_keywords = {
    "Fuel empty / low fuel": ["fuel", "gas", "empty tank", "low fuel"],
    "Battery dead / weak": ["battery", "dead battery", "weak battery", "won't start"],
    "Car not starting": ["not starting", "won't start", "cannot start", "fail start"],
    "Overheating (coolant issue)": ["overheating", "hot engine", "coolant", "temperature"],
    "Brake failure / worn pads": ["brake", "brakes", "brake failure", "pads worn"],
    "Oil leak": ["oil leak", "engine oil", "oil dripping", "oil problem"],
    "Transmission slipping": ["transmission", "gearbox", "slipping gears"],
    "Sensor failure": ["sensor", "check engine light", "malfunction"],
    "ECU malfunction": ["ecu", "computer issue", "engine control"],
    "Hybrid battery degradation": ["hybrid battery", "hybrid issue"],
    "EV charging issue": ["charging", "ev charge", "charge issue"],
    "EV battery overheating": ["ev battery", "battery hot", "overheating battery"],
}

# ------------------------------
# Helper: parse free-text query
# ------------------------------
def parse_query(query):
    query = query.lower()
    brand_found = None
    model_found = None
    symptoms_found = []

    # Detect brand & model
    for brand, models in car_options.items():
        if brand.lower() in query:
            brand_found = brand
            for model in models:
                if model.lower() in query:
                    model_found = model
                    break
            break

    # Detect symptoms using keywords
    for symptom, keywords in symptom_keywords.items():
        for kw in keywords:
            if kw in query:
                symptoms_found.append(symptom)
                break  # stop after first keyword match per symptom

    # Remove duplicates
    symptoms_found = list(set(symptoms_found))
    return brand_found, model_found, symptoms_found

# ------------------------------
# Route: free-text chat
# ------------------------------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get("query", "").lower()

    # --------------------------
    # Handle greetings
    # --------------------------
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(word in query for word in greetings):
        return jsonify({"reply": "👋 Hello! I’m here to help with your car issues. Please tell me your car problem."})

    # --------------------------
    # Detect issues
    # --------------------------
    brand, model, symptoms = parse_query(query)

    if not symptoms:
        # If no specific symptom detected, provide general advice
        return jsonify({
            "reply": "⚠️ Could not detect exact issue. Here are some general suggestions:\n"
                     "- Check battery and fuel.\n"
                     "- Inspect engine oil and coolant.\n"
                     "- Listen for unusual sounds while starting."
        })

    # Format diagnosis results
    results = [diagnosis_map[s] for s in symptoms if s in diagnosis_map]
    formatted = "\n\n".join([f"Cause: {r['cause']}\nSolution: {r['solution']}" for r in results])

    return jsonify({"reply": formatted})

# ------------------------------
# Route: brand-model-symptoms diagnosis
# ------------------------------
@app.route('/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    brand = data.get("brand")
    model = data.get("model")
    symptoms = data.get("symptoms", [])

    # Validate brand & model
    if brand not in car_options:
        return jsonify({"error": "Brand not found"}), 404
    if model not in car_options[brand]:
        return jsonify({"error": "Model not found for selected brand"}), 404

    # Validate symptoms
    results = [diagnosis_map[s] for s in symptoms if s in diagnosis_map]

    if not results:
        return jsonify({
            "cause": "Unknown issue.",
            "solution": "Please consult a mechanic for detailed diagnosis."
        })

    return jsonify({"results": results})

# ------------------------------
# Main
# ------------------------------
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)

    
