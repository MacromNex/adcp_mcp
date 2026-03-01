#!/usr/bin/env python3
"""
UC-005: Batch Processing of Multiple Peptide Sequences

This script demonstrates how to process multiple cyclic peptide sequences
in batch mode. This is useful for virtual screening, SAR analysis, or
when comparing multiple peptide variants.

Usage:
    python use_case_5_batch_processing.py --sequences sequences.txt --target receptor.trg
    python use_case_5_batch_processing.py --help

Requirements:
    - Input file with peptide sequences (one per line)
    - Target receptor file (.trg format from AGFR)
"""

import sys
import os
import argparse
import subprocess
import concurrent.futures
import csv
from pathlib import Path
import time

def parse_sequences_file(sequences_file):
    """Parse sequences from input file"""
    sequences = []

    with open(sequences_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Handle different formats
            if '\t' in line or ',' in line:
                # Tab or comma separated: ID, sequence
                parts = line.replace(',', '\t').split('\t')
                if len(parts) >= 2:
                    seq_id = parts[0].strip()
                    sequence = parts[1].strip().upper()
                else:
                    seq_id = f"seq_{line_num}"
                    sequence = parts[0].strip().upper()
            else:
                # Just sequence
                seq_id = f"seq_{line_num:03d}"
                sequence = line.upper()

            # Basic validation
            if not all(aa in 'ACDEFGHIKLMNPQRSTVWY' for aa in sequence):
                print(f"Warning: Invalid amino acids in sequence {seq_id}: {sequence}")
                continue

            sequences.append((seq_id, sequence))

    return sequences

def dock_single_peptide(seq_id, sequence, target, output_dir, args):
    """Dock a single peptide sequence"""

    print(f"Processing {seq_id}: {sequence}")

    # Create output directory for this sequence
    seq_output_dir = Path(output_dir) / seq_id
    seq_output_dir.mkdir(exist_ok=True)

    # Construct ADCP command
    cmd = [
        "python", "runADCP.py",
        "-s", sequence,
        "-t", target,
        "-o", str(seq_output_dir / seq_id),
        "-n", str(args.numsteps),
        "-N", str(args.nbruns),
        "-c", "1",  # Use single core per sequence for parallel processing
        "--overwriteFiles"  # Allow overwriting
    ]

    # Add constraints
    if args.cyclic:
        cmd.append("--cyclic")
    if args.cystein and 'C' in sequence:
        cmd.append("--cystein")

    start_time = time.time()

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        duration = time.time() - start_time

        # Extract best energy from output
        best_energy = None
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'energy found is' in line:
                    try:
                        best_energy = float(line.split('energy found is')[1].split()[0])
                        break
                    except (IndexError, ValueError):
                        continue

        return {
            'seq_id': seq_id,
            'sequence': sequence,
            'status': 'success',
            'best_energy': best_energy,
            'duration': duration,
            'output_dir': str(seq_output_dir)
        }

    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        return {
            'seq_id': seq_id,
            'sequence': sequence,
            'status': 'failed',
            'error': str(e),
            'duration': duration,
            'output_dir': str(seq_output_dir)
        }

def main():
    parser = argparse.ArgumentParser(
        description="Batch process multiple peptide sequences using ADCP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--sequences",
        default="examples/data/sequences/batch_sequences.txt",
        help="File containing peptide sequences (one per line, or ID<tab>sequence)"
    )

    parser.add_argument(
        "-t", "--target",
        default="examples/data/targets/sample_receptor.trg",
        help="Target receptor file (.trg format from AGFR)"
    )

    parser.add_argument(
        "-o", "--output",
        default="batch_docking_results",
        help="Output directory for batch results"
    )

    parser.add_argument(
        "-n", "--numsteps",
        type=int,
        default=50000,
        help="Number of MC steps per run (reduced for batch processing)"
    )

    parser.add_argument(
        "-N", "--nbruns",
        type=int,
        default=5,
        help="Number of independent docking runs per sequence"
    )

    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of parallel processes"
    )

    parser.add_argument(
        "--cyclic",
        action="store_true",
        default=True,
        help="Apply cyclic constraints to all peptides"
    )

    parser.add_argument(
        "--cystein",
        action="store_true",
        help="Enable disulfide constraints for peptides with cysteines"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse sequences and show what would be processed"
    )

    args = parser.parse_args()

    # Parse sequences
    try:
        sequences = parse_sequences_file(args.sequences)
    except FileNotFoundError:
        print(f"Error: Sequences file not found: {args.sequences}")
        print("Create a file with peptide sequences, one per line:")
        print("GPGPGPGP")
        print("CGPGPGPGC")
        print("or with IDs:")
        print("peptide1\tGPGPGPGP")
        print("peptide2\tCGPGPGPGC")
        return 1

    if not sequences:
        print("Error: No valid sequences found in input file")
        return 1

    print(f"=== Batch Processing of {len(sequences)} Peptide Sequences ===")
    print(f"Sequences file: {args.sequences}")
    print(f"Target: {args.target}")
    print(f"Output directory: {args.output}")
    print(f"Parallel workers: {args.max_workers}")
    print(f"MC Steps per sequence: {args.numsteps}")
    print(f"Runs per sequence: {args.nbruns}")
    print()

    # Show sequences to be processed
    for i, (seq_id, sequence) in enumerate(sequences[:10]):  # Show first 10
        print(f"{i+1:3d}. {seq_id}: {sequence}")
    if len(sequences) > 10:
        print(f"     ... and {len(sequences) - 10} more")
    print()

    if args.dry_run:
        print("Dry run - sequences parsed successfully. No docking will be performed.")
        return 0

    # Check target file
    if not Path(args.target).exists():
        print(f"Error: Target file not found: {args.target}")
        return 1

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    # Run batch processing
    print("Starting batch processing...")
    results = []

    if args.max_workers == 1:
        # Sequential processing
        for seq_id, sequence in sequences:
            result = dock_single_peptide(seq_id, sequence, args.target, output_dir, args)
            results.append(result)
    else:
        # Parallel processing
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.max_workers) as executor:
            futures = []
            for seq_id, sequence in sequences:
                future = executor.submit(dock_single_peptide, seq_id, sequence, args.target, output_dir, args)
                futures.append(future)

            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error in parallel processing: {e}")

    # Generate summary report
    summary_file = output_dir / "batch_summary.csv"
    with open(summary_file, 'w', newline='') as csvfile:
        fieldnames = ['seq_id', 'sequence', 'length', 'status', 'best_energy', 'duration_seconds', 'output_dir']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({
                'seq_id': result['seq_id'],
                'sequence': result['sequence'],
                'length': len(result['sequence']),
                'status': result['status'],
                'best_energy': result.get('best_energy', 'N/A'),
                'duration_seconds': f"{result['duration']:.1f}",
                'output_dir': result['output_dir']
            })

    # Print summary
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful

    print(f"\n=== Batch Processing Summary ===")
    print(f"Total sequences: {len(sequences)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Summary report: {summary_file}")

    if successful > 0:
        # Find best sequences by energy
        successful_results = [r for r in results if r['status'] == 'success' and r['best_energy'] is not None]
        if successful_results:
            successful_results.sort(key=lambda x: x['best_energy'])
            print(f"\nTop 5 sequences by binding energy:")
            for i, result in enumerate(successful_results[:5]):
                print(f"{i+1}. {result['seq_id']}: {result['best_energy']:.2f} kcal/mol ({result['sequence']})")

    return 0

if __name__ == "__main__":
    sys.exit(main())