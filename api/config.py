import os

PIPELINES_CONFIG = {
    "testing-backend-vehicle-api": {
        "nombre_visible": "Vehicle API",
        "workflow_name": "cypress.yml",
        "default_branch": "develop",
        "workflow_input_key": "suite",
        "suites": ["All", "Internal", "External", "Positive", "Negative"]
    },
    "testing-backend-customer-account-api": {
        "nombre_visible": "Customer Account API",
        "workflow_name": "cypress.yml",
        "default_branch": "develop",
        "workflow_input_key": "suite",
        "suites": ["All", "HealthCheck", "AccountConsultation", "NegativeTests"]
    },
    "testing-wsempresas-greatExpectations": {
        "nombre_visible": "Análitica de Datos",
        "workflow_name": "validaciones_manual.yml",
        "default_branch": "feature/fernanda",
        "workflow_input_key": "pipeline",
        "suites": ["invoice_raw", "invoice_trusted", "wallet_dto_raw", "wallet_dto_trusted"]
    },
    "testing-api-facturacion-electronica2": {
        "nombre_visible": "Facturación electrónica 2.0",
        "workflow_name": "main.yml",
        "default_branch": "main",
        "workflow_input_key": "tags",
        "suites": ["all", "main-flows", "billing", "negative", "kafka-stream"]
    }
}

SLACK_REPORT_CHANNEL = os.environ.get("SLACK_REPORT_CHANNEL", "C0B4NEHBMLP")
