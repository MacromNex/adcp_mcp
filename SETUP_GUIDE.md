# ADCP MCP Setup Guide

## Quick Start

For most users, simply run:

```bash
bash quick_setup.sh
```

## Prerequisites

### 1. Install conda/mamba

If you don't have conda or mamba installed:

**Option A: Install Miniforge (Recommended)**
```bash
# Download and install miniforge
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh

# Restart your shell or run:
source ~/.bashrc
```

**Option B: Add existing conda/mamba to PATH**
If you have conda/mamba installed but it's not in PATH:
```bash
# Add to your ~/.bashrc
echo 'export PATH="/home/xux/miniforge3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install git gcc make
```

**CentOS/RHEL/Fedora:**
```bash
# CentOS/RHEL
sudo yum install git gcc make

# Fedora
sudo dnf install git gcc make
```

## Setup Options

### Full Setup (Recommended for first time)
```bash
bash quick_setup.sh
```

### Skip Existing Components
If you've already run setup before and want to skip certain steps:

```bash
# Skip environment creation (if env/ already exists)
bash quick_setup.sh --skip-env

# Skip repository cloning (if repo/ADCP already exists)
bash quick_setup.sh --skip-repo

# Skip binary compilation (if adcp_Linux-x86_64 already exists)
bash quick_setup.sh --skip-build

# Combine flags
bash quick_setup.sh --skip-env --skip-build
```

### Test Before Setup
```bash
# Validate that setup will work
bash test_setup.sh
```

## After Setup

### Register with Claude Code
```bash
claude mcp add adcp-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

### Test Installation
```bash
# Test MCP server
./env/bin/python src/server.py

# Test scripts directly
./env/bin/python scripts/conformational_sampling.py --input GPGPGPGP --dry-run
```

## Troubleshooting

### Environment Issues

**Problem**: `mamba/conda not found`
```bash
# Check if installed
ls /home/xux/miniforge3/bin/mamba

# Add to PATH temporarily
export PATH="/home/xux/miniforge3/bin:$PATH"

# Or use full path in setup
/home/xux/miniforge3/bin/mamba --version
```

**Problem**: `Permission denied` when running setup
```bash
chmod +x quick_setup.sh
bash quick_setup.sh
```

**Problem**: `gcc not found`
```bash
# Install build essentials
sudo apt-get install build-essential  # Ubuntu/Debian
sudo yum groupinstall "Development Tools"  # CentOS/RHEL
```

### Build Issues

**Problem**: ADCP compilation fails
```bash
# Clean and retry
cd repo/ADCP
make clean
make

# Check for missing headers
sudo apt-get install python3-dev  # Ubuntu/Debian
```

**Problem**: Environment already exists and corrupted
```bash
# Remove and recreate
rm -rf env
bash quick_setup.sh
```

### MCP Registration Issues

**Problem**: Claude Code doesn't see the server
```bash
# Check registration
claude mcp list

# Re-register
claude mcp remove adcp-tools
claude mcp add adcp-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

## Manual Installation (Alternative)

If the quick setup fails, you can install manually:

```bash
# 1. Create environment
mamba create -p ./env python=3.12 -y
mamba activate ./env

# 2. Install dependencies
pip install --upgrade pip
pip install numpy loguru click pandas tqdm
pip install --force-reinstall fastmcp

# 3. Clone repository (if needed)
git clone https://github.com/ccsb-scripps/adcp.git repo/ADCP

# 4. Build binary
cd repo/ADCP
make clean && make
cp adcp_Linux-x86_64 ../../
cd ../../

# 5. Copy data files
cp repo/ADCP/ramaprob.data ./
cp repo/ADCP/runADCP.py ./

# 6. Test
./env/bin/python -c "from src.server import mcp; print('OK')"
```

## Performance Notes

- **Setup time**: 5-10 minutes for full installation
- **Disk space**: ~500 MB for environment + binary
- **Memory**: ~100 MB for MCP server
- **CPU**: ADCP jobs are CPU-intensive, recommend multiple cores for batch processing

## Next Steps

After successful setup, see:
- `README.md` - Full documentation and usage examples
- `examples/` - Sample scripts and data
- `tests/run_integration_tests.py` - Integration tests