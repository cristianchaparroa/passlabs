# Constantes de la aplicación

# Blockchain
SCROLL_SEPOLIA_CHAIN_ID = 534351
SCROLL_SEPOLIA_RPC = "https://sepolia-rpc.scroll.io/"

# Gas limits
DEFAULT_GAS_LIMIT = 100000
MAX_GAS_LIMIT = 500000

# Stablecoins
SUPPORTED_STABLECOINS = ["USDC", "USDT", "DAI"]

# Payment limits
MIN_PAYMENT_AMOUNT = 0.01
MAX_PAYMENT_AMOUNT = 1_000_000

# Cache
DEFAULT_CACHE_TTL = 300  # 5 minutos

# DeFiLlama API
DEFI_LLAMA_STABLECOINS_ENDPOINT = "https://stablecoins.llama.fi/stablecoins"

# Transaction confirmations
REQUIRED_CONFIRMATIONS = 12
PENDING_TIMEOUT = 600  # 10 minutos

# Error messages
ERROR_INVALID_ADDRESS = "Dirección Ethereum inválida"
ERROR_INVALID_AMOUNT = "Cantidad inválida"
ERROR_INVALID_STABLECOIN = "Stablecoin no soportada"
ERROR_TRANSACTION_FAILED = "La transacción falló"
ERROR_INSUFFICIENT_GAS = "Gas insuficiente"
ERROR_RPC_CONNECTION = "Error conectando a RPC"
ERROR_API_UNAVAILABLE = "API no disponible"
