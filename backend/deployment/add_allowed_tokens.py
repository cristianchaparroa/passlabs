"""
Script para agregar tokens permitidos al contrato PaymentProcessor

Este script es CRÍTICO para el funcionamiento del sistema.
Sin ejecutar este script, el contrato no reconocerá ningún token como permitido.

Uso:
    python add_allowed_tokens.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from web3 import Web3

# Cargar variables de entorno
load_dotenv()

# ==================== CONFIGURACIÓN ====================

RPC_URL = os.getenv("RPC_URL", "https://sepolia-rpc.scroll.io/")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "534351"))

# Direcciones de tokens en Scroll Sepolia
TOKENS = {
    "USDC": os.getenv("USDC_ADDRESS", "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"),
    "USDT": os.getenv("USDT_ADDRESS", "0x186C0C26c45A8DA1Da34339ee513624a9609156d"),
    "DAI": os.getenv("DAI_ADDRESS", "0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6"),
}

GAS_LIMIT = 200000
CONFIRMATION_BLOCKS = 1

# ==================== COLORES PARA TERMINAL ====================


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text: str):
    """Imprime un encabezado formateado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text: str):
    """Imprime un mensaje de éxito"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Imprime un mensaje de error"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Imprime un mensaje de advertencia"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text: str):
    """Imprime un mensaje de información"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def load_contract_abi() -> List[Dict]:
    """
    Carga el ABI del contrato desde el archivo JSON

    Returns:
        list: ABI del contrato

    Raises:
        FileNotFoundError: Si no encuentra el archivo ABI
    """
    abi_path = Path(__file__).parent.parent / "contracts" / "contract_abi.json"

    if not abi_path.exists():
        raise FileNotFoundError(f"ABI file not found at {abi_path}")

    with open(abi_path, "r") as f:
        return json.load(f)


def validate_configuration() -> bool:
    """
    Valida que la configuración sea correcta

    Returns:
        bool: True si la configuración es válida
    """
    print_header("🔍 Validando Configuración")

    errors = []

    # Validar RPC URL
    if not RPC_URL:
        errors.append("RPC_URL no configurada")
    else:
        print_info(f"RPC URL: {RPC_URL}")

    # Validar Private Key
    if not PRIVATE_KEY:
        errors.append("PRIVATE_KEY no configurada")
    else:
        print_info(f"Private Key cargada: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-4:]}")

    # Validar Contract Address
    if (
        not CONTRACT_ADDRESS
        or CONTRACT_ADDRESS == "0x0000000000000000000000000000000000000000"
    ):
        errors.append("CONTRACT_ADDRESS no configurada o es dirección cero")
    else:
        print_info(f"Contract Address: {CONTRACT_ADDRESS}")

    # Validar direcciones de tokens
    for token_name, token_address in TOKENS.items():
        if (
            not token_address
            or token_address == "0x0000000000000000000000000000000000000000"
        ):
            errors.append(f"{token_name} address not configured properly")
        else:
            print_info(f"{token_name} Address: {token_address}")

    if errors:
        print_error("❌ Configuración incompleta o inválida:")
        for error in errors:
            print_error(f"   - {error}")
        return False

    print_success("Configuración válida")
    return True


def connect_to_blockchain() -> Tuple[Web3, object]:
    """
    Se conecta a la blockchain usando Web3

    Returns:
        tuple: (Web3 instance, Account object)

    Raises:
        ConnectionError: Si no puede conectarse a la blockchain
        ValueError: Si la clave privada es inválida
    """
    print_header("🔗 Conectando a Blockchain")

    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))

        if not w3.is_connected():
            raise ConnectionError(f"Cannot connect to RPC: {RPC_URL}")

        print_success(f"Conectado a blockchain: {RPC_URL}")

        # Obtener información de la red
        chain_id = w3.eth.chain_id
        block_number = w3.eth.block_number

        print_info(f"Chain ID: {chain_id} (Expected: {CHAIN_ID})")
        print_info(f"Block Number: {block_number}")

        if chain_id != CHAIN_ID:
            print_warning(f"Chain ID mismatch! Expected {CHAIN_ID}, got {chain_id}")

        # Cargar cuenta
        account = w3.eth.account.from_key(PRIVATE_KEY)
        print_success(f"Cuenta cargada: {account.address}")

        # Obtener balance
        balance = w3.eth.get_balance(account.address)
        balance_eth = w3.from_wei(balance, "ether")
        print_info(f"Balance: {balance_eth} ETH")

        if balance == 0:
            print_warning("⚠️  Balance es 0, la transacción puede fallar")

        return w3, account

    except Exception as e:
        print_error(f"Error conectando a blockchain: {str(e)}")
        raise


def load_contract(w3: Web3) -> object:
    """
    Carga la instancia del contrato

    Args:
        w3: Web3 instance

    Returns:
        Contract: Instancia del contrato

    Raises:
        Exception: Si hay error al cargar el contrato
    """
    print_header("📋 Cargando Contrato")

    try:
        abi = load_contract_abi()
        print_success(f"ABI cargado con {len(abi)} elementos")

        contract = w3.eth.contract(
            address=w3.to_checksum_address(CONTRACT_ADDRESS),
            abi=abi,
        )

        print_success(f"Contrato cargado: {CONTRACT_ADDRESS}")

        # Obtener información del contrato
        try:
            owner = contract.functions.owner().call()
            print_info(f"Contract Owner: {owner}")
        except Exception as e:
            print_warning(f"No se pudo obtener owner: {str(e)}")

        return contract

    except Exception as e:
        print_error(f"Error cargando contrato: {str(e)}")
        raise


def check_token_status(contract: object, tokens: Dict[str, str]) -> Dict[str, bool]:
    """
    Verifica el estado actual de cada token

    Args:
        contract: Instancia del contrato
        tokens: Diccionario de tokens

    Returns:
        dict: Estado de cada token (True = permitido, False = no permitido)
    """
    print_header("🔎 Verificando Estado de Tokens")

    status = {}

    for token_name, token_address in tokens.items():
        try:
            checksum_address = Web3.to_checksum_address(token_address)
            is_allowed = contract.functions.isTokenAllowed(checksum_address).call()
            status[token_name] = is_allowed

            if is_allowed:
                print_success(f"{token_name}: ✅ YA PERMITIDO")
            else:
                print_warning(f"{token_name}: ❌ NO PERMITIDO (necesita agregarse)")
        except Exception as e:
            print_error(f"{token_name}: Error al verificar - {str(e)}")
            status[token_name] = False

    return status


def add_allowed_tokens(
    w3: Web3, contract: object, account: object, tokens: Dict[str, str]
) -> List[Tuple[str, str]]:
    """
    Agrega los tokens permitidos al contrato

    Args:
        w3: Web3 instance
        contract: Instancia del contrato
        account: Cuenta del owner
        tokens: Diccionario de tokens

    Returns:
        list: Lista de (token_name, tx_hash) para cada token agregado exitosamente
    """
    print_header("➕ Agregando Tokens Permitidos al Contrato")

    # Primero verificar qué tokens ya están permitidos
    current_status = check_token_status(contract, tokens)

    tokens_to_add = [
        (name, address)
        for name, address in tokens.items()
        if not current_status.get(name, False)
    ]

    if not tokens_to_add:
        print_success("✅ Todos los tokens ya están permitidos en el contrato")
        return []

    print_info(f"\nNecesita agregar {len(tokens_to_add)} token(s):")
    for name, address in tokens_to_add:
        print_info(f"  - {name}: {address}")

    added_tokens = []
    nonce = w3.eth.get_transaction_count(account.address)

    for token_name, token_address in tokens_to_add:
        try:
            print(f"\n{Colors.BOLD}Agregando {token_name}...{Colors.ENDC}")

            checksum_address = w3.to_checksum_address(token_address)

            # Construir transacción
            tx = contract.functions.addAllowedToken(checksum_address).build_transaction(
                {
                    "from": account.address,
                    "nonce": nonce,
                    "gas": GAS_LIMIT,
                    "gasPrice": w3.eth.gas_price,
                }
            )

            print_info(f"  Gas Price: {w3.from_wei(tx['gasPrice'], 'gwei')} Gwei")
            print_info(f"  Estimated Gas: {tx['gas']}")

            # Firmar transacción
            signed_tx = w3.eth.account.sign_transaction(tx, account.key)

            # Enviar transacción
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_str = tx_hash.hex()

            print_info(f"  Transaction Hash: {tx_hash_str}")

            # Esperar confirmación
            print_info(f"  Esperando confirmación...")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt["status"] == 1:
                print_success(f"✅ {token_name} agregado exitosamente")
                print_info(f"   Block: {receipt['blockNumber']}")
                print_info(f"   Gas Used: {receipt['gasUsed']}")
                added_tokens.append((token_name, tx_hash_str))
            else:
                print_error(f"❌ {token_name} falló - Transacción revertida")

            nonce += 1

        except Exception as e:
            print_error(f"Error agregando {token_name}: {str(e)}")

    return added_tokens


def verify_tokens_added(contract: object, tokens: Dict[str, str]):
    """
    Verifica que todos los tokens fueron agregados correctamente

    Args:
        contract: Instancia del contrato
        tokens: Diccionario de tokens
    """
    print_header("✅ Verificando Tokens Agregados")

    all_allowed = True

    for token_name, token_address in tokens.items():
        try:
            checksum_address = Web3.to_checksum_address(token_address)
            is_allowed = contract.functions.isTokenAllowed(checksum_address).call()

            if is_allowed:
                print_success(f"{token_name}: ✅ PERMITIDO en el contrato")
            else:
                print_error(f"{token_name}: ❌ NO PERMITIDO (algo salió mal)")
                all_allowed = False
        except Exception as e:
            print_error(f"{token_name}: Error al verificar - {str(e)}")
            all_allowed = False

    return all_allowed


def save_results(added_tokens: List[Tuple[str, str]]):
    """
    Guarda los resultados en un archivo

    Args:
        added_tokens: Lista de tokens agregados
    """
    results = {
        "timestamp": str(__import__("datetime").datetime.utcnow()),
        "network": "Scroll Sepolia",
        "contract_address": CONTRACT_ADDRESS,
        "tokens_added": [
            {
                "name": name,
                "tx_hash": tx_hash,
            }
            for name, tx_hash in added_tokens
        ],
    }

    output_file = Path(__file__).parent / "add_tokens_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print_info(f"Resultados guardados en: {output_file}")


def main():
    """Función principal"""
    try:
        print_header("🔐 Script para Agregar Tokens Permitidos")
        print_info("Este script agrega USDC, USDT y DAI al contrato PaymentProcessor")
        print_info("Esto es REQUERIDO para que el sistema funcione correctamente")

        # Validar configuración
        if not validate_configuration():
            print_error("Configuración inválida. Por favor revisa el archivo .env")
            sys.exit(1)

        # Conectar a blockchain
        w3, account = connect_to_blockchain()

        # Cargar contrato
        contract = load_contract(w3)

        # Agregar tokens permitidos
        added_tokens = add_allowed_tokens(w3, contract, account, TOKENS)

        # Verificar que los tokens fueron agregados
        if verify_tokens_added(contract, TOKENS):
            print_header("✅ ¡ÉXITO! Todos los tokens están configurados correctamente")
            save_results(added_tokens)
            print_success("El sistema está listo para procesar pagos")
        else:
            print_header("⚠️  ADVERTENCIA")
            print_warning("Algunos tokens no se agregaron correctamente")
            print_warning("Por favor revisa los errores arriba")
            sys.exit(1)

    except KeyboardInterrupt:
        print_warning("\n⚠️  Script interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error fatal: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
