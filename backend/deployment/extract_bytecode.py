#!/usr/bin/env python3
"""
Utilidad para Extraer y Validar Bytecode del Contrato PaymentProcessor

Este script ayuda a:
1. Extraer bytecode desde artifact JSON de Hardhat
2. Extraer bytecode desde archivos .bin de solc
3. Validar que el bytecode es correcto
4. Actualizar deploy_final.py automáticamente con el bytecode

Uso:
    python3 extract_bytecode.py --from-hardhat artifacts/contracts/PaymentProcessor.sol/PaymentProcessor.json
    python3 extract_bytecode.py --from-solc output/PaymentProcessor.bin
    python3 extract_bytecode.py --validate "0x608060..."
    python3 extract_bytecode.py --update-deploy-script
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple


class BytecodeExtractor:
    """Extrae y valida bytecode de varias fuentes"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.deploy_script = self.project_root / "deployment" / "deploy_final.py"

    def extract_from_hardhat(self, json_file: str) -> Optional[str]:
        """
        Extrae bytecode desde artifact JSON de Hardhat

        Args:
            json_file: Ruta al archivo JSON del artifact

        Returns:
            Bytecode con prefijo "0x" o None si falla
        """
        try:
            with open(json_file, "r") as f:
                artifact = json.load(f)

            # El bytecode puede estar en diferentes ubicaciones
            bytecode = artifact.get("bytecode") or artifact.get("evm", {}).get(
                "bytecode", {}
            ).get("object")

            if not bytecode:
                print(f"❌ No se encontró bytecode en {json_file}")
                return None

            # Asegurar que tiene prefijo 0x
            if not bytecode.startswith("0x"):
                bytecode = "0x" + bytecode

            print(f"✅ Bytecode extraído desde Hardhat artifact")
            print(f"   Longitud: {len(bytecode)} caracteres")
            return bytecode

        except Exception as e:
            print(f"❌ Error extrayendo desde Hardhat: {str(e)}")
            return None

    def extract_from_solc(self, bin_file: str) -> Optional[str]:
        """
        Extrae bytecode desde archivo .bin de solc

        Args:
            bin_file: Ruta al archivo .bin

        Returns:
            Bytecode con prefijo "0x" o None si falla
        """
        try:
            with open(bin_file, "r") as f:
                bytecode = f.read().strip()

            # Limpiar espacios y saltos de línea
            bytecode = "".join(bytecode.split())

            # Asegurar que tiene prefijo 0x
            if not bytecode.startswith("0x"):
                bytecode = "0x" + bytecode

            print(f"✅ Bytecode extraído desde archivo solc")
            print(f"   Longitud: {len(bytecode)} caracteres")
            return bytecode

        except Exception as e:
            print(f"❌ Error extrayendo desde solc: {str(e)}")
            return None

    def validate_bytecode(self, bytecode: str) -> Tuple[bool, str]:
        """
        Valida que el bytecode es correcto

        Args:
            bytecode: El bytecode a validar

        Returns:
            Tupla (es_válido, mensaje)
        """
        errors = []

        # Verificar que no está vacío
        if not bytecode:
            return False, "Bytecode está vacío"

        # Verificar prefijo 0x
        if not bytecode.startswith("0x"):
            errors.append("⚠️  Falta prefijo '0x'")
            bytecode = "0x" + bytecode

        # Verificar que solo contiene caracteres hex
        hex_part = bytecode[2:]  # Sin el "0x"
        if not all(c in "0123456789abcdefABCDEF" for c in hex_part):
            return (
                False,
                "❌ Contiene caracteres inválidos (solo 0-9, a-f permitidos)",
            )

        # Verificar longitud mínima (al menos 68 caracteres = 34 bytes)
        if len(hex_part) < 68:
            errors.append(
                f"⚠️  Bytecode muy corto ({len(hex_part)} caracteres hex, esperado >68)"
            )

        # Verificar que probablemente sea bytecode válido
        # El bytecode válido usualmente comienza con 60 (PUSH1), 61 (PUSH2), etc.
        if not hex_part.startswith(("60", "61", "62", "63")):
            errors.append(
                f"⚠️  Puede no ser bytecode válido (comienza con {hex_part[:2]})"
            )

        # Compilar resultados
        if errors and len(hex_part) > 2000:
            # Si es lo suficientemente largo, probablemente sea válido
            return True, "✅ Bytecode válido\n" + "\n".join(errors)
        elif errors:
            return False, "❌ Validación falló:\n" + "\n".join(errors)
        else:
            return True, f"✅ Bytecode válido ({len(bytecode)} caracteres)"

    def print_bytecode_info(self, bytecode: str):
        """Imprime información del bytecode"""
        print(f"\n📦 Información del Bytecode")
        print(f"   Longitud total: {len(bytecode)} caracteres")
        print(f"   Longitud hex (sin 0x): {len(bytecode) - 2} caracteres")
        print(f"   Bytes: {(len(bytecode) - 2) // 2} bytes")
        print(f"   Primeros 100 chars: {bytecode[:100]}...")
        print(f"   Últimos 50 chars: ...{bytecode[-50:]}")

    def save_to_file(self, bytecode: str, output_file: str = "bytecode.txt"):
        """Guarda el bytecode en un archivo de texto"""
        try:
            with open(output_file, "w") as f:
                f.write(bytecode)
            print(f"\n✅ Bytecode guardado en {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error guardando bytecode: {str(e)}")
            return False

    def update_deploy_script(self, bytecode: str, dry_run: bool = True) -> bool:
        """
        Actualiza deploy_final.py con el bytecode

        Args:
            bytecode: El bytecode a insertar
            dry_run: Si True, solo muestra lo que haría

        Returns:
            True si tuvo éxito
        """
        try:
            if not self.deploy_script.exists():
                print(f"❌ Script no encontrado: {self.deploy_script}")
                return False

            with open(self.deploy_script, "r") as f:
                content = f.read()

            # Buscar la línea de BYTECODE
            pattern = r'PAYMENT_PROCESSOR_BYTECODE\s*=\s*(?:None|"[^"]*"|\'[^\']*\')'
            replacement = f'PAYMENT_PROCESSOR_BYTECODE = "{bytecode}"'

            if not re.search(pattern, content):
                print(
                    f"❌ No se encontró PAYMENT_PROCESSOR_BYTECODE en {self.deploy_script}"
                )
                return False

            new_content = re.sub(pattern, replacement, content)

            if dry_run:
                print(f"\n📝 Cambios que se harían:")
                print(f"   Archivo: {self.deploy_script}")
                print(f"   Patrón: PAYMENT_PROCESSOR_BYTECODE = ...")
                print(f"   Nuevo valor: {replacement[:80]}...")
                return True
            else:
                with open(self.deploy_script, "w") as f:
                    f.write(new_content)
                print(f"\n✅ Script actualizado: {self.deploy_script}")
                return True

        except Exception as e:
            print(f"❌ Error actualizando script: {str(e)}")
            return False


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extrae y valida bytecode del contrato PaymentProcessor"
    )

    parser.add_argument(
        "--from-hardhat",
        help="Extraer bytecode desde archivo JSON de Hardhat artifact",
        metavar="FILE",
    )
    parser.add_argument(
        "--from-solc",
        help="Extraer bytecode desde archivo .bin de solc",
        metavar="FILE",
    )
    parser.add_argument(
        "--validate", help="Validar un bytecode dado", metavar="BYTECODE"
    )
    parser.add_argument(
        "--update-deploy-script",
        action="store_true",
        help="Actualizar deploy_final.py con el bytecode (requiere --from-hardhat o --from-solc)",
    )
    parser.add_argument(
        "--save-to-file",
        help="Guardar bytecode en archivo",
        metavar="FILE",
        default="bytecode.txt",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Ejecutar cambios sin modo dry-run",
    )

    args = parser.parse_args()

    extractor = BytecodeExtractor()
    bytecode = None

    # Extraer bytecode de la fuente especificada
    if args.from_hardhat:
        bytecode = extractor.extract_from_hardhat(args.from_hardhat)
    elif args.from_solc:
        bytecode = extractor.extract_from_solc(args.from_solc)
    elif args.validate:
        bytecode = args.validate
    else:
        parser.print_help()
        return

    if not bytecode:
        print("❌ No se pudo obtener bytecode")
        sys.exit(1)

    # Validar
    print("\n🔍 Validando bytecode...")
    is_valid, message = extractor.validate_bytecode(bytecode)
    print(message)

    if not is_valid:
        print("❌ Validación fallida")
        sys.exit(1)

    # Mostrar información
    extractor.print_bytecode_info(bytecode)

    # Guardar en archivo si se solicita
    if args.save_to_file:
        extractor.save_to_file(bytecode, args.save_to_file)

    # Actualizar script de deployment si se solicita
    if args.update_deploy_script:
        dry_run = not args.no_dry_run
        success = extractor.update_deploy_script(bytecode, dry_run=dry_run)

        if success and dry_run:
            print("\n💡 Para aplicar los cambios, ejecuta:")
            print(
                f"   python3 extract_bytecode.py --from-{('hardhat' if args.from_hardhat else 'solc')} {'...'} --update-deploy-script --no-dry-run"
            )

        sys.exit(0 if success else 1)

    print("\n✅ Bytecode válido y listo para usar")
    print(f"\nPara usar en deploy_final.py:")
    print(f"  1. Abre deployment/deploy_final.py")
    print(f"  2. Busca: PAYMENT_PROCESSOR_BYTECODE = None")
    print(f'  3. Reemplaza con: PAYMENT_PROCESSOR_BYTECODE = "{bytecode[:50]}..."')
    print(f"\nO ejecuta automáticamente:")
    print(
        f"  python3 extract_bytecode.py --from-{'hardhat' if args.from_hardhat else 'solc'} ... --update-deploy-script --no-dry-run"
    )


if __name__ == "__main__":
    main()
