# Makefile for ZKBioRegistry Hardhat Project in YoLo-Face/Yolo-ZK/Contract

CONTRACT_DIR=Contract

# Default target
all: help

# Start local Hardhat node
node:
	cd $(CONTRACT_DIR) && npx hardhat node &

# Deploy contract and store address
deploy:
	cd $(CONTRACT_DIR) && npx hardhat run scripts/deploy-zkbio.ts --network localhost

# Commit data using the saved address
commit:
	cd $(CONTRACT_DIR) && \
	if [ ! -f zkbio-address.txt ]; then \
		echo "No contract found. Deploying first..."; \
		npx hardhat run scripts/deploy.js --network localhost; \
	fi && \
	npx hardhat run scripts/generate_commitment.ts --network localhost

# Clean up stored address
clean:
	cd $(CONTRACT_DIR) && rm -f zkbio-address.txt

# Display available commands
help:
	@echo "Available commands:"
	@echo "  make node     - Starts the local Hardhat node"
	@echo "  make deploy   - Deploys the ZKBioRegistry contract and saves the address"
	@echo "  make commit   - Runs the commitment script (deploys first if needed)"
	@echo "  make clean    - Removes the saved contract address"
.PHONY: all node deploy commit clean help
.DEFAULT_GOAL := all