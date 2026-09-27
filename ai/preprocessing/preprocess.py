"""
Preprocessing pipeline orchestrator.
High-level module combining loading, validation, feature extraction, and matrix construction.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union

import numpy as np

from ai.preprocessing.load_jsonl import load_jsonl_dataset
from ai.preprocessing.feature_schema import FeatureSchema
from ai.preprocessing.feature_builder import FeatureBuilder

logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """Orchestrates end-to-end dataset preprocessing for training and inference."""

    def __init__(self, schema: Optional[FeatureSchema] = None) -> None:
        self.feature_builder = FeatureBuilder(schema=schema)

    @property
    def schema(self) -> FeatureSchema:
        """Access underlying feature schema."""
        return self.feature_builder.schema

    def process_file(
        self,
        file_path: Union[str, Path]
    ) -> Tuple[np.ndarray, Optional[np.ndarray], List[Dict[str, Any]]]:
        """
        Process a JSONL file into matrix X, label vector y, and raw records list.

        Args:
            file_path: Path to input JSONL file.

        Returns:
            Tuple of (X feature matrix, y labels array or None, records list).
        """
        logger.info(f"Processing JSONL file: {file_path}")
        records = load_jsonl_dataset(file_path, ignore_errors=True)
        if not records:
            logger.warning(f"No records found in {file_path}")
            X = np.empty((0, len(self.schema.feature_names)), dtype=np.float32)
            return X, None, []

        X, y = self.feature_builder.transform_records(records)
        logger.info(f"Processed {len(records)} records -> X shape: {X.shape}, y present: {y is not None}")
        return X, y, records

    def process_single_record(self, record: Dict[str, Any]) -> np.ndarray:
        """
        Process a single raw JSON sample into a 2D feature matrix X of shape (1, N_features).

        Args:
            record: Raw sample dictionary.

        Returns:
            2D numpy array of shape (1, N_features).
        """
        vec = self.feature_builder.transform_record(record)
        return np.expand_dims(vec, axis=0)
