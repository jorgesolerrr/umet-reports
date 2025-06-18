import requests
from src.logging.logger_factory import get_logger
from .suspended_data import (
    test_shortSNAZeroResponse,
    test_shortSNAFullResponse,
)

ENV = "PRODUCTION"
logger = get_logger()


def _filter_response(data: list, programs: list):
    logger.info(f"Filtrando respuesta de SNA - API para programas: {programs}")
    SNA_userListProg = []
    SNA_userList_set = set()
    for user in data:
        if user["programa"] in programs:
            SNA_userList_set.add(user["cedula"])
            SNA_userListProg.append(user)
    return SNA_userList_set, SNA_userListProg


def call_sna_api_deudas():
    debt_users = None
    match ENV:
        case "PRODUCTION":
            try:
                # Llamado de API de producción
                sna_api_deuda_endpoint = "https://alumno.umet.app/CESDEL/deuda"
                response = requests.get(
                    sna_api_deuda_endpoint,
                    headers={
                        "Authorization": "Token ed67224d38aa78f0940a4d332c9cfcab9f4bc20a"
                    },
                )
                response.raise_for_status()
                logger.info(
                    f"Llamada a SNA - API: {sna_api_deuda_endpoint} - con status_code: {response.status_code}"
                )
                response = response.json()

                if "respuesta" not in response.keys() or "data" not in response.keys():
                    logger.error(
                        f"Devolución de respuesta con estructura incorrecta en llamado a {sna_api_deuda_endpoint}, keys: {response.keys()}"
                    )
                    raise ValueError(
                        f"Devolución de respuesta con estructura incorrecta en llamado a {sna_api_deuda_endpoint}"
                    )

                match response["respuesta"]:
                    case "1":
                        debt_users = response["data"]
                    case "2":
                        logger.error(
                            f"Llamado a {sna_api_deuda_endpoint} retorna fuera de tiempo"
                        )
                        raise ValueError(
                            f"Llamado a {sna_api_deuda_endpoint} retorna fuera de tiempo"
                        )
                    case _:
                        logger.error(
                            f"Devolución con código de respuesta desconocido en llamado a {sna_api_deuda_endpoint} -- {response['respuesta']}"
                        )
                        raise ValueError(
                            f"Devolución con código de respuesta desconocido en llamado a {sna_api_deuda_endpoint}"
                        )

            except Exception as e:
                logger.error(
                    f"Error llamando a SNA - API: {sna_api_deuda_endpoint} - {str(e)}"
                )
                raise e
        case "DEV_ZERO_RESPONSE":
            response = test_shortSNAZeroResponse
            debt_users = response["data"]
        case "DEV_SHORT_RESPONSE":
            response = test_shortSNAFullResponse
            debt_users = response["data"]
        case _:
            logger.error(f"Environment {ENV} not supported")
            raise ValueError(f"Environment {ENV} not supported")
        
    return debt_users
