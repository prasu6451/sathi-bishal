"""
AlphaEarth Earth Engine extraction interface.
Handles GEE authentication, ROI querying, and vector extraction for AlphaEarth embeddings.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from ai.config.config import get_default_config

logger = logging.getLogger(__name__)

# Lazy check for Earth Engine dependency
try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    ee = None
    EE_AVAILABLE = False


class AlphaEarthExporter:
    """Interface for querying and sampling pretrained AlphaEarth embeddings from GEE."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        embedding_dim: int = 64
    ) -> None:
        cfg = get_default_config()
        self.project_id = project_id or cfg.EARTHENGINE_PROJECT
        self.asset_id = asset_id or cfg.ALPHAEARTH_EE_ASSET_ID
        self.embedding_dim = embedding_dim
        self._is_initialized = False

    def initialize(self) -> bool:
        """Authenticate and initialize Google Earth Engine."""
        if not EE_AVAILABLE:
            logger.warning("earthengine-api is not installed. Earth Engine extraction disabled.")
            return False

        try:
            ee.Initialize(project=self.project_id)
            self._is_initialized = True
            logger.info(f"Successfully initialized Earth Engine with project: {self.project_id}")
            return True
        except Exception as err:
            logger.warning(
                f"Failed to initialize Earth Engine project '{self.project_id}': {err}. "
                "Attempting default authentication fallback..."
            )
            try:
                ee.Initialize()
                self._is_initialized = True
                logger.info("Successfully initialized Earth Engine using default credentials.")
                return True
            except Exception as auth_err:
                logger.error(
                    f"Earth Engine authentication failed: {auth_err}. "
                    "Please run `earthengine authenticate` or set valid EARTHENGINE_PROJECT."
                )
                self._is_initialized = False
                return False

    def sample_embedding(
        self,
        latitude: float,
        longitude: float,
        date_str: str
    ) -> List[float]:
        """
        Sample 64-dimensional AlphaEarth embedding vector for a given point and date.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            date_str: Target date string (YYYY-MM-DD)

        Returns:
            List of float embedding values (length 64)
        """
        if not self._is_initialized:
            if not self.initialize():
                raise RuntimeError(
                    "Earth Engine is not initialized. Cannot extract AlphaEarth embeddings. "
                    "Ensure earthengine-api is installed and authenticated."
                )

        try:
            point = ee.Geometry.Point([longitude, latitude])
            # Load Earth Engine ImageCollection for AlphaEarth
            collection = (
                ee.ImageCollection(self.asset_id)
                .filterBounds(point)
                .filterDate(date_str)
            )

            image = collection.first()
            if image is None:
                raise ValueError(
                    f"No AlphaEarth image found at ({latitude}, {longitude}) on date {date_str}"
                )

            sampled = image.reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=10
            ).getInfo()

            # Extract 64-dim embedding values
            embedding = []
            for i in range(self.embedding_dim):
                key = f"alphaearth_{i}"
                val = sampled.get(key, sampled.get(f"b{i+1}", 0.0))
                embedding.append(float(val))

            return embedding

        except Exception as err:
            logger.error(f"Error sampling AlphaEarth embedding at ({latitude}, {longitude}): {err}")
            raise

    def export_roi_samples(
        self,
        bounding_box: Tuple[float, float, float, float],
        start_date: str,
        end_date: str,
        num_points: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Export embedding samples for a region of interest (ROI).

        Args:
            bounding_box: Tuple of (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date YYYY-MM-DD
            end_date: End date YYYY-MM-DD
            num_points: Number of spatial points to sample

        Returns:
            List of dictionary sample records containing location and embedding
        """
        if not self._is_initialized:
            if not self.initialize():
                raise RuntimeError("Earth Engine is not initialized.")

        logger.info(f"Sampling ROI {bounding_box} from {start_date} to {end_date}")
        # Structured placeholder for batch extraction tasks
        return []
