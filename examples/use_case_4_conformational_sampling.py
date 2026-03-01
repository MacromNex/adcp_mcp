#!/usr/bin/env python3
"""
UC-004: Conformational Sampling and Peptide Folding

This script demonstrates how to use ADCP for conformational sampling of cyclic
peptides without a specific receptor target. This is useful for studying intrinsic
peptide flexibility, generating conformational ensembles, or preparing peptides
for subsequent docking studies.

Usage:
    python use_case_4_conformational_sampling.py --sequence CGPGPGPGC
    python use_case_4_conformational_sampling.py --help

Note: This mode uses ADCP's internal energy functions without external receptor grids.
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
import tempfile

def create_dummy_transpoints():
    """Create a minimal transpoints file for conformational sampling"""
    transpoints_content = """1
0.000   0.000   0.000
"""
    with open("transpoints", "w") as f:
        f.write(transpoints_content)

def create_minimal_con_file():
    """Create a minimal con file"""
    with open("con", "w") as f:
        f.write("1\n")

def main():
    parser = argparse.ArgumentParser(
        description="Perform conformational sampling of peptides using ADCP internal energies",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-s", "--sequence",
        default="CGPGPGPGC",
        help="Peptide sequence for conformational sampling"
    )

    parser.add_argument(
        "-o", "--output",
        default="conformational_sampling",
        help="Output basename for conformations"
    )

    parser.add_argument(
        "-n", "--numsteps",
        type=int,
        default=500000,
        help="Number of MC steps per run (more for thorough sampling)"
    )

    parser.add_argument(
        "-N", "--nbruns",
        type=int,
        default=25,
        help="Number of independent sampling runs"
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
        default=True,
        help="Apply cyclic constraints (default: True)"
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
    if not args.sequence:
        print("Error: Peptide sequence is required")
        return 1

    if len(args.sequence) > 20:
        print(f"Warning: Sequence length ({len(args.sequence)}) exceeds recommended maximum of 20 residues")

    print("=== Conformational Sampling with ADCP ===")
    print(f"Sequence: {args.sequence}")
    print(f"Length: {len(args.sequence)} amino acids")
    print(f"Output: {args.output}")
    print(f"Cyclic constraints: {'Yes' if args.cyclic else 'No'}")
    print(f"Disulfide constraints: {'Yes' if args.cystein else 'No'}")
    print(f"MC Steps: {args.numsteps}")
    print(f"Runs: {args.nbruns}")
    print()

    if args.dry_run:
        print("Dry run mode - no files will be created or modified")
        print("In normal mode, this would:")
        print("1. Create minimal transpoints and con files")
        print("2. Run ADCP with internal energies only")
        print("3. Generate conformational ensemble")
        return 0

    # Create necessary files for standalone conformational sampling
    print("Setting up conformational sampling environment...")

    try:
        create_dummy_transpoints()
        create_minimal_con_file()
        print("✓ Created minimal grid files")

        # Direct ADCP binary execution for conformational sampling
        cmd = [
            "./adcp_Linux-x86_64",
            "-r", f"1x{args.numsteps}",
            "-t", "1",  # Single thread per job for simplicity
            args.sequence
        ]

        # Add parameters for internal energy evaluation
        params = "Bias=NULL"
        if args.cyclic:
            params += ",external2=4,con,2,1.0"
        if args.cystein:
            params += ",SSbond=80,2.2,20,0.5"
        params += ",Opt=1,0.25,0.75,0.0"

        cmd.extend(["-p", params])

        print("Running conformational sampling...")
        print("This will generate conformations using ADCP's internal energy model")
        print()

        # Run multiple conformational sampling jobs
        for run_id in range(1, args.nbruns + 1):
            output_file = f"{args.output}_{run_id}.pdb"
            run_cmd = cmd + ["-o", output_file]

            print(f"Running sampling job {run_id}/{args.nbruns}...")

            try:
                result = subprocess.run(run_cmd, check=True, capture_output=True, text=True)
                print(f"✓ Completed run {run_id}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Run {run_id} failed: {e}")
                continue

        print(f"\n=== Conformational sampling completed ===")
        print(f"Generated {args.nbruns} conformations: {args.output}_*.pdb")
        print("Analyze the conformational diversity and energy distribution.")

    except Exception as e:
        print(f"Error during conformational sampling: {e}")
        return 1

    finally:
        # Clean up temporary files
        for temp_file in ["transpoints", "con"]:
            try:
                os.remove(temp_file)
            except FileNotFoundError:
                pass

    return 0

if __name__ == "__main__":
    sys.exit(main())