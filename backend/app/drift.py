"""Compare submitted feature values against training data ranges."""
from app.model_registry import registry
from app.schemas import DriftFlag


def check_drift(feature_dict: dict) -> list[DriftFlag]:
    flags = []
    for field, value in feature_dict.items():
        rng = registry.feature_ranges.get(field)
        if rng is None or value is None:
            continue
        lo, hi = rng["min"], rng["max"]
        span = hi - lo if hi > lo else 1.0
        margin = span * 0.05
        if value < lo - margin or value > hi + margin:
            flags.append(DriftFlag(
                field=field,
                value=value,
                training_min=lo,
                training_max=hi,
                message=f"{field}={value} is outside the training data range "
                        f"[{lo:.2f}, {hi:.2f}] — prediction is an out-of-distribution "
                        "extrapolation and confidence should be discounted.",
            ))
    return flags
