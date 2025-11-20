import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from config import settings
from utils.logger import get_logger
from utils.validators import is_valid_stablecoin

logger = get_logger(__name__)


class DeFiLlamaService:
    """
    Servicio para obtener precios de stablecoins desde DeFiLlama API
    Incluye caché local con TTL configurable para optimizar llamadas a la API
    """

    def __init__(self):
        """Inicializar servicio con configuración de caché"""
        self.api_url = settings.DEFI_LLAMA_API_URL
        self.cache_ttl = settings.CACHE_TTL
        self.target_stablecoins = settings.STABLECOINS

        # Almacenamiento de caché
        self.cache: Dict[str, Any] = {}
        self.cache_timestamp: Optional[float] = None

        # Configuración de timeout
        self.timeout = 10.0

        logger.info(
            f"DeFiLlamaService initialized. "
            f"API: {self.api_url}, Cache TTL: {self.cache_ttl}s, "
            f"Target stablecoins: {self.target_stablecoins}"
        )

    async def get_stablecoin_prices(self) -> List[Dict[str, Any]]:
        """
        Obtener precios de stablecoins desde DeFiLlama API con caché

        Returns:
            List[Dict]: Lista de stablecoins con sus precios actualizados:
                - name: Nombre del stablecoin
                - symbol: Símbolo (USDC, USDT, DAI)
                - price_usd: Precio en USD
                - market_cap: Capitalización de mercado
                - change_24h: Cambio en 24 horas (porcentaje)

        Raises:
            Exception: Si hay error al obtener datos y no hay caché disponible
        """
        try:
            # Verificar si caché es válido
            if self._is_cache_valid():
                logger.info("✅ Using cached stablecoin prices")
                return self.cache.get("stablecoins", [])

            logger.info("📡 Fetching fresh stablecoin prices from DeFiLlama")

            # Obtener datos frescos de la API
            stablecoins = await self._fetch_from_api()

            # Actualizar caché
            self._update_cache(stablecoins)

            logger.info(f"✅ Fetched {len(stablecoins)} stablecoins from API")
            return stablecoins

        except Exception as e:
            logger.error(f"Error fetching prices from API: {str(e)}")

            # Si hay error, retornar caché anterior si existe
            if self.cache and "stablecoins" in self.cache:
                logger.warning("⚠️  Returning cached prices after API error")
                return self.cache.get("stablecoins", [])

            # Si no hay caché, retornar lista vacía o lanzar excepción
            logger.error("No cached data available, returning empty list")
            return []

    async def _fetch_from_api(self) -> List[Dict[str, Any]]:
        """
        Obtener datos directamente de DeFiLlama API

        Returns:
            List[Dict]: Datos de stablecoins parseados

        Raises:
            Exception: Si hay error en la conexión o en el parsing
        """
        logger.debug(f"Connecting to DeFiLlama API: {self.api_url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()

                data = response.json()
                logger.debug(f"Received API response with {len(data)} entries")

                # Parsear respuesta
                stablecoins = self._parse_stablecoins(data)

                logger.info(f"Parsed {len(stablecoins)} target stablecoins")
                return stablecoins

        except httpx.TimeoutException:
            logger.error(
                f"Timeout connecting to DeFiLlama API (timeout: {self.timeout}s)"
            )
            raise Exception("Timeout: DeFiLlama API did not respond in time")

        except httpx.HTTPError as e:
            logger.error(f"HTTP error from DeFiLlama API: {str(e)}")
            raise Exception(f"HTTP error: {str(e)}")

        except Exception as e:
            logger.error(f"Error fetching from DeFiLlama API: {str(e)}")
            raise

    def _parse_stablecoins(self, data: Dict) -> List[Dict[str, Any]]:
        """
        Parsear respuesta de DeFiLlama y extraer los stablecoins objetivo

        La API de DeFiLlama retorna una estructura con información de stablecoins
        en diferentes blockchains. Este método filtra y extrae los datos relevantes.

        Args:
            data: Respuesta JSON de DeFiLlama API

        Returns:
            List[Dict]: Stablecoins filtrados con información:
                - name: Nombre completo del token
                - symbol: Símbolo del token (USDC, USDT, DAI)
                - price_usd: Precio en USD
                - market_cap: Capitalización de mercado
                - change_24h: Cambio en 24 horas
                - chains: Blockchains donde está disponible

        Raises:
            ValueError: Si la estructura de datos es inesperada
        """
        try:
            result = []

            # DeFiLlama API retorna diferentes estructuras dependiendo del endpoint
            # Generalmente tiene una lista de stablecoins con información por cadena

            if isinstance(data, dict):
                # Si es un diccionario, podría tener una clave "stablecoins"
                stablecoins_data = data.get("stablecoins", [])

                if not isinstance(stablecoins_data, list):
                    logger.warning("Unexpected data structure from API")
                    return []

            elif isinstance(data, list):
                # Si es una lista directa
                stablecoins_data = data

            else:
                logger.error(f"Unexpected API response type: {type(data)}")
                return []

            # Procesar cada stablecoin
            for item in stablecoins_data:
                try:
                    # Extraer información del stablecoin
                    symbol = item.get("symbol", "").upper()
                    name = item.get("name", "")

                    # Verificar si es uno de nuestros target stablecoins
                    if symbol not in self.target_stablecoins:
                        continue

                    # Extraer precios - pueden estar en diferentes estructuras
                    price_usd = self._extract_price(item)
                    market_cap = self._extract_market_cap(item)
                    change_24h = self._extract_change_24h(item)
                    chains = self._extract_chains(item)

                    # Solo incluir si tiene precio válido
                    if price_usd is not None and price_usd > 0:
                        stablecoin_info = {
                            "name": name or symbol,
                            "symbol": symbol,
                            "price_usd": price_usd,
                            "market_cap": market_cap or "N/A",
                            "change_24h": change_24h or 0.0,
                            "chains": chains,
                            "last_updated": datetime.utcnow().isoformat() + "Z",
                        }
                        result.append(stablecoin_info)
                        logger.debug(f"Parsed {symbol}: ${price_usd}")

                except KeyError as e:
                    logger.debug(f"Missing key in stablecoin data: {str(e)}")
                    continue
                except Exception as e:
                    logger.debug(f"Error parsing stablecoin item: {str(e)}")
                    continue

            logger.info(f"Successfully parsed {len(result)} target stablecoins")
            return result

        except Exception as e:
            logger.error(f"Error parsing stablecoins: {str(e)}")
            return []

    def _extract_price(self, item: Dict) -> Optional[float]:
        """
        Extraer precio en USD del item

        Args:
            item: Item de stablecoin del API

        Returns:
            float: Precio en USD o None
        """
        try:
            # Intentar diferentes estructuras posibles
            # Estructura 1: precio directo
            if "price" in item:
                price = item["price"]
                if isinstance(price, (int, float)) and price > 0:
                    return float(price)

            # Estructura 2: precios por cadena
            if "chainBalances" in item:
                for chain_data in item["chainBalances"].values():
                    if isinstance(chain_data, dict) and "price" in chain_data:
                        price = chain_data["price"]
                        if isinstance(price, (int, float)) and price > 0:
                            return float(price)

            # Estructura 3: información de mercado
            if "marketData" in item and "priceUSD" in item["marketData"]:
                price = item["marketData"]["priceUSD"]
                if isinstance(price, (int, float)) and price > 0:
                    return float(price)

            # Estructura 4: precio_usd con guión
            if "price_usd" in item:
                price = item["price_usd"]
                if isinstance(price, (int, float)) and price > 0:
                    return float(price)

            # Para stablecoins, el precio típicamente debe ser ~1.00
            logger.debug(
                f"Could not extract price from item: {item.get('symbol', 'unknown')}"
            )
            return None

        except Exception as e:
            logger.debug(f"Error extracting price: {str(e)}")
            return None

    def _extract_market_cap(self, item: Dict) -> Optional[str]:
        """
        Extraer capitalización de mercado

        Args:
            item: Item de stablecoin del API

        Returns:
            str: Capitalización de mercado formateada o None
        """
        try:
            # Intentar extraer market cap
            if "marketCap" in item:
                mc = item["marketCap"]
                if isinstance(mc, (int, float)) and mc > 0:
                    return self._format_number(mc)

            if "market_cap" in item:
                mc = item["market_cap"]
                if isinstance(mc, (int, float)) and mc > 0:
                    return self._format_number(mc)

            if "chainBalances" in item:
                total_mc = 0
                for chain_data in item["chainBalances"].values():
                    if isinstance(chain_data, dict) and "mcap" in chain_data:
                        mc = chain_data.get("mcap", 0)
                        if isinstance(mc, (int, float)):
                            total_mc += mc
                if total_mc > 0:
                    return self._format_number(total_mc)

            return None

        except Exception as e:
            logger.debug(f"Error extracting market cap: {str(e)}")
            return None

    def _extract_change_24h(self, item: Dict) -> Optional[float]:
        """
        Extraer cambio de precio en 24 horas

        Args:
            item: Item de stablecoin del API

        Returns:
            float: Porcentaje de cambio o None
        """
        try:
            # Intentar diferentes estructuras
            if "change24h" in item:
                change = item["change24h"]
                if isinstance(change, (int, float)):
                    return float(change)

            if "change_24h" in item:
                change = item["change_24h"]
                if isinstance(change, (int, float)):
                    return float(change)

            if "priceChange24h" in item:
                change = item["priceChange24h"]
                if isinstance(change, (int, float)):
                    return float(change)

            # Para stablecoins, el cambio suele ser muy pequeño
            return 0.0

        except Exception as e:
            logger.debug(f"Error extracting change_24h: {str(e)}")
            return 0.0

    def _extract_chains(self, item: Dict) -> List[str]:
        """
        Extraer blockchains donde está disponible el token

        Args:
            item: Item de stablecoin del API

        Returns:
            list: Lista de nombres de blockchains
        """
        try:
            chains = []

            # Intentar extraer desde diferentes estructuras
            if "chains" in item and isinstance(item["chains"], list):
                chains.extend(item["chains"])

            if "chainBalances" in item and isinstance(item["chainBalances"], dict):
                chains.extend(item["chainBalances"].keys())

            # Filtrar duplicados y retornar
            return list(set(chains)) if chains else ["scroll"]

        except Exception as e:
            logger.debug(f"Error extracting chains: {str(e)}")
            return ["scroll"]

    def _format_number(self, number: float) -> str:
        """
        Formatear número grande de manera legible

        Args:
            number: Número a formatear

        Returns:
            str: Número formateado (ej: "1.2B", "500M")
        """
        try:
            if number >= 1_000_000_000:
                return f"${number / 1_000_000_000:.1f}B"
            elif number >= 1_000_000:
                return f"${number / 1_000_000:.1f}M"
            elif number >= 1_000:
                return f"${number / 1_000:.1f}K"
            else:
                return f"${number:.2f}"
        except Exception as e:
            logger.debug(f"Error formatting number: {str(e)}")
            return "N/A"

    def _is_cache_valid(self) -> bool:
        """
        Verificar si el caché es aún válido (no expirado)

        Returns:
            bool: True si el caché es válido, False si expiró
        """
        if not self.cache or self.cache_timestamp is None:
            logger.debug("Cache is empty or timestamp not set")
            return False

        elapsed = time.time() - self.cache_timestamp
        is_valid = elapsed < self.cache_ttl

        if not is_valid:
            logger.info(
                f"Cache expired (TTL: {self.cache_ttl}s, elapsed: {elapsed:.1f}s)"
            )
        else:
            logger.debug(
                f"Cache is valid (TTL: {self.cache_ttl}s, elapsed: {elapsed:.1f}s)"
            )

        return is_valid

    def _update_cache(self, stablecoins: List[Dict[str, Any]]) -> None:
        """
        Actualizar caché con nuevos datos

        Args:
            stablecoins: Lista de stablecoins para cachear
        """
        self.cache = {
            "stablecoins": stablecoins,
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }
        self.cache_timestamp = time.time()
        logger.info(
            f"✅ Cache updated with {len(stablecoins)} stablecoins "
            f"(TTL: {self.cache_ttl}s)"
        )

    def clear_cache(self) -> None:
        """
        Limpiar caché manualmente (útil para testing o forzar actualización)
        """
        self.cache = {}
        self.cache_timestamp = None
        logger.info("Cache cleared manually")

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Obtener información sobre el estado del caché

        Returns:
            dict: Información del caché:
                - is_valid: Si el caché es válido
                - last_updated: Timestamp de última actualización
                - age_seconds: Edad del caché en segundos
                - ttl_seconds: TTL configurado
                - entries: Número de stablecoins en caché
        """
        try:
            if not self.cache_timestamp:
                return {
                    "is_valid": False,
                    "last_updated": None,
                    "age_seconds": None,
                    "ttl_seconds": self.cache_ttl,
                    "entries": 0,
                }

            age = time.time() - self.cache_timestamp
            is_valid = age < self.cache_ttl

            return {
                "is_valid": is_valid,
                "last_updated": self.cache.get("last_updated"),
                "age_seconds": round(age, 2),
                "ttl_seconds": self.cache_ttl,
                "entries": len(self.cache.get("stablecoins", [])),
            }

        except Exception as e:
            logger.error(f"Error getting cache info: {str(e)}")
            return {}

    async def get_specific_stablecoin(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de un stablecoin específico

        Args:
            symbol: Símbolo del stablecoin (USDC, USDT, DAI)

        Returns:
            dict: Información del stablecoin o None

        Raises:
            ValueError: Si el símbolo no es válido
        """
        try:
            if not is_valid_stablecoin(symbol):
                raise ValueError(f"Invalid stablecoin symbol: {symbol}")

            logger.debug(f"Getting price for {symbol}")

            # Obtener lista de precios
            prices = await self.get_stablecoin_prices()

            # Buscar el stablecoin específico
            for sc in prices:
                if sc["symbol"].upper() == symbol.upper():
                    return sc

            logger.warning(f"Stablecoin {symbol} not found in prices")
            return None

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting stablecoin {symbol}: {str(e)}")
            raise


# Instancia global del servicio
defi_llama_service = DeFiLlamaService()
