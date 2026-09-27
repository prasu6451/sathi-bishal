"""
JSONL streaming dataset loader and saver with error handling and logging.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)


def load_jsonl_dataset(
    file_path: Union[str, Path],
    ignore_errors: bool = True
) -> List[Dict[str, Any]]:
    """
    Read and parse a JSONL file line-by-line into a list of dictionaries.

    Args:
        file_path: Path to the .jsonl file.
        ignore_errors: If True, log warnings for malformed lines instead of raising exception.

    Returns:
        List of parsed sample dictionaries.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"JSONL dataset file not found at: {path}")

    records: List[Dict[str, Any]] = []
    line_number = 0

    logger.info(f"Loading JSONL dataset from: {path}")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_number += 1
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            try:
                record = json.loads(stripped)
                if isinstance(record, dict):
                    records.append(record)
                else:
                    msg = f"Line {line_number} in {path} is not a valid JSON object."
                    if ignore_errors:
                        logger.warning(msg)
                    else:
                        raise ValueError(msg)
            except json.JSONDecodeError as err:
                msg = f"Malformed JSON on line {line_number} in {path}: {err}"
                if ignore_errors:
                    logger.warning(msg)
                else:
                    raise ValueError(msg) from err

    logger.info(f"Loaded {len(records)} valid records from {path} (total lines: {line_number}).")
    return records


def save_jsonl_dataset(
    records: List[Dict[str, Any]],
    file_path: Union[str, Path]
) -> None:
    """
    Write a list of dictionaries to a JSONL file.

    Args:
        records: List of sample dictionaries.
        file_path: Destination file path.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    logger.info(f"Saved {len(records)} records to {path}")
