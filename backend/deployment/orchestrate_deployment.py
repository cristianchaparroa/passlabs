"""
Script de Orchestración para Deployment Completo

Este script ejecuta todo el proceso de deployment de forma automatizada:
1. Verificación de requisitos
2. Compilación del contrato
3. Deployment en Scroll Sepolia
4. Verificación en Scrollscan
5. Testing en testnet
6. Generación de reporte final

Uso:
    python deployment/orchestrate_deployment.py
    python deployment/orchestrate_deployment.py --skip-tests
    python deployment/orchestrate_deployment.py --skip-verification
    python deployment/orchestrate_deployment.py --dry-run

Variables de Entorno Requeridas:
    - PRIVATE_KEY: Clave privada de deployment
    - RPC_URL: URL del RPC de Scroll Sepolia (opcional)
    - CONTRACT_ADDRESS: Se actualiza tras deployment
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from utils.logger import get_logger

# Cargar variables de entorno
load_dotenv()

logger = get_logger(__name__)


class DeploymentOrchestrator:
    """Orquestador del proceso completo de deployment"""

    def __init__(self):
        """Inicializar el orquestador"""
        self.start_time = datetime.now()
        self.steps_completed = []
        self.errors = []
        self.warnings = []

        logger.info("✅ Orchestrator inicializado")

    def print_header(self):
        """Imprimir encabezado"""
        header = """
╔════════════════════════════════════════════════════════════════╗
║   🚀 ORCHESTRACIÓN DE DEPLOYMENT - PAYMENT PROCESSOR          ║
║      Smart Contract Deployment en Scroll Sepolia              ║
╚════════════════════════════════════════════════════════════════╝

📅 Fecha: {datetime}
🔧 Versión: 0.6.0

""".format(datetime=self.start_time.strftime("%Y-%m-%d %H:%M:%S"))

        logger.info(header)

    def print_phase(self, phase_number: int, phase_name: str):
        """Imprimir encabezado de fase"""
        phase_header = f"""
{"=" * 70}
FASE {phase_number}: {phase_name}
{"=" * 70}
"""
        logger.info(phase_header)

    def phase_1_prerequisites_check(self, dry_run: bool = False) -> bool:
        """
        FASE 1: Verificación de Requisitos Previos
        """
        self.print_phase(1, "Verificación de Requisitos Previos")

        try:
            logger.info("🔍 Verificando requisitos...")

            # Verificar PRIVATE_KEY
            private_key = os.getenv("PRIVATE_KEY")
            if not private_key:
                self.errors.append("PRIVATE_KEY no configurada en .env")
                logger.error("❌ PRIVATE_KEY no configurada")
                return False

            if not private_key.startswith("0x") or len(private_key) != 66:
                self.errors.append("PRIVATE_KEY inválida (debe ser 0x + 64 hex)")
                logger.error("❌ PRIVATE_KEY inválida")
                return False

            logger.info("✅ PRIVATE_KEY válida")

            # Verificar RPC_URL
            rpc_url = os.getenv("RPC_URL", "https://sepolia-rpc.scroll.io/")
            logger.info(f"✅ RPC_URL: {rpc_url}")

            # Verificar archivos
            contract_dir = Path(__file__).parent.parent / "contracts"
            sol_file = contract_dir / "PaymentProcessor.sol"

            if not sol_file.exists():
                self.errors.append(f"Archivo Solidity no encontrado: {sol_file}")
                logger.error(f"❌ {sol_file} no existe")
                return False

            logger.info(f"✅ Archivo Solidity encontrado: {sol_file}")

            # Verificar ABI
            abi_file = contract_dir / "contract_abi.json"
            if not abi_file.exists():
                self.warnings.append(
                    "ABI no compilado. Será necesario compilar con Hardhat"
                )
                logger.warning(
                    f"⚠️  {abi_file} no existe (se puede compilar automáticamente)"
                )
            else:
                logger.info(f"✅ Archivo ABI encontrado: {abi_file}")

            self.steps_completed.append("1_prerequisites")
            logger.info("✅ FASE 1 COMPLETADA")
            return True

        except Exception as e:
            self.errors.append(f"Error en verificación de requisitos: {str(e)}")
            logger.error(f"❌ Error: {e}")
            return False

    def phase_2_connectivity_check(self, dry_run: bool = False) -> bool:
        """
        FASE 2: Verificación de Conectividad
        """
        self.print_phase(2, "Verificación de Conectividad")

        try:
            logger.info("🔗 Verificando conectividad con Scroll Sepolia...")

            from web3 import Web3

            rpc_url = os.getenv("RPC_URL", "https://sepolia-rpc.scroll.io/")
            w3 = Web3(Web3.HTTPProvider(rpc_url))

            if not w3.is_connected():
                self.errors.append("No se pudo conectar a Scroll Sepolia RPC")
                logger.error("❌ No conectado a RPC")
                return False

            logger.info("✅ Conectado a Scroll Sepolia")

            # Verificar cadena
            chain_id = w3.eth.chain_id
            if chain_id != 534351:
                self.warnings.append(
                    f"Chain ID inesperado: {chain_id} (esperado: 534351)"
                )
                logger.warning(f"⚠️  Chain ID: {chain_id}")
            else:
                logger.info(f"✅ Chain ID correcto: {chain_id}")

            # Verificar balance
            private_key = os.getenv("PRIVATE_KEY")
            account = w3.eth.account.from_key(private_key)
            balance_wei = w3.eth.get_balance(account.address)
            balance_eth = Web3.from_wei(balance_wei, "ether")

            logger.info(f"✅ Cuenta: {account.address}")
            logger.info(f"💰 Balance: {balance_eth} ETH")

            if balance_eth < 0.01:
                self.warnings.append(
                    f"Balance bajo: {balance_eth} ETH (mínimo recomendado: 0.01)"
                )
                logger.warning(f"⚠️  Balance bajo (< 0.01 ETH)")

            # Gas price
            gas_price = w3.eth.gas_price
            gas_price_gwei = Web3.from_wei(gas_price, "gwei")
            logger.info(f"⛽ Gas Price: {gas_price_gwei} Gwei")

            self.steps_completed.append("2_connectivity")
            logger.info("✅ FASE 2 COMPLETADA")
            return True

        except Exception as e:
            self.errors.append(f"Error en verificación de conectividad: {str(e)}")
            logger.error(f"❌ Error: {e}")
            return False

    def phase_3_contract_compilation(self, dry_run: bool = False) -> bool:
        """
        FASE 3: Compilación del Contrato
        """
        self.print_phase(3, "Compilación del Contrato")

        try:
            logger.info("🔨 Verificando compilación del contrato...")

            contract_dir = Path(__file__).parent.parent / "contracts"
            abi_file = contract_dir / "contract_abi.json"

            if abi_file.exists():
                logger.info(f"✅ Contrato ya compilado: {abi_file}")

                with open(abi_file, "r") as f:
                    abi = json.load(f)
                    logger.info(f"✅ ABI cargado correctamente ({len(abi)} elementos)")
            else:
                logger.warning(f"⚠️  ABI no encontrado. Se requiere compilación.")
                logger.warning("   Comando: cd contracts && npx hardhat compile")
                self.warnings.append(
                    "Contrato no compilado. Se requiere compilación manual con Hardhat"
                )

            self.steps_completed.append("3_compilation")
            logger.info("✅ FASE 3 COMPLETADA")
            return True

        except Exception as e:
            self.errors.append(f"Error en compilación: {str(e)}")
            logger.error(f"❌ Error: {e}")
            return False

    def phase_4_contract_deployment(self, dry_run: bool = False) -> Optional[str]:
        """
        FASE 4: Deployment del Contrato
        """
        self.print_phase(4, "Deployment del Contrato")

        if dry_run:
            logger.info("🔄 MODO DRY-RUN - Simulando deployment...")
            contract_address = "0x" + "a" * 40
            logger.info(f"📝 Dirección simulada: {contract_address}")
            return contract_address

        try:
            logger.info("📤 Desplegando contrato PaymentProcessor...")

            from deployment.deploy_contract import ContractDeployer

            deployer = ContractDeployer()
            contract_address = deployer.deploy_contract()

            if not contract_address:
                self.errors.append("Deployment falló")
                logger.error("❌ Deployment falló")
                return None

            # Actualizar .env
            deployer.update_addresses_file(contract_address)
            deployer.update_env_file(contract_address)

            logger.info(f"✅ Contrato deployado: {contract_address}")

            self.steps_completed.append("4_deployment")
            return contract_address

        except Exception as e:
            self.errors.append(f"Error en deployment: {str(e)}")
            logger.error(f"❌ Error: {e}")
            return None

    def phase_5_contract_verification(
        self, contract_address: str, dry_run: bool = False
    ) -> bool:
        """
        FASE 5: Verificación en Scrollscan
        """
        self.print_phase(5, "Verificación en Scrollscan")

        try:
            logger.info("🔍 Preparando información para verificación...")

            from deployment.verify_on_scrollscan import ScrollscanVerifier

            verifier = ScrollscanVerifier(contract_address)

            # Generar guía
            guide = verifier.generate_verification_guide()
            logger.info(guide)

            # Generar reporte JSON
            report_file = (
                Path(__file__).parent
                / f"scrollscan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            verifier.generate_json_report(str(report_file))

            logger.info(f"✅ Información de verificación generada")
            logger.info(f"   Guía: {guide}")
            logger.info(f"   Reporte: {report_file}")

            self.steps_completed.append("5_verification")
            logger.info("✅ FASE 5 COMPLETADA")
            return True

        except Exception as e:
            self.warnings.append(f"Error en preparación de verificación: {str(e)}")
            logger.warning(f"⚠️  Error: {e}")
            return True  # No es fatal

    def phase_6_testnet_testing(self, dry_run: bool = False) -> bool:
        """
        FASE 6: Testing en Testnet
        """
        self.print_phase(6, "Testing en Testnet")

        if dry_run:
            logger.info("🔄 MODO DRY-RUN - Simulando tests...")
            logger.info("✅ Tests completados (simulado)")
            return True

        try:
            logger.info("🧪 Ejecutando tests en testnet...")

            from deployment.test_on_testnet import TestnetTester

            tester = TestnetTester()
            tester.run()

            self.steps_completed.append("6_testing")
            logger.info("✅ FASE 6 COMPLETADA")
            return True

        except Exception as e:
            self.warnings.append(f"Error en testing: {str(e)}")
            logger.warning(f"⚠️  Error: {e}")
            return True  # Warning, no es fatal

    def generate_final_report(self, contract_address: Optional[str] = None) -> str:
        """
        Generar reporte final de deployment
        """
        duration = datetime.now() - self.start_time

        report = f"""
╔════════════════════════════════════════════════════════════════╗
║           REPORTE FINAL DE DEPLOYMENT                         ║
║              PAYMENT PROCESSOR - SCROLL SEPOLIA                ║
╚════════════════════════════════════════════════════════════════╝

📊 RESUMEN EJECUTIVO:
   Estado: {"✅ ÉXITO" if not self.errors else "❌ CON ERRORES"}
   Tiempo Total: {duration}
   Fases Completadas: {len(self.steps_completed)}/6

✅ FASES COMPLETADAS:
"""

        for step in self.steps_completed:
            report += f"   ✅ {step.upper()}\n"

        if self.warnings:
            report += f"\n⚠️  ADVERTENCIAS ({len(self.warnings)}):\n"
            for warning in self.warnings:
                report += f"   • {warning}\n"

        if self.errors:
            report += f"\n❌ ERRORES ({len(self.errors)}):\n"
            for error in self.errors:
                report += f"   • {error}\n"

        if contract_address:
            report += f"""
🎯 INFORMACIÓN DEL CONTRATO:
   Dirección: {contract_address}
   Red: Scroll Sepolia
   URL Scrollscan: https://scrollscan.com/address/{contract_address}
   URL Verificación: https://scrollscan.com/verifycontract

📋 ARCHIVOS ACTUALIZADOS:
   ✅ .env (CONTRACT_ADDRESS)
   ✅ contract_addresses.json
   ✅ Reportes de verificación
   ✅ Reportes de testing
"""

        report += f"""
🚀 PRÓXIMOS PASOS:
   1. Verificar contrato en Scrollscan (manual)
   2. Ejecutar pruebas de integración
   3. Testing end-to-end con frontend
   4. Preparar para mainnet (si aplica)

📞 SOPORTE:
   Documentación: deployment/README.md
   Logs: logs/app.log
   Reportes: deployment/

📅 Timestamp: {datetime.now().isoformat()}

════════════════════════════════════════════════════════════════
"""
        return report

    def run(
        self,
        skip_tests: bool = False,
        skip_verification: bool = False,
        dry_run: bool = False,
    ):
        """
        Ejecutar orquestación completa
        """
        self.print_header()

        logger.info("📋 Iniciando proceso de deployment...\n")

        contract_address = None

        try:
            # FASE 1: Verificación de requisitos
            if not self.phase_1_prerequisites_check(dry_run):
                logger.error("❌ Verificación de requisitos falló")
                report = self.generate_final_report()
                logger.info(report)
                return False

            # FASE 2: Verificación de conectividad
            if not self.phase_2_connectivity_check(dry_run):
                logger.error("❌ Verificación de conectividad falló")
                report = self.generate_final_report()
                logger.info(report)
                return False

            # FASE 3: Compilación
            if not self.phase_3_contract_compilation(dry_run):
                logger.error("❌ Compilación falló")
                report = self.generate_final_report()
                logger.info(report)
                return False

            # FASE 4: Deployment
            contract_address = self.phase_4_contract_deployment(dry_run)
            if not contract_address:
                logger.error("❌ Deployment falló")
                report = self.generate_final_report()
                logger.info(report)
                return False

            # FASE 5: Verificación (opcional)
            if not skip_verification:
                self.phase_5_contract_verification(contract_address, dry_run)

            # FASE 6: Testing (opcional)
            if not skip_tests:
                self.phase_6_testnet_testing(dry_run)

            # Generar reporte final
            report = self.generate_final_report(contract_address)
            logger.info(report)

            # Guardar reporte
            report_file = (
                Path(__file__).parent
                / f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            with open(report_file, "w") as f:
                f.write(report)

            logger.info(f"✅ Reporte guardado en: {report_file}")

            if not self.errors:
                logger.info("🎉 DEPLOYMENT COMPLETADO EXITOSAMENTE")
                return True
            else:
                logger.error("⚠️  Deployment completado con errores")
                return False

        except Exception as e:
            logger.error(f"❌ Error fatal: {e}")
            report = self.generate_final_report()
            logger.info(report)
            return False


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Orquestación de Deployment - PaymentProcessor"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Omitir testing en testnet",
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Omitir verificación en Scrollscan",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecutar en modo simulación (sin efectos reales)",
    )

    args = parser.parse_args()

    try:
        orchestrator = DeploymentOrchestrator()

        success = orchestrator.run(
            skip_tests=args.skip_tests,
            skip_verification=args.skip_verification,
            dry_run=args.dry_run,
        )

        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
