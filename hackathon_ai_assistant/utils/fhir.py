import datetime

from fhirpy import AsyncFHIRClient

from .. import config


def get_fhir_client(token: str):
    return AsyncFHIRClient(
        f"{config.FHIR_SERVER_URL}/fhir",
        authorization=token,
    )


def get_now():
    """Get timezone aware UTC datetime"""
    return datetime.datetime.now(datetime.UTC)


def format_date_time(date: datetime.datetime):
    iso_str = date.isoformat()
    fhir_str = str(iso_str).replace("+00:00", "Z")
    return fhir_str
