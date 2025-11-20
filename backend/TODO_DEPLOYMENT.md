# 🎯 TODO: Despliegue del Contrato PaymentProcessor en Scroll Sepolia

## 📊 Estado Actual

```
✅ Configuración: 85% completa
✅ Backend API: Funcional
✅ Smart Contract: Código listo (PaymentProcessor.sol)
✅ ABI: Generado (contract_abi.json)
✅ Token Addresses: Configuradas en config.py
❌ Contrato Desplegado: NO (falta bytecode)
❌ Sistema de Pagos: Bloqueado (esperando deployment)
```

---

## 🔴 Problema Actual

```
ERROR: Could not transact with/call contract function
CAUSA: CONTRACT_ADDRESS está vacío - el contrato no ha sido desplegado
```

---

## ✅ CHECKLIST DE DEPLOYMENT (5 PASOS)

### PASO 1: Compilar el Contrato
- [ ] Ir a https://remix.ethereum.org
- [ ] Crear archivo `PaymentProcessor.sol`
- [ ] Copiar contenido de `backend/contracts/PaymentProcessor.sol`
- [ ] Haz click en "Solidity Compiler"
- [ ] Selecciona versión 0.8.0
- [ ] Click "Compile PaymentProcessor.sol"
- [ ] Espera checkmark ✅ verde

**Tiempo estimado:** 2 minutos

---

### PASO 2: Obtener el Bytecode
- [ ] En Remix, click en "Compilation Details"
- [ ] Busca la sección "Object"
- [ ] Copia TODO el código hex (será muy largo)
- [ ] Guarda en un archivo temporal o portapapeles

**Validación:**
- [ ] Comienza con `0x` o `608060...`
- [ ] Solo contiene 0-9 y a-f
- [ ] Tiene más de 1000 caracteres
- [ ] No tiene espacios

**Tiempo estimado:** 2 minutos

---

### PASO 3: Actualizar deploy_final.py
- [ ] Abre `backend/deployment/deploy_final.py`
- [ ] Busca línea: `PAYMENT_PROCESSOR_BYTECODE = None`
- [ ] Reemplaza `None` con tu bytecode:
  ```python
  PAYMENT_PROCESSOR_BYTECODE = "0x608060405234801561001057600080fd5b50..."
  ```
- [ ] Incluye prefijo `0x`
- [ ] Usa comillas dobles
- [ ] Guarda el archivo

**Tiempo estimado:** 2 minutos

---

### PASO 4: Ejecutar Deployment
```bash
cd passlabs/backend
python3 deployment/deploy_final.py --update-env
```

- [ ] Script ejecuta sin errores
- [ ] Muestra: "✅ Contrato deployado en: 0x..."
- [ ] Archivo .env se actualiza automáticamente
- [ ] CONTRACT_ADDRESS ya no está vacío

**Tiempo estimado:** 1 minuto (+ espera blockchain ~30-60s)

---

### PASO 5: Verificar Deployment
```bash
# Local
cd passlabs/backend
python3 deploy_check.py
```

- [ ] Todos los checks pasan con ✅
- [ ] Específicamente: CONTRACT_ADDRESS está configurada

**En blockchain:**
- [ ] Abre https://sepolia.scrollscan.com
- [ ] Busca tu CONTRACT_ADDRESS
- [ ] Verifica que aparece "Contract" badge

**Tiempo estimado:** 2 minutos

---

## 🚀 DESPUÉS DEL DEPLOYMENT

### Paso 6: Reiniciar API y Probar
```bash
# Terminal 1
cd passlabs/backend
python3 main.py

# Terminal 2 (cuando veas "Application startup complete")
curl -X POST http://localhost:8000/payments/create \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1.0,
    "stablecoin": "USDC",
    "recipient_address": "0xa92d504731aa3e99df20ffd200ed03f9a55a6219"
  }'
```

**Respuesta esperada:**
```json
{
  "payment_id": "0xabc123...",
  "amount": 1.0,
  "stablecoin": "USDC",
  "status": "pending"
}
```

- [ ] No hay error 400 Bad Request
- [ ] Respuesta es 200 OK
- [ ] Contiene payment_id válido
- [ ] Status es "pending"

---

## 📋 PRE-REQUISITOS PARA DEPLOYMENT

Verifica antes de comenzar:

```bash
cd passlabs/backend

# 1. Verifica que tienes clave privada
echo $PRIVATE_KEY  # Debe mostrar 0x...

# 2. Verifica balance en wallet
python3 -c "
from web3 import Web3
from config import settings
w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
account = w3.eth.account.from_key(settings.PRIVATE_KEY)
balance = w3.eth.get_balance(account.address)
print(f'Balance: {w3.from_wei(balance, \"ether\")} ETH')
"

# 3. Si balance es 0, obtén testnet ETH:
# https://scroll.io/sepolia/faucet
```

- [ ] PRIVATE_KEY configurada (no vacía)
- [ ] Balance > 0.001 ETH en Scroll Sepolia
- [ ] RPC_URL = https://sepolia-rpc.scroll.io/
- [ ] CHAIN_ID = 534351

---

## 🆘 TROUBLESHOOTING

### Problema: "BYTECODE no configurado"
**Solución:**
1. Vuelve a Paso 2
2. Verifica que copiaste TODO el "Object" desde Compilation Details
3. No debe estar vacío ni tener solo "0x"

### Problema: "Insufficient funds"
**Solución:**
1. Necesitas ETH en Scroll Sepolia
2. Ve a https://scroll.io/sepolia/faucet
3. Pega tu wallet address
4. Obtén 0.5 ETH
5. Espera 2-3 minutos a que llegue
6. Intenta deployment de nuevo

### Problema: "No conectado a RPC"
**Solución:**
```bash
# Verifica RPC en .env
grep RPC_URL backend/.env
# Debe ser: https://sepolia-rpc.scroll.io/

# Si no está, agrégalo
echo "RPC_URL=https://sepolia-rpc.scroll.io/" >> backend/.env
```

### Problema: "Contract deployed correctly and chain synced?"
**Solución:**
1. El contrato no se desplegó correctamente
2. Verifica que no hay errores en el script
3. Espera 30 segundos
4. Verifica en Scrollscan que existe: https://sepolia.scrollscan.com/address/0x...
5. Si no existe, intenta deployment de nuevo

### Problema: "Token not allowed in contract"
**Solución:**
El contrato necesita autorizar los tokens. Después de deployment:
```bash
cd passlabs/backend
python3 -c "
from services.blockchain_service import BlockchainService
from config import settings

bc = BlockchainService()
bc.add_allowed_token(settings.USDC_ADDRESS)
bc.add_allowed_token(settings.USDT_ADDRESS)
bc.add_allowed_token(settings.DAI_ADDRESS)
print('✅ Tokens autorizados')
"
```

---

## 📊 TABLA DE PROGRESO

| Componente | Estado | Acción |
|-----------|--------|--------|
| Contrato Solidity | ✅ Listo | Usar PaymentProcessor.sol |
| ABI del Contrato | ✅ Generado | En contract_abi.json |
| Configuración .env | ✅ Casi completa | Falta agregar bytecode |
| Token Addresses | ✅ Configuradas | En config.py |
| Bytecode Compilado | ⏳ PENDIENTE | Compilar en Remix |
| Deployment | ⏳ PENDIENTE | Ejecutar deploy_final.py |
| Verificación | ⏳ PENDIENTE | Verificar en Scrollscan |
| API Test | ⏳ PENDIENTE | Probar /payments/create |

---

## 🎯 TIMELINE ESTIMADO

| Paso | Tiempo | Acción |
|------|--------|--------|
| 1. Compilar en Remix | 2 min | Ir a remix.ethereum.org |
| 2. Obtener bytecode | 2 min | Copiar desde Compilation Details |
| 3. Actualizar script | 2 min | Editar deploy_final.py |
| 4. Ejecutar deployment | 1 min + espera | Correr script (espera blockchain) |
| 5. Verificar | 2 min | deploy_check.py + Scrollscan |
| 6. Probar API | 3 min | Curl al endpoint |
| **TOTAL** | **~20 min** | **¡Listo para producción!** |

---

## 🔗 REFERENCIAS ÚTILES

### Herramientas Necesarias
- **Remix IDE:** https://remix.ethereum.org
- **Scroll Sepolia Faucet:** https://scroll.io/sepolia/faucet
- **Scrollscan Explorer:** https://sepolia.scrollscan.com

### Documentación
- **Guía Completa:** `deployment/guides/COMPILATION_AND_DEPLOYMENT.md`
- **Bytecode Guide:** `deployment/bytecode/BYTECODE_GUIDE.md`
- **Quick Start:** `QUICK_START_DEPLOYMENT.md`

### Scripts Útiles
- **Deploy:** `deployment/deploy_final.py`
- **Extract Bytecode:** `deployment/extract_bytecode.py`
- **Verify:** `deploy_check.py`

---

## 📝 NOTAS IMPORTANTES

1. **Bytecode es único por compilación**
   - Si recompilamos, cambia el bytecode
   - Guardarlo es importante

2. **Gas es muy barato en Scroll Sepolia**
   - ~0.0157 Gwei
   - Deployment: ~200k-500k gas
   - Costo: < $0.001 USD

3. **El contrato es inmutable**
   - Una vez desplegado, la dirección es final
   - Guarda CONTRACT_ADDRESS en lugar seguro

4. **Testnet es para testing**
   - Los tokens y ETH no tienen valor real
   - Useful para verificar que todo funciona

5. **Próximo paso: Mainnet**
   - Cuando todo esté probado en testnet
   - Usar Scroll mainnet (RPC diferente)
   - Usar ETH y tokens reales

---

## ✨ SIGUIENTE FASE

Una vez deployment esté completo:

- [ ] Verificar todas las funciones del API
- [ ] Testing de pagos con diferentes stablecoins
- [ ] Documentar dirección del contrato
- [ ] Guardar estado en DEPLOYMENT_STATUS.md
- [ ] Preparar para mainnet

---

## 🎉 CUANDO TODO ESTÉ LISTO

Tu sistema tendrá:
✅ Smart Contract desplegado en Scroll Sepolia
✅ API funcional para crear pagos
✅ Validación de tokens en blockchain
✅ Transacciones procesadas exitosamente
✅ Sistema listo para producción

**¡Felicidades! El 90% del trabajo estará completado.**

---

**Última actualización:** 2025-11-20
**Estado:** En progreso - Esperando bytecode y deployment
**Próximo paso:** Compilar en Remix y obtener bytecode