# 🔧 Configurar Remix IDE con OpenZeppelin Imports

## 🔴 Problema
Remix no puede encontrar los imports de OpenZeppelin:
```
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

## ✅ Solución

### OPCIÓN 1: Usar GitHub Compiler (RECOMENDADO - 2 minutos)

Esta es la forma más fácil. Remix puede descargar los archivos directamente desde GitHub.

**Paso 1: En Remix, ve a "File Explorers" (icono carpeta)**
- Haz clic en el icono de carpeta en la izquierda
- O presiona `Ctrl+Shift+F` (Windows/Linux) o `Cmd+Shift+F` (Mac)

**Paso 2: Copia el contrato correctamente**

Modifica los imports para usar GitHub directamente:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/IERC20.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/security/ReentrancyGuard.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol";

// ... resto del contrato igual
```

**Paso 3: Compilar**
- Solidity Compiler → Versión: `0.8.20` (o similar)
- Click "Compile PaymentProcessor.sol"
- Espera ✅ verde

---

### OPCIÓN 2: Usar npm Package (Si prefieres local)

Si quieres compilar en tu máquina local:

```bash
cd passlabs/backend

# Instalar Hardhat y OpenZeppelin
npm install --save-dev hardhat @openzeppelin/contracts

# Inicializar Hardhat
npx hardhat init
# Selecciona: "Create a basic sample project"

# Crear archivo del contrato
mkdir -p contracts
cp contracts/PaymentProcessor.sol contracts/

# Compilar
npx hardhat compile

# El bytecode estará en:
# artifacts/contracts/PaymentProcessor.sol/PaymentProcessor.json
```

Extrae el bytecode:
```bash
cat artifacts/contracts/PaymentProcessor.sol/PaymentProcessor.json | jq '.bytecode' | tr -d '"'
```

---

### OPCIÓN 3: Descargar archivos manualmente (Más trabajo, pero funciona)

**Paso 1: Descargar archivos de OpenZeppelin**

Ve a: https://github.com/OpenZeppelin/openzeppelin-contracts/tree/master/contracts

Descarga:
- `token/ERC20/IERC20.sol`
- `security/ReentrancyGuard.sol`
- `access/Ownable.sol`

(También necesitarás las dependencias internas)

**Paso 2: Crear carpeta en Remix**

En Remix:
- File Explorer → Click ➕ (New Folder)
- Nombre: `@openzeppelin`
- Dentro crea: `contracts`

**Paso 3: Subir archivos**

Arrastra los archivos descargados a la carpeta en Remix.

---

## 🎯 OPCIÓN 1 (GitHub) - RECOMENDADA

Es la más simple. Solo necesitas cambiar los imports a URLs de GitHub.

### Aquí está el contrato listo para Remix:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/IERC20.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/security/ReentrancyGuard.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol";

/**
 * @title PaymentProcessor
 * @dev Contrato para procesar pagos en stablecoins en Scroll Sepolia
 * @notice Este contrato permite transferir stablecoins de forma segura
 */
contract PaymentProcessor is ReentrancyGuard, Ownable {
    // ==================== ESTADO ====================

    /// @dev Estructura para almacenar información de un pago
    struct Payment {
        address recipient;
        uint256 amount;
        address tokenAddress;
        uint256 timestamp;
        bool completed;
    }

    /// @dev Mapeo de payment ID a Payment
    mapping(bytes32 => Payment) public payments;

    /// @dev Mapeo de dirección permitida de tokens
    mapping(address => bool) public allowedTokens;

    /// @dev Contador de pagos procesados
    uint256 public paymentCount;

    /// @dev Balance de tokens retenidos por el contrato
    mapping(address => uint256) public tokenBalances;

    // ==================== EVENTOS ====================

    /**
     * @dev Evento emitido cuando se procesa un pago exitosamente
     */
    event PaymentProcessed(
        bytes32 indexed paymentId,
        address indexed recipient,
        uint256 amount,
        address indexed tokenAddress,
        uint256 timestamp
    );

    /**
     * @dev Evento emitido cuando un pago falla
     */
    event PaymentFailed(
        bytes32 indexed paymentId,
        string reason,
        uint256 timestamp
    );

    /**
     * @dev Evento emitido cuando se retiran fondos
     */
    event FundsWithdrawn(
        address indexed token,
        uint256 amount,
        address indexed recipient,
        uint256 timestamp
    );

    /**
     * @dev Evento emitido cuando se agrega un token permitido
     */
    event TokenAdded(address indexed tokenAddress, uint256 timestamp);

    /**
     * @dev Evento emitido cuando se remueve un token permitido
     */
    event TokenRemoved(address indexed tokenAddress, uint256 timestamp);

    // ==================== MODIFICADORES ====================

    /**
     * @dev Verifica que el token esté permitido
     */
    modifier onlyAllowedToken(address _token) {
        require(allowedTokens[_token], "Token no permitido");
        _;
    }

    /**
     * @dev Verifica que la dirección sea válida
     */
    modifier validAddress(address _address) {
        require(_address != address(0), "Direccion invalida");
        _;
    }

    /**
     * @dev Verifica que la cantidad sea válida
     */
    modifier validAmount(uint256 _amount) {
        require(_amount > 0, "Cantidad debe ser mayor a 0");
        require(_amount <= 1_000_000 * 10 ** 18, "Cantidad demasiado grande");
        _;
    }

    // ==================== CONSTRUCTOR ====================

    /**
     * @dev Inicializa el contrato
     */
    constructor() {
        paymentCount = 0;
    }

    // ==================== FUNCIONES ADMIN ====================

    /**
     * @dev Agrega un token permitido (solo owner)
     * @param _tokenAddress Dirección del contrato del token
     */
    function addAllowedToken(
        address _tokenAddress
    ) external onlyOwner validAddress(_tokenAddress) {
        require(!allowedTokens[_tokenAddress], "Token ya esta permitido");
        allowedTokens[_tokenAddress] = true;
        emit TokenAdded(_tokenAddress, block.timestamp);
    }

    /**
     * @dev Remueve un token permitido (solo owner)
     * @param _tokenAddress Dirección del contrato del token
     */
    function removeAllowedToken(
        address _tokenAddress
    ) external onlyOwner validAddress(_tokenAddress) {
        require(allowedTokens[_tokenAddress], "Token no esta permitido");
        allowedTokens[_tokenAddress] = false;
        emit TokenRemoved(_tokenAddress, block.timestamp);
    }

    /**
     * @dev Retira fondos del contrato (solo owner)
     * @param _tokenAddress Dirección del token a retirar
     * @param _amount Cantidad a retirar
     */
    function withdrawFunds(
        address _tokenAddress,
        uint256 _amount
    )
        external
        onlyOwner
        validAddress(_tokenAddress)
        validAmount(_amount)
        nonReentrant
    {
        require(tokenBalances[_tokenAddress] >= _amount, "Saldo insuficiente");

        tokenBalances[_tokenAddress] -= _amount;

        IERC20 token = IERC20(_tokenAddress);
        require(token.transfer(owner(), _amount), "Fallo al transferir tokens");

        emit FundsWithdrawn(_tokenAddress, _amount, owner(), block.timestamp);
    }

    /**
     * @dev Retira todos los fondos de un token (solo owner)
     * @param _tokenAddress Dirección del token a retirar
     */
    function withdrawAllFunds(
        address _tokenAddress
    ) external onlyOwner validAddress(_tokenAddress) {
        uint256 amount = tokenBalances[_tokenAddress];
        require(amount > 0, "No hay fondos para retirar");

        tokenBalances[_tokenAddress] = 0;

        IERC20 token = IERC20(_tokenAddress);
        require(token.transfer(owner(), amount), "Fallo al transferir tokens");

        emit FundsWithdrawn(_tokenAddress, amount, owner(), block.timestamp);
    }

    // ==================== FUNCIONES PRINCIPALES ====================

    /**
     * @dev Procesa un pago en stablecoin
     * @param _recipient Dirección del destinatario
     * @param _amount Cantidad a transferir (sin decimales ajustados)
     * @param _tokenAddress Dirección del token ERC20
     * @return success Verdadero si el pago se procesó correctamente
     */
    function processPayment(
        address _recipient,
        uint256 _amount,
        address _tokenAddress
    )
        external
        nonReentrant
        onlyAllowedToken(_tokenAddress)
        validAddress(_recipient)
        validAmount(_amount)
        returns (bool success)
    {
        bytes32 paymentId = generatePaymentId(_recipient, _amount);

        // Verificar que el pago no exista ya
        require(!payments[paymentId].completed, "Pago ya fue procesado");

        IERC20 token = IERC20(_tokenAddress);

        // Transferir tokens del remitente a este contrato
        bool transferred = token.transferFrom(
            msg.sender,
            address(this),
            _amount
        );

        if (!transferred) {
            emit PaymentFailed(
                paymentId,
                "Fallo transferencia de tokens",
                block.timestamp
            );
            return false;
        }

        // Registrar el pago
        payments[paymentId] = Payment({
            recipient: _recipient,
            amount: _amount,
            tokenAddress: _tokenAddress,
            timestamp: block.timestamp,
            completed: true
        });

        // Actualizar balance
        tokenBalances[_tokenAddress] += _amount;

        // Incrementar contador
        paymentCount++;

        // Emitir evento
        emit PaymentProcessed(
            paymentId,
            _recipient,
            _amount,
            _tokenAddress,
            block.timestamp
        );

        return true;
    }

    /**
     * @dev Procesa un pago y transfiere inmediatamente al destinatario
     * @param _recipient Dirección del destinatario
     * @param _amount Cantidad a transferir
     * @param _tokenAddress Dirección del token ERC20
     * @return success Verdadero si el pago se completó
     */
    function processPaymentAndTransfer(
        address _recipient,
        uint256 _amount,
        address _tokenAddress
    )
        external
        nonReentrant
        onlyAllowedToken(_tokenAddress)
        validAddress(_recipient)
        validAmount(_amount)
        returns (bool success)
    {
        bytes32 paymentId = generatePaymentId(_recipient, _amount);

        IERC20 token = IERC20(_tokenAddress);

        // Transferir directamente del remitente al destinatario
        bool transferred = token.transferFrom(msg.sender, _recipient, _amount);

        if (!transferred) {
            emit PaymentFailed(
                paymentId,
                "Fallo transferencia directa",
                block.timestamp
            );
            return false;
        }

        // Registrar el pago
        payments[paymentId] = Payment({
            recipient: _recipient,
            amount: _amount,
            tokenAddress: _tokenAddress,
            timestamp: block.timestamp,
            completed: true
        });

        paymentCount++;

        emit PaymentProcessed(
            paymentId,
            _recipient,
            _amount,
            _tokenAddress,
            block.timestamp
        );

        return true;
    }

    // ==================== FUNCIONES DE LECTURA ====================

    /**
     * @dev Obtiene el estado de un pago
     * @param _paymentId ID del pago
     * @return Payment Información del pago
     */
    function getPaymentStatus(
        bytes32 _paymentId
    ) external view returns (Payment memory) {
        return payments[_paymentId];
    }

    /**
     * @dev Verifica si un pago existe y fue completado
     * @param _paymentId ID del pago
     * @return bool Verdadero si el pago fue completado
     */
    function isPaymentCompleted(
        bytes32 _paymentId
    ) external view returns (bool) {
        return payments[_paymentId].completed;
    }

    /**
     * @dev Obtiene el balance de un token en el contrato
     * @param _tokenAddress Dirección del token
     * @return uint256 Balance del token
     */
    function getTokenBalance(
        address _tokenAddress
    ) external view returns (uint256) {
        return tokenBalances[_tokenAddress];
    }

    /**
     * @dev Obtiene el número total de pagos procesados
     * @return uint256 Número de pagos
     */
    function getPaymentCount() external view returns (uint256) {
        return paymentCount;
    }

    /**
     * @dev Verifica si un token está permitido
     * @param _tokenAddress Dirección del token
     * @return bool Verdadero si el token está permitido
     */
    function isTokenAllowed(
        address _tokenAddress
    ) external view returns (bool) {
        return allowedTokens[_tokenAddress];
    }

    // ==================== FUNCIONES INTERNAS ====================

    /**
     * @dev Genera un ID único para un pago
     * @param _recipient Dirección del destinatario
     * @param _amount Cantidad
     * @return bytes32 ID del pago
     */
    function generatePaymentId(
        address _recipient,
        uint256 _amount
    ) internal view returns (bytes32) {
        return
            keccak256(
                abi.encodePacked(
                    msg.sender,
                    _recipient,
                    _amount,
                    block.timestamp,
                    block.number
                )
            );
    }

    // ==================== FUNCIONES DE EMERGENCIA ====================

    /**
     * @dev Permite al owner transferir tokens manualmente en caso de emergencia
     * @param _tokenAddress Dirección del token
     * @param _recipient Dirección del destinatario
     * @param _amount Cantidad a transferir
     */
    function emergencyWithdraw(
        address _tokenAddress,
        address _recipient,
        uint256 _amount
    )
        external
        onlyOwner
        validAddress(_tokenAddress)
        validAddress(_recipient)
        validAmount(_amount)
    {
        IERC20 token = IERC20(_tokenAddress);
        require(
            token.transfer(_recipient, _amount),
            "Fallo transferencia de emergencia"
        );
    }

    /**
     * @dev Recibe ETH (en caso de que se envíe accidentalmente)
     */
    receive() external payable {}

    /**
     * @dev Retira ETH accidental
     */
    function withdrawETH() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No hay ETH para retirar");

        (bool success, ) = payable(owner()).call{value: balance}("");
        require(success, "Fallo al retirar ETH");
    }
}
```

---

## 📋 Pasos Rápidos (GitHub - Opción 1)

1. **Abre Remix:** https://remix.ethereum.org
2. **Crea archivo:** `PaymentProcessor.sol`
3. **Copia el código anterior** (con imports de GitHub)
4. **Solidity Compiler:** Versión `0.8.20`
5. **Click:** "Compile PaymentProcessor.sol"
6. **Espera:** ✅ verde
7. **Click:** "Compilation Details"
8. **Busca:** "Object"
9. **Copia:** TODO el bytecode (5000+ caracteres)

---

## 🚀 Si quieres compilar localmente

```bash
cd passlabs/backend

# Instalar dependencias
npm install --save-dev hardhat @openzeppelin/contracts

# Compilar
npx hardhat compile

# Extraer bytecode
jq '.bytecode' artifacts/contracts/PaymentProcessor.sol/PaymentProcessor.json | tr -d '"'
```

---

## ✅ Cuando tengas el bytecode

1. Abre `deployment/deploy_final.py`
2. Busca: `PAYMENT_PROCESSOR_BYTECODE = None`
3. Reemplaza con tu bytecode: `PAYMENT_PROCESSOR_BYTECODE = "0x..."`
4. Ejecuta: `python3 deployment/deploy_final.py --update-env`

---

## 💡 Resumen

**La forma más rápida:**
- Usa GitHub imports (URL completa)
- Compila en Remix
- Copia bytecode desde "Compilation Details"
- Actualiza deploy_final.py
- ¡Listo!

**Tiempo:** 5 minutos
