"""
Shared utilities for the MCP server.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json


def load_config(config_file: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from JSON file or return defaults."""
    if config_file and config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    return {}


def validate_sequence(sequence: str) -> tuple[bool, str]:
    """Validate peptide sequence and return (is_valid, error_message)."""
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")

    if not sequence:
        return False, "Empty sequence"

    # Check if all characters are valid amino acids
    invalid_chars = [aa for aa in sequence.upper() if aa not in valid_aa]
    if invalid_chars:
        return False, f"Invalid amino acids: {', '.join(set(invalid_chars))}"

    # Check length constraints (from script defaults)
    if len(sequence) < 6:
        return False, "Sequence too short (minimum 6 amino acids)"
    if len(sequence) > 20:
        return False, "Sequence too long (maximum 20 amino acids)"

    return True, ""


def find_adcp_binary(mcp_root: Path) -> Optional[Path]:
    """Find the ADCP binary in common locations."""
    binary_name = "adcp_Linux-x86_64"
    candidates = [
        mcp_root / binary_name,
        Path(binary_name),
        Path(f"./{binary_name}")
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None