from os import environ

OPENAI_API_KEY = environ["OPENAI_API_KEY"]
FHIR_SERVER_URL = environ.get("FHIR_SERVER_URL", "http://localhost:8080")
