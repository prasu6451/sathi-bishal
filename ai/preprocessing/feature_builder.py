"""
Feature Builder module for SATHI AI Pipeline.
Transforms raw sample JSON dictionaries into flat numerical feature matrices.
Implements One-Hot Encoding for categorical features, eliminates post-event data leakage,
and enforces deterministic feature ordering matching FeatureSchema.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

from ai.config.config import get_default_config, Config
from ai.preprocessing.feature_schema import FeatureSchema

logger = logging.getLogger(__name__)


class FeatureBuilder:
    """Extracts, One-Hot encodes, and flattens geospatial samples into numerical matrices."""

    def __init__(self, schema: Optional[FeatureSchema] = None) -> None:
        self.cfg: Config = get_default_config()
        self.embedding_dim = self.cfg.ALPHAEARTH_EMBEDDING_DIM

        if schema is not None:
            self.schema = schema
            self.feature_names = schema.feature_names
            self.categorical_values = schema.categorical_values
        else:
            # Build One-Hot encoded feature names schema
            self.categorical_values = self.cfg.KNOWN_CATEGORICAL_VALUES
            self.feature_names = self._build_feature_name_list()
            self.schema = FeatureSchema(
                feature_names=self.feature_names,
                categorical_values=self.categorical_values,
                embedding_dim=self.embedding_dim
            )

    def _build_feature_name_list(self) -> List[str]:
        """Construct deterministic list of all One-Hot encoded feature names."""
        names = []
        # 1. AlphaEarth embedding dimensions (alphaearth_0 .. alphaearth_63)
        for i in range(self.embedding_dim):
            names.append(f"alphaearth_{i}")

        # 2. Numerical environmental and spatial features
        names.extend(self.cfg.NUMERICAL_FEATURES)

        # 3. One-Hot encoded categorical features
        for cat_col, vals in self.categorical_values.items():
            for v in vals:
                names.append(f"{cat_col}_{v}")

        return names

    def extract_sample_features(self, record: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract flat One-Hot encoded key-value feature dictionary from raw record.
        Excludes post-event citizen reports to prevent temporal data leakage.
        """
        features: Dict[str, float] = {}

        # 1. AlphaEarth Embeddings (flattened 64 dims)
        alpha = record.get("alphaearth", {})
        embedding = alpha.get("embedding", []) if isinstance(alpha, dict) else []
        for i in range(self.embedding_dim):
            key = f"alphaearth_{i}"
            if isinstance(embedding, list) and i < len(embedding):
                try:
                    features[key] = float(embedding[i])
                except (ValueError, TypeError):
                    features[key] = np.nan
            else:
                features[key] = np.nan

        # 2. Terrain Features
        terrain = record.get("terrain", {}) if isinstance(record.get("terrain"), dict) else {}
        features["terrain_elevation"] = self._to_float(terrain.get("elevation"))
        features["terrain_slope"] = self._to_float(terrain.get("slope"))
        features["terrain_aspect"] = self._to_float(terrain.get("aspect"))
        features["terrain_curvature"] = self._to_float(terrain.get("curvature"))
        features["terrain_twi"] = self._to_float(terrain.get("twi"))

        # 3. Rainfall Features
        rainfall = record.get("rainfall", {}) if isinstance(record.get("rainfall"), dict) else {}
        features["rainfall_rain_1h"] = self._to_float(rainfall.get("rain_1h"))
        features["rainfall_rain_24h"] = self._to_float(rainfall.get("rain_24h"))
        features["rainfall_rain_3d"] = self._to_float(rainfall.get("rain_3d"))
        features["rainfall_rain_7d"] = self._to_float(rainfall.get("rain_7d"))
        features["rainfall_rain_14d"] = self._to_float(rainfall.get("rain_14d"))

        # 4. Soil Features
        soil = record.get("soil", {}) if isinstance(record.get("soil"), dict) else {}
        features["soil_moisture_0_7cm"] = self._to_float(soil.get("moisture_0_7cm"))
        features["soil_moisture_7_28cm"] = self._to_float(soil.get("moisture_7_28cm"))

        # 5. Satellite Features
        satellite = record.get("satellite", {}) if isinstance(record.get("satellite"), dict) else {}
        features["satellite_ndvi"] = self._to_float(satellite.get("ndvi"))
        features["satellite_sar_displacement"] = self._to_float(satellite.get("sar_displacement"))

        # 6. Geology Features
        geology = record.get("geology", {}) if isinstance(record.get("geology"), dict) else {}
        features["geology_lineament_distance_m"] = self._to_float(geology.get("lineament_distance_m"))

        # 7. Infrastructure Features
        infra = record.get("infrastructure", {}) if isinstance(record.get("infrastructure"), dict) else {}
        features["infrastructure_distance_to_road_m"] = self._to_float(infra.get("distance_to_road_m"))
        features["infrastructure_distance_to_stream_m"] = self._to_float(infra.get("distance_to_stream_m"))
        features["infrastructure_distance_to_bridge_m"] = self._to_float(infra.get("distance_to_bridge_m"))
        features["infrastructure_distance_to_hospital_m"] = self._to_float(infra.get("distance_to_hospital_m"))
        features["infrastructure_distance_to_village_m"] = self._to_float(infra.get("distance_to_village_m"))

        # 8. Population Density
        pop = record.get("population", {}) if isinstance(record.get("population"), dict) else {}
        features["population_density"] = self._to_float(pop.get("density"))

        # 9. Historical Landslide Features
        hist = record.get("historical", {}) if isinstance(record.get("historical"), dict) else {}
        features["historical_previous_landslide"] = self._bool_to_float(hist.get("previous_landslide"))
        features["historical_landslide_count_nearby"] = self._to_float(hist.get("landslide_count_nearby"))

        # 10. IoT Ingested Sensors
        iot = record.get("iot", {}) if isinstance(record.get("iot"), dict) else {}
        features["iot_rainfall_mm"] = self._to_float(iot.get("rainfall_mm"))
        features["iot_soil_moisture"] = self._to_float(iot.get("soil_moisture"))

        # 11. One-Hot Encoded Categorical Features
        lith_val = str(geology.get("lithology", "unknown")).lower().strip()
        geom_val = str(geology.get("geomorphology", "unknown")).lower().strip()
        land_use = record.get("land_use", {}) if isinstance(record.get("land_use"), dict) else {}
        lulc_val = str(land_use.get("class", "unknown")).lower().strip()

        for cat_col, raw_val in [
            ("geology_lithology", lith_val),
            ("geology_geomorphology", geom_val),
            ("land_use_class", lulc_val)
        ]:
            known_vals = self.categorical_values.get(cat_col, [])
            match_found = False
            for v in known_vals:
                col_name = f"{cat_col}_{v}"
                if raw_val == v:
                    features[col_name] = 1.0
                    match_found = True
                else:
                    features[col_name] = 0.0

            if not match_found and f"{cat_col}_unknown" in features:
                features[f"{cat_col}_unknown"] = 1.0

        return features

    def transform_record(self, record: Dict[str, Any]) -> np.ndarray:
        """Convert a single record dictionary into a 1D numpy array matching schema feature names."""
        feat_dict = self.extract_sample_features(record)
        vector = []
        for name in self.feature_names:
            val = feat_dict.get(name, np.nan)
            vector.append(val)
        return np.array(vector, dtype=np.float32)

    def transform_records(
        self,
        records: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Convert a list of raw sample dictionaries into feature matrix X and label vector y."""
        X_list = []
        y_list = []
        has_labels = True

        for rec in records:
            vec = self.transform_record(rec)
            X_list.append(vec)

            label_dict = rec.get("label")
            if isinstance(label_dict, dict) and "landslide" in label_dict:
                y_list.append(int(label_dict["landslide"]))
            else:
                has_labels = False

        X = np.array(X_list, dtype=np.float32) if X_list else np.empty((0, len(self.feature_names)), dtype=np.float32)
        y = np.array(y_list, dtype=np.int32) if has_labels and y_list else None

        return X, y

    @staticmethod
    def _to_float(val: Any) -> float:
        """Safe float conversion helper returning np.nan for missing/invalid values."""
        if val is None:
            return np.nan
        try:
            return float(val)
        except (ValueError, TypeError):
            return np.nan

    @staticmethod
    def _bool_to_float(val: Any) -> float:
        """Convert boolean or flag to float (1.0 or 0.0)."""
        if val is None:
            return np.nan
        if isinstance(val, bool):
            return 1.0 if val else 0.0
        try:
            f = float(val)
            return 1.0 if f > 0 else 0.0
        except (ValueError, TypeError):
            return np.nan
