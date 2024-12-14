from flask import Flask, jsonify, request
import os
from datetime import datetime
from dotenv import load_dotenv
from flasgger import Swagger, swag_from
import sqlite3

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Swagger Configuration
app.config['SWAGGER'] = {
    'title': 'Fakturering Microservice API',
    'uiversion': 3,
    'openapi': '3.0.0'
}
swagger = Swagger(app)

# Database Opsætning
DATABASE = "database.db"


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Drop tabellen, hvis den allerede eksisterer
        ##cursor.execute("DROP TABLE IF EXISTS invoices")
        # Opret en tabel til fakturaer, hvis den ikke allerede findes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unikt ID for fakturaen
            abonnements_id INTEGER NOT NULL,      -- ID for abonnement
            kunde_id INTEGER NOT NULL,            -- ID for kunde
            beloeb REAL NOT NULL,                 -- Fakturabeløb
            betalingsdato DATETIME NOT NULL,      -- Betalingsdato
            status TEXT NOT NULL,                 -- Fakturastatus
            oprettet_tidspunkt DATETIME NOT NULL  -- Tidspunkt for oprettelse
        )
        """)
        conn.commit()


init_db()

# Enum for Faktura Status
class FakturaStatus:
    IKKE_BETALT = "Ikke betalt"
    BETALT = "Betalt"
    FORFALDEN = "Forfalden"


@app.route('/')
@swag_from('swagger/home.yaml')
def home():
    return jsonify({
        "service": "Fakturering-Service",
        "available_endpoints": [
            {"path": "/create_invoice", "method": "POST", "description": "Opret ny faktura"},
            {"path": "/get_invoice/<int:faktura_id>", "method": "GET", "description": "Hent faktura baseret på FakturaID"},
            {"path": "/update_status/<int:faktura_id>", "method": "PUT", "description": "Opdater fakturastatus"},
            {"path": "/report", "method": "GET", "description": "Få samlet fakturarapportering"},
        ]
    })


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/create_invoice', methods=['POST'])
@swag_from('swagger/create_invoice.yaml')
def create_invoice():
    try:
        # Hent JSON-data fra request
        data = request.get_json()

        # Brug små bogstaver for JSON-nøgler (som modtages i POST)
        abonnements_id = data.get("abonnements_id")
        kunde_id = data.get("kunde_id")
        beloeb = data.get("beloeb")
        betalingsdato = data.get("betalingsdato")
        # Standardstatus og oprettelsestidspunkt
        status = FakturaStatus.IKKE_BETALT
        oprettet_tidspunkt = datetime.now().isoformat()

        # Indsæt data i databasen
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO invoices (abonnements_id, kunde_id, beloeb, betalingsdato, status, oprettet_tidspunkt)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (abonnements_id, kunde_id, beloeb, betalingsdato, status, oprettet_tidspunkt))
            conn.commit()

            faktura_id = cursor.lastrowid

        return jsonify({"message": "Faktura oprettet", "invoice_id": faktura_id}), 201

    except Exception as e:
        # Log fejl og returner generisk fejl
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500


@app.route('/get_invoice/<int:faktura_id>', methods=['GET'])
@swag_from('swagger/get_invoice.yaml')
def get_invoice(faktura_id):
    with get_db_connection() as conn:
        invoice = conn.execute("SELECT * FROM invoices WHERE id = ?", (faktura_id,)).fetchone()

    if invoice is None:
        return jsonify({"error": "Faktura ikke fundet"}), 404

    return jsonify(dict(invoice)), 200


@app.route('/update_status/<int:faktura_id>', methods=['PUT'])
@swag_from('swagger/update_status.yaml')
def update_status(faktura_id):
    data = request.get_json()
    status = data.get("Status")

    if status not in [FakturaStatus.IKKE_BETALT, FakturaStatus.BETALT, FakturaStatus.FORFALDEN]:
        return jsonify({"error": "Ugyldig status"}), 400

    with get_db_connection() as conn:
        cursor = conn.cursor()
        result = cursor.execute("UPDATE invoices SET status = ? WHERE id = ?", (status, faktura_id))
        conn.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Faktura ikke fundet"}), 404

    return jsonify({"message": "Status opdateret"}), 200


@app.route('/report', methods=['GET'])
@swag_from('swagger/report.yaml')
def report():
    with get_db_connection() as conn:
        total_beloeb = conn.execute("SELECT SUM(beloeb) FROM invoices WHERE status = ?", (FakturaStatus.BETALT,)).fetchone()[0] or 0
        unpaid_invoices = conn.execute("SELECT COUNT(*) FROM invoices WHERE status = ?", (FakturaStatus.IKKE_BETALT,)).fetchone()[0]
        overdue_invoices = conn.execute("SELECT COUNT(*) FROM invoices WHERE status = ?", (FakturaStatus.FORFALDEN,)).fetchone()[0]

    report_data = {
        "TotalBetalt": total_beloeb,
        "UbetalteFakturaer": unpaid_invoices,
        "ForfaldneFakturaer": overdue_invoices
    }

    return jsonify(report_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)