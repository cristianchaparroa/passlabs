# 🔐 Configurar Tokens Permitidos en el Contrato

## Problema

Estás recibiendo este error al intentar crear un pago:

```
ERROR - Error checking token allowed: Could not transact with/call contract function
ERROR - Token StablecoinEnum.USDC is not allowed in payment contract
```

**Causa:** Los tokens USDC, USDT y DAI no están agregados como "tokens permitidos" en el contrato `PaymentProcessor`.

## Solución

El contrato `PaymentProcessor` es muy seguro por diseño: solo acepta transferencias de tokens que el owner (propietario) ha agregado explícitamente. Esto previene que alguien transfiera tokens no autorizados.

Necesitas ejecutar un script que agrega estos tokens al contrato.

## Requisitos Previos

1. **Contrato deployed**: El contrato debe estar ya desplegado en Scroll Sepolia
2. **Variables de entorno configuradas** en `.env`:
   - `CONTRACT_ADDRESS`: Dirección del contrato PaymentProcessor
   - `PRIVATE_KEY`: Clave privada del owner del contrato
   - `RPC_URL`: URL del RPC (por defecto: https://sepolia-rpc.scroll.io/)
   - `USDC_ADDRESS`, `USDT_ADDRESS`, `DAI_ADDRESS`: Direcciones de los tokens

3. **ETH en la cuenta**: Necesitas tener ETH en Scroll Sepolia para pagar el gas de las transacciones

## Pasos para Configurar

### 1. Verifica tu archivo `.env`

```bash
cd backend
cat .env
```

Debe contener algo como esto:

```
# Blockchain
NETWORK=scroll-sepolia
RPC_URL=https://sepolia-rpc.scroll.io/
PRIVATE_KEY=0x1234567890abcdef...  # Tu clave privada
CONTRACT_ADDRESS=0x1234...         # Dirección del contrato desplegado
CHAIN_ID=534351

# Tokens (Scroll Sepolia testnet)
USDC_ADDRESS=0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238
USDT_ADDRESS=0x186C0C26c45A8DA1Da34339ee513624a9609156d
DAI_ADDRESS=0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6
```

Si `CONTRACT_ADDRESS` está vacío o es `0x0000...`, primero debes desplegar el contrato. Ver: `DEPLOYMENT_STATUS.md`

### 2. Asegúrate de tener ETH

Necesitas ETH en Scroll Sepolia para pagar el gas. Obtén testnet ETH:

1. Ve a https://scroll.io/bridge
2. Usa el puente de Scroll para pasar ETH de Ethereum Sepolia a Scroll Sepolia
3. O usa un faucet: https://scroll-testnet-faucet.allthatnode.com:3001/

Verifica tu balance:

```bash
python -c "
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))
from eth_keys import keys
pk = keys.PrivateKey(bytes.fromhex(os.getenv('PRIVATE_KEY').replace('0x', '')))
address = pk.public_key.to_checksum_address()
balance = w3.eth.get_balance(address)
print(f'Balance: {w3.from_wei(balance, \"ether\")} ETH')
"
```

### 3. Ejecuta el script de configuración

```bash
python deployment/add_allowed_tokens.py
```

El script hará lo siguiente:

1. ✅ Valida la configuración
2. 🔗 Se conecta a Scroll Sepolia
3. 📋 Carga el contrato PaymentProcessor
4. 🔎 Verifica qué tokens ya están permitidos
5. ➕ Agrega los tokens que falten
6. ✅ Verifica que todo está correcto

### 4. Ejemplo de ejecución exitosa

```
============================================================
🔐 Script para Agregar Tokens Permitidos
============================================================

ℹ️  Este script agrega USDC, USDT y DAI al contrato PaymentProcessor
ℹ️  Esto es REQUERIDO para que el sistema funcione correctamente

============================================================
🔍 Validando Configuración
============================================================

ℹ️  RPC URL: https://sepolia-rpc.scroll.io/
ℹ️  Private Key cargada: 0x1234567...9abc
ℹ️  Contract Address: 0x1234567890abcdef...
ℹ️  USDC Address: 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238
ℹ️  USDT Address: 0x186C0C26c45A8DA1Da34339ee513624a9609156d
ℹ️  DAI Address: 0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6
✅ Configuración válida

============================================================
🔗 Conectando a Blockchain
============================================================

✅ Conectado a blockchain: https://sepolia-rpc.scroll.io/
ℹ️  Chain ID: 534351 (Expected: 534351)
ℹ️  Block Number: 12345678
✅ Cuenta cargada: 0xYourAddress...
ℹ️  Balance: 0.5 ETH

============================================================
📋 Cargando Contrato
============================================================

✅ ABI cargado con 28 elementos
✅ Contrato cargado: 0x1234567890abcdef...
ℹ️  Contract Owner: 0xYourAddress...

============================================================
🔎 Verificando Estado de Tokens
============================================================

⚠️  USDC: ❌ NO PERMITIDO (necesita agregarse)
⚠️  USDT: ❌ NO PERMITIDO (necesita agregarse)
⚠️  DAI: ❌ NO PERMITIDO (necesita agregarse)

============================================================
➕ Agregando Tokens Permitidos al Contrato
============================================================

ℹ️  Necesita agregar 3 token(s):
  - USDC: 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238
  - USDT: 0x186C0C26c45A8DA1Da34339ee513624a9609156d
  - DAI: 0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6

Agregando USDC...
ℹ️  Gas Price: 2.5 Gwei
ℹ️  Estimated Gas: 45000
ℹ️  Transaction Hash: 0xabc123def456...
ℹ️  Esperando confirmación...
✅ USDC agregado exitosamente
   Block: 12345679
   Gas Used: 42156

Agregando USDT...
✅ USDT agregado exitosamente
   Block: 12345680
   Gas Used: 42156

Agregando DAI...
✅ DAI agregado exitosamente
   Block: 12345681
   Gas Used: 42156

============================================================
✅ Verificando Tokens Agregados
============================================================

✅ USDC: ✅ PERMITIDO en el contrato
✅ USDT: ✅ PERMITIDO en el contrato
✅ DAI: ✅ PERMITIDO en el contrato

============================================================
✅ ¡ÉXITO! Todos los tokens están configurados correctamente
============================================================

✅ El sistema está listo para procesar pagos
ℹ️  Resultados guardados en: deployment/add_tokens_results.json
```

## Después de la Configuración

Ahora puedes:

1. ✅ Probar el endpoint de crear pagos:

```bash
curl -X POST http://localhost:8000/payments/create \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_address": "0xa92d504731aa3e99df20ffd200ed03f9a55a6219",
    "amount": 1.0,
    "stablecoin": "USDC",
    "description": "Test payment"
  }'
```

2. ✅ Ver el estado de los pagos:

```bash
curl http://localhost:8000/payments/all
```

3. ✅ Verificar precios de stablecoins:

```bash
curl http://localhost:8000/stablecoins/prices
```

## Solución de Problemas

### Error: "PRIVATE_KEY no configurada"

```bash
echo $PRIVATE_KEY
```

Si está vacío, configúralo:

```bash
export PRIVATE_KEY=0x1234567890abcdef...
```

O edita el archivo `.env`:

```bash
nano .env
```

### Error: "No se puede conectar a RPC"

Verifica que el RPC URL es correcto:

```bash
curl https://sepolia-rpc.scroll.io/
```

### Error: "Balance es 0"

Necesitas obtener ETH de testnet. Ver sección "Asegúrate de tener ETH" arriba.

### Error: "Transacción revertida"

Posibles causas:
- No eres el owner del contrato
- El gas limit es insuficiente
- Hay un error en el contrato

Revisa la transacción en: https://sepolia.scrollscan.com/

### Error: "Contract not loaded"

El ABI del contrato no se encuentra. Verifica:

```bash
ls -la contracts/contract_abi.json
```

Si no existe, obtén el ABI del contrato desplegado en Scrollscan.

## Verificación Manual

Si quieres verificar el estado sin ejecutar el script:

```bash
python -c "
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))

# Cargar ABI
with open('contracts/contract_abi.json') as f:
    abi = json.load(f)

# Crear contrato
contract = w3.eth.contract(
    address=Web3.to_checksum_address(os.getenv('CONTRACT_ADDRESS')),
    abi=abi
)

# Verificar tokens
tokens = {
    'USDC': os.getenv('USDC_ADDRESS'),
    'USDT': os.getenv('USDT_ADDRESS'),
    'DAI': os.getenv('DAI_ADDRESS'),
}

print('Estado de tokens:')
for name, addr in tokens.items():
    is_allowed = contract.functions.isTokenAllowed(
        Web3.to_checksum_address(addr)
    ).call()
    status = '✅' if is_allowed else '❌'
    print(f'{status} {name}: {\"PERMITIDO\" if is_allowed else \"NO PERMITIDO\"}')"
```

## Información de Referencia

### Direcciones de Tokens en Scroll Sepolia

| Token | Dirección |
|-------|-----------|
| USDC | `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238` |
| USDT | `0x186C0C26c45A8DA1Da34339ee513624a9609156d` |
| DAI | `0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6` |

### Exploradores

- Scroll Sepolia: https://sepolia.scrollscan.com/
- Transacciones: https://sepolia.scrollscan.com/tx/{txHash}
- Contratos: https://sepolia.scrollscan.com/address/{address}

### Documentación Relevante

- [Deployment Status](./DEPLOYMENT_STATUS.md)
- [Contrato PaymentProcessor](./contracts/PaymentProcessor.sol)
- [API Documentation](./README.md)

## Próximos Pasos

Una vez configurados los tokens:

1. **Obtener testnet stablecoins**: Usa un faucet para obtener USDC, USDT o DAI de testnet
2. **Hacer approve**: Los usuarios deben hacer `approve()` para que el contrato pueda gastar sus tokens
3. **Crear pagos**: Ya puedes usar el endpoint `/payments/create`
4. **Monitorear transacciones**: Usa `/payments/status/{tx_hash}` para verificar el estado

## Soporte

Si encuentras problemas:

1. Revisa los logs: `tail -f logs/*.log`
2. Verifica la configuración: `cat .env`
3. Prueba la conexión: `python deploy_check.py`
4. Revisa el estado del contrato en: https://sepolia.scrollscan.com/
