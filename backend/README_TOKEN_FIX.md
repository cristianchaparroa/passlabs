# 🔧 SOLUCIÓN: Error "Token not allowed in contract"

## El Problema

```
ERROR - Error checking token allowed: Could not transact with/call contract function
ERROR - Token StablecoinEnum.USDC is not allowed in payment contract
```

## La Causa

El Smart Contract `PaymentProcessor` requiere que cada token sea **agregado explícitamente** por el owner antes de poder procesarlo. Es un mecanismo de seguridad.

**Actualmente:** USDC, USDT y DAI NO están permitidos en tu contrato.

## La Solución (3 Pasos)

### 1️⃣ Verifica tu `.env`

```bash
cd backend
cat .env
```

Debe tener estas variables:
- `CONTRACT_ADDRESS` ← Dirección del contrato desplegado
- `PRIVATE_KEY` ← Tu clave privada (must be contract owner)
- `RPC_URL` ← https://sepolia-rpc.scroll.io/
- `USDC_ADDRESS`, `USDT_ADDRESS`, `DAI_ADDRESS` ← Direcciones de tokens

Si falta algo, edita el archivo:
```bash
nano .env
```

### 2️⃣ Obtén ETH en Scroll Sepolia

Necesitas ~0.05 ETH para pagar el gas:

```bash
# Faucet: https://scroll-testnet-faucet.allthatnode.com:3001/
# O usa el puente: https://scroll.io/bridge
```

Verifica tu balance:
```bash
python check_tokens_status.py
```

### 3️⃣ Ejecuta el Script de Configuración

```bash
python deployment/add_allowed_tokens.py
```

El script:
- ✅ Valida configuración
- ✅ Se conecta a blockchain
- ✅ Verifica qué tokens necesitan agregarse
- ✅ Agrega los tokens (USDC, USDT, DAI)
- ✅ Espera confirmación en blockchain
- ✅ Verifica que todo funcionó

**El script es interactivo y te guiará paso a paso.**

## ✅ Verificación

Después de ejecutar el script, deberías ver:

```
✅ USDC: ✅ PERMITIDO en el contrato
✅ USDT: ✅ PERMITIDO en el contrato
✅ DAI: ✅ PERMITIDO en el contrato

✅ ¡ÉXITO! Todos los tokens están configurados correctamente
✅ El sistema está listo para procesar pagos
```

Luego prueba el endpoint:

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

Si ves una respuesta exitosa con `"success": true`, ¡está funcionando! 🎉

## 🔍 Diagnóstico Rápido

Si quieres verificar el estado sin ejecutar el script completo:

```bash
python check_tokens_status.py
```

Este script solo verifica y reporta, sin modificar nada.

## 📚 Documentación Completa

- **FIX_TOKEN_ERROR.md** - Resumen rápido
- **CONFIGURE_TOKENS.md** - Guía detallada y solución de problemas
- **check_tokens_status.py** - Script de diagnóstico
- **deployment/add_allowed_tokens.py** - Script para agregar tokens

## 🆘 Errores Comunes

| Error | Solución |
|-------|----------|
| "PRIVATE_KEY no configurada" | Edita `.env` y agrega tu clave privada |
| "Contract not deployed correctly" | Verifica `CONTRACT_ADDRESS` en `.env` |
| "Balance es 0" | Obtén ETH de testnet (ver Paso 2) |
| "Not the contract owner" | Solo el owner del contrato puede hacer esto |
| "Transacción timeout" | Espera unos minutos e intenta de nuevo |
| "Connection refused" | Verifica que RPC_URL es correcto |

## 🎯 TL;DR (Resumen Ultra Rápido)

```bash
# 1. Verifica configuración
cat backend/.env

# 2. Obtén ETH (si no tienes)
# https://scroll-testnet-faucet.allthatnode.com:3001/

# 3. Ejecuta el script (UNA SOLA VEZ)
cd backend
python deployment/add_allowed_tokens.py

# 4. ¡Listo! Ya puedes procesar pagos
```

## 🔑 Información Importante

- **Esto solo se hace una vez** después de desplegar el contrato
- **Se aplica para siempre** - Los tokens permanecen permitidos
- **No hay riesgo** - Solo agregamos tokens autorizados
- **Sin modificación** - El script es seguro y transparente

## ❓ Preguntas

**¿Puedo agregar más tokens después?**
Sí, ejecuta el script nuevamente con nuevas direcciones.

**¿Se cobran fees?**
Sí, pequeñas cantidades de gas (~0.001-0.005 ETH por token).

**¿Necesito hacer esto en cada reinicio?**
No, solo una vez. Los tokens quedan permanentemente permitidos en el contrato.

## 📞 Próximos Pasos

1. Ejecuta: `python deployment/add_allowed_tokens.py`
2. Reinicia el servidor
3. Prueba el endpoint `/payments/create`
4. ¡Comienza a procesar pagos! 🚀

---

**Eso es todo. El script maneja todo automáticamente. ¡Adelante!** ✅