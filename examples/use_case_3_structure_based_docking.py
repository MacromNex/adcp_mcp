#!/usr/bin/env python3
"""
UC-003: Structure-Based Peptide Docking

This script demonstrates how to dock peptides starting from an existing 3D structure
(PDB file) rather than just a sequence. This is useful when you have an initial
peptide conformation that you want to refine or dock into a receptor.

Usage:
    python use_case_3_structure_based_docking.py --input peptide.pdb --target receptor.trg
    python use_case_3_structure_based_docking.py --help

Requirements:
    - Initial peptide structure in PDB format
    - Target receptor file (.trg format from AGFR)
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def validate_pdb_file(pdb_file):
    """Basic validation of PDB file"""
    if not Path(pdb_file).exists():
        raise FileNotFoundError(f"PDB file not found: {pdb_file}")

    # Check if file has some basic PDB content
    with open(pdb_file, 'r') as f:
        content = f.read()
        if not any(line.startswith(('ATOM', 'HETATM')) for line in content.split('\n')):
            raise ValueError(f"File does not appear to contain PDB atom records: {pdb_file}")

    return True

def main():
    parser = argparse.ArgumentParser(
        description="Dock a peptide from initial PDB structure using ADCP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-i", "--input",
        default="examples/data/structures/sample_peptide.pdb",
        help="Initial peptide structure in PDB format"
    )

    parser.add_argument(
        "-t", "--target",
        default="examples/data/targets/sample_receptor.trg",
        help="Target receptor file (.trg format from AGFR)"
    )

    parser.add_argument(
        "-o", "--output",
        default="structure_based_docking",
        help="Output basename for docked structures"
    )

    parser.add_argument(
        "-n", "--numsteps",
        type=int,
        default=200000,
        help="Number of MC steps per run (more for refinement)"
    )

    parser.add_argument(
        "-N", "--nbruns",
        type=int,
        default=20,
        help="Number of independent docking runs"
    )

    parser.add_argument(
        "-c", "--maxcores",
        type=int,
        default=4,
        help="Maximum number of CPU cores to use"
    )

    parser.add_argument(
        "--cyclic",
        action="store_true",
        help="Treat peptide as cyclic (add cyclic constraints)"
    )

    parser.add_argument(
        "--cystein",
        action="store_true",
        help="Enable disulfide bridge constraints"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the command that would be executed without running it"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.dry_run:
        try:
            validate_pdb_file(args.input)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            print("Note: This example requires a PDB file with the peptide structure")
            print("For demonstration purposes, you can use --dry-run to see the command")
            return 1

        if not Path(args.target).exists():
            print(f"Error: Target file '{args.target}' not found")
            print("Note: This example requires a receptor target file (.trg) from AGFR")
            print("For demonstration purposes, you can use --dry-run to see the command")
            return 1

    # Construct ADCP command
    cmd = [
        "python", "runADCP.py",
        "-i", args.input,
        "-t", args.target,
        "-o", args.output,
        "-n", str(args.numsteps),
        "-N", str(args.nbruns),
        "-c", str(args.maxcores)
    ]

    # Add optional flags
    if args.cyclic:
        cmd.append("--cyclic")
    if args.cystein:
        cmd.append("--cystein")

    if args.dry_run:
        cmd.append("--dryRun")

    print("=== Structure-Based Peptide Docking ===")
    print(f"Input PDB: {args.input}")
    print(f"Target: {args.target}")
    print(f"Output: {args.output}")
    print(f"Cyclic constraints: {'Yes' if args.cyclic else 'No'}")
    print(f"Disulfide constraints: {'Yes' if args.cystein else 'No'}")
    print(f"MC Steps: {args.numsteps}")
    print(f"Runs: {args.nbruns}")
    print()

    if args.dry_run:
        print("Dry run - Command that would be executed:")
        print(" ".join(cmd))
        return 0

    print("Executing ADCP with initial structure...")
    print("Command:", " ".join(cmd))
    print()

    try:
        # Run ADCP
        result = subprocess.run(cmd, check=True)

        print(f"\n=== Structure-based docking completed successfully ===")
        print(f"Output files: {args.output}_*.pdb")
        print(f"Compare with initial structure: {args.input}")
        print(f"Check the lowest energy conformations for structural improvements.")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"Error running ADCP: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nDocking interrupted by user")
        return 1

if __name__ == "__main__":
    sys.exit(main())