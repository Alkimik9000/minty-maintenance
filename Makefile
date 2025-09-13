# Makefile for Mint Maintenance Script

.PHONY: help test run dry-run install lint clean

help:
	@echo "Mint Maintenance Script - Available commands:"
	@echo "  make test      - Run dry-run test"
	@echo "  make dry-run   - Same as test"
	@echo "  make run       - Run full maintenance (requires sudo)"
	@echo "  make install   - Install dependencies"
	@echo "  make lint      - Run code linters"
	@echo "  make clean     - Clean generated files"

test: dry-run

dry-run:
	@echo "Running maintenance script in dry-run mode..."
	@bash mint-maintainer.sh dry-run

run:
	@echo "Running full maintenance (this will make changes)..."
	@bash mint-maintainer.sh

install:
	@echo "Installing Python dependencies..."
	@sudo apt update
	@sudo apt install -y python3 python3-pip
	@echo "Dependencies installed."

lint:
	@echo "Running Python linter..."
	@python3 -m py_compile scripts/**/*.py 2>/dev/null || true
	@echo "Running shellcheck on bash scripts..."
	@shellcheck mint-maintainer.sh 2>/dev/null || echo "Shellcheck not installed"

clean:
	@echo "Cleaning generated files..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@rm -f reports/*.txt 2>/dev/null || true
	@echo "Clean complete."
