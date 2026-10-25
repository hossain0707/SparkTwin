"""Transparent first-order inference memory model; no invented performance figures.

All capacity arithmetic is GiB (binary), while vendor memory specifications are
converted from decimal GB. This model is intentionally NOT a full runtime simulator.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import math

GB_TO_GIB = 1e9 / (1024**3)

PROFILES = {
    "dgx-spark-128": {"name": "DGX Spark · 128 GB", "system_memory_gb": 128.0,
                      "bandwidth_gbs": 273.0, "source": "https://docs.nvidia.com/dgx/dgx-spark/hardware.html"},
    "custom": {"name": "Custom unified-memory host", "system_memory_gb": None,
               "bandwidth_gbs": None, "source": "User-supplied hardware values"},
}

DEFAULT = {
    "name": "Llama-class 8B · exploratory", "profile": "dgx-spark-128",
    "params_b": 8.0, "weight_bits": 4.0, "weight_overhead": 1.15,
    "layers": 32, "kv_heads": 8, "head_dim": 128, "kv_bytes": 2,
    "context_tokens": 8192, "concurrency": 4, "kv_utilization": 1.0,
    "os_reserve_gib": 12.0, "runtime_reserve_gib": 5.0,
    "activation_reserve_gib": 2.0, "safety_fraction": 0.1,
    "custom_memory_gb": 128.0, "custom_bandwidth_gbs": 273.0,
}

RANGES = {
    "params_b": (0.01, 1000), "weight_bits": (2, 32),
    "weight_overhead": (1, 2.5), "layers": (1, 256),
    "kv_heads": (1, 256), "head_dim": (16, 512),
    "kv_bytes": (0.25, 8), "context_tokens": (128, 1048576),
    "concurrency": (1, 1024), "kv_utilization": (0.01, 1),
    "os_reserve_gib": (0, 1024), "runtime_reserve_gib": (0, 1024),
    "activation_reserve_gib": (0, 1024), "safety_fraction": (0, 0.5),
    "custom_memory_gb": (1, 4096), "custom_bandwidth_gbs": (0.1, 100000),
}
INTS = {"layers", "kv_heads", "head_dim", "context_tokens", "concurrency"}


class InvalidScenario(ValueError):
    pass


def normalize(value: dict) -> dict:
    if not isinstance(value, dict):
        raise InvalidScenario("Scenario must be a JSON object")
    unknown = set(value) - (set(DEFAULT) | {"id", "created_at", "updated_at"})
    if unknown:
        raise InvalidScenario("Unknown fields: " + ", ".join(sorted(unknown)))
    result = dict(DEFAULT)
    result.update({k: v for k, v in value.items() if k in DEFAULT})
    if not isinstance(result["name"], str) or not (1 <= len(result["name"].strip()) <= 120):
        raise InvalidScenario("Name must have 1–120 characters")
    result["name"] = result["name"].strip()
    if result["profile"] not in PROFILES:
        raise InvalidScenario("Unsupported hardware profile")
    for field, (lo, hi) in RANGES.items():
        raw = result[field]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise InvalidScenario(f"{field} must be numeric")
        num = float(raw)
        if not math.isfinite(num) or not lo <= num <= hi:
            raise InvalidScenario(f"{field} must be in [{lo}, {hi}]")
        if field in INTS and not num.is_integer():
            raise InvalidScenario(f"{field} must be an integer")
        result[field] = int(num) if field in INTS else num
    return result


def assess(raw: dict) -> dict:
    s = normalize(raw)
    profile = PROFILES[s["profile"]]
    memory_gb = profile["system_memory_gb"] if s["profile"] != "custom" else s["custom_memory_gb"]
    bandwidth_gbs = profile["bandwidth_gbs"] if s["profile"] != "custom" else s["custom_bandwidth_gbs"]
    physical_gib = memory_gb * GB_TO_GIB
    weights_gib = s["params_b"] * 1e9 * s["weight_bits"] / 8 / 1024**3 * s["weight_overhead"]
    kv_per_token_bytes = 2 * s["layers"] * s["kv_heads"] * s["head_dim"] * s["kv_bytes"]
    kv_gib = kv_per_token_bytes * s["context_tokens"] * s["concurrency"] * s["kv_utilization"] / 1024**3
    reserve_gib = s["os_reserve_gib"] + s["runtime_reserve_gib"] + s["activation_reserve_gib"]
    safety_gib = physical_gib * s["safety_fraction"]
    total_gib = weights_gib + kv_gib + reserve_gib + safety_gib
    headroom = physical_gib - total_gib
    usable_gib = physical_gib - reserve_gib - safety_gib
    # Heads-up only; actual context capacity and scheduler behavior are runtime-specific.
    available_kv_gib = max(0, usable_gib - weights_gib)
    kv_per_session_gib = kv_per_token_bytes * s["context_tokens"] * s["kv_utilization"] / 1024**3
    upper_session_count = math.floor(available_kv_gib / kv_per_session_gib) if kv_per_session_gib else 0
    upper_session_count = max(0, min(upper_session_count, 1_000_000))
    if headroom < 0:
        status = "exceeds"
        description = "Estimated memory demand exceeds configured available unified memory."
    elif headroom < max(2.0, physical_gib * 0.07):
        status = "tight"
        description = "Low estimated headroom. Runtime fragmentation and workload bursts may cause failure."
    else:
        status = "fits-estimate"
        description = "First-order memory estimate fits; successful deployment is NOT established."
    return {
        "scenario": s, "profile_name": profile["name"], "profile_source": profile["source"],
        "memory_gb": memory_gb, "physical_gib": round(physical_gib, 3),
        "bandwidth_gbs": bandwidth_gbs, "weights_gib": round(weights_gib, 3),
        "kv_gib": round(kv_gib, 3), "reserve_gib": round(reserve_gib, 3),
        "safety_gib": round(safety_gib, 3), "total_gib": round(total_gib, 3),
        "headroom_gib": round(headroom, 3), "used_percent": round(100 * total_gib / physical_gib, 1),
        "kv_bytes_per_token": kv_per_token_bytes,
        "upper_bound_sessions": upper_session_count, "status": status, "description": description,
        "throughput_tokens_per_s": None, "throughput_basis": "No hardware-backed benchmark matching this scenario is loaded.",
        "assumptions": [
            "Vendor GB are decimal; displayed capacity is binary GiB.",
            "Weight bits, packing overhead, transformer topology and KV dtype must reflect the real model.",
            "KV uses full configured token length and concurrency with user-defined utilization; paged KV, prefix sharing and offload are not modeled.",
            "Unified memory is shared with CPU/OS; memory reserves and safety margin are explicit user assumptions.",
            "Upper-bound session count is a memory-only estimate, not achievable service concurrency.",
            "No throughput or latency can be inferred reliably from the hardware specification alone.",
        ],
    }


def recommend_variant(raw: dict) -> list[dict]:
    s = normalize(raw)
    variations = [
        ("As configured", {}),
        ("Lower weight precision", {"weight_bits": max(2, round(s["weight_bits"] / 2, 2))}),
        ("Halve context length", {"context_tokens": max(128, int(s["context_tokens"] / 2))}),
        ("Halve concurrency", {"concurrency": max(1, s["concurrency"] // 2)}),
    ]
    out = []
    for title, changed in variations:
        x = dict(s, **changed)
        est = assess(x)
        out.append({"label": title, "changes": changed,
                    "total_gib": est["total_gib"], "headroom_gib": est["headroom_gib"],
                    "status": est["status"], "weight_bits": x["weight_bits"],
                    "context_tokens": x["context_tokens"], "concurrency": x["concurrency"]})
    return out
