# 🚀 Crypto Payments API (MVP - Hackathon) - v0.4.0

Sistema de pagos con criptomonedas utilizando Smart Contracts en Scroll Sepolia y una API en Python FastAPI.

## 📋 Descripción

Esta es una API completa que permite:
- ✅ Crear pagos en stablecoins (USDC, USDT, DAI)
- ✅ Verificar estado de transacciones en blockchain
- ✅ Obtener precios actualizados de stablecoins desde DeFiLlama
- ✅ Interactuar con Scroll Sepolia Testnet
- ✅ Smart Contract seguro con protecciones ReentrancyGuard
- ✅ 9 Endpoints API totalmente funcionales
- ✅ Servicios Core integrados y operacionales
- ✅ Logging detallado y manejo de errores robusto

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

**La API se inicializará y verificará automáticamente:**
- ✅ Conexión a blockchain (Scroll Sepolia)
- ✅ Carga del Smart Contract
- ✅ Inicialización de servicios
- ✅ Obtención de precios iniciales de stablecoins

## ⚡ Inicio Rápido

### 1. Verificar que la API está corriendo
```bash
curl http://localhost:8000/health
```

### 2. Ver listado de endpoints
```bash
curl http://localhost:8000/
```

### 3. Obtener precios de stablecoins
```bash
curl http://localhost:8000/stablecoins/prices
```

### 4. Crear un pago
```bash
curl -X POST http://localhost:8000/payments/create \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
    "amount": 100.50,
    "stablecoin": "USDC"
  }'
```

### 5. Acceder a la documentación interactiva
```
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
```

## 📚 Documentación de API

Una vez que la API esté corriendo, accede a:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔌 Endpoints Principales

### Health & Status
```
GET /health - Verificar que la API está en línea
GET / - Información de la API y listado de endpoints
GET /status - Estado detallado de servicios
```

### Payments API (5 Endpoints)
```
POST /payments/create
Crear un nuevo pago en blockchain

Body:
{
  "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
  "amount": 100.50,
  "stablecoin": "USDC",
  "description": "Pago de servicios"
}

Response (201 Created):
{
  "success": true,
  "message": "Payment created successfully",
  "data": {
    "payment_id": "uuid-xxxxx",
    "tx_hash": "0x...",
    "recipient": "0x...",
    "amount": 100.50,
    "stablecoin": "USDC",
    "status": "pending",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

```
GET /payments/status/{tx_hash}
Obtener estado de una transacción

Response:
{
  "success": true,
  "data": {
    "payment_id": "uuid-xxxxx",
    "tx_hash": "0x...",
    "status": "pending",
    "confirmations": 0,
    "block_number": null
  }
}
```

```
GET /payments/by-id/{payment_id}
Obtener información de un pago por ID

GET /payments/all
Obtener lista de todos los pagos

GET /payments/by-status/{status}
Filtrar pagos por estado (pending, completed, failed, success)
```

### Stablecoins API (4 Endpoints)
```
GET /stablecoins/prices
Obtener precios actualizados de stablecoins

Response:
{
  "success": true,
  "data": {
    "stablecoins": [
      {
        "name": "USD Coin",
        "symbol": "USDC",
        "price_usd": 1.00,
        "market_cap": "33000000000",
        "change_24h": 0.01
      },
      ...
    ],
    "count": 3
  },
  "last_updated": "2024-01-01T12:00:00Z"
}
```

```
GET /stablecoins/prices/{symbol}
Obtener precio de un stablecoin específico

GET /stablecoins/cache-info
Obtener información del caché de precios

POST /stablecoins/cache-clear
Limpiar caché para forzar actualización
```

## 🏗️ Estructura del Proyecto

```
backend/
├── README.md                    # Este archivo
├── PLAN.md                      # Plan de desarrollo y arquitectura
├── FASE_3_SUMMARY.md            # Resumen de Fase 3 (Servicios Core)
├── requirements.txt             # Dependencias Python
├── .env                         # Variables de entorno (no commitear)
├── .env.example                 # Ejemplo de .env
├── .gitignore
├── main.py                      # Entrada de la aplicación (v0.4.0)
├── config.py                    # Configuración global
│
├── contracts/
│   ├── PaymentProcessor.sol     # Smart Contract ✅
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
│   ├── blockchain_service.py    # Interacción con Web3 ✅ (16 métodos)
│   ├── payment_service.py       # Lógica de pagos ✅ (14 métodos)
│   └── defi_llama_service.py    # API de precios ✅ (15 métodos)
│
├── models/
│   ├── __init__.py
│   ├── payment.py               # Modelos de pagos ✅
│   └── stablecoin.py            # Modelos de stablecoins ✅
│
├── routes/
│   ├── __init__.py
│   ├── payments.py              # Endpoints de pagos ✅ (5 endpoints)
│   └── stablecoins.py           # Endpoints de precios ✅ (4 endpoints)
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Sistema de logging ✅
│   ├── validators.py            # Funciones de validación ✅
│   └── constants.py             # Constantes de la app ✅
│
└── logs/
    └── app.log                  # Logs de la aplicación
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

### 1. Verificar Conexión a Blockchain
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

### 2. Ejecutar Pruebas de Setup
```bash
python test_setup.py
```

### 3. Ejecutar Tests del Smart Contract
```bash
cd contracts
npm install
npx hardhat test
```

### 4. Testing de la API - Endpoints de Pagos

#### Crear un Pago
```bash
curl -X POST "http://localhost:8000/payments/create" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
    "amount": 100.50,
    "stablecoin": "USDC",
    "description": "Pago de prueba"
  }'
```

#### Obtener Estado de Pago
```bash
# Por tx_hash
curl "http://localhost:8000/payments/status/0xabc123def456..."

# Por payment_id
curl "http://localhost:8000/payments/by-id/123e4567-e89b-12d3-a456-426614174000"

# Todos los pagos
curl "http://localhost:8000/payments/all"

# Filtrar por estado
curl "http://localhost:8000/payments/by-status/pending"
```

### 5. Testing de la API - Endpoints de Precios

#### Obtener Todos los Precios
```bash
curl "http://localhost:8000/stablecoins/prices"
```

#### Obtener Precio Específico
```bash
curl "http://localhost:8000/stablecoins/prices/USDC"
curl "http://localhost:8000/stablecoins/prices/USDT"
curl "http://localhost:8000/stablecoins/prices/DAI"
```

#### Información del Caché
```bash
curl "http://localhost:8000/stablecoins/cache-info"
```

#### Limpiar Caché
```bash
curl -X POST "http://localhost:8000/stablecoins/cache-clear"
```

### 6. Testing de Health Checks
```bash
# Health general
curl "http://localhost:8000/health"

# Status detallado
curl "http://localhost:8000/status"

# Información de la API
curl "http://localhost:8000/"
```

### 7. Testing en Swagger UI
```
1. Ir a http://localhost:8000/docs
2. Expandir endpoints
3. Hacer clic en "Try it out"
4. Completar parámetros requeridos
5. Hacer clic en "Execute"
```

### 8. Ejecución de Tests Automatizados (FASE 5)

#### Instalar dependencias de testing
```bash
pip install -r requirements.txt  # Incluye pytest y dependencias
```

#### Ejecutar todos los tests
```bash
python run_tests.py
```

#### Ejecutar tests específicos
```bash
# Solo tests de pagos
python run_tests.py payments

# Solo tests de stablecoins
python run_tests.py stablecoins

# Solo tests de servicios
python run_tests.py services

# Con salida detallada
python run_tests.py --verbose

# Con reporte de cobertura
python run_tests.py --coverage
```

#### Ejecutar con pytest directamente
```bash
# Todos los tests
pytest -v

# Tests específicos
pytest test_payments_routes.py -v
pytest test_stablecoins_routes.py -v
pytest test_services.py -v
pytest test_validators.py -v

# Con cobertura
pytest --cov=. --cov-report=html
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
Fase 3: Servicios Core          ✅ COMPLETADA (3-4 horas)
Fase 4: Rutas API               ✅ COMPLETADA (2-3 horas)
Fase 5: Testing & Polish        ✅ COMPLETADA (2 horas)
Fase 6: Deployment              ⏳ PENDIENTE (1 hora)
────────────────────────────────────────────────────────
Total                           85% Completado (12.5-15 horas de 13-17)
```

## 📋 Características Implementadas

### ✅ Backend (Python) - v0.5.0
- FastAPI con documentación automática (Swagger, ReDoc)
- 9 Endpoints API implementados y testeados
- 6 Modelos Pydantic validados
- Sistema de logging a consola y archivo
- Configuración centralizada
- 4 Validadores funcionales
- Exception handlers globales (400, 404, 500, 503)
- Middleware CORS configurado
- 86 tests unitarios e integración (FASE 5)
- pytest configurado con cobertura

### ✅ Smart Contract (Solidity)
- 15 funciones implementadas
- 5 eventos para auditoría
- 3 modificadores de seguridad
- Protección contra reentrancy
- Control de acceso granular
- Gestión de múltiples tokens

### ✅ Servicios Core (Fase 3)
- blockchain_service.py: 16 métodos implementados
- payment_service.py: 14 métodos implementados
- defi_llama_service.py: 15 métodos implementados
- Cache de precios con refresh automático
- Validaciones completas de inputs
- Logging detallado de operaciones

### ✅ Rutas API (Fase 4)
- **Payments (5 endpoints):**
  - POST /payments/create
  - GET /payments/status/{tx_hash}
  - GET /payments/by-id/{payment_id}
  - GET /payments/all
  - GET /payments/by-status/{status}
- **Stablecoins (4 endpoints):**
  - GET /stablecoins/prices
  - GET /stablecoins/prices/{symbol}
  - GET /stablecoins/cache-info
  - POST /stablecoins/cache-clear

### ✅ Documentación
- README.md completo (este archivo)
- PLAN.md con arquitectura completa
- FASE_3_SUMMARY.md con detalles de servicios
- Código documentado con docstrings
- Guías de instalación y setup
- API Documentation en Swagger UI (/docs)

## 🚀 Próximos Pasos

### Inmediato (Fase 6)
1. [ ] Compilar Smart Contract
2. [ ] Deploy en Scroll Sepolia
3. [ ] Verificar en Scrollscan
4. [ ] Testing en testnet

### Completado
✅ Setup Base (Fase 1)
✅ Smart Contract (Fase 2)
✅ Servicios Core (Fase 3)
✅ Rutas API (Fase 4)
✅ Testing & Polish (Fase 5)

### Producción
6. [ ] Deployment final
7. [ ] Monitoreo
8. [ ] Escalabilidad
9. [ ] Documentación de usuario

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