#!/usr/bin/env python3
"""
Script de validación pre-despliegue para Crypto Payments API
Verifica que todos los componentes están configurados correctamente para producción
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Colores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


class DeploymentValidator:
    """Validador de despliegue pre-producción"""

    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        self.errors: List[str] = []

    def print_header(self, text: str) -> None:
        """Imprimir encabezado"""
        print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
        print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
        print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")

    def print_success(self, text: str) -> None:
        """Imprimir mensaje de éxito"""
        print(f"{GREEN}✅ {text}{RESET}")
        self.checks_passed += 1

    def print_error(self, text: str) -> None:
        """Imprimir mensaje de error"""
        print(f"{RED}❌ {text}{RESET}")
        self.checks_failed += 1
        self.errors.append(text)

    def print_warning(self, text: str) -> None:
        """Imprimir mensaje de advertencia"""
        print(f"{YELLOW}⚠️  {text}{RESET}")
        self.warnings += 1

    def print_info(self, text: str) -> None:
        """Imprimir mensaje informativo"""
        print(f"{BLUE}ℹ️  {text}{RESET}")

    def check_python_version(self) -> bool:
        """Verificar versión de Python"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 9:
            self.print_success(f"Python {version.major}.{version.minor} ✓")
            return True
        else:
            self.print_error(
                f"Python 3.9+ requerido (encontrado: {version.major}.{version.minor})"
            )
            return False

    def check_env_file(self) -> bool:
        """Verificar que existe archivo .env"""
        env_path = Path(".env")
        if env_path.exists():
            self.print_success(".env archivo existe")
            return True
        else:
            self.print_error(".env archivo no encontrado")
            return False

    def check_env_variables(self) -> bool:
        """Verificar variables de entorno requeridas"""
        from dotenv import load_dotenv

        load_dotenv()

        required_vars = {
            "PRIVATE_KEY": "Clave privada de Ethereum",
            "CONTRACT_ADDRESS": "Dirección del contrato inteligente",
            "RPC_URL": "URL de RPC de Scroll Sepolia",
            "CHAIN_ID": "ID de la cadena blockchain",
            "API_HOST": "Host de la API",
            "API_PORT": "Puerto de la API",
        }

        all_present = True
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                # No mostrar valor completo por seguridad
                if var == "PRIVATE_KEY":
                    display = (
                        f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
                    )
                elif var == "CONTRACT_ADDRESS":
                    display = f"{value[:10]}..." if len(value) > 10 else value
                else:
                    display = value
                self.print_success(f"{var}: {display}")
            else:
                self.print_error(f"{var} no configurado ({description})")
                all_present = False

        return all_present

    def check_requirements(self) -> bool:
        """Verificar que requirements.txt existe"""
        req_path = Path("requirements.txt")
        if req_path.exists():
            self.print_success("requirements.txt existe")
            return True
        else:
            self.print_error("requirements.txt no encontrado")
            return False

    def check_dependencies(self) -> bool:
        """Verificar que las dependencias principales están instaladas"""
        required_packages = [
            "fastapi",
            "uvicorn",
            "web3",
            "pydantic",
            "httpx",
        ]

        all_installed = True
        for package in required_packages:
            try:
                __import__(package)
                self.print_success(f"Paquete '{package}' instalado")
            except ImportError:
                self.print_error(f"Paquete '{package}' NO está instalado")
                all_installed = False

        return all_installed

    def check_blockchain_connection(self) -> bool:
        """Verificar conexión a blockchain"""
        try:
            from config import settings
            from services.blockchain_service import blockchain_service

            if blockchain_service and blockchain_service.is_connected():
                chain_id = blockchain_service.w3.eth.chain_id
                self.print_success(f"Conectado a blockchain (Chain ID: {chain_id})")
                return True
            else:
                self.print_error("No se puede conectar al RPC de blockchain")
                return False
        except Exception as e:
            self.print_error(f"Error verificando conexión a blockchain: {str(e)}")
            return False

    def check_contract_address(self) -> bool:
        """Verificar que CONTRACT_ADDRESS está configurada y es válida"""
        contract_addr = os.getenv("CONTRACT_ADDRESS", "")

        if not contract_addr:
            self.print_error("CONTRACT_ADDRESS no configurada")
            return False

        if contract_addr.lower() == "0x0000000000000000000000000000000000000000":
            self.print_warning("CONTRACT_ADDRESS es la dirección nula (0x000...)")
            return True

        if not contract_addr.startswith("0x") or len(contract_addr) != 42:
            self.print_error(f"CONTRACT_ADDRESS formato inválido: {contract_addr}")
            return False

        self.print_success(f"CONTRACT_ADDRESS formato válido: {contract_addr[:10]}...")
        return True

    def check_private_key(self) -> bool:
        """Verificar que PRIVATE_KEY está configurada y es válida"""
        from eth_account import Account

        private_key = os.getenv("PRIVATE_KEY", "")

        if not private_key:
            self.print_error("PRIVATE_KEY no configurada")
            return False

        try:
            account = Account.from_key(private_key)
            self.print_success(
                f"PRIVATE_KEY válida - Cuenta: {account.address[:10]}..."
            )
            return True
        except Exception as e:
            self.print_error(f"PRIVATE_KEY inválida: {str(e)}")
            return False

    def check_debug_mode(self) -> bool:
        """Verificar que DEBUG está en False para producción"""
        debug = os.getenv("DEBUG", "False").lower() == "true"

        if debug:
            self.print_warning("DEBUG está habilitado (DEBUG=True)")
            return False
        else:
            self.print_success("DEBUG deshabilitado (DEBUG=False)")
            return True

    def check_file_permissions(self) -> bool:
        """Verificar permisos de archivo .env"""
        env_path = Path(".env")
        if not env_path.exists():
            return True

        # En sistemas Unix
        stat = env_path.stat()
        mode = stat.st_mode & 0o777

        if mode == 0o600:
            self.print_success(".env tiene permisos restrictivos (600)")
            return True
        elif mode == 0o644:
            self.print_warning(
                ".env tiene permisos demasiado permisivos (644) - cambiar a 600"
            )
            return False
        else:
            self.print_info(f".env permisos: {oct(mode)}")
            return True

    def check_gitignore(self) -> bool:
        """Verificar que .env está en .gitignore"""
        gitignore_path = Path(".gitignore")

        if not gitignore_path.exists():
            self.print_warning(".gitignore no encontrado")
            return False

        try:
            with open(gitignore_path, "r") as f:
                content = f.read()

            if ".env" in content:
                self.print_success(".env está en .gitignore")
                return True
            else:
                self.print_error(".env NO está en .gitignore")
                return False
        except Exception as e:
            self.print_error(f"Error leyendo .gitignore: {str(e)}")
            return False

    def check_services(self) -> bool:
        """Verificar que todos los servicios se pueden inicializar"""
        try:
            from services.blockchain_service import blockchain_service
            from services.defi_llama_service import defi_llama_service
            from services.payment_service import PaymentService

            all_good = True

            if blockchain_service is None:
                self.print_error("BlockchainService no inicializado")
                all_good = False
            else:
                self.print_success("BlockchainService inicializado")

            if defi_llama_service is None:
                self.print_error("DeFiLlamaService no inicializado")
                all_good = False
            else:
                self.print_success("DeFiLlamaService inicializado")

            try:
                payment_service = PaymentService(blockchain_service)
                self.print_success("PaymentService inicializado")
            except Exception as e:
                self.print_error(f"PaymentService error: {str(e)}")
                all_good = False

            return all_good

        except Exception as e:
            self.print_error(f"Error inicializando servicios: {str(e)}")
            return False

    def check_api_endpoints(self) -> bool:
        """Verificar que endpoints principales existen"""
        try:
            from main import app

            endpoints = [
                "/health",
                "/status",
                "/stablecoins/prices",
                "/payments/create",
                "/docs",
            ]

            all_found = True
            routes = [route.path for route in app.routes]

            for endpoint in endpoints:
                if endpoint in routes:
                    self.print_success(f"Endpoint {endpoint} existe")
                else:
                    self.print_error(f"Endpoint {endpoint} NO existe")
                    all_found = False

            return all_found

        except Exception as e:
            self.print_error(f"Error verificando endpoints: {str(e)}")
            return False

    def check_logging_config(self) -> bool:
        """Verificar configuración de logging"""
        try:
            from utils.logger import get_logger

            logger = get_logger(__name__)
            self.print_success("Sistema de logging configurado")
            return True

        except Exception as e:
            self.print_error(f"Error en logging: {str(e)}")
            return False

    def run_all_checks(self) -> bool:
        """Ejecutar todas las verificaciones"""
        self.print_header("🚀 VALIDACIÓN PRE-DESPLIEGUE")
        self.print_info("Crypto Payments API v0.5.0\n")

        # Verificaciones básicas
        print(f"{BOLD}1. AMBIENTE PYTHON{RESET}")
        self.check_python_version()

        print(f"\n{BOLD}2. ARCHIVOS DE CONFIGURACIÓN{RESET}")
        self.check_env_file()
        self.check_requirements()
        self.check_gitignore()
        self.check_file_permissions()

        print(f"\n{BOLD}3. VARIABLES DE ENTORNO{RESET}")
        self.check_env_variables()

        print(f"\n{BOLD}4. SEGURIDAD{RESET}")
        self.check_debug_mode()
        self.check_private_key()
        self.check_contract_address()

        print(f"\n{BOLD}5. DEPENDENCIAS{RESET}")
        self.check_dependencies()

        print(f"\n{BOLD}6. SERVICIOS{RESET}")
        self.check_services()

        print(f"\n{BOLD}7. BLOCKCHAIN{RESET}")
        self.check_blockchain_connection()

        print(f"\n{BOLD}8. API{RESET}")
        self.check_logging_config()
        self.check_api_endpoints()

        # Resumen
        self.print_summary()

        return self.checks_failed == 0

    def print_summary(self) -> None:
        """Imprimir resumen de validación"""
        print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
        print(f"{BOLD}{BLUE}RESUMEN DE VALIDACIÓN{RESET}")
        print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")

        print(f"{GREEN}✅ Pasadas: {self.checks_passed}{RESET}")
        print(f"{RED}❌ Fallidas: {self.checks_failed}{RESET}")
        print(f"{YELLOW}⚠️  Advertencias: {self.warnings}{RESET}\n")

        if self.checks_failed == 0 and self.warnings == 0:
            print(f"{GREEN}{BOLD}✨ ¡LISTA PARA DESPLIEGUE A PRODUCCIÓN! ✨{RESET}\n")
            return

        if self.checks_failed > 0:
            print(f"{RED}{BOLD}ERRORES QUE REQUIEREN ATENCIÓN:{RESET}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {RED}{i}. {error}{RESET}")

        if self.warnings > 0:
            print(f"\n{YELLOW}{BOLD}ADVERTENCIAS (Revisar):{RESET}")
            print(f"  {YELLOW}1. Revisar configuración de DEBUG{RESET}")
            print(f"  {YELLOW}2. Revisar permisos de archivo{RESET}")

        print()

    def get_deployment_recommendations(self) -> None:
        """Mostrar recomendaciones de despliegue"""
        print(f"{BOLD}📋 RECOMENDACIONES DE DESPLIEGUE:{RESET}\n")

        recommendations = [
            "1. Usar gestor de secretos (AWS Secrets Manager, HashiCorp Vault)",
            "2. Configurar CORS específicamente (no permitir *)",
            "3. Establecer rate limiting en Nginx",
            "4. Configurar SSL/TLS con Let's Encrypt",
            "5. Implementar monitoreo (logs centralizados)",
            "6. Configurar backups automáticos",
            "7. Usar reverse proxy (Nginx) en producción",
            "8. Ejecutar tests antes de desplegar",
            "9. Tener plan de rollback",
            "10. Monitorear health checks regularmente",
        ]

        for rec in recommendations:
            print(f"  {BLUE}{rec}{RESET}")

        print()


def main():
    """Función principal"""
    validator = DeploymentValidator()

    # Cambiar a directorio del backend si es necesario
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # Ejecutar validaciones
    success = validator.run_all_checks()

    # Mostrar recomendaciones
    if validator.checks_failed == 0:
        validator.get_deployment_recommendations()

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
