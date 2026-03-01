#!/bin/bash
# test_setup.sh - Test the quick_setup.sh script functionality
#
# This script validates that quick_setup.sh will work correctly
# without actually running the full setup process.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[TEST INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[TEST PASS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[TEST WARN]${NC} $1"; }
log_error() { echo -e "${RED}[TEST FAIL]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Testing ADCP Quick Setup Script"
echo "=========================================="
echo

# Test 1: Check script exists and is executable
log_info "Test 1: Checking quick_setup.sh exists and is executable"
if [ -f "quick_setup.sh" ] && [ -x "quick_setup.sh" ]; then
    log_success "quick_setup.sh exists and is executable"
else
    log_error "quick_setup.sh not found or not executable"
    exit 1
fi

# Test 2: Test help functionality
log_info "Test 2: Testing --help option"
if bash quick_setup.sh --help | grep -q "ADCP Cyclic Peptide Tools"; then
    log_success "Help text displays correctly"
else
    log_error "Help text is missing or malformed"
    exit 1
fi

# Test 3: Check system requirements
log_info "Test 3: Checking system requirements"
missing_deps=()

if ! command -v git &> /dev/null; then
    missing_deps+=("git")
fi

if ! command -v gcc &> /dev/null; then
    missing_deps+=("gcc")
fi

if ! command -v make &> /dev/null; then
    missing_deps+=("make")
fi

# Check for conda/mamba
has_conda=false
if command -v mamba &> /dev/null; then
    log_success "mamba found (recommended)"
    has_conda=true
elif command -v conda &> /dev/null; then
    log_success "conda found"
    has_conda=true
else
    missing_deps+=("conda/mamba")
fi

if [ ${#missing_deps[@]} -eq 0 ]; then
    log_success "All system requirements satisfied"
else
    log_warning "Missing system dependencies: ${missing_deps[*]}"
    log_warning "Setup script will fail without these dependencies"
fi

# Test 4: Check required directory structure
log_info "Test 4: Checking project structure"
required_dirs=("src" "scripts" "examples" "configs")
required_files=("README.md" "src/server.py")

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        log_success "Directory $dir exists"
    else
        log_error "Required directory $dir missing"
        exit 1
    fi
done

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        log_success "File $file exists"
    else
        log_error "Required file $file missing"
        exit 1
    fi
done

# Test 5: Check example data files
log_info "Test 5: Checking example data files"
if [ -f "examples/data/sequences/batch_sequences.txt" ]; then
    seq_count=$(grep -v '^#' examples/data/sequences/batch_sequences.txt | grep -v '^$' | wc -l)
    if [ "$seq_count" -gt 0 ]; then
        log_success "Sample sequences file exists with $seq_count sequences"
    else
        log_warning "Sample sequences file exists but appears empty"
    fi
else
    log_warning "Sample sequences file not found (will affect testing)"
fi

# Test 6: Check if environment already exists
log_info "Test 6: Checking existing installation"
if [ -d "env" ]; then
    if [ -f "env/bin/python" ]; then
        python_version=$(./env/bin/python --version 2>&1)
        log_info "Environment already exists: $python_version"
    else
        log_warning "Environment directory exists but appears corrupted"
    fi
else
    log_info "No existing environment found (fresh installation)"
fi

# Test 7: Check if ADCP binary exists
if [ -f "adcp_Linux-x86_64" ]; then
    if [ -x "adcp_Linux-x86_64" ]; then
        binary_size=$(ls -lh adcp_Linux-x86_64 | awk '{print $5}')
        log_info "ADCP binary already exists: $binary_size"
    else
        log_warning "ADCP binary exists but is not executable"
    fi
else
    log_info "No existing ADCP binary found (will be compiled)"
fi

# Test 8: Check repository
if [ -d "repo/ADCP" ]; then
    if [ -f "repo/ADCP/Makefile" ]; then
        log_success "ADCP repository exists with Makefile"
    else
        log_error "ADCP repository exists but missing Makefile"
        exit 1
    fi
else
    log_info "ADCP repository not found (will be cloned)"
fi

# Test 9: Test argument parsing
log_info "Test 9: Testing argument parsing"
test_args=("--skip-env" "--skip-repo" "--skip-build")
for arg in "${test_args[@]}"; do
    if bash quick_setup.sh "$arg" --help 2>/dev/null | grep -q "ADCP Cyclic Peptide Tools"; then
        log_success "Argument $arg parsed correctly"
    else
        log_error "Argument $arg parsing failed"
        exit 1
    fi
done

# Test 10: Estimate disk space
log_info "Test 10: Checking disk space"
available_space=$(df . | tail -1 | awk '{print $4}')
available_mb=$((available_space / 1024))
if [ "$available_mb" -gt 1000 ]; then
    log_success "Sufficient disk space available: ${available_mb}MB"
else
    log_warning "Low disk space: ${available_mb}MB (recommend >1GB)"
fi

echo
echo "=========================================="
echo "Test Summary"
echo "=========================================="

if [ ${#missing_deps[@]} -eq 0 ]; then
    log_success "All tests passed! quick_setup.sh should work correctly."
    echo
    echo "To run the setup:"
    echo "  bash quick_setup.sh"
    echo
    echo "To run with existing components:"
    echo "  bash quick_setup.sh --skip-env    # if environment exists"
    echo "  bash quick_setup.sh --skip-repo   # if repository exists"
    echo "  bash quick_setup.sh --skip-build  # if binary exists"
    echo
    echo "Estimated setup time: 5-10 minutes"
else
    log_warning "Setup will fail due to missing dependencies:"
    for dep in "${missing_deps[@]}"; do
        echo "  - $dep"
    done
    echo
    echo "Install missing dependencies first, then run:"
    echo "  bash quick_setup.sh"
fi

echo