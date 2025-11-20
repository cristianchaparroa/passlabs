"""
Script de diagnóstico rápido para verificar el estado del contrato y los tokens

Este script NO modifica nada, solo verifica y reporta el estado actual.

Uso:
    python check_tokens_status.py
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

# Cargar variables de entorno
load_dotenv()

# ==================== CONFIGURACIÓN ====================

RPC_URL = os.getenv("RPC_URL", "https://sepolia-rpc.scroll.io/")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "534351"))

TOKENS = {
    "USDC": os.getenv("USDC_ADDRESS", "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"),
    "USDT": os.getenv("USDT_ADDRESS", "0x186C0C26c45A8DA1Da34339ee513624a9609156d"),
    "DAI": os.getenv("DAI_ADDRESS", "0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6"),
}

# ==================== COLORES ====================


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_section(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_ok(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")


def print_fail(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")


def print_warn(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")


def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")


def check_env():
    """Verifica variables de entorno"""
    print_section("🔍 Verificando Variables de Entorno")

    issues = []

    if not RPC_URL:
        print_fail("RPC_URL no configurada")
        issues.append("RPC_URL")
    else:
        print_ok(f"RPC_URL: {RPC_URL}")

    if not PRIVATE_KEY:
        print_fail("PRIVATE_KEY no configurada")
        issues.append("PRIVATE_KEY")
    else:
        key_preview = PRIVATE_KEY[:10] + "..." + PRIVATE_KEY[-4:]
        print_ok(f"PRIVATE_KEY: {key_preview}")

    if (
        not CONTRACT_ADDRESS
        or CONTRACT_ADDRESS == "0x0000000000000000000000000000000000000000"
    ):
        print_fail(f"CONTRACT_ADDRESS no configurada o es cero: {CONTRACT_ADDRESS}")
        issues.append("CONTRACT_ADDRESS")
    else:
        print_ok(f"CONTRACT_ADDRESS: {CONTRACT_ADDRESS}")

    for token_name, token_addr in TOKENS.items():
        if not token_addr or token_addr == "0x0000000000000000000000000000000000000000":
            print_fail(f"{token_name}_ADDRESS no configurada o es cero")
            issues.append(f"{token_name}_ADDRESS")
        else:
            print_ok(f"{token_name}_ADDRESS: {token_addr}")

    if issues:
        print(f"\n{Colors.FAIL}❌ Falta configurar: {', '.join(issues)}{Colors.ENDC}")
        print_info("Edita el archivo .env y agrega las variables faltantes")
        return False

    print_ok("Todas las variables de entorno están configuradas")
    return True


def check_connection():
    """Verifica conexión a blockchain"""
    print_section("🔗 Verificando Conexión a Blockchain")

    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))

        if not w3.is_connected():
            print_fail(f"No se puede conectar a {RPC_URL}")
            return None

        print_ok(f"Conectado a: {RPC_URL}")

        chain_id = w3.eth.chain_id
        print_info(f"Chain ID: {chain_id} (Esperado: {CHAIN_ID})")

        if chain_id != CHAIN_ID:
            print_warn(f"Chain ID mismatch! Esperado {CHAIN_ID}, obtenido {chain_id}")

        block_number = w3.eth.block_number
        print_info(f"Bloque actual: {block_number}")

        return w3

    except Exception as e:
        print_fail(f"Error de conexión: {str(e)}")
        return None


def check_account(w3):
    """Verifica la cuenta y su balance"""
    print_section("👤 Verificando Cuenta")

    try:
        account = w3.eth.account.from_key(PRIVATE_KEY)
        print_ok(f"Dirección: {account.address}")

        balance = w3.eth.get_balance(account.address)
        balance_eth = w3.from_wei(balance, "ether")
        print_info(f"Balance: {balance_eth} ETH")

        if balance == 0:
            print_fail("¡Balance es 0! Necesitas ETH para pagar el gas")
            print_info(
                "Obtén testnet ETH en: https://scroll-testnet-faucet.allthatnode.com:3001/"
            )
            return account, False

        if balance_eth < 0.01:
            print_warn(f"Balance muy bajo ({balance_eth} ETH). Podrías necesitar más.")

        return account, True

    except Exception as e:
        print_fail(f"Error al cargar cuenta: {str(e)}")
        return None, False


def check_contract(w3):
    """Verifica el contrato"""
    print_section("📋 Verificando Contrato")

    try:
        abi_path = Path(__file__).parent / "contracts" / "contract_abi.json"

        if not abi_path.exists():
            print_fail(f"ABI no encontrado en {abi_path}")
            return None

        with open(abi_path, "r") as f:
            abi = json.load(f)

        print_ok(f"ABI cargado ({len(abi)} elementos)")

        contract = w3.eth.contract(
            address=w3.to_checksum_address(CONTRACT_ADDRESS),
            abi=abi,
        )

        print_ok(f"Contrato cargado: {CONTRACT_ADDRESS}")

        # Obtener owner
        try:
            owner = contract.functions.owner().call()
            print_info(f"Contract Owner: {owner}")
            return contract, owner
        except Exception as e:
            print_warn(f"No se pudo obtener owner: {str(e)}")
            return contract, None

    except Exception as e:
        print_fail(f"Error cargando contrato: {str(e)}")
        return None, None


def check_tokens(contract):
    """Verifica el estado de los tokens"""
    print_section("🎫 Verificando Tokens")

    if not contract:
        print_fail("Contrato no disponible")
        return False

    all_allowed = True

    for token_name, token_addr in TOKENS.items():
        try:
            checksum_addr = Web3.to_checksum_address(token_addr)
            is_allowed = contract.functions.isTokenAllowed(checksum_addr).call()

            if is_allowed:
                print_ok(f"{token_name}: ✅ PERMITIDO")
            else:
                print_fail(f"{token_name}: ❌ NO PERMITIDO")
                all_allowed = False

        except Exception as e:
            print_fail(f"{token_name}: Error al verificar - {str(e)}")
            all_allowed = False

    return all_allowed


def print_recommendations(
    env_ok, connected, has_balance, contract_ok, tokens_ok, owner
):
    """Imprime recomendaciones basadas en los resultados"""
    print_section("📋 Recomendaciones")

    if not env_ok:
        print_fail("Paso 1: Configura las variables de entorno en .env")
        return

    if not connected:
        print_fail("Paso 1: Verifica que RPC_URL es correcto")
        return

    if not has_balance:
        print_fail("Paso 2: Obtén ETH en Scroll Sepolia")
        print_info("  - Faucet: https://scroll-testnet-faucet.allthatnode.com:3001/")
        print_info("  - Puente: https://scroll.io/bridge")
        return

    if not contract_ok:
        print_fail("Paso 3: Verifica que CONTRACT_ADDRESS es correcto")
        print_info("  - Desplega el contrato si no existe")
        print_info("  - O actualiza CONTRACT_ADDRESS en .env")
        return

    if not tokens_ok:
        print_fail("Paso 4: Ejecuta el script para agregar tokens")
        print_info("  python deployment/add_allowed_tokens.py")
        return

    print_ok("✅ ¡TODO ESTÁ CONFIGURADO CORRECTAMENTE!")
    print_ok("El sistema está listo para procesar pagos")


def main():
    try:
        print(f"{Colors.BOLD}🔍 DIAGNÓSTICO DEL SISTEMA DE PAGOS{Colors.ENDC}")

        # Verificar entorno
        env_ok = check_env()

        if not env_ok:
            print_recommendations(False, False, False, False, False, None)
            sys.exit(1)

        # Verificar conexión
        w3 = check_connection()

        if not w3:
            print_recommendations(True, False, False, False, False, None)
            sys.exit(1)

        # Verificar cuenta
        account, has_balance = check_account(w3)

        if not account or not has_balance:
            print_recommendations(True, True, False, False, False, None)
            sys.exit(1)

        # Verificar contrato
        contract, owner = check_contract(w3)

        if not contract:
            print_recommendations(True, True, True, False, False, None)
            sys.exit(1)

        # Verificar tokens
        tokens_ok = check_tokens(contract)

        # Imprimir recomendaciones
        print_recommendations(True, True, True, True, tokens_ok, owner)

        if tokens_ok:
            print(
                f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Puedes procesar pagos ahora!{Colors.ENDC}\n"
            )
        else:
            print(
                f"\n{Colors.FAIL}{Colors.BOLD}❌ Ejecuta: python deployment/add_allowed_tokens.py{Colors.ENDC}\n"
            )
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrumpido por el usuario{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print_fail(f"Error fatal: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
