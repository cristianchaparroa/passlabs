import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from config import settings
from models.payment import CreatePaymentRequest, PaymentData
from utils.logger import get_logger
from utils.validators import (
    is_valid_amount,
    is_valid_ethereum_address,
    is_valid_stablecoin,
)

logger = get_logger(__name__)


class PaymentService:
    """
    Servicio para gestionar pagos con criptomonedas
    Orquesta la lógica de creación, verificación y seguimiento de pagos
    """

    def __init__(self, blockchain_service):
        """
        Inicializar servicio de pagos

        Args:
            blockchain_service: Instancia de BlockchainService para transacciones
        """
        self.blockchain_service = blockchain_service
        self.payments_cache: Dict[str, Dict] = {}  # payment_id -> payment_data
        self.tx_hash_to_payment: Dict[str, str] = {}  # tx_hash -> payment_id
        logger.info("PaymentService initialized")

    async def create_payment(
        self,
        recipient_address: str,
        amount: float,
        stablecoin: str,
        description: str = "",
    ) -> Dict:
        """
        Crear un nuevo pago en blockchain

        Args:
            recipient_address: Dirección del destinatario (0x...)
            amount: Cantidad a pagar
            stablecoin: Tipo de stablecoin (USDC, USDT, DAI)
            description: Descripción del pago

        Returns:
            dict: Información del pago creado

        Raises:
            ValueError: Si los datos son inválidos
            Exception: Si hay error al procesar el pago
        """
        try:
            logger.info(
                f"Creating payment: {amount} {stablecoin} to {recipient_address}"
            )

            # Validar datos de entrada
            if not is_valid_ethereum_address(recipient_address):
                raise ValueError(f"Invalid recipient address: {recipient_address}")

            if not is_valid_amount(amount):
                raise ValueError(
                    f"Invalid amount: {amount}. Must be between 0.01 and 1,000,000"
                )

            if not is_valid_stablecoin(stablecoin):
                raise ValueError(
                    f"Invalid stablecoin: {stablecoin}. Supported: {settings.STABLECOINS}"
                )

            # Obtener dirección del token
            token_address = self._get_token_address(stablecoin)
            if not token_address:
                raise ValueError(f"Token address not configured for {stablecoin}")

            # Generar ID único del pago
            payment_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat() + "Z"

            # Verificar que el token está permitido en el contrato
            if not await self._verify_token_allowed(token_address):
                logger.warning(f"Token {stablecoin} not allowed in contract")
                raise ValueError(
                    f"Token {stablecoin} is not allowed in payment contract"
                )

            # Crear estructura de datos del pago
            payment_data = {
                "payment_id": payment_id,
                "tx_hash": None,  # Se asignará después de enviar
                "recipient": recipient_address,
                "amount": amount,
                "stablecoin": stablecoin,
                "token_address": token_address,
                "status": "pending",
                "description": description,
                "created_at": now,
                "completed_at": None,
                "confirmations": 0,
                "block_number": None,
                "error": None,
            }

            # Guardar en caché local
            self.payments_cache[payment_id] = payment_data

            logger.info(f"Payment created in cache: {payment_id}")

            # Nota: La transacción real se enviaría aquí
            # Por ahora solo creamos el registro
            # En producción, aquí se llamaría a blockchain_service.send_raw_transaction()

            return payment_data

        except ValueError as e:
            logger.error(f"Validation error creating payment: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            raise

    async def send_payment_transaction(
        self,
        payment_id: str,
    ) -> Dict:
        """
        Enviar transacción de pago al blockchain

        Args:
            payment_id: ID del pago a enviar

        Returns:
            dict: Información actualizada del pago con tx_hash

        Raises:
            ValueError: Si el pago no existe
            Exception: Si hay error al enviar transacción
        """
        try:
            # Obtener pago del caché
            payment = self.payments_cache.get(payment_id)
            if not payment:
                raise ValueError(f"Payment not found: {payment_id}")

            logger.info(f"Sending payment transaction: {payment_id}")

            # Enviar transacción a través de blockchain_service
            # Esto es un placeholder - implementación real dependería del contrato
            tx_hash = await self._send_blockchain_transaction(
                recipient=payment["recipient"],
                amount=payment["amount"],
                token_address=payment["token_address"],
            )

            # Actualizar pago con tx_hash
            payment["tx_hash"] = tx_hash
            payment["status"] = "submitted"
            self.tx_hash_to_payment[tx_hash] = payment_id

            logger.info(f"Payment transaction sent: {tx_hash}")

            return payment

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error sending payment transaction: {str(e)}")
            # Marcar pago como fallido
            if payment_id in self.payments_cache:
                self.payments_cache[payment_id]["status"] = "failed"
                self.payments_cache[payment_id]["error"] = str(e)
            raise

    async def get_payment_status(
        self,
        payment_id: Optional[str] = None,
        tx_hash: Optional[str] = None,
    ) -> Dict:
        """
        Obtener estado de un pago por ID o por tx_hash

        Args:
            payment_id: ID del pago (si se conoce)
            tx_hash: Hash de transacción (alternativa a payment_id)

        Returns:
            dict: Información actualizada del pago

        Raises:
            ValueError: Si no se proporcionan parámetros válidos
            Exception: Si hay error al consultar
        """
        try:
            # Determinar qué búsqueda hacer
            if payment_id:
                payment = self.payments_cache.get(payment_id)
                if not payment:
                    raise ValueError(f"Payment not found: {payment_id}")
            elif tx_hash:
                payment_id = self.tx_hash_to_payment.get(tx_hash)
                if not payment_id:
                    raise ValueError(f"No payment found for tx_hash: {tx_hash}")
                payment = self.payments_cache.get(payment_id)
            else:
                raise ValueError("Must provide either payment_id or tx_hash")

            logger.info(f"Getting payment status: {payment_id}")

            # Si hay tx_hash, obtener estado actualizado del blockchain
            if payment.get("tx_hash"):
                tx_status = self.blockchain_service.get_transaction_status(
                    payment["tx_hash"]
                )

                # Actualizar caché con información del blockchain
                payment["status"] = tx_status.get("status", "pending")
                payment["confirmations"] = tx_status.get("confirmations", 0)
                payment["block_number"] = tx_status.get("block_number")

                # Si está confirmado, marcar como completado
                if payment["confirmations"] >= settings.MIN_CONFIRMATIONS:
                    payment["status"] = "success"
                    payment["completed_at"] = datetime.utcnow().isoformat() + "Z"

                logger.info(f"Payment {payment_id} status: {payment['status']}")

            return payment

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            raise

    def get_payment_by_id(self, payment_id: str) -> Optional[Dict]:
        """
        Obtener información de un pago por ID (desde caché local)

        Args:
            payment_id: ID del pago

        Returns:
            dict: Información del pago o None si no existe

        Raises:
            ValueError: Si el ID es inválido
        """
        try:
            if not payment_id or not isinstance(payment_id, str):
                raise ValueError("Invalid payment_id")

            payment = self.payments_cache.get(payment_id)

            if payment:
                logger.debug(f"Payment found: {payment_id}")
            else:
                logger.debug(f"Payment not found: {payment_id}")

            return payment

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise

    def get_all_payments(self) -> List[Dict]:
        """
        Obtener lista de todos los pagos en caché

        Returns:
            list: Lista de pagos
        """
        try:
            payments = list(self.payments_cache.values())
            logger.debug(f"Retrieved {len(payments)} payments from cache")
            return payments

        except Exception as e:
            logger.error(f"Error getting all payments: {str(e)}")
            return []

    def get_payments_by_status(self, status: str) -> List[Dict]:
        """
        Obtener pagos filtrados por estado

        Args:
            status: Estado a filtrar (pending, submitted, success, failed)

        Returns:
            list: Lista de pagos con ese estado
        """
        try:
            valid_statuses = ["pending", "submitted", "success", "failed"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}")

            filtered = [
                p for p in self.payments_cache.values() if p["status"] == status
            ]
            logger.debug(f"Found {len(filtered)} payments with status: {status}")
            return filtered

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise

    async def refresh_payment_status(self, payment_id: str) -> Dict:
        """
        Actualizar estado de un pago consultando blockchain

        Args:
            payment_id: ID del pago

        Returns:
            dict: Información actualizada del pago

        Raises:
            ValueError: Si el pago no existe
            Exception: Si hay error al consultar blockchain
        """
        try:
            payment = self.payments_cache.get(payment_id)
            if not payment:
                raise ValueError(f"Payment not found: {payment_id}")

            if not payment.get("tx_hash"):
                logger.warning(f"Payment {payment_id} has no tx_hash yet")
                return payment

            logger.info(f"Refreshing payment status: {payment_id}")

            # Obtener estado desde blockchain
            return await self.get_payment_status(payment_id=payment_id)

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error refreshing payment status: {str(e)}")
            raise

    async def cancel_payment(self, payment_id: str) -> Dict:
        """
        Cancelar un pago que aún no ha sido enviado

        Args:
            payment_id: ID del pago

        Returns:
            dict: Información del pago cancelado

        Raises:
            ValueError: Si el pago no existe o no puede cancelarse
        """
        try:
            payment = self.payments_cache.get(payment_id)
            if not payment:
                raise ValueError(f"Payment not found: {payment_id}")

            if payment["status"] not in ["pending", "failed"]:
                raise ValueError(
                    f"Cannot cancel payment with status: {payment['status']}"
                )

            payment["status"] = "cancelled"
            logger.info(f"Payment cancelled: {payment_id}")

            return payment

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise

    # Métodos privados/auxiliares

    def _get_token_address(self, stablecoin: str) -> Optional[str]:
        """
        Obtener dirección del contrato de token

        Args:
            stablecoin: Nombre del stablecoin

        Returns:
            str: Dirección del token o None si no está configurado
        """
        token_map = {
            "USDC": settings.USDC_ADDRESS,
            "USDT": settings.USDT_ADDRESS,
            "DAI": settings.DAI_ADDRESS,
        }
        return token_map.get(stablecoin.upper())

    async def _verify_token_allowed(self, token_address: str) -> bool:
        """
        Verificar si un token está permitido en el contrato

        Args:
            token_address: Dirección del token

        Returns:
            bool: True si está permitido
        """
        try:
            if not self.blockchain_service:
                logger.warning("Blockchain service not available")
                return False

            return self.blockchain_service.is_token_allowed(token_address)

        except Exception as e:
            logger.error(f"Error verifying token allowed: {str(e)}")
            return False

    async def _send_blockchain_transaction(
        self,
        recipient: str,
        amount: float,
        token_address: str,
    ) -> str:
        """
        Enviar transacción de pago al blockchain

        Args:
            recipient: Dirección del destinatario
            amount: Cantidad a enviar
            token_address: Dirección del token

        Returns:
            str: Hash de la transacción

        Raises:
            Exception: Si hay error al enviar
        """
        try:
            # Aquí se implementaría la lógica real de envío
            # Por ahora retornamos un hash dummy para demo
            # En producción, esto llamaría a blockchain_service.send_raw_transaction()

            logger.info(
                f"Sending blockchain transaction: {amount} {token_address} to {recipient}"
            )

            # Simular delay de envío
            await asyncio.sleep(0.1)

            # Retornar hash dummy (en producción sería real)
            tx_hash = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"
            logger.info(f"Blockchain transaction sent: {tx_hash}")

            return tx_hash

        except Exception as e:
            logger.error(f"Error sending blockchain transaction: {str(e)}")
            raise

    def get_payment_statistics(self) -> Dict:
        """
        Obtener estadísticas de pagos

        Returns:
            dict: Estadísticas de los pagos
        """
        try:
            all_payments = self.payments_cache.values()

            stats = {
                "total_payments": len(all_payments),
                "pending": len([p for p in all_payments if p["status"] == "pending"]),
                "submitted": len(
                    [p for p in all_payments if p["status"] == "submitted"]
                ),
                "success": len([p for p in all_payments if p["status"] == "success"]),
                "failed": len([p for p in all_payments if p["status"] == "failed"]),
                "cancelled": len(
                    [p for p in all_payments if p["status"] == "cancelled"]
                ),
                "total_amount": sum(p["amount"] for p in all_payments),
                "successful_amount": sum(
                    p["amount"] for p in all_payments if p["status"] == "success"
                ),
            }

            logger.debug(f"Payment statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting payment statistics: {str(e)}")
            return {}


# Instancia global del servicio (se inicializa en main.py)
payment_service = None
