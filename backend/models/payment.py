from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class StablecoinEnum(str, Enum):
    """Stablecoins soportadas"""

    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"


class PaymentStatusEnum(str, Enum):
    """Estados de pago"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class CreatePaymentRequest(BaseModel):
    """Request para crear un pago"""

    recipient_address: str = Field(
        ..., description="Dirección del destinatario (0x...)"
    )
    amount: float = Field(..., gt=0, description="Cantidad a pagar")
    stablecoin: StablecoinEnum = Field(
        ..., description="Tipo de stablecoin (USDC, USDT, DAI)"
    )
    description: Optional[str] = Field("", description="Descripción del pago")

    @validator("recipient_address")
    def validate_recipient_address(cls, v):
        """Validar que sea una dirección Ethereum válida"""
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError(
                "Dirección inválida. Debe comenzar con 0x y tener 42 caracteres"
            )
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("Dirección inválida. Contiene caracteres no hexadecimales")
        return v

    @validator("amount")
    def validate_amount(cls, v):
        """Validar que la cantidad sea razonable"""
        if v > 1_000_000:
            raise ValueError("Cantidad demasiado alta (máximo 1,000,000)")
        if v < 0.01:
            raise ValueError("Cantidad mínima es 0.01")
        return v


class PaymentData(BaseModel):
    """Datos de un pago"""

    payment_id: str
    tx_hash: str
    recipient: str
    amount: float
    stablecoin: str
    status: str
    description: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class PaymentResponse(BaseModel):
    """Response para crear un pago"""

    success: bool
    message: str
    data: PaymentData


class PaymentStatusResponse(BaseModel):
    """Response para verificar estado de pago"""

    success: bool
    data: dict = Field(..., description="Información del estado de la transacción")


class ErrorResponse(BaseModel):
    """Response de error"""

    success: bool = False
    error: str
    message: str
