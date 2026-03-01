# ADCP Examples and Use Cases

This directory contains example scripts and data files for using ADCP (AutoDock CrankPep) for cyclic peptide docking and analysis.

## Available Use Cases

| Script | Description | Complexity | Priority |
|--------|-------------|------------|----------|
| `use_case_1_cyclic_peptide_docking.py` | Basic cyclic peptide sequence docking | Simple | High |
| `use_case_2_disulfide_cyclic_docking.py` | Disulfide-bridged cyclic peptides | Medium | High |
| `use_case_3_structure_based_docking.py` | Docking from PDB structure | Medium | Medium |
| `use_case_4_conformational_sampling.py` | Peptide folding without receptor | Simple | Medium |
| `use_case_5_batch_processing.py` | Batch processing multiple sequences | Complex | High |

## Quick Start

### 1. Basic Cyclic Peptide Docking
```bash
# Dry run to see the command (no target file needed)
python examples/use_case_1_cyclic_peptide_docking.py --sequence GPGPGPGP --dry-run

# Real docking (requires .trg target file)
python examples/use_case_1_cyclic_peptide_docking.py \
    --sequence GPGPGPGP \
    --target receptor.trg \
    --output my_cyclic_peptide
```

### 2. Disulfide-Bridged Peptides
```bash
python examples/use_case_2_disulfide_cyclic_docking.py \
    --sequence CGPGPGPGC \
    --target receptor.trg \
    --output disulfide_peptide
```

### 3. Structure-Based Docking
```bash
python examples/use_case_3_structure_based_docking.py \
    --input examples/data/structures/sample_peptide.pdb \
    --target receptor.trg \
    --cyclic \
    --output refined_structure
```

### 4. Conformational Sampling
```bash
# Generate conformational ensemble without receptor
python examples/use_case_4_conformational_sampling.py \
    --sequence CGPGPGPGC \
    --output conformations
```

### 5. Batch Processing
```bash
python examples/use_case_5_batch_processing.py \
    --sequences examples/data/sequences/batch_sequences.txt \
    --target receptor.trg \
    --output batch_results
```

## Example Data

### Sequences (`data/sequences/`)
- `batch_sequences.txt` - Collection of sample cyclic peptide sequences
  - Short cyclic peptides (6-8 residues)
  - Disulfide-bridged peptides
  - Medium-length peptides (9-12 residues)
  - RGD-containing sequences
  - Natural-inspired sequences

### Structures (`data/structures/`)
- `sample_peptide.pdb` - Example peptide structure for structure-based docking

### Targets (`data/targets/`)
- See `README_targets.md` for information about receptor target files
- Requires .trg files from AGFR for actual docking

## Command Line Parameters

### Common Parameters
- `-s, --sequence`: Peptide sequence (single letter amino acid codes)
- `-i, --input`: Input PDB file for structure-based docking
- `-t, --target`: Target receptor file (.trg format)
- `-o, --output`: Output basename for results
- `-n, --numsteps`: Number of Monte Carlo steps per run
- `-N, --nbruns`: Number of independent docking runs
- `-c, --maxcores`: Maximum CPU cores to use
- `--dry-run`: Show command without executing

### Constraint Parameters
- `--cyclic`: Enable cyclic peptide constraints (backbone cyclization)
- `--cystein`: Enable disulfide bridge constraints (CYS-CYS bonds)

## Expected Outputs

### Docking Results
Each docking run generates:
- `{output}_{run_number}.pdb` - Docked peptide conformations
- `{output}_{run_number}.out` - Energy and statistics log
- Energy ranking of top conformations

### Batch Processing Results
- `batch_summary.csv` - Summary of all processed sequences
- Individual directories for each sequence
- Energy rankings and statistics

## Requirements

### Software Dependencies
- Python 3.10+
- NumPy
- ADCP binary (compiled from source)
- AGFR for generating .trg target files (optional)

### Input Requirements
- Peptide sequences (1-20 amino acids recommended)
- Receptor target files (.trg format) for docking
- Initial structures (PDB format) for structure-based docking

## Tips and Best Practices

### Sequence Guidelines
- Use standard amino acid single-letter codes
- Cyclic peptides work best with 6-20 residues
- For disulfide bridges, include at least 2 cysteine residues
- Test with shorter sequences first

### Parameter Tuning
- Start with fewer MC steps (50,000-100,000) for testing
- Increase steps (500,000+) for production runs
- Use multiple runs (10-50) for better sampling
- Adjust cores based on available hardware

### Troubleshooting
1. **"No receptor files found"** - Need .trg target file or use --dry-run
2. **Python syntax errors** - Check Python 3 compatibility
3. **Memory issues** - Reduce number of parallel jobs or sequence length
4. **Long runtime** - Reduce MC steps or number of runs

## Integration with MCP

These use cases can be converted to MCP (Model Context Protocol) tools for:
- Automated cyclic peptide docking workflows
- Virtual screening of peptide libraries
- Structure-activity relationship analysis
- Integration with molecular visualization tools

Each use case provides a foundation for building specialized MCP tools for cyclic peptide research and drug discovery applications.