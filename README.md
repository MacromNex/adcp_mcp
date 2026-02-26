# ADCP MCP

> MCP tools for cyclic peptide conformational sampling and analysis using AutoDock CrankPep

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

ADCP MCP provides computational tools for cyclic peptide analysis using AutoDock CrankPep (ADCP). This server enables conformational sampling, structural prediction, and batch processing of cyclic peptides for drug discovery and peptide design applications.

### Features
- 3D conformational sampling for cyclic peptides using Monte Carlo methods
- Batch processing for virtual screening of peptide libraries
- Flexible backbone handling with cyclic constraints
- Disulfide bridge support for cysteine-containing peptides
- Parallel processing for high-throughput analysis

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment
├── src/
│   └── server.py           # MCP server
├── scripts/
│   ├── conformational_sampling.py      # Single peptide conformational sampling
│   ├── batch_processing.py             # Multiple peptide batch processing
│   └── lib/                # Shared utilities
├── examples/
│   └── data/               # Demo data
│       ├── sequences/      # Sample cyclic peptide sequences
│       │   ├── batch_sequences.txt
│       │   └── cyclic_peptides.smi
│       ├── structures/     # Sample 3D structures
│       │   └── sample_peptide.pdb
│       └── targets/        # Receptor target files
│           └── README_targets.md
├── configs/                # Configuration files
│   ├── conformational_sampling_config.json
│   ├── batch_processing_config.json
│   └── default_config.json
├── jobs/                   # Job storage (auto-created)
├── adcp_Linux-x86_64       # ADCP binary
├── ramaprob.data           # Required probability data
└── repo/                   # Original repository
```

---

## Installation

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- GCC compiler and make (for C binary compilation)
- Linux x86_64 system (ADCP binary requirement)

### Create Environment

Following the information from `reports/step3_environment.md`, here's the verified installation procedure:

```bash
# Navigate to the MCP directory
cd /mnt/data/done_projects/2026/BioMolMCP/CycPepMCP/tool-mcps/adcp_mcp

# Create conda environment (use mamba if available)
/home/xux/miniforge3/bin/mamba create -p ./env python=3.12 -y
# or: conda create -p ./env python=3.12 -y

# Activate environment
source /home/xux/miniforge3/etc/profile.d/conda.sh
conda activate ./env
# or: mamba activate ./env

# Install Dependencies
pip install --upgrade pip
pip install numpy loguru click pandas tqdm
pip install --force-reinstall --no-cache-dir fastmcp

# Build ADCP binary (if not already built)
cd repo/ADCP
make clean && make
cd ../../

# Copy required files
cp repo/ADCP/adcp_Linux-x86_64 ./
cp repo/ADCP/ramaprob.data ./
cp repo/ADCP/runADCP.py ./
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/conformational_sampling.py` | Generate conformational ensembles for single cyclic peptides | See below |
| `scripts/batch_processing.py` | Process multiple peptide sequences in parallel | See below |

### Script Examples

#### Conformational Sampling

```bash
# Activate environment
conda activate ./env

# Run conformational sampling
python scripts/conformational_sampling.py \
  --input GPGPGPGP \
  --output results/conformations \
  --numsteps 50000 \
  --nbruns 10
```

**Parameters:**
- `--input, -i`: Peptide sequence (required)
- `--output, -o`: Output directory path (default: auto-generated)
- `--numsteps, -n`: Monte Carlo steps per run (default: 500,000)
- `--nbruns, -N`: Number of independent runs (default: 25)
- `--disulfide`: Enable disulfide constraints
- `--no-cyclic`: Disable cyclic constraints

#### Batch Processing

```bash
python scripts/batch_processing.py \
  --input examples/data/sequences/batch_sequences.txt \
  --output results/batch_output \
  --max-workers 4 \
  --numsteps 5000
```

**Parameters:**
- `--input, -i`: Input file with sequences (required)
- `--output, -o`: Output directory (default: auto-generated)
- `--max-workers, -w`: Parallel workers (default: 4)
- `--numsteps, -n`: MC steps per sequence (default: 1,000 for batch)
- `--timeout, -t`: Timeout per sequence in seconds (default: 300)

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name adcp-tools
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add adcp-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "adcp-tools": {
      "command": "/mnt/data/done_projects/2026/BioMolMCP/CycPepMCP/tool-mcps/adcp_mcp/env/bin/python",
      "args": ["/mnt/data/done_projects/2026/BioMolMCP/CycPepMCP/tool-mcps/adcp_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from adcp-tools?
```

#### Sequence Validation
```
Validate this cyclic peptide sequence: GPGPGPGP
```

#### Conformational Sampling
```
Submit conformational sampling for cyclic peptide GRGDSP with 10 runs and 50000 steps per run
```

#### Check Job Status
```
Check the status of job abc12345 and show me the logs if it's running
```

#### Batch Processing
```
Process the sequences in @examples/data/sequences/batch_sequences.txt using batch processing with 2 workers
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/sequences/batch_sequences.txt` | Reference a sequences file |
| `@configs/conformational_sampling_config.json` | Reference a config file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "adcp-tools": {
      "command": "/mnt/data/done_projects/2026/BioMolMCP/CycPepMCP/tool-mcps/adcp_mcp/env/bin/python",
      "args": ["/mnt/data/done_projects/2026/BioMolMCP/CycPepMCP/tool-mcps/adcp_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available?
> Submit conformational sampling for cyclic peptide GPGPGPGP
```

---

## Available Tools

### Job Management Tools

These tools manage long-running ADCP operations:

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_job_status` | Check job progress and current status | `job_id` |
| `get_job_result` | Get completed job results and output files | `job_id` |
| `get_job_log` | View job execution logs (with tail support) | `job_id`, `tail` (default: 50) |
| `cancel_job` | Cancel a running job | `job_id` |
| `list_jobs` | List all jobs (with optional status filter) | `status` (optional) |

### Submit Tools (Long Operations > 20 minutes)

These tools submit jobs for long-running ADCP operations:

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_conformational_sampling` | Generate conformations for single peptide | `sequence`, `numsteps`, `nbruns`, `cyclic`, `disulfide`, `output_dir`, `job_name` |
| `submit_batch_processing` | Process multiple peptides in parallel | `input_file`, `numsteps`, `max_workers`, `cyclic`, `disulfide`, `timeout`, `output_dir`, `job_name` |

### Utility Tools

These tools provide quick validation and system status:

| Tool | Description | Est. Runtime |
|------|-------------|--------------|
| `validate_peptide_sequence` | Validate amino acid sequence for ADCP | <1 sec |
| `check_adcp_binary` | Verify ADCP binary availability | <1 sec |
| `get_server_info` | Get server capabilities and status | <1 sec |

---

## Examples

### Example 1: Quick Conformational Sampling

**Goal:** Generate conformations for a cyclic peptide

**Using Script:**
```bash
python scripts/conformational_sampling.py \
  --input GPGPGPGP \
  --output results/conformations \
  --numsteps 10000 \
  --nbruns 5
```

**Using MCP (in Claude Code):**
```
Submit conformational sampling for cyclic peptide "GPGPGPGP" with 5 runs and 10000 steps per run. Name the job "test_peptide".
```

**Expected Output:**
- Multiple PDB files with conformational structures
- JSON metadata with sampling statistics
- Execution logs with energy information

### Example 2: Batch Processing Pipeline

**Goal:** Screen a library of cyclic peptides

**Using Script:**
```bash
python scripts/batch_processing.py \
  --input examples/data/sequences/batch_sequences.txt \
  --output results/library_screen \
  --max-workers 2 \
  --numsteps 5000
```

**Using MCP (in Claude Code):**
```
Process the sequences in @examples/data/sequences/batch_sequences.txt using batch processing.
Use 2 workers and 5000 steps per sequence. Name the job "library_screen".
```

### Example 3: Complete Workflow with Job Management

**Goal:** Submit job, monitor progress, and retrieve results

**Using MCP (in Claude Code):**
```
1. First validate the sequence "GRGDSP"
2. Submit conformational sampling for this sequence with 3 runs
3. Check the job status every few minutes
4. When complete, show me the results
```

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With |
|------|-------------|----------|
| `sequences/batch_sequences.txt` | 24 sample peptide sequences | `submit_batch_processing` |
| `sequences/cyclic_peptides.smi` | Sample sequences in SMILES-like format | Manual reference |
| `structures/sample_peptide.pdb` | Sample peptide structure | Structure-based operations |

### Sample Sequence File Format

```
# Comments start with #
cycpep_001	GPGPGP
cycpep_002	GGPGPG
PGPGPG
ACDEFGHIKL
```

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `conformational_sampling_config.json` | Single peptide sampling config | numsteps, nbruns, constraints |
| `batch_processing_config.json` | Batch processing config | max_workers, timeout, constraints |
| `default_config.json` | System defaults | validation rules, binary paths |

### Config Example

```json
{
  "sampling": {
    "numsteps": 50000,
    "nbruns": 10,
    "timeout_seconds": 600
  },
  "constraints": {
    "cyclic": true,
    "disulfide": false,
    "optimization_weights": [1, 0.25, 0.75, 0.0]
  },
  "validation": {
    "min_sequence_length": 6,
    "max_sequence_length": 20
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.12 -y
conda activate ./env
pip install numpy loguru click pandas tqdm fastmcp
```

**Problem:** ADCP binary not found
```bash
# Check binary exists
ls -la adcp_Linux-x86_64
# If missing, rebuild from source
cd repo/ADCP && make && cp adcp_Linux-x86_64 ../../
```

**Problem:** Import errors
```bash
# Verify installation
python -c "from src.server import mcp; print('Server OK')"
python -c "import numpy, fastmcp; print('Environment OK')"
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove adcp-tools
claude mcp add adcp-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

**Problem:** Invalid sequence error
```
Ensure your sequence contains only valid amino acids (ACDEFGHIKLMNPQRSTVWY)
and is between 6-20 amino acids long.
```

**Problem:** Tools not working
```bash
# Test server directly
python -c "
from src.server import mcp
print(list(mcp.list_tools().keys()))
"
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job log
python -c "
from src.jobs.manager import job_manager
print(job_manager.get_job_log('JOB_ID', tail=20))
"
```

**Problem:** Job failed
```
Use get_job_log with job_id "JOB_ID" and tail 100 to see error details
```

**Problem:** Long runtime
```
ADCP conformational sampling typically takes 20-60 minutes.
For testing, use fewer steps: numsteps=1000, nbruns=3
```

---

## Development

### Running Tests

```bash
# Activate environment
conda activate ./env

# Run integration tests
python tests/run_integration_tests.py

# Test individual scripts
python scripts/conformational_sampling.py --input GPGPGPGP --dry-run
python scripts/batch_processing.py --input examples/data/sequences/batch_sequences.txt --dry-run
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
fastmcp dev src/server.py

# Test with MCP client
python -c "
from fastmcp import FastMCP
from src.server import mcp
print(mcp.list_tools())
"
```

### Performance Tuning

| Use Case | Recommended Parameters |
|----------|------------------------|
| Quick Testing | `numsteps=1000, nbruns=3` |
| Development | `numsteps=10000, nbruns=5` |
| Production | `numsteps=500000, nbruns=25` |
| High-Throughput | `numsteps=5000, max_workers=cpu_cores` |

---

## License

ADCP is available under the GNU LGPL v2.0 OpenSource license.
MCP integration code is provided for educational and research purposes.

## Credits

Based on [AutoDock CrankPep (ADCP)](https://adcp.scripps.edu/)
Original repository: [ADCP GitHub](https://github.com/example/adcp)