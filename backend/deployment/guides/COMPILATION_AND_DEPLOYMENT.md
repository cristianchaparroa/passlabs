# Guía Completa: Compilación y Deployment del Contrato PaymentProcessor en Scroll Sepolia

## Parte 1: Compilar el Contrato en Remix IDE

### Paso 1: Acceder a Remix IDE
1. Abre https://remix.ethereum.org en tu navegador
2. Espera a que cargue completamente (puede tomar 30 segundos)

### Paso 2: Crear el Archivo del Contrato
1. En el panel izquierdo, haz clic en el icono "File Explorer" (carpeta)
2. Haz clic en "Create New File"
3. Nombre del archivo: `PaymentProcessor.sol`
4. Copia el contenido completo de `/home/oscar/Github/passlabs/backend/contracts/PaymentProcessor.sol`
5. Pégalo en el editor de Remix

### Paso 3: Configurar el Compilador
1. Haz clic en el icono "Solidity Compiler" (en el panel izquierdo)
2. Versión del compilador: `0.8.0` (o la versión especificada en el pragma del contrato)
3. EVM Version: `istanbul` o `default`
4. Haz clic en "Compile PaymentProcessor.sol"
5. Espera a que aparezca el checkmark verde ✅

### Paso 4: Obtener el Bytecode
1. En el panel "Solidity Compiler", busca la sección "Compilation Details"
2. Haz clic en "Compilation Details"
3. Busca la sección "Object" - este es tu bytecode
4. Copia toda la cadena hexadecimal (comenzará con números/letras, NO necesita "0x" al principio, pero lo agregaremos)
5. Si es muy largo, copia todo (puede ser de 5000+ caracteres)

**Ejemplo de what you'll see:**
```
Object: 608060405234801561001057600080fd5b50611234...
```

## Parte 2: Actualizar el Bytecode en el Script

### Paso 1: Editar deploy_final.py
1. Abre `/home/oscar/Github/passlabs/backend/deployment/deploy_final.py`
2. Busca la línea que dice: `PAYMENT_PROCESSOR_BYTECODE = None  # ← REEMPLAZA CON TU BYTECODE`
3. Reemplaza `None` con `"0x" + <tu_bytecode_copiado>`

**Ejemplo:**
```python
PAYMENT_PROCESSOR_BYTECODE = "0x608060405234801561001057600080fd5b50611234..."
```

### Paso 2: Asegurate que .env está configurado correctamente
```bash
cat passlabs/backend/.env | grep -E "PRIVATE_KEY|RPC_URL|CHAIN_ID|CONTRACT_ADDRESS"
```

Deberías ver:
- `PRIVATE_KEY=0x...` (tu clave privada)
- `RPC_URL=https://sepolia-rpc.scroll.io/`
- `CHAIN_ID=534351`
- `CONTRACT_ADDRESS=` (puede estar vacío)

## Parte 3: Desplegar el Contrato

### Opción A: Deployment Automático (Recomendado)

```bash
cd passlabs/backend
python3 deployment/deploy_final.py --update-env
```

**Qué hace:**
1. Compila el bytecode en bytecode machine
2. Crea la transacción de deployment
3. Calcula el gas necesario
4. Envía la transacción a Scroll Sepolia
5. Espera la confirmación (puede tomar 15-60 segundos)
6. Actualiza automáticamente `CONTRACT_ADDRESS` en `.env`

### Opción B: Dry Run (Sin Enviar Transacción)

```bash
cd passlabs/backend
python3 deployment/deploy_final.py --dry-run
```

Esto simula el deployment sin gastar gas. Útil para verificar que todo está correcto.

### Opción C: Verificación Manual
Si quieres verificar manualmente que el contrato está desplegado:

```bash
cd passlabs/backend
python3 deployment/deploy_final.py --verify-only <CONTRACT_ADDRESS>
```

Reemplaza `<CONTRACT_ADDRESS>` con la dirección del contrato que obtuviste.

## Parte 4: Verificar el Deployment

### Verificación Local
```bash
cd passlabs/backend
python3 deploy_check.py
```

Esto verificará:
- ✅ Conexión a RPC
- ✅ Balance de la wallet
- ✅ CONTRACT_ADDRESS está configurado
- ✅ Archivo ABI existe
- ✅ Contrato se puede cargar

### Verificación en Blockchain
1. Abre https://sepolia.scrollscan.com
2. Pega la dirección del contrato en la barra de búsqueda
3. Deberías ver:
   - "Contract" badge
   - Bytecode
   - Transacciones
   - Funciones del contrato

**Ejemplo URL:**
```
https://sepolia.scrollscan.com/address/0xYourContractAddressHere
```

## Parte 5: Autorizar Stablecoins en el Contrato

Una vez desplegado, necesitas autorizar los tokens en el contrato:

```bash
cd passlabs/backend
python3 -c "
from services.blockchain_service import BlockchainService
from config import settings

blockchain = BlockchainService()

# Autorizar USDC
blockchain.add_allowed_token(settings.USDC_ADDRESS)
print(f'✅ USDC autorizado: {settings.USDC_ADDRESS}')

# Autorizar USDT
blockchain.add_allowed_token(settings.USDT_ADDRESS)
print(f'✅ USDT autorizado: {settings.USDT_ADDRESS}')

# Autorizar DAI
blockchain.add_allowed_token(settings.DAI_ADDRESS)
print(f'✅ DAI autorizado: {settings.DAI_ADDRESS}')
"
```

## Parte 6: Probar el Sistema

### Test Simple
```bash
cd passlabs/backend

# Iniciar el servidor
python3 main.py

# En otra terminal, hacer una request de prueba
curl -X POST http://localhost:8000/payments/create \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1.0,
    "stablecoin": "USDC",
    "recipient_address": "0xa92d504731aa3e99df20ffd200ed03f9a55a6219"
  }'
```

### Respuesta Esperada (Éxito)
```json
{
  "payment_id": "0xabc123...",
  "amount": 1.0,
  "stablecoin": "USDC",
  "recipient": "0xa92d504731aa3e99df20ffd200ed03f9a55a6219",
  "status": "pending",
  "timestamp": "2025-11-20T08:00:59Z"
}
```

## Troubleshooting

### Error: "BYTECODE no configurado"
**Solución:** Ve al Paso 2 y asegúrate de haber copiado el bytecode correctamente desde Remix.

### Error: "No conectado a RPC"
**Solución:** Verifica que RPC_URL en `.env` sea correcto:
```
RPC_URL=https://sepolia-rpc.scroll.io/
```

### Error: "Insufficient funds"
**Solución:** Tu wallet necesita ETH en Scroll Sepolia. Usa el faucet:
```
https://scroll.io/sepolia/faucet
```

### Error: "Token not allowed in contract"
**Solución:** Ejecuta el Paso 5 para autorizar los tokens en el contrato.

### Error: "Contract deployed correctly and chain synced?"
**Solución:** 
1. Verifica que CONTRACT_ADDRESS en `.env` es correcto
2. Espera 30 segundos después del deployment
3. Verifica en Scrollscan que el contrato existe

## Información Útil

### Gas Estimado
- Deployment: ~200,000 - 500,000 gas
- Precio gas en Scroll Sepolia: ~0.0157 Gwei (muy barato)
- Costo total estimado: < $0.001 USD

### Direcciones de Tokens en Scroll Sepolia
- USDC: `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238`
- USDT: `0x186C0C26c45A8DA1Da34339ee513624a9609156d`
- DAI: `0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6`

### Enlaces Útiles
- Remix IDE: https://remix.ethereum.org
- Scroll Sepolia Explorer: https://sepolia.scrollscan.com
- Scroll Sepolia Faucet: https://scroll.io/sepolia/faucet
- Scroll Docs: https://docs.scroll.io