"""
Unit tests for JSONL loading, parsing, saving, and malformed line handling.
"""

import tempfile
from pathlib import Path
import pytest

from ai.preprocessing.load_jsonl import load_jsonl_dataset, save_jsonl_dataset


def test_load_valid_jsonl():
    content = '{"id": "s1", "val": 10}\n{"id": "s2", "val": 20}\n'
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        records = load_jsonl_dataset(tmp_path)
        assert len(records) == 2
        assert records[0]["id"] == "s1"
        assert records[1]["val"] == 20
    finally:
        tmp_path.unlink(missing_ok=True)


def test_load_malformed_jsonl_ignore_errors():
    content = '{"id": "s1", "val": 10}\nTHIS IS MALFORMED JSON\n{"id": "s3", "val": 30}\n'
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        records = load_jsonl_dataset(tmp_path, ignore_errors=True)
        # Should ignore the 2nd line and load 2 valid records
        assert len(records) == 2
        assert records[0]["id"] == "s1"
        assert records[1]["id"] == "s3"
    finally:
        tmp_path.unlink(missing_ok=True)


def test_load_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        load_jsonl_dataset(Path("non_existent_file_xyz.jsonl"))


def test_save_jsonl():
    records = [{"id": "a", "x": 1}, {"id": "b", "x": 2}]
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tmp:
        tmp_path = Path(tmp.name)

    try:
        save_jsonl_dataset(records, tmp_path)
        loaded = load_jsonl_dataset(tmp_path)
        assert len(loaded) == 2
        assert loaded[0]["id"] == "a"
    finally:
        tmp_path.unlink(missing_ok=True)
