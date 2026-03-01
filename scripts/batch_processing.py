#!/usr/bin/env python3
"""
Script: batch_processing.py
Description: Process multiple cyclic peptide sequences in batch using ADCP conformational sampling

Original Use Case: examples/use_case_5_batch_processing.py + results/uc_005/batch_conformational_sampling.py
Dependencies Removed: None (already minimal - only standard library)

Usage:
    python scripts/batch_processing.py --input sequences.txt --output results/
    python scripts/batch_processing.py --input sequences.txt --output results/ --max-workers 4

Example:
    python scripts/batch_processing.py --input examples/data/sequences/batch_sequences.txt --output results/batch_output
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import os
import subprocess
import sys
import csv
from pathlib import Path
from typing import Union, Optional, Dict, Any, List, Tuple
import json
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "numsteps": 1000,  # Lower default for batch processing
    "max_workers": 4,
    "cyclic": True,
    "disulfide": False,
    "optimization_weights": [1, 0.25, 0.75, 0.0],
    "min_sequence_length": 6,
    "max_sequence_length": 20,
    "adcp_binary": "adcp_Linux-x86_64",
    "timeout_seconds": 300,  # 5 minute timeout per job
    "retry_attempts": 1
}

# ==============================================================================
# Inlined Utility Functions (simplified from repo)
# ==============================================================================
def validate_sequence(sequence: str) -> Tuple[bool, str]:
    """Validate peptide sequence and return (is_valid, error_message)."""
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")

    if not sequence:
        return False, "Empty sequence"

    # Check if all characters are valid amino acids
    invalid_chars = [aa for aa in sequence.upper() if aa not in valid_aa]
    if invalid_chars:
        return False, f"Invalid amino acids: {', '.join(set(invalid_chars))}"

    # Check length constraints
    if len(sequence) < DEFAULT_CONFIG["min_sequence_length"]:
        return False, f"Sequence too short (minimum {DEFAULT_CONFIG['min_sequence_length']})"
    if len(sequence) > DEFAULT_CONFIG["max_sequence_length"]:
        return False, f"Sequence too long (maximum {DEFAULT_CONFIG['max_sequence_length']})"

    return True, ""

def parse_sequences_file(file_path: Path) -> List[Tuple[str, str]]:
    """Parse sequences file and return list of (sequence_id, sequence) tuples."""
    sequences = []

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Handle tab-separated format (ID\tSEQUENCE)
            if '\t' in line:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    seq_id, sequence = parts[0].strip(), parts[1].strip()
                else:
                    seq_id = f"seq_{line_num:03d}"
                    sequence = line
            else:
                # Just sequence, generate ID
                seq_id = f"seq_{line_num:03d}"
                sequence = line

            sequences.append((seq_id, sequence))

    return sequences

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

def run_single_conformation_job(
    seq_id: str,
    sequence: str,
    output_dir: Path,
    config: Dict[str, Any],
    adcp_binary: Path,
    temp_dir: Path
) -> Dict[str, Any]:
    """Run conformational sampling for a single sequence."""
    start_time = time.time()

    # Validate sequence first
    is_valid, error_msg = validate_sequence(sequence)
    if not is_valid:
        return {
            "seq_id": seq_id,
            "sequence": sequence,
            "status": "validation_failed",
            "error": error_msg,
            "output_file": None,
            "execution_time": 0
        }

    # Create output file path
    output_file = output_dir / f"{seq_id}_{sequence}.pdb"

    # Build ADCP command
    cmd = [
        str(adcp_binary),
        "-r", f"1x{config['numsteps']}",
        "-t", "1",  # Single thread
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

    # Run the command
    original_cwd = Path.cwd()
    try:
        os.chdir(temp_dir)

        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=config.get("timeout_seconds", 300)
        )

        execution_time = time.time() - start_time

        return {
            "seq_id": seq_id,
            "sequence": sequence,
            "status": "success",
            "error": None,
            "output_file": str(output_file),
            "execution_time": execution_time,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return {
            "seq_id": seq_id,
            "sequence": sequence,
            "status": "timeout",
            "error": f"Timeout after {config.get('timeout_seconds', 300)} seconds",
            "output_file": None,
            "execution_time": execution_time
        }

    except subprocess.CalledProcessError as e:
        execution_time = time.time() - start_time
        return {
            "seq_id": seq_id,
            "sequence": sequence,
            "status": "failed",
            "error": f"Exit code {e.returncode}: {e.stderr}",
            "output_file": None,
            "execution_time": execution_time
        }

    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "seq_id": seq_id,
            "sequence": sequence,
            "status": "error",
            "error": str(e),
            "output_file": None,
            "execution_time": execution_time
        }

    finally:
        os.chdir(original_cwd)

def save_batch_results(results: List[Dict], output_dir: Path, config: Dict) -> None:
    """Save batch processing results to CSV and JSON files."""
    # Save CSV summary
    csv_file = output_dir / "batch_summary.csv"
    with open(csv_file, 'w', newline='') as f:
        fieldnames = ['seq_id', 'sequence', 'status', 'output_file', 'execution_time', 'error']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({
                'seq_id': result['seq_id'],
                'sequence': result['sequence'],
                'status': result['status'],
                'output_file': result['output_file'],
                'execution_time': f"{result['execution_time']:.2f}s" if result['execution_time'] else "0s",
                'error': result['error'] or ""
            })

    # Save detailed JSON
    json_file = output_dir / "batch_detailed_results.json"
    summary_data = {
        "config": config,
        "total_sequences": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] in ["failed", "error", "timeout", "validation_failed"]),
        "total_time": sum(r["execution_time"] for r in results),
        "results": results
    }

    with open(json_file, 'w') as f:
        json.dump(summary_data, f, indent=2)

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_batch_processing(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for batch processing cyclic peptide sequences.

    Args:
        input_file: Path to file containing sequences (one per line or tab-separated ID\\tSEQUENCE)
        output_dir: Directory to save outputs (will be created if not exists)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Summary of processing results
            - output_dir: Path to output directory
            - summary_files: Paths to summary files
            - metadata: Execution metadata

    Example:
        >>> result = run_batch_processing("sequences.txt", "batch_output")
        >>> print(f"Processed {result['metadata']['successful']} sequences")
    """
    # Setup configuration
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Validate inputs
    input_file = Path(input_file)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Setup output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path("results") / "batch_processing"

    output_path.mkdir(parents=True, exist_ok=True)

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

    # Parse input sequences
    print(f"=== Batch Processing with ADCP ===")
    print(f"Input file: {input_file}")
    print(f"Output directory: {output_path}")
    print(f"Max workers: {config['max_workers']}")
    print()

    sequences = parse_sequences_file(input_file)
    print(f"Found {len(sequences)} sequences to process")

    if not sequences:
        raise ValueError(f"No valid sequences found in {input_file}")

    # Validate all sequences first
    valid_sequences = []
    validation_results = []

    for seq_id, sequence in sequences:
        is_valid, error_msg = validate_sequence(sequence)
        if is_valid:
            valid_sequences.append((seq_id, sequence))
        else:
            validation_results.append({
                "seq_id": seq_id,
                "sequence": sequence,
                "status": "validation_failed",
                "error": error_msg,
                "output_file": None,
                "execution_time": 0
            })
            print(f"⚠ Validation failed for {seq_id}: {error_msg}")

    print(f"Valid sequences: {len(valid_sequences)}")
    print(f"Invalid sequences: {len(validation_results)}")
    print()

    if not valid_sequences:
        raise ValueError("No valid sequences to process")

    # Run batch processing
    all_results = validation_results.copy()

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        # Create required files for ADCP
        print("Setting up batch processing environment...")
        create_dummy_transpoints(temp_dir)
        create_minimal_con_file(temp_dir)
        print("✓ Created minimal grid files")

        print(f"Processing {len(valid_sequences)} valid sequences...")
        start_time = time.time()

        if config['max_workers'] == 1:
            # Sequential processing
            for i, (seq_id, sequence) in enumerate(valid_sequences, 1):
                print(f"Processing {i}/{len(valid_sequences)}: {seq_id} ({sequence})")
                result = run_single_conformation_job(
                    seq_id, sequence, output_path, config, adcp_binary, temp_dir
                )
                all_results.append(result)

                if result["status"] == "success":
                    print(f"✓ Completed {seq_id}")
                else:
                    print(f"✗ Failed {seq_id}: {result['error']}")
        else:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=config['max_workers']) as executor:
                # Submit all jobs
                future_to_seq = {
                    executor.submit(
                        run_single_conformation_job,
                        seq_id, sequence, output_path, config, adcp_binary, temp_dir
                    ): (seq_id, sequence)
                    for seq_id, sequence in valid_sequences
                }

                # Collect results as they complete
                completed = 0
                for future in as_completed(future_to_seq):
                    seq_id, sequence = future_to_seq[future]
                    completed += 1

                    try:
                        result = future.result()
                        all_results.append(result)

                        if result["status"] == "success":
                            print(f"✓ Completed {completed}/{len(valid_sequences)}: {seq_id}")
                        else:
                            print(f"✗ Failed {completed}/{len(valid_sequences)}: {seq_id} ({result['error']})")

                    except Exception as e:
                        print(f"✗ Exception {completed}/{len(valid_sequences)}: {seq_id} ({e})")
                        all_results.append({
                            "seq_id": seq_id,
                            "sequence": sequence,
                            "status": "error",
                            "error": str(e),
                            "output_file": None,
                            "execution_time": 0
                        })

        total_time = time.time() - start_time

    # Save results
    save_batch_results(all_results, output_path, config)

    # Generate summary
    successful = sum(1 for r in all_results if r["status"] == "success")
    failed = len(all_results) - successful

    print(f"\n=== Batch processing completed ===")
    print(f"Total sequences: {len(all_results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Results saved to: {output_path}")

    return {
        "result": f"Processed {len(all_results)} sequences ({successful} successful, {failed} failed)",
        "output_dir": str(output_path),
        "summary_files": [
            str(output_path / "batch_summary.csv"),
            str(output_path / "batch_detailed_results.json")
        ],
        "metadata": {
            "total_sequences": len(all_results),
            "successful": successful,
            "failed": failed,
            "execution_time": total_time,
            "config": config
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
                       help='Input file containing peptide sequences (one per line or tab-separated)')
    parser.add_argument('--output', '-o',
                       help='Output directory for results')
    parser.add_argument('--config', '-c',
                       help='Config file (JSON)')
    parser.add_argument('--numsteps', type=int,
                       help=f'Number of MC steps per sequence (default: {DEFAULT_CONFIG["numsteps"]})')
    parser.add_argument('--max-workers', type=int,
                       help=f'Maximum parallel workers (default: {DEFAULT_CONFIG["max_workers"]})')
    parser.add_argument('--cyclic', action='store_true', default=None,
                       help='Enable cyclic constraints (default: True)')
    parser.add_argument('--no-cyclic', action='store_true',
                       help='Disable cyclic constraints')
    parser.add_argument('--disulfide', action='store_true',
                       help='Enable disulfide bridge constraints')
    parser.add_argument('--timeout', type=int,
                       help=f'Timeout per job in seconds (default: {DEFAULT_CONFIG["timeout_seconds"]})')
    parser.add_argument('--dry-run', action='store_true',
                       help='Parse input file and show what would be processed')

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
    if args.max_workers is not None:
        overrides['max_workers'] = args.max_workers
    if args.cyclic is not None:
        overrides['cyclic'] = args.cyclic
    if args.no_cyclic:
        overrides['cyclic'] = False
    if args.disulfide:
        overrides['disulfide'] = True
    if args.timeout:
        overrides['timeout_seconds'] = args.timeout

    if args.dry_run:
        print("Dry run mode - parsing sequences and showing processing plan:")
        try:
            sequences = parse_sequences_file(Path(args.input))
            print(f"\nFound {len(sequences)} sequences:")

            valid_count = 0
            for seq_id, sequence in sequences:
                is_valid, error_msg = validate_sequence(sequence)
                status = "✓" if is_valid else "✗"
                print(f"  {status} {seq_id}: {sequence} {f'({error_msg})' if not is_valid else ''}")
                if is_valid:
                    valid_count += 1

            print(f"\nValid sequences: {valid_count}")
            print(f"Config overrides: {overrides}")

        except Exception as e:
            print(f"Error during dry run: {e}")
            return 1

        return 0

    # Run batch processing
    try:
        result = run_batch_processing(
            input_file=args.input,
            output_dir=args.output,
            config=config,
            **overrides
        )

        print(f"\nSuccess: {result['result']}")
        print(f"Summary files: {', '.join(result['summary_files'])}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())