# 🚀 Guía de Despliegue a Producción - Crypto Payments API

## 📋 Resumen Ejecutivo

Este documento proporciona una guía paso a paso para desplegar la API de Crypto Payments en un entorno de producción. La aplicación está lista para producción después de las correcciones implementadas en v0.5.0.

## ✅ Estado de Preparación para Producción

- ✅ **Blockchain Service**: Conectado y funcional
- ✅ **DeFiLlama Service**: Obtiene precios de stablecoins correctamente
- ✅ **Payment Service**: Inicializado
- ✅ **Gas Price Tracking**: Funcionando correctamente
- ✅ **Error Handling**: Mejorado con manejo granular de errores
- ✅ **Lifespan Events**: Migrado a contexto manager (sin advertencias de deprecación)
- ✅ **Logging**: Completo y estructurado

## 🔧 Cambios Realizados en v0.5.0

### 1. Corrección de Importaciones (constants.py)
- ✅ Agregadas constantes faltantes:
  - `GAS_LIMIT = 100000`
  - `GAS_PRICE_MULTIPLIER = 1.2`
  - `MAX_RETRIES = 3`

### 2. Actualización del Parser de DeFiLlama
- ✅ Corregida estructura de parseo para `peggedAssets`
- ✅ Ahora obtiene correctamente los 3 stablecoins (USDT, USDC, DAI)
- ✅ Calcula correctamente market cap y cambios en 24h

### 3. Mejoras en get_network_info()
- ✅ Manejo granular de errores por campo
- ✅ Retorna valores parciales en caso de error individual
- ✅ Gas price ahora se muestra correctamente

### 4. Migración de on_event a Lifespan
- ✅ Eliminadas advertencias de deprecación
- ✅ Mejor estructura de ciclo de vida
- ✅ Código más limpio y moderno

## 📋 Pre-Requisitos de Despliegue

### Servidor/Infraestructura
- Python 3.9+
- Ubuntu 20.04 LTS o equivalente (recomendado)
- 2GB RAM mínimo
- 10GB almacenamiento
- Conexión a Internet estable

### Credenciales Requeridas
- `PRIVATE_KEY`: Clave privada de cuenta Ethereum en Scroll Sepolia
- `CONTRACT_ADDRESS`: Dirección del contrato inteligente desplegado
- Opcional: `RPC_URL` (por defecto: Scroll Sepolia oficial)

## 🔐 Configuración de Seguridad Pre-Producción

### 1. Variables de Entorno

Crear archivo `.env` (NO incluir en git):

```bash
# Blockchain
NETWORK=scroll-sepolia
RPC_URL=https://sepolia-rpc.scroll.io/
PRIVATE_KEY=your_production_private_key_here
CONTRACT_ADDRESS=0x...deployed_contract_address
CHAIN_ID=534351

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Cache
CACHE_TTL=300

# DeFiLlama
DEFI_LLAMA_API_URL=https://stablecoins.llama.fi/stablecoins
```

### 2. Protección de Secretos

```bash
# Asegurarse de que .env NO está en control de versión
echo ".env" >> .gitignore

# Establecer permisos restrictivos
chmod 600 .env

# Usar gestor de secretos para producción (recomendado)
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
```

### 3. CORS Configuration

Para producción, actualizar `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Específico en producción
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📦 Instalación en Producción

### 1. Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3 python3-pip python3-venv git curl

# Crear usuario de aplicación (no root)
sudo useradd -m -s /bin/bash crypto-payments
sudo su - crypto-payments
```

### 2. Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/passlabs/passlabs.git
cd passlabs/backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con credenciales reales
```

### 3. Verificar Instalación

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar prueba rápida
python3 -c "
from config import settings
from services.blockchain_service import blockchain_service
print('✅ Blockchain Connected' if blockchain_service.is_connected() else '❌ Connection Failed')
"

# Verificar puerto disponible
lsof -i :8000 || echo "✅ Puerto 8000 disponible"
```

## 🚀 Opciones de Despliegue

### Opción 1: Systemd Service (Recomendado para VPS)

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/crypto-payments.service
```

```ini
[Unit]
Description=Crypto Payments API
After=network.target

[Service]
Type=notify
User=crypto-payments
WorkingDirectory=/home/crypto-payments/passlabs/backend
Environment="PATH=/home/crypto-payments/passlabs/backend/venv/bin"
ExecStart=/home/crypto-payments/passlabs/backend/venv/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/crypto-payments/api.log
StandardError=append:/var/log/crypto-payments/error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/crypto-payments
sudo chown crypto-payments:crypto-payments /var/log/crypto-payments

# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable crypto-payments
sudo systemctl start crypto-payments

# Verificar estado
sudo systemctl status crypto-payments

# Ver logs en tiempo real
sudo tail -f /var/log/crypto-payments/api.log
```

### Opción 2: Docker (Recomendado para Cloud)

Crear `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5)" || exit 1

EXPOSE 8000

CMD ["python3", "main.py"]
```

Crear `.dockerignore`:

```
.git
.gitignore
__pycache__
*.pyc
*.pyo
venv
.env
.pytest_cache
logs
```

Construir e ejecutar:

```bash
# Construir imagen
docker build -t crypto-payments:0.5.0 .

# Ejecutar contenedor
docker run -d \
  --name crypto-payments \
  -p 8000:8000 \
  --env-file .env \
  crypto-payments:0.5.0

# Verificar logs
docker logs -f crypto-payments

# Detener contenedor
docker stop crypto-payments
docker rm crypto-payments
```

### Opción 3: Docker Compose

Crear `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: crypto-payments-api
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      - API_HOST=0.0.0.0
      - DEBUG=False
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  nginx:
    image: nginx:alpine
    container_name: crypto-payments-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped
```

Ejecutar:

```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Opción 4: Nginx Reverse Proxy

Crear `/etc/nginx/sites-available/crypto-payments`:

```nginx
upstream crypto_payments {
    server localhost:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    location / {
        proxy_pass http://crypto_payments;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API documentation access
    location /docs {
        proxy_pass http://crypto_payments/docs;
    }
    
    location /redoc {
        proxy_pass http://crypto_payments/redoc;
    }
}
```

Habilitar sitio:

```bash
sudo ln -s /etc/nginx/sites-available/crypto-payments /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 Monitoreo en Producción

### 1. Health Check Endpoint

```bash
# Verificar estado general
curl https://yourdomain.com/health

# Verificar estado detallado
curl https://yourdomain.com/status
```

### 2. Logging

```bash
# Ver últimas líneas
tail -100 /var/log/crypto-payments/api.log

# Buscar errores
grep ERROR /var/log/crypto-payments/error.log

# Monitoreo en tiempo real
watch -n 1 'tail -20 /var/log/crypto-payments/api.log'
```

### 3. Métricas Importantes

- **Uptime**: Verificar que systemd mantiene el servicio activo
- **Errores de RPC**: Monitorear conexión a Scroll Sepolia
- **Rate Limiting**: Implementar límites por IP
- **Gas Prices**: Registrar cambios en precios del gas
- **Latencia API**: Monitorear respuesta a requests

## 🔍 Checklist Pre-Despliegue

```
Seguridad:
☐ .env protegido y NO en git
☐ CORS configurado específicamente
☐ DEBUG=False en producción
☐ SSL/TLS configurado
☐ Firewall configurado

Funcionalidad:
☐ Blockchain conectado correctamente
☐ Smart Contract verificado
☐ DeFiLlama API accesible
☐ Todos los endpoints funcionan
☐ Health check retorna 200

Performance:
☐ Servidor tiene 2GB+ RAM
☐ Database/Cache configurado
☐ Nginx/Reverse proxy funcionando
☐ Rate limiting configurado
☐ Logs rotados

Monitoreo:
☐ Logs configurados
☐ Alertas en lugar
☐ Backup automatizado
☐ Plan de recuperación ante fallos
```

## 🚨 Troubleshooting de Despliegue

### Error: "Address already in use"

```bash
# Encontrar proceso usando puerto 8000
lsof -i :8000

# Matar proceso (si es necesario)
kill -9 <PID>

# O cambiar puerto en .env
API_PORT=8001
```

### Error: "Connection refused" a Blockchain

```bash
# Verificar RPC URL
curl https://sepolia-rpc.scroll.io/

# Verificar PRIVATE_KEY válida
python3 -c "from eth_account import Account; Account.from_key('0x...')"

# Verificar chain ID
echo $CHAIN_ID  # Debe ser 534351
```

### Error: "Module not found"

```bash
# Reinstalar dependencias
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Service no inicia

```bash
# Ver detalles del error
sudo systemctl status crypto-payments -l

# Ver logs del servicio
sudo journalctl -u crypto-payments -n 50

# Reintentar manualmente
cd /home/crypto-payments/passlabs/backend
source venv/bin/activate
python3 main.py
```

## 📈 Scaling en Producción

### Load Balancing

Para múltiples instancias, usar Nginx upstream:

```nginx
upstream crypto_payments {
    least_conn;  # Algoritmo de conexiones mínimas
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}
```

### Caching

```nginx
location /stablecoins/prices {
    proxy_cache_valid 200 5m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}
```

## 🔄 Rollback Plan

Si hay problemas después del despliegue:

```bash
# Ver versión actual
git log -1 --oneline

# Revertir a versión anterior
git revert HEAD
git pull
systemctl restart crypto-payments

# O cambiar rama
git checkout main
git pull
systemctl restart crypto-payments
```

## 📞 Soporte y Contacto

Para problemas de despliegue:
1. Verificar logs: `/var/log/crypto-payments/`
2. Revisar health check: `/health` endpoint
3. Contactar al equipo de desarrollo

## 📝 Notas Importantes

- Backup `.env` en lugar seguro (NO en git)
- Rotar PRIVATE_KEY periódicamente
- Monitorear límites de rate de DeFiLlama API
- Mantener Python y dependencias actualizadas
- Realizar testing en staging antes de producción

---

**Versión**: 0.5.0  
**Última actualización**: Noviembre 2025  
**Estado**: ✅ Listo para Producción