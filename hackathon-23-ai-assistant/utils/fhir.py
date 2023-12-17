from fhirpy import AsyncFHIRClient

from .. import config


def get_fhir_client(token: str):
    return AsyncFHIRClient(
        f"{config.FHIR_SERVER_URL}/fhir",
        authorization=token,
    )
