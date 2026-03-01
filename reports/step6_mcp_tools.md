# Step 6: MCP Tools Documentation

## Server Information
- **Server Name**: adcp-cycpep-tools
- **Version**: 1.0.0
- **Created Date**: 2026-02-23
- **Server Path**: `src/server.py`
- **API Architecture**: Submit-only (all operations >10 minutes)

## Overview

This MCP server provides access to ADCP (conformational sampling) tools for cyclic peptides. All operations are long-running (>10 minutes) and use the submit/async API pattern with comprehensive job management.

## Job Management Tools

| Tool | Description | Returns |
|------|-------------|---------|
| `get_job_status` | Check job progress and current status | Job metadata with status, timestamps |
| `get_job_result` | Get completed job results and output files | Result data or completion confirmation |
| `get_job_log` | View job execution logs (with tail support) | Log lines and total line count |
| `cancel_job` | Cancel a running job | Success/error confirmation |
| `list_jobs` | List all jobs (with optional status filter) | Array of jobs with metadata |

## Submit Tools (Long Operations > 10 min)

| Tool | Description | Source Script | Est. Runtime | Batch Support |
|------|-------------|---------------|--------------|---------------|
| `submit_conformational_sampling` | Generate conformations for single peptide | `scripts/conformational_sampling.py` | 20-60 min | No |
| `submit_batch_processing` | Process multiple peptides in parallel | `scripts/batch_processing.py` | 30+ min | Yes |

## Utility Tools

| Tool | Description | Est. Runtime |
|------|-------------|--------------|
| `validate_peptide_sequence` | Validate amino acid sequence for ADCP | <1 sec |
| `check_adcp_binary` | Verify ADCP binary availability | <1 sec |
| `get_server_info` | Get server capabilities and status | <1 sec |

---

## Detailed Tool Documentation

### Job Management Tools

#### `get_job_status(job_id: str)`
**Purpose**: Check the current status of any submitted job.

**Parameters**:
- `job_id`: Job identifier returned from submit functions

**Returns**:
```json
{
  "job_id": "abc12345",
  "job_name": "conformational_sampling_GPGPGPGP",
  "status": "running|pending|completed|failed|cancelled",
  "submitted_at": "2026-02-23T09:30:00",
  "started_at": "2026-02-23T09:30:15",
  "completed_at": "2026-02-23T10:15:30",
  "error": "Error message if failed"
}
```

#### `get_job_result(job_id: str)`
**Purpose**: Retrieve results from completed jobs.

**Returns**:
```json
{
  "status": "success",
  "result": {
    "output_files": ["path/to/output1.pdb", "path/to/output2.pdb"],
    "conformational_metadata": {...},
    "batch_results": {...}
  }
}
```

#### `get_job_log(job_id: str, tail: int = 50)`
**Purpose**: View execution logs for debugging and monitoring.

**Parameters**:
- `tail`: Number of lines from end (0 = all lines)

#### `cancel_job(job_id: str)`
**Purpose**: Terminate running jobs.

#### `list_jobs(status: str = None)`
**Purpose**: List and filter all submitted jobs.

**Parameters**:
- `status`: Optional filter ("pending", "running", "completed", "failed", "cancelled")

---

### Submit Tools

#### `submit_conformational_sampling()`
**Purpose**: Generate conformational ensembles for a single cyclic peptide.

**Parameters**:
- `sequence` (required): Peptide sequence (6-20 amino acids)
- `numsteps`: MC steps per run (default: 500,000)
- `nbruns`: Number of independent runs (default: 25)
- `cyclic`: Enable cyclic constraints (default: True)
- `disulfide`: Enable disulfide constraints (default: False)
- `output_dir`: Output directory path
- `job_name`: Optional job name for tracking

**Validation**:
- Sequence must contain only valid amino acids (ACDEFGHIKLMNPQRSTVWY)
- Length must be 6-20 amino acids
- ADCP binary must be available

**Output**:
- Multiple PDB files (one per run)
- JSON metadata file with sampling statistics
- Execution logs

**Example**:
```
submit_conformational_sampling("GPGPGPGP", nbruns=10, job_name="test_peptide")
```

#### `submit_batch_processing()`
**Purpose**: Process multiple sequences from a file in parallel.

**Parameters**:
- `input_file` (required): Path to sequences file
- `numsteps`: MC steps per sequence (default: 1,000 for batch)
- `max_workers`: Parallel workers (default: 4)
- `cyclic`: Enable cyclic constraints (default: True)
- `disulfide`: Enable disulfide constraints (default: False)
- `timeout`: Timeout per sequence in seconds (default: 300)
- `output_dir`: Output directory path
- `job_name`: Optional job name for tracking

**Input File Format**:
```
# Comments start with #
GPGPGPGP
seq001	ACDEFGHIKL
seq002	LMNPQRSTVW
```

**Output**:
- Individual PDB files for successful sequences
- CSV summary file (`batch_summary.csv`)
- JSON detailed results (`batch_detailed_results.json`)

---

### Utility Tools

#### `validate_peptide_sequence(sequence: str)`
**Purpose**: Pre-validate sequences before submission.

**Returns**:
```json
{
  "status": "valid|invalid",
  "sequence": "GPGPGPGP",
  "length": 8,
  "message": "Valid peptide sequence with 8 amino acids",
  "error": "Error message if invalid"
}
```

#### `check_adcp_binary()`
**Purpose**: Verify ADCP binary is available before job submission.

**Returns**:
```json
{
  "status": "available|not_found",
  "binary_path": "/path/to/adcp_Linux-x86_64",
  "binary_size": 12345678,
  "searched_paths": ["..."]
}
```

#### `get_server_info()`
**Purpose**: Get server capabilities and current status.

**Returns**: Server metadata, tool list, and system status.

---

## Workflow Examples

### Single Peptide Analysis
```bash
# 1. Validate sequence
validate_peptide_sequence("GPGPGPGP")

# 2. Check ADCP availability
check_adcp_binary()

# 3. Submit job
submit_conformational_sampling("GPGPGPGP", nbruns=5, job_name="my_peptide")
→ Returns: {"status": "submitted", "job_id": "abc12345"}

# 4. Monitor progress
get_job_status("abc12345")
→ Returns: {"status": "running", ...}

# 5. Get results when completed
get_job_result("abc12345")
→ Returns: {"status": "success", "result": {...}}
```

### Batch Processing Workflow
```bash
# 1. Submit batch job
submit_batch_processing("sequences.txt", max_workers=2, job_name="library_screen")
→ Returns: {"status": "submitted", "job_id": "def67890"}

# 2. Monitor progress
get_job_status("def67890")

# 3. View logs for debugging
get_job_log("def67890", tail=20)

# 4. Get comprehensive results
get_job_result("def67890")
→ Returns: CSV + JSON files with all results
```

### Job Management
```bash
# List all jobs
list_jobs()

# List only running jobs
list_jobs("running")

# Cancel a job if needed
cancel_job("abc12345")
```

---

## Technical Details

### Job Storage
- **Location**: `./jobs/` directory
- **Structure**: Each job gets unique directory with metadata, logs, results
- **Persistence**: Jobs survive server restarts
- **Cleanup**: Manual cleanup recommended for old jobs

### Error Handling
All tools return structured error responses:
```json
{
  "status": "error",
  "error": "Descriptive error message"
}
```

### Binary Requirements
- **File**: `adcp_Linux-x86_64` (Linux x86_64 binary)
- **Location**: Project root, current directory, or PATH
- **Dependencies**: Requires `transpoints` and `con` files (auto-generated)

### Performance Characteristics
- **Conformational Sampling**: 20-60 minutes (25 runs × 500k steps)
- **Batch Processing**: Scales with sequence count and workers
- **Job Overhead**: <5 seconds for job submission and monitoring
- **Memory**: Each ADCP process uses ~100-500MB RAM

### Limitations
- **Sequence Length**: 6-20 amino acids (ADCP constraint)
- **Parallel Jobs**: Limited by system resources
- **Storage**: PDB files can be large (1-10MB each)
- **Platform**: Linux x86_64 only (ADCP binary limitation)

---

## Integration Notes

### For LLM Usage
1. **Always validate sequences** before submission
2. **Check binary availability** before long operations
3. **Use meaningful job names** for tracking
4. **Monitor job status** periodically for long runs
5. **Handle errors gracefully** with structured responses

### For Developers
- All tools are async/submit pattern (no sync tools)
- Job management is thread-safe
- Results are automatically collected when available
- Logs are persistent and accessible during and after execution

### Configuration
- Default parameters are optimized for typical use cases
- Batch mode uses lower step counts for faster throughput
- Timeouts prevent runaway jobs
- Output directories are auto-created as needed