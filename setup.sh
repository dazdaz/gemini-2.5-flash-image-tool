#!/bin/bash

# Gemini Image Generator - Setup Script
# This script sets up the virtual environment and installs dependencies

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "=================================================="
echo "  Gemini Image Generator - Setup Script"
echo "=================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

log_success "Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
log_info "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
log_success "Dependencies installed"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    log_warning "gcloud CLI not found. Please install Google Cloud SDK."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
else
    log_success "gcloud CLI found"
    
    # Check if user is authenticated
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        log_success "gcloud authentication found"
    else
        log_warning "Not authenticated with gcloud. Run: gcloud auth login"
    fi
    
    # Check if application default credentials are set
    if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
        log_success "Application default credentials found"
    else
        log_warning "Application default credentials not found. Run: gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform"
    fi
fi

echo ""
log_success "Setup complete!"
echo ""
echo "To use the tool:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Set your project: export GOOGLE_CLOUD_PROJECT=your-project-id"
echo "  3. Run the tool: python aiphoto-tool.py generate output.jpg -p 'A sunset'"
echo ""
echo "For first-time setup, also run:"
echo "  ./01-setup-iam-permission.sh"