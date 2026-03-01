"""MCP Server for ADCP Cyclic Peptide Tools

Provides submit APIs for long-running ADCP conformational sampling operations.
All tools use the submit/async pattern since ADCP operations take >10 minutes.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List
import sys

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager
from utils import validate_sequence, find_adcp_binary
from loguru import logger

# Create MCP server
mcp = FastMCP("adcp-cycpep-tools")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted ADCP computation job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed ADCP computation job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed ADCP job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running ADCP computation job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted ADCP computation jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Submit Tools for Long-Running ADCP Operations
# ==============================================================================

@mcp.tool()
def submit_conformational_sampling(
    sequence: str,
    numsteps: Optional[int] = None,
    nbruns: Optional[int] = None,
    cyclic: bool = True,
    disulfide: bool = False,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a conformational sampling job for a cyclic peptide sequence using ADCP.

    This task generates multiple conformations using Monte Carlo sampling and
    typically takes 20-60 minutes depending on sequence length and parameters.

    Args:
        sequence: Peptide sequence using single-letter amino acid codes (6-20 AA)
        numsteps: Number of Monte Carlo steps per run (default: 500000)
        nbruns: Number of independent sampling runs (default: 25)
        cyclic: Enable cyclic peptide constraints (default: True)
        disulfide: Enable disulfide bridge constraints (default: False)
        output_dir: Directory to save outputs (auto-generated if not provided)
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs

    Example:
        submit_conformational_sampling("GPGPGPGP", nbruns=10, job_name="test_peptide")
    """
    # Validate sequence
    is_valid, error_msg = validate_sequence(sequence)
    if not is_valid:
        return {
            "status": "error",
            "error": f"Invalid sequence: {error_msg}"
        }

    # Check if ADCP binary exists
    adcp_binary = find_adcp_binary(MCP_ROOT)
    if not adcp_binary:
        return {
            "status": "error",
            "error": "ADCP binary not found. Please ensure adcp_Linux-x86_64 is available."
        }

    script_path = str(SCRIPTS_DIR / "conformational_sampling.py")

    # Build arguments
    args = {
        "input": sequence,
    }

    if output_dir:
        args["output"] = output_dir
    if numsteps is not None:
        args["numsteps"] = numsteps
    if nbruns is not None:
        args["nbruns"] = nbruns
    if not cyclic:  # Only add if False (default is True)
        args["no-cyclic"] = True
    if disulfide:
        args["disulfide"] = True

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"conformational_sampling_{sequence[:8]}"
    )

@mcp.tool()
def submit_batch_processing(
    input_file: str,
    numsteps: Optional[int] = None,
    max_workers: Optional[int] = None,
    cyclic: bool = True,
    disulfide: bool = False,
    timeout: Optional[int] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a batch processing job for multiple cyclic peptide sequences using ADCP.

    Processes multiple sequences from a file, with parallel execution support.
    Runtime varies based on number of sequences and workers (typically 30+ minutes).

    Args:
        input_file: Path to file containing sequences (one per line or tab-separated ID\\tSEQUENCE)
        numsteps: Number of Monte Carlo steps per sequence (default: 1000 for batch mode)
        max_workers: Maximum parallel workers (default: 4)
        cyclic: Enable cyclic peptide constraints (default: True)
        disulfide: Enable disulfide bridge constraints (default: False)
        timeout: Timeout per sequence in seconds (default: 300)
        output_dir: Directory to save outputs (auto-generated if not provided)
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job. Results include:
        - CSV summary file with all results
        - JSON file with detailed results
        - Individual PDB files for successful sequences

    Example:
        submit_batch_processing("sequences.txt", max_workers=2, job_name="peptide_library")
    """
    # Validate input file exists
    input_path = Path(input_file)
    if not input_path.exists():
        return {
            "status": "error",
            "error": f"Input file not found: {input_file}"
        }

    # Check if ADCP binary exists
    adcp_binary = find_adcp_binary(MCP_ROOT)
    if not adcp_binary:
        return {
            "status": "error",
            "error": "ADCP binary not found. Please ensure adcp_Linux-x86_64 is available."
        }

    script_path = str(SCRIPTS_DIR / "batch_processing.py")

    # Build arguments
    args = {
        "input": str(input_path),
    }

    if output_dir:
        args["output"] = output_dir
    if numsteps is not None:
        args["numsteps"] = numsteps
    if max_workers is not None:
        args["max-workers"] = max_workers
    if not cyclic:  # Only add if False (default is True)
        args["no-cyclic"] = True
    if disulfide:
        args["disulfide"] = True
    if timeout is not None:
        args["timeout"] = timeout

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"batch_processing_{input_path.stem}"
    )

# ==============================================================================
# Utility Tools
# ==============================================================================

@mcp.tool()
def validate_peptide_sequence(sequence: str) -> dict:
    """
    Validate a peptide sequence for use with ADCP tools.

    Args:
        sequence: Peptide sequence using single-letter amino acid codes

    Returns:
        Dictionary with validation result and details
    """
    is_valid, error_msg = validate_sequence(sequence)

    if is_valid:
        return {
            "status": "valid",
            "sequence": sequence.upper(),
            "length": len(sequence),
            "message": f"Valid peptide sequence with {len(sequence)} amino acids"
        }
    else:
        return {
            "status": "invalid",
            "sequence": sequence,
            "error": error_msg
        }

@mcp.tool()
def check_adcp_binary() -> dict:
    """
    Check if the ADCP binary is available and accessible.

    Returns:
        Dictionary with binary status and path information
    """
    binary_path = find_adcp_binary(MCP_ROOT)

    if binary_path:
        return {
            "status": "available",
            "binary_path": str(binary_path),
            "binary_size": binary_path.stat().st_size,
            "message": "ADCP binary found and accessible"
        }
    else:
        return {
            "status": "not_found",
            "error": "ADCP binary not found",
            "searched_paths": [
                str(MCP_ROOT / "adcp_Linux-x86_64"),
                "adcp_Linux-x86_64",
                "./adcp_Linux-x86_64"
            ]
        }

@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the ADCP MCP server and its capabilities.

    Returns:
        Dictionary with server information, available tools, and system status
    """
    return {
        "server_name": "adcp-cycpep-tools",
        "version": "1.0.0",
        "description": "MCP server for ADCP cyclic peptide conformational sampling",
        "tools": {
            "job_management": [
                "get_job_status",
                "get_job_result",
                "get_job_log",
                "cancel_job",
                "list_jobs"
            ],
            "submit_tools": [
                "submit_conformational_sampling",
                "submit_batch_processing"
            ],
            "utilities": [
                "validate_peptide_sequence",
                "check_adcp_binary",
                "get_server_info"
            ]
        },
        "api_type": "submit_only",
        "reason": "All ADCP operations take >10 minutes and require async execution",
        "binary_status": "available" if find_adcp_binary(MCP_ROOT) else "not_found",
        "jobs_directory": str(job_manager.jobs_dir),
        "scripts_directory": str(SCRIPTS_DIR)
    }

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()