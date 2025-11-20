import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from models.payment import CreatePaymentRequest
from services.blockchain_service import blockchain_service
from services.payment_service import PaymentService
from utils.logger import get_logger
from utils.validators import is_valid_tx_hash

logger = get_logger(__name__)

router = APIRouter()

# Variable global para acceder al payment_service desde main.py
payment_service_instance: Optional[PaymentService] = None


def set_payment_service(service: PaymentService):
    """
    Establecer la instancia del payment_service
    Se llama desde main.py durante startup
    """
    global payment_service_instance
    payment_service_instance = service
    logger.info("✅ Payment service instance set in routes")


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_payment(request: CreatePaymentRequest):
    """
    Crear un nuevo pago en blockchain

    Endpoint: POST /payments/create

    Args:
        request: CreatePaymentRequest con:
            - recipient_address: Dirección del destinatario (0x...)
            - amount: Cantidad a pagar
            - stablecoin: Tipo de stablecoin (USDC, USDT, DAI)
            - description: Descripción del pago (opcional)

    Returns:
        dict: Información del pago creado con tx_hash

    Raises:
        HTTPException 400: Validación fallida
        HTTPException 500: Error interno del servidor
    """
    try:
        if payment_service_instance is None:
            logger.error("Payment service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment service not available",
            )

        logger.info(
            f"📝 Creating payment request: {request.amount} {request.stablecoin} to {request.recipient_address}"
        )

        # Llamar al servicio de pagos
        payment_data = await payment_service_instance.create_payment(
            recipient_address=request.recipient_address,
            amount=request.amount,
            stablecoin=request.stablecoin,
            description=request.description or "",
        )

        logger.info(f"✅ Payment created successfully: {payment_data['payment_id']}")

        return {
            "success": True,
            "message": "Payment created successfully",
            "data": payment_data,
        }

    except ValueError as e:
        logger.warning(f"⚠️  Validation error creating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"❌ Error creating payment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating payment",
        )


@router.get("/status/{tx_hash}")
async def get_payment_status(tx_hash: str):
    """
    Verificar estado de una transacción en blockchain

    Endpoint: GET /payments/status/{tx_hash}

    Args:
        tx_hash: Hash de la transacción (0x...)

    Returns:
        dict: Estado de la transacción con información actualizada

    Raises:
        HTTPException 400: Hash de transacción inválido
        HTTPException 404: Transacción no encontrada
        HTTPException 500: Error interno del servidor
    """
    try:
        # Validar formato del tx_hash
        if not is_valid_tx_hash(tx_hash):
            logger.warning(f"⚠️  Invalid tx_hash format: {tx_hash}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid transaction hash format. Must be 0x followed by 64 hex characters",
            )

        logger.info(f"🔍 Checking payment status for tx_hash: {tx_hash}")

        if payment_service_instance is None:
            logger.error("Payment service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment service not available",
            )

        # Obtener estado del pago
        payment_data = await payment_service_instance.get_payment_status(
            tx_hash=tx_hash
        )

        logger.info(
            f"✅ Payment status retrieved: {payment_data['payment_id']} - {payment_data['status']}"
        )

        return {
            "success": True,
            "data": payment_data,
        }

    except ValueError as e:
        logger.warning(f"⚠️  Payment not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting payment status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payment status",
        )


@router.get("/by-id/{payment_id}")
async def get_payment_by_id(payment_id: str):
    """
    Obtener información de un pago por su ID

    Endpoint: GET /payments/by-id/{payment_id}

    Args:
        payment_id: ID del pago (UUID)

    Returns:
        dict: Información del pago

    Raises:
        HTTPException 404: Pago no encontrado
        HTTPException 500: Error interno del servidor
    """
    try:
        logger.info(f"🔍 Getting payment by ID: {payment_id}")

        if payment_service_instance is None:
            logger.error("Payment service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment service not available",
            )

        # Obtener pago del caché
        payment_data = await payment_service_instance.get_payment_status(
            payment_id=payment_id
        )

        logger.info(f"✅ Payment retrieved: {payment_id}")

        return {
            "success": True,
            "data": payment_data,
        }

    except ValueError as e:
        logger.warning(f"⚠️  Payment not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"❌ Error getting payment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payment",
        )


@router.get("/all")
async def get_all_payments():
    """
    Obtener lista de todos los pagos registrados

    Endpoint: GET /payments/all

    Returns:
        dict: Lista de pagos

    Raises:
        HTTPException 500: Error interno del servidor
    """
    try:
        logger.info("📋 Getting all payments")

        if payment_service_instance is None:
            logger.error("Payment service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment service not available",
            )

        # Obtener todos los pagos
        all_payments = payment_service_instance.get_all_payments()

        logger.info(f"✅ Retrieved {len(all_payments)} payments")

        return {
            "success": True,
            "data": {
                "total": len(all_payments),
                "payments": all_payments,
            },
        }

    except Exception as e:
        logger.error(f"❌ Error getting all payments: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payments",
        )


@router.get("/by-status/{status_filter}")
async def get_payments_by_status(status_filter: str):
    """
    Obtener pagos filtrados por estado

    Endpoint: GET /payments/by-status/{status}

    Args:
        status_filter: Estado a filtrar (pending, completed, failed)

    Returns:
        dict: Lista de pagos con el estado especificado

    Raises:
        HTTPException 400: Estado inválido
        HTTPException 500: Error interno del servidor
    """
    try:
        valid_statuses = ["pending", "completed", "failed", "success"]

        if status_filter.lower() not in valid_statuses:
            logger.warning(f"⚠️  Invalid status filter: {status_filter}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )

        logger.info(f"🔍 Getting payments with status: {status_filter}")

        if payment_service_instance is None:
            logger.error("Payment service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment service not available",
            )

        # Obtener pagos por estado
        filtered_payments = payment_service_instance.get_payments_by_status(
            status_filter.lower()
        )

        logger.info(
            f"✅ Retrieved {len(filtered_payments)} payments with status {status_filter}"
        )

        return {
            "success": True,
            "data": {
                "status": status_filter,
                "total": len(filtered_payments),
                "payments": filtered_payments,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting payments by status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payments",
        )
