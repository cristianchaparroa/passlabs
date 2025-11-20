import json
import logging
from typing import Any, Dict, Optional

from config import settings
from utils.constants import GAS_LIMIT, GAS_PRICE_MULTIPLIER, MAX_RETRIES
from utils.logger import get_logger
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import BlockNotFound, TransactionNotFound

logger = get_logger(__name__)


class BlockchainService:
    """
    Servicio para interactuar con blockchain (Scroll Sepolia)
    Maneja transacciones, consultas de estado y gestión de contratos
    """

    def __init__(self):
        """Inicializar conexión a Web3 y cargar Smart Contract"""
        try:
            # Inicializar Web3
            self.w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))

            # Verificar conexión
            if not self.w3.is_connected():
                logger.error(f"Failed to connect to RPC: {settings.RPC_URL}")
                raise ConnectionError(
                    f"Cannot connect to blockchain RPC: {settings.RPC_URL}"
                )

            logger.info(f"✅ Connected to blockchain RPC: {settings.RPC_URL}")

            # Configurar cuenta desde clave privada
            self.account = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
            logger.info(f"✅ Account loaded: {self.account.address}")

            # Cargar contrato
            self.contract = self._load_contract()
            logger.info(f"✅ Smart Contract loaded: {settings.CONTRACT_ADDRESS}")

            # Obtener información de la red
            chain_id = self.w3.eth.chain_id
            logger.info(f"✅ Chain ID: {chain_id} (Expected: {settings.CHAIN_ID})")

            if chain_id != settings.CHAIN_ID:
                logger.warning(
                    f"⚠️  Chain ID mismatch! Expected {settings.CHAIN_ID}, got {chain_id}"
                )

        except Exception as e:
            logger.error(f"❌ BlockchainService initialization failed: {str(e)}")
            raise

    def _load_contract(self) -> Optional[Contract]:
        """
        Cargar instancia del Smart Contract usando ABI

        Returns:
            Contract: Instancia del contrato o None si falla
        """
        try:
            # Cargar ABI del contrato
            abi_path = "contracts/contract_abi.json"
            try:
                with open(abi_path, "r") as f:
                    contract_abi = json.load(f)
            except FileNotFoundError:
                logger.warning(f"ABI file not found at {abi_path}, using empty ABI")
                contract_abi = []

            # Crear instancia del contrato
            if contract_abi:
                contract = self.w3.eth.contract(
                    address=self.w3.to_checksum_address(settings.CONTRACT_ADDRESS),
                    abi=contract_abi,
                )
                return contract
            else:
                logger.warning("Using contract without ABI (limited functionality)")
                return None

        except Exception as e:
            logger.error(f"Error loading contract: {str(e)}")
            return None

    def is_connected(self) -> bool:
        """
        Verificar si hay conexión activa a blockchain

        Returns:
            bool: True si está conectado, False en caso contrario
        """
        try:
            return self.w3.is_connected()
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False

    def get_balance(self, address: str) -> float:
        """
        Obtener balance de ETH de una dirección

        Args:
            address: Dirección a consultar

        Returns:
            float: Balance en ETH

        Raises:
            ValueError: Si la dirección es inválida
            Exception: Si hay error al consultar
        """
        try:
            # Validar dirección
            if not self.w3.is_address(address):
                raise ValueError(f"Invalid Ethereum address: {address}")

            checksum_address = self.w3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(checksum_address)
            balance_eth = self.w3.from_wei(balance_wei, "ether")

            logger.debug(f"Balance of {checksum_address}: {balance_eth} ETH")
            return float(balance_eth)

        except ValueError as e:
            logger.error(f"Invalid address: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            raise

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Obtener recepción de una transacción (estado completo)

        Args:
            tx_hash: Hash de la transacción

        Returns:
            dict: Información de la transacción o None si no existe

        Raises:
            ValueError: Si el hash es inválido
            Exception: Si hay error al consultar
        """
        try:
            # Validar formato del hash
            if not tx_hash.startswith("0x") or len(tx_hash) != 66:
                raise ValueError(f"Invalid transaction hash format: {tx_hash}")

            # Obtener recepción
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)

            if receipt is None:
                logger.info(f"Transaction receipt not found: {tx_hash}")
                return None

            # Parsear información importante
            result = {
                "tx_hash": receipt.get("hash").hex(),
                "from": receipt.get("from"),
                "to": receipt.get("to"),
                "gas_used": receipt.get("gasUsed"),
                "gas_price": receipt.get("gasPrice"),
                "block_number": receipt.get("blockNumber"),
                "status": "success" if receipt.get("status") == 1 else "failed",
                "confirmations": self._get_confirmations(receipt.get("blockNumber")),
                "transaction_fee": self.w3.from_wei(
                    receipt.get("gasUsed") * receipt.get("gasPrice"), "ether"
                ),
            }

            logger.debug(f"Transaction receipt: {tx_hash} - Status: {result['status']}")
            return result

        except ValueError as e:
            logger.error(f"Invalid transaction hash: {str(e)}")
            raise
        except TransactionNotFound:
            logger.info(f"Transaction not found: {tx_hash}")
            return None
        except Exception as e:
            logger.error(f"Error getting transaction receipt: {str(e)}")
            raise

    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Obtener estado simplificado de una transacción

        Args:
            tx_hash: Hash de la transacción

        Returns:
            dict: Estado con campos principales
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)

            if receipt is None:
                return {
                    "tx_hash": tx_hash,
                    "status": "pending",
                    "confirmations": 0,
                    "block_number": None,
                }

            confirmations = self._get_confirmations(receipt.get("blockNumber"))

            return {
                "tx_hash": tx_hash,
                "status": "success" if receipt.get("status") == 1 else "failed",
                "confirmations": confirmations,
                "block_number": receipt.get("blockNumber"),
                "gas_used": receipt.get("gasUsed"),
            }

        except Exception as e:
            logger.error(f"Error getting transaction status: {str(e)}")
            return {
                "tx_hash": tx_hash,
                "status": "error",
                "confirmations": 0,
                "error": str(e),
            }

    def _get_confirmations(self, block_number: int) -> int:
        """
        Calcular número de confirmaciones de un bloque

        Args:
            block_number: Número del bloque

        Returns:
            int: Número de confirmaciones
        """
        try:
            current_block = self.w3.eth.block_number
            confirmations = max(0, current_block - block_number)
            return confirmations
        except Exception as e:
            logger.error(f"Error calculating confirmations: {str(e)}")
            return 0

    def estimate_gas(
        self,
        to_address: str,
        amount: float,
        data: str = None,
    ) -> int:
        """
        Estimar costo de gas para una transacción

        Args:
            to_address: Dirección destino
            amount: Cantidad en ETH
            data: Datos opcionales de la transacción

        Returns:
            int: Estimación de gas

        Raises:
            ValueError: Si los parámetros son inválidos
            Exception: Si hay error en la estimación
        """
        try:
            if not self.w3.is_address(to_address):
                raise ValueError(f"Invalid address: {to_address}")

            # Construir transacción
            tx = {
                "from": self.account.address,
                "to": self.w3.to_checksum_address(to_address),
                "value": self.w3.to_wei(amount, "ether"),
                "data": data or "0x",
            }

            # Estimar gas
            gas_estimate = self.w3.eth.estimate_gas(tx)
            logger.debug(f"Gas estimate: {gas_estimate}")

            return gas_estimate

        except ValueError as e:
            logger.error(f"Invalid parameter: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error estimating gas: {str(e)}")
            raise

    def send_raw_transaction(self, tx_data: Dict) -> str:
        """
        Enviar transacción firmada al blockchain

        Args:
            tx_data: Datos de la transacción

        Returns:
            str: Hash de la transacción enviada

        Raises:
            Exception: Si hay error al enviar
        """
        try:
            # Estimar gas si no está especificado
            if "gas" not in tx_data:
                tx_data["gas"] = int(
                    self.estimate_gas(
                        tx_data.get("to"),
                        self.w3.from_wei(tx_data.get("value", 0), "ether"),
                    )
                    * GAS_PRICE_MULTIPLIER
                )

            # Obtener gas price actual
            if "gasPrice" not in tx_data:
                tx_data["gasPrice"] = self.w3.eth.gas_price

            # Obtener nonce
            if "nonce" not in tx_data:
                tx_data["nonce"] = self.w3.eth.get_transaction_count(
                    self.account.address
                )

            # Agregar campos obligatorios
            tx_data["chainId"] = settings.CHAIN_ID
            tx_data["from"] = self.account.address

            logger.info(f"Sending transaction to {tx_data.get('to')}")
            logger.debug(f"TX Data: {tx_data}")

            # Firmar transacción
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.account.key)

            # Enviar transacción
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            logger.info(f"✅ Transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()

        except Exception as e:
            logger.error(f"Error sending transaction: {str(e)}")
            raise

    def call_contract_function(self, function_name: str, *args, **kwargs) -> Any:
        """
        Llamar función de lectura del contrato (no consume gas)

        Args:
            function_name: Nombre de la función
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados

        Returns:
            Any: Resultado de la función

        Raises:
            AttributeError: Si la función no existe
            Exception: Si hay error en la llamada
        """
        try:
            if not self.contract:
                raise RuntimeError("Contract not loaded")

            # Obtener función
            if not hasattr(self.contract.functions, function_name):
                raise AttributeError(f"Function {function_name} not found in contract")

            func = getattr(self.contract.functions, function_name)
            result = func(*args).call()

            logger.debug(f"Contract call {function_name}: {result}")
            return result

        except AttributeError as e:
            logger.error(f"Function not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error calling contract function: {str(e)}")
            raise

    def build_contract_transaction(self, function_name: str, *args, **kwargs) -> Dict:
        """
        Construir transacción para llamar función del contrato

        Args:
            function_name: Nombre de la función
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados

        Returns:
            dict: Datos de la transacción

        Raises:
            Exception: Si hay error al construir
        """
        try:
            if not self.contract:
                raise RuntimeError("Contract not loaded")

            # Obtener función
            func = getattr(self.contract.functions, function_name)

            # Construir transacción
            tx = func(*args).build_transaction(
                {
                    "from": self.account.address,
                    "nonce": self.w3.eth.get_transaction_count(self.account.address),
                    "gas": GAS_LIMIT,
                    "gasPrice": self.w3.eth.gas_price,
                }
            )

            logger.debug(f"Contract transaction built: {function_name}")
            return tx

        except Exception as e:
            logger.error(f"Error building contract transaction: {str(e)}")
            raise

    def is_token_allowed(self, token_address: str) -> bool:
        """
        Verificar si un token está permitido en el contrato

        Args:
            token_address: Dirección del token

        Returns:
            bool: True si está permitido
        """
        try:
            if not self.contract:
                logger.warning("Contract not loaded, cannot check token")
                return False

            is_allowed = self.call_contract_function(
                "isTokenAllowed", self.w3.to_checksum_address(token_address)
            )
            return bool(is_allowed)

        except Exception as e:
            logger.error(f"Error checking token allowed: {str(e)}")
            return False

    def get_contract_balance(self, token_address: str) -> float:
        """
        Obtener balance del contrato para un token específico

        Args:
            token_address: Dirección del token

        Returns:
            float: Balance en unidades del token
        """
        try:
            if not self.contract:
                logger.warning("Contract not loaded")
                return 0.0

            balance = self.call_contract_function(
                "getTokenBalance", self.w3.to_checksum_address(token_address)
            )
            return float(self.w3.from_wei(balance, "ether"))

        except Exception as e:
            logger.error(f"Error getting contract balance: {str(e)}")
            return 0.0

    def get_gas_price(self) -> float:
        """
        Obtener precio actual del gas

        Returns:
            float: Gas price en Gwei
        """
        try:
            gas_price_wei = self.w3.eth.gas_price
            gas_price_gwei = self.w3.from_wei(gas_price_wei, "gwei")
            logger.debug(f"Current gas price: {gas_price_gwei} Gwei")
            return float(gas_price_gwei)
        except Exception as e:
            logger.error(f"Error getting gas price: {str(e)}")
            return 0.0

    def get_network_info(self) -> Dict[str, Any]:
        """
        Obtener información general de la red

        Returns:
            dict: Información de la red
        """
        try:
            return {
                "chain_id": self.w3.eth.chain_id,
                "latest_block": self.w3.eth.block_number,
                "gas_price": float(self.w3.from_wei(self.w3.eth.gas_price, "gwei")),
                "is_connected": self.is_connected(),
                "account": self.account.address,
                "account_balance": float(
                    self.w3.from_wei(
                        self.w3.eth.get_balance(self.account.address), "ether"
                    )
                ),
            }
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}")
            return {}


# Instancia global del servicio
try:
    blockchain_service = BlockchainService()
except Exception as e:
    logger.error(f"Failed to initialize blockchain service: {str(e)}")
    blockchain_service = None
