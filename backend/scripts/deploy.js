const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Starting deployment to Scroll Sepolia...\n");

  // Get the deployer's address
  const [deployer] = await hre.ethers.getSigners();
  const deployerAddress = await deployer.getAddress();
  
  console.log("📝 Deploying contract with account:", deployerAddress);

  // Get account balance
  const balance = await hre.ethers.provider.getBalance(deployerAddress);
  console.log("💰 Account balance:", hre.ethers.formatEther(balance), "ETH\n");

  // Check if we have enough balance
  if (balance < hre.ethers.parseEther("0.001")) {
    console.error("❌ Insufficient balance! You need at least 0.001 ETH to deploy.");
    console.log("Get testnet ETH from: https://scroll.io/portal");
    process.exit(1);
  }

  // Deploy the PaymentProcessor contract
  console.log("⏳ Deploying PaymentProcessor...");
  const PaymentProcessor = await hre.ethers.getContractFactory("PaymentProcessor");
  
  // Deploy with the deployer's address as the initial owner
  const paymentProcessor = await PaymentProcessor.deploy(deployerAddress);
  
  console.log("⏳ Waiting for deployment transaction...");
  await paymentProcessor.waitForDeployment();
  
  const contractAddress = await paymentProcessor.getAddress();
  const deployTx = paymentProcessor.deploymentTransaction();
  
  console.log("\n✅ PaymentProcessor deployed successfully!");
  console.log("📍 Contract address:", contractAddress);
  console.log("👤 Owner address:", deployerAddress);
  console.log("🔗 Transaction hash:", deployTx?.hash);
  
  // Save deployment info to contracts directory
  const deploymentInfo = {
    network: "scroll-sepolia",
    chainId: 534351,
    contractAddress: contractAddress,
    ownerAddress: deployerAddress,
    deploymentTime: new Date().toISOString(),
    transactionHash: deployTx?.hash,
    blockNumber: deployTx?.blockNumber,
    constructorArguments: [deployerAddress]
  };
  
  const deploymentsDir = path.join(__dirname, "..", "contracts");
  const deploymentFile = path.join(deploymentsDir, "deployment-info.json");
  
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  console.log("\n💾 Deployment info saved to:", deploymentFile);
  
  // Update .env file with contract address
  const envPath = path.join(__dirname, "..", ".env");
  let envContent = fs.readFileSync(envPath, "utf8");
  
  // Replace or add CONTRACT_ADDRESS
  if (envContent.includes("CONTRACT_ADDRESS=")) {
    envContent = envContent.replace(
      /CONTRACT_ADDRESS=.*/,
      `CONTRACT_ADDRESS=${contractAddress}`
    );
  } else {
    envContent += `\nCONTRACT_ADDRESS=${contractAddress}\n`;
  }
  
  fs.writeFileSync(envPath, envContent);
  console.log("✅ Updated .env file with contract address\n");
  
  console.log("🔗 View on Scrollscan:");
  console.log(`   https://sepolia.scrollscan.com/address/${contractAddress}\n`);
  
  // Wait for block confirmations before verification
  console.log("⏳ Waiting for 5 block confirmations before verification...");
  await deployTx?.wait(5);
  console.log("✅ Confirmations received!\n");
  
  // Verify the contract
  console.log("🔍 Verifying contract on Scrollscan...");
  try {
    await hre.run("verify:verify", {
      address: contractAddress,
      constructorArguments: [deployerAddress],
      contract: "contracts/PaymentProcessor.sol:PaymentProcessor"
    });
    console.log("✅ Contract verified successfully!\n");
  } catch (error) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ Contract is already verified!\n");
    } else {
      console.log("⚠️  Verification failed:", error.message);
      console.log("\n💡 You can verify manually later with:");
      console.log(`   npx hardhat verify --network scroll-sepolia ${contractAddress} "${deployerAddress}"\n`);
    }
  }
  
  // Print summary
  console.log("═".repeat(70));
  console.log("🎉 DEPLOYMENT COMPLETE!");
  console.log("═".repeat(70));
  console.log("\n📋 Summary:");
  console.log(`   Network:          Scroll Sepolia`);
  console.log(`   Contract Address: ${contractAddress}`);
  console.log(`   Owner:            ${deployerAddress}`);
  console.log(`   Transaction:      ${deployTx?.hash}`);
  console.log(`   Explorer:         https://sepolia.scrollscan.com/address/${contractAddress}`);
  console.log("\n⚠️  Next Steps:");
  console.log("   1. Add allowed stablecoin tokens using addAllowedToken()");
  console.log("   2. Test the contract on testnet");
  console.log("   3. Update your backend configuration\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });
