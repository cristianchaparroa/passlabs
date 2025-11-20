# 📦 Guía: Obtener y Usar el Bytecode del Contrato

## ¿Qué es el Bytecode?

El bytecode es el código máquina compilado de tu contrato Solidity. Es lo que se despliega realmente en blockchain.

**Nota Importante:** El bytecode es DIFERENTE del ABI. 
- **ABI**: Define las funciones (interfaz) - ya lo tienes en `contract_abi.json`
- **Bytecode**: Contiene toda la lógica del contrato compilada

---

## Método 1: Obtener Bytecode desde Remix IDE (RECOMENDADO)

### Paso 1: Ir a Remix
1. Abre https://remix.ethereum.org
2. Crea un archivo nuevo: `PaymentProcessor.sol`
3. Copia el contenido de `backend/contracts/PaymentProcessor.sol` en Remix

### Paso 2: Compilar
1. Haz clic en el icono **"Solidity Compiler"** (izquierda)
2. Selecciona Compiler Version: **0.8.0** (o similar)
3. Haz clic en **"Compile PaymentProcessor.sol"**
4. Espera a que aparezca ✅ (verde)

### Paso 3: Obtener el Bytecode
1. En el panel Compiler, haz clic en **"Compilation Details"** (pequeño botón)
2. Se abrirá una ventana con información
3. Busca la sección **"Object"** 
4. Copia TODO el texto hex (puede ser muy largo, 5000+ caracteres)

**Ejemplo de qué buscar:**
```
"Object": "608060405234801561001057600080fd5b50611234..."
```

### Paso 4: Copiar solo el hex (sin comillas ni "Object")
- Copia: `608060405234801561001057600080fd5b50611234...`
- NO copies: `"Object": "..."`

---

## Método 2: Compilar Localmente con Hardhat

### Requisitos
```bash
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat init  # Selecciona "Create a basic sample project"
```

### Compilar
```bash
cd backend
npx hardhat compile
```

El bytecode estará en:
```
artifacts/contracts/PaymentProcessor.sol/PaymentProcessor.json
```

Busca la clave `"bytecode"` en ese archivo.

---

## Método 3: Compilar con Solc (solc-js)

```bash
npm install -g solc

solcjs --bin --abi backend/contracts/PaymentProcessor.sol -o output/

# El bytecode estará en:
# output/PaymentProcessor_sol_PaymentProcessor.bin
```

---

## Usar el Bytecode para Desplegar

### Opción A: Script Automático (RECOMENDADO)

1. Abre `backend/deployment/deploy_final.py`
2. Busca esta línea:
   ```python
   PAYMENT_PROCESSOR_BYTECODE = None  # ← REEMPLAZA CON TU BYTECODE
   ```

3. Reemplaza con:
   ```python
   PAYMENT_PROCESSOR_BYTECODE = "0x608060405234801561001057600080fd5b50611234..."
   ```

4. Ejecuta:
   ```bash
   cd backend
   python3 deployment/deploy_final.py --update-env
   ```

### Opción B: Desplegar Manualmente desde Remix

1. En Remix, ve a **"Deploy & Run Transactions"** (icono play)
2. Selecciona Environment: **"Injected Provider"** (MetaMask)
3. Asegúrate que MetaMask está en **Scroll Sepolia**
4. Haz clic en **"Deploy"**
5. Confirma en MetaMask
6. Espera confirmación (30-60 segundos)
7. Copia la dirección del contrato desplegado

### Opción C: Desplegar con Web3.py (Avanzado)

```python
from web3 import Web3
from config import settings

w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
account = w3.eth.account.from_key(settings.PRIVATE_KEY)

# ABI del contrato
with open("contracts/contract_abi.json") as f:
    abi = json.load(f)

# Bytecode (reemplaza con el tuyo)
bytecode = "0x608060405234801561001057600080fd5b50611234..."

# Crear contrato
contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Construir transacción
constructor_tx = contract.constructor()

# Estimar gas
gas_estimate = constructor_tx.estimate_gas({"from": account.address})
print(f"Gas estimado: {gas_estimate}")

# Construir transacción completa
tx = constructor_tx.build_transaction({
    "from": account.address,
    "gas": gas_estimate,
    "gasPrice": w3.eth.gas_price,
    "nonce": w3.eth.get_transaction_count(account.address),
})

# Firmar
signed_tx = account.sign_transaction(tx)

# Enviar
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(f"Transacción enviada: {tx_hash.hex()}")

# Esperar confirmación
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
print(f"Contrato desplegado en: {receipt.contractAddress}")
```

---

## Verificar que el Bytecode es Correcto

### Verificación 1: Longitud
El bytecode debe tener **al menos 1000 caracteres hex**. Si es muy corto, probablemente copiaste mal.

```bash
python3 -c "
bytecode = '0x608060405234801561001057600080fd5b50611234...'
print(f'Longitud: {len(bytecode)} caracteres')
print(f'Válido: {len(bytecode) > 1000}')
"
```

### Verificación 2: Comienza con "0x"
El bytecode debe comenzar con `0x` (para indicar que es hexadecimal).

Si no comienza con `0x`, agrégalo manualmente:
```python
bytecode = "0x" + bytecode  # si falta el 0x
```

### Verificación 3: Solo caracteres hex
El bytecode debe contener SOLO caracteres hexadecimales (0-9, a-f):

```bash
python3 -c "
bytecode = '0x608060405234801561001057600080fd5b50611234...'
valid_chars = set('0123456789abcdefABCDEF')
is_valid = all(c in valid_chars for c in bytecode[2:])
print(f'Solo hex: {is_valid}')
"
```

---

## Problemas Comunes

### Problema: "Compilation Details no aparece"
**Solución:** En Remix, asegúrate que:
1. El contrato compiló correctamente (verde ✅)
2. Haz clic en el nombre del contrato en "Solidity Compiler"
3. Luego haz clic en "Compilation Details"

### Problema: "No encuentro 'Object' en Compilation Details"
**Solución:** 
1. Busca case-sensitive: `"bytecode"` (minúscula)
2. O busca: `"Object"` (mayúscula)
3. Ambas son sinónimos en diferentes versiones

### Problema: "El bytecode es muy corto"
**Solución:** Probablemente copiaste solo parte. Copia desde `60` hasta el último carácter hex.

### Problema: "El archivo es muy grande para Remix"
**Solución:** Usa Hardhat en tu máquina local:
```bash
npm install hardhat @openzeppelin/contracts
npx hardhat compile
```

---

## Archivo de Referencia: Estructura del JSON de Remix

Cuando abres "Compilation Details" en Remix, verás algo como:

```json
{
  "Object": "608060405234801561001057600080fd5b50...",
  "OpcodeList": "PUSH1 0x80 PUSH1 0x40 MSTORE...",
  "SourceMap": "123:456:0:-:0;...",
  "SwarmSource": "bzzr1://..."
}
```

Lo que necesitas es el valor de **"Object"** (sin las comillas).

---

## Próximos Pasos

Una vez tengas el bytecode:

1. **Agrégalo a `deploy_final.py`**
   ```python
   PAYMENT_PROCESSOR_BYTECODE = "0x..." # tu bytecode
   ```

2. **Ejecuta el deployment**
   ```bash
   python3 deployment/deploy_final.py --update-env
   ```

3. **Verifica en Scrollscan**
   - Abre https://sepolia.scrollscan.com
   - Busca la dirección del contrato
   - Deberías ver "Contract" badge

4. **Prueba el API**
   ```bash
   curl -X POST http://localhost:8000/payments/create \
     -H "Content-Type: application/json" \
     -d '{"amount": 1.0, "stablecoin": "USDC", "recipient_address": "0x..."}'
   ```

---

## 📚 Referencia Rápida

| Tarea | Comando |
|------|---------|
| Compilar en Remix | https://remix.ethereum.org |
| Ver bytecode | "Compilation Details" → "Object" |
| Desplegar automáticamente | `python3 deployment/deploy_final.py --update-env` |
| Desplegar manualmente | Remix → Deploy & Run → Deploy (con MetaMask inyectado) |
| Verificar deployment | https://sepolia.scrollscan.com/address/0x... |
| Compilar localmente | `npx hardhat compile` |
