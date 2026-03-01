# MCP Scripts for Cyclic Peptide Analysis

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only Python standard library (subprocess, pathlib, json, etc.)
2. **Self-Contained**: All necessary functions inlined, no complex external dependencies
3. **Configurable**: Parameters externalized to config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping
5. **Error Handling**: Comprehensive validation and error reporting

## Scripts

| Script | Description | Status | Config File |
|--------|-------------|--------|-------------|
| `conformational_sampling.py` | Single sequence conformational sampling | ✅ Working | `configs/conformational_sampling_config.json` |
| `batch_processing.py` | Multiple sequence batch processing | ✅ Working | `configs/batch_processing_config.json` |

## Quick Start

### Prerequisites

```bash
# Ensure ADCP binary is available
ls -la ../adcp_Linux-x86_64

# Ensure Python 3.6+ is available
python --version
```

### Single Sequence Conformational Sampling

```bash
# Basic usage
python scripts/conformational_sampling.py --input GPGPGPGP --output results/conformations.pdb

# With custom parameters
python scripts/conformational_sampling.py \
    --input CGPGPGC \
    --output results/disulfide_conformations \
    --numsteps 10000 \
    --nbruns 5 \
    --disulfide

# Using configuration file
python scripts/conformational_sampling.py \
    --input GPGPGPGP \
    --output results/conformations \
    --config configs/conformational_sampling_config.json

# Dry run (test without execution)
python scripts/conformational_sampling.py \
    --input GPGPGPGP \
    --output results/test \
    --dry-run
```

### Batch Processing Multiple Sequences

```bash
# Process sequences from file
python scripts/batch_processing.py \
    --input examples/data/sequences/batch_sequences.txt \
    --output results/batch_output

# With custom parameters
python scripts/batch_processing.py \
    --input sequences.txt \
    --output batch_results \
    --numsteps 5000 \
    --max-workers 4 \
    --timeout 600

# Sequential processing (no parallelization)
python scripts/batch_processing.py \
    --input sequences.txt \
    --output batch_results \
    --max-workers 1

# Dry run (validate sequences without processing)
python scripts/batch_processing.py \
    --input examples/data/sequences/batch_sequences.txt \
    --dry-run
```

## Input Formats

### Single Sequence
- **Amino acid sequence**: e.g., `GPGPGPGP`
- **File with sequences**: First valid sequence will be used

### Batch Sequences File
```
# Comments start with #
# Format: ID<tab>SEQUENCE or just SEQUENCE

cycpep_001	GPGPGP
cycpep_002	CGPGPC
GRGDPGG
```

## Output Formats

### Conformational Sampling
```
results/
├── GPGPGPGP_conformations_1.pdb    # Conformation 1
├── GPGPGPGP_conformations_2.pdb    # Conformation 2
├── ...
└── conformational_sampling_metadata.json  # Execution metadata
```

### Batch Processing
```
batch_output/
├── seq_001_GPGPGP.pdb              # Individual sequence results
├── seq_002_CGPGPC.pdb
├── ...
├── batch_summary.csv               # Summary table
└── batch_detailed_results.json     # Detailed results
```

## Configuration Files

Configuration files are in JSON format in the `configs/` directory:

- `conformational_sampling_config.json` - Parameters for single sequence sampling
- `batch_processing_config.json` - Parameters for batch processing
- `default_config.json` - Default parameters for all tools

### Example Configuration

```json
{
  "sampling": {
    "numsteps": 500000,
    "nbruns": 25
  },
  "constraints": {
    "cyclic": true,
    "disulfide": false
  },
  "validation": {
    "min_sequence_length": 6,
    "max_sequence_length": 20
  }
}
```

## For MCP Tool Development

Each script exports a main function that can be wrapped as an MCP tool:

```python
# Example MCP wrapper
from scripts.conformational_sampling import run_conformational_sampling
from scripts.batch_processing import run_batch_processing

@mcp.tool()
def sample_cyclic_peptide_conformations(
    sequence: str,
    num_conformations: int = 25,
    output_dir: str = "results"
) -> dict:
    """Generate conformational ensemble for a cyclic peptide."""
    return run_conformational_sampling(
        input_sequence=sequence,
        output_file=output_dir,
        nbruns=num_conformations
    )

@mcp.tool()
def batch_process_peptides(
    sequences_file: str,
    output_dir: str = "batch_results",
    max_workers: int = 4
) -> dict:
    """Process multiple cyclic peptides in batch."""
    return run_batch_processing(
        input_file=sequences_file,
        output_dir=output_dir,
        max_workers=max_workers
    )
```

## Script Functions

### conformational_sampling.py
- **Main function**: `run_conformational_sampling(input_sequence, output_file, config, **kwargs)`
- **Purpose**: Generate conformational ensembles for single cyclic peptides
- **Returns**: Dict with result summary, output files, and metadata

### batch_processing.py
- **Main function**: `run_batch_processing(input_file, output_dir, config, **kwargs)`
- **Purpose**: Process multiple cyclic peptide sequences in parallel
- **Returns**: Dict with processing summary, output directory, and statistics

## Validation

Both scripts include comprehensive input validation:

- **Sequence validation**: Valid amino acids (ACDEFGHIKLMNPQRSTVWY)
- **Length constraints**: 6-20 amino acids (configurable)
- **File existence**: Input files must exist
- **Binary availability**: ADCP binary must be executable

## Error Handling

Scripts handle common error scenarios:

- Invalid sequences (invalid amino acids, wrong length)
- Missing files (input files, ADCP binary)
- ADCP execution errors (timeouts, crashes)
- File system errors (permissions, disk space)

## Troubleshooting

### Common Issues

1. **ADCP binary not found**
   ```
   FileNotFoundError: ADCP binary not found
   ```
   - Ensure `adcp_Linux-x86_64` is in the parent directory
   - Check binary permissions (`chmod +x adcp_Linux-x86_64`)

2. **Invalid sequences**
   ```
   ValueError: Invalid peptide sequence
   ```
   - Check sequence contains only valid amino acids
   - Ensure sequence length is 6-20 amino acids

3. **Execution timeouts**
   ```
   timeout: Timeout after 300 seconds
   ```
   - Reduce `numsteps` parameter
   - Increase `timeout_seconds` in config

### Debug Mode

Use dry-run mode to validate inputs without execution:

```bash
python scripts/conformational_sampling.py --input SEQUENCE --dry-run
python scripts/batch_processing.py --input file.txt --dry-run
```

## Performance Notes

- **Single sequence**: ~1-60 seconds per conformation depending on parameters
- **Batch processing**: Parallel execution speeds up processing significantly
- **Memory usage**: Minimal (~50MB per worker thread)
- **Disk usage**: ~20-100KB per output PDB file

## Next Steps (Step 6)

These scripts are ready for MCP tool wrapping. The main functions can be imported and wrapped with MCP decorators to create the final cyclic peptide analysis tools.