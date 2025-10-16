import json
import logging
from redis import Redis
from tenacity import stop_after_attempt, wait_fixed, before_log, after_log, retry
from src.settings import settings
from src.utils.logging.logger_factory import get_logger

logger = get_logger()

MAX_ATTEMPTS = 3
WAIT_TIME = 1


class RedisClient:
    def __init__(self):
        self.client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self._check_connection()
    
    @retry(
        stop=stop_after_attempt(MAX_ATTEMPTS),
        wait=wait_fixed(WAIT_TIME),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.WARNING),
    )
    def _check_connection(self):
        try:
            if not self.client.ping():
                raise Exception("No se pudo establecer conexión con Redis")
            logger.info("Conexión a Redis establecida")
        except Exception as e:
            logger.error(f"Error al conectar a Redis: {e}")
            raise e
        

    def _parse_data(self, data: dict) -> dict:
        data = {
            key: json.dumps(value) if isinstance(value, (list, dict)) else value
            for key, value in data.items()
        }
        return data

    def save_hset(self, key: str, data: dict):
        try:
            self.client.hset(key, mapping=self._parse_data(data))
            logger.info(f"Datos guardados en Redis para la clave: {key}")
        except Exception as e:
            logger.error(f"Error al guardar datos en Redis: {e}")
            raise e
        
    def get_hset(self, key: str) -> dict:
        try:
            return self.parse_hset(self.client.hgetall(key))
        except Exception as e:
            logger.error(f"Error al obtener datos de Redis: {e}")
            raise e
        
    def parse_hset(self, data: dict) -> dict:
        for key, value in data.items():
            try:
                data[key] = json.loads(value) if isinstance(value, str) else value
            except Exception as e:
                data[key] = value
        return data
        
    def delete_hset(self, key: str):
        try:
            self.client.delete(key)
            logger.info(f"Datos eliminados de Redis para la clave: {key}")
        except Exception as e:
            logger.error(f"Error al eliminar datos de Redis: {e}")
            raise e
        
    def get_hset_keys(self, prefix: str) -> list[str]:
        try:
            return self.client.keys(f"{prefix}*")
        except Exception as e:
            logger.error(f"Error al obtener claves de Redis: {e}")
            raise e
        
    def get_hset_keys_with_prefix(self, prefix: str) -> list[str]:
        try:
            return self.client.keys(f"{prefix}*")
        except Exception as e:
            logger.error(f"Error al obtener claves de Redis: {e}")
            raise e
