"""
Script para ejecutar todos los tests de la FASE 5 (Testing & Polish)

Ejecuta:
- Tests de rutas de pagos
- Tests de rutas de stablecoins
- Tests de servicios
- Tests de validadores
- Tests de setup

Uso:
    python run_tests.py              # Ejecutar todos los tests
    python run_tests.py --verbose    # Con salida detallada
    python run_tests.py --coverage   # Con cobertura de código
    python run_tests.py payments     # Solo tests de pagos
    python run_tests.py stablecoins  # Solo tests de stablecoins
    python run_tests.py services     # Solo tests de servicios
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n{'=' * 70}")
    print(f"🧪 {description}")
    print(f"{'=' * 70}")
    print(f"Ejecutando: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0


def main():
    """Ejecutar tests según parámetros"""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    coverage = "--coverage" in sys.argv or "-c" in sys.argv
    specific_test = None

    # Identificar test específico
    for arg in sys.argv[1:]:
        if arg.lower() in [
            "payments",
            "stablecoins",
            "services",
            "setup",
            "validators",
        ]:
            specific_test = arg.lower()
            break

    # Construir comando base
    cmd_base = ["python", "-m", "pytest", "-v" if verbose else "-q"]

    if coverage:
        cmd_base.extend(["--cov=.", "--cov-report=html"])

    # Diccionario de tests
    test_files = {
        "payments": "test_payments_routes.py",
        "stablecoins": "test_stablecoins_routes.py",
        "services": "test_services.py",
        "setup": "test_setup.py",
        "validators": "test_validators.py",
    }

    results = {}

    try:
        if specific_test and specific_test in test_files:
            # Ejecutar test específico
            cmd = cmd_base + [test_files[specific_test]]
            results[specific_test] = run_command(cmd, f"Tests de {specific_test}")
        else:
            # Ejecutar todos los tests
            print("=" * 70)
            print("🧪 EJECUTANDO TODOS LOS TESTS - FASE 5")
            print("=" * 70)

            for test_name, test_file in test_files.items():
                cmd = cmd_base + [test_file]
                results[test_name] = run_command(
                    cmd, f"Tests de {test_name} ({test_file})"
                )

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrumpidos por el usuario")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error ejecutando tests: {e}")
        return 1

    # Mostrar resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE TESTS")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"{test_name.upper()}: {status}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("✅ TODOS LOS TESTS PASARON")
        if coverage:
            print("📊 Reporte de cobertura disponible en: htmlcov/index.html")
        return 0
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        return 1


if __name__ == "__main__":
    sys.exit(main())
