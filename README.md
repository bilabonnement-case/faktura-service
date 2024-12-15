# Fakturering-Service

Fakturering-Service is a Flask-based microservice that handles invoice management. It includes endpoints for creating invoices, retrieving invoice details, updating invoice statuses, and generating invoice reports. The service uses SQLite for database management and provides API documentation via Swagger.

## Features
	•	Create Invoices: Add new invoices with customer and subscription details.
	•	Retrieve Invoices: Fetch invoice details by their unique ID.
	•	Update Invoice Status: Change the status of an invoice (e.g., Paid, Unpaid, Overdue).
	•	Invoice Reporting: Generate reports summarizing total payments, unpaid invoices, and overdue invoices.
	•	API Documentation: Integrated Swagger UI for exploring and testing endpoints.

## Requirements

### Python Packages
	•	Python 3.7 or higher
	•	Flask
	•	Flask-Swagger (Flasgger)
	•	python-dotenv
	•	SQLite (built into Python)

### Python Dependencies

Install the required dependencies using:
```Pip install -r requirements.txt```

### Environment Variables

Create a .env file in the root directory and specify the following:
```FLASK_DEBUG=1```
```DATABASE=faktura-database.db```

## Getting Started

1. Initialize the Database

The service uses SQLite to store invoice data. The database is automatically initialized when the service starts. To reinitialize, you can modify the init_db() function in faktura-app.py.

2. Start the Service

Run the Flask application:
```python faktura-app.py```
The service will be available at http://127.0.0.1:5001.

## API Endpoints

1. GET /

Provides a list of available endpoints in the service.

#### Response Example:
```
{
  "service": "Fakturering-Service",
  "available_endpoints": [
    {"path": "/create_invoice", "method": "POST", "description": "Opret ny faktura"},
    {"path": "/get_invoice/<int:faktura_id>", "method": "GET", "description": "Hent faktura baseret på FakturaID"},
    {"path": "/update_status/<int:faktura_id>", "method": "PUT", "description": "Opdater fakturastatus"},
    {"path": "/report", "method": "GET", "description": "Få samlet fakturarapportering"}
  ]
}
```

2. POST /create_invoice

Creates a new invoice.

#### Request Body:
```
{
  "abonnements_id": 123,
  "kunde_id": 456,
  "beloeb": 1200.50,
  "betalingsdato": "2024-12-15 14:30:00"
}
```

#### Response Example:
```
{
  "message": "Faktura oprettet",
  "invoice_id": 1
}
```

3. GET /get_invoice/<int:faktura_id>

Retrieves the details of an invoice by its unique ID.

#### Response Example:
```
{
  "id": 1,
  "abonnements_id": 123,
  "kunde_id": 456,
  "beloeb": 1200.50,
  "betalingsdato": "2024-12-15 14:30:00",
  "status": "Ikke betalt",
  "oprettet_tidspunkt": "2024-12-01T12:00:00"
}
```

4. PUT /update_status/<int:faktura_id>

Updates the status of an invoice.

#### Request Body:
```
{
  "Status": "Betalt"
}
```

#### Response Example:
```
{
  "message": "Status opdateret",
  "invoice": {
    "id": 1,
    "status": "Betalt"
  }
}
```

5. GET /report

Generates a summary report of all invoices.

#### Response Example:
```
{
  "TotalBetalt": 15000.75,
  "UbetalteFakturaer": 10,
  "ForfaldneFakturaer": 2,
  "TotalFakturaer": 50
}
```
## Project Structure
```
.
├── faktura-app.py        # Main Flask application
├── faktura-database.db   # SQLite database (created automatically)
├── swagger/              # YAML files for API documentation
│   ├── create_invoice.yaml
│   ├── get_invoice.yaml
│   ├── update_status.yaml
│   ├── report.yaml
│   └── home.yaml
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md             # Project documentation
```

## Development Notes

### Swagger Documentation
	•	Swagger is available at /apidocs.
	•	API specifications are written in YAML and stored in the swagger/ folder.

### Database Management
	•	Initialization: Automatically initializes the database on start.
	•	Schema: The invoices table has the following structure:
	•	id: Unique invoice ID (primary key).
	•	abonnements_id: Subscription ID.
	•	kunde_id: Customer ID.
	•	beloeb: Invoice amount.
	•	betalingsdato: Due date.
	•	status: Invoice status (Ikke betalt, Betalt, Forfalden).
	•	oprettet_tidspunkt: Creation timestamp.

## Contributions

Feel free to fork the repository and submit pull requests. For major changes, open an issue to discuss what you would like to change.

## License

This project is licensed under the MIT License. See LICENSE for more information.