def notify(anomalies: dict, sample: dict):
    if not anomalies:
        return

    machine = sample.get("machine", "UNKNOWN")

    print(f"[ALERTE] Machine {machine} anomalies détectées : {anomalies}")


