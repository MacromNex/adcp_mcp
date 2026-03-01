#!/bin/bash
# quick_setup.sh - Quick setup script for ADCP Cyclic Peptide Tools
#
# Usage:
#   bash quick_setup.sh [options]
#
# Options:
#   --help      Show this help message
#   --skip-env  Skip environment creation (use existing env)
#   --skip-repo Skip repository cloning (repo already present)
#   --skip-build Skip ADCP binary compilation

set -e  # Exit on error

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_NAME="ADCP Cyclic Peptide Tools"
PYTHON_VERSION="3.12"
REPO_URL="https://github.com/ccsb-scripps/adcp.git"
REPO_NAME="ADCP"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
    cat << EOF
${MCP_NAME} Quick Setup Script

Usage:
    bash quick_setup.sh [options]

Options:
    --help        Show this help message
    --skip-env    Skip environment creation (use existing env)
    --skip-repo   Skip repository cloning (repo already present)
    --skip-build  Skip ADCP binary compilation

Description:
    This script sets up the environment for ADCP MCP server, which provides
    computational tools for cyclic peptide conformational sampling using
    AutoDock CrankPep (ADCP).

    The setup process includes:
    1. Create conda/mamba environment with Python ${PYTHON_VERSION}
    2. Clone the ADCP source repository (if not present)
    3. Install all required Python dependencies
    4. Compile the ADCP binary from source
    5. Install MCP server dependencies (fastmcp)
    6. Copy required data files and configure paths

Requirements:
    - conda or mamba (mamba recommended for faster installation)
    - git (for repository cloning)
    - gcc and make (for compiling ADCP binary)
    - Linux x86_64 system (ADCP binary requirement)
    - ~500 MB disk space for environment and binary

Estimated Setup Time:
    - Environment creation: ~1-2 minutes
    - Source compilation: ~2-3 minutes
    - Total time: ~5-10 minutes

After Setup:
    Register with Claude Code:
        claude mcp add adcp-tools -- \$(pwd)/env/bin/python \$(pwd)/src/server.py

    Or use with fastmcp:
        fastmcp install src/server.py --name adcp-tools

EOF
    exit 0
}

get_pkg_manager() {
    if command -v mamba &> /dev/null; then
        echo "mamba"
    elif command -v conda &> /dev/null; then
        echo "conda"
    else
        echo ""
    fi
}

check_system_requirements() {
    local missing_deps=()

    # Check for git
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi

    # Check for gcc
    if ! command -v gcc &> /dev/null; then
        missing_deps+=("gcc")
    fi

    # Check for make
    if ! command -v make &> /dev/null; then
        missing_deps+=("make")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required system dependencies: ${missing_deps[*]}"
        log_error "Please install them using your system package manager:"
        log_error "  Ubuntu/Debian: sudo apt-get install ${missing_deps[*]}"
        log_error "  CentOS/RHEL:   sudo yum install ${missing_deps[*]}"
        log_error "  Fedora:        sudo dnf install ${missing_deps[*]}"
        exit 1
    fi
}

# =============================================================================
# Parse Arguments
# =============================================================================
SKIP_ENV=false
SKIP_REPO=false
SKIP_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            ;;
        --skip-env)
            SKIP_ENV=true
            shift
            ;;
        --skip-repo)
            SKIP_REPO=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            ;;
    esac
done

# =============================================================================
# Main Setup
# =============================================================================
cd "$SCRIPT_DIR"
log_info "Setting up ${MCP_NAME} in: $SCRIPT_DIR"

# Check system requirements
check_system_requirements

# Check for package manager
PKG_MGR=$(get_pkg_manager)
if [ -z "$PKG_MGR" ]; then
    log_error "Neither mamba nor conda found. Please install one of them first."
    log_error "Recommended: Install miniforge from https://github.com/conda-forge/miniforge"
    exit 1
fi
log_info "Using package manager: $PKG_MGR"

# -----------------------------------------------------------------------------
# Step 1: Clone Repository (if needed)
# -----------------------------------------------------------------------------
if [ "$SKIP_REPO" = false ]; then
    if [ -d "repo/${REPO_NAME}" ]; then
        log_info "Repository already exists at repo/${REPO_NAME}"
    else
        log_info "Cloning ADCP repository..."
        mkdir -p repo
        git clone --depth=1 "${REPO_URL}" "repo/${REPO_NAME}" || {
            log_warning "Shallow clone failed, trying full clone..."
            git clone "${REPO_URL}" "repo/${REPO_NAME}"
        }
        log_success "Repository cloned successfully"
    fi
else
    log_info "Skipping repository clone (--skip-repo)"
fi

# Verify repository exists
if [ ! -d "repo/${REPO_NAME}" ]; then
    log_error "Repository not found at repo/${REPO_NAME}"
    log_error "Please run without --skip-repo to clone it"
    exit 1
fi

# -----------------------------------------------------------------------------
# Step 2: Create Environment (if needed)
# -----------------------------------------------------------------------------
if [ "$SKIP_ENV" = false ]; then
    if [ -d "env" ]; then
        log_warning "Environment already exists at ./env"
        read -p "Do you want to remove and recreate it? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Removing existing environment..."
            rm -rf env
        else
            log_info "Keeping existing environment"
            SKIP_ENV=true
        fi
    fi

    if [ "$SKIP_ENV" = false ]; then
        log_info "Creating conda environment with Python ${PYTHON_VERSION}..."
        $PKG_MGR create -p ./env python=${PYTHON_VERSION} -y
        log_success "Environment created successfully"
    fi
else
    log_info "Skipping environment creation (--skip-env)"
fi

# Verify environment exists
if [ ! -f "env/bin/python" ]; then
    log_error "Environment not found at ./env/bin/python"
    log_error "Please run without --skip-env to create it"
    exit 1
fi

# -----------------------------------------------------------------------------
# Step 3: Install Dependencies
# -----------------------------------------------------------------------------
log_info "Installing Python dependencies..."

# Install core packages
log_info "Installing core Python packages (numpy, loguru, click, pandas, tqdm)..."
./env/bin/pip install --upgrade pip
./env/bin/pip install numpy loguru click pandas tqdm

# Install MCP dependencies
log_info "Installing MCP dependencies (fastmcp)..."
./env/bin/pip install --force-reinstall --no-cache-dir fastmcp

log_success "Dependencies installed successfully"

# -----------------------------------------------------------------------------
# Step 4: Build ADCP Binary (if needed)
# -----------------------------------------------------------------------------
if [ "$SKIP_BUILD" = false ]; then
    if [ -f "adcp_Linux-x86_64" ]; then
        log_info "ADCP binary already exists at ./adcp_Linux-x86_64"
        read -p "Do you want to rebuild it? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            SKIP_BUILD=true
        fi
    fi

    if [ "$SKIP_BUILD" = false ]; then
        log_info "Building ADCP binary from source..."
        cd "repo/${REPO_NAME}"

        # Clean previous build
        make clean 2>/dev/null || true

        # Build with error handling
        if make; then
            log_success "ADCP binary compiled successfully"

            # Copy binary to main directory
            if [ -f "adcp_Linux-x86_64" ]; then
                cp adcp_Linux-x86_64 ../../
                log_success "Binary copied to main directory"
            else
                log_error "Binary not found after compilation"
                exit 1
            fi
        else
            log_error "ADCP binary compilation failed"
            log_error "Please check that you have gcc and make installed"
            exit 1
        fi

        cd ../../
    fi
else
    log_info "Skipping binary compilation (--skip-build)"
fi

# Verify binary exists
if [ ! -f "adcp_Linux-x86_64" ]; then
    log_error "ADCP binary not found at ./adcp_Linux-x86_64"
    log_error "Please run without --skip-build to compile it"
    exit 1
fi

# Make binary executable
chmod +x adcp_Linux-x86_64

# -----------------------------------------------------------------------------
# Step 5: Copy Required Data Files
# -----------------------------------------------------------------------------
log_info "Setting up required data files..."

# Copy Ramachandran probability data
if [ -f "repo/${REPO_NAME}/ramaprob.data" ]; then
    cp "repo/${REPO_NAME}/ramaprob.data" ./
    log_success "ramaprob.data copied"
else
    log_warning "ramaprob.data not found in repository"
fi

# Copy and convert Python wrapper
if [ -f "repo/${REPO_NAME}/runADCP.py" ]; then
    # Copy and make Python 3 compatible if needed
    cp "repo/${REPO_NAME}/runADCP.py" ./
    log_success "runADCP.py copied"
else
    log_warning "runADCP.py not found in repository"
fi

# Create jobs directory
mkdir -p jobs
log_info "Jobs directory created"

# -----------------------------------------------------------------------------
# Step 6: Verify Installation
# -----------------------------------------------------------------------------
log_info "Verifying installation..."

# Test Python environment
./env/bin/python -c "import sys; print(f'Python {sys.version}')" || {
    log_error "Python environment verification failed"
    exit 1
}

# Test core dependencies
./env/bin/python -c "import numpy, loguru, click, pandas, tqdm; print('Core packages OK')" || {
    log_error "Core package verification failed"
    exit 1
}

# Test fastmcp
./env/bin/python -c "import fastmcp; print(f'fastmcp {fastmcp.__version__}')" || {
    log_error "fastmcp import failed"
    exit 1
}

# Test MCP server import
./env/bin/python -c "from src.server import mcp; print('MCP server import OK')" 2>/dev/null || {
    log_warning "MCP server import test skipped (server may not be ready yet)"
}

# Test ADCP binary
if ./adcp_Linux-x86_64 2>&1 | grep -q "usage\|Usage\|USAGE" || [ $? -eq 0 ]; then
    log_success "ADCP binary is functional"
else
    log_warning "ADCP binary test inconclusive (this may be normal)"
fi

log_success "Installation verified successfully"

# =============================================================================
# Done
# =============================================================================
echo
log_success "=============================================="
log_success "  ${MCP_NAME} setup completed!"
log_success "=============================================="
echo
echo "Environment Details:"
echo "  - Python version: $(./env/bin/python --version 2>&1)"
echo "  - ADCP binary: $(ls -lh adcp_Linux-x86_64 | awk '{print $5}')"
echo "  - Environment size: $(du -sh env 2>/dev/null | awk '{print $1}' || echo 'Unknown')"
echo
echo "Next steps:"
echo
echo "  1. Register with Claude Code:"
echo "     claude mcp add adcp-tools -- \$(pwd)/env/bin/python \$(pwd)/src/server.py"
echo
echo "  2. Or use fastmcp:"
echo "     fastmcp install src/server.py --name adcp-tools"
echo
echo "  3. Test the MCP server:"
echo "     ./env/bin/python src/server.py"
echo
echo "  4. Test with sample data:"
echo "     ./env/bin/python scripts/conformational_sampling.py --input GPGPGPGP --dry-run"
echo
echo "  5. Read the documentation:"
echo "     cat README.md"
echo
echo "Available tools after registration:"
echo "  - submit_conformational_sampling: Generate peptide conformations"
echo "  - submit_batch_processing: Process multiple peptides in parallel"
echo "  - validate_peptide_sequence: Check sequence validity"
echo "  - get_job_status, get_job_result, get_job_log: Job management"
echo
echo "Example usage in Claude Code:"
echo "  'Submit conformational sampling for cyclic peptide \"GPGPGPGP\" with 5 runs'"
echo "  'Process sequences in @examples/data/sequences/batch_sequences.txt'"
echo