import re
from typing import Optional


def is_valid_ethereum_address(address: str) -> bool:
    """
    Validar que una dirección sea una dirección Ethereum válida

    Args:
        address: Dirección a validar

    Returns:
        bool: True si es válida, False en caso contrario
    """
    if not address:
        return False

    # Debe comenzar con 0x y tener 42 caracteres
    if not address.startswith("0x") or len(address) != 42:
        return False

    # Debe ser hexadecimal
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def is_valid_tx_hash(tx_hash: str) -> bool:
    """
    Validar que un hash de transacción sea válido

    Args:
        tx_hash: Hash de transacción a validar

    Returns:
        bool: True si es válido, False en caso contrario
    """
    if not tx_hash:
        return False

    # Debe comenzar con 0x y tener 66 caracteres
    if not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return False

    # Debe ser hexadecimal
    try:
        int(tx_hash, 16)
        return True
    except ValueError:
        return False


def is_valid_amount(
    amount: float, min_amount: float = 0.01, max_amount: float = 1_000_000
) -> bool:
    """
    Validar que una cantidad sea válida

    Args:
        amount: Cantidad a validar
        min_amount: Cantidad mínima
        max_amount: Cantidad máxima

    Returns:
        bool: True si es válida, False en caso contrario
    """
    if not isinstance(amount, (int, float)):
        return False

    if amount < min_amount or amount > max_amount:
        return False

    return True


def is_valid_stablecoin(stablecoin: str, valid_coins: list = None) -> bool:
    """
    Validar que un stablecoin sea soportado

    Args:
        stablecoin: Stablecoin a validar
        valid_coins: Lista de stablecoins válidos

    Returns:
        bool: True si es válido, False en caso contrario
    """
    if valid_coins is None:
        valid_coins = ["USDC", "USDT", "DAI"]

    return stablecoin.upper() in valid_coins
