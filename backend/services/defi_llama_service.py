import time
from typing import Dict, List, Optional

import httpx
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class DeFiLlamaService:
    """Servicio para obtener precios de stablecoins desde DeFiLlama API"""

    def __init__(self):
        self.api_url = settings.DEFI_LLAMA_API_URL
        self.cache_ttl = settings.CACHE_TTL
        self.cache: Dict = {}
        self.cache_timestamp: Optional[float] = None
        self.target_stablecoins = settings.STABLECOINS

    async def get_stablecoin_prices(self) -> List[Dict]:
        """
        Obtener precios de stablecoins desde DeFiLlama API con caché

        Returns:
            List[Dict]: Lista de stablecoins con sus precios

        Raises:
            Exception: Si hay error al obtener datos de la API
        """
        # Verificar si caché es válido
        if self._is_cache_valid():
            logger.info("Usando datos en caché de stablecoins")
            return self.cache.get("stablecoins", [])

        # Obtener datos frescos de la API
        try:
            stablecoins = await self._fetch_from_api()
            self._update_cache(stablecoins)
            return stablecoins
        except Exception as e:
            logger.error(f"Error obteniendo precios de DeFiLlama: {str(e)}")
            # Si hay error, retornar caché anterior si existe
            if self.cache:
                logger.warning("Retornando datos en caché después de error")
                return self.cache.get("stablecoins", [])
            raise

    async def _fetch_from_api(self) -> List[Dict]:
        """
        Obtener datos directamente de DeFiLlama API

        Returns:
            List[Dict]: Datos de stablecoins

        Raises:
            Exception: Si hay error en la conexión
        """
        logger.info(f"Obteniendo datos de DeFiLlama desde: {self.api_url}")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()

                data = response.json()
                stablecoins = self._parse_stablecoins(data)
                logger.info(f"Obtenidos {len(stablecoins)} stablecoins")
                return stablecoins

        except httpx.TimeoutException:
            logger.error("Timeout conectando a DeFiLlama API")
            raise Exception("Timeout: DeFiLlama API no responde")
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP en DeFiLlama API: {str(e)}")
            raise Exception(f"Error HTTP: {str(e)}")

    def _parse_stablecoins(self, data: Dict) -> List[Dict]:
        """
        Parsear respuesta de DeFiLlama y extraer los stablecoins objetivo

        Args:
            data: Respuesta JSON de DeFiLlama

        Returns:
            List[Dict]: Stablecoins filtrados con información relevante
        """
        # TODO: Implementar parsing de acuerdo a estructura de respuesta de DeFiLlama
        result = []
        return result

    def _is_cache_valid(self) -> bool:
        """
        Verificar si el caché es aún válido (no expirado)

        Returns:
            bool: True si es válido, False si expiró
        """
        if not self.cache or self.cache_timestamp is None:
            return False

        elapsed = time.time() - self.cache_timestamp
        is_valid = elapsed < self.cache_ttl

        if not is_valid:
            logger.info(f"Caché expirado (TTL: {self.cache_ttl}s, elapsed: {elapsed}s)")

        return is_valid

    def _update_cache(self, stablecoins: List[Dict]) -> None:
        """
        Actualizar caché con nuevos datos

        Args:
            stablecoins: Lista de stablecoins para cachear
        """
        self.cache = {"stablecoins": stablecoins}
        self.cache_timestamp = time.time()
        logger.info(f"Caché actualizado con {len(stablecoins)} stablecoins")


# Instancia global del servicio
defi_llama_service = DeFiLlamaService()
