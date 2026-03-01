# ADCP MCP (AutoDock CrankPep Model Context Protocol)

A specialized MCP tool for cyclic peptide docking and conformational analysis using AutoDock CrankPep (ADCP). This tool enables automated cyclic peptide docking using AutoDock CrankPep, conformer generation, and flexible backbone handling for drug discovery and peptide design applications.

## Quick Start

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+ (tested with 3.12.12)
- GCC compiler and make (for building C binary)
- Git (for repository management)

## Verified Examples

These examples have been tested and verified to work:

### Example 1: Conformational Sampling of Cyclic Peptides
```bash
# Activate environment
./env/bin/python

# Run conformational sampling for a cyclic peptide
python examples/use_case_4_conformational_sampling.py \
  --sequence GPGPGPGP \
  --numsteps 1000 \
  --nbruns 2 \
  --output results/conformations

# Expected output: PDB files with peptide conformations and energy data
```

### Example 2: Direct ADCP Binary Usage
```bash
# Simple peptide folding (no receptor)
./adcp_Linux-x86_64 -r 1x1000 -t 1 GPGPGPGP \
  -p "Bias=NULL,Opt=1,1,0,0" -o simple_folding.pdb

# Cyclic peptide conformational sampling
./adcp_Linux-x86_64 -r 1x5000 -t 1 GPGPGPGP \
  -p "Bias=NULL,external2=4,con,2,1.0,Opt=1,0.25,0.75,0.0" \
  -o cyclic_sampling.pdb

# Expected output: PDB file with final structure and simulation log
```

### Example 3: Batch Processing (Dry Run)
```bash
# Test batch processing setup
python examples/use_case_5_batch_processing.py --dry-run --max-workers 2

# Expected output: List of 21 parsed sequences ready for processing
```

## Important Notes

⚠️ **Receptor-based docking (UC-001, UC-002, UC-003) requires AGFR-generated .trg target files that are not included. These use cases will fail without proper receptor files.**

✅ **Conformational sampling (UC-004) works completely and is scientifically valuable for studying peptide flexibility and folding.**

### Installation

The following commands were tested and verified to work:

```bash
# Navigate to the MCP directory
cd /mnt/data/done_projects/2026/BioMolMCP/CycPepMCP/tool-mcps/adcp_mcp

# Step 1: Create the conda environment
# (Using mamba from miniforge3 installation)
/home/xux/miniforge3/bin/mamba create -p ./env python=3.12 -y

# Step 2: Activate the environment
# Source conda initialization if needed
source /home/xux/miniforge3/etc/profile.d/conda.sh
conda activate ./env

# Step 3: Install Python dependencies
pip install --upgrade pip
pip install numpy loguru click pandas tqdm
pip install --force-reinstall --no-cache-dir fastmcp

# Step 4: Build ADCP binary from C source
cd repo/ADCP
make clean  # Clean any previous builds
make        # Build the binary

# Step 5: Copy required files to MCP root
cd ../../  # Back to MCP root
cp repo/ADCP/adcp_Linux-x86_64 ./
cp repo/ADCP/ramaprob.data ./
cp repo/ADCP/runADCP.py ./

# Step 6: Convert Python wrapper to Python 3 (if needed)
# The runADCP.py was converted from Python 2 to Python 3
# Using 2to3 tool and manual fixes for compatibility
```

### Build Fixes Applied

During the build process, the following issue was encountered and fixed:

**Issue**: Multiple definition errors in C compilation
```
error: multiple definition of `centerX'; first defined here
```

**Solution**: Modified `repo/ADCP/energy.h` to use `extern` declarations and added actual definitions in `repo/ADCP/energy.c`:

```c
// In energy.h - changed to extern declarations
extern double centerX, centerY, centerZ, spacing;
extern int NX, NY, NZ;
extern double targetBest, currTargetEnergy;
extern double *gridmapvalues[9];
extern int transPtsCount;
extern double *Xpts, *Ypts, *Zpts;
extern double *ramaprob, *alaprob, *glyprob;

// In energy.c - added actual definitions
double centerX, centerY, centerZ, spacing;
int NX, NY, NZ;
double targetBest, currTargetEnergy;
double *gridmapvalues[9];
int transPtsCount;
double *Xpts, *Ypts, *Zpts;
double *ramaprob, *alaprob, *glyprob;
```

### Python 2 to 3 Conversion

The original `runADCP.py` was written for Python 2. Conversion steps:

1. Used `2to3` tool for initial conversion
2. Manually fixed remaining print statements
3. Updated argparse version parameter handling
4. Fixed string formatting and iteration issues

### Running the MCP Server

**NEW: Step 7 Claude Code Integration** ✅ **TESTED & READY**

The ADCP MCP server has been fully tested and integrated with Claude Code:

```bash
# 1. Register with Claude Code (one-time setup)
claude mcp add adcp-tools -- $(which python) $(pwd)/src/server.py

# 2. Start Claude Code and verify server appears
claude

# 3. Test server with basic prompts:
# "What tools are available from adcp-tools?"
# "Use get_server_info to show server capabilities"
# "Submit conformational sampling for 'GRGDSP' with 5 runs"
```

**✅ Integration Test Results**:
- All 7 core tests passed (100% success rate)
- Server imports and starts correctly
- ADCP binary available and functional
- Job management system operational
- Example data files present and valid

**Available MCP Tools**:
- **Job Management**: `get_job_status`, `get_job_result`, `get_job_log`, `cancel_job`, `list_jobs`
- **Submit Operations**: `submit_conformational_sampling`, `submit_batch_processing`
- **Utilities**: `validate_peptide_sequence`, `check_adcp_binary`, `get_server_info`

**Quick Test Commands**:
```bash
# Test server manually
python -c "from src.server import mcp; print('Server OK')"

# Test in development mode
fastmcp dev src/server.py

# Run integration tests
python tests/run_integration_tests.py
```

**Production Usage Examples**:
```
1. "Submit conformational sampling for cyclic peptide 'GRGDSP'"
2. "Check the status of all running jobs"
3. "Get results from completed job <job_id>"
4. "Process batch file 'examples/data/sequences/batch_sequences.txt'"
```

📋 **See Complete Testing Documentation**:
- Test prompts: `tests/test_prompts.md` (30+ test scenarios)
- Integration report: `reports/step7_integration.md`
- Tool documentation: `reports/step6_mcp_tools.md`

**Legacy Python Wrapper** (Original)

```bash
# Test ADCP functionality
python runADCP.py --help

# Test with a simple cyclic peptide (dry run)
python runADCP.py -s GPGPGPGP --cyclic --dryRun --output test_output
```

## Verified Use Cases

The following scripts have been tested and work with the installed environment:

| Script | Description | Example Command |
|--------|-------------|-----------------|
| `examples/use_case_1_cyclic_peptide_docking.py` | Basic cyclic peptide sequence docking | `python examples/use_case_1_cyclic_peptide_docking.py --sequence GPGPGPGP --dry-run` |
| `examples/use_case_2_disulfide_cyclic_docking.py` | Disulfide-bridged cyclic peptide docking | `python examples/use_case_2_disulfide_cyclic_docking.py --sequence CGPGPGPGC --dry-run` |
| `examples/use_case_3_structure_based_docking.py` | Structure-based peptide docking from PDB | `python examples/use_case_3_structure_based_docking.py --input examples/data/structures/sample_peptide.pdb --dry-run` |
| `examples/use_case_4_conformational_sampling.py` | Conformational sampling without receptor | `python examples/use_case_4_conformational_sampling.py --sequence CGPGPGPGC --dry-run` |
| `examples/use_case_5_batch_processing.py` | Batch processing multiple sequences | `python examples/use_case_5_batch_processing.py --sequences examples/data/sequences/batch_sequences.txt --dry-run` |

## Installed Packages

Key packages installed in `./env`:
- **numpy=2.4.2** (essential for ADCP)
- **loguru=0.7.3** (logging)
- **click=8.3.1** (CLI interfaces)
- **pandas=3.0.1** (data processing)
- **tqdm=4.67.3** (progress bars)
- **fastmcp=3.0.2** (MCP framework)
- **mcp=1.26.0** (core MCP library)
- **pydantic=2.12.5** (data validation)
- **httpx=0.28.1** (HTTP client)
- **uvicorn=0.41.0** (ASGI server)

Additional dependencies: authlib, cyclopts, jsonschema, rich, watchfiles, websockets, and others (automatically installed)

## ADCP Binary Information

- **Binary**: `adcp_Linux-x86_64` (1,169,968 bytes)
- **Compiler**: GCC with -std=c99 -Wall -O2 flags
- **Status**: Successfully compiled and functional
- **Required data**: `ramaprob.data` (1,000,181 bytes - Ramachandran probabilities)

## Directory Structure

```
./
├── README.md               # This file
├── requirements.txt        # Python dependencies (if created)
├── env/                    # Main conda environment (Python 3.12)
├── adcp_Linux-x86_64       # Compiled ADCP binary
├── ramaprob.data           # Required probability data
├── runADCP.py              # Python wrapper (converted to Python 3)
├── src/                    # **NEW: Step 6 MCP Server**
│   ├── server.py           # Main MCP server with all tools
│   ├── utils.py            # Shared utilities
│   └── jobs/               # Job management system
│       ├── manager.py      # Async job execution
│       └── store.py        # Job persistence
├── scripts/                # **NEW: Clean ADCP scripts from Step 5**
│   ├── conformational_sampling.py  # Single sequence sampling
│   ├── batch_processing.py         # Multiple sequence processing
│   └── README.md           # Script documentation
├── configs/                # Configuration files
│   ├── conformational_sampling_config.json
│   ├── batch_processing_config.json
│   └── default_config.json
├── jobs/                   # **NEW: Job storage (auto-created by MCP server)**
├── examples/               # Use case scripts and demo data
│   ├── use_case_1_cyclic_peptide_docking.py
│   ├── use_case_2_disulfide_cyclic_docking.py
│   ├── use_case_3_structure_based_docking.py
│   ├── use_case_4_conformational_sampling.py
│   ├── use_case_5_batch_processing.py
│   ├── data/
│   │   ├── sequences/      # Sample cyclic peptide sequences
│   │   │   ├── batch_sequences.txt
│   │   │   └── cyclic_peptides.smi
│   │   ├── structures/     # Sample 3D structures
│   │   │   └── sample_peptide.pdb
│   │   └── targets/        # Receptor target files (.trg)
│   │       └── README_targets.md
│   └── README.md           # Examples documentation
├── reports/                # Documentation and reports
│   ├── step3_environment.md
│   ├── step3_use_cases.md
│   └── step6_mcp_tools.md  # **NEW: Complete MCP tool documentation**
└── repo/                   # Original ADCP repository
    └── ADCP/               # C source code and build files
```

## Key Features

### Cyclic Peptide Capabilities
- **Backbone cyclization**: Connect N and C termini
- **Disulfide bridges**: CYS-CYS bond constraints
- **Flexible backbone**: Monte Carlo conformational sampling
- **Size range**: Optimized for 6-20 amino acid peptides

### Docking and Sampling
- **AutoDock energy landscape**: Uses AutoDock grid-based energy evaluation
- **Multiple conformational search**: Independent parallel runs
- **Constraint handling**: Cyclic and disulfide bridge constraints
- **Batch processing**: High-throughput virtual screening

### Input/Output Formats
- **Input**: Amino acid sequences, PDB structures, .trg receptor files
- **Output**: PDB structures with energy rankings
- **Constraints**: Flexible parameter tuning for different peptide types

## Troubleshooting

### Known Issues and Solutions

#### 1. Environment Activation Issues
**Problem**: `EnvironmentLocationNotFound`
**Solution**: Use full path to activate: `conda activate ./env`

#### 2. Binary Not Found
**Problem**: `./adcp_Linux-x86_64: No such file or directory`
**Solution**: Ensure binary was copied to MCP root directory

#### 3. Python Syntax Errors
**Problem**: `SyntaxError: Missing parentheses in call to 'print'`
**Solution**: Already fixed in provided runADCP.py (converted to Python 3)

#### 4. No Receptor Files
**Problem**: `ERROR: no receptor files found`
**Solution**: For real docking, need .trg files from AGFR. Use `--dry-run` for testing

#### 5. Memory Issues
**Problem**: Long runtime or memory errors
**Solution**: Reduce MC steps (`-n`) or number of runs (`-N`)

### Verification Commands

```bash
# Test environment
conda activate ./env
python -c "import numpy, fastmcp; print('Environment OK')"

# Test ADCP binary
./adcp_Linux-x86_64 2>&1 | head -5

# Test Python wrapper
python runADCP.py --help

# Test example use case
python examples/use_case_1_cyclic_peptide_docking.py --sequence GPGPGPGP --dry-run
```

## Requirements for Real Docking

For actual docking (not dry runs), you need:

1. **Receptor target files**: Generated using AGFR (AutoDock Grid Receptor)
   ```bash
   agfr -r receptor.pdb -o receptor.trg
   ```

2. **Sufficient computational resources**:
   - Recommended: 4+ CPU cores
   - RAM: 2-8 GB depending on peptide size and runs
   - Time: Minutes to hours per sequence

3. **Input validation**:
   - Peptide sequences with standard amino acids
   - Reasonable length (6-20 residues recommended)
   - Proper file formats (PDB for structures, .trg for targets)

## Integration with MCP Framework

This ADCP installation is ready for conversion to MCP tools:

- **Standardized interfaces**: All use cases have consistent parameter handling
- **Error handling**: Comprehensive validation and error reporting
- **Modular design**: Each use case can be a separate MCP tool
- **Documentation**: Complete usage examples and API descriptions

See the `examples/` directory for detailed documentation and implementation examples.

## Citation

When using ADCP, please cite:
- AutoDock CrankPep (ADCP) - Available at adcp.scripps.edu
- Original CRANKITE: Podtelezhnikov, A.A. and Wild, D.L. (2008) Source Code Biol. Med., 3, 12.

## License

ADCP is available under the GNU LGPL v2.0 OpenSource license.
MCP integration code is provided for educational and research purposes.