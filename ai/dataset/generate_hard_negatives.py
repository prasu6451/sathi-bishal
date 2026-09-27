import json
import random

random.seed(42)

# Load a reference feature structure from line 1 of test.jsonl
with open("c:/Users/PK/Desktop/sathi/ai/dataset/test.jsonl", "r") as f:
    template = json.loads(f.readline())

records = []

# Generate 300 synthetic hard negative records
for i in range(300):
    rec = json.loads(json.dumps(template))
    
    # Target label: strictly 0 (no landslide)
    rec["label"] = {
        "landslide": 0,
        "risk_level": "LOW",
        "risk_score": 10
    }
    rec["dataset_type"] = "SYNTHETIC_STRESS_TEST"
    rec["id"] = f"SYNTH_HN_{i+1:04d}"
    
    # High-risk terrain (steep slope, high elevation)
    slope = round(random.uniform(25.0, 48.0), 2)
    elev = round(random.uniform(1200.0, 2400.0), 1)
    rec["terrain"]["slope"] = slope
    rec["terrain"]["elevation"] = elev
    rec["terrain"]["twi"] = round(random.uniform(7.0, 11.0), 2)
    
    # Heavy rainfall triggers
    r_1h = round(random.uniform(15.0, 45.0), 1)
    r_24h = round(random.uniform(50.0, 150.0), 1)
    r_3d = round(r_24h + random.uniform(40.0, 120.0), 1)
    r_7d = round(r_3d + random.uniform(80.0, 200.0), 1)
    r_14d = round(r_7d + random.uniform(100.0, 300.0), 1)
    
    rec["rainfall"]["rain_1h"] = r_1h
    rec["rainfall"]["rain_24h"] = r_24h
    rec["rainfall"]["rain_3d"] = r_3d
    rec["rainfall"]["rain_7d"] = r_7d
    rec["rainfall"]["rain_14d"] = r_14d
    
    # High soil saturation
    sm = round(random.uniform(0.42, 0.65), 3)
    rec["soil"]["moisture_0_7cm"] = sm
    rec["soil"]["moisture_7_28cm"] = round(sm * 0.95, 3)
    
    records.append(rec)

# Write to hard_negative_stress_test.jsonl
with open("c:/Users/PK/Desktop/sathi/ai/dataset/hard_negative_stress_test.jsonl", "w") as f:
    for r in records:
        f.write(json.dumps(r) + "\n")

print(f"Successfully generated {len(records)} hard negative stress test records.")
