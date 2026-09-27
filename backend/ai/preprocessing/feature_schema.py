"""
Feature Schema definition and validator for SATHI AI Pipeline.
Encapsulates feature names, feature order, embedding dimension, and validation logic.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class FeatureSchema:
    """Encapsulates feature ordering, embedding dimension, and schema validation."""

    def __init__(
        self,
        feature_names: List[str],
        categorical_values: Optional[Dict[str, List[str]]] = None,
        embedding_dim: int = 64,
        schema_version: str = "v2.0_onehot"
    ) -> None:
        self.feature_names = feature_names
        self.categorical_values = categorical_values or {}
        self.embedding_dim = embedding_dim
        self.schema_version = schema_version

    @property
    def feature_count(self) -> int:
        return len(self.feature_names)

    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary for JSON serialization."""
        return {
            "schema_version": self.schema_version,
            "feature_count": self.feature_count,
            "embedding_dim": self.embedding_dim,
            "feature_names": self.feature_names,
            "categorical_values": self.categorical_values
        }

    def save(self, filepath: Path) -> None:
        """Save schema definition to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> "FeatureSchema":
        """Load schema definition from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(
            feature_names=data.get("feature_names", []),
            categorical_values=data.get("categorical_values", {}),
            embedding_dim=data.get("embedding_dim", 64),
            schema_version=data.get("schema_version", "v2.0_onehot")
        )

    def validate_feature_schema(self, incoming_names: List[str]) -> bool:
        """
        Validate incoming feature names against stored authoritative schema.
        Raises ValueError loudly if order, names, or feature counts do not match exactly.
        """
        if len(incoming_names) != len(self.feature_names):
            raise ValueError(
                f"Feature count mismatch: expected {len(self.feature_names)}, got {len(incoming_names)}"
            )

        for idx, (expected, incoming) in enumerate(zip(self.feature_names, incoming_names)):
            if expected != incoming:
                raise ValueError(
                    f"Feature order mismatch at index {idx}: expected '{expected}', got '{incoming}'"
                )

        return True
