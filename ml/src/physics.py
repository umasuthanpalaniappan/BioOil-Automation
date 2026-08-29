"""Pyrolysis reaction physics used as engineered features for the ML models.

This module encodes actual reactor chemistry — reaction kinetics and a
combustion-engineering energy correlation — as explicit equations, rather
than leaving the model to infer everything statistically from correlations.
The intent (per project review feedback): the model should be told *how the
process works* via governing equations, and only then be trained/tuned on
top of that physical structure ("physics-informed" / hybrid grey-box ML,
not a purely black-box regressor).

-------------------------------------------------------------------------
1) Independent Parallel Reactions (IPR) pyrolysis kinetics
-------------------------------------------------------------------------
Lignocellulosic biomass is treated as three independently-reacting
pseudo-components — cellulose, hemicellulose, lignin — each following a
single first-order Arrhenius reaction (the standard IPR framework used in
biomass pyrolysis kinetics literature, e.g. Orfao, Antunes & Figueiredo,
"Pyrolysis kinetics of lignocellulosic materials - three independent
reactions model", Fuel 78(3), 1999):

    d(alpha_i)/dt = A_i * exp(-Ea_i / (R*T)) * (1 - alpha_i)

  alpha_i(t)  : conversion fraction (0-1) of pseudo-component i at time t
  A_i         : pre-exponential (frequency) factor [1/s]
  Ea_i        : activation energy [J/mol]
  R           : universal gas constant, 8.314 J/(mol*K)
  T           : instantaneous temperature [K]

For a reactor heated at a constant rate HR [deg C/min] from an ambient
starting temperature T0 up to the process temperature PT, temperature
rises linearly with time: T(t) = T0 + HR*t. Integrating the ODE above
from t=0 to the time the bed reaches PT gives the conversion fraction
predicted by reaction kinetics alone for that pseudo-component, under
those exact process conditions — this is a genuine physics computation,
not a fitted statistical feature.

Kinetic triplets (A, Ea) used below are literature-representative single
first-order-reaction (SFOR) values compiled from comparative TGA kinetics
studies of the three pseudo-components (see ml/reports/physics.md for the
full citation and the wide range reported study-to-study — these are used
as physically-motivated priors, not values fitted to this project's
dataset).

-------------------------------------------------------------------------
2) Modified Dulong formula (fuel higher heating value)
-------------------------------------------------------------------------
Standard solid-fuel combustion-engineering correlation estimating higher
heating value (HHV, MJ/kg) directly from a fuel's ultimate (elemental)
analysis:

    HHV = 33.5*C + 142.3*H - 15.4*O - 14.5*N

  C, H, O, N  : mass fractions (0-1) of carbon, hydrogen, oxygen, nitrogen

This gives the models a physics-derived estimate of the feedstock's own
energy content as an input feature, directly relevant to the calorific
value target and to O/C (both track feedstock oxygen loading).
"""
import numpy as np
from scipy.integrate import solve_ivp

R_GAS = 8.314  # J / (mol K)
T0_AMBIENT_K = 298.15  # 25 C, reactor/feed starting temperature

# Single first-order-reaction (SFOR) kinetic triplets, literature-representative.
# See ml/reports/physics.md for citations and reported ranges.
KINETIC_PARAMS = {
    "cellulose":     {"A": 3.50e12, "Ea": 199_660.0},  # A [1/s], Ea [J/mol]
    "hemicellulose": {"A": 9.67e9,  "Ea": 95_390.0},
    "lignin":        {"A": 2.59e5,  "Ea": 174_400.0},
}


def _conversion_fraction(A: float, Ea: float, pt_celsius: float, hr_c_per_min: float) -> float:
    """Integrate the first-order Arrhenius conversion ODE from T0 to PT at
    heating rate HR, and return the predicted conversion fraction (0-1)
    reached by the time the bed hits the process temperature.

    Standard non-isothermal-kinetics technique: change the integration
    variable from time to temperature (dT/dt = beta = const heating rate),
    so d(alpha)/dT = (A/beta) * exp(-Ea/RT) * (1-alpha). Integrating over
    the ~500 K temperature span is well-conditioned; integrating the same
    ODE over real wall-clock seconds at slow heating rates spans many
    thousands of seconds with a sharp late-stage transition and is
    numerically stiff for an explicit solver.
    """
    if pt_celsius is None or hr_c_per_min is None:
        return np.nan
    if np.isnan(pt_celsius) or np.isnan(hr_c_per_min) or hr_c_per_min <= 0:
        return np.nan
    pt_k = pt_celsius + 273.15
    if pt_k <= T0_AMBIENT_K:
        return 0.0

    beta_k_per_s = hr_c_per_min / 60.0  # heating rate, K/s

    def rhs(T, alpha):
        a = min(max(alpha[0], 0.0), 1.0)
        k = A * np.exp(-Ea / (R_GAS * T))
        return [(k / beta_k_per_s) * (1.0 - a)]

    sol = solve_ivp(rhs, [T0_AMBIENT_K, pt_k], [0.0], method="LSODA", rtol=1e-6, atol=1e-9)
    alpha_final = float(sol.y[0, -1])
    return min(max(alpha_final, 0.0), 1.0)


def kinetic_conversion_features(cel_pct, hem_pct, lig_pct, pt_celsius, hr_c_per_min) -> dict:
    """Physics-predicted conversion of each pseudo-component and the
    composition-weighted overall conversion / char-fraction proxy.
    """
    out = {}
    for name, params in KINETIC_PARAMS.items():
        out[f"physics_alpha_{name}"] = _conversion_fraction(params["A"], params["Ea"], pt_celsius, hr_c_per_min)

    fracs = {"cellulose": cel_pct, "hemicellulose": hem_pct, "lignin": lig_pct}
    total = sum(v for v in fracs.values() if v is not None and not np.isnan(v))
    if total and total > 0:
        weighted = sum(
            (fracs[name] / total) * out[f"physics_alpha_{name}"]
            for name in KINETIC_PARAMS
            if fracs[name] is not None and not np.isnan(fracs[name]) and not np.isnan(out[f"physics_alpha_{name}"])
        )
        out["physics_conversion"] = weighted
        out["physics_char_fraction"] = 1.0 - weighted
    else:
        out["physics_conversion"] = np.nan
        out["physics_char_fraction"] = np.nan
    return out


def dulong_hhv(c_pct, h_pct, o_pct, n_pct) -> float:
    """Modified Dulong formula: HHV (MJ/kg) from ultimate analysis mass %."""
    if any(v is None or (isinstance(v, float) and np.isnan(v)) for v in (c_pct, h_pct, o_pct, n_pct)):
        return np.nan
    C, H, O, N = c_pct / 100.0, h_pct / 100.0, o_pct / 100.0, n_pct / 100.0
    return 33.5 * C + 142.3 * H - 15.4 * O - 14.5 * N


def physics_features_for_row(row: dict) -> dict:
    """Compute all physics-informed features for one feedstock/condition row.
    `row` must have keys: Cel, Hem, Lig, C%, H%, O%, N%, PT, HR (raw, un-prefixed).
    """
    feats = kinetic_conversion_features(row.get("Cel"), row.get("Hem"), row.get("Lig"), row.get("PT"), row.get("HR"))
    feats["physics_hhv_dulong"] = dulong_hhv(row.get("C%"), row.get("H%"), row.get("O%"), row.get("N%"))
    return feats


PHYSICS_FEATURE_COLS = [
    "physics_alpha_cellulose", "physics_alpha_hemicellulose", "physics_alpha_lignin",
    "physics_conversion", "physics_char_fraction", "physics_hhv_dulong",
]
