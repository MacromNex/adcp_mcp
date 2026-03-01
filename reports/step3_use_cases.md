# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2026-02-23
- **Filter Applied**: automated cyclic peptide docking using AutoDock CrankPep, conformer generation, flexible backbone handling
- **Python Version**: 3.12.12
- **Environment Strategy**: single
- **Source Repository**: ADCP (AutoDock CrankPep)

## Use Cases Identified and Implemented

### UC-001: Cyclic Peptide Sequence Docking
- **Description**: Basic cyclic peptide docking from amino acid sequence using backbone cyclization
- **Script Path**: `examples/use_case_1_cyclic_peptide_docking.py`
- **Complexity**: Simple
- **Priority**: High
- **Environment**: `./env`
- **Source**: README, runADCP.py analysis

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequence | string | Peptide sequence (single-letter AA codes) | --sequence, -s |
| target | file | Receptor target file (.trg from AGFR) | --target, -t |
| output | string | Output basename for docking results | --output, -o |
| numsteps | int | Monte Carlo steps per run | --numsteps, -n |
| nbruns | int | Number of independent docking runs | --nbruns, -N |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| docked_structures | files | PDB files with docked conformations (output_*.pdb) |
| energy_logs | files | Energy and statistics logs (output_*.out) |

**Example Usage:**
```bash
python examples/use_case_1_cyclic_peptide_docking.py --sequence GPGPGPGP --target receptor.trg --output cyclic_dock
```

**Example Data**: Default sequence GPGPGPGP

---

### UC-002: Disulfide-Bridged Cyclic Peptide Docking
- **Description**: Docking of cyclic peptides with disulfide bridge constraints (CYS-CYS bonds)
- **Script Path**: `examples/use_case_2_disulfide_cyclic_docking.py`
- **Complexity**: Medium
- **Priority**: High
- **Environment**: `./env`
- **Source**: runADCP.py --cystein flag analysis

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequence | string | Peptide with cysteine residues | --sequence, -s |
| target | file | Receptor target file | --target, -t |
| output | string | Output basename | --output, -o |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| docked_structures | files | PDB files with disulfide constraints |
| validation | stdout | Cysteine count and position validation |

**Example Usage:**
```bash
python examples/use_case_2_disulfide_cyclic_docking.py --sequence CGPGPGPGC --target receptor.trg
```

**Example Data**: Default sequence CGPGPGPGC

---

### UC-003: Structure-Based Peptide Docking
- **Description**: Docking peptides from initial 3D structure (PDB) with optional constraints
- **Script Path**: `examples/use_case_3_structure_based_docking.py`
- **Complexity**: Medium
- **Priority**: Medium
- **Environment**: `./env`
- **Source**: runADCP.py -i flag analysis

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_pdb | file | Initial peptide structure | --input, -i |
| target | file | Receptor target file | --target, -t |
| cyclic_flag | boolean | Enable cyclic constraints | --cyclic |
| cystein_flag | boolean | Enable disulfide constraints | --cystein |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| refined_structures | files | Refined peptide conformations |

**Example Usage:**
```bash
python examples/use_case_3_structure_based_docking.py --input examples/data/structures/sample_peptide.pdb --cyclic
```

**Example Data**: `examples/data/structures/sample_peptide.pdb`

---

### UC-004: Conformational Sampling and Peptide Folding
- **Description**: Generate conformational ensembles without specific receptor using internal energies
- **Script Path**: `examples/use_case_4_conformational_sampling.py`
- **Complexity**: Simple
- **Priority**: Medium
- **Environment**: `./env`
- **Source**: ADCP internal energy capabilities, README folding analysis

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequence | string | Peptide sequence for folding | --sequence, -s |
| numsteps | int | MC steps for sampling | --numsteps, -n |
| nbruns | int | Independent sampling runs | --nbruns, -N |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| conformations | files | Ensemble of peptide conformations |

**Example Usage:**
```bash
python examples/use_case_4_conformational_sampling.py --sequence CGPGPGPGC --numsteps 500000
```

**Example Data**: Default sequence CGPGPGPGC

---

### UC-005: Batch Processing Multiple Sequences
- **Description**: High-throughput processing of multiple peptide sequences with parallel execution
- **Script Path**: `examples/use_case_5_batch_processing.py`
- **Complexity**: Complex
- **Priority**: High
- **Environment**: `./env`
- **Source**: Virtual screening and SAR analysis requirements

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequences_file | file | Text file with peptide sequences | --sequences |
| target | file | Receptor target file | --target, -t |
| max_workers | int | Parallel processing limit | --max-workers |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| batch_summary | file | CSV summary with energies and statistics |
| individual_results | directories | Separate results for each sequence |

**Example Usage:**
```bash
python examples/use_case_5_batch_processing.py --sequences examples/data/sequences/batch_sequences.txt --max-workers 4
```

**Example Data**: `examples/data/sequences/batch_sequences.txt` (25 diverse sequences)

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Use Cases Found | 5 |
| Scripts Created | 5 |
| High Priority | 3 |
| Medium Priority | 2 |
| Low Priority | 0 |
| Demo Data Files Created | Yes |

## Use Case Classification by Function

### Docking & Binding
- UC-001: Basic cyclic peptide docking
- UC-002: Disulfide-bridged docking
- UC-003: Structure-based docking

### Sampling & Analysis
- UC-004: Conformational sampling
- UC-005: Batch virtual screening

### Constraint Types Supported
- **Cyclic backbone**: UC-001, UC-003, UC-004
- **Disulfide bridges**: UC-002, UC-003, UC-005 (auto-detected)
- **Flexible backbone**: All use cases (ADCP core feature)
- **AutoDock energy landscape**: All use cases

## Demo Data Index

| Source | Destination | Description |
|--------|-------------|-------------|
| Generated | `examples/data/sequences/batch_sequences.txt` | 25 diverse cyclic peptide sequences |
| Generated | `examples/data/sequences/cyclic_peptides.smi` | Sample sequences in SMILES-like format |
| Generated | `examples/data/structures/sample_peptide.pdb` | Example GPGP peptide structure |
| Documentation | `examples/data/targets/README_targets.md` | Guide for .trg target file requirements |
| Generated | `examples/README.md` | Comprehensive examples documentation |

## Feature Coverage Analysis

### ADCP Core Features Covered
- ✅ Sequence-based docking
- ✅ Structure-based docking
- ✅ Cyclic peptide constraints
- ✅ Disulfide bridge handling
- ✅ Monte Carlo conformational sampling
- ✅ AutoDock energy evaluation
- ✅ Parallel processing support
- ✅ Flexible backbone handling

### Advanced Features
- ✅ Batch virtual screening
- ✅ Energy-based ranking
- ✅ Conformational ensemble generation
- ✅ Multi-constraint handling
- ⚠️ Receptor preparation (requires external AGFR)
- ⚠️ Visualization (could be added as separate tool)

## Integration Readiness

All use cases are designed for easy conversion to MCP tools:

1. **Standardized interfaces**: Consistent parameter naming and validation
2. **Error handling**: Comprehensive input validation and error reporting
3. **Output formatting**: Structured results suitable for programmatic access
4. **Documentation**: Complete usage examples and parameter descriptions
5. **Testing support**: Dry-run modes for validation without execution

## Recommendations for MCP Tool Development

1. **Priority order**: Implement UC-001, UC-005, UC-002 first (highest impact)
2. **Modular design**: Each use case can be a separate MCP tool
3. **Shared utilities**: Common validation and parameter handling across tools
4. **Target file handling**: Consider AGFR integration or pre-computed target library
5. **Results visualization**: Add structure viewing and analysis capabilities