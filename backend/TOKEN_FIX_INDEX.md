# 📚 Índice: Solución del Error "Token Not Allowed in Contract"

## 🎯 Resumen Rápido

Tu sistema de pagos devuelve error porque **los tokens USDC, USDT y DAI no están agregados como "permitidos" en el Smart Contract**. La solución es ejecutar UN script que toma 2-3 minutos.

```bash
python deployment/add_allowed_tokens.py
```

---

## 📖 Documentación (Elige tu nivel)

### 🚀 Nivel 1: Ultra Rápido (1 minuto)
**Mejor para:** Ya entiendes el problema y solo quieres la solución

- 📄 **`README_TOKEN_FIX.md`** - TL;DR de 5 minutos
- 📝 Paso 1: Verifica `.env`
- 💰 Paso 2: Obtén ETH testnet
- ⚙️ Paso 3: Ejecuta el script

### 🔍 Nivel 2: Comprensión Completa (10 minutos)
**Mejor para:** Quieres entender QUÉ pasó y POR QUÉ

- 📄 **`FIX_TOKEN_ERROR.md`** - Explicación clara del problema y solución
- 📊 **`SOLUTION_FLOWCHART.md`** - Diagramas visuales del flujo
- 🔧 Comprenderás el contrato y por qué requiere "tokens permitidos"

### 📚 Nivel 3: Documentación Completa (30 minutos)
**Mejor para:** Necesitas todos los detalles, solución de problemas y referencias

- 📄 **`CONFIGURE_TOKENS.md`** - Guía exhaustiva
- 🧪 Sección de "Solución de Problemas"
- 📋 Información de referencia
- ❓ FAQ (Preguntas Frecuentes)

### 🔧 Nivel 4: Técnico/Debug (Para expertos)
**Mejor para:** Diagnóstico avanzado y troubleshooting

- 📄 **`DEPLOYMENT_STATUS.md`** - Estado completo del despliegue
- 🔐 Verificación manual de contratos
- 📊 Monitoreo en blockchain

---

## 🛠️ Scripts Disponibles

### 1. **`deployment/add_allowed_tokens.py`** ⭐ PRINCIPAL
```bash
python deployment/add_allowed_tokens.py
```
**Qué hace:**
- ✅ Valida tu configuración
- ✅ Se conecta a Scroll Sepolia
- ✅ Agrega USDC, USDT y DAI al contrato
- ✅ Espera confirmación en blockchain
- ✅ Verifica que todo funcionó

**Cuándo usarlo:** SIEMPRE - Este es el script que necesitas ejecutar

**Tiempo:** 2-3 minutos

---

### 2. **`check_tokens_status.py`** 🔍 DIAGNÓSTICO
```bash
python check_tokens_status.py
```
**Qué hace:**
- 🔍 Verifica si tu configuración es correcta
- 🔍 Chequea conexión a blockchain
- 🔍 Verifica tu balance ETH
- 🔍 Muestra estado actual de cada token
- 🔍 Da recomendaciones basadas en lo que encuentra

**Cuándo usarlo:** ANTES de ejecutar add_allowed_tokens.py (opcional pero recomendado)

**Tiempo:** 10 segundos

---

## 📋 Archivos de Documentación

```
passlabs/backend/
├── 📄 README_TOKEN_FIX.md              ← Comienza aquí (nivel 1)
├── 📄 FIX_TOKEN_ERROR.md               ← Explicación clara (nivel 2)
├── 📄 SOLUTION_FLOWCHART.md            ← Diagramas visuales (nivel 2)
├── 📄 CONFIGURE_TOKENS.md              ← Todo detallado (nivel 3)
├── 📄 TOKEN_FIX_INDEX.md               ← Este archivo
│
├── deployment/
│   ├── 🔧 add_allowed_tokens.py        ← Script PRINCIPAL
│   ├── 📋 add_tokens_results.json      ← Resultados (se genera)
│   └── ...
│
└── 🔧 check_tokens_status.py           ← Script DIAGNÓSTICO
```

---

## 🚀 Guía Rápida (Copiar y Pegar)

### Opción A: Si tienes todo configurado
```bash
cd backend
python deployment/add_allowed_tokens.py
```

### Opción B: Si quieres verificar primero
```bash
cd backend
python check_tokens_status.py
python deployment/add_allowed_tokens.py
```

### Opción C: Si necesitas obtener testnet ETH primero
```bash
# 1. Ve a: https://scroll-testnet-faucet.allthatnode.com:3001/
# 2. Ingresa tu dirección (la que está en PRIVATE_KEY)
# 3. Espera ~1 minuto
# 4. Luego ejecuta:
cd backend
python deployment/add_allowed_tokens.py
```

---

## ✅ Checklist de Verificación

Antes de ejecutar el script:

```
CONFIGURACIÓN (.env)
  □ RPC_URL = https://sepolia-rpc.scroll.io/
  □ CONTRACT_ADDRESS = 0x... (tu contrato desplegado)
  □ PRIVATE_KEY = 0x... (tu clave privada, eres el owner)
  □ USDC_ADDRESS = 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238
  □ USDT_ADDRESS = 0x186C0C26c45A8DA1Da34339ee513624a9609156d
  □ DAI_ADDRESS = 0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6

BLOCKCHAIN
  □ Tienes ~0.05 ETH en Scroll Sepolia
  □ Tu cuenta es el owner del contrato

LISTO PARA EJECUTAR
  □ Te encuentras en la carpeta: backend/
  □ Ejecutas: python deployment/add_allowed_tokens.py
  □ Esperas confirmación (2-3 minutos)
  □ Ves "✅ ÉXITO" al final
```

---

## 📊 Qué Cambia Después

### ANTES (Error)
```
POST /payments/create
  → Validación ✅
  → Consulta contrato ❌
  → ERROR 400: "Token not allowed"
```

### DESPUÉS (Funciona)
```
POST /payments/create
  → Validación ✅
  → Consulta contrato ✅
  → Pago creado exitosamente ✅
```

---

## 🎓 Aprende Más

### Documentos por Tema

**Problema y Causa:**
- `FIX_TOKEN_ERROR.md` - ¿Por qué ocurre?
- `SOLUTION_FLOWCHART.md` - Diagramas

**Solución Paso a Paso:**
- `README_TOKEN_FIX.md` - 3 pasos rápidos
- `CONFIGURE_TOKENS.md` - 4 pasos detallados

**Técnico:**
- `SOLUTION_FLOWCHART.md` - Cómo funciona internamente
- `contracts/PaymentProcessor.sol` - Smart Contract

**Solución de Problemas:**
- `CONFIGURE_TOKENS.md` - Sección "Solución de Problemas"
- `check_tokens_status.py` - Diagnóstico automático

---

## 🔄 El Flujo Completo

```
1. Usuario intenta crear pago
   ↓
2. API valida entrada
   ↓
3. Contrato rechaza token (NO PERMITIDO ❌)
   ↓
4. ERROR: "Token not allowed"
   ↓
5. Ejecutar: python deployment/add_allowed_tokens.py
   ↓
6. Script agrega token a contrato
   ↓
7. Contrato ahora permite el token (PERMITIDO ✅)
   ↓
8. Volver al paso 1: Ahora funciona correctamente
   ↓
9. ✅ Pago creado exitosamente
```

---

## 💡 Preguntas Frecuentes

**¿Solo una vez?**
Sí, ejecutas el script UNA SOLA VEZ. Después, los tokens están permitidos para siempre.

**¿Se cobra algo?**
Sí, pequeñas cantidades de gas (~0.001-0.005 ETH por token) en transacciones blockchain.

**¿Puedo agregar más tokens después?**
Sí, ejecuta el script nuevamente con nuevas direcciones en las variables de entorno.

**¿Necesito redeployar el contrato?**
No, este script solo modifica el estado del contrato existente.

---

## 🎯 Próximos Pasos

1. **Ahora:** Lee `README_TOKEN_FIX.md` (5 min)
2. **Luego:** Ejecuta `python check_tokens_status.py` (opcional, 1 min)
3. **Después:** Ejecuta `python deployment/add_allowed_tokens.py` (2-3 min)
4. **Finalmente:** Prueba `/payments/create` endpoint

---

## 📞 Soporte Rápido

| Problema | Solución |
|----------|----------|
| "No sé por dónde empezar" | Lee `README_TOKEN_FIX.md` |
| "Quiero entender el problema" | Lee `FIX_TOKEN_ERROR.md` |
| "Quiero ver diagramas" | Lee `SOLUTION_FLOWCHART.md` |
| "Necesito todo en detalle" | Lee `CONFIGURE_TOKENS.md` |
| "Mi configuración está mal" | Ejecuta `check_tokens_status.py` |
| "El script falla" | Revisa `CONFIGURE_TOKENS.md` → Solución de Problemas |

---

## 🚀 Lo Más Importante

```
╔══════════════════════════════════════════════════════╗
║                                                      ║
║  Ejecuta ESTO una sola vez:                         ║
║                                                      ║
║  python deployment/add_allowed_tokens.py            ║
║                                                      ║
║  Y tu sistema funcionará para siempre después.      ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

---

**Última actualización:** 2025-11-20
**Versión:** 0.5.0
**Estado:** ✅ Documentación Completa
