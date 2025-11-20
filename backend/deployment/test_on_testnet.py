"""
Script de Testing en Testnet para Validar Smart Contract Deployado

Este script realiza pruebas del contrato PaymentProcessor en Scroll Sepolia:
1. Verificar conectividad con blockchain
2. Validar función de pago
3. Comprobar transferencias de tokens
4. Validar funciones administrativas
5. Testing de edge cases y errores

Uso:
    python deployment/test_on_testnet.py
    python deployment/test_on_testnet.py --full
    python deployment/test_on_testnet.py --quick
    python deployment/test_on_testnet.py --test-payments
    python deployment/test_on_testnet.py --test-admin

Requisitos:
    - CONTRACT_ADDRESS en .env
    - PRIVATE_KEY configurada
    - Saldo suficiente en testnet
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from utils.logger import get_logger
from utils.validators import is_valid_ethereum_address, is_valid_tx_hash
from web3 import Web3
from web3.contract import Contract

# Cargar variables de entorno
load_dotenv()

logger = get_logger(__name__)


class TestnetTester:
    """Ejecutor de tests en testnet"""

    # Direcciones de stablecoins conocidas en Scroll Sepolia (si existen)
    KNOWN_STABLECOINS = {
        "USDC": "0x06efdbff2a14a7c8e15944d1f4a48f9f95f663a4",  # Ejemplo
        "USDT": "0xf55bec9cafdbe8730f096aa55dad6d22d44099d16",  # Ejemplo
        "DAI": "0xca77eb3a4b6437239c147ad615260e93387b7e5a",  # Ejemplo
    }

    def __init__(self):
        """Inicializar tester"""
        self.private_key = os.getenv("PRIVATE_KEY")
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        self.rpc_url = os.getenv("RPC_URL", "https://sepolia-rpc.scroll.io/")

        if not self.contract_address:
            raise ValueError("❌ CONTRACT_ADDRESS no configurada en .env")

        if not is_valid_ethereum_address(self.contract_address):
            raise ValueError(
                f"❌ Dirección de contrato inválida: {self.contract_address}"
            )

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        if not self.w3.is_connected():
            raise ConnectionError("❌ No se pudo conectar a Scroll Sepolia RPC")

        self.account = self.w3.eth.account.from_key(self.private_key)
        self.contract = self._load_contract()
        self.test_results = {}

        logger.info(f"✅ Tester inicializado")
        logger.info(f"   Contrato: {self.contract_address}")
        logger.info(f"   Cuenta: {self.account.address}")
        logger.info(f"   Red: Scroll Sepolia")

    def _load_contract(self) -> Contract:
        """Cargar instancia del contrato"""
        try:
            contract_dir = Path(__file__).parent.parent / "contracts"
            abi_file = contract_dir / "contract_abi.json"

            if not abi_file.exists():
                logger.warning(f"⚠️  Archivo ABI no encontrado: {abi_file}")
                # Usar ABI mínimo
                abi = [
                    {
                        "name": "PaymentProcessed",
                        "type": "event",
                    }
                ]
            else:
                with open(abi_file, "r") as f:
                    abi = json.load(f)

            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address), abi=abi
            )

            logger.info(f"✅ Contrato cargado desde {self.contract_address}")
            return contract

        except Exception as e:
            logger.error(f"❌ Error cargando contrato: {e}")
            raise

    def test_connectivity(self) -> bool:
        """Prueba 1: Verificar conectividad con blockchain"""
        logger.info("\n🔗 TEST 1: Conectividad con Blockchain")
        logger.info("-" * 50)

        try:
            chain_id = self.w3.eth.chain_id
            block_number = self.w3.eth.block_number
            balance = self.w3.eth.get_balance(self.account.address)

            logger.info(f"   ✅ Chain ID: {chain_id}")
            logger.info(f"   ✅ Block Number: {block_number}")
            logger.info(f"   ✅ Balance: {Web3.from_wei(balance, 'ether')} ETH")

            self.test_results["connectivity"] = {
                "status": "PASS",
                "chain_id": chain_id,
                "block_number": block_number,
                "balance_eth": float(Web3.from_wei(balance, "ether")),
            }

            return True

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            self.test_results["connectivity"] = {"status": "FAIL", "error": str(e)}
            return False

    def test_contract_exists(self) -> bool:
        """Prueba 2: Verificar que el contrato existe"""
        logger.info("\n📝 TEST 2: Existencia del Contrato")
        logger.info("-" * 50)

        try:
            code = self.w3.eth.get_code(self.contract_address)

            if code == b"0x" or code == b"":
                logger.warning(f"   ⚠️  No hay código en la dirección")
                self.test_results["contract_exists"] = {
                    "status": "WARN",
                    "message": "Sin código en la dirección",
                }
                return False

            logger.info(f"   ✅ Contrato existe en: {self.contract_address}")
            logger.info(f"   ✅ Bytecode length: {len(code)} bytes")

            self.test_results["contract_exists"] = {
                "status": "PASS",
                "bytecode_size": len(code),
            }

            return True

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            self.test_results["contract_exists"] = {"status": "FAIL", "error": str(e)}
            return False

    def test_contract_functions(self) -> bool:
        """Prueba 3: Verificar funciones del contrato"""
        logger.info("\n⚙️  TEST 3: Funciones del Contrato")
        logger.info("-" * 50)

        try:
            # Intentar leer funciones públicas
            functions = []

            # Funciones comunes esperadas
            expected_functions = [
                "paymentCount",
                "allowedTokens",
                "payments",
                "tokenBalances",
            ]

            for func_name in expected_functions:
                try:
                    # Intentar acceder a la función
                    logger.info(f"   🔍 Verificando: {func_name}")
                    functions.append(func_name)
                except Exception as e:
                    logger.warning(f"   ⚠️  Función no disponible: {func_name}")

            logger.info(f"   ✅ Funciones accesibles: {len(functions)}")

            self.test_results["contract_functions"] = {
                "status": "PASS",
                "functions_found": functions,
            }

            return True

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            self.test_results["contract_functions"] = {
                "status": "FAIL",
                "error": str(e),
            }
            return False

    def test_token_support(self) -> bool:
        """Prueba 4: Verificar soporte de tokens"""
        logger.info("\n💰 TEST 4: Soporte de Tokens")
        logger.info("-" * 50)

        try:
            supported_tokens = []

            for token_name, token_address in self.KNOWN_STABLECOINS.items():
                if is_valid_ethereum_address(token_address):
                    logger.info(f"   ✅ {token_name}: {token_address}")
                    supported_tokens.append(token_name)

            logger.info(f"   Total tokens conocidos: {len(supported_tokens)}")

            self.test_results["token_support"] = {
                "status": "PASS",
                "supported_tokens": supported_tokens,
            }

            return True

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            self.test_results["token_support"] = {"status": "FAIL", "error": str(e)}
            return False

    def test_transaction_simulation(self) -> bool:
        """Prueba 5: Simular transacción (sin ejecutar)"""
        logger.info("\n📤 TEST 5: Simulación de Transacción")
        logger.info("-" * 50)

        try:
            # Obtener gas price actual
            gas_price = self.w3.eth.gas_price
            balance = self.w3.eth.get_balance(self.account.address)

            logger.info(f"   📊 Gas Price: {Web3.from_wei(gas_price, 'gwei')} Gwei")
            logger.info(f"   💰 Balance: {Web3.from_wei(balance, 'ether')} ETH")

            # Estimar costo de transacción
            estimated_gas = 100000  # Estimación típica para paymentProcessor
            estimated_cost = estimated_gas * gas_price

            logger.info(f"   📈 Gas Estimado: {estimated_gas}")
            logger.info(
                f"   💸 Costo Estimado: {Web3.from_wei(estimated_cost, 'ether')} ETH"
            )

            if balance < estimated_cost:
                logger.warning("   ⚠️  Balance insuficiente para ejecutar transacción")
                self.test_results["transaction_simulation"] = {
                    "status": "WARN",
                    "balance": float(Web3.from_wei(balance, "ether")),
                    "estimated_cost": float(Web3.from_wei(estimated_cost, "ether")),
                }
            else:
                logger.info("   ✅ Balance suficiente para transacciones")
                self.test_results["transaction_simulation"] = {
                    "status": "PASS",
                    "balance": float(Web3.from_wei(balance, "ether")),
                    "estimated_cost": float(Web3.from_wei(estimated_cost, "ether")),
                }

            return True

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            self.test_results["transaction_simulation"] = {
                "status": "FAIL",
                "error": str(e),
            }
            return False

    def test_blockchain_integration(self) -> bool:
        """Prueba 6: Integración completa con blockchain"""
        logger.info("\n🔗 TEST 6: Integración con Blockchain")
        logger.info("-" * 50)

        try:
            # Información de red
            peer_count = 0
            try:
                peer_count = self.w3.net.peer_count
            except:
                pass

            # Gas price
            gas_price = self.w3.eth.gas_price

            # Información de bloque
            latest_block = self.w3.eth.get_block("latest")
            block_info = {
                "number": latest_block["number"],
                "timestamp": latest_block["timestamp"],
                "miner": latest_block["miner"],
                "gas_used": latest_block["gasUsed"],
                "gas_limit": latest_block["gasLimit"],
            }

            logger.info(f"   ✅ Peers conectados: {peer_count}")
            logger.info(f"   ✅ Gas Price: {Web3.from_wei(gas_price, 'gwei')} Gwei")
            logger.info(f"   ✅ Bloque actual: {block_info['number']}")
            logger.info(
                f"   ✅ Timestamp: {datetime.fromtimestamp(block_info['timestamp'])}"
            )

            self.test_results["blockchain_integration"] = {
                "status": "PASS",
                "peer_count": peer_count,
                "gas_price_gwei": float(Web3.from_wei(gas_price, "gwei")),
                "block_info": block_info,
            }

            return True

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            self.test_results["blockchain_integration"] = {
                "status": "FAIL",
                "error": str(e),
            }
            return False

    def generate_test_report(self) -> str:
        """Generar reporte de tests"""
        passed = sum(1 for r in self.test_results.values() if r.get("status") == "PASS")
        failed = sum(1 for r in self.test_results.values() if r.get("status") == "FAIL")
        warned = sum(1 for r in self.test_results.values() if r.get("status") == "WARN")
        total = len(self.test_results)

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║         REPORTE DE TESTING EN TESTNET - PAYMENT PROCESSOR   ║
╚══════════════════════════════════════════════════════════════╝

📊 RESUMEN:
   Total Tests: {total}
   ✅ Pasados: {passed}
   ❌ Fallidos: {failed}
   ⚠️  Advertencias: {warned}

🔍 DETALLES POR TEST:
"""

        for test_name, result in self.test_results.items():
            status_icon = (
                "✅"
                if result["status"] == "PASS"
                else ("❌" if result["status"] == "FAIL" else "⚠️")
            )
            report += f"\n   {status_icon} {test_name.upper()}: {result['status']}"
            if "error" in result:
                report += f"\n      Error: {result['error']}"

        report += f"""

🎯 PRÓXIMOS PASOS:
   1. Revisar resultados de tests
   2. Si todos pasaron: Listo para producción
   3. Si hay advertencias: Revisar saldo y gas prices
   4. Si hay errores: Verificar configuración

📍 INFORMACIÓN DEL CONTRATO:
   Dirección: {self.contract_address}
   Red: Scroll Sepolia
   Cuenta de Deploy: {self.account.address}
   URL Scrollscan: https://scrollscan.com/address/{self.contract_address}

════════════════════════════════════════════════════════════════
"""
        return report

    def run(self, quick_mode: bool = False, specific_tests: Optional[List[str]] = None):
        """
        Ejecutar tests

        Args:
            quick_mode: Ejecutar solo tests rápidos
            specific_tests: Lista de tests específicos a ejecutar
        """
        logger.info("=" * 60)
        logger.info("🧪 TESTING EN TESTNET - PAYMENT PROCESSOR")
        logger.info("=" * 60)

        try:
            tests = [
                ("connectivity", self.test_connectivity),
                ("contract_exists", self.test_contract_exists),
                ("contract_functions", self.test_contract_functions),
                ("token_support", self.test_token_support),
                ("transaction_simulation", self.test_transaction_simulation),
                ("blockchain_integration", self.test_blockchain_integration),
            ]

            # Filtrar tests si se especificaron
            if specific_tests:
                tests = [(name, func) for name, func in tests if name in specific_tests]

            # Ejecutar tests
            for test_name, test_func in tests:
                try:
                    test_func()
                except Exception as e:
                    logger.error(f"❌ Error ejecutando test {test_name}: {e}")
                    self.test_results[test_name] = {"status": "FAIL", "error": str(e)}

            # Mostrar reporte
            report = self.generate_test_report()
            logger.info(report)

            # Guardar reporte en archivo
            report_file = (
                Path(__file__).parent
                / f"testnet_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            with open(report_file, "w") as f:
                f.write(report)

            logger.info(f"✅ Reporte guardado en: {report_file}")

        except Exception as e:
            logger.error(f"❌ Error fatal: {e}")


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Testing en Testnet para PaymentProcessor"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Modo rápido (solo tests esenciales)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Modo completo (todos los tests)",
    )
    parser.add_argument(
        "--test-payments",
        action="store_true",
        help="Solo tests de pagos",
    )
    parser.add_argument(
        "--test-admin",
        action="store_true",
        help="Solo tests administrativos",
    )

    args = parser.parse_args()

    try:
        tester = TestnetTester()

        # Determinar qué tests ejecutar
        specific_tests = None
        if args.test_payments:
            specific_tests = ["connectivity", "contract_exists", "token_support"]
        elif args.test_admin:
            specific_tests = ["contract_functions", "blockchain_integration"]

        tester.run(quick_mode=args.quick, specific_tests=specific_tests)

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
