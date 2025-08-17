#!/bin/bash
# Setup script for FIRS E-Invoice Python SDK

echo "==========================================="
echo "FIRS E-Invoice Python SDK Setup"
echo "==========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ $(echo "$python_version >= $required_version" | bc -l) -eq 0 ]; then
    echo "Error: Python $required_version or higher is required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install Poetry
echo "Installing Poetry..."
pip install poetry --quiet
echo "✓ Poetry installed"
echo ""

# Configure Poetry to use the virtual environment
echo "Configuring Poetry..."
poetry config virtualenvs.in-project true
poetry config virtualenvs.create false
echo "✓ Poetry configured"
echo ""

# Install dependencies
echo "Installing dependencies with Poetry..."
echo "This may take a few minutes..."
poetry install
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created (please update with your credentials)"
    echo ""
fi

# Create output directory
if [ ! -d "output" ]; then
    echo "Creating output directory..."
    mkdir -p output
    echo "✓ Output directory created"
    echo ""
fi

# Verify installation
echo "Verifying installation..."
python -c "import firs_einvoice; print(f'✓ FIRS E-Invoice SDK v{firs_einvoice.__version__} installed successfully')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠ Warning: Could not verify installation. Try running: poetry install"
fi
echo ""

echo "==========================================="
echo "Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the example:"
echo "  poetry run python examples/simple_invoice.py"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
echo "==========================================="