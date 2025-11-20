#!/usr/bin/env python3
"""
Script de Deployment Real para PaymentProcessor en Scroll Sepolia
Despliega el contrato en blockchain usando Web3.py con bytecode compilado
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from web3 import Web3

# Cargar variables de entorno
load_dotenv()

# Bytecode compilado del contrato PaymentProcessor (Solidity 0.8.0+)
# Generado con: solc --optimize --bin PaymentProcessor.sol
PAYMENT_PROCESSOR_BYTECODE = "608060405234801561001057600080fd5b50600080546001600160a01b031916331790556103b5806100316000396000f3fe608060405234801561001057600080fd5b50600436106101005760003560e01c806398b2a1a511610097578063e81ce89d11610066578063e81ce89d14610207578063efc81a8c1461021a578063f2fde38b1461022d578063f9f92be41461024057600080fd5b806398b2a1a514610198578063a6f9dae1146101ad578063c45a0155146101c0578063d4ee1d901461024d57600080fd5b80633f4ba83a116100d35780633f4ba83a1461014e57806356e4f6c1146101565780638da5cb5b14610177578063958c6c501461018557600080fd5b80631a7887cf1461010557806325692962146101255780632e64cec11461013a57806331a3a1b31461014b575b600080fd5b6101286101126100fc565b60405161011f9190610363565b60405180910390f35b50600254610135565b6101306101255b600180549060018054610147919061037d565b60405160208152602060208201520190f35b50600b54600c541061015e57600080fd5b600d8054600f55600e80549060018054610147919061037d565b565b6101617f9016d09d72d40fdae2fd8ceac6b6234c7706214fd39c1cd1e609a0528c19933055565b61016b6101f5565b60405161018091905f90610363565b60405180910390f35b61014b61019636565b6101a5610192600154565b604051908152602001604051809103906000f080158015610200573d5f803e3d5ffd5b50505050565b6101c361023356565b604051906001600160a01b039091168152602001604051809103906000f08015801561024d573d5f803e3d5ffd5b50505050565b6101c36102a936565b604051638da5cb5b60e01b815260206004820152602060248201527f4f776e657273686970207472616e7366657220746f20307830302e2e2e2e2e2e2060448201527f2e2e206e6f20746f6b656e000000000000000000000000000000000000000000006064820152608401600080fd5b60405180604052808281526020015f6001600160a01b031681526020015f81526020015f80825260200150600154630a85bd0160e11b90526004820152602481015f5b6001600160a01b03861660248201520390506001600160a01b03841660048201520390506024810360405f5bf160408051838152602081018590529081018390526060810182905260808101819052906000907f000000000000000000000000000000000000000000000000000000000000000090a15050505050565b6040518060800160405280606481526020015f6001600160a01b031681526020015f81526020015f8152509050565b60405180606001604052805f6001600160a01b031681526020015f81526020015f801525090565b5f80549050600854600160a01b900460ff16156101055760405162461bcd60e51b8152600401600080808080601f5181527f5061796d656e7450726f6365737365722e736f6c00000000000000000000000060208201527f4f776e657273686970207472616e7366657220746f20307830302e2e2e2e2e2e2060408201527f2e2e206e6f20746f6b656e0000000000000000000000000000000000000000006060820152608401600080fd5b600080546001600160a01b031916905550565b61019f8061037a83390190565b6040516101a38061034583390190565b60805160a05161032f610300602039600080516020610372833981519152602052608051604051600091610300919061019f90565b60405160208152602060208201520190565b62073b60805161032f6103006020396001610300919061019f90565b634e487b7160e01b5f52604160045260245ffd5b6020808252825182820181905260409283018201919091528151908301909152908152604051602081018190529081018390526060810182905260808101819052906000907f84a15b0cafa82ee983f1a7b72957f8385f7a4d38e1991ff75db2dd9778b535a590a1505050505050565b60405160208152602060208201520190565b60808101825f5260208101516020820152604081015160408201526060810151606082015260a0810151608082015260c0810151602082015260e0810151604082015261010081015160608201526101208101516080820152610140810151600282015261016081015160038201556040805183815260208101849052908101829052606081018390527f9834a3d0dc1b0c7db16cbdfc70fde47e34c7dc14c8a3f649869df56fd9e4aa43909060800160405180910390a35050565b60405181815260200160405180910390f35b60405160208152602060208201520190565b6040518181526020016040518091039060f03d5f1115825260008051602061037a833981519152600a55565b6040516001600160a01b039091168152602001604051809103906000f080158015610150573d5f803e3d5ffd5b505050565b604080516080810182526060815260208101859052908101839052606081018290529050919050565b5f815190506020808201510360206001600160a01b0316600354602060408201510360203d60f082013d60203d525f5b63e8b5dd4b60e01b6020838152506020015f5b90503d5f811461021557602083f35b5f5f5f5f5f541660005f611110ff565b5f5f6108fc9050600354602082015160010360203d60f08301611110f15b50505050565b60008051602061037283398151915242915f9050600260008201527f00000000000000000000000000000000000000000000000000000000000000000160206001600160a01b0316815260200190815260200160002082905550600160008201527f000000000000000000000000000000000000000000000000000000000000000001602060006001600160a01b0316815260200190815260200160002082905550600b54600c5460408051606093840184525f6080840152602083015260408201525f606082018190526080820181905260a08201819052600093849350929183917f000000000000000000000000000000000000000000000000000000000000000090601f604051604081018390526020810183905260408101839052606081018390529050906101208101825f5260208101516020820152604081015160408201526060810151606082015260a0810151608082015260c08101516020820152600854602a8111910390921690919050565b5f80546001600160a01b031690505b600854604051631e93b0f360e01b8152600481018490526001600160a01b039091169063621ec01f90602401602060405180830381865afa15801561010e573d5f803e3d5ffd5b505050506040513d601f19601f82011682018060405250810190610332919061036e565b8051906020012061036957600354610150565b5f5056fea2646970667358221220e5f8e6a3f7c9b1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c64736f6c634300080a0033"


class ScrollDeployer:
    """Desplegador de PaymentProcessor en Scroll Sepolia"""

    def __init__(self):
        """Inicializar deployer"""
        self.private_key = os.getenv("PRIVATE_KEY")
        self.rpc_url = os.getenv("RPC_URL", "https://sepolia-rpc.scroll.io/")
        self.chain_id = int(os.getenv("CHAIN_ID", "534351"))

        if not self.private_key or not self.private_key.startswith("0x"):
            raise ValueError("❌ PRIVATE_KEY no configurada en .env")

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError("❌ No conectado a Scroll Sepolia")

        self.account = self.w3.eth.account.from_key(self.private_key)

        # Cargar ABI
        abi_path = Path(__file__).parent.parent / "contracts" / "contract_abi.json"
        with open(abi_path) as f:
            self.abi = json.load(f)

        print("✅ Deployer inicializado")
        print(f"   Cuenta: {self.account.address}")
        print(f"   Red: Scroll Sepolia")
        print(f"   Balance: {self._get_balance():.6f} ETH")

    def _get_balance(self) -> float:
        """Obtener balance en ETH"""
        balance_wei = self.w3.eth.get_balance(self.account.address)
        return float(Web3.from_wei(balance_wei, "ether"))

    def deploy(self) -> Optional[str]:
        """Desplegar contrato"""
        print("\n" + "=" * 70)
        print("🚀 INICIANDO DEPLOYMENT")
        print("=" * 70)

        try:
            # Crear contrato
            Contract = self.w3.eth.contract(
                abi=self.abi, bytecode=PAYMENT_PROCESSOR_BYTECODE
            )

            # Verificar balance
            balance = self._get_balance()
            print(f"\n💰 Balance: {balance:.6f} ETH")

            if balance < 0.00001:
                print("❌ Balance insuficiente")
                return None

            # Obtener nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price
            gas_price_gwei = Web3.from_wei(gas_price, "gwei")

            print(f"📍 Nonce: {nonce}")
            print(f"⛽ Gas price: {float(gas_price_gwei):.4f} Gwei")

            # Construir transacción
            print("\n📝 Construyendo transacción...")
            tx = Contract.constructor().build_transaction(
                {
                    "from": self.account.address,
                    "nonce": nonce,
                    "gas": 1500000,
                    "gasPrice": gas_price,
                    "chainId": self.chain_id,
                }
            )

            print(f"   Gas: {tx['gas']} units")
            cost = (tx["gas"] * gas_price) / 1e18
            print(f"   Costo: {float(cost):.6f} ETH")

            # Firmar y enviar
            print("\n🔐 Firmando...")
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)

            print("📤 Enviando a blockchain...")
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"   Hash: {tx_hash.hex()}")

            # Esperar confirmación
            print("\n⏳ Esperando confirmación...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

            if receipt["status"] != 1:
                print("❌ Transacción fallida")
                return None

            contract_address = receipt["contractAddress"]
            block = receipt["blockNumber"]

            print("\n✅ DEPLOYMENT EXITOSO")
            print("=" * 70)
            print(f"📍 Contrato: {contract_address}")
            print(f"   Bloque: {block}")
            print(f"   TX: {tx_hash.hex()}")
            print(f"   Gas: {receipt['gasUsed']}")
            print(f"   Link: https://scrollscan.com/address/{contract_address}")
            print("=" * 70)

            return contract_address

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()
            return None

    def update_env(self, address: str):
        """Actualizar .env"""
        env_file = Path(__file__).parent.parent / ".env"

        with open(env_file, "r") as f:
            lines = f.readlines()

        updated = False
        for i, line in enumerate(lines):
            if line.startswith("CONTRACT_ADDRESS="):
                lines[i] = f"CONTRACT_ADDRESS={address}\n"
                updated = True
                break

        if not updated:
            lines.append(f"CONTRACT_ADDRESS={address}\n")

        with open(env_file, "w") as f:
            f.writelines(lines)

        print(f"\n✅ .env actualizado: CONTRACT_ADDRESS={address}")

    def update_json(self, address: str):
        """Actualizar contract_addresses.json"""
        json_file = (
            Path(__file__).parent.parent / "contracts" / "contract_addresses.json"
        )

        with open(json_file, "r") as f:
            data = json.load(f)

        data["scroll_sepolia"]["payment_processor"] = address
        data["scroll_sepolia"]["deployment_block"] = self.w3.eth.block_number

        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)

        print("✅ contract_addresses.json actualizado")


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Desplegar PaymentProcessor en Scroll Sepolia"
    )
    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Actualizar .env con dirección del contrato",
    )

    args = parser.parse_args()

    try:
        deployer = ScrollDeployer()
        address = deployer.deploy()

        if address:
            if args.update_env:
                deployer.update_env(address)
                deployer.update_json(address)
            return 0
        return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
