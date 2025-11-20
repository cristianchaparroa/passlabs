require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    "scroll-sepolia": {
      url: "https://sepolia-rpc.scroll.io/",
      chainId: 534351,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    }
  },
  etherscan: {
    apiKey: process.env.SCROLLSCAN_API_KEY || "abc",
    customChains: [
      {
        network: "scroll-sepolia",
        chainId: 534351,
        urls: {
          apiURL: "https://api-sepolia.scrollscan.com/api",
          browserURL: "https://sepolia.scrollscan.com"
        }
      }
    ]
  },
  sourcify: {
    enabled: false
  }
};
