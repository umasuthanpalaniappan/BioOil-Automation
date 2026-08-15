"""Simple, documented rule-based physics/plausibility checks on inputs and
predictions. These are heuristics grounded in pyrolysis literature, not a
full process simulation.
"""
from app.schemas import ConstraintFlag, FeedstockInput

PT_MIN_TRAINING_REGIME = 400
PT_MAX_TRAINING_REGIME = 900


def validate_feedstock(f: FeedstockInput) -> list[ConstraintFlag]:
    flags: list[ConstraintFlag] = []

    biomass_sum = f.Cel + f.Hem + f.Lig
    if biomass_sum > 100:
        flags.append(ConstraintFlag(
            field="Cel/Hem/Lig",
            message=f"Cellulose + hemicellulose + lignin = {biomass_sum:.1f}%, "
                    "exceeds 100% of dry biomass — check inputs.",
            severity="error",
        ))
    elif biomass_sum < 40:
        flags.append(ConstraintFlag(
            field="Cel/Hem/Lig",
            message=f"Cellulose + hemicellulose + lignin = {biomass_sum:.1f}%, "
                    "unusually low for a lignocellulosic feedstock.",
            severity="warning",
        ))

    ultimate_sum = f.C_pct + f.H_pct + f.O_pct + f.N_pct
    if ultimate_sum > 105 or ultimate_sum < 90:
        flags.append(ConstraintFlag(
            field="C%/H%/O%/N%",
            message=f"Ultimate analysis sums to {ultimate_sum:.1f}% "
                    "(expected ~100%, ash/moisture-free basis) — check inputs.",
            severity="warning",
        ))

    proximate_sum = f.VM + f.Ash + f.FC
    if proximate_sum > 105 or proximate_sum < 90:
        flags.append(ConstraintFlag(
            field="VM/Ash/FC",
            message=f"Proximate analysis sums to {proximate_sum:.1f}% "
                    "(expected ~100%) — check inputs.",
            severity="warning",
        ))

    if not (PT_MIN_TRAINING_REGIME <= f.PT <= PT_MAX_TRAINING_REGIME):
        flags.append(ConstraintFlag(
            field="PT",
            message=f"Pyrolysis temperature {f.PT}°C is outside the "
                    f"{PT_MIN_TRAINING_REGIME}-{PT_MAX_TRAINING_REGIME}°C range "
                    "the models were trained on — prediction is an extrapolation.",
            severity="warning",
        ))

    return flags


def validate_prediction(value: float, target: str = "O/C") -> list[ConstraintFlag]:
    flags: list[ConstraintFlag] = []
    if value < 0:
        flags.append(ConstraintFlag(
            field=target,
            message=f"Predicted {target} = {value:.3f} is negative, which is "
                    "physically impossible — treat this prediction as unreliable "
                    "(likely extrapolation beyond training data).",
            severity="error",
        ))
    if target == "O/C" and value > 5:
        flags.append(ConstraintFlag(
            field=target,
            message=f"Predicted O/C = {value:.3f} is far above any observed "
                    "training value (max 3.57) — treat with caution.",
            severity="warning",
        ))
    return flags
