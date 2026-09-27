"""
Singleton AI Model Provider for FastAPI Application Lifespan.
Preloads trained LandslidePredictor once at startup.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

# Ensure project root directory is in sys.path so 'ai' package imports seamlessly
backend_dir = Path(__file__).resolve().parent.parent.parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class AIPredictionService:
    """Preloads trained XGBoost AI Model once during FastAPI startup."""

    def __init__(self) -> None:
        self.predictor = None
        self.is_loaded = False

    def load_model(self) -> None:
        """Preload trained model from ai/saved_models/current or configured directory."""
        try:
            from ai.inference.predictor import LandslidePredictor

            # Resolve model directory
            model_dir = (backend_dir / settings.MODEL_DIR).resolve()

            if not model_dir.exists():
                # Fallback to ai/saved_models/current or backend/ai/saved_models
                model_dir = project_root / "ai" / "saved_models" / "current"
                if not model_dir.exists():
                    model_dir = backend_dir / "ai" / "saved_models"

            self.predictor = LandslidePredictor(model_dir=model_dir)
            self.is_loaded = True
            logger.info(f"AI Model version '{self.predictor.model_version}' preloaded successfully from {model_dir}")

        except Exception as err:
            logger.error(f"Failed to preload AI Model: {err}")
            self.is_loaded = False

    def predict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference through preloaded AI Predictor."""
        if not self.is_loaded or self.predictor is None:
            raise RuntimeError("AI Model Predictor is not loaded.")
        return self.predictor.predict(record)


# Global Singleton Instance
ai_predictor_service = AIPredictionService()


def get_ai_predictor() -> AIPredictionService:
    """Dependency injector for AIPredictionService."""
    return ai_predictor_service
