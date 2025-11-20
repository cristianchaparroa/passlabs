import logging
import sys
from pathlib import Path

# Crear directorio de logs si no existe
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configurar formato de logs
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Logger para consola
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

# Logger para archivo
file_handler = logging.FileHandler(log_dir / "app.log")
file_handler.setFormatter(log_format)

# Logger principal
logger = logging.getLogger("crypto_payments")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Obtener logger con nombre específico

    Args:
        name: Nombre del logger (usualmente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(f"crypto_payments.{name}")
