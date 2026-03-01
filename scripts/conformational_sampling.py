#!/usr/bin/env python3
"""
Script: conformational_sampling.py
Description: Generate conformational ensembles for cyclic peptides using ADCP

Original Use Case: examples/use_case_4_conformational_sampling.py
Dependencies Removed: None (already minimal - only standard library)

Usage:
    python scripts/conformational_sampling.py --input SEQUENCE --output output.pdb
    python scripts/conformational_sampling.py --input examples/data/sequences/batch_sequences.txt --output results/

Example:
    python scripts/conformational_sampling.py --input GPGPGPGP --output results/conformations.pdb
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json
import tempfile

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "numsteps": 500000,
    "nbruns": 25,
    "maxcores": 4,
    "cyclic": True,
    "disulfide": False,
    "optimization_weights": [1, 0.25, 0.75, 0.0],
    "min_sequence_length": 6,
    "max_sequence_length": 20,
    "adcp_binary": "adcp_Linux-x86_64"
}

# ==============================================================================
# Inlined Utility Functions (simplified from repo)
# ==============================================================================
def validate_sequence(sequence: str) -> bool:
    """Validate peptide sequence using single-letter amino acid codes."""
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    if not sequence:
        return False

    # Check if all characters are valid amino acids
    if not all(aa.upper() in valid_aa for aa in sequence):
        return False

    # Check length constraints
    if len(sequence) < DEFAULT_CONFIG["min_sequence_length"]:
        return False
    if len(sequence) > DEFAULT_CONFIG["max_sequence_length"]:
        return False

    return True

def create_dummy_transpoints(temp_dir: Path) -> Path:
    """Create a minimal transpoints file for conformational sampling."""
    transpoints_file = temp_dir / "transpoints"
    transpoints_content = """1
0.000   0.000   0.000
"""
    with open(transpoints_file, "w") as f:
        f.write(transpoints_content)
    return transpoints_file

def create_minimal_con_file(temp_dir: Path) -> Path:
    """Create a minimal con file."""
    con_file = temp_dir / "con"
    with open(con_file, "w") as f:
        f.write("1\n")
    return con_file

def build_adcp_command(
    sequence: str,
    output_file: Path,
    config: Dict[str, Any],
    binary_path: Path
) -> List[str]:
    """Build ADCP command for conformational sampling."""
    cmd = [
        str(binary_path),
        "-r", f"1x{config['numsteps']}",
        "-t", "1",  # Single thread per job
        sequence.upper()
    ]

    # Build parameters string
    params = "Bias=NULL"
    if config["cyclic"]:
        params += ",external2=4,con,2,1.0"
    if config["disulfide"]:
        params += ",SSbond=80,2.2,20,0.5"

    # Add optimization weights
    weights = config["optimization_weights"]
    params += f",Opt={weights[0]},{weights[1]},{weights[2]},{weights[3]}"

    cmd.extend(["-p", params])
    cmd.extend(["-o", str(output_file)])

    return cmd

def save_metadata(
    output_dir: Path,
    sequence: str,
    config: Dict[str, Any],
    results: List[Dict]
) -> None:
    """Save execution metadata to JSON file."""
    metadata = {
        "sequence": sequence,
        "config": config,
        "results": results,
        "total_runs": len(results),
        "successful_runs": sum(1 for r in results if r["status"] == "success")
    }

    metadata_file = output_dir / "conformational_sampling_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_conformational_sampling(
    input_sequence: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for cyclic peptide conformational sampling.

    Args:
        input_sequence: Peptide sequence (string) or file path containing sequences
        output_file: Path to save output (optional, will auto-generate if not provided)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Main computation result
            - output_files: List of generated PDB files
            - metadata: Execution metadata

    Example:
        >>> result = run_conformational_sampling("GPGPGPGP", "output.pdb")
        >>> print(result['output_files'])
    """
    # Setup configuration
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Determine if input is sequence or file
    if isinstance(input_sequence, (str, Path)) and Path(input_sequence).exists():
        # Input is a file path
        input_file = Path(input_sequence)
        with open(input_file, 'r') as f:
            # For now, take first valid sequence from file
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle tab-separated format (ID\tSEQUENCE)
                    if '\t' in line:
                        sequence = line.split('\t')[1]
                    else:
                        sequence = line
                    break
            else:
                raise ValueError(f"No valid sequences found in {input_file}")
    else:
        # Input is a sequence string
        sequence = str(input_sequence)

    # Validate sequence
    if not validate_sequence(sequence):
        raise ValueError(f"Invalid peptide sequence: {sequence}")

    print(f"=== Conformational Sampling with ADCP ===")
    print(f"Sequence: {sequence}")
    print(f"Length: {len(sequence)} amino acids")
    print(f"Cyclic constraints: {'Yes' if config['cyclic'] else 'No'}")
    print(f"Disulfide constraints: {'Yes' if config['disulfide'] else 'No'}")
    print(f"MC Steps: {config['numsteps']}")
    print(f"Runs: {config['nbruns']}")
    print()

    # Setup output directory
    if output_file:
        output_path = Path(output_file)
        if output_path.suffix == '.pdb':
            # Single file output - use directory for multiple runs
            output_dir = output_path.parent / output_path.stem
            output_basename = output_path.stem
        else:
            # Directory or basename
            output_dir = Path(output_file)
            output_basename = f"{sequence}_conformations"
    else:
        # Auto-generate output path
        output_dir = Path("results") / "conformational_sampling"
        output_basename = f"{sequence}_conformations"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find ADCP binary
    script_dir = Path(__file__).parent
    mcp_root = script_dir.parent

    binary_candidates = [
        mcp_root / config["adcp_binary"],
        Path(config["adcp_binary"]),
        Path(f"./{config['adcp_binary']}")
    ]

    adcp_binary = None
    for candidate in binary_candidates:
        if candidate.exists() and candidate.is_file():
            adcp_binary = candidate
            break

    if not adcp_binary:
        raise FileNotFoundError(f"ADCP binary not found. Tried: {[str(c) for c in binary_candidates]}")

    # Run conformational sampling with temporary files
    results = []
    output_files = []

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        # Create required files for ADCP
        print("Setting up conformational sampling environment...")
        transpoints_file = create_dummy_transpoints(temp_dir)
        con_file = create_minimal_con_file(temp_dir)
        print("✓ Created minimal grid files")

        # Change to temp directory for ADCP execution
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_dir)

            print("Running conformational sampling...")
            for run_id in range(1, config['nbruns'] + 1):
                output_file_path = output_dir / f"{output_basename}_{run_id}.pdb"

                # Build command
                cmd = build_adcp_command(sequence, output_file_path, config, adcp_binary)

                print(f"Running sampling job {run_id}/{config['nbruns']}...")

                try:
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print(f"✓ Completed run {run_id}")
                    results.append({
                        "run_id": run_id,
                        "status": "success",
                        "output_file": str(output_file_path),
                        "error": None
                    })
                    output_files.append(str(output_file_path))
                except subprocess.CalledProcessError as e:
                    print(f"✗ Run {run_id} failed: {e}")
                    results.append({
                        "run_id": run_id,
                        "status": "failed",
                        "output_file": None,
                        "error": str(e)
                    })

        finally:
            os.chdir(original_cwd)

    # Save metadata
    save_metadata(output_dir, sequence, config, results)

    print(f"\n=== Conformational sampling completed ===")
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"Generated {success_count}/{config['nbruns']} conformations")
    if output_files:
        print(f"Output files: {output_dir}/{output_basename}_*.pdb")
        print(f"Metadata: {output_dir}/conformational_sampling_metadata.json")

    return {
        "result": f"Generated {success_count} conformations for {sequence}",
        "output_files": output_files,
        "output_dir": str(output_dir),
        "metadata": {
            "sequence": sequence,
            "config": config,
            "total_runs": len(results),
            "successful_runs": success_count
        }
    }

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True,
                       help='Input peptide sequence or file path')
    parser.add_argument('--output', '-o',
                       help='Output file/directory path')
    parser.add_argument('--config', '-c',
                       help='Config file (JSON)')
    parser.add_argument('--numsteps', type=int,
                       help=f'Number of MC steps per run (default: {DEFAULT_CONFIG["numsteps"]})')
    parser.add_argument('--nbruns', type=int,
                       help=f'Number of independent runs (default: {DEFAULT_CONFIG["nbruns"]})')
    parser.add_argument('--cyclic', action='store_true', default=None,
                       help='Enable cyclic constraints (default: True)')
    parser.add_argument('--no-cyclic', action='store_true',
                       help='Disable cyclic constraints')
    parser.add_argument('--disulfide', action='store_true',
                       help='Enable disulfide bridge constraints')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without executing')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Override config with command line arguments
    overrides = {}
    if args.numsteps is not None:
        overrides['numsteps'] = args.numsteps
    if args.nbruns is not None:
        overrides['nbruns'] = args.nbruns
    if args.cyclic is not None:
        overrides['cyclic'] = args.cyclic
    if args.no_cyclic:
        overrides['cyclic'] = False
    if args.disulfide:
        overrides['disulfide'] = True

    if args.dry_run:
        print("Dry run mode - would run conformational sampling with:")
        print(f"  Input: {args.input}")
        print(f"  Output: {args.output or 'auto-generated'}")
        print(f"  Config overrides: {overrides}")
        return 0

    # Run
    try:
        result = run_conformational_sampling(
            input_sequence=args.input,
            output_file=args.output,
            config=config,
            **overrides
        )

        print(f"\nSuccess: {result['result']}")
        if result['output_files']:
            print(f"Output directory: {result['output_dir']}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())