# 🔴 FIX: Token Not Allowed in Payment Contract

## El Problema

Estás recibiendo este error:

```
ERROR - Error checking token allowed: Could not transact with/call contract function
WARNING - Token StablecoinEnum.USDC not allowed in contract
ERROR - Validation error creating payment: Token StablecoinEnum.USDC is not allowed in payment contract
```

## La Causa

El Smart Contract `PaymentProcessor` requiere que **cada token sea agregado explícitamente por el owner** antes de poder procesarlo. Es una medida de seguridad.

Actualmente, USDC, USDT y DAI NO están permitidos en tu contrato.

## La Solución (3 Pasos)

### ✅ Paso 1: Verificar `.env`

Asegúrate de tener en `backend/.env`:

```bash
# Debe estar configurado el contrato desplegado
CONTRACT_ADDRESS=0x...

# Tu clave privada (que debe ser el owner del contrato)
PRIVATE_KEY=0x...

# Direcciones de tokens (estas son correctas para Scroll Sepolia)
USDC_ADDRESS=0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238
USDT_ADDRESS=0x186C0C26c45A8DA1Da34339ee513624a9609156d
DAI_ADDRESS=0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6

# RPC URL
RPC_URL=https://sepolia-rpc.scroll.io/

# Chain ID
CHAIN_ID=534351
```

### ✅ Paso 2: Asegurar que tienes ETH

Necesitas ETH en Scroll Sepolia para pagar el gas:

```bash
# Obtén testnet ETH aquí:
# https://scroll-testnet-faucet.allthatnode.com:3001/
# O usa el puente: https://scroll.io/bridge

# Verifica tu balance:
curl -X POST https://sepolia-rpc.scroll.io/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"eth_getBalance",
    "params":["0xTU_ADDRESS_AQUI", "latest"],
    "id":1
  }'
```

### ✅ Paso 3: Ejecutar el Script (ESTO ES LO IMPORTANTE)

```bash
cd backend
python deployment/add_allowed_tokens.py
```

Este script:
- ✅ Conecta al blockchain
- ✅ Verifica qué tokens están permitidos
- ✅ Agrega los que faltan
- ✅ Espera confirmación
- ✅ Verifica que todo está bien

**El script te guiará interactivamente. Solo sigue las instrucciones.**

## Después de Ejecutar el Script

Una vez que veas:
```
✅ USDC: ✅ PERMITIDO en el contrato
✅ USDT: ✅ PERMITIDO en el contrato
✅ DAI: ✅ PERMITIDO en el contrato
```

Ya puedes:

1. Reiniciar el servidor
2. Probar nuevamente el endpoint `/payments/create`

## Verificación Rápida

Para verificar sin ejecutar el script completo:

```bash
python -c "
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))

with open('contracts/contract_abi.json') as f:
    abi = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(os.getenv('CONTRACT_ADDRESS')),
    abi=abi
)

tokens = {
    'USDC': os.getenv('USDC_ADDRESS'),
    'USDT': os.getenv('USDT_ADDRESS'),
    'DAI': os.getenv('DAI_ADDRESS'),
}

for name, addr in tokens.items():
    is_allowed = contract.functions.isTokenAllowed(
        Web3.to_checksum_address(addr)
    ).call()
    status = '✅' if is_allowed else '❌'
    print(f'{status} {name}')
"
```

## Problemas Comunes

| Problema | Solución |
|----------|----------|
| "PRIVATE_KEY no configurada" | Edita `.env` y agrega tu clave privada |
| "Balance es 0" | Obtén testnet ETH (ver Paso 2) |
| "Not the contract owner" | Solo el owner puede agregar tokens |
| "Transaction timeout" | Espera unos minutos e intenta de nuevo |
| "Connection refused" | Verifica que RPC_URL es correcto |

## Documentación Completa

Para más detalles, lee: `CONFIGURE_TOKENS.md`

## Resumen

```
❌ ANTES (Error)
POST /payments/create → "Token not allowed"

✅ DESPUÉS (Funciona)
python deployment/add_allowed_tokens.py → Ejecutar una sola vez
POST /payments/create → ✅ Éxito!
```

**Eso es todo lo que necesitas hacer. El script maneja todo lo demás automáticamente.**
