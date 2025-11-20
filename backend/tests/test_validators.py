"""
Tests para los validadores (FASE 5 - Testing & Polish)

Pruebas unitarias para:
- is_valid_ethereum_address()
- is_valid_tx_hash()
- is_valid_amount()
- is_valid_stablecoin()
"""

import sys
from pathlib import Path

import pytest

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validators import (
    is_valid_amount,
    is_valid_ethereum_address,
    is_valid_stablecoin,
    is_valid_tx_hash,
)


class TestEthereumAddressValidator:
    """Tests para validador de direcciones Ethereum"""

    def test_valid_ethereum_address(self):
        """Test dirección Ethereum válida"""
        valid_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb"
        assert is_valid_ethereum_address(valid_address) is True

    def test_valid_ethereum_address_lowercase(self):
        """Test dirección Ethereum válida en minúsculas"""
        valid_address = "0x742d35cc6634c0532925a3b844bc9e7595f1beb"
        assert is_valid_ethereum_address(valid_address) is True

    def test_valid_ethereum_address_uppercase(self):
        """Test dirección Ethereum válida en mayúsculas"""
        valid_address = "0x742D35CC6634C0532925A3B844BC9E7595F1BEB"
        assert is_valid_ethereum_address(valid_address) is True

    def test_invalid_ethereum_address_no_prefix(self):
        """Test dirección sin prefijo 0x"""
        invalid_address = "742d35Cc6634C0532925a3b844Bc9e7595f1bEb"
        assert is_valid_ethereum_address(invalid_address) is False

    def test_invalid_ethereum_address_wrong_prefix(self):
        """Test dirección con prefijo incorrecto"""
        invalid_address = "0y742d35Cc6634C0532925a3b844Bc9e7595f1bEb"
        assert is_valid_ethereum_address(invalid_address) is False

    def test_invalid_ethereum_address_wrong_length(self):
        """Test dirección con longitud incorrecta"""
        invalid_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f1b"
        assert is_valid_ethereum_address(invalid_address) is False

    def test_invalid_ethereum_address_too_long(self):
        """Test dirección demasiado larga"""
        invalid_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEbabc"
        assert is_valid_ethereum_address(invalid_address) is False

    def test_invalid_ethereum_address_non_hex_chars(self):
        """Test dirección con caracteres no hexadecimales"""
        invalid_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f1bZZ"
        assert is_valid_ethereum_address(invalid_address) is False

    def test_invalid_ethereum_address_empty(self):
        """Test dirección vacía"""
        assert is_valid_ethereum_address("") is False

    def test_invalid_ethereum_address_none(self):
        """Test dirección None"""
        assert is_valid_ethereum_address(None) is False

    def test_invalid_ethereum_address_spaces(self):
        """Test dirección con espacios"""
        invalid_address = "0x742d35Cc 6634C0532925a3b844Bc9e7595f1bEb"
        assert is_valid_ethereum_address(invalid_address) is False


class TestTransactionHashValidator:
    """Tests para validador de hashes de transacción"""

    def test_valid_tx_hash(self):
        """Test hash de transacción válido"""
        valid_hash = "0x" + "a" * 64
        assert is_valid_tx_hash(valid_hash) is True

    def test_valid_tx_hash_mixed_case(self):
        """Test hash con caracteres mixtos"""
        valid_hash = "0xaAbBcCdDeEfF" + "a" * 52
        assert is_valid_tx_hash(valid_hash) is True

    def test_valid_tx_hash_all_zeros(self):
        """Test hash con todos ceros"""
        valid_hash = "0x" + "0" * 64
        assert is_valid_tx_hash(valid_hash) is True

    def test_invalid_tx_hash_no_prefix(self):
        """Test hash sin prefijo 0x"""
        invalid_hash = "a" * 64
        assert is_valid_tx_hash(invalid_hash) is False

    def test_invalid_tx_hash_wrong_length(self):
        """Test hash con longitud incorrecta"""
        invalid_hash = "0x" + "a" * 63
        assert is_valid_tx_hash(invalid_hash) is False

    def test_invalid_tx_hash_too_long(self):
        """Test hash demasiado largo"""
        invalid_hash = "0x" + "a" * 65
        assert is_valid_tx_hash(invalid_hash) is False

    def test_invalid_tx_hash_non_hex_chars(self):
        """Test hash con caracteres no hexadecimales"""
        invalid_hash = "0x" + "z" * 64
        assert is_valid_tx_hash(invalid_hash) is False

    def test_invalid_tx_hash_empty(self):
        """Test hash vacío"""
        assert is_valid_tx_hash("") is False

    def test_invalid_tx_hash_none(self):
        """Test hash None"""
        assert is_valid_tx_hash(None) is False

    def test_invalid_tx_hash_spaces(self):
        """Test hash con espacios"""
        invalid_hash = "0x" + "a" * 32 + " " + "a" * 32
        assert is_valid_tx_hash(invalid_hash) is False


class TestAmountValidator:
    """Tests para validador de cantidades"""

    def test_valid_amount_minimum(self):
        """Test cantidad en mínimo válido"""
        assert is_valid_amount(0.01) is True

    def test_valid_amount_just_above_minimum(self):
        """Test cantidad justo arriba del mínimo"""
        assert is_valid_amount(0.011) is True

    def test_valid_amount_middle_range(self):
        """Test cantidad en rango medio"""
        assert is_valid_amount(100.50) is True

    def test_valid_amount_maximum(self):
        """Test cantidad en máximo válido"""
        assert is_valid_amount(1_000_000) is True

    def test_valid_amount_integer(self):
        """Test cantidad como entero"""
        assert is_valid_amount(100) is True

    def test_valid_amount_large_decimal(self):
        """Test cantidad con muchos decimales"""
        assert is_valid_amount(999_999.99) is True

    def test_invalid_amount_too_small(self):
        """Test cantidad menor que mínimo"""
        assert is_valid_amount(0.001) is False

    def test_invalid_amount_zero(self):
        """Test cantidad cero"""
        assert is_valid_amount(0) is False

    def test_invalid_amount_negative(self):
        """Test cantidad negativa"""
        assert is_valid_amount(-100) is False

    def test_invalid_amount_too_large(self):
        """Test cantidad mayor que máximo"""
        assert is_valid_amount(2_000_000) is False

    def test_invalid_amount_string(self):
        """Test cantidad como string"""
        assert is_valid_amount("100.50") is False

    def test_invalid_amount_none(self):
        """Test cantidad None"""
        assert is_valid_amount(None) is False

    def test_valid_amount_custom_range(self):
        """Test cantidad con rango personalizado"""
        assert is_valid_amount(50, min_amount=10, max_amount=100) is True

    def test_invalid_amount_custom_range_too_small(self):
        """Test cantidad por debajo de rango personalizado"""
        assert is_valid_amount(5, min_amount=10, max_amount=100) is False

    def test_invalid_amount_custom_range_too_large(self):
        """Test cantidad por encima de rango personalizado"""
        assert is_valid_amount(150, min_amount=10, max_amount=100) is False


class TestStablecoinValidator:
    """Tests para validador de stablecoins"""

    def test_valid_stablecoin_usdc(self):
        """Test USDC es válido"""
        assert is_valid_stablecoin("USDC") is True

    def test_valid_stablecoin_usdt(self):
        """Test USDT es válido"""
        assert is_valid_stablecoin("USDT") is True

    def test_valid_stablecoin_dai(self):
        """Test DAI es válido"""
        assert is_valid_stablecoin("DAI") is True

    def test_valid_stablecoin_lowercase(self):
        """Test stablecoin en minúsculas"""
        assert is_valid_stablecoin("usdc") is True

    def test_valid_stablecoin_mixed_case(self):
        """Test stablecoin en minúsculas/mayúsculas"""
        assert is_valid_stablecoin("UsDc") is True

    def test_invalid_stablecoin_not_supported(self):
        """Test stablecoin no soportado"""
        assert is_valid_stablecoin("BUSD") is False

    def test_invalid_stablecoin_fake(self):
        """Test stablecoin falso"""
        assert is_valid_stablecoin("FAKE") is False

    def test_invalid_stablecoin_empty(self):
        """Test stablecoin vacío"""
        assert is_valid_stablecoin("") is False

    def test_invalid_stablecoin_none(self):
        """Test stablecoin None"""
        assert is_valid_stablecoin(None) is False

    def test_valid_stablecoin_custom_list(self):
        """Test stablecoin con lista personalizada"""
        assert is_valid_stablecoin("CUSTOM", valid_coins=["CUSTOM", "OTHER"]) is True

    def test_invalid_stablecoin_custom_list(self):
        """Test stablecoin no en lista personalizada"""
        assert is_valid_stablecoin("UNKNOWN", valid_coins=["CUSTOM", "OTHER"]) is False

    def test_valid_stablecoin_case_insensitive_custom(self):
        """Test stablecoin case-insensitive con lista personalizada"""
        assert is_valid_stablecoin("custom", valid_coins=["CUSTOM", "OTHER"]) is True


class TestValidatorsIntegration:
    """Tests de integración de validadores"""

    def test_complete_payment_validation(self):
        """Test validación completa de pago"""
        # Dirección válida
        address = "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb"
        assert is_valid_ethereum_address(address) is True

        # Cantidad válida
        amount = 100.50
        assert is_valid_amount(amount) is True

        # Stablecoin válido
        stablecoin = "USDC"
        assert is_valid_stablecoin(stablecoin) is True

    def test_invalid_payment_multiple_errors(self):
        """Test pago inválido con múltiples errores"""
        # Dirección inválida
        address = "invalid"
        assert is_valid_ethereum_address(address) is False

        # Cantidad inválida
        amount = 0.001
        assert is_valid_amount(amount) is False

        # Stablecoin inválido
        stablecoin = "FAKE"
        assert is_valid_stablecoin(stablecoin) is False

    def test_tx_status_check_validation(self):
        """Test validación para verificar estado de tx"""
        # Hash válido
        tx_hash = "0x" + "abc123" + "d" * 58
        assert is_valid_tx_hash(tx_hash) is True

    def test_validators_edge_cases(self):
        """Test casos extremos de validadores"""
        # Dirección con caracteres especiales permitidos
        address = "0x" + "F" * 40
        assert is_valid_ethereum_address(address) is True

        # Hash con todos números
        tx_hash = "0x" + "1" * 64
        assert is_valid_tx_hash(tx_hash) is True

        # Cantidad mínima
        assert is_valid_amount(0.01) is True

        # Stablecoin en lista por defecto
        assert is_valid_stablecoin("USDC") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
