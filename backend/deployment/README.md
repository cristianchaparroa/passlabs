# 🚀 Deployment - FASE 6

Documentación completa para deployment del Smart Contract PaymentProcessor en Scroll Sepolia.

## 📋 Contenido

- `deploy_contract.py` - Script principal de deployment
- `verify_on_scrollscan.py` - Verificación de contrato en Scrollscan
- `test_on_testnet.py` - Testing del contrato en testnet
- `README.md` - Esta documentación

## 🎯 Objetivo

Desplegar el Smart Contract PaymentProcessor en Scroll Sepolia Testnet de forma segura y verificable.

## ✅ Pre-requisitos

### 1. Clave Privada
```bash
# En .env debe estar configurada:
PRIVATE_KEY=0x... (64 caracteres hex)
```

### 2. Fondos en Testnet
- Mínimo 0.01 ETH en Scroll Sepolia
- Obtener en: https://scroll.io/sepolia/faucet

### 3. Variables de Entorno
```bash
# En backend/.env:
PRIVATE_KEY=0x...
RPC_URL=https://sepolia-rpc.scroll.io/
NETWORK_ID=534351
CONTRACT_ADDRESS=0x... (actualizado tras deployment)
```

### 4. Dependencias Instaladas
```bash
cd backend
pip install -r requirements.txt
```

## 🚀 Deployment Paso a Paso

### Paso 1: Verificar Requisitos
```bash
python deployment/deploy_contract.py --check-requirements
```

**Salida esperada:**
- ✅ Conectado a Scroll Sepolia
- ✅ Balance suficiente
- ✅ Archivos compilados disponibles

### Paso 2: Compilar Contrato (Si es necesario)

Si no tienes el ABI compilado, necesitas compilar con Hardhat primero:

```bash
# Ir a carpeta contracts (si existe hardhat.config.js)
cd contracts
npx hardhat compile

# El ABI se guardará en artifacts/contracts/PaymentProcessor.sol/PaymentProcessor.json
```

### Paso 3: Desplegar Contrato

**Sin actualizar .env:**
```bash
python deployment/deploy_contract.py
```

**Actualizar .env automáticamente:**
```bash
python deployment/deploy_contract.py --update-env
```

**Salida esperada:**
```
✅ DEPLOYMENT COMPLETADO EXITOSAMENTE
Contrato: 0x... (nueva dirección)
Bloque: 12345
URL: https://scrollscan.com/address/0x...
```

### Paso 4: Verificar en Scrollscan

**Opción A: Verificación Manual**
```bash
python deployment/verify_on_scrollscan.py --guide
```

Seguir los pasos manuales en Scrollscan:
1. Ir a https://scrollscan.com/address/{CONTRACT_ADDRESS}
2. Click en "Verify Contract"
3. Ingresar código fuente
4. Enviar para verificación

**Opción B: Ver Información de Verificación**
```bash
python deployment/verify_on_scrollscan.py --json-output report.json
```

### Paso 5: Testing en Testnet

```bash
python deployment/test_on_testnet.py
```

**Tests que se ejecutan:**
- ✅ Conectividad con blockchain
- ✅ Existencia del contrato
- ✅ Funciones disponibles
- ✅ Soporte de tokens
- ✅ Simulación de transacciones
- ✅ Integración blockchain

## 📊 Scripts Disponibles

### 1. deploy_contract.py

**Descripción:** Despliega el contrato PaymentProcessor en Scroll Sepolia

**Uso:**
```bash
# Deployment básico
python deployment/deploy_contract.py

# Con actualización automática de .env
python deployment/deploy_contract.py --update-env

# Solo verificar requisitos
python deployment/deploy_contract.py --check-requirements

# Verificar contrato existente
python deployment/deploy_contract.py --verify-only
```

**Funciones:**
- Verifica requisitos previos
- Compila el contrato
- Despliega en Scroll Sepolia
- Actualiza contract_addresses.json
- Actualiza .env (opcional)
- Genera reporte de deployment

### 2. verify_on_scrollscan.py

**Descripción:** Gestiona verificación del contrato en Scrollscan

**Uso:**
```bash
# Mostrar información de verificación
python deployment/verify_on_scrollscan.py

# Mostrar guía detallada
python deployment/verify_on_scrollscan.py --guide

# Generar reporte JSON
python deployment/verify_on_scrollscan.py --json-output report.json

# Obtener estado de verificación
python deployment/verify_on_scrollscan.py --get-verification-status

# Especificar contrato
python deployment/verify_on_scrollscan.py --contract-address 0x...
```

**Funciones:**
- Genera guía de verificación manual
- Prepara datos de verificación
- Crea reportes en JSON
- Proporciona enlaces a Scrollscan

### 3. test_on_testnet.py

**Descripción:** Ejecuta tests del contrato en testnet

**Uso:**
```bash
# Todos los tests
python deployment/test_on_testnet.py

# Modo rápido
python deployment/test_on_testnet.py --quick

# Modo completo
python deployment/test_on_testnet.py --full

# Solo tests de pagos
python deployment/test_on_testnet.py --test-payments

# Solo tests administrativos
python deployment/test_on_testnet.py --test-admin
```

**Tests incluidos:**
1. Conectividad con Blockchain
2. Existencia del Contrato
3. Funciones del Contrato
4. Soporte de Tokens
5. Simulación de Transacciones
6. Integración con Blockchain

## 📁 Estructura de Archivos

```
deployment/
├── README.md                    # Esta documentación
├── deploy_contract.py          # Script de deployment
├── verify_on_scrollscan.py      # Verificación en Scrollscan
├── test_on_testnet.py           # Testing en testnet
└── testnet_report_*.txt         # Reportes generados (auto)
```

## 🔍 Troubleshooting

### Error: "Invalid PRIVATE_KEY"
```bash
# Solución: Verificar que PRIVATE_KEY está en .env y es válida
PRIVATE_KEY=0x... (sin comillas, 66 caracteres)
```

### Error: "Connection refused"
```bash
# Solución: Verificar RPC_URL
RPC_URL=https://sepolia-rpc.scroll.io/

# O usar RPC alternativo:
RPC_URL=https://alpha-rpc.scroll.io/
```

### Error: "Insufficient balance"
```bash
# Solución: Obtener más ETH de testnet
# https://scroll.io/sepolia/faucet

# Verificar balance:
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('https://sepolia-rpc.scroll.io/')); print(Web3.from_wei(w3.eth.get_balance('0x...'), 'ether'))"
```

### Error: "Contract not found at address"
```bash
# Solución: El contrato podría no estar deployado aún
# Esperar 1-2 minutos después del deployment
# Verificar la dirección en contract_addresses.json
```

## 📊 Reportes Generados

### contract_addresses.json
```json
{
  "scroll_sepolia": {
    "payment_processor": "0x...",
    "usdc": "0x...",
    "usdt": "0x...",
    "dai": "0x...",
    "deployment_block": 12345,
    "deployment_date": "2024-01-01T12:00:00"
  }
}
```

### testnet_report_*.txt
Reporte de testing con:
- Resultados de conectividad
- Estado del contrato
- Información de gas
- Detalles de transacciones

## 🔗 Enlaces Útiles

- **Scroll Sepolia Faucet:** https://scroll.io/sepolia/faucet
- **Scrollscan Explorer:** https://scrollscan.com/
- **Scroll Docs:** https://docs.scroll.io/
- **Scroll RPC:** https://sepolia-rpc.scroll.io/

## 📝 Checklist de Deployment

- [ ] Variables de entorno configuradas (.env)
- [ ] Saldo suficiente en testnet (0.01+ ETH)
- [ ] Contrato compilado (ABI disponible)
- [ ] Verificar requisitos: `python deployment/deploy_contract.py --check-requirements`
- [ ] Ejecutar deployment: `python deployment/deploy_contract.py --update-env`
- [ ] Esperar confirmación (1-2 minutos)
- [ ] Verificar en Scrollscan: `python deployment/verify_on_scrollscan.py --guide`
- [ ] Testing en testnet: `python deployment/test_on_testnet.py`
- [ ] Verificar en Scrollscan manualmente
- [ ] Actualizar documentación con nueva dirección
- [ ] Listo para integración frontend

## 🎓 Próximos Pasos Después de Deployment

1. **Verificación en Scrollscan**
   - Ir a https://scrollscan.com/address/{CONTRACT_ADDRESS}
   - Verificar código fuente (opcional pero recomendado)

2. **Testing de Integración**
   ```bash
   cd backend
   python -m pytest tests/ -v
   ```

3. **Testing Manual de Endpoints**
   ```bash
   # Crear pago
   curl -X POST "http://localhost:8000/payments/create" \
     -H "Content-Type: application/json" \
     -d '{
       "recipient_address": "0x...",
       "amount": 100,
       "stablecoin": "USDC"
     }'
   ```

4. **Monitoreo**
   - Verificar logs: `tail -f logs/app.log`
   - Monitorear transacciones en Scrollscan

## 📞 Soporte

Si encuentras problemas:

1. Verificar logs: `backend/logs/app.log`
2. Revisar sección Troubleshooting
3. Verificar configuración en `.env`
4. Ejecutar verificación de requisitos

## 📄 Licencia

MIT - Ver LICENSE en raíz del proyecto

---

**Última actualización:** 2024-01-01
**Estado:** Listo para Deployment ✅