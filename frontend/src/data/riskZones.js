/**
 * Disaster risk zone data categorized by risk levels:
 * CRITICAL (Red), HIGH (Orange), FLOOD PLAIN (Yellow), and LOW (Green).
 */

export const MAP_CENTER = [26.15, 91.75];
export const MAP_ZOOM = 10;

export const riskZones = [
  // 1. Critical Risk Zone (Red)
  {
    id: 'zone-critical-1',
    name: 'Meghalaya Foothills Slope',
    type: 'landslide',
    risk_level: 'CRITICAL',
    risk_category: 'CRITICAL',
    landslide_probability: 0.94,
    coordinates: [
      [25.98, 91.82],
      [26.02, 91.90],
      [25.99, 91.96],
      [25.93, 91.92],
      [25.94, 91.84],
    ],
    telemetry: {
      temperature: 24.2,
      humidity: 94,
      soil_moisture: 0.68,
      rainfall_mm: 58.0
    }
  },

  // 2. High Risk Zone (Orange)
  {
    id: 'zone-high-1',
    name: 'Ri-Bhoi Hill Slopes',
    type: 'landslide',
    risk_level: 'HIGH',
    risk_category: 'HIGH',
    landslide_probability: 0.76,
    coordinates: [
      [25.90, 91.65],
      [25.95, 91.72],
      [25.93, 91.80],
      [25.87, 91.78],
      [25.86, 91.69],
    ],
    telemetry: {
      temperature: 25.1,
      humidity: 88,
      soil_moisture: 0.58,
      rainfall_mm: 41.2
    }
  },

  // 3. Flood Plain Risk Zone (Yellow)
  {
    id: 'zone-floodplain-1',
    name: 'Brahmaputra Floodplain – West',
    type: 'flood',
    risk_level: 'FLOOD PLAIN',
    risk_category: 'FLOOD_PLAIN',
    landslide_probability: 0.45,
    coordinates: [
      [26.22, 91.55],
      [26.28, 91.62],
      [26.25, 91.72],
      [26.18, 91.70],
      [26.15, 91.60],
    ],
    telemetry: {
      temperature: 28.2,
      humidity: 86,
      soil_moisture: 0.52,
      rainfall_mm: 32.5
    }
  },
  {
    id: 'zone-floodplain-2',
    name: 'Brahmaputra Floodplain – East',
    type: 'flood',
    risk_level: 'FLOOD PLAIN',
    risk_category: 'FLOOD_PLAIN',
    landslide_probability: 0.38,
    coordinates: [
      [26.12, 91.78],
      [26.18, 91.85],
      [26.20, 91.95],
      [26.14, 91.98],
      [26.08, 91.88],
    ],
    telemetry: {
      temperature: 27.5,
      humidity: 80,
      soil_moisture: 0.41,
      rainfall_mm: 18.0
    }
  },
  {
    id: 'zone-floodplain-sivasagar-nepali-kuti',
    name: 'Sivasagar Nepali Kuti Flood Zone',
    type: 'flood',
    risk_level: 'FLOOD PLAIN',
    risk_category: 'FLOOD_PLAIN',
    landslide_probability: 0.46,
    coordinates: [
      [26.975, 94.625],
      [26.992, 94.632],
      [26.988, 94.648],
      [26.972, 94.645],
      [26.970, 94.630],
    ],
    telemetry: {
      temperature: 27.8,
      humidity: 91,
      soil_moisture: 0.65,
      rainfall_mm: 52.0
    }
  },

  // 4. Low Risk Zone (Green)
  {
    id: 'zone-low-1',
    name: 'Kolong River Basin Lowland',
    type: 'flood',
    risk_level: 'LOW',
    risk_category: 'LOW',
    landslide_probability: 0.14,
    coordinates: [
      [26.05, 91.60],
      [26.10, 91.68],
      [26.08, 91.76],
      [26.02, 91.73],
      [26.00, 91.64],
    ],
    telemetry: {
      temperature: 26.8,
      humidity: 74,
      soil_moisture: 0.32,
      rainfall_mm: 5.2
    }
  },
];
