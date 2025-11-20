#!/usr/bin/env python3
"""
Script de Deployment con Monitoreo de Balance

Este script monitorea el balance de la cuenta y ejecuta el deployment
automáticamente cuando haya suficientes fondos.

Uso:
    python deployment/deploy_with_monitoring.py
    python deployment/deploy_with_monitoring.py --update-env
    python deployment/deploy_with_monitoring.py --timeout 300
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from web3 import Web3

# Cargar variables de entorno
load_dotenv()


class DeploymentMonitor:
    """Monitor de balance y ejecutor de deployment automático"""

    def __init__(self, timeout: int = 600, check_interval: int = 5):
        """
        Inicializar el monitor

        Args:
            timeout: Tiempo máximo de espera en segundos (default: 600 = 10 minutos)
            check_interval: Intervalo entre verificaciones en segundos (default: 5)
        """
        self.private_key = os.getenv("PRIVATE_KEY")
        self.rpc_url = os.getenv("RPC_URL", "https://sepolia-rpc.scroll.io/")
        self.timeout = timeout
        self.check_interval = check_interval
        self.min_balance = 0.01  # Balance mínimo requerido (ETH)
        self.start_time = datetime.now()

        if not self.private_key or not self.private_key.startswith("0x"):
            raise ValueError("❌ PRIVATE_KEY no configurada o inválida en .env")

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        if not self.w3.is_connected():
            raise ConnectionError("❌ No se pudo conectar a Scroll Sepolia RPC")

        self.account = self.w3.eth.account.from_key(self.private_key)

    def get_balance(self) -> float:
        """Obtener balance actual en ETH"""
        balance_wei = self.w3.eth.get_balance(self.account.address)
        balance_eth = Web3.from_wei(balance_wei, "ether")
        return float(balance_eth)

    def print_header(self):
        """Imprimir encabezado"""
        header = """
╔════════════════════════════════════════════════════════════════╗
║   🚀 DEPLOYMENT MONITOR - PAYMENT PROCESSOR                   ║
║      Monitoreo de Balance y Deployment Automático             ║
╚════════════════════════════════════════════════════════════════╝

📅 Inicio: {start_time}
🔗 Cuenta: {account}
🌐 Red: Scroll Sepolia (Chain ID: 534351)
💰 Balance mínimo requerido: {min_balance} ETH
⏱️  Timeout: {timeout} segundos

""".format(
            start_time=self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            account=self.account.address,
            min_balance=self.min_balance,
            timeout=self.timeout,
        )
        print(header)

    def format_time_elapsed(self) -> str:
        """Obtener tiempo transcurrido formateado"""
        elapsed = datetime.now() - self.start_time
        minutes = elapsed.total_seconds() // 60
        seconds = elapsed.total_seconds() % 60
        return f"{int(minutes):02d}:{int(seconds):02d}"

    def monitor_balance(self) -> bool:
        """
        Monitorear el balance hasta que sea suficiente o se agote el timeout

        Returns:
            True si el balance es suficiente, False si se agotó el timeout
        """
        self.print_header()

        print("⏳ Monitoreando balance...\n")

        check_count = 0
        while True:
            check_count += 1
            balance = self.get_balance()
            elapsed = self.format_time_elapsed()

            # Determinar estado
            if balance >= self.min_balance:
                print(f"\n✅ [{elapsed}] Balance suficiente encontrado!")
                print(f"   Balance: {balance:.6f} ETH")
                print(f"   Intentos: {check_count}")
                return True

            # Verificar timeout
            elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
            if elapsed_seconds > self.timeout:
                print(f"\n❌ [{elapsed}] Timeout alcanzado")
                print(f"   Balance final: {balance:.6f} ETH")
                print(f"   Intentos: {check_count}")
                return False

            # Mostrar progreso
            remaining_seconds = int(self.timeout - elapsed_seconds)
            remaining_time = (
                f"{remaining_seconds // 60:02d}:{remaining_seconds % 60:02d}"
            )

            status = "🟡" if balance < self.min_balance * 0.5 else "🟠"
            print(
                f"{status} [{elapsed}] Balance: {balance:.6f} ETH | Restante: {remaining_time}",
                end="\r",
            )

            time.sleep(self.check_interval)

    def run_deployment(self, update_env: bool = False) -> bool:
        """
        Ejecutar el script de deployment

        Args:
            update_env: Si True, actualiza .env con la nueva dirección

        Returns:
            True si el deployment fue exitoso
        """
        print("\n\n" + "=" * 70)
        print("🚀 INICIANDO DEPLOYMENT")
        print("=" * 70 + "\n")

        try:
            # Construir comando
            cmd = ["python3", "deployment/deploy_contract.py"]
            if update_env:
                cmd.append("--update-env")

            # Ejecutar deployment
            result = subprocess.run(
                cmd,
                cwd=str(Path(__file__).parent.parent),
                capture_output=False,
                text=True,
            )

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error al ejecutar deployment: {e}")
            return False

    def run(self, update_env: bool = False) -> bool:
        """
        Ejecutar monitoreo completo y deployment

        Args:
            update_env: Si True, actualiza .env con la nueva dirección

        Returns:
            True si todo fue exitoso
        """
        # Monitorear balance
        if not self.monitor_balance():
            print("\n❌ Se agotó el tiempo esperando fondos.")
            print("   Por favor, intenta más tarde o verifica el faucet.")
            return False

        # Ejecutar deployment
        return self.run_deployment(update_env=update_env)


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitoreo de balance y deployment automático",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python deployment/deploy_with_monitoring.py
  python deployment/deploy_with_monitoring.py --update-env
  python deployment/deploy_with_monitoring.py --timeout 300
  python deployment/deploy_with_monitoring.py --check-interval 10
        """,
    )

    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Actualizar .env con la nueva dirección del contrato",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Tiempo máximo de espera en segundos (default: 600)",
    )

    parser.add_argument(
        "--check-interval",
        type=int,
        default=5,
        help="Intervalo entre verificaciones en segundos (default: 5)",
    )

    args = parser.parse_args()

    try:
        monitor = DeploymentMonitor(
            timeout=args.timeout, check_interval=args.check_interval
        )

        success = monitor.run(update_env=args.update_env)

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
