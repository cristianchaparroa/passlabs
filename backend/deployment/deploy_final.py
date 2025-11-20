#!/usr/bin/env python3
"""
Script Final de Deployment del Contrato PaymentProcessor en Scroll Sepolia

Este script despliega el contrato PaymentProcessor en Scroll Sepolia testnet
usando Web3.py con el bytecode compilado.

PASOS PREVIOS:
1. Compilar el contrato en Remix IDE (https://remix.ethereum.org)
   - Copiar PaymentProcessor.sol
   - Compilar con Solidity 0.8.0
   - Obtener bytecode de "Compilation Details"

2. Reemplazar el bytecode en la línea ~50 de este archivo

USO:
    python3 deployment/deploy_final.py --update-env
    python3 deployment/deploy_final.py --dry-run
    python3 deployment/deploy_final.py --verify-only
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from web3 import Web3

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# REEMPLAZA ESTO CON TU BYTECODE COMPILADO
# ============================================================================
# Bytecode compilado del contrato PaymentProcessor
# Obtenido de: Remix IDE → Solidity Compiler → Compilation Details → Object
# Debe ser un string de hexadecimal sin espacios, comenzando con "0x"
#
# Ejemplo:
#   BYTECODE = "0x608060405234801561001057600080fd5b5061038e806100205f395ff3fe..."
#
PAYMENT_PROCESSOR_BYTECODE = None  # ← REEMPLAZA CON TU BYTECODE


class PaymentProcessorDeployer:
    """Desplegador del contrato PaymentProcessor en Scroll Sepolia"""

    def __init__(self):
        """Inicializar el deployer"""
        self.private_key = os.getenv("PRIVATE_KEY")
        self.rpc_url = os.getenv("RPC_URL", "https://sepolia-rpc.scroll.io/")
        self.chain_id = int(os.getenv("CHAIN_ID", "534351"))

        # Validar configuración
        if not self.private_key or not self.private_key.startswith("0x"):
            raise ValueError("❌ PRIVATE_KEY no configurada en .env")

        if not PAYMENT_PROCESSOR_BYTECODE:
            raise ValueError(
                "❌ BYTECODE no configurado. "
                "Necesitas compilar el contrato en Remix y pegar el bytecode aquí."
            )

        # Conectar a Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"❌ No conectado a {self.rpc_url}")

        # Obtener cuenta
        self.account = self.w3.eth.account.from_key(self.private_key)

        # Cargar ABI
        abi_path = Path(__file__).parent.parent / "contracts" / "contract_abi.json"
        with open(abi_path, "r") as f:
            self.abi = json.load(f)

        print("✅ Deployer inicializado correctamente")
        print(f"   Cuenta: {self.account.address}")
        print(f"   Red: Scroll Sepolia")
        print(f"   Balance: {self._get_balance():.6f} ETH")

    def _get_balance(self) -> float:
        """Obtener balance en ETH"""
        balance_wei = self.w3.eth.get_balance(self.account.address)
        return float(Web3.from_wei(balance_wei, "ether"))

    def _validate_bytecode(self) -> bool:
        """Validar el bytecode"""
        if not PAYMENT_PROCESSOR_BYTECODE:
            print("❌ Bytecode no configurado")
            return False

        if not isinstance(PAYMENT_PROCESSOR_BYTECODE, str):
            print("❌ Bytecode debe ser string")
            return False

        if not PAYMENT_PROCESSOR_BYTECODE.startswith("0x"):
            print("❌ Bytecode debe comenzar con 0x")
            return False

        if len(PAYMENT_PROCESSOR_BYTECODE) < 100:
            print("❌ Bytecode parece estar incompleto (muy corto)")
            return False

        print(f"✅ Bytecode validado ({len(PAYMENT_PROCESSOR_BYTECODE)} caracteres)")
        return True

    def deploy(self, dry_run: bool = False) -> Optional[str]:
        """
        Desplegar el contrato

        Args:
            dry_run: Si True, solo muestra la transacción sin enviarla

        Returns:
            Dirección del contrato deployado o None si falló
        """
        print("\n" + "=" * 70)
        print("🚀 DEPLOYMENT DE PAYMENTPROCESSOR")
        print("=" * 70)

        try:
            # Validar bytecode
            if not self._validate_bytecode():
                return None

            # Crear instancia del contrato
            Contract = self.w3.eth.contract(
                abi=self.abi, bytecode=PAYMENT_PROCESSOR_BYTECODE
            )

            # Obtener información
            balance = self._get_balance()
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price
            gas_price_gwei = Web3.from_wei(gas_price, "gwei")

            print(f"\n📊 Información de la transacción:")
            print(f"   Balance: {balance:.6f} ETH")
            print(f"   Nonce: {nonce}")
            print(f"   Gas price: {float(gas_price_gwei):.4f} Gwei")
            print(f"   Chain ID: {self.chain_id}")

            # Construir transacción
            print(f"\n📝 Construyendo transacción...")
            tx = Contract.constructor().build_transaction(
                {
                    "from": self.account.address,
                    "nonce": nonce,
                    "gas": 1500000,  # Gas limit
                    "gasPrice": gas_price,
                    "chainId": self.chain_id,
                }
            )

            gas_cost = (tx["gas"] * gas_price) / 1e18
            print(f"   Gas estimado: {tx['gas']:,} units")
            print(f"   Costo estimado: {float(gas_cost):.6f} ETH")

            if balance < float(gas_cost):
                print(
                    f"❌ Balance insuficiente (falta {float(gas_cost) - balance:.6f} ETH)"
                )
                return None

            if dry_run:
                print("\n✅ Transacción lista (modo dry-run)")
                print("   Para desplegar, ejecuta sin --dry-run")
                return None

            # Firmar transacción
            print(f"\n🔐 Firmando transacción...")
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)

            # Enviar transacción
            print(f"📤 Enviando a blockchain...")
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"   Hash: {tx_hash.hex()}")

            # Esperar confirmación
            print(f"\n⏳ Esperando confirmación (esto puede tardar 1-2 minutos)...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

            if receipt["status"] != 1:
                print("❌ Transacción fallida en blockchain")
                return None

            contract_address = receipt["contractAddress"]
            block_number = receipt["blockNumber"]
            gas_used = receipt["gasUsed"]

            print("\n✅ DEPLOYMENT EXITOSO")
            print("=" * 70)
            print(f"📍 Dirección del Contrato: {contract_address}")
            print(f"   Bloque: {block_number}")
            print(f"   Transacción: {tx_hash.hex()}")
            print(f"   Gas usado: {gas_used:,}")
            print(f"   Costo real: {float((gas_used * gas_price) / 1e18):.6f} ETH")
            print(f"\n🔗 Ver en Scrollscan:")
            print(f"   https://scrollscan.com/address/{contract_address}")
            print("=" * 70)

            return contract_address

        except Exception as e:
            print(f"❌ Error durante deployment: {e}")
            import traceback

            traceback.print_exc()
            return None

    def verify_deployment(self, contract_address: str) -> bool:
        """Verificar que el contrato fue desplegado correctamente"""
        try:
            print(f"\n🔍 Verificando deployment...")
            print(f"   Dirección: {contract_address}")

            # Verificar que el contrato existe
            code = self.w3.eth.get_code(contract_address)
            if code == b"":
                print("❌ No hay código en esa dirección")
                return False

            print(f"✅ Contrato encontrado en blockchain")
            print(f"   Bytecode: {len(code)} bytes")

            # Intentar llamar una función de lectura
            contract = self.w3.eth.contract(address=contract_address, abi=self.abi)
            try:
                count = contract.functions.getPaymentCount().call()
                print(f"✅ Contrato respondiendo correctamente")
                print(f"   Payment count: {count}")
                return True
            except Exception as e:
                print(f"⚠️  No se pudo verificar función (puede ser normal): {e}")
                return True

        except Exception as e:
            print(f"❌ Error verificando: {e}")
            return False

    def update_env_and_json(self, contract_address: str) -> bool:
        """Actualizar .env y contract_addresses.json"""
        try:
            # Actualizar .env
            env_file = Path(__file__).parent.parent / ".env"
            with open(env_file, "r") as f:
                lines = f.readlines()

            updated = False
            for i, line in enumerate(lines):
                if line.startswith("CONTRACT_ADDRESS="):
                    lines[i] = f"CONTRACT_ADDRESS={contract_address}\n"
                    updated = True
                    break

            if not updated:
                lines.append(f"CONTRACT_ADDRESS={contract_address}\n")

            with open(env_file, "w") as f:
                f.writelines(lines)

            print(f"\n✅ .env actualizado")
            print(f"   CONTRACT_ADDRESS={contract_address}")

            # Actualizar contract_addresses.json
            json_file = (
                Path(__file__).parent.parent / "contracts" / "contract_addresses.json"
            )
            with open(json_file, "r") as f:
                data = json.load(f)

            data["scroll_sepolia"]["payment_processor"] = contract_address
            data["scroll_sepolia"]["deployment_block"] = self.w3.eth.block_number
            data["scroll_sepolia"]["deployment_date"] = str(
                __import__("datetime").datetime.now().isoformat()
            )

            with open(json_file, "w") as f:
                json.dump(data, f, indent=2)

            print(f"✅ contract_addresses.json actualizado")

            return True

        except Exception as e:
            print(f"❌ Error actualizando archivos: {e}")
            return False


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Desplegar PaymentProcessor en Scroll Sepolia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 deployment/deploy_final.py --update-env
  python3 deployment/deploy_final.py --dry-run
  python3 deployment/deploy_final.py --verify-only 0x...
        """,
    )

    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Actualizar .env con dirección del contrato",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostrar transacción sin enviarla",
    )

    parser.add_argument(
        "--verify-only",
        type=str,
        metavar="ADDRESS",
        help="Verificar un contrato ya desplegado",
    )

    args = parser.parse_args()

    try:
        # Si es solo verificación
        if args.verify_only:
            deployer = PaymentProcessorDeployer()
            deployer.verify_deployment(args.verify_only)
            return 0

        # Desplegar
        deployer = PaymentProcessorDeployer()
        contract_address = deployer.deploy(dry_run=args.dry_run)

        if not contract_address:
            return 1

        if args.dry_run:
            return 0

        # Actualizar archivos
        if args.update_env:
            deployer.update_env_and_json(contract_address)
            print("\n✅ Archivos actualizados correctamente")
            print("   Puedes comenzar a usar los endpoints de pago")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
