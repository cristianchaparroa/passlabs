# 🚀 Crypto Payments API (MVP - Hackathon)

Sistema de pagos con criptomonedas utilizando Smart Contracts en Scroll Sepolia y una API en Python FastAPI.

## 📋 Descripción

Esta es una API que permite:
- ✅ Crear pagos en stablecoins (USDC, USDT, DAI)
- ✅ Verificar estado de transacciones en blockchain
- ✅ Obtener precios actualizados de stablecoins desde DeFiLlama
- ✅ Interactuar con Scroll Sepolia Testnet
- ✅ Smart Contract seguro con protecciones ReentrancyGuard

## 🛠️ Requisitos Previos

- Python 3.11+
- pip (administrador de paquetes de Python)
- Node.js 16+ y npm (para compilar Smart Contract)
- Una cuenta con ETH en Scroll Sepolia Testnet
- Una clave privada (PRIVATE_KEY) para firmar transacciones

## 📦 Instalación

### 1. Clonar el repositorio
```bash
cd passlabs/backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual

**En macOS/Linux:**
```bash
source venv/bin/activate
```

**En Windows:**
```bash
venv\Scripts\activate
```

### 4. Instalar dependencias de Python
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
```bash
cp .env.example .env
```

Edita `.env` y completa los valores:
```
PRIVATE_KEY=tu_clave_privada_aqui
CONTRACT_ADDRESS=0x... (se obtiene al deployar el contrato)
USDC_ADDRESS=0x...
USDT_ADDRESS=0x...
DAI_ADDRESS=0x...
```

### 6. (Opcional) Compilar y desplegar Smart Contract

```bash
cd contracts
npm install
npm install -g hardhat
npx hardhat compile
npx hardhat run scripts/deploy.js --network scroll-sepolia
```

## 🚀 Ejecución

### Iniciar la API
```bash
python main.py
```

O con uvicorn directamente:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`

## 📚 Documentación de API

Una vez que la API esté corriendo, accede a:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔌 Endpoints Principales

### 1. Health Check
```
GET /health

Response:
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00Z",
  "service": "Crypto Payments API"
}
```

### 2. Crear Pago
```
POST /payments/create

Body:
{
  "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
  "amount": 100.50,
  "stablecoin": "USDC",
  "description": "Pago de servicios"
}

Response:
{
  "success": true,
  "message": "Pago creado exitosamente",
  "data": {
    "payment_id": "uuid-xxxxx",
    "tx_hash": "0x...",
    "recipient": "0x...",
    "amount": 100.50,
    "stablecoin": "USDC",
    "status": "pending"
  }
}
```

### 3. Verificar Estado de Pago
```
GET /payments/status/{tx_hash}

Response:
{
  "success": true,
  "data": {
    "tx_hash": "0x...",
    "status": "pending",
    "confirmations": 0,
    "block_number": null
  }
}
```

### 4. Obtener Precios de Stablecoins
```
GET /stablecoins/prices

Response:
{
  "success": true,
  "data": {
    "stablecoins": [
      {
        "name": "USDC",
        "symbol": "USDC",
        "price_usd": 1.00,
        "market_cap": "33000000000",
        "change_24h": 0.01
      },
      ...
    ]
  },
  "last_updated": "2024-01-01T12:00:00Z"
}
```

## 🏗️ Estructura del Proyecto

```
backend/
├── README.md                    # Este archivo
├── PLAN.md                      # Plan de desarrollo y arquitectura
├── requirements.txt             # Dependencias Python
├── .env                         # Variables de entorno (no commitear)
├── .env.example                 # Ejemplo de .env
├── .gitignore
├── main.py                      # Entrada de la aplicación
├── config.py                    # Configuración global
│
├── contracts/
│   ├── PaymentProcessor.sol     # Smart Contract
│   ├── contract_abi.json        # ABI del contrato
│   ├── contract_addresses.json  # Direcciones deployadas
│   ├── hardhat.config.js        # Configuración Hardhat
│   ├── package.json             # Dependencias Node.js
│   ├── scripts/
│   │   ├── deploy.js            # Script de deployment
│   │   └── addTokens.js         # Script para agregar tokens
│   └── test/
│       └── PaymentProcessor.test.js  # Tests del contrato
│
├── services/
│   ├── __init__.py
│   ├── blockchain_service.py    # Interacción con Web3
│   ├── payment_service.py       # Lógica de pagos
│   └── defi_llama_service.py    # API de precios
│
├── models/
│   ├── __init__.py
│   ├── payment.py               # Modelos de pagos
│   └── stablecoin.py            # Modelos de stablecoins
│
├── routes/
│   ├── __init__.py
│   ├── payments.py              # Endpoints de pagos
│   └── stablecoins.py           # Endpoints de precios
│
└── utils/
    ├── __init__.py
    ├── logger.py                # Sistema de logging
    ├── validators.py            # Funciones de validación
    └── constants.py             # Constantes de la app
```

## 🔗 Blockchain Setup

### Scroll Sepolia Testnet

- **RPC URL:** `https://sepolia-rpc.scroll.io/`
- **Chain ID:** `534351`
- **Faucet ETH:** https://sepolia.scroll.io/bridge
- **Block Explorer:** https://sepolia-blockscout.scroll.io/

### Obtener ETH de Prueba

1. Ir a https://sepolia.scroll.io/bridge
2. Conectar wallet (MetaMask)
3. Solicitar ETH de Sepolia Ethereum
4. Bridgear a Scroll Sepolia

## 📜 Smart Contract

### PaymentProcessor.sol

Contrato inteligente para procesar pagos en stablecoins con:
- ✅ Transferencia segura de tokens ERC20
- ✅ Protección contra reentrancy (ReentrancyGuard)
- ✅ Control de acceso (Ownable)
- ✅ Gestión de tokens permitidos
- ✅ Auditoría completa con eventos

**Funciones Principales:**
- `processPayment()` - Procesa pago y retiene tokens
- `processPaymentAndTransfer()` - Procesa pago y transfiere directamente
- `addAllowedToken()` - Agrega token a lista blanca
- `withdrawFunds()` - Retira fondos
- `getPaymentStatus()` - Obtiene estado de pago

**Eventos:**
- `PaymentProcessed` - Pago procesado exitosamente
- `PaymentFailed` - Fallo en el pago
- `FundsWithdrawn` - Fondos retirados
- `TokenAdded` - Token agregado
- `TokenRemoved` - Token removido

### Compilación y Deployment

```bash
# Compilar
cd contracts
npx hardhat compile

# Tests locales
npx hardhat test

# Desplegar en Scroll Sepolia
npx hardhat run scripts/deploy.js --network scroll-sepolia

# Verificar en Scrollscan
npx hardhat verify --network scroll-sepolia CONTRACT_ADDRESS
```

## 🧪 Testing

### Verificar conexión a blockchain
```python
from services.blockchain_service import blockchain_service

# Verificar conexión
if blockchain_service.is_connected():
    print("✅ Conectado a blockchain")
else:
    print("❌ Error de conexión")

# Obtener balance
balance = blockchain_service.get_balance("0xtu_direccion")
print(f"Balance: {balance} ETH")
```

### Ejecutar pruebas de setup
```bash
python test_setup.py
```

### Ejecutar tests del Smart Contract
```bash
cd contracts
npm install
npx hardhat test
```

## 📝 Logs

Los logs se guardan en:
```
backend/logs/app.log
```

También se muestran en consola durante la ejecución.

Ver logs en tiempo real:
```bash
tail -f logs/app.log
```

## 🐛 Troubleshooting

### Error: "Invalid PRIVATE_KEY"
- Verifica que tu clave privada sea válida (sin el prefijo 0x)
- Asegúrate de que esté en `.env` correctamente

### Error: "Connection refused"
- Verifica que el RPC URL sea correcto
- Intenta acceder a https://sepolia-rpc.scroll.io/

### Error: "Insufficient gas"
- Asegúrate de tener suficiente ETH en tu wallet
- Aumenta el GAS_LIMIT en config.py

### Error: "Token no permitido"
- El token no está en la lista blanca del contrato
- Primero agregar el token con `addAllowedToken()`

### Error: "Insufficient funds for gas" (Deployment)
- Obtener más ETH de prueba desde el faucet
- https://sepolia.scroll.io/bridge

### Error: "Invalid private key" (Deployment)
- Verificar PRIVATE_KEY en .env (sin prefijo 0x)
- Formato correcto: abc123... (sin 0x)

## 📊 Arquitectura del Sistema

```
┌──────────────────────┐
│   Frontend (Next.js) │
└──────────┬───────────┘
           │ HTTP/REST
           ▼
┌──────────────────────────────────┐
│   Backend (FastAPI)              │
│  ├─ Routes/API (payments, prices)│
│  ├─ Services (blockchain, DeFi)  │
│  ├─ Models (validados)           │
│  └─ Utils (logger, validators)   │
└──────────┬──────────────────────┘
           │ Web3.py
           ▼
┌──────────────────────────────────┐
│ Blockchain (Scroll Sepolia)      │
│ ├─ Smart Contract (PaymentProc.) │
│ ├─ ERC20 Tokens (USDC/USDT/DAI)  │
│ └─ Chain ID: 534351              │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────┐
│ DeFiLlama API        │
│ (Precios Stablecoins)│
└──────────────────────┘
```

## 🔐 Seguridad

### Configuración de Seguridad
- ✅ Validación de direcciones Ethereum (0x format)
- ✅ Validación de hashes de transacciones
- ✅ Validación de cantidades (0.01 - 1,000,000)
- ✅ Variables sensibles en .env (no committeadas)
- ✅ CORS configurado para desarrollo
- ✅ ReentrancyGuard en Smart Contract
- ✅ Ownable para control de acceso

### Validadores Implementados
- `is_valid_ethereum_address()` - Valida formato 0x...
- `is_valid_tx_hash()` - Valida hash de transacción
- `is_valid_amount()` - Valida rango 0.01 - 1,000,000
- `is_valid_stablecoin()` - Valida contra lista blanca

## 📈 Progreso del Proyecto

```
Fase 1: Setup Base              ✅ COMPLETADA (2 horas)
Fase 2: Smart Contract          ✅ COMPLETADA (2-3 horas)
Fase 3: Servicios Core          ⏳ PENDIENTE (3-4 horas)
Fase 4: Rutas API               ⏳ PENDIENTE (2-3 horas)
Fase 5: Testing & Polish        ⏳ PENDIENTE (1-2 horas)
Fase 6: Deployment              ⏳ PENDIENTE (1 hora)
────────────────────────────────────────────────────────
Total                           34% Completado
```

## 📋 Características Implementadas

### ✅ Backend (Python)
- FastAPI con documentación automática (Swagger, ReDoc)
- 5 Endpoints API implementados
- 6 Modelos Pydantic validados
- Sistema de logging a consola y archivo
- Configuración centralizada
- 4 Validadores funcionales

### ✅ Smart Contract (Solidity)
- 15 funciones implementadas
- 5 eventos para auditoría
- 3 modificadores de seguridad
- Protección contra reentrancy
- Control de acceso granular
- Gestión de múltiples tokens

### ✅ Documentación
- README.md completo (este archivo)
- PLAN.md con arquitectura completa
- Código documentado con docstrings
- Guías de instalación y setup

## 🚀 Próximos Pasos

### Inmediato (Fase 3)
1. [ ] Implementar blockchain_service.py
2. [ ] Implementar payment_service.py
3. [ ] Implementar defi_llama_service.py
4. [ ] Conectar servicios con rutas

### Corto Plazo (Fase 4-5)
5. [ ] Conectar rutas a servicios
6. [ ] Testing completo
7. [ ] Manejo de errores robusto
8. [ ] Pruebas en Scroll Sepolia

### Mediano Plazo (Fase 6)
9. [ ] Deployment en testnet
10. [ ] Verificación en Scrollscan
11. [ ] Testing end-to-end
12. [ ] Documentación final

## 📞 Comandos Útiles

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pruebas
python test_setup.py

# Iniciar API
python main.py

# Ver documentación API
open http://localhost:8000/docs

# Ver logs en tiempo real
tail -f logs/app.log

# Buscar palabra en logs
grep "error" logs/app.log

# Compilar Smart Contract
cd contracts && npx hardhat compile

# Ejecutar tests del contrato
cd contracts && npx hardhat test

# Desplegar contrato
cd contracts && npx hardhat run scripts/deploy.js --network scroll-sepolia
```

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [Scroll Docs](https://docs.scroll.io/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Hardhat Documentation](https://hardhat.org/docs)

## 🎯 Contacto y Soporte

Para preguntas o problemas, revisa:
1. Este README.md
2. PLAN.md para arquitectura detallada
3. Documentación API en `/docs`
4. Logs en `logs/app.log`

## 📄 Licencia

MIT License

## 👨‍💻 Autor

Desarrollado para Hackathon - Sistema de Pagos con Criptomonedas