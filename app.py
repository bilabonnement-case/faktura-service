from flask import Flask, jsonify, request
import os
from datetime import datetime
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flasgger import Swagger, swag_from
from uuid import uuid4
from enum import Enum

# Load environment variables
load_dotenv()

app = Flask(__name__)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
PORT = int(os.getenv('PORT', 5001))
jwt = JWTManager(app)

# Swagger Configuration
app.config['SWAGGER'] = {
    'title': 'Fakturering Microservice API',
    'uiversion': 3,  # Use Swagger UI v3
    'openapi': '3.0.0'
}
swagger = Swagger(app)

# Enum for Faktura Status
class FakturaStatus(str, Enum):
    IKKE_BETALT = "Ikke betalt"
    BETALT = "Betalt"
    FORFALDEN = "Forfalden"

# Simuleret database
invoices = []

@app.route('/')
@swag_from('swagger/home.yaml')
def home():
    return jsonify({
        "service": "Fakturering-Service",
        "available_endpoints": [
            {"path": "/create_invoice", "method": "POST", "description": "Opret ny faktura"},
            {"path": "/get_invoice/<faktura_id>", "method": "GET", "description": "Hent faktura baseret på FakturaID"},
            {"path": "/update_status/<faktura_id>", "method": "PUT", "description": "Opdater fakturastatus"},
            {"path": "/report", "method": "GET", "description": "Få samlet fakturarapportering"},
        ]
    })

# Endpoint for oprettelse af faktura
@app.route('/create_invoice', methods=['POST'])
@jwt_required()
@swag_from('swagger/create_invoice.yaml')
def create_invoice():
    try:
        data = request.get_json()
        invoice = {
            "FakturaID": str(uuid4()),
            "AbonnementsID": data.get("AbonnementsID"),
            "KundeID": data.get("KundeID"),
            "Beløb": data.get("Beløb"),
            "Betalingsdato": data.get("Betalingsdato"),
            "Status": FakturaStatus.IKKE_BETALT.value,
            "OprettetAf": get_jwt_identity(),
            "OprettetTidspunkt": datetime.now().isoformat()
        }
        invoices.append(invoice)
        return jsonify({"message": "Faktura oprettet", "invoice": invoice}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400

# Endpoint for hentning af faktura
@app.route('/get_invoice/<faktura_id>', methods=['GET'])
@jwt_required()
@swag_from('swagger/get_invoice.yaml')
def get_invoice(faktura_id):
    invoice = next((inv for inv in invoices if inv["FakturaID"] == faktura_id), None)
    if invoice:
        return jsonify(invoice), 200
    return jsonify({"error": "Faktura ikke fundet"}), 404

# Endpoint for opdatering af fakturastatus
@app.route('/update_status/<faktura_id>', methods=['PUT'])
@jwt_required()
@swag_from('swagger/update_status.yaml')
def update_status(faktura_id):
    try:
        data = request.get_json()
        status = data.get("Status")
        if status not in FakturaStatus._value2member_map_:
            return jsonify({"error": "Ugyldig status"}), 400
        invoice = next((inv for inv in invoices if inv["FakturaID"] == faktura_id), None)
        if invoice:
            invoice["Status"] = status
            return jsonify({"message": "Status opdateret", "invoice": invoice}), 200
        return jsonify({"error": "Faktura ikke fundet"}), 404
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400

# Endpoint for rapportering
@app.route('/report', methods=['GET'])
@jwt_required()
@swag_from('swagger/report.yaml')
def report():
    total_beloeb = sum([inv["Beløb"] for inv in invoices if inv["Status"] == FakturaStatus.BETALT.value])
    unpaid_invoices = len([inv for inv in invoices if inv["Status"] == FakturaStatus.IKKE_BETALT.value])
    overdue_invoices = len([inv for inv in invoices if inv["Status"] == FakturaStatus.FORFALDEN.value])

    report_data = {
        "TotalBetalt": total_beloeb,
        "UbetalteFakturaer": unpaid_invoices,
        "ForfaldneFakturaer": overdue_invoices,
        "TotalFakturaer": len(invoices)
    }
    return jsonify(report_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)