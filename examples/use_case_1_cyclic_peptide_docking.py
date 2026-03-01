#!/usr/bin/env python3
"""
UC-001: Cyclic Peptide Sequence Docking

This script demonstrates how to dock a cyclic peptide from sequence using ADCP.
ADCP will perform Monte Carlo sampling to find optimal conformations of the
cyclic peptide in the context of a receptor binding site.

Usage:
    python use_case_1_cyclic_peptide_docking.py --sequence GPGPGPGP --target receptor.trg --output cycpep_dock
    python use_case_1_cyclic_peptide_docking.py --help

Requirements:
    - Target receptor file (.trg format from AGFR)
    - Peptide sequence (single letter amino acid codes)
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Dock a cyclic peptide from sequence using ADCP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-s", "--sequence",
        default="GPGPGPGP",
        help="Peptide sequence in single-letter amino acid codes"
    )

    parser.add_argument(
        "-t", "--target",
        default="examples/data/targets/sample_receptor.trg",
        help="Target receptor file (.trg format from AGFR)"
    )

    parser.add_argument(
        "-o", "--output",
        default="cyclic_peptide_docking",
        help="Output basename for docked structures"
    )

    parser.add_argument(
        "-n", "--numsteps",
        type=int,
        default=100000,
        help="Number of MC steps per run (default for quick testing)"
    )

    parser.add_argument(
        "-N", "--nbruns",
        type=int,
        default=10,
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

    if not args.target.endswith('.trg'):
        print("Warning: Target file should be in .trg format (from AGFR)")

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
        "--cyclic",  # Enable cyclic peptide mode
        "-n", str(args.numsteps),
        "-N", str(args.nbruns),
        "-c", str(args.maxcores)
    ]

    if args.dry_run:
        cmd.append("--dryRun")

    print("=== Cyclic Peptide Docking with ADCP ===")
    print(f"Sequence: {args.sequence}")
    print(f"Target: {args.target}")
    print(f"Output: {args.output}")
    print(f"Cyclic: Yes")
    print(f"MC Steps: {args.numsteps}")
    print(f"Runs: {args.nbruns}")
    print()

    if args.dry_run:
        print("Dry run - Command that would be executed:")
        print(" ".join(cmd))
        return 0

    print("Executing ADCP...")
    print("Command:", " ".join(cmd))
    print()

    try:
        # Run ADCP
        result = subprocess.run(cmd, check=True)

        print(f"\n=== Docking completed successfully ===")
        print(f"Output files: {args.output}_*.pdb")
        print(f"Check the lowest energy conformations in the output files.")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"Error running ADCP: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nDocking interrupted by user")
        return 1

if __name__ == "__main__":
    sys.exit(main())