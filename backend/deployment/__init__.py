"""
Deployment Package - FASE 6

Este paquete contiene scripts y herramientas para:
1. Desplegar Smart Contract PaymentProcessor en Scroll Sepolia
2. Verificar el contrato en Scrollscan
3. Ejecutar tests en testnet
4. Generar reportes de deployment

Módulos disponibles:
- deploy_contract: Script principal de deployment
- verify_on_scrollscan: Verificación de contrato
- test_on_testnet: Testing en testnet

Uso:
    from deployment.deploy_contract import ContractDeployer
    deployer = ContractDeployer()
    deployer.run()
"""

__version__ = "0.6.0"
__author__ = "PassLabs Team"
__all__ = [
    "deploy_contract",
    "verify_on_scrollscan",
    "test_on_testnet",
]
