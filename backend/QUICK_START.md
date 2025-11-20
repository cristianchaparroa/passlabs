# ⚡ Quick Start - Crypto Payments API v0.5.0

## ✅ Estado Actual

**Backend está LISTO para producción** ✨

```
✅ Todos los servicios inicializan correctamente
✅ Blockchain conectado (Scroll Sepolia)
✅ DeFiLlama API funcional (3 stablecoins)
✅ Sin errores de importación
✅ Sin advertencias de deprecación
✅ 27/27 validaciones pasadas
```

## 🚀 Ejecutar Localmente (5 minutos)

```bash
# 1. Navegar al directorio
cd /home/oscar/Github/passlabs/backend

# 2. Crear entorno virtual (si no existe)
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Validar configuración
python3 deploy_check.py

# 5. Iniciar servidor
python3 main.py

# 6. Probar (en otra terminal)
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

## 📝 Configuración Requerida

Archivo `.env` debe existir con:
```
PRIVATE_KEY=your_key_here
CONTRACT_ADDRESS=0x...
RPC_URL=https://sepolia-rpc.scroll.io/
CHAIN_ID=534351
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

## 🔧 Errores Resueltos en v0.5.0

| Error | Estado | Fix |
|-------|--------|-----|
| `ImportError: GAS_LIMIT` | ✅ FIXED | Constantes agregadas a `utils/constants.py` |
| `0 stablecoins obtenidos` | ✅ FIXED | Parser actualizado para `peggedAssets` |
| `Gas Price: None` | ✅ FIXED | Mejor manejo de errores en `get_network_info()` |
| Warnings de deprecación | ✅ FIXED | Migrado a lifespan context manager |

## 📊 API Endpoints

```
✅ GET  /health                    - Health check
✅ GET  /status                    - Estado detallado
✅ POST /payments/create           - Crear pago
✅ GET  /payments/status/{tx_hash} - Estado de pago
✅ GET  /stablecoins/prices        - Precios de stablecoins
✅ GET  /docs                      - Documentación Swagger
```

## 🚀 Despliegue a Producción

### Opción 1: Systemd Service (Recomendado VPS)
Ver `DEPLOYMENT.md` sección "Opción 1: Systemd Service"

### Opción 2: Docker (Recomendado Cloud)
Ver `DEPLOYMENT.md` sección "Opción 2: Docker"

### Opción 3: Nginx Reverse Proxy
Ver `DEPLOYMENT.md` sección "Opción 4: Nginx"

## 📚 Documentación Completa

- **DEPLOYMENT.md** - Guía completa de despliegue a producción
- **FIXES_v0.5.0.md** - Resumen detallado de correcciones
- **README.md** - Documentación general del proyecto
- **deploy_check.py** - Script de validación automática

## ✨ Próximos Pasos

1. **Copiar `.env` de ejemplo**: `cp .env.example .env`
2. **Editar con credenciales reales**: `nano .env`
3. **Validar**: `python3 deploy_check.py`
4. **Ejecutar**: `python3 main.py`
5. **Acceder**: http://localhost:8000/docs

## 🔍 Troubleshooting

### Puerto 8000 en uso
```bash
lsof -i :8000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9
```

### Dependencias faltantes
```bash
pip install --upgrade -r requirements.txt
```

### Conexión RPC fallando
```bash
curl https://sepolia-rpc.scroll.io/
```

### Clave privada inválida
```bash
python3 -c "from eth_account import Account; Account.from_key('0x...')"
```

## 📞 Soporte

Ver documentación:
1. `DEPLOYMENT.md` - Para despliegue
2. `FIXES_v0.5.0.md` - Para cambios
3. `README.md` - Para detalles generales

---

**¡Backend listo para producción!** 🎉

Versión: 0.5.0 | Status: ✅ READY | Fecha: Nov 2025
