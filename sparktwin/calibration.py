"""Conservative same-hardware / same-quantization benchmark interpolation.

No prediction is returned for uncalibrated or out-of-domain scenarios.
"""
from __future__ import annotations
import math
from statistics import median
from .model import normalize

REQUIRED = ["device", "params_b", "weight_bits", "context_tokens", "concurrency", "output_tokens_per_second", "source"]


def validate_record(raw):
    if not isinstance(raw, dict):
        raise ValueError("Benchmark must be an object")
    for key in REQUIRED:
        if key not in raw:
            raise ValueError(f"Missing benchmark field: {key}")
    r = {}
    for key in ["device", "source"]:
        v = raw[key]
        if not isinstance(v, str) or not 1 <= len(v.strip()) <= 250:
            raise ValueError(f"{key} must be 1–250 characters")
        r[key] = v.strip()
    for key, lo, hi in [("params_b", .01, 1000),("weight_bits",2,32),
                        ("context_tokens",128,1048576),("concurrency",1,1024),
                        ("output_tokens_per_second",.001,100000)]:
        v = raw[key]
        if isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) or not lo <= v <= hi:
            raise ValueError(f"{key} must be within [{lo}, {hi}]")
        r[key] = float(v)
    for key in ["context_tokens", "concurrency"]:
        if not r[key].is_integer():
            raise ValueError(f"{key} must be integral")
        r[key] = int(r[key])
    r["notes"] = str(raw.get("notes", ""))[:1000]
    return r


def calibrate(scenario, records):
    s = normalize(scenario)
    # Strictly match manufacturer profile; custom devices must use the exact device label.
    device = s["profile"]
    candidates = []
    for candidate in records:
        try:
            row = validate_record(candidate)
        except (ValueError, TypeError):
            continue
        if row["device"] != device or abs(row["weight_bits"] - s["weight_bits"]) > .01:
            continue
        # Nearest-neighbor only within controlled interpolation domain.
        mp = max(row["params_b"], s["params_b"]) / min(row["params_b"], s["params_b"])
        mc = max(row["context_tokens"], s["context_tokens"]) / min(row["context_tokens"], s["context_tokens"])
        mn = max(row["concurrency"], s["concurrency"]) / min(row["concurrency"], s["concurrency"])
        if mp > 1.35 or mc > 2 or mn > 2:
            continue
        dist = 2 * math.log(mp) + math.log(mc) + math.log(mn)
        candidates.append((dist, row))
    candidates.sort(key=lambda x: x[0])
    if len(candidates) < 2:
        return {"estimate": None, "confidence": "uncalibrated", "matches": len(candidates),
                "reason": "At least two nearby measurements on this device profile and weight precision are required."}
    neighbors = candidates[:min(7, len(candidates))]
    weights = [1 / (.12 + d) for d, _ in neighbors]
    value = sum(w * r["output_tokens_per_second"] for w, (_, r) in zip(weights, neighbors)) / sum(weights)
    values = [r["output_tokens_per_second"] for _, r in neighbors]
    spread = (max(values) - min(values)) / max(median(values), .001)
    confidence = "medium" if len(neighbors) >= 3 and spread <= .3 and neighbors[0][0] < .5 else "low"
    return {"estimate": round(value, 2), "confidence": confidence, "matches": len(neighbors),
            "observed_min": min(values), "observed_max": max(values),
            "reason": "Weighted average of nearby imported observations, not a guaranteed or physics-based prediction. Check benchmark provenance and workload comparability.",
            "sources": list(dict.fromkeys(r["source"] for _, r in neighbors))[:7]}
