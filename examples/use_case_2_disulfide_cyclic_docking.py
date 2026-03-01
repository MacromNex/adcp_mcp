#!/usr/bin/env python3
"""
UC-002: Disulfide-Bridged Cyclic Peptide Docking

This script demonstrates how to dock cyclic peptides that are cyclized through
disulfide bridges (cysteine-cysteine bonds) rather than backbone cyclization.
This is common for many naturally occurring cyclic peptides.

Usage:
    python use_case_2_disulfide_cyclic_docking.py --sequence CGPGPGPGC --target receptor.trg
    python use_case_2_disulfide_cyclic_docking.py --help

Requirements:
    - Target receptor file (.trg format from AGFR)
    - Peptide sequence containing at least two cysteine residues
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def validate_cysteine_sequence(sequence):
    """Validate that sequence contains at least 2 cysteine residues for disulfide bridge"""
    cys_count = sequence.upper().count('C')
    if cys_count < 2:
        raise ValueError(f"Sequence must contain at least 2 cysteine (C) residues for disulfide bridging. Found: {cys_count}")
    if cys_count % 2 != 0:
        print(f"Warning: Odd number of cysteines ({cys_count}). One cysteine will be unpaired.")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Dock a disulfide-bridged cyclic peptide using ADCP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-s", "--sequence",
        default="CGPGPGPGC",
        help="Peptide sequence with cysteine residues for disulfide bridges"
    )

    parser.add_argument(
        "-t", "--target",
        default="examples/data/targets/sample_receptor.trg",
        help="Target receptor file (.trg format from AGFR)"
    )

    parser.add_argument(
        "-o", "--output",
        default="disulfide_cyclic_docking",
        help="Output basename for docked structures"
    )

    parser.add_argument(
        "-n", "--numsteps",
        type=int,
        default=150000,
        help="Number of MC steps per run (more steps for disulfide constraints)"
    )

    parser.add_argument(
        "-N", "--nbruns",
        type=int,
        default=15,
        help="Number of independent docking runs"
    )

    parser.add_argument(
        "-c", "--maxcores",
        type=int,
        default=4,
        help="Maximum number of CPU cores to use"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the command that would be executed without running it"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.sequence:
        print("Error: Peptide sequence is required")
        return 1

    try:
        validate_cysteine_sequence(args.sequence)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Check if target file exists (if not using dry run)
    if not args.dry_run and not Path(args.target).exists():
        print(f"Error: Target file '{args.target}' not found")
        print("Note: This example requires a receptor target file (.trg) from AGFR")
        print("For demonstration purposes, you can use --dry-run to see the command")
        return 1

    # Construct ADCP command
    cmd = [
        "python", "runADCP.py",
        "-s", args.sequence,
        "-t", args.target,
        "-o", args.output,
        "--cystein",  # Enable disulfide bridge mode
        "-n", str(args.numsteps),
        "-N", str(args.nbruns),
        "-c", str(args.maxcores)
    ]

    if args.dry_run:
        cmd.append("--dryRun")

    cys_count = args.sequence.upper().count('C')
    cys_positions = [i+1 for i, aa in enumerate(args.sequence.upper()) if aa == 'C']

    print("=== Disulfide-Bridged Cyclic Peptide Docking ===")
    print(f"Sequence: {args.sequence}")
    print(f"Length: {len(args.sequence)} amino acids")
    print(f"Cysteine count: {cys_count}")
    print(f"Cysteine positions: {cys_positions}")
    print(f"Target: {args.target}")
    print(f"Output: {args.output}")
    print(f"Disulfide bridges: Yes")
    print(f"MC Steps: {args.numsteps}")
    print(f"Runs: {args.nbruns}")
    print()

    if args.dry_run:
        print("Dry run - Command that would be executed:")
        print(" ".join(cmd))
        return 0

    print("Executing ADCP with disulfide bridge constraints...")
    print("Command:", " ".join(cmd))
    print()

    try:
        # Run ADCP
        result = subprocess.run(cmd, check=True)

        print(f"\n=== Disulfide-bridged docking completed successfully ===")
        print(f"Output files: {args.output}_*.pdb")
        print(f"Check the lowest energy conformations with proper disulfide bridges.")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"Error running ADCP: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nDocking interrupted by user")
        return 1

if __name__ == "__main__":
    sys.exit(main())