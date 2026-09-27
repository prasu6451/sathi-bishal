# AlphaEarth Foundations Earth Engine Extraction

This package provides a clean, robust interface for extracting 64-dimensional pretrained AlphaEarth satellite embeddings via Google Earth Engine (GEE).

## Earth Engine Setup & Authentication

1. **Install Earth Engine API**:
   ```bash
   pip install earthengine-api
   ```

2. **Authenticate with GEE**:
   Run the interactive Earth Engine CLI command:
   ```bash
   earthengine authenticate
   ```
   Follow the browser prompt to log into your Google Earth Engine account.

3. **Set Project Identifier**:
   Set your registered GEE Cloud Project ID as an environment variable:
   ```bash
   export EARTHENGINE_PROJECT="your-gee-project-id"
   # On Windows PowerShell:
   $env:EARTHENGINE_PROJECT="sathi-507115"
   ```

4. **Configuring the Official AlphaEarth Asset ID**:
   The default configured collection path in `config.py` is:
   `ALPHAEARTH_EE_ASSET_ID = "projects/google/alphaearth/foundations/v1"`

   If your organization has access to a custom or specific GEE Asset ID for AlphaEarth embeddings, override it via environment variable:
   ```bash
   export ALPHAEARTH_EE_ASSET_ID="projects/your-org/assets/alphaearth_v1"
   ```

## Usage Example

```python
from data_collection.alphaearth import AlphaEarthExporter

exporter = AlphaEarthExporter()
# Initialize GEE session
exporter.initialize()

# Sample embedding at latitude/longitude coordinate
embedding = exporter.sample_embedding(
    latitude=30.3165,
    longitude=78.0322,
    date_str="2025-08-20"
)

print(f"Retrieved {len(embedding)}-dimensional embedding vector.")
```
