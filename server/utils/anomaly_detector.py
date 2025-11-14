THRESHOLDS = {
    "cpu": 88.0,
    "ram": 80.0,
    "disk": 90.0
}

def check_anomalies(sample: dict) -> dict:
    anomalies = {}

    for key, limit in THRESHOLDS.items():
        val = sample.get(key)
        if isinstance(val, (int, float)) and val >= limit:
            anomalies[key] = {"value": val, "threshold": limit}

    return anomalies


