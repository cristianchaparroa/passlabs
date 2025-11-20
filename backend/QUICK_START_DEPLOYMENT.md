# 🚀 GUÍA RÁPIDA: Desplegar el Contrato y Arreglar el Error de Pagos

**NOTA IMPORTANTE**: El contrato ahora requiere un parámetro `_initialOwner` en el constructor. El script de deployment automático maneja esto, pero si usas Remix manualmente, asegúrate de pasar tu dirección como owner inicial.

## ⚠️ Problema Actual

```
Error: "Could not transact with/call contract function, is contract deployed correctly?"
Causa: CONTRACT_ADDRESS está vacío o el contrato no fue desplegado
```

---

## ✅ Solución en 3 Pasos (15 minutos)

### PASO 1: Compilar el Contrato (5 minutos)

#### Opción A: Remix IDE (Más Fácil - RECOMENDADO)

1. Abre **https://remix.ethereum.org** en tu navegador
2. Crea archivo nuevo: `PaymentProcessor.sol`
3. Copia todo el contenido de:
   ```
   passlabs/backend/contracts/PaymentProcessor.sol
   ```
4. En Remix, haz clic en **"Solidity Compiler"** (icono engranaje, izquierda)
5. Selecciona versión: **0.8.0** o posterior
6. Haz clic: **"Compile PaymentProcessor.sol"**
7. Espera el checkmark ✅ verde

#### Opción B: Hardhat (Si prefieres local)

```bash
cd passlabs/backend
npm install --save-dev hardhat @openzeppelin/contracts
npx hardhat compile
```

---

### PASO 2: Obtener el Bytecode (3 minutos)

#### Si usaste Remix:

1. En Remix, haz clic en **"Compilation Details"** (en el panel Compiler)
2. Busca la sección: **"Object"**
3. **Copia TODO el código hex** (será muy largo, OK)
4. Debe verse así: `608060405234801561001057600080fd5b50...`

#### Si usaste Hardhat:

```bash
# El bytecode está en:
cat artifacts/contracts/PaymentProcessor.sol/PaymentProcessor.json | jq '.bytecode'
```

---

### PASO 3: Desplegar (7 minutos)

#### Opción A: Despliegue Automático (RECOMENDADO)

**NOTA**: El contrato ahora requiere un parámetro de constructor. El script automático maneja esto pasando tu dirección como owner inicial.

1. Abre `passlabs/backend/deployment/deploy_final.py`
2. Busca esta línea (cerca de línea 50):
   ```python
   PAYMENT_PROCESSOR_BYTECODE = None  # ← REEMPLAZA CON TU BYTECODE
   ```
3. Reemplaza `None` con tu bytecode completo:
   ```python
   PAYMENT_PROCESSOR_BYTECODE = "0x608060405234801561001057600080fd5b50..."
   ```
   
   **IMPORTANTE**: 
   - Incluye el prefijo `0x`
   - Usa comillas dobles
   - Pega TODO el bytecode sin espacios

4. En terminal, ejecuta:
   ```bash
   cd passlabs/backend
   python3 deployment/deploy_final.py --update-env
   ```

5. Espera 30-60 segundos. Verás:
   ```
   ✅ Contrato deployado en: 0x1234567890abcdef...
   ✅ .env actualizado
   ```

#### Opción B: Despliegue Manual desde Remix

**IMPORTANTE**: Si usas Remix manualmente, el contrato ahora requiere un parámetro de constructor:
- En la sección "Deploy", verás un campo para `_initialOwner`
- Ingresa tu dirección de wallet (la misma que `PRIVATE_KEY`)
- Luego haz clic en "Deploy"

1. En Remix, ve a **"Deploy & Run Transactions"** (icono play, izquierda)
2. Environment: **"Injected Provider"** (MetaMask)
3. Verifica MetaMask esté en **Scroll Sepolia**
4. Haz clic: **"Deploy"**
5. Confirma en MetaMask
6. Copia la dirección del contrato desplegado

Luego edita `.env`:
```
CONTRACT_ADDRESS=0x1234567890abcdef... (la dirección que copiaste)
```

---

## 🔧 Verificar que Funcionó

### Verificación 1: Local

```bash
cd passlabs/backend
python3 deploy_check.py
```

Deberías ver:
```
✅ CONTRACT_ADDRESS configurada correctamente
✅ Contrato se puede cargar
✅ Conexión a blockchain OK
```

### Verificación 2: Blockchain

1. Abre **https://sepolia.scrollscan.com**
2. Pega tu `CONTRACT_ADDRESS` en la barra de búsqueda
3. Deberías ver un badge "Contract"

---

## 🚀 Probar el API

### 1. Iniciar el servidor

```bash
cd passlabs/backend
python3 main.py
```

### 2. En otra terminal, hacer una petición de prueba

```bash
curl -X POST http://localhost:8000/payments/create \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1.0,
    "stablecoin": "USDC",
    "recipient_address": "0xa92d504731aa3e99df20ffd200ed03f9a55a6219"
  }'
```

### Respuesta esperada (éxito):

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

---

## 📋 Checklist de Configuración

Antes de desplegar, verifica:

```
✅ PRIVATE_KEY en .env (comienza con 0x)
✅ RPC_URL = https://sepolia-rpc.scroll.io/
✅ CHAIN_ID = 534351
✅ USDC_ADDRESS = 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238
✅ USDT_ADDRESS = 0x186C0C26c45A8DA1Da34339ee513624a9609156d
✅ DAI_ADDRESS = 0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6
✅ Balance en wallet (necesitas ETH para gas)
```

---

## ⚠️ Problemas Comunes

### "Insufficient funds"

Tu wallet no tiene ETH en Scroll Sepolia.

**Solución:** https://scroll.io/sepolia/faucet

### "BYTECODE no configurado"

No copiaste el bytecode correctamente.

**Solución:**
- Verifica que es muy largo (>3000 caracteres)
- Comienza con `0x` o `608060...`
- No tiene espacios en blanco

### "Could not transact with/call contract function"

El contrato aún no está desplegado.

**Solución:**
1. Verifica que CONTRACT_ADDRESS en .env no está vacío
2. Verifica en Scrollscan que existe: https://sepolia.scrollscan.com/address/0x...
3. Espera 30 segundos después del deployment

### "Token not allowed in contract"

El contrato fue desplegado pero no tiene autorización de tokens.

**Solución:** El contrato necesita ser inicializado. Esto se hace automáticamente durante el deployment, pero si no funcionó:

```bash
cd passlabs/backend
python3 -c "
from services.blockchain_service import BlockchainService
from config import settings

try:
    bc = BlockchainService()
    # Autorizar tokens
    bc.add_allowed_token(settings.USDC_ADDRESS)
    bc.add_allowed_token(settings.USDT_ADDRESS)
    bc.add_allowed_token(settings.DAI_ADDRESS)
    print('✅ Tokens autorizados')
except Exception as e:
    print(f'⚠️  Error: {e}')
"
```

---

## 📚 Archivos de Referencia

| Archivo | Propósito |
|---------|-----------|
| `deployment/COMPILATION_AND_DEPLOYMENT.md` | Guía completa detallada |
| `deployment/bytecode/BYTECODE_GUIDE.md` | Guía para obtener bytecode |
| `deployment/extract_bytecode.py` | Script para extraer/validar bytecode |
| `deployment/deploy_final.py` | Script de deployment automático |
| `deploy_check.py` | Verificar configuración |

---

## 🎯 Resumen Rápido

```bash
# 1. Compilar en Remix → Copiar bytecode

# 2. Editar deploy_final.py
sed -i 's/PAYMENT_PROCESSOR_BYTECODE = None/PAYMENT_PROCESSOR_BYTECODE = "0x..."/g' \
  passlabs/backend/deployment/deploy_final.py

# 3. Desplegar
cd passlabs/backend && python3 deployment/deploy_final.py --update-env

# 4. Verificar
python3 deploy_check.py

# 5. Probar
python3 main.py
# En otra terminal:
# curl -X POST http://localhost:8000/payments/create ...
```

---

## ✨ ¡Listo!

Una vez completado, tendrás:
- ✅ Contrato desplegado en Scroll Sepolia
- ✅ API funcional
- ✅ Sistema de pagos operativo

**Tiempo total:** ~15 minutos

Si necesitas más detalles, consulta `deployment/COMPILATION_AND_DEPLOYMENT.md`
